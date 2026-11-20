import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path
from base_conhecimento import BaseConhecimento, normalizar
from orientacao import Orientacao


class Assistente:
    """Coordena o atendimento ao cidadao, historico, indicadores e exportacao."""

    def __init__(self, nome: str, base: BaseConhecimento):
        self.nome = nome
        self.base = base
        self.historico: list[dict] = []
        self.pasta_dados = Path(self.base.caminho).parent
        self.caminho_historico = self.pasta_dados / "historico.json"
        self.caminho_csv = self.pasta_dados / "atendimentos.csv"
        self._carregar_historico_existente()

    def _carregar_historico_existente(self) -> None:
        """Carrega historico previo se existir, sem travar se estiver vazio/corrompido."""
        if not self.caminho_historico.exists():
            self.historico = []
            return
        try:
            with self.caminho_historico.open("r", encoding="utf-8") as f:
                dados = json.load(f)
            if isinstance(dados, list):
                self.historico = dados
        except (json.JSONDecodeError, OSError):
            self.historico = []

    @staticmethod
    def contem_dado_pessoal(texto: str) -> bool:
        """Bloqueia entradas com '@' ou 8 ou mais digitos (ex.: CPF, telefone, RG/CEP)."""
        if "@" in texto:
            return True
        digitos = re.findall(r"\d", texto)
        return len(digitos) >= 8

    @staticmethod
    def classificar_confianca(pontos: int) -> str | None:
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MEDIA"
        return None

    def _ler_sim_nao(self, mensagem: str) -> bool:
        while True:
            resp = input(mensagem).strip().lower()
            if resp in ("s", "sim"):
                return True
            if resp in ("n", "nao", "não"):
                return False
            print("Entrada invalida. Digite 's' para sim ou 'n' para nao.")

    def _ler_nota_facilidade(self) -> int:
        while True:
            entrada = input("\nDe 1 a 5, qual foi a facilidade de uso do assistente? ").strip()
            if entrada in ("1", "2", "3", "4", "5"):
                return int(entrada)
            print("Opcao invalida. Digite um numero inteiro de 1 a 5.")

    def registrar(
        self,
        origem: str,
        pergunta: str,
        orientacao_id: int | None,
        encontrou: bool,
        ajudou: bool,
        tentativas: int,
        tempo_segundos: float,
    ) -> None:
        """Adiciona um atendimento ao historico e salva em data/historico.json."""
        registro = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao_id,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo_segundos,
        }
        self.historico.append(registro)

        try:
            self.pasta_dados.mkdir(parents=True, exist_ok=True)
            with self.caminho_historico.open("w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"\n[Aviso] Nao foi possivel salvar o historico: {erro}")

    def perguntar(self) -> None:
        """Fluxo de atendimento por pergunta livre (0 para voltar)."""
        if not self.base.orientacoes:
            print("\nNenhuma orientacao carregada na base de conhecimento.")
            return

        print("\n--- Perguntar ao Assistente (digite 0 para voltar) ---")
        inicio = time.time()
        tentativas = 0

        while True:
            pergunta = input("\nDigite sua duvida (0 para voltar): ").strip()

            if pergunta == "0":
                return

            if not pergunta:
                print("Entrada vazia. Escreva sua duvida ou digite 0 para voltar.")
                continue

            if self.contem_dado_pessoal(pergunta):
                print("Atencao: nao digite CPF, telefone, e-mail ou sequencias com 8+ digitos. Reescreva.")
                continue

            tentativas += 1
            resultados = self.base.buscar(pergunta)
            melhores_pontos, melhor_orientacao = resultados[0]
            confianca = self.classificar_confianca(melhores_pontos)

            if confianca is None:
                print("\nNao encontrei uma orientacao com confianca suficiente para essa duvida.")
                cats = self.base.categorias()
                if cats:
                    print("Categorias disponiveis:", ", ".join(cats))
                exemplos = []
                for o in self.base.orientacoes[:3]:
                    if o.palavras_chave:
                        exemplos.append(o.palavras_chave[0])
                if exemplos:
                    print("Tente termos como:", ", ".join(exemplos))

                ajudou = self._ler_sim_nao("Mesmo assim, isso ajudou de alguma forma? (s/n): ")
                tempo_gasto = round(time.time() - inicio, 1)
                self.registrar(
                    origem="pergunta",
                    pergunta=pergunta,
                    orientacao_id=None,
                    encontrou=False,
                    ajudou=ajudou,
                    tentativas=tentativas,
                    tempo_segundos=tempo_gasto,
                )
                inicio = time.time()
                tentativas = 0
                continue

            # Mostra a melhor orientacao
            melhor_orientacao.exibir(pontos=melhores_pontos, confianca=confianca)

            # Mostra ate 2 alternativas com pontuacao >= 3
            alternativas = [
                (pts, alt)
                for pts, alt in resultados[1:]
                if pts >= 3
            ][:2]

            if alternativas:
                print("\nOutras orientacoes que podem ajudar:")
                for idx, (pts, alt) in enumerate(alternativas, start=1):
                    print(f"  {idx}. {alt.titulo} [{alt.categoria}] ({pts} pontos)")

                while True:
                    escolha = input(
                        "Digite o numero da alternativa para ver detalhes ou ENTER para continuar: "
                    ).strip()
                    if escolha == "":
                        break
                    if escolha.isdigit() and 1 <= int(escolha) <= len(alternativas):
                        _, alt_escolhida = alternativas[int(escolha) - 1]
                        alt_escolhida.exibir()
                        break
                    print("Opcao invalida. Digite o numero da alternativa ou pressione ENTER.")

            ajudou = self._ler_sim_nao("\nEssa orientacao respondeu sua duvida? (s/n): ")
            tempo_gasto = round(time.time() - inicio, 1)
            self.registrar(
                origem="pergunta",
                pergunta=pergunta,
                orientacao_id=melhor_orientacao.id,
                encontrou=True,
                ajudou=ajudou,
                tentativas=tentativas,
                tempo_segundos=tempo_gasto,
            )
            inicio = time.time()
            tentativas = 0

    def navegar(self) -> None:
        """Navegacao por categorias e orientacoes numeradas (0 para voltar)."""
        cats = self.base.categorias()
        if not cats:
            print("\nNenhuma categoria disponivel.")
            return

        while True:
            print("\n--- Navegar por Categorias ---")
            for i, cat in enumerate(cats, start=1):
                print(f"  {i}. {cat}")
            print("  0. Voltar")

            escolha_cat = input("Escolha uma categoria (0 para voltar): ").strip()
            if escolha_cat == "0":
                return
            if not escolha_cat.isdigit() or not (1 <= int(escolha_cat) <= len(cats)):
                print("Opcao invalida. Escolha um numero da lista ou 0 para voltar.")
                continue

            categoria_selecionada = cats[int(escolha_cat) - 1]
            itens = self.base.por_categoria(categoria_selecionada)

            while True:
                inicio = time.time()
                print(f"\n--- Categoria: {categoria_selecionada} ---")
                for j, item in enumerate(itens, start=1):
                    print(f"  {j}. {item.titulo}")
                print("  0. Voltar")

                escolha_item = input("Escolha uma orientacao (0 para voltar): ").strip()
                if escolha_item == "0":
                    break
                if not escolha_item.isdigit() or not (1 <= int(escolha_item) <= len(itens)):
                    print("Opcao invalida. Escolha um numero da lista ou 0 para voltar.")
                    continue

                orientacao_escolhida = itens[int(escolha_item) - 1]
                orientacao_escolhida.exibir()

                ajudou = self._ler_sim_nao("\nEssa orientacao respondeu sua duvida? (s/n): ")
                tempo_gasto = round(time.time() - inicio, 1)
                self.registrar(
                    origem="categoria",
                    pergunta=f"[Categoria: {categoria_selecionada}] {orientacao_escolhida.titulo}",
                    orientacao_id=orientacao_escolhida.id,
                    encontrou=True,
                    ajudou=ajudou,
                    tentativas=1,
                    tempo_segundos=tempo_gasto,
                )

    def indicadores(self, nota_facilidade: int | None = None) -> dict:
        """Calcula e exibe os indicadores do historico de atendimentos."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda nao ha atendimentos registrados para calcular indicadores.")
            return {}

        encontrados = [r for r in self.historico if r.get("encontrou") is True]
        ajudaram = [r for r in self.historico if r.get("ajudou") is True]

        pct_encontrada = round((len(encontrados) / total) * 100, 1)
        taxa_ajudou = round((len(ajudaram) / total) * 100, 1)

        tempos_encontrados = [
            float(r.get("tempo_segundos", 0.0))
            for r in encontrados
            if r.get("tempo_segundos") is not None
        ]
        tempo_medio = round(sum(tempos_encontrados) / len(tempos_encontrados), 1) if tempos_encontrados else 0.0

        media_tentativas = round(
            sum(int(r.get("tentativas", 1)) for r in self.historico) / total, 2
        )

        duvidas_sem_solucao = [
            r.get("pergunta", "")
            for r in self.historico
            if not (r.get("encontrou") is True and r.get("ajudou") is True)
        ]

        print("\n" + "=" * 60)
        print(f"INDICADORES DO ASSISTENTE - {self.nome}")
        print("=" * 60)
        print(f"Total de atendimentos: {total}")
        print(f"Resposta encontrada (%): {pct_encontrada}%")
        print(f"Tempo medio para encontrar (quando encontrada): {tempo_medio} s")
        if nota_facilidade is not None:
            print(f"Facilidade de uso informada (1 a 5): {nota_facilidade}")
        print(f"Taxa de acerto / ajudou (%): {taxa_ajudou}%")
        print(f"Media de tentativas por atendimento: {media_tentativas}")
        print("Duvidas sem solucao:")
        if duvidas_sem_solucao:
            for d in duvidas_sem_solucao:
                print(f"  - {d}")
        else:
            print("  - Nenhuma duvida sem solucao!")
        print("=" * 60)

        return {
            "total": total,
            "resposta_encontrada_pct": pct_encontrada,
            "tempo_medio_s": tempo_medio,
            "facilidade_1_a_5": nota_facilidade,
            "taxa_ajudou_pct": taxa_ajudou,
            "tentativas_por_atendimento": media_tentativas,
            "duvidas_sem_solucao": duvidas_sem_solucao,
        }

    def exportar_csv(self) -> bool:
        """Exporta os atendimentos de self.historico para data/atendimentos.csv."""
        colunas = [
            "data",
            "origem",
            "pergunta",
            "id_orientacao",
            "encontrou",
            "ajudou",
            "tentativas",
            "tempo_segundos",
        ]
        try:
            self.pasta_dados.mkdir(parents=True, exist_ok=True)
            with self.caminho_csv.open("w", newline="", encoding="utf-8") as f:
                escritor = csv.DictWriter(f, fieldnames=colunas)
                escritor.writeheader()
                for linha in self.historico:
                    escritor.writerow({col: linha.get(col, "") for col in colunas})
            print(f"\nHistorico exportado com sucesso para '{self.caminho_csv}'.")
            return True
        except OSError as erro:
            print(f"\n[Aviso] Nao foi possivel exportar o CSV: {erro}")
            return False
import json
from pathlib import Path
from orientacao import Orientacao

ACENTOS = {
    "á": "a",
    "à": "a",
    "ã": "a",
    "â": "a",
    "ä": "a",
    "é": "e",
    "ê": "e",
    "è": "e",
    "í": "i",
    "î": "i",
    "ó": "o",
    "õ": "o",
    "ô": "o",
    "ö": "o",
    "ú": "u",
    "ü": "u",
    "ç": "c",
}


def normalizar(texto: str) -> str:
    """Remove acentos, pontuacao e excesso de espacos, deixando tudo minusculo."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()[]{}\"'/-":
        texto = texto.replace(sinal, " ")
    return " ".join(texto.split())


class BaseConhecimento:
    """Gerencia o carregamento e a busca nas orientacoes."""

    def __init__(self, caminho: str):
        self.caminho = caminho
        self.orientacoes: list[Orientacao] = []

    def carregar(self) -> bool:
        """Le o arquivo JSON e cria os objetos Orientacao. Nao trava se houver erro."""
        arquivo = Path(self.caminho)
        if not arquivo.exists():
            print(f"\n[Aviso] Arquivo '{self.caminho}' nao encontrado.")
            self.orientacoes = []
            return False

        try:
            with arquivo.open("r", encoding="utf-8") as f:
                dados = json.load(f)
        except (json.JSONDecodeError, OSError) as erro:
            print(f"\n[Aviso] Nao foi possivel ler '{self.caminho}' ({erro}).")
            self.orientacoes = []
            return False

        if not isinstance(dados, list):
            print("\n[Aviso] O JSON da base deve conter uma lista de orientacoes.")
            self.orientacoes = []
            return False

        orientacoes_carregadas: list[Orientacao] = []
        campos_obrigatorios = {
            "id",
            "categoria",
            "titulo",
            "palavras_chave",
            "resposta",
            "documentos",
            "onde",
            "fonte",
            "verificado_em",
        }

        for item in dados:
            if not isinstance(item, dict) or not campos_obrigatorios.issubset(item.keys()):
                continue
            orientacoes_carregadas.append(
                Orientacao(
                    id=item["id"],
                    categoria=str(item["categoria"]),
                    titulo=str(item["titulo"]),
                    palavras_chave=list(item["palavras_chave"]),
                    resposta=str(item["resposta"]),
                    documentos=list(item["documentos"]),
                    onde=str(item["onde"]),
                    fonte=str(item["fonte"]),
                    verificado_em=str(item["verificado_em"]),
                )
            )

        self.orientacoes = orientacoes_carregadas
        return True

    def categorias(self) -> list[str]:
        """Retorna as categorias unicas preservando a ordem."""
        vistas: list[str] = []
        for o in self.orientacoes:
            if o.categoria not in vistas:
                vistas.append(o.categoria)
        return vistas

    def por_categoria(self, categoria: str) -> list[Orientacao]:
        """Retorna as orientacoes pertencentes a uma categoria."""
        cat_norm = normalizar(categoria)
        return [o for o in self.orientacoes if normalizar(o.categoria) == cat_norm]

    def pontuar(self, pergunta_norm: str, orientacao: Orientacao) -> int:
        """
        Calcula a pontuacao de uma orientacao para a pergunta normalizada:
        - +3 pontos para cada palavra-chave normalizada presente na pergunta
        - +1 ponto para cada palavra da pergunta (>= 4 letras) presente no titulo normalizado
        """
        pontos = 0
        palavras_pergunta = pergunta_norm.split()

        # Evita contar a mesma palavra-chave duas vezes na mesma orientacao
        chaves_vistas = set()
        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            if chave_norm and chave_norm not in chaves_vistas:
                chaves_vistas.add(chave_norm)
                # Busca como frase/expressao delimitadas por espacos
                if f" {chave_norm} " in f" {pergunta_norm} ":
                    pontos += 3

        titulo_norm = normalizar(orientacao.titulo)
        palavras_titulo = set(titulo_norm.split())
        palavras_pergunta_vistas = set()

        for palavra in palavras_pergunta:
            if len(palavra) >= 4 and palavra not in palavras_pergunta_vistas:
                palavras_pergunta_vistas.add(palavra)
                if palavra in palavras_titulo:
                    pontos += 1

        return pontos

    def buscar(self, pergunta: str) -> list[tuple[int, Orientacao]]:
        """Retorna lista de tuplas (pontos, orientacao) ordenada do maior para o menor."""
        pergunta_norm = normalizar(pergunta)
        if not pergunta_norm:
            return []

        resultados: list[tuple[int, Orientacao]] = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_norm, orientacao)
            resultados.append((pontos, orientacao))

        resultados.sort(key=lambda par: par[0], reverse=True)
        return resultados
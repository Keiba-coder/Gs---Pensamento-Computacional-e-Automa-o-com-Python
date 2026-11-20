from base_conhecimento import BaseConhecimento
from assistente import Assistente


def main() -> None:
    base = BaseConhecimento("data/base_conhecimento.json")
    carregou = base.carregar()

    assistente = Assistente("Citizen Assist AI", base)

    if not carregou:
        print(
            "O assistente iniciou sem base carregada. "
            "Verifique 'data/base_conhecimento.json' para usar buscas e categorias."
        )

    while True:
        print("\n==========================================")
        print(f"   {assistente.nome} - Orientacao ao Cidadao")
        print("==========================================")
        print("1. Fazer uma pergunta")
        print("2. Navegar por categorias")
        print("3. Ver indicadores atuais")
        print("4. Exportar CSV")
        print("0. Sair")

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            assistente.indicadores()
        elif opcao == "4":
            assistente.exportar_csv()
        elif opcao == "0":
            nota = assistente._ler_nota_facilidade()
            assistente.indicadores(nota_facilidade=nota)
            assistente.exportar_csv()
            print("\nAte logo! Lembre-se: este assistente NAO e um canal oficial.")
            break
        else:
            print("Opcao invalida. Digite 1, 2, 3, 4 ou 0.")


if __name__ == "__main__":
    main()
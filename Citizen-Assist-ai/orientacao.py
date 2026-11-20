class Orientacao:
    """Representa uma orientacao da base de conhecimento."""

    def __init__(
        self,
        id: int,
        categoria: str,
        titulo: str,
        palavras_chave: list[str],
        resposta: str,
        documentos: list[str],
        onde: str,
        fonte: str,
        verificado_em: str,
    ):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self, pontos: int | None = None, confianca: str | None = None) -> None:
        """Exibe a orientacao completa de forma clara no terminal."""
        print("\n" + "=" * 60)
        if pontos is not None and confianca is not None:
            print(f"Confianca da resposta: {confianca} ({pontos} pontos)")
        print(f">> {self.titulo} [{self.categoria}]")
        print("-" * 60)
        print(self.resposta)

        print("\nDocumentos necessarios:")
        if self.documentos:
            for doc in self.documentos:
                print(f"  - {doc}")
        else:
            print("  - Nenhum documento especifico informado.")

        print(f"\nOnde ir / acessar: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NAO e um canal oficial.")
        print("=" * 60)
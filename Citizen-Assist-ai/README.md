Citizen Assist AI — Orientação ao Cidadão

Assistente executado em terminal em Python desenvolvido para o desafio **CitizenTech** (GS 2026.2 — Pensamento Computacional e Automação com Python, FIAP). O sistema orienta o cidadão a partir de uma base de conhecimento verificada em JSON, exibindo fontes, data de verificação, aviso de limitação e sem solicitar ou armazenar dados pessoais.

Integrantes[2]
- Gabriel Jurado Nogueira — RM: 571236
- Vinicius Torralles — RM: 570911

Público e Problema Escolhidos
- Público: Jovens no primeiro emprego e documentação básica.
- Problema: Muitos jovens têm dificuldade para encontrar orientações claras, confiáveis e em linguagem simples sobre emissão de documentos e primeiros passos no mercado de trabalho (como Carteira de Trabalho Digital, Jovem Aprendiz, estágio, CPF, CIN, conta Gov.br, Título de Eleitor, alistamento militar e Cartão SUS), muitas vezes esbarrando em informações espalhadas ou sites não oficiais.

ODS Relacionados
- ODS 8 (Trabalho Decente e Crescimento Econômico): Facilita o acesso à informação sobre inserção formal no trabalho, direitos básicos, aprendizagem e estágio.
- ODS 16 (Paz, Justiça e Instituições Eficazes): Promove acesso transparente a informações de cidadania e documentação pública, reforçando privacidade ao não coletar dados pessoais].

Como Executar
1. Certifique-se de ter o Python 3 instalado na máquina.
2. Abra o terminal na pasta raiz do projeto (citizen-assist-ai).
3. Execute o programa com: python main.py

Regra de Pontuação e Confiança
A busca é baseada em regras após a normalização do texto (minúsculas, remoção de acentos e pontuação):
- +3 pontos: cada palavra-chave normalizada da orientação que aparece na pergunta.
- +1 ponto: cada palavra da pergunta com 4 letras ou mais que aparece no título normalizado da orientação.
Faixas de confiança da melhor orientação:
- Confiança ALTA: 6 pontos ou mais.
- Confiança MÉDIA: de 3 a 5 pontos.
- Não encontrado: abaixo de 3 pontos, exibindo categorias disponíveis e sugestões de termos.
O método buscar() retorna uma lista de tuplas (pontos, orientacao) ordenada da maior para a menor pontuação, exibindo a melhor orientação e até duas alternativas relevantes.   

Fontes Consultadas
- Portal Gov.br — Trabalho e Emprego: https://www.gov.br/trabalho-e-emprego
- Portal Gov.br — Receita Federal: https://www.gov.br/receitafederal
- Portal Gov.br — Governo Digital: https://www.gov.br/governodigital
- Tribunal Superior Eleitoral (TSE): https://www.tse.jus.br
- Alistamento Militar (Exército Brasileiro): https://alistamento.eb.mil.br
- Portal Gov.br — Saúde: https://www.gov.br/saude

Resultado do Teste de Usuários
Total de atendimentos: 11
Resposta encontrada (%): 36.4%
Tempo medio para encontrar (quando encontrada): 27.8 s
Facilidade de uso informada (1 a 5): 4
Taxa de acerto / ajudou (%): 36.4%
Media de tentativas por atendimento: 1.0
Duvidas sem solucao:
  - Como me alistar?
  - Eu tenho cidania espanhola e gostaria de tirar uma outra cidadania depois mas também europeia, tem problema?
  - quero tirar cidadania cm faço?
  - Como tiro a cidadania?
  - Estou muito querendo um trabalho oque me recomenda?
  - Como arrajar um trabalho?
  - Que documentos presciso para tirar a cidadania?
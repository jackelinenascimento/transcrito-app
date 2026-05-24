# Formatters e Writers Rules

Use estas regras ao criar saidas como TXT, SRT, JSON, Markdown ou novos destinos de escrita.

## Regras

- Formatter recebe `Transcription` e retorna `str`.
- Formatter nao escreve arquivo, nao le arquivo e nao chama servico de transcricao.
- Writer recebe conteudo pronto e destino, e apenas persiste.
- Writer nao decide formato e nao altera transcricao.
- Novo formato deve ser uma classe propria em `src/application/formatters`.
- Novo destino de escrita deve ficar em `src/application/writers`.
- Crie contrato abstrato de writer apenas quando houver mais de um destino real ou necessidade clara de teste.
- Se o formato precisar de novos dados, avalie se `Transcription` ou `TranscriptionSegment` devem evoluir.

## Checklist

- Formatacao e escrita estao separadas?
- O formato lida com transcricoes vazias?
- A extensao de arquivo combina com o formato?
- A documentacao explica a nova saida?


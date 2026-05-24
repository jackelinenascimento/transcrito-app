# Testing Rules

Use estas regras ao adicionar ou alterar testes.

## Regras

- Testes unitarios nao devem baixar modelo Whisper.
- Testes unitarios nao devem transcrever videos reais.
- Use fakes ou mocks para `TranscriptionService`.
- Teste formatadores com entidades pequenas em memoria.
- Teste casos de uso com doubles de service, formatter e writer.
- Teste infraestrutura com mock da biblioteca externa.
- Use diretorios temporarios para testes de escrita.
- Enquanto nao houver suite de testes, valide com `python3 -m compileall -q src`.

## Checklist

- O teste e rapido e deterministico?
- O teste evita rede, GPU e arquivos grandes?
- O teste cobre contrato ou comportamento relevante?
- A validacao local foi executada?


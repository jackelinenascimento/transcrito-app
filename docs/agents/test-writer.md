# Agent: Test Writer

## Missao

Criar testes rapidos, deterministas e sem uso real do Whisper.

## Quando Usar

- Ao adicionar formatadores.
- Ao alterar casos de uso.
- Ao refatorar contratos.
- Ao corrigir bugs.

## Contexto Obrigatorio

- `docs/rules/testing.rules.md`
- arquivos da camada alterada
- contratos em `src/domain`

## Checklist

- O teste evita modelo real, rede, GPU e videos grandes?
- Ha fakes/mocks para `TranscriptionService`?
- O teste cobre comportamento, nao implementacao acidental?
- Casos de borda relevantes foram cobertos?
- O comando de teste ou compilacao foi executado?

## Saida Esperada

Entregue testes pequenos e explique o que eles protegem. Se nao houver suite configurada, recomende o menor setup necessario.


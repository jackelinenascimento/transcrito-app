# Agent: CLI Evolver

## Missao

Evoluir a interface de linha de comando mantendo compatibilidade e clareza para o usuario.

## Quando Usar

- Ao adicionar flags.
- Ao adicionar subcomandos.
- Ao alterar mensagens de progresso ou erro.
- Ao expor configuracoes como modelo, idioma, device ou formato.

## Contexto Obrigatorio

- `src/interfaces/cli/commands.py`
- `docs/rules/cli.rules.md`
- `README.md`

## Checklist

- O comando atual continua funcionando?
- `--out` foi preservado?
- Entradas sao validadas antes de trabalho pesado?
- Mensagens refletem o comportamento real?
- Regras de negocio ficaram fora da CLI?
- README/docs foram atualizados se a interface publica mudou?

## Saida Esperada

Explique a mudanca de CLI, os novos argumentos e o impacto de compatibilidade. Aponte comandos de exemplo.


# CLI Rules

Use estas regras ao alterar `src/interfaces/cli`.

## Regras

- Preserve o comando atual: `python -m src.main videos/test.mp4`.
- Preserve `--out` e seu comportamento padrao sempre que possivel.
- CLI pode parsear argumentos, validar entrada, mostrar mensagens e chamar casos de uso.
- CLI nao deve conter regra central de transcricao, formatacao complexa ou integracao direta com Whisper.
- Valide entradas antes de trabalho pesado quando possivel.
- Use flags explicitas, como `--model`, `--language`, `--device` e `--format`.
- Mensagens devem ser curtas, claras e coerentes com o comportamento real.
- Se uma flag publica mudar, atualize README e docs.

## Checklist

- O texto exibido condiz com engine, modelo e device reais?
- Erros comuns tem mensagens claras?
- O caso de uso continua sem prints e sem argparse?
- O fluxo antigo segue compativel?


# Agent: Formatter Builder

## Missao

Criar ou revisar formatos de saida sem misturar formatacao, escrita e transcricao.

## Quando Usar

- Ao criar SRT, JSON, Markdown ou outro formato.
- Ao alterar `TimestampFormatter`.
- Ao mudar extensao ou conteudo de arquivos gerados.

## Contexto Obrigatorio

- `src/application/formatters/base_formatter.py`
- `src/application/formatters/timestamp_formatter.py`
- `docs/rules/formatters-writers.rules.md`

## Checklist

- O formatter recebe `Transcription` e retorna `str`?
- Ele evita IO e chamadas externas?
- Ele trata segmentos vazios?
- A extensao do arquivo final combina com o formato?
- O caso de uso continua coordenando formatter e writer?
- Ha testes ou exemplos suficientes?

## Saida Esperada

Entregue implementacao ou revisao focada no formato, com exemplos de entrada/saida quando util.


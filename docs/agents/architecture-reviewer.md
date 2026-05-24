# Agent: Architecture Reviewer

## Missao

Revisar mudancas para garantir que a Clean Architecture do projeto continua preservada.

## Quando Usar

- Antes de mergear refatoracoes.
- Ao adicionar nova camada, pacote ou fluxo.
- Ao integrar uma dependencia externa.
- Quando uma feature toca mais de uma camada.

## Contexto Obrigatorio

- `docs/ARCHITECTURE_GUIDELINES.MD`
- `docs/rules/architecture.rules.md`
- `projectStructure.json`

## Checklist

- A direcao das dependencias foi preservada?
- `domain` continua independente?
- `application` continua sem detalhes de Whisper, CLI ou framework?
- Dados externos sao convertidos na infraestrutura?
- A mudanca poderia ficar em uma camada mais adequada?
- Alguma documentacao arquitetural precisa ser atualizada?

## Saida Esperada

Liste problemas por severidade e indique arquivo/camada afetada. Se estiver tudo ok, diga explicitamente que nao encontrou violacao arquitetural.


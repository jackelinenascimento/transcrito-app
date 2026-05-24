# Architecture Rules

Use estas regras antes de alterar estrutura, imports ou responsabilidades entre camadas.

## Regras

- Preserve a direcao das dependencias: `interfaces -> application -> domain` e `infrastructure -> domain`.
- `domain` nunca deve importar `application`, `infrastructure`, `interfaces`, Whisper, Torch, argparse ou frameworks.
- `application` deve orquestrar casos de uso e depender de contratos, nao de bibliotecas externas.
- `infrastructure` deve adaptar ferramentas externas e converter dados externos para entidades do dominio.
- `interfaces` deve adaptar entrada/saida com usuario e delegar para casos de uso.
- `main.py` e o composition root atual; mantenha montagem de dependencias concretas nele ou em bootstrap dedicado.
- Nao crie nova camada ou diretorio de topo sem uma responsabilidade que as camadas atuais nao resolvam.
- Se uma mudanca exigir quebrar o fluxo atual, atualize `ARCHITECTURE_GUIDELINES.MD` e explique a razao.

## Checklist

- A camada alterada conhece apenas o que deveria?
- Algum detalhe externo vazou para `domain` ou `application`?
- O caso de uso continua independente do Whisper?
- O fluxo principal ainda e facil de seguir?


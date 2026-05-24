# Feature Evolution Rules

Use estas regras para planejar e implementar novas features.

## Regras

- Entregue features em fatias verticais pequenas, funcionando de ponta a ponta.
- Antes de implementar, defina: entrada, caso de uso, contratos, saida e documentacao afetada.
- Comece pela responsabilidade: dominio para conceitos, aplicacao para fluxo, infraestrutura para integracoes, interfaces para entrada/saida.
- Preserve defaults publicos sempre que possivel.
- Nao crie codigo preparatorio amplo sem uma feature concreta usando esse codigo.
- Crie abstracao somente quando houver variacao real, contrato relevante ou reducao clara de acoplamento.
- Nao misture feature grande com refatoracao ampla.
- Atualize docs quando mudar comando, contrato, formato de saida, dependencia ou estrutura.

## Checklist

- A feature tem ponto de entrada claro?
- O comportamento antigo continua funcionando?
- A mudanca cabe em uma responsabilidade nomeavel?
- Existe validacao minima local?


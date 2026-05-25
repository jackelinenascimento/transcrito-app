# Regras de Evolucao do Projeto

Este documento define regras objetivas para evoluir o `transcrito-app` sem perder simplicidade, consistencia e separacao arquitetural.

Leia junto com:

- `docs/ARCHITECTURE_GUIDELINES.MD`
- `docs/PROJECT_GUIDELINES.MD`
- `docs/rules/README.md`
- `docs/agents/README.md`
- `projectStructure.json`

## Regra 1: Preservar a Direcao das Dependencias

Nenhuma evolucao pode quebrar a direcao atual:

```text
interfaces -> application -> domain
infrastructure -> domain
main -> infrastructure + interfaces
```

Permitido:

- `interfaces` chamar casos de uso de `application`;
- `application` depender de contratos e entidades de `domain`;
- `infrastructure` implementar contratos de `domain`;
- `main.py` montar dependencias concretas.

Proibido:

- `domain` importar `application`, `infrastructure` ou `interfaces`;
- `application` importar Whisper, Torch, argparse ou detalhes de terminal;
- `domain` conhecer filesystem real, CLI, framework web ou bibliotecas de IA;
- casos de uso escolherem modelo Whisper diretamente.

## Regra 2: Comecar Pela Responsabilidade, Nao Pelo Arquivo

Antes de criar ou alterar codigo, classifique a mudanca:

- conceito central do problema: `src/domain`;
- orquestracao de fluxo: `src/application`;
- integracao externa: `src/infrastructure`;
- entrada/saida com usuario: `src/interfaces`;
- montagem de dependencias concretas: `src/main.py`;
- documentacao: `docs`.

Se a mudanca parecer caber em muitos lugares, escolha o lugar mais interno que nao precise conhecer detalhes externos.

## Regra 3: Manter o Dominio Pequeno e Independente

O dominio deve continuar simples, estavel e testavel.

Pode entrar no dominio:

- entidades do problema, como transcricao, segmento, legenda, idioma, metadados relevantes;
- contratos abstratos usados por casos de uso;
- regras puras que nao dependem de IO.

Nao deve entrar no dominio:

- nomes de modelos Whisper;
- estruturas cruas retornadas por bibliotecas externas;
- argumentos de CLI;
- paths de arquivos gerados;
- detalhes de cache, banco, fila, HTTP ou storage.

## Regra 4: Criar Abstracao Somente Com Motivo Claro

Abstracoes sao permitidas quando:

- ha mais de uma implementacao real ou planejada para curto prazo;
- a abstracao protege um caso de uso de detalhe externo;
- a abstracao reduz duplicacao relevante;
- a abstracao representa um contrato do dominio ou da aplicacao.

Evite criar abstracao quando:

- so existe uma implementacao e nenhuma variacao concreta;
- o nome fica generico demais, como `Manager`, `Handler`, `Helper` ou `Processor`;
- a abstracao apenas repassa chamadas sem simplificar nada;
- ela torna uma feature pequena mais dificil de ler.

Excecao atual importante:

- `TranscriptionService` e uma abstracao valida porque isola motores de transcricao.
- `TranscriptionFormatter` e uma abstracao valida porque diferentes saidas sao parte clara do roadmap.
- `FileWriter` ainda e concreto; crie contrato de writer apenas quando houver outro destino real de escrita ou quando testes exigirem esse desacoplamento.

## Regra 5: Toda Feature Nova Deve Ter Um Ponto de Entrada Claro

Toda feature precisa responder:

- Como o usuario aciona isso?
- Qual caso de uso executa isso?
- Quais contratos ela usa?
- Qual saida ela produz?
- Que documentacao muda?

Se uma feature nao tem ponto de entrada claro, nao espalhe codigo preparatorio pelo projeto. Documente a decisao ou implemente uma fatia vertical pequena.

## Regra 6: Evoluir Por Fatias Verticais Pequenas

Prefira entregar uma feature funcionando de ponta a ponta em vez de preparar muitas camadas incompletas.

Exemplo bom para `SRT`:

1. Criar `SrtFormatter`.
2. Permitir escolha de formato na CLI.
3. Gravar extensao correta.
4. Atualizar README/docs.
5. Adicionar testes do formatter se houver suite de testes.

Regra adicional para diarizacao:

- prefira integrar diarizacao como um provider na camada `infrastructure` que retorna `speaker` por segmento; apenas quando esse provider nao estiver disponivel, a camada `application` pode aplicar uma heuristica local (por exemplo pausa > `gap_threshold` para detectar novo locutor). Documente claramente e cubra com testes.

Exemplo ruim:

- criar varias interfaces genericas de legenda, exportacao, pipeline e storage sem nenhuma saida SRT funcionando.

## Regra 7: Nao Quebrar o Fluxo Publico Sem Necessidade

O comando atual deve continuar funcionando:

```bash
python -m src.main videos/test.mp4
```

Mudancas que quebram esse fluxo precisam de motivo forte e atualizacao de documentacao.

Ao adicionar flags:

- preserve defaults atuais;
- mantenha `--out` funcionando;
- use nomes explicitos;
- documente no README;
- evite flags que misturam muitas responsabilidades.

## Regra 8: Configuracao Deve Entrar Pela Borda

Configuracoes como modelo, device, idioma e formato devem entrar por:

- CLI;
- arquivo de configuracao futuro;
- variaveis de ambiente futuras;
- composition root (`main.py`) quando ainda nao forem publicas.

Nao espalhe configuracao fixa em varias camadas.

Valores atuais:

- modelo: `base`;
- device: `cpu`;
- idioma: `pt`;
- saida: `outputs`;
- formato: texto com timestamps.

## Regra 9: Converter Dados Externos Na Infraestrutura

Bibliotecas externas podem retornar dicionarios, objetos complexos ou formatos instaveis. Esses dados devem ser convertidos para entidades internas antes de sair da infraestrutura.

Permitido em `infrastructure`:

```python
result = self.model.transcribe(video_path, language="pt")
segments = [
    TranscriptionSegment(...)
    for s in result["segments"]
]
return Transcription(...)
```

Evite:

- retornar `result` cru do Whisper;
- deixar formatter acessar campos especificos do Whisper;
- deixar caso de uso depender de formato externo.

## Regra 10: Formatadores Formatam, Writers Escrevem

Nao misture responsabilidades.

Formatadores:

- recebem `Transcription`;
- retornam `str`;
- nao escrevem arquivo;
- nao chamam servico de transcricao.

Writers:

- recebem conteudo pronto;
- escrevem no destino;
- nao decidem formato;
- nao alteram transcricao.

Casos de uso:

- coordenam service, formatter e writer;
- nao fazem parse de CLI;
- nao imprimem mensagens.

## Regra 11: CLI Deve Ser Fina

`src/interfaces/cli` pode:

- parsear argumentos;
- validar entrada;
- mostrar progresso;
- criar objetos necessarios;
- chamar caso de uso.

`src/interfaces/cli` nao deve:

- conter regra central de transcricao;
- transformar retorno bruto do Whisper;
- formatar saida manualmente quando existir formatter;
- escrever arquivo diretamente quando existir writer;
- crescer indefinidamente em um unico arquivo.

Se `commands.py` crescer muito, separe por comandos dentro de `src/interfaces/cli`.

## Regra 12: Tratamento de Erro Deve Ser Explicito

Ao adicionar tratamento de erro:

- identifique a falha esperada;
- em CLI, mostre mensagem clara;
- nao esconda erro tecnico importante;
- retorne ou encerre de forma previsivel;
- evite capturar `Exception` sem necessidade.

Erros que merecem tratamento dedicado:

- video inexistente;
- extensao/formato invalido;
- diretorio de saida inacessivel;
- ausencia de `ffmpeg`;
- falha ao carregar modelo;
- falha durante transcricao;
- falha ao escrever arquivo.

## Regra 13: Testes Devem Evitar Trabalho Pesado

Testes unitarios nao devem:

- baixar modelo Whisper;
- transcrever video real;
- depender de GPU;
- depender de arquivos grandes;
- depender de rede.

Preferir:

- fakes de `TranscriptionService`;
- entidades pequenas criadas em memoria;
- diretorios temporarios para writers;
- mocks para infraestrutura;
- testes diretos de formatadores.

Quando ainda nao houver testes, rode pelo menos:

```bash
python3 -m compileall -q src
```

## Regra 14: Documentacao Deve Acompanhar Contratos Publicos

Atualize documentacao quando mudar:

- comando de execucao;
- flags da CLI;
- estrutura de pastas;
- contrato de `Transcription`;
- contrato de `TranscriptionService`;
- formato de saida;
- dependencia obrigatoria;
- fluxo de arquitetura.

Use:

- `README.md` para uso pelo usuario;
- `ARCHITECTURE_GUIDELINES.MD` para arquitetura;
- `PROJECT_GUIDELINES.MD` para boas praticas gerais;
- `EVOLUTION_RULES.MD` para regras normativas de evolucao.
- `docs/rules/` para regras pequenas e acionaveis;
- `docs/agents/` para papeis pequenos de revisao, planejamento e implementacao.

## Regra 15: Dependencias Novas Precisam Justificar o Custo

Antes de adicionar dependencia:

- verifique se a biblioteca padrao resolve;
- avalie peso de instalacao;
- avalie impacto em CPU/GPU;
- isole em `infrastructure` se for dependencia externa;
- atualize `requirements.txt`;
- atualize README se houver dependencia de sistema.

Dependencias de IA, audio e video devem ser tratadas como caras por padrao.

## Regra 16: Roadmap Deve Virar Codigo Em Etapas

Roadmap atual indica:

- SRT;
- processamento de pasta inteira;
- subcomandos CLI;
- barra de progresso;
- fallback GPU/CPU;
- multiplos engines;
- workers assincronos;
- cache;
- FastAPI;
- SaaS, busca semantica e highlights.

Ordem recomendada para evolucao segura:

1. Testes e pequenos ajustes de confiabilidade.
2. SRT como novo formatter.
3. Configuracao de formato/modelo/idioma pela CLI.
4. Processamento em lote como novo caso de uso.
5. Contrato de writer se houver multiplos destinos.
6. Fallback GPU/CPU na infraestrutura.
7. Subcomandos CLI se a interface crescer.
8. API web reutilizando casos de uso.
9. Cache/workers quando houver necessidade real.

Nao pule direto para workers, SaaS ou busca semantica antes de estabilizar contratos e testes.

## Regra 17: Refatoracao Deve Ter Escopo Pequeno

Refatore quando:

- remove duplicacao real;
- melhora testabilidade de uma feature concreta;
- reduz acoplamento que ja esta atrapalhando;
- prepara uma mudanca imediata.

Evite refatorar:

- apenas por estetica;
- para criar arquitetura futura sem uso;
- misturando mudanca estrutural com feature grande;
- alterando comportamento publico sem necessidade.

## Regra 18: Arquivos Gerados Nao Guiam Arquitetura

Nao baseie decisoes de codigo em arquivos de saida gerados.

Trate como locais/gerados:

- `outputs/`;
- `videos/`;
- `.venv/`;
- `venv/`;
- `.idea/`;
- `__pycache__/`.

Esses caminhos nao devem ser fonte de contratos.

## Regra 19: Toda Mudanca Deve Ter Criterio de Pronto

Uma mudanca esta pronta quando:

- implementa uma responsabilidade clara;
- respeita as camadas;
- preserva o fluxo existente ou documenta a quebra;
- tem nomes coerentes;
- foi validada localmente;
- atualizou docs quando necessario;
- nao mexeu em arquivos gerados sem motivo.

Checklist minimo:

```bash
python3 -m compileall -q src
git status --short
```

## Regra 20: Em Caso de Duvida, Favoreca Simplicidade

Se houver duas solucoes aceitaveis:

- escolha a menor;
- escolha a mais explicita;
- escolha a que preserva contratos;
- escolha a que exige menos dependencia;
- escolha a que uma pessoa lendo o projeto pela primeira vez consegue seguir.

O objetivo do projeto e aprender, evoluir e manter clareza. Crescimento bom aqui e crescimento que deixa o proximo passo mais obvio, nao mais misterioso.

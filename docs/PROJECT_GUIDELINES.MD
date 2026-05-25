# Project Guidelines e Boas Praticas

Este documento define guidelines genericos para evoluir o `transcrito-app` com consistencia. Use junto com `docs/ARCHITECTURE_GUIDELINES.MD`: o guia de arquitetura explica as camadas; este guia explica como trabalhar no projeto no dia a dia.

## Principios do Projeto

- Mantenha o projeto simples, incremental e facil de estudar.
- Prefira codigo explicito a abstracoes prematuras.
- Preserve a separacao entre dominio, aplicacao, infraestrutura e interfaces.
- Toda dependencia externa deve ficar nas bordas do sistema.
- O fluxo principal deve continuar facil de entender: entrada CLI, caso de uso, contrato de transcricao, implementacao concreta, formatacao e escrita.
- Novas features devem nascer pequenas, testaveis e com responsabilidade clara.

## Idioma e Nomenclatura

Padrao atual:

- documentacao em portugues;
- codigo em ingles;
- mensagens de CLI com estilo amigavel e direto;
- nomes de modulos em `snake_case`;
- classes em `PascalCase`;
- funcoes, metodos e variaveis em `snake_case`.

Regras:

- mantenha nomes de codigo em ingles, por exemplo `TranscribeVideo`, `FileWriter`, `TimestampFormatter`;
- use portugues na documentacao e em textos explicativos;
- use nomes que descrevem responsabilidade, nao tecnologia, exceto em adaptadores concretos;
- nomes de implementacoes concretas podem incluir a tecnologia, por exemplo `WhisperTranscriptionService`;
- evite abreviacoes que dificultem leitura.

Exemplos bons:

```text
src/application/formatters/srt_formatter.py
src/application/transcribe_batch.py
src/infrastructure/whisper_transcription_service.py
```

Exemplos a evitar:

```text
src/application/do_stuff.py
src/domain/whisper_result.py
src/interfaces/cli/utils2.py
```

## Organizacao de Arquivos

Use a estrutura existente como fonte de verdade:

```text
src/
  domain/
  application/
  infrastructure/
  interfaces/
  main.py
```

Ao adicionar arquivos:

- modelos e contratos centrais entram em `src/domain`;
- casos de uso entram em `src/application`;
- formatadores entram em `src/application/formatters`;
- writers entram em `src/application/writers`;
- integracoes externas entram em `src/infrastructure`;
- entrada CLI entra em `src/interfaces/cli`;
- documentacao entra em `docs`;
- saidas geradas entram em `outputs`, mas nao devem ser tratadas como codigo.

Evite criar novos diretorios de topo sem necessidade. Antes de adicionar uma pasta, verifique se uma das camadas existentes ja expressa a responsabilidade.

## Padroes de Codigo Python

Siga o estilo ja presente:

- imports absolutos a partir de `src`;
- type hints em contratos, entidades, casos de uso e funcoes publicas;
- classes pequenas com uma responsabilidade principal;
- funcoes auxiliares puras quando possivel;
- sem efeitos colaterais escondidos em formatadores ou entidades;
- escrita de arquivo sempre com encoding explicito quando for texto.

Exemplo de import preferido:

```python
from src.domain.transcription import Transcription
```

Evite imports relativos entre camadas:

```python
from ..domain.transcription import Transcription
```

Use `pathlib.Path` para caminhos no codigo novo quando houver manipulacao de filesystem.

## Responsabilidade por Tipo de Codigo

Dominio:

- representa conceitos centrais;
- define contratos;
- nao conhece CLI, arquivos reais, Whisper, Torch ou frameworks.

Aplicacao:

- orquestra casos de uso;
- recebe dependencias por construtor;
- chama contratos e componentes auxiliares;
- nao deve carregar modelo Whisper diretamente.

Infraestrutura:

- conversa com bibliotecas externas;
- converte dados externos para entidades do dominio;
- pode depender de `domain`;
- nao deve conter regras de CLI.

Interfaces:

- parseia argumentos;
- valida entrada do usuario;
- mostra mensagens;
- monta objetos para chamar casos de uso;
- nao deve concentrar regra de negocio.

## Criacao de Novas Features

Antes de implementar, identifique a categoria da mudanca:

- novo comportamento de negocio: comece em `domain` ou `application`;
- novo formato de arquivo: crie formatter;
- novo destino de saida: crie writer;
- novo motor de transcricao: crie implementacao em `infrastructure`;
- nova opcao de terminal: altere `interfaces/cli`;
- nova configuracao de dependencia concreta: ajuste `main.py` ou bootstrap equivalente.

Fluxo recomendado:

1. Defina o contrato ou comportamento esperado.
2. Implemente a menor unidade na camada correta.
3. Conecte a feature na borda apropriada.
4. Adicione ou atualize testes quando existirem.
5. Atualize documentacao se mudar uso, fluxo ou arquitetura.

## Configuracoes e Parametros

Valores atuais importantes:

- modelo Whisper: `base`;
- device: `cpu`;
- idioma: `pt`;
- diretorio de saida: `outputs`;
- formato de saida padrao: texto com timestamps.

Boas praticas:

- nao espalhe valores fixos por varios arquivos;
- se um valor passar a ser configuravel, escolha a borda correta para recebe-lo, normalmente CLI ou composition root;
- mantenha defaults compativeis com o comportamento atual;
- documente novas flags no README quando forem expostas para usuario.

## Tratamento de Erros

O projeto deve tratar falhas esperadas com excecoes explicitas por camada. Ao melhorar:

- retorne mensagens claras para o usuario na CLI;
- preserve excecoes tecnicas para logs ou diagnostico quando necessario;
- valide entrada antes de executar trabalho pesado;
- nao esconda falhas silenciosamente;
- evite `except Exception` generico sem uma acao clara;
- prefira erros especificos para arquivo inexistente, dependencia ausente, modelo indisponivel e falha de transcricao.
- traduza falhas de bibliotecas externas na borda de infraestrutura;
- traduza falhas de escrita dentro do writer responsavel;
- capture na CLI os erros especificos que o usuario consegue entender e agir.

Excecoes atuais:

- `ModelLoadError`: falha ao carregar o modelo de transcricao na infraestrutura;
- `TranscriptionExecutionError`: falha durante a execucao da transcricao;
- `FileWriteError`: falha ao escrever o arquivo de saida.

Areas que merecem cuidado:

- ausencia de `ffmpeg`;
- erro ao carregar modelo Whisper;
- video inexistente ou invalido;
- falha ao criar diretorio de saida;
- falha ao escrever arquivo;
- falta de permissao de leitura/escrita.

## CLI e Experiencia do Usuario

A CLI deve continuar objetiva e previsivel.

Boas praticas:

- mensagens curtas;
- status visivel para operacoes demoradas;
- caminhos exibidos quando ajudam o usuario;
- defaults sensatos;
- flags com nomes claros;
- validacoes antes de carregar o modelo quando possivel.

Ao adicionar flags:

- mantenha `--out` funcionando;
- nao quebre o argumento posicional atual de video sem motivo forte;
- prefira nomes explicitos, como `--model`, `--language`, `--device`, `--format`;
- atualize README e docs se a interface publica mudar.

## Formatadores e Saidas

Formatadores transformam `Transcription` em `str`. Eles nao escrevem arquivos.

Boas praticas:

- crie uma classe por formato;
- mantenha formatadores deterministas;
- nao leia arquivos dentro de formatadores;
- nao chame motores de IA dentro de formatadores;
- trate edge cases como lista vazia de segmentos.

Exemplos:

- `TimestampFormatter` para texto com timestamps;
- `SrtFormatter` para legendas;
- `JsonFormatter` para serializacao JSON, se o contrato continuar retornando `str`.

Se um novo formato exigir dados que nao existem em `Transcription`, avalie primeiro se o dominio deve ser expandido.

## Escrita e Persistencia

Writers persistem conteudo pronto.

Boas praticas:

- writer nao deve formatar transcricao;
- writer nao deve chamar servico de transcricao;
- use encoding `utf-8` para arquivos texto;
- aceite `Path` para destinos locais;
- se houver multiplos writers, crie um contrato abstrato em `src/application/writers/base_writer.py`.

## Dependencias

Antes de adicionar dependencias:

- confirme se a biblioteca e realmente necessaria;
- prefira biblioteca padrao quando suficiente;
- mantenha dependencias de infraestrutura fora do dominio;
- atualize `requirements.txt`;
- documente dependencias de sistema no README;
- evite dependencias pesadas para funcionalidades pequenas.

Dependencias relacionadas a IA, audio e video tendem a ser pesadas. Isole-as em `infrastructure`.

## Testes

Nao ha suite de testes configurada atualmente. Quando adicionar testes:

- priorize testes unitarios rapidos;
- nao baixe modelo Whisper em teste unitario;
- nao transcreva videos reais em teste unitario;
- use fakes/mocks para `TranscriptionService`;
- teste formatadores com entidades pequenas;
- teste casos de uso com writers falsos ou diretorios temporarios.

Estrutura sugerida:

```text
tests/
  domain/
  application/
  infrastructure/
  interfaces/
```

Comandos recomendados quando houver testes:

```bash
python3 -m pytest
```

Enquanto nao houver testes:

```bash
python3 -m compileall -q src
```

## Documentacao

Mantenha a documentacao alinhada com o comportamento real.

Use:

- `README.md` para visao geral, setup e uso pelo usuario;
- `docs/ARCHITECTURE_GUIDELINES.MD` para arquitetura, camadas e contratos;
- `docs/PROJECT_GUIDELINES.MD` para boas praticas, convencoes e fluxo de trabalho;
- `docs/EVOLUTION_RULES.MD` para regras normativas de evolucao;
- `docs/rules/` para regras pequenas por tema;
- `docs/agents/` para agentes pequenos por responsabilidade;
- `projectStructure.json` para mapa estruturado consumivel por ferramentas ou LLMs.

Atualize documentacao quando:

- adicionar flags de CLI;
- mudar comando de execucao;
- alterar estrutura de pastas;
- alterar contrato de dominio ou caso de uso;
- adicionar dependencia obrigatoria;
- mudar formato de saida.

## Git e Arquivos Gerados

Nao trate como fonte de verdade:

- `outputs/`;
- `videos/` com midias locais;
- `.venv/`;
- `venv/`;
- `.idea/`;
- `__pycache__/`.

Antes de commitar, confira:

```bash
git status --short
```

Inclua no commit apenas arquivos relacionados a mudanca. Evite misturar documentacao, refatoracao e feature grande no mesmo commit quando puder separar.

## Checklist Para Mudancas

Use este checklist antes de finalizar uma alteracao:

- A mudanca esta na camada correta?
- Alguma dependencia externa entrou no dominio por engano?
- O comportamento atual da CLI foi preservado?
- Os nomes seguem o padrao do projeto?
- O codigo novo tem type hints nos pontos publicos?
- Arquivos gerados ficaram fora da mudanca?
- `README.md` ou docs precisam ser atualizados?
- `python3 -m compileall -q src` passa?
- Testes foram adicionados ou atualizados quando havia risco relevante?

## Checklist Para LLMs

Ao trabalhar neste repositorio:

- leia primeiro `README.md`, `docs/ARCHITECTURE_GUIDELINES.MD` e este arquivo;
- use `rg --files` para mapear arquivos;
- nao altere `.venv`, `venv`, `.idea`, `outputs` ou `__pycache__`;
- nao faca refatoracao ampla sem necessidade;
- preserve a regra de dependencia entre camadas;
- prefira pequenas mudancas coesas;
- explique qualquer decisao que mude contratos ou experiencia de usuario;
- valide o resultado com comando local quando possivel.

## Anti-Padroes Gerais

Evite:

- colocar tudo em `commands.py`;
- criar utilitarios genericos sem uso real;
- adicionar uma abstracao para uma unica implementacao sem necessidade clara;
- acoplar caso de uso a Whisper;
- misturar parse de CLI com regra de negocio;
- misturar formatacao com escrita;
- capturar erro e apenas imprimir mensagem sem encerrar ou retornar estado claro;
- mudar defaults publicos sem atualizar documentacao;
- usar arquivos de saida como fixtures permanentes sem declarar essa intencao;
- adicionar dependencia nova sem revisar impacto de instalacao.

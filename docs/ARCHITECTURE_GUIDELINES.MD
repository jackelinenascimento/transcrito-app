# Architecture Guidelines para LLMs

Este documento descreve os padroes arquiteturais, convenções e pontos de extensão do `transcrito-app`. Use-o como contexto principal antes de alterar o projeto.

## Visao Geral

`transcrito-app` e uma ferramenta CLI em Python para transcricao de videos usando Whisper. O projeto foi estruturado para estudo e evolucao incremental com principios de Clean Architecture.

Objetivos declarados no repositório:

- transcrever arquivos de video para texto;
- manter o dominio independente de bibliotecas externas como Whisper;
- permitir novos motores de transcricao;
- permitir novos formatos de saida, como SRT;
- permitir diarização (speaker separation) como comportamento padrão ao executar a transcrição;
- preparar a base para processamento em lote, interface web, workers assincronos, cache e busca.

Comando principal esperado:

```bash
python -m src.main videos/test.mp4
```

Saida padrao:

```text
outputs/<nome-do-video>.txt
```

## Stack e Dependencias

Linguagem:

- Python 3.10+.

Dependencias Python atuais em `requirements.txt`:

- `openai-whisper>=20231117`;
- `torch`.

Dependencia de sistema:

- `ffmpeg`, necessario para o Whisper processar midia.

Nao ha framework web, banco de dados, sistema de filas ou suite de testes configurada atualmente.

## Estrutura Atual

```text
src/
  __init__.py
  main.py

  domain/
    __init__.py
    transcription.py
    transcription_service.py

  application/
    __init__.py
    transcribe_video.py

    formatters/
      __init__.py
      base_formatter.py
      timestamp_formatter.py

    utils/
      __init__.py
      time_formatter.py

    writers/
      __init__.py
      file_writer.py

  infrastructure/
    __init__.py
    whisper_transcription_service.py

  interfaces/
    __init__.py
    cli/
      __init__.py
      commands.py
```

Diretorios locais/gerados:

- `outputs/`: arquivos de transcricao gerados.
- `videos/`: local sugerido para videos de entrada.
- `.venv/` e `venv/`: ambientes virtuais locais.
- `.idea/`: configuracao local de IDE.
- `__pycache__/`: artefatos gerados pelo Python, nao devem ser usados como fonte de verdade.

## Regra de Dependencia

O projeto segue a intencao de Clean Architecture:

```text
interfaces -> application -> domain
infrastructure -> domain
main -> infrastructure + interfaces
```

Regra principal:

- camadas externas podem conhecer camadas internas;
- camadas internas nao devem conhecer camadas externas;
- `domain` nao deve importar `application`, `infrastructure`, `interfaces`, Whisper, argparse, pathlib para IO concreto, nem qualquer detalhe de CLI;
- `application` pode depender de contratos do `domain` e de componentes auxiliares da propria camada;
- `infrastructure` implementa contratos definidos no `domain`;
- `interfaces` adapta entradas externas, como CLI, para casos de uso da aplicacao;
- `main.py` e o composition root atual: instancia implementacoes concretas e inicia a interface.

Evite mover dependencias externas para dentro do dominio. Whisper, Torch, ffmpeg, filesystem real e argparse pertencem as bordas.

## Fluxo de Execucao

Fluxo atual:

```text
src/main.py
  -> cria WhisperTranscriptionService("base")
  -> chama run(service)

src/interfaces/cli/commands.py
  -> parseia argumentos com argparse
  -> valida existencia do video
  -> cria diretorio de saida
  -> instancia TimestampFormatter ou SrtFormatter dependendo de --format
  -> instancia FileWriter
  -> instancia TranscribeVideo(service, formatter, writer)
  -> executa o caso de uso
  -> imprime status e caminho final

src/application/transcribe_video.py
  -> service.transcribe(video_path)
  -> formatter.format(transcription)
  -> writer.write(formatted_text, output_file)
  -> retorna Path do arquivo gerado

src/infrastructure/whisper_transcription_service.py
  -> carrega modelo Whisper
  -> transcreve video (idioma configuravel)
  -> converte retorno bruto para entidades de dominio
  -> se o motor fornecer labels de speaker, eles devem ser convertidos para o campo `speaker` dos segmentos
```

## Camadas e Responsabilidades

### `src/domain`

Contem o nucleo conceitual do sistema.

Arquivos:

- `transcription.py`: define as entidades `TranscriptionSegment` e `Transcription`.
- `transcription_service.py`: define o contrato abstrato `TranscriptionService`.

Padroes:

- use `dataclass` para entidades simples de dados;
- mantenha campos explicitamente tipados;
- contratos devem usar `ABC` e `@abstractmethod`;
- o dominio deve ser portavel e testavel sem Whisper, CLI ou arquivos reais.

Entidades atuais:

```python
@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcription:
    text: str
    segments: List[TranscriptionSegment]
    language: str | None = None
```

Contrato atual:

```python
class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, video_path: str) -> Transcription:
        pass
```

Ao adicionar conceitos como legenda, resumo, speaker diarization ou metadados, prefira modelar primeiro em `domain` quando forem conceitos de negocio, nao detalhes tecnicos de uma biblioteca.

### `src/application`

Contem casos de uso e componentes de aplicacao.

Arquivo principal:

- `transcribe_video.py`: caso de uso `TranscribeVideo`.

Novas responsabilidades relevantes:

- ao orquestrar a transcricao, o caso de uso tambem pode aplicar uma heuristica de atribuicao de speakers quando o motor de transcricao nao fornecer labels;
- o caso de uso recebe configuracoes como `diarize`, `gap_threshold` e `max_speakers` injetadas pela CLI/composition root;

Padrao atual de caso de uso:

- classe com dependencias recebidas no construtor;
- metodo `execute(...)` para executar a operacao;
- nao instancia Whisper diretamente;
- coordena contrato de transcricao, formatador e escritor;
- retorna o caminho do arquivo final.

Assinatura atual:

```python
class TranscribeVideo:
    def __init__(
      self,
      service: TranscriptionService,
      formatter: TranscriptionFormatter,
      writer: FileWriter,
      diarize: bool = False,
      gap_threshold: float = 1.5,
      max_speakers: int = 0,
    ):
        ...

    def execute(self, video_path: str, output_dir: Path) -> Path:
        ...
```

Observacao importante: `writer` hoje esta tipado diretamente como `FileWriter`, que e concreto. Se forem adicionadas novas estrategias de escrita, crie um contrato abstrato em `application/writers` para reduzir acoplamento.

Subpacotes:

- `formatters/`: transforma `Transcription` em texto ou outros formatos.
- `writers/`: grava conteudo formatado em algum destino.
- `utils/`: funcoes utilitarias sem estado.

### `src/application/formatters`

Responsabilidade:

- converter entidades de dominio para uma representacao de saida.

Contrato:

```python
class TranscriptionFormatter(ABC):
    @abstractmethod
    def format(self, transcription: Transcription) -> str:
        pass
```

Implementacao atual:

- `TimestampFormatter`: gera texto com blocos contendo timestamp e trecho.

Implementacoes adicionais:

- `SrtFormatter`: gera legendas no formato SRT e inclui rótulos de speaker quando presentes no segmento.

Formato atual aproximado:

```text
[00:12]
Texto do segmento

[00:18]
Outro segmento
```

Funcao auxiliar atual:

```python
def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"
```

Cuidados:

- o formato atual e `MM:SS`, sem horas e sem milissegundos;
- para SRT, crie outro formatter, por exemplo `SrtFormatter`, sem alterar o contrato base se `str` continuar suficiente;
- nao coloque escrita em arquivo dentro do formatter;
- nao coloque chamadas ao Whisper dentro do formatter.

Ao adicionar diarizacao:

- prefira implementar a diarizacao no nivel de infraestrutura (um provider que rode pyannote/whisperx), que retorna `speaker` em cada segmento; a camada `application` deve apenas escolher usar os labels do provider ou aplicar a heuristica de fallback;
- se preferir uma heuristica leve, coloque-a no caso de uso `TranscribeVideo` (ja existe uma implementada que atribui `Speaker N` incrementais quando ha pausas maiores que `gap_threshold`).

### `src/application/writers`

Responsabilidade:

- persistir conteudo formatado.

Implementacao atual:

```python
class FileWriter:
    def write(self, content: str, output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
```

Padroes:

- escrita em UTF-8;
- recebe `Path` para destino;
- nao deve conhecer Whisper nem regras de transcricao.

Possivel evolucao:

- criar `base_writer.py` com contrato `Writer`;
- implementar `FileWriter`, `StdoutWriter`, `StorageWriter` etc.

### `src/application/utils`

Responsabilidade:

- funcoes pequenas, puras e reutilizaveis.

Funcao atual:

- `format_duration(seconds: float) -> str`, usada pela CLI para mostrar duracao total.

Formato atual:

- com horas: `01h 02m 03s`;
- sem horas: `02m 03s`.

Nao coloque regras de negocio complexas em `utils`. Se uma regra virar conceito central, modele em `domain` ou `application`.

### `src/infrastructure`

Responsabilidade:

- integrar bibliotecas externas e detalhes tecnicos.

Implementacao atual:

- `WhisperTranscriptionService`, implementa `TranscriptionService`.

Comportamento atual:

- importa `whisper`;
- suprime warnings globalmente com `warnings.filterwarnings("ignore")`;
- carrega o modelo no construtor;
- usa `whisper.load_model(model_name, device="cpu")`;
- transcreve com `language="pt"`;
- converte `result["segments"]` para `TranscriptionSegment`;
- retorna `Transcription`.

Assinatura:

```python
class WhisperTranscriptionService(TranscriptionService):
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name, device="cpu")

    def transcribe(self, video_path: str) -> Transcription:
        ...
```

Cuidados:

- nao vazar o dicionario bruto do Whisper para `application` ou `domain`;
- sempre converter resultados externos para entidades do dominio;
- se adicionar GPU, idioma configuravel ou modelos diferentes, exponha isso por parametros injetados, sem acoplar o dominio;
- carregar o modelo no construtor tem custo alto; considere lazy loading apenas se isso for uma necessidade clara.

### `src/interfaces/cli`

Responsabilidade:

- adaptar argumentos e interacao de terminal para os casos de uso.

Arquivo atual:

- `commands.py`, funcao `run(service)`.

Comportamento atual:

- usa `argparse`;
- recebe argumento posicional `video`;
- recebe `--out`, com padrao `outputs`;
- valida se o video existe;
- cria diretorio de saida com `mkdir(exist_ok=True)`;
- imprime status com emojis;
- mede tempo total com `time.perf_counter()`;
- instancia formatter, writer e caso de uso;
- executa a transcricao.

Pontos de atencao:

- a CLI imprime `Engine: Whisper (base | CPU)` fixo, mesmo recebendo `service` por injecao. Se modelos/dispositivos virarem configuraveis, atualize esse texto para nao mentir;
- a mensagem `Writing file...` e impressa depois de `use_case.execute(...)`, mas a escrita ja aconteceu dentro do caso de uso. Se quiser progresso mais fiel, mova ou ajuste a mensagem;
- `output_dir.mkdir(exist_ok=True)` nao cria pais intermediarios. Para paths aninhados, use `parents=True, exist_ok=True`.

### `src/main.py`

Responsabilidade:

- composition root atual.

Comportamento:

- instancia `WhisperTranscriptionService("base")`;
- chama `run(service)`.

Padrao:

- deixe a montagem de dependencias concretas aqui ou em um modulo de bootstrap dedicado;
- evite espalhar instanciacao de infraestrutura por casos de uso ou dominio.

## Convencoes de Codigo Observadas

Estilo:

- imports absolutos a partir de `src`, por exemplo `from src.domain.transcription import Transcription`;
- classes em `PascalCase`;
- funcoes, metodos e variaveis em `snake_case`;
- type hints nos principais contratos e entidades;
- linhas em branco separando imports, classes e funcoes;
- sem docstrings atualmente;
- comentarios praticamente inexistentes.

Idioma:

- documentacao e README em portugues;
- nomes de codigo em ingles;
- mensagens de CLI misturam ingles com icones.

Caracteres:

- o codigo ja usa emojis e caracteres Unicode na CLI;
- para novos arquivos de documentacao, portugues com acentos e aceitavel;
- para codigo, preserve o estilo existente e evite Unicode fora de mensagens visuais.

## Como Adicionar Funcionalidades

### Novo motor de transcricao

Exemplo: adicionar outro engine alem do Whisper.

1. Crie uma classe em `src/infrastructure`.
2. Faça a classe herdar de `TranscriptionService`.
3. Implemente `transcribe(video_path: str) -> Transcription`.
4. Converta o resultado externo para `Transcription` e `TranscriptionSegment`.
5. Injete a nova implementacao em `src/main.py` ou via CLI/configuracao.

Nao altere `TranscribeVideo` se o contrato continuar o mesmo.

### Novo formato de saida

Exemplo: SRT, JSON, Markdown.

1. Crie um formatter em `src/application/formatters`.
2. Herde de `TranscriptionFormatter`.
3. Implemente `format(transcription: Transcription) -> str`.
4. Escolha o formatter na camada de interface ou composition root.

Nao coloque escolha de formato dentro do dominio.

### Processamento em lote

Preferencia arquitetural:

- crie um novo caso de uso, por exemplo `TranscribeBatch`;
- ele pode orquestrar multiplas chamadas a `TranscribeVideo` ou compartilhar componentes;
- a CLI deve apenas parsear a pasta/lista de arquivos e delegar.

Evite colocar loop de processamento complexo diretamente em `commands.py`.

### Subcomandos CLI

Se a CLI crescer:

- mantenha `interfaces/cli` como camada de entrada;
- separe comandos por arquivo quando `commands.py` ficar grande;
- use `argparse` subparsers ou outra lib de CLI somente se justificar;
- preserve os casos de uso em `application`.

### API Web ou FastAPI

Se uma interface web for adicionada:

- crie novo pacote em `src/interfaces/http` ou `src/interfaces/api`;
- reutilize casos de uso de `application`;
- nao mova regras da CLI para a API;
- nao faca `domain` depender de FastAPI/Pydantic;
- se precisar de schemas HTTP, mantenha-os na camada de interface.

## Testabilidade Esperada

Ainda nao ha testes no repositorio.

Quando adicionar testes, caminhos sugeridos:

```text
tests/
  domain/
  application/
  infrastructure/
  interfaces/
```

Prioridades de teste:

- `TimestampFormatter.format`;
- `format_timestamp`;
- `format_duration`;
- `TranscribeVideo.execute` com doubles/fakes de service, formatter e writer;
- `WhisperTranscriptionService` apenas com mock do Whisper, para evitar download/modelo real em teste unitario;
- CLI com monkeypatch ou teste de argumentos, sem transcrever video real.

Para testar o caso de uso, prefira fakes:

```python
class FakeTranscriptionService(TranscriptionService):
    def transcribe(self, video_path: str) -> Transcription:
        return Transcription(...)
```

Nao rode Whisper real em testes unitarios.

## Contratos e Dados

`TranscriptionSegment`:

- `start`: segundos como `float`;
- `end`: segundos como `float`;
- `text`: texto do segmento.

`Transcription`:

- `text`: texto completo;
- `segments`: lista de segmentos;
- `language`: idioma detectado ou definido, opcional.

Contrato de transcricao:

- entrada: caminho de video como `str`;
- saida: `Transcription`.

Contrato de formatacao:

- entrada: `Transcription`;
- saida: `str`.

Contrato implicito de escrita:

- entrada: conteudo `str` e destino `Path`;
- efeito: cria/sobrescreve arquivo em UTF-8.

Erros esperados:

- `ModelLoadError`: falha ao carregar o modelo de transcricao na infraestrutura;
- `TranscriptionExecutionError`: falha durante a execucao da transcricao;
- `FileWriteError`: falha ao escrever o arquivo de saida.

## Decisoes Atuais Importantes

- O modelo Whisper padrao e `base`.
- O dispositivo esta fixo em CPU.
- O idioma esta fixo como portugues (`pt`).
- A saida padrao e TXT com timestamps.
- O nome do arquivo de saida usa `Path(video_path).stem + ".txt"`.
- O diretorio de saida padrao e `outputs`.
- A CLI valida apenas existencia do caminho, nao extensao nem tipo de arquivo.
- A aplicacao sobrescreve arquivo de saida com mesmo nome sem confirmacao.

## Riscos e Pontos de Melhoria

Riscos atuais:

- `warnings.filterwarnings("ignore")` e global e pode esconder problemas.
- CLI tem textos fixos sobre engine/dispositivo.
- `outputs/`, `.idea/`, `requirements.txt` e `projectStructure.json` aparecem como nao rastreados no estado atual do Git.

Melhorias provaveis:

- criar testes unitarios para application e formatters;
- adicionar contrato abstrato para writers;
- tornar modelo, device e idioma configuraveis;
- adicionar SRT formatter;
- adicionar batch use case;
- melhorar erros de CLI com codigos de saida;
- atualizar `.gitignore` para `__pycache__/`, outputs locais e ambientes virtuais, caso ainda nao esteja adequado.

## Regras Para LLMs ao Modificar o Projeto

Antes de alterar:

- leia os arquivos da camada afetada;
- respeite a direcao das dependencias;
- prefira adicionar implementacoes nas bordas em vez de acoplar o dominio;
- preserve imports absolutos a partir de `src`;
- mantenha o caso de uso independente de Whisper;
- nao use arquivos gerados em `outputs/` como codigo-fonte;
- nao altere ambientes virtuais, `.idea` ou `__pycache__`;
- evite refatoracoes amplas sem necessidade.

Ao implementar:

- coloque regras centrais em `domain` ou `application`;
- coloque integracoes externas em `infrastructure`;
- coloque parsing, prints e detalhes de entrada em `interfaces`;
- injete dependencias concretas a partir de `main.py` ou da interface;
- converta dados externos para entidades do dominio o quanto antes;
- mantenha funcoes pequenas e tipos explicitos.

Ao finalizar:

- valide sintaxe Python se alterar codigo;
- rode testes se existirem;
- se nao existirem testes, pelo menos valide imports/compilacao com `python3 -m compileall src`;
- documente qualquer mudanca de fluxo, contrato ou comando de uso.

## Exemplos de Onde Colocar Codigo

Novo `JsonFormatter`:

```text
src/application/formatters/json_formatter.py
```

Novo `SrtFormatter`:

```text
src/application/formatters/srt_formatter.py
```

Novo motor `FasterWhisperTranscriptionService`:

```text
src/infrastructure/faster_whisper_transcription_service.py
```

Novo caso de uso de pasta inteira:

```text
src/application/transcribe_batch.py
```

Novos subcomandos CLI:

```text
src/interfaces/cli/commands.py
```

ou, se crescer:

```text
src/interfaces/cli/transcribe_command.py
src/interfaces/cli/batch_command.py
```

Contrato novo de writer:

```text
src/application/writers/base_writer.py
```

## Anti-Padroes Para Evitar

- Importar `whisper` dentro de `domain` ou `application`.
- Criar arquivos em `outputs/` como parte da implementacao.
- Colocar `argparse` dentro de casos de uso.
- Fazer `TranscribeVideo` escolher o modelo Whisper.
- Retornar dicionarios crus do Whisper para fora da infraestrutura.
- Misturar formatacao de texto com escrita em arquivo.
- Colocar regras de CLI dentro das entidades.
- Adicionar dependencias pesadas sem atualizar `requirements.txt` e documentacao.
- Rodar transcricao real como teste automatizado padrao.

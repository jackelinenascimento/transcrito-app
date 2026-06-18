# Transcrito App

Ferramenta de linha de comando (CLI) para transcrição de vídeo para texto usando Whisper, organizada segundo princípios de Clean Architecture.

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação rápida](#instalação-rápida)
- [Uso](#uso)
- [Opções principais](#opções-principais)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Desenvolvimento e testes](#desenvolvimento-e-testes)
- [Documentação adicional](#documentação-adicional)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Visão geral

O projeto fornece um pipeline simples para transcrever vídeos em texto, gerar legendas (SRT) e experimentar estratégias de diariização (speaker diarization). O código segue Clean Architecture: o domínio é independente de frameworks e das implementações concretas de transcrição.

## Funcionalidades

- Transcrição de arquivos de vídeo para texto
- Geração de arquivos de legenda no formato SRT
- Separação por camadas (domain, application, infrastructure, interfaces)
- Extensível para múltiplos motores de transcrição
- Heurística de fallback para diarização quando não disponível
- Heurística de atribuição de speakers extraída como componente testável (`SpeakerAssigner`)

## Requisitos

- Python 3.10+
- ffmpeg (para extrair/normalizar áudio de vídeos)

No Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

## Instalação rápida

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale dependências principais:

```bash
pip install -r requirements.txt
```

3. (Opcional) Dependências para diarização avançada:

```bash
pip install -r requirements-diarization.txt
```

## Uso

Coloque um vídeo na pasta `videos/` ou passe o caminho para o arquivo. Exemplos:

Transcrever um arquivo e gerar saída em `outputs/` (padrão):

```bash
python -m src.main videos/test.mkv
```

Exemplo com opções:

```bash
python -m src.main videos/test.mkv --out outputs --model base --device cpu --language pt --format srt
```

## Opções principais

- `--out`: diretório de saída (padrão `outputs`)
- `--model`: modelo Whisper a ser usado (ex.: `tiny`, `base`, `small`)
- `--device`: dispositivo para inferência (`cpu` ou `cuda`)
- `--language`: idioma da transcrição (`pt`, `en`, ...)
- `--format`: formato de saída (`txt`, `srt`)
- `--diarize`: ativa diarização quando suportada pelo provedor
- `--gap-threshold`: limiar (s) para heurística de novo locutor (padrão 1.5)
- `--max-speakers`: máximo de speakers para heurística (0 = ilimitado)

Para ver todas as opções, execute o comando sem argumentos ou com `-h`:

```bash
python -m src.main -h
```

## Estrutura do projeto

A organização principal está em `src/` seguindo Clean Architecture. Um resumo das pastas:

- `src/domain/` — entidades, contratos e exceções do domínio
- `src/application/` — casos de uso e formatadores (SRT, timestamp)
- `src/infrastructure/` — implementações concretas (ex.: Whisper)
- `src/interfaces/cli/` — adaptadores de entrada (CLI)
- `docs/` — documentação do projeto e guias

O arquivo `projectStructure.json` contém uma visão estruturada do repositório.

## Desenvolvimento e testes

Instale dependências de desenvolvimento (opcional):

```bash
pip install -r requirements-dev.txt
```

Rode a suíte de testes:

```bash
pytest -q
```

Testes específicos

 - Testes da heurística de atribuição de speakers estão em `tests/test_speaker_assigner.py`.
 - Para rodar apenas esses testes:

```bash
PYTHONPATH="$(pwd)" pytest tests/test_speaker_assigner.py -q
```

## Documentação adicional

A pasta `docs/` contém guidelines de arquitetura, regras do projeto e documentos auxiliares. Veja `docs/README.md` para um índice da documentação interna.

## Contribuição

Contribuições são bem-vindas. Para pequenos ajustes, abra um issue ou envie um pull request. Siga as diretrizes de estilo do projeto (pequenas mudanças primeiro; escreva testes para comportamentos novos/alterados).

## Licença

Este projeto é licenciado sob MIT — veja o arquivo `LICENSE` para detalhes.


---

Arquivo gerado/atualizado automaticamente: mantenha o `README.md` em sincronia com `docs/` e `projectStructure.json`.

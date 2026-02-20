# Transcrito App

Ferramenta CLI para transcrição de vídeos utilizando Whisper com uma estrutura baseada em Clean Architecture.

O projeto foi criado para estudar design de software, modelagem de domínio e pipelines de IA, mantendo a base preparada para evoluir para uma aplicação completa com interface web, múltiplos engines e processamento assíncrono.

## Funcionalidades

• Transcrição de arquivos de vídeo para texto
• Separação por Clean Architecture (domain, application, infrastructure, interfaces)
• Estrutura preparada para processamento em lote
• Entidade de domínio com segmentos e timestamps
• Base pronta para geração de legendas (SRT)
• Fácil extensão para outros engines de transcrição

## Arquitetura

O projeto segue princípios de Clean Architecture.

O núcleo não depende de bibliotecas externas como Whisper.

Fluxo:

CLI → Caso de uso → Serviço de transcrição (contrato) → Implementação Whisper → Entidade de domínio → Saída

Estrutura:

```
src/
  domain/
    transcription.py
    transcription_service.py

  application/
    transcribe_video.py

  infrastructure/
    whisper_transcription_service.py

  interfaces/
    cli/
      commands.py

  main.py
```

## Requisitos

Python 3.10+

Dependência de sistema:

```
ffmpeg
```

Instalação no Ubuntu:

```
sudo apt install ffmpeg
```

Dependências Python:

```
pip install -r requirements.txt
```

## Setup

Criar ambiente virtual:

```
python -m venv .venv
source .venv/bin/activate
```

Instalar dependências:

```
pip install -r requirements.txt
```

## Uso

Coloque um vídeo na pasta `videos` ou passe o caminho diretamente.

Executar:

```
python -m src.main videos/test.mp4
```

A saída será gerada em:

```
outputs/
```

O arquivo conterá a transcrição completa.

## Modelo de Domínio

A entidade principal é `Transcription`.

Ela contém:

• texto completo
• idioma
• segmentos com tempo de início e fim

Isso permite evoluções como legendas, busca por trecho, resumo e edição de vídeo.

## Próximos Passos (Roadmap)

Curto prazo:

• Geração de legendas SRT
• Processamento de pasta inteira
• Subcomandos CLI
• Barra de progresso
• Fallback automático GPU/CPU

Médio prazo:

• Múltiplos engines de transcrição
• Workers assíncronos
• Cache
• Interface com FastAPI

Longo prazo:

• Plataforma SaaS
• Base de conhecimento em vídeo
• Busca semântica
• Geração automática de highlights

## Objetivo

Este projeto faz parte de uma jornada de estudo focada em:

• Clean Architecture
• Modelagem de domínio
• Desenvolvimento assistido por IA
• Ferramentas CLI
• Design de sistemas escaláveis

## Licença

MIT

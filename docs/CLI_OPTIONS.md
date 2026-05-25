# Opções da CLI — Transcrito App

Este documento descreve as opções expostas pela CLI (extraído de `src/interfaces/cli/commands.py`).

Posicional

- `video`: Path to the video file — arquivo de vídeo a ser transcrito.

Opções

- `--out` (default: `outputs`)
  - Diretório onde os arquivos gerados serão salvos. O diretório será criado quando necessário.

- `--model` (default: `base`)
  - Nome do modelo Whisper a ser usado (ex.: `tiny`, `base`, `small`, ...).

- `--device` (default: `cpu`)
  - Dispositivo de inferência (`cpu` ou `cuda` quando disponível).

- `--language` (default: `pt`)
  - Idioma da transcrição (`pt`, `en`, ...).

- `--format` (default: `txt`, choices: `txt`, `srt`)
  - Formato de saída. `txt` produz um arquivo de texto com timestamps; `srt` gera legendas.

- `--diarize` (flag)
  - Solicita ao provedor de transcrição que retorne informações de diarização. Quando não disponível, o aplicativo tenta usar uma heurística baseada em gaps entre segmentos.

- `--gap-threshold` (default: 1.5)
  - Limiar em segundos usado pela heurística para detectar mudança de locutor.

- `--max-speakers` (default: 0)
  - Número máximo de speakers que a heurística deve criar (0 = ilimitado).

Mensagens e comportamentos ligados às opções

- `--format srt` carrega `SrtFormatter` internamente.
- Ao criar o serviço (`WhisperTranscriptionService`) o CLI passa `model`, `device` e `language`.
- `--diarize` tenta importar `StubDiarizationProvider` (se presente) e usa como `diarization_provider` no caso de uso.

Observação para desenvolvedores

- A função `run(service_factory)` permite passar:
  - uma classe (ex.: `WhisperTranscriptionService`) — será instanciada,
  - uma função factory (`callable`) — será chamada com os mesmos parâmetros,
  - ou uma instância já criada (objeto com método `transcribe`).

Se desejar, posso gerar um `docs/CLI_EXAMPLES.md` com saídas simuladas e explicações linha a linha.
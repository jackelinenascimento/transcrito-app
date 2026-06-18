# Guia rápido de uso — Transcrito App

Este documento mostra exemplos práticos de uso da CLI do Transcrito App.

Requisitos básicos

- Python 3.10+
- ffmpeg disponível no PATH
- Dependências Python instaladas (`pip install -r requirements.txt`)

Exemplos

1) Transcrever um vídeo para texto (saída em `outputs/`):

```bash
python -m src.main videos/test.mkv
```

2) Transcrever e gerar SRT (legendas):

```bash
python -m src.main videos/test.mkv --format srt --out outputs
```

3) Usar modelo e device específicos (ex.: `base` e `cpu`):

```bash
python -m src.main videos/test.mkv --model base --device cpu
```

4) Habilitar diarização (se o provedor suportar) ou usar a heurística de gaps:

```bash
python -m src.main videos/test.mkv --diarize --gap-threshold 1.5 --max-speakers 4
```

5) Exemplo completo com todas as opções:

```bash
python -m src.main videos/test.mkv --out outputs --model small --device cuda --language pt --format srt --diarize --gap-threshold 2.0 --max-speakers 0
```

Mensagens comuns

- "Video not found": verifique o caminho passado como argumento posicional.
- "ffmpeg not found": instale ffmpeg (`sudo apt install ffmpeg`).
- Mensagens sobre carregamento de modelo: o CLI captura e imprime `ModelLoadError` quando o serviço de transcrição falha ao carregar o modelo.

Notas

- Por padrão a CLI usa o adapter `WhisperTranscriptionService` quando disponível. É possível passar um factory ou uma instância diferente ao chamar `run()` em código (útil para testes ou para trocar o engine programaticamente).
- A saída é escrita pelo `FileWriter` e o formatter padrão é `TimestampFormatter` (quando `--format txt`) ou `SrtFormatter` (quando `--format srt`).

Notas sobre a heurística de speakers

- A heurística de atribuição de speakers (quando o provedor não fornece labels)
	agora é disponibilizada pela classe `SpeakerAssigner` em
	`src/application/speaker_assigner.py`. Isso facilita testes e permite
	configurar `gap_threshold` e `max_speakers` por argumento de CLI.

Testes relacionados

- Trestes unitários da heurística: `tests/test_speaker_assigner.py`.

Se precisar, posso gerar exemplos mais detalhados (saída esperada, trechos de SRT gerados, ou um tutorial passo-a-passo com um vídeo de exemplo).
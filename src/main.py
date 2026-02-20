from src.infrastructure.whisper_transcription_service import WhisperTranscriptionService
from src.interfaces.cli.commands import run


def main():
    service = WhisperTranscriptionService("base")
    run(service)


if __name__ == "__main__":
    main()
from src.interfaces.cli.commands import run


def main():
    try:
        from src.infrastructure.whisper_transcription_service import WhisperTranscriptionService
    except ModuleNotFoundError:
        print("Whisper package is not installed. To run the CLI with the default engine install dependencies:")
        print("  pip install -r requirements.txt")
        return

    run(WhisperTranscriptionService)


if __name__ == "__main__":
    main()

from pathlib import Path
from src.domain.transcription_service import TranscriptionService


class TranscribeVideo:

    def __init__(self, service: TranscriptionService):
        self.service = service

    def execute(self, video_path: str, output_dir: Path):
        transcription = self.service.transcribe(video_path)

        output_file = output_dir / (Path(video_path).stem + ".txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription.text)
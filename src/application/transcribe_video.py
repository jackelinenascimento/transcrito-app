from pathlib import Path

from src.application.formatters.base_formatter import TranscriptionFormatter
from src.application.writers.file_writer import FileWriter
from src.domain.transcription_service import TranscriptionService


class TranscribeVideo:

    def __init__(
            self,
            service: TranscriptionService,
            formatter: TranscriptionFormatter,
            writer: FileWriter
    ):
        self.service = service
        self.formatter = formatter
        self.writer = writer

    def execute(self, video_path: str, output_dir: Path) -> Path:
        transcription = self.service.transcribe(video_path)

        formatted_text = self.formatter.format(transcription)

        output_file = output_dir / f"{Path(video_path).stem}.txt"

        self.writer.write(formatted_text, output_file)

        return output_file

import argparse
from pathlib import Path
from src.application.transcribe_video import TranscribeVideo


def run(service):
    parser = argparse.ArgumentParser(prog="transcrito")
    parser.add_argument("video")
    parser.add_argument("--out", default="outputs")

    args = parser.parse_args()

    output_dir = Path(args.out)
    output_dir.mkdir(exist_ok=True)

    use_case = TranscribeVideo(service)
    use_case.execute(args.video, output_dir)

    print("✅ Transcription completed")
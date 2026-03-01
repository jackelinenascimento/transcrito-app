import argparse
import time
from pathlib import Path

from src.application.formatters.timestamp_formatter import TimestampFormatter
from src.application.transcribe_video import TranscribeVideo
from src.application.writers.file_writer import FileWriter
from src.application.utils.time_formatter import format_duration


def run(service):
    parser = argparse.ArgumentParser(prog="transcrito")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("--out", default="outputs", help="Path to the output directory")

    args = parser.parse_args()

    video_path = Path(args.video)

    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return

    output_dir = Path(args.out)
    output_dir.mkdir(exist_ok=True)

    print("\n🎬 Transcrito App")
    print("────────────────────────")
    print(f"📂 Video: {video_path}")
    print("🧠 Engine: Whisper (base | CPU)\n")

    print("⏳ Transcribing...")

    start_time = time.perf_counter()

    formatter = TimestampFormatter()
    writer = FileWriter()
    use_case = TranscribeVideo(service, formatter, writer)

    output_file = use_case.execute(str(video_path), output_dir)

    print("💾 Writing file...")

    duration = time.perf_counter() - start_time

    print("\n────────────────────────")
    print("✅ Done")
    print(f"⏱ Total time: {format_duration(duration)}")
    print(f"📄 Output: {output_file}\n")

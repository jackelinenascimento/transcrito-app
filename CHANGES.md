# Changelog (work-in-progress)

This file summarizes the changes made in this feature branch/work:

- Add speaker diarization support (default behavior):
  - Domain: add optional `speaker` field to `TranscriptionSegment`.
  - Infrastructure: propagate `speaker` from Whisper segments when present.
  - Application: `TranscribeVideo` gets new options `diarize`, `gap_threshold`, `max_speakers` and a `diarization_provider` hook; implements an incremental heuristic that assigns `Speaker N` when pauses > `gap_threshold`.
  - Interface: CLI flags `--diarize`, `--gap-threshold`, `--max-speakers`.

- Add SRT output support:
  - `SrtFormatter` implemented in `src/application/formatters/srt_formatter.py`.
  - CLI now accepts `--format srt`.

- Add a small Diarization provider contract and a `StubDiarizationProvider` in `src/infrastructure/diarization_provider.py` for demonstration and testing. The provider assigns speakers deterministically for demo.

- Tests:
  - Added/updated tests to cover timestamp formatting with speakers, SRT formatting and transcribe use case speaker assignments.
  - Updated CLI tests to reflect default speaker assignment.

- Docs:
  - Updated `README.md`, `docs/ARCHITECTURE_GUIDELINES.MD`, `docs/PROJECT_GUIDELINES.MD`, `docs/EVOLUTION_RULES.MD` to document new flags, SRT support and diarization guidance.

Suggested commit message (single commit):

```
feat: add speaker diarization support, SRT formatter and CLI flags

- Add optional speaker field to domain segments
- Add stub diarization provider and integration point in TranscribeVideo
- Implement heuristic-based speaker assignment (gap threshold, incremental speakers)
- Add SRT formatter and support via `--format srt`
- Add CLI flags: --diarize, --gap-threshold, --max-speakers
- Update tests and documentation
```

Notes:
- The diarization provider included is a lightweight stub for tests/demo only. Integrate a real provider (pyannote/whisperx) in `src/infrastructure` when ready and update `requirements.txt` accordingly.
- Consider adding CLI documentation examples and a sample integration test for the real provider in a follow-up.

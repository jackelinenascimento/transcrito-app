# Changelog

All notable changes to this project will be documented in this file.

The format is based on "Keep a Changelog" and this project adheres to
Semantic Versioning. See https://keepachangelog.com/en/1.0.0/ for details.

## [Unreleased]


## [0.2.0] - 2026-06-18

### Added

- Extracted speaker-assignment heuristic into a testable component
  `SpeakerAssigner` (`src/application/speaker_assigner.py`).
- Unit tests for `SpeakerAssigner` added (`tests/test_speaker_assigner.py`).
- `SrtFormatter` support and CLI `--format srt` (subtitle generation).
- New CLI flags: `--diarize`, `--gap-threshold`, `--max-speakers`.
- `StubDiarizationProvider` (demo provider) in
  `src/infrastructure/diarization_provider.py`.

### Changed

- `TranscribeVideo` refactored to delegate speaker assignment to
  `SpeakerAssigner` and to accept an optional `speaker_assigner`.
- Documentation updated (`README.md`, `docs/CLI_OPTIONS.md`,
  `docs/USAGE.md`) to reflect the new component and testing instructions.

### Fixed

- Small test and compatibility fixes related to refactor (all tests
  passing locally).

## [0.1.0] - YYYY-MM-DD

Initial baseline release (project scaffolding, formatters, CLI, tests).

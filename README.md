# JARVIS

Local-first Windows 11 desktop assistant built with Python, PySide6, SQLite and Ollama. Work in progress; this is not the complete autonomous assistant yet.

## Resume development
Read AGENTS.md, PROGRESS.md and TASKS.md. The original requirements are in docs/request.md. Latest tested state and unfinished packaging are recorded in PROGRESS.md. Preserve local data and uncommitted work.

## Development
- Python 3.12; install requirements-lock.txt into a virtual environment.
- Launch: `python main.py`
- Tests: `python -m pytest -q`
- Browser integration tests: set `JARVIS_RUN_BROWSER_TEST=1`; a separate Edge context is used if Edge is installed, otherwise Playwright Chromium.
- Guide: `python verify_desktop.py`, then `python make_guide.py`.
- Windows package: `build.ps1` uses the sibling venv and per-user Inno Setup 6. Supply the Apache-2.0 Vosk small English model in speech-model. Models/binaries/runtime profiles are excluded from Git.

## Current scope
Safe explicit file/system commands, local streaming chat, persistent memory/history, declarative CSV/XLSX skills, reminders, optional Vosk/SAPI speech and restricted public-page browser observation. No arbitrary shell execution or unattended global desktop input.

General natural-language tool planning, advanced teaching, authenticated browser workflows, scheduled skills/folder monitoring and the reference-driven UI redesign are pending. The guide generator documents the actual release rather than promising unimplemented features.

## Checkpoints
Private personal repository. Commit/push tested milestones and verify remote SHA. Never upload user databases, credentials, recordings, browser profiles or company-authored local history. Design references supplied by the user are in docs/design; they are targets, not screenshots of the delivered UI.

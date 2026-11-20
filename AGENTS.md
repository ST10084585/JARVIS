# JARVIS development

**CODE STYLE: Prefer the smallest correct, secure, readable implementation. Follow KISS, DRY, and YAGNI. Reuse existing code and libraries. Avoid unnecessary abstractions, files, dependencies, comments, and refactoring. Make focused changes, test them, and move on.**

Local-first Windows 11 personal assistant. Original requirements: docs/request.md. Python 3.12 + Qt Widgets, SQLite profiles, shared localhost Ollama, declarative CSV/XLSX skills, Playwright and Vosk/SAPI loaded on demand.

- Resume by reading PROGRESS.md and TASKS.md, then git status/log. Preserve all existing changes. Inspect only relevant modules/contracts. Do not repeat capability discovery or install existing dependencies.
- Python: `..\venv\Scripts\python.exe`. Tests: `..\venv\Scripts\python.exe -m pytest tests/test_<area>.py -q`; full `-m pytest -q` before packaging. UI tests use offscreen Qt. Live model/browser/audio evidence is separate.
- Run: `..\venv\Scripts\python.exe main.py`. Build: `./build.ps1` (tests, notices, PyInstaller, Inno Setup). Build PATH must exclude unrelated Poppler ICU DLLs.
- Never execute model-generated scripts or shell strings. Tools enforce local authorized roots, deny reparse escapes, preserve originals, require explicit foreground/network permissions. Workflows validate declarative JSON only.
- No unattended global input, focus changes, clipboard writes or hidden recording. Microphone and separate visible observation browser require explicit action. No private-account access without authorization.
- Eco default: one workflow worker, lazy imports, model keep_alive=0, no idle inference or continuous screen/audio capture. Responsiveness takes priority over speed.
- Never commit profiles, credentials, recordings, models or generated binaries. Deliverables go in ../../outputs. Source repo remains here under work/jarvis.
- Use focused tests per edit; update PROGRESS/TASKS and checkpoint verified work. Clearly label limitations. Do not claim the entire master specification is complete based on unit tests.
- Avoid delegation unless it materially reduces work; no duplicate review or retesting on unchanged code.
- GitHub: personal account only. Verify username with GitHub API and obtain explicit user confirmation before repository creation/upload. Never use the work account. Existing work-authored history must remain local; upload a clean personal branch without company author metadata. Preserve original local branches; never force-push or silently rewrite history.
- Once connected, commit/push each meaningful tested milestone and safe WIP checkpoints about every 15–20 minutes. Verify remote SHA after each push. If sync fails, diagnose and record it before accumulating extensive new work.
- Development order: complete interrupted installer validation after GitHub checkpoint, then natural-language tool execution, advanced skills, Watch & Learn, scheduled skills/folder monitoring, voice/bubble, remaining integrations. Mandatory Qt UI redesign follows stable core work; primary target docs/design/jarvis-ui-reference.png, with workflow/orb references alongside. No redesign before higher priorities are pushed.

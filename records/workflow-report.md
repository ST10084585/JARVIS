# Workflow/jobs verification — 19 November 2026

Implemented `jarvis/workflows.py` and `jarvis/jobs.py`; API in `docs/workflow-contract.md`.

Verification on the actual Windows environment, Python 3.12 shared virtual environment:

- `..\venv\Scripts\python.exe -m pytest tests/test_workflows.py -q`: **18 passed in 0.66 s**.
- Full `pytest -q`: collection blocked in `tests/test_ui.py`: `ModuleNotFoundError: No module named 'PySide6'`. Desktop dependencies are installing independently; no full-suite success claimed.
- Initial feature assertion failed because workflow module did not exist. Pytest was initially unavailable and installed. Regression tests subsequently exposed import enablement timing and inference that ignored safe-export formula escaping; both reproduced failures and passed after fixes.

Verified: restricted schema rejects arbitrary operations/unknown fields/bool schema versions; path parent traversal rejected; deterministic CSV select/rename/strip/upper/deduplicate/sort; unchanged original; real concurrent output collision has exactly one winner and no temporary remnants; Excel numeric preservation/text type enforcement; CSV and Excel formula-prefix escaping; reject policy; pre-start and running cooperative cancellation; imported skill atomic disabled insertion; persistent skill history/rollback/review; job result persistence; crash-interrupted jobs not replayed; missed repeating reminder coalescing and no second notification after restart; unattended skills rejected.

Boundaries and limits:

- UI/service must authorize exact input and output files before calling execute. Workflow definitions contain no file paths or code. Import review and enablement do not themselves authorize files.
- Single worker, bounded resource-pressure deferral (up to 5 seconds for low available RAM/high CPU), pause gates queued tasks. Running callbacks must cooperate with cancellation; shutdown waits at most 5 seconds. Progress values use percent 0–100.
- Scheduler supports durable reminders only; recurring file skills and folder monitors are not implemented. At-most-once durable claim precedes UI notification: a crash in that small interval can suppress display, rather than duplicate an execution. Claims remain in schedule.sqlite3; ordinary successful notifications also become completed jobs. Notifications are delivered only while application runs, and missed occurrences coalesce on next tick.
- CSV UTF-8 or UTF-8 BOM; XLSX first worksheet only. No macros, legacy XLS, formulas evaluated, document formatting, arbitrary Python, scripts, or business-specific Sesolos rules. Output rebuilds a data-only table.
- Maximum input 25 MiB / 100,000 rows; XLSX expanded archive maximum 100 MiB. Data is held in memory for sorting/deduplication; these are bounded small-table workflows, not a streaming big-data engine.
- Example inference supports unique per-column identity/strip/case conversions, selection, and renaming with unchanged row counts. It validates exact table values and column order, not byte-for-byte CSV newline/quoting style; formula-like expected strings are rejected because safe export would alter them.
- Paths reject UNC/network paths, traversal, NTFS alternate streams, reserved Windows devices, symlink/junction ancestors. Atomic exclusive hard-link publication requires a filesystem supporting hard links (verified on local NTFS). This is protection against accidental overwrites and imported-workflow escapes, not a sandbox against another malicious process changing directories concurrently.
- No new agents or commits; only assigned files changed.

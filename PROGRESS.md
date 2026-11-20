# LATEST SESSION CHECKPOINT

- Milestone: corrected installer installed, launched, uninstalled and reinstalled successfully.
- Account: confirmed personal ST10084585 (ID 129373209). Private https://github.com/ST10084585/JARVIS created. Separate GitHub CLI configuration; work authentication preserved.
- Last successful GitHub push: c8db2c334e4ff295f031dc60bfd334d9dc350a29, verified via API owner/privacy/tree and git ls-remote on 2026-11-20. Personal main has one clean root; old local history was not uploaded.
- History: original local build-jarvis branch retained. User requires company commit metadata excluded from upload; personal main branch starts from a clean root containing current source, tests and documentation.
- Last verified work: standalone app launched and returned actual time after isolating an incorrect bundled ICU DLL; real source browser read, local model generation/unload and prerecorded speech round trip passed.
- Current changes: packaging/setup/guide sources, browser Edge reuse, model-selection validation and no-tray shutdown fixes, design references, upload exclusions.
- Latest evidence: full suite with actual isolated browser enabled: 54 passed, 5 subtests passed. Real microphone still untested.
- Exact next action: checkpoint installer evidence, then implement natural-language tool control.
- Known packaging state: corrected outputs installer verified on this host; clean second-PC bootstrap remains unverified. build.ps1 isolates PATH.

## Verified / implemented state
- Core: SQLite chats/settings/explicit memory, tool policy, bounded document readers, local inference client. Cancellation repair verified, including stalled stream interruption.
- Workflows: 18 tests passed for CSV/XLSX transformations, example inference, versioning/import disabled, atomic non-overwrite output, job cancellation, persisted reminders and coalescing.
- Integrations: 13 policy/render tests passed using isolated Edge; real public example.com read passed. Vosk transcribed a SAPI-generated WAV correctly in 1.79 seconds. Live microphone and audible playback unverified.
- UI: seven tabs, chat worker, skill editor, memory/settings/help, tray/bubble, explicit observation controls. Actual packaged welcome and time chat verified. Offscreen screenshots corrected and sampled guide pages visually reviewed.
- Models: existing Ollama reused; qwen3:0.6b (~523 MB) installed. Real inference took 77.05 seconds under memory pressure; unloaded model list empty afterward.
- Tools: isolated venv dependencies installed; Inno Setup 6.7.3 verified SHA256 and valid signature, installed per user. No new cloud plugins added.

## Remaining and limits
- Packaging: corrected installer exit 0, actual installed time chat passed, uninstall exit 0 removed executable and preserved test profile; reinstall exit 0. Evidence: records/installer-validation.json.
- Documentation: 20-page illustrated PDF, offline HTML and quick start generated from make_guide.py. Guide accurately identifies release limits; update browser documentation for Edge reuse.
- Performance: packaged app 20-second sample peaked at 94.42 MB RSS, 0.083% whole-machine CPU (1.327% of one core). Disposable 10,000-row transform took 0.025s with foreground handle and clipboard sequence unchanged. Sustained/minimized/typing tests remain.
- Current scheduler handles reminders only; scheduled file skills and folder triggers not implemented.
- Browser observation restricted to public pages; no authenticated forms, uploads, arbitrary application screen learning or global event recording.
- No wake word, runtime MCP/plugins, optional cloud/calendar/email integration, full backup/restore or updater.
- Chat actions use deterministic commands, not general autonomous model tool planning. Small model reasoning has practical limits.
- Shared databases are local plaintext and parser code runs in-process; do not claim encrypted storage or OS sandboxing.

## Decisions
Retain Python/Qt/SQLite architecture. Low-memory model chosen because only ~1.7 GB RAM was free (16 GB total, RTX3050 4GB). No arbitrary generated scripts. Exact run approval for file transformations. Finish current feature and test before expanding scope.

UI redesign is mandatory after pushed core milestones. Primary reference docs/design/jarvis-ui-reference.png; retain three columns, restrained dark cyan/blue identity, central chat/visualization, collapsible navigation/system panels. Other supplied workflow/orb images retained. Do not represent these as implemented UI.

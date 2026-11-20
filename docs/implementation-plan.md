# JARVIS implementation plan

Goal: deliver a local Windows desktop assistant, installer and honest verification records against request.md.
Architecture: Python 3.12, Qt Widgets, SQLite, shared Ollama over localhost. Eco default, no global input hooks or unrestricted shell. Runtime permissions enforced in code. Profiles under LOCALAPPDATA/JARVIS/profiles. Single instance per profile.
Alternatives considered: Electron rejected for idle overhead; Tauri adds compiler and frontend complexity; Qt selected for native widgets and offline HTML help.
User explicitly delegated implementation choices and opted out of routine questions.

## Independent implementation boundaries
1. Core: store.py, tools.py, inference.py and core tests. SQLite persistence, path authorization, deterministic safe tools, Ollama streaming. Interface documented in core-contract.md.
2. Workflows: workflows.py, jobs.py and workflow tests. Restricted declarative CSV transforms, versioned skills, example inference, persistent scheduler and cancellable queue. Interface documented in workflow-contract.md.
3. Integrations: browser.py, voice.py and integration tests. Isolated Playwright structured observation/replay and on-demand Vosk/SAPI. Interface documented in integration-contract.md.
4. Desktop integration: app.py, ui.py, service.py, UI tests. Chat, tools, memory, library, teaching, scheduler, settings, tray, bubble, approvals, profiles, help.
5. Packaging and verification: standalone PyInstaller, per-user installer, real model smoke test, idle measurement, screenshots, PDF/HTML guide, clean temporary profile install/uninstall.

## Constraints and review focus
- No paid services, no personal account access, no credentials in artifacts.
- No silent screen/microphone capture; observation only after explicit UI action.
- No unattended foreground input, clipboard mutation or arbitrary script execution.
- Validate imports, paths, symlinks/reparse points, output collisions and cancellation.
- Model output is untrusted; all tool executions pass policy, never eval/exec.
- Durable history and schedules, missed runs handled conservatively.
- Tests first for security boundaries and deterministic processing; live integration evidence separate from unit tests.
- Unimplemented or unverified requirements must be listed, never represented by inert UI controls.

## Progress
- Capability audit: terminal/PowerShell, filesystem, browser/computer-use, GitHub connector, document tools, workflow skills available. Plugin marketplace checked; no extra cloud connector needed.
- Hardware: Windows 11 Pro 26100 x64; i7-11800H 8C/16T; 16 GB RAM with ~1.7 GB free; RTX3050 4GB; C: ~15GB free. Existing Ollama has no models.
- Environment installation in progress; qwen3:0.6b selected for pressure-aware default, ~523MB Q4_K_M Apache-2.0, larger models remain optional.

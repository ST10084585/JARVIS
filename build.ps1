$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& ..\venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
& ..\venv\Scripts\python.exe collect_licenses.py
# Exclude unrelated tool runtimes (notably Poppler ICU) from DLL discovery.
$savedBuildPath = $env:PATH
$env:PATH = "$PSScriptRoot\..\venv\Scripts;$env:WINDIR\System32;$env:WINDIR"
try {
    & ..\venv\Scripts\python.exe -m PyInstaller --clean --noconfirm --windowed --name JARVIS --onedir --collect-all vosk --collect-all playwright --collect-all sounddevice --hidden-import win32timezone --add-data 'speech-model;speech-model' --add-data 'docs;docs' --add-data 'licenses;licenses' main.py
} finally { $env:PATH = $savedBuildPath }
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Installer build failed' }

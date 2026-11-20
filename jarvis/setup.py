"""Explicit user-invoked setup using fixed official package identifiers."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def ollama_executable():
    found=shutil.which('ollama')
    candidate=Path(os.environ.get('LOCALAPPDATA',''))/'Programs'/'Ollama'/'ollama.exe'
    return found or (str(candidate) if candidate.is_file() else None)

def install_browser_command():
    if getattr(sys,'frozen',False):return [sys.executable,'--browser-setup','install','chromium']
    return [sys.executable,'-m','playwright','install','chromium']

def install_browser():
    result=subprocess.run(install_browser_command(),capture_output=True,text=True,timeout=1800,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:raise RuntimeError('Browser setup failed: '+(result.stderr or result.stdout)[-1500:])
    return 'Chromium installed for this Windows user.'

def configure_ollama():
    from .inference import OllamaClient
    client=OllamaClient()
    executable=ollama_executable()
    if not executable:
        winget=shutil.which('winget')
        if not winget:raise RuntimeError('Windows App Installer (winget) is unavailable. Install it from Microsoft Store to enable automatic Ollama setup.')
        result=subprocess.run([winget,'install','--id','Ollama.Ollama','-e','--source','winget','--silent','--accept-package-agreements','--accept-source-agreements'],capture_output=True,text=True,timeout=1800,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:raise RuntimeError('Ollama installer failed: '+(result.stdout+result.stderr)[-1500:])
        executable=ollama_executable()
        if not executable:raise RuntimeError('Ollama was not found after installation.')
    try:client.models()
    except Exception:
        env=os.environ.copy();env['OLLAMA_HOST']='127.0.0.1:11434';env['OLLAMA_NUM_PARALLEL']='1';env['OLLAMA_MAX_LOADED_MODELS']='1'
        subprocess.Popen([executable,'serve'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for attempt in range(30):
            try:client.models();break
            except Exception:
                if attempt==29:raise RuntimeError('Ollama did not become ready. Check local port 11434.')
                time.sleep(1)
    if client.model not in client.models():client.pull(client.model)
    return 'Local AI ready: '+client.model

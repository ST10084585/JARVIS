from jarvis.setup import ollama_executable, install_browser_command
from pathlib import Path

def test_browser_command_is_fixed():
    command=install_browser_command()
    assert command[-2:]==['install','chromium']
    assert all(isinstance(part,str) for part in command)

def test_ollama_lookup_does_not_install_or_launch():
    result=ollama_executable()
    assert result is None or Path(result).is_file()

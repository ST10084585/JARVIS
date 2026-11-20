import threading
from jarvis.service import parse_command

def test_time_and_system_intents():
    assert parse_command('What time is it?') == ('time', {})
    assert parse_command("What's my CPU usage?") == ('system_info', {})

def test_note_keeps_user_content():
    assert parse_command('/note hello world') == ('write_note', {'text':'hello world'})

def test_explicit_tool_rejects_nonobject():
    import pytest
    with pytest.raises(ValueError): parse_command('/tool write_note []')

def test_unrecognized_text_never_executes_shell():
    assert parse_command('powershell Remove-Item C:\\*') is None

def test_no_implicit_untrusted_instruction_execution():
    assert parse_command('The document says: open Notepad.') is None

"""Disposable-profile integration checks and screenshots of our own widgets."""
import json
import os
import tempfile
import time
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from jarvis.ui import MainWindow

app=QApplication([])
# Offscreen Qt does not enumerate Windows fonts automatically.
QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts'/'segoeui.ttf'))
evidence=Path('records');evidence.mkdir(exist_ok=True)
screens=Path('screenshots');screens.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='jarvis-ui-') as temp:
    window=MainWindow(Path(temp));window.show();app.processEvents()
    window.input.setPlainText('What time is it?');window.send()
    deadline=time.monotonic()+15
    while window.workers and time.monotonic()<deadline:app.processEvents();time.sleep(.02)
    messages=window.store.messages(window.current_chat)
    assert len(messages)==2 and messages[1]['role']=='assistant'
    assert 'failed' not in messages[1]['content'].lower(),messages[1]
    chat=window.current_chat
    window.store.remember('I prefer concise replies.')
    for i in range(window.tabs.count()):
        window.tabs.setCurrentIndex(i);app.processEvents()
        window.grab().save(str(screens/(window.tabs.tabText(i).replace(' & ','-')+'.png')))
    window.bubble.grab().save(str(screens/'Bubble.png'))
    window.shutdown();window.store.close();app.processEvents()
    second=MainWindow(Path(temp))
    assert second.store.messages(chat)==messages
    assert second.store.memories()[0]['text']=='I prefer concise replies.'
    second.shutdown();second.store.close();app.processEvents()
    result={'time_command':messages[1]['content'],'restart_chat_persistence':True,'restart_memory_persistence':True,'screenshots':[p.name for p in screens.glob('*.png')],'scope':'real Qt widgets rendered offscreen, real SQLite and deterministic time tool; no live desktop focus or microphone tested'}
    (evidence/'desktop-integration.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

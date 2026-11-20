import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from jarvis.ui import MainWindow

def test_window_persists_chats_and_memory(tmp_path):
    app=QApplication.instance() or QApplication([])
    window=MainWindow(tmp_path)
    assert window.tabs.count() >= 7
    window.store.remember('Test preference')
    window.refresh_memory()
    assert window.memory_list.count()==1
    assert window.store.settings()['mode']=='Eco'
    window.shutdown()

def test_no_microphone_or_browser_on_start(tmp_path):
    app=QApplication.instance() or QApplication([])
    window=MainWindow(tmp_path)
    assert not window.watch.running
    assert not window.workers
    window.shutdown()

def test_invalid_saved_model_recovers_and_invalid_selection_is_not_saved(tmp_path,monkeypatch):
    from jarvis.store import Store
    store=Store(tmp_path);store.set_setting('model','');store.close()
    app=QApplication.instance() or QApplication([])
    window=MainWindow(tmp_path)
    assert window.model.model=='qwen3:0.6b'
    errors=[];monkeypatch.setattr(window,'error',errors.append)
    window.models.setCurrentText('https://invalid')
    window.select_model()
    assert errors and window.store.settings()['model']=='qwen3:0.6b'
    window.shutdown()

def test_close_without_tray_requests_quit(tmp_path,monkeypatch):
    from PySide6.QtGui import QCloseEvent
    app=QApplication.instance() or QApplication([])
    window=MainWindow(tmp_path);window.tray.hide()
    called=[];monkeypatch.setattr(window,'quit',lambda:called.append(True))
    window.closeEvent(QCloseEvent())
    assert called
    window.shutdown()

"""JARVIS desktop entry point; one process owns each profile."""
import argparse
import os
import re
import sys
from pathlib import Path

def main():
    if '--browser-setup' in sys.argv:
        sys.argv=[sys.argv[0]]+sys.argv[sys.argv.index('--browser-setup')+1:]
        from playwright.__main__ import main as browser_main
        browser_main();return 0
    parser=argparse.ArgumentParser(description='JARVIS local desktop assistant')
    parser.add_argument('--profile',default='Personal')
    parser.add_argument('--data-dir',type=Path)
    parser.add_argument('--minimized',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',args.profile):parser.error('Invalid profile name')
    profile=args.data_dir or Path(os.environ['LOCALAPPDATA'])/'JARVIS'/'profiles'/args.profile
    profile.mkdir(parents=True,exist_ok=True)
    from PySide6.QtCore import QLockFile,QTimer
    from PySide6.QtWidgets import QApplication,QMessageBox
    app=QApplication(sys.argv);app.setApplicationName('JARVIS');app.setQuitOnLastWindowClosed(False)
    lock=QLockFile(str(profile/'instance.lock'));lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        QMessageBox.information(None,'JARVIS','This profile is already running. Open JARVIS from the system tray.');return 0
    from jarvis.ui import MainWindow
    window=MainWindow(profile)
    if not args.minimized:window.show()
    if not window.store.settings().get('onboarded') and not args.minimized:QTimer.singleShot(300,window.tutorial)
    app.aboutToQuit.connect(window.shutdown)
    try:return app.exec()
    finally:lock.unlock()

if __name__=='__main__':
    raise SystemExit(main())

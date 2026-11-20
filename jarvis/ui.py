"""Native Qt interface. Worker threads never manipulate widgets directly."""
import html
import json
import os
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPoint, QUrl
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QDesktopServices, QTextCursor
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,
    QPushButton,QLineEdit,QPlainTextEdit,QTextBrowser,QListWidget,QListWidgetItem,QTabWidget,
    QSplitter,QComboBox,QFileDialog,QMessageBox,QInputDialog,QCheckBox,QFormLayout,QSpinBox,
    QSystemTrayIcon,QMenu,QDialog,QDialogButtonBox,QDateTimeEdit,QScrollArea,QSlider)
from .store import Store
from .tools import ToolRegistry
from .inference import OllamaClient
from .workflows import SkillLibrary,execute,infer_csv
from .jobs import JobManager,Scheduler
from .browser import WatchLearn,BrowserSession
from .voice import SpeechService
from .service import Assistant,HELP

def resources():
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))

def icon():
    p=QPixmap(64,64); p.fill(Qt.GlobalColor.transparent)
    q=QPainter(p); q.setRenderHint(QPainter.RenderHint.Antialiasing)
    q.setBrush(QColor('#133746')); q.setPen(QColor('#63e6cf')); q.drawEllipse(2,2,60,60)
    q.setFont(QFont('Segoe UI',27,QFont.Weight.Bold)); q.drawText(p.rect(),Qt.AlignmentFlag.AlignCenter,'J'); q.end()
    return QIcon(p)

class Worker(QThread):
    chunk=Signal(str)
    result=Signal(object)
    failed=Signal(str)
    ask=Signal(str,object)
    navigate=Signal(str)
    def __init__(self,fn,parent=None):
        super().__init__(parent); self.fn=fn; self.cancel=threading.Event()
    def approval(self,description):
        answer={'event':threading.Event(),'approved':False}
        self.ask.emit(description,answer)
        while not answer['event'].wait(.1):
            if self.cancel.is_set(): return False
        return answer['approved'] and not self.cancel.is_set()
    def run(self):
        try: self.result.emit(self.fn(self))
        except Exception as e: self.failed.emit(f'{type(e).__name__}: {e}')

class Bubble(QWidget):
    def __init__(self,owner):
        super().__init__(None,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint)
        self.owner=owner; self.drag=None
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle('JARVIS quick access'); self.resize(66,66)
        layout=QVBoxLayout(self); layout.setContentsMargins(4,4,4,4)
        self.button=QPushButton('J'); self.button.setObjectName('bubble'); layout.addWidget(self.button)
        self.button.clicked.connect(self.menu)
        self.button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.button.customContextMenuRequested.connect(self.menu)
        settings=owner.store.settings()
        pos=settings.get('bubble_position',[80,80]); self.move(*pos)
        self.setWindowOpacity(float(settings.get('bubble_opacity',.9)))
    def menu(self,*args):
        menu=QMenu(self)
        menu.addAction('Open JARVIS',self.owner.reveal)
        menu.addAction('Quick message',self.quick)
        menu.addAction('Push to talk',self.owner.listen)
        menu.addAction('Skills',lambda:self.owner.go('Skills'))
        menu.addAction('Watch & Learn',lambda:self.owner.go('Watch & Learn'))
        menu.addAction('Pause queue',self.owner.jobs.pause)
        menu.addAction('Resume queue',self.owner.jobs.resume)
        menu.addAction('Emergency stop',self.owner.stop_all)
        menu.addAction('Hide bubble',self.hide)
        menu.exec(self.mapToGlobal(QPoint(0,self.height())))
    def quick(self):
        text,ok=QInputDialog.getText(self,'JARVIS','Message')
        if ok and text: self.owner.input.setPlainText(text); self.owner.send(); self.owner.reveal()
    def mousePressEvent(self,event): self.drag=event.globalPosition().toPoint()-self.pos()
    def mouseMoveEvent(self,event):
        if self.drag is not None: self.move(event.globalPosition().toPoint()-self.drag)
    def mouseReleaseEvent(self,event):
        self.drag=None
        area=self.screen().availableGeometry()
        if abs(self.x()-area.left())<50: self.move(area.left(),self.y())
        elif abs(self.x()+self.width()-area.right())<50: self.move(area.right()-self.width(),self.y())
        self.owner.store.set_setting('bubble_position',[self.x(),self.y()])

class MainWindow(QMainWindow):
    def __init__(self,profile_dir):
        super().__init__(); self.profile_dir=Path(profile_dir)
        self.store=Store(self.profile_dir); self.tools=ToolRegistry(self.store)
        settings=self.store.settings()
        try:self.model=OllamaClient(settings.get('model','qwen3:0.6b'),settings.get('mode','Eco'))
        except ValueError:
            self.model=OllamaClient();self.store.set_setting('model',self.model.model);self.store.set_setting('mode',self.model.mode)
        self.library=SkillLibrary(self.profile_dir); self.jobs=JobManager(self.profile_dir)
        self.scheduler=Scheduler(self.profile_dir,self.jobs)
        self.watch=WatchLearn(self.profile_dir)
        model_path=Path(os.environ.get('JARVIS_SPEECH_MODEL',str(resources()/'speech-model')))
        self.speech=SpeechService(model_path)
        self.workers=[]; self.chat_workers={}; self.closed=False; self.current_chat=None
        self.setWindowTitle('JARVIS • '+self.profile_dir.name); self.setWindowIcon(icon()); self.resize(1140,780)
        self.setAcceptDrops(True)
        base=QWidget(); self.setCentralWidget(base); outer=QVBoxLayout(base); outer.setContentsMargins(22,18,22,16)
        top=QHBoxLayout(); title=QLabel('J A R V I S'); title.setObjectName('brand'); top.addWidget(title)
        top.addWidget(QLabel('LOCAL ASSISTANT'),1)
        self.mode=QComboBox(); self.mode.addItems(['Eco','Balanced','Performance']); self.mode.setCurrentText(self.model.mode)
        self.mode.currentTextChanged.connect(self.change_mode); top.addWidget(self.mode)
        top.addWidget(self.button('Stop all',self.stop_all)); outer.addLayout(top)
        self.tabs=QTabWidget(); outer.addWidget(self.tabs,1)
        self.build_chat(); self.build_skills(); self.build_watch(); self.build_jobs(); self.build_memory(); self.build_settings(); self.build_help()
        self.status=QLabel('Local data • Eco mode • Ready'); outer.addWidget(self.status)
        self.bubble=Bubble(self)
        self.tray=QSystemTrayIcon(icon(),self); self.tray.setToolTip('JARVIS — local assistant')
        menu=QMenu(); menu.addAction('Open JARVIS',self.reveal); menu.addAction('Show bubble',self.bubble.show)
        menu.addAction('Emergency stop',self.stop_all); menu.addSeparator(); menu.addAction('Quit',self.quit)
        self.tray.setContextMenu(menu); self.tray.activated.connect(lambda reason:self.reveal() if reason==QSystemTrayIcon.ActivationReason.DoubleClick else None)
        if QSystemTrayIcon.isSystemTrayAvailable(): self.tray.show()
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(10000)
        self.refresh_chats(); self.refresh_skills(); self.refresh_memory(); self.refresh_jobs()
        if not self.current_chat: self.new_chat()
        self.setStyleSheet(STYLE)

    def button(self,text,fn):
        b=QPushButton(text); b.clicked.connect(fn); return b
    def page(self,name):
        page=QWidget(); layout=QVBoxLayout(page); layout.setContentsMargins(16,18,16,16); self.tabs.addTab(page,name); return layout
    def heading(self,layout,title,subtitle=''):
        label=QLabel(title); label.setObjectName('heading'); layout.addWidget(label)
        if subtitle: l=QLabel(subtitle); l.setWordWrap(True); layout.addWidget(l)
    def go(self,name):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i)==name:self.tabs.setCurrentIndex(i)
        self.reveal()
    def reveal(self): self.showNormal(); self.raise_(); self.activateWindow()
    def notify(self,text): self.status.setText(text)
    def error(self,text): self.notify(text); QMessageBox.warning(self,'JARVIS',text)
    def safe(self,fn):
        try:return fn()
        except Exception as e:self.error(f'{type(e).__name__}: {e}')
    def ask(self,text,answer):
        answer['approved']=QMessageBox.question(self,'Review permission',text,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes
        answer['event'].set()
    def start_worker(self,fn,done=None,fail=None):
        worker=Worker(fn,self); self.workers.append(worker)
        worker.ask.connect(self.ask); worker.navigate.connect(self.go)
        if done:worker.result.connect(done)
        worker.failed.connect(fail or self.error)
        worker.finished.connect(lambda:self.worker_finished(worker)); worker.start(); return worker
    def worker_finished(self,worker):
        if worker in self.workers:self.workers.remove(worker)
        worker.deleteLater()

    def build_chat(self):
        layout=self.page('Chat'); split=QSplitter(); layout.addWidget(split)
        left=QWidget(); side=QVBoxLayout(left); side.setContentsMargins(0,0,12,0)
        side.addWidget(self.button('+ New conversation',self.new_chat))
        self.chat_search=QLineEdit(); self.chat_search.setPlaceholderText('Search conversations'); self.chat_search.textChanged.connect(self.refresh_chats); side.addWidget(self.chat_search)
        self.chat_list=QListWidget(); self.chat_list.currentItemChanged.connect(self.select_chat); side.addWidget(self.chat_list,1)
        row=QHBoxLayout(); row.addWidget(self.button('Rename',self.rename_chat)); row.addWidget(self.button('Archive',self.archive_chat)); side.addLayout(row)
        side.addWidget(self.button('Delete conversation',self.delete_chat)); split.addWidget(left)
        right=QWidget(); box=QVBoxLayout(right); box.setContentsMargins(8,0,0,0)
        self.heading(box,'Your local workspace','Ask a question, use /help for actions, or attach a file for local reading.')
        self.transcript=QTextBrowser(); self.transcript.setOpenExternalLinks(False); self.transcript.anchorClicked.connect(lambda url:self.safe(lambda:QDesktopServices.openUrl(url)) if url.scheme() in ('https','http') and QMessageBox.question(self,'Open link','Open this link in your browser?\n'+url.toString())==QMessageBox.StandardButton.Yes else None)
        box.addWidget(self.transcript,1)
        self.input=QPlainTextEdit(); self.input.setPlaceholderText('Message JARVIS…  (Ctrl+Enter to send)'); self.input.setMaximumHeight(100); box.addWidget(self.input)
        from PySide6.QtGui import QShortcut,QKeySequence
        QShortcut(QKeySequence('Ctrl+Return'),self.input,activated=self.send)
        row=QHBoxLayout(); row.addWidget(self.button('Attach file',self.attach)); row.addWidget(self.button('Push to talk',self.listen))
        row.addWidget(self.button('Speak last reply',self.speak_last)); row.addStretch(); row.addWidget(self.button('Stop reply',self.stop_reply)); row.addWidget(self.button('Send',self.send)); box.addLayout(row)
        split.addWidget(right); split.setSizes([240,820])
    def refresh_chats(self,*args):
        if not hasattr(self,'chat_list'):return
        self.chat_list.blockSignals(True); self.chat_list.clear()
        for chat in self.store.chats(self.chat_search.text()):
            if chat.get('archived'):continue
            item=QListWidgetItem(chat['title']); item.setData(Qt.ItemDataRole.UserRole,chat['id']); self.chat_list.addItem(item)
            if chat['id']==self.current_chat:self.chat_list.setCurrentItem(item)
        self.chat_list.blockSignals(False)
    def new_chat(self):
        self.current_chat=self.store.new_chat(); self.refresh_chats(); self.render_chat()
    def select_chat(self,item,previous=None):
        if item:self.current_chat=item.data(Qt.ItemDataRole.UserRole); self.render_chat()
    def render_chat(self,pending=''):
        if not self.current_chat:return
        content=[]
        for message in self.store.messages(self.current_chat):
            content.append(f"<p style='color:#63e6cf'><b>{'YOU' if message['role']=='user' else 'JARVIS'}</b></p><pre style='white-space:pre-wrap;font-family:Segoe UI'>{html.escape(message['content'])}</pre>")
        if pending:content.append('<p style="color:#63e6cf"><b>JARVIS</b></p><pre style="white-space:pre-wrap">'+html.escape(pending)+'</pre>')
        self.transcript.setHtml(''.join(content) or '<h2>Ready when you are.</h2><p>Local conversation. Safe tools. Reusable workflows.</p><p>Try “What time is it?” or /help.</p>')
        self.transcript.moveCursor(QTextCursor.MoveOperation.End)
    def rename_chat(self):
        title,ok=QInputDialog.getText(self,'Rename conversation','Title')
        if ok and title:self.store.rename_chat(self.current_chat,title);self.refresh_chats()
    def archive_chat(self):
        if self.current_chat:self.store.archive_chat(self.current_chat);self.new_chat()
    def delete_chat(self):
        if QMessageBox.question(self,'Delete conversation','Permanently delete this conversation?')==QMessageBox.StandardButton.Yes:
            self.store.delete_chat(self.current_chat);self.new_chat()
    def send(self):
        text=self.input.toPlainText().strip()
        if not text:return
        chat=self.current_chat
        if chat in self.chat_workers:self.notify('This conversation already has a reply running.');return
        self.input.clear(); self.store.add_message(chat,'user',text)
        if len(self.store.messages(chat))==1:self.store.rename_chat(chat,text[:40]);self.refresh_chats()
        self.render_chat(); parts=[]
        def task(worker):
            assistant=Assistant(self.store,self.tools,self.model,self.library,self.jobs,self.scheduler,worker.approval,worker.navigate.emit)
            for chunk in assistant.reply(text,chat,worker.cancel):
                if worker.cancel.is_set():break
                parts.append(chunk);worker.chunk.emit(''.join(parts))
            return ''.join(parts)+ ('\n[Stopped]' if worker.cancel.is_set() else '')
        def finish(reply):
            self.chat_workers.pop(chat,None);self.store.add_message(chat,'assistant',reply or '[No response]')
            if self.current_chat==chat:self.render_chat()
            self.refresh_memory();self.notify('Reply finished • '+self.model.mode)
        def fail(error):finish('Request failed: '+error)
        worker=Worker(task,self);self.workers.append(worker);self.chat_workers[chat]=worker
        worker.ask.connect(self.ask);worker.navigate.connect(self.go)
        worker.chunk.connect(lambda text:self.render_chat(text) if self.current_chat==chat else None)
        worker.result.connect(finish);worker.failed.connect(fail);worker.finished.connect(lambda:self.worker_finished(worker));worker.start()
        self.notify('Working locally…')
    def stop_reply(self):
        if self.current_chat in self.chat_workers:self.chat_workers[self.current_chat].cancel.set()
    def attach(self,path=None):
        if not isinstance(path,str):path=QFileDialog.getOpenFileName(self,'Select a document','','Documents (*.txt *.md *.csv *.xlsx *.pdf *.docx);;All files (*)')[0]
        if not path:return
        folder=str(Path(path).parent)
        if QMessageBox.question(self,'Document access','Authorize read access to this folder?\n'+folder)==QMessageBox.StandardButton.Yes:
            roots=self.store.settings().get('authorized_roots',[])
            if folder not in roots:roots.append(folder);self.store.set_setting('authorized_roots',roots);self.refresh_roots()
            self.input.setPlainText('/read '+path);self.send()
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():event.acceptProposedAction()
    def dropEvent(self,event):
        urls=event.mimeData().urls()
        if urls and urls[0].isLocalFile():self.attach(urls[0].toLocalFile())
    def listen(self):
        if any(getattr(w,'is_voice',False) for w in self.workers):self.notify('Voice capture is already running. Use Stop all to cancel.');return
        self.notify('MICROPHONE ACTIVE • listening for up to 12 seconds')
        device=self.store.settings().get('audio_device')
        worker=self.start_worker(lambda w:self.speech.listen(w.cancel,seconds=12,device=device),lambda text:(self.input.setPlainText(text),self.notify('Microphone released. Review the transcription and press Send.')))
        worker.is_voice=True
    def speak_last(self):
        texts=[m['content'] for m in self.store.messages(self.current_chat) if m['role']=='assistant']
        if texts:self.start_worker(lambda w:self.speech.speak(texts[-1],w.cancel),lambda _:self.notify('Speech finished.'))

    def build_skills(self):
        layout=self.page('Skills');self.heading(layout,'Teach once. Run locally.','Build deterministic CSV / Excel workflows. Test a new version before enabling it.')
        split=QSplitter();layout.addWidget(split,1);left=QWidget();side=QVBoxLayout(left)
        self.skill_list=QListWidget();self.skill_list.currentItemChanged.connect(self.select_skill);side.addWidget(self.skill_list)
        row=QHBoxLayout();row.addWidget(self.button('New',self.new_skill));row.addWidget(self.button('Import',self.import_skill));side.addLayout(row)
        row=QHBoxLayout();row.addWidget(self.button('Export',self.export_skill));row.addWidget(self.button('Delete',self.delete_skill));side.addLayout(row);split.addWidget(left)
        right=QWidget();box=QVBoxLayout(right)
        self.skill_name=QLineEdit();self.skill_name.setPlaceholderText('Workflow name');box.addWidget(self.skill_name)
        self.skill_description=QLineEdit();self.skill_description.setPlaceholderText('Description');box.addWidget(self.skill_description)
        box.addWidget(self.button('Learn from input + expected CSV',self.learn_examples))
        self.skill_editor=QPlainTextEdit();self.skill_editor.setPlaceholderText('Validated JSON transformation steps');box.addWidget(self.skill_editor,1)
        self.skill_status=QLabel('No skill selected');box.addWidget(self.skill_status)
        row=QHBoxLayout();row.addWidget(self.button('Save version',self.save_skill));row.addWidget(self.button('Review / enable',self.enable_skill));row.addWidget(self.button('Version history',self.skill_history));box.addLayout(row)
        row=QHBoxLayout();row.addWidget(self.button('Test draft on files',lambda:self.run_skill(draft=True)));row.addWidget(self.button('Run saved skill',lambda:self.run_skill(draft=False)));box.addLayout(row)
        split.addWidget(right);split.setSizes([260,700]);self.skill_id=None;self.new_skill()
    def new_skill(self):
        self.skill_id=None;self.skill_name.clear();self.skill_description.clear()
        self.skill_editor.setPlainText(json.dumps({'schema_version':1,'steps':[{'op':'strip','columns':['Name']}],'formula_policy':'escape'},indent=2))
        self.skill_status.setText('New draft • edit column names to match your files')
    def refresh_skills(self):
        self.skill_list.blockSignals(True);self.skill_list.clear()
        for skill in self.library.list():
            item=QListWidgetItem(f"{skill['name']}  ·  v{skill['version']} {'✓' if skill['enabled'] else '○'}");item.setData(Qt.ItemDataRole.UserRole,skill['id']);self.skill_list.addItem(item)
        self.skill_list.blockSignals(False)
    def select_skill(self,item,previous=None):
        if not item:return
        self.skill_id=item.data(Qt.ItemDataRole.UserRole);skill=self.library.get(self.skill_id)
        self.skill_name.setText(skill['name']);self.skill_description.setText(skill['description']);self.skill_editor.setPlainText(json.dumps(skill['definition'],indent=2))
        self.skill_status.setText(f"Version {skill['version']} • {'enabled' if skill['enabled'] else 'disabled — review required'}")
    def save_skill(self):
        def action():
            definition=json.loads(self.skill_editor.toPlainText())
            skill=self.library.save(self.skill_name.text(),self.skill_description.text(),definition,skill_id=self.skill_id)
            self.skill_id=skill['id'];self.library.set_enabled(self.skill_id,False);self.refresh_skills();self.skill_status.setText('Saved disabled. Test the draft, then review / enable.');self.notify('Workflow version saved.')
        self.safe(action)
    def enable_skill(self):
        if not self.skill_id:return
        skill=self.library.get(self.skill_id)
        if QMessageBox.question(self,'Review workflow','Enable this saved version?\n\n'+json.dumps(skill['definition'],indent=2)+'\n\nIt may read only the input file and create the chosen output. Every run requires exact file approval.')==QMessageBox.StandardButton.Yes:
            self.library.set_enabled(self.skill_id,True);self.refresh_skills();self.skill_status.setText('Enabled • file approval required at run time')
    def run_skill(self,draft=False):
        def action():
            if draft:definition=json.loads(self.skill_editor.toPlainText());name='Draft test'
            else:
                if not self.skill_id:raise ValueError('Select a saved skill first.')
                skill=self.library.get(self.skill_id)
                if not skill['enabled']:raise ValueError('Review and enable this skill first.')
                definition=skill['definition'];name=skill['name']
            source=QFileDialog.getOpenFileName(self,'Choose input','','Tables (*.csv *.xlsx)')[0]
            if not source:return
            destination=QFileDialog.getSaveFileName(self,'Create a new output',str(Path(source).with_stem(Path(source).stem+'-processed')),'Tables (*.csv *.xlsx)')[0]
            if not destination:return
            if QMessageBox.question(self,'Approve workflow run',f'{name}\nRead: {source}\nCreate: {destination}\n\nOriginals are preserved. Existing outputs are rejected.\n'+json.dumps(definition,indent=2))!=QMessageBox.StandardButton.Yes:return
            self.jobs.submit(name,lambda cancel,progress:execute(definition,source,destination,cancel=cancel));self.go('Automations');self.refresh_jobs()
        self.safe(action)
    def learn_examples(self):
        source=QFileDialog.getOpenFileName(self,'Original CSV','','CSV (*.csv)')[0]
        if not source:return
        expected=QFileDialog.getOpenFileName(self,'Correctly processed CSV','','CSV (*.csv)')[0]
        if not expected:return
        self.start_worker(lambda w:infer_csv(source,expected),lambda result:(self.skill_editor.setPlainText(json.dumps(result,indent=2)),self.skill_status.setText('Candidate matched these examples. Review and test unseen data before enabling.')))
    def import_skill(self):
        path=QFileDialog.getOpenFileName(self,'Import a workflow','','JSON (*.json)')[0]
        if path:self.safe(lambda:self.library.import_skill(path));self.refresh_skills()
    def export_skill(self):
        if not self.skill_id:return
        path=QFileDialog.getSaveFileName(self,'Export workflow','workflow.json','JSON (*.json)')[0]
        if path:self.safe(lambda:self.library.export_skill(self.skill_id,path))
    def delete_skill(self):
        if self.skill_id and QMessageBox.question(self,'Delete workflow','Delete this workflow and its version history?')==QMessageBox.StandardButton.Yes:
            self.library.delete(self.skill_id);self.new_skill();self.refresh_skills()
    def skill_history(self):
        if not self.skill_id:return
        versions=self.library.versions(self.skill_id)
        items=[str(v['version']) for v in versions]
        version,ok=QInputDialog.getItem(self,'Version history','Choose a version to restore as a new disabled version',items,0,False)
        if ok:self.safe(lambda:self.library.rollback(self.skill_id,int(version)));self.refresh_skills()

    def build_watch(self):
        layout=self.page('Watch & Learn');self.heading(layout,'Observe with permission','Public-page browser demonstrations only. A separate visible browser opens after approval. No passwords, typed values, screenshots or global keystrokes are captured.')
        self.watch_url=QLineEdit('https://example.com');layout.addWidget(self.watch_url)
        row=QHBoxLayout();row.addWidget(self.button('Start observation',self.start_watch));row.addWidget(self.button('Pause',lambda:self.safe(self.watch.pause)));row.addWidget(self.button('Resume',lambda:self.safe(self.watch.resume)));row.addWidget(self.button('Stop',self.stop_watch));layout.addLayout(row)
        self.watch_state=QLabel('NOT RECORDING');self.watch_state.setObjectName('heading');layout.addWidget(self.watch_state)
        self.annotation=QLineEdit();self.annotation.setPlaceholderText('Explain this step (do not include secrets)');layout.addWidget(self.annotation);layout.addWidget(self.button('Add instruction',self.annotate_watch))
        self.watch_review=QPlainTextEdit();self.watch_review.setPlaceholderText('Recorded steps and review-required navigation draft');layout.addWidget(self.watch_review,1)
        row=QHBoxLayout();row.addWidget(self.button('Review navigation draft',self.review_watch));row.addWidget(self.button('Export draft',self.export_watch));row.addWidget(self.button('Run reviewed navigation',self.replay_watch));row.addWidget(self.button('Delete recording',self.delete_watch));layout.addLayout(row)
    def start_watch(self):
        if QMessageBox.question(self,'Authorize observation','Open a separate visible browser and record public-page navigation and generic clicks?\n\nForms, logins and website scripts are blocked. Stop ends capture. No other desktop activity is observed.')!=QMessageBox.StandardButton.Yes:return
        self.safe(lambda:self.watch.start(self.watch_url.text(),consent=True));self.watch_state.setText('RECORDING • separate browser only')
    def stop_watch(self):
        self.watch.pause();self.watch_state.setText('CAPTURE STOPPED • closing browser')
        self.start_worker(lambda w:self.watch.stop(),lambda events:(self.watch_review.setPlainText(json.dumps(events,indent=2)),self.watch_state.setText('NOT RECORDING')))
    def annotate_watch(self):
        self.safe(lambda:self.watch.annotate(self.annotation.text()));self.annotation.clear()
    def review_watch(self):self.safe(lambda:self.watch_review.setPlainText(json.dumps(self.watch.to_workflow(),indent=2)))
    def export_watch(self):
        path=QFileDialog.getSaveFileName(self,'Export navigation draft','navigation-draft.json','JSON (*.json)')[0]
        if path:
            def save():
                with open(path,'x',encoding='utf-8') as f:f.write(self.watch_review.toPlainText())
            self.safe(save)
    def replay_watch(self):
        def action():
            data=json.loads(self.watch_review.toPlainText());steps=data.get('steps',[]) if isinstance(data,dict) else data
            if QMessageBox.question(self,'Approve navigation replay','Fetch these URLs in the background? Clicks and submissions remain blocked.\n'+json.dumps(steps,indent=2))==QMessageBox.StandardButton.Yes:
                self.jobs.submit('Navigation replay',lambda cancel,progress:BrowserSession(self.profile_dir).replay(steps,approved=True,cancel=cancel));self.go('Automations')
        self.safe(action)
    def delete_watch(self):
        if QMessageBox.question(self,'Delete recording','Delete captured events from this profile?')==QMessageBox.StandardButton.Yes:
            self.start_worker(lambda w:self.watch.delete(),lambda _:(self.watch_review.clear(),self.watch_state.setText('NOT RECORDING')))

    def build_jobs(self):
        layout=self.page('Automations');self.heading(layout,'Background activity','One deterministic worker in Eco mode. Minimize JARVIS and work continues. Reminders persist across restarts.')
        row=QHBoxLayout();row.addWidget(self.button('Refresh',self.refresh_jobs));row.addWidget(self.button('Pause queue',self.jobs.pause));row.addWidget(self.button('Resume queue',self.jobs.resume));row.addWidget(self.button('Cancel selected job',self.cancel_job));layout.addLayout(row)
        self.job_list=QListWidget();self.job_list.currentItemChanged.connect(self.show_job);layout.addWidget(self.job_list,1)
        self.job_detail=QPlainTextEdit();self.job_detail.setReadOnly(True);self.job_detail.setMaximumHeight(150);layout.addWidget(self.job_detail)
        row=QHBoxLayout();row.addWidget(QLabel('Reminders'));row.addStretch();row.addWidget(self.button('Add reminder',self.add_reminder));row.addWidget(self.button('Delete reminder',self.remove_reminder));layout.addLayout(row)
        self.schedule_list=QListWidget();self.schedule_list.setMaximumHeight(130);layout.addWidget(self.schedule_list)
    def refresh_jobs(self):
        self.job_list.clear()
        for job in self.jobs.list():
            item=QListWidgetItem(f"{job['label']}  ·  {job['status']}  ·  {job.get('progress',0)}");item.setData(Qt.ItemDataRole.UserRole,job);self.job_list.addItem(item)
        self.schedule_list.clear()
        for schedule in self.scheduler.list():
            item=QListWidgetItem(f"{schedule['label']}  ·  {schedule.get('due_iso',schedule.get('due',''))}");item.setData(Qt.ItemDataRole.UserRole,schedule['id']);self.schedule_list.addItem(item)
    def show_job(self,item,previous=None):
        if item:self.job_detail.setPlainText(json.dumps(item.data(Qt.ItemDataRole.UserRole),indent=2,default=str))
    def cancel_job(self):
        item=self.job_list.currentItem()
        if item:self.jobs.cancel(item.data(Qt.ItemDataRole.UserRole)['id']);self.refresh_jobs()
    def add_reminder(self):
        dialog=QDialog(self);dialog.setWindowTitle('New reminder');layout=QFormLayout(dialog)
        title=QLineEdit();due=QDateTimeEdit(datetime.now()+timedelta(minutes=10));due.setCalendarPopup(True)
        repeat=QComboBox();repeat.addItems(['Once','Every hour','Daily','Weekly'])
        layout.addRow('Reminder',title);layout.addRow('Local date and time',due);layout.addRow('Repeat',repeat)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addRow(buttons)
        if dialog.exec():
            interval=[0,3600,86400,604800][repeat.currentIndex()]
            self.safe(lambda:self.scheduler.add(title.text(),due.dateTime().toPython().astimezone().isoformat(),interval_seconds=interval));self.refresh_jobs()
    def remove_reminder(self):
        item=self.schedule_list.currentItem()
        if item:self.scheduler.remove(item.data(Qt.ItemDataRole.UserRole));self.refresh_jobs()

    def build_memory(self):
        layout=self.page('Memory');self.heading(layout,'Remember what matters','Only facts you explicitly save become memories. Conversation history stays local. Never store passwords or tokens here.')
        self.memory_search=QLineEdit();self.memory_search.setPlaceholderText('Search memories');self.memory_search.textChanged.connect(self.refresh_memory);layout.addWidget(self.memory_search)
        self.memory_list=QListWidget();layout.addWidget(self.memory_list,1)
        row=QHBoxLayout();row.addWidget(self.button('Add memory',self.add_memory));row.addWidget(self.button('Edit selected',self.edit_memory));row.addWidget(self.button('Delete selected',self.delete_memory));row.addWidget(self.button('Export memories',self.export_memory));layout.addLayout(row)
    def refresh_memory(self,*args):
        self.memory_list.clear()
        for memory in self.store.memories(self.memory_search.text()):
            item=QListWidgetItem(memory['text']);item.setData(Qt.ItemDataRole.UserRole,memory['id']);self.memory_list.addItem(item)
    def add_memory(self):
        text,ok=QInputDialog.getMultiLineText(self,'Save memory','Fact or preference')
        if ok and text:self.safe(lambda:self.store.remember(text));self.refresh_memory()
    def edit_memory(self):
        item=self.memory_list.currentItem()
        if not item:return
        text,ok=QInputDialog.getMultiLineText(self,'Edit memory','Fact or preference',item.text())
        if ok and text:
            def update():self.store.remember(text);self.store.forget(item.data(Qt.ItemDataRole.UserRole))
            self.safe(update);self.refresh_memory()
    def delete_memory(self):
        item=self.memory_list.currentItem()
        if item:self.store.forget(item.data(Qt.ItemDataRole.UserRole));self.refresh_memory()
    def export_memory(self):
        path=QFileDialog.getSaveFileName(self,'Export memories','memories.json','JSON (*.json)')[0]
        if path:
            def save():
                with open(path,'x',encoding='utf-8') as f:json.dump(self.store.memories(),f,indent=2)
            self.safe(save)

    def build_settings(self):
        layout=self.page('Settings');self.heading(layout,'Local by default','Permissions and model choices belong to this profile. No cloud inference or account integration is enabled.')
        scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();form=QFormLayout(body);scroll.setWidget(body);layout.addWidget(scroll)
        self.models=QComboBox();self.models.setEditable(True);self.models.addItem(self.model.model)
        row=QHBoxLayout();row.addWidget(self.models);row.addWidget(self.button('Discover',self.discover_models));row.addWidget(self.button('Use',self.select_model));form.addRow('Local AI model',row)
        row=QHBoxLayout();row.addWidget(self.button('Install selected model',self.pull_model));row.addWidget(self.button('Unload model',lambda:self.start_worker(lambda w:self.model.unload(),lambda _:self.notify('Model unload requested.'))));row.addWidget(self.button('Remove selected model',self.delete_model));form.addRow(row)
        row=QHBoxLayout();row.addWidget(self.button('Set up local AI automatically',lambda:self.setup_component('AI')));row.addWidget(self.button('Install browser runtime',lambda:self.setup_component('browser')));form.addRow(row)
        form.addRow(self.button('Benchmark local inference',lambda:self.start_worker(lambda w:self.model.benchmark(),lambda result:self.notify(json.dumps(result)))))
        self.roots=QListWidget();self.roots.setMaximumHeight(110);form.addRow('Authorized folders',self.roots);self.refresh_roots()
        row=QHBoxLayout();row.addWidget(self.button('Authorize folder',self.add_root));row.addWidget(self.button('Revoke selected',self.remove_root));form.addRow(row)
        self.memory_enabled=QCheckBox('Use explicit saved memories in conversation');self.memory_enabled.setChecked(self.store.settings().get('memory_enabled',True));self.memory_enabled.toggled.connect(lambda value:self.store.set_setting('memory_enabled',value));form.addRow(self.memory_enabled)
        row=QHBoxLayout();row.addWidget(self.button('Show floating assistant',lambda:self.bubble.show()));row.addWidget(self.button('Hide',lambda:self.bubble.hide()));form.addRow('Desktop bubble',row)
        opacity=QSlider(Qt.Orientation.Horizontal);opacity.setRange(30,100);opacity.setValue(int(self.store.settings().get('bubble_opacity',.9)*100));opacity.valueChanged.connect(lambda value:(self.bubble.setWindowOpacity(value/100),self.store.set_setting('bubble_opacity',value/100)));form.addRow('Bubble opacity',opacity)
        self.audio_devices=QComboBox();self.audio_devices.addItem('System default',None);form.addRow('Microphone',self.audio_devices)
        self.audio_devices.currentIndexChanged.connect(lambda _:self.store.set_setting('audio_device',self.audio_devices.currentData()))
        form.addRow(self.button('Detect audio devices',self.detect_audio))
        startup=QCheckBox('Start JARVIS at Windows sign-in (this profile)');startup.setChecked(self.store.settings().get('startup',False));startup.toggled.connect(self.set_startup);form.addRow(startup)
        row=QHBoxLayout();row.addWidget(self.button('Switch / create profile',self.switch_profile));row.addWidget(self.button('Backup conversation database',self.backup));form.addRow(row)
        form.addRow(QLabel('Data location'),QLabel(str(self.profile_dir)))
        form.addRow(self.button('Show first-run guide',self.tutorial))
        limitations=QLabel('Version 0.1: no wake word, arbitrary scripts, authenticated website automation, cloud credentials, runtime MCP, automatic updates, scheduled file workflows or folder triggers. These are not silently enabled.');limitations.setWordWrap(True);form.addRow(limitations)
    def change_mode(self,mode):
        self.model.mode=mode;self.store.set_setting('mode',mode)
        if hasattr(self,'status'):self.notify(mode+' mode selected')
    def setup_component(self,component):
        if QMessageBox.question(self,'Install local components','Download and install '+component+' components?\nAI setup uses the official Ollama winget package and Qwen3 0.6B. Browser setup uses Playwright Chromium. Internet and disk space are required. Setup may take several minutes; allow installation to finish before quitting.')!=QMessageBox.StandardButton.Yes:return
        from .setup import configure_ollama,install_browser
        self.notify('Setting up '+component+'…')
        self.start_worker(lambda w:configure_ollama() if component=='AI' else install_browser(),self.notify)
    def discover_models(self):
        def ready(names):self.models.clear();self.models.addItems(names or [self.model.model]);self.models.setCurrentText(self.model.model)
        self.start_worker(lambda w:self.model.models(),ready)
    def select_model(self):
        name=self.models.currentText().strip()
        try:OllamaClient._validate_model(name)
        except ValueError as e:self.error(str(e));return
        self.model.model=name;self.store.set_setting('model',name);self.notify('Selected '+name)
    def pull_model(self):
        name=self.models.currentText().strip()
        if QMessageBox.question(self,'Install model','Download '+name+' through the local Ollama server? This uses disk space and internet data. Check available memory before selecting larger models.')==QMessageBox.StandardButton.Yes:
            self.start_worker(lambda w:self.model.pull(name,progress=lambda data:w.chunk.emit(str(data))),lambda _:(self.discover_models(),self.notify('Model installed.')))
            self.notify('Downloading model…')
    def delete_model(self):
        name=self.models.currentText().strip()
        if QMessageBox.question(self,'Remove shared model','Remove '+name+' from Ollama? Other applications may also use this model.')==QMessageBox.StandardButton.Yes:self.start_worker(lambda w:self.model.delete(name),lambda _:self.discover_models())
    def refresh_roots(self):
        self.roots.clear();self.roots.addItems(self.store.settings().get('authorized_roots',[]))
    def add_root(self):
        folder=QFileDialog.getExistingDirectory(self,'Authorize a folder')
        if folder:
            roots=self.store.settings().get('authorized_roots',[])
            if folder not in roots:roots.append(folder);self.store.set_setting('authorized_roots',roots);self.refresh_roots()
    def remove_root(self):
        item=self.roots.currentItem()
        if item:self.store.set_setting('authorized_roots',[p for p in self.store.settings().get('authorized_roots',[]) if p!=item.text()]);self.refresh_roots()
    def detect_audio(self):
        def ready(devices):
            self.audio_devices.blockSignals(True);self.audio_devices.clear();self.audio_devices.addItem('System default',None)
            for d in devices:
                if d.get('max_input_channels',d.get('input_channels',0))>0:self.audio_devices.addItem(d.get('name','Microphone'),d.get('index'))
            self.audio_devices.blockSignals(False)
        self.start_worker(lambda w:self.speech.devices(),ready)
    def set_startup(self,enabled):
        def action():
            import winreg,subprocess
            key=winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Run')
            with key:
                if enabled:
                    args=[sys.executable]
                    if not getattr(sys,'frozen',False):args += [str(resources()/'main.py')]
                    args += ['--data-dir',str(self.profile_dir),'--minimized']
                    winreg.SetValueEx(key,'JARVIS',0,winreg.REG_SZ,subprocess.list2cmdline(args))
                else:
                    try:winreg.DeleteValue(key,'JARVIS')
                    except FileNotFoundError:pass
            self.store.set_setting('startup',enabled)
        self.safe(action)
    def switch_profile(self):
        name,ok=QInputDialog.getText(self,'Switch profile','Profile name (letters, numbers, dash)')
        if not ok:return
        import re,subprocess
        if not re.fullmatch('[A-Za-z0-9_-]{1,40}',name):self.error('Use 1–40 letters, numbers, underscores or dashes.');return
        args=[sys.executable]
        if not getattr(sys,'frozen',False):args += [str(resources()/'main.py')]
        args += ['--profile',name]
        subprocess.Popen(args,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));self.quit()
    def backup(self):
        path=QFileDialog.getSaveFileName(self,'Backup conversation database','jarvis-backup.sqlite3','SQLite (*.sqlite3)')[0]
        if path:self.safe(lambda:self.store.backup(path));self.notify('Backup requested. Skills export separately from the Skills page.')
    def build_help(self):
        layout=self.page('Help');self.heading(layout,'Help Centre','Offline reference for the features in this version.')
        search=QLineEdit();search.setPlaceholderText('Find in guide');layout.addWidget(search)
        self.help=QTextBrowser();self.help.setOpenExternalLinks(False);layout.addWidget(self.help,1)
        path=resources()/'docs'/'User-Guide.html'
        if path.exists():self.help.setSource(QUrl.fromLocalFile(str(path)))
        else:self.help.setPlainText(HELP)
        search.returnPressed.connect(lambda:self.help.find(search.text()))
        layout.addWidget(self.button('Open PDF manual',lambda:QDesktopServices.openUrl(QUrl.fromLocalFile(str(resources()/'docs'/'JARVIS-User-Guide.pdf')))))
    def tutorial(self):
        dialog=QDialog(self);dialog.setWindowTitle('Welcome to JARVIS');dialog.resize(650,520);layout=QVBoxLayout(dialog)
        text=QTextBrowser();text.setHtml('<h1>Your assistant, on your computer.</h1><p>1. <b>Chat:</b> ask questions. Try /time, /system and /help.</p><p>2. <b>Models:</b> Settings → Discover. Qwen3 0.6B is the low-memory default. Ollama must be installed and running.</p><p>3. <b>Permissions:</b> authorize only the folders you need. New output files preserve originals.</p><p>4. <b>Skills:</b> learn from CSV examples, test a draft, review and enable it.</p><p>5. <b>Watch &amp; Learn:</b> explicit public-page browser observation. This version does not learn logged-in uploads.</p><p>6. <b>Voice:</b> push to talk starts a bounded local recording. Review the text before sending. No background listening.</p><p>7. <b>Eco:</b> models unload after each response. Close minimizes to tray; Quit stops JARVIS.</p><p>The Help Centre documents limits. No cloud subscription or API key is needed.</p>');layout.addWidget(text)
        buttons=QDialogButtonBox();buttons.addButton('Get started',QDialogButtonBox.ButtonRole.AcceptRole);buttons.addButton('Skip',QDialogButtonBox.ButtonRole.RejectRole);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons);dialog.exec();self.store.set_setting('onboarded',True)
    def tick(self):
        try:
            self.scheduler.tick()
            for notice in self.scheduler.notifications[:]:
                self.tray.showMessage('JARVIS reminder',notice['label']);self.notify('Reminder: '+notice['label'])
            self.scheduler.notifications.clear()
            if self.tabs.tabText(self.tabs.currentIndex())=='Automations':self.refresh_jobs()
            if self.watch.error:self.watch_state.setText('NOT RECORDING • '+str(self.watch.error))
        except Exception as e:self.notify('Background check: '+str(e))
    def stop_all(self):
        for worker in self.workers:worker.cancel.set()
        self.speech.stop();self.watch.pause()
        for job in self.jobs.list():
            if job['status'] in ('queued','running'):self.jobs.cancel(job['id'])
        self.jobs.pause();self.notify('Stop requested • queue paused • capture paused')
    def shutdown(self):
        if self.closed:return
        self.closed=True;self.timer.stop();self.stop_all();self.watch.stop();self.jobs.shutdown()
        for worker in self.workers[:]:worker.cancel.set();worker.wait(3000)
        # Keep Store alive until worker callbacks have completed; process exit closes DB.
        self.bubble.close();self.tray.hide()
    def quit(self):
        if any(worker.isRunning() for worker in self.workers):
            self.stop_all();self.notify('Stopping work before quit…');QTimer.singleShot(500,self.quit_when_idle);return
        self.shutdown();QApplication.instance().quit()
    def quit_when_idle(self):
        if self.workers:QTimer.singleShot(500,self.quit_when_idle)
        else:self.quit()
    def closeEvent(self,event):
        if self.tray.isVisible() and not self.closed:self.hide();event.ignore()
        elif self.closed:event.accept()
        else:event.ignore();self.quit()

STYLE='''
QWidget { background:#101a24; color:#e3eaf0; font-family:"Segoe UI"; font-size:13px; }
QLabel#brand { font-size:26px; font-weight:700; color:#63e6cf; padding-right:20px; }
QLabel#heading { font-size:22px; font-weight:600; padding-bottom:6px; }
QTabWidget::pane { border:1px solid #2c414f; border-radius:8px; }
QTabBar::tab { background:#162632; padding:12px 17px; margin-right:2px; }
QTabBar::tab:selected { background:#244553; color:#7af2df; }
QPushButton { background:#243b49; border:1px solid #3c5869; border-radius:6px; padding:8px 12px; }
QPushButton:hover { background:#315465; border-color:#63e6cf; }
QPushButton:disabled { color:#70818a; }
QPushButton#bubble { font-size:27px; font-weight:bold; border-radius:22px; color:#63e6cf; }
QLineEdit,QPlainTextEdit,QTextBrowser,QListWidget,QComboBox,QDateTimeEdit,QSpinBox { background:#14232f; border:1px solid #304754; border-radius:5px; padding:8px; selection-background-color:#315c68; }
QListWidget::item { padding:8px; } QListWidget::item:selected { background:#244f5a; }
QScrollBar:vertical { background:#15232d; width:10px; } QScrollBar::handle:vertical { background:#3a5464; min-height:25px; }
QMenu { background:#1c303f; border:1px solid #45616c; } QMenu::item { padding:9px 18px; } QMenu::item:selected { background:#315465; }
'''

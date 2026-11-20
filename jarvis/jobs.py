"""Single-worker cooperative job queue and durable, coalescing reminders."""
from concurrent.futures import CancelledError
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import sqlite3
import threading
import time
import uuid


class JobManager:
    def __init__(self,profile_dir):
        Path(profile_dir).mkdir(parents=True,exist_ok=True)
        self.path=Path(profile_dir)/'jobs.sqlite3'
        self._lock=threading.RLock(); self._events={}; self._queue=queue.Queue()
        self._resume=threading.Event(); self._resume.set(); self._stop=threading.Event()
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY,label TEXT,status TEXT,progress REAL,result TEXT,error TEXT,created REAL)')
            db.execute("UPDATE jobs SET status='interrupted',error='Application stopped before completion; review before rerunning' WHERE status IN ('queued','running')")
        self._thread=threading.Thread(target=self._worker,name='Jarvis-Eco-worker',daemon=True); self._thread.start()

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10); db.row_factory=sqlite3.Row
        try:
            with db: yield db
        finally: db.close()

    def submit(self,label,fn):
        if not isinstance(label,str) or not label.strip() or len(label)>1000 or not callable(fn): raise ValueError('Invalid job')
        with self._lock:
            if self._stop.is_set(): raise RuntimeError('Job manager is shut down')
            jid=uuid.uuid4().hex; self._events[jid]=threading.Event()
            with self._db() as db: db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?)',(jid,label,'queued',0,None,None,time.time()))
            self._queue.put((jid,fn))
        return jid

    def _update(self,jid,**fields):
        with self._db() as db:
            db.execute('UPDATE jobs SET '+','.join(f'{key}=?' for key in fields)+' WHERE id=?',(*fields.values(),jid))

    def _worker(self):
        while not self._stop.is_set():
            try: item=self._queue.get(timeout=.5)
            except queue.Empty: continue
            if item is None: return
            jid,fn=item; cancel=self._events[jid]
            while not self._resume.wait(.2):
                if cancel.is_set() or self._stop.is_set(): break
            if cancel.is_set() or self._stop.is_set():
                self._update(jid,status='cancelled')
                with self._lock: self._events.pop(jid,None)
                continue
            # Resource pressure defers at most 5s; queued work cannot starve indefinitely.
            try:
                import psutil
                for _ in range(5):
                    if psutil.virtual_memory().available>=512*1024*1024 and psutil.cpu_percent(interval=None)<90: break
                    if cancel.wait(1) or self._stop.is_set(): break
            except ImportError: pass
            if cancel.is_set() or self._stop.is_set():
                self._update(jid,status='cancelled')
                with self._lock: self._events.pop(jid,None)
                continue
            self._update(jid,status='running')
            last_progress=[0.0]
            def progress(value):
                if cancel.is_set(): raise CancelledError()
                value=max(0,min(100,float(value)))
                if time.monotonic()-last_progress[0]>.2 or value==100:
                    self._update(jid,progress=value); last_progress[0]=time.monotonic()
            try:
                result=fn(cancel,progress)
                # A function that returned may have committed its result already. Preserve
                # completion rather than claiming cancellation after an atomic commit.
                payload=json.dumps(result,allow_nan=False)
                self._update(jid,status='completed',progress=100,result=payload)
            except CancelledError: self._update(jid,status='cancelled')
            except Exception as exc: self._update(jid,status='failed',error=f'{type(exc).__name__}: {exc}'[:2000])
            finally:
                with self._lock: self._events.pop(jid,None)

    def list(self):
        with self._db() as db: rows=[dict(r) for r in db.execute('SELECT * FROM jobs ORDER BY created DESC')]
        for row in rows: row['result']=json.loads(row['result']) if row['result'] is not None else None
        return rows

    def cancel(self,jid):
        with self._lock:
            event=self._events.get(jid)
            if event: event.set()
        with self._db() as db: db.execute("UPDATE jobs SET status='cancelled' WHERE id=? AND status='queued'",(jid,))

    def pause(self): self._resume.clear()

    def resume(self): self._resume.set()

    def shutdown(self):
        with self._lock:
            self._stop.set(); self._resume.set()
            for event in self._events.values(): event.set()
            self._queue.put(None)
        self._thread.join(timeout=5)
        with self._db() as db: db.execute("UPDATE jobs SET status='cancelled' WHERE status='queued'")


class Scheduler:
    """Only reminders: unbound callable permission is never persisted as approval."""
    def __init__(self,profile_dir,jobs,run_skill=None):
        Path(profile_dir).mkdir(parents=True,exist_ok=True)
        self.path=Path(profile_dir)/'schedule.sqlite3'; self.jobs=jobs; self.notifications=[]
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS schedules (id TEXT PRIMARY KEY,label TEXT,due REAL,interval_seconds REAL,enabled INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS deliveries (id TEXT PRIMARY KEY,schedule_id TEXT,label TEXT,due REAL,delivered INTEGER)')

    @contextmanager
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10); db.row_factory=sqlite3.Row
        try:
            with db: yield db
        finally: db.close()

    def add(self,label,due_iso,interval_seconds=0,skill_id=None,input_path='',output_path=''):
        if skill_id is not None or input_path or output_path: raise ValueError('Unattended skills require bound approvals; this scheduler supports reminders only')
        if not isinstance(label,str) or not label.strip() or len(label)>1000: raise ValueError('Invalid reminder label')
        if type(interval_seconds) not in (int,float) or not 0<=interval_seconds<=31536000 or 0<interval_seconds<10: raise ValueError('Interval must be zero or 10 seconds to one year')
        try: due=datetime.fromisoformat(due_iso)
        except (TypeError,ValueError) as exc: raise ValueError('Expected ISO date/time') from exc
        if due.tzinfo is None: raise ValueError('Due time requires timezone offset')
        sid=uuid.uuid4().hex
        with self._db() as db: db.execute('INSERT INTO schedules VALUES(?,?,?,?,1)',(sid,label,due.timestamp(),interval_seconds))
        return sid

    def list(self):
        with self._db() as db: rows=[dict(r) for r in db.execute('SELECT * FROM schedules ORDER BY due')]
        for row in rows:
            row['due_iso']=datetime.fromtimestamp(row['due'],timezone.utc).isoformat(); row['enabled']=bool(row['enabled'])
        return rows

    def remove(self,sid):
        with self._db() as db: db.execute('DELETE FROM schedules WHERE id=?',(sid,))

    def tick(self):
        now=time.time()
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            for row in db.execute('SELECT * FROM schedules WHERE enabled=1 AND due<=?',(now,)).fetchall():
                did=f"{row['id']}:{row['due']}"
                db.execute('INSERT OR IGNORE INTO deliveries VALUES(?,?,?,?,0)',(did,row['id'],row['label'],row['due']))
                interval=row['interval_seconds']
                if interval:
                    next_due=row['due']+(int((now-row['due'])//interval)+1)*interval
                    db.execute('UPDATE schedules SET due=? WHERE id=?',(next_due,row['id']))
                else: db.execute('UPDATE schedules SET enabled=0 WHERE id=?',(row['id'],))
            pending=[dict(r) for r in db.execute('SELECT * FROM deliveries WHERE delivered=0')]
            # Durable at-most-once claim, including across multiple Scheduler instances.
            db.execute('UPDATE deliveries SET delivered=1 WHERE delivered=0')
        for delivery in pending:
            notification={key:delivery[key] for key in ('id','label','due')}
            self.notifications.append(notification)
            self.jobs.submit('Reminder: '+delivery['label'],lambda cancel,progress,n=notification:n)

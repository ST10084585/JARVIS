"""Profile-local durable state. No automatic collection of personal memory."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
import threading
import uuid


DEFAULTS = {'mode': 'Eco', 'model': 'qwen3:0.6b', 'authorized_roots': [],
            'memory_enabled': True, 'network_enabled': False}


class Store:
    def __init__(self, profile_dir: Path):
        self.profile_dir = Path(profile_dir).absolute()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.workspace = self.profile_dir / 'workspace'
        self.workspace.mkdir(exist_ok=True)
        self.db_path = self.profile_dir / 'jarvis.db'
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.db_path, timeout=20, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.executescript('''
            PRAGMA journal_mode=WAL;
            PRAGMA foreign_keys=ON;
            PRAGMA secure_delete=ON;
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                role TEXT NOT NULL, content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
            CREATE INDEX IF NOT EXISTS messages_chat ON messages(chat_id, id);
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY, text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, detail TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')));
            PRAGMA user_version=1;
        ''')
        self._db.commit()

    def _write(self, sql, parameters=()):
        with self._lock, self._db:
            return self._db.execute(sql, parameters).rowcount

    def _rows(self, sql, parameters=()):
        with self._lock:
            return [dict(r) for r in self._db.execute(sql, parameters)]

    def settings(self) -> dict:
        result = json.loads(json.dumps(DEFAULTS))
        result.update({r['key']: json.loads(r['value']) for r in self._rows('SELECT * FROM settings')})
        return result

    def set_setting(self, key, value):
        if not isinstance(key, str) or not key or len(key) > 100:
            raise ValueError('Invalid setting name')
        if any(word in key.lower() for word in ('password', 'secret', 'token', 'api_key', 'credential')):
            raise ValueError('Credentials must not be stored in ordinary settings')
        if key == 'mode' and value not in ('Eco', 'Balanced', 'Performance'):
            raise ValueError('Unknown performance mode')
        if key == 'authorized_roots':
            if not isinstance(value, list) or not all(isinstance(p, str) and Path(p).is_absolute()
                    and not p.startswith(('\\\\', '//')) for p in value):
                raise ValueError('Authorized roots must be absolute folder paths')
        if key in ('memory_enabled', 'network_enabled') and not isinstance(value, bool):
            raise ValueError('Expected a boolean setting')
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
        if len(encoded) > 100_000:
            raise ValueError('Setting too large')
        self._write('INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, encoded))

    def new_chat(self, title='New chat') -> str:
        identifier = uuid.uuid4().hex
        self._write('INSERT INTO chats(id,title) VALUES (?,?)', (identifier, self._title(title)))
        return identifier

    @staticmethod
    def _title(title):
        if not isinstance(title, str) or not title.strip() or len(title) > 500:
            raise ValueError('Title must contain 1–500 characters')
        return title.strip()

    def chats(self, search='') -> list[dict]:
        # instr treats wildcard characters literally and never interpolates SQL.
        return self._rows('SELECT id,title,archived FROM chats WHERE instr(lower(title),lower(?))>0 ORDER BY created_at DESC,id', (search,))

    def messages(self, chat_id) -> list[dict]:
        return self._rows('SELECT role,content FROM messages WHERE chat_id=? ORDER BY id', (chat_id,))

    def add_message(self, chat_id, role, content):
        if role not in ('system', 'user', 'assistant', 'tool'):
            raise ValueError('Unknown message role')
        if not isinstance(content, str) or len(content) > 1_000_000:
            raise ValueError('Message must be text shorter than one million characters')
        self._write('INSERT INTO messages(chat_id,role,content) VALUES (?,?,?)', (chat_id, role, content))

    def rename_chat(self, id, title):
        self._write('UPDATE chats SET title=? WHERE id=?', (self._title(title), id))

    def delete_chat(self, id):
        self._write('DELETE FROM chats WHERE id=?', (id,))

    def archive_chat(self, id):
        self._write('UPDATE chats SET archived=1 WHERE id=?', (id,))

    def memories(self, search='') -> list[dict]:
        return self._rows('SELECT id,text FROM memories WHERE instr(lower(text),lower(?))>0 ORDER BY created_at DESC,id', (search,))

    def remember(self, text) -> str:
        if not self.settings()['memory_enabled']:
            raise PermissionError('Memory is disabled in settings')
        if not isinstance(text, str) or not text.strip() or len(text) > 10_000:
            raise ValueError('Memory must contain 1–10,000 characters')
        if re.search(r'(?i)\b(password|passphrase|api[ _-]?key|access[ _-]?token|secret[ _-]?key)\s*(?:is\b|[:=])|-----BEGIN .*PRIVATE KEY-----', text):
            raise ValueError('Do not save credentials in memory; use a password manager')
        identifier = uuid.uuid4().hex
        self._write('INSERT INTO memories(id,text) VALUES (?,?)', (identifier, text.strip()))
        return identifier

    def forget(self, id):
        self._write('DELETE FROM memories WHERE id=?', (id,))

    def audit(self, action, detail):
        # Callers must pass status/metadata, never raw document or secret content.
        self._write('INSERT INTO audit(action,detail) VALUES (?,?)', (str(action)[:100], str(detail)[:2000]))

    def backup(self, path):
        destination = Path(path)
        # Reserve exclusively so backups cannot replace files or the active database.
        fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            with self._lock:
                target = sqlite3.connect(destination)
                try:
                    self._db.backup(target)
                finally:
                    target.close()
        except BaseException:
            destination.unlink(missing_ok=True)
            raise

    def close(self):
        with self._lock:
            if self._db is not None:
                self._db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
                self._db.close()
                self._db = None

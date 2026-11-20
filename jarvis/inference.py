"""Local-only Ollama client with bounded context and cross-profile serialization."""
from __future__ import annotations

from contextlib import contextmanager
import ctypes
import json
import os
import re
import socket
import threading
import time


_GENERATION_LOCK = threading.Lock()


@contextmanager
def generation_slot(cancel=None):
    """Serialize app profiles without creating another inference service."""
    acquired = False
    handle = None
    kernel = None
    try:
        if os.name == 'nt':
            from ctypes import wintypes
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
            kernel.CreateMutexW.restype = wintypes.HANDLE
            kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            kernel.WaitForSingleObject.restype = wintypes.DWORD
            kernel.ReleaseMutex.argtypes = [wintypes.HANDLE]
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            handle = kernel.CreateMutexW(None, False, 'Local\\JARVIS.Ollama.Generation.v1')
            if not handle:
                raise OSError(ctypes.get_last_error(), 'Could not create inference mutex')
            while not (cancel and cancel.is_set()):
                status = kernel.WaitForSingleObject(handle, 100)
                if status in (0, 0x80):  # acquired or abandoned by a crashed process
                    acquired = True
                    break
                if status != 0x102:
                    raise OSError('Could not acquire inference mutex')
        else:
            while not (cancel and cancel.is_set()):
                if _GENERATION_LOCK.acquire(timeout=0.1):
                    acquired = True
                    break
        yield acquired
    finally:
        if kernel is not None and handle:
            if acquired:
                kernel.ReleaseMutex(handle)
            kernel.CloseHandle(handle)
        elif acquired:
            _GENERATION_LOCK.release()


class OllamaClient:
    BASE_URL = 'http://127.0.0.1:11434'

    def __init__(self, model='qwen3:0.6b', mode='Eco'):
        self._validate_model(model)
        if mode not in ('Eco', 'Balanced', 'Performance'):
            raise ValueError('Unknown performance mode')
        self.model = model
        self.mode = mode

    @property
    def keep_alive(self):
        return {'Eco': 0, 'Balanced': '60s', 'Performance': '5m'}[self.mode]

    @staticmethod
    def _validate_model(name):
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}', name) or '://' in name or '..' in name:
            raise ValueError('Invalid Ollama model name')

    @staticmethod
    def _session():
        import requests
        session = requests.Session()
        session.trust_env = False
        return session

    @staticmethod
    def _check(response):
        if 300 <= response.status_code < 400:
            raise RuntimeError('Local inference redirects are prohibited')
        response.raise_for_status()

    def models(self):
        with self._session() as session:
            with session.get(self.BASE_URL + '/api/tags', timeout=(3, 10), allow_redirects=False) as response:
                self._check(response)
                return [entry['name'] for entry in response.json().get('models', [])]

    @staticmethod
    def _messages(messages):
        # Keep recent conversational context below the small-model budget.
        messages = list(messages)
        if any(not isinstance(message, dict) or message.get('role') not in ('system', 'user', 'assistant', 'tool')
               or not isinstance(message.get('content'), str) for message in messages):
            raise ValueError('Invalid chat message')
        system = []
        if messages and messages[0].get('role') == 'system':
            content = messages.pop(0).get('content')
            if not isinstance(content, str):
                raise ValueError('Message content must be text')
            system = [{'role': 'system', 'content': content[:1500]}]
        selected = []
        remaining = 6000 - sum(len(item['content']) for item in system)
        for message in reversed(messages):
            if not isinstance(message, dict) or message.get('role') not in ('system', 'user', 'assistant', 'tool'):
                raise ValueError('Invalid chat message')
            content = message.get('content')
            if not isinstance(content, str):
                raise ValueError('Message content must be text')
            if remaining <= 0:
                break
            text = content[-remaining:]
            selected.append({'role': message['role'], 'content': text})
            remaining -= len(text)
        return system + list(reversed(selected))

    def stream(self, messages, cancel=None):
        if cancel and cancel.is_set():
            return
        payload = {'model': self.model, 'messages': self._messages(messages),
                   'stream': True, 'think': False, 'keep_alive': self.keep_alive,
                   'options': {'num_ctx': 2048, 'num_predict': 512, 'num_thread': 4}}
        with generation_slot(cancel) as acquired:
            if not acquired or cancel and cancel.is_set():
                return
            with self._session() as session:
                with session.post(self.BASE_URL + '/api/chat', json=payload, stream=True,
                                  timeout=(3, 120), allow_redirects=False) as response:
                    self._check(response)
                    stopped = threading.Event()
                    def watch_cancel():
                        while not stopped.wait(0.1):
                            if cancel and cancel.is_set():
                                # Shutdown interrupts a blocked socket read before close waits for it.
                                try:
                                    sock = response.raw._fp.fp.raw._sock
                                    sock.shutdown(socket.SHUT_RDWR)
                                    socket.close(sock.detach())
                                except (AttributeError, OSError):
                                    pass
                                response.close()
                                return
                    watcher = None
                    if cancel is not None:
                        watcher = threading.Thread(target=watch_cancel, name='OllamaCancellation', daemon=True)
                        watcher.start()
                    completed = False
                    try:
                        for line in response.iter_lines(chunk_size=1):
                            if cancel and cancel.is_set():
                                return
                            if not line:
                                continue
                            data = json.loads(line)
                            if data.get('error'):
                                raise RuntimeError(data['error'])
                            text = data.get('message', {}).get('content', '')
                            if text:
                                yield text
                            if data.get('done'):
                                completed = True
                                break
                        if not completed and not (cancel and cancel.is_set()):
                            raise RuntimeError('Local model stream ended before completion')
                    except Exception:
                        if not (cancel and cancel.is_set()):
                            raise
                    finally:
                        stopped.set()
                        response.close()
                        if watcher is not None:
                            watcher.join(timeout=0.5)

    def unload(self):
        with generation_slot():
            with self._session() as session:
                with session.post(self.BASE_URL + '/api/generate', json={'model': self.model, 'keep_alive': 0},
                                  timeout=(3, 20), allow_redirects=False) as response:
                    self._check(response)

    def pull(self, name, progress=None):
        self._validate_model(name)
        with self._session() as session:
            with session.post(self.BASE_URL + '/api/pull', json={'name': name, 'stream': True},
                              stream=True, timeout=(3, 120), allow_redirects=False) as response:
                self._check(response)
                completed = False
                for line in response.iter_lines():
                    if not line:
                        continue
                    record = json.loads(line)
                    if record.get('error'):
                        raise RuntimeError(record['error'])
                    if progress:
                        progress(record)
                    if record.get('status') == 'success':
                        completed = True
                if not completed:
                    raise RuntimeError('Model download ended without confirmation')

    def delete(self, name):
        self._validate_model(name)
        with generation_slot():
            with self._session() as session:
                with session.delete(self.BASE_URL + '/api/delete', json={'name': name},
                                    timeout=(3, 30), allow_redirects=False) as response:
                    self._check(response)

    def benchmark(self):
        start = time.perf_counter()
        text = ''.join(self.stream([{'role': 'user', 'content': 'In one sentence, explain what a local computer assistant does.'}]))
        return {'model': self.model, 'mode': self.mode,
                'seconds': round(time.perf_counter() - start, 3), 'characters': len(text), 'response': text}

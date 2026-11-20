"""Isolated public-web reading and opt-in, bounded public-page demonstrations."""
import copy
import http.client
import ipaddress
import json
import re
import socket
import ssl
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urljoin

MAX_BYTES = 2 * 1024 * 1024


def validate_url(url):
    if not isinstance(url, str) or len(url) > 4096 or any(ord(c) < 33 for c in url):
        raise ValueError('Invalid URL')
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Only public HTTP(S) URLs without credentials are permitted')
    if p.port not in (None, 80, 443):
        raise ValueError('Only standard web ports are permitted')
    records = socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == 'https' else 80), type=socket.SOCK_STREAM)
    addresses = list(dict.fromkeys(r[4][0] for r in records))
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
        raise ValueError('Local, private and reserved destinations are blocked')
    return p, addresses


def recorded_url(url):
    try:
        p = urlsplit(url)
        if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
            return None
        # Omit authentication links and opaque identifiers rather than recording secrets.
        if re.search(r'(?i)(token|auth|login|logout|reset|password|secret|session|oauth|callback)', p.path):
            return None
        if any(len(part) > 40 for part in p.path.split('/')):
            return None
        return urlunsplit((p.scheme, p.netloc, p.path, '', ''))
    except ValueError:
        return None


def _cancelled(cancel):
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Browser operation cancelled')


def _fetch(url, cancel=None):
    deadline = time.monotonic() + 20
    for _ in range(6):
        _cancelled(cancel)
        p, addresses = validate_url(url)
        timeout = deadline - time.monotonic()
        if timeout <= 0:
            raise TimeoutError('Web read exceeded 20 seconds')
        port = p.port or (443 if p.scheme == 'https' else 80)
        sock = socket.create_connection((addresses[0], port), timeout=min(timeout, 5))
        conn = http.client.HTTPConnection(p.hostname, port, timeout=min(timeout, 5))
        try:
            if p.scheme == 'https':
                sock = ssl.create_default_context().wrap_socket(sock, server_hostname=p.hostname)
            conn.sock = sock
            conn.request('GET', urlunsplit(('', '', p.path or '/', p.query, '')),
                         headers={'Host': p.netloc, 'User-Agent': 'JARVIS-PublicReader/1.0', 'Accept-Encoding': 'identity'})
            response = conn.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader('Location')
                if not location:
                    raise ValueError('Redirect missing destination')
                url = urljoin(url, location)
                continue
            if response.status >= 400:
                raise ValueError(f'Website returned HTTP {response.status}')
            content_type = response.getheader('Content-Type', '').split(';')[0].lower()
            if content_type not in ('text/html', 'text/plain', 'application/xhtml+xml'):
                raise ValueError('Only HTML and plain text documents are supported')
            if response.getheader('Content-Encoding', 'identity') != 'identity':
                raise ValueError('Compressed responses are not supported')
            if int(response.getheader('Content-Length', '0')) > MAX_BYTES:
                raise ValueError('Web document exceeds 2 MiB')
            data = bytearray()
            while True:
                _cancelled(cancel)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Web read exceeded 20 seconds')
                sock.settimeout(min(remaining, 2))
                chunk = response.read1(min(65536, MAX_BYTES + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
                if len(data) > MAX_BYTES:
                    raise ValueError('Web document exceeds 2 MiB')
            return url, content_type, bytes(data)
        finally:
            conn.close()
            sock.close()
    raise ValueError('Too many redirects')


def browser_options():
    import os
    for variable in ('PROGRAMFILES(X86)', 'PROGRAMFILES'):
        if (Path(os.environ.get(variable, ''))/'Microsoft/Edge/Application/msedge.exe').is_file():
            return {'channel': 'msedge'}
    return {}


class BrowserSession:
    def __init__(self, profile_dir):
        self.profile_dir = Path(profile_dir)

    def read(self, url, cancel=None):
        final_url, mime, body = _fetch(url, cancel)
        _cancelled(cancel)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, **browser_options())
            try:
                context = browser.new_context(java_script_enabled=False, service_workers='block', accept_downloads=False)
                context.route('**/*', lambda route: route.abort())
                page = context.new_page()
                if mime == 'text/plain':
                    import html
                    body = ('<pre>' + html.escape(body.decode('utf-8', errors='replace')) + '</pre>').encode()
                page.set_content(body.decode('utf-8', errors='replace'), timeout=10000, wait_until='domcontentloaded')
                _cancelled(cancel)
                return {'url': final_url, 'title': page.title(), 'text': page.locator('body').inner_text(timeout=5000)[:100000]}
            finally:
                browser.close()

    def replay(self, steps, approved=False, cancel=None):
        if not isinstance(steps, list) or len(steps) > 30:
            raise ValueError('Replay requires at most 30 declarative steps')
        for step in steps:
            if not isinstance(step, dict) or step.get('action') not in ('navigate', 'read', 'extract') or set(step) - {'action', 'url'}:
                raise ValueError('Only explicit URL navigation/read/extract is replayable; clicks and submissions require manual execution')
            if not isinstance(step.get('url'), str):
                raise ValueError('Each step requires an explicit URL')
        if not approved:
            raise PermissionError('Review and approve the exact workflow before replay')
        results = [self.read(step['url'], cancel) for step in copy.deepcopy(steps)]
        return {'results': results, 'completed': len(results)}


class WatchLearn:
    def __init__(self, profile_dir):
        self.path = Path(profile_dir) / 'watch' / 'events.json'
        self._lock = threading.RLock()
        self._active = threading.Event()
        self._stop = threading.Event()
        self._thread = None
        self.error = None
        self._events = []
        if self.path.is_file():
            try:
                data = json.loads(self.path.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    self._events = data[:1000]
            except (OSError, ValueError):
                pass

    @property
    def running(self):
        return bool(self._thread and self._thread.is_alive())

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self._events, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(self.path)

    def _record(self, event):
        with self._lock:
            if not self._active.is_set() or self._stop.is_set() or len(self._events) >= 1000:
                return
            clean = {'action': event.get('action'), 'time': time.time()}
            if clean['action'] in ('navigate', 'click'):
                url = recorded_url(event.get('url', ''))
                if url is None:
                    return
                clean['url'] = url
                if clean['action'] == 'click':
                    clean['tag'] = event.get('tag') if event.get('tag') in ('A', 'BUTTON', 'SUMMARY') else 'OTHER'
                    clean['replayable'] = False
            elif clean['action'] == 'annotation':
                clean['text'] = str(event.get('text', ''))[:2000]
            else:
                return
            self._events.append(clean)
            self._save()

    def start(self, url, consent=False):
        if not consent:
            raise PermissionError('Explicit observation consent is required')
        if self.running:
            raise RuntimeError('Observation is already running')
        validate_url(url)
        self.error = None
        self._stop.clear()
        self._active.set()
        with self._lock:
            self._events = []
            self._save()
        self._thread = threading.Thread(target=self._run, args=(url,), name='JarvisWatchBrowser', daemon=True)
        self._thread.start()

    def _run(self, url):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=False, **browser_options())
                try:
                    context = browser.new_context(service_workers='block', accept_downloads=False)
                    def route_request(route):
                        request = route.request
                        if self._stop.is_set() or request.method != 'GET' or request.resource_type != 'document':
                            route.abort()
                            return
                        try:
                            final, mime, body = _fetch(request.url, self._stop)
                            route.fulfill(status=200, content_type=mime, body=body,
                                          headers={'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; form-action 'none'; frame-src 'none'; base-uri 'none'"})
                        except Exception:
                            route.abort()
                    context.route('**/*', route_request)
                    page = context.new_page()
                    page.expose_binding('__jarvisEvent', lambda source, event: self._record(event) if source['frame'] == page.main_frame else None)
                    page.add_init_script("""document.addEventListener('click', e => {
                        const el=e.target.closest('a,button,summary');
                        if (!el || el.closest('form') || e.target.closest('input,textarea,[contenteditable]')) return;
                        window.__jarvisEvent({action:'click',url:location.href,tag:el.tagName});
                    }, true);""")
                    page.on('framenavigated', lambda frame: self._record({'action': 'navigate', 'url': frame.url}) if frame == page.main_frame else None)
                    page.on('popup', lambda popup: popup.close())
                    page.goto(url, timeout=22000, wait_until='domcontentloaded')
                    while not self._stop.is_set() and not page.is_closed():
                        page.wait_for_timeout(100)
                finally:
                    browser.close()
        except Exception as exc:
            if not self._stop.is_set():
                self.error = f'{type(exc).__name__}: observation could not continue'
        finally:
            self._active.clear()

    def pause(self):
        with self._lock:
            self._active.clear()

    def resume(self):
        if not self.running:
            raise RuntimeError('No active observation session')
        self._active.set()

    def annotate(self, text):
        self._record({'action': 'annotation', 'text': text})

    def stop(self):
        with self._lock:
            self._active.clear()
            self._stop.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=25)
        return self.events()

    def events(self):
        with self._lock:
            return copy.deepcopy(self._events)

    def delete(self):
        self.stop()
        with self._lock:
            self._events = []
            self.path.unlink(missing_ok=True)
            self.path.with_suffix('.tmp').unlink(missing_ok=True)

    def to_workflow(self):
        events = self.events()
        steps = [{'action': 'navigate', 'url': e['url']} for e in events if e.get('action') == 'navigate']
        return {'name': 'Observed public web navigation', 'kind': 'browser', 'requires_review': True,
                'steps': steps, 'notes': [e for e in events if e.get('action') != 'navigate']}

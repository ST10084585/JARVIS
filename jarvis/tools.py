"""Small deterministic tools with mandatory path and foreground policy."""
from __future__ import annotations

from datetime import datetime
import fnmatch
import os
from pathlib import Path, PureWindowsPath
import platform
import shutil
import socket
import stat
import subprocess
import threading
import time
import zipfile


class ApprovalRequired(PermissionError):
    def __init__(self, description):
        self.description = description
        super().__init__(description)


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise InterruptedError('Operation cancelled')


def is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
        return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)
    except FileNotFoundError:
        return False


class ToolRegistry:
    MAX_BYTES = 25 * 1024 * 1024
    MAX_TEXT = 100_000
    DIAGNOSTICS = {
        'processes': 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 Name,Id,CPU,WorkingSet64 | ConvertTo-Json',
        'disks': 'Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,Size,FreeSpace | ConvertTo-Json',
        'os': 'Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,LastBootUpTime | ConvertTo-Json',
    }
    DESCRIPTORS = [
        ('time', 'Read the local date and time', {}, False, True),
        ('system_info', 'Read real CPU, memory, operating system and disk usage', {}, False, True),
        ('find_files', 'Find files under an authorized folder (maximum 500)', {'path': 'optional folder', 'pattern': 'optional filename wildcard'}, False, True),
        ('read_document', 'Extract bounded text from TXT, MD, CSV, JSON, PDF, DOCX or XLSX', {'path': 'file'}, False, True),
        ('write_note', 'Create a new TXT or Markdown note without replacing files', {'path': 'optional new .txt/.md path', 'text': 'note text'}, False, True),
        ('copy_file', 'Copy an authorized file to a new destination', {'source': 'file', 'destination': 'new file'}, False, True),
        ('make_directory', 'Create a new directory in an authorized folder', {'path': 'new directory'}, False, True),
        ('open_notepad', 'Open Notepad visibly on explicit approval', {}, True, False),
        ('network_check', 'Explicit outbound TCP connection to Cloudflare DNS port 443', {}, True, True),
        ('powershell_diagnostic', 'Run one fixed read-only Windows diagnostic', {'diagnostic': 'processes | disks | os'}, False, True),
    ]

    def __init__(self, store):
        self.store = store

    def list(self):
        return [dict(name=n, description=d, parameters=p.copy(), approval=a, unattended=u)
                for n, d, p, a, u in self.DESCRIPTORS]

    def authorize_path(self, value, *, write=False, approved=False, unattended=False) -> Path:
        if not isinstance(value, (str, Path)) or not str(value).strip():
            raise ValueError('A nonempty local path is required')
        raw = str(value)
        win = PureWindowsPath(raw)
        if raw.startswith(('\\\\', '//')) or '\x00' in raw:
            raise PermissionError('Network and device paths are not permitted')
        if win.drive and not win.is_absolute():
            raise PermissionError('Drive-relative paths are not permitted')
        for part in win.parts:
            if part == win.anchor:
                continue
            if ':' in part or part.endswith((' ', '.')) and part not in ('.', '..'):
                raise PermissionError('Alternate streams and ambiguous paths are not permitted')
            if PureWindowsPath(part).is_reserved():
                raise PermissionError('Windows device names are not permitted')
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = self.store.workspace / candidate
        # Inspect lexical ancestors before resolve() can hide a junction or symlink.
        for component in (candidate, *candidate.parents):
            if is_reparse(component):
                raise PermissionError('Symbolic links and reparse points are not permitted')
        candidate = candidate.resolve()
        workspace = self.store.workspace.resolve()
        roots = [workspace]
        for root in self.store.settings().get('authorized_roots', []):
            if str(root).startswith(('\\\\', '//')):
                continue
            root = Path(root)
            if any(is_reparse(p) for p in (root, *root.parents)):
                continue
            roots.append(root.resolve())
        if not any(candidate.is_relative_to(root) for root in roots):
            raise PermissionError('Path is outside the authorized folders')
        if write and not candidate.is_relative_to(workspace):
            if unattended:
                raise PermissionError('Unattended writes are confined to the profile workspace')
            if not approved:
                raise ApprovalRequired(f'Create a new file or folder outside the workspace: {candidate}')
        return candidate

    def execute(self, name, args, approved=False, unattended=False, cancel=None) -> dict:
        if not isinstance(args, dict):
            raise ValueError('Tool arguments must be an object')
        descriptors = {d['name']: d for d in self.list()}
        if name not in descriptors:
            raise ValueError('Unknown tool')
        spec = descriptors[name]
        if set(args) - set(spec['parameters']):
            raise ValueError('Unexpected tool arguments')
        check_cancel(cancel)
        if unattended and not spec['unattended']:
            raise PermissionError('This tool cannot run unattended')
        if spec['approval'] and not approved:
            raise ApprovalRequired(spec['description'])
        try:
            result = self._execute(name, args, approved, unattended, cancel)
        except Exception as exc:
            self.store.audit(name, f'failed: {type(exc).__name__}')
            raise
        self.store.audit(name, 'completed')
        return result

    def _execute(self, name, args, approved, unattended, cancel):
        def path(value, write=False):
            return self.authorize_path(value, write=write, approved=approved, unattended=unattended)
        if name == 'time':
            return {'time': datetime.now().astimezone().isoformat(timespec='seconds')}
        if name == 'system_info':
            import psutil
            memory = psutil.virtual_memory()
            disk = shutil.disk_usage(self.store.workspace)
            return {'os': platform.platform(), 'cpu_count': os.cpu_count(),
                    'cpu_percent': psutil.cpu_percent(interval=0.15),
                    'memory_total': memory.total, 'memory_available': memory.available,
                    'disk_free': disk.free, 'disk_total': disk.total}
        if name == 'find_files':
            root = path(args.get('path', '.'))
            pattern = args.get('pattern', '*')
            if not isinstance(pattern, str) or len(pattern) > 200 or '/' in pattern or '\\' in pattern:
                raise ValueError('Pattern must be a filename wildcard')
            if not root.is_dir():
                raise NotADirectoryError(root)
            found = []
            started = time.monotonic()
            for directory, dirs, files in os.walk(root, followlinks=False):
                check_cancel(cancel)
                dirs[:] = [d for d in dirs if not is_reparse(Path(directory) / d)]
                for filename in files:
                    candidate = Path(directory) / filename
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()) and not is_reparse(candidate):
                        found.append(str(path(candidate)))
                        if len(found) >= 500:
                            return {'files': found, 'truncated': True}
                if time.monotonic() - started > 10:
                    return {'files': found, 'truncated': True}
            return {'files': found, 'truncated': False}
        if name == 'read_document':
            source = path(args['path'])
            if not source.is_file():
                raise FileNotFoundError(source)
            if source.stat().st_size > self.MAX_BYTES:
                raise ValueError('Document exceeds the 25 MB limit')
            text = self._read(source, cancel)
            return {'path': str(source), 'text': text[:self.MAX_TEXT], 'truncated': len(text) > self.MAX_TEXT}
        if name == 'write_note':
            target = path(args.get('path', f'note-{datetime.now():%Y%m%d-%H%M%S-%f}.txt'), True)
            if target.suffix.lower() not in ('.txt', '.md'):
                raise ValueError('Notes must use .txt or .md')
            text = args['text']
            if not isinstance(text, str) or len(text) > self.MAX_TEXT:
                raise ValueError('Note must be text of at most 100,000 characters')
            check_cancel(cancel)
            with target.open('x', encoding='utf-8', newline='') as output:
                output.write(text)
            return {'path': str(target), 'characters': len(text)}
        if name == 'make_directory':
            target = path(args['path'], True)
            check_cancel(cancel)
            target.mkdir(exist_ok=False)
            return {'path': str(target)}
        if name == 'copy_file':
            source, target = path(args['source']), path(args['destination'], True)
            if source.stat().st_size > 512 * 1024 * 1024:
                raise ValueError('Copy exceeds the 512 MB limit')
            created = False
            try:
                with source.open('rb') as inp, target.open('xb') as out:
                    created = True
                    while chunk := inp.read(1024 * 1024):
                        check_cancel(cancel)
                        out.write(chunk)
            except BaseException:
                if created:
                    target.unlink(missing_ok=True)
                raise
            return {'path': str(target), 'bytes': target.stat().st_size}
        if name == 'open_notepad':
            if os.name != 'nt':
                raise OSError('Notepad requires Windows')
            program = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'notepad.exe'
            process = subprocess.Popen([str(program)], shell=False)
            return {'pid': process.pid, 'message': 'Notepad launched'}
        if name == 'network_check':
            check_cancel(cancel)
            start = time.monotonic()
            try:
                with socket.create_connection(('1.1.1.1', 443), timeout=4):
                    return {'reachable': True, 'target': '1.1.1.1:443', 'seconds': round(time.monotonic()-start, 3)}
            except OSError as exc:
                return {'reachable': False, 'target': '1.1.1.1:443', 'error': str(exc)}
        if name == 'powershell_diagnostic':
            command = self.DIAGNOSTICS.get(args.get('diagnostic'))
            if not command:
                raise ValueError('Diagnostic must be processes, disks, or os')
            if os.name != 'nt':
                raise OSError('This diagnostic requires Windows')
            executable = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
            process = subprocess.Popen([str(executable), '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', command],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            start = time.monotonic()
            try:
                while True:
                    check_cancel(cancel)
                    if time.monotonic() - start > 20:
                        raise TimeoutError('Diagnostic exceeded 20 seconds')
                    try:
                        output, error = process.communicate(timeout=0.2)
                        break
                    except subprocess.TimeoutExpired:
                        pass
            except BaseException:
                process.kill(); process.communicate()
                raise
            if process.returncode:
                raise RuntimeError(error.decode(errors='replace')[:2000])
            return {'diagnostic': args['diagnostic'], 'text': output.decode(errors='replace')[:self.MAX_TEXT]}
        raise ValueError('Unknown tool')

    def _read(self, source, cancel):
        suffix = source.suffix.lower()
        if suffix in ('.docx', '.xlsx'):
            with zipfile.ZipFile(source) as archive:
                members = archive.infolist()
                if len(members) > 20_000 or sum(item.file_size for item in members) > 100 * 1024 * 1024:
                    raise ValueError('Document expanded size exceeds the safe parsing limit')
        chunks = []
        length = 0
        def collect(values):
            nonlocal length
            for text in values:
                check_cancel(cancel)
                text = str(text)
                chunks.append(text)
                length += len(text) + 1
                if length > self.MAX_TEXT:
                    break
            return '\n'.join(chunks)
        if suffix == '.pdf':
            from pypdf import PdfReader
            with source.open('rb') as stream:
                reader = PdfReader(stream)
                if reader.is_encrypted:
                    raise ValueError('Encrypted PDF is not supported')
                return collect(page.extract_text() or '' for page in reader.pages)
        if suffix == '.docx':
            from docx import Document
            document = Document(source)
            def paragraphs():
                yield from (p.text for p in document.paragraphs)
                for table in document.tables:
                    for row in table.rows:
                        yield '\t'.join(cell.text for cell in row.cells)
            return collect(paragraphs())
        if suffix == '.xlsx':
            from openpyxl import load_workbook
            workbook = load_workbook(source, read_only=True, data_only=True, keep_links=False)
            try:
                def rows():
                    for sheet in workbook:
                        yield f'[{sheet.title}]'
                        for row in sheet.iter_rows(values_only=True):
                            yield '\t'.join('' if cell is None else str(cell) for cell in row)
                return collect(rows())
            finally:
                workbook.close()
        if suffix in ('.txt', '.md', '.csv', '.json', '.log', '.xml', '.html', '.htm', '.yaml', '.yml'):
            with source.open(encoding='utf-8-sig', errors='replace') as stream:
                return stream.read(self.MAX_TEXT + 1)
        raise ValueError('Unsupported document format; use TXT, Markdown, CSV, JSON, PDF, DOCX or XLSX')

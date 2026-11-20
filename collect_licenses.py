import importlib.metadata as metadata
from pathlib import Path
import shutil

root=Path('licenses');root.mkdir(exist_ok=True)
(root/'Vosk').mkdir(exist_ok=True)
shutil.copy2('docs/Vosk-COPYING.txt',root/'Vosk'/'COPYING')
lines=['JARVIS 0.1 — THIRD-PARTY COMPONENTS','',
'The application uses dynamically linked Qt/PySide6 libraries. Their LGPL/commercial licensing options are described at https://doc.qt.io/qtforpython-6/licenses.html .',
'LGPL users may replace the bundled dynamic libraries with compatible modified versions; no restriction on debugging those modifications is imposed by JARVIS. Corresponding upstream sources: https://download.qt.io/official_releases/QtForPython/ and https://download.qt.io/official_releases/qt/ .',
'Python: https://www.python.org/psf/license/ . Vosk English model small-en-us-0.15: Apache-2.0, Copyright Alpha Cephei; https://alphacephei.com/vosk/models .',
'Ollama and Qwen3 are downloaded separately, not embedded in this installer. Ollama: MIT, https://github.com/ollama/ollama . Qwen3 0.6B: Apache-2.0, https://ollama.com/library/qwen3:0.6b .',
'Playwright Chromium is downloaded separately through the official Playwright installer. See its bundled notices after installation.','']
for dist in sorted(metadata.distributions(),key=lambda d:d.metadata['Name'].lower()):
    name=dist.metadata['Name'];license_name=dist.metadata.get('License-Expression') or dist.metadata.get('License') or 'See bundled license / upstream'
    lines.append(f'{name} {dist.version}: {license_name.splitlines()[0]}')
    for item in dist.files or []:
        if any(part.lower() in ('licenses','license') for part in item.parts) or item.name.lower().startswith(('license','copying','notice')):
            source=Path(dist.locate_file(item))
            if source.is_file():
                target=root/name/str(item).replace('..','_');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
Path('docs/THIRD-PARTY-NOTICES.txt').write_text('\n'.join(lines),encoding='utf-8')
print('Copied dependency notices and license texts.')

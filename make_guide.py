"""Build the offline guide from one concise source of verified product behavior."""
from pathlib import Path
import html
import shutil
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

chapters=[
('Introduction','Chat',[
'JARVIS 0.1 is a local Windows assistant with text conversation, explicit safe tool commands, reusable CSV/Excel workflows, local memory, reminders and optional speech. It uses a shared Ollama service and Qwen3 0.6B by default. No subscription or API key is required.',
'This is an initial usable release, not the complete autonomous system in the master specification. General chat does not execute actions. Use the documented commands and review controls. The small model can be wrong; verify its advice. Browser teaching is limited to public navigation, and the limits chapter identifies unfinished features.']),
('Installation and first launch',None,[
'Run JARVIS-Setup-x64.exe. It installs for the current Windows user, creates shortcuts, and registers an uninstaller without requiring a separate Python installation. The installer contains the application, speech model and guide. It does not contain your conversations, credentials or recordings.',
'Open JARVIS from the desktop or Start menu. Read or skip the welcome guide. In Settings, choose Set up local AI automatically to install Ollama through the official Windows package manager when needed and download Qwen3 0.6B. This requires internet access and Windows App Installer (winget). Existing Ollama installations and models are reused. Setup failure is shown rather than hidden.',
'For public browser reading and observation, choose Install browser runtime in Settings. This downloads Playwright Chromium for your Windows user. These first-run downloads are not an offline installer. Once AI and speech assets are available, conversation, file tools, skills and reminders work offline.']),
('Text chat','Chat',[
'Choose New conversation, type a message, and click Send or press Ctrl+Enter. Replies stream into the current conversation. Stop reply cancels the current response. You can switch conversations while one is generating; the shared inference lock serializes model work.',
'Use the left search box to find conversations. Rename changes the title; Archive removes a chat from the active list. This version has no archive recovery screen. Delete permanently removes the conversation from active storage. Message editing and retry are not yet included.',
'Attach file or drop a document onto JARVIS. You are asked to authorize its containing folder; the app then reads the file through the same permission policy as /read. Supported formats are text, Markdown, JSON, CSV, XLSX, DOCX and PDF. Extraction is size-bounded. Scanned PDFs need OCR, which is not implemented. Attachments are read locally; there is no automatic whole-disk indexing.']),
('Voice',None,[
'Push to talk explicitly activates the microphone for up to 12 seconds. The status line indicates microphone activity. Recognition uses the included small English Vosk model and releases the model/device afterward. The text appears in the input box: review it and click Send. Speech does not bypass text-command permissions.',
'Settings → Detect audio devices lets you choose a microphone. System default is the initial setting. Speak last reply uses Windows SAPI voices. Stop all requests cancellation. No wake word, continuous listening, global push-to-talk shortcut, voice selector or speed control is implemented.',
'A prerecorded SAPI-generated sample was transcribed correctly during development. That does not verify your microphone, room acoustics, accent, speakers or live speech accuracy.']),
('Floating assistant','Bubble',[
'Settings → Show floating assistant displays the small J button. Its menu opens the main app, accepts a quick message, starts push to talk, opens Skills or Watch & Learn, pauses/resumes the queue, stops work or hides the bubble.',
'Drag the bubble using its outer border. Its position is saved, and it snaps near screen edges. Settings controls opacity. The bubble shares the same models and workers. Automatic fullscreen hiding and a persistent expanded chat panel are not implemented.']),
('Windows tools',None,[
'Use /time for local time, /system for actual system statistics, /find *.csv for workspace filenames, /read followed by an approved path for document text, and /note followed by text to create a new note. “Open Notepad” requires explicit confirmation because it opens a foreground application.',
'The structured form is /tool TOOL_NAME followed by a JSON object. Available tools are time, system_info, find_files, read_document, write_note, copy_file, make_directory, open_notepad, network_check and powershell_diagnostic. For example: /tool copy_file {"source":"input.csv","destination":"copy.csv"}. Fixed PowerShell diagnostics accept processes, disks or os; arbitrary commands are rejected.',
'Settings authorizes folders. Paths outside the workspace or approved roots are denied. Reparse points, network/device paths and alternate data streams are rejected. Existing files are not overwritten. A background workflow cannot move your pointer, type globally or modify the clipboard. Destructive shell operations are unavailable.']),
('Teaching a workflow','Skills',[
'Open Skills → New. Give the workflow a name and description. Learn from input + expected CSV compares two files and proposes only transformations it can reproduce exactly. Supported inference is deliberately narrow: unchanged columns/row count with unambiguous trimming and case changes. Unknown formats and ambiguous transformations raise an error; no Sesolos format is assumed.',
'You may edit the validated JSON directly. The schema contains schema_version: 1, steps and formula_policy. Supported operations are select, rename, strip, upper, lower, drop_blank, drop_duplicates and sort. Column-based steps use a columns list; rename uses a mapping object. Sorting may use descending: true. CSV formulas are escaped by default; formula_policy: reject refuses risky values.',
'Test draft on files chooses an exact input and new output and asks approval. Inspect the result before Save version. Saved drafts start disabled in the interface. Review / enable approves the saved definition. Natural-language generation of scripts, Python/PowerShell script imports and learning arbitrary Excel formulas are not implemented.']),
('Watch & Learn','Watch-Learn',[
'Enter a public URL and choose Start observation. Confirm the scope. JARVIS opens a separate visible Chromium window and records navigation plus generic click metadata in that session only. It does not inspect your existing tabs or entire desktop. Website scripts, forms, submissions and account sessions are blocked.',
'Pause stops event capture; Resume restarts it; Stop immediately gates capture while browser cleanup finishes. Add instruction associates your typed explanation with the recording. Do not enter secrets in annotations. Review navigation draft shows editable JSON with executable navigation steps and unsupported click notes.',
'Export draft saves a local JSON file. Run reviewed navigation asks permission before background public-page fetches. It accepts navigate/read/extract actions only. It cannot replay clicks, authenticate, upload files or learn arbitrary application operations. Delete recording removes locally captured events.']),
('Running and managing skills',None,[
'Select an enabled skill and click Run saved skill. Choose the input CSV or XLSX and a new output path, then approve the exact operation. Work runs in a single background queue and preserves the original. XLSX processing uses the first sheet; it does not preserve workbook formatting or formulas as a general Excel editor.',
'Automations shows job status, result, output path and errors. Cancel selected job is cooperative. A job that has already published its output remains completed. Queue pause affects waiting jobs; use cancellation for running work.',
'Save version retains prior definitions. Version history restores an earlier definition as a new disabled version. Export and Import transfer only the declarative skill package; imported skills require review before enabling. Deleting a skill removes its version history.']),
('Scheduling','Automations',[
'Add reminder accepts local date/time and once, hourly, daily or weekly repetition. /remind 10 Take a break schedules a reminder ten minutes from now. Reminders persist across restart; missed recurring reminders coalesce into one occurrence.',
'JARVIS must be running for delivery. Enable Start JARVIS at Windows sign-in if desired. A tray notification and status message show due reminders. Delete reminder removes a schedule. This version does not yet schedule file workflows or monitor folders.']),
('Memory','Memory',[
'Save facts explicitly with /remember, or use Add memory. Search, edit and delete them in Memory. /memories lists saved facts; /forget followed by an ID removes one. Settings can disable use of saved memories during conversation.',
'Conversations and memories live in local SQLite databases under the selected profile. They are not encrypted by JARVIS and are protected by your Windows account/filesystem permissions. Never store passwords, authentication tokens or payment details. Deletion removes active records; backups and filesystem recovery may retain older data.',
'Export memories writes JSON. Backup conversation database creates an SQLite snapshot of chat/settings/memory only. Export skills separately. A complete profile backup/restore interface is not yet implemented.']),
('Models and performance','Settings',[
'Settings → Discover lists actual Ollama models. Select a model and Use to change it. Install selected model explicitly downloads it; Remove selected model removes the shared Ollama model and may affect other applications. Unload model releases its loaded instance. Benchmark local inference runs a real request.',
'Eco is the default: one workflow worker, a 2,048-token model context, 512-token maximum response and immediate unload after generation. Balanced retains the model for about one minute; Performance retains it for five minutes. All modes share one inference slot. Larger models may produce better answers but consume more memory.',
'The development machine has 16 GB RAM and an RTX 3050 4 GB GPU. Under heavy memory pressure the first 0.6B response took 77 seconds; model unloading was verified. This is not a universal latency estimate. Background monitoring is modest and no model is continuously running for observation.']),
('Browser and integrations',None,[
'Use /web followed by a public HTTP(S) URL to request a page read. Confirm the request. JARVIS validates public addresses and redirects, limits response size, then extracts content in an isolated browser with page scripts disabled. It does not reuse normal browser cookies.',
'No email, calendar, cloud inference, credential vault integration, runtime MCP server manager or third-party executable plugin loader is shipped in this version. Development tools used to build JARVIS are not runtime permissions or integrations.']),
('Security and privacy',None,[
'Permissions are enforced by Python code, not model instructions. User commands can call approved tools; documents and websites are treated as data. The model cannot execute arbitrary shell strings or scripts. Local inference connects only to 127.0.0.1:11434, with environment proxies and redirects disabled.',
'Review output paths and operation definitions before approvals. Authorization applies to this profile. Revoke folders in Settings to remove tool access. Stop all cancels chat/audio work, pauses capture and the job queue, and cancels queued/running jobs cooperatively. It does not roll back completed files or interrupt installers safely.',
'This is not an operating-system sandbox. Document parsers and declarative transformations run under your Windows account. Do not treat malformed hostile documents as harmless. No antivirus, UAC, firewall or authentication protection is bypassed.']),
('Profiles and background operation',None,[
'Settings → Switch / create profile accepts letters, digits, underscores and dashes. Profiles have separate conversations, memory, settings, permissions, skills and task history. Downloads and the Ollama backend are shared. A lock prevents two JARVIS processes from owning the same profile.',
'Closing the window hides it to the tray when available, so queued work and reminders continue. Double-click the tray icon to reopen. Quit shuts down JARVIS. Startup at sign-in is optional and records the selected profile. Different profiles do not imply separate loaded models.']),
('Updates, uninstall and distribution',None,[
'Run a newer compatible installer over the current application to replace program files. User profile data is stored separately and the uninstaller preserves it. Back up important data before upgrading. There is no automatic updater, signed release feed or rollback manager yet.',
'Uninstall through Windows Installed Apps or the Start menu uninstaller. The app does not uninstall shared Ollama models or browser assets used by other installations. The installer is unsigned; no signing certificate was purchased. A clean second-computer environment has not been certified unless the accompanying implementation report explicitly says so.',
'Share the installer and source archive, never your profile directory. First-run AI/browser setup needs internet. The app executable includes Python and Qt; development tools are not required to run it.']),
('Troubleshooting',None,[
'Connection refused: Ollama is not running. Use Set up local AI automatically. Missing model: Discover, select qwen3:0.6b and install it. Slow response: close unnecessary applications yourself, remain in Eco, and check available RAM. Stop reply remains available.',
'Browser executable missing: Install browser runtime. Page blocked: the URL may point to a private network, require scripts/login, or exceed the supported public-document scope. Microphone failure: Detect audio devices, select a usable input, and check Windows microphone permission.',
'Path denied: authorize the containing folder in Settings. Output exists: choose a new filename. Ambiguous examples: edit a deterministic workflow manually instead of guessing. Failed jobs show error details in Automations. Interrupted jobs are not silently rerun after a crash.']),
('Advanced workflow reference',None,[
'Example definition: {"schema_version":1,"steps":[{"op":"strip","columns":["Name"]},{"op":"upper","columns":["Name"]},{"op":"drop_blank","columns":["VIN"]}],"formula_policy":"escape"}. Replace Name and VIN with actual headers; this is an example, not a Sesolos specification.',
'Definitions contain no paths or executable code. Each run supplies exact input/output files. Existing outputs are rejected and results are published atomically. Source code, tests, dependency versions and API contracts accompany the release for maintenance.']),
('Command reference and release limits',None,[
'Quick commands: /help, /time, /system, /model, /mode Eco, /find *.csv, /read C:\\approved\\report.pdf, /note Meeting notes, /remember I prefer concise replies, /memories, /jobs, /skills, /teach, /watch, /run Workflow name, /remind 10 Take a break, /web https://example.com.',
'Not yet delivered: general autonomous tool planning, full Markdown editing/retry, semantic document indexing, arbitrary screen/application teaching, authenticated browser submissions, wake word and voice tuning, scheduled skill execution, folder triggers, runtime MCP/plugins, email/calendar/cloud integrations, full backup/restore, automatic updates and a fully offline AI installer. These remain requirements in the backlog, not completed functionality.'])]

out=Path('docs');out.mkdir(exist_ok=True);(out/'images').mkdir(exist_ok=True)
styles=getSampleStyleSheet();styles['BodyText'].fontSize=10;styles['BodyText'].leading=15;styles['BodyText'].spaceAfter=10
styles['Heading1'].textColor=colors.HexColor('#143d4a');styles['Heading1'].spaceAfter=14
styles['Heading2'].textColor=colors.HexColor('#143d4a')
story=[Paragraph('JARVIS',styles['Title']),Spacer(1,18),Paragraph('Local assistant • User guide',styles['Heading1']),Paragraph('Version 0.1.0 | Windows 11 | 20 November 2026',styles['BodyText']),Spacer(1,15),Paragraph('Quick start',styles['Heading2'])]
quick=['Install and open JARVIS.','Settings: Set up local AI automatically. Install browser runtime only if needed.','Ask “What time is it?” or type /help.','Authorize only the folders needed for your tasks.','Teach and test a CSV workflow, then review and enable it.','Use Eco mode. Close hides to tray; Quit stops the app.']
for step in quick:story.append(Paragraph(html.escape(step),styles['BodyText']))
story.append(Paragraph('Read the release limits before relying on unattended automation.',styles['BodyText']))
parts=['<!doctype html><html><head><meta charset="utf-8"><title>JARVIS User Guide</title><style>body{font:16px Segoe UI,Arial,sans-serif;color:#18323e;max-width:980px;margin:40px auto;padding:0 24px;line-height:1.65}h1,h2{color:#174d5d}img{max-width:100%;border:1px solid #d6e1e5}nav a{display:block}code{background:#eef4f6}p{margin:14px 0}</style></head><body><h1>JARVIS User Guide</h1><p>Version 0.1.0 • Windows 11 • 20 November 2026</p><h2>Quick start</h2><ol>']
parts += ['<li>'+html.escape(s)+'</li>' for s in quick];parts += ['</ol><nav>']
for i,(title,_,_) in enumerate(chapters,1):parts.append(f'<a href="#chapter{i}">{i}. {title}</a>')
parts.append('</nav>')
for i,(title,shot,paragraphs) in enumerate(chapters,1):
    story.extend([PageBreak(),Paragraph(f'{i}. {html.escape(title)}',styles['Heading1'])]);parts.append(f'<h2 id="chapter{i}">{i}. {html.escape(title)}</h2>')
    for text in paragraphs:story.append(Paragraph(html.escape(text),styles['BodyText']));parts.append('<p>'+html.escape(text)+'</p>')
    if shot and (Path('screenshots')/(shot+'.png')).exists():
        target=out/'images'/(shot+'.png');shutil.copy2(Path('screenshots')/(shot+'.png'),target)
        from PIL import Image as PILImage
        with PILImage.open(target) as im:w,h=im.size
        width=min(470,w);height=width*h/w
        story.extend([Spacer(1,10),Image(str(target),width=width,height=height)])
        parts.append(f'<p><img src="images/{shot}.png" alt="Actual JARVIS {html.escape(shot)} interface"></p>')
parts.append('<h2>Licenses</h2><p>See THIRD-PARTY-NOTICES.txt and the bundled licenses directory. Qt/PySide libraries remain dynamically replaceable under their applicable LGPL terms. Source accompanies this release.</p></body></html>')
(out/'User-Guide.html').write_text('\n'.join(parts),encoding='utf-8')
def footer(canvas,doc):
    canvas.setFont('Helvetica',9);canvas.setFillColor(colors.HexColor('#50717e'));canvas.drawString(45,28,'JARVIS 0.1 • Offline user guide');canvas.drawRightString(550,28,str(doc.page))
SimpleDocTemplate(str(out/'JARVIS-User-Guide.pdf'),pagesize=(595,842),rightMargin=45,leftMargin=45,topMargin=45,bottomMargin=48).build(story,onFirstPage=footer,onLaterPages=footer)
(out/'Quick-Start.txt').write_text('JARVIS 0.1 — QUICK START\n\n'+'\n'.join(f'{i}. {step}' for i,step in enumerate(quick,1))+'\n\nRead User-Guide.html or JARVIS-User-Guide.pdf for limitations.\n',encoding='utf-8')
print('Generated PDF, HTML and quick start.')

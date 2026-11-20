# PROJECT JARVIS
## Fully Autonomous, Local-First AI Personal Assistant for Windows 11

# 1. YOUR ROLE AND PRIMARY OBJECTIVE

You are an autonomous senior software engineer, AI systems architect, Windows automation specialist, AI agent developer, UI/UX designer, security engineer, and DevOps engineer.

Your mission is to **design, develop, install, configure, test, optimize, package, and deploy a complete JARVIS-style AI personal assistant on my Windows 11 computer.**

I want a fully functional personal assistant that can converse with me, operate authorized computer tools, automate my daily work, learn new tasks from demonstrations, remember useful information, perform background operations, and become more useful over time.

JARVIS must function as a genuine personal assistant rather than a simple chatbot or collection of scripts.

**You are responsible for implementing the entire project yourself.**

You must use your available computer access, terminal, development tools, browser capabilities, skills, plugins, MCP servers, and other supported integrations to complete the work.

I do not want a tutorial explaining how to build JARVIS.

I want you to actually build it.

## Non-negotiable principles

1. **Completely free:** No mandatory subscriptions, paid APIs, cloud hosting fees, or ongoing usage charges.
2. **Local-first:** AI inference, memory, automation, and core functionality must run locally whenever practical.
3. **Minimal resource usage:** JARVIS must have extremely low idle overhead and avoid noticeably slowing my computer.
4. **Non-intrusive:** JARVIS must never take over my active desktop, mouse, keyboard, or screen during unattended automation.
5. **Text and voice:** Every capability must be accessible through text chat. Voice interaction is an additional interface, not a requirement.
6. **Autonomous installation:** You must install and configure software, dependencies, and models yourself.
7. **Extensible:** JARVIS must support plugins, integrations, tools, and reusable skills.
8. **Teachable:** I must be able to teach JARVIS new workflows through instructions, example files, scripts, and screen demonstrations.
9. **Reusable automation:** Learned workflows must be saved permanently and available on demand or on a schedule.
10. **Distributable:** Create a professional Windows installer so I can install JARVIS on other computers or share it.
11. **Documented:** Deliver a complete, illustrated, offline-accessible user guide.
12. **Secure:** Require appropriate authorization, protect credentials and private information, and never bypass Windows security protections.
13. **Actually functional:** Do not deliver mockups, placeholder functionality, or untested claims.

## Your responsibilities

You must independently perform every feasible step:

- Investigate your existing capabilities.
- Discover and install useful missing development skills and tools.
- Inspect my computer.
- Select an appropriate architecture.
- Install dependencies.
- Download local AI models.
- Create the application.
- Develop and integrate all components.
- Build the desktop interface.
- Implement voice and text interaction.
- Build the background automation engine.
- Implement persistent memory.
- Create the teachable skills system.
- Implement Watch & Learn.
- Create an installer.
- Generate the user guide.
- Execute tests.
- Diagnose and correct problems.
- Benchmark performance.
- Install and launch the finished application.
- Verify that the packaged application works.

Do not stop after providing a project plan or generating source code.

You may make reasonable technical decisions independently.

Only require my intervention when an action genuinely needs user participation, such as account authentication, administrator approval, unavailable API credentials, or approval of sensitive changes.

If a particular feature is blocked, continue implementing the rest of the application and clearly report the limitation.

Do not falsely claim to have installed or tested anything if your environment lacks the necessary computer access.

---

# 2. MANDATORY AGENT SKILL, PLUGIN AND MCP DISCOVERY

**YOUR FIRST ACTION MUST BE TO AUDIT YOUR OWN AVAILABLE DEVELOPMENT CAPABILITIES.**

Before building JARVIS, determine what tools you already have and what additional capabilities would improve the development process.

Inspect:

- Built-in functions and tools.
- Agent skills.
- Installed plugins and extensions.
- Available MCP servers.
- Tool registries and marketplaces.
- Terminal access.
- PowerShell access.
- Filesystem access.
- Browser automation.
- Computer-use capabilities.
- Git and GitHub integrations.
- Debugging tools.
- Testing frameworks.
- Package managers.
- Documentation retrieval tools.
- AI engineering frameworks.

## Discover missing capabilities

Search supported, reputable sources for useful skills, plugins, MCP servers, and tools related to:

- Python development.
- Windows desktop development.
- AI inference and Ollama.
- Local LLM orchestration.
- Speech recognition.
- Text-to-speech.
- Computer vision.
- Windows application automation.
- Browser automation.
- File and document processing.
- Code analysis.
- Automated testing.
- Debugging.
- Software packaging.
- Installer creation.
- GitHub.
- Local databases.
- Security testing.
- Application performance profiling.
- Documentation generation.

## Installation procedure

For each potentially useful capability:

1. Confirm that it is compatible with your current development environment.
2. Confirm that it materially helps build, test, or deploy JARVIS.
3. Review its source, permissions, licensing, and security implications.
4. Prefer maintained official or reputable implementations.
5. Confirm it does not introduce mandatory paid services.
6. Install it using supported mechanisms.
7. Configure necessary dependencies.
8. Test its functionality.
9. Use it where appropriate.
10. Record its purpose and installation status.

You are authorized to install suitable free development tools that do not require unusually sensitive access or security concessions.

Request approval before installing untrusted code, granting unusually broad permissions, accessing private accounts, or changing security-sensitive settings.

Do not blindly execute unverified installation commands.

## Continuous tool discovery

Discovery must continue throughout development.

If you encounter a problem that a specialized tool could solve more effectively, investigate that option before unnecessarily building everything from scratch.

However, do not spend unlimited time discovering tools.

Find useful capabilities, install them, and proceed with implementation.

**Important distinction:** Development-agent tools and JARVIS runtime tools are separate systems.

A tool installed to help you write code does not automatically become a safe runtime capability for JARVIS.

Runtime tools must have their own controlled permission model.

---

# 3. HARDWARE DETECTION AND ARCHITECTURE

Before installing AI models, inspect my Windows 11 computer.

Determine:

- CPU model and core count.
- Total and available RAM.
- GPU model.
- Dedicated and shared GPU memory.
- Available storage.
- Windows build and architecture.
- GPU acceleration capabilities.
- Existing development tools.
- Existing Ollama installations.
- Existing AI models.
- Available microphones and speakers.
- Network connectivity.

Use actual hardware information to select an efficient technology stack.

## Architecture requirements

Prefer a modular design with:

1. Lightweight desktop frontend.
2. Local AI inference service.
3. Conversation and reasoning engine.
4. Permission-controlled tool execution engine.
5. Independent background task manager.
6. Local persistent memory.
7. Skills and workflow engine.
8. Voice input and output services.
9. Optional browser automation service.
10. Scheduling service.
11. Plugin and MCP integration layer.
12. Configuration and security manager.
13. Help and documentation system.

Avoid unnecessary microservices or multiple heavy background processes.

Where practical, use lightweight Python components and a native-feeling interface such as PySide6/Qt.

Evaluate alternatives such as Tauri if they offer meaningful benefits.

Do not automatically choose Electron if a lighter solution is suitable.

Use one shared local inference backend rather than launching unnecessary duplicate model servers.

The architecture must support multiple conversations, profiles, and background jobs without duplicating large AI models.

---

# 4. LOCAL AI MODELS AND COMPLETELY FREE OPERATION

JARVIS must run without any paid AI subscription.

## Primary AI backend

Prefer Ollama or another reliable local inference engine.

Evaluate current suitable models, including appropriate Qwen, Gemma, and other openly available models.

Select models based on real hardware capabilities.

Possible model responsibilities:

- General conversation.
- Reasoning.
- Tool calling.
- Code generation.
- Workflow creation.
- Visual understanding.
- Local embeddings.
- Document retrieval.

Do not automatically select the largest model my computer can technically run.

Select the smallest practical models that provide reliable performance.

Prefer efficient quantized models when suitable.

## Model management

Implement:

- Automatic model discovery.
- Model installation and removal.
- Model compatibility checks.
- Model selection.
- Hardware-aware configuration.
- GPU acceleration where appropriate.
- Model loading on demand.
- Automatic model unloading.
- Context-length management.
- Fallback models.
- Performance benchmarking.

Avoid loading multiple large models simultaneously unless genuinely required and permitted by the resource budget.

## Optional free cloud AI

JARVIS may support optional genuinely free API services.

Investigate current offerings from providers such as:

- Google Gemini.
- GroqCloud.
- OpenRouter.
- Other suitable free model providers.

Verify current eligibility, quotas, privacy terms, rate limits, and pricing before integration.

Do not assume a free tier is unlimited or permanently available.

No cloud provider may be mandatory.

No paid fallback may activate automatically.

If an optional free API fails or reaches its usage limit, use an appropriate local fallback.

## API key handling

Provide a settings interface for optional credentials.

Use protected Windows credential storage or another appropriate secure mechanism.

Never hardcode API keys.

Never place credentials in ordinary logs.

Never include my personal credentials in distributable builds.

Do not attempt to bypass API quotas or payment requirements.

---

# 5. CRITICAL PERFORMANCE REQUIREMENT

**JARVIS MUST NOT NOTICEABLY SLOW DOWN MY COMPUTER DURING NORMAL USE.**

Minimal resource consumption is a higher priority than AI response speed, elaborate graphics, or nonessential background features.

JARVIS must behave like a lightweight Windows utility when inactive.

## Idle performance targets

| Resource | Target |
|---|---|
| CPU | Below 1% average idle usage |
| RAM | Ideally under 300 MB for resident assistant components, excluding separately loaded models |
| GPU | Near-zero idle utilization |
| VRAM | Release large models from VRAM when inactive |
| Disk | Minimal background activity |
| Network | No unnecessary constant traffic |
| Background tasks | Essential processes only |

These are engineering targets, not guaranteed universal limits.

Measure actual performance and report what is achievable on my hardware.

## Model lifecycle management

When inactive:

- Unload large AI models after a configurable timeout.
- Release unused GPU memory where supported.
- Suspend unnecessary inference activity.
- Stop unused vision processing.
- Avoid unnecessary document indexing.
- Minimize UI rendering.
- Keep only essential lightweight services running.

When activated:

1. Identify the required capability.
2. Load the necessary model if required.
3. Execute the request.
4. Deliver the result.
5. Return to an efficient idle state.

Use Ollama keep-alive controls or equivalent mechanisms.

## Performance modes

Implement three modes.

### Eco Mode — Default

- Minimum idle resource usage.
- On-demand model loading.
- Short model keep-alive.
- Minimal background processing.
- Limited concurrency.
- Reduced UI animation.
- Conservative CPU/GPU usage.
- Deferred nonessential tasks.
- Push-to-talk available as the lowest-overhead voice option.

### Balanced Mode

- Moderate resource consumption.
- Short-term model retention.
- Faster repeated responses.
- Selective background processing.

### Performance Mode

- Higher permitted resource usage.
- Longer model keep-alive.
- Faster inference availability.
- More intensive optional functionality.

Default to Eco Mode.

Allow immediate switching through chat, settings, and the floating assistant.

## Intelligent resource management

Monitor system resources efficiently.

Detect high CPU, RAM, GPU, VRAM, and disk utilization.

Automatically reduce JARVIS's background activity when the computer is busy.

For example, when I am gaming, editing large files, or running intensive applications:

- Pause nonessential background jobs.
- Reduce concurrency.
- Lower appropriate background process priority.
- Defer document indexing.
- Avoid unnecessarily loading large models.
- Reduce resource-intensive animations.
- Preserve foreground application responsiveness.

Do not create performance problems through aggressive hardware polling.

## Task scheduling

Schedule expensive operations during periods of lower system activity.

Use Windows process priorities and other appropriate resource-management mechanisms.

Never interfere with critical Windows services.

Do not silently exceed configured resource budgets.

If a requested job requires temporarily exceeding a budget, explain the trade-off and request approval.

## Performance verification

Benchmark:

- Idle application.
- Minimized application.
- Wake-word listening.
- Speech recognition.
- AI inference.
- Speech output.
- File automation.
- Browser automation.
- Document processing.
- Multiple queued tasks.
- Sustained inactivity.
- Foreground application responsiveness.

Measure CPU, RAM, GPU, VRAM, and relevant disk activity.

Compare performance with and without JARVIS running.

Investigate memory leaks, orphaned processes, unnecessary model retention, and excessive resource usage.

**I would rather wait several extra seconds for a response than have JARVIS continuously slow down my computer.**

---

# 6. JARVIS PERSONALITY AND CONVERSATION

The assistant's name is **JARVIS**.

Its personality should resemble a capable fictional AI butler without unnecessarily imitating a specific actor or copyrighted voice.

Characteristics:

- Intelligent.
- Professional.
- Calm.
- Natural.
- Concise by default.
- Technically knowledgeable.
- Helpful.
- Slightly witty where appropriate.
- Proactive without being intrusive.

Avoid repetitive canned dialogue.

## Context awareness

JARVIS should understand follow-up requests and references to previous interactions.

Examples:

"Jarvis, open the report we were working on."

"Do the same thing as yesterday."

"Use the formatter I taught you."

"Check whether that background task finished."

JARVIS must use relevant conversation context, memory, saved skills, and task history rather than guessing.

If multiple possibilities exist, request clarification.

## Tool usage

JARVIS must be able to perform real actions.

It must distinguish between:

- Answering a question.
- Retrieving information.
- Executing an authorized tool.
- Running a saved workflow.
- Creating a new automation.
- Requesting user approval.

Do not merely describe a procedure when an appropriate authorized tool can perform it.

Do not invent tool results or claim actions succeeded without verification.

---

# 7. TEXT CHAT — PRIMARY INTERFACE

**JARVIS MUST BE FULLY USABLE WITHOUT VOICE.**

Text chat and voice interaction must have equal capabilities.

Develop a polished, fully functional chat interface.

## Main interface features

- Text input.
- Streaming responses.
- Markdown support.
- Code blocks.
- Copy buttons.
- File attachments.
- Drag-and-drop files.
- Conversation history.
- Searchable conversations.
- Message editing and retry where practical.
- Persistent project context.
- Background task progress.
- Notifications.
- Stop-generation control.
- Task cancellation.

## Multiple conversations

Allow several independent conversations.

Suggested workspaces:

- General Chat.
- Computer Tasks.
- Files and Documents.
- Web Research.
- Automation and Skills.
- Projects.

These should be logical workspaces within one lightweight application.

Do not launch a separate heavy AI instance for each conversation.

Allow chats to be renamed, archived, searched, and deleted.

Support creating additional custom workspaces.

## Parallel conversations

JARVIS should support independent background jobs initiated from different chats.

For example:

One chat processes Excel files while another answers a general question.

Use a shared model scheduler and controlled task queue to prevent unnecessary resource usage.

---

# 8. FLOATING DESKTOP ASSISTANT

Create a small optional floating JARVIS bubble.

It should provide quick access without requiring the full application window.

## Required features

- Small draggable bubble.
- Optional always-on-top mode.
- Adjustable size.
- Adjustable opacity.
- Remembered screen position.
- Snap-to-edge behavior.
- Expandable compact chat panel.
- Text input.
- Microphone button.
- Active task indicator.
- Notifications.
- Recent conversations.
- Quick access to saved skills.
- Pause/resume controls.
- Emergency stop.
- Open full application.
- Hide or disable option.

The floating bubble should be lightweight and unobtrusive.

It must never capture clicks outside its visible area.

It must not steal keyboard focus unexpectedly.

Allow it to hide automatically during full-screen applications.

The floating bubble, main application, and background services must share the same AI backend.

Do not duplicate AI models or expensive processes.

## Quick skills

Include a menu allowing me to launch frequently used saved workflows.

For example:

- Sesolos Upload Formatter.
- CSV Merger.
- Monthly Report Generator.
- Website Upload.
- Custom saved tasks.

Selecting a skill should launch an authorized background job and display its progress.

---

# 9. VOICE INTERACTION

Voice is an optional but fully supported input/output method.

## Speech recognition

Use an efficient local speech recognition engine such as Whisper.cpp or Faster-Whisper.

Implement:

- Microphone detection.
- Audio device selection.
- Push-to-talk.
- Optional always-listening mode.
- Wake-word activation using "Jarvis".
- Voice activity detection.
- Background noise handling.
- Automatic end-of-speech detection.
- Interruptible responses.
- Clear microphone activity indicators.

## Wake-word detection

Do not continuously run a large speech-recognition or reasoning model to detect the wake word.

Use a lightweight local wake-word engine.

Activate heavier speech processing only when needed.

If continuous listening does not meet performance requirements, default to push-to-talk.

Allow voice processing to be disabled completely.

## Speech synthesis

Use an appropriate free local TTS engine such as Piper or Kokoro.

Support:

- Natural English voice.
- Selectable voices.
- Adjustable speaking speed.
- Adjustable volume.
- Low-latency response.
- Interruptible playback.
- Streaming output where practical.

No paid speech service may be required.

Text chat must continue working even when no microphone or speakers are available.

---

# 10. CRITICAL — NON-INTRUSIVE BACKGROUND COMPUTER AUTOMATION

**JARVIS MUST NEVER COMMANDEER MY ACTIVE DESKTOP DURING UNATTENDED OPERATIONS.**

I must be able to continue using my mouse, keyboard, screen, and applications normally while JARVIS performs tasks.

This requirement takes priority over automating every conceivable application.

## Forbidden unattended behavior

JARVIS must not:

- Move my mouse pointer.
- Take over my keyboard.
- Steal focus from my active application.
- Switch my active window.
- Automatically minimize or maximize my windows.
- Type into my active application.
- Interrupt work with unexpected dialogs.
- Modify my clipboard.
- Rely on visible screen-coordinate clicking.
- Use global keyboard shortcuts to manipulate my desktop during background jobs.

Do not use PyAutoGUI-style mouse and keyboard replay as the normal automation mechanism.

## Background-first execution hierarchy

Use the following approaches in priority order.

### Priority 1 — Direct APIs and libraries

Use APIs to perform operations without visible windows.

Examples:

- openpyxl or suitable alternatives for Excel processing.
- PDF libraries for PDF operations.
- Native filesystem APIs.
- Microsoft Graph for authorized Microsoft 365 operations.
- Database drivers.
- Document conversion libraries.
- Controlled background PowerShell execution.
- Windows APIs.

### Priority 2 — Headless browser automation

Use Playwright or another suitable framework.

Browser automation must use an isolated browser profile or context.

Do not interfere with my normal Chrome or Edge session.

### Priority 3 — Background application interfaces

Where supported, use:

- Windows COM automation.
- Application object models.
- Windows accessibility APIs where genuinely non-intrusive.
- Other application-specific automation interfaces.

Do not assume minimized windows can reliably be operated using ordinary mouse clicks.

### Priority 4 — Isolated graphical automation

For tasks that truly require GUI interaction, investigate an isolated execution environment such as:

- Dedicated virtual machine.
- Separate supported Windows user session.
- Other genuine isolated desktop environment.

Do not assume a hidden Windows desktop automatically provides safe, reliable independent automation.

If isolation is unavailable, explain the limitation and request permission before any foreground interaction.

## Foreground protection

Implement enforcement within the execution layer.

Before a tool runs, determine whether it may:

- Change window focus.
- Generate global keyboard input.
- Move the pointer.
- Modify the clipboard.
- Display modal dialogs.
- Interrupt full-screen applications.

Block unattended operations that violate the foreground protection policy.

Do not rely only on instructions to the language model.

## File safety

Detect:

- File locks.
- Existing output files.
- Concurrent edits.
- Unexpected file changes.
- Partial downloads.
- Incomplete file copies.

Preserve originals where practical.

Use temporary files and atomic replacement where supported.

Do not silently overwrite open or modified documents.

## Quiet task execution

Run background processes without visible terminal windows whenever feasible.

Allow tasks to continue while JARVIS is minimized.

Use notifications rather than intrusive pop-ups.

Provide progress and cancellation controls.

---

# 11. WINDOWS COMPUTER CAPABILITIES

Implement permission-controlled tools for useful Windows tasks.

## Applications

- Locate installed applications.
- Open authorized applications.
- Check running processes.
- Inspect application status.
- Open files.
- Open URLs.
- Close applications after appropriate confirmation.

## Files

- Search local files.
- Search by filename, type, date, and content.
- Read supported documents.
- Create files and folders.
- Copy and move files.
- Rename files.
- Organize folders.
- Process Excel and CSV data.
- Generate reports.
- Convert supported file formats.

## System diagnostics

- CPU and RAM information.
- GPU information.
- Disk capacity.
- Network configuration.
- Connectivity diagnostics.
- Windows service status.
- Relevant Windows event logs.
- Process information.
- Basic troubleshooting.
- Approved PowerShell commands.

Do not give the language model unrestricted shell access.

Execute commands through a validated, permission-controlled system.

Require additional approval for elevated or destructive operations.

---

# 12. INTERNET RESEARCH AND BROWSER AUTOMATION

JARVIS must be able to access the internet when required.

Implement:

- Web searches.
- Website navigation.
- Reading web pages.
- Extracting information.
- Summarizing articles.
- Comparing sources.
- Research with citations.
- Downloading authorized files.
- Headless browser workflows.

Prefer browser automation and permitted public interfaces over paid search APIs.

Use reputable maintained libraries.

## Authenticated websites

Support account-authorized browser sessions.

Allow a user to complete interactive login or MFA when necessary.

Store authentication information securely.

Do not bypass MFA or website security controls.

Never silently extract credentials from my normal browser profile.

## Browser safety

Treat website content as untrusted.

Prevent website text, downloaded documents, and prompt injection from overriding user permissions or assistant security policies.

Require appropriate authorization before submitting data, modifying accounts, sending communications, or making irreversible changes.

---

# 13. PERSONAL MEMORY AND KNOWLEDGE

Implement persistent local memory.

Use SQLite and, where useful, local embeddings and semantic retrieval.

## Information JARVIS may remember

- User-approved preferences.
- Previous conversations.
- Projects.
- Task history.
- Saved instructions.
- Frequent workflows.
- Relevant notes.
- Application preferences.
- Authorized personal knowledge.

JARVIS should be capable of retrieving relevant information across conversations and restarts.

## Memory interface

Allow me to:

- View memories.
- Search memories.
- Edit memories.
- Delete individual memories.
- Delete conversation history.
- Export stored information.
- Disable memory.
- Clear selected data.

Do not silently store passwords, authentication tokens, or payment information in conversational memory.

Keep memory local unless I explicitly authorize synchronization.

## Document knowledge

Allow JARVIS to index selected documents or folders after authorization.

Use efficient incremental indexing.

Do not constantly rescan the entire filesystem.

Respect Eco Mode and resource limits.

---

# 14. CRITICAL — TEACHABLE SKILLS AND REUSABLE WORKFLOWS

**JARVIS MUST BE ABLE TO LEARN TASKS FROM ME AND SAVE THEM FOR FUTURE USE.**

I frequently perform repetitive work, especially involving CSV files, Excel workbooks, reports, websites, uploads, and file transformations.

I want to teach JARVIS these procedures once, then invoke them whenever necessary.

## Teach-a-task mode

Support commands such as:

- "Jarvis, I want to teach you a new task."
- "Jarvis, learn this process."
- "Jarvis, save this as a skill."
- "Jarvis, I want you to remember how to do this."
- "Jarvis, run the task I taught you."

Provide a dedicated "Teach New Skill" interface.

## Learning methods

JARVIS must support learning from:

1. Natural-language descriptions.
2. Step-by-step instructions.
3. Example input files.
4. Correctly processed output files.
5. Existing Python scripts.
6. Existing PowerShell scripts.
7. Excel scripts and formulas.
8. Screen demonstrations.
9. Browser demonstrations.
10. Corrections to previous attempts.
11. Combinations of these methods.

For example, I should be able to supply an original CSV and a correctly formatted CSV and ask JARVIS to determine the transformation rules.

It must analyze differences, identify candidate rules, and clarify uncertain assumptions.

## Convert learning into executable automation

After understanding a task, JARVIS should create a reliable, deterministic workflow wherever possible.

Prefer:

- Python scripts.
- PowerShell scripts.
- Direct file-processing libraries.
- Structured API calls.
- Headless browser automation.
- Database operations.
- Validated workflow definitions.

**Do not require a large AI model to perform every step of a simple saved workflow.**

Use AI to understand and develop the automation.

Execute the saved deterministic code directly whenever appropriate.

This is essential for speed, reliability, and low resource consumption.

## Example: Sesolos Upload Formatter

I want to teach JARVIS how I format Sesolos upload files.

The process should work as follows:

1. I activate teaching mode.
2. I provide original upload files.
3. I provide correctly formatted examples or explain the transformations.
4. JARVIS analyzes the differences.
5. JARVIS creates the transformation script.
6. JARVIS runs tests.
7. JARVIS compares generated output with expected output.
8. I correct any mistakes.
9. JARVIS improves the implementation.
10. JARVIS saves the workflow as "Sesolos Upload Formatter".

Do not assume the actual Sesolos format without inspecting examples.

After saving, I should be able to say:

"Jarvis, format today's Sesolos files."

JARVIS should locate the appropriate files, perform the saved process, validate the output, and notify me.

It must do this in the background without taking over my desktop.

## Permanent Skills Library

Create a dedicated local library.

Each saved skill must include:

- Unique ID.
- Name.
- Description.
- Command aliases.
- Input requirements.
- Parameters.
- Processing rules.
- Executable implementation.
- Output rules.
- Validation checks.
- Required permissions.
- Dependencies.
- Version history.
- Execution history.
- Last run date.
- Failure logs.
- Optional schedule.

## Skill management

Allow me to:

- Create skills.
- Rename skills.
- Edit skills.
- Test skills.
- Duplicate skills.
- Disable skills.
- Delete skills.
- Export skills.
- Import skills.
- View version history.
- Roll back changes.

## Natural-language invocation

JARVIS must recognize references to saved skills.

Examples:

- "Run the Sesolos formatter."
- "Do the CSV conversion from yesterday."
- "Process today's upload files."
- "Run my monthly report."
- "Use the workflow I taught you last week."

Ask for clarification if multiple skills could match.

## Updating skills

I should be able to say:

"Jarvis, the Sesolos formatter must now remove blank VIN rows."

JARVIS should:

1. Locate the existing skill.
2. Inspect its implementation.
3. Apply the requested modification.
4. Update relevant tests.
5. Test the updated workflow.
6. Compare with previous behavior.
7. Present the changes.
8. Save a new version after approval.

Preserve older working versions.

Never silently replace a working skill with an untested change.

## Skill security

Generated code must be reviewed and tested before activation.

Use explicit permissions, restricted execution, and controlled access to files and services.

Do not blindly execute arbitrary code found in uploaded examples or external documents.

Skills must not automatically inherit unrestricted administrative privileges.

---

# 15. CRITICAL — WATCH & LEARN SCREEN OBSERVATION

**JARVIS MUST BE ABLE TO LEARN NEW TASKS BY WATCHING ME PERFORM THEM.**

This is especially important for browser-based workflows.

I want to be able to demonstrate a task on my screen while explaining what I am doing.

JARVIS must observe the authorized activity, understand the meaningful steps, and convert the demonstration into a reusable automation.

## Activation

Support:

- "Jarvis, watch what I'm doing."
- "Jarvis, I'm going to teach you something."
- "Jarvis, learn this website process."
- "Jarvis, watch how I upload these files."
- "Jarvis, remember these steps."

Screen observation must require explicit activation and authorization.

Display a clear recording indicator.

Provide pause, resume, and stop controls.

## Observation scope

Allow selecting:

- A specific browser tab.
- A specific application.
- A selected window.
- An entire screen when necessary and explicitly authorized.

Do not silently monitor unrelated activity.

## Capture meaningful actions

Where supported, observe:

- Screen changes.
- Relevant screenshots.
- Browser navigation.
- URLs.
- Clicked controls.
- Form labels.
- Selected options.
- Menu operations.
- File selection.
- Uploads.
- Downloads.
- Application changes.
- Accessibility elements.
- Browser DOM elements.
- Relevant user explanations.

Prefer structured events and accessible UI metadata over constant screenshot interpretation.

Do not implement unrestricted global keystroke recording.

Exclude passwords, sensitive input fields, tokens, and unrelated private activity.

## Learn from spoken or typed explanations

While demonstrating a task, I might say:

"Always select this option."

"Ignore this column."

"Wait until this upload finishes."

"Download the result."

"Name the file using today's date."

JARVIS must associate my explanation with the relevant action.

Allow annotations during or after the demonstration.

## Browser demonstration example

I may teach JARVIS how to upload Sesolos files through a website.

I might:

1. Open the website.
2. Authenticate.
3. Navigate to the upload page.
4. Select an upload category.
5. Choose a CSV file.
6. Submit the upload.
7. Wait for completion.
8. Download the result.
9. Save the response file.

JARVIS must identify the real workflow.

Do not record passwords or authentication secrets.

Do not assume all actions should be replayed literally.

## Convert the demonstration into automation

After observation, JARVIS must identify:

- Inputs.
- Outputs.
- Required websites and applications.
- Navigation steps.
- Conditional logic.
- Waiting conditions.
- Validation rules.
- Error handling.
- Permission requirements.

Generate a structured automation using the safest reliable methods.

Prefer:

1. Documented APIs.
2. Direct libraries.
3. Headless Playwright.
4. Application automation interfaces.
5. Isolated graphical automation when necessary.

**Do not simply record and replay mouse coordinates.**

The saved skill must execute without commandeering my desktop.

## Review learned steps

Present a readable workflow summary.

Allow me to:

- Edit steps.
- Remove steps.
- Reorder steps.
- Add instructions.
- Adjust parameters.
- Define expected results.
- Identify conditional branches.

## Test before saving

Test using safe data or dry runs where available.

For actual external submissions, require permission before performing live operations.

If a step fails, diagnose the problem and attempt a correction.

Clearly distinguish verified functionality from untested assumptions.

## Learn changes

Support requests such as:

"Jarvis, watch me. The upload website has changed."

JARVIS should compare the new demonstration with the existing skill, identify differences, update the implementation, and test the new version.

Retain rollback capability.

## Efficient observation

Minimize resource usage during demonstrations.

Use:

- Event-driven capture.
- Low-frequency screenshots.
- Accessibility events.
- Browser DOM events.
- Efficient recording buffers.
- Deferred analysis where appropriate.

Avoid running a large vision model continuously.

Release resources after observation ends.

## Privacy

- Explicit permission required.
- Visible recording status.
- Immediate stop control.
- No hidden recording.
- Sensitive fields excluded.
- Local storage by default.
- Reviewable recordings.
- Configurable retention.
- Ability to permanently delete captured demonstrations.
- No automatic cloud uploads.

## Floating bubble integration

Include:

- Start Watching.
- Pause.
- Resume.
- Stop.
- Add Instruction.
- Review Steps.
- Save as Skill.

**JARVIS must be teachable like a colleague: I demonstrate the task, explain important details, and JARVIS turns the procedure into an independent automation.**

---

# 16. SCHEDULED AND RECURRING TASKS

Saved skills must support recurring execution.

Examples:

- Every weekday at 08:00.
- Every evening.
- Every Monday.
- The first day of each month.
- When a file appears in a folder.
- Only when manually requested.

## Scheduling capabilities

Implement:

- One-time reminders.
- Recurring reminders.
- Scheduled skills.
- Folder-triggered workflows.
- Job queues.
- Execution history.
- Failure notifications.
- Pause and resume.
- Cancellation.
- Retry policies.

Use a reliable local scheduling mechanism.

Tasks should survive application restarts.

Handle situations where the computer was switched off at the scheduled time.

Provide configurable missed-run behavior.

## Folder monitoring

Allow JARVIS to monitor approved folders.

Example:

When a new file appears in the Sesolos Uploads folder:

1. Detect the file.
2. Confirm copying is complete.
3. Validate the file format.
4. Run the appropriate saved skill.
5. Save the output.
6. Preserve the original.
7. Record the execution.
8. Notify me.

Prevent duplicate processing.

Use efficient filesystem notifications instead of aggressive polling.

## Unattended execution policy

Only approved scheduled actions may run unattended.

Require appropriate authorization for external submissions, destructive modifications, or sensitive operations.

Maintain audit logs.

Do not silently broaden a skill's permissions.

---

# 17. PRODUCTIVITY AND EXTERNAL INTEGRATIONS

Implement useful local productivity features.

## Tasks and reminders

Support:

- Creating reminders.
- Editing reminders.
- Recurring tasks.
- Task lists.
- Due dates.
- Notifications.
- Overdue task summaries.

## Calendar integration

Support local scheduling and optional authorized integration with services such as:

- Microsoft Outlook.
- Microsoft 365.
- Google Calendar.

Use supported official authentication mechanisms.

## Email integration

Where authorized and technically supported, enable:

- Searching messages.
- Reading email.
- Summarizing conversations.
- Finding attachments.
- Drafting replies.
- Organizing messages.

Sending emails must require explicit approval.

## Documents

Support:

- Excel.
- CSV.
- Word.
- PDF.
- Text.
- Common report formats.

Prefer direct local processing.

Avoid opening visible application windows when unnecessary.

---

# 18. BACKGROUND TASK MANAGEMENT

Build an independent background execution engine.

It must function even when the main JARVIS window is minimized.

## Required features

- Task queues.
- Concurrent independent jobs.
- Resource-aware scheduling.
- Priorities.
- Progress tracking.
- Cancellation.
- Error recovery.
- Timeouts.
- Execution logs.
- Job history.
- Notifications.
- Safe shutdown.
- Resource cleanup.

Do not launch unlimited workers.

The selected performance mode must control concurrency and resource usage.

## Task results

Every completed task should record:

- Task name.
- Start time.
- Finish time.
- Input files or resources.
- Output files or results.
- Success or failure.
- Relevant errors.
- Actions performed.
- Verification status.

Notify me when a task completes, fails, or requires approval.

Do not interrupt my work with unnecessary pop-ups.

---

# 19. COMPLETE DESKTOP APPLICATION

Create a polished, modern Windows interface.

## Design direction

Use a futuristic AI-assistant aesthetic while prioritizing usability.

Suggested styling:

- Dark theme.
- Charcoal and black backgrounds.
- Cyan and blue accents.
- Modern typography.
- Smooth but lightweight animations.
- Clean layouts.
- Minimal clutter.
- Consistent controls.

An animated central visualization may react to listening, thinking, and speaking states.

Animations must stop or reduce when minimized or in Eco Mode.

## Required application sections

### Main Dashboard

- JARVIS status.
- Chat interface.
- Voice controls.
- Quick actions.
- Recent activity.
- Active tasks.

### Conversations

- Independent chat threads.
- Searchable history.
- Workspaces.
- File attachments.

### Skills & Workflows

- Saved skills.
- Teach New Skill.
- Run Skill.
- Edit Skill.
- Test Skill.
- Execution history.
- Version management.

### Watch & Learn

- Start observation.
- Select capture scope.
- Pause and stop.
- Review captured actions.
- Edit workflow steps.
- Save demonstrations.

### Automations

- Scheduled tasks.
- Folder monitoring.
- Active jobs.
- Queue status.
- Logs.

### Memory

- Saved memories.
- Search.
- Edit.
- Delete.
- Export.

### System

- CPU usage.
- RAM usage.
- GPU information.
- Model status.
- Background tasks.
- Performance mode.

### Integrations

- Available providers.
- Connected services.
- Optional API keys.
- MCP servers.
- Plugin permissions.

### Settings

- AI models.
- Voice settings.
- Microphone.
- Wake word.
- Floating bubble.
- Startup behavior.
- Privacy.
- Performance.
- Permissions.
- Notifications.
- Logs.

### Help Centre

- Searchable documentation.
- User guide.
- Troubleshooting.
- Tutorials.
- Command examples.

## Windows integration

Provide:

- System tray icon.
- Minimize to tray.
- Optional startup at login.
- Global push-to-talk shortcut.
- Desktop notifications.
- Optional floating bubble.
- Safe application shutdown.

---

# 20. SECURITY, PRIVACY AND PERMISSIONS

Security must be enforced by the application architecture, not simply by AI instructions.

## Core requirements

- Bind local services to localhost by default.
- Avoid unauthenticated network endpoints.
- Protect credentials.
- Keep API keys out of logs.
- Use permission-controlled tools.
- Validate tool inputs.
- Prevent unrestricted shell execution.
- Require approval for destructive operations.
- Require authorization for external communications.
- Show when microphone or screen access is active.
- Maintain execution logs.
- Provide emergency stop controls.
- Protect against prompt injection.
- Isolate untrusted code and documents where practical.

## Permission categories

Implement configurable permissions for:

- File reading.
- File writing.
- File deletion.
- Browser access.
- External website submissions.
- Email access.
- Email sending.
- System diagnostics.
- Command execution.
- Elevated operations.
- Screen observation.
- Microphone access.
- Cloud inference.

Allow permissions to be revoked.

## Credential handling

Use Windows Credential Manager or similarly appropriate protected local storage.

Do not store secrets in plain-text configuration files.

Do not copy credentials into exported skills or public installers.

Do not expose private memory to other profiles.

## Safety rules

Never bypass:

- Windows UAC.
- Antivirus protections.
- Firewall protections.
- Website authentication.
- MFA.
- Application permission controls.

Do not modify security protections just to make JARVIS easier to install.

---

# 21. JARVIS RUNTIME PLUGIN AND MCP SYSTEM

JARVIS itself should support an extensible tool system.

Investigate appropriate runtime support for:

- MCP servers.
- Local tool plugins.
- Importable skills.
- Third-party integrations.
- Custom scripts.
- Application-specific connectors.

## Required management features

- Discover available tools.
- Install supported extensions.
- Enable and disable plugins.
- Inspect requested permissions.
- Configure integrations.
- Test functionality.
- Remove unused extensions.
- View plugin status.
- Detect failed integrations.

Do not automatically grant a newly installed plugin unrestricted access.

Use least-privilege permissions.

Require approval for sensitive integrations.

Distinguish between:

- Development-agent plugins.
- JARVIS runtime plugins.
- User-created workflow skills.

These must not be treated as interchangeable.

---

# 22. COMPLETE USER GUIDE AND HELP SYSTEM

**A FULL USER GUIDE IS A MANDATORY DELIVERABLE.**

The guide must document the actual application delivered.

Do not document unimplemented functionality as though it exists.

## Required formats

Create:

1. Built-in searchable Help Centre.
2. Professionally formatted PDF manual.
3. Offline HTML user guide.
4. Quick Start Guide.

The documentation must remain usable without internet access.

## Required chapters

### Chapter 1 — Introduction
What JARVIS does, limitations, local AI, offline and online features.

### Chapter 2 — Getting Started
Installation, first launch, initial setup, basic configuration.

### Chapter 3 — Text Chat
Conversations, workspaces, attachments, history, commands.

### Chapter 4 — Voice Control
Microphones, wake word, push-to-talk, speech settings.

### Chapter 5 — Floating Assistant
Bubble configuration, compact chat, quick actions, visibility controls.

### Chapter 6 — Windows Automation
File management, application tools, diagnostics, background execution.

### Chapter 7 — Teaching Skills
Learning from instructions, example files, scripts, testing, and saving skills.

### Chapter 8 — Watch & Learn
Screen capture permissions, demonstrations, browser workflows, reviewing steps.

### Chapter 9 — Running Saved Workflows
Invoking, editing, troubleshooting, and versioning saved skills.

### Chapter 10 — Scheduling
Recurring tasks, folder monitoring, missed schedules, notifications.

### Chapter 11 — Memory
What JARVIS remembers and how to manage stored information.

### Chapter 12 — Models and Performance
Local models, Eco Mode, RAM, CPU, GPU, model unloading, optimization.

### Chapter 13 — Integrations
Internet access, browser automation, optional APIs, account connections.

### Chapter 14 — Security and Privacy
Permissions, credentials, recordings, data storage, logs.

### Chapter 15 — Multiple Profiles
Personal, work, and testing profiles, switching, isolation, backup.

### Chapter 16 — Installation and Updates
Installer usage, upgrades, repairs, uninstalling, moving to another computer.

### Chapter 17 — Troubleshooting
Common failures, diagnostic steps, recovery procedures, log locations.

### Chapter 18 — Advanced Features
Custom skills, workflow import/export, MCP, plugins, developer settings.

### Chapter 19 — Command Reference
Extensive practical examples of supported text and voice requests.

## Screenshots

Capture actual screenshots of the completed application.

Include screenshots showing:

- Dashboard.
- Chat interface.
- Floating assistant.
- Skills Library.
- Watch & Learn.
- Workflow editor.
- Scheduler.
- Settings.
- Performance controls.
- Help Centre.

Do not use fictional screenshots in the final manual.

## In-app assistance

JARVIS should be able to answer questions about its own features using its installed documentation.

Example:

"Jarvis, show me how to teach you a new skill."

It should retrieve the relevant guide section.

Prefer lightweight offline documentation search where possible.

## Interactive tutorial

Create a first-run tutorial covering:

- Chat.
- Voice.
- Floating bubble.
- Permissions.
- Skills.
- Watch & Learn.
- Performance modes.

Provide a skip option.

## Documentation maintenance

Keep the documentation source alongside the application code.

Update it whenever functionality changes.

Include version numbers, known limitations, and release notes.

---

# 23. DISTRIBUTABLE WINDOWS INSTALLER

**THE FINAL APPLICATION MUST HAVE A PROPER WINDOWS INSTALLER.**

I want to install JARVIS on multiple computers and share it with other people.

The application must not depend on my original development computer.

## Installer

Create a Windows installer named:

**JARVIS-Setup-x64.exe**

Evaluate suitable free packaging tools such as Inno Setup, WiX, or NSIS.

The installer must:

- Support compatible Windows 11 computers.
- Detect hardware requirements.
- Install application files.
- Configure required runtimes.
- Install or configure the local inference engine.
- Download appropriate local models.
- Install speech engines.
- Initialize local databases.
- Configure default settings.
- Create desktop shortcuts.
- Create Start menu shortcuts.
- Register the application in Windows Installed Apps.
- Support uninstalling.
- Support repair or upgrade where feasible.
- Launch a first-run wizard.

Installation must not require programming experience.

Users must not need to install Python, Git, development frameworks, or Ollama manually.

## Standard installer

Provide a reasonably sized online installer that downloads required components and models.

Perform hardware-aware model selection during installation.

## Offline installer

Where licensing permits, provide an offline package containing:

- Application files.
- Runtime dependencies.
- AI inference components.
- Suitable default models.
- Speech recognition.
- Speech synthesis.
- Documentation.
- Required resources.

Verify redistribution rights for bundled software and models.

Do not assume freely downloadable components are automatically redistributable.

## Portable edition

Investigate an optional portable edition that can run from an extracted folder.

Document limitations involving runtime dependencies, permissions, and background services.

## First-run wizard

The wizard should configure:

- Local AI.
- Hardware settings.
- Model installation.
- Audio devices.
- Voice or text preferences.
- Wake word.
- Floating assistant.
- Performance mode.
- Privacy settings.
- Optional integrations.
- Storage location.

Default to Eco Mode.

Provide sensible settings requiring minimal technical knowledge.

---

# 24. MULTIPLE INSTANCES AND PROFILES

Support multiple separate JARVIS profiles.

Examples:

- Personal JARVIS.
- Work JARVIS.
- Testing JARVIS.

Each profile must have independent:

- Conversations.
- Memory.
- Skills.
- Schedules.
- Settings.
- Permissions.
- Credentials.
- Task history.
- Integration configuration.

Allow users to switch profiles.

Where simultaneous instances are supported, isolate their data and background task state.

Prevent:

- Database corruption.
- Duplicate scheduled executions.
- Port conflicts.
- Conflicting file modifications.
- Unnecessary duplicate AI servers.

Share downloaded models and infrastructure where safe and practical.

**Multiple profiles must not automatically cause multiple large models to remain loaded in memory.**

A newly installed copy of JARVIS on another person's computer must contain none of my private data.

---

# 25. BACKUP, EXPORT AND IMPORT

Provide reliable local backup and restoration.

Support exporting:

- Saved skills.
- Workflow definitions.
- Application settings.
- Conversation history.
- Authorized memory data.
- Task schedules.

Do not include credentials in ordinary exports.

Allow importing saved skills into another JARVIS installation.

Example:

I create a Sesolos Upload Formatter skill on my computer.

I should be able to export that skill and import it into another JARVIS installation without sharing my personal conversations, account passwords, or memory.

Validate imported workflows and require approval of requested permissions before execution.

Support versioned backups and recovery.

---

# 26. SOFTWARE UPDATES AND MAINTENANCE

Implement a safe update mechanism.

Requirements:

- Application versioning.
- Update checks when enabled.
- Release notes.
- Verified downloads.
- User approval before installing updates.
- Backup before important migrations.
- Preservation of settings and memory.
- Safe database migrations.
- Rollback or recovery where feasible.

Do not automatically execute unverified update scripts.

Do not silently replace user-created skills.

The application must remain functional offline even when update services are unavailable.

---

# 27. REQUIRED DEVELOPMENT PROCEDURE

You must execute this project in logical stages.

Do not merely describe the stages.

## Phase 1 — Agent capability discovery

- Audit installed tools.
- Discover useful missing skills and plugins.
- Evaluate MCP servers.
- Install approved free tools.
- Verify their operation.

## Phase 2 — Hardware inspection

- Inspect Windows.
- Detect CPU, RAM, GPU, and storage.
- Inspect existing software.
- Identify hardware limitations.
- Choose appropriate models and architecture.

## Phase 3 — Environment installation

- Install necessary dependencies.
- Configure development runtimes.
- Install Ollama or chosen inference engine.
- Download local models.
- Install speech dependencies.
- Configure development and testing tools.

## Phase 4 — Core assistant

Build:

- AI inference interface.
- Conversation engine.
- Text chat.
- Tool calling.
- Local memory.
- Configuration system.
- Security and permissions.

## Phase 5 — Windows application

Build:

- Main desktop UI.
- Conversations.
- Floating bubble.
- System tray.
- Settings.
- Background task dashboard.

## Phase 6 — Voice functionality

Implement:

- Speech recognition.
- Speech synthesis.
- Push-to-talk.
- Optional wake word.
- Audio configuration.
- Voice interruption.

## Phase 7 — Computer automation

Implement:

- Filesystem tools.
- System diagnostics.
- Controlled PowerShell.
- Document processing.
- Browser automation.
- Background task execution.
- Foreground protection.

## Phase 8 — Skills system

Build:

- Teach New Skill.
- Workflow generation.
- Skill testing.
- Skills Library.
- Natural-language invocation.
- Versioning.
- Import/export.

## Phase 9 — Watch & Learn

Implement:

- Authorized observation.
- Event collection.
- Screenshot capture where necessary.
- Browser interaction observation.
- Demonstration interpretation.
- Workflow generation.
- Review and correction.
- Saved skill integration.

## Phase 10 — Scheduling and productivity

Implement:

- Recurring tasks.
- Reminders.
- Folder monitoring.
- Background execution.
- Optional calendar/email integrations.

## Phase 11 — Performance optimization

- Benchmark resource usage.
- Optimize model loading.
- Reduce idle overhead.
- Implement performance modes.
- Limit worker concurrency.
- Verify background responsiveness.

Performance constraints must also be considered throughout earlier phases, not only during this phase.

## Phase 12 — Security validation

- Review permissions.
- Test tool restrictions.
- Inspect credential handling.
- Test prompt-injection resistance.
- Validate foreground protection.
- Verify privacy controls.

## Phase 13 — Documentation

- Capture real application screenshots.
- Write the complete manual.
- Generate PDF.
- Generate offline HTML.
- Create Quick Start Guide.
- Integrate the Help Centre.
- Verify documented functionality.

## Phase 14 — Installer and distribution

- Package the application.
- Build the Windows installer.
- Prepare dependencies.
- Configure first-run setup.
- Test installation.
- Prepare offline package where feasible.
- Verify clean profiles.

## Phase 15 — Final installation

- Install JARVIS on my computer.
- Configure local AI.
- Create shortcuts.
- Launch the application.
- Test actual functionality.
- Verify restart persistence.
- Confirm background execution.
- Perform final performance checks.

Do not stop at source-code completion.

---

# 28. AUTOMATED TESTING AND ACCEPTANCE CRITERIA

Create real automated tests where possible.

Use disposable files and safe test environments.

Never claim simulated results prove a real integration works.

## Core functionality

| Test | Expected result |
|---|---|
| "Jarvis, hello." | Responds naturally |
| "What time is it?" | Correct local time |
| Text chat | Fully functional |
| Voice input | Recognizes speech |
| Voice output | Speaks response |
| Restart JARVIS | Settings and history persist |
| "What model are you running?" | Reports actual model |

## Windows tools

| Test | Expected result |
|---|---|
| "Open Notepad." | Opens Notepad on explicit request |
| "What's my CPU usage?" | Retrieves real CPU usage |
| "Find my reports." | Searches authorized local files |
| "Create a test note." | Creates a real file |
| "Check my internet connection." | Executes actual diagnostics |

## Non-intrusive background operation

| Test | Expected result |
|---|---|
| Process Excel files while Notepad is active | Notepad retains focus |
| Run browser automation while using Chrome | User's browser remains unaffected |
| Run a background script | No command window steals focus |
| Type while a task is running | User keyboard input remains uninterrupted |
| Copy and paste during automation | Clipboard remains unchanged |
| Move mouse during automation | JARVIS does not interfere |
| Minimize JARVIS during a task | Task continues |
| Cancel a task | Task stops safely |
| Run concurrent jobs | Resource limits remain respected |

## Memory

| Test | Expected result |
|---|---|
| Save a test fact | Fact is stored |
| Retrieve test fact | Correct information returned |
| Restart application | Memory persists |
| Delete memory | Selected information is removed from active memory storage |

## Teachable skills

| Test | Expected result |
|---|---|
| Provide example input and output | JARVIS analyzes differences |
| Teach simple CSV transformation | Creates executable workflow |
| Test generated workflow | Output is validated |
| Save skill | Skill persists |
| Restart JARVIS | Skill remains available |
| Invoke skill by name | Correct workflow executes |
| Modify skill | New version created |
| Roll back skill | Earlier version restored |
| Export skill | Valid portable skill package generated |
| Import skill | Skill becomes available after validation |

## Watch & Learn

| Test | Expected result |
|---|---|
| Start observation | Requires authorization and shows status |
| Observe browser navigation | Relevant steps captured |
| Explain a step | Instruction associated with action |
| Stop observation | Capture stops immediately |
| Review demonstration | Accurate step summary |
| Generate automation | Workflow created |
| Save skill | Workflow persists |
| Run learned skill | Executes without taking over active desktop |
| Delete recording | Captured data removed according to retention policy |

## Scheduling

| Test | Expected result |
|---|---|
| Create reminder | Reminder scheduled |
| Restart application | Reminder persists |
| Create recurring skill | Schedule stored |
| Place file in monitored folder | Workflow triggers |
| Reprocess same unchanged file | Duplicate execution prevented |

## Performance

Verify:

- Low idle CPU use.
- Low resident memory consumption.
- AI models unload after inactivity.
- Minimal minimized UI usage.
- No persistent unnecessary GPU consumption.
- Background tasks throttle when appropriate.
- Foreground applications remain responsive.
- Closing JARVIS releases its resources.

## Installer

Verify:

- Installer launches.
- Installation succeeds.
- Application launches.
- First-run wizard functions.
- Local model initializes.
- Shortcuts work.
- User data survives upgrades.
- Separate profiles are isolated.
- Uninstall operates correctly.
- Clean installation works without development tools, where test infrastructure is available.

If a test cannot be performed, identify it as unverified rather than successful.

---

# 29. ERROR RECOVERY AND AUTONOMOUS TROUBLESHOOTING

When an implementation step fails:

1. Read the actual error.
2. Investigate the underlying cause.
3. Check documentation and installed tools.
4. Search for an appropriate technical solution.
5. Apply a safe correction.
6. Rerun the failed operation.
7. Verify the result.
8. Continue development.

Do not blindly repeat failing commands.

Do not ask me to debug problems you can diagnose yourself.

Do not replace working features with untested changes.

Maintain checkpoints and version control.

If a preferred technology proves unsuitable, select a suitable alternative and document the change.

Where a limitation cannot be resolved, explain it accurately and continue with achievable functionality.

---

# 30. FINAL DELIVERABLES

The finished project must include:

## Installed application

- Working JARVIS desktop application.
- Text chat.
- Voice functionality.
- Floating assistant.
- System tray integration.
- Local AI model.
- Background automation engine.
- Persistent memory.
- Skills Library.
- Watch & Learn.
- Scheduler.
- Performance management.
- Permissions.
- Help Centre.

## Distribution

- JARVIS-Setup-x64.exe.
- Offline installer where legally and technically feasible.
- Optional portable version.
- Source code.
- Installation instructions.
- Required licenses and acknowledgements.
- Version and release notes.

## Documentation

- Full PDF User Guide.
- Offline HTML Guide.
- In-app Help Centre.
- Quick Start Guide.
- Troubleshooting Guide.
- Example command library.

## Development records

- Installed skills and plugins.
- MCP servers configured.
- AI models installed.
- Dependencies.
- Architecture documentation.
- Automated test results.
- Performance benchmarks.
- Known limitations.
- Security and permission review.

## Final implementation report

Provide:

1. Installation location.
2. Application executable location.
3. Desktop shortcut location.
4. Installer location.
5. Selected local AI models.
6. Speech engines installed.
7. Development tools installed.
8. Runtime plugins and integrations.
9. Verified working features.
10. Saved workflow functionality.
11. Background automation test results.
12. CPU, RAM, GPU, and idle benchmarks.
13. Documentation locations.
14. Outstanding limitations.
15. Any actions requiring my participation.

---

# 31. FINAL ENGINEERING PRIORITIES

Whenever architectural trade-offs arise, use this priority order:

**Priority 1 — Safety and correctness**

Protect my files, credentials, accounts, privacy, and operating system.

**Priority 2 — Non-interference**

Never commandeer my live desktop or interrupt my normal work during unattended operations.

**Priority 3 — Resource efficiency**

Keep idle overhead extremely low and protect foreground application performance.

**Priority 4 — Reliability**

Prefer stable deterministic automation over fragile simulated mouse interaction.

**Priority 5 — Functional completeness**

Implement useful working capabilities rather than visually impressive placeholders.

**Priority 6 — Ease of use**

Make JARVIS intuitive for people who do not have programming knowledge.

**Priority 7 — Extensibility**

Allow skills, plugins, integrations, and automation capabilities to evolve.

**Priority 8 — Response speed and appearance**

Optimize response latency and visual polish without compromising the above priorities.

---

# 32. IMPORTANT DEVELOPMENT RESTRICTIONS

Do not:

- Deliver only a development plan.
- Stop after generating source code.
- Ask me to manually install ordinary dependencies.
- Ask me to copy and execute commands you can run yourself.
- Require a paid subscription.
- Activate paid billing.
- Invent API keys.
- Assume unlimited free cloud inference.
- Keep large AI models running unnecessarily.
- Build automation around uncontrolled mouse and keyboard replay.
- Take over my desktop during background jobs.
- Silently record my screen.
- Store passwords in conversational memory.
- Include personal data in distributable installers.
- Grant untrusted plugins unrestricted access.
- Bypass Windows security protections.
- Claim a feature works without verifying it.
- Mark untested functionality as complete.
- Leave placeholder buttons for core requirements.
- Omit the installer.
- Omit the user guide.
- Ignore resource usage.

You may use independent technical judgment to determine implementation details.

You must actively use your tools, install dependencies, build the application, and test its functionality.

If you are operating in a restricted environment without actual access to my Windows computer, state that limitation clearly and perform the maximum feasible implementation without falsely claiming installation.

Do not initiate deployment actions requiring sensitive permissions without appropriate approval.

---

# 33. FINAL INSTRUCTION — BEGIN IMPLEMENTATION

You are not being asked to describe how JARVIS could theoretically be developed.

**You are being instructed to build, install, and deliver JARVIS.**

Your first actions must be:

1. Audit your available agent tools, skills, plugins, and MCP servers.
2. Discover and install useful missing development capabilities.
3. Inspect my Windows 11 computer.
4. Determine the optimal resource-efficient architecture.
5. Install the necessary development and AI components.
6. Begin creating the actual application.

Work independently through the implementation phases.

Do not stop after giving me an overview or asking routine technical questions.

Use reasonable defaults.

Install what is needed.

Write the code.

Run the tests.

Fix the problems.

Package the software.

Generate the documentation.

Install the application.

Launch it.

Verify that it works.

**THE FINAL OBJECTIVE IS A REAL, FREE, LIGHTWEIGHT, SECURE, DISTRIBUTABLE, TEACHABLE, LOCAL-FIRST JARVIS PERSONAL ASSISTANT THAT WORKS INDEPENDENTLY IN THE BACKGROUND WITHOUT INTERFERING WITH MY COMPUTER.**

**DISCOVER. INSTALL. BUILD. TEST. OPTIMIZE. DOCUMENT. PACKAGE. DEPLOY. VERIFY.**
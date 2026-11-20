[Setup]
AppId={{EA7F6A95-EBA6-4A35-BD39-667FA105E0E9}
AppName=JARVIS
AppVersion=0.1.0
AppPublisher=JARVIS Local Assistant
DefaultDirName={localappdata}\Programs\JARVIS
DefaultGroupName=JARVIS
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.22000
OutputDir=..\..\outputs
OutputBaseFilename=JARVIS-Setup-x64
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\JARVIS.exe
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Files]
Source: "dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: checkedonce

[Icons]
Name: "{group}\JARVIS"; Filename: "{app}\JARVIS.exe"
Name: "{group}\User guide"; Filename: "{app}\_internal\docs\User-Guide.html"
Name: "{group}\Uninstall JARVIS"; Filename: "{uninstallexe}"
Name: "{autodesktop}\JARVIS"; Filename: "{app}\JARVIS.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\JARVIS.exe"; Description: "Open JARVIS"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Profile data and shared AI/browser installations are intentionally preserved.

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "JARVIS"; Flags: uninsdeletevalue

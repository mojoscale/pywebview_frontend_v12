#define AppVer "0.2.0"

[Setup]
AppName=Mojoscale
AppVersion={#AppVer}
DefaultDirName={pf}\Mojoscale
DefaultGroupName=Mojoscale
UninstallDisplayIcon={app}\Mojoscale.exe
OutputDir=build\installer
OutputBaseFilename=Mojoscale-{#AppVer}
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\build\app.dist\app.exe"; DestDir: "{app}"; DestName: "Mojoscale.exe"
Source: "..\build\app.dist\*"; \
    Excludes: "app.exe,*.manifest,*.exp,*.lib,*.build-id,*.bak,__pycache__,*.log,black,platformdirs,pathspec"; \
    DestDir: "{app}"; Flags: recursesubdirs ignoreversion createallsubdirs

[Icons]
Name: "{group}\Mojoscale IDE"; Filename: "{app}\Mojoscale.exe"
Name: "{commondesktop}\Mojoscale IDE"; Filename: "{app}\Mojoscale.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\Mojoscale.exe"; WorkingDir: "{app}"

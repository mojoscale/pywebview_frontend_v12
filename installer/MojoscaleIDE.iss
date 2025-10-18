#define AppVer "0.1.6"

[Setup]
; Basic info
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
; Copy everything from Nuitka build
Source: "..\build\app.dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\Mojoscale IDE"; Filename: "{app}\app.exe"

; Optional desktop shortcut
Name: "{commondesktop}\Mojoscale IDE"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Tasks]
; Checkbox in installer for creating desktop icon
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\app.exe"
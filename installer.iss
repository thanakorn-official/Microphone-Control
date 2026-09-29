[Setup]
AppName=Mic Mute Controller
AppVersion=1.0
DefaultDirName={autopf}\MicMuteController
DefaultGroupName=Mic Mute Controller
OutputDir=Output_Installer
OutputBaseFilename=Mic_Control_Setup
SetupIconFile=mic_icon.ico
UninstallDisplayIcon={app}\Mic_Control.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\Mic_Control\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "languages.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\Mic Mute Controller"; Filename: "{app}\Mic_Control.exe"
Name: "{group}\Uninstall Mic Mute Controller"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Mic Mute Controller"; Filename: "{app}\Mic_Control.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Mic_Control.exe"; Description: "Launch Mic Mute Controller"; Flags: nowait postinstall skipifsilent

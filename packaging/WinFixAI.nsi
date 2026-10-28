Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

!ifndef APP_FILE
  !error "Pass APP_FILE pointing to the single-file Windows app"
!endif
!ifndef OUTPUT_FILE
  !error "Pass OUTPUT_FILE pointing to the setup EXE"
!endif

Name "WinFix AI (Preview)"
OutFile "${OUTPUT_FILE}"
InstallDir "$LOCALAPPDATA\Programs\WinFixAI"
RequestExecutionLevel user
SetCompressor /SOLID lzma
SetCompressorDictSize 32
VIProductVersion "0.1.2.0"
VIAddVersionKey /LANG=1033 "ProductName" "WinFix AI Preview"
VIAddVersionKey /LANG=1033 "FileDescription" "WinFix AI per-user installer"
VIAddVersionKey /LANG=1033 "FileVersion" "0.1.2-preview"
VIAddVersionKey /LANG=1033 "LegalCopyright" "WinFix AI contributors"

!define MUI_ABORTWARNING
!define MUI_LANGDLL_ALLLANGUAGES
!define MUI_LANGDLL_REGISTRY_ROOT HKCU
!define MUI_LANGDLL_REGISTRY_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI"
!define MUI_LANGDLL_REGISTRY_VALUENAME "InstallerLanguage"
!define MUI_WELCOMEPAGE_TEXT "$(Welcome)"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "../LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\WinFixAI.exe"
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Russian"

LangString Welcome ${LANG_ENGLISH} "Install the read-only WinFix AI preview for your Windows account.$\r$\n$\r$\nIncludes a local diagnostics menu and a local HTTPS test session. Remote connectivity requires technician configuration.$\r$\n$\r$\nThis unsigned preview has not yet been tested on Windows. It does not install a service or start automatically at login."
LangString Welcome ${LANG_RUSSIAN} "Установка предварительной версии WinFix AI для вашей учётной записи.$\r$\n$\r$\nДоступны базовая диагностика и локальный тестовый HTTPS-сеанс. Удалённое подключение настраивается специалистом.$\r$\n$\r$\nВерсия не подписана и ещё не проверена в Windows. Службы и автозапуск не устанавливаются."
LangString CloseFirst ${LANG_ENGLISH} "Close WinFix AI before installing or uninstalling."
LangString CloseFirst ${LANG_RUSSIAN} "Перед установкой или удалением закройте WinFix AI."
LangString DataKept ${LANG_ENGLISH} "Private diagnostics and session files are retained in %LOCALAPPDATA%\WinFixAI\Data. Remove them manually when no longer needed."
LangString DataKept ${LANG_RUSSIAN} "Личные отчёты и сеансы сохранены в %LOCALAPPDATA%\WinFixAI\Data. Удалите их вручную, когда они больше не нужны."

Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "WinFix AI requires 64-bit Windows."
    Abort
  ${EndIf}
  SetShellVarContext current
  SetRegView 64
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "WinFix AI" SEC_APP
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /oname=WinFixAI.exe "${APP_FILE}"
  File /oname=LICENSE.txt "../LICENSE"
  File /oname=QUICK-START.txt "QUICK-START.txt"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\WinFix AI"
  CreateShortcut "$SMPROGRAMS\WinFix AI\WinFix AI.lnk" "$INSTDIR\WinFixAI.exe"
  CreateShortcut "$SMPROGRAMS\WinFix AI\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\WinFix AI.lnk" "$INSTDIR\WinFixAI.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "DisplayName" "WinFix AI (Preview)"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "DisplayIcon" "$INSTDIR\WinFixAI.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "DisplayVersion" "0.1.2-preview"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "Publisher" "WinFix AI contributors"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI" "NoRepair" 1
SectionEnd

Function un.onInit
  SetShellVarContext current
  SetRegView 64
  !insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_OKCANCEL "$(CloseFirst)" IDOK +2
  Abort
FunctionEnd

Section "Uninstall"
  ClearErrors
  Delete "$INSTDIR\WinFixAI.exe"
  ${If} ${Errors}
    MessageBox MB_ICONSTOP "$(CloseFirst)"
    Abort
  ${EndIf}
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\QUICK-START.txt"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$DESKTOP\WinFix AI.lnk"
  Delete "$SMPROGRAMS\WinFix AI\WinFix AI.lnk"
  Delete "$SMPROGRAMS\WinFix AI\Uninstall.lnk"
  RMDir "$SMPROGRAMS\WinFix AI"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinFixAI"
  RMDir "$INSTDIR"
  MessageBox MB_OK "$(DataKept)"
SectionEnd

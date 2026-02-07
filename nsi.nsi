; ================================
; DoScript NSIS Installer (FINAL)
; ================================

!define APP_NAME "DoScript"
!define APP_EXE  "do.exe"
!define APP_BAT  "do.bat"
!define APP_DIR  "$PROGRAMFILES\DoScript"

Name "${APP_NAME}"
OutFile "DoScriptSetup.exe"
InstallDir "${APP_DIR}"
RequestExecutionLevel admin

Icon "do.ico"
UninstallIcon "do.ico"

; --------------------------------
; Pages
; --------------------------------
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

; --------------------------------
; Install Section
; --------------------------------
Section "Install"

  SetOutPath "$INSTDIR"

  ; Copy executable and launcher
  File "build\do.exe"
  File "build\do.bat"

  ; ---- Register .do file extension ----
  WriteRegStr HKCU "Software\Classes\.do" "" "DoScriptFile"
  WriteRegStr HKCU "Software\Classes\DoScriptFile" "" "DoScript File"
  WriteRegStr HKCU "Software\Classes\DoScriptFile\DefaultIcon" "" '"$INSTDIR\${APP_EXE}",0'
  WriteRegStr HKCU "Software\Classes\DoScriptFile\shell\open\command" "" '"$INSTDIR\${APP_EXE}" "%1"'

  ; ---- Add to PATH (user) ----
  ReadRegStr $0 HKCU "Environment" "PATH"

  StrCmp $0 "" 0 +2
    StrCpy $0 ""

  StrCpy $1 "$0;$INSTDIR"
  WriteRegExpandStr HKCU "Environment" "PATH" $1

  ; Notify system PATH changed
  System::Call 'user32::SendMessageTimeoutA(i 0xffff, i 0x1A, i 0, t "Environment", i 0, i 5000, *i .r0)'

  ; ---- Write uninstaller ----
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


; --------------------------------
; Uninstall Section
; --------------------------------
Section "Uninstall"

  ; Remove installed files
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\${APP_BAT}"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"

  ; Remove file association
  DeleteRegKey HKCU "Software\Classes\.do"
  DeleteRegKey HKCU "Software\Classes\DoScriptFile"

  ; NOTE:
  ; PATH cleanup intentionally skipped for safety

SectionEnd

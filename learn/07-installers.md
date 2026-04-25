# Lesson 07 — Writing Installer Scripts

Installer scripts are one of the most common uses for DoScript.
This lesson covers the full toolkit — from the basic pattern through
admin checks, shortcuts, registry, package managers, and distributing
as a compiled EXE.

---

## The Core Pattern

```
say "=== My App Installer ==="

global_variable = confirm
ask confirm "Install My App? (y/n)"

if confirm == "y"
    make folder "C:/MyApp"

    try
        download "https://example.com/myapp.zip" to "C:/MyApp/myapp.zip"
    catch NetworkError
        say "Download failed. Visit: https://example.com/myapp"
        exit 1
    end_try

    unzip "C:/MyApp/myapp.zip" to "C:/MyApp"
    path add "C:/MyApp/bin"
    delete "C:/MyApp/myapp.zip"

    say "Installation complete!"
end_if

pause
```

---

## require_admin

Fail immediately with a clear message if the script is not running as
administrator (Windows) or root (Unix/macOS). Put this at the very top.

```
require_admin "Please run this installer as Administrator."

# ... rest of installer only reaches here if running as admin
```

Without this, privileged scripts fail halfway through with cryptic
"Permission denied" errors.

---

## confirm

A cleaner single-line yes/no gate for destructive or irreversible actions:

```
confirm "Delete all logs? (y/N)" else exit
confirm "Overwrite backup? (y/N)" else say "Skipped."
```

The user types `y` or `yes` to proceed. Anything else runs the `else` branch.
Prefer `confirm` over hand-rolling `ask` + `if` for simple yes/no decisions.

---

## make shortcut

Create a desktop or Start Menu shortcut in one line. Works on Windows
(`.lnk` via PowerShell), macOS (Finder alias), and Linux (`.desktop` file).

```
make shortcut "My App" to "C:/MyApp/app.exe" on desktop
make shortcut "My App" to "C:/MyApp/app.exe" on startmenu
make shortcut "My App" to '{appdata}\MyApp\app.exe' on programs
```

The `on` clause is optional — `desktop` is the default.

---

## registry

Read and write the Windows registry directly. Useful for marking an app
as installed or storing user preferences.

```
# Write
registry set HKCU\Software\MyApp Theme "Dark"
registry set HKCU\Software\MyApp Version 2

# Read
global_variable = theme
registry get HKCU\Software\MyApp Theme to theme
say 'Theme is: {theme}'

# Check if already installed
global_variable = installed
registry exists HKCU\Software\MyApp to installed

if installed == true
    say "Already installed — skipping."
    exit
end_if

# Delete
registry delete HKCU\Software\MyApp Theme     # one value
registry delete HKCU\Software\MyApp           # entire key
```

Supported hives: `HKCU`, `HKLM`, `HKCR`, `HKU`, `HKCC`.
Windows only — raises a clear error on other platforms.

---

## install_package

Install software from any supported package manager without leaving the script.

```
install_package from winget "python"
install_package from apt "git"
install_package from brew "ffmpeg"
install_package from pip "requests"
install_package from npm "typescript"
install_package from choco "vlc"
install_package from scoop "curl"
```

Supported managers: `winget`, `choco`, `scoop`, `apt`, `brew`, `dnf`,
`yum`, `pacman`, `pip`, `npm`.

Use `--dry-run` to preview the commands without actually installing anything.

---

## use — Modules

Split large installer scripts into reusable modules. `use` searches:
1. Same folder as your script
2. A `modules/` subfolder
3. `~/DoScript/modules/` — your personal library

```
use "net.do"
use "files.do"
```

Each module is included at most once, so `use` is safe to call from
multiple files.

Recommended project layout:

```
my-project/
  installer.do
  modules/
    net.do
    files.do
```

---

## do build — Compile to EXE

Turn any `.do` script into a standalone distributable executable. Install
PyInstaller once, then build as needed.

```
pip install pyinstaller
python doscript.py build installer.do --onefile
```

Build options:

```
python doscript.py build installer.do --onefile
python doscript.py build installer.do --onefile --windowed
python doscript.py build installer.do --icon app.ico --title "My App Installer"
python doscript.py build installer.do --output build/
```

The compiled EXE includes an interactive recovery shell that activates on
crash — users drop into `doscript-runtime>` instead of seeing a bare error.

---

## Full Example — Production Installer

```
# myapp-installer.do
<doscript=0.6.14>

require_admin "Please run as Administrator."

say "==============================="
say "     MyApp Installer v2.0"
say "==============================="
say ""

global_variable = installed, confirm

registry exists HKCU\Software\MyApp to installed
if installed == true
    confirm "MyApp is already installed. Reinstall? (y/N)" else exit
end_if

global_variable = install_dir
menu install_dir from "Install location?" "AppData (recommended)" "Program Files" "Custom path"

if install_dir == "Custom path"
    select_path install_dir "Choose install folder" from '{user_home}' folders
end_if

say 'Installing to: {install_dir}...'

make folder install_dir

try
    download "https://example.com/myapp.zip" to '{install_dir}/myapp.zip'
catch NetworkError
    say "Download failed. Visit: https://example.com/myapp"
    exit 1
end_try

unzip '{install_dir}/myapp.zip' to install_dir
path add '{install_dir}/bin'
delete '{install_dir}/myapp.zip'

make shortcut "MyApp" to '{install_dir}/myapp.exe' on desktop
make shortcut "MyApp" to '{install_dir}/myapp.exe' on startmenu

registry set HKCU\Software\MyApp Installed "true"
registry set HKCU\Software\MyApp Version "2.0"
registry set HKCU\Software\MyApp Path install_dir

schedule "auto-update.do" daily at "03:00"

notify "MyApp" "Installation complete!"

say ""
say "==============================="
say "  Installation complete!"
say "  Run 'myapp' from any terminal."
say "==============================="

pause
```

---

## Installer Checklist

- [ ] `require_admin` at the top for privileged operations
- [ ] `registry exists` check to detect reinstalls
- [ ] `confirm` before any destructive step
- [ ] `menu` or `select_path` for install location choice
- [ ] `download` wrapped in `try/catch NetworkError`
- [ ] `make folder` before downloading into it
- [ ] `path add` if the app has CLI tools
- [ ] `make shortcut` on desktop and startmenu
- [ ] `registry set` to record install metadata
- [ ] `notify` to tell the user it's done
- [ ] Clean up downloaded archives with `delete`
- [ ] End with `pause` so the window stays open

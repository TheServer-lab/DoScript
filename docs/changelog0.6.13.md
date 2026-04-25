# DoScript v0.6.13 Changelog

## New Features

### `make shortcut` — create OS shortcuts

Create a shortcut to any file, folder, or URL on the Desktop or Start Menu
with a single line. Works on Windows, macOS, and Linux.

```
make shortcut "My App" to "C:/Program Files/MyApp/app.exe"
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on desktop
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on startmenu
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on programs
```

The `on` clause is optional — `desktop` is the default.

| Placement | Windows | macOS | Linux |
|---|---|---|---|
| `desktop` | `%USERPROFILE%\Desktop\Name.lnk` | `~/Desktop/Name.app` | `~/Desktop/Name.desktop` |
| `startmenu` / `programs` | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Name.lnk` | `/Applications/Name.app` | `~/.local/share/applications/Name.desktop` |

On Windows, shortcuts are created via PowerShell's `WScript.Shell` COM object —
no external dependencies required. On Linux, a standard `.desktop` file is
written. On macOS, a Finder alias is created via AppleScript.

Works with `--dry-run` — prints the shortcut path without creating it.

---

### `registry` — Windows registry access

Read, write, delete, and check the existence of Windows registry keys and
values. Raises a clear error on non-Windows platforms.

**Write a value:**

```
registry set HKCU\Software\MyApp Theme "Dark"
registry set HKCU\Software\MyApp Version 2
```

**Read a value into a variable:**

```
global_variable = theme
registry get HKCU\Software\MyApp Theme to theme
say 'Current theme: {theme}'
```

**Check existence:**

```
global_variable = installed
registry exists HKCU\Software\MyApp to installed

if installed == true
    say "Already installed."
end_if
```

**Delete a value or key:**

```
registry delete HKCU\Software\MyApp Theme     # delete one value
registry delete HKCU\Software\MyApp           # delete entire key
```

Supported hives: `HKCU`, `HKLM`, `HKCR`, `HKU`, `HKCC`.
Both `/` and `\` path separators are accepted.

Works with `--dry-run` — prints the operation without touching the registry.

---

### `run_from_web` — run a script from the DoScriptPackage repo

Fetch and run any `.do` script from
[TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage)
in one line, directly inside a script:

```
run_from_web cleaner.do
run_from_web git-setup.do
run_from_web tools/setup-python.do
```

The `.do` extension is optional — both forms work:

```
run_from_web cleaner
run_from_web cleaner.do
```

Single-quoted interpolation works, so the script name can be dynamic:

```
global_variable = tool
tool = "cleaner"
run_from_web '{tool}.do'
```

Scripts in subfolders of the repo are also supported:

```
run_from_web tools/git-setup.do
```

The fetched script runs with full access to the current variable scope and
inherits all declared globals and functions from the calling script. Any
variable changes the web script makes are propagated back to the caller.

Works with `--dry-run` — prints the URL that would be fetched without
downloading or running anything.

If the script is not found in the repo, DoScript raises a `NetworkError`
with the repo URL so you know where to look.

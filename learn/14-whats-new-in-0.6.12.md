# Lesson 14 — What's New in 0.6.12

## `install_package` — one-line software installs

Install any package from your system's package manager without leaving your script:

```
install_package from winget "python"
install_package from apt "git"
install_package from brew "ffmpeg"
install_package from pip "requests"
```

Supported managers: `winget`, `choco`, `scoop`, `apt`, `brew`, `dnf`,
`yum`, `pacman`, `pip`, `npm`.

Use `--dry-run` to preview the commands it would run without actually
installing anything.

---

## `use` — modules

`use` loads a `.do` file as a module. It's like `include`, but smarter about
where it looks:

```
use "net.do"
use "files.do"
```

DoScript searches in order:
1. Same folder as your script
2. A `modules/` subfolder next to your script
3. `~/DoScript/modules/` — your personal module library

The recommended layout for a project with shared utilities:

```
my-project/
  installer.do        ← your main script
  modules/
    net.do            ← use "net.do"
    files.do          ← use "files.do"
```

Each module is included at most once, so `use` is safe to call from
multiple files without double-loading.

---

## Map and array subscript access

You can now read and write nested JSON objects and lists with `[]` directly
in expressions, strings, and assignments.

### Reading

```
global_variable = cfg, tags, val

json_read "config.json" to cfg

val = cfg["version"]
val = cfg["user"]["name"]    # chains work naturally
val = tags[0]
```

You can also use subscripts directly inside interpolated strings:

```
say 'Version: {cfg["version"]}'
say 'Name: {cfg["user"]["name"]}'
say 'First tag: {tags[0]}'
```

### Writing

```
cfg["version"] = "2.0"
cfg["user"]["name"] = "Bob"
tags[1] = "BETA"
```

The change propagates back into the variable, so `json_write cfg to "config.json"`
afterwards saves the updated data correctly.

### Complete example

```
global_variable = cfg, name

json_read "settings.json" to cfg

name = cfg["user"]["name"]
say 'Loaded config for: {name}'

cfg["user"]["name"] = "Alice"
cfg["version"] = "2.0"

json_write cfg to "settings.json"
say 'Saved updated config.'
```

---

## `do build` — compile to EXE

Turn any `.do` script into a distributable executable. Install PyInstaller
once, then build as needed:

```
pip install pyinstaller
python doscript.py build installer.do
```

This produces `dist/installer.exe` on Windows, or `dist/installer` on
Linux/macOS.

### Build options

```
# Portable single file
python doscript.py build installer.do --onefile

# Silent GUI installer (no console)
python doscript.py build installer.do --onefile --windowed

# Custom icon and title
python doscript.py build installer.do --icon app.ico --title "My App Installer"

# Custom output folder
python doscript.py build installer.do --output build/
```

### The DoScript Runtime Console

When someone runs your compiled EXE, they see:

```
=====================================
 My App Installer
 Powered by DoScript Runtime v0.6.12
=====================================
Type 'help' for runtime commands.
```

If the script crashes instead of silently failing, the user drops into an
interactive recovery shell:

```
[ERROR] File not found: config.ini
  line 14: json_read config_path to cfg

Dropping to DoScript Runtime shell. Type 'help' for commands.

doscript-runtime> vars
  app_name = 'MyApp'
  install_path = 'C:/Program Files/MyApp'
doscript-runtime> restart
doscript-runtime> exit
```

Typing `doscript` shows runtime metadata — and introduces the user to
DoScript itself:

```
doscript-runtime> doscript
DoScript Runtime
Version:         0.6.12
Embedded Script: installer.do
Build Date:      2026-04-18
Official Repo:   https://github.com/TheServer-lab/DoScript
```

> **Note:** `_runtime_launcher_template.py` must be in the same folder as
> `doscript.py` when you run `do build`. Both files ship together in the
> DoScript distribution.

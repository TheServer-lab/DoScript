# DoScript v0.6.12 Changelog

## New Features

### `install_package` — cross-platform package installer

Install software from any supported package manager with one line:

```
install_package from winget "python"
install_package from apt "git"
install_package from brew "ffmpeg"
install_package from pip "requests"
install_package from npm "typescript"
```

Supported managers: `winget`, `choco`, `scoop`, `apt` / `apt-get`, `brew`,
`dnf`, `yum`, `pacman`, `pip` / `pip3`, `npm`.

Works with `--dry-run` — prints the underlying command without executing it.
Raises `ProcessError` if the package manager is not found on the current
system, or if the install fails.

---

### `use` — module system

Load a `.do` file as a reusable module. Like `include`, but searches a
dedicated module path instead of requiring a relative path:

```
use "net.do"
use "files.do"
```

**Search order:**
1. Same folder as the current script
2. `./modules/` subfolder relative to the current script
3. `~/DoScript/modules/` — user-global module library

Each module is loaded at most once per run, even if `use` appears multiple
times. Functions and macros defined in a module become available globally.

**Recommended structure:**

```
my-project/
  installer.do
  modules/
    net.do
    files.do
```

---

### Map and array subscript access

Read and write nested maps (JSON objects) and lists using `[]` notation
directly in expressions and assignments.

**Read in expressions:**

```
global_variable = cfg, tags, val

json_read "config.json" to cfg
val = cfg["version"]
val = cfg["user"]["name"]          # nested keys chain naturally

tags = split("alpha,beta,gamma", ",")
val = tags[0]
```

**Read in interpolated strings:**

```
say 'Version: {cfg["version"]}'
say 'First tag: {tags[0]}'
say 'Name: {cfg["user"]["name"]}'
```

**Write:**

```
cfg["version"] = "2.0"
cfg["user"]["name"] = "Bob"
tags[1] = "BETA"
```

Writes propagate back into the variable — `json_write cfg to "config.json"`
afterwards saves the updated data correctly.

---

### `do build` — compile to standalone EXE

Turn any `.do` script into a distributable executable. Requires
`pip install pyinstaller` once.

**Basic build:**

```
python doscript.py build installer.do
```

Outputs `dist/installer.exe` (Windows) or `dist/installer` (Linux/macOS).

**Build flags:**

| Flag | Effect |
|---|---|
| `--onefile` | Single portable file — no folder, just one EXE |
| `--windowed` | No console window (for GUI-style installers) |
| `--icon app.ico` | Set the EXE icon |
| `--title "My App"` | Banner title shown at runtime startup |
| `--output <dir>` | Output directory (default: `./dist`) |

**Examples:**

```
python doscript.py build installer.do --onefile
python doscript.py build installer.do --onefile --windowed --icon app.ico
python doscript.py build installer.do --title "My Program Installer" --output build/
```

**What the compiled EXE contains:**

```
installer.exe = [DoScript runtime engine]
                [embedded installer.do]
                [runtime console]
```

The runtime launches automatically, runs the embedded script, and if the
script crashes it drops into the **DoScript Runtime Console** instead of
showing a raw traceback:

```
=====================================
 My Program Installer
 Powered by DoScript Runtime v0.6.12
=====================================
Type 'help' for runtime commands.

[ERROR] File not found: config.ini
  line 14: json_read config_path to cfg

Dropping to DoScript Runtime shell. Type 'help' for commands.

doscript-runtime>
```

**Runtime console commands:**

| Command | Effect |
|---|---|
| `doscript` / `about` / `version` | Show runtime info and build metadata |
| `link` / `repo` / `website` | Open the DoScript GitHub repo in a browser |
| `run` / `restart` | Re-run the embedded script |
| `vars` | Dump all current variable values |
| `trace on` / `trace off` | Toggle verbose execution tracing |
| `exit` / `quit` | Exit |

**Runtime info command output:**

```
doscript-runtime> doscript
DoScript Runtime
Version:         0.6.12
Embedded Script: installer.do
Build Date:      2026-04-18
Official Repo:   https://github.com/TheServer-lab/DoScript
```

Every compiled EXE becomes a self-contained node in the DoScript ecosystem.
Users who run your installer and type `doscript` discover DoScript itself.

**Architecture note:** The runtime engine (`doscript.py`) and launcher
template (`_runtime_launcher_template.py`) must be in the same folder when
running `do build`. Both files ship together in the DoScript distribution.

# DoScript — Changelog

## v0.6.13

### New Features

**`make shortcut` — OS shortcuts**
Create desktop or Start Menu shortcuts to any file, folder, or URL.
```
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on desktop
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on startmenu
```
Works on Windows (`.lnk` via PowerShell), macOS (Finder alias), Linux (`.desktop`). No extra dependencies.

**`registry` — Windows registry access**
Read, write, delete, and check the existence of registry keys and values.
```
registry set HKCU\Software\MyApp Theme "Dark"
registry get HKCU\Software\MyApp Theme to theme
registry exists HKCU\Software\MyApp to installed
registry delete HKCU\Software\MyApp Theme
```
Supported hives: `HKCU`, `HKLM`, `HKCR`, `HKU`, `HKCC`. Raises a clear error on non-Windows. Respects `--dry-run`.

**`run_from_web` — run a script from DoScriptPackage**
Fetch and run any `.do` script from [TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage) in one line, from inside a script:
```
run_from_web cleaner.do
run_from_web git-setup.do
run_from_web tools/setup-python.do
```
Supports bare names (`.do` auto-appended), single-quoted interpolation, subfolder paths, and `--dry-run`.

---

## v0.6.12

### New Features

**`install_package` — cross-platform package installer**
Install software from any supported package manager in one line.
```
install_package from winget "python"
install_package from apt "git"
install_package from brew "ffmpeg"
install_package from pip "requests"
```
Supported: `winget`, `choco`, `scoop`, `apt`, `brew`, `dnf`, `yum`, `pacman`, `pip`, `npm`.
Works with `--dry-run`. Raises `ProcessError` if the manager is not found or the install fails.

**`use` — module system**
Load a `.do` file as a module. Searches `./modules/` and `~/DoScript/modules/` automatically.
```
use "net.do"
use "files.do"
```

**Map and array subscript access**
Read and write nested JSON objects and lists with `[]` notation in expressions, strings, and assignments.
```
cfg["version"] = "2.0"
cfg["user"]["name"] = "Bob"
say 'Name: {cfg["user"]["name"]}'
val = tags[0]
tags[1] = "BETA"
```

**`do build` — compile to standalone EXE**
Compiles a `.do` script into a distributable executable with an embedded DoScript runtime. Requires `pip install pyinstaller`.
```
python doscript.py build installer.do
python doscript.py build installer.do --onefile --windowed --icon app.ico --title "My App"
```
Built EXEs include the **DoScript Runtime Console**: a branded recovery shell that activates on crash, shows runtime metadata on `doscript`, and opens the official repo on `link`.
The launcher template is embedded inside `doscript.py` — no separate template file required.
`do build` works correctly when DoScript itself is distributed as a compiled `do.exe` (frozen exe detection via `sys.frozen`).

---

v0.6.11
> Merge of parallel v0.6.10 development branches

### Bug Fixes

**Built-in path variables now expand inside double-quoted strings**
Previously, writing `"{downloads}\file.do"` in a double-quoted string would be passed through literally — the file would be saved to a path named `{downloads}\file.do` rather than the user's actual Downloads folder. Built-in read-only variables (`downloads`, `user_home`, `username`, `desktop`, `documents`, `appdata`, `temp`, time variables, and CLI args) are now automatically resolved inside double-quoted strings. The `[HINT]` about single quotes is suppressed for these names since they are system constants, not user-defined variables.

```
# Before — silently wrong, file saved to literal "{downloads}\file.do"
download "https://example.com/setup.do" to "{downloads}\setup.do"

# After — works correctly in both quote styles
download "https://example.com/setup.do" to "{downloads}\setup.do"   # ✅ resolved
download "https://example.com/setup.do" to '{downloads}\setup.do'   # ✅ also fine
```

---

### New Features

**`json_set` command**
Write a value directly into a JSON object variable. Supports dot notation for nested keys.
```
json_read 'config.json' to cfg
json_set cfg "user.name" newName
json_set cfg "version" "2.0"
json_write cfg to 'config.json'
```

**Flexible paths for `json_read` and `json_write`**
Both commands now accept variables, single-quoted interpolated strings, and expressions — not just hardcoded double-quoted paths.
```
global_variable = config_path
config_path = "settings.json"

json_read config_path to cfg
json_write cfg to 'backups/config_{today}.json'
```

**Flexible paths for `system_disk`**
`system_disk` now accepts variable paths and expressions, consistent with other file commands.
```
global_variable = target_drive, usage
target_drive = "C:/"
system_disk target_drive to usage
say 'Disk usage: {usage}%'
```

**Bare function calls as statements**
Functions can now be called as standalone statements without needing to capture their return value.
```
function greet name
    say 'Hello, {name}!'
end_function

greet("Alice")   # works — no assignment needed
```

---

## v0.6.10
> New features and bug fixes

### Bug Fixes

- Replaced deprecated `unicode_escape` codec with manual escape handling — non-ASCII characters in double-quoted strings now work correctly
- Double-quoted strings containing `{var}` patterns now emit a helpful hint suggesting single quotes instead of silently printing the literal `{var}` text

### New Features

**`rename` command**
Dedicated rename command — cleaner than using `move` for renames.
```
rename "draft.txt" to "final.txt"
```

**Environment variable access**
```
set_env "MY_VAR" to "hello"
global_variable = val
val = get_env("MY_VAR")
```

**`require_admin`**
Fails early with a clear message if the script is not running as administrator (Windows) or root (Linux/macOS).
```
require_admin "This installer requires administrator rights."
```

**`confirm` command**
Single-line confirmation prompt — cleaner alternative to `ask` + `if` for destructive actions.
```
confirm "Delete all temp files? (y/n)" else exit
```

**List operations**
Basic list manipulation: `list_add`, `list_get()`, `list_length()`.
```
global_variable = items
list_add items "apple"
list_add items "banana"
say list_get(items, 0)        # apple
say list_length(items)        # 2
```

**`for_each` over a list variable**
```
global_variable = fruits
list_add fruits "apple"
list_add fruits "banana"

for_each fruit in fruits
    say 'Fruit: {fruit}'
end_for
```

**`{loop_count}` variable**
Automatically populated with the number of items iterated after every `for_each` loop.
```
for_each file_in here
    say 'Found: {file_name}'
end_for
say 'Total files: {loop_count}'
```

**Age-based file filters in `for_each`**
```
for_each file_in here older_than 30 days
    delete file_path
end_for

for_each file_in here newer_than 7 days
    say 'Recent: {file_name}'
end_for
```

**Multi-line `make file` (heredoc)**
```
make file "script.sh" with
    #!/bin/bash
    echo "Hello"
    echo "World"
end_file
```

**`is_running()` expression**
```
if is_running("chrome.exe")
    say "Chrome is open."
end_if
```

**Built-in path variables**
Always available — no declaration needed. Cross-platform (Windows, macOS, Linux).

| Variable | Value |
|---|---|
| `user_home` | Current user's home directory |
| `username` | Current user's login name |
| `downloads` | Path to Downloads folder |
| `desktop` | Path to Desktop |
| `documents` | Path to Documents folder |
| `appdata` | AppData/Roaming (or `~/.config` on Linux/macOS) |
| `temp` | System temporary files directory |

```
say 'Hello, {username}!'
make folder '{downloads}/sorted'
zip "project" to '{desktop}/project_backup.zip'
```

**Remote script cache cleanup**
The `.doscript_remote_cache` directory is now automatically cleaned up after each remote script run. Previously, cached copies accumulated indefinitely.

---

## v0.6.9

- `else_if` — cleaner conditional chains without nested fallback `if` blocks
- String helpers: `length()`, `trim()`, `lower()`, `upper()`, `replace()`
- `execute_command "prog" "arg"` — safer process execution without shell parsing
- `loop N as i` — indexed loops expose the current iteration number

---

## v0.6.8

- Fixed include path resolution and error context for included scripts
- Fixed `return`/`break`/`continue` propagation through `try` blocks and loops
- Fixed nested `if_ends_with` / `if_file_contains` parsing inside `for_each`
- Fixed nested `for_each_line` parsing inside `end_for` blocks

---

## v0.6.7

- `if_file_contains "keyword"` — organise files by their text content
- `if_file_not_contains "keyword"` — inverse content check
- `read_content "file.txt" into var` — read file content into a variable
- `contains()` — case-insensitive substring check in expressions
- `{file_content}` — auto-injected in `for_each` loops for text files

---

## v0.6.6

- Fixed URL parsing bug

---

## v0.6.4

- `replace_in_file` — find and replace text inside a file
- `replace_regex_in_file` — regex-based find and replace
- `http_get`, `http_post`, `http_put`, `http_delete` — full HTTP client
- `random_number`, `random_string`, `random_choice` — random value generation
- `system_cpu`, `system_memory`, `system_disk` — system resource monitoring

---

## v0.6.3

- `path add` / `path remove` — Windows PATH environment variable support
- `--system` flag for system-wide PATH modification (requires admin)
- Broadcasts `WM_SETTINGCHANGE` to notify Windows of PATH updates immediately

---

## v0.6.2

- `do_new` — launch another DoScript instance, chain scripts together
- `make file script.do` — script template creation

---

## v0.6.1

- Built-in time variables: `time`, `today`, `now`, `year`, `month`, `day`, `hour`, `minute`, `second`
- JSON operations: `json_read`, `json_write`, `json_get`
- CSV operations: `csv_read`, `csv_write`, `csv_get`
- Archive operations: `zip`, `unzip`, `zip_list`
- Update checker, `open_link`, Windows shutdown command

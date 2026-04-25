# DoScript Reference Guide

> DoScript (v0.6.15) is a human-readable automation DSL that runs via `python doscript.py <script.do>`. Scripts use a `.do` extension and read like plain-English instructions.

---

## Table of Contents

1. [Running Scripts](#running-scripts)
2. [Basics](#basics)
3. [Control Flow](#control-flow)
4. [File Operations](#file-operations)
5. [for_each — File Iteration](#for_each--file-iteration)
6. [Functions and Macros](#functions-and-macros)
7. [Network](#network)
8. [Installer Scripts](#installer-scripts)
9. [Strings and Text Helpers](#strings-and-text-helpers)
10. [Safer Command Execution](#safer-command-execution)
11. [Data: JSON and CSV](#data-json-and-csv)
12. [Interactive UI](#interactive-ui)
13. [Scheduling and Debugging](#scheduling-and-debugging)
14. [Modules and Packages](#modules-and-packages)
15. [External Variables (.slev)](#external-variables-slev)
16. [Tips, Patterns, and Gotchas](#tips-patterns-and-gotchas)

---

## Running Scripts

```
python doscript.py myscript.do                  # run normally
python doscript.py myscript.do --dry-run        # preview without side effects
python doscript.py myscript.do --verbose        # extra runtime logging
python doscript.py myscript.do --debug          # debug header + verbose
python doscript.py --version                    # print interpreter version
python doscript.py --help                       # full usage reference
```

### Module Management

```
python doscript.py install_module math          # install from DoModule registry
python doscript.py install_module cli --dir ./modules   # install to custom path
```

---

## Basics

### Comments

```
# This is a comment
// This is also a comment
say "https://example.com"   # URLs inside strings are safe — // is NOT a comment here
```

### Variables

All variables **must be declared** before use with `global_variable`. You can declare multiple on one line.

```
global_variable = name
global_variable = firstName, lastName, age

name = "Alice"
age = 30
```

Variables are **loosely typed** — they hold strings, numbers, or booleans.

### Strings: Single vs Double Quotes

This is the most important rule in DoScript.

| Quote type | Behaviour | Use for |
|---|---|---|
| `"double"` | Literal — no variable substitution | Fixed text, paths, URLs |
| `'single'` | Interpolated — `{var}` is replaced | Output that includes variables |

```
global_variable = name
name = "World"

say "Hello {name}"      # prints:  Hello {name}   ← NOT interpolated
say 'Hello {name}'      # prints:  Hello World    ← interpolated
```

**Rule of thumb:** Use single quotes whenever you want to include a variable in your output.

### say, ask

```
say "Hello!"
say 'Your name is: {name}'
say 42
say name                    # prints the value of the variable

ask answer "What is your name?"   # auto-declares the variable, no global_variable needed
say 'Hello, {answer}!'
```

### log, warn, error

Use these instead of `say` for unattended scripts — they produce formatted, scannable output.

```
log "Process started"       # prints [INFO] Process started
warn "Disk is almost full"  # prints [WARN] Disk is almost full
error "File not found"      # prints [ERROR] File not found
```

### pause, wait, exit

```
pause               # waits for the user to press Enter
wait 2              # waits 2 seconds
wait 0.5            # waits half a second

exit                # exits with code 0
exit 1              # exits with code 1
```

### Built-in Time Variables

These are always available — do not declare or overwrite them.

| Variable | Value |
|---|---|
| `today` | Current date, e.g. `2025-04-01` |
| `now` | Current time, e.g. `14:30:00` |
| `year` | Current year |
| `month` | Current month (number) |
| `day` | Current day (number) |
| `hour` / `minute` / `second` | Time components |
| `time` | Unix timestamp |
| `arg1` … `arg32` | CLI arguments passed to the script |

### Built-in Path Variables

Seven path variables are always available on every platform.

| Variable | Windows | macOS / Linux |
|---|---|---|
| `user_home` | `C:\Users\Alice` | `/home/alice` |
| `username` | `Alice` | `alice` |
| `downloads` | `C:\Users\Alice\Downloads` | `~/Downloads` |
| `desktop` | `C:\Users\Alice\Desktop` | `~/Desktop` |
| `documents` | `C:\Users\Alice\Documents` | `~/Documents` |
| `appdata` | `C:\Users\Alice\AppData\Roaming` | `~/.config` |
| `temp` | `C:\Users\Alice\AppData\Local\Temp` | `/tmp` |

```
say 'Hello, {username}!'
make folder '{downloads}/Sorted'
zip "project" to '{desktop}/project_backup.zip'
```

Use these instead of hardcoded paths — scripts written with built-in path variables work on any machine.

### A Complete First Script

```
# hello.do
global_variable = name

ask name "What is your name?"
say 'Hello, {name}!'
say 'Today is {today}. Have a great day!'
say 'Your files are in: {downloads}'
pause
```

---

## Control Flow

### if / else_if / else / end_if

Conditions support `==`, `!=`, `<`, `>`, `<=`, `>=`, and logical operators `and`, `or`, `not`.

```
global_variable = age
age = 20

if age >= 18
    say "You are an adult."
else
    say "You are a minor."
end_if

if score >= 90
    say "Grade A"
else_if score >= 80
    say "Grade B"
else
    say "Keep going"
end_if
```

### repeat

```
repeat 5
    say "Hello!"
end_repeat
```

### loop

```
loop 3
    say "Looping..."
end_loop

loop 3 as i
    say 'Iteration {i}'
end_loop

loop forever
    say "This runs until Ctrl+C"
end_loop
```

### break and continue

```
loop forever
    i = i + 1
    if i == 5
        break
    end_if
    say 'i = {i}'
end_loop
```

`continue` is particularly useful inside `for_each` to skip certain files:

```
for_each file_in here
    if_ends_with ".do"
        continue        # skip .do files, process everything else
    end_if
    say 'Processing: {file_name}'
end_for
```

### try / catch / end_try

```
try
    download "https://example.com/file.zip" to "file.zip"
catch NetworkError
    say "Download failed — check your connection."
end_try
```

Available error types to catch:

| Type | Raised by |
|---|---|
| `NetworkError` | `download`, `http_get`, `ping`, etc. |
| `FileError` | `copy`, `move`, `delete`, file reads |
| `ProcessError` | `run`, `execute`, `kill` |
| `DataError` | `json_read`, `csv_read`, etc. |
| *(no type)* | Catches any error |

---

## File Operations

### make folder

Creates a directory (and any missing parent directories). Safe to call even if the folder already exists.

```
make folder "output"
make folder '{downloads}/Sorted'
```

### make file

```
make file "notes.txt"                          # empty file
make file "notes.txt" with "Hello, World!"     # with content
make file 'log_{today}.txt' with "Started"     # single-quoted, interpolated name
```

**Multi-line content with `end_file`:**

```
global_variable = app_name, port
app_name = "MyServer"
port = 8080

make file "config.ini" with
    [server]
    name = {app_name}
    port = {port}
    debug = false
end_file
```

### rename, copy, move, delete

```
rename "draft_v1.txt" to "final.txt"

copy "source.txt" to "backup/source.txt"

move file to "Documents"           # move to folder
move file to 'report_{today}.pdf'  # rename by moving

delete "temp.txt"
delete "C:/Temp/old_logs"          # recursive folder delete
delete file_path                   # use path variable from for_each
```

### exists()

```
if exists("config.json")
    say "Config found!"
end_if
```

### replace_in_file

```
replace_in_file "config.txt" "localhost" "192.168.1.100"
```

### zip and unzip

```
zip "my_folder" to "my_folder.zip"
unzip "archive.zip" to "extracted"

global_variable = contents
zip_list "archive.zip" to contents    # list contents without extracting
```

### read_content

```
global_variable = fileText
read_content "notes.txt" into fileText
say fileText
```

---

## for_each — File Iteration

`for_each` iterates over files, folders, or list items and auto-injects a rich set of variables for each item.

### Basic Syntax

```
for_each file_in here
    say 'Found: {file_name}'
end_for
```

The word before `_in` is your **variable prefix** — it determines all the auto-injected metadata names.

### Scope Keywords

| Keyword | What it scans |
|---|---|
| `here` | Files in the same folder as the script |
| `deep` | Files recursively in the script folder |
| `"some/path"` | Files in a specific folder |

```
for_each file_in here           # current directory, files only
for_each file_in deep           # recursive
for_each file_in "C:/Downloads" # specific path
for_each folder_in here         # folders only (prefix starts with "folder"/"dir")
```

### Auto-Injected Variables

Replace `file` with whatever prefix you chose.

| Variable | Contains |
|---|---|
| `file_name` | Full filename, e.g. `report.pdf` |
| `file_path` | Absolute path |
| `file_ext` | Extension including dot, e.g. `.pdf` |
| `file_size` | Size in bytes |
| `file_size_kb` / `file_size_mb` | Size in KB / MB |
| `file_is_dir` | `true` if it's a folder |
| `file_is_empty` | `true` if size is 0 |
| `file_created` | Creation timestamp (Unix) |
| `file_modified` | Last modified timestamp (Unix) |
| `file_is_old_days` / `_hours` / `_months` | Age since last modification |
| `file_content` | Full text content (text files only) |

### if_ends_with

```
for_each file_in here
    if_ends_with ".txt"
        say 'Text file: {file_name}'
    end_if
end_for
```

> **Note:** `if_ends_with` does **not** support `else`. Use `else_if file_ext ==` chains instead.

### if_file_contains / if_file_not_contains

```
for_each file_in here
    if_file_contains "ERROR"
        move file to "errors"
    end_if
end_for
```

### Age Filters

```
for_each old_file_in here older_than 30 days
    delete old_file_path
end_for

for_each f_in deep newer_than 1 hour
    log 'Recently changed: {f_name}'
end_for
```

Supported units: `seconds`, `minutes`, `hours`, `days`, `months`, `years`.

### {loop_count}

After any `for_each` loop ends, `loop_count` holds the number of items iterated.

```
for_each file_in here
    copy file to "backup"
end_for
say 'Copied {loop_count} files.'
```

### Iterating a List

```
global_variable = fruits, fruit
fruits = split("apple,banana,mango", ",")
list_add fruits "pear"

for_each fruit in fruits
    say 'Fruit: {fruit}'
end_for
```

### for_each_line

```
global_variable = line

for_each_line line in "servers.txt"
    ping line
end_for
```

### Practical Example — Sort Downloads by Extension

```
# sort-downloads.do
# Test first: python doscript.py sort-downloads.do --dry-run

for_each file_in here
    if_ends_with ".do"
        continue
    end_if

    if file_ext == ".jpg"
        make folder "Images"
        move file to "Images"
    else_if file_ext == ".png"
        make folder "Images"
        move file to "Images"
    else_if file_ext == ".mp4"
        make folder "Videos"
        move file to "Videos"
    else_if file_ext == ".pdf"
        make folder "Documents"
        move file to "Documents"
    else_if file_ext == ".zip"
        make folder "Archives"
        move file to "Archives"
    else
        make folder "Other"
        move file to "Other"
    end_if
end_for

say 'Sorted {loop_count} files.'
```

---

## Functions and Macros

### Functions

```
function greet name
    say 'Hello, {name}!'
end_function

greet("Alice")
```

**Return values:**

```
function add a b
    return a + b
end_function

global_variable = result
result = add(10, 5)
say 'Result: {result}'     # prints: Result: 15
```

**Local variables** — scoped to that function call:

```
function calculate x y
    local_variable = temp
    temp = x * y
    return temp
end_function
```

### Macros

Named blocks of statements with no parameters and no return value.

```
make a_command print_separator
    say "--------------------"
end_command

run "print_separator"
say "Section One"
run "print_separator"
```

### Functions vs Macros

| | Function | Macro |
|---|---|---|
| Parameters | ✅ Yes | ❌ No |
| Return value | ✅ Yes | ❌ No |
| Call syntax | `myFunc(args)` | `run "myMacro"` |
| Best for | Calculations, reusable logic | Repeated action sequences |

### include

```
include "helpers.do"

# Functions defined in helpers.do are now available
greet("World")
```

Each file is only included once, even if `include` appears multiple times.

---

## Network

### download

```
download "https://example.com/file.zip" to "file.zip"
download "https://example.com/data.csv" to '{downloads}/data.csv'
```

Always wrap downloads in `try/catch NetworkError`:

```
try
    download "https://example.com/app.zip" to "app.zip"
catch NetworkError
    say "Download failed. Check your internet connection."
    exit 1
end_try
```

### http_get / http_post / http_put / http_delete

```
global_variable = response, result

http_get  "https://api.example.com/status" to response
http_post "https://api.example.com/data" "{\"key\":\"value\"}" to result
http_put  "https://api.example.com/item/1" "{\"name\":\"new\"}" to result
http_delete "https://api.example.com/item/1" to result
```

### ping, open_link, upload

```
try
    ping "8.8.8.8"
    say "Network is up!"
catch NetworkError
    say "No network connection."
end_try

open_link "https://example.com"

upload "report.pdf" to "https://example.com/upload"
```

### set_env / get_env()

```
set_env "MY_APP_HOME" to "C:/MyApp"

global_variable = path
path = get_env("MY_APP_HOME")
say 'App is at: {path}'
```

### is_running()

```
global_variable = running
running = is_running("notepad.exe")

if running == true
    say "Notepad is open"
end_if
```

### run_from_web

Fetch and run a `.do` script from the DoScriptPackage repository without downloading anything manually.

```
run_from_web cleaner.do
run_from_web git-setup.do
```

---

## Installer Scripts

### The Core Pattern

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

### require_admin

Fail immediately with a clear message if not running as administrator. Put this at the very top.

```
require_admin "Please run this installer as Administrator."
```

### confirm

A cleaner single-line yes/no gate:

```
confirm "Delete all logs? (y/N)" else exit
confirm "Overwrite backup? (y/N)" else say "Skipped."
```

### make shortcut

```
make shortcut "My App" to "C:/MyApp/app.exe" on desktop
make shortcut "My App" to "C:/MyApp/app.exe" on startmenu
make shortcut "My App" to "C:/MyApp/app.exe" on programs
```

### registry (Windows only)

```
# Write
registry set HKCU\Software\MyApp Theme "Dark"
registry set HKCU\Software\MyApp Version 2

# Read
global_variable = theme
registry get HKCU\Software\MyApp Theme to theme

# Check existence
global_variable = installed
registry exists HKCU\Software\MyApp to installed

# Delete
registry delete HKCU\Software\MyApp Theme     # one value
registry delete HKCU\Software\MyApp           # entire key
```

Supported hives: `HKCU`, `HKLM`, `HKCR`, `HKU`, `HKCC`.

### install_package

```
install_package from winget "python"
install_package from apt "git"
install_package from brew "ffmpeg"
install_package from pip "requests"
install_package from npm "typescript"
```

Supported managers: `winget`, `choco`, `scoop`, `apt`, `brew`, `dnf`, `yum`, `pacman`, `pip`, `npm`.

### do build — Compile to EXE

```
pip install pyinstaller
python doscript.py build installer.do --onefile
python doscript.py build installer.do --onefile --windowed
python doscript.py build installer.do --icon app.ico --title "My App Installer"
python doscript.py build installer.do --output build/
```

### Installer Checklist

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

---

## Strings and Text Helpers

| Helper | What it returns |
|---|---|
| `length(text)` | Number of characters |
| `trim(text)` | Text with leading/trailing whitespace removed |
| `lower(text)` | Lowercase text |
| `upper(text)` | Uppercase text |
| `replace(text, old, new)` | Text with all matches replaced |

```
global_variable = raw_name, clean_name, loud_name

raw_name = "  Alice Smith  "
clean_name = trim(raw_name)
loud_name = upper(clean_name)

say 'Clean: {clean_name}'
say 'Upper: {loud_name}'
say 'Chars: {length(clean_name)}'
```

Helpers can be nested:

```
global_variable = result
result = upper(trim("  hello world  "))
say '{result}'    # HELLO WORLD
```

**Normalising user input:**

```
global_variable = answer, normalized
ask answer "Continue? (yes/no)"
normalized = lower(trim(answer))

if normalized == "yes"
    say "Continuing..."
end_if
```

---

## Safer Command Execution

DoScript has two ways to run system commands:

- `execute_command` — safer, passes arguments directly without shell interpretation
- `run` — flexible, but uses the system shell

```
# Prefer execute_command
execute_command "git" "status"
execute_command "python" "-m" "http.server" "8000"

# Use run only when you specifically need shell behavior
run "dir"
run "echo Hello > out.txt"
```

**Rule of thumb:** Use `execute_command` for programs and arguments. Use `run` only when you intentionally need the shell.

---

## Data: JSON and CSV

### JSON — Read and Write

```
global_variable = cfg

json_read "config.json" to cfg
json_write cfg to "config.json"
```

### json_get / json_set

Use dot notation to reach keys inside nested objects:

```
global_variable = cfg, name, port

json_read "config.json" to cfg
json_get cfg "user.name" to name
json_get cfg "server.port" to port

json_set cfg "version" "2.0"
json_set cfg "user.name" "Alice"

json_write cfg to "config.json"
```

### Subscript Notation `[]`

```
global_variable = cfg, tags, val

json_read "config.json" to cfg

val = cfg["version"]
val = cfg["user"]["name"]    # chains work naturally
val = tags[0]                # zero-based list access

say 'Version: {cfg["version"]}'

cfg["version"] = "2.0"
json_write cfg to "config.json"
```

### CSV

```
global_variable = data, value

csv_read "data.csv" to data
csv_get data row 0 "email" to value
csv_write data to "output.csv"
```

### List Operations

```
global_variable = items, first, count

items = split("a,b,c", ",")
list_add items "d"

count = list_length(items)    # 4
first = list_get(items, 0)    # "a"

for_each item in items
    say 'Item: {item}'
end_for
```

---

## Interactive UI

### menu — Numbered Option Picker

```
global_variable = theme
menu theme from "Choose a theme" "Dark" "Light" "System default"
say 'Theme set to: {theme}'
```

The user can type a number or enough of the option text to be unambiguous.

### input_password — Hidden Password Input

```
global_variable = pw
input_password pw "Database password:"
```

> **Never** use `ask` for passwords — it echoes input to the screen.

### select_path — CLI Filesystem Navigator

```
global_variable = install_dir
select_path install_dir "Choose install folder" from '{appdata}' folders
say 'Installing to: {install_dir}'
```

| Clause | Meaning |
|---|---|
| `from "path"` | Starting directory |
| `files` | Show only files |
| `folders` | Show only folders |
| `both` | Show files and folders (default) |

At the prompt: enter a number to navigate, `..` to go up, a full path to jump directly, `0` to select the current folder.

### progress_bar — Live CLI Progress Bar

```
global_variable = done, total
total = 200
done = 0

for_each file_in deep
    done = done + 1
    progress_bar done of total "Processing"
    copy file to "backup"
end_for

progress_bar done    # call without "of total" when finished, to fix the cursor
```

### notify — Desktop Notification

```
notify "Backup" "Your backup completed successfully."
notify "Done!"                  # title defaults to "DoScript"
```

---

## Scheduling and Debugging

### schedule

Register a `.do` script with the OS native scheduler (Windows Task Scheduler or `crontab`).

```
schedule "cleanup.do" at "23:00"           # run once today
schedule "check.do" in 15 minutes          # run once in 15 minutes
schedule "backup.do" daily at "03:00"      # run daily
schedule "report.do" on "2026-12-01" at "09:00"   # run on a specific date
```

Scheduling the same script again **replaces** the previous entry — no duplicate tasks pile up.

### debug — Interactive Breakpoint Console

```
global_variable = name, count
name = "Alice"
count = 42

debug "before the loop"

loop 5 as i
    say 'i = {i}'
end_loop
```

When the breakpoint triggers, the script pauses and opens the `doscript-runtime>` console.

**Console commands at a breakpoint:**

| Command | What it does |
|---|---|
| `vars` | Print all current variable values |
| `set <var> <value>` | Override a variable |
| `eval <expr>` | Evaluate an expression |
| `run <statement>` | Execute a single DoScript statement |
| `continue` | Resume the script |

### Version Declaration

Put this on the **first line** to declare which interpreter version a script requires:

```
<doscript=0.6.14>

say "Script body starts here."
```

| Situation | Behaviour |
|---|---|
| Exact match | Runs silently |
| Script is older than interpreter | Runs with a hint |
| Script is newer than interpreter | Refuses with a clear error |
| Tag absent | Runs normally — no check |

### CLI Flags

| Flag | Effect |
|---|---|
| `--dry-run` | Preview all file/network/scheduling actions without executing |
| `--verbose` | Extra runtime information |
| `--debug` | Debug header on startup + verbose output |
| `--version` | Print interpreter version |
| `--help` | Full reference of flags and examples |

---

## Modules and Packages

DoScript has three ways to share and reuse code.

### include — Local File Inclusion

```
include "helpers.do"

# Functions from helpers.do are now available
greet("Alice")
```

Best for splitting one large script across readable files within a single project.

### use — Project-Local Modules

Searches: (1) same folder as your script, (2) a `modules/` subfolder, (3) `~/DoScript/modules/`.

```
use "net.do"
use "files.do"
```

**Recommended project layout:**

```
my-project/
  installer.do
  modules/
    net.do
    files.do
```

### install_module — Global Package Manager

```
python doscript.py install_module math
python doscript.py install_module cli
python doscript.py install_module --dir ./modules datetime
```

Modules are installed to `C:\Server-lab\DoScript\modules\` (Windows) or `~/DoScript/modules/`.

### use_module — Load an Installed Module

```
use_module "math"
use_module "cli"
```

If the module is not installed, DoScript prints a clear error with the install command.

| | `use` | `use_module` |
|---|---|---|
| Looks in global install dir | ❌ | ✅ |
| Looks in local `modules/` | ✅ | ✅ |
| Helpful "install this" error | ❌ | ✅ |

**Rule:** `use` for your own project files, `use_module` for anything from the public registry.

### run_from_web

```
run_from_web cleaner.do
run_from_web tools/setup-python.do
```

Best for one-off community scripts. For persistent reuse, install with `install_module` instead.

### do_new — Launch a Script as a Separate Process

```
do_new "cleanup.do"
do_new "report.do"
```

Variables do **not** share — fully isolated from the parent script.

### Which to use?

| Scenario | Tool |
|---|---|
| Split a big script into readable files | `include` |
| Share helpers across scripts in one project | `use` |
| Use a published community module | `install_module` + `use_module` |
| Run a one-off community utility | `run_from_web` |
| Chain independent scripts | `do_new` |

### Official Modules

| Module | What it provides |
|---|---|
| `math` | Rounding, clamping, factorial, Fibonacci, GCD/LCM |
| `strings` | Padding, repetition, truncation, validation |
| `files` | Path helpers, `ensure_folder`, `backup_file`, file size labels |
| `datetime` | Greetings, weekday/month names, leap years, elapsed time |
| `network` | Connectivity checks, URL encoding, HTTP status labels |
| `system` | OS detection, process control, env vars, admin check |
| `lists` | Search, sum, min/max/average, join, fill |
| `cli` | Banners, step output, `✓`/`⚠`/`✗` indicators, prompts |

---

## External Variables (.slev)

`.slev` files (Server-lab External Variable) let you store key-value configuration outside your `.do` scripts and load them at runtime.

### import_variables

```
import_variables "config.slev"
import_variables '{appdata}/MyApp/settings.slev'
```

All key-value pairs become global variables immediately — no `global_variable` declaration needed.

### .slev File Format

```
# config.slev
api_key   = supersecret123
base_url  = https://api.example.com
port      = 8080
timeout   = 30.5
debug     = false
app_name  = "My Application"
```

**Type coercion:**

| Value looks like | Imported as |
|---|---|
| `8080` (integer) | number |
| `30.5` (float) | float |
| `true` / `false` | boolean |
| Anything else | string (quotes stripped if present) |

### Common Uses

**Keeping secrets out of scripts:**

```
# secrets.slev  ← add to .gitignore
db_password = hunter2
api_key     = sk-abc123xyz
```

```
# deploy.do
import_variables "secrets.slev"
http_post '{base_url}/deploy' '{"key":"{api_key}"}' to response
```

**Sharing config between multiple scripts:**

```
# shared.slev
app_name    = MyApp
version     = 2.1
install_dir = C:/Program Files/MyApp
```

**Environment-specific deployments:**

```
# deploy.do
global_variable = env
ask env "Deploy to which environment? (dev/prod)"
import_variables '{env}.slev'
say 'Deploying to {base_url}...'
```

---

## Tips, Patterns, and Gotchas

### Quote Gotcha — The #1 Mistake

Using double quotes when you need variable interpolation produces silent wrong output.

```
global_variable = name
name = "Alice"

say "Hello {name}"    # ❌  prints: Hello {name}
say 'Hello {name}'    # ✅  prints: Hello Alice
```

### Always Skip .do Files in Loops

```
for_each file_in here
    if_ends_with ".do"
        continue
    end_if
    # ... process everything else
end_for
```

### Deleting Safely

```
if exists("temp.zip")
    delete "temp.zip"
end_if
```

### --dry-run Mode

Always test with `--dry-run` before running any script that moves, deletes, or downloads anything.

```
python doscript.py sort-downloads.do --dry-run
```

### Built-in Expressions

| Expression | What it does |
|---|---|
| `exists("path")` | Check if a file/folder exists |
| `contains(text, "word")` | Case-insensitive substring check |
| `contains_case(text, "Word")` | Case-sensitive substring check |
| `notcontains(text, "word")` | True if text does NOT contain word |
| `startswith(text, "prefix")` | Prefix check |
| `endswith(text, ".txt")` | Suffix check |
| `extension(filename)` | Returns `.txt`, `.pdf`, etc. |
| `read_file("path")` | Returns file contents as a string |
| `split(text, ",")` | Splits string into a list |

### random_number and random_string

```
global_variable = rnd
random_number 1000 9999 to rnd
make file 'temp_{rnd}.txt'

random_string 8 to rnd
make folder '{rnd}_session'
```

### Script Organisation Tips

- Put `global_variable` declarations at the **top** of your script
- Use `say ""` (empty say) to add blank lines for readability
- Use `pause` at the **end** of installer/interactive scripts
- Use `log` / `warn` / `error` instead of `say` for unattended scripts
- Break big scripts into multiple `.do` files and use `include` or `do_new`

### Path Separators

```
# Both work on Windows — forward slashes are more readable
make folder "C:/Users/User/Downloads"   # ✅ preferred
make folder "C:\Users\User\Downloads"   # ✅ also works
```

### Quick Reference — When to Use Which Feature

| Task | Use |
|---|---|
| Sort files by type | `for_each` + `else_if file_ext ==` |
| Delete old files | `for_each … older_than N days` |
| Find files with content | `if_file_contains "keyword"` |
| Backup a folder | `zip "folder" to 'backup_{today}.zip'` |
| Download + install | `download` → `unzip` → `path add` → `make shortcut` |
| Read/write settings | `json_read` / `json_set` / `json_write` |
| Reusable logic | `function` / `use "module.do"` |
| Run safely first | `--dry-run` flag |
| Distribute as EXE | `python doscript.py build installer.do` |

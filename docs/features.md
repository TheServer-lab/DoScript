# DoScript — Feature Reference
> Current version: **0.6.13**

---

## Table of Contents

1. [Comments](#1-comments)
2. [Variables](#2-variables)
3. [Strings and Interpolation](#3-strings-and-interpolation)
4. [Output and Input](#4-output-and-input)
5. [Built-in Read-Only Variables](#5-built-in-read-only-variables)
6. [Control Flow](#6-control-flow)
7. [Loops](#7-loops)
8. [Error Handling](#8-error-handling)
9. [File Operations](#9-file-operations)
10. [File Iteration — `for_each`](#10-file-iteration--for_each)
11. [Archives](#11-archives)
12. [Data — JSON and CSV](#12-data--json-and-csv)
13. [Network](#13-network)
14. [System](#14-system)
15. [Process Execution](#15-process-execution)
16. [Functions](#16-functions)
17. [Macros](#17-macros)
18. [String Helpers](#18-string-helpers)
19. [List Operations](#19-list-operations)
20. [Map and Array Subscripts](#20-map-and-array-subscripts)
21. [Modules — `use` and `include`](#21-modules--use-and-include)
22. [Script Chaining](#22-script-chaining)
23. [Environment Variables](#23-environment-variables)
24. [PATH Management](#24-path-management)
25. [Windows Registry](#25-windows-registry)
26. [Shortcuts](#26-shortcuts)
27. [Package Installation](#27-package-installation)
28. [Web Scripts — `run_from_web`](#28-web-scripts--run_from_web)
29. [Installer Utilities](#29-installer-utilities)
30. [Random Values](#30-random-values)
31. [Timing](#31-timing)
32. [CLI Arguments](#32-cli-arguments)
33. [Dry-Run Mode](#33-dry-run-mode)
34. [Building EXEs — `do build`](#34-building-exes--do-build)

---

## 1. Comments

```
# This is a comment
// This is also a comment
say "https://example.com"   # URLs inside strings are safe
```

---

## 2. Variables

All variables must be declared before use with `global_variable`. Multiple variables can be declared on one line.

```
global_variable = name
global_variable = firstName, lastName, age
```

Assign with `=`:

```
name = "Alice"
age = 30
active = true
```

Variables are loosely typed — they hold strings, numbers, or booleans. `ask` auto-declares its variable; no `global_variable` needed.

Inside functions, use `local_variable` instead:

```
function greet name
    local_variable = msg
    msg = 'Hello, {name}!'
    say msg
end_function
```

---

## 3. Strings and Interpolation

| Quote type | Behaviour |
|---|---|
| `"double"` | Literal — no variable substitution |
| `'single'` | Interpolated — `{var}` is replaced with the variable's value |

```
name = "Alice"
say "Hello {name}"    # prints: Hello {name}
say 'Hello {name}'    # prints: Hello Alice
```

Subscript expressions also work inside single-quoted strings:

```
say 'Version: {cfg["version"]}'
say 'First item: {tags[0]}'
```

**Exception:** Built-in read-only variables (`downloads`, `today`, `username`, etc.) are resolved even inside double-quoted strings, since they are system constants.

---

## 4. Output and Input

```
say "Hello!"                   # print to console
say 'Your name is: {name}'     # interpolated
say 42                         # print a number
say name                       # print variable value

log "Process started"          # [INFO] Process started
warn "Disk almost full"        # [WARN] Disk almost full
error "File not found"         # [ERROR] File not found

ask answer "What is your name?"   # prompt user, store in 'answer'
```

---

## 5. Built-in Read-Only Variables

These are always available. Never declare or overwrite them.

### Time variables

| Variable | Value |
|---|---|
| `today` | Current date, e.g. `2026-04-18` |
| `now` | Current time, e.g. `14:30:00` |
| `year` | Current year |
| `month` | Current month (number) |
| `day` | Current day (number) |
| `hour` / `minute` / `second` | Time components |
| `time` | Unix timestamp |

### Path variables (cross-platform)

| Variable | Windows | macOS / Linux |
|---|---|---|
| `user_home` | `%USERPROFILE%` | `$HOME` |
| `username` | `%USERNAME%` | `$USER` |
| `downloads` | `~\Downloads` | `~/Downloads` |
| `desktop` | `~\Desktop` | `~/Desktop` |
| `documents` | `~\Documents` | `~/Documents` |
| `appdata` | `%APPDATA%` | `~/.config` |
| `temp` | `%TEMP%` | `/tmp` |

```
say 'Hello, {username}!'
make folder '{downloads}/Sorted'
make file '{temp}/run.log' with "Started"
```

### CLI arguments

`arg1` through `arg32` — values passed to the script on the command line.

```
python doscript.py deploy.do production 443
# arg1 = "production", arg2 = "443"
```

---

## 6. Control Flow

```
if age >= 18
    say "Adult"
else_if age >= 13
    say "Teenager"
else
    say "Child"
end_if
```

Operators: `==`, `!=`, `<`, `>`, `<=`, `>=`, `and`, `or`, `not`.

Nested `if` blocks are supported. `else_if` also works inside `for_each` loops.

---

## 7. Loops

### `repeat`

```
repeat 5
    say "Hello!"
end_repeat
```

### `loop`

```
loop 3
    say "Looping..."
end_loop

loop 3 as i
    say 'Iteration {i}'
end_loop

loop forever
    say "Runs until Ctrl+C"
end_loop
```

### `break` and `continue`

```
loop forever
    i = i + 1
    if i == 5
        break
    end_if
end_loop

for_each file_in here
    if_ends_with ".do"
        continue
    end_if
    say 'Processing: {file_name}'
end_for
```

### `for_each_line`

Iterates over lines of a text file:

```
global_variable = line

for_each_line line in "servers.txt"
    ping line
end_for
```

---

## 8. Error Handling

```
try
    download "https://example.com/file.zip" to "file.zip"
catch NetworkError
    say "Download failed."
catch FileError
    say "File problem."
catch
    say "Something unexpected happened."
end_try
```

| Error type | Raised by |
|---|---|
| `NetworkError` | `download`, `http_get`, `ping`, `run_from_web` |
| `FileError` | `copy`, `move`, `delete`, file reads |
| `ProcessError` | `run`, `execute_command`, `kill` |
| `DataError` | `json_read`, `csv_read` |
| *(no type)* | Catches any error |

---

## 9. File Operations

### Create

```
make folder "output"
make folder "C:/Projects/MyApp/logs"

make file "notes.txt"
make file "notes.txt" with "Hello, World!"
make file 'log_{today}.txt' with "Started"
```

Multi-line file content with variable interpolation:

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

### Copy, Move, Rename, Delete

```
copy "source.txt" to "backup/source.txt"
move file to "Documents"
move file to "renamed_file.txt"
rename "draft.txt" to "final.txt"
delete "temp.txt"
delete "C:/Temp/old_logs"     # deletes folder recursively
```

### Check and Read

```
if exists("config.json")
    say "Found!"
end_if

global_variable = text
read_content "notes.txt" into text

text = read_file("notes.txt")         # in expressions
```

### Find and Replace in File

```
replace_in_file "config.txt" "localhost" "192.168.1.100"
replace_regex_in_file "log.txt" "\\d{4}-\\d{2}-\\d{2}" "REDACTED"
```

---

## 10. File Iteration — `for_each`

Iterate over files or folders in a directory. The prefix before `_in` sets the variable names.

```
for_each file_in here            # current directory
for_each file_in deep            # recursive
for_each file_in "C:/Downloads"  # specific path
for_each folder_in here          # directories only (prefix starts with 'folder' or 'dir')
```

### Auto-injected variables

Replace `file` with your chosen prefix.

| Variable | Contains |
|---|---|
| `file_name` | Filename, e.g. `report.pdf` |
| `file_path` | Absolute path |
| `file_ext` | Extension including dot, e.g. `.pdf` |
| `file_size` | Size in bytes |
| `file_size_kb` | Size in KB |
| `file_size_mb` | Size in MB |
| `file_is_dir` | `true` if it's a folder |
| `file_is_empty` | `true` if size is 0 |
| `file_created` | Creation timestamp (Unix) |
| `file_modified` | Last modified timestamp (Unix) |
| `file_is_old_days` | Age in days |
| `file_is_old_hours` | Age in hours |
| `file_is_old_months` | Age in months |
| `file_content` | Full text content (text files only) |

### Age filters

```
for_each old_file_in here older_than 30 days
    delete old_file_path
end_for

for_each f_in deep newer_than 1 hour
    log 'Recently changed: {f_name}'
end_for
```

Supported units: `seconds`, `minutes`, `hours`, `days`, `months`, `years`.

### `{loop_count}`

After any `for_each`, `loop_count` holds the number of items iterated:

```
for_each file_in here
    copy file to "backup"
end_for
say 'Copied {loop_count} files.'
```

### File content checks

```
for_each file_in here
    if_ends_with ".txt"
        say 'Text file: {file_name}'
    end_if

    if_file_contains "ERROR"
        move file to "errors"
    end_if

    if_file_not_contains "reviewed"
        say 'Not reviewed: {file_name}'
    end_if
end_for
```

### Iterating a list variable

```
global_variable = fruits, fruit
fruits = split("apple,banana,mango", ",")

for_each fruit in fruits
    say 'Fruit: {fruit}'
end_for
```

---

## 11. Archives

```
zip "my_folder" to "my_folder.zip"
zip "report.pdf" to "report.zip"

unzip "archive.zip"
unzip "archive.zip" to "extracted"

global_variable = contents
zip_list "archive.zip" to contents
say contents
```

---

## 12. Data — JSON and CSV

### JSON

```
global_variable = cfg

json_read "config.json" to cfg
json_read config_path to cfg          # variable path
json_read 'data/{today}.json' to cfg  # interpolated path

json_get cfg "user.name" to name      # dot notation for nested keys
json_set cfg "user.name" "Alice"      # write a value (dot notation)
json_set cfg "version" "2.0"

json_write cfg to "config.json"
json_write cfg to 'backups/config_{today}.json'
```

### CSV

```
global_variable = data, value

csv_read "data.csv" to data
csv_get data row 0 "email" to value
csv_write data to "output.csv"
```

---

## 13. Network

```
download "https://example.com/file.zip" to "file.zip"
download "https://example.com/file.zip" to '{downloads}/file.zip'

global_variable = response
http_get  "https://api.example.com/status" to response
http_post "https://api.example.com/data" "{\"key\":\"value\"}" to response
http_put  "https://api.example.com/item/1" "{\"name\":\"new\"}" to response
http_delete "https://api.example.com/item/1" to response

upload "report.pdf" to "https://example.com/upload"

ping "8.8.8.8"

open_link "https://github.com/TheServer-lab/DoScript"
```

---

## 14. System

```
global_variable = cpu, mem, disk_usage

system_cpu to cpu
system_memory to mem
system_disk "C:/" to disk_usage
system_disk user_home to disk_usage    # variable path

say 'CPU: {cpu}%  RAM: {mem}%  Disk: {disk_usage}%'
```

Check if a process is running:

```
global_variable = running
running = is_running("notepad.exe")

if not is_running("myservice")
    run "myservice --start"
end_if
```

---

## 15. Process Execution

```
run "git status"                       # via shell
run "echo Hello > out.txt"            # shell redirection works

execute_command "git" "status"         # direct, no shell parsing (safer)
execute_command "python" "-m" "http.server" "8000"

kill "notepad.exe"

do_new "cleanup.do"                    # launch another script in a new instance
```

Capture output:

```
global_variable = output, code
output = capture "git log --oneline -5"
code = run "my-script.sh"             # exit code stored when assigned
```

---

## 16. Functions

```
function greet name
    say 'Hello, {name}!'
end_function

greet("Alice")        # call as a statement (return value discarded)

global_variable = result
result = add(10, 5)   # call in an expression
```

```
function add a b
    return a + b
end_function

function sum_of_squares a b
    local_variable = sa, sb
    sa = square(a)
    sb = square(b)
    return sa + sb
end_function
```

---

## 17. Macros

Named blocks with no parameters and no return value. Called with `run`.

```
make a_command print_separator
    say "--------------------"
end_command

run "print_separator"
say "Section One"
run "print_separator"
```

---

## 18. String Helpers

```
global_variable = result

result = trim("  hello  ")         # "hello"
result = lower("HELLO")            # "hello"
result = upper("hello")            # "HELLO"
result = replace("hi there", "there", "world")   # "hi world"
result = length("hello")           # 5
```

Helpers can be nested:

```
result = upper(trim("  hello world  "))   # "HELLO WORLD"
```

Built-in expression functions:

| Function | Description |
|---|---|
| `exists("path")` | Check if file/folder exists |
| `contains(text, "word")` | Case-insensitive substring check |
| `contains_case(text, "Word")` | Case-sensitive substring check |
| `notcontains(text, "word")` | True if text does NOT contain word |
| `startswith(text, "prefix")` | Prefix check |
| `endswith(text, ".txt")` | Suffix check |
| `extension(filename)` | Returns `.txt`, `.pdf`, etc. |
| `read_file("path")` | Returns file contents as a string |
| `split(text, ",")` | Splits a string into a list |

---

## 19. List Operations

```
global_variable = items, first, count

items = split("a,b,c", ",")
list_add items "d"

count = list_length(items)    # 4
first = list_get(items, 0)    # "a"
```

---

## 20. Map and Array Subscripts

Read and write nested JSON objects and lists using `[]` notation.

```
global_variable = cfg, tags, val

json_read "config.json" to cfg

# Read
val = cfg["version"]
val = cfg["user"]["name"]
val = tags[0]

# Read inside interpolated strings
say 'Version: {cfg["version"]}'
say 'Name: {cfg["user"]["name"]}'

# Write
cfg["version"] = "2.0"
cfg["user"]["name"] = "Bob"
tags[1] = "BETA"

json_write cfg to "config.json"
```

---

## 21. Modules — `use` and `include`

### `use` — module system

Searches for the file in order: script folder → `./modules/` → `~/DoScript/modules/`.

```
use "net.do"
use "files.do"
```

Recommended project layout:

```
my-project/
  installer.do
  modules/
    net.do
    files.do
```

### `include` — relative include

Includes a file by path relative to the current script. Each file is included at most once.

```
include "helpers.do"
```

---

## 22. Script Chaining

```
do_new "cleanup.do"     # launch in a new DoScript instance
do_new "backup.do"
do_new "report.do"
```

---

## 23. Environment Variables

```
set_env "MY_APP_HOME" to "C:/MyApp"

global_variable = path
path = get_env("MY_APP_HOME")
say 'App is at: {path}'
```

---

## 24. PATH Management

```
path add "C:/MyApp/bin"           # add to user PATH
path add --system "C:/MyApp/bin"  # add to system PATH (requires admin)
path remove "C:/OldApp/bin"
```

On Windows, broadcasts `WM_SETTINGCHANGE` so the new PATH takes effect in open terminals immediately.

---

## 25. Windows Registry

Read, write, delete, and check Windows registry keys and values.

```
registry set HKCU\Software\MyApp Theme "Dark"
registry set HKCU\Software\MyApp Version 2

global_variable = theme, installed
registry get    HKCU\Software\MyApp Theme to theme
registry exists HKCU\Software\MyApp to installed
registry delete HKCU\Software\MyApp Theme     # delete one value
registry delete HKCU\Software\MyApp           # delete entire key
```

Supported hives: `HKCU`, `HKLM`, `HKCR`, `HKU`, `HKCC`. Windows only — raises a clear error on other platforms. Respects `--dry-run`.

---

## 26. Shortcuts

Create desktop or Start Menu shortcuts on Windows, macOS, and Linux.

```
make shortcut "My App" to "C:/Program Files/MyApp/app.exe"
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on desktop
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on startmenu
make shortcut "My App" to '{appdata}\MyApp\app.exe' on programs
```

| Placement | Windows | macOS | Linux |
|---|---|---|---|
| `desktop` | `.lnk` via PowerShell | Finder alias | `.desktop` file |
| `startmenu` / `programs` | Start Menu `.lnk` | `/Applications` | `~/.local/share/applications` |

No external dependencies required on any platform.

---

## 27. Package Installation

Install software from any supported package manager:

```
install_package from winget "python"
install_package from apt "git"
install_package from brew "ffmpeg"
install_package from pip "requests"
install_package from npm "typescript"
install_package from choco "vlc"
install_package from scoop "curl"
install_package from dnf "gcc"
install_package from pacman "vim"
```

Supported managers: `winget`, `choco`, `scoop`, `apt` / `apt-get`, `brew`, `dnf`, `yum`, `pacman`, `pip` / `pip3`, `npm`. Raises `ProcessError` if the manager is not found. Respects `--dry-run`.

---

## 28. Web Scripts — `run_from_web`

Fetch and run a `.do` script from [TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage):

```
run_from_web cleaner.do
run_from_web git-setup.do
run_from_web tools/setup-python.do
```

The `.do` extension is optional. Single-quoted interpolation works:

```
global_variable = tool
tool = "cleaner"
run_from_web '{tool}.do'
```

The fetched script shares the calling script's variable scope — variables it sets are available after it returns. Respects `--dry-run`.

---

## 29. Installer Utilities

```
require_admin "Please run this installer as Administrator."

confirm "Delete all logs? (y/N)" else exit
confirm "Overwrite backup? (y/N)" else say "Skipped."
```

`require_admin` fails immediately with a clear message if the script is not running as admin (Windows) or root (Unix). `confirm` prompts for `y`/`yes`; anything else runs the `else` branch.

---

## 30. Random Values

```
global_variable = rnd

random_number 1000 9999 to rnd
make file 'temp_{rnd}.txt'

random_string 8 to rnd
make folder '{rnd}_session'

random_choice "apple,banana,mango" to rnd
```

---

## 31. Timing

```
pause            # wait for user to press Enter
wait 2           # wait 2 seconds
wait 0.5         # wait half a second

exit             # exit with code 0
exit 1           # exit with code 1
```

---

## 32. CLI Arguments

Pass arguments after the script name:

```
python doscript.py deploy.do production 443
```

Access them as `arg1` through `arg32`:

```
say 'Environment: {arg1}'
say 'Port: {arg2}'
```

---

## 33. Dry-Run Mode

Run any script with `--dry-run` to preview destructive operations without executing them. File changes, downloads, registry writes, package installs, and shortcuts all print `[DRY]` messages instead of running.

```
python doscript.py sort-downloads.do --dry-run
```

---

## 34. Building EXEs — `do build`

Compile any `.do` script into a standalone distributable executable. Requires `pip install pyinstaller` once.

```
python doscript.py build installer.do
python doscript.py build installer.do --onefile
python doscript.py build installer.do --onefile --windowed --icon app.ico
python doscript.py build installer.do --title "My App Installer" --output build/
```

| Flag | Effect |
|---|---|
| `--onefile` | Single portable EXE |
| `--windowed` | No console window |
| `--icon <file>` | Application icon |
| `--title <text>` | Runtime banner title |
| `--output <dir>` | Output directory (default: `./dist`) |

The built EXE embeds the DoScript runtime and the `.do` script. It includes a **DoScript Runtime Console** — an interactive shell that activates on crash and on demand:

```
doscript-runtime> doscript     # show version and build metadata
doscript-runtime> vars         # dump all current variables
doscript-runtime> trace on     # enable verbose tracing
doscript-runtime> restart      # re-run the embedded script
doscript-runtime> link         # open the DoScript repo in a browser
doscript-runtime> exit
```

Works correctly when DoScript itself is distributed as a compiled `do.exe`.

# DoScript — Automation for Humans

**DoScript** is a small, safe, human-readable scripting language built for
system automation. Think *Batch 2.0*: clean syntax, built-in safety, and
powerful enough to write real installers, file sorters, and deployment tools
— without ever needing to know Python or PowerShell.

```
ask name "What's your project called?"
make folder '{name}'
download "https://example.com/starter.zip" to 'starters/{name}.zip'
unzip 'starters/{name}.zip' to '{name}'
say 'Done! Your project is ready in /{name}'
```

---

## Why DoScript?

| | Batch | PowerShell | DoScript |
|---|---|---|---|
| Beginner-friendly | ⚠️ | ❌ | ✅ |
| Human-readable syntax | ❌ | ❌ | ✅ |
| Built-in dry-run | ❌ | ❌ | ✅ |
| Structured error handling | ❌ | ✅ | ✅ |
| File metadata in loops | ❌ | ✅ | ✅ |
| HTTP client built in | ❌ | ✅ | ✅ |
| Distributable as .exe | ❌ | ⚠️ | ✅ |

---

## Highlights

- **Human-readable DSL** — scripts read like plain English instructions
- **`--dry-run` built in** — simulate destructive operations safely before running them
- **Rich file loops** — iterate files with auto-injected metadata: name, size, extension, age, content, and more
- **Structured error handling** — `try/catch NetworkError`, `FileError`, `ProcessError`, `DataError`
- **Full HTTP client** — `download`, `http_get`, `http_post`, `upload`, `ping` out of the box
- **Real functions** — parameters, return values, and local variable scoping
- **Modular scripts** — `include` libraries, chain scripts with `do_new`
- **Clear errors** — every error reports the file name, line number, and source line
- **Distributable** — ships as `doscript.exe`, embeds easily in any toolchain

---

## Install

### Prebuilt EXE (Windows)
Download the latest installer from the [Releases](../../releases) page and run it.

```
do script.do
```

### From Source
Requires **Python 3.8+**:

```
python doscript.py myscript.do
```

---

## Usage

```
do <script.do> [--dry-run] [--verbose] [args...]
```

| Flag | What it does |
|---|---|
| `--dry-run` | Simulates all destructive operations — nothing is written, moved, or deleted |
| `--verbose` | Prints extra execution detail |
| `arg1`…`arg32` | CLI arguments available inside the script |

---

## The Language at a Glance

### Variables & Output
```
global_variable = name, age

name = "Alice"
age  = 30

say 'Hello, {name}! You are {age} years old.'
ask answer "Continue? (y/n)"
```

> Use **single quotes** for strings with `{variables}`. Double quotes are always literal.

### Control Flow
```
if age >= 18 and age < 65
    say "Working age."
end_if

loop 3
    say "Retrying..."
    wait 1
end_loop
```

### File Operations
```
make folder "output"
copy "report.pdf" to "backup/report.pdf"
zip "output" to 'output_{today}.zip'

for_each file_in here
    if_ends_with ".log"
        if file_is_old_days > 30
            delete file_path
        end_if
    end_if
end_for
```

### Networking
```
try
    download "https://example.com/app.zip" to "app.zip"
    say "Download complete!"
catch NetworkError
    say "Check your connection and try again."
    exit 1
end_try
```

### Functions
```
function greet name
    say 'Hello, {name}!'
end_function

greet("World")
```

---

## A Real Example — Installer Script

```
say "==========================="
say "    MyApp Installer v1.0"
say "==========================="

global_variable = confirm

ask confirm "Install MyApp? (y/n)"

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

    say "Done! Run 'myapp' from any terminal."
else
    say "Installation cancelled."
end_if

pause
```

---

## Safety Model

DoScript is designed so that mistakes are hard to make and easy to catch.

- **`--dry-run`** replaces every destructive operation with a `[DRY]` log message — nothing is touched
- **Explicit destructive commands** (`delete`, `move`) are clearly named so intent is visible
- **`try/catch`** with typed errors means network and file failures never silently crash a script
- **Structured logging** with `log`, `warn`, and `error` makes unattended scripts easy to monitor

---

## Learn DoScript

The [`/learn`](learn/) folder contains eight step-by-step lessons:

| Lesson | Topic |
|---|---|
| [01 — Basics](learn/01-basics.md) | Variables, `say`, `ask`, comments, quote rules |
| [02 — Control Flow](learn/02-control-flow.md) | `if/else`, `loop`, `repeat`, `break`, `try/catch` |
| [03 — Files](learn/03-files.md) | `make`, `copy`, `move`, `delete`, `zip`, `read_content` |
| [04 — for_each](learn/04-for-each.md) | File iteration, metadata variables, `if_ends_with` |
| [05 — Functions](learn/05-functions.md) | Functions, macros, `include` |
| [06 — Network](learn/06-network.md) | `download`, `http_get/post`, `ping`, `upload` |
| [07 — Installers](learn/07-installers.md) | Writing real installer scripts end-to-end |
| [08 — Tips & Patterns](learn/08-tips-and-patterns.md) | Community patterns, common gotchas |

---

## License

[Server-Lab Open-Control License (SOCL) 1.0](LICENSE)

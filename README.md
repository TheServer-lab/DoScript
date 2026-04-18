# DoScript — Human-Friendly Automation & Installer Language

**DoScript** is a readable scripting language for automation, installers, deployment, and system tasks.

It is designed to feel like writing instructions instead of code:
- easy to read
- practical for real work
- safe to test with `--dry-run`
- powerful enough to build installers and standalone EXEs

```doscript
ask name "What's your project called?"

make folder '{name}'
download "https://example.com/starter.zip" to '{temp}/{name}.zip'
unzip '{temp}/{name}.zip' to '{name}'

say 'Done! Your project is ready in {name}'
```

---

## What DoScript is good at

DoScript is built for the kinds of tasks people do every day:

- creating and organizing files
- downloading and extracting packages
- writing installers
- adding shortcuts and PATH entries
- editing JSON, CSV, and text files
- scanning folders and sorting files
- running commands and checking system state
- packaging scripts into standalone `.exe` files

---

## Why DoScript?

| Feature | Batch | PowerShell | Python | DoScript |
|---|---|---|---|---|
| Beginner-friendly | ⚠️ | ❌ | ⚠️ | ✅ |
| Human-readable syntax | ❌ | ❌ | ❌ | ✅ |
| Built-in dry-run mode | ❌ | ❌ | ❌ | ✅ |
| File automation | ⚠️ | ✅ | ✅ | ✅ |
| HTTP / downloads built in | ❌ | ✅ | ✅ | ✅ |
| Installers are easy to write | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Build scripts into EXEs | ❌ | ⚠️ | ⚠️ | ✅ |
| Functions and modules | ❌ | ✅ | ✅ | ✅ |

---

## Current version

**DoScript v0.6.13**

Notable features include:

- `install_package from <manager> "<pkg>"`
- `use` and `include` modules
- JSON, CSV, archives, and network tools
- `make shortcut`
- registry support
- `require_admin`
- `confirm`
- list operations
- map and array subscripts
- `do build` for standalone EXEs
- built-in path variables like `downloads`, `desktop`, `documents`, `temp`, and `appdata`

---

## Install

### Windows users
Download the latest release from the project releases page and run the bundled executable.

### From source
Requires **Python 3.8+**.

```bash
python doscript.py myscript.do
```

---

## Usage

```bash
do <script.do> [--dry-run] [--verbose] [args...]
```

| Flag | What it does |
|---|---|
| `--dry-run` | Simulates destructive operations instead of executing them |
| `--verbose` | Prints extra execution detail |
| `arg1`…`arg32` | CLI arguments available inside the script |

---

## Quick examples

### Variables and output

```doscript
global_variable = name, age

name = "Alice"
age = 30

say 'Hello, {name}! You are {age} years old.'
ask answer "Continue? (y/n)"
```

### Control flow

```doscript
if age >= 18
    say "Adult"
else_if age >= 13
    say "Teenager"
else
    say "Child"
end_if
```

### Loops

```doscript
loop 3 as i
    say 'Retry {i}'
    wait 1
end_loop
```

### File operations

```doscript
make folder "output"
copy "report.pdf" to "backup/report.pdf"
zip "output" to 'output_{today}.zip'
```

### Network

```doscript
try
    download "https://example.com/app.zip" to "app.zip"
    say "Download complete!"
catch NetworkError
    say "Check your connection and try again."
end_try
```

### Functions

```doscript
function greet name
    say 'Hello, {name}!'
end_function

greet("World")
```

### Lists

```doscript
global_variable = items
items = split("apple,banana,mango", ",")

list_add items "orange"
say list_get(items, 0)
say list_length(items)
```

### JSON

```doscript
json_read "config.json" to cfg
json_set cfg "user.name" "Alice"
json_write cfg to "config.json"
```

### Installers

```doscript
require_admin "Please run as Administrator."

make folder "C:/MyApp"
download "https://example.com/myapp.zip" to "{temp}/myapp.zip"
unzip "{temp}/myapp.zip" to "C:/MyApp"
make shortcut "MyApp" to "C:/MyApp/app.exe" on desktop
path add "C:/MyApp/bin"
say "Installation complete!"
```

---

## Safety model

DoScript is designed to make mistakes easier to catch:

- `--dry-run` previews destructive actions
- `try/catch` handles file, network, process, and data errors
- explicit commands like `delete`, `move`, and `path add` make intent clear
- structured logging with `log`, `warn`, and `error` is built in

---

## Build EXEs

DoScript can compile `.do` scripts into standalone executables.

```bash
do build installer.do
do build installer.do --onefile
do build installer.do --onefile --windowed --icon app.ico
do build installer.do --title "My App Installer" --output build/
```

| Flag | Effect |
|---|---|
| `--onefile` | Single portable EXE |
| `--windowed` | No console window |
| `--icon <file>` | Application icon |
| `--title <text>` | Runtime title |
| `--output <dir>` | Output directory |

The generated EXE embeds the DoScript runtime and the script itself.

---

## Learning resources

The repository includes step-by-step lessons covering:

- basics
- control flow
- file operations
- file iteration
- functions and macros
- network commands
- installer patterns
- common gotchas
- strings and text helpers
- safer command execution
- newer features and workflow improvements

---

## License

**Server-Lab Open-Control License (SOCL) 1.0**

See `LICENSE`

# Lesson 15 — What's New in 0.6.15

Three new features: a module package manager, a `use_module` command, and
external variable files (`.slev`).

---

## `install_module` — Module Package Manager

Download and install a DoScript module from the official
[DoModule repository](https://github.com/TheServer-lab/DoModule) in one command:

```
python doscript.py install_module <name>
```

```
python doscript.py install_module math
python doscript.py install_module strings
python doscript.py install_module cli
```

Modules are fetched from:
```
https://github.com/TheServer-lab/DoModule/tree/main/module
```

And installed to:

| OS | Default install path |
|---|---|
| Windows | `C:\Server-lab\DoScript\modules` |
| macOS / Linux | `~/DoScript/modules/` |

Override the destination with `--dir`:

```
python doscript.py install_module math --dir ./modules
```

After installation, the module is available to any script on the machine via
`use_module`.

---

## `use_module` — Load an Installed Module

`use_module` loads an installed module and merges all of its functions,
variables, and declarations into the calling script's scope.

```
use_module "math"
use_module "cli"
use_module "datetime"
```

It is like `use`, but searches the global install directory first:

1. `C:\Program Files (x86)\DoScript\modules\` (Windows) / `~/DoScript/modules/` (Unix)
2. A `modules/` subfolder next to your script
3. `~/DoScript/modules/` (fallback, same as `use`)

If the module is not installed, DoScript prints a helpful error telling you
exactly which command to run:

```
DoScript FileError: Module 'math.do' is not installed.
Run:  python doscript.py install_module math
```

Each module is loaded at most once per script run, even if `use_module`
appears multiple times.

### Difference between `use` and `use_module`

| | `use` | `use_module` |
|---|---|---|
| Looks in global install dir | ❌ | ✅ |
| Looks in local `modules/` | ✅ | ✅ |
| Merges functions & vars | ✅ | ✅ |
| Helpful "install this" error | ❌ | ✅ |

Use `use` for project-local files. Use `use_module` for anything installed
with `install_module`.

### Full Example

```
# report.do
use_module "cli"
use_module "datetime"
use_module "files"

global_variable = greeting

greeting = time_greeting()
print_banner 'Daily Report — {greeting}'

ensure_folder '{desktop}/Reports'
backup_file "data.csv" '{desktop}/Reports'

print_done()
pause
```

---

## `import_variables` — External Variable Files (.slev)

Load key-value pairs from a `.slev` file (Server-lab External Variable)
directly into your script as global variables.

```
import_variables "config.slev"
import_variables '{appdata}/MyApp/settings.slev'
```

### .slev File Format

One `key = value` pair per line. Blank lines and `#` comments are ignored.

```
# config.slev
api_key   = supersecret123
base_url  = https://api.example.com
port      = 8080
timeout   = 30.5
debug     = false
```

- Integer values (`8080`) are imported as numbers
- Float values (`30.5`) are imported as floats
- Everything else is imported as a string
- Optional surrounding quotes on string values are stripped

### No Declaration Needed

Variables from `.slev` files are **auto-declared** — no `global_variable`
line required. They are immediately available after `import_variables`.

```
import_variables "config.slev"

say 'Connecting to {base_url}:{port}...'
say 'Timeout: {timeout}s'
```

### Use Cases

Keep secrets and environment-specific settings out of your `.do` scripts:

```
# deploy.do
import_variables "secrets.slev"       # api_key, db_password, etc.
import_variables "environment.slev"   # base_url, port, region, etc.

say 'Deploying to {base_url}...'
http_post '{base_url}/deploy' '{"key":"{api_key}"}' to response
say 'Response: {response}'
```

Share configuration between multiple scripts:

```
# shared.slev
app_name    = MyApp
version     = 2.1
install_dir = C:/Program Files/MyApp
log_dir     = C:/Logs/MyApp
```

```
# installer.do
import_variables "shared.slev"
print_banner '{app_name} v{version} Installer'
make folder install_dir

# uninstaller.do
import_variables "shared.slev"
delete install_dir
say '{app_name} has been removed.'
```

### Dry-Run Support

`import_variables` respects `--dry-run`. In dry-run mode it logs what it
would import without actually setting any variables.

---

## Summary

| Feature | How to use |
|---|---|
| Install a module | `python doscript.py install_module <name>` |
| Load in a script | `use_module "<name>"` |
| External variables | `import_variables "<file.slev>"` |

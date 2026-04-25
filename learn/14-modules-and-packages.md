# Lesson 14 — Modules and Packages

DoScript has three ways to share and reuse code across scripts. This
lesson covers all three, when to use each, and how to publish your own.

---

## include — Local File Inclusion

The simplest form: copy the contents of another `.do` file into the
current script at the point of the `include` statement.

```
include "helpers.do"

# Functions and variables from helpers.do are now available
greet("Alice")
```

Each file is included at most once per run, even if `include` appears
multiple times across different files. Best for:
- Splitting one large script across readable files
- Sharing utility functions within a single project

---

## use — Project-Local Modules

`use` is a smarter `include` designed for module reuse within a project.
It searches three locations in order:

1. Same folder as your script
2. A `modules/` subfolder next to your script
3. `~/DoScript/modules/` (your personal module library)

```
use "net.do"
use "files.do"
use "ui.do"
```

Each module is loaded at most once, regardless of how many scripts `use` it.

### Recommended project layout

```
my-project/
  installer.do          ← main script
  updater.do            ← another script that shares modules
  modules/
    net.do              ← use "net.do"
    files.do            ← use "files.do"
    ui.do               ← use "ui.do"
```

Use `use` for any code you want to share within a project without
publishing it to the global module registry.

---

## install_module — Global Module Package Manager

Download and install a DoScript module from the official
[DoModule repository](https://github.com/TheServer-lab/DoModule)
in one command run from the terminal:

```
python doscript.py install_module math
python doscript.py install_module strings
python doscript.py install_module cli
python doscript.py install_module datetime
```

Modules are fetched from GitHub and installed to:

| OS | Install path |
|---|---|
| Windows | `C:\Server-lab\DoScript\modules` |
| macOS / Linux | `~/DoScript/modules/` |

Override the destination with `--dir`:

```
python doscript.py install_module math --dir ./modules
```

After installation, the module is available to any script on the machine
via `use_module`.

---

## use_module — Load an Installed Module

`use_module` loads a module installed via `install_module` and merges all
of its functions, variables, and declarations into the calling script's scope.

```
use_module "math"
use_module "cli"
use_module "datetime"
```

It searches in order:
1. `C:\Program Files (x86)\DoScript\modules\` (Windows) / `~/DoScript/modules/`
2. A `modules/` subfolder next to your script
3. `~/DoScript/modules/` (fallback)

If the module is not installed, DoScript prints a clear error:

```
DoScript FileError: Module 'math.do' is not installed.
Run:  python doscript.py install_module math
```

Each module is loaded at most once per script run.

### use vs use_module

| | `use` | `use_module` |
|---|---|---|
| Looks in global install dir | ❌ | ✅ |
| Looks in local `modules/` | ✅ | ✅ |
| Merges functions & vars | ✅ | ✅ |
| Helpful "install this" error | ❌ | ✅ |

**Rule of thumb:** `use` for your own project files, `use_module` for
anything from the public registry.

---

## run_from_web — Run a Remote Script Directly

Run a `.do` script straight from
[TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage)
without installing anything first.

```
run_from_web cleaner.do
run_from_web git-setup.do
run_from_web tools/setup-python.do
```

The `.do` extension is optional. The fetched script shares your current
variable scope — any variables it sets are visible after it returns.

Best for one-off community scripts. For persistent reuse, install with
`install_module` and load with `use_module` instead.

---

## do_new — Launch a Script as a Separate Process

Run a `.do` script in a completely separate DoScript instance. Variables
do not share — it is fully isolated.

```
do_new "cleanup.do"
do_new "report.do"
```

Use `do_new` when you want to chain large independent scripts, not share
their state.

---

## Which to use?

| Scenario | Tool |
|---|---|
| Split a big script into readable files | `include` |
| Share helpers across scripts in one project | `use` |
| Use a published community module | `install_module` + `use_module` |
| Run a one-off community utility | `run_from_web` |
| Chain independent scripts | `do_new` |

---

## Practical Example — Script Using Community Modules

```
# report.do
<doscript=0.6.15>

use_module "cli"
use_module "datetime"

global_variable = greeting

greeting = time_greeting()        # function from datetime module
print_banner 'Daily Report — {greeting}'   # from cli module

for_each file_in '{documents}/Reports'
    if_ends_with ".csv"
        say 'Report: {file_name} ({file_size_kb}KB)'
    end_if
end_for

say 'Found {loop_count} reports.'
print_done()                       # from cli module
pause
```

Install the modules first:

```
python doscript.py install_module cli
python doscript.py install_module datetime
python doscript.py report.do
```

---

## Writing Your Own Module

A module is just a `.do` file with functions and variables. Anything
declared at the top level is merged into the calling script's scope.

```
# modules/ui.do
# UI helper module

function print_banner title
    say "==============================="
    say '  {title}'
    say "==============================="
end_function

function print_done
    say ""
    say "All done!"
end_function
```

Usage:

```
use "ui.do"

print_banner("My App v2.0")
# ... script body ...
print_done()
```

> **Want to publish?** Add your module to
> [TheServer-lab/DoModule](https://github.com/TheServer-lab/DoModule)
> and anyone with DoScript can install it with `install_module`.

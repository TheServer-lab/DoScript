# DoScript — Learning Materials

Welcome to the DoScript `/learn` folder. These guides will take you from
zero to writing real automation scripts, step by step.

---

## Lessons

| File | What you'll learn |
|---|---|
| [01-basics.md](01-basics.md) | Variables, `say`, `ask`, comments, single vs double quotes, built-in path and time variables |
| [02-control-flow.md](02-control-flow.md) | `if` / `else_if` / `else`, `loop`, `repeat`, `break`, `continue`, `try` / `catch` |
| [03-files.md](03-files.md) | `make folder/file`, `rename`, `copy`, `move`, `delete`, `zip`, `read_content`, multi-line `end_file` |
| [04-for-each.md](04-for-each.md) | File iteration, auto-injected variables, `if_ends_with`, age filters, `{loop_count}`, iterating lists |
| [05-functions.md](05-functions.md) | Defining functions, return values, local variables, macros (`make a_command`), `include` |
| [06-network.md](06-network.md) | `download`, `http_get/post`, `ping`, `set_env/get_env`, `is_running()`, `run_from_web` |
| [07-installers.md](07-installers.md) | Full installer pattern, `require_admin`, `confirm`, `make shortcut`, `registry`, `install_package`, `do build` |
| [08-tips-and-patterns.md](08-tips-and-patterns.md) | Quote gotchas, safe delete, counter patterns, `--dry-run`, built-in expressions |
| [09-strings-and-text.md](09-strings-and-text.md) | `trim`, `lower`, `upper`, `replace`, `length`, `split`, text-cleaning patterns |
| [10-safer-commands.md](10-safer-commands.md) | `execute_command`, shell safety, when to use `run` vs `execute_command` |
| [11-data-and-json.md](11-data-and-json.md) | `json_read/write`, `json_get/set`, `[]` subscript notation, CSV, lists |
| [12-interactive-ui.md](12-interactive-ui.md) | `menu`, `input_password`, `select_path`, `progress_bar`, `notify` |
| [13-scheduling-and-debugging.md](13-scheduling-and-debugging.md) | `schedule`, `debug` breakpoints, version declaration, `--debug` / `--dry-run` / `--verbose` |
| [14-modules-and-packages.md](14-modules-and-packages.md) | `use`, `use_module`, `install_module`, `run_from_web`, `do_new` — when to use each |
| [15-external-variables.md](15-external-variables.md) | `import_variables`, `.slev` file format, secrets, shared config, environment deploys |

---

## Quick Reference

```
# This is a comment
global_variable = myVar       # declare before use
myVar = "hello"               # assign
say 'Value is: {myVar}'       # print with interpolation (single quotes)
ask answer "Question:"        # user input

# Built-in path variables (no declaration needed)
say 'Hello, {username}!'
make folder '{downloads}/Sorted'
```

---

## Running a Script

```
python doscript.py myscript.do                  # run normally
python doscript.py myscript.do --dry-run        # preview without side effects
python doscript.py myscript.do --verbose        # extra runtime logging
python doscript.py myscript.do --debug          # debug header + verbose
python doscript.py --version                    # print interpreter version
python doscript.py --help                       # full usage reference
```

---

## Module Management

```
python doscript.py install_module math          # install from DoModule registry
python doscript.py install_module cli --dir ./modules   # install to custom path
```

Inside a script:

```
use_module "math"           # load an installed module
use "local-helpers.do"      # load a project-local file
import_variables "cfg.slev" # load key=value config file
```

---

## Recommended Reading Order

**New to DoScript:** 01 → 02 → 03 → 04 → 08

**Writing installers:** 07 → 12 → 13 → 14

**Working with data:** 11 → 15

**Publishing scripts:** 14 → 15

---

## DoScript Version

These materials cover **DoScript v0.6.15**.

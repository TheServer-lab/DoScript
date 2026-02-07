# DoScript v0.4 — Language Specification (draft)

This document is the canonical specification draft for **DoScript v0.4**. It describes syntax, semantics, built-ins, and behaviors for the interpreter core and modular features introduced in v0.4. Use this spec to guide implementation, tests, documentation, and the standard library.

---

## 1 — Design goals for v0.4

- Make DoScript **modular** (support `include`) so scripts can reuse code and libraries.
- Clarify **script path** handling (`script_path`) and keep the OS `PATH` separate.
- Provide readable condition sugar (e.g. `if ends_with file ".exe"`) while reusing builtin functions.
- Maintain a safe expression evaluator (AST-based) and predictable variable scoping.
- Keep the core small but practical for automation tasks (file ops, loops, functions, macros, networking, processes).

---

## 2 — Files & CLI

- Script files conventionally use the `.do` extension.
- CLI: `python doscript.py myscript.do` — interpreter reads and executes the file.
- `include` resolves files via the `script_path` stack (see §5).

---

## 3 — Lexical rules & tokens

- Comments: `# comment` or `// comment` until end-of-line.
- Statements are line-oriented; empty lines are ignored.
- Strings: double-quoted `"..."` (escape sequences allowed), single-quoted `'...'` (supports `{var}` interpolation).
- Identifiers: `\w+` (letters, digits, underscore).

**Reserved keywords (non-exhaustive):**

`function`, `end_function`, `make a command`, `end_command`, `if`, `else`, `end_if`, `repeat`, `end_repeat`, `loop`, `end_loop`, `for_each`, `end_for`, `for_each_line`, `try`, `catch`, `end_try`, `return`, `break`, `continue`, `include`, `script_path`, `global_variable`, `local_variable`, `exit`, `run`, `capture`, `say`, `ask`, `pause`, `wait`, `download`, `upload`, `move`, `copy`, `delete`, `make folder`, `make file`, `ping`, `kill`, `capture`.

---

## 4 — Data types & expressions

**Primitive types:** string, integer, float, boolean, list.

- Booleans: `true`, `false`.
- Numeric: integer or float.
- Strings: `"double"` (escapes) and `'single'` (interpolated with `{var}`).
- Lists: produced by builtins like `split()` or comma-separated literal lists in constructs.

**Expressions:**

- Identifiers evaluate to variables.
- Function calls: `fn(arg1, arg2)` — supports builtins and user-defined functions.
- Safe evaluation: uses Python `ast` to allow arithmetic, boolean logic, and comparisons. Allowed ops: `+ - * / %`, unary `-`, logical `and`/`or` (via AST boolean ops), comparisons `== != < > <= >=`.
- Evaluation namespace: local scope (if present) overrides global variables; `__builtins__` is blocked.

**String interpolation:**

- Single-quoted strings `'...'` interpolate `{var}` placeholders.
- Escaped braces `\{` and `\}` produce literal braces.

---

## 5 — Path resolution: `script_path` (internal)

**Purpose:** `script_path` is an internal stack used to resolve non-absolute file paths used by DoScript (includes, file ops, `for_each` patterns). It is **not** the OS environment PATH.

**API:**

- `script_path add "<folder>"`
- `script_path remove "<folder>"`
- `script_path list`  — prints entries

**Resolution rule:**

- Absolute paths are used as-is.
- Otherwise, if `script_path` has entries, `resolve_path()` returns `os.path.join(last_script_path_entry, given_path)`.
- If `script_path` is empty, use the current working directory.

---

## 6 — Modules & `include`

**Syntax:**

```do
include "relative/or/absolute/path.do"
```

**Semantics:**

- The file is resolved via `script_path` and normalized with `os.path.abspath`.
- The interpreter tracks `included_files` (absolute paths); repeated includes are no-ops.
- Included file is parsed and executed in the same interpreter instance: functions, macros, and global variables defined in the included file become available to the including script.
- Top-level statements in the included file execute at the include point (similar to Python imports executing module top-level code).
- Errors inside include propagate as normal DoScript errors and are catchable with `try/catch`.

---

## 7 — Variables & scope

- **Global variables** must be declared via `global_variable = name1, name2`. Declared globals exist in `global_vars`.
- **Local variables** declared via `local_variable = name1, name2` — valid only inside functions. Function params are also local.
- **Assignment**: `name = expr` requires the variable to be present in the current local scope (if inside a function) or declared as a global; otherwise assignment raises an error.
- **Function calls** create a new local scope; after return the previous scope is restored.
- **Macros** (via `make a command`) execute in the global scope (no new local scope).

---

## 8 — Functions & macros

**Function syntax**

```do
function fname param1 param2
    ...statements...
end_function
```

- Parameters are whitespace-separated tokens after the function name.
- `return <expr>` returns a value; `return` alone returns `None`.
- `local_variable = ...` may be used inside functions to predeclare locals.

**Calling**

- `fname(arg1, arg2)` — args evaluated then passed.

**Macros**

```do
make a command mymacro
    ...statements...
end_command
```

- Macros stored as raw statement lists and executed via `run "mymacro"`.
- Macros run in the global scope.

---

## 9 — Control flow

**If**

```
if <expression>
    ...
else
    ...
end_if
```

**Sugar**

```
if ends_with <expr> "<suffix>"
    ...
end_if
```

- The sugar is rewritten to call the builtin `endswith()` function.

**Loops**

- `repeat N ... end_repeat` — repeats N times.
- `loop N ... end_loop` or `loop forever ... end_loop` — infinite until `break`.

**For-each**

- File pattern or literal list forms:

```
for_each item in "pattern"    # wildcard globbing
    ...
end_for
```

or

```
for_each item in "a", "b", "c"
    ...
end_for
```

- If RHS is a wildcard pattern, it is globbed (resolved via `script_path`). The loop variable is stored in global variables (declared automatically if missing).

**for_each_line**

```
for_each_line line in "file.txt"
    ...
end_for
```

- Reads file, sets `line` per iteration (no newline included).

**break / continue** supported.

---

## 10 — TRY/CATCH

```
try
    ...
catch
    ...
catch ProcessError
    ...
end_try
```

- `catch` without type accepts all DoScript errors; `catch TypeName` matches by exception class name.

---

## 11 — File & network built-ins

**Filesystem**

- `make folder "<path>"` — `os.makedirs(..., exist_ok=True)`.
- `make file "path" with "content"` (double-quoted for escapes) or `with 'content'` (single-quoted with interpolation).
- `copy "src" to "dst"`, `move "src" to "dst"`, `delete "path"`.

**Network**

- `download "url" to "path"` — `urllib.request.urlretrieve`.
- `upload "path" to "url"` — HTTP POST with file body.

**Process**

- `run "cmd"` runs shell command (returns exit code on assignment usage).
- `capture "cmd"` captures stdout.
- `ping "host"`, `kill "proc"` platform dependent.

**I/O**

- `say <expr>`, `ask varname <prompt_expr>`, `pause`, `wait N`.

---

## 12 — Built-in functions (expressions)

- `exists(path)`, `date()`, `time()`, `datetime()`
- `substring(text, start, length?)`, `replace(text, old, new)`, `length(text)`
- `uppercase(text)`, `lowercase(text)`, `trim(text)`
- `contains(text, search)`, `startswith(text, prefix)`, `endswith(text, suffix)`
- `split(text, delimiter?)` → list, `read_file(path)` → string

Note: `split()` returns a Python list. Indexing/slicing planned for v0.5.

---

## 13 — Assignment behaviors

- `var = run "cmd"` assigns integer exit code.
- `var = capture "cmd"` assigns captured stdout string.

---

## 14 — Error model & exceptions

- Base: `DoScriptError`; subclasses: `NetworkError`, `FileError`, `ProcessError`.
- Unhandled errors print as `DoScript Error: <message>` on CLI.

---

## 15 — Include / module loading details

- `included_files` prevents duplicates and recursion.
- Included modules execute top-level code in the same interpreter instance and can define functions/macros/globals accessible after include.

---

## 16 — Example: Downloads sorter

*(Canonical example; do not copy here if testing string interpolation behavior.)*

```
script_path add "C:/Users/You/Downloads"

make folder "exe"
make folder "zip"
make folder "images"

for_each file in "*"
    if ends_with file ".exe"
        move file to 'exe/{file}'
    else
        if ends_with file ".zip"
            move file to 'zip/{file}'
        else
            if ends_with file ".png"
                move file to 'images/{file}'
            end_if
        end_if
    end_if
end_for
```

- Note: Use single-quoted destination strings when you want `{file}` interpolation.

---

## 17 — Implementation notes & gotchas

- Assignment requires prior declaration; improve error messages to include filename/line number in a future patch.
- `script_path` uses the last-added entry (LIFO) to resolve relative includes.
- `for_each` globbing returns filenames by default (basename). Use `resolve_path()` inside expressions for full paths.
- `make file` uses single-quoted interpolation; double-quoted decodes escape sequences.

---

## 18 — v0.4 planned but not implemented (roadmap)

- List indexing & slicing — v0.5
- `extension(file)` helper — v0.5
- `while` loop — v0.5
- `switch/case` — v0.6
- Better error reporting (filename + line) — v0.5
- Standard library (`std/`) layout — v0.5
- Optional sandbox mode — later

---

## 19 — Backwards compatibility & migration

- v0.4 renames `path` → `script_path`. Consider adding a compatibility alias that emits a warning for old `path` usage.

---

## 20 — Testing checklist (acceptance)

- Include cycle detection
- script_path resolution (relative & absolute)
- for_each globbing and literal lists
- for_each_line newline handling
- if ends_with sugar and direct `endswith()`
- make file interpolation (single vs double)
- download/upload error handling
- run/capture assignments
- try/catch matching

---

## 21 — Quick cheat-sheet

- `include "file.do"`
- `script_path add/remove/list`
- `global_variable = a, b`
- Functions: `function name params ... end_function`
- Macros: `make a command name ... end_command`
- Loops: `for_each`, `for_each_line`, `repeat`, `loop`
- If sugar: `if ends_with x ".ext"`
- File ops: `make folder`, `make file`, `copy`, `move`, `delete`
- Network: `download`, `upload`
- Process: `run`, `capture`
- I/O: `say`, `ask`, `pause`, `wait`

---

## 22 — Next recommended actions

Choose one to continue:

- **A)** Implement improved error messages (filename + line) — high priority.
- **B)** Implement `extension(file)` and list indexing (v0.5 start).
- **C)** Build a `std/` directory with core helpers (e.g. `files.do`).
- **D)** Add a `script_path` compatibility alias for `path` that warns.

---

_End of DoScript v0.4 specification (draft)._


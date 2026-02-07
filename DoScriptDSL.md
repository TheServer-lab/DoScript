# DoScript DSL — Documentation (v2.0)

**DoScript** is a lightweight automation domain-specific language (DSL) with a small Python interpreter (`doscript.py`) for scripting filesystem, process, network and simple control-flow tasks. This documentation describes the language syntax, built-ins, runtime behavior, examples, and troubleshooting tips for the DoScript Interpreter v2.0.

---

## Table of contents

1. Overview
2. Quick start
3. Script structure and parsing
4. Paths and `path_stack`
5. Strings and interpolation
6. Variables and scoping
7. Expressions and built-in functions
8. Statements and commands
9. Control flow: conditionals & loops
10. Functions and macros
11. Error handling and exceptions
12. I/O, network, and process operations
13. Examples
14. Limitations & security considerations
15. Troubleshooting & FAQ

---

## 1. Overview

DoScript provides a concise syntax for automation tasks such as creating files/folders, copying/moving/deleting files, running commands, downloading/uploading resources, iterating over files or lines, and small program logic (variables, functions, loops, conditionals). The provided interpreter is implemented in Python and aims for safety when evaluating expressions via a restricted AST evaluator.

Interpreter entry point:

```sh
python doscript.py <script.do>
```

If the file does not exist the interpreter exits with an error.

---

## 2. Quick start

Create a file `example.do`:

```doscript
# add a base path
path add "/tmp/doscript_demo"

# create folders and files
make folder "installer/files"
make file "installer/files/hi.txt" with "Hello from DoScript!"

# print
say 'Setup finished: {hi_message}'
```

Run it:

```sh
python doscript.py example.do
```

---

## 3. Script structure and parsing

* The interpreter reads the script, removes `#` and `//` comments and blank lines, and joins statements.
* Statements are parsed one-per-line after cleaning.
* Blocks (functions, loops, ifs, etc.) are delimited with start and end keywords (e.g., `function ...` ... `end_function`, `if ...` ... `end_if`).
* Nested blocks are supported; the interpreter tracks depth for correct pairing.

---

## 4. Paths and `path_stack`

* `path add "..."` — pushes a path onto the internal `path_stack`.
* `path remove "..."` — removes a path from the `path_stack` if present.
* `path list` — prints each path in the stack.

When a non-absolute path is used in file operations, the interpreter resolves it against the last entry in `path_stack` (LIFO). If `path` is absolute it is used directly.

Example:

```doscript
path add "/home/user/projects"
make folder "out"
# Creates /home/user/projects/out
```

---

## 5. Strings and interpolation

* Double-quoted strings (`"like this"`) are treated as literal strings with Python-style escape decoding (e.g. `\n`).
* Single-quoted strings (`'like this'`) are interpolated for `{var}` placeholders.

  * Use `\{` and `\}` to escape literal braces inside single-quoted strings.
* Interpolation only happens for single-quoted strings and only for patterns of the form `{identifier}` where `identifier` is a variable name.

Examples:

```doscript
myvar = "world"  # assign
say 'Hello {myvar}'  # prints: Hello world
say "Tab:\tNext"  # double-quoted: escape sequences are decoded
say 'Literal brace: \{not_a_var\}'
```

Notes:

* When writing file content using `make file "path" with "content"`, double-quoted content decodes escape sequences; single-quoted content is interpolated.

---

## 6. Variables and scoping

* Variables must be declared before use. Assignment uses the `name = expr` syntax.
* Two categories of variables:

  * **Global variables** — declared with `global_variable = name1, name2, ...` and stored in the interpreter's `global_vars` map.
  * **Local variables** — declared with `local_variable = name1, name2, ...` and usable inside functions only.
* Reading a variable first checks the current function local scope, then the global vars.
* Setting a variable modifies local scope (if present) or global if that name was declared as a global. If a name is not declared before set, an error is raised.

Example:

```doscript
global_variable = counter
counter = 0
```

---

## 7. Expressions and built-in functions

### Expression evaluation

* Literals: integers, floats, double-quoted strings, single-quoted (interpolated) strings, `true`, `false`.
* Simple identifier (e.g., `myvar`) is interpreted as a variable reference.
* Function call syntax: `name(arg1, arg2)`.
* For richer expressions the interpreter uses a restricted AST-based evaluator (`ast.parse` + `_eval_node`) which supports:

  * Binary operators: `+ - * / %`
  * Unary operators: negation
  * Comparisons: `==, !=, <, >, <=, >=`
  * Boolean operators: `and`, `or`, `not`
* The namespace for AST evaluation includes only `true`, `false`, and your declared variables — no `__builtins__`.

### Built-in functions

* `exists("path")` — returns true if the path exists (resolved via `path_stack`).
* `date()` — returns current date `YYYY-MM-DD`.
* `time()` — returns current time `HH:MM:SS`.
* `datetime()` — returns `YYYY-MM-DD HH:MM:SS`.

String utilities (common):

* `substring(text, start, length?)`
* `replace(text, old, new)`
* `length(text)`
* `uppercase(text)`, `lowercase(text)`, `trim(text)`
* `contains(text, search)`, `startswith(text, prefix)`, `endswith(text, suffix)`
* `split(text, delimiter?)` — returns a Python list of strings
* `read_file(path)` — returns file contents as a string

### User-defined functions

* Define with `function name [params...]` ... `end_function`.
* Call with `name(arg1, arg2)` as a normal function expression.
* Functions get their own local scope; parameters bind to the local scope.
* `return expr` inside a function yields a return value.

---

## 8. Statements and commands

**File & Folder operations**

* `make folder "path"` — create folders (mkdir -p behavior).
* `make file "path" with <content>` — create a file. Content can be a double-quoted literal, single-quoted (interpolated), or expression.
* `copy "src" to "dst"` — copy a file (preserves metadata via `shutil.copy2`).
* `move "src" to "dst"` — move a file or folder.
* `delete "path"` or `delete varName` — deletes file or folder (recursively for dirs).

**Network operations**

* `download "url" to "path"` — downloads a url to the destination using `urllib.request.urlretrieve`.
* `upload "path" to "url"` — posts file contents to the URL via `urllib.request` (POST).
* `ping "host"` — platform-aware ping command.

**Process operations**

* `run "command"` — runs a command with `shell=True`. If the name matches a macro (see macros), the macro body runs instead.

  * When used as `var = run "cmd"` the interpreter captures the command's exit code and assigns it to `var`.
* `capture "command"` — runs a command and captures stdout; returns `('capture_output', stdout)` internally.

  * When used as `var = capture "cmd"` the `var` receives the stdout string.
* `kill "procname"` — kills a process (uses `taskkill` on Windows or `pkill` on other platforms).

**Flow control & misc**

* `exit` or `exit N` — terminate the interpreter with status code.
* `break`, `continue` — used inside loops.
* `say expr` — evaluate `expr` and print to stdout.
* `ask varName prompt_expr` — prompt the user and store the input in `varName`.
* `pause` — wait for Enter key.
* `wait N` — sleep N seconds.

**Variable declarations**

* `global_variable = a, b, c` — declare globals.
* `local_variable = x, y` — declare locals inside functions.

---

## 9. Control flow: conditionals & loops

**IF statement**

```doscript
if <condition>
  ...
else
  ...
end_if
```

* Conditions are evaluated using the expression evaluator. Nested `if` blocks are supported.

**REPEAT**

```doscript
repeat N
  ...
end_repeat
```

* Repeats body N times.

**LOOP**

```doscript
loop N
  ...
end_loop

# or
loop forever
  ...
end_loop
```

* `break` and `continue` control loop execution.

**TRY/CATCH**

```doscript
try
  ...
catch DoScriptError
  ...
catch
  ... # generic
end_try
```

* `catch` can specify an exception class name (e.g., `NetworkError`, `FileError`) or no type to match any DoScript error. If no catch handles the error it propagates.

**FOR_EACH**

* Iterate a list of explicit items:

```doscript
for_each item in "a", "b", "c"
  say item
end_for
```

* Iterate files matching a glob pattern:

```doscript
for_each f in "*.txt"
  say f
end_for
```

**FOR_EACH_LINE**

```doscript
for_each_line line in "file.txt"
  say line
end_for
```

* Iterates lines from a file; each iteration sets the loop variable to the current line.

---

## 10. Functions and macros

**Functions**

* Syntax:

```doscript
function add a b
  return a + b
end_function
```

* Call as `add(1, 2)` in expressions. Functions have parameter binding and their own local scope. Use `local_variable` inside functions to declare locals.

**Macros / Commands**

* Macro (command) definitions are created via `make a command NAME` ... `end_command` — these are textual macros; calling `run "NAME"` executes the macro body rather than an external command.

Example:

```doscript
make a command build
  echo "Building..."
  # other script statements
end_command

run "build"  # executes macro body
```

---

## 11. Error handling and exceptions

Interpreter-specific exceptions:

* `DoScriptError` — base class for script errors.
* `NetworkError` — network related failures (download/ping/upload)
* `FileError` — file operation failures
* `ProcessError` — failures when running processes

`try`/`catch` blocks in scripts can catch these by class name (e.g., `catch NetworkError`) or catch all DoScript errors by using `catch` with no type.

The interpreter prints errors to stderr and exits with non-zero status when an uncaught exception arrives.

---

## 12. I/O, network, and process operations (details)

* `download` uses `urllib.request.urlretrieve` and will raise `NetworkError` if the operation fails.
* `upload` does a POST of raw file bytes to the target URL.
* `ping` uses the OS `ping` command — behavior may vary by platform.
* `run` executes commands with `shell=True`. Be cautious with untrusted input — this can be a vector for command injection.
* `capture` runs a command and returns captured stdout (text mode).

---

## 13. Examples

### Example: simple backup

```doscript
path add "/home/user"
make folder "backups"
copy "data.db" to "backups/data.db.bak"
say 'Backup complete: {date()}'
```

### Example: find and delete old logs

```doscript
for_each f in "logs/*.log"
  # for_each stores filename (basename) in f
  run "echo Deleting {f}"
  delete "logs/{f}"
end_for
```

### Example: function and loop

```doscript
global_variable = i
function count_down n
  local_variable = i
  repeat n
    i = n
    say 'T-{i}'
    i = i - 1
  end_repeat
end_function

call = count_down(5)
```

---

## 14. Limitations & security considerations

* Expression evaluator intentionally restricts `__builtins__` and uses a safe AST walk — however, treat script inputs as untrusted if coming from remote sources.
* `run` uses `shell=True` — avoid interpolating untrusted text into shell commands.
* Network functions (`download`, `upload`, `ping`) perform blocking I/O and do not provide timeouts or retries.
* `upload` performs a raw POST of bytes; it does not set headers or multipart encoding.
* `for_each` globbing returns platform-native paths; path normalization is applied only via `path_stack` resolution.

---

## 15. Troubleshooting & FAQ

**Q: My variable is "used before declaration" error — why?**
A: All writable variables must be declared beforehand. Use `global_variable = name` for global variables. Inside functions use `local_variable = name`.

**Q: Single vs double quotes — why my `{var}` is not interpolated?**
A: Only single-quoted strings are interpolated for `{var}` placeholders; double-quoted strings are treated as literal with escape decoding.

**Q: How to capture a command's output into a variable?**
A: Use `var = capture "command"`. The variable will receive the command's stdout as a string.

**Q: I need to read file contents inside an expression — is that supported?**
A: Yes — use `read_file("path")` to return the file contents as string.

**Q: How do I declare multiple globals?**
A: `global_variable = a, b, c`

---

## Appendix: Example full script

```doscript
# simple deploy.do example
path add "/home/deploy"
global_variable = BUILD_VER, OUT
BUILD_VER = "1.2.3"
OUT = "out/$BUILD_VER"
make folder "{OUT}"
make file "{OUT}/version.txt" with 'Build {BUILD_VER} built on {datetime()}'

# run build macro
make a command build
  run "make all"
  capture_out = capture "echo done"
end_command

run "build"

say 'Deployed build {BUILD_VER} to {OUT}'
```

---
# DoScript v0.6.10 Changelog

## Bug Fixes

- **Non-ASCII strings in double quotes were silently corrupted** — the
  deprecated `unicode_escape` codec was being used to decode escape sequences
  in double-quoted strings and `make file` content. It has been replaced with
  explicit manual escape processing. Characters like `é`, `ü`, `ñ`, `→`, and
  emoji now work correctly.

- **`{variable}` in double-quoted strings produced no output and no error** —
  double-quoted strings do not interpolate variables (single quotes do). The
  interpreter now emits a `[HINT]` message to stderr when it sees `{word}`
  inside a double-quoted string, pointing users to single quotes. This turns a
  completely silent bug into an actionable clue.

## New Features

### `rename` command

Dedicated rename command — clearer intent than `move` when staying in the
same folder:

```
rename "draft.txt" to "final.txt"
rename file to 'archive_{file}'
```

### `set_env` / `get_env`

Read and write environment variables. Useful for installer scripts that need
to expose a path to other programs:

```
set_env "MY_APP_HOME" to "C:/MyApp"

global_variable = appHome
appHome = get_env("MY_APP_HOME")
say 'Installed to: {appHome}'
```

### `require_admin`

Fail early with a clear message if the script is not running as
administrator (Windows) or root (Unix):

```
require_admin "Please run this installer as Administrator."
```

Without this, scripts that need elevated privileges fail halfway through with
cryptic permission errors.

### `confirm` prompt

Single-line confirmation for destructive actions — cleaner than `ask` +
`if answer == "yes"`:

```
confirm "Delete all files in temp/? (y/N)" else exit
confirm "Overwrite existing backup? (y/N)" else say "Skipped."
```

### `list_add`, `list_get()`, `list_length()`

Basic list operations. You can create lists with `split()`, iterate them
with `for_each`, and now also build and index them:

```
global_variable = items
items = split("a,b,c", ",")
list_add items "d"

global_variable = count, first
count = list_length(items)   # 4
first = list_get(items, 0)   # "a"

say 'Total: {count}, First: {first}'
```

### `for_each` iterates list variables

Previously `for_each item in ...` only worked with a literal comma-separated
list. It now also accepts a variable that holds a list:

```
global_variable = fruits, fruit
fruits = split("apple,banana,mango", ",")

for_each fruit in fruits
    say 'Fruit: {fruit}'
end_for
```

### `{loop_count}` — item count after every `for_each`

After any `for_each` loop ends, `{loop_count}` holds the number of items
that were iterated (respecting `break` and age filters):

```
for_each file_in here
    copy file to "backup"
end_for
say 'Copied {loop_count} files.'
```

### Age filter in `for_each` — `older_than` / `newer_than`

Filter files and folders by how long ago they were last modified:

```
# Delete files not touched in 30 days
global_variable = f
for_each f_in here older_than 30 days
    delete f
end_for
say 'Cleaned up {loop_count} old files.'

# Only process recently changed files
for_each f_in deep newer_than 1 hour
    log 'Recently changed: {f}'
end_for
```

Supported units: `seconds`, `minutes`, `hours`, `days`, `months`, `years`
(singular forms also accepted).

### Multi-line `make file` with `end_file`

Create files with structured multi-line content. Variable interpolation
works inside the block:

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

### `is_running()` expression

Check whether a process is currently running — useful before `kill` or
before launching a program that should not run twice:

```
if is_running("notepad.exe")
    kill "notepad.exe"
end_if

if not is_running("myservice")
    run "myservice --start"
end_if
```

## Version

Interpreter version updated from `0.6.9` to `0.6.10`.

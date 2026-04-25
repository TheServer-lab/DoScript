# Lesson 12 — What's New in 0.6.10

## Bug Fixes

### Non-ASCII characters now work in double-quoted strings

```
# Previously corrupted on Python 3.12+; now works correctly
filename = "résumé_André.txt"
make folder "Ångström"
```

### Hint when you use `{var}` in double quotes

If you accidentally put a variable reference inside double quotes, DoScript
now prints a hint pointing you to single quotes instead of silently producing
wrong output:

```
name = "Alice"
say "Hello {name}"   # prints hint + Hello {name}  (no interpolation)
say 'Hello {name}'   # prints Hello Alice  ✅
```

---

## `rename`

Rename a file or folder in place. Cleaner than `move` when you're not
changing the directory:

```
rename "draft_v1.txt" to "final.txt"
rename file to 'processed_{file}'
```

---

## `set_env` and `get_env()`

Write and read environment variables. Essential for installers that need to
make a path available to other programs:

```
set_env "MY_APP_HOME" to "C:/MyApp"

global_variable = path
path = get_env("MY_APP_HOME")
say 'App is at: {path}'
```

---

## `require_admin`

Fail early with a clear message if the script is not running as administrator
(Windows) or root (Unix/macOS):

```
require_admin "Please run this script as Administrator."

# ... rest of installer continues only if admin
```

Without this, privileged scripts fail halfway through with cryptic
"Permission denied" errors.

---

## `confirm`

Single-line yes/no gate for destructive actions:

```
confirm "Delete all logs? (y/N)" else exit
confirm "Overwrite backup? (y/N)" else say "Skipped."
```

The user types `y` or `yes` to proceed. Anything else runs the `else` branch.

---

## List operations

### `list_add`

```
global_variable = items
items = split("a,b,c", ",")
list_add items "d"
```

### `list_get(list, index)`

Zero-based index access:

```
global_variable = first
first = list_get(items, 0)   # "a"
```

### `list_length(list)`

```
global_variable = n
n = list_length(items)   # 4
```

---

## `for_each` over a list variable

Previously `for_each` only worked with a literal comma-separated list.
Now it also accepts a variable holding a list:

```
global_variable = fruits, fruit
fruits = split("apple,banana,mango", ",")
list_add fruits "pear"

for_each fruit in fruits
    say 'Fruit: {fruit}'
end_for
```

---

## `{loop_count}` — count after every `for_each`

After any `for_each` loop ends, `loop_count` holds the number of items
that were processed:

```
for_each file_in here
    copy file to "backup"
end_for
say 'Copied {loop_count} files.'
```

---

## Age filter in `for_each`

Filter files by last-modified time using `older_than` or `newer_than`:

```
global_variable = old_file
for_each old_file_in here older_than 30 days
    delete old_file
end_for
say 'Deleted {loop_count} old files.'
```

```
global_variable = f
for_each f_in deep newer_than 1 hour
    log 'Recently changed: {f}'
end_for
```

Supported units: `seconds`, `minutes`, `hours`, `days`, `months`, `years`.

Works with `here`, `deep`, and directory paths. Combines with `loop_count`.

---

## Multi-line `make file` with `end_file`

Create structured files — config files, scripts, templates — without
squeezing everything onto one line. Variables interpolate inside the block:

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

---

## `is_running()` expression

Check whether a process is currently running:

```
global_variable = running
running = is_running("notepad.exe")

if running == true
    say "Notepad is open"
end_if

if not is_running("myservice")
    run "myservice --start"
end_if
```

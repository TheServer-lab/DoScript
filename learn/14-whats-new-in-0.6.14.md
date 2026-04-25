# Lesson 14 — What's New in 0.6.14

## `debug` — Breakpoint Console

Drop a breakpoint anywhere. The script pauses and opens the
`doscript-runtime>` console so you can inspect live state, override
variables, and resume.

```
global_variable = name, count
name = "Alice"
count = 42

debug "before the loop"

loop 5 as i
    say 'i = {i}, count = {count}'
end_loop
```

At the prompt:

```
doscript-runtime> vars
    count = 42
    name = 'Alice'
doscript-runtime> set count 100
    count = '100'
doscript-runtime> eval count + 1
    => 101
doscript-runtime> run say 'hello from debug'
hello from debug
doscript-runtime> continue
```

The loop then runs with `count = 100`. Changes made at the breakpoint
persist for the rest of the script.

---

## `<doscript=x.y.z>` — Version Declaration

Put this on the first line to declare which interpreter version a script
requires:

```
<doscript=0.6.14>

say "Script body starts here."
```

The interpreter checks this on startup and either runs silently (exact
match), prints a hint (older minor version), or refuses with a clear
error (script is newer than the interpreter). Omitting the tag is always
safe — it changes nothing.

---

## `menu` — Numbered Option Picker

```
global_variable = theme
menu theme from "Choose a theme" "Dark" "Light" "System default"
say 'Theme set to: {theme}'
```

The user enters a number or unambiguous option text. The chosen string
is stored in the variable.

---

## `input_password` — Hidden Password Input

```
global_variable = pw
input_password pw "Database password:"
```

Input is hidden on real terminals via `getpass`. The variable receives
the raw string — never logged.

---

## `select_path` — CLI Filesystem Navigator

```
global_variable = install_dir
select_path install_dir "Choose install folder" from '{appdata}' folders
say 'Installing to: {install_dir}'
```

Options: `files`, `folders`, `both` (default). The `from` clause sets
the starting directory (defaults to current working directory).

Navigation:
- Enter a number to open a folder or select a file
- Type `..` to go up one level
- Type a full path to jump directly
- Enter `0` to select the current folder (in `folders` or `both` mode)

---

## `progress_bar` — Live CLI Progress Bar

```
global_variable = done, total
total = 200

for_each file_in deep
    # ... process file ...
    progress_bar done of total "Processing"
end_for

progress_bar done
say 'Processed {loop_count} files.'
```

Always call `progress_bar done` when finished — it moves the cursor to
the next line so subsequent output isn't corrupted.

The label is optional:

```
progress_bar i of 10           # no label
progress_bar i of 10 "Copying" # with label
```

---

## `notify` — Desktop Notification

```
notify "Backup" "Your backup completed successfully."
notify "Done!"                  # title defaults to DoScript
```

Works on Windows (tray balloon), macOS (Notification Centre), and Linux
(`notify-send`). If no notification system is available, falls back to
a terminal bell and printed message. Respects `--dry-run`.

---

## `schedule` — OS-Managed Scheduling

```
# Run once at a specific time today
schedule "cleanup.do" at "23:00"

# Run once in the future
schedule "check.do" in 15 minutes
schedule "check.do" in 2 hours

# Run daily at a fixed time
schedule "backup.do" daily at "03:00"

# Run once on a specific date
schedule "report.do" on "2026-12-01" at "09:00"
```

Uses Windows Task Scheduler on Windows, `crontab` on macOS/Linux.
Scheduling the same script again replaces the previous entry.
Respects `--dry-run`.

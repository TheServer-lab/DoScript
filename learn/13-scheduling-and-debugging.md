# Lesson 13 — Scheduling and Debugging

This lesson covers the tools DoScript gives you for running scripts on a
schedule and diagnosing scripts when something goes wrong.

---

## schedule — OS-Managed Scheduling

Register a `.do` script with the operating system's native scheduler —
Windows Task Scheduler or `crontab` on macOS/Linux. No daemon, no config
file — one line in your script.

### Syntax

```
# Run once at a specific time today
schedule "cleanup.do" at "23:00"

# Run once in N minutes or hours from now
schedule "check.do" in 15 minutes
schedule "check.do" in 2 hours

# Run daily at a fixed time
schedule "backup.do" daily at "03:00"

# Run once on a specific date
schedule "report.do" on "2026-12-01" at "09:00"
```

Scheduling the same script again **replaces** the previous entry —
no duplicate tasks pile up. Respects `--dry-run`.

### Typical use in an installer

```
# At the end of setup, register the auto-updater
schedule "auto-update.do" daily at "03:00"
say "Auto-update scheduled for 3:00 AM daily."
```

### Checking what was scheduled

Use `--dry-run` to preview scheduling actions without actually registering
anything:

```
python doscript.py myinstaller.do --dry-run
# [DRY] schedule: would register 'auto-update.do' daily at 03:00
```

---

## debug — Interactive Breakpoint Console

Drop a breakpoint anywhere. When execution reaches it, the script pauses
and opens the `doscript-runtime>` console so you can inspect live state,
override variables, and resume.

```
global_variable = name, count
name = "Alice"
count = 42

debug "before the loop"

loop 5 as i
    say 'i = {i}, count = {count}'
end_loop
```

When the breakpoint triggers:

```
[DEBUG] before the loop
  name  = 'Alice'
  count = 42
doscript-runtime>
```

### Console commands at a breakpoint

| Command | What it does |
|---|---|
| `vars` | Print all current variable values |
| `set <var> <value>` | Override a variable |
| `eval <expr>` | Evaluate an expression and print the result |
| `run <statement>` | Execute a single DoScript statement |
| `continue` | Resume the script from after the breakpoint |

```
doscript-runtime> vars
    count = 42
    name  = 'Alice'
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

### The label is optional

```
debug                    # no label — just drops to the console
debug "after json_read"  # label shown in the breakpoint header
```

---

## <doscript=x.y.z> — Version Declaration

Put this on the **first line** to declare which interpreter version a
script requires. Useful when you publish scripts and want users to know
what they need.

```
<doscript=0.6.14>

say "Script body starts here."
```

### What the interpreter does

| Situation | Behaviour |
|---|---|
| Exact match | Runs silently |
| Script is older than interpreter | Runs with a hint |
| Script is newer than interpreter | Refuses with a clear error |
| Tag absent | Runs normally — no check |

Omitting the tag is always safe. Add it when your script uses features
that weren't available in earlier versions.

---

## CLI Flags for Troubleshooting

### --version

Check which interpreter you have:

```
python doscript.py --version
→ DoScript 0.6.15
```

### --help

Print the full reference of flags, subcommands, and examples:

```
python doscript.py --help
```

### --dry-run

Preview all file system, network, and scheduling actions without executing
them. Every destructive operation prints `[DRY]` instead of running.

```
python doscript.py my-installer.do --dry-run
```

Always test with `--dry-run` before running a script that moves, deletes,
or downloads anything for the first time.

### --verbose

Show extra runtime information — file operations, update checks, module
loading — without enabling the full debug console.

```
python doscript.py my-script.do --verbose
```

### --debug

Enable verbose output **plus** print a debug header on startup. Implies
`--verbose`. Use when diagnosing a specific run without adding `debug`
breakpoints to the script itself.

```
python doscript.py my-script.do --debug
→ [DEBUG] Debug mode active — DoScript 0.6.15
→ [VERBOSE] ...runtime output...
```

---

## Practical Example — Scheduled Backup with Debug Guard

```
# nightly-backup.do
<doscript=0.6.14>

global_variable = dest, file

dest = '{desktop}/Backups'
make folder dest

# Uncomment to debug: inspect variables before the loop
# debug "pre-backup state"

say 'Backing up to {dest}...'

for_each file_in '{documents}' deeper_than 0 days
    copy file to dest
end_for

notify "Backup" 'Nightly backup done — {loop_count} files.'
log 'Backup completed: {loop_count} files'
```

Schedule it from your installer:

```
schedule "nightly-backup.do" daily at "02:00"
say "Nightly backup scheduled."
```

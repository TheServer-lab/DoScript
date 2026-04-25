# DoScript v0.6.14 Changelog

## New Features

### `debug` — interactive breakpoint console

Drop a breakpoint anywhere in a script. Execution pauses and opens the
`doscript-runtime>` console so you can inspect and modify state live,
then resume.

```
debug                          # bare pause
debug "before sort loop"       # with a label shown in the banner
```

Console commands at a breakpoint:

| Command | What it does |
|---|---|
| `continue` / `c` | Resume the script |
| `vars` | List all current variables and their values |
| `set <var> <value>` | Override a variable (barewords treated as strings) |
| `eval <expr>` | Evaluate any expression and print the result |
| `run <statement>` | Execute a single DoScript statement live |
| `stack` | Show active loop variable names |
| `trace on/off` | Toggle verbose output for the rest of the run |
| `exit` | Stop the script entirely |

Variable changes made via `set` persist — the script continues with the
new values.

---

### `<doscript=x.y.z>` — version declaration

Declare which interpreter version a script targets. Place at the top of
any `.do` file:

```
<doscript=0.6.14>
```

Behaviour:

| Declared | Running | Result |
|---|---|---|
| `0.6.14` | `0.6.14` | Silent — exact match |
| `0.6.13` | `0.6.14` | `[INFO]` patch mismatch, continues fine |
| `0.6.9` | `0.6.14` | `[HINT]` older minor version, still runs |
| `0.7.0` | `0.6.14` | **Hard error** — interpreter too old, stops |
| *(omitted)* | any | Completely silent, no change in behaviour |

---

### `menu` — interactive numbered menu

Present a list of options and capture the user's choice:

```
global_variable = choice
menu choice from "Install location?" "AppData" "Program Files" "Custom path"
say 'Installing to: {choice}'
```

The user can enter a number or type an unambiguous option name.
Returns the selected string.

---

### `input_password` — masked password input

Prompt for a password without echoing it to the terminal:

```
global_variable = pw
input_password pw "Enter admin password:"
```

Uses Python's `getpass` — input is hidden on real terminals.

---

### `select_path` — interactive CLI file/folder browser

Let the user navigate the filesystem and pick a file or folder:

```
global_variable = install_dir
select_path install_dir "Where should we install?" from '{appdata}' folders

global_variable = target_file
select_path target_file "Select a config file" files
```

Modes: `files`, `folders`, `both` (default). Displays numbered entries,
`..` goes up, or the user can type a path directly.

---

### `progress_bar` — inline CLI progress bar

Render a live updating progress bar on a single terminal line:

```
global_variable = i
loop 100 as i
    progress_bar i of 100 "Installing"
    wait 0.01
end_loop
progress_bar done
```

Output: `  Installing  [████████████░░░░░░░░░░░░░░░░░░░░░░░░]  33.0%  33/100`

`progress_bar done` moves to the next line cleanly so subsequent output
isn't corrupted.

---

### `notify` — OS desktop notification

Send a system notification from a script:

```
notify "MyApp" "Installation complete!"
notify "Backup finished."      # title defaults to "DoScript"
```

Platform support:
- **Windows** — balloon tray notification via PowerShell
- **macOS** — `osascript` notification centre
- **Linux** — `notify-send` (falls back to terminal bell + print)

Respects `--dry-run`.

---

### `schedule` — register a script with the OS scheduler

Schedule a `.do` script to run at a future time:

```
schedule "cleanup.do" at "22:00"
schedule "backup.do" daily at "03:00"
schedule "check.do" in 30 minutes
schedule "report.do" on "2026-12-01" at "09:00"
```

Platform support:
- **Windows** — Windows Task Scheduler via `schtasks`
- **macOS / Linux** — `crontab`

Respects `--dry-run` — prints what would be scheduled without touching
the system scheduler.

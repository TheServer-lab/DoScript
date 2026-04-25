# Lesson 12 — Interactive UI

DoScript v0.6.14 adds five commands for building polished interactive
scripts — menus, password prompts, filesystem pickers, progress bars,
and desktop notifications — all from the terminal, no GUI framework needed.

---

## menu — Numbered Option Picker

Let the user choose from a list of options. The chosen string is stored
directly in the variable — no need to convert a number.

```
global_variable = theme
menu theme from "Choose a theme" "Dark" "Light" "System default"
say 'Theme set to: {theme}'
```

The user can type a number (`1`, `2`, `3`) or enough of the option text
to be unambiguous (`da` → `Dark`).

Use `menu` instead of hand-rolling `say`/`ask`/`if` chains for option
selection in installers and interactive scripts.

```
global_variable = action
menu action from "What would you like to do?" "Install" "Update" "Uninstall" "Exit"

if action == "Install"
    say "Running installer..."
else_if action == "Update"
    say "Running updater..."
else_if action == "Uninstall"
    confirm "Uninstall MyApp? (y/N)" else exit
    say "Removing..."
else
    exit
end_if
```

---

## input_password — Hidden Password Input

Prompt for a password without echoing input to the terminal.

```
global_variable = pw
input_password pw "Database password:"
```

Input is hidden via `getpass` on real terminals — the value is never
logged or printed. The variable receives the raw string.

```
global_variable = pw, api_key

input_password pw "Enter your password:"
input_password api_key "Enter your API key:"

say "Connecting..."
http_post "https://api.example.com/login" '{"password":"{pw}"}' to response
```

> **Never** use `ask` for passwords — it echoes input to the screen.

---

## select_path — CLI Filesystem Navigator

Let the user navigate the filesystem and pick a file or folder
interactively. The chosen path is stored in the variable.

```
global_variable = install_dir
select_path install_dir "Choose install folder" from '{appdata}' folders
say 'Installing to: {install_dir}'
```

### Options

| Clause | Meaning |
|---|---|
| `from "path"` | Starting directory (defaults to current folder) |
| `files` | Show only files |
| `folders` | Show only folders |
| `both` | Show files and folders (default) |

### Navigation at the prompt

- Enter a number to open a folder or select a file
- Type `..` to go up one level
- Type a full path to jump directly
- Enter `0` to select the current folder (in `folders` or `both` mode)

### Common uses

```
# Pick an install location starting from the user's home
global_variable = dest
select_path dest "Where should we install?" from '{user_home}' folders

# Pick a file to process
global_variable = target
select_path target "Select a config file to edit" from "." files
```

---

## progress_bar — Live CLI Progress Bar

Display a live updating progress bar while processing files or items.

```
global_variable = done, total
total = 200
done = 0

for_each file_in deep
    done = done + 1
    progress_bar done of total "Processing"
    copy file to "backup"
end_for

progress_bar done
say 'Processed {loop_count} files.'
```

Always call `progress_bar <var>` (without `of total`) when finished —
it moves the cursor to a new line so subsequent output isn't corrupted.

### Label is optional

```
progress_bar i of 10            # no label
progress_bar i of 10 "Copying"  # with label
```

### Practical Example — Copying with progress

```
global_variable = file, n, total
n = 0

# Count first
for_each file_in here
    total = total + 1
end_for

for_each file_in here
    n = n + 1
    progress_bar n of total "Copying"
    copy file to "backup"
end_for

progress_bar n
say 'Done — copied {loop_count} files.'
```

---

## notify — Desktop Notification

Send a system notification that appears in the OS notification centre
(Windows tray balloon, macOS Notification Centre, Linux via `notify-send`).

```
notify "Backup" "Your backup completed successfully."
notify "Done!"                  # title defaults to "DoScript"
```

If no notification system is available, DoScript falls back to a terminal
bell and printed message. Respects `--dry-run`.

### Use at end of long tasks

```
for_each file_in deep
    copy file to "backup"
end_for

notify "Backup complete" 'Backed up {loop_count} files to backup/'
```

---

## Practical Example — Interactive Installer with Full UI

```
# interactive-installer.do
<doscript=0.6.14>

say "==============================="
say "     MyApp Interactive Setup"
say "==============================="
say ""

# Pick install location
global_variable = install_dir
select_path install_dir "Choose install folder" from '{user_home}' folders
say 'Will install to: {install_dir}'
say ""

# Pick edition
global_variable = edition
menu edition from "Choose edition" "Full" "Minimal" "Developer"

# Confirm
confirm 'Install {edition} edition to {install_dir}? (y/N)' else exit

# Get credentials if needed
global_variable = api_key
if edition == "Developer"
    input_password api_key "Enter your developer API key:"
end_if

# Install with progress
say "Downloading..."
global_variable = n, total
total = 10
n = 0

loop 10
    n = n + 1
    progress_bar n of total "Downloading"
    wait 0.2
end_loop
progress_bar n

say "Installing..."
make folder install_dir

notify "MyApp Setup" 'Installation complete! {edition} edition installed.'
say ""
say "Done! Run 'myapp' from any terminal."
pause
```

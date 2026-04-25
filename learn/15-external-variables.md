# Lesson 15 — External Variables (.slev)

`.slev` files (Server-lab External Variable) let you store key-value
configuration outside your `.do` scripts and load them at runtime with
`import_variables`. This keeps secrets, environment-specific settings,
and shared config separate from your script logic.

---

## import_variables

Load a `.slev` file into your script. All key-value pairs become global
variables immediately — no `global_variable` declaration needed.

```
import_variables "config.slev"
import_variables '{appdata}/MyApp/settings.slev'
```

Paths can be double-quoted, single-quoted (with interpolation), or a
bare variable name — same as all other file commands.

---

## .slev File Format

One `key = value` pair per line. Blank lines and `#` comments are ignored.
Surrounding quotes on string values are optional and stripped automatically.

```
# config.slev
api_key   = supersecret123
base_url  = https://api.example.com
port      = 8080
timeout   = 30.5
debug     = false
app_name  = "My Application"
```

### Type coercion

| Value looks like | Imported as |
|---|---|
| `8080` (integer) | number |
| `30.5` (float) | float |
| `true` / `false` | boolean |
| Anything else | string (quotes stripped if present) |

---

## Using imported variables

Variables from `.slev` files are used exactly like any other variable.
They are available immediately after `import_variables`.

```
import_variables "config.slev"

say 'Connecting to {base_url}:{port}...'
say 'Timeout: {timeout}s'

if debug == true
    log "Debug mode is on"
end_if
```

---

## Keeping Secrets Out of Scripts

The main use case: store credentials and environment-specific values
in a `.slev` file that is **not** committed to version control.

```
# secrets.slev  ← add to .gitignore
db_password = hunter2
api_key     = sk-abc123xyz
smtp_user   = noreply@example.com
```

```
# deploy.do
import_variables "secrets.slev"
import_variables "environment.slev"

say 'Deploying to {base_url}...'
http_post '{base_url}/deploy' '{"key":"{api_key}"}' to response
say 'Response: {response}'
```

---

## Sharing Config Between Multiple Scripts

Define values once and import them everywhere.

```
# shared.slev
app_name    = MyApp
version     = 2.1
install_dir = C:/Program Files/MyApp
log_dir     = C:/Logs/MyApp
```

```
# installer.do
import_variables "shared.slev"
say '{app_name} v{version} Installer'
make folder install_dir
make folder log_dir
make shortcut app_name to '{install_dir}/myapp.exe' on desktop
registry set HKCU\Software\MyApp Version version
```

```
# uninstaller.do
import_variables "shared.slev"
confirm 'Remove {app_name} v{version}? (y/N)' else exit
delete install_dir
registry delete HKCU\Software\MyApp
say '{app_name} has been removed.'
```

---

## Environment-Specific Deployments

Keep one `.do` script, multiple environment configs:

```
# dev.slev
base_url = http://localhost:3000
db_name  = myapp_dev
debug    = true

# prod.slev
base_url = https://myapp.example.com
db_name  = myapp_prod
debug    = false
```

```
# deploy.do
global_variable = env
ask env "Deploy to which environment? (dev/prod)"

import_variables '{env}.slev'

say 'Deploying {app_name} to {base_url}...'

if debug == true
    log "Debug mode active"
end_if
```

---

## --dry-run Support

`import_variables` respects `--dry-run`. In dry-run mode it logs what
it would import without actually setting any variables:

```
python doscript.py deploy.do --dry-run
# [DRY] import_variables: would load 'config.slev' (6 variables)
```

---

## Practical Example — Full Configuration-Driven Script

```
# backup.do
<doscript=0.6.15>

import_variables "backup.slev"
# backup.slev provides: source_dir, dest_dir, keep_days, notify_title

say '{notify_title}: Starting backup...'

make folder dest_dir

global_variable = file, n
n = 0

# Count files first for progress bar
for_each file_in source_dir
    n = n + 1
end_for

global_variable = done
done = 0

for_each file_in source_dir
    done = done + 1
    progress_bar done of n "Backing up"
    copy file to dest_dir
end_for
progress_bar done

# Clean up old backups
for_each old_in dest_dir older_than keep_days days
    delete old_path
end_for

notify notify_title 'Backup complete — {loop_count} files copied.'
log 'Backup done: {done} copied, {loop_count} old files removed.'
```

```
# backup.slev
source_dir   = C:/Projects
dest_dir     = D:/Backups/Projects
keep_days    = 30
notify_title = Daily Backup
```

Schedule it once:

```
schedule "backup.do" daily at "02:00"
```

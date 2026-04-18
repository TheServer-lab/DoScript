# Lesson 13 — What's New in 0.6.11

## Built-in Path Variables

Seven path variables are now always available — no `global_variable` declaration,
no assignment. They resolve to the correct location on Windows, macOS, and Linux
automatically.

| Variable | Windows | macOS / Linux |
|---|---|---|
| `user_home` | `C:\Users\Alice` | `/home/alice` |
| `username` | `Alice` | `alice` |
| `downloads` | `C:\Users\Alice\Downloads` | `~/Downloads` |
| `desktop` | `C:\Users\Alice\Desktop` | `~/Desktop` |
| `documents` | `C:\Users\Alice\Documents` | `~/Documents` |
| `appdata` | `C:\Users\Alice\AppData\Roaming` | `~/.config` |
| `temp` | `C:\Users\Alice\AppData\Local\Temp` | `/tmp` |

```
say 'Hello, {username}!'
make folder '{downloads}/Sorted'
zip "project" to '{desktop}/project_backup.zip'
make folder '{appdata}/MyApp'
```

These replace any need to hardcode paths like `"C:/Users/User/Downloads"`.
Scripts written with built-in path variables work on any machine without editing.

---

## `json_set` command

Write a value directly into a JSON variable. Supports dot notation for nested keys:

```
json_read "config.json" to cfg

json_set cfg "version" "2.0"
json_set cfg "user.name" "Alice"

json_write cfg to "config.json"
```

---

## Flexible paths for `json_read`, `json_write`, `system_disk`

All three now accept variables, interpolated strings, and expressions — not
just hardcoded double-quoted paths:

```
global_variable = config_path
config_path = "settings.json"

json_read config_path to cfg
json_write cfg to '{appdata}/MyApp/settings.json'

system_disk user_home to disk_usage
say 'Disk usage: {disk_usage}%'
```

---

## Bare function calls as statements

Functions can be called as standalone statements — no dummy assignment needed:

```
function greet name
    say 'Hello, {name}!'
end_function

greet("Alice")
greet("Bob")
```

Previously this required `result = greet("Alice")` even when the return
value wasn't needed.

---

## Remote script cache cleanup

The `.doscript_remote_cache` folder is now automatically deleted after each
remote script run. Previously, each run added a new UUID subfolder that was
never cleaned up.

# Lesson 01 — Basics

## Comments

```
# This is a comment
// This is also a comment
say "https://example.com"   # URLs inside strings are safe — // is NOT treated as a comment here
```

---

## Variables

All variables **must be declared** before use with `global_variable`.
You can declare multiple on one line with commas.

```
global_variable = name
global_variable = firstName, lastName, age
```

Assign with `=`:

```
name = "Alice"
age = 30
```

Variables are **loosely typed** — they hold strings, numbers, or booleans.

---

## Strings: Single vs Double Quotes

This is one of the most important rules in DoScript.

| Quote type | Behaviour | Use for |
|---|---|---|
| `"double"` | Literal — no variable substitution | Fixed text, paths, URLs |
| `'single'` | Interpolated — `{var}` is replaced | Output that includes variables |

```
global_variable = name
name = "World"

say "Hello {name}"      # prints:  Hello {name}   ← NOT interpolated
say 'Hello {name}'      # prints:  Hello World    ← interpolated
```

**Rule of thumb:** Use single quotes whenever you want to include a variable in your output.

---

## say

Prints a value to the console.

```
say "Hello!"
say 'Your name is: {name}'
say 42
say name                    # prints the value of the variable
```

---

## ask

Prompts the user and stores the answer in a variable.
`ask` auto-declares the variable — no `global_variable` line needed.

```
ask answer "What is your name?"
say 'Hello, {answer}!'
```

---

## Built-in Read-Only Variables

These are always available — do not declare or overwrite them.

| Variable | Value |
|---|---|
| `today` | Current date, e.g. `2025-04-01` |
| `now` | Current time, e.g. `14:30:00` |
| `year` | Current year |
| `month` | Current month (number) |
| `day` | Current day (number) |
| `hour` / `minute` / `second` | Time components |
| `time` | Unix timestamp |
| `arg1` … `arg32` | CLI arguments passed to the script |

```
say 'Today is: {today}'
say 'The time is: {now}'
```

---

## pause, wait, exit

```
pause               # waits for the user to press Enter
wait 2              # waits 2 seconds
wait 0.5            # waits half a second

exit                # exits with code 0
exit 1              # exits with code 1
```

---

## log, warn, error

These print formatted messages. Use them instead of `say` when writing
scripts meant to run unattended.

```
log "Process started"       # prints [INFO] Process started
warn "Disk is almost full"  # prints [WARN] Disk is almost full
error "File not found"      # prints [ERROR] File not found
```

---

## A Complete First Script

```
# hello.do
global_variable = name

ask name "What is your name?"
say 'Hello, {name}!'
say 'Today is {today}. Have a great day!'
pause
```

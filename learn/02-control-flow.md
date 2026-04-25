# Lesson 02 — Control Flow

## if / else_if / else / end_if

```
global_variable = age
age = 20

if age >= 18
    say "You are an adult."
else
    say "You are a minor."
end_if
```

`else` is optional, and `else_if` lets you chain extra conditions without
nested fallback blocks. Conditions support `==`, `!=`, `<`, `>`, `<=`, `>=`,
and logical operators `and`, `or`, `not`.

```
if age >= 18 and age < 65
    say "Working age."
end_if

if name == "" or name == "unknown"
    say "No name provided."
end_if

if score >= 90
    say "Grade A"
else_if score >= 80
    say "Grade B"
else
    say "Keep going"
end_if
```

### Nested if

```
if score > 50
    if score > 90
        say "Excellent!"
    else
        say "Passed."
    end_if
else
    say "Failed."
end_if
```

---

## else_if in file loops

`else_if` also works inside `for_each` blocks when you want a single
classification chain:

```
for_each file_in here
    if_ends_with ".jpg"
        say "It's an image"
    else_if file_ext == ".mp4"
        say "It's a video"
    else
        say "Unknown file type"
    end_if
end_for
```

---

## repeat

Runs a block a fixed number of times.

```
repeat 5
    say "Hello!"
end_repeat
```

---

## loop

Runs a block a fixed number of times, or forever.

```
loop 3
    say "Looping..."
end_loop

loop 3 as i
    say 'Iteration {i}'
end_loop

loop forever
    say "This runs until Ctrl+C"
end_loop

loop forever as i
    say 'Heartbeat #{i}'
end_loop
```

---

## break and continue

`break` exits the current loop. `continue` skips to the next iteration.

```
global_variable = i
i = 0

loop forever
    i = i + 1
    if i == 5
        break
    end_if
    say 'i = {i}'
end_loop
```

`continue` is particularly useful inside `for_each` to skip certain files:

```
for_each file_in here
    if_ends_with ".do"
        continue        # skip .do files, process everything else
    end_if
    say 'Processing: {file_name}'
end_for
```

---

## try / catch / end_try

Catches errors so your script can handle them gracefully.

```
try
    download "https://example.com/file.zip" to "file.zip"
catch NetworkError
    say "Download failed — check your connection."
end_try
```

Available error types to catch:

| Type | Raised by |
|---|---|
| `NetworkError` | `download`, `http_get`, `ping`, etc. |
| `FileError` | `copy`, `move`, `delete`, file reads |
| `ProcessError` | `run`, `execute`, `kill` |
| `DataError` | `json_read`, `csv_read`, etc. |
| *(no type)* | Catches any error |

```
try
    delete "important.txt"
catch FileError
    warn "Could not delete the file."
catch
    error "Something unexpected happened."
end_try
```

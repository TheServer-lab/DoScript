# Lesson 04 — for_each (File Iteration)

`for_each` is one of the most powerful features in DoScript. It iterates
over files or folders in a directory and auto-injects a rich set of
variables for each item.

---

## Basic Syntax

```
for_each file_in here
    say 'Found: {file_name}'
end_for
```

The word before `_in` is your **variable prefix**. It determines both the
loop variable name and all the auto-injected metadata names.

---

## Scope Keywords

| Keyword | What it scans |
|---|---|
| `here` | Files in the same folder as the script |
| `deep` | Files in the script folder AND all subfolders (recursive) |
| `"some/path"` | Files in a specific folder |

```
for_each file_in here           # current directory, files only
for_each file_in deep           # recursive, files only
for_each file_in "C:/Downloads" # specific path, files only
for_each folder_in here         # current directory, folders only
```

> **Tip:** If your variable name starts with `folder` or `dir`, DoScript
> automatically scans for directories instead of files.

---

## Auto-Injected Variables

For every file in the loop, these variables are created automatically.
Replace `file` with whatever prefix you chose.

| Variable | Contains |
|---|---|
| `file_name` | Full filename, e.g. `report.pdf` |
| `file_path` | Absolute path, e.g. `C:/Downloads/report.pdf` |
| `file_ext` | Extension including dot, e.g. `.pdf` |
| `file_size` | Size in bytes |
| `file_size_kb` | Size in kilobytes |
| `file_size_mb` | Size in megabytes |
| `file_is_dir` | `true` if it's a folder |
| `file_is_empty` | `true` if size is 0 |
| `file_created` | Creation timestamp (Unix) |
| `file_modified` | Last modified timestamp (Unix) |
| `file_is_old_days` | Age in days since last modification |
| `file_is_old_hours` | Age in hours |
| `file_is_old_months` | Age in months |
| `file_content` | Full text content (text files only — see below) |

---

## if_ends_with

A special shorthand for checking file extensions inside `for_each`.
Cleaner than writing a full `if` condition.

```
for_each file_in here
    if_ends_with ".txt"
        say 'Text file: {file_name}'
    end_if

    if_ends_with ".pdf"
        say 'PDF file: {file_name}'
    end_if
end_for
```

> Note: `if_ends_with` does **not** support `else`. Use the flag pattern
> from Lesson 02 when you need else-if behaviour.

---

## if_file_contains / if_file_not_contains

Check whether the file's text content includes a keyword.
Only works for text files (`.txt`, `.md`, `.log`, `.json`, `.py`, etc.).

```
for_each file_in here
    if_file_contains "ERROR"
        say 'Has errors: {file_name}'
        move file to "errors"
    end_if

    if_file_not_contains "reviewed"
        say 'Not reviewed: {file_name}'
    end_if
end_for
```

---

## Skipping Files with continue

```
for_each file_in here
    # Skip this script itself
    if_ends_with ".do"
        continue
    end_if

    say 'Processing: {file_name}'
end_for
```

---

## Using a Custom Prefix

The prefix can be anything — it just sets the variable names.

```
for_each photo_in "C:/Pictures"
    say 'Photo: {photo_name} ({photo_size_mb}MB)'
end_for

for_each folder_in here
    say 'Folder: {folder_name}'
    if folder_is_empty
        delete folder_path
    end_if
end_for
```

---

## Practical Example — Sort Downloads by Extension

```
# sort-downloads.do
global_variable = file, moved

make folder "Images"
make folder "Videos"
make folder "Documents"
make folder "Archives"
make folder "Programs"
make folder "Other"

for_each file_in here

    if_ends_with ".do"
        continue
    end_if

    moved = 0

    if moved == 0
        if_ends_with ".jpg"
            move file to "Images"
            moved = 1
        end_if
    end_if

    if moved == 0
        if_ends_with ".png"
            move file to "Images"
            moved = 1
        end_if
    end_if

    if moved == 0
        if_ends_with ".mp4"
            move file to "Videos"
            moved = 1
        end_if
    end_if

    if moved == 0
        if_ends_with ".pdf"
            move file to "Documents"
            moved = 1
        end_if
    end_if

    if moved == 0
        if_ends_with ".zip"
            move file to "Archives"
            moved = 1
        end_if
    end_if

    if moved == 0
        if_ends_with ".exe"
            move file to "Programs"
            moved = 1
        end_if
    end_if

    if moved == 0
        move file to "Other"
    end_if

end_for

say "Done!"
```

---

## for_each_line

Iterates over the lines of a text file instead of files in a directory.

```
global_variable = line

for_each_line line in "servers.txt"
    say 'Pinging: {line}'
    ping line
end_for
```

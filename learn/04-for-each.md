# Lesson 04 — for_each (File Iteration)

`for_each` is one of the most powerful features in DoScript. It iterates
over files, folders, or list items and auto-injects a rich set of variables
for each item.

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
| `file_content` | Full text content (text files only) |

---

## if_ends_with

A special shorthand for checking file extensions inside `for_each`.

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

> **Note:** `if_ends_with` does **not** support `else`. Use `else_if file_ext ==`
> for chains where you need a fallthrough (see the sort example below).

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

## Age Filters — older_than / newer_than

Filter files by last-modified time without writing any comparison logic.

```
# Delete files older than 30 days
for_each old_file_in here older_than 30 days
    delete old_file_path
end_for
say 'Deleted {loop_count} old files.'

# Log files changed in the last hour
for_each f_in deep newer_than 1 hour
    log 'Recently changed: {f_name}'
end_for
```

Supported units: `seconds`, `minutes`, `hours`, `days`, `months`, `years`.
Works with `here`, `deep`, and directory paths.

---

## {loop_count}

After any `for_each` loop ends, `loop_count` holds the number of items
that were iterated. No declaration needed.

```
for_each file_in here
    copy file to "backup"
end_for
say 'Copied {loop_count} files.'
```

---

## Iterating a List Variable

`for_each` also works on a variable holding a list (created with `split()`
or `list_add`):

```
global_variable = fruits, fruit
fruits = split("apple,banana,mango", ",")
list_add fruits "pear"

for_each fruit in fruits
    say 'Fruit: {fruit}'
end_for
say 'Total: {loop_count}'
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

## for_each_line

Iterates over the lines of a text file instead of files in a directory.

```
global_variable = line

for_each_line line in "servers.txt"
    say 'Pinging: {line}'
    ping line
end_for
```

---

## Practical Example — Sort Downloads by Extension

Using `else_if file_ext ==` chains for a clean single-pass sort:

```
# sort-downloads.do
# Test first: python doscript.py sort-downloads.do --dry-run

for_each file_in here
    if_ends_with ".do"
        continue
    end_if

    if file_ext == ".jpg"
        make folder "Images"
        move file to "Images"
    else_if file_ext == ".png"
        make folder "Images"
        move file to "Images"
    else_if file_ext == ".mp4"
        make folder "Videos"
        move file to "Videos"
    else_if file_ext == ".pdf"
        make folder "Documents"
        move file to "Documents"
    else_if file_ext == ".zip"
        make folder "Archives"
        move file to "Archives"
    else_if file_ext == ".exe"
        make folder "Programs"
        move file to "Programs"
    else
        make folder "Other"
        move file to "Other"
    end_if
end_for

say 'Sorted {loop_count} files.'
```

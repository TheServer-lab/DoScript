# Lesson 03 — File Operations

## make folder

Creates a directory (and any missing parent directories).
Safe to call even if the folder already exists.

```
make folder "output"
make folder "C:/Projects/MyApp/logs"
make folder '{today}_backup'       # single quotes to interpolate
make folder '{downloads}/Sorted'   # built-in path variable
```

---

## make file

Creates a new file. The path can be double-quoted, single-quoted (with
interpolation), or a bare variable name.

```
make file "notes.txt"                          # empty file
make file "notes.txt" with "Hello, World!"     # with content
make file 'log_{today}.txt' with "Started"     # single-quoted, interpolated name
make file dest_path with "Started"             # bare variable as path
```

### Multi-line content with `end_file`

For structured files — configs, templates, scripts — use the heredoc form.
Variables interpolate inside the block.

```
global_variable = app_name, port
app_name = "MyServer"
port = 8080

make file "config.ini" with
    [server]
    name = {app_name}
    port = {port}
    debug = false
end_file
```

Single-quoted paths work here too:

```
make file 'configs/{app_name}.ini' with
    port = {port}
end_file
```

---

## rename

Rename a file or folder in place without changing its directory.

```
rename "draft_v1.txt" to "final.txt"
rename "old-folder" to "archive-2024"
```

Use `rename` when you want a clean new name. Use `move` when changing
both the name and location in one step.

---

## copy

```
copy "source.txt" to "backup/source.txt"
copy "C:/data/file.csv" to "D:/archive/file.csv"
```

---

## move

`move` moves a file to a folder or renames it by moving to a new name.

```
# Move to a folder
move file to "Documents"
move file to "C:/Users/User/Documents"

# Rename by moving to a new name
move file to "renamed_file.txt"
move file to 'report_{today}.pdf'
```

---

## delete

Deletes a file or an entire folder (recursively).

```
delete "temp.txt"
delete "C:/Temp/old_logs"
delete file_path           # use the path variable from for_each
```

---

## exists()

Returns `true` or `false`. Use in `if` conditions.

```
if exists("config.json")
    say "Config found!"
end_if

if exists("output") == false
    make folder "output"
end_if
```

---

## replace_in_file

Find and replace text inside a file.

```
replace_in_file "config.txt" "localhost" "192.168.1.100"
replace_in_file "template.html" "{{NAME}}" "Alice"
```

---

## zip and unzip

```
zip "my_folder" to "my_folder.zip"
zip "report.pdf" to "report.zip"

unzip "archive.zip"                     # extracts to current directory
unzip "archive.zip" to "extracted"      # extracts to named folder
```

List contents without extracting:

```
global_variable = contents
zip_list "archive.zip" to contents
say contents
```

---

## read_content

Read an entire file's text into a variable.

```
global_variable = fileText
read_content "notes.txt" into fileText
say fileText
```

---

## Checking File Properties

Inside a `for_each` loop these are injected automatically (see Lesson 04),
but you can also use `exists()` and `read_file()` in expressions:

```
global_variable = text
text = read_file("notes.txt")

if contains(text, "ERROR")
    say "Log contains errors!"
end_if
```

---

## Practical Example — Backup a folder

```
# backup.do
global_variable = dest

dest = '{desktop}/backup_{today}.zip'

say 'Backing up to {dest}...'
zip "." to dest
say "Backup complete!"
```

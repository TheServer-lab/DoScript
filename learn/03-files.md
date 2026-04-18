# Lesson 03 — File Operations

## make folder

Creates a directory (and any missing parent directories).
Safe to call even if the folder already exists.

```
make folder "output"
make folder "C:/Projects/MyApp/logs"
make folder '{today}_backup'       # single quotes to interpolate
```

---

## make file

Creates a new file. Optionally write content into it.

```
make file "notes.txt"                          # empty file
make file "notes.txt" with "Hello, World!"     # with content
make file 'log_{today}.txt' with "Started"     # interpolated name
```

---

## copy

```
copy "source.txt" to "backup/source.txt"
copy "C:/data/file.csv" to "D:/archive/file.csv"
```

---

## move (also used for rename)

`move` serves double duty — it both moves files to folders and renames them.

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
global_variable = src, dest

src  = "C:/Projects/MyApp"
dest = 'C:/Backups/MyApp_{today}.zip'

say 'Backing up to {dest}...'
zip src to dest
say "Backup complete!"
```

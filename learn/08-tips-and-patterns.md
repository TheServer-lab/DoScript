# Lesson 08 — Tips, Patterns and Common Gotchas

Real lessons learned from community scripts.

---

## Quote Gotcha — The #1 Mistake

Using double quotes when you need variable interpolation produces silent
wrong output — no error, just a literal `{varName}` in your output.

```
global_variable = name
name = "Alice"

say "Hello {name}"    # ❌  prints: Hello {name}
say 'Hello {name}'    # ✅  prints: Hello Alice
```

**Rule:** Use `'single quotes'` for any string that contains `{variables}`.

---

## move vs copy

`move` removes the source. `copy` keeps it. Use `move` when organising
files so you don't end up with duplicates.

```
move file to "Sorted/Images"    # file is gone from original location
copy file to "Backup/Images"    # file stays in original location too
```

---

## Deleting Safely

Always check `exists()` before deleting if the file might not be there.

```
if exists("temp.zip")
    delete "temp.zip"
end_if
```

Or use a function:

```
function safe_delete path
    if exists(path)
        delete path
    end_if
end_function
```

---

## The counter Pattern

For generating sequentially named files or tracking progress:

```
global_variable = counter
counter = 0

loop forever
    counter = counter + 1
    make folder '{counter}'
    wait 1
end_loop
```

---

## The moved Flag Pattern

Since `if_ends_with` has no `else`, use an integer flag to simulate
`else-if` chains cleanly:

```
global_variable = moved
moved = 0

if moved == 0
    if_ends_with ".jpg"
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
    move file to "Other"   # catch-all
end_if
```

---

## Skipping your own Script

When running a `for_each` inside the same folder as your `.do` file,
always skip the script itself first:

```
for_each file_in here
    if_ends_with ".do"
        continue
    end_if
    # ... process everything else
end_for
```

---

## Path Separators

DoScript accepts both `/` and `\` on Windows. Forward slashes `/` are
safer and more readable:

```
downloads = "C:/Users/User/Downloads"   # ✅ works on Windows
downloads = "C:\Users\User\Downloads"   # ✅ also works, but harder to read
```

---

## do_new — Launch Another Script

Use `do_new` to chain scripts together or break a large task into modules:

```
do_new "cleanup.do"
do_new "backup.do"
do_new "report.do"
```

---

## --dry-run Mode

Run any script with `--dry-run` to preview what it would do without
actually making changes. All `make`, `move`, `delete`, `download` etc.
are replaced with `[DRY]` log messages.

```
python doscript.py sort-downloads.do --dry-run
```

This is especially valuable before running any script that modifies or
deletes files.

---

## Built-in Expressions

These work inside `if` conditions and assignments:

| Expression | What it does |
|---|---|
| `exists("path")` | Check if a file/folder exists |
| `contains(text, "word")` | Case-insensitive substring check |
| `contains_case(text, "Word")` | Case-sensitive substring check |
| `notcontains(text, "word")` | True if text does NOT contain word |
| `startswith(text, "prefix")` | Prefix check |
| `endswith(text, ".txt")` | Suffix check |
| `extension(filename)` | Returns `.txt`, `.pdf`, etc. |
| `read_file("path")` | Returns file contents as a string |
| `split(text, ",")` | Splits string into a list |

---

## random_number and random_string

Useful for generating unique names:

```
global_variable = rnd
random_number 1000 9999 to rnd
make file 'temp_{rnd}.txt'

random_string 8 to rnd
make folder '{rnd}_session'
```

---

## Loops with wait to Avoid Hammering the System

When creating many files or folders in a loop, add a small `wait` to
avoid overwhelming the filesystem or CPU:

```
loop forever
    counter = counter + 1
    make folder '{counter}'
    wait 1      # 1 second between each
end_loop
```

---

## Script Organisation Tips

- Put `global_variable` declarations at the **top** of your script
- Use `say ""` (empty say) to add blank lines for readability
- Use `pause` at the **end** of installer/interactive scripts so the
  window stays open after completion
- Use `log` / `warn` / `error` instead of `say` for unattended scripts
  — they make logs easier to scan
- Break big scripts into multiple `.do` files and use `include` or `do_new`

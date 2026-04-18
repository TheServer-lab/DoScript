# Lesson 09 - Strings and Text Helpers

DoScript v0.6.9 adds several built-in helpers for cleaning and transforming
text directly inside assignments and conditions.

---

## Available Helpers

| Helper | What it returns |
|---|---|
| `length(text)` | Number of characters |
| `trim(text)` | Text with leading/trailing whitespace removed |
| `lower(text)` | Lowercase text |
| `upper(text)` | Uppercase text |
| `replace(text, old, new)` | Text with all matches replaced |

---

## Basic Example

```
global_variable = raw_name, clean_name, loud_name, short_name, chars

raw_name = "  Alice Smith  "
clean_name = trim(raw_name)
loud_name = upper(clean_name)
short_name = replace(clean_name, " Smith", "")
chars = length(clean_name)

say 'Clean: {clean_name}'
say 'Upper: {loud_name}'
say 'Short: {short_name}'
say 'Chars: {chars}'
```

---

## Normalising User Input

```
global_variable = answer, normalized

ask answer "Continue? (yes/no)"
normalized = lower(trim(answer))

if normalized == "yes"
    say "Continuing..."
else_if normalized == "no"
    say "Stopping."
else
    say "Please answer yes or no."
end_if
```

---

## Cleaning File Names

```
global_variable = original, clean

original = " Monthly Report FINAL .txt "
clean = trim(original)
clean = replace(clean, " ", "_")
clean = lower(clean)

say 'New name: {clean}'
```

---

## Combining Helpers

Helpers can be nested:

```
global_variable = result

result = upper(trim("  hello world  "))
say '{result}'    # HELLO WORLD
```

---

## Tip

Use text helpers in assignments first, then reuse the cleaned variable in
your `if` checks and file operations. That keeps scripts easier to read.

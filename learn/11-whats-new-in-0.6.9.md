# Lesson 11 - What's New in v0.6.9

This short lesson covers the biggest workflow improvements added in
DoScript v0.6.9.

---

## 1. else_if

You no longer need nested fallback `if` blocks for common condition chains.

```
global_variable = score
score = 82

if score >= 90
    say "Grade A"
else_if score >= 80
    say "Grade B"
else
    say "Keep going"
end_if
```

---

## 2. Indexed loop

`loop` can now expose the current iteration:

```
global_variable = total
total = 0

loop 4 as i
    total = total + i
end_loop

say 'Total: {total}'
```

This also works with `loop forever as i`.

---

## 3. String helpers

You can now transform text directly in expressions:

```
global_variable = name
name = upper(trim("  alice  "))
say '{name}'
```

---

## 4. Safer process execution

Use `execute_command` when you want to avoid shell parsing:

```
execute_command "git" "status"
```

---

## Suggested Next Steps

Read these follow-up lessons next:

- [`09-strings-and-text.md`](09-strings-and-text.md)
- [`10-safer-commands.md`](10-safer-commands.md)
- [`02-control-flow.md`](02-control-flow.md)

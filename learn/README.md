# DoScript — Learning Materials

Welcome to the DoScript `/learn` folder. These guides will take you from
zero to writing real automation scripts, step by step.

---

## Lessons

| File | What you'll learn |
|---|---|
| [01-basics.md](01-basics.md) | Variables, `say`, `ask`, comments, single vs double quotes |
| [02-control-flow.md](02-control-flow.md) | `if/else`, `loop`, `repeat`, `break`, `continue` |
| [03-files.md](03-files.md) | `make folder/file`, `copy`, `move`, `delete`, `exists()` |
| [04-for-each.md](04-for-each.md) | Iterating files, auto-injected variables, `if_ends_with` |
| [05-functions.md](05-functions.md) | Defining functions, macros (`make a_command`) |
| [06-network.md](06-network.md) | `download`, `http_get/post`, `ping`, `open_link` |
| [07-installers.md](07-installers.md) | Writing real installer scripts end-to-end |
| [08-tips-and-patterns.md](08-tips-and-patterns.md) | Real patterns from community scripts, common gotchas |

---

## Quick Reference

```
# This is a comment
global_variable = myVar       # declare before use
myVar = "hello"               # assign
say 'Value is: {myVar}'       # print (single quotes interpolate)
ask answer "Question:"        # user input
```

---

## Running a Script

```
python doscript.py myscript.do
python doscript.py myscript.do --dry-run    # preview without side effects
python doscript.py myscript.do --verbose    # extra logging
```

---

## DoScript Version

These materials cover **DoScript v0.6.7**.

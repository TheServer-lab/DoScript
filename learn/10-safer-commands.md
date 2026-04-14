# Lesson 10 - Safer Command Execution

DoScript gives you two main ways to run commands:

- `run` - flexible, but uses the system shell
- `execute_command` - safer, because it passes command parts directly

---

## Use execute_command by Default

```
execute_command "git" "status"
execute_command "python" "--version"
```

This is the best choice when you already know the program and arguments you
want to run.

---

## Why It Is Safer

`run` goes through the shell, so shell characters may be interpreted:

```
run "git status"
```

`execute_command` does not do that:

```
execute_command "git" "status"
```

That makes it a better default when command parts come from variables or
user input.

---

## Passing Multiple Arguments

```
execute_command "python" "-m" "http.server" "8000"
```

Each quoted item becomes one argument.

---

## Using Variables

```
global_variable = repo_cmd, repo_arg

repo_cmd = "git"
repo_arg = "status"

execute_command repo_cmd repo_arg
```

---

## When to Still Use run

Use `run` when you specifically want shell behavior, shell built-ins, or a
single shell command string:

```
run "dir"
run "echo Hello > out.txt"
```

If you do this, avoid feeding untrusted input into the command string.

---

## Rule of Thumb

- Use `execute_command` for programs and arguments
- Use `run` only when you intentionally need the shell

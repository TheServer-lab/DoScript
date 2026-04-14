# Lesson 05 — Functions and Macros

## Functions

Define reusable blocks of logic with `function` / `end_function`.

```
function greet name
    say 'Hello, {name}!'
end_function

greet("Alice")
greet("Bob")
```

### Return values

```
function add a b
    return a + b
end_function

global_variable = result
result = add(10, 5)
say 'Result: {result}'     # prints: Result: 15
```

### Local variables

Variables declared inside a function with `local_variable` are scoped to
that function call and don't leak into the global scope.

```
function calculate x y
    local_variable = temp
    temp = x * y
    return temp
end_function
```

### Functions calling functions

```
function square n
    return n * n
end_function

function sum_of_squares a b
    local_variable = sa, sb
    sa = square(a)
    sb = square(b)
    return sa + sb
end_function

global_variable = total
total = sum_of_squares(3, 4)
say 'Sum of squares: {total}'    # 25
```

---

## Macros (make a_command)

Macros are named blocks of statements with no parameters and no return
value. Use them to group side-effect actions you want to repeat.

```
make a_command print_separator
    say "--------------------"
end_command

run "print_separator"
say "Section One"
run "print_separator"
say "Section Two"
run "print_separator"
```

---

## Functions vs Macros

| | Function | Macro |
|---|---|---|
| Parameters | ✅ Yes | ❌ No |
| Return value | ✅ Yes | ❌ No |
| Call syntax | `myFunc(args)` | `run "myMacro"` |
| Best for | Calculations, reusable logic | Repeated action sequences |

---

## include

Split your scripts across multiple files and include them.

```
include "helpers.do"

# Now you can call functions defined in helpers.do
greet("World")
```

> Each file is only included once, even if `include` appears multiple times.

---

## Practical Example — A Logging Library

```
# logger.do
# Include this file in other scripts with: include "logger.do"

global_variable = logPath
logPath = "run.log"

function log_info msg
    say '[INFO] {msg}'
end_function

function log_warn msg
    say '[WARN] {msg}'
end_function

function log_error msg
    say '[ERROR] {msg}'
end_function

make a_command log_separator
    say "==============================="
end_command
```

Usage in another script:

```
include "logger.do"

log_info("Script started")
run "log_separator"
log_warn("Low disk space")
log_error("File not found")
```

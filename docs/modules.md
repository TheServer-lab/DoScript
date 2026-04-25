# DoScript Standard Modules

Install any module with:
```
python doscript.py install_module <name>
```

Use in your scripts with:
```
use_module "<name>"
```

Each module is loaded once even if `use_module` appears multiple times.
All functions are available globally after loading.

---

## Index

| Module | Description |
|---|---|
| [math](#math) | Arithmetic helpers, rounding, number theory |
| [strings](#strings) | String padding, searching, transformation |
| [files](#files) | Path helpers, backup, folder utilities |
| [datetime](#datetime) | Greetings, month/day names, time formatting |
| [network](#network) | Connectivity checks, URL helpers, HTTP safety |
| [system](#system) | OS detection, process control, env vars |
| [lists](#lists) | List search, stats, joining, filling |
| [cli](#cli) | Banners, step output, yes/no helpers, prompts |

---

## math

> `use_module "math"`

Arithmetic utilities, rounding, number theory, and safe division.

| Function | Signature | Description |
|---|---|---|
| `abs_val` | `abs_val(n)` | Absolute value of n |
| `clamp` | `clamp(value, min_val, max_val)` | Clamp value between min and max |
| `lerp` | `lerp(a, b, t)` | Linear interpolation between a and b at factor t (0.0–1.0) |
| `round_to` | `round_to(value, places)` | Round value to N decimal places |
| `sign` | `sign(n)` | Returns 1, -1, or 0 based on sign of n |
| `is_even` | `is_even(n)` | True if n is even |
| `is_odd` | `is_odd(n)` | True if n is odd |
| `factorial` | `factorial(n)` | n! — factorial of n (n ≥ 0) |
| `fibonacci` | `fibonacci(n)` | nth Fibonacci number (0-indexed) |
| `gcd` | `gcd(a, b)` | Greatest common divisor |
| `lcm` | `lcm(a, b)` | Least common multiple |
| `power` | `power(base, exp)` | base raised to the power of exp (integer) |
| `safe_divide` | `safe_divide(a, b)` | Divides a by b; returns 0 if b is zero |

**Example:**
```
use_module "math"

global_variable = result

result = clamp(150, 0, 100)
say 'Clamped: {result}'       # 100

result = power(2, 8)
say 'Two to the 8th: {result}'  # 256

result = safe_divide(10, 0)
say 'Safe divide: {result}'     # 0

result = fibonacci(10)
say 'Fibonacci 10: {result}'    # 55
```

---

## strings

> `use_module "strings"`

String padding, repetition, searching, and validation.

| Function | Signature | Description |
|---|---|---|
| `pad_left` | `pad_left(s, width, char)` | Left-pad s to width using char |
| `pad_right` | `pad_right(s, width, char)` | Right-pad s to width using char |
| `repeat_str` | `repeat_str(s, n)` | Repeat s n times |
| `starts_with` | `starts_with(s, prefix)` | True if s starts with prefix |
| `ends_with` | `ends_with(s, suffix)` | True if s ends with suffix |
| `str_contains` | `str_contains(s, sub)` | True if s contains sub (case-insensitive) |
| `capitalize` | `capitalize(s)` | Uppercase first char, lowercase rest |
| `str_reverse` | `str_reverse(s)` | Reverse the characters of s |
| `count_occurrences` | `count_occurrences(s, sub)` | Count how many times sub appears in s |
| `truncate` | `truncate(s, max_len, suffix)` | Truncate s to max_len, appending suffix |
| `str_is_empty` | `str_is_empty(s)` | True if s is blank or whitespace only |
| `str_is_number` | `str_is_number(s)` | True if s looks like a number |

**Example:**
```
use_module "strings"

global_variable = result

result = pad_left("42", 6, "0")
say 'Padded: {result}'             # 000042

result = repeat_str("=-", 10)
say '{result}'                     # =-=-=-=-=-=-=-=-=-=-

result = count_occurrences("banana", "a")
say 'Count: {result}'              # 3

result = truncate("Hello World", 7, "...")
say 'Truncated: {result}'          # Hello...
```

---

## files

> `use_module "files"`

Path manipulation, safe folder creation, file backup, and counting.

| Function | Signature | Description |
|---|---|---|
| `file_exists` | `file_exists(path)` | True if path points to an existing file or folder |
| `folder_exists` | `folder_exists(path)` | Alias of file_exists for readability |
| `get_extension` | `get_extension(filename)` | Returns the extension including dot, e.g. `.pdf` |
| `get_filename` | `get_filename(path)` | Returns just the filename portion of a path |
| `get_basename` | `get_basename(path)` | Returns filename without extension |
| `ensure_folder` | `ensure_folder(path)` | Creates the folder if it does not already exist |
| `file_size_label` | `file_size_label(bytes)` | Converts a byte count to `"2.0 KB"`, `"1.4 MB"`, etc. |
| `backup_file` | `backup_file(path, dest_folder)` | Copies file to dest_folder with today's date appended |
| `count_files_in` | `count_files_in(folder)` | Counts files in folder (non-recursive) |
| `join_path` | `join_path(base, rel)` | Joins two path segments with `/` |

**Example:**
```
use_module "files"

global_variable = ext, label

ext = get_extension("report_final.pdf")
say 'Extension: {ext}'             # .pdf

ensure_folder "output/logs"        # creates if missing

backup_file "config.json" "backups"
# copies to backups/config_2025-04-25.json

label = file_size_label(1572864)
say 'Size: {label}'                # 1.5 MB
```

---

## datetime

> `use_module "datetime"`

Greetings, weekday/month names, leap year logic, and time formatting.

| Function | Signature | Description |
|---|---|---|
| `time_greeting` | `time_greeting()` | "Good morning/afternoon/evening" based on current hour |
| `is_morning` | `is_morning()` | True if current hour is before noon |
| `is_afternoon` | `is_afternoon()` | True if current hour is 12–16 |
| `is_evening` | `is_evening()` | True if current hour is 17 or later |
| `day_name` | `day_name(n)` | Full name of weekday n (1=Monday … 7=Sunday) |
| `month_name` | `month_name(n)` | Full month name for month number n (1–12) |
| `is_leap_year` | `is_leap_year(y)` | True if y is a leap year |
| `days_in_month` | `days_in_month(m, y)` | Number of days in month m of year y |
| `format_date` | `format_date(y, m, d)` | Returns `"25 April 2025"` |
| `format_time` | `format_time(h, m, s)` | Returns `"09:05:03"` (zero-padded) |
| `elapsed_seconds` | `elapsed_seconds(start_ts)` | Seconds since a Unix timestamp |
| `timestamp_label` | `timestamp_label(ts)` | Converts seconds to `"1h 2m 5s"` |

**Example:**
```
use_module "datetime"

global_variable = greeting, mname, label, start_ts

greeting = time_greeting()
say '{greeting}!'                  # Good morning!

mname = month_name(month)
say 'It is {mname} {year}'         # It is April 2025

start_ts = time
# ... do work ...
label = timestamp_label(elapsed_seconds(start_ts))
say 'Finished in {label}'          # Finished in 0s
```

---

## network

> `use_module "network"`

Connectivity checking, URL encoding, and HTTP status labels.

| Function | Signature | Description |
|---|---|---|
| `is_online` | `is_online()` | True if internet appears reachable |
| `assert_online` | `assert_online()` | Exits the script if there is no internet connection |
| `get_status_label` | `get_status_label(code)` | Human-readable HTTP status, e.g. `"404 Not Found"` |
| `url_encode_spaces` | `url_encode_spaces(s)` | Replaces spaces with `%20` |

**Note:** For downloading and HTTP requests use the built-in commands
`download`, `http_get`, `http_post` directly (see Lesson 06). Wrap them
in `try/catch NetworkError` for resilience.

**Example:**
```
use_module "network"

global_variable = response, label

assert_online()                    # exits if offline

http_get "https://wttr.in/?format=3" to response
say 'Weather: {response}'

label = get_status_label(404)
say '{label}'                      # 404 Not Found

global_variable = query
query = url_encode_spaces("New York")
say '{query}'                      # New%20York
```

---

## system

> `use_module "system"`

OS detection, process control, environment variables, and privileged ops.

| Function | Signature | Description |
|---|---|---|
| `print_system_info` | `print_system_info()` | Prints all built-in path variables and current date/time |
| `require_windows` | `require_windows()` | Exits if not running on Windows |
| `require_unix` | `require_unix()` | Exits if running on Windows |
| `is_process_alive` | `is_process_alive(name)` | True if a process with that name is running |
| `safe_kill` | `safe_kill(name)` | Kills a process only if it is currently running |
| `open_folder` | `open_folder(path)` | Opens a folder in the system file explorer |
| `get_env_or_default` | `get_env_or_default(var_name, default_val)` | Returns env var value, or default if unset |
| `assert_admin` | `assert_admin()` | Exits with an error if not running as admin/root |
| `pause_seconds` | `pause_seconds(n)` | Pauses execution for n seconds |

**Exposes constant:** `SYS_PLATFORM` (set to `"unknown"` at load time; update it yourself if needed)

**Example:**
```
use_module "system"

print_system_info()

global_variable = api_url

api_url = get_env_or_default("MY_API_URL", "https://api.example.com")
say 'Using: {api_url}'

if is_process_alive("oldservice.exe")
    safe_kill "oldservice.exe"
    say "Stopped old service."
end_if

pause_seconds(2)
say "Resuming..."
```

---

## lists

> `use_module "lists"`

List search, statistics, joining, and construction helpers.

| Function | Signature | Description |
|---|---|---|
| `list_contains` | `list_contains(lst, item)` | True if lst contains item |
| `list_first` | `list_first(lst)` | First element of lst |
| `list_last` | `list_last(lst)` | Last element of lst |
| `list_sum` | `list_sum(lst)` | Sum of all numeric items |
| `list_min` | `list_min(lst)` | Smallest numeric value |
| `list_max` | `list_max(lst)` | Largest numeric value |
| `list_average` | `list_average(lst)` | Arithmetic mean |
| `list_join` | `list_join(lst, sep)` | Join all items into a string with sep between them |
| `list_is_empty` | `list_is_empty(lst)` | True if lst has no elements |
| `list_index_of` | `list_index_of(lst, item)` | Zero-based index of item, or -1 if not found |
| `list_fill` | `list_fill(n, value)` | New list of length n filled with value |
| `list_count_where_equal` | `list_count_where_equal(lst, value)` | Count items that equal value |

**Example:**
```
use_module "lists"

global_variable = scores, total, avg, top, joined

scores = split("85,92,70,95,88", ",")

total  = list_sum(scores)
avg    = list_average(scores)
top    = list_max(scores)
joined = list_join(scores, " | ")

say 'Scores : {joined}'           # 85 | 92 | 70 | 95 | 88
say 'Total  : {total}'            # 430
say 'Average: {avg}'              # 86.0
say 'Top    : {top}'              # 95

if list_contains(scores, "70")
    say "One score was 70."
end_if
```

---

## cli

> `use_module "cli"`

Formatted output, banners, step indicators, and user-input helpers.

| Function | Signature | Description |
|---|---|---|
| `print_banner` | `print_banner(title)` | Prints a ════ banner box around title |
| `print_separator` | `print_separator()` | Prints a ──── divider line |
| `print_header` | `print_header(title)` | Prints a section title with a divider below |
| `print_success` | `print_success(msg)` | Prints `  ✓  msg` |
| `print_warning` | `print_warning(msg)` | Prints `  ⚠  msg` |
| `print_error` | `print_error(msg)` | Prints `  ✗  msg` |
| `print_step` | `print_step(n, msg)` | Prints `  [n]  msg` |
| `is_yes` | `is_yes(answer)` | True if answer is y/yes (any case) |
| `is_no` | `is_no(answer)` | True if answer is n/no (any case) |
| `use_default_if_empty` | `use_default_if_empty(value, default_val)` | Returns value, or default if blank |
| `require_arg` | `require_arg(n, name)` | Exits if CLI argument n was not provided |
| `print_kv` | `print_kv(key, value)` | Prints `  key  :  value` |
| `print_done` | `print_done()` | Prints a standard "All done!" completion block |

**Exposes constants:** `CLI_SEP_CHAR` (`"─"`), `CLI_SEP_WIDTH` (`40`)

**Example:**
```
use_module "cli"

global_variable = confirm, port

print_banner "My App Installer v2.0"

print_header "Step 1 — Configuration"
ask port "Port number [8080]:"
port = use_default_if_empty(port, "8080")
print_kv "Port" port

print_header "Step 2 — Confirmation"
ask confirm "Proceed with install? (y/n)"
if is_yes(confirm)
    print_step 1 "Creating folders..."
    make folder 'C:/MyApp'
    print_success "Folders created."

    print_step 2 "Downloading..."
    try
        download "https://example.com/app.zip" to "C:/MyApp/app.zip"
        print_success "Download complete."
    catch NetworkError
        print_error "Download failed."
        exit 1
    end_try

    print_done()
else
    print_warning "Install cancelled."
end_if

pause
```

---

## Using Multiple Modules Together

Modules compose cleanly — just `use_module` each one you need:

```
use_module "cli"
use_module "datetime"
use_module "network"
use_module "files"

global_variable = greeting

greeting = time_greeting()
print_banner 'Backup Tool — {greeting}!'

assert_online()

ensure_folder '{desktop}/Backups'
backup_file "project.zip" '{desktop}/Backups'

print_done()
pause
```

---

## Writing Your Own Modules

Any `.do` file can be a module. Follow these conventions:

- Use a `# module-name.do — description` comment at the top
- Prefix internal (private) variables with `_` to avoid name collisions
- Declare all module-level variables with `global_variable` at the top of the file
- Document each function with a comment block above it

```
# mymodule.do — Does useful things
# Usage: use_module "mymodule"

global_variable = MY_CONSTANT
MY_CONSTANT = 42

function do_thing(x)
    return x * MY_CONSTANT
end_function
```

Place the file in `C:\Program Files (x86)\DoScript\modules\` (Windows)
or `~/DoScript/modules/` (Unix/macOS) to make it globally available,
or in a local `modules/` folder next to your script for project-specific use.

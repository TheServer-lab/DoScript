# Lesson 06 — Network

## download

Downloads a file from a URL and saves it to a local path.

```
download "https://example.com/file.zip" to "file.zip"
download "https://example.com/data.csv" to '{downloads}/data.csv'
```

Always wrap downloads in `try/catch NetworkError` so your script handles
connection failures gracefully:

```
try
    download "https://example.com/app.zip" to "app.zip"
    say "Download complete!"
catch NetworkError
    say "Download failed. Check your internet connection."
    exit 1
end_try
```

---

## http_get / http_post / http_put / http_delete

Makes HTTP requests and stores the response body in a variable.

```
global_variable = response, result

http_get  "https://api.example.com/status" to response
http_post "https://api.example.com/data" "{\"key\":\"value\"}" to result
http_put  "https://api.example.com/item/1" "{\"name\":\"new\"}" to result
http_delete "https://api.example.com/item/1" to result
```

---

## ping

Pings a host. Raises `NetworkError` if unreachable.

```
try
    ping "8.8.8.8"
    say "Network is up!"
catch NetworkError
    say "No network connection."
end_try
```

---

## open_link

Opens a URL in the system's default browser.

```
open_link "https://github.com/TheServer-lab/DoScript"
```

---

## upload

Uploads a local file via HTTP POST.

```
upload "report.pdf" to "https://example.com/upload"
```

---

## set_env / get_env()

Write and read environment variables. Essential for installers that need
to make a path available to other programs.

```
set_env "MY_APP_HOME" to "C:/MyApp"

global_variable = path
path = get_env("MY_APP_HOME")
say 'App is at: {path}'
```

---

## is_running()

Check whether a process is currently running. Returns `true` or `false`.

```
global_variable = running
running = is_running("notepad.exe")

if running == true
    say "Notepad is open"
end_if

if not is_running("myservice")
    run "myservice --start"
end_if
```

---

## run_from_web

Fetch and run a `.do` script from
[TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage)
without downloading anything manually.

```
run_from_web cleaner.do
run_from_web git-setup.do
run_from_web tools/setup-python.do
```

The `.do` extension is optional. You can also use a variable:

```
global_variable = tool
tool = "cleaner"
run_from_web '{tool}.do'
```

The fetched script shares your current variable scope — any variables it
sets are visible in your script after it returns.

Use `--dry-run` to preview the URL without fetching:

```
python doscript.py myscript.do --dry-run
# [DRY] run_from_web: would fetch and run https://raw.githubusercontent.com/...
```

---

## Practical Example — Check connectivity before downloading

```
# safe-download.do
global_variable = url, dest

url  = "https://example.com/installer.msi"
dest = "installer.msi"

say "Checking network..."
try
    ping "8.8.8.8"
    say "Network OK."
catch NetworkError
    say "No internet connection. Aborting."
    exit 1
end_try

say "Downloading..."
try
    download url to dest
    say 'Saved to: {dest}'
catch NetworkError
    say "Download failed."
    exit 1
end_try

say "Done!"
```

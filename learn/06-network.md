# Lesson 06 — Network

## download

Downloads a file from a URL and saves it to a local path.

```
download "https://example.com/file.zip" to "file.zip"
download "https://example.com/data.csv" to "C:/data/data.csv"
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

## http_get

Makes an HTTP GET request and stores the response body in a variable.

```
global_variable = response
http_get "https://api.example.com/status" to response
say response
```

---

## http_post

Makes an HTTP POST request with a JSON body.

```
global_variable = result
http_post "https://api.example.com/data" "{\"key\":\"value\"}" to result
say result
```

---

## http_put / http_delete

```
global_variable = putResult, delResult

http_put "https://api.example.com/item/1" "{\"name\":\"new\"}" to putResult
http_delete "https://api.example.com/item/1" to delResult
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

---

## Practical Example — Read a JSON API

```
# weather-check.do
global_variable = response

http_get "https://wttr.in/?format=3" to response
say 'Current weather: {response}'
```

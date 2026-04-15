# Lesson 07 — Writing Installer Scripts

Installer scripts are one of the most common uses for DoScript.
This lesson shows the canonical pattern used by real installers in the
community (e.g. `vexon-installer.do`).

---

## The Core Installer Pattern

```
say "=== My App Installer ==="

global_variable = confirm
ask confirm "Install My App? (y/n)"

if confirm == "y"
    say "Installing..."

    make folder "C:/MyApp"
    download "https://example.com/myapp.zip" to "C:/MyApp/myapp.zip"
    unzip "C:/MyApp/myapp.zip" to "C:/MyApp"
    path add "C:/MyApp/bin"
    delete "C:/MyApp/myapp.zip"

    say "Installation complete!"
end_if

pause
```

That's the full pattern. Keep it simple — `ask` → `if` → `make folder`
→ `download` → `unzip` → `path add` → `delete` → `say`.

---

## Using .msi Installers

When the download is a `.msi` Windows installer file, launch it with
`run "msiexec /i ..."` rather than `execute`:

```
download "https://example.com/app-1.0.msi" to "app-installer.msi"
run "msiexec /i app-installer.msi"
```

For a silent/quiet install (no GUI):

```
run "msiexec /i app-installer.msi /quiet"
```

---

## Using .exe Installers

```
download "https://example.com/setup.exe" to "setup.exe"
execute "setup.exe"
```

---

## Adding to PATH

`path add` adds a folder to the **user** PATH environment variable.
Use `--system` to add to the system-wide PATH (requires admin rights).

```
path add "C:/MyApp/bin"
path add --system "C:/MyApp/bin"
```

---

## Offering a Cleanup Step

Always give the user the option to remove the downloaded installer
after it's done:

```
global_variable = cleanup
ask cleanup "Remove installer file? (y/n)"

if cleanup == "y"
    if exists("app-installer.msi")
        delete "app-installer.msi"
        say "Installer removed."
    end_if
end_if
```

---

## Handling Multiple Components

Use a numbered menu with `ask` and a flag variable:

```
say "Which component would you like to install?"
say "  1 - Full install"
say "  2 - Minimal install"
say ""

global_variable = choice
ask choice "Enter 1 or 2:"

if choice == "1"
    say "Running full install..."
    # ... full install steps
end_if

if choice == "2"
    say "Running minimal install..."
    # ... minimal install steps
end_if
```

---

## Full Example — A Real Installer

```
# myapp-installer.do
say "==============================="
say "     MyApp Installer v1.0"
say "==============================="
say ""

global_variable = confirm, cleanup

ask confirm "Install MyApp? (y/n)"

if confirm == "y"
    say "Installing..."
    say ""

    make folder "C:/MyApp"

    say "Downloading..."
    try
        download "https://example.com/myapp.zip" to "C:/MyApp/myapp.zip"
        say "Download complete."
    catch NetworkError
        say "Download failed. Check your connection."
        say "Download manually: https://example.com/myapp"
        pause
        exit 1
    end_try

    say "Extracting..."
    unzip "C:/MyApp/myapp.zip" to "C:/MyApp"

    say "Adding to PATH..."
    path add "C:/MyApp/bin"

    say "Cleaning up..."
    delete "C:/MyApp/myapp.zip"

    say ""
    say "==============================="
    say "  Installation complete!"
    say "==============================="
    say ""
    say "Run 'myapp' from any terminal."
else
    say "Installation cancelled."
end_if

pause
```

---

## Checklist for a Good Installer

- [ ] Greet the user with a clear banner (`say "=== ... ==="`)
- [ ] Ask for confirmation before making changes
- [ ] Wrap `download` in `try/catch NetworkError`
- [ ] Create the install folder with `make folder` before downloading
- [ ] Add to PATH if the app has CLI tools
- [ ] Clean up the downloaded archive after extraction
- [ ] Offer cleanup of the installer itself
- [ ] End with `pause` so the window doesn't close immediately

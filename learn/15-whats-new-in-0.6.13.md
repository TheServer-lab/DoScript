# Lesson 15 — What's New in 0.6.13

## `make shortcut` — desktop and Start Menu shortcuts

Create a shortcut to any file, folder, or URL in one line:

```
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on desktop
make shortcut "My App" to "C:/Program Files/MyApp/app.exe" on startmenu
```

The `on` clause is optional — `desktop` is the default.

This works on Windows (`.lnk` via PowerShell), macOS (Finder alias), and
Linux (`.desktop` file). No extra dependencies needed.

A practical use in an installer:

```
say "Installing shortcuts..."
make shortcut "My App" to '{appdata}\MyApp\app.exe' on desktop
make shortcut "My App" to '{appdata}\MyApp\app.exe' on startmenu
say "Done. Check your Desktop."
```

---

## `registry` — Windows registry

Read and write the Windows registry directly from DoScript. Useful for
installers that need to persist settings or mark themselves as installed.

**Write:**

```
registry set HKCU\Software\MyApp Theme "Dark"
registry set HKCU\Software\MyApp Version 2
```

**Read:**

```
global_variable = theme
registry get HKCU\Software\MyApp Theme to theme
say 'Theme is: {theme}'
```

**Check if already installed:**

```
global_variable = installed
registry exists HKCU\Software\MyApp to installed

if installed == true
    say "Already installed — skipping."
    exit
end_if
```

**Delete:**

```
registry delete HKCU\Software\MyApp Theme     # one value
registry delete HKCU\Software\MyApp           # entire key
```

Supported hives: `HKCU`, `HKLM`, `HKCR`, `HKU`, `HKCC`.

> Registry commands only work on Windows. On any other OS, DoScript raises
> a clear error so scripts fail fast instead of silently doing nothing.

---

## `run_from_web` — run scripts from the DoScriptPackage repo

Fetch and run a `.do` script straight from
[TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage)
without downloading anything manually:

```
run_from_web cleaner.do
run_from_web git-setup.do
```

The `.do` extension is optional:

```
run_from_web cleaner        # same as cleaner.do
```

Scripts in subfolders work too:

```
run_from_web tools/setup-python.do
```

You can use a variable for the script name:

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

> **Want to publish a script?** Add a `.do` file to
> [TheServer-lab/DoScriptPackage](https://github.com/TheServer-lab/DoScriptPackage)
> and anyone with DoScript can run it with `run_from_web your-script.do`.

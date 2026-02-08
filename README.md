# DoScript 🚀

**Stop writing Python boilerplate. Start automating.**

DoScript is a dead-simple scripting language for everyday file automation. If you can write plain English, you can automate your computer.

```bash
do organize-downloads.do
```

That's it. No imports, no classes, no boilerplate.

---

## Why DoScript?

**Before:** You write 30 lines of Python just to organize files by type.

**After:** You write this:

```python
# organize-downloads.do
for_each file_in here
    if file_ext == ".pdf"
        move file to "Documents/PDFs/{file_name}"
    end_if
    if file_ext == ".jpg" or file_ext == ".png"  
        move file to "Pictures/{year}/{month}/{file_name}"
    end_if
end_for
say "✓ Downloads organized!"
```

Run it: `do organize-downloads.do`

---

## Quick Start

### Windows (Recommended)

1. **[Download the installer](https://github.com/TheServer-lab/DoScript/releases/latest)** (One-click setup)
2. Open Command Prompt anywhere
3. Create your first script:

```bash
echo say "Hello World!" > hello.do
do hello.do
```

### From Source (All platforms)

```bash
git clone https://github.com/TheServer-lab/DoScript.git
cd DoScript
python doscript.py examples/hello_world.do
```

**Requirements:** Python 3.8+

---

## Real Examples That Actually Help

### 🗂️ Organize Downloads by Type

```python
# organize-downloads.do
for_each file_in here
    if file_ext == ".pdf"
        move file to "Documents/{file_name}"
    end_if
    if file_ext == ".jpg" or file_ext == ".png"
        move file to "Pictures/{file_name}"
    end_if
    if file_ext == ".zip"
        move file to "Archives/{file_name}"
    end_if
end_for
```

### 🧹 Delete Old Files (30+ days)

```python
# clean-old-files.do
for_each file_in deep
    if file_is_old_days > 30
        say "Deleting: {file_name} ({file_is_old_days} days old)"
        delete file_path
    end_if
end_for
```

### 📸 Backup Photos by Date

```python
# backup-photos.do
for_each file_in deep
    if file_ext == ".jpg" or file_ext == ".png"
        copy file to "D:\Backup\{year}\{month}\{file_name}"
        say "Backed up: {file_name}"
    end_if
end_for
```

### 🔍 Find Large Files (50MB+)

```python
# find-large-files.do
for_each file_in deep
    if file_size_mb > 50
        say "{file_name}: {file_size_mb}MB at {file_path}"
    end_if
end_for
```

### 🔄 Rename Files in Bulk

```python
# rename-screenshots.do
global_variable = counter
counter = 1

for_each file_in here
    if file_name starts_with "Screenshot"
        move file to "screenshot_{counter}{file_ext}"
        counter = counter + 1
    end_if
end_for
```

**[📁 See 20+ more examples →](/examples)**

---

## Features That Make Life Easy

### ✅ Built-in Safety

```bash
# Test before running for real
do cleanup.do --dry-run

# See what's happening
do backup.do --verbose
```

### 📅 Time Variables (Built-in)

```python
say "Backup created on {today} at {now}"
# Output: Backup created on 2024-02-08 at 14:30:45

make folder "Backups/{year}/{month}/{day}"
# Creates: Backups/2024/02/08
```

**Available:** `{time}`, `{today}`, `{now}`, `{year}`, `{month}`, `{day}`, `{hour}`, `{minute}`, `{second}`

### 📊 Rich File Metadata

Inside `for_each` loops, you get instant access to:

```python
for_each file_in deep
    say "{file_name}"           # filename.txt
    say "{file_path}"           # C:\full\path\filename.txt  
    say "{file_ext}"            # .txt
    say "{file_size_mb}"        # 2.5
    say "{file_is_old_days}"    # 45
    say "{file_modified}"       # Unix timestamp
end_for
```

**[📖 See all metadata →](/docs/file-metadata.md)**

### 🌐 Cross-Platform

Write once, run anywhere:
- ✅ Windows (tested on 10/11)
- ✅ macOS (10.15+)
- ✅ Linux (Ubuntu, Debian, Arch, etc.)

### 🔧 Modern Features

- **JSON/CSV support:** `json_read`, `csv_read`, `json_get`, `csv_get`
- **Archive handling:** `zip`, `unzip`, `zip_list`
- **Network operations:** `download`, `upload`, `ping`
- **Process control:** `run`, `capture`, `kill`
- **Error handling:** `try`/`catch` blocks
- **Functions & macros:** Reusable code blocks

---

## Documentation

| Doc | Description |
|-----|-------------|
| **[Quick Start Guide](/docs/quickstart.md)** | Get running in 5 minutes |
| **[Language Reference](/docs/reference.md)** | Complete command list |
| **[Examples Library](/examples)** | 20+ ready-to-use scripts |
| **[FAQ](/docs/faq.md)** | Common questions |

---

## Why Not Just Use...?

### vs. Bash/Shell Scripts
- ✅ Readable by non-programmers
- ✅ Cross-platform (same script on Windows/Mac/Linux)
- ✅ File operations are first-class citizens

### vs. Python
- ✅ No boilerplate (`import os, shutil, glob...`)
- ✅ Built for automation, not general programming
- ✅ Instant file metadata without `os.stat()`

### vs. Batch Files
- ✅ Modern syntax
- ✅ Works on all platforms
- ✅ Rich error handling

### vs. PowerShell
- ✅ Simpler syntax
- ✅ Faster to learn (5 min vs 5 hours)
- ✅ No object pipeline confusion

**DoScript is:** "When Bash is too cryptic and Python is overkill"

---

## Use Cases

**Perfect for:**
- 📁 File organization & cleanup
- 💾 Backup automation
- 📦 Software deployment/installation
- 🧹 Scheduled maintenance tasks
- 📊 Log file processing
- 🔄 Batch renaming & conversions

**Not for:**
- Web servers or APIs
- Complex data processing
- Real-time applications
- GPU-accelerated computing

---

## Installation Methods

### Option 1: Prebuilt Installer (Windows)

**[Download Latest Release →](https://github.com/TheServer-lab/DoScript/releases/latest)**

One-click installer that:
- ✅ Adds `do` command to PATH
- ✅ Sets up file associations (`.do` files)
- ✅ Installs syntax highlighting (optional)

### Option 2: Manual Install

```bash
# Clone the repo
git clone https://github.com/TheServer-lab/DoScript.git
cd DoScript

# Run directly
python doscript.py your-script.do

# Or make it globally available
# Windows (PowerShell as Admin):
$env:PATH += ";$(pwd)"

# Linux/Mac:
sudo ln -s $(pwd)/doscript.py /usr/local/bin/do
chmod +x /usr/local/bin/do
```

---

## Command-Line Usage

```bash
# Basic usage
do script.do

# With arguments (accessible as arg1, arg2, etc.)
do deploy.do production us-east-1

# Dry run (simulate without making changes)
do cleanup.do --dry-run

# Verbose output
do backup.do --verbose

# Combine flags
do deploy.do --dry-run --verbose staging
```

---

## What's New in v0.6.1

- ✨ **Time variables:** `{today}`, `{now}`, `{year}`, etc.
- 📊 **JSON/CSV support:** Read, write, and parse data files
- 📦 **ZIP operations:** Create and extract archives
- 🌐 **Open links:** `open_link` command
- 🔄 **Auto-update checker:** Stay current automatically
- 🪟 **Windows shutdown:** System power control

**[📋 Full Changelog →](/CHANGELOG.md)**

---

## Community & Support

- **[💬 Join Discord](https://discord.gg/your-link)** - Get help, share scripts
- **[🐛 Report Issues](https://github.com/TheServer-lab/DoScript/issues)** - Found a bug?
- **[💡 Request Features](https://github.com/TheServer-lab/DoScript/discussions)** - Have an idea?
- **[📖 Read the Blog](https://your-blog.com)** - Tutorials & tips

---

## Contributing

We'd love your help! Check out:
- **[Good First Issues](https://github.com/TheServer-lab/DoScript/labels/good%20first%20issue)** - Easy starting points
- **[Contributing Guide](/CONTRIBUTING.md)** - How to contribute
- **[Share Your Scripts](/examples/community)** - Show off what you've built!

---

## License

[Server-Lab Open-Control License (SOCL) 1.0](/LICENSE)

---

## Star History

⭐ **Star this repo if DoScript saved you time!**

It helps others discover the project and motivates continued development.

---

## Made By

**[TheServer-lab](https://github.com/TheServer-lab)** - Building tools that make computing simpler.

**DoScript:** Because automation shouldn't require a CS degree.

---

<p align="center">
  <sub>Built with ❤️ for people who just want to organize their files</sub>
</p>

# DoScript — Automate Windows with Simple Scripts

Run real automation with commands that read like instructions.

```bash
do https://raw.githubusercontent.com/TheServer-lab/DoScriptPackage/refs/heads/main/files/developer.do
```

👉 Installs a full developer setup in one command.

---

## ⚡ Try it in 10 seconds

### Install

```bash
winget install doscript
```

or:

```bash
choco install doscript
```

---

### Run your first script

```bash
do https://raw.githubusercontent.com/TheServer-lab/DoScriptPackage/refs/heads/main/files/chromebootstrap.do
```

That’s it.

---

## 💡 What can you do with DoScript?

* 🖥️ Set up a new PC in one command
* 🧑‍💻 Install a full developer environment instantly
* 📦 Build your own installers
* 📁 Automate file organization and cleanup
* 🌐 Download and configure apps automatically
* 🔗 Share automation scripts with a simple link

---

## ✨ Why DoScript?

Most automation tools are powerful—but hard to read and write.

DoScript focuses on:

* ✅ Human-readable syntax
* ✅ Built-in automation commands
* ✅ Safe testing with `--dry-run`
* ✅ No boilerplate or setup

---

## 🧠 Example

```doscript
ask name "What's your project called?"

make folder '{name}'
download "https://example.com/starter.zip" to '{temp}/{name}.zip'
unzip '{temp}/{name}.zip' to '{name}'

say 'Done! Your project is ready in {name}'
```

Reads like instructions. Runs like code.

---

## 🔥 Real Use Cases

### 🧑‍💻 Developer Setup

```bash
do https://raw.githubusercontent.com/TheServer-lab/DoScriptPackage/refs/heads/main/files/developer.do
```

Installs:

* Git
* Python
* Node.js
* VS Code

---

### 🎮 Gaming Setup

```bash
do https://raw.githubusercontent.com/TheServer-lab/DoScriptPackage/refs/heads/main/files/gaming.do
```

Installs:

* Steam
* Discord
* GPU tools

---

### 🖥️ New PC Setup

```bash
do https://raw.githubusercontent.com/TheServer-lab/DoScriptPackage/refs/heads/main/files/freshwindows.do
```

Sets up:

* essential apps
* system tweaks
* folder structure

---

## ⚔️ Why not PowerShell?

Powerful—but complex.

|                             | PowerShell | DoScript |
| --------------------------- | ---------- | -------- |
| Easy to learn               | ❌          | ✅        |
| Readable like plain English | ❌          | ✅        |
| Built-in automation tools   | ⚠️         | ✅        |
| Safe preview mode           | ❌          | ✅        |

👉 DoScript is designed for **getting things done quickly**, not writing complex scripts.

---

## 🛠️ Features

* File and folder automation
* Downloads and archives
* JSON, CSV, and text editing
* Registry and system tools
* Installer creation
* Shortcut and PATH management
* Script-to-EXE compilation

---

## 🧪 Safe by design

* `--dry-run` previews actions before executing
* `try/catch` handles errors cleanly
* explicit commands reduce mistakes
* built-in logging (`log`, `warn`, `error`)

---

## 🚀 Build standalone EXEs

```bash
do build installer.do --onefile --icon app.ico
```

Turn scripts into distributable applications.

---

## 📚 Learn DoScript

Included in this repo:

* beginner lessons
* real-world examples
* installer patterns
* common workflows

---

## 📦 Installation

### WinGet

```bash
winget install doscript
```

### Chocolatey

```bash
choco install doscript
```

---

## 🧾 License

**Server-Lab Open-Control License (SOCL) 1.0**

---

## ⭐ If this helped you

Give the repo a star—it helps others discover DoScript.

---

# 💬 Final note

DoScript isn’t trying to replace everything.

It’s built for one thing:

> **turning everyday tasks into simple, shareable commands**
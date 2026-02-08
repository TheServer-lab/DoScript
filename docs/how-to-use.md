# DoScript - How to Use

DoScript is a simple automation language designed to help you automate everyday computer tasks without needing to be a programmer. Think of it as writing instructions for your computer in plain English.

## Table of Contents
- [Getting Started](#getting-started)
- [Your First Script](#your-first-script)
- [Basic Concepts](#basic-concepts)
- [Working with Files and Folders](#working-with-files-and-folders)
- [Working with Text and Variables](#working-with-text-and-variables)
- [Making Decisions (If/Else)](#making-decisions-ifelse)
- [Repeating Tasks (Loops)](#repeating-tasks-loops)
- [Processing Multiple Files](#processing-multiple-files)
- [Network Operations](#network-operations)
- [Running Programs](#running-programs)
- [Creating Reusable Commands](#creating-reusable-commands)
- [Command Line Arguments](#command-line-arguments)
- [Error Handling](#error-handling)
- [Complete Examples](#complete-examples)

---

## Getting Started

### Running a DoScript

Save your script with a `.do` extension (e.g., `my-script.do`) and run it like this:

```bash
python doscript.py my-script.do
```

**Optional flags:**
- `--dry-run` - Shows what would happen without actually doing it (great for testing!)
- `--verbose` - Shows detailed information about what's happening

**With arguments:**
```bash
python doscript.py backup.do "Monday" "/home/documents"
```

---

## Your First Script

Let's start with something simple - creating a folder and a file:

**hello.do:**
```
make folder "MyFolder"
make file "MyFolder/greeting.txt" with "Hello, World!"
say "Done! Check MyFolder for your file."
```

Run it:
```bash
python doscript.py hello.do
```

---

## Basic Concepts

### Comments

Add comments to explain your scripts:

```
# This is a comment - it's ignored when the script runs
// This is also a comment

make folder "backup"  # Comments can go at the end of lines too
```

### Variables

Variables store information you want to use later:

```
# Declare a variable first
global_variable = myName, favoriteColor

# Then assign values
myName = "Alice"
favoriteColor = "blue"

# Use variables with curly braces
say "Hello, {myName}! Your favorite color is {favoriteColor}."
```

### Displaying Messages

```
say "This prints to the screen"
log "This is an info message"
warn "This is a warning"
error "This is an error message"
```

---

## Working with Files and Folders

### Creating Files and Folders

```
# Create a folder
make folder "Documents/Projects"

# Create a text file
make file "notes.txt" with "My important notes"

# Use variables in file content
global_variable = userName
userName = "Alice"
make file "welcome.txt" with "Welcome, {userName}!"
```

### Copying Files

```
# Copy a file
copy "photo.jpg" to "backup/photo.jpg"

# Copy using a variable
global_variable = myFile
myFile = "report.pdf"
copy myFile to "archive/{myFile}"
```

### Moving Files

```
# Move a file
move "temp.txt" to "archive/temp.txt"

# Move using variables
global_variable = fileName
fileName = "data.csv"
move fileName to "processed/{fileName}"
```

### Deleting Files and Folders

```
# Delete a file
delete "old-file.txt"

# Delete a folder and everything in it
delete "temp-folder"
```

### Checking if Files Exist

```
global_variable = fileExists

# Check if a file exists
if exists("photo.jpg")
    say "Photo found!"
else
    say "Photo not found"
end_if
```

---

## Working with Text and Variables

### String Interpolation

Insert variable values into text using `{variableName}`:

```
global_variable = name, age
name = "Bob"
age = 25

say "My name is {name} and I am {age} years old."
make file "info.txt" with "Name: {name}\nAge: {age}"
```

### Reading Files

```
global_variable = content
content = read_file("data.txt")
say "File contains: {content}"
```

### String Functions

```
global_variable = filename, ext, starts, ends

filename = "document.pdf"

# Get file extension
ext = extension(filename)  # Returns ".pdf"

# Check if text starts with something
starts = startswith(filename, "doc")  # Returns true

# Check if text ends with something
ends = endswith(filename, ".pdf")  # Returns true
```

### User Input

```
global_variable = answer
ask answer "What is your name?"
say "Nice to meet you, {answer}!"
```

---

## Making Decisions (If/Else)

### Basic If Statements

```
global_variable = weather
weather = "sunny"

if weather == "sunny"
    say "It's a beautiful day!"
end_if
```

### If/Else

```
global_variable = age
age = 18

if age >= 18
    say "You are an adult"
else
    say "You are a minor"
end_if
```

### Checking File Extensions

```
global_variable = filename

if ends_with filename ".txt"
    say "This is a text file"
else
    say "This is not a text file"
end_if
```

### Complex Conditions

```
global_variable = score, passed

score = 85
passed = true

if score >= 60 and passed
    say "Congratulations! You passed!"
end_if

if score < 60 or not passed
    say "Sorry, you didn't pass"
end_if
```

---

## Repeating Tasks (Loops)

### Repeat a Specific Number of Times

```
repeat 5
    say "Hello!"
end_repeat
```

### Loop with a Variable

```
global_variable = count
count = 3

loop count
    say "Counting..."
end_loop
```

### Loop Forever (until interrupted)

```
loop forever
    say "Press Ctrl+C to stop"
    wait 1  # Wait 1 second
end_loop
```

### Loop Through a List

```
global_variable = color

for_each color in "red", "green", "blue"
    say "Current color: {color}"
end_for
```

### Breaking Out of Loops

```
global_variable = i
i = 0

loop 10
    i = i + 1
    if i == 5
        break  # Exit the loop
    end_if
    say "Number: {i}"
end_loop
```

---

## Processing Multiple Files

### Process All Files in Current Folder

```
global_variable = file

for_each file_in here
    say "Found file: {file}"
    # file_path gives you the full path
    # file_name gives you just the name
    log "Full path: {file_path}"
end_for
```

### Process All Files Recursively

```
global_variable = file

for_each file_in deep
    say "Processing: {file_name}"
end_for
```

### Process Only Specific File Types

```
global_variable = image

for_each image_in here
    if_ends_with ".jpg"
        say "Found image: {image}"
        copy image to "backup/{image}"
    end_if
end_for
```

### File Metadata

When looping through files, you get extra information:

```
global_variable = file

for_each file_in here
    say "Name: {file_name}"
    say "Path: {file_path}"
    say "Extension: {file_ext}"
    say "Size: {file_size_kb} KB"
    
    if file_is_empty
        say "This file is empty"
    end_if
end_for
```

Available metadata:
- `{varname_name}` - File/folder name
- `{varname_path}` - Full path
- `{varname_ext}` - Extension (files only)
- `{varname_size}` - Size in bytes
- `{varname_size_kb}` - Size in KB
- `{varname_size_mb}` - Size in MB
- `{varname_is_empty}` - true if empty
- `{varname_is_dir}` - true if it's a folder
- `{varname_created}` - Creation time
- `{varname_modified}` - Last modified time

### Process Folders

```
global_variable = folder

for_each folder_in here
    say "Found folder: {folder}"
    say "Path: {folder_path}"
end_for
```

### Process Lines in a File

```
global_variable = line

for_each_line line in "data.txt"
    say "Line: {line}"
end_for
```

---

## Network Operations

### Download Files

```
download "https://example.com/file.zip" to "downloads/file.zip"
```

### Upload Files

```
upload "report.pdf" to "https://example.com/upload"
```

### Check Internet Connectivity

```
try
    ping "google.com"
    say "Internet is working"
catch NetworkError
    say "No internet connection"
end_try
```

---

## Running Programs

### Run a Command

```
# Run a simple command
run "notepad"

# Run with the shell
run "dir"  # Windows
run "ls"   # Mac/Linux
```

### Capture Command Output

```
global_variable = output
output = capture "echo Hello World"
say "Command said: {output}"
```

### Check if a Command Succeeded

```
global_variable = result
result = run "some-command"

if result == 0
    say "Success!"
else
    say "Command failed"
end_if
```

### Kill a Process

```
# Kill by process name
kill "notepad.exe"  # Windows
kill "firefox"      # Mac/Linux
```

---

## Creating Reusable Commands

### Define a Macro

```
make a_command greet
    say "Hello from my custom command!"
end_command

# Use it
run "greet"
```

### Functions with Parameters

```
function say_hello name
    say "Hello, {name}!"
    return "Greeted {name}"
end_function

# Call it
global_variable = result
result = say_hello("Alice")
```

### Functions with Local Variables

```
function calculate_tax price
    local_variable = tax, total
    tax = price * 0.1
    total = price + tax
    return total
end_function

global_variable = finalPrice
finalPrice = calculate_tax(100)
say "Final price: {finalPrice}"
```

---

## Command Line Arguments

DoScript automatically provides `arg1` through `arg32` for command-line arguments:

**backup.do:**
```
# arg1, arg2, etc. are automatically available
say "Source: {arg1}"
say "Destination: {arg2}"

copy arg1 to arg2
```

Run it:
```bash
python doscript.py backup.do "photo.jpg" "backup/photo.jpg"
```

---

## Error Handling

### Try/Catch

```
try
    delete "important-file.txt"
    say "File deleted successfully"
catch FileError
    say "Could not delete file - maybe it doesn't exist?"
catch
    say "Something unexpected happened"
end_try
```

### Error Types

- `FileError` - Problems with files/folders
- `NetworkError` - Network problems
- `ProcessError` - Command execution problems
- `DoScriptError` - General errors

---

## Complete Examples

### Example 1: Organize Photos by Date

```
global_variable = photo

say "Organizing photos..."

for_each photo_in here
    if_ends_with ".jpg"
        # Create folder based on today's date
        make folder "sorted/2024-02"
        
        # Copy photo to sorted folder
        copy photo to "sorted/2024-02/{photo}"
        say "Sorted: {photo}"
    end_if
end_for

say "All photos organized!"
```

### Example 2: Backup Script

```
# Get backup location from command line
say "Backing up to: {arg1}"

# Create backup folder
make folder arg1

global_variable = doc

# Copy all documents
for_each doc_in here
    if_ends_with ".txt"
        copy doc to "{arg1}/{doc}"
        log "Backed up: {doc}"
    end_if
    
    if_ends_with ".pdf"
        copy doc to "{arg1}/{doc}"
        log "Backed up: {doc}"
    end_if
end_for

say "Backup complete!"
```

Run it:
```bash
python doscript.py backup.do "backup-folder"
```

### Example 3: Download and Extract

```
global_variable = url, filename

url = "https://example.com/data.zip"
filename = "data.zip"

say "Downloading file..."
download url to filename

if exists(filename)
    say "Download successful!"
    run "unzip {filename}"
    say "File extracted"
else
    error "Download failed"
    exit 1
end_if
```

### Example 4: Clean Up Old Files

```
global_variable = file, days_old

days_old = 30

for_each file_in here
    # Delete files older than 30 days
    # (Note: You'd need to check file_modified timestamp)
    
    if file_size_mb > 100
        say "Large file found: {file_name} ({file_size_mb} MB)"
        
        ask answer "Delete this file? (yes/no)"
        
        if answer == "yes"
            delete file
            say "Deleted {file_name}"
        end_if
    end_if
end_for
```

### Example 5: Batch Rename Files

```
global_variable = photo, counter
counter = 1

for_each photo_in here
    if_ends_with ".jpg"
        move photo to "photo_{counter}.jpg"
        say "Renamed to photo_{counter}.jpg"
        counter = counter + 1
    end_if
end_for

say "Renamed {counter} photos"
```

---

## Tips and Tricks

### Testing Before Running

Always use `--dry-run` to see what will happen:

```bash
python doscript.py my-script.do --dry-run
```

### Debugging

Use `--verbose` to see detailed information:

```bash
python doscript.py my-script.do --verbose
```

### Pausing Execution

```
# Wait for user to press Enter
pause

# Wait for a specific time (in seconds)
wait 2.5
```

### Escaping Curly Braces

If you need literal `{` or `}` characters:

```
make file "code.txt" with "function() \{ return true; \}"
```

### Including Other Scripts

```
# Reuse code from another script
include "utilities.do"
```

### Working Directory

DoScript uses the script's location as the base for relative paths. Add to the search path:

```
script_path add "/home/user/scripts"
```

---

## Quick Reference

| Category | Command | Example |
|----------|---------|---------|
| **Files** | Create file | `make file "test.txt" with "content"` |
| | Copy file | `copy "a.txt" to "b.txt"` |
| | Move file | `move "a.txt" to "folder/a.txt"` |
| | Delete file | `delete "a.txt"` |
| **Folders** | Create folder | `make folder "MyFolder"` |
| | Delete folder | `delete "MyFolder"` |
| **Variables** | Declare | `global_variable = name, age` |
| | Assign | `name = "Alice"` |
| | Use | `say "Hello {name}"` |
| **Control** | If | `if age > 18` ... `end_if` |
| | Loop | `loop 5` ... `end_loop` |
| | Each file | `for_each file_in here` ... `end_for` |
| **Output** | Print | `say "message"` |
| | Log | `log "info message"` |
| | Input | `ask name "Your name?"` |
| **Network** | Download | `download "url" to "file"` |
| | Upload | `upload "file" to "url"` |
| | Ping | `ping "google.com"` |
| **Programs** | Run | `run "command"` |
| | Capture | `output = capture "command"` |
| | Kill | `kill "process"` |

---

## Getting Help

If something goes wrong, DoScript will show you:
- The error type
- The file and line number
- The problematic command

Use this information to fix the issue and try again!

Happy automating! 🚀

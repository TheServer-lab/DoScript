# DoScript v0.6.9 Changelog

## Features

- Added `else_if` for cleaner conditional chains.
- Added string helpers in expressions: `length()`, `trim()`, `lower()`, `upper()`, and `replace()`.
- Added `execute_command` for safer argument-based command execution without the shell.
- Added loop index support with `loop <count> as <name>` and `loop forever as <name>`.
- Added remote script execution, so DoScript can run scripts directly from `http://` and `https://` URLs.

## Fixes

- Stripped UTF-8 BOM markers at the start of scripts during parsing, which improves compatibility with editor-generated files and downloaded remote scripts.

## Version

- Interpreter version updated from `0.6.8` to `0.6.9`.

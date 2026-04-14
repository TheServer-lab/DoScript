# DoScript v0.6.8 Changelog

## Fixes

- Fixed `include` so included scripts now resolve relative paths from their own directory and report errors against the included file instead of the parent script.
- Fixed `return`, `break`, and `continue` propagation through `try` blocks.
- Fixed loop control-flow propagation so `return` now escapes correctly from `repeat`, `loop`, `for_each`, and `for_each_line`, while `continue` behaves consistently.
- Fixed nested `if` parsing inside `if_ends_with`, `if_file_contains`, and `if_file_not_contains` blocks.
- Fixed `end_for` matching when `for_each` contains nested `for_each_line` blocks.
- Removed dead parser accumulation logic and kept statement parsing simple.
- Fixed error line reporting so DoScript now reports original source line numbers instead of flattened statement indexes.
- Fixed `read_content ... into var` in `--dry-run` mode so the target variable is auto-declared consistently.
- Hardened `unzip` against zip-slip path traversal entries.
- Switched `download` away from `urlretrieve` to a timeout-based streaming implementation.
- Added guardrails to `replace_regex_in_file` for large files and regex timeouts when supported by the runtime.
- Added a runtime warning that `run` executes through the system shell and should not receive untrusted input.

## Version

- Interpreter version updated from `0.6.7` to `0.6.8`.

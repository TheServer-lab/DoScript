# CHANGELOG — DoScript v0.6.0

## v0.6.0 — Stable release (Batch 2.0, safety-first)
**Release date:** (your release date here)

### Highlights
- Added beginner-safe CLI arguments (`arg1` … `arg32`) — read-only and default to empty strings when missing.
- Implemented `--dry-run` support for safe simulation of mutating actions.
- Added `--verbose` flag to show interpreter internals (`[VERBOSE]` logs).
- Introduced basic logging primitives: `log`, `warn`, `error` with `[INFO]/[WARN]/[ERROR]` output.
- Stabilized `for_each` behavior (here/deep) and fixed body execution so nested `if`, `loop`, `repeat`, and nested `for_each` work inside loop bodies.
- File & folder metadata injection for `for_each` loops (path/name/ext/size/created/modified/accessed/is_dir/is_empty, etc.).
- Improved error reporting: all runtime errors include error type, file, line number, and source line for easier debugging.
- Added include support and duplicate-include protection.
- Added common filesystem/network/process operations: `make folder`, `make file`, `copy`, `move`, `delete`, `download`, `upload`, `run`, `capture`, `ping`, `kill`.
- Added `for_each_line` for iterating file lines.
- Built safety-first defaults and recommendations for packaging and distribution (dry-run testing, logging, confirmation patterns).

### Fixes & Improvements
- Fixed a bug where block statements inside `for_each` bodies were executed as single-line statements causing `Unknown statement` errors. Now the loop body is transformed to preserve `if_ends_with` sugar and executed by the block engine.
- Deprecated legacy glob usage (`*`, `**`) in favor of human-readable `here` and `deep` keywords; legacy usage still supported with warnings.
- Deprecated `path` as script resolution helper; `script_path` is used for interpreter include/module resolution. Note: `path add/remove` remains available for installer-style OS PATH intent (with dry-run behavior and warnings).
- Safer built-in behaviors: `argN` are protected as read-only; destructive ops print `[DRY]` in dry-run mode and log actions in normal mode.
- Better parsing and comment handling (single-line `#` and `//` comments supported).

### Known limitations (to address in v0.7)
- Parser removes comments naively and may mis-handle `#`/`//` inside quoted strings. Will be fixed with a quote-aware parser in v0.7.
- Double-quote strings do not interpolate variables (single-quoted strings are used for interpolation). Consider making both support interpolation or adding an explicit interpolation operator.
- `path add` persistent OS PATH changes are intentionally conservative; persistent modifications (registry edits, profile changes) are not performed automatically by the interpreter for safety reasons.
- No native confirmation system yet; recommended pattern is to run scripts with `--dry-run` before actual execution or implement `--force` in future versions.
- Windows path modifications and code signing are outside the interpreter — recommended to use external installer tooling for signed builds.

### Developer notes
- Recommended repo layout: `README.md`, `LICENSE.txt`, `VERSION`, `docs/`, `src/doscript.py`, `examples/`, `dist/doscript.exe`, `tests/`.
- Recommended release steps: run tests, update VERSION, update CHANGELOG, build `doscript.exe`, package `dist/` with `LICENSE` and `docs/`.
- Consider implementing `--dry-run-summary` in a future minor release to present a compact summary of simulated actions at the end of a run.

---
**Acknowledgements & License**: DoScript is distributed under the Server-Lab Open-Control License (SOCL) 1.0 (see LICENSE.txt).


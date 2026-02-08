# DoScript --- Beginner-Friendly System Automation (v0.6)

**DoScript** is a small, safe, human-readable scripting language for
system automation --- think *Batch 2.0*: easy for beginners, powerful
enough for installers, cleaners, and deployment tasks, and built with
safety in mind.

------------------------------------------------------------------------

## Highlights

-   Human-readable DSL focused on filesystem & installer automation\
-   `--dry-run` built in so destructive operations can be simulated
    safely\
-   Beginner-safe CLI arguments (`arg1…arg32`) and simple logging
    (`log`, `warn`, `error`)\
-   Recursive file iteration with `for_each file_in here|deep` and rich
    file metadata available inside loops\
-   Clear error reporting: file name, line number, and source line for
    every error\
-   Designed to be distributable as `doscript.exe` and embeddable in
    toolchains

------------------------------------------------------------------------

## Install

### Prebuilt EXE

Copy `doscript.exe` to a folder on your **PATH** and run:

``` bash
do script.do
```

### From source

Requires **Python 3.8+**:

``` bash
python src/doscript.py examples/hello_world.do
```

------------------------------------------------------------------------

## Usage

    do <script.do> [--dry-run] [--verbose] [args...]

------------------------------------------------------------------------

## Safety Model

-   Dry‑run simulation before destructive execution\
-   Explicit destructive commands (`delete`, `move`)\
-   Structured logging (`INFO`, `WARN`, `ERROR`, `DRY`, `VERBOSE`)

------------------------------------------------------------------------

## License

Server‑Lab Open‑Control License (SOCL) 1.0.

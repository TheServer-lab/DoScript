# =============================================================================
#  DoScript Installer Template
#  License: MIT  |  https://github.com/TheServer-lab/DoScript
# =============================================================================
#
#  HOW TO USE THIS TEMPLATE
#  ────────────────────────
#  1. Fill in every value in the ── CONFIGURATION ── section below.
#  2. Replace the INSTALL STEPS section with your actual install logic.
#  3. Ship this file alongside your program files.
#  4. Users run it with:  python doscript.py installer.do
#
#  WHAT THIS TEMPLATE DOES
#  ───────────────────────
#  • Greets the user and shows app info
#  • Asks for install confirmation (with default install path)
#  • Presents the licence — user can read it online or skip to accept/decline
#  • Runs your install steps
#  • Reports success or failure
# =============================================================================


# ── CONFIGURATION ─────────────────────────────────────────────────────────────
#  Change these values.  Everything else adapts automatically.
# ─────────────────────────────────────────────────────────────────────────────

global_variable = APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION
APP_NAME        = "MyApp"
APP_VERSION     = "1.0.0"
APP_AUTHOR      = "Your Name"
APP_DESCRIPTION = "A short one-line description of what your app does."

# Where the app will be installed (user can override at runtime via arg1)
# Uses the built-in 'appdata' variable — resolves to AppData/Roaming on Windows,
# ~/.config on Linux/macOS. No hardcoded paths needed.
global_variable = DEFAULT_INSTALL_DIR
DEFAULT_INSTALL_DIR = '{appdata}/MyApp'

# Licence details
global_variable = LICENCE_NAME, LICENCE_URL
LICENCE_NAME = "MIT Licence"
LICENCE_URL  = "https://opensource.org/licenses/MIT"

# Optional: set a minimum required disk space in MB (0 = skip check)
global_variable = MIN_DISK_MB
MIN_DISK_MB = 50

# ── END CONFIGURATION ─────────────────────────────────────────────────────────


# =============================================================================
#  INSTALLER LOGIC — edit below the "INSTALL STEPS" marker
# =============================================================================

global_variable = install_dir, answer, disk_ok

# ── Allow an install path override from the command line ──────────────────────
#    Usage:  python doscript.py installer.do "D:/Apps/MyApp"
if arg1 != ""
    install_dir = arg1
else
    install_dir = DEFAULT_INSTALL_DIR
end_if

# ── Require admin so we can write to Program Files / system dirs ──────────────
require_admin 'Please run this installer as Administrator (right-click → Run as administrator).'


# ─────────────────────────────────────────────────────────────────────────────
#  WELCOME BANNER
# ─────────────────────────────────────────────────────────────────────────────
say ""
say "════════════════════════════════════════"
say '{APP_NAME} {APP_VERSION} Installer'
say "════════════════════════════════════════"
say '{APP_DESCRIPTION}'
say ""
say 'Author  : {APP_AUTHOR}'
say 'Licence : {LICENCE_NAME}'
say 'Install : {install_dir}'
say ""


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1 — CONFIRM INSTALLATION
# ─────────────────────────────────────────────────────────────────────────────
ask answer 'Install {APP_NAME} {APP_VERSION} to {install_dir}?  [y/N]'

if answer == "y" or answer == "yes"
    say ""
    log "User confirmed installation."
else
    say ""
    say "Installation cancelled. No changes were made."
    exit 0
end_if


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2 — LICENCE AGREEMENT
# ─────────────────────────────────────────────────────────────────────────────
say "── Licence Agreement ──────────────────────────────────────────────────────"
say '{APP_NAME} is distributed under the {LICENCE_NAME}.'
say ""
say "  [1]  View the full licence in your browser"
say "  [2]  Accept and continue"
say "  [3]  Decline and exit"
say ""

ask answer "Your choice [1/2/3]:"

if answer == "1"
    log 'Opening licence: {LICENCE_URL}'
    open_link LICENCE_URL
    say ""
    # Ask again after they've had a chance to read it
    ask answer 'Do you accept the {LICENCE_NAME}?  [y/N]'
    if answer == "y" or answer == "yes"
        log "User accepted the licence after reading."
    else
        say "You must accept the licence to install {APP_NAME}."
        say "Installation cancelled. No changes were made."
        exit 1
    end_if
else_if answer == "2"
    log "User accepted the licence without reading."
else
    say "You must accept the licence to install {APP_NAME}."
    say "Installation cancelled. No changes were made."
    exit 1
end_if

say ""
say "Licence accepted. Starting installation..."
say ""


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3 — PRE-FLIGHT CHECKS
# ─────────────────────────────────────────────────────────────────────────────

# Disk space check (skipped if MIN_DISK_MB is 0)
# Uses the user's home dir — works cross-platform without hardcoded drive letters.
if MIN_DISK_MB > 0
    try
        system_disk user_home to disk_ok
        log 'Disk usage: {disk_ok}%'
        if disk_ok > 95
            error "Not enough free disk space. Please free up space and try again."
            exit 1
        end_if
    catch
        warn "Could not check disk space — continuing anyway."
    end_try
end_if

# Detect existing installation and warn the user
if exists(install_dir)
    say "⚠  An existing installation was found at {install_dir}."
    confirm "Overwrite existing installation?  (y/N)" else exit 0
    say ""
    log "User confirmed overwrite of existing installation."
end_if


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4 — INSTALL STEPS
#  ↓↓↓  Replace the examples below with your own logic  ↓↓↓
# ─────────────────────────────────────────────────────────────────────────────

log "Creating installation directory..."
make folder '{install_dir}'

log "Copying program files..."
# Examples — replace with your actual files:
#   copy "MyApp.exe"         to '{install_dir}/MyApp.exe'
#   copy "README.txt"        to '{install_dir}/README.txt'
#   copy "resources"         to '{install_dir}/resources'

log "Writing default configuration..."
make file '{install_dir}/config.ini' with
    [app]
    name    = {APP_NAME}
    version = {APP_VERSION}
    author  = {APP_AUTHOR}

    [paths]
    install_dir = {install_dir}
end_file

log "Adding to system PATH..."
# Uncomment to add the install dir to the system PATH:
#   path add --system '{install_dir}'

log "Creating uninstaller..."
make file '{install_dir}/uninstall.do' with
    # Uninstaller for {APP_NAME} {APP_VERSION}
    require_admin "Please run the uninstaller as Administrator."
    say "Uninstalling {APP_NAME}..."
    confirm "This will delete {install_dir} and all its contents.  Continue?  (y/N)" else exit 0
    delete '{install_dir}'
    say "{APP_NAME} has been uninstalled."
end_file


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5 — DONE
# ─────────────────────────────────────────────────────────────────────────────
say ""
say "════════════════════════════════════════"
say '{APP_NAME} {APP_VERSION} installed successfully!'
say "════════════════════════════════════════"
say 'Location : {install_dir}'
say 'Licence  : {LICENCE_NAME}'
say ""

pause

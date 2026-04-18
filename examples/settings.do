# =============================================================================
#  DoScript Interactive Settings
#  A reusable settings program — fork and customise for your own app.
# =============================================================================
#
#  HOW TO CUSTOMISE
#  ────────────────
#  1. Set SETTINGS_FILE to wherever you want settings saved.
#  2. Edit the DEFAULT VALUES section to match your app's settings.
#  3. Edit the MENU SECTIONS below to add, remove, or rename categories.
#  4. Each category is a loop that shows current values and lets the user edit.
#
#  Run:  python doscript.py settings.do
# =============================================================================


# ── CONFIGURATION ─────────────────────────────────────────────────────────────

global_variable = SETTINGS_FILE, APP_NAME
SETTINGS_FILE = "settings.json"
APP_NAME      = "MyApp"

# ── DEFAULT VALUES ─────────────────────────────────────────────────────────────
#  Add one global_variable line and one default assignment per setting.
#  Keys must match exactly what you use in json_set / json_get below.

global_variable = cfg_username, cfg_theme, cfg_language, cfg_font_size
global_variable = cfg_host, cfg_port, cfg_timeout, cfg_proxy
global_variable = cfg_autosave, cfg_log_level, cfg_log_file
global_variable = cfg_startup_sound, cfg_notifications

cfg_username        = "user"
cfg_theme           = "dark"
cfg_language        = "en"
cfg_font_size       = 14
cfg_host            = "localhost"
cfg_port            = 8080
cfg_timeout         = 30
cfg_proxy           = ""
cfg_autosave        = "on"
cfg_log_level       = "info"
cfg_log_file        = "app.log"
cfg_startup_sound   = "on"
cfg_notifications   = "on"


# =============================================================================
#  LOAD SAVED SETTINGS  (silently falls back to defaults if file missing)
# =============================================================================

global_variable = cfg

if exists(SETTINGS_FILE)
    try
        json_read SETTINGS_FILE to cfg

        json_get cfg "username"       to cfg_username
        json_get cfg "theme"          to cfg_theme
        json_get cfg "language"       to cfg_language
        json_get cfg "font_size"      to cfg_font_size
        json_get cfg "host"           to cfg_host
        json_get cfg "port"           to cfg_port
        json_get cfg "timeout"        to cfg_timeout
        json_get cfg "proxy"          to cfg_proxy
        json_get cfg "autosave"       to cfg_autosave
        json_get cfg "log_level"      to cfg_log_level
        json_get cfg "log_file"       to cfg_log_file
        json_get cfg "startup_sound"  to cfg_startup_sound
        json_get cfg "notifications"  to cfg_notifications
    catch
        warn "Could not load settings file — using defaults."
    end_try
end_if


# =============================================================================
#  SAVE FUNCTION
# =============================================================================

function save_settings
    make file '{SETTINGS_FILE}' with
        {
            "username":       "{cfg_username}",
            "theme":          "{cfg_theme}",
            "language":       "{cfg_language}",
            "font_size":      {cfg_font_size},
            "host":           "{cfg_host}",
            "port":           {cfg_port},
            "timeout":        {cfg_timeout},
            "proxy":          "{cfg_proxy}",
            "autosave":       "{cfg_autosave}",
            "log_level":      "{cfg_log_level}",
            "log_file":       "{cfg_log_file}",
            "startup_sound":  "{cfg_startup_sound}",
            "notifications":  "{cfg_notifications}"
        }
    end_file
    say ""
    say '  ✔  Settings saved to {SETTINGS_FILE}'
end_function


# =============================================================================
#  HELPER — prompt with a current value shown, keep old value on empty input
# =============================================================================

function prompt_setting label current_val
    local_variable = raw_input, result
    say '  {label}'
    say '    Current : {current_val}'
    ask raw_input '    New     : (press Enter to keep)'
    if raw_input == ""
        return current_val
    end_if
    return raw_input
end_function


# =============================================================================
#  CATEGORY — GENERAL
# =============================================================================

function menu_general
    local_variable = choice, new_val

    loop forever
        say ""
        say "  ┌─ General ──────────────────────────────────┐"
        say '  │  1. Username       : {cfg_username}'
        say '  │  2. Theme          : {cfg_theme}   (dark / light / system)'
        say '  │  3. Language       : {cfg_language}'
        say '  │  4. Font size      : {cfg_font_size}'
        say '  │  5. Startup sound  : {cfg_startup_sound}   (on / off)'
        say '  │  6. Notifications  : {cfg_notifications}  (on / off)'
        say "  │"
        say "  │  s. Save   b. Back"
        say "  └────────────────────────────────────────────┘"
        ask choice "  Choice:"

        if choice == "1"
            new_val = prompt_setting("Username", cfg_username)
            cfg_username = new_val
        else_if choice == "2"
            new_val = prompt_setting("Theme  (dark / light / system)", cfg_theme)
            cfg_theme = new_val
        else_if choice == "3"
            new_val = prompt_setting("Language  (en / fr / de / es / ...)", cfg_language)
            cfg_language = new_val
        else_if choice == "4"
            new_val = prompt_setting("Font size  (e.g. 12 / 14 / 16)", cfg_font_size)
            cfg_font_size = new_val
        else_if choice == "5"
            new_val = prompt_setting("Startup sound  (on / off)", cfg_startup_sound)
            cfg_startup_sound = new_val
        else_if choice == "6"
            new_val = prompt_setting("Notifications  (on / off)", cfg_notifications)
            cfg_notifications = new_val
        else_if choice == "s"
            save_settings()
        else_if choice == "b"
            break
        else
            say "  Unknown option — try again."
        end_if
    end_loop
end_function


# =============================================================================
#  CATEGORY — NETWORK
# =============================================================================

function menu_network
    local_variable = choice, new_val

    loop forever
        say ""
        say "  ┌─ Network ───────────────────────────────────┐"
        say '  │  1. Host        : {cfg_host}'
        say '  │  2. Port        : {cfg_port}'
        say '  │  3. Timeout     : {cfg_timeout}s'
        say '  │  4. Proxy       : {cfg_proxy}  (blank = none)'
        say "  │"
        say "  │  s. Save   b. Back"
        say "  └─────────────────────────────────────────────┘"
        ask choice "  Choice:"

        if choice == "1"
            new_val = prompt_setting("Host", cfg_host)
            cfg_host = new_val
        else_if choice == "2"
            new_val = prompt_setting("Port  (1-65535)", cfg_port)
            cfg_port = new_val
        else_if choice == "3"
            new_val = prompt_setting("Timeout in seconds", cfg_timeout)
            cfg_timeout = new_val
        else_if choice == "4"
            new_val = prompt_setting("Proxy  (e.g. http://proxy:8080 or blank)", cfg_proxy)
            cfg_proxy = new_val
        else_if choice == "s"
            save_settings()
        else_if choice == "b"
            break
        else
            say "  Unknown option — try again."
        end_if
    end_loop
end_function


# =============================================================================
#  CATEGORY — ADVANCED / LOGGING
# =============================================================================

function menu_advanced
    local_variable = choice, new_val

    loop forever
        say ""
        say "  ┌─ Advanced ──────────────────────────────────┐"
        say '  │  1. Autosave    : {cfg_autosave}   (on / off)'
        say '  │  2. Log level   : {cfg_log_level}   (debug / info / warn / error)'
        say '  │  3. Log file    : {cfg_log_file}'
        say "  │"
        say "  │  r. Reset ALL settings to defaults"
        say "  │  s. Save   b. Back"
        say "  └─────────────────────────────────────────────┘"
        ask choice "  Choice:"

        if choice == "1"
            new_val = prompt_setting("Autosave  (on / off)", cfg_autosave)
            cfg_autosave = new_val
        else_if choice == "2"
            new_val = prompt_setting("Log level  (debug / info / warn / error)", cfg_log_level)
            cfg_log_level = new_val
        else_if choice == "3"
            new_val = prompt_setting("Log file path", cfg_log_file)
            cfg_log_file = new_val
        else_if choice == "r"
            confirm "  Reset ALL settings to factory defaults?  (y/N)" else continue
            cfg_username        = "user"
            cfg_theme           = "dark"
            cfg_language        = "en"
            cfg_font_size       = 14
            cfg_host            = "localhost"
            cfg_port            = 8080
            cfg_timeout         = 30
            cfg_proxy           = ""
            cfg_autosave        = "on"
            cfg_log_level       = "info"
            cfg_log_file        = "app.log"
            cfg_startup_sound   = "on"
            cfg_notifications   = "on"
            save_settings()
            say '  ✔  All settings reset to defaults.'
        else_if choice == "s"
            save_settings()
        else_if choice == "b"
            break
        else
            say "  Unknown option — try again."
        end_if
    end_loop
end_function


# =============================================================================
#  MAIN MENU
# =============================================================================

say ""
say "╔══════════════════════════════════════════╗"
say '║   {APP_NAME} Settings'
say "╠══════════════════════════════════════════╣"
say '║  Settings file: {SETTINGS_FILE}'
say "╚══════════════════════════════════════════╝"

global_variable = main_choice

loop forever
    say ""
    say "  ┌─ Main Menu ─────────────────────────────────┐"
    say "  │  1. General"
    say "  │  2. Network"
    say "  │  3. Advanced & Logging"
    say "  │"
    say "  │  s. Save all settings"
    say "  │  q. Quit"
    say "  └─────────────────────────────────────────────┘"
    ask main_choice "  Choice:"

    if main_choice == "1"
        menu_general()
    else_if main_choice == "2"
        menu_network()
    else_if main_choice == "3"
        menu_advanced()
    else_if main_choice == "s"
        save_settings()
    else_if main_choice == "q"
        break
    else
        say "  Unknown option — try again."
    end_if
end_loop

say ""
say "Goodbye."

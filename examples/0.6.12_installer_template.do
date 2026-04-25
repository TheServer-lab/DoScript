# === Installer template using 0.6.12 features ===
# Build with: python doscript.py build installer_template.do --onefile --title "My App Installer"

require_admin "Please run this installer as Administrator."

say ""
say "=== My App Installer ==="
say ""

confirm "Install My App to {appdata}\MyApp? (y/N)" else exit

# Install dependencies
install_package from winget "git"
install_package from pip "requests"

# Create app directory
make folder '{appdata}\MyApp'
make folder '{appdata}\MyApp\logs'

# Write config
global_variable = cfg_path
cfg_path = '{appdata}\MyApp\config.json'

global_variable = cfg
make file '{appdata}\MyApp\config.json' with
    {"installed": true, "version": "1.0", "user": {"name": ""}}
end_file

json_read cfg_path to cfg
cfg["user"]["name"] = username
json_write cfg to cfg_path

say ""
say "Installation complete!"
say 'Installed to: {appdata}\MyApp'
pause

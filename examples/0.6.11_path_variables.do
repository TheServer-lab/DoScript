# === 0.6.11 built-in path variables demo ===
#
# These variables are always available — no declaration or assignment needed.
# They resolve to the correct location on Windows, macOS, and Linux.
#
#   user_home   Current user's home directory
#   username    Current user's OS login name
#   downloads   ~/Downloads
#   desktop     ~/Desktop
#   documents   ~/Documents
#   appdata     AppData/Roaming  (or ~/.config on Linux/macOS)
#   temp        System temporary directory

say 'Hello, {username}!'
say 'Your home folder   : {user_home}'
say 'Downloads          : {downloads}'
say 'Desktop            : {desktop}'
say 'Documents          : {documents}'
say 'App config folder  : {appdata}'
say 'Temp folder        : {temp}'
say ""

# --- Sort downloads without hardcoding any paths ---
say "Checking Downloads folder..."

make folder '{downloads}/Sorted/Images'
make folder '{downloads}/Sorted/Documents'
make folder '{downloads}/Sorted/Archives'
make folder '{downloads}/Sorted/Other'

global_variable = f

for_each f_in '{downloads}'
    if f_ext == ".png" or f_ext == ".jpg" or f_ext == ".jpeg" or f_ext == ".gif" or f_ext == ".webp"
        move f to '{downloads}/Sorted/Images/{f}'
    else_if f_ext == ".pdf" or f_ext == ".docx" or f_ext == ".txt" or f_ext == ".md"
        move f to '{downloads}/Sorted/Documents/{f}'
    else_if f_ext == ".zip" or f_ext == ".rar" or f_ext == ".7z" or f_ext == ".tar"
        move f to '{downloads}/Sorted/Archives/{f}'
    end_if
end_for

say 'Sorted {loop_count} files in Downloads.'

# --- Write a config file to the OS app data folder ---
say ""
say "Writing app config..."

make folder '{appdata}/MyApp'

make file '{appdata}/MyApp/config.ini' with
    [app]
    user    = {username}
    version = 0.6.11

    [paths]
    downloads = {downloads}
    documents = {documents}
    temp      = {temp}
end_file

say 'Config written to {appdata}/MyApp/config.ini'

# --- Create a temp working file ---
global_variable = tmp_file
tmp_file = '{temp}/myapp_work.txt'
make file tmp_file with "temporary working file"
say 'Temp file: {tmp_file}'

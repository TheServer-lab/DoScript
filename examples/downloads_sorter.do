# === Downloads Sorter (DoScript v0.6.10) ===

log "Starting Downloads sorter..."

# 'downloads' is a built-in variable — no need to declare or assign it.
# It resolves to the current user's Downloads folder on any OS.

# --- Ensure target folders exist ---
make folder '{downloads}/exe'
make folder '{downloads}/zip'
make folder '{downloads}/images'
make folder '{downloads}/docs'
make folder '{downloads}/other'

# --- Loop through files (non-recursive) ---
global_variable = file

for_each file_in here
    # Skip folders
    if file_is_dir == true
        continue
    end_if

    # Sort by extension using else_if chains
    if file_ext == ".exe"
        move file to '{downloads}/exe/{file}'
    else_if file_ext == ".zip" or file_ext == ".rar" or file_ext == ".7z"
        move file to '{downloads}/zip/{file}'
    else_if file_ext == ".png" or file_ext == ".jpg" or file_ext == ".jpeg" or file_ext == ".gif"
        move file to '{downloads}/images/{file}'
    else_if file_ext == ".pdf" or file_ext == ".docx" or file_ext == ".txt"
        move file to '{downloads}/docs/{file}'
    else
        move file to '{downloads}/other/{file}'
    end_if

end_for

log 'Sorted {loop_count} files.'
log "Downloads sorting complete."

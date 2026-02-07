# === Downloads Sorter (DoScript v0.6) ===

log "Starting Downloads sorter..."

# --- Declare variables ---
global_variable = downloads

# --- CHANGE THIS PATH IF NEEDED ---
downloads = "C:/Users/User/Downloads"

# --- Ensure target folders exist ---
make folder "{downloads}/exe"
make folder "{downloads}/zip"
make folder "{downloads}/images"
make folder "{downloads}/docs"
make folder "{downloads}/other"

# --- Loop through all files recursively ---
for_each file_in deep

    if file_is_dir == false

        if_ends_with ".exe"
            move file to "{downloads}/exe/{file}"
        end_if

        if file_ext == ".zip" or file_ext == ".rar" or file_ext == ".7z"
            move file to "{downloads}/zip/{file}"
        end_if

        if file_ext == ".png" or file_ext == ".jpg" or file_ext == ".jpeg" or file_ext == ".gif"
            move file to "{downloads}/images/{file}"
        end_if

        if file_ext == ".pdf" or file_ext == ".docx" or file_ext == ".txt"
            move file to "{downloads}/docs/{file}"
        end_if

        if file_ext != ".exe" and file_ext != ".zip" and file_ext != ".rar" and file_ext != ".7z" and file_ext != ".png" and file_ext != ".jpg" and file_ext != ".jpeg" and file_ext != ".gif" and file_ext != ".pdf" and file_ext != ".docx" and file_ext != ".txt"
            move file to "{downloads}/other/{file}"
        end_if

    end_if

end_for

log "Downloads sorting complete."

# Downloads sorter for DoScript v0.6

log "Starting Downloads sorter..."

global_variable = downloads
downloads = "C:/Users/User/Downloads"

# --- create category folders ---
make folder "{downloads}/exe"
make folder "{downloads}/zip"
make folder "{downloads}/images"
make folder "{downloads}/docs"
make folder "{downloads}/other"

# --- scan all files recursively ---
for_each file_in deep

    # skip directories
    if file_is_dir == true
        end_if

    # --- executables ---
    if_ends_with ".exe"
        move file to "{downloads}/exe/{file_name}"
    end_if

    # --- archives ---
    if_ends_with ".zip"
        move file to "{downloads}/zip/{file_name}"
    end_if

    if_ends_with ".rar"
        move file to "{downloads}/zip/{file_name}"
    end_if

    # --- images ---
    if_ends_with ".png"
        move file to "{downloads}/images/{file_name}"
    end_if

    if_ends_with ".jpg"
        move file to "{downloads}/images/{file_name}"
    end_if

    if_ends_with ".jpeg"
        move file to "{downloads}/images/{file_name}"
    end_if

    # --- documents ---
    if_ends_with ".pdf"
        move file to "{downloads}/docs/{file_name}"
    end_if

    if_ends_with ".docx"
        move file to "{downloads}/docs/{file_name}"
    end_if

    if_ends_with ".txt"
        move file to "{downloads}/docs/{file_name}"
    end_if

    # --- everything else ---
    if file_ext != ".exe"
        if file_ext != ".zip"
            if file_ext != ".rar"
                if file_ext != ".png"
                    if file_ext != ".jpg"
                        if file_ext != ".jpeg"
                            if file_ext != ".pdf"
                                if file_ext != ".docx"
                                    if file_ext != ".txt"
                                        move file to "{downloads}/other/{file_name}"
                                    end_if
                                end_if
                            end_if
                        end_if
                    end_if
                end_if
            end_if
        end_if
    end_if

end_for

log "Downloads sorting complete."

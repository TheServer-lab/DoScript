<doscript=0.6.15>
# downloads-organizer.do
# Organizes your Downloads folder into Images, Videos, Documents, and more.
# Test first: python doscript.py downloads-organizer.do --dry-run

say "========================================="
say " DoScript Downloads Organizer"
say "========================================="

# ---------------------------
# ENSURE CONFIG EXISTS AND IS CURRENT
# ---------------------------
global_variable = config_ok
global_variable = img_exts, vid_exts, doc_exts, ignore, fallback

config_ok = false

if exists("downloads-organizer.slev")
    import_variables "downloads-organizer.slev"
    if img_exts != ""
        config_ok = true
    end_if
end_if

if config_ok == false
    warn "No valid config found. Starting setup..."
    ask img_exts "Image extensions (comma separated, include dots, e.g. .jpg,.png):"
    ask vid_exts "Video extensions (e.g. .mp4,.mkv,.mov):"
    ask doc_exts "Document extensions (e.g. .pdf,.docx,.txt):"
    ignore = ".tmp,.crdownload"
    fallback = "Other"
    make file "downloads-organizer.slev" with
img_exts = {img_exts}
vid_exts = {vid_exts}
doc_exts = {doc_exts}
ignore = {ignore}
fallback = {fallback}
    end_file
    log "Config created!"
end_if

# ---------------------------
# GLOBALS
# ---------------------------
global_variable = choice

# ---------------------------
# ORGANIZER FUNCTION
# ---------------------------
function run_organizer
    local_variable = total, done, ext, proceed

    ask proceed "Organize your Downloads folder? (y/N):"
    if proceed != "y"
        return
    end_if

    # Count total files for progress bar
    total = 0
    for_each f_in '{downloads}'
        if f_is_dir == true
            continue
        end_if
        if_ends_with ".do"
            continue
        end_if
        if_ends_with ".slev"
            continue
        end_if
        total = total + 1
    end_for

    done = 0

    for_each file_in '{downloads}'
        if file_is_dir == true
            continue
        end_if
        if_ends_with ".do"
            continue
        end_if
        if_ends_with ".slev"
            continue
        end_if

        done = done + 1
        progress_bar done of total "Organizing"

        ext = lower(file_ext)

        # Skip ignored extensions
        if contains(ignore, ext)
            continue
        end_if

        # Images
        if contains(img_exts, ext)
            make folder '{downloads}/Images'
            try
                move file to '{downloads}/Images'
            catch FileError
                warn 'Skipped duplicate: {file_name}'
            end_try

        # Videos
        else_if contains(vid_exts, ext)
            make folder '{downloads}/Videos'
            try
                move file to '{downloads}/Videos'
            catch FileError
                warn 'Skipped duplicate: {file_name}'
            end_try

        # Documents
        else_if contains(doc_exts, ext)
            make folder '{downloads}/Docs'
            try
                move file to '{downloads}/Docs'
            catch FileError
                warn 'Skipped duplicate: {file_name}'
            end_try

        # Fallback: has extension → named fallback folder
        else_if ext != ""
            make folder '{downloads}/{fallback}'
            try
                move file to '{downloads}/{fallback}'
            catch FileError
                warn 'Skipped duplicate: {file_name}'
            end_try

        # No extension at all
        else
            make folder '{downloads}/no_extension'
            try
                move file to '{downloads}/no_extension'
            catch FileError
                warn 'Skipped duplicate: {file_name}'
            end_try
        end_if

    end_for

    progress_bar done
    log "Done organizing!"
    notify "Downloads Organizer" "Completed!"
end_function

# ---------------------------
# CONFIG EDITOR FUNCTION
# ---------------------------
function config_editor
    local_variable = subchoice, category, new_ext

    loop forever
        say ""
        menu subchoice from "Config Editor" "View config" "Add extension" "Remove extension" "Edit ignore list" "Save and return" "Cancel"

        if subchoice == "View config"
            say 'Images:    {img_exts}'
            say 'Videos:    {vid_exts}'
            say 'Documents: {doc_exts}'
            say 'Ignore:    {ignore}'
            say 'Fallback:  {fallback}'

        else_if subchoice == "Add extension"
            menu category from "Category" "images" "videos" "documents"
            ask new_ext "Extension to add (example: .webp):"
            if category == "images"
                img_exts = img_exts + "," + new_ext
            else_if category == "videos"
                vid_exts = vid_exts + "," + new_ext
            else_if category == "documents"
                doc_exts = doc_exts + "," + new_ext
            end_if
            log 'Added {new_ext} to {category}.'

        else_if subchoice == "Remove extension"
            menu category from "Category" "images" "videos" "documents"
            ask new_ext "Extension to remove (example: .webp):"
            if category == "images"
                img_exts = replace(img_exts, new_ext, "")
                img_exts = replace(img_exts, ",,", ",")
            else_if category == "videos"
                vid_exts = replace(vid_exts, new_ext, "")
                vid_exts = replace(vid_exts, ",,", ",")
            else_if category == "documents"
                doc_exts = replace(doc_exts, new_ext, "")
                doc_exts = replace(doc_exts, ",,", ",")
            end_if
            log 'Removed {new_ext} from {category}.'

        else_if subchoice == "Edit ignore list"
            say 'Current ignore list: {ignore}'
            ask ignore "New ignore list (comma separated, e.g. .tmp,.crdownload):"

        else_if subchoice == "Save and return"
            make file "downloads-organizer.slev" with
img_exts = {img_exts}
vid_exts = {vid_exts}
doc_exts = {doc_exts}
ignore = {ignore}
fallback = {fallback}
            end_file
            log "Config saved!"
            break

        else_if subchoice == "Cancel"
            warn "Changes discarded."
            break
        end_if

    end_loop
end_function

# ---------------------------
# MAIN MENU
# ---------------------------
loop forever
    say ""
    menu choice from "Main Menu" "Organize Downloads" "Edit Config" "Exit"

    if choice == "Organize Downloads"
        run_organizer()
    else_if choice == "Edit Config"
        config_editor()
    else_if choice == "Exit"
        say "Goodbye!"
        break
    end_if
end_loop

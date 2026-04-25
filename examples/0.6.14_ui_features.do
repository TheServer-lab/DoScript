<doscript=0.6.14>
# === 0.6.14 features demo ===

# ── menu ──────────────────────────────────────────────────────────────────────
global_variable = install_loc
menu install_loc from "Where to install?" "AppData (recommended)" "Program Files" "Custom path"
say 'Location: {install_loc}'

# ── select_path (only runs if Custom path chosen) ─────────────────────────────
if install_loc == "Custom path"
    global_variable = custom_dir
    select_path custom_dir "Choose install folder" from '{user_home}' folders
    say 'Custom dir: {custom_dir}'
end_if

# ── input_password ────────────────────────────────────────────────────────────
global_variable = pw
input_password pw "Enter your account password:"
say "Password received."

# ── progress_bar ──────────────────────────────────────────────────────────────
global_variable = step
loop 20 as step
    progress_bar step of 20 "Installing"
    wait 0.05
end_loop
progress_bar done
say "Installation complete!"

# ── notify ────────────────────────────────────────────────────────────────────
notify "MyApp" "Installation finished successfully."

# ── schedule ──────────────────────────────────────────────────────────────────
schedule "auto-update.do" daily at "03:00"
say "Auto-update scheduled for 03:00 daily."

# ── debug (uncomment to test breakpoint) ──────────────────────────────────────
# debug "inspect state here"

say "Demo complete."

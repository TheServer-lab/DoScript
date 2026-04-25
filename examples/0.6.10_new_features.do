# === 0.6.10 new features demo ===

# require_admin "This script needs admin rights."  # uncomment for real installers

# set_env / get_env
set_env "APP_HOME" to "C:/MyApp"
global_variable = home
home = get_env("APP_HOME")
say 'Installed to: {home}'

# rename
make file "draft.txt" with "work in progress"
rename "draft.txt" to "final.txt"
say "Renamed: final.txt exists"

# list_add / list_get / list_length
global_variable = tags, tag, count, first_tag
tags = split("alpha,beta,gamma", ",")
list_add tags "delta"
count = list_length(tags)
first_tag = list_get(tags, 0)
say 'Tags: {count} total, first is {first_tag}'

# for_each over a list variable + loop_count
for_each tag in tags
    log 'tag: {tag}'
end_for
say 'Iterated {loop_count} tags'

# older_than filter
global_variable = old_file
for_each old_file_in here older_than 7 days
    log 'Old file found: {old_file}'
end_for
say 'Found {loop_count} files older than 7 days'

# multi-line make file
global_variable = app_name, port
app_name = "MyServer"
port = 8080
make file "server_config.ini" with
    [server]
    name = {app_name}
    port = {port}
    debug = false
end_file
say "Config file created"

# is_running
global_variable = py_running
py_running = is_running("python")
if py_running == true
    say "Python process detected"
end_if

# confirm (interactive - uncomment when running manually)
# confirm "Delete temp files? (y/N)" else exit

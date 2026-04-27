# === 0.6.12 — Map and array subscript demo ===

global_variable = cfg, tags, val

make file "demo_config.json" with
    {"app": {"name": "MyApp", "port": 8080}, "version": "1.0"}
end_file

json_read "demo_config.json" to cfg

# subscript read
val = cfg["version"]
say 'Version: {val}'
say 'App name: {cfg["app"]["name"]}'
say 'Port: {cfg["app"]["port"]}'

# subscript write
cfg["version"] = "2.0"
cfg["app"]["name"] = "MyApp Pro"

# read back through interpolation
say 'Updated: {cfg["version"]} — {cfg["app"]["name"]}'

json_write cfg to "demo_config.json"
say "Config saved."

# list subscripts
tags = split("alpha,beta,gamma", ",")
say 'First tag: {tags[0]}'
tags[1] = "BETA"
say 'Second tag after write: {tags[1]}'

delete "demo_config.json"

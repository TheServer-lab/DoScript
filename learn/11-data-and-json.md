# Lesson 11 — Data: JSON and CSV

DoScript has first-class support for reading, modifying, and writing JSON
and CSV files — the most common data formats in automation work.

---

## JSON — Read and Write

```
global_variable = cfg

json_read "config.json" to cfg
json_write cfg to "config.json"
```

Paths can be double-quoted, single-quoted (with interpolation), or a variable:

```
json_read config_path to cfg
json_read 'data/{today}.json' to cfg
json_write cfg to '{appdata}/MyApp/settings.json'
```

---

## json_get — Read a Nested Value

Use dot notation to reach keys inside nested objects:

```
global_variable = cfg, name, port

json_read "config.json" to cfg
json_get cfg "user.name" to name
json_get cfg "server.port" to port

say 'User: {name}, port: {port}'
```

---

## json_set — Write a Nested Value

Dot notation also works for writing. Changes stay in the variable until
you call `json_write`.

```
json_read "config.json" to cfg

json_set cfg "version" "2.0"
json_set cfg "user.name" "Alice"

json_write cfg to "config.json"
```

---

## Subscript Notation `[]`

You can read and write JSON objects and lists with `[]` directly in
expressions, strings, and assignments — no helper command needed.

### Reading

```
global_variable = cfg, tags, val

json_read "config.json" to cfg

val = cfg["version"]
val = cfg["user"]["name"]    # chains work naturally
val = tags[0]                # zero-based list access
```

Use subscripts directly inside interpolated strings:

```
say 'Version: {cfg["version"]}'
say 'Name: {cfg["user"]["name"]}'
say 'First tag: {tags[0]}'
```

### Writing

```
cfg["version"] = "2.0"
cfg["user"]["name"] = "Bob"
tags[1] = "BETA"

json_write cfg to "config.json"
```

---

## CSV

```
global_variable = data, value

csv_read "data.csv" to data
csv_get data row 0 "email" to value
say 'First email: {value}'

csv_write data to "output.csv"
```

---

## List Operations

Use `split()` to turn a delimited string into a list, then manipulate it.

```
global_variable = items, first, count

items = split("a,b,c", ",")
list_add items "d"

count = list_length(items)    # 4
first = list_get(items, 0)    # "a"
```

Iterate a list with `for_each`:

```
for_each item in items
    say 'Item: {item}'
end_for
```

---

## Practical Example — Update a Config File

```
# update-config.do
global_variable = cfg, old_version

json_read "settings.json" to cfg

old_version = cfg["version"]
say 'Updating from version {old_version}...'

cfg["version"] = "2.0"
cfg["user"]["name"] = "Alice"
cfg["features"]["dark_mode"] = true

json_write cfg to "settings.json"
say "Config updated."
```

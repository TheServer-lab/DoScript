#!/usr/bin/env python3
"""
DoScript v0.6.10 - New features and bug fixes
Changes:
- Bug fix: replaced deprecated unicode_escape codec with manual escape handling (non-ASCII chars now work)
- Bug fix: double-quoted strings containing {var} patterns now emit a hint pointing to single quotes
- New: rename "old" to "new" — dedicated rename command
- New: set_env "VAR" to "value" / get_env("VAR") — environment variable access
- New: require_admin "message" — fail early with a clear message if not running as admin/root
- New: confirm "message" else exit — single-line confirmation prompt for destructive actions
- New: list_add, list_get(), list_length() — basic list manipulation
- New: for_each item in list_var — iterate a variable holding a list
- New: {loop_count} — populated with item count after every for_each loop
- New: for_each file_in here older_than 30 days — age-based file filter (also newer_than)
- New: multi-line make file "x" with ... end_file — heredoc-style file creation
- New: is_running("process") — check if a process is running (expression)
- New: built-in path variables (user_home, username, downloads, desktop, documents, appdata, temp)
- New: remote script cache is cleaned up after each run (was previously accumulating)

Previous version (0.6.9):
- Added else_if for cleaner conditional chains
- Added string helpers: length(), trim(), lower(), upper(), replace()
- Added execute_command for safer argument-based process execution
- Added loop <count> as <index> support

Previous version (0.6.8):
- Control flow and include fixes
- Fixed include path resolution and error context for included scripts
- Fixed return/break/continue propagation through try blocks and loops
- Fixed nested if_ends_with / if_file_contains parsing inside for_each
- Fixed nested for_each_line parsing inside end_for blocks

Previous version (0.6.7):
- Content-based file organization
Changes:
- if_file_contains "keyword" - organize files by their text content
- if_file_not_contains "keyword" - inverse content check
- read_content "file.txt" into var - read file content into variable
- contains() function in expressions - check if string contains substring
- Auto-injects {file_content} variable in for_each loops (text files)

Previous version (0.6.6):
- Fixed URL parsing bug

Previous version (0.6.4):
- replace_in_file: Find and replace text in files
- replace_regex_in_file: Regex-based find and replace
- http_get, http_post, http_put, http_delete: HTTP request commands
- random_number: Generate random integers
- random_string: Generate random alphanumeric strings
- random_choice: Pick random item from list
- system_cpu, system_memory, system_disk: System resource monitoring

Previous version (0.6.3):
- path add/remove: Windows PATH environment variable support
- Added --system flag for system-wide PATH modification
- Broadcasts WM_SETTINGCHANGE to notify Windows of PATH changes

Previous version (0.6.2):
- do_new: Execute a new DoScript instance
- Template creation: Use 'make file script.do' and write your own content

Previous version (0.6.1):
- Built-in time variables (time, today, now, year, month, day, hour, minute, second)
- JSON operations: json_read, json_write, json_get
- CSV operations: csv_read, csv_write, csv_get
- Archive operations: zip, unzip, zip_list
- Added: update checker, open_link command, Windows shutdown command
"""

import os
import sys
import re
import glob
import shutil
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import ast
import operator
import time as time_module
import json
import csv
import zipfile
import webbrowser
import random
import string
import uuid
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

# Try to import psutil for system info (optional)
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Current interpreter version
VERSION = "0.6.10"

# ----------------------------
# Script Template
# ----------------------------
SCRIPT_TEMPLATE = '''# DoScript Automation Script
# Created: {timestamp}
# Description: Add your description here

# Declare your variables
global_variable = myVar

# Your automation code here
say "Script started!"

# Example: Process files in current directory
# for_each file_in here
#     say "Found: {file_name}"
# end_for

say "Script completed!"
'''

# ----------------------------
# Exceptions with context
# ----------------------------
class DoScriptError(Exception):
    def __init__(self, message: str, file: Optional[str] = None, line: Optional[int] = None, source: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.file = file
        self.line = line
        self.source = source

class FileError(DoScriptError):
    pass

class NetworkError(DoScriptError):
    pass

class ProcessError(DoScriptError):
    pass

class DataError(DoScriptError):
    pass

# ----------------------------
# Update checker helper
# ----------------------------
def _to_raw_github(url: str) -> str:
    """
    Convert a github.com blob URL to raw.githubusercontent.com if possible.
    Example:
      https://github.com/owner/repo/blob/main/version.txt
    -> https://raw.githubusercontent.com/owner/repo/main/version.txt
    """
    if 'github.com' in url and '/blob/' in url:
        return url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
    return url

def _is_remote_script_target(target: str) -> bool:
    parsed = urllib.parse.urlparse(target)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

def _download_remote_script(script_url: str, timeout: int = 30) -> Tuple[str, str]:
    req = urllib.request.Request(script_url, headers={'User-Agent': 'DoScript/1.0'})
    cache_root = os.path.join(os.getcwd(), '.doscript_remote_cache')
    os.makedirs(cache_root, exist_ok=True)
    temp_dir = os.path.join(cache_root, f'doscript-remote-{uuid.uuid4().hex}')
    os.makedirs(temp_dir, exist_ok=True)
    parsed = urllib.parse.urlparse(script_url)
    basename = os.path.basename(parsed.path) or 'remote_script.do'
    if not basename.lower().endswith('.do'):
        basename += '.do'
    safe_name = re.sub(r'[^A-Za-z0-9._-]', '_', basename)
    local_path = os.path.join(temp_dir, safe_name)
    with urllib.request.urlopen(req, timeout=timeout) as response, open(local_path, 'wb') as out_f:
        shutil.copyfileobj(response, out_f)
    return local_path, temp_dir

def check_for_updates(interp, version_url: str, repo_url: str, timeout: int = 5):
    """
    Check remote version file and if newer, prompt user to open repo_url.
    Non-fatal on network errors (logs a verbose message).
    """
    raw_url = _to_raw_github(version_url)
    try:
        req = urllib.request.Request(raw_url, headers={'User-Agent': 'DoScript-Updater/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode('utf-8', errors='ignore').strip()
            # try to find a version-like token in the response
            m = re.search(r'(\d+\.\d+\.\d+)', text)
            if m:
                remote_ver = m.group(1)
            else:
                # if the file is just one-line, use stripped content
                remote_ver = text.splitlines()[0].strip() if text else ''
            if not remote_ver:
                interp.log_verbose("Update check: couldn't parse remote version.")
                return
            def ver_tuple(v):
                return tuple(int(x) for x in v.split('.') if x.isdigit())
            try:
                if ver_tuple(remote_ver) > ver_tuple(VERSION):
                    # prompt user
                    prompt = f"Update available: {VERSION} -> {remote_ver}. Open repository to update? (y/N): "
                    ans = input(prompt).strip().lower()
                    if ans in ('y','yes'):
                        interp.log_info(f"Opening repository: {repo_url}")
                        try:
                            webbrowser.open(repo_url)
                        except Exception as e:
                            interp.log_error(f"Failed to open browser: {e}")
                    else:
                        interp.log_info("User chose not to open repository.")
                else:
                    interp.log_verbose(f"No update: remote {remote_ver} <= local {VERSION}")
            except Exception as e:
                interp.log_verbose(f"Version comparison failed: {e}")
    except urllib.error.URLError as e:
        interp.log_verbose(f"Update check failed (network): {e}")
    except Exception as e:
        interp.log_verbose(f"Update check failed: {e}")

# ----------------------------
# Interpreter
# ----------------------------
class DoScriptInterpreter:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        # runtime
        self.script_path_stack: List[str] = []
        self.global_vars: Dict[str, Any] = {}
        self.declared_globals: set = set()
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.macros: Dict[str, Dict[str, Any]] = {}
        self.local_scope: Optional[Dict[str, Any]] = None
        self.included_files: set = set()
        self.loop_var_stack: List[str] = []
        # flags
        self.dry_run = dry_run
        self.verbose = verbose
        # execution context for error reporting
        self.current_file: Optional[str] = None
        self.current_line: Optional[int] = None
        self.current_source: Optional[str] = None
        self.current_line_map: List[int] = []
        
        # Initialize time variables (read-only)
        self._init_time_variables()
        
        # Initialize path variables (read-only)
        self._init_path_variables()
        
        # CLI args initialization (filled by CLI runner)
        # populate arg1..arg32 with empty strings and mark as declared (read-only)
        for i in range(1, 33):
            name = f'arg{i}'
            self.declared_globals.add(name)
            self.global_vars[name] = ""

    def _init_time_variables(self):
        """Initialize built-in time variables"""
        now = datetime.now()
        timestamp = int(time_module.time())
        
        # Built-in time variables (read-only)
        time_vars = {
            'time': timestamp,                    # Unix timestamp
            'today': now.strftime('%Y-%m-%d'),   # 2024-02-08-like
            'now': now.strftime('%H:%M:%S'),     # 14:30:45-like
            'year': now.year,
            'month': now.month,
            'day': now.day,
            'hour': now.hour,
            'minute': now.minute,
            'second': now.second,
        }
        
        for name, value in time_vars.items():
            self.declared_globals.add(name)
            self.global_vars[name] = value

    def _init_path_variables(self):
        """Initialize built-in cross-platform path variables (read-only)"""
        home = os.path.expanduser("~")

        if sys.platform == "win32":
            downloads  = os.path.join(home, "Downloads")
            desktop    = os.path.join(home, "Desktop")
            documents  = os.path.join(home, "Documents")
            appdata    = os.environ.get("APPDATA",    os.path.join(home, "AppData", "Roaming"))
            temp       = os.environ.get("TEMP",       os.environ.get("TMP", os.path.join(home, "AppData", "Local", "Temp")))
            username   = os.environ.get("USERNAME",   os.path.basename(home))
        else:
            # macOS / Linux
            downloads  = os.path.join(home, "Downloads")
            desktop    = os.path.join(home, "Desktop")
            documents  = os.path.join(home, "Documents")
            appdata    = os.path.join(home, ".config")
            temp       = "/tmp"
            username   = os.environ.get("USER", os.path.basename(home))

        path_vars = {
            'user_home':  home,
            'username':   username,
            'downloads':  downloads,
            'desktop':    desktop,
            'documents':  documents,
            'appdata':    appdata,
            'temp':       temp,
        }

        for name, value in path_vars.items():
            self.declared_globals.add(name)
            self.global_vars[name] = value

    # ----------------------------
    # Helpers: error / logging
    # ----------------------------
    def raise_error(self, exc_cls, message: str):
        raise exc_cls(message, self.current_file, self.current_line, self.current_source)

    def log_info(self, msg: str):
        print(f"[INFO] {msg}")

    def log_warn(self, msg: str):
        print(f"[WARN] {msg}")

    def log_error(self, msg: str):
        print(f"[ERROR] {msg}")

    def log_verbose(self, msg: str):
        if self.verbose:
            print(f"[VERBOSE] {msg}")

    def log_dry(self, msg: str):
        print(f"[DRY] {msg}")

    # ----------------------------
    # Path resolution
    # ----------------------------
    def resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        if self.script_path_stack:
            return os.path.join(self.script_path_stack[-1], path)
        return path

    # ----------------------------
    # Interpolation
    # ----------------------------
    def interpolate_string(self, s: str) -> str:
        s = s.replace(r'\{', '\x00').replace(r'\}', '\x01')
        def repl(m):
            name = m.group(1)
            try:
                val = self.get_variable(name)
            except DoScriptError:
                val = ""
            return str(val) if val is not None else ""
        s = re.sub(r'\{(\w+)\}', repl, s)
        s = s.replace('\x00', '{').replace('\x01', '}')
        return s

    def interpolate_if_needed(self, s: str) -> str:
        if '{' in s and '}' in s:
            return self.interpolate_string(s)
        return s

    # ----------------------------
    # Variables (argN and time vars are read-only)
    # ----------------------------
    def get_variable(self, name: str) -> Any:
        if self.local_scope is not None and name in self.local_scope:
            return self.local_scope[name]
        if name in self.global_vars:
            return self.global_vars[name]
        self.raise_error(DoScriptError, f"Variable '{name}' is not defined")

    def set_variable(self, name: str, value: Any):
        # protect argN read-only
        if re.match(r'^arg([1-9]|[12]\d|3[0-2])$', name):
            self.raise_error(DoScriptError, f"CLI argument '{name}' is read-only")
        
        # protect time variables (read-only)
        if name in ('time', 'today', 'now', 'year', 'month', 'day', 'hour', 'minute', 'second'):
            self.raise_error(DoScriptError, f"Built-in time variable '{name}' is read-only")
        
        # protect path variables (read-only)
        if name in ('user_home', 'username', 'downloads', 'desktop', 'documents', 'appdata', 'temp'):
            self.raise_error(DoScriptError, f"Built-in path variable '{name}' is read-only")
        
        if self.local_scope is not None and name in self.local_scope:
            self.local_scope[name] = value
            return
        if name in self.declared_globals:
            self.global_vars[name] = value
            return
        self.raise_error(DoScriptError, f"Variable '{name}' used before declaration")

    # ----------------------------
    # Process / admin helpers
    # ----------------------------
    def _is_process_running(self, name: str) -> bool:
        """Return True if a process with the given name is currently running."""
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['name']):
                try:
                    pname = proc.info.get('name') or ''
                    if name.lower() in pname.lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return False
        try:
            if sys.platform == 'win32':
                out = subprocess.run(
                    ['tasklist', '/FI', f'IMAGENAME eq {name}'],
                    capture_output=True, text=True
                )
                return name.lower() in out.stdout.lower()
            else:
                out = subprocess.run(['pgrep', '-x', name], capture_output=True, text=True)
                return out.returncode == 0
        except Exception:
            return False

    def _is_admin(self) -> bool:
        """Return True if the current process has admin / root privileges."""
        try:
            if sys.platform == 'win32':
                import ctypes
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    # ----------------------------
    # Expression evaluation (safe)
    # ----------------------------
    def evaluate_expression(self, expr: str) -> Any:
        expr = expr.strip()
        if not expr:
            return ""

        # String literal double-quoted -> decode escapes (manual, avoids deprecated unicode_escape codec)
        if (expr.startswith('"') and expr.endswith('"')) and len(expr) >= 2:
            inner = expr[1:-1]
            # Built-in read-only variables are interpolated even in double-quoted strings,
            # because they are system constants (paths, time, CLI args) that users
            # virtually never want as a literal string.
            BUILTIN_VARS = {
                'time', 'today', 'now', 'year', 'month', 'day', 'hour', 'minute', 'second',
                'user_home', 'username', 'downloads', 'desktop', 'documents', 'appdata', 'temp',
                *(f'arg{i}' for i in range(1, 33)),
            }
            def _repl_builtins(m):
                name = m.group(1)
                if name in BUILTIN_VARS:
                    try:
                        return str(self.get_variable(name))
                    except DoScriptError:
                        pass
                return m.group(0)  # leave non-builtins untouched
            inner = re.sub(r'\{([A-Za-z_]\w*)\}', _repl_builtins, inner)
            # Hint: only warn about remaining {varname} patterns that are user-defined
            remaining = re.findall(r'\{([A-Za-z_]\w*)\}', inner)
            if any(v not in BUILTIN_VARS for v in remaining):
                print(f"[HINT] Use single quotes for variable interpolation: {expr[:60]}", file=sys.stderr)
            result = inner.replace('\\\\', '\x00')
            result = result.replace('\\n', '\n')
            result = result.replace('\\t', '\t')
            result = result.replace('\\r', '\r')
            result = result.replace('\\\"', '"')
            result = result.replace('\x00', '\\')
            return result

        # Single-quoted -> interpolate
        if (expr.startswith("'") and expr.endswith("'")) and len(expr) >= 2:
            return self.interpolate_string(expr[1:-1])

        # booleans
        if expr == 'true':
            return True
        if expr == 'false':
            return False

        # numbers
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # function call / builtins
        m = re.match(r'^(\w+)\((.*)\)$', expr)
        if m:
            fname = m.group(1)
            args_raw = m.group(2).strip()
            args = [a.strip() for a in self._split_args(args_raw)] if args_raw else []
            if fname == 'exists' and len(args) == 1:
                return os.path.exists(self.resolve_path(self.evaluate_expression(args[0])))
            if fname == 'extension' and len(args) == 1:
                val = self.evaluate_expression(args[0])
                return os.path.splitext(str(val))[1]
            if fname == 'read_file' and len(args) == 1:
                p = self.resolve_path(self.evaluate_expression(args[0]))
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    self.raise_error(FileError, f"read_file failed: {e}")
            if fname == 'startswith' and len(args) == 2:
                return str(self.evaluate_expression(args[0])).startswith(str(self.evaluate_expression(args[1])))
            if fname == 'endswith' and len(args) == 2:
                return str(self.evaluate_expression(args[0])).endswith(str(self.evaluate_expression(args[1])))
            if fname == 'contains' and len(args) == 2:
                return str(self.evaluate_expression(args[1])).lower() in str(self.evaluate_expression(args[0])).lower()
            if fname == 'contains_case' and len(args) == 2:
                # case-sensitive version
                return str(self.evaluate_expression(args[1])) in str(self.evaluate_expression(args[0]))
            if fname == 'notcontains' and len(args) == 2:
                return str(self.evaluate_expression(args[1])).lower() not in str(self.evaluate_expression(args[0])).lower()
            if fname == 'split':
                if len(args) == 1:
                    return str(self.evaluate_expression(args[0])).split()
                if len(args) == 2:
                    return str(self.evaluate_expression(args[0])).split(str(self.evaluate_expression(args[1])))
                return []
            if fname == 'length' and len(args) == 1:
                return len(self.evaluate_expression(args[0]))
            if fname == 'trim' and len(args) == 1:
                return str(self.evaluate_expression(args[0])).strip()
            if fname == 'lower' and len(args) == 1:
                return str(self.evaluate_expression(args[0])).lower()
            if fname == 'upper' and len(args) == 1:
                return str(self.evaluate_expression(args[0])).upper()
            if fname == 'replace' and len(args) == 3:
                return str(self.evaluate_expression(args[0])).replace(
                    str(self.evaluate_expression(args[1])),
                    str(self.evaluate_expression(args[2])),
                )
            if fname == 'list_get' and len(args) == 2:
                lst = self.evaluate_expression(args[0])
                idx = int(self.evaluate_expression(args[1]))
                if not isinstance(lst, list):
                    self.raise_error(DoScriptError, f"list_get: first argument is not a list")
                if idx < 0 or idx >= len(lst):
                    self.raise_error(DoScriptError, f"list_get: index {idx} out of range (list has {len(lst)} items)")
                return lst[idx]
            if fname == 'list_length' and len(args) == 1:
                lst = self.evaluate_expression(args[0])
                if isinstance(lst, (list, str)):
                    return len(lst)
                self.raise_error(DoScriptError, f"list_length: argument is not a list or string")
            if fname == 'get_env' and len(args) == 1:
                var_name = str(self.evaluate_expression(args[0]))
                return os.environ.get(var_name, '')
            if fname == 'is_running' and len(args) == 1:
                proc_name = str(self.evaluate_expression(args[0]))
                return self._is_process_running(proc_name)
            if fname in self.functions:
                evaluated_args = [self.evaluate_expression(a) for a in args]
                return self.call_function(fname, evaluated_args)
            self.raise_error(DoScriptError, f"Unknown function '{fname}'")

        # exists "path" shorthand
        exists_match = re.match(r'^exists\s+"([^"]+)"$', expr)
        if exists_match:
            path = exists_match.group(1)
            return os.path.exists(self.resolve_path(path))

        # simple identifier
        if re.match(r'^\w+$', expr):
            return self.get_variable(expr)

        # safe AST eval
        try:
            namespace = {'true': True, 'false': False, '__builtins__': {}}
            if self.local_scope:
                namespace.update(self.local_scope)
            namespace.update(self.global_vars)
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body, namespace)
        except DoScriptError:
            raise
        except Exception as e:
            self.raise_error(DoScriptError, f"Failed to evaluate '{expr}': {e}")

    def _split_args(self, s: str) -> List[str]:
        if not s:
            return []
        parts = []
        cur = ''
        in_double = False
        in_single = False
        i = 0
        while i < len(s):
            c = s[i]
            if c == '"' and not in_single:
                in_double = not in_double
                cur += c
            elif c == "'" and not in_double:
                in_single = not in_single
                cur += c
            elif c == ',' and not in_double and not in_single:
                parts.append(cur.strip())
                cur = ''
            else:
                cur += c
            i += 1
        if cur.strip():
            parts.append(cur.strip())
        return parts

    def _eval_node(self, node, ns):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in ns:
                return ns[node.id]
            self.raise_error(DoScriptError, f"Unknown name '{node.id}'")
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, ns)
            right = self._eval_node(node.right, ns)
            ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Mod: operator.mod}
            if type(node.op) in ops:
                return ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            val = self._eval_node(node.operand, ns)
            if isinstance(node.op, ast.USub):
                return -val
            if isinstance(node.op, ast.Not):
                return not val
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left, ns)
            for op, comp in zip(node.ops, node.comparators):
                right = self._eval_node(comp, ns)
                if isinstance(op, ast.Eq):
                    if not (left == right): return False
                elif isinstance(op, ast.NotEq):
                    if not (left != right): return False
                elif isinstance(op, ast.Lt):
                    if not (left < right): return False
                elif isinstance(op, ast.Gt):
                    if not (left > right): return False
                elif isinstance(op, ast.LtE):
                    if not (left <= right): return False
                elif isinstance(op, ast.GtE):
                    if not (left >= right): return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                for v in node.values:
                    if not self._eval_node(v, ns): return False
                return True
            if isinstance(node.op, ast.Or):
                for v in node.values:
                    if self._eval_node(v, ns): return True
                return False
        self.raise_error(DoScriptError, f"Unsupported AST node {type(node).__name__}")

    # ----------------------------
    # Function call
    # ----------------------------
    def call_function(self, name: str, args: List[Any]) -> Any:
        if name not in self.functions:
            self.raise_error(DoScriptError, f"Function '{name}' not defined")
        f = self.functions[name]
        params = f['params']
        body = f['body']
        body_line_map = f.get('line_map', [])
        prev_local = self.local_scope
        self.local_scope = {}
        for i, p in enumerate(params):
            self.local_scope[p] = args[i] if i < len(args) else None
        ret = None
        try:
            r = self.execute_lines(body, 0, len(body), body_line_map)
            if r is not None and r[0] == 'return':
                ret = r[1]
            elif r is not None and r[0] in ('break','continue'):
                self.raise_error(DoScriptError, f"'{r[0]}' not valid inside function")
        finally:
            self.local_scope = prev_local
        return ret

    # ----------------------------
    # Parsing
    # ----------------------------
    def parse_script(self, filename: str) -> List[str]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                raw = f.readlines()
        except Exception as e:
            self.raise_error(FileError, f"Failed to open script '{filename}': {e}")
        out: List[str] = []
        line_map: List[int] = []
        for line_no, line in enumerate(raw, start=1):
            if line_no == 1:
                line = line.lstrip('\ufeff')
            # remove comments (quote-aware - don't remove # or // inside strings)
            line = self._remove_comments(line)
            line = line.rstrip('\n\r')
            t = line.strip()
            if t:
                out.append(t)
                line_map.append(line_no)
        self.current_line_map = line_map
        return out
    
    def _remove_comments(self, line: str) -> str:
        """Remove comments but preserve # and // inside quoted strings"""
        result = []
        in_double_quote = False
        in_single_quote = False
        i = 0
        while i < len(line):
            char = line[i]
            
            # Track quote state
            if char == '"' and not in_single_quote and (i == 0 or line[i-1] != '\\'):
                in_double_quote = not in_double_quote
                result.append(char)
            elif char == "'" and not in_double_quote and (i == 0 or line[i-1] != '\\'):
                in_single_quote = not in_single_quote
                result.append(char)
            # Check for comments outside quotes
            elif not in_double_quote and not in_single_quote:
                if char == '#':
                    # Rest of line is comment
                    break
                elif char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    # Rest of line is comment
                    break
                else:
                    result.append(char)
            else:
                # Inside quotes, keep everything
                result.append(char)
            
            i += 1
        
        return ''.join(result)

    def extract_string(self, s: str) -> str:
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            inner = s[1:-1]
            # Process escape sequences manually (in correct order) to avoid unicode_escape deprecation
            # First, handle escaped backslashes
            result = inner.replace('\\\\', '\x00')  # Temporary placeholder
            result = result.replace('\\n', '\n')
            result = result.replace('\\t', '\t')
            result = result.replace('\\r', '\r')
            result = result.replace('\\"', '"')
            result = result.replace('\x00', '\\')  # Restore escaped backslashes
            return result
        if s.startswith("'") and s.endswith("'"):
            return self.interpolate_string(s[1:-1])
        return s

    # ----------------------------
    # Block extraction
    # ----------------------------
    def execute_block(self, lines: List[str], start_idx: int, end_keyword: str, line_map: Optional[List[int]] = None) -> Tuple[int, List[str], List[int]]:
        block: List[str] = []
        block_line_map: List[int] = []
        i = start_idx
        depth = 1
        if line_map is None:
            line_map = self.current_line_map
        while i < len(lines):
            line = lines[i].strip()
            if end_keyword == 'end_function' and line.startswith('function '):
                depth += 1
            elif end_keyword == 'end_loop' and line.startswith('loop '):
                depth += 1
            elif end_keyword == 'end_repeat' and line.startswith('repeat '):
                depth += 1
            elif end_keyword == 'end_if' and line.startswith('if '):
                depth += 1
            elif end_keyword == 'end_try' and line == 'try':
                depth += 1
            elif end_keyword == 'end_command' and (line.startswith('make a_command ') or line.startswith('make a command ')):
                depth += 1
            elif end_keyword == 'end_for' and (line.startswith('for_each ') or line.startswith('for_each_line ')):
                depth += 1
            elif line == end_keyword or line.startswith(end_keyword + ' '):
                depth -= 1
                if depth == 0:
                    return i, block, block_line_map
            block.append(lines[i])
            if 0 <= i < len(line_map):
                block_line_map.append(line_map[i])
            i += 1
        self.raise_error(DoScriptError, f"Missing {end_keyword}")

    def _extract_if_block(self, body: List[str], start_idx: int, error_name: str) -> Tuple[int, List[str]]:
        inner_lines: List[str] = []
        depth = 1
        q = start_idx + 1
        while q < len(body):
            stripped = body[q].strip()
            if stripped.startswith('if '):
                depth += 1
            elif stripped == 'end_if':
                depth -= 1
                if depth == 0:
                    return q, inner_lines
            inner_lines.append(body[q])
            q += 1
        self.raise_error(DoScriptError, f"Missing end_if in {error_name} block")

    def _propagate_control_flow(self, res: Optional[Tuple[str, Any]], allow_continue: bool = True) -> Optional[Tuple[str, Any]]:
        if res is None:
            return None
        if res[0] == 'break':
            return res
        if res[0] == 'continue':
            return None if allow_continue else res
        if res[0] == 'return':
            return res
        return None

    def _split_space_tokens(self, s: str) -> List[str]:
        if not s.strip():
            return []
        parts: List[str] = []
        cur = ''
        in_double = False
        in_single = False
        i = 0
        while i < len(s):
            c = s[i]
            if c == '"' and not in_single:
                in_double = not in_double
                cur += c
            elif c == "'" and not in_double:
                in_single = not in_single
                cur += c
            elif c.isspace() and not in_double and not in_single:
                if cur:
                    parts.append(cur)
                    cur = ''
            else:
                cur += c
            i += 1
        if cur:
            parts.append(cur)
        return parts

    # ----------------------------
    # Execute single statement
    # ----------------------------
    def _exec_statement(self, stmt: str) -> Optional[Tuple[str, Any]]:
        stmt = stmt.strip()
        if not stmt:
            return None

        # logging commands
        if stmt.startswith('log '):
            msg = self.evaluate_expression(stmt[4:].strip())
            self.log_info(str(msg))
            return None
        if stmt.startswith('warn '):
            msg = self.evaluate_expression(stmt[5:].strip())
            self.log_warn(str(msg))
            return None
        if stmt.startswith('error '):
            msg = self.evaluate_expression(stmt[6:].strip())
            self.log_error(str(msg))
            return None

        # JSON operations
        if stmt.startswith('json_read '):
            m = re.match(r'json_read\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                filepath, varname = m.groups()
                resolved = self.resolve_path(filepath)
                try:
                    with open(resolved, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # Ensure variable is declared
                    if varname not in self.declared_globals:
                        self.declared_globals.add(varname)
                        self.global_vars[varname] = None
                    self.set_variable(varname, data)
                    self.log_verbose(f"Loaded JSON from {resolved}")
                except Exception as e:
                    self.raise_error(DataError, f"Failed to read JSON from '{filepath}': {e}")
                return None

        if stmt.startswith('json_write '):
            m = re.match(r'json_write\s+(\w+)\s+to\s+"([^"]+)"$', stmt)
            if m:
                varname, filepath = m.groups()
                resolved = self.resolve_path(filepath)
                data = self.get_variable(varname)
                if self.dry_run:
                    self.log_dry(f"json_write {varname} -> {resolved}")
                else:
                    try:
                        os.makedirs(os.path.dirname(resolved) or '.', exist_ok=True)
                        with open(resolved, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                        self.log_info(f"Wrote JSON to {resolved}")
                    except Exception as e:
                        self.raise_error(DataError, f"Failed to write JSON to '{filepath}': {e}")
                return None

        if stmt.startswith('json_get '):
            m = re.match(r'json_get\s+(\w+)\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                source_var, key, dest_var = m.groups()
                data = self.get_variable(source_var)
                try:
                    # Support dot notation for nested keys
                    keys = key.split('.')
                    value = data
                    for k in keys:
                        if isinstance(value, dict):
                            value = value[k]
                        elif isinstance(value, list):
                            value = value[int(k)]
                        else:
                            self.raise_error(DataError, f"Cannot access key '{k}' in non-dict/list")
                    
                    if dest_var not in self.declared_globals:
                        self.declared_globals.add(dest_var)
                        self.global_vars[dest_var] = None
                    self.set_variable(dest_var, value)
                except (KeyError, IndexError, ValueError) as e:
                    self.raise_error(DataError, f"Key '{key}' not found in {source_var}: {e}")
                return None

        # CSV operations
        if stmt.startswith('csv_read '):
            m = re.match(r'csv_read\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                filepath, varname = m.groups()
                resolved = self.resolve_path(filepath)
                try:
                    with open(resolved, 'r', encoding='utf-8', newline='') as f:
                        reader = csv.DictReader(f)
                        data = list(reader)
                    
                    if varname not in self.declared_globals:
                        self.declared_globals.add(varname)
                        self.global_vars[varname] = None
                    self.set_variable(varname, data)
                    self.log_verbose(f"Loaded CSV from {resolved} ({len(data)} rows)")
                except Exception as e:
                    self.raise_error(DataError, f"Failed to read CSV from '{filepath}': {e}")
                return None

        if stmt.startswith('csv_write '):
            m = re.match(r'csv_write\s+(\w+)\s+to\s+"([^"]+)"$', stmt)
            if m:
                varname, filepath = m.groups()
                resolved = self.resolve_path(filepath)
                data = self.get_variable(varname)
                if self.dry_run:
                    self.log_dry(f"csv_write {varname} -> {resolved}")
                else:
                    try:
                        if not isinstance(data, list) or not data:
                            self.raise_error(DataError, "CSV data must be a non-empty list of dictionaries")
                        
                        os.makedirs(os.path.dirname(resolved) or '.', exist_ok=True)
                        with open(resolved, 'w', encoding='utf-8', newline='') as f:
                            fieldnames = data[0].keys()
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(data)
                        self.log_info(f"Wrote CSV to {resolved} ({len(data)} rows)")
                    except Exception as e:
                        self.raise_error(DataError, f"Failed to write CSV to '{filepath}': {e}")
                return None

        if stmt.startswith('csv_get '):
            m = re.match(r'csv_get\s+(\w+)\s+row\s+(\d+)\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                source_var, row_str, column, dest_var = m.groups()
                data = self.get_variable(source_var)
                try:
                    row_idx = int(row_str)
                    if not isinstance(data, list) or row_idx >= len(data):
                        self.raise_error(DataError, f"Row {row_idx} out of range")
                    
                    value = data[row_idx].get(column)
                    if dest_var not in self.declared_globals:
                        self.declared_globals.add(dest_var)
                        self.global_vars[dest_var] = None
                    self.set_variable(dest_var, value)
                except (KeyError, ValueError) as e:
                    self.raise_error(DataError, f"Failed to get CSV value: {e}")
                return None

        # ZIP operations
        if stmt.startswith('zip ') and ' to ' in stmt:
            m = re.match(r'zip\s+"([^"]+)"\s+to\s+"([^"]+)"$', stmt)
            if m:
                source, zipfile_path = m.groups()
                source_resolved = self.resolve_path(source)
                zip_resolved = self.resolve_path(zipfile_path)
                
                if self.dry_run:
                    self.log_dry(f"zip {source_resolved} -> {zip_resolved}")
                else:
                    try:
                        os.makedirs(os.path.dirname(zip_resolved) or '.', exist_ok=True)
                        with zipfile.ZipFile(zip_resolved, 'w', zipfile.ZIP_DEFLATED) as zf:
                            if os.path.isfile(source_resolved):
                                zf.write(source_resolved, os.path.basename(source_resolved))
                            elif os.path.isdir(source_resolved):
                                for root, dirs, files in os.walk(source_resolved):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, os.path.dirname(source_resolved))
                                        zf.write(file_path, arcname)
                        self.log_info(f"Created archive {zip_resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to create zip '{zipfile_path}': {e}")
                return None

        if stmt.startswith('unzip '):
            m = re.match(r'unzip\s+"([^"]+)"(?:\s+to\s+"([^"]+)")?$', stmt)
            if m:
                zipfile_path = m.group(1)
                dest = m.group(2) if m.group(2) else '.'
                zip_resolved = self.resolve_path(zipfile_path)
                dest_resolved = self.resolve_path(dest)
                
                if self.dry_run:
                    self.log_dry(f"unzip {zip_resolved} -> {dest_resolved}")
                else:
                    try:
                        os.makedirs(dest_resolved, exist_ok=True)
                        with zipfile.ZipFile(zip_resolved, 'r') as zf:
                            dest_real = os.path.realpath(dest_resolved)
                            for member in zf.infolist():
                                member_path = os.path.realpath(os.path.join(dest_resolved, member.filename))
                                if member_path != dest_real and not member_path.startswith(dest_real + os.sep):
                                    self.raise_error(FileError, f"Zip slip detected in '{zipfile_path}': {member.filename}")
                            zf.extractall(dest_resolved)
                        self.log_info(f"Extracted {zip_resolved} to {dest_resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to unzip '{zipfile_path}': {e}")
                return None

        if stmt.startswith('zip_list '):
            m = re.match(r'zip_list\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                zipfile_path, varname = m.groups()
                zip_resolved = self.resolve_path(zipfile_path)
                try:
                    with zipfile.ZipFile(zip_resolved, 'r') as zf:
                        files = zf.namelist()
                    
                    if varname not in self.declared_globals:
                        self.declared_globals.add(varname)
                        self.global_vars[varname] = None
                    self.set_variable(varname, files)
                    self.log_verbose(f"Listed {len(files)} files from {zip_resolved}")
                except Exception as e:
                    self.raise_error(FileError, f"Failed to list zip '{zipfile_path}': {e}")
                return None

        # script_path
        if stmt.startswith('script_path add '):
            path = self.extract_string(stmt[16:])
            self.script_path_stack.append(os.path.abspath(path))
            self.log_verbose(f"script_path added {path}")
            return None
        if stmt.startswith('script_path remove '):
            path = self.extract_string(stmt[19:])
            rp = os.path.abspath(path)
            if rp in self.script_path_stack:
                self.script_path_stack.remove(rp)
            return None
        if stmt == 'script_path list':
            for p in self.script_path_stack:
                print(p)
            return None

        # path (system PATH) - installer-style (must respect dry-run)
        if stmt.startswith('path add '):
            rest = stmt[9:].strip()
            # Check for --system flag
            use_system = False
            if rest.startswith('--system '):
                use_system = True
                rest = rest[9:].strip()
            
            p = self.extract_string(rest)
            resolved = os.path.abspath(self.resolve_path(p))
            
            if self.dry_run:
                scope = "SYSTEM" if use_system else "USER"
                self.log_dry(f"path add [{scope}] {resolved}")
            else:
                if sys.platform == 'win32':
                    try:
                        import winreg
                        
                        # Choose registry key based on scope
                        if use_system:
                            key_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
                            root_key = winreg.HKEY_LOCAL_MACHINE
                            scope_name = "SYSTEM"
                        else:
                            key_path = r'Environment'
                            root_key = winreg.HKEY_CURRENT_USER
                            scope_name = "USER"
                        
                        # Open registry key
                        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                        
                        try:
                            # Read current PATH
                            current_path, _ = winreg.QueryValueEx(key, 'Path')
                        except FileNotFoundError:
                            current_path = ''
                        
                        # Split into components
                        paths = [p.strip() for p in current_path.split(';') if p.strip()]
                        
                        # Add new path if not already present
                        if resolved not in paths:
                            paths.append(resolved)
                            new_path = ';'.join(paths)
                            
                            # Write back to registry
                            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                            winreg.CloseKey(key)
                            
                            # Broadcast environment change
                            try:
                                import ctypes
                                HWND_BROADCAST = 0xFFFF
                                WM_SETTINGCHANGE = 0x001A
                                SMTO_ABORTIFHUNG = 0x0002
                                result = ctypes.c_long()
                                SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
                                SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
                            except:
                                pass  # Broadcasting is optional
                            
                            self.log_info(f"Added to {scope_name} PATH: {resolved}")
                        else:
                            self.log_info(f"Path already in {scope_name} PATH: {resolved}")
                            winreg.CloseKey(key)
                        
                    except PermissionError:
                        self.raise_error(ProcessError, f"Permission denied. {'Administrator' if use_system else 'User'} rights required to modify PATH.")
                    except Exception as e:
                        self.raise_error(ProcessError, f"Failed to add to PATH: {e}")
                else:
                    # Unix-like systems
                    self.log_info("path add on Unix requires manual shell profile edit (~/.bashrc, ~/.zshrc, etc.)")
                    self.log_info(f"Add this line: export PATH=\"$PATH:{resolved}\"")
            return None
            
        if stmt.startswith('path remove '):
            rest = stmt[12:].strip()
            # Check for --system flag
            use_system = False
            if rest.startswith('--system '):
                use_system = True
                rest = rest[9:].strip()
            
            p = self.extract_string(rest)
            resolved = os.path.abspath(self.resolve_path(p))
            
            if self.dry_run:
                scope = "SYSTEM" if use_system else "USER"
                self.log_dry(f"path remove [{scope}] {resolved}")
            else:
                if sys.platform == 'win32':
                    try:
                        import winreg
                        
                        # Choose registry key based on scope
                        if use_system:
                            key_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
                            root_key = winreg.HKEY_LOCAL_MACHINE
                            scope_name = "SYSTEM"
                        else:
                            key_path = r'Environment'
                            root_key = winreg.HKEY_CURRENT_USER
                            scope_name = "USER"
                        
                        # Open registry key
                        key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                        
                        try:
                            # Read current PATH
                            current_path, _ = winreg.QueryValueEx(key, 'Path')
                        except FileNotFoundError:
                            current_path = ''
                        
                        # Split into components
                        paths = [p.strip() for p in current_path.split(';') if p.strip()]
                        
                        # Remove the path if present
                        if resolved in paths:
                            paths.remove(resolved)
                            new_path = ';'.join(paths)
                            
                            # Write back to registry
                            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                            winreg.CloseKey(key)
                            
                            # Broadcast environment change
                            try:
                                import ctypes
                                HWND_BROADCAST = 0xFFFF
                                WM_SETTINGCHANGE = 0x001A
                                SMTO_ABORTIFHUNG = 0x0002
                                result = ctypes.c_long()
                                SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
                                SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
                            except:
                                pass  # Broadcasting is optional
                            
                            self.log_info(f"Removed from {scope_name} PATH: {resolved}")
                        else:
                            self.log_info(f"Path not found in {scope_name} PATH: {resolved}")
                            winreg.CloseKey(key)
                        
                    except PermissionError:
                        self.raise_error(ProcessError, f"Permission denied. {'Administrator' if use_system else 'User'} rights required to modify PATH.")
                    except Exception as e:
                        self.raise_error(ProcessError, f"Failed to remove from PATH: {e}")
                else:
                    # Unix-like systems
                    self.log_info("path remove on Unix requires manual shell profile edit (~/.bashrc, ~/.zshrc, etc.)")
                    self.log_info(f"Remove this from PATH: {resolved}")
            return None

        # include
        if stmt.startswith('include '):
            file_expr = stmt[8:].strip()
            file_path = self.extract_string(file_expr)
            resolved = os.path.abspath(self.resolve_path(file_path))
            if resolved in self.included_files:
                return None
            if not os.path.exists(resolved):
                self.raise_error(FileError, f"Included file not found: {file_path}")
            self.included_files.add(resolved)
            prev_file = self.current_file
            prev_line = self.current_line
            prev_source = self.current_source
            prev_line_map = self.current_line_map
            include_dir = os.path.dirname(resolved)
            self.script_path_stack.append(include_dir)
            self.current_file = resolved
            try:
                lines = self.parse_script(resolved)
                self.execute_lines(lines)
            finally:
                if self.script_path_stack and self.script_path_stack[-1] == include_dir:
                    self.script_path_stack.pop()
                self.current_file = prev_file
                self.current_line = prev_line
                self.current_source = prev_source
                self.current_line_map = prev_line_map
            return None

        # make folder
        if stmt.startswith('make folder '):
            path = self.extract_string(stmt[12:])
            resolved = os.path.abspath(self.resolve_path(path))
            if self.dry_run:
                self.log_dry(f"make folder {resolved}")
            else:
                try:
                    os.makedirs(resolved, exist_ok=True)
                    self.log_info(f"Created folder {resolved}")
                except Exception as e:
                    self.raise_error(FileError, f"Failed to create folder '{path}': {e}")
            return None

        # make file
        if stmt.startswith('make file '):
            m = re.match(r'make file "([^"]+)" with (.+)$', stmt)
            if m:
                path = m.group(1)
                content_expr = m.group(2).strip()
                if content_expr.startswith('"') and content_expr.endswith('"'):
                    inner = content_expr[1:-1]
                    # Hint: {varname} in double-quoted content won't interpolate
                    if re.search(r'\{[A-Za-z_]\w*\}', inner):
                        print(f"[HINT] Use single quotes for variable interpolation in make file content", file=sys.stderr)
                    result = inner.replace('\\\\', '\x00')
                    result = result.replace('\\n', '\n')
                    result = result.replace('\\t', '\t')
                    result = result.replace('\\r', '\r')
                    result = result.replace('\\\"', '"')
                    content = result.replace('\x00', '\\')
                elif content_expr.startswith("'") and content_expr.endswith("'"):
                    content = self.interpolate_string(content_expr[1:-1])
                else:
                    content = str(self.evaluate_expression(content_expr))
                resolved = os.path.abspath(self.resolve_path(path))
                if self.dry_run:
                    self.log_dry(f"make file {resolved} (len={len(content)})")
                else:
                    try:
                        os.makedirs(os.path.dirname(resolved), exist_ok=True)
                        with open(resolved, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.log_info(f"Created file {resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to create file '{path}': {e}")
            else:
                # Support simple syntax without "with" (creates empty file), like make folder
                rest = stmt[10:].strip()
                path = self.extract_string(rest)
                resolved = os.path.abspath(self.resolve_path(path))
                if self.dry_run:
                    self.log_dry(f"make file {resolved}")
                else:
                    try:
                        os.makedirs(os.path.dirname(resolved) or '.', exist_ok=True)
                        with open(resolved, 'w', encoding='utf-8') as f:
                            pass  # Create empty file
                        self.log_info(f"Created file {resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to create file '{path}': {e}")
            return None

        # copy
        if ' to ' in stmt and stmt.startswith('copy '):
            m = re.match(r'copy\s+(.+)\s+to\s+(.+)$', stmt)
            if m:
                src_tok = m.group(1).strip()
                dst_tok = m.group(2).strip()
                if (src_tok.startswith('"') and src_tok.endswith('"')) or (src_tok.startswith("'") and src_tok.endswith("'")):
                    src = self.extract_string(src_tok)
                else:
                    varname = src_tok
                    path_var = varname + '_path'
                    if path_var in self.global_vars and self.global_vars[path_var]:
                        src = self.global_vars[path_var]
                    else:
                        src = self.get_variable(varname)
                dst = self.extract_string(dst_tok)
                dst_interp = self.interpolate_if_needed(dst)
                src_res = os.path.abspath(self.resolve_path(str(src)))
                dst_res = os.path.abspath(self.resolve_path(dst_interp))
                if self.dry_run:
                    self.log_dry(f"copy {src_res} -> {dst_res}")
                else:
                    try:
                        os.makedirs(os.path.dirname(dst_res), exist_ok=True)
                        shutil.copy2(src_res, dst_res)
                        self.log_info(f"Copied {src_res} -> {dst_res}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to copy '{src}' to '{dst_interp}': {e}")
            return None

        # move
        if ' to ' in stmt and stmt.startswith('move '):
            m = re.match(r'move\s+(.+)\s+to\s+(.+)$', stmt)
            if m:
                src_tok = m.group(1).strip()
                dst_tok = m.group(2).strip()
                if (src_tok.startswith('"') and src_tok.endswith('"')) or (src_tok.startswith("'") and src_tok.endswith("'")):
                    src_path = self.extract_string(src_tok)
                else:
                    varname = src_tok
                    path_var = varname + '_path'
                    if path_var in self.global_vars and self.global_vars[path_var]:
                        src_path = self.global_vars[path_var]
                    else:
                        src_path = self.get_variable(varname)
                dst_raw = self.extract_string(dst_tok)
                dst_interp = self.interpolate_if_needed(dst_raw)
                src_res = os.path.abspath(self.resolve_path(str(src_path)))
                dst_res = os.path.abspath(self.resolve_path(dst_interp))
                if self.dry_run:
                    self.log_dry(f"move {src_res} -> {dst_res}")
                else:
                    try:
                        os.makedirs(os.path.dirname(dst_res), exist_ok=True)
                        shutil.move(src_res, dst_res)
                        self.log_info(f"Moved {src_res} -> {dst_res}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to move '{src_path}' to '{dst_interp}': {e}")
            return None

        # rename
        if stmt.startswith('rename ') and ' to ' in stmt:
            m = re.match(r'rename\s+(.+)\s+to\s+(.+)$', stmt)
            if m:
                src_tok = m.group(1).strip()
                dst_tok = m.group(2).strip()
                src = self.extract_string(src_tok) if src_tok.startswith(('"', "'")) else str(self.evaluate_expression(src_tok))
                dst_raw = self.extract_string(dst_tok)
                dst = self.interpolate_if_needed(dst_raw)
                src_res = os.path.abspath(self.resolve_path(src))
                dst_res = os.path.abspath(self.resolve_path(dst))
                if self.dry_run:
                    self.log_dry(f"rename {src_res} -> {dst_res}")
                else:
                    try:
                        os.makedirs(os.path.dirname(dst_res) or '.', exist_ok=True)
                        os.rename(src_res, dst_res)
                        self.log_info(f"Renamed {src_res} -> {dst_res}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to rename '{src}' to '{dst}': {e}")
            return None

        # set_env
        if stmt.startswith('set_env ') and ' to ' in stmt:
            m = re.match(r'set_env\s+(.+?)\s+to\s+(.+)$', stmt)
            if m:
                name_expr = m.group(1).strip()
                val_expr = m.group(2).strip()
                env_name = str(self.evaluate_expression(name_expr))
                env_val = str(self.evaluate_expression(val_expr))
                if self.dry_run:
                    self.log_dry(f"set_env {env_name}={env_val}")
                else:
                    os.environ[env_name] = env_val
                    self.log_info(f"Set environment variable {env_name}")
            return None

        # require_admin
        if stmt.startswith('require_admin'):
            msg_part = stmt[len('require_admin'):].strip()
            msg = str(self.evaluate_expression(msg_part)) if msg_part else "This script requires administrator privileges."
            if not self._is_admin():
                self.log_error(msg)
                sys.exit(1)
            self.log_verbose("Admin check passed.")
            return None

        # confirm
        if stmt.startswith('confirm '):
            # confirm "message" else <statement>
            m = re.match(r'confirm\s+(.+?)\s+else\s+(.+)$', stmt)
            if m:
                prompt_expr = m.group(1).strip()
                else_stmt = m.group(2).strip()
                prompt = str(self.evaluate_expression(prompt_expr))
                ans = input(prompt + " ").strip().lower()
                if ans not in ('y', 'yes'):
                    self._exec_statement(else_stmt)
            else:
                # confirm without else — just prompt, continue regardless
                prompt = str(self.evaluate_expression(stmt[8:].strip()))
                input(prompt + " ")
            return None

        # list_add
        if stmt.startswith('list_add '):
            parts = stmt[9:].strip().split(None, 1)
            if len(parts) != 2:
                self.raise_error(DoScriptError, "list_add requires: list_add <listVar> <value>")
            list_var, val_expr = parts
            lst = self.get_variable(list_var)
            if lst is None:
                lst = []
                self.set_variable(list_var, lst)
            if not isinstance(lst, list):
                self.raise_error(DoScriptError, f"list_add: '{list_var}' is not a list")
            val = self.evaluate_expression(val_expr.strip())
            lst.append(val)
            # list is mutable so already updated in place, but set to be safe
            self.set_variable(list_var, lst)
            self.log_verbose(f"list_add: appended to {list_var} (now {len(lst)} items)")
            return None

        # delete
        if stmt.startswith('delete '):
            path_expr = stmt[7:].strip()
            if (path_expr.startswith('"') and path_expr.endswith('"')) or (path_expr.startswith("'") and path_expr.endswith("'")):
                path = self.extract_string(path_expr)
            else:
                varname = path_expr
                path_var = varname + '_path'
                if path_var in self.global_vars and self.global_vars[path_var]:
                    path = self.global_vars[path_var]
                else:
                    path = str(self.evaluate_expression(path_expr))
            resolved = os.path.abspath(self.resolve_path(path))
            if self.dry_run:
                self.log_dry(f"delete {resolved}")
            else:
                try:
                    if os.path.isdir(resolved):
                        shutil.rmtree(resolved)
                        self.log_info(f"Deleted folder {resolved}")
                    else:
                        os.remove(resolved)
                        self.log_info(f"Deleted file {resolved}")
                except Exception as e:
                    self.raise_error(FileError, f"Failed to delete '{path}': {e}")
            return None

        # download
        if stmt.startswith('download ') and ' to ' in stmt:
            m = re.match(r'download\s+("[^"]*"|\'[^\']*\')\s+to\s+("[^"]*"|\'[^\']*\')$', stmt)
            if m:
                url = self.evaluate_expression(m.group(1))
                path = self.evaluate_expression(m.group(2))
                resolved = os.path.abspath(self.resolve_path(path))
                if self.dry_run:
                    self.log_dry(f"download {url} -> {resolved}")
                else:
                    try:
                        os.makedirs(os.path.dirname(resolved), exist_ok=True)
                        req = urllib.request.Request(url, headers={'User-Agent': 'DoScript/1.0'})
                        with urllib.request.urlopen(req, timeout=30) as response, open(resolved, 'wb') as out_f:
                            shutil.copyfileobj(response, out_f)
                        self.log_info(f"Downloaded {url} -> {resolved}")
                    except Exception as e:
                        self.raise_error(NetworkError, f"Failed to download '{url}': {e}")
            return None

        # upload
        if stmt.startswith('upload ') and ' to ' in stmt:
            m = re.match(r'upload\s+"([^"]+)"\s+to\s+"([^"]+)"$', stmt)
            if m:
                path, url = m.groups()
                resolved = os.path.abspath(self.resolve_path(path))
                if self.dry_run:
                    self.log_dry(f"upload {resolved} -> {url}")
                else:
                    try:
                        with open(resolved, 'rb') as f:
                            data = f.read()
                        req = urllib.request.Request(url, data=data, method='POST')
                        urllib.request.urlopen(req)
                        self.log_info(f"Uploaded {resolved} -> {url}")
                    except Exception as e:
                        self.raise_error(NetworkError, f"Failed to upload '{path}': {e}")
            return None

        # ping
        if stmt.startswith('ping '):
            host = self.extract_string(stmt[5:])
            try:
                if sys.platform == 'win32':
                    subprocess.run(['ping', '-n', '1', host], check=True)
                else:
                    subprocess.run(['ping', '-c', '1', host], check=True)
                self.log_info(f"Pinged {host}")
            except Exception as e:
                self.raise_error(NetworkError, f"Failed to ping '{host}': {e}")
            return None

        # run (macro or shell)
        if stmt.startswith('run '):
            token = stmt[4:].strip()
            name = self.extract_string(token)
            if name in self.macros:
                macro = self.macros[name]
                res = self.execute_lines(macro['body'], 0, len(macro['body']), macro.get('line_map', []))
                if res is not None and res[0] in ('break', 'continue', 'return'):
                    return res
                return None
            else:
                try:
                    self.log_warn("run executes through the system shell. Avoid passing untrusted input to this command.")
                    subprocess.run(name, shell=True, check=False)
                    self.log_info(f"Ran shell: {name}")
                except Exception as e:
                    self.raise_error(ProcessError, f"Failed to run '{name}': {e}")
                return None

        # execute - execute an exe file
        if stmt.startswith('execute '):
            exe_path = self.extract_string(stmt[8:].strip())
            exe_resolved = self.resolve_path(exe_path)
            
            if self.dry_run:
                self.log_dry(f"execute {exe_resolved}")
            else:
                try:
                    if sys.platform == 'win32':
                        # On Windows, execute the .exe file
                        subprocess.run([exe_resolved], check=False)
                        self.log_info(f"Executed: {exe_resolved}")
                    else:
                        # On Unix-like systems, try to execute it
                        subprocess.run([exe_resolved], check=False)
                        self.log_info(f"Executed: {exe_resolved}")
                except Exception as e:
                    self.raise_error(ProcessError, f"Failed to execute '{exe_path}': {e}")
            return None

        # execute_command - safer argument-based process execution
        if stmt.startswith('execute_command '):
            rest = stmt[len('execute_command '):].strip()
            arg_exprs = self._split_space_tokens(rest)
            if not arg_exprs:
                self.raise_error(DoScriptError, "execute_command requires at least one argument")
            cmd = [str(self.evaluate_expression(arg)) for arg in arg_exprs]
            if self.dry_run:
                self.log_dry(f"execute_command {' '.join(cmd)}")
            else:
                try:
                    subprocess.run(cmd, check=False)
                    self.log_info(f"Executed command: {' '.join(cmd)}")
                except Exception as e:
                    self.raise_error(ProcessError, f"Failed to execute command '{cmd[0]}': {e}")
            return None

        # do_new - execute a new DoScript instance
        if stmt.startswith('do_new '):
            rest = stmt[7:].strip()
            parts = self._split_args(rest)
            if not parts:
                self.raise_error(DoScriptError, "do_new requires script path")
            
            script_expr = parts[0]
            script_path = self.evaluate_expression(script_expr)
            script_path = self.interpolate_if_needed(str(script_path))
            script_resolved = self.resolve_path(script_path)
            
            # Build command - detect if running as frozen executable
            if getattr(sys, 'frozen', False):
                # Running as compiled executable (e.g., PyInstaller)
                cmd = [sys.executable, script_resolved]
                self.log_info(f"[FROZEN] Executing: {sys.executable} {script_resolved}")
            else:
                # Running as Python script
                cmd = [sys.executable, os.path.abspath(__file__), script_resolved]
                self.log_info(f"[PYTHON] Executing: {sys.executable} {os.path.abspath(__file__)} {script_resolved}")
            
            # Add any additional arguments
            for arg in parts[1:]:
                arg_val = self.evaluate_expression(arg)
                cmd.append(str(arg_val))
            
            if self.dry_run:
                self.log_dry(f"Would execute DoScript: {' '.join(cmd)}")
                return None
            
            self.log_info(f"Full command: {' '.join(cmd)}")
            self.log_verbose(f"Executing DoScript: {script_path}")
            try:
                result = subprocess.run(cmd, check=True)
                self.log_verbose(f"DoScript completed with exit code {result.returncode}")
            except subprocess.CalledProcessError as e:
                self.raise_error(ProcessError, f"DoScript '{script_path}' failed with exit code {e.returncode}")
            except Exception as e:
                self.raise_error(ProcessError, f"Failed to execute DoScript '{script_path}': {e}")
            return None

        # capture
        if stmt.startswith('capture '):
            token = stmt[8:].strip()
            name = self.extract_string(token)
            try:
                result = subprocess.run(name, shell=True, capture_output=True, text=True)
                return ('capture_output', result.stdout.strip())
            except Exception as e:
                self.raise_error(ProcessError, f"Failed to capture '{name}': {e}")

        # exit
        if stmt.startswith('exit'):
            if stmt == 'exit':
                sys.exit(0)
            else:
                code_expr = stmt[4:].strip()
                code = int(self.evaluate_expression(code_expr))
                sys.exit(code)

        # break / continue
        if stmt == 'break':
            return ('break', None)
        if stmt == 'continue':
            return ('continue', None)

        # kill
        if stmt.startswith('kill '):
            proc_name = self.extract_string(stmt[5:])
            try:
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/IM', proc_name], check=True)
                else:
                    subprocess.run(['pkill', proc_name], check=True)
                self.log_info(f"Killed process {proc_name}")
            except Exception as e:
                self.raise_error(ProcessError, f"Failed to kill '{proc_name}': {e}")
            return None

        # shutdown (Windows-only)
        if stmt.startswith('shutdown'):
            args = stmt[len('shutdown'):].strip()
            if sys.platform == 'win32':
                if self.dry_run:
                    self.log_dry("shutdown (Windows) - dry run")
                else:
                    try:
                        # allow optional seconds like: shutdown 60
                        if args and args.isdigit():
                            subprocess.run(['shutdown', '/s', '/t', args], check=True)
                        else:
                            subprocess.run(['shutdown', '/s', '/t', '0'], check=True)
                        self.log_info("Shutdown command executed (Windows).")
                    except Exception as e:
                        self.raise_error(ProcessError, f"Failed to shutdown Windows: {e}")
            else:
                self.raise_error(ProcessError, "shutdown command is only supported on Windows in this interpreter.")
            return None

        # open_link <url>
        if stmt.startswith('open_link '):
            link = self.extract_string(stmt[len('open_link '):])
            if self.dry_run:
                self.log_dry(f"open_link {link}")
            else:
                try:
                    webbrowser.open(link)
                    self.log_info(f"Opened link: {link}")
                except Exception as e:
                    self.raise_error(ProcessError, f"Failed to open link '{link}': {e}")
            return None

        # read_content - Read file content into a variable
        # Usage: read_content "file.txt" into myvar
        if stmt.startswith('read_content '):
            m = re.match(r'read_content\s+(.+?)\s+into\s+(\w+)$', stmt)
            if m:
                path_expr, varname = m.groups()
                filepath = self.extract_string(path_expr.strip())
                resolved = self.resolve_path(filepath)
                if varname not in self.declared_globals:
                    self.declared_globals.add(varname)
                    self.global_vars[varname] = None
                if self.dry_run:
                    self.log_dry(f"read_content {resolved} into {varname}")
                    self.set_variable(varname, "")
                else:
                    try:
                        with open(resolved, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        self.set_variable(varname, content)
                        self.log_info(f"Read {len(content)} chars from {resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"read_content failed for '{filepath}': {e}")
                return None

        # replace_in_file - Find and replace text in files
        if stmt.startswith('replace_in_file '):
            m = re.match(r'replace_in_file\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$', stmt)
            if m:
                filepath, search_text, replace_text = m.groups()
                resolved = self.resolve_path(filepath)
                
                if self.dry_run:
                    self.log_dry(f"replace_in_file {resolved}: '{search_text}' -> '{replace_text}'")
                else:
                    try:
                        with open(resolved, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        count = content.count(search_text)
                        new_content = content.replace(search_text, replace_text)
                        
                        with open(resolved, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        self.log_info(f"Replaced {count} occurrence(s) in {resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to replace in file '{filepath}': {e}")
                return None

        # replace_regex_in_file - Regex-based find and replace
        if stmt.startswith('replace_regex_in_file '):
            m = re.match(r'replace_regex_in_file\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$', stmt)
            if m:
                filepath, pattern, replacement = m.groups()
                resolved = self.resolve_path(filepath)
                
                if self.dry_run:
                    self.log_dry(f"replace_regex_in_file {resolved}: pattern '{pattern}' -> '{replacement}'")
                else:
                    try:
                        with open(resolved, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if len(content) > 1_000_000:
                            self.raise_error(FileError, f"Regex replace skipped for '{filepath}': file too large for safe regex processing")

                        try:
                            regex = re.compile(pattern, timeout=2.0)
                        except TypeError:
                            regex = re.compile(pattern)
                        matches = len(regex.findall(content))
                        new_content = regex.sub(replacement, content)

                        with open(resolved, 'w', encoding='utf-8') as f:
                            f.write(new_content)

                        self.log_info(f"Replaced {matches} regex match(es) in {resolved}")
                    except TimeoutError:
                        self.raise_error(FileError, f"Regex replace timed out for '{filepath}'")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to regex replace in file '{filepath}': {e}")
                return None

        # HTTP GET request
        if stmt.startswith('http_get '):
            m = re.match(r'http_get\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                url, varname = m.groups()
                
                if self.dry_run:
                    self.log_dry(f"http_get {url} -> {varname}")
                else:
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'DoScript/1.0'})
                        with urllib.request.urlopen(req, timeout=30) as response:
                            data = response.read().decode('utf-8')
                        
                        if varname not in self.declared_globals:
                            self.declared_globals.add(varname)
                            self.global_vars[varname] = None
                        self.set_variable(varname, data)
                        self.log_info(f"HTTP GET from {url} (length: {len(data)} bytes)")
                    except Exception as e:
                        self.raise_error(NetworkError, f"HTTP GET failed for '{url}': {e}")
                return None

        # HTTP POST request
        if stmt.startswith('http_post '):
            m = re.match(r'http_post\s+"([^"]+)"\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                url, data_str, varname = m.groups()
                
                if self.dry_run:
                    self.log_dry(f"http_post {url} -> {varname}")
                else:
                    try:
                        data = data_str.encode('utf-8')
                        req = urllib.request.Request(url, data=data, method='POST',
                                                     headers={'User-Agent': 'DoScript/1.0',
                                                             'Content-Type': 'application/json'})
                        with urllib.request.urlopen(req, timeout=30) as response:
                            response_data = response.read().decode('utf-8')
                        
                        if varname not in self.declared_globals:
                            self.declared_globals.add(varname)
                            self.global_vars[varname] = None
                        self.set_variable(varname, response_data)
                        self.log_info(f"HTTP POST to {url} (response length: {len(response_data)} bytes)")
                    except Exception as e:
                        self.raise_error(NetworkError, f"HTTP POST failed for '{url}': {e}")
                return None

        # HTTP PUT request
        if stmt.startswith('http_put '):
            m = re.match(r'http_put\s+"([^"]+)"\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                url, data_str, varname = m.groups()
                
                if self.dry_run:
                    self.log_dry(f"http_put {url} -> {varname}")
                else:
                    try:
                        data = data_str.encode('utf-8')
                        req = urllib.request.Request(url, data=data, method='PUT',
                                                     headers={'User-Agent': 'DoScript/1.0',
                                                             'Content-Type': 'application/json'})
                        with urllib.request.urlopen(req, timeout=30) as response:
                            response_data = response.read().decode('utf-8')
                        
                        if varname not in self.declared_globals:
                            self.declared_globals.add(varname)
                            self.global_vars[varname] = None
                        self.set_variable(varname, response_data)
                        self.log_info(f"HTTP PUT to {url} (response length: {len(response_data)} bytes)")
                    except Exception as e:
                        self.raise_error(NetworkError, f"HTTP PUT failed for '{url}': {e}")
                return None

        # HTTP DELETE request
        if stmt.startswith('http_delete '):
            m = re.match(r'http_delete\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                url, varname = m.groups()
                
                if self.dry_run:
                    self.log_dry(f"http_delete {url} -> {varname}")
                else:
                    try:
                        req = urllib.request.Request(url, method='DELETE',
                                                     headers={'User-Agent': 'DoScript/1.0'})
                        with urllib.request.urlopen(req, timeout=30) as response:
                            response_data = response.read().decode('utf-8')
                        
                        if varname not in self.declared_globals:
                            self.declared_globals.add(varname)
                            self.global_vars[varname] = None
                        self.set_variable(varname, response_data)
                        self.log_info(f"HTTP DELETE from {url} (response length: {len(response_data)} bytes)")
                    except Exception as e:
                        self.raise_error(NetworkError, f"HTTP DELETE failed for '{url}': {e}")
                return None

        # random_number - Generate random integer
        if stmt.startswith('random_number '):
            m = re.match(r'random_number\s+(-?\d+)\s+(-?\d+)\s+to\s+(\w+)$', stmt)
            if m:
                min_val, max_val, varname = m.groups()
                min_val = int(min_val)
                max_val = int(max_val)
                
                num = random.randint(min_val, max_val)
                
                if varname not in self.declared_globals:
                    self.declared_globals.add(varname)
                    self.global_vars[varname] = None
                self.set_variable(varname, num)
                self.log_verbose(f"Generated random number: {num}")
                return None

        # random_string - Generate random alphanumeric string
        if stmt.startswith('random_string '):
            m = re.match(r'random_string\s+(\d+)\s+to\s+(\w+)$', stmt)
            if m:
                length, varname = m.groups()
                length = int(length)
                
                chars = string.ascii_letters + string.digits
                rand_str = ''.join(random.choice(chars) for _ in range(length))
                
                if varname not in self.declared_globals:
                    self.declared_globals.add(varname)
                    self.global_vars[varname] = None
                self.set_variable(varname, rand_str)
                self.log_verbose(f"Generated random string of length {length}")
                return None

        # random_choice - Pick random item from list
        if stmt.startswith('random_choice '):
            m = re.match(r'random_choice\s+(.+)\s+to\s+(\w+)$', stmt)
            if m:
                items_str, varname = m.groups()
                items = [self.extract_string(item.strip()) for item in items_str.split(',')]
                
                if not items:
                    self.raise_error(DoScriptError, "random_choice requires at least one item")
                
                choice = random.choice(items)
                
                if varname not in self.declared_globals:
                    self.declared_globals.add(varname)
                    self.global_vars[varname] = None
                self.set_variable(varname, choice)
                self.log_verbose(f"Randomly chose: {choice}")
                return None

        # system_cpu - Get CPU usage percentage
        if stmt.startswith('system_cpu to '):
            varname = stmt[14:].strip()
            
            if not HAS_PSUTIL:
                self.raise_error(ProcessError, "system_cpu requires 'psutil' module. Install with: pip install psutil")
            
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                
                if varname not in self.declared_globals:
                    self.declared_globals.add(varname)
                    self.global_vars[varname] = None
                self.set_variable(varname, cpu_percent)
                self.log_verbose(f"CPU usage: {cpu_percent}%")
            except Exception as e:
                self.raise_error(ProcessError, f"Failed to get CPU usage: {e}")
            return None

        # system_memory - Get memory usage percentage
        if stmt.startswith('system_memory to '):
            varname = stmt[17:].strip()
            
            if not HAS_PSUTIL:
                self.raise_error(ProcessError, "system_memory requires 'psutil' module. Install with: pip install psutil")
            
            try:
                mem = psutil.virtual_memory()
                mem_percent = mem.percent
                
                if varname not in self.declared_globals:
                    self.declared_globals.add(varname)
                    self.global_vars[varname] = None
                self.set_variable(varname, mem_percent)
                self.log_verbose(f"Memory usage: {mem_percent}%")
            except Exception as e:
                self.raise_error(ProcessError, f"Failed to get memory usage: {e}")
            return None

        # system_disk - Get disk usage percentage for a path
        if stmt.startswith('system_disk '):
            m = re.match(r'system_disk\s+"([^"]+)"\s+to\s+(\w+)$', stmt)
            if m:
                path, varname = m.groups()
                resolved = self.resolve_path(path)
                
                if not HAS_PSUTIL:
                    self.raise_error(ProcessError, "system_disk requires 'psutil' module. Install with: pip install psutil")
                
                try:
                    disk = psutil.disk_usage(resolved)
                    disk_percent = disk.percent
                    
                    if varname not in self.declared_globals:
                        self.declared_globals.add(varname)
                        self.global_vars[varname] = None
                    self.set_variable(varname, disk_percent)
                    self.log_verbose(f"Disk usage for {resolved}: {disk_percent}%")
                except Exception as e:
                    self.raise_error(ProcessError, f"Failed to get disk usage for '{path}': {e}")
                return None

        # say
        if stmt.startswith('say '):
            expr = stmt[4:].strip()
            val = self.evaluate_expression(expr)
            print(val)
            return None

        # ask (interactive)
        if stmt.startswith('ask '):
            m = re.match(r'ask\s+(\w+)\s+(.+)$', stmt)
            if m:
                var_name = m.group(1)
                prompt_expr = m.group(2).strip()
                prompt = str(self.evaluate_expression(prompt_expr))
                ans = input(prompt + " ")
                # allow setting ask results to variables; declare if needed
                if var_name not in self.declared_globals and self.local_scope is None:
                    self.declared_globals.add(var_name)
                    self.global_vars[var_name] = ans
                else:
                    self.set_variable(var_name, ans)
            return None

        # pause
        if stmt == 'pause':
            input("Press Enter to continue...")
            return None

        # wait
        if stmt.startswith('wait '):
            sec_expr = stmt[5:].strip()
            sec = float(self.evaluate_expression(sec_expr))
            time_module.sleep(sec)
            return None

        # global_variable
        if stmt.startswith('global_variable = '):
            names = stmt[18:].split(',')
            for n in names:
                n = n.strip()
                self.declared_globals.add(n)
                if n not in self.global_vars:
                    self.global_vars[n] = None
            return None

        # local_variable
        if stmt.startswith('local_variable = '):
            if self.local_scope is None:
                self.raise_error(DoScriptError, "local_variable can only be used inside functions")
            names = stmt[17:].split(',')
            for n in names:
                n = n.strip()
                if n not in self.local_scope:
                    self.local_scope[n] = None
            return None

        # return
        if stmt.startswith('return'):
            if stmt == 'return':
                return ('return', None)
            else:
                val = self.evaluate_expression(stmt[6:].strip())
                return ('return', val)

        # assignment
        if '=' in stmt and not stmt.startswith(('if ', 'repeat ', 'loop ', 'for_each ', 'for_each_line ')):
            m = re.match(r'^(\w+)\s*=\s*(.+)$', stmt)
            if m:
                var_name = m.group(1)
                rhs = m.group(2).strip()
                if rhs.startswith('run '):
                    res = self._exec_statement(rhs)
                    if res and res[0] == 'exit_code':
                        self.set_variable(var_name, res[1])
                    else:
                        self.set_variable(var_name, 0)
                elif rhs.startswith('capture '):
                    res = self._exec_statement(rhs)
                    if res and res[0] == 'capture_output':
                        self.set_variable(var_name, res[1])
                    else:
                        self.set_variable(var_name, "")
                else:
                    val = self.evaluate_expression(rhs)
                    self.set_variable(var_name, val)
            return None

        # nothing matched
        self.raise_error(DoScriptError, f"Unknown statement: {stmt}")

    # ----------------------------
    # Calculate file age
    # ----------------------------
    def calculate_file_age(self, timestamp: float) -> Dict[str, float]:
        """Calculate how old a file is in various units"""
        now = time_module.time()
        age_seconds = now - timestamp
        
        return {
            'seconds': age_seconds,
            'minutes': age_seconds / 60,
            'hours': age_seconds / 3600,
            'days': age_seconds / 86400,
            'months': age_seconds / (86400 * 30.44),  # Average month length
            'years': age_seconds / (86400 * 365.25),  # Account for leap years
        }

    # ----------------------------
    # Top-level block execution
    # ----------------------------
    def execute_lines(self, lines: List[str], start_idx: int = 0, end_idx: Optional[int] = None, line_map: Optional[List[int]] = None):
        if end_idx is None:
            end_idx = len(lines)
        if line_map is None:
            line_map = self.current_line_map
        i = start_idx
        # lines is a list of statements; track real line numbers for error reporting
        while i < end_idx:
            stmt = lines[i].strip()
            # set current position for error reporting
            if 0 <= i < len(line_map):
                self.current_line = line_map[i]
            else:
                self.current_line = i + 1
            self.current_source = stmt
            # function def
            if stmt.startswith('function '):
                m = re.match(r'function\s+(\w+)\s*(.*)', stmt)
                if m:
                    fname = m.group(1)
                    params = [p for p in m.group(2).split() if p]
                    end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_function', line_map)
                    self.functions[fname] = {'params': params, 'body': body, 'line_map': body_line_map}
                    i = end_i + 1
                    continue

            # macro def
            if stmt.startswith('make a_command '):
                name = stmt[14:].strip()
                end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_command', line_map)
                self.macros[name] = {'body': body, 'line_map': body_line_map}
                i = end_i + 1
                continue
            if stmt.startswith('make a command '):
                # backward compatibility (deprecated)
                print("Warning: 'make a command' is deprecated. Use 'make a_command'.", file=sys.stderr)
                name = stmt[15:].strip()
                end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_command', line_map)
                self.macros[name] = {'body': body, 'line_map': body_line_map}
                i = end_i + 1
                continue

            # IF
            if stmt.startswith('if '):
                cond_expr = stmt[3:].strip()
                m = re.match(r'ends_with\s+(.+?)\s+("([^"]+)"|\'([^\']+)\')\s*$', cond_expr)
                if m:
                    left_expr = m.group(1).strip()
                    suffix = m.group(3) if m.group(3) is not None else m.group(4)
                    cond = self.evaluate_expression(f'endswith({left_expr}, "{suffix}")')
                else:
                    cond = self.evaluate_expression(cond_expr)
                depth = 1
                else_idx = None
                elif_blocks: List[Tuple[int, str]] = []
                end_if_idx = None
                j = i + 1
                while j < end_idx:
                    line = lines[j].strip()
                    if line.startswith('if '):
                        depth += 1
                    elif line.startswith('else_if ') and depth == 1:
                        elif_blocks.append((j, line[len('else_if '):].strip()))
                    elif line == 'else' and depth == 1:
                        else_idx = j
                    elif line == 'end_if':
                        depth -= 1
                        if depth == 0:
                            end_if_idx = j
                            break
                    j += 1
                if end_if_idx is None:
                    self.raise_error(DoScriptError, "Missing end_if")
                branch_points = [idx for idx, _ in elif_blocks]
                if else_idx is not None:
                    branch_points.append(else_idx)
                if cond:
                    block_end = branch_points[0] if branch_points else end_if_idx
                    res = self.execute_lines(lines, i + 1, block_end, line_map)
                    if res and res[0] in ('return', 'break', 'continue'):
                        return res
                else:
                    handled = False
                    for idx, branch_expr in elif_blocks:
                        branch_cond = self.evaluate_expression(branch_expr)
                        next_points = [p for p in branch_points if p > idx]
                        branch_end = next_points[0] if next_points else end_if_idx
                        if branch_cond:
                            res = self.execute_lines(lines, idx + 1, branch_end, line_map)
                            if res and res[0] in ('return', 'break', 'continue'):
                                return res
                            handled = True
                            break
                    if not handled and else_idx is not None:
                        res = self.execute_lines(lines, else_idx + 1, end_if_idx, line_map)
                        if res and res[0] in ('return', 'break', 'continue'):
                            return res
                i = end_if_idx + 1
                continue

            # repeat
            if stmt.startswith('repeat '):
                count_expr = stmt[7:].strip()
                count = int(self.evaluate_expression(count_expr))
                end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_repeat', line_map)
                for _ in range(count):
                    res = self.execute_lines(body, 0, len(body), body_line_map)
                    propagated = self._propagate_control_flow(res)
                    if propagated is not None:
                        if propagated[0] == 'break':
                            break
                        return propagated
                i = end_i + 1
                continue

            # loop
            if stmt.startswith('loop '):
                loop_expr = stmt[5:].strip()
                index_var = None
                m_loop_idx = re.match(r'(.+?)\s+as\s+(\w+)$', loop_expr)
                if m_loop_idx:
                    loop_expr = m_loop_idx.group(1).strip()
                    index_var = m_loop_idx.group(2)
                    if self.local_scope is not None:
                        if index_var not in self.local_scope:
                            self.local_scope[index_var] = None
                    else:
                        self.declared_globals.add(index_var)
                        if index_var not in self.global_vars:
                            self.global_vars[index_var] = None
                end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_loop', line_map)
                if loop_expr == 'forever':
                    iteration = 1
                    while True:
                        try:
                            if index_var:
                                self.set_variable(index_var, iteration)
                            res = self.execute_lines(body, 0, len(body), body_line_map)
                            propagated = self._propagate_control_flow(res)
                            if propagated is not None:
                                if propagated[0] == 'break':
                                    break
                                return propagated
                            iteration += 1
                        except KeyboardInterrupt:
                            break
                else:
                    count = int(self.evaluate_expression(loop_expr))
                    for iteration in range(1, count + 1):
                        if index_var:
                            self.set_variable(index_var, iteration)
                        res = self.execute_lines(body, 0, len(body), body_line_map)
                        propagated = self._propagate_control_flow(res)
                        if propagated is not None:
                            if propagated[0] == 'break':
                                break
                            return propagated
                i = end_i + 1
                continue

            # try/catch
            if stmt == 'try':
                catch_blocks = []
                depth = 1
                j = i + 1
                try_body_end = None
                while j < end_idx:
                    line = lines[j].strip()
                    if line == 'try':
                        depth += 1
                    elif line.startswith('catch'):
                        if depth == 1:
                            if try_body_end is None:
                                try_body_end = j
                            error_type = None
                            if line != 'catch':
                                error_type = line[6:].strip()
                            k = j + 1
                            while k < end_idx:
                                next_line = lines[k].strip()
                                if next_line == 'end_try' or next_line.startswith('catch'):
                                    break
                                k += 1
                            catch_blocks.append({'type': error_type, 'start': j + 1, 'end': k})
                            j = k - 1
                    elif line == 'end_try':
                        depth -= 1
                        if depth == 0:
                            if try_body_end is None:
                                try_body_end = j
                            try:
                                res = self.execute_lines(lines, i + 1, try_body_end, line_map)
                                propagated = self._propagate_control_flow(res, allow_continue=False)
                                if propagated is not None:
                                    return propagated
                            except DoScriptError as e:
                                handled = False
                                error_class_name = type(e).__name__
                                for cb in catch_blocks:
                                    if cb['type'] is None or cb['type'] == error_class_name:
                                        res = self.execute_lines(lines, cb['start'], cb['end'], line_map)
                                        propagated = self._propagate_control_flow(res, allow_continue=False)
                                        if propagated is not None:
                                            return propagated
                                        handled = True
                                        break
                                if not handled:
                                    raise
                            i = j + 1
                            break
                    j += 1
                continue

            # for_each (here/deep or list)
            if stmt.startswith('for_each ') and ('_in ' in stmt or ' in ' in stmt):
                m_var_in = re.match(r'for_each\s+(\w+)_in\s+(.+)$', stmt)
                m_var_list = None
                if not m_var_in:
                    m_var_list = re.match(r'for_each\s+(\w+)\s+in\s+(.+)$', stmt)
                if m_var_in:
                    var_name = m_var_in.group(1)
                    token = m_var_in.group(2).strip()
                    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                        pattern = self.extract_string(token)
                        if pattern == '*' or pattern == '**':
                            print("Warning: legacy '*' or '**' used; prefer 'here' or 'deep'.", file=sys.stderr)
                    else:
                        pattern = token
                    # Parse optional age filter: older_than N days/hours/minutes/seconds/months/years
                    #                             newer_than N days/...
                    age_filter_dir = None   # 'older' or 'newer'
                    age_filter_seconds = None
                    age_m = re.match(
                        r'^(.+?)\s+(older_than|newer_than)\s+(\d+(?:\.\d+)?)\s+(second|seconds|minute|minutes|hour|hours|day|days|month|months|year|years)$',
                        token
                    )
                    if age_m:
                        token = age_m.group(1).strip()
                        age_filter_dir = 'older' if age_m.group(2) == 'older_than' else 'newer'
                        age_amount = float(age_m.group(3))
                        age_unit = age_m.group(4).rstrip('s')  # normalise plural
                        unit_secs = {'second': 1, 'minute': 60, 'hour': 3600,
                                     'day': 86400, 'month': 2629800, 'year': 31557600}
                        age_filter_seconds = age_amount * unit_secs.get(age_unit, 86400)
                        # re-evaluate pattern after stripping age clause
                        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                            token = self.extract_string(token)
                        pattern = token
                    handle_folders = var_name.lower().startswith('folder') or var_name.lower().startswith('dir')
                    matched_paths: List[str] = []
                    if pattern == 'here':
                        base = self.script_path_stack[-1] if self.script_path_stack else os.getcwd()
                        try:
                            entries = [os.path.join(base, e) for e in os.listdir(base)]
                        except Exception:
                            entries = []
                        if handle_folders:
                            matched_paths = [p for p in entries if os.path.isdir(p)]
                        else:
                            matched_paths = [p for p in entries if os.path.isfile(p)]
                    elif pattern == 'deep':
                        base = self.script_path_stack[-1] if self.script_path_stack else os.getcwd()
                        matched = []
                        for root, dirs, files in os.walk(base):
                            if handle_folders:
                                for d in dirs:
                                    matched.append(os.path.join(root, d))
                            else:
                                for f in files:
                                    matched.append(os.path.join(root, f))
                        matched_paths = matched
                    else:
                        if pattern == '*' or pattern == '**':
                            print("Warning: legacy glob used; prefer 'here' or 'deep'.", file=sys.stderr)
                        resolved = self.resolve_path(pattern)
                        # If resolved is a directory, list its contents
                        if os.path.isdir(resolved):
                            try:
                                entries = [os.path.join(resolved, e) for e in os.listdir(resolved)]
                            except Exception:
                                entries = []
                            if handle_folders:
                                matched_paths = [p for p in entries if os.path.isdir(p)]
                            else:
                                matched_paths = [p for p in entries if os.path.isfile(p)]
                        else:
                            if '**' in pattern:
                                matched_all = glob.glob(resolved, recursive=True)
                            else:
                                matched_all = glob.glob(resolved)
                            if handle_folders:
                                matched_paths = [p for p in matched_all if os.path.isdir(p)]
                            else:
                                matched_paths = [p for p in matched_all if os.path.isfile(p)]
                    # Apply age filter if specified
                    if age_filter_seconds is not None:
                        now_ts = time_module.time()
                        filtered = []
                        for p in matched_paths:
                            try:
                                mtime = os.path.getmtime(p)
                                age_secs = now_ts - mtime
                                if age_filter_dir == 'older' and age_secs >= age_filter_seconds:
                                    filtered.append(p)
                                elif age_filter_dir == 'newer' and age_secs < age_filter_seconds:
                                    filtered.append(p)
                            except Exception:
                                pass
                        matched_paths = filtered

                    # ensure declared
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_for', line_map)
                    self.loop_var_stack.append(var_name)
                    loop_count = 0
                    try:
                        for full_path in matched_paths:
                            loop_count += 1
                            full_abs = os.path.abspath(full_path)
                            basename = os.path.basename(full_abs)
                            # set primary var to basename
                            self.set_variable(var_name, basename)
                            alias = var_name + '_'
                            if alias not in self.declared_globals:
                                self.declared_globals.add(alias)
                                self.global_vars[alias] = None
                            self.global_vars[alias] = basename
                            # prepare metadata
                            meta = {}
                            meta[var_name + '_path'] = full_abs
                            meta[var_name + '_name'] = basename
                            meta[var_name + '_'] = basename
                            try:
                                st = os.stat(full_abs)
                            except Exception:
                                st = None
                            if os.path.isfile(full_abs):
                                size = int(st.st_size) if st else 0
                                created = int(st.st_ctime) if st else 0
                                modified = int(st.st_mtime) if st else 0
                                accessed = int(st.st_atime) if st else 0
                                
                                # Calculate file age based on modification time
                                age_data = self.calculate_file_age(modified)
                                
                                meta[var_name + '_ext'] = os.path.splitext(basename)[1]
                                meta[var_name + '_size'] = size
                                meta[var_name + '_size_kb'] = round(size / 1024, 3)
                                meta[var_name + '_size_mb'] = round(size / (1024*1024), 3)
                                meta[var_name + '_created'] = created
                                meta[var_name + '_modified'] = modified
                                meta[var_name + '_accessed'] = accessed
                                meta[var_name + '_is_dir'] = False
                                meta[var_name + '_is_empty'] = (size == 0)
                                
                                # Add age metadata
                                meta[var_name + '_is_old_seconds'] = age_data['seconds']
                                meta[var_name + '_is_old_minutes'] = age_data['minutes']
                                meta[var_name + '_is_old_hours'] = age_data['hours']
                                meta[var_name + '_is_old_days'] = age_data['days']
                                meta[var_name + '_is_old_months'] = age_data['months']
                                meta[var_name + '_is_old_years'] = age_data['years']
                                
                            elif os.path.isdir(full_abs):
                                created = int(st.st_ctime) if st else 0
                                modified = int(st.st_mtime) if st else 0
                                accessed = int(st.st_atime) if st else 0
                                
                                # Calculate folder age based on modification time
                                age_data = self.calculate_file_age(modified)
                                
                                try:
                                    is_empty = (len(os.listdir(full_abs)) == 0)
                                except Exception:
                                    is_empty = False
                                meta[var_name + '_is_empty'] = is_empty
                                meta[var_name + '_created'] = created
                                meta[var_name + '_modified'] = modified
                                meta[var_name + '_accessed'] = accessed
                                meta[var_name + '_is_dir'] = True
                                meta[var_name + '_ext'] = ''
                                meta[var_name + '_size'] = 0
                                meta[var_name + '_size_kb'] = 0.0
                                meta[var_name + '_size_mb'] = 0.0
                                
                                # Add age metadata for folders too
                                meta[var_name + '_is_old_seconds'] = age_data['seconds']
                                meta[var_name + '_is_old_minutes'] = age_data['minutes']
                                meta[var_name + '_is_old_hours'] = age_data['hours']
                                meta[var_name + '_is_old_days'] = age_data['days']
                                meta[var_name + '_is_old_months'] = age_data['months']
                                meta[var_name + '_is_old_years'] = age_data['years']
                                
                            # inject metadata
                            for k, v in meta.items():
                                if k not in self.declared_globals:
                                    self.declared_globals.add(k)
                                    self.global_vars[k] = None
                                self.global_vars[k] = v
                            
                            # inject file content for text files (for if_file_contains)
                            content_key = var_name + '_content'
                            if os.path.isfile(full_abs):
                                text_exts = {'.txt', '.md', '.csv', '.log', '.json', '.xml',
                                             '.html', '.htm', '.py', '.js', '.ts', '.css',
                                             '.yaml', '.yml', '.ini', '.cfg', '.conf',
                                             '.do', '.sh', '.bat', '.ps1', '.rst', '.toml'}
                                _, ext = os.path.splitext(basename)
                                if ext.lower() in text_exts:
                                    try:
                                        with open(full_abs, 'r', encoding='utf-8', errors='ignore') as f:
                                            file_content = f.read()
                                    except Exception:
                                        file_content = ''
                                else:
                                    file_content = ''
                            else:
                                file_content = ''
                            if content_key not in self.declared_globals:
                                self.declared_globals.add(content_key)
                                self.global_vars[content_key] = None
                            self.global_vars[content_key] = file_content

                            # --- Execute body as a proper block (preserve if_ends_with sugar) ---
                            transformed: List[str] = []
                            p = 0
                            while p < len(body):
                                ln = body[p]
                                stripped = ln.strip()
                                if stripped.startswith('if_ends_with '):
                                    suffix_tok = stripped[len('if_ends_with '):].strip()
                                    suffix = self.extract_string(suffix_tok)
                                    current_var = self.loop_var_stack[-1] if self.loop_var_stack else None
                                    if current_var is None:
                                        self.raise_error(DoScriptError, "if_ends_with used outside for_each")
                                    cond_expr = f'endswith({current_var}_name, \"{suffix}\")'
                                    q, inner_lines = self._extract_if_block(body, p, 'if_ends_with')
                                    transformed.append(f'if {cond_expr}')
                                    transformed.extend(inner_lines)
                                    transformed.append('end_if')
                                    p = q + 1
                                elif stripped.startswith('if_file_contains '):
                                    # if_file_contains "keyword" → checks file_content variable
                                    keyword_tok = stripped[len('if_file_contains '):].strip()
                                    keyword = self.extract_string(keyword_tok)
                                    current_var = self.loop_var_stack[-1] if self.loop_var_stack else None
                                    if current_var is None:
                                        self.raise_error(DoScriptError, "if_file_contains used outside for_each")
                                    cond_expr = f'contains({current_var}_content, \"{keyword}\")'
                                    q, inner_lines = self._extract_if_block(body, p, 'if_file_contains')
                                    transformed.append(f'if {cond_expr}')
                                    transformed.extend(inner_lines)
                                    transformed.append('end_if')
                                    p = q + 1
                                elif stripped.startswith('if_file_not_contains '):
                                    # if_file_not_contains "keyword" → checks file does NOT contain keyword
                                    keyword_tok = stripped[len('if_file_not_contains '):].strip()
                                    keyword = self.extract_string(keyword_tok)
                                    current_var = self.loop_var_stack[-1] if self.loop_var_stack else None
                                    if current_var is None:
                                        self.raise_error(DoScriptError, "if_file_not_contains used outside for_each")
                                    cond_expr = f'notcontains({current_var}_content, "{keyword}")'
                                    q, inner_lines = self._extract_if_block(body, p, 'if_file_not_contains')
                                    transformed.append(f'if {cond_expr}')
                                    transformed.extend(inner_lines)
                                    transformed.append('end_if')
                                    p = q + 1
                                else:
                                    transformed.append(ln)
                                    p += 1

                            res = self.execute_lines(transformed, 0, len(transformed), body_line_map)
                            if res is not None:
                                if res[0] == 'break':
                                    # break out of the file iteration loop
                                    break
                                if res[0] == 'continue':
                                    # next file
                                    continue
                                if res[0] == 'return':
                                    return res
                    finally:
                        self.loop_var_stack.pop()
                    # expose loop_count after the loop
                    if 'loop_count' not in self.declared_globals:
                        self.declared_globals.add('loop_count')
                    self.global_vars['loop_count'] = loop_count
                    i = end_i + 1
                    continue
                elif m_var_list:
                    var_name = m_var_list.group(1)
                    list_expr = m_var_list.group(2).strip()
                    items = []
                    # Support iterating a list variable as well as a literal list
                    if not (',' in list_expr or list_expr.startswith(('"', "'"))):
                        # Might be a variable holding a list
                        try:
                            maybe_list = self.evaluate_expression(list_expr)
                            if isinstance(maybe_list, list):
                                items = maybe_list
                            else:
                                items = [maybe_list]
                        except Exception:
                            items = []
                    else:
                        parts = self._split_args(list_expr)
                        for p in parts:
                            items.append(self.evaluate_expression(p))
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_for', line_map)
                    list_loop_count = 0
                    for item in items:
                        list_loop_count += 1
                        self.set_variable(var_name, item)
                        res = self.execute_lines(body, 0, len(body), body_line_map)
                        propagated = self._propagate_control_flow(res)
                        if propagated is not None:
                            if propagated[0] == 'break':
                                break
                            return propagated
                    # expose loop_count
                    if 'loop_count' not in self.declared_globals:
                        self.declared_globals.add('loop_count')
                    self.global_vars['loop_count'] = list_loop_count
                    i = end_i + 1
                    continue

            # for_each_line
            if stmt.startswith('for_each_line ') and ' in ' in stmt:
                m = re.match(r'for_each_line\s+(\w+)\s+in\s+(.+)$', stmt)
                if m:
                    var_name = m.group(1)
                    file_expr = m.group(2).strip()
                    file_val = self.evaluate_expression(file_expr)
                    file_str = str(file_val)
                    file_str = self.interpolate_if_needed(file_str)
                    file_resolved = self.resolve_path(file_str)
                    end_i, body, body_line_map = self.execute_block(lines, i + 1, 'end_for', line_map)
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    try:
                        with open(file_resolved, 'r', encoding='utf-8') as fh:
                            for raw_line in fh:
                                ln = raw_line.rstrip('\n\r')
                                self.set_variable(var_name, ln)
                                res = self.execute_lines(body, 0, len(body), body_line_map)
                                propagated = self._propagate_control_flow(res)
                                if propagated is not None:
                                    if propagated[0] == 'break':
                                        break
                                    return propagated
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to read file '{file_str}': {e}")
                    i = end_i + 1
                    continue

            # multi-line make file "path" with ... end_file
            if stmt.startswith('make file ') and stmt.endswith(' with'):
                # Collect lines until end_file
                path_part = stmt[len('make file '):-len(' with')].strip()
                file_path = self.extract_string(path_part)
                j = i + 1
                body_lines = []
                while j < end_idx:
                    ln = lines[j].strip()
                    if ln == 'end_file':
                        break
                    body_lines.append(lines[j])
                    j += 1
                if j >= end_idx:
                    self.raise_error(DoScriptError, "Missing end_file")
                # Interpolate each body line
                content_str = '\n'.join(self.interpolate_string(ln) for ln in body_lines)
                resolved = os.path.abspath(self.resolve_path(file_path))
                if self.dry_run:
                    self.log_dry(f"make file (multiline) {resolved} ({len(body_lines)} lines)")
                else:
                    try:
                        os.makedirs(os.path.dirname(resolved) or '.', exist_ok=True)
                        with open(resolved, 'w', encoding='utf-8') as fh:
                            fh.write(content_str)
                        self.log_info(f"Created file {resolved}")
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to create file '{file_path}': {e}")
                i = j + 1
                continue

            # default
            res = self._exec_statement(stmt)
            if res is not None:
                if res[0] in ('return','break','continue'):
                    return res
            i += 1

    # ----------------------------
    # Runner
    # ----------------------------
    def run(self, filename: str):
        # set current file BEFORE parsing/execution (for errors)
        if not os.path.exists(filename):
            # set context then raise
            self.current_file = filename
            self.current_line = 0
            self.current_source = ""
            self.raise_error(FileError, f"Script file not found: {filename}")
        self.current_file = os.path.abspath(filename)
        script_dir = os.path.abspath(os.path.dirname(filename))
        self.script_path_stack.append(script_dir)
        try:
            lines = self.parse_script(filename)
            self.execute_lines(lines)
        finally:
            if self.script_path_stack and self.script_path_stack[-1] == script_dir:
                self.script_path_stack.pop()

# ----------------------------
# CLI
# ----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  python doscript.py <script.do> [--dry-run] [--verbose] [args...]", file=sys.stderr)
        print("", file=sys.stderr)
        print("To create a new script, use the 'make file' command inside a script:", file=sys.stderr)
        print("  make file \"myscript.do\" \"say 'Hello World!'\"", file=sys.stderr)
        sys.exit(1)
    
    argv = sys.argv[1:]
    dry = False
    verbose = False
    # collect flags
    normalized = []
    for a in argv:
        if a == '--dry-run':
            dry = True
        elif a == '--verbose':
            verbose = True
        else:
            normalized.append(a)
    if not normalized:
        print("Error: no script provided", file=sys.stderr)
        sys.exit(1)
    script = normalized[0]
    cli_args = normalized[1:]
    interp = DoScriptInterpreter(dry_run=dry, verbose=verbose)
    cleanup_dir = None

    # --- Update checker: URL from your request ---
    # The provided URL and repo link (as requested)
    version_check_url = "https://github.com/TheServer-lab/DoScript/blob/main/version.txt"
    repo_url = "https://github.com/TheServer-lab/DoScript"
    # perform update check (non-fatal)
    try:
        check_for_updates(interp, version_check_url, repo_url, timeout=5)
    except Exception as e:
        # don't fail startup if update check errors out
        interp.log_verbose(f"Update check raised exception: {e}")

    # populate arg1..arg32
    for i in range(1, 33):
        name = f'arg{i}'
        value = cli_args[i-1] if i-1 < len(cli_args) else ""
        interp.global_vars[name] = value
    try:
        if _is_remote_script_target(script):
            try:
                local_script, cleanup_dir = _download_remote_script(script, timeout=30)
                interp.log_info(f"Downloaded remote script: {script}")
                script = local_script
            except Exception as e:
                raise NetworkError(f"Failed to download remote script '{script}': {e}")
        interp.run(script)
    except DoScriptError as e:
        # pretty print error with context
        header = f"DoScript {type(e).__name__}: {e.message}"
        print(header, file=sys.stderr)
        if e.file:
            line_info = f"  in {e.file}"
            if e.line:
                line_info += f":{e.line}"
            print(line_info, file=sys.stderr)
        if e.source:
            print(f"  → {e.source}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nScript interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if cleanup_dir:
            try:
                shutil.rmtree(cleanup_dir)
            except Exception:
                pass

if __name__ == '__main__':
    main()

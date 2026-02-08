#!/usr/bin/env python3
"""
DoScript v0.6 - CLI args + basic logging + error reporting
Fixed: for_each body now executes full blocks (fixes unknown-statement errors inside for_each bodies)
"""

import os
import sys
import re
import glob
import shutil
import subprocess
import urllib.request
import ast
import operator
import time
from typing import Any, Dict, List, Optional, Tuple

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
        self.macros: Dict[str, List[str]] = {}
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
        # CLI args initialization (filled by CLI runner)
        # populate arg1..arg32 with empty strings and mark as declared (read-only)
        for i in range(1, 33):
            name = f'arg{i}'
            self.declared_globals.add(name)
            self.global_vars[name] = ""

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
    # Variables (argN are read-only)
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
        if self.local_scope is not None and name in self.local_scope:
            self.local_scope[name] = value
            return
        if name in self.declared_globals:
            self.global_vars[name] = value
            return
        self.raise_error(DoScriptError, f"Variable '{name}' used before declaration")

    # ----------------------------
    # Expression evaluation (safe)
    # ----------------------------
    def evaluate_expression(self, expr: str) -> Any:
        expr = expr.strip()
        if not expr:
            return ""

        # String literal double-quoted -> decode escapes
        if (expr.startswith('"') and expr.endswith('"')) and len(expr) >= 2:
            inner = expr[1:-1]
            try:
                return bytes(inner, "utf-8").decode("unicode_escape")
            except Exception:
                return inner

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
            if fname == 'split':
                if len(args) == 1:
                    return str(self.evaluate_expression(args[0])).split()
                if len(args) == 2:
                    return str(self.evaluate_expression(args[0])).split(str(self.evaluate_expression(args[1])))
                return []
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
        prev_local = self.local_scope
        self.local_scope = {}
        for i, p in enumerate(params):
            self.local_scope[p] = args[i] if i < len(args) else None
        ret = None
        try:
            for s in body:
                r = self._exec_statement(s)
                if r is not None and r[0] == 'return':
                    ret = r[1]
                    break
                if r is not None and r[0] in ('break','continue'):
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
        cur = ""
        for line in raw:
            # remove comments (note: simplistic - removes everything after # or //)
            line = re.sub(r'#.*$', '', line)
            line = re.sub(r'//.*$', '', line)
            line = line.rstrip('\n\r')
            t = line.strip()
            if t:
                cur += (" " + t) if cur else t
                out.append(cur)
                cur = ""
        return out

    def extract_string(self, s: str) -> str:
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            inner = s[1:-1]
            try:
                return bytes(inner, "utf-8").decode("unicode_escape")
            except Exception:
                return inner
        if s.startswith("'") and s.endswith("'"):
            return self.interpolate_string(s[1:-1])
        return s

    # ----------------------------
    # Block extraction
    # ----------------------------
    def execute_block(self, lines: List[str], start_idx: int, end_keyword: str) -> Tuple[int, List[str]]:
        block: List[str] = []
        i = start_idx
        depth = 1
        start_keywords = {
            'end_function': 'function',
            'end_loop': 'loop',
            'end_repeat': 'repeat',
            'end_if': 'if',
            'end_try': 'try',
            'end_command': 'make a_command',
            'end_for': 'for_each',
        }
        start_keyword = start_keywords.get(end_keyword, '')
        while i < len(lines):
            line = lines[i].strip()
            if start_keyword and line.startswith(start_keyword):
                depth += 1
            elif line == end_keyword or line.startswith(end_keyword + ' '):
                depth -= 1
                if depth == 0:
                    return i, block
            block.append(lines[i])
            i += 1
        self.raise_error(DoScriptError, f"Missing {end_keyword}")

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
            p = self.extract_string(stmt[9:])
            resolved = p
            if self.dry_run:
                self.log_dry(f"path add {resolved}")
            else:
                if sys.platform == 'win32':
                    try:
                        self.log_info("path add on Windows requires admin/setup - skipping persistent change (use installer patterns).")
                    except Exception as e:
                        self.raise_error(ProcessError, f"path add failed: {e}")
                else:
                    self.log_info("path add (persistent) is OS-specific; please add to your shell profile manually.")
            return None
        if stmt.startswith('path remove '):
            p = self.extract_string(stmt[12:])
            resolved = p
            if self.dry_run:
                self.log_dry(f"path remove {resolved}")
            else:
                self.log_info("path remove is OS-specific; interpreter won't modify persistent PATH automatically.")
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
            lines = self.parse_script(resolved)
            # execute included file with context
            self.execute_lines(lines)
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
                    try:
                        content = bytes(inner, "utf-8").decode("unicode_escape")
                    except Exception:
                        content = inner
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
            m = re.match(r'download\s+"([^"]+)"\s+to\s+"([^"]+)"$', stmt)
            if m:
                url, path = m.groups()
                resolved = os.path.abspath(self.resolve_path(path))
                if self.dry_run:
                    self.log_dry(f"download {url} -> {resolved}")
                else:
                    try:
                        os.makedirs(os.path.dirname(resolved), exist_ok=True)
                        urllib.request.urlretrieve(url, resolved)
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
                for s in self.macros[name]:
                    self._exec_statement(s)
                return None
            else:
                try:
                    subprocess.run(name, shell=True, check=False)
                    self.log_info(f"Ran shell: {name}")
                except Exception as e:
                    self.raise_error(ProcessError, f"Failed to run '{name}': {e}")
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
            time.sleep(sec)
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
    # Top-level block execution
    # ----------------------------
    def execute_lines(self, lines: List[str], start_idx: int = 0, end_idx: Optional[int] = None):
        if end_idx is None:
            end_idx = len(lines)
        i = start_idx
        # lines is a list of statements; track real line numbers for error reporting
        while i < end_idx:
            stmt = lines[i].strip()
            # set current position for error reporting
            # +1 because lines are 0-indexed list constructed from parse_script
            self.current_line = i + 1
            self.current_source = stmt
            # function def
            if stmt.startswith('function '):
                m = re.match(r'function\s+(\w+)\s*(.*)', stmt)
                if m:
                    fname = m.group(1)
                    params = [p for p in m.group(2).split() if p]
                    end_i, body = self.execute_block(lines, i + 1, 'end_function')
                    self.functions[fname] = {'params': params, 'body': body}
                    i = end_i + 1
                    continue

            # macro def
            if stmt.startswith('make a_command '):
                name = stmt[14:].strip()
                end_i, body = self.execute_block(lines, i + 1, 'end_command')
                self.macros[name] = body
                i = end_i + 1
                continue
            if stmt.startswith('make a command '):
                # backward compatibility (deprecated)
                print("Warning: 'make a command' is deprecated. Use 'make a_command'.", file=sys.stderr)
                name = stmt[15:].strip()
                end_i, body = self.execute_block(lines, i + 1, 'end_command')
                self.macros[name] = body
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
                end_if_idx = None
                j = i + 1
                while j < end_idx:
                    line = lines[j].strip()
                    if line.startswith('if '):
                        depth += 1
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
                if cond:
                    block_end = else_idx if else_idx else end_if_idx
                    res = self.execute_lines(lines, i + 1, block_end)
                    if res and res[0] in ('return', 'break', 'continue'):
                        return res
                else:
                    if else_idx:
                        res = self.execute_lines(lines, else_idx + 1, end_if_idx)
                        if res and res[0] in ('return', 'break', 'continue'):
                            return res
                i = end_if_idx + 1
                continue

            # repeat
            if stmt.startswith('repeat '):
                count_expr = stmt[7:].strip()
                count = int(self.evaluate_expression(count_expr))
                end_i, body = self.execute_block(lines, i + 1, 'end_repeat')
                for _ in range(count):
                    res = self.execute_lines(body, 0, len(body))
                    if res and res[0] == 'break':
                        break
                i = end_i + 1
                continue

            # loop
            if stmt.startswith('loop '):
                loop_expr = stmt[5:].strip()
                end_i, body = self.execute_block(lines, i + 1, 'end_loop')
                if loop_expr == 'forever':
                    while True:
                        try:
                            res = self.execute_lines(body, 0, len(body))
                            if res and res[0] == 'break':
                                break
                        except KeyboardInterrupt:
                            break
                else:
                    count = int(self.evaluate_expression(loop_expr))
                    for _ in range(count):
                        res = self.execute_lines(body, 0, len(body))
                        if res and res[0] == 'break':
                            break
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
                                self.execute_lines(lines, i + 1, try_body_end)
                            except DoScriptError as e:
                                handled = False
                                error_class_name = type(e).__name__
                                for cb in catch_blocks:
                                    if cb['type'] is None or cb['type'] == error_class_name:
                                        self.execute_lines(lines, cb['start'], cb['end'])
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
                        if '**' in pattern:
                            matched_all = glob.glob(resolved, recursive=True)
                        else:
                            matched_all = glob.glob(resolved)
                        if handle_folders:
                            matched_paths = [p for p in matched_all if os.path.isdir(p)]
                        else:
                            matched_paths = [p for p in matched_all if os.path.isfile(p)]
                    # ensure declared
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    end_i, body = self.execute_block(lines, i + 1, 'end_for')
                    self.loop_var_stack.append(var_name)
                    try:
                        for full_path in matched_paths:
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
                                meta[var_name + '_ext'] = os.path.splitext(basename)[1]
                                meta[var_name + '_size'] = size
                                meta[var_name + '_size_kb'] = round(size / 1024, 3)
                                meta[var_name + '_size_mb'] = round(size / (1024*1024), 3)
                                meta[var_name + '_created'] = created
                                meta[var_name + '_modified'] = modified
                                meta[var_name + '_accessed'] = accessed
                                meta[var_name + '_is_dir'] = False
                                meta[var_name + '_is_empty'] = (size == 0)
                            elif os.path.isdir(full_abs):
                                created = int(st.st_ctime) if st else 0
                                modified = int(st.st_mtime) if st else 0
                                accessed = int(st.st_atime) if st else 0
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
                            # inject metadata
                            for k, v in meta.items():
                                if k not in self.declared_globals:
                                    self.declared_globals.add(k)
                                    self.global_vars[k] = None
                                self.global_vars[k] = v

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
                                    inner_lines = []
                                    q = p + 1
                                    while q < len(body):
                                        if body[q].strip() == 'end_if':
                                            break
                                        inner_lines.append(body[q])
                                        q += 1
                                    if q >= len(body):
                                        self.raise_error(DoScriptError, "Missing end_if in if_ends_with block")
                                    transformed.append(f'if {cond_expr}')
                                    transformed.extend(inner_lines)
                                    transformed.append('end_if')
                                    p = q + 1
                                else:
                                    transformed.append(ln)
                                    p += 1

                            res = self.execute_lines(transformed, 0, len(transformed))
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
                    i = end_i + 1
                    continue
                elif m_var_list:
                    var_name = m_var_list.group(1)
                    list_expr = m_var_list.group(2).strip()
                    items = []
                    parts = self._split_args(list_expr)
                    for p in parts:
                        items.append(self.evaluate_expression(p))
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    end_i, body = self.execute_block(lines, i + 1, 'end_for')
                    for item in items:
                        self.set_variable(var_name, item)
                        res = self.execute_lines(body, 0, len(body))
                        if res and res[0] == 'break':
                            break
                        if res and res[0] == 'continue':
                            continue
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
                    end_i, body = self.execute_block(lines, i + 1, 'end_for')
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    try:
                        with open(file_resolved, 'r', encoding='utf-8') as fh:
                            for raw_line in fh:
                                ln = raw_line.rstrip('\n\r')
                                self.set_variable(var_name, ln)
                                res = self.execute_lines(body, 0, len(body))
                                if res and res[0] == 'break':
                                    break
                                if res and res[0] == 'continue':
                                    continue
                    except Exception as e:
                        self.raise_error(FileError, f"Failed to read file '{file_str}': {e}")
                    i = end_i + 1
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
        print("Usage: python doscript_v0_6_fixed.py <script.do> [--dry-run] [--verbose] [args...]", file=sys.stderr)
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
    # populate arg1..arg32
    for i in range(1, 33):
        name = f'arg{i}'
        value = cli_args[i-1] if i-1 < len(cli_args) else ""
        interp.global_vars[name] = value
    try:
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

if __name__ == '__main__':
    main()

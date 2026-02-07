#!/usr/bin/env python3
"""
DoScript Interpreter v0.5

Features:
- script_path add/remove/list (internal resolution)
- include "file.do" with recursion protection
- functions and macros (make a_command)
- for_each <var>_in "<pattern>" (glob) and literal lists
- for_each_line <var> in "file"
- if_ends_with "<suffix>" (implicit loop var)
- if ends_with <expr> "<suffix>" (explicit)
- builtins including extension(), endswith(), startswith(), split(), read_file(), etc.
- file/network/process operations
- try/catch
- variable scoping with global_variable/local_variable
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
# Exceptions
# ----------------------------
class DoScriptError(Exception):
    pass

class NetworkError(DoScriptError):
    pass

class FileError(DoScriptError):
    pass

class ProcessError(DoScriptError):
    pass

# ----------------------------
# Interpreter
# ----------------------------
class DoScriptInterpreter:
    def __init__(self):
        # internal script path stack (LIFO)
        self.script_path_stack: List[str] = []
        # variables
        self.global_vars: Dict[str, Any] = {}
        self.declared_globals: set = set()
        # functions & macros
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.macros: Dict[str, List[str]] = {}
        # local scope for functions
        self.local_scope: Optional[Dict[str, Any]] = None
        # included files tracker
        self.included_files: set = set()
        # loop variable stack: stores variable name for each nested for_each
        self.loop_var_stack: List[str] = []

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
    # String interpolation
    # ----------------------------
    def interpolate_string(self, s: str) -> str:
        # Replace escaped braces first
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
    # Variables
    # ----------------------------
    def get_variable(self, name: str) -> Any:
        if self.local_scope is not None and name in self.local_scope:
            return self.local_scope[name]
        if name in self.global_vars:
            return self.global_vars[name]
        raise DoScriptError(f"Variable '{name}' is not defined")

    def set_variable(self, name: str, value: Any):
        if self.local_scope is not None and name in self.local_scope:
            self.local_scope[name] = value
        elif name in self.declared_globals:
            self.global_vars[name] = value
        else:
            raise DoScriptError(f"Variable '{name}' used before declaration")

    # ----------------------------
    # Expression evaluation (safe)
    # ----------------------------
    def evaluate_expression(self, expr: str) -> Any:
        expr = expr.strip()
        if not expr:
            return ""

        # String literal (double-quoted -> escapes)
        if (expr.startswith('"') and expr.endswith('"')) and len(expr) >= 2:
            inner = expr[1:-1]
            try:
                return bytes(inner, "utf-8").decode("unicode_escape")
            except Exception:
                return inner

        # Single-quoted -> interpolate
        if (expr.startswith("'") and expr.endswith("'")) and len(expr) >= 2:
            return self.interpolate_string(expr[1:-1])

        # Booleans
        if expr == 'true':
            return True
        if expr == 'false':
            return False

        # Numbers
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass

        # Function call pattern
        func_call_match = re.match(r'^(\w+)\((.*)\)$', expr)
        if func_call_match:
            fname = func_call_match.group(1)
            args_str = func_call_match.group(2).strip()
            args = [a.strip() for a in self._split_args(args_str)] if args_str else []

            # Builtins
            if fname == 'exists':
                if args:
                    path_arg = self.evaluate_expression(args[0])
                    return os.path.exists(self.resolve_path(str(path_arg)))
                return False
            if fname == 'date':
                from datetime import datetime
                return datetime.now().strftime('%Y-%m-%d')
            if fname == 'time':
                from datetime import datetime
                return datetime.now().strftime('%H:%M:%S')
            if fname == 'datetime':
                from datetime import datetime
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if fname == 'extension':
                if args:
                    val = self.evaluate_expression(args[0])
                    return os.path.splitext(str(val))[1]
                return ""
            if fname == 'substring':
                vals = [self.evaluate_expression(a) for a in args]
                if len(vals) >= 3:
                    return str(vals[0])[int(vals[1]):int(vals[1])+int(vals[2])]
                if len(vals) == 2:
                    return str(vals[0])[int(vals[1]):]
                return ""
            if fname == 'replace':
                vals = [self.evaluate_expression(a) for a in args]
                if len(vals) >= 3:
                    return str(vals[0]).replace(str(vals[1]), str(vals[2]))
                return ""
            if fname == 'length':
                if args:
                    return len(str(self.evaluate_expression(args[0])))
                return 0
            if fname == 'uppercase':
                if args:
                    return str(self.evaluate_expression(args[0])).upper()
                return ""
            if fname == 'lowercase':
                if args:
                    return str(self.evaluate_expression(args[0])).lower()
                return ""
            if fname == 'trim':
                if args:
                    return str(self.evaluate_expression(args[0])).strip()
                return ""
            if fname == 'contains':
                vals = [self.evaluate_expression(a) for a in args]
                if len(vals) >= 2:
                    return str(vals[1]) in str(vals[0])
                return False
            if fname == 'startswith':
                vals = [self.evaluate_expression(a) for a in args]
                if len(vals) >= 2:
                    return str(vals[0]).startswith(str(vals[1]))
                return False
            if fname == 'endswith':
                vals = [self.evaluate_expression(a) for a in args]
                if len(vals) >= 2:
                    return str(vals[0]).endswith(str(vals[1]))
                return False
            if fname == 'split':
                vals = [self.evaluate_expression(a) for a in args]
                if len(vals) >= 2:
                    return str(vals[0]).split(str(vals[1]))
                if len(vals) == 1:
                    return str(vals[0]).split()
                return []
            if fname == 'read_file':
                if args:
                    p = self.resolve_path(str(self.evaluate_expression(args[0])))
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        raise FileError(f"Failed to read file '{p}': {e}")
                return ""

            # user-defined function
            if fname in self.functions:
                evaluated_args = [self.evaluate_expression(a) for a in args]
                return self.call_function(fname, evaluated_args)

            raise DoScriptError(f"Unknown function: {fname}")

        # 'exists "path"' shorthand
        exists_match = re.match(r'^exists\s+"([^"]+)"$', expr)
        if exists_match:
            path = exists_match.group(1)
            return os.path.exists(self.resolve_path(path))

        # variable by name
        if re.match(r'^\w+$', expr):
            return self.get_variable(expr)

        # safe AST evaluation
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
            raise DoScriptError(f"Failed to evaluate expression '{expr}': {e}")

    def _split_args(self, args_str: str) -> List[str]:
        if not args_str:
            return []
        parts = []
        cur = ''
        in_double = False
        in_single = False
        i = 0
        while i < len(args_str):
            c = args_str[i]
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

    def _eval_node(self, node, namespace):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in namespace:
                return namespace[node.id]
            raise DoScriptError(f"Variable '{node.id}' not found")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, namespace)
            right = self._eval_node(node.right, namespace)
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Mod: operator.mod,
            }
            if type(node.op) in ops:
                return ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, namespace)
            if isinstance(node.op, ast.Not):
                return not operand
            elif isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, namespace)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, namespace)
                if isinstance(op, ast.Eq):
                    if not (left == right):
                        return False
                elif isinstance(op, ast.NotEq):
                    if not (left != right):
                        return False
                elif isinstance(op, ast.Lt):
                    if not (left < right):
                        return False
                elif isinstance(op, ast.Gt):
                    if not (left > right):
                        return False
                elif isinstance(op, ast.LtE):
                    if not (left <= right):
                        return False
                elif isinstance(op, ast.GtE):
                    if not (left >= right):
                        return False
                left = right
            return True
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for value in node.values:
                    result = result and self._eval_node(value, namespace)
                    if not result:
                        return False
                return True
            elif isinstance(node.op, ast.Or):
                result = False
                for value in node.values:
                    result = result or self._eval_node(value, namespace)
                    if result:
                        return True
                return False
        raise DoScriptError(f"Unsupported expression type: {type(node).__name__}")

    # ----------------------------
    # Function call
    # ----------------------------
    def call_function(self, name: str, args: List[Any]) -> Any:
        if name not in self.functions:
            raise DoScriptError(f"Function '{name}' not defined")
        func = self.functions[name]
        params = func['params']
        body = func['body']
        old_local = self.local_scope
        self.local_scope = {}
        for i, p in enumerate(params):
            self.local_scope[p] = args[i] if i < len(args) else None
        return_value = None
        try:
            for stmt in body:
                result = self.execute_statement(stmt)
                if result is not None and result[0] == 'return':
                    return_value = result[1]
                    break
                if result is not None and result[0] in ('break', 'continue'):
                    raise DoScriptError(f"'{result[0]}' not allowed inside function")
        finally:
            self.local_scope = old_local
        return return_value

    # ----------------------------
    # Parsing
    # ----------------------------
    def parse_script(self, filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        statements: List[str] = []
        current_line = ""
        for line in lines:
            # remove comments
            line = re.sub(r'#.*$', '', line)
            line = re.sub(r'//.*$', '', line)
            line = line.rstrip('\n\r')
            stripped = line.strip()
            if stripped:
                current_line += (" " + stripped) if current_line else stripped
                # treat line-oriented statements
                statements.append(current_line)
                current_line = ""
        return statements

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
        raise DoScriptError(f"Missing {end_keyword}")

    # ----------------------------
    # Execute single statement (commands, assignments, small control)
    # Returns None or tuple like ('return', value) / ('break', None) / ('continue', None)
    # ----------------------------
    def execute_statement(self, stmt: str) -> Optional[Tuple[str, Any]]:
        stmt = stmt.strip()
        if not stmt:
            return None

        # script_path
        if stmt.startswith('script_path add '):
            path = self.extract_string(stmt[16:])
            self.script_path_stack.append(os.path.abspath(path))
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

        # compatibility alias for old 'path' (warn)
        if stmt.startswith('path add '):
            print("Warning: 'path' is deprecated. Use 'script_path add'.", file=sys.stderr)
            path = self.extract_string(stmt[9:])
            self.script_path_stack.append(os.path.abspath(path))
            return None
        if stmt.startswith('path remove '):
            print("Warning: 'path' is deprecated. Use 'script_path remove'.", file=sys.stderr)
            path = self.extract_string(stmt[12:])
            rp = os.path.abspath(path)
            if rp in self.script_path_stack:
                self.script_path_stack.remove(rp)
            return None
        if stmt == 'path list':
            print("Warning: 'path' is deprecated. Use 'script_path list'.", file=sys.stderr)
            for p in self.script_path_stack:
                print(p)
            return None

        # include
        if stmt.startswith('include '):
            file_expr = stmt[8:].strip()
            file_path = self.extract_string(file_expr)
            resolved = os.path.abspath(self.resolve_path(file_path))
            if resolved in self.included_files:
                return None
            if not os.path.exists(resolved):
                raise FileError(f"Included file not found: '{file_path}'")
            self.included_files.add(resolved)
            lines = self.parse_script(resolved)
            self.execute_lines(lines)
            return None

        # make folder
        if stmt.startswith('make folder '):
            path = self.extract_string(stmt[12:])
            resolved = os.path.abspath(self.resolve_path(path))
            try:
                os.makedirs(resolved, exist_ok=True)
            except Exception as e:
                raise FileError(f"Failed to create folder '{path}': {e}")
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
                try:
                    os.makedirs(os.path.dirname(resolved), exist_ok=True)
                    with open(resolved, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    raise FileError(f"Failed to create file '{path}': {e}")
            return None

        # copy
        if ' to ' in stmt and stmt.startswith('copy '):
            m = re.match(r'copy "([^"]+)" to "([^"]+)"$', stmt)
            if m:
                src, dst = m.groups()
                src_resolved = os.path.abspath(self.resolve_path(src))
                dst_resolved = os.path.abspath(self.resolve_path(dst))
                try:
                    os.makedirs(os.path.dirname(dst_resolved), exist_ok=True)
                    shutil.copy2(src_resolved, dst_resolved)
                except Exception as e:
                    raise FileError(f"Failed to copy '{src}' to '{dst}': {e}")
            return None

        # move
        if ' to ' in stmt and stmt.startswith('move '):
            # support: move file to "exe/{file}"  OR move "C:/a.txt" to "b.txt"
            m = re.match(r'move\s+(.+)\s+to\s+(.+)$', stmt)
            if m:
                src_tok = m.group(1).strip()
                dst_tok = m.group(2).strip()
                # evaluate src
                if (src_tok.startswith('"') and src_tok.endswith('"')) or (src_tok.startswith("'") and src_tok.endswith("'")):
                    src_path = self.extract_string(src_tok)
                else:
                    # treat as variable name
                    src_path = self.evaluate_expression(src_tok) if re.match(r'^["\']', src_tok) else self.get_variable(src_tok)
                # destination: extract and interpolate
                dst_raw = self.extract_string(dst_tok)
                dst_interp = self.interpolate_if_needed(dst_raw)
                src_resolved = os.path.abspath(self.resolve_path(str(src_path)))
                dst_resolved = os.path.abspath(self.resolve_path(dst_interp))
                try:
                    os.makedirs(os.path.dirname(dst_resolved), exist_ok=True)
                    shutil.move(src_resolved, dst_resolved)
                except Exception as e:
                    raise FileError(f"Failed to move '{src_path}' to '{dst_interp}': {e}")
            return None

        # delete
        if stmt.startswith('delete '):
            path_expr = stmt[7:].strip()
            if (path_expr.startswith('"') and path_expr.endswith('"')) or (path_expr.startswith("'") and path_expr.endswith("'")):
                path = self.extract_string(path_expr)
            else:
                path = str(self.evaluate_expression(path_expr))
            resolved = os.path.abspath(self.resolve_path(path))
            try:
                if os.path.isdir(resolved):
                    shutil.rmtree(resolved)
                else:
                    os.remove(resolved)
            except Exception as e:
                raise FileError(f"Failed to delete '{path}': {e}")
            return None

        # download
        if stmt.startswith('download ') and ' to ' in stmt:
            m = re.match(r'download\s+"([^"]+)"\s+to\s+"([^"]+)"$', stmt)
            if m:
                url, path = m.groups()
                resolved = os.path.abspath(self.resolve_path(path))
                try:
                    os.makedirs(os.path.dirname(resolved), exist_ok=True)
                    urllib.request.urlretrieve(url, resolved)
                except Exception as e:
                    raise NetworkError(f"Failed to download '{url}': {e}")
            return None

        # upload
        if stmt.startswith('upload ') and ' to ' in stmt:
            m = re.match(r'upload\s+"([^"]+)"\s+to\s+"([^"]+)"$', stmt)
            if m:
                path, url = m.groups()
                resolved = os.path.abspath(self.resolve_path(path))
                try:
                    with open(resolved, 'rb') as f:
                        data = f.read()
                    req = urllib.request.Request(url, data=data, method='POST')
                    urllib.request.urlopen(req)
                except Exception as e:
                    raise NetworkError(f"Failed to upload '{path}': {e}")
            return None

        # ping
        if stmt.startswith('ping '):
            host = self.extract_string(stmt[5:])
            try:
                if sys.platform == 'win32':
                    subprocess.run(['ping', '-n', '1', host], check=True)
                else:
                    subprocess.run(['ping', '-c', '1', host], check=True)
            except Exception as e:
                raise NetworkError(f"Failed to ping '{host}': {e}")
            return None

        # run (macro or shell)
        if stmt.startswith('run '):
            token = stmt[4:].strip()
            name = self.extract_string(token)
            if name in self.macros:
                for s in self.macros[name]:
                    self.execute_statement(s)
                return None
            else:
                try:
                    subprocess.run(name, shell=True, check=False)
                except Exception as e:
                    raise ProcessError(f"Failed to run '{name}': {e}")
                return None

        # capture
        if stmt.startswith('capture '):
            token = stmt[8:].strip()
            name = self.extract_string(token)
            try:
                result = subprocess.run(name, shell=True, capture_output=True, text=True)
                return ('capture_output', result.stdout.strip())
            except Exception as e:
                raise ProcessError(f"Failed to capture '{name}': {e}")

        # exit
        if stmt.startswith('exit'):
            if stmt == 'exit':
                sys.exit(0)
            else:
                code_expr = stmt[4:].strip()
                code = int(self.evaluate_expression(code_expr))
                sys.exit(code)

        # break / continue for loops
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
            except Exception as e:
                raise ProcessError(f"Failed to kill '{proc_name}': {e}")
            return None

        # say
        if stmt.startswith('say '):
            expr = stmt[4:].strip()
            val = self.evaluate_expression(expr)
            print(val)
            return None

        # ask
        if stmt.startswith('ask '):
            m = re.match(r'ask\s+(\w+)\s+(.+)$', stmt)
            if m:
                var_name = m.group(1)
                prompt_expr = m.group(2).strip()
                prompt = str(self.evaluate_expression(prompt_expr))
                ans = input(prompt + " ")
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

        # local_variable (only inside functions)
        if stmt.startswith('local_variable = '):
            if self.local_scope is None:
                raise DoScriptError("local_variable can only be used inside functions")
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

        # Assignment and special RHS handling
        if '=' in stmt and not stmt.startswith(('if ', 'repeat ', 'loop ', 'for_each ', 'for_each_line ')):
            m = re.match(r'^(\w+)\s*=\s*(.+)$', stmt)
            if m:
                var_name = m.group(1)
                rhs = m.group(2).strip()
                # run/capture special
                if rhs.startswith('run '):
                    res = self.execute_statement(rhs)
                    if res and res[0] == 'exit_code':
                        self.set_variable(var_name, res[1])
                    else:
                        self.set_variable(var_name, 0)
                elif rhs.startswith('capture '):
                    res = self.execute_statement(rhs)
                    if res and res[0] == 'capture_output':
                        self.set_variable(var_name, res[1])
                    else:
                        self.set_variable(var_name, "")
                else:
                    val = self.evaluate_expression(rhs)
                    self.set_variable(var_name, val)
            return None

        # If none matched: no-op
        return None

    # ----------------------------
    # Block execution (handles constructs)
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
        raise DoScriptError(f"Missing {end_keyword}")

    # ----------------------------
    # Top-level lines execution (supports nested blocks)
    # ----------------------------
    def execute_lines(self, lines: List[str], start_idx: int = 0, end_idx: Optional[int] = None):
        if end_idx is None:
            end_idx = len(lines)
        i = start_idx
        while i < end_idx:
            stmt = lines[i].strip()

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

            # macro def: make a_command NAME
            if stmt.startswith('make a_command '):
                name = stmt[14:].strip()
                end_i, body = self.execute_block(lines, i + 1, 'end_command')
                self.macros[name] = body
                i = end_i + 1
                continue
            # backward-compat: "make a command" (deprecated)
            if stmt.startswith('make a command '):
                print("Warning: 'make a command' is deprecated. Use 'make a_command'.", file=sys.stderr)
                name = stmt[15:].strip()
                end_i, body = self.execute_block(lines, i + 1, 'end_command')
                self.macros[name] = body
                i = end_i + 1
                continue

            # IF (normal explicit expression)
            if stmt.startswith('if '):
                cond_expr = stmt[3:].strip()
                # special explicit sugar: ends_with <expr> "suffix"
                m = re.match(r'ends_with\s+(.+?)\s+("([^"]+)"|\'([^\']+)\')\s*$', cond_expr)
                if m:
                    left_expr = m.group(1).strip()
                    suffix = m.group(3) if m.group(3) is not None else m.group(4)
                    cond = self.evaluate_expression(f'endswith({left_expr}, "{suffix}")')
                else:
                    cond = self.evaluate_expression(cond_expr)

                # find else and end_if
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
                    raise DoScriptError("Missing end_if")
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

            # REPEAT
            if stmt.startswith('repeat '):
                count_expr = stmt[7:].strip()
                count = int(self.evaluate_expression(count_expr))
                end_i, body = self.execute_block(lines, i + 1, 'end_repeat')
                for _ in range(count):
                    res = self.execute_lines(body, 0, len(body))
                    if res and res[0] == 'break':
                        break
                    if res and res[0] == 'continue':
                        continue
                i = end_i + 1
                continue

            # LOOP
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
                        if res and res[0] == 'continue':
                            continue
                i = end_i + 1
                continue

            # TRY/CATCH
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

            # FOR_EACH - two syntaxes:
            # 1) for_each var_in "pattern"
            # 2) for_each var in "a", "b", "c"  (literal list)
            if stmt.startswith('for_each ') and ('_in ' in stmt or ' in ' in stmt):
                # Decide syntax
                m_var_in = re.match(r'for_each\s+(\w+)_in\s+(.+)$', stmt)
                m_var_list = None
                if not m_var_in:
                    m_var_list = re.match(r'for_each\s+(\w+)\s+in\s+(.+)$', stmt)
                if m_var_in:
                    var_name = m_var_in.group(1)
                    pattern_token = m_var_in.group(2).strip()
                    # pattern may be quoted or an expression
                    if (pattern_token.startswith('"') and pattern_token.endswith('"')) or (pattern_token.startswith("'") and pattern_token.endswith("'")):
                        pattern = self.extract_string(pattern_token)
                    else:
                        pattern = str(self.evaluate_expression(pattern_token))
                    resolved_pattern = self.resolve_path(pattern)
                    matched_files = glob.glob(resolved_pattern)
                    # ensure declared
                    if var_name not in self.declared_globals:
                        self.declared_globals.add(var_name)
                        self.global_vars[var_name] = None
                    # extract body
                    end_i, body = self.execute_block(lines, i + 1, 'end_for')
                    # push loop var for implicit if_ends_with
                    self.loop_var_stack.append(var_name)
                    try:
                        for full_path in matched_files:
                            # set variable to basename by default
                            self.set_variable(var_name, os.path.basename(full_path))
                            # execute body with special handling for if_ends_with
                            j = 0
                            while j < len(body):
                                line = body[j].strip()
                                # handle if_ends_with "<suffix>"
                                if line.startswith('if_ends_with '):
                                    suffix_tok = line[len('if_ends_with '):].strip()
                                    suffix = self.extract_string(suffix_tok)
                                    current_var = self.loop_var_stack[-1] if self.loop_var_stack else None
                                    if current_var is None:
                                        raise DoScriptError("if_ends_with used outside a for_each")
                                    val = self.get_variable(current_var)
                                    cond = str(val).endswith(suffix)
                                    # gather inner until end_if
                                    inner = []
                                    k = j + 1
                                    while k < len(body):
                                        if body[k].strip() == 'end_if':
                                            break
                                        inner.append(body[k])
                                        k += 1
                                    if k >= len(body):
                                        raise DoScriptError("Missing end_if in if_ends_with block")
                                    if cond:
                                        self.execute_lines(inner)
                                    j = k + 1
                                    continue
                                # normal statement
                                res = self.execute_statement(line)
                                if res is not None and res[0] in ('break', 'continue', 'return'):
                                    if res[0] == 'break':
                                        # break out of file iteration
                                        j = len(body)
                                        break
                                    if res[0] == 'continue':
                                        break
                                    if res[0] == 'return':
                                        return res
                                j += 1
                    finally:
                        self.loop_var_stack.pop()
                    i = end_i + 1
                    continue
                elif m_var_list:
                    var_name = m_var_list.group(1)
                    list_expr = m_var_list.group(2).strip()
                    # split on commas while respecting quotes
                    items = []
                    parts = self._split_args(list_expr)
                    for p in parts:
                        items.append(self.evaluate_expression(p))
                    # ensure declared
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
                        raise FileError(f"Failed to read file '{file_str}': {e}")
                    i = end_i + 1
                    continue

            # run / other statements handled by execute_statement
            res = self.execute_statement(stmt)
            if res is not None:
                if res[0] in ('return', 'break', 'continue'):
                    return res
            i += 1

    # ----------------------------
    # Public runner
    # ----------------------------
    def run(self, filename: str):
        if not os.path.exists(filename):
            raise FileError(f"Script file not found: {filename}")
        # push script dir into script_path so includes resolve
        script_dir = os.path.abspath(os.path.dirname(filename))
        self.script_path_stack.append(script_dir)
        try:
            lines = self.parse_script(filename)
            self.execute_lines(lines)
        finally:
            if self.script_path_stack and self.script_path_stack[-1] == script_dir:
                self.script_path_stack.pop()

    # ----------------------------
    # Helpers
    # ----------------------------
    def parse_script(self, filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            raw = f.readlines()
        out: List[str] = []
        cur = ""
        for line in raw:
            line = re.sub(r'#.*$', '', line)
            line = re.sub(r'//.*$', '', line)
            line = line.rstrip('\n\r')
            t = line.strip()
            if t:
                cur += (" " + t) if cur else t
                out.append(cur)
                cur = ""
        return out

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

# ----------------------------
# CLI
# ----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python doscript_v0_5.py <script.do>")
        sys.exit(1)
    script = sys.argv[1]
    interp = DoScriptInterpreter()
    try:
        interp.run(script)
    except DoScriptError as e:
        print(f"DoScript Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nScript interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

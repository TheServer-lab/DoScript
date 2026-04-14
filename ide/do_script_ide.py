# Save as doscript_ide_fixed.py and run with python
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import re
import sys

APP_TITLE = "DoScript IDE"
# The IDE will always use the configured command below. No automatic check for /mnt/data/doscript.py
DOSCRIPT_CMD = "doscript"

# Keywords for completion/highlighting
KEYWORDS = [
    'function','end_function','if','else','end_if','loop','end_loop','repeat','end_repeat',
    'for_each','end_for','for_each_line','make','include','run','capture','say','ask','pause','wait','return','break','continue',
    'global_variable','local_variable','script_path','path','copy','move','delete','ping','kill','log','warn','error',
    'true','false'
]

class DoScriptIDE:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1000x700")

        self.file_path = None

        self.create_menu()
        self.create_editor()
        # console removed
        self.bind_events()

        # Completion UI
        self.completion_box = tk.Listbox(self.root, height=8)
        self.completion_box.bind('<Double-Button-1>', self._insert_completion)
        self.completion_box.bind('<Return>', self._insert_completion)
        self.completion_box.bind('<<ListboxSelect>>', self._on_completion_select)

        # Tooltip window for signatures
        self.sig_win = None

        # Keep last error highlighted
        self._last_error_line = None

    # ---------------- MENU ----------------
    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Run DoScript", command=self.run_doscript)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Run", menu=run_menu)

        self.root.config(menu=menu_bar)

    # ---------------- EDITOR ----------------
    def create_editor(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        # gutter
        self.gutter = tk.Text(frame, width=5, padx=4, takefocus=0, border=0,
                              state='disabled', bg='#202225', fg='#8e9297', font=('Consolas', 11))
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)

        self.editor = scrolledtext.ScrolledText(
            frame,
            wrap=tk.NONE,
            font=("Consolas", 12),
            undo=True,
            bg='#36393f', fg='#dcddde', insertbackground='#ffffff'
        )
        self.editor.pack(fill=tk.BOTH, expand=True)

        # highlighting tags
        self.editor.tag_config('kw', foreground='#ffcc66')
        self.editor.tag_config('str', foreground='#a3be8c')
        self.editor.tag_config('cmt', foreground='#7f8c8d')
        self.editor.tag_config('num', foreground='#b294bb')
        self.editor.tag_config('err', background='#5b1e1e')

    # ---------------- EVENTS ----------------
    def bind_events(self):
        self.editor.bind('<KeyRelease>', self.on_key_release)
        self.editor.bind('<Return>', self.on_return)
        # Tab will complete selection if completion box visible, otherwise insert 4 spaces
        self.editor.bind('<Tab>', self.on_tab_key)
        self.editor.bind('<Control-space>', self.show_completions)
        self.editor.bind('<Key>', self._on_key)
        # Open suggestions with Down arrow
        self.editor.bind('<Down>', self._on_down_key)
        self.editor.bind('<Up>', self._on_up_key)
        self.gutter.bind('<Button-1>', lambda e: None)
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        # update gutter periodically
        self.root.after(200, self._update_gutter)

    def _on_key(self, event):
        # Do NOT auto-show completions while typing.
        # If completion box is visible, allow navigation keys to operate it.
        try:
            if self.completion_box.winfo_ismapped():
                if event.keysym == 'Down':
                    self._move_completion(1)
                    return 'break'
                if event.keysym == 'Up':
                    self._move_completion(-1)
                    return 'break'
                if event.keysym in ('Return', 'Tab'):
                    self._insert_completion()
                    return 'break'
                # other keys should allow typing — do not auto-refresh the list
                return
        except Exception:
            # if completion box not initialized or other error, ignore
            return

    def _on_down_key(self, event=None):
        # If completion visible, move selection; else open suggestions menu
        if self.completion_box.winfo_ismapped():
            self._move_completion(1)
            return 'break'
        tok = self._get_current_token()
        self._show_inline_completions(tok or '')
        # ensure first item selected
        try:
            self.completion_box.selection_clear(0, tk.END)
            self.completion_box.selection_set(0)
            self.completion_box.activate(0)
            self.completion_box.focus_set()
        except Exception:
            pass
        return 'break'

    def _on_up_key(self, event=None):
        if self.completion_box.winfo_ismapped():
            self._move_completion(-1)
            return 'break'
        return

    def _move_completion(self, delta):
        try:
            cur = self.completion_box.curselection()
            if not cur:
                idx = 0 if delta > 0 else max(0, self.completion_box.size()-1)
            else:
                idx = max(0, min(self.completion_box.size()-1, cur[0] + delta))
            self.completion_box.selection_clear(0, tk.END)
            self.completion_box.selection_set(idx)
            self.completion_box.activate(idx)
            self.completion_box.see(idx)
        except Exception:
            pass

    def on_key_release(self, event=None):
        self.highlight_syntax()

    def on_return(self, event=None):
        # simple auto-indent
        idx = self.editor.index('insert').split('.')
        line = int(idx[0])
        cur_line = self.editor.get(f'{line}.0', f'{line}.end')
        m = re.match(r'^(\s*)', cur_line)
        indent = m.group(1) if m else ''
        block_keywords = ('if ', 'function ', 'loop ', 'repeat ', 'for_each ')
        extra = ''
        if cur_line.strip():
            for bk in block_keywords:
                if cur_line.strip().startswith(bk):
                    extra = '    '
                    break
        self.editor.insert('insert', '\n' + indent + extra)
        return 'break'

    def on_tab_key(self, event=None):
        # If completion visible, accept selected item
        if self.completion_box.winfo_ismapped():
            self._insert_completion()
            return 'break'
        # otherwise insert tab spaces
        self.editor.insert('insert', '    ')
        return 'break'

    # ---------------- GUTTER ----------------
    def _update_gutter(self):
        try:
            self.gutter.config(state='normal')
            self.gutter.delete('1.0', tk.END)
            line_count = int(self.editor.index('end-1c').split('.')[0])
            s = ''
            for i in range(1, line_count + 1):
                s += f"{i:>3}\n"
            self.gutter.insert('1.0', s)
            self.gutter.config(state='disabled')
        except Exception:
            pass
        self.root.after(200, self._update_gutter)

    # ---------------- SYNTAX HIGHLIGHTING ----------------
    def highlight_syntax(self):
        text = self.editor.get('1.0', tk.END)
        # clear tags except selection
        for tag in self.editor.tag_names():
            if tag != 'sel':
                self.editor.tag_remove(tag, '1.0', tk.END)
        # keywords
        for kw in KEYWORDS:
            for m in re.finditer(r'\b' + re.escape(kw) + r'\b', text):
                start = self._index_from_pos(m.start())
                end = self._index_from_pos(m.end())
                self.editor.tag_add('kw', start, end)
        # strings
        for m in re.finditer(r'".*?"|\'.*?\'', text, re.DOTALL):
            start = self._index_from_pos(m.start())
            end = self._index_from_pos(m.end())
            self.editor.tag_add('str', start, end)
        # comments (# or //)
        for m in re.finditer(r'(#.*?$|//.*?$)', text, re.MULTILINE):
            start = self._index_from_pos(m.start())
            end = self._index_from_pos(m.end())
            self.editor.tag_add('cmt', start, end)
        # numbers
        for m in re.finditer(r'\b\d+(?:\.\d+)?\b', text):
            start = self._index_from_pos(m.start())
            end = self._index_from_pos(m.end())
            self.editor.tag_add('num', start, end)

    def _index_from_pos(self, pos):
        return '1.0 + %dc' % pos

    # ---------------- COMPLETION ----------------
    def show_completions(self, event=None):
        tok = self._get_current_token()
        self._show_inline_completions(tok or '')

    def _get_current_token(self):
        idx = self.editor.index('insert')
        line, col = map(int, idx.split('.'))
        line_text = self.editor.get(f'{line}.0', f'{line}.end')
        left = line_text[:col]
        m = re.search(r"([A-Za-z0-9_]+)$", left)
        return m.group(1) if m else ''

    def _collect_candidates(self):
        words = set(KEYWORDS)
        text = self.editor.get('1.0', tk.END)
        for m in re.finditer(r'^function\s+(\w+)', text, re.MULTILINE):
            words.add(m.group(1))
        return sorted(words)

    def _fuzzy_score(self, query, word):
        # improved fuzzy scoring:
        q = query.lower()
        w = word.lower()
        if not q:
            return 1
        # exact start = best
        if w.startswith(q):
            return 1000 - (len(w) - len(q))
        # exact substring
        if q in w:
            return 700 - (len(w) - len(q))
        # subsequence scoring with gap penalty
        qi = 0
        score = 0
        gaps = 0
        for ch in w:
            if qi < len(q) and ch == q[qi]:
                qi += 1
                score += 10
            else:
                gaps += 1
        if qi == len(q):
            # reward shorter words
            return score - gaps
        return 0

    def _show_inline_completions(self, token):
        candidates = self._collect_candidates()
        scored = []
        for w in candidates:
            s = self._fuzzy_score(token, w)
            if s > 0:
                scored.append((s, w))
        if not scored:
            self._hide_completion()
            return
        scored.sort(key=lambda x: (-x[0], x[1]))
        self.completion_box.delete(0, tk.END)
        for _, w in scored[:40]:
            self.completion_box.insert(tk.END, w)
        # position listbox near cursor
        try:
            bbox = self.editor.bbox('insert')
            if bbox:
                x, y, w, h = bbox
                px = self.editor.winfo_rootx() + x
                py = self.editor.winfo_rooty() + y + h
                self.completion_box.place(x=px - self.root.winfo_rootx(), y=py - self.root.winfo_rooty())
            else:
                self.completion_box.place(x=100, y=100)
        except Exception:
            self.completion_box.place(x=100, y=100)
        self.completion_box.lift()
        self.completion_box.focus_set()
        # pre-select first item
        try:
            self.completion_box.selection_set(0)
        except Exception:
            pass

    def _hide_completion(self):
        try:
            self.completion_box.place_forget()
        except Exception:
            pass
        self._hide_signature()

    def _insert_completion(self, event=None):
        try:
            sel = self.completion_box.get(tk.ACTIVE)
        except Exception:
            sel = None
        if not sel:
            # nothing selected; hide
            self._hide_completion()
            return
        # delete current token
        token = self._get_current_token()
        if token:
            idx = self.editor.index('insert')
            line, col = map(int, idx.split('.'))
            start = f'{line}.{col - len(token)}'
            self.editor.delete(start, idx)
        self.editor.insert('insert', sel)
        self._hide_completion()
        self.editor.focus_set()

    def _on_completion_select(self, event=None):
        # show signature tooltip for selected item
        try:
            sel = self.completion_box.get(self.completion_box.curselection())
        except Exception:
            sel = None
        if not sel:
            self._hide_signature()
            return
        sig = self._get_signature(sel)
        if sig:
            self._show_signature(sig)
        else:
            self._hide_signature()

    # ---------------- SIGNATURE PARSING / TOOLTIP ----------------
    def _parse_functions(self):
        # return dict name -> signature string (if found)
        text = self.editor.get('1.0', tk.END)
        funcs = {}
        # look for lines like: function name(params)  OR function name
        for m in re.finditer(r'^function\s+(\w+)(?:\s*\(([^)]*)\))?', text, re.MULTILINE):
            name = m.group(1)
            params = m.group(2) or ''
            params = params.strip()
            funcs[name] = f'{name}({params})' if params != '' else f'{name}()'
        # also try to capture a comment line immediately above function as a short doc
        for m in re.finditer(r'(^#.*\n)?^function\s+(\w+)', text, flags=re.MULTILINE):
            doc = m.group(1).strip() if m.group(1) else None
            name = m.group(2)
            if doc:
                # attach doc to signature if available
                sig = funcs.get(name, f'{name}()')
                funcs[name] = f'{sig} - {doc.lstrip('#').strip()}'
        return funcs

    def _get_signature(self, name):
        funcs = self._parse_functions()
        return funcs.get(name)

    def _show_signature(self, text):
        self._hide_signature()
        try:
            bbox = self.editor.bbox('insert')
            if bbox:
                x, y, w, h = bbox
                px = self.editor.winfo_rootx() + x
                py = self.editor.winfo_rooty() + y - 30
            else:
                px = self.root.winfo_rootx() + 100
                py = self.root.winfo_rooty() + 100
            self.sig_win = tk.Toplevel(self.root)
            self.sig_win.wm_overrideredirect(True)
            self.sig_win.attributes('-topmost', True)
            lbl = tk.Label(self.sig_win, text=text, bg='#1f2326', fg='#ffffff', font=('Consolas', 10), bd=1, relief='solid')
            lbl.pack()
            self.sig_win.geometry(f'+{px}+{py}')
        except Exception:
            pass

    def _hide_signature(self):
        try:
            if self.sig_win:
                self.sig_win.destroy()
        except Exception:
            pass
        self.sig_win = None

    # ---------------- RUN + ERROR PARSING ----------------
    def run_doscript(self):
        if not self.file_path:
            messagebox.showwarning("No file", "Please save the file before running.")
            return

        self.append_console(f"> Running: {self.file_path}\n")

        # always use configured DOSCRIPT_CMD (no automatic interpreter check)
        cmd = [DOSCRIPT_CMD, self.file_path]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=False
            )

            if result.stdout:
                self.append_console(result.stdout)
            if result.stderr:
                self.append_console(result.stderr)
                self._try_parse_error(result.stderr)

        except Exception as e:
            self.append_console(f"Error: {e}\n")

    def _try_parse_error(self, stderr_text):
        # matches patterns like: in /path/to/file:123 or File "path", line 123
        m = re.search(r"in\s+(?P<file>[^:\n\s]+):(\s?)(?P<line>\d+)", stderr_text)
        if not m:
            m = re.search(r'File\s+"(?P<file>[^"]+)",\s+line\s+(?P<line>\d+)', stderr_text)
            if not m:
                return
        file = m.group('file').strip()
        line = int(m.group('line'))
        if not self.file_path:
            return
        try:
            if os.path.abspath(file) == os.path.abspath(self.file_path):
                self._highlight_error_line(line)
                self._update_status(f'Error at line {line}')
        except Exception:
            pass

    def _highlight_error_line(self, line):
        # remove existing error tag
        if self._last_error_line:
            try:
                self.editor.tag_remove('err', f'{self._last_error_line}.0', f'{self._last_error_line}.end')
            except Exception:
                pass
        start = f"{line}.0"
        end = f"{line}.end"
        self.editor.tag_add('err', start, end)
        self.editor.see(start)
        self._last_error_line = line

    # ---------------- HELPERS ----------------
    def append_console(self, text):
        # Console UI removed — use popups for important messages
        if not text:
            return
        lower = text.lower()
        if 'error' in lower or 'traceback' in lower:
            messagebox.showerror("DoScript", text)
        else:
            # for long outputs, write to a temporary file and notify user
            if len(text) > 1000:
                import tempfile
                tf = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
                tf.write(text)
                tf.close()
                messagebox.showinfo("DoScript Output", f"Output written to {tf.name}")
            else:
                messagebox.showinfo("DoScript Output", text)

    def new_file(self):
        if self.confirm_discard_changes():
            self.editor.delete("1.0", tk.END)
            self.file_path = None
            self.root.title(APP_TITLE)

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("DoScript Files", "*.do"), ("All Files", "*.*")]
        )
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            self.editor.delete("1.0", tk.END)
            self.editor.insert(tk.END, f.read())

        self.file_path = path
        self.root.title(f"{APP_TITLE} - {os.path.basename(path)}")
        self.highlight_syntax()

    def save_file(self):
        if not self.file_path:
            return self.save_as()

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(self.editor.get("1.0", tk.END))

        messagebox.showinfo("Saved", "File saved successfully.")

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".do",
            filetypes=[("DoScript Files", "*.do"), ("All Files", "*.*")]
        )
        if not path:
            return

        self.file_path = path
        self.save_file()
        self.root.title(f"{APP_TITLE} - {os.path.basename(path)}")

    def confirm_discard_changes(self):
        if self.editor.get("1.0", tk.END).strip():
            return messagebox.askyesno("Discard?", "Discard current changes?")
        return True

    def _get_current_token(self):
        idx = self.editor.index('insert')
        line, col = map(int, idx.split('.'))
        line_text = self.editor.get(f'{line}.0', f'{line}.end')
        left = line_text[:col]
        m = re.search(r"([A-Za-z0-9_]+)$", left)
        return m.group(1) if m else ''

    def _collect_candidates(self):
        words = set(KEYWORDS)
        text = self.editor.get('1.0', tk.END)
        for m in re.finditer(r'^function\s+(\w+)', text, re.MULTILINE):
            words.add(m.group(1))
        return sorted(words)

    def _index_from_pos(self, pos):
        return '1.0 + %dc' % pos

    def _update_status(self, txt):
        try:
            self.root.title(f"{APP_TITLE} - {os.path.basename(self.file_path) if self.file_path else ''} - {txt}")
        except Exception:
            self.root.title(APP_TITLE)

    def on_close(self):
        if self.confirm_discard_changes():
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DoScriptIDE(root)
    root.mainloop()

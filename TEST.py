import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os
import threading
import keyword
import builtins
import ast
import re

class PythonEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Editor")
        self.geometry("1200x800")
        self.minsize(900, 600)

        self.current_file = None
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.pos_var = tk.StringVar(value="Ln 1, Col 1")
        self.output_queue = []
        self.find_win = None

        self._setup_ui()
        self._bind_shortcuts()
        self._update_line_numbers()
        self.after(100, self._poll_queue)

    def _setup_ui(self):
        self._setup_menu()
        self._setup_toolbar()
        self._setup_editor_area()
        self._setup_output_area()
        self._setup_statusbar()

    def _setup_menu(self):
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        filemenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        filemenu.add_command(label="Save As...", command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.text.event_generate("<<Undo>>"))
        editmenu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self.text.event_generate("<<Redo>>"))
        editmenu.add_separator()
        editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.text.event_generate("<<Cut>>"))
        editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.text.event_generate("<<Copy>>"))
        editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.text.event_generate("<<Paste>>"))
        editmenu.add_separator()
        editmenu.add_command(label="Find", accelerator="Ctrl+F", command=self.show_find)
        editmenu.add_command(label="Replace", accelerator="Ctrl+H", command=self.show_replace)
        editmenu.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: self.text.tag_add("sel", "1.0", "end"))
        menubar.add_cascade(label="Edit", menu=editmenu)

        runmenu = tk.Menu(menubar, tearoff=0)
        runmenu.add_command(label="Run", accelerator="F5", command=self.run_code)
        runmenu.add_command(label="Check Syntax", command=self.check_syntax)
        menubar.add_cascade(label="Run", menu=runmenu)

        self.config(menu=menubar)

    def _setup_toolbar(self):
        tb = ttk.Frame(self, padding=(6, 4))
        tb.pack(side="top", fill="x")

        for text, cmd in [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("Run", self.run_code),
            ("Check", self.check_syntax),
            ("Find", self.show_find),
        ]:
            ttk.Button(tb, text=text, command=cmd).pack(side="left", padx=3)

    def _setup_editor_area(self):
        container = ttk.Panedwindow(self, orient="horizontal")
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container)
        right = ttk.Frame(container)
        container.add(left, weight=1)
        container.add(right, weight=3)

        self.line_numbers = tk.Text(
            left,
            width=5,
            padx=4,
            takefocus=0,
            border=0,
            state="disabled",
            background="#f0f0f0",
            foreground="#666",
        )
        self.line_numbers.pack(side="left", fill="y")

        editor_frame = ttk.Frame(right)
        editor_frame.pack(fill="both", expand=True)

        yscroll = ttk.Scrollbar(editor_frame)
        yscroll.pack(side="right", fill="y")
        xscroll = ttk.Scrollbar(editor_frame, orient="horizontal")
        xscroll.pack(side="bottom", fill="x")

        self.text = tk.Text(
            editor_frame,
            wrap="none",
            undo=True,
            autoseparators=True,
            maxundo=-1,
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set,
            font=("Consolas", 12),
            insertbackground="white",
            background="#1e1e1e",
            foreground="#f8f8f2",
            selectbackground="#264f78",
        )
        self.text.pack(side="left", fill="both", expand=True)

        yscroll.config(command=self._on_scroll_y)
        xscroll.config(command=self.text.xview)

        self.text.bind("<KeyRelease>", self._on_change)
        self.text.bind("<ButtonRelease-1>", self._on_change)
        self.text.bind("<MouseWheel>", self._on_change)
        self.text.bind("<Control-f>", lambda e: self.show_find())
        self.text.bind("<Control-h>", lambda e: self.show_replace())
        self.text.bind("<Control-s>", lambda e: self.save_file())
        self.text.bind("<Control-o>", lambda e: self.open_file())
        self.text.bind("<Control-n>", lambda e: self.new_file())
        self.text.bind("<F5>", lambda e: self.run_code())

        self.text.bind("<<Modified>>", self._on_modified)

        self._create_syntax_tags()
        self._setup_find_replace()

    def _setup_output_area(self):
        frame = ttk.LabelFrame(self, text="Output", padding=4)
        frame.pack(side="bottom", fill="both", expand=False)

        self.output = tk.Text(
            frame,
            height=10,
            wrap="none",
            font=("Consolas", 11),
            background="#111",
            foreground="#ddd",
        )
        self.output.pack(side="left", fill="both", expand=True)

        out_scroll = ttk.Scrollbar(frame, command=self.output.yview)
        out_scroll.pack(side="right", fill="y")
        self.output.config(yscrollcommand=out_scroll.set)

    def _setup_statusbar(self):
        bar = ttk.Frame(self)
        bar.pack(side="bottom", fill="x")
        ttk.Label(bar, textvariable=self.status_var, anchor="w").pack(side="left", fill="x", expand=True)
        ttk.Label(bar, textvariable=self.pos_var).pack(side="right")

        self.text.bind("<KeyRelease>", self._update_cursor_pos)
        self.text.bind("<ButtonRelease-1>", self._update_cursor_pos)

    def _setup_find_replace(self):
        self.find_win = None

    def _bind_shortcuts(self):
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-f>", lambda e: self.show_find())
        self.bind_all("<Control-h>", lambda e: self.show_replace())
        self.bind_all("<F5>", lambda e: self.run_code())

    def _create_syntax_tags(self):
        self.keyword_pattern = keyword.kwlist
        self.text.tag_configure("keyword", foreground="#c678dd")
        self.text.tag_configure("string", foreground="#98c379")
        self.text.tag_configure("comment", foreground="#5c6370")
        self.text.tag_configure("number", foreground="#d19a66")
        self.text.tag_configure("builtin", foreground="#61afef")

    def _on_scroll_y(self, *args):
        self.text.yview(*args)
        self._sync_line_numbers()

    def _on_change(self, event=None):
        self.after_idle(self._highlight_syntax)
        self.after_idle(self._update_line_numbers)
        self.after_idle(self._update_cursor_pos)
        self.after_idle(self._sync_line_numbers)

    def _on_modified(self, event=None):
        self.text.edit_modified(False)

    def _update_cursor_pos(self, event=None):
        idx = self.text.index("insert")
        line, col = idx.split(".")
        self.pos_var.set(f"Ln {line}, Col {int(col) + 1}")

    def _update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        line_count = int(self.text.index("end-1c").split(".")[0])
        nums = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", nums)
        self.line_numbers.config(state="disabled")
        self._sync_line_numbers()

    def _sync_line_numbers(self):
        self.line_numbers.yview_moveto(self.text.yview()[0])

    def _highlight_syntax(self, event=None):
        code = self.text.get("1.0", "end-1c")
        for tag in ("keyword", "string", "comment", "number", "builtin"):
            self.text.tag_remove(tag, "1.0", "end")

        for match in re.finditer(r"#[^\n]*", code):
            self._tag_from_span("comment", match.start(), match.end())

        string_pattern = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')'
        for match in re.finditer(string_pattern, code, re.S):
            self._tag_from_span("string", match.start(), match.end())

        for match in re.finditer(r"\b\d+(?:\.\d+)?\b", code):
            self._tag_from_span("number", match.start(), match.end())

        for kw in self.keyword_pattern:
            for match in re.finditer(rf"\b{re.escape(kw)}\b", code):
                self._tag_from_span("keyword", match.start(), match.end())

        for name in dir(builtins):
            if not name.startswith("_"):
                for match in re.finditer(rf"\b{re.escape(name)}\b", code):
                    self._tag_from_span("builtin", match.start(), match.end())

    def _tag_from_span(self, tag, start, end):
        start_idx = self._index_from_pos(start)
        end_idx = self._index_from_pos(end)
        self.text.tag_add(tag, start_idx, end_idx)

    def _index_from_pos(self, pos):
        data = self.text.get("1.0", "end-1c")
        line = data.count("\n", 0, pos) + 1
        last_nl = data.rfind("\n", 0, pos)
        col = pos if last_nl == -1 else pos - last_nl - 1
        return f"{line}.{col}"

    def new_file(self):
        if self._confirm_discard():
            self.text.delete("1.0", "end")
            self.current_file = None
            self.title("Python Editor")
            self.status_var.set("New file")
            self.output.delete("1.0", "end")

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.current_file = path
        self.title(f"Python Editor - {os.path.basename(path)}")
        self.status_var.set(f"Opened {path}")
        self._highlight_syntax()
        self._update_line_numbers()

    def save_file(self):
        if self.current_file is None:
            return self.save_as()
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", "end-1c"))
        self.status_var.set(f"Saved {self.current_file}")
        self.text.edit_modified(False)

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
        if not path:
            return
        self.current_file = path
        self.save_file()
        self.title(f"Python Editor - {os.path.basename(path)}")

    def check_syntax(self):
        code = self.text.get("1.0", "end-1c")
        try:
            ast.parse(code)
            self._set_output("Syntax OK\n")
            self.status_var.set("Syntax check passed")
        except SyntaxError as e:
            self._set_output(f"SyntaxError: {e.msg} at line {e.lineno}, column {e.offset}\n")
            self.status_var.set("Syntax check failed")

    def run_code(self):
        code = self.text.get("1.0", "end-1c")
        self._set_output("Running...\n")

        def worker():
            try:
                proc = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                out = proc.stdout + proc.stderr
                self.output_queue.append(out if out else "(no output)\n")
                self.output_queue.append(f"Exit code: {proc.returncode}\n")
            except Exception as e:
                self.output_queue.append(f"Error: {e}\n")

        threading.Thread(target=worker, daemon=True).start()

    def show_find(self):
        self._show_find_replace(mode="find")

    def show_replace(self):
        self._show_find_replace(mode="replace")

    def _show_find_replace(self, mode="find"):
        if self.find_win and self.find_win.winfo_exists():
            self.find_win.lift()
            return

        win = tk.Toplevel(self)
        self.find_win = win
        win.title("Find / Replace")
        win.resizable(False, False)

        ttk.Label(win, text="Find:").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        ttk.Entry(win, textvariable=self.find_var, width=30).grid(row=0, column=1, padx=6, pady=4)

        if mode == "replace":
            ttk.Label(win, text="Replace:").grid(row=1, column=0, padx=6, pady=4, sticky="e")
            ttk.Entry(win, textvariable=self.replace_var, width=30).grid(row=1, column=1, padx=6, pady=4)
            ttk.Button(win, text="Replace All", command=self.replace_all).grid(row=2, column=0, columnspan=2, pady=6)

        ttk.Button(win, text="Find Next", command=self.find_next).grid(
            row=3 if mode == "replace" else 1,
            column=0,
            columnspan=2,
            pady=6,
        )

    def find_next(self):
        needle = self.find_var.get()
        if not needle:
            return
        start = self.text.index("insert")
        pos = self.text.search(needle, start, stopindex="end", nocase=False)
        if not pos:
            pos = self.text.search(needle, "1.0", stopindex=start, nocase=False)
        if pos:
            end = f"{pos}+{len(needle)}c"
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", pos, end)
            self.text.mark_set("insert", end)
            self.text.see(pos)

    def replace_all(self):
        needle = self.find_var.get()
        repl = self.replace_var.get()
        if not needle:
            return
        content = self.text.get("1.0", "end-1c").replace(needle, repl)
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self._highlight_syntax()

    def _set_output(self, text):
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.see("end")

    def _poll_queue(self):
        if self.output_queue:
            text = "".join(self.output_queue)
            self.output_queue.clear()
            self._set_output(text)
            self.status_var.set("Run complete")
        self.after(100, self._poll_queue)

    def _confirm_discard(self):
        if self.text.edit_modified():
            return messagebox.askyesno("Unsaved changes", "Discard current changes?")
        return True

if __name__ == "__main__":
    app = PythonEditor()
    app.mainloop()
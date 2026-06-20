import ast
from dataclasses import dataclass, field

TK_WIDGETS = {"Label", "Entry", "Button", "Frame"}

@dataclass
class Widget:
    kind: str
    var_name: str | None = None
    text: str = ""
    command: str | None = None
    textvariable: str | None = None

@dataclass
class UIModel:
    title: str = "App"
    widgets: list = field(default_factory=list)
    stringvars: dict = field(default_factory=dict)

class TkToHTML(ast.NodeVisitor):
    def __init__(self):
        self.model = UIModel()
        self.func_names = set()

    def _name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _const_str(self, node):
        return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else ""

    def visit_FunctionDef(self, node):
        self.func_names.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call):
            fn = self._name(node.value.func)
            target = node.targets[0] if node.targets else None
            target_name = target.id if isinstance(target, ast.Name) else None

            if fn == "StringVar":
                value = ""
                for kw in node.value.keywords:
                    if kw.arg == "value":
                        value = self._const_str(kw.value)
                self.model.stringvars[target_name] = value
                return

            if fn in TK_WIDGETS:
                text = ""
                command = None
                textvariable = None
                for kw in node.value.keywords:
                    if kw.arg == "text":
                        text = self._const_str(kw.value)
                    elif kw.arg == "command":
                        command = self._name(kw.value)
                    elif kw.arg == "textvariable":
                        textvariable = self._name(kw.value)

                self.model.widgets.append(
                    Widget(
                        kind=fn,
                        var_name=target_name,
                        text=text,
                        command=command,
                        textvariable=textvariable,
                    )
                )
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            attr = node.value.func.attr
            if attr == "title" and node.value.args:
                self.model.title = self._const_str(node.value.args[0])
        self.generic_visit(node)

def render_html(model: UIModel) -> str:
    lines = [
        "<!doctype html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{model.title}</title>",
        """<style>
body{font-family:Arial,sans-serif;margin:24px}
.app{max-width:420px;padding:16px;border:1px solid #ccc;border-radius:12px}
.row{margin:10px 0}
input,button{font-size:14px;padding:8px}
button{margin-right:8px}
.error{color:#b00020;margin-top:10px}
</style>""",
        "</head>",
        "<body>",
        f'<div class="app"><h2>{model.title}</h2>',
    ]

    for w in model.widgets:
        if w.kind == "Label":
            if w.textvariable and w.textvariable in model.stringvars:
                lines.append(f'<div class="row" id="{w.var_name}">{model.stringvars[w.textvariable]}</div>')
            else:
                lines.append(f'<div class="row">{w.text}</div>')
        elif w.kind == "Entry":
            lines.append(f'<input class="row" id="{w.var_name}" type="text">')
        elif w.kind == "Button":
            lines.append(f'<button id="{w.var_name}">{w.text}</button>')

    lines += [
        '<div class="error" id="error"></div>',
        "</div>",
        "<script>",
        "const $ = (id) => document.getElementById(id);",
        "function setResult(text){",
        "  const out = document.querySelector('.result');",
        "  if (out) out.textContent = text;",
        "}",
        "</script>",
        "</body>",
        "</html>",
    ]
    return "\n".join(lines)

source = open("readthis.py", encoding="utf-8").read()
tree = ast.parse(source)
conv = TkToHTML()
conv.visit(tree)
html = render_html(conv.model)
open("out_putfile.html", "w", encoding="utf-8").write(html)
print(html)

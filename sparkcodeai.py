from openai import OpenAI
from pyscript import when, document
import asyncio
import json
import ast
from dataclasses import dataclass, field

OPENAI_API_KEY = "" #Due to security reasons on GitHub this API key is left blank.

button_dict = {
    # Desktop Apps
    "desktop-1": "Create a modern desktop habit tracker with streaks, reminders, analytics, and a clean mobile-first UI.",
    "desktop-2": "Build a sleek desktop expense tracker with charts, categories, monthly goals, and dark mode support.",
    "desktop-3": "Design a desktop study planner app with task lists, deadlines, progress bars, and an elegant dashboard.",
    "desktop-4": "Create a desktop note-taking app with folders, search, tags, and a minimalist interface.",
    
    # Mobile Apps
    "mobile-apps-1": "Create a mobile fitness tracking app with workout logs, progress charts, and personalized plans.",
    "mobile-apps-2": "Build a mobile social media app with posts, comments, likes, and real-time notifications.",
    "mobile-apps-3": "Design a mobile shopping app with product categories, filters, cart, and secure checkout.",
    "mobile-apps-4": "Create a mobile weather app with live updates, forecasts, maps, and customizable alerts.",
    
    # Web Apps
    "web-apps-1": "Build a modern web habit tracker with streaks, reminders, analytics, and a clean responsive UI.",
    "web-apps-2": "Create a web expense tracker with charts, categories, monthly goals, and dark mode support.",
    "web-apps-3": "Design a web study planner with task lists, deadlines, progress bars, and an elegant dashboard.",
    "web-apps-4": "Build a web project management tool with teams, tasks, timelines, and real-time collaboration.",
    
    # Websites
    "websites-1": "Create a modern portfolio website with animated sections, gallery, and contact form.",
    "websites-2": "Build an e-commerce website landing page with product showcase, features, and checkout button.",
    "websites-3": "Design a blog website with articles, categories, search, and responsive layout.",
    "websites-4": "Create a restaurant website with menu, reservations, reviews, and location map.",
    
    # Desktop Games
    "desktop-games-1": "Generate a polished desktop memory card game with levels, score tracking, timers, and smooth animations.",
    "desktop-games-2": "Make a desktop snake game with responsive controls, high scores, and a clean retro-modern UI.",
    "desktop-games-3": "Create a desktop quiz game with categories, score tracking, timer mode, and a modern dashboard.",
    "desktop-games-4": "Build a desktop puzzle game with levels, hints, score system, and elegant visual effects.",
    
    # Mobile Games
    "mobile-games-1": "Create a casual mobile jumping game with collectibles, levels, power-ups, and smooth animations.",
    "mobile-games-2": "Build a mobile racing game with tracks, cars, upgrades, and competitive leaderboards.",
    "mobile-games-3": "Design a mobile matching game with patterns, timers, streaks, and colorful visuals.",
    "mobile-games-4": "Create a mobile arcade shooter with enemies, weapons, scores, and epic boss battles.",
    
    # Web Games
    "web-games-1": "Generate a polished web memory card game with levels, score tracking, timers, and smooth animations.",
    "web-games-2": "Make a web snake game with responsive controls, high scores, and a clean retro-modern UI.",
    "web-games-3": "Create a web quiz game with categories, score tracking, timer mode, and a modern dashboard.",
    "web-games-4": "Build a simple web platformer with collectibles, levels, and smooth character movement.",
    
    # 2D Games
    "2d-games-1": "Create a 2D platformer game with levels, collectibles, enemies, and smooth character controls.",
    "2d-games-2": "Build a 2D top-down shooter with weapons, enemies, health system, and epic boss fights.",
    "2d-games-3": "Design a 2D puzzle game with mechanics, levels, hints, and beautiful visual effects.",
    "2d-games-4": "Create a 2D racing game with tracks, cars, boosts, and competitive time trials.",
    
    # 3D Games
    "3d-games-1": "Make an immersive 3D adventure with exploration, quests, items, and realistic graphics.",
    "3d-games-2": "Create a 3D shooter with weapons, enemies, levels, and stunning visual effects.",
    "3d-games-3": "Build a 3D racing game with tracks, cars, upgrades, and realistic physics.",
    "3d-games-4": "Design a 3D puzzle game with mechanics, levels, and immersive environments.",
    
    # Chatbot
    "chatbot-1": "Create an AI chatbot with natural conversations, context memory, and helpful responses.",
    "chatbot-2": "Build a customer support chatbot with FAQs, troubleshooting, and ticket creation.",
    "chatbot-3": "Design a learning chatbot with tutorials, quizzes, explanations, and progress tracking.",
    "chatbot-4": "Create a fun chatbot with personality, jokes, stories, and interactive games.",
    
    # Analytics Tools
    "analytics-tools-1": "Create an analytics dashboard with charts, metrics, filters, and real-time data updates.",
    "analytics-tools-2": "Build a data visualization tool with graphs, tables, exports, and customizable views.",
    "analytics-tools-3": "Design a business analytics tool with KPIs, reports, trends, and predictive insights.",
    "analytics-tools-4": "Create a web analytics tool with traffic, conversions, user behavior, and reports.",
    
    # Research Tools
    "research-tools-1": "Create a research organizer with notes, citations, sources, and automated bibliography.",
    "research-tools-2": "Build a literature search tool with filters, results, saving, and export capabilities.",
    "research-tools-3": "Design a data collection tool with surveys, responses, analysis, and visualizations.",
    "research-tools-4": "Create a citation manager with databases, grouping, formats, and quick insertion.",
    
    # AI Assistants
    "ai-assistants-1": "Create an AI assistant with task automation, reminders, suggestions, and smart notifications.",
    "ai-assistants-2": "Build a writing assistant with grammar check, suggestions, improvements, and style analysis.",
    "ai-assistants-3": "Design a coding assistant with code generation, debugging, explanations, and best practices.",
    "ai-assistants-4": "Create a research assistant with search, summarization, citations, and insights.",
}

#last_chat_target = None
chat_state = {"last_target": None}


@when("click", ".step2-btn")
async def button_handler(event):    
    question = button_dict.get(event.target.id)
    add_question = mainc(chat_state["last_target"])
    if add_question:
        full_question = question + add_question
    else:
        full_question = question
    print(full_question)
    await answer_Promt(full_question)


async def answer_Promt(question):
    try:
        if not question:
            await typing_print("Error: No question provided")
            return
        answer = await call_openai(question)
        await typing_print(answer)
    except Exception as e:
        await typing_print(f"Error: {str(e)}")

async def call_openai(question):
    from pyscript import fetch
    
    url = "https://api.openai.com/v1/responses"
    payload = {
        "model": "gpt-5.4-mini",
        "input": question,
        "store": True,
    }
    response = await fetch(
        url,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        body=json.dumps(payload),
    )
    if not response.ok:
        error_data = await response.json()
        raise Exception(f"OpenAI API error: {error_data}")
    
    data = await response.json()
    answer = data["output"][0]["content"][0]["text"]
    return answer

async def typing_print(text, delay=0.001):
    import sys

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        await asyncio.sleep(delay)
    print()

def run_openaiforcustom(custom_text):
    response = OpenAI(api_key=OPENAI_API_KEY).responses.create(
        model="gpt-5.4-mini",
        input=custom_text,
        store=True,
    )
    answer = response.output_text
    print(answer)


@when("click", "#send-button")
def on_send_click(event):
    input_elem = document.querySelector("#chat-input")
    custom_text = input_elem.value.strip()
    add_question = mainc(chat_state["last_target"])
    if add_question:
        full_question = custom_text + add_question
    else:
        full_question = custom_text

    if custom_text:
        run_openaiforcustom(full_question)
    else:
        print("Input is empty!")

app_names = {
    "desktop": "desktop app",
    "mobile": "mobile app",
    "web": "web app",
    "websites": "website",
    "desktop-games": "desktop game",
    "mobile-games": "mobile game",
    "web-games": "web game",
    "2d": "2D game",
    "3d": "3D game",
    "chatbot": "chatbot",
    "analytics": "analytics tool",
    "research": "research tool",
    "ai": "AI assistant",
}

def mainc(target):
    if not target:
        return None
    lang_id = target.id
    if "-" not in lang_id:
        return None
    parts = lang_id.split("-", 1)
    app_key = parts[0]
    language = parts[1]
    
    if app_key in app_names:
        base = f"{language.title()}, {app_names[app_key]}"
        add_question = f" in {base}."
        return add_question
    
    return None


@when("click", "#chat-area")
async def on_chat_area_click(event):
    target = event.target
    chat_state["last_target"] = target
    mainc(target)

match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
answer = match.group(1).strip() if match else text.strip()

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

source = open(answer, encoding="utf-8").read()
tree = ast.parse(source)
conv = TkToHTML()
conv.visit(tree)
html = render_html(conv.model)
open("preview.html", "w", encoding="utf-8").write(html)
print(html)

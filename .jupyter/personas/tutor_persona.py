"""
Tutor — a local Jupyter AI v3 persona for this Python learning workspace.

WHAT IT DOES
    Helps you learn Python inside JupyterLab:

      • `new <topic>`   — scaffold a ready-to-run practice notebook
        (`practice_<topic>.ipynb`, a copy of `practice_template.ipynb` with the
        TOPIC pre-set) into the workspace, then point you at it.
      • `list`          — list the course lessons (`lessons/`) and the practice
        notebooks already in the workspace. (`lessons` works too.)
      • `help`          — command help.

    Anything else is answered conversationally by the configured chat model
    (Ollama or OpenRouter — whatever is selected in Jupyternaut Settings),
    using a Python-tutor system prompt.

HOW JUPYTER AI FINDS THIS FILE
    Jupyter AI v3 auto-loads any `*.py` whose name contains "persona" (and does
    not start with "_") from `<workspace>/.jupyter/personas/`, importing every
    `BasePersona` subclass it declares. No packaging / entry point is required.
    See `jupyter_ai_persona_manager.persona_manager.load_from_dir`. After editing
    this file, run the `/refresh-personas` command in chat (or restart Jupyter
    Lab) to reload it.

DESIGN NOTE — why the commands are deterministic, not tool-calls
    This workspace defaults to a *local Ollama* model, whose function/tool
    calling can be unreliable (especially on smaller models). So the scaffolding
    and listing actions are executed deterministically by this persona the
    moment a command is recognised — they never depend on the model emitting a
    correct tool call. The configured chat model is used only for the
    conversational layer (explanations / free-form questions) when no command
    is matched. This makes the commands work regardless of which model is
    selected. It's also a worked example of how to build your own persona —
    see `docs/PERSONAS.md`.

WHY EXERCISES LIVE IN THE NOTEBOOK
    A persona streams markdown into the chat panel; it cannot render into your
    notebook, and runnable code + `%%ai` cells are exactly what a notebook is
    for. So this persona *scaffolds* the notebook and lets the `%%ai` cells
    inside it generate topic-specific exercises when you run them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from jupyter_ai_persona_manager import BasePersona, PersonaDefaults
from jupyterlab_chat.models import Message

# ── Workspace layout ────────────────────────────────────────────────────────
# This file lives at <workspace>/.jupyter/personas/tutor_persona.py, so the
# workspace root is three parents up. The practice-notebook template lives at
# the workspace root, and scaffolded notebooks are written there too.
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_NOTEBOOK = WORKSPACE_ROOT / "practice_template.ipynb"
LESSONS_DIR = WORKSPACE_ROOT / "lessons"
AVATAR_PATH = str(Path(__file__).resolve().parent / "tutor_avatar.svg")

PRACTICE_PREFIX = "practice_"

SYSTEM_PROMPT = """\
You are **Tutor**, a friendly Python tutor embedded in a JupyterLab learning \
workspace. The learner is an individual studying Python development; meet them \
at their level, explain *why* and not just *how*, and prefer small runnable \
examples they can paste into a notebook cell.

You can perform these chat commands yourself (tell the user to type them \
exactly; you do NOT need to call a tool — the workspace executes the command \
deterministically):

  • `new <topic>` — scaffold a practice notebook for a topic, e.g. \
`new list comprehensions` → `practice_list_comprehensions.ipynb`
  • `list`        — list the course lessons and the practice notebooks in \
the workspace (`lessons` works too)
  • `help`        — show command help

Key facts to convey accurately:
  • The **eight-week beginner course** lives in the `lessons/` folder \
(`lessons/01-welcome-to-python.ipynb` through `08-...`); learners should \
start with lesson 01 and open the notebooks from the file browser. \
`lessons/README.md` has the full schedule.
  • Practice notebooks are created from `practice_template.ipynb` at the \
workspace root and contain `%%ai` cells that generate exercises for the topic \
when run — the learner should open the scaffolded notebook and *Run All*.
  • The workspace also has **@Jupyternaut** (the general assistant) and the \
`%%ai` notebook magics; the model used by all of them is picked in \
**Settings → Jupyternaut Settings** (local `ollama_chat/...` or hosted \
`openrouter/...`).
  • The data toolkit (`numpy`, `pandas`, `matplotlib`, `scipy`) is already \
installed in the workspace venv.

Be concise and encouraging. When the user clearly wants a practice notebook, \
remind them of the exact `new <topic>` syntax rather than generating exercises \
in chat."""


# ── Pure helpers (module-level so tests/test_tutor_persona.py can hit them) ──

def strip_mentions(body: str) -> str:
    """Remove leading @-mentions (e.g. '@Tutor') the UI prepends."""
    return re.sub(r"^(?:\s*@[\w-]+)+\s*", "", body)


def slugify_topic(topic: str) -> str:
    """
    Turn a free-form topic ('List Comprehensions!') into a filename-safe slug
    ('list_comprehensions'). Returns '' if nothing safe remains.
    """
    slug = topic.strip().lower()
    slug = re.sub(r"[\s/]+", "_", slug)          # spaces and slashes → _
    slug = re.sub(r"[^a-z0-9_-]", "", slug)       # drop anything else
    slug = re.sub(r"_+", "_", slug).strip("_-")   # collapse/trim separators
    return slug[:48]


def parse_command(text: str) -> dict[str, Any]:
    """
    Parse an explicit Tutor command. Returns a dict with `kind` one of:
    new | list | help | chat, plus the captured `topic` for `new`.
    Lenient: 'new', 'practice', 'scaffold', and 'notebook' are all accepted verbs.
    """
    lower = text.lower().strip()
    if lower in ("help", "?", "/help", "commands"):
        return {"kind": "help"}
    if lower in ("list", "ls", "notebooks", "lessons"):
        return {"kind": "list"}

    tokens = text.split()
    if not tokens:
        return {"kind": "chat"}

    verb = tokens[0].lower()
    if verb not in ("new", "practice", "scaffold", "notebook"):
        return {"kind": "chat"}

    # Everything after the verb is the topic ('new list comprehensions').
    return {"kind": "new", "topic": " ".join(tokens[1:]).strip() or None}


def format_listing(lesson_names: list[str], practice_names: list[str]) -> str:
    """
    Render the `list` reply from the two notebook collections (names only —
    the caller does the filesystem walking, keeping this pure for tests).
    """
    sections = []

    if lesson_names:
        lines = "\n".join(f"- `lessons/{name}`" for name in lesson_names)
        sections.append(
            "**Course lessons** — open from the `lessons/` folder in the file "
            "browser; start with lesson 01 (the schedule is in "
            "`lessons/README.md`):\n\n" + lines
        )

    if practice_names:
        lines = "\n".join(f"- `{name}`" for name in practice_names)
        sections.append("**Practice notebooks**\n\n" + lines)
    else:
        sections.append(
            "**Practice notebooks** — none yet. Create one with `new <topic>` "
            "— e.g. `new list comprehensions`."
        )

    return "\n\n".join(sections)


def set_topic(nb: dict, topic: str) -> int:
    """Rewrite the `TOPIC = …` assignment in the notebook dict. Returns count."""
    count = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        lines = src if isinstance(src, list) else src.splitlines(keepends=True)
        new_lines = []
        for line in lines:
            if line.lstrip().startswith("TOPIC"):
                escaped = topic.replace("\\", "\\\\").replace('"', '\\"')
                new_lines.append(
                    f'TOPIC = "{escaped}"  # scaffolded by Tutor\n'
                )
                count += 1
            else:
                new_lines.append(line)
        cell["source"] = new_lines
    return count


class TutorPersona(BasePersona):
    """Scaffolds practice notebooks on command; tutors via the configured model."""

    @property
    def defaults(self) -> PersonaDefaults:
        return PersonaDefaults(
            name="Tutor",
            description=(
                "Python tutor: answers learning questions with the configured "
                "model and scaffolds ready-to-run practice notebooks "
                "(`new <topic>`) from practice_template.ipynb."
            ),
            avatar_path=AVATAR_PATH,
            system_prompt=SYSTEM_PROMPT,
        )

    # ── entry point ─────────────────────────────────────────────────────────
    async def process_message(self, message: Message) -> None:
        text = strip_mentions(message.body or "").strip()
        parsed = parse_command(text)

        try:
            if parsed["kind"] == "help":
                self.send_message(self._help_text())
            elif parsed["kind"] == "list":
                self.send_message(self._list_text())
            elif parsed["kind"] == "new":
                await self.stream_message(self._run_new(parsed))
            else:
                # No recognised command → conversational tutoring via the model.
                await self._respond_with_model(message)
        except Exception as e:  # never let the persona crash the chat
            self.log.exception("Tutor failed to process a message.")
            self.send_message(f"**Tutor error:** {e}")

    # ── `new` — scaffold a practice notebook ─────────────────────────────────
    async def _run_new(self, cmd: dict[str, Any]) -> AsyncIterator[str]:
        topic = cmd.get("topic")
        if not topic:
            yield (
                "**Missing topic.** Usage: `new <topic>` — e.g. "
                "`new list comprehensions`, `new dictionaries`, `new pandas basics`."
            )
            return

        slug = slugify_topic(topic)
        if not slug:
            yield (
                f"**Couldn't make a notebook name out of `{topic}`.** Use letters, "
                "digits, spaces, `-` or `_` — e.g. `new string formatting`."
            )
            return

        if not TEMPLATE_NOTEBOOK.exists():
            yield f"**Template missing:** `{self._rel(TEMPLATE_NOTEBOOK)}` not found."
            return

        yield f"Scaffolding a practice notebook for **{topic}** …\n\n"
        try:
            nb = json.loads(TEMPLATE_NOTEBOOK.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            yield f"**Couldn't read the template notebook:** {e}"
            return

        replaced = set_topic(nb, topic)
        if not replaced:
            yield (
                "**Couldn't find a `TOPIC = …` line** in the template; "
                "aborting so nothing is written incorrectly."
            )
            return

        dest = WORKSPACE_ROOT / f"{PRACTICE_PREFIX}{slug}.ipynb"
        existed = dest.exists()
        dest.write_text(json.dumps(nb, indent=1), encoding="utf-8")

        yield (
            f"- ✅ Wrote `{self._rel(dest)}` (TOPIC pre-set, {replaced} cell updated)."
            + (" *(replaced the previous copy)*" if existed else "")
            + "\n\n**Open it** from the JupyterLab file browser and *Run All*. "
            "Its `%%ai` cells ask the configured model for an explanation and "
            "exercises about your topic; solve them in the empty cells that follow."
        )

    # ── `list` — course lessons + practice notebooks ──────────────────────────
    def _list_text(self) -> str:
        # Numbered course notebooks; sorted() puts them in course order
        # (01-…, 02-…). The folder may be absent in stripped-down copies.
        lessons = (
            sorted(n.name for n in LESSONS_DIR.glob("*.ipynb"))
            if LESSONS_DIR.is_dir()
            else []
        )
        practice = sorted(
            n.name
            for n in WORKSPACE_ROOT.glob(f"{PRACTICE_PREFIX}*.ipynb")
            if n.name != TEMPLATE_NOTEBOOK.name
        )
        return format_listing(lessons, practice)

    @staticmethod
    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(WORKSPACE_ROOT))
        except ValueError:
            return str(p)

    # ── conversational fallback (uses the user-configured chat model) ────────
    def _config_manager(self):
        try:
            return self.parent.serverapp.web_app.settings.get("jupyternaut.config_manager")
        except Exception:
            return None

    async def _respond_with_model(self, message: Message) -> None:
        cfg = self._config_manager()
        model_id = getattr(cfg, "chat_model", None) if cfg else None
        if not model_id:
            # No model configured — still useful: explain what the persona can do.
            self.send_message(
                "I'm **Tutor**. No chat model is configured "
                "(*Settings → Jupyternaut Settings*), so I can't free-form chat, "
                "but I can still scaffold practice notebooks.\n\n" + self._help_text()
            )
            return

        try:
            from jupyter_ai_jupyternaut.jupyternaut.chat_models import ChatLiteLLM
            from langchain_core.messages import HumanMessage, SystemMessage

            model = ChatLiteLLM(
                **cfg.chat_model_args, model=model_id, streaming=True
            )
            history = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=message.body or ""),
            ]

            async def aiter() -> AsyncIterator[str]:
                async for chunk in model.astream(history):
                    content = getattr(chunk, "content", "")
                    if isinstance(content, str) and content:
                        yield content

            await self.stream_message(aiter())
        except Exception:
            self.log.exception("Tutor model fallback failed.")
            self.send_message(
                "I couldn't reach the configured chat model. You can still "
                "scaffold practice notebooks directly:\n\n" + self._help_text()
            )

    # ── static text ──────────────────────────────────────────────────────────
    def _help_text(self) -> str:
        return (
            "**Tutor — commands**\n\n"
            "- `new <topic>` — scaffold `practice_<topic>.ipynb` from the "
            "template, with the topic pre-set (e.g. `new list comprehensions`)\n"
            "- `list` — list the course lessons (`lessons/`) and the practice "
            "notebooks in the workspace\n"
            "- `help` — this message\n\n"
            "Anything else is answered conversationally by the configured chat "
            "model (pick it in *Settings → Jupyternaut Settings*). Practice "
            "notebooks are written to the workspace root."
        )

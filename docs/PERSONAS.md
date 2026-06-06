# Writing your own AI persona

Jupyter AI v3 lets a workspace ship its own chat participants — **local
personas** — as plain Python files. This repo's **Tutor**
([`.jupyter/personas/tutor_persona.py`](../.jupyter/personas/tutor_persona.py))
is a complete worked example; this doc explains the mechanism and the design
pattern so you can build your own.

## How personas are discovered

Jupyter AI auto-loads any `*.py` file whose name contains `persona` (and does
not start with `_`) from `<workspace>/.jupyter/personas/`, importing every
`BasePersona` subclass it declares. No packaging, entry points, or pip install
required — drop the file in, and the persona appears in the chat's `@`-mention
menu.

- After editing a persona file, run **`/refresh-personas`** in the chat (or
  restart JupyterLab) to reload it. (This repo's `jupyter_ai_config.py` patches
  an upstream bug that otherwise crashes `/refresh-personas`.)
- Import errors are reported in the Jupyter server log — check there if your
  persona doesn't appear.

## The minimal skeleton

```python
from jupyter_ai_persona_manager import BasePersona, PersonaDefaults
from jupyterlab_chat.models import Message


class MyPersona(BasePersona):
    @property
    def defaults(self) -> PersonaDefaults:
        return PersonaDefaults(
            name="My Persona",                      # the @-mention name
            description="One line shown in the UI.",
            avatar_path="/abs/path/to/avatar.svg",  # optional
            system_prompt="You are …",
        )

    async def process_message(self, message: Message) -> None:
        self.send_message(f"You said: {message.body}")
```

Two ways to reply:

- `self.send_message(markdown_str)` — one complete message.
- `await self.stream_message(async_iterator_of_str)` — stream chunks as they're
  produced (used for progress reporting and for model output).

## The pattern: deterministic commands + model fallback

The Tutor follows a structure worth copying whenever your persona must *do*
things (download, scaffold, report) rather than just talk:

1. **Parse the message for explicit commands first** (`new <topic>`, `list`,
   `help`). When a command matches, execute it **deterministically in Python**
   — never by asking the model to emit a tool call. Local Ollama models
   (especially small ones) are unreliable at function calling; running the
   action yourself makes it work regardless of which model is selected.
2. **Fall back to the configured chat model** for everything else, with your
   persona's system prompt. The user's model choice (Ollama or OpenRouter) is
   read from Jupyternaut's config manager:

   ```python
   cfg = self.parent.serverapp.web_app.settings.get("jupyternaut.config_manager")
   model_id = getattr(cfg, "chat_model", None)         # e.g. "ollama/gemma4:26b-mlx"

   from jupyter_ai_jupyternaut.jupyternaut.chat_models import ChatLiteLLM
   from langchain_core.messages import HumanMessage, SystemMessage

   model = ChatLiteLLM(**cfg.chat_model_args, model=model_id, streaming=True)
   # async-iterate model.astream([...]) and stream_message() the chunks
   ```

3. **Never let the persona crash the chat** — wrap `process_message` in a
   `try/except` and report errors as a message.
4. **Strip the leading `@`-mention** the UI prepends before parsing:

   ```python
   re.sub(r"^(?:\s*@[\w-]+)+\s*", "", message.body or "")
   ```

Other conventions the Tutor demonstrates:

- **Locating the workspace root** from the persona file:
  `Path(__file__).resolve().parents[2]` (the file lives two levels down, in
  `.jupyter/personas/`).
- **Chat is for text; notebooks are for code and rich output.** A persona
  streams markdown into the chat panel — it cannot render plots or run cells.
  When the user needs runnable content, *scaffold a notebook* (copy a template
  `.ipynb`, rewrite a marker line like `TOPIC = …`, write it to the workspace)
  and point them at it. See `_run_new` / `set_topic` in the Tutor.
- **Keep pure logic at module level** (parsing, slug-making, notebook
  rewriting) so it's unit-testable without a running Jupyter server — see
  [`tests/test_tutor_persona.py`](../tests/test_tutor_persona.py).
- **Long-running / blocking work** (HTTP calls, file downloads) should run off
  the event loop: `await asyncio.to_thread(blocking_fn)`.

## Default responder for un-mentioned messages

With several personas loaded, a message with **no** `@`-mention is only routed
if a *default* persona is configured. This repo pins Jupyternaut as the default
in `jupyter_ai_config.py`:

```python
c.PersonaManager.default_persona_id = (
    "jupyter-ai-personas::jupyter_ai_jupyternaut::JupyternautPersona"
)
```

(The upstream default points at a stale id, so without this, bare messages
reach no one.) `@`-mention any other persona to override per-message.

## Avatar

`PersonaDefaults.avatar_path` takes an absolute path to an image; this repo
keeps a small SVG next to the persona file:

```python
AVATAR_PATH = str(Path(__file__).resolve().parent / "tutor_avatar.svg")
```

## Checklist for a new persona

1. Copy `tutor_persona.py` to `.jupyter/personas/<name>_persona.py`.
2. Rename the class, `PersonaDefaults`, system prompt, and avatar.
3. Define your commands in `parse_command` and implement each handler
   deterministically; keep the model fallback for free-form chat.
4. Run `/refresh-personas` in the chat and test each command.
5. Add unit tests for the module-level helpers in `tests/`.

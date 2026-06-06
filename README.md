# Python Workspace

A ready-to-use **JupyterLab + AI** workspace for learning Python development —
local-first, with a built-in AI tutor.

- **One command to start**: `./start.sh` creates the environment, installs
  everything, and opens JupyterLab.
- **AI that runs on your machine**: chat and notebook AI are powered by
  [Jupyter AI](https://jupyter-ai.readthedocs.io/en/v3/) v3 with a local
  [Ollama](https://ollama.com) model by default — no API keys, no cost, and
  nothing you type leaves your computer.
- **Hosted models when you want them**: flip to
  [OpenRouter](https://openrouter.ai) with a single API key for access to
  frontier models (Anthropic, OpenAI, Google, …).
- **A Python tutor in the chat**: the `@Tutor` persona answers learning
  questions and scaffolds ready-to-run practice notebooks for any topic.
- **The data toolkit pre-installed**: `numpy`, `pandas`, `matplotlib`, `scipy`.

## Getting started

1. Install [Ollama](https://ollama.com/download) and pull a model
   (or skip this and use OpenRouter — see
   [SETUP.md](SETUP.md#using-openrouter-instead-of-ollama)):

   ```bash
   ollama pull gemma4:26b-mlx     # repo default (needs ≥36 GB unified memory)
   # lighter machines: ollama pull llama3.2
   ```

2. Launch:

   ```bash
   ./start.sh
   ```

3. In JupyterLab, open **`welcome.ipynb`** and follow the tour. The first time,
   pick your model in **Settings → Jupyternaut Settings** (e.g.
   `ollama/gemma4:26b-mlx`).

The full environment guide — models by machine size, memory tuning, switching
between Ollama and OpenRouter, `%%ai` magics, troubleshooting — is in
**[SETUP.md](SETUP.md)**.

## Learning with the Tutor

The **Tutor** persona lives in this repo
([`.jupyter/personas/tutor_persona.py`](.jupyter/personas/tutor_persona.py)) and
appears automatically in the chat. `@`-mention it:

- `new <topic>` — scaffold a ready-to-run practice notebook for a topic
- `list` — list your practice notebooks
- `help` — command help

Anything else is answered conversationally by the configured model, with a
Python-tutor system prompt.

Example interaction:

> **You**
>
> `@Tutor new list comprehensions`
>
> **Tutor**
>
> Scaffolding a practice notebook for **list comprehensions** …
>
> - ✅ Wrote `practice_list_comprehensions.ipynb` (TOPIC pre-set, 1 cell updated).
>
> **Open it** from the JupyterLab file browser and *Run All*. Its `%%ai` cells
> ask the configured model for an explanation and exercises about your topic;
> solve them in the empty cells that follow.

Each practice notebook (from [`practice_template.ipynb`](practice_template.ipynb))
walks the same loop: **explanation → exercises (no solutions) → your attempts →
AI review**. Re-run the `%%ai` cells for a fresh set, or edit their prompts to
raise the difficulty.

## Two ways to use AI

1. **The chat panel** — `@Jupyternaut` (general assistant; can read/write files
   and work with notebooks, asking permission first) and `@Tutor` (this repo's
   Python tutor).
2. **`%%ai` magics in notebook cells** — generate explanations or code inline:

   ```python
   %load_ext jupyter_ai_magic_commands
   %ai alias gemma ollama/gemma4:26b-mlx

   %%ai gemma -f code
   Write a function that checks whether a string is a palindrome.
   ```

Both use the model selected in **Jupyternaut Settings** — local (`ollama/...`)
or hosted (`openrouter/...`). See [SETUP.md](SETUP.md#usage).

## Build your own AI persona

The Tutor is also a worked example of Jupyter AI's **local persona** mechanism:
drop a `*persona*.py` file into `.jupyter/personas/` and it appears in the chat —
no packaging required. The pattern (deterministic chat commands + a
conversational model fallback, so it works even with small local models) is
documented in **[docs/PERSONAS.md](docs/PERSONAS.md)**.

## What's in here

| Path                         | Purpose                                                        |
| ---------------------------- | -------------------------------------------------------------- |
| `start.sh`                   | One-command launcher (venv, deps, kernel pinning, pre-flight checks) |
| `SETUP.md`                   | Full environment guide (Ollama, OpenRouter, models, tuning)     |
| `welcome.ipynb`              | Guided tour of the workspace                                    |
| `practice_template.ipynb`    | Template the Tutor scaffolds practice notebooks from            |
| `.jupyter/personas/`         | The Tutor persona (+ avatar) — auto-loaded by Jupyter AI        |
| `jupyter_ai_config.py`       | Per-model parameters (context-window cap) + upstream workarounds |
| `docs/PERSONAS.md`           | How to write your own chat persona                              |
| `requirements.txt`           | Dependencies (Jupyter AI v3, JupyterLab, data toolkit)          |
| `requirements.lock.txt`      | Fully pinned versions from a known-good environment             |
| `tests/`                     | Unit tests for the Tutor persona's pure helpers                 |

## Development

Run the tests from the workspace venv:

```sh
.venv/bin/python -m unittest discover -s tests
```

## License

[MIT](LICENSE)

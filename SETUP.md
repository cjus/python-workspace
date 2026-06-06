# Environment Setup — Jupyter AI

> Setup & operation of the Jupyter AI environment for this workspace. For a
> project overview, see [`README.md`](README.md).

A [Jupyter AI](https://jupyter-ai.readthedocs.io/en/v3/) **v3** setup with two
backend options: [Ollama](https://ollama.com) for fully local inference (no
cloud API keys, no data leaving the host) or [OpenRouter](https://openrouter.ai)
for hosted access to a wide range of models via a single API key. Ollama is the
default; OpenRouter is an opt-in alternative.

This setup follows the official Jupyter AI v3 user guide:
<https://jupyter-ai.readthedocs.io/en/v3/users/index.html>

Prefer a hosted model over a local one? See
[Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).

---

## How this setup works (read this first)

A few things to know before you start:

- **Models use [LiteLLM](https://docs.litellm.ai/) IDs** of the form
  `<provider>/<model>` — e.g. `ollama/gemma4:26b-mlx`,
  `openrouter/anthropic/claude-3.5-sonnet`.
- **The chat runs through the Jupyternaut agent.** Jupyter AI ships no model on
  its own; the "pick a provider" chat — including Ollama and OpenRouter — comes
  from the **Jupyternaut** agent, which this repo installs via the
  `[jupyternaut]` extra.
- **Chats are files + AI personas.** Each agent appears as an **AI persona** you
  invoke by `@`-mention (e.g. `@Jupyternaut`, or this repo's `@Tutor`). Chats
  are saved as files in your workspace, so you can reopen and keep several in
  parallel.
- **No slash commands.** There's no `/ask`, `/learn`, or `/generate` — Jupyternaut
  infers intent from your prompt and uses tools/MCP instead. (There's no `/learn`
  RAG feature, so no embedding model is needed.)
- **Optional ACP agents.** Jupyter AI can also connect external coding agents
  (Claude Code, Gemini CLI, Codex, …) over ACP. Those need their own cloud
  accounts/logins, so this repo keeps **Jupyternaut + Ollama** as the local-first
  default. See [ACP agents (optional)](#acp-agents-optional).

---

## What's in here

| File                   | Purpose                                                            |
| ---------------------- | ----------------------------------------------------------------- |
| `requirements.txt`     | Python dependencies (Jupyter AI v3 with the `jupyternaut` + `magics` extras, JupyterLab, the data toolkit) |
| `requirements.lock.txt`| Fully pinned versions captured from the working environment        |
| `jupyter_ai_config.py` | Optional per-model parameters (e.g. the Ollama `num_ctx` cap)      |
| `start.sh`             | Launcher for macOS/Linux (checks Ollama, or continues for OpenRouter if a key is set, then starts Lab) |
| `start.cmd` + `start.ps1` | The same launcher for Windows — run `start.cmd` (it invokes `start.ps1` in a way that works under Windows' default script-execution policy) |
| `.venv/`               | Local virtualenv (git-ignored; created on first install). On Windows the interpreter/activate scripts live under `.venv\Scripts\`, not `.venv/bin/` |

---

## Prerequisites

1. **Python 3.9+** (this environment was built with 3.12). On Windows, install
   from <https://www.python.org/downloads/> or the Microsoft Store — the `py`
   launcher the Windows launcher prefers is included by default. (Careful: on a
   machine without Python, typing `python` opens the Microsoft Store — that's a
   Windows stub, not an install.)
2. **Ollama** installed and running. Install from <https://ollama.com/download>
   (Windows: a native app — `winget install Ollama.Ollama` also works), then
   start the server (it usually runs automatically after install; on Windows it
   autostarts as a tray app, so this step is normally unnecessary):
   ```bash
   ollama serve
   ```
   By default Ollama listens on `127.0.0.1:11434`.
3. At least one **Ollama model** pulled locally (see below).

> **Using OpenRouter instead?** You can skip the Ollama server and local models
> entirely — you only need an **OpenRouter API key**. See
> [Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).

---

## Pull some Ollama models

Jupyter AI references models by the name shown in `ollama list`.

```bash
# Default chat model for this repo on macOS (Apple Silicon, MLX build)
ollama pull gemma4:26b-mlx

# Default on Windows / Linux (standard GGUF build)
ollama pull gemma4:12b

# An alternative, lighter chat model (any OS)
ollama pull llama3.2

# See what you have
ollama list
```

> **Default model:** on Apple Silicon this repo defaults to **`gemma4:26b-mlx`**,
> a 26B model in Apple's MLX format. **MLX builds (`*-mlx` tags) are
> Apple-Silicon-only** — Ollama uses MLX as its Apple Silicon backend and
> llama.cpp (GGUF) everywhere else, so on Windows/Linux pull a standard tag
> instead: **`gemma4:12b`** is the repo's cross-platform default. On lighter
> machines swap in a smaller model from the
> [Ollama library](https://ollama.com/library) (e.g. `llama3.2`, `mistral`,
> `qwen2.5`, `codellama`, `phi3`).

---

## Recommended models

### Local (Ollama) — pick by available memory

**Apple Silicon (macOS).** The model shares **unified memory** with everything
else, so match the model to the machine:

| Machine memory      | Recommended model | Why                                            |
| ------------------- | ----------------- | ---------------------------------------------- |
| **≥ 36 GB**         | `gemma4:26b-mlx`  | 26B, Apple MLX format — the repo default; best quality the hardware can comfortably hold |
| **< 36 GB** (e.g. 16 GB) | `gemma4:e4b`  | Smaller/lighter; runs well where 26B would be too tight |

**Windows / Linux.** `*-mlx` tags won't run here — use the standard GGUF tags.
Ollama runs them on CPU, NVIDIA (CUDA), or AMD (ROCm); size against your GPU
VRAM (or system RAM if CPU-only), keeping roughly 1.5× the model's download
size free:

| Hardware                          | Recommended model       | Why                                  |
| --------------------------------- | ----------------------- | ------------------------------------ |
| **~16 GB RAM** or a ~8 GB GPU     | `gemma4:12b` (~7.6 GB)  | The repo's Windows/Linux default     |
| **≥ 32 GB RAM** or a ≥ 24 GB GPU  | `gemma4:26b` (~18 GB)   | Best quality the hardware can hold   |
| Older / low-memory machines       | `gemma4:e2b-it-qat` (~4.3 GB) or `llama3.2` | Ultra-light, still capable |

Set the choice in Jupyternaut Settings (and, if you want, as the repo default —
see [Switching models](#switching-models)).

### Cloud (OpenRouter) — offload heavier work

To take LLM work off the local machine, use [OpenRouter](#using-openrouter-instead-of-ollama),
where high-end **frontier models** are available on demand. Cost-effective picks:

- **Qwen: Qwen3.7 Max**
- **Google: Gemma 4 31B**

When choosing on OpenRouter, **prefer models that support vision and programming**
(learning Python means lots of code, and often screenshots/plots). If you need
the strongest available models, the **latest from OpenAI, Google, and Anthropic**
are all readily available there too.

> Copy the exact model slug from <https://openrouter.ai/models> and use it as
> `openrouter/<org>/<model>`. See
> [Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).

---

## Running it

Just use the launcher:

```bash
./start.sh     # macOS / Linux
```

```powershell
.\start.cmd    # Windows (PowerShell or cmd; double-clicking it works too)
```

On first run it creates `.venv` and installs the dependencies, then it verifies
Ollama is reachable, lists your models, and opens JupyterLab. No separate install
step is needed.

> **Windows note:** run `start.cmd`, not `start.ps1` directly — Windows' default
> *Restricted* execution policy blocks `.ps1` files, and the `.cmd` shim runs it
> with a process-scoped bypass (your machine's policy is not changed). If you'd
> rather invoke it yourself:
> `powershell -NoProfile -ExecutionPolicy Bypass -File start.ps1`.

> **OpenRouter:** set the key before running the launcher. With it set, the
> launcher treats a missing Ollama server as a warning instead of an error, so
> you can run OpenRouter-only. See
> [Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).
>
> ```bash
> export OPENROUTER_API_KEY="sk-or-..."   # macOS / Linux
> ./start.sh
> ```
>
> ```powershell
> $env:OPENROUTER_API_KEY = "sk-or-..."   # Windows PowerShell
> .\start.cmd
> ```
>
> ```bat
> set OPENROUTER_API_KEY=sk-or-...        # Windows cmd
> start.cmd
> ```

### Manual setup (optional)

If you'd rather not use the launcher — or want the exact pinned versions — set up
the venv yourself.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt          # or requirements.lock.txt for pinned versions
jupyter lab --config=jupyter_ai_config.py
```

**Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1               # blocked? run first:  Set-ExecutionPolicy -Scope Process RemoteSigned
python -m pip install --upgrade pip
pip install -r requirements.txt          # or requirements.lock.txt for pinned versions
jupyter lab --config=jupyter_ai_config.py
```

(In `cmd` use `.venv\Scripts\activate.bat` instead of `Activate.ps1`.)

`requirements.txt` installs `jupyter-ai[jupyternaut,magics]` (the Jupyternaut
agent for the chat + the `%%ai` notebook magics, both backed by LiteLLM) and
JupyterLab, plus the standard data toolkit: `numpy`, `pandas`, `matplotlib`,
and `scipy` — pre-installed so notebooks (and AI-generated code) run without
per-package pip detours.

---

## Usage

There are two ways to use Jupyter AI: the **chat (Jupyternaut persona)** and the
**`%%ai` magic commands** inside notebook cells.

### A. Chat with Jupyternaut (UI)

1. Open a chat: click the **Chat** card on the JupyterLab launcher, or the **+**
   in the chat sidebar panel. (Chats are saved as files in your workspace; reopen
   one anytime, or run several at once.)
2. The first time, configure the model: open **Settings → Jupyternaut Settings**
   and set the **Chat model**:
   - For Ollama, choose the `ollama/` provider and enter the model name, e.g.
     **`ollama/gemma4:26b-mlx`** on Apple Silicon or **`ollama/gemma4:12b`** on
     Windows/Linux (any name from `ollama list`). No API key needed.
   - If Ollama runs on a non-default host/port, set the **`api_base`** field in
     the *Model parameters* section to your address, e.g.
     `http://localhost:11000`.
   - Click **Save**.
3. Type a message and `@`-mention the persona: `@Jupyternaut explain this cell`.
   Jupyternaut replies only when `@`-mentioned (just like a human in a group
   chat). It infers what you want — there are no `/ask` / `/learn` / `/generate`
   slash commands anymore.

> Jupyternaut can read/write files, run shell commands, and work with notebooks
> through the Jupyter MCP server; it asks permission before anything beyond
> reading files in your workspace.

> This repo also ships a local **@Tutor** persona for Python learning — see the
> [README](README.md) and [`docs/PERSONAS.md`](docs/PERSONAS.md).

> To use **OpenRouter** here instead, choose the `openrouter/` provider, enter an
> `openrouter/<org>/<model>` model, and set your API key — see
> [Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).

### B. `%%ai` magic commands (in notebook cells)

Load the extension once per kernel session:

```python
%load_ext jupyter_ai_magic_commands
```

**Local Ollama models need an alias.** The `%%ai` cell magic only accepts models
in LiteLLM's known-model list *or* an alias you register. Local Ollama model
names aren't in that list, so register an alias first, then use it (Windows /
Linux: substitute your non-MLX model, e.g. `ollama/gemma4:12b`):

```python
%ai alias gemma ollama/gemma4:26b-mlx
%%ai gemma
What is a transformer in machine learning? Explain briefly.
```

Format the response as Markdown, code, HTML, math, or an image with `-f`:

```python
%%ai gemma -f code
Write a Python function that returns the nth Fibonacci number.
```

Other helpful magics:

```python
%ai list                       # list providers and known models
%ai list ollama                # list known models for one provider
%ai alias fast ollama/llama3.2 # create another shorthand
%ai dealias fast               # remove an alias
```

> Models already in LiteLLM's list (e.g. `openrouter/...`, `openai/...`) can be
> used directly as `%%ai <provider>/<model>` without an alias.

#### Non-default Ollama host for magics

Either set the `OLLAMA_HOST` environment variable before loading the extension,
or pass `--api-base` when you register the alias:

```python
import os
os.environ["OLLAMA_HOST"] = "http://localhost:11000"
%load_ext jupyter_ai_magic_commands
# or, per-alias:
%ai alias gemma ollama/gemma4:26b-mlx --api-base http://localhost:11000
```

---

## Tuning memory (Ollama context window)

> **Applies to Ollama only.** This whole section is about local memory. It does
> **not** apply to OpenRouter — see [Context on OpenRouter](#context-on-openrouter)
> below.

The biggest memory knob for a **local** chat model is its **context window**
(`num_ctx` in Ollama) — it sizes the KV cache, which is allocated in your
machine's RAM/VRAM on top of the model weights.
This repo caps its default models via `jupyter_ai_config.py` — 128K for the
big-machine defaults, 32K for the 16-GB-class `gemma4:12b`:

```python
c.AiExtension.model_parameters = {
    "ollama/gemma4:26b-mlx": {"num_ctx": 131072},  # macOS default — 128K
    "ollama/gemma4:12b":     {"num_ctx": 32768},   # Windows/Linux default — 32K
    "ollama/gemma4:26b":     {"num_ctx": 131072},  # big Windows/Linux boxes — 128K
}
```

Both launchers load this automatically (`jupyter lab
--config=jupyter_ai_config.py`). LiteLLM passes `num_ctx` straight through to
Ollama. **The keys are matched exactly** — if you switch to a different model,
add/edit a key to match it or no cap applies.

> **Verify it took effect.** After a chat exchange, run `ollama ps` to see the
> loaded context size for the model. If `num_ctx` doesn't appear to apply, set it
> on the Ollama side instead with a Modelfile (guaranteed to work):
>
> ```dockerfile
> FROM gemma4:26b-mlx
> PARAMETER num_ctx 131072
> ```
> ```bash
> ollama create gemma4-128k -f Modelfile   # then use ollama/gemma4-128k
> ```

If memory is still tight, lower `num_ctx` further (each value is in tokens):

| `num_ctx` | Context  | Relative KV-cache memory |
| --------- | -------- | ------------------------ |
| `262144`  | 256K     | highest                  |
| `131072`  | 128K     | repo default             |
| `32768`   | 32K      | ~4× less than 128K       |
| `8192`    | 8K       | smallest practical       |

Notes:
- The keys are matched exactly as `"<provider>/<model>"`, so add an entry per
  model you want to tune (e.g. a separate one for `ollama/llama3.2`).
- The model weights themselves (`gemma4:26b-mlx` is ~16 GB) are fixed; `num_ctx`
  only affects the additional KV-cache memory, not the weights.

You can also set these parameters per-model in **Jupyternaut Settings → Model
parameters** instead of the config file.

### Context on OpenRouter

`num_ctx` is **Ollama-specific** and is ignored by OpenRouter — there's no local
KV cache to size because the model runs on the provider's servers, not your
machine. So there's nothing to "tune for memory" here:

- Each OpenRouter model has a **fixed context window** set by the provider (some
  go up to **~1M tokens**). You can use up to that limit; you don't allocate it.
- The real cost of a big context is **price and latency** (you pay per token),
  not RAM. The knob you'd actually set is **`max_tokens`** (a cap on *output*
  length), not `num_ctx`:

  ```python
  c.AiExtension.model_parameters = {
      "openrouter/anthropic/claude-3.5-sonnet": {"max_tokens": 1024},
  }
  ```

See [Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).

---

## Switching models

There are **two layers** that decide which model the chat actually uses, and a
common gotcha is updating one but not the other:

1. **The active selection** — Jupyternaut saves the model you pick in its
   settings to a machine-local runtime file (this is *not* in the repo):

   ```
   ~/Library/Jupyter/jupyter_ai/config.json          # macOS
   ~/.local/share/jupyter/jupyter_ai/config.json     # Linux
   %APPDATA%\jupyter\jupyter_ai\config.json          # Windows (C:\Users\<you>\AppData\Roaming\...)
   ```

   (If in doubt, `jupyter --paths` prints the data directory the
   `jupyter_ai` folder lives in.)

   Its `"model_provider_id"` (e.g. `"ollama/gemma4:26b-mlx"`) is what loads on
   startup. The repo's `jupyter_ai_config.py` only sets per-model *parameters*
   (like `num_ctx`); it does **not** change which model is selected.

2. **The repo defaults** — `jupyter_ai_config.py`, `start.sh`, and this README.

### To switch the default model (e.g. to `mymodel`)

**Ollama:**

```bash
# 1. Pull it
ollama pull mymodel

# 2. Point the repo's parameter config + docs at it
#    - jupyter_ai_config.py: change (or add) the "ollama/<model>" key
#    - start.sh / start.ps1: update DEFAULT_MODEL (cosmetic — see note below)
```

**OpenRouter:** there's nothing to pull — just use the model ID
`openrouter/<org>/<model>` and make sure `OPENROUTER_API_KEY` is set. See
[Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama).

Then update the **active selection** one of two ways:

- **In the UI (simplest):** open **Settings → Jupyternaut Settings**, choose the
  new model (Ollama or OpenRouter), click **Save**. This rewrites `config.json`.
- **By hand:** edit `config.json` and set `"model_provider_id"` to
  `"ollama/mymodel"` or `"openrouter/org/model"`. Do this only while **JupyterLab
  is not running**, or Lab may overwrite your edit on shutdown.

> **Does the launcher need updating too?** Its `DEFAULT_MODEL` is **not** what
> selects the model — `config.json` (above) is. `DEFAULT_MODEL` only drives the
> startup "available models" message and the *pull-me* hint, so changing it is
> cosmetic; keep it accurate for whichever Ollama model you default to (it lives
> in `start.sh` on macOS/Linux and `start.ps1` on Windows). The launcher *does*
> matter for OpenRouter in one way: set `OPENROUTER_API_KEY` before running
> it, or the Ollama pre-flight check stops the launch.

### Free the old model from memory (Ollama only)

Ollama keeps the previous model resident in RAM/VRAM until its idle timeout.
Check and unload it immediately:

```bash
ollama ps                 # shows what's currently loaded (and its context size)
ollama stop gemma4:26b-mlx   # unload a specific model now
```

OpenRouter is hosted, so there's nothing loaded locally to free.

> **Tip:** if the chat "still loads the old model" after you changed the repo
> files, it's almost always the saved `model_provider_id` in `config.json` (layer
> 1) — update that, then `ollama stop` the old one.

---

## Using OpenRouter instead of Ollama

[OpenRouter](https://openrouter.ai) is a hosted gateway to many models (Anthropic,
OpenAI, Google, Meta, etc.) behind a single API key. Jupyter AI reaches it through
LiteLLM's `openrouter` provider, so you can use it as a drop-in alternative to
Ollama.

> **Heads-up — this is the opposite trade-off from Ollama.** OpenRouter is a
> **cloud** service: it needs an **API key**, it **costs money** (per-token
> billing), and your prompts **leave the machine**. Use it when you want a bigger
> or hosted model; stay on Ollama when you need everything local and free.

No extra install is needed — LiteLLM ships with `jupyter-ai[jupyternaut,magics]`
(see `requirements.txt`).

### 1. Get an API key

Create a key at <https://openrouter.ai/keys> (you'll also need some credit on the
account). The provider reads it from the **`OPENROUTER_API_KEY`** environment
variable.

### 2. Provide the key

- **For the launcher / chat** — set it before starting Lab (keep it out of
  git; the repo already ignores `.env`):

  ```bash
  export OPENROUTER_API_KEY="sk-or-..."   # macOS / Linux
  ./start.sh
  ```

  ```powershell
  $env:OPENROUTER_API_KEY = "sk-or-..."   # Windows PowerShell
  .\start.cmd
  ```

  You can instead paste the key into **Jupyternaut Settings** (Jupyter AI persists
  it to a local secrets/config store, e.g. a `.env` file alongside the workspace
  or `~/Library/Jupyter/jupyter_ai/config.json`).

- **For `%%ai` magics** — set it in the notebook before loading the extension:

  ```python
  import os
  os.environ["OPENROUTER_API_KEY"] = "sk-or-..."
  %load_ext jupyter_ai_magic_commands
  ```

### 3. Pick a model

The model ID is whatever OpenRouter lists (`<org>/<model>`), prefixed with
`openrouter/`. Browse them at <https://openrouter.ai/models>. Examples:

```python
%%ai openrouter/anthropic/claude-3.5-sonnet
Explain a transformer in two sentences.
```

```python
%%ai openrouter/openai/gpt-4o-mini -f code
Write a Python function that returns the nth Fibonacci number.
```

In the **chat**: open **Settings → Jupyternaut Settings → Chat model**, choose
the `openrouter/` provider, enter the model (e.g.
`openrouter/anthropic/claude-3.5-sonnet`), make sure the API key is set, and
**Save**. To make it the persisted default by hand, set
`"model_provider_id": "openrouter/anthropic/claude-3.5-sonnet"` in `config.json`
while Lab is stopped (see [Switching models](#switching-models)).

### Notes

- **Custom base URL** (e.g. a proxy) is optional — set `api_base` in the chat
  *Model parameters* section if needed. The provider defaults to
  `https://openrouter.ai/api/v1`.
- The `num_ctx` setting in `jupyter_ai_config.py` is **Ollama-specific** and does
  nothing for OpenRouter. To pass OpenRouter/OpenAI-style parameters instead, add
  an entry keyed by the OpenRouter model, e.g.:

  ```python
  c.AiExtension.model_parameters = {
      "openrouter/anthropic/claude-3.5-sonnet": {"max_tokens": 1024},
  }
  ```

### Verify it

```bash
# macOS / Linux
export OPENROUTER_API_KEY="sk-or-..."
python - <<'PY'
import litellm
r = litellm.completion(
    model="openrouter/anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content": "Reply with the single word: pong"}],
)
print(r.choices[0].message.content)
PY
```

```powershell
# Windows PowerShell (a here-string piped to python replaces the bash heredoc)
$env:OPENROUTER_API_KEY = "sk-or-..."
@'
import litellm
r = litellm.completion(
    model="openrouter/anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content": "Reply with the single word: pong"}],
)
print(r.choices[0].message.content)
'@ | .venv\Scripts\python.exe -
```

---

## ACP agents (optional)

v3 can also drive external coding agents over the **Agent Client Protocol (ACP)** —
Claude Code, Gemini CLI, Codex, Goose, OpenCode, and others. They appear as
additional AI personas you `@`-mention, and can read/write files and run commands
through the Jupyter MCP server.

This repo stays Ollama/Jupyternaut-first because those agents need their **own
cloud accounts and logins** (the opposite of this environment's local, no-keys
default). If you want one anyway:

1. Install the agent CLI (follow its docs), e.g.
   [Claude Code](https://docs.anthropic.com/en/docs/claude-code/quickstart) or
   [Gemini CLI](https://geminicli.com/docs/get-started/installation/).
2. Install its ACP adapter if required, e.g.
   `npm install -g @zed-industries/claude-agent-acp` (Claude Code) or
   `npm install -g @zed-industries/codex-acp` (Codex).
3. Restart JupyterLab; the agent shows up in the `@`-mention menu. Log in when
   prompted (Jupyter AI opens a terminal for you when possible).

See the v3 [Getting Started](https://jupyter-ai.readthedocs.io/en/v3/getting-started.html)
guide for the full list and details.

---

## Verifying the backend

A quick end-to-end check from the activated venv, without opening Lab:

```bash
# macOS / Linux
python - <<'PY'
import litellm
r = litellm.completion(
    model="ollama/gemma4:26b-mlx",        # uses http://127.0.0.1:11434
    messages=[{"role": "user", "content": "Reply with the single word: pong"}],
)
print(r.choices[0].message.content)
PY
```

```powershell
# Windows PowerShell — note the non-MLX model tag
@'
import litellm
r = litellm.completion(
    model="ollama/gemma4:12b",            # uses http://127.0.0.1:11434
    messages=[{"role": "user", "content": "Reply with the single word: pong"}],
)
print(r.choices[0].message.content)
'@ | .venv\Scripts\python.exe -
```

If you get a reply, Jupyternaut and the `%%ai` magics will work too.

> For an **OpenRouter** check instead, use the
> [Verify it](#verify-it) snippet in the OpenRouter section (it needs
> `OPENROUTER_API_KEY`).

---

## Troubleshooting

| Symptom                                   | Fix                                                                        |
| ----------------------------------------- | -------------------------------------------------------------------------- |
| Ollama / connection errors                | Make sure `ollama serve` is running (Windows: the Ollama tray app) and `curl http://127.0.0.1:11434/api/tags` returns JSON. In *Windows PowerShell*, `curl` is an alias for `Invoke-WebRequest` — use `curl.exe ...` or `Invoke-RestMethod http://127.0.0.1:11434/api/tags`. |
| Model "not found"                         | `ollama pull <model>`; the name after `ollama/` must match `ollama list`.  |
| A `*-mlx` model won't pull / load on Windows or Linux | MLX builds are Apple-Silicon-only. Pull a standard GGUF tag instead (e.g. `gemma4:12b`) and select that in Jupyternaut Settings. |
| Windows: "running scripts is disabled on this system" | You ran `start.ps1` (or `Activate.ps1`) under the default *Restricted* policy. Use `start.cmd`, or `powershell -NoProfile -ExecutionPolicy Bypass -File start.ps1`, or for activation `Set-ExecutionPolicy -Scope Process RemoteSigned`. |
| Windows: `python` opens the Microsoft Store | That's the Windows app-alias stub, not Python. Install Python from python.org/the Store, then use the `py` launcher (`py -3 ...`) — `start.cmd` already prefers it. |
| `@Jupyternaut` doesn't appear in the chat | Confirm `jupyter-ai[jupyternaut]` is installed in the **same** venv running Lab (`pip show jupyter-ai-jupyternaut`). |
| `@Tutor` doesn't appear in the chat       | The persona auto-loads from `.jupyter/personas/`; check the server log for import errors, then run `/refresh-personas` in chat or restart Lab. See `docs/PERSONAS.md`. |
| `%%ai ollama/<model>` says "not a known model or alias" | Register an alias first: `%ai alias gemma ollama/<model>`, then `%%ai gemma`. Local Ollama models aren't in LiteLLM's static list. |
| Custom port not respected                 | Chat: set `api_base` in Model parameters. Magics: set `OLLAMA_HOST` (or `--api-base` on the alias) before `%load_ext`. |
| Slow first response                       | Ollama loads the model into memory on first use; later calls are faster.   |
| Chat keeps loading an old model           | Update `"model_provider_id"` in `jupyter_ai/config.json` (or re-pick + Save in Jupyternaut Settings), then `ollama stop <old-model>`. See [Switching models](#switching-models). |
| OpenRouter auth / `invalid_api_key`       | Set `OPENROUTER_API_KEY` (env var before launch, or the key field in Jupyternaut Settings) and confirm the account has credit. See [Using OpenRouter](#using-openrouter-instead-of-ollama). |

---

## References

- Jupyter AI v3 user guide: <https://jupyter-ai.readthedocs.io/en/v3/users/index.html>
- Jupyter AI v3 getting started: <https://jupyter-ai.readthedocs.io/en/v3/getting-started.html>
- LiteLLM providers: <https://docs.litellm.ai/docs/providers>
- Ollama library: <https://ollama.com/library>
- OpenRouter models: <https://openrouter.ai/models> · API keys: <https://openrouter.ai/keys>

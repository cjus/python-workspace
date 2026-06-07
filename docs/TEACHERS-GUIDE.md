# Teacher's Guide

This guide is for **instructors** running a course with this workspace, and for
**advanced users** who want the technical details. Students don't need anything
in here — the student-facing docs are [`README.md`](../README.md) (the quick
start) and [`SETUP.md`](../SETUP.md) (step-by-step setup and troubleshooting).

**Contents**

- [Before the first class — checklist](#before-the-first-class--checklist)
- [Choosing models for your machines](#choosing-models-for-your-machines)
- [Running a class on OpenRouter](#running-a-class-on-openrouter)
- [Teaching with the Tutor persona](#teaching-with-the-tutor-persona)
- [How the workspace works (under the hood)](#how-the-workspace-works-under-the-hood)
- [Tuning memory (Ollama context window)](#tuning-memory-ollama-context-window)
- [Switching the default model](#switching-the-default-model)
- [Advanced OpenRouter configuration](#advanced-openrouter-configuration)
- [ACP agents (optional)](#acp-agents-optional)
- [Manual environment setup](#manual-environment-setup)
- [Verifying a machine end-to-end](#verifying-a-machine-end-to-end)
- [Repo internals](#repo-internals)
- [Running the tests](#running-the-tests)
- [References](#references)

---

## Before the first class — checklist

The model download is the long pole (4–18 GB per machine), and the first
launcher run installs ~2 GB of Python packages. Do both **before** class, on
classroom bandwidth you control:

1. **Install Python 3.9+** on each machine (3.12 recommended).
   - Windows: python.org installer or Microsoft Store. The `py` launcher
     (installed by default) is what `start.cmd` prefers — it sidesteps the
     "typing `python` opens the Microsoft Store" stub on machines where Python
     isn't really installed.
   - macOS: python.org installer or Homebrew.
2. **Install Ollama** from <https://ollama.com/download>
   (Windows: `winget install Ollama.Ollama` also works; it installs as a tray
   app that autostarts, so students never need to run `ollama serve`).
3. **Pull the model for that machine** (see
   [Choosing models](#choosing-models-for-your-machines)):
   ```bash
   ollama pull gemma4:12b        # the repo default — any OS, ~16 GB machines
   ```
   (Bigger hardware? See [Choosing models](#choosing-models-for-your-machines)
   for larger models and the Apple-Silicon `-mlx` builds.)
4. **Get the repo onto the machine** (git clone, or Download ZIP for students
   who don't have git yet).
5. **Run the launcher once** (`./start.sh` / `start.cmd`) — this creates
   `.venv` and installs all Python dependencies, so first class isn't spent
   watching pip.
6. **Open a chat, set the model** (Settings → Jupyternaut Settings), and send
   `@Tutor help` to confirm the persona loads.
7. **Open `welcome.ipynb` and Run All** — it doubles as a machine check (the
   first cell verifies the environment; the `%%ai` cells verify the model).

> **Low-spec machines?** If the hardware can't hold a local model, run the
> class on OpenRouter instead — see
> [Running a class on OpenRouter](#running-a-class-on-openrouter).

---

## Choosing models for your machines

Two facts drive the choice:

- **Model format is platform-specific.** Ollama uses Apple's **MLX** framework
  as its backend on Apple Silicon and **llama.cpp (GGUF)** on Windows/Linux.
  Tags ending in `-mlx` run *only* on Apple Silicon Macs; on any other machine
  pull a standard tag.
- **Memory is the constraint.** On Apple Silicon the model shares *unified
  memory* with everything else. On Windows/Linux, size against GPU VRAM (or
  system RAM if CPU-only), keeping roughly **1.5× the model's download size**
  free for the model plus its working memory.

The repo default on **every platform** is `gemma4:12b` (~7.6 GB) — it fits a
typical 16 GB machine and is selected automatically on first start. The tables
below are for sizing *up* or *down* from that default.

### Windows / Linux

| Hardware                          | Recommended model       | Why                                  |
| --------------------------------- | ----------------------- | ------------------------------------ |
| **~16 GB RAM** or a ~8 GB GPU     | `gemma4:12b` (~7.6 GB)  | The repo default                     |
| **≥ 32 GB RAM** or a ≥ 24 GB GPU  | `gemma4:26b` (~18 GB)   | Best quality the hardware can hold   |
| Older / low-memory machines       | `gemma4:e2b-it-qat` (~4.3 GB) or `llama3.2` | Ultra-light, still capable |

### Apple Silicon (macOS) — advanced options

`gemma4:12b` (the repo default) runs fine on Apple Silicon. If you want to
push further, the MLX builds use Apple's native framework and run noticeably
faster — but they are **Apple-Silicon-only** and need plenty of unified
memory:

| Machine memory      | Advanced option   | Why                                            |
| ------------------- | ----------------- | ---------------------------------------------- |
| **≥ 36 GB**         | `gemma4:26b-mlx`  | 26B in Apple MLX format — best quality the hardware can comfortably hold |
| **< 36 GB** (e.g. 16 GB) | `gemma4:e4b`  | Smaller/lighter alternative where 26B would be too tight |

After pulling one, select it in **Settings → Jupyternaut Settings** (e.g.
`ollama_chat/gemma4:26b-mlx`).

Browse alternatives at <https://ollama.com/library> (e.g. `llama3.2`,
`mistral`, `qwen2.5`, `codellama`, `phi3`). Explicit quantization tags
(`*-q4_K_M`, `*-q8_0`, `*-qat`) trade quality for memory; skip the
accelerator-specific `-mxfp8` / `-nvfp4` tags for classroom use.

### Cloud (OpenRouter) — offload heavier work

To take LLM work off the local machines entirely, use OpenRouter, where
frontier models are available on demand. Cost-effective picks:

- **Qwen: Qwen3.7 Max**
- **Google: Gemma 4 31B**

Prefer models that support **vision and programming** (a Python course means
lots of code, and often screenshots/plots). The latest from OpenAI, Google, and
Anthropic are all available too. Copy the exact slug from
<https://openrouter.ai/models> and use it as `openrouter/<org>/<model>`.

---

## Running a class on OpenRouter

When local hardware is too weak (or you want one consistent model for
everyone), the workspace runs entirely on [OpenRouter](https://openrouter.ai)
— no Ollama, no model downloads. The student-facing steps are in
[SETUP.md → Using OpenRouter instead of Ollama](../SETUP.md#using-openrouter-instead-of-ollama).
Classroom considerations:

- **Billing is per-token.** A chat-heavy student session on a mid-tier model
  costs cents, not dollars, but budget and monitor it — OpenRouter shows
  per-key usage.
- **Keys:** create **one key per student** (revocable individually, usage
  visible per student) rather than sharing one key. Students put the key in
  `.env` (copy `.env.example`) or paste it into Jupyternaut Settings.
- **Privacy:** unlike local Ollama, prompts leave the machine and are
  processed by the model provider. Check your institution's policy before
  routing student work through a cloud model.
- **The launcher cooperates:** with `OPENROUTER_API_KEY` set, `start.sh` /
  `start.cmd` treat a missing Ollama install as a warning, not an error, so
  OpenRouter-only machines work fine.

---

## Teaching with the Tutor persona

The workspace gives you two complementary teaching assets: the **eight-week
course** in [`lessons/`](../lessons/README.md) (fixed, hand-written, one
~45-minute notebook per week) and the **@Tutor** persona
(`.jupyter/personas/tutor_persona.py`), which generates practice material on
demand. What the Tutor does and how to lean on it:

- **`new <topic>`** scaffolds `practice_<topic>.ipynb` from
  `practice_template.ipynb` with the topic pre-set. The notebook walks
  *explanation → exercises (no solutions) → student attempts → AI review*.
  Natural homework loop: assign `@Tutor new functions`, students submit the
  completed notebook.
- **`list`** shows the course lessons (`lessons/`) plus the practice
  notebooks a student has generated — a quick view of the course and what
  they've covered. (`lessons` works as an alias.)
- **Free-form questions** go to the configured model with a Python-tutor
  system prompt (encouraging, explains *why*, prefers small runnable
  examples).

### Pairing the lessons with practice notebooks

The two halves solve different problems, and the course works best when you
use them together deliberately:

- **Lessons give you a shared sequence.** Everyone covers the same core, in
  the same order, with the same vocabulary — your class time stays anchored,
  and the **🖊️ Your turn** exercises and **🧠 Check yourself** quizzes give
  every student the same baseline reps.
- **Practice notebooks give you differentiation without authoring.** The
  lesson's reps are fixed and finite; the Tutor's are unlimited and targeted.
  A student shaky on loops drills loops; a student who's ahead edits the
  `%%ai` prompt to ask for interview-level problems — neither needs you to
  write a worksheet.
- **The pairing is a spaced-repetition loop.** The lesson introduces the
  concept in class; the practice notebook makes the student *retrieve* it
  days later, with immediate AI review closing the feedback gap before the
  next session. The lesson supplies the topic vocabulary that makes
  `new <topic>` prompts land on-syllabus.

Concrete patterns that work:

- **End every class with an assignment**: "before next week, run
  `@Tutor new <this week's topic>` and complete it." The notebook's *AI
  review* cell gives formative feedback; students submit the completed
  notebook if you want evidence of work.
- **`@Tutor list` as a progress check**: in office hours or while circulating,
  it shows the course plus every practice notebook the student has generated —
  a one-command view of what they've drilled beyond the lessons.
- **Pre-seed weak spots**: after a rough quiz on lesson N, tell specific
  students which `new <topic>` to run — cheaper than re-teaching, and private.

One caveat: generated exercises vary with the model (and run-to-run), so skim
a sample before treating them as graded material — the AI review cell is
formative feedback, not an answer key. For consistent exercises across a
class, standardize the model (see
[Choosing models](#choosing-models-for-your-machines)) or bake fixed
exercises into the template instead.

### Customizing it for your course

- **The system prompt** is the `SYSTEM_PROMPT` string at the top of
  `tutor_persona.py`. Edit it to set your course's tone, vocabulary level, or
  rules ("never give full solutions", "always end with a check-your-
  understanding question"). After editing, run `/refresh-personas` in the chat
  (or restart JupyterLab).
- **The practice template** (`practice_template.ipynb`) is yours to reshape —
  add your course's header, grading rubric cell, or different `%%ai` prompts.
  The Tutor only requires one code line starting with `TOPIC` (it rewrites
  that line when scaffolding).
- **New personas** (a grader, a quiz-master, a project advisor) are single
  Python files dropped into `.jupyter/personas/` — the full how-to, including
  the deterministic-commands + model-fallback pattern the Tutor uses, is in
  [PERSONAS.md](PERSONAS.md).

### A note on command design

The Tutor's commands run **deterministically in Python** the moment they're
recognized — they never depend on the model emitting a correct tool call.
That's deliberate: small local models are unreliable at function calling, and
a classroom can't debug flaky tool use. Only free-form conversation touches
the model. Keep that split if you extend it.

---

## How the workspace works (under the hood)

- **Jupyter AI v3** provides the chat panel and the `%%ai` magics. It ships
  no model of its own; the provider-based chat comes from the **Jupyternaut**
  agent (installed via the `[jupyternaut]` extra in `requirements.txt`).
- **Models use [LiteLLM](https://docs.litellm.ai/) IDs** of the form
  `<provider>/<model>` — e.g. `ollama_chat/gemma4:12b`,
  `openrouter/anthropic/claude-3.5-sonnet`. LiteLLM (not LangChain) is the
  transport for both the chat and the magics.
- **Local models: always the `ollama_chat/` prefix, not `ollama/`.** LiteLLM
  has two Ollama providers: `ollama_chat/` talks to Ollama's native chat API
  (`/api/chat`) with real tool calling, while the older `ollama/` uses
  `/api/generate` and *emulates* tools by instructing the model to answer
  only with a JSON tool call. Jupyternaut binds tools to the chat agent, so
  with `ollama/` every reply arrives as raw
  `{"name": "...", "arguments": ...}` JSON instead of an answer. (The one
  exception: the *embeddings* model keeps the `ollama/` prefix —
  `ollama_chat/` has no embeddings endpoint.)
- **Chats are files + AI personas.** Each agent is an **AI persona** invoked
  by `@`-mention. Chats are saved as files in the workspace, so students can
  reopen them and keep several in parallel. Local personas auto-load from
  `.jupyter/personas/` (see [PERSONAS.md](PERSONAS.md)).
- **No slash commands.** v3 removed `/ask`, `/learn`, `/generate` — Jupyternaut
  infers intent and uses tools/MCP instead. (No `/learn` RAG feature means no
  embedding model is needed.)
- **Jupyternaut can act on the workspace** — read/write files, run shell
  commands, edit notebooks via the Jupyter MCP server — and asks permission
  before anything beyond reading. Worth demonstrating to students once so the
  permission prompts don't surprise them.
- **`%%ai` magics details:** local Ollama models need an alias
  (`%ai alias gemma ollama_chat/<model>`) because they aren't in LiteLLM's
  static model list; `openrouter/...` ids work directly. `-f code|math|html|image`
  formats the output. `%ai list`, `%ai dealias <name>` manage aliases. For a
  non-default Ollama host, set `OLLAMA_HOST` before `%load_ext`, or pass
  `--api-base` when registering the alias.

---

## Tuning memory (Ollama context window)

> Applies to **local Ollama models only** — OpenRouter models run on the
> provider's servers (see [the note below](#context-on-openrouter)).

The biggest memory knob for a local model is its **context window** (`num_ctx`)
— it sizes the KV cache, allocated in RAM/VRAM *on top of* the model weights.
The repo caps its default models in `jupyter_ai_config.py`:

```python
c.JupyternautExtension.model_parameters = {
    "ollama_chat/gemma4:12b":     {"num_ctx": 32768},   # the repo default — 32K
    "ollama_chat/gemma4:26b":     {"num_ctx": 131072},  # big Windows/Linux boxes — 128K
    "ollama_chat/gemma4:26b-mlx": {"num_ctx": 131072},  # Apple-Silicon advanced option — 128K
}
```

(The repo's actual config also registers each cap under the legacy `ollama/`
prefix, so it applies however the id is written.)

Both launchers load this automatically (`jupyter lab
--config=jupyter_ai_config.py`). **Keys are matched exactly** against the
LiteLLM id — if you standardize your class on a different model, add a key for
it or no cap applies.

> **Verify it took effect:** after a chat exchange, `ollama ps` shows the
> loaded context size. LiteLLM does not reliably forward `num_ctx` in all
> versions (BerriAI/litellm#12930, #13904) — if the cap doesn't apply, set it
> on the Ollama side with a Modelfile instead (guaranteed):
>
> ```dockerfile
> FROM gemma4:12b
> PARAMETER num_ctx 32768
> ```
> ```bash
> ollama create gemma4-32k -f Modelfile   # then use ollama_chat/gemma4-32k
> ```

If memory is tight, lower `num_ctx` (values are tokens): `131072` = 128K,
`32768` = 32K (~4× less KV-cache than 128K), `8192` = smallest practical. The
weights themselves are fixed; `num_ctx` only changes the additional cache.
You can also set these per-model in **Jupyternaut Settings → Model
parameters** instead of the config file.

### Context on OpenRouter

`num_ctx` is Ollama-specific and ignored by OpenRouter — there's no local KV
cache to size. Each OpenRouter model has a fixed context window set by the
provider (some up to ~1M tokens); the real cost of a big context is **price
and latency**, not RAM. The knob you'd set is `max_tokens` (output cap):

```python
c.AiExtension.model_parameters = {
    "openrouter/anthropic/claude-3.5-sonnet": {"max_tokens": 1024},
}
```

---

## Switching the default model

**Two layers** decide which model the chat uses; the classic gotcha is
updating one but not the other:

1. **The active selection** — Jupyternaut saves the picked model to a
   machine-local runtime file (NOT in the repo):

   ```
   ~/Library/Jupyter/jupyter_ai/config.json          # macOS
   ~/.local/share/jupyter/jupyter_ai/config.json     # Linux
   %APPDATA%\jupyter\jupyter_ai\config.json          # Windows (C:\Users\<you>\AppData\Roaming\...)
   ```

   (`jupyter --paths` prints the data directory this lives in.) Its
   `"model_provider_id"` is what loads on startup.

2. **The repo defaults** — `jupyter_ai_config.py` (parameters only),
   `start.sh` / `start.ps1` (`DEFAULT_MODEL`, cosmetic: it drives the startup
   message and pull hint, not the selection), and the docs.

To switch a machine: pick the new model in **Settings → Jupyternaut Settings**
and **Save** (this rewrites `config.json`), or edit `config.json` by hand
*while Lab is stopped* (Lab may overwrite it on shutdown). To switch the
*repo* default for your course, also update the `jupyter_ai_config.py` key and
the launcher's `DEFAULT_MODEL`.

**Free the old model from memory (Ollama):** Ollama keeps the previous model
resident until an idle timeout — `ollama ps` to check, `ollama stop <model>`
to unload now. If the chat "still loads the old model" after a switch, it's
almost always the saved `model_provider_id` in `config.json`.

---

## Advanced OpenRouter configuration

(Student-facing OpenRouter setup is in
[SETUP.md](../SETUP.md#using-openrouter-instead-of-ollama).)

- **Custom base URL** (e.g. an institutional proxy): set `api_base` in the
  chat's *Model parameters*; the provider defaults to
  `https://openrouter.ai/api/v1`.
- **Passing OpenAI-style parameters:** key an entry by the OpenRouter model id
  in `jupyter_ai_config.py`, e.g.
  `"openrouter/anthropic/claude-3.5-sonnet": {"max_tokens": 1024}`.
- **Where keys persist:** a key pasted into Jupyternaut Settings is stored in
  the machine-local config/secrets store (e.g. `config.json` above or a `.env`
  alongside the workspace) — relevant for shared lab machines; prefer
  per-student keys and revoke at term end.

---

## ACP agents (optional)

Jupyter AI v3 can also drive external coding agents over the **Agent Client
Protocol (ACP)** — Claude Code, Gemini CLI, Codex, Goose, OpenCode, and
others. They appear as additional `@`-mention personas and can read/write
files and run commands through the Jupyter MCP server.

This repo stays Ollama/Jupyternaut-first because ACP agents need their **own
cloud accounts and logins** — the opposite of a no-keys classroom default. If
you want one anyway:

1. Install the agent CLI (e.g.
   [Claude Code](https://docs.anthropic.com/en/docs/claude-code/quickstart) or
   [Gemini CLI](https://geminicli.com/docs/get-started/installation/)).
2. Install its ACP adapter if required, e.g.
   `npm install -g @zed-industries/claude-agent-acp` (Claude Code) or
   `npm install -g @zed-industries/codex-acp` (Codex).
3. Restart JupyterLab; the agent appears in the `@`-mention menu and prompts
   for login.

See the v3 [Getting Started](https://jupyter-ai.readthedocs.io/en/v3/getting-started.html)
guide for the full list.

---

## Manual environment setup

If you'd rather not use the launchers — or want the exact pinned versions —
set up the venv yourself.

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

`requirements.txt` installs `jupyter-ai[jupyternaut,magics]` + JupyterLab +
the data toolkit (`numpy`, `pandas`, `matplotlib`, `scipy`).
`requirements.lock.txt` is the fully pinned set captured from a known-good
environment — use it when you need every lab machine identical.

---

## Verifying a machine end-to-end

A backend check from the activated venv, without opening Lab:

**macOS / Linux:**

```bash
python - <<'PY'
import litellm
r = litellm.completion(
    model="ollama_chat/gemma4:12b",       # uses http://127.0.0.1:11434
    messages=[{"role": "user", "content": "Reply with the single word: pong"}],
)
print(r.choices[0].message.content)
PY
```

**Windows (PowerShell):**

```powershell
@'
import litellm
r = litellm.completion(
    model="ollama_chat/gemma4:12b",       # uses http://127.0.0.1:11434
    messages=[{"role": "user", "content": "Reply with the single word: pong"}],
)
print(r.choices[0].message.content)
'@ | .venv\Scripts\python.exe -
```

For OpenRouter, set `OPENROUTER_API_KEY` first and use an
`openrouter/<org>/<model>` id. If you get a reply, Jupyternaut and the `%%ai`
magics will work too.

### Troubleshooting beyond the student table

(The student-facing fixes are in
[SETUP.md → When something goes wrong](../SETUP.md#when-something-goes-wrong).)

- **Probe Ollama directly:** `curl http://127.0.0.1:11434/api/tags` should
  return JSON. In *Windows PowerShell*, `curl` is an alias for
  `Invoke-WebRequest` — use `curl.exe ...` or
  `Invoke-RestMethod http://127.0.0.1:11434/api/tags`.
- **`@Jupyternaut` missing from chat:** the `[jupyternaut]` extra isn't in
  the venv running Lab — `pip show jupyter-ai-jupyternaut` to confirm, then
  reinstall from `requirements.txt`.
- **`%%ai ollama_chat/<model>` says "not a known model or alias":** local
  Ollama names aren't in LiteLLM's static list — register an alias first
  (`%ai alias gemma ollama_chat/<model>`), then use `%%ai gemma`.
- **Chat keeps loading an old model after a switch:** the saved
  `model_provider_id` in the machine-local `config.json` wins — see
  [Switching the default model](#switching-the-default-model), then
  `ollama stop <old-model>` to free its memory.
- **Custom Ollama port not respected:** chat — set `api_base` in *Model
  parameters*; magics — set `OLLAMA_HOST` (or `--api-base` on the alias)
  before `%load_ext`.
- **OpenRouter `invalid_api_key`:** key unset in the launching environment or
  the account has no credit — check per-key usage on openrouter.ai.

---

## Repo internals

What the launchers (`start.sh` and its Windows port `start.ps1`, entered via
`start.cmd`) actually do, in order:

1. **Ollama pre-flight** — probe `/api/tags`; fatal unless `OPENROUTER_API_KEY`
   is set (then it's a warning, enabling OpenRouter-only machines). A
   scheme-less `OLLAMA_HOST` (Ollama convention, e.g. `0.0.0.0:11434`) is
   normalized to `http://...`.
2. **Venv bootstrap** — create `.venv` on first run; re-install whenever
   `requirements.txt` is newer than a stamp file
   (`.venv/.requirements-installed`), so added dependencies land in existing
   venvs. Self-healing and idempotent.
3. **Kernelspec pinning** — `ipykernel install --sys-prefix` rewrites the
   kernel's `argv[0]` to the venv's absolute interpreter path. Without this, a
   machine where bare `python` resolves elsewhere (Anaconda, the Windows
   Store stub) silently runs notebooks *outside* the venv with missing
   dependencies — the single most confusing failure mode on student machines.
   Both launchers fail closed if the pin fails.
4. **Jupyternaut presence check** — warns if the `[jupyternaut]` extra is
   missing (no `@Jupyternaut` in chat).
5. **Launch** — `jupyter lab --config=jupyter_ai_config.py` (applies the
   `num_ctx` caps and the persona-routing fixes; see the comments in that
   file for the two upstream workarounds it carries).

Other internals:

- **`start.ps1`** is deliberately ASCII-only and Windows PowerShell
  5.1-compatible (no `&&`/`||`); `start.cmd` runs it with a process-scoped
  `-ExecutionPolicy Bypass` so the default *Restricted* policy doesn't block
  first-time users. Keep `start.sh` and `start.ps1` in behavioral parity when
  editing either.
- **`.gitattributes`** pins line endings: `*.sh`/`*.py`/docs stay LF even
  under `core.autocrlf=true` (a CRLF `start.sh` breaks bash); the Windows
  launchers are stored with verbatim CRLF bytes (`-text`) so even raw GitHub
  downloads get valid files.
- **`.env.example` → `.env`** is the template for the optional
  `OPENROUTER_API_KEY`; `.env` is git-ignored.

---

## Running the tests

The Tutor persona's pure helpers (command parsing, topic slugs, notebook
rewriting) are unit-tested:

```sh
.venv/bin/python -m unittest discover -s tests        # macOS / Linux
.venv\Scripts\python -m unittest discover -s tests    # Windows
```

The tests load the persona by file path and skip (not fail) if the workspace
dependencies aren't installed.

---

## References

- Jupyter AI v3 user guide: <https://jupyter-ai.readthedocs.io/en/v3/users/index.html>
- Jupyter AI v3 getting started: <https://jupyter-ai.readthedocs.io/en/v3/getting-started.html>
- LiteLLM providers: <https://docs.litellm.ai/docs/providers>
- Ollama library: <https://ollama.com/library>
- OpenRouter models: <https://openrouter.ai/models> · API keys: <https://openrouter.ai/keys>

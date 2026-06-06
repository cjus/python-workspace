# Setting up — step by step

This guide gets the workspace running on your computer, even if you've never
programmed before. Follow it top to bottom; each step tells you exactly what
to type or click. (In a hurry? The short version is in the
[README](README.md).)

You'll install two free programs, download an AI model, and start the
workspace. The AI runs **on your own computer** — it's free, it works
offline, and nothing you type is sent to the internet.

> **Teachers & advanced users:** the technical reference (model tuning,
> switching defaults, cloud configuration, how it all works) lives in
> [docs/TEACHERS-GUIDE.md](docs/TEACHERS-GUIDE.md).

**Contents**

1. [Install Python](#1-install-python)
2. [Install Ollama (the AI engine)](#2-install-ollama-the-ai-engine)
3. [Download an AI model](#3-download-an-ai-model)
4. [Start the workspace](#4-start-the-workspace)
5. [Tell the chat which AI to use](#5-tell-the-chat-which-ai-to-use)
6. [Try it out](#6-try-it-out)
7. [Using OpenRouter instead of Ollama](#using-openrouter-instead-of-ollama) (optional — cloud AI)
8. [When something goes wrong](#when-something-goes-wrong)

---

## 1. Install Python

Python is the programming language you're here to learn.

- **Windows:** install from <https://www.python.org/downloads/> (or the
  Microsoft Store). The defaults are fine.
  > Careful: on a computer *without* Python, typing `python` opens the
  > Microsoft Store — that's a Windows shortcut, not Python itself. Install it
  > first, and you'll never hit this.
- **macOS:** install from <https://www.python.org/downloads/>. The defaults
  are fine.

Any Python from 3.9 up works (3.12 recommended).

## 2. Install Ollama (the AI engine)

[Ollama](https://ollama.com) is the free app that runs AI models on your own
computer.

- Download it from <https://ollama.com/download> and install it like any other
  app.
- **Windows:** after installing, Ollama starts automatically and sits in your
  system tray — nothing else to do.
- **macOS:** after installing, Ollama runs in the menu bar. If it ever isn't
  running, open the Ollama app (or run `ollama serve` in a terminal).

## 3. Download an AI model

A "model" is the AI brain Ollama runs. You download it once; after that it
works offline. **It's a big download (4–18 GB)** — use good Wi-Fi and give it
time.

Open a terminal (**Windows:** press Start, type `powershell`, press Enter.
**macOS:** open the *Terminal* app) and type the line for your computer:

```bash
# Mac with Apple Silicon (M1/M2/M3/M4) and 36 GB+ memory:
ollama pull gemma4:26b-mlx

# Windows or Linux (most machines — this is the usual choice):
ollama pull gemma4:12b

# Older or low-memory machine (any OS) — smaller and faster to download:
ollama pull llama3.2
```

Not sure which? `gemma4:12b` is a safe choice on Windows/Linux; on a smaller
Mac use `gemma4:e4b`. (Why different models per machine? Short answer: Macs
and PCs use different model formats, and bigger models need more memory — the
full story is in the
[Teacher's Guide](docs/TEACHERS-GUIDE.md#choosing-models-for-your-machines).)

## 4. Start the workspace

First, get this folder onto your computer if you haven't already (your teacher
may have done this for you): on the GitHub page click **Code → Download ZIP**
and unzip it, or use `git clone` if you know git.

Then start it:

- **Windows:** double-click **`start.cmd`** in the folder. (Or, in PowerShell:
  `cd` into the folder and run `.\start.cmd`.)
- **macOS / Linux:** open Terminal, `cd` into the folder, and run:
  ```bash
  ./start.sh
  ```

**The first run takes a few minutes** — it sets up a private Python
environment and downloads the tools it needs (about 2 GB). You'll see lots of
text scroll by; that's normal. When it's done, **JupyterLab opens in your web
browser** — that's the workspace.

Every time after that, the same command starts in seconds.

> Windows may show "running scripts is disabled" if you run `start.ps1`
> directly — use **`start.cmd`** instead; it exists exactly to avoid that.

## 5. Tell the chat which AI to use

One-time setting:

1. In JupyterLab, open the **Settings** menu (top of the window) and choose
   **Jupyternaut Settings**.
2. In the **Chat model** field, type `ollama/` followed by the model you
   downloaded in step 3. For example:
   - `ollama/gemma4:26b-mlx` (Apple Silicon Mac)
   - `ollama/gemma4:12b` (Windows / Linux)
3. Click **Save**.

That's it — no account, no API key. (If you forget what you downloaded, type
`ollama list` in a terminal.)

## 6. Try it out

1. **Open `welcome.ipynb`** from the file list on the left and follow it —
   it checks your setup and walks you through everything below. Click a cell
   and press **Shift+Enter** to run it.
2. **Open a chat:** click the **Chat** card on the launcher (or the chat icon
   in the left sidebar) and say hello:
   - `@Tutor what is a variable?` — your AI Python tutor
   - `@Tutor new variables` — creates a practice notebook just for you
   - `@Jupyternaut what does this error mean?` — the general assistant
3. The first reply can take a little while (the model is loading into
   memory); after that it's faster.

You can also ask the AI from inside a notebook with the `%%ai` magic —
`welcome.ipynb` shows you how.

---

## Using OpenRouter instead of Ollama

*Optional.* If your computer is too small for a local model — or your teacher
gave you an **OpenRouter key** — the workspace can use a cloud AI instead.

> The trade-off: OpenRouter needs an account and **costs money per use**, and
> what you type **is sent over the internet** to the model provider. Ollama is
> free and private; OpenRouter gives you bigger models on weak hardware.

1. **Get a key.** Your teacher may give you one. Otherwise create one at
   <https://openrouter.ai/keys> (the account needs some credit).
2. **Give the workspace the key.** Easiest: copy the file `.env.example` to
   `.env` (same folder) and paste your key after `OPENROUTER_API_KEY=`.
   You can also paste it into **Settings → Jupyternaut Settings** instead.
3. **Pick a cloud model** in **Settings → Jupyternaut Settings → Chat
   model**: choose the `openrouter/` provider and enter a model id like
   `openrouter/anthropic/claude-3.5-sonnet` (browse ids at
   <https://openrouter.ai/models>), then **Save**.

With the key set, the launcher works even if Ollama isn't installed at all.
(Setting the key as an environment variable, custom endpoints, and per-model
options are covered in the
[Teacher's Guide](docs/TEACHERS-GUIDE.md#advanced-openrouter-configuration).)

---

## When something goes wrong

| What you see                                   | What to do                                                              |
| ---------------------------------------------- | ----------------------------------------------------------------------- |
| `ERROR: Ollama server not reachable`           | Ollama isn't running. Open the Ollama app (Windows: check the system tray; macOS: the menu bar), then run the launcher again. |
| "running scripts is disabled on this system" (Windows) | You ran `start.ps1` directly. Use **`start.cmd`** instead.       |
| Typing `python` opens the Microsoft Store (Windows) | Python isn't installed yet — do [step 1](#1-install-python). The launcher uses the right Python automatically once it's installed. |
| The chat never replies / "model not found"     | The model name in **Settings → Jupyternaut Settings** must exactly match one from `ollama list` (with `ollama/` in front). Fix it and **Save**. |
| A model ending in `-mlx` won't download or run | `-mlx` models are for Apple Silicon Macs only. On Windows/Linux use `gemma4:12b` (see [step 3](#3-download-an-ai-model)). |
| The first reply takes forever                  | Normal — the model is loading into memory. Later replies are faster.    |
| A notebook says a package is missing (`numpy`, `pandas`, …) | Run the launcher again (it installs anything missing), then in the notebook menu pick **Kernel → Restart Kernel**. |
| `@Tutor` doesn't appear in the chat            | Restart the launcher. If it still doesn't appear, tell your teacher — the server log will say why (see the [Teacher's Guide](docs/TEACHERS-GUIDE.md)). |
| Download is huge / slow                        | Yes — models are 4–18 GB. Use good Wi-Fi, start it before a break, and only pull one model. |

Still stuck? Ask your teacher, or open an issue on the repo — include the
exact message you saw.

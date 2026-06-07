# 🐍 Python Workspace

Learn Python with a friendly AI tutor — right on your own computer.

This is a ready-made workspace for learning Python. It gives you:

- **A place to write and run Python** — [JupyterLab](https://jupyter.org)
  opens in your web browser; you write code in *notebooks* and run it with
  Shift+Enter.
- **An AI tutor in the chat** — ask **@Tutor** anything about Python, and it
  can create practice notebooks on any topic, just for you.
- **AI that's free and private** — by default the AI runs *on your computer*
  (via [Ollama](https://ollama.com)): no account, no cost, and nothing you
  type leaves your machine. (A cloud option exists too, if you want it.)
- **The everyday Python libraries pre-installed** — `numpy`, `pandas`,
  `matplotlib`, `scipy` — so examples from tutorials just work.

No programming experience needed — that's what you're here to get.

## Get started

Three steps, all spelled out click-by-click in **[SETUP.md](SETUP.md)**:

1. **Install two free programs** — Python and Ollama — then download an AI
   model (one command; it's a big download, so give it time).
2. **Start the workspace:**

   ```bash
   ./start.sh      # macOS / Linux
   .\start.cmd     # Windows (double-clicking start.cmd works too)
   ```

   The first run sets everything up (a few minutes); after that it starts in
   seconds. JupyterLab opens in your browser.
3. **Open `welcome.ipynb`** in JupyterLab and follow along — it checks your
   setup and gives you the tour.

If anything doesn't work, the fix is almost certainly in
[SETUP.md → When something goes wrong](SETUP.md#when-something-goes-wrong).

## The eight-week course

Want a structured path instead of wandering? **[`lessons/`](lessons/README.md)**
is a complete beginner course: eight notebooks, one ~45-minute session per
week, from "what is Python?" to building your first small program. Lesson 1
is a light tour of the whole course, so you can decide after a single session
whether it's for you.

## Meet your tutor

Open a chat (the **Chat** card on the JupyterLab launcher) and talk to
**@Tutor**:

- Ask anything: `@Tutor what's the difference between a list and a tuple?`
- Get a practice notebook: `@Tutor new loops`
- See the course lessons and your notebooks: `@Tutor list`

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
> **Open it** from the JupyterLab file browser and *Run All*.

Each practice notebook walks the same loop: **explanation → exercises → your
attempts → AI review**. Run the AI cells again any time for a fresh set, or
ask for harder ones.

**Lessons and practice notebooks are two halves of one loop.** The
[`lessons/`](lessons/README.md) course is the fixed path — the same eight
hand-written notebooks for everyone, in order. Practice notebooks are the
opposite: generated on demand, about whatever *you* need more reps on, as
many as you like. A good rhythm: finish a lesson, then
`@Tutor new <something from that lesson>` for extra practice before the next
session. Lessons teach; practice notebooks make it stick.

There's also **@Jupyternaut**, the general assistant — great for *"what does
this error mean?"* — and you can ask the AI from inside any notebook with the
`%%ai` magic (the welcome notebook shows you how).

## What's in this folder

| You'll use…                  | What it is                                              |
| ---------------------------- | ------------------------------------------------------- |
| `start.sh` / `start.cmd`     | Starts everything (macOS-Linux / Windows)               |
| `welcome.ipynb`              | The guided tour — start here                            |
| `lessons/`                   | The eight-week beginner course (start with lesson 01)   |
| `SETUP.md`                   | Click-by-click setup help and fixes                     |
| `practice_…ipynb` notebooks  | Your practice notebooks (made by @Tutor)                |

| Behind the scenes…           |                                                         |
| ---------------------------- | ------------------------------------------------------- |
| `practice_template.ipynb`    | The template @Tutor copies for practice notebooks       |
| `.jupyter/personas/`         | The Tutor itself — a small Python program you can read  |
| `requirements*.txt`, `jupyter_ai_config.py`, `start.ps1` | Environment plumbing — the launcher handles these |
| `docs/`, `tests/`            | Guides for teachers & tinkerers, and the test suite     |

## For teachers and tinkerers

- **[docs/TEACHERS-GUIDE.md](docs/TEACHERS-GUIDE.md)** — classroom setup
  checklist, choosing models for your machines, running a class on a cloud
  model, customizing the Tutor for your course, and all the technical
  reference (memory tuning, model switching, how the launchers work, tests).
- **[docs/PERSONAS.md](docs/PERSONAS.md)** — build your own AI chat persona
  (the Tutor is a worked example you can copy).

## License

[MIT](LICENSE)

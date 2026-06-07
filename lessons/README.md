# 🐍 The eight-week Python course

A beginner course in eight notebooks — one ~45-minute session per week. No
programming experience needed; everything runs in this workspace.

**Start with Lesson 1.** It's a light tour of Python and of the whole course,
so you can decide after one session whether you want to continue — no harm
done either way.

## The schedule

| Week | Notebook | What you'll learn |
| ---- | -------- | ----------------- |
| 1 | [Welcome to Python](01-welcome-to-python.ipynb) | What Python is, run your first code, tour of the course — and an honest "is this for you?" |
| 2 | [Variables & Data](02-variables-and-data.ipynb) | Variables, numbers, text and f-strings, types and conversions |
| 3 | [Making Decisions](03-making-decisions.ipynb) | Booleans, comparisons, `if`/`elif`/`else`, `and`/`or`/`not`, `while` loops |
| 4 | [Lists & Loops](04-lists-and-loops.ipynb) | Lists, `for` loops, `range`, and the everyday loop patterns (sum, count, find, build) |
| 5 | [Functions](05-functions.ipynb) | `def`, parameters, `return` vs `print`, docstrings, importing modules |
| 6 | [When Things Go Wrong](06-when-things-go-wrong.ipynb) | Reading error messages, debugging strategies, and `try`/`except` |
| 7 | [Files & Real Data](07-files-and-real-data.ipynb) | Reading and writing files with `open`, and parsing simple comma-separated data |
| 8 | [Dictionaries & Your First Project](08-dictionaries-and-mini-project.ipynb) | Dictionaries, plus a quiz-game capstone that uses everything — and where to go next |

> Why these eight? Weeks 2–5 are the universal core every intro course
> teaches. Weeks 6–7 (errors and files) are the two topics benchmark courses
> — Harvard's CS50P, MIT 6.0001, *Automate the Boring Stuff* — and the
> ACM/IEEE curriculum guidelines all treat as essential first-course
> material. Classes/OOP, comprehensions, and the like are deliberately left
> for after the course.

## How to use a lesson

1. Start the workspace (`./start.sh` — Windows: `start.cmd`) and open the
   week's notebook from this folder.
2. Run the cells top to bottom with **Shift+Enter**, editing and re-running
   as you go — the notebooks are meant to be tinkered with.
3. Do the **🖊️ Your turn** exercises as you reach them; check the
   **🧠 Check yourself** quiz at the end.
4. Between classes (optional): ask the tutor in the chat panel —
   `@Tutor new <topic>` scaffolds a practice notebook on anything from that
   week. See the [README](../README.md) for more on the tutor.

> **Lessons vs. practice notebooks:** these eight lessons are the fixed
> course — hand-written, the same for everyone, done in order. Practice
> notebooks are AI-generated drills made just for you, on demand, on any
> topic — create as many as you like; they never change the course itself.
> `@Tutor list` in the chat shows both.

## For instructors

- Each notebook is one 45-minute session, with rough per-section pacing hints
  in the headings. Lesson 1 is deliberately light — it's the "decide if this
  course is for you" session.
- Every notebook runs top-to-bottom offline with no setup beyond the
  workspace itself (the `input()` demos are commented out so *Run All* never
  stalls; uncomment them for live play in class).
- Lessons 7 and 8 create small `.txt` data files in this folder as part of
  the exercises — that's expected (and they're git-ignored).
- Classroom setup, model choices, and customizing the Tutor:
  [docs/TEACHERS-GUIDE.md](../docs/TEACHERS-GUIDE.md).

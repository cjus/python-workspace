# User Journey

*A product-manager's map of how a real person travels through this workspace —
from first encounter to finished course — and where they delight, stumble, or
quit.* Last reviewed: June 2026 — backlog items addressed June 2026; see the
Status column in [Gap analysis & opportunity backlog](#gap-analysis--opportunity-backlog).

This document is for the **maintainer** and **future contributors/teachers**.
It is not a student doc and not a teacher doc — those are
[`../README.md`](../README.md), [`../SETUP.md`](../SETUP.md), and
[`./TEACHERS-GUIDE.md`](./TEACHERS-GUIDE.md). This one thinks in *journeys,
friction, and a prioritized backlog*. Every claim below is grounded in a file
in this repo (cited inline) or in published research (cited in
[What the research says](#what-the-research-says)).

A through-line runs under the whole map: **drop-off science**. Self-paced
online courses complete at roughly 7–13%; attrition concentrates around the
2/3 point; the strongest single predictor of completion is *active
participation in week 1*; and help-seeking is *negatively* correlated with
quitting. So the recurring question at each stage is: **does this stage earn an
"it worked!" moment, and does it pull the learner toward week 2?**

---

## Contents

- [The learner personas](#the-learner-personas)
- [The journey map](#the-journey-map)
  - [Stage 0 — Discover](#stage-0--discover)
  - [Stage 1 — Set up](#stage-1--set-up)
  - [Stage 2 — First session (welcome.ipynb)](#stage-2--first-session-welcomeipynb)
  - [Stage 3 — The weekly lesson loop](#stage-3--the-weekly-lesson-loop)
  - [Stage 4 — Between-class @Tutor practice](#stage-4--between-class-tutor-practice)
  - [Stage 5 — Capstone (week 8)](#stage-5--capstone-week-8)
  - [Stage 6 — After the course](#stage-6--after-the-course)
- [The core AI interaction loop](#the-core-ai-interaction-loop)
- [What the research says](#what-the-research-says)
- [Gap analysis & opportunity backlog](#gap-analysis--opportunity-backlog)
- [Unused Jupyter AI features (free wins)](#unused-jupyter-ai-features-free-wins)
- [What already works — delights to preserve](#what-already-works--delights-to-preserve)
- [Success metrics](#success-metrics)
- [Baselines, targets & validation](#baselines-targets--validation)

---

## The learner personas

Three personas, built from what the docs actually promise and the code
actually does. The same human is often #1 and #2 at different moments.

### 1. Maya — the solo at-home beginner *(PRIMARY)*

A zero-experience adult who found the repo and wants the structured eight-week
course. She works **alone**, evenings and weekends, with **no instructor in
the room**. She is the README's literal audience: *"No programming experience
needed — that's what you're here to get"* ([`../README.md`](../README.md):18)
and *"no grades, nothing to hand in."*

Because she has no teacher, Maya hits every gap that quietly assumes one:
- the capstone game whose real interactive version is *commented out* "to play
  live in class" (`lessons/08-…`:cell `ec677d7d`),
- the "Your turn" exercises with **no answer key** to check herself against,
- the "copy the lines into a new cell" debugging pattern, when Lesson 1 only
  ever taught her Shift+Enter.

Maya is the drop-off-science archetype: she is the one the weeks-2–3 attrition
cliff claims unless every early lesson hands her a win.

### 2. Sam — the non-technical setter-upper *(SECONDARY; often Maya at t=0)*

Has never opened a terminal. Sam lives or dies in the
**README → SETUP → launcher → welcome.ipynb** corridor. He feels every step of
time-to-first-success: install Python, install Ollama, pull a multi-GB model,
run a launcher that downloads ~2 GB more and builds a venv, then maybe pick a
model. On macOS he meets the unexplained `cd` jargon; on Windows
`start.cmd`'s double-click smooths most of it. He is the one the launcher's own
closing tip can mislead.

### 3. Mr. Lee — the volunteer teacher / club facilitator *(TERTIARY, supporting)*

Runs the course for a small cohort. Reads
[`./TEACHERS-GUIDE.md`](./TEACHERS-GUIDE.md) and
[`./PERSONAS.md`](./PERSONAS.md), and may edit the `SYSTEM_PROMPT` in
[`../.jupyter/personas/tutor_persona.py`](../.jupyter/personas/tutor_persona.py).
He cares about the homework loop (`@Tutor new <topic>`), classroom presence,
and whether the AI is *pedagogically* sound. Conveniently, most high-leverage
AI fixes land in his lap as edits to **one readable Python file**.

---

## The journey map

Each stage notes: **what the learner does**, **touchpoints**, the
**emotional curve**, **delights**, **friction & drop-off risk**, and
**opportunities**.

### Stage 0 — Discover

**Who:** Sam / Maya. **Touchpoints:** [`../README.md`](../README.md).
**Emotional curve:** curious → reassured → motivated.

**What they do:** read the front door and decide whether this is for them.

**Delights (preserve verbatim):** The opening line lands the value prop with
zero jargon — *"Learn Python with a friendly AI tutor — right on your own
computer"* — and the tagline preempts the #1 fear (*"No programming experience
needed — that's what you're here to get"*). Every term that could block a
beginner (notebook, JupyterLab, Ollama, libraries) is glossed on first use
([`../README.md`](../README.md):7–18). The course is offered as an explicit
*choice* with a graceful exit, which lowers the cost of trying. This stage is
doing real conversion work; it is the strongest part of the funnel.

**Friction:** minimal. The conversion job here is essentially done.

**Opportunity:** none urgent — protect it from regression.

### Stage 1 — Set up

**Who:** Sam. **Touchpoints:** [`../SETUP.md`](../SETUP.md),
[`../start.sh`](../start.sh) / `start.cmd` / `start.ps1`, first downloads.
**Emotional curve:** willing → daunted (big download) → reassured ("slow is
normal") → *(risk: confused/abandon)* → relieved when JupyterLab opens.

**What they do:** install Python, install Ollama, `ollama pull gemma4:12b`
(~7.6 GB), run the launcher (venv + ~2 GB of packages), optionally pick a
model, open `welcome.ipynb`. This is **5–6 strictly serial, gated steps with
two large downloads back-to-back** before anything visible happens.

**Delights (preserve):**
- The big, slow downloads are framed *up front* and paired with coping advice —
  *"models are 4–18 GB. Use good Wi-Fi, start it before a break, and only pull
  one model"* ([`../SETUP.md`](../SETUP.md):180) — so a stall reads as expected,
  not as failure. Same care for first-reply latency
  ([`../SETUP.md`](../SETUP.md):132–133, 177).
- Windows/mac launcher parity is genuinely engineered: `start.cmd` is a thin
  documented shim that defuses the PowerShell execution-policy wall, and both
  README and SETUP give the two commands side by side. The "typing `python`
  opens the Microsoft Store" trap is pre-empted ([`../SETUP.md`](../SETUP.md):36).

**Friction & drop-off risk:**
- **BLOCKER — the launcher contradicts the docs on the model prefix.** The last
  line both launchers print before JupyterLab opens steers the learner to the
  *broken* `ollama/` prefix: *"Pick the model in Settings → Jupyternaut
  Settings (e.g. `ollama/gemma4:12b`)"* ([`../start.sh`](../start.sh):102,
  `start.ps1`:179). But [`../SETUP.md`](../SETUP.md):114–117 and the
  troubleshooting row at :174 explicitly warn that `ollama/` yields raw
  `{"name": …, "arguments": …}` JSON and you **must** use `ollama_chat/`. The
  tool's own output overrides the doc the learner just read.
- **macOS terminal jargon.** SETUP says *"open Terminal, `cd` into the folder,
  and run `./start.sh`"* ([`../SETUP.md`](../SETUP.md):87–90) with `cd` never
  defined — the single biggest unexplained step for someone who has never
  opened a terminal. Windows gets "double-click `start.cmd`"; mac has no
  double-click equivalent. The OS-parity gap falls precisely on the
  least-technical persona.
- **Two silent runtime blockers.** Neither launcher checks **RAM** before
  recommending a 12B model, so an under-resourced machine produces a frozen
  chat — and the "first reply takes forever / normal"
  ([`../SETUP.md`](../SETUP.md):177) framing actively tells the learner to keep
  waiting on a hang. Separately, a busy **port 8888** has no handling or
  troubleshooting row; the launcher just `exec`s Lab.
- **Long, serial TTFS.** The two big downloads run back-to-back with no hint
  they could overlap. The default's real size — `gemma4:12b` ~7.6 GB
  ([`./TEACHERS-GUIDE.md`](./TEACHERS-GUIDE.md):78) — is never shown to the
  learner in SETUP, which only gives the "4–18 GB" worst-case range
  ([`../SETUP.md`](../SETUP.md):58, 180), so learners over-estimate.

**Opportunities:** flip both launcher tips to `ollama_chat/`; add a one-line
mac `cd` explainer (or ship a double-clickable launcher); add a RAM warning and
a port-in-use row + retry; note that the model pull and launcher run can happen
in parallel and state the default's real size.

### Stage 2 — First session (welcome.ipynb)

**Who:** Maya. **Touchpoints:** `welcome.ipynb`. **Emotional curve:**
nervous → *delight (green checkmarks)* → mild overwhelm (`%%ai` jargon) →
*(risk: "now what?")*.

**What they do:** open `welcome.ipynb`, Run All, get the tour. This is the
**hinge from tour-taker to course-taker.**

**Delight (preserve):** The first "it worked!" is an **AI-free environment
check** that prints green checkmarks for numpy/pandas/etc. — the first win is
*decoupled from the slow Ollama path*, so the learner succeeds before touching
the part most likely to be slow or misconfigured. Emotionally well-designed.

**Friction & drop-off risk:**
- **The tour never hands off to the course it promised.** The "Next steps" cell
  (`welcome.ipynb` cell `next-md`) points only to `@Tutor new variables and
  types`, SETUP, the Teacher's Guide, and PERSONAS — there is **no link to
  `lessons/` or Lesson 1**. (Verified: zero occurrences of `lessons/` anywhere
  in `welcome.ipynb`.) A learner who came specifically for the structured
  course — promised in [`../README.md`](../README.md):41–47 — finishes the tour
  with no signpost into it. This is a UI-only gap: the Tutor's own
  `SYSTEM_PROMPT` already knows the course lives in `lessons/01-…`
  ([`../.jupyter/personas/tutor_persona.py`](../.jupyter/personas/tutor_persona.py):82–85).
- **`%%ai` magic is a jargon spike** introduced right after the gentle env
  check.

**Opportunity:** add a first bullet to the next-steps cell — *"Take the course:
open `lessons/01-welcome-to-python.ipynb`."* Cheap, high-leverage conversion.

### Stage 3 — The weekly lesson loop

**Who:** Maya. **Touchpoints:** [`../lessons/README.md`](../lessons/README.md)
and `lessons/01…08`. **Emotional curve, week by week:** momentum →
*(weeks 3–4 cognitive overload)* → *(week 6 motivation cliff)* → earned pride
(week 8). This is the eight-week spine and **where the gaps cluster.**

**What they do:** one ~45-minute notebook per week, run top-to-bottom with
Shift+Enter, do the **🖊️ Your turn** exercises, check the
**🧠 Check yourself** quiz.

**Delights (preserve):**
- **The core in-notebook loop** — read → run a demo → "Your turn" TODO →
  "Fix the bug" → collapsible "Check yourself" reveal. The `<details><summary>`
  reveal-quiz pattern appears in **all of lessons 2–8** (4 per lesson) and is
  exactly the model the bare Your-turn cells should adopt.
- **The week-to-week spiral.** Every lesson opens with a "last week / today"
  recap and closes with a teaser; later lessons tag where each ingredient came
  from, so progress feels cumulative and the capstone feels earned.
- **Lesson 1 onboarding tone.** Instant Hello-world win, explicit
  no-tests/no-grades framing, "you can't break anything" + how to restart the
  kernel, and an honest "is this for you?" with a graceful exit. The strongest
  motivational asset in the course.

**Friction & drop-off risk:**
- **BLOCKER for the solo learner — no answer key on "Your turn".** The hands-on
  exercises have no answer, assert, or reveal. Maya literally cannot confirm
  she got it right. Example: the Lesson 2 bill-splitter (`lessons/02-…` cell
  `3c6c7c71`) prints with no expected value. The right pattern *already exists
  inconsistently* — Lesson 5 embeds `# should print 20` and `# should be 32.0`
  target comments (`lessons/05-…`), and every "Check yourself" quiz is a
  collapsible answer. Standardize a "should be X" / collapsible answer on every
  Your-turn across all eight lessons. This is the highest-impact learner-facing
  gap.
- **STRUCTURAL — the headline AI features are never used in-flow.** @Tutor,
  @Jupyternaut, and `%%ai` *define* this workspace, yet **zero `%%ai` cells
  appear in any lesson body** (verified across all eight notebooks), and AI is
  only mentioned in optional *"After class (optional)"* footers
  ([`../lessons/README.md`](../lessons/README.md):38–40; e.g. `lessons/05-…`
  ends with `@Tutor new functions`). A footer-skipper can finish all eight
  weeks and never use the product's reason for existing. *(In-flow framing
  addressed June 2026 — see Status, backlog #3: every lesson body 02–08 now
  carries one mandatory "🤖 Ask your tutor" moment; live `%%ai` cells stay
  commented by design to keep Run-All offline.)*
- **The week-6 motivation cliff.** Lesson 6 has **no chart or game payoff**
  (verified: 0 matplotlib/plot cells — true of lessons 2–7, but it matters most
  here), centers on red error text, and its longest section is
  `## 4. try / except … (~15 min)`. Its one copy-and-fix bug hunt
  (`lessons/06-…` markdown `91a79e20` / code cell `b45a54d4`, the
  `count_long_words` snippet) plus a fill-in-TODO "Your turn" (`aed0a850`,
  `safe_divide`) keep the whole session in error-handling territory. It lands
  exactly where drop-off science says motivation sags. The "errors are not
  failures" reframe is good, but the session ends visually unrewarding.
- **Lessons 3 & 4 are overstuffed for 45 minutes.** Lesson 3 packs booleans,
  comparisons, `if/elif/else`, `and/or/not`, and `while` into sections summing
  to ~41 min before slack (`## 2.`–`## 5.` = 8+14+7+10). Lesson 4 even labels
  itself a "big one" and crams lists, `for`, `range`, and four loop patterns
  into 2+12+12+12+3 min covering ~10 ideas. No slack for a slower learner.
- **Fix-the-bug is a retype-from-comments chore.** The bug exercises ask the
  learner to retype/uncomment the broken lines in the editable area *already
  provided in the same cell* and remove the `#` marks (`lessons/04-…` cell
  `c30d84bf`, `lessons/06-…` cell `b45a54d4`, `lessons/07-…` cell `409f5f43`;
  each ships a TODO placeholder + runnable `print(...)`). So no new-cell skill
  is strictly required — but it is still fiddly, and worth noting that "add a
  cell" is never taught either: Lesson 1 only teaches Shift+Enter (verified: no
  "press B" / "add a cell" instruction in `lessons/01-…`), so any exercise that
  *did* need a fresh cell would strand the learner. *(Addressed June 2026 — see
  Status, backlog #10: the retype/TODO placeholders are gone — bugs are now
  fixed in place, live where they only mis-print and uncomment-in-place where
  they'd otherwise raise; "add a cell" via press B / the + toolbar is now taught
  once in Lesson 1.)*

**Opportunities:** answer key on every Your-turn; one in-flow AI moment early
(e.g. a Lesson 2 `%%ai` "explain this", or `%ai fix` in Lesson 6); a small
feel-good win to close Lesson 6 (a program that gracefully survives bad input);
mark the densest pieces of 3 & 4 as skippable stretch goals; teach "press B to
add a cell" once in Lesson 1, or ship broken code in an editable cell.

### Stage 4 — Between-class @Tutor practice

**Who:** Maya (mechanism) + Mr. Lee (prompt & reliability).
**Touchpoints:** the chat panel,
[`../.jupyter/personas/tutor_persona.py`](../.jupyter/personas/tutor_persona.py),
`practice_template.ipynb`. **Emotional curve:** curious → *delight (a notebook
made just for me)* → *(risk: `%%ai` fails until the alias is hand-edited)* →
either momentum or let-down.

**What they do:** type `@Tutor new <topic>` (e.g. `@Tutor new loops`), open the
scaffolded `practice_<topic>.ipynb`, Run All, attempt the exercises, ask for
AI review. The loop is *explanation → exercises → attempt → review.*

**Delight (preserve):** The generated exercises are deliberately
**solution-free** — the template's `exercises-ai` cell instructs the model to
"Create exactly 3 practice exercises … Do NOT include solutions or hints"
(`practice_template.ipynb`), protecting learner authorship.
The command layer is also robust by design: `new`/`list`/`help` run
*deterministically in Python* and never depend on a small model emitting a
correct tool call.

**Friction & drop-off risk:**
- **The alias needs a manual edit on any non-default model.**
  `practice_template.ipynb`'s `ai-setup` cell runs
  `%ai alias tutor ollama_chat/gemma4:12b`. The cell *does* document the fix
  inline — a comment directly above the line says "Change the model to any name
  from `ollama list` (keep the `ollama_chat/` prefix)," with a worked MLX
  example — so this is documented friction, not a silent trap. But a learner on
  `llama3.2` or any other model still has to spot that note, edit one line, and
  Run All before `%%ai` works; a beginner who skips the comment gets a let-down
  on the first try. Only `welcome.ipynb` ever taught the alias concept. (The
  persona's no-model fallback at
  [`tutor_persona.py`](../.jupyter/personas/tutor_persona.py):310–316 is
  graceful but doesn't hand the learner the exact `ollama_chat/` id to fix it.)
- **Silent overwrite.** `@Tutor new variables` writes `practice_variables.ipynb`
  *unconditionally*; if one exists it is overwritten and the learner is told
  *only after the fact* — "(replaced the previous copy)"
  ([`tutor_persona.py`](../.jupyter/personas/tutor_persona.py):266–272). Re-run
  it and any prior work in that notebook is gone with no pre-confirmation.
- **@Tutor can't read the open notebook.** The conversational fallback passes
  only the user's raw message text — no code, no error, no cell context
  ([`tutor_persona.py`](../.jupyter/personas/tutor_persona.py):326–329). A
  learner asking "why is my code wrong?" must describe it; the better route is
  @Jupyternaut + a dragged-in cell (see
  [unused features](#unused-jupyter-ai-features-free-wins)).
- **The system prompt is generic, not Socratic.** It says "explain *why* and
  not just *how*" and "prefer small runnable examples"
  ([`tutor_persona.py`](../.jupyter/personas/tutor_persona.py):65–98) — the
  answer-giving default research links to *worse* outcomes. It has no rule to
  withhold full solutions, open with a diagnostic question, ask one question per
  turn, or escalate hints. This is the single highest-leverage AI change, and
  it is a pure edit to one readable file.

**Opportunities:** make the alias self-healing or document the one-time setup +
add a "first time? pick a model in Settings" pointer in an early lesson footer;
warn before overwrite (or suffix a counter); add a short, imperative
hints-not-answers ladder to `SYSTEM_PROMPT` (kept short — the local 12B follows
long behavioral prompts less reliably).

### Stage 5 — Capstone (week 8)

**Who:** Maya. **Touchpoints:** `lessons/08-dictionaries-and-mini-project.ipynb`.
**Emotional curve:** anticipation → *(deflation: I'm only watching)* → pride at
the journey chart.

**What they do:** build a quiz game in labeled steps a–g, each citing the week
it came from, ending with a "make it yours" step and a pandas/matplotlib bar
chart of the learner's own journey.

**Delight (preserve):** The capstone *visibly reuses every week* and composes
into something real — a satisfying "it all fits together" payoff.

**Friction:** **the game isn't actually *played* by a solo learner.** The only
version that runs unattended is a scripted demo with `preset_answers = [...]
# the 3rd one is wrong on purpose` (`lessons/08-…` cell `32b33763`). The real
interactive `play_live` using `input()` is **fully commented out**, ending
*"Remove the # marks above to play live in class"* (cell `ec677d7d`). Maya, at
home with no class, watches pre-canned answers being graded instead of playing
her own game — blunting the mastery payoff.

**Opportunity:** add a prominent solo-learner nudge near the top of the project
— *"At home? Uncomment the cell below to play it yourself right now."*

### Stage 6 — After the course

**Who:** Maya. **Touchpoints:** the closing "Where to go next" section.
**Emotional curve:** accomplished → reassured (it persists) → *(open question:
what keeps me going?)*.

**What they do:** read the four concrete starter projects (each scoped to what
was taught), the external links (docs.python.org, *Automate the Boring Stuff*),
and the reassurance that the workspace and tutor persist.

**Delight (preserve):** A strong, non-abandoning close — concrete next projects
annotated with the tools they use, plus persistence reassurance.

**Friction & drop-off risk:** the **post-week-8 cliff.** This is the one stage
with no measured outcome: the course ends with starter projects and links but
**no next-cohort hook, no recurring touchpoint, and nothing that pulls Maya back
in week 9**. The funnel's thesis is completion *and persistence*, yet the back
end is entirely unmeasured — once the eight notebooks are done, whether anyone
keeps using the workspace is invisible.

**Opportunity:** small add — per-project difficulty/time labels. This is also
the natural seat for any **cohort / streak / accountability** layer, which the
drop-off research says is what lifts completion from the self-paced baseline;
pair it with a post-course continuation signal (metric 13) so the lever is
measurable.

---

## The core AI interaction loop

The product's reason for existing, spelled out as the learner experiences it:

1. **In a lesson**, Maya reads a demo and reaches a "Your turn" exercise
   (`lessons/0N-…`).
2. **She gets stuck** — code errors, or she's unsure her answer is right.
3. **She opens the chat** and either asks @Tutor a question, or asks
   @Jupyternaut *"what does this error mean?"* ([`../README.md`](../README.md):82–84).
4. **She wants structured practice**, so she types `@Tutor new loops`. The
   persona deterministically copies `practice_template.ipynb`, rewrites the
   `TOPIC = …` line, and writes `practice_loops.ipynb`
   ([`tutor_persona.py`](../.jupyter/personas/tutor_persona.py):229–275).
5. **She opens it and Runs All.** The `%%ai` cells call the configured model
   for an explanation and solution-free exercises about *loops*.
6. **She attempts** the exercises in the empty cells, then re-runs an AI-review
   cell for feedback (or asks for harder ones).
7. **She returns to the lesson** with the concept reinforced.

**Where the loop breaks today:** step 3 is friction (@Tutor can't see her code;
she must describe it). Step 5 fails *silently* if her model isn't the hard-coded
alias default. Step 6's "review" is generic, not Socratic, and never warns her
the AI can be wrong — risky for a beginner who can't yet tell right code from
wrong. And critically, **steps 3–7 are only ever invited from optional "After
class" footers**, so a footer-skipper never enters the loop at all. *(Addressed
June 2026 — see backlog #3: each lesson body 02–08 now carries one mandatory
in-flow "🤖 Ask your tutor" moment, so the loop is invited inside the lesson,
not only from the footer.)*

---

## What the research says

A short, cited basis for the recommendations above. URLs are real and link to
the sources behind the synthesis.

**Drop-off science (why early wins matter).**
- Self-paced completion is very low (median ~12.6%) and *starting early /
  active participation in week 1* is the strongest completion predictor (~14×);
  attrition concentrates around the Module-2→3 / ~2/3 point. — Ruzuku,
  *The Completion Gap*: <https://www.ruzuku.com/learn/articles/completion-gap>
- *Mastery experiences* drive self-efficacy, which predicts novice persistence;
  early frustration and undetected failure are worst-case for self-efficacy —
  the case for an answer key and against the "slow is normal" framing masking a
  RAM hang. — <https://arxiv.org/abs/1707.04291>

**AI-tutor UX patterns (hints, not answers).**
- Heavier LLM reliance correlates with lower grades, and CS1 students resubmit
  LLM code without understanding it; published tutors (Khanmigo, Codecademy)
  hard-code *hint-before-answer*. — <https://arxiv.org/pdf/2309.14049> ·
  <https://www.khanmigo.ai/>
- A scaffolded-tutor prompt (never volunteer a full solution; open with "what
  have you tried?"; one question per turn; a hint ladder; self-explanation
  prompts) is the evidence-based shape for `SYSTEM_PROMPT`. —
  <https://arxiv.org/pdf/2506.19107>
- Beginners can't yet vet AI output: students understood LLM-generated code
  only ~32% of the time and ~91% showed automation bias (entering the prompt's
  *expected* output as the code's *actual* output) — the case for a one-line
  "the AI can be wrong; run it and check" caveat and a predict-then-run habit.
  — <https://arxiv.org/html/2504.19037v1>

**Jupyter AI in education (capabilities & teaching the tool).**
- v3 uses LiteLLM ids and the chat assistant needs tool calling, which only
  `ollama_chat/` supports — the technical reason the `ollama/` launcher tip is
  a blocker. — <https://jupyter-ai.readthedocs.io/en/v3/getting-started.html>
- Novices need explicit notebook-UI teaching (Shift+Enter, adding cells,
  Restart-and-Run-All) because cells share state and can run out of order;
  45-min sessions should chunk into 3–5 explain-then-do blocks (adult attention
  ~10–18 min) — the basis for the Lesson-1 "add a cell" gap and the
  Lessons-3/4 density flag. —
  <https://jupyter4edu.github.io/jupyter-edu-book/jupyter.html>
- A lightweight, local-model auto-check (assert cells before AI feedback) is
  validated for exactly this private/local setup. — <https://arxiv.org/abs/2502.18425>

---

## Gap analysis & opportunity backlog

Prioritized by horizon (now / next / later), with impact and effort. "Now"
items are cheap, high-impact, and unblock the primary persona. **Within a
horizon**, rows are ordered by impact first, then ascending effort (smallest
unblock-the-most fix wins ties). See [Baselines, targets &
validation](#baselines-targets--validation) for the effort-sizing key and per-row
owners. The [Unused Jupyter AI features](#unused-jupyter-ai-features-free-wins)
below are scoped/cross-referenced into this backlog rather than ranked
separately.

| # | Gap | Stage | Persona | Impact | Effort | Horizon | Status |
|---|-----|-------|---------|--------|--------|---------|--------|
| 1 | Launcher's closing tip steers to the broken `ollama/` prefix the docs warn against (`start.sh`:102, `start.ps1`:179) | 1 | Sam | High | Small | **Now** | ✅ Shipped (Jun 2026) |
| 2 | "Your turn" exercises have no answer key/self-check; solo learner can't verify (`lessons/02-…` `3c6c7c71` vs the good `# should print` in `lessons/05-…`) | 3 | Maya | High | Medium | **Now** | ✅ Shipped (Jun 2026) |
| 3 | Headline AI features only in optional "After class" footers — 0 `%%ai` cells in any lesson body; never experienced in-flow | 3/4 | Maya | High | Medium | **Now** | ✅ Shipped (Jun 2026) — one in-flow "🤖 Ask your tutor" markdown moment now in every lesson body 02–08 (each a distinct angle: ask-a-concept, one-more-decision/challenge, review-your-function, read-the-error, predict-then-run, brainstorm), verified exactly one per lesson; live `%%ai` stays commented out by design to keep Run-All offline |
| 4 | welcome.ipynb tour never links `lessons/` or Lesson 1 (cell `next-md`) | 2 | Maya | Medium | Small | **Now** | ✅ Shipped (Jun 2026) |
| 5 | Capstone game's interactive `play_live` is commented out; solo learner only watches a demo (`lessons/08-…` `ec677d7d`) | 5 | Maya | Medium | Small | **Now** | ✅ Shipped (Jun 2026) |
| 6 | No RAM check + no port-8888 handling; "slow is normal" masks a hang (`start.sh`/`start.ps1`; `SETUP.md`:177) | 1 | Sam | High | Medium | Next | ✅ Shipped (Jun 2026) |
| 7 | `@Tutor` `SYSTEM_PROMPT` is generic, not Socratic — no hints-not-answers guardrail (`tutor_persona.py`:65–98) | 4 | Mr. Lee | High | Small | Next | ✅ Shipped (Jun 2026) |
| 8 | Practice template alias defaults to `gemma4:12b`; needs a one-line hand-edit + Run All on any other model (inline note exists but a beginner may skip it) (`practice_template.ipynb` `ai-setup`) | 4 | Maya | Medium | Medium | Next | ✅ Shipped (Jun 2026) |
| 9 | `@Tutor new` silently overwrites a prior practice notebook (`tutor_persona.py`:266–272) | 4 | Maya | Medium | Small | Next | ✅ Shipped (Jun 2026) |
| 10 | Fix-the-bug is a fiddly retype-from-comments chore in an in-cell editable area (`lessons/06-…` `b45a54d4`, also 04 `c30d84bf` / 07 `409f5f43`); and "add a cell" is never taught (Lesson 1 only teaches Shift+Enter) | 3 | Maya | Medium | Medium | Next | ✅ Shipped (Jun 2026) — no retype-from-comments chore survives: each Fix-the-bug is now fix-in-place. Live (CASE A) bugs run with wrong output and the learner edits them directly (04 `c30d84bf`, 06 `b45a54d4`); exception/infinite-loop (CASE B) bugs stay commented by design to keep Run-All offline-safe, with the learner un-commenting them *right in the same cell* (delete the `#`s or Cmd+/ / Ctrl+/). "Add a cell" (press B / + toolbar) is now taught once in Lesson 1, and a drag-into-chat stuck-nudge sits on every Fix-the-bug. (The commented CASE B starting state is a deliberate Run-All residual, not the old chore.) |
| 11 | Lesson 6 motivation cliff — no visual/game payoff at the 2/3 drop-off point (0 plot cells; `## 4. try / except … (~15 min)`) | 3 | Maya | Medium | Small | Next | ✅ Shipped (Jun 2026) |
| 12 | Long, serial TTFS — two big downloads back-to-back; default's real size (`gemma4:12b` ~7.6 GB, `TEACHERS-GUIDE.md`:78) never shown to the learner, only the "4–18 GB" range | 1 | Sam | Medium | Small | Next | ✅ Shipped (Jun 2026) |
| 13 | macOS setup assumes `cd`; no double-click mac launcher (`SETUP.md`:87–90) | 1 | Sam | Medium | Small | Next | ✅ Shipped (Jun 2026) |
| 14 | No AI-fallibility warning anywhere (welcome / template / tutor's first reply) | 2/4 | Maya | Medium | Small | Next | ✅ Shipped (Jun 2026) |
| 15 | Lessons 3 & 4 overstuffed for 45 min; mark densest pieces as skippable stretch goals | 3 | Maya | Medium | Small | Later | ✅ Shipped (Jun 2026) — as scoped (mark, don't slim): Lesson 3's `while` section and number-guessing demo, and Lesson 4's `for`+`if` filter pattern, are all tagged *stretch goal — skip if short on time*. A re-check confirmed nothing else qualifies as genuinely optional — booleans/`if`/`and`-`or`-`not` and lists/`for`/loop-patterns are load-bearing for Lessons 4/5 — so the underlying content is deliberately left intact rather than slimmed. |

---

## Unused Jupyter AI features (free wins)

Capabilities the repo already has installed/enabled but doesn't surface — each
is mostly a *doc + one demo cell*, not new infrastructure.

The last column ranks each (Impact / Effort / Horizon) on the same scale as the
backlog and points to the numbered gap it serves, so these aren't a separate
unranked list.

| Feature | What it is | Why it matters here | Impact / Effort / Horizon (→ backlog #) |
|---------|-----------|---------------------|-----------------------------------------|
| `%ai fix` + `Err[n]` / `In[n]` / `Out[n]` refs | v3 magics auto-explain the last error and let prompts reference prior cells | A built-in "explain my error" tutor that maps exactly onto **Lesson 6** and a beginner's #1 need. Zero copy-paste. The Teacher's Guide documents `-f` and aliases (`TEACHERS-GUIDE.md`:262–267) but never `%ai fix`. <https://jupyter-ai.readthedocs.io/en/v3/users/magic_commands/index.html> | High / Medium / Now (→ #3, #11) · ✅ Shipped (Jun 2026, doc) — "Three v3 magics worth teaching" added to the Teacher's Guide |
| `{variable}` interpolation into `%%ai` | Prompts can interpolate Python values, e.g. `{Err[1]}` or `{df.head()}` | Lets a learner feed *actual* data/errors into a prompt, and makes the template's `{TOPIC}` robust rather than version-dependent. | Medium / Small / Next (→ #3, #8) · ✅ Shipped (Jun 2026, doc) — covered in the Teacher's Guide magics subsection |
| Chat context attachments (`@file:<path>`, drag a file **or a cell**, paperclip) | v3's no-embeddings successor to `/learn`; personas read the attached context | **Highest-leverage beginner add:** drag the broken cell into chat and ask "why is this wrong?" — directly fixes the "@Tutor can't read the notebook" gap. <https://jupyter-ai.readthedocs.io/en/v3/users/index.html> | High / Small / Now (→ Stage 4 "@Tutor can't read the open notebook") · ✅ Shipped (Jun 2026, doc) — Teacher's Guide attachments bullet plus drag-a-cell pointers in welcome.ipynb, the lessons, and `lessons/README.md` |
| Notebook tools (MCP) + code-toolbar (insert-as-cell / replace; reading the active cell is a notebook-tool, not a toolbar button) | Personas can act on the active notebook; MCP is already ON in this repo (`TEACHERS-GUIDE.md`:256–260) | Turns chat answers into runnable code in one click. The guide under-sells it as an advanced "demonstrate once" aside. | Medium / Small / Later (→ #3) · ✅ Shipped (Jun 2026, doc) — Teacher's Guide "Chat code → runnable cell in one click" subsection now surfaces the three code-toolbar buttons (copy / insert-as-cell / replace) and the already-on MCP notebook tools, with a three-click demonstrate-in-class flow |
| Socratic `SYSTEM_PROMPT` (hint ladder, one diagnostic question, self-explanation) | Not a Jupyter AI feature — the one file the repo fully controls | The highest-leverage AI change; a few imperative lines convert a generic chatbot into a tutor that preserves authorship. <https://arxiv.org/pdf/2506.19107> | High / Small / Next (= #7) · ✅ Shipped (Jun 2026) — Socratic hints-not-answers ladder added to `SYSTEM_PROMPT` |
| Assert-based "check my work" cells (NBgrader/PyEvalAI pattern) | A lightweight test cell that runs first, *then* asks the model | Closes the biggest solo-learner feedback gap (no answer key). Full NBgrader is overkill; a few asserts in the template + lessons is proportionate. <https://arxiv.org/abs/2502.18425> | High / Medium / Now (= #2) · ◐ Partial — the answer-key gap (#2) is closed via collapsible "✅ Check your answer" reveals in all 8 lessons, not auto-running assert cells |
| ⚠️ Inline ghost-text autocomplete — **NOT in v3** | jupyter-ai's inline completer is disabled in v3 pending a LiteLLM refactor (issue #1431) | Expectation correction: don't hunt for a toggle that doesn't exist. For as-you-type completion the real path is a separate extension (jupyterlite/ai, Notebook Intelligence). Worth one line in the Teacher's Guide. <https://github.com/jupyterlab/jupyter-ai/issues/1431> | Low / Small / Later (doc-only) · ✅ Shipped (Jun 2026, doc) — expectation-correction bullet added to the Teacher's Guide |

---

## What already works — delights to preserve

Treat these as regression-risk: they are doing the heavy lifting.

1. **README front door** — value prop + fear-preemption in the first screen,
   with inline jargon-glossing ([`../README.md`](../README.md):3–18).
2. **AI-free first win** — welcome.ipynb's env-check green checkmarks decouple
   the first success from the slow model path.
3. **Honest, calm download/latency framing** — the big pull and first-reply
   latency are flagged up front with coping advice
   ([`../SETUP.md`](../SETUP.md):180, 177).
4. **Engineered Windows/mac launcher parity** — `start.cmd` defuses the
   execution-policy wall; the Microsoft-Store python trap is pre-empted.
5. **Lesson 1 onboarding tone** — instant win, no-grades framing, "you can't
   break anything," and a graceful "is this for you?" exit.
6. **The week-to-week spiral** — recap/teaser bookends and "week 4 pattern!"
   callbacks make progress cumulative and the capstone earned.
7. **The collapsible "Check yourself" pattern** — `<details>` reveal quizzes in
   lessons 2–8; the model the Your-turn cells should copy.
8. **Capstone construction** — labeled steps a–g, a "make it yours" step, and a
   journey bar chart.
9. **Solution-withholding practice template** — exercises generated *without*
   solutions ("Do NOT include solutions or hints" in the template's
   `exercises-ai` cell, `practice_template.ipynb`), protecting learner
   authorship.
10. **Deterministic command layer** — `new`/`list`/`help` run in Python, never
    relying on small-model tool calls.
11. **On-mission architecture** — local-first/private via Ollama (no keys, no
    cost), v3 personas, correct `ollama_chat/` LiteLLM ids in the docs, and ACP
    cloud agents deliberately *not* in the default.

---

## Success metrics

This is a **local-first product with no telemetry**, so there is no
auto-instrumentation. Each metric below names *how* it would actually be
collected — **(local log)** = an opt-in `~/.python-workspace` activity log a
pilot cohort agrees to share; **(facilitator)** = Mr. Lee observes/stopwatches
in a session; **(survey)** = a self-report form. Nothing phones home. Two
metrics are explicitly *not* auto-measurable and are tagged accordingly.

1. **Time-to-first-success (TTFS).** Minutes to the first green checkmark in
   welcome.ipynb's env-check, and *separately* to the first successful AI reply.
   *Collection:* the **in-Lab** segments are **(local log)** once a cell runs;
   the **pre-Lab** segment (clone → Ollama install → multi-GB pull, before any
   instrumentable surface exists) is **(facilitator)** stopwatch or **(survey)**
   only — not auto-instrumentable.
2. **Setup completion rate** with funnel drop-off per gated step (Python
   install → Ollama → model pull → launcher → model selection). Watch the
   model-prefix step specifically (the `ollama/` vs `ollama_chat/` blocker).
   *Collection:* **(facilitator)** / **(survey)** — these steps are pre-Lab.
3. **First-session activation** — % who run ≥1 code cell *and* make one
   successful AI interaction in session 1 (the ~14× completion predictor).
   *Collection:* **(local log)**.
4. **Lesson-by-lesson completion (1→8)** with explicit attention to the
   weeks-2→3 attrition cliff and the Lesson 6 dip. *Collection:* **(local log)**
   (cells run per lesson notebook) or **(survey)**.
5. **Eight-week completion rate** vs. the self-paced baseline (~7–13%); set a
   stretch target nearer cohort/active-discussion rates *if* an accountability
   layer is added. *Collection:* **(facilitator)** / **(survey)**.
6. **AI-feature reach** — % who use @Tutor, @Jupyternaut, or a `%%ai` cell at
   least once (today this can be **0%** for a footer-skipper). *Collection:*
   **(local log)**.
7. **Self-check coverage & use** — % of Your-turn cells with an answer
   key/assert (a static repo count), and % of learners who use them
   **(local log)**.
8. **@Tutor reliability** — practice-notebook generation success on first
   attempt (model configured + alias healthy) and the rate the "No chat model
   is configured" fallback fires. *Collection:* **(local log)**.
9. **Capstone play-through** — % of solo learners who actually run an
   interactive game (uncomment `play_live`) vs. only watch the demo.
   *Collection:* **(local log)** / **(survey)**.
10. **Help-seeking rate** — questions per learner per week; *rising* help-
    seeking is a positive retention signal. *Collection:* **(local log)**.
11. **Over-reliance guardrail** — rate of learners *modifying* AI-suggested code
    before running vs. pasting verbatim (automation-bias proxy), once a
    predict-then-run step exists. *Collection:* **pilot/survey-only** — capturing
    chat output, the pasted cell, and edit-then-run timing has **no hook in this
    stack**, so this is observed in a moderated pilot, not auto-instrumented.
12. **Runtime-failure incidence** — frequency of RAM-hang and port-conflict
    events and whether the learner recovered. *Collection:* **(facilitator)** /
    **(survey)**.
13. **Post-course continuation** — % still using the workspace N weeks after
    Lesson 8 (any cell run, or a new `practice_*.ipynb` created), measuring the
    post-week-8 cliff (Stage 6) and any accountability-layer effect.
    *Collection:* **(survey)** or opt-in **(local log)**.

---

## Baselines, targets & validation

The map above is grounded in the repo and in research, but **no claim here has
yet been checked against a real learner.** This section makes the gaps in
evidence explicit so prioritization is falsifiable rather than asserted.

### Baselines & targets

No telemetry exists today, so most baselines are **(est.)** — to be replaced by
a first pilot cohort (Mr. Lee's class) before any target is treated as real.
Targets are deliberately rough; the point is a number to move, not precision.

| # | Metric | Baseline (today) | Target | Notes |
|---|--------|------------------|--------|-------|
| 1 | TTFS (env-check) | ~10–30 min incl. downloads (est.) | < 5 min in-Lab after pull | pre-Lab segment dominated by the pull, not the product |
| 2 | Setup completion | unknown (est.) | ≥ 80% reach JupyterLab | model-prefix step is the suspected leak |
| 3 | First-session activation | unknown (est.) | ≥ 70% run a cell + 1 AI reply | the ~14× completion predictor |
| 4 | Lesson 1→8 completion | follows ~7–13% self-paced curve (est.) | flatten the weeks-2→3 and L6 dips | per-lesson, not just final |
| 5 | 8-week completion | ~7–13% (self-paced baseline, cited) | ≥ 30% *with* accountability layer | baseline is the cited research, not measured here |
| 6 | AI-feature reach | can be **0%** (footer-skipper) | ≥ 90% touch AI by week 2 | direct consequence of gap #3 |
| 7 | Self-check coverage | shipped — "✅ Check your answer" reveals across all 8 lessons (27 total) | 100% of Your-turn cells | static repo count, measurable now |
| 8 | @Tutor first-attempt success | unknown (est.) | ≥ 95% on a configured model | gated by the alias edit (gap #8) |
| 9 | Capstone play-through | likely low — `play_live` commented out | ≥ 60% of solo learners play live | gap #5 |
| 10 | Help-seeking rate | unknown (est.) | trend *up* week-over-week | rising is the positive signal |
| 11 | Over-reliance guardrail | unknown (est.) | majority *edit* before running | pilot/survey-only |
| 12 | Runtime-failure incidence | unknown (est.) | < 10% hit an unrecovered hang/port clash | RAM + port-8888 gaps (#6) |
| 13 | Post-course continuation | unmeasured | ≥ 25% active at week +4 | the back-end of the funnel |

### Effort-sizing key

Backlog Small/Medium map to rough engineering time (one contributor, familiar
with the stack):

- **Small** — under ~half a day; a doc/copy edit or a single-cell/single-line
  change (e.g. #1 flip the launcher tip, #4 add a lessons link).
- **Medium** — roughly half a day to ~2 days; touches multiple notebooks or
  needs design/testing across the eight lessons (e.g. #2 answer keys
  everywhere, #3 in-flow AI moments).
- **Large** — multi-day / cross-cutting (none in the current backlog; an
  accountability layer would be the first).

### Ownership (default per horizon)

- **Now** — repo maintainer (you); all five are doc/notebook edits with no
  persona-behavior risk.
- **Next** — split: launcher/setup items (#6, #12, #13) → maintainer;
  AI-behavior items (#7 `SYSTEM_PROMPT`, #8 alias, #9 overwrite) → **Mr. Lee's
  seat**, since they are edits to the one readable persona file he already owns.
- **Later** — maintainer, scheduled after a pilot validates the thesis.

### Assumptions & how we'd validate

These are **inferred from docs + research, not yet observed**:

- **The three personas** (Maya / Sam / Mr. Lee) are constructed from what the
  docs promise and the code does — no real learner has been interviewed.
  *Validate:* 3–5 user interviews + a watch-them-set-up session before committing
  "Next"-horizon effort.
- **The drop-off thesis** (weeks-2→3 cliff, Lesson-6 motivation sag) is imported
  from general self-paced-MOOC research, not measured on *this* course.
  *Validate:* run metric 4 (per-lesson completion) on the first cohort and
  confirm the dips land where predicted before optimizing for them.
- **"Footer-skippers never use AI"** assumes learners skip the optional "After
  class" sections. *Validate:* metric 6 against a cohort; if reach is already
  high, gap #3 drops in priority.
- **Targets** above are placeholders. *Validate:* set real baselines from the
  first pilot, then revisit each target.

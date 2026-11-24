# ⚽ Matchday AI

**An AI caption pipeline for football matches that checks its own work.**

Matchday AI takes football results, writes social media captions for Instagram, TikTok and X, and checks every caption for mistakes before it is accepted. If a caption fails a check, the writer gets feedback and tries again. Every attempt is saved in a database. Each match also gets a ready-to-post image card.

> A personal learning project by **Fatemeh Yousefi**.

<p align="center">
  <img src="docs/example-card.png" alt="Example match card: Real Madrid 3-2 Barcelona" width="480">
</p>

---

## The project in two ways

**🟢 In simple words**

Imagine you work for a football page on Instagram. After every match, someone has to write a short post: *"FULL TIME: Ajax 2-1 PSV!"*. An AI can write these posts very fast, but sometimes it makes mistakes, like writing the score the wrong way around.

So this project works like a team of two:
- a **writer**, who writes the post, and
- a **checker**, who reads it and says *"this is wrong, please fix it"*.

The writer tries again until the checker is happy (at most 3 times). Then the project makes a nice picture for the post and keeps a notebook (a database) of every try.

**🔵 Technically**

A Python pipeline that reads match data from JSON, validates it with Pydantic, and generates a structured caption (`caption` + `hashtags`) for each match × platform. Six check functions return `CheckResult` objects. If any check fails, the failure details go back to the writer as feedback (up to `MAX_ATTEMPTS = 3`). Every attempt and every check result goes into two SQLite tables, and a SQL report prints the first-try pass rate per platform. Approved Instagram captions are rendered into 1080×1080 PNG cards with Pillow.

## Why I built this

AI models write fluent text, but they can also get facts wrong: a swapped score, a player who never scored, or too many hashtags. On a sports account with millions of fans, one wrong score is a public mistake.

I built this project to learn how to use AI-generated text safely in practice. The model writes the captions, plain Python code checks them, and nothing is published until every check passes.

## What I learned

| Topic | What I practised |
|---|---|
| **Data modelling** | Describing matches, goals and captions with **Pydantic** models, so bad data is rejected straight away (for example, a goal in minute 200) |
| **Prompt design** | Writing a system prompt with a brand voice and hard rules, and building the user prompt from real match data |
| **Structured output** | Making the writer return a fixed shape (`caption` + `hashtags`) instead of free text |
| **Guardrails** | Writing small, testable checks that catch wrong facts and broken rules |
| **Feedback loops** | Sending failed checks back to the writer so it can fix its own mistakes (up to 3 attempts) |
| **Testing** | Unit tests for every check with **pytest** |
| **Databases & SQL** | Saving every attempt and check result in **SQLite**, then reporting pass rates with SQL |
| **Image generation** | Drawing match cards with **Pillow**: gradients, glows, team badges and text layout |
| **Developer tools** | Virtual environments, the `src/` project layout, linters (**flake8**, **mypy**) and VS Code settings |
| **Git** | Building the project in small commits, one idea at a time |

## Challenges I faced (and how I solved them)

Not everything worked the first time. These are the real problems I hit while building this project.

### 1. The AI can get the facts wrong
- 🟢 **Problem:** a caption can look perfect but still have the score the wrong way around (`1-2` instead of `2-1`) or too many hashtags.
- 🔵 **Solution:** I made the `MockWriter` make these mistakes **on purpose** on the first try. Then I built checks that catch them and a feedback loop that sends the error back to the writer. In the report, TikTok passes **0%** on the first try but every caption is fixed on the retry, which shows why the loop is needed.
- 💡 **Lesson:** never trust AI output just because it reads well. Check the facts with code.

### 2. Small text details break simple checks
- 🟢 **Problem:** a score can be written with a long dash (`2–1`) instead of a normal one (`2-1`), so a simple text search would miss it.
- 🔵 **Solution:** `check_score` changes `–` to `-` before it searches.
- 💡 **Lesson:** a check is only as good as the cases it expects. Tests help find the cases I forgot.

### 3. Emojis disappeared from the pictures
- 🟢 **Problem:** the captions have emojis (👇 🔥), but the font can't draw them, so they showed up as empty boxes on the card.
- 🔵 **Solution:** remove emojis before drawing the caption on the image. The emojis stay in the post text itself.
- 💡 **Lesson:** text that looks fine on screen can behave differently inside an image.

### 4. Making the card beautiful but keeping the code simple
- 🟢 **Problem:** my first card was plain: white text on black. I wanted it to look like a real sports graphic, without hundreds of lines of code.
- 🔵 **Solution:** a few Pillow tricks go a long way: a gradient background (`Image.linear_gradient`), soft glows (a blurred ellipse with `GaussianBlur`), round team badges, a dimmed score for the losing team, and a see-through caption panel. Centring text with `anchor="mm"` kept the layout code short. The whole file is still about 80 lines.
- 💡 **Lesson:** good design comes from a few well-chosen ideas, not from lots of code.

### 5. "No module named matchday" / "No module named pytest"
- 🟢 **Problem:** Python couldn't find my own code, and `pytest` didn't work.
- 🔵 **Solution:** my code lives in `src/`, so Python needs `PYTHONPATH=src` to find it (and `pythonpath = ["src"]` in `pyproject.toml` for pytest). The packages were installed in `.venv`, so I have to turn it on first with `source .venv/bin/activate`.
- 💡 **Lesson:** most "module not found" errors are about **where** Python looks, not about the code.

### 6. My project picture didn't show on GitHub
- 🟢 **Problem:** the cards are saved in `output/`, but that folder is in `.gitignore`, so it is never uploaded.
- 🔵 **Solution:** I copied one example card to `docs/example-card.png` and used that in this README.
- 💡 **Lesson:** `.gitignore` keeps generated files out of git, so anything the README shows has to live somewhere that is committed.

### 7. Red errors in VS Code, but the code was fine (the hardest one!)
- 🟢 **Problem:** VS Code showed red error counts on `checks.py`, `models.py` and `writers.py`. One error said `Module "matchday.models" has no attribute "CaptionDraft"`, even though `CaptionDraft` was clearly there. The tests passed, and the checks were clean in the terminal.
- 🔵 **Solution:** step by step, I found several causes stacked on top of each other:
  1. **flake8** marked every line over 79 characters as an error → a `.flake8` file sets a longer limit (130).
  2. A few real small issues (an unused import, missing blank lines) → fixed in the code.
  3. **mypy** didn't know my code was in `src/` → added `[tool.mypy] mypy_path = "src"` to `pyproject.toml`.
  4. VS Code's mypy ran on an old **Python 3.9**, which can't read code written for my **Python 3.14** → installed mypy inside `.venv` and pointed VS Code to it in `.vscode/settings.json`.
  5. **The real cause:** old mypy background processes (daemons) had been running for weeks and still remembered **old versions of my files**. Stopping them and fully quitting VS Code (Cmd+Q) finally cleared the errors.
- 💡 **Lesson:** if the editor and the terminal disagree, trust the terminal and look for something **stale**: an old process, an old cache, or the wrong Python version. Read the exact error message: it tells you which tool is complaining.

## Key takeaways

1. **AI + code checks > AI alone.** The model writes, and plain Python decides whether it is good enough.
2. **Feedback makes the system better.** Telling the writer *exactly* what was wrong works better than just asking it again.
3. **Measure everything.** Saving every attempt in SQLite lets me see *which* rules fail most, not just whether something failed.
4. **Small steps win.** One idea per commit made every problem easy to find and fix.
5. **Tests give confidence.** After every change (even the image redesign), `pytest` told me nothing else had broken.
6. **Debugging is about the environment too.** Many of my problems were not in my code at all, but in paths, versions, settings and old processes.

## How I built it, step by step

I built the project in small steps and committed each one to git. Each step adds one idea on top of the one before.

### Stage 1: Describe the data
| # | Step | Details |
|---|---|---|
| 1 | Match and Goal models + sample data | Pydantic `Match` and `Goal` models with validation (`minute` between 1 and 130, scores ≥ 0), plus `data/matches.json` |
| 2 | Improve the models | `scoreline` and `scorers` properties on `Match` |
| 3 | Platform class | A frozen `Platform` dataclass with `max_chars`, `max_hashtags` and `style`, stored in a `PLATFORMS` dict |

### Stage 2: The writer
| # | Step | Details |
|---|---|---|
| 4 | System prompt | `SYSTEM_PROMPT` in `writers.py` with the brand voice and hard factual rules |
| 5 | User prompt | `build_user_prompt()` puts the platform style, limits and match JSON together, and adds feedback when there is any |
| 6–7 | Fake AI (MockWriter) | `MockWriter.write()` returns a `CaptionDraft`. It makes mistakes on purpose on the first try |

### Stage 3: The checker
| # | Step | Details |
|---|---|---|
| 8 | Score, team and player checks | `check_score`, `check_teams`, `check_players` each return a `CheckResult` |
| 9 | All quality checks | `check_length`, `check_hashtags`, `check_safe_language` (regex + banned word set), combined in `run_all_checks()` |

### Stage 4: Tests
| # | Step | Details |
|---|---|---|
| 10 | First tests | pytest unit tests: a correct score passes, a swapped score fails |
| 11 | A test for every check | 8 tests in `tests/test_checks.py`; `pythonpath = ["src"]` in `pyproject.toml` |

### Stage 5: The pipeline
| # | Step | Details |
|---|---|---|
| 12 | Load all matches | `load_matches()` with `Match.model_validate()` for each item |
| 13 | Feedback loop | `caption_with_retries()`: failed check details go back as `feedback`, up to `MAX_ATTEMPTS = 3` |

### Stage 6: Remember everything
| # | Step | Details |
|---|---|---|
| 14 | Save every attempt | `db.save_caption()` is called on every attempt |
| 15 | SQLite + SQL report | Tables `captions` and `checks`. `GROUP BY` queries for the first-try pass rate and the most failed checks |

### Stage 7: Pictures
| # | Step | Details |
|---|---|---|
| 16 | First match card | Pillow `Image` + `ImageDraw`, a 1080×1080 PNG |
| 17 | Caption on the card | Text wrapping, emoji removal, and rendering inside the pipeline for passing Instagram captions |
| 18 | Nicer design + README | Gradient background, blurred glows, team badges, dimmed losing score, see-through caption panel |
| 19 | Clean code + editor setup | `.flake8`, `[tool.mypy]` in `pyproject.toml`, `.vscode/settings.json`, mypy in `.venv`, small style fixes |

## How it works

```
 data/matches.json
        │
        ▼
 ┌──────────────┐    prompt + feedback    ┌──────────────┐
 │   Pipeline   │ ──────────────────────▶ │    Writer    │
 │              │ ◀────────────────────── │  (mock LLM)  │
 └──────┬───────┘     caption draft       └──────────────┘
        │
        ▼
 ┌──────────────┐   failed? → feedback → try again (max 3)
 │    Checks    │
 └──────┬───────┘
        │ every attempt
        ▼
 ┌──────────────┐        ┌──────────────────────┐
 │    SQLite    │        │  Pillow match card    │
 │  matchday.db │        │  output/<match>.png   │
 └──────────────┘        └──────────────────────┘
```

1. **Load** the matches from `data/matches.json` and validate them with Pydantic.
2. **Write** a caption for each match and each platform (Instagram, TikTok, X). Each platform has its own style and limits.
3. **Check** the caption with six rules (see below).
4. **Retry** with feedback if any check fails, for example: *"Score must appear as 2-1 (home-away)"*.
5. **Save** every attempt and every check result in SQLite.
6. **Render** a match card image for each approved Instagram caption.
7. **Report** the first-try pass rate per platform and the most common failures.

### The six checks

| Check | What it catches |
|---|---|
| `score_correct` | The score is missing or swapped (`1-2` instead of `2-1`) |
| `teams_mentioned` | One of the team names is missing |
| `only_real_scorers` | A player is mentioned who did not score in this match |
| `length_ok` | The caption is too long for the platform |
| `hashtags_ok` | Too many (or zero) hashtags |
| `safe_language` | Insulting words that don't fit the brand voice |

### About the mock writer

The pipeline uses `MockWriter`, a fake LLM. It is free, works offline and gives the same answer every time. It also **makes mistakes on purpose** on the first try (a swapped score, too many hashtags), so you can watch the feedback loop fix them. The prompts in `writers.py` are written for a real model, so a real LLM can replace it later.

## Example output

```
  feedback: ['score_correct: Score must appear as 2-1 (home-away)']
[PASS] m001 instagram (attempts: 2) FULL TIME: Ajax 2-1 PSV. Brian Brobbey steals the show! Who was your player of the match? 👇
...

=== First-try pass rate ===
instagram  3/5 = 60%
tiktok     0/5 = 0%
x          3/5 = 60%

=== Failed checks ===
score_correct   6
hashtags_ok     5
```

## How to run the project

You only need **Python 3.10 or newer**. No API key and no internet are needed, because the writer is a mock. All commands go in a terminal (on Mac: the *Terminal* app).

### Step 0: Check that Python is installed

```bash
python3 --version
```

🟢 This prints something like `Python 3.14.0`. If you see an error, install Python from [python.org](https://www.python.org/downloads/) first.

### Step 1: Download the project and go into its folder

```bash
git clone <this-repository-url>
cd matchday-ai
```

🟢 This copies the project to your computer and moves you inside it. All the next commands must run from this folder.

### Step 2: Create a virtual environment (one time only)

```bash
python3 -m venv .venv
```

🟢 A *virtual environment* is a private box for this project's packages, so they don't mix with other projects on your computer.
🔵 This creates a `.venv/` folder with its own Python interpreter and `site-packages`. It is in `.gitignore`, so it is never committed.

### Step 3: Turn the virtual environment on (every time you open a new terminal)

```bash
source .venv/bin/activate
```

🟢 Your terminal line now starts with `(.venv)`. That means it's on. To turn it off later, type `deactivate`.
🔵 `activate` puts `.venv/bin` first on your `PATH`, so `python`, `pip` and `pytest` use the project's environment.

### Step 4: Install the packages (one time only)

```bash
pip install pydantic pillow pytest
```

🟢 This downloads the three tools the project uses.
🔵 `pydantic` handles data models and validation, `pillow` draws the images, and `pytest` runs the tests.

### Step 5: Run the pipeline

```bash
PYTHONPATH=src python -m matchday
```

🟢 This starts the project. You'll see the writer make mistakes, get feedback and fix them, and a small report appears at the end.
🔵 The code lives in `src/matchday/`, so `PYTHONPATH=src` tells Python where to find the `matchday` package. `-m matchday` runs `src/matchday/__main__.py`, which calls `run_pipeline()`.

### Step 6: Look at the results

Everything is saved in the `output/` folder:

| File | What it is |
|---|---|
| `output/m001.png` … `m005.png` | 🟢 The match pictures, one per match. Open them like any photo: `open output/m003.png` (Mac) |
| `output/matchday.db` | 🟢 The "notebook" with every try. 🔵 A SQLite database with the tables `captions` and `checks` |

🔵 To look inside the database with SQL:

```bash
sqlite3 output/matchday.db "SELECT match_id, platform, attempt, passed, caption FROM captions;"
```

> Every run starts fresh: the old database is deleted and the images are overwritten.

### Step 7: Run the tests

```bash
pytest
```

🟢 This automatically checks that the checker works correctly. You should see `8 passed`.
🔵 pytest finds `tests/test_checks.py` (configured in `pyproject.toml`) and runs one or more unit tests per check function.

### Try it yourself ✏️

- **Add your own match:** add a new entry to `data/matches.json` (copy an existing one and change the teams, score and goals), then run Step 5 again.
- **Change the card colours:** edit `HOME`, `AWAY`, `TOP` and `BOTTOM` at the top of `src/matchday/graphics.py`.
- **Break a rule on purpose:** add a word like `"trash"` to the caption in `writers.py` and watch `safe_language` fail.

### Problems?

| You see | Fix |
|---|---|
| `No module named matchday` | You forgot `PYTHONPATH=src`, or you are not in the project folder |
| `No module named pydantic` / `PIL` / `pytest` | The virtual environment is off: run Step 3, then Step 4 |
| `command not found: python` | Use `python3`, or turn on the virtual environment first |
| Red errors in VS Code, but `pytest` passes | Old mypy processes may still be running: run `pkill -f dmypy`, then quit VS Code with Cmd+Q and reopen it (see challenge 7) |
| The card font looks plain | The cards use *Avenir Next Condensed*, which comes with macOS. On Windows or Linux, Pillow's default font is used instead |

## Project structure

```
matchday-ai/
├── data/
│   └── matches.json        # sample match results
├── src/matchday/
│   ├── __main__.py         # entry point: python -m matchday
│   ├── models.py           # Pydantic models: Match, Goal, CaptionDraft, Platform
│   ├── writers.py          # system prompt, user prompt and the MockWriter
│   ├── checks.py           # the six quality checks
│   ├── pipeline.py         # load → write → check → retry → save → render
│   ├── db.py               # SQLite tables and the SQL report
│   └── graphics.py         # match card image with Pillow
└── tests/
    └── test_checks.py      # pytest tests for every check
```

## Next steps

- [ ] Replace `MockWriter` with a real LLM (for example the Claude API) using the same prompts
- [ ] Add real team colours and logos to the match cards
- [ ] Add a `requirements.txt` or `pyproject.toml` dependencies
- [ ] Compare first-try pass rates across different prompts

---

<p align="center">Made with ⚽ and Python by <b>Fatemeh Yousefi</b></p>

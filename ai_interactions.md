# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Build the PawPal+ logic layer, tests, CLI demo, and Streamlit wiring from a UML design,
implementing sorting, filtering, recurrence, conflict detection, a next-available-slot
algorithm, and JSON persistence.

**What did the agent do?**

- Created `pawpal_system.py` (Priority/Task/Pet/Owner/Scheduler + JSON helpers)
- Created `tests/test_pawpal.py` (17 tests, TDD: failing test before each feature)
- Created `main.py` CLI demo with a `tabulate` table
- Rewrote `app.py` to import the logic layer and persist an `Owner` in `st.session_state`
- Updated `diagrams/uml.mmd` and added `diagrams/uml_final.mmd`

**What did you have to verify or fix manually?**

I reviewed each step before moving on instead of accepting everything at once. The main thing I caught
was the priority sort: the first draft sorted priorities as strings, which ordered them alphabetically
instead of by importance, so I had it switch to an `IntEnum` and sort on the number. I also double-checked
that completing a daily task actually attached the next occurrence to the same pet (not a copy), and I
confirmed the `Priority` enum survived being saved to JSON and loaded back. I ran `python -m pytest`
after each change rather than trusting that the code worked.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

I compared two answers to the same task: "when a daily or weekly task is completed, create the next
occurrence."

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude | ChatGPT |
| **Prompt** | "Given a Task with a `frequency` and an ISO `date` string, return the next occurrence (daily = +1 day, weekly = +7 days, once = None)." | Same prompt. |
| **Response summary** | Used `datetime.date.fromisoformat` + `timedelta`, returned a brand-new `Task` with `completed=False`. | Did the date math by manually splitting the string and adding to the day number. |
| **What was useful** | Handles month/year rollover correctly because `timedelta` does the arithmetic. | Slightly shorter, no import needed. |
| **Problems noticed** | A little more code. | Broke on month boundaries — adding 1 to Jan 31 gave "2026-01-32" instead of Feb 1. |
| **Decision** | **Kept this one.** | Rejected. |

**Which approach did you use in your final implementation and why?**

I went with Option A (the `timedelta` version) because correctness mattered more than saving a line or
two — Option B silently produced invalid dates at the end of a month, and the `timedelta` approach
handles rollover for free. This is the version in `Task.next_occurrence()`.

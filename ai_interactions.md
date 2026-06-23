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

> _TODO (your words): note anything you reviewed, questioned, or changed — e.g. the
> conflict-detection tradeoff, or whether the sort key was correct._

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

> _TODO: pick one algorithm (e.g. weekly recurrence) you prompted two models for, and
> fill the table with what each produced and which you kept._

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->

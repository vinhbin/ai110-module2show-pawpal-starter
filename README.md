# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a simple priority list. The scheduler applies a multi-stage pipeline to turn raw tasks into a realistic daily plan:

- **Frequency filtering** — `daily` tasks are always considered; `weekly` tasks only appear on their scheduled day; `as-needed` tasks are never auto-scheduled.
- **Required-task guarantee** — tasks marked `required` are always included first, before any time-budget check.
- **Preference-aware sorting** — optional tasks are ordered by time slot (morning → afternoon → evening → any), then priority, then whether the category matches the owner's preferences, then shortest-first within a tier to maximise the number of tasks that fit.
- **Greedy fill without early exit** — the scheduler never stops at the first task that doesn't fit; it continues checking later tasks so shorter ones can still be scheduled even after a longer one is skipped.
- **Recurring task auto-spawn** — when a `daily` or `weekly` task is marked complete, a new instance is automatically added to the pet's task list with its `due_date` advanced using Python's `timedelta` (`+1 day` or `+7 days`).
- **Conflict detection** — after scheduling, the plan is scanned for three warning classes: same-pet slot overlap (a pet has two tasks in the same slot), slot budget overrun (total slot minutes exceed the recommended cap), and required-task collisions (two required tasks share a slot). Warnings are returned as plain strings — the program never crashes on a conflict.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

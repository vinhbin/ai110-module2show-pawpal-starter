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

## 🖥️ Sample Output

Output from running the CLI demo (`python main.py`):

```
🐾 Today's Schedule for Jordan

╭────┬────────┬────────────┬─────────┬──────────────┬────────────┬───────────╮
│    │ Time   │ Priority   │ Pet     │ Task         │ Duration   │ Repeats   │
├────┼────────┼────────────┼─────────┼──────────────┼────────────┼───────────┤
│ ⬜  │ 08:00  │ 🔴 HIGH     │ Biscuit │ Morning meds │ 5 min      │ daily     │
│ ⬜  │ 08:00  │ 🔴 HIGH     │ Mochi   │ Litter scoop │ 5 min      │ once      │
│ ⬜  │ 18:00  │ 🟡 MEDIUM   │ Biscuit │ Evening walk │ 30 min     │ daily     │
│ ⬜  │ 12:00  │ 🟢 LOW      │ Mochi   │ Play time    │ 15 min     │ once      │
╰────┴────────┴────────────┴─────────┴──────────────┴────────────┴───────────╯

⚠️  Conflict check:
  - Conflict at 08:00: Biscuit's 'Morning meds' overlaps with Mochi's 'Litter scoop'.

🕒 Next free 30-min slot today: 06:00

🔁 Completing Biscuit's daily 'Morning meds' (should spawn tomorrow's)...
   New occurrence created for: 2026-01-02
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Verbose:
python -m pytest -v
```

These tests cover recurrence (daily/weekly/once), sorting by time and priority,
filtering by pet and status, same-time conflict detection, complete-with-recurrence,
next-available-slot search, and JSON save/load round-trips.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 17 items

tests/test_pawpal.py::test_classes_exist_and_construct PASSED            [  5%]
tests/test_pawpal.py::test_next_occurrence_daily_advances_one_day PASSED [ 11%]
tests/test_pawpal.py::test_next_occurrence_weekly_advances_seven_days PASSED [ 17%]
tests/test_pawpal.py::test_next_occurrence_once_returns_none PASSED      [ 23%]
tests/test_pawpal.py::test_sort_by_time_chronological PASSED             [ 29%]
tests/test_pawpal.py::test_sort_by_priority_high_first_then_time PASSED  [ 35%]
tests/test_pawpal.py::test_filter_by_pet_name PASSED                     [ 41%]
tests/test_pawpal.py::test_filter_by_completed_status PASSED             [ 47%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time_same_pet PASSED [ 52%]
tests/test_pawpal.py::test_detect_conflicts_none_when_times_differ PASSED [ 58%]
tests/test_pawpal.py::test_mark_task_complete_spawns_next_for_daily PASSED [ 64%]
tests/test_pawpal.py::test_mark_task_complete_once_returns_none PASSED   [ 70%]
tests/test_pawpal.py::test_next_available_slot_returns_day_start_when_empty PASSED [ 76%]
tests/test_pawpal.py::test_next_available_slot_skips_busy_block PASSED   [ 82%]
tests/test_pawpal.py::test_next_available_slot_none_when_day_full PASSED [ 88%]
tests/test_pawpal.py::test_todays_schedule_orders_by_priority_then_time PASSED [ 94%]
tests/test_pawpal.py::test_json_round_trip PASSED                        [100%]

============================= 17 passed in 0.04s ==============================
```

**Confidence level:** ⭐️⭐️⭐️⭐️ (4/5) — core scheduling paths and edge cases are tested;
overlap-by-duration conflicts and timezone handling are not yet covered.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Lambda key on `"HH:MM"`; priority desc then time asc |
| Filtering | `Scheduler.filter_tasks(pet_name=…, completed=…)` | By pet and/or completion status |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings for same-start-time tasks; never raises |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily/weekly task spawns the next via `timedelta` |
| Next free slot | `Scheduler.next_available_slot(duration)` | Earliest gap that fits a duration between day_start/day_end |
| Priority scheduling | `Priority` enum + `Scheduler.todays_schedule()` | High-priority tasks ordered first, then by time |
| Persistence | `save_to_json()`, `load_from_json()` | Round-trips owner/pets/tasks to `data.json` (enum stored as int) |

## 📸 Demo Walkthrough

PawPal+ runs as a Streamlit app (`streamlit run app.py`) backed by a pure-Python logic layer.

**Main UI features & actions:**
- Sidebar: set the owner name and add pets (name + species).
- Main form: add tasks to a pet (title, time, duration, priority, repeat frequency).
- Schedule panel: shows today's plan as a table, conflict warnings, and the next free slot.

**Example workflow:**
1. In the sidebar, add a pet "Biscuit" (dog).
2. Add a task: "Morning meds", 08:00, 5 min, HIGH, daily.
3. Add a task: "Evening walk", 18:00, 30 min, MEDIUM, daily.
4. Add a conflicting task on another pet at 08:00 → a ⚠️ conflict warning appears.
5. View "Today's Schedule": tasks are ordered HIGH→LOW then by time.

**Key Scheduler behaviors shown:** priority+time sorting, same-time conflict warnings,
next-available-slot suggestion, and recurrence when a daily task is completed.

### Sample CLI output (`python main.py`)

```
🐾 Today's Schedule for Jordan

╭────┬────────┬────────────┬─────────┬──────────────┬────────────┬───────────╮
│    │ Time   │ Priority   │ Pet     │ Task         │ Duration   │ Repeats   │
├────┼────────┼────────────┼─────────┼──────────────┼────────────┼───────────┤
│ ⬜  │ 08:00  │ 🔴 HIGH     │ Biscuit │ Morning meds │ 5 min      │ daily     │
│ ⬜  │ 08:00  │ 🔴 HIGH     │ Mochi   │ Litter scoop │ 5 min      │ once      │
│ ⬜  │ 18:00  │ 🟡 MEDIUM   │ Biscuit │ Evening walk │ 30 min     │ daily     │
│ ⬜  │ 12:00  │ 🟢 LOW      │ Mochi   │ Play time    │ 15 min     │ once      │
╰────┴────────┴────────────┴─────────┴──────────────┴────────────┴───────────╯

⚠️  Conflict check:
  - Conflict at 08:00: Biscuit's 'Morning meds' overlaps with Mochi's 'Litter scoop'.

🕒 Next free 30-min slot today: 06:00

🔁 Completing Biscuit's daily 'Morning meds' (should spawn tomorrow's)...
   New occurrence created for: 2026-01-02
```

**Persistence:** `save_to_json(owner, "data.json")` writes all pets/tasks to `data.json`;
`load_from_json("data.json")` restores them on a later run. The `Priority` enum is stored
as its integer value and rebuilt on load. (See `pawpal_system.py`.)

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

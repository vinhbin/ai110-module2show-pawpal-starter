# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The system uses four core classes plus a `Priority` enum:

- **Task** (dataclass): one care activity — title, duration, priority, time, frequency, completion, date. Knows how to `mark_complete()` and compute its `next_occurrence()`.
- **Pet** (dataclass): pet info (name, species) and its own list of tasks. `add_task()`, `task_count()`.
- **Owner**: manages multiple pets; `add_pet()`, `get_pet()`, `all_tasks()` flattens tasks across pets.
- **Scheduler**: the "brain" — reads the Owner, then sorts, filters, detects conflicts, and builds the daily plan. Holds no data of its own.

> _TODO (your words): in 1–2 sentences, say why you split data (Owner/Pet/Task) from logic (Scheduler)._

**b. Design changes**

Changes from the initial draft to the final implementation:
- Added `Priority` as an `IntEnum` (not a plain string) so the scheduler can sort numerically.
- Added `Owner.all_tasks_with_pet()` so conflict/display logic knows which pet owns each task.
- Added module-level `save_to_json` / `load_from_json` for persistence.
- Added `Scheduler.next_available_slot()` as a third algorithm.

> _TODO (your words): pick ONE of the above and explain in 1–2 sentences why you changed it._

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers each task's **start time** ("HH:MM"), its **priority** (LOW/MEDIUM/HIGH),
its **duration** (used by next-available-slot), and its **frequency** (once/daily/weekly).
`todays_schedule()` orders by priority first, then time.

- How did you decide which constraints mattered most?

> _TODO (your words)._

**b. Tradeoffs**

The conflict detector flags tasks that share the **same start time** only — it does not
check whether two tasks of different durations *overlap* (e.g., an 08:00 60-min task and an
08:30 task). This keeps `detect_conflicts()` O(n) and easy to reason about, which is
reasonable for a single owner's daily plan where exact-time clashes are the common case.

> _TODO (your words): do you agree this tradeoff is acceptable? When would overlap-detection matter?_

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

> _TODO (your words)._

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

> _TODO (your words)._

---

## 4. Testing and Verification

**a. What you tested**

The suite (`tests/test_pawpal.py`) covers recurrence (daily/weekly/once), sorting by time
and by priority, filtering by pet and status, same-time conflict detection,
complete-with-recurrence, next-available-slot search, and JSON round-trips — 17 tests, all passing.

> _TODO (your words): why were these the important behaviors to lock down?_

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

> _TODO (your words)._

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

> _TODO (your words)._

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

> _TODO (your words)._

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

> _TODO (your words)._

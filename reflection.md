# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The system uses four core classes plus a `Priority` enum:

- **Task** (dataclass): one care activity — title, duration, priority, time, frequency, completion, date. Knows how to `mark_complete()` and compute its `next_occurrence()`.
- **Pet** (dataclass): pet info (name, species) and its own list of tasks. `add_task()`, `task_count()`.
- **Owner**: manages multiple pets; `add_pet()`, `get_pet()`, `all_tasks()` flattens tasks across pets.
- **Scheduler**: the "brain" — reads the Owner, then sorts, filters, detects conflicts, and builds the daily plan. Holds no data of its own.

I split the data classes (Owner/Pet/Task) from the logic class (Scheduler) because I wanted the
things that *hold information* to stay simple and the thing that *makes decisions* to live in one
place. That way, if I change how the schedule is built later, I only touch the Scheduler and the
Pet/Task data stays exactly the same.

**b. Design changes**

Changes from the initial draft to the final implementation:
- Added `Priority` as an `IntEnum` (not a plain string) so the scheduler can sort numerically.
- Added `Owner.all_tasks_with_pet()` so conflict/display logic knows which pet owns each task.
- Added module-level `save_to_json` / `load_from_json` for persistence.
- Added `Scheduler.next_available_slot()` as a third algorithm.

The biggest change was making `Priority` an `IntEnum` instead of just storing "low"/"medium"/"high"
as strings. I started with strings because they were easy to type, but once I tried to sort by
priority I realized strings sort alphabetically ("high" < "low" < "medium"), which is wrong. Switching
to an `IntEnum` let me sort numerically (HIGH=3 first) and still print a readable name in the table.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers each task's **start time** ("HH:MM"), its **priority** (LOW/MEDIUM/HIGH),
its **duration** (used by next-available-slot), and its **frequency** (once/daily/weekly).
`todays_schedule()` orders by priority first, then time.

- How did you decide which constraints mattered most?

I decided priority mattered most because as a pet owner the thing I care about is "what happens if I
run out of time today" — I want the important stuff (meds) to come before the nice-to-have stuff
(play time). Time is the tiebreaker so two equally-important tasks still show up in the order they
actually happen during the day.

**b. Tradeoffs**

The conflict detector flags tasks that share the **same start time** only — it does not
check whether two tasks of different durations *overlap* (e.g., an 08:00 60-min task and an
08:30 task). This keeps `detect_conflicts()` O(n) and easy to reason about, which is
reasonable for a single owner's daily plan where exact-time clashes are the common case.

I think this tradeoff is acceptable for now because most of my test cases were exact clashes (two
things booked for 08:00), and catching those covers the common mistake. Overlap detection would
matter once tasks have real durations that bump into each other — like a 60-minute walk at 08:00 and
a vet appointment at 08:30. If I kept building this, that's the first thing I'd upgrade.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI mostly as a pair-programmer: I'd describe the class or method I wanted, let it draft the
code and a test, then read both before keeping them. The most helpful prompts were the specific ones —
"sort these tasks by priority, then by time" worked way better than "make the scheduler smart." I also
leaned on it to draft the UML and the tests first, which kept me building in small, checkable steps.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The clearest moment was the priority sorting. The first version stored priority as a string and sorted
on it, and I noticed the order looked wrong — "high" was landing after "low" because it was sorting
alphabetically. I didn't just trust that the code "looked right"; I checked it against a test where
Meds (HIGH) had to come before Walk (LOW), and that's what pushed me to switch to an `IntEnum` and sort
on the number instead. In general I verified things by running `python -m pytest` and reading the
actual output rather than assuming the suggestion was correct.

---

## 4. Testing and Verification

**a. What you tested**

The suite (`tests/test_pawpal.py`) covers recurrence (daily/weekly/once), sorting by time
and by priority, filtering by pet and status, same-time conflict detection,
complete-with-recurrence, next-available-slot search, and JSON round-trips — 17 tests, all passing.

These were the behaviors I most expected to break, so they were the ones worth locking down. Sorting
and conflict detection are the core promise of the app, recurrence touches dates (which are easy to get
off by a day), and the JSON round-trip is where I worried the `Priority` enum might not survive being
saved and reloaded. Testing those gave me confidence that the parts users actually rely on really work.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident — around 4 out of 5. All 17 tests pass and they cover the main paths plus a few
edge cases (a task with no recurrence, a day that's completely full). With more time I'd test
overlapping-duration conflicts, tasks scheduled across midnight, and what happens if someone types a
bad time like "8:00" or "25:00" instead of a clean "HH:MM" string.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how clean the separation ended up between the logic layer and the UI. Because
all the real work lives in `pawpal_system.py`, I could test everything from the terminal before I ever
touched Streamlit, and wiring up the app at the end was almost boring — it just called methods that
already worked.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd improve the conflict detection so it understands durations and catches real overlaps, not just
identical start times. I'd also add input validation for the time field so a typo can't slip a bad
"HH:MM" string into the scheduler.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest thing I learned is that designing the structure first — the classes and the UML — made
everything afterward easier, and that I get much better results from AI when I'm specific and verify
its output with tests instead of trusting it. I was the one making the design calls; the AI was fast
hands, but I still had to catch the things it got wrong (like the priority sort).

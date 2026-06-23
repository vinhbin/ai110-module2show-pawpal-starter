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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

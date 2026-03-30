# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

To start the project, I read the README.md to understand the full scope of PawPal+. The scenario described a busy pet owner who needs help staying consistent with pet care. The app needs to collect basic owner and pet information, allow the user to add and edit care tasks (like walks, feeding, medications, grooming, and enrichment), and then generate a daily schedule based on constraints like available time and task priority. The plan should also explain why it was generated that way.

From this, I identified the following core classes for my initial UML design:

- **Owner** — stores the owner's name and available time per day
- **Pet** — stores the pet's name, species, and any special needs
- **Task** — represents a single care task with attributes for name, duration, priority, and category
- **Scheduler** — takes a list of tasks and constraints and produces an ordered daily plan
- **Plan** — holds the output of the scheduler: the ordered list of tasks and the reasoning behind the selection

The **Scheduler** was identified as the most critical class since it contains the core logic. **Task** objects flow into it, and a **Plan** object comes out. **Owner** and **Pet** serve as context that the Scheduler can use to apply constraints.

**b. Design changes**

Yes, one change was made after reviewing the initial skeleton against the UML spec.

**`_filter_feasible` return type corrected from `list[Task]` to `tuple[list[Task], list[Task]]`**

The initial skeleton declared `_filter_feasible` as returning a single `list[Task]`. During review, I identified that this was incorrect: the method must return *two* lists — one for tasks that fit within the remaining time budget, and one for tasks that were skipped. Without the tuple return, `generate_plan` would have no way to populate `plan.skipped_tasks`, silently dropping skipped tasks from the output. The fix aligns the return type with both the UML spec and the scheduling contract described in `agent.md`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

**Tradeoff: Named time slots instead of exact start/end times**

The scheduler assigns tasks to broad named slots — `morning`, `afternoon`, `evening`, or `any` — rather than tracking precise start and end times (e.g., 8:00–8:30 AM). Conflict detection checks whether the *total minutes* in a slot exceed a recommended budget, and whether a single pet has more than one task in the same slot. It does not check whether two tasks' durations would literally overlap on a clock.

This means two tasks in the `morning` slot each taking 20 minutes are flagged as a same-pet conflict, even if they could be scheduled back-to-back at 7:00 and 7:20 without any real overlap. Conversely, two tasks totalling exactly 45 minutes pass without a conflict warning even though fitting them both in might leave no buffer for the owner.

This tradeoff is reasonable for a home pet-care scenario because the target user is not managing a hospital schedule — they're fitting care routines around a flexible morning or evening. The slot model is simpler to reason about, easier to display, and avoids requiring the owner to input precise clock times for every task. The budget-overrun warning still surfaces situations where a slot is genuinely overloaded, giving the owner useful feedback without demanding minute-by-minute precision they don't actually need.

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

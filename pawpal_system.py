"""
PawPal+ Logic Layer
All backend classes for the pet care scheduling system.
"""

from collections import defaultdict
from datetime import date, timedelta


# Slot order for time-of-day sorting
_SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}

# Recommended maximum minutes per named time slot
_SLOT_BUDGETS = {"morning": 45, "afternoon": 30, "evening": 30}

# How far ahead each recurring frequency schedules its next occurrence
_RECUR_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


class Task:
    """Represents a single care activity."""

    VALID_FREQUENCIES = {"daily", "weekly", "as-needed"}
    VALID_TIME_SLOTS = {"morning", "afternoon", "evening", "any"}

    def __init__(
        self,
        name: str,
        category: str,
        duration_minutes: int,
        priority: int,
        frequency: str = "daily",
        required: bool = False,
        notes: str = "",
        time_slot: str = "any",
        scheduled_day: str = "",
        due_date: "date | None" = None,
    ):
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be > 0")
        if not (1 <= priority <= 5):
            raise ValueError("priority must be between 1 (highest) and 5 (lowest)")
        if frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {self.VALID_FREQUENCIES}")
        if time_slot not in self.VALID_TIME_SLOTS:
            raise ValueError(f"time_slot must be one of {self.VALID_TIME_SLOTS}")

        self.name = name
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.frequency = frequency
        self.required = required
        self.notes = notes
        self.time_slot = time_slot
        self.scheduled_day = scheduled_day.lower()  # e.g. "monday", "wednesday"
        self.due_date: date = due_date if due_date is not None else date.today()
        self.completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Clear completion status (e.g. at start of a new day)."""
        self.completed = False

    def clone_for_next_occurrence(self) -> "Task | None":
        """
        Return a fresh, incomplete copy of this task due on its next occurrence.

        The new task is identical in every attribute except `completed` (reset to
        False) and `due_date` (advanced by the frequency's timedelta via
        `_RECUR_DELTA`).  Returns None for 'as-needed' tasks, which are never
        auto-scheduled.

        Returns:
            Task: a new Task instance with due_date advanced by 1 day (daily)
                  or 7 days (weekly).
            None: if frequency is 'as-needed'.
        """
        delta = _RECUR_DELTA.get(self.frequency)
        if delta is None:  # as-needed — never auto-recur
            return None

        next_due = self.due_date + delta
        return Task(
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            required=self.required,
            notes=self.notes,
            time_slot=self.time_slot,
            scheduled_day=self.scheduled_day,
            due_date=next_due,
        )

    def is_feasible(self, remaining_minutes: int) -> bool:
        """Return True if this task fits within the remaining time budget."""
        return self.duration_minutes <= remaining_minutes

    def __repr__(self) -> str:
        slot_tag = f", {self.time_slot}" if self.time_slot != "any" else ""
        status = " [DONE]" if self.completed else ""
        required_tag = " [REQUIRED]" if self.required else ""
        return (
            f"[P{self.priority}] {self.name} ({self.duration_minutes} min, "
            f"{self.frequency}{slot_tag}, due {self.due_date}){required_tag}{status}"
        )


class Pet:
    """Represents the animal being cared for. Owns its own task list."""

    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.special_needs: list[str] = []
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, name: str) -> bool:
        """Remove a task by name; returns False if not found."""
        for task in self.tasks:
            if task.name == name:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.completed]

    def add_special_need(self, need: str) -> None:
        """Register a special care requirement if not already listed."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def has_special_need(self, need: str) -> bool:
        """Return True if this pet has the given special need (case-insensitive)."""
        return any(need.lower() == n.lower() for n in self.special_needs)

    def __repr__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age})"


class Owner:
    """Manages multiple pets and their tasks."""

    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: list[str] = []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name; returns False if not found."""
        for pet in self.pets:
            if pet.name == name:
                self.pets.remove(pet)
                return True
        return False

    def get_pet(self, name: str) -> "Pet | None":
        """Look up a pet by name; returns None if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[tuple["Pet", Task]]:
        """Return every (pet, task) pair across all owned pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def set_available_time(self, minutes: int) -> None:
        """Update the owner's daily time budget in minutes."""
        if minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        self.available_minutes = minutes

    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference category if not already listed."""
        if preference not in self.preferences:
            self.preferences.append(preference)

    def prefers(self, category: str) -> bool:
        """Return True if the category matches any of the owner's preferences."""
        return any(category.lower() in p.lower() for p in self.preferences)

    def __repr__(self) -> str:
        return f"Owner({self.name!r}, {len(self.pets)} pet(s), {self.available_minutes} min/day)"


class Plan:
    """The output of a scheduling run."""

    def __init__(self):
        self.scheduled_tasks: list[tuple[Pet, Task]] = []
        self.skipped_tasks: list[tuple[Pet, Task]] = []
        self.reasoning: list[str] = []
        self.conflicts: list[str] = []

    @property
    def total_duration(self) -> int:
        """Sum of duration_minutes across all scheduled tasks."""
        return sum(task.duration_minutes for _, task in self.scheduled_tasks)

    def add_reasoning(self, note: str) -> None:
        """Append a human-readable explanation note to the plan."""
        self.reasoning.append(note)

    def get_summary(self) -> str:
        """Return a one-line overview."""
        n_scheduled = len(self.scheduled_tasks)
        n_skipped = len(self.skipped_tasks)
        n_conflicts = len(self.conflicts)
        base = (
            f"{n_scheduled} task(s) scheduled ({self.total_duration} min); "
            f"{n_skipped} skipped"
        )
        if n_conflicts:
            base += f"; {n_conflicts} conflict(s) detected"
        return base

    def display(self) -> str:
        """Return the full formatted plan string."""
        lines = ["=== PawPal+ Daily Plan ===", ""]

        if self.scheduled_tasks:
            lines.append("Scheduled Tasks:")
            for pet, task in self.scheduled_tasks:
                lines.append(f"  [{pet.name}] {task}")
            lines.append(f"\nTotal Time: {self.total_duration} min")
        else:
            lines.append("No tasks scheduled.")

        if self.skipped_tasks:
            lines.append("\nSkipped Tasks:")
            for pet, task in self.skipped_tasks:
                lines.append(f"  [{pet.name}] {task}")

        if self.conflicts:
            lines.append("\nConflicts Detected:")
            for c in self.conflicts:
                lines.append(f"  ! {c}")

        if self.reasoning:
            lines.append("\nReasoning:")
            for note in self.reasoning:
                lines.append(f"  - {note}")

        lines.append("")
        lines.append(self.get_summary())
        return "\n".join(lines)


class Scheduler:
    """Brain that retrieves, organizes, and schedules tasks across all pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # --- task access ---

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete tasks across all pets."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks() if not task.completed]

    def get_tasks_for_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs for a specific pet by name."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if pet.name.lower() == pet_name.lower()
        ]

    def get_tasks_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs matching the given completion status."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.completed == completed
        ]

    def mark_task_complete(self, pet_name: str, task_name: str) -> bool:
        """
        Mark a specific task as completed and, for recurring tasks, automatically
        add a new instance for the next occurrence. Returns False if not found.
        """
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False
        for task in pet.tasks:
            if task.name == task_name:
                task.mark_complete()
                next_task = task.clone_for_next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return True
        return False

    def reset_all_tasks(self) -> None:
        """Clear completion status on all tasks (e.g. start of a new day)."""
        for _, task in self.owner.get_all_tasks():
            task.reset()

    # --- plan generation ---

    def generate_plan(self, day_of_week: str = "") -> Plan:
        """
        Build and return a Plan by scheduling pending tasks within the owner's
        time budget. Pass day_of_week (e.g. 'monday') to filter recurring tasks.
        """
        plan = Plan()
        pending = self.get_pending_tasks()

        # 1. Filter by frequency / day
        active, excluded = self._filter_by_frequency(pending, day_of_week)
        for pet, task in excluded:
            day_info = f" ({task.scheduled_day})" if task.scheduled_day else ""
            plan.add_reasoning(
                f"[{pet.name}] '{task.name}' excluded — {task.frequency}{day_info} "
                f"not applicable today."
            )

        # 2. Split required vs optional
        required_pairs, optional_pairs = self._separate_required(active)

        for pet, task in required_pairs:
            plan.scheduled_tasks.append((pet, task))
            plan.add_reasoning(f"[{pet.name}] '{task.name}' is required — always included.")

        remaining = self.owner.available_minutes - plan.total_duration

        # 3. If required tasks already bust the budget, skip optional pipeline
        if remaining < 0:
            plan.add_reasoning(
                f"Required tasks exceed available time by {abs(remaining)} min. "
                f"All optional tasks skipped."
            )
            plan.skipped_tasks.extend(optional_pairs)
            plan.conflicts = self._detect_conflicts(plan.scheduled_tasks)
            return plan

        # 4. Sort optional tasks: time slot → priority → preference → duration
        # _apply_preferences sorts by (slot, priority, preferred, duration) which
        # is a superset of _sort_by_time_slot — no need to pre-sort.
        sorted_optional = self._apply_preferences(optional_pairs)

        # 5. Greedy fill — does NOT bail on first skip; tries all remaining tasks
        feasible, skipped = self._filter_feasible(sorted_optional, remaining)

        plan.scheduled_tasks.extend(feasible)
        plan.skipped_tasks.extend(skipped)

        # 6. Sort all scheduled tasks by time slot for display
        plan.scheduled_tasks = self._sort_by_time_slot(plan.scheduled_tasks)

        # 7. Log per-task reasoning with accurate remaining budget
        budget = remaining
        for pet, task in feasible:
            plan.add_reasoning(
                f"[{pet.name}] '{task.name}' scheduled "
                f"(priority {task.priority}, {task.duration_minutes} min, "
                f"{task.time_slot} slot, {budget} min remaining)."
            )
            budget -= task.duration_minutes

        for pet, task in skipped:
            plan.add_reasoning(
                f"[{pet.name}] '{task.name}' skipped — "
                f"needs {task.duration_minutes} min, only {budget} min left."
            )

        # 8. Detect conflicts in the final scheduled set
        plan.conflicts = self._detect_conflicts(plan.scheduled_tasks)

        return plan

    # --- private helpers ---

    def _filter_by_frequency(
        self, pairs: list[tuple[Pet, Task]], day_of_week: str
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task]]]:
        """
        Partition (pet, task) pairs into active and excluded lists based on
        each task's frequency and today's day of the week.

        Rules:
          - 'daily'     → always active regardless of day_of_week.
          - 'weekly'    → active only when task.scheduled_day matches
                          day_of_week (case-insensitive); included if either
                          value is empty (no day filter applied).
          - 'as-needed' → always excluded; must be added to a plan manually.

        Args:
            pairs:       All (pet, task) pairs to evaluate.
            day_of_week: Lowercase weekday string, e.g. 'monday'. Pass ''
                         to skip day-based filtering for weekly tasks.

        Returns:
            A tuple of (active, excluded) pair lists.
        """
        active: list[tuple[Pet, Task]] = []
        excluded: list[tuple[Pet, Task]] = []
        today = day_of_week.lower()

        for pet, task in pairs:
            if task.frequency == "as-needed":
                excluded.append((pet, task))
            elif task.frequency == "weekly":
                if task.scheduled_day and today and task.scheduled_day != today:
                    excluded.append((pet, task))
                else:
                    active.append((pet, task))
            else:  # daily
                active.append((pet, task))

        return active, excluded

    def _separate_required(
        self, pairs: list[tuple[Pet, Task]]
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task]]]:
        """
        Partition pairs into required and optional lists in a single pass.

        Required tasks (task.required == True) are always scheduled before
        the time-budget check; optional tasks are only added if budget permits.

        Args:
            pairs: Active (pet, task) pairs to partition.

        Returns:
            A tuple of (required, optional) pair lists.
        """
        required: list[tuple[Pet, Task]] = []
        optional: list[tuple[Pet, Task]] = []
        for pair in pairs:
            (required if pair[1].required else optional).append(pair)
        return required, optional

    def _sort_by_time_slot(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """
        Sort tasks by time slot then priority for display ordering.

        Slot order: morning (0) → afternoon (1) → evening (2) → any (3).
        Within the same slot, lower priority numbers sort first (P1 before P5).

        Args:
            pairs: (pet, task) pairs to sort.

        Returns:
            A new sorted list; the input is not modified.
        """
        return sorted(
            pairs,
            key=lambda pt: (_SLOT_ORDER.get(pt[1].time_slot, 3), pt[1].priority),
        )

    def _apply_preferences(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """
        Sort tasks by slot, priority, owner preference, and duration.

        Sort key (ascending): (slot_order, priority, preferred, duration_minutes)
          - slot_order:  morning=0 … any=3  (same as _sort_by_time_slot)
          - priority:    1 (highest) sorts before 5 (lowest)
          - preferred:   0 if owner.prefers(category) else 1  — preferred first
          - duration:    shorter tasks first within the same tier, maximising
                         the number of tasks that fit the remaining budget

        This is a superset of _sort_by_time_slot, so no pre-sort is needed.

        Args:
            pairs: Optional (pet, task) pairs to order.

        Returns:
            A new sorted list; the input is not modified.
        """
        def sort_key(pt: tuple[Pet, Task]) -> tuple:
            preferred = 0 if self.owner.prefers(pt[1].category) else 1
            return (
                _SLOT_ORDER.get(pt[1].time_slot, 3),
                pt[1].priority,
                preferred,
                pt[1].duration_minutes,  # shorter first within same tier
            )

        return sorted(pairs, key=sort_key)

    def _filter_feasible(
        self, pairs: list[tuple[Pet, Task]], remaining_minutes: int
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task]]]:
        """
        Greedily fill the time budget, never bailing early on a skip.

        Each task is tested with task.is_feasible(budget). If it fits, it is
        added to feasible and the budget is reduced. If it doesn't fit, it is
        added to skipped and the loop continues — a shorter task later in the
        list can still be scheduled even after a longer one is skipped.

        Args:
            pairs:             Sorted (pet, task) pairs to evaluate.
            remaining_minutes: Time budget available after required tasks.

        Returns:
            A tuple of (feasible, skipped) pair lists.
        """
        feasible: list[tuple[Pet, Task]] = []
        skipped: list[tuple[Pet, Task]] = []
        budget = remaining_minutes

        for pet, task in pairs:
            if task.is_feasible(budget):
                feasible.append((pet, task))
                budget -= task.duration_minutes
            else:
                skipped.append((pet, task))

        return feasible, skipped

    def _detect_conflicts(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[str]:
        """
        Scan the scheduled set for three classes of conflict and return warnings.

        Checks (in order, per named slot):
          1. Same-pet slot overlap — a single pet has 2+ tasks in the same
             named slot; a pet can only do one thing at a time.
          2. Slot budget overrun — total scheduled minutes in a slot exceeds
             the recommended budget (morning: 45, afternoon: 30, evening: 30).
          3. Required-task collision — two or more required tasks share the
             same named slot.

        Tasks with time_slot='any' are excluded from all checks.
        No exception is raised; the returned list is empty when there are no
        issues, so callers can always iterate over it safely.

        Args:
            pairs: The final scheduled (pet, task) pairs to inspect.

        Returns:
            A list of human-readable warning strings (empty = no conflicts).
        """
        conflicts: list[str] = []
        slot_groups: dict[str, list[tuple[Pet, Task]]] = defaultdict(list)

        for pet, task in pairs:
            if task.time_slot != "any":
                slot_groups[task.time_slot].append((pet, task))

        for slot, slot_pairs in slot_groups.items():

            # 1. Same-pet slot overlap
            pet_task_counts: dict[str, list[str]] = defaultdict(list)
            for pet, task in slot_pairs:
                pet_task_counts[pet.name].append(task.name)
            for pet_name, task_names in pet_task_counts.items():
                if len(task_names) > 1:
                    names_str = ", ".join(f"'{n}'" for n in task_names)
                    conflicts.append(
                        f"Same-pet conflict: [{pet_name}] has {len(task_names)} tasks "
                        f"in the {slot} slot ({names_str}) — only one can run at a time."
                    )

            # 2. Slot budget overrun
            total = sum(t.duration_minutes for _, t in slot_pairs)
            budget = _SLOT_BUDGETS.get(slot, 60)
            if total > budget:
                conflicts.append(
                    f"{slot.capitalize()} slot overloaded: "
                    f"{total} min scheduled vs. {budget} min recommended."
                )

            # 3. Multiple required tasks in same slot
            required_in_slot = [(p, t) for p, t in slot_pairs if t.required]
            if len(required_in_slot) > 1:
                names = ", ".join(
                    f"[{p.name}] {t.name}" for p, t in required_in_slot
                )
                conflicts.append(
                    f"Multiple required tasks in {slot} slot: {names}."
                )

        return conflicts

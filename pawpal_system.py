"""
PawPal+ Logic Layer
All backend classes for the pet care scheduling system.
"""


class Task:
    """Represents a single care activity."""

    VALID_FREQUENCIES = {"daily", "weekly", "as-needed"}

    def __init__(
        self,
        name: str,
        category: str,
        duration_minutes: int,
        priority: int,
        frequency: str = "daily",
        required: bool = False,
        notes: str = "",
    ):
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be > 0")
        if not (1 <= priority <= 5):
            raise ValueError("priority must be between 1 (highest) and 5 (lowest)")
        if frequency not in self.VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {self.VALID_FREQUENCIES}")

        self.name = name
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.frequency = frequency
        self.required = required
        self.notes = notes
        self.completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Clear completion status (e.g. at start of a new day)."""
        self.completed = False

    def is_feasible(self, remaining_minutes: int) -> bool:
        """Return True if this task fits within the remaining time budget."""
        return self.duration_minutes <= remaining_minutes

    def __repr__(self) -> str:
        """Return a concise string like '[P1] Walk (30 min, daily) [REQUIRED]'."""
        status = " [DONE]" if self.completed else ""
        required_tag = " [REQUIRED]" if self.required else ""
        return (
            f"[P{self.priority}] {self.name} ({self.duration_minutes} min, "
            f"{self.frequency}){required_tag}{status}"
        )


class Pet:
    """Represents the animal being cared for. Owns its own task list."""

    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.special_needs: list[str] = []
        self.tasks: list[Task] = []

    # --- task management ---

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

    # --- special needs ---

    def add_special_need(self, need: str) -> None:
        """Register a special care requirement if not already listed."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def has_special_need(self, need: str) -> bool:
        """Return True if this pet has the given special need (case-insensitive)."""
        return need.lower() in [n.lower() for n in self.special_needs]

    def __repr__(self) -> str:
        """Return a readable summary like 'Buddy (dog, age 4)'."""
        return f"{self.name} ({self.species}, age {self.age})"


class Owner:
    """Manages multiple pets and their tasks."""

    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: list[str] = []
        self.pets: list[Pet] = []

    # --- pet management ---

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

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name; returns None if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all owned pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    # --- time and preferences ---

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
        """Return a readable summary like 'Owner('Alex', 2 pet(s), 90 min/day)'."""
        return f"Owner({self.name!r}, {len(self.pets)} pet(s), {self.available_minutes} min/day)"


class Plan:
    """The output of a scheduling run."""

    def __init__(self):
        self.scheduled_tasks: list[tuple[Pet, Task]] = []
        self.skipped_tasks: list[tuple[Pet, Task]] = []
        self.reasoning: list[str] = []

    @property
    def total_duration(self) -> int:
        """Sum of duration_minutes across all scheduled tasks."""
        return sum(task.duration_minutes for _, task in self.scheduled_tasks)

    def add_reasoning(self, note: str) -> None:
        """Append a human-readable explanation note to the plan."""
        self.reasoning.append(note)

    def get_summary(self) -> str:
        """Return a one-line overview like '5 task(s) scheduled (120 min); 2 skipped'."""
        n_scheduled = len(self.scheduled_tasks)
        n_skipped = len(self.skipped_tasks)
        return (
            f"{n_scheduled} task(s) scheduled ({self.total_duration} min); "
            f"{n_skipped} skipped"
        )

    def display(self) -> str:
        """Return the full formatted plan string including tasks, skipped, and reasoning."""
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

        if self.reasoning:
            lines.append("\nReasoning:")
            for note in self.reasoning:
                lines.append(f"  - {note}")

        lines.append("")
        lines.append(self.get_summary())
        return "\n".join(lines)


class Scheduler:
    """Brain that retrieves, organizes, and manages tasks across all pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # --- task access ---

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete tasks across all pets."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks() if not task.completed]

    def mark_task_complete(self, pet_name: str, task_name: str) -> bool:
        """Mark a specific task as completed. Returns False if not found."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False
        for task in pet.tasks:
            if task.name == task_name:
                task.mark_complete()
                return True
        return False

    def reset_all_tasks(self) -> None:
        """Clear completion status on all tasks (e.g. start of a new day)."""
        for _, task in self.owner.get_all_tasks():
            task.reset()

    # --- plan generation ---

    def generate_plan(self) -> Plan:
        """Build and return a Plan by scheduling pending tasks within the owner's time budget."""
        plan = Plan()
        pending = self.get_pending_tasks()

        required_pairs, optional_pairs = self._separate_required(pending)

        for pet, task in required_pairs:
            plan.scheduled_tasks.append((pet, task))
            plan.add_reasoning(f"[{pet.name}] '{task.name}' is required — always included.")

        remaining = self.owner.available_minutes - plan.total_duration
        if remaining < 0:
            plan.add_reasoning(
                f"Required tasks exceed available time by {abs(remaining)} min."
            )

        sorted_optional = self._sort_by_priority(optional_pairs)
        sorted_optional = self._apply_preferences(sorted_optional)
        feasible, skipped = self._filter_feasible(sorted_optional, remaining)

        plan.scheduled_tasks.extend(feasible)
        plan.skipped_tasks.extend(skipped)

        for pet, task in feasible:
            plan.add_reasoning(
                f"[{pet.name}] '{task.name}' scheduled "
                f"(priority {task.priority}, {task.duration_minutes} min)."
            )
        for pet, task in skipped:
            plan.add_reasoning(
                f"[{pet.name}] '{task.name}' skipped — not enough remaining time ({remaining} min left)."
            )

        return plan

    # --- private helpers ---

    def _separate_required(
        self, pairs: list[tuple[Pet, Task]]
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task]]]:
        """Split pairs into (required, optional) lists."""
        required = [(pet, t) for pet, t in pairs if t.required]
        optional = [(pet, t) for pet, t in pairs if not t.required]
        return required, optional

    def _filter_feasible(
        self, pairs: list[tuple[Pet, Task]], remaining_minutes: int
    ) -> tuple[list[tuple[Pet, Task]], list[tuple[Pet, Task]]]:
        """Greedily fill the time budget; return (feasible, skipped) pairs."""
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

    def _sort_by_priority(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """Sort tasks by priority ascending (1 = highest)."""
        return sorted(pairs, key=lambda pt: pt[1].priority)

    def _apply_preferences(
        self, pairs: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """Within each priority tier, move owner-preferred categories to the front."""
        def sort_key(pt: tuple[Pet, Task]):
            preferred = 0 if self.owner.prefers(pt[1].category) else 1
            return (pt[1].priority, preferred)
        return sorted(pairs, key=sort_key)

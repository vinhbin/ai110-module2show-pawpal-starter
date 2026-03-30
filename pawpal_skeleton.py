"""
PawPal+ — Class Skeleton
Names, attributes, and empty method stubs based on the UML design in agent.md.
"""


class Owner:
    """Represents the person caring for the pet."""

    def __init__(self, name: str, available_minutes: int):
        self.name: str = name
        self.available_minutes: int = available_minutes
        self.preferences: list[str] = []

    def set_available_time(self, minutes: int) -> None:
        pass

    def add_preference(self, preference: str) -> None:
        pass

    def prefers(self, category: str) -> bool:
        pass


class Pet:
    """Represents the animal being cared for."""

    def __init__(self, name: str, species: str, age: int):
        self.name: str = name
        self.species: str = species
        self.age: int = age
        self.special_needs: list[str] = []

    def add_special_need(self, need: str) -> None:
        pass

    def has_special_need(self, need: str) -> bool:
        pass

    def __repr__(self) -> str:
        pass


class Task:
    """Represents a single care activity."""

    def __init__(
        self,
        name: str,
        category: str,
        duration_minutes: int,
        priority: int,
        required: bool = False,
        notes: str = "",
    ):
        self.name: str = name
        self.category: str = category
        self.duration_minutes: int = duration_minutes
        self.priority: int = priority
        self.required: bool = required
        self.notes: str = notes

    def is_feasible(self, remaining_minutes: int) -> bool:
        pass

    def __repr__(self) -> str:
        pass


class Plan:
    """The output of a scheduling run."""

    def __init__(self):
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: list[str] = []

    @property
    def total_duration(self) -> int:
        pass

    def add_reasoning(self, note: str) -> None:
        pass

    def display(self) -> str:
        pass

    def get_summary(self) -> str:
        pass


class Scheduler:
    """Core engine that turns tasks + constraints into a plan."""

    def __init__(self, owner: Owner, pet: Pet):
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, name: str) -> bool:
        pass

    def generate_plan(self) -> Plan:
        pass

    def _separate_required(
        self, tasks: list[Task]
    ) -> tuple[list[Task], list[Task]]:
        pass

    def _filter_feasible(
        self, tasks: list[Task], remaining_minutes: int
    ) -> list[Task]:
        pass

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def _apply_preferences(self, tasks: list[Task]) -> list[Task]:
        pass

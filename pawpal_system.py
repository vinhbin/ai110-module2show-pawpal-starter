"""PawPal+ logic layer: Owner/Pet/Task/Scheduler for pet-care planning."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as _date, timedelta
from enum import IntEnum


class Priority(IntEnum):
    """Task importance; higher value = higher priority."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """A single pet-care activity with a time, duration, priority, and frequency."""
    title: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    time: str = "09:00"
    frequency: str = "once"
    completed: bool = False
    date: str = "2026-01-01"

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return the next recurrence of this task, or None if it does not repeat."""
        deltas = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        step = deltas.get(self.frequency)
        if step is None:
            return None
        current = _date.fromisoformat(self.date)
        nxt = (current + step).isoformat()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            date=nxt,
        )


@dataclass
class Pet:
    """A pet owned by an Owner, holding its own list of care tasks."""
    name: str
    species: str = "dog"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner managing one or more pets and their tasks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> "Pet | None":
        """Find a pet by name, or None."""
        return next((p for p in self.pets if p.name == name), None)

    def all_tasks(self) -> list[Task]:
        """Flatten every task across all pets."""
        return [t for p in self.pets for t in p.tasks]

    def all_tasks_with_pet(self) -> list[tuple[Pet, Task]]:
        """Flatten tasks paired with their owning pet (for display/conflicts)."""
        return [(p, t) for p in self.pets for t in p.tasks]


class Scheduler:
    """The brain: organizes, sorts, filters, and validates an owner's tasks."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self) -> list[Task]:
        """Return all tasks ordered by start time."""
        return sorted(self.owner.all_tasks(), key=lambda t: t.time)

    def sort_by_priority(self) -> list[Task]:
        """Return all tasks ordered by priority (high first), then time."""
        return sorted(
            self.owner.all_tasks(),
            key=lambda t: (-int(t.priority), t.time),
        )

    def filter_tasks(self, *, pet_name=None, completed=None) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        if pet_name is not None:
            pet = self.owner.get_pet(pet_name)
            tasks = list(pet.tasks) if pet else []
        else:
            tasks = self.owner.all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def mark_task_complete(self, task: Task) -> "Task | None":
        """Complete a task; if it recurs, spawn and return the next occurrence."""
        task.mark_complete()
        nxt = task.next_occurrence()
        if nxt is None:
            return None
        for pet in self.owner.pets:
            if task in pet.tasks:
                pet.add_task(nxt)
                break
        return nxt

    def detect_conflicts(self) -> list[str]:
        """Return human-readable warnings for tasks scheduled at the same time."""
        seen: dict[str, str] = {}   # time -> first task label
        warnings: list[str] = []
        for pet, task in self.owner.all_tasks_with_pet():
            label = f"{pet.name}'s '{task.title}'"
            if task.time in seen:
                warnings.append(
                    f"Conflict at {task.time}: {seen[task.time]} overlaps with {label}."
                )
            else:
                seen[task.time] = label
        return warnings

    def next_available_slot(self, duration_minutes, day_start="06:00", day_end="22:00") -> "str | None":
        """Return the earliest 'HH:MM' that fits a task of the given duration, or None."""
        raise NotImplementedError

    def todays_schedule(self) -> list[Task]:
        """Return today's plan, sorted by priority then time."""
        raise NotImplementedError


def save_to_json(owner: Owner, path: str) -> None:
    """Persist an owner (and nested pets/tasks) to a JSON file."""
    raise NotImplementedError


def load_from_json(path: str) -> Owner:
    """Reconstruct an Owner from a JSON file written by save_to_json."""
    raise NotImplementedError

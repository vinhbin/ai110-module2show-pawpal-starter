from datetime import date, timedelta

import pytest

from pawpal_system import Task, Pet, Owner, Scheduler, Plan


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning Walk", "walk", duration_minutes=30, priority=1)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog", 4)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority=2))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Evening Walk", "walk", duration_minutes=20, priority=3))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scheduler(available_minutes=120):
    owner = Owner("Alex", available_minutes)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    return Scheduler(owner), pet


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_slot_order():
    """Tasks should come out morning → afternoon → evening → any."""
    _, pet = make_scheduler()
    scheduler = Scheduler(pet.__class__.__new__(pet.__class__))  # avoid reuse

    owner = Owner("Alex", 120)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    evening = Task("Bath", "grooming", 20, priority=1, time_slot="evening")
    morning = Task("Walk", "walk", 30, priority=1, time_slot="morning")
    any_slot = Task("Training", "enrichment", 10, priority=1, time_slot="any")
    afternoon = Task("Meds", "meds", 5, priority=1, time_slot="afternoon")

    for t in [evening, morning, any_slot, afternoon]:
        pet.add_task(t)

    plan = scheduler.generate_plan()
    slots = [task.time_slot for _, task in plan.scheduled_tasks]
    # any slot always last; named slots in order
    named = [s for s in slots if s != "any"]
    assert named == sorted(named, key=lambda s: {"morning": 0, "afternoon": 1, "evening": 2}[s])
    assert slots[-1] == "any" or "any" not in slots


def test_sort_priority_within_same_slot():
    """Within the same time slot, lower priority number (higher urgency) sorts first."""
    owner = Owner("Alex", 120)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    low_pri = Task("Brush", "grooming", 10, priority=4, time_slot="morning")
    high_pri = Task("Insulin", "meds", 5, priority=1, time_slot="morning")

    pet.add_task(low_pri)
    pet.add_task(high_pri)

    plan = scheduler.generate_plan()
    morning_tasks = [task for _, task in plan.scheduled_tasks if task.time_slot == "morning"]
    assert morning_tasks[0].priority < morning_tasks[1].priority


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_clone_has_next_day_due_date():
    """Completing a daily task should produce a clone due tomorrow."""
    scheduler, pet = make_scheduler()
    today = date.today()
    task = Task("Morning Walk", "walk", 30, priority=1, frequency="daily", due_date=today)
    pet.add_task(task)

    scheduler.mark_task_complete("Buddy", "Morning Walk")

    new_tasks = [t for t in pet.tasks if t.name == "Morning Walk" and not t.completed]
    assert len(new_tasks) == 1
    assert new_tasks[0].due_date == today + timedelta(days=1)


def test_weekly_task_clone_has_next_week_due_date():
    """Completing a weekly task should produce a clone due in 7 days."""
    scheduler, pet = make_scheduler()
    today = date.today()
    task = Task("Bath", "grooming", 20, priority=2, frequency="weekly",
                scheduled_day="monday", due_date=today)
    pet.add_task(task)

    scheduler.mark_task_complete("Buddy", "Bath")

    new_tasks = [t for t in pet.tasks if t.name == "Bath" and not t.completed]
    assert len(new_tasks) == 1
    assert new_tasks[0].due_date == today + timedelta(weeks=1)


def test_as_needed_task_creates_no_clone():
    """Completing an as-needed task should NOT add a follow-up task."""
    scheduler, pet = make_scheduler()
    task = Task("Vet Visit", "meds", 60, priority=1, frequency="as-needed")
    pet.add_task(task)
    initial_count = len(pet.tasks)

    scheduler.mark_task_complete("Buddy", "Vet Visit")

    assert len(pet.tasks) == initial_count  # no new task added


def test_completed_task_excluded_from_pending():
    """A completed task should not appear in get_pending_tasks."""
    scheduler, pet = make_scheduler()
    task = Task("Walk", "walk", 30, priority=1, frequency="daily")
    pet.add_task(task)

    scheduler.mark_task_complete("Buddy", "Walk")

    pending_names = [t.name for _, t in scheduler.get_pending_tasks() if t.name == "Walk"]
    # The original is done; only the cloned (incomplete) instance counts
    assert all(not t.completed for _, t in scheduler.get_pending_tasks())


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_same_pet_slot_conflict_detected():
    """Two tasks for the same pet in the same named slot should raise a conflict."""
    owner = Owner("Alex", 120)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    pet.add_task(Task("Walk", "walk", 20, priority=1, time_slot="morning"))
    pet.add_task(Task("Brush", "grooming", 15, priority=2, time_slot="morning"))

    plan = scheduler.generate_plan()
    assert any("Same-pet conflict" in c for c in plan.conflicts)


def test_slot_overrun_conflict_detected():
    """Total morning minutes > 45 should flag a slot overrun conflict."""
    owner = Owner("Alex", 200)
    pet1 = Pet("Buddy", "dog", 4)
    pet2 = Pet("Mittens", "cat", 3)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner)

    pet1.add_task(Task("Long Walk", "walk", 30, priority=1, time_slot="morning"))
    pet2.add_task(Task("Feeding", "feeding", 20, priority=2, time_slot="morning"))

    plan = scheduler.generate_plan()
    assert any("overloaded" in c.lower() for c in plan.conflicts)


def test_required_collision_conflict_detected():
    """Two required tasks in the same named slot should flag a required collision."""
    owner = Owner("Alex", 200)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    pet.add_task(Task("Insulin", "meds", 5, priority=1, required=True, time_slot="morning"))
    pet.add_task(Task("Walk", "walk", 20, priority=2, required=True, time_slot="morning"))

    plan = scheduler.generate_plan()
    assert any("required" in c.lower() for c in plan.conflicts)


def test_any_slot_tasks_exempt_from_conflicts():
    """Tasks with time_slot='any' should never trigger conflict warnings."""
    owner = Owner("Alex", 120)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    pet.add_task(Task("Training", "enrichment", 30, priority=1, time_slot="any"))
    pet.add_task(Task("Play", "enrichment", 30, priority=2, time_slot="any"))

    plan = scheduler.generate_plan()
    assert plan.conflicts == []


# ---------------------------------------------------------------------------
# Budget / required-task guard
# ---------------------------------------------------------------------------

def test_required_tasks_always_scheduled():
    """Required tasks must appear in the plan even when optional budget is zero."""
    owner = Owner("Alex", 5)  # very tight budget
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    required = Task("Insulin", "meds", 5, priority=1, required=True)
    optional = Task("Walk", "walk", 30, priority=2, required=False)
    pet.add_task(required)
    pet.add_task(optional)

    plan = scheduler.generate_plan()
    scheduled_names = [t.name for _, t in plan.scheduled_tasks]
    assert "Insulin" in scheduled_names
    assert "Walk" not in scheduled_names


def test_greedy_fill_continues_past_skipped_task():
    """A short task that fits should be scheduled even after a long task is skipped."""
    owner = Owner("Alex", 15)
    pet = Pet("Buddy", "dog", 4)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    long_task = Task("Long Walk", "walk", 30, priority=2)
    short_task = Task("Quick Feed", "feeding", 10, priority=3)
    pet.add_task(long_task)
    pet.add_task(short_task)

    plan = scheduler.generate_plan()
    scheduled_names = [t.name for _, t in plan.scheduled_tasks]
    assert "Quick Feed" in scheduled_names
    assert "Long Walk" not in scheduled_names


# ---------------------------------------------------------------------------
# Frequency filtering
# ---------------------------------------------------------------------------

def test_as_needed_excluded_from_plan():
    """as-needed tasks must never appear in scheduled or considered tasks."""
    scheduler, pet = make_scheduler()
    pet.add_task(Task("Vet Visit", "meds", 60, priority=1, frequency="as-needed"))

    plan = scheduler.generate_plan()
    all_names = [t.name for _, t in plan.scheduled_tasks + plan.skipped_tasks]
    assert "Vet Visit" not in all_names


def test_weekly_task_excluded_on_wrong_day():
    """A weekly task scheduled for Monday should be excluded on Tuesday."""
    scheduler, pet = make_scheduler()
    pet.add_task(Task("Bath", "grooming", 20, priority=2,
                      frequency="weekly", scheduled_day="monday"))

    plan = scheduler.generate_plan(day_of_week="tuesday")
    all_names = [t.name for _, t in plan.scheduled_tasks + plan.skipped_tasks]
    assert "Bath" not in all_names


def test_weekly_task_included_on_correct_day():
    """A weekly task scheduled for Monday should appear when day_of_week='monday'."""
    scheduler, pet = make_scheduler()
    pet.add_task(Task("Bath", "grooming", 20, priority=2,
                      frequency="weekly", scheduled_day="monday"))

    plan = scheduler.generate_plan(day_of_week="monday")
    all_names = [t.name for _, t in plan.scheduled_tasks + plan.skipped_tasks]
    assert "Bath" in all_names


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_task_rejects_zero_duration():
    with pytest.raises(ValueError):
        Task("Bad", "walk", duration_minutes=0, priority=1)


def test_task_rejects_invalid_priority():
    with pytest.raises(ValueError):
        Task("Bad", "walk", duration_minutes=10, priority=6)


def test_task_rejects_invalid_frequency():
    with pytest.raises(ValueError):
        Task("Bad", "walk", duration_minutes=10, priority=1, frequency="hourly")


def test_owner_rejects_negative_available_minutes():
    owner = Owner("Alex", 60)
    with pytest.raises(ValueError):
        owner.set_available_time(-1)

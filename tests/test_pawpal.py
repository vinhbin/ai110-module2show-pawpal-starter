from pawpal_system import Priority, Task, Pet, Owner, Scheduler


def test_classes_exist_and_construct():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Walk", 30, Priority.HIGH, time="08:00")
    owner.add_pet(pet)
    pet.add_task(task)
    assert owner.name == "Jordan"
    assert pet.task_count() == 1
    assert task.priority == Priority.HIGH
    assert Scheduler(owner).owner is owner


def test_next_occurrence_daily_advances_one_day():
    t = Task("Walk", 30, frequency="daily", date="2026-01-01")
    nxt = t.next_occurrence()
    assert nxt is not None
    assert nxt.date == "2026-01-02"
    assert nxt.completed is False
    assert nxt.title == "Walk"


def test_next_occurrence_weekly_advances_seven_days():
    t = Task("Bath", 20, frequency="weekly", date="2026-01-01")
    assert t.next_occurrence().date == "2026-01-08"


def test_next_occurrence_once_returns_none():
    t = Task("Vet visit", 60, frequency="once", date="2026-01-01")
    assert t.next_occurrence() is None

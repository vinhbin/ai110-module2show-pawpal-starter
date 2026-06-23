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


def _owner_with_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Dinner", 10, Priority.HIGH, time="18:00"))
    pet.add_task(Task("Walk", 30, Priority.LOW, time="08:00"))
    pet.add_task(Task("Meds", 5, Priority.HIGH, time="08:00"))
    owner.add_pet(pet)
    return owner


def test_sort_by_time_chronological():
    s = Scheduler(_owner_with_tasks())
    times = [t.time for t in s.sort_by_time()]
    assert times == ["08:00", "08:00", "18:00"]


def test_sort_by_priority_high_first_then_time():
    s = Scheduler(_owner_with_tasks())
    ordered = s.sort_by_priority()
    # HIGH tasks first (Meds 08:00 before Dinner 18:00), then LOW Walk
    assert [t.title for t in ordered] == ["Meds", "Dinner", "Walk"]


def _multi_pet_owner():
    owner = Owner("Jordan")
    dog = Pet("Mochi", "dog")
    cat = Pet("Sushi", "cat")
    done = Task("Walk", 30, time="08:00")
    done.mark_complete()
    dog.add_task(done)
    dog.add_task(Task("Dinner", 10, time="18:00"))
    cat.add_task(Task("Litter", 5, time="07:00"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


def test_filter_by_pet_name():
    s = Scheduler(_multi_pet_owner())
    titles = {t.title for t in s.filter_tasks(pet_name="Sushi")}
    assert titles == {"Litter"}


def test_filter_by_completed_status():
    s = Scheduler(_multi_pet_owner())
    incomplete = s.filter_tasks(completed=False)
    assert {t.title for t in incomplete} == {"Dinner", "Litter"}
    complete = s.filter_tasks(completed=True)
    assert {t.title for t in complete} == {"Walk"}

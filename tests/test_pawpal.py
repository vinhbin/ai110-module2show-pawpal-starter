from pawpal_system import Task, Pet


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

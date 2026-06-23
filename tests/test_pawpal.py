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

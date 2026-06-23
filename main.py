"""PawPal+ CLI demo — verifies the logic layer end-to-end in the terminal."""
from tabulate import tabulate

from pawpal_system import Owner, Pet, Task, Priority, Scheduler

PRIORITY_ICON = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}


def status_icon(task: Task) -> str:
    return "✅" if task.completed else "⬜"


def build_demo_owner() -> Owner:
    owner = Owner("Jordan")
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")

    # Added intentionally out of order to prove sorting works.
    biscuit.add_task(Task("Evening walk", 30, Priority.MEDIUM, time="18:00", frequency="daily"))
    biscuit.add_task(Task("Morning meds", 5, Priority.HIGH, time="08:00", frequency="daily"))
    mochi.add_task(Task("Litter scoop", 5, Priority.HIGH, time="08:00"))  # conflicts w/ meds at 08:00
    mochi.add_task(Task("Play time", 15, Priority.LOW, time="12:00"))

    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    return owner


def print_schedule(scheduler: Scheduler) -> None:
    rows = []
    for pet, task in scheduler.owner.all_tasks_with_pet():
        rows.append([
            status_icon(task),
            task.time,
            f"{PRIORITY_ICON[task.priority]} {task.priority.name}",
            pet.name,
            task.title,
            f"{task.duration_minutes} min",
            task.frequency,
        ])
    # Sort the display rows by priority then time using the scheduler's ordering.
    order = {id(t): i for i, t in enumerate(scheduler.todays_schedule())}
    paired = list(zip(scheduler.owner.all_tasks(), rows))
    paired.sort(key=lambda pr: order[id(pr[0])])
    headers = ["", "Time", "Priority", "Pet", "Task", "Duration", "Repeats"]
    print(tabulate([r for _, r in paired], headers=headers, tablefmt="rounded_outline"))


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner)

    print(f"\n🐾 Today's Schedule for {owner.name}\n")
    print_schedule(scheduler)

    print("\n⚠️  Conflict check:")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for c in conflicts:
            print(f"  - {c}")
    else:
        print("  None 🎉")

    slot = scheduler.next_available_slot(30)
    print(f"\n🕒 Next free 30-min slot today: {slot}")

    print("\n🔁 Completing Biscuit's daily 'Morning meds' (should spawn tomorrow's)...")
    meds = next(t for t in owner.get_pet("Biscuit").tasks if t.title == "Morning meds")
    spawned = scheduler.mark_task_complete(meds)
    print(f"   New occurrence created for: {spawned.date if spawned else 'n/a'}\n")


if __name__ == "__main__":
    main()

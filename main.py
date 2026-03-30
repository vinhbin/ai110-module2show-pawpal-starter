from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("Alex", available_minutes=90)
owner.add_preference("walk")
owner.add_preference("feeding")

buddy = Pet("Buddy", "dog", 4)
luna = Pet("Luna", "cat", 2)

# --- Tasks for Buddy added OUT OF ORDER (evening → afternoon → morning) ---
buddy.add_task(Task("Evening Walk",  "walk",     duration_minutes=20, priority=3,
                    time_slot="evening", frequency="weekly", scheduled_day="monday"))
buddy.add_task(Task("Grooming",      "grooming", duration_minutes=20, priority=4,
                    time_slot="afternoon"))
buddy.add_task(Task("Breakfast",     "feeding",  duration_minutes=10, priority=2,
                    time_slot="morning"))
buddy.add_task(Task("Morning Walk",  "walk",     duration_minutes=30, priority=1,
                    required=True, time_slot="morning"))

# --- Tasks for Luna added OUT OF ORDER (afternoon → weekly → morning) ---
luna.add_task(Task("Playtime",       "enrichment", duration_minutes=15, priority=3,
                   time_slot="afternoon", frequency="daily"))
luna.add_task(Task("Vet Check-up",   "meds",       duration_minutes=30, priority=2,
                   frequency="weekly", scheduled_day="wednesday"))
luna.add_task(Task("Flea Treatment", "grooming",   duration_minutes=10, priority=5,
                   frequency="as-needed"))
luna.add_task(Task("Feeding",        "feeding",    duration_minutes=10, priority=2,
                   time_slot="morning"))
luna.add_task(Task("Insulin Shot",   "meds",       duration_minutes=5,  priority=1,
                   required=True, time_slot="morning", notes="0.5u before meal"))

# --- Register pets ---
owner.add_pet(buddy)
owner.add_pet(luna)

scheduler = Scheduler(owner)

# ── Show raw (unsorted) task order — as added ────────────────────────────────
print("=== Raw Task Order (as added — intentionally out of order) ===")
for pet, task in scheduler.get_all_tasks():
    print(f"  [{pet.name}] {task}")

# ── Sorting: use _sort_by_time_slot to reorder ───────────────────────────────
print("\n=== Sorted by Time Slot (morning -> afternoon -> evening -> any) ===")
sorted_tasks = scheduler._sort_by_time_slot(scheduler.get_all_tasks())
for pet, task in sorted_tasks:
    print(f"  [{pet.name}] {task}")

# ── Filter by pet name ────────────────────────────────────────────────────────
print("\n=== Tasks for Buddy ===")
for pet, task in scheduler.get_tasks_for_pet("Buddy"):
    print(f"  {task}")

print("\n=== Tasks for Luna ===")
for pet, task in scheduler.get_tasks_for_pet("Luna"):
    print(f"  {task}")

# ── Filter by status (nothing completed yet) ─────────────────────────────────
print("\n=== Pending Tasks (before any completions) ===")
for pet, task in scheduler.get_tasks_by_status(completed=False):
    print(f"  [{pet.name}] {task}")

# ── Generate plan — Monday ────────────────────────────────────────────────────
print("\n\n--- Monday Plan ---")
monday_plan = scheduler.generate_plan(day_of_week="monday")
print(monday_plan.display())

# ── Generate plan — Wednesday ─────────────────────────────────────────────────
print("\n--- Wednesday Plan ---")
scheduler.reset_all_tasks()
wednesday_plan = scheduler.generate_plan(day_of_week="wednesday")
print(wednesday_plan.display())

# ── Mark tasks complete and re-check status filter ────────────────────────────
scheduler.mark_task_complete("Buddy", "Morning Walk")
scheduler.mark_task_complete("Luna",  "Insulin Shot")

print("\n=== Completed Tasks (after marking two done) ===")
for pet, task in scheduler.get_tasks_by_status(completed=True):
    print(f"  [{pet.name}] {task}")

print("\n=== Still Pending ===")
for pet, task in scheduler.get_tasks_by_status(completed=False):
    print(f"  [{pet.name}] {task}")

# ── Conflict detection demo ───────────────────────────────────────────────────
# Two tasks for Buddy both in the morning slot → same-pet overlap warning.
# One task for Luna also in the morning slot → cross-pet slot overrun.
print("\n\n--- Conflict Detection Demo ---")

conflict_owner = Owner("Sam", available_minutes=120)

rex = Pet("Rex", "dog", 3)
rex.add_task(Task("Morning Walk",   "walk",    duration_minutes=30, priority=1,
                  required=True, time_slot="morning"))
rex.add_task(Task("Breakfast Feed", "feeding", duration_minutes=15, priority=2,
                  time_slot="morning"))   # same slot as Morning Walk → overlap

mochi = Pet("Mochi", "cat", 5)
mochi.add_task(Task("Insulin Shot", "meds",    duration_minutes=5,  priority=1,
                    required=True, time_slot="morning"))  # shares morning slot with Rex's tasks

conflict_owner.add_pet(rex)
conflict_owner.add_pet(mochi)

conflict_scheduler = Scheduler(conflict_owner)
conflict_plan = conflict_scheduler.generate_plan()

print(conflict_plan.display())

if conflict_plan.conflicts:
    print("*** Conflict warnings detected! ***")
    for warning in conflict_plan.conflicts:
        print(f"  WARNING: {warning}")
else:
    print("No conflicts detected.")

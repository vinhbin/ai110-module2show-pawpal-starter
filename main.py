from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("Alex", available_minutes=90)
owner.add_preference("walk")
owner.add_preference("feeding")

buddy = Pet("Buddy", "dog", 4)
luna = Pet("Luna", "cat", 2)

# --- Tasks for Buddy ---
buddy.add_task(Task("Morning Walk", "walk", duration_minutes=30, priority=1, required=True))
buddy.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority=2))
buddy.add_task(Task("Grooming", "grooming", duration_minutes=20, priority=4))

# --- Tasks for Luna ---
luna.add_task(Task("Insulin Shot", "meds", duration_minutes=5, priority=1, required=True, notes="0.5u before meal"))
luna.add_task(Task("Feeding", "feeding", duration_minutes=10, priority=2, frequency="daily"))
luna.add_task(Task("Playtime", "enrichment", duration_minutes=15, priority=3, frequency="daily"))

# --- Register pets with owner ---
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Schedule ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

print(plan.display())

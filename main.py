from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
owner = Owner(
    first_name="Jordan",
    last_name="Rivera",
    age=29,
    email="jordan@email.com",
    time_available=90,  # 90 minutes free today
)

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------
mochi = Pet(name="Mochi", age=3, breed="Tabby Cat")
rex = Pet(name="Rex", age=5, breed="Golden Retriever")

owner.add_pet(mochi)
owner.add_pet(rex)

# ---------------------------------------------------------------------------
# Tasks  (name, duration_minutes, description, task_type, priority)
# ---------------------------------------------------------------------------
morning_walk = Task("Morning Walk", 30, "Take Rex around the block", "walk", "high")
feed_breakfast = Task(
    "Feed Breakfast", 10, "Half cup dry food for both pets", "feed", "high"
)
meds = Task("Mochi's Meds", 5, "Administer daily thyroid tablet", "medication", "high")
grooming = Task(
    "Brush Mochi", 15, "Brush coat and check for tangles", "grooming", "medium"
)
playtime = Task("Backyard Play", 20, "Fetch and tug-of-war with Rex", "walk", "low")

rex.add_task(morning_walk)
rex.add_task(feed_breakfast)
rex.add_task(playtime)
mochi.add_task(meds)
mochi.add_task(grooming)
mochi.add_task(feed_breakfast)  # shared feeding task

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
scheduler = Scheduler(time_zone="America/Los_Angeles")
owner.set_schedule(scheduler)

plan = scheduler.create_plan(owner)
explanation = scheduler.create_explanation()

# ---------------------------------------------------------------------------
# Print Today's Schedule
# ---------------------------------------------------------------------------
print("=" * 50)
print("       PAWPAL+  —  Today's Schedule")
print("=" * 50)
print(f"Owner : {owner.first_name} {owner.last_name}")
print(f"Pets  : {', '.join(p.get_name() for p in owner.get_pets())}")
print(f"Budget: {owner.time_available} minutes available")
print("-" * 50)

if plan:
    for i, task in enumerate(plan, start=1):
        status_icon = "✓" if task.get_status() == "completed" else "○"
        print(
            f"  {i}. {status_icon} [{task.get_priority().upper():6}] "
            f"{task.get_name():<20} {task.get_duration():>3} min"
        )
else:
    print("  No tasks could be scheduled.")

print("-" * 50)
print(explanation)
print("=" * 50)

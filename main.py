from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
owner = Owner(
    first_name="Jordan",
    last_name="Rivera",
    age=29,
    email="jordan@email.com",
    time_available=90,
)

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------
mochi = Pet(name="Mochi", age=3, breed="Tabby Cat")
rex   = Pet(name="Rex",   age=5, breed="Golden Retriever")

owner.add_pet(mochi)
owner.add_pet(rex)

# ---------------------------------------------------------------------------
# Tasks — added INTENTIONALLY OUT OF CHRONOLOGICAL ORDER to demo sort_by_time
# (name, duration, description, task_type, priority, status, start_time, ...)
# ---------------------------------------------------------------------------
playtime     = Task("Backyard Play",   20, "Fetch and tug-of-war",          "walk",        "low",    start_time="15:00")
morning_walk = Task("Morning Walk",    30, "Take Rex around the block",      "walk",        "high",   start_time="07:30")
feed_pm      = Task("Evening Feed",    10, "Half cup dry food",              "feed",        "high",   start_time="17:00",
                    is_recurring=True, recurrence_days=1)
meds         = Task("Mochi's Meds",    5,  "Administer daily thyroid tablet","medication",  "high",   start_time="09:00",
                    is_recurring=True, recurrence_days=1)
feed_am      = Task("Morning Feed",    10, "Half cup dry food",              "feed",        "high",   start_time="08:00",
                    is_recurring=True, recurrence_days=1)
grooming     = Task("Brush Mochi",     15, "Brush coat, check for tangles",  "grooming",    "medium", start_time="11:30")

# Attach tasks to pets (out of time order — sort_by_time will fix the display)
rex.add_task(playtime)       # 15:00 added before
rex.add_task(morning_walk)   # 07:30 added second
rex.add_task(feed_pm)        # 17:00

mochi.add_task(meds)         # 09:00
mochi.add_task(grooming)     # 11:30
mochi.add_task(feed_am)      # 08:00 — added last

# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------
scheduler = Scheduler(time_zone="America/Los_Angeles")
owner.set_schedule(scheduler)

plan        = scheduler.create_plan(owner)
explanation = scheduler.create_explanation()

# ===========================================================================
# 1. TODAY'S SCHEDULE  (priority + shortest-first order)
# ===========================================================================
print("=" * 54)
print("         PAWPAL+  —  Today's Schedule")
print("=" * 54)
print(f"Owner : {owner.first_name} {owner.last_name}")
print(f"Pets  : {', '.join(p.get_name() for p in owner.get_pets())}")
print(f"Budget: {owner.time_available} minutes available")
print("-" * 54)

if plan:
    for i, task in enumerate(plan, start=1):
        icon = "✓" if task.get_status() == "completed" else "○"
        rec  = " ↻" if task.get_is_recurring() else ""
        print(f"  {i}. {icon} [{task.get_priority().upper():6}] "
              f"{task.get_name():<22} {task.get_duration():>3} min{rec}")
else:
    print("  No tasks could be scheduled.")

print("-" * 54)
print(explanation)

# ===========================================================================
# 2. SORTED BY START TIME  (chronological view using sort_by_time)
# ===========================================================================
print("\n" + "=" * 54)
print("         Sorted by Start Time (HH:MM)")
print("=" * 54)
# sort_by_time uses a lambda on start_time strings — HH:MM sorts lexicographically
# the same way it does chronologically, so "07:30" < "09:00" < "15:00" naturally
all_tasks      = owner.get_all_tasks()
sorted_by_time = scheduler.sort_by_time(all_tasks)

for task in sorted_by_time:
    time_label = task.get_start_time() or "  --  "
    rec        = " ↻" if task.get_is_recurring() else ""
    print(f"  {time_label}  {task.get_name():<24} [{task.get_priority():<6}]{rec}")

# ===========================================================================
# 3. FILTER — pending tasks only
# ===========================================================================
print("\n" + "=" * 54)
print("         Filter: Pending Tasks Only")
print("=" * 54)
pending_tasks = scheduler.filter_tasks(owner, status="pending")
for task in pending_tasks:
    print(f"  ○ {task.get_name():<24} {task.get_duration():>3} min  [{task.get_priority()}]")

# ===========================================================================
# 4. FILTER — Rex's tasks only
# ===========================================================================
print("\n" + "=" * 54)
print("         Filter: Rex's Tasks Only")
print("=" * 54)
rex_tasks = scheduler.filter_tasks(owner, pet_name="Rex")
for task in rex_tasks:
    print(f"  {task.get_name():<24} {task.get_duration():>3} min  [{task.get_priority()}]")

# ===========================================================================
# 5. CONFLICT DETECTION
# ===========================================================================
print("\n" + "=" * 54)
print("         Conflict Detection")
print("=" * 54)
conflicts = scheduler.detect_conflicts(owner)
if conflicts:
    for w in conflicts:
        print(f"  ⚠  {w}")
else:
    print("  No conflicts detected.")

print("=" * 54)

# ===========================================================================
# 6. RECURRING TASK AUTO-GENERATION
#    Mark a recurring task complete → scheduler creates the next occurrence
#    using timedelta(days=recurrence_days) from the base due date
# ===========================================================================
print("\n" + "=" * 54)
print("         Recurring Task Auto-Generation")
print("=" * 54)

print(f"Mochi tasks before completing meds : {len(mochi.get_tasks())}")
print(f"Marking '{meds.get_name()}' as complete...")

next_occurrence = scheduler.mark_task_complete(meds, mochi)

print(f"Mochi tasks after  completing meds : {len(mochi.get_tasks())}")
if next_occurrence:
    print(f"  New task auto-created : '{next_occurrence.get_name()}'")
    print(f"  Due date              : {next_occurrence.get_due_date()}   "
          f"(today + {next_occurrence.get_recurrence_days()} day)")
    print(f"  Status                : {next_occurrence.get_status()}")

print()
print("Evening Feed — daily recurring, mark complete:")
print(f"  Rex tasks before : {len(rex.get_tasks())}")
next_feed = scheduler.mark_task_complete(feed_pm, rex)
print(f"  Rex tasks after  : {len(rex.get_tasks())}")
if next_feed:
    print(f"  Next occurrence due : {next_feed.get_due_date()}")

print()
print("Morning Walk — NOT recurring (no new instance expected):")
print(f"  Rex tasks before : {len(rex.get_tasks())}")
result = scheduler.mark_task_complete(morning_walk, rex)
print(f"  Rex tasks after  : {len(rex.get_tasks())}")
print(f"  New task created : {result is not None}")

print("=" * 54)

# ===========================================================================
# 7. TIME CONFLICT DETECTION
#    Two tasks that overlap in [start_time, start_time + duration) are flagged
#    as warnings — the scheduler never crashes, it just reports the problem.
# ===========================================================================
print("\n" + "=" * 54)
print("         Time Conflict Detection")
print("=" * 54)

# Rex: vet visit 09:00 – 10:00 (60 min)
# Mochi: groomer 09:30 – 10:15 (45 min)  ← overlaps with vet visit by 30 min
vet_visit = Task("Rex Vet Visit", 60, "Annual checkup",     "appointment", "high",   start_time="09:00")
groomer   = Task("Mochi Groomer", 45, "Full groom session", "grooming",    "medium", start_time="09:30")

rex.add_task(vet_visit)
mochi.add_task(groomer)

# Rebuild the plan so detect_conflicts has fresh scheduled_names
scheduler.create_plan(owner)
conflicts = scheduler.detect_conflicts(owner)

print("Tasks added:")
print(f"  Rex   — '{vet_visit.get_name()}' @ {vet_visit.get_start_time()}, {vet_visit.get_duration()} min  (ends 10:00)")
print(f"  Mochi — '{groomer.get_name()}'   @ {groomer.get_start_time()}, {groomer.get_duration()} min  (ends 10:15)")
print(f"  Overlap window: 09:30 – 10:00\n")

time_conflicts = [w for w in conflicts if w.startswith("Time conflict")]
print(f"Time conflicts found: {len(time_conflicts)}")
for w in time_conflicts:
    print(f"  ⚠  {w}")

print("=" * 54)

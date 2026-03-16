# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## Smarter Scheduling

Beyond the basic daily plan, PawPal+ includes four algorithmic improvements implemented in `pawpal_system.py`.

### 1. Priority + Shortest-Job-First sorting

`Scheduler.create_plan` sorts pending tasks by a two-key tuple:

```
(priority_rank, duration_minutes)
```

Tasks with the same priority are ordered shortest-first. This greedy strategy maximises the number of tasks that fit within the owner's available time budget.

### 2. Chronological view — `sort_by_time`

`Scheduler.sort_by_time(tasks)` returns any task list reordered by `start_time` (HH:MM). Because the format is zero-padded, plain string comparison produces correct chronological order. Tasks without a start time appear last. Used by the UI to display the schedule as a readable daily timeline.

### 3. Recurring task automation — `mark_task_complete`

When a recurring task (e.g. daily medication) is marked complete via `Scheduler.mark_task_complete(task, pet)`, the scheduler automatically clones it with:

- `status = "pending"`
- `due_date = base_date + timedelta(days=recurrence_days)`

The owner never has to re-enter daily or weekly tasks. One-off tasks are simply marked done with no clone created.

### 4. Conflict detection — `detect_conflicts`

`Scheduler.detect_conflicts(owner)` runs three checks and returns plain-text warnings (never raises):

| Check | What it catches |
|---|---|
| Budget overrun | Pending tasks that didn't fit in the time budget |
| Duplicate types | A pet with more than one task of the same type |
| Time overlap | Any two pending timed tasks whose windows intersect across all pets |

The time-overlap check uses the interval test `s1 < s2+d2 AND s2 < s1+d1` so partial overlaps (e.g. a 60-min vet visit at 09:00 and a 45-min groom at 09:30) are caught, not just exact same-start conflicts.

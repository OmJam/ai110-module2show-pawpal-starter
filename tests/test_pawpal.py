"""
PawPal+ test suite — covers the five core scheduling behaviours:
  1. create_plan   — greedy priority + shortest-job-first scheduler
  2. sort_by_time  — chronological ordering by HH:MM start_time
  3. filter_tasks  — filter by pet name and/or status
  4. mark_task_complete + recurring automation
  5. detect_conflicts — budget overrun, duplicate types, time overlaps
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Shared fixtures — reusable building blocks for every test
# ---------------------------------------------------------------------------

@pytest.fixture
def scheduler():
    """A fresh Scheduler with no tasks and no existing plan."""
    return Scheduler()


@pytest.fixture
def owner():
    """An Owner with 60 minutes available and no pets attached."""
    return Owner(
        first_name="Test", last_name="User",
        age=30, email="test@test.com",
        time_available=60,
    )


@pytest.fixture
def pet():
    """A single Pet with no tasks."""
    return Pet(name="Buddy", age=3, breed="Labrador")


# ---------------------------------------------------------------------------
# 1. create_plan
# ---------------------------------------------------------------------------

class TestCreatePlan:
    """
    create_plan collects all pending tasks from every pet, sorts them by
    (priority_rank, duration), and greedily fits them within
    owner.time_available.
    """

    def test_happy_path_all_tasks_fit(self, owner, pet, scheduler):
        """All tasks fit: plan length equals number of tasks added."""
        pet.add_task(Task("Walk", 30, "", "walk",       "high"))
        pet.add_task(Task("Feed",  5, "", "feed",       "high"))
        pet.add_task(Task("Play", 10, "", "walk",       "low"))
        owner.add_pet(pet)

        plan = scheduler.create_plan(owner)

        assert len(plan) == 3

    def test_high_priority_before_low(self, owner, pet, scheduler):
        """A low-priority task is inserted first but a high-priority task
        must appear earlier in the plan output."""
        pet.add_task(Task("Play",  10, "", "walk",       "low"))   # added first
        pet.add_task(Task("Meds",   5, "", "medication", "high"))  # added second
        owner.add_pet(pet)

        plan = scheduler.create_plan(owner)

        assert plan[0].get_name() == "Meds"
        assert plan[1].get_name() == "Play"

    def test_shortest_job_first_within_same_priority(self, owner, pet, scheduler):
        """Within the same priority tier, the shorter task must be scheduled
        first (Shortest-Job-First heuristic)."""
        pet.add_task(Task("Long Walk", 30, "", "walk",       "high"))  # 30 min
        pet.add_task(Task("Quick Med",  5, "", "medication", "high"))  # 5 min
        owner.add_pet(pet)

        plan = scheduler.create_plan(owner)

        assert plan[0].get_name() == "Quick Med"

    def test_tasks_across_two_pets(self, owner, scheduler):
        """Tasks from multiple pets must all appear in the plan."""
        buddy = Pet("Buddy", 3)
        mochi = Pet("Mochi", 2)
        buddy.add_task(Task("Walk",  20, "", "walk",       "high"))
        mochi.add_task(Task("Meds",  10, "", "medication", "high"))
        owner.add_pet(buddy)
        owner.add_pet(mochi)

        plan = scheduler.create_plan(owner)

        names = [t.get_name() for t in plan]
        assert "Walk" in names
        assert "Meds" in names

    def test_zero_time_available_returns_empty_plan(self, owner, pet, scheduler):
        """With no time budget the plan must be empty."""
        owner.time_available = 0
        pet.add_task(Task("Walk", 30, "", "walk", "high"))
        owner.add_pet(pet)

        plan = scheduler.create_plan(owner)

        assert plan == []

    def test_no_tasks_returns_empty_plan(self, owner, pet, scheduler):
        """A pet with no tasks produces an empty plan."""
        owner.add_pet(pet)

        plan = scheduler.create_plan(owner)

        assert plan == []

    def test_completed_tasks_excluded(self, owner, pet, scheduler):
        """Tasks already marked completed must never appear in the plan."""
        pet.add_task(Task("Done Walk", 30, "", "walk", "high", status="completed"))
        owner.add_pet(pet)

        plan = scheduler.create_plan(owner)

        assert plan == []

    def test_tasks_that_exactly_fill_budget(self, scheduler):
        """When task durations sum exactly to time_available, all must be scheduled."""
        o = Owner("T", "U", 30, "t@t.com", time_available=35)
        p = Pet("Buddy", 3)
        p.add_task(Task("Walk", 30, "", "walk", "high"))
        p.add_task(Task("Feed",  5, "", "feed", "high"))
        o.add_pet(p)

        plan = scheduler.create_plan(o)

        assert len(plan) == 2
        assert sum(t.get_duration() for t in plan) == 35

    def test_oversized_task_skipped_but_smaller_later_task_included(self, scheduler):
        """Greedy must skip a task that doesn't fit rather than stopping entirely;
        a later smaller task must still be included if it fits."""
        o = Owner("T", "U", 30, "t@t.com", time_available=15)
        p = Pet("Buddy", 3)
        # High-priority 50-min task won't fit in 15-min budget
        p.add_task(Task("Big Walk",   50, "", "walk",       "high"))
        # Low-priority 10-min task will fit
        p.add_task(Task("Quick Feed", 10, "", "feed",       "low"))
        o.add_pet(p)

        plan = scheduler.create_plan(o)

        # Big Walk should be skipped; Quick Feed should be in the plan
        names = [t.get_name() for t in plan]
        assert "Quick Feed" in names
        assert "Big Walk" not in names


# ---------------------------------------------------------------------------
# 2. sort_by_time
# ---------------------------------------------------------------------------

class TestSortByTime:
    """
    sort_by_time sorts tasks by their start_time string (HH:MM).
    Tasks with no start_time appear last under the sentinel "99:99".
    """

    def test_out_of_order_times_sorted_correctly(self, scheduler):
        """Tasks added in reverse chronological order must come out sorted."""
        t1 = Task("Evening", 10, "", "walk", "low",    start_time="17:00")
        t2 = Task("Morning", 30, "", "walk", "high",   start_time="07:30")
        t3 = Task("Midday",  15, "", "feed", "medium", start_time="12:00")

        result = scheduler.sort_by_time([t1, t2, t3])

        assert [t.get_name() for t in result] == ["Morning", "Midday", "Evening"]

    def test_untimed_tasks_go_last(self, scheduler):
        """A task with no start_time must appear after all timed tasks."""
        timed   = Task("Walk",  30, "", "walk",       "high", start_time="08:00")
        untimed = Task("Meds",   5, "", "medication", "high")

        result = scheduler.sort_by_time([untimed, timed])

        assert result[0].get_name() == "Walk"
        assert result[1].get_name() == "Meds"

    def test_empty_list_returns_empty_list(self, scheduler):
        """Empty input must return empty output without raising."""
        assert scheduler.sort_by_time([]) == []

    def test_all_untimed_returns_all_tasks(self, scheduler):
        """When no task has a start_time all tasks are still returned."""
        t1 = Task("A", 10, "", "walk", "high")
        t2 = Task("B", 10, "", "feed", "high")

        result = scheduler.sort_by_time([t1, t2])

        assert len(result) == 2

    def test_same_start_time_both_included(self, scheduler):
        """Two tasks sharing a start_time must both appear in the output."""
        t1 = Task("First",  10, "", "walk", "high", start_time="09:00")
        t2 = Task("Second", 10, "", "feed", "high", start_time="09:00")

        result = scheduler.sort_by_time([t1, t2])

        assert len(result) == 2
        assert {t.get_name() for t in result} == {"First", "Second"}

    def test_original_list_not_mutated(self, scheduler):
        """sort_by_time must return a new list and leave the input unchanged."""
        t1 = Task("Z Task", 10, "", "walk", "high", start_time="23:00")
        t2 = Task("A Task", 10, "", "feed", "high", start_time="01:00")
        original = [t1, t2]

        scheduler.sort_by_time(original)

        assert original[0].get_name() == "Z Task"   # original order preserved


# ---------------------------------------------------------------------------
# 3. filter_tasks
# ---------------------------------------------------------------------------

class TestFilterTasks:
    """filter_tasks returns tasks matching the given pet_name and/or status filters."""

    def _setup_two_pet_owner(self, scheduler):
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        buddy = Pet("Buddy", 3)
        mochi = Pet("Mochi", 2)
        buddy.add_task(Task("Walk",  30, "", "walk",       "high"))
        mochi.add_task(Task("Meds",   5, "", "medication", "high"))
        owner.add_pet(buddy)
        owner.add_pet(mochi)
        return owner, buddy, mochi

    def test_filter_by_pet_name(self, scheduler):
        """Only tasks belonging to the named pet are returned."""
        owner, _, _ = self._setup_two_pet_owner(scheduler)

        result = scheduler.filter_tasks(owner, pet_name="Buddy")

        assert len(result) == 1
        assert result[0].get_name() == "Walk"

    def test_filter_by_status_pending(self, scheduler):
        """Only pending tasks are returned when status='pending'."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=60)
        p = Pet("Buddy", 3)
        p.add_task(Task("Done", 10, "", "walk", "high", status="completed"))
        p.add_task(Task("Todo", 10, "", "feed", "high"))
        owner.add_pet(p)

        result = scheduler.filter_tasks(owner, status="pending")

        assert len(result) == 1
        assert result[0].get_name() == "Todo"

    def test_filter_combined_pet_and_status(self, scheduler):
        """Intersection of pet_name and status filters."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        buddy = Pet("Buddy", 3)
        mochi = Pet("Mochi", 2)
        buddy.add_task(Task("Done Walk", 30, "", "walk", "high", status="completed"))
        buddy.add_task(Task("Feed",       5, "", "feed", "high"))
        mochi.add_task(Task("Meds",       5, "", "medication", "high"))
        owner.add_pet(buddy)
        owner.add_pet(mochi)

        result = scheduler.filter_tasks(owner, pet_name="Buddy", status="pending")

        assert len(result) == 1
        assert result[0].get_name() == "Feed"

    def test_filter_nonexistent_pet_returns_empty(self, scheduler):
        """Filtering by a pet name that doesn't exist returns an empty list."""
        owner, _, _ = self._setup_two_pet_owner(scheduler)

        result = scheduler.filter_tasks(owner, pet_name="Ghost")

        assert result == []

    def test_filter_no_args_returns_all_tasks(self, scheduler):
        """Calling filter_tasks with no filters returns every task."""
        owner, _, _ = self._setup_two_pet_owner(scheduler)

        result = scheduler.filter_tasks(owner)

        assert len(result) == 2


# ---------------------------------------------------------------------------
# 4. mark_task_complete + recurring automation
# ---------------------------------------------------------------------------

class TestMarkTaskComplete:
    """
    mark_task_complete marks a task done.  For recurring tasks it also
    clones the task onto the pet with status='pending' and a new due_date
    calculated via timedelta.
    """

    def test_recurring_daily_creates_new_task(self, scheduler):
        """Completing a daily recurring task adds a second task to the pet."""
        pet = Pet("Buddy", 3)
        task = Task("Meds", 5, "", "medication", "high",
                    is_recurring=True, recurrence_days=1)
        pet.add_task(task)

        scheduler.mark_task_complete(task, pet)

        assert len(pet.get_tasks()) == 2

    def test_original_task_marked_completed(self, scheduler):
        """The original task's status becomes 'completed'."""
        pet = Pet("Buddy", 3)
        task = Task("Meds", 5, "", "medication", "high",
                    is_recurring=True, recurrence_days=1)
        pet.add_task(task)

        scheduler.mark_task_complete(task, pet)

        assert task.get_status() == "completed"

    def test_new_task_is_pending(self, scheduler):
        """The auto-created next occurrence starts as pending."""
        pet = Pet("Buddy", 3)
        task = Task("Meds", 5, "", "medication", "high",
                    is_recurring=True, recurrence_days=1)
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)

        assert next_task.get_status() == "pending"

    def test_due_date_incremented_by_one_day(self, scheduler):
        """Daily recurring task: next due = today + 1 day."""
        pet = Pet("Buddy", 3)
        task = Task("Meds", 5, "", "medication", "high",
                    is_recurring=True, recurrence_days=1)
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)
        expected  = (date.today() + timedelta(days=1)).isoformat()

        assert next_task.get_due_date() == expected

    def test_due_date_incremented_by_seven_days(self, scheduler):
        """Weekly recurring task: next due = today + 7 days."""
        pet = Pet("Buddy", 3)
        task = Task("Grooming", 30, "", "grooming", "medium",
                    is_recurring=True, recurrence_days=7)
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)
        expected  = (date.today() + timedelta(days=7)).isoformat()

        assert next_task.get_due_date() == expected

    def test_chains_from_existing_due_date_not_today(self, scheduler):
        """If a task already has a due_date, the next occurrence is due_date + N,
        not today + N.  This ensures the chain doesn't drift."""
        pet  = Pet("Buddy", 3)
        base = date(2026, 3, 15)
        task = Task("Meds", 5, "", "medication", "high",
                    is_recurring=True, recurrence_days=1,
                    due_date=base.isoformat())
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)

        assert next_task.get_due_date() == "2026-03-16"

    def test_non_recurring_returns_none(self, scheduler):
        """Completing a one-off task returns None (no clone created)."""
        pet  = Pet("Buddy", 3)
        task = Task("One-off Walk", 30, "", "walk", "high")
        pet.add_task(task)

        result = scheduler.mark_task_complete(task, pet)

        assert result is None

    def test_non_recurring_does_not_add_task(self, scheduler):
        """Completing a one-off task must not increase the pet's task count."""
        pet  = Pet("Buddy", 3)
        task = Task("One-off Walk", 30, "", "walk", "high")
        pet.add_task(task)

        scheduler.mark_task_complete(task, pet)

        assert len(pet.get_tasks()) == 1

    def test_cloned_task_is_a_new_instance(self, scheduler):
        """The returned next occurrence must be a distinct object, not the same task."""
        pet  = Pet("Buddy", 3)
        task = Task("Meds", 5, "", "medication", "high",
                    is_recurring=True, recurrence_days=1)
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)

        assert next_task is not task

    def test_cloned_task_inherits_correct_fields(self, scheduler):
        """The clone must copy name, duration, start_time, and task_type."""
        pet  = Pet("Buddy", 3)
        task = Task("Meds", 10, "Thyroid pill", "medication", "high",
                    start_time="09:00", is_recurring=True, recurrence_days=1)
        pet.add_task(task)

        next_task = scheduler.mark_task_complete(task, pet)

        assert next_task.get_name()       == "Meds"
        assert next_task.get_duration()   == 10
        assert next_task.get_start_time() == "09:00"
        assert next_task.get_task_type()  == "medication"


# ---------------------------------------------------------------------------
# 5. detect_conflicts
# ---------------------------------------------------------------------------

class TestDetectConflicts:
    """
    detect_conflicts runs three independent checks:
      1. Budget overrun  — pending tasks not included in the plan
      2. Duplicate types — same task_type on the same pet more than once
      3. Time overlaps   — pending timed tasks whose windows intersect
    """

    def test_no_conflicts_returns_empty_list(self, scheduler):
        """A clean setup with no problems must return an empty list."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=60)
        pet   = Pet("Buddy", 3)
        pet.add_task(Task("Walk", 30, "", "walk", "high", start_time="07:00"))
        owner.add_pet(pet)
        scheduler.create_plan(owner)

        assert scheduler.detect_conflicts(owner) == []

    def test_skipped_task_flagged(self, scheduler):
        """A task that doesn't fit the budget must appear in the warnings."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=10)
        pet   = Pet("Buddy", 3)
        pet.add_task(Task("Long Walk", 30, "", "walk", "high"))
        owner.add_pet(pet)
        scheduler.create_plan(owner)

        warnings = scheduler.detect_conflicts(owner)

        assert any("Long Walk" in w for w in warnings)

    def test_duplicate_task_type_flagged(self, scheduler):
        """Two tasks of the same type on the same pet must produce a warning."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        pet   = Pet("Buddy", 3)
        pet.add_task(Task("Morning Walk",   30, "", "walk", "high"))
        pet.add_task(Task("Afternoon Walk", 20, "", "walk", "medium"))
        owner.add_pet(pet)
        scheduler.create_plan(owner)

        warnings = scheduler.detect_conflicts(owner)

        assert any("walk" in w for w in warnings)

    def test_time_overlap_detected(self, scheduler):
        """Two tasks on different pets whose time windows intersect must be flagged."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        buddy = Pet("Buddy", 3)
        mochi = Pet("Mochi", 2)
        # Buddy 09:00–10:00, Mochi 09:30–10:15 — overlap 09:30–10:00
        buddy.add_task(Task("Vet",     60, "", "appointment", "high",   start_time="09:00"))
        mochi.add_task(Task("Groomer", 45, "", "grooming",    "medium", start_time="09:30"))
        owner.add_pet(buddy)
        owner.add_pet(mochi)
        scheduler.create_plan(owner)

        warnings = scheduler.detect_conflicts(owner)

        assert any("Time conflict" in w for w in warnings)

    def test_adjacent_tasks_do_not_conflict(self, scheduler):
        """Tasks that share an endpoint but do not overlap must NOT be flagged.
        e.g. 09:00+30 min ends exactly at 09:30 when the next task begins."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        pet   = Pet("Buddy", 3)
        pet.add_task(Task("Walk", 30, "", "walk", "high", start_time="09:00"))
        pet.add_task(Task("Feed", 10, "", "feed", "high", start_time="09:30"))
        owner.add_pet(pet)
        scheduler.create_plan(owner)

        warnings = scheduler.detect_conflicts(owner)
        time_warnings = [w for w in warnings if "Time conflict" in w]

        assert time_warnings == []

    def test_completed_task_overlap_not_flagged(self, scheduler):
        """A completed task overlapping a pending task's window must NOT produce
        a time-conflict warning (completed tasks are already done)."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        pet   = Pet("Buddy", 3)
        pet.add_task(Task("Done",    30, "", "walk", "high",
                          start_time="09:00", status="completed"))
        pet.add_task(Task("Pending", 10, "", "feed", "high", start_time="09:15"))
        owner.add_pet(pet)
        scheduler.create_plan(owner)

        warnings = scheduler.detect_conflicts(owner)
        time_warnings = [w for w in warnings if "Time conflict" in w]

        assert time_warnings == []

    def test_tasks_without_start_time_no_false_overlap(self, scheduler):
        """Tasks with no start_time must never generate a time-conflict warning."""
        owner = Owner("T", "U", 30, "t@t.com", time_available=120)
        pet   = Pet("Buddy", 3)
        pet.add_task(Task("Walk",  30, "", "walk", "high"))   # no start_time
        pet.add_task(Task("Meds",   5, "", "medication", "high"))  # no start_time
        owner.add_pet(pet)
        scheduler.create_plan(owner)

        warnings = scheduler.detect_conflicts(owner)
        time_warnings = [w for w in warnings if "Time conflict" in w]

        assert time_warnings == []

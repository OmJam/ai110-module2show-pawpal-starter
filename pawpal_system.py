from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

# Scheduler sorts tasks by this ranking: lower number = scheduled first
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _time_to_minutes(hhmm: str) -> int:
    """Convert a HH:MM string to total minutes since midnight.

    Args:
        hhmm: Time string in "HH:MM" 24-hour format, e.g. "08:30".

    Returns:
        Integer minutes since midnight (0–1439), or -1 if the string is
        empty, missing a colon, or contains non-numeric parts. Returning
        -1 lets callers skip invalid times without raising an exception.
    """
    if not hhmm or ":" not in hhmm:
        return -1
    try:
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)
    except ValueError:
        return -1


def _tasks_overlap(start1: int, dur1: int, start2: int, dur2: int) -> bool:
    """Return True if two time windows overlap (lightweight interval check).

    Uses the standard interval-overlap test: two half-open intervals
    [s1, s1+d1) and [s2, s2+d2) overlap when neither ends before the
    other begins — i.e. s1 < s2+d2 AND s2 < s1+d1.

    Args:
        start1: Start of window A in minutes since midnight.
        dur1:   Duration of window A in minutes.
        start2: Start of window B in minutes since midnight.
        dur2:   Duration of window B in minutes.

    Returns:
        True if the two windows share at least one minute; False otherwise.
    """
    return start1 < start2 + dur2 and start2 < start1 + dur1


# ---------------------------------------------------------------------------
# Task — represents a single pet care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    duration: int          # minutes
    description: str
    task_type: str         # walk | feed | medication | grooming | appointment | other
    priority: str          # low | medium | high
    status: str = "pending"       # pending | completed
    start_time: str = ""          # HH:MM format, e.g. "08:30"
    is_recurring: bool = False    # True if this task repeats on a schedule
    recurrence_days: int = 1      # repeat every N days (1 = daily, 7 = weekly)
    due_date: str = ""            # ISO date string YYYY-MM-DD, e.g. "2026-03-16"

    def set_name(self, name: str) -> None:
        """Set the task name."""
        self.name = name

    def get_name(self) -> str:
        """Return the task name."""
        return self.name

    def set_duration(self, duration: int) -> None:
        """Set the task duration in minutes."""
        self.duration = duration

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration

    def set_description(self, description: str) -> None:
        """Set the task description."""
        self.description = description

    def get_description(self) -> str:
        """Return the task description."""
        return self.description

    def set_task_type(self, task_type: str) -> None:
        """Set the task type (walk, feed, medication, grooming, appointment, or other)."""
        self.task_type = task_type

    def get_task_type(self) -> str:
        """Return the task type."""
        return self.task_type

    def set_priority(self, priority: str) -> None:
        """Set the task priority (low, medium, or high)."""
        self.priority = priority

    def get_priority(self) -> str:
        """Return the task priority."""
        return self.priority

    def set_status(self, status: str) -> None:
        """Set the task status (pending or completed)."""
        self.status = status

    def get_status(self) -> str:
        """Return the task status."""
        return self.status

    def set_start_time(self, start_time: str) -> None:
        """Set the start time in HH:MM format."""
        self.start_time = start_time

    def get_start_time(self) -> str:
        """Return the start time string in HH:MM format."""
        return self.start_time

    def set_is_recurring(self, is_recurring: bool) -> None:
        """Set whether this task repeats on a schedule."""
        self.is_recurring = is_recurring

    def get_is_recurring(self) -> bool:
        """Return True if this task is recurring."""
        return self.is_recurring

    def set_recurrence_days(self, recurrence_days: int) -> None:
        """Set how many days between each recurrence."""
        self.recurrence_days = recurrence_days

    def get_recurrence_days(self) -> int:
        """Return the recurrence interval in days."""
        return self.recurrence_days

    def set_due_date(self, due_date: str) -> None:
        """Set the due date as an ISO string (YYYY-MM-DD)."""
        self.due_date = due_date

    def get_due_date(self) -> str:
        """Return the due date ISO string, or empty string if not set."""
        return self.due_date

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"


# ---------------------------------------------------------------------------
# Pet — stores pet profile and owns a list of care tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    age: int               # years
    breed: str = ""
    # medications: list of {"name": str, "frequency": str, "unit": str}
    medications: List[dict] = field(default_factory=list)
    # grooming:    list of {"name": str, "frequency": str, "unit": str}
    grooming: List[dict] = field(default_factory=list)
    habits: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        """Set the pet's name."""
        self.name = name

    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name

    def set_age(self, age: int) -> None:
        """Set the pet's age in years."""
        self.age = age

    def get_age(self) -> int:
        """Return the pet's age in years."""
        return self.age

    def set_breed(self, breed: str) -> None:
        """Set the pet's breed."""
        self.breed = breed

    def get_breed(self) -> str:
        """Return the pet's breed."""
        return self.breed

    def set_medications(self, medications: List[dict]) -> None:
        """Replace the full medications list."""
        self.medications = medications

    def get_medications(self) -> List[dict]:
        """Return the list of medication dicts."""
        return self.medications

    def set_grooming(self, grooming: List[dict]) -> None:
        """Replace the full grooming list."""
        self.grooming = grooming

    def get_grooming(self) -> List[dict]:
        """Return the list of grooming dicts."""
        return self.grooming

    def set_habits(self, habits: List[str]) -> None:
        """Replace the habits list."""
        self.habits = habits

    def get_habits(self) -> List[str]:
        """Return the list of habit strings."""
        return self.habits

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


# ---------------------------------------------------------------------------
# Owner — manages one or more pets and provides access to all their tasks
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        age: int,
        email: str,
        middle_name: str = "",
        gender: str = "",
        time_available: int = 0,  # total minutes available today
    ):
        """Initialise an Owner with profile info, an empty pet list, and no schedule."""
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.email = email
        self.time_available = time_available
        self._pets: List[Pet] = []
        self._schedule: Optional["Scheduler"] = None

    def add_pet(self, pet: Pet) -> None:
        """Append a single pet to this owner's pet list."""
        self._pets.append(pet)

    def set_pets(self, pets: List[Pet]) -> None:
        """Replace the entire pet list."""
        self._pets = pets

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self._pets

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks: List[Task] = []
        for pet in self._pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def set_schedule(self, schedule: "Scheduler") -> None:
        """Assign a Scheduler instance to this owner."""
        self._schedule = schedule

    def get_schedule(self) -> Optional["Scheduler"]:
        """Return this owner's assigned Scheduler, or None."""
        return self._schedule


# ---------------------------------------------------------------------------
# Scheduler — the "brain": retrieves, organises, and prioritises tasks
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, time_zone: str = "UTC"):
        """Initialise the Scheduler with a time zone, empty task list, and no plan."""
        self.time_zone = time_zone
        self._tasks: List[Task] = []   # tasks added directly to this scheduler
        self.plan: List[Task] = []     # the generated daily plan
        self.explanation: str = ""

    def set_time_zone(self, tz: str) -> None:
        """Set the scheduler's time zone string."""
        self.time_zone = tz

    def get_time_zone(self) -> str:
        """Return the current time zone string."""
        return self.time_zone

    def set_tasks(self, tasks: List[Task]) -> None:
        """Replace all directly-managed tasks with the given list."""
        self._tasks = tasks

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks managed directly by this scheduler."""
        return self._tasks

    def add_task(self, task: Task) -> None:
        """Append a task to the scheduler's direct task list."""
        self._tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the scheduler's direct task list."""
        self._tasks.remove(task)

    def set_plan(self, plan: List[Task]) -> None:
        """Manually assign a pre-built task list as the current plan."""
        self.plan = plan

    def get_plan(self) -> List[Task]:
        """Return the current scheduled plan."""
        return self.plan

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of tasks sorted chronologically by start_time.

        HH:MM strings sort correctly as plain strings because the format is
        zero-padded and left-to-right significant — "08:00" < "14:30"
        lexicographically the same way they are chronologically.  Tasks with
        no start_time receive the sentinel value "99:99" so they always
        appear at the end of the sorted list.

        Args:
            tasks: Any list of Task objects; the original list is not mutated.

        Returns:
            A new list with the same tasks ordered earliest start_time first.
            Tasks sharing the same start_time keep their relative order.
        """
        return sorted(
            tasks,
            key=lambda t: t.get_start_time() if t.get_start_time() else "99:99"
        )

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: str = None,
        status: str = None,
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Both filters are optional and can be combined. Omitting a filter
        means "match everything" for that dimension.

        Args:
            owner:    The Owner whose pets' tasks are searched.
            pet_name: If provided, only tasks belonging to the pet with this
                      name are included. Case-sensitive.
            status:   If provided, only tasks whose status equals this string
                      are included (e.g. "pending" or "completed").

        Returns:
            A list of matching Task objects in the order they appear on each
            pet (pets are visited in the order they were added to the owner).
        """
        result: List[Task] = []
        for pet in owner.get_pets():
            if pet_name and pet.get_name() != pet_name:
                continue                          # skip pets that don't match
            for task in pet.get_tasks():
                if status and task.get_status() != status:
                    continue                      # skip tasks with wrong status
                result.append(task)
        return result

    def reset_recurring_tasks(self, owner: Owner) -> None:
        """Reset all completed recurring tasks to pending so they reappear the next day.

        Intended to be called once at the start of a new day (or when the
        user clicks a "New Day" button in the UI). Only tasks where both
        `is_recurring` is True and `status` is "completed" are affected;
        one-off completed tasks are left unchanged.

        Args:
            owner: The Owner whose pets' tasks will be scanned and reset.

        Returns:
            None. Tasks are mutated in place.
        """
        for task in owner.get_all_tasks():
            if task.get_is_recurring() and task.get_status() == "completed":
                task.set_status("pending")

    def detect_conflicts(self, owner: Owner) -> List[str]:
        """Scan for scheduling problems and return human-readable warning strings.

        Runs three independent checks in order:
          1. Budget overrun — pending tasks that did not fit in the plan.
          2. Duplicate types — a pet has more than one task of the same type.
          3. Time overlaps — any two pending timed tasks whose windows intersect,
             across all pets (catches cases where the owner cannot be in two
             places at once).

        The method never raises an exception; all problems are reported as
        plain strings so the caller can display them however it likes.

        Args:
            owner: The Owner whose pets and tasks are inspected.

        Returns:
            A list of warning strings (may be empty if no problems are found).
            Each string is self-contained and human-readable.
        """
        warnings: List[str] = []
        scheduled_names = {t.get_name() for t in self.plan}

        # 1. Warn about every pending task that didn't make it into the plan
        for task in owner.get_all_tasks():
            if task.get_status() == "pending" and task.get_name() not in scheduled_names:
                warnings.append(
                    f"'{task.get_name()}' ({task.get_priority()} priority, "
                    f"{task.get_duration()} min) was skipped — not enough time."
                )

        # 2. Warn when a pet has more than one task of the same type
        for pet in owner.get_pets():
            type_counts: dict = {}
            for task in pet.get_tasks():
                key = task.get_task_type()
                type_counts[key] = type_counts.get(key, 0) + 1
            for task_type, count in type_counts.items():
                if count > 1:
                    warnings.append(
                        f"{pet.get_name()} has {count} '{task_type}' tasks "
                        f"— possible duplicate."
                    )

        # 3. Time overlap detection across all pets
        #    Only pending tasks matter — completed ones are already done.
        #    Build a flat list of (start_minutes, duration, task_name, pet_name)
        #    for every pending task that has a start_time set, then check all pairs.
        timed: List[tuple] = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                if task.get_status() != "pending":
                    continue                            # skip completed tasks
                mins = _time_to_minutes(task.get_start_time())
                if mins >= 0:                           # skip tasks with no start time
                    timed.append((mins, task.get_duration(), task.get_name(), pet.get_name()))

        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                s1, d1, n1, p1 = timed[i]
                s2, d2, n2, p2 = timed[j]
                if _tasks_overlap(s1, d1, s2, d2):
                    warnings.append(
                        f"Time conflict: '{n1}' ({p1}, "
                        f"{s1 // 60:02d}:{s1 % 60:02d}, {d1} min) overlaps "
                        f"'{n2}' ({p2}, {s2 // 60:02d}:{s2 % 60:02d}, {d2} min)."
                    )

        return warnings

    def mark_task_complete(self, task: Task, pet: Pet) -> Optional[Task]:
        """Mark a task complete and, if recurring, auto-create the next occurrence on the pet.

        Uses timedelta to calculate the next due date:
          next_due = base_date + timedelta(days=task.recurrence_days)

        The base date is the task's existing due_date if set, otherwise today.
        Returns the newly created Task for recurring tasks, or None for one-off tasks.
        """
        task.mark_complete()

        if not task.get_is_recurring():
            return None

        # Calculate next due date with timedelta
        if task.get_due_date():
            base_date = date.fromisoformat(task.get_due_date())
        else:
            base_date = date.today()

        next_due = base_date + timedelta(days=task.get_recurrence_days())

        # Clone the task with a fresh pending status and the new due date
        next_task = Task(
            name=task.get_name(),
            duration=task.get_duration(),
            description=task.get_description(),
            task_type=task.get_task_type(),
            priority=task.get_priority(),
            status="pending",
            start_time=task.get_start_time(),
            is_recurring=True,
            recurrence_days=task.get_recurrence_days(),
            due_date=next_due.isoformat(),
        )
        pet.add_task(next_task)
        return next_task

    def create_plan(self, owner: Owner) -> List[Task]:
        """Sort pending tasks by priority then duration (shortest first), fit within owner.time_available."""
        # 1. Gather all candidate tasks
        all_tasks: List[Task] = list(self._tasks)
        for p in owner.get_pets():
            all_tasks.extend(p.get_tasks())

        # 2. Keep only pending tasks
        pending = [t for t in all_tasks if t.get_status() == "pending"]

        # 3. Sort: primary key = priority, secondary key = duration (Shortest-Job-First
        #    within the same priority tier to maximise the number of tasks that fit)
        sorted_tasks = sorted(
            pending,
            key=lambda t: (PRIORITY_ORDER.get(t.get_priority(), 99), t.get_duration())
        )

        # 4. Greedy time-fitting
        scheduled: List[Task] = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.get_duration() <= owner.time_available:
                scheduled.append(task)
                time_used += task.get_duration()

        self.plan = scheduled
        return self.plan

    def set_explanation(self, explanation: str) -> None:
        """Store a custom explanation string for the current plan."""
        self.explanation = explanation

    def get_explanation(self) -> str:
        """Return the stored plan explanation."""
        return self.explanation

    def create_explanation(self) -> str:
        """Build and store a human-readable summary of the current plan."""
        if not self.plan:
            self.explanation = (
                "No tasks were scheduled. Either there are no pending tasks "
                "or the available time is too short for any task."
            )
            return self.explanation

        total_time = sum(t.get_duration() for t in self.plan)
        lines = [
            f"Scheduled {len(self.plan)} task(s) using {total_time} minute(s).",
            "Tasks are ordered by priority, then shortest duration first:",
        ]
        for i, task in enumerate(self.plan, start=1):
            time_label = f" @ {task.get_start_time()}" if task.get_start_time() else ""
            recurring   = " (recurring)" if task.get_is_recurring() else ""
            lines.append(
                f"  {i}. [{task.get_priority().upper()}] {task.get_name()}"
                f"{time_label} — {task.get_duration()} min"
                f"  |  {task.get_task_type()}{recurring}"
            )
            if task.get_description():
                lines.append(f"       {task.get_description()}")

        self.explanation = "\n".join(lines)
        return self.explanation

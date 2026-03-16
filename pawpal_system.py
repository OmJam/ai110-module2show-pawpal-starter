from dataclasses import dataclass, field
from typing import List, Optional

# Scheduler sorts tasks by this ranking: lower number = scheduled first
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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
    status: str = "pending"  # pending | completed

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

    def create_plan(self, owner: Owner) -> List[Task]:
        """Sort pending tasks by priority and greedily fit them within owner.time_available."""
        # 1. Gather all candidate tasks
        all_tasks: List[Task] = list(self._tasks)
        for p in owner.get_pets():
            all_tasks.extend(p.get_tasks())

        # 2. Keep only pending tasks
        pending = [t for t in all_tasks if t.get_status() == "pending"]

        # 3. Sort by priority (unknown priorities go last)
        sorted_tasks = sorted(
            pending,
            key=lambda t: PRIORITY_ORDER.get(t.get_priority(), 99)
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
            "Tasks are ordered from highest to lowest priority:",
        ]
        for i, task in enumerate(self.plan, start=1):
            lines.append(
                f"  {i}. [{task.get_priority().upper()}] {task.get_name()} "
                f"— {task.get_duration()} min  |  type: {task.get_task_type()}"
            )
            if task.get_description():
                lines.append(f"       {task.get_description()}")

        self.explanation = "\n".join(lines)
        return self.explanation

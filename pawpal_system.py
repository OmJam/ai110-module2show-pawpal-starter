from dataclasses import dataclass, field
from typing import List, Optional


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
        pass

    def get_name(self) -> str:
        pass

    def set_duration(self, duration: int) -> None:
        pass

    def get_duration(self) -> int:
        pass

    def set_description(self, description: str) -> None:
        pass

    def get_description(self) -> str:
        pass

    def set_task_type(self, task_type: str) -> None:
        pass

    def get_task_type(self) -> str:
        pass

    def set_priority(self, priority: str) -> None:
        pass

    def get_priority(self) -> str:
        pass

    def set_status(self, status: str) -> None:
        pass

    def get_status(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Pet — stores pet profile and care requirements
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    age: int               # years
    breed: str = ""
    # medications: list of {"name": str, "frequency": str, "unit": str}
    medications: List[dict] = field(default_factory=list)
    # grooming: list of {"name": str, "frequency": str, "unit": str}
    grooming: List[dict] = field(default_factory=list)
    habits: List[str] = field(default_factory=list)

    def set_name(self, name: str) -> None:
        pass

    def get_name(self) -> str:
        pass

    def set_age(self, age: int) -> None:
        pass

    def get_age(self) -> int:
        pass

    def set_breed(self, breed: str) -> None:
        pass

    def get_breed(self) -> str:
        pass

    def set_medications(self, medications: List[dict]) -> None:
        pass

    def get_medications(self) -> List[dict]:
        pass

    def set_grooming(self, grooming: List[dict]) -> None:
        pass

    def get_grooming(self) -> List[dict]:
        pass

    def set_habits(self, habits: List[str]) -> None:
        pass

    def get_habits(self) -> List[str]:
        pass


# ---------------------------------------------------------------------------
# Owner — stores owner profile, their pets, and their assigned schedule
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
        pass

    def set_pets(self, pets: List[Pet]) -> None:
        pass

    def get_pets(self) -> List[Pet]:
        pass

    def set_schedule(self, schedule: "Scheduler") -> None:
        pass

    def get_schedule(self) -> Optional["Scheduler"]:
        pass


# ---------------------------------------------------------------------------
# Scheduler — generates and stores the daily plan for a given owner + pet
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, time_zone: str = "UTC"):
        self.time_zone = time_zone
        self._tasks: List[Task] = []
        self.plan: List[Task] = []
        self.explanation: str = ""

    def set_time_zone(self, tz: str) -> None:
        pass

    def get_time_zone(self) -> str:
        pass

    def set_tasks(self, tasks: List[Task]) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def set_plan(self, plan: List[Task]) -> None:
        pass

    def get_plan(self) -> List[Task]:
        pass

    def create_plan(self, owner: Owner, pet: Pet) -> List[Task]:
        pass

    def set_explanation(self, explanation: str) -> None:
        pass

    def get_explanation(self) -> str:
        pass

    def create_explanation(self) -> str:
        pass

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care task."""
    title: str
    time: str              # Format: "HH:MM"
    duration_minutes: int
    priority: str          # "low", "medium", or "high"
    frequency: str         # "once", "daily", or "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self):
        """Return a new Task scheduled for the next occurrence."""
        if self.frequency == "daily":
            new_date = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            new_date = self.due_date + timedelta(weeks=1)
        else:
            return None  # "once" tasks don't repeat

        return Task(
            title=self.title,
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=new_date
        )


@dataclass
class Pet:
    """Represents a pet with a list of tasks."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's list."""
        self.tasks.append(task)

    def get_tasks(self):
        """Return all tasks for this pet."""
        return self.tasks


class Owner:
    """Represents the pet owner who manages multiple pets."""

    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self):
        """Return every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet.name, task))
        return all_tasks


class Scheduler:
    """The brain — organizes, sorts, filters, and checks tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_sorted_tasks(self):
        """Return all tasks sorted by time (earliest first)."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda x: x[1].time)

    def filter_by_status(self, completed: bool):
        """Return tasks filtered by completion status."""
        return [(name, task) for name, task in self.owner.get_all_tasks()
                if task.completed == completed]

    def filter_by_pet(self, pet_name: str):
        """Return tasks for a specific pet."""
        return [(name, task) for name, task in self.owner.get_all_tasks()
                if name.lower() == pet_name.lower()]

    def detect_conflicts(self):
        """Return a list of warning messages for tasks at the same time."""
        all_tasks = self.owner.get_all_tasks()
        time_map = {}
        warnings = []

        for pet_name, task in all_tasks:
            if task.time in time_map:
                warnings.append(
                    f"⚠️ Conflict: '{task.title}' and "
                    f"'{time_map[task.time][1].title}' are both at {task.time}"
                )
            else:
                time_map[task.time] = (pet_name, task)

        return warnings

    def mark_task_complete(self, pet_name: str, task_title: str):
        """Mark a task done and auto-schedule the next one if recurring."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                for task in pet.tasks:
                    if task.title.lower() == task_title.lower():
                        task.mark_complete()
                        next_task = task.next_occurrence()
                        if next_task:
                            pet.add_task(next_task)
                        return
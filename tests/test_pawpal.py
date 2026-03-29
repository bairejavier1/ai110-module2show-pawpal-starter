"""
tests/test_pawpal.py
====================
Automated test suite for PawPal+ (pawpal_system.py).

Run with:
    python -m pytest tests/ -v

Coverage summary (17 tests total):
    Batch 1 — Core behavior (8 tests)
        1.  Task completion status change
        2.  Adding a task increases pet's task count
        3.  Scheduler sorts tasks chronologically
        4.  Daily task recurrence after mark_complete
        5.  Conflict detected when two tasks share a time
        6.  No false conflict when all times are unique
        7.  Filter by pet name returns correct tasks
        8.  Filter by status returns only incomplete tasks

    Batch 2 — Edge cases (9 tests)
        9.  Pet with zero tasks returns empty list
        10. Scheduler handles a pet with no tasks
        11. Owner with no pets returns empty task list
        12. Scheduler handles an owner with zero pets
        13. Weekly task correctly rolls over a month boundary
        14. "once" task returns None from next_occurrence()
        15. Marking a "once" task complete adds no new task
        16. Marking a nonexistent task does not crash
        17. filter_by_pet() is case-insensitive
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ═════════════════════════════════════════════════════════════════════════════
# SHARED HELPER
# Creates a reusable Owner with two pets and four tasks for tests that need
# a populated system without caring about the specific setup details.
# ═════════════════════════════════════════════════════════════════════════════

def make_owner_with_pets():
    """Return an Owner containing Mochi (cat) and Rex (dog), each with 2 tasks."""
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "cat")
    mochi.add_task(Task("Evening feeding", "17:00", 10, "high",   "daily"))
    mochi.add_task(Task("Playtime",        "09:00", 20, "medium", "daily"))

    rex = Pet("Rex", "dog")
    rex.add_task(Task("Morning walk",   "07:00", 30, "high",   "daily"))
    rex.add_task(Task("Afternoon walk", "14:00", 30, "medium", "daily"))

    owner.add_pet(mochi)
    owner.add_pet(rex)
    return owner


# ═════════════════════════════════════════════════════════════════════════════
# BATCH 1 — CORE BEHAVIOR TESTS (tests 1–8)
# These verify the fundamental features every pet scheduler must have.
# ═════════════════════════════════════════════════════════════════════════════

# ── Test 1 ────────────────────────────────────────────────────────────────────
def test_mark_complete_changes_status():
    """
    mark_complete() must flip a task's completed flag from False to True.
    This is the most basic behavior — if this breaks, nothing else works.
    """
    task = Task("Bath time", "10:00", 15, "low", "once")

    # Newly created tasks should always start incomplete
    assert task.completed is False

    task.mark_complete()

    # After calling mark_complete(), the flag must be True
    assert task.completed is True


# ── Test 2 ────────────────────────────────────────────────────────────────────
def test_add_task_increases_count():
    """
    Calling add_task() on a Pet should increase its task list length by 1.
    Verifies that tasks are actually stored, not silently discarded.
    """
    pet = Pet("Mochi", "cat")

    # A brand-new pet should have zero tasks
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", "08:00", 10, "high", "daily"))

    # After adding one task the count must be exactly 1
    assert len(pet.tasks) == 1


# ── Test 3 ────────────────────────────────────────────────────────────────────
def test_tasks_sorted_by_time():
    """
    get_sorted_tasks() must return tasks in chronological (HH:MM) order
    regardless of the order they were added.
    """
    owner = make_owner_with_pets()
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.get_sorted_tasks()
    times = [task.time for _, task in sorted_tasks]

    # The list of times must equal itself when sorted — i.e. already sorted
    assert times == sorted(times), "Tasks are not in chronological order"


# ── Test 4 ────────────────────────────────────────────────────────────────────
def test_daily_task_recurrence():
    """
    Marking a daily task complete should automatically add a new task
    scheduled for the following day (today + 1).
    The original task stays in the list as completed; the new one is appended.
    """
    owner = Owner("Jordan")
    rex = Pet("Rex", "dog")
    rex.add_task(Task("Morning walk", "07:00", 30, "high", "daily"))
    owner.add_pet(rex)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Rex", "Morning walk")

    # Rex should now have 2 tasks: the completed original + tomorrow's copy
    assert len(rex.tasks) == 2

    tomorrow = date.today() + timedelta(days=1)
    new_task = rex.tasks[1]

    # The new task must be scheduled for tomorrow and start incomplete
    assert new_task.due_date == tomorrow
    assert new_task.completed is False


# ── Test 5 ────────────────────────────────────────────────────────────────────
def test_conflict_detection():
    """
    detect_conflicts() must return exactly one warning when two tasks
    are scheduled at the same time (09:00 in this case).
    The warning string must mention the conflicting time.
    """
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat")
    mochi.add_task(Task("Playtime",        "09:00", 20, "medium", "daily"))
    mochi.add_task(Task("Vet appointment", "09:00", 60, "high",   "once"))
    owner.add_pet(mochi)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "09:00" in warnings[0]


# ── Test 6 ────────────────────────────────────────────────────────────────────
def test_no_false_conflict():
    """
    detect_conflicts() must return zero warnings when all tasks have
    distinct times. Guards against false positives.
    """
    owner = make_owner_with_pets()  # tasks at 07:00, 09:00, 14:00, 17:00
    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 0


# ── Test 7 ────────────────────────────────────────────────────────────────────
def test_filter_by_pet():
    """
    filter_by_pet("Rex") must return only Rex's tasks — not Mochi's.
    Also checks that the correct number of tasks is returned.
    """
    owner = make_owner_with_pets()
    scheduler = Scheduler(owner)

    rex_tasks = scheduler.filter_by_pet("Rex")

    # Every returned tuple must have "Rex" as the pet name
    assert all(name == "Rex" for name, _ in rex_tasks)
    # Rex has exactly 2 tasks in our helper fixture
    assert len(rex_tasks) == 2


# ── Test 8 ────────────────────────────────────────────────────────────────────
def test_filter_by_status_incomplete():
    """
    filter_by_status(False) must return only tasks where completed == False.
    Since no tasks have been marked done yet, all 4 tasks should appear.
    """
    owner = make_owner_with_pets()
    scheduler = Scheduler(owner)

    incomplete = scheduler.filter_by_status(False)

    # Every returned task must actually be incomplete
    assert all(not task.completed for _, task in incomplete)


# ═════════════════════════════════════════════════════════════════════════════
# BATCH 2 — EDGE CASE TESTS (tests 9–17)
# These verify the system handles empty/unusual inputs without crashing
# and that boundary conditions (month rollover, "once" tasks, etc.) work.
# ═════════════════════════════════════════════════════════════════════════════

# ── Test 9 ────────────────────────────────────────────────────────────────────
def test_pet_with_no_tasks():
    """
    A freshly created Pet with no tasks added should return an empty list,
    not raise an error or return None.
    """
    pet = Pet("Ghost", "cat")
    assert pet.get_tasks() == []


# ── Test 10 ───────────────────────────────────────────────────────────────────
def test_scheduler_with_empty_pet():
    """
    A Scheduler whose Owner has one pet with zero tasks should return
    empty lists from all query methods — no crash, no unexpected output.
    """
    owner = Owner("Jordan")
    owner.add_pet(Pet("Ghost", "cat"))
    scheduler = Scheduler(owner)

    assert scheduler.get_sorted_tasks() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.filter_by_pet("Ghost") == []
    assert scheduler.filter_by_status(False) == []


# ── Test 11 ───────────────────────────────────────────────────────────────────
def test_owner_with_no_pets():
    """
    An Owner with no pets added should return an empty task list from
    get_all_tasks() — not crash or return None.
    """
    owner = Owner("Jordan")
    assert owner.get_all_tasks() == []


# ── Test 12 ───────────────────────────────────────────────────────────────────
def test_scheduler_with_no_pets():
    """
    A Scheduler whose Owner has zero pets should gracefully return empty
    results from every method rather than raising an exception.
    """
    owner = Owner("Jordan")
    scheduler = Scheduler(owner)

    assert scheduler.get_sorted_tasks() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.filter_by_pet("Rex") == []
    assert scheduler.filter_by_status(False) == []


# ── Test 13 ───────────────────────────────────────────────────────────────────
def test_weekly_task_crosses_month_boundary():
    """
    A weekly task due on March 28 should reschedule to April 4
    (28 + 7 days), correctly crossing the month boundary.
    Python's timedelta handles this automatically, but we verify it here.
    """
    end_of_month = date(2026, 3, 28)
    task = Task(
        title            = "Weekly grooming",
        time             = "10:00",
        duration_minutes = 30,
        priority         = "medium",
        frequency        = "weekly",
        due_date         = end_of_month
    )

    next_task = task.next_occurrence()

    # A weekly task must produce a new task (not None)
    assert next_task is not None
    # New due date must be exactly 7 days later: April 4
    assert next_task.due_date == date(2026, 4, 4)
    # Must have crossed into April
    assert next_task.due_date.month == 4
    # The rescheduled task must start as incomplete
    assert next_task.completed is False


# ── Test 14 ───────────────────────────────────────────────────────────────────
def test_once_task_does_not_recur():
    """
    A task with frequency="once" should return None from next_occurrence()
    because one-time tasks do not repeat.
    """
    task = Task("Vet visit", "09:00", 60, "high", "once")
    assert task.next_occurrence() is None


# ── Test 15 ───────────────────────────────────────────────────────────────────
def test_mark_complete_once_task_no_new_task():
    """
    Marking a "once" task complete via the Scheduler should NOT append
    a new task to the pet — the pet's task count must stay at 1.
    The existing task should be marked completed.
    """
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat")
    mochi.add_task(Task("Vet visit", "09:00", 60, "high", "once"))
    owner.add_pet(mochi)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Mochi", "Vet visit")

    # Count must still be 1 — no recurrence was added
    assert len(mochi.tasks) == 1
    # The task itself must now be marked done
    assert mochi.tasks[0].completed is True


# ── Test 16 ───────────────────────────────────────────────────────────────────
def test_mark_complete_nonexistent_task():
    """
    Calling mark_task_complete() with a title that doesn't exist should
    silently do nothing — no exception, no side effects on existing tasks.
    """
    owner = Owner("Jordan")
    rex = Pet("Rex", "dog")
    rex.add_task(Task("Morning walk", "07:00", 30, "high", "daily"))
    owner.add_pet(rex)

    scheduler = Scheduler(owner)

    # This task title does not exist — must not crash
    scheduler.mark_task_complete("Rex", "Nonexistent task")

    # Rex's task list must be unchanged
    assert len(rex.tasks) == 1


# ── Test 17 ───────────────────────────────────────────────────────────────────
def test_filter_by_pet_case_insensitive():
    """
    filter_by_pet() should match the pet name regardless of letter casing.
    "rex", "REX", and "Rex" must all return the same result.
    """
    owner = Owner("Jordan")
    rex = Pet("Rex", "dog")
    rex.add_task(Task("Morning walk", "07:00", 30, "high", "daily"))
    owner.add_pet(rex)

    scheduler = Scheduler(owner)

    assert len(scheduler.filter_by_pet("rex")) == 1   # all lowercase
    assert len(scheduler.filter_by_pet("REX")) == 1   # all uppercase
    assert len(scheduler.filter_by_pet("Rex")) == 1   # title case
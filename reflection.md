# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four classes:

- **Task** — holds title, time (HH:MM), duration, priority, frequency, completion status, and due date. Can mark itself complete and generate its next occurrence using Python's `timedelta`.
- **Pet** — stores name, species, and a list of Tasks. Exposes `add_task()` and `get_tasks()`.
- **Owner** — holds a list of Pets and returns all tasks across them as `(pet_name, task)` tuples via `get_all_tasks()`.
- **Scheduler** — the brain. Accepts an Owner and handles sorting, filtering, conflict detection, and recurring task logic.

Three core user actions: add a pet with tasks, view today's sorted schedule with conflict warnings, mark a task complete and have it auto-reschedule.

**b. Design changes**

Two changes from my initial draft:
1. Added `due_date` to `Task` — required for `timedelta` recurrence logic to work.
2. Split a generic `get_schedule()` into `filter_by_pet()` and `filter_by_status()` after realizing owners need targeted views, not just a full task dump.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time (chronological sort), priority (low/medium/high label), and frequency (once/daily/weekly with auto-reschedule). Time-based sorting took priority because a pet owner's main need is knowing what to do next throughout the day.

**b. Tradeoffs**

Conflict detection only flags tasks at the exact same start time. It does not catch overlapping durations — a 60-min task at 09:00 and a 20-min task at 09:30 would overlap but not be flagged. This is a reasonable first-version tradeoff: exact-time matching covers the most obvious mistakes without requiring complex interval comparison logic.

---

## 3. AI Collaboration

**a. How you used AI**

- **Design** — generated the Mermaid.js UML diagram from my class descriptions.
- **Scaffolding** — used Agent Mode to produce class skeletons, then filled in logic incrementally.
- **Tests** — used `#codebase` to draft an initial test plan, then extended it with edge cases manually.
- **UI** — asked Copilot to explain `st.session_state` for data persistence across Streamlit reruns.

Most effective prompts were specific and file-referenced, e.g. *"Based on #file:pawpal_system.py, how should Scheduler retrieve tasks from Owner's pets?"*

**b. Judgment and verification**

When Copilot suggested raising an `Exception` on conflict detection I rejected it — a crash is not useful to a pet owner. I changed it to collect warning strings and return a list instead, then verified by running `main.py` with two tasks at "09:00". I also rejected storing tasks as plain dictionaries inside `Pet` because it would have broken the OOP design and made Scheduler methods harder to write cleanly.

---

## 4. Testing and Verification

**a. What you tested**

17 tests across two batches:

- **Core (8):** task completion, task count, sort order, daily recurrence, conflict detection, no false conflicts, pet filter, status filter.
- **Edge cases (9):** pet with no tasks, scheduler with empty pet, owner with no pets, scheduler with no pets, weekly task crossing month boundary, "once" task not recurring, marking "once" complete adds no new task, marking nonexistent task doesn't crash, case-insensitive pet name filter.

**b. Confidence**

⭐⭐⭐⭐⭐ (5/5) — All 17 tests pass in 0.04s, covering both happy paths and edge cases. Next tests I'd add: duration-aware overlap detection and Streamlit session state persistence verification.

---

## 5. Reflection

**a. What went well**

The recurring task logic. Splitting responsibility between `Task.next_occurrence()` (calculates the date) and `Scheduler.mark_task_complete()` (decides whether to call it) kept each method small, focused, and independently testable.

**b. What you would improve**

1. Duration-aware conflict detection to catch overlapping windows, not just exact start-time matches.
2. JSON persistence via `save_to_json()` / `load_from_json()` on `Owner` so data survives between sessions.

**c. Key takeaway**

AI is most powerful as a scaffolding tool, not a decision-maker. Copilot accelerated the implementation, but the design decisions — rejecting a crashing conflict detector, keeping `Task` as a dataclass instead of a dictionary — were mine to make. The quality of the system came from the architecture, not from accepting the first AI output.
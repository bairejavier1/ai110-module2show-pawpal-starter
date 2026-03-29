from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("Jordan")

mochi = Pet("Mochi", "cat")
mochi.add_task(Task("Evening feeding", "17:00", 10, "high", "daily"))
mochi.add_task(Task("Playtime",        "09:00", 20, "medium", "daily"))
mochi.add_task(Task("Vet appointment", "09:00", 60, "high", "once"))  # conflict!

rex = Pet("Rex", "dog")
rex.add_task(Task("Morning walk",  "07:00", 30, "high", "daily"))
rex.add_task(Task("Afternoon walk","14:00", 30, "medium", "daily"))

owner.add_pet(mochi)
owner.add_pet(rex)

scheduler = Scheduler(owner)

# --- Sorted Schedule ---
print("\n📅 Today's Schedule (sorted by time):")
for pet_name, task in scheduler.get_sorted_tasks():
    status = "✅" if task.completed else "🔲"
    print(f"  {status} [{task.time}] {pet_name}: {task.title} ({task.priority} priority)")

# --- Conflict Detection ---
print("\n🚨 Conflict Check:")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(" ", w)
else:
    print("  No conflicts found.")

# --- Mark a task complete (recurring) ---
print("\n🔁 Marking 'Morning walk' complete...")
scheduler.mark_task_complete("Rex", "Morning walk")

print("\n📅 Rex's updated task list:")
for task in rex.get_tasks():
    status = "✅" if task.completed else "🔲"
    print(f"  {status} [{task.time}] {task.title} — due {task.due_date}")
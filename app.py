import re
from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Quick Demo Inputs (original starter section, now wired to backend)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Quick Demo Inputs (UI only)")

# Session state: persist the Owner object across Streamlit reruns
if "owner" not in st.session_state:
    st.session_state.owner = None

owner_name = st.text_input("Owner name", value="Jordan")
pet_name   = st.text_input("Pet name",   value="Mochi")
species    = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Create Owner & Pet"):
    new_owner = Owner(owner_name)
    new_owner.add_pet(Pet(pet_name, species))
    st.session_state.owner = new_owner
    st.success(f"✅ Created owner **{owner_name}** with pet **{pet_name}** ({species})")

# Add another pet once an owner exists
if st.session_state.owner:
    with st.expander("➕ Add another pet"):
        col_a, col_b = st.columns(2)
        with col_a:
            extra_pet_name    = st.text_input("New pet name", value="Rex")
        with col_b:
            extra_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="extra_species")
        if st.button("Add Pet"):
            existing = [p.name.lower() for p in st.session_state.owner.pets]
            if extra_pet_name.lower() in existing:
                st.warning(f"⚠️ A pet named **{extra_pet_name}** already exists.")
            else:
                st.session_state.owner.add_pet(Pet(extra_pet_name, extra_pet_species))
                st.success(f"✅ Added **{extra_pet_name}** ({extra_pet_species})")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

# Task input form (wired to real backend)
if st.session_state.owner and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title    = st.text_input("Task title", value="Morning walk")
    with col2:
        duration      = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority      = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        task_time     = st.text_input("Time (HH:MM)", value="07:00")
    with col5:
        frequency     = st.selectbox("Frequency", ["once", "daily", "weekly"])

    selected_pet = st.selectbox("Assign to pet", pet_names)

    if st.button("Add task"):
        if not re.match(r"^\d{2}:\d{2}$", task_time):
            st.error("❌ Please use HH:MM format (e.g. 07:00)")
        else:
            for pet in st.session_state.owner.pets:
                if pet.name == selected_pet:
                    pet.add_task(Task(
                        title            = task_title,
                        time             = task_time,
                        duration_minutes = int(duration),
                        priority         = priority,
                        frequency        = frequency,
                        due_date         = date.today()
                    ))
                    st.success(f"✅ Added **{task_title}** to {selected_pet}'s schedule")
                    break

    # Show current tasks table
    all_tasks = st.session_state.owner.get_all_tasks() if st.session_state.owner else []
    if all_tasks:
        st.write("Current tasks:")
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        status_icon   = {True: "✅", False: "🔲"}
        st.table([
            {
                "Status"   : status_icon[t.completed],
                "Pet"      : pn,
                "Task"     : t.title,
                "Time"     : t.time,
                "Priority" : f"{priority_icon.get(t.priority,'')} {t.priority}",
                "Duration" : f"{t.duration_minutes} min",
                "Frequency": t.frequency,
            }
            for pn, t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Create an owner and pet above before adding tasks.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Build Schedule (original starter button, now fully implemented)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Build Schedule")
st.caption("This button calls your scheduling logic and displays the results.")

if st.button("Generate schedule"):
    if not st.session_state.owner or not st.session_state.owner.get_all_tasks():
        st.warning("⚠️ Add an owner, a pet, and at least one task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # Conflict warnings
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("✅ No scheduling conflicts detected")

        # Sorted schedule table
        sorted_tasks = scheduler.get_sorted_tasks()
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        status_icon   = {True: "✅", False: "🔲"}

        st.markdown("#### 📅 Today's Schedule (sorted by time)")
        st.table([
            {
                "Status"   : status_icon[t.completed],
                "Time"     : t.time,
                "Pet"      : pn,
                "Task"     : t.title,
                "Priority" : f"{priority_icon.get(t.priority,'')} {t.priority}",
                "Duration" : f"{t.duration_minutes} min",
                "Frequency": t.frequency,
                "Due"      : str(t.due_date),
            }
            for pn, t in sorted_tasks
        ])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Mark Task Complete
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.owner:
    incomplete = [
        (pn, t) for pn, t in st.session_state.owner.get_all_tasks()
        if not t.completed
    ]
    if incomplete:
        st.divider()
        st.subheader("✔️ Mark Task Complete")
        labels       = [f"{pn}: {t.title} @ {t.time}" for pn, t in incomplete]
        selected_lbl = st.selectbox("Select a task", labels)

        if st.button("Mark Complete"):
            idx      = labels.index(selected_lbl)
            pn       = incomplete[idx][0]
            title    = incomplete[idx][1].title
            freq     = incomplete[idx][1].frequency
            Scheduler(st.session_state.owner).mark_task_complete(pn, title)
            if freq in ("daily", "weekly"):
                st.success(f"✅ **{title}** marked complete — next {freq} occurrence scheduled!")
            else:
                st.success(f"✅ **{title}** marked complete!")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Filter Tasks
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.owner and st.session_state.owner.get_all_tasks():
    st.divider()
    st.subheader("🔍 Filter Tasks")
    scheduler = Scheduler(st.session_state.owner)

    col1, col2 = st.columns(2)
    with col1:
        filter_pet    = st.selectbox("Filter by pet",    ["All"] + [p.name for p in st.session_state.owner.pets])
    with col2:
        filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

    filtered = scheduler.filter_by_pet(filter_pet) if filter_pet != "All" else st.session_state.owner.get_all_tasks()
    if filter_status == "Incomplete":
        filtered = [(pn, t) for pn, t in filtered if not t.completed]
    elif filter_status == "Complete":
        filtered = [(pn, t) for pn, t in filtered if t.completed]

    if not filtered:
        st.info("No tasks match this filter.")
    else:
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        status_icon   = {True: "✅", False: "🔲"}
        st.table([
            {
                "Status"   : status_icon[t.completed],
                "Time"     : t.time,
                "Pet"      : pn,
                "Task"     : t.title,
                "Priority" : f"{priority_icon.get(t.priority,'')} {t.priority}",
                "Frequency": t.frequency,
            }
            for pn, t in filtered
        ])
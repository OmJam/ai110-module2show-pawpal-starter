from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session State  —  "the vault"
#
# Streamlit reruns this entire script from top to bottom on every interaction.
# Without session_state, every click would wipe your objects and start fresh.
#
# st.session_state works like a persistent dictionary:
#   - Keys you store in it survive reruns for the lifetime of the browser tab.
#   - The pattern below checks "is this key already in the vault?" before
#     creating a new object, so existing data is never accidentally overwritten.
#
# Pattern:
#   if "key" not in st.session_state:
#       st.session_state.key = <initial value>
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None          # Owner object, set when the form is submitted

if "pet" not in st.session_state:
    st.session_state.pet = None            # The currently active Pet

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()   # Created once, reused for every plan

# ---------------------------------------------------------------------------
# Section 1 — Owner Setup
# ---------------------------------------------------------------------------
st.subheader("👤 Owner Setup")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First name", placeholder="e.g. Jordan")
        last_name  = st.text_input("Last name",  placeholder="e.g. Rivera")
    with col2:
        email          = st.text_input("Email", placeholder="e.g. jordan@email.com")
        time_available = st.number_input(
            "Minutes available today", min_value=0, max_value=480, value=90
        )
    owner_submitted = st.form_submit_button("Save Owner")

if owner_submitted:
    st.session_state.owner = Owner(
        first_name=first_name,
        last_name=last_name,
        age=0,
        email=email,
        time_available=int(time_available),
    )
    st.success(f"Owner **{first_name} {last_name}** saved!")

if st.session_state.owner:
    o = st.session_state.owner
    st.caption(
        f"Active owner: **{o.first_name} {o.last_name}** | {o.time_available} min available today"
    )

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Pet Setup
# ---------------------------------------------------------------------------
st.subheader("🐾 Pet Setup")

with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name  = st.text_input("Pet name",    placeholder="e.g. Mochi")
    with col2:
        pet_age   = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    with col3:
        pet_breed = st.text_input("Breed",        placeholder="e.g. Tabby Cat")
    pet_submitted = st.form_submit_button("Save Pet")

if pet_submitted:
    if st.session_state.owner is None:
        st.warning("Save an owner first, then add a pet.")
    else:
        new_pet = Pet(name=pet_name, age=int(pet_age), breed=pet_breed)
        st.session_state.pet = new_pet
        st.session_state.owner.add_pet(new_pet)
        st.success(f"**{pet_name}** added to {st.session_state.owner.first_name}'s profile!")

if st.session_state.owner and st.session_state.owner.get_pets():
    pet_names = [p.get_name() for p in st.session_state.owner.get_pets()]
    selected_name = st.selectbox("Active pet", pet_names, key="active_pet")
    st.session_state.pet = next(
        p for p in st.session_state.owner.get_pets() if p.get_name() == selected_name
    )
    p = st.session_state.pet
    st.caption(f"Active pet: **{p.get_name()}** — {p.get_breed()}, age {p.get_age()}")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Add Tasks
# ---------------------------------------------------------------------------
st.subheader("📋 Add Tasks")

with st.form("task_form"):
    col1, col2 = st.columns(2)
    with col1:
        task_name  = st.text_input("Task name",   placeholder="e.g. Morning Walk")
        task_desc  = st.text_input("Description", placeholder="optional details")
        start_time = st.text_input("Start time (HH:MM)", placeholder="e.g. 08:00")
    with col2:
        task_duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        task_type = st.selectbox(
            "Type", ["walk", "feed", "medication", "grooming", "appointment", "other"]
        )
        task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    col3, col4 = st.columns(2)
    with col3:
        is_recurring = st.checkbox("Recurring task")
    with col4:
        recurrence_days = st.number_input(
            "Repeat every N days", min_value=1, max_value=365, value=1,
            disabled=not is_recurring
        )
    task_submitted = st.form_submit_button("Add Task")

if task_submitted:
    if st.session_state.pet is None:
        st.warning("Save a pet first before adding tasks.")
    else:
        new_task = Task(
            name=task_name,
            duration=int(task_duration),
            description=task_desc,
            task_type=task_type,
            priority=task_priority,
            start_time=start_time,
            is_recurring=is_recurring,
            recurrence_days=int(recurrence_days),
        )
        st.session_state.pet.add_task(new_task)
        st.success(f"Task **{task_name}** added!")

# Task list with status filter
if st.session_state.pet and st.session_state.pet.get_tasks():
    st.write(f"Tasks for **{st.session_state.pet.get_name()}**:")

    status_filter = st.selectbox(
        "Filter by status", ["all", "pending", "completed"], key="task_filter"
    )

    tasks_to_show = st.session_state.pet.get_tasks()
    if status_filter != "all":
        tasks_to_show = [t for t in tasks_to_show if t.get_status() == status_filter]

    if tasks_to_show:
        st.table(
            [
                {
                    "Task":           t.get_name(),
                    "Start":          t.get_start_time() or "—",
                    "Due":            t.get_due_date() or "—",
                    "Duration (min)": t.get_duration(),
                    "Type":           t.get_task_type(),
                    "Priority":       t.get_priority(),
                    "Status":         t.get_status(),
                    "Recurring":      "yes" if t.get_is_recurring() else "no",
                }
                for t in tasks_to_show
            ]
        )
    else:
        st.info(f"No {status_filter} tasks.")
else:
    st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Mark Task Complete
# ---------------------------------------------------------------------------
if st.session_state.pet and st.session_state.pet.get_tasks():
    pending = [t for t in st.session_state.pet.get_tasks() if t.get_status() == "pending"]
    if pending:
        st.markdown("**Mark a task complete:**")
        col_a, col_b = st.columns([3, 1])
        with col_a:
            task_names   = [t.get_name() for t in pending]
            selected_name = st.selectbox("Select task", task_names, key="complete_select")
        with col_b:
            st.write("")   # vertical alignment spacer
            st.write("")
            if st.button("Complete"):
                selected_task = next(t for t in pending if t.get_name() == selected_name)
                next_task = st.session_state.scheduler.mark_task_complete(
                    selected_task, st.session_state.pet
                )
                if next_task:
                    st.success(
                        f"'{selected_name}' marked complete. "
                        f"Next occurrence created — due {next_task.get_due_date()}."
                    )
                else:
                    st.success(f"'{selected_name}' marked complete.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("📅 Generate Schedule")

if st.button("Generate Schedule"):
    owner     = st.session_state.owner
    scheduler = st.session_state.scheduler

    if owner is None:
        st.error("Please set up an owner first.")
    elif not owner.get_pets() or not any(p.get_tasks() for p in owner.get_pets()):
        st.warning("Add at least one pet with tasks before generating a schedule.")
    else:
        plan        = scheduler.create_plan(owner)
        explanation = scheduler.create_explanation()
        conflicts   = scheduler.detect_conflicts(owner)

        # Conflict warnings
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠ {warning}")

        if plan:
            total = sum(t.get_duration() for t in plan)
            st.success(f"Scheduled **{len(plan)} task(s)** — {total} min total")

            # Display sorted by start time for a readable daily timeline
            sorted_plan = scheduler.sort_by_time(plan)
            st.table(
                [
                    {
                        "Start":          t.get_start_time() or "—",
                        "Task":           t.get_name(),
                        "Duration (min)": t.get_duration(),
                        "Priority":       t.get_priority(),
                        "Type":           t.get_task_type(),
                        "Recurring":      "yes" if t.get_is_recurring() else "no",
                    }
                    for t in sorted_plan
                ]
            )
            with st.expander("Why this plan?"):
                st.text(explanation)
        else:
            st.warning("No tasks fit within the available time.")

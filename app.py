"""PawPal+ Streamlit UI — thin presentation layer over pawpal_system."""
import streamlit as st

from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan your pets' care day: add pets and tasks, then generate a prioritized schedule.")

# --- Session memory: one Owner persists across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Owner + pet entry ---
with st.sidebar:
    st.header("Setup")
    owner.name = st.text_input("Owner name", value=owner.name)

    st.subheader("Add a pet")
    new_pet = st.text_input("Pet name", key="new_pet_name")
    new_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    if st.button("Add pet"):
        if new_pet and owner.get_pet(new_pet) is None:
            owner.add_pet(Pet(new_pet, new_species))
            st.success(f"Added {new_pet} 🐾")
        elif owner.get_pet(new_pet):
            st.warning(f"{new_pet} already exists.")
        else:
            st.warning("Enter a pet name first.")

if not owner.pets:
    st.info("Add a pet in the sidebar to get started.")
    st.stop()

# --- Task entry ---
st.subheader("Add a task")
with st.form("add_task", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
        title = st.text_input("Task title", value="Walk")
        time_str = st.text_input("Time (HH:MM)", value="08:00")
    with c2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
        priority_name = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"])
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
    if st.form_submit_button("Add task"):
        owner.get_pet(pet_name).add_task(
            Task(title, int(duration), Priority[priority_name], time=time_str, frequency=frequency)
        )
        st.success(f"Added '{title}' for {pet_name}.")

# --- Schedule display ---
st.divider()
st.subheader("📅 Today's Schedule")

if not owner.all_tasks():
    st.info("No tasks yet. Add one above.")
else:
    conflicts = scheduler.detect_conflicts()
    for c in conflicts:
        st.warning(f"⚠️ {c}")
    if not conflicts:
        st.success("No scheduling conflicts. ✅")

    icon = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}
    rows = []
    pet_of = {id(t): p.name for p, t in owner.all_tasks_with_pet()}
    for t in scheduler.todays_schedule():
        rows.append({
            "Done": "✅" if t.completed else "⬜",
            "Time": t.time,
            "Priority": f"{icon[t.priority]} {t.priority.name}",
            "Pet": pet_of[id(t)],
            "Task": t.title,
            "Duration": f"{t.duration_minutes} min",
            "Repeats": t.frequency,
        })
    st.table(rows)

    slot = scheduler.next_available_slot(30)
    st.caption(f"🕒 Next free 30-min slot: {slot if slot else 'none — day is full'}")

import streamlit as st
import pandas as pd
import subprocess
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime
from src.tasks import (load_tasks, save_tasks, filter_tasks_by_priority, filter_tasks_by_category,
                      generate_unique_id, clear_completed_tasks, sort_tasks_by_due_date, postpone_task_due_date)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def main():
    st.title("To-Do Application")
    
    # Load existing tasks
    tasks = load_tasks()
    
    # Sidebar for adding new tasks
    st.sidebar.header("Add New Task")
    
    # Task creation form
    with st.sidebar.form("new_task_form"):
        task_title = st.text_input("Task Title")
        task_description = st.text_area("Description")
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
        task_due_date = st.date_input("Due Date")
        submit_button = st.form_submit_button("Add Task")
        
        if submit_button and task_title:
            new_task = {
                "id": generate_unique_id(tasks),
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")
    
    # Main area to display tasks
    st.header("Your Tasks")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set([task["category"] for task in tasks])))
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    
    show_completed = st.checkbox("Show Completed Tasks")
    
    # Apply filters
    filtered_tasks = tasks.copy()
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    if not show_completed:
        filtered_tasks = [task for task in filtered_tasks if not task["completed"]]
    
    # Display tasks
    for task in filtered_tasks:
        col1, col2 = st.columns([4, 1])
        with col1:
            if task["completed"]:
                st.markdown(f"~~**{task['title']}**~~")
            else:
                st.markdown(f"**{task['title']}**")
            st.write(task["description"])
            st.caption(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")
        with col2:
            if st.button("Complete" if not task["completed"] else "Undo", key=f"complete_{task['id']}"):
                for t in tasks:
                    if t["id"] == task["id"]:
                        t["completed"] = not t["completed"]
                        save_tasks(tasks)
                        st.rerun()
            if st.button("Delete", key=f"delete_{task['id']}"):
                tasks = [t for t in tasks if t["id"] != task["id"]]
                save_tasks(tasks)
                st.rerun()
    
    # Unit Test
    st.markdown("---")
    if st.button("▶️ Run Unit Tests"):
        with st.spinner("Running pytest…"):
            result = subprocess.run(
                ["pytest", "tests/test_basic.py", "-v", "-s", "--disable-warnings"],
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            st.success("✅ Step 1 unit tests passed!")
        else:
            st.error("❌ Some unit tests failed")

        st.text_area("📝 Test Output", result.stdout + result.stderr, height=400)

    st.markdown("---")
    st.subheader("Step 3: Pytest Features")
    c1, c2 = st.columns(2)

    # Coverage
    if c1.button("▶️ Coverage"):
        with st.spinner("Running pytest with coverage…"):
            cov = subprocess.run(
                [
                    "pytest",
                    "--maxfail=1",
                    "--disable-warnings",
                    "--cov=src.tasks",
                    "--cov-report=term-missing",
                ],
                capture_output=True,
                text=True,
            )
        if cov.returncode == 0:
            st.success("✅ Coverage run passed!")
        else:
            st.error("❌ Coverage run failed")
        st.text_area("📝 Coverage Output", cov.stdout + cov.stderr, height=300)

    # HTML Report
    if c1.button("▶️ HTML Report"):
        with st.spinner("Generating HTML report…"):
            html = subprocess.run(
                [
                    "pytest",
                    "--maxfail=1",
                    "--disable-warnings",
                    "--html=report.html",
                    "--self-contained-html",
                ],
                capture_output=True,
                text=True,
            )
        if html.returncode == 0:
            st.success("✅ HTML report generated")
            st.markdown("[Download report.html](report.html)")
        else:
            st.error("❌ Report generation failed")
        st.text_area("📝 HTML Report Output", html.stdout + html.stderr, height=300)

    # Parametrized Tests
    if c2.button("▶️ Parametrized"):
        with st.spinner("Running parameterized tests…"):
            param = subprocess.run(
                [
                    "pytest",
                    "-q",
                    "tests/test_advanced.py::test_filter_by_priority_param",
                ],
                capture_output=True,
                text=True,
            )
        if param.returncode == 0:
            st.success("✅ Parametrized tests passed")
        else:
            st.error("❌ Parametrized tests failed")
        st.text_area("📝 Parametrized Output", param.stdout + param.stderr, height=200)

    # Mocking Tests
    if c2.button("▶️ Mocking"):
        with st.spinner("Running mocking tests…"):
            mock = subprocess.run(
                [
                    "pytest",
                    "-q",
                    "tests/test_advanced.py::test_save_tasks_uses_json_dump",
                ],
                capture_output=True,
                text=True,
            )
        if mock.returncode == 0:
            st.success("✅ Mocking tests passed")
        else:
            st.error("❌ Mocking tests failed")
        st.text_area("📝 Mocking Output", mock.stdout + mock.stderr, height=200)

    st.markdown("---")
    st.subheader("Step 4: TDD-Driven Features")

    # Load once at the start
    tasks = load_tasks()

    # 1) Clear Completed Tasks
    if st.button("🧹 Clear Completed Tasks"):
        tasks = clear_completed_tasks(tasks)
        save_tasks(tasks)
        st.success("✅ Completed tasks removed")

    # 2) Sort by Due Date
    st.write("Sort tasks by due date:")
    col1, col2 = st.columns([1,3])
    with col1:
        sort_order = st.selectbox("Order", ["Ascending", "Descending"])
    with col2:
        if st.button("↕️ Apply Sort"):
            ascending = sort_order == "Ascending"
            tasks = sort_tasks_by_due_date(tasks, ascending=ascending)
            save_tasks(tasks)
            st.success(f"✅ Tasks sorted {sort_order.lower()}")

    # 3) Postpone a Task
    st.write("Postpone a task’s due date:")
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        task_ids = [t["id"] for t in tasks]
        if task_ids:
            chosen = st.selectbox("Task ID", task_ids)
        else:
            chosen = None
    with col2:
        days = st.number_input("Days to add", min_value=1, value=1)
    with col3:
        if st.button("⏩ Postpone"):
            if chosen is not None:
                tasks = postpone_task_due_date(tasks, task_id=chosen, days=days)
                save_tasks(tasks)
                st.success(f"✅ Task {chosen} postponed by {days} days")
            else:
                st.error("⚠️ No tasks available to postpone")

    # Refresh display
    st.markdown("**Current Tasks**")
    st.table(tasks)

    st.markdown("---")
    st.subheader("Step 5b: Detailed BDD Test Run")

    if st.button("🧪 Run BDD Tests (Detailed)"):
        with st.spinner("Running BDD tests in verbose mode…"):
            detailed = subprocess.run(
                [
                    "pytest",
                    "-v",
                    "--disable-warnings",
                    "tests/feature"
                ],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
        st.text_area(
            "📝 Detailed BDD Output",
            detailed.stdout + detailed.stderr,
            height=600,
        )
        if detailed.returncode == 0:
            st.success("✅ All BDD scenarios passed")
        else:
            st.error("❌ Some BDD scenarios failed")

    st.markdown("---")
    st.subheader("Step 6: Property-Based Testing")

    if st.button("▶️ Property-Based"):
        with st.spinner("Running Hypothesis tests…"):
            prop = subprocess.run(
                ["pytest", "-q", "tests/test_property.py"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
        if prop.returncode == 0:
            st.success("✅ Property-based tests passed")
        else:
            st.error("❌ Property-based tests failed")
        st.text_area("📝 Property-Based Output", prop.stdout + prop.stderr, height=400)

if __name__ == "__main__":
    main()
import datetime
from hypothesis import given, strategies as st
from src.tasks import (
    generate_unique_id,
    filter_tasks_by_priority,
    filter_tasks_by_completion,
    search_tasks,
    postpone_task_due_date,
)

@given(st.integers(min_value=0, max_value=10))
def test_generate_unique_id_sequence(n):
    # If IDs are 1..n, the next should be n+1
    tasks = [{"id": i + 1} for i in range(n)]
    new = generate_unique_id(tasks)
    assert new == n + 1

@given(st.lists(st.integers(min_value=1, max_value=20), unique=True))
def test_generate_unique_id_not_in_existing(ids):
    tasks = [{"id": x} for x in ids]
    new = generate_unique_id(tasks)
    assert new not in ids
    assert isinstance(new, int) and new > 0

@given(
    st.lists(
        st.fixed_dictionaries({
            "id": st.integers(min_value=1, max_value=100),
            "priority": st.sampled_from(["Low", "Medium", "High"]),
        }),
        min_size=1,
    )
)
def test_filter_tasks_by_priority(tasks):
    for p in ["Low", "Medium", "High"]:
        out = filter_tasks_by_priority(tasks, p)
        # All returned tasks have priority p
        assert all(t["priority"] == p for t in out)
        # They’re a subset of the original list
        assert all(t in tasks for t in out)

@given(
    st.lists(
        st.fixed_dictionaries({
            "id": st.integers(min_value=1, max_value=100),
            "completed": st.booleans(),
        }),
        min_size=1,
    )
)
def test_filter_tasks_by_completion(tasks):
    for c in [True, False]:
        out = filter_tasks_by_completion(tasks, c)
        assert all(t["completed"] == c for t in out)
        assert all(t in tasks for t in out)

@given(
    st.lists(
        st.fixed_dictionaries({
            "id": st.integers(min_value=1, max_value=100),
            "title": st.text(min_size=1),
            "description": st.text(),
        }),
        min_size=1,
    ),
    st.text(min_size=1),
)
def test_search_tasks(tasks, keyword):
    out = search_tasks(tasks, keyword)
    # Every result must contain the keyword in title or description
    assert all(
        keyword.lower() in (t["title"] + t["description"]).lower()
        for t in out
    )
    assert all(t in tasks for t in out)

@given(st.dates(), st.integers(min_value=0, max_value=365))
def test_postpone_task_due_date(date, days):
    s = date.strftime("%Y-%m-%d")
    task = {"id": 1, "due_date": s}
    out = postpone_task_due_date([task], 1, days)
    expected = (date + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    assert out[0]["due_date"] == expected

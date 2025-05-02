import pytest
from datetime import datetime, timedelta

# We expect these to be defined in src/tasks.py
from src.tasks import (
    clear_completed_tasks,
    sort_tasks_by_due_date,
    postpone_task_due_date,
)

@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "A", "due_date": "2025-01-01", "completed": False},
        {"id": 2, "title": "B", "due_date": "2025-01-02", "completed": True},
        {"id": 3, "title": "C", "due_date": "2025-01-03", "completed": False},
    ]

def test_clear_completed_tasks(sample_tasks):
    remaining = clear_completed_tasks(sample_tasks)
    # Only tasks 1 and 3 remain
    assert {t["id"] for t in remaining} == {1, 3}
    assert all(not t["completed"] for t in remaining)

def test_sort_tasks_by_due_date_ascending(sample_tasks):
    # scramble the order
    mixed = sample_tasks[::-1]
    sorted_tasks = sort_tasks_by_due_date(mixed, ascending=True)
    assert [t["id"] for t in sorted_tasks] == [1, 2, 3]

def test_sort_tasks_by_due_date_descending(sample_tasks):
    sorted_desc = sort_tasks_by_due_date(sample_tasks, ascending=False)
    assert [t["id"] for t in sorted_desc] == [3, 2, 1]

def test_postpone_task_due_date(sample_tasks):
    postponed = postpone_task_due_date(sample_tasks, task_id=1, days=10)
    # Task 1’s date should now be 2025-01-11
    assert any(
        t["id"] == 1 and t["due_date"] == "2025-01-11"
        for t in postponed
    )

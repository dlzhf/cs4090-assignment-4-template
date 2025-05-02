import json
import tempfile
import sys, os
import pytest
import src.tasks as tasks
import src.app   as app
import streamlit as st
from datetime import datetime, timedelta
from types import SimpleNamespace

# import your functions
from src.tasks import (
    load_tasks,
    save_tasks,
    generate_unique_id,
    filter_tasks_by_priority,
    filter_tasks_by_category,
    filter_tasks_by_completion,
    search_tasks,
    get_overdue_tasks,
)


@pytest.fixture
def sample_tasks_file(tmp_path):
    """Create a temp JSON file with two example tasks."""
    tasks = [
        {
            "id": 1,
            "title": "Buy milk",
            "description": "2 liters",
            "priority": "High",
            "category": "Personal",
            "due_date": "2025-01-01",
            "completed": False,
        },
        {
            "id": 2,
            "title": "Send report",
            "description": "Q1 numbers",
            "priority": "Medium",
            "category": "Work",
            "due_date": "2020-01-01",
            "completed": False,
        },
    ]
    p = tmp_path / "tasks.json"
    p.write_text(json.dumps(tasks))
    return str(p), tasks


def test_load_tasks_missing_file(tmp_path):
    # If file doesn't exist, load_tasks should return []
    missing = tmp_path / "nope.json"
    assert load_tasks(str(missing)) == []


def test_load_and_save_roundtrip(tmp_path):
    path = tmp_path / "round.json"
    tasks = [{"id": 42, "title": "Test"}]
    save_tasks(tasks, str(path))
    loaded = load_tasks(str(path))
    assert loaded == tasks


def test_generate_unique_id_empty():
    assert generate_unique_id([]) == 1


def test_generate_unique_id_nonempty():
    existing = [{"id": 3}, {"id": 7}, {"id": 2}]
    assert generate_unique_id(existing) == 8


def test_filter_tasks_by_priority(sample_tasks_file):
    _, tasks = sample_tasks_file
    high = filter_tasks_by_priority(tasks, "High")
    assert len(high) == 1 and high[0]["id"] == 1


def test_filter_tasks_by_category(sample_tasks_file):
    _, tasks = sample_tasks_file
    work = filter_tasks_by_category(tasks, "Work")
    assert work == [tasks[1]]


def test_filter_tasks_by_completion(sample_tasks_file):
    _, tasks = sample_tasks_file
    # mark first as complete
    tasks[0]["completed"] = True
    completed = filter_tasks_by_completion(tasks, True)
    assert completed == [tasks[0]]


def test_search_tasks_case_insensitive(sample_tasks_file):
    _, tasks = sample_tasks_file
    # search for “report”
    found = search_tasks(tasks, "REPORT")
    assert len(found) == 1 and found[0]["id"] == 2


def test_get_overdue_tasks(monkeypatch, sample_tasks_file):
    _, tasks = sample_tasks_file
    # freeze “now” just after 2020-01-02
    class FakeDateTime:
        @classmethod
        def now(cls):
            return datetime(2020, 1, 2)
    monkeypatch.setattr("src.tasks.datetime", FakeDateTime)

    overdue = get_overdue_tasks(tasks)
    # only the 2020-01-01 task is overdue
    assert all(t["due_date"] < "2020-01-02" for t in overdue)
    assert overdue[0]["id"] == 2

def test_default_tasks_file_is_in_src():
    # The DEFAULT_TASKS_FILE should always point to src/tasks.json
    expected = os.path.join(os.path.dirname(tasks.__file__), "tasks.json")
    assert tasks.DEFAULT_TASKS_FILE == expected
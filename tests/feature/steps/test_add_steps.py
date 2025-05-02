import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from src.tasks import (
    load_tasks,
    save_tasks,
    generate_unique_id,
    filter_tasks_by_priority,
    search_tasks,
)

scenarios(os.path.join(os.path.dirname(__file__), "..", "add_task.feature"))

@pytest.fixture(autouse=True)
def temp_tasks_file(monkeypatch, tmp_path):
    """Use a fresh tasks.json for each scenario."""
    fake = tmp_path / "tasks.json"
    fake.write_text("[]")
    import src.tasks as tasks_mod
    monkeypatch.setattr(tasks_mod, "DEFAULT_TASKS_FILE", str(fake))
    return fake

@given("I start with no tasks")
def start_empty():
    pass

@when(parsers.parse('I add a task titled "{title}"'))
def add_task(title):
    tasks = load_tasks()
    tasks.append({
        "id": generate_unique_id(tasks),
        "title": title,
        "description": "",
        "priority": "",
        "category": "",
        "due_date": "",
        "completed": False,
    })
    save_tasks(tasks)

@then(parsers.parse('I should have exactly {count:d} task titled "{title}"'))
def verify_count_and_title(count, title):
    tasks = load_tasks()
    assert len(tasks) == count
    assert tasks and tasks[0]["title"] == title

@given(parsers.parse('I have a task titled "{title}"'))
def have_one_task(title):
    save_tasks([{
        "id": 1,
        "title": title,
        "description": "",
        "priority": "",
        "category": "",
        "due_date": "",
        "completed": False,
    }])

@when(parsers.parse('I delete the task titled "{title}"'))
def delete_by_title(title):
    tasks = [t for t in load_tasks() if t["title"] != title]
    save_tasks(tasks)

@then("I should have no tasks")
def verify_no_tasks():
    assert load_tasks() == []

@when(parsers.parse('I mark the task titled "{title}" as completed'))
def mark_completed(title):
    tasks = load_tasks()
    for t in tasks:
        if t["title"] == title:
            t["completed"] = True
    save_tasks(tasks)

@then(parsers.parse('the task titled "{title}" should be marked completed'))
def verify_marked_completed(title):
    t = next((t for t in load_tasks() if t["title"] == title), None)
    assert t and t["completed"]

@given(parsers.parse(
    'I have tasks titled "{t1}" with priority "{p1}" and "{t2}" with priority "{p2}"'
))
def have_two_with_priorities(t1, p1, t2, p2):
    save_tasks([
        {"id":1, "title":t1, "description":"", "priority":p1, "category":"", "due_date":"", "completed":False},
        {"id":2, "title":t2, "description":"", "priority":p2, "category":"", "due_date":"", "completed":False},
    ])

@when(parsers.parse('I filter tasks by priority "{priority}"'))
def filter_by_prio(priority):
    save_tasks(filter_tasks_by_priority(load_tasks(), priority))

@then(parsers.parse('I should only see the task titled "{title}"'))
def verify_single_title(title):
    tasks = load_tasks()
    assert len(tasks) == 1 and tasks[0]["title"] == title

@given(parsers.parse('I have tasks titled "{t1}" and "{t2}"'))
def have_two_titles(t1, t2):
    save_tasks([
        {"id":1, "title":t1, "description":"", "priority":"", "category":"", "due_date":"", "completed":False},
        {"id":2, "title":t2, "description":"", "priority":"", "category":"", "due_date":"", "completed":False},
    ])

@when(parsers.parse('I search for "{query}"'))
def do_search(query):
    save_tasks(search_tasks(load_tasks(), query))
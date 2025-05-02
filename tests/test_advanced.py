import json
import pytest
from src.tasks import (
    save_tasks,
    load_tasks,
    filter_tasks_by_priority,
)

# 1. Parameterization
@pytest.mark.parametrize(
    "tasks, priority, expected_ids",
    [
        ([{"id":1,"priority":"High"},{"id":2,"priority":"Low"}], "High", [1]),
        ([{"id":3,"priority":"High"},{"id":4,"priority":"High"}], "High", [3,4]),
        ([], "Medium", []),
    ],
)
def test_filter_by_priority_param(tasks, priority, expected_ids):
    result = filter_tasks_by_priority(tasks, priority)
    assert [t["id"] for t in result] == expected_ids

# 2. Mocking
def test_save_tasks_uses_json_dump(tmp_path, monkeypatch):
    import src.tasks as tasks_module

    called = {}
    def fake_dump(obj, fp, indent=None):
        called['obj']    = obj
        called['fp']     = fp
        called['indent'] = indent

    monkeypatch.setattr(tasks_module.json, 'dump', fake_dump)

    data = [{'id': 42, 'title': 'Foo'}]
    out_file = tmp_path / "out.json"

    # Run save_tasks — it will open out_file and then call fake_dump
    tasks_module.save_tasks(data, str(out_file))

    # Assertions
    assert called['obj'] == data
    # The file-like passed to json.dump should have .name == our path
    assert hasattr(called['fp'], 'name')
    assert called['fp'].name == str(out_file)
    # And indent kwarg should be 2
    assert called['indent'] == 2

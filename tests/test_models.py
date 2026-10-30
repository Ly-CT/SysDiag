# ===== tests/test_models.py =====
from sysdiag.models import Check, ModuleResult, Status


def test_module_status_is_worst_check():
    r = ModuleResult("x", [Check("a", Status.OK), Check("b", Status.WARN), Check("c", Status.OK)])
    assert r.status is Status.WARN


def test_empty_module_is_skip():
    assert ModuleResult("x").status is Status.SKIP
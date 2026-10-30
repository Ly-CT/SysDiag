# ===== tests/test_powershell.py =====
import pytest

from sysdiag import powershell


def test_missing_powershell(monkeypatch):
    monkeypatch.setattr(powershell.shutil, "which", lambda _: None)
    with pytest.raises(powershell.PowerShellError):
        powershell.run_ps("1")


def test_parses_json(monkeypatch):
    class Proc:
        returncode = 0
        stdout = '{"a": 1}'
        stderr = ""

    monkeypatch.setattr(powershell.shutil, "which", lambda _: "powershell")
    monkeypatch.setattr(powershell.subprocess, "run", lambda *a, **k: Proc())
    assert powershell.run_ps("x") == {"a": 1}


def test_as_list():
    assert powershell.as_list(None) == []
    assert powershell.as_list({"a": 1}) == [{"a": 1}]
    assert powershell.as_list([1, 2]) == [1, 2]

# ===== tests/test_report.py =====
from sysdiag.models import Check, ModuleResult, Status
from sysdiag.report import build_report, render_html


def test_html_escapes_dynamic_content():
    results = [ModuleResult("M", [Check("<script>alert(1)</script>", Status.OK, "<b>x</b>")])]
    out = render_html(build_report(results))
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
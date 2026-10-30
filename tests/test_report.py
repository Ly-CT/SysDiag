# ===== tests/test_report.py =====
from sysdiag.models import Check, ModuleResult, Status
from sysdiag.report import build_report, render_html


def test_html_escapes_dynamic_content():
    results = [ModuleResult("M", [Check("<script>alert(1)</script>", Status.OK, "<b>x</b>")])]
    out = render_html(build_report(results))
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
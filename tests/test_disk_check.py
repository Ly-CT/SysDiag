# ===== tests/test_disk_check.py =====
from collections import namedtuple

from sysdiag.models import Config, Status
from sysdiag.modules import disk_check

Usage = namedtuple("Usage", "total used free")


def _run_with(monkeypatch, free_pct: int):
    monkeypatch.setattr(disk_check, "list_fixed_drives", lambda: ["C:\\"])
    monkeypatch.setattr(disk_check.shutil, "disk_usage", lambda root: Usage(100, 100 - free_pct, free_pct))
    return disk_check.run(Config())[0]


def test_disk_ok(monkeypatch):
    assert _run_with(monkeypatch, 50).status is Status.OK


def test_disk_warn(monkeypatch):
    assert _run_with(monkeypatch, 15).status is Status.WARN


def test_disk_fail(monkeypatch):
    assert _run_with(monkeypatch, 5).status is Status.FAIL
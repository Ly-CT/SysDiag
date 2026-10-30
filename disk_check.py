# ===== src/sysdiag/modules/disk_check.py =====
from __future__ import annotations

import os
import shutil
import string

from ..models import Check, Config, Status

NAME = "Disk Check"
_GB = 1024**3


def list_fixed_drives() -> list[str]:
    """Solo discos fijos: evita que unidades de red o lectores vacíos bloqueen la consulta."""
    if os.name != "nt":
        return ["/"]
    import ctypes

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    mask = kernel32.GetLogicalDrives()
    drives = []
    for i, letter in enumerate(string.ascii_uppercase):
        root = f"{letter}:\\"
        if mask & (1 << i) and kernel32.GetDriveTypeW(root) == 3:  # DRIVE_FIXED
            drives.append(root)
    return drives


def run(config: Config) -> list[Check]:
    checks: list[Check] = []
    for root in list_fixed_drives():
        name = f"Unidad {root}"
        try:
            usage = shutil.disk_usage(root)
        except OSError as exc:
            checks.append(Check(name, Status.ERROR, str(exc)))
            continue
        free_pct = usage.free / usage.total * 100 if usage.total else 0.0
        if free_pct < config.disk_fail_pct:
            status = Status.FAIL
        elif free_pct < config.disk_warn_pct:
            status = Status.WARN
        else:
            status = Status.OK
        checks.append(
            Check(
                name,
                status,
                f"{free_pct:.1f}% libre ({usage.free / _GB:.1f} de {usage.total / _GB:.1f} GB)",
                {"total_bytes": usage.total, "free_bytes": usage.free, "free_pct": round(free_pct, 1)},
            )
        )
    if not checks:
        checks.append(Check("Unidades", Status.SKIP, "No se encontraron unidades fijas"))
    return checks
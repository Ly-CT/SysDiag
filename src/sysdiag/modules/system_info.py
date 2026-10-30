# ===== src/sysdiag/modules/system_info.py =====
from __future__ import annotations

import platform

from ..models import Check, Config, Status
from ..powershell import PowerShellError, run_ps

NAME = "System Info"

_OS_SCRIPT = (
    "$os = Get-CimInstance Win32_OperatingSystem; "
    "[pscustomobject]@{Caption=$os.Caption; Version=$os.Version; Build=$os.BuildNumber; "
    "LastBoot=$os.LastBootUpTime.ToString('o'); "
    "TotalMemKB=[int64]$os.TotalVisibleMemorySize; FreeMemKB=[int64]$os.FreePhysicalMemory} "
    "| ConvertTo-Json -Compress"
)


def run(config: Config) -> list[Check]:
    checks = [
        Check(
            "Equipo",
            Status.OK,
            platform.node(),
            {"arquitectura": platform.machine(), "python": platform.python_version()},
        )
    ]
    try:
        info = run_ps(_OS_SCRIPT)
    except PowerShellError as exc:
        checks.append(Check("Windows", Status.SKIP, f"No se pudo consultar vía PowerShell: {exc}"))
        return checks

    checks.append(
        Check(
            "Windows",
            Status.OK,
            f"{info['Caption']} (build {info['Build']})",
            {"version": info["Version"], "ultimo_arranque": info["LastBoot"]},
        )
    )
    total, free = info["TotalMemKB"], info["FreeMemKB"]
    free_pct = free / total * 100 if total else 0.0
    checks.append(
        Check(
            "Memoria RAM",
            Status.OK if free_pct >= 10 else Status.WARN,
            f"{free_pct:.0f}% libre de {total / 1024 / 1024:.1f} GB",
            {"total_kb": total, "libre_kb": free},
        )
    )
    return checks
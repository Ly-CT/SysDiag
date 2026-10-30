# ===== src/sysdiag/models.py =====
"""Modelos de datos compartidos por todos los módulos."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


class Status(str, Enum):
    # El orden define la severidad (de menor a mayor).
    SKIP = "SKIP"    # no aplicable o sin permisos
    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"    # el equipo tiene un problema
    ERROR = "ERROR"  # la herramienta no pudo comprobarlo

    @property
    def severity(self) -> int:
        return list(Status).index(self)


def worst(statuses: Iterable[Status]) -> Status:
    return max(statuses, key=lambda s: s.severity, default=Status.SKIP)


@dataclass
class Check:
    name: str
    status: Status
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class ModuleResult:
    module: str
    checks: list[Check] = field(default_factory=list)
    duration_s: float = 0.0

    @property
    def status(self) -> Status:
        return worst(c.status for c in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "status": self.status.value,
            "duration_s": self.duration_s,
            "checks": [c.to_dict() for c in self.checks],
        }


@dataclass
class Config:
    dns_hosts: list[str] = field(default_factory=lambda: ["example.com", "microsoft.com"])
    port_targets: list[tuple[str, int]] = field(default_factory=lambda: [("example.com", 443)])
    disk_warn_pct: float = 20.0  # % libre por debajo del cual hay advertencia
    disk_fail_pct: float = 10.0  # % libre por debajo del cual hay fallo
    timeout_s: float = 3.0

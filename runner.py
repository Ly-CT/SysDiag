# ===== src/sysdiag/runner.py =====
from __future__ import annotations

import time

from .models import Check, Config, ModuleResult, Status
from .modules import MODULES


def run_modules(selected: list[str], config: Config) -> list[ModuleResult]:
    """Ejecuta los módulos pedidos; un fallo en uno nunca detiene a los demás."""
    results: list[ModuleResult] = []
    for key in selected:
        module = MODULES[key]
        start = time.perf_counter()
        try:
            checks = module.run(config)
        except Exception as exc:  # noqa: BLE001 - frontera de aislamiento deliberada
            checks = [Check("Ejecución del módulo", Status.ERROR, f"{type(exc).__name__}: {exc}")]
        results.append(
            ModuleResult(module.NAME, checks, round(time.perf_counter() - start, 3))
        )
    return results
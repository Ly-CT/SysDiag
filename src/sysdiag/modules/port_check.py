# ===== src/sysdiag/modules/port_check.py =====
from __future__ import annotations

import socket
import time

from ..models import Check, Config, Status

NAME = "Port Check"


def _check(host: str, port: int, timeout: float) -> Check:
    name = f"TCP {host}:{port}"
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            ms = (time.perf_counter() - start) * 1000
        return Check(name, Status.OK, f"Puerto abierto ({ms:.0f} ms)", {"ms": round(ms)})
    except TimeoutError:
        return Check(name, Status.FAIL, f"Tiempo agotado ({timeout:g}s): posible bloqueo por firewall")
    except ConnectionRefusedError:
        return Check(name, Status.FAIL, "Conexión rechazada: el host responde pero no hay servicio escuchando")
    except socket.gaierror as exc:
        return Check(name, Status.FAIL, f"No se pudo resolver el nombre: {exc.strerror or exc}")
    except OSError as exc:
        return Check(name, Status.FAIL, f"Error de red: {exc}")


def run(config: Config) -> list[Check]:
    return [_check(host, port, config.timeout_s) for host, port in config.port_targets]

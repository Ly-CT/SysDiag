# ===== src/sysdiag/modules/dns_check.py =====
from __future__ import annotations

import socket
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout

from ..models import Check, Config, Status

NAME = "DNS Check"


def _resolve(host: str) -> tuple[list[str], float]:
    start = time.perf_counter()
    infos = socket.getaddrinfo(host, None)
    return sorted({i[4][0] for i in infos}), (time.perf_counter() - start) * 1000


def run(config: Config) -> list[Check]:
    # getaddrinfo no admite timeout: se ejecuta en hilos y se espera con límite.
    pool = ThreadPoolExecutor(max_workers=max(1, len(config.dns_hosts)))
    futures = {h: pool.submit(_resolve, h) for h in config.dns_hosts}
    checks: list[Check] = []
    try:
        for host, fut in futures.items():
            name = f"Resolución de {host}"
            try:
                addrs, ms = fut.result(timeout=config.timeout_s)
            except FutureTimeout:
                checks.append(Check(name, Status.FAIL, f"Sin respuesta en {config.timeout_s:g}s"))
            except socket.gaierror as exc:
                checks.append(Check(name, Status.FAIL, f"No se pudo resolver: {exc.strerror or exc}"))
            else:
                checks.append(
                    Check(
                        name,
                        Status.OK if ms < 1000 else Status.WARN,
                        f"{len(addrs)} dirección(es) en {ms:.0f} ms",
                        {"direcciones": addrs, "ms": round(ms)},
                    )
                )
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    return checks

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
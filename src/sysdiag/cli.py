# ===== src/sysdiag/cli.py =====
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from . import __version__
from .models import Config
from .modules import MODULES
from .report import build_report, write_html, write_json
from .runner import run_modules


def parse_target(text: str) -> tuple[str, int]:
    host, sep, port = text.rpartition(":")
    if not sep or not host or not port.isdigit() or not 1 <= int(port) <= 65535:
        raise argparse.ArgumentTypeError(f"'{text}' no tiene el formato HOST:PUERTO")
    return host, int(port)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sysdiag", description="Diagnóstico básico de equipos Windows")
    p.add_argument(
        "-m", "--modules", nargs="+", choices=list(MODULES), default=list(MODULES),
        metavar="MODULO", help=f"Módulos a ejecutar ({', '.join(MODULES)}). Por defecto: todos",
    )
    p.add_argument("-o", "--output-dir", type=Path, default=Path("reports"))
    p.add_argument("--ports", nargs="+", type=parse_target, metavar="HOST:PUERTO")
    p.add_argument("--dns-hosts", nargs="+", metavar="HOST")
    p.add_argument("--timeout", type=float, default=3.0, help="Segundos de espera por prueba de red")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config(timeout_s=args.timeout)
    if args.dns_hosts:
        config.dns_hosts = args.dns_hosts
    if args.ports:
        config.port_targets = args.ports

    results = run_modules(args.modules, config)
    report = build_report(results)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = args.output_dir / f"sysdiag_{stamp}.html"
    json_path = args.output_dir / f"sysdiag_{stamp}.json"
    write_html(report, html_path)
    write_json(report, json_path)

    for r in results:
        print(f"[{r.status.value:<5}] {r.module}")
    print(f"Estado global: {report['overall_status']}")
    print(f"Reportes: {html_path}\n          {json_path}")
    return {"ERROR": 2, "FAIL": 1}.get(report["overall_status"], 0)
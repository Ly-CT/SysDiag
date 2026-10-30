# ===== src/sysdiag/report/generator.py =====
from __future__ import annotations

import html
import json
import platform
from datetime import datetime
from pathlib import Path
from typing import Any

from .. import __version__
from ..models import ModuleResult, worst

_COLORS = {"OK": "#2e7d32", "WARN": "#ed6c02", "FAIL": "#c62828", "ERROR": "#6a1b9a", "SKIP": "#757575"}

_CSS = """
body{font-family:Segoe UI,Arial,sans-serif;margin:2rem auto;max-width:900px;color:#222;padding:0 1rem}
h1,h2{margin-bottom:.3rem}.meta{color:#666;margin-top:0}
table{width:100%;border-collapse:collapse;margin:.5rem 0 1.5rem}
td,th{border-bottom:1px solid #ddd;padding:.45rem .6rem;text-align:left;vertical-align:top}
.badge{color:#fff;border-radius:4px;padding:2px 8px;font-size:.75rem;font-weight:600}
pre{background:#f5f5f5;padding:.5rem;overflow-x:auto;font-size:.8rem}
"""


def build_report(results: list[ModuleResult], generated_at: datetime | None = None) -> dict[str, Any]:
    generated_at = generated_at or datetime.now().astimezone()
    return {
        "tool": "SYSDIAG",
        "version": __version__,
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "host": platform.node(),
        "overall_status": worst(r.status for r in results).value,
        "modules": [r.to_dict() for r in results],
    }


def write_json(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _badge(status: str) -> str:
    color = _COLORS.get(status, "#757575")
    return f'<span class="badge" style="background:{color}">{html.escape(status)}</span>'


def _row(check: dict[str, Any]) -> str:
    e = html.escape
    details = ""
    if check["details"]:
        raw = json.dumps(check["details"], ensure_ascii=False, indent=2)
        details = f"<details><summary>detalles</summary><pre>{e(raw)}</pre></details>"
    return (
        f"<tr><td>{e(check['name'])}</td><td>{_badge(check['status'])}</td>"
        f"<td>{e(check['message'])}{details}</td></tr>"
    )


def render_html(report: dict[str, Any]) -> str:
    e = html.escape
    sections = []
    for mod in report["modules"]:
        rows = "".join(_row(c) for c in mod["checks"])
        sections.append(
            f"<section><h2>{e(mod['module'])} {_badge(mod['status'])}</h2>"
            f"<table><tr><th>Comprobación</th><th>Estado</th><th>Resultado</th></tr>{rows}</table></section>"
        )
    body = "".join(sections)
    overall = _badge(report["overall_status"])
    meta = f"Equipo: {e(report['host'])} · Generado: {e(report['generated_at'])} · v{e(report['version'])}"
    return (
        '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
        f"<title>SYSDIAG</title><style>{_CSS}</style></head><body>"
        f'<h1>SYSDIAG {overall}</h1><p class="meta">{meta}</p>{body}</body></html>'
    )


def write_html(report: dict[str, Any], path: Path) -> None:
    path.write_text(render_html(report), encoding="utf-8")
# ===== src/sysdiag/report/__init__.py =====
from .generator import build_report, render_html, write_html, write_json

__all__ = ["build_report", "render_html", "write_html", "write_json"]
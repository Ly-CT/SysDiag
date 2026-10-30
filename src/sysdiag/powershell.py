# ===== src/sysdiag/powershell.py =====
"""Ejecución controlada de PowerShell. Los scripts deben terminar en ConvertTo-Json.

Nunca interpolar entradas del usuario dentro de `script`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


class PowerShellError(RuntimeError):
    pass


_PREAMBLE = (
    "$ProgressPreference='SilentlyContinue'; $ErrorActionPreference='Stop'; "
    "[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false; "
)


def run_ps(script: str, timeout: float = 20.0) -> Any:
    """Ejecuta `script` y devuelve su salida JSON ya convertida a objetos Python."""
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if exe is None:
        raise PowerShellError("PowerShell no está disponible en este equipo")
    try:
        proc = subprocess.run(
            [exe, "-NoProfile", "-NonInteractive", "-Command", _PREAMBLE + script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PowerShellError(f"PowerShell excedió el límite de {timeout:g}s") from exc
    if proc.returncode != 0:
        raise PowerShellError(proc.stderr.strip() or f"código de salida {proc.returncode}")
    out = proc.stdout.lstrip("\ufeff").strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise PowerShellError(f"La salida no es JSON válido: {out[:200]}") from exc


def as_list(data: Any) -> list:
    """ConvertTo-Json devuelve objeto si hay 1 elemento, lista si hay varios, nada si 0."""
    if data is None:
        return []
    return data if isinstance(data, list) else [data]
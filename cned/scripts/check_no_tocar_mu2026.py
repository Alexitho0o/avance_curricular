"""Chequea que archivos protegidos MU2026/PES_READY no tengan cambios locales."""

from __future__ import annotations

import subprocess
from pathlib import Path


PROTECTED_FILES = [
    "qa_checks.py",
    "scripts/auditoria_maestra.py",
    "scripts/run_oficial.sh",
    "scripts/validate_oficial.sh",
    "scripts/run_mu_operativo.sh",
    "scripts/mu2026_complemento_95_codcli.py",
    "scripts/auditoria_mu2026_punto0_complemento95.py",
    "scripts/generar_excel_trazabilidad_4165.py",
    "scripts/generar_reporte_95_codcli_excel.py",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def changed(paths: list[str], cached: bool = False) -> list[str]:
    cmd = ["git", "diff", "--name-only"]
    if cached:
        cmd.append("--cached")
    cmd.extend(["--", *paths])
    result = subprocess.run(cmd, cwd=repo_root(), check=True, capture_output=True, text=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    unstaged = changed(PROTECTED_FILES, cached=False)
    staged = changed(PROTECTED_FILES, cached=True)
    touched = sorted(set(unstaged + staged))
    if touched:
        print("ALERTA: se detectaron modificaciones en archivos protegidos de MU2026.")
        for path in touched:
            print(f"- {path}")
        return 1
    print("OK: no se detectaron modificaciones en archivos protegidos de MU2026.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

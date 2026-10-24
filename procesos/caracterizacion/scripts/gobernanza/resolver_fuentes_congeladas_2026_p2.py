#!/usr/bin/env python3
"""
H044 — Resolución gobernada de fuentes congeladas para Caracterización 2026 P2.

Este módulo NO ejecuta el pipeline de caracterización ni reemplaza el
mecanismo general de selección automática desde Downloads usado por otros
años/períodos. Su único propósito es, exclusivamente para 2026 P2, resolver
la cuaterna congelada (matrícula, tokens, resultados y promedios académicos) declarada en:

    docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json

validar su integridad (ubicación, existencia, tipo, nombre, SHA-256 y
consistencia interna de survey_id) y, si todo es correcto, emitir las
variables de entorno que `caracterizacion.py` ya soporta de forma nativa con
prioridad sobre Downloads: RUTA_MATRICULA, RUTA_INSCRITOS, RUTA_RESULTADOS y RUTA_PROMEDIOS.

Precedencia gobernada (documentada en docs/gobernanza/H044_FUENTES_P2_DETERMINISTICAS.md):
  1. Ruta explícita ya presente en el entorno (RUTA_MATRICULA / RUTA_INSCRITOS /
     RUTA_RESULTADOS establecida por quien invoca el lanzador) prevalece
     rol por rol y NO es sobrescrita por este resolutor.
  2. Fuente congelada gobernada para 2026 P2 (este módulo) para cualquier rol
     que no tenga una ruta explícita ya establecida.
  3. Selección automática histórica desde Downloads: nunca ocurre para 2026 P2
     mientras el manifiesto exista, incluso si algún rol quedó en override
     manual con una ruta inválida (ese caso lo bloquea `caracterizacion.py`
     directamente, sin caer a Downloads).

Si cualquier control de integridad falla, este módulo levanta
`FuentesCongeladasError` y no debe permitirse continuar con el pipeline.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROLES_ESPERADOS = (
    "matricula_oficial",
    "inscritos_limesurvey",
    "resultados_limesurvey",
    "promedios_academicos_auxiliar",
)

ROL_A_VARIABLE_ENTORNO = {
    "matricula_oficial": "RUTA_MATRICULA",
    "inscritos_limesurvey": "RUTA_INSCRITOS",
    "resultados_limesurvey": "RUTA_RESULTADOS",
    "promedios_academicos_auxiliar": "RUTA_PROMEDIOS",
}

ROL_A_ETIQUETA_TRAZA = {
    "matricula_oficial": "Matrícula",
    "inscritos_limesurvey": "Tokens",
    "resultados_limesurvey": "Resultados",
    "promedios_academicos_auxiliar": "Promedios académicos",
}

RUTA_CONGELADA_PREFIJO = Path(".local") / "fuentes_congeladas"


class FuentesCongeladasError(Exception):
    """Cualquier falla de gobernanza sobre las fuentes congeladas 2026 P2."""


@dataclass
class ResolucionFuentes:
    manifiesto_path: Path
    version_fuentes: str
    survey_id: str
    rutas_por_rol: dict[str, Path]
    exportar_por_rol: dict[str, bool]
    trace_lines: list[str] = field(default_factory=list)

    def lineas_export(self) -> list[str]:
        lineas = []
        for rol, var in ROL_A_VARIABLE_ENTORNO.items():
            if self.exportar_por_rol.get(rol):
                ruta = self.rutas_por_rol[rol]
                lineas.append(f'export {var}="{ruta}"')
        return lineas


def _sha256_archivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cargar_manifiesto(manifiesto_path: Path) -> dict:
    if not manifiesto_path.exists():
        raise FuentesCongeladasError(
            f"Manifiesto no encontrado: {manifiesto_path}"
        )
    try:
        with manifiesto_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise FuentesCongeladasError(
            f"Manifiesto ilegible o con JSON inválido: {manifiesto_path} ({exc})"
        ) from exc
    if not isinstance(data, dict):
        raise FuentesCongeladasError(
            f"Manifiesto con formato inesperado (se esperaba un objeto JSON): {manifiesto_path}"
        )
    return data


def _validar_ruta_dentro_de_zona_restringida(path_absoluto: Path, repo_root: Path) -> Path:
    zona_restringida = (repo_root / RUTA_CONGELADA_PREFIJO).resolve()
    try:
        resuelto = path_absoluto.resolve(strict=False)
    except OSError as exc:
        raise FuentesCongeladasError(
            f"No fue posible resolver la ruta del archivo: {path_absoluto} ({exc})"
        ) from exc
    try:
        resuelto.relative_to(zona_restringida)
    except ValueError:
        raise FuentesCongeladasError(
            "La ruta resuelta escapa de la zona restringida "
            f".local/fuentes_congeladas/: {resuelto}"
        ) from None
    return resuelto


def resolver_fuentes_congeladas(
    manifiesto_path: Path,
    repo_root: Path,
    anio_esperado: int,
    periodo_esperado: int,
    *,
    entorno: dict[str, str] | None = None,
) -> ResolucionFuentes:
    """Valida el manifiesto y la terna congelada; nunca cae a Downloads."""
    entorno = os.environ if entorno is None else entorno
    manifiesto = cargar_manifiesto(manifiesto_path)

    anio_manifiesto = manifiesto.get("anio")
    periodo_manifiesto = manifiesto.get("periodo")
    if anio_manifiesto != anio_esperado:
        raise FuentesCongeladasError(
            f"Año del manifiesto ({anio_manifiesto!r}) no coincide con el año "
            f"solicitado ({anio_esperado!r})."
        )
    if periodo_manifiesto != periodo_esperado:
        raise FuentesCongeladasError(
            f"Periodo del manifiesto ({periodo_manifiesto!r}) no coincide con el "
            f"periodo solicitado ({periodo_esperado!r})."
        )

    estado = manifiesto.get("estado")
    if estado != "CONGELADO":
        raise FuentesCongeladasError(
            f"El manifiesto no está en estado CONGELADO (estado={estado!r})."
        )

    survey_id_manifiesto = str(manifiesto.get("survey_id") or "").strip()
    if not survey_id_manifiesto:
        raise FuentesCongeladasError("El manifiesto no declara survey_id.")

    version_fuentes = str(manifiesto.get("version_fuentes") or "").strip()
    if not version_fuentes:
        raise FuentesCongeladasError("El manifiesto no declara version_fuentes.")

    archivos = manifiesto.get("archivos")
    if not isinstance(archivos, list):
        raise FuentesCongeladasError("El manifiesto no declara una lista 'archivos'.")

    archivos_por_rol = {}
    for entrada in archivos:
        if not isinstance(entrada, dict):
            raise FuentesCongeladasError("Entrada de 'archivos' con formato inesperado.")
        rol = entrada.get("rol")
        if rol in archivos_por_rol:
            raise FuentesCongeladasError(f"Rol duplicado en el manifiesto: {rol!r}.")
        archivos_por_rol[rol] = entrada

    faltantes = [rol for rol in ROLES_ESPERADOS if rol not in archivos_por_rol]
    if faltantes:
        raise FuentesCongeladasError(
            f"El manifiesto no declara los roles requeridos: {', '.join(faltantes)}."
        )

    rutas_por_rol: dict[str, Path] = {}
    for rol in ROLES_ESPERADOS:
        entrada = archivos_por_rol[rol]
        nombre_declarado = entrada.get("nombre")
        ruta_relativa = entrada.get("ruta_relativa_restringida")
        sha256_esperado = entrada.get("sha256")
        if not nombre_declarado or not ruta_relativa or not sha256_esperado:
            raise FuentesCongeladasError(
                f"Entrada incompleta para el rol {rol!r} (falta nombre, ruta o sha256)."
            )

        ruta_relativa_str = str(ruta_relativa)
        if not ruta_relativa_str.replace("\\", "/").startswith(
            str(RUTA_CONGELADA_PREFIJO).replace("\\", "/")
        ):
            raise FuentesCongeladasError(
                f"[{nombre_declarado}] La ruta declarada no pertenece a "
                f".local/fuentes_congeladas/: {ruta_relativa_str}"
            )

        path_absoluto = repo_root / ruta_relativa_str
        path_validado = _validar_ruta_dentro_de_zona_restringida(path_absoluto, repo_root)

        if not path_validado.exists():
            raise FuentesCongeladasError(
                f"[{nombre_declarado}] Archivo congelado no existe: {path_validado}"
            )
        if path_validado.is_symlink():
            raise FuentesCongeladasError(
                f"[{nombre_declarado}] La fuente congelada no puede ser un enlace simbólico: {path_validado}"
            )
        if not path_validado.is_file():
            raise FuentesCongeladasError(
                f"[{nombre_declarado}] La ruta no es un archivo regular: {path_validado}"
            )
        if path_validado.name != nombre_declarado:
            raise FuentesCongeladasError(
                f"[{nombre_declarado}] El nombre real del archivo ({path_validado.name}) "
                f"no coincide con el nombre declarado en el manifiesto."
            )

        sha256_real = _sha256_archivo(path_validado)
        if sha256_real != sha256_esperado:
            raise FuentesCongeladasError(
                f"[{nombre_declarado}] SHA-256 no coincide con el manifiesto "
                f"(esperado={sha256_esperado}, real={sha256_real})."
            )

        if rol in ("inscritos_limesurvey", "resultados_limesurvey"):
            survey_id_archivo = str(entrada.get("survey_id") or "").strip()
            if not survey_id_archivo or survey_id_archivo != survey_id_manifiesto:
                raise FuentesCongeladasError(
                    f"[{nombre_declarado}] survey_id del archivo ({survey_id_archivo!r}) "
                    f"es inconsistente con el survey_id del manifiesto ({survey_id_manifiesto!r})."
                )

        rutas_por_rol[rol] = path_validado

    exportar_por_rol: dict[str, bool] = {}
    trace_lines = [
        "[H044][FUENTES] Modo: FUENTES_CONGELADAS",
        f"[H044][FUENTES] Manifiesto: {manifiesto_path}",
        f"[H044][FUENTES] Versión: {version_fuentes}",
    ]
    for rol in ROLES_ESPERADOS:
        var = ROL_A_VARIABLE_ENTORNO[rol]
        etiqueta = ROL_A_ETIQUETA_TRAZA[rol]
        override_manual = bool(str(entorno.get(var, "")).strip())
        exportar_por_rol[rol] = not override_manual
        if override_manual:
            trace_lines.append(
                f"[H044][FUENTES] {etiqueta}: OVERRIDE_MANUAL ({var} ya establecida "
                "externamente; prevalece sobre la fuente congelada)"
            )
        else:
            trace_lines.append(f"[H044][FUENTES] {etiqueta}: {rutas_por_rol[rol].name}")

    trace_lines.append(f"[H044][FUENTES] Survey ID: {survey_id_manifiesto}")
    trace_lines.append("[H044][FUENTES] SHA-256: OK")
    trace_lines.append("[H044][FUENTES] Downloads utilizados: NO")

    return ResolucionFuentes(
        manifiesto_path=manifiesto_path,
        version_fuentes=version_fuentes,
        survey_id=survey_id_manifiesto,
        rutas_por_rol=rutas_por_rol,
        exportar_por_rol=exportar_por_rol,
        trace_lines=trace_lines,
    )


def _resumen_kv(resolucion: ResolucionFuentes) -> list[str]:
    return [
        "MODO_FUENTES=CONGELADAS",
        f"VERSION_FUENTES={resolucion.version_fuentes}",
        f"SURVEY_ID={resolucion.survey_id}",
        "HASHES=OK",
        "DOWNLOADS=NO",
    ]


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anio", type=int, default=2026)
    parser.add_argument("--periodo", type=int, default=2)
    parser.add_argument(
        "--manifiesto",
        type=str,
        default=None,
        help="Ruta al manifiesto (por defecto: docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    manifiesto_path = (
        Path(args.manifiesto)
        if args.manifiesto
        else repo_root / "docs" / "gobernanza" / "FUENTES_CONGELADAS_2026_P2.json"
    )

    try:
        resolucion = resolver_fuentes_congeladas(
            manifiesto_path, repo_root, args.anio, args.periodo
        )
    except FuentesCongeladasError as exc:
        print(f"[H044][FUENTES][BLOQUEO] {exc}", file=sys.stdout, flush=True)
        return 3

    for linea in resolucion.trace_lines:
        print(linea, flush=True)
    for linea in _resumen_kv(resolucion):
        print(linea, flush=True)
    for linea in resolucion.lineas_export():
        print(linea, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

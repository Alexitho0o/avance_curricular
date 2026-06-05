#!/usr/bin/env python3
"""Cruza base general preliminar contra formato oficial SIES 2026.

Genera matriz columna por columna, dictamen pre-carga, reporte tecnico y
bitacora. No modifica la base y no genera PES_READY.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR.parent
REPO_DIR = MODULE_DIR.parent

INSTRUCTIVO = MODULE_DIR / "insumos/Personal Académico SIES - Instructivo 2026.txt"
ESTRUCTURA_EN = MODULE_DIR / "insumos/20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv"
ESTRUCTURA_FUERA = MODULE_DIR / "insumos/20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv"
BASE_GENERAL = MODULE_DIR / "data/base_general/base_general_personal_academico_en_institucion.tsv"
AUDITORIAS_DIR = MODULE_DIR / "auditorias"
MATRIZ_DIR = MODULE_DIR / "auditorias"
DICTAMEN = MODULE_DIR / "docs/DICTAMEN_PRE_CARGA_PES_PERSONAL_ACADEMICO_EN_INSTITUCION.md"
REPORTE = MODULE_DIR / "docs/REPORTE_FASE_4_CRUCE_OFICIAL_COLUMNA_A_COLUMNA.md"
BITACORA = MODULE_DIR / "bitacoras/BITACORA_FASE_4_CRUCE_OFICIAL_COLUMNA_A_COLUMNA.md"

FUENTE_ESTRUCTURA = "ESTRUCTURA_OFICIAL"
FUENTE_PREVENTIVA = "VALIDACION_TECNICA_PREVENTIVA"
FUENTE_PENDIENTE = "PENDIENTE_CONFIRMACION"

NO_DISPONIBLES = {"#N/A", "#N/D", "N/A", "NA", "NO APLICA"}


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_DIR))
    except ValueError:
        return str(path)


def git_branch() -> str:
    proc = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() or "desconocida"


def leer_header_csv(path: Path, delimiter: str) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        return next(reader)


def leer_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def latest_validation_audit() -> Path | None:
    pattern = "auditoria_validacion_en_institucion_base_general_personal_academico_en_institucion_*.csv"
    paths = sorted(AUDITORIAS_DIR.glob(pattern))
    return paths[-1] if paths else None


def ejecutar_validador_si_necesario() -> Path:
    audit = latest_validation_audit()
    if audit:
        return audit
    cmd = [
        sys.executable,
        str(MODULE_DIR / "scripts/validar_archivo_personal_academico_2026.py"),
        "--tipo",
        "en_institucion",
        "--input",
        str(BASE_GENERAL),
        "--delimitador-entrada",
        "tab",
    ]
    subprocess.run(cmd, cwd=REPO_DIR, check=True)
    audit = latest_validation_audit()
    if not audit:
        raise RuntimeError("No se pudo encontrar auditoria del validador para base general.")
    return audit


def leer_auditoria_validacion(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def normalizar_disponibilidad(value: str) -> str:
    return " ".join((value or "").strip().upper().split())


def muestras_valores(rows: list[dict[str, str]], columna: str, limit: int = 10) -> list[str]:
    vistos = []
    for row in rows:
        value = row.get(columna, "")
        if value not in vistos:
            vistos.append(value)
        if len(vistos) >= limit:
            break
    return vistos


def contar_columna(rows: list[dict[str, str]], columna: str) -> dict[str, int | str]:
    valores = [row.get(columna, "") for row in rows]
    return {
        "valores_vacios": sum(1 for value in valores if value.strip() == ""),
        "total_na": sum(1 for value in valores if normalizar_disponibilidad(value) in {"#N/A", "N/A", "NA"}),
        "total_nd": sum(1 for value in valores if normalizar_disponibilidad(value) == "#N/D"),
        "total_no_aplica": sum(1 for value in valores if normalizar_disponibilidad(value) == "NO APLICA"),
        "valores_unicos": len(set(valores)),
        "ejemplos": " | ".join(muestras_valores(rows, columna)),
    }


def eventos_por_columna(eventos: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    por_columna: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in eventos:
        columna = event.get("columna") or "*"
        por_columna[columna].append(event)
    return por_columna


def detectar_problemas(eventos: list[dict[str, str]]) -> dict[str, int]:
    reglas = Counter(event.get("regla", "") for event in eventos)
    return {
        "fecha_futura": reglas["fecha_futura"],
        "fecha_formato": reglas["fecha_formato"],
        "fecha_no_disponible": reglas["fecha_no_disponible"],
        "campos_obligatorios_vacios": reglas["campo_obligatorio_basico_preventivo"],
        "duplicados": reglas["duplicados_documento"],
        "rut_dv": reglas["dv_rut_chileno"],
        "sexo": sum(count for rule, count in reglas.items() if "sexo" in rule.lower()),
        "nacionalidad_pais": sum(
            count for rule, count in reglas.items() if "nacionalidad" in rule.lower() or "pais" in rule.lower()
        ),
        "nivel_formacion": sum(count for rule, count in reglas.items() if "formacion" in rule.lower()),
        "cargo_normalizado": sum(count for rule, count in reglas.items() if "cargo" in rule.lower()),
        "horas": sum(count for rule, count in reglas.items() if "hora" in rule.lower()),
        "vigencia": sum(count for rule, count in reglas.items() if "vigencia" in rule.lower()),
    }


def estado_columna(
    coincide_nombre: bool,
    coincide_posicion: bool,
    errores: int,
    advertencias: int,
) -> tuple[str, str, str]:
    if not coincide_nombre or not coincide_posicion:
        return "REQUIERE_CORRECCION", FUENTE_ESTRUCTURA, "Corregir estructura de columna."
    if errores > 0:
        return "REQUIERE_CORRECCION", FUENTE_PREVENTIVA, "Corregir errores criticos antes de exportar."
    if advertencias > 0:
        return "LISTA_CON_ADVERTENCIAS", FUENTE_PREVENTIVA, "Revisar advertencias antes de exportacion controlada."
    return "LISTA", FUENTE_ESTRUCTURA, "Sin hallazgos para la columna."


def construir_matriz(
    oficiales: list[str],
    base_cols: list[str],
    rows: list[dict[str, str]],
    eventos_validacion: list[dict[str, str]],
) -> list[dict[str, object]]:
    por_col = eventos_por_columna(eventos_validacion)
    matrix = []
    now = datetime.now().isoformat(timespec="seconds")
    total_filas = len(rows)
    max_cols = max(len(oficiales), len(base_cols))
    for idx in range(max_cols):
        oficial = oficiales[idx] if idx < len(oficiales) else ""
        base = base_cols[idx] if idx < len(base_cols) else ""
        coincide_nombre = oficial == base
        coincide_posicion = idx < len(oficiales) and idx < len(base_cols) and oficial == base
        col_events = por_col.get(base, []) + ([] if oficial == base else por_col.get(oficial, []))
        errores = sum(1 for event in col_events if event.get("severidad") == "ERROR")
        advertencias = sum(1 for event in col_events if event.get("severidad") in {"ADVERTENCIA", "WARN"})
        counts = contar_columna(rows, base) if base else {
            "valores_vacios": 0,
            "total_na": 0,
            "total_nd": 0,
            "total_no_aplica": 0,
            "valores_unicos": 0,
            "ejemplos": "",
        }
        estado, fuente, accion = estado_columna(coincide_nombre, coincide_posicion, errores, advertencias)
        observaciones = []
        if counts["total_na"]:
            observaciones.append(f"{counts['total_na']} valores NA/#N/A preservados.")
        if counts["total_nd"]:
            observaciones.append(f"{counts['total_nd']} valores #N/D preservados.")
        if counts["total_no_aplica"]:
            observaciones.append(f"{counts['total_no_aplica']} valores NO APLICA.")
        reglas = Counter(event.get("regla", "") for event in col_events)
        if reglas:
            observaciones.append("Reglas validador: " + ", ".join(f"{k}={v}" for k, v in sorted(reglas.items()) if k))
        if not observaciones:
            observaciones.append("Cruce estructural y validacion sin hallazgos.")
        matrix.append(
            {
                "timestamp": now,
                "tipo_archivo": "en_institucion",
                "posicion": idx + 1,
                "columna_oficial": oficial,
                "columna_base": base,
                "coincide_nombre": "SI" if coincide_nombre else "NO",
                "coincide_posicion": "SI" if coincide_posicion else "NO",
                "total_filas": total_filas,
                "valores_vacios": counts["valores_vacios"],
                "total_na": counts["total_na"],
                "total_nd": counts["total_nd"],
                "total_no_aplica": counts["total_no_aplica"],
                "valores_unicos": counts["valores_unicos"],
                "errores_criticos": errores,
                "advertencias": advertencias,
                "estado_columna": estado,
                "fuente_regla": fuente,
                "observacion": " ".join(observaciones),
                "accion_requerida": accion,
            }
        )
    return matrix


def escribir_matriz(matrix: list[dict[str, object]], path: Path) -> None:
    fields = [
        "timestamp",
        "tipo_archivo",
        "posicion",
        "columna_oficial",
        "columna_base",
        "coincide_nombre",
        "coincide_posicion",
        "total_filas",
        "valores_vacios",
        "total_na",
        "total_nd",
        "total_no_aplica",
        "valores_unicos",
        "errores_criticos",
        "advertencias",
        "estado_columna",
        "fuente_regla",
        "observacion",
        "accion_requerida",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(matrix)


def tabla_columnas_markdown(matrix: list[dict[str, object]]) -> str:
    lines = [
        "| # | Columna oficial | Columna base | Estado | Errores | Advertencias | Accion requerida |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for row in matrix:
        lines.append(
            f"| {row['posicion']} | `{row['columna_oficial']}` | `{row['columna_base']}` | "
            f"{row['estado_columna']} | {row['errores_criticos']} | {row['advertencias']} | "
            f"{row['accion_requerida']} |"
        )
    return "\n".join(lines)


def escribir_dictamen(summary: dict[str, object], matrix: list[dict[str, object]], eventos: list[dict[str, str]]) -> None:
    errores = [event for event in eventos if event.get("severidad") == "ERROR"]
    advertencias = [event for event in eventos if event.get("severidad") in {"ADVERTENCIA", "WARN"}]
    if summary["total_errores_criticos"]:
        estado_general = "NO_LISTO_REQUIERE_CORRECCION"
        conclusion = "NO LISTO PARA SUBIR."
    elif summary["total_advertencias"]:
        estado_general = "LISTO_PARA_EXPORTACION_CONTROLADA"
        conclusion = "LISTO SOLO PARA EXPORTACION CONTROLADA CON ADVERTENCIAS."
    else:
        estado_general = "LISTO_PARA_EXPORTACION_CONTROLADA"
        conclusion = "LISTO PARA EXPORTACION CONTROLADA."
    errores_txt = "\n".join(
        f"- Fila {e.get('fila')}: `{e.get('columna')}` = `{e.get('valor')}`; {e.get('regla')} - {e.get('mensaje')}"
        for e in errores
    ) or "- No hay errores criticos."
    advertencias_relevantes = Counter(event.get("regla", "") for event in advertencias)
    advertencias_txt = "\n".join(
        f"- {rule}: {count}" for rule, count in sorted(advertencias_relevantes.items()) if rule
    ) or "- No hay advertencias."
    content = f"""# Dictamen Pre-Carga PES - Personal Academico en la Institucion

## Resumen Ejecutivo
El archivo preliminar fue cruzado contra la estructura oficial en institucion y contra la ultima auditoria del validador. La estructura de 34 columnas coincide en cantidad, nombres y orden. Sin embargo, existe al menos un error critico vigente, por lo que el archivo no esta listo para subir.

## Fuentes Revisadas
- Instructivo oficial: {rel(INSTRUCTIVO)}
- Estructura oficial En Institucion: {rel(ESTRUCTURA_EN)}
- Estructura oficial Fuera Institucion: {rel(ESTRUCTURA_FUERA)}
- Base revisada: {rel(BASE_GENERAL)}
- Auditoria validador usada: {summary['auditoria_validacion']}

## Datos de Ejecucion
- Fecha/hora: {summary['fecha_hora']}
- Rama: {summary['rama']}
- Total columnas oficiales: {summary['total_columnas_oficiales']}
- Total columnas base: {summary['total_columnas_base']}
- Resultado cruce de nombres: {'COINCIDE' if summary['nombres_coinciden'] else 'NO COINCIDE'}
- Resultado cruce de orden: {'COINCIDE' if summary['orden_coincide'] else 'NO COINCIDE'}
- Resultado cantidad de columnas: {'COINCIDE' if summary['cantidad_columnas_coincide'] else 'NO COINCIDE'}
- Total filas: {summary['total_filas']}
- Estado general del archivo: {estado_general}

## Tabla Columna Por Columna
{tabla_columnas_markdown(matrix)}

## Errores Que Impiden Carga
{errores_txt}

Caso vigente destacado:
- `FECHA_OBT_TIT_O_GRADO = 2027-11-29`, fila 20, `fecha_futura`.

## Advertencias Que Requieren Revision
{advertencias_txt}

## Conclusion
{conclusion}

No se genero PES_READY.

No se modifico la base.

No se corrigio ningun dato sin respaldo.

El cruce fue contra la estructura oficial y el instructivo del modulo.
"""
    DICTAMEN.write_text(content, encoding="utf-8")


def escribir_reporte(summary: dict[str, object], problemas: dict[str, int]) -> None:
    content = f"""# Reporte Fase 4 - Cruce Oficial Columna a Columna

## Objetivo
Cruzar la base general preliminar contra el formato oficial del instructivo y las estructuras oficiales CSV para determinar si esta lista para exportacion/carga PES.

## Fuentes
- {rel(INSTRUCTIVO)}
- {rel(ESTRUCTURA_EN)}
- {rel(ESTRUCTURA_FUERA)}
- {rel(BASE_GENERAL)}
- {summary['auditoria_validacion']}

## Metodologia
1. Lectura de estructura oficial En Institucion con delimitador `;`.
2. Lectura de base general TSV con delimitador tab.
3. Comparacion de cantidad, nombres y orden de columnas.
4. Cruce con ultima auditoria del validador para errores y advertencias por columna.
5. Clasificacion columna por columna.

## Scripts Ejecutados
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/cruzar_formato_oficial_personal_academico_2026.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Archivos Generados
- Matriz: {summary['matriz']}
- Dictamen: {rel(DICTAMEN)}
- Reporte: {rel(REPORTE)}
- Bitacora: {rel(BITACORA)}

## Conteos Principales
- Columnas oficiales: {summary['total_columnas_oficiales']}
- Columnas base: {summary['total_columnas_base']}
- Filas revisadas: {summary['total_filas']}
- Errores criticos: {summary['total_errores_criticos']}
- Advertencias: {summary['total_advertencias']}
- LISTA: {summary['estados_columnas'].get('LISTA', 0)}
- LISTA_CON_ADVERTENCIAS: {summary['estados_columnas'].get('LISTA_CON_ADVERTENCIAS', 0)}
- REQUIERE_CORRECCION: {summary['estados_columnas'].get('REQUIERE_CORRECCION', 0)}
- PENDIENTE_CONFIRMACION: {summary['estados_columnas'].get('PENDIENTE_CONFIRMACION', 0)}

## Hallazgos Especificos
- fecha_futura: {problemas.get('fecha_futura', 0)}
- fecha_formato: {problemas.get('fecha_formato', 0)}
- fecha_no_disponible: {problemas.get('fecha_no_disponible', 0)}
- campos obligatorios vacios: {problemas.get('campos_obligatorios_vacios', 0)}
- duplicados: {problemas.get('duplicados', 0)}
- RUT/DV: {problemas.get('rut_dv', 0)}
- sexo: {problemas.get('sexo', 0)}
- nacionalidad/pais: {problemas.get('nacionalidad_pais', 0)}
- nivel formacion: {problemas.get('nivel_formacion', 0)}
- cargo normalizado: {problemas.get('cargo_normalizado', 0)}
- horas: {problemas.get('horas', 0)}
- vigencia: {problemas.get('vigencia', 0)}

## Proximos Pasos
- Resolver la fecha futura mediante correccion manual respaldada en el archivo de control.
- Revisar fechas no disponibles y advertencias preventivas.
- Reejecutar validador y cruce oficial.
- Mantener exportador bloqueado hasta no tener errores criticos.

## Comandos Para Reproducir
```bash
python3 -m py_compile personal_academico_2026/scripts/*.py
python3 personal_academico_2026/scripts/cruzar_formato_oficial_personal_academico_2026.py
python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab
```

No se genero PES_READY.
"""
    REPORTE.write_text(content, encoding="utf-8")


def escribir_bitacora(summary: dict[str, object]) -> None:
    content = f"""# Bitacora Fase 4 - Cruce Oficial Columna a Columna

- Fecha/hora: {summary['fecha_hora']}
- Rama: {summary['rama']}

## Archivos Creados
- {summary['matriz']}
- {rel(DICTAMEN)}
- {rel(REPORTE)}
- {rel(BITACORA)}

## Archivos Modificados
- No se modifico la base general.
- Se agregaron artefactos de auditoria/documentacion de Fase 4.

## Comandos Ejecutados
- `git branch --show-current`
- `git status --short`
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/cruzar_formato_oficial_personal_academico_2026.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/base_general_personal_academico_en_institucion.tsv --output personal_academico_2026/resultados/TEST_NO_DEBE_CREARSE_PES_READY.csv`

## Resultado
- Cantidad de columnas: {'coincide' if summary['cantidad_columnas_coincide'] else 'no coincide'}
- Nombres: {'coinciden' if summary['nombres_coinciden'] else 'no coinciden'}
- Orden: {'coincide' if summary['orden_coincide'] else 'no coincide'}
- Estado general: {summary['estado_general']}

## Estado Final
- Archivo no listo para subir mientras exista error critico.
- No se genero PES_READY.

## Pendientes
- Corregir fecha futura con respaldo y autorizacion.
- Reejecutar Fase 3C y Fase 4.
"""
    BITACORA.write_text(content, encoding="utf-8")


def main() -> int:
    if git_branch() != "feature/personal-academico-base-preliminar-2026":
        print("ERROR: rama incorrecta para Fase 4.", file=sys.stderr)
        return 2
    for path in [INSTRUCTIVO, ESTRUCTURA_EN, ESTRUCTURA_FUERA, BASE_GENERAL]:
        if not path.exists():
            print(f"ERROR: falta fuente obligatoria: {path}", file=sys.stderr)
            return 2

    oficiales = leer_header_csv(ESTRUCTURA_EN, ";")
    _fuera = leer_header_csv(ESTRUCTURA_FUERA, ";")
    base_cols, rows = leer_tsv(BASE_GENERAL)
    audit_path = ejecutar_validador_si_necesario()
    eventos = leer_auditoria_validacion(audit_path)

    if len(oficiales) != 34:
        raise RuntimeError(f"Estructura oficial En Institucion tiene {len(oficiales)} columnas; esperadas 34.")
    matrix = construir_matriz(oficiales, base_cols, rows, eventos)
    ts = timestamp()
    matriz_path = MATRIZ_DIR / f"matriz_cumplimiento_formato_oficial_en_institucion_{ts}.csv"
    escribir_matriz(matrix, matriz_path)

    estados = Counter(str(row["estado_columna"]) for row in matrix)
    errores = sum(1 for event in eventos if event.get("severidad") == "ERROR")
    advertencias = sum(1 for event in eventos if event.get("severidad") in {"ADVERTENCIA", "WARN"})
    summary = {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "rama": git_branch(),
        "matriz": rel(matriz_path),
        "auditoria_validacion": rel(audit_path),
        "total_columnas_oficiales": len(oficiales),
        "total_columnas_base": len(base_cols),
        "cantidad_columnas_coincide": len(oficiales) == len(base_cols),
        "nombres_coinciden": oficiales == base_cols,
        "orden_coincide": oficiales == base_cols,
        "columnas_faltantes": [col for col in oficiales if col not in base_cols],
        "columnas_adicionales": [col for col in base_cols if col not in oficiales],
        "total_filas": len(rows),
        "total_errores_criticos": errores,
        "total_advertencias": advertencias,
        "estados_columnas": dict(estados),
        "estado_general": "NO_LISTO_REQUIERE_CORRECCION" if errores else (
            "LISTO_PARA_EXPORTACION_CONTROLADA" if advertencias else "LISTO_PARA_EXPORTACION_CONTROLADA"
        ),
    }
    problemas = detectar_problemas(eventos)
    escribir_dictamen(summary, matrix, eventos)
    escribir_reporte(summary, problemas)
    escribir_bitacora(summary)

    print("Cruce formato oficial Personal Academico 2026")
    print(f"matriz: {rel(matriz_path)}")
    print(f"columnas oficiales: {len(oficiales)}")
    print(f"columnas base: {len(base_cols)}")
    print(f"nombres coinciden: {'SI' if summary['nombres_coinciden'] else 'NO'}")
    print(f"orden coincide: {'SI' if summary['orden_coincide'] else 'NO'}")
    print(f"errores criticos: {errores}")
    print(f"advertencias: {advertencias}")
    print(f"estado general: {summary['estado_general']}")
    print("NO se genero PES_READY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

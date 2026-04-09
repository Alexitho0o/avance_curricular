from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


REPO = Path("/Users/alexi/Documents/GitHub/avance_curricular")
MONOLITO = REPO / "codigo_gobernanza_v2.py"
TZ = ZoneInfo("America/Santiago")

DEFAULT_CARGA = (
    REPO
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
)

CARRERAS_NOMBRE = "5810_Precarga Carreras Avance Curricular 20268.csv"
MATRICULA_NOMBRE = "5809_Precarga Matrícula Avance Curricular 2026.csv"
PROMEDIOS_NOMBRE = "PROMEDIOSDEALUMNOS_7804.xlsx"

CAMPOS_CALCULADOS_MATRICULA = [
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
]

CAMPOS_MODIFICABLES_CARRERAS = {
    "PLAN_ESTUDIOS",
    "TIPO_UNIDAD_MEDIDA",
    "OTRA_UNIDAD_MEDIDA",
    "TOTAL_UNIDADES_MEDIDA",
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
    "VIGENCIA",
}

CAMPOS_MODIFICABLES_MATRICULA = {
    "PLAN_ESTUDIOS",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def normalizar_nombre(nombre: str) -> str:
    return unicodedata.normalize("NFC", nombre).casefold()


def localizar_archivo(carpeta: Path, nombre_esperado: str) -> Path:
    objetivo = normalizar_nombre(nombre_esperado)
    candidatos = [
        p
        for p in carpeta.iterdir()
        if p.is_file() and normalizar_nombre(p.name) == objetivo
    ]

    if len(candidatos) != 1:
        raise RuntimeError(
            f"No fue posible identificar un único archivo para "
            f"{nombre_esperado!r}. Candidatos: {[str(p) for p in candidatos]}"
        )

    return candidatos[0]


def leer_csv_precarga(path: Path) -> tuple[pd.DataFrame, str]:
    errores: list[str] = []

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(
                path,
                sep=";",
                dtype=str,
                encoding=encoding,
                keep_default_na=False,
                na_filter=False,
            )
            return df, encoding
        except UnicodeDecodeError as exc:
            errores.append(f"{encoding}: {exc}")

    raise RuntimeError(
        f"No se pudo leer {path} con las codificaciones permitidas: {errores}"
    )


def cargar_modulo():
    if not MONOLITO.exists():
        raise FileNotFoundError(MONOLITO)

    spec = importlib.util.spec_from_file_location(
        "codigo_gobernanza_v2_reutilizado",
        MONOLITO,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar el módulo: {MONOLITO}")

    modulo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def serie_vacia_como_na(serie: pd.Series) -> pd.Series:
    return serie.replace(r"^\s*$", pd.NA, regex=True)


def construir_matricula_control_desde_precarga(
    modulo,
    matricula_intermedia: pd.DataFrame,
    resumen: pd.DataFrame,
) -> pd.DataFrame:
    salida = matricula_intermedia.copy()

    if not resumen.empty:
        salida = salida.merge(
            resumen,
            on=["RUT_NORM", "CODIGO_UNICO"],
            how="left",
            suffixes=("", "_CALC"),
            validate="many_to_one",
        )

    for campo in CAMPOS_CALCULADOS_MATRICULA:
        calculado = f"{campo}_CALC"

        if calculado not in salida.columns:
            continue

        if campo not in salida.columns:
            salida[campo] = salida[calculado]
        else:
            original = serie_vacia_como_na(salida[campo])
            salida[campo] = original.combine_first(salida[calculado])

    for campo in modulo.MATRICULA_AC_COLUMNS:
        if campo not in salida.columns:
            salida[campo] = pd.NA

    return salida[modulo.MATRICULA_AC_COLUMNS].copy()


def comparar_no_modificables(
    original: pd.DataFrame,
    salida: pd.DataFrame,
    modificables: set[str],
    columnas_oficiales: list[str],
) -> dict[str, object]:
    columnas = [
        c
        for c in columnas_oficiales
        if c not in modificables
        and c in original.columns
        and c in salida.columns
    ]

    diferencias: dict[str, int] = {}

    if len(original) != len(salida):
        return {
            "filas_original": len(original),
            "filas_salida": len(salida),
            "filas_coinciden": False,
            "columnas_comparadas": columnas,
            "diferencias": {"__FILAS__": abs(len(original) - len(salida))},
            "sin_diferencias": False,
        }

    for columna in columnas:
        izquierda = original[columna].fillna("").astype(str)
        derecha = salida[columna].fillna("").astype(str)
        cantidad = int((izquierda != derecha).sum())

        if cantidad:
            diferencias[columna] = cantidad

    return {
        "filas_original": len(original),
        "filas_salida": len(salida),
        "filas_coinciden": True,
        "columnas_comparadas": columnas,
        "diferencias": diferencias,
        "sin_diferencias": not diferencias,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Ejecutor Avance Curricular 2026 basado en precargas oficiales "
            "y funciones existentes de codigo_gobernanza_v2.py."
        )
    )
    parser.add_argument(
        "--carga-congelada",
        default=str(DEFAULT_CARGA),
    )
    parser.add_argument(
        "--anio-referencia",
        type=int,
        default=2025,
    )
    parser.add_argument(
        "--output-dir",
        default=None,
    )
    args = parser.parse_args()

    inicio = datetime.now(TZ)
    stamp = inicio.strftime("%Y%m%d_%H%M%S")

    carga = Path(args.carga_congelada).expanduser().resolve()

    if not carga.exists():
        raise FileNotFoundError(f"No existe carga congelada: {carga}")

    carreras_path = localizar_archivo(carga, CARRERAS_NOMBRE)
    matricula_path = localizar_archivo(carga, MATRICULA_NOMBRE)
    promedios_path = localizar_archivo(carga, PROMEDIOS_NOMBRE)

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        output_dir = (
            REPO
            / "avance_curricular_2026"
            / "10_resultados"
            / "ejecuciones"
            / f"CONTROL_DESDE_PRECARGAS_{stamp}"
        )

    output_dir.mkdir(parents=True, exist_ok=False)

    modulo = cargar_modulo()

    carreras_raw, encoding_carreras = leer_csv_precarga(carreras_path)
    matricula_raw, encoding_matricula = leer_csv_precarga(matricula_path)

    # Se reutiliza el código existente solamente para extraer histórico
    # y equivalencias desde PROMEDIOSDEALUMNOS.
    _, _, historico_raw, equivalencia = modulo.cargar_fuentes(promedios_path)

    if "ANO" not in historico_raw.columns:
        raise RuntimeError("El histórico no contiene la columna ANO.")

    anios = pd.to_numeric(historico_raw["ANO"], errors="coerce")

    if not (anios == args.anio_referencia).any():
        raise RuntimeError(
            f"No existen registros del año de referencia "
            f"{args.anio_referencia} en el histórico."
        )

    # Acumulado solo hasta el cierre de 2025.
    historico_hasta_corte = historico_raw[
        anios.notna() & (anios <= args.anio_referencia)
    ].copy()

    matricula_intermedia = modulo.preparar_matricula_intermedia(
        matricula_raw
    )

    puente, diagnostico_ambiguedad = modulo.construir_puente_equiv(
        equivalencia
    )

    historico_mapeado, revision_sin_mapeo = (
        modulo.mapear_historico_con_equiv(
            historico_hasta_corte,
            puente,
        )
    )

    resumen = modulo.construir_resumen_historico(
        historico_mapeado
    )

    carreras_control = modulo.construir_carreras_control(
        carreras_raw
    )

    matricula_control = construir_matricula_control_desde_precarga(
        modulo,
        matricula_intermedia,
        resumen,
    )

    issues = []
    issues.extend(modulo.validar_carreras(carreras_control))
    issues.extend(
        modulo.validar_matricula_ac(
            matricula_control,
            carreras_control,
        )
    )

    control_carreras_path = (
        output_dir
        / "CARRERAS_AVANCE_CURRICULAR_2026_CONTROL.csv"
    )
    control_matricula_path = (
        output_dir
        / "MATRICULA_AVANCE_CURRICULAR_2026_CONTROL.csv"
    )

    carreras_control.to_csv(
        control_carreras_path,
        index=False,
        encoding="utf-8",
    )

    matricula_control.to_csv(
        control_matricula_path,
        index=False,
        encoding="utf-8",
    )

    diagnostico_ambiguedad.to_csv(
        output_dir / "DIAGNOSTICO_AMBIGUEDAD_EQUIVALENCIAS.csv",
        index=False,
        encoding="utf-8",
    )

    revision_sin_mapeo.to_csv(
        output_dir / "HISTORICO_SIN_MAPEO_CODIGO_UNICO.csv",
        index=False,
        encoding="utf-8",
    )

    resumen.to_csv(
        output_dir / "RESUMEN_HISTORICO_CALCULADO.csv",
        index=False,
        encoding="utf-8",
    )

    preservacion_carreras = comparar_no_modificables(
        carreras_raw,
        carreras_control,
        CAMPOS_MODIFICABLES_CARRERAS,
        list(modulo.CARRERAS_AC_COLUMNS),
    )

    preservacion_matricula = comparar_no_modificables(
        matricula_raw,
        matricula_control,
        CAMPOS_MODIFICABLES_MATRICULA,
        list(modulo.MATRICULA_AC_COLUMNS),
    )

    bloqueos = [
        issue.__dict__
        for issue in issues
        if issue.severity in {"BLOCKER", "ERROR"}
    ]

    reporte = {
        "proceso": "Avance Curricular SIES 2026",
        "anio_referencia": args.anio_referencia,
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": datetime.now(TZ).isoformat(),
        "zona_horaria": "America/Santiago",
        "modo": "SOLO_CONTROL_DESDE_PRECARGAS_OFICIALES",
        "fuentes": {
            "carreras": {
                "ruta": str(carreras_path),
                "sha256": sha256(carreras_path),
                "encoding": encoding_carreras,
                "filas": len(carreras_raw),
                "columnas": len(carreras_raw.columns),
            },
            "matricula": {
                "ruta": str(matricula_path),
                "sha256": sha256(matricula_path),
                "encoding": encoding_matricula,
                "filas": len(matricula_raw),
                "columnas": len(matricula_raw.columns),
            },
            "promedios": {
                "ruta": str(promedios_path),
                "sha256": sha256(promedios_path),
                "filas_historico_total": len(historico_raw),
                "filas_historico_hasta_corte": len(
                    historico_hasta_corte
                ),
            },
            "codigo_reutilizado": {
                "ruta": str(MONOLITO),
                "sha256": sha256(MONOLITO),
            },
        },
        "resultados": {
            "carreras_control": len(carreras_control),
            "matricula_control": len(matricula_control),
            "resumen_historico": len(resumen),
            "historico_mapeado": int(
                historico_mapeado["CODIGO_UNICO"].notna().sum()
            ),
            "historico_sin_mapeo": int(
                historico_mapeado["CODIGO_UNICO"].isna().sum()
            ),
        },
        "preservacion_no_modificables": {
            "carreras": preservacion_carreras,
            "matricula": preservacion_matricula,
        },
        "issues": [issue.__dict__ for issue in issues],
        "bloqueos": bloqueos,
        "pes_generado": False,
        "apto_para_revision_control": (
            preservacion_carreras["sin_diferencias"]
            and preservacion_matricula["sin_diferencias"]
        ),
        "apto_para_pes": False,
        "motivo_no_pes": (
            "Esta ejecución genera exclusivamente archivos de control. "
            "No se permite PES mientras existan bloqueos o pendientes."
        ),
    }

    reporte_path = output_dir / "REPORTE_CONTROL_AVANCE_2026.json"
    reporte_path.write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("AVANCE CURRICULAR 2026 — CONTROL DESDE PRECARGAS")
    print("=" * 72)
    print(f"Salida: {output_dir}")
    print(f"Carreras originales: {len(carreras_raw):,}")
    print(f"Carreras control: {len(carreras_control):,}")
    print(f"Matrícula original: {len(matricula_raw):,}")
    print(f"Matrícula control: {len(matricula_control):,}")
    print(f"Histórico hasta {args.anio_referencia}: {len(historico_hasta_corte):,}")
    print(f"Resumen persona-carrera: {len(resumen):,}")
    print(f"Issues totales: {len(issues):,}")
    print(f"Bloqueos ERROR/BLOCKER: {len(bloqueos):,}")
    print(
        "No modificables Carreras preservados:",
        preservacion_carreras["sin_diferencias"],
    )
    print(
        "No modificables Matrícula preservados:",
        preservacion_matricula["sin_diferencias"],
    )
    print("PES generado: NO")
    print()
    print("REPORTE:")
    print(reporte_path)
    print()
    print("ABRIR SALIDA:")
    print(f'open "{output_dir}"')


if __name__ == "__main__":
    main()

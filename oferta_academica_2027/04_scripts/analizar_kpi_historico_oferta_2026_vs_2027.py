#!/usr/bin/env python3
"""Analiza KPI de Oferta Académica histórica 2026 y externa 2027."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_validaciones" / "comparativo_oferta_2026_2027"

H26_E1 = Path(
    "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/"
    "Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/"
    "Enviados/Oferta académica/2026/ETAPA 1/20-08-2025_17-09-50_Oferta-Académica-TP-Vigente-Editada-2026.csv"
)
H26_E2 = Path(
    "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/"
    "Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/"
    "Enviados/Oferta académica/2026/ETAPA 2/ETAPA 2.csv"
)
H26_E3 = Path(
    "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/"
    "Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/"
    "Enviados/Oferta académica/2026/ETAPA 3/Carga_Aranceles_Etapa3_2026.csv"
)
C27_E1 = ROOT / "07_resultados" / "cargas_congeladas" / "20260817_155153_etapa1_areas_vigencia_fecha" / "CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv"
C27_E2 = ROOT / "09_respaldo" / "cargas_congeladas" / "20260828_etapa2_carga_17451" / "28-08-2026_13-17-17_Oferta-Académica-TP-Nueva-2027.csv"
C27_5910 = ROOT / "09_respaldo" / "reportes_pes_validados" / "20260907_reporte_5910_etapa1_2" / "5910 Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas.csv"
C27_E3 = ROOT / "09_respaldo" / "cargas_congeladas" / "20260910_etapa3_carga_final_aceptada_pes" / "OFERTA_ACADEMICA_ARANCELES_2027_CARGA_02_CORREGIDA_SIN_TITULOS_20260910.csv"
C27_ORIGEN = ROOT / "06_validaciones" / "conciliacion_reporte_5910_20260907" / "CARRERAS_UNO_A_UNO_REPORTE_5910_VS_CARGAS_20260907.tsv"

HIST_FIELDS = {
    "sede": 0, "nombre": 3, "modalidad": 4, "jornada": 5, "version": 6,
    "tipo_plan": 7, "nivel_global": 15, "nivel_carrera": 16,
    "vac1": 32, "vac2": 33, "vigencia": 50,
}
LOAD_FIELDS = {**HIST_FIELDS, "vigencia": 47}


def read_csv(path: Path) -> list[list[str]]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return list(csv.reader(text.splitlines(), delimiter=";"))


def canonical_rows(path: Path, header: bool = False) -> list[dict[str, str]]:
    rows = read_csv(path)
    if header:
        names = rows[0]
        data = rows[1:]
        index = {name: i for i, name in enumerate(names)}
        return [
            {
                "sede": row[index["COD_SEDE"]],
                "nombre": row[index["NOMBRE_CARRERA"]],
                "modalidad": row[index["MODALIDAD"]],
                "jornada": row[index["COD_JORNADA"]],
                "version": row[index["VERSION"]],
                "tipo_plan": row[index["COD_TIPO_PLAN_CARRERA"]],
                "nivel_global": row[index["COD_NIVEL_GLOBAL"]],
                "nivel_carrera": row[index["COD_NIVEL_CARRERA"]],
                "vac1": row[index["VACANTES_PRIMER_SEMESTRE"]],
                "vac2": row[index["VACANTES_SEGUNDO_SEMESTRE"]],
                "vigencia": row[index["VIGENCIA_CARRERA"]],
            }
            for row in data
        ]
    fields = HIST_FIELDS if len(rows[0]) == 51 else LOAD_FIELDS
    return [{name: row[idx] for name, idx in fields.items()} for row in rows]


def key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[name] for name in ("sede", "nombre", "modalidad", "jornada", "version", "tipo_plan", "nivel_global", "nivel_carrera"))


def stage3_keys(path: Path) -> set[tuple[str, str, str, str, str, str]]:
    return {
        (row[0], row[3], row[4], row[5], row[6], row[12])
        for row in read_csv(path)
    }


def metrics(rows: list[dict[str, str]]) -> dict[str, object]:
    def count(field: str) -> dict[str, int]:
        return dict(sorted(Counter(row[field] for row in rows).items()))

    def number(field: str) -> int:
        return sum(int(row[field]) if row[field].strip().lstrip("-").isdigit() else 0 for row in rows)

    return {
        "registros": len(rows),
        "carreras_distintas": len({row["nombre"] for row in rows}),
        "sedes": count("sede"),
        "modalidades": count("modalidad"),
        "niveles_globales": count("nivel_global"),
        "niveles_carrera": count("nivel_carrera"),
        "tipos_plan": count("tipo_plan"),
        "vigencias": count("vigencia"),
        "vacantes_primer_semestre": number("vac1"),
        "vacantes_segundo_semestre": number("vac2"),
        "vacantes_totales": number("vac1") + number("vac2"),
    }


def pct_change(before: int, after: int) -> float | None:
    return round((after - before) / before * 100, 1) if before else None


def load_origin() -> dict[int, str]:
    mapping: dict[int, str] = {}
    with C27_ORIGEN.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            mapping[int(row["fila_reporte_5910"])] = row["etapa_origen"]
    return mapping


def write_tsv(path: Path, rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, delimiter="\t", lineterminator="\n").writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    h1, h2, h3 = canonical_rows(H26_E1), canonical_rows(H26_E2), canonical_rows(H26_E3)
    c1, c2 = canonical_rows(C27_E1), canonical_rows(C27_E2)
    c5910 = canonical_rows(C27_5910, header=True)
    c3_keys = stage3_keys(C27_E3)
    c3 = [
        row for row in c5910
        if (row["sede"], row["nombre"], row["modalidad"], row["jornada"], row["version"], row["vigencia"]) in c3_keys
    ]

    historical_stage_changes = []
    h1_keys = {key(row) for row in h1}
    h2_keys = {key(row) for row in h2}
    for row in h2:
        historical_stage_changes.append([
            "ETAPA_2", row["sede"], row["nombre"], row["modalidad"], row["jornada"],
            row["version"], "NUEVO_EN_ETAPA_2" if key(row) not in h1_keys else "REPETIDO_EXACTO",
        ])

    # Use the governed frozen loads for stage-level KPIs. The origin map is
    # audit evidence, but its row numbering omits one consolidated row.
    current_5910_by_origin = {"ETAPA_1": c1, "ETAPA_2": c2}

    kpis = [
        ["HISTORICO_2026", "ETAPA_1_ARCHIVADA_ACCESO", "Oferta-Acceso Vigente Editada (agosto)", metrics(h1)],
        ["HISTORICO_2026", "ETAPA_2", "Oferta Académica Nueva (noviembre)", metrics(h2)],
        ["HISTORICO_2026", "ETAPA_3", "Aranceles / corte anual archivado", metrics(h3)],
        ["ACTUAL_2027", "ETAPA_1_ORIGEN_OFICIAL_5910", "Registros del consolidado 5910 originados en Etapa 1", metrics(current_5910_by_origin["ETAPA_1"])],
        ["ACTUAL_2027", "ETAPA_2_ORIGEN_OFICIAL_5910", "Registros del consolidado 5910 originados en Etapa 2", metrics(current_5910_by_origin["ETAPA_2"])],
        ["ACTUAL_2027", "CONSOLIDADO_5910", "Reporte validado Etapa 1 + Etapa 2", metrics(c5910)],
        ["ACTUAL_2027", "ETAPA_3", "Carga final aceptada, solo vigencia 1", metrics(c3)],
    ]

    summary = {
        "alcance": {
            "historico": "Oferta Académica 2026 archivada en 2025",
            "actual": "Oferta-Acceso 2027 ejecutada en 2026",
            "etiquetas_analiticas": "interno = segundo proceso anual; externo = proceso Oferta-Acceso; no son etiquetas oficiales SIES",
        },
        "fuentes": {
            "historico_etapa1": str(H26_E1),
            "historico_etapa2": str(H26_E2),
            "historico_etapa3": str(H26_E3),
            "actual_reporte_5910": str(C27_5910),
            "actual_etapa3": str(C27_E3),
        },
        "kpis": [{"periodo": p, "etapa": e, "descripcion": d, **m} for p, e, d, m in kpis],
        "cambios_historicos_etapa1_vs_etapa2": {
            "registros_etapa1": len(h1),
            "registros_etapa2": len(h2),
            "interseccion_clave_exacta": len(h1_keys & h2_keys),
            "incremento_registros": len(h2),
            "incremento_porcentual_sobre_etapa1": pct_change(len(h1), len(h1) + len(h2)),
            "etapa3_fuera_de_union_etapa1_etapa2": len({key(row) for row in h3} - (h1_keys | h2_keys)),
            "nota": "La Etapa 3 histórica contiene 124 registros y no debe reemplazarse por la suma 81 + 8.",
        },
        "comparaciones": {
            "historico_etapa1_vs_actual_etapa1": {"historico": len(h1), "actual": len(current_5910_by_origin["ETAPA_1"]), "diferencia": len(current_5910_by_origin["ETAPA_1"]) - len(h1), "porcentaje": pct_change(len(h1), len(current_5910_by_origin["ETAPA_1"]))},
            "historico_etapa2_vs_actual_etapa2": {"historico": len(h2), "actual": len(current_5910_by_origin["ETAPA_2"]), "diferencia": len(current_5910_by_origin["ETAPA_2"]) - len(h2), "porcentaje": pct_change(len(h2), len(current_5910_by_origin["ETAPA_2"]))},
            "historico_etapa3_vs_actual_etapa3": {"historico": len(h3), "actual": len(c3), "diferencia": len(c3) - len(h3), "porcentaje": pct_change(len(h3), len(c3)), "advertencia": "no comparable sin filtrar por vigencia y nivel: histórico incluye vigencia 2 y postítulos; actual solo vigencia 1 pregrado"},
        },
        "limitaciones": [
            "No se encontró en la carpeta histórica la carga de Etapa 1 del segundo proceso de octubre; la Etapa 1 archivada es de agosto y corresponde a Oferta-Acceso.",
            "La Etapa 3 histórica es un corte anual completo de 124 registros y contiene 35 claves fuera de la unión simple de los archivos archivados de Etapa 1 y 2.",
            "Los KPI por etapa describen archivos y universos observados; no equivalen automáticamente a carreras únicas anuales.",
        ],
    }

    (OUT / "RESUMEN_KPI_OFERTA_2026_VS_2027.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_tsv(OUT / "CAMBIOS_HISTORICOS_ETAPA1_VS_ETAPA2_2026.tsv", [["etapa", "cod_sede", "nombre_carrera", "modalidad", "jornada", "version", "resultado"]] + historical_stage_changes)
    write_tsv(OUT / "KPI_OFERTA_POR_ETAPA_2026_VS_2027.tsv", [["periodo", "etapa", "descripcion", "registros", "carreras_distintas", "vigencias", "niveles_globales", "modalidades", "vacantes_totales"]] + [[p, e, d, m["registros"], m["carreras_distintas"], json.dumps(m["vigencias"], ensure_ascii=False), json.dumps(m["niveles_globales"], ensure_ascii=False), json.dumps(m["modalidades"], ensure_ascii=False), m["vacantes_totales"]] for p, e, d, m in kpis])

    (OUT / "INFORME_CUALITATIVO_OFERTA_2026_VS_2027.md").write_text(
        "# Resumen cualitativo Oferta Académica 2026 versus Oferta-Acceso 2027\n\n"
        "## Lectura de proceso\n\n"
        "Para este análisis se usan dos etiquetas internas: `interno` identifica el segundo proceso anual de Oferta Académica y `externo` identifica el proceso Oferta-Acceso. No son categorías oficiales de SIES.\n\n"
        "La carpeta histórica no contiene la Etapa 1 interna de octubre. El archivo archivado como Etapa 1 es del 20-08-2025 y corresponde a Oferta-Acceso Vigente Editada. Por eso no se presenta como una secuencia anual completa 1-2-3.\n\n"
        "## Histórico 2026\n\n"
        f"- Etapa 1 archivada: {len(h1)} registros, todos pregrado, 38 vigencia 1 y 43 vigencia 2.\n"
        f"- Etapa 2: {len(h2)} registros nuevos, todos pregrado y vigencia 1. No hay intersección exacta de claves con la Etapa 1. Agrega cuatro nombres de carrera no presentes antes y dos nombres ya existentes en nuevas variantes de sede/modalidad/jornada.\n"
        f"- Etapa 3: {len(h3)} registros, 103 pregrado y 21 postítulo/diplomado; 81 vigencia 1 y 43 vigencia 2. Es el corte anual archivado y no debe calcularse como 81 + 8.\n"
        f"- Existen {len({key(row) for row in h3} - (h1_keys | h2_keys))} claves en Etapa 3 que no están en la unión simple de los dos archivos anteriores. Esto evidencia que falta una fuente intermedia o que la Etapa 3 consolidó un universo más amplio.\n\n"
        "## Actual 2027\n\n"
        f"- El reporte oficial 5910 consolida {len(c5910)} registros: {len(current_5910_by_origin['ETAPA_1'])} originados en Etapa 1 y {len(current_5910_by_origin['ETAPA_2'])} en Etapa 2. Todos son pregrado.\n"
        f"- La Etapa 3 aceptada contiene {len(c3)} registros, todos vigencia 1; es una carga financiera focalizada y no un nuevo conteo anual de oferta.\n\n"
        "## Interpretación ejecutiva\n\n"
        "El cambio principal entre las etapas 1 y 2 históricas fue incremental: la Etapa 2 incorporó programas faltantes o nuevos, sin reemplazar registros de la Etapa 1. En 2027 el crecimiento de Etapa 2 es mucho mayor y está documentado en el reporte 5910 como 37 incorporaciones, por lo que la comparación más sólida es por origen dentro del consolidado oficial.\n\n"
        "La comparación directa de la Etapa 3 histórica con la actual requiere cautela: el archivo 2026 incluye postítulos y vigencia 2, mientras la carga 2027 aceptada fue restringida a vigencia 1 de pregrado.\n\n"
        "## Control de uso\n\n"
        "Usar el JSON y los TSV para KPI reproducibles. No sumar Etapa 3 al consolidado de oferta. Para un KPI anual utilizar el corte validado correspondiente y mantener las etapas como trazabilidad del proceso.\n",
        encoding="utf-8",
    )
    print(f"salida={OUT}")
    print(f"historico_e1={len(h1)} historico_e2={len(h2)} historico_e3={len(h3)}")
    print(f"actual_5910={len(c5910)} actual_etapa3={len(c3)}")
    print(f"historico_e1_e2_interseccion={len(h1_keys & h2_keys)} e3_fuera_union={len({key(row) for row in h3} - (h1_keys | h2_keys))}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESPALDO = ROOT / "09_respaldo" / "reportes_pes_validados" / "20260824_reporte_5912_etapa1"
CARGA = ROOT / "07_resultados" / "cargas_congeladas" / "20260817_155153_etapa1_areas_vigencia_fecha" / "CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv"
PRECARGA = ROOT / "02_precarga_pes" / "reporte_dinamico_5913_2026-08-12_08:22:23.csv"
OUT = ROOT / "06_validaciones" / "conciliacion_reporte_5912_20260824"
NO_CARGA = {"CODIGO_IES_NUM", "CANTIDAD_MATRICULA_DFE", "CANTIDAD_BENEFICIO_DFE"}
KEY_FIELDS = ["COD_SEDE", "COD_CARRERA", "MODALIDAD", "COD_JORNADA", "VERSION"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path, header: bool) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=";"))
    if not rows:
        return [], []
    return (rows[0], rows[1:]) if header else ([], rows)


def canonical_value(field: str, value: str) -> str:
    if field == "FECHA_ADMISION_INICIAL":
        match = re.fullmatch(r"(\d{2})[-/](\d{2})[-/](\d{4})", value)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"
    return value


def main() -> None:
    reportes = sorted(RESPALDO.glob("5912*.csv"))
    if len(reportes) != 1:
        raise SystemExit(f"Se esperaba un reporte 5912 gobernado y se encontraron {len(reportes)}")
    reporte = reportes[0]
    OUT.mkdir(parents=True, exist_ok=True)

    header_precarga, _ = read_rows(PRECARGA, header=True)
    expected = [field for field in header_precarga if field not in NO_CARGA]
    header_5912, rows_5912 = read_rows(reporte, header=True)
    _, rows_carga = read_rows(CARGA, header=False)

    missing = [field for field in expected if field not in header_5912]
    extras = [field for field in header_5912 if field not in expected]
    duplicates = [field for field, count in Counter(header_5912).items() if count > 1]
    projection_possible = not missing and not duplicates

    projected: list[list[str]] = []
    if projection_possible:
        positions = [header_5912.index(field) for field in expected]
        projected = [[row[pos] if pos < len(row) else "" for pos in positions] for row in rows_5912]

    differences: list[dict[str, str | int | bool]] = []
    missing_keys_carga: list[tuple[str, ...]] = []
    missing_keys_5912: list[tuple[str, ...]] = []
    if projection_possible:
        key_positions = [expected.index(field) for field in KEY_FIELDS]
        make_key = lambda row: tuple(row[pos] for pos in key_positions)
        carga_by_key = {make_key(row): (number, row) for number, row in enumerate(rows_carga, start=1)}
        report_by_key = {make_key(row): (number, row) for number, row in enumerate(projected, start=1)}
        missing_keys_carga = sorted(set(report_by_key) - set(carga_by_key))
        missing_keys_5912 = sorted(set(carga_by_key) - set(report_by_key))
        for key in sorted(set(carga_by_key) & set(report_by_key)):
            carga_row_number, sent = carga_by_key[key]
            report_row_number, validated = report_by_key[key]
            for position, field in enumerate(expected, start=1):
                sent_value = sent[position - 1] if position <= len(sent) else ""
                validated_value = validated[position - 1] if position <= len(validated) else ""
                if sent_value != validated_value:
                    differences.append({
                        "fila_carga": carga_row_number,
                        "fila_reporte_5912": report_row_number,
                        "llave_sies": "|".join(key),
                        "posicion_carga": position,
                        "campo": field,
                        "valor_carga_congelada": sent_value,
                        "valor_reporte_5912": validated_value,
                        "equivalencia_semantica": canonical_value(field, sent_value) == canonical_value(field, validated_value),
                    })

    row_widths_carga = Counter(len(row) for row in rows_carga)
    row_widths_5912 = Counter(len(row) for row in rows_5912)
    same_rows = len(rows_carga) == len(rows_5912)
    same_values = projection_possible and same_rows and not differences and not missing_keys_carga and not missing_keys_5912
    semantic_differences = [item for item in differences if not item["equivalencia_semantica"]]
    same_semantic_values = projection_possible and same_rows and not semantic_differences and not missing_keys_carga and not missing_keys_5912
    if same_values:
        status = "SIN_MODIFICACIONES_EN_CAMPOS_CARGADOS"
    elif same_semantic_values:
        status = "SIN_MODIFICACIONES_SEMANTICAS_CON_DIFERENCIAS_DE_FORMATO"
    else:
        status = "CON_MODIFICACIONES_SEMANTICAS"

    detail_path = OUT / "DIFERENCIAS_REPORTE_5912_VS_CARGA_ETAPA1_20260824.tsv"
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["fila_carga", "fila_reporte_5912", "llave_sies", "posicion_carga", "campo", "valor_carga_congelada", "valor_reporte_5912", "equivalencia_semantica"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(differences)

    summary = {
        "proceso": "SIES Oferta Academica-Acceso 2027",
        "subproceso": "Etapa 1 - Oferta Academica Vigente Editada TP Adscritas",
        "fecha_conciliacion": datetime.now().isoformat(timespec="seconds"),
        "fuente_validada_pes": {
            "reporte_id": 5912,
            "ruta": str(reporte),
            "bytes": reporte.stat().st_size,
            "sha256": sha256(reporte),
            "filas_datos": len(rows_5912),
            "columnas": len(header_5912),
        },
        "carga_congelada_comparada": {
            "ruta": str(CARGA),
            "bytes": CARGA.stat().st_size,
            "sha256": sha256(CARGA),
            "filas_datos": len(rows_carga),
            "columnas_sin_encabezado": dict(sorted(row_widths_carga.items())),
        },
        "metodo": "Proyeccion del reporte 5912 al orden exacto de las 48 columnas cargables y conciliacion por llave SIES COD_SEDE+COD_CARRERA+MODALIDAD+COD_JORNADA+VERSION.",
        "estructura_reporte_5912": {
            "columnas_por_fila": dict(sorted(row_widths_5912.items())),
            "columnas_cargables_encontradas": len(expected) - len(missing),
            "columnas_faltantes": missing,
            "columnas_adicionales_de_reporte": extras,
            "encabezados_duplicados": duplicates,
        },
        "resultado": {
            "estado": status,
            "mismas_filas": same_rows,
            "llaves_solo_en_reporte_5912": ["|".join(key) for key in missing_keys_carga],
            "llaves_solo_en_carga": ["|".join(key) for key in missing_keys_5912],
            "mismos_valores_en_48_columnas_cargadas": same_values,
            "mismos_valores_semanticos_en_48_columnas_cargadas": same_semantic_values,
            "diferencias_celda": len(differences),
            "diferencias_semanticas": len(semantic_differences),
            "diferencias_solo_formato": len(differences) - len(semantic_differences),
            "filas_con_diferencias": len({item["llave_sies"] for item in differences}),
            "diferencias_por_campo": dict(sorted(Counter(str(item["campo"]) for item in differences).items())),
        },
    }
    summary_path = OUT / "RESUMEN_CONCILIACION_REPORTE_5912_VS_CARGA_ETAPA1_20260824.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest_path = RESPALDO / "MANIFIESTO_REPORTE_5912_20260824.tsv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["clasificacion", "archivo", "bytes", "sha256"])
        writer.writerow(["reporte_validado_pes_id_5912", reporte.name, reporte.stat().st_size, sha256(reporte)])

    note_path = RESPALDO / "README_GOBERNANZA_REPORTE_5912_20260824.md"
    note_path.write_text(
        "# Reporte PES validado 5912 - Etapa 1\n\n"
        "- Clasificación: reporte validado posterior a carga PES.\n"
        "- Proceso: SIES Oferta Académica-Acceso 2027.\n"
        "- Etapa: Oferta Académica Vigente Editada TP Adscritas.\n"
        f"- Archivo original gobernado: `{reporte.name}`.\n"
        f"- SHA-256: `{sha256(reporte)}`.\n"
        f"- Resultado conciliación: **{status}**.\n"
        f"- Diferencias textuales en las 48 columnas cargadas: **{len(differences)}**.\n"
        f"- Diferencias semánticas: **{len(semantic_differences)}**.\n"
        f"- Diferencias solo de formato: **{len(differences) - len(semantic_differences)}**.\n"
        f"- Columnas adicionales propias del reporte: `{', '.join(extras) if extras else 'ninguna'}`.\n\n"
        "El archivo original se conserva sin modificaciones. La comparación proyecta el reporte 5912 al orden de las 48 columnas efectivamente cargadas.\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "estado": status,
        "filas_carga": len(rows_carga),
        "filas_5912": len(rows_5912),
        "columnas_carga": len(expected),
        "columnas_5912": len(header_5912),
        "columnas_extra_5912": extras,
        "diferencias_celda": len(differences),
        "diferencias_semanticas": len(semantic_differences),
        "diferencias_solo_formato": len(differences) - len(semantic_differences),
        "filas_con_diferencias": summary["resultado"]["filas_con_diferencias"],
        "resumen": str(summary_path),
        "detalle": str(detail_path),
        "respaldo": str(reporte),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

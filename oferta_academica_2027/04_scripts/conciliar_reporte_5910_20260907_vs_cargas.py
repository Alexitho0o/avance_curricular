#!/usr/bin/env python3
"""Concilia el reporte 5910 (consolidado Etapa 1 + Etapa 2) contra las dos cargas congeladas.

Universo de comparacion = carga congelada Etapa 1 (103 filas) + carga congelada
Etapa 2 aceptada (37 filas) = 140 programas. Se valida, uno a uno, que el 5910
trae todas las carreras cargadas y que las vacantes (1er y 2do semestre)
coinciden fila a fila y en el total.

Los programas de Etapa 1 ya tienen COD_CARRERA asignado por SIES, por lo que se
concilian por la llave SIES clasica (COD_SEDE+COD_CARRERA+MODALIDAD+COD_JORNADA+
VERSION). Los programas de Etapa 2 son carreras NUEVAS: en la carga congelada
COD_CARRERA viaja vacio porque el codigo aun no existe, y SIES lo asigna recien
al validar (por eso aparece poblado en el 5910). Para esos se concilia por una
llave alternativa estable (COD_SEDE+NOMBRE_CARRERA+MODALIDAD+COD_JORNADA+
DURACION_TOTAL+REGIMEN), verificada empiricamente como unica para las 37 filas.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTE_5910 = ROOT / "09_respaldo" / "reportes_pes_validados" / "20260907_reporte_5910_etapa1_2" / "5910 Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas.csv"
CARGA_ETAPA1 = ROOT / "07_resultados" / "cargas_congeladas" / "20260817_155153_etapa1_areas_vigencia_fecha" / "CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv"
CARGA_ETAPA2 = ROOT / "09_respaldo" / "cargas_congeladas" / "20260828_etapa2_carga_17451" / "28-08-2026_13-17-17_Oferta-Académica-TP-Nueva-2027.csv"
OUT = ROOT / "06_validaciones" / "conciliacion_reporte_5910_20260907"

NO_CARGA = {"CODIGO_IES_NUM"}
KEY_FIELDS_ETAPA1 = ["COD_SEDE", "COD_CARRERA", "MODALIDAD", "COD_JORNADA", "VERSION"]
KEY_FIELDS_ETAPA2 = ["COD_SEDE", "NOMBRE_CARRERA", "MODALIDAD", "COD_JORNADA", "DURACION_TOTAL", "REGIMEN"]
VACANTES_FIELDS = ["VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE"]

# 48 columnas cargables, mismo orden en las tres etapas (ver CONTRATO_CAMPOS_ETAPA1).
COLUMNAS_CARGABLES = [
    "COD_SEDE", "NOMBRE_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD",
    "COD_JORNADA", "VERSION", "COD_TIPO_PLAN_CARRERA", "CARACTERISTICAS_TIPO_PLAN",
    "DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL", "REGIMEN",
    "DURACION_REGIMEN", "NOMBRE_TITULO", "COD_NIVEL_GLOBAL", "COD_NIVEL_CARRERA",
    "ANIO_INICIO", "ACREDITACION", "REQUISITO_INGRESO", "SEMESTRES_RECONOCIDOS",
    "AREA_ACTUAL", "AREA_ADMIN_DERECHO", "AREA_AGRI_SILVI_PESCA_VET",
    "AREA_ARTES_HUMANIDADES", "AREA_CIENCIAS_NAT_MAT_ESTAD",
    "AREA_CS_SOCIAL_PERIODISMO_INFO", "AREA_EDUCACION",
    "AREA_INGE_INDUSTRIA_CONSTRUC", "AREA_SALUD_BIENESTAR", "AREA_SERVICIOS",
    "AREA_TECNO_INFO_COMUNICA", "VACANTES_PRIMER_SEMESTRE",
    "VACANTES_SEGUNDO_SEMESTRE", "FECHA_ADMISION_INICIAL", "ENLACE_INFO_PROGRAMA",
    "LICENCIA_ENS_MEDIA", "NOTAS_ENS_MEDIA", "PROMEDIO_MIN_ENS_MEDIA",
    "RECONOCIMIENTOS_APREN_PREVIOS", "EXPERIENCIA_LABORAL", "MAIL_DIFUSION_CARRERA",
    "FORMATO_VALOR", "VALOR_MATRICULA_ANUAL", "COSTO_TITULACION",
    "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL", "VIGENCIA_CARRERA",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path, header: bool) -> tuple[list[str], list[list[str]], str]:
    for encoding in ("utf-8", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                rows = list(csv.reader(handle, delimiter=";"))
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit(f"No se pudo decodificar {path}")
    if not rows:
        return [], [], encoding
    return (rows[0], rows[1:], encoding) if header else ([], rows, encoding)


def canonical_value(field: str, value: str) -> str:
    if field == "FECHA_ADMISION_INICIAL":
        match = re.fullmatch(r"(\d{2})[-/](\d{2})[-/](\d{4})", value)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"
    return value


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    header_5910, rows_5910, enc_5910 = read_rows(REPORTE_5910, header=True)
    _, rows_carga_e1, enc_e1 = read_rows(CARGA_ETAPA1, header=False)
    _, rows_carga_e2, enc_e2 = read_rows(CARGA_ETAPA2, header=False)

    expected = COLUMNAS_CARGABLES
    missing = [field for field in expected if field not in header_5910]
    extras = [field for field in header_5910 if field not in expected and field not in NO_CARGA]
    duplicates = [field for field, count in Counter(header_5910).items() if count > 1]
    projection_possible = not missing and not duplicates

    projected: list[list[str]] = []
    if projection_possible:
        positions = [header_5910.index(field) for field in expected]
        projected = [[row[pos] if pos < len(row) else "" for pos in positions] for row in rows_5910]

    vac_positions = [expected.index(field) for field in VACANTES_FIELDS]
    key_positions_e1 = [expected.index(field) for field in KEY_FIELDS_ETAPA1]
    key_positions_e2 = [expected.index(field) for field in KEY_FIELDS_ETAPA2]
    key_e1 = lambda row: tuple(row[p] for p in key_positions_e1)
    key_e2 = lambda row: tuple(row[p] for p in key_positions_e2)

    # Etapa 1: COD_CARRERA ya asignado por SIES, se puede conciliar por llave clasica.
    carga_e1_by_key: dict[tuple, tuple[int, list[str]]] = {}
    duplicated_keys_carga_e1: list[tuple] = []
    for numero, row in enumerate(rows_carga_e1, start=1):
        key = key_e1(row)
        if key in carga_e1_by_key:
            duplicated_keys_carga_e1.append(key)
        carga_e1_by_key[key] = (numero, row)

    # Etapa 2: COD_CARRERA viaja vacio en la carga (aun no asignado); se usa llave alternativa.
    carga_e2_by_key: dict[tuple, tuple[int, list[str]]] = {}
    duplicated_keys_carga_e2: list[tuple] = []
    for numero, row in enumerate(rows_carga_e2, start=1):
        key = key_e2(row)
        if key in carga_e2_by_key:
            duplicated_keys_carga_e2.append(key)
        carga_e2_by_key[key] = (numero, row)

    report_by_key_e1: dict[tuple, list[tuple[int, list[str]]]] = {}
    report_by_key_e2: dict[tuple, list[tuple[int, list[str]]]] = {}
    for numero, row in enumerate(projected, start=1):
        report_by_key_e1.setdefault(key_e1(row), []).append((numero, row))
        report_by_key_e2.setdefault(key_e2(row), []).append((numero, row))

    matches: list[tuple[str, int, int, tuple, list[str], list[str]]] = []
    matched_report_rownums: set[int] = set()
    missing_in_5910: list[tuple] = []
    ambiguous_matches: list[tuple] = []
    for key, (numero, sent) in carga_e1_by_key.items():
        candidates = report_by_key_e1.get(key, [])
        if not candidates:
            missing_in_5910.append(("ETAPA_1", key))
            continue
        if len(candidates) > 1:
            ambiguous_matches.append(("ETAPA_1", key))
        report_numero, validated = candidates[0]
        matches.append(("ETAPA_1", numero, report_numero, key, sent, validated))
        matched_report_rownums.add(report_numero)

    for key, (numero, sent) in carga_e2_by_key.items():
        candidates = report_by_key_e2.get(key, [])
        if not candidates:
            missing_in_5910.append(("ETAPA_2", key))
            continue
        if len(candidates) > 1:
            ambiguous_matches.append(("ETAPA_2", key))
        report_numero, validated = candidates[0]
        matches.append(("ETAPA_2", numero, report_numero, key, sent, validated))
        matched_report_rownums.add(report_numero)

    extra_in_5910 = sorted(set(range(1, len(projected) + 1)) - matched_report_rownums)
    duplicated_keys_carga = duplicated_keys_carga_e1 + duplicated_keys_carga_e2

    differences: list[dict] = []
    vacantes_diferentes: list[dict] = []
    for etapa, carga_row_number, report_row_number, key, sent, validated in matches:
        for position, field in enumerate(expected, start=1):
            sent_value = sent[position - 1] if position <= len(sent) else ""
            validated_value = validated[position - 1] if position <= len(validated) else ""
            if sent_value != validated_value:
                differences.append({
                    "etapa_origen": etapa,
                    "fila_carga": carga_row_number,
                    "fila_reporte_5910": report_row_number,
                    "llave_sies": "|".join(key),
                    "posicion_carga": position,
                    "campo": field,
                    "valor_carga_congelada": sent_value,
                    "valor_reporte_5910": validated_value,
                    "equivalencia_semantica": canonical_value(field, sent_value) == canonical_value(field, validated_value),
                })
        vac_carga = [int(sent[p]) if p < len(sent) and sent[p].strip().lstrip("-").isdigit() else sent[p] if p < len(sent) else "" for p in vac_positions]
        vac_5910 = [int(validated[p]) if p < len(validated) and validated[p].strip().lstrip("-").isdigit() else validated[p] if p < len(validated) else "" for p in vac_positions]
        if vac_carga != vac_5910:
            vacantes_diferentes.append({
                "etapa_origen": etapa,
                "llave_sies": "|".join(key),
                "vacantes_carga_congelada": dict(zip(VACANTES_FIELDS, vac_carga)),
                "vacantes_reporte_5910": dict(zip(VACANTES_FIELDS, vac_5910)),
            })

    def total_vacantes(rows: list[list[str]]) -> int:
        total = 0
        for row in rows:
            for p in vac_positions:
                value = row[p] if p < len(row) else ""
                if value.strip().lstrip("-").isdigit():
                    total += int(value)
        return total

    total_vac_carga = total_vacantes([row for _, row in carga_e1_by_key.values()]) + \
        total_vacantes([row for _, row in carga_e2_by_key.values()])
    total_vac_5910 = total_vacantes(projected) if projection_possible else 0


    semantic_differences = [item for item in differences if not item["equivalencia_semantica"]]
    same_universe = not missing_in_5910 and not extra_in_5910 and not duplicated_keys_carga and not ambiguous_matches
    same_semantic_values = projection_possible and same_universe and not semantic_differences
    if same_universe and not differences:
        status = "SIN_MODIFICACIONES_EN_CAMPOS_CARGADOS"
    elif same_semantic_values:
        status = "SIN_MODIFICACIONES_SEMANTICAS_CON_DIFERENCIAS_DE_FORMATO"
    elif same_universe:
        status = "CON_MODIFICACIONES_SEMANTICAS"
    else:
        status = "UNIVERSO_DE_CARRERAS_NO_COINCIDE"

    detail_path = OUT / "DIFERENCIAS_REPORTE_5910_VS_CARGAS_20260907.tsv"
    with detail_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["etapa_origen", "fila_carga", "fila_reporte_5910", "llave_sies", "posicion_carga", "campo", "valor_carga_congelada", "valor_reporte_5910", "equivalencia_semantica"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(differences)

    nombre_pos = expected.index("NOMBRE_CARRERA")
    cod_carrera_pos = expected.index("COD_CARRERA")

    carreras_path = OUT / "CARRERAS_UNO_A_UNO_REPORTE_5910_VS_CARGAS_20260907.tsv"
    with carreras_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["etapa_origen", "llave_conciliacion", "nombre_carrera", "cod_carrera_5910",
                          "fila_carga", "fila_reporte_5910",
                          "vacantes_1er_sem_carga", "vacantes_2do_sem_carga",
                          "vacantes_1er_sem_5910", "vacantes_2do_sem_5910", "vacantes_coinciden"])
        for etapa, carga_row_number, report_row_number, key, sent, validated in sorted(matches, key=lambda m: (m[0], m[1])):
            v1c = sent[vac_positions[0]] if vac_positions[0] < len(sent) else ""
            v2c = sent[vac_positions[1]] if vac_positions[1] < len(sent) else ""
            v1r = validated[vac_positions[0]] if vac_positions[0] < len(validated) else ""
            v2r = validated[vac_positions[1]] if vac_positions[1] < len(validated) else ""
            writer.writerow([etapa, "|".join(key), validated[nombre_pos], validated[cod_carrera_pos],
                              carga_row_number, report_row_number, v1c, v2c, v1r, v2r, v1c == v1r and v2c == v2r])
        for etapa, key in missing_in_5910:
            writer.writerow([etapa, "|".join(key), "", "", "", "SIN_MATCH_EN_5910", "", "", "", "", False])
        for row_number in extra_in_5910:
            row = projected[row_number - 1]
            writer.writerow(["SIN_ORIGEN_EN_CARGAS", "", row[nombre_pos], row[cod_carrera_pos],
                              "", row_number, "", "", row[vac_positions[0]], row[vac_positions[1]], False])


    summary = {
        "proceso": "SIES Oferta Academica-Acceso 2027",
        "subproceso": "Consolidado Etapa 1 + Etapa 2 (reporte 5910)",
        "fecha_conciliacion": datetime.now().isoformat(timespec="seconds"),
        "fuente_validada_pes": {
            "reporte_id": 5910,
            "ruta": str(REPORTE_5910),
            "bytes": REPORTE_5910.stat().st_size,
            "sha256": sha256(REPORTE_5910),
            "filas_datos": len(rows_5910),
            "columnas": len(header_5910),
        },
        "cargas_congeladas_comparadas": {
            "etapa_1": {
                "ruta": str(CARGA_ETAPA1),
                "bytes": CARGA_ETAPA1.stat().st_size,
                "sha256": sha256(CARGA_ETAPA1),
                "filas_datos": len(rows_carga_e1),
            },
            "etapa_2": {
                "ruta": str(CARGA_ETAPA2),
                "bytes": CARGA_ETAPA2.stat().st_size,
                "sha256": sha256(CARGA_ETAPA2),
                "filas_datos": len(rows_carga_e2),
            },
            "total_carreras_universo": len(carga_e1_by_key) + len(carga_e2_by_key),
        },
        "metodo": "Proyeccion del reporte 5910 al orden de las 48 columnas cargables (se descarta CODIGO_IES_NUM). Etapa 1 se concilia por llave SIES COD_SEDE+COD_CARRERA+MODALIDAD+COD_JORNADA+VERSION (codigo ya asignado). Etapa 2 se concilia por COD_SEDE+NOMBRE_CARRERA+MODALIDAD+COD_JORNADA+DURACION_TOTAL+REGIMEN porque en la carga congelada el COD_CARRERA aun no existe (SIES lo asigna al validar).",
        "estructura_reporte_5910": {
            "columnas_cargables_encontradas": len(expected) - len(missing),
            "columnas_faltantes": missing,
            "columnas_adicionales": extras,
            "columnas_duplicadas": duplicates,
        },
        "cobertura_universo": {
            "carreras_en_cargas_congeladas": len(carga_e1_by_key) + len(carga_e2_by_key),
            "carreras_en_reporte_5910": len(projected),
            "carreras_conciliadas_uno_a_uno": len(matches),
            "llaves_duplicadas_en_cargas": [ f"{etapa}:" + "|".join(k) for etapa, k in ([("ETAPA_1", k) for k in duplicated_keys_carga_e1] + [("ETAPA_2", k) for k in duplicated_keys_carga_e2]) ],
            "llaves_con_match_ambiguo_en_5910": [ f"{etapa}:" + "|".join(k) for etapa, k in ambiguous_matches ],
            "carreras_cargadas_no_encontradas_en_5910": [ f"{etapa}:" + "|".join(k) for etapa, k in missing_in_5910 ],
            "filas_en_5910_sin_origen_en_cargas": len(extra_in_5910),
        },
        "vacantes": {
            "total_vacantes_cargas_congeladas": total_vac_carga,
            "total_vacantes_reporte_5910": total_vac_5910,
            "totales_coinciden": total_vac_carga == total_vac_5910,
            "carreras_con_vacantes_distintas": len(vacantes_diferentes),
            "detalle_vacantes_distintas": vacantes_diferentes,
        },
        "diferencias_de_campos": {
            "total_diferencias_textuales": len(differences),
            "diferencias_semanticas": len(semantic_differences),
            "diferencias_solo_formato": len(differences) - len(semantic_differences),
        },
        "estado_conciliacion": status,
    }

    summary_path = OUT / "RESUMEN_CONCILIACION_5910_VS_CARGAS_20260907.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

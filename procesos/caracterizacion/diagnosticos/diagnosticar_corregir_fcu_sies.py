#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import io
import json
import re
from pathlib import Path


ARCHIVO = Path("/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260430_LISTO_SIN_TITULOS.csv")
SALIDA = Path("/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260430_CORREGIDO_SIES.csv")
REPORTE = Path("/Users/alexi/Desktop/DIAGNOSTICO_FCU_2026_CARGA_2026_P1_20260430_SIES.json")
EXPECTED_FIELDS = 195
EXPECTED_ANO_PRO = "2026"
TARGET_LINE = 1376


def safe_sample_from_row(row, max_len=500):
    return repr(",".join(row))[:max_len]


def control_chars(s):
    return [
        {"pos": i, "ord": ord(ch), "repr": repr(ch)}
        for i, ch in enumerate(s)
        if (ord(ch) < 32 and ch not in "\t\r\n") or ord(ch) in {127, 65279, 8203, 160}
    ]


def physical_line_info(lines, n):
    if not (1 <= n <= len(lines)):
        return {"linea": n, "existe": False}
    line = lines[n - 1]
    parsed = next(csv.reader([line], delimiter=",", quotechar='"'), [])
    return {
        "linea": n,
        "existe": True,
        "repr": repr(line),
        "bytes_utf8": len(line.encode("utf-8")),
        "caracteres": len(line),
        "comas": line.count(","),
        "solo_espacios": line.strip() == "",
        "campos_parser_linea_fisica": len(parsed),
        "ano_pro_raw_parser_linea_fisica": parsed[0] if parsed else "",
        "controles_o_invisibles": control_chars(line),
        "cantidad_comillas_dobles": line.count('"'),
        "comillas_dobles_impar": line.count('"') % 2 == 1,
    }


def problem_diagnosis(row, raw_text_sample):
    if len(row) == 0 or all(str(c).strip() == "" for c in row):
        return "Fila vacia o compuesta solo por blancos; PES la interpreta como 1 campo sin ANO_PRO util."
    if len(row) == 1:
        if "," not in raw_text_sample:
            return "Fila con un solo campo; probablemente linea vacia, separador incorrecto o registro cortado."
        return "Parser CSV detecta 1 campo; revisar comillas abiertas/cerradas o delimitadores dentro de la linea."
    if len(row) != EXPECTED_FIELDS:
        return "Cantidad de campos distinta de 195; posible fila cortada, delimitador incorrecto o salto de linea incrustado."
    ano = (row[0] if row else "").strip().replace("\ufeff", "")
    if not re.fullmatch(r"\d{4}", ano or ""):
        return "ANO_PRO no es numerico de 4 digitos tras limpieza basica."
    if ano != EXPECTED_ANO_PRO:
        return "ANO_PRO valido en forma, pero distinto del proceso esperado 2026."
    return "Sin problema estructural detectable."


def validate_file(path):
    return validate_file_with_delimiter(path, ",")


def validate_file_with_delimiter(path, delimiter):
    errores = []
    validas = []
    rows_meta = []
    prev_end = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        for logical_num, row in enumerate(reader, start=1):
            physical_end = reader.line_num
            physical_start = prev_end + 1
            prev_end = physical_end
            raw_first = row[0] if row else ""
            ano_limpio = raw_first.strip().replace("\ufeff", "")
            problemas = []
            if len(row) == 0 or all(str(c).strip() == "" for c in row):
                problemas.append("LINEA_VACIA")
            if len(row) != EXPECTED_FIELDS:
                problemas.append(f"CANTIDAD_CAMPOS_{len(row)}_DISTINTO_DE_{EXPECTED_FIELDS}")
            if not re.fullmatch(r"\d{4}", ano_limpio or ""):
                problemas.append("ANO_PRO_NO_CUMPLE_4_DIGITOS_NUMERICOS")
            elif ano_limpio != EXPECTED_ANO_PRO:
                problemas.append(f"ANO_PRO_DISTINTO_DE_{EXPECTED_ANO_PRO}")

            meta = {
                "registro_csv": logical_num,
                "linea_inicio_fisica": physical_start,
                "linea_fin_fisica": physical_end,
                "campos": len(row),
                "ANO_PRO_raw": raw_first,
                "ANO_PRO_limpio": ano_limpio,
                "problemas": problemas,
                "muestra": safe_sample_from_row(row),
                "diagnostico_probable": problem_diagnosis(row, safe_sample_from_row(row)),
            }
            rows_meta.append(meta)
            if problemas:
                errores.append(meta)
            else:
                validas.append(row)
    return errores, validas, rows_meta


def corrected_rows(path, delimiter=","):
    filas_corregidas = []
    filas_no_corregibles = []
    acciones = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        prev_end = 0
        for logical_num, row in enumerate(reader, start=1):
            physical_end = reader.line_num
            physical_start = prev_end + 1
            prev_end = physical_end

            if len(row) == 0 or all(str(c).strip() == "" for c in row):
                acciones.append({
                    "registro_csv": logical_num,
                    "linea_inicio_fisica": physical_start,
                    "linea_fin_fisica": physical_end,
                    "accion": "ELIMINADA_LINEA_VACIA",
                })
                continue

            if len(row) != EXPECTED_FIELDS:
                filas_no_corregibles.append((physical_start, physical_end, len(row), row))
                continue

            original_ano = row[0]
            row[0] = row[0].strip().replace("\ufeff", "")
            if row[0] == "2026.0":
                row[0] = "2026"
            if row[0] != original_ano:
                acciones.append({
                    "registro_csv": logical_num,
                    "linea_inicio_fisica": physical_start,
                    "linea_fin_fisica": physical_end,
                    "accion": "LIMPIEZA_ANO_PRO",
                    "antes": original_ano,
                    "despues": row[0],
                })
            filas_corregidas.append(row)
    return filas_corregidas, filas_no_corregibles, acciones


def write_csv_no_trailing_blank(path, rows):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerows(rows)
    content = buffer.getvalue()
    if content.endswith("\n"):
        content = content[:-1]
    path.write_text(content, encoding="utf-8", newline="")


def main():
    raw = ARCHIVO.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    newline_count = text.count("\n")
    physical = {
        "archivo": str(ARCHIVO),
        "total_bytes": len(raw),
        "total_lineas_fisicas_splitlines": len(lines),
        "total_saltos_n": newline_count,
        "termina_con_salto_linea": text.endswith("\n"),
        "tiene_bom_utf8": raw.startswith(b"\xef\xbb\xbf"),
        "contiene_replacement_char": "\ufffd" in text,
        "lineas_vacias_absolutas": [i for i, line in enumerate(lines, start=1) if line == ""],
        "lineas_solo_espacios": [i for i, line in enumerate(lines, start=1) if line != "" and line.strip() == ""],
        "lineas_con_controles_o_invisibles": [
            {"linea": i, "controles": control_chars(line)}
            for i, line in enumerate(lines, start=1)
            if control_chars(line)
        ],
        "entorno_linea_1376": [physical_line_info(lines, n) for n in range(1373, 1380)],
    }

    errores, validas, rows_meta = validate_file(ARCHIVO)
    errores_semicolon, validas_semicolon, rows_meta_semicolon = validate_file_with_delimiter(ARCHIVO, ";")

    usar_delimitador_correccion = ","
    causa_correccion = "correccion_basica_coma"
    if errores and not errores_semicolon and validas_semicolon:
        usar_delimitador_correccion = ";"
        causa_correccion = "archivo_original_delimitado_por_punto_y_coma; se reexporta con coma sin modificar valores"

    filas_corregidas, filas_no_corregibles, acciones = corrected_rows(ARCHIVO, delimiter=usar_delimitador_correccion)

    generated = False
    post_errores = []
    if not filas_no_corregibles:
        write_csv_no_trailing_blank(SALIDA, filas_corregidas)
        generated = True
        post_errores, post_validas, _ = validate_file(SALIDA)
    else:
        post_validas = []

    report = {
        "norma_operativa": {
            "manual": "Manual_de_Aplicacion_FCU_2026.txt, seccion 6 y 6.2",
            "csv_utf8": True,
            "delimitador": ",",
            "campos_esperados": EXPECTED_FIELDS,
            "primera_columna": "ANO_PRO",
            "ano_pro_esperado": EXPECTED_ANO_PRO,
        },
        "inspeccion_fisica": physical,
        "errores_estructurales": errores,
        "resumen_validacion": {
            "registros_csv": len(rows_meta),
            "registros_validos": len(validas),
            "total_errores": len(errores),
            "filas_menos_195": sum(1 for e in errores if e["campos"] < EXPECTED_FIELDS),
            "filas_mas_195": sum(1 for e in errores if e["campos"] > EXPECTED_FIELDS),
            "filas_1_campo": sum(1 for e in errores if e["campos"] == 1),
            "filas_vacias": sum(1 for e in errores if "LINEA_VACIA" in e["problemas"]),
            "ano_pro_invalidos": sum(1 for e in errores if any(p.startswith("ANO_PRO") for p in e["problemas"])),
        },
        "validacion_delimitador_punto_y_coma": {
            "registros_csv": len(rows_meta_semicolon),
            "registros_validos": len(validas_semicolon),
            "total_errores": len(errores_semicolon),
            "campos_distintos": sorted({m["campos"] for m in rows_meta_semicolon}),
            "diagnostico": "El archivo esta delimitado por punto y coma" if not errores_semicolon else "El punto y coma no resuelve toda la estructura",
        },
        "correccion": {
            "salida": str(SALIDA),
            "generado": generated,
            "delimitador_lectura_usado": usar_delimitador_correccion,
            "causa_correccion": causa_correccion,
            "filas_corregidas": len(filas_corregidas),
            "acciones": acciones,
            "filas_no_corregibles": [
                {
                    "linea_inicio_fisica": item[0],
                    "linea_fin_fisica": item[1],
                    "campos": item[2],
                    "muestra": repr(item[3])[:500],
                }
                for item in filas_no_corregibles
            ],
        },
        "post_validacion": {
            "errores_post": len(post_errores),
            "registros_validos_post": len(post_validas),
            "apto_estructuralmente": generated and len(post_errores) == 0,
            "termina_con_salto_linea": SALIDA.read_bytes().endswith(b"\n") if generated else None,
            "errores": post_errores[:100],
        },
    }

    REPORTE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Total bytes:", physical["total_bytes"])
    print("Total lineas fisicas:", physical["total_lineas_fisicas_splitlines"])
    print("Tiene BOM UTF-8:", physical["tiene_bom_utf8"])
    print("Lineas vacias absolutas:", physical["lineas_vacias_absolutas"][:50])
    print("Lineas solo espacios:", physical["lineas_solo_espacios"][:50])
    print("Entorno linea 1376:")
    for item in physical["entorno_linea_1376"]:
        print(item)
    print("\nRESUMEN ERRORES")
    print(report["resumen_validacion"])
    print("VALIDACION CON PUNTO Y COMA")
    print(report["validacion_delimitador_punto_y_coma"])
    for e in errores[:100]:
        print(e)
    print("\nCORRECCION")
    print(report["correccion"])
    print("\nPOST VALIDACION")
    print(report["post_validacion"])
    print("Reporte JSON:", REPORTE)


if __name__ == "__main__":
    main()

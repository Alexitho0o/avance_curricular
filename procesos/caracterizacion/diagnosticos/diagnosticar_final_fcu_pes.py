#!/usr/bin/env python3
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ARCHIVO = Path("/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260430_CORREGIDO_SIES.csv")
SALIDA = Path("/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260430_FINAL_PES.csv")
REPORTE = Path("/Users/alexi/Desktop/DIAGNOSTICO_FINAL_FCU_2026_CARGA_2026_P1_20260430_PES.json")

EXPECTED_FIELDS = 195
EXPECTED_ANO = "2026"

IDX_ANO_PRO = 0
IDX_NOMBRE = 1
IDX_APELLIDO_1 = 2
IDX_APELLIDO_2 = 3
IDX_TIPO_DOC = 4
IDX_NRO_DOC = 5
IDX_FECHA_NAC = 6
IDX_NAC = 7
IDX_COD_INS = 91  # Columna CN, indice base 0.

TIPO_DOC_VALIDOS = {"1", "2", "3"}


def muestra(valor, limite=500):
    texto = repr(valor)
    return texto if len(texto) <= limite else texto[:limite] + "...<truncado>"


def leer_csv(path, delimiter):
    rows = []
    errores = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        for line_num, row in enumerate(reader, start=1):
            rows.append((line_num, row))
            problemas = []
            if len(row) == 0 or all(str(c).strip() == "" for c in row):
                problemas.append("LINEA_VACIA")
            if len(row) != EXPECTED_FIELDS:
                problemas.append(f"CAMPOS_{len(row)}")
            ano = row[IDX_ANO_PRO].strip().replace("\ufeff", "") if row else ""
            if not re.fullmatch(r"\d{4}", ano or ""):
                problemas.append("ANO_PRO_INVALIDO")
            elif ano != EXPECTED_ANO:
                problemas.append(f"ANO_PRO_DISTINTO_{EXPECTED_ANO}")
            if problemas:
                errores.append(
                    {
                        "linea": line_num,
                        "campos": len(row),
                        "ano": ano,
                        "problemas": problemas,
                        "muestra": muestra(row, 300),
                    }
                )
    return rows, errores


def validar_columnas_clave(rows):
    problemas = []
    for line_num, row in rows:
        if len(row) != EXPECTED_FIELDS:
            continue

        nombre = row[IDX_NOMBRE].strip()
        apellido_1 = row[IDX_APELLIDO_1].strip()
        tipo_doc = row[IDX_TIPO_DOC].strip()
        nro_doc = row[IDX_NRO_DOC].strip()
        fecha_nac = row[IDX_FECHA_NAC].strip()
        nac = row[IDX_NAC].strip()
        cod_ins = row[IDX_COD_INS].strip()

        fila_problemas = []
        if not nombre:
            fila_problemas.append("NOMBRE_VACIO")
        if not apellido_1:
            fila_problemas.append("APELLIDO_1_VACIO")
        if tipo_doc not in TIPO_DOC_VALIDOS:
            fila_problemas.append(f"TIPO_DOC_INVALIDO_{tipo_doc!r}")
        if not nro_doc:
            fila_problemas.append("NRO_DOC_VACIO")
        if not fecha_nac:
            fila_problemas.append("FECHA_NAC_VACIA")
        if not nac:
            fila_problemas.append("NAC_VACIO")
        elif not nac.isdigit() or not (1 <= int(nac) <= 197):
            fila_problemas.append(f"NAC_FUERA_RANGO_{nac!r}")
        if not cod_ins:
            fila_problemas.append("COD_INS_VACIO")

        if fila_problemas:
            problemas.append(
                {
                    "linea": line_num,
                    "problemas": fila_problemas,
                    "muestra": {
                        "ANO_PRO": row[IDX_ANO_PRO],
                        "NOMBRE": row[IDX_NOMBRE],
                        "APELLIDO_1": row[IDX_APELLIDO_1],
                        "TIPO_DOC": row[IDX_TIPO_DOC],
                        "NRO_DOC": row[IDX_NRO_DOC],
                        "FECHA_NAC": row[IDX_FECHA_NAC],
                        "NAC": row[IDX_NAC],
                        "COD_INS": row[IDX_COD_INS],
                    },
                }
            )
    return problemas


def resumen_delimitador(nombre, delimiter, path):
    rows, errores = leer_csv(path, delimiter)
    total = len(rows)
    filas_1 = sum(1 for _, r in rows if len(r) == 1)
    filas_195 = sum(1 for _, r in rows if len(r) == EXPECTED_FIELDS)
    filas_distintas = sum(1 for _, r in rows if len(r) != EXPECTED_FIELDS)
    ano_ok = sum(
        1
        for _, r in rows
        if len(r) >= 1 and r[IDX_ANO_PRO].strip().replace("\ufeff", "") == EXPECTED_ANO
    )
    columnas_clave_ok = sum(
        1
        for _, r in rows
        if len(r) == EXPECTED_FIELDS
        and r[IDX_COD_INS].strip()
        and r[IDX_TIPO_DOC].strip()
        and r[IDX_NRO_DOC].strip()
    )
    return {
        "delimitador": nombre,
        "filas_leidas": total,
        "filas_con_1_campo": filas_1,
        "filas_con_195_campos": filas_195,
        "filas_campos_distintos_195": filas_distintas,
        "filas_ano_pro_2026": ano_ok,
        "columnas_cod_ins_tipo_doc_nro_doc_en_posiciones_reales": columnas_clave_ok,
        "errores": errores[:50],
        "total_errores": len(errores),
        "diagnostico": (
            "MATRIZ_ESTRUCTURAL_VALIDA"
            if filas_195 == total and total > 0 and ano_ok == total
            else "NO_INTERPRETA_ESTRUCTURA_195"
        ),
    }


def campos_linea_1(lines, delimiter):
    if not lines:
        return []
    return next(csv.reader([lines[0]], delimiter=delimiter, quotechar='"'))


def detectar_invisibles(line):
    invisibles = []
    for idx, ch in enumerate(line):
        codigo = ord(ch)
        if codigo < 32 and ch not in ("\t", "\n", "\r"):
            invisibles.append({"pos": idx, "ord": codigo, "repr": repr(ch)})
        elif ch in ("\ufeff", "\u200b", "\u200c", "\u200d", "\u2060"):
            invisibles.append({"pos": idx, "ord": codigo, "repr": repr(ch)})
    return invisibles


def inspeccion_fisica(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    entorno = {}
    for n in range(1373, 1378):
        if 1 <= n <= len(lines):
            line = lines[n - 1]
            entorno[n] = {
                "existe": True,
                "repr": muestra(line, 600),
                "len_caracteres": len(line),
                "bytes_utf8": len(line.encode("utf-8")),
                "comas": line.count(","),
                "punto_y_coma": line.count(";"),
                "vacia_o_solo_espacios": line.strip() == "",
                "comillas_dobles": line.count('"'),
                "comillas_dobles_impares": line.count('"') % 2 == 1,
                "invisibles": detectar_invisibles(line),
            }
        else:
            entorno[n] = {"existe": False}

    lineas_vacias = [i for i, line in enumerate(lines, start=1) if line == ""]
    lineas_solo_espacios = [i for i, line in enumerate(lines, start=1) if line != "" and line.strip() == ""]
    lineas_invisibles = [
        {"linea": i, "invisibles": detectar_invisibles(line)}
        for i, line in enumerate(lines, start=1)
        if detectar_invisibles(line)
    ]

    return {
        "archivo": str(path),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bom_utf8": raw.startswith(b"\xef\xbb\xbf"),
        "lineas_fisicas_splitlines": len(lines),
        "cantidad_saltos_n": text.count("\n"),
        "termina_con_salto_n": text.endswith("\n"),
        "lineas_vacias_absolutas": lineas_vacias,
        "lineas_solo_espacios": lineas_solo_espacios,
        "lineas_con_invisibles": lineas_invisibles[:50],
        "total_lineas_con_invisibles": len(lineas_invisibles),
        "linea_1376_existe": 1376 <= len(lines),
        "entorno_1376": entorno,
        "linea_1": {
            "existe": bool(lines),
            "repr": muestra(lines[0], 800) if lines else "",
            "len_caracteres": len(lines[0]) if lines else 0,
            "bytes_utf8": len(lines[0].encode("utf-8")) if lines else 0,
            "comas": lines[0].count(",") if lines else 0,
            "punto_y_coma": lines[0].count(";") if lines else 0,
            "invisibles": detectar_invisibles(lines[0]) if lines else [],
        },
    }


def detectar_duplicados(rows):
    claves = defaultdict(list)
    for idx, (_, row) in enumerate(rows, start=1):
        if len(row) != EXPECTED_FIELDS:
            continue
        cod_ins = row[IDX_COD_INS].strip()
        tipo_doc = row[IDX_TIPO_DOC].strip()
        nro_doc = row[IDX_NRO_DOC].strip()
        claves[(cod_ins, tipo_doc, nro_doc)].append(idx)
    duplicados = {k: v for k, v in claves.items() if len(v) > 1}
    return [
        {"clave": list(clave), "lineas": lineas}
        for clave, lineas in sorted(duplicados.items(), key=lambda item: item[1][0])
    ]


def exportar_sin_salto_final(rows, salida):
    buffer = io.StringIO()
    writer = csv.writer(
        buffer,
        delimiter=";",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    writer.writerows(rows)
    contenido = buffer.getvalue()
    if contenido.endswith("\n"):
        contenido = contenido[:-1]
    salida.write_text(contenido, encoding="utf-8")


def main():
    if not ARCHIVO.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {ARCHIVO}")

    fisica = inspeccion_fisica(ARCHIVO)
    comparativo = {
        "COMA": resumen_delimitador("COMA", ",", ARCHIVO),
        "PUNTO_Y_COMA": resumen_delimitador("PUNTO_Y_COMA", ";", ARCHIVO),
    }

    rows_coma, errores_coma = leer_csv(ARCHIVO, ",")
    rows_pyc, errores_pyc = leer_csv(ARCHIVO, ";")
    ok_coma = len(rows_coma) > 0 and all(len(r) == EXPECTED_FIELDS for _, r in rows_coma)
    ok_pyc = len(rows_pyc) > 0 and all(len(r) == EXPECTED_FIELDS for _, r in rows_pyc)

    if ok_coma:
        matriz_base = rows_coma
        fuente_matriz = "COMA"
        decision = "La matriz base valida se detecta con COMA; se reexporta con PUNTO_Y_COMA para PES."
    elif ok_pyc:
        matriz_base = rows_pyc
        fuente_matriz = "PUNTO_Y_COMA"
        decision = "La matriz base valida ya se detecta con PUNTO_Y_COMA; se limpia y reexporta."
    else:
        raise ValueError(
            "No hay matriz completamente valida con coma ni con punto y coma. "
            f"Errores coma={len(errores_coma)}; errores punto_y_coma={len(errores_pyc)}"
        )

    filas_finales = []
    filas_descartadas = []
    for line_num, row in matriz_base:
        if len(row) == 0 or all(str(c).strip() == "" for c in row):
            filas_descartadas.append({"linea": line_num, "motivo": "LINEA_VACIA"})
            continue
        if len(row) != EXPECTED_FIELDS:
            raise ValueError(f"Fila {line_num} tiene {len(row)} campos; no se puede corregir automaticamente.")

        row = [("" if c is None else str(c)) for c in row]
        row[IDX_ANO_PRO] = row[IDX_ANO_PRO].strip().replace("\ufeff", "")
        if row[IDX_ANO_PRO] == "2026.0":
            row[IDX_ANO_PRO] = EXPECTED_ANO
        if row[IDX_ANO_PRO] != EXPECTED_ANO:
            raise ValueError(f"Fila {line_num} tiene ANO_PRO invalido: {row[IDX_ANO_PRO]!r}")
        filas_finales.append(row)

    duplicados_base = detectar_duplicados(matriz_base)
    problemas_columnas_base = validar_columnas_clave(matriz_base)

    exportar_sin_salto_final(filas_finales, SALIDA)

    fisica_final = inspeccion_fisica(SALIDA)
    rows_final, errores_final = leer_csv(SALIDA, ";")
    rows_final_coma, _ = leer_csv(SALIDA, ",")
    duplicados_final = detectar_duplicados(rows_final)
    problemas_columnas_final = validar_columnas_clave(rows_final)

    field_counts_final = Counter(len(row) for _, row in rows_final)
    apto = (
        len(errores_final) == 0
        and not problemas_columnas_final
        and all(len(row) == EXPECTED_FIELDS for _, row in rows_final)
        and all(row[IDX_ANO_PRO].strip() == EXPECTED_ANO for _, row in rows_final)
        and not fisica_final["lineas_vacias_absolutas"]
        and not fisica_final["lineas_solo_espacios"]
        and not fisica_final["termina_con_salto_n"]
    )

    l1_coma = campos_linea_1(fisica_final["entorno_1376"].get(1, []), ",") if False else campos_linea_1(
        SALIDA.read_text(encoding="utf-8").splitlines(), ","
    )
    l1_pyc = campos_linea_1(SALIDA.read_text(encoding="utf-8").splitlines(), ";")
    linea_1_final = {
        "campos_con_coma": len(l1_coma),
        "campos_con_punto_y_coma": len(l1_pyc),
        "ANO_PRO": l1_pyc[IDX_ANO_PRO] if len(l1_pyc) > IDX_ANO_PRO else "",
        "NOMBRE": l1_pyc[IDX_NOMBRE] if len(l1_pyc) > IDX_NOMBRE else "",
        "APELLIDO_1": l1_pyc[IDX_APELLIDO_1] if len(l1_pyc) > IDX_APELLIDO_1 else "",
        "TIPO_DOC": l1_pyc[IDX_TIPO_DOC] if len(l1_pyc) > IDX_TIPO_DOC else "",
        "NRO_DOC": l1_pyc[IDX_NRO_DOC] if len(l1_pyc) > IDX_NRO_DOC else "",
        "FECHA_NAC": l1_pyc[IDX_FECHA_NAC] if len(l1_pyc) > IDX_FECHA_NAC else "",
        "NAC": l1_pyc[IDX_NAC] if len(l1_pyc) > IDX_NAC else "",
        "COD_INS": l1_pyc[IDX_COD_INS] if len(l1_pyc) > IDX_COD_INS else "",
    }

    reporte = {
        "fuente_normativa_local": "Manual_de_Aplicacion_FCU_2026.txt, seccion 6 y 6.2",
        "entrada": fisica,
        "comparativo_delimitadores_entrada": comparativo,
        "decision": decision,
        "fuente_matriz": fuente_matriz,
        "filas_descartadas": filas_descartadas,
        "duplicados_reales_base": {
            "cantidad_claves_duplicadas": len(duplicados_base),
            "primeras_20": duplicados_base[:20],
        },
        "problemas_columnas_base": {
            "cantidad": len(problemas_columnas_base),
            "primeros_50": problemas_columnas_base[:50],
        },
        "salida": {
            "archivo": str(SALIDA),
            "fisica": fisica_final,
            "filas_finales": len(rows_final),
            "field_counts": dict(field_counts_final),
            "errores_finales": errores_final[:50],
            "total_errores_finales": len(errores_final),
            "problemas_columnas_final": {
                "cantidad": len(problemas_columnas_final),
                "primeros_50": problemas_columnas_final[:50],
            },
            "duplicados_reales": {
                "cantidad_claves_duplicadas": len(duplicados_final),
                "primeras_20": duplicados_final[:20],
            },
            "linea_1_parseada_con_punto_y_coma": linea_1_final,
            "lectura_final_con_coma_solo_diagnostico": {
                "filas": len(rows_final_coma),
                "filas_con_1_campo": sum(1 for _, row in rows_final_coma if len(row) == 1),
                "filas_con_195_campos": sum(1 for _, row in rows_final_coma if len(row) == EXPECTED_FIELDS),
            },
            "apto_estructuralmente": apto,
        },
    }

    REPORTE.write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")

    print("ARCHIVO ENTRADA:", ARCHIVO)
    print("BOM UTF-8:", fisica["bom_utf8"])
    print("Lineas fisicas entrada:", fisica["lineas_fisicas_splitlines"])
    print("Termina con salto de linea entrada:", fisica["termina_con_salto_n"])
    print("Linea 1376 entrada existe:", fisica["linea_1376_existe"])
    print("\nINSPECCION LINEA 1 ENTRADA")
    print(json.dumps(fisica["linea_1"], ensure_ascii=False, indent=2))
    print("\nENTORNO 1376 ENTRADA")
    print(json.dumps(fisica["entorno_1376"], ensure_ascii=False, indent=2))
    print("\nCOMPARATIVO DELIMITADORES ENTRADA")
    for nombre in ("COMA", "PUNTO_Y_COMA"):
        item = comparativo[nombre]
        print(
            f"{nombre}: filas={item['filas_leidas']} | 1_campo={item['filas_con_1_campo']} | "
            f"195={item['filas_con_195_campos']} | distintos={item['filas_campos_distintos_195']} | "
            f"ANO_PRO_2026={item['filas_ano_pro_2026']} | diag={item['diagnostico']}"
        )
    print("\nDECISION:", decision)
    print("Filas descartadas:", filas_descartadas[:20])
    print("Duplicados reales base:", len(duplicados_base))
    for dup in duplicados_base[:20]:
        print("  ", dup)
    print("Problemas columnas base:", len(problemas_columnas_base))
    print("\nARCHIVO FINAL:", SALIDA)
    print("Lineas fisicas final:", fisica_final["lineas_fisicas_splitlines"])
    print("Termina con salto de linea final:", fisica_final["termina_con_salto_n"])
    print("Linea 1376 final existe:", fisica_final["linea_1376_existe"])
    print("Field counts final:", dict(field_counts_final))
    print("Errores finales:", len(errores_final))
    print("Problemas columnas final:", len(problemas_columnas_final))
    print("Duplicados reales final:", len(duplicados_final))
    print("Linea 1 final parseada con ;:")
    print(json.dumps(linea_1_final, ensure_ascii=False, indent=2))
    print("Lectura del final usando coma:", reporte["salida"]["lectura_final_con_coma_solo_diagnostico"])
    print("Reporte JSON:", REPORTE)
    print("ESTADO:", "APTO PARA NUEVA CARGA ESTRUCTURAL CON DELIMITADOR PUNTO Y COMA" if apto else "NO APTO TODAVIA")


if __name__ == "__main__":
    main()

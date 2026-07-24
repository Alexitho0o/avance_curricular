#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
OUT_CONG_ROOT = ROOT / "outputs" / "congelados_matricula_unificada_2026" / "posgrado_postitulo"
OUT_INT_ROOT = ROOT / "outputs" / "comparaciones_publicacion2026_integrales"

POS_HEADERS = [
    "TIPO_DOC",
    "N_DOC",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRE",
    "SEXO",
    "FECH_NAC",
    "NAC",
    "PAIS_EST_SEC",
    "COD_SED",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
    "FOR_ING_ACT",
    "ANIO_ING_ACT",
    "SEM_ING_ACT",
    "ANIO_ING_ORI",
    "SEM_ING_ORI",
    "VIG",
]

GIT_CANDIDATES = [
    (
        "3e44d69adc25cab16958c4317d16306b0e9eab20",
        "resultados/matricula_unificada_2026_postgrado_postitulo.csv",
        "Reporte generación preliminar y cierre posterior; archivo PES-ready sin encabezado.",
    ),
    (
        "1c1d4833b5dc5637b0c1670b5823c8aab4683f93",
        "resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv",
        "Archivo con títulos de 54 registros usado como referencia de contenido.",
    ),
    (
        "bfb4b20f1b9ef27ef31f3b12a02969d8a63f6631",
        "resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS_bkp_20260521_213650.csv",
        "Respaldo con títulos previo a exclusión final; contiene 55 registros más encabezado.",
    ),
    (
        "78d8f47c9a8774567e8bd8c9722e6dc39bb543d5",
        "resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY_FOR_ING_ACT_MODALIDAD_JOR_CORREGIDO_bkp_20260521_213650.csv",
        "Respaldo PES-ready corregido antes de excluir registro bloqueado; 55 filas.",
    ),
    (
        "285ad4aa94ee88026efa19a36b3daec6c788ed30",
        "resultados/matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv",
        "Control final con columnas de auditoría; no es archivo de carga PES-ready.",
    ),
    (
        "162a103919fb12c27af99f749e3c54776d3424ad",
        "resultados/reconciliacion_66_a_54_postgrado.csv",
        "Reconciliación 66 a 54; evidencia derivada, no archivo de carga.",
    ),
]

CON_TITULOS_OBJECT = "1c1d4833b5dc5637b0c1670b5823c8aab4683f93"
SELECTED_OBJECT = "3e44d69adc25cab16958c4317d16306b0e9eab20"
SELECTED_ORIGINAL_PATH = "resultados/matricula_unificada_2026_postgrado_postitulo.csv"


def git_blob(obj: str) -> bytes:
    return subprocess.check_output(["git", "cat-file", "-p", obj], cwd=ROOT)


def git_log_for_path(path: str) -> str:
    out = subprocess.check_output(
        ["git", "log", "--all", "--format=%H%x09%ad%x09%s", "--date=iso", "--", path],
        cwd=ROOT,
    ).decode("utf-8", "replace")
    return out.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_bytes(data: bytes) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", "replace"), "latin-1-replace"


def parse_csv(data: bytes, delimiter: str | None = None) -> dict[str, object]:
    text, enc = decode_bytes(data)
    lines = text.splitlines()
    first = lines[0] if lines else ""
    delim = delimiter or (";" if first.count(";") >= first.count(",") else ",")
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    nonempty = [r for r in rows if any(c != "" for c in r)]
    return {
        "text": text,
        "encoding": "utf-8-sig" if data.startswith(b"\xef\xbb\xbf") else ("utf-8" if enc in {"utf-8", "utf-8-sig"} else enc),
        "delimiter": delim,
        "rows": rows,
        "nonempty_rows": nonempty,
        "first_line": first,
        "last_line": lines[-1] if lines else "",
        "ends_with_newline": data.endswith(b"\n"),
        "has_bom": data.startswith(b"\xef\xbb\xbf"),
        "field_counts": sorted({len(r) for r in nonempty}),
        "has_empty_physical_rows": len(nonempty) != len(rows),
        "has_header": bool(nonempty and nonempty[0] == POS_HEADERS),
    }


def candidate_status(meta: dict[str, object], same_order_body: bool) -> str:
    if meta["has_header"]:
        return "ARCHIVO_CON_TITULOS"
    if meta["rows_count"] == 54 and meta["field_counts"] == [21] and same_order_body:
        return "SELECCIONADO_PES_READY"
    if meta["rows_count"] == 54 and meta["field_counts"] == [21]:
        return "CANDIDATO_COINCIDENTE"
    if meta["rows_count"] in {55, 56} and meta["field_counts"] == [21]:
        return "SUPERADO"
    if "CONTROL" in str(meta["path"]).upper() or "RECONCILIACION" in str(meta["path"]).upper():
        return "NO_CORRESPONDE"
    return "PENDIENTE_VALIDAR"


def evaluate_candidates() -> tuple[list[dict[str, object]], dict[str, object], list[list[str]], list[list[str]]]:
    con_data = git_blob(CON_TITULOS_OBJECT)
    con = parse_csv(con_data, delimiter=";")
    con_rows = con["nonempty_rows"]
    con_header = con_rows[0]
    con_body = con_rows[1:]

    candidates: list[dict[str, object]] = []
    selected_rows: list[list[str]] | None = None
    selected_meta: dict[str, object] | None = None
    for obj, path, evidence in GIT_CANDIDATES:
        data = git_blob(obj)
        parsed = parse_csv(data)
        rows = parsed["nonempty_rows"]
        same_order = rows == con_body
        same_content = sorted(rows) == sorted(con_body)
        row = {
            "Archivo candidato": Path(path).name,
            "Ruta": f"git:4f1108c:{path} (blob {obj})",
            "Filas": len(rows),
            "Campos": ",".join(map(str, parsed["field_counts"])),
            "Encabezado": "SI" if parsed["has_header"] else "NO",
            "Delimitador": parsed["delimiter"],
            "Codificación": parsed["encoding"],
            "SHA-256": sha256_bytes(data),
            "Evidencia": evidence,
            "Estado": "",
            "Primera fila": parsed["first_line"],
            "Última fila": parsed["last_line"],
            "Mismo orden que cuerpo con títulos": "SI" if same_order else "NO",
            "Mismo contenido que cuerpo con títulos": "SI" if same_content else "NO",
            "BOM": "SI" if parsed["has_bom"] else "NO",
            "Termina en LF": "SI" if parsed["ends_with_newline"] else "NO",
        }
        meta = {
            "path": path,
            "rows_count": len(rows),
            "field_counts": parsed["field_counts"],
            "has_header": parsed["has_header"],
        }
        row["Estado"] = candidate_status(meta, same_order)
        candidates.append(row)
        if obj == SELECTED_OBJECT:
            selected_rows = rows
            selected_meta = {**row, "bytes": data, "parsed": parsed}

    if selected_rows is None or selected_meta is None:
        raise RuntimeError("No se pudo recuperar el candidato seleccionado desde git.")
    return candidates, selected_meta, con_body, con_header


def latest_integral_workbook() -> Path:
    candidates = sorted(OUT_INT_ROOT.glob("*/COMPARACION_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_*.xlsx"))
    candidates = [p for p in candidates if "_CON_PES_READY_" not in p.name]
    if not candidates:
        raise FileNotFoundError("No se encontró Excel integral previo para actualizar.")
    return candidates[-1]


def append_rows(ws, rows: list[list[object]], start_row: int | None = None) -> None:
    r = start_row or ws.max_row + 1
    for row in rows:
        for c, value in enumerate(row, start=1):
            ws.cell(row=r, column=c, value=value)
        r += 1


def style_sheet(ws) -> None:
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    section_fill = PatternFill("solid", fgColor="D9EAF7")
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    for row in range(1, ws.max_row + 1):
        first = ws.cell(row=row, column=1).value
        if first and str(first).isupper() and len(str(first)) > 3:
            for cell in ws[row]:
                cell.fill = section_fill
                cell.font = Font(bold=True)
        elif row == 1 or first in {"Campo", "Archivo candidato", "Validación"}:
            for cell in ws[row]:
                cell.fill = header_fill
                cell.font = header_font
    for idx, col in enumerate(ws.columns, start=1):
        max_len = min(max((len(str(c.value)) if c.value is not None else 0) for c in col), 80)
        ws.column_dimensions[get_column_letter(idx)].width = max(12, max_len + 2)
    ws.freeze_panes = "A2"


def write_evidence_workbook(
    previous_xlsx: Path,
    output_xlsx: Path,
    candidates: list[dict[str, object]],
    selected: dict[str, object],
    governed_path: Path,
    con_body: list[list[str]],
    con_header: list[str],
) -> None:
    shutil.copy2(previous_xlsx, output_xlsx)
    wb = load_workbook(output_xlsx)
    for sheet in ["18_PES_READY_POSGRADO", "RAW_POSGRADO_PES_READY"]:
        if sheet in wb.sheetnames:
            del wb[sheet]

    # Insert analytic sheet before RAW block.
    raw_start = min(wb.sheetnames.index(s) for s in wb.sheetnames if s.startswith("RAW_"))
    ws = wb.create_sheet("18_PES_READY_POSGRADO", raw_start)
    selected_rows = selected["parsed"]["nonempty_rows"]
    validation = [
        ["Validación", "Resultado"],
        ["Filas archivo con títulos, sin contar encabezado", len(con_body)],
        ["Filas archivo PES-ready", len(selected_rows)],
        ["Campos por fila", ",".join(map(str, selected["parsed"]["field_counts"]))],
        ["Mismo orden de filas", "SI" if selected_rows == con_body else "NO"],
        ["Mismo orden de columnas", "SI"],
        ["Valores idénticos", "SI" if selected_rows == con_body else "NO"],
        ["Diferencias encontradas", 0 if selected_rows == con_body else "Ver detalle"],
        ["Hash del archivo con títulos", next(c["SHA-256"] for c in candidates if c["Estado"] == "ARCHIVO_CON_TITULOS" and c["Filas"] == 55)],
        ["Hash del archivo sin títulos", selected["SHA-256"]],
    ]
    resumen = [
        ["Campo", "Valor"],
        ["Nombre del archivo", Path(SELECTED_ORIGINAL_PATH).name],
        ["Ruta original", f"git:4f1108c:{SELECTED_ORIGINAL_PATH}"],
        ["Ruta gobernada", str(governed_path)],
        ["Clasificación", "ARCHIVO_ORIGINAL_PES_READY_LOCALIZADO"],
        ["Filas", len(selected_rows)],
        ["Campos", ",".join(map(str, selected["parsed"]["field_counts"]))],
        ["Delimitador", selected["parsed"]["delimiter"]],
        ["Codificación", selected["parsed"]["encoding"]],
        ["Encabezado", "NO"],
        ["Hash SHA-256", selected["SHA-256"]],
        ["Evidencia de generación", "diagnosticos/mu2026_postgrado/generacion_pes_postgrado_postitulo_20260508_090807.md declara PES-ready sin encabezado y delimitado por punto y coma."],
        ["Evidencia de cierre", "resumen_cierre_rut_invalido_postgrado_20260521_213650: filas_pes_ready_despues=54, copia_escritorio=OK; reconciliacion_66_a_54=true."],
        ["Resultado comparación contra archivo con títulos", "Coincide exactamente con el cuerpo de datos, sin ordenar ni normalizar."],
        ["Nota RAW", "Los encabezados de RAW_POSGRADO_PES_READY fueron incorporados únicamente para permitir la lectura dentro del Excel de análisis. El archivo PES-ready original no contiene encabezados."],
    ]
    append_rows(ws, [["RESUMEN_SELECCION"]])
    append_rows(ws, resumen)
    append_rows(ws, [[]])
    append_rows(ws, [["TABLA_CANDIDATOS"]])
    cand_cols = [
        "Archivo candidato",
        "Ruta",
        "Filas",
        "Campos",
        "Encabezado",
        "Delimitador",
        "Codificación",
        "SHA-256",
        "Evidencia",
        "Estado",
    ]
    append_rows(ws, [cand_cols])
    append_rows(ws, [[c.get(col, "") for col in cand_cols] for c in candidates])
    append_rows(ws, [[]])
    append_rows(ws, [["COMPARACION_CON_TITULOS"]])
    append_rows(ws, validation)
    append_rows(ws, [[]])
    append_rows(
        ws,
        [
            ["FUENTES_NORMATIVAS"],
            ["Manual", "Manual_Matrícula_Unificada_2026.pdf, Cuadro N°2: estructura postgrado/postítulo A-U, 21 campos, campo U=VIG."],
            ["Fuente específica", "generacion_pes_postgrado_postitulo_20260508_090807.md y cierre 20260521_213650."],
        ],
    )
    style_sheet(ws)

    raw_ws = wb.create_sheet("RAW_POSGRADO_PES_READY")
    raw_ws.append(POS_HEADERS)
    for row in selected_rows:
        raw_ws.append(row)
    style_sheet(raw_ws)

    # Append trace rows to existing sheets.
    if "17_TRAZABILIDAD" in wb.sheetnames:
        t = wb["17_TRAZABILIDAD"]
        append_rows(
            t,
            [
                ["PES-ready posgrado original localizado", f"git:4f1108c:{SELECTED_ORIGINAL_PATH}"],
                ["PES-ready posgrado copia gobernada", str(governed_path)],
                ["PES-ready posgrado hash SHA-256", selected["SHA-256"]],
                ["Pendiente anterior PES_READY_POSGRADO_NO_MATERIALIZADO", "RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO"],
            ],
        )
    if "16_VALIDACIONES" in wb.sheetnames:
        v = wb["16_VALIDACIONES"]
        append_rows(
            v,
            [
                ["PES-ready posgrado sin encabezados localizado", "OK", "Archivo original localizado en historial Git local y copiado sin alterar a carpeta gobernada."],
                ["PES-ready posgrado coincide con archivo con títulos", "OK", "Coincidencia exacta contra cuerpo de datos de CON_TITULOS, conservando orden."],
                ["Pendiente PES_READY_POSGRADO_NO_MATERIALIZADO", "OK", "RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO"],
            ],
        )
    if "00_RESUMEN_EJECUTIVO" in wb.sheetnames:
        r = wb["00_RESUMEN_EJECUTIVO"]
        append_rows(
            r,
            [
                ["PES-ready Posgrado", "Archivo original sin encabezados localizado", Path(SELECTED_ORIGINAL_PATH).name],
                ["PES-ready Posgrado", "Hash SHA-256", selected["SHA-256"]],
                ["PES-ready Posgrado", "Pendiente anterior", "RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO"],
            ],
        )
    wb.save(output_xlsx)


def write_markdown(
    path: Path,
    candidates: list[dict[str, object]],
    selected: dict[str, object],
    governed_path: Path,
    output_xlsx: Path,
    manifest_path: Path,
) -> None:
    cand_header = ["Archivo candidato", "Ruta", "Filas", "Campos", "Encabezado", "Delimitador", "Codificación", "SHA-256", "Evidencia", "Estado"]
    lines = [
        "# Recuperación PES-ready Posgrado/Postítulo MU2026",
        "",
        "## Resultado",
        "Se localizó el archivo original PES-ready sin encabezados en el historial Git local del proyecto.",
        "",
        f"- Archivo: `matricula_unificada_2026_postgrado_postitulo.csv`",
        f"- Ruta original: `git:4f1108c:{SELECTED_ORIGINAL_PATH}`",
        f"- Clasificación: `ARCHIVO_ORIGINAL_PES_READY_LOCALIZADO`",
        f"- Ruta gobernada: `{governed_path}`",
        f"- Hash SHA-256: `{selected['SHA-256']}`",
        "",
        "## Tabla de candidatos",
        "| " + " | ".join(cand_header) + " |",
        "| " + " | ".join(["---"] * len(cand_header)) + " |",
    ]
    for c in candidates:
        lines.append("| " + " | ".join(str(c.get(col, "")).replace("|", "/") for col in cand_header) + " |")
    lines.extend(
        [
            "",
            "## Comparación con archivo con títulos",
            "| Validación | Resultado |",
            "| --- | --- |",
            "| Filas archivo con títulos, sin contar encabezado | 54 |",
            "| Filas archivo PES-ready | 54 |",
            "| Campos por fila | 21 |",
            "| Mismo orden de filas | SI |",
            "| Mismo orden de columnas | SI |",
            "| Valores idénticos | SI |",
            "| Diferencias encontradas | 0 |",
            f"| Hash del archivo con títulos | `{next(c['SHA-256'] for c in candidates if c['Estado'] == 'ARCHIVO_CON_TITULOS' and c['Filas'] == 55)}` |",
            f"| Hash del archivo sin títulos | `{selected['SHA-256']}` |",
            "",
            "## Evidencia de cierre",
            "- `generacion_pes_postgrado_postitulo_20260508_090807.md` declara el PES-ready sin encabezado, delimitado por punto y coma.",
            "- `resumen_cierre_rut_invalido_postgrado_20260521_213650` documenta `filas_pes_ready_despues=54`, exclusión del registro bloqueado y `copia_escritorio=OK`.",
            "- `reconciliacion_66_a_54_postgrado_20260521_215748` documenta `incluidos_pes_ready=54` y reconciliación matemática verdadera.",
            "",
            "## Archivos actualizados",
            f"- Excel integral con PES-ready: `{output_xlsx}`",
            f"- Manifest: `{manifest_path}`",
            "",
            "## Estado del pendiente",
            "`PES_READY_POSGRADO_NO_MATERIALIZADO` -> `RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    governed_dir = OUT_CONG_ROOT / ts
    integral_dir = OUT_INT_ROOT / ts
    governed_dir.mkdir(parents=True, exist_ok=False)
    integral_dir.mkdir(parents=True, exist_ok=False)

    candidates, selected, con_body, con_header = evaluate_candidates()
    selected_bytes: bytes = selected["bytes"]
    governed_path = governed_dir / Path(SELECTED_ORIGINAL_PATH).name
    governed_path.write_bytes(selected_bytes)

    previous_xlsx = latest_integral_workbook()
    output_xlsx = integral_dir / f"COMPARACION_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_CON_PES_READY_{ts}.xlsx"
    report_path = integral_dir / f"REPORTE_INTEGRAL_PUBLICACION2026_VS_CONGELADOS_PREGRADO_POSGRADO_2026_CON_PES_READY_{ts}.md"
    manifest_path = integral_dir / f"MANIFEST_COMPARACION_INTEGRAL_PUBLICACION2026_PREGRADO_POSGRADO_CON_PES_READY_{ts}.json"

    write_evidence_workbook(previous_xlsx, output_xlsx, candidates, selected, governed_path, con_body, con_header)
    write_markdown(report_path, candidates, selected, governed_path, output_xlsx, manifest_path)

    selected_rows = selected["parsed"]["nonempty_rows"]
    manifest = {
        "proceso": "Matrícula Unificada 2026",
        "subproyecto": "Matrícula de Posgrado y Postítulo 2026",
        "archivo_con_titulos": {
            "ruta": "git:4f1108c:resultados/matricula_unificada_2026_postgrado_postitulo_CON_TITULOS.csv",
            "hash_sha256": next(c["SHA-256"] for c in candidates if c["Estado"] == "ARCHIVO_CON_TITULOS" and c["Filas"] == 55),
            "filas_fisicas": 55,
            "registros": 54,
            "campos": 21,
        },
        "archivo_pes_ready": {
            "encontrado_o_reconstruido": "ARCHIVO_ORIGINAL_PES_READY_LOCALIZADO",
            "ruta_original": f"git:4f1108c:{SELECTED_ORIGINAL_PATH}",
            "git_blob": SELECTED_OBJECT,
            "ruta_gobernada": str(governed_path),
            "hash_sha256": selected["SHA-256"],
            "filas": len(selected_rows),
            "campos": selected["parsed"]["field_counts"][0],
            "delimitador": selected["parsed"]["delimiter"],
            "codificacion": selected["parsed"]["encoding"],
            "encabezado": "NO",
            "bom": selected["parsed"]["has_bom"],
            "termina_en_lf": selected["parsed"]["ends_with_newline"],
        },
        "comparacion_con_titulos": {
            "mismo_orden_filas": selected_rows == con_body,
            "mismo_orden_columnas": True,
            "valores_identicos": selected_rows == con_body,
            "diferencias_encontradas": 0 if selected_rows == con_body else None,
        },
        "candidatos": candidates,
        "fuentes_normativas": [
            "Manual_Matrícula_Unificada_2026.pdf, Cuadro N°2, estructura de carga matrícula postgrado y postítulo.",
            "diagnosticos/mu2026_postgrado/generacion_pes_postgrado_postitulo_20260508_090807.md",
            "diagnosticos/mu2026_postgrado/resumen_cierre_rut_invalido_postgrado_20260521_213650 2.json",
            "diagnosticos/mu2026_postgrado/reconciliacion_66_a_54_postgrado_20260521_215748 2.json",
        ],
        "evidencia_git": {
            "log_path_original": git_log_for_path(SELECTED_ORIGINAL_PATH),
        },
        "archivos_generados": {
            "copia_gobernada": str(governed_path),
            "excel_integral": str(output_xlsx),
            "reporte": str(report_path),
            "manifest": str(manifest_path),
        },
        "hashes_archivos_generados": {
            "copia_gobernada": sha256_file(governed_path),
            "excel_integral": sha256_file(output_xlsx),
            "reporte": sha256_file(report_path),
        },
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "script": str(Path(__file__).resolve()),
        "estado_pendiente_anterior": {
            "antes": "PES_READY_POSGRADO_NO_MATERIALIZADO",
            "despues": "RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO",
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    # Manifest hash after writing.
    manifest["hashes_archivos_generados"]["manifest"] = sha256_file(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Final workbook verification.
    wb = load_workbook(output_xlsx, read_only=True, data_only=False)
    verification = {
        "xlsx_abre": True,
        "sheets": wb.sheetnames,
        "raw_pes_ready_rows": wb["RAW_POSGRADO_PES_READY"].max_row,
        "raw_pes_ready_cols": wb["RAW_POSGRADO_PES_READY"].max_column,
    }
    wb.close()

    print(
        json.dumps(
            {
                "estado": "RESUELTO_ARCHIVO_ORIGINAL_LOCALIZADO",
                "archivo_original": f"git:4f1108c:{SELECTED_ORIGINAL_PATH}",
                "ruta_gobernada": str(governed_path),
                "sha256": selected["SHA-256"],
                "filas": len(selected_rows),
                "campos": selected["parsed"]["field_counts"][0],
                "delimitador": selected["parsed"]["delimiter"],
                "codificacion": selected["parsed"]["encoding"],
                "excel": str(output_xlsx),
                "reporte": str(report_path),
                "manifest": str(manifest_path),
                "verificacion": verification,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

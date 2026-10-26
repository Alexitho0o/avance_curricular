"""Project the October 6047 report without changing any retained value.

This is a preparation and audit, not a PES submission or acceptance record.
Run with the bundled Python (pypdf is required for the manual schema check).
"""

import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
RUN = "etapa1_octubre_20261020"
DOWNLOADS = Path.home() / "Downloads"
SOURCE = DOWNLOADS / "reporte_dinamico_6047_2026-10-20_09:05:04.csv"
MANUAL = DOWNLOADS / "Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf"
OFFICE = DOWNLOADS / "Ord.  5669.pdf"
RAW = ROOT / "00_fuentes_originales" / RUN
AUDIT = ROOT / "06_validaciones" / RUN
GOV = ROOT / "11_gobernanza" / RUN
DRAFT = ROOT / "07_resultados" / "borradores_prueba_no_oficiales" / RUN
NAME = "BORRADOR_NO_CARGAR_OFERTA_2027_ETAPA1_OCTUBRE_17467_20261020.csv"

# A-AV, October 2026 manual, pages 21-28. This is not the August manual.
FIELDS = """COD_SEDE NOMBRE_SEDE COD_CARRERA NOMBRE_CARRERA MODALIDAD
COD_JORNADA VERSION COD_TIPO_PLAN_CARRERA CARACTERISTICAS_TIPO_PLAN
DURACION_ESTUDIOS DURACION_TITULACION DURACION_TOTAL REGIMEN DURACION_REGIMEN
NOMBRE_TITULO COD_NIVEL_GLOBAL COD_NIVEL_CARRERA ANIO_INICIO ACREDITACION
REQUISITO_INGRESO SEMESTRES_RECONOCIDOS AREA_ACTUAL AREA_ADMIN_DERECHO
AREA_AGRI_SILVI_PESCA_VET AREA_ARTES_HUMANIDADES AREA_CIENCIAS_NAT_MAT_ESTAD
AREA_CS_SOCIAL_PERIODISMO_INFO AREA_EDUCACION AREA_INGE_INDUSTRIA_CONSTRUC
AREA_SALUD_BIENESTAR AREA_SERVICIOS AREA_TECNO_INFO_COMUNICA
VACANTES_PRIMER_SEMESTRE VACANTES_SEGUNDO_SEMESTRE FECHA_ADMISION_INICIAL
ENLACE_INFO_PROGRAMA LICENCIA_ENS_MEDIA NOTAS_ENS_MEDIA PROMEDIO_MIN_ENS_MEDIA
RECONOCIMIENTOS_APREN_PREVIOS EXPERIENCIA_LABORAL MAIL_DIFUSION_CARRERA
FORMATO_VALOR VALOR_MATRICULA_ANUAL COSTO_TITULACION VALOR_CERTIFICADO_DIPLOMA
ARANCEL_ANUAL VIGENCIA_CARRERA""".split()
OMITTED = {"CODIGO_IES_NUM", "CANTIDAD_MATRICULA_DFE", "CANTIDAD_BENEFICIO_DFE"}
KEY = ["COD_SEDE", "COD_CARRERA", "MODALIDAD", "COD_JORNADA", "VERSION"]
FINANCE = ["VALOR_MATRICULA_ANUAL", "COSTO_TITULACION", "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(f"Existing different content; preserve it: {path}")
    else:
        path.write_bytes(data)


def tsv(path, rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, delimiter="\t", lineterminator="\n").writerows(rows)
    write_once(path, stream.getvalue().encode("utf-8"))


def main():
    original_hashes = {p: sha(p) for p in (SOURCE, MANUAL, OFFICE)}
    raw = SOURCE.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="strict")
        encoding = "cp1252"
    assert text.encode(encoding) == raw, "Input decoding must round-trip exactly"
    records = list(csv.reader(io.StringIO(text, newline=""), delimiter=";", strict=True))
    header, source_rows = records[0], records[1:]
    assert len(header) == 51 and len(header) == len(set(header))
    assert all(len(row) == 51 for row in source_rows)
    assert [c for c in header if c not in OMITTED] == FIELDS
    assert len(FIELDS) == 48

    pages = PdfReader(MANUAL).pages
    page_texts = {i: pages[i - 1].extract_text() for i in range(21, 29)}
    extracted = []
    for i, content in page_texts.items():
        extracted.extend(re.findall(r"^\s*(?:[A-Z]|A[A-V])\s+([A-Z][A-Z_]+)\b", content, re.MULTILINE))
    assert extracted == FIELDS, "The October manual's ordered schema must match"

    rows = [dict(zip(header, row)) for row in source_rows]
    assert {r["CODIGO_IES_NUM"] for r in rows} == {"162"}
    keys = [tuple(r[k] for k in KEY) for r in rows]
    assert len(keys) == len(set(keys)), "Duplicate program keys"
    projected = [[r[c] for c in FIELDS] for r in rows]

    findings = []
    def finding(i, r, c, rule, page):
        findings.append([i, i + 1, "|".join(r[k] for k in KEY), r["NOMBRE_CARRERA"], c, r[c], rule, page])

    domains = {
        "MODALIDAD": {"1", "2", "3"}, "COD_JORNADA": set("12345"),
        "COD_TIPO_PLAN_CARRERA": set("123"), "REGIMEN": set("1234"),
        "COD_NIVEL_GLOBAL": {"1", "3"}, "COD_NIVEL_CARRERA": set("0123456"),
        "ACREDITACION": set("123"), "REQUISITO_INGRESO": set("123456"),
        "AREA_ACTUAL": {str(n) for n in range(1, 11)},
        "FORMATO_VALOR": {"1", "2"}, "VIGENCIA_CARRERA": set("123"),
        **{c: {"0", "1"} for c in FIELDS[22:32]},
    }
    numeric = set(FIELDS[:34]) - {
        "NOMBRE_SEDE", "NOMBRE_CARRERA", "CARACTERISTICAS_TIPO_PLAN", "NOMBRE_TITULO"
    }
    combinations = {("1", "1"), ("1", "2"), ("1", "5"), ("2", "1"),
                    ("2", "2"), ("2", "3"), ("2", "5"), ("3", "4")}
    for i, r in enumerate(rows, 1):
        for c in FIELDS[:34] + FIELDS[42:]:
            if r[c] == "":
                finding(i, r, c, "Campo obligatorio vacio en precarga; no imputado", "27-28" if c in FINANCE else "21-28")
        for c, allowed in domains.items():
            if r[c] not in allowed:
                finding(i, r, c, "Fuera de dominio", "21-28")
        for c in numeric:
            if not re.fullmatch(r"[0-9]+", r[c]):
                finding(i, r, c, "Se exige numero entero", "21-26")
        for c in FINANCE:
            if r[c]:
                try:
                    assert Decimal(r[c].replace(",", ".")).is_finite()
                except (InvalidOperation, AssertionError):
                    finding(i, r, c, "Valor no numerico", "27-28")
        if (r["MODALIDAD"], r["COD_JORNADA"]) not in combinations:
            finding(i, r, "COD_JORNADA", "Combinacion modalidad/jornada incompatible", "56")
        if (r["COD_NIVEL_GLOBAL"], r["COD_NIVEL_CARRERA"]) not in {("1", "1"), ("1", "2"), ("3", "5"), ("3", "6")}:
            finding(i, r, "COD_NIVEL_CARRERA", "Combinacion de nivel incompatible para IP", "57")
        de, dt, total = (int(r[c]) for c in ["DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL"])
        if not de <= total <= de + dt:
            finding(i, r, "DURACION_TOTAL", "DE <= DF <= DE + DT", "57")
        if de > 14:
            finding(i, r, "DURACION_ESTUDIOS", "Mayor a 14; consultar al encargado", "57")
        access = r["COD_NIVEL_GLOBAL"] == "1" and r["VIGENCIA_CARRERA"] == "1"
        for c in FIELDS[34:42]:
            if access and not r[c]:
                finding(i, r, c, "Obligatorio en pregrado Acceso vigencia 1", "26-27")
            if not access and r[c]:
                finding(i, r, c, "Grupo sin alumnos nuevos/postitulo: obligatorio vacio", "26-27")
        if access:
            if r["LICENCIA_ENS_MEDIA"] != "SI":
                finding(i, r, "LICENCIA_ENS_MEDIA", "Obligatorio SI", "26")
            for c in ["NOTAS_ENS_MEDIA", "RECONOCIMIENTOS_APREN_PREVIOS", "EXPERIENCIA_LABORAL"]:
                if r[c] not in {"SI", "NO"}:
                    finding(i, r, c, "Dominio SI/NO", "27")
            try:
                datetime.strptime(r["FECHA_ADMISION_INICIAL"], "%d/%m/%Y")
            except ValueError:
                finding(i, r, "FECHA_ADMISION_INICIAL", "Formato DD/MM/AAAA", "26")

    buffer = io.StringIO(newline="")
    csv.writer(buffer, delimiter=";", lineterminator="\n").writerows(projected)
    payload = buffer.getvalue().encode("utf-8")
    reread = list(csv.reader(io.StringIO(payload.decode("utf-8")), delimiter=";", strict=True))
    assert reread == projected
    differences = [sum(a[j] != b[j] for a, b in zip(projected, reread)) for j in range(48)]
    assert sum(differences) == 0

    # No final/released load is produced: the official precarga has mandatory gaps.
    assert findings, "Review this script's DRAFT status before using it with different inputs"
    output = DRAFT / NAME
    desktop = Path.home() / "Desktop" / NAME
    for p in (SOURCE, MANUAL, OFFICE):
        dest = RAW / p.name
        write_once(dest, p.read_bytes())
        assert sha(dest) == original_hashes[p]
    write_once(output, payload)
    write_once(desktop, payload)
    assert sha(output) == sha(desktop)

    tsv(AUDIT / "HALLAZGOS.tsv", [["fila_carga", "fila_csv_con_encabezado", "clave", "nombre_carrera", "campo", "valor", "hallazgo", "pagina_manual"]] + findings)
    tsv(AUDIT / "CONTROL_48_COLUMNAS.tsv", [["posicion_carga", "campo", "pagina_manual", "celdas_comparadas", "diferencias_con_fuente"]] + [
        [j + 1, c, next(i for i, t in page_texts.items() if c in t), len(rows), differences[j]] for j, c in enumerate(FIELDS)
    ])
    docs = [RAW / p.name for p in (SOURCE, MANUAL, OFFICE)]
    manifest = {
        "fecha_ejecucion": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        "proceso": "Oferta Academica 2027, proceso 2026, segundo proceso octubre",
        "etapa": 1, "reporte_inicial": 6047, "id_carga": 17467,
        "estado": "BORRADOR_NO_CARGAR_PENDIENTE_VALIDACION",
        "confirmacion_usuario": "Docencia confirmo que no hay cambios, comunicada por el usuario en esta conversacion; no se adjunto correo de confirmacion.",
        "fuentes": [{"original": str(p), "copia_proyecto": str(d), "sha256": sha(d)} for p, d in zip((SOURCE, MANUAL, OFFICE), docs)],
        "script": {"ruta": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))},
        "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=REPO, text=True).strip(),
        "git_head_preparacion": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "transformacion": {"encoding_origen": encoding, "encoding_salida": "utf-8 sin BOM", "separador_salida": ";", "columnas_retiradas": sorted(OMITTED), "encabezados_salida": False, "filtrado_filas": False, "celdas_modificadas": 0, "imputaciones": 0},
        "controles": {"filas": len(rows), "columnas_origen": 51, "columnas_salida": 48, "celdas_conservadas": len(rows) * 48, "duplicados_clave": 0, "total_vacantes": sum(int(r[c]) for r in rows for c in FIELDS[32:34]), "vigencias": dict(Counter(r["VIGENCIA_CARRERA"] for r in rows)), "niveles": dict(Counter(r["COD_NIVEL_GLOBAL"] for r in rows)), "hallazgos": len(findings), "programas_con_hallazgos": len({r[0] for r in findings})},
        "salidas": [{"ruta": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in (output, desktop)],
        "pendientes": ["Resolver vacios financieros obligatorios de diplomados con Docencia/Finanzas o confirmar excepcion escrita de SIES.", "88 fechas de admision usan DD-MM-AAAA; el manual p26 exige DD/MM/AAAA. Conversion de formato pendiente en una version liberada.", "Confirmar separador y restricciones tecnicas en estructura actual ID 17467: manual p14 dice delimitado por comas, reporte usa punto y coma. El borrador preserva separador observado, no certifica su aceptacion.", "Validacion integral de reglas, largos, nombre exigido y catalogos PES pendiente; controles ejecutados no equivalen a aceptacion.", "No se realizo carga PES ni commit/push. CSV ignorado por .gitignore; respaldo local reproducible."],
    }
    manifest_path = GOV / "MANIFIESTO_PREPARACION.json"
    if not manifest_path.exists():
        write_once(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    note = f"""# Etapa 1 de octubre: borrador sin cambios institucionales

Estado: BORRADOR NO CARGAR. No es una carga aceptada ni una version congelada en PES.
Destino previsto: Oferta Academica Vigente Editada TP, ID 17467. Cierre: 23-10-2026.
Confirmacion de Docencia transmitida por el usuario: no hay cambios. No se adjunto correo.

Se conservaron {len(rows)} programas y sus 48 campos de carga, sin modificar valores,
normalizar nombres, completar vacios ni eliminar registros. Se retiraron unicamente
el encabezado y CODIGO_IES_NUM, CANTIDAD_MATRICULA_DFE y CANTIDAD_BENEFICIO_DFE
(manual octubre 2026, p. 14). Se convirtio cp1252 a UTF-8 sin perdida de caracteres.
La secuencia A-AV coincide con el manual pp. 21-28. Se conservan 5.461 vacantes.

## Pendientes que impiden liberar la carga

Los 21 diplomados traen vacios VALOR_MATRICULA_ANUAL, COSTO_TITULACION,
VALOR_CERTIFICADO_DIPLOMA y ARANCEL_ANUAL: 84 celdas. El manual pp. 27-28
los marca obligatorios para postitulos. Esto viene en la precarga de SIES; no
es una modificacion de Docencia. No se rellenaron con 0 ni -1 por criterio propio.
Es necesario completar con datos autorizados o confirmar con SIES que estos vacios
se admiten en Etapa 1. No se afirma que PES ya los haya rechazado.

Ademas, 88 fechas FECHA_ADMISION_INICIAL vienen como DD-MM-AAAA; el manual
p. 26 pide DD/MM/AAAA. Se conserva el original en este borrador. La conversion
de formato debe registrarse en la version liberada. Total: 172 hallazgos sobre
109 programas (84 vacios financieros y 88 formatos de fecha).

El manual p. 14 menciona CSV delimitado por comas; el reporte usa punto y coma.
El borrador conserva punto y coma. Confirmar la estructura vigente ID 17467 en PES
antes de liberar el archivo, incluidos largos y nombre requerido.

## Trazabilidad

Originales completos: {RAW}
Detalle fila/campo: {AUDIT / 'HALLAZGOS.tsv'}
Control de 7.728 celdas: {AUDIT / 'CONTROL_48_COLUMNAS.tsv'}
Manifiesto y SHA-256: {manifest_path}
Copia local del proyecto: {output}
Copia identica del Escritorio: {desktop}

Los CSV estan ignorados por Git. Respaldo local reproducible; no se hizo commit ni push.
Reanudacion: resolver pendientes, validar la estructura actual, generar una nueva
version liberada; tras carga comprobar Finalizado, descargar editada y luego 6048.
"""
    write_once(GOV / "ESTADO_Y_REANUDACION.md", note.encode("utf-8"))
    write_once(Path.home() / "Desktop" / "LEER_ANTES_DE_CARGAR_OFERTA_2027_ETAPA1_OCTUBRE_20261020.txt", note.encode("utf-8"))
    for p, expected in original_hashes.items():
        assert sha(p) == expected, f"Original changed: {p}"
    print(json.dumps({"estado": manifest["estado"], **manifest["controles"], "desktop": str(desktop), "proyecto": str(output), "sha256": sha(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

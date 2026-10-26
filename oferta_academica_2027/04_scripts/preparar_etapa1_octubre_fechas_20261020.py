"""Correct date serialization only; preserve unsupported financial blanks."""

import csv
import hashlib
import io
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from preparar_etapa1_octubre_20261020 import FIELDS, FINANCE, KEY, OMITTED, ROOT, write_once, tsv


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    run = "etapa1_octubre_20261020"
    source = ROOT / "00_fuentes_originales" / run / "reporte_dinamico_6047_2026-10-20_09:05:04.csv"
    manual = source.parent / "Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf"
    initial = digest(source)
    parsed = list(csv.reader(io.StringIO(source.read_bytes().decode("cp1252")), delimiter=";", strict=True))
    header, rows = parsed[0], parsed[1:]
    assert len(rows) == 161 and all(len(r) == 51 for r in rows)
    assert [c for c in header if c not in OMITTED] == FIELDS
    idx = {c: i for i, c in enumerate(header)}
    output_rows = []
    changes = []
    empty_financials = []
    for line, r in enumerate(rows, 1):
        projected = [r[idx[c]] for c in FIELDS]
        field = "FECHA_ADMISION_INICIAL"
        original = r[idx[field]]
        if original:
            date = datetime.strptime(original, "%d-%m-%Y")
            formatted = date.strftime("%d/%m/%Y")
            assert datetime.strptime(formatted, "%d/%m/%Y") == date
            projected[FIELDS.index(field)] = formatted
            if original != formatted:
                changes.append([line, line + 1, "|".join(r[idx[k]] for k in KEY), field, original, formatted, "Solo formato; misma fecha. Manual p.26"])
        for c in FINANCE:
            if r[idx[c]] == "":
                assert r[idx["COD_NIVEL_GLOBAL"]] == "3" and r[idx["COD_NIVEL_CARRERA"]] == "5"
                empty_financials.append([line, line + 1, "|".join(r[idx[k]] for k in KEY), r[idx["NOMBRE_CARRERA"]], c, "", "Sin codigo sustituto confirmado para este campo y grupo"])
        for j, c in enumerate(FIELDS):
            if c != field:
                assert projected[j] == r[idx[c]]
        output_rows.append(projected)
    assert len(changes) == 88 and len(empty_financials) == 84
    assert len({tuple(r[FIELDS.index(k)] for k in KEY) for r in output_rows}) == 161
    assert sum(int(r[FIELDS.index(c)]) for r in output_rows for c in ["VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE"]) == 5461
    stream = io.StringIO(newline="")
    csv.writer(stream, delimiter=";", lineterminator="\n").writerows(output_rows)
    payload = stream.getvalue().encode("utf-8")
    assert list(csv.reader(io.StringIO(payload.decode("utf-8")), delimiter=";")) == output_rows

    name = "PENDIENTE_NO_CARGAR_OFERTA_2027_ETAPA1_17467_FECHAS_CORREGIDAS_20261020.csv"
    output = ROOT / "07_resultados" / "borradores_prueba_no_oficiales" / run / name
    desktop = Path.home() / "Desktop" / name
    audit = ROOT / "06_validaciones" / run / "v02_fechas"
    gov = ROOT / "11_gobernanza" / run / "v02_fechas"
    write_once(output, payload)
    write_once(desktop, payload)
    assert digest(output) == digest(desktop) and digest(source) == initial
    tsv(audit / "CAMBIOS_FECHAS.tsv", [["fila_carga", "fila_reporte", "clave", "campo", "antes", "despues", "respaldo"]] + changes)
    tsv(audit / "PENDIENTES_FINANCIEROS.tsv", [["fila_carga", "fila_reporte", "clave", "programa", "campo", "valor_preservado", "motivo"]] + empty_financials)
    note = """# Version 02: fechas corregidas, pendiente de liberacion

Fecha: 20-10-2026. Segundo proceso Oferta Academica 2027, Etapa 1, ID 17467.
No es una carga aceptada ni un archivo liberado para subir.

Se mantienen 161 programas, 48 columnas y 5.461 vacantes. Se retiran solamente
el encabezado y las tres columnas de consulta indicadas en el manual p.14.
Se convierten 88 fechas de DD-MM-AAAA a DD/MM/AAAA (p.26), sin cambiar el dia.
Se mantiene punto y coma del reporte de origen y se exporta en UTF-8 sin BOM.
La confirmacion de Docencia sin cambios fue transmitida por el usuario.

Los 84 vacios de los 21 diplomados siguen intactos. No se uso 9, -1 ni 0:
el manual p.5 menciona Sin Informacion (-1) para programas vigentes con alumnos
nuevos informados en el primer proceso; no especifica en ese pasaje un valor
sustituto para los cuatro campos de los diplomados en la carga de octubre.
Las pp.27-28 los califican como obligatorios; las pp.42-45 asignan a Etapa 3
la definicion de esos valores y explicitan que alli no pueden quedar vacios.
No se extrapola la excepcion de pregrado a postitulos ni a costos diferentes.

Antes de liberar: confirmar con la estructura vigente de ID 17467 o SIES la
aceptacion de vacios o el codigo permitido por cada campo para los diplomados;
alternativamente incorporar montos autorizados. Confirmar tambien el separador:
la p.14 dice delimitado por comas, mientras la precarga utiliza punto y coma.
Sin confirmacion no se afirma aceptacion de esta version por PES.

La copia de Escritorio y la del proyecto tienen el mismo SHA-256. Entradas,
procedimiento, cambios y pendientes quedan registrados. Respaldo local;
los CSV estan ignorados por Git. No hubo carga PES, commit ni push.
"""
    write_once(gov / "ESTADO.md", note.encode("utf-8"))
    manifest = {
        "fecha": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        "estado": "FECHAS_CORREGIDAS_PENDIENTE_LIBERACION",
        "source": {"path": str(source), "sha256": initial},
        "manual": {"path": str(manual), "sha256": digest(manual)},
        "script": {"path": str(Path(__file__).resolve()), "sha256": digest(Path(__file__))},
        "helper": {"path": str(Path(__file__).with_name("preparar_etapa1_octubre_20261020.py")), "sha256": digest(Path(__file__).with_name("preparar_etapa1_octubre_20261020.py"))},
        "controles": {"filas": 161, "columnas": 48, "cambios_formato_fecha": 88, "celdas_sin_cambios": 7640, "fechas_semanticamente_identicas": True, "otros_cambios": 0, "vacantes": 5461, "vacios_financieros_preservados": 84, "diplomados_pendientes": 21},
        "salidas": [{"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size} for p in [output, desktop]],
        "encoding": "utf-8 sin BOM", "separador": ";", "encabezados": False,
        "estado_git": "copia local, sin commit/push; CSV ignorado por reglas vigentes",
    }
    mp = gov / "MANIFIESTO.json"
    if not mp.exists():
        write_once(mp, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"estado": manifest["estado"], **manifest["controles"], "escritorio": str(desktop), "proyecto": str(output), "hash": digest(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Verify and publish the date-only derivative for a user-authorized PES test."""

import csv
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from preparar_etapa1_octubre_20261020 import FIELDS, FINANCE, OMITTED, ROOT, write_once


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    run = "etapa1_octubre_20261020"
    source = ROOT / "00_fuentes_originales" / run / "reporte_dinamico_6047_2026-10-20_09:05:04.csv"
    folder = ROOT / "07_resultados" / "borradores_prueba_no_oficiales" / run
    previous = folder / "PENDIENTE_NO_CARGAR_OFERTA_2027_ETAPA1_17467_FECHAS_CORREGIDAS_20261020.csv"
    source_hash = sha(source)
    rows = list(csv.reader(io.StringIO(source.read_bytes().decode("cp1252")), delimiter=";", strict=True))
    header, original = rows[0], rows[1:]
    assert [c for c in header if c not in OMITTED] == FIELDS
    projected = [[row[header.index(c)] for c in FIELDS] for row in original]
    data = previous.read_bytes()
    output = list(csv.reader(io.StringIO(data.decode("utf-8")), delimiter=";", strict=True))
    assert len(output) == len(original) == 161
    assert all(len(row) == len(FIELDS) == 48 for row in output)
    changes = 0
    for before, after in zip(projected, output):
        for j, field in enumerate(FIELDS):
            if before[j] != after[j]:
                assert field == "FECHA_ADMISION_INICIAL"
                date = datetime.strptime(before[j], "%d-%m-%Y")
                assert after[j] == date.strftime("%d/%m/%Y")
                changes += 1
    assert changes == 88
    blank_cells = sum(row[FIELDS.index(f)] == "" for row in output for f in FINANCE)
    assert blank_cells == 84
    vacancies = sum(int(row[FIELDS.index(f)]) for row in output for f in ("VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE"))
    assert vacancies == 5461
    name = "PRUEBA_PES_OFERTA_2027_ETAPA1_17467_20261020.csv"
    targets = [folder / name, Path.home() / "Desktop" / name]
    for target in targets:
        write_once(target, data)
        assert target.read_bytes() == data
    assert sha(source) == source_hash
    gov = ROOT / "11_gobernanza" / run / "v03_prueba_autorizada"
    note = """# Prueba PES autorizada por el usuario

Proceso 2026, Oferta Academica 2027, segundo proceso, Etapa 1, ID 17467.
El usuario solicita conservar los vacios de SIES y cambiar solo el formato
de fechas para probar la carga. Esta decision habilita una prueba; no modifica
las reglas del manual ni demuestra que PES admita los vacios financieros.

161 registros, 48 columnas, 5.461 vacantes. Solo 88 cambios DD-MM-AAAA a
DD/MM/AAAA. Se conservan las 84 celdas financieras vacias de 21 diplomados.
La proyeccion de columnas y retiro del encabezado son los mismos del derivado
v02; no se agrega ni elimina ningun registro. CSV UTF-8 sin BOM, punto y coma.

Esta version sustituye v02 para la prueba solicitada, sin borrar antecedentes.
No se ha subido a PES ni se ha confirmado su aceptacion. Pendiente registrar
resultado de carga y, si finaliza, conciliar contra reporte validado 6048 antes
de congelar como aceptado. Si falla, conservar los mensajes exactos de PES.
Se mantiene pendiente la comprobacion del separador con la estructura vigente.
Los importes de diplomados quedan pendientes para su tratamiento en Etapa 3.
Gobernanza local: no se realizo commit ni push; los CSV estan ignorados por Git.
"""
    write_once(gov / "ESTADO.md", note.encode("utf-8"))
    manifest = {
        "fecha": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        "estado": "PRUEBA_PES_AUTORIZADA_NO_CONFIRMADA",
        "autorizacion": "Conservar vacios SIES; corregir solo fechas; generar copias para probar PES.",
        "fuente": {"ruta": str(source), "sha256": source_hash},
        "derivado_previo": {"ruta": str(previous), "sha256": sha(previous)},
        "script": {"ruta": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))},
        "controles": {"filas": 161, "columnas": 48, "fechas_corregidas": changes, "otros_cambios_de_valor": 0, "vacios_financieros": blank_cells, "vacantes": vacancies},
        "salidas": [{"ruta": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in targets],
        "carga_pes": "No ejecutada; pendiente de resultado y conciliacion 6048",
    }
    if not (gov / "MANIFIESTO.json").exists():
        write_once(gov / "MANIFIESTO.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"estado": manifest["estado"], **manifest["controles"], "salidas": manifest["salidas"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

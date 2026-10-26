"""Remove exactly one terminal LF from the tested CSV; preserve every other byte."""

import csv
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from preparar_etapa1_octubre_20261020 import ROOT, write_once


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    run = "etapa1_octubre_20261020"
    folder = ROOT / "07_resultados" / "borradores_prueba_no_oficiales" / run
    source = folder / "PRUEBA_PES_OFERTA_2027_ETAPA1_17467_20261020.csv"
    error = Path.home() / "Downloads" / "20-10-2026_17-59-19_Oferta-Académica-Vigente-Editada-TP.csv.txt"
    original = source.read_bytes()
    evidence = error.read_bytes()
    assert original.endswith(b"\n") and not original.endswith((b"\n\n", b"\r\n"))
    corrected = original[:-1]
    assert corrected + b"\n" == original
    assert not corrected.endswith((b"\n", b"\r"))
    before = list(csv.reader(io.StringIO(original.decode("utf-8")), delimiter=";", strict=True))
    after = list(csv.reader(io.StringIO(corrected.decode("utf-8")), delimiter=";", strict=True))
    assert before == after and len(after) == 161
    assert all(len(row) == 48 for row in after)
    name = "PRUEBA_PES_OFERTA_2027_ETAPA1_17467_20261020_V04_SIN_SALTO_FINAL.csv"
    targets = [folder / name, Path.home() / "Desktop" / name]
    for target in targets:
        write_once(target, corrected)
        assert target.read_bytes() == corrected
    gov = ROOT / "11_gobernanza" / run / "v04_sin_salto_final"
    write_once(gov / error.name, evidence)
    note = """# Version 04: correccion de salto final

Oferta Academica 2027, proceso 2026, Etapa 1 de octubre, ID 17467.
Autorizacion: eliminar solo el salto de linea final para reintentar en PES.
El reporte de PES informa linea 162 vacia, 1 campo en lugar de 48 y COD_SEDE
invalido. Se conserva el reporte original como evidencia, sin modificarlo.

Cambio unico: retiro del ultimo byte LF (0A). Los otros 45.257 bytes permanecen
identicos; los 161 registros y sus 48 campos son iguales antes y despues.
No se modifican fechas, valores, vacios, delimitador, codificacion ni registros.
Se conservan los antecedentes y versiones previas. Usar V04 para el reintento.

Estado: pendiente de nueva carga y resultado PES; no aceptada ni congelada.
La ausencia de otros errores en el reporte no acredita aceptacion definitiva.
Tras Finalizado, conciliar el reporte validado 6048 con la carga enviada.
Gobernanza local con hashes y script; no se realizo commit ni push.
"""
    write_once(gov / "ESTADO.md", note.encode("utf-8"))
    manifest = {
        "fecha": datetime.now(ZoneInfo("America/Santiago")).isoformat(),
        "estado": "CORREGIDO_SALTO_FINAL_PENDIENTE_REINTENTO_PES",
        "entrada": {"ruta": str(source), "sha256": digest(original), "bytes": len(original)},
        "evidencia_error": {"origen": str(error), "copia": str(gov / error.name), "sha256": digest(evidence)},
        "script": {"ruta": str(Path(__file__).resolve()), "sha256": digest(Path(__file__).read_bytes())},
        "cambio": {"byte_eliminado": "0A", "posicion_base_cero": len(original)-1, "otros_bytes_modificados": 0},
        "controles": {"filas": 161, "columnas": 48, "igualdad_celda_por_celda": True, "salto_final": False},
        "salidas": [{"ruta": str(p), "sha256": digest(p.read_bytes()), "bytes": p.stat().st_size} for p in targets],
    }
    if not (gov / "MANIFIESTO.json").exists():
        write_once(gov / "MANIFIESTO.json", (json.dumps(manifest, ensure_ascii=False, indent=2)+"\n").encode("utf-8"))
    assert source.read_bytes() == original and error.read_bytes() == evidence
    print(json.dumps({"controles": manifest["controles"], "salidas": manifest["salidas"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

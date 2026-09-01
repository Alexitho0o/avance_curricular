#!/usr/bin/env python3
"""Promueve la pre-carga de Etapa 3 a carga final aceptada en PES."""

from __future__ import annotations

import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGEN = (
    ROOT
    / "09_respaldo"
    / "cargas_congeladas"
    / "20260910_etapa3_preparada_carga_02"
    / "OFERTA_ACADEMICA_ARANCELES_2027_CARGA_02_CORREGIDA_SIN_TITULOS_20260910.csv"
)
DESTINO = ROOT / "09_respaldo" / "cargas_congeladas" / "20260910_etapa3_carga_final_aceptada_pes"
ARCHIVO_FINAL = DESTINO / ORIGEN.name
NOTA = ROOT / "11_gobernanza" / "NOTA_GOBERNANZA_CARGA_ACEPTADA_ETAPA3_20260910.md"
BLOQUEO = ROOT / "12_pendientes" / "REGISTRO_BLOQUEO_CARGA_ETAPA3_20260910.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not ORIGEN.is_file():
        raise FileNotFoundError(ORIGEN)

    with ORIGEN.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=";"))
    if len(rows) != 88 or any(len(row) != 13 for row in rows):
        raise ValueError("La pre-carga no conserva el control esperado de 88 filas y 13 columnas")
    if any(row[12] != "1" for row in rows):
        raise ValueError("La pre-carga contiene registros distintos de vigencia 1")

    DESTINO.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ORIGEN, ARCHIVO_FINAL)
    huella = sha256(ARCHIVO_FINAL)
    if huella != sha256(ORIGEN):
        raise ValueError("La copia final no conserva la huella de la pre-carga")

    with (DESTINO / "MANIFIESTO_CARGA_FINAL_ACEPTADA_ETAPA3_20260910.tsv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "clasificacion", "archivo", "filas", "columnas", "sha256", "estado_pes",
            "fuente_confirmacion", "fecha_confirmacion",
        ])
        writer.writerow([
            "carga_final_congelada_etapa3", ARCHIVO_FINAL.name, 88, 13, huella,
            "CARGADA_OK", "confirmacion_usuario_en_conversacion", "2026-09-10",
        ])

    (DESTINO / "README_GOBERNANZA_CARGA_FINAL_ETAPA3_20260910.md").write_text(
        "# Carga final congelada Etapa 3\n\n"
        "- Proceso: SIES Oferta Academica-Acceso 2027.\n"
        "- Etapa: 3 - Definicion de Arancel.\n"
        "- Fecha informada de carga: 10-09-2026.\n"
        "- Estado PES informado: `CARGADA_OK`.\n"
        "- Registros: 88.\n"
        "- Columnas: 13, sin encabezado.\n"
        "- Universo: solo vigencia 1.\n"
        f"- SHA-256: `{huella}`.\n"
        "- Fuente de confirmacion: declaracion del usuario en la conversacion del proyecto.\n\n"
        "La huella coincide exactamente con la pre-carga congelada. No se modifico el archivo durante la "
        "promocion. Si PES entrega un comprobante o reporte posterior, debe incorporarse como evidencia "
        "adicional sin reemplazar esta copia.\n",
        encoding="utf-8",
    )

    NOTA.write_text(
        "# Nota de gobernanza - Carga aceptada Etapa 3\n\n"
        "El usuario confirmo el 10-09-2026 que PES acepto correctamente la segunda carga de Etapa 3. "
        "Se promovio la pre-carga congelada, sin cambios, a carga final aceptada.\n\n"
        f"- Archivo: `{ARCHIVO_FINAL.relative_to(ROOT)}`.\n"
        f"- SHA-256: `{huella}`.\n"
        "- Estado: `CARGADA_OK_CONFIRMADA_POR_USUARIO`.\n"
        "- Evidencia tecnica de plataforma: no adjunta al momento de esta confirmacion.\n",
        encoding="utf-8",
    )

    BLOQUEO.write_text(
        "# Bloqueo de carga Etapa 3 - 10-09-2026\n\n"
        "Estado: `RESUELTO`.\n\n"
        "Resolucion: PES acepto la carga corregida de 88 filas y 13 columnas, segun confirmacion del usuario.\n\n"
        f"Carga final congelada: `{ARCHIVO_FINAL.relative_to(ROOT)}`.\n\n"
        f"SHA-256: `{huella}`.\n",
        encoding="utf-8",
    )

    print("estado=CARGADA_OK_CONFIRMADA_POR_USUARIO")
    print("filas=88 columnas=13 vigencia=1")
    print(f"sha256={huella}")
    print(f"congelado={ARCHIVO_FINAL.relative_to(ROOT)}")
    print(f"fecha_registro={datetime.now().astimezone().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()

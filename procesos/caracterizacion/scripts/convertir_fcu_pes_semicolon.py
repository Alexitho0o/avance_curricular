from pathlib import Path
import csv
from collections import Counter

desktop = Path("/Users/alexi/Desktop")

candidatos = sorted(
    desktop.glob("FCU_2026_CARGA_2026_P1_*_LISTO_SIN_TITULOS.csv"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

if not candidatos:
    raise SystemExit("ERROR: No se encontró archivo FCU LISTO_SIN_TITULOS en Desktop.")

src = candidatos[0]
dst = src.with_name(src.stem + "_PES_SEMICOLON.csv")

text = src.read_text(encoding="utf-8-sig", errors="replace")
lineas = text.splitlines()

rows = list(csv.reader(lineas, delimiter=","))

conteo_origen = Counter(len(r) for r in rows)
if conteo_origen != Counter({195: len(rows)}):
    raise SystemExit(f"ERROR: archivo origen no tiene 195 campos por fila con coma: {dict(conteo_origen)}")

with dst.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(
        f,
        delimiter=";",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    writer.writerows(rows)

text_out = dst.read_text(encoding="utf-8", errors="replace")
lineas_out = text_out.splitlines()

rows_semicolon = list(csv.reader(lineas_out, delimiter=";"))
rows_comma = list(csv.reader(lineas_out, delimiter=","))

conteo_semicolon = Counter(len(r) for r in rows_semicolon)
conteo_comma = Counter(len(r) for r in rows_comma)

print("ORIGEN:", src)
print("SALIDA:", dst)
print("filas:", len(rows_semicolon))
print("auditoria_origen_coma:", dict(conteo_origen))
print("auditoria_salida_semicolon:", dict(conteo_semicolon))
print("auditoria_salida_coma:", dict(conteo_comma))
print("ultima_linea_vacia:", text_out.endswith("\n\n"))

if conteo_semicolon != Counter({195: len(rows_semicolon)}):
    raise SystemExit("ERROR: salida semicolon no quedó con 195 campos por fila.")

if any(len(r) != 195 for r in rows_semicolon):
    raise SystemExit("ERROR: hay filas con estructura distinta de 195 campos.")

print("OK_PES_SEMICOLON_LISTO_PARA_SUBIR")

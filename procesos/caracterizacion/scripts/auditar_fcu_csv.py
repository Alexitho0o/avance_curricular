import csv
import pathlib
import re
import collections

candidatos = sorted(
    pathlib.Path("/Users/alexi/Desktop").glob("FCU_2026_CARGA_2026_P1_*_LISTO_SIN_TITULOS.csv"),
    key=lambda p: p.stat().st_mtime,
)

if not candidatos:
    raise SystemExit("No se encontró LISTO_SIN_TITULOS en Desktop.")

p = candidatos[-1]
lineas = p.read_bytes().decode("utf-8-sig", errors="replace").splitlines()

print("archivo:", p)
print("filas_fisicas:", len(lineas))
print("ultima_linea_vacia:", bool(lineas and lineas[-1].strip() == ""))

for sep in [",", ";"]:
    rows_sep = list(csv.reader(lineas, delimiter=sep))
    print("sep", repr(sep), collections.Counter(len(r) for r in rows_sep).most_common(5))

rows = list(csv.reader(lineas, delimiter=","))

bad_len = []
bad_reg = []
bad_com = []

for i, r in enumerate(rows, 1):
    if len(r) != 195:
        bad_len.append((i, len(r)))
        continue

    reg = r[28].strip()
    com = r[29].strip()

    if not re.fullmatch(r"\d+", reg or "") or not (1 <= int(reg) <= 16):
        bad_reg.append((i, reg, com))

    if not re.fullmatch(r"\d+", com or "") or not (1101 <= int(com) <= 16305):
        bad_com.append((i, com, reg))

print("filas_no_195_con_coma:", len(bad_len))
print("region_invalidas:", len(bad_reg))
print("comuna_invalidas:", len(bad_com))
print("primeros_region:", bad_reg[:20])
print("primeros_comuna:", bad_com[:20])

if bad_len:
    raise SystemExit("AUDITORIA_FALLA_ESTRUCTURA_195")

if bad_reg or bad_com:
    print("AUDITORIA_WARN_REGION_COMUNA_PENDIENTE")
else:
    print("AUDITORIA_OK_REGION_COMUNA")

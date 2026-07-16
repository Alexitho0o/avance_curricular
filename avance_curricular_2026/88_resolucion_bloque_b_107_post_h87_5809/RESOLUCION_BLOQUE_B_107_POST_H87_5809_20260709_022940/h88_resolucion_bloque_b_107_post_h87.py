from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import hashlib
import re
import unicodedata

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/88_resolucion_bloque_b_107_post_h87_5809"
    / f"RESOLUCION_BLOQUE_B_107_POST_H87_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H88_RESOLUCION_BLOQUE_B_107_POST_H87_5809_{ts}"

SALIDA.mkdir(parents=True, exist_ok=True)
ESCRITORIO.mkdir(parents=True, exist_ok=True)

def norm_txt(x):
    x = "" if pd.isna(x) else str(x)
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("ascii")
    x = x.upper().strip()
    x = re.sub(r"\s+", " ", x)
    return x

def norm_col(x):
    x = norm_txt(x)
    x = re.sub(r"[^A-Z0-9]+", "_", x)
    return re.sub(r"_+", "_", x).strip("_")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def ultimo(base, prefijo):
    dirs = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")
    return dirs[0]

def primer_excel(carpeta):
    excels = sorted(
        [p for p in carpeta.glob("*.xlsx") if not p.name.startswith("~$")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not excels:
        raise SystemExit(f"BLOQUEO: no hay Excel en {carpeta}")
    return excels[0]

def buscar_hoja(xlsx, patrones):
    xls = pd.ExcelFile(xlsx, engine="openpyxl")
    hojas = {h: norm_col(h) for h in xls.sheet_names}
    for patron in patrones:
        pn = norm_col(patron)
        for h, hn in hojas.items():
            if pn == hn or pn in hn:
                return h
    return None

def leer_excel(xlsx, patrones):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        xls = pd.ExcelFile(xlsx, engine="openpyxl")
        raise SystemExit(f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. Hojas: {xls.sheet_names}")
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def imprimir(titulo, df, n=None):
    print()
    print("=" * 170)
    print(titulo)
    print("=" * 170)
    if df.empty:
        print("(sin datos)")
        return
    if n is None:
        print(df.to_string(index=False))
    else:
        print(df.head(n).to_string(index=False))
        if len(df) > n:
            print(f"... mostrando {n} de {len(df)} filas")

print("[1/9] Localizando H87...", flush=True)

H87 = ultimo(
    RAIZ / "avance_curricular_2026/87_periodo5_y_bloque_b_107_post_h86_5809",
    "PERIODO5_Y_BLOQUE_B_107_POST_H86_5809_",
)
EX87 = primer_excel(H87)

print(f"   H87: {EX87}")

print("[2/9] Leyendo Bloque B 107...", flush=True)

dictamen_h87 = leer_excel(EX87, ["00_DICTAMEN_GLOBAL"])
resumen_h87 = leer_excel(EX87, ["01_RESUMEN_GLOBAL"])
periodo5_h87 = leer_excel(EX87, ["02_PERIODO5_RESUELTO"])
bloque_b = leer_excel(EX87, ["03_BLOQUE_B_107"])
resumen_b = leer_excel(EX87, ["04_RESUMEN_BLOQUE_B"])
control_h87 = leer_excel(EX87, ["06_CONTROL"])

if len(bloque_b) != 107:
    raise SystemExit(f"BLOQUEO: se esperaban 107 casos Bloque B, observado={len(bloque_b)}")

print("[3/9] Separando 100 CODCLI solo otro año y 7 pendientes restantes...", flush=True)

bloque_b["CLASIFICACION_NORM"] = bloque_b["CLASIFICACION_BLOQUE_B_H87"].map(norm_txt)

b1_100 = bloque_b[bloque_b["CLASIFICACION_NORM"].eq("B1_CODCLI_EXISTE_SOLO_OTRO_ANO")].copy()
pendientes_7 = bloque_b[~bloque_b["CLASIFICACION_NORM"].eq("B1_CODCLI_EXISTE_SOLO_OTRO_ANO")].copy()

if len(b1_100) != 100:
    raise SystemExit(f"BLOQUEO: se esperaban 100 B1 CODCLI solo otro año, observado={len(b1_100)}")
if len(pendientes_7) != 7:
    raise SystemExit(f"BLOQUEO: se esperaban 7 pendientes restantes, observado={len(pendientes_7)}")

print("[4/9] Aplicando cierre documental a 100 sin registros académicos 2025...", flush=True)

# Validación conservadora: FILAS_PROMEDIOS_2025 debe ser 0 en los 100.
if "FILAS_PROMEDIOS_2025" not in b1_100.columns:
    raise SystemExit("BLOQUEO: no existe columna FILAS_PROMEDIOS_2025 en Bloque B.")

b1_100["_FILAS_2025_NUM"] = pd.to_numeric(b1_100["FILAS_PROMEDIOS_2025"], errors="coerce").fillna(-1).astype(int)

no_cero = b1_100[b1_100["_FILAS_2025_NUM"] != 0]
if len(no_cero) > 0:
    raise SystemExit(
        f"BLOQUEO: hay {len(no_cero)} casos B1 con FILAS_PROMEDIOS_2025 distinto de 0. "
        "No se aplica cierre masivo."
    )

resueltos_b1 = b1_100.copy()
resueltos_b1["ESTADO_H88"] = "RESUELTO_SIN_ACTIVIDAD_ACADEMICA_2025"
resueltos_b1["TRATAMIENTO_H88"] = (
    "CODCLI con registros observados solo en años distintos de 2025 y FILAS_PROMEDIOS_2025=0. "
    "Se cierra documentalmente 16=NO, 17=NO, 18=0, 19=0."
)
resueltos_b1["NIVEL_RESPALDO_H88"] = "B_DATO_OBSERVADO_D_DECISION_INTERNA"
resueltos_b1["REGLA_OFICIAL_SIES"] = "NO"
resueltos_b1["16_H88"] = "NO"
resueltos_b1["17_H88"] = "NO"
resueltos_b1["18_H88"] = 0
resueltos_b1["19_H88"] = 0
resueltos_b1["CORRECCION_APLICADA"] = "NO"
resueltos_b1["GENERA_CARGA"] = "NO"

print("[5/9] Dejando 7 pendientes reales separados...", flush=True)

pendientes_7["ESTADO_H88"] = "PENDIENTE_REAL_POST_H88"
pendientes_7["TRATAMIENTO_H88"] = (
    "No se cierra en H88. Requiere mapeo/identidad o fuente complementaria."
)
pendientes_7["NIVEL_RESPALDO_H88"] = "B_DATO_OBSERVADO_E_PENDIENTE"
pendientes_7["CORRECCION_APLICADA"] = "NO"
pendientes_7["GENERA_CARGA"] = "NO"

resumen_pendientes_7 = (
    pendientes_7
    .groupby("CLASIFICACION_BLOQUE_B_H87", dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_estados_b1 = (
    resueltos_b1
    .groupby("ESTADOS_ACADEMICOS_OBSERVADOS", dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_anos_b1 = (
    resueltos_b1
    .groupby("ANOS_OBSERVADOS_PROMEDIOS", dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

print("[6/9] Consolidando estado global post H88...", flush=True)

total_resueltos_post_h88 = 316 + len(resueltos_b1)
total_pendientes_post_h88 = len(pendientes_7)

resumen_global = pd.DataFrame([
    {
        "BLOQUE": "RESUELTOS_POST_H87",
        "CASOS": 316,
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "OBSERVACION": "Acumulado hasta H87.",
    },
    {
        "BLOQUE": "H88_B1_CODCLI_SOLO_OTRO_ANO",
        "CASOS": len(resueltos_b1),
        "ESTADO": "RESUELTO_SIN_ACTIVIDAD_ACADEMICA_2025",
        "OBSERVACION": "Cierre documental 16=NO, 17=NO, 18=0, 19=0.",
    },
    {
        "BLOQUE": "PENDIENTES_REALES_POST_H88",
        "CASOS": len(pendientes_7),
        "ESTADO": "PENDIENTE_REAL",
        "OBSERVACION": "6 mapeo/identidad y 1 fuente complementaria.",
    },
    {
        "BLOQUE": "TOTAL_16_19_ORIGINAL",
        "CASOS": 423,
        "ESTADO": f"{total_resueltos_post_h88}_RESUELTOS_{total_pendientes_post_h88}_PENDIENTES",
        "OBSERVACION": "Control global 423.",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H88 resolución Bloque B 107 post H87 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "BLOQUE_B_ENTRADA": 107,
    "B1_CODCLI_SOLO_OTRO_ANO_RESUELTOS": len(resueltos_b1),
    "PENDIENTES_REALES_POST_H88": len(pendientes_7),
    "TOTAL_RESUELTOS_16_19_POST_H88": total_resueltos_post_h88,
    "TOTAL_PENDIENTES_16_19_POST_H88": total_pendientes_post_h88,
    "CRITERIO_B1": "CODCLI con registros solo en otros años y FILAS_PROMEDIOS_2025=0 => 16=NO,17=NO,18=0,19=0",
    "NIVEL_RESPALDO_B1": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
    "REGLA_OFICIAL_SIES": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "20_21_EVALUADO": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

control = pd.DataFrame([
    {"CONTROL": "Bloque B entrada", "RESULTADO": "OK", "OBSERVADO": len(bloque_b), "ESPERADO": 107},
    {"CONTROL": "B1 CODCLI solo otro año", "RESULTADO": "OK", "OBSERVADO": len(resueltos_b1), "ESPERADO": 100},
    {"CONTROL": "B1 con FILAS_PROMEDIOS_2025=0", "RESULTADO": "OK", "OBSERVADO": int((resueltos_b1["_FILAS_2025_NUM"] == 0).sum()), "ESPERADO": 100},
    {"CONTROL": "Pendientes reales", "RESULTADO": "OK", "OBSERVADO": len(pendientes_7), "ESPERADO": 7},
    {"CONTROL": "Total 423", "RESULTADO": "OK", "OBSERVADO": total_resueltos_post_h88 + total_pendientes_post_h88, "ESPERADO": 423},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[7/9] Escribiendo productos H88...", flush=True)

informe = f"""# Hito 88 — Resolución Bloque B 107 post H87

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado

Se resolvió documentalmente el subgrupo B1 del Bloque B:

- Bloque B entrada: 107
- B1 CODCLI solo otro año resueltos: {len(resueltos_b1)}
- Pendientes reales post H88: {len(pendientes_7)}

## Criterio aplicado

Cuando el caso fue clasificado como CODCLI_EXISTE_SOLO_OTRO_ANO y además FILAS_PROMEDIOS_2025=0, se cierra como sin actividad académica 2025 para columnas 16-19:

- 16=NO
- 17=NO
- 18=0
- 19=0

Nivel de respaldo: B dato observado + D decisión interna.
No corresponde presentarlo como regla oficial SIES.

## Estado consolidado

- Total resueltos 16-19 post H88: {total_resueltos_post_h88}
- Total pendientes 16-19 post H88: {total_pendientes_post_h88}

## Control

No se modifican fuentes originales.
No se genera archivo de carga.
No se genera SIES_READY.
Las columnas 20-21 siguen fuera de alcance.
"""

excel_out = SALIDA / "RESOLUCION_BLOQUE_B_107_POST_H87_5809.xlsx"
informe_out = SALIDA / "INFORME_RESOLUCION_BLOQUE_B_107_POST_H87_5809.md"
manifest_out = SALIDA / "manifest_resolucion_bloque_b_107_post_h87_5809.json"
script_out = SALIDA / "h88_resolucion_bloque_b_107_post_h87.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_global.to_excel(writer, sheet_name="01_RESUMEN_GLOBAL", index=False)
    resueltos_b1.to_excel(writer, sheet_name="02_RESUELTOS_B1_100", index=False)
    pendientes_7.to_excel(writer, sheet_name="03_PENDIENTES_REALES_7", index=False)
    resumen_pendientes_7.to_excel(writer, sheet_name="04_RESUMEN_PENDIENTES_7", index=False)
    resumen_estados_b1.to_excel(writer, sheet_name="05_ESTADOS_B1_100", index=False)
    resumen_anos_b1.to_excel(writer, sheet_name="06_ANOS_B1_100", index=False)
    control.to_excel(writer, sheet_name="07_CONTROL", index=False)
    bloque_b.to_excel(writer, sheet_name="08_BLOQUE_B_ORIGEN_107", index=False)
    resumen_b.to_excel(writer, sheet_name="09_RESUMEN_B_H87", index=False)
    pd.DataFrame([
        {"FUENTE": "H87", "RUTA": str(H87), "EXCEL": str(EX87), "SHA256": sha256(EX87)},
    ]).to_excel(writer, sheet_name="10_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 88,
        "bloque_b_entrada": 107,
        "b1_resueltos": len(resueltos_b1),
        "pendientes_reales_post_h88": len(pendientes_7),
        "total_resueltos_16_19_post_h88": total_resueltos_post_h88,
        "total_pendientes_16_19_post_h88": total_pendientes_post_h88,
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="11_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe_out.write_text(informe, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H88 resolución Bloque B 107 post H87 5809 columnas 16-19",
    "hito": 88,
    "bloque_b_entrada": 107,
    "b1_codcli_solo_otro_ano_resueltos": len(resueltos_b1),
    "pendientes_reales_post_h88": len(pendientes_7),
    "total_resueltos_16_19_post_h88": total_resueltos_post_h88,
    "total_pendientes_16_19_post_h88": total_pendientes_post_h88,
    "criterio_b1": "CODCLI solo otro año y FILAS_PROMEDIOS_2025=0 => 16=NO,17=NO,18=0,19=0",
    "nivel_respaldo": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
    "regla_oficial_sies": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h88_resolucion_bloque_b_107_post_h87.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/9] Validando productos...", flush=True)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[9/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 88 — RESOLUCIÓN BLOQUE B 107 POST H87 GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Bloque B entrada: 107")
print("B1 CODCLI solo otro año resueltos: 100")
print("Criterio B1: FILAS_PROMEDIOS_2025=0 => 16=NO,17=NO,18=0,19=0")
print("Nivel respaldo: B_DATO_OBSERVADO_D_DECISION_INTERNA")
print("Regla oficial SIES: NO")
print(f"Total resueltos 16-19 post H88: {total_resueltos_post_h88}")
print(f"Pendientes reales post H88: {total_pendientes_post_h88}")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN GLOBAL", resumen_global)
imprimir("RESUMEN PENDIENTES 7", resumen_pendientes_7)
imprimir("CONTROL", control)
imprimir("MUESTRA RESUELTOS B1 100", resueltos_b1, 30)
imprimir("PENDIENTES REALES 7", pendientes_7)

print()
print("=" * 170)
print("ARCHIVOS H88")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)

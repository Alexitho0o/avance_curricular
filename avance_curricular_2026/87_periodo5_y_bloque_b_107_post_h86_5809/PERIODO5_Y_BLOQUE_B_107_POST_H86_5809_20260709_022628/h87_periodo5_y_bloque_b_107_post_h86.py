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
    / "avance_curricular_2026/87_periodo5_y_bloque_b_107_post_h86_5809"
    / f"PERIODO5_Y_BLOQUE_B_107_POST_H86_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H87_PERIODO5_Y_BLOQUE_B_107_POST_H86_5809_{ts}"

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

print("[1/9] Localizando H86...", flush=True)

H86 = ultimo(
    RAIZ / "avance_curricular_2026/86_aplicacion_criterio_h77_periodo_157_h85_5809",
    "APLICACION_CRITERIO_H77_PERIODO_157_H85_5809_",
)
EX86 = primer_excel(H86)

print(f"   H86: {EX86}")

print("[2/9] Leyendo pendientes post H86...", flush=True)

dictamen_h86 = leer_excel(EX86, ["00_DICTAMEN_GLOBAL"])
resumen_h86 = leer_excel(EX86, ["01_RESUMEN_GLOBAL"])
resueltos_h86 = leer_excel(EX86, ["04_RESUELTOS_H86"])
pendientes_h86 = leer_excel(EX86, ["05_PENDIENTES_POST_H86"])
evidencia_h86 = leer_excel(EX86, ["07_EVIDENCIA_PERIODOS"])
control_h86 = leer_excel(EX86, ["08_CONTROL"])

if len(pendientes_h86) != 109:
    raise SystemExit(f"BLOQUEO: se esperaban 109 pendientes post H86, observado={len(pendientes_h86)}")

print("[3/9] Separando PERIODO 5 y Bloque B 107...", flush=True)

pendientes_h86["ESTADO_H86_NORM"] = pendientes_h86["ESTADO_H86"].map(norm_txt)
pendientes_h86["PERIODOS_H86_TXT"] = pendientes_h86.get("PERIODOS_H86", "").astype(str)

periodo5 = pendientes_h86[
    pendientes_h86["ESTADO_H86_NORM"].eq("NO_RESUELTO_PERIODO_FUERA_CRITERIO_H77")
].copy()

bloque_b_107 = pendientes_h86[
    pendientes_h86["ESTADO_H86_NORM"].eq("NO_RESUELTO_SIN_EVIDENCIA_2025_EN_H85")
].copy()

if len(periodo5) != 2:
    raise SystemExit(f"BLOQUEO: se esperaban 2 casos PERIODO 5, observado={len(periodo5)}")
if len(bloque_b_107) != 107:
    raise SystemExit(f"BLOQUEO: se esperaban 107 casos Bloque B, observado={len(bloque_b_107)}")

print("[4/9] Resolviendo 2 casos PERIODO 5 con decisión interna extendida...", flush=True)

periodo5_resuelto = periodo5.copy()

periodo5_resuelto["CRITERIO_H87"] = (
    "Decisión interna proyecto: antecedente H82 nombró PERIODO 5 como semestre 1; "
    "usuario instruye aplicar ese tratamiento a estos 2 casos post H86."
)
periodo5_resuelto["NIVEL_RESPALDO_H87"] = "D_DECISION_INTERNA_PROYECTO"
periodo5_resuelto["REGLA_OFICIAL_SIES"] = "NO"
periodo5_resuelto["ESTADO_H87"] = "RESUELTO_PERIODO_5_CON_DECISION_INTERNA"
periodo5_resuelto["TRATAMIENTO_H87"] = (
    "PERIODO 5 se trata como primer semestre / columna 16. "
    "No se modifica fuente original ni se genera carga."
)
periodo5_resuelto["16_H87"] = "SI"
periodo5_resuelto["17_H87"] = periodo5_resuelto["17_H86"]
periodo5_resuelto["18_H87"] = periodo5_resuelto["18_H86"]
periodo5_resuelto["19_H87"] = periodo5_resuelto["19_H86"]
periodo5_resuelto["CORRECCION_APLICADA"] = "NO"
periodo5_resuelto["GENERA_CARGA"] = "NO"

print("[5/9] Analizando Bloque B 107 sin evidencia 2025 en H85...", flush=True)

bloque_b = bloque_b_107.copy()

def clasificar_b(row):
    causa = norm_txt(row.get("CAUSA_H72", ""))
    estados = norm_txt(row.get("ESTADOS_ACADEMICOS_OBSERVADOS", ""))
    anos = norm_txt(row.get("ANOS_OBSERVADOS_PROMEDIOS", ""))
    codcli = norm_txt(row.get("CODCLI_TOKENS", ""))

    if "CODCLI_EXISTE_SOLO_OTRO_ANO" in causa:
        return "B1_CODCLI_EXISTE_SOLO_OTRO_ANO"
    if "SIN_REGISTROS_2025" in causa:
        return "B2_SIN_REGISTROS_2025"
    if "FUENTE" in causa or "COMPLEMENTARIA" in causa:
        return "B3_REQUIERE_FUENTE_COMPLEMENTARIA"
    if "MAPEO" in causa or "RUT" in causa or "DOCUMENTO" in causa:
        return "B4_REQUIERE_MAPEO_IDENTIDAD"
    if "ELIMINADO" in estados and "2025" not in anos:
        return "B5_ELIMINADO_SIN_2025_OBSERVADO"
    if "TITULADO" in estados and "2025" not in anos:
        return "B6_TITULADO_SIN_2025_OBSERVADO"
    if codcli == "":
        return "B7_SIN_CODCLI_OBSERVADO"
    return "B9_REVISION_FUNCIONAL"

bloque_b["CLASIFICACION_BLOQUE_B_H87"] = bloque_b.apply(clasificar_b, axis=1)

bloque_b["ESTADO_H87"] = "PENDIENTE_BLOQUE_B_REQUIERE_DECISION_O_FUENTE"
bloque_b["TRATAMIENTO_H87"] = (
    "No se cierra en H87 porque no existe evidencia académica 2025 asociada en H85. "
    "Se clasifica para resolución del Bloque B."
)
bloque_b["NIVEL_RESPALDO_H87"] = "B_DATO_OBSERVADO_D_DECISION_PENDIENTE"
bloque_b["CORRECCION_APLICADA"] = "NO"
bloque_b["GENERA_CARGA"] = "NO"

resumen_b = (
    bloque_b
    .groupby("CLASIFICACION_BLOQUE_B_H87", dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_b_estado = (
    bloque_b
    .groupby(["CLASIFICACION_BLOQUE_B_H87", "ESTADOS_ACADEMICOS_OBSERVADOS"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["CLASIFICACION_BLOQUE_B_H87", "CASOS"], ascending=[True, False])
)

print("[6/9] Consolidando estado global post H87...", flush=True)

total_resueltos_post_h87 = 314 + len(periodo5_resuelto)
total_pendientes_post_h87 = len(bloque_b)

resumen_global = pd.DataFrame([
    {
        "BLOQUE": "RESUELTOS_POST_H86",
        "CASOS": 314,
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "OBSERVACION": "Acumulado H68 + H85 + H86.",
    },
    {
        "BLOQUE": "H87_PERIODO_5",
        "CASOS": len(periodo5_resuelto),
        "ESTADO": "RESUELTO_CON_DECISION_INTERNA",
        "OBSERVACION": "PERIODO 5 tratado como semestre 1 / columna 16 por decisión interna.",
    },
    {
        "BLOQUE": "H87_BLOQUE_B",
        "CASOS": len(bloque_b),
        "ESTADO": "PENDIENTE_CLASIFICADO",
        "OBSERVACION": "Sin evidencia académica 2025 en H85; pasa a resolución Bloque B.",
    },
    {
        "BLOQUE": "TOTAL_16_19_ORIGINAL",
        "CASOS": 423,
        "ESTADO": f"{total_resueltos_post_h87}_RESUELTOS_{total_pendientes_post_h87}_PENDIENTES",
        "OBSERVACION": "Control global 423.",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H87 resolución PERIODO 5 y clasificación Bloque B 107 post H86 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "PERIODO_5_RESUELTOS": len(periodo5_resuelto),
    "BLOQUE_B_107_CLASIFICADOS": len(bloque_b),
    "TOTAL_RESUELTOS_16_19_POST_H87": total_resueltos_post_h87,
    "TOTAL_PENDIENTES_16_19_POST_H87": total_pendientes_post_h87,
    "CRITERIO_PERIODO_5": "PERIODO 5=>SEM1/COL16",
    "NIVEL_RESPALDO_PERIODO_5": "D_DECISION_INTERNA_PROYECTO",
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
    {"CONTROL": "Pendientes H86 entrada", "RESULTADO": "OK", "OBSERVADO": len(pendientes_h86), "ESPERADO": 109},
    {"CONTROL": "Periodo 5 resuelto", "RESULTADO": "OK", "OBSERVADO": len(periodo5_resuelto), "ESPERADO": 2},
    {"CONTROL": "Bloque B", "RESULTADO": "OK", "OBSERVADO": len(bloque_b), "ESPERADO": 107},
    {"CONTROL": "Total 423", "RESULTADO": "OK", "OBSERVADO": total_resueltos_post_h87 + total_pendientes_post_h87, "ESPERADO": 423},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[7/9] Escribiendo productos H87...", flush=True)

informe = f"""# Hito 87 — Resolución PERIODO 5 y Bloque B 107 post H86

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Decisión interna aplicada

Se resuelven los 2 casos con PERIODO 5 usando criterio interno del proyecto:

- PERIODO 5 => primer semestre / columna 16.

Nivel de respaldo: D. Decisión interna del proyecto.
No es regla oficial SIES.

## Resultado

- Resueltos post H86: 314
- Resueltos H87 por PERIODO 5: {len(periodo5_resuelto)}
- Total resueltos 16-19 post H87: {total_resueltos_post_h87}
- Pendientes Bloque B post H87: {total_pendientes_post_h87}

## Bloque B

Los 107 casos restantes no tienen evidencia académica 2025 asociada en H85.
H87 los clasifica para resolución específica, sin modificar fuentes ni generar carga.
"""

excel_out = SALIDA / "PERIODO5_Y_BLOQUE_B_107_POST_H86_5809.xlsx"
informe_out = SALIDA / "INFORME_PERIODO5_Y_BLOQUE_B_107_POST_H86_5809.md"
manifest_out = SALIDA / "manifest_periodo5_y_bloque_b_107_post_h86_5809.json"
script_out = SALIDA / "h87_periodo5_y_bloque_b_107_post_h86.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_global.to_excel(writer, sheet_name="01_RESUMEN_GLOBAL", index=False)
    periodo5_resuelto.to_excel(writer, sheet_name="02_PERIODO5_RESUELTO", index=False)
    bloque_b.to_excel(writer, sheet_name="03_BLOQUE_B_107", index=False)
    resumen_b.to_excel(writer, sheet_name="04_RESUMEN_BLOQUE_B", index=False)
    resumen_b_estado.to_excel(writer, sheet_name="05_BLOQUE_B_ESTADOS", index=False)
    control.to_excel(writer, sheet_name="06_CONTROL", index=False)
    pendientes_h86.to_excel(writer, sheet_name="07_PENDIENTES_H86_ORIGEN", index=False)
    evidencia_h86.to_excel(writer, sheet_name="08_EVIDENCIA_H86", index=False)
    pd.DataFrame([
        {"FUENTE": "H86", "RUTA": str(H86), "EXCEL": str(EX86), "SHA256": sha256(EX86)},
    ]).to_excel(writer, sheet_name="09_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 87,
        "periodo5_resueltos": len(periodo5_resuelto),
        "bloque_b_107": len(bloque_b),
        "total_resueltos_16_19_post_h87": total_resueltos_post_h87,
        "total_pendientes_16_19_post_h87": total_pendientes_post_h87,
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="10_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "H87 periodo 5 y bloque B 107 post H86 5809 columnas 16-19",
    "hito": 87,
    "periodo5_resueltos": len(periodo5_resuelto),
    "bloque_b_107_clasificados": len(bloque_b),
    "total_resueltos_16_19_post_h87": total_resueltos_post_h87,
    "total_pendientes_16_19_post_h87": total_pendientes_post_h87,
    "criterio_periodo5": "PERIODO 5=>SEM1/COL16",
    "nivel_respaldo": "D_DECISION_INTERNA_PROYECTO",
    "regla_oficial_sies": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h87_periodo5_y_bloque_b_107_post_h86.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/9] Validando productos...", flush=True)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[9/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 87 — PERIODO 5 RESUELTO Y BLOQUE B 107 CLASIFICADO")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("PERIODO 5 resueltos: 2")
print("Criterio PERIODO 5: SEM1/COL16")
print("Nivel respaldo: D_DECISION_INTERNA_PROYECTO")
print("Regla oficial SIES: NO")
print(f"Total resueltos 16-19 post H87: {total_resueltos_post_h87}")
print(f"Pendientes Bloque B post H87: {total_pendientes_post_h87}")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN GLOBAL", resumen_global)
imprimir("RESUMEN BLOQUE B", resumen_b)
imprimir("CONTROL", control)
imprimir("PERIODO 5 RESUELTO", periodo5_resuelto)
imprimir("MUESTRA BLOQUE B 107", bloque_b, 30)

print()
print("=" * 170)
print("ARCHIVOS H87")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)

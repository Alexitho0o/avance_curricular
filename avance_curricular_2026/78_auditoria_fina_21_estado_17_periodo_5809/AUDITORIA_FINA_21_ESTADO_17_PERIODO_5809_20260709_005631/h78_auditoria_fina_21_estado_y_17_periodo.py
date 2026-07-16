from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import re
import hashlib

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/78_auditoria_fina_21_estado_17_periodo_5809"
    / f"AUDITORIA_FINA_21_ESTADO_17_PERIODO_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_AUDITORIA_FINA_21_ESTADO_17_PERIODO_5809_{timestamp}"

SALIDA.mkdir(parents=True, exist_ok=True)
ESCRITORIO.mkdir(parents=True, exist_ok=True)

def norm(x):
    x = str(x or "").upper()
    for a, b in {"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","Ñ":"N"}.items():
        x = x.replace(a, b)
    x = re.sub(r"[^A-Z0-9]+", "_", x)
    return re.sub(r"_+", "_", x).strip("_")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def ultimo(base, prefijo):
    if not base.exists():
        raise SystemExit(f"BLOQUEO: no existe carpeta base: {base}")
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
    for p in patrones:
        for h in xls.sheet_names:
            if norm(p) == norm(h) or norm(p) in norm(h):
                return h
    return None

def leer(xlsx, patrones):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        xls = pd.ExcelFile(xlsx, engine="openpyxl")
        raise SystemExit(
            f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. "
            f"Hojas disponibles: {xls.sheet_names}"
        )
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def col(df, patrones):
    mapa = {norm(c): c for c in df.columns}
    for p in patrones:
        if norm(p) in mapa:
            return mapa[norm(p)]
    for c in df.columns:
        nc = norm(c)
        for p in patrones:
            if norm(p) in nc:
                return c
    return None

def cols_like(df, patrones):
    out = []
    for c in df.columns:
        nc = norm(c)
        if any(norm(p) in nc for p in patrones):
            out.append(c)
    return out

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

print("[1/9] Localizando H63 y H77...", flush=True)

H63 = ultimo(
    RAIZ / "avance_curricular_2026/63_terminal_revision_38_decision_funcional_restante_5809",
    "REVISION_38_DECISION_FUNCIONAL_RESTANTE_",
)

H77 = ultimo(
    RAIZ / "avance_curricular_2026/77_registro_decisiones_usuario_h68_256_16_19_5809",
    "REGISTRO_DECISIONES_USUARIO_H68_256_16_19_5809_",
)

EX63 = primer_excel(H63)
EX77 = primer_excel(H77)

print(f"   H63: {EX63}")
print(f"   H77: {EX77}")

print("[2/9] Leyendo hojas reales de H63 y H77...", flush=True)

detalle21 = leer(EX63, ["03_21_ESTADO_ACAD", "21_ESTADO"])
detalle17 = leer(EX63, ["04_17_PERIODO_NO_1_2", "17_PERIODO"])
evidencia_h56 = leer(EX63, ["05_EVIDENCIA_H56", "EVIDENCIA_H56"])
evidencia_h55 = leer(EX63, ["06_EVIDENCIA_H55", "EVIDENCIA_H55"])
periodo_h55 = leer(EX63, ["07_DETALLE_PERIODO_H55", "DETALLE_PERIODO"])
decisiones77 = leer(EX77, ["01_DECISIONES_USUARIO", "DECISIONES"])

if len(detalle21) != 21:
    raise SystemExit(f"BLOQUEO: detalle21 esperado 21, detectado {len(detalle21)}")

if len(detalle17) != 17:
    raise SystemExit(f"BLOQUEO: detalle17 esperado 17, detectado {len(detalle17)}")

print("[3/9] Filtrando evidencia exacta de los 21...", flush=True)

c_fila_21 = col(detalle21, ["FILA_KEY", "FILA_5809", "FILA"])
c_fila_h56 = col(evidencia_h56, ["FILA_KEY", "FILA_5809", "FILA"])

if not c_fila_21:
    raise SystemExit("BLOQUEO: no se encontró FILA_KEY/FILA en detalle21.")

if not c_fila_h56:
    raise SystemExit("BLOQUEO: no se encontró FILA_KEY/FILA en evidencia_h56.")

detalle21 = detalle21.copy()
evidencia_h56 = evidencia_h56.copy()

detalle21["_FILA_KEY_JOIN"] = detalle21[c_fila_21].astype(str).str.strip()
evidencia_h56["_FILA_KEY_JOIN"] = evidencia_h56[c_fila_h56].astype(str).str.strip()

filas21 = set(detalle21["_FILA_KEY_JOIN"])

evidencia21 = evidencia_h56[evidencia_h56["_FILA_KEY_JOIN"].isin(filas21)].copy()

if evidencia21.empty:
    print("ADVERTENCIA: no se encontró evidencia H56 filtrada para los 21. Se usará detalle21.", flush=True)

# Columnas reales de estado/situación en evidencia 21
cols_estado21 = cols_like(
    evidencia21 if not evidencia21.empty else detalle21,
    ["SITUACION", "ESTADO", "ACADEMIC", "VIGENTE", "ELIMINADO"]
)

cols_ident21 = []
for patrones in [
    ["FILA"],
    ["NUM_DOCUMENTO", "DOCUMENTO", "RUT"],
    ["CODCLI"],
    ["CODIGO_UNICO"],
    ["PLAN"],
    ["CAUSA"],
    ["ANOS"],
    ["FILAS_2025"],
    ["FILAS_2026"],
    ["MAPEO"],
]:
    for c in (evidencia21 if not evidencia21.empty else detalle21).columns:
        if any(norm(p) in norm(c) for p in patrones) and c not in cols_ident21:
            cols_ident21.append(c)

base21 = evidencia21 if not evidencia21.empty else detalle21
cols_vista21 = []
for c in cols_ident21 + cols_estado21:
    if c in base21.columns and c not in cols_vista21:
        cols_vista21.append(c)

if not cols_vista21:
    cols_vista21 = list(base21.columns)

vista21 = base21[cols_vista21].copy()

# Explosión de estados observados por separador " | "
estado_col = None
for c in cols_estado21:
    if "ESTADOS_ACADEMICOS_OBSERVADOS" == norm(c):
        estado_col = c
        break
if estado_col is None:
    for c in cols_estado21:
        if "ESTADO" in norm(c) and "INACTIVO" not in norm(c):
            estado_col = c
            break

estados_expand_rows = []
if estado_col and estado_col in base21.columns:
    for _, r in base21.iterrows():
        raw = str(r[estado_col]).strip()
        partes = [p.strip() for p in raw.split("|") if p.strip()]
        if not partes:
            partes = ["(VACIO)"]
        for p in partes:
            estados_expand_rows.append({
                "FILA_KEY": r.get("_FILA_KEY_JOIN", ""),
                "COLUMNA_ESTADO": estado_col,
                "ESTADO_RAW": raw,
                "ESTADO_ATOMICO": p,
                "ES_COMBINACION": "SI" if "|" in raw else "NO",
            })

estados_expand = pd.DataFrame(estados_expand_rows)

resumen_estados_atomicos = (
    estados_expand
    .groupby(["ESTADO_ATOMICO"], dropna=False)
    .size()
    .reset_index(name="CASOS_ATOMICOS")
    .sort_values("CASOS_ATOMICOS", ascending=False)
) if not estados_expand.empty else pd.DataFrame(columns=["ESTADO_ATOMICO", "CASOS_ATOMICOS"])

resumen_estado_raw = (
    estados_expand
    .drop_duplicates(["FILA_KEY", "ESTADO_RAW"])
    .groupby(["ESTADO_RAW", "ES_COMBINACION"], dropna=False)
    .size()
    .reset_index(name="FILAS")
    .sort_values("FILAS", ascending=False)
) if not estados_expand.empty else pd.DataFrame(columns=["ESTADO_RAW", "ES_COMBINACION", "FILAS"])

combo21 = estados_expand[estados_expand["ES_COMBINACION"].eq("SI")].copy() if not estados_expand.empty else pd.DataFrame()

print("[4/9] Filtrando evidencia exacta de los 17...", flush=True)

c_fila_17 = col(detalle17, ["FILA_KEY", "FILA_5809", "FILA"])
c_fila_periodo = col(periodo_h55, ["FILA_KEY", "FILA_5809", "FILA"])

if not c_fila_17:
    raise SystemExit("BLOQUEO: no se encontró FILA_KEY/FILA en detalle17.")

if not c_fila_periodo:
    raise SystemExit("BLOQUEO: no se encontró FILA_KEY/FILA en periodo_h55.")

detalle17 = detalle17.copy()
periodo_h55 = periodo_h55.copy()

detalle17["_FILA_KEY_JOIN"] = detalle17[c_fila_17].astype(str).str.strip()
periodo_h55["_FILA_KEY_JOIN"] = periodo_h55[c_fila_periodo].astype(str).str.strip()

filas17 = set(detalle17["_FILA_KEY_JOIN"])

periodo17 = periodo_h55[periodo_h55["_FILA_KEY_JOIN"].isin(filas17)].copy()

if periodo17.empty:
    print("ADVERTENCIA: no se encontró evidencia H55 filtrada para los 17. Se usará detalle17.", flush=True)

base17_periodo = periodo17 if not periodo17.empty else detalle17

cols_periodo17 = cols_like(base17_periodo, ["PERIODO"])
periodo_col = None
for c in cols_periodo17:
    if norm(c) == "PERIODO":
        periodo_col = c
        break
if periodo_col is None:
    for c in cols_periodo17:
        if "PERIODO" in norm(c) and "NO_1_2" not in norm(c):
            periodo_col = c
            break

cols_ident17 = []
for patrones in [
    ["FILA"],
    ["NUM_DOCUMENTO", "DOCUMENTO", "RUT"],
    ["CODCLI"],
    ["CODIGO_UNICO"],
    ["PLAN"],
    ["PERIODO"],
    ["ESTADO"],
    ["ASIGNATURA"],
    ["COLUMNA"],
    ["VALOR"],
]:
    for c in base17_periodo.columns:
        if any(norm(p) in norm(c) for p in patrones) and c not in cols_ident17:
            cols_ident17.append(c)

vista17 = base17_periodo[cols_ident17 if cols_ident17 else base17_periodo.columns].copy()

def map_periodo_usuario(x):
    s = str(x).strip()
    if s == "1":
        return "1"
    if s in ["2", "3"]:
        return "2"
    return "NO_DEFINIDO_POR_USUARIO"

if periodo_col and periodo_col in base17_periodo.columns:
    periodo17_map = base17_periodo.copy()
    periodo17_map["PERIODO_RAW_AUDITADO"] = periodo17_map[periodo_col].astype(str).str.strip()
    periodo17_map["MAPEO_USUARIO"] = periodo17_map["PERIODO_RAW_AUDITADO"].apply(map_periodo_usuario)
else:
    periodo17_map = base17_periodo.copy()
    periodo17_map["PERIODO_RAW_AUDITADO"] = ""
    periodo17_map["MAPEO_USUARIO"] = "SIN_COLUMNA_PERIODO"

resumen_periodos17 = (
    periodo17_map
    .groupby(["PERIODO_RAW_AUDITADO", "MAPEO_USUARIO"], dropna=False)
    .size()
    .reset_index(name="FILAS_EVIDENCIA")
    .sort_values(["MAPEO_USUARIO", "PERIODO_RAW_AUDITADO"])
)

periodos17_no_def = periodo17_map[
    periodo17_map["MAPEO_USUARIO"].eq("NO_DEFINIDO_POR_USUARIO")
].copy()

# Conteo por FILA_KEY de los 17
periodo17_por_fila = (
    periodo17_map
    .groupby("_FILA_KEY_JOIN", dropna=False)
    .agg(
        PERIODOS_RAW=("PERIODO_RAW_AUDITADO", lambda s: " | ".join(sorted(set(str(x) for x in s if str(x).strip())))),
        MAPEOS_USUARIO=("MAPEO_USUARIO", lambda s: " | ".join(sorted(set(str(x) for x in s if str(x).strip())))),
        FILAS_EVIDENCIA=("MAPEO_USUARIO", "size"),
    )
    .reset_index()
    .rename(columns={"_FILA_KEY_JOIN": "FILA_KEY"})
)

print("[5/9] Construyendo dictamen fino...", flush=True)

hay_combo = not combo21.empty
hay_periodos_no_def = not periodos17_no_def.empty

dictamen21 = (
    "BLOQUEADO: existe al menos una fila con ESTADOS_ACADEMICOS_OBSERVADOS combinado. Debe separarse por CODCLI/estado antes de cerrar."
    if hay_combo
    else "No se detecta combinación ELIMINADO | VIGENTE en la evidencia filtrada de los 21."
)

dictamen17 = (
    "BLOQUEADO_PARCIAL: en evidencia filtrada de los 17 hay períodos fuera de 1/2/3; falta decisión usuario para esos períodos."
    if hay_periodos_no_def
    else "APLICABLE: todos los períodos filtrados de los 17 quedan cubiertos por criterio usuario 1=1 y 2/3=2."
)

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Auditoría fina 21 situación académica y 17 período archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "AUDITORIA_FINA_TERMINAL",
    "CASOS_21": 21,
    "DICTAMEN_21": dictamen21,
    "COMBINACION_ELIMINADO_VIGENTE_DETECTADA": "SI" if hay_combo else "NO",
    "CASOS_17": 17,
    "DICTAMEN_17": dictamen17,
    "PERIODOS_17_NO_DEFINIDOS": "SI" if hay_periodos_no_def else "NO",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

decision_recomendada = pd.DataFrame([
    {
        "BLOQUE": "21_SIN_REGISTROS_2025",
        "RESULTADO_AUDITORIA": dictamen21,
        "DECISION_RECOMENDADA": "No cerrar todavía si existe combinación. Revisar fila combinada y separar si corresponde a dos CODCLI/estados distintos.",
        "ACCION_SIGUIENTE": "Ver COMBINACIONES_21 y VISTA_21_TERMINAL.",
    },
    {
        "BLOQUE": "17_PERIODO_NO_1_2",
        "RESULTADO_AUDITORIA": dictamen17,
        "DECISION_RECOMENDADA": "Aplicar criterio usuario solo si todos los registros filtrados tienen PERIODO 1,2,3; si aparecen 4/5, pedir decisión para 4/5 o bloquear esas filas.",
        "ACCION_SIGUIENTE": "Ver PERIODOS_17_NO_DEFINIDOS y PERIODO_17_POR_FILA.",
    },
])

print("[6/9] Escribiendo productos H78...", flush=True)

excel_out = SALIDA / "AUDITORIA_FINA_21_ESTADO_17_PERIODO_5809.xlsx"
informe_out = SALIDA / "INFORME_AUDITORIA_FINA_21_ESTADO_17_PERIODO_5809.md"
manifest_out = SALIDA / "manifest_auditoria_fina_21_estado_17_periodo_5809.json"
script_out = SALIDA / "h78_auditoria_fina_21_estado_y_17_periodo.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    decision_recomendada.to_excel(writer, sheet_name="01_DECISION_RECOMENDADA", index=False)
    vista21.to_excel(writer, sheet_name="02_VISTA_21_TERMINAL", index=False)
    resumen_estado_raw.to_excel(writer, sheet_name="03_RESUMEN_ESTADO_RAW_21", index=False)
    resumen_estados_atomicos.to_excel(writer, sheet_name="04_ESTADOS_ATOMICOS_21", index=False)
    combo21.to_excel(writer, sheet_name="05_COMBINACIONES_21", index=False)
    detalle21.to_excel(writer, sheet_name="06_DETALLE_21_ORIGINAL", index=False)
    evidencia21.to_excel(writer, sheet_name="07_EVIDENCIA_21_FILTRADA", index=False)
    vista17.to_excel(writer, sheet_name="08_VISTA_17_TERMINAL", index=False)
    resumen_periodos17.to_excel(writer, sheet_name="09_RESUMEN_PERIODOS_17", index=False)
    periodo17_por_fila.to_excel(writer, sheet_name="10_PERIODO_17_POR_FILA", index=False)
    periodos17_no_def.to_excel(writer, sheet_name="11_PERIODOS_17_NO_DEFINIDOS", index=False)
    detalle17.to_excel(writer, sheet_name="12_DETALLE_17_ORIGINAL", index=False)
    periodo17.to_excel(writer, sheet_name="13_EVIDENCIA_17_FILTRADA", index=False)
    decisiones77.to_excel(writer, sheet_name="14_REFERENCIA_H77", index=False)
    pd.DataFrame([
        {"HITO": "63", "RUTA": str(H63), "EXCEL": str(EX63), "SHA256": sha256(EX63)},
        {"HITO": "77", "RUTA": str(H77), "EXCEL": str(EX77), "SHA256": sha256(EX77)},
    ]).to_excel(writer, sheet_name="15_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 78,
        "casos_21": 21,
        "combo_21_detectado": "SI" if hay_combo else "NO",
        "casos_17": 17,
        "periodos_17_no_definidos": "SI" if hay_periodos_no_def else "NO",
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="16_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe = f"""# Hito 78 — Auditoría fina 21 situación académica y 17 período

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado 21

{dictamen21}

## Resultado 17

{dictamen17}

## Control

No se modifican fuentes originales.
No se aplican correcciones.
No se genera archivo de carga.
No se genera SIES_READY.
No se permite subida SIES.
"""

informe_out.write_text(informe, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Auditoria fina 21 situacion academica y 17 periodo archivo 5809",
    "hito": 78,
    "casos_21": 21,
    "dictamen_21": dictamen21,
    "combo_21_detectado": bool(hay_combo),
    "casos_17": 17,
    "dictamen_17": dictamen17,
    "periodos_17_no_definidos": bool(hay_periodos_no_def),
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h78_auditoria_fina_21_estado_y_17_periodo.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[7/9] Verificando productos...", flush=True)

assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert len(detalle21) == 21
assert len(detalle17) == 17

print("[8/9] Mostrando auditoría fina en terminal...", flush=True)

print()
print("=" * 170)
print("HITO 78 — AUDITORÍA FINA 21 ESTADO Y 17 PERIODO GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("21 revisados: SI")
print(f"Combinación ELIMINADO | VIGENTE detectada: {'SI' if hay_combo else 'NO'}")
print(f"Dictamen 21: {dictamen21}")
print("17 revisados: SI")
print(f"Períodos 17 no definidos por usuario: {'SI' if hay_periodos_no_def else 'NO'}")
print(f"Dictamen 17: {dictamen17}")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("DECISION RECOMENDADA", decision_recomendada)
imprimir("21 — VISTA TERMINAL CON SITUACION/ESTADO", vista21)
imprimir("21 — RESUMEN ESTADO RAW", resumen_estado_raw)
imprimir("21 — ESTADOS ATOMICOS", resumen_estados_atomicos)
imprimir("21 — COMBINACIONES DETECTADAS", combo21)
imprimir("17 — VISTA TERMINAL FILTRADA", vista17, 80)
imprimir("17 — RESUMEN PERIODOS FILTRADOS", resumen_periodos17)
imprimir("17 — PERIODO POR FILA", periodo17_por_fila)
imprimir("17 — PERIODOS NO DEFINIDOS", periodos17_no_def, 80)

print()
print("=" * 170)
print("ARCHIVOS H78")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)

print("[9/9] Terminado.", flush=True)

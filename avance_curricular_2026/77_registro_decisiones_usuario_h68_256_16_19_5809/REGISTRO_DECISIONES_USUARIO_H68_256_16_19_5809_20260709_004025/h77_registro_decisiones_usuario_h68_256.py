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
    / "avance_curricular_2026/77_registro_decisiones_usuario_h68_256_16_19_5809"
    / f"REGISTRO_DECISIONES_USUARIO_H68_256_16_19_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_REGISTRO_DECISIONES_USUARIO_H68_256_16_19_5809_{timestamp}"

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

def col_candidates(df, tokens):
    out = []
    for c in df.columns:
        nc = norm(c)
        if any(t in nc for t in tokens):
            out.append(c)
    return out

def imprimir(titulo, df, n=None):
    print()
    print("=" * 160)
    print(titulo)
    print("=" * 160)
    if df.empty:
        print("(sin datos)")
        return
    if n is None:
        print(df.to_string(index=False))
    else:
        print(df.head(n).to_string(index=False))
        if len(df) > n:
            print(f"... mostrando {n} de {len(df)} filas")

print("[1/10] Localizando H62, H63, H67, H68, H76...", flush=True)

H62 = ultimo(
    RAIZ / "avance_curricular_2026/62_decision_funcional_candidata_columna_19_solo_a_5809",
    "DECISION_FUNCIONAL_CANDIDATA_19_SOLO_A_",
)
H63 = ultimo(
    RAIZ / "avance_curricular_2026/63_terminal_revision_38_decision_funcional_restante_5809",
    "REVISION_38_DECISION_FUNCIONAL_RESTANTE_",
)
H67 = ultimo(
    RAIZ / "avance_curricular_2026/67_gobernanza_periodo_raw_5809",
    "GOBERNANZA_PERIODO_RAW_5809_",
)
H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)
H76 = ultimo(
    RAIZ / "avance_curricular_2026/76_fundamento_metodologico_h68_256_decision_funcional_5809",
    "FUNDAMENTO_METODOLOGICO_H68_256_DECISION_FUNCIONAL_5809_",
)

EX62 = primer_excel(H62)
EX63 = primer_excel(H63)
EX67 = primer_excel(H67)
EX68 = primer_excel(H68)
EX76 = primer_excel(H76)

print(f"   H62: {EX62}")
print(f"   H63: {EX63}")
print(f"   H67: {EX67}")
print(f"   H68: {EX68}")
print(f"   H76: {EX76}")

print("[2/10] Leyendo matrices base...", flush=True)

detalle218 = leer(EX62, ["07_DETALLE_218", "DETALLE_218"])
numeros63 = leer(EX63, ["01_NUMEROS_BASE", "NUMEROS_BASE"])
detalle38 = leer(EX63, ["02_DETALLE_38", "DETALLE_38"])
detalle21 = leer(EX63, ["03_21_ESTADO_ACAD", "21_ESTADO"])
detalle17 = leer(EX63, ["04_17_PERIODO_NO_1_2", "17_PERIODO"])
evidencia_h56 = leer(EX63, ["05_EVIDENCIA_H56", "EVIDENCIA_H56"])
evidencia_h55 = leer(EX63, ["06_EVIDENCIA_H55", "EVIDENCIA_H55"])
periodo_h55 = leer(EX63, ["07_DETALLE_PERIODO_H55", "DETALLE_PERIODO"])
matriz67 = leer(EX67, ["08_MATRIZ_DECISION_PERIODO", "MATRIZ_DECISION"])
dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
fundamento76 = leer(EX76, ["01_FUNDAMENTO_256", "FUNDAMENTO"])

print("[3/10] Validando conteos base...", flush=True)

if len(detalle218) != 218:
    raise SystemExit(f"BLOQUEO: detalle218 esperado 218, detectado {len(detalle218)}")

if len(detalle21) != 21:
    raise SystemExit(f"BLOQUEO: detalle21 esperado 21, detectado {len(detalle21)}")

if len(detalle17) != 17:
    raise SystemExit(f"BLOQUEO: detalle17 esperado 17, detectado {len(detalle17)}")

print("[4/10] Auditando situación académica de los 21...", flush=True)

# Buscar columnas probables de situación/estado académico.
cols_estado_21 = col_candidates(detalle21, ["SITUACION", "ESTADO", "VIGENTE", "ACADEM"])
cols_estado_38 = col_candidates(detalle38, ["SITUACION", "ESTADO", "VIGENTE", "ACADEM"])
cols_estado_h56 = col_candidates(evidencia_h56, ["SITUACION", "ESTADO", "VIGENTE", "ACADEM"])

# Consolidar vista amplia para terminal.
cols_base_21 = []
for tokens in [
    ["FILA"],
    ["NUM_DOCUMENTO", "DOCUMENTO", "RUT"],
    ["CODIGO_UNICO"],
    ["PLAN"],
    ["CODCLI"],
]:
    for c in detalle21.columns:
        if any(t in norm(c) for t in tokens) and c not in cols_base_21:
            cols_base_21.append(c)

cols_vista_21 = []
for c in cols_base_21 + cols_estado_21:
    if c not in cols_vista_21:
        cols_vista_21.append(c)

if not cols_vista_21:
    cols_vista_21 = list(detalle21.columns)

vista21 = detalle21[cols_vista_21].copy()

# Detectar valores únicos de columnas de estado/situación.
estado_rows = []
for origen, df, cols in [
    ("H63_03_21_ESTADO_ACAD", detalle21, cols_estado_21),
    ("H63_02_DETALLE_38", detalle38, cols_estado_38),
    ("H63_05_EVIDENCIA_H56", evidencia_h56, cols_estado_h56),
]:
    for c in cols:
        valores = (
            df[c]
            .astype(str)
            .str.strip()
            .replace("", "(VACIO)")
            .value_counts()
            .reset_index()
        )
        valores.columns = ["VALOR", "CASOS"]
        for _, r in valores.iterrows():
            estado_rows.append({
                "ORIGEN": origen,
                "COLUMNA": c,
                "VALOR": r["VALOR"],
                "CASOS": int(r["CASOS"]),
            })

resumen_estados = pd.DataFrame(estado_rows)

# Validación específica solicitada: no debería existir combinación ELIMINADO | VIGENTE como estado atómico.
patron_combo = re.compile(r"ELIMINADO\s*\|\s*VIGENTE|VIGENTE\s*\|\s*ELIMINADO", re.I)

combos_detectados = []
for origen, df, cols in [
    ("H63_03_21_ESTADO_ACAD", detalle21, cols_estado_21),
    ("H63_02_DETALLE_38", detalle38, cols_estado_38),
    ("H63_05_EVIDENCIA_H56", evidencia_h56, cols_estado_h56),
]:
    for c in cols:
        mask = df[c].astype(str).str.contains(patron_combo, na=False)
        if mask.any():
            tmp = df.loc[mask].copy()
            tmp.insert(0, "ORIGEN_DETECCION", origen)
            tmp.insert(1, "COLUMNA_DETECCION", c)
            combos_detectados.append(tmp)

if combos_detectados:
    combos_df = pd.concat(combos_detectados, ignore_index=True, sort=False)
else:
    combos_df = pd.DataFrame(columns=["ORIGEN_DETECCION", "COLUMNA_DETECCION"])

# Clasificación de los 21 según auditoría.
if not resumen_estados.empty:
    valores_globales = set(resumen_estados["VALOR"].astype(str).str.upper())
else:
    valores_globales = set()

hay_combo = not combos_df.empty

decision_21_estado = "PENDIENTE_REVISION_USUARIO"
if hay_combo:
    decision_21_estado = "BLOQUEADO_POR_COMBINACION_ESTADO_A_REVISAR"
else:
    # No forzar cierre: el usuario pidió ver primero.
    decision_21_estado = "PENDIENTE_DECISION_USUARIO_TRAS_REVISION_TERMINAL"

print("[5/10] Evaluando los 17 con decisión usuario PERIODO 1=1, 2/3=2...", flush=True)

# Buscar columnas de periodo y columnas afectadas.
cols_periodo_17 = col_candidates(detalle17, ["PERIODO"])
cols_periodo_h55 = col_candidates(periodo_h55, ["PERIODO"])

# Construir vista periodo desde detalle17 + periodo_h55.
cols_base_17 = []
for tokens in [
    ["FILA"],
    ["NUM_DOCUMENTO", "DOCUMENTO", "RUT"],
    ["CODIGO_UNICO"],
    ["PLAN"],
    ["CODCLI"],
    ["COLUMNA"],
    ["VALOR"],
    ["PERIODO"],
]:
    for c in detalle17.columns:
        if any(t in norm(c) for t in tokens) and c not in cols_base_17:
            cols_base_17.append(c)

vista17 = detalle17[cols_base_17 if cols_base_17 else detalle17.columns].copy()

periodo_rows = []
for origen, df, cols in [
    ("H63_04_17_PERIODO_NO_1_2", detalle17, cols_periodo_17),
    ("H63_07_DETALLE_PERIODO_H55", periodo_h55, cols_periodo_h55),
]:
    for c in cols:
        vals = (
            df[c]
            .astype(str)
            .str.strip()
            .replace("", "(VACIO)")
            .value_counts()
            .reset_index()
        )
        vals.columns = ["PERIODO_RAW", "CASOS"]
        for _, r in vals.iterrows():
            periodo_rows.append({
                "ORIGEN": origen,
                "COLUMNA": c,
                "PERIODO_RAW": r["PERIODO_RAW"],
                "CASOS": int(r["CASOS"]),
                "MAPEO_USUARIO": "1" if str(r["PERIODO_RAW"]).strip() == "1" else ("2" if str(r["PERIODO_RAW"]).strip() in ["2", "3"] else "NO_DEFINIDO_POR_USUARIO"),
            })

resumen_periodos = pd.DataFrame(periodo_rows)

periodos_no_definidos = resumen_periodos[
    resumen_periodos["MAPEO_USUARIO"].eq("NO_DEFINIDO_POR_USUARIO")
].copy() if not resumen_periodos.empty else pd.DataFrame()

decision_17_estado = (
    "APROBADO_USUARIO_MAPEO_PERIODO_1_1_2_3_2"
    if periodos_no_definidos.empty
    else "APROBADO_PARCIAL_CON_PERIODOS_NO_DEFINIDOS"
)

print("[6/10] Registrando decisiones usuario...", flush=True)

decisiones_usuario = pd.DataFrame([
    {
        "BLOQUE": "COLUMNA_19_SOLO_A",
        "CASOS": 218,
        "DECISION_USUARIO": "APRUEBO_CERRAR_ESTOS_218",
        "TRATAMIENTO": "Cerrar sin cambio. Mantener columna 19 contando solo A=APROBADO; excluir E/I del anual 2025.",
        "CORRECCION_DATOS": "NO",
        "ESTADO_RESULTANTE": "CERRADO_SIN_CAMBIO_POR_DECISION_USUARIO",
        "OBSERVACION": "Decisión entregada explícitamente por usuario en conversación.",
    },
    {
        "BLOQUE": "ESTADO_ACADEMICO_SIN_REGISTROS_2025",
        "CASOS": 21,
        "DECISION_USUARIO": "NO_APROBADO_AUN_REVISAR_SITUACION_ACADEMICA",
        "TRATAMIENTO": "Mantener pendiente hasta revisar situación académica en terminal.",
        "CORRECCION_DATOS": "NO",
        "ESTADO_RESULTANTE": decision_21_estado,
        "OBSERVACION": "Usuario indica que no existe combinación ELIMINADO | VIGENTE y solicita ver columna situación académica.",
    },
    {
        "BLOQUE": "PERIODO_NO_1_2",
        "CASOS": 17,
        "DECISION_USUARIO": "APRUEBO_CRITERIO_PERIODO_1_ES_1_Y_PERIODO_2_3_ES_2",
        "TRATAMIENTO": "Aplicar como decisión interna: PERIODO raw 1 = semestre 1; PERIODO raw 2 y 3 = semestre 2. No declarar como regla oficial.",
        "CORRECCION_DATOS": "PENDIENTE_EVALUAR_IMPACTO_TECNICO",
        "ESTADO_RESULTANTE": decision_17_estado,
        "OBSERVACION": "Decisión interna del usuario; no equivale a regla oficial del instructivo.",
    },
])

estado_post_decision = pd.DataFrame([
    {
        "CATEGORIA": "CERRADOS_SIN_CAMBIO_POR_DECISION_USUARIO",
        "CASOS": 218,
        "DETALLE": "218 COLUMNA_19_SOLO_A.",
    },
    {
        "CATEGORIA": "PENDIENTES_REVISION_USUARIO_21",
        "CASOS": 21,
        "DETALLE": "Revisar situación académica: ELIMINADO o VIGENTE; no combinación.",
    },
    {
        "CATEGORIA": "APROBADOS_CRITERIO_PERIODO_USUARIO_17",
        "CASOS": 17,
        "DETALLE": "PERIODO 1=1; PERIODO 2/3=2. Requiere evaluar impacto técnico antes de corrección.",
    },
    {
        "CATEGORIA": "BLOQUEADOS_H72_EVIDENCIA_FALTANTE",
        "CASOS": 167,
        "DETALLE": "No abordados por esta decisión; siguen bloqueados.",
    },
])

control_carga = pd.DataFrame([
    {"CONTROL": "218 cerrados por decisión usuario", "RESULTADO": "SI", "DICTAMEN": "Cierre sin cambio documentado."},
    {"CONTROL": "21 cerrados", "RESULTADO": "NO", "DICTAMEN": "Usuario solicita revisión terminal de situación académica."},
    {"CONTROL": "17 con criterio usuario", "RESULTADO": "SI_PENDIENTE_IMPACTO", "DICTAMEN": "Criterio interno registrado; falta evaluar impacto técnico/corrección."},
    {"CONTROL": "167 H72 resueltos", "RESULTADO": "NO", "DICTAMEN": "Siguen bloqueados por evidencia faltante."},
    {"CONTROL": "Archivo de carga generado", "RESULTADO": "NO", "DICTAMEN": "No corresponde."},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "DICTAMEN": "No corresponde."},
    {"CONTROL": "Subida SIES permitida", "RESULTADO": "NO", "DICTAMEN": "No corresponde."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Registro decisiones usuario H68 256 columnas 16-19 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "REGISTRO_DECISIONES_USUARIO_PARCIAL",
    "DECISION_218": "APROBADO_CIERRE_SIN_CAMBIO",
    "DECISION_21": "PENDIENTE_REVISION_SITUACION_ACADEMICA",
    "DECISION_17": "APROBADO_CRITERIO_USUARIO_PERIODO_1_1_2_3_2",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "DICTAMEN_GLOBAL": "Se registra decisión usuario: cerrar 218 sin cambio; mantener 21 pendientes hasta revisar situación académica; aprobar criterio interno para 17 periodos. No se genera carga.",
}])

print("[7/10] Redactando informe...", flush=True)

informe = f"""# Hito 77 — Registro decisiones usuario H68 256

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Decisiones registradas

### 218 COLUMNA_19_SOLO_A

Usuario aprueba cerrar estos 218.
Tratamiento: cierre sin cambio.
Corrección de datos: NO.

### 21 SIN REGISTROS 2025

Usuario no aprueba aún.
Solicita revisar en terminal la columna de situación académica.
Criterio indicado por usuario: debe ser ELIMINADO o VIGENTE; no existe combinación ELIMINADO | VIGENTE.

Estado: {decision_21_estado}.

### 17 PERIODO_NO_1_2

Usuario define criterio interno:

- PERIODO 1 = 1.
- PERIODO 2 y 3 = 2.

Este criterio se registra como decisión interna del usuario, no como regla oficial del instructivo.

## Control

No se modifican fuentes originales.
No se aplican correcciones.
No se genera archivo de carga.
No se genera SIES_READY.
No se permite subida SIES.
"""

print("[8/10] Escribiendo productos H77...", flush=True)

excel_out = SALIDA / "REGISTRO_DECISIONES_USUARIO_H68_256_16_19_5809.xlsx"
informe_out = SALIDA / "INFORME_REGISTRO_DECISIONES_USUARIO_H68_256_16_19_5809.md"
manifest_out = SALIDA / "manifest_registro_decisiones_usuario_h68_256_16_19_5809.json"
script_out = SALIDA / "h77_registro_decisiones_usuario_h68_256.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    decisiones_usuario.to_excel(writer, sheet_name="01_DECISIONES_USUARIO", index=False)
    estado_post_decision.to_excel(writer, sheet_name="02_ESTADO_POST_DECISION", index=False)
    vista21.to_excel(writer, sheet_name="03_TERMINAL_21_SIT_ACAD", index=False)
    resumen_estados.to_excel(writer, sheet_name="04_RESUMEN_ESTADOS_21", index=False)
    combos_df.to_excel(writer, sheet_name="05_COMBOS_ELIM_VIG_21", index=False)
    vista17.to_excel(writer, sheet_name="06_TERMINAL_17_PERIODO", index=False)
    resumen_periodos.to_excel(writer, sheet_name="07_MAPEO_USUARIO_PERIODOS", index=False)
    periodos_no_definidos.to_excel(writer, sheet_name="08_PERIODOS_NO_DEFINIDOS", index=False)
    control_carga.to_excel(writer, sheet_name="09_CONTROL_CARGA", index=False)
    matriz68.to_excel(writer, sheet_name="10_REFERENCIA_H68", index=False)
    fundamento76.to_excel(writer, sheet_name="11_REFERENCIA_H76", index=False)
    detalle218.to_excel(writer, sheet_name="12_DETALLE_218", index=False)
    detalle21.to_excel(writer, sheet_name="13_DETALLE_21_COMPLETO", index=False)
    detalle17.to_excel(writer, sheet_name="14_DETALLE_17_COMPLETO", index=False)
    evidencia_h56.to_excel(writer, sheet_name="15_EVIDENCIA_H56_21", index=False)
    periodo_h55.to_excel(writer, sheet_name="16_EVIDENCIA_H55_17", index=False)
    pd.DataFrame([
        {"HITO": "62", "RUTA": str(H62), "EXCEL": str(EX62), "SHA256": sha256(EX62)},
        {"HITO": "63", "RUTA": str(H63), "EXCEL": str(EX63), "SHA256": sha256(EX63)},
        {"HITO": "67", "RUTA": str(H67), "EXCEL": str(EX67), "SHA256": sha256(EX67)},
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "76", "RUTA": str(H76), "EXCEL": str(EX76), "SHA256": sha256(EX76)},
    ]).to_excel(writer, sheet_name="17_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 77,
        "decision_218": "APROBADO_CIERRE_SIN_CAMBIO",
        "decision_21": "PENDIENTE_REVISION_SITUACION_ACADEMICA",
        "decision_17": "APROBADO_CRITERIO_USUARIO_PERIODO_1_1_2_3_2",
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
        "subida_sies_permitida": "NO",
    }]).to_excel(writer, sheet_name="18_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "Registro decisiones usuario H68 256 columnas 16-19 archivo 5809",
    "hito": 77,
    "decision_218": "APROBADO_CIERRE_SIN_CAMBIO",
    "decision_21": "PENDIENTE_REVISION_SITUACION_ACADEMICA",
    "decision_17": "APROBADO_CRITERIO_USUARIO_PERIODO_1_1_2_3_2",
    "estado_21": decision_21_estado,
    "estado_17": decision_17_estado,
    "hay_combo_eliminado_vigente": bool(hay_combo),
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h77_registro_decisiones_usuario_h68_256.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[9/10] Verificando productos...", flush=True)

assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert len(detalle218) == 218
assert len(detalle21) == 21
assert len(detalle17) == 17

print("[10/10] Mostrando resultado terminal completo...", flush=True)

print()
print("=" * 160)
print("HITO 77 — REGISTRO DECISIONES USUARIO H68 256 GENERADO")
print("=" * 160)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("218 COLUMNA_19_SOLO_A: APROBADO CERRAR SIN CAMBIO")
print("21 SIN REGISTROS 2025: PENDIENTE — revisar situación académica")
print("17 PERIODO_NO_1_2: APROBADO criterio usuario PERIODO 1=1; PERIODO 2/3=2")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("DECISIONES USUARIO", decisiones_usuario)
imprimir("SITUACION ACADEMICA 21 — VISTA TERMINAL", vista21)
imprimir("RESUMEN ESTADOS/SITUACION 21", resumen_estados)
imprimir("COMBINACIONES ELIMINADO | VIGENTE DETECTADAS", combos_df)
imprimir("PERIODOS 17 — VISTA TERMINAL", vista17)
imprimir("MAPEO USUARIO PERIODOS", resumen_periodos)
imprimir("PERIODOS NO DEFINIDOS POR USUARIO", periodos_no_definidos)
imprimir("CONTROL CARGA", control_carga)

print()
print("=" * 160)
print("ARCHIVOS H77")
print("=" * 160)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 160)

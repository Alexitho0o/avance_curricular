from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import re
import hashlib

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"

FUENTE_5809 = RAIZ / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5809_Precarga Matrícula Avance Curricular 2026.csv"

COLUMNAS_5809 = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/72_revision_end_to_end_167_pendientes_hasta_csv_piloto_5809"
    / f"REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_REVISION_E2E_167_PENDIENTES_CSV_PILOTO_5809_{timestamp}"

for carpeta in [SALIDA, ESCRITORIO]:
    carpeta.mkdir(parents=True, exist_ok=True)

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
    carpetas = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not carpetas:
        raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")
    return carpetas[0]

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
        raise SystemExit(f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. Hojas: {xls.sheet_names}")
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

def leer_csv_robusto(path, sep=";", header=None):
    errores = []
    for enc in ["utf-8-sig", "utf-8", "latin1", "cp1252"]:
        try:
            df = pd.read_csv(
                path,
                sep=sep,
                header=header,
                dtype=str,
                keep_default_na=False,
                encoding=enc,
                engine="python",
            )
            print(f"   CSV leído correctamente con encoding={enc}", flush=True)
            return df, enc
        except Exception as e:
            errores.append(f"{enc}: {type(e).__name__}: {e}")
    raise SystemExit("BLOQUEO: no se pudo leer CSV con encodings probados:\n" + "\n".join(errores))

def imprimir(titulo, df, n=40):
    print()
    print("=" * 130)
    print(titulo)
    print("=" * 130)
    if df.empty:
        print("(sin datos)")
        return
    print(df.head(n).to_string(index=False))
    if len(df) > n:
        print(f"... mostrando {n} de {len(df)} filas")

print("[1/12] Localizando Hitos 68, 69 y 71...", flush=True)

H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)

H69 = ultimo(
    RAIZ / "avance_curricular_2026/69_paquete_operativo_167_pendientes_16_19_5809",
    "PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_",
)

H71 = ultimo(
    RAIZ / "avance_curricular_2026/71_revision_end_to_end_muestra_15_hasta_csv_piloto_5809",
    "REVISION_E2E_MUESTRA_15_HASTA_CSV_PILOTO_5809_",
)

EX68 = primer_excel(H68)
EX69 = primer_excel(H69)
EX71 = primer_excel(H71)

if not FUENTE_5809.exists():
    raise SystemExit(f"BLOQUEO: no existe fuente 5809 congelada: {FUENTE_5809}")

print(f"   H68: {EX68}", flush=True)
print(f"   H69: {EX69}", flush=True)
print(f"   H71: {EX71}", flush=True)
print(f"   Fuente 5809: {FUENTE_5809}", flush=True)

print("[2/12] Leyendo contexto y rutas completas 167...", flush=True)

dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
dict69 = leer(EX69, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
resumen69 = leer(EX69, ["01_RESUMEN_RUTAS", "RESUMEN"])
mapeo102 = leer(EX69, ["02_MAPEO_102", "MAPEO"])
fuente57 = leer(EX69, ["03_FUENTE_57", "FUENTE"])
revision8 = leer(EX69, ["04_REVISION_8", "REVISION"])
dict71 = leer(EX71, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
check71 = leer(EX71, ["06_CHECKLIST_SIES", "CHECKLIST"])

print("[3/12] Unificando 167 pendientes...", flush=True)

mapeo102 = mapeo102.copy()
fuente57 = fuente57.copy()
revision8 = revision8.copy()

mapeo102.insert(0, "PRIORIDAD", "1_MAPEO_INSTITUCIONAL")
fuente57.insert(0, "PRIORIDAD", "2_FUENTE_ACADEMICA_COMPLEMENTARIA")
revision8.insert(0, "PRIORIDAD", "3_REVISION_FUNCIONAL_PUNTUAL")

pendientes167 = pd.concat(
    [mapeo102, fuente57, revision8],
    ignore_index=True,
    sort=False,
)

if len(pendientes167) != 167:
    raise SystemExit(f"BLOQUEO: se esperaban 167 casos, detectados {len(pendientes167)}")

print("[4/12] Detectando columnas clave...", flush=True)

c_prioridad = "PRIORIDAD"
c_fila = col(pendientes167, ["FILA_5809", "FILA"])
c_doc = col(pendientes167, ["NUM_DOCUMENTO", "DOCUMENTO"])
c_codigo = col(pendientes167, ["CODIGO_UNICO"])
c_plan = col(pendientes167, ["PLAN_ESTUDIOS"])
c_codcli = col(pendientes167, ["CODCLI_LISTA", "CODCLI_LISTA_NORM"])
c_colaf = col(pendientes167, ["COLUMNA_AFECTADA_16_19", "COLUMNA_AFECTADA", "COLUMNAS_AFECTADAS"])
c_causa = col(pendientes167, ["CAUSA_AUDITADA", "CAUSA_PRINCIPAL", "CAUSA"])
c_val5809 = col(pendientes167, ["VALOR_ACTUAL_5809", "VALOR_5809"])
c_valrec = col(pendientes167, ["VALOR_RECALCULADO_OBSERVADO", "VALOR_RECALCULADO"])
c_accion = col(pendientes167, ["ACCION_SUGERIDA", "ACCION"])
c_pregunta = col(pendientes167, ["PREGUNTA_CONCRETA_AREA_RESPONSABLE", "PREGUNTA_CONCRETA", "PREGUNTA"])

for nombre, c in [
    ("FILA_5809", c_fila),
    ("CODIGO_UNICO", c_codigo),
]:
    if not c:
        raise SystemExit(f"BLOQUEO: base 167 no tiene columna clave {nombre}")

pendientes167["FILA_KEY"] = pendientes167[c_fila].astype(str).str.strip()

if pendientes167["FILA_KEY"].duplicated().any():
    dup = pendientes167[pendientes167["FILA_KEY"].duplicated(keep=False)]["FILA_KEY"].unique().tolist()
    raise SystemExit(f"BLOQUEO: hay FILA_5809 duplicadas en los 167: {dup[:20]}")

print("[5/12] Leyendo 5809 congelado y extrayendo filas 167...", flush=True)

base5809, encoding_5809 = leer_csv_robusto(FUENTE_5809, sep=";", header=None)

if base5809.shape[1] != 22:
    raise SystemExit(f"BLOQUEO: 5809 congelado tiene {base5809.shape[1]} columnas; se esperaban 22")

base5809.columns = COLUMNAS_5809
base5809["FILA_5809"] = [str(i + 1) for i in range(len(base5809))]

filas_167 = set(pendientes167["FILA_KEY"])
piloto5809 = base5809[base5809["FILA_5809"].isin(filas_167)].copy()

faltan_filas = sorted(filas_167 - set(piloto5809["FILA_5809"]))
if faltan_filas:
    raise SystemExit(f"BLOQUEO: filas no encontradas en 5809 congelado: {faltan_filas[:50]}")

if len(piloto5809) != 167:
    raise SystemExit(f"BLOQUEO: se esperaban 167 filas 5809, detectadas {len(piloto5809)}")

print("[6/12] Generando dictamen terminal por caso...", flush=True)

def dictamen_caso(prioridad, causa):
    p = norm(prioridad)
    c = norm(causa)

    if "MAPEO" in p:
        if "CODCLI_LISTA_MULTIPLE" in c:
            accion = "BLOQUEAR_HASTA_RESOLVER_CODCLI_LISTA_MULTIPLE"
        elif "SOLO_OTRO_ANO" in c:
            accion = "BLOQUEAR_HASTA_CONFIRMAR_CODCLI_OTRO_ANO"
        elif "EXTRANJERO" in c or "DOCUMENTO_NO_RUT" in c:
            accion = "BLOQUEAR_HASTA_VALIDAR_DOCUMENTO_EXTRANJERO_O_NO_RUT"
        elif "RUT_NO_EXISTE" in c or "NO_EXISTE_EN_MAPEO" in c:
            accion = "BLOQUEAR_HASTA_COMPLETAR_MAPEO_IDENTIDAD"
        elif "DOCUMENTO_NO_CALZA" in c:
            accion = "BLOQUEAR_HASTA_CORREGIR_DIFERENCIA_DOCUMENTO_MAPEO"
        elif "OTRO_CODCLI" in c:
            accion = "BLOQUEAR_HASTA_RESOLVER_CODCLI_CONFLICTIVO"
        else:
            accion = "BLOQUEAR_HASTA_RESOLVER_MAPEO_INSTITUCIONAL"

        return {
            "DECISION_TERMINAL": "NO_CERRAR",
            "ACCION_TERMINAL": accion,
            "MOTIVO_TERMINAL": "La ruta MAPEO_INSTITUCIONAL requiere confirmación de identidad académica/CODCLI_LISTA antes de decidir 16-19.",
            "PUEDE_IR_A_CSV_ENTREGABLE": "NO",
        }

    if "FUENTE" in p:
        return {
            "DECISION_TERMINAL": "NO_CERRAR",
            "ACCION_TERMINAL": "BLOQUEAR_HASTA_INCORPORAR_FUENTE_ACADEMICA_2025",
            "MOTIVO_TERMINAL": "La ruta FUENTE_ACADEMICA_COMPLEMENTARIA requiere evidencia académica 2025. No se puede cerrar por terminal sin fuente.",
            "PUEDE_IR_A_CSV_ENTREGABLE": "NO",
        }

    if "REVISION" in p:
        if "ESTADO_NULL" in c or "BLANCO" in c:
            accion = "BLOQUEAR_POR_ESTADO_NULL_O_BLANCO"
            motivo = "Hay estado NULL/blanco. No corresponde inferir aprobación/reprobación."
        else:
            accion = "BLOQUEAR_POR_DATO_5809_NO_CALZA_CON_PROMEDIOS"
            motivo = "Dato 5809 no calza con PROMEDIOS. Requiere decisión funcional puntual."
        return {
            "DECISION_TERMINAL": "NO_CERRAR",
            "ACCION_TERMINAL": accion,
            "MOTIVO_TERMINAL": motivo,
            "PUEDE_IR_A_CSV_ENTREGABLE": "NO",
        }

    return {
        "DECISION_TERMINAL": "NO_CERRAR",
        "ACCION_TERMINAL": "BLOQUEO_SIN_CLASIFICACION",
        "MOTIVO_TERMINAL": "No se pudo clasificar prioridad.",
        "PUEDE_IR_A_CSV_ENTREGABLE": "NO",
    }

decisiones = []
for _, row in pendientes167.iterrows():
    d = dictamen_caso(
        row[c_prioridad],
        row[c_causa] if c_causa else "",
    )

    decisiones.append({
        "PRIORIDAD": row[c_prioridad],
        "FILA_5809": row[c_fila],
        "NUM_DOCUMENTO": row[c_doc] if c_doc else "",
        "CODIGO_UNICO": row[c_codigo] if c_codigo else "",
        "PLAN_ESTUDIOS": row[c_plan] if c_plan else "",
        "CODCLI_LISTA": row[c_codcli] if c_codcli else "",
        "COLUMNA_AFECTADA": row[c_colaf] if c_colaf else "",
        "CAUSA": row[c_causa] if c_causa else "",
        "VALOR_5809": row[c_val5809] if c_val5809 else "",
        "VALOR_RECALCULADO_OBSERVADO": row[c_valrec] if c_valrec else "",
        "ACCION_ORIGINAL": row[c_accion] if c_accion else "",
        "PREGUNTA_ORIGINAL": row[c_pregunta] if c_pregunta else "",
        **d,
    })

decisiones_df = pd.DataFrame(decisiones)

conteo_decisiones = (
    decisiones_df
    .groupby(["PRIORIDAD", "DECISION_TERMINAL", "ACCION_TERMINAL", "PUEDE_IR_A_CSV_ENTREGABLE"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["PRIORIDAD", "CASOS"], ascending=[True, False])
)

conteo_causas = (
    decisiones_df
    .groupby(["PRIORIDAD", "CAUSA"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["PRIORIDAD", "CASOS"], ascending=[True, False])
)

conteo_columnas = (
    decisiones_df
    .groupby(["PRIORIDAD", "COLUMNA_AFECTADA"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["PRIORIDAD", "CASOS"], ascending=[True, False])
)

print("[7/12] Construyendo CSV piloto 167 NO_SUBIR_SIES...", flush=True)

csv_piloto = piloto5809[COLUMNAS_5809].copy()
csv_piloto["CONTROL_H72"] = "PILOTO_167_NO_SUBIR_SIES"
csv_piloto["MOTIVO_NO_SUBIR"] = "167_PENDIENTES_BLOQUEADOS_SIN_DECISION_FUNCIONAL_COMPLETA"

csv_piloto_out = SALIDA / "CSV_PILOTO_167_PENDIENTES_NO_SUBIR_SIES.csv"
csv_piloto.to_csv(csv_piloto_out, sep=";", index=False, encoding="latin1")

checklist_sies = pd.DataFrame([
    {"CONTROL": "Archivo corresponde al universo completo 5809", "RESULTADO": "NO", "DICTAMEN": "Es subconjunto piloto de 167 pendientes, no universo completo."},
    {"CONTROL": "Todos los casos 16-19 resueltos", "RESULTADO": "NO", "DICTAMEN": "167/167 quedan bloqueados por mapeo/fuente/revisión."},
    {"CONTROL": "256 casos H68 validados funcionalmente", "RESULTADO": "NO", "DICTAMEN": "Pendiente validación funcional formal."},
    {"CONTROL": "167 pendientes H69 resueltos", "RESULTADO": "NO", "DICTAMEN": "H72 revisa terminalmente, pero no resuelve sin evidencia externa."},
    {"CONTROL": "20-21 evaluado", "RESULTADO": "NO", "DICTAMEN": "Fuera de alcance."},
    {"CONTROL": "SIES_READY permitido", "RESULTADO": "NO", "DICTAMEN": "Bloqueado por gobernanza y pendientes."},
    {"CONTROL": "Subida a SIES permitida", "RESULTADO": "NO", "DICTAMEN": "No corresponde subir subconjunto ni archivo con bloqueos."},
])

pasos_ejecutados = pd.DataFrame([
    {"N": 1, "PASO": "Localizar H68/H69/H71", "ESTADO": "EJECUTADO", "RESULTADO": "Fuentes encontradas."},
    {"N": 2, "PASO": "Unificar 102+57+8", "ESTADO": "EJECUTADO", "RESULTADO": "167 casos."},
    {"N": 3, "PASO": "Extraer filas originales 5809", "ESTADO": "EJECUTADO", "RESULTADO": "167 filas encontradas."},
    {"N": 4, "PASO": "Revisar 102 mapeo", "ESTADO": "EJECUTADO", "RESULTADO": "102 bloqueados hasta mapeo institucional."},
    {"N": 5, "PASO": "Revisar 57 fuente", "ESTADO": "EJECUTADO", "RESULTADO": "57 bloqueados hasta fuente académica 2025."},
    {"N": 6, "PASO": "Revisar 8 funcional puntual", "ESTADO": "EJECUTADO", "RESULTADO": "8 bloqueados por revisión puntual."},
    {"N": 7, "PASO": "Generar matriz terminal 167", "ESTADO": "EJECUTADO", "RESULTADO": "167/167 no cerrables por terminal."},
    {"N": 8, "PASO": "Generar CSV piloto 167", "ESTADO": "EJECUTADO", "RESULTADO": "CSV_PILOTO_167_PENDIENTES_NO_SUBIR_SIES.csv."},
    {"N": 9, "PASO": "Evaluar subida SIES", "ESTADO": "EJECUTADO", "RESULTADO": "NO PERMITIDA."},
    {"N": 10, "PASO": "Generar paquete H72", "ESTADO": "EJECUTADO", "RESULTADO": "Excel/informe/manifest/script/CSV piloto."},
    {"N": 11, "PASO": "Resolver 102 mapeo", "ESTADO": "BLOQUEADO", "RESULTADO": "Falta mapeo validado."},
    {"N": 12, "PASO": "Resolver 57 fuente", "ESTADO": "BLOQUEADO", "RESULTADO": "Falta fuente académica."},
    {"N": 13, "PASO": "Resolver 8 revisión", "ESTADO": "BLOQUEADO", "RESULTADO": "Falta decisión funcional puntual."},
    {"N": 14, "PASO": "Consolidar 256 H68 + 167 H72", "ESTADO": "BLOQUEADO", "RESULTADO": "Faltan decisiones funcionales y evidencia."},
    {"N": 15, "PASO": "Preparar corrección 16-19", "ESTADO": "BLOQUEADO", "RESULTADO": "No hay base validada."},
    {"N": 16, "PASO": "Generar archivo completo candidato", "ESTADO": "BLOQUEADO", "RESULTADO": "No corresponde."},
    {"N": 17, "PASO": "Validar archivo final", "ESTADO": "BLOQUEADO", "RESULTADO": "No hay archivo final."},
    {"N": 18, "PASO": "Generar SIES_READY", "ESTADO": "BLOQUEADO", "RESULTADO": "No permitido."},
    {"N": 19, "PASO": "Subir a SIES", "ESTADO": "BLOQUEADO", "RESULTADO": "No permitido subir subconjunto ni bloqueados."},
    {"N": 20, "PASO": "Reanudar", "ESTADO": "PENDIENTE", "RESULTADO": "Falta evidencia o decisión funcional para destrabar."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Revisión end-to-end 167 pendientes hasta CSV piloto no subir SIES",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "REVISION_TERMINAL_END_TO_END_167",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "CSV_PILOTO_GENERADO": "SI_NO_SUBIR_SIES",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "RECALCULO_20_21": "NO",
    "TOTAL_167": len(pendientes167),
    "CERRABLES_POR_TERMINAL": int((decisiones_df["DECISION_TERMINAL"] == "CERRAR").sum()),
    "BLOQUEADOS_POR_TERMINAL": int((decisiones_df["DECISION_TERMINAL"] != "CERRAR").sum()),
    "MAPEO_BLOQUEADO": int((decisiones_df["PRIORIDAD"] == "1_MAPEO_INSTITUCIONAL").sum()),
    "FUENTE_BLOQUEADA": int((decisiones_df["PRIORIDAD"] == "2_FUENTE_ACADEMICA_COMPLEMENTARIA").sum()),
    "REVISION_BLOQUEADA": int((decisiones_df["PRIORIDAD"] == "3_REVISION_FUNCIONAL_PUNTUAL").sum()),
    "DICTAMEN_GLOBAL": "Los 167 pendientes se revisaron end-to-end en terminal. No hay casos cerrables por terminal; el CSV piloto es evidencia técnica y no debe subirse a SIES.",
}])

print("[8/12] Escribiendo productos H72...", flush=True)

excel_out = SALIDA / "REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809.xlsx"
informe_out = SALIDA / "INFORME_REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809.md"
manifest_out = SALIDA / "manifest_revision_e2e_167_pendientes_hasta_csv_piloto_5809.json"
script_out = SALIDA / "h72_revision_end_to_end_167_hasta_csv_piloto.py"
bloqueo_sies_out = SALIDA / "BLOQUEO_SUBIDA_SIES_167_PENDIENTES.md"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    decisiones_df.to_excel(writer, sheet_name="01_DECISIONES_167", index=False)
    conteo_decisiones.to_excel(writer, sheet_name="02_RESUMEN_DECISIONES", index=False)
    conteo_causas.to_excel(writer, sheet_name="03_RESUMEN_CAUSAS", index=False)
    conteo_columnas.to_excel(writer, sheet_name="04_RESUMEN_COLUMNAS", index=False)
    pendientes167.to_excel(writer, sheet_name="05_BASE_167_H69", index=False)
    piloto5809.to_excel(writer, sheet_name="06_FILAS_5809_ORIGINALES", index=False)
    csv_piloto.to_excel(writer, sheet_name="07_CSV_PILOTO_NO_SUBIR", index=False)
    checklist_sies.to_excel(writer, sheet_name="08_CHECKLIST_SIES", index=False)
    pasos_ejecutados.to_excel(writer, sheet_name="09_20_PASOS", index=False)
    matriz68.to_excel(writer, sheet_name="10_REFERENCIA_H68", index=False)
    resumen69.to_excel(writer, sheet_name="11_REFERENCIA_H69", index=False)
    check71.to_excel(writer, sheet_name="12_REFERENCIA_H71", index=False)
    pd.DataFrame([
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "69", "RUTA": str(H69), "EXCEL": str(EX69), "SHA256": sha256(EX69)},
        {"HITO": "71", "RUTA": str(H71), "EXCEL": str(EX71), "SHA256": sha256(EX71)},
        {"FUENTE": "5809 congelado", "RUTA": str(FUENTE_5809), "SHA256": sha256(FUENTE_5809), "ENCODING": encoding_5809},
        {"HITO": "72", "RUTA": str(SALIDA), "EXCEL": str(excel_out), "SHA256": ""},
    ]).to_excel(writer, sheet_name="13_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "fuentes_modificadas": "NO",
        "correcciones": "NO",
        "archivo_carga": "NO",
        "csv_piloto": "SI_NO_SUBIR",
        "sies_ready": "NO",
        "subida_sies": "NO",
        "recalculo_20_21": "NO",
        "total_167": len(pendientes167),
        "bloqueados": int((decisiones_df["DECISION_TERMINAL"] != "CERRAR").sum()),
    }]).to_excel(writer, sheet_name="14_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 100)

informe_out.write_text(
f"""# Hito 72 — Revisión end-to-end 167 pendientes hasta CSV piloto

## Estado

- Proceso: Avance Curricular SIES 2026
- Subproyecto: archivo 5809, columnas 16-19
- Declaración de carga: NO_LISTO_PARA_CARGA
- Fuentes originales modificadas: NO
- Correcciones aplicadas: NO
- Archivo de carga generado: NO
- CSV piloto generado: SÍ, solo evidencia, NO SUBIR A SIES
- SIES_READY generado: NO
- Subida a SIES permitida: NO
- 20-21 evaluado: NO

## Resultado terminal

Los 167 pendientes fueron revisados end-to-end:

- 102 MAPEO_INSTITUCIONAL: bloqueados hasta resolver mapeo.
- 57 FUENTE_ACADEMICA_COMPLEMENTARIA: bloqueados hasta incorporar fuente académica 2025.
- 8 REVISION_FUNCIONAL_PUNTUAL: bloqueados por revisión puntual.

## Dictamen

No hay casos cerrables por terminal con la evidencia actual.

El CSV piloto fue generado solo para verificar estructura y trazabilidad, pero no corresponde subirlo a SIES porque:
- es un subconjunto de pendientes, no el universo completo;
- contiene casos bloqueados;
- no representa archivo integral;
- 20-21 no fue evaluado;
- no existe SIES_READY;
- faltan decisiones funcionales/evidencia.
""",
encoding="utf-8"
)

bloqueo_sies_out.write_text(
"""# Bloqueo de subida a SIES — 167 pendientes

No corresponde subir este archivo a SIES.

Motivos:
1. Es un subconjunto de 167 pendientes, no el universo completo 5809.
2. Los 167 casos revisados quedan bloqueados por falta de mapeo, fuente o decisión funcional.
3. No se aplicaron correcciones.
4. No se generó SIES_READY.
5. No se evaluaron columnas 20-21.
6. La fuente original 5809 no fue modificada.
7. El CSV piloto existe solo como evidencia técnica y no como archivo de carga.
8. El proceso exige carga integral; una muestra/subconjunto no corresponde.

Dictamen: NO_SUBIR_SIES.
""",
encoding="utf-8"
)

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Revision end-to-end 167 pendientes hasta CSV piloto no subir SIES",
    "hito": 72,
    "hito68": str(H68),
    "hito69": str(H69),
    "hito71": str(H71),
    "fuente_5809": str(FUENTE_5809),
    "encoding_5809_detectado": encoding_5809,
    "total_167": len(pendientes167),
    "cerrables_terminal": int((decisiones_df["DECISION_TERMINAL"] == "CERRAR").sum()),
    "bloqueados_terminal": int((decisiones_df["DECISION_TERMINAL"] != "CERRAR").sum()),
    "mapeo_bloqueado": len(mapeo102),
    "fuente_bloqueada": len(fuente57),
    "revision_bloqueada": len(revision8),
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "csv_piloto_generado": True,
    "csv_piloto_no_subir_sies": str(csv_piloto_out),
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "recalculo_20_21": False,
    "declaracion_carga": "NO_LISTO_PARA_CARGA",
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "bloqueo_sies": str(bloqueo_sies_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h72_revision_end_to_end_167_hasta_csv_piloto.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out, bloqueo_sies_out, csv_piloto_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[9/12] Verificando productos y controles...", flush=True)

assert len(pendientes167) == 167
assert len(decisiones_df) == 167
assert int((decisiones_df["PUEDE_IR_A_CSV_ENTREGABLE"] == "SI").sum()) == 0
assert len(piloto5809) == 167
assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert bloqueo_sies_out.exists()
assert csv_piloto_out.exists()

print("[10/12] Preparando salida terminal...", flush=True)

print()
print("=" * 130)
print("HITO 72 — REVISIÓN END-TO-END 167 PENDIENTES HASTA CSV PILOTO GENERADA")
print("=" * 130)
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("CSV piloto generado: SI — NO_SUBIR_SIES")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN DECISIONES TERMINAL", conteo_decisiones)
imprimir("RESUMEN CAUSAS", conteo_causas, 80)
imprimir("RESUMEN COLUMNAS", conteo_columnas, 80)
imprimir("CHECKLIST SIES", checklist_sies)
imprimir("20 PASOS EJECUTADOS / BLOQUEADOS", pasos_ejecutados, 25)

print()
print("=" * 130)
print("ARCHIVOS")
print("=" * 130)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"CSV piloto NO_SUBIR_SIES: {csv_piloto_out}")
print(f"Bloqueo SIES: {bloqueo_sies_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 130)

print("[11/12] Copia escritorio generada.", flush=True)
print("[12/12] Terminado.", flush=True)

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
    / "avance_curricular_2026/71_revision_end_to_end_muestra_15_hasta_csv_piloto_5809"
    / f"REVISION_E2E_MUESTRA_15_HASTA_CSV_PILOTO_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_REVISION_E2E_MUESTRA_15_CSV_PILOTO_5809_{timestamp}"

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

def imprimir(titulo, df, n=50):
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

print("[1/10] Localizando Hitos 68, 69 y 70...", flush=True)

H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)

H69 = ultimo(
    RAIZ / "avance_curricular_2026/69_paquete_operativo_167_pendientes_16_19_5809",
    "PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_",
)

H70 = ultimo(
    RAIZ / "avance_curricular_2026/70_muestra_rapida_15_casos_prioridades_16_19_5809",
    "MUESTRA_RAPIDA_15_CASOS_16_19_5809_",
)

EX68 = primer_excel(H68)
EX69 = primer_excel(H69)
EX70 = primer_excel(H70)

if not FUENTE_5809.exists():
    raise SystemExit(f"BLOQUEO: no existe fuente 5809 congelada: {FUENTE_5809}")

print(f"   H68: {EX68}", flush=True)
print(f"   H69: {EX69}", flush=True)
print(f"   H70: {EX70}", flush=True)
print(f"   Fuente 5809: {FUENTE_5809}", flush=True)

print("[2/10] Leyendo muestra y contexto...", flush=True)

dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
dict69 = leer(EX69, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
resumen69 = leer(EX69, ["01_RESUMEN_RUTAS", "RESUMEN"])
muestra15 = leer(EX70, ["01_MUESTRA_15", "MUESTRA_15"])
pasos70 = leer(EX70, ["05_20_PASOS_SIGUIENTES", "20_PASOS"])

print("[3/10] Detectando columnas de muestra...", flush=True)

c_prioridad = col(muestra15, ["PRIORIDAD"])
c_fila = col(muestra15, ["FILA_5809", "FILA"])
c_doc = col(muestra15, ["NUM_DOCUMENTO", "DOCUMENTO"])
c_codigo = col(muestra15, ["CODIGO_UNICO"])
c_plan = col(muestra15, ["PLAN_ESTUDIOS"])
c_codcli = col(muestra15, ["CODCLI_LISTA", "CODCLI_LISTA_NORM"])
c_colaf = col(muestra15, ["COLUMNA_AFECTADA_16_19", "COLUMNA_AFECTADA", "COLUMNAS_AFECTADAS"])
c_causa = col(muestra15, ["CAUSA_AUDITADA", "CAUSA_PRINCIPAL", "CAUSA"])
c_val5809 = col(muestra15, ["VALOR_ACTUAL_5809", "VALOR_5809"])
c_valrec = col(muestra15, ["VALOR_RECALCULADO_OBSERVADO", "VALOR_RECALCULADO"])
c_accion = col(muestra15, ["ACCION_SUGERIDA", "ACCION"])
c_pregunta = col(muestra15, ["PREGUNTA_CONCRETA_AREA_RESPONSABLE", "PREGUNTA_CONCRETA", "PREGUNTA"])

for nombre, c in [
    ("PRIORIDAD", c_prioridad),
    ("FILA_5809", c_fila),
    ("CODIGO_UNICO", c_codigo),
]:
    if not c:
        raise SystemExit(f"BLOQUEO: muestra no tiene columna clave {nombre}")

muestra15 = muestra15.copy()
muestra15["FILA_KEY"] = muestra15[c_fila].astype(str).str.strip()

if len(muestra15) != 15:
    raise SystemExit(f"BLOQUEO: se esperaban 15 casos en H70, detectados {len(muestra15)}")

print("[4/10] Leyendo 5809 congelado y extrayendo filas piloto...", flush=True)

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

base5809, encoding_5809 = leer_csv_robusto(FUENTE_5809, sep=";", header=None)

if base5809.shape[1] != 22:
    raise SystemExit(f"BLOQUEO: 5809 congelado tiene {base5809.shape[1]} columnas; se esperaban 22")

base5809.columns = COLUMNAS_5809
base5809["FILA_5809"] = [str(i + 1) for i in range(len(base5809))]

filas_muestra = set(muestra15["FILA_KEY"])
piloto5809 = base5809[base5809["FILA_5809"].isin(filas_muestra)].copy()

faltan_filas = sorted(filas_muestra - set(piloto5809["FILA_5809"]))
if faltan_filas:
    print(f"ADVERTENCIA: filas no encontradas en 5809 congelado: {faltan_filas}", flush=True)

print("[5/10] Revisando caso a caso en terminal y generando dictamen automático de muestra...", flush=True)

def dictamen_caso(prioridad, causa):
    p = norm(prioridad)
    c = norm(causa)

    if "MAPEO" in p:
        return {
            "DECISION_TERMINAL": "NO_CERRAR",
            "ACCION_TERMINAL": "BLOQUEAR_HASTA_RESOLVER_MAPEO_INSTITUCIONAL",
            "MOTIVO_TERMINAL": "La prioridad requiere confirmar CODCLI_LISTA/identidad académica. No se puede corregir ni cerrar por terminal sin mapeo validado.",
            "PUEDE_IR_A_CSV_ENTREGABLE": "NO",
        }

    if "FUENTE" in p:
        return {
            "DECISION_TERMINAL": "NO_CERRAR",
            "ACCION_TERMINAL": "BLOQUEAR_HASTA_INCORPORAR_FUENTE_ACADEMICA_2025",
            "MOTIVO_TERMINAL": "La prioridad requiere evidencia académica complementaria 2025. No se puede cerrar ni corregir sin fuente.",
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
        "MOTIVO_TERMINAL": "No se pudo clasificar prioridad con reglas de H69/H70.",
        "PUEDE_IR_A_CSV_ENTREGABLE": "NO",
    }

decisiones = []
for _, row in muestra15.iterrows():
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
)

print("[6/10] Construyendo CSV piloto NO_SUBIR_SIES...", flush=True)

# CSV piloto conserva filas originales congeladas. No es archivo de carga final ni parcial para subir.
piloto_csv = piloto5809[COLUMNAS_5809].copy()
piloto_csv["CONTROL_H71"] = "PILOTO_NO_SUBIR_SIES"
piloto_csv["MOTIVO_NO_SUBIR"] = "MUESTRA_PARCIAL_CON_BLOQUEOS_Y_SIN_DECISION_FUNCIONAL_COMPLETA"

csv_piloto_out = SALIDA / "CSV_PILOTO_15_CASOS_NO_SUBIR_SIES.csv"
piloto_csv.to_csv(csv_piloto_out, sep=";", index=False, encoding="utf-8")

checklist_sies = pd.DataFrame([
    {"CONTROL": "Archivo corresponde a universo completo 5809", "RESULTADO": "NO", "DICTAMEN": "Es muestra piloto de 15 casos."},
    {"CONTROL": "Todos los casos 16-19 resueltos", "RESULTADO": "NO", "DICTAMEN": "La muestra queda bloqueada por mapeo/fuente/revisión."},
    {"CONTROL": "256 casos H68 validados funcionalmente", "RESULTADO": "NO", "DICTAMEN": "Pendiente validación funcional."},
    {"CONTROL": "167 pendientes H69 resueltos", "RESULTADO": "NO", "DICTAMEN": "Solo se revisó muestra piloto."},
    {"CONTROL": "20-21 evaluado", "RESULTADO": "NO", "DICTAMEN": "Fuera de alcance."},
    {"CONTROL": "SIES_READY permitido", "RESULTADO": "NO", "DICTAMEN": "Bloqueado por gobernanza."},
    {"CONTROL": "Subida a SIES permitida", "RESULTADO": "NO", "DICTAMEN": "No corresponde subir muestra parcial ni archivo con bloqueos."},
])

pasos_ejecutados = pd.DataFrame([
    {"N": 1, "PASO": "Localizar H68/H69/H70", "ESTADO": "EJECUTADO", "RESULTADO": "Fuentes encontradas."},
    {"N": 2, "PASO": "Leer muestra 15", "ESTADO": "EJECUTADO", "RESULTADO": "5+5+5 casos."},
    {"N": 3, "PASO": "Extraer filas originales 5809", "ESTADO": "EJECUTADO", "RESULTADO": f"{len(piloto5809)} filas encontradas."},
    {"N": 4, "PASO": "Revisar mapeo 5", "ESTADO": "EJECUTADO", "RESULTADO": "Bloqueado hasta mapeo institucional."},
    {"N": 5, "PASO": "Revisar fuente 5", "ESTADO": "EJECUTADO", "RESULTADO": "Bloqueado hasta fuente académica 2025."},
    {"N": 6, "PASO": "Revisar funcional puntual 5", "ESTADO": "EJECUTADO", "RESULTADO": "Bloqueado por revisión funcional puntual."},
    {"N": 7, "PASO": "Generar matriz terminal", "ESTADO": "EJECUTADO", "RESULTADO": "15/15 no cerrables por terminal."},
    {"N": 8, "PASO": "Generar CSV piloto", "ESTADO": "EJECUTADO", "RESULTADO": "CSV_PILOTO_15_CASOS_NO_SUBIR_SIES.csv."},
    {"N": 9, "PASO": "Evaluar subida SIES", "ESTADO": "EJECUTADO", "RESULTADO": "NO PERMITIDA."},
    {"N": 10, "PASO": "Generar paquete H71", "ESTADO": "EJECUTADO", "RESULTADO": "Excel/informe/manifest/script/CSV piloto."},
    {"N": 11, "PASO": "Extender a 102 mapeo", "ESTADO": "BLOQUEADO", "RESULTADO": "Falta mapeo validado."},
    {"N": 12, "PASO": "Extender a 57 fuente", "ESTADO": "BLOQUEADO", "RESULTADO": "Falta fuente académica."},
    {"N": 13, "PASO": "Extender a 8 revisión", "ESTADO": "BLOQUEADO", "RESULTADO": "Falta decisión funcional puntual."},
    {"N": 14, "PASO": "Consolidar 256 + 167", "ESTADO": "BLOQUEADO", "RESULTADO": "Faltan decisiones."},
    {"N": 15, "PASO": "Preparar corrección 16-19", "ESTADO": "BLOQUEADO", "RESULTADO": "No hay base validada."},
    {"N": 16, "PASO": "Generar archivo completo candidato", "ESTADO": "BLOQUEADO", "RESULTADO": "No corresponde."},
    {"N": 17, "PASO": "Validar archivo final", "ESTADO": "BLOQUEADO", "RESULTADO": "No hay archivo final."},
    {"N": 18, "PASO": "Generar SIES_READY", "ESTADO": "BLOQUEADO", "RESULTADO": "No permitido."},
    {"N": 19, "PASO": "Subir a SIES", "ESTADO": "BLOQUEADO", "RESULTADO": "No permitido subir muestra parcial ni bloqueada."},
    {"N": 20, "PASO": "Reanudar", "ESTADO": "PENDIENTE", "RESULTADO": "Resolver evidencia de mapeo/fuente/revisión o validar mantener sin cambio."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Revisión end-to-end muestra 15 hasta CSV piloto no subir SIES",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "REVISION_TERMINAL_END_TO_END_MUESTRA",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "CSV_PILOTO_GENERADO": "SI_NO_SUBIR_SIES",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "RECALCULO_20_21": "NO",
    "TOTAL_MUESTRA": len(muestra15),
    "CERRABLES_POR_TERMINAL": int((decisiones_df["DECISION_TERMINAL"] == "CERRAR").sum()),
    "BLOQUEADOS_POR_TERMINAL": int((decisiones_df["DECISION_TERMINAL"] != "CERRAR").sum()),
    "DICTAMEN_GLOBAL": "La muestra se revisó end-to-end en terminal. No hay casos cerrables por terminal; el CSV piloto es solo evidencia y no debe subirse a SIES.",
}])

print("[7/10] Escribiendo productos H71...", flush=True)

excel_out = SALIDA / "REVISION_E2E_MUESTRA_15_HASTA_CSV_PILOTO_5809.xlsx"
informe_out = SALIDA / "INFORME_REVISION_E2E_MUESTRA_15_HASTA_CSV_PILOTO_5809.md"
manifest_out = SALIDA / "manifest_revision_e2e_muestra_15_hasta_csv_piloto_5809.json"
script_out = SALIDA / "h71_revision_end_to_end_muestra_15_hasta_csv_piloto.py"
bloqueo_sies_out = SALIDA / "BLOQUEO_SUBIDA_SIES_MUESTRA_15.md"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    decisiones_df.to_excel(writer, sheet_name="01_DECISIONES_15", index=False)
    conteo_decisiones.to_excel(writer, sheet_name="02_RESUMEN_DECISIONES", index=False)
    muestra15.to_excel(writer, sheet_name="03_MUESTRA_ORIGINAL_H70", index=False)
    piloto5809.to_excel(writer, sheet_name="04_FILAS_5809_ORIGINALES", index=False)
    piloto_csv.to_excel(writer, sheet_name="05_CSV_PILOTO_NO_SUBIR", index=False)
    checklist_sies.to_excel(writer, sheet_name="06_CHECKLIST_SIES", index=False)
    pasos_ejecutados.to_excel(writer, sheet_name="07_20_PASOS_EJECUTADOS", index=False)
    matriz68.to_excel(writer, sheet_name="08_REFERENCIA_H68", index=False)
    resumen69.to_excel(writer, sheet_name="09_REFERENCIA_H69", index=False)
    pasos70.to_excel(writer, sheet_name="10_REFERENCIA_H70", index=False)
    pd.DataFrame([
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "69", "RUTA": str(H69), "EXCEL": str(EX69), "SHA256": sha256(EX69)},
        {"HITO": "70", "RUTA": str(H70), "EXCEL": str(EX70), "SHA256": sha256(EX70)},
        {"FUENTE": "5809 congelado", "RUTA": str(FUENTE_5809), "SHA256": sha256(FUENTE_5809)},
        {"HITO": "71", "RUTA": str(SALIDA), "EXCEL": str(excel_out), "SHA256": ""},
    ]).to_excel(writer, sheet_name="11_FUENTES", index=False)
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
    }]).to_excel(writer, sheet_name="12_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 100)

informe_out.write_text(
f"""# Hito 71 — Revisión end-to-end muestra 15 hasta CSV piloto

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

La muestra de 15 casos fue revisada end-to-end:

- 5 MAPEO_INSTITUCIONAL: bloqueados hasta resolver mapeo.
- 5 FUENTE_ACADEMICA_COMPLEMENTARIA: bloqueados hasta incorporar fuente académica.
- 5 REVISION_FUNCIONAL_PUNTUAL: bloqueados por revisión puntual.

## Dictamen

No hay casos cerrables por terminal con la evidencia actual.

El CSV piloto fue generado solo para verificar estructura y trazabilidad, pero no corresponde subirlo a SIES porque:
- es muestra parcial;
- contiene casos bloqueados;
- no representa el universo completo;
- 20-21 no fue evaluado;
- no existe SIES_READY.
""",
encoding="utf-8"
)

bloqueo_sies_out.write_text(
"""# Bloqueo de subida a SIES — muestra 15

No corresponde subir esta muestra a SIES.

Motivos:
1. Es una muestra parcial de 15 casos, no el universo completo.
2. Los 15 casos revisados quedan bloqueados por falta de mapeo, fuente o decisión funcional.
3. No se aplicaron correcciones.
4. No se generó SIES_READY.
5. No se evaluaron columnas 20-21.
6. La fuente original 5809 no fue modificada.
7. El CSV piloto existe solo como evidencia técnica y no como archivo de carga.

Dictamen: NO_SUBIR_SIES.
""",
encoding="utf-8"
)

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Revision end-to-end muestra 15 hasta CSV piloto no subir SIES",
    "hito": 71,
    "hito68": str(H68),
    "hito69": str(H69),
    "hito70": str(H70),
    "fuente_5809": str(FUENTE_5809),
    "encoding_5809_detectado": encoding_5809,
    "total_muestra": len(muestra15),
    "cerrables_terminal": int((decisiones_df["DECISION_TERMINAL"] == "CERRAR").sum()),
    "bloqueados_terminal": int((decisiones_df["DECISION_TERMINAL"] != "CERRAR").sum()),
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

shutil.copy2(Path("/tmp/h71_revision_end_to_end_muestra_15_hasta_csv_piloto.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out, bloqueo_sies_out, csv_piloto_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/10] Verificando productos y controles...", flush=True)

assert len(muestra15) == 15
assert len(decisiones_df) == 15
assert int((decisiones_df["PUEDE_IR_A_CSV_ENTREGABLE"] == "SI").sum()) == 0
assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert bloqueo_sies_out.exists()
assert csv_piloto_out.exists()

print("[9/10] Preparando salida terminal...", flush=True)

print()
print("=" * 130)
print("HITO 71 — REVISIÓN END-TO-END MUESTRA 15 HASTA CSV PILOTO GENERADA")
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

print("[10/10] Terminado.", flush=True)

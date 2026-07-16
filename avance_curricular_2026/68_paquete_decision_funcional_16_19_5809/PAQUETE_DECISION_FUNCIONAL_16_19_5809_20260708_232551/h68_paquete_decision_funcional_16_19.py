from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import re

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809"
    / f"PAQUETE_DECISION_FUNCIONAL_16_19_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_PAQUETE_DECISION_FUNCIONAL_16_19_5809_{timestamp}"

for c in [SALIDA, ESCRITORIO]:
    c.mkdir(parents=True, exist_ok=True)

def norm(x):
    x = str(x or "").upper()
    for a, b in {"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","Ñ":"N"}.items():
        x = x.replace(a, b)
    x = re.sub(r"[^A-Z0-9]+", "_", x)
    return re.sub(r"_+", "_", x).strip("_")

def ultimo(base, prefijo):
    if not base.exists():
        raise SystemExit(f"BLOQUEO: no existe {base}")
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

def hoja(xlsx, patrones):
    xls = pd.ExcelFile(xlsx, engine="openpyxl")
    for p in patrones:
        for h in xls.sheet_names:
            if norm(p) == norm(h):
                return h
    for p in patrones:
        for h in xls.sheet_names:
            if norm(p) in norm(h):
                return h
    raise SystemExit(f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. Hojas: {xls.sheet_names}")

def leer(xlsx, patrones):
    h = hoja(xlsx, patrones)
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

print("[1/7] Localizando hitos 58, 62, 63, 66 y 67...", flush=True)

H58 = ultimo(
    RAIZ / "avance_curricular_2026/58_consolidado_resolucion_16_19_gobernado_5809",
    "CONSOLIDADO_RESOLUCION_16_19_GOBERNADO_"
)

H62 = ultimo(
    RAIZ / "avance_curricular_2026/62_decision_funcional_candidata_columna_19_solo_a_5809",
    "DECISION_FUNCIONAL_CANDIDATA_19_SOLO_A_"
)

H63 = ultimo(
    RAIZ / "avance_curricular_2026/63_terminal_revision_38_decision_funcional_restante_5809",
    "REVISION_38_DECISION_FUNCIONAL_RESTANTE_"
)

H66 = ultimo(
    RAIZ / "avance_curricular_2026/66_correccion_dictamen_post_h64_16_19_5809",
    "CORRECCION_DICTAMEN_POST_H64_16_19_"
)

H67 = ultimo(
    RAIZ / "avance_curricular_2026/67_gobernanza_periodo_raw_5809",
    "GOBERNANZA_PERIODO_RAW_5809_"
)

EX58 = primer_excel(H58)
EX62 = primer_excel(H62)
EX63 = primer_excel(H63)
EX66 = primer_excel(H66)
EX67 = primer_excel(H67)

print("[2/7] Leyendo insumos trazables...", flush=True)

d62 = leer(EX62, ["00_DICTAMEN"])
bloque21 = leer(EX63, ["03_21_ESTADO_ACAD", "21_ESTADO"])
bloque17 = leer(EX63, ["04_17_PERIODO_NO_1_2", "17_PERIODO"])
h66_dictamen = leer(EX66, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
h67_dictamen = leer(EX67, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
h67_esc = leer(EX67, ["07_ESCENARIOS_DE_MAPEO", "ESCENARIOS"])
h67_matriz = leer(EX67, ["08_MATRIZ_DECISION_PERIODO", "MATRIZ"])

# H58 puede tener nombres variables; se usa para traer/remarcar rutas restantes si existe detalle.
try:
    h58_detalle = leer(EX58, ["01_CONSOLIDADO_423", "02_DETALLE_423", "DETALLE", "CONSOLIDADO"])
except SystemExit:
    h58_detalle = pd.DataFrame()

print("[3/7] Construyendo matriz ejecutiva de decisión...", flush=True)

casos_218 = int(float(str(d62.loc[0, "CASOS_QUE_SE_CIERRAN_SIN_CAMBIO"]).replace(",", ".")))
casos_21 = len(bloque21)
casos_17 = len(bloque17)
cerrables = casos_218 + casos_21 + casos_17
pendientes_originales = 423
pendientes_restantes = pendientes_originales - cerrables

matriz_decision = pd.DataFrame([
    {
        "BLOQUE": "COLUMNA_19_SOLO_A",
        "CASOS": casos_218,
        "DECISION_SOLICITADA": "Validar cierre sin cambio",
        "TRATAMIENTO_PROPUESTO": "Mantener columna 19 contando solo A=APROBADO; excluir E=CONVALIDACION e I=HOMOLOGADO para anual 2025.",
        "RESPALDO": "Instructivo oficial Avance + dato observado PROMEDIOS + hito 66",
        "NIVEL_RESPALDO": "A/B/D",
        "CORRECCION_REQUERIDA": "NO",
        "ESTADO": "CERRABLE_SI_SE_VALIDA",
    },
    {
        "BLOQUE": "ESTADO_ACADEMICO_SIN_REGISTROS_2025",
        "CASOS": casos_21,
        "DECISION_SOLICITADA": "Validar cierre sin cambio",
        "TRATAMIENTO_PROPUESTO": "Mantener 16=NO, 17=NO, 18=0, 19=0 por ausencia de registros académicos 2025 para CODCLI_LISTA.",
        "RESPALDO": "Hito 63 + hito 66; estados observados reales: ELIMINADO 20, ELIMINADO | VIGENTE 1",
        "NIVEL_RESPALDO": "B/D",
        "CORRECCION_REQUERIDA": "NO",
        "ESTADO": "CERRABLE_SI_SE_VALIDA",
    },
    {
        "BLOQUE": "PERIODO_NO_1_2",
        "CASOS": casos_17,
        "DECISION_SOLICITADA": "Validar mantener 5809 sin cambio o mantener bloqueo",
        "TRATAMIENTO_PROPUESTO": "Escenario que calza con 5809: mantener sin cambio 17/17. No aplicar mapeo PERIODO raw sin decisión funcional.",
        "RESPALDO": "Hito 67; PERIODO raw no tiene regla oficial encontrada",
        "NIVEL_RESPALDO": "B/D/E",
        "CORRECCION_REQUERIDA": "NO, si se valida mantener 5809 sin cambio",
        "ESTADO": "CERRABLE_SOLO_CON_DECISION_FUNCIONAL_EXPLICITA",
    },
])

rutas_restantes = pd.DataFrame([
    {
        "RUTA": "MAPEO_INSTITUCIONAL",
        "CASOS": 102,
        "ACCION": "Resolver llave/CODCLI_LISTA/mapeo institucional antes de cualquier corrección.",
        "ESTADO": "PENDIENTE",
    },
    {
        "RUTA": "FUENTE_ACADEMICA_COMPLEMENTARIA",
        "CASOS": 57,
        "ACCION": "Solicitar o incorporar fuente académica complementaria.",
        "ESTADO": "PENDIENTE",
    },
    {
        "RUTA": "REVISION_FUNCIONAL_PUNTUAL",
        "CASOS": 8,
        "ACCION": "Revisión caso a caso por dato no calzante, NULL/blanco u otra inconsistencia puntual.",
        "ESTADO": "PENDIENTE",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Paquete decisión funcional 16-19 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "PAQUETE_DECISION_FUNCIONAL",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "RECALCULO_20_21": "NO",
    "PENDIENTES_16_19_ORIGINAL": pendientes_originales,
    "CERRABLES_SI_SE_VALIDAN": cerrables,
    "PENDIENTES_RESTANTES_ESTIMADOS": pendientes_restantes,
    "MAPEO_INSTITUCIONAL": 102,
    "FUENTE_ACADEMICA_COMPLEMENTARIA": 57,
    "REVISION_FUNCIONAL_PUNTUAL": 8,
    "DICTAMEN_GLOBAL": "Paquete listo para validación funcional. No aplica cambios. Si se validan los 256 casos, quedan 167 pendientes por rutas separadas.",
}])

print("[4/7] Preparando detalle de 256 casos...", flush=True)

# Detalle 218 desde hito 62: usar hoja de detalle si existe, si no repetir dictamen agregado.
try:
    detalle218 = leer(EX62, ["01_DETALLE_218", "02_DETALLE_218", "DETALLE"])
except SystemExit:
    detalle218 = pd.DataFrame([{
        "BLOQUE": "COLUMNA_19_SOLO_A",
        "CASOS": casos_218,
        "DETALLE": "Detalle no disponible en hoja esperada; usar hito 62 como evidencia agregada.",
        "FUENTE": str(EX62),
    }])

detalle218["BLOQUE_DECISION"] = "COLUMNA_19_SOLO_A"
detalle218["DECISION_SOLICITADA"] = "Validar cierre sin cambio"
detalle218["CORRECCION_REQUERIDA"] = "NO"

bloque21 = bloque21.copy()
bloque21["BLOQUE_DECISION"] = "ESTADO_ACADEMICO_SIN_REGISTROS_2025"
bloque21["DECISION_SOLICITADA"] = "Validar cierre sin cambio"
bloque21["CORRECCION_REQUERIDA"] = "NO"

bloque17 = bloque17.copy()
bloque17["BLOQUE_DECISION"] = "PERIODO_NO_1_2"
bloque17["DECISION_SOLICITADA"] = "Validar mantener 5809 sin cambio o mantener bloqueo"
bloque17["CORRECCION_REQUERIDA"] = "NO si se valida decisión funcional explícita"

# Borrador listo para envío
borrador = f"""# Solicitud de validación funcional — Avance Curricular SIES 2026, archivo 5809 columnas 16-19

Estimados/as,

Se solicita validar funcionalmente el cierre sin modificación de 256 casos observados en la revisión de columnas 16-19 del archivo 5809 Matrícula Avance Curricular 2026.

## 1. Bloque columna 19 — 218 casos

Se solicita validar mantener sin cambio 218 casos de `UNIDADES_APROBADAS` anual 2025.

Fundamento:
- El instructivo oficial indica que para las unidades aprobadas durante el último año académico 2025 no se deben incluir unidades aprobadas por validación de estudios o reconocimiento de aprendizajes previos.
- En la fuente PROMEDIOS, los estados observados son:
  - A = APROBADO
  - E = CONVALIDACION
  - I = HOMOLOGADO
  - R = REPROBADO
- El hito 62 muestra que 218/218 casos calzan contando solo A como aprobado y 0/218 calzan contando A+E+I.

Decisión solicitada:
Validar que para columna 19 anual 2025 se mantenga el criterio `solo A cuenta como aprobado`, excluyendo E/I del anual 2025.

## 2. Bloque sin registros académicos 2025 — 21 casos

Se solicita validar mantener sin cambio 21 casos con:
- 16 CURSO_1ER_SEM = NO
- 17 CURSO_2DO_SEM = NO
- 18 UNIDADES_CURSADAS = 0
- 19 UNIDADES_APROBADAS = 0

Evidencia:
- FILAS_2025_CODCLI_LISTA = 0.
- Estados académicos observados reales:
  - ELIMINADO: 20 casos.
  - ELIMINADO | VIGENTE: 1 caso.
- No se usa “inactivo” como estado académico.

Decisión solicitada:
Validar que la ausencia de registros académicos 2025 y los estados observados no contradicen mantener 0,0,0,0.

## 3. Bloque PERIODO_NO_1_2 — 17 casos

El hito 67 confirma que `PERIODO` raw no tiene regla oficial encontrada para mapear 1,2,3,4,5 a semestres.

Resultado:
- El escenario que calza con 5809 es mantener 5809 sin cambio: 17/17.
- El escenario 1=SEM1 y 2/3=SEM2 está bloqueado y no se aplica.

Decisión solicitada:
Validar una de estas opciones:
1. Mantener 5809 sin cambio para estos 17 casos.
2. Mantenerlos bloqueados hasta una definición institucional formal de PERIODO raw.

## Alcance

Esta validación aplica solo a Avance Curricular SIES 2026, archivo 5809, columnas 16-19.
No incluye columnas 20-21.
No implica generación de archivo de carga ni SIES_READY.

Saludos.
"""

print("[5/7] Escribiendo productos...", flush=True)

excel_out = SALIDA / "PAQUETE_DECISION_FUNCIONAL_16_19_5809.xlsx"
informe_out = SALIDA / "INFORME_PAQUETE_DECISION_FUNCIONAL_16_19_5809.md"
manifest_out = SALIDA / "manifest_paquete_decision_funcional_16_19_5809.json"
borrador_out = SALIDA / "BORRADOR_SOLICITUD_VALIDACION_FUNCIONAL_16_19_5809.md"
script_out = SALIDA / "h68_paquete_decision_funcional_16_19.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    matriz_decision.to_excel(writer, sheet_name="01_MATRIZ_DECISION", index=False)
    detalle218.to_excel(writer, sheet_name="02_DETALLE_218", index=False)
    bloque21.to_excel(writer, sheet_name="03_DETALLE_21", index=False)
    bloque17.to_excel(writer, sheet_name="04_DETALLE_17", index=False)
    h67_esc.to_excel(writer, sheet_name="05_ESCENARIOS_H67", index=False)
    h67_matriz.to_excel(writer, sheet_name="06_MATRIZ_PERIODO_H67", index=False)
    rutas_restantes.to_excel(writer, sheet_name="07_RUTAS_167", index=False)
    if not h58_detalle.empty:
        h58_detalle.head(5000).to_excel(writer, sheet_name="08_BASE_H58_REFERENCIA", index=False)
    pd.DataFrame([
        {"HITO": "58", "RUTA": str(H58), "EXCEL": str(EX58)},
        {"HITO": "62", "RUTA": str(H62), "EXCEL": str(EX62)},
        {"HITO": "63", "RUTA": str(H63), "EXCEL": str(EX63)},
        {"HITO": "66", "RUTA": str(H66), "EXCEL": str(EX66)},
        {"HITO": "67", "RUTA": str(H67), "EXCEL": str(EX67)},
        {"HITO": "68", "RUTA": str(SALIDA), "EXCEL": str(excel_out)},
    ]).to_excel(writer, sheet_name="09_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "fuentes_modificadas": "NO",
        "correcciones": "NO",
        "sies_ready": "NO",
        "archivo_carga": "NO",
        "recalculo_20_21": "NO",
    }]).to_excel(writer, sheet_name="10_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            length = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 12), 90)

informe_out.write_text(
f"""# Hito 68 — Paquete de decisión funcional 16-19

## Estado

- Proceso: Avance Curricular SIES 2026
- Subproyecto: archivo 5809, columnas 16-19
- Declaración de carga: NO_LISTO_PARA_CARGA
- Fuentes originales modificadas: NO
- Correcciones aplicadas: NO
- Archivo de carga generado: NO
- SIES_READY generado: NO
- 20-21 evaluado: NO

## Dictamen

Se deja preparado el paquete para validación funcional de {cerrables} casos cerrables sin cambio si se aprueban los criterios documentados.

## Bloques a validar

| Bloque | Casos | Decisión solicitada |
|---|---:|---|
| Columna 19 SOLO A | {casos_218} | Validar cierre sin cambio |
| Sin registros académicos 2025 | {casos_21} | Validar cierre sin cambio |
| PERIODO_NO_1_2 | {casos_17} | Validar mantener 5809 sin cambio o mantener bloqueo |

## Pendientes restantes si se validan los 256

| Ruta | Casos |
|---|---:|
| Mapeo institucional | 102 |
| Fuente académica complementaria | 57 |
| Revisión funcional puntual | 8 |

Total pendiente restante estimado: {pendientes_restantes}.
""",
encoding="utf-8"
)

borrador_out.write_text(borrador, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Paquete decision funcional 16-19 archivo 5809",
    "hito": 68,
    "hito58": str(H58),
    "hito62": str(H62),
    "hito63": str(H63),
    "hito66": str(H66),
    "hito67": str(H67),
    "pendientes_originales": pendientes_originales,
    "cerrables_si_se_validan": cerrables,
    "pendientes_restantes_estimados": pendientes_restantes,
    "mapeo_institucional": 102,
    "fuente_academica_complementaria": 57,
    "revision_funcional_puntual": 8,
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "recalculo_20_21": False,
    "declaracion_carga": "NO_LISTO_PARA_CARGA",
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "borrador": str(borrador_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

# copiar script real ejecutado
Path("/tmp/h68_paquete_decision_funcional_16_19.py").replace(script_out)

for archivo in [excel_out, informe_out, manifest_out, borrador_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[6/7] Verificando productos...", flush=True)

xls = pd.ExcelFile(excel_out, engine="openpyxl")
assert len(xls.sheet_names) >= 10
assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert borrador_out.exists()
assert script_out.exists()

print("[7/7] Terminado.", flush=True)

print()
print("=" * 120)
print("HITO 68 — PAQUETE DECISIÓN FUNCIONAL 16-19 GENERADO")
print("=" * 120)
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print()
print("DICTAMEN GLOBAL")
print("-" * 120)
print(dictamen.to_string(index=False))
print()
print("MATRIZ DECISIÓN")
print("-" * 120)
print(matriz_decision.to_string(index=False))
print()
print("RUTAS RESTANTES 167")
print("-" * 120)
print(rutas_restantes.to_string(index=False))
print()
print("ARCHIVOS")
print("-" * 120)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Borrador validación: {borrador_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 120)

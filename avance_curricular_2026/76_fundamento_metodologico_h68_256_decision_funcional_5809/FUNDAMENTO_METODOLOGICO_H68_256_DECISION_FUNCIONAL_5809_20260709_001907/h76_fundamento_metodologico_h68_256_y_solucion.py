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
    / "avance_curricular_2026/76_fundamento_metodologico_h68_256_decision_funcional_5809"
    / f"FUNDAMENTO_METODOLOGICO_H68_256_DECISION_FUNCIONAL_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_FUNDAMENTO_H68_256_DECISION_FUNCIONAL_5809_{timestamp}"

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
            f"Hojas: {xls.sheet_names}"
        )
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def imprimir(titulo, df, n=None):
    print()
    print("=" * 150)
    print(titulo)
    print("=" * 150)
    if df.empty:
        print("(sin datos)")
        return
    if n is None:
        print(df.to_string(index=False))
    else:
        print(df.head(n).to_string(index=False))
        if len(df) > n:
            print(f"... mostrando {n} de {len(df)} filas")

print("[1/9] Localizando fuentes metodológicas H61, H62, H63, H66, H67, H68, H73 y H75...", flush=True)

H61 = ultimo(
    RAIZ / "avance_curricular_2026/61_terminal_revision_218_convalidacion_homologacion_19_5809",
    "REVISION_218_CONVALIDACION_HOMOLOGACION_19_",
)
H62 = ultimo(
    RAIZ / "avance_curricular_2026/62_decision_funcional_candidata_columna_19_solo_a_5809",
    "DECISION_FUNCIONAL_CANDIDATA_19_SOLO_A_",
)
H63 = ultimo(
    RAIZ / "avance_curricular_2026/63_terminal_revision_38_decision_funcional_restante_5809",
    "REVISION_38_DECISION_FUNCIONAL_RESTANTE_",
)
H66 = ultimo(
    RAIZ / "avance_curricular_2026/66_correccion_dictamen_post_h64_16_19_5809",
    "CORRECCION_DICTAMEN_POST_H64_16_19_",
)
H67 = ultimo(
    RAIZ / "avance_curricular_2026/67_gobernanza_periodo_raw_5809",
    "GOBERNANZA_PERIODO_RAW_5809_",
)
H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)
H73 = ultimo(
    RAIZ / "avance_curricular_2026/73_consolidado_final_estado_16_19_5809",
    "CONSOLIDADO_FINAL_ESTADO_16_19_5809_",
)
H75 = ultimo(
    RAIZ / "avance_curricular_2026/75_auditoria_terminal_entregable_h74_16_19_5809",
    "AUDITORIA_TERMINAL_ENTREGABLE_H74_16_19_",
)

EX61 = primer_excel(H61)
EX62 = primer_excel(H62)
EX63 = primer_excel(H63)
EX66 = primer_excel(H66)
EX67 = primer_excel(H67)
EX68 = primer_excel(H68)
EX73 = primer_excel(H73)
EX75 = primer_excel(H75)

print(f"   H61: {EX61}")
print(f"   H62: {EX62}")
print(f"   H63: {EX63}")
print(f"   H66: {EX66}")
print(f"   H67: {EX67}")
print(f"   H68: {EX68}")
print(f"   H73: {EX73}")
print(f"   H75: {EX75}")

print("[2/9] Leyendo matrices clave...", flush=True)

# H61 no tiene hoja 00_DICTAMEN; su respaldo principal está en escenarios/calce/detalle.
escenarios61 = leer(EX61, ["01_ESCENARIOS", "ESCENARIOS"])
calce61 = leer(EX61, ["02_CALCE_5809", "CALCE"])
tipo_ei61 = leer(EX61, ["03_TIPO_E_I", "TIPO_E_I"])
impacto61 = leer(EX61, ["04_IMPACTO_DELTA", "IMPACTO"])
detalle218_h61 = leer(EX61, ["05_DETALLE_218", "DETALLE_218"])

dict62 = leer(EX62, ["00_DICTAMEN", "DICTAMEN"])
detalle218 = leer(EX62, ["07_DETALLE_218", "DETALLE_218"])
# H63 no tiene hoja 00_DICTAMEN; su respaldo está en números base y detalles 21/17.
numeros63 = leer(EX63, ["01_NUMEROS_BASE", "NUMEROS_BASE"])
detalle38_63 = leer(EX63, ["02_DETALLE_38", "DETALLE_38"])
detalle21 = leer(EX63, ["03_21_ESTADO_ACAD", "21_ESTADO"])
detalle17 = leer(EX63, ["04_17_PERIODO_NO_1_2", "17_PERIODO"])
evidencia_h56_63 = leer(EX63, ["05_EVIDENCIA_H56", "EVIDENCIA_H56"])
evidencia_h55_63 = leer(EX63, ["06_EVIDENCIA_H55", "EVIDENCIA_H55"])
detalle_periodo_h55_63 = leer(EX63, ["07_DETALLE_PERIODO_H55", "DETALLE_PERIODO"])
dict66 = leer(EX66, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
dict67 = leer(EX67, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz_periodo67 = leer(EX67, ["08_MATRIZ_DECISION_PERIODO", "MATRIZ_DECISION"])
dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
dict73 = leer(EX73, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
tablero73 = leer(EX73, ["01_TABLERO_FINAL", "TABLERO"])
dict75 = leer(EX75, ["00_DICTAMEN_AUDITORIA", "DICTAMEN_AUDITORIA"])
validaciones75 = leer(EX75, ["01_VALIDACIONES", "VALIDACIONES"])

print("[3/9] Validando cifras de H68...", flush=True)

d68 = dict68.iloc[0]

pendientes_originales = int(str(d68["PENDIENTES_16_19_ORIGINAL"]))
cerrables = int(str(d68["CERRABLES_SI_SE_VALIDAN"]))
restantes = int(str(d68["PENDIENTES_RESTANTES_ESTIMADOS"]))

if pendientes_originales != 423 or cerrables != 256 or restantes != 167:
    raise SystemExit(
        f"BLOQUEO: H68 no cuadra. Detectado pendientes={pendientes_originales}, cerrables={cerrables}, restantes={restantes}"
    )

# Validar matriz H68
bloques = {}
for _, r in matriz68.iterrows():
    bloques[str(r["BLOQUE"])] = int(str(r["CASOS"]))

esperado_bloques = {
    "COLUMNA_19_SOLO_A": 218,
    "ESTADO_ACADEMICO_SIN_REGISTROS_2025": 21,
    "PERIODO_NO_1_2": 17,
}

for bloque, esperado in esperado_bloques.items():
    if bloques.get(bloque) != esperado:
        raise SystemExit(f"BLOQUEO: bloque H68 {bloque} esperado {esperado}, detectado {bloques.get(bloque)}")

if sum(esperado_bloques.values()) != 256:
    raise SystemExit("BLOQUEO: suma bloques H68 no da 256.")

print("[4/9] Construyendo fundamento metodológico por bloque...", flush=True)

fundamento = pd.DataFrame([
    {
        "BLOQUE": "COLUMNA_19_SOLO_A",
        "CASOS": 218,
        "QUE_RESPALDA_H68": "H68 respalda que estos casos son cerrables sin corrección si se valida mantener el criterio observado: columna 19 anual 2025 cuenta solo A=APROBADO.",
        "POR_QUE_ES_METODOLOGICAMENTE_VALIDO": "H61 demostró que 218/218 calzan con escenario SOLO_A y 0/218 con A_E_I. H66 corrigió el dictamen y vinculó el criterio con el instructivo oficial: unidades aprobadas anuales excluyen validación/reconocimiento; E=CONVALIDACION e I=HOMOLOGADO son datos observados de PROMEDIOS, no regla oficial.",
        "POR_QUE_SIGUE_PENDIENTE": "Porque H68 no es una decisión aprobada; es un paquete de validación. La evidencia respalda mantener sin cambio, pero requiere acto/registro de decisión funcional para cerrar el bloque.",
        "RIESGO_SI_SE_CIERRA_SIN_DECISION": "Convertir una conclusión técnica/observada en decisión funcional sin autorización.",
        "SOLUCION_PROPUESTA": "Registrar decisión funcional: mantener columna 19 anual 2025 contando solo A=APROBADO y excluir E/I para este bloque; no aplicar corrección.",
        "TIPO_SOLUCION": "CIERRE_SIN_CAMBIO_CON_ACTA_FUNCIONAL",
        "CORRECCION_DATOS": "NO",
        "ESTADO_PROPUESTO": "CERRABLE_SI_SE_REGISTRA_DECISION_FUNCIONAL",
    },
    {
        "BLOQUE": "ESTADO_ACADEMICO_SIN_REGISTROS_2025",
        "CASOS": 21,
        "QUE_RESPALDA_H68": "H68 respalda que estos casos son cerrables sin cambio si se valida mantener 16=NO, 17=NO, 18=0, 19=0 por ausencia de registros académicos 2025 para CODCLI_LISTA.",
        "POR_QUE_ES_METODOLOGICAMENTE_VALIDO": "H63 mostró que los 21 casos no tienen registros 2025 para CODCLI_LISTA y que 5809 coincide con recálculo 0/NO. H66 corrigió la lectura: no se debe llamarlos inactivos; los estados observados reales son ELIMINADO 20 y ELIMINADO | VIGENTE 1.",
        "POR_QUE_SIGUE_PENDIENTE": "Porque la ausencia de registros es dato observado, no regla oficial automática de cierre. Requiere decisión funcional para aceptar mantener sin cambio.",
        "RIESGO_SI_SE_CIERRA_SIN_DECISION": "Usar estado académico observado como regla normativa automática.",
        "SOLUCION_PROPUESTA": "Registrar decisión funcional: para estos 21 casos, mantener 16=NO, 17=NO, 18=0, 19=0 por ausencia documentada de registros académicos 2025 para CODCLI_LISTA; no aplicar corrección.",
        "TIPO_SOLUCION": "CIERRE_SIN_CAMBIO_CON_ACTA_FUNCIONAL",
        "CORRECCION_DATOS": "NO",
        "ESTADO_PROPUESTO": "CERRABLE_SI_SE_REGISTRA_DECISION_FUNCIONAL",
    },
    {
        "BLOQUE": "PERIODO_NO_1_2",
        "CASOS": 17,
        "QUE_RESPALDA_H68": "H68 respalda que los 17 pueden cerrarse solo si existe decisión funcional explícita de mantener 5809 sin cambio; no respalda aplicar mapeo PERIODO raw.",
        "POR_QUE_ES_METODOLOGICAMENTE_VALIDO": "H67 verificó que PERIODO raw 1-5 no tiene regla oficial encontrada; el escenario que calza con 5809 es mantener sin cambio 17/17, pero solo como decisión funcional, no como regla técnica automática.",
        "POR_QUE_SIGUE_PENDIENTE": "Porque no existe regla oficial para traducir PERIODO raw 3/4/5 a semestre; cerrar requiere decidir mantener 5809 sin cambio o dejar bloqueo.",
        "RIESGO_SI_SE_CIERRA_SIN_DECISION": "Inventar una regla de período o aplicar una equivalencia no oficial.",
        "SOLUCION_PROPUESTA": "Registrar decisión funcional explícita: mantener valores 5809 sin cambio para los 17 casos PERIODO_NO_1_2, dejando documentado que no se aplica mapeo PERIODO raw.",
        "TIPO_SOLUCION": "CIERRE_SIN_CAMBIO_SOLO_CON_DECISION_EXPLICITA",
        "CORRECCION_DATOS": "NO",
        "ESTADO_PROPUESTO": "CERRABLE_SOLO_CON_DECISION_FUNCIONAL_EXPLICITA",
    },
])

print("[5/9] Construyendo propuesta de solución gobernada...", flush=True)

solucion = pd.DataFrame([
    {
        "PASO": 1,
        "ACCION": "Emitir acta de decisión funcional interna para H68.",
        "DETALLE": "El acta debe declarar explícitamente que los 256 casos se cierran sin cambio, separados en 218/21/17.",
        "RESULTADO_ESPERADO": "Acta firmada/validada o decisión registrada.",
        "APLICA_CORRECCION": "NO",
        "GENERA_CARGA": "NO",
    },
    {
        "PASO": 2,
        "ACCION": "Registrar H77 como cierre funcional de 256.",
        "DETALLE": "Crear matriz que marque 256 como cerrados por decisión funcional, sin tocar fuente 5809.",
        "RESULTADO_ESPERADO": "H77_CIERRE_FUNCIONAL_256.",
        "APLICA_CORRECCION": "NO",
        "GENERA_CARGA": "NO",
    },
    {
        "PASO": 3,
        "ACCION": "Mantener 167 de H72 bloqueados.",
        "DETALLE": "No mezclar con 256. Los 167 siguen requiriendo mapeo/fuente/revisión.",
        "RESULTADO_ESPERADO": "Pendientes restantes formales: 167.",
        "APLICA_CORRECCION": "NO",
        "GENERA_CARGA": "NO",
    },
    {
        "PASO": 4,
        "ACCION": "Actualizar tablero 16-19 post decisión.",
        "DETALLE": "Cambiar 256 desde PENDIENTE_VALIDACION_FUNCIONAL a CERRADO_SIN_CAMBIO_POR_DECISION_FUNCIONAL.",
        "RESULTADO_ESPERADO": "Nuevo tablero: 256 cerrados, 167 bloqueados.",
        "APLICA_CORRECCION": "NO",
        "GENERA_CARGA": "NO",
    },
    {
        "PASO": 5,
        "ACCION": "No generar SIES_READY.",
        "DETALLE": "Aunque se cierren los 256, quedan 167 bloqueados y 20-21 está fuera de alcance.",
        "RESULTADO_ESPERADO": "NO_LISTO_PARA_CARGA se mantiene.",
        "APLICA_CORRECCION": "NO",
        "GENERA_CARGA": "NO",
    },
])

acta_propuesta = f"""# Propuesta de decisión funcional — Cierre H68 256 casos 16-19

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Año referencia datos

2025.

## Antecedente

H68 consolidó 256 casos cerrables solo con decisión funcional:

- 218 casos COLUMNA_19_SOLO_A.
- 21 casos ESTADO_ACADEMICO_SIN_REGISTROS_2025.
- 17 casos PERIODO_NO_1_2.

## Fundamento metodológico

### 218 COLUMNA_19_SOLO_A

Se propone validar el cierre sin cambio porque H61 mostró que los 218 casos calzan con el escenario SOLO_A, y H66 vinculó ese tratamiento con el instructivo oficial de Avance: las unidades aprobadas anuales excluyen validación/reconocimiento. E/I son datos observados en PROMEDIOS, no regla oficial.

### 21 SIN REGISTROS 2025

Se propone validar el cierre sin cambio porque H63 mostró ausencia de registros académicos 2025 para CODCLI_LISTA y H66 corrigió la interpretación de estados observados: ELIMINADO 20 y ELIMINADO | VIGENTE 1. No se usa “inactivo” como estado.

### 17 PERIODO_NO_1_2

Se propone validar el cierre sin cambio solo con decisión explícita porque H67 no encontró regla oficial para PERIODO raw 1-5. El escenario que calza con 5809 es mantener sin cambio 17/17, pero no aplicar mapeo automático de período.

## Decisión propuesta

Registrar como decisión funcional:

1. Cerrar los 256 casos H68 sin corrección de datos.
2. Mantener los valores originales del archivo 5809 para esos 256 casos.
3. No aplicar mapeos no oficiales.
4. No modificar fuentes originales.
5. No generar archivo de carga.
6. No generar SIES_READY.
7. Mantener 167 casos H72 bloqueados por evidencia faltante.
8. Mantener 20-21 como frente separado.

## Dictamen post decisión propuesta

Si esta decisión se registra, el estado quedaría:

- 256 cerrados sin cambio por decisión funcional.
- 167 bloqueados por evidencia faltante.
- 0 corregibles por terminal.
- NO_LISTO_PARA_CARGA.
- NO_APTO_PARA_CARGA.
"""

print("[6/9] Construyendo controles de metodología...", flush=True)

controles = pd.DataFrame([
    {
        "CONTROL": "H68 suma 256",
        "RESULTADO": "OK",
        "EVIDENCIA": "218 + 21 + 17 = 256.",
        "INTERPRETACION": "H68 respalda universo cerrable solo si existe decisión funcional.",
    },
    {
        "CONTROL": "218 no requieren corrección",
        "RESULTADO": "OK",
        "EVIDENCIA": "H61/H62/H66: 218/218 calzan con SOLO_A.",
        "INTERPRETACION": "La solución es cierre sin cambio, no recálculo ni carga.",
    },
    {
        "CONTROL": "21 no requieren corrección",
        "RESULTADO": "OK",
        "EVIDENCIA": "H63/H66: sin registros 2025 para CODCLI_LISTA; 5809 coincide con 0/NO.",
        "INTERPRETACION": "La solución es cierre sin cambio con decisión funcional.",
    },
    {
        "CONTROL": "17 no tienen regla oficial de período",
        "RESULTADO": "OK",
        "EVIDENCIA": "H67: PERIODO raw 1-5 sin regla oficial encontrada.",
        "INTERPRETACION": "No se aplica mapeo automático; solo puede cerrarse por decisión explícita de mantener 5809.",
    },
    {
        "CONTROL": "No modificar fuente original",
        "RESULTADO": "OK",
        "EVIDENCIA": "Todos los bloques proponen cierre sin cambio.",
        "INTERPRETACION": "No hay corrección técnica que aplicar.",
    },
    {
        "CONTROL": "No generar carga",
        "RESULTADO": "OK",
        "EVIDENCIA": "H73/H75: aún quedan 167 bloqueados y 20-21 fuera de alcance.",
        "INTERPRETACION": "La decisión de 256 no habilita SIES_READY.",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Fundamento metodológico H68 256 decisión funcional archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "FUNDAMENTO_Y_PROPUESTA_SOLUCION",
    "H68_RESPALDA_256": "SI",
    "POR_QUE_RESPALDA": "Porque H68 consolida tres bloques con evidencia suficiente para cierre sin cambio si se registra decisión funcional: 218 SOLO_A, 21 sin registros 2025 y 17 PERIODO_NO_1_2.",
    "POR_QUE_SIGUE_PENDIENTE": "Porque la evidencia técnica no equivale a decisión funcional aprobada. Sin acta/registro, no corresponde cerrar ni modificar el estado.",
    "SOLUCION_PROPUESTA": "Emitir y registrar decisión funcional de cierre sin cambio para los 256 casos; luego crear H77 como cierre funcional documentado. No corregir datos, no generar carga, no SIES_READY.",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
}])

print("[7/9] Escribiendo productos H76...", flush=True)

excel_out = SALIDA / "FUNDAMENTO_METODOLOGICO_H68_256_DECISION_FUNCIONAL_5809.xlsx"
informe_out = SALIDA / "INFORME_FUNDAMENTO_METODOLOGICO_H68_256_DECISION_FUNCIONAL_5809.md"
acta_out = SALIDA / "PROPUESTA_ACTA_DECISION_FUNCIONAL_H68_256_5809.md"
manifest_out = SALIDA / "manifest_fundamento_metodologico_h68_256_decision_funcional_5809.json"
script_out = SALIDA / "h76_fundamento_metodologico_h68_256_y_solucion.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    fundamento.to_excel(writer, sheet_name="01_FUNDAMENTO_256", index=False)
    matriz68.to_excel(writer, sheet_name="02_MATRIZ_H68", index=False)
    solucion.to_excel(writer, sheet_name="03_SOLUCION_PROPUESTA", index=False)
    controles.to_excel(writer, sheet_name="04_CONTROLES_METODOLOGIA", index=False)
    escenarios61.to_excel(writer, sheet_name="05_H61_ESCENARIOS", index=False)
    calce61.to_excel(writer, sheet_name="06_H61_CALCE_5809", index=False)
    tipo_ei61.to_excel(writer, sheet_name="07_H61_TIPO_E_I", index=False)
    impacto61.to_excel(writer, sheet_name="08_H61_IMPACTO_DELTA", index=False)
    detalle218_h61.to_excel(writer, sheet_name="09_H61_DETALLE_218", index=False)
    detalle218.to_excel(writer, sheet_name="10_H62_DETALLE_218", index=False)
    numeros63.to_excel(writer, sheet_name="11_H63_NUMEROS_BASE", index=False)
    detalle38_63.to_excel(writer, sheet_name="12_H63_DETALLE_38", index=False)
    detalle21.to_excel(writer, sheet_name="13_H63_DETALLE_21", index=False)
    detalle17.to_excel(writer, sheet_name="14_H63_DETALLE_17", index=False)
    evidencia_h56_63.to_excel(writer, sheet_name="15_H63_EVIDENCIA_H56", index=False)
    evidencia_h55_63.to_excel(writer, sheet_name="16_H63_EVIDENCIA_H55", index=False)
    detalle_periodo_h55_63.to_excel(writer, sheet_name="17_H63_DETALLE_PERIODO", index=False)
    matriz_periodo67.to_excel(writer, sheet_name="18_H67_PERIODO_RAW", index=False)
    tablero73.to_excel(writer, sheet_name="19_H73_TABLERO", index=False)
    validaciones75.to_excel(writer, sheet_name="20_H75_VALIDACIONES", index=False)
    pd.DataFrame([
        {"HITO": "61", "RUTA": str(H61), "EXCEL": str(EX61), "SHA256": sha256(EX61), "HOJAS_USADAS": "01_ESCENARIOS;02_CALCE_5809;03_TIPO_E_I;04_IMPACTO_DELTA;05_DETALLE_218"},
        {"HITO": "62", "RUTA": str(H62), "EXCEL": str(EX62), "SHA256": sha256(EX62)},
        {"HITO": "63", "RUTA": str(H63), "EXCEL": str(EX63), "SHA256": sha256(EX63), "HOJAS_USADAS": "01_NUMEROS_BASE;02_DETALLE_38;03_21_ESTADO_ACAD;04_17_PERIODO_NO_1_2;05_EVIDENCIA_H56;06_EVIDENCIA_H55;07_DETALLE_PERIODO_H55"},
        {"HITO": "66", "RUTA": str(H66), "EXCEL": str(EX66), "SHA256": sha256(EX66)},
        {"HITO": "67", "RUTA": str(H67), "EXCEL": str(EX67), "SHA256": sha256(EX67)},
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "73", "RUTA": str(H73), "EXCEL": str(EX73), "SHA256": sha256(EX73)},
        {"HITO": "75", "RUTA": str(H75), "EXCEL": str(EX75), "SHA256": sha256(EX75)},
    ]).to_excel(writer, sheet_name="21_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 76,
        "h68_respalda_256": "SI",
        "pendiente_por": "FALTA_DECISION_FUNCIONAL_REGISTRADA",
        "solucion": "ACTA_DECISION_FUNCIONAL_CIERRE_SIN_CAMBIO_256",
        "correcciones": "NO",
        "archivo_carga": "NO",
        "sies_ready": "NO",
        "subida_sies": "NO",
    }]).to_excel(writer, sheet_name="22_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe = f"""# Hito 76 — Fundamento metodológico H68 256 y solución propuesta

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Pregunta

Por qué metodológicamente H68 respalda los 256 casos cerrables solo con decisión funcional, por qué siguen pendientes y cuál es la solución propuesta.

## Respuesta

H68 respalda los 256 casos porque consolida tres bloques con evidencia suficiente para cierre sin cambio, pero no para cierre automático:

| Bloque | Casos | Fundamento | Pendiente |
|---|---:|---|---|
| COLUMNA_19_SOLO_A | 218 | H61/H62/H66: calzan con SOLO_A y el instructivo respalda excluir validación/reconocimiento en aprobadas anuales. | Falta decisión funcional de cierre sin cambio. |
| ESTADO_ACADEMICO_SIN_REGISTROS_2025 | 21 | H63/H66: no hay registros 2025 para CODCLI_LISTA y 5809 ya refleja NO/0. | Falta decisión funcional de aceptar mantener sin cambio. |
| PERIODO_NO_1_2 | 17 | H67: no hay regla oficial para PERIODO raw; mantener 5809 calza, pero solo como decisión explícita. | Falta decisión funcional explícita. |

## Por qué sigue pendiente

Porque una evidencia técnica o dato observado no equivale a una regla oficial ni a una decisión funcional aprobada.

## Solución propuesta

Emitir y registrar una decisión funcional que cierre los 256 casos sin cambio:

1. Mantener valores 5809.
2. No aplicar corrección de datos.
3. No modificar fuentes originales.
4. No generar archivo de carga.
5. No generar SIES_READY.
6. Mantener 167 pendientes H72 bloqueados.
7. Mantener 20-21 como frente separado.

## Dictamen

H68 respalda metodológicamente el cierre de los 256 solo si se registra una decisión funcional explícita.
Sin esa decisión, el estado correcto sigue siendo PENDIENTE.
"""

informe_out.write_text(informe, encoding="utf-8")
acta_out.write_text(acta_propuesta, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Fundamento metodologico H68 256 decision funcional archivo 5809",
    "hito": 76,
    "h68_respalda_256": True,
    "motivo_respaldo": "Tres bloques con evidencia suficiente para cierre sin cambio si existe decision funcional: 218 SOLO_A, 21 sin registros 2025, 17 PERIODO_NO_1_2.",
    "motivo_pendiente": "Falta decision funcional registrada; evidencia tecnica no equivale a aprobacion funcional.",
    "solucion_propuesta": "Acta de decision funcional y H77 de cierre sin cambio de 256.",
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "dictamen_carga": "NO_APTO_PARA_CARGA",
    "declaracion_carga": "NO_LISTO_PARA_CARGA",
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "acta_propuesta": str(acta_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h76_fundamento_metodologico_h68_256_y_solucion.py"), script_out)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/9] Verificando productos...", flush=True)

assert excel_out.exists()
assert informe_out.exists()
assert acta_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert len(fundamento) == 3
assert fundamento["CASOS"].sum() == 256
assert len(solucion) == 5

print("[9/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 150)
print("HITO 76 — FUNDAMENTO METODOLÓGICO H68 256 Y SOLUCIÓN PROPUESTA GENERADO")
print("=" * 150)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("H68 respalda metodológicamente los 256: SI")
print("Estado actual: PENDIENTE POR FALTA DE DECISIÓN FUNCIONAL REGISTRADA")
print("Solución propuesta: ACTA_DECISION_FUNCIONAL + H77_CIERRE_SIN_CAMBIO_256")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Dictamen carga: NO_APTO_PARA_CARGA")
print("Declaración carga: NO_LISTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("FUNDAMENTO METODOLOGICO POR BLOQUE", fundamento)
imprimir("SOLUCION PROPUESTA", solucion)
imprimir("CONTROLES METODOLOGICOS", controles)
imprimir("MATRIZ H68", matriz68)

print()
print("=" * 150)
print("ARCHIVOS H76")
print("=" * 150)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Acta propuesta: {acta_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 150)

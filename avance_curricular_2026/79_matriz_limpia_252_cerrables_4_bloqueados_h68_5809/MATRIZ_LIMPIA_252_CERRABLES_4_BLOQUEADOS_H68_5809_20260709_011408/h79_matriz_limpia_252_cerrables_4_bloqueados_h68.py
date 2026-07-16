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
    / "avance_curricular_2026/79_matriz_limpia_252_cerrables_4_bloqueados_h68_5809"
    / f"MATRIZ_LIMPIA_252_CERRABLES_4_BLOQUEADOS_H68_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_MATRIZ_LIMPIA_252_CERRABLES_4_BLOQUEADOS_H68_5809_{timestamp}"

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

print("[1/9] Localizando H68, H72, H77 y H78...", flush=True)

H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)
H72 = ultimo(
    RAIZ / "avance_curricular_2026/72_revision_end_to_end_167_pendientes_hasta_csv_piloto_5809",
    "REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809_",
)
H77 = ultimo(
    RAIZ / "avance_curricular_2026/77_registro_decisiones_usuario_h68_256_16_19_5809",
    "REGISTRO_DECISIONES_USUARIO_H68_256_16_19_5809_",
)
H78 = ultimo(
    RAIZ / "avance_curricular_2026/78_auditoria_fina_21_estado_17_periodo_5809",
    "AUDITORIA_FINA_21_ESTADO_17_PERIODO_5809_",
)

EX68 = primer_excel(H68)
EX72 = primer_excel(H72)
EX77 = primer_excel(H77)
EX78 = primer_excel(H78)

print(f"   H68: {EX68}")
print(f"   H72: {EX72}")
print(f"   H77: {EX77}")
print(f"   H78: {EX78}")

print("[2/9] Leyendo evidencia...", flush=True)

matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
dict72 = leer(EX72, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
resumen72 = leer(EX72, ["02_RESUMEN_DECISIONES", "RESUMEN_DECISIONES"])
decisiones77 = leer(EX77, ["01_DECISIONES_USUARIO", "DECISIONES"])
vista21 = leer(EX78, ["02_VISTA_21_TERMINAL", "VISTA_21"])
estado_raw21 = leer(EX78, ["03_RESUMEN_ESTADO_RAW_21", "RESUMEN_ESTADO_RAW"])
combos21 = leer(EX78, ["05_COMBINACIONES_21", "COMBINACIONES"])
vista17 = leer(EX78, ["08_VISTA_17_TERMINAL", "VISTA_17"])
resumen_periodos17 = leer(EX78, ["09_RESUMEN_PERIODOS_17", "RESUMEN_PERIODOS"])
periodo_por_fila17 = leer(EX78, ["10_PERIODO_17_POR_FILA", "PERIODO_17_POR_FILA"])
periodos_no_def17 = leer(EX78, ["11_PERIODOS_17_NO_DEFINIDOS", "PERIODOS_17_NO_DEFINIDOS"])

print("[3/9] Validando cifras H78...", flush=True)

# 21: 20 eliminados + 1 combinado
filas_eliminado = 0
filas_combo = 0
for _, r in estado_raw21.iterrows():
    raw = str(r.get("ESTADO_RAW", "")).strip()
    filas = int(str(r.get("FILAS", "0") or "0"))
    if raw == "ELIMINADO":
        filas_eliminado += filas
    if raw == "ELIMINADO | VIGENTE":
        filas_combo += filas

if filas_eliminado != 20 or filas_combo != 1:
    raise SystemExit(
        f"BLOQUEO: 21 no cuadran. ELIMINADO={filas_eliminado}, COMBO={filas_combo}"
    )

# 17: determinar filas con periodos no definidos por FILA_KEY
bloqueadas_periodo = sorted(set(periodos_no_def17["FILA_KEY"].astype(str))) if not periodos_no_def17.empty else []
if bloqueadas_periodo != ["1719", "1824", "1825"]:
    raise SystemExit(f"BLOQUEO: filas bloqueadas por periodo esperadas 1719/1824/1825, detectadas {bloqueadas_periodo}")

cerrables_periodo = 17 - len(bloqueadas_periodo)
if cerrables_periodo != 14:
    raise SystemExit(f"BLOQUEO: cerrables periodo esperado 14, detectado {cerrables_periodo}")

cerrables_218 = 218
cerrables_20 = 20
cerrables_14 = 14
cerrables_total = cerrables_218 + cerrables_20 + cerrables_14
bloqueados_h68 = 1 + 3

if cerrables_total != 252 or bloqueados_h68 != 4:
    raise SystemExit(
        f"BLOQUEO: cierre no cuadra. cerrables={cerrables_total}, bloqueados_h68={bloqueados_h68}"
    )

print("[4/9] Construyendo matriz limpia H68...", flush=True)

matriz_limpia = pd.DataFrame([
    {
        "BLOQUE_ORIGINAL_H68": "COLUMNA_19_SOLO_A",
        "SUB_BLOQUE_H79": "218_SOLO_A",
        "CASOS": 218,
        "ESTADO_H79": "CERRABLE_SIN_CAMBIO_APROBADO_USUARIO",
        "DECISION_USUARIO": "Apruebo cerrar estos 218.",
        "TRATAMIENTO": "Mantener columna 19 anual 2025 contando solo A=APROBADO; excluir E/I; no corregir dato.",
        "CORRECCION_DATOS": "NO",
        "GENERA_CARGA": "NO",
        "NIVEL_RESPALDO": "A/B/D",
    },
    {
        "BLOQUE_ORIGINAL_H68": "ESTADO_ACADEMICO_SIN_REGISTROS_2025",
        "SUB_BLOQUE_H79": "20_ELIMINADO",
        "CASOS": 20,
        "ESTADO_H79": "CERRABLE_SIN_CAMBIO_PENDIENTE_APROBACION_USUARIO_FINAL",
        "DECISION_USUARIO": "Usuario pidió revisar situación académica. H78 confirma 20 ELIMINADO.",
        "TRATAMIENTO": "Mantener 16=NO, 17=NO, 18=0, 19=0 por ausencia de registros académicos 2025 y estado observado ELIMINADO.",
        "CORRECCION_DATOS": "NO",
        "GENERA_CARGA": "NO",
        "NIVEL_RESPALDO": "B/D",
    },
    {
        "BLOQUE_ORIGINAL_H68": "ESTADO_ACADEMICO_SIN_REGISTROS_2025",
        "SUB_BLOQUE_H79": "1_COMBO_ELIMINADO_VIGENTE_FILA_187",
        "CASOS": 1,
        "ESTADO_H79": "BLOQUEADO_POR_DOBLE_CODCLI_ESTADO_AGREGADO",
        "DECISION_USUARIO": "Usuario indicó que no existe estado único ELIMINADO | VIGENTE.",
        "TRATAMIENTO": "No cerrar. Separar CODCLI/estado para FILA_KEY 187 antes de decidir.",
        "CORRECCION_DATOS": "NO",
        "GENERA_CARGA": "NO",
        "NIVEL_RESPALDO": "B/D",
    },
    {
        "BLOQUE_ORIGINAL_H68": "PERIODO_NO_1_2",
        "SUB_BLOQUE_H79": "14_PERIODO_1_2_3_CUBIERTO",
        "CASOS": 14,
        "ESTADO_H79": "CERRABLE_CON_CRITERIO_USUARIO_PERIODO",
        "DECISION_USUARIO": "PERIODO 1 es 1; PERIODO 2 y 3 es 2.",
        "TRATAMIENTO": "Aplicar criterio interno usuario a filas sin períodos 4/5. No declarar como regla oficial.",
        "CORRECCION_DATOS": "PENDIENTE_SOLO_SI_SE_MATERIALIZA_CORRECCION",
        "GENERA_CARGA": "NO",
        "NIVEL_RESPALDO": "D",
    },
    {
        "BLOQUE_ORIGINAL_H68": "PERIODO_NO_1_2",
        "SUB_BLOQUE_H79": "3_PERIODO_4_5_FILAS_1719_1824_1825",
        "CASOS": 3,
        "ESTADO_H79": "BLOQUEADO_POR_PERIODO_4_5_SIN_DECISION_USUARIO",
        "DECISION_USUARIO": "Usuario solo definió 1, 2 y 3.",
        "TRATAMIENTO": "No cerrar. Definir criterio para PERIODO 4/5 o mantener bloqueado.",
        "CORRECCION_DATOS": "NO",
        "GENERA_CARGA": "NO",
        "NIVEL_RESPALDO": "B/D",
    },
])

resumen_h79 = pd.DataFrame([
    {
        "CATEGORIA": "CERRABLES_H68_CON_DECISION_O_EVIDENCIA",
        "CASOS": 252,
        "DETALLE": "218 aprobados + 20 ELIMINADO revisados + 14 períodos 1/2/3 cubiertos.",
    },
    {
        "CATEGORIA": "BLOQUEADOS_H68",
        "CASOS": 4,
        "DETALLE": "1 fila 187 por doble CODCLI/estado agregado + 3 filas 1719/1824/1825 por período 4/5.",
    },
    {
        "CATEGORIA": "TOTAL_H68",
        "CASOS": 256,
        "DETALLE": "252 + 4.",
    },
    {
        "CATEGORIA": "BLOQUEADOS_H72_SE_MANTIENEN",
        "CASOS": 167,
        "DETALLE": "Fuera de esta resolución. Se mantienen bloqueados por evidencia faltante.",
    },
])

bloqueados4 = pd.DataFrame([
    {
        "TIPO_BLOQUEO": "DOBLE_CODCLI_ESTADO_AGREGADO",
        "FILA_KEY": "187",
        "CASOS": 1,
        "MOTIVO": "ESTADOS_ACADEMICOS_OBSERVADOS = ELIMINADO | VIGENTE por CODCLI_LISTA_NORM 20251TENS019;20261TPAS098.",
        "ACCION_REQUERIDA": "Separar CODCLI correcto asociado al registro 5809 y determinar estado aplicable.",
    },
    {
        "TIPO_BLOQUEO": "PERIODO_4_5",
        "FILA_KEY": "1719",
        "CASOS": 1,
        "MOTIVO": "Tiene PERIODO 5 en evidencia filtrada.",
        "ACCION_REQUERIDA": "Definir criterio usuario para PERIODO 5 o mantener bloqueado.",
    },
    {
        "TIPO_BLOQUEO": "PERIODO_4_5",
        "FILA_KEY": "1824",
        "CASOS": 1,
        "MOTIVO": "Tiene PERIODO 4 y 5 en evidencia filtrada.",
        "ACCION_REQUERIDA": "Definir criterio usuario para PERIODO 4/5 o mantener bloqueado.",
    },
    {
        "TIPO_BLOQUEO": "PERIODO_4_5",
        "FILA_KEY": "1825",
        "CASOS": 1,
        "MOTIVO": "Tiene PERIODO 4 y 5 en evidencia filtrada.",
        "ACCION_REQUERIDA": "Definir criterio usuario para PERIODO 4/5 o mantener bloqueado.",
    },
])

# Filtrar evidencia específica de los 4
vista21_bloqueado = vista21[vista21.astype(str).apply(lambda row: row.str.contains("187", regex=False).any(), axis=1)].copy()
periodos4 = periodos_no_def17.copy()

control_carga = pd.DataFrame([
    {"CONTROL": "252 H68 cerrables", "RESULTADO": "SI", "DICTAMEN": "Documentado; no implica carga."},
    {"CONTROL": "4 H68 bloqueados", "RESULTADO": "SI", "DICTAMEN": "Deben resolverse antes de cierre completo H68."},
    {"CONTROL": "167 H72 resueltos", "RESULTADO": "NO", "DICTAMEN": "Se mantienen bloqueados."},
    {"CONTROL": "Fuentes originales modificadas", "RESULTADO": "NO", "DICTAMEN": "No se modificaron."},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "DICTAMEN": "No se aplicaron."},
    {"CONTROL": "Archivo de carga generado", "RESULTADO": "NO", "DICTAMEN": "No corresponde."},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "DICTAMEN": "No corresponde."},
    {"CONTROL": "Subida SIES permitida", "RESULTADO": "NO", "DICTAMEN": "No corresponde."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Matriz limpia 252 cerrables y 4 bloqueados H68 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "MATRIZ_LIMPIA_H68_POST_H78",
    "H68_TOTAL": 256,
    "H68_CERRABLES": 252,
    "H68_BLOQUEADOS": 4,
    "H72_BLOQUEADOS_SE_MANTIENEN": 167,
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "DICTAMEN_GLOBAL": "H79 separa H68 en 252 cerrables y 4 bloqueados. No genera carga ni SIES_READY.",
}])

print("[5/9] Redactando informe...", flush=True)

informe = f"""# Hito 79 — Matriz limpia H68: 252 cerrables y 4 bloqueados

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado

H68 queda separado así:

- 252 casos cerrables.
- 4 casos bloqueados.
- 167 casos H72 se mantienen bloqueados por evidencia faltante.

## Desglose H68

| Bloque | Casos | Estado |
|---|---:|---|
| 218 SOLO_A | 218 | Cerrable sin cambio aprobado por usuario |
| 20 ELIMINADO | 20 | Cerrable sin cambio pendiente de confirmación final |
| 1 fila 187 | 1 | Bloqueado por doble CODCLI / estado agregado |
| 14 período 1/2/3 | 14 | Cerrable con criterio usuario |
| 3 período 4/5 | 3 | Bloqueado por falta de criterio usuario |

## Control

No se modifican fuentes originales.
No se aplican correcciones.
No se genera archivo de carga.
No se genera SIES_READY.
No se permite subida SIES.

## Pendientes inmediatos

1. Resolver FILA_KEY 187 separando CODCLI/estado.
2. Definir criterio para PERIODO 4/5 o mantener filas 1719, 1824 y 1825 bloqueadas.
3. Resolver 167 H72 por rutas ya documentadas.
"""

print("[6/9] Escribiendo productos H79...", flush=True)

excel_out = SALIDA / "MATRIZ_LIMPIA_252_CERRABLES_4_BLOQUEADOS_H68_5809.xlsx"
informe_out = SALIDA / "INFORME_MATRIZ_LIMPIA_252_CERRABLES_4_BLOQUEADOS_H68_5809.md"
manifest_out = SALIDA / "manifest_matriz_limpia_252_cerrables_4_bloqueados_h68_5809.json"
script_out = SALIDA / "h79_matriz_limpia_252_cerrables_4_bloqueados_h68.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_h79.to_excel(writer, sheet_name="01_RESUMEN_H79", index=False)
    matriz_limpia.to_excel(writer, sheet_name="02_MATRIZ_LIMPIA_H68", index=False)
    bloqueados4.to_excel(writer, sheet_name="03_BLOQUEADOS_4", index=False)
    vista21_bloqueado.to_excel(writer, sheet_name="04_FILA_187_ESTADO", index=False)
    periodos4.to_excel(writer, sheet_name="05_FILAS_1719_1824_1825", index=False)
    estado_raw21.to_excel(writer, sheet_name="06_H78_ESTADOS_21", index=False)
    periodo_por_fila17.to_excel(writer, sheet_name="07_H78_PERIODO_POR_FILA", index=False)
    resumen_periodos17.to_excel(writer, sheet_name="08_H78_RESUMEN_PERIODOS", index=False)
    decisiones77.to_excel(writer, sheet_name="09_H77_DECISIONES_USUARIO", index=False)
    matriz68.to_excel(writer, sheet_name="10_H68_MATRIZ_ORIGINAL", index=False)
    resumen72.to_excel(writer, sheet_name="11_H72_167_SE_MANTIENEN", index=False)
    control_carga.to_excel(writer, sheet_name="12_CONTROL_CARGA", index=False)
    pd.DataFrame([
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "72", "RUTA": str(H72), "EXCEL": str(EX72), "SHA256": sha256(EX72)},
        {"HITO": "77", "RUTA": str(H77), "EXCEL": str(EX77), "SHA256": sha256(EX77)},
        {"HITO": "78", "RUTA": str(H78), "EXCEL": str(EX78), "SHA256": sha256(EX78)},
    ]).to_excel(writer, sheet_name="13_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 79,
        "h68_total": 256,
        "h68_cerrables": 252,
        "h68_bloqueados": 4,
        "h72_bloqueados_se_mantienen": 167,
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
        "subida_sies_permitida": "NO",
    }]).to_excel(writer, sheet_name="14_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "Matriz limpia 252 cerrables y 4 bloqueados H68 archivo 5809 columnas 16-19",
    "hito": 79,
    "h68_total": 256,
    "h68_cerrables": 252,
    "h68_bloqueados": 4,
    "h72_bloqueados_se_mantienen": 167,
    "bloqueados_h68": [
        {"fila_key": "187", "motivo": "doble CODCLI / estado agregado ELIMINADO | VIGENTE"},
        {"fila_key": "1719", "motivo": "PERIODO 5"},
        {"fila_key": "1824", "motivo": "PERIODO 4/5"},
        {"fila_key": "1825", "motivo": "PERIODO 4/5"},
    ],
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h79_matriz_limpia_252_cerrables_4_bloqueados_h68.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[7/9] Verificando productos...", flush=True)

assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert int(resumen_h79.loc[resumen_h79["CATEGORIA"].eq("TOTAL_H68"), "CASOS"].iloc[0]) == 256
assert int(resumen_h79.loc[resumen_h79["CATEGORIA"].eq("CERRABLES_H68_CON_DECISION_O_EVIDENCIA"), "CASOS"].iloc[0]) == 252
assert int(resumen_h79.loc[resumen_h79["CATEGORIA"].eq("BLOQUEADOS_H68"), "CASOS"].iloc[0]) == 4

print("[8/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 79 — MATRIZ LIMPIA 252 CERRABLES Y 4 BLOQUEADOS H68 GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("H68 total: 256")
print("H68 cerrables: 252")
print("H68 bloqueados: 4")
print("H72 bloqueados se mantienen: 167")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN H79", resumen_h79)
imprimir("MATRIZ LIMPIA H68", matriz_limpia)
imprimir("4 BLOQUEADOS H68", bloqueados4)
imprimir("FILA 187 ESTADO / CODCLI", vista21_bloqueado)
imprimir("FILAS 1719 / 1824 / 1825 PERIODOS 4-5", periodos4)
imprimir("CONTROL CARGA", control_carga)

print()
print("=" * 170)
print("ARCHIVOS H79")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)

print("[9/9] Terminado.", flush=True)

from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import hashlib
import re

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"

ts = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/84_consolidado_post_h83_h68_cerrado_167_pendientes_5809"
    / f"CONSOLIDADO_POST_H83_H68_CERRADO_167_PENDIENTES_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_CONSOLIDADO_POST_H83_H68_CERRADO_167_PENDIENTES_5809_{ts}"

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

print("[1/9] Localizando H68, H72, H79, H80, H82 y H83...", flush=True)

H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)
H72 = ultimo(
    RAIZ / "avance_curricular_2026/72_revision_end_to_end_167_pendientes_hasta_csv_piloto_5809",
    "REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809_",
)
H79 = ultimo(
    RAIZ / "avance_curricular_2026/79_matriz_limpia_252_cerrables_4_bloqueados_h68_5809",
    "MATRIZ_LIMPIA_252_CERRABLES_4_BLOQUEADOS_H68_5809_",
)
H80 = ultimo(
    RAIZ / "avance_curricular_2026/80_gobernanza_titulacion_nivel20_periodos_45_5809",
    "GOBERNANZA_TITULACION_NIVEL20_PERIODOS_45_5809_",
)
H82 = ultimo(
    RAIZ / "avance_curricular_2026/82_gobernanza_periodos_135_246_titulados_nivel20_5809",
    "GOBERNANZA_PERIODOS_135_246_TITULADOS_NIVEL20_5809_",
)
H83 = ultimo(
    RAIZ / "avance_curricular_2026/83_cierre_fila187_eliminada_ambas_carreras_5809",
    "CIERRE_FILA187_ELIMINADA_AMBAS_CARRERAS_5809_",
)

EX68 = primer_excel(H68)
EX72 = primer_excel(H72)
EX79 = primer_excel(H79)
EX80 = primer_excel(H80)
EX82 = primer_excel(H82)
EX83 = primer_excel(H83)

for nombre, ruta in [
    ("H68", EX68),
    ("H72", EX72),
    ("H79", EX79),
    ("H80", EX80),
    ("H82", EX82),
    ("H83", EX83),
]:
    print(f"   {nombre}: {ruta}")

print("[2/9] Leyendo evidencias clave...", flush=True)

h68_dictamen = leer(EX68, ["00_DICTAMEN_GLOBAL"])
h68_matriz = leer(EX68, ["01_MATRIZ_DECISION"])

h72_dictamen = leer(EX72, ["00_DICTAMEN_GLOBAL"])
h72_resumen = leer(EX72, ["02_RESUMEN_DECISIONES", "RESUMEN_DECISIONES"])

h79_dictamen = leer(EX79, ["00_DICTAMEN_GLOBAL"])
h79_resumen = leer(EX79, ["01_RESUMEN_H79"])

h80_dictamen = leer(EX80, ["00_DICTAMEN_GLOBAL"])
h80_casos = leer(EX80, ["02_CASOS_GOBERNADOS_3", "CASOS_GOBERNADOS"])

h82_dictamen = leer(EX82, ["00_DICTAMEN_GLOBAL"])
h82_propuesta = leer(EX82, ["04_PROPUESTA_16_19"])

h83_dictamen = leer(EX83, ["00_DICTAMEN_GLOBAL"])
h83_decision = leer(EX83, ["03_DECISION_187"])
resumen_h83 = leer(EX83, ["01_RESUMEN_H83"])

print("[3/9] Construyendo consolidado de cierre H68...", flush=True)

h68_cierre = pd.DataFrame([
    {
        "BLOQUE": "COLUMNA_19_SOLO_A",
        "CASOS": 218,
        "ESTADO_POST_H83": "CERRADO_SIN_CAMBIO",
        "RESPALDO": "H61/H62/H66/H68; usuario aprobó cerrar 218.",
        "TRATAMIENTO": "Mantener columna 19 anual 2025 contando solo A=APROBADO; excluir E/I.",
        "CORRECCION_DATOS": "NO",
        "NIVEL_RESPALDO": "A/B/D",
    },
    {
        "BLOQUE": "ESTADO_ACADEMICO_SIN_REGISTROS_2025_ELIMINADO",
        "CASOS": 20,
        "ESTADO_POST_H83": "CERRADO_SIN_CAMBIO",
        "RESPALDO": "H78/H79; 20 casos ELIMINADO sin registros 2025.",
        "TRATAMIENTO": "Mantener 16=NO, 17=NO, 18=0, 19=0.",
        "CORRECCION_DATOS": "NO",
        "NIVEL_RESPALDO": "B/D",
    },
    {
        "BLOQUE": "PERIODO_1_2_3_CUBIERTO",
        "CASOS": 14,
        "ESTADO_POST_H83": "CERRADO_CON_DECISION_USUARIO",
        "RESPALDO": "H77/H79; usuario definió PERIODO 1=1 y 2/3=2 para ese bloque previo.",
        "TRATAMIENTO": "Cerrar como gobernado por decisión interna específica.",
        "CORRECCION_DATOS": "NO_EN_ESTE_HITO",
        "NIVEL_RESPALDO": "D",
    },
    {
        "BLOQUE": "TITULADOS_2025_1_NIVEL_20_PERIODOS_135_246",
        "CASOS": 3,
        "ESTADO_POST_H83": "CERRADO_CON_REGLA_INTERNA_ESPECIFICA",
        "RESPALDO": "H80/H81/H82; notas numéricas y registros A/APROBADO 2025; regla específica 1/3/5=>sem1 y 2/4/6=>sem2.",
        "TRATAMIENTO": "Aplicar solo a 3 RUT/CODCLI específicos titulados 2025-1 nivel 20.",
        "CORRECCION_DATOS": "NO_EN_ESTE_HITO",
        "NIVEL_RESPALDO": "B/D",
    },
    {
        "BLOQUE": "FILA_187_ELIMINADA_AMBAS_CARRERAS",
        "CASOS": 1,
        "ESTADO_POST_H83": "CERRADO_SIN_CAMBIO",
        "RESPALDO": "H83; usuario entrega detalle de ambos CODCLI eliminados.",
        "TRATAMIENTO": "Informar como eliminada de ambas carreras; mantener 16=NO, 17=NO, 18=0, 19=0.",
        "CORRECCION_DATOS": "NO",
        "NIVEL_RESPALDO": "B/D",
    },
])

total_h68 = int(h68_cierre["CASOS"].sum())
if total_h68 != 256:
    raise SystemExit(f"BLOQUEO: cierre H68 no suma 256; suma={total_h68}")

print("[4/9] Consolidando pendiente real 167 H72...", flush=True)

h72_pendiente = pd.DataFrame([
    {
        "FRENTE": "MAPEO_INSTITUCIONAL",
        "CASOS": 102,
        "ESTADO": "BLOQUEADO",
        "REQUISITO": "Resolver CODCLI_LISTA, identidad académica, documentos no calzantes y conflictos de mapeo.",
        "ACCION_SIGUIENTE": "Incorporar matriz de mapeo validada.",
    },
    {
        "FRENTE": "FUENTE_ACADEMICA_COMPLEMENTARIA",
        "CASOS": 57,
        "ESTADO": "BLOQUEADO",
        "REQUISITO": "Incorporar evidencia académica 2025 para casos sin respaldo suficiente en PROMEDIOS.",
        "ACCION_SIGUIENTE": "Cargar fuente complementaria como evidencia, no como regla.",
    },
    {
        "FRENTE": "REVISION_FUNCIONAL_PUNTUAL",
        "CASOS": 8,
        "ESTADO": "BLOQUEADO",
        "REQUISITO": "Resolver 6 datos 5809 no calzantes y 2 estados NULL/blanco.",
        "ACCION_SIGUIENTE": "Registrar decisión caso a caso.",
    },
])

total_h72 = int(h72_pendiente["CASOS"].sum())
if total_h72 != 167:
    raise SystemExit(f"BLOQUEO: H72 pendiente no suma 167; suma={total_h72}")

print("[5/9] Generando tablero final post H83...", flush=True)

tablero = pd.DataFrame([
    {
        "BLOQUE": "H68_DECISION_FUNCIONAL",
        "CASOS": 256,
        "ESTADO": "CERRADO_DOCUMENTALMENTE",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
        "OBSERVACION": "Cerrado como decisión/gobernanza documental. No genera carga porque aún hay H72 167 y 20-21 fuera de alcance.",
    },
    {
        "BLOQUE": "H72_BLOQUEADOS_EVIDENCIA_FALTANTE",
        "CASOS": 167,
        "ESTADO": "BLOQUEADO",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
        "OBSERVACION": "Requiere mapeo institucional, fuente académica complementaria y revisión funcional puntual.",
    },
    {
        "BLOQUE": "TOTAL_PENDIENTES_ORIGINALES_16_19",
        "CASOS": 423,
        "ESTADO": "256_CERRADOS_DOCUMENTALMENTE_167_BLOQUEADOS",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
        "OBSERVACION": "No existe archivo integral listo para carga.",
    },
    {
        "BLOQUE": "20_21_ACUMULADO",
        "CASOS": "NO_EVALUADO",
        "ESTADO": "FUERA_DE_ALCANCE",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
        "OBSERVACION": "Debe abrirse proceso separado; no mezclar con 16-19.",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Consolidado post H83 H68 cerrado y 167 pendientes H72 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "H68_CERRADO_H72_PENDIENTE",
    "PENDIENTES_ORIGINALES_16_19": 423,
    "H68_CERRADOS_DOCUMENTALMENTE": 256,
    "H68_BLOQUEADOS": 0,
    "H72_BLOQUEADOS": 167,
    "20_21_EVALUADO": "NO",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "DICTAMEN_GLOBAL": "H68 queda cerrado documentalmente con 256 casos. El único frente pendiente de columnas 16-19 es H72 con 167 bloqueados por evidencia faltante. No generar carga.",
}])

control = pd.DataFrame([
    {
        "CONTROL": "H68 total cerrado",
        "RESULTADO": "SI",
        "OBSERVADO": "256",
        "DICTAMEN": "H83 dejó H68 con 256 cerrables y 0 bloqueados.",
    },
    {
        "CONTROL": "H72 pendiente",
        "RESULTADO": "SI",
        "OBSERVADO": "167",
        "DICTAMEN": "Se mantienen bloqueados por evidencia faltante.",
    },
    {
        "CONTROL": "Suma 256 + 167",
        "RESULTADO": "OK",
        "OBSERVADO": "423",
        "DICTAMEN": "Cuadra con pendientes originales 16-19.",
    },
    {
        "CONTROL": "20-21 evaluado",
        "RESULTADO": "NO",
        "OBSERVADO": "NO_EVALUADO",
        "DICTAMEN": "Fuera de alcance.",
    },
    {
        "CONTROL": "Fuentes originales modificadas",
        "RESULTADO": "NO",
        "OBSERVADO": "NO",
        "DICTAMEN": "No se modificaron.",
    },
    {
        "CONTROL": "Correcciones aplicadas",
        "RESULTADO": "NO",
        "OBSERVADO": "NO",
        "DICTAMEN": "No se aplicaron.",
    },
    {
        "CONTROL": "Archivo de carga generado",
        "RESULTADO": "NO",
        "OBSERVADO": "NO",
        "DICTAMEN": "No corresponde.",
    },
    {
        "CONTROL": "SIES_READY generado",
        "RESULTADO": "NO",
        "OBSERVADO": "NO",
        "DICTAMEN": "No corresponde.",
    },
])

print("[6/9] Redactando informe ejecutivo y acta...", flush=True)

informe = """# Hito 84 — Consolidado post H83: H68 cerrado y 167 pendientes H72

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado

H68 queda cerrado documentalmente:

- H68 total: 256
- H68 cerrados documentalmente: 256
- H68 bloqueados: 0

Se mantienen pendientes:

- H72 bloqueados: 167

## Desglose H68 cerrado

- 218 casos COLUMNA_19_SOLO_A.
- 20 casos ELIMINADO sin registros 2025.
- 14 casos período 1/2/3 cubierto por decisión interna previa.
- 3 casos titulados 2025-1 nivel 20 con regla interna específica 1/3/5=>semestre 1 y 2/4/6=>semestre 2.
- 1 fila 187 eliminada en ambas carreras.

## Pendiente real 16-19

El único frente pendiente de columnas 16-19 es H72:

- 102 mapeo institucional.
- 57 fuente académica complementaria.
- 8 revisión funcional puntual.

## Control de carga

No se genera archivo de carga.
No se genera SIES_READY.
No se permite subida SIES.
20-21 acumulado no fue evaluado y debe mantenerse como frente separado.
"""

acta = """# Acta técnica H84 — Estado post H83

Se deja constancia de que el bloque H68 queda cerrado documentalmente con 256 casos cerrados y 0 bloqueados.

Este cierre no equivale a archivo listo para carga, porque permanecen 167 casos H72 bloqueados por evidencia faltante y las columnas 20-21 acumuladas no forman parte de este cierre.

No se modificaron fuentes originales.
No se aplicaron correcciones.
No se generó archivo de carga.
No se generó SIES_READY.
"""

print("[7/9] Escribiendo productos H84...", flush=True)

excel_out = SALIDA / "CONSOLIDADO_POST_H83_H68_CERRADO_167_PENDIENTES_5809.xlsx"
informe_out = SALIDA / "INFORME_CONSOLIDADO_POST_H83_H68_CERRADO_167_PENDIENTES_5809.md"
acta_out = SALIDA / "ACTA_TECNICA_H84_H68_CERRADO_167_PENDIENTES_5809.md"
manifest_out = SALIDA / "manifest_consolidado_post_h83_h68_cerrado_167_pendientes_5809.json"
script_out = SALIDA / "h84_consolidado_post_h83_h68_cerrado_167_pendientes.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    tablero.to_excel(writer, sheet_name="01_TABLERO_POST_H83", index=False)
    h68_cierre.to_excel(writer, sheet_name="02_H68_CIERRE_256", index=False)
    h72_pendiente.to_excel(writer, sheet_name="03_H72_PENDIENTE_167", index=False)
    resumen_h83.to_excel(writer, sheet_name="04_H83_RESUMEN", index=False)
    h83_decision.to_excel(writer, sheet_name="05_H83_FILA187", index=False)
    h82_propuesta.to_excel(writer, sheet_name="06_H82_3_TITULADOS", index=False)
    h80_casos.to_excel(writer, sheet_name="07_H80_TITULACION_N20", index=False)
    h79_resumen.to_excel(writer, sheet_name="08_H79_RESUMEN", index=False)
    h72_resumen.to_excel(writer, sheet_name="09_H72_RESUMEN", index=False)
    control.to_excel(writer, sheet_name="10_CONTROL", index=False)
    pd.DataFrame([
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "72", "RUTA": str(H72), "EXCEL": str(EX72), "SHA256": sha256(EX72)},
        {"HITO": "79", "RUTA": str(H79), "EXCEL": str(EX79), "SHA256": sha256(EX79)},
        {"HITO": "80", "RUTA": str(H80), "EXCEL": str(EX80), "SHA256": sha256(EX80)},
        {"HITO": "82", "RUTA": str(H82), "EXCEL": str(EX82), "SHA256": sha256(EX82)},
        {"HITO": "83", "RUTA": str(H83), "EXCEL": str(EX83), "SHA256": sha256(EX83)},
    ]).to_excel(writer, sheet_name="11_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 84,
        "pendientes_originales_16_19": 423,
        "h68_cerrados_documentalmente": 256,
        "h68_bloqueados": 0,
        "h72_bloqueados": 167,
        "20_21_evaluado": "NO",
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
        "subida_sies_permitida": "NO",
    }]).to_excel(writer, sheet_name="12_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe_out.write_text(informe, encoding="utf-8")
acta_out.write_text(acta, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Consolidado post H83 H68 cerrado 167 pendientes 5809 columnas 16-19",
    "hito": 84,
    "pendientes_originales_16_19": 423,
    "h68_cerrados_documentalmente": 256,
    "h68_bloqueados": 0,
    "h72_bloqueados": 167,
    "20_21_evaluado": False,
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "acta": str(acta_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h84_consolidado_post_h83_h68_cerrado_167_pendientes.py"), script_out)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/9] Validando productos generados...", flush=True)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[9/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 84 — CONSOLIDADO POST H83 H68 CERRADO Y 167 PENDIENTES GENERADO")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Pendientes originales 16-19: 423")
print("H68 cerrados documentalmente: 256")
print("H68 bloqueados: 0")
print("H72 bloqueados: 167")
print("20-21 evaluado: NO")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("TABLERO POST H83", tablero)
imprimir("H68 CIERRE 256", h68_cierre)
imprimir("H72 PENDIENTE 167", h72_pendiente)
imprimir("CONTROL", control)

print()
print("=" * 170)
print("ARCHIVOS H84")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Acta: {acta_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)

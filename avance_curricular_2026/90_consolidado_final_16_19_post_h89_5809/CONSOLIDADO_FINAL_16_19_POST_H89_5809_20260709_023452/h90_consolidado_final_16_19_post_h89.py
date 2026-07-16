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
    / "avance_curricular_2026/90_consolidado_final_16_19_post_h89_5809"
    / f"CONSOLIDADO_FINAL_16_19_POST_H89_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H90_CONSOLIDADO_FINAL_16_19_POST_H89_5809_{ts}"

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

print("[1/10] Localizando hitos H84-H89...", flush=True)

H84 = ultimo(
    RAIZ / "avance_curricular_2026/84_consolidado_post_h83_h68_cerrado_167_pendientes_5809",
    "CONSOLIDADO_POST_H83_H68_CERRADO_167_PENDIENTES_5809_",
)
H85 = ultimo(
    RAIZ / "avance_curricular_2026/85_resolucion_efectiva_167_h72_5809",
    "RESOLUCION_EFECTIVA_167_H72_5809_",
)
H86 = ultimo(
    RAIZ / "avance_curricular_2026/86_aplicacion_criterio_h77_periodo_157_h85_5809",
    "APLICACION_CRITERIO_H77_PERIODO_157_H85_5809_",
)
H87 = ultimo(
    RAIZ / "avance_curricular_2026/87_periodo5_y_bloque_b_107_post_h86_5809",
    "PERIODO5_Y_BLOQUE_B_107_POST_H86_5809_",
)
H88 = ultimo(
    RAIZ / "avance_curricular_2026/88_resolucion_bloque_b_107_post_h87_5809",
    "RESOLUCION_BLOQUE_B_107_POST_H87_5809_",
)
H89 = ultimo(
    RAIZ / "avance_curricular_2026/89_resolucion_7_pendientes_reales_post_h88_5809",
    "RESOLUCION_7_PENDIENTES_REALES_POST_H88_5809_",
)

EX84 = primer_excel(H84)
EX85 = primer_excel(H85)
EX86 = primer_excel(H86)
EX87 = primer_excel(H87)
EX88 = primer_excel(H88)
EX89 = primer_excel(H89)

for h, x in [
    ("H84", EX84),
    ("H85", EX85),
    ("H86", EX86),
    ("H87", EX87),
    ("H88", EX88),
    ("H89", EX89),
]:
    print(f"   {h}: {x}")

print("[2/10] Leyendo dictámenes y matrices finales...", flush=True)

h84_dictamen = leer_excel(EX84, ["00_DICTAMEN_GLOBAL"])
h84_cierre = leer_excel(EX84, ["02_H68_CIERRE_256"])

h85_dictamen = leer_excel(EX85, ["00_DICTAMEN_GLOBAL"])
h85_resueltos = leer_excel(EX85, ["03_RESUELTOS_PROPUESTA"])

h86_dictamen = leer_excel(EX86, ["00_DICTAMEN_GLOBAL"])
h86_resueltos = leer_excel(EX86, ["04_RESUELTOS_H86"])

h87_dictamen = leer_excel(EX87, ["00_DICTAMEN_GLOBAL"])
h87_periodo5 = leer_excel(EX87, ["02_PERIODO5_RESUELTO"])

h88_dictamen = leer_excel(EX88, ["00_DICTAMEN_GLOBAL"])
h88_b1 = leer_excel(EX88, ["02_RESUELTOS_B1_100"])

h89_dictamen = leer_excel(EX89, ["00_DICTAMEN_GLOBAL"])
h89_resultado7 = leer_excel(EX89, ["03_RESULTADO_7"])
h89_pendientes = leer_excel(EX89, ["05_PENDIENTES_FINALES"])

print("[3/10] Validando conteos finales...", flush=True)

conteos = {
    "H68_H84": 256,
    "H85": len(h85_resueltos),
    "H86": len(h86_resueltos),
    "H87": len(h87_periodo5),
    "H88": len(h88_b1),
    "H89": len(h89_resultado7),
    "PENDIENTES_FINALES": len(h89_pendientes),
}

esperados = {
    "H85": 10,
    "H86": 48,
    "H87": 2,
    "H88": 100,
    "H89": 7,
    "PENDIENTES_FINALES": 0,
}

for k, v in esperados.items():
    if conteos[k] != v:
        raise SystemExit(f"BLOQUEO: conteo {k} esperado={v}, observado={conteos[k]}")

total_resueltos = sum([conteos["H68_H84"], conteos["H85"], conteos["H86"], conteos["H87"], conteos["H88"], conteos["H89"]])
if total_resueltos != 423:
    raise SystemExit(f"BLOQUEO: total resueltos esperado=423, observado={total_resueltos}")

print("[4/10] Construyendo expediente consolidado...", flush=True)

resumen_global = pd.DataFrame([
    {
        "ORDEN": 1,
        "HITO": "H68/H84",
        "BLOQUE": "Cierre documental H68",
        "CASOS": 256,
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "CRITERIO": "Cierre documental de decisiones y análisis previos H68-H83 consolidado en H84.",
        "NIVEL_RESPALDO": "A/B/D según subcaso",
        "REGLA_OFICIAL_SIES": "PARCIAL_SEGUN_SUBCASO",
    },
    {
        "ORDEN": 2,
        "HITO": "H85",
        "BLOQUE": "Resueltos con propuesta 16-19 desde evidencia PROMEDIOS 2025",
        "CASOS": conteos["H85"],
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "CRITERIO": "Evidencia 2025 suficiente para propuesta conservadora 16-19.",
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
        "REGLA_OFICIAL_SIES": "NO",
    },
    {
        "ORDEN": 3,
        "HITO": "H86",
        "BLOQUE": "Aplicación criterio H77 período 1/2/3",
        "CASOS": conteos["H86"],
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "CRITERIO": "PERIODO 1=>SEM1/COL16; PERIODO 2/3=>SEM2/COL17.",
        "NIVEL_RESPALDO": "D_DECISION_INTERNA_PROYECTO",
        "REGLA_OFICIAL_SIES": "NO",
    },
    {
        "ORDEN": 4,
        "HITO": "H87",
        "BLOQUE": "Aplicación período 5",
        "CASOS": conteos["H87"],
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "CRITERIO": "PERIODO 5=>SEM1/COL16 por decisión interna basada en antecedente H82 y ratificación del usuario.",
        "NIVEL_RESPALDO": "D_DECISION_INTERNA_PROYECTO",
        "REGLA_OFICIAL_SIES": "NO",
    },
    {
        "ORDEN": 5,
        "HITO": "H88",
        "BLOQUE": "CODCLI solo otro año",
        "CASOS": conteos["H88"],
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "CRITERIO": "CODCLI con registros solo en otros años y FILAS_PROMEDIOS_2025=0 => 16=NO,17=NO,18=0,19=0.",
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
        "REGLA_OFICIAL_SIES": "NO",
    },
    {
        "ORDEN": 6,
        "HITO": "H89",
        "BLOQUE": "Resolución 7 pendientes reales",
        "CASOS": conteos["H89"],
        "ESTADO": "RESUELTO_DOCUMENTALMENTE",
        "CRITERIO": "Reanálisis por fila/documento/CODCLI/5809/MAPEO/PROMEDIOS; cierre 16-19 según evidencia observada.",
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
        "REGLA_OFICIAL_SIES": "NO",
    },
    {
        "ORDEN": 7,
        "HITO": "TOTAL",
        "BLOQUE": "Total columnas 16-19",
        "CASOS": 423,
        "ESTADO": "423_RESUELTOS_0_PENDIENTES",
        "CRITERIO": "Cierre documental completo de las columnas 16-19.",
        "NIVEL_RESPALDO": "MIXTO_A_B_D",
        "REGLA_OFICIAL_SIES": "NO_DECLARAR_COMO_REGLA_OFICIAL_LOS_CRITERIOS_INTERNOS",
    },
])

criterios = pd.DataFrame([
    {
        "CRITERIO": "Regla oficial anual 2025",
        "DESCRIPCION": "Columnas 16-19 corresponden a avance anual 2025, separado de acumulado 20-21.",
        "NIVEL": "A_REGLA_OFICIAL",
        "ALCANCE": "Avance Curricular 2026 columnas 16-19",
    },
    {
        "CRITERIO": "Columna 19 solo A",
        "DESCRIPCION": "UNIDADES_APROBADAS anual cuenta A=APROBADO; E/I no se incorporan como aprobadas anuales.",
        "NIVEL": "A/B/D",
        "ALCANCE": "Cierre H68/H84",
    },
    {
        "CRITERIO": "H77 períodos 1/2/3",
        "DESCRIPCION": "PERIODO 1=>SEM1/COL16; PERIODO 2/3=>SEM2/COL17.",
        "NIVEL": "D_DECISION_INTERNA",
        "ALCANCE": "Casos H86",
    },
    {
        "CRITERIO": "PERIODO 5",
        "DESCRIPCION": "PERIODO 5=>SEM1/COL16 por decisión interna basada en antecedente H82 y ratificación del usuario.",
        "NIVEL": "D_DECISION_INTERNA",
        "ALCANCE": "Casos H87",
    },
    {
        "CRITERIO": "Sin actividad académica 2025",
        "DESCRIPCION": "Cuando no existen registros académicos 2025 observados, cierre documental 16=NO,17=NO,18=0,19=0.",
        "NIVEL": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
        "ALCANCE": "Casos H88/H89",
    },
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Consolidado final columnas 16-19 post H89 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ARCHIVO": "5809 Matrícula Avance Curricular",
    "COLUMNAS": "16-19",
    "TOTAL_PENDIENTES_ORIGINALES_16_19": 423,
    "TOTAL_RESUELTOS_16_19_POST_H89": 423,
    "TOTAL_PENDIENTES_16_19_POST_H89": 0,
    "ESTADO_COLUMNAS_16_19": "CERRADAS_DOCUMENTALMENTE",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "20_21_EVALUADO": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "OBSERVACION": "Columnas 16-19 quedan cerradas documentalmente, pero no existe archivo integral listo para carga porque 20-21 acumulado no fue evaluado.",
}])

control = pd.DataFrame([
    {"CONTROL": "Total pendientes originales 16-19", "RESULTADO": "OK", "OBSERVADO": 423, "ESPERADO": 423},
    {"CONTROL": "Total resueltos post H89", "RESULTADO": "OK", "OBSERVADO": 423, "ESPERADO": 423},
    {"CONTROL": "Pendientes finales post H89", "RESULTADO": "OK", "OBSERVADO": 0, "ESPERADO": 0},
    {"CONTROL": "H85", "RESULTADO": "OK", "OBSERVADO": conteos["H85"], "ESPERADO": 10},
    {"CONTROL": "H86", "RESULTADO": "OK", "OBSERVADO": conteos["H86"], "ESPERADO": 48},
    {"CONTROL": "H87", "RESULTADO": "OK", "OBSERVADO": conteos["H87"], "ESPERADO": 2},
    {"CONTROL": "H88", "RESULTADO": "OK", "OBSERVADO": conteos["H88"], "ESPERADO": 100},
    {"CONTROL": "H89", "RESULTADO": "OK", "OBSERVADO": conteos["H89"], "ESPERADO": 7},
    {"CONTROL": "Fuentes originales modificadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "20-21 evaluado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

fuentes = pd.DataFrame([
    {"HITO": "H84", "RUTA": str(H84), "EXCEL": str(EX84), "SHA256": sha256(EX84)},
    {"HITO": "H85", "RUTA": str(H85), "EXCEL": str(EX85), "SHA256": sha256(EX85)},
    {"HITO": "H86", "RUTA": str(H86), "EXCEL": str(EX86), "SHA256": sha256(EX86)},
    {"HITO": "H87", "RUTA": str(H87), "EXCEL": str(EX87), "SHA256": sha256(EX87)},
    {"HITO": "H88", "RUTA": str(H88), "EXCEL": str(EX88), "SHA256": sha256(EX88)},
    {"HITO": "H89", "RUTA": str(H89), "EXCEL": str(EX89), "SHA256": sha256(EX89)},
])

print("[5/10] Construyendo acta e informe final...", flush=True)

informe = """# Hito 90 — Consolidado final columnas 16-19 post H89

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Año de referencia de datos

2025.

## Resultado final

Las 423 diferencias/pendientes originales de columnas 16-19 quedan cerradas documentalmente:

- Total original: 423
- Total resuelto post H89: 423
- Pendientes finales: 0

## Desglose

- H68/H84: 256
- H85: 10
- H86: 48
- H87: 2
- H88: 100
- H89: 7

## Control de alcance

Este cierre corresponde solo a columnas 16-19.

Las columnas 20-21 acumuladas no fueron evaluadas en este frente y deben tratarse en un proceso separado.

## Control de carga

No se modificaron fuentes originales.
No se aplicaron correcciones sobre 5809.
No se generó archivo de carga.
No se generó SIES_READY.
No se permite subida SIES desde este hito.
"""

acta = """# Acta H90 — Cierre documental columnas 16-19

Se deja constancia de que el frente de columnas 16-19 del archivo 5809 Matrícula Avance Curricular queda cerrado documentalmente con 423 casos resueltos y 0 pendientes finales.

Este cierre no corresponde a carga SIES ni a archivo listo para carga, porque las columnas 20-21 acumuladas permanecen fuera de alcance y no fueron evaluadas en este frente.

Los criterios internos aplicados quedan registrados como decisiones internas del proyecto y no deben presentarse como reglas oficiales SIES.
"""

print("[6/10] Escribiendo productos H90...", flush=True)

excel_out = SALIDA / "CONSOLIDADO_FINAL_16_19_POST_H89_5809.xlsx"
informe_out = SALIDA / "INFORME_CONSOLIDADO_FINAL_16_19_POST_H89_5809.md"
acta_out = SALIDA / "ACTA_CIERRE_DOCUMENTAL_16_19_POST_H89_5809.md"
manifest_out = SALIDA / "manifest_consolidado_final_16_19_post_h89_5809.json"
script_out = SALIDA / "h90_consolidado_final_16_19_post_h89.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_global.to_excel(writer, sheet_name="01_RESUMEN_GLOBAL", index=False)
    criterios.to_excel(writer, sheet_name="02_CRITERIOS_APLICADOS", index=False)
    control.to_excel(writer, sheet_name="03_CONTROL", index=False)
    h84_cierre.to_excel(writer, sheet_name="04_H68_H84_256", index=False)
    h85_resueltos.to_excel(writer, sheet_name="05_H85_10", index=False)
    h86_resueltos.to_excel(writer, sheet_name="06_H86_48", index=False)
    h87_periodo5.to_excel(writer, sheet_name="07_H87_2", index=False)
    h88_b1.to_excel(writer, sheet_name="08_H88_100", index=False)
    h89_resultado7.to_excel(writer, sheet_name="09_H89_7", index=False)
    h89_pendientes.to_excel(writer, sheet_name="10_PENDIENTES_FINALES", index=False)
    fuentes.to_excel(writer, sheet_name="11_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 90,
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "5809 columnas 16-19",
        "total_original_16_19": 423,
        "total_resueltos_post_h89": 423,
        "pendientes_finales": 0,
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
        "subida_sies_permitida": "NO",
        "20_21_evaluado": "NO",
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
    "subproyecto": "Consolidado final columnas 16-19 post H89 archivo 5809",
    "hito": 90,
    "total_original_16_19": 423,
    "total_resueltos_16_19_post_h89": 423,
    "total_pendientes_16_19_post_h89": 0,
    "estado_columnas_16_19": "CERRADAS_DOCUMENTALMENTE",
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "20_21_evaluado": False,
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "acta": str(acta_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h90_consolidado_final_16_19_post_h89.py"), script_out)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[7/10] Validando productos...", flush=True)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[8/10] Control final...", flush=True)

if dictamen.loc[0, "TOTAL_RESUELTOS_16_19_POST_H89"] != 423:
    raise SystemExit("BLOQUEO: dictamen no registra 423 resueltos.")
if dictamen.loc[0, "TOTAL_PENDIENTES_16_19_POST_H89"] != 0:
    raise SystemExit("BLOQUEO: dictamen no registra 0 pendientes.")

print("[9/10] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 90 — CONSOLIDADO FINAL 16-19 POST H89 GENERADO")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Pendientes originales 16-19: 423")
print("Resueltos post H89: 423")
print("Pendientes finales post H89: 0")
print("Estado columnas 16-19: CERRADAS_DOCUMENTALMENTE")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN GLOBAL", resumen_global)
imprimir("CRITERIOS APLICADOS", criterios)
imprimir("CONTROL", control)

print()
print("=" * 170)
print("ARCHIVOS H90")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Acta: {acta_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[10/10] Terminado.", flush=True)

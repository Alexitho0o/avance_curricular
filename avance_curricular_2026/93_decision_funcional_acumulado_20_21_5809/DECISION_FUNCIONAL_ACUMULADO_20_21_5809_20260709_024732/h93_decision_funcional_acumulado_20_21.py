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
    / "avance_curricular_2026/93_decision_funcional_acumulado_20_21_5809"
    / f"DECISION_FUNCIONAL_ACUMULADO_20_21_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H93_DECISION_FUNCIONAL_ACUMULADO_20_21_5809_{ts}"

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

print("[1/9] Localizando H90 y H92...", flush=True)

H90 = ultimo(
    RAIZ / "avance_curricular_2026/90_consolidado_final_16_19_post_h89_5809",
    "CONSOLIDADO_FINAL_16_19_POST_H89_5809_",
)

H92 = ultimo(
    RAIZ / "avance_curricular_2026/92_analisis_escenarios_acumulados_20_21_5809",
    "ANALISIS_ESCENARIOS_ACUMULADOS_20_21_5809_",
)

EX90 = primer_excel(H90)
EX92 = primer_excel(H92)

print(f"   H90: {EX90}")
print(f"   H92: {EX92}")

print("[2/9] Leyendo evidencias...", flush=True)

h90_dictamen = leer_excel(EX90, ["00_DICTAMEN_GLOBAL"])
h92_dictamen = leer_excel(EX92, ["00_DICTAMEN_GLOBAL"])
resumen_ei = leer_excel(EX92, ["01_RESUMEN_IMPACTO_EI"])
resumen_clasificacion = leer_excel(EX92, ["02_RESUMEN_CLASIFICACION"])
criterios_h92 = leer_excel(EX92, ["04_CRITERIOS_CANDIDATOS"])
analisis = leer_excel(EX92, ["05_ANALISIS_ESCENARIOS"])
extractos = leer_excel(EX92, ["08_EXTRACTOS_INSTRUCTIVO"])
control_h92 = leer_excel(EX92, ["09_CONTROL"])

if len(analisis) != 2371:
    raise SystemExit(f"BLOQUEO: se esperaban 2371 filas en H92, observado={len(analisis)}")

print("[3/9] Preparando matriz candidata acumulada 20-21...", flush=True)

for c in ["20_ESCENARIO_A_E_I_R", "21_ESCENARIO_A_E_I"]:
    if c not in analisis.columns:
        raise SystemExit(f"BLOQUEO: falta columna {c} en H92.")

matriz_candidata = analisis.copy()

matriz_candidata["20_CANDIDATO_UNID_CURSADAS_TOTAL"] = pd.to_numeric(
    matriz_candidata["20_ESCENARIO_A_E_I_R"], errors="coerce"
).fillna(0).astype(int)

matriz_candidata["21_CANDIDATO_UNID_APROBADAS_TOTAL"] = pd.to_numeric(
    matriz_candidata["21_ESCENARIO_A_E_I"], errors="coerce"
).fillna(0).astype(int)

matriz_candidata["CRITERIO_H93"] = (
    "20=A/E/I/R acumulado hasta 2025; 21=A/E/I acumulado hasta 2025"
)
matriz_candidata["NIVEL_RESPALDO_H93"] = "B_DATO_OBSERVADO_D_DECISION_FUNCIONAL"
matriz_candidata["REGLA_OFICIAL_SIES"] = "NO"
matriz_candidata["CORRECCION_APLICADA"] = "NO"
matriz_candidata["GENERA_CARGA"] = "NO"
matriz_candidata["ESTADO_H93"] = "MATRIZ_CANDIDATA_20_21_DEFINIDA"

print("[4/9] Resumiendo decisión e impacto...", flush=True)

total_20 = int(matriz_candidata["20_CANDIDATO_UNID_CURSADAS_TOTAL"].sum())
total_21 = int(matriz_candidata["21_CANDIDATO_UNID_APROBADAS_TOTAL"].sum())

filas_con_ei = int((matriz_candidata["TIENE_EI_IMPACTO_TOTAL"] == "SI").sum())
filas_sin_ei = int((matriz_candidata["TIENE_EI_IMPACTO_TOTAL"] == "NO").sum())

dif20 = int(pd.to_numeric(matriz_candidata["DIF_20_EI_EN_CURSADAS"], errors="coerce").fillna(0).sum())
dif21 = int(pd.to_numeric(matriz_candidata["DIF_21_EI_EN_APROBADAS"], errors="coerce").fillna(0).sum())

decision = pd.DataFrame([
    {
        "DECISION": "CRITERIO_FUNCIONAL_ACUMULADO_20_21",
        "COLUMNA_20": "UNID_CURSADAS_TOTAL = A/E/I/R acumulado hasta 2025",
        "COLUMNA_21": "UNID_APROBADAS_TOTAL = A/E/I acumulado hasta 2025",
        "JUSTIFICACION": (
            "Para acumulado, E/I representan avance reconocido en trayectoria académica. "
            "Se separa del criterio anual 16-19 y se registra como decisión funcional interna."
        ),
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_FUNCIONAL",
        "REGLA_OFICIAL_SIES": "NO",
        "APLICA_A": "Columnas 20-21 acumuladas del archivo 5809",
        "NO_APLICA_A": "Columnas 16-19 anuales ya cerradas en H90",
    }
])

resumen_global = pd.DataFrame([
    {
        "BLOQUE": "16-19",
        "ESTADO": "CERRADAS_DOCUMENTALMENTE_EN_H90",
        "CASOS": 423,
        "OBSERVACION": "No se reabre en H93.",
    },
    {
        "BLOQUE": "20-21",
        "ESTADO": "CRITERIO_FUNCIONAL_DEFINIDO",
        "CASOS": len(matriz_candidata),
        "OBSERVACION": "Se define matriz candidata acumulada A/E/I/R y A/E/I.",
    },
    {
        "BLOQUE": "IMPACTO_EI",
        "ESTADO": "MEDIDO_EN_H92",
        "CASOS": filas_con_ei,
        "OBSERVACION": f"E/I impacta {filas_con_ei} filas; diferencia total 20={dif20}, 21={dif21}.",
    },
    {
        "BLOQUE": "CARGA",
        "ESTADO": "NO_GENERADA",
        "CASOS": 0,
        "OBSERVACION": "H93 no modifica originales ni genera SIES_READY.",
    },
])

resumen_candidato = pd.DataFrame([
    {"INDICADOR": "Filas matriz candidata", "VALOR": len(matriz_candidata)},
    {"INDICADOR": "Total candidato columna 20", "VALOR": total_20},
    {"INDICADOR": "Total candidato columna 21", "VALOR": total_21},
    {"INDICADOR": "Filas con impacto E/I", "VALOR": filas_con_ei},
    {"INDICADOR": "Filas sin impacto E/I", "VALOR": filas_sin_ei},
    {"INDICADOR": "Diferencia total 20 por E/I", "VALOR": dif20},
    {"INDICADOR": "Diferencia total 21 por E/I", "VALOR": dif21},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H93 decisión funcional acumulado 20-21 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "FILAS_ANALIZADAS": len(matriz_candidata),
    "CRITERIO_20": "A/E/I/R acumulado hasta 2025",
    "CRITERIO_21": "A/E/I acumulado hasta 2025",
    "TOTAL_CANDIDATO_20": total_20,
    "TOTAL_CANDIDATO_21": total_21,
    "FILAS_CON_IMPACTO_EI": filas_con_ei,
    "DIF_TOTAL_20_POR_EI": dif20,
    "DIF_TOTAL_21_POR_EI": dif21,
    "CRITERIO_DEFINITIVO_APLICADO": "SI_COMO_DECISION_FUNCIONAL_INTERNA",
    "REGLA_OFICIAL_SIES": "NO",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "16_19_ESTADO": "CERRADAS_DOCUMENTALMENTE_EN_H90",
    "20_21_ESTADO": "CRITERIO_FUNCIONAL_DEFINIDO_MATRIZ_CANDIDATA",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

control = pd.DataFrame([
    {"CONTROL": "Filas H92 leídas", "RESULTADO": "OK", "OBSERVADO": len(analisis), "ESPERADO": 2371},
    {"CONTROL": "Matriz candidata generada", "RESULTADO": "OK", "OBSERVADO": len(matriz_candidata), "ESPERADO": 2371},
    {"CONTROL": "Criterio 20 definido", "RESULTADO": "OK", "OBSERVADO": "A/E/I/R", "ESPERADO": "A/E/I/R"},
    {"CONTROL": "Criterio 21 definido", "RESULTADO": "OK", "OBSERVADO": "A/E/I", "ESPERADO": "A/E/I"},
    {"CONTROL": "Regla oficial SIES", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Fuentes originales modificadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[5/9] Redactando acta e informe...", flush=True)

informe = f"""# Hito 93 — Decisión funcional acumulado 20-21

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 20-21 acumuladas.

## Decisión funcional interna

Se define el criterio funcional candidato para acumulado 20-21:

- Columna 20 `UNID_CURSADAS_TOTAL`: A/E/I/R acumulado hasta 2025.
- Columna 21 `UNID_APROBADAS_TOTAL`: A/E/I acumulado hasta 2025.

## Nivel de respaldo

B. Dato observado + D. Decisión funcional interna.

No se declara como regla oficial SIES.

## Justificación

El acumulado 20-21 representa trayectoria acumulada hasta 2025.
A diferencia del avance anual 16-19, el acumulado debe reconocer E/I cuando estos representan convalidación u homologación dentro de la trayectoria académica observada.

## Impacto H92

- Filas analizadas: {len(matriz_candidata)}
- Filas con impacto E/I: {filas_con_ei}
- Diferencia total columna 20 por E/I: {dif20}
- Diferencia total columna 21 por E/I: {dif21}
- Total candidato columna 20: {total_20}
- Total candidato columna 21: {total_21}

## Control

No se modifican fuentes originales.
No se genera archivo de carga.
No se genera SIES_READY.
No se permite subida SIES desde este hito.

## Siguiente paso

H94 debe materializar un derivado candidato del 5809 con columnas 16-21 completas, manteniendo trazabilidad y sin modificar el archivo original.
"""

acta = f"""# Acta H93 — Decisión funcional acumulado 20-21

Se registra decisión funcional interna para el frente acumulado 20-21 del archivo 5809 Matrícula Avance Curricular 2026.

## Criterio definido

- 20 UNID_CURSADAS_TOTAL = A/E/I/R acumulado hasta 2025.
- 21 UNID_APROBADAS_TOTAL = A/E/I acumulado hasta 2025.

## Respaldo

- H91 abrió diagnóstico separado de columnas 20-21.
- H92 midió impacto entre escenario conservador y ampliado.
- H93 define el escenario ampliado como matriz candidata.

## Restricciones

Esta decisión no modifica fuentes originales.
Esta decisión no genera archivo de carga.
Esta decisión no corresponde a regla oficial SIES.
Esta decisión queda registrada como criterio funcional interno del proyecto.
"""

print("[6/9] Escribiendo productos H93...", flush=True)

excel_out = SALIDA / "DECISION_FUNCIONAL_ACUMULADO_20_21_5809.xlsx"
informe_out = SALIDA / "INFORME_DECISION_FUNCIONAL_ACUMULADO_20_21_5809.md"
acta_out = SALIDA / "ACTA_DECISION_FUNCIONAL_ACUMULADO_20_21_5809.md"
manifest_out = SALIDA / "manifest_decision_funcional_acumulado_20_21_5809.json"
script_out = SALIDA / "h93_decision_funcional_acumulado_20_21.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    decision.to_excel(writer, sheet_name="01_DECISION_FUNCIONAL", index=False)
    resumen_global.to_excel(writer, sheet_name="02_RESUMEN_GLOBAL", index=False)
    resumen_candidato.to_excel(writer, sheet_name="03_RESUMEN_CANDIDATO", index=False)
    matriz_candidata.to_excel(writer, sheet_name="04_MATRIZ_CANDIDATA_20_21", index=False)
    resumen_ei.to_excel(writer, sheet_name="05_IMPACTO_H92", index=False)
    resumen_clasificacion.to_excel(writer, sheet_name="06_CLASIFICACION_H92", index=False)
    criterios_h92.to_excel(writer, sheet_name="07_CRITERIOS_H92", index=False)
    extractos.to_excel(writer, sheet_name="08_EXTRACTOS_INSTRUCTIVO", index=False)
    control.to_excel(writer, sheet_name="09_CONTROL", index=False)
    pd.DataFrame([
        {"FUENTE": "H90", "RUTA": str(H90), "EXCEL": str(EX90), "SHA256": sha256(EX90)},
        {"FUENTE": "H92", "RUTA": str(H92), "EXCEL": str(EX92), "SHA256": sha256(EX92)},
    ]).to_excel(writer, sheet_name="10_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 93,
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "5809 columnas 20-21 acumuladas",
        "criterio_20": "A/E/I/R acumulado hasta 2025",
        "criterio_21": "A/E/I acumulado hasta 2025",
        "filas_matriz_candidata": len(matriz_candidata),
        "total_candidato_20": total_20,
        "total_candidato_21": total_21,
        "regla_oficial_sies": "NO",
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="11_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "H93 decisión funcional acumulado 20-21 5809",
    "hito": 93,
    "criterio_20": "A/E/I/R acumulado hasta 2025",
    "criterio_21": "A/E/I acumulado hasta 2025",
    "filas_matriz_candidata": len(matriz_candidata),
    "total_candidato_20": total_20,
    "total_candidato_21": total_21,
    "filas_con_impacto_ei": filas_con_ei,
    "dif_total_20_por_ei": dif20,
    "dif_total_21_por_ei": dif21,
    "regla_oficial_sies": False,
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h93_decision_funcional_acumulado_20_21.py"), script_out)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[7/9] Validando productos...", flush=True)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[8/9] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 93 — DECISIÓN FUNCIONAL ACUMULADO 20-21 GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 20-21 acumuladas")
print("Criterio 20: A/E/I/R acumulado hasta 2025")
print("Criterio 21: A/E/I acumulado hasta 2025")
print(f"Filas matriz candidata: {len(matriz_candidata)}")
print(f"Total candidato columna 20: {total_20}")
print(f"Total candidato columna 21: {total_21}")
print(f"Filas con impacto E/I: {filas_con_ei}")
print(f"Diferencia total 20 por E/I: {dif20}")
print(f"Diferencia total 21 por E/I: {dif21}")
print("Regla oficial SIES: NO")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("DECISION FUNCIONAL", decision)
imprimir("RESUMEN GLOBAL", resumen_global)
imprimir("RESUMEN CANDIDATO", resumen_candidato)
imprimir("CONTROL", control)

print()
print("=" * 170)
print("ARCHIVOS H93")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Acta: {acta_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[9/9] Terminado.", flush=True)

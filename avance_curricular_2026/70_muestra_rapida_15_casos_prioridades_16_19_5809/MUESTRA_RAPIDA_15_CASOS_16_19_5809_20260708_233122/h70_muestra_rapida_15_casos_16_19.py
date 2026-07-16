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
    / "avance_curricular_2026/70_muestra_rapida_15_casos_prioridades_16_19_5809"
    / f"MUESTRA_RAPIDA_15_CASOS_16_19_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_MUESTRA_RAPIDA_15_CASOS_16_19_5809_{timestamp}"

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

def muestra_priorizada(df, n, causa_col=None, codigo_col=None):
    d = df.copy()
    d["_orden_original"] = range(1, len(d) + 1)

    orden_cols = []
    asc = []

    if causa_col and causa_col in d.columns:
        freq = d[causa_col].value_counts().to_dict()
        d["_freq_causa"] = d[causa_col].map(freq).fillna(0).astype(int)
        orden_cols.append("_freq_causa")
        asc.append(False)

    if codigo_col and codigo_col in d.columns:
        freq_cod = d[codigo_col].value_counts().to_dict()
        d["_freq_codigo"] = d[codigo_col].map(freq_cod).fillna(0).astype(int)
        orden_cols.append("_freq_codigo")
        asc.append(False)

    orden_cols.append("_orden_original")
    asc.append(True)

    d = d.sort_values(orden_cols, ascending=asc).head(n).copy()

    for c in ["_freq_causa", "_freq_codigo", "_orden_original"]:
        if c in d.columns:
            d.drop(columns=[c], inplace=True)

    return d

def imprimir(titulo, df, n=30):
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

print("[1/8] Localizando Hito 69...", flush=True)

H69 = ultimo(
    RAIZ / "avance_curricular_2026/69_paquete_operativo_167_pendientes_16_19_5809",
    "PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_",
)

EX69 = primer_excel(H69)

print(f"   H69: {EX69}", flush=True)

print("[2/8] Leyendo rutas 102 / 57 / 8...", flush=True)

dict69 = leer(EX69, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
resumen69 = leer(EX69, ["01_RESUMEN_RUTAS", "RESUMEN"])
mapeo102 = leer(EX69, ["02_MAPEO_102", "MAPEO"])
fuente57 = leer(EX69, ["03_FUENTE_57", "FUENTE"])
revision8 = leer(EX69, ["04_REVISION_8", "REVISION"])

print("[3/8] Detectando columnas clave...", flush=True)

c_causa_m = col(mapeo102, ["CAUSA_AUDITADA", "CAUSA_PRINCIPAL", "CAUSA"])
c_codigo_m = col(mapeo102, ["CODIGO_UNICO"])

c_causa_f = col(fuente57, ["CAUSA_AUDITADA", "CAUSA_PRINCIPAL", "CAUSA"])
c_codigo_f = col(fuente57, ["CODIGO_UNICO"])

c_causa_r = col(revision8, ["CAUSA_AUDITADA", "CAUSA_PRINCIPAL", "CAUSA"])
c_codigo_r = col(revision8, ["CODIGO_UNICO"])

print("[4/8] Extrayendo muestra 5 + 5 + 5...", flush=True)

muestra_mapeo = muestra_priorizada(mapeo102, 5, c_causa_m, c_codigo_m)
muestra_fuente = muestra_priorizada(fuente57, 5, c_causa_f, c_codigo_f)
muestra_revision = muestra_priorizada(revision8, 5, c_causa_r, c_codigo_r)

muestra_mapeo.insert(0, "PRIORIDAD", "1_MAPEO_INSTITUCIONAL")
muestra_fuente.insert(0, "PRIORIDAD", "2_FUENTE_ACADEMICA_COMPLEMENTARIA")
muestra_revision.insert(0, "PRIORIDAD", "3_REVISION_FUNCIONAL_PUNTUAL")

muestra_total = pd.concat(
    [muestra_mapeo, muestra_fuente, muestra_revision],
    ignore_index=True,
    sort=False,
)

if len(muestra_total) != 15:
    raise SystemExit(f"BLOQUEO: muestra esperada 15 casos, detectada {len(muestra_total)}")

print("[5/8] Armando 20 pasos siguientes...", flush=True)

pasos = pd.DataFrame([
    {"N": 1, "PASO": "Enviar paquete H68 para validación funcional de 256 casos cerrables sin cambio.", "SALIDA": "Respuesta funcional SI/NO por bloque 218/21/17."},
    {"N": 2, "PASO": "Enviar muestra H70 de 15 casos como piloto rápido.", "SALIDA": "Validación preliminar por prioridad."},
    {"N": 3, "PASO": "Revisar los 5 casos de MAPEO_INSTITUCIONAL.", "SALIDA": "Confirmación de CODCLI_LISTA correcto o bloqueo."},
    {"N": 4, "PASO": "Revisar los 5 casos de FUENTE_ACADEMICA_COMPLEMENTARIA.", "SALIDA": "Fuente académica 2025 o confirmación de ausencia."},
    {"N": 5, "PASO": "Revisar los 5 casos de REVISION_FUNCIONAL_PUNTUAL.", "SALIDA": "Decisión mantener/corregir/bloquear."},
    {"N": 6, "PASO": "Registrar respuestas del piloto en una matriz de decisión.", "SALIDA": "Matriz piloto validada."},
    {"N": 7, "PASO": "Si el piloto de mapeo confirma patrón, extender a los 102 casos.", "SALIDA": "Plan de resolución mapeo 102."},
    {"N": 8, "PASO": "Si el piloto de fuente confirma ausencia, extender solicitud a los 57 casos.", "SALIDA": "Plan de fuente académica 57."},
    {"N": 9, "PASO": "Si el piloto de revisión funcional define criterio, extender a los 8 casos.", "SALIDA": "Cierre revisión puntual 8."},
    {"N": 10, "PASO": "Crear H71 con respuestas recibidas del piloto.", "SALIDA": "H71 matriz de respuestas piloto."},
    {"N": 11, "PASO": "Separar respuestas piloto en mantener, corregir, bloquear o solicitar fuente.", "SALIDA": "Clasificación por acción."},
    {"N": 12, "PASO": "No aplicar correcciones hasta validar lote completo o decisión explícita.", "SALIDA": "Control de no modificación."},
    {"N": 13, "PASO": "Preparar paquete completo para los 102 de mapeo si piloto fue suficiente.", "SALIDA": "H72 paquete mapeo completo."},
    {"N": 14, "PASO": "Preparar paquete completo para los 57 de fuente si piloto fue suficiente.", "SALIDA": "H73 paquete fuente completo."},
    {"N": 15, "PASO": "Preparar paquete completo para los 8 de revisión puntual si piloto fue suficiente.", "SALIDA": "H74 revisión puntual completa."},
    {"N": 16, "PASO": "Consolidar decisiones 256 + respuestas de 167.", "SALIDA": "H75 consolidado de decisiones 16-19."},
    {"N": 17, "PASO": "Identificar si queda algún bloqueo material 16-19.", "SALIDA": "Listado final de bloqueos."},
    {"N": 18, "PASO": "Solo si no hay bloqueos, preparar candidato técnico de corrección 16-19.", "SALIDA": "Candidato controlado, no carga."},
    {"N": 19, "PASO": "Validar nuevamente contra instructivo y validador de gobernanza.", "SALIDA": "Dictamen apto/no apto."},
    {"N": 20, "PASO": "Recién después evaluar archivo final; 20-21 sigue separado.", "SALIDA": "Ruta posterior a 16-19."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Muestra rápida 15 casos prioridades 16-19 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "MUESTRA_CONTROLADA",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "RECALCULO_20_21": "NO",
    "MUESTRA_MAPEO": len(muestra_mapeo),
    "MUESTRA_FUENTE": len(muestra_fuente),
    "MUESTRA_REVISION": len(muestra_revision),
    "TOTAL_MUESTRA": len(muestra_total),
    "DICTAMEN_GLOBAL": "Muestra piloto lista para validación rápida. No aplica cambios ni resuelve casos automáticamente.",
}])

print("[6/8] Redactando borrador corto para enviar muestra...", flush=True)

borrador = f"""# Muestra piloto rápida — Avance Curricular 5809 columnas 16-19

Estimados/as,

Adjunto una muestra piloto de 15 casos pendientes para avanzar rápido en la validación de criterios antes de procesar el total de 167 pendientes.

## Composición

- 5 casos de MAPEO_INSTITUCIONAL.
- 5 casos de FUENTE_ACADEMICA_COMPLEMENTARIA.
- 5 casos de REVISION_FUNCIONAL_PUNTUAL.

## Qué se solicita

Para cada caso, indicar una decisión:

1. Mantener valor 5809.
2. Corregir en etapa posterior.
3. Solicitar fuente complementaria.
4. Bloquear por falta de evidencia.
5. Confirmar CODCLI_LISTA correcto, cuando corresponda.

## Importante

Esta muestra no modifica datos.
No genera archivo de carga.
No genera SIES_READY.
No incluye columnas 20-21.

Objetivo: validar rápidamente el criterio de tratamiento antes de escalar a los 167 casos.
"""

informe = f"""# Hito 70 — Muestra rápida 15 casos prioridades 16-19

## Estado

- Proceso: Avance Curricular SIES 2026
- Subproyecto: archivo 5809, columnas 16-19
- Declaración carga: NO_LISTO_PARA_CARGA
- Fuentes originales modificadas: NO
- Correcciones aplicadas: NO
- Archivo de carga generado: NO
- SIES_READY generado: NO
- 20-21 evaluado: NO

## Resultado

Se extrajo muestra controlada de 15 casos:

| Prioridad | Casos |
|---|---:|
| MAPEO_INSTITUCIONAL | {len(muestra_mapeo)} |
| FUENTE_ACADEMICA_COMPLEMENTARIA | {len(muestra_fuente)} |
| REVISION_FUNCIONAL_PUNTUAL | {len(muestra_revision)} |

## Uso

La muestra sirve para validación rápida, no para aplicar correcciones.
"""

print("[7/8] Escribiendo productos...", flush=True)

excel_out = SALIDA / "MUESTRA_RAPIDA_15_CASOS_PRIORIDADES_16_19_5809.xlsx"
informe_out = SALIDA / "INFORME_MUESTRA_RAPIDA_15_CASOS_16_19_5809.md"
manifest_out = SALIDA / "manifest_muestra_rapida_15_casos_16_19_5809.json"
borrador_out = SALIDA / "BORRADOR_ENVIO_MUESTRA_RAPIDA_15_CASOS_16_19_5809.md"
script_out = SALIDA / "h70_muestra_rapida_15_casos_16_19.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    muestra_total.to_excel(writer, sheet_name="01_MUESTRA_15", index=False)
    muestra_mapeo.to_excel(writer, sheet_name="02_MUESTRA_MAPEO_5", index=False)
    muestra_fuente.to_excel(writer, sheet_name="03_MUESTRA_FUENTE_5", index=False)
    muestra_revision.to_excel(writer, sheet_name="04_MUESTRA_REVISION_5", index=False)
    pasos.to_excel(writer, sheet_name="05_20_PASOS_SIGUIENTES", index=False)
    resumen69.to_excel(writer, sheet_name="06_RESUMEN_H69", index=False)
    dict69.to_excel(writer, sheet_name="07_DICTAMEN_H69", index=False)
    pd.DataFrame([
        {"HITO": "69", "RUTA": str(H69), "EXCEL": str(EX69), "SHA256": sha256(EX69)},
        {"HITO": "70", "RUTA": str(SALIDA), "EXCEL": str(excel_out), "SHA256": ""},
    ]).to_excel(writer, sheet_name="08_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "fuentes_modificadas": "NO",
        "correcciones": "NO",
        "archivo_carga": "NO",
        "sies_ready": "NO",
        "recalculo_20_21": "NO",
        "total_muestra": len(muestra_total),
    }]).to_excel(writer, sheet_name="09_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 90)

informe_out.write_text(informe, encoding="utf-8")
borrador_out.write_text(borrador, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Muestra rapida 15 casos prioridades 16-19 archivo 5809",
    "hito": 70,
    "hito69": str(H69),
    "muestra_mapeo": len(muestra_mapeo),
    "muestra_fuente": len(muestra_fuente),
    "muestra_revision": len(muestra_revision),
    "total_muestra": len(muestra_total),
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

shutil.copy2(Path("/tmp/h70_muestra_rapida_15_casos_16_19.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, borrador_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/8] Verificando...", flush=True)

assert len(muestra_total) == 15
assert len(muestra_mapeo) == 5
assert len(muestra_fuente) == 5
assert len(muestra_revision) == 5
assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert borrador_out.exists()
assert script_out.exists()

print()
print("=" * 130)
print("HITO 70 — MUESTRA RÁPIDA 15 CASOS 16-19 GENERADA")
print("=" * 130)
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("MUESTRA POR PRIORIDAD", muestra_total[["PRIORIDAD"]].value_counts().reset_index(name="CASOS"))
imprimir("20 PASOS SIGUIENTES", pasos, 25)

print()
print("=" * 130)
print("ARCHIVOS")
print("=" * 130)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Borrador envío: {borrador_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 130)

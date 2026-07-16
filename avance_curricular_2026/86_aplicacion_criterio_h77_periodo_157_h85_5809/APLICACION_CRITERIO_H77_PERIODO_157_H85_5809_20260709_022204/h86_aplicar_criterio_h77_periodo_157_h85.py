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
    / "avance_curricular_2026/86_aplicacion_criterio_h77_periodo_157_h85_5809"
    / f"APLICACION_CRITERIO_H77_PERIODO_157_H85_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H86_CRITERIO_H77_PERIODO_157_H85_5809_{ts}"

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

def col(df, nombres):
    mapa = {norm_col(c): c for c in df.columns}
    for n in nombres:
        nn = norm_col(n)
        if nn in mapa:
            return mapa[nn]
    for n in nombres:
        nn = norm_col(n)
        for k, v in mapa.items():
            if nn in k:
                return v
    return None

def to_num(x):
    try:
        s = str(x).replace(",", ".").strip()
        if s == "":
            return None
        return float(s)
    except Exception:
        return None

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

print("[1/10] Localizando H85...", flush=True)

H85 = ultimo(
    RAIZ / "avance_curricular_2026/85_resolucion_efectiva_167_h72_5809",
    "RESOLUCION_EFECTIVA_167_H72_5809_",
)
EX85 = primer_excel(H85)

print(f"   H85: {EX85}")

print("[2/10] Leyendo pendientes y evidencia H85...", flush=True)

h85_dictamen = leer_excel(EX85, ["00_DICTAMEN_GLOBAL"])
h85_resumen = leer_excel(EX85, ["01_RESUMEN_GLOBAL"])
h85_estados = leer_excel(EX85, ["02_RESUMEN_ESTADOS"])
h85_resueltos_previos = leer_excel(EX85, ["03_RESUELTOS_PROPUESTA"])
pendientes_157 = leer_excel(EX85, ["04_PENDIENTES_POST_H85"])
evidencia = leer_excel(EX85, ["05_EVIDENCIA_PROM_2025"])
control_h85 = leer_excel(EX85, ["11_CONTROL"])

if len(pendientes_157) != 157:
    raise SystemExit(f"BLOQUEO: se esperaban 157 pendientes H85, observado={len(pendientes_157)}")

print("[3/10] Detectando columnas de evidencia...", flush=True)

c_id = col(evidencia, ["_ID_H85", "ID_H85"])
c_periodo = col(evidencia, ["PERIODO"])
c_estado = col(evidencia, ["ESTADO"])
c_codcli = col(evidencia, ["_CODCLI_NORM", "CODCLI"])
c_doc = col(evidencia, ["_DOC_NORM", "NUM_DOCUMENTO", "RUT"])

if not c_id or not c_periodo or not c_estado:
    raise SystemExit(
        f"BLOQUEO: evidencia H85 no tiene columnas mínimas. "
        f"ID={c_id}, PERIODO={c_periodo}, ESTADO={c_estado}"
    )

evidencia["_ID_H85_N"] = evidencia[c_id].astype(str).str.strip()
evidencia["_PERIODO_NUM"] = evidencia[c_periodo].map(to_num)
evidencia["_ESTADO_NORM"] = evidencia[c_estado].map(norm_txt)

pendientes_157["_ID_H85_N"] = pendientes_157["ID_H85"].astype(str).str.strip()

print("[4/10] Aplicando criterio interno H77 sobre períodos 1/2/3...", flush=True)

resueltos_h86 = []
siguen_pendientes = []
detalle_periodos = []

for _, row in pendientes_157.iterrows():
    idh = str(row["_ID_H85_N"])
    ev = evidencia[evidencia["_ID_H85_N"] == idh].copy()

    base = row.to_dict()
    base["CRITERIO_H86"] = "H77: PERIODO 1=>SEM1/COL16; PERIODO 2/3=>SEM2/COL17"
    base["NIVEL_RESPALDO_H86"] = "D_DECISION_INTERNA_PROYECTO"
    base["REGLA_OFICIAL_SIES"] = "NO"
    base["CORRECCION_APLICADA"] = "NO"
    base["GENERA_CARGA"] = "NO"

    if ev.empty:
        base["ESTADO_H86"] = "NO_RESUELTO_SIN_EVIDENCIA_2025_EN_H85"
        base["TRATAMIENTO_H86"] = "No hay detalle de evidencia PROMEDIOS 2025 asociado al ID_H85."
        base["16_H86"] = ""
        base["17_H86"] = ""
        base["18_H86"] = ""
        base["19_H86"] = ""
        base["PERIODOS_H86"] = ""
        base["ESTADOS_H86"] = ""
        siguen_pendientes.append(base)
        continue

    periodos = sorted(
        set(
            int(x)
            for x in ev["_PERIODO_NUM"].dropna().tolist()
            if float(x).is_integer()
        )
    )
    estados = sorted(set(ev["_ESTADO_NORM"].astype(str)))

    fuera_h77 = [p for p in periodos if p not in [1, 2, 3]]

    cursadas = ev[ev["_ESTADO_NORM"].isin(["A", "R"])]
    aprobadas = ev[ev["_ESTADO_NORM"] == "A"]

    base["PERIODOS_H86"] = " | ".join(map(str, periodos))
    base["ESTADOS_H86"] = " | ".join(estados)
    base["16_H86"] = "SI" if 1 in periodos else "NO"
    base["17_H86"] = "SI" if any(p in periodos for p in [2, 3]) else "NO"
    base["18_H86"] = int(len(cursadas))
    base["19_H86"] = int(len(aprobadas))

    if fuera_h77:
        base["ESTADO_H86"] = "NO_RESUELTO_PERIODO_FUERA_CRITERIO_H77"
        base["TRATAMIENTO_H86"] = (
            "Existe evidencia 2025, pero contiene períodos fuera de 1/2/3. "
            "No se aplica equivalencia no gobernada."
        )
        base["PERIODOS_FUERA_H77"] = " | ".join(map(str, fuera_h77))
        siguen_pendientes.append(base)
    else:
        base["ESTADO_H86"] = "RESUELTO_CON_CRITERIO_INTERNO_H77"
        base["TRATAMIENTO_H86"] = (
            "Caso resuelto documentalmente para columnas 16-19 aplicando decisión interna H77. "
            "No se modifica fuente original ni se genera carga."
        )
        base["PERIODOS_FUERA_H77"] = ""
        resueltos_h86.append(base)

    tmp = ev.copy()
    tmp["_ID_H85"] = idh
    tmp["_ESTADO_H86_CASO"] = base["ESTADO_H86"]
    detalle_periodos.append(tmp)

resueltos_h86 = pd.DataFrame(resueltos_h86)
siguen_pendientes = pd.DataFrame(siguen_pendientes)
detalle_periodos = pd.concat(detalle_periodos, ignore_index=True, sort=False) if detalle_periodos else pd.DataFrame()

total = len(resueltos_h86) + len(siguen_pendientes)
if total != 157:
    raise SystemExit(f"BLOQUEO: total H86 no cuadra. resueltos={len(resueltos_h86)}, pendientes={len(siguen_pendientes)}, total={total}")

print("[5/10] Consolidando estado total 16-19 post H86...", flush=True)

total_resueltos_16_19 = 256 + 10 + len(resueltos_h86)
total_pendientes_16_19 = len(siguen_pendientes)

resumen_global = pd.DataFrame([
    {
        "BLOQUE": "H68_CERRADO_H84",
        "CASOS": 256,
        "ESTADO": "CERRADO_DOCUMENTALMENTE",
        "OBSERVACION": "Cierre documental previo.",
    },
    {
        "BLOQUE": "H85_RESUELTOS_PREVIOS",
        "CASOS": 10,
        "ESTADO": "RESUELTO_CON_PROPUESTA_16_19",
        "OBSERVACION": "Resueltos por evidencia 2025 básica antes de aplicar H77.",
    },
    {
        "BLOQUE": "H86_RESUELTOS_CRITERIO_H77",
        "CASOS": len(resueltos_h86),
        "ESTADO": "RESUELTO_CON_DECISION_INTERNA_H77",
        "OBSERVACION": "Aplicación gobernada PERIODO 1=>SEM1; 2/3=>SEM2.",
    },
    {
        "BLOQUE": "PENDIENTES_POST_H86",
        "CASOS": len(siguen_pendientes),
        "ESTADO": "PENDIENTE",
        "OBSERVACION": "No resueltos por no tener evidencia H85 o por períodos fuera de H77.",
    },
    {
        "BLOQUE": "TOTAL_16_19_ORIGINAL",
        "CASOS": 423,
        "ESTADO": f"{total_resueltos_16_19}_RESUELTOS_{total_pendientes_16_19}_PENDIENTES",
        "OBSERVACION": "Control total 423 pendientes originales.",
    },
])

resumen_estados = (
    pd.concat([resueltos_h86, siguen_pendientes], ignore_index=True, sort=False)
    .groupby(["FRENTE_H72", "ESTADO_H86"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["ESTADO_H86", "FRENTE_H72"])
)

resumen_periodos = (
    pd.concat([resueltos_h86, siguen_pendientes], ignore_index=True, sort=False)
    .groupby(["PERIODOS_H86", "ESTADO_H86"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Aplicación criterio H77 período sobre 157 pendientes H85 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "CRITERIO_APLICADO": "PERIODO 1=>SEM1/COL16; PERIODO 2/3=>SEM2/COL17",
    "NIVEL_RESPALDO": "D_DECISION_INTERNA_PROYECTO",
    "REGLA_OFICIAL_SIES": "NO",
    "UNIVERSO_H86": 157,
    "RESUELTOS_H86": len(resueltos_h86),
    "PENDIENTES_POST_H86": len(siguen_pendientes),
    "TOTAL_RESUELTOS_16_19_POST_H86": total_resueltos_16_19,
    "TOTAL_PENDIENTES_16_19_POST_H86": total_pendientes_16_19,
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "20_21_EVALUADO": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

control = pd.DataFrame([
    {"CONTROL": "Universo H86", "RESULTADO": "OK", "OBSERVADO": total, "ESPERADO": 157},
    {"CONTROL": "Total 423", "RESULTADO": "OK", "OBSERVADO": total_resueltos_16_19 + total_pendientes_16_19, "ESPERADO": 423},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "20-21 evaluado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[6/10] Redactando informe H86...", flush=True)

informe = f"""# Hito 86 — Aplicación gobernada criterio H77 sobre 157 pendientes H85

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Criterio aplicado

Se aplicó la decisión interna registrada en el proyecto:

- PERIODO 1 => primer semestre / columna 16.
- PERIODO 2 y 3 => segundo semestre / columna 17.

Nivel de respaldo: D. Decisión interna del proyecto.
No corresponde presentarlo como regla oficial SIES.

## Resultado H86

- Universo H86: 157
- Resueltos H86 con criterio H77: {len(resueltos_h86)}
- Pendientes post H86: {len(siguen_pendientes)}

## Estado consolidado columnas 16-19

- H68 cerrado documentalmente: 256
- H85 resueltos previos: 10
- H86 resueltos por H77: {len(resueltos_h86)}
- Total resueltos 16-19 post H86: {total_resueltos_16_19}
- Total pendientes 16-19 post H86: {total_pendientes_16_19}

## Control

No se modifican fuentes originales.
No se genera archivo de carga.
No se genera SIES_READY.
Las columnas 20-21 permanecen fuera de alcance.
"""

print("[7/10] Escribiendo productos H86...", flush=True)

excel_out = SALIDA / "APLICACION_CRITERIO_H77_PERIODO_157_H85_5809.xlsx"
informe_out = SALIDA / "INFORME_APLICACION_CRITERIO_H77_PERIODO_157_H85_5809.md"
manifest_out = SALIDA / "manifest_aplicacion_criterio_h77_periodo_157_h85_5809.json"
script_out = SALIDA / "h86_aplicar_criterio_h77_periodo_157_h85.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_global.to_excel(writer, sheet_name="01_RESUMEN_GLOBAL", index=False)
    resumen_estados.to_excel(writer, sheet_name="02_RESUMEN_ESTADOS", index=False)
    resumen_periodos.to_excel(writer, sheet_name="03_RESUMEN_PERIODOS", index=False)
    resueltos_h86.to_excel(writer, sheet_name="04_RESUELTOS_H86", index=False)
    siguen_pendientes.to_excel(writer, sheet_name="05_PENDIENTES_POST_H86", index=False)
    h85_resueltos_previos.to_excel(writer, sheet_name="06_H85_RESUELTOS_PREVIOS", index=False)
    detalle_periodos.to_excel(writer, sheet_name="07_EVIDENCIA_PERIODOS", index=False)
    control.to_excel(writer, sheet_name="08_CONTROL", index=False)
    h85_estados.to_excel(writer, sheet_name="09_H85_RESUMEN_ESTADOS", index=False)
    pd.DataFrame([
        {"FUENTE": "H85", "RUTA": str(H85), "EXCEL": str(EX85), "SHA256": sha256(EX85)},
    ]).to_excel(writer, sheet_name="10_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 86,
        "criterio": "H77 PERIODO 1=>SEM1; 2/3=>SEM2",
        "universo_h86": 157,
        "resueltos_h86": len(resueltos_h86),
        "pendientes_post_h86": len(siguen_pendientes),
        "total_resueltos_16_19_post_h86": total_resueltos_16_19,
        "total_pendientes_16_19_post_h86": total_pendientes_16_19,
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

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Aplicación criterio H77 período 157 H85 5809 columnas 16-19",
    "hito": 86,
    "criterio": "H77 PERIODO 1=>SEM1; 2/3=>SEM2",
    "nivel_respaldo": "D_DECISION_INTERNA_PROYECTO",
    "regla_oficial_sies": False,
    "universo_h86": 157,
    "resueltos_h86": len(resueltos_h86),
    "pendientes_post_h86": len(siguen_pendientes),
    "total_resueltos_16_19_post_h86": total_resueltos_16_19,
    "total_pendientes_16_19_post_h86": total_pendientes_16_19,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h86_aplicar_criterio_h77_periodo_157_h85.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/10] Validando productos...", flush=True)
for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[9/10] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 86 — APLICACIÓN CRITERIO H77 PERIODO 157 H85 GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Criterio aplicado: H77 PERIODO 1=>SEM1/COL16; PERIODO 2/3=>SEM2/COL17")
print("Nivel respaldo: D_DECISION_INTERNA_PROYECTO")
print("Regla oficial SIES: NO")
print(f"Universo H86: 157")
print(f"Resueltos H86: {len(resueltos_h86)}")
print(f"Pendientes post H86: {len(siguen_pendientes)}")
print(f"Total resueltos 16-19 post H86: {total_resueltos_16_19}")
print(f"Total pendientes 16-19 post H86: {total_pendientes_16_19}")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN GLOBAL", resumen_global)
imprimir("RESUMEN ESTADOS", resumen_estados)
imprimir("RESUMEN PERIODOS", resumen_periodos)
imprimir("CONTROL", control)
imprimir("MUESTRA RESUELTOS H86", resueltos_h86, 30)
imprimir("MUESTRA PENDIENTES POST H86", siguen_pendientes, 30)

print()
print("=" * 170)
print("ARCHIVOS H86")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[10/10] Terminado.", flush=True)

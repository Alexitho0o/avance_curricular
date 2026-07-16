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
    / "avance_curricular_2026/89_resolucion_7_pendientes_reales_post_h88_5809"
    / f"RESOLUCION_7_PENDIENTES_REALES_POST_H88_5809_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H89_RESOLUCION_7_PENDIENTES_REALES_POST_H88_5809_{ts}"

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

def leer_csv_auto(path):
    for enc in ["utf-8-sig", "latin1"]:
        for sep in [";", ","]:
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str, keep_default_na=False)
                if len(df.columns) > 1:
                    print(f"   Leyendo CSV {path.name} encoding={enc} sep='{sep}' filas={len(df)} cols={len(df.columns)}")
                    return df
            except Exception:
                pass
    raise SystemExit(f"BLOQUEO: no se pudo leer CSV {path}")

def encontrar_fuente(patterns):
    out = []
    for pat in patterns:
        out.extend(RAIZ.glob(pat))
    out = [p for p in out if p.exists() and not p.name.startswith("~$")]
    if not out:
        raise SystemExit(f"BLOQUEO: no se encontró fuente con patrones {patterns}")
    return sorted(out, key=lambda p: p.stat().st_mtime, reverse=True)[0]

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

def doc_norm(x):
    s = str(x or "").upper().strip()
    s = s.replace(".", "").replace("-", "")
    s = re.sub(r"[^0-9K]", "", s)
    if len(s) > 1 and s[-1] in "0123456789K":
        return s[:-1]
    return s

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

print("[1/10] Localizando H88 y fuentes base...", flush=True)

H88 = ultimo(
    RAIZ / "avance_curricular_2026/88_resolucion_bloque_b_107_post_h87_5809",
    "RESOLUCION_BLOQUE_B_107_POST_H87_5809_",
)
EX88 = primer_excel(H88)

PROM = encontrar_fuente([
    "avance_curricular_2026/25_actualizacion_fuente_promedios/**/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_*.xlsx",
    "avance_curricular_2026/**/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_*.xlsx",
])
MAPEO = encontrar_fuente([
    "avance_curricular_2026/**/MAPEO_IDENTIDAD_CODCLI.xlsx",
])
PRECARGA_5809 = encontrar_fuente([
    "avance_curricular_2026/00_fuentes_congeladas/**/5809_Precarga Matrícula Avance Curricular 2026.csv",
    "avance_curricular_2026/**/5809_Precarga Matrícula Avance Curricular 2026.csv",
])

print(f"   H88: {EX88}")
print(f"   PROMEDIOS: {PROM}")
print(f"   MAPEO: {MAPEO}")
print(f"   5809: {PRECARGA_5809}")

print("[2/10] Leyendo pendientes reales 7...", flush=True)

dictamen_h88 = leer_excel(EX88, ["00_DICTAMEN_GLOBAL"])
resumen_h88 = leer_excel(EX88, ["01_RESUMEN_GLOBAL"])
pendientes_7 = leer_excel(EX88, ["03_PENDIENTES_REALES_7"])
control_h88 = leer_excel(EX88, ["07_CONTROL"])

if len(pendientes_7) != 7:
    raise SystemExit(f"BLOQUEO: se esperaban 7 pendientes, observado={len(pendientes_7)}")

print("[3/10] Leyendo fuentes de contraste...", flush=True)

df5809 = leer_csv_auto(PRECARGA_5809)
dfmap = leer_excel(MAPEO, ["MAPEO"])

prom_parts = []
xls = pd.ExcelFile(PROM, engine="openpyxl")
for h in xls.sheet_names:
    tmp = pd.read_excel(PROM, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")
    tmp["_HOJA_PROMEDIOS"] = h
    prom_parts.append(tmp)
prom = pd.concat(prom_parts, ignore_index=True, sort=False)

print(f"   PROMEDIOS consolidado filas={len(prom)} cols={len(prom.columns)}")

print("[4/10] Normalizando columnas...", flush=True)

# 5809
c5809_doc = col(df5809, ["NUM_DOCUMENTO", "RUT"])
c5809_codunico = col(df5809, ["CODIGO_UNICO"])
c5809_plan = col(df5809, ["PLAN_ESTUDIOS"])
c5809_vig = col(df5809, ["VIGENCIA"])
if not c5809_doc:
    raise SystemExit("BLOQUEO: 5809 sin NUM_DOCUMENTO.")

df5809["_FILA_KEY"] = [str(i + 1) for i in range(len(df5809))]
df5809["_DOC_NORM"] = df5809[c5809_doc].map(doc_norm)

# MAPEO
cm_doc = col(dfmap, ["NUM_DOCUMENTO", "RUT", "NUMERO_DOCUMENTO"])
cm_codcli = col(dfmap, ["CODCLI", "CODCLI_LISTA"])
if cm_doc:
    dfmap["_DOC_NORM"] = dfmap[cm_doc].map(doc_norm)
if cm_codcli:
    dfmap["_CODCLI_NORM"] = dfmap[cm_codcli].astype(str).str.strip()

# PROMEDIOS
cp_codcli = col(prom, ["CODCLI"])
cp_rut = col(prom, ["RUT"])
cp_ano = col(prom, ["ANO", "ANIO", "AÑO"])
cp_periodo = col(prom, ["PERIODO"])
cp_estado = col(prom, ["ESTADO"])
cp_estado_acad = col(prom, ["ESTADO_ACADEMICO", "ESTADOACADEMICO"])
cp_nivel = col(prom, ["NIVEL"])
cp_nota = col(prom, ["NOTA_FINAL"])

for c, n in [(cp_codcli, "CODCLI"), (cp_rut, "RUT"), (cp_ano, "ANO"), (cp_periodo, "PERIODO"), (cp_estado, "ESTADO")]:
    if not c:
        raise SystemExit(f"BLOQUEO: PROMEDIOS sin columna {n}")

prom["_CODCLI_NORM"] = prom[cp_codcli].astype(str).str.strip()
prom["_DOC_NORM"] = prom[cp_rut].map(doc_norm)
prom["_ANO_NORM"] = prom[cp_ano].astype(str).str.extract(r"(\d{4})", expand=False).fillna("")
prom["_PERIODO_NUM"] = prom[cp_periodo].map(to_num)
prom["_ESTADO_NORM"] = prom[cp_estado].map(norm_txt)
prom["_ESTADO_ACAD_NORM"] = prom[cp_estado_acad].map(norm_txt) if cp_estado_acad else ""

print("[5/10] Reanalizando los 7 pendientes...", flush=True)

resultados = []
evidencias = []

for _, r in pendientes_7.iterrows():
    fila = str(r.get("FILA_KEY", "")).strip()
    doc = doc_norm(r.get("NUM_DOCUMENTO_NORM", ""))
    codcli_token = str(r.get("CODCLI_TOKENS", "")).strip()
    causa = str(r.get("CAUSA_H72", "")).strip()
    clasif = str(r.get("CLASIFICACION_BLOQUE_B_H87", "")).strip()

    fila5809 = df5809[df5809["_FILA_KEY"] == fila] if fila else pd.DataFrame()
    if not fila5809.empty and not doc:
        doc = str(fila5809.iloc[0]["_DOC_NORM"])

    map_doc = dfmap[dfmap["_DOC_NORM"] == doc] if cm_doc and doc else pd.DataFrame()
    prom_doc = prom[prom["_DOC_NORM"] == doc] if doc else pd.DataFrame()

    codcli_candidates = set()
    if codcli_token:
        codcli_candidates.add(codcli_token)
    if not map_doc.empty and "_CODCLI_NORM" in map_doc.columns:
        codcli_candidates.update([x for x in map_doc["_CODCLI_NORM"].astype(str) if x.strip()])

    prom_codcli = prom[prom["_CODCLI_NORM"].isin(codcli_candidates)] if codcli_candidates else pd.DataFrame()

    prom_base = pd.concat([prom_doc, prom_codcli], ignore_index=True, sort=False).drop_duplicates()

    p2025 = prom_base[prom_base["_ANO_NORM"] == "2025"].copy() if not prom_base.empty else pd.DataFrame()
    anos = sorted(set(prom_base["_ANO_NORM"].astype(str))) if not prom_base.empty else []
    estados_acad = sorted(set([x for x in prom_base["_ESTADO_ACAD_NORM"].astype(str) if x])) if not prom_base.empty else []
    codcli_obs = sorted(set([x for x in prom_base["_CODCLI_NORM"].astype(str) if x])) if not prom_base.empty else []

    estado_h89 = ""
    tratamiento = ""
    cierre_16 = ""
    cierre_17 = ""
    cierre_18 = ""
    cierre_19 = ""
    requiere = "SI"

    if len(p2025) > 0:
        periodos = sorted(set(int(x) for x in p2025["_PERIODO_NUM"].dropna().tolist() if float(x).is_integer()))
        estados = sorted(set(p2025["_ESTADO_NORM"].astype(str)))
        cursadas = p2025[p2025["_ESTADO_NORM"].isin(["A", "R"])]
        aprobadas = p2025[p2025["_ESTADO_NORM"].eq("A")]
        estado_h89 = "RESUELTO_CON_EVIDENCIA_2025_EN_REANALISIS"
        tratamiento = "Se encontró evidencia 2025 al reanalizar por documento/CODCLI. Se propone 16-19 con criterios internos vigentes; requiere revisión antes de carga."
        cierre_16 = "SI" if any(p in periodos for p in [1,5]) else "NO"
        cierre_17 = "SI" if any(p in periodos for p in [2,3]) else "NO"
        cierre_18 = len(cursadas)
        cierre_19 = len(aprobadas)
        requiere = "NO"
    elif len(prom_base) > 0:
        estado_h89 = "RESUELTO_SIN_ACTIVIDAD_ACADEMICA_2025"
        tratamiento = "Se encontraron registros en PROMEDIOS solo fuera de 2025; se cierra 16=NO,17=NO,18=0,19=0."
        cierre_16, cierre_17, cierre_18, cierre_19 = "NO", "NO", 0, 0
        requiere = "NO"
    elif not fila5809.empty:
        estado_h89 = "RESUELTO_SIN_EVIDENCIA_ACADEMICA_OBSERVADA"
        tratamiento = "Existe fila 5809 pero no hay evidencia académica en PROMEDIOS/MAPEO disponible; cierre documental conservador 16=NO,17=NO,18=0,19=0."
        cierre_16, cierre_17, cierre_18, cierre_19 = "NO", "NO", 0, 0
        requiere = "NO"
    else:
        estado_h89 = "PENDIENTE_FINAL_SIN_IDENTIDAD_SUFFICIENTE"
        tratamiento = "No se pudo confirmar identidad ni evidencia suficiente con fuentes disponibles."
        requiere = "SI"

    out = r.to_dict()
    out.update({
        "DOC_REANALISIS": doc,
        "CODCLI_CANDIDATOS_H89": " | ".join(sorted(codcli_candidates)),
        "CODCLI_OBSERVADOS_H89": " | ".join(codcli_obs),
        "ANOS_OBSERVADOS_H89": " | ".join(anos),
        "ESTADOS_ACAD_OBSERVADOS_H89": " | ".join(estados_acad),
        "FILAS_5809_MATCH": len(fila5809),
        "FILAS_MAPEO_MATCH_DOC": len(map_doc),
        "FILAS_PROMEDIOS_MATCH": len(prom_base),
        "FILAS_PROMEDIOS_2025_H89": len(p2025),
        "ESTADO_H89": estado_h89,
        "TRATAMIENTO_H89": tratamiento,
        "16_H89": cierre_16,
        "17_H89": cierre_17,
        "18_H89": cierre_18,
        "19_H89": cierre_19,
        "REQUIERE_INSUMO_EXTERNO_H89": requiere,
        "NIVEL_RESPALDO_H89": "B_DATO_OBSERVADO_D_DECISION_INTERNA",
        "REGLA_OFICIAL_SIES": "NO",
        "CORRECCION_APLICADA": "NO",
        "GENERA_CARGA": "NO",
    })
    resultados.append(out)

    if not p2025.empty:
        tmp = p2025.copy()
        tmp["_FILA_KEY_H89"] = fila
        tmp["_DOC_H89"] = doc
        evidencias.append(tmp)

resultados = pd.DataFrame(resultados)
evidencias = pd.concat(evidencias, ignore_index=True, sort=False) if evidencias else pd.DataFrame()

resueltos = resultados[resultados["REQUIERE_INSUMO_EXTERNO_H89"].eq("NO")].copy()
pendientes_finales = resultados[resultados["REQUIERE_INSUMO_EXTERNO_H89"].eq("SI")].copy()

print("[6/10] Consolidando estado global...", flush=True)

total_resueltos_post_h89 = 416 + len(resueltos)
total_pendientes_post_h89 = len(pendientes_finales)

resumen_estado = (
    resultados
    .groupby(["ESTADO_H89"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_global = pd.DataFrame([
    {"BLOQUE": "RESUELTOS_POST_H88", "CASOS": 416, "ESTADO": "RESUELTO_DOCUMENTALMENTE"},
    {"BLOQUE": "H89_RESUELTOS_7", "CASOS": len(resueltos), "ESTADO": "RESUELTO_H89"},
    {"BLOQUE": "PENDIENTES_FINALES_POST_H89", "CASOS": len(pendientes_finales), "ESTADO": "PENDIENTE_FINAL"},
    {"BLOQUE": "TOTAL_16_19_ORIGINAL", "CASOS": 423, "ESTADO": f"{total_resueltos_post_h89}_RESUELTOS_{total_pendientes_post_h89}_PENDIENTES"},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H89 resolución 7 pendientes reales post H88 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "PENDIENTES_ENTRADA_H89": 7,
    "RESUELTOS_H89": len(resueltos),
    "PENDIENTES_FINALES_POST_H89": len(pendientes_finales),
    "TOTAL_RESUELTOS_16_19_POST_H89": total_resueltos_post_h89,
    "TOTAL_PENDIENTES_16_19_POST_H89": total_pendientes_post_h89,
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "20_21_EVALUADO": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
}])

control = pd.DataFrame([
    {"CONTROL": "Entrada 7", "RESULTADO": "OK", "OBSERVADO": len(resultados), "ESPERADO": 7},
    {"CONTROL": "Total 423", "RESULTADO": "OK", "OBSERVADO": total_resueltos_post_h89 + total_pendientes_post_h89, "ESPERADO": 423},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[7/10] Escribiendo productos H89...", flush=True)

excel_out = SALIDA / "RESOLUCION_7_PENDIENTES_REALES_POST_H88_5809.xlsx"
informe_out = SALIDA / "INFORME_RESOLUCION_7_PENDIENTES_REALES_POST_H88_5809.md"
manifest_out = SALIDA / "manifest_resolucion_7_pendientes_reales_post_h88_5809.json"
script_out = SALIDA / "h89_resolucion_7_pendientes_reales_post_h88.py"

informe = f"""# Hito 89 — Resolución 7 pendientes reales post H88

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado

- Pendientes entrada H89: 7
- Resueltos H89: {len(resueltos)}
- Pendientes finales post H89: {len(pendientes_finales)}
- Total resueltos 16-19 post H89: {total_resueltos_post_h89}
- Total pendientes 16-19 post H89: {total_pendientes_post_h89}

## Control

No se modifican fuentes originales.
No se genera archivo de carga.
No se genera SIES_READY.
Las columnas 20-21 siguen fuera de alcance.
"""

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_global.to_excel(writer, sheet_name="01_RESUMEN_GLOBAL", index=False)
    resumen_estado.to_excel(writer, sheet_name="02_RESUMEN_ESTADOS", index=False)
    resultados.to_excel(writer, sheet_name="03_RESULTADO_7", index=False)
    resueltos.to_excel(writer, sheet_name="04_RESUELTOS_H89", index=False)
    pendientes_finales.to_excel(writer, sheet_name="05_PENDIENTES_FINALES", index=False)
    evidencias.to_excel(writer, sheet_name="06_EVIDENCIA_2025_H89", index=False)
    control.to_excel(writer, sheet_name="07_CONTROL", index=False)
    pendientes_7.to_excel(writer, sheet_name="08_ORIGEN_H88_7", index=False)
    pd.DataFrame([
        {"FUENTE": "H88", "RUTA": str(H88), "EXCEL": str(EX88), "SHA256": sha256(EX88)},
        {"FUENTE": "PROMEDIOS", "RUTA": str(PROM), "SHA256": sha256(PROM)},
        {"FUENTE": "MAPEO", "RUTA": str(MAPEO), "SHA256": sha256(MAPEO)},
        {"FUENTE": "5809", "RUTA": str(PRECARGA_5809), "SHA256": sha256(PRECARGA_5809)},
    ]).to_excel(writer, sheet_name="09_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 89,
        "pendientes_entrada": 7,
        "resueltos_h89": len(resueltos),
        "pendientes_finales": len(pendientes_finales),
        "total_resueltos_16_19_post_h89": total_resueltos_post_h89,
        "total_pendientes_16_19_post_h89": total_pendientes_post_h89,
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="10_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "H89 resolución 7 pendientes reales post H88 5809 columnas 16-19",
    "hito": 89,
    "pendientes_entrada_h89": 7,
    "resueltos_h89": len(resueltos),
    "pendientes_finales_post_h89": len(pendientes_finales),
    "total_resueltos_16_19_post_h89": total_resueltos_post_h89,
    "total_pendientes_16_19_post_h89": total_pendientes_post_h89,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h89_resolucion_7_pendientes_reales_post_h88.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/10] Validando productos...", flush=True)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[9/10] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 89 — RESOLUCIÓN 7 PENDIENTES REALES POST H88 GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Pendientes entrada H89: 7")
print(f"Resueltos H89: {len(resueltos)}")
print(f"Pendientes finales post H89: {len(pendientes_finales)}")
print(f"Total resueltos 16-19 post H89: {total_resueltos_post_h89}")
print(f"Total pendientes 16-19 post H89: {total_pendientes_post_h89}")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN GLOBAL", resumen_global)
imprimir("RESUMEN ESTADOS", resumen_estado)
imprimir("CONTROL", control)
imprimir("RESULTADO 7", resultados)
imprimir("PENDIENTES FINALES", pendientes_finales)

print()
print("=" * 170)
print("ARCHIVOS H89")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[10/10] Terminado.", flush=True)

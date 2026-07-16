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
    / "avance_curricular_2026/94d_materializacion_5809_entregable_16_21"
    / f"MATERIALIZACION_5809_ENTREGABLE_16_21_{ts}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_H94D_MATERIALIZACION_5809_ENTREGABLE_16_21_{ts}"

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

def encontrar_fuente(patterns):
    out = []
    for pat in patterns:
        out.extend(RAIZ.glob(pat))
    out = [p for p in out if p.exists() and not p.name.startswith("~$")]
    if not out:
        raise SystemExit(f"BLOQUEO: no se encontró fuente con patrones {patterns}")
    return sorted(out, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def leer_csv_auto(path):
    for enc in ["utf-8-sig", "latin1"]:
        for sep in [";", ","]:
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str, keep_default_na=False)
                if len(df.columns) > 1:
                    print(f"   Leyendo CSV {path.name} encoding={enc} sep='{sep}' filas={len(df)} cols={len(df.columns)}")
                    return df, enc, sep
            except Exception:
                pass
    raise SystemExit(f"BLOQUEO: no se pudo leer CSV {path}")

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
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl"), h

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

def entero_str(x):
    if pd.isna(x):
        return "0"
    s = str(x).strip()
    if s == "":
        return "0"
    try:
        return str(int(float(s.replace(",", "."))))
    except Exception:
        return "0"

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

print("[1/13] Localizando fuentes oficiales, institucionales y cierres previos...", flush=True)

PRECARGA_5809 = encontrar_fuente([
    "avance_curricular_2026/00_fuentes_congeladas/**/5809_Precarga Matrícula Avance Curricular 2026.csv",
    "avance_curricular_2026/**/5809_Precarga Matrícula Avance Curricular 2026.csv",
])

PROM = encontrar_fuente([
    "avance_curricular_2026/25_actualizacion_fuente_promedios/**/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_*.xlsx",
    "avance_curricular_2026/**/PROMEDIOSDEALUMNOS_7804_ACTUALIZADO_*.xlsx",
])

MAPEO = encontrar_fuente([
    "avance_curricular_2026/**/MAPEO_IDENTIDAD_CODCLI.xlsx",
])

INSTRUCTIVO = encontrar_fuente([
    "avance_curricular_2026/00_fuentes_congeladas/**/Instructivo_Avance Curricular SIES - 2026.txt",
    "avance_curricular_2026/**/Instructivo_Avance Curricular SIES - 2026.txt",
])

H90 = ultimo(
    RAIZ / "avance_curricular_2026/90_consolidado_final_16_19_post_h89_5809",
    "CONSOLIDADO_FINAL_16_19_POST_H89_5809_",
)

H93 = ultimo(
    RAIZ / "avance_curricular_2026/93_decision_funcional_acumulado_20_21_5809",
    "DECISION_FUNCIONAL_ACUMULADO_20_21_5809_",
)

EX90 = primer_excel(H90)
EX93 = primer_excel(H93)

print(f"   5809 original: {PRECARGA_5809}")
print(f"   PROMEDIOS: {PROM}")
print(f"   MAPEO: {MAPEO}")
print(f"   INSTRUCTIVO: {INSTRUCTIVO}")
print(f"   H90: {EX90}")
print(f"   H93: {EX93}")

print("[2/13] Leyendo 5809 original...", flush=True)

df5809, enc5809, sep5809 = leer_csv_auto(PRECARGA_5809)

if len(df5809) != 2371:
    raise SystemExit(f"BLOQUEO: 5809 esperado 2371 filas, observado={len(df5809)}")
if len(df5809.columns) != 22:
    raise SystemExit(f"BLOQUEO: 5809 esperado 22 columnas, observado={len(df5809.columns)}")

cols_oficiales = list(df5809.columns)
df5809["_FILA_KEY"] = [str(i + 1) for i in range(len(df5809))]

c_doc = col(df5809, ["NUM_DOCUMENTO"])
c16 = "CURSO_1ER_SEM"
c17 = "CURSO_2DO_SEM"
c18 = "UNIDADES_CURSADAS"
c19 = "UNIDADES_APROBADAS"
c20 = "UNID_CURSADAS_TOTAL"
c21 = "UNID_APROBADAS_TOTAL"

for c in [c_doc, c16, c17, c18, c19, c20, c21]:
    if not c or c not in df5809.columns:
        raise SystemExit(f"BLOQUEO: columna requerida no encontrada: {c}")

df5809["_DOC_NORM"] = df5809[c_doc].map(doc_norm)

print("[3/13] Leyendo MAPEO y PROMEDIOS...", flush=True)

dfmap, hoja_map = leer_excel(MAPEO, ["MAPEO"])

cm_doc = col(dfmap, ["NUM_DOCUMENTO", "RUT", "NUMERO_DOCUMENTO"])
cm_codcli = col(dfmap, ["CODCLI", "CODCLI_LISTA"])

if cm_doc:
    dfmap["_DOC_NORM"] = dfmap[cm_doc].map(doc_norm)
if cm_codcli:
    dfmap["_CODCLI_NORM"] = dfmap[cm_codcli].astype(str).str.strip()

prom_parts = []
xls = pd.ExcelFile(PROM, engine="openpyxl")
for h in xls.sheet_names:
    tmp = pd.read_excel(PROM, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")
    tmp["_HOJA_PROMEDIOS"] = h
    prom_parts.append(tmp)

prom = pd.concat(prom_parts, ignore_index=True, sort=False)
print(f"   PROMEDIOS consolidado filas={len(prom)} cols={len(prom.columns)}")

cp_codcli = col(prom, ["CODCLI"])
cp_rut = col(prom, ["RUT"])
cp_ano = col(prom, ["ANO", "ANIO", "AÑO"])
cp_periodo = col(prom, ["PERIODO"])
cp_estado = col(prom, ["ESTADO"])
cp_estado_acad = col(prom, ["ESTADO_ACADEMICO", "ESTADOACADEMICO"])

for nombre, c in [
    ("CODCLI", cp_codcli),
    ("RUT", cp_rut),
    ("ANO", cp_ano),
    ("PERIODO", cp_periodo),
    ("ESTADO", cp_estado),
]:
    if not c:
        raise SystemExit(f"BLOQUEO: PROMEDIOS sin columna {nombre}")

prom["_CODCLI_NORM"] = prom[cp_codcli].astype(str).str.strip()
prom["_DOC_NORM"] = prom[cp_rut].map(doc_norm)
prom["_ANO_NUM"] = pd.to_numeric(prom[cp_ano].astype(str).str.extract(r"(\d{4})", expand=False), errors="coerce")
prom["_PERIODO_NUM"] = prom[cp_periodo].map(to_num)
prom["_ESTADO_NORM"] = prom[cp_estado].map(norm_txt)
prom["_ESTADO_ACAD_NORM"] = prom[cp_estado_acad].map(norm_txt) if cp_estado_acad else ""

print("[4/13] Leyendo H90 y H93 como respaldo de decisión...", flush=True)

h90_dictamen, _ = leer_excel(EX90, ["00_DICTAMEN_GLOBAL"])
h93_dictamen, _ = leer_excel(EX93, ["00_DICTAMEN_GLOBAL"])
h93_matriz, _ = leer_excel(EX93, ["04_MATRIZ_CANDIDATA_20_21"])

if len(h93_matriz) != 2371:
    raise SystemExit(f"BLOQUEO: H93 esperado 2371 filas, observado={len(h93_matriz)}")

print("[5/13] Calculando 16-21 para las 2.371 filas...", flush=True)

registros = []
evidencia_muestra = []
periodos_fuera = []

for _, r in df5809.iterrows():
    fila = r["_FILA_KEY"]
    doc = r["_DOC_NORM"]

    map_doc = dfmap[dfmap["_DOC_NORM"].eq(doc)] if cm_doc and doc else pd.DataFrame()

    codcli_candidates = set()
    if not map_doc.empty and "_CODCLI_NORM" in map_doc.columns:
        codcli_candidates.update([x for x in map_doc["_CODCLI_NORM"].astype(str) if x.strip()])

    prom_doc = prom[prom["_DOC_NORM"].eq(doc)] if doc else pd.DataFrame()
    if not prom_doc.empty:
        codcli_candidates.update([x for x in prom_doc["_CODCLI_NORM"].astype(str) if x.strip()])

    prom_codcli = prom[prom["_CODCLI_NORM"].isin(codcli_candidates)] if codcli_candidates else pd.DataFrame()

    prom_base = (
        pd.concat([prom_doc, prom_codcli], ignore_index=True, sort=False)
        .drop_duplicates()
    )

    p2025 = prom_base[prom_base["_ANO_NUM"].eq(2025)].copy()
    phasta2025 = prom_base[
        prom_base["_ANO_NUM"].notna()
        & (prom_base["_ANO_NUM"] <= 2025)
    ].copy()

    # 16-19 anual 2025
    p2025_ar = p2025[p2025["_ESTADO_NORM"].isin(["A", "R"])].copy()
    p2025_a = p2025[p2025["_ESTADO_NORM"].eq("A")].copy()

    periodos_ar = sorted(
        set(
            int(x)
            for x in p2025_ar["_PERIODO_NUM"].dropna().tolist()
            if float(x).is_integer()
        )
    )

    fuera = [p for p in periodos_ar if p not in [1, 2, 3, 4, 5, 6]]
    if fuera:
        periodos_fuera.append({
            "FILA_KEY": fila,
            "NUM_DOCUMENTO": r[c_doc],
            "PERIODOS_FUERA": " | ".join(map(str, fuera)),
            "CODCLI_CANDIDATOS": " | ".join(sorted(codcli_candidates)),
        })

    curso_1 = "SI" if any(p in [1, 5] for p in periodos_ar) else "NO"
    curso_2 = "SI" if any(p in [2, 3, 4, 6] for p in periodos_ar) else "NO"
    unid_cursadas = len(p2025_ar)
    unid_aprobadas = len(p2025_a)

    # 20-21 acumulado hasta 2025
    pacum_curs = phasta2025[phasta2025["_ESTADO_NORM"].isin(["A", "E", "I", "R"])]
    pacum_apr = phasta2025[phasta2025["_ESTADO_NORM"].isin(["A", "E", "I"])]

    unid_curs_total = len(pacum_curs)
    unid_aprob_total = len(pacum_apr)

    estados2025 = sorted(set([x for x in p2025["_ESTADO_NORM"].astype(str) if x]))
    estados_hasta = sorted(set([x for x in phasta2025["_ESTADO_NORM"].astype(str) if x]))
    anos = sorted(set([str(int(x)) for x in prom_base["_ANO_NUM"].dropna().tolist()]))
    estados_acad = sorted(set([x for x in prom_base["_ESTADO_ACAD_NORM"].astype(str) if x]))

    registros.append({
        "FILA_KEY": fila,
        "NUM_DOCUMENTO": r[c_doc],
        "DOC_NORM": doc,
        "CODCLI_CANDIDATOS": " | ".join(sorted(codcli_candidates)),
        "ANOS_PROMEDIOS": " | ".join(anos),
        "ESTADOS_ACAD_OBSERVADOS": " | ".join(estados_acad),
        "FILAS_PROM_BASE": len(prom_base),
        "FILAS_PROM_2025": len(p2025),
        "PERIODOS_AR_2025": " | ".join(map(str, periodos_ar)),
        "ESTADOS_2025": " | ".join(estados2025),
        "ESTADOS_HASTA_2025": " | ".join(estados_hasta),
        "16_CANDIDATO": curso_1,
        "17_CANDIDATO": curso_2,
        "18_CANDIDATO": unid_cursadas,
        "19_CANDIDATO": unid_aprobadas,
        "20_CANDIDATO": unid_curs_total,
        "21_CANDIDATO": unid_aprob_total,
        "CRITERIO_16_19": "16/17 por períodos A/R 2025; 18=A/R 2025; 19=A 2025",
        "CRITERIO_20_21": "20=A/E/I/R acumulado hasta 2025; 21=A/E/I acumulado hasta 2025",
        "NIVEL_RESPALDO": "B_DATO_OBSERVADO_D_DECISION_FUNCIONAL",
    })

    if len(evidencia_muestra) < 500 and (len(p2025) > 0 or len(phasta2025) > 0):
        tmp = phasta2025.head(20).copy()
        tmp["_FILA_KEY_5809"] = fila
        tmp["_NUM_DOCUMENTO_5809"] = r[c_doc]
        evidencia_muestra.append(tmp)

calc = pd.DataFrame(registros)
periodos_fuera_df = pd.DataFrame(periodos_fuera)
evidencia_muestra_df = pd.concat(evidencia_muestra, ignore_index=True, sort=False) if evidencia_muestra else pd.DataFrame()

if len(calc) != 2371:
    raise SystemExit(f"BLOQUEO: cálculo esperado 2371 filas, observado={len(calc)}")

print("[6/13] Materializando entregable sobre copia derivada...", flush=True)

derivado = df5809.copy()

for col_calc, col_5809 in [
    ("16_CANDIDATO", c16),
    ("17_CANDIDATO", c17),
    ("18_CANDIDATO", c18),
    ("19_CANDIDATO", c19),
    ("20_CANDIDATO", c20),
    ("21_CANDIDATO", c21),
]:
    mapa = calc.set_index("FILA_KEY")[col_calc].to_dict()
    derivado[col_5809] = derivado.apply(lambda r: mapa.get(r["_FILA_KEY"], r[col_5809]), axis=1)

derivado_salida = derivado[cols_oficiales].copy()

print("[7/13] Validando estructura de entregable...", flush=True)

validaciones = []

def add_val(nombre, resultado, observado, esperado):
    validaciones.append({
        "VALIDACION": nombre,
        "RESULTADO": resultado,
        "OBSERVADO": observado,
        "ESPERADO": esperado,
    })

add_val("Filas entregable", "OK" if len(derivado_salida) == 2371 else "ERROR", len(derivado_salida), 2371)
add_val("Columnas entregable", "OK" if len(derivado_salida.columns) == 22 else "ERROR", len(derivado_salida.columns), 22)
add_val("Orden columnas conservado", "OK" if list(derivado_salida.columns) == cols_oficiales else "ERROR", "SI", "SI")

for c in [c16, c17]:
    vals = sorted(set(derivado_salida[c].astype(str).str.strip()))
    invalidos = [v for v in vals if v not in ["SI", "NO"]]
    add_val(f"Valores permitidos {c}", "OK" if not invalidos else "ERROR", " | ".join(invalidos), "SI/NO")

for c in [c18, c19, c20, c21]:
    nums = pd.to_numeric(derivado_salida[c], errors="coerce")
    nulos = int(nums.isna().sum())
    negativos = int((nums.fillna(0) < 0).sum())
    decimales = int(((nums.fillna(0) % 1) != 0).sum())
    add_val(f"Numérico {c}", "OK" if nulos == 0 else "ERROR", nulos, 0)
    add_val(f"Entero {c}", "OK" if decimales == 0 else "ERROR", decimales, 0)
    add_val(f"No negativo {c}", "OK" if negativos == 0 else "ERROR", negativos, 0)

# Reglas de consistencia básica.
n_19_mayor_18 = int((pd.to_numeric(derivado_salida[c19]) > pd.to_numeric(derivado_salida[c18])).sum())
n_21_mayor_20 = int((pd.to_numeric(derivado_salida[c21]) > pd.to_numeric(derivado_salida[c20])).sum())
add_val("19 <= 18", "OK" if n_19_mayor_18 == 0 else "ERROR", n_19_mayor_18, 0)
add_val("21 <= 20", "OK" if n_21_mayor_20 == 0 else "ERROR", n_21_mayor_20, 0)

validaciones_df = pd.DataFrame(validaciones)
errores = validaciones_df[validaciones_df["RESULTADO"].eq("ERROR")]

if len(errores) > 0:
    print(errores.to_string(index=False))
    raise SystemExit("BLOQUEO: validaciones críticas fallaron. No se escribe entregable.")

print("[8/13] Construyendo resúmenes...", flush=True)

resumen = pd.DataFrame([
    {"BLOQUE": "5809_ORIGINAL", "FILAS": len(df5809), "COLUMNAS": len(cols_oficiales), "ESTADO": "NO_MODIFICADO"},
    {"BLOQUE": "16-19", "FILAS_CALCULADAS": 2371, "ESTADO": "CALCULADO_INTEGRALMENTE_DESDE_PROMEDIOS_2025"},
    {"BLOQUE": "20-21", "FILAS_CALCULADAS": 2371, "ESTADO": "CALCULADO_INTEGRALMENTE_DESDE_PROMEDIOS_HASTA_2025"},
    {"BLOQUE": "ENTREGABLE_CANDIDATO", "FILAS": len(derivado_salida), "COLUMNAS": len(derivado_salida.columns), "ESTADO": "GENERADO_VALIDADO_ESTRUCTURALMENTE"},
])

resumen_totales = pd.DataFrame([
    {"INDICADOR": "Total columna 18 UNIDADES_CURSADAS", "VALOR": int(pd.to_numeric(derivado_salida[c18], errors="coerce").fillna(0).sum())},
    {"INDICADOR": "Total columna 19 UNIDADES_APROBADAS", "VALOR": int(pd.to_numeric(derivado_salida[c19], errors="coerce").fillna(0).sum())},
    {"INDICADOR": "Total columna 20 UNID_CURSADAS_TOTAL", "VALOR": int(pd.to_numeric(derivado_salida[c20], errors="coerce").fillna(0).sum())},
    {"INDICADOR": "Total columna 21 UNID_APROBADAS_TOTAL", "VALOR": int(pd.to_numeric(derivado_salida[c21], errors="coerce").fillna(0).sum())},
])

resumen_16_17 = (
    derivado_salida.groupby([c16, c17], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("CASOS", ascending=False)
)

resumen_vigencia = (
    derivado_salida.groupby(["VIGENCIA"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values("VIGENCIA")
)

resumen_evidencia = pd.DataFrame([
    {"INDICADOR": "Filas con registros PROMEDIOS base", "VALOR": int((calc["FILAS_PROM_BASE"].astype(int) > 0).sum())},
    {"INDICADOR": "Filas sin registros PROMEDIOS base", "VALOR": int((calc["FILAS_PROM_BASE"].astype(int) == 0).sum())},
    {"INDICADOR": "Filas con registros 2025", "VALOR": int((calc["FILAS_PROM_2025"].astype(int) > 0).sum())},
    {"INDICADOR": "Filas sin registros 2025", "VALOR": int((calc["FILAS_PROM_2025"].astype(int) == 0).sum())},
    {"INDICADOR": "Filas con períodos fuera 1-6 en A/R 2025", "VALOR": len(periodos_fuera_df)},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "H94D materialización entregable candidato 5809 columnas 16-21",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ARCHIVO_ORIGINAL": str(PRECARGA_5809),
    "FILAS": len(derivado_salida),
    "COLUMNAS": len(derivado_salida.columns),
    "CRITERIO_16": "SI si A/R 2025 en PERIODO 1 o 5",
    "CRITERIO_17": "SI si A/R 2025 en PERIODO 2, 3, 4 o 6",
    "CRITERIO_18": "A/R anual 2025",
    "CRITERIO_19": "A anual 2025",
    "CRITERIO_20": "A/E/I/R acumulado hasta 2025",
    "CRITERIO_21": "A/E/I acumulado hasta 2025",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "ENTREGABLE_CANDIDATO_GENERADO": "SI",
    "VALIDACION_ESTRUCTURAL": "OK",
    "ARCHIVO_CARGA_GENERADO": "CANDIDATO_TECNICO_FUNCIONAL",
    "SIES_READY_GENERADO": "NO_DECLARADO",
    "SUBIDA_SIES_PERMITIDA": "NO_HASTA_VALIDACION_FINAL_USUARIO",
    "DECLARACION_CARGA": "ENTREGABLE_CANDIDATO_GENERADO_NO_SUBIR_SIN_REVISION_FINAL",
    "DICTAMEN_CARGA": "CANDIDATO_VALIDADO_ESTRUCTURALMENTE",
}])

control = pd.DataFrame([
    {"CONTROL": "Original no modificado", "RESULTADO": "OK", "OBSERVADO": "NO_MODIFICADO"},
    {"CONTROL": "Entregable candidato generado", "RESULTADO": "OK", "OBSERVADO": "SI"},
    {"CONTROL": "Filas", "RESULTADO": "OK", "OBSERVADO": len(derivado_salida), "ESPERADO": 2371},
    {"CONTROL": "Columnas", "RESULTADO": "OK", "OBSERVADO": len(derivado_salida.columns), "ESPERADO": 22},
    {"CONTROL": "16-19 calculado integral", "RESULTADO": "OK", "OBSERVADO": 2371, "ESPERADO": 2371},
    {"CONTROL": "20-21 calculado integral", "RESULTADO": "OK", "OBSERVADO": 2371, "ESPERADO": 2371},
    {"CONTROL": "CSV sin encabezado", "RESULTADO": "OK", "OBSERVADO": "SI"},
    {"CONTROL": "Separador punto y coma", "RESULTADO": "OK", "OBSERVADO": ";"},
    {"CONTROL": "SIES_READY declarado", "RESULTADO": "NO", "OBSERVADO": "NO_DECLARADO"},
])

print("[9/13] Escribiendo entregable CSV, Excel y auditoría...", flush=True)

csv_entregable = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_ENTREGABLE_CANDIDATO.csv"
xlsx_entregable = SALIDA / "5809_MATRICULA_AVANCE_CURRICULAR_2026_ENTREGABLE_CANDIDATO.xlsx"
excel_auditoria = SALIDA / "AUDITORIA_5809_ENTREGABLE_CANDIDATO_16_21.xlsx"
informe_out = SALIDA / "INFORME_5809_ENTREGABLE_CANDIDATO_16_21.md"
manifest_out = SALIDA / "manifest_5809_entregable_candidato_16_21.json"
script_out = SALIDA / "h94d_materializar_5809_entregable_16_21.py"

# Entregable CSV: sin encabezado, punto y coma.
derivado_salida.to_csv(csv_entregable, sep=";", index=False, header=False, encoding="utf-8-sig")

with pd.ExcelWriter(xlsx_entregable, engine="openpyxl") as writer:
    derivado_salida.to_excel(writer, sheet_name="5809_ENTREGABLE_CON_ENCABEZADO", index=False)
    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

with pd.ExcelWriter(excel_auditoria, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen.to_excel(writer, sheet_name="01_RESUMEN", index=False)
    resumen_totales.to_excel(writer, sheet_name="02_TOTALES", index=False)
    resumen_16_17.to_excel(writer, sheet_name="03_RESUMEN_16_17", index=False)
    resumen_vigencia.to_excel(writer, sheet_name="04_RESUMEN_VIGENCIA", index=False)
    resumen_evidencia.to_excel(writer, sheet_name="05_RESUMEN_EVIDENCIA", index=False)
    validaciones_df.to_excel(writer, sheet_name="06_VALIDACIONES", index=False)
    periodos_fuera_df.to_excel(writer, sheet_name="07_PERIODOS_FUERA", index=False)
    calc.to_excel(writer, sheet_name="08_CALCULO_16_21", index=False)
    evidencia_muestra_df.to_excel(writer, sheet_name="09_MUESTRA_EVIDENCIA", index=False)
    h90_dictamen.to_excel(writer, sheet_name="10_H90_DICTAMEN", index=False)
    h93_dictamen.to_excel(writer, sheet_name="11_H93_DICTAMEN", index=False)
    pd.DataFrame([
        {"FUENTE": "5809_ORIGINAL", "RUTA": str(PRECARGA_5809), "SHA256": sha256(PRECARGA_5809), "ENCODING": enc5809, "SEPARADOR": sep5809},
        {"FUENTE": "PROMEDIOS", "RUTA": str(PROM), "SHA256": sha256(PROM)},
        {"FUENTE": "MAPEO", "RUTA": str(MAPEO), "SHA256": sha256(MAPEO)},
        {"FUENTE": "INSTRUCTIVO", "RUTA": str(INSTRUCTIVO), "SHA256": sha256(INSTRUCTIVO)},
        {"FUENTE": "H90", "RUTA": str(H90), "EXCEL": str(EX90), "SHA256": sha256(EX90)},
        {"FUENTE": "H93", "RUTA": str(H93), "EXCEL": str(EX93), "SHA256": sha256(EX93)},
        {"FUENTE": "CSV_ENTREGABLE_CANDIDATO", "RUTA": str(csv_entregable), "SHA256": sha256(csv_entregable)},
        {"FUENTE": "XLSX_ENTREGABLE_CANDIDATO", "RUTA": str(xlsx_entregable), "SHA256": sha256(xlsx_entregable)},
    ]).to_excel(writer, sheet_name="12_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": "H94D",
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "5809 columnas 16-21",
        "filas": len(derivado_salida),
        "columnas": len(derivado_salida.columns),
        "csv_sin_encabezado": "SI",
        "separador": ";",
        "fuentes_originales_modificadas": "NO",
        "entregable_candidato_generado": "SI",
        "sies_ready_declarado": "NO",
    }]).to_excel(writer, sheet_name="13_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe = f"""# Hito 94D — 5809 entregable candidato 16-21

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular.

## Resultado

Se generó el archivo 5809 como entregable candidato técnico-funcional, con columnas 16-21 calculadas para las 2.371 filas.

## Criterios aplicados

- 16 `CURSO_1ER_SEM`: SI si hay actividad A/R 2025 en período 1 o 5.
- 17 `CURSO_2DO_SEM`: SI si hay actividad A/R 2025 en período 2, 3, 4 o 6.
- 18 `UNIDADES_CURSADAS`: cantidad anual 2025 con estado A/R.
- 19 `UNIDADES_APROBADAS`: cantidad anual 2025 con estado A.
- 20 `UNID_CURSADAS_TOTAL`: acumulado hasta 2025 con A/E/I/R.
- 21 `UNID_APROBADAS_TOTAL`: acumulado hasta 2025 con A/E/I.

## Archivos generados

- CSV entregable candidato sin encabezado: `{csv_entregable}`
- Excel entregable candidato con encabezado: `{xlsx_entregable}`
- Auditoría: `{excel_auditoria}`

## Validación

- Filas: {len(derivado_salida)}
- Columnas: {len(derivado_salida.columns)}
- CSV sin encabezado: SI
- Separador: punto y coma
- Validación estructural: OK

## Control

No se modificó el archivo original.
El archivo queda como entregable candidato.
No se declara SIES_READY hasta revisión final de usuario o hito de validación final.
"""
informe_out.write_text(informe, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H94D 5809 entregable candidato 16-21",
    "filas": len(derivado_salida),
    "columnas": len(derivado_salida.columns),
    "criterio_16": "SI si A/R 2025 en periodo 1 o 5",
    "criterio_17": "SI si A/R 2025 en periodo 2, 3, 4 o 6",
    "criterio_18": "A/R anual 2025",
    "criterio_19": "A anual 2025",
    "criterio_20": "A/E/I/R acumulado hasta 2025",
    "criterio_21": "A/E/I acumulado hasta 2025",
    "csv_entregable_candidato": str(csv_entregable),
    "xlsx_entregable_candidato": str(xlsx_entregable),
    "excel_auditoria": str(excel_auditoria),
    "sha256_csv": sha256(csv_entregable),
    "sha256_xlsx": sha256(xlsx_entregable),
    "fuentes_originales_modificadas": False,
    "entregable_candidato_generado": True,
    "sies_ready_declarado": False,
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h94d_materializar_5809_entregable_16_21.py"), script_out)

for archivo in [csv_entregable, xlsx_entregable, excel_auditoria, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[10/13] Releyendo entregable CSV para validación final...", flush=True)

relectura = pd.read_csv(csv_entregable, sep=";", header=None, dtype=str, keep_default_na=False, encoding="utf-8-sig")
if relectura.shape != (2371, 22):
    raise SystemExit(f"BLOQUEO: CSV entregable esperado 2371x22, observado={relectura.shape}")

print("[11/13] Validando archivos generados...", flush=True)

for archivo in [csv_entregable, xlsx_entregable, excel_auditoria, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[12/13] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 94D — 5809 ENTREGABLE CANDIDATO 16-21 GENERADO")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-21")
print("Filas entregable: 2371")
print("Columnas entregable: 22")
print("CSV: sin encabezado, separador punto y coma")
print("16-19: calculadas integralmente desde PROMEDIOS 2025")
print("20-21: calculadas integralmente desde PROMEDIOS acumulado hasta 2025")
print("Fuentes originales modificadas: NO")
print("Entregable candidato generado: SI")
print("Validación estructural: OK")
print("SIES_READY declarado: NO")
print("Subida SIES permitida: NO hasta revisión final")
print("Declaración carga: ENTREGABLE_CANDIDATO_GENERADO_NO_SUBIR_SIN_REVISION_FINAL")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN", resumen)
imprimir("TOTALES", resumen_totales)
imprimir("RESUMEN 16/17", resumen_16_17)
imprimir("RESUMEN EVIDENCIA", resumen_evidencia)
imprimir("VALIDACIONES", validaciones_df)
imprimir("CONTROL", control)

print()
print("=" * 170)
print("ARCHIVOS H94D")
print("=" * 170)
print(f"CSV entregable candidato: {csv_entregable}")
print(f"Excel entregable candidato: {xlsx_entregable}")
print(f"Auditoría: {excel_auditoria}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[13/13] Terminado.", flush=True)

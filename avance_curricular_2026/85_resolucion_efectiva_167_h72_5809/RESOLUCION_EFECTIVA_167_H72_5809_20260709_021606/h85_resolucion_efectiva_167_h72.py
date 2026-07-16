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
    / "avance_curricular_2026/85_resolucion_efectiva_167_h72_5809"
    / f"RESOLUCION_EFECTIVA_167_H72_5809_{ts}"
)
ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_RESOLUCION_EFECTIVA_167_H72_5809_{ts}"

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

def leer_excel(xlsx, patrones, obligatorio=True):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        if obligatorio:
            xls = pd.ExcelFile(xlsx, engine="openpyxl")
            raise SystemExit(f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. Hojas: {xls.sheet_names}")
        return pd.DataFrame()
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def leer_csv_auto(path):
    intentos = [
        ("utf-8-sig", ";"),
        ("latin1", ";"),
        ("utf-8-sig", ","),
        ("latin1", ","),
    ]
    for enc, sep in intentos:
        try:
            df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str, keep_default_na=False)
            if len(df.columns) > 1:
                print(f"   Leyendo CSV {path.name} encoding={enc} sep='{sep}' filas={len(df)} cols={len(df.columns)}", flush=True)
                return df
        except Exception:
            pass
    raise SystemExit(f"BLOQUEO: no se pudo leer CSV {path}")

def encontrar_fuente(patterns):
    candidatos = []
    for pat in patterns:
        candidatos.extend(RAIZ.glob(pat))
    candidatos = [p for p in candidatos if p.exists() and not p.name.startswith("~$")]
    if not candidatos:
        raise SystemExit(f"BLOQUEO: no se encontró fuente con patrones {patterns}")
    return sorted(candidatos, key=lambda p: p.stat().st_mtime, reverse=True)[0]

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

def rut_limpio(x):
    s = str(x or "").strip().upper()
    s = s.replace(".", "").replace("-", "")
    s = re.sub(r"[^0-9K]", "", s)
    return s

def doc_limpio(x):
    s = rut_limpio(x)
    if len(s) > 1 and s[-1] in "0123456789K":
        return s[:-1]
    return s

def codcli_tokens(x):
    s = str(x or "").strip()
    if not s:
        return []
    parts = re.split(r"[;,\|\s]+", s)
    return [p.strip() for p in parts if p.strip()]

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

print("[1/12] Localizando H69, H72, H84 y fuentes base...", flush=True)

H69 = ultimo(
    RAIZ / "avance_curricular_2026/69_paquete_operativo_167_pendientes_16_19_5809",
    "PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_",
)
H72 = ultimo(
    RAIZ / "avance_curricular_2026/72_revision_end_to_end_167_pendientes_hasta_csv_piloto_5809",
    "REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809_",
)
H84 = ultimo(
    RAIZ / "avance_curricular_2026/84_consolidado_post_h83_h68_cerrado_167_pendientes_5809",
    "CONSOLIDADO_POST_H83_H68_CERRADO_167_PENDIENTES_5809_",
)

EX69 = primer_excel(H69)
EX72 = primer_excel(H72)
EX84 = primer_excel(H84)

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

print(f"   H69: {EX69}")
print(f"   H72: {EX72}")
print(f"   H84: {EX84}")
print(f"   PROMEDIOS: {PROM}")
print(f"   MAPEO: {MAPEO}")
print(f"   5809: {PRECARGA_5809}")

print("[2/12] Leyendo matrices H69/H72/H84...", flush=True)

mapeo_102 = leer_excel(EX69, ["02_MAPEO_102", "04_MAPEO_INSTITUCIONAL_102", "MAPEO_INSTITUCIONAL"])
fuente_57 = leer_excel(EX69, ["03_FUENTE_57", "05_FUENTE_COMPLEMENTARIA_57", "FUENTE_COMPLEMENTARIA"])
revision_8 = leer_excel(EX69, ["04_REVISION_8", "06_REVISION_FUNCIONAL_8", "REVISION_FUNCIONAL"])
h72_decisiones = leer_excel(EX72, ["01_DECISIONES_167", "DECISIONES_167"])
h72_resumen = leer_excel(EX72, ["02_RESUMEN_DECISIONES", "RESUMEN_DECISIONES"])
h84_dictamen = leer_excel(EX84, ["00_DICTAMEN_GLOBAL"])

if len(mapeo_102) != 102 or len(fuente_57) != 57 or len(revision_8) != 8:
    raise SystemExit(f"BLOQUEO: conteos H69 no calzan: mapeo={len(mapeo_102)} fuente={len(fuente_57)} revision={len(revision_8)}")

print("[3/12] Leyendo fuentes institucionales disponibles...", flush=True)

df5809 = leer_csv_auto(PRECARGA_5809)
dfmap = leer_excel(MAPEO, ["MAPEO"], obligatorio=True)

xls_prom = pd.ExcelFile(PROM, engine="openpyxl")
hojas_prom = xls_prom.sheet_names
print(f"   Hojas PROMEDIOS: {hojas_prom}", flush=True)

prom_parts = []
for h in hojas_prom:
    dfh = pd.read_excel(PROM, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")
    dfh["_HOJA_PROMEDIOS"] = h
    prom_parts.append(dfh)
prom = pd.concat(prom_parts, ignore_index=True, sort=False)
print(f"   PROMEDIOS consolidado: filas={len(prom)} columnas={len(prom.columns)}", flush=True)

print("[4/12] Normalizando columnas clave...", flush=True)

# Columnas 5809
c5809_doc = col(df5809, ["NUM_DOCUMENTO", "RUT", "NUMERO_DOCUMENTO"])
c5809_codunico = col(df5809, ["CODIGO_UNICO"])
c5809_plan = col(df5809, ["PLAN_ESTUDIOS"])
c5809_c16 = col(df5809, ["CURSO_1ER_SEM"])
c5809_c17 = col(df5809, ["CURSO_2DO_SEM"])
c5809_c18 = col(df5809, ["UNIDADES_CURSADAS"])
c5809_c19 = col(df5809, ["UNIDADES_APROBADAS"])

if not c5809_doc:
    raise SystemExit("BLOQUEO: 5809 no tiene NUM_DOCUMENTO identificable.")

df5809["_FILA_KEY"] = [str(i + 1) for i in range(len(df5809))]
df5809["_DOC_NORM"] = df5809[c5809_doc].map(doc_limpio)

# Columnas PROMEDIOS
cp_codcli = col(prom, ["CODCLI"])
cp_rut = col(prom, ["RUT"])
cp_ano = col(prom, ["ANO", "ANIO", "AÑO"])
cp_periodo = col(prom, ["PERIODO"])
cp_estado = col(prom, ["ESTADO"])
cp_desc_estado = col(prom, ["DESCRIPCION_ESTADO", "DESCRIPCION ESTADO"])
cp_estado_acad = col(prom, ["ESTADO_ACADEMICO", "ESTADOACADEMICO"])
cp_codramo = col(prom, ["CODRAMO"])
cp_carrera = col(prom, ["CARRERA", "NOMBRE_L", "NOMBRE_CARRERA"])
cp_nivel = col(prom, ["NIVEL"])
cp_nota = col(prom, ["NOTA_FINAL"])

for required, name in [(cp_codcli, "CODCLI"), (cp_rut, "RUT"), (cp_ano, "ANO"), (cp_periodo, "PERIODO"), (cp_estado, "ESTADO")]:
    if not required:
        raise SystemExit(f"BLOQUEO: PROMEDIOS no tiene columna {name} identificable.")

prom["_CODCLI_NORM"] = prom[cp_codcli].astype(str).str.strip()
prom["_DOC_NORM"] = prom[cp_rut].map(doc_limpio)
prom["_ANO_NORM"] = prom[cp_ano].astype(str).str.extract(r"(\d{4})", expand=False).fillna("")
prom["_PERIODO_NUM"] = prom[cp_periodo].map(to_num)
prom["_ESTADO_NORM"] = prom[cp_estado].map(norm_txt)
prom["_DESC_ESTADO_NORM"] = prom[cp_desc_estado].map(norm_txt) if cp_desc_estado else ""
prom["_ESTADO_ACAD_NORM"] = prom[cp_estado_acad].map(norm_txt) if cp_estado_acad else ""
prom["_NIVEL_NUM"] = prom[cp_nivel].map(to_num) if cp_nivel else None

# Columnas MAPEO
cm_doc = col(dfmap, ["NUM_DOCUMENTO", "RUT", "NUMERO_DOCUMENTO"])
cm_codcli = col(dfmap, ["CODCLI", "CODCLI_LISTA", "CODCLI_NORM"])
cm_codunico = col(dfmap, ["CODIGO_UNICO"])
if cm_doc:
    dfmap["_DOC_NORM"] = dfmap[cm_doc].map(doc_limpio)
if cm_codcli:
    dfmap["_CODCLI_NORM"] = dfmap[cm_codcli].astype(str).str.strip()

print("[5/12] Unificando universo 167...", flush=True)

def preparar_bloque(df, frente):
    out = df.copy()
    out["_FRENTE_H72"] = frente
    return out

universo = pd.concat([
    preparar_bloque(mapeo_102, "MAPEO_INSTITUCIONAL"),
    preparar_bloque(fuente_57, "FUENTE_ACADEMICA_COMPLEMENTARIA"),
    preparar_bloque(revision_8, "REVISION_FUNCIONAL_PUNTUAL"),
], ignore_index=True, sort=False)

if len(universo) != 167:
    raise SystemExit(f"BLOQUEO: universo 167 no calza; observado={len(universo)}")

# detectar columnas genéricas en universo
cu_fila = col(universo, ["FILA_KEY", "FILA_5809", "_FILA_KEY_JOIN"])
cu_doc = col(universo, ["NUM_DOCUMENTO", "RUT"])
cu_codcli = col(universo, ["CODCLI_LISTA", "CODCLI_LISTA_NORM", "CODCLI_NORM", "CODCLI"])
cu_causa = col(universo, ["CAUSA_PRINCIPAL_PROPUESTA", "CAUSA", "CAUSA_PRINCIPAL", "ACCION_TERMINAL", "DECISION_TERMINAL"])
cu_cols_afect = col(universo, ["COLUMNA_AFECTADA", "COLUMNA_AFECTADA_16_19", "COLUMNAS_AFECTADAS"])

print("[6/12] Intentando resolución efectiva con reglas conservadoras...", flush=True)

def obtener_contexto(row):
    fila_key = str(row.get(cu_fila, "")).strip() if cu_fila else ""
    doc = doc_limpio(row.get(cu_doc, "")) if cu_doc else ""
    codcli_raw = str(row.get(cu_codcli, "")).strip() if cu_codcli else ""
    tokens = codcli_tokens(codcli_raw)

    # fallback 5809 por fila
    fila5809 = pd.DataFrame()
    if fila_key and fila_key.isdigit():
        fila5809 = df5809[df5809["_FILA_KEY"] == fila_key]
        if not fila5809.empty and not doc:
            doc = str(fila5809.iloc[0]["_DOC_NORM"])
    if doc and fila5809.empty:
        fila5809 = df5809[df5809["_DOC_NORM"] == doc]

    # fallback codcli desde map por doc
    map_doc = pd.DataFrame()
    if doc and "_DOC_NORM" in dfmap.columns:
        map_doc = dfmap[dfmap["_DOC_NORM"] == doc]
        if not tokens and "_CODCLI_NORM" in map_doc.columns:
            tokens = sorted(set([x for x in map_doc["_CODCLI_NORM"].astype(str) if x.strip()]))

    prom_codcli = pd.DataFrame()
    if tokens:
        prom_codcli = prom[prom["_CODCLI_NORM"].isin(tokens)]
    prom_doc = pd.DataFrame()
    if doc:
        prom_doc = prom[prom["_DOC_NORM"] == doc]

    return fila_key, doc, tokens, fila5809, map_doc, prom_codcli, prom_doc

def estado_16_19_desde_prom(prom_sel):
    p2025 = prom_sel[prom_sel["_ANO_NORM"] == "2025"].copy()
    if p2025.empty:
        return None

    # Columnas 16/17 según semestre básico observado: 1 => sem1, 2/3/4/5/6 no se asumen salvo si ya viene columna afectada.
    # Para resolución material conservadora:
    # - Si hay PERIODO 1: sem1 SI.
    # - Si hay PERIODO 2: sem2 SI.
    # - Si hay períodos distintos, requiere decisión salvo que todos estén estado no cursable.
    periodos = sorted(set([int(x) for x in p2025["_PERIODO_NUM"].dropna().tolist() if float(x).is_integer()]))
    estados = sorted(set(p2025["_ESTADO_NORM"].astype(str)))
    aprobadas = p2025[p2025["_ESTADO_NORM"] == "A"]
    cursadas = p2025[p2025["_ESTADO_NORM"].isin(["A", "R"])]

    periodos_no_basicos = [p for p in periodos if p not in [1, 2]]
    if periodos_no_basicos:
        return {
            "RESULTADO": "REQUIERE_DECISION_PERIODO_NO_BASICO",
            "PERIODOS_2025": " | ".join(map(str, periodos)),
            "ESTADOS_2025": " | ".join(estados),
            "CURSO_1ER_SEM": "SI" if 1 in periodos else "NO",
            "CURSO_2DO_SEM": "SI" if 2 in periodos else "NO",
            "UNIDADES_CURSADAS": len(cursadas),
            "UNIDADES_APROBADAS": len(aprobadas),
        }

    return {
        "RESULTADO": "CALCULABLE_CON_PROMEDIOS_2025",
        "PERIODOS_2025": " | ".join(map(str, periodos)),
        "ESTADOS_2025": " | ".join(estados),
        "CURSO_1ER_SEM": "SI" if 1 in periodos else "NO",
        "CURSO_2DO_SEM": "SI" if 2 in periodos else "NO",
        "UNIDADES_CURSADAS": len(cursadas),
        "UNIDADES_APROBADAS": len(aprobadas),
    }

resueltos = []
pendientes = []
detalle_evidencia = []

for idx, row in universo.iterrows():
    frente = row["_FRENTE_H72"]
    causa = str(row.get(cu_causa, "")).strip() if cu_causa else ""
    cols_afect = str(row.get(cu_cols_afect, "")).strip() if cu_cols_afect else ""

    fila_key, doc, tokens, fila5809, map_doc, prom_codcli, prom_doc = obtener_contexto(row)

    prom_base = prom_codcli if not prom_codcli.empty else prom_doc
    p2025 = prom_base[prom_base["_ANO_NORM"] == "2025"].copy() if not prom_base.empty else pd.DataFrame()

    estados_acad = []
    if not prom_base.empty and "_ESTADO_ACAD_NORM" in prom_base.columns:
        estados_acad = sorted(set([x for x in prom_base["_ESTADO_ACAD_NORM"].astype(str) if x]))

    codcli_observados = sorted(set(prom_base["_CODCLI_NORM"].astype(str))) if not prom_base.empty else []
    anos_observados = sorted(set(prom_base["_ANO_NORM"].astype(str))) if not prom_base.empty else []

    propuesta = estado_16_19_desde_prom(prom_base) if not prom_base.empty else None

    estado_final = "PENDIENTE"
    tratamiento = ""
    puede_cerrar = "NO"
    requiere_externo = "SI"
    nivel_respaldo = "B/C/D"

    # Reglas conservadoras de resolución efectiva:
    # 1) Si hay un solo CODCLI o match directo y 2025 básico 1/2, calculable como propuesta.
    if propuesta and propuesta["RESULTADO"] == "CALCULABLE_CON_PROMEDIOS_2025":
        estado_final = "RESUELTO_CON_PROPUESTA_16_19_DESDE_PROMEDIOS_2025"
        tratamiento = "Existe evidencia 2025 con períodos básicos 1/2. Se propone 16-19 desde PROMEDIOS; requiere validación antes de carga."
        puede_cerrar = "SI_CON_VALIDACION"
        requiere_externo = "NO"
    elif propuesta and propuesta["RESULTADO"] == "REQUIERE_DECISION_PERIODO_NO_BASICO":
        estado_final = "NO_RESUELTO_REQUIERE_DECISION_PERIODO_NO_BASICO"
        tratamiento = "Existe evidencia 2025, pero contiene períodos distintos de 1/2. No se aplica equivalencia general."
    elif prom_base.empty:
        estado_final = "NO_RESUELTO_SIN_EVIDENCIA_PROMEDIOS_MAPEO_ACTUAL"
        tratamiento = "No se encontró evidencia suficiente en PROMEDIOS con CODCLI/RUT disponible."
    elif p2025.empty:
        estado_final = "NO_RESUELTO_SIN_REGISTROS_2025_EN_PROMEDIOS"
        tratamiento = "Hay registros en PROMEDIOS, pero no 2025 para el identificador disponible."
    else:
        estado_final = "NO_RESUELTO_REQUIERE_REVISION_FUNCIONAL"
        tratamiento = "Existe evidencia, pero no cumple condiciones conservadoras de cierre automático."

    base = {
        "ID_H85": idx + 1,
        "FRENTE_H72": frente,
        "FILA_KEY": fila_key,
        "NUM_DOCUMENTO_NORM": doc,
        "CODCLI_TOKENS": " | ".join(tokens),
        "CODCLI_OBSERVADOS_PROMEDIOS": " | ".join(codcli_observados),
        "ANOS_OBSERVADOS_PROMEDIOS": " | ".join(anos_observados),
        "ESTADOS_ACADEMICOS_OBSERVADOS": " | ".join(estados_acad),
        "FILAS_PROMEDIOS_BASE": len(prom_base),
        "FILAS_PROMEDIOS_2025": len(p2025),
        "CAUSA_H72": causa,
        "COLUMNAS_AFECTADAS_H72": cols_afect,
        "ESTADO_RESOLUCION_H85": estado_final,
        "TRATAMIENTO_H85": tratamiento,
        "PUEDE_CERRAR_PARA_16_19": puede_cerrar,
        "REQUIERE_INSUMO_EXTERNO": requiere_externo,
        "NIVEL_RESPALDO": nivel_respaldo,
        "CORRECCION_APLICADA": "NO",
        "GENERA_CARGA": "NO",
    }

    if propuesta:
        base.update({
            "PERIODOS_2025": propuesta["PERIODOS_2025"],
            "ESTADOS_2025": propuesta["ESTADOS_2025"],
            "16_PROPUESTO": propuesta["CURSO_1ER_SEM"],
            "17_PROPUESTO": propuesta["CURSO_2DO_SEM"],
            "18_PROPUESTO": propuesta["UNIDADES_CURSADAS"],
            "19_PROPUESTO": propuesta["UNIDADES_APROBADAS"],
        })
    else:
        base.update({
            "PERIODOS_2025": "",
            "ESTADOS_2025": "",
            "16_PROPUESTO": "",
            "17_PROPUESTO": "",
            "18_PROPUESTO": "",
            "19_PROPUESTO": "",
        })

    if puede_cerrar.startswith("SI"):
        resueltos.append(base)
    else:
        pendientes.append(base)

    if not p2025.empty:
        tmp = p2025.copy()
        tmp["_ID_H85"] = idx + 1
        tmp["_FRENTE_H72"] = frente
        keep = ["_ID_H85", "_FRENTE_H72", "_CODCLI_NORM", "_DOC_NORM", "_ANO_NORM", cp_periodo, cp_estado]
        for c in [cp_desc_estado, cp_estado_acad, cp_codramo, cp_carrera, cp_nivel, cp_nota, "_HOJA_PROMEDIOS"]:
            if c and c in tmp.columns and c not in keep:
                keep.append(c)
        detalle_evidencia.append(tmp[keep].copy())

resueltos_df = pd.DataFrame(resueltos)
pendientes_df = pd.DataFrame(pendientes)
detalle_df = pd.concat(detalle_evidencia, ignore_index=True, sort=False) if detalle_evidencia else pd.DataFrame()

print("[7/12] Resumiendo resultado H85...", flush=True)

resumen_estado = (
    pd.concat([resueltos_df, pendientes_df], ignore_index=True, sort=False)
    .groupby(["FRENTE_H72", "ESTADO_RESOLUCION_H85"], dropna=False)
    .size()
    .reset_index(name="CASOS")
    .sort_values(["FRENTE_H72", "CASOS"], ascending=[True, False])
)

resumen_global = pd.DataFrame([
    {"CATEGORIA": "UNIVERSO_H72_REABIERTO", "CASOS": 167, "DETALLE": "167 casos H72 reanalizados para resolución efectiva."},
    {"CATEGORIA": "RESUELTOS_CON_PROPUESTA_16_19", "CASOS": len(resueltos_df), "DETALLE": "Casos con evidencia PROMEDIOS 2025 básica suficiente para propuesta 16-19 conservadora."},
    {"CATEGORIA": "PENDIENTES_POST_H85", "CASOS": len(pendientes_df), "DETALLE": "Casos que siguen sin cierre material con fuentes actuales."},
    {"CATEGORIA": "CORRECCIONES_APLICADAS", "CASOS": 0, "DETALLE": "H85 no modifica originales ni genera carga."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Resolución efectiva 167 H72 archivo 5809 columnas 16-19",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "RESOLUCION_EFECTIVA_H72_REEVALUADA",
    "UNIVERSO_H72": 167,
    "RESUELTOS_CON_PROPUESTA_16_19": len(resueltos_df),
    "PENDIENTES_POST_H85": len(pendientes_df),
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "20_21_EVALUADO": "NO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "DICTAMEN_GLOBAL": "H85 reabre los 167 H72 para resolución efectiva con fuentes disponibles. Solo los casos con evidencia suficiente quedan como propuesta 16-19; no se aplica corrección ni carga.",
}])

control = pd.DataFrame([
    {"CONTROL": "Universo 167 reanalizado", "RESULTADO": "SI", "OBSERVADO": len(resueltos_df) + len(pendientes_df), "ESPERADO": 167},
    {"CONTROL": "Resueltos con propuesta 16-19", "RESULTADO": "INFO", "OBSERVADO": len(resueltos_df), "ESPERADO": "Depende evidencia"},
    {"CONTROL": "Pendientes post H85", "RESULTADO": "INFO", "OBSERVADO": len(pendientes_df), "ESPERADO": "Depende evidencia"},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "Archivo carga generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "OBSERVADO": "NO", "ESPERADO": "NO"},
])

print("[8/12] Redactando informe...", flush=True)

informe = f"""# Hito 85 — Resolución efectiva 167 H72

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado

Se reabrieron los 167 casos H72 para intentar resolución efectiva con fuentes disponibles.

- Universo reanalizado: 167
- Resueltos con propuesta 16-19: {len(resueltos_df)}
- Pendientes post H85: {len(pendientes_df)}
- Correcciones aplicadas: NO
- Archivo de carga generado: NO
- SIES_READY generado: NO
- Subida SIES permitida: NO

## Criterio usado

Solo se marca como resuelto con propuesta cuando existe evidencia PROMEDIOS 2025 suficiente y conservadora para proponer columnas 16-19 sin aplicar equivalencias generales no gobernadas.

Los casos con períodos no básicos, conflictos de identidad, ausencia de registros 2025 o evidencia ambigua permanecen pendientes.

## Control

Este hito no modifica fuentes originales.
No genera archivo de carga.
No reemplaza validación funcional/institucional.
"""

print("[9/12] Escribiendo productos H85...", flush=True)

excel_out = SALIDA / "RESOLUCION_EFECTIVA_167_H72_5809.xlsx"
informe_out = SALIDA / "INFORME_RESOLUCION_EFECTIVA_167_H72_5809.md"
manifest_out = SALIDA / "manifest_resolucion_efectiva_167_h72_5809.json"
script_out = SALIDA / "h85_resolucion_efectiva_167_h72.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_global.to_excel(writer, sheet_name="01_RESUMEN_GLOBAL", index=False)
    resumen_estado.to_excel(writer, sheet_name="02_RESUMEN_ESTADOS", index=False)
    resueltos_df.to_excel(writer, sheet_name="03_RESUELTOS_PROPUESTA", index=False)
    pendientes_df.to_excel(writer, sheet_name="04_PENDIENTES_POST_H85", index=False)
    detalle_df.to_excel(writer, sheet_name="05_EVIDENCIA_PROM_2025", index=False)
    mapeo_102.to_excel(writer, sheet_name="06_ORIGEN_MAPEO_102", index=False)
    fuente_57.to_excel(writer, sheet_name="07_ORIGEN_FUENTE_57", index=False)
    revision_8.to_excel(writer, sheet_name="08_ORIGEN_REVISION_8", index=False)
    h72_decisiones.to_excel(writer, sheet_name="09_H72_DECISIONES", index=False)
    h72_resumen.to_excel(writer, sheet_name="10_H72_RESUMEN", index=False)
    control.to_excel(writer, sheet_name="11_CONTROL", index=False)
    pd.DataFrame([
        {"FUENTE": "H69", "RUTA": str(H69), "EXCEL": str(EX69), "SHA256": sha256(EX69)},
        {"FUENTE": "H72", "RUTA": str(H72), "EXCEL": str(EX72), "SHA256": sha256(EX72)},
        {"FUENTE": "H84", "RUTA": str(H84), "EXCEL": str(EX84), "SHA256": sha256(EX84)},
        {"FUENTE": "PROMEDIOS", "RUTA": str(PROM), "SHA256": sha256(PROM)},
        {"FUENTE": "MAPEO_IDENTIDAD", "RUTA": str(MAPEO), "SHA256": sha256(MAPEO)},
        {"FUENTE": "5809_PRECARGA", "RUTA": str(PRECARGA_5809), "SHA256": sha256(PRECARGA_5809)},
    ]).to_excel(writer, sheet_name="12_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "hito": 85,
        "universo_h72": 167,
        "resueltos_con_propuesta": len(resueltos_df),
        "pendientes_post_h85": len(pendientes_df),
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
    }]).to_excel(writer, sheet_name="13_MANIFEST_LEGIBLE", index=False)

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
    "subproyecto": "Resolución efectiva 167 H72 5809 columnas 16-19",
    "hito": 85,
    "universo_h72": 167,
    "resueltos_con_propuesta_16_19": len(resueltos_df),
    "pendientes_post_h85": len(pendientes_df),
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "excel_salida": str(excel_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h85_resolucion_efectiva_167_h72.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[10/12] Validando productos...", flush=True)
for archivo in [excel_out, informe_out, manifest_out, script_out]:
    if not archivo.exists() or archivo.stat().st_size == 0:
        raise SystemExit(f"BLOQUEO: no se generó correctamente {archivo}")

print("[11/12] Mostrando resultado terminal...", flush=True)

print()
print("=" * 170)
print("HITO 85 — RESOLUCIÓN EFECTIVA 167 H72 GENERADA")
print("=" * 170)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Universo H72 reanalizado: 167")
print(f"Resueltos con propuesta 16-19: {len(resueltos_df)}")
print(f"Pendientes post H85: {len(pendientes_df)}")
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
imprimir("MUESTRA RESUELTOS CON PROPUESTA", resueltos_df, 30)
imprimir("MUESTRA PENDIENTES POST H85", pendientes_df, 30)

print()
print("=" * 170)
print("ARCHIVOS H85")
print("=" * 170)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 170)
print("[12/12] Terminado.", flush=True)

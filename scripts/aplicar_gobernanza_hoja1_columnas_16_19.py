#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()

BASE_GOB = (
    RAIZ
    / "avance_curricular_2026"
    / "06_gobernanza_columnas_5809"
    / "GOBERNANZA_COLUMNAS_5809_20260703_231812"
)

FUENTE_5809 = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "5809_Precarga Matrícula Avance Curricular 2026.csv"
)

FUENTE_PROMEDIOS = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "PROMEDIOSDEALUMNOS_7804.xlsx"
)

FUENTE_5810 = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "5810_Precarga Carreras Avance Curricular 20268.csv"
)

FUENTE_PLANES = (
    RAIZ
    / "avance_curricular_2026"
    / "01_fuentes_institucionales"
    / "planes_estudio"
    / "Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx"
)

MATRIZ_GOB = BASE_GOB / "09_MATRIZ_MAESTRA_GOBERNANZA_5809.xlsx"
MANUAL_GOB = BASE_GOB / "10_MANUAL_GOBERNADO_5809_AVANCE_CURRICULAR_2026.md"
CATALOGO_CASOS = BASE_GOB / "11_CATALOGO_CASOS_ESPECIALES_5809.xlsx"
BLOQUEOS = BASE_GOB / "14_EXPEDIENTE_BLOQUEOS_FINAL.xlsx"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "06_gobernanza_columnas_5809"
    / f"APLICACION_GOBERNANZA_HOJA1_16_19_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIA = SALIDA / "03_AUDITORIA"
REPORTES = SALIDA / "04_REPORTES"

for carpeta in [RESULTADOS, AUDITORIA, REPORTES]:
    carpeta.mkdir(parents=True, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def detectar_csv(path):
    raw = path.read_bytes()

    for enc in ["utf-8-sig", "utf-8", "cp1252", "latin1"]:
        try:
            texto = raw.decode(enc)
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError(f"No se pudo detectar codificación: {path}")

    try:
        dialecto = csv.Sniffer().sniff(
            texto[:10000],
            delimiters=[";", ",", "\t", "|"],
        )
        delimitador = dialecto.delimiter
    except Exception:
        delimitador = ";"

    return encoding, delimitador


def norm_texto(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    return texto.strip("_")


def normalizar_rut(valor):
    texto = str(valor or "").strip().upper()
    texto = texto.replace(".", "").replace("-", "")
    texto = re.sub(r"[^0-9K]", "", texto)
    return texto


def buscar_columna(cols, candidatos):
    mapa = {norm_texto(c): c for c in cols}

    for cand in candidatos:
        cn = norm_texto(cand)
        if cn in mapa:
            return mapa[cn]

    for col in cols:
        coln = norm_texto(col)
        for cand in candidatos:
            cn = norm_texto(cand)
            if cn and cn in coln:
                return col

    return None


def leer_excel_completo_texto(path):
    xls = pd.ExcelFile(path, engine="openpyxl")
    partes = []

    for hoja in xls.sheet_names:
        try:
            df = pd.read_excel(
                path,
                sheet_name=hoja,
                dtype=str,
                keep_default_na=False,
                engine="openpyxl",
            )
        except Exception:
            continue

        partes.append(f"\n--- HOJA: {hoja} ---\n")
        partes.append(" | ".join(map(str, df.columns)))

        for _, row in df.head(5000).iterrows():
            partes.append(" | ".join(str(v) for v in row.tolist()))

    return "\n".join(partes)


def buscar_respaldo(texto, termino, ventana=350):
    termino_limpio = str(termino or "").strip()
    if not termino_limpio:
        return ""

    texto_norm = norm_texto(texto)
    termino_norm = norm_texto(termino_limpio)

    pos = texto_norm.find(termino_norm)

    if pos < 0:
        return ""

    inicio = max(pos - ventana, 0)
    fin = min(pos + ventana, len(texto_norm))

    return texto_norm[inicio:fin]


def contiene_alguno(texto, terminos):
    n = norm_texto(texto)
    return any(norm_texto(t) in n for t in terminos)


for ruta in [
    FUENTE_5809,
    FUENTE_PROMEDIOS,
    FUENTE_5810,
    MATRIZ_GOB,
    MANUAL_GOB,
    CATALOGO_CASOS,
    BLOQUEOS,
]:
    if not ruta.exists():
        raise SystemExit(f"No existe fuente requerida: {ruta}")


manual_texto = MANUAL_GOB.read_text(encoding="utf-8", errors="replace")
catalogo_texto = leer_excel_completo_texto(CATALOGO_CASOS)
bloqueos_texto = leer_excel_completo_texto(BLOQUEOS)

texto_gobernado_total = "\n".join([
    manual_texto,
    catalogo_texto,
    bloqueos_texto,
])


encoding_5809, sep_5809 = detectar_csv(FUENTE_5809)

df_5809 = pd.read_csv(
    FUENTE_5809,
    sep=sep_5809,
    encoding=encoding_5809,
    dtype=str,
    keep_default_na=False,
    header=0,
    engine="python",
)

df_5809["_DOC_NORM"] = df_5809["NUM_DOCUMENTO"].map(normalizar_rut)
df_5809["_RUT_DV_NORM"] = (
    df_5809["NUM_DOCUMENTO"].map(normalizar_rut)
    + df_5809["DV"].map(normalizar_rut)
)

df_hoja1 = pd.read_excel(
    FUENTE_PROMEDIOS,
    sheet_name="Hoja1",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

cols = list(df_hoja1.columns)

col_codcli = buscar_columna(cols, ["CODCLI", "COD_ALUMNO", "CODIGO_ALUMNO"])
col_rut = buscar_columna(cols, ["RUT", "NUM_DOCUMENTO", "DOCUMENTO"])
col_carrera = buscar_columna(cols, ["CODCARR", "CODCARPR", "COD_CARRERA", "CARRERA"])
col_ano = buscar_columna(cols, ["ANO", "ANIO", "AÑO", "PERIODO"])
col_nivel = buscar_columna(cols, ["NIVEL", "CURSO"])
col_asignatura = buscar_columna(cols, ["ASIGNATURA", "RAMO", "ACTIVIDAD", "MODULO"])
col_estado = buscar_columna(cols, ["ESTADO", "SITUACION", "SITUACION_FINAL", "ESTADO_ASIGNATURA"])

columnas_criticas = {
    "CODCLI": col_codcli,
    "RUT": col_rut,
    "CODCARR": col_carrera,
    "ANO": col_ano,
    "NIVEL": col_nivel,
    "ASIGNATURA": col_asignatura,
    "ESTADO": col_estado,
}

faltantes_hoja1 = [
    nombre for nombre, col in columnas_criticas.items()
    if not col
]

if faltantes_hoja1:
    raise SystemExit(
        "Hoja1 no contiene columnas críticas esperadas: "
        + " | ".join(faltantes_hoja1)
    )


df_hoja1["_RUT_NORM"] = df_hoja1[col_rut].map(normalizar_rut)
df_hoja1["_CODCLI_NORM"] = df_hoja1[col_codcli].astype(str).str.strip().str.upper()
df_hoja1["_ANO_NORM"] = df_hoja1[col_ano].astype(str).str.strip()
df_hoja1["_NIVEL_NUM"] = pd.to_numeric(df_hoja1[col_nivel], errors="coerce")
df_hoja1["_ESTADO_NORM"] = df_hoja1[col_estado].map(norm_texto)
df_hoja1["_ASIGNATURA_NORM"] = df_hoja1[col_asignatura].astype(str).str.strip()


# -------------------------------------------------------------------
# 1. Catálogo gobernado de ESTADO.
# -------------------------------------------------------------------

catalogo_estado = (
    df_hoja1[[col_estado, "_ESTADO_NORM"]]
    .drop_duplicates()
    .sort_values("_ESTADO_NORM")
    .copy()
)

filas_estado = []

for _, row in catalogo_estado.iterrows():
    estado_original = row[col_estado]
    estado_norm = row["_ESTADO_NORM"]

    respaldo_manual = buscar_respaldo(manual_texto, estado_original)
    respaldo_catalogo = buscar_respaldo(catalogo_texto, estado_original)
    respaldo_bloqueos = buscar_respaldo(bloqueos_texto, estado_original)

    respaldo_existe = bool(respaldo_manual or respaldo_catalogo or respaldo_bloqueos)

    cuenta_cursado = "NO_GOBERNADO"
    cuenta_aprobado = "NO_GOBERNADO"
    tipo_tratamiento = "NO_GOBERNADO_EN_ARTEFACTOS"

    if respaldo_existe:
        if contiene_alguno(estado_norm, ["APROB"]):
            cuenta_cursado = "SI"
            cuenta_aprobado = "SI"
            tipo_tratamiento = "APROBADO_SEGUN_ESTADO_GOBERNADO"
        elif contiene_alguno(estado_norm, ["REPROB", "RECHAZ", "NO_APROB"]):
            cuenta_cursado = "SI"
            cuenta_aprobado = "NO"
            tipo_tratamiento = "CURSADO_NO_APROBADO_SEGUN_ESTADO_GOBERNADO"
        elif contiene_alguno(estado_norm, ["CONVALID", "HOMOLOG", "RECONOC"]):
            cuenta_cursado = "TRATAR_SEGUN_CAMPO"
            cuenta_aprobado = "TRATAR_SEGUN_CAMPO"
            tipo_tratamiento = "HOMOLOGACION_CONVALIDACION_RECONOCIMIENTO_GOBERNADO"
        else:
            cuenta_cursado = "REVISAR_GOBERNANZA"
            cuenta_aprobado = "REVISAR_GOBERNANZA"
            tipo_tratamiento = "ESTADO_EXISTE_EN_GOBERNANZA_PERO_NO_CLASIFICADO_AUTOMATICAMENTE"

    filas_estado.append({
        "ESTADO_ORIGINAL": estado_original,
        "ESTADO_NORM": estado_norm,
        "RESPALDO_EN_MANUAL_GOBERNADO": "SI" if respaldo_manual else "NO",
        "RESPALDO_EN_CATALOGO_CASOS": "SI" if respaldo_catalogo else "NO",
        "RESPALDO_EN_EXPEDIENTE_BLOQUEOS": "SI" if respaldo_bloqueos else "NO",
        "CUENTA_COMO_CURSADO": cuenta_cursado,
        "CUENTA_COMO_APROBADO": cuenta_aprobado,
        "TIPO_TRATAMIENTO": tipo_tratamiento,
        "EVIDENCIA_MANUAL_SNIPPET_NORM": respaldo_manual[:500],
        "EVIDENCIA_CATALOGO_SNIPPET_NORM": respaldo_catalogo[:500],
    })

estado_gob_df = pd.DataFrame(filas_estado)


# -------------------------------------------------------------------
# 2. Determinar si ASIGNATURA puede operar como unidad según gobernanza.
# -------------------------------------------------------------------

respaldo_asignatura_manual = buscar_respaldo(manual_texto, "ASIGNATURA")
respaldo_asignatura_catalogo = buscar_respaldo(catalogo_texto, "ASIGNATURA")

asignatura_como_unidad = (
    bool(respaldo_asignatura_manual or respaldo_asignatura_catalogo)
    and contiene_alguno(
        texto_gobernado_total,
        ["ASIGNATURA", "UNIDAD", "UNIDADES", "CURSOS", "MODULOS", "MÓDULOS"],
    )
)

unidad_df = pd.DataFrame([{
    "ELEMENTO": "ASIGNATURA",
    "PUEDE_OPERAR_COMO_UNIDAD_SEGUN_ARTEFACTOS_GOBERNADOS": (
        "SI" if asignatura_como_unidad else "NO_GOBERNADO"
    ),
    "RESPALDO_MANUAL": "SI" if respaldo_asignatura_manual else "NO",
    "RESPALDO_CATALOGO": "SI" if respaldo_asignatura_catalogo else "NO",
    "DECISION": (
        "USAR_CONTEO_ASIGNATURAS_COMO_PRUEBA_GOBERNADA"
        if asignatura_como_unidad
        else "NO_USAR_ASIGNATURA_COMO_UNIDAD_HASTA_RESPALDO_EXPLICITO"
    ),
    "EVIDENCIA_MANUAL_SNIPPET_NORM": respaldo_asignatura_manual[:700],
    "EVIDENCIA_CATALOGO_SNIPPET_NORM": respaldo_asignatura_catalogo[:700],
}])


# -------------------------------------------------------------------
# 3. Curso 1er/2do semestre: no inventar semestre si no existe.
# -------------------------------------------------------------------

respaldo_curso_1 = buscar_respaldo(manual_texto, "CURSO_1ER_SEM")
respaldo_curso_2 = buscar_respaldo(manual_texto, "CURSO_2DO_SEM")
respaldo_nivel = buscar_respaldo(catalogo_texto, "NIVEL")

curso_df = pd.DataFrame([
    {
        "CAMPO_5809": "CURSO_1ER_SEM",
        "HOJA1_TRAE_ANO": "SI",
        "HOJA1_TRAE_NIVEL": "SI",
        "HOJA1_TRAE_SEMESTRE": "NO",
        "RESPALDO_MANUAL_CAMPO": "SI" if respaldo_curso_1 else "NO",
        "RESPALDO_CATALOGO_NIVEL": "SI" if respaldo_nivel else "NO",
        "DECISION_GOBERNADA": (
            "NO_ESCRIBIR_COMO_SEMESTRE_SIN_REGLA_EXPLICITA"
        ),
        "VALOR_TECNICO_DISPONIBLE": "NIVEL_ANUAL_2025",
        "ACCION": "PROBAR_NIVEL_ANUAL_COMO_EVIDENCIA_NO_COMO_CARGA_FINAL",
    },
    {
        "CAMPO_5809": "CURSO_2DO_SEM",
        "HOJA1_TRAE_ANO": "SI",
        "HOJA1_TRAE_NIVEL": "SI",
        "HOJA1_TRAE_SEMESTRE": "NO",
        "RESPALDO_MANUAL_CAMPO": "SI" if respaldo_curso_2 else "NO",
        "RESPALDO_CATALOGO_NIVEL": "SI" if respaldo_nivel else "NO",
        "DECISION_GOBERNADA": (
            "NO_ESCRIBIR_COMO_SEMESTRE_SIN_REGLA_EXPLICITA"
        ),
        "VALOR_TECNICO_DISPONIBLE": "NIVEL_ANUAL_2025",
        "ACCION": "PROBAR_NIVEL_ANUAL_COMO_EVIDENCIA_NO_COMO_CARGA_FINAL",
    },
])


# -------------------------------------------------------------------
# 4. Prueba gobernada con 15 RUT/CODCLI.
# -------------------------------------------------------------------

docs_hoja1 = set(df_hoja1["_RUT_NORM"])
muestra_15 = df_5809[df_5809["_DOC_NORM"].isin(docs_hoja1)].head(15).copy()

if muestra_15.empty:
    muestra_15 = df_5809.head(15).copy()
    modo_muestra = "SIN_MATCH_RUT_TOMA_PRIMEROS_15"
else:
    modo_muestra = "MATCH_RUT_HOJA1"

# Mapa estados.
map_estado = estado_gob_df.set_index("ESTADO_NORM").to_dict("index")

resultados = []

for _, alum in muestra_15.iterrows():
    doc = alum["_DOC_NORM"]

    det = df_hoja1[
        df_hoja1["_RUT_NORM"].eq(doc)
        & df_hoja1["_ANO_NORM"].astype(str).str.contains("2025", na=False)
    ].copy()

    codcli_obs = ""
    if not det.empty:
        codcli_obs = " | ".join(
            sorted(det["_CODCLI_NORM"].dropna().astype(str).unique().tolist())
        )

    # Nivel anual observado.
    nivel_anual = ""
    if det["_NIVEL_NUM"].notna().any():
        nivel_anual = int(det["_NIVEL_NUM"].max())

    det["_ESTADO_GOB_CURSADO"] = det["_ESTADO_NORM"].map(
        lambda x: map_estado.get(x, {}).get("CUENTA_COMO_CURSADO", "NO_GOBERNADO")
    )

    det["_ESTADO_GOB_APROBADO"] = det["_ESTADO_NORM"].map(
        lambda x: map_estado.get(x, {}).get("CUENTA_COMO_APROBADO", "NO_GOBERNADO")
    )

    det["_ASIGNATURA_VALIDA"] = det["_ASIGNATURA_NORM"].ne("")

    cursadas = ""
    aprobadas = ""

    if asignatura_como_unidad and not det.empty:
        cursadas = int(
            det[
                det["_ASIGNATURA_VALIDA"]
                & det["_ESTADO_GOB_CURSADO"].isin(["SI"])
            ][["_CODCLI_NORM", "_ASIGNATURA_NORM"]]
            .drop_duplicates()
            .shape[0]
        )

        aprobadas = int(
            det[
                det["_ASIGNATURA_VALIDA"]
                & det["_ESTADO_GOB_APROBADO"].isin(["SI"])
            ][["_CODCLI_NORM", "_ASIGNATURA_NORM"]]
            .drop_duplicates()
            .shape[0]
        )

    estados_no_gob = sorted(
        det.loc[
            det["_ESTADO_GOB_CURSADO"].eq("NO_GOBERNADO"),
            col_estado,
        ].astype(str).unique().tolist()
    )

    resultados.append({
        "TIPO_DOCUMENTO": alum.get("TIPO_DOCUMENTO", ""),
        "NUM_DOCUMENTO": alum.get("NUM_DOCUMENTO", ""),
        "DV": alum.get("DV", ""),
        "DOC_NORM": doc,
        "CODCLI_HOJA1_2025": codcli_obs,
        "CODIGO_UNICO_5809": alum.get("CODIGO_UNICO", ""),
        "PLAN_ESTUDIOS_5809": alum.get("PLAN_ESTUDIOS", ""),
        "REGISTROS_HOJA1_2025": len(det),
        "NIVEL_ANUAL_2025_OBSERVADO": nivel_anual,
        "CURSO_1ER_SEM_PROPUESTO": "",
        "CURSO_2DO_SEM_PROPUESTO": "",
        "MOTIVO_CURSO_NO_ESCRITO": "Hoja1 no trae semestre; no se escribe 1er/2do semestre sin regla explícita.",
        "UNIDADES_CURSADAS_PRUEBA": cursadas,
        "UNIDADES_APROBADAS_PRUEBA": aprobadas,
        "UNIDADES_ESCRIBIBLES_EN_5809": (
            "NO_FINAL_SOLO_PRUEBA"
            if asignatura_como_unidad else "NO"
        ),
        "ESTADOS_NO_GOBERNADOS_OBSERVADOS": " | ".join(estados_no_gob),
        "ESTADO_PRUEBA": (
            "PRUEBA_GOBERNADA_PARCIAL"
            if len(det) > 0 else "SIN_DATOS_HOJA1_2025"
        ),
    })

prueba_15_df = pd.DataFrame(resultados)


# -------------------------------------------------------------------
# 5. Diagnóstico final por columna 16-19.
# -------------------------------------------------------------------

diag_cols = []

for campo in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
    diag_cols.append({
        "CAMPO_5809": campo,
        "FUENTE": "PROMEDIOSDEALUMNOS_7804.xlsx / Hoja1",
        "COLUMNAS_USADAS": "RUT, CODCLI, CODCARR, ANO, NIVEL, ASIGNATURA, ESTADO",
        "DATO_DISPONIBLE": "NIVEL_ANUAL_2025",
        "DATO_FALTANTE": "SEMESTRE_O_REGLA_GOBERNADA_PARA_DERIVAR_1ER_2DO_SEM",
        "ESTADO": "BLOQUEADO_COMO_CARGA_FINAL",
        "PUEDE_PROBARSE": "SI_COMO_EVIDENCIA_ANUAL",
        "PUEDE_ESCRIBIRSE_EN_5809": "NO",
        "ACCION": "No duplicar NIVEL anual en ambos semestres sin regla explícita.",
    })

estado_unidades = (
    "PRUEBA_CONTROLADA_POSIBLE"
    if asignatura_como_unidad
    else "BLOQUEADO_HASTA_RESPALDO_UNIDAD_MEDIDA"
)

for campo in ["UNIDADES_CURSADAS", "UNIDADES_APROBADAS"]:
    diag_cols.append({
        "CAMPO_5809": campo,
        "FUENTE": "PROMEDIOSDEALUMNOS_7804.xlsx / Hoja1",
        "COLUMNAS_USADAS": "RUT, CODCLI, CODCARR, ANO, ASIGNATURA, ESTADO",
        "DATO_DISPONIBLE": "CONTEO_ASIGNATURAS_2025_SEGUN_ESTADO_GOBERNADO",
        "DATO_FALTANTE": (
            "RESPALDO_EXPLICITO_DE_UNIDAD_MEDIDA_ASIGNATURA"
            if not asignatura_como_unidad else ""
        ),
        "ESTADO": estado_unidades,
        "PUEDE_PROBARSE": "SI",
        "PUEDE_ESCRIBIRSE_EN_5809": "NO_FINAL",
        "ACCION": "Mantener como prueba controlada hasta validación integral de unidad de medida por plan.",
    })

diag_cols_df = pd.DataFrame(diag_cols)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "HOJA1_LEIDA",
        "RESULTADO": "OK",
        "DETALLE": len(df_hoja1),
    },
    {
        "VALIDACION": "ARTEFACTOS_GOBERNADOS_LEIDOS",
        "RESULTADO": "OK",
        "DETALLE": "Manual gobernado + catálogo casos + bloqueos",
    },
    {
        "VALIDACION": "ESTADOS_HOJA1_CATALOGADOS",
        "RESULTADO": "OK",
        "DETALLE": len(estado_gob_df),
    },
    {
        "VALIDACION": "ESTADOS_CON_RESPALDO_GOBERNADO",
        "RESULTADO": (
            "OK"
            if not estado_gob_df[
                estado_gob_df["TIPO_TRATAMIENTO"].eq("NO_GOBERNADO_EN_ARTEFACTOS")
            ].shape[0]
            else "REVISAR"
        ),
        "DETALLE": int(
            estado_gob_df[
                estado_gob_df["TIPO_TRATAMIENTO"].eq("NO_GOBERNADO_EN_ARTEFACTOS")
            ].shape[0]
        ),
    },
    {
        "VALIDACION": "ASIGNATURA_COMO_UNIDAD_GOBERNADA",
        "RESULTADO": "OK" if asignatura_como_unidad else "REVISAR",
        "DETALLE": unidad_df.iloc[0]["DECISION"],
    },
    {
        "VALIDACION": "CURSO_SEMESTRAL_ESCRIBIBLE",
        "RESULTADO": "NO",
        "DETALLE": "Hoja1 no trae semestre; no se escribe CURSO_1ER_SEM/CURSO_2DO_SEM.",
    },
    {
        "VALIDACION": "PRUEBA_15_GENERADA",
        "RESULTADO": "OK" if len(prueba_15_df) == 15 else "REVISAR",
        "DETALLE": f"{len(prueba_15_df)} / {modo_muestra}",
    },
    {
        "VALIDACION": "CSV_CARGA_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "SIES_READY_GENERADO",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


fuentes = pd.DataFrame([
    {"FUENTE": "PRECARGA_5809", "RUTA": str(FUENTE_5809), "SHA256": sha256(FUENTE_5809)},
    {"FUENTE": "PROMEDIOSDEALUMNOS_7804_HOJA1", "RUTA": str(FUENTE_PROMEDIOS), "SHA256": sha256(FUENTE_PROMEDIOS)},
    {"FUENTE": "PRECARGA_5810", "RUTA": str(FUENTE_5810), "SHA256": sha256(FUENTE_5810)},
    {"FUENTE": "MATRIZ_GOBERNADA", "RUTA": str(MATRIZ_GOB), "SHA256": sha256(MATRIZ_GOB)},
    {"FUENTE": "MANUAL_GOBERNADO", "RUTA": str(MANUAL_GOB), "SHA256": sha256(MANUAL_GOB)},
    {"FUENTE": "CATALOGO_CASOS", "RUTA": str(CATALOGO_CASOS), "SHA256": sha256(CATALOGO_CASOS)},
    {"FUENTE": "EXPEDIENTE_BLOQUEOS", "RUTA": str(BLOQUEOS), "SHA256": sha256(BLOQUEOS)},
])

if FUENTE_PLANES.exists():
    fuentes.loc[len(fuentes)] = {
        "FUENTE": "LISTADO_PLANES",
        "RUTA": str(FUENTE_PLANES),
        "SHA256": sha256(FUENTE_PLANES),
    }


estado_gob_df.to_csv(RESULTADOS / "01_CATALOGO_ESTADOS_HOJA1_GOBERNADO.tsv", sep="\t", index=False)
unidad_df.to_csv(RESULTADOS / "02_GOBERNANZA_ASIGNATURA_COMO_UNIDAD.tsv", sep="\t", index=False)
curso_df.to_csv(RESULTADOS / "03_GOBERNANZA_CURSO_SEMESTRAL.tsv", sep="\t", index=False)
prueba_15_df.to_csv(RESULTADOS / "04_PRUEBA_GOBERNADA_15_RUT_CODCLI.tsv", sep="\t", index=False)
diag_cols_df.to_csv(RESULTADOS / "05_DIAGNOSTICO_GOBERNADO_COLUMNAS_16_19.tsv", sep="\t", index=False)
validaciones.to_csv(RESULTADOS / "06_VALIDACIONES_GOBERNANZA_HOJA1_16_19.tsv", sep="\t", index=False)
fuentes.to_csv(AUDITORIA / "FUENTES_GOBERNANZA_HOJA1_16_19.tsv", sep="\t", index=False)


excel = RESULTADOS / "APLICACION_GOBERNANZA_HOJA1_16_19.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    diag_cols_df.to_excel(writer, sheet_name="DIAGNOSTICO_16_19", index=False)
    estado_gob_df.to_excel(writer, sheet_name="ESTADOS_HOJA1", index=False)
    unidad_df.to_excel(writer, sheet_name="ASIGNATURA_UNIDAD", index=False)
    curso_df.to_excel(writer, sheet_name="CURSO_SEMESTRAL", index=False)
    prueba_15_df.to_excel(writer, sheet_name="PRUEBA_15", index=False)
    validaciones.to_excel(writer, sheet_name="VALIDACIONES", index=False)
    fuentes.to_excel(writer, sheet_name="FUENTES", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 70)


if (
    validaciones.loc[
        validaciones["VALIDACION"].eq("ESTADOS_CON_RESPALDO_GOBERNADO"),
        "RESULTADO",
    ].iloc[0] == "OK"
    and asignatura_como_unidad
):
    estado_final = "HOJA1_GOBERNADA_PARA_PRUEBA_UNIDADES_ANUALES"
else:
    estado_final = "HOJA1_GOBERNADA_PARCIAL_CON_BLOQUEOS"


informe = REPORTES / "INFORME_APLICACION_GOBERNANZA_HOJA1_16_19.md"

informe.write_text(
f"""# Aplicación de gobernanza sobre Hoja1 — columnas 16-19

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

## Estado

**{estado_final}**

## Corrección metodológica

Esta fase no busca columnas literales llamadas semestre, unidades o convalidación.  
Aplica los artefactos gobernados ya construidos sobre `Hoja1`.

## Resultado

- `CURSO_1ER_SEM` y `CURSO_2DO_SEM`: no se escriben como carga final porque `Hoja1` no trae semestre explícito ni regla gobernada para dividir NIVEL anual en ambos semestres.
- `UNIDADES_CURSADAS` y `UNIDADES_APROBADAS`: se prueban mediante conteo de asignaturas 2025 según ESTADO gobernado, solo si ASIGNATURA está respaldada como unidad de medida.
- No se genera CSV.
- No se genera SIES_READY.
- No se modifican fuentes originales.

## Archivos

- Excel: `{excel}`
- Carpeta: `{SALIDA}`
""",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_aplicacion_gobernanza_hoja1_16_19.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "estado_final": estado_final,
            "fuente": str(FUENTE_PROMEDIOS),
            "hoja": "Hoja1",
            "prueba_15": len(prueba_15_df),
            "csv_carga_generado": False,
            "sies_ready_generado": False,
            "fuentes_originales_modificadas": False,
            "excel": str(excel),
            "informe": str(informe),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 120)
print("APLICACIÓN DE GOBERNANZA SOBRE HOJA1 — COLUMNAS 16-19")
print("=" * 120)
print(f"Estado final: {estado_final}")
print(f"Registros Hoja1: {len(df_hoja1)}")
print(f"Prueba 15: {len(prueba_15_df)} / {modo_muestra}")
print("CSV de carga generado: NO")
print("SIES_READY generado: NO")
print("Fuentes originales modificadas: NO")
print()
print("COLUMNAS HOJA1 USADAS")
print("-" * 120)
print(f"CODCLI: {col_codcli}")
print(f"RUT: {col_rut}")
print(f"CODCARR: {col_carrera}")
print(f"ANO: {col_ano}")
print(f"NIVEL: {col_nivel}")
print(f"ASIGNATURA: {col_asignatura}")
print(f"ESTADO: {col_estado}")
print()
print("DIAGNÓSTICO COLUMNAS 16-19")
print("-" * 120)
print(diag_cols_df.to_string(index=False))
print()
print("CATÁLOGO ESTADO HOJA1")
print("-" * 120)
print(
    estado_gob_df[
        [
            "ESTADO_ORIGINAL",
            "CUENTA_COMO_CURSADO",
            "CUENTA_COMO_APROBADO",
            "TIPO_TRATAMIENTO",
            "RESPALDO_EN_MANUAL_GOBERNADO",
            "RESPALDO_EN_CATALOGO_CASOS",
        ]
    ].to_string(index=False)
)
print()
print("PRUEBA 15")
print("-" * 120)
print(prueba_15_df.to_string(index=False))
print()
print("VALIDACIONES")
print("-" * 120)
print(validaciones.to_string(index=False))
print()
print("=" * 120)
print("ARCHIVOS GENERADOS")
print("=" * 120)
print(f"Excel: {excel}")
print(f"Informe: {informe}")
print(f"Carpeta: {SALIDA}")
print("=" * 120)

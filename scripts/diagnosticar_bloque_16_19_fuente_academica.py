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

MATRIZ = BASE_GOB / "09_MATRIZ_MAESTRA_GOBERNANZA_5809.xlsx"
MANUAL = BASE_GOB / "10_MANUAL_GOBERNADO_5809_AVANCE_CURRICULAR_2026.md"
CATALOGO_CASOS = BASE_GOB / "11_CATALOGO_CASOS_ESPECIALES_5809.xlsx"
BLOQUEOS = BASE_GOB / "14_EXPEDIENTE_BLOQUEOS_FINAL.xlsx"

FUENTE_5809 = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "5809_Precarga Matrícula Avance Curricular 2026.csv"
)

FUENTE_ACADEMICA = (
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

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "06_gobernanza_columnas_5809"
    / f"DIAGNOSTICO_BLOQUE_16_19_FUENTE_ACADEMICA_{timestamp}"
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


def normalizar_doc(valor):
    texto = str(valor or "").strip().upper()
    texto = texto.replace(".", "").replace("-", "")
    texto = re.sub(r"[^0-9K]", "", texto)
    return texto


def buscar_columna(cols, candidatos):
    norm_map = {norm_texto(c): c for c in cols}
    for cand in candidatos:
        cand_norm = norm_texto(cand)
        if cand_norm in norm_map:
            return norm_map[cand_norm]
    return None


def clasificar_columna(nombre):
    n = norm_texto(nombre)

    grupos = []

    if any(t in n for t in ["CODCLI", "COD_ALUM", "CODIGO_ALUM", "CLIENTE"]):
        grupos.append("CODCLI")

    if any(t in n for t in ["RUT", "NUM_DOCUMENTO", "DOCUMENTO", "DNI", "PASAPORTE"]):
        grupos.append("DOCUMENTO")

    if any(t in n for t in ["CODIGO_UNICO", "COD_UNICO"]):
        grupos.append("CODIGO_UNICO")

    if any(t in n for t in ["CODCARR", "COD_CARR", "CARRERA", "CODCARPR", "PLAN"]):
        grupos.append("CARRERA_PLAN")

    if any(t in n for t in ["ANIO", "ANO", "AÑO", "PERIODO", "SEMESTRE", "SEM"]):
        grupos.append("PERIODO")

    if any(t in n for t in ["NIVEL", "CURSO"]):
        grupos.append("CURSO_NIVEL")

    if any(t in n for t in ["CREDIT", "UNIDAD", "HORAS", "ASIGNATURA", "RAMO"]):
        grupos.append("UNIDADES_ASIGNATURA")

    if any(t in n for t in ["APROB", "ESTADO", "SITUACION", "NOTA"]):
        grupos.append("APROBACION_ESTADO")

    if any(t in n for t in ["CONVALID", "HOMOLOG", "RECONOC"]):
        grupos.append("CONVALIDACION")

    return " | ".join(grupos) if grupos else "OTRA"


for path in [MATRIZ, MANUAL, CATALOGO_CASOS, BLOQUEOS, FUENTE_5809, FUENTE_ACADEMICA, FUENTE_5810]:
    if not path.exists():
        raise SystemExit(f"No existe fuente requerida: {path}")


encoding_5809, delimitador_5809 = detectar_csv(FUENTE_5809)

df_5809 = pd.read_csv(
    FUENTE_5809,
    sep=delimitador_5809,
    encoding=encoding_5809,
    dtype=str,
    keep_default_na=False,
    header=0,
    engine="python",
)

campos_bloque = [
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
]

faltan = [c for c in campos_bloque if c not in df_5809.columns]
if faltan:
    raise SystemExit(
        "Faltan columnas 16-19 en 5809: "
        + " | ".join(faltan)
    )


# -------------------------------------------------------------------
# 1. Leer matriz gobernada.
# -------------------------------------------------------------------

xls_matriz = pd.ExcelFile(MATRIZ, engine="openpyxl")
hoja_matriz = xls_matriz.sheet_names[0]

for posible in [
    "MATRIZ_MAESTRA",
    "MATRIZ_5809",
    "GOBERNANZA_5809",
    "MATRIZ",
]:
    if posible in xls_matriz.sheet_names:
        hoja_matriz = posible
        break

matriz = pd.read_excel(
    MATRIZ,
    sheet_name=hoja_matriz,
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

campo_col = None
estado_col = None
tipo_col = None
bloqueo_col = None

for c in matriz.columns:
    cu = c.upper()
    if cu in ["CAMPO_5809", "CAMPO", "NOMBRE_COLUMNA", "COLUMNA"]:
        campo_col = c
    if cu in ["ESTADO_COLUMNA", "ESTADO"]:
        estado_col = c
    if cu in ["TIPO_CAMPO", "TIPO"]:
        tipo_col = c
    if cu in ["BLOQUEO", "BLOQUEO_COLUMNA"]:
        bloqueo_col = c

if campo_col is None:
    raise SystemExit("No se encontró columna campo en matriz maestra.")

matriz_bloque = matriz[
    matriz[campo_col].astype(str).isin(campos_bloque)
].copy()


# -------------------------------------------------------------------
# 2. Inventariar fuente académica.
# -------------------------------------------------------------------

xls_acad = pd.ExcelFile(FUENTE_ACADEMICA, engine="openpyxl")

inventario = []
candidatas = []

for hoja in xls_acad.sheet_names:
    try:
        dfh = pd.read_excel(
            FUENTE_ACADEMICA,
            sheet_name=hoja,
            dtype=str,
            keep_default_na=False,
            engine="openpyxl",
        )
    except Exception as exc:
        inventario.append({
            "HOJA": hoja,
            "FILAS": "",
            "COLUMNAS": "",
            "ERROR": str(exc),
        })
        continue

    columnas = list(dfh.columns)
    columnas_norm = [norm_texto(c) for c in columnas]

    grupos = {}
    for c in columnas:
        tipo = clasificar_columna(c)
        grupos.setdefault(tipo, []).append(c)

    score = 0
    score += 3 if any("CODCLI" in clasificar_columna(c) for c in columnas) else 0
    score += 2 if any("DOCUMENTO" in clasificar_columna(c) for c in columnas) else 0
    score += 2 if any("PERIODO" in clasificar_columna(c) for c in columnas) else 0
    score += 2 if any("CURSO_NIVEL" in clasificar_columna(c) for c in columnas) else 0
    score += 2 if any("UNIDADES_ASIGNATURA" in clasificar_columna(c) for c in columnas) else 0
    score += 2 if any("APROBACION_ESTADO" in clasificar_columna(c) for c in columnas) else 0

    inventario.append({
        "HOJA": hoja,
        "FILAS": len(dfh),
        "COLUMNAS": len(dfh.columns),
        "SCORE_UTILIDAD": score,
        "COLUMNAS_CODCLI": " | ".join(grupos.get("CODCLI", [])),
        "COLUMNAS_DOCUMENTO": " | ".join(grupos.get("DOCUMENTO", [])),
        "COLUMNAS_PERIODO": " | ".join(grupos.get("PERIODO", [])),
        "COLUMNAS_CURSO_NIVEL": " | ".join(grupos.get("CURSO_NIVEL", [])),
        "COLUMNAS_UNIDADES": " | ".join(grupos.get("UNIDADES_ASIGNATURA", [])),
        "COLUMNAS_ESTADO_APROBACION": " | ".join(grupos.get("APROBACION_ESTADO", [])),
        "COLUMNAS_CONVALIDACION": " | ".join(grupos.get("CONVALIDACION", [])),
        "ERROR": "",
    })

    for c in columnas:
        tipo = clasificar_columna(c)
        if tipo != "OTRA":
            muestra = " | ".join(
                dfh[c].astype(str).head(10).tolist()
            )
            candidatas.append({
                "HOJA": hoja,
                "COLUMNA": c,
                "TIPO_DETECTADO": tipo,
                "NO_VACIOS": int(dfh[c].astype(str).str.strip().ne("").sum()),
                "VALORES_UNICOS": int(dfh[c].astype(str).nunique(dropna=False)),
                "MUESTRA": muestra,
            })

inventario_df = pd.DataFrame(inventario).sort_values(
    ["SCORE_UTILIDAD", "FILAS"],
    ascending=False,
)

candidatas_df = pd.DataFrame(candidatas)


# -------------------------------------------------------------------
# 3. Seleccionar hoja candidata principal.
# -------------------------------------------------------------------

hoja_principal = None

if "DatosAlumnos" in xls_acad.sheet_names:
    hoja_principal = "DatosAlumnos"
elif not inventario_df.empty:
    hoja_principal = inventario_df.iloc[0]["HOJA"]

if not hoja_principal:
    raise SystemExit("No se pudo seleccionar hoja candidata principal.")

df_acad = pd.read_excel(
    FUENTE_ACADEMICA,
    sheet_name=hoja_principal,
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

cols = list(df_acad.columns)

col_codcli = buscar_columna(cols, ["CODCLI", "COD_ALUMNO", "CODIGO_ALUMNO"])
col_rut = buscar_columna(cols, ["RUT", "NUM_DOCUMENTO", "DOCUMENTO"])
col_dv = buscar_columna(cols, ["DV"])
col_codigo_unico = buscar_columna(cols, ["CODIGO_UNICO"])
col_carrera = buscar_columna(cols, ["CODCARR", "COD_CARRERA", "CODCARPR", "CARRERA"])
col_anio = buscar_columna(cols, ["ANIO", "AÑO", "ANO", "PERIODO_ANIO"])
col_sem = buscar_columna(cols, ["SEMESTRE", "SEM", "PERIODO_SEM"])
col_nivel = buscar_columna(cols, ["NIVEL", "CURSO", "CURSO_NIVEL"])
col_unidades = buscar_columna(cols, ["UNIDADES", "CREDITOS", "CREDITOS_ASIGNATURA", "HORAS"])
col_estado = buscar_columna(cols, ["ESTADO", "ESTADO_ASIGNATURA", "SITUACION", "SITUACION_FINAL"])
col_aprob = buscar_columna(cols, ["APROBADA", "APROBACION", "APRUEBA"])
col_conval = buscar_columna(cols, ["CONVALIDACION", "CONVALIDADA", "HOMOLOGACION", "RECONOCIMIENTO"])


# -------------------------------------------------------------------
# 4. Cobertura preliminar contra 5809.
# -------------------------------------------------------------------

df_5809["_DOC_NORM"] = df_5809["NUM_DOCUMENTO"].map(normalizar_doc)

cobertura = []

if col_rut:
    df_acad["_DOC_NORM"] = df_acad[col_rut].map(normalizar_doc)
    docs_acad = set(df_acad["_DOC_NORM"])
    df_5809["_MATCH_DOC_ACAD"] = df_5809["_DOC_NORM"].isin(docs_acad)

    cobertura.append({
        "LLAVE": "NUM_DOCUMENTO/RUT",
        "COLUMNA_FUENTE": col_rut,
        "REGISTROS_5809_CUBIERTOS": int(df_5809["_MATCH_DOC_ACAD"].sum()),
        "REGISTROS_5809_TOTAL": len(df_5809),
        "COBERTURA_PCT": round(float(df_5809["_MATCH_DOC_ACAD"].mean()) * 100, 2),
    })

if col_codigo_unico:
    cod_acad = set(df_acad[col_codigo_unico].astype(str).str.strip())
    df_5809["_MATCH_CODIGO_UNICO_ACAD"] = (
        df_5809["CODIGO_UNICO"].astype(str).str.strip().isin(cod_acad)
    )

    cobertura.append({
        "LLAVE": "CODIGO_UNICO",
        "COLUMNA_FUENTE": col_codigo_unico,
        "REGISTROS_5809_CUBIERTOS": int(df_5809["_MATCH_CODIGO_UNICO_ACAD"].sum()),
        "REGISTROS_5809_TOTAL": len(df_5809),
        "COBERTURA_PCT": round(float(df_5809["_MATCH_CODIGO_UNICO_ACAD"].mean()) * 100, 2),
    })

if col_codcli:
    cobertura.append({
        "LLAVE": "CODCLI",
        "COLUMNA_FUENTE": col_codcli,
        "REGISTROS_5809_CUBIERTOS": "NO_EVALUADO_DIRECTO",
        "REGISTROS_5809_TOTAL": len(df_5809),
        "COBERTURA_PCT": "REQUIERE_MAPEO_DOCUMENTO_A_CODCLI",
    })

cobertura_df = pd.DataFrame(cobertura)


# -------------------------------------------------------------------
# 5. Diagnóstico por campo 16-19.
# -------------------------------------------------------------------

diagnostico = []

for orden, campo in enumerate(campos_bloque, start=16):
    serie = df_5809[campo].astype(str)
    vacios = int(serie.str.strip().eq("").sum())
    no_vacios = int(serie.str.strip().ne("").sum())

    fila_gob = matriz_bloque[
        matriz_bloque[campo_col].astype(str).eq(campo)
    ]

    if fila_gob.empty:
        estado_gob = "NO_ENCONTRADO_EN_MATRIZ"
        tipo_gob = ""
        bloqueo_gob = "REVISAR"
    else:
        r = fila_gob.iloc[0]
        estado_gob = r.get(estado_col, "") if estado_col else ""
        tipo_gob = r.get(tipo_col, "") if tipo_col else ""
        bloqueo_gob = r.get(bloqueo_col, "") if bloqueo_col else ""

    if campo in ["CURSO_1ER_SEM", "CURSO_2DO_SEM"]:
        fuente_minima = "nivel/curso + año/semestre + trayectoria"
        columnas_minimas_ok = bool(col_nivel and (col_anio or col_sem))
        columnas_detectadas = {
            "CURSO_NIVEL": col_nivel or "",
            "ANIO": col_anio or "",
            "SEMESTRE": col_sem or "",
        }
    else:
        fuente_minima = "unidades/créditos + estado aprobación + año 2025 + trayectoria"
        columnas_minimas_ok = bool(col_unidades and (col_estado or col_aprob) and (col_anio or col_sem))
        columnas_detectadas = {
            "UNIDADES": col_unidades or "",
            "ESTADO_APROBACION": col_estado or col_aprob or "",
            "ANIO": col_anio or "",
            "SEMESTRE": col_sem or "",
            "CONVALIDACION": col_conval or "",
        }

    if vacios == len(df_5809) and columnas_minimas_ok:
        estado_factibilidad = "FUENTE_CANDIDATA_DETECTADA_REQUIERE_PRUEBA_CALCULO"
        accion = "NO_COMPLETAR_TODAVIA_PROBAR_LOGICA_EN_MUESTRA"
        bloqueo = "PARCIAL"
    elif vacios == len(df_5809):
        estado_factibilidad = "BLOQUEADO_FUENTE_INSUFICIENTE"
        accion = "NO_COMPLETAR_SOLICITAR_FUENTE_O_REGLA"
        bloqueo = "SI"
    else:
        estado_factibilidad = "PRECARGA_TRAE_VALORES_REVISAR"
        accion = "VALIDAR_VALORES_EXISTENTES"
        bloqueo = "REVISAR"

    diagnostico.append({
        "ORDEN_COLUMNA": orden,
        "CAMPO_5809": campo,
        "ESTADO_GOBERNANZA": estado_gob,
        "TIPO_CAMPO": tipo_gob,
        "BLOQUEO_GOBERNANZA": bloqueo_gob,
        "REGISTROS_TOTAL": len(df_5809),
        "NO_VACIOS_PRECARGA": no_vacios,
        "VACIOS_PRECARGA": vacios,
        "FUENTE_CANDIDATA": str(FUENTE_ACADEMICA),
        "HOJA_CANDIDATA": hoja_principal,
        "FUENTE_MINIMA_REQUERIDA": fuente_minima,
        "COLUMNAS_DETECTADAS": json.dumps(columnas_detectadas, ensure_ascii=False),
        "COLUMNAS_MINIMAS_DETECTADAS": "SI" if columnas_minimas_ok else "NO",
        "ESTADO_FACTIBILIDAD": estado_factibilidad,
        "ACCION_SIGUIENTE": accion,
        "BLOQUEA_ARCHIVO_FINAL": bloqueo,
    })

diagnostico_df = pd.DataFrame(diagnostico)


# -------------------------------------------------------------------
# 6. Muestra de registros para siguiente prueba.
# -------------------------------------------------------------------

muestra_5809 = df_5809.head(50).copy()

if col_rut and "_DOC_NORM" in df_acad.columns:
    muestra_cruce = muestra_5809.merge(
        df_acad.head(5000),
        left_on="_DOC_NORM",
        right_on="_DOC_NORM",
        how="left",
        suffixes=("_5809", "_ACAD"),
    )
else:
    muestra_cruce = pd.DataFrame()


# -------------------------------------------------------------------
# 7. Validaciones.
# -------------------------------------------------------------------

validaciones = []

validaciones.append({
    "VALIDACION": "REGISTROS_5809",
    "RESULTADO": "OK" if len(df_5809) == 2371 else "REVISAR",
    "DETALLE": len(df_5809),
})

validaciones.append({
    "VALIDACION": "COLUMNAS_16_19_EXISTEN",
    "RESULTADO": "OK" if not faltan else "ERROR",
    "DETALLE": " | ".join(campos_bloque),
})

validaciones.append({
    "VALIDACION": "COLUMNAS_16_19_VACIAS_EN_PRECARGA",
    "RESULTADO": (
        "OK"
        if all(df_5809[c].astype(str).str.strip().eq("").all() for c in campos_bloque)
        else "REVISAR"
    ),
    "DETALLE": "La precarga no alimenta estos campos; requieren fuente académica.",
})

validaciones.append({
    "VALIDACION": "FUENTE_ACADEMICA_LEIDA",
    "RESULTADO": "OK",
    "DETALLE": f"{FUENTE_ACADEMICA.name} / hoja candidata: {hoja_principal}",
})

validaciones.append({
    "VALIDACION": "LLAVE_DOCUMENTO_DETECTADA_EN_FUENTE_ACADEMICA",
    "RESULTADO": "OK" if col_rut else "REVISAR",
    "DETALLE": col_rut or "NO_DETECTADA",
})

validaciones.append({
    "VALIDACION": "CODCLI_DETECTADO_EN_FUENTE_ACADEMICA",
    "RESULTADO": "OK" if col_codcli else "REVISAR",
    "DETALLE": col_codcli or "NO_DETECTADO",
})

validaciones.append({
    "VALIDACION": "CURSO_NIVEL_DETECTADO",
    "RESULTADO": "OK" if col_nivel else "REVISAR",
    "DETALLE": col_nivel or "NO_DETECTADO",
})

validaciones.append({
    "VALIDACION": "UNIDADES_DETECTADAS",
    "RESULTADO": "OK" if col_unidades else "REVISAR",
    "DETALLE": col_unidades or "NO_DETECTADO",
})

validaciones.append({
    "VALIDACION": "ESTADO_APROBACION_DETECTADO",
    "RESULTADO": "OK" if (col_estado or col_aprob) else "REVISAR",
    "DETALLE": col_estado or col_aprob or "NO_DETECTADO",
})

validaciones.append({
    "VALIDACION": "PERIODO_DETECTADO",
    "RESULTADO": "OK" if (col_anio or col_sem) else "REVISAR",
    "DETALLE": f"ANIO={col_anio or ''}; SEM={col_sem or ''}",
})

validaciones.append({
    "VALIDACION": "CONVALIDACION_DETECTADA",
    "RESULTADO": "INFORMATIVO" if col_conval else "NO_DETECTADO",
    "DETALLE": col_conval or "",
})

validaciones.append({
    "VALIDACION": "CSV_CARGA_GENERADO",
    "RESULTADO": "OK",
    "DETALLE": "NO",
})

validaciones.append({
    "VALIDACION": "SIES_READY_GENERADO",
    "RESULTADO": "OK",
    "DETALLE": "NO",
})

validaciones.append({
    "VALIDACION": "FUENTES_ORIGINALES_MODIFICADAS",
    "RESULTADO": "OK",
    "DETALLE": "NO",
})

validaciones_df = pd.DataFrame(validaciones)


# -------------------------------------------------------------------
# 8. Fuentes y salidas.
# -------------------------------------------------------------------

fuentes_lista = [
    ("PRECARGA_5809", FUENTE_5809),
    ("PRECARGA_5810", FUENTE_5810),
    ("FUENTE_ACADEMICA_PROMEDIOS", FUENTE_ACADEMICA),
    ("MATRIZ_MAESTRA_GOBERNANZA_5809", MATRIZ),
    ("MANUAL_GOBERNADO_5809", MANUAL),
    ("CATALOGO_CASOS_ESPECIALES_5809", CATALOGO_CASOS),
    ("EXPEDIENTE_BLOQUEOS_FINAL", BLOQUEOS),
]

if FUENTE_PLANES.exists():
    fuentes_lista.append(("LISTADO_PLANES", FUENTE_PLANES))

fuentes = pd.DataFrame([
    {
        "FUENTE": nombre,
        "RUTA": str(ruta),
        "SHA256": sha256(ruta),
    }
    for nombre, ruta in fuentes_lista
])


diagnostico_df.to_csv(
    RESULTADOS / "DIAGNOSTICO_BLOQUE_16_19.tsv",
    sep="\t",
    index=False,
)

inventario_df.to_csv(
    RESULTADOS / "INVENTARIO_FUENTE_ACADEMICA.xlsx.tsv",
    sep="\t",
    index=False,
)

candidatas_df.to_csv(
    RESULTADOS / "COLUMNAS_CANDIDATAS_FUENTE_ACADEMICA.tsv",
    sep="\t",
    index=False,
)

cobertura_df.to_csv(
    RESULTADOS / "COBERTURA_LLAVES_5809_FUENTE_ACADEMICA.tsv",
    sep="\t",
    index=False,
)

validaciones_df.to_csv(
    RESULTADOS / "VALIDACIONES_BLOQUE_16_19.tsv",
    sep="\t",
    index=False,
)

fuentes.to_csv(
    AUDITORIA / "FUENTES_BLOQUE_16_19.tsv",
    sep="\t",
    index=False,
)

if not muestra_cruce.empty:
    muestra_cruce.head(5000).to_csv(
        RESULTADOS / "MUESTRA_CRUCE_5809_FUENTE_ACADEMICA.tsv",
        sep="\t",
        index=False,
    )


excel = RESULTADOS / "DIAGNOSTICO_BLOQUE_16_19_FUENTE_ACADEMICA.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    diagnostico_df.to_excel(writer, sheet_name="DIAGNOSTICO", index=False)
    validaciones_df.to_excel(writer, sheet_name="VALIDACIONES", index=False)
    inventario_df.to_excel(writer, sheet_name="INVENTARIO_ACADEMICO", index=False)
    candidatas_df.to_excel(writer, sheet_name="COLUMNAS_CANDIDATAS", index=False)
    cobertura_df.to_excel(writer, sheet_name="COBERTURA_LLAVES", index=False)
    matriz_bloque.to_excel(writer, sheet_name="MATRIZ_GOBERNADA", index=False)
    fuentes.to_excel(writer, sheet_name="FUENTES", index=False)

    if not muestra_cruce.empty:
        muestra_cruce.head(2000).to_excel(writer, sheet_name="MUESTRA_CRUCE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 70)


if diagnostico_df["BLOQUEA_ARCHIVO_FINAL"].eq("SI").any():
    estado_bloque = "BLOQUEADO_FUENTE_INSUFICIENTE"
elif diagnostico_df["BLOQUEA_ARCHIVO_FINAL"].eq("PARCIAL").any():
    estado_bloque = "FUENTE_CANDIDATA_DETECTADA_REQUIERE_PRUEBA"
else:
    estado_bloque = "REVISAR"


informe = REPORTES / "INFORME_DIAGNOSTICO_BLOQUE_16_19_FUENTE_ACADEMICA.md"

informe.write_text(
f"""# Diagnóstico Bloque 16-19 — Fuente académica

## Contexto

Proceso: Avance Curricular SIES 2026  
Subproyecto: Matrícula 5809  
Año de referencia: 2025  

Columnas revisadas:

16. CURSO_1ER_SEM  
17. CURSO_2DO_SEM  
18. UNIDADES_CURSADAS  
19. UNIDADES_APROBADAS  

## Resultado

Estado del bloque: **{estado_bloque}**

La precarga 5809 trae estas columnas vacías, por lo que no se conservan como dato completo.  
A diferencia de las columnas 1-15, estas columnas requieren construcción desde fuente académica, trayectoria, período 2025 y validación funcional.

## Fuente académica candidata

Fuente: `{FUENTE_ACADEMICA}`  
Hoja candidata: `{hoja_principal}`

Columnas detectadas:

- CODCLI: `{col_codcli or 'NO_DETECTADO'}`
- Documento/RUT: `{col_rut or 'NO_DETECTADO'}`
- Código único: `{col_codigo_unico or 'NO_DETECTADO'}`
- Carrera/plan: `{col_carrera or 'NO_DETECTADO'}`
- Año: `{col_anio or 'NO_DETECTADO'}`
- Semestre: `{col_sem or 'NO_DETECTADO'}`
- Nivel/curso: `{col_nivel or 'NO_DETECTADO'}`
- Unidades/créditos: `{col_unidades or 'NO_DETECTADO'}`
- Estado/aprobación: `{col_estado or col_aprob or 'NO_DETECTADO'}`
- Convalidación: `{col_conval or 'NO_DETECTADO'}`

## Diagnóstico por columna

{diagnostico_df.to_markdown(index=False)}

## Validaciones

{validaciones_df.to_markdown(index=False)}

## Conclusión

Esta fase no completa valores.  
Solo confirma si existe fuente candidata para probar la construcción de las columnas 16-19.  
Si el estado queda como `FUENTE_CANDIDATA_DETECTADA_REQUIERE_PRUEBA`, la siguiente fase debe ejecutar una prueba controlada de cálculo sobre una muestra, sin generar archivo de carga.

## Archivos

- Excel: `{excel}`
- Carpeta: `{SALIDA}`
""",
    encoding="utf-8",
)


manifest = SALIDA / "manifest_diagnostico_bloque_16_19.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "anio_referencia": 2025,
            "bloque": "16-19",
            "columnas": campos_bloque,
            "estado_bloque": estado_bloque,
            "registros_5809": len(df_5809),
            "fuente_academica": str(FUENTE_ACADEMICA),
            "hoja_academica_candidata": hoja_principal,
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
print("DIAGNÓSTICO BLOQUE 16-19 — FUENTE ACADÉMICA")
print("=" * 120)
print(f"Registros 5809: {len(df_5809)}")
print(f"Fuente académica: {FUENTE_ACADEMICA}")
print(f"Hoja candidata: {hoja_principal}")
print(f"Estado bloque: {estado_bloque}")
print("CSV de carga generado: NO")
print("SIES_READY generado: NO")
print("Fuentes originales modificadas: NO")
print()
print("COLUMNAS DETECTADAS EN FUENTE CANDIDATA")
print("-" * 120)
print(f"CODCLI: {col_codcli or 'NO_DETECTADO'}")
print(f"Documento/RUT: {col_rut or 'NO_DETECTADO'}")
print(f"Código único: {col_codigo_unico or 'NO_DETECTADO'}")
print(f"Carrera/plan: {col_carrera or 'NO_DETECTADO'}")
print(f"Año: {col_anio or 'NO_DETECTADO'}")
print(f"Semestre: {col_sem or 'NO_DETECTADO'}")
print(f"Nivel/curso: {col_nivel or 'NO_DETECTADO'}")
print(f"Unidades/créditos: {col_unidades or 'NO_DETECTADO'}")
print(f"Estado/aprobación: {col_estado or col_aprob or 'NO_DETECTADO'}")
print(f"Convalidación: {col_conval or 'NO_DETECTADO'}")
print()
print("DIAGNÓSTICO POR COLUMNA")
print("-" * 120)
print(
    diagnostico_df[
        [
            "ORDEN_COLUMNA",
            "CAMPO_5809",
            "ESTADO_GOBERNANZA",
            "VACIOS_PRECARGA",
            "COLUMNAS_MINIMAS_DETECTADAS",
            "ESTADO_FACTIBILIDAD",
            "ACCION_SIGUIENTE",
            "BLOQUEA_ARCHIVO_FINAL",
        ]
    ].to_string(index=False)
)
print()
print("COBERTURA DE LLAVES")
print("-" * 120)
if cobertura_df.empty:
    print("No se pudo evaluar cobertura de llaves.")
else:
    print(cobertura_df.to_string(index=False))
print()
print("VALIDACIONES")
print("-" * 120)
print(validaciones_df.to_string(index=False))
print()
print("=" * 120)
print("ARCHIVOS GENERADOS")
print("=" * 120)
print(f"Excel: {excel}")
print(f"Informe: {informe}")
print(f"Carpeta: {SALIDA}")
print("=" * 120)

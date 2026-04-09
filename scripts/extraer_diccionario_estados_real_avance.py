#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import pandas as pd
import re
import json
import hashlib

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()

CANDIDATOS = [
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/CONFIRMACION_GOBERNANZA_PROMEDIOSALUMNOS_20260701_165732/06_RESULTADOS/CONFIRMACION_GOBERNANZA_PROMEDIOSALUMNOS.xlsx",
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/GOBERNANZA_AVANCE_CURRICULAR_2026_20260701_234932/02_RESULTADOS/GOBERNANZA_AVANCE_CURRICULAR_END_TO_END.xlsx",
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/RECALCULO_NIVELES_2371_CORREGIDO_20260702_001635/02_RESULTADOS/RECALCULO_NIVELES_2371_CORREGIDO.xlsx",
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/EXPEDIENTE_REVISION_644_20260702_012504/02_RESULTADOS/EXPEDIENTE_REVISION_644_PENDIENTES.xlsx",
    RAIZ / "avance_curricular_2026/06_gobernanza_columnas_5809/GOBERNANZA_COLUMNAS_5809_20260703_231812/BLOQUE_04_20260703_231812/BLOQUE_04_RESULTADO.xlsx",
    RAIZ / "avance_curricular_2026/06_gobernanza_columnas_5809/GOBERNANZA_COLUMNAS_5809_20260703_231812/BLOQUE_05_20260703_231812/BLOQUE_05_RESULTADO.xlsx",
]

PROMEDIOS = (
    RAIZ
    / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/PROMEDIOSDEALUMNOS_7804.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/06_gobernanza_columnas_5809"
    / f"EXTRACCION_DICCIONARIO_ESTADOS_REAL_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
REPORTES = SALIDA / "04_REPORTES"
AUDITORIA = SALIDA / "03_AUDITORIA"

for c in [RESULTADOS, REPORTES, AUDITORIA]:
    c.mkdir(parents=True, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def norm(x):
    return re.sub(
        r"[^A-Z0-9]+",
        "_",
        str(x or "").strip().upper()
    ).strip("_")


def leer_texto(path):
    for enc in ["utf-8", "utf-8-sig", "cp1252", "latin1"]:
        try:
            return path.read_text(encoding=enc, errors="replace")
        except Exception:
            continue
    return ""


def columnas_estado(df):
    cols = []
    for c in df.columns:
        cn = norm(c)
        if any(t in cn for t in [
            "ESTADO",
            "SITUACION",
            "APROB",
            "CURSADO",
            "TRATAMIENTO",
            "ACCION",
            "DECISION",
            "MOTIVO",
            "OBSERVACION",
            "FORMULA",
            "LOGICA",
        ]):
            cols.append(c)
    return cols


def contiene_codigos_estado(df):
    texto = " ".join(
        df.head(5000).astype(str).fillna("").values.ravel()
    )
    tn = norm(texto)
    codigos = {}
    for codigo in ["A", "E", "I", "R", "NULL"]:
        # buscar como token separado
        codigos[codigo] = bool(re.search(rf"(^|_){codigo}(_|$)", tn))
    return codigos


def clasificar_relevancia(cols, df):
    cols_norm = " ".join(norm(c) for c in cols)
    texto = " ".join(df.head(200).astype(str).fillna("").values.ravel())
    texto_norm = norm(texto)

    score = 0

    fuertes = [
        "CUENTA_COMO_CURSADO",
        "CUENTA_COMO_APROBADO",
        "ESTADO_ORIGINAL",
        "ESTADO_HOJA1",
        "TIPO_TRATAMIENTO",
        "FORMULA_O_LOGICA",
        "UNIDADES_CURSADAS",
        "UNIDADES_APROBADAS",
        "ASIGNATURA",
        "ANO",
        "NIVEL",
        "CODCLI",
        "RUT",
    ]

    for p in fuertes:
        if norm(p) in cols_norm or norm(p) in texto_norm:
            score += 5

    for p in [" A ", " E ", " I ", " R ", "NULL", "APROB", "REPROB", "INSCR", "ELIM"]:
        if norm(p) in texto_norm:
            score += 2

    return score


hallazgos = []
filas_relevantes = []
scripts_hallazgos = []

# 1) Revisar Excel candidatos.
for path in CANDIDATOS:
    if not path.exists():
        hallazgos.append({
            "RUTA": str(path),
            "EXISTE": "NO",
            "HOJA": "",
            "SCORE": 0,
            "COLUMNAS_RELEVANTES": "",
            "OBSERVACION": "No existe en la ruta esperada.",
        })
        continue

    xls = pd.ExcelFile(path, engine="openpyxl")

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

        cols_rel = columnas_estado(df)
        codigos = contiene_codigos_estado(df)
        score = clasificar_relevancia(df.columns, df)

        if cols_rel or any(codigos.values()) or score > 0:
            hallazgos.append({
                "RUTA": str(path),
                "ARCHIVO": path.name,
                "EXISTE": "SI",
                "HOJA": hoja,
                "FILAS": len(df),
                "COLUMNAS": len(df.columns),
                "SCORE": score,
                "COLUMNAS_RELEVANTES": " | ".join(cols_rel),
                "CONTIENE_A": "SI" if codigos["A"] else "NO",
                "CONTIENE_E": "SI" if codigos["E"] else "NO",
                "CONTIENE_I": "SI" if codigos["I"] else "NO",
                "CONTIENE_R": "SI" if codigos["R"] else "NO",
                "CONTIENE_NULL": "SI" if codigos["NULL"] else "NO",
                "SHA256": sha256(path),
            })

            if cols_rel:
                sub = df[cols_rel].copy()
            else:
                sub = df.copy()

            # Extraer filas donde aparezcan A/E/I/R/NULL o conceptos de estado.
            for idx, row in sub.head(5000).iterrows():
                texto = " | ".join(str(v) for v in row.tolist())
                tn = norm(texto)

                if (
                    re.search(r"(^|_)A(_|$)", tn)
                    or re.search(r"(^|_)E(_|$)", tn)
                    or re.search(r"(^|_)I(_|$)", tn)
                    or re.search(r"(^|_)R(_|$)", tn)
                    or "NULL" in tn
                    or "APROB" in tn
                    or "REPROB" in tn
                    or "CURS" in tn
                    or "UNIDADES" in tn
                    or "ASIGNATURA" in tn
                ):
                    filas_relevantes.append({
                        "ARCHIVO": path.name,
                        "RUTA": str(path),
                        "HOJA": hoja,
                        "FILA_EXCEL_APROX": idx + 2,
                        "COLUMNAS_REVISADAS": " | ".join(cols_rel) if cols_rel else "TODAS",
                        "CONTENIDO": texto[:3000],
                    })

# 2) Buscar en scripts referencias exactas a ESTADO A/E/I/R.
for path in (RAIZ / "scripts").rglob("*.py"):
    texto = leer_texto(path)
    tn = norm(texto)

    if any(p in tn for p in [
        "ESTADO",
        "SITUACION",
        "UNIDADES_CURSADAS",
        "UNIDADES_APROBADAS",
        "ASIGNATURA",
        "HOJA1",
        "PROMEDIOS",
    ]):
        for n_linea, linea in enumerate(texto.splitlines(), start=1):
            ln = norm(linea)
            if any(p in ln for p in [
                "ESTADO",
                "SITUACION",
                "APROB",
                "REPROB",
                "CURS",
                "UNIDADES",
                "ASIGNATURA",
                "HOJA1",
                "PROMEDIOS",
            ]):
                scripts_hallazgos.append({
                    "SCRIPT": str(path),
                    "LINEA": n_linea,
                    "TEXTO": linea[:1000],
                })

hallazgos_df = pd.DataFrame(hallazgos)
filas_df = pd.DataFrame(filas_relevantes)
scripts_df = pd.DataFrame(scripts_hallazgos)

if not hallazgos_df.empty:
    hallazgos_df = hallazgos_df.sort_values(
        ["SCORE", "ARCHIVO", "HOJA"],
        ascending=[False, True, True],
    )

# 3) Extraer catálogo real de ESTADO en Hoja1.
df_hoja1 = pd.read_excel(
    PROMEDIOS,
    sheet_name="Hoja1",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if "ESTADO" not in df_hoja1.columns:
    raise SystemExit("Hoja1 no tiene columna ESTADO.")

catalogo_hoja1 = (
    df_hoja1["ESTADO"]
    .astype(str)
    .str.strip()
    .value_counts(dropna=False)
    .rename_axis("ESTADO_HOJA1")
    .reset_index(name="CASOS")
)

# 4) Crear matriz de decisión pendiente/observada, sin inventar.
matriz_decision = []

for estado in catalogo_hoja1["ESTADO_HOJA1"].tolist():
    estado_norm = norm(estado)

    coincidencias_excel = filas_df[
        filas_df["CONTENIDO"].astype(str).map(norm).str.contains(
            rf"(^|_){re.escape(estado_norm)}(_|$)",
            regex=True,
            na=False,
        )
    ] if not filas_df.empty and estado_norm else pd.DataFrame()

    coincidencias_script = scripts_df[
        scripts_df["TEXTO"].astype(str).map(norm).str.contains(
            rf"(^|_){re.escape(estado_norm)}(_|$)",
            regex=True,
            na=False,
        )
    ] if not scripts_df.empty and estado_norm else pd.DataFrame()

    matriz_decision.append({
        "ESTADO_HOJA1": estado,
        "CASOS_HOJA1": int(
            catalogo_hoja1.loc[
                catalogo_hoja1["ESTADO_HOJA1"].eq(estado),
                "CASOS"
            ].iloc[0]
        ),
        "HALLAZGOS_EXCEL": len(coincidencias_excel),
        "HALLAZGOS_SCRIPT": len(coincidencias_script),
        "RUTAS_EXCEL": " | ".join(
            coincidencias_excel["RUTA"].drop_duplicates().head(5).tolist()
        ) if not coincidencias_excel.empty else "",
        "RUTAS_SCRIPT": " | ".join(
            coincidencias_script["SCRIPT"].drop_duplicates().head(5).tolist()
        ) if not coincidencias_script.empty else "",
        "ESTADO_DECISION": (
            "REUTILIZAR_LOGICA_EXISTENTE_REVISAR_HALLAZGOS"
            if len(coincidencias_excel) or len(coincidencias_script)
            else "SIN_DICCIONARIO_EXPLICITO_ENCONTRADO"
        ),
    })

matriz_decision_df = pd.DataFrame(matriz_decision)

# Guardar.
hallazgos_df.to_csv(
    RESULTADOS / "01_HALLAZGOS_EXCEL_CANDIDATOS.tsv",
    sep="\t",
    index=False,
)

filas_df.to_csv(
    RESULTADOS / "02_FILAS_RELEVANTES_EXCEL.tsv",
    sep="\t",
    index=False,
)

scripts_df.to_csv(
    RESULTADOS / "03_REFERENCIAS_SCRIPTS_ESTADOS.tsv",
    sep="\t",
    index=False,
)

catalogo_hoja1.to_csv(
    RESULTADOS / "04_CATALOGO_ESTADOS_REALES_HOJA1.tsv",
    sep="\t",
    index=False,
)

matriz_decision_df.to_csv(
    RESULTADOS / "05_MATRIZ_DECISION_ESTADOS_HOJA1.tsv",
    sep="\t",
    index=False,
)

excel = RESULTADOS / "EXTRACCION_DICCIONARIO_ESTADOS_REAL_AVANCE.xlsx"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    hallazgos_df.to_excel(writer, sheet_name="HALLAZGOS_EXCEL", index=False)
    filas_df.to_excel(writer, sheet_name="FILAS_RELEVANTES", index=False)
    scripts_df.to_excel(writer, sheet_name="SCRIPTS", index=False)
    catalogo_hoja1.to_excel(writer, sheet_name="ESTADOS_REALES_HOJA1", index=False)
    matriz_decision_df.to_excel(writer, sheet_name="MATRIZ_DECISION", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 100)

manifest = SALIDA / "manifest_extraccion_diccionario_estados_real.json"

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "artefactos_revisados": [str(p) for p in CANDIDATOS],
            "excel": str(excel),
            "fuentes_originales_modificadas": False,
            "csv_carga_generado": False,
            "sies_ready_generado": False,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

informe = REPORTES / "INFORME_EXTRACCION_DICCIONARIO_ESTADOS_REAL.md"

top_hallazgos = hallazgos_df.head(20) if not hallazgos_df.empty else pd.DataFrame()

informe.write_text(
    "# Extracción de diccionario real de estados Hoja1\n\n"
    "Proceso: Avance Curricular SIES 2026  \n"
    "Subproyecto: Matrícula 5809  \n\n"
    f"Estados reales Hoja1: {len(catalogo_hoja1)}  \n"
    f"Hallazgos Excel: {len(hallazgos_df)}  \n"
    f"Filas relevantes Excel: {len(filas_df)}  \n"
    f"Referencias en scripts: {len(scripts_df)}  \n\n"
    "## Matriz de decisión estados\n\n"
    + matriz_decision_df.to_markdown(index=False)
    + "\n\n"
    f"Excel: `{excel}`\n\n"
    f"Carpeta: `{SALIDA}`\n",
    encoding="utf-8",
)

print()
print("=" * 120)
print("EXTRACCIÓN DICCIONARIO REAL DE ESTADOS — AVANCE CURRICULAR")
print("=" * 120)
print(f"Estados reales Hoja1: {len(catalogo_hoja1)}")
print(f"Hallazgos Excel: {len(hallazgos_df)}")
print(f"Filas relevantes Excel: {len(filas_df)}")
print(f"Referencias scripts: {len(scripts_df)}")
print("CSV de carga generado: NO")
print("SIES_READY generado: NO")
print("Fuentes originales modificadas: NO")
print()
print("ESTADOS REALES HOJA1")
print("-" * 120)
print(catalogo_hoja1.to_string(index=False))
print()
print("MATRIZ DECISIÓN")
print("-" * 120)
print(matriz_decision_df.to_string(index=False))
print()
print("TOP HALLAZGOS")
print("-" * 120)
if top_hallazgos.empty:
    print("No hay hallazgos.")
else:
    print(
        top_hallazgos[
            [
                "SCORE",
                "ARCHIVO",
                "HOJA",
                "COLUMNAS_RELEVANTES",
                "RUTA",
            ]
        ].to_string(index=False)
    )
print()
print("=" * 120)
print("ARCHIVOS GENERADOS")
print("=" * 120)
print(f"Excel: {excel}")
print(f"Informe: {informe}")
print(f"Carpeta: {SALIDA}")
print("=" * 120)

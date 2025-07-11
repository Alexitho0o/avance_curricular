# @title
# ╔═════════════════════════════════════════════════════════════╗
#   BLOQUE 1 · FORMA — estructura técnica y utilidades          #
# ╚═════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────
# ❶ · Librerías y utilidades generales
# ──────────────────────────────────────────────────────────────
import os                       # 🔧 Corrección aplicada: gestión robusta de rutas
import re, warnings
from pathlib import Path
import pandas as pd, numpy as np
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment

warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

# ──────────────────────────────────────────────────────────────
# ❷ · Carga / descarga de archivos en Google Colab
# ──────────────────────────────────────────────────────────────
def _in_colab() -> bool:
    """Detecta si el entorno de ejecución es Google Colab."""
    try:
        import google.colab  # type: ignore
        return True
    except ModuleNotFoundError:
        return False

def _ruta_content(fname: str | Path) -> Path:
    """
    🔧 Corrección aplicada:
    Convierte cualquier nombre de archivo a una ruta absoluta dentro de /content
    cuando el código se ejecuta en Colab, previniendo errores de I/O.
    """
    p = Path(fname)
    if _in_colab():
        return Path("/content") / p.name
    return p.resolve()

def cargar_excel() -> Path:
    """
    • En Colab muestra el widget `files.upload()`  
    • En local (Jupyter/Lab) solicita la ruta por input().
    Devuelve siempre la ruta absoluta dentro del directorio de trabajo.
    """
    if _in_colab():
        from google.colab import files  # type: ignore
        ruta_subida = Path(next(iter(files.upload())))
        destino = _ruta_content(ruta_subida)
        ruta_subida.replace(destino)
        print(f"✔ Archivo guardado en: {destino}")
        return destino
    else:
        ruta_local = Path(input("Ruta de archivo .xlsx: ").strip())
        if not ruta_local.exists():
            raise FileNotFoundError(ruta_local)
        return ruta_local.resolve()

def descargar_excel(path: str | Path) -> None:
    """
    Descarga el archivo al equipo en Colab; en local no hace nada.
    """
    if _in_colab():
        from google.colab import files  # type: ignore
        files.download(str(path))

# ──────────────────────────────────────────────────────────────
# ❸ · Normalización de RUT + formateo de Excel
# ──────────────────────────────────────────────────────────────
def normalizar_rut(num, dv) -> str:
    return re.sub(r"[^0-9]", "", str(num)) + str(dv).upper().strip()

def formatear_excel(path: str | Path) -> None:
    """
    • Activa filtro en fila 1  
    • Centra texto horizontal/vertical  
    • Ajusta ancho de columnas (12 – 45 px)
    """
    path = Path(path)
    wb = load_workbook(path)
    alin = Alignment(horizontal="center", vertical="center")
    for ws in wb.worksheets:
        ws.auto_filter.ref = ws.dimensions
        for col in ws.columns:
            w = max(len(str(c.value)) if c.value else 0 for c in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max(12, min(45, w + 2))
        for row in ws.iter_rows():
            for c in row:
                c.alignment = alin
    wb.save(path)

# ╔═════════════════════════════════════════════════════════════╗
#   BLOQUE 2 · FONDO — lógica Avance Curricular SIES 2025       #
# ╚═════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────
# ❹ · Carga y validación de hojas obligatorias + Equivalencia
# ──────────────────────────────────────────────────────────────
def cargar_datos(ruta: Path):
    book = pd.read_excel(ruta, sheet_name=None)

    df_carreras  = next((df for df in book.values()
                         if {"CODIGO_UNICO", "PLAN_ESTUDIOS", "TOTAL_UNIDADES_MEDIDA"}.issubset(df.columns)), None)
    df_matricula = next((df for df in book.values()
                         if {"NUM_DOCUMENTO", "CODIGO_UNICO", "PLAN_ESTUDIOS"}.issubset(df.columns)), None)
    hojas_hist   = [df for df in book.values()
                    if {"ANO", "PERIODO", "RUT"}.issubset(df.columns)]
    df_equiv     = book.get("Equivalencia")

    if df_carreras is None or df_matricula is None or not hojas_hist or df_equiv is None:
        raise ValueError("Faltan hojas Carreras, Matrícula, Históricos o Equivalencia.")

    df_hist = pd.concat(hojas_hist, ignore_index=True)
    return df_carreras, df_matricula, df_hist, df_equiv

# ──────────────────────────────────────────────────────────────
# ❺ · Limpieza, normalización y selección de carrera vigente
# ──────────────────────────────────────────────────────────────
def preparar_datos(df_carreras, df_matricula, df_hist, df_equiv):
    # A · Normalizar RUT
    df_hist['RUT_NORM']      = [normalizar_rut(r, d) for r, d in zip(df_hist['RUT'], df_hist['DIG'])]
    df_matricula['RUT_NORM'] = [normalizar_rut(n, d) for n, d in zip(df_matricula['NUM_DOCUMENTO'], df_matricula['DV'])]

    # B · Deduplicación
    df_carreras  = df_carreras.drop_duplicates(['CODIGO_UNICO', 'PLAN_ESTUDIOS'])
    df_matricula = df_matricula.drop_duplicates(['RUT_NORM', 'CODIGO_UNICO', 'PLAN_ESTUDIOS'])

    # C · Columnas opcionales con valores por defecto
    if "ESTADO_ACADEMICO" not in df_matricula.columns:
        df_matricula["ESTADO_ACADEMICO"] = "VIGENTE"
    if "VIGENCIA" not in df_matricula.columns:
        df_matricula["VIGENCIA"] = 1
    col_plan = "PLAN_DE_ESTUDIO" if "PLAN_DE_ESTUDIO" in df_matricula.columns else None

    # D · Cálculo de PESO_CARRERA
    prioridad = {"VIGENTE": 3, "SUSPENDIDO": 2, "ELIMINADO": 1}
    df_matricula["ANIO_PLAN"] = (
        df_matricula[col_plan].astype(str).str.extract(r"(\d{4})")[0].astype(float)
        if col_plan else 0
    )
    df_matricula["PESO_CARRERA"] = (
        df_matricula["ESTADO_ACADEMICO"].map(prioridad).fillna(0) * 1e6 +
        df_matricula["VIGENCIA"] * 1e3 +
        df_matricula["ANIO_PLAN"].fillna(0)
    )

    # E · Seleccionar carrera vigente por RUT
    idx_vig = (df_matricula.sort_values("PESO_CARRERA", ascending=False)
               .groupby("RUT_NORM").head(1).index)
    df_mat_ok = df_matricula.loc[idx_vig].copy()

    # F · Mapear CODCARR → CODIGO_UNICO usando Equivalencia
    if "CODCARR" in df_hist.columns:
        mapa_eq = (df_equiv[["CODCARR", "CODIGO_UNICO"]]
                   .dropna(subset=["CODCARR", "CODIGO_UNICO"])
                   .drop_duplicates("CODCARR")
                   .set_index("CODCARR")["CODIGO_UNICO"])
        df_hist["CODIGO_UNICO_EQ"] = df_hist["CODCARR"].map(mapa_eq)
        df_hist = df_hist.merge(
            df_mat_ok[["RUT_NORM", "CODIGO_UNICO"]],
            left_on=["RUT_NORM", "CODIGO_UNICO_EQ"],
            right_on=["RUT_NORM", "CODIGO_UNICO"],
            how="inner"
        ).drop(columns=["CODIGO_UNICO_EQ"])

    # G · Asegurar CODIGO_UNICO y PLAN_ESTUDIOS en histórico
    df_hist = df_hist.merge(
        df_mat_ok[["RUT_NORM", "CODIGO_UNICO", "PLAN_ESTUDIOS"]],
        on="RUT_NORM", how="left", suffixes=("", "_MAT")
    )
    for col in ["CODIGO_UNICO", "PLAN_ESTUDIOS"]:
        alt = f"{col}_MAT"
        if alt in df_hist.columns:
            df_hist[col] = df_hist[col].combine_first(df_hist[alt])
            df_hist.drop(columns=[alt], inplace=True)

    # H · Filtrar histórico por la carrera vigente seleccionada
    df_hist_ok = df_hist.merge(
        df_mat_ok[["RUT_NORM", "CODIGO_UNICO", "PLAN_ESTUDIOS"]],
        on=["RUT_NORM", "CODIGO_UNICO", "PLAN_ESTUDIOS"],
        how="inner"
    )
    return df_carreras, df_mat_ok, df_hist_ok

# ──────────────────────────────────────────────────────────────
# ❻ · Hoja Intentos — histórico alineado a la carrera vigente
# ──────────────────────────────────────────────────────────────
def construir_hoja_intentos(df_hist, df_matricula):
    return df_hist.copy()

# ──────────────────────────────────────────────────────────────
# ❼ · Construcción Resumen SIES 2024 por estudiante
# ──────────────────────────────────────────────────────────────
def construir_resumen_sies(df_intentos, df_carreras, log_errores=None):
    res, pat24, pat_hist = [], r"APROB", r"(?:APROB|CONVALID|RECONOC|EQUIV|HOMOLOG)"
    tot_plan = (df_carreras[["CODIGO_UNICO", "PLAN_ESTUDIOS", "TOTAL_UNIDADES_MEDIDA"]]
                .assign(TOTAL_UNIDADES_MEDIDA=lambda d: pd.to_numeric(d["TOTAL_UNIDADES_MEDIDA"], errors="coerce"))
                .set_index(["CODIGO_UNICO", "PLAN_ESTUDIOS"])["TOTAL_UNIDADES_MEDIDA"]
                .to_dict())

    for (rut, cu, plan), sub in df_intentos.groupby(["RUT_NORM", "CODIGO_UNICO", "PLAN_ESTUDIOS"]):
        total = tot_plan.get((cu, plan), np.nan)
        if pd.isna(total) or total <= 0:
            if log_errores is not None:
                log_errores.append({"tipo": "TOTAL_UNIDADES_MEDIDA vacío", "CODIGO_UNICO": cu, "PLAN_ESTUDIOS": plan})
            total = max(sub["CODRAMO"].nunique(), 1)

        sub24 = sub[sub["ANO"] == 2024]
        e24   = sub24["DESCRIPCION_ESTADO"].astype(str).str.upper()
        eh    = sub["DESCRIPCION_ESTADO"].astype(str).str.upper()

        cur24 = sub24["CODRAMO"].drop_duplicates().size
        apr24 = sub24[e24.str.contains(pat24, regex=True, na=False)]["CODRAMO"].drop_duplicates().size
        curt  = sub["CODRAMO"].drop_duplicates().size
        aprt  = min(
            (sub[eh.str.contains(pat_hist, regex=True, na=False)]
             .sort_values(["CODRAMO", "ANO", "PERIODO"])
             .drop_duplicates("CODRAMO").shape[0]),
            int(round(1.25 * total))
        )

        desglose = {
            f"UNIDADES_{n}_ANIO": sub24[sub24["PERIODO"] == n]["CODRAMO"].drop_duplicates().size
            for n in range(1, 8)
        }
        rec = sub.sort_values(["ANO", "PERIODO"]).iloc[-1]
        res.append({
            "RUT": rut, "CODIGO_UNICO": cu, "PLAN_ESTUDIOS": plan,
            "CURSO_1ER_SEM": "SI" if (sub24["PERIODO"] == 1).any() else "NO",
            "CURSO_2DO_SEM": "SI" if (sub24["PERIODO"] == 2).any() else "NO",
            "UNIDADES_CURSADAS": cur24, "UNIDADES_APROBADAS": apr24,
            "UNID_CURSADAS_TOTAL": curt, "UNID_APROBADAS_TOTAL": aprt,
            "ESTADO_ACADEMICO": rec.get("ESTADO_ACADEMICO", "SIN_INFO"),
            **desglose
        })

    columnas = [
        "RUT", "CODIGO_UNICO", "PLAN_ESTUDIOS",
        "CURSO_1ER_SEM", "CURSO_2DO_SEM",
        "UNIDADES_CURSADAS", "UNIDADES_APROBADAS",
        "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL",
        "ESTADO_ACADEMICO"
    ] + [f"UNIDADES_{n}_ANIO" for n in range(1, 8)]
    return pd.DataFrame(res, columns=columnas)

# ──────────────────────────────────────────────────────────────
# ❽ · Hoja “A. C. Carrera 2024” (estudiantes)
# ──────────────────────────────────────────────────────────────
def construir_hoja_ac_carrera2024(df_matricula, df_resumen):
    hoja = df_matricula.merge(
        df_resumen,
        left_on=["RUT_NORM", "CODIGO_UNICO", "PLAN_ESTUDIOS"],
        right_on=["RUT",       "CODIGO_UNICO", "PLAN_ESTUDIOS"],
        how="left",
        suffixes=("_MAT", "_RES")
    )

    # Aseguramos NUM_DOCUMENTO
    if "NUM_DOCUMENTO" not in hoja.columns:
        hoja["NUM_DOCUMENTO"] = df_matricula["NUM_DOCUMENTO"].values

    campos = [
        "NUM_DOCUMENTO",
        "CURSO_1ER_SEM", "CURSO_2DO_SEM",
        "UNIDADES_CURSADAS", "UNIDADES_APROBADAS",
        "UNID_CURSADAS_TOTAL", "UNID_APROBADAS_TOTAL",
        "ESTADO_ACADEMICO"
    ] + [f"UNIDADES_{n}_ANIO" for n in range(1, 8)]

    for c in campos:
        src = f"{c}_RES"
        base = hoja[c]  if c in hoja.columns else pd.Series(np.nan, index=hoja.index)
        srcs = hoja[src] if src in hoja.columns else pd.Series(np.nan, index=hoja.index)
        # 🔧 Corrección: sustituimos combine_first por where para evitar FutureWarning
        hoja[c] = base.where(~base.isna(), srcs)
        hoja.drop(columns=[src], errors="ignore", inplace=True)

    hoja.drop(columns=[col for col in hoja.columns if col.endswith("_MAT")] + ["RUT"], errors="ignore", inplace=True)

    final_cols = [col for col in df_matricula.columns if col != "VIGENCIA"] + campos + ["VIGENCIA"]
    for col in final_cols:
        if col not in hoja.columns:
            hoja[col] = np.nan

    hoja = hoja.loc[:, ~hoja.columns.duplicated()].reindex(columns=final_cols)
    hoja["VIGENCIA"] = 1
    return hoja

# ──────────────────────────────────────────────────────────────
# ❾ · Hoja “A. C. Matrícula 2024” (planes)
# ──────────────────────────────────────────────────────────────
def construir_hoja_ac_matricula2024(df_carreras, df_resumen):
    hoja = df_carreras.drop_duplicates(['CODIGO_UNICO', 'PLAN_ESTUDIOS']).copy()

    dist = [f"UNIDADES_{t}" for t in
            ["1ER_ANIO", "2DO_ANIO", "3ER_ANIO", "4TO_ANIO", "5TO_ANIO", "6TO_ANIO", "7MO_ANIO"]]

    agreg = (
        df_resumen
        .groupby(["CODIGO_UNICO", "PLAN_ESTUDIOS"])[[f"UNIDADES_{n}_ANIO" for n in range(1, 8)]]
        .max()
        .rename(columns={f"UNIDADES_{n}_ANIO": dist[n-1] for n in range(1, 8)})
        .reset_index()
    )
    hoja = hoja.merge(agreg, on=["CODIGO_UNICO", "PLAN_ESTUDIOS"], how="left")

    for col in dist:
        if col not in hoja.columns:
            hoja[col] = 0
        hoja[col] = hoja[col].fillna(0)

    hoja["TOTAL_UNIDADES_MEDIDA"] = hoja[dist].sum(axis=1)
    hoja["VIGENCIA"] = 1
    return hoja.loc[:, ~hoja.columns.duplicated()]

# ──────────────────────────────────────────────────────────────
# ❿ · Exportación y formateo final
# ──────────────────────────────────────────────────────────────
def exportar_archivos(hoja_carrera, hoja_matricula):
    dest_car = _ruta_content("A. C. Carrera 2024.xlsx")
    dest_mat = _ruta_content("A. C. Matrícula 2024.xlsx")

    with pd.ExcelWriter(dest_car, engine="openpyxl") as w1:
        hoja_carrera.to_excel(w1, index=False, sheet_name="A. C. Carrera 2024")
    with pd.ExcelWriter(dest_mat, engine="openpyxl") as w2:
        hoja_matricula.to_excel(w2, index=False, sheet_name="A. C. Matrícula 2024")

    formatear_excel(dest_car)
    formatear_excel(dest_mat)

# ──────────────────────────────────────────────────────────────
# ⓫ · Ejecución principal con contadores adicionales
# ──────────────────────────────────────────────────────────────
def main():
    ruta = cargar_excel()
    df_car, df_mat, df_hist, df_equiv = cargar_datos(ruta)
    df_car, df_mat, df_hist = preparar_datos(df_car, df_mat, df_hist, df_equiv)

    print(f"✔ Matrícula leída:               {len(df_mat)} registros")
    print(f"✔ Histórico filtrado:            {len(df_hist)} registros")

    df_int = construir_hoja_intentos(df_hist, df_mat)
    print(f"✔ Intentos a procesar:           {len(df_int)} filas")

    errores = []
    df_res  = construir_resumen_sies(df_int, df_car, errores)
    print(f"✔ Estudiantes procesados:        {len(df_res)}")
    print(f"✔ Cursaron 1er semestre (SI):    {df_res['CURSO_1ER_SEM'].eq('SI').sum()}")
    print(f"✔ Cursaron 2do semestre (SI):    {df_res['CURSO_2DO_SEM'].eq('SI').sum()}")

    hoja_car = construir_hoja_ac_carrera2024(df_mat, df_res)
    hoja_mat = construir_hoja_ac_matricula2024(df_car, df_res)

    exportar_archivos(hoja_car, hoja_mat)

    if errores:
        print("\n⚠ Inconsistencias registradas:")
        for e in errores:
            print("  •", e)

    descargar_excel(_ruta_content("A. C. Carrera 2024.xlsx"))
    descargar_excel(_ruta_content("A. C. Matrícula 2024.xlsx"))

if __name__ == "__main__":
    main()

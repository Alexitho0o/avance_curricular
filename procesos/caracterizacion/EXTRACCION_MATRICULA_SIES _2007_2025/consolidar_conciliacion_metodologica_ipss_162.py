#!/usr/bin/env python3
"""Genera un consolidado metodologico del informe SIES y la base local IPSS."""

from __future__ import annotations

import logging
import unicodedata
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, LineChart, Reference, Series
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


BASE_DIR = Path(__file__).resolve().parent
INFORME = BASE_DIR / "Informe_Retencion_SIES_2025.xlsx"
CSV_LOCAL = BASE_DIR / "salida" / "reporte_matricula_ip_san_sebastian_ORIGINAL.csv"
SALIDA = BASE_DIR / "Consolidado_Retencion_Trazable_Completo.xlsx"


def fmt_entero(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(round(float(value))):,}".replace(",", ".")


def fmt_decimal(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar(texto: object) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto).casefold())
        if unicodedata.category(c) != "Mn"
    )


def extraer_oficial(ruta: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    excel = pd.ExcelFile(ruta)
    logging.info("Hojas oficiales detectadas: %s", fmt_entero(len(excel.sheet_names)))
    hoja = next((n for n in excel.sheet_names if "retencion 1er ano" in normalizar(n) and "ies" in normalizar(n)), None)
    if hoja is None:
        raise ValueError("No se encontró la hoja oficial de retención por IES.")
    matriz = pd.read_excel(excel, sheet_name=hoja, header=None)
    encabezado = next((i for i, fila in matriz.iterrows() if any("cod." in normalizar(v) and "instituc" in normalizar(v) for v in fila.dropna())), None)
    if encabezado is None:
        raise ValueError("No se encontró el encabezado de la tabla por IES.")
    tabla = pd.read_excel(excel, sheet_name=hoja, header=encabezado)
    tabla.columns = [str(c).strip() for c in tabla.columns]
    codigo_col = next(c for c in tabla.columns if "cod." in normalizar(c) and "instituc" in normalizar(c))
    nombre_col = next(c for c in tabla.columns if "nombre" in normalizar(c))
    codigo = tabla[codigo_col].astype("string").str.replace(r"\.0$", "", regex=True).str.strip()
    fila = tabla[codigo.eq("162") | tabla[nombre_col].astype("string").str.contains("SAN SEBASTIAN", case=False, na=False)].iloc[0]
    oficiales = []
    for columna in tabla.columns:
        texto = str(columna).strip().removesuffix(".0")
        if texto.isdigit() and 2000 <= int(texto) <= 2030:
            valor = pd.to_numeric(fila[columna], errors="coerce")
            oficiales.append({"anio": int(texto), "tasa_oficial_pct": valor * 100 if pd.notna(valor) and valor <= 1 else valor, "hoja_oficial": hoja, "fila_encabezado_excel": encabezado + 1})
    logging.info("IPSS 162 extraído: %s años", fmt_entero(len(oficiales)))
    return pd.DataFrame(oficiales).sort_values("anio"), excel.sheet_names


def cargar_local(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta, dtype="string", encoding="utf-8-sig")
    df.columns = [str(c).strip().lower() for c in df.columns]
    for col in ("cat_periodo", "anio_ing_carr_act", "dur_estudio_carr", "dur_total_carr"):
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["mrun"] = df["mrun"].str.strip()
    return df[df["mrun"].notna() & df["mrun"].ne("") & df["cod_inst"].astype("string").str.strip().eq("162")].copy()


def tasa_local(df: pd.DataFrame, nombre: str, filtro) -> dict:
    cohorte = df[(df.cat_periodo == 2024) & (df.anio_ing_carr_act == 2024) & df.tipo_plan_carr.fillna("").str.casefold().eq("plan regular") & filtro(df)].drop_duplicates(["mrun", "cod_carrera", "codigo_unico"])
    futuro = df[df.cat_periodo == 2025]
    claves = set(zip(futuro.mrun, futuro.cod_inst))
    base = cohorte[["mrun", "cod_inst"]].drop_duplicates()
    retenidos = sum((r.mrun, r.cod_inst) in claves for r in base.itertuples())
    n = len(base)
    return {"escenario": nombre, "cohorte_n": n, "retenidos": retenidos, "tasa_local_pct": 100 * retenidos / n if n else pd.NA}


def construir_brecha(df: pd.DataFrame) -> pd.DataFrame:
    escenarios = [
        tasa_local(df, "Bruto local (todos los niveles)", lambda x: pd.Series(True, index=x.index)),
        tasa_local(df, "Solo Pregrado", lambda x: x.nivel_global.eq("Pregrado")),
        tasa_local(df, "Pregrado con umbrales SIES", lambda x: (
            (x.nivel_global == "Pregrado")
            & (
                ((x.nivel_carrera_2 == "Carreras Técnicas") & (x.dur_estudio_carr >= 4))
                | ((x.nivel_carrera_1 == "Profesional Sin Licenciatura") & (x.dur_estudio_carr >= 6))
                | ((x.nivel_carrera_1 == "Profesional Con Licenciatura") & (x.dur_estudio_carr >= 8))
            )
        )),
    ]
    result = pd.DataFrame(escenarios)
    result["detalle"] = [
        "Incluye 13 registros Postítulo identificados en la cohorte local 2024.",
        "Excluye Postítulo; conserva los criterios locales de cohorte y seguimiento.",
        "Aplica los umbrales explícitos del informe: 4, 6 y 8 semestres según programa.",
    ]
    return result


def construir_cuadratura(df: pd.DataFrame) -> pd.DataFrame:
    """Compara el total institucional local con la suma del detalle de carreras."""
    filas = []
    for anio in sorted(df["cat_periodo"].dropna().unique()):
        cohorte = df[(df.cat_periodo == anio) & (df.anio_ing_carr_act == anio) & df.tipo_plan_carr.fillna("").str.casefold().eq("plan regular")]
        futuro = df[df.cat_periodo == anio + 1]
        if cohorte.empty or futuro.empty:
            continue
        keys = set(zip(futuro.mrun, futuro.cod_inst))
        institucional = cohorte[["mrun", "cod_inst"]].drop_duplicates()
        detalle = cohorte.drop_duplicates(["mrun", "cod_carrera", "codigo_unico"])
        retenidos_inst = sum((r.mrun, r.cod_inst) in keys for r in institucional.itertuples())
        retenidos_carr = sum((r.mrun, r.cod_inst) in keys for r in detalle.itertuples())
        filas.append({"anio_cohorte": int(anio), "tamano_institucional": len(institucional), "tamano_suma_carreras": len(detalle), "retenidos_institucional": retenidos_inst, "retenidos_suma_carreras": retenidos_carr, "dif_tamano": len(institucional) - len(detalle), "dif_retenidos": retenidos_inst - retenidos_carr})
    result = pd.DataFrame(filas)
    if not result.empty:
        result["cuadra"] = result.dif_tamano.eq(0) & result.dif_retenidos.eq(0)
    return result


def construir_ranking_2024(df: pd.DataFrame, estandar: float) -> pd.DataFrame:
    """Construye el detalle 2024 por carrera y programa con transicion a 2025."""
    cohorte = df[(df.cat_periodo == 2024) & (df.anio_ing_carr_act == 2024) & df.tipo_plan_carr.fillna("").str.casefold().eq("plan regular")]
    futuro = df[df.cat_periodo == 2025]
    keys_inst = set(zip(futuro.mrun, futuro.cod_inst))
    keys_prog = set(zip(futuro.mrun, futuro.codigo_unico))
    detalle = cohorte.drop_duplicates(["mrun", "cod_carrera", "codigo_unico"]).copy()
    detalle["retenido_inst"] = [int((r.mrun, r.cod_inst) in keys_inst) for r in detalle.itertuples()]
    detalle["retenido_programa"] = [int((r.mrun, r.codigo_unico) in keys_prog) for r in detalle.itertuples()]
    carrera = detalle.groupby(["cod_carrera", "nomb_carrera"], dropna=False, as_index=False).agg(tamano_cohorte=("mrun", "nunique"), retenidos=("retenido_inst", "sum"))
    carrera["nivel_detalle"] = "carrera"
    programa = detalle.groupby(["cod_carrera", "nomb_carrera", "codigo_unico"], dropna=False, as_index=False).agg(tamano_cohorte=("mrun", "nunique"), retenidos=("retenido_programa", "sum"))
    programa["nivel_detalle"] = "programa"
    result = pd.concat([carrera, programa], ignore_index=True, sort=False)
    result["anio_cohorte"] = 2024
    result["tasa_recalculada_pct"] = 100 * result.retenidos / result.tamano_cohorte.replace(0, pd.NA)
    result["estandar_institucional_pct"] = estandar
    result["Delta_Interno_pct"] = result.tasa_recalculada_pct - estandar
    return result.sort_values(["nivel_detalle", "tasa_recalculada_pct"], ascending=[True, False])


def construir_retencion_granular(df: pd.DataFrame) -> pd.DataFrame:
    """Reconstruye el detalle estudiante-programa de cada cohorte evaluable."""
    filas = []
    for anio in sorted(df["cat_periodo"].dropna().unique()):
        cohorte = df[
            (df.cat_periodo == anio)
            & (df.anio_ing_carr_act == anio)
            & df.tipo_plan_carr.fillna("").str.casefold().eq("plan regular")
        ].copy()
        futuro = df[df.cat_periodo == anio + 1]
        if cohorte.empty or futuro.empty:
            continue
        futuro_inst = set(zip(futuro.mrun, futuro.cod_inst))
        futuro_carrera = set(zip(futuro.mrun, futuro.cod_carrera))
        futuro_programa = set(zip(futuro.mrun, futuro.codigo_unico))
        cohorte = cohorte.drop_duplicates(["mrun", "cod_carrera", "codigo_unico"])
        for registro in cohorte.itertuples(index=False):
            fila = {
                "mrun": registro.mrun,
                "cod_inst": registro.cod_inst,
                "nomb_inst": registro.nomb_inst,
                "cat_periodo": int(anio),
                "anio_cohorte": int(anio),
                "anio_seguimiento": int(anio + 1),
                "anio_ing_carr_act": registro.anio_ing_carr_act,
                "cod_carrera": registro.cod_carrera,
                "nomb_carrera": registro.nomb_carrera,
                "codigo_unico": registro.codigo_unico,
                "cod_sede": registro.cod_sede,
                "sede": registro.nomb_sede,
                "nivel_global": registro.nivel_global,
                "nivel_carrera_1": registro.nivel_carrera_1,
                "nivel_carrera_2": registro.nivel_carrera_2,
                "modalidad": registro.modalidad,
                "jornada": registro.jornada,
                "tipo_plan_carr": registro.tipo_plan_carr,
                "dur_estudio_carr": registro.dur_estudio_carr,
                "dur_proceso_tit": registro.dur_proceso_tit,
                "dur_total_carr": registro.dur_total_carr,
                "retenido_inst": int((registro.mrun, registro.cod_inst) in futuro_inst),
                "retenido_carrera": int((registro.mrun, registro.cod_carrera) in futuro_carrera),
                "retenido_programa": int((registro.mrun, registro.codigo_unico) in futuro_programa),
            }
            filas.append(fila)
    result = pd.DataFrame(filas)
    logging.info("Detalle granular Retencion IPSS: %s filas", fmt_entero(len(result)))
    return result


def extraer_notas(ruta: Path, nombres: list[str]) -> pd.DataFrame:
    relevantes = [n for n in nombres if any(k in normalizar(n) for k in ("retencion", "comparacion"))]
    filas = []
    for nombre in relevantes:
        matriz = pd.read_excel(ruta, sheet_name=nombre, header=None)
        for indice, fila in matriz.iterrows():
            valores = [str(v).strip() for v in fila.tolist() if pd.notna(v) and str(v).strip()]
            if valores:
                filas.append({"hoja": nombre, "fila_excel": int(indice) + 1, "contenido_integro": " | ".join(valores)})
    logging.info("Filas metodológicas/documentales preservadas: %s", fmt_entero(len(filas)))
    return pd.DataFrame(filas)


def formatear_regional(frame: pd.DataFrame) -> pd.DataFrame:
    """Convierte numeros exportados a texto regional chileno, sin simbolo %."""
    result = frame.copy()
    for columna in result.columns:
        if not pd.api.types.is_numeric_dtype(result[columna]):
            continue
        if columna.startswith("_GRAFICO_"):
            continue
        if columna == "anio" or columna == "cat_periodo" or columna.startswith("anio_") or columna.endswith("_anio"):
            result[columna] = result[columna].astype("Int64")
            continue
        if "tasa" in columna or "diferencia" in columna or "delta" in columna or "estandar" in columna:
            result[columna] = result[columna].map(fmt_decimal)
        else:
            result[columna] = result[columna].map(fmt_entero)
    return result


def agregar_fuentes_numericas(
    frame: pd.DataFrame,
    columnas: list[str],
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Conserva copias numericas ocultas para alimentar graficos de Excel."""
    result = frame.copy()
    fuentes = {}
    for columna in columnas:
        nombre = f"_GRAFICO_{columna}"
        result[nombre] = pd.to_numeric(frame[columna], errors="coerce")
        fuentes[columna] = nombre
    return result, fuentes


def exportar(oficial: pd.DataFrame, brecha: pd.DataFrame, notas: pd.DataFrame, ranking: pd.DataFrame, cuadratura: pd.DataFrame, granular: pd.DataFrame, ruta: Path) -> None:
    conciliacion = oficial.copy()
    bruto = brecha.loc[brecha.escenario.eq("Bruto local (todos los niveles)"), "tasa_local_pct"].iloc[0]
    conciliacion["tasa_bruta_local_pct"] = bruto
    conciliacion["diferencia_oficial_menos_bruto_pp"] = conciliacion.tasa_oficial_pct - bruto
    conciliacion["coincide_2_decimales"] = conciliacion["diferencia_oficial_menos_bruto_pp"].abs().le(0.01)
    conciliacion, fuentes_conciliacion = agregar_fuentes_numericas(
        conciliacion, ["tasa_oficial_pct", "tasa_bruta_local_pct"]
    )
    ranking, fuentes_ranking = agregar_fuentes_numericas(
        ranking, ["tamano_cohorte", "retenidos"]
    )
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        for frame, sheet in ((conciliacion, "Conciliacion_Oficial_162"), (ranking, "Ranking_Carreras_2024"), (cuadratura, "Cuadratura_Anual"), (brecha, "Explicacion_Brecha_2024"), (notas, "Notas_Metodologicas_SIES"), (granular, "Retención IPSS")):
            if sheet != "Notas_Metodologicas_SIES":
                frame = formatear_regional(frame)
            frame.to_excel(writer, sheet_name=sheet, index=False)
    mejorar_presentacion(ruta, fuentes_conciliacion, fuentes_ranking)
    logging.info("Archivo escrito y verificado: %s bytes", fmt_entero(ruta.stat().st_size))


def mejorar_presentacion(
    ruta: Path,
    fuentes_conciliacion: dict[str, str],
    fuentes_ranking: dict[str, str],
) -> None:
    """Aplica estilo, filtros, anchos y graficos nativos al libro final."""
    libro = load_workbook(ruta)
    relleno = PatternFill("solid", fgColor="1F497D")
    for hoja in libro.worksheets:
        hoja.sheet_view.showGridLines = True
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions
        for celda in hoja[1]:
            celda.fill = relleno
            celda.font = Font(color="FFFFFF", bold=True)
        for columna in hoja.columns:
            letra = columna[0].column_letter
            ancho = min(max(len(str(c.value or "")) for c in columna) + 3, 55)
            hoja.column_dimensions[letra].width = max(ancho, 10)
    oficial = libro["Conciliacion_Oficial_162"]
    grafico_linea = LineChart()
    grafico_linea.title = "Tasa oficial SIES versus reconstrucción local"
    grafico_linea.y_axis.title = "Porcentaje"
    grafico_linea.x_axis.title = "Año"
    for columna in fuentes_conciliacion.values():
        indice = next(c.column for c in oficial[1] if c.value == columna)
        serie = Reference(oficial, min_col=indice, min_row=2, max_row=oficial.max_row)
        grafico_linea.series.append(Series(serie, title=columna.replace("_GRAFICO_", "")))
    grafico_linea.set_categories(Reference(oficial, min_col=1, min_row=2, max_row=oficial.max_row))
    grafico_linea.height = 8
    grafico_linea.width = 15
    oficial.add_chart(grafico_linea, "I2")
    ranking_hoja = libro["Ranking_Carreras_2024"]
    grafico_barras = BarChart()
    grafico_barras.type = "bar"
    grafico_barras.style = 10
    grafico_barras.title = "Tamaño de cohorte y retenidos 2024"
    grafico_barras.y_axis.title = "Carrera / programa"
    grafico_barras.x_axis.title = "Estudiantes"
    for columna in fuentes_ranking.values():
        indice = next(c.column for c in ranking_hoja[1] if c.value == columna)
        serie = Reference(ranking_hoja, min_col=indice, min_row=2, max_row=min(ranking_hoja.max_row, 31))
        grafico_barras.series.append(Series(serie, title=columna.replace("_GRAFICO_", "")))
    grafico_barras.set_categories(Reference(ranking_hoja, min_col=2, min_row=2, max_row=min(ranking_hoja.max_row, 31)))
    grafico_barras.height = 10
    grafico_barras.width = 17
    ranking_hoja.add_chart(grafico_barras, "L2")
    for hoja in (oficial, ranking_hoja):
        for indice in range(1, hoja.max_column + 1):
            if str(hoja.cell(1, indice).value).startswith("_GRAFICO_"):
                hoja.column_dimensions[get_column_letter(indice)].hidden = True
    libro.save(ruta)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    oficial, hojas = extraer_oficial(INFORME)
    local = cargar_local(CSV_LOCAL)
    logging.info("Filas locales IPSS 162 con MRUN: %s", fmt_entero(len(local)))
    brecha = construir_brecha(local)
    notas = extraer_notas(INFORME, hojas)
    estandar = float(oficial.loc[oficial.anio.eq(2024), "tasa_oficial_pct"].iloc[0])
    ranking = construir_ranking_2024(local, estandar)
    cuadratura = construir_cuadratura(local)
    granular = construir_retencion_granular(local)
    exportar(oficial, brecha, notas, ranking, cuadratura, granular, SALIDA)
    logging.info("Salida: %s", SALIDA)
    print("Conciliación oficial IPSS 162:")
    print(oficial[["anio", "tasa_oficial_pct"]].to_string(index=False))
    print("\nEscenarios cohorte 2024:")
    print(brecha[["escenario", "cohorte_n", "retenidos", "tasa_local_pct"]].to_string(index=False))
    libro = load_workbook(SALIDA, read_only=True)
    for hoja in libro.worksheets:
        logging.info("Hoja %s: %s filas x %s columnas", hoja.title, fmt_entero(hoja.max_row), fmt_entero(hoja.max_column))


if __name__ == "__main__":
    main()
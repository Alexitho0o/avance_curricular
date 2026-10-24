#!/usr/bin/env python3
"""Audita y cruza retencion IPSS 162 desde un informe Excel SIES."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "Informe_Retencion_SIES_2025.xlsx"
DEFAULT_OUTPUT = BASE_DIR / "Auditoria_y_Cruces_IPSS_162.xlsx"
REQUIRED_COLUMNS = {
    "anio_cohorte",
    "anio_seguimiento",
    "nivel",
    "tamano_cohorte",
    "retenidos",
    "tasa_retencion_pct",
}


def configurar_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def formato_entero(value: object) -> str:
    """Formatea conteos con punto como separador de miles."""
    if pd.isna(value):
        return "-"
    return f"{int(round(float(value))):,}".replace(",", ".")


def formato_decimal(value: object) -> str:
    """Formatea decimales con miles punto y decimales coma."""
    if pd.isna(value):
        return "-"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def leer_informe(ruta: Path) -> pd.DataFrame:
    """Lee todas las hojas y agrega la hoja de origen para trazabilidad."""
    logging.info("Cargando archivo: %s", ruta)
    hojas = pd.read_excel(ruta, sheet_name=None)
    tablas = []
    for nombre, tabla in hojas.items():
        tabla = tabla.copy()
        tabla.columns = [str(col).strip().lower() for col in tabla.columns]
        tabla["hoja_origen"] = nombre
        tablas.append(tabla)
        logging.info("Hoja %s: %s filas", nombre, formato_entero(len(tabla)))
    if not tablas:
        raise ValueError("El archivo Excel no contiene hojas.")
    datos = pd.concat(tablas, ignore_index=True, sort=False)
    faltantes = sorted(REQUIRED_COLUMNS - set(datos.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")
    return datos


def limpiar_datos(datos: pd.DataFrame) -> pd.DataFrame:
    """Normaliza niveles y convierte conteos booleanos/nulos a enteros."""
    datos = datos.copy()
    datos["nivel"] = datos["nivel"].astype("string").str.strip().str.casefold()
    for columna in ("anio_cohorte", "anio_seguimiento"):
        datos[columna] = pd.to_numeric(datos[columna], errors="coerce").astype("Int64")
    for columna in ("tamano_cohorte", "retenidos"):
        datos[columna] = datos[columna].map(
            lambda valor: int(valor) if isinstance(valor, bool) else valor
        )
        datos[columna] = (
            pd.to_numeric(datos[columna], errors="coerce")
            .fillna(0)
            .round()
            .astype("int64")
        )
    datos["tasa_retencion_pct"] = pd.to_numeric(
        datos["tasa_retencion_pct"], errors="coerce"
    )
    logging.info("Filas procesadas despues de limpieza: %s", formato_entero(len(datos)))
    return datos


def auditar_cuadratura(datos: pd.DataFrame) -> pd.DataFrame:
    """Cuadra por año institucional versus suma de carreras."""
    institucional = (
        datos[datos["nivel"] == "institucional"]
        .groupby("anio_cohorte", as_index=False)
        .agg(
            tamano_institucional=("tamano_cohorte", "sum"),
            retenidos_institucional=("retenidos", "sum"),
        )
    )
    carreras = (
        datos[datos["nivel"] == "carrera"]
        .groupby("anio_cohorte", as_index=False)
        .agg(
            tamano_suma_carreras=("tamano_cohorte", "sum"),
            retenidos_suma_carreras=("retenidos", "sum"),
        )
    )
    result = institucional.merge(carreras, on="anio_cohorte", how="outer").fillna(0)
    result["dif_tamano"] = result.tamano_institucional - result.tamano_suma_carreras
    result["dif_retenidos"] = result.retenidos_institucional - result.retenidos_suma_carreras
    result["cuadra"] = result.dif_tamano.eq(0) & result.dif_retenidos.eq(0)
    logging.info(
        "Cuadratura: %s años auditados | %s discrepancias",
        formato_entero(len(result)),
        formato_entero((~result["cuadra"]).sum()),
    )
    return result.sort_values("anio_cohorte")


def construir_ranking(datos: pd.DataFrame) -> pd.DataFrame:
    """Recalcula tasas de carrera 2024 y las compara con el estándar institucional."""
    institucional = datos[(datos["nivel"] == "institucional") & datos.anio_cohorte.eq(2024)]
    estandares = institucional["tasa_retencion_pct"].dropna().unique()
    if len(estandares) != 1:
        raise ValueError(f"Se esperaba un estándar institucional 2024; encontrados: {estandares.tolist()}")
    estandar = float(estandares[0])
    logging.info("Estandar institucional 2024: %s", formato_decimal(estandar))

    carreras = datos[(datos["nivel"] == "carrera") & datos.anio_cohorte.eq(2024)].copy()
    if carreras.empty:
        raise ValueError("No existen registros de carreras para la cohorte 2024.")
    carreras["tasa_recalculada_pct"] = (
        carreras["retenidos"].div(carreras["tamano_cohorte"].replace(0, pd.NA)).mul(100).fillna(0)
    )
    carreras["estandar_institucional_pct"] = estandar
    carreras["Delta_Interno_pct"] = carreras["tasa_recalculada_pct"] - estandar
    carreras["error_tasa_origen"] = (
        carreras["tasa_retencion_pct"] - carreras["tasa_recalculada_pct"]
    ).abs().gt(0.01)
    carreras = carreras.sort_values(
        ["tasa_recalculada_pct", "cod_carrera"], ascending=[False, True], na_position="last"
    ).reset_index(drop=True)
    carreras.insert(0, "ranking", carreras.index + 1)
    logging.info("Carreras 2024 ordenadas: %s", formato_entero(len(carreras)))
    return carreras


def preparar_exportacion(cuadratura: pd.DataFrame, ranking: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convierte los resultados a texto regional para su lectura inequívoca en Excel."""
    cuadratura = cuadratura.copy()
    ranking = ranking.copy()
    for frame in (cuadratura, ranking):
        for columna in frame.columns:
            if columna in {"cuadra", "error_tasa_origen", "hoja_origen", "nivel", "cod_carrera", "nomb_carrera", "codigo_unico"}:
                continue
            if "tasa" in columna or "pct" in columna.lower() or "delta" in columna.lower() or "estandar" in columna.lower():
                frame[columna] = frame[columna].map(formato_decimal)
            else:
                frame[columna] = frame[columna].map(formato_entero)
    return cuadratura, ranking


def exportar(cuadratura: pd.DataFrame, ranking: pd.DataFrame, ruta: Path) -> None:
    logging.info("Exportando hojas finales: %s", ruta)
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        cuadratura.to_excel(writer, sheet_name="Cuadratura_Anual", index=False)
        ranking.to_excel(writer, sheet_name="Ranking_Carreras_2024", index=False)
    logging.info("Exportacion exitosa: %s", ruta)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    configurar_logging()
    datos = limpiar_datos(leer_informe(args.entrada))
    cuadratura = auditar_cuadratura(datos)
    ranking = construir_ranking(datos)
    cuadratura_export, ranking_export = preparar_exportacion(cuadratura, ranking)
    exportar(cuadratura_export, ranking_export, args.salida)


if __name__ == "__main__":
    main()
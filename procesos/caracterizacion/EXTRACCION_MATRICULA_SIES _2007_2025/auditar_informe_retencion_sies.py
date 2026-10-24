#!/usr/bin/env python3
"""Audita Informe_Retencion_SIES_2025.xlsx y exporta resultados trazables."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "Informe_Retencion_SIES_2025.xlsx"
DEFAULT_OUTPUT = BASE_DIR / "Auditoria_Estructural_IPSS.xlsx"
REQUIRED_COLUMNS = {
    "anio_cohorte",
    "anio_seguimiento",
    "nivel",
    "tamano_cohorte",
    "retenidos",
    "tasa_retencion_pct",
}
HEADER_FILL = PatternFill("solid", fgColor="1F497D")


def formato_entero(value: object) -> str:
    """Devuelve enteros con punto como separador de miles."""
    if pd.isna(value):
        return "-"
    return f"{int(value):,}".replace(",", ".")


def formato_decimal(value: object) -> str:
    """Devuelve decimales con miles punto y decimales coma."""
    if pd.isna(value):
        return "-"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def configurar_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def leer_informe(ruta: Path) -> pd.DataFrame:
    """Lee todas las hojas y las combina conservando el origen."""
    logging.info("Leyendo informe: %s", ruta)
    hojas = pd.read_excel(ruta, sheet_name=None)
    if not hojas:
        raise ValueError("El archivo Excel no contiene hojas.")

    tablas = []
    for nombre_hoja, tabla in hojas.items():
        tabla = tabla.copy()
        tabla.columns = [str(col).strip().lower() for col in tabla.columns]
        tabla["hoja_origen"] = nombre_hoja
        tablas.append(tabla)
        logging.info("Hoja %s: %s filas", nombre_hoja, formato_entero(len(tabla)))

    df = pd.concat(tablas, ignore_index=True, sort=False)
    faltantes = sorted(REQUIRED_COLUMNS - set(df.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")
    return df


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte conteos a enteros y tasas a numeros en puntos porcentuales."""
    result = df.copy()
    result["nivel"] = result["nivel"].astype("string").str.strip().str.casefold()
    for column in ("anio_cohorte", "anio_seguimiento"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    for column in ("tamano_cohorte", "retenidos"):
        # Booleanos: True=1 y False=0. Texto no numerico: NaN, luego 0.
        result[column] = result[column].map(
            lambda value: int(value) if isinstance(value, bool) else value
        )
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).round().astype("int64")
    result["tasa_retencion_pct"] = pd.to_numeric(
        result["tasa_retencion_pct"], errors="coerce"
    )
    result["cod_carrera"] = result.get("cod_carrera", pd.Series(pd.NA, index=result.index))
    result["nomb_carrera"] = result.get("nomb_carrera", pd.Series(pd.NA, index=result.index))
    result["codigo_unico"] = result.get("codigo_unico", pd.Series(pd.NA, index=result.index))
    logging.info("Filas despues de limpieza: %s", formato_entero(len(result)))
    return result


def cuadratura(df: pd.DataFrame) -> pd.DataFrame:
    """Compara los totales institucionales contra la suma de carreras."""
    institucional = (
        df[df["nivel"] == "institucional"]
        .groupby("anio_cohorte", as_index=False)
        .agg(tamano_institucional=("tamano_cohorte", "sum"), retenidos_institucional=("retenidos", "sum"))
    )
    carreras = (
        df[df["nivel"] == "carrera"]
        .groupby("anio_cohorte", as_index=False)
        .agg(tamano_suma_carreras=("tamano_cohorte", "sum"), retenidos_suma_carreras=("retenidos", "sum"))
    )
    result = institucional.merge(carreras, on="anio_cohorte", how="outer").fillna(0)
    result["diferencia_tamano"] = result.tamano_institucional - result.tamano_suma_carreras
    result["diferencia_retenidos"] = result.retenidos_institucional - result.retenidos_suma_carreras
    result["cuadra"] = result["diferencia_tamano"].eq(0) & result["diferencia_retenidos"].eq(0)
    discrepancias = result[~result["cuadra"]]
    logging.info("Anios auditados: %s | discrepancias: %s", formato_entero(len(result)), formato_entero(len(discrepancias)))
    return result.sort_values("anio_cohorte")


def validar_carreras(df: pd.DataFrame) -> pd.DataFrame:
    """Recalcula tasas por carrera y ordena 2024 de mayor a menor."""
    result = df[df["nivel"] == "carrera"].copy()
    result["tasa_recalculada_pct"] = (
        result["retenidos"].div(result["tamano_cohorte"].replace(0, pd.NA)).mul(100).fillna(0)
    )
    result["diferencia_tasa_pct"] = result["tasa_retencion_pct"] - result["tasa_recalculada_pct"]
    result["error_calculo_origen"] = result["diferencia_tasa_pct"].abs().gt(0.01)
    result["orden_2024"] = pd.NA
    recientes = result["anio_cohorte"].eq(2024)
    result.loc[recientes, "orden_2024"] = (
        result.loc[recientes, "tasa_recalculada_pct"].rank(method="first", ascending=False).astype("int64")
    )
    return result.sort_values(["anio_cohorte", "tasa_recalculada_pct"], ascending=[False, False])


def exportar(cuadra: pd.DataFrame, carreras: pd.DataFrame, ruta: Path) -> None:
    """Exporta dos hojas con formato regional visible en Excel."""
    logging.info("Exportando resultados: %s", ruta)
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        cuadra.to_excel(writer, sheet_name="Cuadratura_Totales", index=False)
        carreras.to_excel(writer, sheet_name="Validacion_Carreras", index=False)

    book = load_workbook(ruta)
    for sheet in book.worksheets:
        sheet.sheet_view.showGridLines = True
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.fill = HEADER_FILL
            cell.font = Font(color="FFFFFF", bold=True)
        headers = {str(cell.value).lower(): cell.column for cell in sheet[1]}
        for header, column in headers.items():
            if any(word in header for word in ("tamano", "retenidos", "diferencia", "orden")):
                for row in range(2, sheet.max_row + 1):
                    sheet.cell(row, column).number_format = "#.##0"
            if any(word in header for word in ("tasa", "delta")):
                for row in range(2, sheet.max_row + 1):
                    sheet.cell(row, column).number_format = "0,00"
        for column in sheet.columns:
            letter = column[0].column_letter
            width = min(max(len(str(cell.value or "")) for cell in column) + 3, 55)
            sheet.column_dimensions[letter].width = max(width, 10)
    book.save(ruta)
    logging.info("Exportacion exitosa: %s", ruta)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    configurar_logging()
    datos = limpiar_datos(leer_informe(args.entrada))
    cuadra = cuadratura(datos)
    carreras = validar_carreras(datos)
    if not carreras.empty:
        errores = int(carreras["error_calculo_origen"].sum())
        logging.info("Errores de tasa detectados: %s", formato_entero(errores))
        recientes = carreras[carreras["anio_cohorte"] == 2024]
        logging.info("Carreras ordenadas para 2024: %s", formato_entero(len(recientes)))
    exportar(cuadra, carreras, args.salida)


if __name__ == "__main__":
    main()
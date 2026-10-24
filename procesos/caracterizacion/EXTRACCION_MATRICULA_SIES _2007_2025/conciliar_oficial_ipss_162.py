#!/usr/bin/env python3
"""Concilia el informe ancho SIES contra el CSV original de matricula."""

from __future__ import annotations

import logging
import unicodedata
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INFORME = BASE_DIR / "Informe_Retencion_SIES_2025.xlsx"
CSV_ORIGINAL = BASE_DIR / "salida" / "reporte_matricula_ip_san_sebastian_ORIGINAL.csv"
SALIDA = BASE_DIR / "Conciliacion_Oficial_IPSS_162.xlsx"


def fmt_entero(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(round(float(value))):,}".replace(",", ".")


def fmt_decimal(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def encontrar_hoja(excel: pd.ExcelFile, fragmentos: tuple[str, ...]) -> str:
    for hoja in excel.sheet_names:
        normalizada = "".join(
            caracter for caracter in unicodedata.normalize("NFD", hoja.casefold())
            if unicodedata.category(caracter) != "Mn"
        )
        if all(fragmento in normalizada for fragmento in fragmentos):
            return hoja
    raise ValueError(f"No se encontró una hoja compatible con {fragmentos}.")


def extraer_ies(informe: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Detecta la tabla ancha por IES y extrae la fila de codigo 162."""
    excel = pd.ExcelFile(informe)
    inspeccion = pd.DataFrame({"hoja": excel.sheet_names})
    logging.info("Hojas detectadas: %s", fmt_entero(len(excel.sheet_names)))
    hoja = encontrar_hoja(excel, ("retencion 1er ano", "ies"))
    crudo = pd.read_excel(excel, sheet_name=hoja, header=None)
    encabezado = None
    for indice, fila in crudo.iterrows():
        valores = {str(valor).strip().casefold() for valor in fila.dropna()}
        if "cod. institución" in valores or "cod. institucion" in valores:
            encabezado = indice
            break
    if encabezado is None:
        raise ValueError(f"No se detectó encabezado de instituciones en {hoja}.")
    tabla = pd.read_excel(excel, sheet_name=hoja, header=encabezado)
    tabla.columns = [str(col).strip() for col in tabla.columns]
    codigo_col = next((c for c in tabla.columns if "cod." in c.casefold() and "instit" in c.casefold()), tabla.columns[0])
    nombre_col = next((c for c in tabla.columns if "nombre" in c.casefold()), tabla.columns[1])
    codigo = tabla[codigo_col].astype("string").str.replace(r"\.0$", "", regex=True).str.strip()
    fila = tabla[codigo.eq("162") | tabla[nombre_col].astype("string").str.contains("SAN SEBASTIAN", case=False, na=False)]
    if fila.empty:
        raise ValueError("No se encontró IP SAN SEBASTIAN / código 162 en el informe.")
    registro = fila.iloc[0]
    valores = []
    for columna in tabla.columns:
        texto = str(columna).strip()
        if texto.endswith(".0"):
            texto = texto[:-2]
        if texto.isdigit() and 2000 <= int(texto) <= 2030:
            valor = pd.to_numeric(registro[columna], errors="coerce")
            valores.append({"anio": int(texto), "tasa_informe_pct": valor * 100 if pd.notna(valor) and valor <= 1 else valor})
    resultado = pd.DataFrame(valores).sort_values("anio")
    resultado["hoja_informe"] = hoja
    resultado["fila_encabezado_0_based"] = encabezado
    logging.info("IPSS 162 encontrado en %s; años extraídos: %s", hoja, fmt_entero(len(resultado)))
    return resultado, inspeccion


def calcular_desde_original(csv: Path) -> pd.DataFrame:
    """Reconstruye tasas desde cohortes regulares del CSV original."""
    df = pd.read_csv(csv, dtype="string", encoding="utf-8-sig")
    df.columns = [col.strip().lower() for col in df.columns]
    df["cat_periodo"] = pd.to_numeric(df["cat_periodo"], errors="coerce")
    df["anio_ing_carr_act"] = pd.to_numeric(df["anio_ing_carr_act"], errors="coerce")
    df["mrun"] = df["mrun"].str.strip()
    df = df[df["mrun"].notna() & df["mrun"].ne("")]
    df = df[df["cod_inst"].astype("string").str.strip().eq("162")]
    salida = []
    for anio in sorted(df["cat_periodo"].dropna().unique()):
        cohorte = df[(df.cat_periodo == anio) & (df.anio_ing_carr_act == anio) & df.tipo_plan_carr.fillna("").str.casefold().eq("plan regular")]
        futuro = df[df.cat_periodo == anio + 1]
        if cohorte.empty or futuro.empty:
            continue
        cohorte = cohorte.drop_duplicates(["mrun", "cod_carrera", "codigo_unico"])
        futuro_keys = set(zip(futuro.mrun, futuro.cod_inst))
        cohorte_keys = cohorte[["mrun", "cod_inst"]].drop_duplicates()
        retenidos = sum((row.mrun, row.cod_inst) in futuro_keys for row in cohorte_keys.itertuples())
        n = len(cohorte_keys)
        salida.append({"anio": int(anio), "tamano_original_n": n, "retenidos_original": retenidos, "tasa_original_pct": 100 * retenidos / n})
    resultado = pd.DataFrame(salida)
    logging.info("Tasas reconstruidas desde original: %s años", fmt_entero(len(resultado)))
    return resultado


def exportar(informe: pd.DataFrame, original: pd.DataFrame, hojas: pd.DataFrame, ruta: Path) -> pd.DataFrame:
    conciliacion = informe.merge(original, on="anio", how="outer")
    conciliacion["diferencia_tasa_puntos"] = conciliacion["tasa_informe_pct"] - conciliacion["tasa_original_pct"]
    conciliacion["coincide_redondeo_2dp"] = conciliacion["diferencia_tasa_puntos"].abs().le(0.01)
    logging.info("Años conciliados: %s | coincidencias a 2 decimales: %s", fmt_entero(len(conciliacion)), fmt_entero(conciliacion.coincide_redondeo_2dp.sum()))
    informe_export = informe.copy()
    original_export = original.copy()
    conciliacion_export = conciliacion.copy()
    for frame in (informe_export, original_export, conciliacion_export):
        for col in frame.columns:
            if col == "anio" or col.startswith("fila_") or not pd.api.types.is_numeric_dtype(frame[col]):
                continue
            if frame[col].dtype == bool:
                continue
            frame[col] = frame[col].map(fmt_decimal if "tasa" in col or "diferencia" in col else fmt_entero)
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        conciliacion_export.to_excel(writer, sheet_name="Conciliacion_IPSS_162", index=False)
        informe_export.to_excel(writer, sheet_name="Tasas_Informe_Oficial", index=False)
        original_export.to_excel(writer, sheet_name="Tasas_CSV_Original", index=False)
        hojas.to_excel(writer, sheet_name="Inspeccion_Hojas", index=False)
    logging.info("Archivo escrito: %s", ruta)
    return conciliacion


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    if not INFORME.exists() or not CSV_ORIGINAL.exists():
        raise FileNotFoundError("Falta el informe Excel o el CSV original en el proyecto.")
    tasas_informe, hojas = extraer_ies(INFORME)
    tasas_original = calcular_desde_original(CSV_ORIGINAL)
    conciliacion = exportar(tasas_informe, tasas_original, hojas, SALIDA)
    logging.info("Conciliación completada; discrepancias de tasa: %s", fmt_entero((~conciliacion.coincide_redondeo_2dp).sum()))
    logging.info("Salida verificada en disco: %s bytes", fmt_entero(SALIDA.stat().st_size))


if __name__ == "__main__":
    main()
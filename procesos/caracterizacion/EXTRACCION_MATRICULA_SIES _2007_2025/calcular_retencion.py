#!/usr/bin/env python3
"""Calcula retención de primer año con la base histórica de matrícula SIES."""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SALIDA_DIR = BASE_DIR / "salida"
FUENTE = SALIDA_DIR / "reporte_matricula_ip_san_sebastian_ORIGINAL.csv"
REPORTE_INSTITUCIONAL = SALIDA_DIR / "retencion_institucional_2007_2024.csv"
REPORTE_CARRERA = SALIDA_DIR / "retencion_por_carrera_2007_2024.csv"
REPORTE_PROGRAMA = SALIDA_DIR / "retencion_por_codigo_unico_2007_2024.csv"


def cargar_base(ruta: Path) -> pd.DataFrame:
    """Lee la base, normaliza nombres y elimina MRUN nulos o vacios."""
    df = pd.read_csv(ruta, dtype="string", encoding="utf-8-sig")
    df.columns = [col.strip().lower() for col in df.columns]
    requeridas = {
        "cat_periodo",
        "mrun",
        "anio_ing_carr_act",
        "cod_inst",
        "nomb_inst",
        "cod_carrera",
        "nomb_carrera",
        "codigo_unico",
        "tipo_plan_carr",
    }
    faltantes = sorted(requeridas - set(df.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")

    for col in ("cat_periodo", "anio_ing_carr_act"):
        df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")

    df["mrun"] = df["mrun"].str.strip()
    return df[df["mrun"].notna() & df["mrun"].ne("")].copy()


def preparar_llaves(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Conserva una observacion por estudiante y llave analitica."""
    return df[["mrun", *columnas]].drop_duplicates()


def calcular_retencion(df: pd.DataFrame, nivel: str) -> pd.DataFrame:
    """Calcula cohortes T y matricula en T+1 sin duplicar MRUN por fuente."""
    resultados = []
    columnas_nivel = {
        "institucional": [],
        "carrera": ["cod_carrera", "nomb_carrera"],
        "programa": ["codigo_unico"],
    }[nivel]

    for anio in sorted(df["cat_periodo"].dropna().unique()):
        siguiente = anio + 1
        cohorte = df[
            (df["cat_periodo"] == anio)
            & (df["anio_ing_carr_act"] == anio)
            & df["tipo_plan_carr"].fillna("").str.casefold().eq("plan regular")
        ].copy()
        futuro = df[df["cat_periodo"] == siguiente].copy()
        if cohorte.empty or futuro.empty:
            continue

        if nivel == "institucional":
            cohorte_llaves = preparar_llaves(cohorte, [])
            futuro_llaves = preparar_llaves(futuro, [])
            futuro_llaves["retenido"] = True
            detalle = cohorte_llaves.merge(futuro_llaves, on="mrun", how="left")
            retenidos = int(detalle["retenido"].fillna(False).sum())
            resultados.append(
                pd.DataFrame(
                    [
                        {
                            "anio_cohorte": int(anio),
                            "anio_seguimiento": int(siguiente),
                            "nivel": nivel,
                            "tamano_cohorte": len(cohorte_llaves),
                            "retenidos": retenidos,
                            "tasa_retencion_pct": round(
                                100 * retenidos / len(cohorte_llaves), 2
                            ),
                        }
                    ]
                )
            )
            continue

        cohorte_llaves = preparar_llaves(cohorte, columnas_nivel)
        futuro_llaves = preparar_llaves(futuro, columnas_nivel)
        futuro_llaves["retenido"] = True
        detalle = cohorte_llaves.merge(
            futuro_llaves.assign(_en_siguiente=True),
            on=["mrun", *columnas_nivel],
            how="left",
        )
        detalle["retenido"] = detalle["_en_siguiente"].fillna(False)
        agrupadores = columnas_nivel
        resumen = (
            detalle.groupby(agrupadores, dropna=False, as_index=False)
            .agg(
                tamano_cohorte=("mrun", "nunique"),
                retenidos=("retenido", "sum"),
            )
        )
        resumen["anio_cohorte"] = int(anio)
        resumen["anio_seguimiento"] = int(siguiente)
        resumen["nivel"] = nivel
        resumen["tasa_retencion_pct"] = (
            100 * resumen["retenidos"] / resumen["tamano_cohorte"]
        ).round(2)
        resultados.append(resumen)

    if not resultados:
        return pd.DataFrame()
    return pd.concat(resultados, ignore_index=True)


def main() -> None:
    df = cargar_base(FUENTE)
    institucional = calcular_retencion(df, "institucional")
    carrera = calcular_retencion(df, "carrera")
    programa = calcular_retencion(df, "programa")
    institucional.to_csv(REPORTE_INSTITUCIONAL, index=False, encoding="utf-8-sig")
    carrera.to_csv(REPORTE_CARRERA, index=False, encoding="utf-8-sig")
    programa.to_csv(REPORTE_PROGRAMA, index=False, encoding="utf-8-sig")
    print(f"Base: {len(df):,} filas | MRUN: {df['mrun'].nunique():,}")
    print(f"Institucional: {len(institucional):,} periodos")
    print(f"Carrera: {len(carrera):,} filas")
    print(f"Programa: {len(programa):,} filas")


if __name__ == "__main__":
    main()
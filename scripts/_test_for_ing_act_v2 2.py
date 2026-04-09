#!/usr/bin/env python3
"""
Análisis FOR_ING_ACT v2 — usando SOLO columnas de DatosAlumnos:
  NOMBRE_L, ANOMATRICULA, PERIODOMATRICULA, ANOINGRESO, PERIODOINGRESO, NIVEL

Hipótesis: CONTINUIDAD en NOMBRE_L + NIVEL=1 → FOR_ING_ACT=11, todo lo demás → 1
"""
import pandas as pd

EXCEL = "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx"

xls = pd.ExcelFile(EXCEL)
da = pd.read_excel(xls, sheet_name="DatosAlumnos")
bd = pd.read_excel(xls, sheet_name="base_datos")

ruts_bd = set(bd["N_DOC"].dropna().astype(int))
da["_RUT_NUM"] = da["RUT"].str.extract(r"(\d+)", expand=False).astype(float).astype("Int64")
da_f = da[da["_RUT_NUM"].isin(ruts_bd)].copy()

print(f"Total alumnos filtrados (base_datos): {len(da_f)}")
print()

# -------------------------------------------------------------------
# 1) Columnas clave — distribución general
# -------------------------------------------------------------------
print("=" * 100)
print("1) DISTRIBUCIÓN DE COLUMNAS CLAVE")
print("=" * 100)
for c in ["ANOMATRICULA", "PERIODOMATRICULA", "ANOINGRESO", "PERIODOINGRESO", "NIVEL"]:
    print(f"\n  {c}:")
    print(f"  {da_f[c].value_counts().sort_index().to_dict()}")

da_f["ES_CONTINUIDAD"] = da_f["NOMBRE_L"].str.upper().str.contains("CONTINUIDAD", na=False)
print(f"\n  ES_CONTINUIDAD: True={da_f['ES_CONTINUIDAD'].sum()}, False={(~da_f['ES_CONTINUIDAD']).sum()}")

# -------------------------------------------------------------------
# 2) CONTINUIDAD: desglose por ANOINGRESO, PERIODOINGRESO, NIVEL
# -------------------------------------------------------------------
cont = da_f[da_f["ES_CONTINUIDAD"]].copy()
no_cont = da_f[~da_f["ES_CONTINUIDAD"]].copy()

print()
print("=" * 100)
print("2) CONTINUIDAD — desglose ANOINGRESO / PERIODOINGRESO / NIVEL")
print("=" * 100)

for nombre, g in cont.groupby("NOMBRE_L"):
    n = len(g)
    nuevos = g[(g["NIVEL"] == 1) & (g["ANOINGRESO"] == g["ANOMATRICULA"])]
    antiguos = g[~((g["NIVEL"] == 1) & (g["ANOINGRESO"] == g["ANOMATRICULA"]))]
    print(f"\n  {nombre}  ({n} alumnos)")
    print(f"    NUEVOS (NIVEL=1, ANOINGRESO=ANOMATRICULA): {len(nuevos)}")
    print(f"    ANTIGUOS (NIVEL>1 o ANOINGRESO<ANOMATRICULA): {len(antiguos)}")
    if len(antiguos) > 0:
        for _, r in antiguos.iterrows():
            print(f"      {r['CODCLI']:20s}  AMAT={r['ANOMATRICULA']} PMAT={r['PERIODOMATRICULA']} "
                  f"AING={r['ANOINGRESO']} PING={r['PERIODOINGRESO']} NIV={r['NIVEL']}")

# -------------------------------------------------------------------
# 3) NO-CONTINUIDAD: ¿hay alguno con NIVEL=1 pero ANOINGRESO ≠ ANOMATRICULA? (raro)
# -------------------------------------------------------------------
print()
print("=" * 100)
print("3) NO-CONTINUIDAD — NIVEL=1 con ANOINGRESO ≠ ANOMATRICULA (anomalías)")
print("=" * 100)

raros = no_cont[(no_cont["NIVEL"] == 1) & (no_cont["ANOINGRESO"] != no_cont["ANOMATRICULA"])]
print(f"\n  Encontrados: {len(raros)}")
if len(raros) > 0:
    for _, r in raros.iterrows():
        print(f"    {r['CODCLI']:20s} {r['NOMBRE_L']:45s} AMAT={r['ANOMATRICULA']} "
              f"AING={r['ANOINGRESO']} NIV={r['NIVEL']}")

# -------------------------------------------------------------------
# 4) NO-CONTINUIDAD: NIVEL > 1 (son ANTIGUOS que se rematriculan)
#    ¿Todos tienen ANOINGRESO < ANOMATRICULA?
# -------------------------------------------------------------------
print()
print("=" * 100)
print("4) NO-CONTINUIDAD — NIVEL > 1 (antiguos que rematriculan)")
print("=" * 100)

ant_nc = no_cont[no_cont["NIVEL"] > 1]
print(f"\n  Total: {len(ant_nc)}")
print(f"  ANOINGRESO < ANOMATRICULA: {(ant_nc['ANOINGRESO'] < ant_nc['ANOMATRICULA']).sum()}")
print(f"  ANOINGRESO == ANOMATRICULA: {(ant_nc['ANOINGRESO'] == ant_nc['ANOMATRICULA']).sum()}")
print(f"  NIVEL distribución: {ant_nc['NIVEL'].value_counts().sort_index().to_dict()}")
print(f"  ANOINGRESO distribución: {ant_nc['ANOINGRESO'].value_counts().sort_index().to_dict()}")

# Los que tienen ANOINGRESO == ANOMATRICULA Y NIVEL > 1 — ¿cómo?
raros2 = ant_nc[ant_nc["ANOINGRESO"] == ant_nc["ANOMATRICULA"]]
if len(raros2) > 0:
    print(f"\n  NIVEL > 1 pero ANOINGRESO == ANOMATRICULA: {len(raros2)} (convalidación/reconocimiento?)")
    for _, r in raros2.iterrows():
        print(f"    {r['CODCLI']:20s} {r['NOMBRE_L']:45s} AMAT={r['ANOMATRICULA']} "
              f"AING={r['ANOINGRESO']} NIV={r['NIVEL']}")

# -------------------------------------------------------------------
# 5) CONTINUIDAD con NIVEL > 1 — son ANTIGUOS del programa de continuidad
#    Ellos ingresaron a la continuidad en un año anterior y siguen
# -------------------------------------------------------------------
print()
print("=" * 100)
print("5) CONTINUIDAD con NIVEL > 1 (antiguos del programa continuidad)")
print("=" * 100)

cont_ant = cont[cont["NIVEL"] > 1]
print(f"\n  Total: {len(cont_ant)}")
if len(cont_ant) > 0:
    print(f"  NIVEL distribución: {cont_ant['NIVEL'].value_counts().sort_index().to_dict()}")
    print(f"  ANOINGRESO distribución: {cont_ant['ANOINGRESO'].value_counts().sort_index().to_dict()}")

# -------------------------------------------------------------------
# 6) CONCLUSIÓN: Clasificación propuesta
# -------------------------------------------------------------------
print()
print("=" * 100)
print("6) CLASIFICACIÓN FOR_ING_ACT PROPUESTA")
print("=" * 100)

def clasificar(row):
    """
    Solo usando DatosAlumnos: NOMBRE_L, NIVEL, ANOINGRESO, ANOMATRICULA
    """
    es_cont = "CONTINUIDAD" in str(row["NOMBRE_L"]).upper()
    if es_cont:
        return 11  # Articulación (continuidad TNS → ING)
    else:
        return 1   # Enseñanza media (default)

da_f["FOR_ING_ACT_CALC"] = da_f.apply(clasificar, axis=1)

print(f"\n  FOR_ING_ACT = 1  (Enseñanza Media):  {(da_f['FOR_ING_ACT_CALC'] == 1).sum()}")
print(f"  FOR_ING_ACT = 11 (Articulación):     {(da_f['FOR_ING_ACT_CALC'] == 11).sum()}")
print(f"  TOTAL:                                {len(da_f)}")

# ¿Qué pasa con los ANIO_ING_ACT y ANIO_ING_ORI?
print()
print("=" * 100)
print("7) IMPLICANCIAS PARA ANIO_ING_ACT / ANIO_ING_ORI")
print("=" * 100)

# Para código 11 (CONTINUIDAD):
#   ANIO_ING_ACT = ANOINGRESO (al programa de continuidad)
#   ANIO_ING_ORI = primer registro en Hoja1 como TNS (año original)
print(f"\n  Para FOR_ING_ACT=11 (CONTINUIDAD):")
print(f"    ANIO_ING_ACT = ANOINGRESO (del programa continuidad)")
print(f"    ANIO_ING_ORI = año de ingreso original al TNS (requiere Hoja1)")
print(f"    Ejemplo:")
for _, r in cont.head(5).iterrows():
    print(f"      {r['CODCLI']:20s} AING={r['ANOINGRESO']} → ANIO_ING_ACT={r['ANOINGRESO']}")

# Para código 1 (resto):
#   ANIO_ING_ACT = ANOINGRESO
#   ANIO_ING_ORI = ANOINGRESO (mismo, porque no han cambiado de forma de ingreso)
print(f"\n  Para FOR_ING_ACT=1 (todo lo demás):")
print(f"    ANIO_ING_ACT = ANOINGRESO")
print(f"    ANIO_ING_ORI = ANOINGRESO (misma temporalidad)")

# -------------------------------------------------------------------
# 8) RESUMEN TABULAR por programa
# -------------------------------------------------------------------
print()
print("=" * 100)
print("8) RESUMEN POR NOMBRE_L")
print("=" * 100)
print(f"\n  {'NOMBRE_L':55s} {'N':>5s} {'NIV1':>5s} {'NIV>1':>5s} {'CONT':>5s} {'AING_MIN':>8s} {'AING_MAX':>8s} {'FOR':>4s}")
print(f"  {'-'*55} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*8} {'-'*8} {'-'*4}")

for nombre, g in da_f.groupby("NOMBRE_L"):
    n = len(g)
    n1 = (g["NIVEL"] == 1).sum()
    n_gt1 = (g["NIVEL"] > 1).sum()
    es_c = "SI" if "CONTINUIDAD" in nombre.upper() else ""
    aing_min = g["ANOINGRESO"].min()
    aing_max = g["ANOINGRESO"].max()
    for_ing = 11 if "CONTINUIDAD" in nombre.upper() else 1
    print(f"  {nombre:55s} {n:5d} {n1:5d} {n_gt1:5d} {es_c:>5s} {aing_min:8d} {aing_max:8d} {for_ing:4d}")

print()
print("TOTAL:", len(da_f))

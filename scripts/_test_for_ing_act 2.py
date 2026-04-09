#!/usr/bin/env python3
"""Test clasificación FOR_ING_ACT según manual MU 2026 cruzando DatosAlumnos + Hoja1."""
import pandas as pd
import sys

INPUT = "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx"

print("Leyendo Excel...", flush=True)
xls = pd.ExcelFile(INPUT)
da = pd.read_excel(xls, sheet_name="DatosAlumnos")
bd = pd.read_excel(xls, sheet_name="base_datos")
h1 = pd.read_excel(xls, sheet_name="Hoja1", usecols=["CODCLI", "RUT", "CODCARR", "ANO"])
print(f"Leídos: DA={len(da)}, H1={len(h1)}, BD={len(bd)}", flush=True)

ruts_bd = set(bd["N_DOC"].dropna().astype(int))
da["_RUT_NUM"] = da["RUT"].str.extract(r"(\d+)", expand=False).astype(float).astype("Int64")
da_filt = da[da["_RUT_NUM"].isin(ruts_bd)].copy()

h1["_RUT_NUM"] = h1["RUT"].astype(str).str.extract(r"(\d+)", expand=False).astype(float).astype("Int64")
h1_filt = h1[h1["_RUT_NUM"].isin(ruts_bd)]

# Historial por RUT
hist = {}
for rut, g in h1_filt.groupby("_RUT_NUM"):
    hist[rut] = {
        "carreras": set(g["CODCARR"].dropna().unique()),
        "anio_min": int(g["ANO"].min()),
    }

print(f"Alumnos filtrados: {len(da_filt)} | Historial: {len(hist)} RUTs", flush=True)


def es_continuidad(nombre_l):
    if pd.isna(nombre_l):
        return False
    return "CONTINUIDAD" in str(nombre_l).upper()


def es_extranjero_via(viasadm):
    if pd.isna(viasadm):
        return False
    return str(viasadm).upper().strip() == "EXTRANJERO"


def nac_no_chilena(nac):
    if pd.isna(nac):
        return False
    n = str(nac).upper().strip()
    return n not in ("CHILENA", "CHILE", "")


def es_cambio_carrera_sit(situacion):
    if pd.isna(situacion):
        return False
    return "24" in str(situacion)


def tiene_uni_externa(nombre_uni):
    if pd.isna(nombre_uni):
        return False
    n = str(nombre_uni).upper().strip()
    return n != "" and "IPSS" not in n and "CIISA" not in n and n != "NAN"


results = []
for _, row in da_filt.iterrows():
    rut = row["_RUT_NUM"]
    codcli = row["CODCLI"]
    codcarpr = row["CODCARPR"]
    nombre_l = row["NOMBRE_L"]
    anio_ing = row["ANOINGRESO"]
    viasadm = row["VIASDEADMISION"]
    situacion = row["SITUACION"]
    nac = row["NACIONALIDAD"]
    nombre_uni = row.get("NOMBREUNIVERSIDAD", None)
    carrera_ant = row.get("CARRERARANTERIOR", None)

    h = hist.get(rut, {"carreras": set(), "anio_min": anio_ing})
    carreras_hist = h["carreras"]
    anio_mas_antiguo = h["anio_min"]
    n_carreras = len(carreras_hist)

    # ---- REGLAS MANUAL MU 2026 ----

    # R11: Articulación TNS->profesional (CONTINUIDAD en nombre)
    if es_continuidad(nombre_l):
        for_ing = 11
        met = "R11_CONTINUIDAD_NOMBRE_L"
        anio_ori = anio_mas_antiguo if anio_mas_antiguo < anio_ing else 1900

    # R6: Ingreso especial extranjero
    elif es_extranjero_via(viasadm) and nac_no_chilena(nac):
        for_ing = 6
        met = "R6_VIASADM_EXTRANJERO"
        anio_ori = anio_ing

    # R4: Cambio Externo (universidad anterior externa)
    elif tiene_uni_externa(nombre_uni):
        for_ing = 4
        met = "R4_UNI_ANTERIOR_EXTERNA"
        anio_ori = 1900

    # R3: Cambio Interno (SITUACION=24 cambio carrera)
    elif es_cambio_carrera_sit(situacion):
        for_ing = 3
        met = "R3_SITUACION_24_CAMBIO"
        anio_ori = anio_mas_antiguo if anio_mas_antiguo < anio_ing else anio_ing

    # R3 alt: múltiples carreras en historial Hoja1
    elif n_carreras > 1:
        for_ing = 3
        met = "R3_HISTORIAL_MULTI_CARRERA"
        anio_ori = anio_mas_antiguo if anio_mas_antiguo < anio_ing else anio_ing

    # R10: Educación Continua (no continuidad)
    elif str(viasadm).upper().strip() == "PROGRAMA DE EDUCACION CONTINUA":
        for_ing = 10
        met = "R10_VIASADM_EDUC_CONTINUA"
        anio_ori = anio_ing

    # R1: default - Ingreso Directo
    else:
        for_ing = 1
        met = "R1_INGRESO_DIRECTO"
        anio_ori = anio_ing

    results.append(
        {
            "CODCLI": codcli,
            "CODCARPR": codcarpr,
            "NOMBRE_L": nombre_l,
            "ANOINGRESO": anio_ing,
            "VIASADM": viasadm,
            "SITUACION": situacion,
            "NAC": nac,
            "UNI_ANT": nombre_uni,
            "CARRERA_ANT": carrera_ant,
            "N_CARRERAS_HIST": n_carreras,
            "FOR_ING_ACT": for_ing,
            "ANIO_ING_ORI": anio_ori,
            "METODO": met,
        }
    )

df_r = pd.DataFrame(results)

print()
print("=" * 80)
print(f"CLASIFICACION FOR_ING_ACT — {len(df_r)} alumnos base_datos")
print("=" * 80)
print()
print("=== Distribucion FOR_ING_ACT propuesto ===")
vc = df_r["FOR_ING_ACT"].value_counts().sort_index()
for k, v in vc.items():
    pct = v / len(df_r) * 100
    print(f"  {k:2d} -> {v:5d}  ({pct:5.1f}%)")
print()
print("=== Metodo de clasificacion ===")
print(df_r["METODO"].value_counts().to_string())
print()

# Detalle NO-1
no1 = df_r[df_r["FOR_ING_ACT"] != 1]
print(f"=== {len(no1)} registros con FOR_ING_ACT != 1 ===")
print()

for cod in sorted(no1["FOR_ING_ACT"].unique()):
    sub = no1[no1["FOR_ING_ACT"] == cod]
    print(f"--- FOR_ING_ACT = {cod} ({len(sub)} registros) ---")
    display = sub[
        [
            "CODCLI",
            "NOMBRE_L",
            "ANOINGRESO",
            "ANIO_ING_ORI",
            "VIASADM",
            "NAC",
            "UNI_ANT",
            "SITUACION",
            "METODO",
        ]
    ].copy()
    display["NOMBRE_L"] = display["NOMBRE_L"].str[:40]
    display["UNI_ANT"] = display["UNI_ANT"].fillna("").astype(str).str[:25]
    display["SITUACION"] = display["SITUACION"].astype(str).str[:30]
    display["NAC"] = display["NAC"].astype(str).str[:12]
    print(display.head(15).to_string(index=False))
    print()

# Validaciones Cruzadas
print("=" * 80)
print("VALIDACIONES CRUZADAS (reglas relacionales del manual)")
print("=" * 80)
print()

# V1: R11 continuidad: ANIO_ORI < ANIO_ACT (o 1900)
r11 = df_r[df_r["FOR_ING_ACT"] == 11]
r11_lt = (r11["ANIO_ING_ORI"] < r11["ANOINGRESO"]).sum()
r11_1900 = (r11["ANIO_ING_ORI"] == 1900).sum()
r11_eq = (r11["ANIO_ING_ORI"] == r11["ANOINGRESO"]).sum()
print(f"R11 continuidad: {len(r11)} alumnos")
print(f"  ANIO_ORI < ANIO_ACT: {r11_lt} | ANIO_ORI=1900: {r11_1900} | ANIO_ORI==ANIO_ACT: {r11_eq}")
print()

# V2: R3 cambio interno: ANIO_ACT > ANIO_ORI
r3 = df_r[df_r["FOR_ING_ACT"] == 3]
r3_gt = (r3["ANOINGRESO"] > r3["ANIO_ING_ORI"]).sum()
r3_eq = (r3["ANOINGRESO"] == r3["ANIO_ING_ORI"]).sum()
print(f"R3 cambio interno: {len(r3)} alumnos")
print(f"  ANIO_ACT > ANIO_ORI: {r3_gt} | ANIO_ACT == ANIO_ORI: {r3_eq}")
if r3_eq > 0:
    eq_sample = r3[r3["ANOINGRESO"] == r3["ANIO_ING_ORI"]]
    print("  ALERTA: cambios internos con ANIO_ACT==ANIO_ORI:")
    print(
        eq_sample[["CODCLI", "NOMBRE_L", "ANOINGRESO", "ANIO_ING_ORI", "SITUACION", "METODO"]]
        .head(5)
        .to_string(index=False)
    )
print()

# V3: R4 cambio externo: ANIO_ORI = 1900
r4 = df_r[df_r["FOR_ING_ACT"] == 4]
r4_ok = (r4["ANIO_ING_ORI"] == 1900).sum()
print(f"R4 cambio externo: {len(r4)} alumnos")
print(f"  ANIO_ORI = 1900: {r4_ok}/{len(r4)}")
print()

# V4: R6 extranjero: ANIO_ORI == ANIO_ACT
r6 = df_r[df_r["FOR_ING_ACT"] == 6]
r6_ok = (r6["ANIO_ING_ORI"] == r6["ANOINGRESO"]).sum()
print(f"R6 extranjero: {len(r6)} alumnos")
print(f"  ANIO_ORI == ANIO_ACT: {r6_ok}/{len(r6)}")
print()

# V5: R1 ingreso directo: ANIO_ORI == ANIO_ACT
r1 = df_r[df_r["FOR_ING_ACT"] == 1]
r1_ok = (r1["ANIO_ING_ORI"] == r1["ANOINGRESO"]).sum()
print(f"R1 ingreso directo: {len(r1)} alumnos")
print(f"  ANIO_ORI == ANIO_ACT: {r1_ok}/{len(r1)}")
print()

# RESUMEN COMPARATIVO: actual (todo=1) vs propuesto
print("=" * 80)
print("RESUMEN COMPARATIVO: actual (todo=1) vs propuesto")
print("=" * 80)
print(f"  Actual:   FOR_ING_ACT=1 para 100% ({len(df_r)} alumnos)")
print(f"  Propuesto:")
for k, v in vc.items():
    pct = v / len(df_r) * 100
    lbl = {1: "Ingreso Directo", 3: "Cambio Interno", 4: "Cambio Externo",
           6: "Extranjero", 10: "Otras (Educ.Continua)", 11: "Articulacion TNS"}
    print(f"    {k:2d} {lbl.get(k,'?'):30s} -> {v:5d}  ({pct:5.1f}%)")
print(f"  Total afectados: {len(no1)} ({len(no1)/len(df_r)*100:.1f}%) recibirían código distinto de 1")

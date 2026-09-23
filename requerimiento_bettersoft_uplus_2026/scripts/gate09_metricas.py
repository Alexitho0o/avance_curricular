"""Gate 09: recalcula desde las fuentes las métricas agregadas que respaldan cada resolución.

Solo escribe conteos agregados (sin RUT, nombres ni valores individuales) en
resultados/gate09/METRICAS_EVIDENCIA_GATE09.json.

Fuentes (ver 01_fuentes_oficiales/MANIFIESTO_FUENTES_GATE09.tsv):
- Archivos cargados en PES MU 2026 (08-05 y 11-05, copias _orig) en .local_restricted.
- Respuesta de errores PES 07-05-2026 12:19 en .local_restricted.
- Snapshot U+ del 08-05-2026 (PROMEDIOSDEALUMNOS_7804.xlsx, hoja DatosAlumnos).
- Base MU informada 2022-2026 (outputs/base_retencion_matricula_unificada_2022_2026).
- PUENTE_SIES_COMPILADO.tsv, plantillas PES de Oferta y contrato Etapa 1.
- Archivo enviado Extranjeros Regulares 1ª carga.
"""
import argparse
import collections
import io
import json
import re
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SUB = REPO / "requerimiento_bettersoft_uplus_2026"
RES = REPO / ".local_restricted" / "requerimiento_bettersoft_uplus_2026" / "gate09_evidencia"
MU_COLS = ("TIPO_DOC N_DOC DV PRIMER_APELLIDO SEGUNDO_APELLIDO NOMBRE SEXO FECH_NAC NAC PAIS_EST_SEC COD_SED COD_CAR "
           "MODALIDAD JOR VERSION FOR_ING_ACT ANIO_ING_ACT SEM_ING_ACT ANIO_ING_ORI SEM_ING_ORI ASI_INS_ANT ASI_APR_ANT "
           "PROM_PRI_SEM PROM_SEG_SEM ASI_INS_HIS ASI_APR_HIS NIV_ACA SIT_FON_SOL SUS_PRE FECHA_MATRICULA "
           "REINCORPORACION VIG").split()
EXT_COLS = ("TIPO_DOCUMENTO NUM_DOCUMENTO DV PRIMER_APELLIDO SEGUNDO_APELLIDO NOMBRES SEXO FECHA_NACIMIENTO NACIONALIDAD "
            "TIPO_RESIDENCIA_ESTUDIANTE PAIS_ORIGEN PAIS_ESTUDIOS_SECUNDARIOS CODIGO_UNICO ANIO_INGRESO_CARRERA_ACTUAL "
            "SEM_INGRESO_CARRERA_ACTUAL ANIO_INGRESO_CARRERA_ORIGEN SEM_INGRESO_CARRERA_ORIGEN NOMBRE_UNIVERSIDAD_ORIGEN "
            "PAIS_UNIVERSIDAD_ORIGEN VIGENCIA").split()


def leer_csv(data, cols):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            d = pd.read_csv(io.BytesIO(data), sep=";", header=None, dtype=str, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if d.iloc[0].tolist()[: len(cols)] == cols[: d.shape[1]]:
        d = d.iloc[1:]
    d.columns = cols[: d.shape[1]]
    return d.apply(lambda s: s.str.strip())


def leer_zip(p):
    with zipfile.ZipFile(p) as z:
        return leer_csv(z.read(z.namelist()[0]), MU_COLS)


def conteo(s):
    return {str(k): int(v) for k, v in s.value_counts(dropna=False).items()}


def rut(s):
    return s.astype(str).str.split("-").str[0].str.replace(".", "", regex=False).str.strip()


def main(prom7804: Path) -> None:
    mu = RES / "matricula_unificada_2026"
    a = leer_zip(mu / "08-05-2026_23-21-16_Matrícula-Pregrado-2026.csv_orig.zip")
    b = leer_zip(mu / "11-05-2026_12-12-47_Matrícula-Pregrado-2026.csv_orig.zip")
    pes = pd.concat([a, b], ignore_index=True)
    pes["RUTN"] = pes.N_DOC
    m = {"pes_mu2026": {"filas_08_05": len(a), "filas_11_05": len(b), "filas_total": len(pes)}}
    for c in ["SEXO", "PAIS_EST_SEC", "JOR", "MODALIDAD", "FOR_ING_ACT", "SIT_FON_SOL", "SUS_PRE", "REINCORPORACION", "VIG"]:
        m["pes_mu2026"][c] = conteo(pes[c])
    m["pes_mu2026"]["NAC_distinta_38"] = int((pes.NAC != "38").sum())
    m["pes_mu2026"]["FECH_NAC_1900"] = int(pes.FECH_NAC.str.contains("1900", na=False).sum())
    f2 = pes[pes.FOR_ING_ACT == "2"]
    m["pes_mu2026"]["FOR2_ANIO_ORI_1900"] = int((f2.ANIO_ING_ORI == "1900").sum())
    m["pes_mu2026"]["JOR_x_MODALIDAD"] = {f"{j}|{mo}": int(n) for (j, mo), n in pes.groupby(["JOR", "MODALIDAD"]).size().items()}

    # Respuesta de errores PES 07-05-2026
    log = (mu / "07-05-2026_12-19-13_Matrícula-Pregrado-2026.csv.txt").read_text(encoding="utf-8", errors="replace")
    msgs = collections.Counter(l.strip() for l in log.splitlines() if l.startswith("\t"))
    m["pes_errores_07_05"] = {k: v for k, v in msgs.items() if "FONDO SOLIDARIO" in k or "1900" in k}

    # Snapshot U+ del 08-05-2026
    u = pd.read_excel(prom7804, sheet_name="DatosAlumnos", dtype=str)
    u["RUTN"] = rut(u.RUT)
    u["JOR_U"] = u.JORNADA.str.strip()
    u["SIT_COD"] = u.SITUACION.str.split(" - ").str[0].str.strip()
    solo_tit = u.groupby("RUTN").ESTADOACADEMICO.agg(lambda s: set(s) == {"TITULADO"})
    tit = u[u.ESTADOACADEMICO == "TITULADO"]
    m["uplus_0508"] = {
        "filas": len(u), "SEXO": conteo(u.SEXO), "ESTADOACADEMICO": conteo(u.ESTADOACADEMICO),
        "JORNADA_raw": conteo(u.JORNADA), "PERIODOMATRICULA": conteo(u.PERIODOMATRICULA),
        "VIASDEADMISION": conteo(u.VIASDEADMISION.str.replace("\xa0", " ").str.split().str.join(" ")),
        "NACIONALIDAD_por_definir": int((u.NACIONALIDAD == "Por definir").sum()),
    }
    m["ct01"] = {
        "filas_pes_rut_con_fila_titulado": int(pes.RUTN.isin(set(tit.RUTN)).sum()),
        "vig_pes_rut_con_fila_titulado": conteo(pes[pes.RUTN.isin(set(tit.RUTN))].VIG),
        "filas_pes_rut_solo_titulado": int(pes.RUTN.isin(set(solo_tit[solo_tit].index)).sum()),
        "titulado_anomatricula": conteo(tit.ANOMATRICULA),
        "egresado_filas": int((u.ESTADOACADEMICO == "EGRESADO").sum()),
    }
    cj = u[u.SIT_COD.isin(["49", "27"])]
    f3 = pes[pes.FOR_ING_ACT == "3"]
    sit_f3 = collections.Counter()
    for r in f3.RUTN:
        sit_f3.update(set(u.loc[u.RUTN == r, "SIT_COD"]))
    m["ct02"] = {"uplus_sit_49_27": len(cj), "pes_for_rut_sit_49_27": conteo(pes[pes.RUTN.isin(set(cj.RUTN))].FOR_ING_ACT),
                 "pes_for3": len(f3), "situaciones_uplus_de_for3": dict(sit_f3.most_common())}
    co = u[u.NOMBRE_L.str.upper().str.contains("CONTINUIDAD", na=False)]
    m["ct03"] = {"uplus_filas_continuidad": len(co), "programas_continuidad": int(co.NOMBRE_L.nunique()),
                 "pes_for2": len(f2), "pes_for2_rut_con_programa_continuidad": int(f2.RUTN.isin(set(co.RUTN)).sum()),
                 "continuidad_categoria": conteo(co.CATEGORIA),
                 "continuidad_carrera_anterior_informada": round(float(co.CARRERARANTERIOR.notna().mean()), 3),
                 "continuidad_institucion_anterior_informada": round(float(co.NOMBREUNIVERSIDAD.notna().mean()), 3)}
    # Pares inequívocos (1 fila U+ año 2026 y 1 fila PES por RUT) para cruces
    u26 = u[u.ANOMATRICULA == "2026"]
    one = u26.groupby("RUTN").filter(lambda g: len(g) == 1)
    ps = pes.groupby("RUTN").filter(lambda g: len(g) == 1)
    pr = ps.merge(one, on="RUTN", suffixes=("", "_U"))
    m["cruces"] = {
        "pares_inequivocos": len(pr),
        "SEXO_uplus_x_pes": {f"{a}|{b}": int(n) for (a, b), n in pr.groupby(["SEXO_U", "SEXO"]).size().items()},
        "SEDE_uplus_x_pes": {f"{a}|{b}": int(n) for (a, b), n in pr.groupby(["SEDE", "COD_SED"]).size().items()},
        "JORNADA_uplus_x_pes": {f"{a}|{b}": int(n) for (a, b), n in pr.groupby(["JOR_U", "JOR"]).size().items()},
        "JORNADA_O_a_2_situacion": conteo(pr[(pr.JOR_U == "O") & (pr.JOR == "2")].SIT_COD),
        "NACIONALIDAD_valores_con_mas_de_un_codigo": int((pr.groupby("NACIONALIDAD").NAC.nunique() > 1).sum()),
        "NACIONALIDAD_valores": int(pr.NACIONALIDAD.nunique()),
        "NACIONALIDAD_por_definir_a_38": int(((pr.NACIONALIDAD == "Por definir") & (pr.NAC == "38")).sum()),
    }
    sx = pes[pes.SEXO == "NB"]
    m["ct04"] = {"uplus_S_filas": int((u.SEXO == "S").sum()), "uplus_S_rut": int(u[u.SEXO == "S"].RUTN.nunique()),
                 "pes_NB": len(sx), "pes_NB_con_uplus_S": int(sum(set(u.loc[u.RUTN == r, "SEXO"]) == {"S"} for r in sx.RUTN))}
    for c in ["PROM_PRI_SEM", "PROM_SEG_SEM"]:
        v = pd.to_numeric(pes[c], errors="coerce")
        m.setdefault("escala_notas", {})[c] = {"0": int((v == 0).sum()), "100_700": int(v.between(100, 700).sum()),
                                               "fuera_rango": int((~((v == 0) | v.between(100, 700))).sum())}

    # MU informada 2022-2026
    base = next((REPO / "outputs/base_retencion_matricula_unificada_2022_2026").glob("20260901_142342/BASE_*.xlsx"))
    h = pd.read_excel(base, dtype=str).apply(lambda s: s.str.replace(r"\.0$", "", regex=True).str.strip())
    h["ANIO"] = h.ANIO_INFORMADO.str[:4]
    m["historico"] = {}
    for y, g in h.groupby("ANIO"):
        m["historico"][y] = {"filas": len(g), "FOR_ING_ACT": conteo(g.FOR_ING_ACT), "VIG": conteo(g.VIG),
                             "SIT_FON_SOL": conteo(g.SIT_FON_SOL), "SUS_PRE_distinto_0": int((g.SUS_PRE != "0").sum()),
                             "PAIS_EST_SEC_38": int((g.PAIS_EST_SEC == "38").sum()), "NAC_distinta_38": int((g.NAC != "38").sum()),
                             "PAIS_igual_NAC_entre_extranjeros": int(((g.PAIS_EST_SEC == g.NAC) & (g.NAC != "38")).sum()),
                             "JOR_x_MODALIDAD": {f"{j}|{mo}": int(n) for (j, mo), n in g.groupby(["JOR", "MODALIDAD"]).size().items()}}
    h25 = h[h.ANIO == "2025"]
    comp3 = collections.Counter()
    for _, r in pes[pes.FOR_ING_ACT == "3"].iterrows():
        p = h25[h25.N_DOC == r.N_DOC]
        if p.empty:
            comp3["sin_registro_MU2025"] += 1
        elif (p.COD_CAR == r.COD_CAR).any():
            q = p[p.COD_CAR == r.COD_CAR]
            comp3["mismo_COD_CAR_" + ("distinta_JOR" if (q.JOR != r.JOR).all() else "misma_JOR")] += 1
            comp3["for_2025_" + q.FOR_ING_ACT.iloc[0]] += 1
        else:
            comp3["distinto_COD_CAR"] += 1
    comp2 = collections.Counter()
    for _, r in f2.iterrows():
        p = h25[(h25.N_DOC == r.N_DOC) & (h25.COD_CAR == r.COD_CAR)]
        comp2["sin_mismo_programa_MU2025" if p.empty else "for_2025_" + p.FOR_ING_ACT.iloc[0]] += 1
    car2 = set(f2.COD_CAR)
    m["ct02"]["for3_2026_vs_mu2025"] = dict(comp3)
    m["ct03"]["for2_2026_vs_mu2025"] = dict(comp2)
    m["ct03"]["cod_car_for2_2026"] = len(car2)
    m["ct03"]["cod_car_for2_2026_con_for11_2026"] = len(car2 & set(pes[pes.FOR_ING_ACT == "11"].COD_CAR))

    # PUENTE: componentes del código único por jornada U+
    pu = pd.read_csv(REPO / "control/catalogos/PUENTE_SIES_COMPILADO.tsv", sep="\t", dtype=str).fillna("")
    comp = lambda s: re.findall(r"I162S(\d+)C(\d+)J(\d+)V(\d+)", s)
    filas = []
    for _, r in pu.iterrows():
        cs = comp(r.CODIGOS_SIES_POTENCIALES + " " + r.CODIGO_UNICO_FINAL)
        filas.append({"JOR": r.JORNADA, "n": len(set(cs)), **{k: len({c[i] for c in cs}) for i, k in enumerate("SCJV")},
                      "J_codes": sorted({c[2] for c in cs})})
    d = pd.DataFrame(filas)
    amb = d[d.n > 1]
    m["puente"] = {"combinaciones": len(d), "ambiguas": len(amb),
                   "ambiguas_difieren_en": {k: int((amb[k] > 1).sum()) for k in "SCJV"},
                   "J_por_jornada_uplus": {j: dict(collections.Counter(x for s in g.J_codes for x in s)) for j, g in d.groupby("JOR")}}

    # Oferta: plantilla PES vs contrato
    tpl = (SUB / "01_fuentes_oficiales/oferta_academica_2027/20260810_34992_Estructura_OA_1_TP_VIGENTE_EDITADA.csv")
    cols_tpl = tpl.read_text(encoding="utf-8-sig").strip().split(";")
    ctr = pd.read_csv(REPO / "oferta_academica_2027/11_gobernanza/CONTRATO_CAMPOS_ETAPA1_OFERTA_ACADEMICA_2027.tsv", sep="\t", dtype=str)
    m["oferta"] = {"columnas_plantilla_pes": len(cols_tpl), "delimitador_plantilla": ";", "campos_contrato": len(ctr),
                   "campos_contrato_fuera_de_plantilla": sorted(set(ctr.campo) - set(cols_tpl))}

    # Extranjeros 1ª carga
    ext = leer_csv((RES / "estudiantes_extranjeros_2026/EXTRANJEROS_REGULARES_2025_PES_READY_RESIDENCIA_0_20260626_121728.csv").read_bytes(), EXT_COLS)
    m["extranjeros_1a_carga"] = {"filas": len(ext), "SEXO": conteo(ext.SEXO), "VIGENCIA": conteo(ext.VIGENCIA),
                                 "TIPO_RESIDENCIA": conteo(ext.TIPO_RESIDENCIA_ESTUDIANTE),
                                 "PAIS_EST_SEC_igual_NAC": int((ext.PAIS_ESTUDIOS_SECUNDARIOS == ext.NACIONALIDAD).sum()),
                                 "PAIS_EST_SEC_38": int((ext.PAIS_ESTUDIOS_SECUNDARIOS == "38").sum())}

    out = SUB / "resultados/gate09/METRICAS_EVIDENCIA_GATE09.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prom7804", type=Path, required=True, help="PROMEDIOSDEALUMNOS_7804.xlsx usado en la carga MU 2026")
    main(ap.parse_args().prom7804)

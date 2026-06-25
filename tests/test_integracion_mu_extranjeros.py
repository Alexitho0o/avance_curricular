from pathlib import Path

import pandas as pd

ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")


def test_puente_sin_duplicados_si_existe():
    path = ROOT / "resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026.tsv"
    if not path.exists():
        return
    df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    key = ["CODCLI", "CODCARPR", "PLAN_DE_ESTUDIO", "COD_SED", "JOR", "MODALIDAD"]
    assert not df.duplicated(key).any()
    assert not ((df["ES_APTO_PARA_EXTRANJEROS"].eq("SI")) & df["CODIGO_UNICO"].eq("")).any()


def test_extranjeros_v7_codigos_criticos_si_existe():
    path = ROOT / "estudiantes_extranjeros_2026/data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V7.csv"
    if not path.exists():
        return
    df = pd.read_csv(path, dtype=str).fillna("")
    assert len(df) == 61
    assert df.loc[df["CODCLI"].eq("20251IINF072"), "CODIGO_UNICO_PROPUESTO"].iloc[0] == "I162S2C1J2V4"
    assert df.loc[df["CODCLI"].eq("20251AUDT004"), "CODIGO_UNICO_PROPUESTO"].iloc[0] == "I162S2C86J4V1"
    icre = df[df["CODCLI"].eq("20241ICRE068")].iloc[0]
    assert icre["CODIGO_UNICO_PROPUESTO"] == ""
    assert icre["CODIGO_UNICO_ESTADO"] == "PENDIENTE_INSTITUCIONAL"


def test_extranjeros_v8_cierra_icre068_si_existe():
    path = ROOT / "estudiantes_extranjeros_2026/data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V8.csv"
    if not path.exists():
        return
    df = pd.read_csv(path, dtype=str).fillna("")
    assert len(df) == 61
    counts = df["ESTADO_GLOBAL_REGISTRO"].value_counts().to_dict()
    assert counts.get("APTO", 0) == 56
    assert counts.get("APTO_CON_ADVERTENCIAS", 0) == 5
    assert counts.get("PENDIENTE_INSTITUCIONAL", 0) == 0
    assert df.loc[df["CODCLI"].eq("20251IINF072"), "CODIGO_UNICO_PROPUESTO"].iloc[0] == "I162S2C1J2V4"
    assert df.loc[df["CODCLI"].eq("20251AUDT004"), "CODIGO_UNICO_PROPUESTO"].iloc[0] == "I162S2C86J4V1"
    icre = df[df["CODCLI"].eq("20241ICRE068")].iloc[0]
    assert icre["CODIGO_UNICO_PROPUESTO"] == "I162S2C3J2V4"
    assert icre["CODIGO_UNICO_ESTADO"] == "VALIDADO_DECISION_INSTITUCIONAL"
    assert icre["ID_RESOLUCION_INSTITUCIONAL"] == "EXT-ICRE068-2026-002"


def test_puente_v2_icre068_resuelto_si_existe():
    path = ROOT / "resultados/puentes/PUENTE_MU_EXTRANJEROS_CODIGOS_SIES_2026_V2.tsv"
    if not path.exists():
        return
    df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    row = df[df["CODCLI"].eq("20241ICRE068")]
    assert len(row) == 1
    row = row.iloc[0]
    assert row["CODIGO_UNICO"] == "I162S2C3J2V4"
    assert row["ID_RESOLUCION_INSTITUCIONAL"] == "EXT-ICRE068-2026-002"
    assert row["ES_APTO_PARA_EXTRANJEROS"] == "SI"
    assert row["REQUIERE_REVISION"] == "NO"

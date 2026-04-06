#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


RULES = {
    ("INGENIERIA EN CIBERSEGURIDAD", "D"): ("I162S2C46J1V1", "A"),
    ("INGENIERIA EN CIBERSEGURIDAD", "V"): ("I162S2C46J2V1", "B"),
    ("CONTINUIDAD INGENIERIA CIBERSEGURIDAD", "V"): ("I162S2C46J2V3", "C"),
    ("CONTINUIDAD INGENIERIA CIBERSEGURIDAD", "O"): ("I162S2C46J4V1", "D"),
    ("INGENIERIA EN CIBERSEGURIDAD", "O"): ("I162S2C46J4V3", "E"),
}


BASE_COLS = [
    "CODCLI",
    "N_DOC",
    "DV",
    "NOMBRE_CARRERA_FUENTE",
    "JORNADA_FUENTE",
    "CODCARPR_NORM",
    "SOURCE_KEY_3",
    "KEY_3_NO_JORNADA",
    "CODIGOS_SIES_POTENCIALES",
    "N_CODES_SIES",
    "CODIGO_CARRERA_SIES_FINAL",
    "SIES_MATCH_STATUS",
    "SIES_MATCH_DIAG",
    "SIES_RESOLUCION_HEURISTICA",
]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


def load_archivo_subida(xlsx_path: Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path, sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str)
    for col in BASE_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def build_universe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["NOMBRE_NORM"] = out["NOMBRE_CARRERA_FUENTE"].map(normalize_text)
    out["JORNADA_NORM"] = out["JORNADA_FUENTE"].fillna("").astype(str).str.strip().str.upper()
    out["CODCARPR_NORM"] = out["CODCARPR_NORM"].map(normalize_text)
    out["RUT"] = (
        out["N_DOC"].fillna("").astype(str).str.replace(r"\D", "", regex=True)
        + "-"
        + out["DV"].fillna("").astype(str).str.strip().str.upper()
    )
    out["CODIGO_ESPERADO"] = out.apply(
        lambda r: RULES.get((r["NOMBRE_NORM"], r["JORNADA_NORM"]), (pd.NA, pd.NA))[0], axis=1
    )
    out["REGLA_A_E"] = out.apply(
        lambda r: RULES.get((r["NOMBRE_NORM"], r["JORNADA_NORM"]), (pd.NA, pd.NA))[1], axis=1
    )
    out = out[out["CODIGO_ESPERADO"].notna()].copy()
    out["AUDIT_KEY"] = (
        out["CODCLI"].fillna("").astype(str).str.strip()
        + "|"
        + out["N_DOC"].fillna("").astype(str).str.strip()
        + "|"
        + out["DV"].fillna("").astype(str).str.strip().str.upper()
        + "|"
        + out["SOURCE_KEY_3"].fillna("").astype(str).str.strip()
    )
    out["SEQ_KEY"] = out.groupby("AUDIT_KEY", dropna=False).cumcount()
    return out


def classify_cause(row: pd.Series) -> str:
    codcarpr = str(row.get("CODCARPR_NORM", "") or "").strip()
    diag = str(row.get("SIES_MATCH_DIAG", "") or "").upper()
    status = str(row.get("SIES_MATCH_STATUS", "") or "").upper()
    final_code = str(row.get("CODIGO_CARRERA_SIES_FINAL", "") or "").strip().upper()
    expected = str(row.get("CODIGO_ESPERADO", "") or "").strip().upper()
    n_codes = pd.to_numeric(pd.Series([row.get("N_CODES_SIES")]), errors="coerce").iloc[0]

    if not codcarpr:
        return "BLOQUEANTE_CODCARPR_NORM_VACIO"
    if "PROBABLE_PROBLEMA_" in diag:
        return "PROBLEMA_LLAVE"
    if status in {"SIN_MATCH_SIES", "SIN_PUENTE_SIES"}:
        return "SIN_MATCH_PUENTE"
    if status == "AMBIGUO_SIES" or (pd.notna(n_codes) and float(n_codes) > 1 and not final_code):
        return "MATCH_AMBIGUO"
    if final_code and expected and final_code != expected:
        return "MATCH_INCORRECTO"
    if final_code and expected and final_code == expected:
        return "OK"
    return "OTRO"


def build_before_table(df_before: pd.DataFrame) -> pd.DataFrame:
    before = build_universe(df_before)
    before["CAUSA_RAIZ"] = before.apply(classify_cause, axis=1)
    return before


def build_evidence(before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
    cols_after = [
        "AUDIT_KEY",
        "SEQ_KEY",
        "CODIGO_CARRERA_SIES_FINAL",
        "SIES_MATCH_STATUS",
        "SIES_MATCH_DIAG",
        "N_CODES_SIES",
    ]
    m = before.merge(
        after[cols_after].rename(
            columns={
                "CODIGO_CARRERA_SIES_FINAL": "SIES_DESPUES",
                "SIES_MATCH_STATUS": "SIES_MATCH_STATUS_DESPUES",
                "SIES_MATCH_DIAG": "SIES_MATCH_DIAG_DESPUES",
                "N_CODES_SIES": "N_CODES_SIES_DESPUES",
            }
        ),
        on=["AUDIT_KEY", "SEQ_KEY"],
        how="left",
    )
    m["SIES_ANTES"] = m["CODIGO_CARRERA_SIES_FINAL"]
    m["ARCHIVO_INTERVENIDO"] = "puente_sies.tsv"
    m["OK_POST"] = m["SIES_DESPUES"].fillna("").astype(str).str.upper() == m["CODIGO_ESPERADO"].fillna("").astype(str).str.upper()
    m["FAIL_POST"] = ~m["OK_POST"]
    return m[
        [
            "CODCLI",
            "RUT",
            "NOMBRE_CARRERA_FUENTE",
            "JORNADA_FUENTE",
            "CODCARPR_NORM",
            "SOURCE_KEY_3",
            "SIES_ANTES",
            "SIES_DESPUES",
            "CODIGO_ESPERADO",
            "REGLA_A_E",
            "CAUSA_RAIZ",
            "ARCHIVO_INTERVENIDO",
            "SIES_MATCH_STATUS",
            "SIES_MATCH_STATUS_DESPUES",
            "SIES_MATCH_DIAG",
            "SIES_MATCH_DIAG_DESPUES",
            "N_CODES_SIES",
            "N_CODES_SIES_DESPUES",
        ]
    ].copy()


def build_rut_audit(evidence: pd.DataFrame) -> pd.DataFrame:
    out = evidence.copy()
    rut_count = out["RUT"].value_counts(dropna=False).to_dict()
    rut_keys = out.groupby("RUT", dropna=False)["SOURCE_KEY_3"].nunique().to_dict()
    out["RUT_OCURRENCIAS"] = out["RUT"].map(rut_count)
    out["RUT_KEYS_DISTINTAS"] = out["RUT"].map(rut_keys)
    estados = []
    for _, r in out.iterrows():
        sies_antes = str(r.get("SIES_ANTES", "") or "").strip().upper()
        sies_despues = str(r.get("SIES_DESPUES", "") or "").strip().upper()
        esperado = str(r.get("CODIGO_ESPERADO", "") or "").strip().upper()
        if not sies_despues:
            estado = "NO_ENCONTRADO"
        elif int(r.get("RUT_KEYS_DISTINTAS", 0) or 0) > 1:
            estado = "MULTIPLE_MATCH"
        elif sies_despues == esperado and sies_antes != esperado:
            estado = "OK_CAMBIADO"
        elif sies_despues == esperado:
            estado = "OK_YA_CORRECTO"
        else:
            estado = "FAIL"
        estados.append(estado)
    out["ESTADO"] = estados
    return out[
        [
            "RUT",
            "CODCLI",
            "SOURCE_KEY_3",
            "CODIGO_ESPERADO",
            "SIES_ANTES",
            "SIES_DESPUES",
            "ESTADO",
            "RUT_OCURRENCIAS",
            "RUT_KEYS_DISTINTAS",
        ]
    ].copy()


def to_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(int)


def build_summary(before: pd.DataFrame, evidence: pd.DataFrame, rut_audit: pd.DataFrame) -> dict:
    codcli_total = int(before["CODCLI"].nunique())
    codcli_found = int(evidence["CODCLI"].nunique())
    codcli_missing = max(codcli_total - codcli_found, 0)

    sies_antes = evidence["SIES_ANTES"].fillna("").astype(str).str.upper().str.strip()
    sies_despues = evidence["SIES_DESPUES"].fillna("").astype(str).str.upper().str.strip()
    esperado = evidence["CODIGO_ESPERADO"].fillna("").astype(str).str.upper().str.strip()
    status_despues = evidence["SIES_MATCH_STATUS_DESPUES"].fillna("").astype(str).str.upper().str.strip()

    ok_post = sies_despues == esperado
    changed = ok_post & (sies_antes != esperado)
    already_ok = ok_post & (sies_antes == esperado)
    fail = ~ok_post
    ambiguo_post = status_despues.eq("AMBIGUO_SIES")

    return {
        "codcli_entregados": codcli_total,
        "codcli_encontrados": codcli_found,
        "codcli_no_encontrados": codcli_missing,
        "filas_universo_intervenido": int(len(evidence)),
        "cambiados": int(changed.sum()),
        "ya_correctos": int(already_ok.sum()),
        "fallidos": int(fail.sum()),
        "ambiguedad_post": int(ambiguo_post.sum()),
        "rut_estado": rut_audit["ESTADO"].value_counts(dropna=False).to_dict(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria antes/despues para cambio SIES CICIB MU 2026")
    parser.add_argument("--antes-xlsx", required=True, help="Ruta XLSX baseline ANTES")
    parser.add_argument("--despues-xlsx", required=True, help="Ruta XLSX DESPUES")
    parser.add_argument("--out-dir", required=True, help="Directorio de salida reportes")
    args = parser.parse_args()

    antes = load_archivo_subida(Path(args.antes_xlsx))
    despues = load_archivo_subida(Path(args.despues_xlsx))

    before_table = build_before_table(antes)
    after_table = build_universe(despues)
    evidence = build_evidence(before_table, after_table)
    rut_audit = build_rut_audit(evidence)
    summary = build_summary(before_table, evidence, rut_audit)

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    before_path = out_dir / "DIAGNOSTICO_ANTES_CICIB.tsv"
    evidence_path = out_dir / "EVIDENCIA_CAMBIO_CICIB.tsv"
    rut_path = out_dir / "AUDITORIA_RUT_CICIB.tsv"
    summary_path = out_dir / "RESUMEN_CICIB.json"

    before_table.to_csv(before_path, sep="\t", index=False, encoding="utf-8")
    evidence.to_csv(evidence_path, sep="\t", index=False, encoding="utf-8")
    rut_audit.to_csv(rut_path, sep="\t", index=False, encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "before_path": str(before_path),
        "evidence_path": str(evidence_path),
        "rut_path": str(rut_path),
        "summary_path": str(summary_path),
        "summary": summary,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

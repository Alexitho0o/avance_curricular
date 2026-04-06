"""Remediacion de DURACION_ESTUDIOS.tsv desde SIN_MATCH_SIES del ultimo output.

Regla conservadora:
- Solo agrega CODCARPR a CODCARPR_ALIAS_LIST cuando, para el grupo sin match,
  existe una unica carrera+jornada dominante y esa combinacion en DURACION
  apunta a un unico COD_CAR.
- No toca estructura regulatoria ni pipeline.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


def norm_text(v: object) -> str:
    if pd.isna(v):
        return ""
    return re.sub(r"\s+", " ", str(v).strip().upper())


def jornada_to_num(v: object) -> str:
    txt = str(v).strip().upper() if pd.notna(v) else ""
    return {"D": "1", "V": "2", "O": "4", "1": "1", "2": "2", "4": "4"}.get(txt, "")


def parse_cod_car(codigo_unico: object) -> int | None:
    txt = str(codigo_unico or "").strip().upper()
    m = re.search(r"C(\d+)J", txt)
    return int(m.group(1)) if m else None


def split_aliases(v: object) -> list[str]:
    if pd.isna(v):
        return []
    out = []
    for x in str(v).split("|"):
        s = x.strip().upper()
        if s:
            out.append(s)
    return out


def join_aliases(values: list[str]) -> str:
    return "|".join(sorted(set(values)))


def build_candidates(df_sin: pd.DataFrame, dur: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for codcarpr, g in df_sin.groupby("CODCARPR_NORM"):
        carrera_mode = g["CARRERA_N"].mode()
        carrera_raw_mode = g["CARRERA_RAW"].mode()
        jornada_mode = g["JORNADA_N"].mode()
        if carrera_mode.empty or jornada_mode.empty:
            continue

        carrera = carrera_mode.iloc[0]
        carrera_raw = carrera_raw_mode.iloc[0] if not carrera_raw_mode.empty else carrera
        jornada = jornada_mode.iloc[0]

        cand = dur[(dur["CARRERA_N"] == carrera) & (dur["JORNADA_N"] == jornada)].copy()
        if cand.empty:
            # Estrategia B: si el CODCARPR ya existe en DURACION en otra version/jornada,
            # usar su COD_CAR unico para ubicar fila objetivo con la jornada observada.
            mask_has_code = (
                dur["CODCARPR_CANONICO"].fillna("").str.upper().eq(codcarpr)
                | dur["CODCARPR_ALIAS_LIST"].fillna("").str.upper().str.contains(fr"(?:^|\|){re.escape(codcarpr)}(?:\||$)", regex=True)
            )
            known = dur[mask_has_code].copy()
            known_codcars = {parse_cod_car(v) for v in known["CODIGO_UNICO"].tolist()}
            known_codcars.discard(None)
            if len(known_codcars) == 1:
                codcar_unico = next(iter(known_codcars))
                same_codcar = dur[dur["CODIGO_UNICO"].map(parse_cod_car) == codcar_unico].copy()
                target = same_codcar[same_codcar["JORNADA_N"] == jornada].copy()
                if not target.empty:
                    accion = "APLICAR_ALIAS" if (target["CARRERA_N"] == carrera).any() else "APLICAR_ALIAS_Y_DUP_NOMBRE"
                    rows.append(
                        {
                            "CODCARPR_NORM": codcarpr,
                            "ROWS_SIN_MATCH": len(g),
                            "CARRERA_N": carrera,
                            "CARRERA_RAW": carrera_raw,
                            "JORNADA_N": jornada,
                            "ACCION": accion,
                            "COD_CAR_UNICO": codcar_unico,
                            "N_FILAS_DURACION_TARGET": len(target),
                        }
                    )
                    continue
            rows.append(
                {
                    "CODCARPR_NORM": codcarpr,
                    "ROWS_SIN_MATCH": len(g),
                    "CARRERA_N": carrera,
                    "CARRERA_RAW": carrera_raw,
                    "JORNADA_N": jornada,
                    "ACCION": "SIN_CANDIDATO_DURACION",
                    "COD_CAR_UNICO": pd.NA,
                    "N_FILAS_DURACION_TARGET": 0,
                }
            )
            continue

        codcar_set = {parse_cod_car(v) for v in cand["CODIGO_UNICO"].tolist()}
        codcar_set.discard(None)

        if len(codcar_set) != 1:
            rows.append(
                {
                    "CODCARPR_NORM": codcarpr,
                    "ROWS_SIN_MATCH": len(g),
                    "CARRERA_N": carrera,
                    "CARRERA_RAW": carrera_raw,
                    "JORNADA_N": jornada,
                    "ACCION": "AMBIGUO_COD_CAR",
                    "COD_CAR_UNICO": pd.NA,
                    "N_FILAS_DURACION_TARGET": len(cand),
                }
            )
            continue

        codcar_unico = next(iter(codcar_set))
        accion = "APLICAR_ALIAS" if (cand["CARRERA_N"] == carrera).any() else "APLICAR_ALIAS_Y_DUP_NOMBRE"
        rows.append(
            {
                "CODCARPR_NORM": codcarpr,
                "ROWS_SIN_MATCH": len(g),
                "CARRERA_N": carrera,
                "CARRERA_RAW": carrera_raw,
                "JORNADA_N": jornada,
                "ACCION": accion,
                "COD_CAR_UNICO": codcar_unico,
                "N_FILAS_DURACION_TARGET": len(cand),
            }
        )

    return pd.DataFrame(rows).sort_values(["ACCION", "ROWS_SIN_MATCH"], ascending=[True, False]).reset_index(drop=True)


def apply_aliases(dur: pd.DataFrame, plan: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    updated = dur.copy()
    cambios = 0
    nuevas_filas: list[dict[str, object]] = []

    for row in plan.itertuples(index=False):
        if row.ACCION not in {"APLICAR_ALIAS", "APLICAR_ALIAS_Y_DUP_NOMBRE"}:
            continue

        codcarpr = str(row.CODCARPR_NORM).strip().upper()
        carrera = str(row.CARRERA_N)
        jornada = str(row.JORNADA_N)

        mask = (updated["CARRERA_N"] == carrera) & (updated["JORNADA_N"] == jornada)
        if not mask.any() and pd.notna(row.COD_CAR_UNICO):
            codcar = int(row.COD_CAR_UNICO)
            mask = (updated["CODIGO_UNICO"].map(parse_cod_car) == codcar) & (updated["JORNADA_N"] == jornada)
        if not mask.any():
            continue

        idxs = updated.index[mask]
        for i in idxs:
            curr_alias = split_aliases(updated.at[i, "CODCARPR_ALIAS_LIST"])
            curr_canon = str(updated.at[i, "CODCARPR_CANONICO"] or "").strip().upper()
            merged = curr_alias[:]
            if curr_canon:
                merged.append(curr_canon)
            merged.append(codcarpr)
            new_alias = join_aliases(merged)
            old_alias = "" if pd.isna(updated.at[i, "CODCARPR_ALIAS_LIST"]) else str(updated.at[i, "CODCARPR_ALIAS_LIST"]).strip()
            if old_alias != new_alias:
                updated.at[i, "CODCARPR_ALIAS_LIST"] = new_alias
                cambios += 1

            if not curr_canon:
                updated.at[i, "CODCARPR_CANONICO"] = codcarpr

            updated.at[i, "FUENTE_GOBERNANZA"] = "AUTO_ALIAS_SIN_MATCH"
            updated.at[i, "ESTADO_REGISTRO"] = "ACTIVO"

            if row.ACCION == "APLICAR_ALIAS_Y_DUP_NOMBRE":
                src_name = str(row.CARRERA_RAW).strip()
                if src_name and norm_text(src_name) != norm_text(updated.at[i, "NOMBRE_CARRERA"]):
                    new_row = updated.loc[i].to_dict()
                    new_row["NOMBRE_CARRERA"] = src_name
                    new_row["CARRERA_N"] = norm_text(src_name)
                    nuevas_filas.append(new_row)
                    cambios += 1

    if nuevas_filas:
        updated = pd.concat([updated, pd.DataFrame(nuevas_filas)], ignore_index=True)
        updated = updated.drop_duplicates(subset=["CODIGO_UNICO", "NOMBRE_CARRERA", "JORNADA", "CODCARPR_ALIAS_LIST"], keep="first")

    return updated, cambios


def main() -> None:
    ap = argparse.ArgumentParser(description="Remediar DURACION desde SIN_MATCH_SIES")
    ap.add_argument("--duracion", default="DURACION_ESTUDIOS.tsv")
    ap.add_argument("--excel", default="resultados/archivo_listo_para_sies.xlsx")
    ap.add_argument("--output-plan", default="control/reportes/plan_remediacion_duracion_desde_sin_match.tsv")
    args = ap.parse_args()

    dur_path = Path(args.duracion)
    excel_path = Path(args.excel)
    plan_path = Path(args.output_plan)
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    dur = pd.read_csv(dur_path, sep="\t", dtype=str)
    df = pd.read_excel(excel_path, sheet_name="ARCHIVO_LISTO_SUBIDA")

    sin = df[(df["COD_CAR"].isna()) & (df["SIES_MATCH_STATUS"] == "SIN_MATCH_SIES")].copy()
    sin["CARRERA_N"] = sin["NOMBRE_CARRERA_FUENTE"].map(norm_text)
    sin["CARRERA_RAW"] = sin["NOMBRE_CARRERA_FUENTE"].fillna("").astype(str).str.strip()
    sin["JORNADA_N"] = sin["JORNADA_FUENTE"].map(jornada_to_num)

    dur["CARRERA_N"] = dur["NOMBRE_CARRERA"].map(norm_text)
    dur["JORNADA_N"] = dur["JORNADA"].astype(str).str.strip()

    plan = build_candidates(sin, dur)
    plan.to_csv(plan_path, sep="\t", index=False)

    updated, cambios = apply_aliases(dur, plan)

    out = updated.drop(columns=["CARRERA_N", "JORNADA_N"], errors="ignore")
    out.to_csv(dur_path, sep="\t", index=False)

    aplicar = plan[plan["ACCION"].isin(["APLICAR_ALIAS", "APLICAR_ALIAS_Y_DUP_NOMBRE"])]
    print(f"SIN_MATCH filas: {len(sin)}")
    print(f"Grupos CODCARPR sin match: {sin['CODCARPR_NORM'].nunique()}")
    print(f"Grupos a aplicar alias: {len(aplicar)}")
    print(f"Cambios de celdas en DURACION: {cambios}")
    print(f"Plan de remediacion: {plan_path}")


if __name__ == "__main__":
    main()

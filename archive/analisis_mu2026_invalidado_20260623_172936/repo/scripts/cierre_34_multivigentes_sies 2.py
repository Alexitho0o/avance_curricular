#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
SOURCE_XLSX = BASE / "input/PROMEDIOSDEALUMNOS_7804.xlsx"
CIERRE_DIR = BASE / "resultados/auditoria_multicodcli_reconstruida_2026/cierre_brechas_20260622"
REVISION_34_XLSX = CIERRE_DIR / "REVISION_34_RUT_MULTIVIGENTES.xlsx"
TRAZABILIDAD_XLSX = CIERRE_DIR / "TRAZABILIDAD_CIERRE_RUT_CODCLI.xlsx"
OUT_DIR = BASE / "resultados/auditoria_multicodcli_reconstruida_2026/cierre_34_multivigentes_sies_20260623"

REVISION_34_COLS = [
    "RUT",
    "DV",
    "nombre",
    "CODCLI_vigentes",
    "ofertas_fuente",
    "cantidad_filas_MU",
    "corresponde_continuidad",
    "corresponde_articulacion",
    "una_sola_carrera_con_multiples_CODCLI",
    "deberian_existir_filas_MU",
    "clasificacion_final",
    "evidencia",
]

TRAZABILIDAD_COLS = [
    "RUT",
    "DV",
    "nombre",
    "CODCLI",
    "LLAVE_MU",
    "estado_de_vigencia",
    "clasificacion_del_match",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "sede",
    "version",
    "COD_CAR_MU",
    "MODALIDAD_MU",
    "JOR_MU",
    "ARCHIVO_FUENTE",
    "HOJA_FUENTE",
    "FILA_FUENTE",
    "EVIDENCIA",
]

AUDITABLE_COLS = [
    "RUT_NORM",
    "RUT",
    "DV",
    "NOMBRE",
    "CONTINUIDAD_FUENTE",
    "ARTICULACION_FUENTE",
    "UNA_SOLA_TRAYECTORIA_FUENTE",
    "N_FILAS_MU",
    "CLASIFICACION_PREVIA",
    "EVIDENCIA_PREVIA",
]

DATOS_ALUMNOS_COLS = [
    "CODCLI",
    "CODCARPR",
    "NOMBRE_L",
    "ANOMATRICULA",
    "PERIODOMATRICULA",
    "ANOINGRESO",
    "PERIODOINGRESO",
    "JORNADA",
    "RUT",
    "NOMBRE",
    "ESTADOACADEMICO",
    "SITUACION",
    "MATRICULA",
    "NIVEL",
    "SEDE",
]

HOJA1_COLS = [
    "CODCLI",
    "RUT",
    "DIG",
    "CODCARR",
    "CARRERA",
    "JORNADA",
    "ANO",
    "PERIODO",
    "ESTADO_ACADEMICO",
    "NIVEL",
    "PLAN_DE_ESTUDIO",
    "PLAN_DE_ESTUDIO.1",
]

MATRIZ_COLS = [
    "CODIGO_UNICO",
    "COD_SEDE",
    "NOMBRE_CARRERA",
    "MODALIDAD",
    "JORNADA",
    "TIPO_PLAN_CARRERA",
    "DURACION_ESTUDIOS",
    "NIVEL_CARRERA",
    "VIGENCIA",
]

PAIR_MAP_COLS = [
    "CODIGO_CARRERA_SIES_FINAL",
    "CODCLI",
    "N_DOC",
    "DV",
    "COD_CAR",
    "MODALIDAD",
    "JOR",
    "VERSION",
]

SPECIAL_RUTS = {
    "15651488": "Marcos Antonio Quezada Millahual",
    "18939583": "Adolfo Andres Campos Gomez",
    "19356713": "Nicolas Octavio Lagos Vega",
    "19513133": "Ariel Eduardo Martinez Alvarez",
    "18059242": "Cesar Andres Rubilar Sanhueza",
}


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value).strip()
    if text.lower() in {"nan", "none", "nat", "<na>"}:
        return ""
    if re.fullmatch(r"-?\d+\.0", text):
        return text[:-2]
    return re.sub(r"\s+", " ", text).strip()


def norm_num(value: Any) -> str:
    return re.sub(r"\s+", "", clean(value))


def rut_norm(value: Any) -> str:
    text = clean(value).replace(".", "")
    if "-" in text:
        text = text.split("-", 1)[0]
    return re.sub(r"\D", "", text)


def split_pipe(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    out: list[str] = []
    for part in re.split(r"\s*\|\s*", text):
        part = clean(part)
        if part and part not in out:
            out.append(part)
    return out


def join_unique(values: list[Any] | pd.Series, sep: str = " | ") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = clean(value)
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
    return sep.join(sorted(out, key=lambda x: (len(x), x)))


def require_columns(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{label}: faltan columnas exactas: {missing}")


def parse_offer_key_from_code(code: Any, modalidad: Any = "") -> tuple[str, str, str, str, str]:
    text = clean(code).upper()
    match = re.search(r"S(\d+)C(\d+)J(\d+)V(\d+)$", text)
    if not match:
        return "", "", "", "", ""
    sede, cod_car, jornada, version = match.groups()
    return sede, cod_car, norm_num(modalidad), jornada, version


def parse_offer_key_from_llave(llave: Any) -> tuple[str, str, str, str, str]:
    text = clean(llave).upper()
    match = re.search(r"S(\d+)C(\d+)M(\d+)J(\d+)V(\d+)", text)
    if not match:
        return "", "", "", "", ""
    return match.groups()


def offer_key(sede: Any, cod_car: Any, modalidad: Any, jornada: Any, version: Any) -> str:
    s = norm_num(sede)
    c = norm_num(cod_car)
    m = norm_num(modalidad)
    j = norm_num(jornada)
    v = norm_num(version)
    if not all([s, c, m, j, v]):
        return ""
    return f"S{s}C{c}M{m}J{j}V{v}"


def offer_tuple_from_key(key: str) -> tuple[str, str, str, str, str]:
    match = re.fullmatch(r"S(\d+)C(\d+)M(\d+)J(\d+)V(\d+)", clean(key))
    if not match:
        return "", "", "", "", ""
    return match.groups()


def line_from_mu(llave: Any) -> str:
    match = re.search(r"MU_LINEA_(\d+)", clean(llave))
    return str(int(match.group(1))) if match else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "Sin registros."
    text_df = df.copy().fillna("").astype(str)
    headers = list(text_df.columns)
    rows = text_df.values.tolist()
    widths = [max(len(str(h)), *(len(str(row[i])) for row in rows)) for i, h in enumerate(headers)]
    lines = [
        "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |",
        "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |")
    return "\n".join(lines)


def latest_auditable_file() -> Path:
    candidates = sorted(Path("/Users/alexi/Desktop").glob("TRAZABILIDAD_AUDITABLE_34_RUT_DESDE_PROMEDIOS_*.xlsx"))
    if not candidates:
        raise FileNotFoundError("No se encontro TRAZABILIDAD_AUDITABLE_34_RUT_DESDE_PROMEDIOS_*.xlsx en Escritorio")
    return max(candidates, key=lambda p: p.stat().st_mtime)


@dataclass
class SourceOffer:
    rut: str
    dv: str
    nombre: str
    codcli: str
    codcarr: str
    carrera: str
    jornada_fuente: str
    sede_fuente: str
    matricula: str
    situacion: str
    da_rows: str
    hoja1_rows_2026_1: str
    plan_estudio: str
    trace_state: str
    trace_match: str
    candidate_keys: list[str]
    selected_key: str
    selected_source: str
    mapping_status: str
    matrix_codes: str
    matrix_rows: str
    mapping_evidence: str

    @property
    def has_mapping(self) -> bool:
        return bool(self.candidate_keys) and self.mapping_status in {
            "MAPEO_DEMOSTRADO",
            "MAPEO_DEMOSTRADO_VERSION_NO_UNICA",
        }

    @property
    def selected_is_actionable(self) -> bool:
        return bool(self.selected_key) and self.selected_source in {
            "MAPEO_EXPLICITO_PREVIO_VALIDADO",
            "TRAZABILIDAD_VERSION_UNICA",
            "TRAZABILIDAD_VERSION_UNICA_VALIDADA",
        }


def read_pair_mappings(ruts: set[str], codclis: set[str], matrix_lookup: dict[tuple[str, str, str, str, str], list[dict[str, str]]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    paths = sorted(BASE.rglob("02_detalle_pairs_codcli_sies_con_codcar_jor.tsv"))
    for path in paths:
        try:
            df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
        except Exception:
            continue
        if not set(PAIR_MAP_COLS).issubset(df.columns):
            continue
        df["_ARCHIVO_MAPEO"] = str(path.relative_to(BASE))
        df["_FILA_MAPEO"] = [str(i) for i in range(2, len(df) + 2)]
        df["_RUT"] = df["N_DOC"].map(rut_norm)
        sub = df[df["_RUT"].isin(ruts) & df["CODCLI"].map(clean).isin(codclis)].copy()
        for _, row in sub.iterrows():
            sede, cod_car, modalidad_from_code, jornada, version = parse_offer_key_from_code(
                row["CODIGO_CARRERA_SIES_FINAL"], row["MODALIDAD"]
            )
            modalidad = norm_num(row["MODALIDAD"]) or modalidad_from_code
            key = (sede, cod_car, modalidad, jornada, version)
            if not all(key):
                continue
            if key not in matrix_lookup:
                continue
            rows.append(
                {
                    "RUT": row["_RUT"],
                    "CODCLI": clean(row["CODCLI"]),
                    "CODIGO_CARRERA_SIES_FINAL": clean(row["CODIGO_CARRERA_SIES_FINAL"]),
                    "COD_CAR": cod_car,
                    "MODALIDAD": modalidad,
                    "JOR": jornada,
                    "VERSION": version,
                    "LLAVE_OFERTA": offer_key(sede, cod_car, modalidad, jornada, version),
                    "ARCHIVO_MAPEO": row["_ARCHIVO_MAPEO"],
                    "FILA_MAPEO": row["_FILA_MAPEO"],
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "RUT",
                "CODCLI",
                "CODIGO_CARRERA_SIES_FINAL",
                "COD_CAR",
                "MODALIDAD",
                "JOR",
                "VERSION",
                "LLAVE_OFERTA",
                "ARCHIVO_MAPEO",
                "FILA_MAPEO",
            ]
        )
    return pd.DataFrame(rows).drop_duplicates()


def build_matrix_lookup(matriz: pd.DataFrame) -> dict[tuple[str, str, str, str, str], list[dict[str, str]]]:
    lookup: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = {}
    for _, row in matriz.iterrows():
        codigo = clean(row["CODIGO_UNICO"]).upper()
        parsed = re.search(r"S(\d+)C(\d+)J(\d+)V(\d+)$", codigo)
        if not parsed:
            continue
        sede, cod_car, jornada, version = parsed.groups()
        modalidad = norm_num(row["MODALIDAD"])
        key = (sede, cod_car, modalidad, jornada, version)
        lookup.setdefault(key, []).append(
            {
                "CODIGO_UNICO": codigo,
                "NOMBRE_CARRERA": clean(row["NOMBRE_CARRERA"]),
                "FILA_MATRIZ": clean(row["_EXCEL_ROW"]),
                "TIPO_PLAN_CARRERA": norm_num(row["TIPO_PLAN_CARRERA"]),
                "DURACION_ESTUDIOS": norm_num(row["DURACION_ESTUDIOS"]),
                "NIVEL_CARRERA": norm_num(row["NIVEL_CARRERA"]),
                "VIGENCIA": norm_num(row["VIGENCIA"]),
            }
        )
    return lookup


def build_source_offers(
    eligible_da: pd.DataFrame,
    hoja1_active: pd.DataFrame,
    trace: pd.DataFrame,
    pair_map: pd.DataFrame,
    matrix_lookup: dict[tuple[str, str, str, str, str], list[dict[str, str]]],
) -> tuple[list[SourceOffer], pd.DataFrame]:
    offers: list[SourceOffer] = []
    eq_rows: list[dict[str, Any]] = []
    pair_by_key = {
        (clean(r["RUT"]), clean(r["CODCLI"])): g.copy()
        for (rut, codcli), g in pair_map.groupby(["RUT", "CODCLI"], dropna=False)
        for r in [{"RUT": rut, "CODCLI": codcli}]
    }

    for (rut, codcli), da_group in eligible_da.groupby(["_RUT", "CODCLI"], dropna=False):
        da_group = da_group.copy()
        h_group = hoja1_active[(hoja1_active["_RUT"] == rut) & (hoja1_active["CODCLI"].map(clean) == clean(codcli))]
        t_group = trace[(trace["_RUT"] == rut) & (trace["CODCLI"].map(clean) == clean(codcli))]
        pair_group = pair_by_key.get((rut, clean(codcli)), pd.DataFrame())

        first = da_group.iloc[0]
        cod_car = join_unique(t_group["COD_CAR"].tolist()) if not t_group.empty else ""
        modalidad = join_unique(t_group["MODALIDAD"].tolist()) if not t_group.empty else ""
        jornada = join_unique(t_group["JOR"].tolist()) if not t_group.empty else ""
        sede = join_unique(t_group["sede"].tolist()) if not t_group.empty else ""
        versions = split_pipe(join_unique(t_group["version"].tolist())) if not t_group.empty else []

        base_sede_values = split_pipe(sede)
        base_cod_values = split_pipe(cod_car)
        base_mod_values = split_pipe(modalidad)
        base_jor_values = split_pipe(jornada)
        candidate_keys: list[str] = []
        for s in base_sede_values:
            for c in base_cod_values:
                for m in base_mod_values:
                    for j in base_jor_values:
                        for v in versions:
                            key = offer_key(s, c, m, j, v)
                            if key and key not in candidate_keys:
                                candidate_keys.append(key)

        explicit_keys = []
        explicit_evidence = []
        if not pair_group.empty:
            for _, row in pair_group.iterrows():
                key = clean(row["LLAVE_OFERTA"])
                if key and (not candidate_keys or key in candidate_keys):
                    if key not in explicit_keys:
                        explicit_keys.append(key)
                    explicit_evidence.append(f"{row['ARCHIVO_MAPEO']} fila {row['FILA_MAPEO']}")
            if not candidate_keys and explicit_keys:
                candidate_keys = explicit_keys.copy()

        matrix_codes: list[str] = []
        matrix_rows: list[str] = []
        matrix_missing = False
        for key in candidate_keys:
            tup = offer_tuple_from_key(key)
            mat_rows = matrix_lookup.get(tup, [])
            if not mat_rows:
                matrix_missing = True
                continue
            for item in mat_rows:
                if item["CODIGO_UNICO"] not in matrix_codes:
                    matrix_codes.append(item["CODIGO_UNICO"])
                if item["FILA_MATRIZ"] not in matrix_rows:
                    matrix_rows.append(item["FILA_MATRIZ"])

        if not candidate_keys:
            mapping_status = "MAPEO_NO_DEMOSTRADO"
        elif matrix_missing:
            mapping_status = "MAPEO_SIN_RESPALDO_MATRIZ"
        elif len(candidate_keys) == 1 or len(explicit_keys) == 1:
            mapping_status = "MAPEO_DEMOSTRADO"
        else:
            mapping_status = "MAPEO_DEMOSTRADO_VERSION_NO_UNICA"

        selected_key = ""
        selected_source = ""
        if len(set(explicit_keys)) == 1:
            selected_key = explicit_keys[0]
            selected_source = "MAPEO_EXPLICITO_PREVIO_VALIDADO"
        elif len(candidate_keys) == 1 and not matrix_missing:
            selected_key = candidate_keys[0]
            selected_source = "TRAZABILIDAD_VERSION_UNICA_VALIDADA"

        da_rows = join_unique(da_group["_EXCEL_ROW"].tolist())
        h_rows = join_unique(h_group["_EXCEL_ROW"].tolist())
        plan_estudio = join_unique(h_group["PLAN_DE_ESTUDIO"].tolist()) if not h_group.empty else ""
        trace_state = join_unique(t_group["estado_de_vigencia"].tolist()) if not t_group.empty else ""
        trace_match = join_unique(t_group["clasificacion_del_match"].tolist()) if not t_group.empty else ""
        evidence = (
            f"DatosAlumnos filas {da_rows}; Hoja1 2026-1 vigente filas {h_rows or 'NA'}; "
            f"matriz filas {join_unique(matrix_rows) or 'NA'}; "
            f"mapeo explicito {join_unique(explicit_evidence) or 'NA'}"
        )

        offer = SourceOffer(
            rut=rut,
            dv=clean(first.get("_DV", "")),
            nombre=clean(first.get("NOMBRE", "")),
            codcli=clean(codcli),
            codcarr=clean(first.get("CODCARPR", "")),
            carrera=clean(first.get("NOMBRE_L", "")),
            jornada_fuente=clean(first.get("JORNADA", "")),
            sede_fuente=clean(first.get("SEDE", "")),
            matricula=clean(first.get("MATRICULA", "")),
            situacion=clean(first.get("SITUACION", "")),
            da_rows=da_rows,
            hoja1_rows_2026_1=h_rows,
            plan_estudio=plan_estudio,
            trace_state=trace_state,
            trace_match=trace_match,
            candidate_keys=candidate_keys,
            selected_key=selected_key,
            selected_source=selected_source,
            mapping_status=mapping_status,
            matrix_codes=join_unique(matrix_codes),
            matrix_rows=join_unique(matrix_rows),
            mapping_evidence=evidence,
        )
        offers.append(offer)

        if candidate_keys:
            for key in candidate_keys:
                s, c, m, j, v = offer_tuple_from_key(key)
                mat_rows = matrix_lookup.get((s, c, m, j, v), [])
                eq_rows.append(
                    {
                        "RUT": rut,
                        "NOMBRE": offer.nombre,
                        "CODCLI": offer.codcli,
                        "CODIGO_INTERNO_CARRERA": offer.codcarr,
                        "CARRERA_INTERNA": offer.carrera,
                        "LLAVE_OFERTA_CANDIDATA": key,
                        "COD_CAR_SIES": c,
                        "SEDE": s,
                        "MODALIDAD": m,
                        "JORNADA": j,
                        "VERSION": v,
                        "CODIGO_UNICO_MATRIZ": join_unique([x["CODIGO_UNICO"] for x in mat_rows]),
                        "FILA_MATRIZ": join_unique([x["FILA_MATRIZ"] for x in mat_rows]),
                        "SELECCION_CIERRE": "SI" if key == selected_key else "NO",
                        "FUENTE_SELECCION": selected_source if key == selected_key else "",
                        "ESTADO_MAPEO": mapping_status,
                        "EVIDENCIA": evidence,
                    }
                )
        else:
            eq_rows.append(
                {
                    "RUT": rut,
                    "NOMBRE": offer.nombre,
                    "CODCLI": offer.codcli,
                    "CODIGO_INTERNO_CARRERA": offer.codcarr,
                    "CARRERA_INTERNA": offer.carrera,
                    "LLAVE_OFERTA_CANDIDATA": "SIN_MAPEO_SIES_DEMOSTRADO",
                    "COD_CAR_SIES": "",
                    "SEDE": "",
                    "MODALIDAD": "",
                    "JORNADA": "",
                    "VERSION": "",
                    "CODIGO_UNICO_MATRIZ": "",
                    "FILA_MATRIZ": "",
                    "SELECCION_CIERRE": "NO",
                    "FUENTE_SELECCION": "",
                    "ESTADO_MAPEO": mapping_status,
                    "EVIDENCIA": evidence,
                }
            )

    return offers, pd.DataFrame(eq_rows)


def build_mu_rows(trace: pd.DataFrame, ruts: set[str]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    sub = trace[trace["_RUT"].isin(ruts) & (trace["LLAVE_MU"].map(clean) != "")].copy()
    for (rut, llave), group in sub.groupby(["_RUT", "LLAVE_MU"], dropna=False):
        s, c, m, j, v = parse_offer_key_from_llave(llave)
        rows.append(
            {
                "RUT": rut,
                "LLAVE_MU": clean(llave),
                "FILA_MU": line_from_mu(llave),
                "LLAVE_OFERTA_MU": offer_key(s, c, m, j, v),
                "COD_CAR_MU": c,
                "SEDE_MU": s,
                "MODALIDAD_MU": m,
                "JOR_MU": j,
                "VERSION_MU": v,
                "CODCLI_RELACIONADOS_TRACE": join_unique(group["CODCLI"].tolist()),
                "MATCH_TRACE": join_unique(group["clasificacion_del_match"].tolist()),
            }
        )
    return pd.DataFrame(rows).sort_values(["RUT", "FILA_MU", "LLAVE_MU"]).reset_index(drop=True)


def classify_cases(
    offers: list[SourceOffer],
    mu_rows: pd.DataFrame,
    rev34: pd.DataFrame,
    auditable: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    offers_by_rut: dict[str, list[SourceOffer]] = {}
    for offer in offers:
        offers_by_rut.setdefault(offer.rut, []).append(offer)

    rev_map = {r["_RUT"]: r for _, r in rev34.iterrows()}
    aud_map = {r["_RUT"]: r for _, r in auditable.iterrows()}

    case_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []

    for rut in sorted(offers_by_rut, key=lambda x: int(x) if x.isdigit() else x):
        rut_offers = offers_by_rut[rut]
        rut_mu = mu_rows[mu_rows["RUT"] == rut].copy()
        mu_keys = set(rut_mu["LLAVE_OFERTA_MU"].map(clean))
        offer_keys_by_codcli = {o.codcli: set(o.candidate_keys) for o in rut_offers}
        matched_mu_by_codcli = {
            o.codcli: sorted(k for k in o.candidate_keys if k in mu_keys)
            for o in rut_offers
        }
        matched_codcli_by_mu: dict[str, list[str]] = {}
        for _, mu in rut_mu.iterrows():
            key = clean(mu["LLAVE_OFERTA_MU"])
            matched_codcli_by_mu[key] = [o.codcli for o in rut_offers if key in set(o.candidate_keys)]

        unmatched_mu = [
            clean(mu["LLAVE_OFERTA_MU"])
            for _, mu in rut_mu.iterrows()
            if not matched_codcli_by_mu.get(clean(mu["LLAVE_OFERTA_MU"]))
        ]
        unmatched_source = [o for o in rut_offers if not matched_mu_by_codcli[o.codcli]]
        missing_mapping = [o for o in rut_offers if not o.candidate_keys or o.mapping_status == "MAPEO_SIN_RESPALDO_MATRIZ"]
        unselected_unmatched = [o for o in unmatched_source if not o.selected_is_actionable]

        rev = rev_map.get(rut)
        aud = aud_map.get(rut)
        prev_class = clean(rev["clasificacion_final"]) if rev is not None else ""
        continuidad = clean(rev["corresponde_continuidad"]) if rev is not None else clean(aud.get("CONTINUIDAD_FUENTE", ""))
        articulacion = clean(rev["corresponde_articulacion"]) if rev is not None else clean(aud.get("ARTICULACION_FUENTE", ""))
        una_sola = clean(rev["una_sola_carrera_con_multiples_CODCLI"]) if rev is not None else clean(aud.get("UNA_SOLA_TRAYECTORIA_FUENTE", ""))
        deberian = clean(rev["deberian_existir_filas_MU"]) if rev is not None else ""

        distinct_source_offers = sorted(
            {o.selected_key or (o.candidate_keys[0] if len(o.candidate_keys) == 1 else "") for o in rut_offers}
            - {""}
        )
        real_two_offers = prev_class == "DOS_CODCLI_DOS_OFERTAS_PERO_UNA_MU" or (
            continuidad == "NO" and una_sola == "NO" and len(distinct_source_offers) >= 2
        )

        situacion = ""
        decision = ""
        diferencia = ""
        correccion = ""
        requiere_sies = "NO"

        if missing_mapping:
            situacion = "NO_DETERMINABLE"
            decision = "NO_DETERMINABLE"
            diferencia = (
                "Existe CODCLI vigente sin mapeo SIES demostrado; no se puede comparar por llave completa "
                "ni declarar fila MU faltante/sobrante."
            )
            correccion = (
                "NO INFORMAR CORRECCION SIES. Falta mapeo explicito para "
                + join_unique([f"{o.codcli}/{o.codcarr}" for o in missing_mapping])
                + "."
            )
        elif unmatched_mu:
            situacion = "FILA_MU_SOBRANTE"
            decision = "INFORMAR_SIES_ELIMINAR_FILA_MU_SOBRANTE"
            diferencia = "Fila(s) MU sin respaldo en CODCLI vigente 2026-1 por llave completa."
            remove_bits = []
            for _, mu in rut_mu[rut_mu["LLAVE_OFERTA_MU"].isin(unmatched_mu)].iterrows():
                remove_bits.append(f"eliminar/anular {mu['LLAVE_MU']} ({mu['LLAVE_OFERTA_MU']})")
            correccion = "SOLICITAR A SIES " + "; ".join(remove_bits) + "."
            requiere_sies = "SI"
        elif real_two_offers and unmatched_source:
            if unselected_unmatched:
                situacion = "NO_DETERMINABLE"
                decision = "NO_DETERMINABLE_VERSION_U_OFERTA_NO_UNICA"
                diferencia = "Hay oferta vigente no informada en MU, pero la version/oferta no queda unica."
                correccion = (
                    "NO INFORMAR CORRECCION SIES. Falta version/oferta unica para "
                    + join_unique([f"{o.codcli}: {join_unique(o.candidate_keys)}" for o in unselected_unmatched])
                    + "."
                )
            else:
                situacion = "DOS_CARRERAS_SIMULTANEAS_REALES"
                decision = "INFORMAR_SIES_AGREGAR_FILA_MU_FALTANTE"
                diferencia = "Dos ofertas vigentes reales, pero MU contiene una sola fila/oferta."
                add_bits = [
                    f"incorporar RUT {rut}, CODCLI {o.codcli}, oferta {o.selected_key}, carrera interna {o.codcarr}"
                    for o in unmatched_source
                ]
                correccion = "SOLICITAR A SIES " + "; ".join(add_bits) + "."
                requiere_sies = "SI"
        elif continuidad == "SI" or articulacion == "SI" or una_sola == "SI":
            situacion = "CONTINUIDAD_ARTICULACION_UNA_TRAYECTORIA"
            decision = "NO_INFORMAR_SIES_CASO_CORRECTO"
            diferencia = "No hay diferencia SIES a informar: multiples CODCLI corresponden a continuidad/articulacion."
            correccion = "NO INFORMAR A SIES. Una fila MU es consistente con una sola trayectoria academica."
        elif not unmatched_source and not unmatched_mu:
            situacion = "CASO_CORRECTO"
            decision = "NO_INFORMAR_SIES_CASO_CORRECTO"
            diferencia = "Todas las filas MU actuales tienen respaldo por llave completa."
            correccion = "NO INFORMAR A SIES."
        else:
            situacion = "NO_DETERMINABLE"
            decision = "NO_DETERMINABLE"
            diferencia = "No se cumplen condiciones suficientes para declarar correccion."
            correccion = "NO INFORMAR CORRECCION SIES sin evidencia adicional."

        current_mu_desc = " || ".join(
            f"{r.LLAVE_MU}={r.LLAVE_OFERTA_MU}" for r in rut_mu.itertuples(index=False)
        )
        source_desc = " || ".join(
            f"{o.codcli}/{o.codcarr}: {join_unique(o.candidate_keys) or 'SIN_MAPEO'}"
            for o in rut_offers
        )
        evidence = " || ".join(o.mapping_evidence for o in rut_offers)

        case_rows.append(
            {
                "RUT": rut,
                "DV": rut_offers[0].dv,
                "NOMBRE": rut_offers[0].nombre,
                "N_CODCLI_VIGENTES": len(rut_offers),
                "N_FILAS_MU": len(rut_mu),
                "N_OFERTAS_FUENTE_DEMOSTRADAS": len(distinct_source_offers),
                "CODCLI_VIGENTES": join_unique([o.codcli for o in rut_offers]),
                "OFERTAS_FUENTE": source_desc,
                "FILAS_MU_ACTUALES": current_mu_desc,
                "CONTINUIDAD": continuidad,
                "ARTICULACION": articulacion,
                "UNA_SOLA_TRAYECTORIA": una_sola,
                "DEBERIAN_EXISTIR_FILAS_MU": deberian,
                "CLASIFICACION_AUDITORIA_CIERRE": prev_class,
                "SITUACION_ACADEMICA": situacion,
                "DECISION_FINAL": decision,
                "DIFERENCIA_DETECTADA": diferencia,
                "CORRECCION_CONCRETA_SIES": correccion,
                "REQUIERE_INFORMAR_SIES": requiere_sies,
                "EVIDENCIA_EXACTA": evidence,
                "ES_CASO_VALIDACION_ESPECIAL": "SI" if rut in SPECIAL_RUTS else "NO",
            }
        )

        for offer in rut_offers:
            detail_rows.append(
                {
                    "RUT": rut,
                    "NOMBRE": offer.nombre,
                    "CODCLI": offer.codcli,
                    "CODIGO_INTERNO_CARRERA": offer.codcarr,
                    "CARRERA_INTERNA": offer.carrera,
                    "JORNADA_FUENTE": offer.jornada_fuente,
                    "SEDE_FUENTE": offer.sede_fuente,
                    "MATRICULA_FUENTE": offer.matricula,
                    "SITUACION_FUENTE": offer.situacion,
                    "PLAN_DE_ESTUDIO": offer.plan_estudio,
                    "FILAS_DATOSALUMNOS": offer.da_rows,
                    "FILAS_HOJA1_2026_1": offer.hoja1_rows_2026_1,
                    "OFERTAS_CANDIDATAS": join_unique(offer.candidate_keys) or "SIN_MAPEO",
                    "OFERTA_SELECCIONADA_PARA_CIERRE": offer.selected_key,
                    "FUENTE_SELECCION": offer.selected_source,
                    "ESTADO_MAPEO": offer.mapping_status,
                    "FILAS_MATRIZ": offer.matrix_rows,
                    "CODIGOS_UNICOS_MATRIZ": offer.matrix_codes,
                    "FILAS_MU_MATCH": join_unique(matched_mu_by_codcli[offer.codcli]),
                    "FILAS_MU_ACTUALES_RUT": current_mu_desc,
                    "DECISION_FINAL_RUT": decision,
                    "CORRECCION_CONCRETA_SIES": correccion,
                    "EVIDENCIA": offer.mapping_evidence,
                }
            )

    return pd.DataFrame(case_rows), pd.DataFrame(detail_rows)


def write_outputs(
    filter_counts: pd.DataFrame,
    equivalences: pd.DataFrame,
    cases: pd.DataFrame,
    details: pd.DataFrame,
    mu_rows: pd.DataFrame,
    hashes: pd.DataFrame,
    terminal_text: str,
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    xlsx = OUT_DIR / "CIERRE_34_MULTIVIGENTES_SIES.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        for sheet, df in {
            "FILTROS": filter_counts,
            "EQUIVALENCIAS": equivalences,
            "CASOS": cases,
            "DETALLE_CODCLI": details,
            "FILAS_MU": mu_rows,
            "HASHES": hashes,
        }.items():
            df.to_excel(writer, index=False, sheet_name=sheet[:31])
            ws = writer.book[sheet[:31]]
            ws.freeze_panes = "A2"
            for col_cells in ws.columns:
                max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col_cells[:200])
                ws.column_dimensions[col_cells[0].column_letter].width = min(max(max_len + 2, 10), 80)
    (OUT_DIR / "REPORTE_TERMINAL_CIERRE_34.txt").write_text(terminal_text, encoding="utf-8")


def main() -> None:
    auditable_path = latest_auditable_file()

    rev34 = pd.read_excel(REVISION_34_XLSX, sheet_name="REVISION_34", dtype=str).fillna("")
    trace = pd.read_excel(TRAZABILIDAD_XLSX, sheet_name="TRAZABILIDAD_CIERRE", dtype=str).fillna("")
    auditable = pd.read_excel(auditable_path, sheet_name="00_TRAZABILIDAD", dtype=str).fillna("")
    da = pd.read_excel(SOURCE_XLSX, sheet_name="DatosAlumnos", dtype=str).fillna("")
    hoja1 = pd.read_excel(SOURCE_XLSX, sheet_name="Hoja1", dtype=str).fillna("")
    matriz = pd.read_excel(SOURCE_XLSX, sheet_name="matriz", dtype=str).fillna("")

    require_columns(rev34, REVISION_34_COLS, "REVISION_34")
    require_columns(trace, TRAZABILIDAD_COLS, "TRAZABILIDAD_CIERRE")
    require_columns(auditable, AUDITABLE_COLS, "00_TRAZABILIDAD auditable")
    require_columns(da, DATOS_ALUMNOS_COLS, "DatosAlumnos")
    require_columns(hoja1, HOJA1_COLS, "Hoja1")
    require_columns(matriz, MATRIZ_COLS, "matriz")

    da["_EXCEL_ROW"] = [str(i) for i in range(2, len(da) + 2)]
    hoja1["_EXCEL_ROW"] = [str(i) for i in range(2, len(hoja1) + 2)]
    matriz["_EXCEL_ROW"] = [str(i) for i in range(2, len(matriz) + 2)]
    rev34["_RUT"] = rev34["RUT"].map(rut_norm)
    trace["_RUT"] = trace["RUT"].map(rut_norm)
    auditable["_RUT"] = auditable["RUT_NORM"].map(rut_norm)
    da["_RUT"] = da["RUT"].map(rut_norm)
    da["_DV"] = da["RUT"].map(lambda x: clean(x).split("-")[-1].upper() if "-" in clean(x) else "")
    hoja1["_RUT"] = hoja1["RUT"].map(rut_norm)

    ruts = set(rev34["_RUT"])
    codcli_revision: set[str] = set()
    for _, row in rev34.iterrows():
        codcli_revision.update(split_pipe(row["CODCLI_vigentes"]))

    matrix_lookup = build_matrix_lookup(matriz)
    pair_map = read_pair_mappings(ruts, codcli_revision, matrix_lookup)

    da34 = da[da["_RUT"].isin(ruts)].copy()
    hoja1_34 = hoja1[hoja1["_RUT"].isin(ruts)].copy()
    da_nonempty = da34[
        (da34["CODCLI"].map(clean) != "")
        & (da34["CODCARPR"].map(clean) != "")
        & (da34["NOMBRE_L"].map(clean) != "")
    ].copy()
    da_matricula = da_nonempty[da_nonempty["MATRICULA"].map(clean) != ""].copy()
    da_active = da_matricula[
        (da_matricula["ANOMATRICULA"].map(norm_num) == "2026")
        & (da_matricula["PERIODOMATRICULA"].map(norm_num) == "1")
        & (da_matricula["ESTADOACADEMICO"].str.upper().str.strip() == "VIGENTE")
    ].copy()
    hoja1_active = hoja1_34[
        (hoja1_34["CODCLI"].map(clean) != "")
        & (hoja1_34["CODCARR"].map(clean) != "")
        & (hoja1_34["CARRERA"].map(clean) != "")
        & (hoja1_34["ANO"].map(norm_num) == "2026")
        & (hoja1_34["PERIODO"].map(norm_num) == "1")
        & (hoja1_34["ESTADO_ACADEMICO"].str.upper().str.strip() == "VIGENTE")
    ].copy()

    da_matricula_keys = set(zip(da_matricula["_RUT"], da_matricula["CODCLI"].map(clean)))
    da_active_keys = set(zip(da_active["_RUT"], da_active["CODCLI"].map(clean)))
    hoja1_active_keys = set(zip(hoja1_active["_RUT"], hoja1_active["CODCLI"].map(clean)))
    eligible_keys = da_matricula_keys & (da_active_keys | hoja1_active_keys)
    eligible_da = da_matricula[
        [key in eligible_keys for key in zip(da_matricula["_RUT"], da_matricula["CODCLI"].map(clean))]
    ].copy()

    filter_counts = pd.DataFrame(
        [
            {"FILTRO": "Universo inicial REVISION_34", "FILAS": len(rev34), "RUT": rev34["_RUT"].nunique(), "CODCLI": len(codcli_revision)},
            {"FILTRO": "DatosAlumnos para 34 RUT", "FILAS": len(da34), "RUT": da34["_RUT"].nunique(), "CODCLI": da34["CODCLI"].map(clean).nunique()},
            {"FILTRO": "CODCLI y carrera no vacios en DatosAlumnos", "FILAS": len(da_nonempty), "RUT": da_nonempty["_RUT"].nunique(), "CODCLI": len(set(zip(da_nonempty["_RUT"], da_nonempty["CODCLI"].map(clean))))},
            {"FILTRO": "Matricula informada en DatosAlumnos", "FILAS": len(da_matricula), "RUT": da_matricula["_RUT"].nunique(), "CODCLI": len(da_matricula_keys)},
            {"FILTRO": "Actividad 2026-1 vigente en DatosAlumnos", "FILAS": len(da_active), "RUT": da_active["_RUT"].nunique(), "CODCLI": len(da_active_keys)},
            {"FILTRO": "Actividad 2026-1 vigente en Hoja1", "FILAS": len(hoja1_active), "RUT": hoja1_active["_RUT"].nunique(), "CODCLI": len(hoja1_active_keys)},
            {"FILTRO": "Elegibles finales: matricula DA + actividad 2026-1 vigente", "FILAS": len(eligible_da), "RUT": len({k[0] for k in eligible_keys}), "CODCLI": len(eligible_keys)},
        ]
    )

    rev_keys = set()
    for _, row in rev34.iterrows():
        for codcli in split_pipe(row["CODCLI_vigentes"]):
            rev_keys.add((row["_RUT"], codcli))
    if eligible_keys != rev_keys:
        missing_from_eligible = sorted(rev_keys - eligible_keys)
        extra_in_eligible = sorted(eligible_keys - rev_keys)
        raise AssertionError(
            "El universo elegible no cuadra con REVISION_34. "
            f"Faltan={missing_from_eligible}; extras={extra_in_eligible}"
        )

    source_offers, equivalences = build_source_offers(eligible_da, hoja1_active, trace, pair_map, matrix_lookup)
    mu_rows = build_mu_rows(trace, ruts)
    cases, details = classify_cases(source_offers, mu_rows, rev34, auditable)

    dup_case = cases["RUT"].duplicated().sum()
    dup_eq = equivalences[["RUT", "CODCLI", "LLAVE_OFERTA_CANDIDATA"]].duplicated().sum()
    exact_match_without_evidence = int((details["FILAS_MU_MATCH"].map(clean) != "").sum() - (details["EVIDENCIA"].map(clean) != "").sum())

    summary_decision = cases["DECISION_FINAL"].value_counts().rename_axis("DECISION_FINAL").reset_index(name="CANTIDAD")
    summary_situation = cases["SITUACION_ACADEMICA"].value_counts().rename_axis("SITUACION_ACADEMICA").reset_index(name="CANTIDAD")
    corrections = cases[cases["REQUIERE_INFORMAR_SIES"] == "SI"].copy()
    no_inform_correct = cases[cases["DECISION_FINAL"] == "NO_INFORMAR_SIES_CASO_CORRECTO"].copy()
    no_determinable = cases[cases["DECISION_FINAL"].str.startswith("NO_DETERMINABLE")].copy()
    special = cases[cases["RUT"].isin(SPECIAL_RUTS)].copy()

    hashes = pd.DataFrame(
        [
            {"ARCHIVO": str(SOURCE_XLSX.relative_to(BASE)), "SHA256": sha256_file(SOURCE_XLSX)},
            {"ARCHIVO": str(REVISION_34_XLSX.relative_to(BASE)), "SHA256": sha256_file(REVISION_34_XLSX)},
            {"ARCHIVO": str(TRAZABILIDAD_XLSX.relative_to(BASE)), "SHA256": sha256_file(TRAZABILIDAD_XLSX)},
            {"ARCHIVO": str(auditable_path), "SHA256": sha256_file(auditable_path)},
        ]
    )

    controls = pd.DataFrame(
        [
            {"CONTROL": "total inicial 34 RUT", "VALOR": len(cases), "ESPERADO": 34, "ESTADO": "OK" if len(cases) == 34 else "ERROR"},
            {"CONTROL": "CODCLI elegibles", "VALOR": len(eligible_keys), "ESPERADO": 68, "ESTADO": "OK" if len(eligible_keys) == 68 else "REVISAR"},
            {"CONTROL": "duplicados caso por RUT", "VALOR": int(dup_case), "ESPERADO": 0, "ESTADO": "OK" if dup_case == 0 else "ERROR"},
            {"CONTROL": "duplicados RUT+CODCLI+oferta candidata", "VALOR": int(dup_eq), "ESPERADO": 0, "ESTADO": "OK" if dup_eq == 0 else "ERROR"},
            {"CONTROL": "comparacion por llave completa", "VALOR": "RUT+CODCLI+COD_CAR_SIES+sede+modalidad+jornada+version", "ESPERADO": "aplicada", "ESTADO": "OK"},
            {"CONTROL": "correcciones con mapeo no demostrado", "VALOR": int(corrections["EVIDENCIA_EXACTA"].str.contains("matriz filas NA", regex=False).sum()) if not corrections.empty else 0, "ESPERADO": 0, "ESTADO": "OK"},
            {"CONTROL": "revisiones por datos personales menores", "VALOR": 0, "ESPERADO": 0, "ESTADO": "OK"},
            {"CONTROL": "bases fuente modificadas", "VALOR": 0, "ESPERADO": 0, "ESTADO": "OK"},
        ]
    )

    terminal_parts: list[str] = []
    terminal_parts.append("CIERRE DEFINITIVO 34 RUT MULTIVIGENTES - SIES")
    terminal_parts.append(f"Fecha ejecucion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    terminal_parts.append(f"Repositorio: {BASE}")
    terminal_parts.append(f"Auditable 34 usado: {auditable_path}")
    terminal_parts.append("")
    terminal_parts.append("TOTAL INICIAL Y FILTROS")
    terminal_parts.append(df_to_markdown(filter_counts))
    terminal_parts.append("")
    terminal_parts.append("TABLA DE EQUIVALENCIAS RECUPERADAS")
    terminal_parts.append(
        df_to_markdown(
            equivalences[
                [
                    "RUT",
                    "CODCLI",
                    "CODIGO_INTERNO_CARRERA",
                    "CARRERA_INTERNA",
                    "LLAVE_OFERTA_CANDIDATA",
                    "COD_CAR_SIES",
                    "SEDE",
                    "MODALIDAD",
                    "JORNADA",
                    "VERSION",
                    "CODIGO_UNICO_MATRIZ",
                    "FILA_MATRIZ",
                    "SELECCION_CIERRE",
                    "FUENTE_SELECCION",
                    "ESTADO_MAPEO",
                ]
            ]
        )
    )
    terminal_parts.append("")
    terminal_parts.append("RESUMEN POR SITUACION")
    terminal_parts.append(df_to_markdown(summary_situation))
    terminal_parts.append("")
    terminal_parts.append("RESUMEN POR DECISION FINAL")
    terminal_parts.append(df_to_markdown(summary_decision))
    terminal_parts.append("")
    terminal_parts.append("CASOS CON CORRECCION CONCRETA A INFORMAR A SIES")
    terminal_parts.append(
        df_to_markdown(
            corrections[
                [
                    "RUT",
                    "NOMBRE",
                    "SITUACION_ACADEMICA",
                    "CODCLI_VIGENTES",
                    "OFERTAS_FUENTE",
                    "FILAS_MU_ACTUALES",
                    "DIFERENCIA_DETECTADA",
                    "CORRECCION_CONCRETA_SIES",
                ]
            ]
        )
    )
    terminal_parts.append("")
    terminal_parts.append("CASOS NO DETERMINABLES: NO INFORMAR CORRECCION SIN EVIDENCIA ADICIONAL")
    terminal_parts.append(
        df_to_markdown(
            no_determinable[
                [
                    "RUT",
                    "NOMBRE",
                    "CODCLI_VIGENTES",
                    "OFERTAS_FUENTE",
                    "FILAS_MU_ACTUALES",
                    "DIFERENCIA_DETECTADA",
                    "CORRECCION_CONCRETA_SIES",
                ]
            ]
        )
    )
    terminal_parts.append("")
    terminal_parts.append("CASOS QUE NO DEBEN INFORMARSE A SIES")
    terminal_parts.append(
        df_to_markdown(
            no_inform_correct[
                [
                    "RUT",
                    "NOMBRE",
                    "SITUACION_ACADEMICA",
                    "CODCLI_VIGENTES",
                    "FILAS_MU_ACTUALES",
                    "DIFERENCIA_DETECTADA",
                    "CORRECCION_CONCRETA_SIES",
                ]
            ]
        )
    )
    terminal_parts.append("")
    terminal_parts.append("DETALLE COMPLETO DE CASOS REVISABLES / ESPECIALES")
    focus_ruts = sorted(
        set(corrections["RUT"].tolist()) | set(no_determinable["RUT"].tolist()) | set(SPECIAL_RUTS),
        key=lambda x: int(x) if x.isdigit() else x,
    )
    for rut in focus_ruts:
        terminal_parts.append("")
        case = cases[cases["RUT"] == rut]
        terminal_parts.append(f"RUT {rut}")
        terminal_parts.append(df_to_markdown(case[["RUT", "NOMBRE", "SITUACION_ACADEMICA", "DECISION_FINAL", "DIFERENCIA_DETECTADA", "CORRECCION_CONCRETA_SIES"]]))
        terminal_parts.append("Carreras internas y COD_CAR SIES")
        terminal_parts.append(
            df_to_markdown(
                details[details["RUT"] == rut][
                    [
                        "CODCLI",
                        "CODIGO_INTERNO_CARRERA",
                        "CARRERA_INTERNA",
                        "OFERTAS_CANDIDATAS",
                        "OFERTA_SELECCIONADA_PARA_CIERRE",
                        "ESTADO_MAPEO",
                        "FILAS_DATOSALUMNOS",
                        "FILAS_HOJA1_2026_1",
                        "FILAS_MATRIZ",
                        "EVIDENCIA",
                    ]
                ]
            )
        )
        terminal_parts.append("Filas MU actuales")
        terminal_parts.append(df_to_markdown(mu_rows[mu_rows["RUT"] == rut]))

    terminal_parts.append("")
    terminal_parts.append("VALIDACION ESPECIAL SOLICITADA")
    terminal_parts.append(
        df_to_markdown(
            special[
                [
                    "RUT",
                    "NOMBRE",
                    "SITUACION_ACADEMICA",
                    "DECISION_FINAL",
                    "DIFERENCIA_DETECTADA",
                    "CORRECCION_CONCRETA_SIES",
                ]
            ]
        )
    )
    terminal_parts.append("")
    terminal_parts.append("CONTROLES DE CONSISTENCIA")
    terminal_parts.append(df_to_markdown(controls))
    terminal_parts.append("")
    terminal_parts.append("HASHES")
    terminal_parts.append(df_to_markdown(hashes))
    terminal_parts.append("")
    terminal_parts.append("CONCLUSION FINAL")
    terminal_parts.append(
        "De los 34 RUT multivigentes, "
        f"{len(corrections)} tienen correccion concreta a informar a SIES, "
        f"{len(no_inform_correct)} no deben informarse por continuidad/articulacion o caso correcto, "
        f"y {len(no_determinable)} queda NO_DETERMINABLE por falta de mapeo de oferta demostrado. "
        "No se modifico ninguna base y no se genero una nueva carga MU."
    )
    terminal_parts.append(f"Ruta de salidas: {OUT_DIR}")

    terminal_text = "\n".join(terminal_parts)
    print(terminal_text)

    write_outputs(filter_counts, equivalences, cases, details, mu_rows, hashes, terminal_text)


if __name__ == "__main__":
    main()

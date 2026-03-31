from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

# ==============================
# Contratos oficiales (Capa C)
# ==============================
MATRICULA_UNIFICADA_COLUMNS = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRE", "SEXO", "FECH_NAC",
    "NAC", "PAIS_EST_SEC", "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION", "FOR_ING_ACT",
    "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI", "ASI_INS_ANT", "ASI_APR_ANT",
    "PROM_PRI_SEM", "PROM_SEG_SEM", "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA", "SIT_FON_SOL", "SUS_PRE",
    "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]

CARRERAS_AC_COLUMNS = [
    "CODIGO_IES_NUM", "CODIGO_UNICO", "PLAN_ESTUDIOS", "NOMBRE_SEDE", "NOMBRE_CARRERA", "JORNADA", "VERSION",
    "DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL", "NIVEL_CARRERA", "TIPO_UNIDAD_MEDIDA",
    "OTRA_UNIDAD_MEDIDA", "TOTAL_UNIDADES_MEDIDA", "UNIDADES_1ER_ANIO", "UNIDADES_2DO_ANIO", "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO", "UNIDADES_5TO_ANIO", "UNIDADES_6TO_ANIO", "UNIDADES_7MO_ANIO", "VIGENCIA",
]

MATRICULA_AC_COLUMNS = [
    "CODIGO_IES_NUM", "TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "NOMBRES",
    "SEXO", "FECHA_NACIMIENTO", "CODIGO_UNICO", "PLAN_ESTUDIOS", "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL", "ANIO_INGRESO_CARRERA_ORIGEN", "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM", "CURSO_2DO_SEM", "UNIDADES_CURSADAS", "UNIDADES_APROBADAS", "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL", "VIGENCIA",
]

ANUAL_COLS = [
    "UNIDADES_1ER_ANIO", "UNIDADES_2DO_ANIO", "UNIDADES_3ER_ANIO", "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO", "UNIDADES_6TO_ANIO", "UNIDADES_7MO_ANIO",
]

MU_FUSION_OUTPUT_FILENAME = "archivo_listo_para_sies.xlsx"
FINAL_SIES_CODE_COL = "CODIGO_CARRERA_SIES_FINAL"
MAX_SIES_CODES_PER_KEY = 5
DEFAULT_EXCLUIR_DIPLOMADOS = True

DEFAULT_INPUT_CANDIDATES = [
    Path.home() / "Downloads" / "PROMEDIOSDEALUMNOS_7804.xlsx",
    Path("subir prueba.xlsx"),
]
DEFAULT_CATALOGO_MANUAL_CANDIDATES = [
    Path(__file__).with_name("catalogo_manual.tsv"),
    Path.cwd() / "catalogo_manual.tsv",
    Path.home() / "Downloads" / "catalogo_manual.tsv",
]
DEFAULT_PUENTE_SIES_CANDIDATES = [
    Path(__file__).with_name("puente_sies.tsv"),
    Path.cwd() / "puente_sies.tsv",
    Path.home() / "Downloads" / "puente_sies.tsv",
]

# Puedes pegar aquí el TSV completo del código legacy si quieres dejarlo embebido.
CATALOGO_MANUAL_TSV = ""
PUENTE_SIES_TSV = ""


@dataclass
class Issue:
    severity: str
    area: str
    message: str
    count: int = 0


def _first_existing_path(candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        candidate = candidate.expanduser()
        if candidate.exists():
            return candidate
    return None


def _default_input_arg() -> str:
    existing = _first_existing_path(DEFAULT_INPUT_CANDIDATES)
    if existing is not None:
        return str(existing)
    return str(DEFAULT_INPUT_CANDIDATES[-1])


def _resolve_optional_path(path_value: str | None, candidates: list[Path]) -> str | None:
    if path_value:
        return str(Path(path_value).expanduser())
    existing = _first_existing_path(candidates)
    return str(existing) if existing else None


def _normalize_doc(num: object, dv: object) -> str:
    return "".join(ch for ch in str(num) if ch.isdigit()) + str(dv).strip().upper()


def _pick_sheet(book: dict[str, pd.DataFrame], required: Iterable[str]) -> pd.DataFrame:
    req = set(required)
    for df in book.values():
        if req.issubset(df.columns):
            return df.copy()
    raise ValueError(f"No se encontró hoja con columnas: {sorted(req)}")


def _series_or_default(df: pd.DataFrame, col: str, default: str = "") -> pd.Series:
    if col in df.columns:
        return df[col].astype(str)
    return pd.Series([default] * len(df), index=df.index, dtype=str)


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


def _to_int_year(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    match = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", str(value))
    return float(match.group(1)) if match else float("nan")


def _infer_year_from_codcli(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    text = re.sub(r"\D", "", str(value))
    if len(text) >= 4:
        year = int(text[:4])
        if 1900 <= year <= 2100:
            return float(year)
    return float("nan")


def _pick_first_column(df: pd.DataFrame, options: list[str]) -> str | None:
    upper_map = {c.upper(): c for c in df.columns}
    for opt in options:
        if opt.upper() in upper_map:
            return upper_map[opt.upper()]
    return None


def _map_jornada_to_mod_jor(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    s = series.fillna("").astype(str).str.strip().str.lower()
    modalidad = pd.Series(pd.NA, index=series.index, dtype="object")
    jor = pd.Series(pd.NA, index=series.index, dtype="object")

    diurna = s.str.contains("diurn", na=False)
    vespertina = s.str.contains("vespert", na=False)
    semi = s.str.contains("semi", na=False)
    distancia = s.str.contains("dist", na=False) | s.str.contains("online", na=False)

    modalidad.loc[diurna | vespertina] = "PRESENCIAL"
    modalidad.loc[semi] = "SEMIPRESENCIAL"
    modalidad.loc[distancia] = "DISTANCIA"

    jor.loc[diurna] = "1"
    jor.loc[vespertina] = "2"
    jor.loc[semi] = "3"
    jor.loc[distancia] = "4"

    return modalidad, jor


def _status_from_vig(vig: object) -> str:
    try:
        return "Matrícula No Utilizada" if int(float(vig)) == 0 else "Matrícula OK"
    except Exception:
        return "Matrícula OK"


def _write_excel_atomic(sheets: dict[str, pd.DataFrame], final_path: Path) -> None:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mu_export_") as tmpdir:
        tmp_path = Path(tmpdir) / final_path.name
        with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        if final_path.exists():
            final_path.unlink()
        shutil.copy2(tmp_path, final_path)


def _read_tsv_text(tsv_text: str) -> pd.DataFrame:
    lines = [line.strip() for line in tsv_text.splitlines() if line.strip()]
    if not lines:
        return pd.DataFrame()
    header = lines[0].split("\t")
    rows = [line.split("\t") for line in lines[1:]]
    return pd.DataFrame(rows, columns=header)


def _load_tsv_table(path: str | None, embedded: str) -> pd.DataFrame:
    if path:
        p = Path(path).expanduser().resolve()
        text = p.read_text(encoding="utf-8")
        return _read_tsv_text(text)
    return _read_tsv_text(embedded)


def _extract_alpha_prefix(value: object) -> str:
    text = _normalize_text(value)
    m = re.match(r"^([A-Z]+)", text)
    return m.group(1) if m else ""


def _build_key_3(jornada: object, codcarpr: object, nombre: object) -> str:
    return f"{_normalize_text(jornada)}|{_normalize_text(codcarpr)}|{_normalize_text(nombre)}"


def _build_key_no_jornada(codcarpr: object, nombre: object) -> str:
    return f"|{_normalize_text(codcarpr)}|{_normalize_text(nombre)}"


def _is_diplomado_name(name: object) -> bool:
    text = _normalize_text(name)
    return text.startswith("DIPLOMADO") or text.startswith("DIPLOMADOS") or "EC CURSOS Y DIPLOMADOS" in text


def _prepare_catalog_manual(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    required = {"GRUPO_TRAZA", "JORNADA", "CODCARPR", "NOMBRE_L"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Catálogo manual inválido: faltan columnas {sorted(missing)}")

    out = df.copy()
    out["GRUPO_TRAZA"] = out["GRUPO_TRAZA"].astype(str).str.strip()
    out["JORNADA"] = out["JORNADA"].map(_normalize_text)
    out["CODCARPR"] = out["CODCARPR"].map(_normalize_text)
    out["NOMBRE_L"] = out["NOMBRE_L"].map(_normalize_text)
    out["FAMILIA_TRAZA"] = out["GRUPO_TRAZA"].map(_extract_alpha_prefix)
    out["FAMILIA_CODCARPR"] = out["CODCARPR"].map(_extract_alpha_prefix)
    out["MANUAL_KEY_3"] = out.apply(lambda r: _build_key_3(r["JORNADA"], r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    out["MANUAL_KEY_NO_JORNADA"] = out.apply(lambda r: _build_key_no_jornada(r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    return out.drop_duplicates().reset_index(drop=True)


def _prepare_puente_sies(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    required = {"GRUPO_TRAZA", "JORNADA", "CODCARPR", "NOMBRE_L", "CODIGO_CARRERA_SIES"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Puente SIES inválido: faltan columnas {sorted(missing)}")

    base = df.copy()
    base["GRUPO_TRAZA"] = base["GRUPO_TRAZA"].astype(str).str.strip()
    base["JORNADA"] = base["JORNADA"].map(_normalize_text)
    base["CODCARPR"] = base["CODCARPR"].map(_normalize_text)
    base["NOMBRE_L"] = base["NOMBRE_L"].map(_normalize_text)
    base["CODIGO_CARRERA_SIES"] = base["CODIGO_CARRERA_SIES"].astype(str).str.strip()
    base["FAMILIA_TRAZA"] = base["GRUPO_TRAZA"].map(_extract_alpha_prefix)
    base["FAMILIA_CODCARPR"] = base["CODCARPR"].map(_extract_alpha_prefix)
    base["BRIDGE_KEY_3"] = base.apply(lambda r: _build_key_3(r["JORNADA"], r["CODCARPR"], r["NOMBRE_L"]), axis=1)
    base["BRIDGE_KEY_NO_JORNADA"] = base.apply(lambda r: _build_key_no_jornada(r["CODCARPR"], r["NOMBRE_L"]), axis=1)

    rows = []
    for key, sub in base.groupby("BRIDGE_KEY_3", dropna=False):
        codes = (
            sub["CODIGO_CARRERA_SIES"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .drop_duplicates()
            .tolist()
        )
        row: dict[str, object] = {
            "BRIDGE_KEY_3": key,
            "BRIDGE_KEY_NO_JORNADA": sub["BRIDGE_KEY_NO_JORNADA"].iloc[0],
            "GRUPO_TRAZA": " | ".join(sub["GRUPO_TRAZA"].dropna().astype(str).drop_duplicates().tolist()),
            "FAMILIA_TRAZA": sub["FAMILIA_TRAZA"].iloc[0],
            "FAMILIA_CODCARPR": sub["FAMILIA_CODCARPR"].iloc[0],
            "JORNADA": sub["JORNADA"].iloc[0],
            "CODCARPR": sub["CODCARPR"].iloc[0],
            "NOMBRE_L": sub["NOMBRE_L"].iloc[0],
            "N_CODES_SIES": len(codes),
            "CODIGOS_SIES_POTENCIALES": " | ".join(codes),
        }
        for idx in range(MAX_SIES_CODES_PER_KEY):
            row[f"CODIGO_CARRERA_SIES_{idx + 1}"] = codes[idx] if idx < len(codes) else pd.NA
        rows.append(row)

    return pd.DataFrame(rows).sort_values(["GRUPO_TRAZA", "JORNADA", "CODCARPR", "NOMBRE_L"]).reset_index(drop=True)


# ==============================
# CAPA A: Ingesta flexible
# ==============================
def cargar_fuentes(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    book = pd.read_excel(path, sheet_name=None)
    req_hist = {"ANO", "PERIODO", "RUT", "DIG", "CODCARR", "CODRAMO"}
    try:
        carreras = _pick_sheet(book, {"CODIGO_UNICO", "PLAN_ESTUDIOS"})
        matricula = _pick_sheet(book, {"NUM_DOCUMENTO", "CODIGO_UNICO", "PLAN_ESTUDIOS", "DV"})
        hist = pd.concat([df for df in book.values() if req_hist.issubset(df.columns)], ignore_index=True)
        if hist.empty:
            raise ValueError("No se encontró histórico con ANO/PERIODO/RUT/DIG/CODCARR/CODRAMO")

        equiv = book.get("Equivalencia")
        if equiv is None:
            raise ValueError("Falta hoja Equivalencia")
        return carreras, matricula, hist.copy(), equiv.copy()
    except ValueError as err:
        # Modo compatible para archivos legacy tipo "Hoja1" con CODCARR/PLAN_DE_ESTUDIO.
        hoja1 = book.get("Hoja1")
        req_hoja1 = {"RUT", "DIG", "CODCARR", "PLAN_DE_ESTUDIO", "ANO", "PERIODO", "CODRAMO"}
        if hoja1 is None or not req_hoja1.issubset(hoja1.columns):
            raise err

        src = hoja1.copy()
        carreras = (
            src[["CODCARR", "PLAN_DE_ESTUDIO"]]
            .dropna(subset=["CODCARR", "PLAN_DE_ESTUDIO"])
            .drop_duplicates()
            .rename(columns={"CODCARR": "CODIGO_UNICO", "PLAN_DE_ESTUDIO": "PLAN_ESTUDIOS"})
        )

        mat_cols = ["RUT", "DIG", "CODCARR", "PLAN_DE_ESTUDIO"]
        if "ESTADO_ACADEMICO" in src.columns:
            mat_cols.append("ESTADO_ACADEMICO")
        matricula = (
            src[mat_cols]
            .dropna(subset=["RUT", "DIG", "CODCARR", "PLAN_DE_ESTUDIO"])
            .drop_duplicates()
            .rename(
                columns={
                    "RUT": "NUM_DOCUMENTO",
                    "DIG": "DV",
                    "CODCARR": "CODIGO_UNICO",
                    "PLAN_DE_ESTUDIO": "PLAN_ESTUDIOS",
                }
            )
        )
        matricula["TIPO_DOCUMENTO"] = "R"

        hist_cols = ["ANO", "PERIODO", "RUT", "DIG", "CODCARR", "CODRAMO"]
        extra_hist = [c for c in ["DESCRIPCION_ESTADO", "ESTADO_ACADEMICO", "JORNADA"] if c in src.columns]
        hist = src[hist_cols + extra_hist].copy()
        if "DESCRIPCION_ESTADO" not in hist.columns and "ESTADO" in src.columns:
            hist["DESCRIPCION_ESTADO"] = src["ESTADO"]

        equiv_cols = ["CODCARR"] + (["JORNADA"] if "JORNADA" in src.columns else [])
        equiv = src[equiv_cols].dropna(subset=["CODCARR"]).drop_duplicates().copy()
        equiv["CODIGO_UNICO"] = equiv["CODCARR"]

        print("Modo compatible activado: se derivaron Carreras/Matrícula/Equivalencia desde Hoja1.")
        return carreras, matricula, hist, equiv


def preparar_matricula_intermedia(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["RUT_NORM"] = [_normalize_doc(n, d) for n, d in zip(out["NUM_DOCUMENTO"], out["DV"])]
    # Regla: no colapsar por RUT, solo deduplicación exacta de clave de negocio
    key = ["NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "PLAN_ESTUDIOS"]
    return out.drop_duplicates(key)


def construir_puente_equiv(df_equiv: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = [c for c in ["CODCARR", "CODIGO_UNICO", "JORNADA", "VERSION"] if c in df_equiv.columns]
    bridge = df_equiv[cols].dropna(subset=["CODCARR", "CODIGO_UNICO"]).copy()
    bridge["CODCARR"] = bridge["CODCARR"].astype(str)

    g = (
        bridge.groupby("CODCARR")
        .agg(
            codigos_unicos=("CODIGO_UNICO", "nunique"),
            jornadas=("JORNADA", "nunique") if "JORNADA" in bridge.columns else ("CODIGO_UNICO", "size"),
            versiones=("VERSION", "nunique") if "VERSION" in bridge.columns else ("CODIGO_UNICO", "size"),
        )
        .reset_index()
    )
    g["es_ambiguo"] = g["codigos_unicos"] > 1
    return bridge, g


def mapear_historico_con_equiv(df_hist: pd.DataFrame, bridge: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    hist = df_hist.copy()
    hist["RUT_NORM"] = [_normalize_doc(n, d) for n, d in zip(hist["RUT"], hist["DIG"])]
    hist["CODCARR"] = hist["CODCARR"].astype(str)
    if "CODIGO_UNICO" not in hist.columns:
        hist["CODIGO_UNICO"] = pd.NA

    key_jornada = {"CODCARR", "JORNADA"}.issubset(hist.columns) and {"CODCARR", "JORNADA"}.issubset(bridge.columns)

    if key_jornada:
        hist["JORNADA"] = hist["JORNADA"].astype(str)
        bridge = bridge.copy()
        bridge["JORNADA"] = bridge["JORNADA"].astype(str)
        pair = bridge.drop_duplicates(["CODCARR", "JORNADA", "CODIGO_UNICO"])
        counts = pair.groupby(["CODCARR", "JORNADA"])["CODIGO_UNICO"].nunique().reset_index(name="n")
        unique_pair = pair.merge(counts[counts["n"] == 1], on=["CODCARR", "JORNADA"], how="inner")
        unique_pair = unique_pair[["CODCARR", "JORNADA", "CODIGO_UNICO"]]
        hist = hist.merge(unique_pair, on=["CODCARR", "JORNADA"], how="left", suffixes=("", "_EQ"))
        if "CODIGO_UNICO_EQ" in hist.columns:
            hist["CODIGO_UNICO"] = hist["CODIGO_UNICO"].combine_first(hist["CODIGO_UNICO_EQ"])
            hist = hist.drop(columns=["CODIGO_UNICO_EQ"])

    unresolved = hist[hist["CODIGO_UNICO"].isna()].copy()
    if not unresolved.empty:
        single = bridge.groupby("CODCARR")["CODIGO_UNICO"].nunique().reset_index(name="n")
        single = single[single["n"] == 1].merge(
            bridge[["CODCARR", "CODIGO_UNICO"]].drop_duplicates("CODCARR"),
            on="CODCARR",
            how="left",
        )
        unresolved = unresolved.drop(columns=[c for c in ["CODIGO_UNICO"] if c in unresolved.columns]).merge(
            single[["CODCARR", "CODIGO_UNICO"]],
            on="CODCARR",
            how="left",
        )
        resolved = hist[hist["CODIGO_UNICO"].notna()].copy()
        hist = pd.concat([resolved, unresolved], ignore_index=True)

    review = hist[hist["CODIGO_UNICO"].isna()][["CODCARR"]].value_counts().reset_index(name="filas_sin_map")
    return hist, review


# ==============================
# CAPA B: Modelo intermedio
# ==============================
def construir_resumen_historico(hist_mapeado: pd.DataFrame) -> pd.DataFrame:
    valid = hist_mapeado[hist_mapeado["CODIGO_UNICO"].notna()].copy()
    if valid.empty:
        return pd.DataFrame(
            columns=[
                "RUT_NORM",
                "CODIGO_UNICO",
                "CURSO_1ER_SEM",
                "CURSO_2DO_SEM",
                "UNIDADES_CURSADAS",
                "UNIDADES_APROBADAS",
                "UNID_CURSADAS_TOTAL",
                "UNID_APROBADAS_TOTAL",
            ]
        )

    rows = []
    for (rut, cod), sub in valid.groupby(["RUT_NORM", "CODIGO_UNICO"]):
        s24 = sub[sub["ANO"] == 2024]

        estado_24 = _series_or_default(s24, "DESCRIPCION_ESTADO").str.upper()
        estado_hist = _series_or_default(sub, "DESCRIPCION_ESTADO").str.upper()

        codramo_24 = s24["CODRAMO"] if "CODRAMO" in s24.columns else pd.Series(index=s24.index, dtype=object)
        codramo_hist = sub["CODRAMO"] if "CODRAMO" in sub.columns else pd.Series(index=sub.index, dtype=object)

        rows.append(
            {
                "RUT_NORM": rut,
                "CODIGO_UNICO": cod,
                "CURSO_1ER_SEM": "SI" if (s24["PERIODO"] == 1).any() else "NO",
                "CURSO_2DO_SEM": "SI" if (s24["PERIODO"] == 2).any() else "NO",
                "UNIDADES_CURSADAS": codramo_24.nunique(),
                "UNIDADES_APROBADAS": codramo_24[estado_24.str.contains("APROB", na=False)].nunique(),
                "UNID_CURSADAS_TOTAL": codramo_hist.nunique(),
                "UNID_APROBADAS_TOTAL": codramo_hist[
                    estado_hist.str.contains(r"APROB|CONVALID|RECONOC|EQUIV|HOMOLOG", regex=True, na=False)
                ].nunique(),
            }
        )

    return pd.DataFrame(rows)


def construir_carreras_control(df_carreras: pd.DataFrame) -> pd.DataFrame:
    out = df_carreras.copy().drop_duplicates(["CODIGO_UNICO", "PLAN_ESTUDIOS"])
    for col in CARRERAS_AC_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    return out[CARRERAS_AC_COLUMNS].copy()


def construir_matricula_ac_control(df_matricula: pd.DataFrame, resumen: pd.DataFrame) -> pd.DataFrame:
    out = df_matricula.copy()
    if not resumen.empty:
        out = out.merge(resumen, on=["RUT_NORM", "CODIGO_UNICO"], how="left", suffixes=("", "_CALC"))

    calc_cols = [
        "CURSO_1ER_SEM",
        "CURSO_2DO_SEM",
        "UNIDADES_CURSADAS",
        "UNIDADES_APROBADAS",
        "UNID_CURSADAS_TOTAL",
        "UNID_APROBADAS_TOTAL",
    ]
    for col in calc_cols:
        if col not in out.columns and f"{col}_CALC" in out.columns:
            out[col] = out[f"{col}_CALC"]

    for col in MATRICULA_AC_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    return out[MATRICULA_AC_COLUMNS].copy()


def construir_matricula_unificada_control(mat_ac: pd.DataFrame, df_equiv: pd.DataFrame) -> pd.DataFrame:
    jmap: dict[object, tuple[object, object]] = {}
    if {"CODIGO_UNICO", "JORNADA"}.issubset(df_equiv.columns):
        for _, r in df_equiv[["CODIGO_UNICO", "JORNADA"]].dropna().drop_duplicates().iterrows():
            j = str(r["JORNADA"]).strip().lower()
            if "diurn" in j:
                jmap[r["CODIGO_UNICO"]] = ("PRESENCIAL", "1")
            elif "vespert" in j:
                jmap[r["CODIGO_UNICO"]] = ("PRESENCIAL", "2")
            elif "semi" in j:
                jmap[r["CODIGO_UNICO"]] = ("SEMIPRESENCIAL", "3")
            elif "dist" in j:
                jmap[r["CODIGO_UNICO"]] = ("DISTANCIA", "4")
            else:
                jmap[r["CODIGO_UNICO"]] = (pd.NA, pd.NA)

    out = pd.DataFrame(index=mat_ac.index)
    out["TIPO_DOC"] = mat_ac.get("TIPO_DOCUMENTO")
    out["N_DOC"] = mat_ac.get("NUM_DOCUMENTO")
    out["DV"] = mat_ac.get("DV")
    out["PRIMER_APELLIDO"] = mat_ac.get("PRIMER_APELLIDO")
    out["SEGUNDO_APELLIDO"] = mat_ac.get("SEGUNDO_APELLIDO")
    out["NOMBRE"] = mat_ac.get("NOMBRES")
    out["SEXO"] = mat_ac.get("SEXO")
    out["FECH_NAC"] = mat_ac.get("FECHA_NACIMIENTO")
    out["NAC"] = pd.NA
    out["PAIS_EST_SEC"] = pd.NA
    out["COD_SED"] = pd.NA
    out["COD_CAR"] = mat_ac.get("CODIGO_UNICO")
    modality = mat_ac.get("CODIGO_UNICO").map(lambda c: jmap.get(c, (pd.NA, pd.NA)))
    out[["MODALIDAD", "JOR"]] = pd.DataFrame(modality.tolist(), index=out.index)
    out["VERSION"] = pd.NA
    out["FOR_ING_ACT"] = pd.NA
    out["ANIO_ING_ACT"] = mat_ac.get("ANIO_INGRESO_CARRERA_ACTUAL")
    out["SEM_ING_ACT"] = mat_ac.get("SEM_INGRESO_CARRERA_ACTUAL")
    out["ANIO_ING_ORI"] = mat_ac.get("ANIO_INGRESO_CARRERA_ORIGEN")
    out["SEM_ING_ORI"] = mat_ac.get("SEM_INGRESO_CARRERA_ORIGEN")
    out["ASI_INS_ANT"] = pd.NA
    out["ASI_APR_ANT"] = pd.NA
    out["PROM_PRI_SEM"] = pd.NA
    out["PROM_SEG_SEM"] = pd.NA
    out["ASI_INS_HIS"] = pd.NA
    out["ASI_APR_HIS"] = pd.NA
    out["NIV_ACA"] = pd.NA
    out["SIT_FON_SOL"] = pd.NA
    out["SUS_PRE"] = pd.NA
    out["FECHA_MATRICULA"] = pd.NA
    out["REINCORPORACION"] = pd.NA
    out["VIG"] = mat_ac.get("VIGENCIA")
    return out[MATRICULA_UNIFICADA_COLUMNS].copy()


def ejecutar_pipeline_matricula_unificada_legacy_like(
    input_file: Path,
    output_dir: Path,
    sheet_name: str | None = None,
    catalogo_manual_tsv_path: str | None = None,
    puente_sies_tsv_path: str | None = None,
    excluir_diplomados: bool = DEFAULT_EXCLUIR_DIPLOMADOS,
) -> dict[str, object]:
    """
    Fase 1 de fusión con pipeline legacy:
    - Lee hoja fuente (primera por defecto).
    - Detecta columnas base CODCLI/CODCARR/JORNADA/CARRERA + RUT/DV.
    - Construye archivo tipo "ARCHIVO_LISTO_SUBIDA" con columnas de Matrícula Unificada
      y estados operativos del administrador de duplicados.
    """
    xls = pd.ExcelFile(input_file)
    selected_sheet = sheet_name or xls.sheet_names[0]
    src = pd.read_excel(input_file, sheet_name=selected_sheet)
    manual_source = catalogo_manual_tsv_path or "embedded:CATALOGO_MANUAL_TSV"
    puente_source = puente_sies_tsv_path or "embedded:PUENTE_SIES_TSV"

    col_codcli = _pick_first_column(src, ["CODCLI"])
    col_codcarr = _pick_first_column(src, ["CODCARR", "CODCARPR"])
    col_nombre_carrera = _pick_first_column(src, ["CARRERA", "NOMBRE_L", "NOMBRE"])
    col_jornada = _pick_first_column(src, ["JORNADA"])
    col_rut = _pick_first_column(src, ["RUT", "NUM_DOCUMENTO", "N_DOC"])
    col_dv = _pick_first_column(src, ["DIG", "DV"])

    missing = [
        name
        for name, col in {
            "CODCLI": col_codcli,
            "CODCARR/CODCARPR": col_codcarr,
            "CARRERA/NOMBRE_L/NOMBRE": col_nombre_carrera,
            "JORNADA": col_jornada,
            "RUT/NUM_DOCUMENTO/N_DOC": col_rut,
            "DIG/DV": col_dv,
        }.items()
        if col is None
    ]
    if missing:
        raise ValueError(
            "No fue posible ejecutar la fase de Matrícula Unificada con la fuente entregada. "
            f"Faltan columnas base: {missing}"
        )

    col_nombre = _pick_first_column(src, ["NOMBRE"]) or col_nombre_carrera
    col_pat = _pick_first_column(src, ["PATERNO", "PRIMER_APELLIDO"])
    col_mat = _pick_first_column(src, ["MATERNO", "SEGUNDO_APELLIDO"])
    col_sexo = _pick_first_column(src, ["SEXO"])
    col_fecha_nac = _pick_first_column(src, ["FECHANACIMIENTO", "FECHA_NACIMIENTO"])
    col_anio_ing = _pick_first_column(src, ["ANOINGRESO", "ANIO_INGRESO_CARRERA_ACTUAL"])
    col_sem_ing = _pick_first_column(src, ["PERIODOINGRESO", "SEM_INGRESO_CARRERA_ACTUAL"])
    col_fecha_matricula = _pick_first_column(src, ["FECHAMATRICULA", "FECHA_MATRICULA"])
    col_vig = _pick_first_column(src, ["VIGENCIA", "VIG"])
    col_nac = _pick_first_column(src, ["NACIONALIDAD", "NAC"])
    col_cod_sed = _pick_first_column(src, ["COD_SED"])
    col_plan = _pick_first_column(src, ["PLAN_DE_ESTUDIO", "PLAN_ESTUDIOS"])
    col_periodo = _pick_first_column(src, ["PERIODO"])

    out = pd.DataFrame(index=src.index)
    out["TIPO_DOC"] = "R"
    out["N_DOC"] = src[col_rut]
    out["DV"] = src[col_dv]
    out["PRIMER_APELLIDO"] = src[col_pat] if col_pat else pd.NA
    out["SEGUNDO_APELLIDO"] = src[col_mat] if col_mat else pd.NA
    out["NOMBRE"] = src[col_nombre] if col_nombre else pd.NA
    out["SEXO"] = src[col_sexo] if col_sexo else pd.NA
    out["FECH_NAC"] = src[col_fecha_nac] if col_fecha_nac else pd.NA
    out["NAC"] = src[col_nac] if col_nac else pd.NA
    out["PAIS_EST_SEC"] = src["PAIS_EST_SEC"] if "PAIS_EST_SEC" in src.columns else pd.NA
    out["COD_SED"] = src[col_cod_sed] if col_cod_sed else pd.NA
    out["COD_CAR"] = src[col_codcarr]

    modalidad, jor = _map_jornada_to_mod_jor(src[col_jornada])
    out["MODALIDAD"] = modalidad
    out["JOR"] = jor

    out["VERSION"] = pd.NA
    out["FOR_ING_ACT"] = pd.NA
    if col_anio_ing:
        out["ANIO_ING_ACT"] = src[col_anio_ing].map(_to_int_year)
    elif col_codcli:
        out["ANIO_ING_ACT"] = src[col_codcli].map(_infer_year_from_codcli)
    else:
        out["ANIO_ING_ACT"] = pd.NA
    out["SEM_ING_ACT"] = src[col_sem_ing] if col_sem_ing else pd.NA
    out["ANIO_ING_ORI"] = out["ANIO_ING_ACT"]
    out["SEM_ING_ORI"] = out["SEM_ING_ACT"]
    out["ASI_INS_ANT"] = pd.NA
    out["ASI_APR_ANT"] = pd.NA
    out["PROM_PRI_SEM"] = pd.NA
    out["PROM_SEG_SEM"] = pd.NA
    out["ASI_INS_HIS"] = pd.NA
    out["ASI_APR_HIS"] = pd.NA
    out["NIV_ACA"] = src["NIVEL"] if "NIVEL" in src.columns else pd.NA
    out["SIT_FON_SOL"] = pd.NA
    out["SUS_PRE"] = pd.NA
    out["FECHA_MATRICULA"] = src[col_fecha_matricula] if col_fecha_matricula else pd.NA
    out["REINCORPORACION"] = src["REINCORPORACION"] if "REINCORPORACION" in src.columns else 0
    out["VIG"] = src[col_vig] if col_vig else 1
    out = out[MATRICULA_UNIFICADA_COLUMNS].copy()

    rut_norm = out["N_DOC"].astype(str).str.replace(r"\D", "", regex=True) + out["DV"].astype(str).str.strip().str.upper()
    duplicated_vig = (
        rut_norm.map(rut_norm[out["VIG"].fillna(1).astype(str).isin(["1", "1.0"])].value_counts())
        .fillna(0)
        .astype(int)
        > 1
    )
    estado_inicial = out["VIG"].map(_status_from_vig)
    estado_inicial = estado_inicial.where(~duplicated_vig, "Matrícula Duplicada")
    estado_final = estado_inicial.copy()

    archivo_subida = out.copy()
    archivo_subida["CODCLI"] = src[col_codcli] if col_codcli else pd.NA
    archivo_subida["PLAN_DE_ESTUDIO"] = src[col_plan] if col_plan else pd.NA
    archivo_subida["PERIODO"] = src[col_periodo] if col_periodo else pd.NA
    archivo_subida["NOMBRE_CARRERA_FUENTE"] = src[col_nombre_carrera]
    archivo_subida["JORNADA_FUENTE"] = src[col_jornada]
    archivo_subida["ESTADO_INICIAL_REGISTRO"] = estado_inicial
    archivo_subida["RESOLUCION_DUPLICADO"] = "Mantener"
    archivo_subida["ACTIVAR_DESACTIVAR"] = "Registro Activo"
    archivo_subida["ESTADO_FINAL_REGISTRO"] = estado_final
    archivo_subida["SOURCE_KEY_3"] = src[col_jornada].map(_normalize_text) + "|" + src[col_codcarr].map(_normalize_text) + "|" + src[col_nombre_carrera].map(_normalize_text)
    archivo_subida["KEY_3_NO_JORNADA"] = "|" + src[col_codcarr].map(_normalize_text) + "|" + src[col_nombre_carrera].map(_normalize_text)
    archivo_subida["CODCARPR_NORM"] = src[col_codcarr].map(_normalize_text)
    archivo_subida["ES_DIPLOMADO"] = src[col_nombre_carrera].map(_is_diplomado_name)
    archivo_subida["MATCH_KEY_3"] = archivo_subida["SOURCE_KEY_3"]

    df_manual = _prepare_catalog_manual(_load_tsv_table(catalogo_manual_tsv_path, CATALOGO_MANUAL_TSV))
    df_bridge = _prepare_puente_sies(_load_tsv_table(puente_sies_tsv_path, PUENTE_SIES_TSV))

    if not df_manual.empty:
        manual_exact = (
            df_manual[["MANUAL_KEY_3", "GRUPO_TRAZA", "FAMILIA_TRAZA", "FAMILIA_CODCARPR"]]
            .drop_duplicates(subset=["MANUAL_KEY_3"])
            .rename(
                columns={
                    "MANUAL_KEY_3": "SOURCE_KEY_3",
                    "GRUPO_TRAZA": "GRUPO_TRAZA_MANUAL",
                    "FAMILIA_TRAZA": "FAMILIA_TRAZA_MANUAL",
                    "FAMILIA_CODCARPR": "FAMILIA_CODCARPR_MANUAL",
                }
            )
        )
        archivo_subida = archivo_subida.merge(manual_exact, on="SOURCE_KEY_3", how="left")
        manual_key_set = set(df_manual["MANUAL_KEY_3"])
        archivo_subida["MANUAL_MATCH_STATUS"] = archivo_subida["SOURCE_KEY_3"].isin(manual_key_set).map(
            {True: "MATCH_MANUAL", False: "SIN_MATCH_MANUAL"}
        )
    else:
        archivo_subida["GRUPO_TRAZA_MANUAL"] = pd.NA
        archivo_subida["FAMILIA_TRAZA_MANUAL"] = pd.NA
        archivo_subida["FAMILIA_CODCARPR_MANUAL"] = pd.NA
        archivo_subida["MANUAL_MATCH_STATUS"] = "SIN_CATALOGO_MANUAL"

    for idx in range(1, MAX_SIES_CODES_PER_KEY + 1):
        archivo_subida[f"CODIGO_CARRERA_SIES_{idx}"] = pd.NA
    archivo_subida["N_CODES_SIES"] = pd.NA
    archivo_subida["CODIGOS_SIES_POTENCIALES"] = pd.NA
    archivo_subida[FINAL_SIES_CODE_COL] = pd.NA

    if not df_bridge.empty:
        sies_cols = [
            "N_CODES_SIES",
            "CODIGOS_SIES_POTENCIALES",
        ] + [f"CODIGO_CARRERA_SIES_{idx}" for idx in range(1, MAX_SIES_CODES_PER_KEY + 1)]
        archivo_subida = archivo_subida.drop(columns=[c for c in sies_cols if c in archivo_subida.columns], errors="ignore")

        bridge_join_cols = [
            "BRIDGE_KEY_3",
            "GRUPO_TRAZA",
            "FAMILIA_TRAZA",
            "FAMILIA_CODCARPR",
            "N_CODES_SIES",
            "CODIGOS_SIES_POTENCIALES",
        ] + [f"CODIGO_CARRERA_SIES_{idx}" for idx in range(1, MAX_SIES_CODES_PER_KEY + 1)]
        bridge_exact = df_bridge[bridge_join_cols].rename(
            columns={
                "BRIDGE_KEY_3": "SOURCE_KEY_3",
                "GRUPO_TRAZA": "GRUPO_TRAZA_PUENTE",
                "FAMILIA_TRAZA": "FAMILIA_TRAZA_PUENTE",
                "FAMILIA_CODCARPR": "FAMILIA_CODCARPR_PUENTE",
            }
        )
        archivo_subida = archivo_subida.merge(bridge_exact, on="SOURCE_KEY_3", how="left")

        key_exact = set(df_bridge["BRIDGE_KEY_3"])
        key_no_jornada = set(df_bridge["BRIDGE_KEY_NO_JORNADA"])
        codcarpr_bridge = set(df_bridge["CODCARPR"])

        match_exact = archivo_subida["SOURCE_KEY_3"].isin(key_exact)
        exists_no_j = archivo_subida["KEY_3_NO_JORNADA"].isin(key_no_jornada)
        exists_cod = archivo_subida["CODCARPR_NORM"].isin(codcarpr_bridge)
        n_codes = pd.to_numeric(archivo_subida["N_CODES_SIES"], errors="coerce").fillna(0)

        archivo_subida["SIES_MATCH_STATUS"] = "SIN_MATCH_SIES"
        archivo_subida["SIES_MATCH_DIAG"] = "SIN_CODCARPR_EN_PUENTE_SIES"

        unique_mask = match_exact & (n_codes == 1)
        amb_mask = match_exact & (n_codes > 1)

        archivo_subida.loc[unique_mask, "SIES_MATCH_STATUS"] = "MATCH_SIES"
        archivo_subida.loc[unique_mask, "SIES_MATCH_DIAG"] = "MATCH_SIES_UNICO"
        archivo_subida.loc[unique_mask, FINAL_SIES_CODE_COL] = archivo_subida.loc[unique_mask, "CODIGO_CARRERA_SIES_1"]

        archivo_subida.loc[amb_mask, "SIES_MATCH_STATUS"] = "AMBIGUO_SIES"
        archivo_subida.loc[amb_mask, "SIES_MATCH_DIAG"] = "MATCH_SIES_AMBIGUO"

        archivo_subida.loc[(~match_exact) & exists_no_j, "SIES_MATCH_DIAG"] = "PROBABLE_PROBLEMA_JORNADA_SIES"
        archivo_subida.loc[(~match_exact) & (~exists_no_j) & exists_cod, "SIES_MATCH_DIAG"] = "PROBABLE_PROBLEMA_NOMBRE_SIES"
    else:
        archivo_subida["GRUPO_TRAZA_PUENTE"] = pd.NA
        archivo_subida["FAMILIA_TRAZA_PUENTE"] = pd.NA
        archivo_subida["FAMILIA_CODCARPR_PUENTE"] = pd.NA
        archivo_subida["SIES_MATCH_STATUS"] = "SIN_PUENTE_SIES"
        archivo_subida["SIES_MATCH_DIAG"] = "SIN_PUENTE_SIES"

    archivo_subida["GRUPO_TRAZA"] = archivo_subida["GRUPO_TRAZA_PUENTE"].combine_first(archivo_subida["GRUPO_TRAZA_MANUAL"])
    archivo_subida["FAMILIA_TRAZA"] = archivo_subida["GRUPO_TRAZA"].map(_extract_alpha_prefix)
    archivo_subida["FAMILIA_CODCARPR"] = archivo_subida["CODCARPR_NORM"].map(_extract_alpha_prefix)

    if excluir_diplomados:
        excl = archivo_subida["ES_DIPLOMADO"].fillna(False)
        archivo_subida.loc[excl, "SIES_MATCH_STATUS"] = "EXCLUIDO_DIPLOMADO"
        archivo_subida.loc[excl, "SIES_MATCH_DIAG"] = "EXCLUIDO_DIPLOMADO"
        archivo_subida.loc[excl, FINAL_SIES_CODE_COL] = pd.NA
        archivo_subida.loc[excl, "CODIGOS_SIES_POTENCIALES"] = pd.NA
        archivo_subida.loc[excl, "N_CODES_SIES"] = pd.NA
        for idx in range(1, MAX_SIES_CODES_PER_KEY + 1):
            archivo_subida.loc[excl, f"CODIGO_CARRERA_SIES_{idx}"] = pd.NA

    resumen = pd.DataFrame(
        [
            {"metrica": "filas_fuente", "valor": len(src)},
            {"metrica": "filas_archivo_subida", "valor": len(archivo_subida)},
            {"metrica": "rut_duplicados_vigentes", "valor": int(duplicated_vig.sum())},
            {"metrica": "matricula_ok_inicial", "valor": int((estado_inicial == "Matrícula OK").sum())},
            {"metrica": "matricula_duplicada_inicial", "valor": int((estado_inicial == "Matrícula Duplicada").sum())},
            {"metrica": "matricula_no_utilizada_inicial", "valor": int((estado_inicial == "Matrícula No Utilizada").sum())},
            {"metrica": "catalogo_manual_rows", "valor": len(df_manual)},
            {"metrica": "puente_sies_rows", "valor": len(df_bridge)},
            {"metrica": "excluir_diplomados", "valor": int(excluir_diplomados)},
        ]
    )
    resumen_manual = (
        archivo_subida["MANUAL_MATCH_STATUS"].fillna("<NA>").value_counts(dropna=False).rename_axis("estado").reset_index(name="n")
    )
    resumen_sies = (
        archivo_subida["SIES_MATCH_DIAG"].fillna("<NA>").value_counts(dropna=False).rename_axis("estado").reset_index(name="n")
    )
    ambiguos = archivo_subida[archivo_subida["SIES_MATCH_STATUS"] == "AMBIGUO_SIES"].copy()
    sin_match = archivo_subida[archivo_subida["SIES_MATCH_STATUS"] == "SIN_MATCH_SIES"].copy()

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / MU_FUSION_OUTPUT_FILENAME
    sheets_export: dict[str, pd.DataFrame] = {
        "ARCHIVO_LISTO_SUBIDA": archivo_subida,
        "RESUMEN_MU": resumen,
        "RESUMEN_MANUAL": resumen_manual,
        "RESUMEN_SIES": resumen_sies,
        "SIES_AMBIGUOS_POR_RESOL": ambiguos,
        "SIN_MATCH_SIES": sin_match,
    }
    if not df_manual.empty:
        sheets_export["CATALOGO_MANUAL"] = df_manual
    if not df_bridge.empty:
        sheets_export["PUENTE_SIES"] = df_bridge
    _write_excel_atomic(sheets_export, out_path)

    return {
        "output_file": str(out_path),
        "sheet_used": selected_sheet,
        "rows": len(archivo_subida),
        "estado_inicial": estado_inicial.value_counts(dropna=False).to_dict(),
        "manual_match": resumen_manual.set_index("estado")["n"].to_dict(),
        "sies_diag": resumen_sies.set_index("estado")["n"].to_dict(),
        "catalogo_manual_rows": len(df_manual),
        "puente_sies_rows": len(df_bridge),
        "catalogo_manual_source": manual_source,
        "puente_sies_source": puente_source,
    }


# ==============================
# CAPA C: Validación + Export
# ==============================
def _check_schema(df: pd.DataFrame, expected: list[str], area: str, issues: list[Issue]) -> None:
    if df.columns.tolist() != expected:
        issues.append(Issue("ERROR", area, "Schema exacto incumplido"))


def validar_carreras(carr: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []
    _check_schema(carr, CARRERAS_AC_COLUMNS, "carreras", issues)

    if carr["PLAN_ESTUDIOS"].isna().any():
        issues.append(Issue("ERROR", "carreras", "PLAN_ESTUDIOS vacío", int(carr["PLAN_ESTUDIOS"].isna().sum())))
    bad_tum = ~carr["TIPO_UNIDAD_MEDIDA"].astype(str).isin(["1", "2", "3"]) & carr["TIPO_UNIDAD_MEDIDA"].notna()
    if bad_tum.any():
        issues.append(Issue("ERROR", "carreras", "TIPO_UNIDAD_MEDIDA fuera de catálogo", int(bad_tum.sum())))
    tum3 = carr["TIPO_UNIDAD_MEDIDA"].astype(str) == "3"
    if tum3.any() and carr.loc[tum3, "OTRA_UNIDAD_MEDIDA"].isna().any():
        issues.append(
            Issue(
                "ERROR",
                "carreras",
                "OTRA_UNIDAD_MEDIDA faltante cuando TIPO_UNIDAD_MEDIDA=3",
                int(carr.loc[tum3, "OTRA_UNIDAD_MEDIDA"].isna().sum()),
            )
        )

    annual = carr[ANUAL_COLS].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    total = pd.to_numeric(carr["TOTAL_UNIDADES_MEDIDA"], errors="coerce")
    mismatch = total.notna() & (annual != total)
    if mismatch.any():
        issues.append(Issue("WARN", "carreras", "Suma de unidades anuales distinta al total", int(mismatch.sum())))

    vig_bad = ~carr["VIGENCIA"].astype(str).isin(["0", "1"]) & carr["VIGENCIA"].notna()
    if vig_bad.any():
        issues.append(Issue("ERROR", "carreras", "VIGENCIA fuera de catálogo 0/1", int(vig_bad.sum())))
    return issues


def validar_matricula_ac(mat: pd.DataFrame, carr: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []
    _check_schema(mat, MATRICULA_AC_COLUMNS, "matricula_ac", issues)

    for c in ["TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV", "CODIGO_UNICO", "PLAN_ESTUDIOS"]:
        if mat[c].isna().any():
            issues.append(Issue("ERROR", "matricula_ac", f"{c} vacío", int(mat[c].isna().sum())))

    bad_td = ~mat["TIPO_DOCUMENTO"].astype(str).isin(["R", "P"]) & mat["TIPO_DOCUMENTO"].notna()
    if bad_td.any():
        issues.append(Issue("ERROR", "matricula_ac", "TIPO_DOCUMENTO fuera de catálogo R/P", int(bad_td.sum())))
    bad_sex = ~mat["SEXO"].astype(str).isin(["M", "H", "X"]) & mat["SEXO"].notna()
    if bad_sex.any():
        issues.append(Issue("WARN", "matricula_ac", "SEXO fuera de catálogo M/H/X", int(bad_sex.sum())))

    bad_curso = ~mat["CURSO_1ER_SEM"].astype(str).isin(["SI", "NO"]) & mat["CURSO_1ER_SEM"].notna()
    bad_curso2 = ~mat["CURSO_2DO_SEM"].astype(str).isin(["SI", "NO"]) & mat["CURSO_2DO_SEM"].notna()
    if bad_curso.any() or bad_curso2.any():
        issues.append(
            Issue(
                "ERROR",
                "matricula_ac",
                "CURSO_1ER_SEM/CURSO_2DO_SEM fuera de catálogo SI/NO",
                int(bad_curso.sum() + bad_curso2.sum()),
            )
        )

    sem1 = pd.to_numeric(mat["SEM_INGRESO_CARRERA_ACTUAL"], errors="coerce")
    sem2 = pd.to_numeric(mat["SEM_INGRESO_CARRERA_ORIGEN"], errors="coerce")
    bad_sem = (~sem1.isin([1, 2]) & sem1.notna()) | (~sem2.isin([1, 2]) & sem2.notna())
    if bad_sem.any():
        issues.append(Issue("WARN", "matricula_ac", "Semestres de ingreso fuera de 1/2", int(bad_sem.sum())))

    apr_gt_cur = pd.to_numeric(mat["UNIDADES_APROBADAS"], errors="coerce") > pd.to_numeric(
        mat["UNIDADES_CURSADAS"], errors="coerce"
    )
    if apr_gt_cur.any():
        issues.append(Issue("WARN", "matricula_ac", "UNIDADES_APROBADAS > UNIDADES_CURSADAS", int(apr_gt_cur.sum())))

    aprt_gt_curt = pd.to_numeric(mat["UNID_APROBADAS_TOTAL"], errors="coerce") > pd.to_numeric(
        mat["UNID_CURSADAS_TOTAL"], errors="coerce"
    )
    if aprt_gt_curt.any():
        issues.append(Issue("WARN", "matricula_ac", "UNID_APROBADAS_TOTAL > UNID_CURSADAS_TOTAL", int(aprt_gt_curt.sum())))

    keys_c = set(map(tuple, carr[["CODIGO_UNICO", "PLAN_ESTUDIOS"]].dropna().drop_duplicates().to_records(index=False)))
    keys_m = set(map(tuple, mat[["CODIGO_UNICO", "PLAN_ESTUDIOS"]].dropna().drop_duplicates().to_records(index=False)))
    if keys_m - keys_c:
        issues.append(Issue("ERROR", "matricula_ac", "PLAN_ESTUDIOS no referenciado en carreras", len(keys_m - keys_c)))
    return issues


def validar_matricula_unificada(mu: pd.DataFrame) -> list[Issue]:
    issues: list[Issue] = []
    _check_schema(mu, MATRICULA_UNIFICADA_COLUMNS, "matricula_unificada", issues)

    vig_bad = ~mu["VIG"].astype(str).isin(["0", "1"]) & mu["VIG"].notna()
    if vig_bad.any():
        issues.append(Issue("ERROR", "matricula_unificada", "VIG fuera de catálogo 0/1", int(vig_bad.sum())))

    reinc_bad = ~mu["REINCORPORACION"].astype(str).isin(["0", "1"]) & mu["REINCORPORACION"].notna()
    if reinc_bad.any():
        issues.append(Issue("ERROR", "matricula_unificada", "REINCORPORACION fuera de 0/1", int(reinc_bad.sum())))
    if mu["REINCORPORACION"].isna().any():
        issues.append(
            Issue(
                "BLOCKER",
                "matricula_unificada",
                "REINCORPORACION obligatorio vacío",
                int(mu["REINCORPORACION"].isna().sum()),
            )
        )

    if mu["PAIS_EST_SEC"].isna().any():
        issues.append(
            Issue("BLOCKER", "matricula_unificada", "PAIS_EST_SEC obligatorio vacío", int(mu["PAIS_EST_SEC"].isna().sum()))
        )

    fechas = pd.to_datetime(mu["FECHA_MATRICULA"], errors="coerce")
    futuras = fechas.notna() & (fechas > pd.Timestamp.today().normalize())
    if futuras.any():
        issues.append(Issue("ERROR", "matricula_unificada", "FECHA_MATRICULA posterior a fecha de carga", int(futuras.sum())))

    mod_missing = mu["COD_CAR"].notna() & mu["MODALIDAD"].isna()
    if mod_missing.any():
        issues.append(
            Issue(
                "WARN",
                "matricula_unificada",
                "COD_CAR con MODALIDAD no resuelta (equivalencia dudosa)",
                int(mod_missing.sum()),
            )
        )
    return issues


def exportar_control_y_pes(
    df: pd.DataFrame, control_path: Path, pes_path: Path, issues: list[Issue], area: str
) -> None:
    df.to_csv(control_path, index=False, encoding="utf-8")
    if "CODIGO_IES_NUM" not in df.columns:
        issues.append(Issue("ERROR", area, "No existe CODIGO_IES_NUM para generar pes_ready"))
        return
    pes = df.drop(columns=["CODIGO_IES_NUM"])
    pes.to_csv(pes_path, index=False, header=False, encoding="utf-8")


def _profile_column(series: pd.Series) -> dict[str, float]:
    s = series.astype(object)
    null_pct = float(s.isna().mean())
    zero_pct = float((pd.to_numeric(s, errors="coerce") == 0).fillna(False).mean())
    default_like_pct = float(s.fillna("").astype(str).str.strip().isin(["", "0", "NO", "N/A", "NA"]).mean())
    return {
        "null_pct": round(null_pct, 4),
        "zero_pct": round(zero_pct, 4),
        "default_like_pct": round(default_like_pct, 4),
    }


def generar_procedencia_y_calidad(
    output_dir: Path, mu: pd.DataFrame, ca: pd.DataFrame, ma: pd.DataFrame, issues: list[Issue]
) -> dict[str, object]:
    provenance_rules = {
        "matricula_unificada": {
            "TIPO_DOC": "source_exact",
            "N_DOC": "source_exact",
            "DV": "source_exact",
            "COD_CAR": "manual_mapping",
            "MODALIDAD": "manual_mapping",
            "JOR": "manual_mapping",
            "ANIO_ING_ACT": "source_exact",
            "SEM_ING_ACT": "source_exact",
            "ANIO_ING_ORI": "source_exact",
            "SEM_ING_ORI": "source_exact",
            "VIG": "source_exact",
            "PAIS_EST_SEC": "missing_blocker",
            "REINCORPORACION": "missing_blocker",
        },
        "carreras_ac": {c: "template_preserved" for c in CARRERAS_AC_COLUMNS},
        "matricula_ac": {c: "template_preserved" for c in MATRICULA_AC_COLUMNS},
    }

    for c in [
        "CURSO_1ER_SEM",
        "CURSO_2DO_SEM",
        "UNIDADES_CURSADAS",
        "UNIDADES_APROBADAS",
        "UNID_CURSADAS_TOTAL",
        "UNID_APROBADAS_TOTAL",
    ]:
        provenance_rules["matricula_ac"][c] = "derived_rule"

    frames = {"matricula_unificada": mu, "carreras_ac": ca, "matricula_ac": ma}
    out_rows = []
    summary: dict[str, object] = {}

    for name, df in frames.items():
        rows = []
        for col in df.columns:
            prov = provenance_rules.get(name, {}).get(col, "source_normalized")
            profile = _profile_column(df[col])
            row = {"archivo": name, "columna": col, "provenance": prov, **profile}
            if prov == "missing_blocker" and profile["null_pct"] > 0.2:
                issues.append(Issue("BLOCKER", name, f"{col} con missing_blocker masivo", int(profile["null_pct"] * len(df))))
            if col in {
                "CURSO_1ER_SEM",
                "CURSO_2DO_SEM",
                "UNIDADES_CURSADAS",
                "UNIDADES_APROBADAS",
                "UNID_CURSADAS_TOTAL",
                "UNID_APROBADAS_TOTAL",
            } and profile["default_like_pct"] > 0.8:
                sev = "BLOCKER" if col in {"UNIDADES_CURSADAS", "UNID_CURSADAS_TOTAL"} else "ERROR"
                issues.append(Issue(sev, name, f"{col} con default_like_pct alto", int(profile["default_like_pct"] * len(df))))
            rows.append(row)

        t = pd.DataFrame(rows)
        summary[name] = {
            "avg_null_pct": round(float(t["null_pct"].mean()), 4),
            "avg_default_like_pct": round(float(t["default_like_pct"].mean()), 4),
            "provenance_pct": {k: round(float((t["provenance"] == k).mean()), 4) for k in t["provenance"].unique()},
        }
        out_rows.extend(rows)

    prov_df = pd.DataFrame(out_rows)
    prov_df.to_csv(output_dir / "reporte_procedencia.csv", index=False, encoding="utf-8")
    (output_dir / "reporte_calidad_semantica.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def ejecutar_pipeline(input_file: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    issues: list[Issue] = []

    carreras_raw, mat_raw, hist_raw, equiv = cargar_fuentes(input_file)

    mat_i = preparar_matricula_intermedia(mat_raw)
    bridge, diag_amb = construir_puente_equiv(equiv)
    hist_map, review_nomap = mapear_historico_con_equiv(hist_raw, bridge)
    resumen = construir_resumen_historico(hist_map)

    carreras_ctrl = construir_carreras_control(carreras_raw)
    matac_ctrl = construir_matricula_ac_control(mat_i, resumen)
    mu_ctrl = construir_matricula_unificada_control(matac_ctrl, equiv)

    issues.extend(validar_carreras(carreras_ctrl))
    issues.extend(validar_matricula_ac(matac_ctrl, carreras_ctrl))
    issues.extend(validar_matricula_unificada(mu_ctrl))

    mu_ctrl.to_csv(output_dir / "matricula_unificada_2026_control.csv", index=False, encoding="utf-8")
    mu_ctrl.to_excel(output_dir / "matricula_unificada_2026_oficial.xlsx", index=False)
    exportar_control_y_pes(
        carreras_ctrl,
        output_dir / "carreras_avance_curricular_2025_control.csv",
        output_dir / "carreras_avance_curricular_2025_pes_ready.csv",
        issues,
        "carreras",
    )
    exportar_control_y_pes(
        matac_ctrl,
        output_dir / "matricula_avance_curricular_2025_control.csv",
        output_dir / "matricula_avance_curricular_2025_pes_ready.csv",
        issues,
        "matricula_ac",
    )

    diag_amb.to_csv(output_dir / "sies_ambiguedad_diagnostico.csv", index=False, encoding="utf-8")
    review_nomap.to_csv(output_dir / "sies_codcarr_sin_mapeo.csv", index=False, encoding="utf-8")

    calidad_semantica = generar_procedencia_y_calidad(output_dir, mu_ctrl, carreras_ctrl, matac_ctrl, issues)

    report = {
        "rows": {
            "carreras_control": len(carreras_ctrl),
            "matricula_ac_control": len(matac_ctrl),
            "matricula_unificada_control": len(mu_ctrl),
            "historico_total": len(hist_raw),
            "historico_mapeado": int(hist_map["CODIGO_UNICO"].notna().sum()),
            "historico_sin_mapeo": int(hist_map["CODIGO_UNICO"].isna().sum()),
        },
        "issues": [i.__dict__ for i in issues],
        "ambiguedad": {
            "codcarr_total": int(len(diag_amb)),
            "codcarr_ambiguos": int(diag_amb["es_ambiguo"].sum()) if not diag_amb.empty else 0,
        },
        "calidad_semantica": calidad_semantica,
        "apto_oficial": {
            "matricula_unificada": not any(
                i.severity in {"BLOCKER", "ERROR"} and i.area in {"matricula_unificada"} for i in issues
            ),
            "avance_curricular": not any(
                i.severity in {"BLOCKER", "ERROR"} and i.area in {"carreras", "matricula_ac", "carreras_ac"}
                for i in issues
            ),
        },
    }
    (output_dir / "reporte_validacion.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def generar_comparacion_versiones(output_dir: Path) -> None:
    md = """# Comparación evolutiva de pipeline

| Dimensión | Versión actual previa | Idea histórica (referencia) | Decisión híbrida aplicada |
|---|---|---|---|
| Granularidad AC | colapsaba por RUT | mantener múltiples programas | deduplicación por clave de negocio, no por RUT |
| Equivalencias | `drop_duplicates(CODCARR)` | no forzar ambiguos | mapeo por `(CODCARR,JORNADA)` y fallback solo si CODCARR único |
| Validación | schema + catálogos | auditoría por bloques | capas A/B/C + issues con severidad |
| Exportación PES | quitaba primera columna por índice | contrato explícito | quitar `CODIGO_IES_NUM` por nombre |
| Defaults sensibles | rellenos por defecto | evitar inventar | `PAIS_EST_SEC` y `REINCORPORACION` quedan BLOCKER si faltan |
| Ambigüedad SIES | diagnóstico simple | revisión consolidada | diagnóstico + archivo de `CODCARR` sin mapeo |
"""
    (output_dir / "comparacion_versiones.md").write_text(md, encoding="utf-8")


def generar_diccionario_columnas(output_dir: Path) -> None:
    rows = [
        ("MODALIDAD", "respaldada por manual"),
        ("VIG", "respaldada por manual"),
        ("COD_CAR", "respaldada por código"),
        ("ANIO_ING_ACT", "respaldada por código"),
        ("SEM_ING_ACT", "respaldada por código"),
        ("ANIO_ING_ORI", "respaldada por código"),
        ("SEM_ING_ORI", "respaldada por código"),
    ]
    known = {r[0] for r in rows}
    rows.extend((c, "inferencia operativa / pendiente de validación documental") for c in MATRICULA_UNIFICADA_COLUMNS if c not in known)
    lines = ["# Diccionario de columnas y clasificación", "", "| Columna | Clasificación |", "|---|---|"]
    lines.extend(f"| {c} | {k} |" for c, k in rows)
    (output_dir / "diccionario_columnas.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pipeline híbrido SIES/PES")
    p.add_argument(
        "--input",
        default=_default_input_arg(),
        help="Ruta del Excel de entrada (por defecto detecta PROMEDIOSDEALUMNOS_7804.xlsx si existe).",
    )
    p.add_argument("--output-dir", default="resultados", help="Carpeta de salida")
    p.add_argument(
        "--proceso",
        default="avance",
        choices=["avance", "matricula", "ambos"],
        help="Qué pipeline ejecutar: avance curricular, matrícula unificada (legacy-like) o ambos",
    )
    p.add_argument(
        "--sheet",
        default=None,
        help="Nombre de hoja para el proceso matrícula (por defecto usa la primera)",
    )
    p.add_argument(
        "--catalogo-manual-tsv",
        default=None,
        help="Ruta a TSV de catálogo manual (opcional). Si no se informa, usa CATALOGO_MANUAL_TSV embebido.",
    )
    p.add_argument(
        "--puente-sies-tsv",
        default=None,
        help="Ruta a TSV puente SIES (opcional). Si no se informa, usa PUENTE_SIES_TSV embebido.",
    )
    p.add_argument(
        "--excluir-diplomados",
        choices=["true", "false"],
        default="true" if DEFAULT_EXCLUIR_DIPLOMADOS else "false",
        help="Para proceso matrícula: excluir diplomados en asignación SIES.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"No se encontró archivo de entrada: {input_path}. Usa --input para indicar uno válido.")

    out = Path(args.output_dir).expanduser().resolve()
    reports: dict[str, object] = {}

    if args.proceso in {"avance", "ambos"}:
        report_avance = ejecutar_pipeline(input_path, out)
        generar_comparacion_versiones(out)
        generar_diccionario_columnas(out)
        reports["avance"] = report_avance

    if args.proceso in {"matricula", "ambos"}:
        catalogo_manual_tsv_path = _resolve_optional_path(args.catalogo_manual_tsv, DEFAULT_CATALOGO_MANUAL_CANDIDATES)
        puente_sies_tsv_path = _resolve_optional_path(args.puente_sies_tsv, DEFAULT_PUENTE_SIES_CANDIDATES)
        report_mu = ejecutar_pipeline_matricula_unificada_legacy_like(
            input_path,
            out,
            sheet_name=args.sheet,
            catalogo_manual_tsv_path=catalogo_manual_tsv_path,
            puente_sies_tsv_path=puente_sies_tsv_path,
            excluir_diplomados=(args.excluir_diplomados == "true"),
        )
        reports["matricula"] = report_mu

    if args.proceso == "avance":
        print(json.dumps(reports["avance"], indent=2, ensure_ascii=False))
    elif args.proceso == "matricula":
        print(json.dumps(reports["matricula"], indent=2, ensure_ascii=False))
    else:
        print(json.dumps(reports, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

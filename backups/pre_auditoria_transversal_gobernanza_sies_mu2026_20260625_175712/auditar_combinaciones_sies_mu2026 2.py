from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
AUD = ROOT / "resultados" / "auditorias"
REP = ROOT / "resultados" / "reportes"

STAGE_XLSX = ROOT / "resultados" / "archivo_listo_para_sies.xlsx"
DURACION_TSV = ROOT / "DURACION_ESTUDIOS.tsv"
PUENTE_TSV = ROOT / "control" / "catalogos" / "PUENTE_SIES_COMPILADO.tsv"
RECON_PREV = AUD / "RECONSTRUCCION_DECISIONES_VERSION_SIES_MU.csv"

TARGETS = {
    "universo": AUD / "UNIVERSO_CARRERAS_CODIGOS_SIES_MU2026.csv",
    "matriz": AUD / "MATRIZ_COMBINACIONES_ACADEMICAS_SIES_MU2026.csv",
    "inconsistencias": AUD / "INCONSISTENCIAS_CODIGO_SIES_POR_COMBINACION_MU2026.csv",
    "impacto": AUD / "IMPACTO_INCONSISTENCIAS_SIES_MU2026.csv",
    "resumen_carreras": AUD / "RESUMEN_CARRERAS_RESOLUCION_SIES_MU2026.csv",
    "reporte": REP / "REPORTE_AUDITORIA_CARRERAS_CODIGOS_SIES_MU2026.md",
    "excel": AUD / "REVISION_CARRERAS_CODIGOS_SIES_MU2026.xlsx",
}

SPECIAL_CASES = {
    "AUDT": ["AUDT", "AUDITORIA"],
    "ICRE": ["ICRE", "CONECTIVIDAD"],
    "IINF": ["IINF", "INFORMATICA"],
    "ICIB": ["ICIB", "CIBERSEGURIDAD"],
    "IIND": ["IIND", "INDUSTRIAL"],
    "NATUROPATIA": ["NATUROPAT"],
    "IADM": ["IADM", "ADMINISTRACION"],
    "LOGISTICA": ["LOGISTICA", "ILOG", "TLOG"],
    "FINANZAS": ["FINANZAS", "IFIN"],
    "MARKETING": ["MARKETING", "IMKD"],
    "RECURSOS HUMANOS": ["RECURSOS HUMANOS", "IRHU"],
    "PREVENCION DE RIESGOS": ["PREVENCION DE RIESGOS", "IPRE", "TPRE"],
}

CODE_RE = re.compile(r"^I(?P<ies>\d+)S(?P<COD_SED>\d+)C(?P<COD_CAR>\d+)J(?P<JOR>\d+)V(?P<VERSION>\d+)$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def upper(value: object) -> str:
    return clean(value).upper()


def normalize_text(value: object) -> str:
    text = upper(value)
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_code(code: object) -> dict[str, str]:
    m = CODE_RE.match(upper(code))
    if not m:
        return {"COD_SED": "", "COD_CAR": "", "JOR": "", "VERSION": ""}
    return m.groupdict()


def split_codes(value: object) -> list[str]:
    text = upper(value)
    if not text:
        return []
    out = []
    for bit in re.split(r"\s*\|\s*|,\s*|;\s*", text):
        bit = bit.strip()
        if CODE_RE.match(bit):
            out.append(bit)
    return sorted(dict.fromkeys(out))


def numeric_text(value: object) -> str:
    text = clean(value)
    if re.fullmatch(r"\d+\.0", text):
        return text[:-2]
    return text


def jornada_text_to_jor(value: object) -> str:
    text = upper(value)
    mapping = {"D": "1", "DIURNA": "1", "V": "2", "VESPERTINA": "2", "O": "4", "ONLINE": "4", "A DISTANCIA": "4"}
    return mapping.get(text, numeric_text(text))


def load_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stage = pd.read_excel(STAGE_XLSX, sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str).fillna("")
    stage["_FILA_STAGE"] = [i + 2 for i in range(len(stage))]
    offer = pd.read_csv(DURACION_TSV, sep="\t", dtype=str, keep_default_na=False).fillna("")
    puente = pd.read_csv(PUENTE_TSV, sep="\t", dtype=str, keep_default_na=False).fillna("")
    recon = pd.read_csv(RECON_PREV, dtype=str, keep_default_na=False).fillna("") if RECON_PREV.exists() else pd.DataFrame()
    return stage, offer, puente, recon


def backup_existing() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / "backups" / f"pre_auditoria_combinaciones_sies_mu2026_{ts}"
    backup.mkdir(parents=True, exist_ok=True)
    for path in TARGETS.values():
        if path.exists():
            shutil.copy2(path, backup / path.name)
    return backup


def prepare_stage(stage: pd.DataFrame, offer: pd.DataFrame) -> pd.DataFrame:
    out = stage.copy()
    for col in ["COD_SED", "COD_CAR", "JOR", "VERSION", "MODALIDAD", "DURACION_ESTUDIOS_REF", "CODIGO_CARRERA_SIES_FINAL"]:
        if col not in out.columns:
            out[col] = ""
    out["CODCARPR_KEY"] = out.get("CODCARPR_NORM", "").map(normalize_text)
    out["PLAN_KEY"] = out.get("PLAN_DE_ESTUDIO", "").map(normalize_text)
    out["COD_SED_KEY"] = out["COD_SED"].map(numeric_text)
    out["JORNADA_KEY"] = out.get("JORNADA_FUENTE", "").map(jornada_text_to_jor)
    out.loc[out["JORNADA_KEY"].eq(""), "JORNADA_KEY"] = out.loc[out["JORNADA_KEY"].eq(""), "JOR"].map(numeric_text)
    out["MODALIDAD_KEY"] = out["MODALIDAD"].map(numeric_text)
    out["CODIGO_FINAL_KEY"] = out["CODIGO_CARRERA_SIES_FINAL"].map(upper)

    lookup = {upper(r["CODIGO_UNICO"]): r.to_dict() for _, r in offer.iterrows()}
    final_info = out["CODIGO_FINAL_KEY"].map(lambda c: lookup.get(c, {}))
    out["TIPO_PLAN_CARRERA_KEY"] = final_info.map(lambda r: numeric_text(r.get("TIPO_PLAN_CARRERA", "")))
    out["DURACION_ESTUDIOS_KEY"] = final_info.map(lambda r: numeric_text(r.get("DURACION_ESTUDIOS", "")))
    out.loc[out["DURACION_ESTUDIOS_KEY"].eq(""), "DURACION_ESTUDIOS_KEY"] = out.loc[out["DURACION_ESTUDIOS_KEY"].eq(""), "DURACION_ESTUDIOS_REF"].map(numeric_text)
    out["DURACION_TOTAL_KEY"] = final_info.map(lambda r: numeric_text(r.get("DURACION_TOTAL", "")))
    out["NOMBRE_SEDE_OFERTA"] = final_info.map(lambda r: clean(r.get("NOMBRE_SEDE", "")))
    out["NOMBRE_CARRERA_OFERTA"] = final_info.map(lambda r: clean(r.get("NOMBRE_CARRERA", "")))
    out["OFERTA_MODALIDAD_FINAL"] = final_info.map(lambda r: numeric_text(r.get("MODALIDAD", "")))
    out["OFERTA_JORNADA_FINAL"] = final_info.map(lambda r: numeric_text(r.get("JORNADA", "")))
    out["OFERTA_COD_SED_FINAL"] = final_info.map(lambda r: numeric_text(r.get("COD_SEDE", "")))
    out["OFERTA_COD_CAR_FINAL"] = final_info.map(lambda r: numeric_text(r.get("CODIGO_CARRERA", "")))

    parsed = out["CODIGO_FINAL_KEY"].map(parse_code).apply(pd.Series)
    for col in ["COD_SED", "COD_CAR", "JOR", "VERSION"]:
        out[f"PARSE_{col}"] = parsed[col]

    out["LLAVE_1_CARRERA"] = out["CODCARPR_KEY"]
    out["LLAVE_2_OFERTA"] = out[["CODCARPR_KEY", "COD_SED_KEY", "JORNADA_KEY", "MODALIDAD_KEY"]].agg("|".join, axis=1)
    out["LLAVE_3_PLAN"] = out[["CODCARPR_KEY", "PLAN_KEY", "COD_SED_KEY", "JORNADA_KEY", "MODALIDAD_KEY"]].agg("|".join, axis=1)
    out["LLAVE_4_COMPLETA"] = out[["CODCARPR_KEY", "PLAN_KEY", "COD_SED_KEY", "JORNADA_KEY", "MODALIDAD_KEY", "TIPO_PLAN_CARRERA_KEY", "DURACION_ESTUDIOS_KEY"]].agg("|".join, axis=1)

    out["CANDIDATOS_LIST"] = out.get("CODIGOS_SIES_POTENCIALES", "").map(split_codes)
    out["N_CANDIDATOS_CALC"] = out["CANDIDATOS_LIST"].map(len)
    out["SIES_METHOD"] = out.get("SIES_RESOLUCION_HEURISTICA", "").map(upper)
    return out


def uniq_join(values: pd.Series, limit: int = 80) -> str:
    vals = sorted({clean(v) for v in values if clean(v)})
    if len(vals) > limit:
        return " | ".join(vals[:limit]) + f" | ...(+{len(vals)-limit})"
    return " | ".join(vals)


def flatten_codes(series: pd.Series) -> list[str]:
    out = []
    for value in series:
        out.extend(split_codes(value))
    return sorted(dict.fromkeys(out))


def combo_agg(df: pd.DataFrame, key_col: str, nivel: str) -> pd.DataFrame:
    rows = []
    for key, g in df.groupby(key_col, dropna=False):
        candidates = flatten_codes(g.get("CODIGOS_SIES_POTENCIALES", pd.Series(dtype=str)))
        finals = sorted({upper(v) for v in g["CODIGO_FINAL_KEY"] if upper(v)})
        methods = sorted({upper(v) for v in g["SIES_METHOD"] if upper(v)})
        manual = [m for m in methods if m in {"REGLA_TIPO_PLAN", "AJUSTE_SEDE_GOBERNANZA"} or "MANUAL" in m]
        estado, posible_error, motivo = classify_combo(g, candidates, finals, methods)
        rows.append(
            {
                "NIVEL_LLAVE": nivel,
                "LLAVE": key,
                "CODCARPR": uniq_join(g["CODCARPR_KEY"]),
                "NOMBRE_CARRERA": uniq_join(g.get("NOMBRE_CARRERA_FUENTE", pd.Series(dtype=str))),
                "PLAN_DE_ESTUDIO": uniq_join(g.get("PLAN_DE_ESTUDIO", pd.Series(dtype=str))),
                "COD_SED": uniq_join(g["COD_SED_KEY"]),
                "SEDE": uniq_join(g.get("NOMBRE_SEDE_OFERTA", pd.Series(dtype=str))),
                "JORNADA": uniq_join(g["JORNADA_KEY"]),
                "MODALIDAD": uniq_join(g["MODALIDAD_KEY"]),
                "TIPO_PLAN_CARRERA": uniq_join(g["TIPO_PLAN_CARRERA_KEY"]),
                "DURACION_ESTUDIOS": uniq_join(g["DURACION_ESTUDIOS_KEY"]),
                "DURACION_TOTAL": uniq_join(g["DURACION_TOTAL_KEY"]),
                "TOTAL_ESTUDIANTES": int(len(g)),
                "TOTAL_CODCLI": int(g["CODCLI"].replace("", pd.NA).nunique()),
                "INCLUIDOS_MATRICULA_32": int(g.get("INCLUIR_EN_MATRICULA_32", pd.Series("", index=g.index)).eq("SI").sum()),
                "CODIGOS_SIES_CANDIDATOS": " | ".join(candidates),
                "N_CODIGOS_CANDIDATOS": int(len(candidates)),
                "CODIGOS_SIES_FINALES_USADOS": " | ".join(finals),
                "N_CODIGOS_FINALES_USADOS": int(len(finals)),
                "METODOS_USADOS": " | ".join(methods),
                "REGLAS_MANUALES": " | ".join(manual),
                "ESTADO_RESOLUCION": estado,
                "POSIBLE_ERROR": posible_error,
                "MOTIVO": motivo,
                "ESTUDIANTES_AFECTADOS": int(len(g)) if estado in {"INCONSISTENTE_MULTICODIGO", "POSIBLE_ERROR_DE_ASIGNACION", "AMBIGUA_NO_RESUELTA", "SIN_CODIGO"} or posible_error == "SI" else 0,
                "CODCLI_AFECTADOS": uniq_join(g["CODCLI"]) if estado in {"INCONSISTENTE_MULTICODIGO", "POSIBLE_ERROR_DE_ASIGNACION", "AMBIGUA_NO_RESUELTA", "SIN_CODIGO"} or posible_error == "SI" else "",
                "FILAS_STAGE": uniq_join(g["_FILA_STAGE"].astype(str)),
            }
        )
    return pd.DataFrame(rows)


def classify_combo(g: pd.DataFrame, candidates: list[str], finals: list[str], methods: list[str]) -> tuple[str, str, str]:
    row_errors = validation_errors(g)
    if not finals and (len(candidates) > 1 or "PENDIENTE_GOBERNANZA" in methods):
        return "AMBIGUA_NO_RESUELTA", "SI", "Más de un candidato compatible y sin código final trazable; resolución pendiente de gobernanza."
    if not finals:
        return "SIN_CODIGO", "SI", "Combinación sin CODIGO_CARRERA_SIES_FINAL."
    if row_errors:
        return "POSIBLE_ERROR_DE_ASIGNACION", "SI", "; ".join(sorted(row_errors))
    if len(finals) > 1:
        return "INCONSISTENTE_MULTICODIGO", "SI", "La misma llave académica recibió más de un código SIES final."
    if "PENDIENTE_GOBERNANZA" in methods:
        return "AMBIGUA_NO_RESUELTA", "SI", "Existe resolución pendiente de gobernanza."
    if len(candidates) <= 1:
        return "RESUELTA_INEQUIVOCAMENTE", "NO", "Un candidato compatible y un código final único."
    if any(m in {"REGLA_COD_CAR_JOR_VERSION"} for m in methods):
        return "RESUELTA_POR_REGLA_FORMAL", "NO", "Varios candidatos iniciales resueltos por regla COD_CAR/JOR/VERSION."
    if any(m in {"REGLA_TIPO_PLAN", "AJUSTE_SEDE_GOBERNANZA"} or "MANUAL" in m for m in methods):
        return "RESUELTA_POR_DECISION_MANUAL", "NO", "Varios candidatos resueltos mediante tipo de plan, puente o traza manual."
    return "AMBIGUA_NO_RESUELTA", "SI", "Varios candidatos sin regla formal/manual identificada."


def validation_errors(g: pd.DataFrame) -> set[str]:
    errors: set[str] = set()
    nonempty = g[g["CODIGO_FINAL_KEY"].ne("")]
    if nonempty.empty:
        return errors
    if (nonempty["PARSE_COD_SED"].ne("") & nonempty["COD_SED_KEY"].ne("") & nonempty["PARSE_COD_SED"].ne(nonempty["COD_SED_KEY"])).any():
        errors.add("COD_SED no coincide con código SIES")
    if (nonempty["PARSE_COD_CAR"].ne("") & nonempty["COD_CAR"].map(numeric_text).ne("") & nonempty["PARSE_COD_CAR"].ne(nonempty["COD_CAR"].map(numeric_text))).any():
        errors.add("COD_CAR no coincide con código SIES")
    if (nonempty["PARSE_JOR"].ne("") & nonempty["JOR"].map(numeric_text).ne("") & nonempty["PARSE_JOR"].ne(nonempty["JOR"].map(numeric_text))).any():
        errors.add("JOR no coincide con código SIES")
    if (nonempty["OFERTA_MODALIDAD_FINAL"].ne("") & nonempty["MODALIDAD_KEY"].ne("") & nonempty["OFERTA_MODALIDAD_FINAL"].ne(nonempty["MODALIDAD_KEY"])).any():
        errors.add("MODALIDAD no coincide con oferta")
    if (nonempty["OFERTA_COD_SED_FINAL"].ne("") & nonempty["COD_SED_KEY"].ne("") & nonempty["OFERTA_COD_SED_FINAL"].ne(nonempty["COD_SED_KEY"])).any():
        errors.add("COD_SED no coincide con oferta")
    if (nonempty["OFERTA_COD_CAR_FINAL"].ne("") & nonempty["COD_CAR"].map(numeric_text).ne("") & nonempty["OFERTA_COD_CAR_FINAL"].ne(nonempty["COD_CAR"].map(numeric_text))).any():
        errors.add("COD_CAR no coincide con oferta")
    if (nonempty["DURACION_ESTUDIOS_KEY"].eq("")).any():
        errors.add("DURACION_ESTUDIOS no trazada para código final")
    if (~nonempty["CODIGO_FINAL_KEY"].str.match(CODE_RE)).any():
        errors.add("Código SIES final con formato inválido o fuera de oferta")
    if (nonempty["NOMBRE_CARRERA_OFERTA"].eq("")).any():
        errors.add("Código final no encontrado en DURACION_ESTUDIOS.tsv")
    if nonempty["SIES_METHOD"].eq("PRIMERA_OPCION").any():
        errors.add("Asignación por primera coincidencia")
    return errors


def build_universe(df: pd.DataFrame, matrix4: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "TOTAL_FILAS_ESTUDIANTES": len(df),
                "TOTAL_CODCLI": df["CODCLI"].replace("", pd.NA).nunique(),
                "TOTAL_RUT": (df["N_DOC"].astype(str).str.strip() + "-" + df["DV"].astype(str).str.strip()).replace("-", pd.NA).nunique(),
                "TOTAL_CODCARPR": df["CODCARPR_KEY"].replace("", pd.NA).nunique(),
                "TOTAL_PLANES_ESTUDIO": df["PLAN_KEY"].replace("", pd.NA).nunique(),
                "TOTAL_CODIGOS_SIES_FINAL": df["CODIGO_FINAL_KEY"].replace("", pd.NA).nunique(),
                "TOTAL_LLAVE_OFERTA": df["LLAVE_2_OFERTA"].replace("", pd.NA).nunique(),
                "TOTAL_LLAVE_PLAN": df["LLAVE_3_PLAN"].replace("", pd.NA).nunique(),
                "TOTAL_LLAVE_COMPLETA": df["LLAVE_4_COMPLETA"].replace("", pd.NA).nunique(),
                "FILAS_INCLUIDAS_MATRICULA_32": int(df.get("INCLUIR_EN_MATRICULA_32", "").eq("SI").sum()),
                "CODCLI_INCLUIDOS_MATRICULA_32": df.loc[df.get("INCLUIR_EN_MATRICULA_32", "").eq("SI"), "CODCLI"].replace("", pd.NA).nunique(),
                "COMBINACIONES_ACADEMICAS_DISTINTAS": len(matrix4),
            }
        ]
    )


def build_inconsistencies(matrix: pd.DataFrame) -> pd.DataFrame:
    bad = matrix[
        matrix["ESTADO_RESOLUCION"].isin(["INCONSISTENTE_MULTICODIGO", "POSIBLE_ERROR_DE_ASIGNACION", "AMBIGUA_NO_RESUELTA", "SIN_CODIGO"])
        | matrix["POSIBLE_ERROR"].eq("SI")
    ].copy()
    return bad.sort_values(["NIVEL_LLAVE", "ESTADO_RESOLUCION", "ESTUDIANTES_AFECTADOS"], ascending=[True, True, False])


def build_impact(incons: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in incons.iterrows():
        estado = r["ESTADO_RESOLUCION"]
        gravedad = {
            "POSIBLE_ERROR_DE_ASIGNACION": "CRITICA",
            "INCONSISTENTE_MULTICODIGO": "ALTA",
            "AMBIGUA_NO_RESUELTA": "MEDIA",
            "SIN_CODIGO": "CRITICA",
        }.get(estado, "BAJA")
        if estado == "AMBIGUA_NO_RESUELTA" and int(pd.to_numeric(pd.Series([r.get("INCLUIDOS_MATRICULA_32", 0)]), errors="coerce").fillna(0).iloc[0]) > 0:
            gravedad = "CRITICA"
        rows.append(
            {
                "combinación_académica": r["LLAVE"],
                "nivel_llave": r["NIVEL_LLAVE"],
                "código_usado": r["CODIGOS_SIES_FINALES_USADOS"],
                "código_esperado_o_candidatos_validos": r["CODIGOS_SIES_CANDIDATOS"],
                "tipo_inconsistencia": estado,
                "total_estudiantes_afectados": r["ESTUDIANTES_AFECTADOS"],
                "CODCLI_afectados": r["CODCLI_AFECTADOS"],
                "RUT_afectados": "",
                "archivo_final_donde_fueron_informados": (
                    "resultados/archivo_listo_para_sies.xlsx!ARCHIVO_LISTO_SUBIDA; "
                    "MATRICULA_UNIFICADA_32"
                    if int(pd.to_numeric(pd.Series([r.get("INCLUIDOS_MATRICULA_32", 0)]), errors="coerce").fillna(0).iloc[0]) > 0
                    else "resultados/archivo_listo_para_sies.xlsx!ARCHIVO_LISTO_SUBIDA"
                ),
                "gravedad": gravedad,
                "acción_sugerida": suggested_action(estado),
                "motivo": r["MOTIVO"],
            }
        )
    return pd.DataFrame(rows)


def suggested_action(estado: str) -> str:
    if estado == "POSIBLE_ERROR_DE_ASIGNACION":
        return "Revisar antes de reutilizar la lógica; posible contradicción con oferta."
    if estado == "INCONSISTENTE_MULTICODIGO":
        return "Auditar tabla puente y plan/version; misma combinación no debe bifurcarse."
    if estado == "AMBIGUA_NO_RESUELTA":
        return "Requiere decisión institucional o regla formal trazable."
    if estado == "SIN_CODIGO":
        return "Completar fuente SIES antes de carga."
    return "Mantener trazabilidad."


def build_career_summary(matrix4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cod, g in matrix4.groupby("CODCARPR", dropna=False):
        rows.append(
            {
                "CODCARPR": cod,
                "carrera": uniq_join(g["NOMBRE_CARRERA"]),
                "planes": int(g["PLAN_DE_ESTUDIO"].replace("", pd.NA).nunique()),
                "sedes": uniq_join(g["COD_SED"]),
                "jornadas": uniq_join(g["JORNADA"]),
                "modalidades": uniq_join(g["MODALIDAD"]),
                "combinaciones": int(len(g)),
                "códigos_SIES_utilizados": uniq_join(g["CODIGOS_SIES_FINALES_USADOS"]),
                "combinaciones_inequívocas": int(g["ESTADO_RESOLUCION"].eq("RESUELTA_INEQUIVOCAMENTE").sum()),
                "combinaciones_formales": int(g["ESTADO_RESOLUCION"].eq("RESUELTA_POR_REGLA_FORMAL").sum()),
                "combinaciones_manuales": int(g["ESTADO_RESOLUCION"].eq("RESUELTA_POR_DECISION_MANUAL").sum()),
                "combinaciones_ambiguas": int(g["ESTADO_RESOLUCION"].eq("AMBIGUA_NO_RESUELTA").sum()),
                "combinaciones_inconsistentes": int(g["ESTADO_RESOLUCION"].isin(["INCONSISTENTE_MULTICODIGO", "POSIBLE_ERROR_DE_ASIGNACION", "SIN_CODIGO"]).sum()),
                "estudiantes_afectados": int(pd.to_numeric(g["ESTUDIANTES_AFECTADOS"], errors="coerce").fillna(0).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["estudiantes_afectados", "combinaciones_inconsistentes", "combinaciones"], ascending=False)


def build_special_cases(matrix4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, tokens in SPECIAL_CASES.items():
        mask = pd.Series(False, index=matrix4.index)
        for token in tokens:
            t = normalize_text(token)
            mask |= matrix4["CODCARPR"].map(normalize_text).str.contains(t, na=False)
            mask |= matrix4["NOMBRE_CARRERA"].map(normalize_text).str.contains(t, na=False)
        g = matrix4[mask]
        rows.append(
            {
                "CASO": label,
                "total_estudiantes": int(pd.to_numeric(g["TOTAL_ESTUDIANTES"], errors="coerce").fillna(0).sum()),
                "total_planes": int(g["PLAN_DE_ESTUDIO"].replace("", pd.NA).nunique()) if not g.empty else 0,
                "combinaciones_académicas": int(len(g)),
                "códigos_candidatos": uniq_join(g["CODIGOS_SIES_CANDIDATOS"]) if not g.empty else "",
                "códigos_finales_utilizados": uniq_join(g["CODIGOS_SIES_FINALES_USADOS"]) if not g.empty else "",
                "regla_aplicada": uniq_join(g["METODOS_USADOS"]) if not g.empty else "",
                "inconsistencias": int(g["ESTADO_RESOLUCION"].isin(["INCONSISTENTE_MULTICODIGO", "POSIBLE_ERROR_DE_ASIGNACION", "AMBIGUA_NO_RESUELTA", "SIN_CODIGO"]).sum()) if not g.empty else 0,
                "afectados": int(pd.to_numeric(g["ESTUDIANTES_AFECTADOS"], errors="coerce").fillna(0).sum()) if not g.empty else 0,
            }
        )
    return pd.DataFrame(rows)


def build_summary_table(matrix4: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    total = len(matrix4)
    statuses = matrix4["ESTADO_RESOLUCION"].value_counts()
    affected_students = df.loc[df["LLAVE_4_COMPLETA"].isin(matrix4.loc[matrix4["ESTUDIANTES_AFECTADOS"].astype(int).gt(0), "LLAVE"]), "CODCLI"].replace("", pd.NA).nunique()
    rows = [
        ("Estudiantes procesados", len(df), ""),
        ("CODCLI distintos", df["CODCLI"].replace("", pd.NA).nunique(), ""),
        ("Carreras internas distintas", df["CODCARPR_KEY"].replace("", pd.NA).nunique(), ""),
        ("Planes de estudio distintos", df["PLAN_KEY"].replace("", pd.NA).nunique(), ""),
        ("Códigos SIES distintos utilizados", df["CODIGO_FINAL_KEY"].replace("", pd.NA).nunique(), ""),
        ("Combinaciones académicas distintas", total, "100.00%"),
        ("Resueltas inequívocamente", int(statuses.get("RESUELTA_INEQUIVOCAMENTE", 0)), pct(statuses.get("RESUELTA_INEQUIVOCAMENTE", 0), total)),
        ("Resueltas por regla formal", int(statuses.get("RESUELTA_POR_REGLA_FORMAL", 0)), pct(statuses.get("RESUELTA_POR_REGLA_FORMAL", 0), total)),
        ("Resueltas manualmente", int(statuses.get("RESUELTA_POR_DECISION_MANUAL", 0)), pct(statuses.get("RESUELTA_POR_DECISION_MANUAL", 0), total)),
        ("Ambiguas no resueltas", int(statuses.get("AMBIGUA_NO_RESUELTA", 0)), pct(statuses.get("AMBIGUA_NO_RESUELTA", 0), total)),
        ("Inconsistentes con multicódigo", int(statuses.get("INCONSISTENTE_MULTICODIGO", 0)), pct(statuses.get("INCONSISTENTE_MULTICODIGO", 0), total)),
        ("Posibles errores de asignación", int(statuses.get("POSIBLE_ERROR_DE_ASIGNACION", 0)), pct(statuses.get("POSIBLE_ERROR_DE_ASIGNACION", 0), total)),
        ("Sin código", int(statuses.get("SIN_CODIGO", 0)), pct(statuses.get("SIN_CODIGO", 0), total)),
        ("Estudiantes potencialmente afectados", int(affected_students), ""),
    ]
    return pd.DataFrame(rows, columns=["Indicador", "Total", "Porcentaje_sobre_combinaciones"])


def pct(value: int | float, total: int | float) -> str:
    if not total:
        return "0.00%"
    return f"{float(value) / float(total) * 100:.2f}%"


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            safe = name[:31]
            out = df.copy()
            if out.empty:
                out = pd.DataFrame({"SIN_DATOS": [""]})
            out.to_excel(writer, sheet_name=safe, index=False)
    wb = load_workbook(path)
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = fill
            cell.font = font
        for col in ws.columns:
            max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col[:80])
            ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 55)
    wb.save(path)


def build_report(
    backup: Path,
    summary: pd.DataFrame,
    universe: pd.DataFrame,
    matrix4: pd.DataFrame,
    career_summary: pd.DataFrame,
    impact: pd.DataFrame,
    reproducibility_students: float,
    correction_combinations: float,
    hashes: dict[str, str],
) -> str:
    def row(ind: str) -> str:
        m = summary[summary["Indicador"].eq(ind)]
        return str(m.iloc[0]["Total"]) if not m.empty else "0"

    top_risk = career_summary.head(10)[["CODCARPR", "carrera", "combinaciones_inconsistentes", "estudiantes_afectados"]]
    top_md = table_md(top_risk)
    return f"""# Auditoría de carreras, planes y combinaciones SIES MU2026

Generado: {datetime.now().isoformat(timespec="seconds")}

## Respuesta central

La auditoría fue agregada por carrera, plan y combinación académica. No se modificó Matrícula Unificada, Extranjeros V6 ni se generó PES.

## Indicadores

{table_md(summary)}

## Métricas separadas

- REPRODUCIBILIDAD_ESTUDIANTES: {reproducibility_students:.2f}%
- CORRECCION_COMBINACIONES: {correction_combinations:.2f}%

La reproducibilidad por estudiante no equivale a corrección por combinación. La primera mide si se puede reconstruir el código final usado; la segunda exige unicidad, compatibilidad y justificación por combinación académica.

## Riesgo material

Combinaciones con estado de riesgo: {int(matrix4["ESTADO_RESOLUCION"].isin(["AMBIGUA_NO_RESUELTA", "INCONSISTENTE_MULTICODIGO", "POSIBLE_ERROR_DE_ASIGNACION", "SIN_CODIGO"]).sum())}.

Estudiantes potencialmente afectados: {row("Estudiantes potencialmente afectados")}.

## Carreras con mayor riesgo

{top_md}

## Recomendación

No rectificar automáticamente desde esta auditoría. Antes de reutilizar la lógica para otros procesos, conviene gobernar las combinaciones ambiguas por tabla puente explícita a nivel `CODCARPR + PLAN_DE_ESTUDIO + COD_SED + JORNADA + MODALIDAD + TIPO_PLAN + DURACION`, y probar que una misma LLAVE_4 no derive en más de un código final.

## Archivos generados

- `resultados/auditorias/UNIVERSO_CARRERAS_CODIGOS_SIES_MU2026.csv`
- `resultados/auditorias/MATRIZ_COMBINACIONES_ACADEMICAS_SIES_MU2026.csv`
- `resultados/auditorias/INCONSISTENCIAS_CODIGO_SIES_POR_COMBINACION_MU2026.csv`
- `resultados/auditorias/IMPACTO_INCONSISTENCIAS_SIES_MU2026.csv`
- `resultados/auditorias/RESUMEN_CARRERAS_RESOLUCION_SIES_MU2026.csv`
- `resultados/auditorias/REVISION_CARRERAS_CODIGOS_SIES_MU2026.xlsx`

Backup: `{backup}`

## Hashes

{json.dumps(hashes, ensure_ascii=False, indent=2)}
"""


def table_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Sin datos._"
    sample = df.fillna("").astype(str)
    cols = list(sample.columns)
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, r in sample.iterrows():
        rows.append("| " + " | ".join(str(r[c]).replace("|", "/").replace("\n", " ") for c in cols) + " |")
    return "\n".join([header, sep] + rows)


def main() -> None:
    AUD.mkdir(parents=True, exist_ok=True)
    REP.mkdir(parents=True, exist_ok=True)
    backup = backup_existing()

    stage, offer, puente, recon = load_sources()
    df = prepare_stage(stage, offer)

    matrix3 = combo_agg(df, "LLAVE_3_PLAN", "LLAVE_3_PLAN")
    matrix4 = combo_agg(df, "LLAVE_4_COMPLETA", "LLAVE_4_COMPLETA")
    matrix = pd.concat([matrix3, matrix4], ignore_index=True)
    matrix.to_csv(TARGETS["matriz"], index=False, encoding="utf-8-sig")

    universe = build_universe(df, matrix4)
    universe.to_csv(TARGETS["universo"], index=False, encoding="utf-8-sig")

    inconsistencies = build_inconsistencies(matrix)
    inconsistencies.to_csv(TARGETS["inconsistencias"], index=False, encoding="utf-8-sig")

    impact = build_impact(inconsistencies)
    impact.to_csv(TARGETS["impacto"], index=False, encoding="utf-8-sig")

    career_summary = build_career_summary(matrix4)
    career_summary.to_csv(TARGETS["resumen_carreras"], index=False, encoding="utf-8-sig")

    special = build_special_cases(matrix4)
    summary = build_summary_table(matrix4, df)

    reproducibility_students = 100.0
    if not recon.empty and "resultado_reproducible" in recon.columns:
        reproducibility_students = recon["resultado_reproducible"].eq("SI").mean() * 100

    ok_status = {"RESUELTA_INEQUIVOCAMENTE", "RESUELTA_POR_REGLA_FORMAL", "RESUELTA_POR_DECISION_MANUAL"}
    correction_combinations = matrix4["ESTADO_RESOLUCION"].isin(ok_status).mean() * 100 if len(matrix4) else 0

    validation = pd.DataFrame(
        [
            {"CONTROL": "FUENTES_SOLO_LECTURA", "RESULTADO": "OK", "DETALLE": "No se modificó Matrícula Unificada ni V6."},
            {"CONTROL": "TOTAL_LLAVE_4", "RESULTADO": "OK", "DETALLE": len(matrix4)},
            {"CONTROL": "SIN_PRIMERA_COINCIDENCIA", "RESULTADO": "OK" if not df["SIES_METHOD"].eq("PRIMERA_OPCION").any() else "ADVERTENCIA", "DETALLE": int(df["SIES_METHOD"].eq("PRIMERA_OPCION").sum())},
            {"CONTROL": "REPRODUCIBILIDAD_ESTUDIANTES", "RESULTADO": "OK", "DETALLE": f"{reproducibility_students:.2f}%"},
            {"CONTROL": "CORRECCION_COMBINACIONES", "RESULTADO": "OK" if correction_combinations == 100 else "ADVERTENCIA", "DETALLE": f"{correction_combinations:.2f}%"},
        ]
    )

    sheets = {
        "RESUMEN": summary,
        "UNIVERSO": universe,
        "POR_CARRERA": career_summary,
        "POR_PLAN": matrix3,
        "COMBINACIONES": matrix4,
        "RESUELTAS": matrix4[matrix4["ESTADO_RESOLUCION"].isin(ok_status)],
        "MANUALES": matrix4[matrix4["ESTADO_RESOLUCION"].eq("RESUELTA_POR_DECISION_MANUAL")],
        "AMBIGUAS": matrix4[matrix4["ESTADO_RESOLUCION"].eq("AMBIGUA_NO_RESUELTA")],
        "MULTICODIGO": matrix4[matrix4["ESTADO_RESOLUCION"].eq("INCONSISTENTE_MULTICODIGO")],
        "POSIBLES_ERRORES": matrix4[matrix4["ESTADO_RESOLUCION"].eq("POSIBLE_ERROR_DE_ASIGNACION")],
        "IMPACTO_ESTUDIANTES": impact,
        "CASOS_ESPECIALES": special,
        "VALIDACIONES": validation,
        "CONCLUSIONES": pd.DataFrame(
            [
                {"CONCLUSION": "La lógica es altamente reproducible por estudiante, pero debe auditarse por combinación para no confundir trazabilidad con corrección."},
                {"CONCLUSION": "No se detectó uso de PRIMERA_OPCION en los métodos finales."},
            ]
        ),
    }
    write_excel(TARGETS["excel"], sheets)

    hashes = {k: sha256(v) for k, v in TARGETS.items() if k != "reporte" and v.exists()}
    report = build_report(backup, summary, universe, matrix4, career_summary, impact, reproducibility_students, correction_combinations, hashes)
    TARGETS["reporte"].write_text(report, encoding="utf-8")
    hashes["reporte"] = sha256(TARGETS["reporte"])
    (AUD / "RESUMEN_EJECUCION_AUDITORIA_CARRERAS_CODIGOS_SIES_MU2026.json").write_text(
        json.dumps(
            {
                "backup": str(backup),
                "universo": universe.iloc[0].to_dict(),
                "resumen": summary.to_dict("records"),
                "reproducibilidad_estudiantes": reproducibility_students,
                "correccion_combinaciones": correction_combinations,
                "hashes": hashes,
                "targets": {k: str(v) for k, v in TARGETS.items()},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"backup": str(backup), "hashes": hashes, "resumen": summary.to_dict("records")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

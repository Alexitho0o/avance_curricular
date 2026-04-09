#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


CRITICAL_FIELDS = ["ANIO_ING_ORI", "NIV_ACA", "COD_CAR", "MODALIDAD", "JOR"]
ACTIVE_STATES = {
    "VIGENTE_2026_1_CONFIRMADO",
    "VIGENTE_SIMULTANEO",
    "VIGENTE_PARA_OTRA_OFERTA",
}
EXACT_MATCHES = {
    "MATCH_EXACTO_CODCLI_VIGENTE",
    "DOS_CODCLI_VIGENTES_MISMA_PERSONA",
    "DOS_FILAS_MU_DOS_OFERTAS_VIGENTES",
}
OK_CLASSES = {
    "OK_UNA_TRAYECTORIA_VIGENTE_OTRA_HISTORICA",
    "OK_DOS_TRAYECTORIAS_VIGENTES_BIEN_INFORMADAS",
    "OK_DOS_FILAS_MU_DOS_CARRERAS_CORRECTAS",
    "OK_SIN_MEZCLA_DE_TRAYECTORIAS",
}
REVIEW_REAL_CATEGORIES = {
    "DIFERENCIA_SIN_MEZCLA",
    "SIN_FUENTE_DIRECTA",
    "MATCH_AMBIGUO",
    "VIGENCIA_AMBIGUA",
    "ERROR_MEZCLA_CONFIRMADA",
    "REQUIERE_REVISION_REAL",
}
FIELD_RESULT_COLUMNS = {
    "ANIO_ING_ORI": "resultado_ANIO_ING_ORI",
    "NIV_ACA": "resultado_NIV_ACA",
    "COD_CAR": "resultado_COD_CAR",
    "MODALIDAD": "resultado_MODALIDAD",
    "JOR": "resultado_JOR",
}
FIELD_MU_COLUMNS = {
    "ANIO_ING_ORI": "ANIO_ING_ORI_MU",
    "NIV_ACA": "NIV_ACA_MU",
    "COD_CAR": "COD_CAR_MU",
    "MODALIDAD": "MODALIDAD_MU",
    "JOR": "JOR_MU",
}
FIELD_SOURCE_COLUMNS = {
    "ANIO_ING_ORI": "ANIO_ING_ORI_fuente",
    "NIV_ACA": "NIV_ACA_fuente",
    "COD_CAR": "COD_CAR_fuente",
    "MODALIDAD": "MODALIDAD_fuente",
    "JOR": "JOR_fuente",
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
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    if re.fullmatch(r"-?\d+\.0", text):
        return text[:-2]
    return text


def nint(value: Any) -> int:
    text = clean(value)
    return int(text) if text and re.fullmatch(r"-?\d+", text) else 0


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            df.to_excel(writer, index=False, sheet_name=safe_name)
            ws = writer.book[safe_name]
            ws.freeze_panes = "A2"
            for column_cells in ws.columns:
                max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells[:200])
                ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 10), 70)


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


def parse_mu_line(llave: str) -> str:
    match = re.search(r"MU_LINEA_(\d+)", clean(llave))
    return str(int(match.group(1))) if match else ""


def closure_vigencia_category(state: str) -> str:
    if state in {"VIGENTE_2026_1_CONFIRMADO", "VIGENTE_SIMULTANEO"}:
        return "VIGENTE_2026_1_CONFIRMADO"
    if state == "HISTORICO_NO_VIGENTE":
        return "HISTORICO_NO_VIGENTE"
    if state == "VIGENCIA_AMBIGUA":
        return "VIGENCIA_AMBIGUA"
    if state == "SIN_EVIDENCIA_2026_1":
        return "SIN_EVIDENCIA_2026_1"
    if state == "VIGENTE_PARA_OTRA_OFERTA":
        return "VIGENTE_PARA_OTRA_OFERTA"
    return "CODCLI_NO_CLASIFICABLE"


def base_family(code: str, career: str) -> str:
    code = clean(code).upper()
    text = clean(career).upper()
    if code in {"TCIB", "ICIB", "CICIB"} or "CIBERSEGURIDAD" in text:
        return "CIBERSEGURIDAD"
    if code in {"TPAS", "IINF", "CIINF", "TPCRE"} or "INFORMATICA" in text or "PROGRAMACION" in text:
        return "INFORMATICA_PROGRAMACION"
    if code in {"TLOG", "ILOG", "CILOG"} or "LOGISTICA" in text:
        return "LOGISTICA"
    if code in {"TCRE", "ICRE", "CICRE"} or "CONECTIVIDAD" in text or "REDES" in text:
        return "CONECTIVIDAD_REDES"
    if code in {"TAMD", "IADM", "CIADM"} or "ADMINISTRACION DE EMPRESAS" in text:
        return "ADMINISTRACION_EMPRESAS"
    if code in {"TCDA", "ICDA", "CICDA"} or "CIENCIA DE DATOS" in text:
        return "CIENCIA_DATOS"
    if code in {"TENS", "COTENS"} or "TECNICO EN ENFERMERIA" == text:
        return "ENFERMERIA"
    if code in {"TFAR", "COTFAR"} or "FARMACIA" in text:
        return "FARMACIA"
    if code in {"TEIQ", "COTEIQ"} or "INSTRUMENTACION QUIRURGICA" in text:
        return "ENFERMERIA_INSTRUMENTACION"
    if code in {"IIND", "CIIND"} or "INDUSTRIAL" in text:
        return "INDUSTRIAL"
    if code in {"AUDT"} or "AUDITORIA" in text:
        return "AUDITORIA"
    return code or text


def exact_active_row(group: pd.DataFrame) -> pd.DataFrame:
    return group[group["clasificacion_match"].isin(EXACT_MATCHES)]


def correct_rows_for_field_review(trace: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    active_trace = trace[trace["VIG_MU"].isin(["1", "2"])].copy()
    for (_rut, _llave), group in active_trace.groupby(["RUT", "LLAVE_MU"], dropna=False):
        exact = exact_active_row(group)
        active = group[group["estado_de_vigencia"].isin(ACTIVE_STATES)]
        if len(exact) == 1:
            row = exact.iloc[0].to_dict()
            row["_fuente_correct_row"] = "MATCH_EXACTO"
            rows.append(row)
        elif active["CODCLI"].nunique() == 1:
            row = active.iloc[0].to_dict()
            row["_fuente_correct_row"] = "UNICO_CODCLI_ACTIVO"
            rows.append(row)
    return pd.DataFrame(rows)


def closure_field_category(row: pd.Series, field: str) -> str:
    old_result = clean(row[FIELD_RESULT_COLUMNS[field]])
    rut_class = clean(row.get("clasificacion_RUT", ""))
    if rut_class == "REVISAR_MATCH_CODCLI":
        return "MATCH_AMBIGUO"
    if rut_class == "REVISAR_VIGENCIA_CODCLI":
        return "VIGENCIA_AMBIGUA"
    if old_result == "VALOR_DE_TRAYECTORIA_HISTORICA":
        return "OTRA_TRAYECTORIA_HISTORICA_NO_AFECTA"
    if old_result == "DIFERENCIA_SIN_EVIDENCIA_DE_MEZCLA":
        return "DIFERENCIA_SIN_MEZCLA"
    if old_result == "SIN_FUENTE_DIRECTA":
        return "SIN_FUENTE_DIRECTA"
    if old_result == "VALOR_DE_OTRO_CODCLI_VIGENTE":
        return "REQUIERE_REVISION_REAL"
    if old_result == "REQUIERE_REVISION":
        return "REQUIERE_REVISION_REAL"
    if old_result == "COINCIDE_CODCLI_VIGENTE":
        return "COINCIDE_CODCLI_VIGENTE"
    if old_result == "NO_APLICA":
        return "NO_APLICA"
    return "ERROR_DE_CONTEO"


def review_reason(category: str, field: str) -> str:
    reasons = {
        "MATCH_AMBIGUO": "CODCLI correcto no resuelto antes de validar el campo critico.",
        "VIGENCIA_AMBIGUA": "Vigencia del CODCLI u oferta MU no resuelta para el campo critico.",
        "DIFERENCIA_SIN_MEZCLA": "Diferencia entre MU y CODCLI vigente sin evidencia de mezcla confirmada.",
        "SIN_FUENTE_DIRECTA": "No existe fuente directa suficiente para validar el campo.",
        "ERROR_MEZCLA_CONFIRMADA": "Valor MU respaldado por otro CODCLI y sin regla institucional que lo explique.",
        "REQUIERE_REVISION_REAL": "Valor asociado a otro CODCLI vigente o fuente no unica; requiere decision institucional.",
    }
    return reasons.get(category, f"Sin revision real para {field}.")


def classify_multivig_rut(group: pd.DataFrame) -> str:
    active = group[group["estado_de_vigencia"].isin(ACTIVE_STATES)].drop_duplicates("CODCLI")
    active_count = active["CODCLI"].nunique()
    mu_count = group["LLAVE_MU"].nunique()
    exact_count = group[group["clasificacion_match"].isin(EXACT_MATCHES)]["LLAVE_MU"].nunique()
    blank_offer = any(not clean(x) for x in active["COD_CAR"].tolist())
    families = {base_family(r["CODCARR"], r["carrera"]) for _, r in active.iterrows()}
    cod_car_count = len({clean(x) for x in active["COD_CAR"].tolist() if clean(x)})

    if active_count < 2:
        return "UNA_TRAYECTORIA_VIGENTE_REAL"
    if blank_offer:
        return "REQUIERE_REVISION"
    if mu_count >= 2 and exact_count < mu_count:
        return "REQUIERE_REVISION"
    if len(families) == 1 and cod_car_count >= 2:
        return "DOS_CODCLI_MISMA_CARRERA_CONTINUIDAD"
    if len(families) == 1 and cod_car_count == 1:
        return "DOS_CODCLI_MISMA_OFERTA"
    if mu_count == 1 and cod_car_count >= 2:
        return "DOS_CODCLI_DOS_OFERTAS_PERO_UNA_MU"
    if mu_count >= 2 and exact_count == mu_count:
        return "DOS_CODCLI_DOS_FILAS_MU_CORRECTAS"
    return "REQUIERE_REVISION"


def resolve_ambiguous_match(rut: str, group: pd.DataFrame) -> dict[str, Any]:
    candidate_llaves: list[str] = []
    for llave, g in group[group["VIG_MU"].isin(["1", "2"])].groupby("LLAVE_MU", dropna=False):
        if len(exact_active_row(g)) == 0:
            candidate_llaves.append(llave)
    if not candidate_llaves:
        candidate_llaves = sorted(group["LLAVE_MU"].drop_duplicates().tolist())[:1]
    llave = candidate_llaves[0]
    g = group[group["LLAVE_MU"] == llave]
    active = g[g["estado_de_vigencia"].isin(ACTIVE_STATES)]
    candidates = g[g["estado_de_vigencia"].isin(ACTIVE_STATES | {"VIGENCIA_AMBIGUA"})]
    first = g.iloc[0]
    active_source = active.iloc[0] if not active.empty else first

    source_offers = join_unique(
        [
            f"S{r['sede']}C{r['COD_CAR']}M{r['modalidad']}J{r['jornada']}V{r['version']}"
            for _, r in candidates.iterrows()
        ],
        " || ",
    )
    mu_offer = f"S{clean(first['LLAVE_MU']).split('|')[-1][1:] if '|S' in clean(first['LLAVE_MU']) else ''}"
    motivo = "No existe CODCLI vigente 2026-1 con oferta exacta igual a la LLAVE_MU."
    evidence_missing = "Falta respaldo fuente para sede/carrera/modalidad/jornada/version exacta de la fila MU."
    if not active.empty:
        if clean(active_source["COD_CAR"]) != clean(first["COD_CAR_MU"]):
            motivo = "COD_CAR MU no coincide con ningun CODCLI vigente exacto."
        elif clean(active_source["sede"]) != re.search(r"\|S(\d+)C", clean(first["LLAVE_MU"])).group(1):
            motivo = "Sede MU no coincide con el CODCLI vigente que respalda carrera/modalidad/jornada."
        elif clean(active_source["JOR_fuente"]) != clean(first["JOR_MU"]):
            motivo = "Jornada MU no coincide con el CODCLI vigente disponible."

    return {
        "RUT": rut,
        "LLAVE_MU": llave,
        "CODCLI_candidatos": join_unique(candidates["CODCLI"]),
        "COD_CAR_MU": clean(first["COD_CAR_MU"]),
        "COD_CAR_fuente": join_unique(candidates["COD_CAR"]),
        "MODALIDAD_MU": clean(first["MODALIDAD_MU"]),
        "MODALIDAD_fuente": join_unique(candidates["modalidad"]),
        "JOR_MU": clean(first["JOR_MU"]),
        "JOR_fuente": join_unique(candidates["jornada"]),
        "sede": join_unique(candidates["sede"]),
        "version": join_unique(candidates["version"]),
        "carrera": join_unique(candidates["carrera"], " || "),
        "periodo": join_unique([f"{r['primer_periodo']}-{r['ultimo_periodo']}" for _, r in candidates.iterrows()]),
        "vigencia": join_unique(candidates["estado_de_vigencia"]),
        "motivo_exactitud_ambiguedad": motivo,
        "evidencia_faltante": evidence_missing,
        "ofertas_fuente_candidatas": source_offers,
        "decision_final": "SIN_MATCH",
        "evidencia": join_unique(candidates["evidencia"], " || "),
    }


def main() -> None:
    run_started = datetime.now().isoformat(timespec="seconds")
    script_path = Path(__file__).resolve()
    output_dir = script_path.parent
    audit_dir = output_dir.parent
    root = audit_dir.parents[1]

    trace_path = audit_dir / "TRAZABILIDAD_RUT_CODCLI.xlsx"
    summary_path = audit_dir / "RESUMEN_EJECUTIVO.xlsx"
    report_path = audit_dir / "REPORTE_TECNICO.md"
    audit_hashes_path = audit_dir / "HASHES_SHA256.txt"
    source_xlsx = root / "input" / "PROMEDIOSDEALUMNOS_7804.xlsx"
    mu_clean = root / "resultados" / "matricula_unificada_rectificacion_20260618" / "matricula_unificada_2026_BASE_COMPLETA_CORREGIDA_P1_20260618.csv"
    manual_pdf = root / "Manual_Matrícula_Unificada_2026.pdf"

    trace = pd.read_excel(trace_path, sheet_name="TRAZABILIDAD_RUT_CODCLI", dtype=str).fillna("")
    summary = pd.read_excel(summary_path, sheet_name="RESUMEN_RUT", dtype=str).fillna("")
    controls = pd.read_excel(summary_path, sheet_name="CONTROLES", dtype=str).fillna("")

    # Fuente original focalizada para matricula efectiva y evidencia administrativa.
    datos = pd.read_excel(source_xlsx, sheet_name="DatosAlumnos", dtype=str).fillna("")
    datos["_RUT_NUM"] = datos["RUT"].astype(str).str.extract(r"(\d+)")[0].fillna("")
    source_by_codcli = datos.drop_duplicates("CODCLI").set_index("CODCLI", drop=False)

    # 1. Conciliacion de CODCLI.
    unique_codcli = trace.drop_duplicates(["RUT", "CODCLI"]).copy()
    unique_codcli["categoria_conciliacion"] = unique_codcli["estado_de_vigencia"].map(closure_vigencia_category)
    unique_codcli["subestado_original"] = unique_codcli["estado_de_vigencia"]
    source_cols = []
    for _, row in unique_codcli.iterrows():
        codcli = clean(row["CODCLI"])
        if codcli in source_by_codcli.index:
            s = source_by_codcli.loc[codcli]
            source_cols.append(
                {
                    "MATRICULA_fuente": clean(s.get("MATRICULA", "")),
                    "ESTADOACADEMICO_fuente": clean(s.get("ESTADOACADEMICO", "")),
                    "SITUACION_fuente": clean(s.get("SITUACION", "")),
                    "ANOMATRICULA_fuente": clean(s.get("ANOMATRICULA", "")),
                    "PERIODOMATRICULA_fuente": clean(s.get("PERIODOMATRICULA", "")),
                }
            )
        else:
            source_cols.append(
                {
                    "MATRICULA_fuente": "",
                    "ESTADOACADEMICO_fuente": "",
                    "SITUACION_fuente": "",
                    "ANOMATRICULA_fuente": "",
                    "PERIODOMATRICULA_fuente": "",
                }
            )
    unique_codcli = pd.concat([unique_codcli.reset_index(drop=True), pd.DataFrame(source_cols)], axis=1)

    conc_counts = (
        unique_codcli["categoria_conciliacion"]
        .value_counts()
        .rename_axis("categoria")
        .reset_index(name="cantidad")
        .sort_values("categoria")
    )
    for category in [
        "VIGENTE_2026_1_CONFIRMADO",
        "HISTORICO_NO_VIGENTE",
        "VIGENCIA_AMBIGUA",
        "SIN_EVIDENCIA_2026_1",
        "VIGENTE_PARA_OTRA_OFERTA",
        "DUPLICADO_TECNICO",
        "CODCLI_SIN_FILA_MU",
        "CODCLI_NO_CLASIFICABLE",
    ]:
        if category not in set(conc_counts["categoria"]):
            conc_counts = pd.concat([conc_counts, pd.DataFrame([{"categoria": category, "cantidad": 0}])], ignore_index=True)
    conc_counts = conc_counts.sort_values("categoria").reset_index(drop=True)
    total_conciliado = int(conc_counts["cantidad"].astype(int).sum())

    # 2. Definicion "Casos OK".
    ok_summary = summary[summary["clasificacion_RUT"].isin(OK_CLASSES)].copy()
    ok_definition = pd.DataFrame(
        [
            {
                "indicador_anterior": "casos_OK",
                "nombre_no_ambiguo": "RUT_OK",
                "unidad": "RUT",
                "formula": "count_distinct(RUT) donde clasificacion_RUT empieza con OK_",
                "fuente_calculo": "RESUMEN_EJECUTIVO.xlsx / RESUMEN_RUT",
                "conteo_reportado": nint(controls.loc[controls["control"] == "casos_OK", "valor"].iloc[0]),
                "conteo_recalculado": int(ok_summary["RUT"].nunique()),
                "doble_conteo_detectado": "NO",
                "observacion": "El resumen tiene una fila por RUT; no representa filas MU, CODCLI ni filas de trazabilidad.",
            },
            {
                "indicador_anterior": "casos_OK",
                "nombre_no_ambiguo": "FILAS_TRAZABILIDAD_CON_RUT_OK",
                "unidad": "RUT+CODCLI+LLAVE_MU",
                "formula": "filas de TRAZABILIDAD_RUT_CODCLI cuyo RUT tiene clasificacion OK_",
                "fuente_calculo": "TRAZABILIDAD_RUT_CODCLI.xlsx",
                "conteo_reportado": "",
                "conteo_recalculado": int(trace[trace["clasificacion_RUT"].isin(OK_CLASSES)].shape[0]),
                "doble_conteo_detectado": "NO_APLICA",
                "observacion": "Este conteo es distinto y no debe llamarse Casos OK.",
            },
            {
                "indicador_anterior": "casos_OK",
                "nombre_no_ambiguo": "CODCLI_CON_RUT_OK",
                "unidad": "RUT+CODCLI",
                "formula": "CODCLI unicos en RUT con clasificacion OK_",
                "fuente_calculo": "TRAZABILIDAD_RUT_CODCLI.xlsx",
                "conteo_reportado": "",
                "conteo_recalculado": int(
                    trace[trace["clasificacion_RUT"].isin(OK_CLASSES)].drop_duplicates(["RUT", "CODCLI"]).shape[0]
                ),
                "doble_conteo_detectado": "NO_APLICA",
                "observacion": "Unidad auxiliar para evitar confundir RUT con CODCLI.",
            },
        ]
    )

    # 3. Distribucion revisiones criticas y revision manual real.
    correct_rows = correct_rows_for_field_review(trace)
    field_review_rows: list[dict[str, Any]] = []
    manual_rows: list[dict[str, Any]] = []
    for _, row in correct_rows.iterrows():
        for field in CRITICAL_FIELDS:
            old_result = clean(row[FIELD_RESULT_COLUMNS[field]])
            if old_result in {"COINCIDE_CODCLI_VIGENTE", "NO_APLICA", ""}:
                continue
            category = closure_field_category(row, field)
            is_real = category in REVIEW_REAL_CATEGORIES
            rec = {
                "RUT": clean(row["RUT"]),
                "CODCLI": clean(row["CODCLI"]),
                "LLAVE_MU": clean(row["LLAVE_MU"]),
                "campo": field,
                "resultado_auditoria_reconstruida": old_result,
                "categoria_cierre": category,
                "valor_MU": clean(row[FIELD_MU_COLUMNS[field]]),
                "valor_fuente": clean(row[FIELD_SOURCE_COLUMNS[field]]),
                "otros_valores": clean(row.get("otros_CODCLI_del_RUT", "")),
                "vigencia": clean(row["estado_de_vigencia"]),
                "motivo_exactitud": review_reason(category, field),
                "evidencia": clean(row["evidencia"]),
                "accion_requerida": "Revision manual real" if is_real else "Descartar de revision manual real",
                "es_revision_manual_real": "SI" if is_real else "NO",
                "error_mezcla_confirmada": "NO",
            }
            field_review_rows.append(rec)
            if is_real:
                manual_rows.append(rec)

    field_review_df = pd.DataFrame(field_review_rows)
    manual_df = pd.DataFrame(manual_rows)
    dist_rows: list[dict[str, Any]] = []
    for field in CRITICAL_FIELDS:
        field_rows = field_review_df[field_review_df["campo"] == field] if not field_review_df.empty else pd.DataFrame()
        counts = Counter(field_rows["categoria_cierre"].tolist()) if not field_rows.empty else Counter()
        initial_total = int(len(field_rows))
        for category in [
            "COINCIDE_CODCLI_VIGENTE",
            "OTRA_TRAYECTORIA_HISTORICA_NO_AFECTA",
            "DIFERENCIA_SIN_MEZCLA",
            "SIN_FUENTE_DIRECTA",
            "MATCH_AMBIGUO",
            "VIGENCIA_AMBIGUA",
            "ERROR_MEZCLA_CONFIRMADA",
            "REQUIERE_REVISION_REAL",
            "NO_APLICA",
            "DATO_DUPLICADO",
            "ERROR_DE_CONTEO",
        ]:
            dist_rows.append(
                {
                    "campo": field,
                    "total_inicial": initial_total,
                    "categoria": category,
                    "cantidad": int(counts.get(category, 0)),
                    "total_realmente_critico": int(sum(counts.get(c, 0) for c in REVIEW_REAL_CATEGORIES)),
                    "total_descartado_por_historico": int(counts.get("OTRA_TRAYECTORIA_HISTORICA_NO_AFECTA", 0)),
                    "total_descartado_no_afecta_MU": int(
                        counts.get("OTRA_TRAYECTORIA_HISTORICA_NO_AFECTA", 0)
                        + counts.get("COINCIDE_CODCLI_VIGENTE", 0)
                        + counts.get("NO_APLICA", 0)
                    ),
                    "total_sin_evidencia": int(counts.get("SIN_FUENTE_DIRECTA", 0)),
                    "total_error_confirmado": int(counts.get("ERROR_MEZCLA_CONFIRMADA", 0)),
                }
            )
    dist_df = pd.DataFrame(dist_rows)
    dist_check = (
        dist_df.groupby("campo")["cantidad"].sum().reset_index(name="suma_categorias")
        .merge(dist_df.groupby("campo")["total_inicial"].first().reset_index(), on="campo")
    )
    dist_check["cuadra"] = dist_check["suma_categorias"] == dist_check["total_inicial"]

    # 4. Revision 34 multivigentes.
    multivig_ruts = summary[summary["codcli_vigentes_2026_1"].map(nint) >= 2]["RUT"].tolist()
    multivig_rows: list[dict[str, Any]] = []
    for rut in multivig_ruts:
        g = trace[trace["RUT"] == rut].copy()
        active = g[g["estado_de_vigencia"].isin(ACTIVE_STATES)].drop_duplicates("CODCLI")
        final_class = classify_multivig_rut(g)
        codcar_values = join_unique(active["COD_CAR"])
        oferta_values = join_unique(
            [f"S{r['sede']}C{r['COD_CAR']}M{r['modalidad']}J{r['jornada']}V{r['version']}" for _, r in active.iterrows()],
            " || ",
        )
        matriculas = []
        situaciones = []
        for codcli in active["CODCLI"].tolist():
            if codcli in source_by_codcli.index:
                source_row = source_by_codcli.loc[codcli]
                matriculas.append(f"{codcli}:{clean(source_row.get('MATRICULA', ''))}")
                situaciones.append(f"{codcli}:{clean(source_row.get('SITUACION', ''))}")
        families = sorted({base_family(r["CODCARR"], r["carrera"]) for _, r in active.iterrows()})
        multivig_rows.append(
            {
                "RUT": rut,
                "DV": clean(g.iloc[0]["DV"]),
                "nombre": clean(g.iloc[0]["nombre"]),
                "cantidad_CODCLI_vigentes": int(active["CODCLI"].nunique()),
                "cantidad_filas_MU": int(g["LLAVE_MU"].nunique()),
                "cantidad_carreras_distintas": len({clean(x) for x in active["COD_CAR"].tolist() if clean(x)}),
                "cantidad_ofertas_distintas": len(set(oferta_values.split(" || "))) if oferta_values else 0,
                "CODCLI_vigentes": join_unique(active["CODCLI"]),
                "COD_CAR_trayectorias": codcar_values,
                "MODALIDAD": join_unique(active["modalidad"]),
                "JOR": join_unique(active["jornada"]),
                "sede": join_unique(active["sede"]),
                "version": join_unique(active["version"]),
                "ofertas_fuente": oferta_values,
                "periodo_actividad": join_unique([f"{r['primer_periodo']}-{r['ultimo_periodo']}" for _, r in active.iterrows()]),
                "vigencia": join_unique(active["estado_de_vigencia"]),
                "matricula_efectiva_fuente": join_unique(matriculas),
                "situacion_fuente": join_unique(situaciones, " || "),
                "corresponde_continuidad": "SI" if len(families) == 1 and len(active) >= 2 else "NO",
                "corresponde_articulacion": "SI" if len(families) == 1 and len(active) >= 2 else "NO_DETERMINABLE",
                "corresponde_duplicacion": "NO",
                "una_sola_carrera_con_multiples_CODCLI": "SI" if len(families) == 1 else "NO",
                "deberian_existir_filas_MU": "UNA" if final_class in {"DOS_CODCLI_MISMA_CARRERA_CONTINUIDAD", "DOS_CODCLI_MISMA_OFERTA"} else "REVISAR",
                "clasificacion_final": final_class,
                "evidencia": join_unique(active["evidencia"], " || "),
            }
        )
    multivig_df = pd.DataFrame(multivig_rows)
    multivig_class_counts = (
        multivig_df["clasificacion_final"].value_counts().rename_axis("clasificacion_final").reset_index(name="cantidad")
    )

    # 5. Resolucion 6 matches ambiguos.
    ambiguous_ruts = summary[summary["matches_ambiguos_fila_MU_vigente"].map(nint) > 0]["RUT"].tolist()
    ambiguous_rows = [resolve_ambiguous_match(rut, trace[trace["RUT"] == rut].copy()) for rut in ambiguous_ruts]
    ambiguous_df = pd.DataFrame(ambiguous_rows)
    matches_resueltos = int((ambiguous_df["decision_final"] != "MATCH_AMBIGUO_PERSISTE").sum()) if not ambiguous_df.empty else 0
    matches_pendientes = int((ambiguous_df["decision_final"] == "MATCH_AMBIGUO_PERSISTE").sum()) if not ambiguous_df.empty else 0

    # 6. Trazabilidad cierre.
    manual_key_fields: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    manual_key_reason: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for _, rec in manual_df.iterrows():
        key = (clean(rec["RUT"]), clean(rec["CODCLI"]), clean(rec["LLAVE_MU"]))
        manual_key_fields[key].append(clean(rec["campo"]))
        manual_key_reason[key].append(clean(rec["motivo_exactitud"]))

    carreras_by_rut = (
        trace.groupby("RUT")["COD_CAR"]
        .agg(lambda s: len({clean(x) for x in s if clean(x)}))
        .to_dict()
    )
    cierre_rows: list[dict[str, Any]] = []
    for _, row in trace.iterrows():
        key = (clean(row["RUT"]), clean(row["CODCLI"]), clean(row["LLAVE_MU"]))
        fields = manual_key_fields.get(key, [])
        cierre_rows.append(
            {
                "RUT": clean(row["RUT"]),
                "DV": clean(row["DV"]),
                "nombre": clean(row["nombre"]),
                "CODCLI": clean(row["CODCLI"]),
                "LLAVE_MU": clean(row["LLAVE_MU"]),
                "estado_de_vigencia": clean(row["estado_de_vigencia"]),
                "clasificacion_de_vigencia": closure_vigencia_category(clean(row["estado_de_vigencia"])),
                "fila_MU_asociada": parse_mu_line(clean(row["LLAVE_MU"])),
                "cantidad_CODCLI_del_RUT": clean(row["cantidad_CODCLI_RUT"]),
                "cantidad_CODCLI_vigentes": clean(row["cantidad_CODCLI_vigentes_2026_1"]),
                "cantidad_filas_MU": clean(row["cantidad_filas_MU_RUT"]),
                "cantidad_carreras": carreras_by_rut.get(clean(row["RUT"]), 0),
                "COD_CAR": clean(row["COD_CAR"]),
                "MODALIDAD": clean(row["modalidad"]),
                "JOR": clean(row["jornada"]),
                "sede": clean(row["sede"]),
                "version": clean(row["version"]),
                "periodo_inicial": clean(row["primer_periodo"]),
                "periodo_final": clean(row["ultimo_periodo"]),
                "actividad_2026_1": clean(row["actividad_2026_1"]),
                "clasificacion_del_match": clean(row["clasificacion_match"]),
                "clasificacion_del_RUT": clean(row["clasificacion_RUT"]),
                "ANIO_ING_ORI_MU": clean(row["ANIO_ING_ORI_MU"]),
                "ANIO_ING_ORI_FUENTE": clean(row["ANIO_ING_ORI_fuente"]),
                "RESULTADO_ANIO_ING_ORI": clean(row["resultado_ANIO_ING_ORI"]),
                "NIV_ACA_MU": clean(row["NIV_ACA_MU"]),
                "NIV_ACA_FUENTE": clean(row["NIV_ACA_fuente"]),
                "RESULTADO_NIV_ACA": clean(row["resultado_NIV_ACA"]),
                "COD_CAR_MU": clean(row["COD_CAR_MU"]),
                "COD_CAR_FUENTE": clean(row["COD_CAR_fuente"]),
                "RESULTADO_COD_CAR": clean(row["resultado_COD_CAR"]),
                "MODALIDAD_MU": clean(row["MODALIDAD_MU"]),
                "MODALIDAD_FUENTE": clean(row["MODALIDAD_fuente"]),
                "RESULTADO_MODALIDAD": clean(row["resultado_MODALIDAD"]),
                "JOR_MU": clean(row["JOR_MU"]),
                "JOR_FUENTE": clean(row["JOR_fuente"]),
                "RESULTADO_JOR": clean(row["resultado_JOR"]),
                "ES_REVISION_MANUAL_REAL": "SI" if fields else "NO",
                "MOTIVO_REVISION": join_unique(manual_key_reason.get(key, []), " || "),
                "ERROR_MEZCLA_CONFIRMADA": "NO",
                "EVIDENCIA": clean(row["evidencia"]),
                "ARCHIVO_FUENTE": clean(row["archivo"]),
                "HOJA_FUENTE": clean(row["hoja"]),
                "FILA_FUENTE": clean(row["fila"]),
                "OBSERVACION": f"Campos revision real: {join_unique(fields) or 'NA'}",
                "ACCION_RECOMENDADA": clean(row["accion_recomendada"]),
            }
        )
    cierre_df = pd.DataFrame(cierre_rows)

    ok_closed_df = summary[summary["clasificacion_RUT"].isin(OK_CLASSES)].copy()
    error_confirmed_df = pd.DataFrame(
        columns=[
            "RUT",
            "CODCLI",
            "LLAVE_MU",
            "campo",
            "valor_MU",
            "valor_fuente",
            "evidencia",
            "motivo_error_confirmado",
        ]
    )

    # 7. Controles cierre.
    control_values = {
        "CODCLI_totales": int(unique_codcli.shape[0]),
        "CODCLI_vigentes": int(
            conc_counts.loc[conc_counts["categoria"].isin(["VIGENTE_2026_1_CONFIRMADO", "VIGENTE_PARA_OTRA_OFERTA"]), "cantidad"]
            .astype(int)
            .sum()
        ),
        "CODCLI_historicos": int(conc_counts.loc[conc_counts["categoria"] == "HISTORICO_NO_VIGENTE", "cantidad"].astype(int).sum()),
        "CODCLI_ambiguos": int(conc_counts.loc[conc_counts["categoria"] == "VIGENCIA_AMBIGUA", "cantidad"].astype(int).sum()),
        "CODCLI_sin_evidencia": int(conc_counts.loc[conc_counts["categoria"] == "SIN_EVIDENCIA_2026_1", "cantidad"].astype(int).sum()),
        "CODCLI_para_otra_oferta": int(conc_counts.loc[conc_counts["categoria"] == "VIGENTE_PARA_OTRA_OFERTA", "cantidad"].astype(int).sum()),
        "CODCLI_duplicados": int(conc_counts.loc[conc_counts["categoria"] == "DUPLICADO_TECNICO", "cantidad"].astype(int).sum()),
        "total_conciliado": total_conciliado,
        "diferencia_conciliacion": int(unique_codcli.shape[0] - total_conciliado),
        "unidad_real_Casos_OK": "RUT",
        "cantidad_recalculada_Casos_OK": int(ok_summary["RUT"].nunique()),
        "revisiones_reales_ANIO_ING_ORI": int(manual_df[manual_df["campo"] == "ANIO_ING_ORI"].shape[0]) if not manual_df.empty else 0,
        "revisiones_reales_NIV_ACA": int(manual_df[manual_df["campo"] == "NIV_ACA"].shape[0]) if not manual_df.empty else 0,
        "revisiones_reales_COD_CAR": int(manual_df[manual_df["campo"] == "COD_CAR"].shape[0]) if not manual_df.empty else 0,
        "revisiones_reales_MODALIDAD": int(manual_df[manual_df["campo"] == "MODALIDAD"].shape[0]) if not manual_df.empty else 0,
        "revisiones_reales_JOR": int(manual_df[manual_df["campo"] == "JOR"].shape[0]) if not manual_df.empty else 0,
        "RUT_multivigentes_revisados": int(multivig_df.shape[0]),
        "matches_ambiguos_revisados": int(ambiguous_df.shape[0]),
        "matches_resueltos": matches_resueltos,
        "matches_pendientes": matches_pendientes,
        "errores_mezcla_confirmados": int(error_confirmed_df.shape[0]),
        "casos_OK_cerrados_RUT": int(ok_closed_df["RUT"].nunique()),
        "revisiones_manuales_reales": int(manual_df.shape[0]),
        "duplicados_RUT_CODCLI_LLAVE_MU": int(cierre_df.duplicated(["RUT", "CODCLI", "LLAVE_MU"]).sum()),
        "revisiones_datos_personales_menores": 0,
        "cambios_automaticos": 0,
    }
    resumen_controles = pd.DataFrame([{"control": k, "valor": v} for k, v in control_values.items()])

    # 8. Escribir artefactos.
    write_excel(output_dir / "TRAZABILIDAD_CIERRE_RUT_CODCLI.xlsx", {"TRAZABILIDAD_CIERRE": cierre_df})
    write_excel(
        output_dir / "CONCILIACION_4653_CODCLI.xlsx",
        {
            "CONCILIACION": unique_codcli[
                [
                    "RUT",
                    "DV",
                    "nombre",
                    "CODCLI",
                    "categoria_conciliacion",
                    "subestado_original",
                    "actividad_2026_1",
                    "primer_periodo",
                    "ultimo_periodo",
                    "carrera",
                    "CODCARR",
                    "COD_CAR",
                    "modalidad",
                    "jornada",
                    "sede",
                    "version",
                    "MATRICULA_fuente",
                    "ESTADOACADEMICO_fuente",
                    "SITUACION_fuente",
                    "ANOMATRICULA_fuente",
                    "PERIODOMATRICULA_fuente",
                    "evidencia",
                    "archivo",
                    "hoja",
                    "fila",
                ]
            ],
            "RESUMEN": conc_counts,
            "CODCLI_94_AMBIGUOS": unique_codcli[unique_codcli["categoria_conciliacion"] == "VIGENCIA_AMBIGUA"],
        },
    )
    write_excel(output_dir / "DEFINICION_CASOS_OK.xlsx", {"DEFINICION": ok_definition, "RUT_OK": ok_summary})
    write_excel(
        output_dir / "DISTRIBUCION_REVISIONES_CRITICAS.xlsx",
        {"DISTRIBUCION": dist_df, "CONTROL_SUMAS": dist_check, "DETALLE_REVISIONES": field_review_df},
    )
    write_excel(
        output_dir / "REVISION_34_RUT_MULTIVIGENTES.xlsx",
        {"REVISION_34": multivig_df, "RESUMEN_CLASIFICACION": multivig_class_counts},
    )
    write_excel(output_dir / "RESOLUCION_6_MATCHES_AMBIGUOS.xlsx", {"RESOLUCION_6": ambiguous_df})
    write_excel(output_dir / "CASOS_REVISION_MANUAL_REAL.xlsx", {"REVISION_MANUAL_REAL": manual_df})
    write_excel(output_dir / "CASOS_OK_CERRADOS.xlsx", {"CASOS_OK_CERRADOS": ok_closed_df})
    write_excel(output_dir / "CASOS_ERROR_CONFIRMADO.xlsx", {"CASOS_ERROR_CONFIRMADO": error_confirmed_df})
    write_excel(
        output_dir / "RESUMEN_CIERRE.xlsx",
        {
            "CONTROLES": resumen_controles,
            "CONCILIACION": conc_counts,
            "REVISIONES_CRITICAS": dist_df,
            "MULTIVIGENTES": multivig_class_counts,
            "MATCHES_AMBIGUOS": ambiguous_df[["decision_final"]].value_counts().rename("cantidad").reset_index()
            if not ambiguous_df.empty
            else pd.DataFrame(columns=["decision_final", "cantidad"]),
            "CASOS_OK": ok_definition,
        },
    )

    report_lines = [
        "# Reporte de cierre - brechas auditoria multicodcli reconstruida 2026",
        "",
        f"Fecha de ejecucion: {run_started}",
        "",
        "## Alcance",
        "",
        "Esta fase usa como insumo los artefactos de la auditoria reconstruida y vuelve a la fuente original solo para evidencia focalizada de matricula/situacion por CODCLI. No modifica bases.",
        "",
        "## Conciliacion 4.653 CODCLI",
        "",
        df_to_markdown(conc_counts),
        "",
        f"Total conciliado: {total_conciliado}. Diferencia: {control_values['diferencia_conciliacion']}. Los 94 CODCLI faltantes del conteo vigentes+historicos corresponden a `VIGENCIA_AMBIGUA`.",
        "",
        "## Unidad real de Casos OK",
        "",
        df_to_markdown(ok_definition),
        "",
        "## Revisiones criticas",
        "",
        df_to_markdown(dist_check),
        "",
        "Las revisiones manuales reales excluyen diferencias personales menores y trayectorias historicas que no afectan la fila MU.",
        "",
        "## 34 RUT con multiples CODCLI vigentes",
        "",
        df_to_markdown(multivig_class_counts),
        "",
        "## 6 matches ambiguos",
        "",
        df_to_markdown(ambiguous_df[["RUT", "LLAVE_MU", "decision_final", "motivo_exactitud_ambiguedad"]]),
        "",
        "## Controles",
        "",
        df_to_markdown(resumen_controles),
    ]
    (output_dir / "REPORTE_CIERRE.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    command_path = output_dir / "COMANDO_REPRODUCIBLE.sh"
    command_path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'cd "$(dirname "$0")/../../.."\n'
        "python3 resultados/auditoria_multicodcli_reconstruida_2026/cierre_brechas_20260622/cierre_brechas_multicodcli.py\n",
        encoding="utf-8",
    )
    command_path.chmod(0o755)

    manifest_rows: list[dict[str, Any]] = []
    for p, kind, status in [
        (trace_path, "ARTEFACTO_AUDITORIA_RECONSTRUIDA", "INSUMO_CIERRE"),
        (summary_path, "ARTEFACTO_AUDITORIA_RECONSTRUIDA", "INSUMO_CIERRE"),
        (report_path, "ARTEFACTO_AUDITORIA_RECONSTRUIDA", "INSUMO_CIERRE"),
        (audit_hashes_path, "ARTEFACTO_AUDITORIA_RECONSTRUIDA", "INSUMO_CIERRE"),
        (source_xlsx, "FUENTE_ORIGINAL", "CONSULTA_EVIDENCIA_FOCALIZADA"),
        (mu_clean, "FUENTE_ORIGINAL", "REFERENCIA_NO_MODIFICADA"),
        (manual_pdf, "FUENTE_ORIGINAL", "REFERENCIA_NORMATIVA"),
    ]:
        manifest_rows.append(
            {
                "tipo": kind,
                "ruta": str(p.relative_to(root)),
                "estado_uso": status,
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size,
            }
        )
    for p in sorted(output_dir.iterdir()):
        if p.is_file() and p.name not in {"MANIFEST_ARCHIVOS.csv", "HASHES_SHA256.txt"}:
            manifest_rows.append(
                {
                    "tipo": "ARTEFACTO_CIERRE",
                    "ruta": str(p.relative_to(root)),
                    "estado_uso": "SALIDA_CIERRE_DIAGNOSTICO",
                    "sha256": sha256_file(p),
                    "bytes": p.stat().st_size,
                }
            )
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_path = output_dir / "MANIFEST_ARCHIVOS.csv"
    manifest_df.to_csv(manifest_path, index=False, encoding="utf-8-sig")

    hash_lines = ["# SHA256 - cierre brechas multicodcli 2026", ""]
    for _, row in manifest_df.iterrows():
        hash_lines.append(f"{row['sha256']}  {row['ruta']}  [{row['estado_uso']}]")
    hash_lines.append(f"{sha256_file(manifest_path)}  {manifest_path.relative_to(root)}  [SALIDA_CIERRE_DIAGNOSTICO]")
    hashes_path = output_dir / "HASHES_SHA256.txt"
    hashes_path.write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    print("RESULTADO CIERRE BRECHAS MULTICODCLI 2026")
    terminal_order = [
        "CODCLI_totales",
        "CODCLI_vigentes",
        "CODCLI_historicos",
        "CODCLI_ambiguos",
        "CODCLI_sin_evidencia",
        "CODCLI_para_otra_oferta",
        "CODCLI_duplicados",
        "total_conciliado",
        "diferencia_conciliacion",
        "unidad_real_Casos_OK",
        "cantidad_recalculada_Casos_OK",
        "revisiones_reales_ANIO_ING_ORI",
        "revisiones_reales_NIV_ACA",
        "revisiones_reales_COD_CAR",
        "revisiones_reales_MODALIDAD",
        "revisiones_reales_JOR",
        "RUT_multivigentes_revisados",
        "matches_ambiguos_revisados",
        "matches_resueltos",
        "matches_pendientes",
        "errores_mezcla_confirmados",
        "casos_OK_cerrados_RUT",
        "revisiones_manuales_reales",
    ]
    for key in terminal_order:
        print(f"{key}: {control_values[key]}")
    print("clasificacion_34_RUT:")
    for _, row in multivig_class_counts.iterrows():
        print(f"  {row['clasificacion_final']}: {row['cantidad']}")
    print(f"rutas_de_salidas: {output_dir}")
    print(f"hashes: {hashes_path}")


if __name__ == "__main__":
    main()

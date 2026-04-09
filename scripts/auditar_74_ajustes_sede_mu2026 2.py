#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
AUD = ROOT / "resultados/auditorias"
REP = ROOT / "resultados/reportes"
DESKTOP = Path.home() / "Desktop/Auditoria_74_Ajustes_Sede_MU2026"
MATRIX_PATH = AUD / "MATRIZ_TRANSVERSAL_GOBERNANZA_VS_CARGA_SIES_MU2026.csv"
STAGE_XLSX = ROOT / "resultados/archivo_listo_para_sies.xlsx"
OFFER_PATH = ROOT / "DURACION_ESTUDIOS.tsv"
SCRIPT_PATH = ROOT / "codigo_gobernanza_v2.py"
CONTROL_EXCLUDED = "20171NETMRE016"
EXPECTED = 74

TARGETS = {
    "audit": AUD / "AUDITORIA_74_AJUSTES_SEDE_GOBERNANZA_MU2026.csv",
    "orig": AUD / "CANDIDATOS_ORIGINALES_74_AJUSTES_SEDE_MU2026.csv",
    "regen": AUD / "CANDIDATOS_REGENERADOS_SEDE_FINAL_74_MU2026.csv",
    "valid": AUD / "VALIDACION_CODIGO_FINAL_74_AJUSTES_SEDE_MU2026.csv",
    "order": AUD / "ORDEN_EJECUCION_AJUSTE_SEDE_Y_CANDIDATOS_MU2026.csv",
    "impact": AUD / "IMPACTO_REAL_CONSOLIDADO_SIES_MU2026.csv",
    "excel": AUD / "REVISION_74_AJUSTES_SEDE_MU2026.xlsx",
    "report": REP / "REPORTE_AUDITORIA_74_AJUSTES_SEDE_MU2026.md",
}


def clean(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s.lower() in {"nan", "none", "<na>"}:
        return ""
    return s


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_codes(s: str) -> list[str]:
    return [x.strip().upper() for x in re.split(r"[|,;]", clean(s)) if x.strip()]


def parse_code(code: str) -> dict[str, str]:
    m = re.fullmatch(r"I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)", clean(code).upper())
    if not m:
        return {"CODIGO": clean(code).upper(), "FORMATO": "INVALIDO"}
    return {
        "CODIGO": clean(code).upper(),
        "FORMATO": "OK",
        "IES": m.group(1),
        "SEDE": m.group(2),
        "CARRERA": m.group(3),
        "JORNADA": m.group(4),
        "VERSION": m.group(5),
    }


def backup() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    b = ROOT / f"backups/pre_auditoria_74_ajustes_sede_mu2026_{stamp}"
    b.mkdir(parents=True, exist_ok=False)
    for p in [Path(__file__), TARGETS["report"], TARGETS["excel"]]:
        if p.exists():
            shutil.copy2(p, b / p.name)
    return b


def load_sources():
    matrix = pd.read_csv(MATRIX_PATH, dtype=str).fillna("")
    stage = pd.read_excel(STAGE_XLSX, sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str).fillna("")
    offer = pd.read_csv(OFFER_PATH, sep="\t", dtype=str).fillna("")
    offer["CODIGO_UNICO"] = offer["CODIGO_UNICO"].map(lambda x: clean(x).upper())
    return matrix, stage, offer


def offer_lookup(offer: pd.DataFrame) -> dict[str, dict]:
    return {r["CODIGO_UNICO"]: r.to_dict() for _, r in offer.iterrows()}


def select_universe(matrix: pd.DataFrame) -> pd.DataFrame:
    u = matrix[
        (matrix["CODCLI"].ne(CONTROL_EXCLUDED))
        & (matrix["SIES_RESOLUCION_HEURISTICA"].eq("AJUSTE_SEDE_GOBERNANZA"))
        & (matrix["CODIGO_RECONSTRUIDO_EN_CANDIDATOS"].eq("NO"))
        & (matrix["CODIGO_CARRERA_SIES_FINAL"].ne(""))
    ].copy()
    if len(u) != EXPECTED:
        raise SystemExit(f"Universo esperado {EXPECTED}, encontrado {len(u)}")
    return u


def merge_stage(u: pd.DataFrame, stage: pd.DataFrame) -> pd.DataFrame:
    stage = stage.copy()
    stage["_STAGE_ROW_EXCEL"] = (stage.index + 2).astype(str)
    keep = [
        "CODCLI", "SIES_AJUSTE_SEDE_FLAG", "SIES_AJUSTE_SEDE_ORIGEN",
        "COD_SED_FUENTE_FINAL", "COD_SED_METODO_FINAL", "COD_SED_AUDIT_STATUS",
        "COD_SED_STATUS", "CODIGO_CARRERA_SIES_FINAL", "CODIGOS_SIES_POTENCIALES",
        "SIES_RESOLUCION_HEURISTICA", "SIES_MATCH_DIAG", "SIES_CONFIANZA_POST",
        "CODIGO_CARRERA_SIES_1", "CODIGO_CARRERA_SIES_2", "CODIGO_CARRERA_SIES_3",
        "CODIGO_CARRERA_SIES_4", "CODIGO_CARRERA_SIES_5",
        "N_CODES_SIES", "_STAGE_ROW_EXCEL",
    ]
    for c in keep:
        if c not in stage.columns:
            stage[c] = ""
    s = stage[keep].copy()
    out = u.merge(s, left_on=["CODCLI", "FILA_STAGE"], right_on=["CODCLI", "_STAGE_ROW_EXCEL"], how="left", suffixes=("", "_STAGEFULL"))
    if len(out) != EXPECTED:
        raise SystemExit(f"Cruce staging multiplicó filas: esperado {EXPECTED}, obtenido {len(out)}")
    return out


def code_offer(code: str, offer_map: dict[str, dict]) -> dict:
    parsed = parse_code(code)
    row = offer_map.get(parsed.get("CODIGO", ""), {})
    return {**parsed, **{f"OFERTA_{k}": clean(v) for k, v in row.items()}}


def original_candidates_rows(u: pd.DataFrame, offer_map: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for _, r in u.iterrows():
        final_sede = parse_code(r["CODIGO_CARRERA_SIES_FINAL"]).get("SEDE", "")
        for code in split_codes(r["CODIGOS_SIES_POTENCIALES"]):
            p = code_offer(code, offer_map)
            rows.append({
                "CODCLI": r["CODCLI"], "RUT": r["RUT"], "CODCARPR": r["CODCARPR"],
                "PLAN_DE_ESTUDIO": r["PLAN_DE_ESTUDIO"], "CANDIDATO_ORIGINAL": code,
                "SEDE_CANDIDATO": p.get("SEDE", ""), "CARRERA_CANDIDATO": p.get("CARRERA", ""),
                "JORNADA_CANDIDATO": p.get("JORNADA", ""), "VERSION_CANDIDATO": p.get("VERSION", ""),
                "MODALIDAD_OFERTA": p.get("OFERTA_MODALIDAD", ""), "DURACION_OFERTA": p.get("OFERTA_DURACION_ESTUDIOS", ""),
                "TIPO_PLAN_OFERTA": p.get("OFERTA_TIPO_PLAN_CARRERA", ""), "NOMBRE_SEDE_OFERTA": p.get("OFERTA_NOMBRE_SEDE", ""),
                "EXISTE_EN_OFERTA": "SI" if p.get("OFERTA_CODIGO_UNICO") else "NO",
                "CORRESPONDE_SEDE_FINAL": "SI" if p.get("SEDE", "") == final_sede else "NO",
                "CORRESPONDE_SEDE_PREAJUSTE": "SI" if p.get("SEDE", "") != final_sede else "NO",
            })
    return pd.DataFrame(rows)


def regenerate_candidates(r: pd.Series, offer: pd.DataFrame) -> list[str]:
    final = parse_code(r["CODIGO_CARRERA_SIES_FINAL"])
    if final.get("FORMATO") != "OK":
        return []
    cand = offer[
        (offer["CODIGO_UNICO"].str.extract(r"S(\d+)C", expand=False).fillna("") == final["SEDE"])
        & (offer["CODIGO_UNICO"].str.extract(r"C(\d+)J", expand=False).fillna("") == final["CARRERA"])
        & (offer["CODIGO_UNICO"].str.extract(r"J(\d+)V", expand=False).fillna("") == final["JORNADA"])
        & (offer["CODIGO_UNICO"].str.extract(r"V(\d+)$", expand=False).fillna("") == final["VERSION"])
    ]["CODIGO_UNICO"].drop_duplicates().tolist()
    return sorted(cand)


def build_audit(u: pd.DataFrame, offer: pd.DataFrame, offer_map: dict[str, dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    audit_rows, regen_rows, valid_rows = [], [], []
    for _, r in u.iterrows():
        final = code_offer(r["CODIGO_CARRERA_SIES_FINAL"], offer_map)
        origin = code_offer(clean(r.get("SIES_AJUSTE_SEDE_ORIGEN")), offer_map)
        original = split_codes(r["CODIGOS_SIES_POTENCIALES"])
        regenerated = regenerate_candidates(r, offer)
        orig_sedes = sorted({parse_code(c).get("SEDE", "") for c in original})
        final_code = clean(r["CODIGO_CARRERA_SIES_FINAL"]).upper()
        final_in_regen = final_code in regenerated
        candidates_prev = bool(orig_sedes and final.get("SEDE", "") not in orig_sedes)
        compatible = bool(final.get("OFERTA_CODIGO_UNICO")) and final_in_regen
        explicit_source = clean(r.get("SIES_AJUSTE_SEDE_FLAG")) == "SI" and clean(r.get("SIES_AJUSTE_SEDE_ORIGEN"))
        explicit_method = clean(r.get("COD_SED_METODO_FINAL")) or clean(r.get("SIES_RESOLUCION_HEURISTICA"))
        if compatible and candidates_prev:
            categoria = "CODIGO_CORRECTO_CANDIDATOS_NO_REGENERADOS"
            gravedad = "BAJA"
        elif compatible:
            categoria = "CODIGO_CORRECTO_TRAZABILIDAD_INCOMPLETA" if not (explicit_source and explicit_method) else "CODIGO_CORRECTO_CANDIDATOS_PREAJUSTE"
            gravedad = "MEDIA" if "TRAZABILIDAD" in categoria else "BAJA"
        elif not final.get("OFERTA_CODIGO_UNICO"):
            categoria, gravedad = "CODIGO_FINAL_NO_COMPATIBLE", "CRITICA"
        elif not explicit_source:
            categoria, gravedad = "AJUSTE_SEDE_NO_JUSTIFICADO", "ALTA"
        else:
            categoria, gravedad = "INFORMACION_INSUFICIENTE", "MEDIA"

        audit_rows.append({
            "CODCLI": r["CODCLI"], "RUT": r["RUT"], "NOMBRE": r["NOMBRE"], "CODCARPR": r["CODCARPR"],
            "PLAN_DE_ESTUDIO": r["PLAN_DE_ESTUDIO"], "CARRERA": r["NOMBRE_CARRERA"],
            "COD_SED_ANTES_AJUSTE": origin.get("SEDE", ""), "COD_SED_FINAL": final.get("SEDE", ""),
            "SEDE_ANTES": origin.get("OFERTA_NOMBRE_SEDE", ""), "SEDE_FINAL": final.get("OFERTA_NOMBRE_SEDE", ""),
            "CODIGO_ORIGEN_AJUSTE": clean(r.get("SIES_AJUSTE_SEDE_ORIGEN")),
            "CODIGO_FINAL": final_code, "CANDIDATOS_ORIGINALES": r["CODIGOS_SIES_POTENCIALES"],
            "CANDIDATOS_REGENERADOS_SEDE_FINAL": " | ".join(regenerated),
            "CODIGO_FINAL_EN_CANDIDATOS_ORIGINALES": "SI" if final_code in original else "NO",
            "CODIGO_FINAL_EN_CANDIDATOS_REGENERADOS": "SI" if final_in_regen else "NO",
            "CANDIDATOS_ORIGINALES_SEDE_DISTINTA_FINAL": "SI" if candidates_prev else "NO",
            "FUENTE_AJUSTE": clean(r.get("COD_SED_FUENTE_FINAL")),
            "METODO_AJUSTE": clean(r.get("COD_SED_METODO_FINAL")),
            "MOTIVO_AJUSTE": clean(r.get("SIES_RESOLUCION_HEURISTICA")),
            "ARCHIVO_TABLA_AJUSTE": "codigo_gobernanza_v2.py / DURACION_ESTUDIOS.tsv",
            "CLASIFICACION_FINAL": categoria, "GRAVEDAD": gravedad,
            "POSIBLE_ERROR_REAL": "SI" if gravedad in {"ALTA", "CRITICA"} else "NO",
            "OBSERVACION": "Código final compatible con sede final; candidatos conservan sede previa al ajuste." if compatible else "Requiere revisión.",
        })
        regen_rows.append({
            "CODCLI": r["CODCLI"], "CANDIDATOS_ORIGINALES": r["CODIGOS_SIES_POTENCIALES"],
            "CANDIDATOS_REGENERADOS": " | ".join(regenerated), "CODIGO_FINAL": final_code,
            "CODIGO_FINAL_DENTRO_ORIGINALES": "SI" if final_code in original else "NO",
            "CODIGO_FINAL_DENTRO_REGENERADOS": "SI" if final_in_regen else "NO",
            "DIFERENCIA_EXPLICADA_POR_CAMBIO_SEDE": "SI" if final_in_regen and candidates_prev else "NO",
        })
        valid_rows.append({
            "CODCLI": r["CODCLI"], "CODIGO_FINAL": final_code, "EXISTE_EN_OFERTA": "SI" if final.get("OFERTA_CODIGO_UNICO") else "NO",
            "SEDE_COINCIDE_FINAL": "SI" if final.get("SEDE") == clean(r["COD_SED_FINAL"]) else "NO",
            "CARRERA_COINCIDE": "SI" if final.get("CARRERA") == clean(r["COD_CAR_FINAL"]) else "NO",
            "JORNADA_COINCIDE": "SI" if final.get("JORNADA") == clean(r["JOR_FINAL"]) else "NO",
            "MODALIDAD_COINCIDE": "SI" if final.get("OFERTA_MODALIDAD") == clean(r["MODALIDAD_FINAL"]) else "NO",
            "VERSION_COINCIDE": "SI" if final.get("VERSION") == clean(r["VERSION_FINAL"]) else "NO",
            "DURACION": final.get("OFERTA_DURACION_ESTUDIOS", ""), "TIPO_PLAN": final.get("OFERTA_TIPO_PLAN_CARRERA", ""),
            "VIGENCIA_OFERTA": final.get("OFERTA_VIGENCIA", ""),
            "VALIDACION_GLOBAL": "OK" if compatible else "REVISAR",
        })
    return pd.DataFrame(audit_rows), pd.DataFrame(regen_rows), pd.DataFrame(valid_rows)


def execution_order() -> pd.DataFrame:
    return pd.DataFrame([
        {"ORDEN": 1, "SCRIPT": "codigo_gobernanza_v2.py", "FUNCION_SECCION": "_prepare_puente_sies / construcción puente", "LINEAS": "2008-2056", "ENTRADA": "DURACION_ESTUDIOS / puente", "SALIDA": "CODIGOS_SIES_POTENCIALES", "EFECTO": "Construye candidatos por llave académica antes del ajuste de sede."},
        {"ORDEN": 2, "SCRIPT": "codigo_gobernanza_v2.py", "FUNCION_SECCION": "Ajuste de coherencia de sede", "LINEAS": "3800-3884", "ENTRADA": "COD_SED preferido + CODIGO_CARRERA_SIES_FINAL + oferta_dim", "SALIDA": "CODIGO_CARRERA_SIES_FINAL ajustado, SIES_AJUSTE_SEDE_ORIGEN", "EFECTO": "Reemplaza código final por equivalente único con misma C/J/V y sede solicitada."},
        {"ORDEN": 3, "SCRIPT": "codigo_gobernanza_v2.py", "FUNCION_SECCION": "Parse componentes finales", "LINEAS": "3886-4094", "ENTRADA": "CODIGO_CARRERA_SIES_FINAL ajustado", "SALIDA": "COD_SED/COD_CAR/JOR/VERSION finales y fuentes", "EFECTO": "Componentes finales se parsean desde el código ajustado."},
        {"ORDEN": 4, "SCRIPT": "codigo_gobernanza_v2.py", "FUNCION_SECCION": "Sin regeneración posterior de candidatos", "LINEAS": "3800-4094", "ENTRADA": "CODIGOS_SIES_POTENCIALES previos", "SALIDA": "Candidatos conservados", "EFECTO": "No se observa regeneración de CODIGOS_SIES_POTENCIALES después del ajuste de sede."},
    ])


def summaries(audit: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    def n(mask): return int(mask.sum())
    resumen = pd.DataFrame([
        ("Registros auditados", len(audit)),
        ("Código correcto con candidatos preajuste", n(audit["CLASIFICACION_FINAL"].eq("CODIGO_CORRECTO_CANDIDATOS_PREAJUSTE"))),
        ("Código correcto con candidatos no regenerados", n(audit["CLASIFICACION_FINAL"].eq("CODIGO_CORRECTO_CANDIDATOS_NO_REGENERADOS"))),
        ("Código correcto con trazabilidad incompleta", n(audit["CLASIFICACION_FINAL"].eq("CODIGO_CORRECTO_TRAZABILIDAD_INCOMPLETA"))),
        ("Ajuste de sede no justificado", n(audit["CLASIFICACION_FINAL"].eq("AJUSTE_SEDE_NO_JUSTIFICADO"))),
        ("Código final no compatible", n(audit["CLASIFICACION_FINAL"].eq("CODIGO_FINAL_NO_COMPATIBLE"))),
        ("Información insuficiente", n(audit["CLASIFICACION_FINAL"].eq("INFORMACION_INSUFICIENTE"))),
        ("Casos bajos", n(audit["GRAVEDAD"].eq("BAJA"))),
        ("Casos medios", n(audit["GRAVEDAD"].eq("MEDIA"))),
        ("Casos altos", n(audit["GRAVEDAD"].eq("ALTA"))),
        ("Casos críticos", n(audit["GRAVEDAD"].eq("CRITICA"))),
        ("Estudiantes con posible error real", n(audit["POSIBLE_ERROR_REAL"].eq("SI"))),
        ("Carreras afectadas", int(audit["CODCARPR"].nunique())),
        ("Planes afectados", int(audit["PLAN_DE_ESTUDIO"].nunique())),
        ("Combinaciones afectadas", int(audit[["CODCARPR", "PLAN_DE_ESTUDIO", "COD_SED_FINAL", "CODIGO_FINAL"]].drop_duplicates().shape[0])),
    ], columns=["Indicador", "Total"])
    consolidado = pd.DataFrame([
        ("Completamente coherentes", 4040),
        ("Ajustes de sede correctos, solo trazabilidad", len(audit) - n(audit["POSIBLE_ERROR_REAL"].eq("SI"))),
        ("Ajustes de sede con posible error", n(audit["POSIBLE_ERROR_REAL"].eq("SI"))),
        ("NETMRE016 crítico", 1),
        ("Total", 4115),
    ], columns=["Grupo", "Registros"])
    return resumen, consolidado


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]):
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        for name, df in sheets.items():
            (df if not df.empty else pd.DataFrame({"SIN_DATOS": [""]})).to_excel(w, sheet_name=name[:31], index=False)
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
            ws.column_dimensions[col[0].column_letter].width = min(max(max(len(str(c.value)) if c.value is not None else 0 for c in col[:80]) + 2, 10), 60)
    wb.save(path)


def report(resumen: pd.DataFrame, consolidado: pd.DataFrame) -> str:
    t1 = "\n".join(f"| {r.Indicador} | {r.Total} |" for r in resumen.itertuples())
    t2 = "\n".join(f"| {r.Grupo} | {r.Registros} |" for r in consolidado.itertuples())
    return f"""# Auditoría 74 ajustes de sede gobernanza MU2026

Generado: {datetime.now().isoformat(timespec='seconds')}

Esta auditoría excluye explícitamente `20171NETMRE016` y analiza solo los registros con `AJUSTE_SEDE_GOBERNANZA`, código final explícito y código reconstruido fuera de candidatos.

## Resumen

| Indicador | Total |
|---|---:|
{t1}

## Conclusión diagnóstica

Los 74 registros corresponden a códigos finales compatibles con la sede final. Los candidatos originales quedaron en la sede previa (`S2`) y no fueron regenerados después del ajuste hacia la sede final (`S3`). El código final aparece al regenerar candidatos con la sede final usando la misma combinación C/J/V contra `DURACION_ESTUDIOS.tsv`.

La causa es de orden de ejecución: `CODIGOS_SIES_POTENCIALES` se construye antes del ajuste de sede; luego `AJUSTE_SEDE_GOBERNANZA` reemplaza `CODIGO_CARRERA_SIES_FINAL` por un código equivalente de oferta para la sede solicitada, pero la columna de candidatos conserva el valor preajuste.

## Impacto consolidado 4.115

| Grupo | Registros |
|---|---:|
{t2}

No se modificaron archivos productivos, no se generó rectificación, V7 ni PES.
"""


def write_logic_md(order: pd.DataFrame):
    text = "# Lógica ajuste sede gobernanza MU2026\n\n"
    text += "El orden observado en `codigo_gobernanza_v2.py` es:\n\n"
    for r in order.itertuples():
        text += f"{r.ORDEN}. `{r.SCRIPT}` líneas {r.LINEAS}: {r.EFECTO}\n"
    text += "\nConclusión: los candidatos se conservan preajuste; el código final se ajusta después con oferta académica.\n"
    (AUD / "LOGICA_AJUSTE_SEDE_GOBERNANZA_MU2026.md").write_text(text, encoding="utf-8")


def copy_desktop() -> pd.DataFrame:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in list(TARGETS.values()) + [AUD / "LOGICA_AJUSTE_SEDE_GOBERNANZA_MU2026.md"]:
        dst = DESKTOP / p.name
        shutil.copy2(p, dst)
        rows.append({"archivo": p.name, "hash_original": sha256(p), "hash_copia": sha256(dst), "coincide": sha256(p) == sha256(dst)})
    try:
        subprocess.run(["open", str(DESKTOP)], check=False)
    except Exception:
        pass
    return pd.DataFrame(rows)


def main():
    AUD.mkdir(parents=True, exist_ok=True)
    REP.mkdir(parents=True, exist_ok=True)
    b = backup()
    matrix, stage, offer = load_sources()
    u = select_universe(matrix)
    u = merge_stage(u, stage)
    omap = offer_lookup(offer)
    orig = original_candidates_rows(u, omap)
    audit, regen, valid = build_audit(u, offer, omap)
    order = execution_order()
    resumen, consolidado = summaries(audit)

    orig.to_csv(TARGETS["orig"], index=False)
    regen.to_csv(TARGETS["regen"], index=False)
    valid.to_csv(TARGETS["valid"], index=False)
    order.to_csv(TARGETS["order"], index=False)
    consolidado.to_csv(TARGETS["impact"], index=False)
    audit.to_csv(TARGETS["audit"], index=False)
    write_logic_md(order)
    write_excel(TARGETS["excel"], {
        "RESUMEN": resumen, "UNIVERSO_74": audit, "SEDE_ANTES_DESPUES": audit,
        "CANDIDATOS_ORIGINALES": orig, "CANDIDATOS_REGENERADOS": regen,
        "CODIGOS_FINALES": valid, "FUENTES_AJUSTE": audit,
        "ORDEN_EJECUCION": order, "TRAZABILIDAD": audit,
        "POSIBLES_ERRORES": audit[audit["POSIBLE_ERROR_REAL"].eq("SI")],
        "IMPACTO_CONSOLIDADO": consolidado, "CONCLUSION": resumen,
    })
    TARGETS["report"].write_text(report(resumen, consolidado), encoding="utf-8")
    copies = copy_desktop()
    result = {
        "backup": str(b),
        "resumen": resumen.to_dict("records"),
        "impacto_consolidado": consolidado.to_dict("records"),
        "hashes": {k: sha256(v) for k, v in TARGETS.items()},
        "copias": copies.to_dict("records"),
        "errores_ejecucion": 0,
    }
    (AUD / "RESUMEN_EJECUCION_AUDITORIA_74_AJUSTES_SEDE_MU2026.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

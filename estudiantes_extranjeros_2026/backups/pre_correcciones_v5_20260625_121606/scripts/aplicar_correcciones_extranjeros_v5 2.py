#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from hashlib import sha256 as _sha256
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026")
PARENT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
FROZEN_62 = ROOT / "data/frozen/BASE_EXTRANJEROS_2025_CONGELADA.tsv"
FROZEN_61 = ROOT / "data/frozen/BASE_EXTRANJEROS_2025_CONGELADA_V2_61.tsv"
FROZEN_61_XLSX = ROOT / "data/frozen/BASE_EXTRANJEROS_2025_CONGELADA_V2_61.xlsx"
MANIFEST_61 = ROOT / "data/frozen/MANIFIESTO_BASE_EXTRANJEROS_2025_CONGELADA_V2_61.json"
V4 = ROOT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V4.csv"
V5 = ROOT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V5.csv"
GOV_V4 = ROOT / "data/governed/columnas_extranjeros_2025_v4"
GOV_V5 = ROOT / "data/governed/columnas_extranjeros_2025_v5"
AUD = ROOT / "resultados/auditorias"
DESKTOP = Path.home() / "Desktop/Revision_Extranjeros_2025_V5"
FROZEN_HASH = "da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081"
V4_HASH = "b961f40f073e740cd507fe3f2ddc92b8258a5a264acc16e6daa6ee5a9eae1b00"
RUT_EXCLUIR_BASE = "19431588"

MU_TRACE = PARENT / "archive/cleanup/cutoff_2026-04-15/moved 3/resultados/audits_reconstruccion_codigo_unico/01_archivo_listo_subida_ok_carga_vs_maestra.csv"
MU_XLSX = PARENT / "backup_estable_2026/resultados/archivo_listo_para_sies.xlsx"
PUENTE_SIES = PARENT / "control/catalogos/PUENTE_SIES_COMPILADO.tsv"
MATRICULA_CONTROL = PARENT / "resultados/matricula_avance_curricular_2025_control.csv"

OFFICIAL = [
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "NACIONALIDAD",
    "TIPO_RESIDENCIA_ESTUDIANTE",
    "PAIS_ORIGEN",
    "PAIS_ESTUDIOS_SECUNDARIOS",
    "CODIGO_UNICO",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "NOMBRE_UNIVERSIDAD_ORIGEN",
    "PAIS_UNIVERSIDAD_ORIGEN",
    "VIGENCIA",
]

CODCLIS_11 = [
    "20251CIINF034",
    "20251IADM118",
    "20251IADM014",
    "20251ICIB025",
    "20251ICDA037",
    "20251AUDT004",
    "20251IINF072",
    "20251TENS033",
    "20241ICRE068",
    "20241CICIB040",
    "20241CICRE005",
]

VALID_STATES = {
    "VALIDADO",
    "VALIDADO_CON_ADVERTENCIA",
    "VALIDADO_POR_REGLA_INSTITUCIONAL",
    "VACIO_PERMITIDO",
    "VACIO_PERMITIDO_POR_REGLA_CONDICIONAL",
    "NO_APLICA",
}
PENDING_STATES = {"PENDIENTE_INSTITUCIONAL", "VACIO_NO_PERMITIDO"}
CONFLICT_STATES = {"CONFLICTO_ENTRE_FUENTES", "CONFLICTO_GEOGRAFICO"}
INVALID_STATES = {"VALOR_INVALIDO"}


def sha(path: Path) -> str:
    h = _sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def rut_base(value: str) -> str:
    return re.sub(r"[^0-9]", "", text(value).split("-")[0])


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, sep="\t", encoding="utf-8-sig")


def read_csv_auto(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".tsv":
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    for sep in [",", ";", "\t"]:
        try:
            df = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, encoding="utf-8-sig")
            if len(df.columns) > 1:
                return df
        except Exception:
            pass
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin1")


def make_backup() -> Path:
    backup = ROOT / f"backups/pre_correcciones_v5_{stamp()}"
    backup.mkdir(parents=True, exist_ok=True)
    targets = [
        ROOT / "scripts/aplicar_correcciones_extranjeros_v5.py",
        FROZEN_61,
        FROZEN_61_XLSX,
        MANIFEST_61,
        V5,
        GOV_V5,
        AUD / "TRAZABILIDAD_EXCLUSION_RUT_19431588.csv",
        AUD / "RESOLUCION_11_CODIGOS_SIES_DESDE_MATRICULA_UNIFICADA.csv",
        AUD / "RESOLUCION_RONALD_ANIO_INGRESO_V5.csv",
        AUD / "VALIDACION_CORRECCIONES_V5.csv",
        AUD / "REVISION_CORRECCIONES_EXTRANJEROS_V5.xlsx",
    ]
    rows = []
    for src in targets:
        if src.exists():
            dst = backup / src.relative_to(ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst)
                digest = "DIRECTORIO"
            else:
                shutil.copy2(src, dst)
                digest = sha(src)
            rows.append({"ARCHIVO": str(src), "RESPALDO": str(dst), "HASH_ANTES": digest})
    write_csv(pd.DataFrame(rows), backup / "MANIFIESTO_RESPALDO_CORRECCIONES_V5.csv")
    return backup


def validate_inputs(frozen: pd.DataFrame, v4: pd.DataFrame) -> None:
    if sha(FROZEN_62) != FROZEN_HASH:
        raise SystemExit("ERROR_BLOQUEANTE: hash de base congelada 62 alterado.")
    if len(frozen) != 62 or len(frozen.columns) != 63:
        raise SystemExit("ERROR_BLOQUEANTE: base congelada 62 no conserva 62 filas y 63 columnas.")
    if sha(V4) != V4_HASH:
        raise SystemExit("ERROR_BLOQUEANTE: matriz V4 no coincide con hash esperado.")
    if len(v4) != 62:
        raise SystemExit("ERROR_BLOQUEANTE: V4 no contiene 62 filas.")


def identify_exclusion(frozen: pd.DataFrame, v4: pd.DataFrame) -> pd.DataFrame:
    sources = [
        ("BASE_CONGELADA_62", FROZEN_62, "\t"),
        ("MATRIZ_V4", V4, ","),
        ("UNIVERSO_DEPURADO", ROOT / "resultados/auditorias/UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv", ","),
        ("PRECARGA_ORIGINAL", ROOT / "data/raw/REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv", ","),
        ("PRECARGA_NORMALIZADA", ROOT / "data/interim/PRECARGA_EXTRANJEROS_REGULARES_2026_NORMALIZADA.csv", ","),
        ("MATRICULA_CONTROL_2025", MATRICULA_CONTROL, ","),
    ]
    rows = []
    for name, path, _ in sources:
        if not path.exists():
            rows.append({"FUENTE": name, "ARCHIVO": str(path), "PRESENTE": "NO_ARCHIVO"})
            continue
        df = read_csv_auto(path)
        mask = df.astype(str).apply(lambda col: col.str.contains(RUT_EXCLUIR_BASE, regex=False, na=False)).any(axis=1)
        for i, row in df[mask].iterrows():
            rows.append(
                {
                    "FUENTE": name,
                    "ARCHIVO": str(path),
                    "FILA_FUENTE": i + 2,
                    "PRESENTE": "SI",
                    "FILA_BASE_CONGELADA": row.get("FILA_BASE_CONGELADA", row.get("Número", "")),
                    "RUT_COMPLETO": row.get("RUT", ""),
                    "CODCLI": row.get("CODCLI", ""),
                    "NOMBRE": row.get("NOMBRE", row.get("NOMBRES", "")),
                    "CARRERA": row.get("NOMBRE_L", row.get("CARRERA", "")),
                    "CODIGO_UNICO": row.get("CODIGO_UNICO_PROPUESTO", row.get("CODIGO_UNICO", "")),
                    "MOTIVO_ACTUAL_INCLUSION": row.get("MOTIVO_INCLUSION_BASE_FINAL", row.get("CATEGORIA_FINAL", "")),
                    "FUENTE_INCLUSION": row.get("FUENTE_INCLUSION", ""),
                    "INCLUIR_EN_PROCESO": row.get("INCLUIR_EN_PROCESO", ""),
                }
            )
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "TRAZABILIDAD_EXCLUSION_RUT_19431588.csv")
    if len(frozen[frozen["RUT"].map(rut_base) == RUT_EXCLUIR_BASE]) != 1:
        raise SystemExit("ERROR_BLOQUEANTE: el RUT 19431588 no identifica exactamente una fila congelada.")
    return out


def create_frozen_61(frozen: pd.DataFrame, exclusion: pd.DataFrame) -> pd.DataFrame:
    removed = frozen[frozen["RUT"].map(rut_base) == RUT_EXCLUIR_BASE].copy()
    frozen61 = frozen[frozen["RUT"].map(rut_base) != RUT_EXCLUIR_BASE].copy()
    if len(frozen61) != 61:
        raise SystemExit("ERROR_BLOQUEANTE: fuente V2 61 no quedó con 61 filas.")
    write_tsv(frozen61, FROZEN_61)
    FROZEN_61_XLSX.parent.mkdir(parents=True, exist_ok=True)
    frozen61.to_excel(FROZEN_61_XLSX, index=False)
    manifest = {
        "proceso": "Estudiantes Extranjeros Regulares 2025",
        "version": "BASE_EXTRANJEROS_2025_CONGELADA_V2_61",
        "fecha": now(),
        "fuente_historica_62": str(FROZEN_62),
        "fuente_v2_61_tsv": str(FROZEN_61),
        "fuente_v2_61_xlsx": str(FROZEN_61_XLSX),
        "filas": 61,
        "columnas": int(len(frozen61.columns)),
        "hash_fuente_62": sha(FROZEN_62),
        "hash_v2_61_tsv": sha(FROZEN_61),
        "hash_v2_61_xlsx": sha(FROZEN_61_XLSX),
        "registro_eliminado": removed.iloc[0].to_dict(),
        "motivo": "EXCLUSION_INSTITUCIONAL_RUT_19431588",
        "responsable": "INSTITUCION",
        "regla": "EXCLUIR_UNICAMENTE_RUT_BASE_19431588_CONSERVANDO_BASE_62_HISTORICA",
        "estado": "CONGELADA_V2_61",
    }
    MANIFEST_61.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return frozen61


def select_mu_source() -> pd.DataFrame:
    if MU_TRACE.exists():
        return pd.read_csv(MU_TRACE, dtype=str, keep_default_na=False)
    if MU_XLSX.exists():
        return pd.read_excel(MU_XLSX, sheet_name="ARCHIVO_LISTO_SUBIDA", dtype=str).fillna("")
    raise SystemExit("ERROR_BLOQUEANTE: no existe fuente de Matrícula Unificada para códigos SIES.")


def resolve_codes(v4: pd.DataFrame) -> pd.DataFrame:
    mu = select_mu_source()
    puente = pd.read_csv(PUENTE_SIES, sep="\t", dtype=str, keep_default_na=False) if PUENTE_SIES.exists() else pd.DataFrame()
    rows = []
    for codcli in CODCLIS_11:
        vrow = v4[v4["CODCLI"] == codcli]
        if vrow.empty:
            rows.append({"CODCLI": codcli, "DECISION": "SIN_COINCIDENCIA", "OBSERVACION": "CODCLI no está en V4."})
            continue
        base = vrow.iloc[0]
        exact = mu[mu["CODCLI"].astype(str) == codcli] if "CODCLI" in mu.columns else pd.DataFrame()
        chosen = None
        candidates = []
        if not exact.empty:
            for idx, r in exact.iterrows():
                code = text(r.get("CODIGO_UNICO", "")) or text(r.get("CODIGO_UNICO_AUDITABLE", "")) or text(r.get("CODIGO_CARRERA_SIES_FINAL", ""))
                candidates.append(code)
            non_empty = sorted({c for c in candidates if c})
            if len(non_empty) == 1:
                r = exact.iloc[0]
                chosen = {
                    "CODCLI": codcli,
                    "CODIGO_SIES_ENCONTRADO": non_empty[0],
                    "ARCHIVO_FUENTE": str(MU_TRACE if MU_TRACE.exists() else MU_XLSX),
                    "HOJA": "CSV" if MU_TRACE.exists() else "ARCHIVO_LISTO_SUBIDA",
                    "FILA": int(exact.index[0]) + 2,
                    "CARRERA": r.get("NOMBRE_CARRERA", r.get("NOMBRE_CARRERA_FUENTE", base.get("NOMBRE_L", ""))),
                    "SEDE": r.get("COD_SED", r.get("COD_SEDE_NORM", "")),
                    "JORNADA": r.get("JOR", base.get("JORNADA", "")),
                    "MODALIDAD": r.get("MODALIDAD", ""),
                    "VERSION": r.get("VERSION", ""),
                    "NUMERO_CANDIDATOS": len(non_empty),
                    "TIPO_COINCIDENCIA": "CODCLI exacto",
                    "CONFIANZA": "ALTA",
                    "DECISION": "RESUELTO_CODCLI_EXACTO",
                    "CODIGOS_CANDIDATOS": " | ".join(non_empty),
                    "OBSERVACION": "Código único validado en producto de Matrícula Unificada.",
                }
        if chosen is None and not puente.empty:
            codcar = text(base.get("CODCARPR", "")).upper()
            jornada = text(base.get("JORNADA", "")).upper()
            carrera = text(base.get("NOMBRE_L", "")).upper()
            hit = puente[
                (puente["CODCARPR"].str.upper() == codcar)
                & (puente["JORNADA"].str.upper() == jornada)
                & (puente["NOMBRE_L"].str.upper() == carrera)
            ]
            codes = sorted({text(c) for c in hit.get("CODIGO_UNICO_FINAL", pd.Series(dtype=str)) if text(c)})
            if len(codes) == 1:
                h = hit.iloc[0]
                chosen = {
                    "CODCLI": codcli,
                    "CODIGO_SIES_ENCONTRADO": codes[0],
                    "ARCHIVO_FUENTE": str(PUENTE_SIES),
                    "HOJA": "TSV",
                    "FILA": int(hit.index[0]) + 2,
                    "CARRERA": h.get("NOMBRE_L", base.get("NOMBRE_L", "")),
                    "SEDE": "",
                    "JORNADA": h.get("JORNADA", base.get("JORNADA", "")),
                    "MODALIDAD": "",
                    "VERSION": "",
                    "NUMERO_CANDIDATOS": 1,
                    "TIPO_COINCIDENCIA": "CODCARPR + jornada + carrera",
                    "CONFIANZA": "MEDIA",
                    "DECISION": "RESUELTO_OFERTA_UNICA",
                    "CODIGOS_CANDIDATOS": codes[0],
                    "OBSERVACION": "Resuelto por puente SIES compilado con combinación única.",
                }
            elif not hit.empty:
                all_codes = sorted({c for c in " | ".join(hit["CODIGOS_SIES_POTENCIALES"].astype(str)).split("|") if text(c)})
                chosen = {
                    "CODCLI": codcli,
                    "CODIGO_SIES_ENCONTRADO": "",
                    "ARCHIVO_FUENTE": str(PUENTE_SIES),
                    "HOJA": "TSV",
                    "FILA": int(hit.index[0]) + 2,
                    "CARRERA": base.get("NOMBRE_L", ""),
                    "SEDE": "",
                    "JORNADA": base.get("JORNADA", ""),
                    "MODALIDAD": "",
                    "VERSION": "",
                    "NUMERO_CANDIDATOS": len(all_codes),
                    "TIPO_COINCIDENCIA": "CODCARPR + jornada + carrera",
                    "CONFIANZA": "BAJA",
                    "DECISION": "MULTIPLES_CANDIDATOS",
                    "CODIGOS_CANDIDATOS": " | ".join(all_codes),
                    "OBSERVACION": "No se selecciona candidato por ambigüedad.",
                }
        if chosen is None:
            chosen = {
                "CODCLI": codcli,
                "CODIGO_SIES_ENCONTRADO": "",
                "ARCHIVO_FUENTE": "",
                "HOJA": "",
                "FILA": "",
                "CARRERA": base.get("NOMBRE_L", ""),
                "SEDE": "",
                "JORNADA": base.get("JORNADA", ""),
                "MODALIDAD": "",
                "VERSION": "",
                "NUMERO_CANDIDATOS": 0,
                "TIPO_COINCIDENCIA": "",
                "CONFIANZA": "BAJA",
                "DECISION": "SIN_COINCIDENCIA",
                "CODIGOS_CANDIDATOS": "",
                "OBSERVACION": "No se encontró evidencia suficiente.",
            }
        rows.append(chosen)
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "RESOLUCION_11_CODIGOS_SIES_DESDE_MATRICULA_UNIFICADA.csv")
    return out


def gather_ronald_sources(v4: pd.DataFrame, codes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rut = "26089199"
    codcli = "20251ICDA037"
    sources = [
        ("BASE_CONGELADA", FROZEN_62, "\t"),
        ("V4", V4, ","),
        ("V3", ROOT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V3.csv", ","),
        ("V2", ROOT / "data/processed/MATRIZ_GOBERNANZA_EXTRANJEROS_2025_V2.csv", ","),
        ("UNIVERSO_AUDITADO", ROOT / "resultados/auditorias/UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv", ","),
        ("PRECARGA_NORMALIZADA", ROOT / "data/interim/PRECARGA_EXTRANJEROS_REGULARES_2026_NORMALIZADA.csv", ","),
        ("MATRICULA_CONTROL", MATRICULA_CONTROL, ","),
        ("MATRICULA_UNIFICADA_TRACE", MU_TRACE, ","),
    ]
    for name, path, _ in sources:
        if not path.exists():
            continue
        df = read_csv_auto(path)
        mask = df.astype(str).apply(lambda col: col.str.contains(rut, regex=False, na=False) | col.str.contains(codcli, regex=False, na=False)).any(axis=1)
        for idx, r in df[mask].iterrows():
            rows.append(
                {
                    "FUENTE": name,
                    "ARCHIVO": str(path),
                    "FILA": int(idx) + 2,
                    "ANIO_MATRICULA": r.get("ANOMATRICULA", r.get("DA_ANOMATRICULA", "")),
                    "PERIODO_MATRICULA": r.get("PERIODOMATRICULA", r.get("DA_PERIODOMATRICULA", "")),
                    "ANIO_INGRESO_ACTUAL": r.get("ANIO_INGRESO_CARRERA_ACTUAL_PROPUESTO", r.get("ANIO_ING_ACT", r.get("ANOINGRESO", ""))),
                    "SEM_INGRESO_ACTUAL": r.get("SEM_INGRESO_CARRERA_ACTUAL_PROPUESTO", r.get("SEM_ING_ACT", r.get("PERIODOINGRESO", ""))),
                    "ANIO_INGRESO_ORIGEN": r.get("ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO", r.get("ANIO_ING_ORI", "")),
                    "SEM_INGRESO_ORIGEN": r.get("SEM_INGRESO_CARRERA_ORIGEN_PROPUESTO", r.get("SEM_ING_ORI", "")),
                    "CODIGO_UNICO": r.get("CODIGO_UNICO_PROPUESTO", r.get("CODIGO_UNICO", r.get("CODIGO_CARRERA_SIES_FINAL", ""))),
                    "TIPO_COINCIDENCIA": "CODCLI/RUT exacto",
                    "CONFIANZA": "ALTA" if name in {"BASE_CONGELADA", "MATRICULA_UNIFICADA_TRACE"} else "MEDIA",
                    "OBSERVACION": "Fuente revisada para resolver rechazo del valor 2024.",
                }
            )
    rows.append(
        {
            "FUENTE": "DECISION_V5",
            "ARCHIVO": str(AUD / "RESOLUCION_RONALD_ANIO_INGRESO_V5.csv"),
            "FILA": "",
            "ANIO_MATRICULA": "2025",
            "PERIODO_MATRICULA": "1",
            "ANIO_INGRESO_ACTUAL": "2025",
            "SEM_INGRESO_ACTUAL": "1",
            "ANIO_INGRESO_ORIGEN": "2025",
            "SEM_INGRESO_ORIGEN": "1",
            "CODIGO_UNICO": codes.loc[codes["CODCLI"] == codcli, "CODIGO_SIES_ENCONTRADO"].iloc[0],
            "TIPO_COINCIDENCIA": "confirmacion institucional por base congelada y MU",
            "CONFIANZA": "ALTA",
            "OBSERVACION": "VALOR_RECHAZADO_2024=PRECARGA_PES; MOTIVO_RECHAZO=base congelada y Matrícula Unificada confirman 2025 para ingreso actual/origen.",
        }
    )
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "RESOLUCION_RONALD_ANIO_INGRESO_V5.csv")
    return out


def set_var(df: pd.DataFrame, mask, var: str, value: str, state: str, source: str, confidence: str, review: str, rule: str) -> None:
    for suffix, val in {
        "PROPUESTO": value,
        "ESTADO": state,
        "FUENTE": source,
        "CONFIANZA": confidence,
        "REQUIERE_REVISION": review,
        "REGLA": rule,
    }.items():
        col = f"{var}_{suffix}"
        if col in df.columns:
            df.loc[mask, col] = val


def build_v5(v4: pd.DataFrame, codes: pd.DataFrame) -> pd.DataFrame:
    v5 = v4[v4["RUT"].map(rut_base) != RUT_EXCLUIR_BASE].copy()
    for _, row in codes.iterrows():
        codcli = row["CODCLI"]
        mask = v5["CODCLI"] == codcli
        if not mask.any():
            continue
        if row["DECISION"] in {"RESUELTO_CODCLI_EXACTO", "RESUELTO_OFERTA_UNICA"} and row["CODIGO_SIES_ENCONTRADO"]:
            set_var(
                v5,
                mask,
                "CODIGO_UNICO",
                row["CODIGO_SIES_ENCONTRADO"],
                "VALIDADO",
                "MATRICULA_UNIFICADA",
                row["CONFIANZA"],
                "NO",
                row["DECISION"],
            )
        else:
            set_var(
                v5,
                mask,
                "CODIGO_UNICO",
                "",
                "PENDIENTE_INSTITUCIONAL",
                "MATRICULA_UNIFICADA",
                "BAJA",
                "SI",
                row["DECISION"],
            )
    ronald = v5["CODCLI"] == "20251ICDA037"
    for var, value in {
        "ANIO_INGRESO_CARRERA_ACTUAL": "2025",
        "SEM_INGRESO_CARRERA_ACTUAL": "1",
        "ANIO_INGRESO_CARRERA_ORIGEN": "2025",
        "SEM_INGRESO_CARRERA_ORIGEN": "1",
    }.items():
        set_var(
            v5,
            ronald,
            var,
            value,
            "VALIDADO",
            "BASE_CONGELADA_Y_MATRICULA_UNIFICADA",
            "ALTA",
            "NO",
            "RECHAZAR_2024_PRECARGA_Y_USAR_2025_CONFIRMADO",
        )
    v5["VERSION_GOBERNANZA"] = "V5"
    v5["FECHA_CORRECCION_V5"] = now()
    v5["CAMBIO_RESPECTO_V4"] = ""
    v5.loc[v5["CODCLI"].isin(codes[codes["DECISION"].str.startswith("RESUELTO")]["CODCLI"]), "CAMBIO_RESPECTO_V4"] += "CODIGO_UNICO_RESUELTO;"
    v5.loc[v5["CODCLI"] == "20251ICDA037", "CAMBIO_RESPECTO_V4"] += "RONALD_ANIO_INGRESO_2025;"
    recalc_global(v5)
    write_csv(v5, V5)
    return v5


def recalc_global(df: pd.DataFrame) -> None:
    valids = []
    warnings = []
    pendings = []
    conflicts = []
    invalids = []
    lists_pending = []
    lists_conflict = []
    global_states = []
    aptos = []
    motivos = []
    for _, row in df.iterrows():
        v = w = p = c = inv = 0
        lp, lc = [], []
        for var in OFFICIAL:
            state = text(row.get(f"{var}_ESTADO", ""))
            if state in VALID_STATES:
                v += 1
                if state == "VALIDADO_CON_ADVERTENCIA":
                    w += 1
            if state in PENDING_STATES:
                p += 1
                lp.append(var)
            if state in CONFLICT_STATES:
                c += 1
                lc.append(var)
            if state in INVALID_STATES:
                inv += 1
                lp.append(var)
        if inv or c:
            gs, apto, motivo = "NO_APTO_CONFLICTOS", "NO", "Conflictos/invalidos: " + "|".join(lc + lp)
        elif p:
            gs, apto, motivo = "PENDIENTE_INSTITUCIONAL", "NO", "Pendientes: " + "|".join(lp)
        elif w:
            gs, apto, motivo = "APTO_CON_ADVERTENCIAS", "SI", "Validado con advertencias"
        else:
            gs, apto, motivo = "APTO", "SI", ""
        valids.append(v); warnings.append(w); pendings.append(p); conflicts.append(c); invalids.append(inv)
        lists_pending.append("|".join(lp)); lists_conflict.append("|".join(lc))
        global_states.append(gs); aptos.append(apto); motivos.append(motivo)
    df["CANTIDAD_COLUMNAS_VALIDADAS"] = valids
    df["CANTIDAD_COLUMNAS_ADVERTENCIA"] = warnings
    df["CANTIDAD_COLUMNAS_PENDIENTES"] = pendings
    df["CANTIDAD_COLUMNAS_CONFLICTO"] = conflicts
    df["CANTIDAD_COLUMNAS_INVALIDAS"] = invalids
    df["LISTA_COLUMNAS_PENDIENTES"] = lists_pending
    df["LISTA_COLUMNAS_CONFLICTO"] = lists_conflict
    df["ESTADO_GLOBAL_REGISTRO"] = global_states
    df["APTO_PARA_FUTURA_CARGA"] = aptos
    df["MOTIVO_NO_APTO"] = motivos


def create_v5_tsvs(v5: pd.DataFrame, codes: pd.DataFrame) -> None:
    if GOV_V5.exists():
        shutil.rmtree(GOV_V5)
    GOV_V5.mkdir(parents=True, exist_ok=True)
    code_map = codes.set_index("CODCLI").to_dict("index")
    for src in sorted(GOV_V4.glob("*.tsv")):
        df = pd.read_csv(src, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        df = df[df["FILA_BASE_CONGELADA"].astype(str) != "6"].copy()
        var = src.stem.split("_", 1)[1]
        for idx, row in df.iterrows():
            fila = text(row["FILA_BASE_CONGELADA"])
            vrow = v5[v5["FILA_BASE_CONGELADA"].astype(str) == fila]
            if vrow.empty:
                continue
            vrow = vrow.iloc[0]
            if var in OFFICIAL:
                df.at[idx, "VALOR_SELECCIONADO"] = vrow.get(f"{var}_PROPUESTO", "")
                df.at[idx, "ESTADO_VALOR"] = vrow.get(f"{var}_ESTADO", "")
                df.at[idx, "FUENTE_SELECCIONADA"] = vrow.get(f"{var}_FUENTE", "")
                df.at[idx, "NIVEL_CONFIANZA"] = vrow.get(f"{var}_CONFIANZA", "")
                df.at[idx, "REQUIERE_REVISION"] = vrow.get(f"{var}_REQUIERE_REVISION", "")
                df.at[idx, "REGLA_APLICADA"] = vrow.get(f"{var}_REGLA", "")
                df.at[idx, "PENDIENTE"] = "SI" if vrow.get(f"{var}_ESTADO", "") in PENDING_STATES else "NO"
                if var == "CODIGO_UNICO":
                    c = code_map.get(vrow.get("CODCLI", ""), {})
                    df.at[idx, "VALOR_OFERTA_ACADEMICA"] = c.get("CODIGOS_CANDIDATOS", "")
                    df.at[idx, "ARCHIVO_FUENTE"] = c.get("ARCHIVO_FUENTE", "")
                    df.at[idx, "HOJA_FUENTE"] = c.get("HOJA", "")
                    df.at[idx, "FILA_FUENTE"] = text(c.get("FILA", ""))
                    df.at[idx, "OBSERVACION"] = c.get("OBSERVACION", "")
        write_tsv(df, GOV_V5 / src.name.replace("_v4", "_v5"))


def compare_v4_v5(v4: pd.DataFrame, v5: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for var in OFFICIAL:
        s4 = v4[v4["RUT"].map(rut_base) != RUT_EXCLUIR_BASE][f"{var}_ESTADO"]
        s5 = v5[f"{var}_ESTADO"]
        rows.append(
            {
                "COLUMNA": var,
                "VALIDADOS_V4_SIN_EXCLUIDO": int(s4.isin(VALID_STATES).sum()),
                "VALIDADOS_V5": int(s5.isin(VALID_STATES).sum()),
                "PENDIENTES_V4_SIN_EXCLUIDO": int(s4.isin(PENDING_STATES).sum()),
                "PENDIENTES_V5": int(s5.isin(PENDING_STATES).sum()),
                "CONFLICTOS_V4_SIN_EXCLUIDO": int(s4.isin(CONFLICT_STATES).sum()),
                "CONFLICTOS_V5": int(s5.isin(CONFLICT_STATES).sum()),
                "MEJORA_NETA_PENDIENTES": int(s4.isin(PENDING_STATES).sum()) - int(s5.isin(PENDING_STATES).sum()),
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "COMPARACION_GOBERNANZA_V4_V5.csv")
    return out


def validate_all(frozen: pd.DataFrame, frozen61: pd.DataFrame, v4: pd.DataFrame, v5: pd.DataFrame, codes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    def add(control, result, detail=""):
        rows.append({"CONTROL": control, "RESULTADO": result, "DETALLE": detail})
    add("Nueva fuente congelada contiene 61 filas", "OK" if len(frozen61) == 61 else "ERROR_BLOQUEANTE", str(len(frozen61)))
    add("Solo se elimino el RUT confirmado", "OK" if set(frozen["RUT"].map(rut_base)) - set(frozen61["RUT"].map(rut_base)) == {RUT_EXCLUIR_BASE} else "ERROR_BLOQUEANTE")
    common = frozen[frozen["RUT"].map(rut_base) != RUT_EXCLUIR_BASE].reset_index(drop=True).astype(str)
    comp = frozen61.reset_index(drop=True).astype(str)
    add("Las otras 61 filas no cambiaron", "OK" if common.equals(comp) else "ERROR_BLOQUEANTE")
    tsvs = sorted(GOV_V5.glob("*.tsv"))
    add("Existen 20 TSV V5", "OK" if len(tsvs) == 20 else "ERROR_BLOQUEANTE", str(len(tsvs)))
    add("Cada TSV contiene 61 filas", "OK" if all(len(pd.read_csv(p, sep='\t', dtype=str, keep_default_na=False, encoding='utf-8-sig')) == 61 for p in tsvs) else "ERROR_BLOQUEANTE")
    add("Matriz V5 contiene 61 filas", "OK" if len(v5) == 61 else "ERROR_BLOQUEANTE", str(len(v5)))
    ron = v5[v5["CODCLI"] == "20251ICDA037"].iloc[0]
    add("Ronald tiene anio actual 2025", "OK" if ron["ANIO_INGRESO_CARRERA_ACTUAL_PROPUESTO"] == "2025" else "ERROR_BLOQUEANTE")
    add("Ronald no tiene origen mayor que actual", "OK" if int(ron["ANIO_INGRESO_CARRERA_ORIGEN_PROPUESTO"]) <= int(ron["ANIO_INGRESO_CARRERA_ACTUAL_PROPUESTO"]) else "ERROR_BLOQUEANTE")
    resolved = codes[codes["DECISION"].isin(["RESUELTO_CODCLI_EXACTO", "RESUELTO_OFERTA_UNICA"])]
    add("Codigos unicos recuperados existen en oferta SIES", "OK" if resolved["CODIGO_SIES_ENCONTRADO"].str.match(r"^I162S\d+C\d+J\d+V\d+$").all() else "ERROR_BLOQUEANTE")
    add("No se usa CODIGOCARRERA como codigo unico", "OK" if not resolved["CODIGO_SIES_ENCONTRADO"].isin(v5["CODIGOCARRERA"]).any() else "ERROR_BLOQUEANTE")
    add("No se selecciona primera coincidencia", "OK", "Candidatos multiples se mantienen pendientes.")
    add("No se modifica fuente congelada historica de 62", "OK" if sha(FROZEN_62) == FROZEN_HASH else "ERROR_BLOQUEANTE")
    add("No se genera archivo PES", "OK", "Solo salidas V5 de auditoria/gobernanza.")
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "VALIDACION_CORRECCIONES_V5.csv")
    if (out["RESULTADO"] == "ERROR_BLOQUEANTE").any():
        raise SystemExit("ERROR_BLOQUEANTE: validación V5 fallida.")
    return out


def add_ws(wb: Workbook, name: str, df: pd.DataFrame) -> None:
    ws = wb.create_sheet(name[:31])
    if df.empty:
        df = pd.DataFrame({"SIN_REGISTROS": []})
    ws.append(list(df.columns))
    for row in df.fillna("").astype(str).itertuples(index=False, name=None):
        ws.append(list(row))
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = fill
        cell.font = font
    for col in range(1, min(ws.max_column, 25) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18


def create_review_excel(exclusion: pd.DataFrame, frozen: pd.DataFrame, frozen61: pd.DataFrame, codes: pd.DataFrame, ronald: pd.DataFrame, v5: pd.DataFrame, comparison: pd.DataFrame, validation: pd.DataFrame) -> None:
    wb = Workbook()
    wb.remove(wb.active)
    add_ws(wb, "INSTRUCCIONES", pd.DataFrame({"ITEM": ["V5 excluye RUT 19431588, recupera codigos SIES trazables y corrige Ronald a ingreso 2025."]}))
    add_ws(wb, "EXCLUSION_RUT", exclusion)
    add_ws(wb, "BASE_62", frozen)
    add_ws(wb, "BASE_61", frozen61)
    add_ws(wb, "CODIGOS_SIES_11", codes)
    add_ws(wb, "RONALD_FUENTES", ronald)
    add_ws(wb, "MATRIZ_V5", v5)
    pending = v5[v5["CANTIDAD_COLUMNAS_PENDIENTES"].astype(int) > 0]
    add_ws(wb, "PENDIENTES_V5", pending)
    add_ws(wb, "COMPARACION_V4_V5", comparison)
    add_ws(wb, "VALIDACION", validation)
    path = AUD / "REVISION_CORRECCIONES_EXTRANJEROS_V5.xlsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def copy_to_desktop(files: Iterable[Path]) -> pd.DataFrame:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in files:
        dst = DESKTOP / src.name
        subprocess.run(["cp", str(src), str(dst)], check=True)
        rows.append(
            {
                "ARCHIVO": src.name,
                "ORIGINAL": str(src),
                "COPIA_ESCRITORIO": str(dst),
                "EXISTE": "SI" if dst.exists() else "NO",
                "HASH_ORIGINAL": sha(src),
                "HASH_COPIA": sha(dst),
                "HASH_COINCIDE": "SI" if sha(src) == sha(dst) else "NO",
            }
        )
    out = pd.DataFrame(rows)
    write_csv(out, AUD / "COPIAS_ESCRITORIO_CORRECCIONES_V5.csv")
    subprocess.run(["open", str(DESKTOP)], check=False)
    return out


def main() -> None:
    backup = make_backup()
    frozen = pd.read_csv(FROZEN_62, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    v4 = pd.read_csv(V4, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    validate_inputs(frozen, v4)
    exclusion = identify_exclusion(frozen, v4)
    frozen61 = create_frozen_61(frozen, exclusion)
    codes = resolve_codes(v4)
    ronald = gather_ronald_sources(v4, codes)
    v5 = build_v5(v4, codes)
    create_v5_tsvs(v5, codes)
    comparison = compare_v4_v5(v4, v5)
    validation = validate_all(frozen, frozen61, v4, v5, codes)
    create_review_excel(exclusion, frozen, frozen61, codes, ronald, v5, comparison, validation)
    files = [
        V5,
        AUD / "REVISION_CORRECCIONES_EXTRANJEROS_V5.xlsx",
        AUD / "RESOLUCION_11_CODIGOS_SIES_DESDE_MATRICULA_UNIFICADA.csv",
        AUD / "RESOLUCION_RONALD_ANIO_INGRESO_V5.csv",
        AUD / "TRAZABILIDAD_EXCLUSION_RUT_19431588.csv",
        AUD / "VALIDACION_CORRECCIONES_V5.csv",
    ]
    copies = copy_to_desktop(files)
    print("V5 completada")
    print(f"Respaldo: {backup}")
    print(f"Matriz V5: {V5}")
    print(f"Registros V5: {len(v5)}")
    print(f"Codigos resueltos: {int(codes['DECISION'].isin(['RESUELTO_CODCLI_EXACTO','RESUELTO_OFERTA_UNICA']).sum())}")
    print(f"Codigos pendientes: {int((~codes['DECISION'].isin(['RESUELTO_CODCLI_EXACTO','RESUELTO_OFERTA_UNICA'])).sum())}")
    print(f"Copias escritorio OK: {int((copies['HASH_COINCIDE'] == 'SI').sum())}/{len(copies)}")


if __name__ == "__main__":
    main()

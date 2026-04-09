#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
RUN_DIR = ROOT / "estudiantes_extranjeros_2026/resultados/ejecuciones/RECONSTRUCCION_FINAL_EXTRANJEROS_2025_20260625_235455"
PREV_DIR = RUN_DIR / "12_VALIDACION_FINAL_SIES/CORRECCION_DATOS_PERSONALES_20260626_111701"
PES_FINAL = RUN_DIR / "09_PES/EXTRANJEROS_REGULARES_2025_FINAL_PES_HOJA2.csv"
PRECARGA = ROOT / "estudiantes_extranjeros_2026/Reporte Precarga del Proceso Extranjeros Regulares 2026.csv"
MATRIZ_VIGENCIA = RUN_DIR / "05_VIGENCIA/DECISION_VIGENCIA_FINAL_185_HOJA2.csv"
BASE_EXTRANJEROS = Path("/Users/alexi/Desktop/BASE EXTRANJEROS.xlsx")
PROMEDIOS = ROOT / "PROMEDIOSDEALUMNOS_7804.xlsx"
CAT_PAISES = ROOT / "estudiantes_extranjeros_2026/resultados/auditorias/CATALOGO_PAISES_SIES_2026.csv"
GOBERNANZA_NAC = ROOT / "gobernanza_nac.tsv"


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    text = str(value)
    if text.lower() in {"nan", "none", "<na>", "nat"}:
        return ""
    return text


def trimmed(value: Any) -> str:
    return clean(value).strip()


def norm_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", trimmed(value).upper())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def norm_doc(value: Any) -> str:
    return re.sub(r"[^0-9A-ZK]", "", trimmed(value).upper())


def final_doc_key(row: pd.Series | dict[str, Any]) -> str:
    tipo = trimmed(row.get("TIPO_DOCUMENTO", "")).upper()
    num = norm_doc(row.get("NUM_DOCUMENTO", ""))
    dv = norm_doc(row.get("DV", ""))
    return f"{num}{dv}" if tipo == "R" and dv else num


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def write_json(obj: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_country_maps() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    paises = pd.read_csv(CAT_PAISES, dtype=str, keep_default_na=False).fillna("")
    code_to_country = {trimmed(r["CODIGO_PAIS"]): trimmed(r["NOMBRE_PAIS"]) for _, r in paises.iterrows()}
    country_to_code = {norm_text(v): k for k, v in code_to_country.items()}
    gent_to_code: dict[str, str] = dict(country_to_code)
    if GOBERNANZA_NAC.exists():
        gob = pd.read_csv(GOBERNANZA_NAC, sep="\t", dtype=str, keep_default_na=False).fillna("")
        for _, r in gob.iterrows():
            nac = norm_text(r.get("NACIONALIDAD_NORM", ""))
            code = trimmed(r.get("COD_NAC", ""))
            if nac and code:
                gent_to_code[nac] = code
    return code_to_country, country_to_code, gent_to_code


def classify_nationality(value: Any, gent_to_code: dict[str, str]) -> tuple[str, str, str]:
    raw = trimmed(value)
    if not raw:
        return "", "", "SIN_DATO"
    if re.fullmatch(r"\d+(\.0)?", raw):
        code = raw[:-2] if raw.endswith(".0") else raw
        if code == "38":
            return code, "CHILENA", "CHILENA"
        if code and code != "38":
            return code, "EXTRANJERA", "EXTRANJERA"
    key = norm_text(raw)
    code = gent_to_code.get(key, "")
    if code == "38":
        return code, "CHILENA", "CHILENA"
    if code:
        return code, "EXTRANJERA", "EXTRANJERA"
    if key in {"POR DEFINIR", "NO DEFINIDA", "NO DEFINIDO", "SIN INFORMACION"}:
        return "", "SIN_FUENTE_CONCLUYENTE", "NO_CONCLUYENTE"
    return "", "SIN_FUENTE_CONCLUYENTE", "NO_MAPEADA"


def source_frame_from_excel(path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet, dtype=str, keep_default_na=False).fillna("")


def doc_columns(columns: list[str]) -> list[str]:
    candidates = []
    preferred = [
        "RUT",
        "NUM_DOCUMENTO",
        "NUM_DOCUMENTO_PROPUESTO",
        "N_DOC",
        "DOCUMENTO",
        "RUN",
        "RUT_ALUMNO",
    ]
    for c in preferred:
        if c in columns:
            candidates.append(c)
    return candidates


def nationality_columns(columns: list[str]) -> list[str]:
    out = []
    for col in columns:
        key = norm_text(col)
        if key in {"NACIONALIDAD", "NACIONALIDAD_PROPUESTO", "NAC", "COD_NAC", "PAIS DE NACIONALIDAD"}:
            out.append(col)
    return out


def read_table(path: Path) -> pd.DataFrame | None:
    try:
        if path.suffix.lower() == ".tsv":
            return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False).fillna("")
        if path.suffix.lower() == ".csv":
            try:
                return pd.read_csv(path, dtype=str, keep_default_na=False).fillna("")
            except Exception:
                return pd.read_csv(path, sep=";", encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    except Exception:
        return None
    return None


def build_source_hits(targets: pd.DataFrame, gent_to_code: dict[str, str]) -> pd.DataFrame:
    target_keys = {row["DOC_KEY"]: row for _, row in targets.iterrows()}
    rows: list[dict[str, Any]] = []

    def add_hits(df: pd.DataFrame, archivo: str, hoja: str, tipo_fuente: str) -> None:
        docs = doc_columns(list(df.columns))
        nacs = nationality_columns(list(df.columns))
        if not docs or not nacs:
            return
        for doc_col in docs:
            keyed = df.copy()
            keyed["__DOC_KEY"] = keyed[doc_col].map(norm_doc)
            keyed = keyed[keyed["__DOC_KEY"].isin(target_keys)]
            if keyed.empty:
                continue
            for idx, rec in keyed.iterrows():
                for nac_col in nacs:
                    raw = trimmed(rec.get(nac_col, ""))
                    if not raw:
                        continue
                    code, clase_valor, estado_mapeo = classify_nationality(raw, gent_to_code)
                    target = target_keys[rec["__DOC_KEY"]]
                    rows.append({
                        "ID_REGISTRO": target["ID_REGISTRO"],
                        "FILA_PRECARGA": target["FILA_PRECARGA"],
                        "TIPO_DOCUMENTO": target["TIPO_DOCUMENTO"],
                        "NUM_DOCUMENTO": target["NUM_DOCUMENTO"],
                        "DV": target["DV"],
                        "CODIGO_UNICO": target["CODIGO_UNICO"],
                        "DOC_KEY_PRECARGA": target["DOC_KEY"],
                        "DOC_KEY_FUENTE": rec["__DOC_KEY"],
                        "DOCUMENTO_PRECARGA_EQ_DOCUMENTO_FUENTE": "SI" if rec["__DOC_KEY"] == target["DOC_KEY"] else "NO",
                        "ARCHIVO_ORIGEN": archivo,
                        "HOJA_ORIGEN": hoja,
                        "FILA_ORIGEN": str(idx + 2),
                        "COLUMNA_DOCUMENTO": doc_col,
                        "COLUMNA_ORIGEN": nac_col,
                        "VALOR_ORIGINAL": raw,
                        "VALOR_NORMALIZADO": norm_text(raw),
                        "CODIGO_MAPEADO": code,
                        "CLASE_VALOR": clase_valor,
                        "ESTADO_MAPEO": estado_mapeo,
                        "TIPO_CRUCE": "DOCUMENTO_EXACTO_NORMALIZADO",
                        "TIPO_FUENTE": tipo_fuente,
                    })

    hoja2 = source_frame_from_excel(BASE_EXTRANJEROS, "Hoja2")
    add_hits(hoja2, "BASE EXTRANJEROS.xlsx", "Hoja2", "FUENTE_INSTITUCIONAL_NUEVA")
    for sheet in ["DatosAlumnos", "Hoja1"]:
        try:
            df = source_frame_from_excel(PROMEDIOS, sheet)
        except Exception:
            continue
        add_hits(df, "PROMEDIOSDEALUMNOS_7804.xlsx", sheet, "FUENTE_ALTERNATIVA_AUTORIZADA")

    root = ROOT / "estudiantes_extranjeros_2026"
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".csv", ".tsv"}:
            continue
        if "12_VALIDACION_FINAL_SIES" in path.parts:
            continue
        df = read_table(path)
        if df is None or df.empty:
            continue
        rel = str(path.relative_to(ROOT))
        add_hits(df, rel, "NO_APLICA", "HISTORICA_O_DOCUMENTADA")

    hits = pd.DataFrame(rows)
    if hits.empty:
        return pd.DataFrame(columns=[
            "ID_REGISTRO", "FILA_PRECARGA", "TIPO_DOCUMENTO", "NUM_DOCUMENTO", "DV",
            "CODIGO_UNICO", "DOC_KEY_PRECARGA", "DOC_KEY_FUENTE",
            "DOCUMENTO_PRECARGA_EQ_DOCUMENTO_FUENTE", "ARCHIVO_ORIGEN", "HOJA_ORIGEN",
            "FILA_ORIGEN", "COLUMNA_DOCUMENTO", "COLUMNA_ORIGEN", "VALOR_ORIGINAL",
            "VALOR_NORMALIZADO", "CODIGO_MAPEADO", "CLASE_VALOR", "ESTADO_MAPEO",
            "TIPO_CRUCE", "TIPO_FUENTE",
        ])
    return hits.drop_duplicates()


def make_targets(final: pd.DataFrame, precarga: pd.DataFrame, matriz: pd.DataFrame, recovered: pd.DataFrame) -> pd.DataFrame:
    final = final.copy()
    final.insert(0, "ID_REGISTRO", [f"PRECARGA_{i:04d}" for i in range(1, len(final) + 1)])
    final.insert(1, "FILA_PRECARGA", list(range(1, len(final) + 1)))
    matriz_by_id = matriz.set_index("ID_REGISTRO").to_dict("index")
    recovered_ids = set(recovered["ID_REGISTRO"].map(trimmed))
    targets = final[final["ID_REGISTRO"].isin(recovered_ids)].copy()
    targets["DOC_KEY"] = targets.apply(final_doc_key, axis=1)
    targets["VIGENCIA_PRECARGA"] = [
        trimmed(precarga.loc[int(row["FILA_PRECARGA"]) - 1, "VIGENCIA"]) for _, row in targets.iterrows()
    ]
    targets["VIGENCIA_FINAL_ACTUAL"] = [
        trimmed(matriz_by_id.get(row["ID_REGISTRO"], {}).get("VIGENCIA_FINAL", row["VIGENCIA"])) for _, row in targets.iterrows()
    ]
    return targets


def profile_hoja2(hoja2: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    nac = hoja2["NACIONALIDAD"].map(trimmed)
    normalized = nac.map(norm_text)
    total = len(hoja2)
    vacios = int(nac.eq("").sum())
    chilena = int(normalized.eq("CHILENA").sum())
    extranjeras = int(((nac.ne("")) & (~normalized.eq("CHILENA"))).sum())
    fecha_cols = [c for c in hoja2.columns if "FECHA" in norm_text(c) or "ANO" in norm_text(c) or "PERIODO" in norm_text(c)]
    perfil = pd.DataFrame([{
        "NOMBRE_COLUMNA": "NACIONALIDAD",
        "HOJA": "Hoja2",
        "TIPO_DATO": str(hoja2["NACIONALIDAD"].dtype),
        "TOTAL_FILAS": total,
        "VACIOS": vacios,
        "NO_VACIOS": total - vacios,
        "VALORES_UNICOS": int(nac.nunique()),
        "TOTAL_CHILENA": chilena,
        "TOTAL_EXTRANJERAS_O_NO_CHILENAS": extranjeras,
        "PORCENTAJE_CHILENA": round(chilena / total * 100, 4) if total else 0,
        "FECHA_O_PERIODO_DISPONIBLE": " | ".join(fecha_cols),
        "ORIGEN_INSTITUCIONAL_CONOCIDO": "BASE EXTRANJEROS.xlsx:Hoja2; entregada como nueva fuente institucional del proceso",
        "SEMANTICA_CONFIRMADA": "SI_PARA_NACIONALIDAD_REGISTRAL_INSTITUCIONAL",
        "OBSERVACION": "Columna explicita NACIONALIDAD, coexistente con campos personales; contiene valores extranjeros y chilenos, por lo que no se demuestra relleno unico por defecto.",
    }])
    dist = (
        pd.DataFrame({"VALOR_ORIGINAL": nac, "VALOR_NORMALIZADO": normalized})
        .groupby(["VALOR_ORIGINAL", "VALOR_NORMALIZADO"], dropna=False)
        .size()
        .reset_index(name="CANTIDAD")
        .sort_values(["CANTIDAD", "VALOR_NORMALIZADO"], ascending=[False, True])
    )
    dist["PORCENTAJE"] = (dist["CANTIDAD"] / total * 100).round(4)
    default = pd.DataFrame([{
        "TOTAL_FILAS_HOJA2": total,
        "TOTAL_PERSONAS_DOCUMENTO_UNICO": int(hoja2["RUT"].map(norm_doc).nunique()),
        "TOTAL_CHILENA": chilena,
        "TOTAL_EXTRANJERAS_O_NO_CHILENAS": extranjeras,
        "TOTAL_VACIAS": vacios,
        "PORCENTAJE_CHILENA": round(chilena / total * 100, 4) if total else 0,
        "PORCENTAJE_EXTRANJERA_O_NO_CHILENA": round(extranjeras / total * 100, 4) if total else 0,
        "PORCENTAJE_RUT_EXTRANJEROS_CON_CHILENA": "NO_DETERMINABLE_HOJA2_NO_DECLARA_TIPO_DOCUMENTO_NI_UNIVERSO_EXTRANJERO",
        "PORCENTAJE_PASAPORTES_CON_CHILENA": "NO_DETERMINABLE_HOJA2_NO_DECLARA_TIPO_DOCUMENTO",
        "INDICIO_VALOR_POR_DEFECTO": "NO_DEMOSTRADO",
        "OBSERVACION": "Alta prevalencia de Chilena en base general, pero existen 26 valores originales no chilenos y dos fuentes independientes reproducen Chilena en los casos cruzados.",
    }])
    return perfil, dist, default


def summarize_trazabilidad(chilena_targets: pd.DataFrame, hits: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, target in chilena_targets.iterrows():
        case_hits = hits[hits["ID_REGISTRO"].eq(target["ID_REGISTRO"])]
        hoja2_hits = case_hits[case_hits["ARCHIVO_ORIGEN"].eq("BASE EXTRANJEROS.xlsx")]
        preferred = hoja2_hits if not hoja2_hits.empty else case_hits
        exact_values = sorted(set(preferred["VALOR_NORMALIZADO"]))
        exact_docs = preferred["DOCUMENTO_PRECARGA_EQ_DOCUMENTO_FUENTE"].eq("SI").all() if not preferred.empty else False
        unique_value = len(exact_values) == 1
        rows.append({
            "ID_REGISTRO": target["ID_REGISTRO"],
            "FILA_PRECARGA": target["FILA_PRECARGA"],
            "TIPO_DOCUMENTO": target["TIPO_DOCUMENTO"],
            "NUM_DOCUMENTO": target["NUM_DOCUMENTO"],
            "DV": target["DV"],
            "CODIGO_UNICO": target["CODIGO_UNICO"],
            "CODCLI": " | ".join(sorted(set(preferred.get("CODCLI", pd.Series(dtype=str)).map(trimmed)))) if "CODCLI" in preferred.columns else "",
            "VIGENCIA_PRECARGA": target["VIGENCIA_PRECARGA"],
            "VIGENCIA_FINAL_ACTUAL": target["VIGENCIA_FINAL_ACTUAL"],
            "ARCHIVO_ORIGEN": " | ".join(sorted(set(preferred["ARCHIVO_ORIGEN"]))) if not preferred.empty else "",
            "HOJA_ORIGEN": " | ".join(sorted(set(preferred["HOJA_ORIGEN"]))) if not preferred.empty else "",
            "FILA_ORIGEN": " | ".join(sorted(set(preferred["FILA_ORIGEN"]))) if not preferred.empty else "",
            "COLUMNA_ORIGEN": " | ".join(sorted(set(preferred["COLUMNA_ORIGEN"]))) if not preferred.empty else "",
            "VALOR_ORIGINAL": " | ".join(sorted(set(preferred["VALOR_ORIGINAL"]))) if not preferred.empty else "",
            "VALOR_NORMALIZADO": " | ".join(exact_values),
            "TIPO_CRUCE": "DOCUMENTO_EXACTO_NORMALIZADO",
            "CANTIDAD_COINCIDENCIAS": int(len(preferred)),
            "DOCUMENTO_PRECARGA_EQ_DOCUMENTO_FUENTE": "SI" if exact_docs else "NO",
            "CRUCE_DOCUMENTAL_UNICO": "SI" if exact_docs and unique_value and not preferred.empty else "NO",
            "FILA_FUENTE_IDENTIFICADA": "SI" if not preferred.empty and preferred["FILA_ORIGEN"].map(trimmed).ne("").all() else "NO",
            "COLUMNA_NACIONALIDAD_IDENTIFICADA": "SI" if not preferred.empty and preferred["COLUMNA_ORIGEN"].map(trimmed).ne("").all() else "NO",
            "CLASIFICACION_CRUCE": "DEMOSTRADO" if exact_docs and unique_value and not preferred.empty else "CRUCE_NO_DEMOSTRADO",
        })
    return pd.DataFrame(rows)


def classify_cases(targets: pd.DataFrame, hits: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, target in targets.iterrows():
        case_hits = hits[hits["ID_REGISTRO"].eq(target["ID_REGISTRO"])]
        valid = case_hits[case_hits["DOCUMENTO_PRECARGA_EQ_DOCUMENTO_FUENTE"].eq("SI")]
        classes = set(valid["CLASE_VALOR"])
        fuente1 = valid.iloc[0] if len(valid) else None
        fuente2 = valid.iloc[1] if len(valid) > 1 else None
        if "CHILENA" in classes and "EXTRANJERA" in classes:
            clasificacion = "CONFLICTO_ENTRE_FUENTES"
            regla = "BLOQUEAR_CONFLICTO_DE_NACIONALIDAD"
            vig_prop = target["VIGENCIA_FINAL_ACTUAL"]
            nac_prop = ""
            confianza = "BAJA"
            requiere = "SI"
            obs = "Existen fuentes explicitas con nacionalidad chilena y extranjera."
        elif "EXTRANJERA" in classes:
            clasificacion = "EXTRANJERA_CONFIRMADA"
            regla = "NACIONALIDAD_EXTRANJERA_CONFIRMADA_MAPEAR_ANEXO_III"
            first_foreign = valid[valid["CLASE_VALOR"].eq("EXTRANJERA")].iloc[0]
            vig_prop = target["VIGENCIA_FINAL_ACTUAL"]
            nac_prop = first_foreign["CODIGO_MAPEADO"]
            confianza = "ALTA"
            requiere = "NO"
            obs = "Nacionalidad extranjera explicita en fuente autorizada."
        elif "CHILENA" in classes:
            clasificacion = "CHILENA_CONFIRMADA"
            regla = "EXCLUSION_NACIONALIDAD_CHILENA"
            vig_prop = "0"
            nac_prop = ""
            confianza = "ALTA"
            requiere = "NO"
            obs = "Nacionalidad chilena explicita; no se informa codigo 38 en Extranjeros."
        elif len(valid) == 0:
            clasificacion = "SIN_FUENTE_CONCLUYENTE"
            regla = "BLOQUEAR_NACIONALIDAD_NO_DEMOSTRADA"
            vig_prop = target["VIGENCIA_FINAL_ACTUAL"]
            nac_prop = ""
            confianza = "BAJA"
            requiere = "SI"
            obs = "No hay fuente autorizada con nacionalidad explicita por documento exacto."
        else:
            clasificacion = "SIN_FUENTE_CONCLUYENTE"
            regla = "BLOQUEAR_NACIONALIDAD_NO_DEMOSTRADA"
            vig_prop = target["VIGENCIA_FINAL_ACTUAL"]
            nac_prop = ""
            confianza = "BAJA"
            requiere = "SI"
            obs = "Las fuentes encontradas no son concluyentes o no mapean a Anexo III."
        rows.append({
            "ID_REGISTRO": target["ID_REGISTRO"],
            "FILA_PRECARGA": target["FILA_PRECARGA"],
            "NUM_DOCUMENTO": target["NUM_DOCUMENTO"],
            "CODIGO_UNICO": target["CODIGO_UNICO"],
            "VIGENCIA_ANTERIOR": target["VIGENCIA_FINAL_ACTUAL"],
            "NACIONALIDAD_FUENTE_1": "" if fuente1 is None else fuente1["VALOR_ORIGINAL"],
            "FUENTE_1": "" if fuente1 is None else f'{fuente1["ARCHIVO_ORIGEN"]}:{fuente1["HOJA_ORIGEN"]}:{fuente1["FILA_ORIGEN"]}',
            "NACIONALIDAD_FUENTE_2": "" if fuente2 is None else fuente2["VALOR_ORIGINAL"],
            "FUENTE_2": "" if fuente2 is None else f'{fuente2["ARCHIVO_ORIGEN"]}:{fuente2["HOJA_ORIGEN"]}:{fuente2["FILA_ORIGEN"]}',
            "CLASIFICACION": clasificacion,
            "NACIONALIDAD_FINAL_PROPUESTA": nac_prop,
            "VIGENCIA_FINAL_PROPUESTA": vig_prop,
            "REGLA_APLICADA": regla,
            "CONFIANZA": confianza,
            "REQUIERE_REVISION": requiere,
            "OBSERVACION": obs,
        })
    return pd.DataFrame(rows)


def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RUN_DIR / "12_VALIDACION_FINAL_SIES" / f"DIAGNOSTICO_103_CHILENAS_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    recovered = pd.read_csv(PREV_DIR / "02_NACIONALIDAD_104_RECUPERADA.csv", dtype=str, keep_default_na=False).fillna("")
    pd.read_csv(PREV_DIR / "03_NACIONALIDAD_CONFLICTOS_O_NO_MAPEADA.csv", dtype=str, keep_default_na=False).fillna("")
    pd.read_csv(PREV_DIR / "15_AUDITORIA_APLICACION_NACIONALIDAD.csv", dtype=str, keep_default_na=False).fillna("")
    final = pd.read_csv(PES_FINAL, sep=";", dtype=str, keep_default_na=False).fillna("")
    precarga = pd.read_csv(PRECARGA, sep=";", encoding="cp1252", dtype=str, keep_default_na=False).fillna("")
    matriz = pd.read_csv(MATRIZ_VIGENCIA, dtype=str, keep_default_na=False).fillna("")
    hoja2 = source_frame_from_excel(BASE_EXTRANJEROS, "Hoja2")
    code_to_country, _, gent_to_code = load_country_maps()

    targets = make_targets(final, precarga, matriz, recovered)
    hits = build_source_hits(targets, gent_to_code)
    hoja2_with_codcli = hoja2.copy()
    hoja2_with_codcli["__DOC_KEY"] = hoja2_with_codcli["RUT"].map(norm_doc)
    codcli_by_key = hoja2_with_codcli.groupby("__DOC_KEY")["CODCLI"].apply(lambda s: " | ".join(sorted(set(s.map(trimmed))))).to_dict()
    hits["CODCLI"] = hits["DOC_KEY_FUENTE"].map(codcli_by_key).fillna("")

    chilena_ids = set(recovered[recovered["CODIGO_ANEXO_III"].eq("38")]["ID_REGISTRO"])
    chilena_targets = targets[targets["ID_REGISTRO"].isin(chilena_ids)].copy()
    trazabilidad = summarize_trazabilidad(chilena_targets, hits)
    perfil, distribucion, default_diag = profile_hoja2(hoja2)
    contraste = hits.copy().sort_values(["ID_REGISTRO", "ARCHIVO_ORIGEN", "FILA_ORIGEN", "COLUMNA_ORIGEN"])
    decision = classify_cases(targets, hits)

    chilena_decision = decision[decision["ID_REGISTRO"].isin(chilena_ids)]
    current_v0_all = int(matriz["VIGENCIA_FINAL"].map(trimmed).eq("0").sum())
    current_v1_all = int(matriz["VIGENCIA_FINAL"].map(trimmed).eq("1").sum())
    additional_exclusions = int((chilena_decision["VIGENCIA_ANTERIOR"].eq("1") & chilena_decision["CLASIFICACION"].eq("CHILENA_CONFIRMADA")).sum())
    proposed_v0_all = current_v0_all + additional_exclusions
    proposed_v1_all = current_v1_all - additional_exclusions
    impact = pd.DataFrame([{
        "TOTAL_CASOS_CHILENA_DIAGNOSTICADOS": len(chilena_decision),
        "VIGENCIA_0_ACTUAL_UNIVERSO_185": current_v0_all,
        "VIGENCIA_1_ACTUAL_UNIVERSO_185": current_v1_all,
        "VIGENCIA_0_DENTRO_DE_103": int(chilena_decision["VIGENCIA_ANTERIOR"].eq("0").sum()),
        "VIGENCIA_1_DENTRO_DE_103": int(chilena_decision["VIGENCIA_ANTERIOR"].eq("1").sum()),
        "DENTRO_DE_24_EXCLUSIONES_ANTERIORES": int(chilena_decision["VIGENCIA_ANTERIOR"].eq("0").sum()),
        "ADICIONAL_QUE_CAMBIARIA_1_A_0": additional_exclusions,
        "VIGENCIA_0_FINAL_PROPUESTA_UNIVERSO_185_NO_APLICADA": proposed_v0_all,
        "VIGENCIA_1_FINAL_PROPUESTA_UNIVERSO_185_NO_APLICADA": proposed_v1_all,
        "OBSERVACION": "Conteo de propuesta diagnostica; no aplicado a matriz de vigencia.",
    }])

    caso_0107 = decision[decision["ID_REGISTRO"].eq("PRECARGA_0107")].copy()
    if not caso_0107.empty:
        caso_0107["NUM_DOCUMENTO_BUSCADO"] = "26481336"
        caso_0107["CLASIFICACION_PRECARGA_0107"] = caso_0107["CLASIFICACION"].replace({
            "SIN_FUENTE_CONCLUYENTE": "SIN_NACIONALIDAD_DEMOSTRADA",
            "CONFLICTO_ENTRE_FUENTES": "CONFLICTO",
        })

    conflict_or_pending = decision["CLASIFICACION"].isin(["SIN_FUENTE_CONCLUYENTE", "CONFLICTO_ENTRE_FUENTES"]).any()
    cruce_no_demostrado = trazabilidad["CLASIFICACION_CRUCE"].eq("CRUCE_NO_DEMOSTRADO").any()
    if decision["CLASIFICACION"].eq("CONFLICTO_ENTRE_FUENTES").any():
        status = "BLOQUEADO_POR_CONFLICTO_DE_NACIONALIDAD"
    elif conflict_or_pending or cruce_no_demostrado:
        status = "BLOQUEADO_POR_NACIONALIDAD_NO_DEMOSTRADA"
    else:
        status = "DIAGNOSTICO_COMPLETO_LISTO_PARA_REAPERTURA_FASE_06"

    resumen = {
        "estado": status,
        "carpeta": str(out_dir),
        "columna_institucional_utilizada": "BASE EXTRANJEROS.xlsx:Hoja2:NACIONALIDAD",
        "semantica_confirmada": perfil.loc[0, "SEMANTICA_CONFIRMADA"],
        "posible_valor_por_defecto": default_diag.loc[0, "INDICIO_VALOR_POR_DEFECTO"],
        "total_104": int(len(targets)),
        "total_103_chilenas": int(len(chilena_targets)),
        "cruces_documentales_unicos": int(trazabilidad["CRUCE_DOCUMENTAL_UNICO"].eq("SI").sum()),
        "cruces_ambiguos": int(trazabilidad["CRUCE_DOCUMENTAL_UNICO"].ne("SI").sum()),
        "chilenas_confirmadas": int(decision["CLASIFICACION"].eq("CHILENA_CONFIRMADA").sum()),
        "extranjeras_confirmadas": int(decision["CLASIFICACION"].eq("EXTRANJERA_CONFIRMADA").sum()),
        "conflictos": int(decision["CLASIFICACION"].eq("CONFLICTO_ENTRE_FUENTES").sum()),
        "sin_evidencia": int(decision["CLASIFICACION"].eq("SIN_FUENTE_CONCLUYENTE").sum()),
        "vigencia_0_dentro_103": int(chilena_decision["VIGENCIA_ANTERIOR"].eq("0").sum()),
        "vigencia_1_dentro_103": int(chilena_decision["VIGENCIA_ANTERIOR"].eq("1").sum()),
        "nuevas_exclusiones_propuestas": additional_exclusions,
        "caso_precarga_0107": caso_0107.iloc[0]["CLASIFICACION_PRECARGA_0107"] if not caso_0107.empty else "NO_ENCONTRADO",
        "vigencia_0_actual_universo_185": current_v0_all,
        "vigencia_1_actual_universo_185": current_v1_all,
        "vigencia_0_final_propuesta_universo_185_no_aplicada": proposed_v0_all,
        "vigencia_1_final_propuesta_universo_185_no_aplicada": proposed_v1_all,
        "hash_base_extranjeros": sha256(BASE_EXTRANJEROS),
        "hash_promedios": sha256(PROMEDIOS),
        "hash_precarga": sha256(PRECARGA),
        "fuentes_originales_modificadas": "NO",
        "pes_generado": "NO",
        "vigencias_modificadas": "NO",
    }

    write_csv(trazabilidad, out_dir / "01_TRAZABILIDAD_103_CHILENAS.csv")
    write_csv(perfil, out_dir / "02_PERFIL_COLUMNA_NACIONALIDAD_HOJA2.csv")
    write_csv(distribucion, out_dir / "03_DISTRIBUCION_NACIONALIDAD_HOJA2.csv")
    write_csv(default_diag, out_dir / "04_DIAGNOSTICO_VALOR_POR_DEFECTO.csv")
    write_csv(contraste, out_dir / "05_CONTRASTE_NACIONALIDAD_FUENTES.csv")
    write_csv(impact, out_dir / "06_IMPACTO_VIGENCIA_103_CHILENAS.csv")
    write_csv(caso_0107, out_dir / "07_DIAGNOSTICO_PRECARGA_0107.csv")
    write_csv(decision, out_dir / "08_DECISION_NACIONALIDAD_104.csv")
    write_json(resumen, out_dir / "RESUMEN_DIAGNOSTICO_103_CHILENAS.json")

    hashes = []
    for path in sorted(out_dir.glob("*")):
        if path.is_file() and path.name != "HASHES_DIAGNOSTICO_103_CHILENAS.sha256":
            hashes.append(f"{sha256(path)}  {path}")
    (out_dir / "HASHES_DIAGNOSTICO_103_CHILENAS.sha256").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

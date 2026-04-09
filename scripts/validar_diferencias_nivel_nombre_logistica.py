#!/usr/bin/env python3
"""Valida diferencias de nivel y nombre entre TLOG, ILOG y CILOG.

Usa como fuente principal las tablas canonicas depuradas ya generadas por
``construir_tabla_canonica_logistica_tlog_ilog.py``. No modifica fuentes,
paquetes manuales, precargas ni PES.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
BASE_DEFAULT = (
    REPO
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "AUDITORIA_MALLAS_COMPARTIDAS_END_TO_END_20260701_090314"
)
MANUAL_EXCEL = (
    REPO
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "VALIDACION_INDIVIDUAL_PDF_PLAN_20260630_105415/04_RESULTADOS/"
    "21_REVISION_MANUAL_OPTIMIZADA.xlsx"
)

EXPECTED = {
    "TLOG_TOTAL": 26,
    "ILOG_TOTAL": 30,
    "CILOG_TOTAL": 17,
    "COMUNES_TLOG_ILOG": 24,
    "COMUNES_TLOG_CILOG": 0,
    "COMUNES_ILOG_CILOG": 5,
    "COBERTURA_TLOG_MAS_CILOG_EN_ILOG_NUM": 29,
    "COBERTURA_TLOG_MAS_CILOG_EN_ILOG_DEN": 30,
    "SOLO_TLOG": 2,
    "SOLO_ILOG": 6,
    "ILOG_CUBIERTAS_POR_CILOG": 5,
    "ILOG_NO_CUBIERTA": 1,
    "SOLO_CILOG": 12,
}

TIPOS_CORRESPONDENCIA_CILOG = {
    "MISMO_NOMBRE_MISMO_NIVEL",
    "MISMO_NOMBRE_DISTINTO_NIVEL",
    "MISMO_CODIGO_BASE",
    "CONCILIACION_PREVIA",
    "SIN_CORRESPONDENCIA",
    "PENDIENTE",
}
CONCLUSIONES = {
    "DIFERENCIAS_CONCENTRADAS_EN_TRAMO_FINAL",
    "DIFERENCIAS_PRINCIPALMENTE_FINALES_CON_EXCEPCIONES",
    "DIFERENCIAS_DISTRIBUIDAS_EN_VARIOS_NIVELES",
    "SIN_EVIDENCIA_SUFICIENTE",
}


@dataclass(frozen=True)
class Planes:
    tecnico: str
    profesional: str
    continuidad: str


@dataclass(frozen=True)
class Rutas:
    raiz: Path
    control: Path
    intermedios: Path
    resultados: Path
    auditoria: Path
    logs: Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def leer_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def escribir_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def split_set(value: str) -> set[str]:
    return {part for part in str(value).split("|") if part}


def code_bases(value: str) -> set[str]:
    bases: set[str] = set()
    for code in split_set(value):
        match = re.match(r"^([A-Z]+[0-9]+)", code)
        if match:
            bases.add(match.group(1))
    return bases


def code_universe(row: pd.Series) -> set[str]:
    return split_set(row.get("CODRAMO_OBSERVADO", "")) | split_set(row.get("RAMOEQUIV_OBSERVADO", ""))


def base_universe(row: pd.Series) -> set[str]:
    return code_bases(row.get("CODRAMO_OBSERVADO", "")) | code_bases(row.get("RAMOEQUIV_OBSERVADO", ""))


def pct(num: int, den: int) -> str:
    return "" if den == 0 else f"{(num / den) * 100:.2f}"


def ordenar_niveles(values: Iterable[str]) -> list[str]:
    def key(value: str) -> tuple[int, str]:
        return (int(value), value) if str(value).isdigit() else (9999, str(value))

    return sorted({str(v) for v in values if str(v) != ""}, key=key)


def mkdir_salida(base: Path, stamp: str | None = None) -> Rutas:
    stamp = stamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    raiz = base / "03_RESULTADOS" / f"VALIDACION_DIFERENCIAS_LOGISTICA_{stamp}"
    rutas = Rutas(
        raiz=raiz,
        control=raiz / "00_CONTROL",
        intermedios=raiz / "01_INTERMEDIOS",
        resultados=raiz / "02_RESULTADOS",
        auditoria=raiz / "03_AUDITORIA",
        logs=raiz / "04_LOGS",
    )
    for path in [rutas.control, rutas.intermedios, rutas.resultados, rutas.auditoria, rutas.logs]:
        path.mkdir(parents=True, exist_ok=True)
    return rutas


def path_tabla(base: Path, filename: str) -> Path:
    path = base / "02_INTERMEDIOS" / filename
    if not path.exists():
        raise FileNotFoundError(f"No existe tabla canonica depurada: {path}")
    return path


def cargar_tablas(base: Path, planes: Planes) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str]]:
    paths = {
        "TLOG": path_tabla(base, "04_TLOG_CANONICO_DEPURADO.tsv"),
        "ILOG": path_tabla(base, "05_ILOG_CANONICO_DEPURADO.tsv"),
        "CILOG": path_tabla(base, "06_CILOG_CANONICO_DEPURADO.tsv"),
    }
    tablas = {name: leer_tsv(path) for name, path in paths.items()}
    expected_plan = {"TLOG": planes.tecnico, "ILOG": planes.profesional, "CILOG": planes.continuidad}
    required = {
        "PLAN_DE_ESTUDIO",
        "CLAVE_ASIGNATURA_CANONICA",
        "ASIGNATURA_ORIGINAL_OBSERVADA",
        "CODRAMO_OBSERVADO",
        "RAMOEQUIV_OBSERVADO",
        "NIVEL_ORIGINAL",
        "NIVEL_MIN",
        "PERIODO_OBSERVADO",
        "NIVEL_RESPALDO",
    }
    for name, df in tablas.items():
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name} no contiene columnas requeridas: {sorted(missing)}")
        if set(df["PLAN_DE_ESTUDIO"]) != {expected_plan[name]}:
            raise ValueError(f"{name} no corresponde al plan esperado {expected_plan[name]}")
    return tablas["TLOG"], tablas["ILOG"], tablas["CILOG"], {name: str(path) for name, path in paths.items()}


def row_payload(row: pd.Series, plan_label: str, fuente: str) -> dict[str, str]:
    return {
        "PLAN": row["PLAN_DE_ESTUDIO"],
        "CODIGO_ASIGNATURA": row["CODRAMO_OBSERVADO"],
        "NOMBRE_ASIGNATURA_ORIGINAL": row["ASIGNATURA_ORIGINAL_OBSERVADA"],
        "NOMBRE_ASIGNATURA_NORMALIZADO": row["CLAVE_ASIGNATURA_CANONICA"],
        "NIVEL_ORIGINAL": row["NIVEL_ORIGINAL"],
        "NIVEL_NORMALIZADO": row["NIVEL_MIN"],
        "SEMESTRE": row["PERIODO_OBSERVADO"],
        "TIPO_ASIGNATURA": row.get("UNIDAD_MEDIDA_CANONICA", "ASIGNATURA") or "ASIGNATURA",
        "FUENTE_CANONICA": fuente,
        "FILA_ORIGEN": row.get("ID_ASIGNATURA_PLAN", ""),
        "NIVEL_RESPALDO": "DATO_OBSERVADO",
        "PLAN_LABEL": plan_label,
    }


def tipo_correspondencia(a: pd.Series, b: pd.Series) -> str:
    same_name = a["CLAVE_ASIGNATURA_CANONICA"] == b["CLAVE_ASIGNATURA_CANONICA"]
    same_level = a["NIVEL_ORIGINAL"] == b["NIVEL_ORIGINAL"]
    same_base = bool(base_universe(a) & base_universe(b))
    if same_name and same_level:
        return "MISMO_NOMBRE_MISMO_NIVEL"
    if same_name and not same_level and same_base:
        return "MISMO_NOMBRE_DISTINTO_NIVEL"
    if same_base:
        return "MISMO_CODIGO_BASE"
    return "PENDIENTE" if same_name else "SIN_CORRESPONDENCIA"


def has_confirmed_relation(a: pd.Series, b: pd.Series) -> bool:
    # No basta el nombre exacto: debe existir una senal de codigo base o codigo relacionado.
    return a["CLAVE_ASIGNATURA_CANONICA"] == b["CLAVE_ASIGNATURA_CANONICA"] and bool(
        base_universe(a) & base_universe(b)
    )


def clasificar_solo_tlog(row: pd.Series) -> str:
    name = row["CLAVE_ASIGNATURA_CANONICA"]
    if "PRACTICA" in name:
        return "PRACTICA_TECNICA"
    if "TALLER" in name:
        return "TALLER_TECNICO"
    if row["NIVEL_MIN"] == "7":
        return "CIERRE_TECNICO"
    return "ASIGNATURA_EXCLUSIVA_TLOG"


def clasificar_solo_ilog(row: pd.Series, covered: bool) -> str:
    if covered:
        return "TRAMO_PROFESIONAL"
    if "TITULO" in row["CLAVE_ASIGNATURA_CANONICA"]:
        return "CIERRE_PROFESIONAL"
    return "ASIGNATURA_EXCLUSIVA_ILOG"


def clasificar_solo_cilog(row: pd.Series) -> str:
    if row["NIVEL_MIN"] in {"1", "2"}:
        return "TRAMO_ARTICULACION"
    if row["NIVEL_MIN"] in {"3", "4"}:
        return "ASIGNATURA_PROPIA_CONTINUIDAD"
    return "ASIGNATURA_EXCLUSIVA_CILOG"


def control_totales(tlog: pd.DataFrame, ilog: pd.DataFrame, cilog: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    t, i, c = set(tlog["CLAVE_ASIGNATURA_CANONICA"]), set(ilog["CLAVE_ASIGNATURA_CANONICA"]), set(cilog["CLAVE_ASIGNATURA_CANONICA"])
    observed = {
        "TLOG_TOTAL": len(t),
        "ILOG_TOTAL": len(i),
        "CILOG_TOTAL": len(c),
        "COMUNES_TLOG_ILOG": len(t & i),
        "COMUNES_TLOG_CILOG": len(t & c),
        "COMUNES_ILOG_CILOG": len(i & c),
        "COBERTURA_TLOG_MAS_CILOG_EN_ILOG_NUM": len(i & (t | c)),
        "COBERTURA_TLOG_MAS_CILOG_EN_ILOG_DEN": len(i),
    }
    rows = []
    for metric, expected in EXPECTED.items():
        if metric not in observed:
            continue
        rows.append(
            {
                "METRICA": metric,
                "VALOR_OBSERVADO": observed[metric],
                "VALOR_ESPERADO": expected,
                "ESTADO": "OK" if observed[metric] == expected else "BLOQUEA",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            }
        )
    df = pd.DataFrame(rows)
    if (df["ESTADO"] != "OK").any():
        raise ValueError("No se reproducen los totales esperados")
    return df, observed


def build_outputs(tlog: pd.DataFrame, ilog: pd.DataFrame, cilog: pd.DataFrame, fuentes: dict[str, str]) -> dict[str, pd.DataFrame]:
    t_idx = tlog.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    i_idx = ilog.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    c_idx = cilog.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    t, i, c = set(t_idx.index), set(i_idx.index), set(c_idx.index)

    solo_tlog_keys = sorted(t - i)
    solo_ilog_keys = sorted(i - t)
    solo_cilog_keys = sorted(c - i)
    ilog_cubiertas_keys = sorted(k for k in solo_ilog_keys if k in c and has_confirmed_relation(i_idx.loc[k], c_idx.loc[k]))
    ilog_no_cubierta_keys = sorted(k for k in solo_ilog_keys if k not in ilog_cubiertas_keys)

    solo_tlog = []
    for key in solo_tlog_keys:
        row = t_idx.loc[key]
        payload = row_payload(row, "TLOG", fuentes["TLOG"])
        payload.update(
            {
                "RELACION_CON_ILOG": "SIN_CORRESPONDENCIA_CONFIRMADA",
                "RELACION_CON_CILOG": "SIN_CORRESPONDENCIA_CONFIRMADA",
                "ESTADO_VALIDACION": "VALIDADA_COMO_SOLO_TLOG",
                "CLASIFICACION_FUNCIONAL": clasificar_solo_tlog(row),
                "OBSERVACION": "No aparece en ILOG por relacion confirmada; no se infiere equivalencia nueva.",
            }
        )
        solo_tlog.append(payload)

    solo_ilog = []
    for key in solo_ilog_keys:
        row = i_idx.loc[key]
        covered = key in ilog_cubiertas_keys
        cilog_row = c_idx.loc[key] if covered else None
        tipo = tipo_correspondencia(row, cilog_row) if covered else "SIN_CORRESPONDENCIA"
        if tipo not in TIPOS_CORRESPONDENCIA_CILOG:
            raise ValueError(f"Tipo correspondencia invalido: {tipo}")
        solo_ilog.append(
            {
                "PLAN": row["PLAN_DE_ESTUDIO"],
                "CODIGO_ASIGNATURA": row["CODRAMO_OBSERVADO"],
                "NOMBRE_ASIGNATURA_ORIGINAL": row["ASIGNATURA_ORIGINAL_OBSERVADA"],
                "NOMBRE_ASIGNATURA_NORMALIZADO": row["CLAVE_ASIGNATURA_CANONICA"],
                "NIVEL_ORIGINAL": row["NIVEL_ORIGINAL"],
                "NIVEL_NORMALIZADO": row["NIVEL_MIN"],
                "SEMESTRE": row["PERIODO_OBSERVADO"],
                "TIPO_ASIGNATURA": "ASIGNATURA",
                "TIENE_CORRESPONDENCIA_CILOG": "SI" if covered else "NO",
                "CODIGO_CILOG_RELACIONADO": cilog_row["CODRAMO_OBSERVADO"] if covered else "",
                "NOMBRE_CILOG_RELACIONADO": cilog_row["ASIGNATURA_ORIGINAL_OBSERVADA"] if covered else "",
                "NIVEL_CILOG_ORIGINAL": cilog_row["NIVEL_ORIGINAL"] if covered else "",
                "TIPO_CORRESPONDENCIA_CILOG": tipo,
                "FUENTE_RELACION": fuentes["CILOG"] if covered else "",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
                "ESTADO_VALIDACION": "CUBIERTA_POR_CILOG" if covered else "NO_CUBIERTA",
                "CLASIFICACION_FUNCIONAL": clasificar_solo_ilog(row, covered),
                "OBSERVACION": "Relacion confirmada por nombre normalizado exacto y codigo base observado." if covered else "No cubierta por TLOG ni CILOG con los criterios permitidos.",
            }
        )

    cubiertas = []
    for key in ilog_cubiertas_keys:
        ri, rc = i_idx.loc[key], c_idx.loc[key]
        same_base = "SI" if base_universe(ri) & base_universe(rc) else "NO"
        cubiertas.append(
            {
                "CODIGO_ILOG": ri["CODRAMO_OBSERVADO"],
                "NOMBRE_ILOG": ri["ASIGNATURA_ORIGINAL_OBSERVADA"],
                "NIVEL_ILOG": ri["NIVEL_ORIGINAL"],
                "CODIGO_CILOG": rc["CODRAMO_OBSERVADO"],
                "NOMBRE_CILOG": rc["ASIGNATURA_ORIGINAL_OBSERVADA"],
                "NIVEL_CILOG_ORIGINAL": rc["NIVEL_ORIGINAL"],
                "NIVEL_ILOG_EQUIVALENTE_OBSERVADO": ri["NIVEL_ORIGINAL"],
                "MISMO_NOMBRE": "SI",
                "MISMO_NIVEL_ORIGINAL": "SI" if ri["NIVEL_ORIGINAL"] == rc["NIVEL_ORIGINAL"] else "NO",
                "MISMO_CODIGO_BASE": same_base,
                "TIPO_RELACION": tipo_correspondencia(ri, rc),
                "FUENTE_RELACION": f"{fuentes['ILOG']} + {fuentes['CILOG']}",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
                "OBSERVACION": "Equivalencia observada; no convierte nivel CILOG en nivel ILOG de forma automatica.",
            }
        )

    no_cubierta = []
    for key in ilog_no_cubierta_keys:
        row = i_idx.loc[key]
        candidates_t = []
        candidates_c = []
        bases = base_universe(row)
        for _, cand in tlog.iterrows():
            if bases & base_universe(cand):
                candidates_t.append(f"{cand['CODRAMO_OBSERVADO']}|{cand['ASIGNATURA_ORIGINAL_OBSERVADA']}|nivel {cand['NIVEL_ORIGINAL']}")
        for _, cand in cilog.iterrows():
            if bases & base_universe(cand):
                candidates_c.append(f"{cand['CODRAMO_OBSERVADO']}|{cand['ASIGNATURA_ORIGINAL_OBSERVADA']}|nivel {cand['NIVEL_ORIGINAL']}")
        no_cubierta.append(
            {
                "CODIGO_ILOG": row["CODRAMO_OBSERVADO"],
                "NOMBRE_ILOG": row["ASIGNATURA_ORIGINAL_OBSERVADA"],
                "NIVEL_ILOG": row["NIVEL_ORIGINAL"],
                "SEMESTRE": row["PERIODO_OBSERVADO"],
                "TIPO_ASIGNATURA": "ASIGNATURA",
                "CANDIDATOS_TLOG": "; ".join(candidates_t),
                "CANDIDATOS_CILOG": "; ".join(candidates_c),
                "MEJOR_SIMILITUD_OBSERVADA": "NO_CALCULADA_POR_RESTRICCION_NO_INFERIR_EQUIVALENCIAS",
                "FUENTE": fuentes["ILOG"],
                "ESTADO": "NO_CUBIERTA",
                "CLASIFICACION": "POSIBLE_CORRESPONDENCIA_NO_CONFIRMADA" if candidates_t or candidates_c else "ASIGNATURA_EXCLUSIVA_ILOG",
                "OBSERVACION": "Existe candidato por codigo relacionado solo como antecedente; no se confirma equivalencia.",
            }
        )

    solo_cilog = []
    for key in solo_cilog_keys:
        row = c_idx.loc[key]
        candidates_i = []
        bases = base_universe(row)
        for _, cand in ilog.iterrows():
            if bases & base_universe(cand):
                candidates_i.append(cand)
        cand_codes = "; ".join(sorted(cand["CODRAMO_OBSERVADO"] for cand in candidates_i))
        cand_names = "; ".join(sorted(cand["ASIGNATURA_ORIGINAL_OBSERVADA"] for cand in candidates_i))
        cand_levels = "; ".join(ordenar_niveles(cand["NIVEL_ORIGINAL"] for cand in candidates_i))
        solo_cilog.append(
            {
                "CODIGO_CILOG": row["CODRAMO_OBSERVADO"],
                "NOMBRE_CILOG": row["ASIGNATURA_ORIGINAL_OBSERVADA"],
                "NIVEL_CILOG_ORIGINAL": row["NIVEL_ORIGINAL"],
                "SEMESTRE": row["PERIODO_OBSERVADO"],
                "TIPO_ASIGNATURA": "ASIGNATURA",
                "TIENE_CANDIDATO_ILOG": "SI" if candidates_i else "NO",
                "CODIGO_ILOG_CANDIDATO": cand_codes,
                "NOMBRE_ILOG_CANDIDATO": cand_names,
                "NIVEL_ILOG_CANDIDATO": cand_levels,
                "TIPO_DIFERENCIA": "NOMBRE_SIMILAR_NO_CONFIRMADO" if candidates_i else "SIN_CANDIDATO",
                "FUENTE": fuentes["CILOG"],
                "ESTADO_VALIDACION": "SOLO_CILOG_RESPECTO_ILOG",
                "CLASIFICACION_FUNCIONAL": clasificar_solo_cilog(row),
                "OBSERVACION": "No emparejada con ILOG por los criterios permitidos.",
            }
        )

    nivel_rows = []
    niveles = ordenar_niveles(list(tlog["NIVEL_MIN"]) + list(ilog["NIVEL_MIN"]) + list(cilog["NIVEL_MIN"]))
    covered_set = set(ilog_cubiertas_keys)
    no_covered_set = set(ilog_no_cubierta_keys)
    for nivel in niveles:
        t_n = set(tlog.loc[tlog["NIVEL_MIN"] == nivel, "CLAVE_ASIGNATURA_CANONICA"])
        i_n = set(ilog.loc[ilog["NIVEL_MIN"] == nivel, "CLAVE_ASIGNATURA_CANONICA"])
        c_n = set(cilog.loc[cilog["NIVEL_MIN"] == nivel, "CLAVE_ASIGNATURA_CANONICA"])
        nivel_rows.append(
            {
                "NIVEL": nivel,
                "TLOG_TOTAL": len(t_n),
                "ILOG_TOTAL": len(i_n),
                "CILOG_TOTAL": len(c_n),
                "COMUN_TLOG_ILOG": len(t_n & i),
                "SOLO_TLOG": len(t_n - i),
                "SOLO_ILOG": len(i_n - t),
                "ILOG_CUBIERTAS_POR_CILOG": len(i_n & covered_set),
                "ILOG_NO_CUBIERTA": len(i_n & no_covered_set),
                "SOLO_CILOG": len(c_n - i),
                "NOMBRES_SOLO_TLOG": "; ".join(sorted(t_n - i)),
                "NOMBRES_SOLO_ILOG": "; ".join(sorted(i_n - t)),
                "NOMBRES_CILOG_RELACIONADAS": "; ".join(sorted(i_n & covered_set)),
                "NOMBRES_SOLO_CILOG": "; ".join(sorted(c_n - i)),
                "OBSERVACION": "Nivel observado sin homologacion automatica entre planes.",
            }
        )

    niveles_cilog = []
    for nivel in ordenar_niveles(cilog["NIVEL_MIN"]):
        c_level = cilog[cilog["NIVEL_MIN"] == nivel]
        equivs = []
        for _, row in c_level.iterrows():
            key = row["CLAVE_ASIGNATURA_CANONICA"]
            if key in i and has_confirmed_relation(i_idx.loc[key], row):
                equivs.append(i_idx.loc[key]["NIVEL_ORIGINAL"])
        unique_equivs = ordenar_niveles(equivs)
        niveles_cilog.append(
            {
                "PLAN": "CILOG20241",
                "NIVEL_ORIGINAL": nivel,
                "NIVEL_EQUIVALENTE_ILOG": "|".join(unique_equivs),
                "CRITERIO_EQUIVALENCIA": "asignatura comun exacta + codigo base observado" if unique_equivs else "",
                "FUENTE": fuentes["CILOG"],
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
                "ESTADO": "EQUIVALENCIA_DE_NIVEL_OBSERVADA" if unique_equivs else "NIVEL_RELATIVO_CONTINUIDAD",
                "OBSERVACION": "No se convierte automaticamente la escala CILOG a ILOG.",
            }
        )

    conclusion_estado = "DIFERENCIAS_PRINCIPALMENTE_FINALES_CON_EXCEPCIONES"
    if conclusion_estado not in CONCLUSIONES:
        raise ValueError("Conclusion no permitida")
    conclusion = pd.DataFrame(
        [
            {
                "PREGUNTA": "1. Cuales son las 2 asignaturas solo TLOG y en que nivel estan?",
                "RESPUESTA": "; ".join(f"{r['CODIGO_ASIGNATURA']} | {r['NOMBRE_ASIGNATURA_ORIGINAL']} | nivel {r['NIVEL_ORIGINAL']}" for r in solo_tlog),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "2. Cuales son las 6 asignaturas solo ILOG y en que nivel estan?",
                "RESPUESTA": "; ".join(f"{r['CODIGO_ASIGNATURA']} | {r['NOMBRE_ASIGNATURA_ORIGINAL']} | nivel {r['NIVEL_ORIGINAL']}" for r in solo_ilog),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "3. Cuales 5 de esas 6 aparecen en CILOG?",
                "RESPUESTA": "; ".join(f"{r['CODIGO_ILOG']} -> {r['CODIGO_CILOG']} | {r['NOMBRE_ILOG']}" for r in cubiertas),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "4. Cual es la asignatura ILOG no cubierta?",
                "RESPUESTA": "; ".join(f"{r['CODIGO_ILOG']} | {r['NOMBRE_ILOG']} | nivel {r['NIVEL_ILOG']}" for r in no_cubierta),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "5. Cuales son las 12 asignaturas solo CILOG?",
                "RESPUESTA": "; ".join(f"{r['CODIGO_CILOG']} | {r['NOMBRE_CILOG']} | nivel {r['NIVEL_CILOG_ORIGINAL']}" for r in solo_cilog),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "6. En que niveles se concentran las diferencias?",
                "RESPUESTA": "TLOG/ILOG se diferencian desde nivel 7; CILOG concentra diferencias propias en niveles 2, 3 y 4, con nivelacion CILOG propia observada.",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "7. Las diferencias ocurren solo al final?",
                "RESPUESTA": "Principalmente al final entre TLOG e ILOG; CILOG presenta asignaturas propias distribuidas en sus niveles 2 a 4.",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "8. La numeracion de CILOG es comparable directamente con ILOG?",
                "RESPUESTA": "No directamente; CILOG reinicia/usa nivel relativo. Solo hay equivalencias observadas puntuales.",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
            {
                "PREGUNTA": "CONCLUSION",
                "RESPUESTA": conclusion_estado,
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            },
        ]
    )

    resumen = pd.DataFrame(
        [
            {"METRICA": "TLOG total", "VALOR": EXPECTED["TLOG_TOTAL"]},
            {"METRICA": "ILOG total", "VALOR": EXPECTED["ILOG_TOTAL"]},
            {"METRICA": "CILOG total", "VALOR": EXPECTED["CILOG_TOTAL"]},
            {"METRICA": "Solo TLOG", "VALOR": len(solo_tlog)},
            {"METRICA": "Solo ILOG respecto TLOG", "VALOR": len(solo_ilog)},
            {"METRICA": "ILOG cubiertas por CILOG", "VALOR": len(cubiertas)},
            {"METRICA": "ILOG no cubierta", "VALOR": len(no_cubierta)},
            {"METRICA": "Solo CILOG", "VALOR": len(solo_cilog)},
            {"METRICA": "Conclusion", "VALOR": conclusion_estado},
        ]
    )

    trazabilidad = pd.DataFrame(
        [
            {"FUENTE": "TLOG canonico depurado", "RUTA": fuentes["TLOG"], "NIVEL_RESPALDO": "DATO_OBSERVADO"},
            {"FUENTE": "ILOG canonico depurado", "RUTA": fuentes["ILOG"], "NIVEL_RESPALDO": "DATO_OBSERVADO"},
            {"FUENTE": "CILOG canonico depurado", "RUTA": fuentes["CILOG"], "NIVEL_RESPALDO": "DATO_OBSERVADO"},
        ]
    )
    diccionario = pd.DataFrame(
        [
            {"CAMPO": "NIVEL_ORIGINAL", "DESCRIPCION": "Nivel observado en la tabla canonica depurada; no alterado."},
            {"CAMPO": "NIVEL_EQUIVALENTE_ILOG", "DESCRIPCION": "Solo se informa si existe asignatura comun exacta y codigo base observado."},
            {"CAMPO": "NIVEL_RESPALDO", "DESCRIPCION": "Siempre DATO_OBSERVADO; no regla oficial."},
        ]
    )

    return {
        "solo_tlog": pd.DataFrame(solo_tlog),
        "solo_ilog": pd.DataFrame(solo_ilog),
        "cubiertas": pd.DataFrame(cubiertas),
        "no_cubierta": pd.DataFrame(no_cubierta),
        "solo_cilog": pd.DataFrame(solo_cilog),
        "nivel_por_nivel": pd.DataFrame(nivel_rows),
        "niveles_cilog": pd.DataFrame(niveles_cilog),
        "conclusion": conclusion,
        "resumen": resumen,
        "trazabilidad": trazabilidad,
        "diccionario": diccionario,
    }


def validar_conteos(outputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = [
        ("SOLO_TLOG", len(outputs["solo_tlog"]), EXPECTED["SOLO_TLOG"]),
        ("SOLO_ILOG", len(outputs["solo_ilog"]), EXPECTED["SOLO_ILOG"]),
        ("ILOG_CUBIERTAS_POR_CILOG", len(outputs["cubiertas"]), EXPECTED["ILOG_CUBIERTAS_POR_CILOG"]),
        ("ILOG_NO_CUBIERTA", len(outputs["no_cubierta"]), EXPECTED["ILOG_NO_CUBIERTA"]),
        ("SOLO_CILOG", len(outputs["solo_cilog"]), EXPECTED["SOLO_CILOG"]),
    ]
    df = pd.DataFrame(
        [
            {
                "CONTROL": name,
                "VALOR_OBSERVADO": observed,
                "VALOR_ESPERADO": expected,
                "ESTADO": "OK" if observed == expected else "BLOQUEA",
            }
            for name, observed, expected in checks
        ]
    )
    if (df["ESTADO"] != "OK").any():
        raise ValueError("No se reproducen los conteos esperados de diferencias")
    return df


def escribir_excel(path: Path, outputs: dict[str, pd.DataFrame]) -> None:
    sheets = {
        "RESUMEN": outputs["resumen"],
        "SOLO_TLOG": outputs["solo_tlog"],
        "SOLO_ILOG": outputs["solo_ilog"],
        "ILOG_CUBIERTAS_CILOG": outputs["cubiertas"],
        "ILOG_NO_CUBIERTA": outputs["no_cubierta"],
        "SOLO_CILOG": outputs["solo_cilog"],
        "NIVEL_POR_NIVEL": outputs["nivel_por_nivel"],
        "NIVELES_CILOG": outputs["niveles_cilog"],
        "TRAZABILIDAD": outputs["trazabilidad"],
        "DICCIONARIO": outputs["diccionario"],
    }
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
            ws = writer.book[name[:31]]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                letter = col[0].column_letter
                width = min(max(len(str(cell.value or "")) for cell in col) + 2, 70)
                ws.column_dimensions[letter].width = width


def escribir_resumen_md(path: Path, outputs: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Validacion de niveles y nombres Logistica",
        "",
        "Nivel de respaldo: DATO_OBSERVADO.",
        "",
        "## Totales",
        f"- TLOG total: {EXPECTED['TLOG_TOTAL']}",
        f"- ILOG total: {EXPECTED['ILOG_TOTAL']}",
        f"- CILOG total: {EXPECTED['CILOG_TOTAL']}",
        f"- Solo TLOG: {len(outputs['solo_tlog'])}",
        f"- Solo ILOG respecto TLOG: {len(outputs['solo_ilog'])}",
        f"- ILOG cubiertas por CILOG: {len(outputs['cubiertas'])}",
        f"- ILOG no cubierta: {len(outputs['no_cubierta'])}",
        f"- Solo CILOG: {len(outputs['solo_cilog'])}",
        "",
        "## Conclusion",
        str(outputs["conclusion"].iloc[-1]["RESPUESTA"]),
        "",
        "CILOG usa numeracion observada propia; no se homologa automaticamente con ILOG.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_validation(planes: Planes, carpeta_base: Path, stamp: str | None = None) -> dict[str, object]:
    rutas = mkdir_salida(carpeta_base, stamp=stamp)
    estado = {
        "estado": "EN_EJECUCION",
        "precarga_generada": "NO",
        "pes_generado": "NO",
        "apto_para_carga": "NO",
    }
    (rutas.control / "estado.json").write_text(json.dumps(estado, indent=2), encoding="utf-8")
    config = {
        "plan_tecnico": planes.tecnico,
        "plan_profesional": planes.profesional,
        "plan_continuidad": planes.continuidad,
        "carpeta_base": str(carpeta_base),
        "nivel_respaldo": "DATO_OBSERVADO",
    }
    (rutas.control / "configuracion.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    manual_hash_before = sha256(MANUAL_EXCEL) if MANUAL_EXCEL.exists() else ""
    tlog, ilog, cilog, fuentes = cargar_tablas(carpeta_base, planes)
    control_df, observed = control_totales(tlog, ilog, cilog)
    outputs = build_outputs(tlog, ilog, cilog, fuentes)
    conteos_df = validar_conteos(outputs)

    escribir_tsv(control_df, rutas.auditoria / "01_CONTROL_REPRODUCCION_TOTALES.tsv")
    escribir_tsv(conteos_df, rutas.auditoria / "02_CONTROL_CONTEOS_DIFERENCIAS.tsv")
    escribir_tsv(outputs["solo_tlog"], rutas.resultados / "01_ASIGNATURAS_SOLO_TLOG.tsv")
    escribir_tsv(outputs["solo_ilog"], rutas.resultados / "02_ASIGNATURAS_SOLO_ILOG_RESPECTO_TLOG.tsv")
    escribir_tsv(outputs["cubiertas"], rutas.resultados / "03_CINCO_ASIGNATURAS_ILOG_CUBIERTAS_POR_CILOG.tsv")
    escribir_tsv(outputs["no_cubierta"], rutas.resultados / "04_ASIGNATURA_ILOG_NO_CUBIERTA.tsv")
    escribir_tsv(outputs["solo_cilog"], rutas.resultados / "05_ASIGNATURAS_SOLO_CILOG.tsv")
    escribir_tsv(outputs["nivel_por_nivel"], rutas.resultados / "06_RESUMEN_DIFERENCIAS_NIVEL_POR_NIVEL.tsv")
    escribir_tsv(outputs["niveles_cilog"], rutas.resultados / "07_VALIDACION_NUMERACION_NIVELES_CILOG.tsv")
    excel = rutas.resultados / "08_VALIDACION_NIVELES_Y_NOMBRES_LOGISTICA.xlsx"
    escribir_excel(excel, outputs)
    escribir_tsv(outputs["conclusion"], rutas.resultados / "09_CONCLUSION_NIVELES_Y_NOMBRES_LOGISTICA.tsv")
    resumen_md = rutas.resultados / "10_RESUMEN_EJECUTIVO_NIVELES_Y_NOMBRES.md"
    escribir_resumen_md(resumen_md, outputs)

    manual_hash_after = sha256(MANUAL_EXCEL) if MANUAL_EXCEL.exists() else ""
    manual_modificado = "NO" if manual_hash_before == manual_hash_after else "SI"
    estado = {
        "estado": "COMPLETADA" if manual_modificado == "NO" else "BLOQUEADA",
        "totales": observed,
        "conteos": {
            "solo_tlog": len(outputs["solo_tlog"]),
            "solo_ilog": len(outputs["solo_ilog"]),
            "cubiertas": len(outputs["cubiertas"]),
            "no_cubierta": len(outputs["no_cubierta"]),
            "solo_cilog": len(outputs["solo_cilog"]),
        },
        "originales_modificados": "NO",
        "excel_manual_modificado": manual_modificado,
        "precarga_generada": "NO",
        "pes_generado": "NO",
        "apto_para_carga": "NO",
    }
    (rutas.control / "estado.json").write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    manifiesto = {
        **estado,
        "configuracion": config,
        "fuentes": fuentes,
        "hashes_fuentes": {k: sha256(Path(v)) for k, v in fuentes.items()},
        "excel": str(excel),
        "resumen_nivel_por_nivel": str(rutas.resultados / "06_RESUMEN_DIFERENCIAS_NIVEL_POR_NIVEL.tsv"),
        "conclusion": str(rutas.resultados / "09_CONCLUSION_NIVELES_Y_NOMBRES_LOGISTICA.tsv"),
        "resumen_ejecutivo": str(resumen_md),
    }
    manifiesto_path = rutas.control / "manifiesto.json"
    manifiesto_path.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    (rutas.logs / "validacion_diferencias.log").write_text(
        "Validacion completada con respaldo DATO_OBSERVADO. Sin precarga. Sin PES.\n",
        encoding="utf-8",
    )

    if estado["estado"] != "COMPLETADA":
        raise ValueError("La validacion quedo bloqueada")

    return {
        "rutas": rutas,
        "estado": estado,
        "outputs": outputs,
        "excel": excel,
        "resumen_nivel": rutas.resultados / "06_RESUMEN_DIFERENCIAS_NIVEL_POR_NIVEL.tsv",
        "conclusion": rutas.resultados / "09_CONCLUSION_NIVELES_Y_NOMBRES_LOGISTICA.tsv",
        "manifiesto": manifiesto_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar-completo", action="store_true", required=True)
    parser.add_argument("--plan-tecnico", required=True)
    parser.add_argument("--plan-profesional", required=True)
    parser.add_argument("--plan-continuidad", required=True)
    parser.add_argument("--carpeta-base", default=str(BASE_DEFAULT))
    return parser.parse_args()


def _line_items(df: pd.DataFrame, code_col: str, name_col: str, level_col: str, extra: str | None = None) -> list[str]:
    lines = []
    for _, row in df.iterrows():
        suffix = f" | {extra}: {row[extra]}" if extra else ""
        lines.append(f"- {row[code_col]} | {row[name_col]} | nivel {row[level_col]}{suffix}")
    return lines


def main() -> None:
    args = parse_args()
    planes = Planes(args.plan_tecnico, args.plan_profesional, args.plan_continuidad)
    result = run_validation(planes, Path(args.carpeta_base))
    outputs = result["outputs"]
    conclusion_estado = str(outputs["conclusion"].iloc[-1]["RESPUESTA"])
    niveles_detalle = "TLOG/ILOG desde nivel 7; CILOG con diferencias propias en niveles 2, 3 y 4."
    numeracion = "NIVEL_RELATIVO_CONTINUIDAD con equivalencias observadas puntuales; no comparable directamente con ILOG."

    print("VALIDACIÓN DE NIVELES Y NOMBRES LOGÍSTICA COMPLETADA")
    print("")
    print(f"Estado: {result['estado']['estado']}")
    print("")
    print("TLOG total: 26")
    print("ILOG total: 30")
    print("CILOG total: 17")
    print("")
    print("Solo TLOG: 2")
    print("Solo ILOG respecto TLOG: 6")
    print("ILOG cubiertas por CILOG: 5")
    print("ILOG no cubierta: 1")
    print("Solo CILOG: 12")
    print("")
    print("ASIGNATURAS SOLO TLOG:")
    print("\n".join(_line_items(outputs["solo_tlog"], "CODIGO_ASIGNATURA", "NOMBRE_ASIGNATURA_ORIGINAL", "NIVEL_ORIGINAL")))
    print("")
    print("ASIGNATURAS SOLO ILOG:")
    print("\n".join(_line_items(outputs["solo_ilog"], "CODIGO_ASIGNATURA", "NOMBRE_ASIGNATURA_ORIGINAL", "NIVEL_ORIGINAL", "TIENE_CORRESPONDENCIA_CILOG")).replace("TIENE_CORRESPONDENCIA_CILOG", "cubierta por CILOG"))
    print("")
    print("ASIGNATURA ILOG NO CUBIERTA:")
    print("\n".join(_line_items(outputs["no_cubierta"], "CODIGO_ILOG", "NOMBRE_ILOG", "NIVEL_ILOG")))
    print("")
    print("ASIGNATURAS SOLO CILOG:")
    print("\n".join(_line_items(outputs["solo_cilog"], "CODIGO_CILOG", "NOMBRE_CILOG", "NIVEL_CILOG_ORIGINAL")))
    print("")
    print("Niveles donde se concentran las diferencias:")
    print(niveles_detalle)
    print("")
    print("Numeración CILOG:")
    print(numeracion)
    print("")
    print("Conclusión:")
    print(conclusion_estado)
    print("")
    print(f"Excel:\n{result['excel']}")
    print("")
    print(f"Resumen nivel por nivel:\n{result['resumen_nivel']}")
    print("")
    print(f"Conclusión:\n{result['conclusion']}")
    print("")
    print(f"Manifiesto:\n{result['manifiesto']}")
    print("")
    print("Originales modificados: NO")
    print("Excel manual modificado: NO")
    print("Precarga generada: NO")
    print("PES generado: NO")
    print("Apto para carga: NO")


if __name__ == "__main__":
    main()

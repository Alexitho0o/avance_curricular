"""Primer ingreso institucional 2027 a partir del histórico completo de matrícula.

Este módulo no modifica matrícula, tokens ni respuestas. Clasifica las filas del
período conservando sus índices para que ambos caminos operativos apliquen la
misma decisión antes de construir el universo de caracterización.
"""
from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path
import re

import pandas as pd

from caracterizacion_universo import normalizar_programa

ROOT = Path(__file__).resolve().parent
POLICY = "PRIMER_INGRESO_INSTITUCIONAL_2027-v1"


def _column_key(value):
    return re.sub(r"[^A-Z0-9]", "", normalizar_programa(value))


@lru_cache(maxsize=1)
def _governed_rules():
    """Extrae helpers puros y diccionario vigentes sin ejecutar el código 2026."""
    reference = ROOT / "caracterizacion.py"
    tree = ast.parse(reference.read_text(encoding="utf-8"))
    names = {"_clean_str", "token_match_rut", "_norm_estado_oficial",
             "_clasificar_estado_oficial", "_evento_academico_oficial"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    context = {"pd": pd, "re": re}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "_MAPA_ESTADO_OFICIAL" for t in node.targets
        ):
            context["_MAPA_ESTADO_OFICIAL"] = ast.literal_eval(node.value)
    if {n.name for n in nodes} != names or "_MAPA_ESTADO_OFICIAL" not in context:
        raise ValueError("No se encontraron las reglas gobernadas de trayectoria institucional.")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(reference), "exec"), context)
    return context


@lru_cache(maxsize=1)
def _career_aliases():
    """Equivalencias explícitas del mismo snapshot que usa el bloque trayectorias."""
    path = ROOT / "gobernanza/sies/DURACION_ESTUDIOS.tsv"
    if not path.is_file():
        raise ValueError("No existe el catálogo gobernado de equivalencias CODCARPR.")
    catalog = pd.read_csv(path, sep="\t", dtype=str, encoding="utf-8-sig").fillna("")
    required = {"CODCARPR_CANONICO", "CODCARPR_ALIAS_LIST"}
    if not required.issubset(catalog.columns):
        raise ValueError("Faltan columnas del catálogo gobernado de equivalencias CODCARPR.")
    aliases = {}
    for _, row in catalog.iterrows():
        canonical = normalizar_programa(row.CODCARPR_CANONICO)
        if not canonical:
            continue
        codes = [canonical] + row.CODCARPR_ALIAS_LIST.split("|")
        for code in codes:
            code = normalizar_programa(code)
            if code:
                aliases.setdefault(code, set()).add(canonical)
    return aliases


def _academic_state(estado, situacion, rules):
    # El catálogo documental IPSS V001, tabla 4, y la etiqueta observada en
    # DATOSDEALUMNOS corroboran 101/VIGENTE como título intermedio 2. El mapa
    # histórico congelado omite esta combinación; se añade SOLO aquí, con
    # código y etiqueta concordantes, sin cambiar sus helpers ni inferir otros
    # estados por analogía. 101/ELIMINADO conserva su clasificación original.
    if (normalizar_programa(estado) == "VIGENTE" and
            normalizar_programa(situacion) == "101 TITULO INTERMEDIO 2"):
        return "SALIDA_INTERMEDIA"
    category = rules["_clasificar_estado_oficial"](situacion, estado)
    event = rules["_evento_academico_oficial"](situacion, category)
    if category == "TITULADO":
        return "TITULADO"
    if category == "VIGENTE":
        return "SALIDA_INTERMEDIA" if event == "TITULACION_INTERMEDIA" else "VIGENTE"
    return "POR_REVISAR" if category == "POR_REVISAR" else "NO_AUTORIZADO"


def _career_relation(current, peer, aliases):
    code, other = current["_CODCARPR"], peer["_CODCARPR"]
    if not code or not other:
        return "POR_REVISAR"
    if code == other:
        return "MISMA_CARRERA"
    canonical, other_canonical = aliases.get(code, set()), aliases.get(other, set())
    if len(canonical) > 1 or len(other_canonical) > 1:
        return "POR_REVISAR"
    if canonical & other_canonical:
        return "MISMA_CARRERA"
    name, other_name = current["_NOMBREL"], peer["_NOMBREL"]
    if not name or not other_name:
        return "POR_REVISAR"
    # Los códigos pueden cambiar por plan/jornada. Un código distinto por sí
    # solo no demuestra otra carrera; también se exige nombre distinto.
    return "MISMA_CARRERA" if name == other_name else "OTRA_CARRERA"


def _temporal_relation(current, peer):
    """Fecha de matrícula no equivale a fecha de primer ingreso académico."""
    year, other_year = current["_ANOINGRESO"], peer["_ANOINGRESO"]
    if pd.isna(year) or pd.isna(other_year):
        return "POR_REVISAR"
    if other_year < year:
        return "ANTERIOR"
    if other_year > year:
        return "POSTERIOR"
    period, other_period = current["_PERIODOINGRESO"], peer["_PERIODOINGRESO"]
    if pd.isna(period) or pd.isna(other_period):
        return "POR_REVISAR"
    if other_period < period:
        return "ANTERIOR"
    if other_period > period:
        return "POSTERIOR"
    # Dos nuevas matrículas en la misma cohorte no crean una trayectoria previa
    # porque una fue cargada días antes. Se conserva el caso para revisión.
    return "MISMA_COHORTE"


def classify_trajectories(matricula: pd.DataFrame, year=2027, period=1):
    """Devuelve (detalle del período, resumen agregado, evidencia individual).

    Se debe recibir DATOSDEALUMNOS completo, no una cohorte ya filtrada. El
    detalle conserva todas las filas del período y su índice original. Solo se
    excluyen antecedentes de otra carrera, de ingreso académico estrictamente
    anterior y con combinación estado/situación gobernada titulada, vigente o
    de salida intermedia. Otros estados y casos ambiguos quedan visibles sin
    inventar una exclusión. Los duplicados técnicos no crean antecedentes.

    La evidencia contiene identificadores: guardar únicamente en rutas privadas
    ignoradas por Git o en el análisis privado de la ejecución.
    """
    if int(year) != 2027 or int(period) not in (1, 2, 3):
        raise ValueError("La política de primer ingreso institucional es exclusiva de 2027.")
    if not isinstance(matricula, pd.DataFrame):
        raise TypeError("matricula debe ser el DataFrame histórico completo.")
    if not matricula.index.is_unique:
        raise ValueError("El índice de matrícula debe ser único para conservar la trazabilidad.")
    columns = {}
    for column in matricula.columns:
        key = _column_key(column)
        if key in columns:
            raise ValueError("Columnas de matrícula ambiguas por nombre normalizado: " + key)
        columns[key] = column
    required = {"RUT", "CODCLI", "CODCARPR", "NOMBREL", "ANOMATRICULA",
                "PERIODOMATRICULA", "ANOINGRESO", "PERIODOINGRESO",
                "ESTADOACADEMICO", "SITUACION"}
    if required - columns.keys():
        raise ValueError("Faltan columnas de trayectoria institucional: " + ", ".join(sorted(required - columns.keys())))
    rules, aliases = _governed_rules(), _career_aliases()
    frame = matricula.copy()
    frame["TOKEN"] = frame[columns["RUT"]].map(rules["token_match_rut"])
    for key in ["ANOMATRICULA", "PERIODOMATRICULA", "ANOINGRESO", "PERIODOINGRESO"]:
        frame["_" + key] = pd.to_numeric(frame[columns[key]], errors="coerce")
    for key in ["CODCARPR", "NOMBREL", "CODCLI"]:
        frame["_" + key] = frame[columns[key]].map(normalizar_programa)
    frame["_ESTADO_TRAYECTORIA"] = [
        _academic_state(e, s, rules)
        for e, s in zip(frame[columns["ESTADOACADEMICO"]], frame[columns["SITUACION"]])
    ]
    target = frame.loc[frame._ANOMATRICULA.eq(int(year)) & frame._PERIODOMATRICULA.eq(int(period))]
    detail = matricula.loc[target.index].copy()
    detail["TOKEN"] = target.TOKEN
    detail["TIENE_TRAYECTORIA_PREVIA"] = False
    detail["PRIMER_INGRESO_INSTITUCIONAL"] = target._ANOINGRESO.eq(int(year))
    detail["MOTIVO_TRAYECTORIA"] = "SIN_ANTECEDENTE_VALIDO_EN_OTRA_CARRERA"
    detail.loc[~target._ANOINGRESO.eq(int(year)), "MOTIVO_TRAYECTORIA"] = "INGRESO_ACADEMICO_FUERA_COHORTE"
    for field in ["ANTECEDENTES_VALIDOS", "ANTECEDENTES_TITULADOS", "ANTECEDENTES_SALIDA_INTERMEDIA",
                  "ANTECEDENTES_VIGENTES", "CASOS_TRAYECTORIA_POR_REVISAR", "MATRICULAS_MISMA_COHORTE",
                  "DUPLICADOS_TECNICOS_ANTECEDENTES"]:
        detail[field] = 0
    evidence = []
    historical = {key: group for key, group in frame.groupby("TOKEN", sort=False) if key}
    for index, current in target.iterrows():
        if not current.TOKEN:
            continue  # el consumidor mantiene su control estructural de RUT
        seen = set()
        reasons = set()
        for peer_index, peer in historical[current.TOKEN].iterrows():
            if peer_index == index:
                continue
            career = _career_relation(current, peer, aliases)
            if career == "MISMA_CARRERA":
                continue
            temporal = _temporal_relation(current, peer)
            state = peer._ESTADO_TRAYECTORIA
            signature = tuple(peer[k] if pd.notna(peer[k]) else "" for k in
                              ["_CODCLI", "_CODCARPR", "_NOMBREL", "_ANOINGRESO", "_PERIODOINGRESO",
                               "_ANOMATRICULA", "_PERIODOMATRICULA", "_ESTADO_TRAYECTORIA"])
            duplicate = signature in seen
            seen.add(signature)
            valid = (not duplicate and career == "OTRA_CARRERA" and temporal == "ANTERIOR"
                     and state in {"TITULADO", "SALIDA_INTERMEDIA", "VIGENTE"})
            ambiguous = (not duplicate and temporal != "POSTERIOR" and
                         (career == "POR_REVISAR" or state == "POR_REVISAR" or temporal == "POR_REVISAR"))
            if duplicate:
                detail.at[index, "DUPLICADOS_TECNICOS_ANTECEDENTES"] += 1
            if valid:
                reasons.add(state)
                detail.at[index, "ANTECEDENTES_VALIDOS"] += 1
                detail.at[index, "ANTECEDENTES_" + {"TITULADO":"TITULADOS", "VIGENTE":"VIGENTES",
                                                       "SALIDA_INTERMEDIA":"SALIDA_INTERMEDIA"}[state]] += 1
            if ambiguous:
                detail.at[index, "CASOS_TRAYECTORIA_POR_REVISAR"] += 1
            if not duplicate and career == "OTRA_CARRERA" and temporal == "MISMA_COHORTE" and state in {"TITULADO", "SALIDA_INTERMEDIA", "VIGENTE"}:
                detail.at[index, "MATRICULAS_MISMA_COHORTE"] += 1
            evidence.append({
                "INDICE_OBJETIVO": index, "INDICE_ANTECEDENTE": peer_index, "TOKEN": current.TOKEN,
                "CODCLI_OBJETIVO": current[columns["CODCLI"]], "CODCARPR_OBJETIVO": current[columns["CODCARPR"]],
                "NOMBRE_CARRERA_OBJETIVO": current[columns["NOMBREL"]],
                "CODCLI_ANTECEDENTE": peer[columns["CODCLI"]], "CODCARPR_ANTECEDENTE": peer[columns["CODCARPR"]],
                "NOMBRE_CARRERA_ANTECEDENTE": peer[columns["NOMBREL"]],
                "ANOINGRESO_ANTECEDENTE": peer[columns["ANOINGRESO"]],
                "PERIODOINGRESO_ANTECEDENTE": peer[columns["PERIODOINGRESO"]],
                "ESTADOACADEMICO_ANTECEDENTE": peer[columns["ESTADOACADEMICO"]],
                "SITUACION_ANTECEDENTE": peer[columns["SITUACION"]],
                "CLASIFICACION_ANTECEDENTE": state, "RELACION_CARRERA": career,
                "RELACION_TEMPORAL": temporal, "DUPLICADO_TECNICO": duplicate,
                "ANTECEDENTE_VALIDO": valid, "POR_REVISAR": ambiguous,
            })
        if reasons:
            detail.at[index, "TIENE_TRAYECTORIA_PREVIA"] = True
            detail.at[index, "PRIMER_INGRESO_INSTITUCIONAL"] = False
            detail.at[index, "MOTIVO_TRAYECTORIA"] = "TRAYECTORIA_PREVIA: " + "; ".join(sorted(reasons))
    evidence_columns = ["INDICE_OBJETIVO", "INDICE_ANTECEDENTE", "TOKEN", "CODCLI_OBJETIVO", "CODCARPR_OBJETIVO",
                        "NOMBRE_CARRERA_OBJETIVO", "CODCLI_ANTECEDENTE", "CODCARPR_ANTECEDENTE", "NOMBRE_CARRERA_ANTECEDENTE",
                        "ANOINGRESO_ANTECEDENTE", "PERIODOINGRESO_ANTECEDENTE", "ESTADOACADEMICO_ANTECEDENTE",
                        "SITUACION_ANTECEDENTE", "CLASIFICACION_ANTECEDENTE", "RELACION_CARRERA", "RELACION_TEMPORAL",
                        "DUPLICADO_TECNICO", "ANTECEDENTE_VALIDO", "POR_REVISAR"]
    individual = pd.DataFrame(evidence, columns=evidence_columns)
    summary = {
        "POLITICA": POLICY, "ANO": int(year), "PERIODO": int(period),
        "REGISTROS_HISTORICO_COMPLETO": len(matricula), "REGISTROS_PERIODO": len(detail),
        "PERSONAS_PERIODO": int(detail.loc[detail.TOKEN.ne(""), "TOKEN"].nunique()),
        "PRIMER_INGRESO_INSTITUCIONAL_REGISTROS": int(detail.PRIMER_INGRESO_INSTITUCIONAL.sum()),
        "PRIMER_INGRESO_INSTITUCIONAL_PERSONAS": int(detail.loc[detail.PRIMER_INGRESO_INSTITUCIONAL & detail.TOKEN.ne(""), "TOKEN"].nunique()),
        "TRAYECTORIA_PREVIA_REGISTROS": int(detail.TIENE_TRAYECTORIA_PREVIA.sum()),
        "TRAYECTORIA_PREVIA_PERSONAS": int(detail.loc[detail.TIENE_TRAYECTORIA_PREVIA & detail.TOKEN.ne(""), "TOKEN"].nunique()),
        "REGISTROS_CON_ANTECEDENTE_TITULADO": int(detail.ANTECEDENTES_TITULADOS.gt(0).sum()),
        "REGISTROS_CON_ANTECEDENTE_SALIDA_INTERMEDIA": int(detail.ANTECEDENTES_SALIDA_INTERMEDIA.gt(0).sum()),
        "REGISTROS_CON_ANTECEDENTE_VIGENTE": int(detail.ANTECEDENTES_VIGENTES.gt(0).sum()),
        "REGISTROS_CON_CASOS_POR_REVISAR": int(detail.CASOS_TRAYECTORIA_POR_REVISAR.gt(0).sum()),
        "REGISTROS_CON_MATRICULA_MISMA_COHORTE": int(detail.MATRICULAS_MISMA_COHORTE.gt(0).sum()),
        "DUPLICADOS_TECNICOS_ANTECEDENTES": int(detail.DUPLICADOS_TECNICOS_ANTECEDENTES.sum()),
        "REGLA_TIEMPO": "ANOINGRESO/PERIODOINGRESO estrictamente anterior; no por orden ni FECHAMATRICULA",
        "REGLA_CARRERA": "CODCARPR distinto, sin alias canónico compartido y NOMBRE_L normalizado distinto",
    }
    return detail, summary, individual


__all__ = ["POLICY", "classify_trajectories"]

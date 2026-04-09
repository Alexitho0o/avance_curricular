#!/usr/bin/env python3
"""Construye la tabla canonica Logistica TLOG/ILOG/CILOG.

El script trabaja solo con fuentes locales observadas. No genera precarga,
no genera PES y no modifica fuentes originales.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CARPETA_DEFAULT = (
    REPO
    / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/"
    "AUDITORIA_MALLAS_COMPARTIDAS_END_TO_END_20260701_090314"
)
FUENTE_PLANES = CARPETA_DEFAULT / "04_RESULTADOS/28_CODIGOS_PLAN_LOGISTICA_CONFIRMADOS.tsv"
CONTROL_PLANES = CARPETA_DEFAULT / "05_AUDITORIA/FASE8C_CONTROL_CODIGOS_PLAN_LOGISTICA.tsv"
FUENTE_CANONICA = (
    REPO
    / "avance_curricular_2026/04_gobernanza_mallas/02_conciliacion/"
    "CONCILIACION_CANONICA_PDF_HOJA1_20260626_170541/"
    "02_CATALOGO_HOJA1_PLANES_CANONICOS.tsv"
)

ESTADOS_HIPOTESIS = {
    "CONFIRMADA",
    "CONFIRMADA_CON_MATICES",
    "PARCIALMENTE_CONFIRMADA",
    "NO_CONFIRMADA",
    "SIN_EVIDENCIA_SUFICIENTE",
}


@dataclass(frozen=True)
class Planes:
    tecnico: str
    profesional: str
    continuidad: str


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalizar_texto(valor: object) -> str:
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    texto = texto.upper()
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def leer_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def ordenar_numerico(valores: Iterable[str]) -> list[str]:
    def key(v: str) -> tuple[int, str]:
        return (int(v), v) if str(v).isdigit() else (10_000, str(v))

    return sorted({str(v) for v in valores if str(v) != ""}, key=key)


def unir(valores: Iterable[str]) -> str:
    return "|".join(ordenar_numerico(valores))


def unir_texto(valores: Iterable[str]) -> str:
    return "|".join(sorted({str(v) for v in valores if str(v) != ""}))


def validar_planes_confirmados(planes: Planes) -> None:
    for path in [FUENTE_PLANES, CONTROL_PLANES, FUENTE_CANONICA]:
        if not path.exists():
            raise FileNotFoundError(f"Fuente obligatoria no encontrada: {path}")

    df = leer_tsv(FUENTE_PLANES)
    requeridas = {
        "CODIGO_PLAN",
        "NOMBRE_CARRERA",
        "TIPO_PROGRAMA",
        "TIPO_PLAN_CARRERA",
        "DURACION_ESTUDIOS",
        "ES_CONTINUIDAD",
        "FUENTE",
        "NIVEL_RESPALDO",
    }
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"La fuente de planes no contiene columnas requeridas: {sorted(faltantes)}")

    observados = set(df["CODIGO_PLAN"].astype(str))
    esperados = {planes.tecnico, planes.profesional, planes.continuidad}
    if not esperados <= observados:
        raise ValueError(f"Planes no confirmados en la fuente: {sorted(esperados - observados)}")

    respaldo = df[df["CODIGO_PLAN"].isin(esperados)]["NIVEL_RESPALDO"].replace("", pd.NA).dropna()
    if respaldo.empty or set(respaldo) != {"DATO_OBSERVADO"}:
        raise ValueError("Los planes deben estar respaldados solo como DATO_OBSERVADO")


def cargar_bruto(plan: str, fuente_hash: str) -> pd.DataFrame:
    df = leer_tsv(FUENTE_CANONICA)
    requerido = {
        "CODCARR",
        "PLAN_DE_ESTUDIO",
        "REGIMEN",
        "NIVEL",
        "PERIODO",
        "CODRAMO",
        "RAMOEQUIV",
        "ASIGNATURA",
        "ASIGNATURA_NORMALIZADA",
        "ANO",
    }
    faltantes = requerido - set(df.columns)
    if faltantes:
        raise ValueError(f"Fuente canonica incompleta: {sorted(faltantes)}")
    bruto = df[df["PLAN_DE_ESTUDIO"] == plan].copy()
    if bruto.empty:
        raise ValueError(f"Sin registros canonicos para plan {plan}")
    bruto.insert(0, "ID_REGISTRO_BRUTO", [f"{plan}_B_{i:04d}" for i in range(1, len(bruto) + 1)])
    bruto["CLAVE_ASIGNATURA_CANONICA"] = bruto["ASIGNATURA_NORMALIZADA"].map(normalizar_texto)
    bruto["FUENTE_CANONICA"] = str(FUENTE_CANONICA)
    bruto["HASH_FUENTE_CANONICA"] = fuente_hash
    bruto["NIVEL_RESPALDO"] = "DATO_OBSERVADO"
    return bruto.sort_values(["NIVEL", "PERIODO", "CLAVE_ASIGNATURA_CANONICA", "CODRAMO"])


def depurar(bruto: pd.DataFrame, plan: str) -> pd.DataFrame:
    filas: list[dict[str, str]] = []
    for i, (clave, grupo) in enumerate(bruto.groupby("CLAVE_ASIGNATURA_CANONICA", sort=True), start=1):
        niveles = ordenar_numerico(grupo["NIVEL"])
        periodos = ordenar_numerico(grupo["PERIODO"])
        anos = ordenar_numerico(grupo["ANO"])
        filas.append(
            {
                "ID_ASIGNATURA_PLAN": f"{plan}_D_{i:03d}",
                "PLAN_DE_ESTUDIO": plan,
                "CODCARR": unir_texto(grupo["CODCARR"]),
                "CLAVE_ASIGNATURA_CANONICA": clave,
                "ASIGNATURA_CANONICA": unir_texto(grupo["ASIGNATURA_NORMALIZADA"]),
                "ASIGNATURA_ORIGINAL_OBSERVADA": unir_texto(grupo["ASIGNATURA"]),
                "CODRAMO_OBSERVADO": unir_texto(grupo["CODRAMO"]),
                "RAMOEQUIV_OBSERVADO": unir_texto(grupo["RAMOEQUIV"]),
                "NIVEL_ORIGINAL": "|".join(niveles),
                "NIVEL_MIN": niveles[0] if niveles else "",
                "NIVEL_MAX": niveles[-1] if niveles else "",
                "PERIODO_OBSERVADO": "|".join(periodos),
                "ANO_OBSERVADO": "|".join(anos),
                "REGIMEN": unir_texto(grupo["REGIMEN"]),
                "FILAS_BRUTAS": str(len(grupo)),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
                "CRITERIO_DEPURACION": "PLAN+ASIGNATURA_NORMALIZADA; sin keep first/last",
            }
        )
    return pd.DataFrame(filas).sort_values(["NIVEL_MIN", "PERIODO_OBSERVADO", "CLAVE_ASIGNATURA_CANONICA"])


def expand_codes(valor: str) -> set[str]:
    return {v for v in str(valor).split("|") if v}


def comparar(a: pd.DataFrame, b: pd.DataFrame, nombre_a: str, nombre_b: str) -> pd.DataFrame:
    keys = sorted(set(a["CLAVE_ASIGNATURA_CANONICA"]) | set(b["CLAVE_ASIGNATURA_CANONICA"]))
    a_idx = a.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    b_idx = b.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    filas = []
    for key in keys:
        en_a = key in a_idx.index
        en_b = key in b_idx.index
        ra = a_idx.loc[key] if en_a else None
        rb = b_idx.loc[key] if en_b else None
        codes_a = expand_codes(ra["CODRAMO_OBSERVADO"]) | expand_codes(ra["RAMOEQUIV_OBSERVADO"]) if en_a else set()
        codes_b = expand_codes(rb["CODRAMO_OBSERVADO"]) | expand_codes(rb["RAMOEQUIV_OBSERVADO"]) if en_b else set()
        inter_codes = sorted(codes_a & codes_b)
        tipo = "COMUN_NOMBRE_NORMALIZADO_EXACTO" if en_a and en_b else f"SOLO_{nombre_a if en_a else nombre_b}"
        if en_a and en_b and inter_codes:
            tipo = "COMUN_NOMBRE_NORMALIZADO_Y_CODIGO_RELACIONADO"
        filas.append(
            {
                "CLAVE_ASIGNATURA_CANONICA": key,
                f"EN_{nombre_a}": "SI" if en_a else "NO",
                f"EN_{nombre_b}": "SI" if en_b else "NO",
                "TIPO_COMPARACION": tipo,
                f"NIVEL_{nombre_a}": ra["NIVEL_ORIGINAL"] if en_a else "",
                f"NIVEL_{nombre_b}": rb["NIVEL_ORIGINAL"] if en_b else "",
                f"CODRAMO_{nombre_a}": ra["CODRAMO_OBSERVADO"] if en_a else "",
                f"CODRAMO_{nombre_b}": rb["CODRAMO_OBSERVADO"] if en_b else "",
                f"RAMOEQUIV_{nombre_a}": ra["RAMOEQUIV_OBSERVADO"] if en_a else "",
                f"RAMOEQUIV_{nombre_b}": rb["RAMOEQUIV_OBSERVADO"] if en_b else "",
                "CODIGOS_RELACIONADOS_OBSERVADOS": "|".join(inter_codes),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            }
        )
    return pd.DataFrame(filas)


def comparar_union(tlog: pd.DataFrame, cilog: pd.DataFrame, ilog: pd.DataFrame) -> pd.DataFrame:
    t_idx = tlog.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    c_idx = cilog.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    i_idx = ilog.set_index("CLAVE_ASIGNATURA_CANONICA", drop=False)
    union_tc = sorted(set(t_idx.index) | set(c_idx.index))
    keys = sorted(set(union_tc) | set(i_idx.index))
    filas = []
    for key in keys:
        en_t = key in t_idx.index
        en_c = key in c_idx.index
        en_i = key in i_idx.index
        if en_i and (en_t or en_c):
            estado = "ILOG_CUBIERTO_POR_TLOG_MAS_CILOG"
        elif en_i:
            estado = "SOLO_ILOG"
        else:
            estado = "EXTRA_TLOG_MAS_CILOG"
        filas.append(
            {
                "CLAVE_ASIGNATURA_CANONICA": key,
                "EN_TLOG": "SI" if en_t else "NO",
                "EN_CILOG": "SI" if en_c else "NO",
                "EN_TLOG_MAS_CILOG_UNICO": "SI" if (en_t or en_c) else "NO",
                "EN_ILOG": "SI" if en_i else "NO",
                "ESTADO_COMPARACION": estado,
                "NIVEL_TLOG": t_idx.loc[key]["NIVEL_ORIGINAL"] if en_t else "",
                "NIVEL_CILOG_ORIGINAL": c_idx.loc[key]["NIVEL_ORIGINAL"] if en_c else "",
                "NIVEL_ILOG": i_idx.loc[key]["NIVEL_ORIGINAL"] if en_i else "",
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            }
        )
    return pd.DataFrame(filas)


def pct(num: int, den: int) -> str:
    return "" if den == 0 else f"{(num / den) * 100:.2f}"


def resumen_nivel(tlog: pd.DataFrame, ilog: pd.DataFrame, cilog: pd.DataFrame) -> pd.DataFrame:
    t_keys = set(tlog["CLAVE_ASIGNATURA_CANONICA"])
    i_keys = set(ilog["CLAVE_ASIGNATURA_CANONICA"])
    c_keys = set(cilog["CLAVE_ASIGNATURA_CANONICA"])
    niveles = ordenar_numerico(list(tlog["NIVEL_MIN"]) + list(ilog["NIVEL_MIN"]) + list(cilog["NIVEL_MIN"]))
    filas = []
    for nivel in niveles:
        t_n = set(tlog.loc[tlog["NIVEL_MIN"] == nivel, "CLAVE_ASIGNATURA_CANONICA"])
        i_n = set(ilog.loc[ilog["NIVEL_MIN"] == nivel, "CLAVE_ASIGNATURA_CANONICA"])
        c_n = set(cilog.loc[cilog["NIVEL_MIN"] == nivel, "CLAVE_ASIGNATURA_CANONICA"])
        tc_union_n = t_n | c_n
        obs = "CILOG usa nivel original propio; no homologar directo salvo evidencia en validacion."
        filas.append(
            {
                "NIVEL": nivel,
                "TLOG_TOTAL": len(t_n),
                "ILOG_TOTAL": len(i_n),
                "CILOG_TOTAL": len(c_n),
                "COMUN_TLOG_ILOG": len(t_n & i_keys),
                "COMUN_TLOG_CILOG": len(t_n & c_keys),
                "COMUN_ILOG_CILOG": len(i_n & c_keys),
                "COMUN_TRES_PLANES": len(t_n & i_keys & c_keys),
                "SOLO_TLOG": len(t_n - i_keys - c_keys),
                "SOLO_ILOG": len(i_n - t_keys - c_keys),
                "SOLO_CILOG": len(c_n - t_keys - i_keys),
                "TLOG_MAS_CILOG_UNICOS": len(tc_union_n),
                "COBERTURA_TLOG_EN_ILOG": pct(len(i_n & t_keys), len(i_n)),
                "COBERTURA_CILOG_EN_ILOG": pct(len(i_n & c_keys), len(i_n)),
                "COBERTURA_TLOG_MAS_CILOG_EN_ILOG": pct(len(i_n & (t_keys | c_keys)), len(i_n)),
                "OBSERVACION": obs,
            }
        )
    return pd.DataFrame(filas)


def validacion_continuidad(tlog: pd.DataFrame, ilog: pd.DataFrame, cilog: pd.DataFrame) -> pd.DataFrame:
    t, i, c = set(tlog["CLAVE_ASIGNATURA_CANONICA"]), set(ilog["CLAVE_ASIGNATURA_CANONICA"]), set(cilog["CLAVE_ASIGNATURA_CANONICA"])
    ci = comparar(cilog, ilog, "CILOG", "ILOG")
    comunes_ci = ci[(ci["EN_CILOG"] == "SI") & (ci["EN_ILOG"] == "SI")].copy()
    equivalencias = []
    for _, row in comunes_ci.iterrows():
        equivalencias.append(f"CILOG {row['NIVEL_CILOG']} -> ILOG {row['NIVEL_ILOG']}: {row['CLAVE_ASIGNATURA_CANONICA']}")
    union_tc = t | c
    t_en_i = len(t & i)
    c_en_i = len(c & i)
    union_en_i = len(union_tc & i)
    estado_h1 = "PARCIALMENTE_CONFIRMADA" if t_en_i < len(t) else "CONFIRMADA"
    estado_h2 = "PARCIALMENTE_CONFIRMADA" if 0 < c_en_i < len(c) else ("CONFIRMADA" if c_en_i == len(c) else "NO_CONFIRMADA")
    estado_h3 = "PARCIALMENTE_CONFIRMADA" if union_en_i < len(i) or len(union_tc - i) > 0 else "CONFIRMADA"
    niveles_t_dif = sorted({r["NIVEL_TLOG"] for _, r in comparar(tlog, ilog, "TLOG", "ILOG").iterrows() if r["EN_TLOG"] == "SI" and r["EN_ILOG"] == "NO" and r["NIVEL_TLOG"]})
    niveles_i_dif = sorted({r["NIVEL_ILOG"] for _, r in comparar(tlog, ilog, "TLOG", "ILOG").iterrows() if r["EN_ILOG"] == "SI" and r["EN_TLOG"] == "NO" and r["NIVEL_ILOG"]})
    primer_dif = ordenar_numerico(niveles_t_dif + niveles_i_dif)
    estado_h4 = "CONFIRMADA_CON_MATICES" if primer_dif and primer_dif[0] == "7" else "NO_CONFIRMADA"
    rows = [
        {
            "TIPO_REGISTRO": "HIPOTESIS",
            "HIPOTESIS": "HIPOTESIS 1",
            "DESCRIPCION": "TLOG esta contenida en ILOG.",
            "ESTADO": estado_h1,
            "EVIDENCIA": f"{t_en_i}/{len(t)} asignaturas TLOG aparecen en ILOG por nombre normalizado exacto.",
            "NIVEL_RESPALDO": "DATO_OBSERVADO",
        },
        {
            "TIPO_REGISTRO": "HIPOTESIS",
            "HIPOTESIS": "HIPOTESIS 2",
            "DESCRIPCION": "CILOG corresponde al tramo profesional final de ILOG.",
            "ESTADO": estado_h2,
            "EVIDENCIA": f"{c_en_i}/{len(c)} asignaturas CILOG aparecen en ILOG por nombre normalizado exacto. Equivalencias observadas: {'; '.join(equivalencias) if equivalencias else 'sin equivalencias exactas'}",
            "NIVEL_RESPALDO": "DATO_OBSERVADO",
        },
        {
            "TIPO_REGISTRO": "HIPOTESIS",
            "HIPOTESIS": "HIPOTESIS 3",
            "DESCRIPCION": "TLOG mas CILOG reconstruyen la malla de ILOG.",
            "ESTADO": estado_h3,
            "EVIDENCIA": f"{union_en_i}/{len(i)} asignaturas ILOG cubiertas por TLOG+CILOG; extras TLOG+CILOG no presentes en ILOG: {len(union_tc - i)}.",
            "NIVEL_RESPALDO": "DATO_OBSERVADO",
        },
        {
            "TIPO_REGISTRO": "HIPOTESIS",
            "HIPOTESIS": "HIPOTESIS 4",
            "DESCRIPCION": "Las diferencias entre TLOG e ILOG ocurren unicamente al final.",
            "ESTADO": estado_h4,
            "EVIDENCIA": f"Primer nivel observado con diferencias TLOG/ILOG: {primer_dif[0] if primer_dif else 'sin diferencias'}; niveles con diferencias TLOG={unir(niveles_t_dif)}, ILOG={unir(niveles_i_dif)}.",
            "NIVEL_RESPALDO": "DATO_OBSERVADO",
        },
    ]
    for estado in [r["ESTADO"] for r in rows]:
        if estado not in ESTADOS_HIPOTESIS:
            raise ValueError(f"Estado de hipotesis no permitido: {estado}")
    for _, row in comunes_ci.iterrows():
        rows.append(
            {
                "TIPO_REGISTRO": "EQUIVALENCIA_NIVEL_OBSERVADA",
                "HIPOTESIS": "CONTROL_ESPECIAL_NIVELES",
                "DESCRIPCION": "Equivalencia observada por asignatura comun exacta CILOG/ILOG.",
                "ESTADO": "PARCIALMENTE_CONFIRMADA",
                "EVIDENCIA": (
                    f"NIVEL_CILOG_ORIGINAL={row['NIVEL_CILOG']}; "
                    f"NIVEL_ILOG_EQUIVALENTE_OBSERVADO={row['NIVEL_ILOG']}; "
                    f"ASIGNATURA={row['CLAVE_ASIGNATURA_CANONICA']}; FUENTE_EQUIVALENCIA=nombre normalizado exacto"
                ),
                "NIVEL_RESPALDO": "DATO_OBSERVADO",
            }
        )
    return pd.DataFrame(rows)


def casos_criticos(tlog: pd.DataFrame, ilog: pd.DataFrame, cilog: pd.DataFrame) -> pd.DataFrame:
    comp_ti = comparar(tlog, ilog, "TLOG", "ILOG")
    comp_ci = comparar(cilog, ilog, "CILOG", "ILOG")
    union = comparar_union(tlog, cilog, ilog)
    filas = []
    for _, row in comp_ti.iterrows():
        if row["EN_TLOG"] == "SI" and row["EN_ILOG"] == "NO":
            filas.append(
                {
                    "CASO": "SOLO_TLOG_FRENTE_A_ILOG",
                    "CLAVE_ASIGNATURA_CANONICA": row["CLAVE_ASIGNATURA_CANONICA"],
                    "DETALLE": "Asignatura observada en TLOG sin nombre normalizado exacto en ILOG.",
                    "NIVEL_RESPALDO": "DATO_OBSERVADO",
                }
            )
        if row["EN_ILOG"] == "SI" and row["EN_TLOG"] == "NO":
            filas.append(
                {
                    "CASO": "SOLO_ILOG_FRENTE_A_TLOG",
                    "CLAVE_ASIGNATURA_CANONICA": row["CLAVE_ASIGNATURA_CANONICA"],
                    "DETALLE": "Asignatura observada en ILOG sin nombre normalizado exacto en TLOG.",
                    "NIVEL_RESPALDO": "DATO_OBSERVADO",
                }
            )
    for _, row in comp_ci.iterrows():
        if row["EN_CILOG"] == "SI" and row["EN_ILOG"] == "NO":
            filas.append(
                {
                    "CASO": "SOLO_CILOG_FRENTE_A_ILOG",
                    "CLAVE_ASIGNATURA_CANONICA": row["CLAVE_ASIGNATURA_CANONICA"],
                    "DETALLE": "Asignatura CILOG no encontrada en ILOG por nombre normalizado exacto.",
                    "NIVEL_RESPALDO": "DATO_OBSERVADO",
                }
            )
    for _, row in union.iterrows():
        if row["ESTADO_COMPARACION"] in {"SOLO_ILOG", "EXTRA_TLOG_MAS_CILOG"}:
            filas.append(
                {
                    "CASO": row["ESTADO_COMPARACION"],
                    "CLAVE_ASIGNATURA_CANONICA": row["CLAVE_ASIGNATURA_CANONICA"],
                    "DETALLE": "Diferencia al comparar TLOG+CILOG sin duplicados contra ILOG.",
                    "NIVEL_RESPALDO": "DATO_OBSERVADO",
                }
            )
    return pd.DataFrame(filas).drop_duplicates().sort_values(["CASO", "CLAVE_ASIGNATURA_CANONICA"])


def escribir_excel(path: Path, hojas: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in hojas.items():
            sheet = name[:31]
            df.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.book[sheet]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                letter = col[0].column_letter
                width = min(max(len(str(cell.value or "")) for cell in col) + 2, 60)
                ws.column_dimensions[letter].width = width


def ejecutar(planes: Planes, carpeta: Path) -> dict[str, object]:
    validar_planes_confirmados(planes)
    inter = carpeta / "02_INTERMEDIOS"
    res = carpeta / "03_RESULTADOS"
    inter.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)

    fuente_hash = sha256(FUENTE_CANONICA)
    bruto_t = cargar_bruto(planes.tecnico, fuente_hash)
    bruto_i = cargar_bruto(planes.profesional, fuente_hash)
    bruto_c = cargar_bruto(planes.continuidad, fuente_hash)
    dep_t = depurar(bruto_t, planes.tecnico)
    dep_i = depurar(bruto_i, planes.profesional)
    dep_c = depurar(bruto_c, planes.continuidad)

    comp_ti = comparar(dep_t, dep_i, "TLOG", "ILOG")
    comp_tc = comparar(dep_t, dep_c, "TLOG", "CILOG")
    comp_ic = comparar(dep_i, dep_c, "ILOG", "CILOG")
    comp_union = comparar_union(dep_t, dep_c, dep_i)
    resumen = resumen_nivel(dep_t, dep_i, dep_c)
    validacion = validacion_continuidad(dep_t, dep_i, dep_c)
    criticos = casos_criticos(dep_t, dep_i, dep_c)

    salidas = {
        inter / "01_TLOG_CANONICO_BRUTO.tsv": bruto_t,
        inter / "02_ILOG_CANONICO_BRUTO.tsv": bruto_i,
        inter / "03_CILOG_CANONICO_BRUTO.tsv": bruto_c,
        inter / "04_TLOG_CANONICO_DEPURADO.tsv": dep_t,
        inter / "05_ILOG_CANONICO_DEPURADO.tsv": dep_i,
        inter / "06_CILOG_CANONICO_DEPURADO.tsv": dep_c,
        res / "01_COMPARACION_TLOG_ILOG.tsv": comp_ti,
        res / "02_COMPARACION_TLOG_CILOG.tsv": comp_tc,
        res / "03_COMPARACION_ILOG_CILOG.tsv": comp_ic,
        res / "04_COMPARACION_TLOG_MAS_CILOG_VS_ILOG.tsv": comp_union,
        res / "05_RESUMEN_NIVEL_POR_NIVEL_TRES_PLANES.tsv": resumen,
        res / "06_VALIDACION_ESTRUCTURA_CONTINUIDAD.tsv": validacion,
        res / "07_CASOS_CRITICOS_LOGISTICA.tsv": criticos,
    }
    for path, df in salidas.items():
        df.to_csv(path, sep="\t", index=False)

    excel = res / "08_TABLA_CANONICA_LOGISTICA_TRES_PLANES.xlsx"
    escribir_excel(
        excel,
        {
            "RESUMEN_NIVELES": resumen,
            "VALIDACION_CONTINUIDAD": validacion,
            "TLOG_DEPURADO": dep_t,
            "ILOG_DEPURADO": dep_i,
            "CILOG_DEPURADO": dep_c,
            "TLOG_ILOG": comp_ti,
            "TLOG_CILOG": comp_tc,
            "ILOG_CILOG": comp_ic,
            "TLOG_CILOG_VS_ILOG": comp_union,
            "CASOS_CRITICOS": criticos,
            "DICCIONARIO": pd.DataFrame(
                [
                    {"CAMPO": "CLAVE_ASIGNATURA_CANONICA", "DESCRIPCION": "Nombre normalizado sin acentos ni signos usado para comparacion exacta."},
                    {"CAMPO": "NIVEL_RESPALDO", "DESCRIPCION": "Todas las filas son DATO_OBSERVADO; no son regla oficial."},
                    {"CAMPO": "NIVEL_CILOG_ORIGINAL", "DESCRIPCION": "Nivel observado en CILOG; no homologar directo sin evidencia."},
                ]
            ),
        },
    )

    manifiesto = {
        "estado": "COMPLETADA",
        "planes": {
            "tecnico": planes.tecnico,
            "profesional": planes.profesional,
            "continuidad": planes.continuidad,
        },
        "fuente_planes": str(FUENTE_PLANES),
        "control_planes": str(CONTROL_PLANES),
        "fuente_canonica": str(FUENTE_CANONICA),
        "hash_fuente_canonica": fuente_hash,
        "salidas": {str(k): {"filas": len(v), "hash": sha256(k)} for k, v in salidas.items()},
        "excel": str(excel),
        "hash_excel": sha256(excel),
        "nivel_respaldo": "DATO_OBSERVADO",
        "precarga_generada": "NO",
        "pes_generado": "NO",
        "apto_para_carga": "NO",
    }
    (res / "09_MANIFIESTO_TABLA_CANONICA_LOGISTICA.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "estado": "COMPLETADA",
        "bruto": {"TLOG": len(bruto_t), "ILOG": len(bruto_i), "CILOG": len(bruto_c)},
        "depurado": {"TLOG": len(dep_t), "ILOG": len(dep_i), "CILOG": len(dep_c)},
        "comunes": {
            "TLOG_ILOG": int(((comp_ti["EN_TLOG"] == "SI") & (comp_ti["EN_ILOG"] == "SI")).sum()),
            "TLOG_CILOG": int(((comp_tc["EN_TLOG"] == "SI") & (comp_tc["EN_CILOG"] == "SI")).sum()),
            "ILOG_CILOG": int(((comp_ic["EN_ILOG"] == "SI") & (comp_ic["EN_CILOG"] == "SI")).sum()),
            "TLOG_MAS_CILOG_EN_ILOG": int((comp_union["ESTADO_COMPARACION"] == "ILOG_CUBIERTO_POR_TLOG_MAS_CILOG").sum()),
        },
        "excel": str(excel),
        "resumen": str(res / "05_RESUMEN_NIVEL_POR_NIVEL_TRES_PLANES.tsv"),
        "validacion": str(res / "06_VALIDACION_ESTRUCTURA_CONTINUIDAD.tsv"),
        "criticos": str(res / "07_CASOS_CRITICOS_LOGISTICA.tsv"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar-completo", action="store_true", required=True)
    parser.add_argument("--plan-tecnico", required=True)
    parser.add_argument("--plan-profesional", required=True)
    parser.add_argument("--plan-continuidad", required=True)
    parser.add_argument("--carpeta-ejecucion", default=str(CARPETA_DEFAULT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    planes = Planes(
        tecnico=args.plan_tecnico,
        profesional=args.plan_profesional,
        continuidad=args.plan_continuidad,
    )
    resultado = ejecutar(planes, Path(args.carpeta_ejecucion))
    print("TABLA CANONICA LOGISTICA TRES PLANES COMPLETADA")
    print(f"Estado: {resultado['estado']}")
    print(f"Asignaturas depuradas TLOG: {resultado['depurado']['TLOG']}")
    print(f"Asignaturas depuradas ILOG: {resultado['depurado']['ILOG']}")
    print(f"Asignaturas depuradas CILOG: {resultado['depurado']['CILOG']}")
    print(f"Comunes TLOG/ILOG: {resultado['comunes']['TLOG_ILOG']}")
    print(f"Comunes TLOG/CILOG: {resultado['comunes']['TLOG_CILOG']}")
    print(f"Comunes ILOG/CILOG: {resultado['comunes']['ILOG_CILOG']}")
    print(f"TLOG+CILOG en ILOG: {resultado['comunes']['TLOG_MAS_CILOG_EN_ILOG']}")
    print(f"Excel: {resultado['excel']}")
    print(f"Resumen: {resultado['resumen']}")
    print(f"Validacion continuidad: {resultado['validacion']}")
    print(f"Casos criticos: {resultado['criticos']}")


if __name__ == "__main__":
    main()

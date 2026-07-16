#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cierre funcional/documental de NIVEL y periodizacion anual para Carreras
Avance Curricular SIES 2026, ID 16769.

No genera CSV final, no corrige datos, no modifica fuentes originales y no
declara SIES_READY.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
BASE = RAIZ / "avance_curricular_2026"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_BASE = BASE / "110_cierre_funcional_nivel_periodizacion_carreras_16769"
OUT = OUT_BASE / f"CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769_{TS}"

DIAG109 = (
    BASE
    / "109_diagnostico_gobernado_carreras_16769/DIAGNOSTICO_GOBERNADO_CARRERAS_16769_20260709_105803"
)
DIAG_XLSX = DIAG109 / "DIAGNOSTICO_GOBERNADO_CARRERAS_16769.xlsx"
DIAG_MD = DIAG109 / "INFORME_DIAGNOSTICO_GOBERNADO_CARRERAS_16769.md"
DIAG_MANIFEST = DIAG109 / "manifest_diagnostico_gobernado_carreras_16769.json"

MANUAL = (
    BASE
    / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/"
    / "Instructivo_Avance Curricular SIES - 2026.txt"
)
PRECARGA = (
    BASE
    / "00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/"
    / "5810_Precarga Carreras Avance Curricular 20268.csv"
)
CANONICO = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/CANONICO_TODOS_PLANES_ESTUDIO_20260701_140528/"
    / "02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv"
)
CONC43 = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/CIERRE_FINAL_43_RESUELTAS_0_PENDIENTES_20260701_171409/"
    / "02_RESULTADOS/01_CONCILIACION_FINAL_43.tsv"
)
SEMANTICA_RESUMEN = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/INVESTIGACION_SEMANTICA_NIVEL_PLANES_20260701_191051/"
    / "06_REPORTES/RESUMEN_INVESTIGACION_SEMANTICA_NIVEL.md"
)
SEMANTICA_GLOBAL = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/INVESTIGACION_SEMANTICA_NIVEL_PLANES_20260701_191051/"
    / "05_RESULTADOS/conclusion_semantica_global.tsv"
)
SEMANTICA_PLAN = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/INVESTIGACION_SEMANTICA_NIVEL_PLANES_20260701_191051/"
    / "05_RESULTADOS/conclusion_semantica_por_plan.tsv"
)
HIPOTESIS = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/INVESTIGACION_SEMANTICA_NIVEL_PLANES_20260701_191051/"
    / "04_HIPOTESIS/evaluacion_hipotesis.tsv"
)
FORMULAS_COMENTARIOS = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/INVESTIGACION_SEMANTICA_NIVEL_PLANES_20260701_191051/"
    / "01_ESTRUCTURA_EXCEL/formulas_comentarios_validaciones.tsv"
)
BUSQUEDA_CONCLUSION = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/BUSQUEDA_FUENTE_SEMESTRE_ANIO_MALLAS_20260701_220323/"
    / "05_RESULTADOS/conclusion_busqueda_fuente.tsv"
)
FUENTE_FALTANTE = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/BUSQUEDA_FUENTE_SEMESTRE_ANIO_MALLAS_20260701_220323/"
    / "05_RESULTADOS/especificacion_fuente_faltante.tsv"
)
VALID_EQ_MANIFEST = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/VALIDACION_EQUIVALENCIA_NIVEL_ANIO_20260701_225538/"
    / "manifiesto.json"
)
VALID_EQ_EQUIV = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/VALIDACION_EQUIVALENCIA_NIVEL_ANIO_20260701_225538/"
    / "equivalencia_nivel_anio.tsv"
)
VALID_EQ_VALIDACIONES = (
    BASE
    / "04_gobernanza_mallas/03_auditorias/VALIDACION_EQUIVALENCIA_NIVEL_ANIO_20260701_225538/"
    / "validaciones.tsv"
)
GOB_MU_NIV_ACA = RAIZ / "gobernanza_columnas_mu/gob_mu_niv_aca.tsv"

UNIT_COLS = [
    "UNIDADES_1ER_ANIO",
    "UNIDADES_2DO_ANIO",
    "UNIDADES_3ER_ANIO",
    "UNIDADES_4TO_ANIO",
    "UNIDADES_5TO_ANIO",
    "UNIDADES_6TO_ANIO",
    "UNIDADES_7MO_ANIO",
]


def sha256(path: Path) -> str:
    if not path.exists() or path.is_dir():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str).fillna("")


def read_excel(sheet: str) -> pd.DataFrame:
    return pd.read_excel(DIAG_XLSX, sheet_name=sheet, dtype=str).fillna("")


def as_int(value: Any, default: int = 0) -> int:
    text = "" if value is None else str(value).strip()
    if text == "":
        return default
    try:
        return int(float(text.replace(",", ".")))
    except Exception:
        return default


def ceil_div2(value: Any) -> int | None:
    text = "" if value is None else str(value).strip()
    if text == "":
        return None
    try:
        return int(math.ceil(float(text.replace(",", ".")) / 2))
    except Exception:
        return None


def ordered_levels(series: pd.Series) -> str:
    vals = []
    for value in series.astype(str):
        value = value.strip()
        if not value:
            continue
        try:
            vals.append(int(float(value)))
        except Exception:
            continue
    if not vals:
        return ""
    return " | ".join(str(x) for x in sorted(set(vals)))


def build_context() -> dict[str, pd.DataFrame]:
    prec = read_excel("02_PRECARGA_5810")
    conv = read_excel("05_CONVERSION_NIVEL_A_ANIO")
    dist = read_excel("06_DISTRIBUCION_RECONSTRUIDA")
    reglas = read_excel("01_REGLAS_MANUAL")
    fuente_sel = read_excel("04_FUENTE_DETALLE_SELECCIONADA")
    canon = read_tsv(CANONICO)
    conc = read_tsv(CONC43)
    sem_global = read_tsv(SEMANTICA_GLOBAL)
    sem_plan = read_tsv(SEMANTICA_PLAN)
    hip = read_tsv(HIPOTESIS)
    busq = read_tsv(BUSQUEDA_CONCLUSION)
    faltante = read_tsv(FUENTE_FALTANTE)
    valid_eq = read_tsv(VALID_EQ_EQUIV)
    valid_eq_val = read_tsv(VALID_EQ_VALIDACIONES)
    formulas = read_tsv(FORMULAS_COMENTARIOS)
    return {
        "prec": prec,
        "conv": conv,
        "dist": dist,
        "reglas": reglas,
        "fuente_sel": fuente_sel,
        "canon": canon,
        "conc": conc,
        "sem_global": sem_global,
        "sem_plan": sem_plan,
        "hip": hip,
        "busq": busq,
        "faltante": faltante,
        "valid_eq": valid_eq,
        "valid_eq_val": valid_eq_val,
        "formulas": formulas,
    }


def build_canon_columns(canon: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, col in enumerate(canon.columns, start=1):
        non_empty = int((canon[col].astype(str).str.strip() != "").sum()) if not canon.empty else 0
        distinct = int(canon[col].nunique()) if not canon.empty else 0
        sample = " | ".join(canon[col].astype(str).str.strip().replace("", pd.NA).dropna().drop_duplicates().head(8).tolist()) if not canon.empty else ""
        rows.append(
            {
                "posicion": i,
                "columna": col,
                "no_vacios": non_empty,
                "distintos": distinct,
                "muestra": sample,
                "rol_observado": classify_col(col),
                "nivel_respaldo": "B - dato observado fuente canonica",
            }
        )
    return pd.DataFrame(rows)


def classify_col(col: str) -> str:
    c = col.upper()
    if c in {"CODPESTUD", "CODCARR", "CODRAMO", "RAMOEQUIV", "LLAVE_CANONICA"}:
        return "llave/codigo"
    if c == "NIVEL":
        return "atributo curricular observado; semantica temporal no confirmada"
    if c in {"NOMBRE", "NOMBRE_L", "NOMPESTUD", "DESCRAMOEQUIV", "DESCRAMOREQ"}:
        return "descripcion"
    if c in {"FUENTE", "HOJA_FUENTE", "NIVEL_RESPALDO", "ESTADO_CANONICO"}:
        return "trazabilidad"
    return "atributo"


def build_relationship(prec: pd.DataFrame, conv: pd.DataFrame, conc: pd.DataFrame) -> pd.DataFrame:
    conv = conv.copy()
    conv["TIENE_DETALLE_CANONICO"] = conv["CODRAMO"].astype(str).str.strip().ne("")
    rows = []
    for _, p in prec.iterrows():
        code = str(p.get("CODIGO_UNICO", "")).strip()
        det = conv[(conv["CODIGO_UNICO"].astype(str).str.strip() == code) & conv["TIENE_DETALLE_CANONICO"]]
        crows = conc[conc["CODIGO_UNICO"].astype(str).str.strip() == code] if not conc.empty else pd.DataFrame()
        c0 = crows.iloc[0] if not crows.empty else pd.Series(dtype=str)
        codp_struct = str(c0.get("CODPESTUD", "")).strip()
        fundamento = str(c0.get("FUNDAMENTO", "")).strip()
        plan_ref = str(c0.get("PLAN_DE_ESTUDIO_CANONICO", "") or c0.get("PLAN_DE_ESTUDIO_CANONICO_CIERRE", "")).strip()
        rows.append(
            {
                "CODIGO_UNICO": code,
                "PLAN_ESTUDIOS": p.get("PLAN_ESTUDIOS", ""),
                "NOMBRE_CARRERA": p.get("NOMBRE_CARRERA", ""),
                "JORNADA": p.get("JORNADA", ""),
                "VERSION": p.get("VERSION", ""),
                "DURACION_ESTUDIOS": p.get("DURACION_ESTUDIOS", ""),
                "ANIOS_PERMITIDOS": ceil_div2(p.get("DURACION_ESTUDIOS", "")),
                "CODPESTUD_ESTRUCTURADO_CONCILIACION": codp_struct,
                "PLAN_REFERIDO_TEXTO_CONCILIACION": plan_ref,
                "FUNDAMENTO_TECNICO_CONCILIACION": fundamento,
                "TIENE_DETALLE_CANONICO": "SI" if not det.empty else "NO",
                "REGISTROS_DETALLE": len(det),
                "ASIGNATURAS_UNICAS_CODRAMO": det["CODRAMO"].nunique() if not det.empty else 0,
                "NIVELES_OBSERVADOS": ordered_levels(det["NIVEL"]) if not det.empty else "",
                "NIVEL_MIN": min([as_int(x) for x in det["NIVEL"]]) if not det.empty else "",
                "NIVEL_MAX": max([as_int(x) for x in det["NIVEL"]]) if not det.empty else "",
                "ESTADO_CIERRE_CONCILIACION": c0.get("ESTADO_CIERRE", ""),
                "ORIGEN_ESTADO_CIERRE": c0.get("ORIGEN_ESTADO_CIERRE", ""),
                "DICTAMEN_RELACION": (
                    "OK_ESTRUCTURADO"
                    if codp_struct and not det.empty
                    else "BLOQUEO_SIN_CODPESTUD_ESTRUCTURADO_AUNQUE_HAY_FUNDAMENTO_TECNICO"
                    if fundamento
                    else "BLOQUEO_SIN_RELACION_CODPESTUD"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_semantic_evidence(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = [
        {
            "evidencia": "Manual Avance Curricular SIES 2026",
            "tipo": "A. Regla oficial",
            "hallazgo": "Define DURACION_ESTUDIOS en semestres y las unidades por anio del plan, pero no define la columna raw NIVEL de la fuente institucional.",
            "permite_conversion": "NO",
            "fuente": str(MANUAL),
        },
        {
            "evidencia": "Fuente canonica 01_CANONICO_TODOS_PLANES.tsv",
            "tipo": "B. Dato observado",
            "hallazgo": "NIVEL aparece junto a CODPESTUD, CODRAMO, NOMBRE y trazabilidad de malla; globalmente toma valores 1 a 20.",
            "permite_conversion": "NO_POR_SI_SOLO",
            "fuente": str(CANONICO),
        },
        {
            "evidencia": "Investigacion semantica NIVEL",
            "tipo": "B/C. Dato observado + implementacion tecnica revisada",
            "hallazgo": "Conclusion global NIVEL_CURRICULAR_SIN_EQUIVALENCIA; no hay definicion explicita, formulas, comentarios, nombres definidos ni origen tecnico encontrado.",
            "permite_conversion": "NO",
            "fuente": str(SEMANTICA_GLOBAL),
        },
        {
            "evidencia": "Busqueda de fuente semestre/anio",
            "tipo": "C/E. Auditoria tecnica + pendiente",
            "hallazgo": "Sin fuentes institucionales aptas ni parciales; requiere solicitud institucional.",
            "permite_conversion": "NO",
            "fuente": str(BUSQUEDA_CONCLUSION),
        },
        {
            "evidencia": "Validacion equivalencia NIVEL->anio 20260701_225538",
            "tipo": "C. Implementacion tecnica candidata",
            "hallazgo": "Prueba regla AÑO_CURRICULAR=TECHO(NIVEL/2) usando gob_mu_niv_aca.tsv de Matricula Unificada; no es regla oficial de Avance ni cubre todos los planes objetivo.",
            "permite_conversion": "NO_SIN_CONFIRMACION_FUNCIONAL_AVANCE",
            "fuente": str(VALID_EQ_EQUIV),
        },
        {
            "evidencia": "Regla critica transversal MU/Avance",
            "tipo": "D/E. Decision interna/pendiente",
            "hallazgo": "Una regla de Matricula Unificada no aplica automaticamente a Avance Curricular.",
            "permite_conversion": "NO_AUTOMATICO",
            "fuente": str(GOB_MU_NIV_ACA),
        },
    ]
    return pd.DataFrame(rows)


def build_conversion_candidate(valid_eq: pd.DataFrame) -> pd.DataFrame:
    if valid_eq.empty:
        valid_eq = pd.DataFrame(
            {
                "NIVEL": [str(i) for i in range(1, 21)],
                "ANIO_CURRICULAR": [str(math.ceil(i / 2)) for i in range(1, 21)],
                "REGLA": ["AÑO_CURRICULAR = TECHO(NIVEL / 2)"] * 20,
                "RESPALDO": ["Regla candidata; requiere confirmacion funcional Avance"] * 20,
            }
        )
    out = valid_eq.copy()
    out["USO_AUTORIZADO_EN_CSV"] = "NO"
    out["CONDICION_PARA_AUTORIZAR"] = (
        "Confirmacion documental/funcional de Docencia o Registro Curricular de que NIVEL representa semestre curricular del plan para Avance 5810."
    )
    out["VALIDACIONES_OBLIGATORIAS_SI_SE_APRUEBA"] = (
        "43/43 con CODPESTUD; deduplicar por CODRAMO/RAMOEQUIV; total=suma anios; cero unidades despues de techo(DURACION_ESTUDIOS/2); justificar planes sin detalle."
    )
    return out


def build_validations(relationship: pd.DataFrame, dist: pd.DataFrame) -> pd.DataFrame:
    total = len(relationship)
    with_detail = int((relationship["TIENE_DETALLE_CANONICO"] == "SI").sum())
    no_detail = total - with_detail
    outside = int((dist["VALIDACION_DURACION"].astype(str) != "OK").sum()) if not dist.empty else total
    total_ok = int((dist["VALIDACION_TOTAL"].astype(str) == "OK").sum()) if not dist.empty else 0
    rows = [
        ("43/43 carreras con detalle o justificacion formal", "43", f"{with_detail} con detalle estructurado; {no_detail} sin CODPESTUD estructurado", "BLOQUEADO"),
        ("NIVEL interpretado de forma trazable", "SI", "NO; sin definicion explicita ni fuente institucional apta", "BLOQUEADO"),
        ("TOTAL_UNIDADES_MEDIDA calculable desde detalle", "SI", "Parcial: calculable para 40 con detalle, no para 3 sin enlace estructurado", "BLOQUEADO"),
        ("UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO compatibles con DURACION_ESTUDIOS", "SI", "NO bajo conversion candidata; hay unidades fuera de duracion", "BLOQUEADO"),
        ("Cero unidades fuera de techo(DURACION_ESTUDIOS/2)", "0", f"{outside} filas con validacion duracion distinta de OK en diagnostico", "BLOQUEADO"),
        ("TOTAL_UNIDADES_MEDIDA = suma anios", "43/43", f"{total_ok}/43 en reconstruccion diagnostica", "NO_CIERRA_ETAPA"),
        ("Sin PROMEDIOS como fuente estructural", "SI", "SI; no se usa PROMEDIOS", "OK"),
        ("Sin matricula 5809 como fuente estructural", "SI", "SI; diagnostico 109 la penaliza/no usa como estructura", "OK"),
        ("Sin matriz agregada rechazada por SIES como fuente final", "SI", "SI; H106 solo queda como evidencia de rechazo", "OK"),
    ]
    return pd.DataFrame(rows, columns=["validacion", "esperado", "observado", "estado"])


def build_dictamen(relationship: pd.DataFrame) -> pd.DataFrame:
    no_detail = int((relationship["TIENE_DETALLE_CANONICO"] == "NO").sum())
    return pd.DataFrame(
        [
            {"campo": "Proceso", "valor": "Avance Curricular SIES 2026"},
            {"campo": "Subproyecto", "valor": "Carreras Avance Curricular 2026 / ID SIES 16769"},
            {"campo": "Diagnostico base", "valor": str(DIAG109)},
            {"campo": "Dictamen", "valor": "BLOQUEADO_CON_PENDIENTES"},
            {"campo": "Declaracion carga", "valor": "NO_LISTO_PARA_CARGA"},
            {"campo": "CSV final generado", "valor": "NO"},
            {"campo": "SIES_READY generado", "valor": "NO"},
            {"campo": "Fuentes originales modificadas", "valor": "NO"},
            {"campo": "Fuente canonica usada", "valor": str(CANONICO)},
            {"campo": "Cruce CODIGO_UNICO-CODPESTUD", "valor": str(CONC43)},
            {"campo": "Carreras con detalle canonico estructurado", "valor": str(43 - no_detail)},
            {"campo": "Carreras sin detalle canonico estructurado", "valor": str(no_detail)},
            {
                "campo": "Conclusion NIVEL",
                "valor": "NIVEL es dato observado de malla/plan, pero no queda cerrado como semestre ni anio curricular para Avance 5810.",
            },
            {
                "campo": "Proximo paso",
                "valor": "Enviar requerimiento a Docencia/Registro Curricular y no generar CSV hasta recibir confirmacion documental/funcional.",
            },
        ]
    )


def build_correo(relationship: pd.DataFrame) -> str:
    no_detail = relationship[relationship["TIENE_DETALLE_CANONICO"] == "NO"].copy()
    no_detail_rows = "\n".join(
        f"- {r.CODIGO_UNICO}: {r.NOMBRE_CARRERA}, jornada {r.JORNADA}, version {r.VERSION}, duracion {r.DURACION_ESTUDIOS} semestres. "
        f"Plan mencionado en fundamento tecnico/conciliacion: {r.PLAN_REFERIDO_TEXTO_CONCILIACION or 'sin CODPESTUD estructurado'}."
        for r in no_detail.itertuples(index=False)
    )
    return f"""# Borrador correo - cierre pendiente NIVEL / Carreras Avance Curricular 2026

Asunto: Confirmacion requerida - ubicacion curricular por NIVEL para Carreras Avance Curricular SIES 2026

Estimadas/os,

Junto con saludar, en el marco del proceso Avance Curricular SIES 2026, carga Carreras ID SIES 16769, necesitamos confirmar la interpretacion funcional de la columna `NIVEL` de la fuente institucional de planes de estudio utilizada para preparar la distribucion anual de unidades del archivo 5810.

La fuente revisada contiene asignaturas por plan (`CODPESTUD`, `CODRAMO`, nombre de asignatura, creditos y `NIVEL`), pero las auditorias locales no encontraron una definicion explicita que indique si `NIVEL` representa semestre curricular, anio curricular, secuencia interna, nivel academico u otra codificacion. Por esta razon no podemos usar automaticamente la conversion `NIVEL 1-2 = anio 1`, `NIVEL 3-4 = anio 2`, etc.

Solicitamos confirmar documental o funcionalmente:

1. Que significa exactamente `NIVEL` en la fuente de planes de estudio.
2. Si `NIVEL` corresponde a semestre curricular del plan para las mallas de Avance Curricular 2025.
3. Si se autoriza, para el archivo Carreras Avance Curricular 2026, convertir `NIVEL` a anio SIES mediante `ANIO = techo(NIVEL / 2)`.
4. Como deben tratarse asignaturas en niveles que, bajo esa conversion, quedan fuera de `techo(DURACION_ESTUDIOS / 2)`.
5. Si existen actividades de practica, titulacion, examen final, continuidad, electivos u otra categoria que deban incluirse o excluirse de `TOTAL_UNIDADES_MEDIDA` y de `UNIDADES_1ER_ANIO` a `UNIDADES_7MO_ANIO`.
6. Confirmar o corregir el plan institucional (`CODPESTUD`) de las siguientes carreras que no tienen enlace estructurado en la conciliacion usada por el diagnostico:

{no_detail_rows}

Idealmente necesitamos una tabla o confirmacion con estos campos:

- CODIGO_UNICO.
- CODCARR.
- CODPESTUD.
- Codigo de asignatura/ramo.
- Nombre de asignatura.
- Creditos o unidad de medida.
- Semestre curricular y/o anio curricular dentro del plan.
- Definicion del campo semestre/anio o de `NIVEL`.
- Vigencia del plan para el anio academico 2025.
- Fuente/sistema de origen y fecha de extraccion.

Mientras no contemos con esta confirmacion, el archivo Carreras Avance Curricular 2026 queda BLOQUEADO_CON_PENDIENTES y no se generara CSV de carga ni SIES_READY.

Muchas gracias.
"""


def write_report(
    path: Path,
    dictamen: pd.DataFrame,
    relationship: pd.DataFrame,
    canon_columns: pd.DataFrame,
    semantic: pd.DataFrame,
    validations: pd.DataFrame,
    correo_path: Path,
) -> None:
    no_detail = relationship[relationship["TIENE_DETALLE_CANONICO"] == "NO"]
    levels_summary = relationship[["CODIGO_UNICO", "NOMBRE_CARRERA", "CODPESTUD_ESTRUCTURADO_CONCILIACION", "TIENE_DETALLE_CANONICO", "NIVELES_OBSERVADOS", "NIVEL_MAX"]]
    no_detail_md = markdown_table(
        no_detail[
            [
                "CODIGO_UNICO",
                "NOMBRE_CARRERA",
                "JORNADA",
                "VERSION",
                "DURACION_ESTUDIOS",
                "PLAN_REFERIDO_TEXTO_CONCILIACION",
                "FUNDAMENTO_TECNICO_CONCILIACION",
            ]
        ]
    )
    validations_md = markdown_table(validations)
    levels_md = markdown_table(levels_summary)
    text = f"""# Cierre funcional de NIVEL y periodizacion - Carreras Avance Curricular 2026

## Dictamen

**BLOQUEADO_CON_PENDIENTES / NO_LISTO_PARA_CARGA.**

No se genero CSV final, no se corrigieron datos, no se modificaron fuentes originales y no se genero SIES_READY.

## A. Regla oficial

El instructivo oficial de Avance Curricular SIES 2026 define la carga Carreras ID 16769, la duracion de estudios en semestres y los campos `TOTAL_UNIDADES_MEDIDA` y `UNIDADES_1ER_ANIO` a `UNIDADES_7MO_ANIO` como distribucion anual del plan. El manual no define la columna raw `NIVEL` de la fuente institucional de planes.

## B. Dato observado

Fuente canonica usada:

`{CANONICO}`

Columnas principales detectadas: {", ".join(canon_columns["columna"].head(22).tolist())}.

La relacion `CODIGO_UNICO -> CODPESTUD` se toma desde:

`{CONC43}`

El diagnostico identifica 40/43 carreras con detalle canonico estructurado mediante `CODPESTUD` y 3/43 sin enlace estructurado. Las 3 carreras son:

{no_detail_md}

En la fuente canonica completa `NIVEL` toma valores 1 a 20. En las 40 carreras con detalle estructurado del diagnostico 109 se observan niveles hasta 12, 7, 6 o 5 segun el plan/carrera.

## C. Implementacion tecnica posible

Existe una conversion tecnica candidata:

`ANIO_CURRICULAR = techo(NIVEL / 2)`.

Pero esa prueba usa como respaldo semantico una gobernanza de Matricula Unificada (`gob_mu_niv_aca.tsv`) y no una regla oficial/documental de Avance Curricular Carreras. Por tanto puede quedar como escenario de validacion, no como regla aplicable al CSV.

## D. Decision interna previa

El diagnostico 109 excluye PROMEDIOS, no usa matricula 5809 como fuente estructural y no reutiliza la matriz agregada H106 como fuente final porque fue rechazada por SIES con unidades fuera de duracion.

## E. Pendiente o bloqueo

No existe evidencia suficiente para cerrar que `NIVEL` sea semestre, anio o una escala temporal aplicable a `UNIDADES_1ER_ANIO` a `UNIDADES_7MO_ANIO`. Las auditorias locales concluyen `NIVEL_CURRICULAR_SIN_EQUIVALENCIA` y `REQUIERE_SOLICITUD_INSTITUCIONAL`.

## Validaciones antes de CSV

{validations_md}

## Tabla resumida por carrera

{levels_md}

## Requerimiento funcional

Queda redactado el correo/pregunta exacta para Docencia o Registro Curricular en:

`{correo_path}`

## Conclusion

No se puede declarar `APTO_PARA_GENERAR_CSV`. La salida correcta de esta etapa es **BLOQUEADO_CON_PENDIENTES** hasta recibir una confirmacion documental o funcional de la semantica de `NIVEL`, la periodizacion anual por plan y el enlace formal de las 3 carreras sin `CODPESTUD` estructurado.
"""
    path.write_text(text, encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(sin datos)"
    work = df.fillna("").astype(str)
    cols = list(work.columns)
    lines = []
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in work.iterrows():
        vals = [str(row[col]).replace("|", "/").replace("\n", " ") for col in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def to_excel(writer: pd.ExcelWriter, df: pd.DataFrame, sheet: str) -> None:
    out = df.copy()
    if out.empty:
        out = pd.DataFrame([{"sin_datos": ""}])
    name = sheet[:31]
    out.to_excel(writer, sheet_name=name, index=False)
    ws = writer.book[name]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col_cells in ws.columns:
        width = min(max(len(str(col_cells[0].value or "")) + 2, 12), 60)
        ws.column_dimensions[col_cells[0].column_letter].width = width


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data = build_context()
    canon_cols = build_canon_columns(data["canon"])
    relationship = build_relationship(data["prec"], data["conv"], data["conc"])
    semantic = build_semantic_evidence(data)
    conversion = build_conversion_candidate(data["valid_eq"])
    validations = build_validations(relationship, data["dist"])
    dictamen = build_dictamen(relationship)
    correo = build_correo(relationship)

    excel_out = OUT / "CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769.xlsx"
    informe_out = OUT / "INFORME_CIERRE_FUNCIONAL_NIVEL_PERIODIZACION_CARRERAS_16769.md"
    correo_out = OUT / "BORRADOR_CORREO_DOCENCIA_REGISTRO_CURRICULAR_NIVEL_16769.md"
    manifest_out = OUT / "manifest_cierre_funcional_nivel_periodizacion_carreras_16769.json"
    script_out = OUT / "cierre_funcional_nivel_periodizacion_carreras_16769.py"

    correo_out.write_text(correo, encoding="utf-8")
    write_report(informe_out, dictamen, relationship, canon_cols, semantic, validations, correo_out)

    fuentes = [
        DIAG_XLSX,
        DIAG_MD,
        DIAG_MANIFEST,
        MANUAL,
        PRECARGA,
        CANONICO,
        CONC43,
        SEMANTICA_RESUMEN,
        SEMANTICA_GLOBAL,
        SEMANTICA_PLAN,
        HIPOTESIS,
        FORMULAS_COMENTARIOS,
        BUSQUEDA_CONCLUSION,
        FUENTE_FALTANTE,
        VALID_EQ_MANIFEST,
        VALID_EQ_EQUIV,
        VALID_EQ_VALIDACIONES,
        GOB_MU_NIV_ACA,
    ]
    fuentes_df = pd.DataFrame(
        [{"ruta": str(p), "existe": p.exists(), "sha256": sha256(p)} for p in fuentes]
    )

    with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
        to_excel(writer, dictamen, "00_DICTAMEN")
        to_excel(writer, fuentes_df, "01_FUENTES")
        to_excel(writer, data["reglas"], "02_REGLA_OFICIAL_MANUAL")
        to_excel(writer, canon_cols, "03_COLUMNAS_CANONICO")
        to_excel(writer, relationship, "04_CU_CODPESTUD_NIVELES")
        to_excel(writer, relationship[relationship["TIENE_DETALLE_CANONICO"] == "NO"], "05_3_SIN_DETALLE")
        to_excel(writer, semantic, "06_EVIDENCIA_SEMANTICA")
        to_excel(writer, data["sem_global"], "07_CONCLUSION_SEM_GLOBAL")
        to_excel(writer, data["sem_plan"], "08_CONCLUSION_SEM_PLAN")
        to_excel(writer, data["hip"], "09_HIPOTESIS_NIVEL")
        to_excel(writer, data["busq"], "10_BUSQUEDA_FUENTE")
        to_excel(writer, conversion, "11_REGLA_CANDIDATA_NO_APLICAR")
        to_excel(writer, validations, "12_VALIDACIONES_ANTES_CSV")
        to_excel(writer, pd.DataFrame([{"correo": correo}]), "13_CORREO")

    manifest = {
        "proceso": "Avance Curricular SIES 2026",
        "subproyecto": "Carreras Avance Curricular 2026 / ID SIES 16769",
        "hito": "110_cierre_funcional_nivel_periodizacion_carreras_16769",
        "fecha": TS,
        "dictamen": "BLOQUEADO_CON_PENDIENTES",
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "csv_final_generado": "NO",
        "sies_ready_generado": "NO",
        "fuentes_originales_modificadas": "NO",
        "salidas": {
            "excel": str(excel_out),
            "informe": str(informe_out),
            "correo": str(correo_out),
            "manifest": str(manifest_out),
            "script": str(script_out),
        },
        "fuentes": fuentes_df.to_dict(orient="records"),
    }
    manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(Path(__file__).resolve(), script_out)

    print("CIERRE FUNCIONAL NIVEL / PERIODIZACION CARRERAS 16769 — GENERADO")
    print("Fuentes originales modificadas: NO")
    print("CSV final generado: NO")
    print("SIES_READY generado: NO")
    print("Declaracion carga: NO_LISTO_PARA_CARGA")
    print("Dictamen: BLOQUEADO_CON_PENDIENTES")
    print("\n3 CARRERAS SIN DETALLE ESTRUCTURADO")
    print(relationship[relationship["TIENE_DETALLE_CANONICO"] == "NO"][["CODIGO_UNICO", "NOMBRE_CARRERA", "JORNADA", "VERSION", "DURACION_ESTUDIOS", "PLAN_REFERIDO_TEXTO_CONCILIACION"]].to_string(index=False))
    print("\nVALIDACIONES")
    print(validations.to_string(index=False))
    print("\nARCHIVOS")
    print(f"Excel: {excel_out}")
    print(f"Informe: {informe_out}")
    print(f"Correo: {correo_out}")
    print(f"Manifest: {manifest_out}")
    print(f"Script: {script_out}")


if __name__ == "__main__":
    main()

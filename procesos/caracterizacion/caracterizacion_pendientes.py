from __future__ import annotations

import unicodedata
from typing import Any

import pandas as pd


RESPUESTA_COMPLETA = "SI"
RESPUESTA_INCOMPLETA = "INCOMPLETO"
RESPUESTA_NO = "NO"
ESTADOS_GOBERNADOS = {RESPUESTA_COMPLETA, RESPUESTA_INCOMPLETA, RESPUESTA_NO}


def normalizar_estado_respuesta(valor: Any) -> str:
    """Normaliza estados de respuesta sin convertir desconocidos en completos."""
    if valor is None or pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.upper().strip()


def _auditar_pendientes_encuesta(
    df: pd.DataFrame,
    seleccion: pd.DataFrame,
    estados_norm: pd.Series,
    columna_llave: str | None = None,
) -> dict[str, int | str]:
    respuestas_completas = int(estados_norm.eq(RESPUESTA_COMPLETA).sum())
    respuestas_incompletas = int(estados_norm.eq(RESPUESTA_INCOMPLETA).sum())
    sin_respuesta = int(estados_norm.isin({"", RESPUESTA_NO}).sum())
    otros_estados = int(
        (~estados_norm.isin({"", *ESTADOS_GOBERNADOS})).sum()
    )
    vigentes_elegibles = int(len(df))
    pendientes_exportados = int(len(seleccion))
    pendientes_esperados = vigentes_elegibles

    total_componentes = (
        respuestas_completas
        + respuestas_incompletas
        + sin_respuesta
        + otros_estados
    )
    if total_componentes != vigentes_elegibles:
        raise RuntimeError(
            "[Bloque 4] Auditoria de estados no cuadra: "
            f"vigentes={vigentes_elegibles}; componentes={total_componentes}."
        )

    if pendientes_exportados != pendientes_esperados:
        raise RuntimeError(
            "[Bloque 4] Pendientes exportados no cuadran: "
            f"pendientes={pendientes_exportados}; esperados={pendientes_esperados}."
        )

    estados_pendientes = estados_norm.loc[seleccion.index]
    completas_en_pendientes = int(estados_pendientes.eq(RESPUESTA_COMPLETA).sum())
    if completas_en_pendientes != respuestas_completas:
        raise RuntimeError(
            "[Bloque 4] La salida de pendientes no conserva todas las respuestas completas."
        )

    pendientes_fuera_de_vigentes = 0
    if columna_llave and columna_llave in df.columns and columna_llave in seleccion.columns:
        llaves_vigentes = set(df[columna_llave].fillna("").astype(str))
        llaves_pendientes = set(seleccion[columna_llave].fillna("").astype(str))
        pendientes_fuera_de_vigentes = int(
            len(llaves_pendientes - llaves_vigentes)
        )
        if pendientes_fuera_de_vigentes != 0:
            raise RuntimeError(
                "[Bloque 4] Existen pendientes fuera del universo vigente."
            )

    estados_desconocidos = sorted(
        estado for estado in estados_norm.unique().tolist()
        if estado and estado not in ESTADOS_GOBERNADOS
    )

    return {
        "VIGENTES_ELEGIBLES": vigentes_elegibles,
        "RESPUESTAS_COMPLETAS": respuestas_completas,
        "RESPUESTAS_INCOMPLETAS": respuestas_incompletas,
        "SIN_RESPUESTA": sin_respuesta,
        "OTROS_ESTADOS": otros_estados,
        "PENDIENTES_ESPERADOS": pendientes_esperados,
        "PENDIENTES_EXPORTADOS": pendientes_exportados,
        "RESPUESTAS_COMPLETAS_EN_PENDIENTES": completas_en_pendientes,
        "PENDIENTES_FUERA_DE_VIGENTES": pendientes_fuera_de_vigentes,
        "ESTADOS_DESCONOCIDOS": ",".join(estados_desconocidos),
    }


def seleccionar_pendientes_encuesta(
    df: pd.DataFrame,
    columna_respuesta: str = "Responden",
    *,
    columna_llave: str | None = None,
    devolver_auditoria: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, int | str]]:
    """Devuelve el universo vigente para el archivo Estudiantes_pendientes.

    En este proceso el archivo conserva todos los vigentes, incluyendo SI,
    INCOMPLETO, NO, vacios y estados desconocidos. La columna Responden
    permite distinguir su situacion.
    """
    if columna_respuesta not in df.columns:
        raise RuntimeError(
            f"[Bloque 4] Falta columna requerida: {columna_respuesta}"
        )

    estados_norm = df[columna_respuesta].map(normalizar_estado_respuesta)
    seleccion = df.copy()

    if not devolver_auditoria:
        return seleccion

    auditoria = _auditar_pendientes_encuesta(
        df,
        seleccion,
        estados_norm,
        columna_llave=columna_llave,
    )
    return seleccion, auditoria

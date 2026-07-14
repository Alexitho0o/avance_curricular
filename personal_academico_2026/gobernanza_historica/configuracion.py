"""Configuracion explicita de fuentes gobernadas por anio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .descubrimiento_fuentes import normalize_text


TRANSFORMER_VERSION = "gobernanza_historica_fase_1.0.0"


@dataclass(frozen=True)
class ApprovedSourceRule:
    """Regla explicita para fijar una fuente anual aprobada."""

    anio: int
    filename: str
    estado: str
    nivel_confianza: str
    evidencia_pes: str
    responsable: str
    observaciones: str


def approved_source_rules(responsable: str) -> list[ApprovedSourceRule]:
    """Define la configuracion permanente inicial de fuentes por anio."""

    return [
        ApprovedSourceRule(
            anio=2022,
            filename="14-06-2022_17-11-37_Personal_Académico_en_Institucion_2022 (oficial).csv",
            estado="OFICIAL_CONFIRMADA_POR_NOMBRE_Y_ESTRUCTURA",
            nivel_confianza="ALTA",
            evidencia_pes="Nombre contiene oficial; carpeta anual Enviados; estructura academica detectable.",
            responsable=responsable,
            observaciones="Fuente anual fijada por configuracion Fase 1; no seleccionada por fecha ni filas.",
        ),
        ApprovedSourceRule(
            anio=2023,
            filename="PAC_IP_CIISA_2023.xlsx",
            estado="CANDIDATA_GOBERNADA_PENDIENTE_EVIDENCIA_FINAL",
            nivel_confianza="MEDIA",
            evidencia_pes="Archivo anual tabular con encabezados academicos compatibles en carpeta Enviados.",
            responsable=responsable,
            observaciones="Fuente congelada para reproducibilidad; requiere validacion institucional de envio final.",
        ),
        ApprovedSourceRule(
            anio=2024,
            filename="IPSSPAC2024F.xlsx",
            estado="OFICIAL_CONFIRMADA_POR_ANTECEDENTE_USUARIO",
            nivel_confianza="ALTA",
            evidencia_pes="Antecedente confirmado por instruccion de Fase 1: fuente oficial 2024.",
            responsable=responsable,
            observaciones="No se vuelve a seleccionar mediante busqueda heuristica; queda fijada por manifiesto.",
        ),
        ApprovedSourceRule(
            anio=2025,
            filename="Carga_IPSSvf.csv",
            estado="CANDIDATA_GOBERNADA_PENDIENTE_EVIDENCIA_FINAL",
            nivel_confianza="MEDIA_ALTA",
            evidencia_pes="Archivo de carga VF en carpeta anual Enviados con estructura academica compatible.",
            responsable=responsable,
            observaciones="Fuente congelada para reproducibilidad; requiere evidencia institucional final de carga.",
        ),
        ApprovedSourceRule(
            anio=2026,
            filename="personal_academico_en_institucion_2026_PES_READY.csv",
            estado="OFICIAL_PROBABLE_PES_READY",
            nivel_confianza="MEDIA_ALTA",
            evidencia_pes="Archivo PES_READY en raiz anual 2026, no backup, con estructura academica compatible.",
            responsable=responsable,
            observaciones="Fuente congelada para reproducibilidad; no se integra al flujo PES en esta fase.",
        ),
    ]


def find_rule_path(root: Path, rule: ApprovedSourceRule) -> Path | None:
    """Busca la ruta exacta esperada tolerando diferencias de composicion Unicode."""

    target = normalize_text(rule.filename)
    matches = [path for path in root.rglob("*") if path.is_file() and normalize_text(path.name) == target]
    if rule.anio == 2026:
        matches = [path for path in matches if "BACKUP" not in normalize_text(path.as_posix()) and "/OTROS/" not in normalize_text(path.as_posix())]
    if not matches:
        return None
    return sorted(matches, key=lambda item: len(item.parts))[0]


def build_approved_sources(root: Path, inventory: pd.DataFrame, responsable: str) -> pd.DataFrame:
    """Construye la configuracion explicita de fuentes aprobadas por anio."""

    rows: list[dict[str, object]] = []
    for rule in approved_source_rules(responsable):
        path = find_rule_path(root, rule)
        inventory_row = pd.DataFrame()
        if path is not None and not inventory.empty:
            inventory_row = inventory[inventory["ruta"].eq(str(path))]
        row = {
            "anio": rule.anio,
            "archivo": rule.filename,
            "ruta_original": "" if path is None else str(path),
            "sha256": "" if inventory_row.empty else str(inventory_row.iloc[0]["sha256"]),
            "estado": rule.estado,
            "version": "1",
            "fecha_congelamiento": "",
            "nivel_confianza": rule.nivel_confianza,
            "evidencia_pes": rule.evidencia_pes,
            "responsable": rule.responsable,
            "observaciones": rule.observaciones if path is not None else f"NO_ENCONTRADA: {rule.observaciones}",
            "fuente_id_inventario": "" if inventory_row.empty else str(inventory_row.iloc[0]["fuente_id"]),
            "hoja_seleccionada": "" if inventory_row.empty else str(inventory_row.iloc[0].get("hoja_seleccionada", "")),
            "encoding": "" if inventory_row.empty else str(inventory_row.iloc[0].get("encoding", "")),
            "delimitador": "" if inventory_row.empty else str(inventory_row.iloc[0].get("delimitador", "")),
            "filas": 0 if inventory_row.empty else int(inventory_row.iloc[0]["cantidad_filas"]),
            "columnas": 0 if inventory_row.empty else int(inventory_row.iloc[0]["cantidad_columnas"]),
            "personas_vigentes": 0 if inventory_row.empty else int(inventory_row.iloc[0]["personas_vigentes"]),
            "personas_no_vigentes": 0 if inventory_row.empty else int(inventory_row.iloc[0]["personas_no_vigentes"]),
            "duplicados": 0 if inventory_row.empty else int(inventory_row.iloc[0]["duplicados"]),
        }
        rows.append(row)
    return pd.DataFrame(rows)

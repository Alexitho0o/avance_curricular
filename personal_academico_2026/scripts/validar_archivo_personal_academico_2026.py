#!/usr/bin/env python3
"""CLI de validacion base para Personal Academico SIES 2026."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from config_personal_academico_2026 import (  # noqa: E402
    AUDITORIAS_DIR,
    COLUMNAS_OBLIGATORIAS_BASICAS_PREVENTIVAS,
    DELIMITADOR_ESTRUCTURA_OBSERVADO,
    ENCODING_DEFAULT,
    columnas_fecha_por_tipo,
    columnas_horas_por_tipo,
    columnas_por_tipo,
)
from validaciones_personal_academico_2026 import (  # noqa: E402
    construir_reporte_validacion,
    validar_campos_obligatorios_basicos,
    validar_columnas_exactas,
    validar_duplicados_documento,
    validar_dv_documentos_chilenos,
    validar_fechas_formato,
    validar_horas_numericas,
    validar_sin_columnas_adicionales,
    validar_valores_basicos_preventivos,
)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ruta_auditoria_default(tipo: str, input_path: Path) -> Path:
    AUDITORIAS_DIR.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem.replace(" ", "_")
    return AUDITORIAS_DIR / f"auditoria_validacion_{tipo}_{stem}_{_timestamp()}.csv"


def leer_csv(path: Path, delimitador: str, encoding: str) -> pd.DataFrame:
    if delimitador.lower() == "tab":
        delimitador = "\t"
    return pd.read_csv(path, sep=delimitador, encoding=encoding, dtype=str, keep_default_na=False)


def evaluar_estado(reporte: pd.DataFrame, estructura_ok: bool) -> str:
    errores = int((reporte["severidad"] == "ERROR").sum())
    advertencias = int((reporte["severidad"] == "ADVERTENCIA").sum())
    pendientes = int((reporte["fuente_regla"] == "PENDIENTE_CONFIRMACION").sum())
    if not estructura_ok or errores > 0:
        return "RECHAZADO"
    if pendientes > 0:
        return "PENDIENTE_CONFIRMACION"
    if advertencias > 0:
        return "APROBADO_CON_ADVERTENCIAS"
    return "APROBADO_CON_ADVERTENCIAS"


def validar_archivo(args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, object]]:
    input_path = Path(args.input)
    columnas_esperadas = columnas_por_tipo(args.tipo)
    df = leer_csv(input_path, args.delimitador_entrada, args.encoding)

    resultado_columnas = validar_columnas_exactas(df, columnas_esperadas)
    resultados = [
        resultado_columnas,
        validar_sin_columnas_adicionales(df, columnas_esperadas),
    ]

    estructura_ok = bool(resultado_columnas["ok"])
    if estructura_ok:
        resultados.extend(
            [
                validar_duplicados_documento(df),
                validar_dv_documentos_chilenos(df),
                validar_fechas_formato(df, columnas_fecha_por_tipo(args.tipo)),
                validar_horas_numericas(df, columnas_horas_por_tipo(args.tipo)),
                validar_campos_obligatorios_basicos(
                    df, COLUMNAS_OBLIGATORIAS_BASICAS_PREVENTIVAS
                ),
                validar_valores_basicos_preventivos(df),
            ]
        )

    reporte = construir_reporte_validacion(input_path.name, args.tipo, resultados)
    resumen = {
        "filas": len(df),
        "columnas": len(df.columns),
        "estructura_ok": estructura_ok,
        "errores": int((reporte["severidad"] == "ERROR").sum()),
        "advertencias": int((reporte["severidad"] == "ADVERTENCIA").sum()),
        "duplicados": int(
            (
                (reporte["regla"] == "duplicados_documento")
                & (reporte["severidad"] == "ERROR")
            ).sum()
        ),
        "estado_final": evaluar_estado(reporte, estructura_ok),
    }
    return reporte, resumen


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida archivos de trabajo para Personal Academico SIES 2026."
    )
    parser.add_argument("--tipo", choices=["en_institucion", "fuera_institucion"], required=True)
    parser.add_argument("--input", required=True, help="Ruta del archivo CSV de entrada.")
    parser.add_argument("--output-auditoria", default=None, help="Ruta opcional de auditoria CSV.")
    parser.add_argument("--delimitador-entrada", default=DELIMITADOR_ESTRUCTURA_OBSERVADO)
    parser.add_argument("--encoding", default=ENCODING_DEFAULT)
    parser.add_argument("--strict", action="store_true", help="Retorna codigo 1 ante rechazo.")
    parser.add_argument(
        "--export-normalizado",
        default=None,
        help="Reservado para fase futura. No exporta final PES en esta fase.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: no existe archivo de entrada: {input_path}", file=sys.stderr)
        return 2

    reporte, resumen = validar_archivo(args)
    auditoria_path = (
        Path(args.output_auditoria)
        if args.output_auditoria
        else _ruta_auditoria_default(args.tipo, input_path)
    )
    auditoria_path.parent.mkdir(parents=True, exist_ok=True)
    reporte.to_csv(auditoria_path, index=False, encoding=args.encoding)

    if args.export_normalizado:
        print(
            "ADVERTENCIA: --export-normalizado esta reservado para fase futura; "
            "no se genero archivo final PES/SIES."
        )

    print("Resumen validacion Personal Academico SIES 2026")
    print(f"tipo: {args.tipo}")
    print(f"archivo: {input_path}")
    print(f"total filas: {resumen['filas']}")
    print(f"total columnas: {resumen['columnas']}")
    print(f"errores criticos: {resumen['errores']}")
    print(f"advertencias: {resumen['advertencias']}")
    print(f"duplicados: {resumen['duplicados']}")
    print(f"auditoria: {auditoria_path}")
    print(f"estado final: {resumen['estado_final']}")

    if args.strict and resumen["estado_final"] == "RECHAZADO":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exportador controlado para Personal Academico SIES 2026.

Por defecto bloquea la exportacion final hasta contar con auditoria aprobada.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
import shutil
import sys

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from config_personal_academico_2026 import (  # noqa: E402
    AUDITORIAS_DIR,
    DELIMITADOR_ESTRUCTURA_OBSERVADO,
    DELIMITADOR_INSTRUCTIVO_DECLARADO,
    ENCODING_DEFAULT,
    EXPORTAR_CON_ENCABEZADO_DEFAULT,
    EXPORTAR_INDICE_DEFAULT,
    columnas_por_tipo,
)
from validaciones_personal_academico_2026 import (  # noqa: E402
    FUENTE_ESTRUCTURA,
    FUENTE_PENDIENTE,
    FUENTE_PREVENTIVA,
    construir_reporte_validacion,
    validar_columnas_exactas,
)
from transformaciones_pes_personal_academico_2026 import (  # noqa: E402
    detectar_registro_no_cargable,
    generar_auditoria_transformaciones,
    transformar_fila_para_pes,
)


MODULE_DIR = SCRIPT_DIR.parent
REPO_DIR = MODULE_DIR.parent
AUDITORIAS_EXPORTACION_DIR = MODULE_DIR / "auditorias/exportacion_controlada"
REPORTE_FASE_6 = MODULE_DIR / "docs/REPORTE_FASE_6_AJUSTES_EXPORTADOR_PES_REAL.md"
BITACORA_FASE_6 = MODULE_DIR / "bitacoras/BITACORA_FASE_6_AJUSTES_EXPORTADOR_PES_REAL.md"
REPORTE_FASE_7 = MODULE_DIR / "docs/REPORTE_FASE_7_REGLAS_PES_HORAS_Y_ESPECIALIDAD.md"
BITACORA_FASE_7 = MODULE_DIR / "bitacoras/BITACORA_FASE_7_REGLAS_PES_HORAS_Y_ESPECIALIDAD.md"
REPORTE_FASE_8 = MODULE_DIR / "docs/REPORTE_FASE_8_CORRECCION_NOMBRE_TITULO_A_Z.md"
BITACORA_FASE_8 = MODULE_DIR / "bitacoras/BITACORA_FASE_8_CORRECCION_NOMBRE_TITULO_A_Z.md"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _evento_exportacion(
    *,
    severidad: str,
    regla: str,
    estado: str,
    mensaje: str,
    fuente_regla: str,
    columna: str = "",
    valor: str = "",
) -> dict[str, object]:
    return {
        "validacion": "exportacion_controlada",
        "ok": severidad != "ERROR",
        "errores": [],
        "advertencias": [],
        "resumen": {},
        "eventos": [
            {
                "severidad": severidad,
                "regla": regla,
                "estado": estado,
                "columna": columna,
                "fila": "",
                "valor": valor,
                "mensaje": mensaje,
                "fuente_regla": fuente_regla,
            }
        ],
    }


def _auditoria_exportacion_default(tipo: str, output_path: Path) -> Path:
    AUDITORIAS_DIR.mkdir(parents=True, exist_ok=True)
    return AUDITORIAS_DIR / f"auditoria_exportacion_{tipo}_{output_path.stem}_{_timestamp()}.csv"


def str_a_bool(valor: str | bool) -> bool:
    if isinstance(valor, bool):
        return valor
    return valor.strip().lower() in {"1", "true", "si", "sí", "yes", "y"}


def normalizar_delimitador(valor: str) -> str:
    normalizado = valor.strip().lower()
    if normalizado == "tab":
        return "\t"
    if normalizado in {"punto_coma", "punto-y-coma", "semicolon"}:
        return ";"
    if normalizado in {"coma", "comma"}:
        return ","
    return valor


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_DIR))
    except ValueError:
        return str(path)


def _audit_path(prefix: str) -> Path:
    AUDITORIAS_EXPORTACION_DIR.mkdir(parents=True, exist_ok=True)
    return AUDITORIAS_EXPORTACION_DIR / f"{prefix}_{_timestamp()}.csv"


def _backup_if_exists(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"{path.stem}_{_timestamp()}{path.suffix}"
    shutil.copy2(path, backup)
    return backup


def _write_exclusion_audit(path: Path, eventos: list[dict[str, object]]) -> None:
    fields = [
        "timestamp",
        "tipo_evento",
        "severidad",
        "fila_origen",
        "motivo",
        "accion",
        "detalle",
        "fuente_regla",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(eventos)


def _write_reporte_fase_6(resumen: dict[str, object]) -> None:
    motivos = resumen.get("motivos_exclusion", {})
    motivos_txt = "\n".join(f"- {motivo}: {total}" for motivo, total in sorted(motivos.items())) or "- Sin exclusiones."
    contenido = f"""# Reporte Fase 6 - Ajustes Exportador PES Real

## Errores Observados En PES/SIES
- CSV con coma fue leido como 1 campo; para esta carga PES/SIES acepto separador punto y coma.
- Fechas `YYYY-MM-DD` fueron rechazadas; PES acepto fechas en `DD-MM-AAAA`.
- Reporte PES mostro problemas de codificacion con tildes.
- `COMUNA_MAYOR_FUNCION` vacia fue rechazada.
- Persisten rechazos por valores no disponibles en campos estructurados y horas con decimales largos.

## Ajustes Incorporados Al Codigo
- Delimitador final configurable y por defecto `punto_coma`.
- Encoding de salida configurable y por defecto `cp1252`.
- Fechas PES en `DD-MM-AAAA`.
- Normalizacion tecnica de exportacion: mayusculas, sin tildes, sin espacios dobles y sin separadores internos conflictivos.
- Completar `COMUNA_MAYOR_FUNCION` desde `COMUNA_PRINCIPAL_PROGRAMA` solo en exportacion.
- Modo explicito `--excluir-registros-no-cargables true`.
- Horas numericas a maximo 2 decimales.

## Base General
La base general original no fue modificada. Las transformaciones son solo de exportacion.

## Exclusiones
Las exclusiones se aplican solo si se usa `--excluir-registros-no-cargables true`.
{motivos_txt}

## Archivo Generado
- Salida modulo: {resumen.get('salida', '')}
- Copia Escritorio: {resumen.get('desktop_output', '') or 'No solicitada'}
- Filas exportadas: {resumen.get('filas_exportadas', 0)}
- Filas excluidas: {resumen.get('filas_excluidas', 0)}
- Delimitador: {resumen.get('delimitador_salida_label', '')}
- Encoding: {resumen.get('encoding_salida', '')}
- Encabezado: {'NO' if resumen.get('sin_encabezado') else 'SI'}

## Auditorias
- Transformaciones: {resumen.get('auditoria_transformaciones', '')}
- Exclusiones: {resumen.get('auditoria_exclusiones', '')}

Advertencia: no se deben hacer correcciones manuales directas sobre el CSV final sin reflejarlas en codigo y auditoria.
"""
    REPORTE_FASE_6.write_text(contenido, encoding="utf-8")


def _write_bitacora_fase_6(resumen: dict[str, object]) -> None:
    contenido = f"""# Bitacora Fase 6 - Ajustes Exportador PES Real

- Fecha/hora: {datetime.now().isoformat(timespec='seconds')}
- Rama: feature/personal-academico-base-preliminar-2026

## Archivos Creados
- {rel(REPORTE_FASE_6)}
- {rel(BITACORA_FASE_6)}
- {resumen.get('auditoria_transformaciones', '')}
- {resumen.get('auditoria_exclusiones', '')}
- {resumen.get('salida', '')}

## Archivos Modificados
- {rel(MODULE_DIR / 'scripts/exportar_personal_academico_2026.py')}
- {rel(MODULE_DIR / 'scripts/transformaciones_pes_personal_academico_2026.py')}

## Comandos Ejecutados
- `python3 -m py_compile personal_academico_2026/scripts/*.py`
- `python3 personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/candidatos_exportacion/base_general_en_institucion_SIN_PENDIENTE_FECHA_FUTURA_20260611_234029.tsv --delimitador-entrada tab`
- `python3 personal_academico_2026/scripts/exportar_personal_academico_2026.py --tipo en_institucion --input personal_academico_2026/data/base_general/candidatos_exportacion/base_general_en_institucion_SIN_PENDIENTE_FECHA_FUTURA_20260611_234029.tsv --output personal_academico_2026/resultados/personal_academico_en_institucion_2026_PES_READY_CANDIDATO_FILTRADO.csv --permitir-exportacion-final true --delimitador-salida punto_coma --encoding-salida cp1252 --formato-fecha-pes true --normalizar-texto-pes true --completar-comuna-mayor true --excluir-registros-no-cargables true --copiar-escritorio true --desktop-output /Users/alexi/Desktop/personal_academico_en_institucion_2026_PES_READY.csv`

## Resultado
- Filas exportadas: {resumen.get('filas_exportadas', 0)}
- Filas excluidas: {resumen.get('filas_excluidas', 0)}
- Comunas completadas: {resumen.get('comunas_completadas', 0)}
- Fechas transformadas: {resumen.get('fechas_transformadas', 0)}

## Pendientes
- Registrar en codigo cualquier nueva correccion detectada por PES/SIES.
- Mantener la base general intacta salvo correcciones manuales autorizadas.
"""
    BITACORA_FASE_6.write_text(contenido, encoding="utf-8")


def _write_reporte_fase_7(resumen: dict[str, object]) -> None:
    motivos = resumen.get("motivos_exclusion", {})
    motivos_txt = "\n".join(f"- {motivo}: {total}" for motivo, total in sorted(motivos.items())) or "- Sin exclusiones."
    contenido = f"""# Reporte Fase 7 - Reglas PES Horas y Especialidad

## Objetivo
Corregir en codigo las reglas pendientes detectadas por PES/SIES y regenerar el archivo final candidato sin parches manuales sobre el CSV.

## Reglas Incorporadas
- Textos PES con caracteres seguros: mayusculas, sin tildes, `Ñ -> N`, `Ü -> U`, sin caracteres raros.
- `NUM_HORAS_PLANTA`, `NUM_HORAS_CONTRATA` y `NUM_HORAS_HONORARIOS` no salen nulos: valores vacios o no cargables se exportan como `0`.
- Horas numericas se reducen a maximo 2 decimales.
- Si `NIVEL_FORMACION_ACADEMICO` es 5, 6, 7 u 8, se limpia todo el bloque de especialidad.
- Si falta `NIVEL_FORMACION_ESPECIALIDAD`, se limpian campos dependientes de especialidad para no inventar el nivel.
- Si `FECHA_OBTENCION_ESPECIALIDAD` no es cargable, se limpia en exportacion.
- La deteccion/exclusion de registros no cargables ocurre despues de transformar.

## Resultado
- Salida modulo: {resumen.get('salida', '')}
- Copia Escritorio: {resumen.get('desktop_output', '') or 'No solicitada'}
- Filas exportadas: {resumen.get('filas_exportadas', 0)}
- Filas excluidas: {resumen.get('filas_excluidas', 0)}
- Horas nulas completadas con 0: {resumen.get('horas_cero', 0)}
- Bloques de especialidad limpiados: {resumen.get('bloques_especialidad_limpiados', 0)}
- Fechas de especialidad limpiadas: {resumen.get('fechas_especialidad_limpiadas', 0)}
- Textos normalizados: {resumen.get('textos_normalizados', 0)}
- Delimitador: {resumen.get('delimitador_salida_label', '')}
- Encoding: {resumen.get('encoding_salida', '')}
- Encabezado: {'NO' if resumen.get('sin_encabezado') else 'SI'}

## Motivos de Exclusion
{motivos_txt}

## Auditorias
- Transformaciones: {resumen.get('auditoria_transformaciones', '')}
- Exclusiones: {resumen.get('auditoria_exclusiones', '')}

La base general original no fue modificada. Toda transformacion ocurre solo en exportacion.
"""
    REPORTE_FASE_7.write_text(contenido, encoding="utf-8")


def _write_bitacora_fase_7(resumen: dict[str, object]) -> None:
    contenido = f"""# Bitacora Fase 7 - Reglas PES Horas y Especialidad

- Fecha/hora: {datetime.now().isoformat(timespec='seconds')}
- Rama: feature/personal-academico-base-preliminar-2026

## Archivos Creados
- {rel(REPORTE_FASE_7)}
- {rel(BITACORA_FASE_7)}
- {resumen.get('auditoria_transformaciones', '')}
- {resumen.get('auditoria_exclusiones', '')}
- {resumen.get('salida', '')}

## Archivos Modificados
- {rel(MODULE_DIR / 'scripts/exportar_personal_academico_2026.py')}
- {rel(MODULE_DIR / 'scripts/transformaciones_pes_personal_academico_2026.py')}

## Resultado
- Filas exportadas: {resumen.get('filas_exportadas', 0)}
- Filas excluidas: {resumen.get('filas_excluidas', 0)}
- Horas nulas completadas con 0: {resumen.get('horas_cero', 0)}
- Bloques especialidad limpiados: {resumen.get('bloques_especialidad_limpiados', 0)}
- Fechas especialidad limpiadas: {resumen.get('fechas_especialidad_limpiadas', 0)}
- Textos normalizados: {resumen.get('textos_normalizados', 0)}

## Pendientes
- Subir el archivo copiado al Escritorio a PES/SIES.
- Incorporar cualquier nueva regla PES al codigo, no al CSV manualmente.
"""
    BITACORA_FASE_7.write_text(contenido, encoding="utf-8")


def _write_reporte_fase_8(resumen: dict[str, object]) -> None:
    contenido = f"""# Reporte Fase 8 - Correccion NOMBRE_TITULO_O_GRADO A-Z

## Objetivo
Aplicar una regla especifica de exportacion para que `NOMBRE_TITULO_O_GRADO` contenga solo letras mayusculas `A-Z` y espacios simples, segun rechazo PES/SIES.

## Regla Incorporada
- Funcion: `normalizar_solo_letras_az_pes(valor)`.
- Campo aplicado: `NOMBRE_TITULO_O_GRADO`.
- Reemplaza cualquier caracter distinto de `A-Z` por espacio.
- Quita tildes y convierte `Ñ` a `N`.
- No modifica la base general original.

## Resultado
- Archivo repo: {resumen.get('salida', '')}
- Archivo Escritorio: {resumen.get('desktop_output', '')}
- Filas exportadas: {resumen.get('filas_exportadas', 0)}
- Titulos corregidos: {resumen.get('titulos_solo_az', 0)}
- Auditoria transformaciones: {resumen.get('auditoria_transformaciones', '')}
- Auditoria exclusiones: {resumen.get('auditoria_exclusiones', '')}

La correccion queda en codigo y auditoria; no se hizo parche manual sobre el CSV final.
"""
    REPORTE_FASE_8.write_text(contenido, encoding="utf-8")


def _write_bitacora_fase_8(resumen: dict[str, object]) -> None:
    contenido = f"""# Bitacora Fase 8 - Correccion NOMBRE_TITULO_O_GRADO A-Z

- Fecha/hora: {datetime.now().isoformat(timespec='seconds')}
- Rama: feature/personal-academico-base-preliminar-2026

## Archivos Modificados
- {rel(MODULE_DIR / 'scripts/transformaciones_pes_personal_academico_2026.py')}
- {rel(MODULE_DIR / 'scripts/exportar_personal_academico_2026.py')}

## Archivos Creados
- {rel(REPORTE_FASE_8)}
- {rel(BITACORA_FASE_8)}
- {resumen.get('auditoria_transformaciones', '')}
- {resumen.get('auditoria_exclusiones', '')}

## Resultado
- Archivo repo: {resumen.get('salida', '')}
- Archivo Escritorio: {resumen.get('desktop_output', '')}
- Filas finales: {resumen.get('filas_exportadas', 0)}
- Titulos corregidos: {resumen.get('titulos_solo_az', 0)}

## Pendiente
- Reintentar carga en PES/SIES y traer cualquier nueva regla al codigo.
"""
    BITACORA_FASE_8.write_text(contenido, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exportador bloqueado por auditoria para Personal Academico SIES 2026."
    )
    parser.add_argument("--tipo", choices=["en_institucion", "fuera_institucion"], required=True)
    parser.add_argument("--input", required=True, help="Ruta del archivo validado.")
    parser.add_argument("--output", required=True, help="Ruta CSV de salida propuesta.")
    parser.add_argument("--delimitador-salida", default="punto_coma")
    parser.add_argument("--sin-encabezado", default=str(not EXPORTAR_CON_ENCABEZADO_DEFAULT))
    parser.add_argument("--encoding", default=ENCODING_DEFAULT)
    parser.add_argument("--encoding-salida", default="cp1252", choices=["cp1252", "utf-8-sig", "utf-8"])
    parser.add_argument("--permitir-exportacion-final", default="false")
    parser.add_argument("--delimitador-entrada", default=DELIMITADOR_ESTRUCTURA_OBSERVADO)
    parser.add_argument("--formato-fecha-pes", default="true")
    parser.add_argument("--normalizar-texto-pes", default="true")
    parser.add_argument("--completar-comuna-mayor", default="true")
    parser.add_argument("--excluir-registros-no-cargables", default="false")
    parser.add_argument("--copiar-escritorio", default="false")
    parser.add_argument("--desktop-output", default=None)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    permitir_exportacion = str_a_bool(args.permitir_exportacion_final)
    sin_encabezado = str_a_bool(args.sin_encabezado)
    formato_fecha_pes = str_a_bool(args.formato_fecha_pes)
    normalizar_texto_pes = str_a_bool(args.normalizar_texto_pes)
    completar_comuna_mayor = str_a_bool(args.completar_comuna_mayor)
    excluir_no_cargables = str_a_bool(args.excluir_registros_no_cargables)
    copiar_escritorio = str_a_bool(args.copiar_escritorio)
    delimitador_entrada = normalizar_delimitador(args.delimitador_entrada)
    if args.delimitador_entrada == DELIMITADOR_ESTRUCTURA_OBSERVADO and input_path.suffix.lower() == ".tsv":
        delimitador_entrada = "\t"
    delimitador_salida = normalizar_delimitador(args.delimitador_salida)
    delimitador_salida_label = "punto_coma" if delimitador_salida == ";" else "coma" if delimitador_salida == "," else args.delimitador_salida

    if not input_path.exists():
        print(f"ERROR: no existe archivo de entrada: {input_path}", file=sys.stderr)
        return 2

    columnas_esperadas = columnas_por_tipo(args.tipo)
    df = pd.read_csv(
        input_path,
        sep=delimitador_entrada,
        encoding=args.encoding,
        dtype=str,
        keep_default_na=False,
    )
    resultado_columnas = validar_columnas_exactas(df, columnas_esperadas)
    eventos = [resultado_columnas]

    actuales = list(df.columns)
    if set(actuales) == set(columnas_esperadas) and actuales != columnas_esperadas:
        eventos.append(
            _evento_exportacion(
                severidad="ADVERTENCIA",
                regla="reordenamiento_columnas",
                estado="ADVERTENCIA",
                mensaje=(
                    "Columnas presentes pero en orden distinto; se reordenarian antes de exportar."
                ),
                fuente_regla=FUENTE_ESTRUCTURA,
                columna="*",
            )
        )

    eventos.append(
        _evento_exportacion(
            severidad="INFO",
            regla="delimitador_salida_parametrizado",
            estado="OK",
            valor=args.delimitador_salida,
            mensaje=(
                "Delimitador de salida configurado. Para carga real PES/SIES se usa "
                "punto y coma por hallazgo operativo auditado en Fase 6."
            ),
            fuente_regla=FUENTE_PREVENTIVA,
        )
    )

    if EXPORTAR_INDICE_DEFAULT is False:
        eventos.append(
            _evento_exportacion(
                severidad="INFO",
                regla="sin_indice",
                estado="OK",
                mensaje="La exportacion se configura sin indice.",
                fuente_regla=FUENTE_PREVENTIVA,
            )
        )

    if not permitir_exportacion:
        eventos.append(
            _evento_exportacion(
                severidad="ADVERTENCIA",
                regla="bloqueo_exportacion_final",
                estado="BLOQUEADO",
                mensaje=(
                    "Exportacion final bloqueada. Active --permitir-exportacion-final true "
                    "solo con auditoria aprobada."
                ),
                fuente_regla=FUENTE_PREVENTIVA,
            )
        )

    reporte = construir_reporte_validacion(input_path.name, args.tipo, eventos)
    auditoria_path = _auditoria_exportacion_default(args.tipo, output_path)
    reporte.to_csv(auditoria_path, index=False, encoding=args.encoding)

    if not resultado_columnas["ok"]:
        print("RECHAZADO: estructura no coincide con columnas oficiales.")
        print(f"auditoria: {auditoria_path}")
        return 1

    if not permitir_exportacion:
        print("BLOQUEADO: no se genero archivo final PES/SIES.")
        print("Motivo: falta activar --permitir-exportacion-final true con auditoria aprobada.")
        print(f"auditoria: {auditoria_path}")
        return 0

    df = df[columnas_esperadas]
    registros = df.to_dict(orient="records")
    transformaciones: list[dict[str, object]] = []
    exclusiones: list[dict[str, object]] = []
    filas_exportacion: list[list[str]] = []
    motivos_exclusion: Counter[str] = Counter()

    for idx, registro in enumerate(registros, start=2):
        transformado, eventos_fila = transformar_fila_para_pes(
            registro,
            columnas_esperadas,
            args.tipo,
            formato_fecha_pes=formato_fecha_pes,
            normalizar_texto=normalizar_texto_pes,
            completar_comuna=completar_comuna_mayor,
        )
        for evento in eventos_fila:
            transformaciones.append(
                {
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "tipo_evento": evento["tipo_evento"],
                    "severidad": evento["severidad"],
                    "fila_origen": idx,
                    "columna": evento["columna"],
                    "valor_original": evento["valor_original"],
                    "valor_transformado": evento["valor_transformado"],
                    "accion": "TRANSFORMAR_SOLO_EXPORTACION",
                    "mensaje": evento["mensaje"],
                    "fuente_regla": evento["fuente_regla"],
                }
            )

        motivos = detectar_registro_no_cargable(transformado, columnas_esperadas, args.tipo)
        if motivos:
            if excluir_no_cargables:
                for motivo in motivos:
                    motivos_exclusion[motivo] += 1
                exclusiones.append(
                    {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "tipo_evento": "REGISTRO_EXCLUIDO_NO_CARGABLE",
                        "severidad": "WARN",
                        "fila_origen": idx,
                        "motivo": " | ".join(motivos),
                        "accion": "EXCLUIR_SOLO_EXPORTACION",
                        "detalle": "Registro excluido del candidato PES_READY filtrado; base original intacta.",
                        "fuente_regla": FUENTE_PREVENTIVA,
                    }
                )
                continue
            for motivo in motivos:
                exclusiones.append(
                    {
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                        "tipo_evento": "EXPORTACION_BLOQUEADA_REGISTRO_NO_CARGABLE",
                        "severidad": "ERROR",
                        "fila_origen": idx,
                        "motivo": motivo,
                        "accion": "BLOQUEAR_EXPORTACION",
                        "detalle": "Use --excluir-registros-no-cargables true o corrija con respaldo.",
                        "fuente_regla": FUENTE_PENDIENTE,
                    }
                )
            auditoria_exclusiones = _audit_path("auditoria_exclusiones_pes")
            _write_exclusion_audit(auditoria_exclusiones, exclusiones)
            print("BLOQUEADO: existen registros no cargables para PES/SIES.")
            print(f"auditoria exclusiones: {auditoria_exclusiones}")
            return 1
        filas_exportacion.append([transformado.get(col, "") for col in columnas_esperadas])

    auditoria_transformaciones = _audit_path("auditoria_transformaciones_pes_fase7")
    auditoria_exclusiones = _audit_path("auditoria_exclusiones_pes_fase7")
    generar_auditoria_transformaciones(auditoria_transformaciones, transformaciones)
    _write_exclusion_audit(auditoria_exclusiones, exclusiones)

    backup_output = _backup_if_exists(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding=args.encoding_salida, newline="") as fh:
        writer = csv.writer(fh, delimiter=delimitador_salida, lineterminator="\n")
        if not sin_encabezado:
            writer.writerow(columnas_esperadas)
        writer.writerows(filas_exportacion)

    desktop_output = ""
    if copiar_escritorio:
        if not args.desktop_output:
            print("ERROR: --copiar-escritorio true requiere --desktop-output.", file=sys.stderr)
            return 2
        desktop_path = Path(args.desktop_output)
        _backup_if_exists(desktop_path)
        desktop_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, desktop_path)
        desktop_output = str(desktop_path)

    conteos_transformaciones = Counter(str(e["tipo_evento"]) for e in transformaciones)
    resumen_fase_6 = {
        "salida": rel(output_path),
        "desktop_output": desktop_output,
        "filas_exportadas": len(filas_exportacion),
        "filas_excluidas": len(exclusiones),
        "motivos_exclusion": dict(motivos_exclusion),
        "comunas_completadas": conteos_transformaciones.get("COMUNA_MAYOR_FUNCION_COMPLETADA", 0),
        "fechas_transformadas": conteos_transformaciones.get("FECHA_FORMATO_PES", 0),
        "horas_cero": conteos_transformaciones.get("HORA_OBLIGATORIA_COMPLETADA_CERO", 0),
        "bloques_especialidad_limpiados": (
            conteos_transformaciones.get("BLOQUE_ESPECIALIDAD_LIMPIADO_NIVEL_ACADEMICO", 0)
            + conteos_transformaciones.get("BLOQUE_ESPECIALIDAD_DEPENDIENTE_LIMPIADO_SIN_NIVEL", 0)
            + conteos_transformaciones.get("BLOQUE_ESPECIALIDAD_LIMPIADO_FECHA_FUTURA_SIN_NIVEL", 0)
        ),
        "fechas_especialidad_limpiadas": conteos_transformaciones.get("FECHA_ESPECIALIDAD_LIMPIADA_NO_CARGABLE", 0),
        "textos_normalizados": conteos_transformaciones.get("TEXTO_NORMALIZADO_PES", 0),
        "titulos_solo_az": conteos_transformaciones.get("NOMBRE_TITULO_SOLO_A_Z", 0),
        "auditoria_transformaciones": rel(auditoria_transformaciones),
        "auditoria_exclusiones": rel(auditoria_exclusiones),
        "delimitador_salida_label": delimitador_salida_label,
        "encoding_salida": args.encoding_salida,
        "sin_encabezado": sin_encabezado,
    }
    _write_reporte_fase_6(resumen_fase_6)
    _write_bitacora_fase_6(resumen_fase_6)
    _write_reporte_fase_7(resumen_fase_6)
    _write_bitacora_fase_7(resumen_fase_6)
    _write_reporte_fase_8(resumen_fase_6)
    _write_bitacora_fase_8(resumen_fase_6)

    print("EXPORTADO: archivo final generado bajo autorizacion explicita.")
    print(f"salida: {output_path}")
    if desktop_output:
        print(f"copia escritorio: {desktop_output}")
    print(f"auditoria: {auditoria_path}")
    print(f"auditoria transformaciones: {auditoria_transformaciones}")
    print(f"auditoria exclusiones: {auditoria_exclusiones}")
    print(f"filas exportadas: {len(filas_exportacion)}")
    print(f"filas excluidas: {len(exclusiones)}")
    if backup_output:
        print(f"backup salida previa: {backup_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

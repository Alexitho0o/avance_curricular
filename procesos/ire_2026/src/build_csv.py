"""Entregable 1: CSV de carga PES. Sin encabezados, ';' delimitado, UTF-8 sin BOM."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # raíz del monorepo (para 'common.*')
sys.path.insert(0, str(Path(__file__).parent.parent))       # procesos/ire_2026 (para 'src.*'; va primero: evita colision con src/ raiz de MU2026)

from datetime import datetime
from typing import List, Dict, Tuple

from common.io_csv import leer_csv, escribir_csv
from common.validacion import ejecutar, agrupar_por_severidad, Severidad
from src.schema import COLUMNAS
from src.validators import obtener_reglas, validar_dataset
from src.config_loader import (
    cargar_institucion,
    cargar_parametros,
    verificar_claves_bloqueantes,
    aplicar_herencias,
    aplicar_convenios_nuevos,
    aplicar_predios,
    aplicar_eliminaciones,
    ConfiguracionIncompleta,
)

RAIZ_PROCESO = Path(__file__).parent.parent
RUTA_INPUT = RAIZ_PROCESO / "data" / "input" / "ire_2026.csv"
RUTA_OUTPUT = RAIZ_PROCESO / "output"


class ValidacionFallida(Exception):
    """Error accionable: el dataset final no pasa las reglas de validación."""
    pass


def _limpiar_marcadores_revisar(filas: List[Dict]) -> List[Dict]:
    """
    Verificar que no quede ningún marcador <<REVISAR>> sin resolver tras aplicar
    la configuración. Si queda alguno, el campo llegó vacío/sin reemplazar.
    """
    pendientes = []
    for i, fila in enumerate(filas):
        for campo, valor in fila.items():
            if valor == "<<REVISAR>>":
                pendientes.append(f"Fila {i} ({fila.get('NOMBRE_IDENTIFICACION', '')}): campo '{campo}' sigue en <<REVISAR>>")

    if pendientes:
        raise ConfiguracionIncompleta(
            "Quedan campos <<REVISAR>> sin resolver en data/input/ire_2026.csv tras "
            "aplicar config/parametros_2026.yaml:\n" +
            "\n".join(f"  - {p}" for p in pendientes)
        )

    return filas


def construir_dataset(log: List[str] = None) -> List[Dict]:
    """
    Construir el dataset final 2026: input + config (herencias, convenios,
    predios, eliminaciones). Aborta con ConfiguracionIncompleta si faltan
    claves bloqueantes o quedan <<REVISAR>> sin resolver.
    """
    if log is None:
        log = []

    institucion = cargar_institucion()
    parametros = cargar_parametros()

    verificar_claves_bloqueantes(parametros)

    encabezados, filas = leer_csv(str(RUTA_INPUT), delimitador=';', encoding='utf-8')

    filas, log_herencias = aplicar_herencias(parametros, filas)
    log.extend(log_herencias)

    filas = aplicar_convenios_nuevos(parametros, filas, COLUMNAS)
    filas = aplicar_predios(parametros, filas, COLUMNAS)

    filas, log_eliminaciones = aplicar_eliminaciones(parametros, filas)
    log.extend(log_eliminaciones)

    filas = _limpiar_marcadores_revisar(filas)

    return filas


def validar_dataset_completo(filas: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Ejecutar reglas por fila + reglas de dataset sobre el conjunto final.

    Returns:
        (es_valido, mensajes_error) — mensajes_error lista TODOS los errores,
        no solo el primero.
    """
    reglas = obtener_reglas()
    resultados, sin_errores_fila = ejecutar(reglas, filas, detener_en_error=False)
    por_severidad = agrupar_por_severidad(resultados)

    mensajes = [
        f"Fila {r.fila_indice}: {r.regla_id} - {r.mensaje}"
        for r in por_severidad[Severidad.ERROR]
    ]

    errores_dataset = validar_dataset(filas)
    mensajes.extend(errores_dataset)

    es_valido = len(mensajes) == 0
    return es_valido, mensajes


def generar_csv_carga(filas: List[Dict], fecha_sufijo: str = None) -> Tuple[Path, Path]:
    """
    Generar las dos variantes del CSV de carga (';' y ',').

    Returns:
        (ruta_puntoycoma, ruta_coma)
    """
    if fecha_sufijo is None:
        fecha_sufijo = datetime.now().strftime('%Y%m%d')

    RUTA_OUTPUT.mkdir(parents=True, exist_ok=True)

    ruta_puntoycoma = RUTA_OUTPUT / f"IRE_2026_carga_{fecha_sufijo}_puntoycoma.csv"
    ruta_coma = RUTA_OUTPUT / f"IRE_2026_carga_{fecha_sufijo}_coma.csv"

    escribir_csv(
        ruta=str(ruta_puntoycoma),
        encabezados=COLUMNAS,
        filas=filas,
        delimitador=';',
        encoding='utf-8',
        con_encabezados=False,
        quote_minimal=True,
    )

    escribir_csv(
        ruta=str(ruta_coma),
        encabezados=COLUMNAS,
        filas=filas,
        delimitador=',',
        encoding='utf-8',
        con_encabezados=False,
        quote_minimal=True,
    )

    return ruta_puntoycoma, ruta_coma


def main():
    log = []

    print("=" * 70)
    print("IRE 2026 — Generación del CSV de carga PES")
    print("=" * 70)

    try:
        filas = construir_dataset(log)
    except ConfiguracionIncompleta as e:
        print("\n✗ PIPELINE DETENIDO — configuración incompleta\n")
        print(str(e))
        sys.exit(1)

    if log:
        print(f"\nHerencias aplicadas ({len(log)}):")
        for entrada in log:
            print(f"  - {entrada}")

    print(f"\nValidando {len(filas)} filas...")
    es_valido, mensajes = validar_dataset_completo(filas)

    if not es_valido:
        print(f"\n✗ VALIDACIÓN FALLIDA — {len(mensajes)} error(es):\n")
        for m in mensajes:
            print(f"  - {m}")
        raise ValidacionFallida(f"{len(mensajes)} error(es) de validación; ver detalle arriba")

    print("✓ Validación exitosa, sin errores.")

    ruta_pyc, ruta_coma = generar_csv_carga(filas)
    print(f"\n✓ Generado: {ruta_pyc}")
    print(f"✓ Generado: {ruta_coma}")

    print("\n⚠ ADVERTENCIA: FECHA_TERMINO de Miguel Claro 337 es PROVISIONAL (2027-12).")
    print("  Reemplazar en config/parametros_2026.yaml antes de subir a PES.")
    print("  Clave: tenencia.fecha_termino")


if __name__ == '__main__':
    main()

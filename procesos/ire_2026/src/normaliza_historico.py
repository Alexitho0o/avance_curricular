"""Normalizar histórico Excel: limpiar suciedades, extraer FEC_REF, guardar como CSV."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from common.texto import normalizar, limpiar_numero_texto
from common.io_csv import escribir_csv
from src.schema import COLUMNAS


def limpiar_valor(valor):
    """Limpiar un valor: número guardado como texto, '0' como vacío en texto, espacios."""
    if pd.isna(valor) or valor == '':
        return ''

    valor_str = str(valor).strip()

    # Si es '0' en un campo que sería texto, convertir a vacío
    if valor_str == '0':
        return ''

    # Si es un número guardado como texto, intentar convertir
    try:
        return float(valor_str)
    except ValueError:
        # Mantener como texto, pero limpio
        return valor_str


def limpiar_espacios_blanco_especiales(texto):
    """Remover \xa0 (non-breaking space) y espacios múltiples."""
    if not isinstance(texto, str):
        return texto

    texto = texto.replace('\xa0', ' ')
    import re
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def normalizar_historico_excel(ruta_excel: str, ruta_salida_csv: str, hoja: str = "2025") -> None:
    """
    Leer Excel histórico, limpiar, y guardar como CSV.

    Args:
        ruta_excel: Ruta al .xlsm
        ruta_salida_csv: Ruta para guardar CSV normalizado
        hoja: Nombre de hoja a leer (default "2025")
    """
    ruta_excel_path = Path(ruta_excel)

    if not ruta_excel_path.exists():
        print(f"ADVERTENCIA: Archivo {ruta_excel} no encontrado. Saltando normalización.")
        return

    print(f"Leyendo histórico desde {hoja}...")
    try:
        # Leer con keep_vba=True para no perder macros
        df = pd.read_excel(ruta_excel_path, sheet_name=hoja, engine='openpyxl')
    except Exception as e:
        print(f"ERROR al leer hoja {hoja}: {e}")
        raise

    print(f"Filas leídas: {len(df)}")

    # Limpiar espacios en nombres de columnas
    df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]

    # Detectar si existe FEC_REF (posición 5, índice 4)
    fec_ref_col = None
    if len(df.columns) > 4 and 'FEC_REF' in str(df.columns[4]):
        fec_ref_col = df.columns[4]
        print(f"Detectado FEC_REF en columna {fec_ref_col}")

        # Extraer FEC_REF como metadato y sacarlo del dataframe
        fecha_corte = df[fec_ref_col].iloc[0] if len(df) > 0 else None
        print(f"Fecha de corte: {fecha_corte}")

        # Remover columna FEC_REF
        df = df.drop(columns=[fec_ref_col])
        print(f"Columnas restantes: {len(df.columns)}")

    # Verificar que tengamos 54 columnas
    if len(df.columns) != 54:
        print(f"ADVERTENCIA: Se esperan 54 columnas, se encontraron {len(df.columns)}")
        print(f"Columnas: {list(df.columns)}")

    # Limpiar valores
    print("Limpiando valores...")
    for col in df.columns:
        if col in COLUMNAS:
            df[col] = df[col].apply(limpiar_valor)
            df[col] = df[col].apply(limpiar_espacios_blanco_especiales)

    # Remover filas completamente vacías
    df = df.dropna(how='all')

    # Convertir a diccionarios para escribir con io_csv
    filas = df.to_dict(orient='records')

    # Convertir valores a strings para CSV
    filas_str = []
    for fila in filas:
        fila_str = {}
        for col, val in fila.items():
            if pd.isna(val):
                fila_str[col] = ''
            elif isinstance(val, (int, float)):
                # Si es número entero, no poner decimal
                if isinstance(val, float) and val == int(val):
                    fila_str[col] = str(int(val))
                else:
                    fila_str[col] = str(val)
            else:
                fila_str[col] = str(val).strip()
        filas_str.append(fila_str)

    print(f"Escribiendo {len(filas_str)} filas a {ruta_salida_csv}...")
    escribir_csv(
        ruta=ruta_salida_csv,
        encabezados=COLUMNAS,
        filas=filas_str,
        delimitador=';',
        con_encabezados=True,
    )

    print(f"✓ Histórico normalizado guardado en {ruta_salida_csv}")


if __name__ == '__main__':
    import sys

    # Uso: python normaliza_historico.py <ruta_excel> <ruta_salida_csv> [hoja]
    if len(sys.argv) < 2:
        print("Uso: python normaliza_historico.py <ruta_excel> [ruta_salida_csv] [hoja]")
        sys.exit(1)

    ruta_excel = sys.argv[1]
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else "data/historico/ire_historico.csv"
    hoja = sys.argv[3] if len(sys.argv) > 3 else "2025"

    normalizar_historico_excel(ruta_excel, ruta_salida, hoja)

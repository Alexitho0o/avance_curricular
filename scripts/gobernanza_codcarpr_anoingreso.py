"""Gobernanza CODCARPR por cohorte (ANOINGRESO).

Genera artefactos de gobernanza para detectar y resolver superposiciones
de CODCARPR por (NOMBRE_L, JORNADA, ANOINGRESO). No modifica el pipeline
regulatorio ni la estructura del CSV final MU32.

Uso:
    python scripts/gobernanza_codcarpr_anoingreso.py \
        --input /ruta/PROMEDIOSDEALUMNOS_7804.xlsx \
        --output-dir resultados
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------

def _norm_jornada(s: object) -> str:
    if pd.isna(s):
        return ''
    return str(s).strip().upper()


def _norm_nombre(s: object) -> str:
    if pd.isna(s):
        return ''
    return re.sub(r'\s+', ' ', str(s).strip().upper())


def _extract_year_columns(columns: list[object]) -> list[object]:
    years: list[tuple[int, object]] = []
    for c in columns:
        if isinstance(c, str):
            txt = c.strip()
            if txt.isdigit() and len(txt) == 4:
                y = int(txt)
                if 1900 <= y <= 2100:
                    years.append((y, c))
                continue
        if isinstance(c, (int, float)) and float(c) == int(c):
            y = int(c)
            if 1900 <= y <= 2100:
                years.append((y, c))
    years_sorted = [orig for _, orig in sorted(years, key=lambda x: x[0])]
    return years_sorted


# ---------------------------------------------------------------------------
# Paso 0 — Localizar Excel de gobernanza
# ---------------------------------------------------------------------------

def _locate_gobernanza_xlsx(input_path: Path) -> Path:
    """Busca 'gobernanza CODCARPR_ANOINGRESO.xlsx' junto al input del pipeline."""
    parent = input_path.parent
    gob_path = parent / 'gobernanza CODCARPR_ANOINGRESO.xlsx'
    if not gob_path.exists():
        sys.exit(f'ERROR: No se encontró {gob_path}')
    return gob_path


# ---------------------------------------------------------------------------
# Paso 1 — Excel → TSV long (una sola vez)
# ---------------------------------------------------------------------------

def paso1_excel_a_tsv_long(gob_xlsx: Path, control_dir: Path) -> pd.DataFrame:
    """Despivotar Hoja1 de gobernanza a formato long y guardar TSV."""
    df = pd.read_excel(gob_xlsx, sheet_name=0)

    # Identificar columnas-año (headers numéricos enteros)
    year_cols = _extract_year_columns(list(df.columns))
    if not year_cols:
        raise ValueError('No se detectaron columnas-año en Hoja1 de gobernanza')
    id_cols = ['CODCARPR', 'JORNADA', 'NOMBRE_L']

    long = df.melt(id_vars=id_cols, value_vars=year_cols,
                   var_name='ANOINGRESO', value_name='VAL')
    long['ANOINGRESO'] = pd.to_numeric(long['ANOINGRESO'], errors='coerce').astype('Int64')
    long['VAL'] = pd.to_numeric(long['VAL'], errors='coerce')

    # Filtrar VAL > 0
    long = long[long['ANOINGRESO'].notna() & long['VAL'].notna() & (long['VAL'] > 0)].copy()
    long['ANOINGRESO'] = long['ANOINGRESO'].astype(int)

    # Normalización obligatoria
    long['JORNADA'] = long['JORNADA'].apply(_norm_jornada)
    long['NOMBRE_L'] = long['NOMBRE_L'].apply(_norm_nombre)

    long = long.sort_values(['NOMBRE_L', 'JORNADA', 'ANOINGRESO', 'CODCARPR']).reset_index(drop=True)

    tsv_path = control_dir / 'gob_codcarpr_anioingreso_long.tsv'
    long.to_csv(tsv_path, sep='\t', index=False)
    print(f'  ✅ TSV long generado: {tsv_path} ({len(long)} filas)')
    return long


# ---------------------------------------------------------------------------
# Paso 2 — Detectar superposiciones desde TSV long
# ---------------------------------------------------------------------------

def paso2_detectar_superposiciones(long: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por (NOMBRE_L, JORNADA, ANOINGRESO) y detecta N_CODCARPR > 1."""

    def _agg(g: pd.DataFrame) -> pd.Series:
        codcarprs = g.sort_values('VAL', ascending=False)
        codcarpr_list = '|'.join(codcarprs['CODCARPR'].unique())
        codcarpr_vals = '|'.join(
            f"{row.CODCARPR}:{int(row.VAL)}" for row in codcarprs.itertuples()
        )
        return pd.Series({
            'N_CODCARPR': g['CODCARPR'].nunique(),
            'CODCARPR_LIST': codcarpr_list,
            'CODCARPR_VALS': codcarpr_vals,
        })

    agg = long.groupby(['NOMBRE_L', 'JORNADA', 'ANOINGRESO'], as_index=False).apply(
        _agg, include_groups=False,
    )
    sup = agg[agg['N_CODCARPR'] > 1].copy().reset_index(drop=True)
    print(f'  ✅ Superposiciones: {len(sup)} claves con >1 CODCARPR')
    return sup


def paso2b_cargar_long_desde_tsv(control_dir: Path) -> pd.DataFrame:
    """Carga TSV long persistido para que el resto del análisis use esa fuente."""
    tsv_path = control_dir / 'gob_codcarpr_anioingreso_long.tsv'
    if not tsv_path.exists():
        raise FileNotFoundError(f'No existe TSV long: {tsv_path}')
    long = pd.read_csv(tsv_path, sep='\t', dtype={'CODCARPR': str, 'JORNADA': str, 'NOMBRE_L': str})
    long['ANOINGRESO'] = pd.to_numeric(long['ANOINGRESO'], errors='coerce').astype('Int64')
    long['VAL'] = pd.to_numeric(long['VAL'], errors='coerce')
    long = long[long['ANOINGRESO'].notna() & long['VAL'].notna() & (long['VAL'] > 0)].copy()
    long['ANOINGRESO'] = long['ANOINGRESO'].astype(int)
    long['JORNADA'] = long['JORNADA'].apply(_norm_jornada)
    long['NOMBRE_L'] = long['NOMBRE_L'].apply(_norm_nombre)
    return long


# ---------------------------------------------------------------------------
# Paso 3 — Cruce con universo real del pipeline
# ---------------------------------------------------------------------------

def paso3_cruce_universo_real(
    input_xlsx: Path,
    sup: pd.DataFrame,
) -> pd.DataFrame:
    """Cruza superposiciones de gobernanza contra CODCLI reales."""

    xls = pd.ExcelFile(input_xlsx)

    # --- Hoja1: deduplicar por CODCLI ---
    h1 = pd.read_excel(xls, sheet_name='Hoja1',
                        usecols=['CODCLI', 'CODCARR', 'CARRERA', 'JORNADA', 'PLAN_DE_ESTUDIO'])
    h1 = h1.drop_duplicates(subset=['CODCLI']).copy()
    h1['CARRERA_N'] = h1['CARRERA'].apply(_norm_nombre)
    h1['JORNADA_N'] = h1['JORNADA'].apply(_norm_jornada)

    # --- DatosAlumnos: ANOINGRESO por CODCLI ---
    da = pd.read_excel(xls, sheet_name='DatosAlumnos',
                        usecols=['CODCLI', 'ANOINGRESO'])
    da = da.drop_duplicates(subset=['CODCLI']).copy()
    da['ANOINGRESO'] = pd.to_numeric(da['ANOINGRESO'], errors='coerce').astype('Int64')

    # Merge
    uni = h1.merge(da[['CODCLI', 'ANOINGRESO']], on='CODCLI', how='inner')
    print(f'  → Universo real (Hoja1 ∩ DatosAlumnos): {len(uni)} CODCLI')

    # Crear clave de cruce en superposiciones y universo
    sup['_KEY'] = sup['NOMBRE_L'] + '||' + sup['JORNADA'] + '||' + sup['ANOINGRESO'].astype(str)
    uni['_KEY'] = uni['CARRERA_N'] + '||' + uni['JORNADA_N'] + '||' + uni['ANOINGRESO'].astype(str)

    keys_sup = set(sup['_KEY'])
    afectados = uni[uni['_KEY'].isin(keys_sup)].copy()

    # Enriquecer con datos de superposición
    sup_lookup = sup.set_index('_KEY')[['N_CODCARPR', 'CODCARPR_LIST', 'CODCARPR_VALS']]
    afectados = afectados.merge(sup_lookup, left_on='_KEY', right_index=True, how='left')
    afectados['ANOINGRESO_FUENTE'] = 'DatosAlumnos:ANOINGRESO'
    afectados['REQUIERE_REVISION'] = 'SI'

    # Columnas finales
    afectados = afectados[[
        'CODCLI', 'CODCARR', 'CARRERA', 'JORNADA', 'PLAN_DE_ESTUDIO',
        'ANOINGRESO', 'ANOINGRESO_FUENTE',
        'N_CODCARPR', 'CODCARPR_LIST', 'CODCARPR_VALS', 'REQUIERE_REVISION',
    ]].sort_values(['CARRERA', 'JORNADA', 'ANOINGRESO', 'CODCLI']).reset_index(drop=True)

    print(f'  ✅ CODCLI afectados por superposición: {len(afectados)}')
    return afectados


# ---------------------------------------------------------------------------
# Paso 4 — Generar artefactos de gobernanza
# ---------------------------------------------------------------------------

def paso4_generar_outputs(
    afectados: pd.DataFrame,
    sup: pd.DataFrame,
    gob_xlsx: Path,
    output_dir: Path,
) -> dict[str, Path]:
    """Genera Excel y TSV de superposiciones + Excel de gobernanza con Hoja2."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    # --- A) Excel de superposiciones ---
    sup_xlsx = output_dir / 'codcli_superposiciones_codcarpr_por_anoingreso.xlsx'
    claves_sup = sup.drop(columns=['_KEY'], errors='ignore').copy()
    claves_sup = claves_sup.rename(columns={'NOMBRE_L': 'NOMBRE_L_N', 'JORNADA': 'JORNADA_N'})

    with pd.ExcelWriter(sup_xlsx, engine='openpyxl') as w:
        afectados.to_excel(w, sheet_name='CODCLI_SUPERPOSICION', index=False)
        claves_sup.to_excel(w, sheet_name='CLAVES_SUPERPOSICION', index=False)
    paths['sup_xlsx'] = sup_xlsx
    print(f'  ✅ Excel superposiciones: {sup_xlsx}')

    # --- B) TSV equivalente ---
    sup_tsv = output_dir / 'codcli_superposiciones_codcarpr_por_anoingreso.tsv'
    afectados.to_csv(sup_tsv, sep='\t', index=False)
    paths['sup_tsv'] = sup_tsv
    print(f'  ✅ TSV superposiciones: {sup_tsv}')

    # --- C) Excel de gobernanza con Hoja2 ---
    gob_out = output_dir / 'gobernanza_CODCARPR_ANOINGRESO_con_Hoja2.xlsx'
    hoja1_orig = pd.read_excel(gob_xlsx, sheet_name=0)

    # Construir Hoja2 desde afectados
    hoja2 = afectados[[
        'PLAN_DE_ESTUDIO', 'ANOINGRESO', 'JORNADA', 'CARRERA',
        'CODCLI', 'CODCARPR_LIST', 'CODCARPR_VALS',
    ]].copy()
    hoja2['CODCARPR_RESUELTO'] = ''
    hoja2['MOTIVO'] = ''
    hoja2['ESTADO'] = ''

    with pd.ExcelWriter(gob_out, engine='openpyxl') as w:
        hoja1_orig.to_excel(w, sheet_name='Hoja1', index=False)
        hoja2.to_excel(w, sheet_name='DESAMBIGUACION_SUPERPOSICION', index=False)
    paths['gob_xlsx'] = gob_out
    print(f'  ✅ Excel gobernanza con Hoja2: {gob_out}')

    return paths


# ---------------------------------------------------------------------------
# Validaciones finales
# ---------------------------------------------------------------------------

def validaciones_finales(
    afectados: pd.DataFrame,
    sup: pd.DataFrame,
    control_dir: Path,
    output_dir: Path,
) -> None:
    print('\n' + '=' * 60)
    print('  VALIDACIONES FINALES')
    print('=' * 60)

    n_claves = len(sup)
    n_codcli = len(afectados)
    fuente_ok = (afectados['ANOINGRESO_FUENTE'] == 'DatosAlumnos:ANOINGRESO').all() if len(afectados) > 0 else True

    print(f'  • Claves superpuestas detectadas:       {n_claves}')
    print(f'  • CODCLI afectados:                     {n_codcli}')
    print(f'  • ANOINGRESO_FUENTE 100% DatosAlumnos:  {"SI" if fuente_ok else "NO"}')

    expected = {
        'TSV long': control_dir / 'gob_codcarpr_anioingreso_long.tsv',
        'Excel superposiciones': output_dir / 'codcli_superposiciones_codcarpr_por_anoingreso.xlsx',
        'TSV superposiciones': output_dir / 'codcli_superposiciones_codcarpr_por_anoingreso.tsv',
        'Excel gobernanza Hoja2': output_dir / 'gobernanza_CODCARPR_ANOINGRESO_con_Hoja2.xlsx',
    }
    all_ok = True
    for label, p in expected.items():
        exists = p.exists()
        icon = '✅' if exists else '❌'
        print(f'  {icon} {label}: {p.name}')
        if not exists:
            all_ok = False

    if all_ok and fuente_ok:
        print(f'\n  ✅ GOBERNANZA CODCARPR OK — {n_claves} claves, {n_codcli} CODCLI afectados')
    else:
        print(f'\n  ❌ GOBERNANZA CODCARPR CON PROBLEMAS')
    print('=' * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Gobernanza CODCARPR por cohorte (ANOINGRESO)')
    p.add_argument('--input', required=True, help='Ruta a PROMEDIOSDEALUMNOS_7804.xlsx')
    p.add_argument('--output-dir', default='resultados', help='Directorio de salida')
    p.add_argument('--control-dir', default='control', help='Directorio de control')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    control_dir = Path(args.control_dir)

    print('=' * 60)
    print('  GOBERNANZA CODCARPR × ANOINGRESO')
    print('=' * 60)

    # Paso 0
    print('\n📂 Paso 0: Localizar Excel de gobernanza...')
    gob_xlsx = _locate_gobernanza_xlsx(input_path)
    print(f'  ✅ Encontrado: {gob_xlsx.name}')

    # Paso 1
    print('\n📊 Paso 1: Excel → TSV long...')
    control_dir.mkdir(parents=True, exist_ok=True)
    _ = paso1_excel_a_tsv_long(gob_xlsx, control_dir)
    long = paso2b_cargar_long_desde_tsv(control_dir)

    # Paso 2
    print('\n🔍 Paso 2: Detectar superposiciones...')
    sup = paso2_detectar_superposiciones(long)

    if len(sup) == 0:
        print('\n  ℹ️  Sin superposiciones detectadas. No se generan artefactos adicionales.')
        validaciones_finales(pd.DataFrame(), sup, control_dir, output_dir)
        return

    # Paso 3
    print('\n🔗 Paso 3: Cruce con universo real...')
    afectados = paso3_cruce_universo_real(input_path, sup)

    # Paso 4
    print('\n📝 Paso 4: Generar artefactos de gobernanza...')
    paso4_generar_outputs(afectados, sup, gob_xlsx, output_dir)

    # Validaciones
    validaciones_finales(afectados, sup, control_dir, output_dir)


if __name__ == '__main__':
    main()

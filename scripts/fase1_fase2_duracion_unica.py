from __future__ import annotations

from pathlib import Path
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DUR_PATH = BASE / 'DURACION_ESTUDIOS.tsv'
MAT_PATH = BASE / 'matriz_desambiguacion_sies_final.tsv'
PUE_PATH = BASE / 'puente_sies.tsv'
BACKFILL_PATH = BASE / 'control' / 'pendientes' / 'backfill_duracion_desde_matriz.tsv'
REPORTE_PATH = BASE / 'control' / 'reportes' / 'reporte_fase1_fase2_duracion_unica.tsv'

CONTRACT_COLS = [
    'CODCARPR_CANONICO',
    'CODCARPR_ALIAS_LIST',
    'REGLA_DESAMBIGUACION',
    'FUENTE_GOBERNANZA',
    'ESTADO_REGISTRO',
]


def ensure_dirs() -> None:
    BACKFILL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dur = pd.read_csv(DUR_PATH, sep='\t', dtype=str).fillna('')
    mat = pd.read_csv(MAT_PATH, sep='\t', dtype=str).fillna('')
    pue = pd.read_csv(PUE_PATH, sep='\t', dtype=str).fillna('')
    return dur, mat, pue


def apply_contract_columns(dur: pd.DataFrame, mat: pd.DataFrame) -> pd.DataFrame:
    out = dur.copy()
    for c in CONTRACT_COLS:
        if c not in out.columns:
            out[c] = ''

    # Completar columnas que no requieren inferencias riesgosas.
    out['FUENTE_GOBERNANZA'] = out['FUENTE_GOBERNANZA'].replace('', 'DURACION_ESTUDIOS')
    out['ESTADO_REGISTRO'] = out['ESTADO_REGISTRO'].replace('', 'ACTIVO')

    # CODCARPR_CANONICO: solo si hay 1 unico CODCARPR para el CODIGO_SIES_FINAL.
    canon = (
        mat.groupby('CODIGO_SIES_FINAL')['CODCARPR']
        .agg(lambda s: sorted(set(s)))
        .to_dict()
    )

    def pick_canon(codigo: str) -> str:
        vals = canon.get(codigo, [])
        return vals[0] if len(vals) == 1 else ''

    out['CODCARPR_CANONICO'] = out.apply(
        lambda r: r['CODCARPR_CANONICO'] if r['CODCARPR_CANONICO'] else pick_canon(r['CODIGO_UNICO']),
        axis=1,
    )

    # Alias list: solo cuando hay multiples CODCARPR en matriz para el mismo codigo unico.
    def alias_list(codigo: str) -> str:
        vals = canon.get(codigo, [])
        return '|'.join(vals) if len(vals) > 1 else ''

    out['CODCARPR_ALIAS_LIST'] = out.apply(
        lambda r: r['CODCARPR_ALIAS_LIST'] if r['CODCARPR_ALIAS_LIST'] else alias_list(r['CODIGO_UNICO']),
        axis=1,
    )

    # Regla de desambiguacion por defecto, editable.
    out['REGLA_DESAMBIGUACION'] = out['REGLA_DESAMBIGUACION'].replace('', 'MATRIZ_VIGENTE_O_REVISION_MANUAL')

    return out


def build_backfill_queue(dur: pd.DataFrame, mat: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(set(mat['CODIGO_SIES_FINAL']) - set(dur['CODIGO_UNICO']))
    pending = mat[mat['CODIGO_SIES_FINAL'].isin(missing)].copy()

    # Dedupe por codigo final para no repetir trabajo de carga.
    pending = pending.sort_values(['CODIGO_SIES_FINAL', 'CONFIANZA'], ascending=[True, False])
    pending = pending.drop_duplicates(subset=['CODIGO_SIES_FINAL'], keep='first')

    pending = pending.rename(columns={'CODIGO_SIES_FINAL': 'CODIGO_UNICO'})
    pending.insert(0, 'MOTIVO_BACKFILL', 'FALTA_EN_DURACION_ESTUDIOS')
    pending.insert(1, 'COMPLETAR_MANUAL', 'SI')

    ordered = [
        'MOTIVO_BACKFILL',
        'COMPLETAR_MANUAL',
        'CODIGO_UNICO',
        'CODCARPR',
        'TIPO_CARRERA',
        'JORNADA',
        'VERSION',
        'CONFIANZA',
        'NOTAS',
    ]
    return pending[ordered].reset_index(drop=True)


def build_report(dur: pd.DataFrame, mat: pd.DataFrame, pue: pd.DataFrame, backfill: pd.DataFrame) -> pd.DataFrame:
    mat_codes = set(mat['CODIGO_SIES_FINAL'])
    pue_codes = set(pue['CODIGO_CARRERA_SIES'])
    dur_codes = set(dur['CODIGO_UNICO'])

    rows = [
        ('duracion_filas', str(len(dur))),
        ('matriz_filas', str(len(mat))),
        ('puente_filas', str(len(pue))),
        ('duracion_codigos_unicos', str(len(dur_codes))),
        ('matriz_codigos_unicos', str(len(mat_codes))),
        ('puente_codigos_unicos', str(len(pue_codes))),
        ('faltantes_matriz_en_duracion', str(len(mat_codes - dur_codes))),
        ('faltantes_puente_en_duracion', str(len(pue_codes - dur_codes))),
        ('backfill_pendiente', str(len(backfill))),
        ('contrato_cols_presentes', str(all(c in dur.columns for c in CONTRACT_COLS))),
    ]
    return pd.DataFrame(rows, columns=['metrica', 'valor'])


def main() -> None:
    ensure_dirs()
    dur, mat, pue = load()

    dur2 = apply_contract_columns(dur, mat)
    dur2.to_csv(DUR_PATH, sep='\t', index=False)

    backfill = build_backfill_queue(dur2, mat)
    backfill.to_csv(BACKFILL_PATH, sep='\t', index=False)

    report = build_report(dur2, mat, pue, backfill)
    report.to_csv(REPORTE_PATH, sep='\t', index=False)

    print('FASE 1+2 DURACION UNICA')
    print(f'Contrato aplicado en: {DUR_PATH}')
    print(f'Backfill pendiente: {BACKFILL_PATH} ({len(backfill)} filas)')
    print(f'Reporte: {REPORTE_PATH}')


if __name__ == '__main__':
    main()

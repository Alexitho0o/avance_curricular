from __future__ import annotations

from pathlib import Path
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DUR_PATH = BASE / 'DURACION_ESTUDIOS.tsv'
MAT_PATH = BASE / 'matriz_desambiguacion_sies_final.tsv'
PUE_PATH = BASE / 'puente_sies.tsv'
OUT_XLSX_PATH = BASE / 'resultados' / 'archivo_listo_para_sies.xlsx'

CATALOGO_PATH = BASE / 'control' / 'reportes' / 'catalogo_resolucion_codcarpr_fase3.tsv'
AMB_PATH = BASE / 'control' / 'pendientes' / 'codcarpr_resolucion_ambigua_fase3.tsv'
REP_PATH = BASE / 'control' / 'reportes' / 'reporte_fase3_resolucion_codcarpr.tsv'


def ensure_dirs() -> None:
    CATALOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
    AMB_PATH.parent.mkdir(parents=True, exist_ok=True)
    REP_PATH.parent.mkdir(parents=True, exist_ok=True)


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dur = pd.read_csv(DUR_PATH, sep='\t', dtype=str).fillna('')
    mat = pd.read_csv(MAT_PATH, sep='\t', dtype=str).fillna('')
    pue = pd.read_csv(PUE_PATH, sep='\t', dtype=str).fillna('')
    return dur, mat, pue


def build_resolution_catalog(dur: pd.DataFrame, mat: pd.DataFrame) -> pd.DataFrame:
    ref = (
        mat.groupby('CODIGO_SIES_FINAL')['CODCARPR']
        .agg(lambda s: sorted(set(v for v in s if v)))
        .to_dict()
    )

    rows = []
    for row in dur.itertuples(index=False):
        codigo = row.CODIGO_UNICO
        cods = ref.get(codigo, [])
        n = len(cods)
        if n == 0:
            estado = 'SIN_REFERENCIA_MATRIZ'
            canon = ''
            alias = ''
        elif n == 1:
            estado = 'UNICO'
            canon = cods[0]
            alias = ''
        else:
            estado = 'AMBIGUO'
            canon = ''
            alias = '|'.join(cods)

        rows.append({
            'CODIGO_UNICO': codigo,
            'CODCARPR_CANONICO_FASE3': canon,
            'CODCARPR_ALIAS_LIST_FASE3': alias,
            'ESTADO_RESOLUCION_FASE3': estado,
            'N_CODCARPR_REF': str(n),
            'CODCARPR_REF_LIST': '|'.join(cods),
            'FUENTE_REFERENCIA': 'MATRIZ_DESAMBIGUACION_SIES_FINAL',
        })

    cat = pd.DataFrame(rows)
    return cat


def apply_resolution_to_duracion(dur: pd.DataFrame, cat: pd.DataFrame) -> pd.DataFrame:
    out = dur.copy()

    for c in ['CODCARPR_CANONICO', 'CODCARPR_ALIAS_LIST']:
        if c not in out.columns:
            out[c] = ''

    if 'CODCARPR_RESOLUCION_ESTADO' not in out.columns:
        out['CODCARPR_RESOLUCION_ESTADO'] = ''

    cidx = cat.set_index('CODIGO_UNICO')

    def canon_for(codigo: str, previo: str) -> str:
        if previo:
            return previo
        val = cidx.at[codigo, 'CODCARPR_CANONICO_FASE3'] if codigo in cidx.index else ''
        return val

    def alias_for(codigo: str, previo: str) -> str:
        if previo:
            return previo
        val = cidx.at[codigo, 'CODCARPR_ALIAS_LIST_FASE3'] if codigo in cidx.index else ''
        return val

    def estado_for(codigo: str) -> str:
        if codigo not in cidx.index:
            return 'SIN_REFERENCIA_MATRIZ'
        return cidx.at[codigo, 'ESTADO_RESOLUCION_FASE3']

    out['CODCARPR_CANONICO'] = [canon_for(c, p) for c, p in zip(out['CODIGO_UNICO'], out['CODCARPR_CANONICO'])]
    out['CODCARPR_ALIAS_LIST'] = [alias_for(c, p) for c, p in zip(out['CODIGO_UNICO'], out['CODCARPR_ALIAS_LIST'])]
    out['CODCARPR_RESOLUCION_ESTADO'] = [estado_for(c) for c in out['CODIGO_UNICO']]

    return out


def validate_with_output_xlsx(cat: pd.DataFrame) -> dict[str, str]:
    metrics: dict[str, str] = {}
    if not OUT_XLSX_PATH.exists():
        metrics['output_xlsx_present'] = 'False'
        return metrics

    stage = pd.read_excel(OUT_XLSX_PATH, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    if 'CODIGO_CARRERA_SIES_FINAL' not in stage.columns:
        metrics['output_xlsx_present'] = 'True'
        metrics['output_col_present'] = 'False'
        return metrics

    codigos_out = set(v for v in stage['CODIGO_CARRERA_SIES_FINAL'] if v)
    cat_idx = cat.set_index('CODIGO_UNICO')

    miss = sorted(c for c in codigos_out if c not in cat_idx.index)
    not_unique = sorted(
        c for c in codigos_out
        if c in cat_idx.index and cat_idx.at[c, 'ESTADO_RESOLUCION_FASE3'] != 'UNICO'
    )

    metrics['output_xlsx_present'] = 'True'
    metrics['output_col_present'] = 'True'
    metrics['output_codigos_unicos'] = str(len(codigos_out))
    metrics['output_codigos_no_en_duracion'] = str(len(miss))
    metrics['output_codigos_no_unicos'] = str(len(not_unique))
    return metrics


def build_report(dur: pd.DataFrame, mat: pd.DataFrame, pue: pd.DataFrame, cat: pd.DataFrame, out_metrics: dict[str, str]) -> pd.DataFrame:
    dur_codes = set(dur['CODIGO_UNICO'])
    mat_codes = set(mat['CODIGO_SIES_FINAL'])
    pue_codes = set(pue['CODIGO_CARRERA_SIES'])

    s = cat['ESTADO_RESOLUCION_FASE3'].value_counts().to_dict()

    rows = [
        ('duracion_filas', str(len(dur))),
        ('duracion_codigos_unicos', str(len(dur_codes))),
        ('matriz_codigos_unicos', str(len(mat_codes))),
        ('puente_codigos_unicos', str(len(pue_codes))),
        ('resolucion_unico', str(s.get('UNICO', 0))),
        ('resolucion_ambiguo', str(s.get('AMBIGUO', 0))),
        ('resolucion_sin_referencia', str(s.get('SIN_REFERENCIA_MATRIZ', 0))),
        ('faltantes_matriz_en_duracion', str(len(mat_codes - dur_codes))),
        ('faltantes_puente_en_duracion', str(len(pue_codes - dur_codes))),
    ]
    for k, v in out_metrics.items():
        rows.append((k, v))

    return pd.DataFrame(rows, columns=['metrica', 'valor'])


def main() -> None:
    ensure_dirs()
    dur, mat, pue = load()

    cat = build_resolution_catalog(dur, mat)
    cat.to_csv(CATALOGO_PATH, sep='\t', index=False)

    dur2 = apply_resolution_to_duracion(dur, cat)
    dur2.to_csv(DUR_PATH, sep='\t', index=False)

    amb = cat[cat['ESTADO_RESOLUCION_FASE3'] != 'UNICO'].copy()
    amb.to_csv(AMB_PATH, sep='\t', index=False)

    out_metrics = validate_with_output_xlsx(cat)
    rep = build_report(dur2, mat, pue, cat, out_metrics)
    rep.to_csv(REP_PATH, sep='\t', index=False)

    print('FASE 3 RESOLUCION CODCARPR')
    print(f'Catalogo: {CATALOGO_PATH}')
    print(f'Pendientes/ambiguos: {AMB_PATH} ({len(amb)} filas)')
    print(f'Reporte: {REP_PATH}')


if __name__ == '__main__':
    main()

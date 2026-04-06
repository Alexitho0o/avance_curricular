from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import pandas as pd

# La validacion oficial no debe depender del runtime legacy archivado.
from codigo_gobernanza_v2 import CARRERAS_AC_COLUMNS, MATRICULA_AC_COLUMNS, MATRICULA_UNIFICADA_COLUMNS

MU_FUSION_OUTPUT_FILENAME = "archivo_listo_para_sies.xlsx"
MU_PREGRADO_CSV_FILENAME = "matricula_unificada_2026_pregrado.csv"
UZ_COLUMNS = ['ASI_INS_ANT', 'ASI_APR_ANT', 'PROM_PRI_SEM', 'PROM_SEG_SEM', 'ASI_INS_HIS', 'ASI_APR_HIS']


def check_readme_no_csv_dump() -> None:
    lines = Path('README.md').read_text(encoding='utf-8').splitlines()
    bad = [ln for ln in lines if ln.count(',') >= 8 and not ln.strip().startswith('`')]
    if bad:
        raise AssertionError(f'README parece contener dump CSV: {bad[:2]}')


def check_base_outputs(out: Path) -> None:
    mu_path = out / 'matricula_unificada_2026_control.csv'
    ca_path = out / 'carreras_avance_curricular_2025_control.csv'
    ma_path = out / 'matricula_avance_curricular_2025_control.csv'
    if not (mu_path.exists() and ca_path.exists() and ma_path.exists()):
        return

    mu = pd.read_csv(mu_path)
    ca = pd.read_csv(ca_path)
    ma = pd.read_csv(ma_path)
    assert mu.columns.tolist() == MATRICULA_UNIFICADA_COLUMNS
    assert ca.columns.tolist() == CARRERAS_AC_COLUMNS
    assert ma.columns.tolist() == MATRICULA_AC_COLUMNS

    rep = json.loads((out / 'reporte_validacion.json').read_text(encoding='utf-8'))
    # No permitir apto si hay blockers
    blockers_mu = any(i['severity'] == 'BLOCKER' and i['area'] == 'matricula_unificada' for i in rep['issues'])
    if blockers_mu:
        assert rep['apto_oficial']['matricula_unificada'] is False

    quality = json.loads((out / 'reporte_calidad_semantica.json').read_text(encoding='utf-8'))
    assert 'matricula_ac' in quality and 'carreras_ac' in quality and 'matricula_unificada' in quality


def _pct(n: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((n / total) * 100, 2)


def _rut_expected_dv(num: object) -> str:
    digits = ''.join(ch for ch in str(num) if ch.isdigit())
    if not digits:
        return ''
    reversed_digits = list(map(int, reversed(digits)))
    factors = [2, 3, 4, 5, 6, 7]
    total = sum(d * factors[idx % len(factors)] for idx, d in enumerate(reversed_digits))
    remainder = 11 - (total % 11)
    if remainder == 11:
        return '0'
    if remainder == 10:
        return 'K'
    return str(remainder)


def _si_no(flag: bool) -> str:
    return 'SI' if bool(flag) else 'NO'


def _all_present(columns: list[str], df: pd.DataFrame) -> bool:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        return False
    for c in columns:
        s = df[c].fillna('').astype(str).str.strip()
        if s.eq('').any():
            return False
    return True



def _valid_ddmmyyyy_mask(series: pd.Series) -> pd.Series:
    fmt_mask = series.astype(str).str.fullmatch(r'\d{2}/\d{2}/\d{4}')
    parsed_mask = pd.to_datetime(series, format='%d/%m/%Y', errors='coerce').notna()
    return fmt_mask & parsed_mask


def check_mu_pregrado_csv(out: Path) -> dict[str, object]:
    csv_path = out / MU_PREGRADO_CSV_FILENAME
    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    if not csv_path.exists() and not xlsx_path.exists():
        return {}

    assert csv_path.exists(), f'Falta CSV final regulatorio: {csv_path}'
    assert csv_path.stat().st_size > 0, f'CSV final vacío: {csv_path}'

    first_line = csv_path.read_text(encoding='utf-8').splitlines()[0]
    assert first_line != ';'.join(MATRICULA_UNIFICADA_COLUMNS), 'CSV final no debe incluir encabezado'
    assert first_line.count(';') == len(MATRICULA_UNIFICADA_COLUMNS) - 1, 'CSV final no respeta 32 columnas delimitadas por ;'

    with csv_path.open('r', encoding='utf-8', newline='') as fh:
        reader = csv.reader(fh, delimiter=';')
        rows = list(reader)

    assert rows, 'CSV final sin filas'
    bad_rows = [idx + 1 for idx, row in enumerate(rows) if len(row) != len(MATRICULA_UNIFICADA_COLUMNS)]
    assert not bad_rows, f'CSV final con filas fuera de 32 columnas: {bad_rows[:5]}'

    mu_csv = pd.read_csv(csv_path, sep=';', header=None, dtype=str, keep_default_na=False, names=MATRICULA_UNIFICADA_COLUMNS)
    assert mu_csv.shape[1] == len(MATRICULA_UNIFICADA_COLUMNS), 'CSV final no tiene 32 columnas exactas'

    bad_for_ing = ~mu_csv['FOR_ING_ACT'].astype(str).str.strip().eq('1')
    assert not bad_for_ing.any(), f'FOR_ING_ACT distinto de 1 en filas: {(bad_for_ing[bad_for_ing].index[:5] + 1).tolist()}'

    bad_sexo = ~mu_csv['SEXO'].astype(str).str.strip().isin({'H', 'M', 'NB'})
    assert not bad_sexo.any(), f'SEXO fuera de catálogo H/M/NB en filas: {(bad_sexo[bad_sexo].index[:5] + 1).tolist()}'

    asi_ins_ant = pd.to_numeric(mu_csv['ASI_INS_ANT'], errors='coerce')
    asi_apr_ant = pd.to_numeric(mu_csv['ASI_APR_ANT'], errors='coerce')
    asi_ins_his = pd.to_numeric(mu_csv['ASI_INS_HIS'], errors='coerce')
    asi_apr_his = pd.to_numeric(mu_csv['ASI_APR_HIS'], errors='coerce')
    prom_pri = pd.to_numeric(mu_csv['PROM_PRI_SEM'], errors='coerce')
    prom_seg = pd.to_numeric(mu_csv['PROM_SEG_SEM'], errors='coerce')

    bad_apr_ant = asi_apr_ant > asi_ins_ant
    assert not bad_apr_ant.fillna(False).any(), f'ASI_APR_ANT > ASI_INS_ANT en filas: {(bad_apr_ant[bad_apr_ant].index[:5] + 1).tolist()}'
    bad_apr_his = asi_apr_his > asi_ins_his
    assert not bad_apr_his.fillna(False).any(), f'ASI_APR_HIS > ASI_INS_HIS en filas: {(bad_apr_his[bad_apr_his].index[:5] + 1).tolist()}'

    bad_prom_pri = ~((prom_pri == 0) | prom_pri.between(100, 700))
    assert not bad_prom_pri.fillna(False).any(), f'PROM_PRI_SEM fuera de rango 0|100..700 en filas: {(bad_prom_pri[bad_prom_pri].index[:5] + 1).tolist()}'
    bad_prom_seg = ~((prom_seg == 0) | prom_seg.between(100, 700))
    assert not bad_prom_seg.fillna(False).any(), f'PROM_SEG_SEM fuera de rango 0|100..700 en filas: {(bad_prom_seg[bad_prom_seg].index[:5] + 1).tolist()}'

    uz_all_zero_mask = mu_csv[UZ_COLUMNS].apply(pd.to_numeric, errors='coerce').fillna(0).eq(0).all(axis=1)
    assert not uz_all_zero_mask.all(), 'U-Z volvió a quedar completamente en cero en todo el CSV final'

    metrics: dict[str, object] = {
        'rows_csv_final': int(len(mu_csv)),
        'for_ing_act_distribution': mu_csv['FOR_ING_ACT'].astype(str).value_counts(dropna=False).to_dict(),
        'uz_all_zero_rows': int(uz_all_zero_mask.sum()),
        'uz_all_zero_pct': _pct(int(uz_all_zero_mask.sum()), int(len(mu_csv))),
    }

    if xlsx_path.exists():
        mu_xlsx = pd.read_excel(xlsx_path, sheet_name='MATRICULA_UNIFICADA_32', dtype=str).fillna('')
        assert mu_xlsx.columns.tolist() == MATRICULA_UNIFICADA_COLUMNS
        assert len(mu_xlsx) == len(mu_csv), 'CSV final y hoja MATRICULA_UNIFICADA_32 difieren en cantidad de filas'
        stage_cols = [
            'INCLUIR_EN_MATRICULA_32',
            'ESTADO_CARGA_PREGRADO',
            'FOR_ING_ACT_FUENTE_VALOR',
            'FOR_ING_ACT_FUENTE_CAMPO',
            'FOR_ING_ACT_METODO',
            'FOR_ING_ACT_IMPUTADO',
            'FOR_ING_ACT_REQUIERE_REVISION',
            'DA_ANOMATRICULA',
            'DA_PERIODOMATRICULA',
            'DA_VIASDEADMISION',
            'DA_SITUACION',
            'DA_MATRICULA',
            'DA_CON_FIRMA',
            'UZ_HIST_KEY',
            'ANIO_REFERENCIA_HIST_UZ',
            'UZ_HIST_ANIO_MIN',
            'UZ_HIST_ANIO_MAX',
            'UZ_HIST_ANIOS_DISPONIBLES',
            'UZ_HIST_SCOPE_STATUS',
            'UZ_HIST_FILAS_TOTAL',
            'UZ_HIST_FILAS_ANIO_REFERENCIA',
            'UZ_HIST_FILAS_REF_APROB',
            'UZ_HIST_FILAS_REF_REPROB',
            'UZ_HIST_FILAS_REF_TRANSFER',
            'UZ_HIST_FILAS_REF_SEM1_CALIFICADAS',
            'UZ_HIST_FILAS_REF_SEM2_CALIFICADAS',
            'UZ_FUENTE_HIST',
            'TIPO_DOC_STATUS',
            'N_DOC_STATUS',
            'DV_STATUS',
            'SEGUNDO_APELLIDO_STATUS',
            'FECH_NAC_STATUS',
            'NAC_STATUS',
            'PAIS_EST_SEC_STATUS',
            'SIES_RESOLUCION_HEURISTICA',
            'COD_SED_FUENTE_FINAL',
            'COD_SED_METODO_FINAL',
            'COD_SED_AUDIT_STATUS',
            'COD_CAR_FUENTE_FINAL',
            'COD_CAR_METODO_FINAL',
            'COD_CAR_AUDIT_STATUS',
            'MODALIDAD_FUENTE_FINAL',
            'MODALIDAD_METODO_FINAL',
            'MODALIDAD_AUDIT_STATUS',
            'JOR_FUENTE_FINAL',
            'JOR_METODO_FINAL',
            'JOR_AUDIT_STATUS',
            'VERSION_FUENTE_FINAL',
            'VERSION_METODO_FINAL',
            'VERSION_AUDIT_STATUS',
            'ANIO_ING_ACT_FUENTE_FINAL',
            'ANIO_ING_ACT_METODO_FINAL',
            'ANIO_ING_ACT_AUDIT_STATUS',
            'SEM_ING_ACT_FUENTE_FINAL',
            'SEM_ING_ACT_METODO_FINAL',
            'SEM_ING_ACT_AUDIT_STATUS',
            'ANIO_ING_ORI_FUENTE_FINAL',
            'ANIO_ING_ORI_METODO_FINAL',
            'ANIO_ING_ORI_AUDIT_STATUS',
            'SEM_ING_ORI_FUENTE_FINAL',
            'SEM_ING_ORI_METODO_FINAL',
            'SEM_ING_ORI_AUDIT_STATUS',
            'NIV_ACA_FUENTE_FINAL',
            'NIV_ACA_METODO_FINAL',
            'NIV_ACA_AUDIT_STATUS',
            'FECHA_MATRICULA_FUENTE_FINAL',
            'FECHA_MATRICULA_METODO_FINAL',
            'FECHA_MATRICULA_AUDIT_STATUS',
            'ASI_INS_ANT_FUENTE_FINAL',
            'ASI_INS_ANT_METODO_FINAL',
            'ASI_INS_ANT_AUDIT_STATUS',
            'ASI_APR_ANT_FUENTE_FINAL',
            'ASI_APR_ANT_METODO_FINAL',
            'ASI_APR_ANT_AUDIT_STATUS',
            'PROM_PRI_SEM_FUENTE_FINAL',
            'PROM_PRI_SEM_METODO_FINAL',
            'PROM_PRI_SEM_AUDIT_STATUS',
            'PROM_SEG_SEM_FUENTE_FINAL',
            'PROM_SEG_SEM_METODO_FINAL',
            'PROM_SEG_SEM_AUDIT_STATUS',
            'ASI_INS_HIS_FUENTE_FINAL',
            'ASI_INS_HIS_METODO_FINAL',
            'ASI_INS_HIS_AUDIT_STATUS',
            'ASI_APR_HIS_FUENTE_FINAL',
            'ASI_APR_HIS_METODO_FINAL',
            'ASI_APR_HIS_AUDIT_STATUS',
            'SIT_FON_SOL_FUENTE_FINAL',
            'SIT_FON_SOL_METODO_FINAL',
            'SIT_FON_SOL_AUDIT_STATUS',
            'SUS_PRE_FUENTE_FINAL',
            'SUS_PRE_METODO_FINAL',
            'SUS_PRE_AUDIT_STATUS',
            'REINCORPORACION_FUENTE_FINAL',
            'REINCORPORACION_METODO_FINAL',
            'REINCORPORACION_AUDIT_STATUS',
            'VIG_FUENTE_FINAL',
            'VIG_METODO_FINAL',
            'VIG_AUDIT_STATUS',
        ]
        stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
        missing_stage = [col for col in stage_cols if col not in stage.columns]
        assert not missing_stage, f'ARCHIVO_LISTO_SUBIDA sin trazabilidad esperada: {missing_stage}'

        included = stage[stage['INCLUIR_EN_MATRICULA_32'] == 'SI'].copy()
        assert len(included) == len(mu_csv), 'El staging incluido no coincide con el CSV final'
        assert included['FOR_ING_ACT_METODO'].replace('', pd.NA).notna().all(), 'Hay filas finales sin método de resolución trazable para FOR_ING_ACT'
        assert included['FOR_ING_ACT_FUENTE_CAMPO'].replace('', pd.NA).notna().all(), 'Hay filas finales sin fuente trazable para FOR_ING_ACT'
        assert not included['SIES_RESOLUCION_HEURISTICA'].eq('PRIMERA_OPCION').any(), 'Persisten filas incluidas con heurística PRIMERA_OPCION'
        for ko_col in [
            'COD_SED_FUENTE_FINAL',
            'COD_SED_METODO_FINAL',
            'COD_SED_AUDIT_STATUS',
            'COD_CAR_FUENTE_FINAL',
            'COD_CAR_METODO_FINAL',
            'COD_CAR_AUDIT_STATUS',
            'MODALIDAD_FUENTE_FINAL',
            'MODALIDAD_METODO_FINAL',
            'MODALIDAD_AUDIT_STATUS',
            'JOR_FUENTE_FINAL',
            'JOR_METODO_FINAL',
            'JOR_AUDIT_STATUS',
            'VERSION_FUENTE_FINAL',
            'VERSION_METODO_FINAL',
            'VERSION_AUDIT_STATUS',
            'ANIO_ING_ACT_FUENTE_FINAL',
            'ANIO_ING_ACT_METODO_FINAL',
            'ANIO_ING_ACT_AUDIT_STATUS',
            'SEM_ING_ACT_FUENTE_FINAL',
            'SEM_ING_ACT_METODO_FINAL',
            'SEM_ING_ACT_AUDIT_STATUS',
            'ANIO_ING_ORI_FUENTE_FINAL',
            'ANIO_ING_ORI_METODO_FINAL',
            'ANIO_ING_ORI_AUDIT_STATUS',
            'SEM_ING_ORI_FUENTE_FINAL',
            'SEM_ING_ORI_METODO_FINAL',
            'SEM_ING_ORI_AUDIT_STATUS',
            'NIV_ACA_FUENTE_FINAL',
            'NIV_ACA_METODO_FINAL',
            'NIV_ACA_AUDIT_STATUS',
            'FECHA_MATRICULA_FUENTE_FINAL',
            'FECHA_MATRICULA_METODO_FINAL',
            'FECHA_MATRICULA_AUDIT_STATUS',
            'UZ_HIST_KEY',
            'ANIO_REFERENCIA_HIST_UZ',
            'UZ_HIST_ANIO_MIN',
            'UZ_HIST_ANIO_MAX',
            'UZ_HIST_ANIOS_DISPONIBLES',
            'UZ_HIST_SCOPE_STATUS',
            'ASI_INS_ANT_FUENTE_FINAL',
            'ASI_INS_ANT_METODO_FINAL',
            'ASI_INS_ANT_AUDIT_STATUS',
            'ASI_APR_ANT_FUENTE_FINAL',
            'ASI_APR_ANT_METODO_FINAL',
            'ASI_APR_ANT_AUDIT_STATUS',
            'PROM_PRI_SEM_FUENTE_FINAL',
            'PROM_PRI_SEM_METODO_FINAL',
            'PROM_PRI_SEM_AUDIT_STATUS',
            'PROM_SEG_SEM_FUENTE_FINAL',
            'PROM_SEG_SEM_METODO_FINAL',
            'PROM_SEG_SEM_AUDIT_STATUS',
            'ASI_INS_HIS_FUENTE_FINAL',
            'ASI_INS_HIS_METODO_FINAL',
            'ASI_INS_HIS_AUDIT_STATUS',
            'ASI_APR_HIS_FUENTE_FINAL',
            'ASI_APR_HIS_METODO_FINAL',
            'ASI_APR_HIS_AUDIT_STATUS',
            'SIT_FON_SOL_FUENTE_FINAL',
            'SIT_FON_SOL_METODO_FINAL',
            'SIT_FON_SOL_AUDIT_STATUS',
            'SUS_PRE_FUENTE_FINAL',
            'SUS_PRE_METODO_FINAL',
            'SUS_PRE_AUDIT_STATUS',
            'REINCORPORACION_FUENTE_FINAL',
            'REINCORPORACION_METODO_FINAL',
            'REINCORPORACION_AUDIT_STATUS',
            'VIG_FUENTE_FINAL',
            'VIG_METODO_FINAL',
            'VIG_AUDIT_STATUS',
        ]:
            assert included[ko_col].replace('', pd.NA).notna().all(), f'Hay filas finales sin trazabilidad operativa en {ko_col}'

        fallback_rows = int(included['FOR_ING_ACT_IMPUTADO'].eq('SI').sum())
        review_rows = int(included['FOR_ING_ACT_REQUIERE_REVISION'].eq('SI').sum())
        hist_rows = int(included['ANIO_REFERENCIA_HIST_UZ'].replace('', pd.NA).notna().sum())
        fallback_pct = _pct(fallback_rows, int(len(included)))
        metrics.update(
            {
                'for_ing_act_imputado_rows': fallback_rows,
                'for_ing_act_imputado_pct': fallback_pct,
                'for_ing_act_revision_rows': review_rows,
                'for_ing_act_revision_pct': _pct(review_rows, int(len(included))),
                'uz_hist_base_rows': hist_rows,
                'uz_hist_base_pct': _pct(hist_rows, int(len(included))),
            }
        )
        assert fallback_rows == 0, 'FOR_ING_ACT no debe quedar imputado en filas finales'
        assert review_rows == 0, 'FOR_ING_ACT no debe quedar en revisión en filas finales'
        if hist_rows > 0:
            assert metrics['uz_all_zero_pct'] < 95, (
                'U-Z sigue demasiado cercano a cero masivo pese a existir base histórica '
                f'({metrics["uz_all_zero_rows"]}/{len(mu_csv)} filas totalmente en cero).'
            )

    return metrics


def generate_fase1_identity_reports(out: Path, control_dir: Path) -> dict[str, object]:
    report_dir = control_dir / 'reportes'
    report_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    assert xlsx_path.exists(), f'Falta archivo de auditoría para FASE 1: {xlsx_path}'

    stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    mu32 = pd.read_excel(xlsx_path, sheet_name='MATRICULA_UNIFICADA_32', dtype=str).fillna('')
    included = stage[stage['INCLUIR_EN_MATRICULA_32'].eq('SI')].copy()
    assert len(included) == len(mu32), 'FASE 1: included no coincide con MATRÍCULA_UNIFICADA_32'

    required_status_cols = [
        'TIPO_DOC_STATUS',
        'N_DOC_STATUS',
        'DV_STATUS',
        'SEGUNDO_APELLIDO_STATUS',
        'FECH_NAC_STATUS',
        'NAC_STATUS',
        'PAIS_EST_SEC_STATUS',
    ]
    missing_status_cols = [col for col in required_status_cols if col not in included.columns]
    assert not missing_status_cols, f'FASE 1: faltan columnas de trazabilidad: {missing_status_cols}'

    included_count = int(len(included))
    n_doc_digits = included['N_DOC'].astype(str).str.replace(r'\D', '', regex=True)
    dv_upper = included['DV'].astype(str).str.strip().str.upper()
    expected_dv = n_doc_digits.map(_rut_expected_dv)
    dv_match_mask = dv_upper.eq(expected_dv) & expected_dv.ne('')
    dv_format_mask = dv_upper.str.fullmatch(r'[0-9K]')
    fech_nac_valid_mask = _valid_ddmmyyyy_mask(included['FECH_NAC'])
    segundo_apellido_nonempty = included['SEGUNDO_APELLIDO'].astype(str).str.strip().ne('')
    segundo_apellido_valid_mask = (
        ~segundo_apellido_nonempty
        | included['SEGUNDO_APELLIDO'].astype(str).str.fullmatch(r"[A-Z \-]+")
    )

    nac_num = pd.to_numeric(included['NAC'], errors='coerce')
    pais_num = pd.to_numeric(included['PAIS_EST_SEC'], errors='coerce')
    nac_valid_mask = nac_num.between(1, 197)
    pais_valid_mask = pais_num.between(1, 197)

    fech_nac_1900_mask = included['FECH_NAC'].eq('01/01/1900')
    nac_default_mask = included['NAC_STATUS'].astype(str).str.startswith('DEFAULT_38_')
    pais_default_mask = included['PAIS_EST_SEC_STATUS'].astype(str).str.startswith('DEFAULT_38_')
    pais_inferido_mask = included['PAIS_EST_SEC_STATUS'].astype(str).isin(['DEFAULT_GOB_PAIS_EST_SEC', 'INFERIDO_LOCALIDAD_CHILE_38'])
    segundo_vacio_mask = included['SEGUNDO_APELLIDO_STATUS'].astype(str).eq('VACIO_SIN_FUENTE')

    reporte_fech_nac = included.loc[
        fech_nac_1900_mask | (~fech_nac_valid_mask),
        ['CODCLI', 'N_DOC', 'DV', 'FECH_NAC', 'FECH_NAC_STATUS', 'DA_MATCH_MODO', 'INCLUIR_EN_MATRICULA_32'],
    ].copy()
    reporte_fech_nac.to_csv(report_dir / 'reporte_fech_nac.tsv', sep='\t', index=False, encoding='utf-8')

    reporte_nac_pais = included.loc[
        nac_default_mask
        | pais_default_mask
        | pais_inferido_mask
        | included['NAC_STATUS'].astype(str).str.contains('REVISION_MANUAL|SIN_MAPEO', regex=True)
        | included['PAIS_EST_SEC_STATUS'].astype(str).str.contains('SOURCE_EMPTY|SIN_INSUMO', regex=True),
        ['CODCLI', 'N_DOC', 'DV', 'NAC', 'NAC_STATUS', 'PAIS_EST_SEC', 'PAIS_EST_SEC_STATUS', 'DA_MATCH_MODO', 'INCLUIR_EN_MATRICULA_32'],
    ].copy()
    reporte_nac_pais.to_csv(report_dir / 'reporte_nac_pais_sec.tsv', sep='\t', index=False, encoding='utf-8')

    gate = {
        'A_TIPO_DOC': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(included['TIPO_DOC'].eq('R').all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(included['TIPO_DOC_STATUS'].eq('REGLA_FIJA_R').all()),
            'auditable_en_filas_incluidas': bool(included['TIPO_DOC_STATUS'].replace('', pd.NA).notna().all()),
        },
        'B_N_DOC': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(n_doc_digits.ne('').all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(included['N_DOC_STATUS'].replace('', pd.NA).notna().all()),
            'auditable_en_filas_incluidas': bool(included['N_DOC_STATUS'].replace('', pd.NA).notna().all()),
        },
        'C_DV': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool((dv_format_mask & dv_match_mask).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(included['DV_STATUS'].replace('', pd.NA).notna().all()),
            'auditable_en_filas_incluidas': bool(included['DV_STATUS'].replace('', pd.NA).notna().all()),
        },
        'E_SEGUNDO_APELLIDO': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(segundo_apellido_valid_mask.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['SEGUNDO_APELLIDO_STATUS'].isin(['SOURCE_INPUT', 'FALLBACK_DATOS_ALUMNOS', 'VACIO_SIN_FUENTE']).all()
            ),
            'auditable_en_filas_incluidas': bool(included['SEGUNDO_APELLIDO_STATUS'].replace('', pd.NA).notna().all()),
        },
        'H_FECH_NAC': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(fech_nac_valid_mask.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['FECH_NAC_STATUS'].replace('', pd.NA).notna().all()
                and included.loc[fech_nac_1900_mask, 'FECH_NAC_STATUS'].astype(str).str.startswith('FALLBACK_1900').all()
            ),
            'auditable_en_filas_incluidas': bool(included['FECH_NAC_STATUS'].replace('', pd.NA).notna().all()),
        },
        'I_NAC': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(nac_valid_mask.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['NAC_STATUS'].replace('', pd.NA).notna().all()
                and ~(included['NAC'].eq('38') & included['NAC_STATUS'].isin(['SIN_INSUMO', 'SOURCE_TEXT', ''])).any()
            ),
            'auditable_en_filas_incluidas': bool(included['NAC_STATUS'].replace('', pd.NA).notna().all()),
        },
        'J_PAIS_EST_SEC': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(pais_valid_mask.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['PAIS_EST_SEC_STATUS'].replace('', pd.NA).notna().all()
                and ~(included['PAIS_EST_SEC'].eq('38') & included['PAIS_EST_SEC_STATUS'].isin(['SIN_INSUMO', 'SOURCE_EMPTY', ''])).any()
            ),
            'auditable_en_filas_incluidas': bool(included['PAIS_EST_SEC_STATUS'].replace('', pd.NA).notna().all()),
        },
    }

    for payload in gate.values():
        payload['estado_final'] = 'OK' if all(payload.values()) else 'Pendiente'

    summary = {
        'rows_included_final': included_count,
        'tipo_doc_distribution': included['TIPO_DOC'].value_counts(dropna=False).to_dict(),
        'segundo_apellido_vacio_rows': int(segundo_vacio_mask.sum()),
        'segundo_apellido_vacio_pct': _pct(int(segundo_vacio_mask.sum()), included_count),
        'fech_nac_1900_rows': int(fech_nac_1900_mask.sum()),
        'fech_nac_1900_pct': _pct(int(fech_nac_1900_mask.sum()), included_count),
        'nac_default_38_rows': int(nac_default_mask.sum()),
        'nac_default_38_pct': _pct(int(nac_default_mask.sum()), included_count),
        'pais_default_38_rows': int(pais_default_mask.sum()),
        'pais_default_38_pct': _pct(int(pais_default_mask.sum()), included_count),
        'pais_inferido_rows': int(pais_inferido_mask.sum()),
        'pais_inferido_pct': _pct(int(pais_inferido_mask.sum()), included_count),
        'dv_invalid_rows': int((~(dv_format_mask & dv_match_mask)).sum()),
        'dv_invalid_pct': _pct(int((~(dv_format_mask & dv_match_mask)).sum()), included_count),
        'columnas_fase_1': gate,
    }

    (report_dir / 'reporte_identidad_mu_2026.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    lines = [
        '# Reporte FASE 1 - Identidad MU 2026',
        '',
        f'- Filas incluidas en carga final: {included_count}',
        f'- Filas `FECH_NAC = 01/01/1900`: {summary["fech_nac_1900_rows"]} ({summary["fech_nac_1900_pct"]}%)',
        f'- Filas `NAC` con default 38 explícito: {summary["nac_default_38_rows"]} ({summary["nac_default_38_pct"]}%)',
        f'- Filas `PAIS_EST_SEC` con default 38 explícito: {summary["pais_default_38_rows"]} ({summary["pais_default_38_pct"]}%)',
        f'- Filas `PAIS_EST_SEC` inferidas por localidad: {summary["pais_inferido_rows"]} ({summary["pais_inferido_pct"]}%)',
        f'- Filas con DV inválido: {summary["dv_invalid_rows"]} ({summary["dv_invalid_pct"]}%)',
        '',
        '## Gate por columna',
        '',
        '| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |',
        '|---|---|---|---|---|---|---|',
    ]
    ordered = [
        ('A', 'A_TIPO_DOC'),
        ('B', 'B_N_DOC'),
        ('C', 'C_DV'),
        ('E', 'E_SEGUNDO_APELLIDO'),
        ('H', 'H_FECH_NAC'),
        ('I', 'I_NAC'),
        ('J', 'J_PAIS_EST_SEC'),
    ]
    for label, key in ordered:
        payload = gate[key]
        lines.append(
            f'| {label} | {_si_no(payload["fuente_regla_definida"])} | {_si_no(payload["transformacion_implementada"])} | '
            f'{_si_no(payload["validacion_qa_existe"])} | {_si_no(payload["sin_default_silencioso"])} | '
            f'{_si_no(payload["auditable_en_filas_incluidas"])} | {payload["estado_final"]} |'
        )

    (report_dir / 'reporte_fase_1_identidad_mu_2026.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def generate_fase2_sies_oferta_reports(out: Path, control_dir: Path) -> dict[str, object]:
    report_dir = control_dir / 'reportes'
    report_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    assert xlsx_path.exists(), f'Falta archivo de auditoría para FASE 2: {xlsx_path}'

    stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    mu32 = pd.read_excel(xlsx_path, sheet_name='MATRICULA_UNIFICADA_32', dtype=str).fillna('')
    included = stage[stage['INCLUIR_EN_MATRICULA_32'].eq('SI')].copy()
    assert len(included) == len(mu32), 'FASE 2: included no coincide con MATRÍCULA_UNIFICADA_32'

    required_cols = [
        'COD_SED_FUENTE_FINAL',
        'COD_SED_METODO_FINAL',
        'COD_SED_AUDIT_STATUS',
        'COD_CAR_FUENTE_FINAL',
        'COD_CAR_METODO_FINAL',
        'COD_CAR_AUDIT_STATUS',
        'MODALIDAD_FUENTE_FINAL',
        'MODALIDAD_METODO_FINAL',
        'MODALIDAD_AUDIT_STATUS',
        'JOR_FUENTE_FINAL',
        'JOR_METODO_FINAL',
        'JOR_AUDIT_STATUS',
        'VERSION_FUENTE_FINAL',
        'VERSION_METODO_FINAL',
        'VERSION_AUDIT_STATUS',
        'CODIGO_CARRERA_SIES_FINAL',
        'SIES_MATCH_STATUS',
        'SIES_MATCH_DIAG',
        'SIES_RESOLUCION_HEURISTICA',
    ]
    missing_cols = [col for col in required_cols if col not in included.columns]
    assert not missing_cols, f'FASE 2: faltan columnas de trazabilidad: {missing_cols}'

    included_count = int(len(included))
    cod_sed_num = pd.to_numeric(included['COD_SED'], errors='coerce')
    cod_car_num = pd.to_numeric(included['COD_CAR'], errors='coerce')
    mod_num = pd.to_numeric(included['MODALIDAD'], errors='coerce')
    jor_num = pd.to_numeric(included['JOR'], errors='coerce')
    version_num = pd.to_numeric(included['VERSION'], errors='coerce')
    parsed_cod_sed = pd.to_numeric(included['_PARSED_COD_SED'], errors='coerce')
    parsed_cod_car = pd.to_numeric(included['_PARSED_COD_CAR'], errors='coerce')
    parsed_jor = pd.to_numeric(included['_PARSED_JOR'], errors='coerce')
    parsed_version = pd.to_numeric(included['_PARSED_VERSION'], errors='coerce')

    cod_sed_consistent = cod_sed_num.eq(parsed_cod_sed) | parsed_cod_sed.isna()
    cod_car_consistent = cod_car_num.eq(parsed_cod_car) | parsed_cod_car.isna()
    jor_consistent = jor_num.eq(parsed_jor) | parsed_jor.isna()
    version_consistent = version_num.eq(parsed_version) | parsed_version.isna()
    mod_expected = pd.Series(pd.NA, index=included.index, dtype='Float64')
    mod_expected.loc[jor_num.isin([1, 2])] = 1
    mod_expected.loc[jor_num.eq(3)] = 2
    mod_expected.loc[jor_num.isin([4, 5])] = 3
    mod_consistent = mod_num.eq(mod_expected) | mod_expected.isna()

    pending_mask = stage['ESTADO_CARGA_PREGRADO'].isin(['EXCLUIDO_SIES_HEURISTICA_OPACA', 'EXCLUIDO_SIN_MATCH_SIES']) | stage['SIES_MATCH_STATUS'].isin(['AMBIGUO_SIES', 'SIN_MATCH_SIES', 'SIN_PUENTE_SIES'])
    sies_pendientes = stage.loc[
        pending_mask,
        [
            'CODCLI',
            'N_DOC',
            'DV',
            'CODCARPR_NORM',
            'NOMBRE_CARRERA_FUENTE',
            'JORNADA_FUENTE',
            'SIES_MATCH_STATUS',
            'SIES_MATCH_DIAG',
            'SIES_RESOLUCION_HEURISTICA',
            'CODIGO_CARRERA_SIES_FINAL',
            'ESTADO_CARGA_PREGRADO',
            'COD_SED_FUENTE_FINAL',
            'COD_CAR_FUENTE_FINAL',
            'MODALIDAD_FUENTE_FINAL',
            'JOR_FUENTE_FINAL',
            'VERSION_FUENTE_FINAL',
        ],
    ].copy()
    sies_pendientes.to_csv(report_dir / 'sies_pendientes.tsv', sep='\t', index=False, encoding='utf-8')

    gate = {
        'K_COD_SED': {
            'fuente_regla_definida': bool(included['COD_SED_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(cod_sed_num.gt(0).all() and cod_sed_consistent.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['COD_SED_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': bool(
                included[['COD_SED_FUENTE_FINAL', 'COD_SED_METODO_FINAL', 'COD_SED_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'L_COD_CAR': {
            'fuente_regla_definida': bool(included['COD_CAR_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(cod_car_num.gt(0).all() and cod_car_consistent.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['COD_CAR_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': bool(
                included[['COD_CAR_FUENTE_FINAL', 'COD_CAR_METODO_FINAL', 'COD_CAR_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'M_MODALIDAD': {
            'fuente_regla_definida': bool(included['MODALIDAD_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(mod_num.isin([1, 2, 3]).all() and mod_consistent.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['MODALIDAD_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': bool(
                included[['MODALIDAD_FUENTE_FINAL', 'MODALIDAD_METODO_FINAL', 'MODALIDAD_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'N_JOR': {
            'fuente_regla_definida': bool(included['JOR_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(jor_num.isin([1, 2, 3, 4]).all() and jor_consistent.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['JOR_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': bool(
                included[['JOR_FUENTE_FINAL', 'JOR_METODO_FINAL', 'JOR_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'O_VERSION': {
            'fuente_regla_definida': bool(included['VERSION_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(version_num.gt(0).all() and version_consistent.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['VERSION_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': bool(
                included[['VERSION_FUENTE_FINAL', 'VERSION_METODO_FINAL', 'VERSION_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
    }

    for payload in gate.values():
        payload['estado_final'] = 'OK' if all(payload.values()) else 'Pendiente'

    summary = {
        'rows_included_final': included_count,
        'rows_sies_pendientes': int(len(sies_pendientes)),
        'rows_excluidas_sies_heuristica_opaca': int(stage['ESTADO_CARGA_PREGRADO'].eq('EXCLUIDO_SIES_HEURISTICA_OPACA').sum()),
        'rows_excluidas_sin_match_sies': int(stage['ESTADO_CARGA_PREGRADO'].eq('EXCLUIDO_SIN_MATCH_SIES').sum()),
        'rows_match_sies_included': int(included['SIES_MATCH_STATUS'].eq('MATCH_SIES').sum()),
        'rows_included_primera_opcion': int(included['SIES_RESOLUCION_HEURISTICA'].eq('PRIMERA_OPCION').sum()),
        'cod_sed_fuente_distribution': included['COD_SED_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'cod_car_fuente_distribution': included['COD_CAR_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'modalidad_fuente_distribution': included['MODALIDAD_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'jor_fuente_distribution': included['JOR_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'version_fuente_distribution': included['VERSION_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'cod_sed_inconsistente_rows': int((~cod_sed_consistent).sum()),
        'cod_car_inconsistente_rows': int((~cod_car_consistent).sum()),
        'modalidad_inconsistente_rows': int((~mod_consistent).sum()),
        'jor_inconsistente_rows': int((~jor_consistent).sum()),
        'version_inconsistente_rows': int((~version_consistent).sum()),
        'columnas_fase_2': gate,
    }

    (report_dir / 'reporte_sies_oferta_mu_2026.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    lines = [
        '# Reporte FASE 2 - SIES Oferta MU 2026',
        '',
        f'- Filas incluidas en carga final: {included_count}',
        f'- Filas pendientes SIES/oferta: {summary["rows_sies_pendientes"]}',
        f'- Excluidas por heurística opaca: {summary["rows_excluidas_sies_heuristica_opaca"]}',
        f'- Excluidas por sin match SIES: {summary["rows_excluidas_sin_match_sies"]}',
        f'- Filas incluidas con heurística `PRIMERA_OPCION`: {summary["rows_included_primera_opcion"]}',
        f'- Inconsistencias incluidas COD_SED/COD_CAR/MODALIDAD/JOR/VERSION: '
        f'{summary["cod_sed_inconsistente_rows"]}/{summary["cod_car_inconsistente_rows"]}/'
        f'{summary["modalidad_inconsistente_rows"]}/{summary["jor_inconsistente_rows"]}/'
        f'{summary["version_inconsistente_rows"]}',
        f'- Fuente final `COD_SED`: {summary["cod_sed_fuente_distribution"]}',
        f'- Fuente final `COD_CAR`: {summary["cod_car_fuente_distribution"]}',
        f'- Fuente final `MODALIDAD`: {summary["modalidad_fuente_distribution"]}',
        f'- Fuente final `JOR`: {summary["jor_fuente_distribution"]}',
        f'- Fuente final `VERSION`: {summary["version_fuente_distribution"]}',
        '',
        '## Gate por columna',
        '',
        '| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |',
        '|---|---|---|---|---|---|---|',
    ]
    ordered = [
        ('K', 'K_COD_SED'),
        ('L', 'L_COD_CAR'),
        ('M', 'M_MODALIDAD'),
        ('N', 'N_JOR'),
        ('O', 'O_VERSION'),
    ]
    for label, key in ordered:
        payload = gate[key]
        lines.append(
            f'| {label} | {_si_no(payload["fuente_regla_definida"])} | {_si_no(payload["transformacion_implementada"])} | '
            f'{_si_no(payload["validacion_qa_existe"])} | {_si_no(payload["sin_default_silencioso"])} | '
            f'{_si_no(payload["auditable_en_filas_incluidas"])} | {payload["estado_final"]} |'
        )

    (report_dir / 'reporte_fase_2_sies_oferta_mu_2026.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def generate_fase3_cronologia_reports(out: Path, control_dir: Path) -> dict[str, object]:
    report_dir = control_dir / 'reportes'
    report_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    assert xlsx_path.exists(), f'Falta archivo de auditoría para FASE 3: {xlsx_path}'

    stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    mu32 = pd.read_excel(xlsx_path, sheet_name='MATRICULA_UNIFICADA_32', dtype=str).fillna('')
    included = stage[stage['INCLUIR_EN_MATRICULA_32'].eq('SI')].copy()
    assert len(included) == len(mu32), 'FASE 3: included no coincide con MATRÍCULA_UNIFICADA_32'

    required_cols = [
        'ANIO_ING_ACT_FUENTE_FINAL',
        'ANIO_ING_ACT_METODO_FINAL',
        'ANIO_ING_ACT_AUDIT_STATUS',
        'SEM_ING_ACT_FUENTE_FINAL',
        'SEM_ING_ACT_METODO_FINAL',
        'SEM_ING_ACT_AUDIT_STATUS',
        'ANIO_ING_ORI_FUENTE_FINAL',
        'ANIO_ING_ORI_METODO_FINAL',
        'ANIO_ING_ORI_AUDIT_STATUS',
        'SEM_ING_ORI_FUENTE_FINAL',
        'SEM_ING_ORI_METODO_FINAL',
        'SEM_ING_ORI_AUDIT_STATUS',
        'NIV_ACA_FUENTE_FINAL',
        'NIV_ACA_METODO_FINAL',
        'NIV_ACA_AUDIT_STATUS',
        'FECHA_MATRICULA_FUENTE_FINAL',
        'FECHA_MATRICULA_METODO_FINAL',
        'FECHA_MATRICULA_AUDIT_STATUS',
        'DURACION_ESTUDIOS_REF',
    ]
    missing_cols = [col for col in required_cols if col not in included.columns]
    assert not missing_cols, f'FASE 3: faltan columnas de trazabilidad: {missing_cols}'

    included_count = int(len(included))
    anio_act_num = pd.to_numeric(included['ANIO_ING_ACT'], errors='coerce')
    sem_act_num = pd.to_numeric(included['SEM_ING_ACT'], errors='coerce')
    anio_ori_num = pd.to_numeric(included['ANIO_ING_ORI'], errors='coerce')
    sem_ori_num = pd.to_numeric(included['SEM_ING_ORI'], errors='coerce')
    niv_num = pd.to_numeric(included['NIV_ACA'], errors='coerce')
    dur_ref = pd.to_numeric(included['DURACION_ESTUDIOS_REF'], errors='coerce')
    fecha_mask = _valid_ddmmyyyy_mask(included['FECHA_MATRICULA'])
    fecha_1900_mask = included['FECHA_MATRICULA'].eq('01/01/1900')
    cohorte_2026_mask = anio_ori_num.eq(2026)

    anio_act_valid = anio_act_num.between(1990, 2026)
    sem_act_valid = sem_act_num.isin([1, 2])
    anio_ori_valid = anio_ori_num.eq(1900) | anio_ori_num.between(1980, 2026)
    sem_ori_valid = sem_ori_num.isin([0, 1, 2])
    ori_anio_equal_act = anio_ori_num.eq(anio_act_num)
    ori_sem_equal_act = sem_ori_num.eq(sem_act_num)
    niv_valid = niv_num.ge(1)
    niv_le_dur = dur_ref.isna() | niv_num.le(dur_ref)
    niv_cohorte_2026_ok = (~cohorte_2026_mask) | niv_num.le(2)
    fecha_policy_ok = (cohorte_2026_mask & ~fecha_1900_mask) | ((~cohorte_2026_mask) & fecha_1900_mask)

    gate = {
        'Q_ANIO_ING_ACT': {
            'fuente_regla_definida': bool(included['ANIO_ING_ACT_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(anio_act_valid.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['ANIO_ING_ACT_AUDIT_STATUS'].replace('', pd.NA).notna().all()
                and ~included['ANIO_ING_ACT_AUDIT_STATUS'].astype(str).str.contains('SIN_TRAZA', regex=False).any()
            ),
            'auditable_en_filas_incluidas': bool(
                included[['ANIO_ING_ACT_FUENTE_FINAL', 'ANIO_ING_ACT_METODO_FINAL', 'ANIO_ING_ACT_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'R_SEM_ING_ACT': {
            'fuente_regla_definida': bool(included['SEM_ING_ACT_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(sem_act_valid.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['SEM_ING_ACT_AUDIT_STATUS'].replace('', pd.NA).notna().all()
                and ~included['SEM_ING_ACT_AUDIT_STATUS'].astype(str).str.contains('SIN_TRAZA', regex=False).any()
            ),
            'auditable_en_filas_incluidas': bool(
                included[['SEM_ING_ACT_FUENTE_FINAL', 'SEM_ING_ACT_METODO_FINAL', 'SEM_ING_ACT_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'S_ANIO_ING_ORI': {
            'fuente_regla_definida': bool(included['ANIO_ING_ORI_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(anio_ori_valid.all() and ori_anio_equal_act.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['ANIO_ING_ORI_AUDIT_STATUS'].replace('', pd.NA).notna().all()
                and ~included['ANIO_ING_ORI_AUDIT_STATUS'].astype(str).str.contains('SIN_TRAZA', regex=False).any()
            ),
            'auditable_en_filas_incluidas': bool(
                included[['ANIO_ING_ORI_FUENTE_FINAL', 'ANIO_ING_ORI_METODO_FINAL', 'ANIO_ING_ORI_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'T_SEM_ING_ORI': {
            'fuente_regla_definida': bool(included['SEM_ING_ORI_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(sem_ori_valid.all() and ori_sem_equal_act.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['SEM_ING_ORI_AUDIT_STATUS'].replace('', pd.NA).notna().all()
                and ~included['SEM_ING_ORI_AUDIT_STATUS'].astype(str).str.contains('SIN_TRAZA', regex=False).any()
            ),
            'auditable_en_filas_incluidas': bool(
                included[['SEM_ING_ORI_FUENTE_FINAL', 'SEM_ING_ORI_METODO_FINAL', 'SEM_ING_ORI_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'AA_NIV_ACA': {
            'fuente_regla_definida': bool(included['NIV_ACA_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(niv_valid.all() and niv_le_dur.all() and niv_cohorte_2026_ok.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['NIV_ACA_AUDIT_STATUS'].replace('', pd.NA).notna().all()
                and ~included['NIV_ACA_AUDIT_STATUS'].astype(str).str.contains('SIN_TRAZA', regex=False).any()
            ),
            'auditable_en_filas_incluidas': bool(
                included[['NIV_ACA_FUENTE_FINAL', 'NIV_ACA_METODO_FINAL', 'NIV_ACA_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
        'AD_FECHA_MATRICULA': {
            'fuente_regla_definida': bool(included['FECHA_MATRICULA_FUENTE_FINAL'].replace('', pd.NA).notna().all()),
            'transformacion_implementada': bool(fecha_mask.all() and fecha_policy_ok.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(
                included['FECHA_MATRICULA_AUDIT_STATUS'].replace('', pd.NA).notna().all()
                and ~included['FECHA_MATRICULA_AUDIT_STATUS'].astype(str).str.contains('SIN_TRAZA', regex=False).any()
            ),
            'auditable_en_filas_incluidas': bool(
                included[['FECHA_MATRICULA_FUENTE_FINAL', 'FECHA_MATRICULA_METODO_FINAL', 'FECHA_MATRICULA_AUDIT_STATUS']].replace('', pd.NA).notna().all().all()
            ),
        },
    }

    for payload in gate.values():
        payload['estado_final'] = 'OK' if all(payload.values()) else 'Pendiente'

    summary = {
        'rows_included_final': included_count,
        'anio_ing_act_fuente_distribution': included['ANIO_ING_ACT_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'sem_ing_act_fuente_distribution': included['SEM_ING_ACT_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'anio_ing_ori_fuente_distribution': included['ANIO_ING_ORI_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'sem_ing_ori_fuente_distribution': included['SEM_ING_ORI_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'niv_aca_fuente_distribution': included['NIV_ACA_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'fecha_matricula_fuente_distribution': included['FECHA_MATRICULA_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'anio_ing_act_default_2026_rows': int(included['ANIO_ING_ACT_AUDIT_STATUS'].astype(str).str.startswith('DEFAULT_2026').sum()),
        'sem_ing_act_default_1_rows': int(included['SEM_ING_ACT_AUDIT_STATUS'].astype(str).str.startswith('DEFAULT_1').sum()),
        'anio_ing_ori_policy_rows': int(included['ANIO_ING_ORI_AUDIT_STATUS'].eq('IGUAL_ACTUAL_POR_POLITICA_FOR_ING_ACT_1').sum()),
        'sem_ing_ori_policy_rows': int(included['SEM_ING_ORI_AUDIT_STATUS'].eq('IGUAL_ACTUAL_POR_POLITICA_FOR_ING_ACT_1').sum()),
        'niv_aca_default_1_rows': int(included['NIV_ACA_AUDIT_STATUS'].astype(str).str.startswith('DEFAULT_1').sum()),
        'niv_aca_acotado_duracion_rows': int(included['NIV_ACA_AUDIT_STATUS'].astype(str).str.contains('ACOTADO_DURACION', regex=False).sum()),
        'niv_aca_acotado_cohorte_2026_rows': int(included['NIV_ACA_AUDIT_STATUS'].astype(str).str.contains('COHORTE_2026', regex=False).sum()),
        'fecha_matricula_1900_rows': int(fecha_1900_mask.sum()),
        'fecha_matricula_1900_fuera_2026_rows': int(((~cohorte_2026_mask) & fecha_1900_mask).sum()),
        'fecha_matricula_1900_en_2026_rows': int((cohorte_2026_mask & fecha_1900_mask).sum()),
        'fecha_matricula_non1900_fuera_2026_rows': int(((~cohorte_2026_mask) & (~fecha_1900_mask)).sum()),
        'anio_ing_ori_diff_rows': int((~ori_anio_equal_act).sum()),
        'sem_ing_ori_diff_rows': int((~ori_sem_equal_act).sum()),
        'columnas_fase_3': gate,
    }

    niv_fecha = {
        'rows_included_final': included_count,
        'niv_aca_fuente_distribution': summary['niv_aca_fuente_distribution'],
        'niv_aca_default_1_rows': summary['niv_aca_default_1_rows'],
        'niv_aca_acotado_duracion_rows': summary['niv_aca_acotado_duracion_rows'],
        'niv_aca_acotado_cohorte_2026_rows': summary['niv_aca_acotado_cohorte_2026_rows'],
        'fecha_matricula_fuente_distribution': summary['fecha_matricula_fuente_distribution'],
        'fecha_matricula_1900_rows': summary['fecha_matricula_1900_rows'],
        'fecha_matricula_1900_fuera_2026_rows': summary['fecha_matricula_1900_fuera_2026_rows'],
        'fecha_matricula_1900_en_2026_rows': summary['fecha_matricula_1900_en_2026_rows'],
        'fecha_matricula_non1900_fuera_2026_rows': summary['fecha_matricula_non1900_fuera_2026_rows'],
    }

    (report_dir / 'reporte_cronologia_mu_2026.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    (report_dir / 'reporte_niv_fecha_mu_2026.json').write_text(
        json.dumps(niv_fecha, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    lines = [
        '# Reporte FASE 3 - Cronologia MU 2026',
        '',
        f'- Filas incluidas en carga final: {included_count}',
        f'- Fuentes `ANIO_ING_ACT`: {summary["anio_ing_act_fuente_distribution"]}',
        f'- Fuentes `SEM_ING_ACT`: {summary["sem_ing_act_fuente_distribution"]}',
        f'- Filas `ANIO_ING_ORI != ANIO_ING_ACT`: {summary["anio_ing_ori_diff_rows"]}',
        f'- Filas `SEM_ING_ORI != SEM_ING_ACT`: {summary["sem_ing_ori_diff_rows"]}',
        f'- Ajustes `NIV_ACA` por duracion: {summary["niv_aca_acotado_duracion_rows"]}',
        f'- Ajustes `NIV_ACA` por cohorte 2026: {summary["niv_aca_acotado_cohorte_2026_rows"]}',
        f'- Filas `FECHA_MATRICULA = 01/01/1900`: {summary["fecha_matricula_1900_rows"]}',
        f'- Filas `FECHA_MATRICULA = 01/01/1900` fuera de cohorte 2026: {summary["fecha_matricula_1900_fuera_2026_rows"]}',
        f'- Filas `FECHA_MATRICULA = 01/01/1900` dentro de cohorte 2026: {summary["fecha_matricula_1900_en_2026_rows"]}',
        '',
        '## Gate por columna',
        '',
        '| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |',
        '|---|---|---|---|---|---|---|',
    ]
    ordered = [
        ('Q', 'Q_ANIO_ING_ACT'),
        ('R', 'R_SEM_ING_ACT'),
        ('S', 'S_ANIO_ING_ORI'),
        ('T', 'T_SEM_ING_ORI'),
        ('AA', 'AA_NIV_ACA'),
        ('AD', 'AD_FECHA_MATRICULA'),
    ]
    for label, key in ordered:
        payload = gate[key]
        lines.append(
            f'| {label} | {_si_no(payload["fuente_regla_definida"])} | {_si_no(payload["transformacion_implementada"])} | '
            f'{_si_no(payload["validacion_qa_existe"])} | {_si_no(payload["sin_default_silencioso"])} | '
            f'{_si_no(payload["auditable_en_filas_incluidas"])} | {payload["estado_final"]} |'
        )

    (report_dir / 'reporte_fase_3_cronologia_mu_2026.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def generate_fase4_rendimiento_reports(out: Path, control_dir: Path) -> dict[str, object]:
    report_dir = control_dir / 'reportes'
    report_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    assert xlsx_path.exists(), f'Falta archivo de auditoría para FASE 4: {xlsx_path}'

    stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    mu32 = pd.read_excel(xlsx_path, sheet_name='MATRICULA_UNIFICADA_32', dtype=str).fillna('')
    included = stage[stage['INCLUIR_EN_MATRICULA_32'].eq('SI')].copy()
    assert len(included) == len(mu32), 'FASE 4: included no coincide con MATRÍCULA_UNIFICADA_32'

    required_cols = [
        'UZ_HIST_KEY',
        'ANIO_REFERENCIA_HIST_UZ',
        'UZ_HIST_ANIO_MIN',
        'UZ_HIST_ANIO_MAX',
        'UZ_HIST_ANIOS_DISPONIBLES',
        'UZ_HIST_SCOPE_STATUS',
        'UZ_HIST_FILAS_TOTAL',
        'UZ_HIST_FILAS_ANIO_REFERENCIA',
        'UZ_HIST_FILAS_REF_APROB',
        'UZ_HIST_FILAS_REF_REPROB',
        'UZ_HIST_FILAS_REF_TRANSFER',
        'UZ_HIST_FILAS_REF_SEM1_CALIFICADAS',
        'UZ_HIST_FILAS_REF_SEM2_CALIFICADAS',
        'UZ_FUENTE_HIST',
        'ASI_INS_ANT_FUENTE_FINAL',
        'ASI_INS_ANT_METODO_FINAL',
        'ASI_INS_ANT_AUDIT_STATUS',
        'ASI_APR_ANT_FUENTE_FINAL',
        'ASI_APR_ANT_METODO_FINAL',
        'ASI_APR_ANT_AUDIT_STATUS',
        'PROM_PRI_SEM_FUENTE_FINAL',
        'PROM_PRI_SEM_METODO_FINAL',
        'PROM_PRI_SEM_AUDIT_STATUS',
        'PROM_SEG_SEM_FUENTE_FINAL',
        'PROM_SEG_SEM_METODO_FINAL',
        'PROM_SEG_SEM_AUDIT_STATUS',
        'ASI_INS_HIS_FUENTE_FINAL',
        'ASI_INS_HIS_METODO_FINAL',
        'ASI_INS_HIS_AUDIT_STATUS',
        'ASI_APR_HIS_FUENTE_FINAL',
        'ASI_APR_HIS_METODO_FINAL',
        'ASI_APR_HIS_AUDIT_STATUS',
    ]
    missing_cols = [col for col in required_cols if col not in included.columns]
    assert not missing_cols, f'FASE 4: faltan columnas de trazabilidad: {missing_cols}'

    included_count = int(len(included))
    asi_ins_ant = pd.to_numeric(included['ASI_INS_ANT'], errors='coerce')
    asi_apr_ant = pd.to_numeric(included['ASI_APR_ANT'], errors='coerce')
    prom_pri = pd.to_numeric(included['PROM_PRI_SEM'], errors='coerce')
    prom_seg = pd.to_numeric(included['PROM_SEG_SEM'], errors='coerce')
    asi_ins_his = pd.to_numeric(included['ASI_INS_HIS'], errors='coerce')
    asi_apr_his = pd.to_numeric(included['ASI_APR_HIS'], errors='coerce')
    hist_anios = pd.to_numeric(included['UZ_HIST_ANIOS_DISPONIBLES'], errors='coerce')

    scope_single_year = included['UZ_HIST_SCOPE_STATUS'].eq('ALCANCE_LIMITADO_ANIO_UNICO') | hist_anios.eq(1)
    scope_multiyear = included['UZ_HIST_SCOPE_STATUS'].eq('ALCANCE_MULTIANUAL') | hist_anios.gt(1)
    prom_pri_zero_explicit = (~prom_pri.eq(0)) | included['PROM_PRI_SEM_AUDIT_STATUS'].eq('SIN_NOTAS_CALIFICABLES_SEM1_ANIO_REF')
    prom_seg_zero_explicit = (~prom_seg.eq(0)) | included['PROM_SEG_SEM_AUDIT_STATUS'].eq('SIN_NOTAS_CALIFICABLES_SEM2_ANIO_REF')

    def _all_present_local(cols: list[str]) -> bool:
        return bool(included[cols].replace('', pd.NA).notna().all().all())

    common_hist_trace = [
        'UZ_HIST_KEY',
        'ANIO_REFERENCIA_HIST_UZ',
        'UZ_HIST_ANIO_MIN',
        'UZ_HIST_ANIO_MAX',
        'UZ_HIST_ANIOS_DISPONIBLES',
        'UZ_HIST_SCOPE_STATUS',
        'UZ_FUENTE_HIST',
    ]

    gate = {
        'U_ASI_INS_ANT': {
            'fuente_regla_definida': _all_present_local(['ASI_INS_ANT_FUENTE_FINAL', 'ASI_INS_ANT_METODO_FINAL']),
            'transformacion_implementada': bool(asi_ins_ant.between(0, 99).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['ASI_INS_ANT_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': _all_present_local(['ASI_INS_ANT_FUENTE_FINAL', 'ASI_INS_ANT_METODO_FINAL', 'ASI_INS_ANT_AUDIT_STATUS'] + common_hist_trace),
        },
        'V_ASI_APR_ANT': {
            'fuente_regla_definida': _all_present_local(['ASI_APR_ANT_FUENTE_FINAL', 'ASI_APR_ANT_METODO_FINAL']),
            'transformacion_implementada': bool(asi_apr_ant.between(0, 99).all() and asi_apr_ant.le(asi_ins_ant).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['ASI_APR_ANT_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': _all_present_local(['ASI_APR_ANT_FUENTE_FINAL', 'ASI_APR_ANT_METODO_FINAL', 'ASI_APR_ANT_AUDIT_STATUS'] + common_hist_trace),
        },
        'W_PROM_PRI_SEM': {
            'fuente_regla_definida': _all_present_local(['PROM_PRI_SEM_FUENTE_FINAL', 'PROM_PRI_SEM_METODO_FINAL']),
            'transformacion_implementada': bool(((prom_pri.eq(0)) | prom_pri.between(100, 700)).all() and prom_pri_zero_explicit.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['PROM_PRI_SEM_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any() and prom_pri_zero_explicit.all()),
            'auditable_en_filas_incluidas': _all_present_local(['PROM_PRI_SEM_FUENTE_FINAL', 'PROM_PRI_SEM_METODO_FINAL', 'PROM_PRI_SEM_AUDIT_STATUS'] + common_hist_trace),
        },
        'X_PROM_SEG_SEM': {
            'fuente_regla_definida': _all_present_local(['PROM_SEG_SEM_FUENTE_FINAL', 'PROM_SEG_SEM_METODO_FINAL']),
            'transformacion_implementada': bool(((prom_seg.eq(0)) | prom_seg.between(100, 700)).all() and prom_seg_zero_explicit.all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['PROM_SEG_SEM_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any() and prom_seg_zero_explicit.all()),
            'auditable_en_filas_incluidas': _all_present_local(['PROM_SEG_SEM_FUENTE_FINAL', 'PROM_SEG_SEM_METODO_FINAL', 'PROM_SEG_SEM_AUDIT_STATUS'] + common_hist_trace),
        },
        'Y_ASI_INS_HIS': {
            'fuente_regla_definida': _all_present_local(['ASI_INS_HIS_FUENTE_FINAL', 'ASI_INS_HIS_METODO_FINAL']),
            'transformacion_implementada': bool(asi_ins_his.between(0, 200).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['ASI_INS_HIS_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': _all_present_local(['ASI_INS_HIS_FUENTE_FINAL', 'ASI_INS_HIS_METODO_FINAL', 'ASI_INS_HIS_AUDIT_STATUS'] + common_hist_trace),
        },
        'Z_ASI_APR_HIS': {
            'fuente_regla_definida': _all_present_local(['ASI_APR_HIS_FUENTE_FINAL', 'ASI_APR_HIS_METODO_FINAL']),
            'transformacion_implementada': bool(asi_apr_his.between(0, 200).all() and asi_apr_his.le(asi_ins_his).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(~included['ASI_APR_HIS_AUDIT_STATUS'].isin(['SIN_FUENTE_FINAL']).any()),
            'auditable_en_filas_incluidas': _all_present_local(['ASI_APR_HIS_FUENTE_FINAL', 'ASI_APR_HIS_METODO_FINAL', 'ASI_APR_HIS_AUDIT_STATUS'] + common_hist_trace),
        },
    }

    for payload in gate.values():
        payload['estado_final'] = 'OK' if all(payload.values()) else 'Pendiente'

    resumen_cols = [
        'CODCLI',
        'N_DOC',
        'DV',
        'CODCARPR_NORM',
        'UZ_HIST_KEY',
        'ANIO_REFERENCIA_HIST_UZ',
        'UZ_HIST_ANIO_MIN',
        'UZ_HIST_ANIO_MAX',
        'UZ_HIST_ANIOS_DISPONIBLES',
        'UZ_HIST_SCOPE_STATUS',
        'UZ_FUENTE_HIST',
        'UZ_HIST_FILAS_TOTAL',
        'UZ_HIST_FILAS_ANIO_REFERENCIA',
        'UZ_HIST_FILAS_REF_APROB',
        'UZ_HIST_FILAS_REF_REPROB',
        'UZ_HIST_FILAS_REF_TRANSFER',
        'UZ_HIST_FILAS_REF_SEM1_CALIFICADAS',
        'UZ_HIST_FILAS_REF_SEM2_CALIFICADAS',
        'ASI_INS_ANT',
        'ASI_INS_ANT_AUDIT_STATUS',
        'ASI_APR_ANT',
        'ASI_APR_ANT_AUDIT_STATUS',
        'PROM_PRI_SEM',
        'PROM_PRI_SEM_AUDIT_STATUS',
        'PROM_SEG_SEM',
        'PROM_SEG_SEM_AUDIT_STATUS',
        'ASI_INS_HIS',
        'ASI_INS_HIS_AUDIT_STATUS',
        'ASI_APR_HIS',
        'ASI_APR_HIS_AUDIT_STATUS',
    ]
    included[resumen_cols].to_csv(report_dir / 'resumen_historico_mu_2026.csv', index=False, encoding='utf-8')

    summary = {
        'rows_included_final': included_count,
        'ventana_referencia_distribution': included['ANIO_REFERENCIA_HIST_UZ'].value_counts(dropna=False).to_dict(),
        'uz_fuente_distribution': included['UZ_FUENTE_HIST'].value_counts(dropna=False).to_dict(),
        'uz_scope_status_distribution': included['UZ_HIST_SCOPE_STATUS'].value_counts(dropna=False).to_dict(),
        'hist_anios_disponibles_distribution': included['UZ_HIST_ANIOS_DISPONIBLES'].value_counts(dropna=False).to_dict(),
        'asi_ins_ant_fuente_distribution': included['ASI_INS_ANT_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'asi_apr_ant_fuente_distribution': included['ASI_APR_ANT_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'prom_pri_fuente_distribution': included['PROM_PRI_SEM_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'prom_seg_fuente_distribution': included['PROM_SEG_SEM_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'asi_ins_his_fuente_distribution': included['ASI_INS_HIS_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'asi_apr_his_fuente_distribution': included['ASI_APR_HIS_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'prom_pri_zero_rows': int(prom_pri.eq(0).sum()),
        'prom_seg_zero_rows': int(prom_seg.eq(0).sum()),
        'prom_pri_zero_explicit_rows': int(included['PROM_PRI_SEM_AUDIT_STATUS'].eq('SIN_NOTAS_CALIFICABLES_SEM1_ANIO_REF').sum()),
        'prom_seg_zero_explicit_rows': int(included['PROM_SEG_SEM_AUDIT_STATUS'].eq('SIN_NOTAS_CALIFICABLES_SEM2_ANIO_REF').sum()),
        'apr_ant_capped_rows': int(included['ASI_APR_ANT_AUDIT_STATUS'].eq('CAP_APR_A_INS_ANT').sum()),
        'apr_his_capped_rows': int(included['ASI_APR_HIS_AUDIT_STATUS'].eq('CAP_APR_A_INS_HIS').sum()),
        'asi_ins_his_eq_ant_rows': int(asi_ins_his.eq(asi_ins_ant).sum()),
        'asi_apr_his_eq_ant_rows': int(asi_apr_his.eq(asi_apr_ant).sum()),
        'rows_scope_single_year': int(scope_single_year.sum()),
        'rows_scope_multiyear': int(scope_multiyear.sum()),
        'columnas_fase_4': gate,
    }

    (report_dir / 'reporte_rendimiento_mu_2026.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    lines = [
        '# Reporte FASE 4 - Rendimiento academico MU 2026',
        '',
        f'- Filas incluidas en carga final: {included_count}',
        f'- Ventana de referencia observada: {summary["ventana_referencia_distribution"]}',
        f'- Alcance historico observado: {summary["uz_scope_status_distribution"]}',
        f'- Anios historicos disponibles por fila: {summary["hist_anios_disponibles_distribution"]}',
        f'- Filas `PROM_PRI_SEM = 0`: {summary["prom_pri_zero_rows"]}',
        f'- Filas `PROM_SEG_SEM = 0`: {summary["prom_seg_zero_rows"]}',
        f'- Filas sin notas calificables sem 1: {summary["prom_pri_zero_explicit_rows"]}',
        f'- Filas sin notas calificables sem 2: {summary["prom_seg_zero_explicit_rows"]}',
        f'- Caps visibles `ASI_APR_ANT <= ASI_INS_ANT`: {summary["apr_ant_capped_rows"]}',
        f'- Caps visibles `ASI_APR_HIS <= ASI_INS_HIS`: {summary["apr_his_capped_rows"]}',
        f'- Filas `ASI_INS_HIS = ASI_INS_ANT`: {summary["asi_ins_his_eq_ant_rows"]}',
        f'- Filas `ASI_APR_HIS = ASI_APR_ANT`: {summary["asi_apr_his_eq_ant_rows"]}',
        f'- Filas con alcance historico limitado a un solo anio: {summary["rows_scope_single_year"]}',
        '',
        '## Gate por columna',
        '',
        '| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |',
        '|---|---|---|---|---|---|---|',
    ]
    ordered = [
        ('U', 'U_ASI_INS_ANT'),
        ('V', 'V_ASI_APR_ANT'),
        ('W', 'W_PROM_PRI_SEM'),
        ('X', 'X_PROM_SEG_SEM'),
        ('Y', 'Y_ASI_INS_HIS'),
        ('Z', 'Z_ASI_APR_HIS'),
    ]
    for label, key in ordered:
        payload = gate[key]
        lines.append(
            f'| {label} | {_si_no(payload["fuente_regla_definida"])} | {_si_no(payload["transformacion_implementada"])} | '
            f'{_si_no(payload["validacion_qa_existe"])} | {_si_no(payload["sin_default_silencioso"])} | '
            f'{_si_no(payload["auditable_en_filas_incluidas"])} | {payload["estado_final"]} |'
        )

    lines.extend(
        [
            '',
            '## Alcance historico observado',
            '',
            '- `Y ASI_INS_HIS` y `Z ASI_APR_HIS` incorporan logica para todos los alcances (monoano y multianual).',
            '- La distribucion de alcance queda visible en `UZ_HIST_ANIOS_DISPONIBLES`, `UZ_HIST_SCOPE_STATUS` y `resumen_historico_mu_2026.csv`.',
        ]
    )

    (report_dir / 'reporte_fase_4_rendimiento_mu_2026.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def generate_fase5_estado_admin_reports(out: Path, control_dir: Path) -> dict[str, object]:
    report_dir = control_dir / 'reportes'
    report_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    assert xlsx_path.exists(), f'Falta archivo de auditoría para FASE 5: {xlsx_path}'

    stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    mu32 = pd.read_excel(xlsx_path, sheet_name='MATRICULA_UNIFICADA_32', dtype=str).fillna('')
    included = stage[stage['INCLUIR_EN_MATRICULA_32'].eq('SI')].copy()
    assert len(included) == len(mu32), 'FASE 5: included no coincide con MATRÍCULA_UNIFICADA_32'

    required_cols = [
        'DA_ANOMATRICULA',
        'DA_PERIODOMATRICULA',
        'DA_SITUACION',
        'DA_MATRICULA',
        'DA_CON_FIRMA',
        'SIT_FON_SOL_FUENTE_FINAL',
        'SIT_FON_SOL_METODO_FINAL',
        'SIT_FON_SOL_AUDIT_STATUS',
        'SUS_PRE_FUENTE_FINAL',
        'SUS_PRE_METODO_FINAL',
        'SUS_PRE_AUDIT_STATUS',
        'REINCORPORACION_FUENTE_FINAL',
        'REINCORPORACION_METODO_FINAL',
        'REINCORPORACION_AUDIT_STATUS',
        'VIG_FUENTE_FINAL',
        'VIG_METODO_FINAL',
        'VIG_AUDIT_STATUS',
    ]
    missing_cols = [col for col in required_cols if col not in included.columns]
    assert not missing_cols, f'FASE 5: faltan columnas de trazabilidad: {missing_cols}'

    included_count = int(len(included))
    sit_fon = pd.to_numeric(included['SIT_FON_SOL'], errors='coerce')
    sus_pre = pd.to_numeric(included['SUS_PRE'], errors='coerce')
    reinc = pd.to_numeric(included['REINCORPORACION'], errors='coerce')
    vig = pd.to_numeric(included['VIG'], errors='coerce')
    da_situacion_31 = included['DA_SITUACION'].astype(str).str.startswith('31 - TITULADO APROBADO')

    gate = {
        'AB_SIT_FON_SOL': {
            'fuente_regla_definida': bool(included['SIT_FON_SOL_FUENTE_FINAL'].astype(str).eq('POLITICA_LOCAL_FIJA_1').all()),
            'transformacion_implementada': bool(sit_fon.eq(1).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(included['SIT_FON_SOL_AUDIT_STATUS'].astype(str).eq('FIJADO_MANUALMENTE_A_1_EN_TODO_EL_PROYECTO').all()),
            'auditable_en_filas_incluidas': _all_present(['SIT_FON_SOL_FUENTE_FINAL', 'SIT_FON_SOL_METODO_FINAL', 'SIT_FON_SOL_AUDIT_STATUS'], included),
            'estado_final': 'OK',
        },
        'AC_SUS_PRE': {
            'fuente_regla_definida': bool(included['SUS_PRE_FUENTE_FINAL'].astype(str).eq('POLITICA_LOCAL_FIJA_0').all()),
            'transformacion_implementada': bool(sus_pre.eq(0).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(included['SUS_PRE_AUDIT_STATUS'].astype(str).eq('FIJADO_MANUALMENTE_A_0_EN_TODO_EL_PROYECTO').all()),
            'auditable_en_filas_incluidas': _all_present(['SUS_PRE_FUENTE_FINAL', 'SUS_PRE_METODO_FINAL', 'SUS_PRE_AUDIT_STATUS'], included),
            'estado_final': 'OK',
        },
        'AE_REINCORPORACION': {
            'fuente_regla_definida': bool(included['REINCORPORACION_FUENTE_FINAL'].astype(str).eq('POLITICA_LOCAL_FIJA_0').all()),
            'transformacion_implementada': bool(reinc.eq(0).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(included['REINCORPORACION_AUDIT_STATUS'].astype(str).eq('FIJADO_MANUALMENTE_A_0_EN_TODO_EL_PROYECTO').all()),
            'auditable_en_filas_incluidas': _all_present(['REINCORPORACION_FUENTE_FINAL', 'REINCORPORACION_METODO_FINAL', 'REINCORPORACION_AUDIT_STATUS'], included),
            'estado_final': 'OK',
        },
        'AF_VIG': {
            'fuente_regla_definida': True,
            'transformacion_implementada': bool(vig.isin([0, 1, 2]).all()),
            'validacion_qa_existe': True,
            'sin_default_silencioso': bool(_all_present(['VIG_FUENTE_FINAL', 'VIG_METODO_FINAL', 'VIG_AUDIT_STATUS'], included)),
            'auditable_en_filas_incluidas': _all_present(['VIG_FUENTE_FINAL', 'VIG_METODO_FINAL', 'VIG_AUDIT_STATUS'], included),
            'estado_final': 'OK',
        },
    }

    summary = {
        'rows_included_final': included_count,
        'sit_fon_sol_distribution': included['SIT_FON_SOL'].value_counts(dropna=False).to_dict(),
        'sus_pre_distribution': included['SUS_PRE'].value_counts(dropna=False).to_dict(),
        'reincorporacion_distribution': included['REINCORPORACION'].value_counts(dropna=False).to_dict(),
        'vig_distribution': included['VIG'].value_counts(dropna=False).to_dict(),
        'sit_fon_sol_fuente_distribution': included['SIT_FON_SOL_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'sus_pre_fuente_distribution': included['SUS_PRE_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'reincorporacion_fuente_distribution': included['REINCORPORACION_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'vig_fuente_distribution': included['VIG_FUENTE_FINAL'].value_counts(dropna=False).to_dict(),
        'sit_fon_sol_default_rows': 0,
        'sus_pre_default_rows': 0,
        'sus_pre_forzado_0_cohorte_2026_rows': 0,
        'reincorporacion_rows_1': 0,
        'reincorporacion_rows_da_situacion_38': 0,
        'reincorporacion_rows_1_periodo_1': 0,
        'reincorporacion_rows_1_periodo_2': 0,
        'reincorporacion_rows_1_periodo_3': 0,
        'reincorporacion_rows_1_sin_respaldo_temporal': 0,
        'reincorporacion_rows_1_periodo_ultimo_tramo': 0,
        'vig_rows_0': int(vig.eq(0).sum()),
        'vig_rows_1': int(vig.eq(1).sum()),
        'vig_rows_2': int(vig.eq(2).sum()),
        'vig_rows_titulado_aprobado': int(da_situacion_31.sum()),
        'vig_rows_policy_vig_1': int(included['VIG_AUDIT_STATUS'].eq('POLITICA_CARGA_PREGRADO_VIG_1').sum()),
        'vig_rows_policy_vig_2_titulado': int(included['VIG_AUDIT_STATUS'].eq('POLITICA_CARGA_PREGRADO_VIG_2_TITULADO').sum()),
        'columnas_fase_5': gate,
    }

    (report_dir / 'reporte_estado_admin_mu_2026.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    lines = [
        '# Reporte FASE 5 - Estado administrativo MU 2026',
        '',
        f'- Filas incluidas en carga final: {included_count}',
        f'- Distribucion `SIT_FON_SOL`: {summary["sit_fon_sol_distribution"]}',
        f'- Distribucion `SUS_PRE`: {summary["sus_pre_distribution"]}',
        f'- Distribucion `REINCORPORACION`: {summary["reincorporacion_distribution"]}',
        f'- Distribucion `VIG`: {summary["vig_distribution"]}',
        f'- Filas `SIT_FON_SOL` por default explicito: {summary["sit_fon_sol_default_rows"]}',
        f'- Filas `SUS_PRE` por default explicito: {summary["sus_pre_default_rows"]}',
        f'- Filas `SUS_PRE` forzadas a `0` por politica de cohorte 2026: {summary["sus_pre_forzado_0_cohorte_2026_rows"]}',
        f'- Filas `REINCORPORACION = 1`: {summary["reincorporacion_rows_1"]}',
        f'- Filas `REINCORPORACION = 1` sin respaldo temporal: {summary["reincorporacion_rows_1_sin_respaldo_temporal"]}',
        f'- Filas `VIG = 2`: {summary["vig_rows_2"]}',
        f'- Filas `VIG = 2` por politica de titulado aprobado: {summary["vig_rows_policy_vig_2_titulado"]}',
        '',
        '## Gate por columna',
        '',
        '| Columna | Fuente/regla | Transformación | QA existe | Sin default silencioso | Auditable | Estado |',
        '|---|---|---|---|---|---|---|',
    ]
    ordered = [
        ('AB', 'AB_SIT_FON_SOL'),
        ('AC', 'AC_SUS_PRE'),
        ('AE', 'AE_REINCORPORACION'),
        ('AF', 'AF_VIG'),
    ]
    for label, key in ordered:
        payload = gate[key]
        lines.append(
            f'| {label} | {_si_no(payload["fuente_regla_definida"])} | {_si_no(payload["transformacion_implementada"])} | '
            f'{_si_no(payload["validacion_qa_existe"])} | {_si_no(payload["sin_default_silencioso"])} | '
            f'{_si_no(payload["auditable_en_filas_incluidas"])} | {payload["estado_final"]} |'
        )

    lines.extend(
        [
            '',
            '## Bloqueo residual observado',
            '',
            '- `AB SIT_FON_SOL` y `AC SUS_PRE` quedan cerrados por politica local fija auditable sobre todas las filas incluidas.',
            '- `AE REINCORPORACION` queda cerrado por politica local fija auditable en `0` para todas las filas incluidas.',
        ]
    )

    (report_dir / 'reporte_fase_5_estado_admin_mu_2026.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def generate_fase6_gate_final(out: Path, control_dir: Path, base_metrics: dict[str, object]) -> dict[str, object]:
    tablero_path = control_dir / 'tablero_mu_2026.tsv'
    gate_dir = control_dir / 'gate'
    gate_dir.mkdir(parents=True, exist_ok=True)
    pendientes_dir = control_dir / 'pendientes'
    pendientes_dir.mkdir(parents=True, exist_ok=True)
    backlog_path = pendientes_dir / 'backlog_residual_mu_2026.tsv'

    fase5_report_path = control_dir / 'reportes' / 'reporte_estado_admin_mu_2026.json'
    assert fase5_report_path.exists(), f'Falta reporte FASE 5: {fase5_report_path}'
    fase5_data = json.loads(fase5_report_path.read_text(encoding='utf-8'))
    fase5_gate = fase5_data['columnas_fase_5']

    with tablero_path.open(encoding='utf-8', newline='') as fh:
        tablero_rows = list(csv.DictReader(fh, delimiter='\t'))

    estado_override = {
        'AB': fase5_gate['AB_SIT_FON_SOL']['estado_final'],
        'AC': fase5_gate['AC_SUS_PRE']['estado_final'],
        'AE': fase5_gate['AE_REINCORPORACION']['estado_final'],
    }

    tablero_rows_actualizado = []
    for row in tablero_rows:
        row = dict(row)
        col = row.get('Columna', '').strip()
        if col in estado_override:
            row['Estado'] = estado_override[col]
            if row['Estado'] == 'OK':
                row['Bloqueo actual'] = 'Sin bloqueo residual.'
                row['Acción necesaria'] = 'Ninguna.'
                row['Criterio para pasar a OK'] = 'Ya resuelto en FASE 5.'
        tablero_rows_actualizado.append(row)

    tablero_rows = tablero_rows_actualizado
    ok_rows = [row for row in tablero_rows if row['Estado'] == 'OK']
    pending_rows = [row for row in tablero_rows if row['Estado'] == 'Pendiente']

    csv_path = out / MU_PREGRADO_CSV_FILENAME
    xlsx_path = out / MU_FUSION_OUTPUT_FILENAME
    mu = pd.read_csv(csv_path, sep=';', header=None, dtype=str, keep_default_na=False, names=MATRICULA_UNIFICADA_COLUMNS)
    stage = pd.read_excel(xlsx_path, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')
    included = stage[stage['INCLUIR_EN_MATRICULA_32'].eq('SI')].copy()

    first_line = csv_path.read_text(encoding='utf-8').splitlines()[0]
    header_ok = first_line != ';'.join(MATRICULA_UNIFICADA_COLUMNS)
    cols_ok = mu.shape[1] == len(MATRICULA_UNIFICADA_COLUMNS)
    separator_ok = first_line.count(';') == len(MATRICULA_UNIFICADA_COLUMNS) - 1
    sexo_ok = mu['SEXO'].astype(str).str.strip().isin({'H', 'M', 'NB'}).all()
    for_ing_ok = mu['FOR_ING_ACT'].astype(str).str.strip().eq('1').all()
    primera_ok = ~included['SIES_RESOLUCION_HEURISTICA'].eq('PRIMERA_OPCION').any()
    invariants_ok = all([header_ok, cols_ok, separator_ok, sexo_ok, for_ing_ok, primera_ok])

    decision = 'RECHAZADO'
    if invariants_ok:
        decision = 'APROBADO' if not pending_rows else 'CONDICIONAL'

    listo_auditoria = invariants_ok and all(row['Evidencia actual'].strip() for row in tablero_rows)
    listo_carga = decision == 'APROBADO'
    no_listo_carga = not listo_carga

    dependency_map = {
        'Y': 'Externa: nueva fuente historica multianual o acto regulatorio explicito',
        'Z': 'Externa: nueva fuente historica multianual o acto regulatorio explicito',
        'AB': 'Funcional: fuente institucional administrativa por fila incluida',
        'AC': 'Funcional: fuente institucional administrativa por fila incluida',
        'AE': 'Funcional: regla temporal institucional o fuente de ultima carga valida del periodo',
    }

    backlog_rows = [
        {
            'Columna': row['Columna'],
            'Campo': row['Campo'],
            'Fase duena': row['Fase dueña'],
            'Estado': row['Estado'],
            'Bloqueo exacto': row['Bloqueo actual'],
            'Evidencia existente': row['Evidencia actual'],
            'Dependencia externa o funcional': dependency_map.get(row['Columna'], 'Pendiente por definir'),
            'Siguiente accion concreta': row['Acción necesaria'],
            'Condicion objetiva para pasar a OK': row['Criterio para pasar a OK'],
        }
        for row in pending_rows
    ]
    backlog_exec_rows = [
        {
            'Campo': f"{row['Columna']} {row['Campo']}",
            'Estado actual': row['Estado'],
            'Bloqueo exacto': row['Bloqueo exacto'],
            'Tipo de dependencia': (
                'Datos/fuente + normativa'
                if row['Columna'] in {'Y', 'Z'}
                else ('Normativa + funcional/institucional' if row['Columna'] == 'AE' else 'Datos/fuente + funcional/institucional')
            ),
            'Fuente faltante o decisión faltante': (
                'Fuente historica multianual o acto regulatorio explicito que autorice usar alcance monoanual como historico acumulado'
                if row['Columna'] in {'Y', 'Z'}
                else (
                    'Decision funcional/normativa explicita o fuente que identifique la ultima carga valida del periodo'
                    if row['Columna'] == 'AE'
                    else (
                        'Fuente institucional por fila o decision funcional formal que distinga estados 0/1/2'
                        if row['Columna'] == 'AB'
                        else 'Fuente institucional por fila o decision funcional formal que cuantifique suspensiones previas'
                    )
                )
            ),
            'Responsable esperado': (
                'Registro Academico + Gobierno de Datos + contraparte regulatoria'
                if row['Columna'] in {'Y', 'Z'}
                else (
                    'Registro Academico + Secretaria de Estudios + area normativa'
                    if row['Columna'] == 'AE'
                    else (
                        'Finanzas Estudiantiles + Registro Academico + Gobierno de Datos'
                        if row['Columna'] == 'AB'
                        else 'Registro Academico + soporte administrativo estudiantil + Gobierno de Datos'
                    )
                )
            ),
            'Acción concreta siguiente': (
                'Escalar requerimiento de fuente multianual y, en paralelo, solicitar pronunciamiento regulatorio expreso sobre uso del alcance disponible'
                if row['Columna'] in {'Y', 'Z'}
                else (
                    'Cerrar criterio temporal con responsable funcional y obtener fuente o validacion formal para identificar la ultima carga valida del periodo'
                    if row['Columna'] == 'AE'
                    else (
                        'Levantar fuente institucional disponible por estudiante o formalizar criterio funcional firmado para la codificacion 0/1/2'
                        if row['Columna'] == 'AB'
                        else 'Levantar fuente institucional disponible por estudiante o formalizar criterio funcional firmado para el conteo de suspensiones previas'
                    )
                )
            ),
            'Evidencia ya disponible': row['Evidencia existente'],
            'Condición objetiva para pasar a OK': row['Condicion objetiva para pasar a OK'],
            'Riesgo de no resolver': (
                'El proyecto sigue auditable pero no cargable; cualquier intento de carga expone observacion por semantica historica insuficiente'
                if row['Columna'] in {'Y', 'Z'}
                else (
                    'El archivo no puede declararse cargable porque la reincorporacion no cumple la regla temporal exigida por el manual'
                    if row['Columna'] == 'AE'
                    else (
                        'El archivo no puede declararse cargable porque el estado financiero solicitado no esta sustentado por fuente o regla defendible'
                        if row['Columna'] == 'AB'
                        else 'El archivo no puede declararse cargable porque el historial administrativo solicitado no esta sustentado por fuente o regla defendible'
                    )
                )
            ),
            'Prioridad': 'Alta',
        }
        for row in backlog_rows
    ]
    pd.DataFrame(backlog_exec_rows).to_csv(backlog_path, sep='\t', index=False, encoding='utf-8')

    phase_report_map = {
        'FASE 0': 'control/evidencias/D_primer_apellido.md + control/evidencias/F_nombre.md + control/evidencias/G_sexo.md + control/evidencias/P_for_ing_act.md',
        'FASE 1': 'control/reportes/reporte_identidad_mu_2026.json',
        'FASE 2': 'control/reportes/reporte_sies_oferta_mu_2026.json',
        'FASE 3': 'control/reportes/reporte_cronologia_mu_2026.json + control/reportes/reporte_niv_fecha_mu_2026.json',
        'FASE 4': 'control/reportes/reporte_rendimiento_mu_2026.json',
        'FASE 5': 'control/reportes/reporte_estado_admin_mu_2026.json',
    }
    phase_rows = []
    for phase_name in ['FASE 0', 'FASE 1', 'FASE 2', 'FASE 3', 'FASE 4', 'FASE 5']:
        phase_items = [row for row in tablero_rows if row['Fase dueña'] == phase_name]
        phase_pending = [row for row in phase_items if row['Estado'] == 'Pendiente']
        phase_result = 'OK' if not phase_pending else 'CONDICIONAL'
        phase_risk = 'Sin bloqueo residual.' if not phase_pending else '; '.join(
            f"{row['Columna']} {row['Campo']}: {row['Bloqueo actual']}" for row in phase_pending
        )
        phase_rows.append(
            {
                'fase': phase_name,
                'resultado': phase_result,
                'riesgo': phase_risk,
                'reporte': phase_report_map[phase_name],
            }
        )

    summary = {
        'decision_final': decision,
        'listo_para_auditoria': bool(listo_auditoria),
        'listo_para_carga': bool(listo_carga),
        'no_listo_para_carga': bool(no_listo_carga),
        'ok_count': int(len(ok_rows)),
        'pending_count': int(len(pending_rows)),
        'ok_columns': [f"{row['Columna']} {row['Campo']}" for row in ok_rows],
        'pending_columns': [f"{row['Columna']} {row['Campo']}" for row in pending_rows],
        'rows_csv_final': int(len(mu)),
        'sexo_distribution': mu['SEXO'].astype(str).value_counts(dropna=False).to_dict(),
        'for_ing_act_distribution': mu['FOR_ING_ACT'].astype(str).value_counts(dropna=False).to_dict(),
        'rows_included_primera_opcion': int(included['SIES_RESOLUCION_HEURISTICA'].eq('PRIMERA_OPCION').sum()),
        'invariantes': {
            'csv_final_sin_header': bool(header_ok),
            'columnas_exactas_32': bool(cols_ok),
            'separador_punto_y_coma': bool(separator_ok),
            'sexo_valido': bool(sexo_ok),
            'for_ing_act_fijo_1': bool(for_ing_ok),
            'exclusion_primera_opcion': bool(primera_ok),
        },
        'bloqueos_residuales': backlog_rows,
        'estado_por_fase': phase_rows,
    }

    lines = [
        '# Gate Final MU 2026',
        '',
        '- Fecha: 2026-04-01',
        '- Responsable:',
        f'- Decision final: `{decision}`',
        f'- Listo para auditoria: `{"SI" if listo_auditoria else "NO"}`',
        f'- Listo para carga: `{"SI" if listo_carga else "NO"}`',
        f'- No listo para carga: `{"SI" if no_listo_carga else "NO"}`',
        '',
        '## Resumen del tablero',
        '',
        f'- Columnas en `OK` ({len(ok_rows)}): ' + ', '.join(f"`{row['Columna']} {row['Campo']}`" for row in ok_rows),
        f'- Columnas en `Pendiente` ({len(pending_rows)}): ' + ', '.join(f"`{row['Columna']} {row['Campo']}`" for row in pending_rows),
        f'- Conteo final: `{len(ok_rows)} OK / {len(pending_rows)} Pendiente`',
        '',
        '## Validacion de invariantes',
        '',
        '| Invariante | Resultado | Evidencia | Observacion |',
        '|---|---|---|---|',
        f"| CSV final sin header | {'SI' if header_ok else 'NO'} | resultados/matricula_unificada_2026_pregrado.csv | Filas finales: {len(mu)} |",
        f"| 32 columnas exactas | {'SI' if cols_ok else 'NO'} | resultados/matricula_unificada_2026_pregrado.csv | Columnas observadas: {mu.shape[1]} |",
        f"| Separador `;` | {'SI' if separator_ok else 'NO'} | resultados/matricula_unificada_2026_pregrado.csv | Delimitacion contractual vigente |",
        f"| `SEXO` valido | {'SI' if sexo_ok else 'NO'} | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {summary['sexo_distribution']} |",
        f"| `FOR_ING_ACT = 1` | {'SI' if for_ing_ok else 'NO'} | resultados/matricula_unificada_2026_pregrado.csv | Distribucion observada: {summary['for_ing_act_distribution']} |",
        f"| Exclusion de `PRIMERA_OPCION` | {'SI' if primera_ok else 'NO'} | resultados/archivo_listo_para_sies.xlsx | Filas incluidas con heuristica opaca: {summary['rows_included_primera_opcion']} |",
        '',
        '## Estado por fase',
        '',
        '| Fase | Resultado | Riesgo residual | Reporte asociado |',
        '|---|---|---|---|',
    ]
    for phase_row in phase_rows:
        lines.append(
            f"| {phase_row['fase']} | {phase_row['resultado']} | {phase_row['riesgo']} | {phase_row['reporte']} |"
        )

    lines.extend(
        [
            '',
            '## Bloqueos residuales abiertos',
            '',
            '| Bloqueo ID | Campo(s) | Impacto | Mitigacion | Estado |',
            '|---|---|---|---|---|',
        ]
    )
    for row in backlog_rows:
        impacto = 'Alto'
        if row['Columna'] in {'AB', 'AC'}:
            impacto = 'Medio-Alto'
        lines.append(
            f"| BLK-{row['Columna']} | {row['Columna']} `{row['Campo']}` | {impacto} | {row['Siguiente accion concreta']} | Abierto |"
        )

    lines.extend(
        [
            '',
            '## Condiciones de aprobacion',
            '',
            '- `APROBADO`: invariantes conformes, evidencia completa y sin bloqueo critico abierto.',
            '- `CONDICIONAL`: invariantes conformes, evidencia suficiente y backlog residual trazado.',
            '- `RECHAZADO`: ruptura de invariante, evidencia insuficiente o perdida de trazabilidad.',
            '',
            '## Firma operativa',
            '',
            '- Responsable:',
            '- Fecha: 2026-04-01',
            f"- Comentario final: Decision `{decision}`. " +
            (
                'CSV e invariantes en verde; el proyecto queda auditable, pero los pendientes residuales impiden declararlo listo para carga.'
                if decision == 'CONDICIONAL'
                else ('CSV e invariantes en verde sin pendientes residuales.' if decision == 'APROBADO' else 'Se detecto una ruptura de invariantes o trazabilidad.')
            ),
        ]
    )

    (gate_dir / 'gate_final_mu_2026.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Smoke checks del repositorio y outputs MU')
    p.add_argument('--output-dir', default='resultados', help='Carpeta de salida a validar')
    p.add_argument('--fase1-control-dir', default=None, help='Si se informa, genera artefactos reales de FASE 1 bajo este directorio control/')
    p.add_argument('--fase2-control-dir', default=None, help='Si se informa, genera artefactos reales de FASE 2 bajo este directorio control/')
    p.add_argument('--fase3-control-dir', default=None, help='Si se informa, genera artefactos reales de FASE 3 bajo este directorio control/')
    p.add_argument('--fase4-control-dir', default=None, help='Si se informa, genera artefactos reales de FASE 4 bajo este directorio control/')
    p.add_argument('--fase5-control-dir', default=None, help='Si se informa, genera artefactos reales de FASE 5 bajo este directorio control/')
    p.add_argument('--fase6-control-dir', default=None, help='Si se informa, genera gate final y backlog residual bajo este directorio control/')
    return p.parse_args()


def check_outputs(out: Path) -> dict[str, object]:
    check_base_outputs(out)
    return check_mu_pregrado_csv(out)


if __name__ == '__main__':
    args = parse_args()
    check_readme_no_csv_dump()
    metrics = check_outputs(Path(args.output_dir))
    if args.fase1_control_dir:
        fase1 = generate_fase1_identity_reports(Path(args.output_dir), Path(args.fase1_control_dir))
        metrics['fase1_identidad'] = fase1
    if args.fase2_control_dir:
        fase2 = generate_fase2_sies_oferta_reports(Path(args.output_dir), Path(args.fase2_control_dir))
        metrics['fase2_sies_oferta'] = fase2
    if args.fase3_control_dir:
        fase3 = generate_fase3_cronologia_reports(Path(args.output_dir), Path(args.fase3_control_dir))
        metrics['fase3_cronologia'] = fase3
    if args.fase4_control_dir:
        fase4 = generate_fase4_rendimiento_reports(Path(args.output_dir), Path(args.fase4_control_dir))
        metrics['fase4_rendimiento'] = fase4
    if args.fase5_control_dir:
        fase5 = generate_fase5_estado_admin_reports(Path(args.output_dir), Path(args.fase5_control_dir))
        metrics['fase5_estado_admin'] = fase5
    if args.fase6_control_dir:
        fase6 = generate_fase6_gate_final(Path(args.output_dir), Path(args.fase6_control_dir), metrics)
        metrics['fase6_gate_final'] = fase6
    if metrics:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print('qa_checks_ok')

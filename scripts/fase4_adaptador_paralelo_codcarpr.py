from __future__ import annotations

from pathlib import Path
import re
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DUR_PATH = BASE / 'DURACION_ESTUDIOS.tsv'
OUT_XLSX_PATH = BASE / 'resultados' / 'archivo_listo_para_sies.xlsx'

DETALLE_PATH = BASE / 'control' / 'reportes' / 'fase4_adaptador_detalle.tsv'
REPORTE_PATH = BASE / 'control' / 'reportes' / 'reporte_fase4_adaptador_paralelo.tsv'
PEND_PATH = BASE / 'control' / 'pendientes' / 'fase4_adaptador_pendientes.tsv'


def ensure_dirs() -> None:
    DETALLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PEND_PATH.parent.mkdir(parents=True, exist_ok=True)


def parse_jornada_from_codigo(codigo_unico: str) -> str:
    m = re.search(r'J(\d+)V\d+$', str(codigo_unico))
    return m.group(1) if m else ''


def explode_alias(canon: str, alias: str) -> list[str]:
    cods = set()
    c = str(canon).strip()
    if c:
        cods.add(c)
    a = str(alias).strip()
    if a:
        for x in a.split('|'):
            x = x.strip()
            if x:
                cods.add(x)
    return sorted(cods)


def build_duracion_lookup(dur: pd.DataFrame) -> dict[tuple[str, str], list[str]]:
    """(CODCARPR, JOR_NUM) -> [CODIGO_UNICO candidatos con estado UNICO]."""
    lookup: dict[tuple[str, str], list[str]] = {}
    df = dur[dur['CODCARPR_RESOLUCION_ESTADO'].eq('UNICO')].copy()

    for row in df.itertuples(index=False):
        cod_unico = row.CODIGO_UNICO
        jor_num = parse_jornada_from_codigo(cod_unico)
        codcarprs = explode_alias(row.CODCARPR_CANONICO, row.CODCARPR_ALIAS_LIST)
        for cp in codcarprs:
            key = (cp, jor_num)
            lookup.setdefault(key, [])
            if cod_unico not in lookup[key]:
                lookup[key].append(cod_unico)

    return lookup


def main() -> None:
    ensure_dirs()

    dur = pd.read_csv(DUR_PATH, sep='\t', dtype=str).fillna('')
    stage = pd.read_excel(OUT_XLSX_PATH, sheet_name='ARCHIVO_LISTO_SUBIDA', dtype=str).fillna('')

    needed = ['CODCLI', 'CODCARPR_NORM', 'JOR', 'CODIGO_CARRERA_SIES_FINAL', 'INCLUIR_EN_MATRICULA_32']
    missing = [c for c in needed if c not in stage.columns]
    if missing:
        raise RuntimeError(f'Faltan columnas en output para Fase4: {missing}')

    lookup = build_duracion_lookup(dur)

    rows = []
    for r in stage.itertuples(index=False):
        codcli = r.CODCLI
        codcarpr = str(r.CODCARPR_NORM).strip()
        jor = str(r.JOR).strip()
        actual = str(r.CODIGO_CARRERA_SIES_FINAL).strip()
        incluir = str(r.INCLUIR_EN_MATRICULA_32).strip()

        cands = lookup.get((codcarpr, jor), [])
        if len(cands) == 1:
            proposed = cands[0]
            source = 'DURACION_UNICO'
            estado = 'RESUELTO_DURACION'
        elif len(cands) > 1:
            proposed = ''
            source = 'DURACION_MULTIPLE'
            estado = 'REQUIERE_REVISION_DURACION'
        elif actual:
            proposed = actual
            source = 'FALLBACK_PIPELINE_ACTUAL'
            estado = 'RESUELTO_FALLBACK'
        else:
            proposed = ''
            source = 'SIN_RESOLUCION'
            estado = 'PENDIENTE'

        rows.append({
            'CODCLI': codcli,
            'CODCARPR_NORM': codcarpr,
            'JOR': jor,
            'INCLUIR_EN_MATRICULA_32': incluir,
            'CODIGO_SIES_ACTUAL': actual,
            'CODIGO_SIES_PROPUESTO_F4': proposed,
            'FUENTE_PROPUESTA_F4': source,
            'ESTADO_F4': estado,
            'N_CANDIDATOS_DURACION': str(len(cands)),
            'CANDIDATOS_DURACION': '|'.join(cands),
            'COINCIDE_CON_ACTUAL': 'SI' if proposed and actual and proposed == actual else 'NO',
        })

    detalle = pd.DataFrame(rows)
    detalle.to_csv(DETALLE_PATH, sep='\t', index=False)

    pendientes = detalle[detalle['ESTADO_F4'].isin(['PENDIENTE', 'REQUIERE_REVISION_DURACION'])].copy()
    pendientes.to_csv(PEND_PATH, sep='\t', index=False)

    comp = detalle[(detalle['CODIGO_SIES_PROPUESTO_F4'] != '') & (detalle['CODIGO_SIES_ACTUAL'] != '')]
    coincide = int((comp['COINCIDE_CON_ACTUAL'] == 'SI').sum())

    rep = pd.DataFrame([
        ('total_filas_output', str(len(detalle))),
        ('filas_incluir_mu32_si', str(int((detalle['INCLUIR_EN_MATRICULA_32'] == 'SI').sum()))),
        ('resueltas_por_duracion_unico', str(int((detalle['FUENTE_PROPUESTA_F4'] == 'DURACION_UNICO').sum()))),
        ('resueltas_por_fallback_actual', str(int((detalle['FUENTE_PROPUESTA_F4'] == 'FALLBACK_PIPELINE_ACTUAL').sum()))),
        ('pendientes_sin_resolucion', str(int((detalle['ESTADO_F4'] == 'PENDIENTE').sum()))),
        ('requieren_revision_duracion', str(int((detalle['ESTADO_F4'] == 'REQUIERE_REVISION_DURACION').sum()))),
        ('comparables_con_actual', str(len(comp))),
        ('coinciden_con_actual', str(coincide)),
        ('tasa_coincidencia_pct', f"{(coincide / len(comp) * 100):.2f}" if len(comp) else '0.00'),
    ], columns=['metrica', 'valor'])
    rep.to_csv(REPORTE_PATH, sep='\t', index=False)

    print('FASE 4 ADAPTADOR PARALELO CODCARPR')
    print(f'Detalle: {DETALLE_PATH}')
    print(f'Pendientes: {PEND_PATH} ({len(pendientes)} filas)')
    print(f'Reporte: {REPORTE_PATH}')


if __name__ == '__main__':
    main()

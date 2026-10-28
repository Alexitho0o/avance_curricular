"""Comparación H001 a cohorte fija; no exporta identificadores individuales."""
from collections import Counter, defaultdict
from hashlib import file_digest
import json
from pathlib import Path
from openpyxl import load_workbook
from common.analisis_desercion.h001 import reproducir_h001, llave, origen, positivo, codigo, normalizar

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx'
with path.open('rb') as f:
    assert file_digest(f, 'sha256').hexdigest() == '5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3'
w = load_workbook(path, read_only=True, data_only=True)
def read(name):
    it = w[name].values
    h = next(it)
    return [dict(zip(h, r)) for r in it if any(x is not None for x in r)]
rows = read('BASE_RETENCION_MU')
catalogo = read('01_CATALOGO_CARRERA')
eligible = reproducir_h001(rows, catalogo)
index = defaultdict(list)
for row in rows:
    index[(row['ANIO_INFORMADO'], llave(row))].append(row)
official = {2022:0.6895161290322581, 2023:0.7057220708446866, 2024:0.675, 2025:0.5821152192605331}
for year in (2022, 2023, 2024, 2025):
    cohort = eligible[year]
    outcomes = []
    for row, positive in cohort:
        next_rows = index[(year+1, llave(row))]
        same = [r for r in next_rows if origen(r) == origen(row)]
        any_vig = bool(same)
        outcomes.append((row, positive, any_vig, next_rows, same))
    den = len(outcomes)
    count_pos = sum(x[1] for x in outcomes)
    count_any = sum(x[2] for x in outcomes)
    assert count_any >= count_pos
    print(year, 'den',den,'vig_positivo',count_pos,'cualquier_vig',count_any,
          'delta_personas',count_any-count_pos,'tasas_pct',round(100*count_pos/den,4),round(100*count_any/den,4),
          'brechas_pp',round((count_pos/den-official[year])*100,4),round((count_any/den-official[year])*100,4))
    if year == 2022:
        situation = Counter()
        codes = Counter()
        for row, pos, any_vig, next_rows, same in outcomes:
            if pos: continue
            reason = 'sin_registro_tmas1' if not next_rows else ('mismo_origen_solo_vig0' if same else 'otro_origen_sin_mismo_origen')
            situation[reason] += 1
            codes[codigo(row)] += 1
        print('2022_no_retenidos_estado_tmas1',dict(situation))
        print('2022_no_retenidos_por_codigo',dict(sorted(codes.items())))
        prior = {llave(r) for r in rows if r['ANIO_INFORMADO']==2022 and r['ANIO_ING_ACT']==2022 and r['VIG']==1}
        h001 = {llave(r) for r, _ in cohort}
        by_program = defaultdict(list)
        for c in catalogo:
            by_program[(normalizar(c['ANO']),normalizar(c['CODIGO_UNICO']))].append(c)
        reasons = Counter()
        limits = {'Técnico de Nivel Superior':4, 'Profesional Sin Licenciatura':6,
                  'Profesional Con Licenciatura':8, 'Licenciatura no conducente a título':8}
        for k in prior-h001:
            rs = [r for r in index[(2022,k)] if r['ANIO_ING_ACT']==2022 and r['VIG']==1]
            if any(origen(r)[0]!='2022' or origen(r)[1] not in ('1','2') for r in rs):
                reasons['origen_no_admitido']+=1
            elif any(len(by_program[('OFE_2022',codigo(r))])!=1 for r in rs):
                reasons['catalogo_no_unico']+=1
            else:
                cs=[by_program[('OFE_2022',codigo(r))][0] for r in rs]
                if any(normalizar(c['NIVEL_GLOBAL'])!='Pregrado' or normalizar(c['TIPO_CARRERA'])!='Plan Regular' or normalizar(c['PLAN_ESPECIAL'])!='NO APLICA' for c in cs):
                    reasons['programa_no_regular_o_especial']+=1
                elif any(normalizar(c['NIVEL_CARRERA']) not in limits or c['DURACION_ESTUDIOS'] is None for c in cs):
                    reasons['duracion_nivel_no_disponible']+=1
                elif any(float(c['DURACION_ESTUDIOS'])<limits[normalizar(c['NIVEL_CARRERA'])] for c in cs):
                    reasons['duracion_menor_al_minimo']+=1
                else:
                    reasons['duplicidad_o_inconsistencia']+=1
        print('2022_solo_prototipo_primera_causa',dict(reasons))

audit_path = ROOT/'data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json'
with audit_path.open('rb') as f:
    assert file_digest(f, 'sha256').hexdigest() == '003c55b57e2aa476a8bd6d9223ec46d4155f59f7311d0183eea24c795226cff0'
audit = json.loads(audit_path.read_text())
union = audit['impacto_nominas']['UNION']
assert (union['en_retencion_anual2025'], union['no_retenidos_anual2025'],
        union['con_misma_cohorte_en_base2026_no_retenidos']) == (291, 291, 276)
baseline = eligible[2025]
retained = sum(ret for _, ret in baseline)
assert (len(baseline), retained) == (1150, 668)
print('escenario_H001_nominas', 'cohorte', len(baseline), 'en_nominas',291,
      'misma_cohorte_vig0',276,'retenidos_base',retained,
      'retenidos_escenario',retained+276,'tasa_escenario',round((retained+276)/len(baseline)*100,4))

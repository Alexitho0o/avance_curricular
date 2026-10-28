"""Reproduce H001 y compara universo 2025, emitiendo solo agregados."""
from collections import Counter, defaultdict
from hashlib import file_digest
from pathlib import Path
from openpyxl import load_workbook
from common.analisis_desercion.h001 import reproducir_h001, llave, codigo, origen, normalizar
from common.analisis_desercion.retencion_primer_anio import calcular

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / 'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx'
with p.open('rb') as f:
    assert file_digest(f, 'sha256').hexdigest() == '5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3'
w = load_workbook(p, read_only=True, data_only=True)
def read(name):
    it = w[name].values
    h = next(it)
    return [dict(zip(h, r)) for r in it if any(x is not None for x in r)]
rows, catalogo = read('BASE_RETENCION_MU'), read('01_CATALOGO_CARRERA')
eligible = reproducir_h001(rows, catalogo)
expected = {2022:(305,224), 2023:(366,258), 2024:(558,326), 2025:(1150,668)}
for y, (den, num) in expected.items():
    cases = eligible[y]
    assert (len(cases), sum(ret for _, ret in cases)) == (den, num)
    assert len({llave(r) for r, _ in cases}) == den
    print(y, 'casos',den,'retenidos',num,'tasa',round(100*num/den,6),'personas_unicas',den)
for result in calcular(rows, catalogo):
    assert (result['denominador'], result['retenidos']) == expected[result['cohorte']]
print('consumidor_default_2022_2025: PASS')

# Compare old prototype's eligible individuals with H001 without exporting IDs.
old = {llave(r) for r in rows if r['ANIO_INFORMADO'] == 2025 and r['ANIO_ING_ACT'] == 2025 and r['VIG'] == 1}
new = {llave(r) for r, _ in eligible[2025]}
print('2025 prototipo',len(old),'H001',len(new),'interseccion',len(old & new),'solo_prototipo',len(old-new),'solo_H001',len(new-old))
cat = defaultdict(list)
for r in catalogo:
    cat[(normalizar(r['ANO']),normalizar(r['CODIGO_UNICO']))].append(r)
groups = Counter()
origenes = Counter()
detalles_104 = Counter()
tipos_de_los_353 = Counter()
especiales_353 = Counter()
duracion_353 = Counter()
por_carrera = Counter()
person_index = defaultdict(list)
for r in rows:
    person_index[(r['ANIO_INFORMADO'],llave(r))].append(r)
for k in old-new:
    rr = [r for r in rows if r['ANIO_INFORMADO'] == 2025 and r['ANIO_ING_ACT'] == 2025 and r['VIG'] == 1 and llave(r)==k]
    # Classification is hierarchical, person-level and only for differences.
    if any(origen(r)[0] != '2025' or origen(r)[1] not in ('1','2') for r in rr):
        reason = 'origen_distinto_o_periodo_no_admitido'
        origenes[tuple(sorted({origen(r) for r in rr}))] += 1
    elif any(len(cat[('OFE_2025',codigo(r))]) != 1 for r in rr):
        reason = 'catalogo_no_unico'
    else:
        cc = [cat[('OFE_2025',codigo(r))][0] for r in rr]
        if any(normalizar(c['NIVEL_GLOBAL']) != 'Pregrado' or normalizar(c['TIPO_CARRERA']) != 'Plan Regular' or normalizar(c['PLAN_ESPECIAL']) != 'NO APLICA' for c in cc):
            reason = 'programa_no_regular_o_especial'
        elif any(normalizar(c['NIVEL_CARRERA']) not in {'Técnico de Nivel Superior','Profesional Sin Licenciatura','Profesional Con Licenciatura','Licenciatura no conducente a título'} or c['DURACION_ESTUDIOS'] is None for c in cc):
            reason = 'duracion_o_nivel_no_disponible'
        elif any(float(c['DURACION_ESTUDIOS']) < {'Técnico de Nivel Superior':4,'Profesional Sin Licenciatura':6,'Profesional Con Licenciatura':8,'Licenciatura no conducente a título':8}[normalizar(c['NIVEL_CARRERA'])] for c in cc):
            reason = 'duracion_menor_al_minimo'
        else:
            reason = 'duplicidad_o_inconsistencia_cohorte_t1_tmas1'
            r = rr[0]; co=origen(r)
            active = [x for x in person_index[(2025,k)] if x['VIG'] in (1,2) and origen(x)==co]
            follow = [x for x in person_index[(2026,k)] if x['VIG'] in (1,2)]
            same = [x for x in follow if origen(x)==co]
            detalles_104[(len(active)>1, len(follow)>len(same))] += 1
    groups[reason]+=1
    for kind in {normalizar(c.get('TIPO_CARRERA')) for r in rr for c in cat[('OFE_2025',codigo(r))]}:
        tipos_de_los_353[kind]+=1
    for flag in {normalizar(c.get('PLAN_ESPECIAL')) for r in rr for c in cat[('OFE_2025',codigo(r))]}:
        especiales_353[flag]+=1
    for c in [c for r in rr for c in cat[('OFE_2025',codigo(r))]]:
        minimum={'Técnico de Nivel Superior':4,'Profesional Sin Licenciatura':6,'Profesional Con Licenciatura':8,'Licenciatura no conducente a título':8}.get(normalizar(c['NIVEL_CARRERA']))
        if minimum is None or c['DURACION_ESTUDIOS'] is None:
            duracion_353['sin_minimo_o_duracion']+=1
        elif float(c['DURACION_ESTUDIOS']) < minimum:
            duracion_353['menor_al_minimo']+=1
        else:
            duracion_353['cumple_minimo']+=1
    for cod in {codigo(r) for r in rr}:
        por_carrera[cod]+=1
print('solo_prototipo_2025_por_primera_causa',dict(groups))
print('origenes_249',dict(origenes))
print('detalles_104_actual_multiple_y_siguiente_diferente',dict(detalles_104))
print('tipos_353_no_excluyentes',dict(tipos_de_los_353))
print('especiales_353_no_excluyentes',dict(especiales_353))
print('duracion_353_por_fila_catalogo_no_personas',dict(duracion_353))
print('codigos_353_no_excluyentes',dict(por_carrera))
for year in (2022, 2024):
    prior = {llave(r) for r in rows if r['ANIO_INFORMADO']==year and r['ANIO_ING_ACT']==year and r['VIG']==1}
    hkeys = {llave(r) for r, _ in eligible[year]}
    additions, removals = prior-hkeys, hkeys-prior
    programs = Counter(codigo(r) for r in rows if r['ANIO_INFORMADO']==year and r['ANIO_ING_ACT']==year and r['VIG']==1 and llave(r) in additions)
    print(year,'prototipo',len(prior),'H001',len(hkeys),'solo_prototipo',len(additions),'solo_H001',len(removals),'registros_por_codigo_solo_prototipo',dict(programs))

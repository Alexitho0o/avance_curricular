#!/usr/bin/env python3
"""Reconstruye hechos observados MRUN sin exportar identidades ni asignar mallas.

Contrato: docs/fase_2_historia_observada_mrun.md. Solo biblioteca estándar.
Las transiciones unen cortes observados, no prueban migraciones curriculares.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

ACADEMIC = ('codigo_unico','cod_inst','cod_sede','cod_carrera','nomb_carrera',
            'modalidad','jornada','version','tipo_plan_carr','vigencia_carrera',
            'dur_estudio_carr','dur_proceso_tit','dur_total_carr')
COHORTS = ('anio_ing_carr_ori','sem_ing_carr_ori','anio_ing_carr_act','sem_ing_carr_act')
DURATIONS = ('dur_estudio_carr','dur_proceso_tit','dur_total_carr')
DETAIL = ('cat_periodo',) + ACADEMIC + COHORTS
MISSING = {'','NULL','NAN','NONE'}
PATTERN = re.compile(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)\Z')


def digest(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def components(code: str):
    match = PATTERN.fullmatch(code)
    return tuple(int(v) for v in match.groups()) if match else None


def family(row: dict) -> str | None:
    p=components(row['codigo_unico'])
    return f'I{p[0]}S{p[1]}C{p[2]}J{p[3]}' if p else None


def present(value: str) -> bool:
    return value.upper() not in MISSING


def cohort_status(row: dict, side: str) -> str:
    year=row[f'anio_ing_carr_{side}']; semester=row[f'sem_ing_carr_{side}']
    if not present(year) or not present(semester):
        return 'INCOMPLETA'
    if year=='1900' and semester=='0':
        return 'SENTINELA_1900_0'
    if year=='1900':
        return 'VALOR_ESPECIAL_1900_OTRO_SEMESTRE'
    if not re.fullmatch(r'\d{4}',year) or semester not in ('1','2'):
        return 'FORMATO_O_SEMESTRE_NO_ESTANDAR'
    if int(year)>int(row['cat_periodo']):
        return 'POSTERIOR_AL_ANIO_OBSERVADO'
    return 'CRONOLOGICA_COMPLETA'


def nonnegative_number(value: str) -> bool:
    try:
        number=Decimal(value)
        return number.is_finite() and number>=0
    except InvalidOperation:
        return False


def public_row(row: dict) -> dict:
    return {'registro_csv':row['_record'], 'linea_final_csv':row['_line'],
            **{k:row[k] for k in DETAIL}}


def classify(left: list[dict], right: list[dict]) -> str:
    if len(left)!=1 or len(right)!=1:
        return 'CONJUNTOS_CON_MULTIMATRICULA_SIN_EMPAREJAR'
    a,b=left[0]['codigo_unico'],right[0]['codigo_unico']
    if a==b:
        return 'MISMO_CODIGO'
    pa,pb=components(a),components(b)
    if pa is None or pb is None:
        return 'CAMBIO_CON_CODIGO_HEREDADO'
    if pa[:4]==pb[:4]:
        return 'CAMBIO_VERSION_AUMENTA' if pb[4]>pa[4] else 'CAMBIO_VERSION_DISMINUYE'
    changed=[name for name,x,y in zip(('INSTITUCION','SEDE','CARRERA','JORNADA'),pa[:4],pb[:4]) if x!=y]
    return 'CAMBIO_'+'_Y_'.join(changed)


def build(rows: list[dict]) -> dict:
    """Funciones puras; el MRUN queda solo en estructuras locales de memoria."""
    person_year=defaultdict(lambda:defaultdict(list))
    code_rows=defaultdict(list)
    annual_groups=defaultdict(list)
    cohort_groups=defaultdict(list)
    families=defaultdict(list)
    complete_keys=set()
    missing_identity=[]
    component_mismatches=[]
    cohort_order_exceptions=[]
    status_counts=defaultdict(Counter)
    chronological_order_inversions=0
    last_year=None
    for r in rows:
        y=int(r['cat_periodo'])
        if not 2007<=y<=2026 or r['cod_inst']!='162':
            raise ValueError('Fuera del alcance institución162/años2007–2026')
        if last_year is not None and y<last_year:
            chronological_order_inversions+=1
        last_year=y
        identity=r.get('mrun','')
        if present(identity):
            key=(identity,y,r['codigo_unico'])
            if key in complete_keys:
                raise ValueError('Clave persona-año-código duplicada: revisar fuente; no se deduplica automáticamente')
            complete_keys.add(key)
            person_year[identity][y].append(r)
        else:
            missing_identity.append(public_row(r))
        code_rows[r['codigo_unico']].append(r)
        annual_groups[tuple(r[k] for k in ('cat_periodo',)+ACADEMIC)].append(r)
        cohort_groups[tuple(r[k] for k in DETAIL)].append(r)
        f=family(r)
        if f:
            families[f].append(r)
            p=components(r['codigo_unico'])
            for key,expected in zip(('cod_inst','cod_sede','cod_carrera','version'),(p[0],p[1],p[2],p[4])):
                if r[key]!=str(expected):
                    component_mismatches.append({'registro_csv':r['_record'],'codigo_unico':r['codigo_unico'],'campo':key,'valor':r[key],'componente':expected})
        for side in ('ori','act'):
            status_counts[(y,side)][cohort_status(r,side)]+=1
        if all(cohort_status(r,side)=='CRONOLOGICA_COMPLETA' for side in ('ori','act')):
            original=(int(r['anio_ing_carr_ori']),int(r['sem_ing_carr_ori']))
            actual=(int(r['anio_ing_carr_act']),int(r['sem_ing_carr_act']))
            if original>actual:
                cohort_order_exceptions.append(public_row(r))

    history=[]
    for code,group in sorted(code_rows.items()):
        years=sorted({int(r['cat_periodo']) for r in group})
        byyear=Counter(r['cat_periodo'] for r in group)
        names={y:sorted({r['nomb_carrera'] for r in group if r['cat_periodo']==str(y)}) for y in years}
        history.append({'codigo_unico':code,'familia_sies':family(group[0]),
            'estructura':'MODERNA' if components(code) else 'HEREDADA_NO_DESCOMPUESTA',
            'anios_observados':years,'primera_observacion':years[0],'ultima_observacion':years[-1],
            'anios_intermedios_sin_observacion':[y for y in range(years[0],years[-1]+1) if y not in years],
            'filas_por_anio':dict(sorted(byyear.items())), 'nombres_mrun_por_anio':names,
            'registros_ejemplo_por_anio':{y:min(r['_record'] for r in group if r['cat_periodo']==str(y)) for y in years},
            'limite':'Primera/última observación no son vigencias de oferta ni fechas de malla.'})

    family_history=[]
    coexistences=[]
    for f,group in sorted(families.items()):
        fy=defaultdict(list)
        for r in group: fy[int(r['cat_periodo'])].append(r)
        versions=sorted({components(r['codigo_unico'])[4] for r in group})
        first_year=min(fy)
        first_versions=sorted({components(r['codigo_unico'])[4] for r in fy[first_year]})
        family_history.append({'familia':f,'versiones_observadas':versions,
            'primer_anio_observado':first_year,'versiones_en_primer_anio_observado':first_versions,
            'versiones_por_anio':{y:sorted({components(r['codigo_unico'])[4] for r in g}) for y,g in sorted(fy.items())},
            'limite':'No completar V1 ni ordenar mallas por el ordinal V.'})
        for y,g in sorted(fy.items()):
            v=sorted({components(r['codigo_unico'])[4] for r in g})
            if len(v)>1:
                coexistences.append({'familia':f,'anio_observado':y,'versiones':v,'filas_matricula':len(g),
                    'registros_ejemplo_por_version':{str(n):min(r['_record'] for r in g if components(r['codigo_unico'])[4]==n) for n in v}})

    signature_fields=('cat_periodo','modalidad','tipo_plan_carr')+COHORTS+DURATIONS+('nomb_carrera','jornada')
    signatures=defaultdict(list)
    eligible=0
    for r in rows:
        f=family(r)
        if not f or not all(present(r[k]) for k in signature_fields): continue
        if any(cohort_status(r,side)!='CRONOLOGICA_COMPLETA' for side in ('ori','act')): continue
        if (int(r['anio_ing_carr_ori']),int(r['sem_ing_carr_ori']))>(int(r['anio_ing_carr_act']),int(r['sem_ing_carr_act'])): continue
        if not all(nonnegative_number(r[k]) for k in DURATIONS): continue
        signatures[(f,)+tuple(r[k] for k in signature_fields)].append(r)
        eligible+=1
    ambiguous=[]
    for signature,group in sorted(signatures.items()):
        codes=sorted({r['codigo_unico'] for r in group})
        if len(codes)<2: continue
        ambiguous.append({'familia':signature[0], **dict(zip(signature_fields,signature[1:])),
            'codigos_observados':codes,'filas_matricula':len(group),
            'registros_ejemplo_por_codigo':{c:min(r['_record'] for r in group if r['codigo_unico']==c) for c in codes},
            'interpretacion':'Mismos criterios observados dejan varias versiones; causa curricular no demostrada.'})

    transitions=defaultdict(lambda:{'count':0,'example':None})
    transition_counts=Counter();contiguous_counts=Counter();gap_count=0
    expected_transitions=0
    multi_years=0
    same_code_attribute_changes=0
    for yearly in person_year.values():
        years=sorted(yearly)
        expected_transitions+=max(0,len(years)-1)
        multi_years+=sum(len(v)>1 for v in yearly.values())
        for ya,yb in zip(years,years[1:]):
            left=sorted(yearly[ya],key=lambda r:r['codigo_unico'])
            right=sorted(yearly[yb],key=lambda r:r['codigo_unico'])
            kind=classify(left,right)
            prev_codes=tuple(r['codigo_unico'] for r in left)
            next_codes=tuple(r['codigo_unico'] for r in right)
            changed=tuple(k for k in ACADEMIC+COHORTS if len(left)==len(right)==1 and left[0][k]!=right[0][k])
            if kind=='MISMO_CODIGO' and changed: same_code_attribute_changes+=1
            key=(ya,yb,prev_codes,next_codes,kind,changed)
            transitions[key]['count']+=1
            pair=(tuple(r['_record'] for r in left),tuple(r['_record'] for r in right))
            old=transitions[key]['example']
            if old is None or pair<old: transitions[key]['example']=pair
            transition_counts[kind]+=1
            if yb-ya==1: contiguous_counts[kind]+=1
            else: gap_count+=1
    transition_rows=[]
    for key,g in sorted(transitions.items()):
        ya,yb,pc,nc,kind,changed=key
        transition_rows.append({'anio_anterior':ya,'anio_siguiente_observado':yb,'anios_sin_observacion':yb-ya-1,
           'codigos_anteriores':list(pc),'codigos_siguientes':list(nc),'clase':kind,
           'atributos_distintos_en_pares_singulares':list(changed),'transiciones_entre_cortes':g['count'],
           'registros_ejemplo_anterior':list(g['example'][0]),'registros_ejemplo_siguiente':list(g['example'][1])})
    assert sum(transition_counts.values())==expected_transitions
    assert sum(r['transiciones_entre_cortes'] for r in transition_rows)==expected_transitions

    def grouped_export(groups,fields):
        return [{**dict(zip(fields,key)),'filas_matricula':len(g),
                 'registro_ejemplo':min(r['_record'] for r in g)} for key,g in sorted(groups.items())]
    annual=grouped_export(annual_groups,('cat_periodo',)+ACADEMIC)
    cohorts=grouped_export(cohort_groups,DETAIL)
    assert sum(r['filas_matricula'] for r in annual)==len(rows)
    assert sum(r['filas_matricula'] for r in cohorts)==len(rows)
    representatives=[]
    for label,f in [('Informatica_diurna','I162S2C1J1'),('Logistica_distancia','I162S2C77J4'),
                    ('Ciberseguridad_vespertina','I162S2C46J2'),('Naturopatia_vespertina','I162S2C90J2')]:
        relevant=[h for h in history if h['familia_sies']==f]
        reps=[]
        for h in relevant:
            code=h['codigo_unico'];g=code_rows[code]
            first=min(g,key=lambda r:(int(r['cat_periodo']),r['_record']))
            reps.append(public_row(first))
        representatives.append({'caso':label,'familia':f,'primeras_observaciones_por_codigo':reps,
            'coexistencias':[c for c in coexistences if c['familia']==f],
            'contraejemplo_criterios_completos':next((a for a in ambiguous if a['familia']==f),None)})

    return {'historia_codigos.json':history,'versiones_por_familia.json':family_history,
       'historia_codigo_anio.tsv':annual,'cohortes_observadas.tsv':cohorts,
       'coexistencias.json':coexistences,'criterios_insuficientes.json':{
           'key_fields':['familia_sies']+list(signature_fields),'eligible_observations':eligible,
           'complete_signature_groups':len(signatures),'groups_with_multiple_versions':len(ambiguous),
           'filter':'Componentes modernos; atributos presentes; ambas cohortes con años de cuatro dígitos distintos de1900, semestres1/2, años<=observación y (año,semestre) original<=actual; duraciones numéricas no negativas. Filtro analítico, no validación normativa retrospectiva.',
           'groups':ambiguous},
       'transiciones_observadas.tsv':transition_rows,'ejemplos_academicos.json':representatives,
       'excepciones.json':{'missing_identity':missing_identity,'component_mismatches':component_mismatches,
           'original_cohort_after_current':cohort_order_exceptions,
           'cohort_status_by_year':[{'anio_observado':y,'cohorte':s,**dict(sorted(c.items()))} for (y,s),c in sorted(status_counts.items())],
           'legacy_codes':[h for h in history if h['estructura']!='MODERNA'],
           'limite':'Vacíos y códigos heredados se conservan. Un estado analítico no demuestra error ni autoriza corregir la fuente.'},
       'resumen.json':{'phase':2,'milestone':'H2_HISTORIA_OBSERVADA_RECONSTRUIDA',
           'observations':len(rows),'years_observed':sorted({int(r['cat_periodo']) for r in rows}),
           'distinct_mrun_in_memory_only':len(person_year),'complete_observation_keys':len(complete_keys),
           'observations_without_mrun':len(missing_identity),'program_codes':len(history),
           'modern_families':len(family_history),'families_with_multiple_versions':sum(len(f['versiones_observadas'])>1 for f in family_history),
           'families_first_observed_without_v1':[f['familia'] for f in family_history if 1 not in f['versiones_en_primer_anio_observado']],
           'family_years_with_coexisting_versions':len(coexistences),
           'complete_criteria_groups_with_multiple_versions':len(ambiguous),
           'source_year_order_decreases':chronological_order_inversions,
           'person_years_with_multiple_programs':multi_years,
           'transitions_between_observed_years':expected_transitions,
           'transitions_with_unobserved_years_between':gap_count,
           'transition_counts_all_observed_pairs':dict(sorted(transition_counts.items())),
           'transition_counts_contiguous_years':dict(sorted(contiguous_counts.items())),
           'same_code_pairs_with_any_attribute_change':same_code_attribute_changes,
           'units':'Observaciones=filas de matrícula; códigos y familias=programas; transiciones=pares de años observados de una máscara. Unidades no sumables.',
           'limits':['No se asigna versión UMAS ni se prueba actualización de malla.',
                     'La causa de cambios SIES, correcciones o continuidad requiere contraste con otras fuentes.',
                     'Primera aparición no prueba inicio real; ausencia no prueba cierre, abandono o reingreso.',
                     'No se enlazaron personas MRUN con RUT/CODCLI de UMAS.',
                     'La unicidad del identificador se evalúa en esta instantánea; no acredita estabilidad entre entregas.']}}


def read_rows(path: Path) -> list[dict]:
    rows=[]
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        required=set(DETAIL)|{'mrun'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f'Faltan columnas: {sorted(required-set(reader.fieldnames or []))}')
        for index,raw in enumerate(reader,start=2):
            if None in raw:
                raise ValueError(f'Columnas sobrantes en registro{index}')
            rows.append({**{k:str(raw.get(k) or '').strip() for k in required},
                         '_record':index,'_line':reader.line_num})
    return rows


def encode_outputs(data: dict) -> dict[str,bytes]:
    import io
    encoded={}
    for name,body in sorted(data.items()):
        if name.endswith('.json'):
            text=json.dumps(body,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
        else:
            stream=io.StringIO(newline='')
            columns=list(body[0]) if body else []
            writer=csv.DictWriter(stream,fieldnames=columns,delimiter='\t',lineterminator='\n')
            writer.writeheader()
            for row in body:
                writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in row.items()})
            text=stream.getvalue()
        encoded[name]=text.encode('utf-8')
    return encoded


def run(source: Path, expected: str, destination: Path) -> dict:
    actual=digest(source)
    if actual!=expected:
        raise ValueError('SHA-256 distinto del esperado; no se sustituye silenciosamente el corte')
    rows=read_rows(source)
    data=build(rows)
    data['resumen.json']['source']={'path':str(source.resolve()),'sha256':actual,
        'row_locator':'registro_csv empieza en2 con encabezado en1; linea_final_csv usa csv.reader.line_num.'}
    encoded=encode_outputs(data)
    manifest={'schema_version':1,'phase':2,'source_sha256':actual,
        'script_sha256':digest(Path(__file__)), 'outputs':{n:hashlib.sha256(b).hexdigest() for n,b in encoded.items()},
        'privacy':'Solo dimensiones académicas, conteos agregados y localizadores de ejemplo; sin valores MRUN/RUT/CODCLI ni IDs derivados.',
        'checks':{'complete_keys_unique':True,'all_observations_reconciled_in_annual_and_cohort_groups':True,
                  'transitions_reconciled':True,'original_source_unchanged':digest(source)==actual}}
    assert manifest['checks']['original_source_unchanged']
    encoded['manifest.json']=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    for name,body in encoded.items():
        p=destination/name
        if p.exists() and p.read_bytes()!=body:
            raise ValueError(f'Salida existente diferente: {p}; usar destino nuevo para otra versión')
    destination.mkdir(parents=True,exist_ok=True)
    for name,body in encoded.items():
        (destination/name).write_bytes(body)
    return data['resumen.json']


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fuente',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.fuente,args.sha256,args.salida),ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())

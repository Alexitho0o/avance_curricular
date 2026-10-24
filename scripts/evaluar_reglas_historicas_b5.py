#!/usr/bin/env python3
"""Aprende reglas observadas con reserva por persona y ensayos temporales separados."""
import json,sys,hashlib
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fuentes_reglas_b5 import cargar_base_b4
from scripts.fuentes_ensayo_enlace_conjunto import doc,token,sha
from scripts.reconstruir_planes_umas import read_sheet
from common.reglas_historicas_b5 import clave,estado,consultar,EXTRAS
OUT=ROOT/'data/reglas_historicas_b5/20261016'


def clean(v):
    v=token(v)
    return '' if v.upper() in {'NULL','NONE','NAN'} else v


def main():
    b=cargar_base_b4();d=b['d'];ctx=b['ctx'];sources=b['sources']
    matrix=json.loads((ROOT/'data/matriz_academica_b4/20261016/matriz_contextos.json').read_text())
    bykey={(r['codcarpr'],r['sede_umas'],r['jornada_umas'],r['anio_observado'],r['ingreso_original_declarado'],r['primer_anio_observado_en_carrera'],tuple(r['planes_observados'])):r for r in matrix}
    extra,_=read_sheet(d['sm']['path'],d['sm']['sheet'],('PERIODOINGRESO','PERIODOMATRICULA','ANOMATRICULA'))
    extra={r['_fila']:r for r in extra}
    refrows=defaultdict(list)
    for r in d['references']:
        if r['person']:refrows[r['year'],r['person']].append(r)
    records=[];excluded=Counter()
    for (row,y),flags in sorted(ctx['evidence'].items()):
        r=ctx['byrow'][row];p=doc(r['RUT']);g=b['rowgroups'][row]
        if not g:excluded['SIN_GRUPO']+=1;continue
        family=set(g['familias'])
        refs=[x for x in refrows[y,p] if x['code'].rsplit('V',1)[0] in family and len(b['possible_programs'][p,x['code'].rsplit('V',1)[0]])==1]
        codes={x['code'] for x in refs}
        if len(codes)!=1:
            excluded['SIN_ETIQUETA_DOCUMENTAL' if not codes else 'VARIOS_CODIGOS_EN_MISMA_OBSERVACION']+=1;continue
        career=token(r['CODCARPR']);episode=b['episodes'][p,career];ps=tuple(sorted(b['plans'][row,y]));ori=token(r['ANOINGRESO'])
        key=(career,token(r['SEDE']),token(r['JORNADA']),y,ori,episode,ps);context=bykey[key]['contexto']
        x=extra[row]
        inp=dict(codcarpr=career,sede=token(r['SEDE']),jornada=token(r['JORNADA']),anio=y,ingreso_original=clean(ori),primera_observacion=episode,
                 planes=list(ps) or ['PLAN_NO_OBSERVADO'],periodo_ingreso=clean(x['PERIODOINGRESO']),anomatricula=clean(x['ANOMATRICULA']),periodo_matricula=clean(x['PERIODOMATRICULA']))
        split='RESERVA' if int(hashlib.sha256(('b5-reserva-persona-v1|'+p).encode()).hexdigest(),16)%5==0 else 'CONSTRUCCION'
        records.append({'person':p,'input':inp,'code':next(iter(codes)),'context':context,'split':split,
                        'report':{f:tuple(sorted({x[f] for x in refs})) for f in ('ori','semori','act','semact')}})
    trainpeople={r['person'] for r in records if r['split']=='CONSTRUCCION'};testpeople={r['person'] for r in records if r['split']=='RESERVA'}
    assert not trainpeople & testpeople
    registry=[];evaluations={};examples=[]
    for model in EXTRAS:
        train=defaultdict(lambda:defaultdict(set));test=defaultdict(lambda:defaultdict(set));inputs={};contexts=defaultdict(set)
        for r in records:
            k=clave(r['input'],model)
            if k is None:continue
            (train if r['split']=='CONSTRUCCION' else test)[k][r['code']].add(r['person'])
            inputs[k]=r['input'];contexts[k].add(r['context'])
        counts=Counter()
        for k,tc in test.items():
            codes=set(train.get(k,{}))
            for code,persons in tc.items():
                result='SIN_REGLA' if not codes else 'CONFLICTO_CONSTRUCCION' if len(codes)>1 else 'COINCIDE' if code in codes else 'CONTRADICE'
                counts[result]+=len(persons)
        counts['OBSERVACIONES_RESERVA_SIN_CLAVE']=len({(r['person'],r['context']) for r in records if r['split']=='RESERVA' and clave(r['input'],model) is None})
        for n,(k,tc) in enumerate(sorted(train.items()),1):
            codes=set(tc);good=bad=0
            for code,persons in test.get(k,{}).items():
                if len(codes)==1:
                    if code in codes:good+=len(persons)
                    else:bad+=len(persons)
            offerok=all((inputs[k]['anio'],code) in b['offer'] for code in codes)
            mat=inputs[k]['anomatricula']
            posterior='anomatricula' in EXTRAS[model] and mat.isdigit() and int(mat)>inputs[k]['anio']
            state=estado(codes,offerok,good,bad,posterior)
            registry.append({'id':f'B5-{model}-{n:04d}','modelo':model,'clave':k,'entrada':{f:inputs[k][f] for f in inputs[k] if f in ('codcarpr','sede','jornada','anio','ingreso_original','primera_observacion','planes')+EXTRAS[model]},
                'codigos_construccion':sorted(codes),'personas_construccion':len(set().union(*tc.values())),
                'reserva_coincidente':good,'reserva_contradictoria':bad,'oferta_anual_presente':offerok,
                'estado':state,'matricula_posterior_al_anio_observado':posterior,'contextos_b4':sorted(contexts[k]),'habilitada_para_resolver':False,'autoridad':'INTERNA_OBSERVACIONAL'})
        evaluations[model]={'reglas_construidas':len(train),'evaluacion_reserva':dict(counts),
            'estados_reglas':dict(Counter(r['estado'] for r in registry if r['modelo']==model))}
    # Ensayo de transporte temporal separado: construcción 2018-2020, contraste 2022.
    temporal={}
    for model in EXTRAS:
        tr=defaultdict(set);te=set()
        for r in records:
            k=clave(r['input'],model,True)
            if k is None:continue
            if r['input']['anio']<2022:tr[k].add(r['code'])
            elif r['input']['anio']==2022:te.add((r['person'],k,r['code']))
        counts=Counter()
        for p,k,c in te:
            codes=tr.get(k,set())
            counts['SIN_REGLA' if not codes else 'CONFLICTO_CONSTRUCCION' if len(codes)>1 else 'COINCIDE' if c in codes else 'CONTRADICE']+=1
        temporal[model]=dict(counts)
    # Explicaciones de multiplicidad: particiones diagnósticas, nunca entradas asumidas.
    splits={'K0':(), 'PERIODOINGRESO_UMAS':('periodo_ingreso',), 'MATRICULA_UMAS':('anomatricula','periodo_matricula'),
            'K3_UMAS':('periodo_ingreso','anomatricula','periodo_matricula'),
            'SEM_ORIGINAL_SIES':('semori',), 'INGRESO_ACTUAL_SIES':('act','semact'), 'INGRESOS_SIES_COMPLETOS':('ori','semori','act','semact')}
    multi=[]
    for context in [r for r in matrix if r['estado']=='MULTIPLES_DESTINOS']:
        rr=[r for r in records if r['context']==context['contexto']];partitions={}
        for name,fields in splits.items():
            parts=defaultdict(set);people=defaultdict(set)
            for r in rr:
                k=tuple(r['input'][f] if f in r['input'] else r['report'][f] for f in fields)
                parts[k].add(r['code']);people[k].add(r['person'])
            partitions[name]={'grupos':len(parts),'grupos_con_varios_codigos':sum(len(cs)>1 for cs in parts.values()),'grupos_con_una_persona':sum(len(ps)==1 for ps in people.values())}
        multi.append({'contexto':context['contexto'],'codcarpr':context['codcarpr'],'anio':context['anio_observado'],'codigos_b4':context['codigos_documentales'],
            'personas_etiqueta_documental':len({r['person'] for r in rr}),'particiones':partitions})
    for state in ('CORROBORADA_EN_RESERVA','CONTRADICCION_EN_RESERVA','CONFLICTO_CONSTRUCCION','OBSERVADA_SIN_RESERVA'):
        r=next((r for r in registry if r['modelo']=='K0' and r['estado']==state),None)
        if r:examples.append({'entrada':r['entrada'],'resultado':consultar(registry,r['entrada']),'personas_construccion':r['personas_construccion'],'reserva_coincidente':r['reserva_coincidente'],'reserva_contradictoria':r['reserva_contradictoria']})
    summary={'hito':'B5','estado':'REGLAS_OBSERVADAS_Y_VALIDACION_EJECUTADAS','personas_construccion':len(trainpeople),'personas_reserva':len(testpeople),
       'observaciones_etiquetadas':len(records),'exclusiones_observaciones':dict(excluded),'hipotesis':evaluations,'transporte_2018_2020_a_2022':temporal,
       'contextos_multiples_b4':len(multi),'contextos_sin_multiplicidad_tras_particion':{name:sum(bool(r['particiones'][name]['grupos']) and r['particiones'][name]['grupos_con_varios_codigos']==0 for r in multi) for name in splits},
       'reglas_efectivas_h5_promovidas':0,'modelo_seleccionado_para_produccion':None,
       'limites':['Reserva por persona comparte fuentes institucionales; no es certificación formal.','Primera observación y etiqueta de plan no acreditan vigencia histórica.','Conservar todas las hipótesis evita elegir con la reserva y reutilizarla como prueba independiente.']}
    for p,h in sources.items():assert sha(Path(p) if Path(p).is_absolute() else ROOT/p)==h,p
    protected=json.loads((ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json').read_text())['referencias_sha256']
    for p,h in protected.items():assert sha(ROOT/p)==h,p
    excel=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_8_20261015/entrega.json').read_text())['archivo']
    assert sha(excel)=='f6431d9bf571a4db0769cf8f4d5b90eee95413477406ddf9a328e657a85298dd'
    prior=ROOT/'data/matriz_academica_b4/20261016';manifest=json.loads((prior/'manifest.json').read_text())
    for n,h in manifest['salidas_sha256'].items():assert sha(prior/n)==h
    OUT.mkdir(parents=True,exist_ok=True)
    outputs={'resumen.json':summary,'reglas_observadas.json':registry,'diagnostico_16_contextos.json':multi,'ejemplos_consulta.json':examples,
       'qa.json':{'personas_construccion_y_reserva_disjuntas':True,'contextos_multiples_conservados':len(multi)==16,'referencias_preservadas':len(protected),'excel_intacto':True,'b4_intacto':True,'identificadores_exportados':False}}
    for n,v in outputs.items():(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    for p in ('scripts/evaluar_reglas_historicas_b5.py','scripts/consultar_reglas_b5.py','scripts/fuentes_reglas_b5.py','common/reglas_historicas_b5.py','tests/test_reglas_historicas_b5.py','scripts/fuentes_matriz_academica.py','scripts/fuentes_capa_demografica.py','scripts/fuentes_ensayo_enlace_conjunto.py','scripts/diagnosticar_enlace_conjunto.py','common/capa_demografica.py','common/enlace_conjunto.py','common/presencia_anual.py','common/matriz_academica.py'):
        sources[p]=sha(ROOT/p)
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_y_codigo_sha256':sources,'salidas_sha256':{n:sha(OUT/n) for n in outputs}},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Audita demografía y retiene propuestas contradictorias sin generar unicidad nueva."""
import json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fuentes_capa_demografica import cargar_presencia
from scripts.fuentes_ensayo_enlace_conjunto import doc,token,year,sha
from scripts.diagnosticar_enlace_conjunto import build_graphs
from common.capa_demografica import nacimiento,sexo,comparar,puerta
from common.enlace_conjunto import solve
OUT=ROOT/'data/capa_demografica/20261016'


def main():
    ctx=cargar_presencia();d=ctx['d'];sources=ctx['sources']
    up=defaultdict(lambda:{'birth':set(),'sex':set(),'bad':False})
    mp=defaultdict(lambda:{'birth':set(),'sex':set(),'bad':False})
    rp=defaultdict(lambda:{'birth':set(),'sex':set()})
    raw_quality=defaultdict(Counter)
    for r in d['da']:
        p=doc(r['RUT'])
        b,bs=nacimiento(r['FECHANACIMIENTO']);s,ss=sexo(r['SEXO'],'UMAS')
        raw_quality['UMAS_nacimiento'][bs]+=1;raw_quality['UMAS_sexo'][ss]+=1
        if not p:continue
        up[p]['birth'].add(b);up[p]['sex'].add(s);up[p]['bad'] |= bs!='VALIDO' or ss!='VALIDO'
    # Auditoría longitudinal MRUN: no ligar MRUN distintos por sus atributos.
    for r in d['rawmr']:
        m=token(r['mrun'])
        b,bs=nacimiento(r['fec_nac_alu']);s,ss=sexo(r['gen_alu'],'MRUN')
        raw_quality['MRUN_nacimiento'][bs]+=1;raw_quality['MRUN_sexo'][ss]+=1
        if not m:continue
        mp[m]['birth'].add(b);mp[m]['sex'].add(s);mp[m]['bad'] |= bs!='VALIDO' or ss!='VALIDO'
    for r in d['references']:
        if not r['person']:continue
        key=r['year'],r['person']
        rp[key]['birth'].add(r['birth']);rp[key]['sex'].add({'M':'HOMBRE','F':'MUJER'}.get(r['sex']))
    def clean_ok(v):
        return not v['bad'] and len(v['birth'])==1 and len(v['sex'])==1
    comparisons={};counts=Counter();byyear=Counter();incidences=[]
    for (y,p),v in rp.items():
        if p not in up:
            counts['PERSONA_AUSENTE_UMAS']+=1
            continue
        states={f:comparar(up[p][f],v[f]) for f in ('birth','sex')}
        comparisons[y,p]=states
        for f,s in states.items():byyear[y,f,s]+=1
        label='COINCIDE_AMBOS' if all(s=='COINCIDE' for s in states.values()) else 'REQUIERE_REVISION'
        counts[label]+=1
        if label!='COINCIDE_AMBOS':
            incidences.append({'anio':y,'nacimiento':states['birth'],'sexo':states['sex']})
    graphs,_,_,_=build_graphs(ctx['expanded'],d['mr'],d['groups'])
    sol={}
    for y,g in graphs['cohorte_original'].items():
        forced,_=solve(g);sol.update({(y,p):m for p,m in forced.items()})
    def evaluate(m,target):
        if not m:return 'SIN_ENLACE_FORZADO'
        if not target:return 'ENLACE_SIN_REFERENCIA_UNIVOCA'
        return 'CONCUERDA_CON_REFERENCIA' if m==target else 'CONTRADICE_REFERENCIA'
    cases=[];evaluations={v:Counter() for v in ('base','calidad_interna','contraste_documental')};gates=Counter()
    retained=defaultdict(Counter)
    for n,p in enumerate(d['sample'],1):
        anchor=d['anchors'][p];y=int(anchor['ANOMATRICULA']);m=sol.get((y,p));target=d['adjudicated'].get((y,p))
        internal=clean_ok(up[p]) and (clean_ok(mp[m]) if m else True)
        states=comparisons.get((y,p))
        gate=puerta(internal, list(states.values()) if states is not None else None)
        gates[gate]+=1
        choices={'base':m,'calidad_interna':m if internal else None,
                 'contraste_documental':m if not gate.startswith('RETENIDO_') else None}
        rr={'caso':f'ENSAYO-{n:03d}','anio':y,'codcarpr':token(anchor['CODCARPR']),
            'contraste_por_documento':states,'estado_calidad':gate,'evaluacion':{}}
        for v,chosen in choices.items():
            result=evaluate(chosen,target);evaluations[v][result]+=1;rr['evaluacion'][v]=result
            if m and not chosen:retained[v][evaluate(m,target)]+=1
        cases.append(rr)
    baseline=json.loads((ROOT/'data/presencia_anual/20261016/resumen.json').read_text())['evaluacion_500']['cohorte_original']
    assert dict(evaluations['base'])==baseline,'No hay paridad con ensayo previo'
    assert len(cases)==len(set(d['sample']))==500
    # Agrupar incidencias; no exponer persona, fechas ni identificadores seudónimos.
    agg=Counter((r['anio'],r['nacimiento'],r['sexo']) for r in incidences)
    population=Counter()
    for (y,p),m in sol.items():
        states=comparisons.get((y,p))
        population[puerta(clean_ok(up[p]) and clean_ok(mp[m]),list(states.values()) if states is not None else None)]+=1
    summary={'muestra_personas':500,'paridad_ensayo_anterior':True,'calidad_campos_filas':{k:dict(v) for k,v in raw_quality.items()},
        'personas_umas_documento_normalizable':len(up),'mrun_historicos_distintos':len(mp),
        'conflictos_entre_expedientes_umas':{f:sum(len(v[f]-{None})>1 for v in up.values()) for f in ('birth','sex')},
        'conflictos_longitudinales_mrun':{f:sum(len(v[f]-{None})>1 for v in mp.values()) for f in ('birth','sex')},
        'contraste_persona_anio_documental':dict(counts),'calidad_muestra_500':dict(gates),
        'evaluacion_500':{v:dict(c) for v,c in evaluations.items()},'enlaces_retenidos_muestra':{v:dict(c) for v,c in retained.items()},
        'calidad_propuestas_universo':dict(population),
        'advertencia':'La puerta documental comparte reportes con la referencia: no constituye validación independiente. Solo retiene propuestas; no las corrige ni crea nuevas.',
        'identidades_certificadas':0}
    for p,h in sources.items():assert sha(Path(p) if Path(p).is_absolute() else ROOT/p)==h,p
    protected=json.loads((ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json').read_text())['referencias_sha256']
    for p,h in protected.items():assert sha(ROOT/p)==h,p
    excel=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_8_20261015/entrega.json').read_text())['archivo']
    assert sha(excel)=='f6431d9bf571a4db0769cf8f4d5b90eee95413477406ddf9a328e657a85298dd'
    # Verificar también que ningún artefacto anterior cambió durante la ampliación.
    prior=ROOT/'data/presencia_anual/20261016';manifest=json.loads((prior/'manifest.json').read_text())
    for n,h in manifest['salidas_sha256'].items():assert sha(prior/n)==h
    OUT.mkdir(parents=True,exist_ok=True)
    outputs={'resumen.json':summary,'casos_500.json':cases,
      'contraste_por_anio.json':[{'anio':k[0],'campo':k[1],'estado':k[2],'personas':v} for k,v in sorted(byyear.items())],
      'incidencias_agregadas.json':[{'anio':k[0],'nacimiento':k[1],'sexo':k[2],'personas':v} for k,v in sorted(agg.items())],
      'qa.json':{'paridad_500':True,'referencias_preservadas':len(protected),'excel_intacto':True,'resultados_previos_intactos':True,'identificadores_exportados':False}}
    for n,v in outputs.items():(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    for p in ('scripts/diagnosticar_capa_demografica.py','scripts/fuentes_capa_demografica.py','common/capa_demografica.py','tests/test_capa_demografica.py','scripts/fuentes_ensayo_enlace_conjunto.py','scripts/diagnosticar_enlace_conjunto.py','common/enlace_conjunto.py','common/presencia_anual.py'):
        sources[p]=sha(ROOT/p)
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_y_codigo_sha256':sources,'salidas_sha256':{n:sha(OUT/n) for n in outputs}},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

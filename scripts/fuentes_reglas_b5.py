#!/usr/bin/env python3
"""Reproduce insumos y claves B4 en memoria sin alterar la edición cerrada."""
import json,sys
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fuentes_matriz_academica import cargar_evidencia
from scripts.fuentes_ensayo_enlace_conjunto import doc,token,year,sha
from scripts.reconstruir_planes_umas import read_sheet
from common.presencia_anual import evaluar_nota
from common.versiones_por_cohorte import clave_grupo
from common.capa_demografica import puerta
from common.matriz_academica import estado_contexto,comparar_evidencias
OUT=ROOT/'data/matriz_academica_b4/20261016'


def cargar_base_b4():
    z=cargar_evidencia();ctx=z['ctx'];d=z['d'];sources=z['sources']
    assert len(z['sol'])==2418
    masterpath=ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json'
    assert sha(masterpath)=='2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5'
    sources[str(masterpath)]=sha(masterpath);master=json.loads(masterpath.read_text())
    offer={(r['anio'],r['codigo_unico']):r for r in master['oferta_anual']}
    firstoffer={}
    for y,code in offer:firstoffer[code]=min(y,firstoffer.get(code,y))
    plans=defaultdict(set);plan_sources=defaultdict(set)
    for p in ctx['paths']:
        rows,_=read_sheet(p,'Hoja1',('CODCLI','RUT','DIG','CODCARR','ANO','DESCRIPCION_ESTADO','CONVALIDADO','PLAN_DE_ESTUDIO'))
        for r in rows:
            aa=ctx['index'][token(r['CODCLI']),token(r['CODCARR'])]
            status,y=evaluar_nota(r,aa);plan=token(r['PLAN_DE_ESTUDIO'])
            if status=='ACTIVIDAD_VERIFICADA' and plan and plan.upper() not in {'NULL','NONE','NAN'}:
                for a in aa:
                    plans[a['_fila'],y].add(plan)
                    plan_sources[a['_fila'],y].add(str(p))
    groups=d['groups'];rowgroups={};possible_programs=defaultdict(set)
    for r in d['da']:
        p=doc(r['RUT']);key=clave_grupo(token(r['CODCARPR']),token(r['SEDE']),token(r['JORNADA']))
        g=groups.get(key);rowgroups[r['_fila']]=g
        if p and g:
            for family in g['familias']:possible_programs[p,family].add(key)
    episodes={}
    for (row,y) in ctx['evidence']:
        r=ctx['byrow'][row];k=(doc(r['RUT']),token(r['CODCARPR']))
        episodes[k]=min(y,episodes.get(k,y))
    refs=defaultdict(set);mrcodes=defaultdict(set)
    for r in d['references']:
        if r['person']:refs[r['year'],r['person']].add(r['code'])
    for r in d['mr']:mrcodes[r['year'],r['mrun']].add(r['code'])
    buckets={};observations=Counter()
    for (row,y),flags in sorted(ctx['evidence'].items()):
        r=ctx['byrow'][row];p=doc(r['RUT']);career=token(r['CODCARPR']);g=rowgroups[row]
        families=set(g['familias']) if g else set()
        original=token(r['ANOINGRESO']);episode=episodes[p,career]
        key=(career,token(r['SEDE']),token(r['JORNADA']),y,original,episode,tuple(sorted(plans[row,y])))
        if key not in buckets:
            buckets[key]={'people':set(),'files':set(),'rows':0,'doc':set(),'inf':set(),'amb':set(),'conflicts':0,
                          'persons_with_code':set(),'obs_with_code':0,'obs_only_ambiguous':0,'obs_without_code':0,'units':defaultdict(set),'flags':set(),'source':set(),'gate':Counter()}
        b=buckets[key];b['people'].add(p);b['files'].add(token(r['CODCLI']));b['rows']+=1;b['flags'].update(flags);b['source'].update(plan_sources[row,y])
        dc={c for c in refs[y,p] if c.rsplit('V',1)[0] in families}
        m=z['sol'].get((y,p));states=z['comparisons'].get((y,p))
        gate=puerta(z['clean_ok'](z['up'][p]) and (z['clean_ok'](z['mp'][m]) if m else True),list(states.values()) if states else None)
        b['gate'][gate]+=1
        ic={c for c in mrcodes.get((y,m),set()) if c.rsplit('V',1)[0] in families} if m and not gate.startswith('RETENIDO_') else set()
        # Evitar atribuir la familia de una persona a varios programas UMAS distintos.
        ambiguous={c for c in dc|ic if len(possible_programs[p,c.rsplit('V',1)[0]])>1}
        b['amb'].update(ambiguous);dc-=ambiguous;ic-=ambiguous
        b['doc'].update(dc);b['inf'].update(ic)
        if dc or ic:
            b['obs_with_code']+=1;b['persons_with_code'].add(p)
        elif ambiguous:b['obs_only_ambiguous']+=1
        else:b['obs_without_code']+=1
        for c in dc:b['units']['DOCUMENTAL',c].add(p)
        for c in ic:b['units']['MRUN_PROPUESTO',c].add(p)
        b['conflicts']+=comparar_evidencias(dc,ic)
        observations['sin_grupo' if not g else 'con_grupo']+=1
    h5groups=defaultdict(list)
    for c in master['candidatos_plan_sies']:h5groups[c['codcarpr'],c['sede_umas'],c['jornada_umas']].append(c)
    return locals()

#!/usr/bin/env python3
"""Construye B4 desde evidencia preservada; no genera equivalencias efectivas."""
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


def main():
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
    matrix=[]
    for n,(k,b) in enumerate(sorted(buckets.items()),1):
        career,sede,jornada,y,ori,episode,ps=k;codes=b['doc']|b['inf'];allcodes=codes|b['amb']
        links=[]
        for code in sorted(allcodes):
            o=offer.get((y,code))
            links.append({'codigo_unico':code,'personas_documental':len(b['units']['DOCUMENTAL',code]),'personas_mrun_propuesto':len(b['units']['MRUN_PROPUESTO',code]),
                'tambien_presente_en_asignaciones_ambiguas':code in b['amb'],'primera_oferta_observada':firstoffer.get(code),
                'oferta_anual':({field:o[field] for field in ('nombre_carrera','jornada','modalidad','tipo_plan_sies','duracion_estudios','duracion_total','vigencia','fuente')} if o else None)})
        matrix.append({'contexto':f'B4-{n:05d}','codcarpr':career,'sede_umas':sede,'jornada_umas':jornada,'anio_observado':y,
          'ingreso_original_declarado':ori,'primer_anio_observado_en_carrera':episode,'planes_observados':list(ps),
          'personas':len(b['people']),'personas_con_codigo_admisible':len(b['persons_with_code']),
          'observaciones_con_codigo_admisible':b['obs_with_code'],'observaciones_solo_ambiguas':b['obs_only_ambiguous'],'observaciones_sin_codigo':b['obs_without_code'],'expedientes':len(b['files']),'observaciones_umas':b['rows'],
          'evidencia_presencia':sorted(b['flags']),'fuentes_plan':sorted(b['source']),
          'estado':estado_contexto(codes,bool(b['amb']),b['conflicts']),
          'codigos_documentales':sorted(b['doc']),'codigos_mrun_propuestos':sorted(b['inf']),'codigos_asignacion_ambigua':sorted(b['amb']),
          'observaciones_con_contradiccion':b['conflicts'],'estados_demograficos_observaciones':dict(b['gate']),
          'relaciones_sies':links,'regla_efectiva':False,
          'cobertura_personal_del_anio':y in {2018,2019,2020,2022},
          'codigos_candidatos_h5':sorted({c['codigo_unico'] for c in h5groups[career,sede,jornada] if not ps or c['plan_umas'] in ps}),
          'ambito_candidatos_h5':2026})
    code_index=defaultdict(list);plan_index=defaultdict(list)
    for r in matrix:
        for link in r['relaciones_sies']:code_index[link['codigo_unico']].append(r)
        for plan in r['planes_observados']:plan_index[plan].append(r)
    coverage_codes=[]
    for c in master['universo_sies']:
        code=c['codigo_unico'];rr=code_index[code]
        coverage_codes.append({'codigo_unico':code,'nombre_literal_oferta_2026':c['nombre_literal_oferta_2026'],
          'primera_oferta_observada':firstoffer.get(code),'anios_mrun_maestro':c['anios_mrun'],
          'candidatos_h5':c['candidatos_plan'],'contextos_con_evidencia_b4':len(rr),
          'contextos_evidencia_no_ambigua_b4':sum(code in set(r['codigos_documentales']+r['codigos_mrun_propuestos']) for r in rr),
          'contextos_destino_unico_b4':sum(r['estado']=='DESTINO_UNICO_OBSERVADO' and code in set(r['codigos_documentales']+r['codigos_mrun_propuestos']) for r in rr),
          'estado_cobertura':'CON_EVIDENCIA_B4' if rr else 'SOLO_CANDIDATURA_H5' if c['candidatos_plan'] else 'SIN_RELACION_UMAS_OBSERVADA',
          'reglas_efectivas':0})
    coverage_plans=[]
    for p in master['planes_umas']:
        plan=p['CODPESTUD'];rr=plan_index[plan]
        codes=sorted({c for r in rr for c in r['codigos_documentales']+r['codigos_mrun_propuestos']})
        coverage_plans.append({'plan_umas':plan,'contextos_observados_b4':len(rr),'codigos_con_evidencia_b4':codes,
          'codigos_candidatos_h5':p['codigos_sies_candidatos'],
          'estado_cobertura':'CON_RELACION_OBSERVADA_B4' if codes else 'CON_ACTIVIDAD_SIN_RELACION_B4' if rr else 'SIN_ACTIVIDAD_OBSERVADA_B4',
          'asignacion_historica_efectiva_acreditada':False})
    candidates=[]
    for c in master['candidatos_plan_sies']:
        rr=[r for r in plan_index[c['plan_umas']] if (r['codcarpr'],r['sede_umas'],r['jornada_umas'])==(c['codcarpr'],c['sede_umas'],c['jornada_umas'])]
        supported=[r for r in rr if c['codigo_unico'] in set(r['codigos_documentales']+r['codigos_mrun_propuestos'])]
        other=[r for r in rr if r['codigos_documentales'] or r['codigos_mrun_propuestos']]
        candidates.append({'id_h5':c['id'],'codcarpr':c['codcarpr'],'plan_umas':c['plan_umas'],'sede_umas':c['sede_umas'],
           'jornada_umas':c['jornada_umas'],'codigo_unico':c['codigo_unico'],'ambito_candidato_h5':c['ambito_candidato'],
           'contextos_observados':len(rr),'contextos_con_codigo_observado':len(supported),'anios_con_codigo_observado':sorted({r['anio_observado'] for r in supported}),
           'estado':'CODIGO_OBSERVADO_EN_CONTEXTO' if supported else 'OTROS_CODIGOS_OBSERVADOS_NO_DESCARTA_CANDIDATO' if other else 'SIN_CONTRASTE_DISPONIBLE',
           'habilitada_para_resolver':False})
    summary={'hito':'B4','estado':'MATRIZ_CONSTRUIDA_SIN_PROMOCION_DE_REGLAS','contextos':len(matrix),
       'estados_contextos':dict(Counter(r['estado'] for r in matrix)),
       'cobertura_codigos_sies':dict(Counter(r['estado_cobertura'] for r in coverage_codes)),
       'cobertura_planes_umas':dict(Counter(r['estado_cobertura'] for r in coverage_plans)),
       'contraste_candidatos_h5':dict(Counter(r['estado'] for r in candidates)),
       'codigos_sies_preservados':len(coverage_codes),'planes_umas_preservados':len(coverage_plans),'candidatos_h5_preservados':len(candidates),
       'planes_observados_fuera_maestro':sorted(set(plan_index)-{r['plan_umas'] for r in coverage_plans}),
       'codigos_observados_fuera_maestro':sorted(set(code_index)-{r['codigo_unico'] for r in coverage_codes}),
       'contextos_sin_evidencia_dentro_cobertura_personal':sum(r['estado']=='SIN_EVIDENCIA' and r['cobertura_personal_del_anio'] for r in matrix),
       'contextos_sin_evidencia_fuera_cobertura_personal':sum(r['estado']=='SIN_EVIDENCIA' and not r['cobertura_personal_del_anio'] for r in matrix),
       'anios_con_enlace_personal_evaluado':sorted(d['YEARS']) if 'YEARS' in d else [2018,2019,2020,2022],
       'observaciones_umas':dict(observations),'reglas_promovidas':0,
       'limite':'Destino único observado no acredita equivalencia temporal. Las fuentes documental/MRUN no son independientes; no sumar personas entre contextos.'}
    assert (len(coverage_codes),len(coverage_plans),len(candidates))==(141,236,513)
    assert sum(r['observaciones_umas'] for r in matrix)==len(ctx['evidence'])
    assert all(r['observaciones_umas']==r['observaciones_con_codigo_admisible']+r['observaciones_solo_ambiguas']+r['observaciones_sin_codigo'] for r in matrix)
    for path,h in sources.items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==h,path
    protected=json.loads((ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json').read_text())['referencias_sha256']
    for path,h in protected.items():assert sha(ROOT/path)==h,path
    excel=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_8_20261015/entrega.json').read_text())['archivo']
    assert sha(excel)=='f6431d9bf571a4db0769cf8f4d5b90eee95413477406ddf9a328e657a85298dd'
    OUT.mkdir(parents=True,exist_ok=True)
    outputs={'oferta_anual_referencia.json':master['oferta_anual'],'resumen.json':summary,'matriz_contextos.json':matrix,'cobertura_sies.json':coverage_codes,'cobertura_planes.json':coverage_plans,'contraste_513_candidatos.json':candidates,
       'qa.json':{'universos_preservados':True,'observaciones_conciliadas':True,'referencias_preservadas':len(protected),'excel_intacto':True,'propuestas_mrun_antes_puerta':len(z['sol']),'identificadores_exportados':False}}
    for n,v in outputs.items():(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    for p in ('scripts/construir_matriz_academica_b4.py','scripts/fuentes_matriz_academica.py','common/matriz_academica.py','tests/test_matriz_academica.py','scripts/fuentes_capa_demografica.py','scripts/fuentes_ensayo_enlace_conjunto.py','scripts/diagnosticar_enlace_conjunto.py','common/capa_demografica.py','common/enlace_conjunto.py','common/presencia_anual.py'):
        sources[p]=sha(ROOT/p)
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_y_codigo_sha256':sources,'salidas_sha256':{n:sha(OUT/n) for n in outputs}},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

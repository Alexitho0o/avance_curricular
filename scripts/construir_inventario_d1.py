#!/usr/bin/env python3
"""Concilia universos académicos D1 sin reconstruir ni promover equivalencias."""
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/cierre_d1/20261016'
B4='data/matriz_academica_b4/20261016/'
B5='data/reglas_historicas_b5/20261016/'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((ROOT/name).read_text())
def write(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')

def main():
    sources={}
    def source(name):
        sources[name]=digest(ROOT/name);return read(name)
    for prefix in (B4,B5):
        manifest=source(prefix+'manifest.json')
        for name,sha in manifest['salidas_sha256'].items():
            assert digest(ROOT/prefix/name)==sha,(prefix,name)
    ctx=source(B4+'matriz_contextos.json');codes=source(B4+'cobertura_sies.json');plans=source(B4+'cobertura_planes.json')
    rules=source(B5+'reglas_observadas.json');k0=[r for r in rules if r['modelo']=='K0']
    starts=source('data/reglas_negocio/20261015/inicios_por_codigo.json')['codigos']
    starts={r['codigo_unico']:r for r in starts}
    candidates=source(B4+'contraste_513_candidatos.json')
    offers=source(B4+'oferta_anual_referencia.json')
    criteria=source('data/cierre_d1/20261016/criterios.json')
    source('data/cierre_d1/20261016/semantica_temporal.json')
    criteria={x['id']:x for x in criteria}
    ids={c['contexto'] for c in ctx};code_ids={c['codigo_unico'] for c in codes};plan_ids={p['plan_umas'] for p in plans}
    assert (len(ids),len(code_ids),len(plan_ids))==(1986,141,236)
    assert set(starts)==code_ids
    by_context=defaultdict(list)
    for r in k0:
        assert set(r['contextos_b4'])<=ids
        for cid in r['contextos_b4']:by_context[cid].append(r)
    problematic=[r for r in k0 if r['estado'] in ('CONFLICTO_CONSTRUCCION','CONTRADICCION_EN_RESERVA')]
    badctx={cid for r in problematic for cid in r['contextos_b4']}
    multictx={c['contexto'] for c in ctx if c['estado']=='MULTIPLES_DESTINOS'}
    observed=defaultdict(set);ambiguous=defaultdict(set);hypotheses=defaultdict(set);by_plan=defaultdict(set)
    inventory=[]
    def item(kind,key,origin,causes,links,priority):
        causes=sorted(set(causes));assert set(causes)<=set(criteria)
        return {'universo':kind,'id':key,'fuente_original':origin,'vinculos':links,
                'causas_pendientes':causes,'criterios':causes,'prioridad_d2':priority,
                'estado_cierre':'PENDIENTE_REVISION_D2','asignacion_habilitada':False}
    for c in ctx:
        cid=c['contexto'];rr=by_context[cid];states={r['estado'] for r in rr}
        obs=set(c['codigos_documentales'])|set(c['codigos_mrun_propuestos'])
        amb=set(c['codigos_asignacion_ambigua']);hyp=set(c['codigos_candidatos_h5'])
        assert obs|amb|hyp<=code_ids
        assert set(c['planes_observados'])<=plan_ids
        for code in obs:observed[code].add(cid)
        for code in amb:ambiguous[code].add(cid)
        for code in hyp:hypotheses[code].add(cid)
        for plan in c['planes_observados']:by_plan[plan].add(cid)
        causes=['PRIMERA_OBSERVACION_NO_ES_INGRESO','SEDE_JORNADA_HISTORICAS_NO_ACREDITADAS']
        if cid in badctx|multictx:causes.append('CONFLICTO')
        if amb:causes.append('AMBIGUEDAD')
        if not rr:causes.append('SIN_REGLA_K0')
        if 'OBSERVADA_SIN_RESERVA' in states:causes.append('SIN_CONTRASTE_RESERVADO')
        if 'CORROBORADA_EN_RESERVA' in states:causes.append('CORROBORACION_NO_ACREDITACION')
        if not c['planes_observados']:causes.append('SIN_PLAN_OBSERVADO')
        else:
            causes.append('VIGENCIA_MALLA_NO_ACREDITADA')
            if len(c['planes_observados'])>1:causes.append('VARIOS_PLANES_OBSERVADOS')
        if c['estado']=='SIN_EVIDENCIA':causes.append('SIN_EVIDENCIA_EN_ANIOS_EVALUADOS' if c['cobertura_personal_del_anio'] else 'FUERA_COBERTURA_PERSONAL')
        if any(r['oferta_anual'] is None for r in c['relaciones_sies']):causes.append('SIN_OFERTA')
        priority=1 if cid in badctx|multictx else 2 if c['codcarpr'].startswith('CILOG') else 3 if obs or amb else 4
        inventory.append(item('CONTEXTO',cid,c,causes,{'reglas_k0':[r['id'] for r in rr],'codigos_observados':sorted(obs),'codigos_ambiguos':sorted(amb),'codigos_candidatos_h5_ambito_2026':sorted(hyp),'planes_observados':c['planes_observados'],'nivel_observacion':'PROGRAMA_SIN_PLAN' if not c['planes_observados'] else 'CONTEXTO_CON_PLANES_NO_ACREDITADOS'},priority))
    for c in codes:
        code=c['codigo_unico'];start=starts[code];causes=[]
        if not start['anios_ofertados']:causes.append('SIN_OFERTA')
        if start['coincide_limite_inferior_fuente']:causes.append('OFERTA_EN_LIMITE_2010')
        if c['estado_cobertura']=='SIN_RELACION_UMAS_OBSERVADA':causes.append('SIN_RELACION_UMAS')
        elif c['estado_cobertura']=='SOLO_CANDIDATURA_H5':causes.append('SOLO_CANDIDATURA_H5')
        else:causes.append('CORROBORACION_NO_ACREDITACION')
        linked=observed[code]|ambiguous[code]
        inventory.append(item('CODIGO_SIES',code,{'cobertura':c,'inicio':start},causes,{'contextos_observados':sorted(observed[code]),'contextos_ambiguos':sorted(ambiguous[code]),'contextos_candidatura_h5_2026':sorted(hypotheses[code]),'candidatos_h5':[r['id_h5'] for r in candidates if r['codigo_unico']==code]},1 if linked & (badctx|multictx) else 3 if linked else 4))
    for p in plans:
        plan=p['plan_umas'];linked=by_plan[plan]
        causes=['VIGENCIA_MALLA_NO_ACREDITADA']
        if p['estado_cobertura']=='SIN_ACTIVIDAD_OBSERVADA_B4':causes.append('SIN_ACTIVIDAD_OBSERVADA')
        elif p['estado_cobertura']=='CON_ACTIVIDAD_SIN_RELACION_B4':causes.append('SIN_RELACION_PLAN')
        inventory.append(item('PLAN_UMAS',plan,p,causes,{'contextos_observados':sorted(linked),'candidatos_h5':[r['id_h5'] for r in candidates if r['plan_umas']==plan]},1 if linked & (badctx|multictx) else 2 if plan.startswith('CILOG') else 3 if linked else 4))
    # Una fila por contexto P1, con todos sus disparadores: no sumar reglas y contextos.
    queue=[{'expediente':c['contexto'],'codcarpr':c['codcarpr'],'sede':c['sede_umas'],'jornada':c['jornada_umas'],'anio':c['anio_observado'],'contexto_multiple_b4':c['contexto'] in multictx,'reglas_k0_problematicas':[r['id'] for r in problematic if c['contexto'] in r['contextos_b4']],'estado':'PENDIENTE_D2','criterio':'CONFLICTO'} for c in ctx if c['contexto'] in badctx|multictx]
    assert len(inventory)==len({(r['universo'],r['id']) for r in inventory})==2363
    assert {r['id'] for r in inventory if r['universo']=='CONTEXTO'}==ids
    summary={'fase':'D1','estado':'H1_H2_H3_COMPLETADOS','universos':dict(Counter(r['universo'] for r in inventory)),
      'estados_contextos':dict(Counter(c['estado'] for c in ctx)), 'estados_codigos':dict(Counter(c['estado_cobertura'] for c in codes)),
      'estados_planes':dict(Counter(p['estado_cobertura'] for p in plans)), 'estados_k0':dict(Counter(r['estado'] for r in k0)),
      'prioridad_1':{'reglas_k0_problematicas':len(problematic),'contextos_de_reglas_problematicas':len(badctx),'contextos_multiples_b4':len(multictx),'interseccion_contextos':len(badctx&multictx),'expedientes_unicos':len(queue),'solo_b4':sorted(multictx-badctx),'solo_k0':sorted(badctx-multictx)},
      'contextos_cilog':sum(c['codcarpr'].startswith('CILOG') for c in ctx),
      'contextos_sin_plan':sum(not c['planes_observados'] for c in ctx),
      'codigos_sin_oferta':sum(not s['anios_ofertados'] for s in starts.values()),
      'codigos_en_limite_inferior':sum(s['coincide_limite_inferior_fuente'] for s in starts.values()),
      'causas_por_universo':{u:dict(Counter(x for r in inventory if r['universo']==u for x in r['causas_pendientes'])) for u in ('CODIGO_SIES','PLAN_UMAS','CONTEXTO')},
      'categorias_no_aditivas':True,'reglas_promovidas':0,'siguiente_fase':'D2'}
    write('inventario.json',inventory);write('cola_prioridad_1.json',queue);write('resumen.json',summary)
    protected=read('data/unificacion_proyectos/20261015/control_preservacion_final.json')['referencias_sha256']
    for name,sha in protected.items():assert digest(ROOT/name)==sha,name
    c1=source('data/diccionario_c1/20261016/entrega.json')
    for name,sha in c1['archivos_sha256'].items():assert digest(ROOT/name)==sha,name
    c2=source('data/consumo_comun_c2/20261016/qa.json')
    for name,sha in c2['archivos_sha256'].items():assert digest(ROOT/name)==sha,name
    for name in ['fuentes/glosario_oferta_2010_2026.md','fuentes/glosario_oferta_2010_2026.pdf']:
        sources[str((OUT/name).relative_to(ROOT))]=digest(OUT/name)
    sources['scripts/construir_inventario_d1.py']=digest(Path(__file__))
    write('manifest.json',{'fuentes_sha256':sources,'salidas_sha256':{n:digest(OUT/n) for n in ('inventario.json','cola_prioridad_1.json','resumen.json')},'preservacion':{'referencias':len(protected),'c1':True,'c2':True}})
    print(json.dumps({k:v for k,v in summary.items() if k!='causas_por_universo'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

"""Revisión limitada a los 59 E. No toma un estado de DA ni un intake por código SIES."""
import collections as C
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from inventario import ROOT,OUT,P,H14,load,dump,sha
sys.path[:0]=[str(ROOT/'outputs/versiones_mu_h012_20261030'),str(ROOT/'outputs/regla_reol_h011_20261030'),str(ROOT)]
from resolver import vote,reference_year
from aplicar_h011 import anchors,exp,dim
from common.diccionario_sies_seguimiento import rut_normalizado

def main():
    os.umask(0o077)
    x=load(P/'indices.json');target=x['objetivos'];inv=load(OUT/'INVENTARIO.json')['archivos']
    previous=load(P.parent/'h014_20261030/ASIGNACIONES_H014_PRIVADAS.json')
    assert sha(P.parent/'h014_20261030/ASIGNACIONES_H014_PRIVADAS.json') in str(load(H14/'QA_FINAL.json')['reproduccion_sha256'])
    prev={z['observacion_id']:z for z in previous}
    active=load(ROOT/'data/diccionario_sies_seguimiento/activo.json');desc=load(ROOT/active['descriptor'])
    db=sqlite3.connect(Path(desc['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    obs={z['observacion_id']:z for p, in db.execute('select payload from observaciones_archivo_v20') if (z:=json.loads(p))}
    order=load(ROOT/'data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json')['fuentes']['enlaces_privados_H002g']
    assert sha(order['ruta'])==order['sha256'];links=load(order['ruta']);historic=anchors(obs.values(),db,links)
    mu0={(p,int(y),c) for p,y,c in db.execute('select persona,anio,codigo from mu_anual')};db.close()
    ps=load(ROOT/'data/paridad_codigo_sies/tipo_plan_h011_20261030/TIPO_PLAN_v3_CANDIDATO.json')['perfiles']
    profiles={(z['carrera'],z['plan'],z['sede'],z['jornada'],z['anio']):z for z in ps}
    par=load(ROOT/'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
    fam=C.defaultdict(set)
    for r in par:
        for z in r['candidatos_internos']:
            for pl in z['plan_umas']:fam[z['codcarpr'],pl,str(r['cod_sede']),str(r['cod_jornada'])].add(r['codigo_unico'].rsplit('V',1)[0])
    corrected={r['plan']:r['familia_candidata'] for r in load(ROOT/'outputs/versiones_mu_h012_20261030/CORRECCION_FAMILIA_H002_CANDIDATA.json') if r['familia_candidata']}
    offers=C.defaultdict(set)
    for r in load(ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')['oferta_anual']:
        offers[int(r['anio']),r['codigo_unico']].add((r['tipo_plan_sies'],str(r['duracion_total']),r['vigencia']))
    # Catálogo cerrado. Un archivo de preparación/incremental sin recepción no acredita T1.
    received=C.defaultdict(set);prepared=C.defaultdict(set)
    for f,sheet,y,p,code,quality in x['mu']:
        if y.startswith('MAT_'):y=y[4:]
        if not y.isdigit() or not re.fullmatch(r'I162S\d+C\d+J\d+V\d+',code):continue
        (received if quality=='DOCUMENTAL' else prepared)[p,int(y),code].add(f)
    das=C.defaultdict(set)
    for f,sh,b,p,cli,c,s,j,ing,pi,mat,pm,st,si in x['da']:
        if p and cli:das[p,cli].add((c,s,j,ing))
    dims=lambda c,s,j:(c,{'RE':'2','CO':'3','PTG':'4'}.get(s,s),{'D':'1','V':'2','O':'4'}.get(j,j))
    refs=C.defaultdict(set)
    for p,cli,pl,c,j,y,term,f in x['planes']:
        if not p or not y.isdigit() or not cli or not pl:continue
        for car,site,jour,ing in das[p,cli]:
            if car==c and j==jour and ing.isdigit() and int(ing)<=int(y):
                refs[p,int(y)].add((cli,pl,*dims(c,site,j)))
    pools=C.defaultdict(lambda:C.defaultdict(set));novel=C.defaultdict(lambda:C.defaultdict(set))
    for (person,cli,plan),timeline in historic.items():
        for year,cs in timeline.items():
            for code,dimensions in cs:pools[plan,year][person].add(code)
    # Completar el universo documental H012: observaciones documentales en cualquier
    # período con respaldo de mu_anual. No se recalculan asignaciones H010–H014.
    for r in obs.values():
        code=r.get('codigo_documental_atribuible');y=int(r['ano'])
        if (r['persona'],y,code) in mu0:pools[r['plan'],y][r['persona']].add(code)
    extra=C.defaultdict(lambda:C.defaultdict(set));proof=C.defaultdict(set)
    for (person,year,code),files in received.items():
        candidates=set()
        for cli,pl,c,s,j in refs[person,year]:
            if pl in corrected and code.split('C')[1].split('J')[0]!=corrected[pl]:continue
            if code.rsplit('V',1)[0] in fam[c,pl,s,j]:candidates.add((cli,pl,c,s,j))
        if len(candidates)!=1:continue
        cli,pl,c,s,j=next(iter(candidates));ek=(person,cli,pl);entry=(code,(c,s,j))
        if entry not in historic.get(ek,{}).get(year,set()):
            extra[ek][year].add(entry);proof[ek,year,code].update(files)
        if code not in pools[pl,year].get(person,set()):
            novel[pl,year][person].add(code)
    existing=load(H14/'RESIDUAL_E_ACTUAL.json')
    reasons={(r['anio'],r['periodo'],r['plan'],r['sede'],r['jornada'],r['motivo_h013']):r['motivo'] for r in existing}
    byperson=C.defaultdict(list)
    for p,y,c in received:byperson[p].append((y,c,received[p,y,c]))
    results=[]
    for r in target:
        a=prev[r['observacion_id']];assert a['nivel_asignacion']=='E'
        y=a['anio'];ek=exp(r);plan=r['plan'];person=r['persona'];dims0=dim(r);period=a['periodo']
        orig=reasons[y,period,plan,a['sede'],a['jornada'],a['motivo']]
        timeline={yr:set(values) for yr,values in historic.get(ek,{}).items()}
        for yr,values in extra.get(ek,{}).items():timeline.setdefault(yr,set()).update(values)
        doc_year=y if y in timeline else min((yy for yy in timeline if yy>y),default=None)
        if doc_year is None:doc_year=max((yy for yy in timeline if yy<y),default=None)
        out={'observacion_id':r['observacion_id'],'plan':plan,'anio':y,'periodo':period,'motivo_H014':orig,'estado':'E','nivel':None,'codigo':None,'fuentes_con_persona':sorted({f for yr,c,fs in byperson[person] for f in fs}),'sin_T1_expediente_plan':not timeline,'hay_MU_de_persona':bool(byperson[person]) or any(pp==person for pp,yy,cc in mu0),'cargas_preparadas_con_persona':sorted({f for (pp,yr,c),fs in prepared.items() if pp==person for f in fs}),'resultado':orig}
        if orig=='PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO':
            results.append(out);continue
        if doc_year is not None:
            options=timeline[doc_year]
            if len(options)==1:
                code,dd=next(iter(options));annual=doc_year if doc_year>y else y
                pf=profiles.get((r['carrera'],plan,a['sede'],a['jornada'],annual)) or profiles.get((r['carrera'],plan,a['sede'],a['jornada'],y))
                attrs={( {'Plan Regular':'REGULAR','Plan Regular de Continuidad':'CONTINUIDAD'}.get(t,'E'),float(n) if n else None) for t,n,v in offers[annual,code]}
                if dd==dims0 and pf and attrs=={(pf['tipo'],pf['duracion_control'])} and proof[ek,doc_year,code]:
                    level='PRIMER_T1_POSTERIOR' if doc_year>y else 'ARRASTRE_ULTIMO_T1' if doc_year<y else 'DOCUMENTAL_T1' if period=='1' else 'HERENCIA_T1_MISMO_AÑO'
                    out.update(estado='ASIGNADA',nivel=level,codigo=code,fuentes=sorted(proof[ek,doc_year,code]),anio_fuente=doc_year,resultado='NUEVO_ENLACE_ANUAL_ACREDITADO')
        if out['estado']=='E' and orig in ('MU_PLAN_NO_UNANIME','MU_PLAN_MENOS_DE_TRES_PERSONAS') and (timeline or out['hay_MU_de_persona']):
            years={yr for pl,yr in set(pools)|set(novel) if pl==plan};ref=reference_year(years,y)
            if ref is not None:
                pool={p:set(cs) for p,cs in pools[plan,ref].items()}
                for p,cs in novel[plan,ref].items():pool.setdefault(p,set()).update(cs)
                code,why,distribution=vote(pool)
                out.update(anio_referencia=ref,distribucion=distribution)
                if code and novel[plan,ref] and offers[y,code]:
                    out.update(estado='ASIGNADA',nivel='VERSION_POR_MU_DEL_PLAN',codigo=code,fuentes=sorted({f for (p,yy,c),fs in received.items() if yy==ref and c==code and p in novel[plan,ref] for f in fs}),anio_fuente=ref,resultado='UNANIMIDAD_DOCUMENTAL_CON_APORTE_NUEVO')
        if out['estado']=='E' and not out['hay_MU_de_persona'] and not timeline:
            out['resultado']='NUNCA_INFORMADO_PENDIENTE_DECISION_FASE_3'
        results.append(out)
    assert len(results)==59
    dump(P/'RESIDUAL_59_PRIVADO.json',results)
    def agg(fields):
        c=C.Counter(tuple(z.get(k) for k in fields) for z in results)
        return [dict(zip(fields,vals),n=n) for vals,n in sorted(c.items(),key=lambda a:str(a[0]))]
    dump(OUT/'RESIDUAL_59.json',{'total':59,'por_resultado':agg(['estado','resultado']),'por_plan_anio_periodo':agg(['plan','anio','periodo','motivo_H014','resultado','nivel','codigo']),'presencias_por_fuente':[{'archivo':f,'contextos_con_persona_en_MU':sum(f in z['fuentes_con_persona'] for z in results),'contextos_en_preparacion':sum(f in z['cargas_preparadas_con_persona'] for z in results)} for f in sorted({f for z in results for f in z['fuentes_con_persona']+z['cargas_preparadas_con_persona']})],'nuevas':sum(z['estado']=='ASIGNADA' for z in results),'limite':'NUNCA_INFORMADO es ausencia en las fuentes internas examinadas, no inexistencia histórica en SIES. No se asigna código a ese grupo. No se cruza MRUN con RUT.'})
    print(agg(['estado','resultado']))
if __name__=='__main__':main()

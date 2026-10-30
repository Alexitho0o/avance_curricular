"""D10: ampliar únicamente contextos E que tienen un primer T1 posterior acreditado."""
import collections as C
import json
import os
import sqlite3
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
DATA=ROOT/'data/diccionario_sies_seguimiento'
OLD=DATA/'v21_20261030_h013/descriptor.json'
D=DATA/'v22_20261030_h014'
PRIVATE=Path.home()/'.local/share/ipss/h014_20261030'
sys.path.insert(0,str(ROOT/'outputs/regla_reol_h011_20261030'))
from aplicar_h011 import anchors,exp,dim,sha,dump,aggregate
load=lambda p:json.loads(Path(p).read_text())
def ro(p):return sqlite3.connect(Path(p).as_uri()+'?mode=ro',uri=True)
def evaluar(timeline,year,dims,period_ok,profile_for,oferta):
    first=min((t for t in timeline if t>year),default=None)
    if first is None:return first,None,'SIN_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN'
    if not period_ok:return first,None,'PERIODO_NO_HOMOLOGADO'
    if timeline.get(year):return first,None,'TIENE_T1_DEL_ANIO'
    if len(timeline[first])!=1:return first,None,'PRIMER_T1_NO_UNICO'
    code,observed=next(iter(timeline[first]))
    if observed!=dims:return first,code,'DIMENSIONES_DISTINTAS'
    attrs=oferta.get((first,code),set())
    if not attrs:return first,code,'SIN_OFERTA_ANIO_T1'
    pf=profile_for(first)
    if not pf or pf['tipo']=='E' or not pf['duracion_control']:return first,code,'PERFIL_PLAN_NO_ACREDITADO'
    expected=(pf['tipo'],float(pf['duracion_control']))
    actual={(typ,float(total) if total else None) for typ,total in attrs}
    if actual!={expected}:return first,code,'TIPO_O_DURACION_NO_COINCIDE'
    return first,code,'OFERTA_AÑO_T1'


def main():
    os.umask(0o077);PRIVATE.mkdir(exist_ok=True);D.mkdir(parents=True,exist_ok=True)
    old=load(OLD);assert sha(OLD)=='4f6530860a529fbc39ca5c607ecbf14498c0c74de0c14e2c5d4be7f092ab64be'
    base=Path(old['base_privada']['ruta']);assert sha(base)==old['base_privada']['sha256']
    dest=PRIVATE/'DICCIONARIO_V22.sqlite'
    live=load(ROOT/load(DATA/'activo.json')['descriptor'])
    if Path(live['base_privada']['ruta'])==dest:raise RuntimeError('La edición de destino ya está activa')
    db=ro(base);obs={z['observacion_id']:z for p, in db.execute('select payload from observaciones_archivo_v20') if (z:=json.loads(p))}
    sources=load(ROOT/'outputs/versiones_mu_h012_20261030/FUENTES_H012.json')
    def governed(p):
        p=Path(p);p=p if p.is_absolute() else ROOT/p
        assert sha(p)==sources[str(p)];return load(p)
    aa=anchors(obs.values(),db,governed(PRIVATE.parent/'h002g_20261029/ENLACES_MU_DA.json'))
    mu_persona_anio={(p,int(y)) for p,y in db.execute('select distinct persona,anio from mu_anual')}
    candidates=governed('data/paridad_codigo_sies/tipo_plan_h011_20261030/TIPO_PLAN_v3_CANDIDATO.json')['perfiles']
    profiles={(x['carrera'],x['plan'],x['sede'],x['jornada'],x['anio']):x for x in candidates}
    offers=C.defaultdict(set)
    types={'Plan Regular':'REGULAR','Plan Regular de Continuidad':'CONTINUIDAD'}
    for x in governed('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')['oferta_anual']:
        offers[int(x['anio']),x['codigo_unico']].add((types.get(x['tipo_plan_sies'],'E'),x['duracion_total']))
    inp=PRIVATE.parent/'h013_20261030/ASIGNACIONES_H013_PRIVADAS.json'
    assert sha(inp)==load(ROOT/'outputs/activacion_v21_h013_20261030/QA_FINAL.json')['reproduccion_privada']['asignaciones']
    before=load(inp);audit=[]
    def resolve(b):
        if b['nivel_asignacion']!='E':return b
        r=obs[b['observacion_id']];year=b['anio'];timeline=aa[exp(r)]
        key=(b['carrera'],b['plan'],b['sede'],b['jornada'])
        def perfil(t):return profiles.get((*key,t)) or profiles.get((*key,year))
        next_y,code,why=evaluar(timeline,year,dim(r),b['motivo']!='PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO',perfil,offers)
        pf=perfil(next_y)
        audit.append({'observacion_id':b['observacion_id'],'plan':b['plan'],'anio':year,'anio_T1':next_y,'codigo_T1':code,'motivo_anterior':b['motivo'],'control_D10':why,'persona_en_MU_2026':(r['persona'],2026) in mu_persona_anio,'tipo_y_duracion_plan':(pf['tipo'],pf['duracion_control']) if pf else None,'tipo_y_duracion_T1':sorted(offers.get((next_y,code),set()))})
        if why!='OFERTA_AÑO_T1':return b
        return b|{'codigo_candidato':code,'nivel_asignacion':'PRIMER_T1_POSTERIOR','regla':'H014_D10','clase':'D/C','motivo':'OFERTA_AÑO_T1','marcas':[*b.get('marcas',[]),'OFERTA_AÑO_T1'],'año_T1_fuente':next_y,'desfase':next_y-year,'evidencia':[{'anio':next_y,'codigo':code,'fuente':'MU y enlace anual del mismo expediente/plan','control':'OFERTA_AÑO_T1','tipo':pf['tipo'],'duracion_total':pf['duracion_control']}]}
    after=[resolve(b) for b in before];idx={z['observacion_id']:z for z in after};assert all(a==b for a,b in zip(before,after) if a['nivel_asignacion']!='E')
    d7=governed('data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json')
    assert sha(d7['base_privada']['ruta'])==d7['base_privada']['sha256']
    db7=ro(d7['base_privada']['ruta']);hist={z['observacion_id'] for p, in db7.execute('select payload from observaciones') if not (z:=json.loads(p)).get('codigo_interno_adoptado')};db7.close()
    p99=PRIVATE.parent/'h010_20261030/POSICIONES_99_H010B_PRIVADAS.json'
    assert sha(p99)==load(ROOT/'outputs/regla_t1_h010_20261030/REPRODUCCION_H010B.json')['hashes'][str(p99)]
    slots=[idx[x['observacion_id']] for x in load(p99)]
    cases=[z for z in after if z['observacion_id'] in hist];assert len(cases)==3049 and len(slots)==99
    residual=[z for z in cases if z['nivel_asignacion']=='E']
    dump(OUT/'COBERTURA.json',{'historico':aggregate(cases,['nivel_asignacion']),'posiciones99':aggregate(slots,['nivel_asignacion']),'revision_59':aggregate([z for z in audit if z['observacion_id'] in hist],['plan','anio','anio_T1','codigo_T1','motivo_anterior','control_D10']),'residual':aggregate(residual,['motivo'])})
    dump(OUT/'CONTROL_CASOS_ESPERADOS.json',[{k:z[k] for k in z if k!='observacion_id'}|{'contextos':n} for line,n in sorted(C.Counter(json.dumps({k:v for k,v in x.items() if k!='observacion_id'},ensure_ascii=False,sort_keys=True) for x in audit if x['observacion_id'] in hist and x['motivo_anterior'] in ('CODIGO_MU_PLAN_AUSENTE_OFERTA_ANUAL','T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO')).items()) for z in [json.loads(line)]])
    dump(OUT/'RESIDUAL.json',aggregate(residual,['anio','plan','sede','jornada','periodo','motivo']))
    dump(PRIVATE/'ASIGNACIONES_H014_PRIVADAS.json',after)
    tmp=PRIVATE/'v22.tmp.sqlite'
    if tmp.exists():tmp.unlink()
    nc=sqlite3.connect(tmp);db.backup(nc);nc.execute('alter table asignaciones_v21 rename to asignaciones_v22')
    for a,b in zip(before,after):
        if a==b:continue
        oid=b['observacion_id'];r=json.loads(nc.execute('select payload from observaciones where id=?',(oid,)).fetchone()[0])
        r.update(nivel_asignacion=b['nivel_asignacion'],regla=b['regla'],año_T1_fuente=b['año_T1_fuente'],evidencia_asignacion=b['evidencia'],clase=b['clase'],codigo_documental_atribuible=None,codigo_interno_adoptado=b['codigo_candidato'],estado_interno=b['nivel_asignacion'],requisito_pendiente=None,marcas=b['marcas'])
        nc.execute('update observaciones set payload=? where id=?',(json.dumps(r,ensure_ascii=False,sort_keys=True),oid))
        nc.execute('update asignaciones_v22 set nivel_asignacion=?,regla=?,año_T1_fuente=?,evidencia=?,clase=?,codigo=? where observacion_id=?',(b['nivel_asignacion'],b['regla'],b['año_T1_fuente'],json.dumps(b['evidencia'],ensure_ascii=False,sort_keys=True),b['clase'],b['codigo_candidato'],oid))
    nc.commit();assert nc.execute('pragma integrity_check').fetchone()[0]=='ok';nc.close();db.close();tmp.replace(dest)
    meta=load(ROOT/old['capa_promedios']['metadata']);assert sha(ROOT/old['capa_promedios']['metadata'])==old['capa_promedios']['sha256'] and sha(meta['capa_privada']['ruta'])==meta['capa_privada']['sha256']
    meta['sha256_base_diccionario']=sha(dest);dump(D/'CAPA_PROMEDIOS.json',meta)
    desc=old|{'edicion':D.name,'DECISION':'D10, Alexi 30-10-2026','ACTIVO_ANTERIOR':{'descriptor':str(OLD.relative_to(ROOT)),'sha256':sha(OLD),'base_sha256':sha(base)},'base_privada':{'ruta':str(dest),'sha256':sha(dest)},'capa_promedios':{'metadata':str((D/'CAPA_PROMEDIOS.json').relative_to(ROOT)),'sha256':sha(D/'CAPA_PROMEDIOS.json')},'contrato':old['contrato'].replace('v21','v22')+' D10 verifica oferta del primer T1 posterior individual.'}
    dump(D/'descriptor.json',desc);print('Residual',len(residual),'Altas',59-len(residual))
if __name__=='__main__':main()

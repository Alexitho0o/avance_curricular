"""Reutiliza H012, aplica D7 aprobada y construye la base privada v21."""
import collections as C
import json
import os
import sqlite3
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
INPUTS=Path.home()/'.local/share/ipss'
P=INPUTS/'h013_20261030'
D=ROOT/'data/diccionario_sies_seguimiento/v21_20261030_h013'
H12=ROOT/'outputs/versiones_mu_h012_20261030'
sys.path.insert(0,str(H12))
from resolver import vote,reference_year,sha,dump,aggregate,txt,rut_normalizado
OLD='data/diccionario_sies_seguimiento/v20_20261027_candidata_fase_g/descriptor.json'
load=lambda p:json.loads(Path(p).read_text())
def db_ro(p):
    return sqlite3.connect(Path(p).as_uri()+'?mode=ro',uri=True)
def main():
    pointer=load(ROOT/"data/diccionario_sies_seguimiento/activo.json")
    active_source=Path(load(ROOT/pointer["descriptor"])["base_privada"]["ruta"])
    if active_source.resolve()==(P/"DICCIONARIO_V21.sqlite").resolve():raise ValueError("La base de destino ya está activa; reproducir en un directorio privado nuevo")
    os.umask(0o077);P.mkdir(exist_ok=True);D.mkdir(parents=True,exist_ok=True)
    pins=load(H12/'FUENTES_H012.json')
    def governed(p):
        p=Path(p);p=p if p.is_absolute() else ROOT/p
        assert sha(p)==pins[str(p)],p.name
        return load(p)
    old=governed(OLD);base=Path(old['base_privada']['ruta']);assert sha(base)==old['base_privada']['sha256']
    db=db_ro(base)
    obs={z['observacion_id']:z for v, in db.execute('select payload from observaciones') if (z:=json.loads(v))}
    mu={(person,int(y),code) for person,y,code in db.execute('select persona,anio,codigo from mu_anual')}
    pools=C.defaultdict(lambda:C.defaultdict(set))
    for r in obs.values():
        y=int(r['ano']);code=r.get('codigo_documental_atribuible')
        if (r['persona'],y,code) in mu:pools[r['plan'],y][r['persona']].add(code)
    for z in governed(INPUTS/'h002g_20261029/ENLACES_MU_DA.json'):
        if not z['seleccion'] or z['plan_respaldo']!='ANUAL' or not z['plan'] or z['identidad'][0]!='R':continue
        _,body,dv=z['identidad'];person=rut_normalizado(txt(body)+'-'+txt(dv))
        if (person,z['anio'],z['codigo_sies']) in mu:pools[z['plan'],z['anio']][person].add(z['codigo_sies'])
    years=C.defaultdict(set)
    for pl,y in pools:years[pl].add(y)
    inp=INPUTS/'h012_20261030/ASIGNACIONES_H012_PRIVADAS.json'
    assert sha(inp)==load(H12/'QA_H012.json')['reproduccion'][inp.name]
    before=load(inp)
    profiles=governed('data/paridad_codigo_sies/tipo_plan_h011_20261030/TIPO_PLAN_v3_CANDIDATO.json')['perfiles']
    profiles={(p['carrera'],p['plan'],p['sede'],p['jornada'],p['anio']):p for p in profiles}
    # Identificar el único error específico de los 956/1/233 sin reclasificar H012.
    families={x['plan']:x['familia_candidata'] for x in load(H12/'CORRECCION_FAMILIA_H002_CANDIDATA.json') if x['familia_candidata']}
    possible={(z['plan'],z['anio'],z['observado'],z['predicho']) for z in load(H12/'VALIDACION_D7.json')['errores']}
    errors=C.Counter()
    for z in before:
        if z['nivel_asignacion']!='DOCUMENTAL_T1':continue
        p=profiles.get((z['carrera'],z['plan'],z['sede'],z['jornada'],z['anio']))
        if not p or p['motivo_E']:continue
        opts={c for c in p['compatibles'] if p['opciones'][c]['vigencia'] in ('Vigente con estudiantes nuevos','Vigente sin estudiantes nuevos') and (z['plan'] not in families or c.split('C')[1].split('J')[0]==families[z['plan']])}
        if len(opts)<2 or len({(p['opciones'][c]['total'],p['opciones'][c]['tipo']) for c in opts})!=1:continue
        pred,_,_=vote(pools[z['plan'],z['anio']],obs[z['observacion_id']]['persona'])
        key=z['plan'],z['anio'],z['codigo_candidato'],pred
        if pred in opts and key in possible:errors[key]+=1
    assert sum(errors.values())==1
    dump(OUT/'ERROR_D7.json',[{'plan':k[0],'anio':k[1],'informado':k[2],'previsto':k[3],'contextos':n,'distribucion_MU_plan':vote(pools[k[0],k[1]])[2]} for k,n in errors.items()])
    offers={(x['codigo_unico'],int(x['anio'])) for x in governed('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')['oferta_anual']}
    def apply(b):
        if b['nivel_asignacion']!='E':return b
        ext=b['motivo']=='SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD'
        if not ext and not b['motivo'].startswith('D7_NO_SUPERA_VALIDACION'):return b
        pl=b['plan'];y=b['anio'];ref=reference_year(years[pl],y)
        code,why,dist=vote(pools[pl,ref])
        evidence={'referencia':ref,'personas_por_codigo':dist,'motivo_h012':b['motivo']}
        if not code:return b|{'motivo':'MU_PLAN_'+why,'evidencia_h013':evidence}
        if (code,y) not in offers:return b|{'motivo':'CODIGO_MU_PLAN_AUSENTE_OFERTA_ANUAL','evidencia_h013':evidence}
        if not ext and code not in b.get('opciones_h012',[]):return b|{'motivo':'MU_PLAN_FUERA_OPCIONES_COMPATIBLES','evidencia_h013':evidence}
        return b|{'nivel_asignacion':'VERSION_POR_MU_DEL_PLAN','codigo_candidato':code,'regla':'H013_D7_EXTENDIDA' if ext else 'H013_D7','año_T1_fuente':ref,'desfase':ref-y,'evidencia':[evidence],'clase':'D/C','motivo':'CONVERSION_NO_CONFIRMADA' if ext else 'MU_PLAN_UNANIME'}
    after=[apply(b) for b in before];idx={z['observacion_id']:z for z in after}
    d7=governed('data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json')
    assert sha(d7['base_privada']['ruta'])==d7['base_privada']['sha256']
    db7=db_ro(d7['base_privada']['ruta']);ids={r['observacion_id'] for v, in db7.execute('select payload from observaciones') if not (r:=json.loads(v)).get('codigo_interno_adoptado')};db7.close()
    hist=[z for z in after if z['observacion_id'] in ids]
    p99=INPUTS/'h010_20261030/POSICIONES_99_H010B_PRIVADAS.json'
    assert sha(p99)==load(ROOT/'outputs/regla_t1_h010_20261030/REPRODUCCION_H010B.json')['hashes'][str(p99)]
    pos=[idx[z['observacion_id']] for z in load(p99)]
    new=[z for b,z in zip(before,after) if b['observacion_id'] in ids and b['nivel_asignacion']=='E' and z['nivel_asignacion']!='E']
    dump(OUT/'COBERTURA.json',{'historico':aggregate(hist,['nivel_asignacion']),'posiciones99':aggregate(pos,['nivel_asignacion']),'altas':aggregate(new,['regla','plan','anio']),'residual':aggregate([z for z in hist if z['nivel_asignacion']=='E'],['motivo'])})
    dump(OUT/'RESIDUAL.json',aggregate([z for z in hist if z['nivel_asignacion']=='E'],['anio','periodo','plan','sede','jornada','motivo']))
    diagnosis=[]
    for b in before:
        if b['observacion_id'] not in ids or b['nivel_asignacion']!='E' or b['motivo']!='SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD':continue
        key=b['carrera'],b['plan'],b['sede'],b['jornada'],b['anio'];p=profiles[key]
        if not any(z['clave']==list(key) for z in diagnosis):
            diagnosis.append({'clave':list(key),'perfil':p,'mu_documental_por_anio':{yr:vote(pools[b['plan'],yr])[2] for yr in sorted(years[b['plan']])},'resultados':dict(C.Counter(idx[a['observacion_id']]['motivo'] for a in before if a['observacion_id'] in ids and a['motivo']=='SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD' and (a['carrera'],a['plan'],a['sede'],a['jornada'],a['anio'])==key))})
    dump(OUT/'DESCALCES_41.json',diagnosis)
    dump(P/'ASIGNACIONES_H013_PRIVADAS.json',after)
    # La proyección de consulta muestra la edición activa. La fuente v20 se conserva
    # íntegra en la tabla de archivo y en su base original.
    tmp=P/'v21.construccion.sqlite'
    if tmp.exists():tmp.unlink()
    conn=sqlite3.connect(tmp);db.backup(conn);conn.execute('create table observaciones_archivo_v20 as select * from observaciones')
    conn.execute('create table asignaciones_v21(observacion_id integer primary key,nivel_asignacion text,regla text,año_T1_fuente integer,evidencia text,clase text,codigo text)')
    for z in after:
        oid=z['observacion_id'];r=dict(obs[oid]);code=z['codigo_candidato'] or None;lvl=z['nivel_asignacion']
        r.update({k:z[k] for k in ['nivel_asignacion','regla','año_T1_fuente','clase']})
        r.update(evidencia_asignacion=z['evidencia'],codigo_documental_atribuible=code if lvl=='DOCUMENTAL_T1' else None,codigo_interno_adoptado=code if lvl not in ('E','DOCUMENTAL_T1') else None,estado_interno=lvl,requisito_pendiente=z['motivo'] if not code else None)
        if lvl!='DOCUMENTAL_T1':r['aceptacion_SIES']='NO_ACREDITADA'
        conn.execute('update observaciones set payload=? where id=?',(json.dumps(r,ensure_ascii=False,sort_keys=True),oid))
        conn.execute('insert into asignaciones_v21 values(?,?,?,?,?,?,?)',(oid,lvl,z['regla'],z['año_T1_fuente'],json.dumps(z['evidencia'],ensure_ascii=False,sort_keys=True),z['clase'],code))
    conn.commit();assert conn.execute('pragma integrity_check').fetchone()[0]=='ok'
    assert conn.execute('select * from observaciones_archivo_v20 order by id').fetchall()==db.execute('select * from observaciones order by id').fetchall();conn.close();db.close()
    target=P/'DICCIONARIO_V21.sqlite';tmp.replace(target)
    meta=governed(old['capa_promedios']['metadata']) if str(ROOT/old['capa_promedios']['metadata']) in pins else load(ROOT/old['capa_promedios']['metadata'])
    assert sha(ROOT/old['capa_promedios']['metadata'])==old['capa_promedios']['sha256'] and sha(meta['capa_privada']['ruta'])==meta['capa_privada']['sha256']
    meta['sha256_base_diccionario']=sha(target);dump(D/'CAPA_PROMEDIOS.json',meta)
    descriptor={'edicion':'v21_20261030_h013','estado':'ACTIVA','fecha':'2026-10-30','responsable':'Alexi','DECISION':'D7 extendida y activación H013','ACTIVO_ANTERIOR':{'descriptor':OLD,'sha256':sha(ROOT/OLD),'base_sha256':sha(base)},'base_privada':{'ruta':str(target),'sha256':sha(target)},'capa_promedios':{'metadata':'data/diccionario_sies_seguimiento/v21_20261030_h013/CAPA_PROMEDIOS.json','sha256':sha(D/'CAPA_PROMEDIOS.json')},'componentes_sha256':old['componentes_sha256'],'contrato':'Proyección contextual v21 en observaciones. Evidencia v20 preservada íntegra en observaciones_archivo_v20. Nivel, regla, año fuente, evidencia y clase en asignaciones_v21 y payload. MU anual literal se conserva.'}
    dump(D/'descriptor.json',descriptor)
    assert all(a==b for a,b in zip(before,after) if a['nivel_asignacion']!='E') and len(hist)==3049 and len(pos)==99
    print(load(OUT/'COBERTURA.json')['altas'])
if __name__=='__main__':main()

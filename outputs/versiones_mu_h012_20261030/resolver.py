"""H012. Validación y decisiones internas sobre el residual congelado de H011."""
import collections as C
import json
import os
import sqlite3
import sys
from pathlib import Path
from fractions import Fraction

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
OLD=ROOT/'outputs/regla_reol_h011_20261030'
P=Path.home()/'.local/share/ipss/h012_20261030'
sys.path[:0]=[str(ROOT),str(ROOT/'outputs/regla_t1_h010_20261030')]
from construir import sha, dump, txt, aggregate
from common.diccionario_sies_seguimiento import rut_normalizado

V1='Vigente con estudiantes nuevos'
V2='Vigente sin estudiantes nuevos'


def vote(pool, excluded=None):
    """Cada persona cuenta una vez por código. Un solo disenso impide decidir."""
    distribution=C.Counter()
    persons=set()
    for person,codes in pool.items():
        if person==excluded:continue
        persons.add(person)
        distribution.update(codes)
    if len(distribution)>1:return '', 'NO_UNANIME',dict(sorted(distribution.items()))
    if len(persons)<3:return '', 'MENOS_DE_TRES_PERSONAS',dict(distribution)
    return next(iter(distribution)),'UNANIME',dict(distribution)


def reference_year(years,y):
    if y in years:return y
    return min((t for t in years if t>y),default=None) or max((t for t in years if t<y),default=None)


def family(code):return code.split('J')[0]
def number(code):return code.split('C')[1].split('J')[0]


def main():
    os.umask(0o077);P.mkdir(exist_ok=True)
    hashes={}
    def verify(p,h=None):
        p=Path(p);p=p if p.is_absolute() else ROOT/p
        value=sha(p)
        if h and h!=value:raise ValueError('Hash distinto '+p.name)
        hashes[str(p)]=value
        return p
    def load(p,h=None):return json.loads(verify(p,h).read_text())
    prior=load(OLD/'QA_H011.json')['reproduccion_sha256']
    sources=load(OLD/'FUENTES_H011.json',prior['FUENTES_H011.json'])
    frozen=P.parent/'h011_20261030/ASIGNACIONES_H011_PRIVADAS.json'
    before=load(frozen,prior[frozen.name])
    catalog=load('data/paridad_codigo_sies/tipo_plan_h011_20261030/TIPO_PLAN_v3_CANDIDATO.json',prior['TIPO_PLAN_v3_CANDIDATO.json'])['perfiles']
    profiles={(p['carrera'],p['plan'],p['sede'],p['jornada'],p['anio']):p for p in catalog}
    def governed(p):
        p=Path(p);p=p if p.is_absolute() else ROOT/p
        return load(p,sources[str(p)])
    def db_from(desc):
        p=verify(desc['base_privada']['ruta'],desc['base_privada']['sha256'])
        return sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    active=governed('data/diccionario_sies_seguimiento/activo.json')
    db=db_from(load(active['descriptor'],active['sha256']))
    obs={z['observacion_id']:z for p, in db.execute('select payload from observaciones') if (z:=json.loads(p))}
    mu={(person,int(y),code) for person,y,code in db.execute('select persona,anio,codigo from mu_anual')}
    db.close()
    pools=C.defaultdict(lambda:C.defaultdict(set))
    previous=C.defaultdict(set)
    for r in obs.values():
        person=r['persona'];y=int(r['ano']);code=r.get('codigo_documental_atribuible')
        if (person,y,code) in mu:
            pools[r['plan'],y][person].add(code)
            previous[person,txt(r['CODCLI'])].add(y)
        for da in r.get('contextos_DA',[]):
            if txt(da.get('CODCLI'))==txt(r['CODCLI']) and da.get('persona')==person:
                yr=txt(da.get('ANOMATRICULA'))
                if yr.isdigit():previous[person,txt(r['CODCLI'])].add(int(yr))
    links=governed(P.parent/'h002g_20261029/ENLACES_MU_DA.json')
    for z in links:
        if not z['seleccion'] or z['identidad'][0]!='R':continue
        _,body,dv=z['identidad'];person=rut_normalizado(txt(body)+'-'+txt(dv));y=z['anio'];code=z['codigo_sies']
        if (person,y,code) not in mu:continue
        previous[person,txt(z['seleccion'][0])].add(y)
        if z['plan_respaldo']=='ANUAL' and z['plan']:pools[z['plan'],y][person].add(code)
    # Control de familia anterior a la aplicación y a la validación D7.
    par=governed('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
    maestro=governed('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
    names={r['CODPESTUD']:r['nombres_internos_catalogo'] for r in maestro['planes_umas']}
    offers=C.defaultdict(set)
    for r in maestro['oferta_anual']:offers[number(r['codigo_unico'])].add(r['nombre_carrera'])
    hrows=C.defaultdict(list)
    for row in par:
        for candidate in row['candidatos_internos']:
            for plan in candidate['plan_umas']:
                if row['codigo_unico'] not in [z['codigo'] for z in hrows[plan] if z['anio']==row['anio']]:
                    hrows[plan].append({'anio':row['anio'],'codigo':row['codigo_unico'],'estado':row['estado']})
    targets={b['plan'] for b in before if b['nivel_asignacion']=='E'} | {pl for pl in hrows if pl.startswith('IECIREOL')}
    import openpyxl
    listing=verify('data/cierre_d2/20261016/fuentes/Listado_Planes_estudio_Sedes RE+CO.xlsx','fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049')
    wb=openpyxl.load_workbook(listing,read_only=True,data_only=True)
    it=wb['BBDD Bruta'].values;header=next(it);listed=C.defaultdict(set)
    for row in it:
        r=dict(zip(header,row))
        if r['CODPESTUD'] in targets:listed[r['CODPESTUD']].add((txt(r['NOMPESTUD']),txt(r['Nombre_L'])))
    wb.close()
    doc=verify('oferta_academica_2027/01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt')
    assert '3. No Vigente (Sin Estudiantes).' in doc.read_text()

    controls=[];correct={}
    for plan in sorted(targets):
        families={number(x['codigo']) for x in hrows[plan]}
        if len(families)<2 and not plan.startswith('IECIREOL'):continue
        records=[]
        for (pl,y),pool in sorted(pools.items()):
            if pl==plan:
                for code,n in sorted(C.Counter(c for codes in pool.values() for c in codes).items()):
                    records.append({'anio':y,'codigo':code,'personas':n})
        documented={number(x['codigo']) for x in records}
        chosen=None
        if len(documented)==1 and documented<=families:
            f=next(iter(documented))
            if set(names.get(plan,[])) & offers[f]:chosen=f
        if chosen:correct[plan]=chosen
        controls.append({'plan':plan,'nombre_UMAS':names.get(plan,[]),'NOMPESTUD_y_Nombre_L_listado':sorted(listed[plan]),'filas_H002':hrows[plan],'carreras_oferta':{f:sorted(offers[f]) for f in sorted(families)},'MU_documental':records,'familia_candidata':chosen,'estado':'CORRECCION_CANDIDATA' if chosen else 'MEZCLA_DOCUMENTAL' if len(documented)>1 else 'E_SIN_EVIDENCIA_CONCORDANTE'})
    dump(OUT/'CORRECCION_FAMILIA_H002_CANDIDATA.json',controls)
    # Validación dentro del año. El candidato nunca ve la etiqueta del evaluado.
    tests=C.Counter();validation_year=C.defaultdict(C.Counter);errors=C.Counter()
    for (plan,y),pool in pools.items():
        for person,codes in pool.items():
            pred,why,_=vote(pool,person)
            for actual in codes:
                label='ABSTENCION' if not pred else 'ACIERTO' if pred==actual else 'ERROR'
                tests[label]+=1;validation_year[y][label]+=1
                if label=='ERROR':errors[plan,y,pred,actual]+=1
    denominator=tests['ACIERTO']+tests['ERROR']
    precision=Fraction(tests['ACIERTO'],denominator) if denominator else Fraction(0)
    enabled=precision>=Fraction(999,1000)
    documental_t1={(obs[z['observacion_id']]['persona'],z['plan'],z['anio'],z['codigo_candidato']) for z in before if z['nivel_asignacion']=='DOCUMENTAL_T1'}
    checks_t1=C.Counter()
    for person,plan,year,actual in documental_t1:
        pred,why,_=vote(pools[plan,year],person)
        checks_t1['ABSTENCION' if not pred else 'ACIERTO' if pred==actual else 'ERROR']+=1
    scores=checks_t1['ACIERTO']+checks_t1['ERROR']
    t1precision=Fraction(checks_t1['ACIERTO'],scores) if scores else Fraction(0)
    enabled=enabled and t1precision>=Fraction(999,1000)
    # Control específico en el dominio de perfiles anuales H011. Las opciones
    # proceden del contexto UMAS antes de mirar el código oculto.
    applicable=C.Counter()
    for b in before:
        if b['nivel_asignacion']!='DOCUMENTAL_T1':continue
        prof=profiles.get((b['carrera'],b['plan'],b['sede'],b['jornada'],b['anio']))
        if not prof or prof['motivo_E']:continue
        opts={c for c in prof['compatibles'] if (b['plan'] not in correct or number(c)==correct[b['plan']]) and prof['opciones'][c]['vigencia'] in (V1,V2)}
        if len(opts)<2 or len({(prof['opciones'][c]['total'],prof['opciones'][c]['tipo']) for c in opts})!=1:continue
        pred,why,_=vote(pools[b['plan'],b['anio']],obs[b['observacion_id']]['persona'])
        applicable['ABSTENCION' if pred not in opts else 'ACIERTO' if pred==b['codigo_candidato'] else 'ERROR']+=1
    n_app=applicable['ACIERTO']+applicable['ERROR']
    applicable_precision=Fraction(applicable['ACIERTO'],n_app) if n_app else Fraction(0)
    enabled=enabled and applicable_precision>=Fraction(999,1000)

    dump(OUT/'VALIDACION_D7.json',{'clase':'C','unidad':'persona × CODPESTUD × año × código documental distinto','metodo':'Ocultar todos los códigos de la persona en el plan/año. Exigir 3 personas distintas restantes y unanimidad. Precisión = aciertos / predicciones emitidas. Abstenciones separadas. Prueba dentro del año, sin extrapolar al desfase temporal.','totales':dict(tests),'solo_DOCUMENTAL_T1':dict(checks_t1),'contextos_DOCUMENTAL_T1_con_versiones_identicas_en_perfiles_H011':dict(applicable),'precision_dominio_H011_pct':100*float(applicable_precision),'precision_DOCUMENTAL_T1_pct':100*float(t1precision),'por_anio':dict(validation_year),'errores':[{'plan':k[0],'anio':k[1],'predicho':k[2],'observado':k[3],'n':v} for k,v in sorted(errors.items())],'precision_pct':100*float(precision),'umbral_pct':99.9,'D7_habilitada':enabled})
    d7plans=C.defaultdict(set)
    for pl,y in pools:d7plans[pl].add(y)
    def decide(b):
        if b['nivel_asignacion']!='E':return b
        y=b['anio'];plan=b['plan'];old=b['motivo']
        key=(b['carrera'],plan,b['sede'],b['jornada'],y);p=profiles.get(key)
        if old not in {'AMBIGUEDAD_ANUAL_PERSISTENTE','SIN_VIGENCIA_1_COMPATIBLE','VARIAS_VIGENCIA_1_COMPATIBLES'}:return b
        if not p or p['motivo_E']:
            return b|{'motivo':p['motivo_E'] if p else 'SIN_PERFIL_ANUAL','motivo_h011':old}

        r=obs[b['observacion_id']];person=r['persona'];prev=sorted(t for t in previous[person,txt(r['CODCLI'])] if t<y)
        # Un ingreso observado de este año no es continuador a efectos de D8.
        intake={txt(d.get('ANOINGRESO')) for d in r.get('contextos_DA',[]) if txt(d.get('CODCLI'))==txt(r['CODCLI']) and d.get('persona')==person}
        cont=bool(prev) and str(y) not in intake
        orig=p['compatibles'];compatible=[c for c in orig if plan not in correct or number(c)==correct[plan]]
        standard=[c for c in compatible if p['opciones'][c]['vigencia']==V1]
        broaden=old=='SIN_VIGENCIA_1_COMPATIBLE' and cont
        both=[c for c in compatible if p['opciones'][c]['vigencia'] in {V1,V2}]
        options=both if broaden or old=='AMBIGUEDAD_ANUAL_PERSISTENTE' and cont else standard
        def result(reason,code='',level='E',reference=None,distribution=None):
            return b|{'nivel_asignacion':level,'codigo_candidato':code,'motivo':reason,'motivo_h011':old,'regla':'H012','clase':'D/C' if code else 'E','opciones_h012':options,'referencia_documental':reference,'distribucion_documental':distribution or {},'anios_previos_expediente':prev,'D8':broaden,'año_T1_fuente':None,'desfase':None,'evidencia':['Perfil anual H011, control de familia H012 y decisiones D7/D8']}
        if not options:return result('SIN_VERSION_ADMISIBLE_CONTINUADOR' if cont else 'SIN_VIGENCIA_1_O_CONTINUIDAD_ACREDITADA')
        if len(options)==1:
            if not broaden and plan not in correct:return b
            return result('OPCION_UNICA_D8' if broaden else 'OPCION_UNICA_TRAS_CONTROL_FAMILIA',options[0],'VIGENCIA_CONTINUADOR' if broaden else 'FAMILIA_CORREGIDA_CANDIDATA')
        if len({(p['opciones'][c]['total'],p['opciones'][c]['tipo']) for c in options})!=1:return result('PERFILES_NO_IDENTICOS')
        reference=reference_year(d7plans[plan],y)
        if reference is None:return result('SIN_DOCUMENTALES_DEL_PLAN')
        code,why,dist=vote(pools[plan,reference])
        if not enabled:return result('D7_NO_SUPERA_VALIDACION_'+why,reference=reference,distribution=dist)
        if not code:return result('DOCUMENTALES_'+why,reference=reference,distribution=dist)
        if code not in options:return result('VERSION_DOCUMENTAL_FUERA_OPCIONES_ANUALES',reference=reference,distribution=dist)
        return result('UNANIMIDAD_MU_DEL_PLAN',code,'VERSION_POR_MU_DEL_PLAN',reference,dist)
    after=[decide(b) for b in before]
    dump(P/'ASIGNACIONES_H012_PRIVADAS.json',after)
    db7=db_from(governed('data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json'))
    ids={r['observacion_id'] for p, in db7.execute('select payload from observaciones') if not (r:=json.loads(p)).get('codigo_interno_adoptado')};db7.close()
    rows=[(a,b) for a,b in zip(before,after) if a['observacion_id'] in ids]
    assert len(rows)==3049 and all(a==b for a,b in zip(before,after) if a['nivel_asignacion']!='E')
    residual=[b for a,b in rows if b['nivel_asignacion']=='E']
    new=[b for a,b in rows if a['nivel_asignacion']=='E' and b['nivel_asignacion']!='E']
    def details(z):
        return {k:z.get(k) for k in ['anio','plan','carrera','sede','jornada','periodo','motivo','referencia_documental']}|{'opciones':','.join(z.get('opciones_h012',[])),'distribucion':json.dumps(z.get('distribucion_documental',{}),sort_keys=True)}
    rr=[details(z) for z in residual]
    dump(OUT/'RESIDUAL_H012.json',aggregate(rr,list(rr[0])) if rr else [])
    dump(OUT/'COBERTURA_H012.json',{'total':3049,'antes_E':177,'despues_E':len(residual),'altas':aggregate(new,['nivel_asignacion']),'residual':aggregate(residual,['motivo']),'posiciones99':load(OLD/'COBERTURA_H011.json',prior['COBERTURA_H011.json'])['posiciones99'],'altas_con_D8':sum(b.get('D8',False) for b in new)})
    assert len(residual)+len(new)==177
    for z in new:
        p=profiles[z['carrera'],z['plan'],z['sede'],z['jornada'],z['anio']]
        assert z['codigo_candidato'] in p['compatibles'] and z['nivel_asignacion']!='DOCUMENTAL_T1'
    assert all(sha(p)==h for p,h in hashes.items())
    dump(OUT/'FUENTES_H012.json',hashes)
    print('D7',dict(tests),float(precision),'altas',len(new),'E',len(residual))
if __name__=='__main__':main()

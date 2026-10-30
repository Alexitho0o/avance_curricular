"""H011. Overlay privado de residuales sobre H010b. Nunca edita las bases de entrada."""
import collections as C
import json
import os
import sqlite3
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import openpyxl

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = ROOT / 'outputs/regla_t1_h010_20261030'
PRIVATE = Path.home()/'.local/share/ipss/h011_20261030'
sys.path[:0] = [str(ROOT), str(OLD)]
from construir import sha, dump, txt, exp, dim, aggregate
from resolver_h010b import escoger
from common.diccionario_sies_seguimiento import rut_normalizado

CAT = ROOT/'data/paridad_codigo_sies/tipo_plan_h011_20261030'
SITES = {'2':'RE','3':'CO','4':'PTG'}
MODES = {'No Presencial','No presencial','A Distancia'}
TYPES = {'Plan Regular':'REGULAR','Plan Regular de Continuidad':'CONTINUIDAD'}


def semestres(nivel, regimen):
    if not nivel or regimen not in ('BIMESTRAL','TRIMESTRAL','SEMESTRAL'):
        return None,None,'NIVEL_O_REGIMEN_NO_ACREDITADO'
    factor = {'BIMESTRAL':Fraction(2,5),'TRIMESTRAL':Fraction(2,3),'SEMESTRAL':1}[regimen]
    exacto = Fraction(nivel)*factor
    if abs(exacto % 1 - Fraction(1,2)) <= Fraction(1,10):
        return exacto,None,'FRONTERA_REDONDEO'
    entero = -(-exacto.numerator//exacto.denominator) if regimen=='TRIMESTRAL' else int(exacto+Fraction(1,2))
    return exacto,entero,''


def anchors(rows, db, links):
    result = C.defaultdict(lambda:C.defaultdict(set))
    mu = {(person,int(year),code) for person,year,code in db.execute('select persona,anio,codigo from mu_anual')}
    for r in rows:
        y=int(r['ano'])
        c=r.get('codigo_documental_atribuible')
        if txt(r['periodo'])=='1' and (r['persona'],y,c) in mu:
            result[exp(r)][y].add((c,dim(r)))
    for z in links:
        if not z['seleccion'] or z['plan_respaldo']!='ANUAL' or z['identidad'][0]!='R':
            continue
        _,body,dv=z['identidad']
        person=rut_normalizado(txt(body)+'-'+txt(dv))
        sel=z['seleccion']
        sede={'RE':'2','CO':'3','PTG':'4'}.get(txt(sel[2]))
        jornada={'D':'1','V':'2','O':'4'}.get(txt(sel[3]))
        y,c=z['anio'],z['codigo_sies']
        if sede and jornada and (person,y,c) in mu:
            result[person,txt(sel[0]),z['plan']][y].add((c,(txt(sel[1]),sede,jornada)))
    return result


def main():
    os.umask(0o077)
    PRIVATE.mkdir(exist_ok=True)
    CAT.mkdir(parents=True,exist_ok=True)
    hashes={}
    def verify(path,expected=None):
        p=Path(path)
        p=p if p.is_absolute() else ROOT/p
        h=sha(p)
        if expected and h!=expected: raise ValueError('Hash distinto: '+p.name)
        hashes[str(p)]=h
        return p
    def load(path,expected=None):
        return json.loads(verify(path,expected).read_text())
    def database(path):
        d=load(path)
        p=verify(d['base_privada']['ruta'],d['base_privada']['sha256'])
        return sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
    frozen=load(OLD/'REPRODUCCION_H010B.json')['hashes']
    originals=load(OLD/'FUENTES_H010B.json')['fuentes']
    pins={x['ruta']:x['sha256'] for x in originals}
    def governed(path):
        return load(path,pins[str(ROOT/path)])
    ref=load('data/diccionario_sies_seguimiento/activo.json')
    verify(ref['descriptor'],ref['sha256'])
    db=database(ref['descriptor'])
    rows=[json.loads(p) for p, in db.execute('select payload from observaciones')]
    obs={r['observacion_id']:r for r in rows}
    db7=database('data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json')
    historical={z['observacion_id'] for p, in db7.execute('select payload from observaciones') if not (z:=json.loads(p)).get('codigo_interno_adoptado')}
    db7.close()
    previous_dir=PRIVATE.parent/'h010_20261030'
    def previous(name):
        p=previous_dir/name
        return load(p,frozen[str(p)])
    before=previous('ASIGNACIONES_H010B_PRIVADAS.json')
    pos=previous('POSICIONES_99_H010B_PRIVADAS.json')
    e=load(OUT/'EVIDENCIA_PASO1_REOL.json')
    assert e['reanudacion_paso1c']['regimen']=={'S':11228,'A':210}
    paso1_reg={(z['plan'],int(z['anio'])):set(z['regimenes']) for z in e['regimen_por_plan_anio'] if z['anio'].isdigit()}
    rule=governed('data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json')
    link=rule['fuentes']['enlaces_privados_H002g']
    t1=anchors(rows,db,load(link['ruta'],link['sha256']))
    db.close()
    parity=governed('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
    families=C.defaultdict(set)
    for r in parity:
        for candidate in r['candidatos_internos']:
            for plan in candidate['plan_umas']:
                key=(candidate['codcarpr'],plan,txt(r['cod_sede']),txt(r['cod_jornada']))
                families[key].add(r['codigo_unico'].rsplit('V',1)[0])
    offers=C.defaultdict(list)
    for r in governed('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')['oferta_anual']:
        offers[int(r['anio']),r['codigo_unico'].rsplit('V',1)[0]].append(r)
    v2=C.defaultdict(set)
    for r in governed('data/paridad_codigo_sies/regla_operativa_mu_v2/TIPO_PLAN_POR_PLAN_UMAS.json')['filas']:
        if r['tipo_plan'] in TYPES.values() and r['duracion_diagnostica_semestres'] is not None:
            v2[r['codcarpr'],r['plan_umas'],r['sede_umas']].add((r['tipo_plan'],float(r['duracion_diagnostica_semestres'])))
    listing=verify('data/cierre_d2/20261016/fuentes/Listado_Planes_estudio_Sedes RE+CO.xlsx','fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049')
    wb=openpyxl.load_workbook(listing,read_only=True,data_only=True)
    it=wb['BBDD Bruta'].values
    h=next(it); levels=C.defaultdict(set)
    for values in it:
        r=dict(zip(h,values))
        if r['CODRAMO'] and txt(r['NIVEL']).isdigit():
            levels[txt(r['CODPESTUD'])].add(int(r['NIVEL']))
    wb.close()
    verify('docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md')
    prof_umas=load('outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json')['perfiles']
    regimes=C.defaultdict(set)
    for p in prof_umas:
        for z in p['PROMEDIOS']:
            regimes[p['codcarpr'],p['CODPESTUD'],p['sede_umas'],z['jornada']].add(z['regimen'])
    def regime(c,plan,s,j,y):
        rs=paso1_reg.get((plan,y)) or regimes[c,plan,SITES.get(s),{'1':'D','2':'V','4':'O'}.get(j)]
        return next(iter(rs)) if len(rs)==1 else 'E'
    @lru_cache(None)
    def profile(c,pl,s,j,y):
        site=SITES.get(s); reg=regime(c,pl,s,j,y);n=max(levels[pl],default=None)
        exact,duration,error=semestres(n,reg)
        fixed=v2[c,pl,site]
        typ=None
        method='NIVELES_LISTADO+OFERTA_SIES_AÑO'
        if len(fixed)==1:
            typ,duration=next(iter(fixed));method='CATALOGO_V2';error=''
        elif len(fixed)>1:error='PERFILES_V2_MULTIPLES'
        options={}
        for fam in sorted(families[c,pl,s,j]):
            for r in offers[y,fam]:
                options[r['codigo_unico']]={'tipo':TYPES.get(r['tipo_plan_sies'],'E'),'total':r['duracion_total'],'modalidad':r['modalidad'],'vigencia':r['vigencia']}
        matches=[code for code,o in options.items() if o['tipo']!='E' and o['total'] and float(o['total'])==duration and (not typ or typ==o['tipo']) and (method=='CATALOGO_V2' or o['modalidad'] in MODES)]
        if not error:
            if not options:error='SIN_FAMILIA_H002_U_OFERTA_ANUAL'
            elif not matches:error='SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD'
            elif len({options[code]['tipo'] for code in matches})!=1:error='TIPOS_DISTINTOS_MISMA_DURACION'
        return {'carrera':c,'plan':pl,'sede':s,'jornada':j,'anio':y,'nivel_maximo':n,'regimen':reg,'semestres_exactos':str(exact) if exact is not None else None,'semestres_convertidos':semestres(n,reg)[1],'duracion_control':duration,'origen':method,'opciones':options,'compatibles':sorted(matches),'tipo':typ or (options[matches[0]]['tipo'] if matches and not error else 'E'),'motivo_E':error}
    # D6 se habilita únicamente con evidencia de régimen de actividad por plan/año.
    reol=set(z['plan'] for z in e['listado_UMAS'])
    considered={}
    def register(key):
        considered[key]=profile(*key)
        return considered[key]
    def resolve(b):
        if b['nivel_asignacion']!='E':return b
        r=obs[b['observacion_id']];y=b['anio'];native=b['periodo'] in ('4','5')
        key=(b['carrera'],b['plan'],b['sede'],b['jornada'],y)
        p=register(key)
        def pending(reason):return b|{'motivo':reason,'motivo_h010b':b['motivo']}
        if native and (b['plan'] not in reol or paso1_reg.get((b['plan'],y))!={'BIMESTRAL'}):
            return pending('PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO')
        if not native and b['motivo'] not in ('TIPO_DURACION_PLAN_E','SIN_T1_POSTERIOR_CON_ANTECEDENTE_PREVIO'):
            return b
        if p['motivo_E']:return pending(p['motivo_E'])
        aa=t1[exp(r)]
        later=sorted(a for a in aa if a>y)
        earlier=sorted(a for a in aa if a<y)
        source=None
        if y in aa:source=y;via='HERENCIA_T1_MISMO_AÑO'
        elif later:source=later[0];via='PRIMER_T1_POSTERIOR'
        elif earlier:source=earlier[-1];via='ARRASTRE_ULTIMO_T1'
        if source is not None:
            items=aa[source]
            if len(items)!=1:return pending('T1_MULTIPLE')
            code,dims=next(iter(items))
            if dims!=dim(r):return pending('T1_DIMENSION_DISTINTA')
            if code not in p['compatibles']:return pending('T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO')
            if via=='PRIMER_T1_POSTERIOR' and (register((*key[:4],source))['motivo_E'] or code not in register((*key[:4],source))['compatibles']):
                return pending('T1_POSTERIOR_SIN_PERFIL_COMPATIBLE_EN_ORIGEN')
        else:
            changed=b.get('motivo_h010') in {'CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE','CAMBIO_SEDE_JORNADA_ANTES_T1'}
            options={code:{p['opciones'][code]['vigencia']} for code in p['compatibles'] if p['opciones'][code]['vigencia']!='Sin estudiantes nuevos ni antiguos'}
            code,reason=escoger(options,exige_vigente=y==2026 or not changed)
            if not code:return pending(reason)
            via='INGRESO_2026_NO_INFORMADO' if y==2026 else 'CAMBIO_PLAN_SEDE_CATALOGO_D3' if changed else 'NUNCA_INFORMADO'
        return b|{'nivel_asignacion':via,'codigo_candidato':code,'año_T1_fuente':source,'desfase':source-y if source is not None else None,'clase':'D/C','regla':'H011','motivo_h010b':b['motivo'],'motivo':'PERFIL_ANUAL_COMPATIBLE','via_h011':'D6' if native else 'D4' if via=='ARRASTRE_ULTIMO_T1' else 'D5','perfil_h011':key,'evidencia':['Oferta anual y catálogo H011',via]}
    after=[resolve(b) for b in before]
    byid={z['observacion_id']:z for z in after}
    periods=load(OLD/'PERIODOS45_H010B.json')['historicos_por_carrera_plan']
    groups={'historico':[(a,b) for a,b in zip(before,after) if a['observacion_id'] in historical],'posiciones99':[(a,byid[a['observacion_id']]) for a in pos]}
    dump(PRIVATE/'ASIGNACIONES_H011_PRIVADAS.json',after)
    catalog=list(considered[key] for key in sorted(considered))
    dump(CAT/'TIPO_PLAN_v3_CANDIDATO.json',{'estado':'CANDIDATO_NO_ACTIVO','perfiles':catalog})
    result={}
    for name,pairs in groups.items():
        prev=[a for a,b in pairs];post=[b for a,b in pairs]
        result[name]={'total':len(post),'antes':aggregate(prev,['nivel_asignacion']),'despues':aggregate(post,['nivel_asignacion']),'altas_por_via':aggregate([b for b in post if b.get('regla')=='H011'],['via_h011','nivel_asignacion']),'residual':aggregate([b for b in post if b['nivel_asignacion']=='E'],['motivo'])}
    dump(OUT/'COBERTURA_H011.json',result)
    dump(OUT/'RESIDUAL_H011.json',aggregate([b for a,b in groups['historico'] if b['nivel_asignacion']=='E'],['anio','periodo','carrera','plan','sede','jornada','motivo']))
    assert len(historical)==3049 and len(pos)==99 and all(a==b for a,b in zip(before,after) if a['nivel_asignacion']!='E')
    for a,b in zip(before,after):
        if b.get('regla')=='H011' and b['nivel_asignacion']!='E':
            p=considered[tuple(b['perfil_h011'])]
            assert not p['motivo_E'] and b['codigo_candidato'] in p['compatibles']
    assert sum(r['n'] for r in periods if r['REGIMEN_FUENTE']!='BIMESTRAL')==6
    assert all(byid[a['observacion_id']]['nivel_asignacion']=='E' for a,b in groups['historico'] if a['periodo'] in ('4','5') and a['plan'] not in reol)
    assert all(sha(p)==h for p,h in hashes.items())
    dump(OUT/'FUENTES_H011.json',hashes)
    print(result)

if __name__=='__main__':main()

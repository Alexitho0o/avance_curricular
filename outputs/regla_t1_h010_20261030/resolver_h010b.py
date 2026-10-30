"""D1–D3 sobre residuales congelados de H010. Ninguna asignación previa se recalcula.
Uso: python resolver_h010b.py --repo R --privado P [--salida O]
Identidades y evidencia granular permanecen sólo en P; no abre Excel.
"""
import argparse, collections as C, copy, json, os, re, sqlite3, sys
from pathlib import Path
from construir import txt, sha, dump, aggregate, ctx, exp, dim, profile_check

def escoger(opciones, exige_vigente=False):
    """Opciones ya filtradas por tipo/duración y presencia anual; no usa nombres."""
    activas=[c for c,v in opciones.items() if v == {'Vigente con estudiantes nuevos'}]
    if exige_vigente: return (activas[0], 'VIGENCIA_1_UNICA') if len(activas)==1 else ('','SIN_VIGENCIA_1_COMPATIBLE' if not activas else 'VARIAS_VIGENCIA_1_COMPATIBLES')
    if len(opciones)==1:return next(iter(opciones)),'COMPATIBLE_UNICO'
    if len(activas)==1:return activas[0],'DESEMPATE_VIGENCIA_1'
    return '', 'SIN_CODIGO_ANUAL_COMPATIBLE' if not opciones else 'AMBIGUEDAD_ANUAL_PERSISTENTE'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--privado',type=Path,required=True);ap.add_argument('--salida',type=Path);a=ap.parse_args();R=a.repo.resolve();P=a.privado.resolve();O=a.salida or R/'outputs/regla_t1_h010_20261030';O.mkdir(parents=True,exist_ok=True);os.umask(0o077)
    assert not P.is_relative_to(R)
    sources={}
    def load(p,expected=None):
        p=Path(p);p=p if p.is_absolute() else R/p;h=sha(p)
        if expected:assert h==expected,p.name
        sources[str(p)]={'sha256':h};return json.loads(p.read_text())
    active=load('data/diccionario_sies_seguimiento/activo.json');desc=load(active['descriptor'],active['sha256']);base=Path(desc['base_privada']['ruta']);assert sha(base)==desc['base_privada']['sha256'];sources[str(base)]={'sha256':sha(base)}
    db=sqlite3.connect(base.as_uri()+'?mode=ro',uri=True)
    rows=[json.loads(t[0]) for t in db.execute('select payload from observaciones order by id')];obs={r['observacion_id']:r for r in rows}
    before=load(P/'ASIGNACIONES_PRIVADAS.json');p99old=load(P/'POSICIONES_99_PRIVADAS.json')
    # La lista histórica se recupera de v7, sin volver a clasificarla.
    d7=load('data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json');b7=Path(d7['base_privada']['ruta']);assert sha(b7)==d7['base_privada']['sha256'];sources[str(b7)]={'sha256':sha(b7)}
    c7=sqlite3.connect(b7.as_uri()+'?mode=ro',uri=True);hist={z['observacion_id'] for t in c7.execute('select payload from observaciones') if not (z:=json.loads(t[0])).get('codigo_interno_adoptado')};c7.close();assert len(hist)==3049
    profiles=load('data/paridad_codigo_sies/regla_operativa_mu_v2/TIPO_PLAN_POR_PLAN_UMAS.json')['filas'];maestro=load('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json');parity=load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas'];offers=C.defaultdict(list)
    for o in maestro['oferta_anual']:offers[int(o['anio']),o['codigo_unico']].append(o)
    profile_index=C.defaultdict(list)
    for p in profiles:profile_index[p['codcarpr'],p['plan_umas'],p['sede_umas']].append(p)
    def prof(r):return profile_index[r['carrera'],r['plan'],{'2':'RE','3':'CO','4':'PTG'}.get(txt(r.get('sede_dimension')))]
    def check(r,code,y):return profile_check(prof(r),offers[y,code])
    anchors=C.defaultdict(list);annual=C.defaultdict(set);mu=C.defaultdict(list)
    for person,y,code,payload in db.execute('select persona,anio,codigo,payload from mu_anual'):mu[person,int(y)].append(json.loads(payload))
    for r in rows:
        y=int(r['ano']);code=r.get('codigo_documental_atribuible')
        if code and any(m['codigo']==code for m in mu[r['persona'],y]):
            annual[dim(r),r['plan'],y].add(code)
            if txt(r['periodo'])=='1':anchors[exp(r)].append({'anio':y,'codigo':code,'dimensiones':dim(r),'origen':'v20_documental_T1'})
    rule=load('data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json');ref=rule['fuentes']['enlaces_privados_H002g'];links=load(ref['ruta'],ref['sha256']);sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import rut_normalizado
    for z in links:
        if not z['seleccion'] or z['plan_respaldo']!='ANUAL' or z['identidad'][0]!='R':continue
        ident=z['identidad'];person=rut_normalizado(txt(ident[1])+'-'+txt(ident[2]));sel=z['seleccion'];year=z['anio'];code=z['codigo_sies'];ss={'RE':'2','CO':'3','PTG':'4'}.get(txt(sel[2]));jj={'D':'1','V':'2','O':'4'}.get(txt(sel[3]))
        if ss is None or jj is None or not any(m['codigo']==code for m in mu[person,year]):continue
        dims=txt(sel[1]),ss,jj;e=person,txt(sel[0]),z['plan'];anchors[e].append({'anio':year,'codigo':code,'dimensiones':dims,'origen':'H002g_ANUAL','fila_fuente_mu':z['fila_fuente_mu']});annual[dims,z['plan'],year].add(code)
    def candidates(r):
        y=int(r['ano']);codes=set(annual[dim(r),r['plan'],y]);families=set()
        for p in parity:
            if r['carrera'] in p['codcarpr'] and r['plan'] in p['plan_umas'] and txt(p['cod_sede'])==txt(r.get('sede_dimension')) and txt(p['cod_jornada'])==txt(r.get('jornada_sies')):families.add(p['codigo_unico'].rsplit('V',1)[0])
        families.update(c.rsplit('V',1)[0] for c in codes)
        codes.update(code for yy,code in offers if yy==y and code.rsplit('V',1)[0] in families)
        good={};rejected={}
        for code in sorted(codes):
            ok,why=check(r,code,y);vig={x['vigencia'] for x in offers[y,code]}
            if ok and vig and 'Sin estudiantes nuevos ni antiguos' not in vig:good[code]=vig
            else:rejected[code]=why if not ok else 'VIGENCIA_SIN_ESTUDIANTES'
        return good,rejected
    eligible={'T1_SIN_LINEA_ATRIBUIDA_AL_EXPEDIENTE','MU2027_SIN_FILA_ANTIGUO_INEQUIVOCA_NO_COHORTE_NUEVA_2027','PERSONA_EN_MU_SIN_T1_MISMO_EXPEDIENTE_PLAN_ACREDITADO','CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE','CAMBIO_SEDE_JORNADA_ANTES_T1','SIN_MU_LOCALIZADA_Y_SIN_CATALOGO_ANUAL_UNICO','TIPO_DURACION_PLAN_E'}
    def classify(z,simulate_period=False):
        r=obs[z['observacion_id']];y=int(r['ano']);out=copy.deepcopy(z)
        if z['nivel_asignacion']!='E':return out
        if txt(r['periodo']) in {'4','5'} and not simulate_period:return out
        if z['motivo'] not in eligible and not simulate_period:return out
        # Tipo E encaja en D1 sólo como contexto sin T1; los controles permanecen obligatorios.
        out.update(regla='H010B_D_Alexi_20261030',motivo_h010=z['motivo'])
        if simulate_period:
            same=[x for x in anchors[exp(r)] if x['anio']==y and x['dimensiones']==dim(r)]
            samecodes={x['codigo'] for x in same}
            if len(samecodes)==1 and check(r,next(iter(samecodes)),y)[0]:
                out.update(nivel_asignacion='HERENCIA_T1_MISMO_ANIO_SIMULADA',codigo_candidato=next(iter(samecodes)),clase='C/E_NO_APLICADO',motivo='HIPOTESIS_PERIODO_MISMO_ANIO_CON_T1');return out

        later=[x for x in anchors[exp(r)] if x['anio']>y];first=min((x['anio'] for x in later),default=None);firstrows=[x for x in later if x['anio']==first];codes={x['codigo'] for x in firstrows}
        is2026=y==2026
        if firstrows and not is2026 and z['motivo'] not in {'CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE','CAMBIO_SEDE_JORNADA_ANTES_T1'}:
            if len(codes)==1 and all(x['dimensiones']==dim(r) for x in firstrows):
                code=next(iter(codes));ok,why=check(r,code,first);okyear,whyyear=check(r,code,y)
                if ok and okyear:
                    out.update(nivel_asignacion='PRIMER_T1_POSTERIOR',codigo_candidato=code,año_T1_fuente=first,desfase=first-y,clase='D/C',motivo='D1_PRIMER_T1_POSTERIOR_MISMO_EXPEDIENTE_PLAN',evidencia=firstrows,control_tipo_duracion=True,control_oferta_anio=True);return out
                out.update(motivo=why if not ok else 'CONTEXTO_'+whyyear,evidencia=firstrows);return out
            # Primer T1 existente pero no unívoco: no inventar que nunca se informó.
            out.update(motivo='PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS',evidencia=firstrows);return out
        if not is2026 and not firstrows and anchors[exp(r)] and z['motivo'] not in {'CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE','CAMBIO_SEDE_JORNADA_ANTES_T1'}:
            out.update(motivo='SIN_T1_POSTERIOR_CON_ANTECEDENTE_PREVIO',evidencia=['Existe T1 previo; no corresponde rotular NUNCA_INFORMADO. Falta decisión específica para arrastre anterior.']);return out
        good,rejected=candidates(r);code,why=escoger(good,exige_vigente=is2026 or z['motivo'] not in {'CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE','CAMBIO_SEDE_JORNADA_ANTES_T1'})
        out['opciones_compatibles']=sorted(good);out['rechazos_control']=rejected
        if code:
            level='INGRESO_2026_NO_INFORMADO' if is2026 else 'CAMBIO_PLAN_SEDE_CATALOGO_D3' if z['motivo'] in {'CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE','CAMBIO_SEDE_JORNADA_ANTES_T1'} else 'NUNCA_INFORMADO'
            out.update(nivel_asignacion=level,codigo_candidato=code,año_T1_fuente=None,desfase=None,clase='D/C',motivo='D2_'+why if is2026 else 'D1_D3_'+why,evidencia=['H002 familia del plan + perfil v2 + oferta del año; no atribución documental'],control_tipo_duracion=True,control_oferta_anio=True)
            if level=='NUNCA_INFORMADO':out['marcas'].append('NUNCA_EN_MISMO_EXPEDIENTE_PLAN_DENTRO_FUENTES_DISPONIBLES_NO_INEXISTENCIA_SIES')
        else:
            ok,_=profile_check(prof(r),[])
            ps={(p['tipo_codigo'],p['duracion_diagnostica_semestres']) for p in prof(r)}
            out.update(motivo='TIPO_DURACION_PLAN_E' if not ps or any(t not in {'1','3'} or d is None for t,d in ps) else why)
        return out
    results=[classify(z) for z in before];idx={z['observacion_id']:z for z in results};new=[z for b,z in zip(before,results) if b['nivel_asignacion']=='E' and z['nivel_asignacion']!='E']
    groups={'v7_3049':([b for b in before if b['observacion_id'] in hist],[z for z in results if z['observacion_id'] in hist]),'V24_99_posiciones':(p99old,[idx[z['observacion_id']] for z in p99old]),'v20_completa':(before,results)}
    coverage={k:{'total':len(aa),'antes':aggregate(bb,['nivel_asignacion']),'despues':aggregate(aa,['nivel_asignacion']),'residual_E':aggregate([z for z in aa if z['nivel_asignacion']=='E'],['motivo']),'nuevas':sum(b['nivel_asignacion']=='E' and z['nivel_asignacion']!='E' for b,z in zip(bb,aa))} for k,(bb,aa) in groups.items()}
    dump(P/'ASIGNACIONES_H010B_PRIVADAS.json',results);dump(P/'POSICIONES_99_H010B_PRIVADAS.json',groups['V24_99_posiciones'][1]);dump(O/'COBERTURA_H010B.json',coverage)
    requirements={'PERIODO_NATIVO_4_5_NO_HOMOLOGADO':'Calendario/definición oficial UMAS por régimen y año, y decisión D de homologación; no asignar','TIPO_DURACION_PLAN_E':'Perfil gobernado del plan con tipo y duración inequívocos','SIN_VIGENCIA_1_COMPATIBLE':'Oferta anual con versión vigente compatible o decisión explícita para ausencia de admisión','VARIAS_VIGENCIA_1_COMPATIBLES':'Evidencia que distinga versiones con igual perfil y vigencia','SIN_CODIGO_ANUAL_COMPATIBLE':'Correspondencia anual de familia/plan y tipo/duración compatible','AMBIGUEDAD_ANUAL_PERSISTENTE':'Plan/versión acreditados para el año; el nombre no basta','PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS':'T1 inequívoco del expediente/plan y evidencia de sede/jornada','CONTEXTO_OFERTA_ANIO_T1_NO_LOCALIZADA':'Código del T1 posterior presente en oferta del contexto o decisión que autorice excepción temporal','CONTRADICCION_TIPO_O_DURACION':'Evidencia que resuelva contradicción de tipo/duración; no elegir por nombre'}
    residual=[z for z in results if z['nivel_asignacion']=='E'];reasons={z['motivo'] for z in residual};requirements.update({k:requirements.get(k,'Evidencia anual que satisfaga el control '+k+'; no asignación automática') for k in reasons})
    dump(O/'RESIDUAL_H010B.json',{'clase':'E','unidad':'observaciones nativas; no personas','casos':aggregate(residual,['anio','periodo','carrera','plan','sede','jornada','motivo']),'requisitos':{k:requirements[k] for k in sorted(reasons)}})
    simulated=[classify(z,True) for z in before if z['observacion_id'] in hist and z['periodo'] in {'4','5'}];dump(O/'EFECTO_HIPOTETICO_PERIODOS45.json',{'clase':'C/E_NO_APLICADO','hipotesis':'Si Alexi acreditara y autorizara tratarlos como actividad del mismo año, se simula T1 del mismo expediente/plan/año y, en su ausencia, D1–D3. No demuestra qué significan 4/5 ni los homologa.','total':len(simulated),'por_nivel':aggregate(simulated,['nivel_asignacion']),'por_motivo':aggregate(simulated,['nivel_asignacion','motivo'])})
    candidate=P/'DICCIONARIO_V21_H010B_CANDIDATA.sqlite'
    if candidate.exists():candidate.unlink() # sólo derivado propio; nunca la base H010 ni v20
    nc=sqlite3.connect(candidate);db.backup(nc);nc.execute('create table asignaciones_h010 (observacion_id integer primary key,payload text not null)');nc.executemany('insert into asignaciones_h010 values (?,?)',[(z['observacion_id'],json.dumps(z,ensure_ascii=False,sort_keys=True)) for z in results]);nc.commit()
    intact=all(nc.execute('select * from '+table+' order by rowid').fetchall()==db.execute('select * from '+table+' order by rowid').fetchall() for table in ['observaciones','mu_anual']);assert intact;nc.close();db.close()
    checks={'asignaciones_previas_intactas':all(b==z for b,z in zip(before,results) if b['nivel_asignacion']!='E'),'periodos45_no_asignados':all(b==z for b,z in zip(before,results) if b['periodo'] in {'4','5'}),'v20_tablas_intactas':intact,'3049':len(groups['v7_3049'][1])==3049,'99':len(groups['V24_99_posiciones'][1])==99,'nuevas_no_documentales':all(z['nivel_asignacion']!='DOCUMENTAL_T1' for z in new),'controles_nuevas':all(z['control_oferta_anio'] and z['control_tipo_duracion'] and check(obs[z['observacion_id']],z['codigo_candidato'],z['anio'])[0] for z in new),'2026_vigencia1':all({v['vigencia'] for v in offers[2026,z['codigo_candidato']]}=={'Vigente con estudiantes nuevos'} for z in new if z['anio']==2026),'fuentes_intactas':all(sha(p)==v['sha256'] for p,v in sources.items())}
    assert all(checks.values());dump(O/'QA_RESOLUCION_H010B.json',{'estado':'PASS','controles':checks,'asignaciones_nuevas_total_v20':len(new),'base_privada_sha256':sha(candidate),'overlay_sha256':sha(P/'ASIGNACIONES_H010B_PRIVADAS.json'),'tasas_delta_pp':{'R01_R04':0.0,'R19':0.0},'limite':'Conservación; no integración ni recálculo de indicadores.'});dump(O/'FUENTES_H010B.json',{'fuentes':[{'ruta':p,**v} for p,v in sorted(sources.items())]});print(json.dumps({k:{'nuevas':v['nuevas'],'residual':sum(x['n'] for x in v['residual_E'])} for k,v in coverage.items()}))
if __name__=='__main__':main()

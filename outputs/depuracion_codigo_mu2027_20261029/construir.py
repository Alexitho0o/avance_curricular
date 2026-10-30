#!/usr/bin/env python3
"""H002l: lista v2 y cierre documental; fuentes y H002 permanecen intactos."""
import argparse,csv,hashlib,io,json,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
REL=str(OUT.relative_to(ROOT));BASE='82cb49c8b1136214a989676d914766d829e4c4dc'
RULE='data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027'
MILE='manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027'
sys.path.insert(0,str(ROOT))
from common.codigo_sies_mu2027 import cargar_contexto,resolver

def js(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def old(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def tab(rows,keys):return '\n'.join(['| '+' | '.join(keys)+' |','|'+'---|'*len(keys)]+['| '+' | '.join(str(r.get(k,'')) for k in keys)+' |' for r in rows])
def construir():
    plans,offer,anc,pending=cargar_contexto();built={}
    def put(p,x):built[p]=x if isinstance(x,bytes) else x.encode() if isinstance(x,str) else js(x)
    sources={}
    paths=['outputs/activacion_codigo_mu2027_20261029/SIMULACION_CATALOGO_NUEVOS_2027.json','outputs/activacion_codigo_mu2027_20261029/LISTA_REVISION_MANUAL_MU2027.json',
        'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json','data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.csv']
    for p in paths:
        raw=(ROOT/p).read_bytes();assert raw==old(p),'Antecedente alterado: '+p
        sources[p]={'sha256':sha(raw),'commit':BASE}
    baseline=json.loads(old(paths[1]));previous_new=json.loads(old(paths[0]))
    counts=Counter();manual=Counter();info=Counter();private_manual=[];private_info=[];prior1046=0
    for ref,r in sorted(anc.items()):
        result=resolver({'anio':2027,'via_solicitada':'ANTIGUO','fila_mu2026':ref},plans,offer,anc,pending)
        counts[result['motivo']]+=1
        row={'familia':r['familia'],'codcarpr':r['codcarpr'],'plan':r['plan']}
        personal={**row,'fila_mu2026':ref,'identidad':r['identidad'],'expediente':r['expediente'],'resultado':result}
        if result['via']=='REVISION_MANUAL':
            manual[r['familia'],r['codcarpr'],r['plan'],result['motivo']]+=1;private_manual.append(personal)
        else:assert result['codigo']==r['real']
        marks=result.get('marcas_informativas',[])
        if marks:
            info[r['familia'],r['codcarpr'],r['plan'],' + '.join(marks)]+=1;private_info.append(personal)
        prior1046+=plans.get((r['codcarpr'],r['plan'],r['sede_umas']),'E') not in {'1','3'}
    assert prior1046==baseline['MU2026']['manual_por_motivo']['ANTIGUO_TIPO_E']==1046
    def aggregate(c):return [{'familia':f,'codcarpr':car,'plan':p,'motivo':m,'matriculas_potenciales':n} for (f,car,p,m),n in sorted(c.items())]
    transitions=Counter();new=[]
    for r in previous_new:
        f={'anio':2027,'cohorte':2027,'via_solicitada':'NUEVO','familia':r['familia'],'codcarpr':r['codcarpr'],'plan_umas':r['plan'],'sede_umas':r['sede_umas']}
        ans=resolver(f,plans,offer,anc,pending);transitions[r['motivo'],ans['motivo']]+=1
        new.append({k:r[k] for k in ['familia','codcarpr','plan','sede_umas','unidad']}|{'motivo_H002k':r['motivo'],**ans})
    real=[r for r in new if r['via']=='REVISION_MANUAL'];informative=[r for r in new if r['via']=='INFORMATIVO']
    old_reasons=['ANTIGUO_1_CODIGO_O_FILA_NO_RESUELTA','ANTIGUO_2_CODIGO_SIN_OFERTA_2027','ANTIGUO_3_VIGENCIA_3']
    totals={'antiguos':{'unidad':'MATRICULAS_POTENCIALES_MU2026','total':len(anc),'revision_H002k':1046,
        'revision_H002l':sum(manual.values()),'por_motivo':{m:counts[m] for m in old_reasons},
        'conservan_codigo':len(anc)-sum(manual.values()),'tipo_E_informativo':sum(info.values())},
        'nuevos':{'unidad':'OPCIONES_PLAN_FAMILIA_CATALOGO_NO_PERSONAS','total':len(new),'asignacion':sum(r['via']=='NUEVO' for r in new),'revision_real':len(real),'informativos':len(informative),
            'revision_por_motivo':dict(Counter(r['motivo'] for r in real)),
            'de_108':{'PLAN_SIN_ADMISION_2027':transitions['SIN_VERSION_VIGENTE_PARA_TIPO','PLAN_SIN_ADMISION_2027'],
                      'REVISION_REAL':transitions['SIN_VERSION_VIGENTE_PARA_TIPO','REVISION_REAL_TIPO_SIN_VERSION_EN_FAMILIA_CON_ADMISION']},
            'de_40_tipo_E':{'familia_admite':transitions['NUEVO_TIPO_E','NUEVO_TIPO_E_CON_ADMISION'],'familia_no_admite':transitions['NUEVO_TIPO_E','PLAN_SIN_ADMISION_2027']}},
        'codigos_sin_plan':{'unidad':'CODIGO_CATALOGO_NO_PERSONAS','total':len(pending),'solapamiento':'El código sin plan de las opciones nuevas está incluido en los 37; no sumar unidades.'}}
    assert sum(totals['nuevos']['de_108'].values())==108 and sum(totals['nuevos']['de_40_tipo_E'].values())==40
    assert totals['nuevos']['asignacion']+len(real)+len(informative)==len(previous_new)==223
    review={'hito':'H002l','fecha':'2026-10-29','clase':'D/C/E','no_es_carga':True,'totales':totals,'antiguos':aggregate(manual),'nuevos':real,
            'codigos_sin_plan':baseline['codigos_sin_plan']['filas'],'fuentes':sources,'criterio':'Familia sin ninguna VIGENCIA 1: informativo. Familia con admisión pero sin versión del tipo: revisión real.'}
    put(REL+'/LISTA_REVISION_MANUAL_MU2027_v2.json',review)
    put(REL+'/LISTA_REVISION_MANUAL_MU2027_v2.md','# H002l · Revisión manual MU 2027 v2\n\nD · Alexi, 29-10-2026. Universo potencial; no carga ni matrícula 2027 observada.\nLas matrículas, opciones de catálogo y códigos son unidades distintas.\n\n## Totales\n\n```json\n'+json.dumps(totals,ensure_ascii=False,indent=2)+'\n```\n\n## Antiguos: sólo tres motivos reales\n\n'+tab(aggregate(manual),['familia','codcarpr','plan','motivo','matriculas_potenciales'])+'\n\n## Nuevos: revisión real\n\n'+tab(real,['familia','codcarpr','plan','motivo'])+'\n\n## Códigos sin plan (37; no sumar a opciones)\n\n'+tab(review['codigos_sin_plan'],['codigo_unico','nombre_carrera','motivo'])+'\n')
    put(REL+'/MARCAS_INFORMATIVAS_MU2027.json',{'clase':'C/D','antiguos':aggregate(info),'nuevos':informative,'nota':'Marcas informativas, no tareas manuales ni autorización de carga. Los motivos tipo E y plan ausente se superponen; cada matrícula se cuenta una vez.'})
    put(REL+'/MARCAS_INFORMATIVAS_MU2027.md','# H002l · Información sin revisión manual\n\n## Antiguos: tipo/plan no intervienen en conservar código\n\n'+tab(aggregate(info),['familia','codcarpr','plan','motivo','matriculas_potenciales'])+'\n\n## Nuevos: familia sin admisión 2027\n\n'+tab(informative,['familia','codcarpr','plan','motivo','tipo_E'])+'\n')
    put(REL+'/SIMULACION_CATALOGO_NUEVOS_2027_v2.json',new)
    rule=json.loads(old(RULE+'.json'))
    rule.update(revision='H002l',fecha_correccion='2026-10-29',decision_correccion='D · Alexi, 29-10-2026, H002l: antiguo no depende del tipo; revisión sólo por código/fila, ausencia en oferta o VIGENCIA 3.',
        antecedente={'commit':BASE,'ruta':RULE+'.json','sha256':sha(old(RULE+'.json'))})
    rule['reglas']['ANTIGUO']='Conserva código MU 2026 sin usar tipo de plan. Revisión sólo (1) código/fila no resuelta; (2) código ausente en oferta 2027; (3) VIGENCIA 3. Tipo E/plan ausente son informativos.'
    rule['reglas']['REVISION_MANUAL']=['Antiguo: sólo motivos 1/2/3 anteriores.','Nuevo: familia admite pero tipo no determinable o sin versión compatible; varias versiones vigentes del mismo tipo; códigos sin plan.','OTRO: revisión fuera de la vía ANTIGUO; no convertir cambios de carrera ni reingresos sin evidencia en antiguos.']
    rule['reglas']['PLAN_SIN_ADMISION_2027']='Si no hay ninguna VIGENCIA 1 en la familia, informativo (incluye tipo E); no asigna código para nuevos. Si la familia admite pero no el tipo, REVISION_REAL.'
    rule['lista_revision_vigente']=REL+'/LISTA_REVISION_MANUAL_MU2027_v2.json'
    rule['marcas_informativas']=REL+'/MARCAS_INFORMATIVAS_MU2027.json'
    rule['contrato_entrada']='ANTIGUO requiere referencia inequívoca a fila MU 2026. Su clasificación está acreditada por el llamador. NUEVO exige cohorte 2027; OTRO queda separado. La simulación no acredita continuidad efectiva 2027.'
    put(RULE+'.json',rule)
    md=old(RULE+'.md').decode();a=md.index('- **ANTIGUO**:');b=md.index('\n## Límites',a)
    md=md[:a]+'\n'.join('- **'+k+'**: '+(v if isinstance(v,str) else '; '.join(v)) for k,v in rule['reglas'].items())+'\n'+md[b:]
    md=md.replace('Antiguo: referencia exacta `fila_mu2026` y `cambio_carrera_o_plan=False` explícito; sin certeza pasa a revisión.','Antiguo: referencia exacta `fila_mu2026`; tipo E y plan ausente sólo informativos. La clasificación previa ANTIGUO debe estar acreditada por el llamador.')
    md+='\n## Corrección H002l · D, Alexi, 29-10-2026\n\nSustituye el bloqueo de tipo E de H002k. VIGENCIA 2 permite conservar antiguos; VIGENCIA 3 bloquea.\nLa regla no revisa tipo de plan para conservar el código anterior. Las marcas no son decisiones pendientes.\nLista vigente: `'+REL+'/LISTA_REVISION_MANUAL_MU2027_v2.json`. V1 preservada por commit y archivo original.\nNuevos: familia sin admisión es informativa; familia con admisión y sin tipo compatible requiere revisión.\nLa oferta V06 sigue preparada C; no se genera carga y no se alteran fuentes ni H002.\n'
    put(RULE+'.md',md)
    log=subprocess.check_output(['git','log','--reverse','--format=%H%x09%s','7807542..'+BASE],cwd=ROOT,text=True)
    commits=[{'commit':line.split('\t',1)[0],'descripcion':line.split('\t',1)[1]} for line in log.splitlines() if line.split('\t',1)[1].startswith('H002')]
    commits.append({'commit':'COMMIT_QUE_INTRODUCE_CIERRE_H002L','descripcion':'H002l depura revisión MU 2027 y cierra H002',
        'resolver':"git log --diff-filter=A --format=%H -- manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/CIERRE_H002L.json"})
    closure={'hito':'H002','estado':'CERRADO_DOCUMENTADO_CON_PENDIENTES_OPERATIVOS_2027','clase':'D/C/E','fecha':'2026-10-29','responsable':'Alexi',
        'resuelto':{'tabla_2027':'97 códigos resueltos (53 CONTINUA + 31 VERSION_MULTIPLE_RESUELTA + 13 APROBADA_D); 0 VERSION_MULTIPLE_E. Tabla inalterada.',
            'regla':'ACTIVA interna MU 2027, corrección H002l; no exportador PES.',
            'historico_2007_2021':'Cerrado E con causa por decisión D H002i; SIES cuadra con publicación, sin vínculo a planes/notas UMAS. No cuadrar con foto actual Datos Alumnos.',
            'paridad_2022_2026':'Trabajo documentado H002f–j: anclas 2022/2024/2025; 2023 parcial y 2026 contraste. No implica identidad completa de planes ni explicación de la brecha 226; antecedentes y discrepancias conservados.'},
        'pendientes':{'37_codigos':'Cerrar con MU 2027 por código y total; hasta entonces sin plan E. No pedir otro listado.',
            'revision_manual':totals,'oferta':'Reemplazar V06 preparada C por carga aceptada con hash antes de una carga real.'},
        'rutas':{'tabla':'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json','regla':RULE+'.json','historico':'data/paridad_codigo_sies/cierre_historico_2007_2021/README.md','paridad':'data/paridad_codigo_sies/cohorte_2007_2026_v2/','revision':REL+'/LISTA_REVISION_MANUAL_MU2027_v2.json'},
        'commits':commits,'nota_commit':'H002 inicial se publicó junto a H002b en 76830cf. El hash propio se resuelve por el commit que introduce este registro, evitando una autorreferencia imposible.'}
    put(MILE+'/CIERRE_H002L.json',closure)
    put(MILE+'/CIERRE_H002L.md','# Cierre documental H002 · H002l\n\nD · Alexi, 29-10-2026. CERRADO_DOCUMENTADO_CON_PENDIENTES_OPERATIVOS_2027.\n\n## Resuelto\n\n'+'\n'.join('- **'+k+'**: '+v for k,v in closure['resuelto'].items())+'\n\n## Pendientes y forma de cierre\n\n37 códigos: MU 2027 por código/total. Revisión depurada: '+REL+'/LISTA_REVISION_MANUAL_MU2027_v2.md. Oferta aceptada antes de carga.\nNo equivale a matrícula 2027 completa ni a una nueva conciliación histórica.\n\n## Commits H002–H002l\n\n'+tab(commits,['commit','descripcion'])+'\n\n'+closure['nota_commit']+'\n\nEl hash propio se obtiene con `'+commits[-1]['resolver']+'`.\n')
    register=json.loads(old(MILE+'/REGISTRO.json'));register.update(actualizacion='H002l',estado=closure['estado'],cierre=closure['resuelto'],pendientes=closure['pendientes'],cierre_documentado=MILE+'/CIERRE_H002L.json',QA_entrega=REL+'/QA_FINAL.json',regla_activa=RULE+'.json')
    put(MILE+'/REGISTRO.json',register)
    md=old(MILE+'/README.md').decode().replace('## Estado vigente H002k','## Antecedente H002k (corregido por H002l)')
    md+='\n## Cierre vigente H002l · 29-10-2026\n\nD · Alexi: '+closure['estado']+'. Antiguos conservan sin usar tipo de plan; sólo tres motivos de revisión.\nVéase [cierre y commits](CIERRE_H002L.md). Lista v2: '+REL+'/LISTA_REVISION_MANUAL_MU2027_v2.md.\nLa tabla 2027, V1 y antecedentes quedan intactos; 37 códigos y revisión real se cierran con evidencia MU 2027.\n'
    put(MILE+'/README.md',md)
    put(REL+'/INFORME.md','# H002l · Depuración y cierre\n\nD · Alexi, 29-10-2026. Implementación C; evidencia B/C; pendientes E.\n\n```json\n'+json.dumps(totals,ensure_ascii=False,indent=2)+'\n```\n\nLos cuatro SIN_OFERTA_2027 de H002 son antecedentes de catálogo: no hay filas MU2026 con esos códigos en el universo potencial. No se inventan matrículas para ellos.\n\nLa revisión real de nuevos mantiene las cinco familias ambiguas y los 37 códigos sin plan; estos no se suman a opciones de catálogo.\n\n## Transiciones de motivos nuevos\n\n'+tab([{'antes':a,'ahora':b,'opciones':n} for (a,b),n in sorted(transitions.items())],['antes','ahora','opciones'])+'\n\nReproducción: `python3 '+REL+'/construir.py --check`. Las salidas H002k se reproducen en su commit congelado, con su función anterior.\n')
    put(REL+'/FUENTES.json',{'entradas':sources,'regla_antecedente':{'commit':BASE,'ruta':RULE+'.json','sha256':sha(old(RULE+'.json'))},'fuentes_privadas':rule['fuentes']})
    return built,private_manual,private_info,totals

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();built,manual,info,totals=construir()
    for rel,raw in built.items():
        p=ROOT/rel
        if args.check:
            if not p.exists() or p.read_bytes()!=raw:raise ValueError('No reproducible: '+rel)
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    if not args.check:
        d=Path.home()/'.local/share/ipss/h002l_20261029';d.mkdir(exist_ok=True,mode=0o700)
        for name,rows in [('REVISION_MANUAL.json',manual),('INFORMATIVOS.json',info)]:
            p=d/name;p.write_bytes(js(rows));p.chmod(0o600)
    print(json.dumps({'estado':'PASS','salidas':len(built),'totales':totals},ensure_ascii=False))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""H002k: promoción acotada del catálogo y regla interna; sin carga PES."""
import argparse, copy, csv, hashlib, io, json, re, subprocess, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = 'outputs/activacion_codigo_mu2027_20261029'
DATA = 'data/paridad_codigo_sies/20261029'
RULE = 'data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027'
MILE = 'manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027'
BASE = 'a6c34668983eb8a067f360ecef7ff1fa18559d83'
sys.path[:0] = [str(ROOT), str(ROOT/'outputs/paridad_codigo_sies_20261029')]
import construir_paridad as anterior
from common.codigo_sies_mu2027 import resolver


def sha(raw): return hashlib.sha256(raw).hexdigest()
def js(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def read(p): return json.loads((ROOT/p).read_bytes())
def frozen(p): return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def csvbytes(rows):
    stream=io.StringIO(newline=''); fields=list(dict.fromkeys(k for r in rows for k in r))
    w=csv.DictWriter(stream,fieldnames=fields,delimiter=';',lineterminator='\n');w.writeheader()
    for r in rows: w.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else '' if v is None else v for k,v in r.items()})
    return stream.getvalue().encode()
def table(rows, keys):
    return '\n'.join(['| '+' | '.join(keys)+' |','|'+'---|'*len(keys)]+['| '+' | '.join(str(r.get(k,'')) for k in keys)+' |' for r in rows])


def aplicar(payload, decision):
    result=copy.deepcopy(payload)
    approvals={d['codigo_unico']:d for d in decision['correspondencias']}
    assert len(approvals)==2
    for row in result['filas']:
        if row['anio']!=2027 or row['codigo_unico'] not in approvals:continue
        assert row['estado']=='VERSION_MULTIPLE_E'
        d=approvals[row['codigo_unico']]
        row['antecedente_H002e_H002k']={k:row.pop(k) for k in ['indicio_H002e','decisiones_por_grupo_H002e'] if k in row}
        row['candidatos_internos_antes_H002k']=row['candidatos_internos']
        row['resoluciones_grupo_antes_H002k']=row['resoluciones_grupo']
        row['codcarpr']=[d['codcarpr']];row['plan_umas']=[d['plan_umas']]
        row['candidatos_internos']=[copy.deepcopy(c) for c in row['candidatos_internos'] if c['codcarpr']==d['codcarpr']]
        row['resoluciones_grupo']=[copy.deepcopy(g) for g in row['resoluciones_grupo'] if g['codcarpr']==d['codcarpr']]
        for g in row['resoluciones_grupo']:
            g.update(estado_paridad_2027='APROBADA_D_2027',clase_paridad_2027='D',codigo_sies_aprobado=d['codigo_unico'],planes_explicitos_aprobados=[d['plan_umas']])
            g['resolucion_nuevos_2027']={'estado':'D_APROBADA','seleccion':d['codigo_unico'],'opciones':[d['codigo_unico']],'motivo':decision['fuente']}
        for c in row['candidatos_internos']:
            c.update(estado_paridad_2027='APROBADA_D_2027',clase_paridad_2027='D',codigo_sies_aprobado_grupo=d['codigo_unico'],seleccion_grupo={'estado':'D_APROBADA','seleccion':d['codigo_unico'],'opciones':[d['codigo_unico']],'motivo':decision['fuente']})
        row.update(estado='APROBADA_D_2027',clase='D',version_para_nuevos_2027='sí',
            estado_plan_por_cohorte='D_PLAN_EXPLICITO_SIN_ATRIBUCION_PERSONAL',motivo=decision['fuente']+'; aprobación del plan explícito, sin cambio de historia informada.',
            correspondencias_aprobadas_H002k=[d],decision_H002k={'id':decision['id'],'fuente':decision['fuente'],'clase':'D'})
        row['evidencia']+=decision['evidencia']+[{'ruta':DATA+'/DECISIONES_APROBADAS_v3.json','sha256':sha((ROOT/DATA/'DECISIONES_APROBADAS_v3.json').read_bytes()),'clase':'D'}]
    changes=[(a['anio'],a['codigo_unico']) for a,b in zip(payload['filas'],result['filas']) if a!=b]
    assert set(changes)=={(2027,c) for c in approvals} and len(changes)==2
    for year in ['2026','2027']:
        count=Counter(r['estado'] for r in result['filas'] if r['anio']==int(year))
        result['conteos_por_anio_estado'][year]={k:count[k] for k in payload['conteos_por_anio_estado'][year]}
    result['hito']='H002k'
    return result,changes


def construir():
    refs=read(OUT+'/FUENTES.json')
    for k,e in refs.items():
        if sha((ROOT/e['ruta']).read_bytes())!=e['sha256']:raise ValueError('Fuente alterada: '+k)
    # Reproduce toda la base H002e sin escribir sus salidas/QA históricos.
    base_outputs,base_qa=anterior.construir(ROOT)
    baseline=json.loads(base_outputs[DATA+'/TABLA_PARIDAD_2026_2027.json'])
    assert baseline==json.loads(frozen(DATA+'/TABLA_PARIDAD_2026_2027.json'))
    decision=read(refs['decision']['ruta']);payload,changes=aplicar(baseline,decision)
    built={}
    def put(p,x):built[p]=x if isinstance(x,bytes) else x.encode() if isinstance(x,str) else js(x)
    put(DATA+'/TABLA_PARIDAD_2026_2027.json',payload);put(DATA+'/TABLA_PARIDAD_2026_2027.csv',csvbytes(payload['filas']))
    oldout='outputs/paridad_codigo_sies_20261029'
    pending_doc=json.loads(base_outputs[oldout+'/DECISIONES_PENDIENTES.json'])
    pending_doc.update(estado_vigente='H002k: ADMP/CADMP aprobados; 37 códigos y revisión manual pendientes',
        version_multiple_E_por_grupo=[],correspondencias_aprobadas_D=[r['codigo_unico'] for r in payload['filas'] if r['anio']==2027 and r['estado']=='APROBADA_D_2027'],
        cierre_codigos_nuevos='Cuando exista MU 2027, por código y total; no solicitar otro listado UMAS')
    put(oldout+'/DECISIONES_PENDIENTES.json',pending_doc)
    put(oldout+'/DECISIONES_PENDIENTES.md','# H002 · Pendientes vigentes después de H002k\n\nD · Alexi, 29-10-2026: ADMP20251/V1 y CADMP20251/V2 aprobados. No quedan VERSION_MULTIPLE_E en 2027.\n\nLos 37 códigos sin plan se cierran con la MU 2027 por código y total. La revisión manual de la regla activa se documenta en '+OUT+'/LISTA_REVISION_MANUAL_MU2027.md.\n\nSe conservan las fichas v1/v2/v3 y la decisión H002e como antecedentes; no son la lista de pendientes vigente.\n')
    groups=json.loads(base_outputs[oldout+'/RESOLUCIONES_POR_GRUPO.json'])
    changed_groups={g['grupo']:g for r in payload['filas'] if r['anio']==2027 and r.get('correspondencias_aprobadas_H002k') for g in r['resoluciones_grupo']}
    put(oldout+'/RESOLUCIONES_POR_GRUPO.json',[changed_groups.get(g['grupo'],g) for g in groups])
    counts=payload['conteos_por_anio_estado'];countrows=[{'Estado':k,'2026':counts['2026'][k],'2027':counts['2027'][k]} for k in counts['2027']]
    refs['tabla_H002']={'ruta':DATA+'/TABLA_PARIDAD_2026_2027.json','sha256':sha(built[DATA+'/TABLA_PARIDAD_2026_2027.json']),'clase':'C/D','datos_personales':False}
    metrics=read(refs['metricas']['ruta'])
    rule={'id':'CODIGO_SIES_MU2027_H002K','estado':'ACTIVA','clase':'D','proceso':'Matrícula Unificada 2027','anio_proceso':2027,
        'fecha':'2026-10-29','responsable':'Alexi','decision':decision['fuente'],'fuentes':refs,
        'reglas':{'ANTIGUO':'Conserva el código de su fila MU 2026, incluso inconsistente con tipo; tipo E y cambios pasan a revisión.',
                  'NUEVO':'Cohorte 2027: familia respaldada + plan/sede de tipo conocido + una única versión VIGENCIA 1 del mismo tipo.',
                  'REVISION_MANUAL':['Tipo E con alumnos potenciales','Familia con varias VIGENCIA 1 del mismo tipo','37 códigos sin plan','Cambio de carrera/plan, reingreso no acreditado u otra insuficiencia de evidencia'],
                  'CODIGOS_SIN_HISTORIA':'Se cierran cuando exista MU 2027 por cuadratura de código y total; no solicitar listado nuevo a UMAS.'},
        'aprobaciones':decision['correspondencias'],'metricas_prueba_H002j':{k:v for k,v in metrics.items() if k in ['por_grupo','total_evaluable','totales','por_anio','total_por_anio']},
        'metricas_nota':'Métricas históricas H002j preservadas, no una promesa de acierto 2027; los nuevos bloqueos de revisión no recalculan sus denominadores.',
        'limites':['Oferta V06 preparada C, sustituir por carga aceptada con hash y revisión antes de carga.',
                   'Decisión interna; no modifica norma, VIG, retención, v20, bases ni denominadores.',
                   'No hay exportador ni archivo de carga PES; no acredita matrícula ni elegibilidad 2027.',
                   'Sin plan anual observado no se rellena por nombre ni mayoría. Tipo por plan no se deduce de FOR_ING_ACT.'],
        'funcion':'common/codigo_sies_mu2027.py:asignar_codigo_mu2027',
        'vigencia_estado_situacion_independiente':'data/reglas_negocio/mu2027/activo.json'}
    put(RULE+'.json',rule)
    planrows=read(refs['tipo_plan']['ruta'])['filas'];plans={(p['codcarpr'],p['plan_umas'],p['sede_umas']):p['tipo_codigo'] for p in planrows}
    offer=[r for r in payload['filas'] if r['anio']==2027]
    pending=[r['codigo_unico'] for r in offer if r['estado']=='NUEVO_2027_SIN_PLAN_E'];assert len(pending)==37
    oldrows=[r for r in read(refs['prueba_privada_H002j']['ruta']) if r['anio']==2026]
    links={r['fila_fuente_mu']:r for r in read(refs['enlaces_privados_H002g']['ruta']) if r['anio']==2026}
    old={r['fila_mu']:{**r,'sede_umas':links[r['fila_mu']]['seleccion'][2] if links[r['fila_mu']]['seleccion'] else None} for r in oldrows}
    assert len(old)==4105
    detail=[]; agg=Counter();summary=Counter();five_E=0;retained=0
    five={'I162S2C1J4','I162S2C3J4','I162S2C46J4','I162S2C76J4','I162S2C77J4'}
    for ref,r in sorted(old.items()):
        ans=resolver({'anio':2027,'via_solicitada':'ANTIGUO','fila_mu2026':ref,'cambio_carrera_o_plan':False},plans,offer,old,pending)
        summary[ans['via']]+=1
        if ans['via']=='REVISION_MANUAL':
            agg[r['familia'],r['codcarpr'],r['plan'],ans['motivo']]+=1
            detail.append({'fila_fuente_mu':ref,'identidad':r['identidad'],'expediente':r['expediente'],'familia':r['familia'],'codcarpr':r['codcarpr'],'plan':r['plan'],'resultado':ans})
            if r['familia'] in five and ans['motivo']=='ANTIGUO_TIPO_E':five_E+=1
        else:
            assert ans['codigo']==r['real']
            retained+=ans['motivo']=='CONSERVA_CODIGO_INCONSISTENTE_D'
    assert five_E==252
    manual=[{'familia':f,'codcarpr':c,'plan':p,'motivo':m,'matriculas_potenciales_MU2026':n,'clase':'C/E'} for (f,c,p,m),n in sorted(agg.items())]
    # Simulación por opciones de catálogo. No hay alumnos nuevos 2027 observados.
    newinputs={}
    for row in offer:
        if row['estado'] in {'FUERA_ALCANCE','HISTORICO_SIN_MATRICULA_RECIENTE'}:continue
        fam=row['codigo_unico'].rsplit('V',1)[0]
        for g in row['resoluciones_grupo']:
            for plan in g['planes_catalogados_candidatos']:
                key=(fam,g['codcarpr'],plan,g['sede_umas'])
                newinputs[key]={'anio':2027,'cohorte':2027,'via_solicitada':'NUEVO','familia':fam,'codcarpr':g['codcarpr'],'plan_umas':plan,'sede_umas':g['sede_umas']}
    new=[]
    for key,f in sorted(newinputs.items()):
        ans=resolver(f,plans,offer,old,pending)
        new.append({'familia':key[0],'codcarpr':key[1],'plan':key[2],'sede_umas':key[3],'unidad':'OPCION_CATALOGO_NO_ALUMNO',**ans})
    new_manual=[r for r in new if r['via']=='REVISION_MANUAL']
    pendingrows=[{'codigo_unico':r['codigo_unico'],'familia':r['codigo_unico'].rsplit('V',1)[0],'nombre_carrera':r['nombre_carrera'],
                  'motivo':'CODIGO_NUEVO_SIN_PLAN','unidad':'CODIGO_CATALOGO_NO_ALUMNO','clase':'E'} for r in offer if r['codigo_unico'] in pending]
    ambiguous={}
    for row in offer:
        if row['vigencia_2027']=='1' and row['estado']!='FUERA_ALCANCE':
            key=(row['codigo_unico'].rsplit('V',1)[0],row['tipo_plan_codigo'])
            ambiguous.setdefault(key,[]).append(row['codigo_unico'])
    ambiguous_rows=[{'familia':f,'tipo_plan_codigo':t,'codigos':v,'motivo':'VARIAS_VERSIONES_VIGENTES_MISMO_TIPO'} for (f,t),v in sorted(ambiguous.items()) if len(v)>1]
    review={'alcance':'Universo potencial; no carga ni alumnos 2027 observados. Unidades separadas, no sumar entre bloques.',
        'MU2026':{'unidad':'MATRICULA','total':4105,'por_via':dict(summary),'manual_por_motivo':dict(Counter({m:sum(n for (f,c,p,reason),n in agg.items() if reason==m) for m in {k[3] for k in agg}})),
                  'cinco_familias_tipo_E':five_E,'codigos_inconsistentes_conservados':retained,'filas':manual},
        'nuevos_simulados':{'unidad':'OPCION_PLAN_FAMILIA_CATALOGO','total':len(new),'revision':len(new_manual),'motivos':dict(Counter(r['motivo'] for r in new_manual)),'filas':new_manual},
        'familias_ambiguas_catalogo':{'unidad':'FAMILIA_TIPO','total':len(ambiguous_rows),'filas':ambiguous_rows},
        'codigos_sin_plan':{'unidad':'CODIGO_CATALOGO','total':37,'filas':pendingrows},
        'advertencia':'Opciones de catálogo no equivalen a matrículas; E de plan sólo se materializa si recibe alumnos 2027. No aplicar elegibilidad ni VIG.'}
    put(OUT+'/LISTA_REVISION_MANUAL_MU2027.json',review)
    put(OUT+'/LISTA_REVISION_MANUAL_MU2027.md','# Revisión manual MU 2027 · potencial, no carga\n\n'+review['alcance']+'\n\n## Matrículas MU 2026\n\n'+table(manual,['familia','codcarpr','plan','motivo','matriculas_potenciales_MU2026'])+'\n\n## Opciones nuevas de catálogo (no personas)\n\n'+table(new_manual,['familia','codcarpr','plan','motivo'])+'\n\n## Familias con varias versiones vigentes del mismo tipo\n\n'+table(ambiguous_rows,['familia','tipo_plan_codigo','codigos','motivo'])+'\n\n## 37 códigos sin plan\n\n'+table(pendingrows,['codigo_unico','nombre_carrera','motivo'])+'\n')
    put(OUT+'/SIMULACION_CATALOGO_NUEVOS_2027.json',new)
    # Evidencia ADMP/CADMP recontada sin publicar identificadores.
    cad=Counter((r['codcarpr'],r['plan'],r['real'],r['vig']) for r in oldrows if r['familia']=='I162S2C83J4')
    evidence=[{'codcarpr':c,'plan':p,'codigo_unico':k,'VIG':v,'matriculas_MU2026':n} for (c,p,k,v),n in sorted(cad.items())]
    assert sum(n for (c,p,k,v),n in cad.items() if k=='I162S2C83J4V2' and v=='1')==9
    assert sum(n for (c,p,k,v),n in cad.items() if k=='I162S2C83J4V2' and c=='CADMP' and v=='1')==9
    review3=read(decision['evidencia'][1]['ruta'])
    control_sies=[x for c in review3['casos'] if c['codcarpr']=='CADMP' for x in c['totales_por_anio_codigo'] if x['anio']==2026 and x['codigo_unico']=='I162S2C83J4V2']
    assert len(control_sies)==1 and control_sies[0]['SIES_total']==9 and control_sies[0]['MU_VIG1']==9
    put(OUT+'/CONTROL_ADMP_CADMP.json',{'clase':'B/C','filas':evidence,'fuente':refs['prueba_privada_H002j'],'decision':refs['decision'],'control_SIES_gobernado':control_sies,'evidencia_SIES':decision['evidencia'][1]})
    put(RULE+'.md','# Regla activa de código SIES · MU 2027\n\nD · Alexi, 29-10-2026. Activación interna H002k.\n\n'+ '\n'.join('- **'+k+'**: '+(v if isinstance(v,str) else '; '.join(v)) for k,v in rule['reglas'].items())+'\n\n## Límites\n\n'+'\n'.join('- '+v for v in rule['limites'])+'\n\n## Fuentes fijadas\n\n'+table([{'id':k,**v} for k,v in refs.items()],['id','ruta','sha256','clase'])+'\n\n## Métricas históricas H002j (C)\n\n'+table(metrics['por_grupo'],['anio','grupo','filas_mu','aciertos_H002j','acierto_H002j_pct'])+'\n\nEstas métricas no son una tasa SIES ni un resultado de matrícula 2027.\n\n## Uso\n\n`common.codigo_sies_mu2027.asignar_codigo_mu2027(fila)` verifica hashes antes de resolver.\nAntiguo: referencia exacta `fila_mu2026` y `cambio_carrera_o_plan=False` explícito; sin certeza pasa a revisión.\nNuevo: `anio=2027`, `cohorte=2027`, familia y clave de plan/sede exactos.\nSin actividad anual no se inventa plan; FOR_ING_ACT no decide regular/continuidad.\n')
    text=frozen(DATA+'/README.md').decode()
    text=text.replace('Estado vigente: H002e','Estado vigente: H002k').replace('Pendientes de planes UMAS.','Se resolverán con MU 2027 por código y total, sin solicitar otro listado.')
    text=text.replace('seis códigos H002b y cinco relaciones H002e.','seis códigos H002b, cinco relaciones H002e y dos H002k.')
    text=text.replace('- VERSION_MULTIPLE_E: CADMP, pendiente en dos filas de código; indicio 7–10\n  expedientes frente a 9 en V2 y 94 en V1, sin aprobación.','- VERSION_MULTIPLE_E: ninguna fila 2027; ADMP y CADMP aprobados en DECISIONES_APROBADAS_v3.json. Los 14 casos históricos 2026 no se alteran.')
    start=text.index('| Estado | 2026 | 2027 |');end=text.index('\n\n',start)
    text=text[:start]+table(countrows,['Estado','2026','2027'])+text[end:]
    text+='\n## Cierre H002k\n\nADMP20251 → I162S2C83J4V1; CADMP20251 → I162S2C83J4V2 (D, Alexi).\nSe conservan las candidaturas anteriores como antecedente explícito dentro de las dos filas.\nRegla activa interna: `'+RULE+'.json`. Los 37 y las revisiones manuales permanecen visibles.\nNo significa catálogo operativo sin pendientes ni autorización de carga.\n\nReproducción vigente: `python3 '+OUT+'/construir.py --check`.\nEl constructor anterior reproduce H002e; para su salida histórica usar checkout del commit base.\nQA vigente: `'+OUT+'/QA.json`; antecedentes QA_H002E y decisiones v1/v2 no se reescriben.\n'
    put(DATA+'/README.md',text)
    qa={'estado':'PASS','clase':'C','filas':267,'conteos':counts,'filas_modificadas':changes,'controles':{
        'base_H002e_reproducida':all(base_qa['controles'].values()),'solo_dos_filas_2027':len(changes)==2,
        '106_2026_y_161_2027':Counter(r['anio'] for r in payload['filas'])==Counter({2026:106,2027:161}),
        '13_aprobadas_0_version_multiple_E_2027':counts['2027']['APROBADA_D_2027']==13 and counts['2027']['VERSION_MULTIPLE_E']==0,
        'resto_filas_intacto':sum(a==b for a,b in zip(baseline['filas'],payload['filas']))==265,
        'MU2026_4105_potenciales':sum(summary.values())==4105,'cinco_familias_252_E':five_E==252,
        'antiguos_con_codigo_conservado':summary['ANTIGUO']+summary['REVISION_MANUAL']==4105,
        'nuevos_simulados_sin_personas':True,'37_no_resueltos':len(pending)==37},'familias_ambiguas':ambiguous_rows,'revision':{k:v for k,v in review['MU2026'].items() if k!='filas'},'nuevos_catalogo':{k:v for k,v in review['nuevos_simulados'].items() if k!='filas'}}
    assert all(qa['controles'].values())
    put(OUT+'/QA.json',qa);put('outputs/paridad_codigo_sies_20261029/QA.json',qa)
    register=json.loads(frozen(MILE+'/REGISTRO.json'))
    register.update(actualizacion='H002k',estado='PARIDAD_2027_CERRADA_CON_REVISION_MANUAL_Y_37_PENDIENTES',conteos=counts,
        correspondencias_aprobadas_D=13,decision=DATA+'/DECISIONES_APROBADAS_v3.json',QA_entrega=OUT+'/QA.json',
        regla_activa=RULE+'.json',pendientes_sin_plan=37,pendiente_CADMP=False,
        cierre={'resuelto':'Dos últimas versiones ADMP/CADMP, 13 aprobaciones D, 0 VERSION_MULTIPLE_E 2027',
                'pendiente':'37 códigos sin plan hasta MU 2027; revisión manual potencial por tipo/ambigüedad; oferta aceptada antes de carga',
                'clase':'D','fuente':decision['fuente'],'lista_revision':OUT+'/LISTA_REVISION_MANUAL_MU2027.json'})
    # Manifest no contiene su propio hash; salidas nuevas y fuentes explícitas.
    manifest={'hito':'H002k','fecha':'2026-10-29','base_commit':BASE,'estado':'ACTIVA_INTERNA_NO_CARGA','fuentes':refs,
        'antecedente_manifest_sha256':sha(frozen(DATA+'/MANIFEST.json')),
        'generador':{'ruta':OUT+'/construir.py','sha256':sha(Path(__file__).read_bytes())},
        'funcion':{'ruta':'common/codigo_sies_mu2027.py','sha256':sha((ROOT/'common/codigo_sies_mu2027.py').read_bytes())},
        'salidas':{p:sha(b) for p,b in sorted(built.items())}}
    put(DATA+'/MANIFEST.json',manifest);register['manifest_sha256']=sha(built[DATA+'/MANIFEST.json'])
    put(MILE+'/REGISTRO.json',register)
    text=frozen(MILE+'/README.md').decode().replace('## Estado vigente H002e','## Antecedente H002e (superado sólo en alcance H002k)')
    text+='\n## Estado vigente H002k · 29-10-2026\n\nD · Alexi: ADMP20251/V1 y CADMP20251/V2 aprobados; 13 códigos APROBADA_D_2027 y cero VERSION_MULTIPLE_E en 2027.\nRegla interna activa: '+RULE+'.json. Antiguos conservan su código, aun inconsistente; tipo E y otros casos pasan a revisión.\nPendientes: 37 códigos sin plan hasta MU 2027, revisión manual y reemplazo de V06 preparada por aceptada.\nNo se modifica retención, VIG, v20 ni cargas. QA: '+OUT+'/QA.json.\n'
    put(MILE+'/README.md',text)
    put(OUT+'/INFORME.md','# H002k · Activación interna MU 2027\n\nD · Alexi, 29-10-2026. No se genera carga.\n\n'+table(countrows,['Estado','2026','2027'])+'\n\n## Universo potencial MU 2026 (matrículas, todos los VIG)\n\n'+json.dumps({k:v for k,v in review['MU2026'].items() if k!='filas'},ensure_ascii=False,indent=2)+'\n\nLos 252 pertenecen sólo a cinco familias. No confundir el universo potencial con continuidad observada 2027.\n\n## Nuevos simulados: opciones de catálogo\n\n'+json.dumps({k:v for k,v in review['nuevos_simulados'].items() if k!='filas'},ensure_ascii=False,indent=2)+'\n\n37 códigos adicionales sin plan: no personas. No sumar las unidades.\n\n## ADMP/CADMP: control MU 2026\n\n'+table(evidence,['codcarpr','plan','codigo_unico','VIG','matriculas_MU2026'])+'\n\nC83J4V2 tiene 9 VIG 1 de CADMP (7 con plan anual observado, 2 sin él) y 1 VIG 0 sin plan. Las referencias sin plan pasan a revisión; decisión nueva sólo catálogo 2027. Perfil H002j y antecedentes citados con hash.\n\n## Reproducción\n\n`python3 '+OUT+'/construir.py --check` verifica bytes sin escribir.\nPruebas: `python3 -m unittest discover -s '+OUT+" -p 'test_*.py'`.\nDetalle de revisión sólo en `~/.local/share/ipss/h002k_20261029/`; no versionado.\n")
    return built,detail,qa


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    built,detail,qa=construir()
    for rel,raw in built.items():
        p=ROOT/rel
        if args.check:
            if not p.exists() or p.read_bytes()!=raw:raise ValueError('No reproducible: '+rel)
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    if not args.check:
        private=Path.home()/'.local/share/ipss/h002k_20261029';private.mkdir(parents=True,exist_ok=True,mode=0o700)
        p=private/'LISTA_REVISION_MANUAL_MU2027.json';p.write_bytes(js(detail));p.chmod(0o600)
    print(json.dumps({'estado':qa['estado'],'salidas':len(built),'check':args.check,'revision':qa['revision'],'catalogo':qa['nuevos_catalogo']},ensure_ascii=False))
if __name__=='__main__':main()

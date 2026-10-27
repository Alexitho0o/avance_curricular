"""Evalúa cierres candidatos desde evidencias persistentes, sin reabrir bases."""
from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
O=Path(__file__).resolve().parent;R=O.parents[1]
def read(rel):return json.loads((R/rel).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
head=git('rev-parse','HEAD');protected={p:sha(R/p) for p in git('diff','--name-only').splitlines() if (R/p).is_file()}
inputs=['outputs/revision_21_ramos_4_expedientes_20261026/RESULTADO_AGREGADO.json','outputs/confirmacion_reconocimientos_20261026/RESULTADO_AGREGADO.json','outputs/busqueda_homologaciones_promedios_20261026/RESULTADO_AGREGADO.json','outputs/origen_docencia_titulacion_20261026/DECISION_CIERRE_INTERNO.json']
a,b,c,decision=[read(x) for x in inputs]
p=Path(a['privado']['ruta']);assert sha(p)==a['privado']['sha256'];cases=json.loads(p.read_text());result=[]
for case in cases:
 if not any(x['carrera']=='IINF' for x in case['contextos_v11']):continue
 sources=sorted({x['fuente'] for x in case['datosalumnos']});selected=set();observed=[]
 for src in sources:
  rows=[x for x in case['datosalumnos'] if x['fuente']==src]
  titles=[x for x in rows if x['estado']=='TITULADO'];assert len(titles)==1
  t=titles[0];assert t['carrera']=='IINF' and t['situacion']=='31 - TITULADO APROBADO'
  selected.add(t['CODCLI']);old=[x for x in rows if x['CODCLI']!=t['CODCLI']]
  assert all(x['estado']=='ELIMINADO' and x['situacion']=='10 - ACTUALIZACIÓN DE PLAN DE ESTUDIO 2024' for x in old)
  observed.append({'fuente':src,'fila_titulado':t['fila'],'expedientes':len(rows),'titulados':len(titles)})
 assert len(selected)==1
 selected_cod=next(iter(selected));contexts=[x for x in case['contextos_v11'] if x['CODCLI']==selected_cod];plans={x['plan'] for x in contexts};assert plans=={'IINF20241'}
 result.append({'caso':case['caso'],'estado':'PROPUESTO_CIERRE_INTERNO_NO_APLICADO','clasificacion':'C','evidencia_clasificacion':'B/C','carrera':'IINF','plan':'IINF20241','datos_alumnos':observed,'contextos':len(contexts),'periodos':sorted({str(x['ano'])+'-P'+str(x['periodo']) for x in contexts}),'titulo_observado':[{k:v for k,v in t.items() if k!='expedientes_compatibles'} for t in case['titulos']],'reserva':'La traza calculada anterior seleccionó otro expediente; la propuesta acepta actividad y estado posterior como respaldo interno, no formal. La aprobación de TCRE no se extiende automáticamente a este caso.'})
assert len(result)==3
key=lambda d:(d['carrera'],d['plan'],d['ramo'])
allpairs={key(x):x for x in a['ramos']};rec={key(x):x for x in b['pares']}
assert len(allpairs)==21 and len(rec)==15 and set(rec)<=set(allpairs)
ramos=[]
for k,v in allpairs.items():
 obs=[x for x in c['resultados_exactos'] if key(x)==k and x['fuente']=='PROMEDIOSDEALUMNOS_7804.xlsx'];assert obs
 has=k in rec
 ramos.append({'carrera':k[0],'plan':k[1],'ramo':k[2],'clasificacion':'B/C','reconocimiento_individual_observado':has,'registros_reconocimiento_repetidos':rec[k]['registros_en_7804'] if has else 0,'estados':sorted({x['estado_ramo']+' / '+x['descripcion_estado'] for x in obs}),'ramoequiv_observados':sorted({x['ramo_equivalente'] for x in obs}),'cierre_posible':'Registro individual de reconocimiento observado, limitado a sus expedientes y períodos.' if has else 'Actividad observada; no homologación acreditada.','equivalencia_general':'E: no acreditada para aplicación general en el plan.'})
assert sum(x['registros_reconocimiento_repetidos'] for x in ramos)==21
assert all(x['personas_de_los_cuatro_casos_en_7804']==0 for x in b['pares'])
payload={'fecha_hora':datetime.now(ZoneInfo('America/Santiago')).isoformat(),'alcance':'Revisión de evidencia existente; sin búsquedas en bases ni cambios de canon.','titulaciones':result,'ramos':ramos,'conteos':{'titulo_tcre_cerrado_D':1,'titulos_iinf_propuestos_C':3,'pares_plan_ramo_con_actividad':21,'pares_con_reconocimientos_individuales':15,'registros_reconocimiento_repetidos_no_sumables':21,'pares_solo_aprobacion_reprobacion':6,'equivalencias_generales_nuevas_confirmadas':0},'no_extrapolar':'Los reconocimientos de los 15 pares no corresponden a las cuatro personas en 7804. No vincular estos dos grupos por asociación.','fuentes':{x:sha(R/x) for x in inputs},'privado_verificado':{'ruta':str(p),'sha256':sha(p)},'decision_tcre':decision['id']}
txt=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
for case in cases:
 assert case['RUT'].split('-')[0] not in txt
 for x in case['datosalumnos']:
  if x['CODCLI']:assert str(x['CODCLI']) not in txt
assert all(sha(R/p)==h for p,h in protected.items());assert git('rev-parse','HEAD')==head
(O/'RESULTADO.json').write_text(txt)
qa={'clasificacion':'C','estado':'PASS_REVISION_EVIDENCIA_GUARDADA','sin_nuevas_busquedas':True,'detalle_privado_hash_verificado':True,'salida_sin_rut_codcli':True,'bases_denominadores_diccionario_sin_cambios':True,'head_antes':head,'head_despues':git('rev-parse','HEAD'),'resultado_sha256':sha(O/'RESULTADO.json'),'regla_nueva_aplicada':False,'limite':'Reutiliza evidencia ya registrada; no vuelve a certificar cobertura completa de las fuentes ni atribución formal.'}
(O/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(payload['conteos'],ensure_ascii=False))

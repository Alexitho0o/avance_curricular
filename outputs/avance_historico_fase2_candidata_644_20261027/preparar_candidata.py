"""Prepara propuestas contextuales y simula su impacto sin activar atribuciones."""
from pathlib import Path
import json, hashlib, os, subprocess, re, copy
from collections import Counter, defaultdict
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
PRIOR=ROOT/'outputs/avance_historico_periodos_815_20261027'
AUDIT=ROOT/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior_files={str(p):sha(p) for d in [PRIOR,AUDIT.parent,ROOT/'outputs/avance_historico_fase1_20261027'] for p in d.iterdir() if p.is_file()}
prior_manifest=json.loads((PRIOR/'MANIFEST.json').read_text())
assert sha(PRIOR/'revisar_periodos.py')==prior_manifest['script_sha256']
assert sha(AUDIT)==prior_manifest['lector_reutilizado']['sha256']
# Ejecutar solo el lector/revisor, sin las escrituras ni el cierre anteriores.
ns={'__file__':str(PRIOR/'revisar_periodos.py')}
exec(compile((PRIOR/'revisar_periodos.py').read_text().split('# Solo agregados se exportan.')[0],str(PRIOR/'revisar_periodos.py'),'exec'),ns)
ns['OUT']=OUT
ns['dump']=lambda n,d:(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
exec(compile((PRIOR/'verificar_evidencia.py').read_text(),str(PRIOR/'verificar_evidencia.py'),'exec'),ns)
service=ns['service']; ck=ns['ck'];checks=ns['checks']; dump=ns['dump']
strong=ns['strong_keys'];assert len(strong)==644
if any(x['estado']!='PASS' for x in checks):raise ValueError('QA de fuente fallido')
# Localización de filas físicas PROMEDIOS, conservando valores originales.
f=ns['ns']['frames']['Hoja1']
source_rows=defaultdict(list)
for idx,row in f.iterrows():
 try:
  key=(ns['body'](row['RUT'])+'-'+ns['body'](row['DIG']),ns['clean'](row['CODCLI']),ns['clean'](row['PLAN_DE_ESTUDIO']),ns['clean'](row['CODCARR']),ns['clean'](row['JORNADA']),str(int(float(row['ANO']))),str(int(float(row['PERIODO']))))
 except (ValueError,TypeError):continue
 if key not in strong or ns['clean'](row['ESTADO']) not in ('A','E','I','R'):continue
 source_rows[key].append({'fuente':str(ns['src']['promedios']),'hoja':'Hoja1','fila':int(idx)+2,'RUT_original':row['RUT'],'DV_original':row['DIG'],'CODCLI_original':row['CODCLI'],'plan_original':row['PLAN_DE_ESTUDIO'],'carrera_original':row['CODCARR'],'jornada_original':row['JORNADA'],'ano_original':row['ANO'],'periodo_original':row['PERIODO'],'estado_ramo_original':row['ESTADO']})
proposals=[]
for c in sorted(ns['candidates'],key=lambda x:x['key']):
 if c['key'] not in strong:continue
 key=c['key'];pe,cli,plan,car,jor,year,per=key
 code=c['codes'][0];mm=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)',code)
 assert mm and source_rows[key] and c['codes']==c['mu_codes']
 proposals.append({'contexto':{'persona':pe,'CODCLI':cli,'plan':plan,'carrera':car,'jornada_UMAS':jor,'ano':year,'periodo_UMAS':per},'codigo_propuesto':code,'codigo_adoptado':None,'estado':'PROPUESTA_NO_APROBADA','clasificacion':'C/E','regla_propuesta':'MISMO_ANIO_EXPEDIENTE_PLAN_CARRERA_JORNADA_MU_UNICA_SIN_ALTERNATIVA_OBSERVADA','sede_SIES_candidata':mm[1],'procedencia_sede':'Familia gobernada y MU anual; PROMEDIOS no acredita sede directamente','anclas_existentes':[{'observacion_id':x['observacion_id'],'ano':x['ano'],'periodo':x['periodo'],'codigo_documental':x.get('codigo_documental_atribuible'),'codigo_interno':x.get('codigo_interno_adoptado'),'regla':x['regla']} for x in c['exact']],'evidencias_MU':c['mu'],'evidencias_PROMEDIOS':source_rows[key],'actividad':c['activity'],'filas_H113_excel':[int(i)+1 for i in sorted(ns['refs'][key])],'pendiente':'Aprobación interna acotada; no acredita fecha efectiva, correlativo PLAN_ESTUDIOS ni aceptación SIES.'})
ck('Propuestas únicas',644,len({tuple(p['contexto'].values()) for p in proposals}))
# Ruta privada autorizada histórica, fuera de cualquier checkout Git.
PRIVATE=Path('/Users/alexi/.local/share/ipss/avance_historico_candidata_644_20261027')
assert not PRIVATE.resolve().is_relative_to(ROOT)
for parent in [PRIVATE,*PRIVATE.parents]:assert not (parent/'.git').exists(), 'Directorio privado dentro de Git'
PRIVATE.mkdir(mode=0o700,parents=True,exist_ok=True);PRIVATE.chmod(0o700)
private_path=PRIVATE/'PROPUESTAS_CONTEXTUALES_644.json'
private_data={'estado':'CANDIDATA_NO_ACTIVA','clasificacion':'C/E','edicion_base':service.edicion,'base_sha256':service.descriptor['base_privada']['sha256'],'propuestas':proposals}
content=json.dumps(private_data,ensure_ascii=False,indent=2)+'\n'
if private_path.exists():assert private_path.read_text()==content, 'No sobrescribir una candidata diferente'
else:
 fd=os.open(private_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as fh:fh.write(content)
ck('Detalle privado permisos',0o600,private_path.stat().st_mode&0o777)
# Reutilizar exactamente el cálculo contextual anterior, sin sus escrituras.
section=AUDIT.read_text().split('# Query once per exact context.')[1].split('\n',1)[1].split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0]
base_ns=ns['ns'].copy();base_ns['checks']=checks;base_ns['ck']=ck
exec(compile(section,str(AUDIT),'exec'),base_ns)
baseline=base_ns['result']; original_cache=base_ns['cache']
expected=json.loads((AUDIT.parent/'RESULTADOS.json').read_text())
ck('Reproducción íntegra del diagnóstico previo',expected,baseline)
# Proyección explícita, NO un consumidor operativo ni nueva decisión D.
lookup={tuple(p['contexto'].values()):p for p in proposals}
class Scenario:
 def __init__(self,base):self.base=base;self.db=base.db;self.edicion=base.edicion
 def consultar(self,**q):
  matches=[p for k,p in lookup.items() if k[0]==q['persona'] and k[1]==q['codcli'] and k[2]==q['plan'] and k[3]==q['carrera'] and k[5]==q['anio'] and k[6]==q['periodo']]
  if not matches:return self.base.consultar(**q)
  assert len(matches)==1
  p=matches[0]
  return {'estado':'REUTILIZABLE','codigo_sies':p['codigo_propuesto'],'nivel_respaldo':'C_SIMULACION_NO_ADOPTADA','motivo':'PROPUESTA_644_NO_APROBADA','evidencia':p}
scenario_ns=ns['ns'].copy();scenario_ns['service']=Scenario(service);scenario_ns['checks']=checks;scenario_ns['ck']=ck
exec(compile(section,str(AUDIT),'exec'),scenario_ns)
scenario=scenario_ns['result']; scenario['escenario_adoptado']=False
ck('Mismas unidades de actividad',baseline['unidades_identidad_exacta_foco'],scenario['unidades_identidad_exacta_foco'])
ck('Mismos contextos',5144,scenario['contextos_unicos_consultados'])
ck('Mismas personas foco',488,scenario['personas_con_actividad_exacta'])
ck('Mismos expedientes foco',1032,scenario['expedientes_persona_codcli_carrera'])
ck('Contextos distintos solo propuestas',strong,{k for k,v in scenario_ns['cache'].items() if v.get('codigo_sies')!=original_cache[k].get('codigo_sies')})
# Convertir sets de QA a cantidades: nunca exportar identidades.
checks[-1]['esperado']=644;checks[-1]['observado']=sum(v.get('codigo_sies')!=original_cache[k].get('codigo_sies') for k,v in scenario_ns['cache'].items())
def coverage(cache,dimension):
 grouped=defaultdict(list)
 for k,v in cache.items():
  entity=k[0] if dimension=='personas' else (k[0],k[1],k[3])
  grouped[entity].append(bool(v.get('codigo_sies')))
 return dict(Counter('sin_pendientes' if all(x) else 'parcialmente_atribuidos' if any(x) else 'sin_codigo_atribuido' for x in grouped.values()))
coverage_before={d:coverage(original_cache,d) for d in ('personas','expedientes')}
coverage_after={d:coverage(scenario_ns['cache'],d) for d in ('personas','expedientes')}
ck('Pendientes observados foco',2018,sum(not v.get('codigo_sies') for v in original_cache.values()))
ck('Pendientes proyectados foco',1374,sum(not v.get('codigo_sies') for v in scenario_ns['cache'].values()))
# Partición independiente: sumar aportes de cada candidato a cada fila H113 destino.
independent=copy.deepcopy(baseline['particion_unidades_por_atribucion'])
for c in ns['candidates']:
 if c['key'] not in strong:continue
 key=c['key'];pe,cli,pl,ca,jo,an,per=key
 rr=ns['h'];selected=rr.loc[ns['strict'].get(tuple(pe.split('-')),[])]
 g=selected[(selected['CODCLI'].map(ns['clean'])==cli)&(selected['PLAN_DE_ESTUDIO'].map(ns['clean'])==pl)&(selected['CODCARR'].map(ns['clean'])==ca)&(selected['JORNADA'].map(ns['clean'])==jo)&(selected['_ANO_NUM']==int(an))&(selected['_PERIODO_NUM']==int(per))]
 vals=[int(an=='2025')*int(g['_ESTADO_NORM'].isin(['A','R']).sum()),int(an=='2025')*int(g['_ESTADO_NORM'].eq('A').sum()),len(g),int(g['_ESTADO_NORM'].isin(['A','E','I']).sum())]
 code=c['codes'][0]
 for i in ns['refs'][key]:
  dest=ns['t'].loc[i,8]
  bucket='MISMO_CODIGO' if code==dest else 'OTRA_VERSION_MISMA_FAMILIA' if code.rsplit('V',1)[0]==dest.rsplit('V',1)[0] else 'OTRA_FAMILIA'
  for m,n in zip(base_ns['metrics'],vals):independent['PENDIENTE'][m]-=n;independent[bucket][m]+=n
ck('Impacto independiente de unidades',independent,scenario['particion_unidades_por_atribucion'])
for name,counts in [('antes',coverage_before),('proyectado',coverage_after)]:
 for d,n in [('personas',488),('expedientes',1032)]:ck('Partición '+name+' '+d,n,sum(counts[d].values()))
result={'clasificacion':'B/C/E','estado':'CANDIDATA_NO_ACTIVA_PENDIENTE_APROBACION','propuestas':644,'personas_propuestas':316,'expedientes_propuestas':375,'foco_contextos':5144,'pendientes_actuales':2018,'pendientes_si_se_aprueba':1374,'reduccion_proyectada_contextos':644,'cobertura_personas_expedientes_actual':coverage_before,'cobertura_personas_expedientes_simulada':coverage_after,'anual_actual':baseline['estados_anuales_filas'],'anual_simulado':scenario['estados_anuales_filas'],'acumulado_actual':baseline['estados_acumulados_filas'],'acumulado_simulado':scenario['estados_acumulados_filas'],'unidades_actual':baseline['particion_unidades_por_atribucion'],'unidades_simuladas':scenario['particion_unidades_por_atribucion'],'universo_precarga_inalterado':2371,'filas_foco':489,'asignaciones_aplicadas':0,'tasa_retencion_recalculada':False,'detalle_privado':{'ruta':str(private_path),'sha256':sha(private_path),'git':False},'limite':'Proyección restringida al foco auditado; no es cobertura global, avance curricular validado ni aceptación SIES. No resuelve PLAN_ESTUDIOS numérico.'}
dump('RESULTADOS.json',result)
for k,p in ns['src'].items():ck('Fuente preservada '+k,ns['manifest']['fuentes'][k]['sha256'],sha(p))
for p,hsh in prior_files.items():ck('Salida previa preservada '+str(Path(p).relative_to(ROOT)),hsh,sha(p))
for p,hsh in ns['protected'].items():ck('Cambio previo preservado '+p,hsh,sha(ROOT/p))
ck('Base activa preservada',service.descriptor['base_privada']['sha256'],sha(service.descriptor['base_privada']['ruta']))
ck('Puntero activo preservado',ns['activehash'],sha(ns['active']))
ck('HEAD preservado',ns['start']['head'],ns['git']('rev-parse','HEAD'))
ck('Rama preservada',ns['start']['rama'],ns['git']('branch','--show-current'))
service.close()
# QA público: las comparaciones de conjuntos nunca se serializan.
assert all(not isinstance(x['esperado'],set) and not isinstance(x['observado'],set) for x in checks)
status='PASS_CANDIDATA_NO_ACTIVA' if all(x['estado']=='PASS' for x in checks) else 'FAIL'
dump('QA.json',{'estado':status,'controles':checks,'limite':'No valida promoción ni equivalencia de malla/PLAN_ESTUDIOS.'})
dump('CHECKPOINT.json',{'fase':2,'hito':'2.3','estado':status,'siguiente':'Revisar y aprobar o rechazar las 644 correspondencias internas acotadas antes de activar. Después tratar 171 períodos restantes y los otros grupos de atribución sin repetir auditorías.','fase_3_iniciada':False,'asignaciones_aplicadas':0})
dump('MANIFEST.json',{'fecha_utc':datetime.now(timezone.utc).isoformat(),'clasificacion':'B fuentes; C candidata y simulación; E aprobación pendiente','fuentes':ns['manifest']['fuentes'],'fuentes_mu':ns['source_audit'],'codigo_reutilizado':{str(p.relative_to(ROOT)):sha(p) for p in [AUDIT,PRIOR/'revisar_periodos.py',PRIOR/'verificar_evidencia.py']},'diccionario':{'edicion':service.edicion,'base_sha256':service.descriptor['base_privada']['sha256'],'estado':'SIN_CAMBIOS'},'detalle_privado':result['detalle_privado'],'git_antes':ns['start'],'git_despues':{'rama':ns['git']('branch','--show-current'),'head':ns['git']('rev-parse','HEAD')},'commit':False,'push':False,'salidas':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST.json'}})
print(json.dumps({'qa':status,'controles':len(checks),'resultados':result},ensure_ascii=False,indent=2))
if status=='FAIL':raise SystemExit(1)

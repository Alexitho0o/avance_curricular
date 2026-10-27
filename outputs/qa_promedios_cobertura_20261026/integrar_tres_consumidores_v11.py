"""Prueba aislamiento y activa revisión v11 con capa; preserva SQLite y denominadores."""
import copy,datetime,json,os,shutil,sqlite3,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import sha256
pointer=ROOT/'data/diccionario_sies_seguimiento/activo.json';old=pointer.read_bytes();active=json.loads(old);oldpath=ROOT/active['descriptor'];assert sha256(oldpath)==active['sha256'] and active['sha256']=='825a6c62a5fa4f59fa0b82e1aca5716082b23cea7014993b50ca51c5c7da252a'
d=json.loads(oldpath.read_text());metadata=OUT/'RESULTADO_CAPA_V11_PROMEDIOS_INTEGRADA.json';m=json.loads(metadata.read_text());assert m['sha256_base_v11']==d['base_privada']['sha256'] and sha256(m['capa_privada']['ruta'])==m['capa_privada']['sha256']
helper=OUT/'candidato_seguimiento_promedios_v11.py';wrapper=OUT/'candidato_consultor_v11_integrado.py';central=ROOT/'scripts/consultar_diccionario_sies_seguimiento.py';helper_dest=ROOT/'common/seguimiento_promedios_v11.py';assert not helper_dest.exists()
scripts=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']
for rel,h in d['componentes_sha256'].items():assert sha256(ROOT/rel)==h
nd=copy.deepcopy(d);nd['edicion']='v11_20261026_86_promedios_integrada';nd['estado']='CANDIDATA_NO_ACTIVA';nd['edicion_anterior']=active;nd['componentes_sha256']['scripts/consultar_diccionario_sies_seguimiento.py']=sha256(wrapper);nd['componentes_sha256']['common/seguimiento_promedios_v11.py']=sha256(helper);nd['capa_promedios']={'metadata':'outputs/qa_promedios_cobertura_20261026/RESULTADO_CAPA_V11_PROMEDIOS_INTEGRADA.json','sha256':sha256(metadata),'alcance':'Último período observado en 12166; datos de extracción y fotos separados, sin recálculo de tasas.'}
private=Path(m['capa_privada']['ruta']).parent;layers=json.loads(Path(m['capa_privada']['ruta']).read_text());selected=[]
for flag in ('NOTA_EXTRACCIONES_DISTINTA','SECCION_EXTRACCIONES_DISTINTA','ESTADO_EXTRACCIONES_DISTINTO','ESTADO_PROMEDIOS_ACTUAL_Y_FOTO_DIFIEREN'):
 r=next(x for x in layers if flag in x['alertas']);selected.append((flag,r['observacion_id']))
db=sqlite3.connect(Path(d['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True);cols=('persona','codcli','plan','anio','periodo','carrera','sede','jornada');requests=[]
for flag,oid in selected:
 row=db.execute('SELECT persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones WHERE id=?',(oid,)).fetchone();assert row;requests.append({'metodo':'consultar','entrada':dict(zip(cols,row))})
amb=db.execute('SELECT persona,codcli,plan,anio,periodo FROM observaciones WHERE payload LIKE ? LIMIT 1',('%ALTERNATIVA_JORNADA_AMBIGUA_SIN_ADJUDICAR%',)).fetchone();assert amb;requests.append({'metodo':'consultar','entrada':dict(zip(cols[:5],amb))});requests.append({'metodo':'codigos_mu','entrada':{'persona':amb[0],'anio':amb[3]}});db.close()
with tempfile.TemporaryDirectory(prefix='qa_integracion_v11_',dir=private) as td:
 t=Path(td)/'repo';t.mkdir()
 for rel in d['componentes_sha256']:
  dest=t/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
 shutil.copyfile(wrapper,t/scripts[0]);shutil.copyfile(helper,t/'common/seguimiento_promedios_v11.py')
 metad=t/nd['capa_promedios']['metadata'];metad.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(metadata,metad)
 (t/'descriptor.json').write_text(json.dumps(nd,ensure_ascii=False));(t/'activo.json').write_text(json.dumps({'descriptor':'descriptor.json','sha256':sha256(t/'descriptor.json')}));(t/'PROYECTO_IPSS.json').write_text(json.dumps({'recursos_comunes':{'diccionario_sies_seguimiento':'activo.json'}}))
 outputs=[]
 for i,script in enumerate(scripts):
  f=Path(td)/f'consulta_{i}.json';p=subprocess.run([sys.executable,str(t/script),'--salida-privada',str(f)],input=json.dumps(requests),text=True,capture_output=True)
  if p.returncode:raise RuntimeError('Consumidor no pasa QA: '+script+' '+p.stderr.splitlines()[-1])
  outputs.append(json.loads(f.read_text()))
 assert outputs[0]==outputs[1]==outputs[2]
 for i,(flag,_) in enumerate(selected):
  layer=outputs[0][i]['seguimiento_promedios'];assert layer['estado']=='DISPONIBLE' and flag in layer['observaciones'][0]['alertas']
 assert outputs[0][4]['motivo']=='CONTEXTO_MULTIPLE' and len(outputs[0][4]['seguimiento_promedios']['observaciones'])==2 and outputs[0][5]['seguimiento_promedios']['estado']=='SIN_CONTEXTO_DE_EXPEDIENTE'
 for i in range(3):
  for j in (0,1):assert outputs[0][i]['seguimiento_promedios']['observaciones'][0]['detalles_discrepancias']
 # Capa privada ausente o alterada: devuelve pendiente explícito, sin asignar valores.
 bad=copy.deepcopy(nd);bad['capa_promedios']['sha256']='0'*64;(t/'descriptor.json').write_text(json.dumps(bad));(t/'activo.json').write_text(json.dumps({'descriptor':'descriptor.json','sha256':sha256(t/'descriptor.json')}));f=Path(td)/'faltante.json';p=subprocess.run([sys.executable,str(t/scripts[0]),'--salida-privada',str(f)],input=json.dumps(requests[:1]),text=True,capture_output=True);assert p.returncode==0 and json.loads(f.read_text())[0]['seguimiento_promedios']['estado']=='PENDIENTE_CAPA_NO_DISPONIBLE_O_NO_VERIFICADA'
dir=ROOT/'data/diccionario_sies_seguimiento/v11_20261026_promedios_integrada';assert not dir.exists();dir.mkdir();nd['estado']='ACTIVA';nd['fecha_hora_activacion']=datetime.datetime.now().astimezone().isoformat();dp=dir/'descriptor.json';dp.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n');(dir/'ACTIVO_ANTERIOR.json').write_bytes(old)
alert={'clasificacion':'D autorización; C integración; E cobertura y fecha','responsable':'Alexi','fecha_hora':nd['fecha_hora_activacion'],'motivo':'Integrar PROMEDIOS y mostrar discrepancias en los tres consumidores de v11','edicion_anterior':active,'base_sha256':d['base_privada']['sha256'],'tres_consumidores_qa':True,'reglas':'Último periodo observado y estado del extracto, sin aplicarlo retroactivamente; fotos y alertas separadas.','limitaciones':['PROMEDIOS incompleto o frescura no certificada','estado histórico y fecha de cambio no acreditados','discrepancias no resueltas','sin cambio de bases ni denominadores'],'reversion':'Restituir wrapper anterior desde Git y ACTIVO_ANTERIOR.json; conservar capa privada y base.'};(dir/'ALERTA_INTEGRACION.json').write_text(json.dumps(alert,ensure_ascii=False,indent=2)+'\n')
before_central=central.read_bytes();project=ROOT/'PROYECTO_IPSS.json';before_project=project.read_bytes();config=json.loads(before_project);config['recursos_comunes']['seguimiento_promedios_v11']=nd['capa_promedios']['metadata'];tmp=pointer.with_name('activo.integracion.tmp')
try:
 helper_dest.write_bytes(helper.read_bytes());central.write_bytes(wrapper.read_bytes());project.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n');tmp.write_text(json.dumps({'descriptor':str(dp.relative_to(ROOT)),'sha256':sha256(dp)},ensure_ascii=False,indent=2)+'\n');os.replace(tmp,pointer)
 with tempfile.TemporaryDirectory(dir=private) as actual:
  results=[]
  for i,script in enumerate(scripts):
   f=Path(actual)/f"consulta_{i}.json"
   check=subprocess.run([sys.executable,str(ROOT/script),"--salida-privada",str(f)],input=json.dumps(requests),text=True,capture_output=True)
   if check.returncode:raise RuntimeError("QA activo falló: "+script+" "+check.stderr.splitlines()[-1])
   results.append(json.loads(f.read_text()))
  assert results[0]==results[1]==results[2]
  assert results[0][0]["seguimiento_promedios"]["estado"]=="DISPONIBLE" and len(results[0][4]["seguimiento_promedios"]["observaciones"])==2

except BaseException:
 central.write_bytes(before_central);project.write_bytes(before_project);pointer.write_bytes(old);helper_dest.unlink(missing_ok=True);tmp.unlink(missing_ok=True);raise
qa={'clasificacion':'C controles; E cobertura y fecha','estado':'PASS_CON_ALCANCE','consultas_por_consumidor':len(requests),'consumidores':3,'respuestas_iguales':True,'alertas_probadas':[x[0] for x in selected],'ambiguo_dos_alternativas':True,'sin_contexto_mu':True,'metadatos_alterados_dejan_pendiente':True,'qa_activa':True,'base_sha256':d['base_privada']['sha256'],'descriptor_sha256':sha256(dp),'sin_cambio_denominadores':True};(OUT/'QA_INTEGRACION_TRES_CONSUMIDORES.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False))

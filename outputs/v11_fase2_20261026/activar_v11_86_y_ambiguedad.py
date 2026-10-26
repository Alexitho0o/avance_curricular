"""Activa v11 autorizada, conserva reversión y no modifica datos originales."""
import collections,copy,datetime,json,os,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
OUT=Path(__file__).parent; pointer=ROOT/'data/diccionario_sies_seguimiento/activo.json'
active=json.loads(pointer.read_text());expected={'descriptor':'data/diccionario_sies_seguimiento/v10_20261026_mu2026_27/descriptor.json','sha256':'409d77a85f4d910baeebc99e89ac1518809d8fa89d3043d4425a991679e28f4c'}
assert active==expected and sha256(ROOT/active['descriptor'])==active['sha256']
candidate=OUT/'DESCRIPTOR_CANDIDATA_86_Y_AMBIGUEDAD.json'; assert sha256(candidate)=='0818890e4365834615cb8bcfdf8c6e6c765439bf322339628509f70a52d630af'
d=json.loads(candidate.read_text()); assert d['estado']=='CANDIDATA_NO_ACTIVA' and d['base_privada']['sha256']=='1dafb1486f3ebd080ad4435a3af80b65a1a7016ba47b51f30d91b9a050985141'
qa=json.loads((OUT/'QA_CANDIDATA_86_Y_AMBIGUEDAD.json').read_text()); regression=json.loads((OUT/'QA_V11_86_REGRESION.json').read_text()); refs=json.loads((OUT/'QA_FUENTES_JORNADAS_AMBIGUAS.json').read_text())
assert qa['estado']=='PASS_CON_ALCANCE_NO_ACTIVA' and regression['consultas_completas']==25900 and regression['consultas_sin_dimensiones']==25900 and regression['otros_cambios']==0 and not regression['errores'] and refs['errores']==0
service=DiccionarioSiesSeguimiento(descriptor=candidate);db=service.db
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and db.execute('SELECT count(*) FROM observaciones').fetchone()[0]==25902 and db.execute('SELECT count(*) FROM mu_anual').fetchone()[0]==12207
states=collections.Counter();ids=set()
for person,cli,payload in db.execute('SELECT persona,codcli,payload FROM observaciones'):
 r=json.loads(payload);states['documental' if r['codigo_documental_atribuible'] else 'interno' if r['codigo_interno_adoptado'] else 'pendiente']+=1;ids.update((person,cli))
assert dict(states)=={'documental':21569,'interno':298,'pendiente':4035};service.close()
name='v11_20261026_86_y_ambiguedad';directory=ROOT/'data/diccionario_sies_seguimiento'/name
if directory.exists():raise SystemExit('Edición ya existe; no sobrescribir')
directory.mkdir(); now=datetime.datetime.now().astimezone().isoformat();nd=copy.deepcopy(d)
nd.update({'edicion':name,'estado':'ACTIVA','fecha_hora_activacion':now,'edicion_anterior':active,'candidata_verificada':{'ruta':str(candidate),'sha256':sha256(candidate)},'qa_alcance':'PASS_CON_ALCANCE; cobertura y atribuciones pendientes documentadas'})
nd['resumen'].update({'personas':6524,'expedientes_persona_codcli_carrera':7264,'codigo_documental_reutilizado':states['documental'],'solo_correspondencia_interna_aprobada':states['interno'],'pendientes_internos_observaciones':states['pendiente']})
files=['DECISION_73_CO_V1_20261026.md','DECISION_13_2025_Y_AMBIGUEDAD.md','QA_FINAL_V11_86_AMBIGUEDAD_20261026.md','QA_V11_86_REGRESION.json','QA_FUENTES_JORNADAS_AMBIGUAS.json','QA_CANDIDATA_86_Y_AMBIGUEDAD.json']
nd['evidencia_activacion_sha256']={str(OUT/f):sha256(OUT/f) for f in files}
dp=directory/'descriptor.json';dp.write_text(json.dumps(nd,ensure_ascii=False,indent=2)+'\n'); dh=sha256(dp)
(directory/'ACTIVO_ANTERIOR.json').write_text(json.dumps(active,ensure_ascii=False,indent=2)+'\n')
notice={'clasificacion':'D autorización; C activación; E límites','responsable_aprobacion':'Alexi','responsable_ejecucion':'Codex','fecha_ejecucion':now,'autorizacion':'Activa la v11 como diccionario vigente y deja documentados los pendientes, sin cambiar las bases ni los denominadores y sin hacer push.','edicion_anterior':active,'edicion_nueva':{'descriptor':str(dp.relative_to(ROOT)),'sha256':dh},'qa':'PASS_CON_ALCANCE','pendientes':['Cobertura incompleta de PROMEDIOS 2026','Atribución documental trimestral y aceptación SIES de correspondencias internas','Dos alternativas de jornada sin adjudicar','Otras excepciones de familia, T1 e identidad documental'],'reversion':'Restituir activo.json desde ACTIVO_ANTERIOR.json; conservar bases privadas.','bases_y_denominadores_modificados':False,'push':False}
(directory/'ALERTA_ACTIVACION.json').write_text(json.dumps(notice,ensure_ascii=False,indent=2)+'\n')
(directory/'PENDIENTES.md').write_text('# Pendientes de la edición v11\n\n'+'\n'.join('- **E:** '+s for s in notice['pendientes'])+'\n\n**C:** Actividad no acredita vigencia ni retención. Los registros sin actividad localizada no se interpretan como deserción.\n')
for path in directory.iterdir():
 text=path.read_text()
 if any(x and len(x)>=6 and x in text for x in ids):raise SystemExit('Identificador individual en documento; activación detenida: '+path.name)
if json.loads(pointer.read_text())!=active:raise SystemExit('Puntero cambiado durante preparación')
tmp=pointer.with_name('activo.v11.tmp');
if tmp.exists():raise SystemExit('Archivo temporal de puntero existente')
tmp.write_text(json.dumps({'descriptor':str(dp.relative_to(ROOT)),'sha256':dh},ensure_ascii=False,indent=2)+'\n');os.replace(tmp,pointer)
s=DiccionarioSiesSeguimiento();assert s.edicion==name;s.close()
print(json.dumps({'edicion':name,'descriptor':str(dp),'descriptor_sha256':dh,'base_sha256':nd['base_privada']['sha256'],'activo_anterior_sha256':active['sha256'],'conteos':dict(states),'fecha':now},ensure_ascii=False))

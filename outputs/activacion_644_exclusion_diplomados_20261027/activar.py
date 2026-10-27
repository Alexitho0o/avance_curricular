"""Promoción autorizada, aditiva y reversible de 644 contextos. Sin publicación."""
import json,sqlite3,sys,copy,os,re,hashlib,subprocess,tempfile
from pathlib import Path
from datetime import datetime
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
from common.seguimiento_promedios_v11 import CapaPromedios
OUT=Path(__file__).parent;PRIVATE=Path('/Users/alexi/.local/share/ipss/activacion_644_20261027')
ED='v12_20261027_644_internos';DEST=ROOT/'data/diccionario_sies_seguimiento'/ED
ACTIVE=ROOT/'data/diccionario_sies_seguimiento/activo.json'
P=Path('/Users/alexi/.local/share/ipss/avance_historico_candidata_644_20261027/PROPUESTAS_CONTEXTUALES_644.json')
assert sha256(P)=='4e41f7e692a0927d74e0f24cf6a4cadb84482e6d34b504a8237565df93502cd2'
assert not DEST.exists();DEST.mkdir()
oldactive=ACTIVE.read_bytes();a=json.loads(oldactive);old=DiccionarioSiesSeguimiento();assert old.edicion=='v11_20261026_86_promedios_integrada'
props=json.loads(P.read_text());assert props['base_sha256']==old.descriptor['base_privada']['sha256'];props=props['propuestas'];assert len(props)==644
inputs=json.load(open('/Users/alexi/.local/share/ipss/avance_historico_fase4_20261027/inputs.json'))
excluded={c:n for c,n in inputs['names'].items() if c.upper()=='ECCURYDP' or 'DIPLOMADO' in n.upper()}
assert not any(p['contexto']['carrera'] in excluded for p in props)
base=PRIVATE/'DICCIONARIO_V12.sqlite';assert not base.exists();db=sqlite3.connect(base);old.db.backup(db);os.chmod(base,0o600)
rows=old.db.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload FROM observaciones ORDER BY id').fetchall();n=max(x[0] for x in rows);new=[]
for p in props:
 x=p['contexto'];q=dict(persona=x['persona'],codcli=x['CODCLI'],plan=x['plan'],anio=x['ano'],periodo=x['periodo_UMAS'],carrera=x['carrera'])
 assert old.consultar(**q)['motivo']=='CONTEXTO_NO_LOCALIZADO'
 assert {v['codigo'] for v in p['evidencias_MU']}=={p['codigo_propuesto']}
 ancs=[]
 for an in p['anclas_existentes']:
  r=json.loads(old.db.execute('SELECT payload FROM observaciones WHERE id=?',(an['observacion_id'],)).fetchone()[0]);ancs.append(r)
  assert (r['persona'],r['CODCLI'],r['plan'],r['ano'],r['carrera'])==(x['persona'],x['CODCLI'],x['plan'],x['ano'],x['carrera'])
  assert (r['codigo_documental_atribuible'] or r['codigo_interno_adoptado'])==p['codigo_propuesto']
 assert ancs
 match=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)',p['codigo_propuesto']);assert match
 assert {str(r['jornada_sies']) for r in ancs}=={match[3]}
 n+=1
 r={'observacion_id':n,'persona':x['persona'],'CODCLI':x['CODCLI'],'plan':x['plan'],'ano':x['ano'],'periodo':x['periodo_UMAS'],'carrera':x['carrera'],'sede_dimension':match[1],'jornada_sies':match[3], 'codigo_documental_atribuible':'','codigo_interno_adoptado':p['codigo_propuesto'],'codigo_propuesto':'','estado_documental':'PENDIENTE_ATRIBUCION_PERIODO','estado_interno':'CORRESPONDENCIA_INTERNA_644_APROBADA','clasificacion':'D_CORRESPONDENCIA_INTERNA_APROBADA','regla':p['regla_propuesta'],'requisito_pendiente':'Atribución documental del período, fecha efectiva del plan y PLAN_ESTUDIOS curricular no acreditados. No prueba envío/aceptación SIES.','aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO','fuentes_promedios':p['evidencias_PROMEDIOS'],'evidencias_matricula':p['evidencias_MU'],'anclas_existentes':p['anclas_existentes'],'procedencia_sede':p['procedencia_sede'],'decision':'DECISION_644_20261027','actividad':p['actividad']}
 db.execute('INSERT INTO observaciones VALUES (?,?,?,?,?,?,?,?,?,?)',(n,x['persona'],x['CODCLI'],x['plan'],x['ano'],x['periodo_UMAS'],x['carrera'],match[1],match[3],json.dumps(r,ensure_ascii=False)))
 new.append(r)
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.commit();db.close()
d=copy.deepcopy(old.descriptor);d.update(edicion=ED,fecha_hora=datetime.now().astimezone().isoformat(),estado='APROBADA_PENDIENTE_QA',base_privada={'ruta':str(base),'sha256':sha256(base)},edicion_anterior=a)
d['resumen_anterior']=d['resumen'];d['resumen']={'universo_observaciones':len(rows)+len(new),'codigo_documental_reutilizado':21569,'solo_correspondencia_interna_aprobada':298+644,'pendientes_internos_observaciones':4035,'nuevos_contextos_internos':644,'personas':len({r[1] for r in rows}|{r['persona'] for r in new}),'expedientes_persona_codcli_carrera':len({(r[1],r[2],r[6]) for r in rows}|{(r['persona'],r['CODCLI'],r['carrera']) for r in new})}
# Conservar íntegra capa previa: nuevas observaciones sin capa se declaran pendientes.
meta_path=ROOT/old.descriptor['capa_promedios']['metadata'];meta=json.loads(meta_path.read_text());assert sha256(meta_path)==old.descriptor['capa_promedios']['sha256']
meta['edicion_diccionario']=ED;meta['sha256_base_v11']=sha256(base);meta['alcance_v12']='25902 observaciones anteriores conservadas; 644 nuevas con capa PROMEDIOS pendiente de indexación. No se infieren fotos ni estados.'
mp=DEST/'CAPA_PROMEDIOS_COMPATIBLE.json';mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2));d['capa_promedios']['metadata']=str(mp.relative_to(ROOT));d['capa_promedios']['sha256']=sha256(mp)
dp=DEST/'descriptor.json';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2));candidate=DiccionarioSiesSeguimiento(descriptor=dp)
cols=('persona','codcli','plan','anio','periodo','carrera','sede','jornada');checked=0
for r in rows:
 q=dict(zip(cols,r[1:9]));u=old.consultar(**q);v=candidate.consultar(**q);u.pop('edicion');v.pop('edicion');assert u==v;checked+=1
for r in new:
 q=dict(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
 v=candidate.consultar(**q);assert v['codigo_sies']==r['codigo_interno_adoptado'] and v['codigo_documental'] is None and v['nivel_respaldo']=='D_CORRESPONDENCIA_INTERNA_APROBADA'
# Todos los registros antiguos y el índice MU se conservan literalmente.
assert candidate.db.execute('SELECT * FROM observaciones WHERE id<=? ORDER BY id',(max(r[0] for r in rows),)).fetchall()==rows
assert candidate.db.execute('SELECT * FROM mu_anual ORDER BY rowid').fetchall()==old.db.execute('SELECT * FROM mu_anual ORDER BY rowid').fetchall()
layer=CapaPromedios(candidate);assert layer.problema is None
qa={'estado':'PASS','consultas_anteriores_iguales':checked,'nuevas_internas_verificadas':len(new),'documentales_nuevas':0,'filas_mu_conservadas':True,'fuentes_y_denominadores_sin_cambio':True,'excluidas_de_candidata':0,'exclusion_vistas_codigos':excluded,'resumen_diccionario':d['resumen'],'limites':['644 nuevas observaciones sin capa de fotos/último estado indexada; consumidor devuelve pendiente explícito','La exclusión de programas no es resolución de atribución']}
old.close();candidate.close()
assert sha256(Path(d['edicion_anterior']['descriptor']))==a['sha256']
assert sha256(Path(json.load(open(ROOT/a['descriptor']))['base_privada']['ruta']))==json.load(open(P))['base_sha256']
# Validar rechazo de base con hash incorrecto, sin tocar SQLite.
bad=copy.deepcopy(d);bad['base_privada']['sha256']='0'*64;bp=PRIVATE/'descriptor_negativo.json';bp.write_text(json.dumps(bad))
try:DiccionarioSiesSeguimiento(descriptor=bp);raise AssertionError('Aceptó hash incorrecto')
except ValueError:qa['hash_incorrecto_rechazado']=True
qa['criterio']='Adición acotada aprobada; no propagación universal'
d['estado']='ACTIVA_APROBADA_QA_PASS';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2))
(DEST/'ACTIVO_ANTERIOR.json').write_bytes(oldactive)
dec={'clase':'D','responsable':'Alexi','ejecutor':'Codex','fecha_hora':datetime.now().astimezone().isoformat(),'autorizacion':'eliminemos ECCURYDP y todo lo que contenga la palabra DIPLOMADO en la carrera observada; la apruebo, incorporala y comprueba','alcance':'644 contextos de candidata hash fijado; exclusión solo vistas internas','candidata_sha256':sha256(P),'atribucion_documental':'PENDIENTE','commit':False,'push':False}
(DEST/'DECISION.json').write_text(json.dumps(dec,ensure_ascii=False,indent=2));(DEST/'ALERTA_CAMBIO.json').write_text(json.dumps({'antes':a,'despues':{'descriptor':str(dp.relative_to(ROOT)),'sha256':sha256(dp)},'decision':'DECISION.json','nuevos':644,'modificados_previos':0},indent=2))
assert ACTIVE.read_bytes()==oldactive
ACTIVE.write_text(json.dumps({'descriptor':str(dp.relative_to(ROOT)),'sha256':sha256(dp)},indent=2)+'\n')
# Tres consumidores reales, consultas nuevas y anteriores, rollback si falla.
try:
 req=[]
 for r in new[:5]:req.append({'metodo':'consultar','entrada':dict(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'])})
 req.append({'metodo':'consultar','entrada':dict(zip(cols,rows[0][1:9]))})
 outputs=[]
 with tempfile.TemporaryDirectory(dir=PRIVATE) as td:
  for i,s in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
   f=Path(td)/str(i);p=subprocess.run([sys.executable,str(ROOT/s),'--salida-privada',str(f)],input=json.dumps(req),text=True,capture_output=True);assert p.returncode==0,'Consumidor falló';outputs.append(json.loads(f.read_text()))
 assert outputs[0]==outputs[1]==outputs[2]
 qa['tres_consumidores_iguales']=True
except Exception:
 ACTIVE.write_bytes(oldactive);raise
(OUT/'QA_DICCIONARIO.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));(DEST/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in qa.items() if k!='exclusion_vistas_codigos'},ensure_ascii=False))

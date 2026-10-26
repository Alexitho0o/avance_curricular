"""Candidata privada aditiva; ningún contexto nuevo recibe código adjudicado."""
import collections, copy, datetime, hashlib, json, os, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026'); OUT=Path(__file__).parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
active=json.loads((ROOT/'data/diccionario_sies_seguimiento/activo.json').read_text()); dp=ROOT/active['descriptor'];assert sha(dp)==active['sha256']
d=json.loads(dp.read_text()); old=Path(d['base_privada']['ruta']);assert sha(old)==d['base_privada']['sha256']
candidate=PRIVATE/'DICCIONARIO_SIES_CANDIDATO_V11.sqlite'
if candidate.exists():raise SystemExit('Candidata existe: preservar ejecución anterior')
source=sqlite3.connect(old.as_uri()+'?mode=ro',uri=True); dest=sqlite3.connect(candidate);source.backup(dest);os.chmod(candidate,0o600)
oldrows=source.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload FROM observaciones ORDER BY id').fetchall();oldkeys={(r[1],r[2],r[3],r[4],r[5]) for r in oldrows}; owners=collections.defaultdict(set)
for r in oldrows:owners[r[2]].add(r[1])
incoming=json.loads((PRIVATE/'CONTEXTOS_CANDIDATOS.json').read_text()); counts=collections.Counter((x['persona'],x['CODCLI'],x['plan'],x['anio'],x['periodo']) for x in incoming)
incoming_owners=collections.defaultdict(set)
for x in incoming:incoming_owners[x['CODCLI']].add(x['persona'])
added=[]; skipped=collections.Counter(); nextid=max(r[0] for r in oldrows)+1
for x in incoming:
 k=(x['persona'],x['CODCLI'],x['plan'],x['anio'],x['periodo'])
 if k in oldkeys:skipped['contexto_existente']+=1;continue
 if counts[k]!=1:skipped['multiples_dimensiones_misma_llave']+=1;continue
 if owners.get(x['CODCLI'],set())-{x['persona']}:skipped['codcli_otra_identidad_en_v10']+=1;continue
 if incoming_owners[x['CODCLI']]!={x['persona']}:skipped['codcli_ambiguo_en_entradas']+=1;continue
 # La sede DA es actual: el campo se mantiene como código UMAS observado, sin fecharlo.
 payload={'observacion_id':nextid,'persona':x['persona'],'CODCLI':x['CODCLI'],'plan':x['plan'],'ano':x['anio'],'periodo':x['periodo'],'carrera':x['carrera'],'sede_dimension':x['sede_umas_actual'],'jornada_sies':x['jornada_sies'],'codigo_documental_atribuible':'','codigo_interno_adoptado':'','codigo_propuesto':'','estado_interno':'CONTEXTO_ACTIVIDAD_SEDE_HISTORICA_PENDIENTE','clasificacion':'E_PENDIENTE','regla':'ACTIVIDAD_CANDIDATA_SIN_ADJUDICACION','requisito_pendiente':'Acreditar sede histórica, versión y atribución individual; actividad no acredita matrícula vigente.','aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO','familias_candidatas':x['familias_candidatas'],'fuentes_promedios':x['fuentes_filas']}
 dest.execute('INSERT INTO observaciones (id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload) VALUES (?,?,?,?,?,?,?,?,?,?)',(nextid,*k,x['carrera'],x['sede_umas_actual'],x['jornada_sies'],json.dumps(payload,ensure_ascii=False)))
 added.append(k);nextid+=1
dest.commit();check=dest.execute('PRAGMA integrity_check').fetchone()[0];dest.close();source.close();assert check=='ok'
descriptor=copy.deepcopy(d);descriptor['edicion']='v11_candidata_actividad_20261026';descriptor['fecha_hora']=datetime.datetime.now().astimezone().isoformat();descriptor['estado']='CANDIDATA_NO_ACTIVA';descriptor['base_privada']={'ruta':str(candidate),'sha256':sha(candidate)};descriptor['edicion_anterior']={'descriptor':active['descriptor'],'sha256':active['sha256']};descriptor['resumen_base_v10']=descriptor.pop('resumen');descriptor['resumen']={'universo_observaciones':len(oldrows)+len(added),'contextos_nuevos_E':len(added),'personas_y_expedientes_candidata':'Pendiente de reconciliación sin doble conteo'};descriptor['nota_v11']='Candidata aditiva; sede de DA actual no acredita sede histórica; no adopta códigos.'
dp11=OUT/'DESCRIPTOR_CANDIDATA.json';dp11.write_text(json.dumps(descriptor,ensure_ascii=False,indent=2))
before=DiccionarioSiesSeguimiento();after=DiccionarioSiesSeguimiento(descriptor=dp11)
diff=0;seen=set()
for r in oldrows:
 q={'persona':r[1],'codcli':r[2],'plan':r[3],'anio':r[4],'periodo':r[5],'carrera':r[6],'sede':r[7],'jornada':r[8]}
 try:
  a=before.consultar(**q);b=after.consultar(**q)
  a.pop('edicion',None);b.pop('edicion',None)
  if a!=b:diff+=1
 except ValueError:seen.add('consulta_identidad_invalida')
before.close();after.close()
qa={'estado':'CANDIDATA_PENDIENTE_QA_COMPLETO','observaciones_v10':len(oldrows),'contextos_nuevos_E':len(added),'saltados':dict(skipped),'consultas_comparadas':len(oldrows),'diferencias_consulta':diff,'excepciones_qa':sorted(seen),'integridad_sqlite':check,'sha_v10':sha(old),'sha_v11':sha(candidate),'sha_descriptor':sha(dp11),'activo_sin_cambios':sha(dp)==active['sha256'],'nota':'QA parcial: faltan otros consumidores, controles dirigidos e índice por posición. No activar.'}
(OUT/'QA_CANDIDATA_PARCIAL.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False))

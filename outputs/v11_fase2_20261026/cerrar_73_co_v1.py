"""Construye una copia candidata con 73 decisiones D, sin activar ni modificar fuentes."""
import collections,copy,datetime,hashlib,json,os,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,aplicar_adjudicaciones
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026');BASE=PRIVATE/'DICCIONARIO_SIES_CANDIDATO_V11.sqlite';CAND=PRIVATE/'DICCIONARIO_SIES_CANDIDATO_V11_73_CO.sqlite'
INPUT=PRIVATE/'EVALUACION_CIERRE_CO_V1_DETALLE_V2.json';OPS=PRIVATE/'ADJUDICACIONES_73_CO_V1.json';DESCRIPTOR=OUT/'DESCRIPTOR_CANDIDATA_73_CO.json'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
for p in (CAND,OPS,DESCRIPTOR):
 if p.exists():raise SystemExit('No sobrescribir candidato o salida anterior: '+str(p))
if subprocess_check:=os.system('git -C '+str(PRIVATE)+' rev-parse --show-toplevel >/dev/null 2>&1')==0:raise SystemExit('Ubicación privada pertenece a Git')
d=json.loads((OUT/'DESCRIPTOR_CANDIDATA.json').read_text());assert d['estado']=='CANDIDATA_NO_ACTIVA' and sha(BASE)==d['base_privada']['sha256']
act=json.loads((ROOT/'data/diccionario_sies_seguimiento/activo.json').read_text());assert sha(ROOT/act['descriptor'])==act['sha256']
targets=[x for x in json.loads(INPUT.read_text()) if x['co']];assert len(targets)==73 and len({x['persona'] for x in targets})==51 and len({(x['persona'],x['codcli']) for x in targets})==51
expected={'COTEIQ':'I162S3C114J2V1','COTFAR':'I162S3C115J2V1','COTENS':'I162S3C91J2V1'}
src=sqlite3.connect(BASE.as_uri()+'?mode=ro',uri=True);dst=sqlite3.connect(CAND);src.backup(dst);os.chmod(CAND,0o600)
before=list(src.execute('select id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload from observaciones order by id'));before_mu=list(src.execute('select * from mu_anual order by rowid'));operations=[];updated=[];counts=collections.Counter()
for t in targets:
 code=expected[t['carrera']]; assert t['anio']=='2026' and t['sede_actual']=='CO' and t['jornada']=='2' and t['codigo_T1']==code
 for f in ('DA_P2_2026','DA_P3_2026'):
  assert any(x['sede']=='CO' and x['carrera']==t['carrera'] and x['jornada']=='V' for x in t['respaldos'][f])
 annual=[x for x in t['mu_fuente_primaria'] if x['anio']==t['anio_T1']];assert {x['codigo'] for x in annual}=={code} and any(x['vig']=='1' and x['codigo']==code for x in annual)
 activity=[k.split('|') for k in t['promedios']];assert any(x[1:3]==['2026','1'] and x[3]==t['plan'] and x[4]==t['carrera'] and x[5]=='V' for x in activity)
 args=(t['persona'],t['codcli'],t['plan'],t['anio'],t['periodo'],t['carrera'],'CO','2')
 rows=dst.execute('select id,payload from observaciones where persona=? and codcli=? and plan=? and anio=? and periodo=? and carrera=? and sede=? and jornada=?',args).fetchall();assert len(rows)==1
 oid,payload=rows[0];r=json.loads(payload);assert r['codigo_interno_adoptado']=='' and r['codigo_documental_atribuible']=='' and r['familias_candidatas']==[code.rsplit('V',1)[0]]
 new=copy.deepcopy(r);new.update({'codigo_interno_adoptado':code,'estado_interno':'CORRESPONDENCIA_INTERNA_CO_V1_APROBADA','regla':'CO_V1_T1_PLAN_JORNADA_73_APROBADO_20261026','clasificacion':'D correspondencia interna aprobada; B oferta y MU anual; E atribución documental trimestral','requisito_pendiente':'No acredita asignación documental al CODCLI en T2/T3, aceptación SIES, fecha exacta del corte ni matrícula vigente; no extrapolar.'})
 ops={'observacion_id':r['observacion_id'],'estado_antes':r,'estado_despues':new};assert aplicar_adjudicaciones([r],[ops])==[new]
 dst.execute('update observaciones set payload=? where id=?',(json.dumps(new,ensure_ascii=False),oid));operations.append(ops);updated.append(oid);counts[code]+=1
dst.commit();assert dst.execute('pragma integrity_check').fetchone()[0]=='ok'
after=list(dst.execute('select id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload from observaciones order by id'));after_mu=list(dst.execute('select * from mu_anual order by rowid'))
assert len(before)==len(after)==25900 and before_mu==after_mu and all(x[:9]==y[:9] for x,y in zip(before,after))
changed=[x[0] for x,y in zip(before,after) if x[9]!=y[9]];assert len(changed)==73 and set(changed)==set(updated)
dst.close();src.close(); assert sha(BASE)==d['base_privada']['sha256']
fd=os.open(OPS,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(operations,f,ensure_ascii=False)
newdesc=copy.deepcopy(d);newdesc['edicion']='v11_candidata_73_co_v1_20261026';newdesc['fecha_hora']=datetime.datetime.now().astimezone().isoformat();newdesc['base_privada']={'ruta':str(CAND),'sha256':sha(CAND)};newdesc['edicion_anterior']={'descriptor':str(OUT/'DESCRIPTOR_CANDIDATA.json'),'sha256':sha(OUT/'DESCRIPTOR_CANDIDATA.json')};newdesc['resumen']['adjudicaciones_internas_co']=73;newdesc['resumen']['contextos_nuevos_E']=1053;newdesc['estado']='CANDIDATA_NO_ACTIVA';newdesc['nota_v11']='73 decisiones D aprobadas; otras observaciones nuevas siguen E; sin modificación de denominadores.'
DESCRIPTOR.write_text(json.dumps(newdesc,ensure_ascii=False,indent=2))
qa={'estado':'PENDIENTE_QA_CONSUMIDORES','filas_v11_antes_despues':len(before),'decisiones_D':len(changed),'por_codigo':dict(counts),'dimensiones_y_mu_identicas':True,'campos_adjudicados_restringidos':True,'integridad_sqlite':'ok','base_v11_original_intacta':sha(BASE)==d['base_privada']['sha256'],'puntero_activo_intacto':sha(ROOT/act['descriptor'])==act['sha256'],'base_sha256':sha(BASE),'candidata_sha256':sha(CAND),'descriptor_sha256':sha(DESCRIPTOR),'operaciones_privadas_sha256':sha(OPS)}
(OUT/'QA_CIERRE_73_CO.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False))

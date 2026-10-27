"""Candidata v18: adjudicaciones autorizadas y capa complementaria privada."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import copy,json,sqlite3,sys,os,re,subprocess,unicodedata,openpyxl
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,aplicar_adjudicaciones,sha256
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_g_v19_candidata_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
active=R/'data/diccionario_sies_seguimiento/activo.json';ab=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='190ca4c979c8cb38d672ac26832c330d1b883593'
cases=json.loads((P/'APROBADOS_PRIVADO.json').read_text());assert len(cases)==105
old=DiccionarioSiesSeguimiento();assert old.edicion=='v18_20261027_candidata_fase_f';oldrows=old.db.execute('select * from observaciones order by id').fetchall();classification=[]
for x in cases:
 rows=old.db.execute('select id,sede,jornada,payload from observaciones where persona=? and codcli=? and carrera=? and plan=? and anio=? and periodo=?',(x['persona'],x['codcli'],x['carrera'],x['plan'],x['anio'],x['periodo'])).fetchall();assert len(rows)<=1;mm=re.fullmatch(r'I162S(\d+)C\d+J(\d+)V\d+',x['codigo_candidato']);assert mm
 if rows:
  ident,sed,jor,payload=rows[0];z=json.loads(payload);assert not z.get('codigo_documental_atribuible') and not z.get('codigo_interno_adoptado');assert (sed,jor)==(mm[1],mm[2]),'CLAVE_EXISTENTE_INCOMPATIBLE';classification.append(('existing',x,ident))
 else:classification.append(('new',x,None))
print('clasificacion',dict(Counter(z[0] for z in classification)),flush=True)
base=P/'DICCIONARIO_V19_CANDIDATA.sqlite';assert not base.exists();db=sqlite3.connect(base);old.db.backup(db);os.chmod(base,0o600);maxid=max(r[0] for r in oldrows);new=[];ops=[]
for kind,x,ident in classification:
 code=x['codigo_candidato'];mm=re.fullmatch(r'I162S(\d+)C\d+J(\d+)V\d+',code);pending='Atribución documental por período y aceptación SIES pendientes; cobertura PROMEDIOS y fecha histórica de sede no certificadas.'
 if kind=='existing':
  before=json.loads(db.execute('select payload from observaciones where id=?',(ident,)).fetchone()[0]);after=copy.deepcopy(before);after.update({'codigo_interno_adoptado':code,'estado_interno':'CORRESPONDENCIA_INTERNA_APROBADA','clasificacion':'D_CORRESPONDENCIA_INTERNA_APROBADA','regla':'D_FASE_G_MU_SIGUIENTE_CODCLI_INGRESO_ACTIVIDAD_OFERTA','requisito_pendiente':pending});after=aplicar_adjudicaciones([before],[{'observacion_id':ident,'estado_antes':before,'estado_despues':after}])[0];db.execute('update observaciones set payload=? where id=?',(json.dumps(after,ensure_ascii=False),ident));ops.append({'observacion_id':ident,'estado_antes':before,'estado_despues':after})
 else:
  maxid+=1;row={'observacion_id':maxid,'persona':x['persona'],'CODCLI':x['codcli'],'plan':x['plan'],'ano':x['anio'],'periodo':x['periodo'],'carrera':x['carrera'],'sede_dimension':mm[1],'jornada_sies':mm[2],'codigo_documental_atribuible':'','codigo_interno_adoptado':code,'codigo_propuesto':'','estado_documental':'PENDIENTE_ATRIBUCION_PERIODO','estado_interno':'CORRESPONDENCIA_INTERNA_APROBADA','clasificacion':'D_CORRESPONDENCIA_INTERNA_APROBADA','regla':'D_FASE_G_MU_SIGUIENTE_CODCLI_INGRESO_ACTIVIDAD_OFERTA','requisito_pendiente':pending,'aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO','fuentes_promedios':x['actividad'],'evidencias_matricula':x['mu_anio_siguiente'],'evidencias_oferta':x['oferta'],'decision':'AUTORIZACION_ALEXI_FASE_G_20261027','nivel_aprobacion':x['autorizacion'],'riesgo_adicional':'Respaldo al año siguiente en correspondencia interna D, no documental' if x['autorizacion']=='D2A_INTERNA_NO_DOCUMENTAL' else ''};db.execute('insert into observaciones values (?,?,?,?,?,?,?,?,?,?)',(maxid,x['persona'],x['codcli'],x['plan'],x['anio'],x['periodo'],x['carrera'],mm[1],mm[2],json.dumps(row,ensure_ascii=False)));new.append((row,x))
assert len(ops)+len(new)==105;db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok';cnt=Counter()
for (p,) in db.execute('select payload from observaciones'):
 x=json.loads(p);cnt['B/C' if x.get('codigo_documental_atribuible') else 'D' if x.get('codigo_interno_adoptado') else 'E']+=1
db.close()
meta_old=R/old.descriptor['capa_promedios']['metadata'];assert sha256(meta_old)==old.descriptor['capa_promedios']['sha256'];mo=json.loads(meta_old.read_text());oldlayer=Path(mo['capa_privada']['ruta']);assert sha256(oldlayer)==mo['capa_privada']['sha256'];layer=json.loads(oldlayer.read_text());assert len(layer)==27148
# Read actual source rows already indexed in the approved evidence; preserve period and source.
needed=defaultdict(set)
for row,x in new:
 for ref in x['actividad']:needed[ref['fuente']].add(ref['fila'])
raw={};src_hash={}
for path,lines in needed.items():
 refs=[ref for row,x in new for ref in x['actividad'] if ref['fuente']==path];expected={z['sha256'] for z in refs};assert len(expected)==1 and sha256(path)==next(iter(expected));w=openpyxl.load_workbook(path,read_only=True,data_only=True);ws=w['Hoja1'];it=ws.iter_rows(values_only=True);heads={str(z).strip().upper():i for i,z in enumerate(next(it)) if z is not None}
 for rn,values in enumerate(it,2):
  if rn not in lines:continue
  def v(k):
   i=heads.get(k);z=values[i] if i is not None and i<len(values) else None
   return None if z is None else str(z)
  raw[(path,rn)]={k:v(k) for k in ['CODRAMO','CODSECC','NOTA_FINAL','ESTADO','ESTADO_ACADEMICO','ANO','PERIODO']}
 w.close();assert sha256(path)==next(iter(expected));src_hash[path]=next(iter(expected))
for row,x in new:
 records=[{'fuente':ref['fuente'],'sha256':ref['sha256'],'hoja':ref['hoja'],'fila':ref['fila'],**raw[(ref['fuente'],ref['fila'])]} for ref in x['actividad']];assert records
 # No extrapolate extract state: activity is dated, while latest state not reconstructed.
 layer.append({'observacion_id':row['observacion_id'],'ultimo_periodo_promedios':{'ano':None,'periodo':None,'estado':None,'resultado':'NO_RECONSTRUIDO_EN_FASE_F'},'foto_matricula':{'resultado':'FOTO_NO_COMPARADA','estados':[]},'alertas':[],'detalles_discrepancias':[],'indice_complementario':{'actividad_del_contexto':records,'limite':'Estado académico es el de cada extracto; no acredita vigencia histórica.'}})
assert len(layer)==27148+len(new) and len({x['observacion_id'] for x in layer})==len(layer);lp=P/'CAPA_PROMEDIOS_V19_INICIAL.json';assert not lp.exists();fd=os.open(lp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:json.dump(layer,f,ensure_ascii=False)
for name,obj in [('ADJUDICACIONES_PRIVADAS.json',ops),('NUEVAS_OBSERVACIONES_PRIVADAS.json',[x[0] for x in new])]:
 q=P/name;q.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');os.chmod(q,0o600)
ed='v19_20261027_candidata_fase_g';dest=R/'data/diccionario_sies_seguimiento'/ed;assert not dest.exists();dest.mkdir();meta=copy.deepcopy(mo);meta['sha256_base_diccionario']=sha256(base);meta['edicion_diccionario']=ed;meta['total_observaciones']=len(layer);meta['capa_privada']={'ruta':str(lp),'sha256':sha256(lp)};meta['alcance_v18']='Entradas nuevas con actividad fuente; estado más reciente y fotos no reconstruidos y no inferidos.';mp=dest/'CAPA_PROMEDIOS.json';mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');d=copy.deepcopy(old.descriptor);d['edicion']=ed;d['estado']='CANDIDATA_NO_ACTIVA';d['fecha_hora']=datetime.now().astimezone().isoformat();d['fecha_hora_activacion']=None;d['edicion_anterior']=json.loads(ab);d['base_privada']={'ruta':str(base),'sha256':sha256(base)};d['capa_promedios']={'metadata':str(mp.relative_to(R)),'sha256':sha256(mp),'alcance':'Actividad por contexto; estado histórico no inferido.'};d['resumen']={'universo_observaciones':sum(cnt.values()),'B/C':cnt['B/C'],'D':cnt['D'],'E':cnt['E'],'pendientes_internos_observaciones':cnt['E'],'capa_complementaria_observaciones':len(layer),'E_actualizadas':len(ops),'nuevas_observaciones':len(new)};dp=dest/'descriptor.json';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');assert '/sessions/' not in dp.read_text();cand=DiccionarioSiesSeguimiento(descriptor=dp);orows=old.db.execute('select * from observaciones order by id').fetchall();nrows=cand.db.execute('select * from observaciones order by id').fetchall();changedids={z['observacion_id'] for z in ops};unchanged=0
for a,b in zip(orows,nrows):
 assert a[:9]==b[:9]
 if a[0] not in changedids:assert a[9]==b[9];unchanged+=1
 else:assert json.loads(b[9])==next(z['estado_despues'] for z in ops if z['observacion_id']==a[0])
 q=dict(zip(['persona','codcli','plan','anio','periodo','carrera','sede','jornada'],a[1:9]));u=old.consultar(**q);v=cand.consultar(**q);u.pop('edicion',None);v.pop('edicion',None)
 if a[0] not in changedids:assert u==v
 else:assert v.get('nivel_respaldo')=='D_CORRESPONDENCIA_INTERNA_APROBADA'
for row,x in new:
 q={'persona':row['persona'],'codcli':row['CODCLI'],'plan':row['plan'],'anio':row['ano'],'periodo':row['periodo'],'carrera':row['carrera'],'sede':row['sede_dimension'],'jornada':row['jornada_sies']};v=cand.consultar(**q);assert v.get('codigo_sies')==row['codigo_interno_adoptado'] and v.get('nivel_respaldo')=='D_CORRESPONDENCIA_INTERNA_APROBADA'
assert old.db.execute('select * from mu_anual order by rowid').fetchall()==cand.db.execute('select * from mu_anual order by rowid').fetchall();assert active.read_bytes()==ab
old.close();cand.close();res={'existentes_E':len(ops),'nuevas':len(new),'otras_consultas_iguales':unchanged,'resumen':d['resumen'],'base_sha256':sha256(base),'capa_sha256':sha256(lp),'descriptor_sha256':sha256(dp),'fuentes_actividad_sha256':src_hash,'puntero_intacto':True};(O/'CONSTRUCCION_QA.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='fuentes_actividad_sha256'},ensure_ascii=False))

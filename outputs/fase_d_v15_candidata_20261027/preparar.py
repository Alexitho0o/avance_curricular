"""Candidata v15: aprobación de 308 contextos; no activa ni publica."""
from pathlib import Path
from datetime import datetime
from collections import Counter
import copy,hashlib,json,os,re,sqlite3,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,aplicar_adjudicaciones,sha256
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
active=R/'data/diccionario_sies_seguimiento/activo.json';ab=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='567795c77eed72d92f4ba6879960ecf9d56e9909'
m=R/'outputs/fase_d_hito2b_20261027/MANIFEST.json';assert sha256(m)=='38f85f005438fc6751c8d162ea2fb41f9bb0a65c684be4b0f3dfbf0da983734a';ma=json.loads(m.read_text());ap=Path(ma['detalle_privado']['ruta']);assert sha256(ap)==ma['detalle_privado']['sha256'];cases=[x for x in json.loads(ap.read_text()) if x['nivel']=='D1_PROPUESTA'];assert len(cases)==308
old=DiccionarioSiesSeguimiento();assert old.edicion=='v14_20261027_contextos_42';dbfile=P/'DICCIONARIO_V15_CANDIDATA.sqlite';assert not dbfile.exists();conn=sqlite3.connect(dbfile);old.db.backup(conn);os.chmod(dbfile,0o600)
oldrows=old.db.execute('select * from observaciones order by id').fetchall();maxid=max(r[0] for r in oldrows);ops=[];added=[];touched=[]
for x in cases:
 pe=x['persona'];cli=x['codcli'];car=x['carrera'];plan=x['plan'];year=x['anio'];period=x['periodo'];code=x['codigo_propuesto'];mm=re.fullmatch(r'I162S(\d+)C\d+J(\d+)V\d+',code);assert mm
 rows=conn.execute('select id,payload from observaciones where persona=? and codcli=? and carrera=? and plan=? and anio=? and periodo=?',(pe,cli,car,plan,year,period)).fetchall();assert len(rows)<=1
 if rows:
  ident,payload=rows[0];before=json.loads(payload);assert not before['codigo_documental_atribuible'] and not before['codigo_interno_adoptado'];after=copy.deepcopy(before);after.update({'codigo_interno_adoptado':code,'estado_interno':'CORRESPONDENCIA_INTERNA_APROBADA','regla':'D_HITO2B_MU_ANUAL_CONTEXTO_ACTIVIDAD_INGRESO_OFERTA','clasificacion':'D_CORRESPONDENCIA_INTERNA_APROBADA','requisito_pendiente':'Atribución documental por período y aceptación SIES pendientes; cobertura PROMEDIOS no certificada.'});after=aplicar_adjudicaciones([before],[{'observacion_id':ident,'estado_antes':before,'estado_despues':after}])[0];conn.execute('update observaciones set payload=? where id=?',(json.dumps(after,ensure_ascii=False),ident));ops.append({'observacion_id':ident,'estado_antes':before,'estado_despues':after});touched.append(ident)
 else:
  maxid+=1;row={'observacion_id':maxid,'persona':pe,'CODCLI':cli,'plan':plan,'ano':year,'periodo':period,'carrera':car,'sede_dimension':mm[1],'jornada_sies':mm[2],'codigo_documental_atribuible':'','codigo_interno_adoptado':code,'codigo_propuesto':'','estado_documental':'PENDIENTE_ATRIBUCION_PERIODO','estado_interno':'CORRESPONDENCIA_INTERNA_APROBADA','clasificacion':'D_CORRESPONDENCIA_INTERNA_APROBADA','regla':'D_HITO2B_MU_ANUAL_CONTEXTO_ACTIVIDAD_INGRESO_OFERTA','requisito_pendiente':'Atribución documental por período y aceptación SIES pendientes; cobertura PROMEDIOS no certificada.','aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO','fuentes_promedios':x['promedios_fuentes'],'evidencias_matricula':x['ingreso_fuentes'],'evidencias_oferta':x['oferta_filas'],'decision':'AUTORIZACION_ALEXI_20261027_D_HITO2B'};conn.execute('insert into observaciones values (?,?,?,?,?,?,?,?,?,?)',(maxid,pe,cli,plan,year,period,car,mm[1],mm[2],json.dumps(row,ensure_ascii=False)));added.append(row)
assert len(ops)==6 and len(added)==302
conn.commit();assert conn.execute('pragma integrity_check').fetchone()[0]=='ok';conn.close()
for name,obj in [('ADJUDICACIONES_PRIVADAS.json',ops),('NUEVAS_OBSERVACIONES_PRIVADAS.json',added)]:
 q=P/name;q.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');os.chmod(q,0o600)
d=copy.deepcopy(old.descriptor);ed='v15_20261027_candidata_308';d['edicion']=ed;d['estado']='CANDIDATA_NO_ACTIVA_QA_PENDIENTE';d['fecha_hora']=datetime.now().astimezone().isoformat();d['base_privada']={'ruta':str(dbfile),'sha256':sha256(dbfile)};d['edicion_anterior']=json.loads(ab);d['fecha_hora_activacion']=None
rows=sqlite3.connect('file:'+str(dbfile)+'?mode=ro',uri=True);counter=Counter()
for (payload,) in rows.execute('select payload from observaciones'):
 p=json.loads(payload);counter['B_C' if p.get('codigo_documental_atribuible') else 'D' if p.get('codigo_interno_adoptado') else 'E']+=1
rows.close();d['resumen']={'universo_observaciones':sum(counter.values()),'B_C':counter['B_C'],'D':counter['D'],'E':counter['E'],'observaciones_existentes_actualizadas':len(ops),'observaciones_nuevas':len(added),'alcance':'Recuento exclusivo de observaciones; B/C documental prevalece sobre D si ambos existen.'}
dest=R/'data/diccionario_sies_seguimiento'/ed;assert not dest.exists();dest.mkdir();meta0=R/old.descriptor['capa_promedios']['metadata'];assert sha256(meta0)==old.descriptor['capa_promedios']['sha256'];meta=json.loads(meta0.read_text());meta['edicion_diccionario']=ed;meta['sha256_base_v11']=sha256(dbfile);meta['alcance_v15']='Se conserva la capa anterior; 302 nuevas observaciones aún requieren indexación complementaria.';mp=dest/'CAPA_PROMEDIOS_COMPATIBLE.json';mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');d['capa_promedios']['metadata']=str(mp.relative_to(R));d['capa_promedios']['sha256']=sha256(mp)
dp=dest/'descriptor.json';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');assert '/sessions/' not in dp.read_text();cand=DiccionarioSiesSeguimiento(descriptor=dp)
unchanged=0;failed=[]
for row in oldrows:
 ident,pe,cli,plan,year,period,car,sed,jor,payload=row
 if ident in touched:continue
 q=dict(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car,sede=sed,jornada=jor)
 a=old.consultar(**q);b=cand.consultar(**q);a.pop('edicion',None);b.pop('edicion',None)
 if a!=b:failed.append(ident)
 unchanged+=1
for x in cases:
 code=x['codigo_propuesto'];mm=re.fullmatch(r'I162S(\d+)C\d+J(\d+)V\d+',code);q={'persona':x['persona'],'codcli':x['codcli'],'plan':x['plan'],'carrera':x['carrera'],'anio':x['anio'],'periodo':x['periodo'],'sede':mm[1],'jornada':mm[2]};z=cand.consultar(**q)
 if z.get('codigo_sies')!=code or z.get('nivel_respaldo')!='D_CORRESPONDENCIA_INTERNA_APROBADA':failed.append('autorizada_no_reutilizable')
assert not failed, f'QA de consultas falló: {len(failed)}'
assert old.db.execute('select * from mu_anual order by rowid').fetchall()==cand.db.execute('select * from mu_anual order by rowid').fetchall()
old.close();cand.close();assert active.read_bytes()==ab
(O/'RESULTADO_PRELIMINAR.json').write_text(json.dumps({'existentes_e':len(ops),'nuevas':len(added),'consultas_anteriores_sin_cambio':unchanged,'resumen':d['resumen'],'descriptor':str(dp),'descriptor_sha256':sha256(dp),'puntero_sin_cambio':True},ensure_ascii=False,indent=2)+'\n');print((O/'RESULTADO_PRELIMINAR.json').read_text())

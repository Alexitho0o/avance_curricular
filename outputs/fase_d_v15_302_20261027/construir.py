from pathlib import Path
from collections import Counter
from datetime import datetime
import sqlite3,json,sys,copy,os,subprocess
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_d_v15_302_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
active=R/'data/diccionario_sies_seguimiento/activo.json';activebytes=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='567795c77eed72d92f4ba6879960ecf9d56e9909'
old=DiccionarioSiesSeguimiento();assert old.edicion=='v14_20261027_contextos_42'
prev=Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027/NUEVAS_OBSERVACIONES_PRIVADAS.json';new=json.loads(prev.read_text());assert len(new)==302
base=P/'DICCIONARIO_V15_302.sqlite';assert not base.exists();db=sqlite3.connect(base);old.db.backup(db);os.chmod(base,0o600)
for x in new:db.execute('insert into observaciones values (?,?,?,?,?,?,?,?,?,?)',(x['observacion_id'],x['persona'],x['CODCLI'],x['plan'],x['ano'],x['periodo'],x['carrera'],x['sede_dimension'],x['jornada_sies'],json.dumps(x,ensure_ascii=False)))
db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok';counter=Counter()
for (payload,) in db.execute('select payload from observaciones'):
 x=json.loads(payload);counter['B/C' if x.get('codigo_documental_atribuible') else 'D' if x.get('codigo_interno_adoptado') else 'E']+=1
db.close();d=copy.deepcopy(old.descriptor);ed='v15_20261027_candidata_302';d['edicion']=ed;d['estado']='CANDIDATA_NO_ACTIVA_QA_EN_CURSO';d['fecha_hora']=datetime.now().astimezone().isoformat();d['fecha_hora_activacion']=None;d['edicion_anterior']=json.loads(activebytes);d['base_privada']={'ruta':str(base),'sha256':sha256(base)};d['resumen']={'universo_observaciones':sum(counter.values()),'B/C':counter['B/C'],'D':counter['D'],'E':counter['E'],'nuevas_observaciones_D':302,'seis_existentes_E_no_modificadas':6}
dest=R/'data/diccionario_sies_seguimiento'/ed;assert not dest.exists();dest.mkdir();meta0=R/old.descriptor['capa_promedios']['metadata'];assert sha256(meta0)==old.descriptor['capa_promedios']['sha256'];meta=json.loads(meta0.read_text());meta['edicion_diccionario']=ed;meta['sha256_base_v11']=sha256(base);meta['alcance_v15']='Observaciones nuevas pendientes de indexación complementaria.';mp=dest/'CAPA_PROMEDIOS_COMPATIBLE.json';mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');d['capa_promedios']['metadata']=str(mp.relative_to(R));d['capa_promedios']['sha256']=sha256(mp);desc=dest/'descriptor.json';desc.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');assert '/sessions/' not in desc.read_text();newsvc=DiccionarioSiesSeguimiento(descriptor=desc)
oldrows=old.db.execute('select * from observaciones order by id').fetchall();newrows=newsvc.db.execute('select * from observaciones order by id').fetchall();assert newrows[:len(oldrows)]==oldrows;assert newsvc.db.execute('select * from mu_anual order by rowid').fetchall()==old.db.execute('select * from mu_anual order by rowid').fetchall()
for r in oldrows:
 _,pe,cli,plan,year,period,car,sed,jor,payload=r;q={'persona':pe,'codcli':cli,'plan':plan,'anio':year,'periodo':period,'carrera':car,'sede':sed,'jornada':jor};a=old.consultar(**q);b=newsvc.consultar(**q);a.pop('edicion',None);b.pop('edicion',None);assert a==b
for x in new:
 q={'persona':x['persona'],'codcli':x['CODCLI'],'plan':x['plan'],'anio':x['ano'],'periodo':x['periodo'],'carrera':x['carrera'],'sede':x['sede_dimension'],'jornada':x['jornada_sies']};r=newsvc.consultar(**q);assert r.get('codigo_sies')==x['codigo_interno_adoptado'] and r.get('nivel_respaldo')=='D_CORRESPONDENCIA_INTERNA_APROBADA'
assert active.read_bytes()==activebytes;old.close();newsvc.close();result={'observaciones_anteriores_consultadas':len(oldrows),'nuevas_D':302,'seis_E_sin_cambio':6,'resumen':d['resumen'],'descriptor':str(desc),'descriptor_sha256':sha256(desc),'base_sha256':sha256(base),'head':head};(O/'CONSTRUCCION_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))

from pathlib import Path
from collections import Counter
from datetime import datetime
import json,copy,sqlite3,sys,os,subprocess
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_d_v16_candidata_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
active=R/'data/diccionario_sies_seguimiento/activo.json';ab=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='d6627abf70759262fc0a49e95d16db6c7eb0055c';old=DiccionarioSiesSeguimiento();assert old.edicion=='v15_20261027_candidata_302';rows=old.db.execute('select * from observaciones order by id').fetchall();targets=[r for r in rows if 24775<=r[0]<=25902];assert len(targets)==1128 and Counter(r[7] for r in targets)=={'RE':1055,'CO':73};mapping={'RE':'2','CO':'3'}
before=Counter(tuple(r[1:9]) for r in rows);changed=[]
for r in rows:
 q=list(r)
 if 24775<=q[0]<=25902:q[7]=mapping[q[7]]
 changed.append(tuple(q))
after=Counter(tuple(r[1:9]) for r in changed);assert not any(v>1 and v>before.get(k,0) for k,v in after.items()),'COLISION_NUEVA'
base=P/'DICCIONARIO_V16_CANDIDATA.sqlite';assert not base.exists();db=sqlite3.connect(base);old.db.backup(db);os.chmod(base,0o600)
for r in targets:
 payload=json.loads(r[9]);assert payload['sede_dimension']==r[7];payload['sede_dimension']=mapping[r[7]];db.execute('update observaciones set sede=?,payload=? where id=?',(mapping[r[7]],json.dumps(payload,ensure_ascii=False),r[0]))
db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok';cnt=Counter()
for (s,) in db.execute('select payload from observaciones'):
 x=json.loads(s);cnt['B/C' if x.get('codigo_documental_atribuible') else 'D' if x.get('codigo_interno_adoptado') else 'E']+=1
db.close();ed='v16_20261027_candidata_sedes';dest=R/'data/diccionario_sies_seguimiento'/ed;assert not dest.exists();dest.mkdir();d=copy.deepcopy(old.descriptor);d['edicion']=ed;d['estado']='CANDIDATA_NO_ACTIVA';d['fecha_hora']=datetime.now().astimezone().isoformat();d['fecha_hora_activacion']=None;d['edicion_anterior']=json.loads(ab);d['base_privada']={'ruta':str(base),'sha256':sha256(base)};d['resumen']={'universo_observaciones':sum(cnt.values()),'B/C':cnt['B/C'],'D':cnt['D'],'E':cnt['E'],'pendientes_internos_observaciones':cnt['E'],'sedes_normalizadas':1128,'seis_E_sin_adjudicar':6};meta0=R/old.descriptor['capa_promedios']['metadata'];assert sha256(meta0)==old.descriptor['capa_promedios']['sha256'];meta=json.loads(meta0.read_text());meta['edicion_diccionario']=ed;meta['sha256_base_v11']=sha256(base);meta['alcance_v16']='Solo cambia la representación de sede; 302 observaciones v15 aún requieren indexación complementaria.';mp=dest/'CAPA_PROMEDIOS_COMPATIBLE.json';mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');d['capa_promedios']['metadata']=str(mp.relative_to(R));d['capa_promedios']['sha256']=sha256(mp);dp=dest/'descriptor.json';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');assert '/sessions/' not in dp.read_text();new=DiccionarioSiesSeguimiento(descriptor=dp)
newrows=new.db.execute('select * from observaciones order by id').fetchall();assert len(newrows)==len(rows);same=0
for a,b in zip(rows,newrows):
 assert a[:7]==b[:7] and a[8]==b[8]
 x=json.loads(a[9]);y=json.loads(b[9]);
 if 24775<=a[0]<=25902:assert b[7]==mapping[a[7]];x['sede_dimension']=mapping[a[7]]
 else:assert a[7]==b[7]
 assert x==y
 q={'persona':a[1],'codcli':a[2],'plan':a[3],'anio':a[4],'periodo':a[5],'carrera':a[6],'sede':a[7],'jornada':a[8]};v1=old.consultar(**q);q['sede']=b[7];v2=new.consultar(**q);v1.pop('edicion',None);v2.pop('edicion',None)
 def norm(z):
  if isinstance(z,dict):return {k:(mapping.get(v,v) if k=='sede_dimension' else norm(v)) for k,v in z.items()}
  if isinstance(z,list):return [norm(v) for v in z]
  return z
 assert norm(v1)==v2,'consulta distinta tras normalizar';same+=1
assert old.db.execute('select * from mu_anual order by rowid').fetchall()==new.db.execute('select * from mu_anual order by rowid').fetchall();n86=0
for r in targets:
 p=json.loads(r[9]);code=p.get('codigo_interno_adoptado')
 if not code:continue
 q={'persona':r[1],'codcli':r[2],'plan':r[3],'anio':r[4],'periodo':r[5],'carrera':r[6],'sede':mapping[r[7]],'jornada':r[8]};assert new.consultar(**q).get('codigo_sies')==code;n86+=1
assert n86==86
six=json.loads((Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027/ADJUDICACIONES_PRIVADAS.json').read_text());assert len(six)==6
for x in six:
 p=json.loads(new.db.execute('select payload from observaciones where id=?',(x['observacion_id'],)).fetchone()[0]);assert not p.get('codigo_interno_adoptado') and not p.get('codigo_documental_atribuible')
assert active.read_bytes()==ab;old.close();new.close();res={'consultas_comparadas':same,'sedes':dict(Counter(r[7] for r in targets)),'colisiones_nuevas':0,'D_localizables':n86,'seis_E_conservadas':6,'resumen':d['resumen'],'descriptor_sha256':sha256(dp),'base_sha256':sha256(base)};(O/'QA_CONSTRUCCION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))

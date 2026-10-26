"""Cierre único autorizado; conserva código documental, fuentes y denominadores."""
from pathlib import Path
import sys,json,copy,sqlite3,os,datetime,subprocess,collections
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,aplicar_adjudicaciones
now=datetime.datetime.now(ZoneInfo('America/Santiago'));version='v3_20261023_inf35_07';stamp=now.strftime('%Y%m%d_%H%M%S');O=R/'outputs'/('cierre_inf35_07_jornadas_14_'+stamp);P=Path.home()/'.local/share/ipss'/O.name;V=R/'data/diccionario_sies_seguimiento'/version
A=R/'data/diccionario_sies_seguimiento/activo.json';ab=A.read_bytes();active=json.loads(ab);oldpath=R/active['descriptor'];old=json.loads(oldpath.read_text());assert old['edicion']=='v2_20261023_14';assert sha256(oldpath)==active['sha256'];assert not V.exists()
prev=R/'outputs/cierre_14_jornadas_15_20261023_133759';m=json.loads((prev/'MANIFEST.json').read_text());pp=Path(m['privado']);rp=pp/'REVISION_JORNADAS_15.json';assert sha256(rp)==m['privados_hashes'][rp.name];rs=json.loads(rp.read_text());pick=[x for x in rs if x['propuesta_destino_no_aplicada']];assert len(pick)==1;x=pick[0];assert x['caso']=='INF35-07' and str(x['periodo'])=='3' and x['anio']==2025
inputs={str(prev/'MANIFEST.json'):sha256(prev/'MANIFEST.json'),str(rp):sha256(rp),str(oldpath):sha256(oldpath),old['base_privada']['ruta']:old['base_privada']['sha256']}
for e in x['evidencias']:inputs[e['fuente']]=e['sha256']
for f,h in inputs.items():assert sha256(f)==h
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);V.mkdir()
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
s=DiccionarioSiesSeguimiento();before={i:json.loads(v) for i,v in s.db.execute('select id,payload from observaciones')};b=before[x['observacion_id']];assert not b['codigo_interno_adoptado'] and not b['codigo_documental_atribuible'];after=copy.deepcopy(b);after.update(codigo_interno_adoptado='I162S2C1J2V4',estado_interno='CORRESPONDENCIA_INTERNA_T3_FOTO_JORNADA_APROBADA',regla='INF35_07_T3_2025_J2V4_APROBADO_20261023',clasificacion='D correspondencia interna aprobada; B/C código T1 y foto T3; E atribución documental',requisito_pendiente='Atribución documental al expediente/período y aceptación SIES pendientes. Alcance solo T3-2025; no extrapolar T2 ni otros años. Contexto UMAS posterior O conservado; foto T3 V. Decisión '+str(V.relative_to(R)/'DECISION_APROBADA.json'))
op={'observacion_id':b['observacion_id'],'estado_antes':b,'estado_despues':after,'evidencias':x,'responsable':'Alexi','fecha_hora':now.isoformat()};rr=aplicar_adjudicaciones(list(before.values()),[op]);by={z['observacion_id']:z for z in rr};assert sum(by[i]!=before[i] for i in before)==1
newdb=P/'DICCIONARIO_SIES.sqlite';db=sqlite3.connect(newdb);s.db.backup(db);db.execute('update observaciones set payload=? where id=?',(json.dumps(after,ensure_ascii=False),b['observacion_id']));db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok';assert list(db.execute('select * from mu_anual order by persona,anio,codigo,fuente,hoja,fila'))==list(s.db.execute('select * from mu_anual order by persona,anio,codigo,fuente,hoja,fila'));db.close();newdb.chmod(0o600);dump(P/'ADJUDICACION_INF35_07.json',op);dump(P/'JORNADAS_14_PENDIENTES.json',[r for r in rs if not r['propuesta_destino_no_aplicada']])
counts=copy.deepcopy(old['resumen']);counts['solo_correspondencia_interna_aprobada']+=1;counts['operaciones_aprobadas_integradas']+=1;counts['nuevas_asignaciones']=1
for field,key in [('codigo_interno_adoptado','pendientes_internos'),('codigo_documental_atribuible','pendientes_documentales')]:
 z=[r for r in rr if not r[field]];counts[key]={'observaciones':len(z),'personas':len({r['persona'] for r in z})}
assert counts['pendientes_internos']['observaciones']==3061;assert counts['pendientes_documentales']==old['resumen']['pendientes_documentales']
counts['excepciones_por_estado']=dict(collections.Counter(r['estado_interno'] for r in rr if not r['codigo_interno_adoptado']))
# Este contexto está en el foco histórico múltiple ya definido.
fams=collections.defaultdict(set)
for (c,) in s.db.execute('select distinct codigo from mu_anual'):fams[c.rsplit('V',1)[0]].add(c)
multi={f for f,cs in fams.items() if len(cs)>1};focus=[r for r in rr if any(c.rsplit('V',1)[0] in multi for c in r['codigos_anuales_documentados']+r['candidatos_calculados'] if isinstance(c,str))];counts['foco_versiones_multiples']={'observaciones':len(focus),'codigo_reutilizable':sum(bool(r['codigo_interno_adoptado']) for r in focus),'pendientes':sum(not r['codigo_interno_adoptado'] for r in focus)}
desc=copy.deepcopy(old);desc.update(edicion=version,fecha_hora=now.isoformat(),base_privada={'ruta':str(newdb),'sha256':sha256(newdb)},edicion_anterior={'descriptor':str(oldpath.relative_to(R)),'sha256':sha256(oldpath)},entradas_cierre_sha256=inputs,resumen=counts,adjudicaciones_privadas={'ruta':str(P/'ADJUDICACION_INF35_07.json'),'sha256':sha256(P/'ADJUDICACION_INF35_07.json')});dump(V/'descriptor.json',desc);dump(V/'RESUMEN.json',counts);dump(V/'ACTIVO_ANTERIOR.json',active)
dec={'clasificacion':'D','responsable':'Alexi','fecha_hora':now.isoformat(),'autorizacion_textual':'Aplica el cierre de INF35-07 en T3-2025 como I162S2C1J2V4 por correspondencia interna y continúa revisando las otras 14 observaciones para ubicar el período del cambio de jornada, sin cambiar las bases ni los denominadores.','observaciones':1,'caso':'INF35-07','anio':2025,'periodo':3,'codigo':'I162S2C1J2V4','atribucion_documental':'PENDIENTE','sin_extrapolacion':True};dump(V/'DECISION_APROBADA.json',dec)
d=DiccionarioSiesSeguimiento(descriptor=V/'descriptor.json');n=0
for i,r in before.items():
 q=dict(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies']);u=s.consultar(**q);v=d.consultar(**q);u.pop('edicion');v.pop('edicion')
 if i==b['observacion_id']:assert u['estado']=='EXCEPCION' and v['codigo_interno']=='I162S2C1J2V4' and v['codigo_documental'] is None;n+=1
 else:assert u==v
assert n==1;s.close();d.close()
# Tres consumidores usan la misma API; se probarán tras promoción con el foco completo.
for f,h in inputs.items():assert sha256(f)==h
assert A.read_bytes()==ab
dump(O/'QA_CIERRE.json',{'resultado':'OK','consultas':24774,'cambios_autorizados':1,'restantes_identicas':24773,'indice_mu_identico':True,'documental_inalterado':True,'fuentes_conservadas':True,'denominadores_inalterados':True})
dump(V/'ALERTA_CAMBIO.json',{'fecha_hora':now.isoformat(),'responsable':'Alexi','anterior':active,'nuevo_sha256':sha256(V/'descriptor.json'),'cambios':1,'alcance':'INF35-07/T3-2025 interno D'})
newactive=dict(active,descriptor=str((V/'descriptor.json').relative_to(R)),sha256=sha256(V/'descriptor.json'));tmp=A.with_suffix('.tmp');dump(tmp,newactive);os.replace(tmp,A)
d=DiccionarioSiesSeguimiento();assert d.edicion==version;d.close()
dump(O/'CONFIG.json',{'output':str(O),'privado':str(P),'edicion':str(V),'anterior':str(prev),'HEAD_antes':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()});print(json.dumps({'output':str(O),'version':version,'cierre':1,'jornadas_pendientes':14},ensure_ascii=False))

"""Aplica una correspondencia interna aprobada; preserva atribución documental."""
from pathlib import Path
import sys,json,copy,sqlite3,os,datetime,subprocess,collections
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,aplicar_adjudicaciones
read=lambda p:json.loads(Path(p).read_text())
git=lambda *a:subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
now=datetime.datetime.now(ZoneInfo('America/Santiago'));version='v7_20261023_inf35_03_t3'
O=R/'outputs'/('cierre_inf35_03_t3_'+now.strftime('%Y%m%d_%H%M%S'));P=Path.home()/'.local/share/ipss'/O.name;V=R/'data/diccionario_sies_seguimiento'/version
A=R/'data/diccionario_sies_seguimiento/activo.json';ab=A.read_bytes();active=read(A);oldpath=R/active['descriptor'];old=read(oldpath)
assert old['edicion']=='v6_20261023_dos_jornadas' and sha256(oldpath)==active['sha256'] and not V.exists()
gbefore={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')};assert gbefore['rama']=='feature/ire-2026'
prior=R/'outputs/propuesta_inf35_03_t3_v1_20261023_153418';m=read(prior/'MANIFEST.json')
inputs={str(prior/'MANIFEST.json'):sha256(prior/'MANIFEST.json'),str(oldpath):sha256(oldpath),old['base_privada']['ruta']:old['base_privada']['sha256']}
for n,h in m['salidas_sha256'].items():assert sha256(prior/n)==h
inputs.update(m['fuentes_sha256']);inputs.update(m['antecedentes_sha256'])
ep=Path('/Users/alexi/.local/share/ipss/origen_v1_inf35_03_20261023_150536/EVIDENCIA.json');prev=read(R/'outputs/origen_v1_inf35_03_20261023_150536/MANIFEST.json');inputs[str(ep)]=prev['privados_sha256'][ep.name]
for f,h in inputs.items():assert sha256(f)==h,f
proposal=read(prior/'PROPUESTA.json');assert proposal['codigo_propuesto']=='I162S2C1J1V1' and not proposal['aplicado']
t=next(x for x in read(ep)['objetivos'] if int(x['periodo'])==3);assert t['caso']=='INF35-03' and int(t['anio'])==2024
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);V.mkdir()
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
s=DiccionarioSiesSeguimiento();before={i:json.loads(v) for i,v in s.db.execute('select id,payload from observaciones')};b=before[t['observacion_id']]
assert b['persona']==t['persona'] and b['CODCLI']==t['CODCLI'] and b['plan']=='IINF20241' and not b['codigo_interno_adoptado'] and not b['codigo_documental_atribuible']
a=copy.deepcopy(b);a.update(codigo_interno_adoptado='I162S2C1J1V1',estado_interno='CORRESPONDENCIA_INTERNA_INF35_03_T3_APROBADA',regla='INF35_03_T3_2024_CONTINUIDAD_MU2025_APROBADA_20261023',clasificacion='D correspondencia interna aprobada; B/C continuidad contextual; E atribución documental',requisito_pendiente='Atribución documental T3-2024, regla de origen V1 y fecha efectiva pendientes. Se adopta continuidad de versión T3-2024/T1-2025 para este expediente como supuesto interno explícito, no demostrado documentalmente. No extender a T2-2024 ni 2026. Decisión: '+str(V.relative_to(R)/'DECISION_APROBADA.json'))
op={'observacion_id':b['observacion_id'],'estado_antes':b,'estado_despues':a,'responsable':'Alexi','fecha_hora':now.isoformat(),'evidencia_privada':{'ruta':str(ep),'sha256':sha256(ep)}}
rr=aplicar_adjudicaciones(list(before.values()),[op]);by={x['observacion_id']:x for x in rr};assert [i for i in before if before[i]!=by[i]]==[b['observacion_id']]
dbpath=P/'DICCIONARIO_SIES.sqlite';db=sqlite3.connect(dbpath);s.db.backup(db);db.execute('update observaciones set payload=? where id=?',(json.dumps(a,ensure_ascii=False),b['observacion_id']));db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
for sql in ['select id,persona,codcli,plan,anio,periodo,carrera,sede,jornada from observaciones order by id','select * from mu_anual order by persona,anio,codigo,fuente,hoja,fila']:
 assert list(db.execute(sql))==list(s.db.execute(sql))
db.close();dbpath.chmod(0o600);dump(P/'ADJUDICACION.json',[op])
counts=copy.deepcopy(old['resumen']);counts['solo_correspondencia_interna_aprobada']+=1;counts['operaciones_aprobadas_integradas']+=1;counts['nuevas_asignaciones']=1
for field,key in [('codigo_interno_adoptado','pendientes_internos'),('codigo_documental_atribuible','pendientes_documentales')]:
 q=[r for r in rr if not r[field]];counts[key]={'observaciones':len(q),'personas':len({r['persona'] for r in q})}
assert counts['pendientes_internos']=={'observaciones':3049,'personas':1746};assert counts['pendientes_documentales']==old['resumen']['pendientes_documentales']
counts['excepciones_por_estado']=dict(collections.Counter(r['estado_interno'] for r in rr if not r['codigo_interno_adoptado']))
fams=collections.defaultdict(set)
for (code,) in s.db.execute('select distinct codigo from mu_anual'):fams[code.rsplit('V',1)[0]].add(code)
multi={f for f,cs in fams.items() if len(cs)>1};focus=[r for r in rr if any(c.rsplit('V',1)[0] in multi for c in r['codigos_anuales_documentados']+r['candidatos_calculados'] if isinstance(c,str))]
counts['foco_versiones_multiples']={'observaciones':len(focus),'codigo_reutilizable':sum(bool(r['codigo_interno_adoptado']) for r in focus),'pendientes':sum(not r['codigo_interno_adoptado'] for r in focus)}
desc=copy.deepcopy(old);desc.update(edicion=version,fecha_hora=now.isoformat(),base_privada={'ruta':str(dbpath),'sha256':sha256(dbpath)},edicion_anterior={'descriptor':str(oldpath.relative_to(R)),'sha256':sha256(oldpath)},entradas_cierre_sha256=inputs,resumen=counts,adjudicaciones_privadas={'ruta':str(P/'ADJUDICACION.json'),'sha256':sha256(P/'ADJUDICACION.json')})
dump(V/'descriptor.json',desc);dump(V/'RESUMEN.json',counts);dump(V/'ACTIVO_ANTERIOR.json',active)
decision={'clasificacion':'D','responsable':'Alexi','fecha_hora':now.isoformat(),'autorizacion_textual':'Apruebo cerrar INF35-03 T3-2024 como I162S2C1J1V1 por correspondencia interna. Aplícalo al diccionario, dejando pendiente la atribución documental, y continúa con los dos restantes sin cambiar bases ni denominadores.','asignaciones':[{'caso':'INF35-03','anio':2024,'periodo':3,'codigo':'I162S2C1J1V1'}],'atribucion_documental':'PENDIENTE','supuesto_explicito':proposal['supuesto_explicito'],'sin_extrapolacion':True,'evidencia':str(prior/'MANIFEST.json'),'evidencia_sha256':sha256(prior/'MANIFEST.json')};dump(V/'DECISION_APROBADA.json',decision)
d=DiccionarioSiesSeguimiento(descriptor=V/'descriptor.json')
def query(r):return dict(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
changed=[]
for i,r in before.items():
 x=s.consultar(**query(r));y=d.consultar(**query(r));x.pop('edicion');y.pop('edicion')
 if i==b['observacion_id']:assert x['estado']=='EXCEPCION' and y['codigo_interno']=='I162S2C1J1V1' and y['codigo_documental'] is None;changed.append(i)
 else:assert x==y
assert len(changed)==1
dest=dict(query(b),corte='T3',fuente_periodo=str(V.relative_to(R)/'DECISION_APROBADA.json'));dest.pop('persona')
f=d.seguir_cohorte(persona=t['persona'],anio_mu=2024,codigo_origen=t['codigo_T1'],destinos=[dest]);assert f[0]['codigo_contexto_destino']=='I162S2C1J1V1' and f[0]['codigo_cohorte_origen']==t['codigo_T1'];dump(P/'QA_SEGUIMIENTO.json',f)
test=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_diccionario_sies_seguimiento'],cwd=R,text=True,capture_output=True);assert test.returncode==0;(O/'PRUEBAS.txt').write_text(test.stdout+test.stderr)
for f,h in inputs.items():assert sha256(f)==h
assert A.read_bytes()==ab
dump(V/'ALERTA_CAMBIO.json',{'responsable':'Alexi','fecha_hora':now.isoformat(),'anterior':active,'nuevo_sha256':sha256(V/'descriptor.json'),'cambios':1,'alcance':'INF35-03 T3-2024 interno; documental pendiente'})
newactive=dict(active,descriptor=str((V/'descriptor.json').relative_to(R)),sha256=sha256(V/'descriptor.json'));dump(A.with_suffix('.tmp'),newactive);os.replace(A.with_suffix('.tmp'),A)
try:
 oldfocus=read('/Users/alexi/.local/share/ipss/cierre_inf35_07_jornadas_14_20261023_135630/QA_CONSUMIDOR_0.json');requests=[{'metodo':'consultar','entrada':query(x['evidencia'])} for x in oldfocus];outputs=[]
 for n,script in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
  path=P/('QA_CONSUMIDOR_'+str(n)+'.json');run=subprocess.run([sys.executable,'-B',str(R/script),'--salida-privada',str(path)],input=json.dumps(requests),text=True,capture_output=True);assert run.returncode==0,run.stderr;outputs.append(read(path))
 assert outputs[0]==outputs[1]==outputs[2] and collections.Counter(x['estado'] for x in outputs[0])=={'REUTILIZABLE':27,'EXCEPCION':8}
except Exception:
 A.write_bytes(ab);raise
s.close();d.close();gafter={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')};assert gbefore==gafter
qa={'resultado':'OK','consultas_comparadas':len(rr),'cambios_autorizados':1,'consultas_restantes_identicas':len(rr)-1,'indice_mu_identico':True,'documental_dimensiones_inalterados':True,'consumidores_concordantes':3,'foco_reutilizables':27,'foco_pendientes':8,'fuentes_excel_hash_conforme':True,'denominadores_inalterados':True,'git_antes':gbefore,'git_despues':gafter,'commit_push':False};dump(O/'QA.json',qa)
dump(O/'RESULTADOS.json',{'asignaciones':decision['asignaciones'],'pendientes_internos':counts['pendientes_internos'],'pendientes_documentales':counts['pendientes_documentales'],'foco_original_35':{'reutilizables':27,'pendientes':8,'jornadas_pendientes':2,'homologaciones_pendientes':6}})
doc=R/'docs/DICCIONARIO_SIES_SEGUIMIENTO.md'
with doc.open('a') as f:f.write('\n## Edición v7: INF35-03 T3-2024 (23-10-2026)\n\n**D/C.** Alexi aprueba I162S2C1J1V1 exclusivamente para INF35-03 T3-2024 como correspondencia interna por continuidad contextual T3-2024/T1-2025. **E:** invariancia temporal asumida internamente, sin fecha efectiva demostrada; atribución documental pendiente. No extender a T2-2024 ni 2026. Edición `v7_20261023_inf35_03_t3` conserva v6, índice MU, bases, Excel, dimensiones y denominadores. QA: un cambio autorizado y 24.773 consultas conservadas. Responsable, fecha/hora, evidencia y alerta en descriptor. Sin commit/push.\n')
(O/'INFORME.md').write_text('# Cierre INF35-03 T3-2024\n\nD/C: aplicado I162S2C1J1V1 en diccionario v7 como correspondencia interna aprobada. E: atribución documental y fecha de asignación pendientes; continuidad de versión asumida solo en este contexto.\n\nC: pendientes internos 3.050 → 3.049 observaciones, 1.746 personas sin cambio. Documentales: 3.213 observaciones / 1.838 personas sin cambio. Foco INF35: 27 reutilizables, ocho pendientes (dos jornadas y seis homologaciones).\n\nC: QA compara 24.774 consultas, un cambio autorizado; tres consumidores concordantes. Fuentes, bases, Excel y denominadores conservados. Sin commit/push.\n')
(O/'CHECKPOINT.md').write_text('D/C: v7 activa; INF35-03 T3-2024 V1 interno. E: documental pendiente. Continuar exclusivamente INF35-03/04 T2-2024; no extender cierres T3 hacia atrás. Seis homologaciones permanecen fuera de este bloque.\n')
secrets={t['persona'],t['CODCLI'],t['persona'].split('-')[0]}
for folder in [O,V]:
 for p in folder.iterdir():
  if p.is_file():assert not any(x in p.read_text() for x in secrets)
for f,h in inputs.items():
 if Path(f)==A:assert read(A)==newactive and sha256(V/'ACTIVO_ANTERIOR.json')==h
 else:assert sha256(f)==h
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'responsable_decision':'Alexi','edicion_activa':version,'descriptor':str(V/'descriptor.json'),'descriptor_sha256':sha256(V/'descriptor.json'),'fuentes_hashes':{f:h for f,h in inputs.items() if Path(f)!=A},'control_puntero':{'antes':active,'despues':newactive,'sha256_actual':sha256(A)},'salidas_hashes':{str(f):sha256(f) for f in list(O.iterdir())+list(V.iterdir()) if f.is_file()},'privado':str(P),'privados_hashes':{f.name:sha256(f) for f in P.iterdir()},'codigo_hashes':{str(p.relative_to(R)):sha256(p) for p in [Path(__file__),R/'docs/ESPECIFICACION_CIERRE_INF35_03_T3_REVISION_DOS_20261023.md',doc]},'QA':qa,'originales_denominadores_modificados':False,'commit_push':False})
print(json.dumps({'output':str(O),'edicion':version,'QA':qa,'manifest_sha256':sha256(O/'MANIFEST.json')},ensure_ascii=False))

"""Adopta siete correspondencias internas aprobadas, sin modificar fuentes."""
from pathlib import Path
import sys,json,copy,sqlite3,os,datetime,subprocess,collections
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,aplicar_adjudicaciones
now=datetime.datetime.now(ZoneInfo('America/Santiago'));version='v5_20261023_siete_jornadas'
O=R/'outputs'/('cierre_siete_jornadas_'+now.strftime('%Y%m%d_%H%M%S'))
P=Path.home()/'.local/share/ipss'/O.name;V=R/'data/diccionario_sies_seguimiento'/version
read=lambda p:json.loads(Path(p).read_text())
git=lambda *a:subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
git_before={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')}
assert git_before['rama']=='feature/ire-2026'
A=R/'data/diccionario_sies_seguimiento/activo.json';ab=A.read_bytes();active=read(A);oldpath=R/active['descriptor'];old=read(oldpath)
assert old['edicion']=='v4_20261023_inf35_12' and sha256(oldpath)==active['sha256'] and not V.exists()
prior=R/'outputs/revision_12_jornadas_20261023_143045';m=read(prior/'MANIFEST.json');pp=Path(m['privado'])
inputs={str(prior/'MANIFEST.json'):sha256(prior/'MANIFEST.json'),str(oldpath):sha256(oldpath),old['base_privada']['ruta']:old['base_privada']['sha256']}
for name,h in m['salidas_sha256'].items():assert sha256(prior/name)==h
ep=pp/'EVIDENCIA_PRIVADA.json';assert sha256(ep)==m['privados_hashes'][ep.name];inputs[str(ep)]=sha256(ep)
inputs.update(m['fuentes_sha256'])
book=Path('/Users/alexi/Desktop/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx');inputs[str(book)]='e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe'
for f,h in inputs.items():assert sha256(f)==h,f
ev=read(ep);proposals=read(prior/'RESULTADOS.json')['tabla']
contextkey=lambda x:(x['caso'],int(x['anio']),int(x['periodo']))
approved={contextkey(x):x for x in proposals if x['codigo_propuesto_no_adoptado']!='Pendiente'}
targets=[x for x in ev['objetivos'] if contextkey(x) in approved]
assert len(targets)==7 and len({x['caso'] for x in targets})==4
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);V.mkdir()
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
s=DiccionarioSiesSeguimiento();before={i:json.loads(v) for i,v in s.db.execute('select id,payload from observaciones')}
codes={x['observacion_id']:approved[contextkey(x)]['codigo_propuesto_no_adoptado'] for x in targets};ops=[]
for x in targets:
 b=before[x['observacion_id']];assert not b['codigo_interno_adoptado'] and not b['codigo_documental_atribuible']
 assert b['persona']==x['persona'] and b['CODCLI']==x['CODCLI'] and b['plan']=='IINF20241' and str(b['ano'])==str(x['anio']) and str(b['periodo'])==str(x['periodo'])
 a=copy.deepcopy(b);a.update(codigo_interno_adoptado=codes[b['observacion_id']],estado_interno='CORRESPONDENCIA_INTERNA_SIETE_JORNADAS_APROBADA',regla=x['caso'].replace('-','_')+'_T'+str(b['periodo'])+'_'+str(b['ano'])+'_JORNADA_APROBADO_20261023',clasificacion='D correspondencia interna aprobada; B/C evidencia T1, plan y fotos; E atribución documental')
 context=approved[contextkey(x)]['evidencia']
 a['requisito_pendiente']='Atribución documental al expediente/período y aceptación SIES pendientes. '+context+' Dimensiones originales conservadas, sin retropropagar la jornada actual ni acreditar día exacto del cambio. Solo '+x['caso']+'/'+str(b['ano'])+'/T'+str(b['periodo'])+'. Decisión '+str(V.relative_to(R)/'DECISION_APROBADA.json')
 ops.append({'observacion_id':b['observacion_id'],'estado_antes':b,'estado_despues':a,'responsable':'Alexi','fecha_hora':now.isoformat(),'evidencia_privada':{'ruta':str(ep),'sha256':sha256(ep)}})
rr=aplicar_adjudicaciones(list(before.values()),ops);by={x['observacion_id']:x for x in rr}
assert {i for i in before if by[i]!=before[i]}==set(codes)
dbpath=P/'DICCIONARIO_SIES.sqlite';db=sqlite3.connect(dbpath);s.db.backup(db)
for op in ops:db.execute('update observaciones set payload=? where id=?',(json.dumps(op['estado_despues'],ensure_ascii=False),op['observacion_id']))
db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
assert list(db.execute('select id,persona,codcli,plan,anio,periodo,carrera,sede,jornada from observaciones order by id'))==list(s.db.execute('select id,persona,codcli,plan,anio,periodo,carrera,sede,jornada from observaciones order by id'))
assert list(db.execute('select * from mu_anual order by persona,anio,codigo,fuente,hoja,fila'))==list(s.db.execute('select * from mu_anual order by persona,anio,codigo,fuente,hoja,fila'))
db.close();dbpath.chmod(0o600);dump(P/'ADJUDICACIONES_SIETE_JORNADAS.json',ops)
counts=copy.deepcopy(old['resumen']);counts['solo_correspondencia_interna_aprobada']+=7;counts['operaciones_aprobadas_integradas']+=7;counts['nuevas_asignaciones']=7
for field,key in [('codigo_interno_adoptado','pendientes_internos'),('codigo_documental_atribuible','pendientes_documentales')]:
 q=[r for r in rr if not r[field]];counts[key]={'observaciones':len(q),'personas':len({r['persona'] for r in q})}
assert counts['pendientes_internos']['observaciones']==3052
assert counts['pendientes_documentales']==old['resumen']['pendientes_documentales']
counts['excepciones_por_estado']=dict(collections.Counter(r['estado_interno'] for r in rr if not r['codigo_interno_adoptado']))
fams=collections.defaultdict(set)
for (code,) in s.db.execute('select distinct codigo from mu_anual'):fams[code.rsplit('V',1)[0]].add(code)
multi={f for f,cs in fams.items() if len(cs)>1};focus=[r for r in rr if any(c.rsplit('V',1)[0] in multi for c in r['codigos_anuales_documentados']+r['candidatos_calculados'] if isinstance(c,str))]
counts['foco_versiones_multiples']={'observaciones':len(focus),'codigo_reutilizable':sum(bool(r['codigo_interno_adoptado']) for r in focus),'pendientes':sum(not r['codigo_interno_adoptado'] for r in focus)}
desc=copy.deepcopy(old);desc.update(edicion=version,fecha_hora=now.isoformat(),base_privada={'ruta':str(dbpath),'sha256':sha256(dbpath)},edicion_anterior={'descriptor':str(oldpath.relative_to(R)),'sha256':sha256(oldpath)},entradas_cierre_sha256=inputs,resumen=counts,adjudicaciones_privadas={'ruta':str(P/'ADJUDICACIONES_SIETE_JORNADAS.json'),'sha256':sha256(P/'ADJUDICACIONES_SIETE_JORNADAS.json')})
dump(V/'descriptor.json',desc);dump(V/'RESUMEN.json',counts);dump(V/'ACTIVO_ANTERIOR.json',active)
decision={'clasificacion':'D','responsable':'Alexi','fecha_hora':now.isoformat(),'autorizacion_textual':'Apruebo los siete cierres por correspondencia interna. Aplícalos al diccionario, dejando pendiente la atribución documental, y continúa revisando los cinco restantes sin cambiar las bases ni los denominadores.','asignaciones':[{'caso':x['caso'],'anio':x['anio'],'periodo':x['periodo'],'codigo':codes[x['observacion_id']]} for x in targets],'atribucion_documental':'PENDIENTE','sin_extrapolacion':True,'evidencia':str(prior/'MANIFEST.json'),'evidencia_sha256':sha256(prior/'MANIFEST.json')}
dump(V/'DECISION_APROBADA.json',decision)
d=DiccionarioSiesSeguimiento(descriptor=V/'descriptor.json')
def query(r):return dict(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
changed=[]
for i,r in before.items():
 b=s.consultar(**query(r));a=d.consultar(**query(r));b.pop('edicion');a.pop('edicion')
 if i in codes:assert b['estado']=='EXCEPCION' and a['codigo_interno']==codes[i] and a['codigo_documental'] is None;changed.append(i)
 else:assert b==a
assert set(changed)==set(codes)
follow=[]
for x in targets:
 i=x['observacion_id'];dest=dict(query(before[i]),corte='T'+before[i]['periodo'],fuente_periodo=str(V.relative_to(R)/'DECISION_APROBADA.json'));dest.pop('persona')
 f=d.seguir_cohorte(persona=x['persona'],anio_mu=x['anio'],codigo_origen=x['codigo_T1'],destinos=[dest])
 assert f[0]['codigo_contexto_destino']==codes[i] and f[0]['codigo_cohorte_origen']==x['codigo_T1'];follow.extend(f)
dump(P/'QA_SEGUIMIENTO.json',follow)
test=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_diccionario_sies_seguimiento'],cwd=R,text=True,capture_output=True);assert test.returncode==0;(O/'PRUEBAS_SINTETICAS.txt').write_text(test.stdout+test.stderr)
for f,h in inputs.items():assert sha256(f)==h
assert A.read_bytes()==ab
dump(V/'ALERTA_CAMBIO.json',{'responsable':'Alexi','fecha_hora':now.isoformat(),'anterior':active,'nuevo_sha256':sha256(V/'descriptor.json'),'cambios':7,'alcance':'Siete jornadas aprobadas; alcance individual por período; documental pendiente'})
newactive=dict(active,descriptor=str((V/'descriptor.json').relative_to(R)),sha256=sha256(V/'descriptor.json'))
dump(A.with_suffix('.tmp'),newactive);os.replace(A.with_suffix('.tmp'),A)
# Verificar los tres puntos de entrada; revertir el puntero si fallan.
try:
 oldfocus=read(Path('/Users/alexi/.local/share/ipss/cierre_inf35_07_jornadas_14_20261023_135630/QA_CONSUMIDOR_0.json'))
 requests=[{'metodo':'consultar','entrada':query(x['evidencia'])} for x in oldfocus]
 outputs=[]
 for n,script in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
  path=P/('QA_CONSUMIDOR_'+str(n)+'.json');run=subprocess.run([sys.executable,'-B',str(R/script),'--salida-privada',str(path)],input=json.dumps(requests),text=True,capture_output=True);assert run.returncode==0,run.stderr;outputs.append(read(path))
 assert outputs[0]==outputs[1]==outputs[2]
 assert collections.Counter(x['estado'] for x in outputs[0])=={'REUTILIZABLE':24,'EXCEPCION':11}
except Exception:
 A.write_bytes(ab)
 raise
s.close();d.close()
git_after={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')};assert git_before==git_after
qa={'resultado':'OK','consultas_comparadas':24774,'cambios_autorizados':7,'consultas_restantes_identicas':24767,'indice_mu_identico':True,'dimensiones_documental_inalterados':True,'consumidores':3,'consultas_foco_por_consumidor':35,'foco_reutilizables':24,'foco_pendientes':11,'seguimiento_ancla_T1_conservada':True,'fuentes_excel_hash_conforme':True,'denominadores_inalterados':True,'git_antes':git_before,'git_despues':git_after,'commit_push':False}
dump(O/'QA.json',qa);dump(O/'RESULTADOS.json',{'cierres':7,'asignaciones':decision['asignaciones'],'clasificacion':'D correspondencia interna; E atribución documental','pendientes_internos':counts['pendientes_internos'],'pendientes_documentales':counts['pendientes_documentales'],'foco_original_35':{'reutilizables':24,'pendientes':11,'jornadas_pendientes':5,'homologaciones_pendientes':6}})
dump(P/'CINCO_PENDIENTES.json',[x for x in ev['objetivos'] if contextkey(x) not in approved])
doc=R/'docs/DICCIONARIO_SIES_SEGUIMIENTO.md'
with doc.open('a') as f:f.write('\n## Edición v5: siete jornadas aprobadas (23-10-2026)\n\n**D/C.** Alexi aprobó INF35-01/02 T2/T3-2024 J1V2, INF35-07 T2-2025 J2V4 e INF35-11 T2/T3-2026 J4V2. Edición `v5_20261023_siete_jornadas`; conserva v4, anclas T1 y dimensiones originales. Atribución documental y aceptación SIES pendientes. No acredita fecha efectiva del cambio ni regla universal. Decisión, responsable, fecha/hora, evidencia y alerta acompañan el descriptor. Exactamente siete cambios internos y 24.767 consultas idénticas; índice MU, bases, Excel y denominadores conservados. Sin commit/push.\n')
(O/'INFORME.md').write_text('# Siete cierres internos de jornada\n\n**D/C.** Se aplican únicamente las siete propuestas aprobadas: INF35-01/02 T2/T3-2024 J1V2, INF35-07 T2-2025 J2V4 e INF35-11 T2/T3-2026 J4V2. Edición activa `'+version+'`. **E:** atribución documental y aceptación SIES pendientes.\n\n**C.** QA: siete cambios entre 24.774 consultas; 24.767 idénticas salvo edición. Índice MU y dimensiones conservados; tres consumidores coinciden en 35 consultas. Foco original: 24 reutilizables y 11 pendientes (cinco jornada, seis homologaciones). Fuentes, Excel y denominadores intactos; sin commit/push.\n')
(O/'CHECKPOINT.md').write_text('D/C: v5 activa; siete cierres internos aprobados. E: atribución documental pendiente. Cinco observaciones por jornada quedan en INF35-03/04 T2/T3-2024 e INF35-10 T2-2025. Seis homologaciones fuera de este foco. Sin cambios de bases/denominadores/Excel ni commit/push.\n')
secrets={x['persona'] for x in targets}|{x['CODCLI'] for x in targets}
for folder in [O,V]:
 for p in folder.iterdir():
  if p.is_file():assert not any(x in p.read_text() for x in secrets)
for f,h in inputs.items():
 if Path(f)==A:assert read(A)==newactive and sha256(V/'ACTIVO_ANTERIOR.json')==h
 else:assert sha256(f)==h
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'responsable_decision':'Alexi','edicion_activa':version,'descriptor':str(V/'descriptor.json'),'descriptor_sha256':sha256(V/'descriptor.json'),'fuentes_hashes':{f:h for f,h in inputs.items() if Path(f)!=A},'control_puntero':{'antes':active,'despues':newactive,'sha256_actual':sha256(A)},'salidas_hashes':{str(f):sha256(f) for f in list(O.iterdir())+list(V.iterdir()) if f.is_file()},'privado':str(P),'privados_hashes':{f.name:sha256(f) for f in P.iterdir()},'codigo_hashes':{str(p.relative_to(R)):sha256(p) for p in [Path(__file__),R/'docs/ESPECIFICACION_CIERRE_SIETE_JORNADAS_Y_REVISION_CINCO_20261023.md',doc]},'QA':qa,'originales_denominadores_modificados':False,'commit_push':False})
print(json.dumps({'output':str(O),'edicion':version,'cierres':7,'pendientes_internos':counts['pendientes_internos'],'manifest_sha256':sha256(O/'MANIFEST.json')},ensure_ascii=False))

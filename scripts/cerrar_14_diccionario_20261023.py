"""Cierre D autorizado de 14 contextos; edición inmutable y QA previo al puntero."""
from pathlib import Path
import json,datetime,sqlite3,copy,os,subprocess,sys,collections
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,aplicar_adjudicaciones
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S');version='v2_20261023_14'
O=R/'outputs'/('cierre_14_jornadas_15_'+stamp);P=Path.home()/'.local/share/ipss'/O.name;V=R/'data/diccionario_sies_seguimiento'/version
A=R/'data/diccionario_sies_seguimiento/activo.json';ab=A.read_bytes();active=json.loads(ab);oldpath=R/active['descriptor'];old=json.loads(oldpath.read_text());assert old['edicion']=='v1_20261023';assert sha256(oldpath)==active['sha256']
assert not V.exists();assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
O.mkdir();P.mkdir(mode=0o700);V.mkdir();os.chmod(P,0o700)
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):os.chmod(p,0o600)
prev=R/'outputs/revision_35_informatica_20261023_130829';m=json.loads((prev/'MANIFEST.json').read_text());pp=Path(m['privado']);rs=json.loads((pp/'REVISION_OBSERVACIONES.json').read_text());assert sha256(pp/'REVISION_OBSERVACIONES.json')==m['privado_hashes']['REVISION_OBSERVACIONES.json']
selected=[r for r in rs if r['codigo_recuperable']];assert len(selected)==14
inputs={str(prev/'MANIFEST.json'):sha256(prev/'MANIFEST.json'),str(pp/'REVISION_OBSERVACIONES.json'):sha256(pp/'REVISION_OBSERVACIONES.json'),str(oldpath):sha256(oldpath),old['base_privada']['ruta']:old['base_privada']['sha256']}
for x in selected:
 for e in x['fuentes_mu']+x['fuentes_actividad']+x['puente_identidad']:inputs[e['fuente']]=e['sha256']
for f,h in inputs.items():assert sha256(f)==h
src=DiccionarioSiesSeguimiento();before={i:json.loads(p) for i,p in src.db.execute('select id,payload from observaciones')};ops=[]
for x in selected:
 oid=x['original_consulta']['observacion_id'];b=before[oid];assert b==x['original_consulta']['evidencia'];assert not b['codigo_interno_adoptado'] and not b['codigo_documental_atribuible']
 a=copy.deepcopy(b);is_t1=x['resultado_revision']=='BC_ANCLA_T1_RECUPERABLE'
 a.update(codigo_interno_adoptado=x['codigo_recuperable'],estado_interno='ANCLA_T1_HISTORICA_APROBADA' if is_t1 else 'PUENTE_DOCUMENTAL_P_RUT_APROBADO',regla='INF35_ANCLA_T1_CONTEXTO_HISTORICO_20261023' if is_t1 else 'INF35_P_RUT_PLAN_JORNADA_CORROBORADOS_20261023',clasificacion='D correspondencia interna aprobada; B/C código anual y evidencia; E atribución documental de expediente/período',requisito_pendiente=('Código literal T1 aprobado como ancla histórica; jornada actual del contexto discrepa y se conserva. No extrapolar T2/T3. ' if is_t1 else 'Identidad P–RUT acreditada; reutilización interna del código anual. ')+'Atribución documental al expediente/período y aceptación SIES no acreditadas por este cierre. Decisión '+str(V.relative_to(R)/'DECISION_APROBADA.json'))
 ops.append({'observacion_id':oid,'estado_antes':b,'estado_despues':a,'evidencia_revision':x,'responsable_decision':'Alexi','fecha_hora':now.isoformat()})
after=aplicar_adjudicaciones(list(before.values()),ops);by={r['observacion_id']:r for r in after};assert len(before)==len(by)==24774
changed={i for i in before if before[i]!=by[i]};assert changed=={x['observacion_id'] for x in ops} and len(changed)==14
newdb=P/'DICCIONARIO_SIES.sqlite';db=sqlite3.connect(newdb);src.db.backup(db)
for i in changed:db.execute('update observaciones set payload=? where id=?',(json.dumps(by[i],ensure_ascii=False),i))
# Solo dos enlaces verificados, preservando el documento P de origen.
aliases={}
for x in selected:
 if x['resultado_revision']=='BC_RECUPERABLE_PUENTE_EXPLICITO':aliases[(x['persona'],x['anio'])]=x
assert len(aliases)==2
muold=list(src.db.execute('select * from mu_anual'));assert len(muold)==12201
for (person,year),x in aliases.items():
 assert not src.codigos_mu(persona=person,anio=year)['codigos']
 e=x['fuentes_mu'][0];t=x['original_consulta'];pay={'codigo':x['codigo_recuperable'],'anio':year,'fuente':e['fuente'],'hoja':e['hoja'],'fila':e['fila'],'tipo_doc_original':t['tipo_doc'],'documento_original':t['documento_original'],'dv_original':None,'puente_identidad':x['puente_identidad'],'alcance':'B enlace explícito P–RUT; fila MU original conservada, no nueva matrícula'}
 db.execute('insert into mu_anual values (?,?,?,?,?,?,?)',(person,str(year),pay['codigo'],e['fuente'],e['hoja'],e['fila'],json.dumps(pay,ensure_ascii=False)))
db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok';assert len(list(db.execute('select * from mu_anual')))==len(muold)+2;db.close();newdb.chmod(0o600)
dump(P/'ADJUDICACIONES_14.json',{'operaciones':ops});dump(P/'REVISION_35_ANTERIOR.json',rs)
counts=copy.deepcopy(old['resumen']);counts['solo_correspondencia_interna_aprobada']+=14;counts['nuevas_asignaciones']=14;counts['operaciones_aprobadas_integradas']+=14
for field,key in [('codigo_interno_adoptado','pendientes_internos'),('codigo_documental_atribuible','pendientes_documentales')]:
 pending=[r for r in after if not r[field]];counts[key]={'observaciones':len(pending),'personas':len({r['persona'] for r in pending})}
assert counts['pendientes_internos']['observaciones']==3062;assert counts['pendientes_documentales']==old['resumen']['pendientes_documentales']
counts['excepciones_por_estado']=dict(collections.Counter(r['estado_interno'] for r in after if not r['codigo_interno_adoptado']))
counts['filas_mu_sin_llave_rut_en_indice']={'TIPO_DOCUMENTO_NO_RUT_SIN_PUENTE':23};counts['filas_fuente_mu']=10200;counts['filas_indice_mu_total_historico']=len(muold)+2;counts['filas_indice_mu_2022_2026']=10177;counts['puentes_documentales_explicitos']=2
# Mismo foco del constructor v1, recalculado sin cambiar su definición.
fams=collections.defaultdict(set)
for (code,) in src.db.execute('select distinct codigo from mu_anual'):fams[code.rsplit('V',1)[0]].add(code)
multi={f for f,c in fams.items() if len(c)>1};focus=[r for r in after if any(c.rsplit('V',1)[0] in multi for c in r['codigos_anuales_documentados']+r['candidatos_calculados'] if isinstance(c,str))]
counts['foco_versiones_multiples']={'observaciones':len(focus),'codigo_reutilizable':sum(bool(r['codigo_interno_adoptado']) for r in focus),'pendientes':sum(not r['codigo_interno_adoptado'] for r in focus)}
desc=copy.deepcopy(old);desc.update(edicion=version,fecha_hora=now.isoformat(),base_privada={'ruta':str(newdb),'sha256':sha256(newdb)},resumen=counts,edicion_anterior={'descriptor':str(oldpath.relative_to(R)),'sha256':sha256(oldpath)},entradas_cierre_sha256=inputs,adjudicaciones_privadas={'ruta':str(P/'ADJUDICACIONES_14.json'),'sha256':sha256(P/'ADJUDICACIONES_14.json')})
dump(V/'descriptor.json',desc);dump(V/'RESUMEN.json',counts)
decision={'clasificacion':'D decisión interna; B/C evidencia revisada','responsable':'Alexi','fecha_hora':now.isoformat(),'autorizacion_textual':'Aplica los 14 cierres recuperables al diccionario y revisa los respaldos históricos para ubicar los cambios de jornada de las 15 observaciones T2/T3, sin cambiar las bases ni los denominadores.','alcance':{'anclas_T1':8,'puente_P_RUT':6,'observaciones':14,'personas':10,'enlaces_identidad_mu':2},'fuente_revision':str(prev/'MANIFEST.json'),'reglas':['No extrapolar de ancla T1 a T2/T3','No transformar cierre interno en atribución documental o aceptación SIES','No cambiar dimensiones originales ni denominadores'],'pendientes_foco':{'T2_T3_jornada':15,'homologaciones_TPAS':6}}
dump(V/'DECISION_APROBADA.json',decision);dump(V/'ACTIVO_ANTERIOR.json',active)
# Comparación completa de consultas, incluyendo negativos de contexto.
dst=DiccionarioSiesSeguimiento(descriptor=V/'descriptor.json');n=0
for i,b in before.items():
 q={'persona':b['persona'],'codcli':b['CODCLI'],'plan':b['plan'],'anio':b['ano'],'periodo':b['periodo'],'carrera':b['carrera'],'sede':b['sede_dimension'],'jornada':b['jornada_sies']}
 a1=src.consultar(**q);a2=dst.consultar(**q);a1.pop('edicion');a2.pop('edicion')
 if i not in changed:assert a1==a2
 else:assert a1['estado']=='EXCEPCION' and a2['estado']=='REUTILIZABLE' and a2['codigo_documental'] is None and a2['codigo_interno']==by[i]['codigo_interno_adoptado'];n+=1
for (person,year),x in aliases.items():
 assert dst.codigos_mu(persona=person,anio=year)['codigos']==[x['codigo_recuperable']]
 dest=[{'codcli':y['CODCLI'],'plan':y['plan'],'anio':year,'periodo':y['periodo_nativo'],'corte':'T'+str(y['periodo_nativo']),'fuente_periodo':'PROMEDIOS_12166 REGIMEN TRIMESTRAL, ANO/PERIODO'} for y in selected if y['persona']==person and str(y['periodo_nativo']) in ('2','3')]
 assert len(dest)==2
 got=dst.seguir_cohorte(persona=person,anio_mu=year,codigo_origen=x['codigo_recuperable'],destinos=dest);assert all(z['codigo_contexto_destino']==x['codigo_recuperable'] for z in got)
assert n==14;src.close();dst.close()
for f,h in inputs.items():assert sha256(f)==h
assert A.read_bytes()==ab
qa={'resultado':'OK','consultas_comparadas':24774,'cierres_exactos':14,'restantes_identicos':24760,'codigo_documental_inalterado':True,'dimensiones_originales_inalteradas':True,'nuevos_enlaces_identidad_mu':2,'fuentes_conservadas':True,'seguimiento_puente_P_T2_T3':True,'sin_cambio_denominadores':True}
dump(O/'QA_CIERRE.json',qa);dump(V/'ALERTA_CAMBIO.json',{'responsable':'Alexi','fecha_hora':now.isoformat(),'anterior':active,'nuevo_sha256':sha256(V/'descriptor.json'),'cambios':14,'clasificacion':'D interna; documental intacto','sin_cambio_denominadores':True})
# Promover después del QA, con reemplazo atómico y copia anterior preservada.
newactive=dict(active,descriptor=str((V/'descriptor.json').relative_to(R)),sha256=sha256(V/'descriptor.json'));tmp=A.with_suffix('.tmp');dump(tmp,newactive);os.replace(tmp,A)
s=DiccionarioSiesSeguimiento();assert s.edicion==version;s.close()
dump(O/'CONFIG.json',{'output':str(O),'privado':str(P),'edicion':str(V),'revision_previa':str(prev),'HEAD_antes':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()})
dump(O/'RESULTADOS_CIERRE.json',{'cierres':14,'restantes_foco':21,'pendientes_internos':counts['pendientes_internos'],'pendientes_documentales':counts['pendientes_documentales']})
print(json.dumps({'output':str(O),'privado':str(P),'version':version,'qa':qa,'resumen':counts['pendientes_internos']},ensure_ascii=False))

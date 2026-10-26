"""Aplica exclusivamente cinco cierres internos autorizados; fuentes inalteradas."""
import copy,datetime,hashlib,json,os,subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('cierre_cinco_v1_programacion_'+stamp);Q=P/('cierre_cinco_v1_programacion_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir(mode=0o700);H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(p,h=None):
 p=Path(p);p=p if p.is_absolute() else R/p;a=sha(p);assert h is None or a==h,str(p);H[str(p)]=a;return p

def load(p,h=None):return json.loads(src(p,h).read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def git():return {k:subprocess.check_output(['git','-C',str(R),*args],text=True).strip() for k,args in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('remotos',['remote','-v']),('status',['status','--short'])]}
def apply(rows,changes):
 out=copy.deepcopy(rows);idx={x['observacion_id']:x for x in out};assert len(idx)==len(out)
 for op in changes:
  x=idx[op['observacion_id']]
  if x==op['estado_despues']:continue
  if x!=op['estado_antes']:raise ValueError('Estado anterior incompatible')
  x.clear();x.update(copy.deepcopy(op['estado_despues']))
 return out

def counts(rows,key):
 a=[x for x in rows if not x[key]];return {'observaciones':len(a),'personas':len({x['persona'] for x in a})}

gb=git();dump(O/'GIT_ANTES.json',gb)
prev=R/'outputs/cierre_siete_v1_programacion_20261023_105611';pm=load(prev/'MANIFEST.json')
for p,h in pm['fuentes_hashes'].items():src(p,h)
for p,h in pm['salidas_hashes'].items():src(prev/p,h)
for p,h in pm['privados_hashes'].items():src(Path(pm['privado'])/p,h)
assert pm['qa']['estado']=='OK_CON_ADVERTENCIAS'
old=load(Path(pm['privado'])/'ADJUDICACIONES_ACUMULADAS.json',pm['privados_hashes']['ADJUDICACIONES_ACUMULADAS.json'])
five=load(Path(pm['privado'])/'CINCO_CRITERIO_COMPLEMENTARIO.json',pm['privados_hashes']['CINCO_CRITERIO_COMPLEMENTARIO.json'])
criterion=load(prev/'CRITERIO_COMPLEMENTARIO_PROPUESTO.json',pm['salidas_hashes']['CRITERIO_COMPLEMENTARIO_PROPUESTO.json'])
bp=P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json';base=load(bp,H[str(bp)])
before=apply(base,old['adjudicaciones']);idx={x['observacion_id']:x for x in before}
assert len(five)==5 and len({x['observacion']['persona'] for x in five})==3
assert len(old['adjudicaciones'])==14 and all(x['criterio_evaluado']['cumple_criterio_propuesto'] and all(x['criterio_evaluado']['controles'].values()) for x in five)
CODE='I162S2C57J4V1';rid='PROGRAMACION_CINCO_V1_CRITERIO_COMPLEMENTARIO_APROBADO_20261023'
decision={'regla_id':rid,'responsable_decision':'Alexi','ejecutor':'Codex','fecha_hora':now.isoformat(),'clasificacion':'D decisión aprobada; B evidencia; C aplicación; E atribución documental',
 'autorizacion_textual':'Apruebo el criterio complementario. Cierra las otras cinco observaciones como V1 por correspondencia interna, dejando pendiente la atribución documental, sin cambiar las bases ni los denominadores.',
 'alcance':'Cinco observaciones de tres personas, Programación 2024: tres de continuidad del plan anterior y dos de actualización con actividad en ambos planes.',
 'codigo_interno_adoptado':CODE,'criterio':'Código personal MU2024 + actividad aprobada exacta de CODCLI/plan/año/período + respaldo histórico de continuidad o actualización; conservar régimen y no inventar matrícula posterior ni día administrativo.',
 'antecedente':str(prev/'MANIFEST.json'),'sha256_antecedente':H[str(prev/'MANIFEST.json')],
 'criterio_original':str(prev/'CRITERIO_COMPLEMENTARIO_PROPUESTO.json'),'sha256_criterio_original':H[str(prev/'CRITERIO_COMPLEMENTARIO_PROPUESTO.json')],
 'alerta':'Cierre interno acotado a cinco observaciones. No equivalencia universal, no envío/aceptación SIES ni fecha efectiva probada. No cerrar otras homologaciones por asociación.',
 'reversion':'Omitir únicamente estas cinco adjudicaciones; conservar las catorce operaciones anteriores.'}
changes=[]
for z in five:
 o=z['observacion'];b=idx[o['observacion_id']];assert b==z['estado_antes']==z['estado_despues_vigente'] and not b['codigo_interno_adoptado'] and z['codigo_propuesto']==CODE
 y=copy.deepcopy(b);y.update(codigo_interno_adoptado=CODE,estado_interno='CORRESPONDENCIA_INTERNA_APROBADA',regla=rid,clasificacion='D correspondencia interna aprobada; B evidencia; C aplicación; E atribución documental',requisito_pendiente='Atribución documental al expediente/período y fecha administrativa efectiva pendientes. Correspondencia interna aprobada solo para esta observación; no acredita envío/aceptación SIES ni equivalencia universal de planes.')
 changes.append({'observacion_id':o['observacion_id'],'estado_antes':b,'estado_despues':y,'regla_id':rid,'via_evidencia':z['criterio_evaluado']['via']})
after=apply(before,changes)
assert counts(before,'codigo_interno_adoptado')=={'observaciones':3081,'personas':1750}
assert counts(after,'codigo_interno_adoptado')=={'observaciones':3076,'personas':1750}
assert counts(after,'codigo_documental_atribuible')=={'observaciones':3213,'personas':1838}
reverse=[{'observacion_id':x['observacion_id'],'estado_antes':x['estado_despues'],'estado_despues':x['estado_antes']} for x in changes]
allowed={'codigo_interno_adoptado','estado_interno','regla','clasificacion','requisito_pendiente'}
qa={'estado':'OK_CON_ADVERTENCIAS','cinco_cambios_exactos':sum(a!=b for a,b in zip(before,after))==5,'solo_campos_autorizados':all({k for k in a if a[k]!=b[k]}<=allowed for a,b in zip(before,after)), 'documental_intacto':all(a['codigo_documental_atribuible']==b['codigo_documental_atribuible'] and a['estado_documental']==b['estado_documental'] for a,b in zip(before,after)),'idempotencia':apply(after,changes)==after,'reversion':apply(after,reverse)==before,'universo_intacto':len(after)==24774 and len({x['persona'] for x in after})==5901,'advertencias':['Atribución documental al expediente/período sigue pendiente.','Fecha efectiva administrativa no acreditada; no es regla universal.']}
bad=copy.deepcopy(before);next(x for x in bad if x['observacion_id']==changes[0]['observacion_id'])['estado_interno']='INCOMPATIBLE'
try:apply(bad,changes)
except ValueError:qa['estado_incompatible_rechazado']=True
else:qa['estado_incompatible_rechazado']=False
assert all(v for v in qa.values() if isinstance(v,bool))
acc={'orden_aplicacion':old['orden_aplicacion']+[rid],'adjudicaciones':old['adjudicaciones']+changes}
assert len(acc['adjudicaciones'])==19 and apply(base,acc['adjudicaciones'])==after
approved=copy.deepcopy(criterion);approved.update(id=rid,estado='APROBADO_APLICADO_ALCANCE_CINCO_OBSERVACIONES',clasificacion='D decisión aprobada; B evidencia; C aplicación; E atribución documental y fecha efectiva',responsable_decision='Alexi',fecha_hora_aprobacion_registrada=now.isoformat(),criterio_previo_id=criterion['id'],resultado_revision={'observaciones_que_cumplen':5,'personas':3,'codigo_interno_adoptado':CODE,'cierres_aplicados':5})
dump(Q/'ADJUDICACIONES_CINCO_V1.json',{'decision':decision,'adjudicaciones':changes})
dump(Q/'ADJUDICACIONES_ACUMULADAS.json',acc);dump(Q/'CINCO_DESPUES.json',[x['estado_despues'] for x in changes])
dump(Q/'EVIDENCIAS_CINCO_APROBADAS.json',five)
dump(O/'DECISION_APROBADA.json',decision);dump(O/'CRITERIO_COMPLEMENTARIO_APROBADO.json',approved)
result={'clasificacion':'D cierre; B respaldo; C conteos; E atribución documental','cierres_internos_aplicados':5,'personas_del_cierre':3,'codigo':CODE,'antes':counts(before,'codigo_interno_adoptado'),'despues':counts(after,'codigo_interno_adoptado'),'documental':counts(after,'codigo_documental_atribuible'),'bloque_programacion_con_aprobacion':{'observaciones':12,'personas':7,'cerradas_internamente':12,'pendientes_documentales':12},'universo_conservado':{'personas':5901,'expedientes_aprobados':6622,'observaciones':24774},'operaciones_acumuladas':19,'asignaciones_acumuladas':18,'clasificaciones_sin_version_acumuladas':1}
# Explicitly verify the combined block (prior seven + these five), not just counts.
block=old['adjudicaciones'][-7:]+changes;ai={x['observacion_id']:x for x in after}
assert len({x['observacion_id'] for x in block})==12 and len({ai[x['observacion_id']]['persona'] for x in block})==7
assert all(ai[x['observacion_id']]['codigo_interno_adoptado']==CODE and not ai[x['observacion_id']]['codigo_documental_atribuible'] for x in block)
qa['doce_programacion_cerradas_internamente_documental_pendiente']=True
dump(O/'RESULTADOS.json',result)
(O/'INFORME.md').write_text('''# Cierre interno aprobado de cinco observaciones de Programación

**D:** Alexi aprobó el criterio complementario y se aplicó únicamente a sus cinco
observaciones de tres personas como **I162S2C57J4V1**, por correspondencia interna.
La decisión conserva autorización textual, responsable, fecha/hora, alcance, alerta
y reversión en DECISION_APROBADA.json. No es equivalencia universal de planes.

**B/C:** tres observaciones tienen continuidad en TPAREOL20231 y dos corresponden
a una actualización con actividad en TPAREOL20231 y TPAS20241. El respaldo combina
código personal MU2024, aprobación exacta por CODCLI/plan/año/período y evidencia
histórica de continuidad o actualización. Se verificaron los hashes de la revisión
aprobada; no se inventan matrículas posteriores, fechas administrativas ni se
confunden bimestres y trimestres. La propuesta anterior se conserva intacta; su
nueva versión aprobada está en CRITERIO_COMPLEMENTARIO_APROBADO.json.

| Indicador C | Antes | Después |
|---|---:|---:|
| Observaciones internas pendientes | 3.081 | 3.076 |
| Personas con al menos un pendiente interno | 1.750 | 1.750 |
| Observaciones documentales pendientes | 3.213 | 3.213 |
| Personas con pendiente documental | 1.838 | 1.838 |

**C:** junto con las siete anteriores, quedan **12 observaciones de siete personas
cerradas internamente como V1** en este bloque de Programación con aprobación.
**E:** las doce conservan pendiente la atribución documental al expediente/período.
No se acredita envío/aceptación SIES ni día efectivo administrativo. Las personas
conservan otros pendientes; no se declara resuelta una persona por estas observaciones.

No se modifican las bases, los libros, el motor, los catálogos operativos, los
numeradores/denominadores ni las tasas. Universo aprobado conservado: 5.901 personas,
6.622 expedientes y 24.774 observaciones. No se cierran otras homologaciones por
asociación ni se convierte una observación de actividad en matrícula adicional.

QA **OK_CON_ADVERTENCIAS**: cinco cambios internos exactos, cero documentales o
ajenos al alcance; idempotencia, reversión y rechazo de estado anterior incompatible;
conservación de fuentes por hash y rama/HEAD. La advertencia corresponde al pendiente
documental y a la fecha administrativa no acreditada, no a un fallo de los controles.

La capa acumulada privada contiene 19 operaciones: 18 asignaciones y la clasificación
TCRE sin versión. MANIFEST.json registra entradas, salidas, hashes y la ubicación
privada fuera de Git; los identificadores no están en el informe agregado. Reconstruir
sobre la base fijada por hash y aplicar las operaciones en orden, validando antes/después.

Trabajo local reproducible, sin commit/push ni publicación en GitHub. Siguiente paso:
continuar con los demás pendientes, manteniendo este bloque cerrado internamente y
sin reutilizar el criterio fuera de su alcance autorizado.
''')
(O/'CHECKPOINT.md').write_text('# Reanudación\n\nCinco observaciones complementarias de Programación cerradas por aprobación de Alexi como I162S2C57J4V1. Bloque de aprobación completo: 12 observaciones/7 personas cerradas internamente; documental sigue pendiente en las 12. Global interno 3.076 observaciones/1.750 personas; documental 3.213/1.838. Reconstruir desde OBSERVACIONES_PRIVADAS de 20261023_004044 y ADJUDICACIONES_ACUMULADAS.json privado de esta ejecución (19 operaciones: 18 asignaciones y clasificación TCRE sin versión). Reversión selectiva omite solo las últimas cinco. Fuentes, libros, bases, motor y denominadores intactos. No propagar a otras homologaciones/planes. Sin commit/push.\n')
for p in [Path(__file__),R/'docs/ESPECIFICACION_CIERRE_CINCO_V1_PROGRAMACION_20261023.md']:src(p)
qa['fuentes_intactas']=all(sha(p)==h for p,h in H.items());qa['privados_0600']=all((f.stat().st_mode & 0o077)==0 for f in Q.iterdir());assert qa['fuentes_intactas'] and qa['privados_0600']
ga=git();assert (gb['rama'],gb['HEAD'])==(ga['rama'],ga['HEAD']);dump(O/'GIT_DESPUES.json',ga);dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',H)
secrets={x['persona'] for x in base}|{x['CODCLI'] for x in base}
for f in O.iterdir():assert not any(k and k in f.read_text() for k in secrets),str(f)
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'fuentes_hashes':H,'salidas_hashes':{f.name:sha(f) for f in O.iterdir()},'privado':str(Q),'privados_hashes':{f.name:sha(f) for f in Q.iterdir()},'resultado':result,'qa':qa,'rama':ga['rama'],'HEAD':ga['HEAD'],'commit_push':False,'estado_publicacion':'Local no publicado'})
print(json.dumps({'salida':str(O),'resultado':result,'QA':qa['estado']},ensure_ascii=False))

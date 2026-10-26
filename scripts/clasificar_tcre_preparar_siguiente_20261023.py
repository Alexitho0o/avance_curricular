"""Clasificación autorizada sin versión; prevalidación exacta del siguiente bloque."""
import copy,collections,datetime,hashlib,json,os,subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
import openpyxl
R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
now=datetime.datetime.now(ZoneInfo('America/Santiago'));stamp=now.strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('clasificacion_tcre_siguiente_bloque_'+stamp);Q=P/('clasificacion_tcre_siguiente_bloque_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir();H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(p,h=None):
 p=Path(p);actual=sha(p);assert h is None or h==actual,str(p);H[str(p)]=actual;return p
def load(p,h=None):return json.loads(src(p,h).read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def git():return {k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]}
def apply(rows,changes):
 out=copy.deepcopy(rows);idx={x['observacion_id']:x for x in out};assert len(idx)==len(out)
 for c in changes:
  x=idx[c['observacion_id']]
  if x==c['estado_despues']:continue
  if x!=c['estado_antes']:raise ValueError('Estado incompatible')
  x.clear();x.update(copy.deepcopy(c['estado_despues']))
 return out
def counts(rows,field):
 a=[x for x in rows if not x[field]];return {'observaciones':len(a),'personas':len({x['persona'] for x in a})}
gb=git();dump(O/'GIT_ANTES.json',gb)
prev=R/'outputs/cierre_dos_v2_homologaciones_20261023_091509';pm=load(prev/'MANIFEST.json')
hist=R/'outputs/historico_rechazo_tcre_20261023_093127';hm=load(hist/'MANIFEST.json')
for name,h in hm['salidas_hashes'].items():src(hist/name,h)
for name,h in hm['privados_hashes'].items():src(Path(hm['privado'])/name,h)
for name,h in hm['fuentes_hashes'].items():src(name,h)
old=load(Path(pm['privado'])/'ADJUDICACIONES_ACUMULADAS.json',pm['privados_hashes']['ADJUDICACIONES_ACUMULADAS.json'])
base=P/'reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json';obs=load(base,H[str(base)])
before=apply(obs,old['adjudicaciones'])
third=load(Path(pm['privado'])/'REVISION_HOMOLOGACIONES.json',pm['privados_hashes']['REVISION_HOMOLOGACIONES.json'])['observacion']
actual=next(x for x in before if x['observacion_id']==third['observacion_id']);assert actual==third
decision={'regla_id':'TCRE20241_HOMOLOGACION_PLAN_RECHAZADO_20261023',
 'responsable_decision':'Alexi','ejecutor':'Codex','fecha_hora':now.isoformat(),
 'autorizacion_textual':'Entonces deja esa tercera observación como homologación en un plan rechazado, sin forzar V2, y continuemos con los demás pendientes. ¿Qué grupo podemos resolver ahora sin cambiar las bases ni los denominadores?',
 'clasificacion':'D decisión; B evidencia; C registro; E versión y atribución documental',
 'alcance':'Solo la observación TCRE20241/2024/trimestre 1 revisada',
 'etiqueta':'Homologación en plan rechazado','codigo_interno_adoptado':'',
 'no_equivale_a':'Cierre de versión, exclusión del universo, cursado o retención',
 'alerta':'Clasificación autorizada acotada; no heredar V2 del expediente anterior ni generalizar a otros reconocimientos.',
 'antecedente':str(hist/'MANIFEST.json'),'sha256_antecedente':H[str(hist/'MANIFEST.json')],
 'reversion':'Omitir esta clasificación y conservar las seis adjudicaciones internas anteriores.'}
y=copy.deepcopy(third);y.update(estado_interno='HOMOLOGACION_EN_PLAN_RECHAZADO_SIN_VERSION',regla=decision['regla_id'],clasificacion='B/C/D; E versión del expediente y atribución documental',requisito_pendiente='Homologación en plan rechazado; no forzar V2 ni contar cursado. Versión del expediente destino y atribución documental permanecen pendientes; fecha efectiva del rechazo no acreditada.')
change={'observacion_id':third['observacion_id'],'estado_antes':third,'estado_despues':y,'regla_id':decision['regla_id']}
after=apply(before,[change]);pending=[x for x in after if not x['codigo_interno_adoptado']]
group=[x for x in pending if x['estado_documental']=='CONTRADICCION_O_ATRIBUCION_MULTIPLE' and x['observacion_id']!=third['observacion_id']]
assert len(group)==79 and len({x['persona'] for x in group})==20 and all(len(x['codigos_anuales_documentados'])==1 for x in group)
focus=[x for x in group if x['carrera'] in ['TPAREOL','TPAS'] and x['ano']=='2024']
assert len(focus)==24 and len({x['persona'] for x in focus})==8
assert {c for x in focus for c in x['codigos_anuales_documentados']}=={'I162S2C57J4V1'}
# Exact reread of all source rows supporting these observations; no adoption.
requests=collections.defaultdict(list)
for x in focus:
 for e in x['fuentes_promedios']:requests[(e['fuente'],e['hoja'])].append((e['fila'],x))
activity=collections.defaultdict(list)
for (path,sheet),items in requests.items():
 src(path,H[path]);lookup=collections.defaultdict(list)
 for rn,x in items:lookup[int(rn)].append(x)
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values);head=next(it);found=set()
 for rn,row in enumerate(it,2):
  if rn not in lookup:continue
  d=dict(zip(head,row));found.add(rn)
  for x in lookup[rn]:
   assert val(d['RUT']).replace('.','')+'-'+val(d['DIG']).upper()==x['persona']
   assert all(val(d[k])==x[v] for k,v in [('CODCLI','CODCLI'),('CODCARR','carrera'),('PLAN_DE_ESTUDIO','plan'),('ANO','ano'),('PERIODO','periodo')])
   activity[x['observacion_id']].append({'fuente':path,'hoja':sheet,'fila':rn,**{k:val(d.get(k)) for k in ['CODCLI','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','REGIMEN','CODRAMO','ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','ESTADO_ACADEMICO']}})
 w.close();assert found==set(lookup)
# Current DA confirms which status to investigate; it is not a dated historic event.
da=Path.home()/'Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx';src(da,H[str(da)])
owners={x['CODCLI']:x['persona'] for x in focus};da_rows=[]
w=openpyxl.load_workbook(da,read_only=True,data_only=True);it=iter(w['Hoja1'].values);head=next(it)
for rn,row in enumerate(it,2):
 d=dict(zip(head,row));cc=val(d.get('CODCLI'))
 if cc not in owners:continue
 assert val(d['RUT']).upper().replace('.','')==owners[cc]
 da_rows.append({'fuente':str(da),'hoja':'Hoja1','fila':rn,**{k:val(d.get(k)) for k in ['CODCLI','CODCARPR','JORNADA','SEDE','ANOMATRICULA','PERIODOMATRICULA','FECHAMATRICULA','ESTADOACADEMICO','SITUACION']},'limite':'Estado de respaldo sin historia fechada; no atribuir al período analizado automáticamente.'})
w.close()
profile=[]
for x in focus:
 a=activity[x['observacion_id']]
 rec=lambda r:r['CONVALIDADO']=='S' or r['DESCRIPCION_ESTADO'] in ['HOMOLOGADO','CONVALIDACION']
 kind='SOLO_RECONOCIMIENTOS' if all(rec(r) for r in a) else 'CON_APROBACION_SIN_RECONOCIMIENTO' if any(r['DESCRIPCION_ESTADO']=='APROBADO' and not rec(r) for r in a) else 'OTRA_ACTIVIDAD_SIN_APROBACION'
 profile.append({'observacion':x,'filas_releidas':a,'tipo_evidencia':kind,'datos_alumnos':[r for r in da_rows if r['CODCLI']==x['CODCLI']],'codigo_anual':x['codigos_anuales_documentados'][0],'codigo_nuevo_adoptado':''})
result={'clasificacion':'B evidencia; C conteos; D clasificación; E asignaciones pendientes',
 'clasificaciones_nuevas':1,'versiones_nuevas_adoptadas':0,
 'internos':counts(after,'codigo_interno_adoptado'),'documentales':counts(after,'codigo_documental_atribuible'),
 'siguiente_bloque':{'observaciones':len(group),'personas':len({x['persona'] for x in group})},
 'primer_grupo':{'carreras':['TPAREOL','TPAS'],'planes':['TPAREOL20231','TPAS20241'],'ano':2024,'codigo_anual':'I162S2C57J4V1','observaciones':len(focus),'personas':len({x['persona'] for x in focus}),'tipos_evidencia':dict(collections.Counter(x['tipo_evidencia'] for x in profile)),'expedientes_en_foco':len(owners),'expedientes_DA_localizados':len({x['CODCLI'] for x in da_rows}),'estados_DA_por_expediente':dict(collections.Counter(x['ESTADOACADEMICO']+' / '+x['SITUACION'] for x in da_rows))},
 'universo_conservado':{'personas':5901,'expedientes_aprobados':6622,'observaciones':24774},'tasas_retencion_modificadas':False}
assert result['internos']=={'observaciones':3088,'personas':1750} and result['documentales']=={'observaciones':3213,'personas':1838}
allowed={'estado_interno','regla','clasificacion','requisito_pendiente'}
qa={'estado':'OK_CON_ADVERTENCIAS','un_cambio_clasificatorio':sum(a!=b for a,b in zip(before,after))==1,
 'solo_campos_autorizados':all({k for k in a if a[k]!=b[k]}<=allowed for a,b in zip(before,after)),
 'idempotencia':apply(after,[change])==after,'universo_inalterado':len(after)==24774 and len({x['persona'] for x in after})==5901,
 '24_observaciones_releidas':len(activity)==24,'sin_adopcion_siguiente_grupo':all(not x['codigo_nuevo_adoptado'] for x in profile),
 'advertencia':'Clasificar no cierra versión. El código anual del siguiente grupo no está aún atribuido a cada expediente/período.'}
bad=copy.deepcopy(before);next(x for x in bad if x['observacion_id']==third['observacion_id'])['estado_interno']='INCOMPATIBLE'
try:apply(bad,[change])
except ValueError:qa['estado_incompatible_rechazado']=True
else:qa['estado_incompatible_rechazado']=False
assert all(v for v in qa.values() if isinstance(v,bool))
dump(Q/'CLASIFICACION_TCRE.json',{'decision':decision,'adjudicaciones':[change]})
dump(Q/'ADJUDICACIONES_ACUMULADAS.json',{'orden_aplicacion':old['orden_aplicacion']+[decision['regla_id']],'adjudicaciones':old['adjudicaciones']+[change]})
dump(Q/'TCRE_DESPUES.json',y);dump(Q/'SIGUIENTE_BLOQUE_79.json',group);dump(Q/'PROGRAMACION_24_PREVALIDACION.json',profile)
dump(O/'DECISION_APROBADA.json',decision);dump(O/'RESULTADOS.json',result)
src(__file__);src(R/'docs/ESPECIFICACION_CLASIFICACION_TCRE_Y_SIGUIENTE_BLOQUE_20261023.md')
qa['fuentes_intactas']=all(sha(p)==h for p,h in H.items());assert qa['fuentes_intactas'];dump(O/'QA.json',qa)
report=f'''# Clasificación TCRE y siguiente grupo de trabajo

## Decisión aplicada D / registro C

La tercera observación TCRE20241/2024/1 queda **Homologación en plan rechazado**,
sin código interno y con atribución documental pendiente. No se fuerza V2, no se
elimina la observación y no se cuenta como cursado o retención. El rechazo y la
continuidad del plan anterior tienen respaldo B; su fecha efectiva sigue E.
Autorización de Alexi registrada {now.isoformat()}. La clasificación no reduce
pendientes de versión: **3.088 observaciones / 1.750 personas** internas;
documentales **3.213 / 1.838**, sin cambios. Se conservan seis cierres anteriores.

## Siguiente bloque — C, asignación por resolver E

Hay **79 observaciones de 20 personas** con código anual único localizado y
atribución al expediente sin resolver, excluyendo la observación TCRE ya clasificada.
No son necesariamente contradicciones de códigos: debe atribuirse el código anual
a cada expediente y período. No se trasladan códigos de otra carrera o año.

Primero: **Programación y Análisis de Sistemas, 2024**, TPAREOL20231/TPAS20241:
**24 observaciones de 8 personas**, todas con código anual **I162S2C57J4V1**.
Se releyeron sus filas exactas de PROMEDIOS, corroborando identidad, CODCLI,
plan, año y período. El perfil no adopta ninguna versión nueva.

| Evidencia del período | Observaciones |
|---|---:|
| Al menos una aprobación sin reconocimiento | {result['primer_grupo']['tipos_evidencia'].get('CON_APROBACION_SIN_RECONOCIMIENTO',0)} |
| Solo homologación/convalidación | {result['primer_grupo']['tipos_evidencia'].get('SOLO_RECONOCIMIENTOS',0)} |
| Otra actividad, sin aprobación corroborada | {result['primer_grupo']['tipos_evidencia'].get('OTRA_ACTIVIDAD_SIN_APROBACION',0)} |

Las categorías son exclusivas y suman 24. No significan 24 personas ni 24 cierres
seguros. Reprobar o no tener una aprobación no determina por sí solo la versión.
DatosAlumnos localiza {result['primer_grupo']['expedientes_DA_localizados']} de {len(owners)} expedientes del foco;
sus estados se conservan en el detalle privado, sin extrapolarlos al pasado.

El siguiente trabajo concreto es contrastar la trayectoria 2023–2025 y los respaldos
fechados de cada uno de esos ocho casos: separar actividad del plan anterior,
actividad del nuevo y reconocimientos de actualizaciones rechazadas. Empezar por
las 12 observaciones con aprobación; revisar las otras sin descartarlas.
El número efectivamente cerrable sigue E hasta atribuir expediente/período.

## Gobernanza y reanudación

Clasificación materializada localmente en TCRE_DESPUES.json; estados antes/después
y siete operaciones acumuladas (seis asignaciones previas + una clasificación)
en ADJUDICACIONES_ACUMULADAS.json, fuera de Git. Reconstruir sobre la base
diagnóstica fijada por hash; verificar estado anterior y repetir sin duplicar cambios.
Reversión: omitir únicamente la última clasificación.

QA OK_CON_ADVERTENCIAS: exactamente un cambio clasificatorio, ningún código ni
atribución documental modificado, 24 filas de observaciones cotejadas con fuentes,
contadores y universo conservados, idempotencia y rechazo de estado incompatible.
Universo: 5.901 personas / 6.622 expedientes / 24.774 observaciones. No se modifican
bases, denominadores, tasas, libros ni motor. Registro local no publicado.
Sin commit/push. Rama/HEAD conservados en los registros Git adjuntos.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('# Reanudación\n\nTCRE20241/2024/1 clasificado por autorización como Homologación en plan rechazado, código vacío. No reabrir como candidato automático V2; documental/versión siguen E. Estado vigente se reproduce con siete operaciones acumuladas privadas. Pendientes internos 3.088/1.750, documentales 3.213/1.838. Siguiente bloque 79 observaciones/20 personas con código anual único sin atribución. Primer grupo ya prevalidado: Programación 2024, 24 observaciones/8 personas, TPAREOL20231 y TPAS20241, código anual V1 I162S2C57J4V1. Revisar cronología exacta por persona y período antes de proponer cierres. Sin commit/push.\n')
ga=git();assert gb['rama']==ga['rama'] and gb['HEAD']==ga['HEAD'];dump(O/'GIT_DESPUES.json',ga);dump(O/'FUENTES_HASHES.json',H)
secrets={x['persona'] for x in obs}|{x['CODCLI'] for x in obs}
for f in O.iterdir():
 text=f.read_text();assert not any(k and k in text for k in secrets),str(f)
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'fuentes_hashes':H,'salidas_hashes':{f.name:sha(f) for f in O.iterdir()},'privado':str(Q),'privados_hashes':{f.name:sha(f) for f in Q.iterdir()},'resultado':result,'qa':qa,'rama':ga['rama'],'HEAD':ga['HEAD'],'commit_push':False,'estado_publicacion':'Local no publicado'})
print(json.dumps({'salida':str(O),'resultado':result,'QA':qa['estado']},ensure_ascii=False))

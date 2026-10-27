"""Cierres D y reconocimientos B/C: fuentes intactas y detalle individual privado."""
import os, json, hashlib, subprocess, collections, re, unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import openpyxl
OUT=Path(__file__).resolve().parent; REPO=OUT.parents[1]
PRIV=Path('/Users/alexi/.local/share/ipss/cierre_interno_iinf_reconocimientos_20261026')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for part in iter(lambda:f.read(1048576),b''):h.update(part)
 return h.hexdigest()
def normalize(v):
 if v is None:return ''
 if isinstance(v,(float,int)) and v==int(v):return str(int(v))
 return str(v).strip().upper()
def git(*x):return subprocess.check_output(['git',*x],cwd=REPO,text=True).strip()
def private_write(p,content):
 flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
 fd=os.open(p,flags,0o600)
 with os.fdopen(fd,'w') as f:f.write(content)
HEAD=git('rev-parse','HEAD');branch=git('branch','--show-current'); status_before=git('status','--short','--untracked-files=no')
tracked={x:digest(REPO/x) for x in git('diff','--name-only').splitlines() if (REPO/x).is_file()}
rev=REPO/'outputs/evaluacion_cierres_tres_casos_21_ramos_20261026/RESULTADO.json'
review=json.loads(rev.read_text());qa=json.loads((rev.parent/'QA.json').read_text())
assert digest(rev)==qa['resultado_sha256']
for f,h in review['fuentes'].items():assert digest(REPO/f)==h
private_old=Path(review['privado_verificado']['ruta']);assert digest(private_old)==review['privado_verificado']['sha256']
cases=json.loads(private_old.read_text());info={x['caso']:x for x in cases}; proposals=review['titulaciones'];assert {x['caso'] for x in proposals}=={'C01','C02','C03'}
base=Path('/Users/alexi/.local/share/ipss').resolve();assert base.is_dir() and not any((p/'.git').exists() for p in [base,*base.parents])
PRIV.mkdir(mode=0o700,exist_ok=True);os.chmod(PRIV,0o700)
assert not any(PRIV.iterdir()), 'El destino privado ya contiene archivos; no sobrescribir.'
closed=[];private_cases=[]
for x in proposals:
 c=info[x['caso']]; selected=[]
 for src in sorted({v['fuente'] for v in c['datosalumnos']}):
  rows=[v for v in c['datosalumnos'] if v['fuente']==src];valid=[v for v in rows if v['estado']=='TITULADO' and v['situacion']=='31 - TITULADO APROBADO' and v['carrera']=='IINF']
  assert len(valid)==1;selected.append(valid[0])
 assert len({v['CODCLI'] for v in selected})==1
 cod=selected[0]['CODCLI']; contexts=[v for v in c['contextos_v11'] if v['CODCLI']==cod]
 assert {v['plan'] for v in contexts}=={'IINF20241'} and len(contexts)==4
 closed.append({'caso':x['caso'],'estado':'CERRADO_INTERNO','clasificacion':'D','plan':'IINF20241','localizadores':x['datos_alumnos'],'titulo_observado':x['titulo_observado'],'reserva':'Traza 2130 apunta al expediente anterior; atribución formal, fórmula 2130 y fecha efectiva de cambio permanecen E.'})
 private_cases.append({'caso':x['caso'],'RUT':c['RUT'],'CODCLI':cod,'plan':'IINF20241','fuentes':x['datos_alumnos']})
targets={(x['carrera'],x['plan'],x['ramo']) for x in review['ramos'] if x['reconocimiento_individual_observado']};assert len(targets)==15
prev=json.loads((REPO/'outputs/confirmacion_reconocimientos_20261026/RESULTADO_AGREGADO.json').read_text()); refs={Path(x['ruta']).name:x for x in prev['fuentes']}
root=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-InstitutoProfesionalSanSebasti*'))
folder=root/'IPSS_CONCILIACION_UMAS_SIES_BASES'/'04_UMAS_PROMEDIOSDEALUMNOS'
fields=('RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','CODRAMO','CODSECC','ESTADO','DESCRIPCION_ESTADO','RAMOEQUIV','CONVALIDADO')
byfile={};hashes={}
for name in ('PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx'):
 p=folder/name;h=digest(p);assert h==refs[name]['sha256'];hashes[name]=h
 w=openpyxl.load_workbook(p,read_only=True,data_only=True); it=w['Hoja1'].iter_rows(values_only=True);hd={normalize(v):i for i,v in enumerate(next(it)) if v is not None};assert set(fields)<=set(hd)
 eventmap=collections.defaultdict(list)
 for rn,row in enumerate(it,2):
  def v(k):return normalize(row[hd[k]]) if hd[k]<len(row) else ''
  if (v('CODCARR'),v('PLAN_DE_ESTUDIO'),v('CODRAMO')) not in targets or v('ESTADO') not in ('I','E'):continue
  body=v('RUT').replace('.','').replace(' ',''); dv=v('DIG')
  assert body.isdigit() and re.fullmatch('[0-9K]',dv) and v('CODCLI') and v('ANO') and v('PERIODO')
  key=(str(int(body))+'-'+dv,)+tuple(v(k) for k in fields[2:]);eventmap[key].append(rn)
 w.close();assert digest(p)==h;byfile[name]=eventmap
start=byfile['PROMEDIOSDEALUMNOS_7804.xlsx'];other=byfile['PROMEDIOSDEALUMNOS_12166.xlsx']
assert len(start)==21 and set(start)<=set(other)
assert len({(k[2],k[3],k[6]) for k in start})==15
private_events=[]
for k in sorted(start):
 private_events.append(dict(zip(('RUT_DV',)+fields[2:],k))|{'fuentes':{'PROMEDIOSDEALUMNOS_7804.xlsx':{'hoja':'Hoja1','filas':start[k]},'PROMEDIOSDEALUMNOS_12166.xlsx':{'hoja':'Hoja1','filas':other[k]}}})
private={'clasificacion':'B/C','alcance':'21 registros distintos en 15 pares; no se suman copias. Datos individuales solo locales.','titulaciones':private_cases,'reconocimientos':private_events,'fuentes_sha256':hashes}
private_path=PRIV/'DETALLE_CIERRE_PRIVADO.json';private_write(private_path,json.dumps(private,ensure_ascii=False,indent=2)+'\n')
time=datetime.now(ZoneInfo('America/Santiago')).isoformat()
ramos=[{'carrera':x['carrera'],'plan':x['plan'],'ramo':x['ramo'],'estado_observado':x['estados'],'registros_distintos':x['registros_reconocimiento_repetidos'],'estatus':'RECONOCIMIENTO_INDIVIDUAL_OBSERVADO','clasificacion':'B/C','equivalencia_general':'E - pendiente de acreditación de plan, origen/destino y alcance'} for x in review['ramos'] if x['reconocimiento_individual_observado']]
assert sum(x['registros_distintos'] for x in ramos)==21
out={'id':'CIERRE_IINF_15_RECONOCIMIENTOS_20261026','fecha_hora':time,'responsable_aprobacion':'Alexi, usuario del chat','autorizacion':'Apruebo cerrar los tres títulos de Informática como correspondencia interna con IINF20241. Registra también los 15 reconocimientos individuales, dejando pendientes las equivalencias generales, sin cambiar bases ni denominadores.','clasificacion_decision':'D','cierres':closed,'reconocimientos':ramos,'conteos':{'titulos_cerrados_internamente':3,'pares_con_reconocimiento_observado':15,'registros_individuales_distintos':21,'otros_pares_sin_I_E':6,'equivalencias_generales_discrepantes_pendientes':21},'privado':{'ruta':str(private_path),'sha256':digest(private_path),'fuera_de_git':True},'fuentes_sha256':hashes,'evidencia_anterior':{'ruta':str(rev),'sha256':digest(rev)},'pendientes':['E: acta formal para cada título; no bloquea cierre interno.','E: la traza 2130 elegía expediente anterior; su fórmula y el momento efectivo de migración siguen sin acreditarse.','E: equivalencias generales de los 21 pares, incluyendo origen/destino y alcance.'],'alcance':'Decisiones específicas; no modificar bases, mallas, diccionario SIES ni denominadores y no inferir aceptación oficial.'}
serialized=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
for c in cases:
 assert c['RUT'].split('-')[0] not in serialized
 for a in c['datosalumnos']:
  if a['CODCLI']:assert normalize(a['CODCLI']) not in serialized
for k in start:
 assert k[0].split('-')[0] not in serialized and k[1] not in serialized
assert all(digest(REPO/p)==h for p,h in tracked.items());assert git('rev-parse','HEAD')==HEAD
(OUT/'DECISION_Y_REGISTRO.json').write_text(serialized)
qaout={'clasificacion':'C','estado':'PASS_CIERRE_INTERNO_Y_REGISTRO','fecha_hora':time,'rama':branch,'head_antes':HEAD,'head_despues':git('rev-parse','HEAD'),'tres_cierres_validados':True,'conteo_reconocimientos':{'pares':15,'registros':21,'repetidos_entre_fuentes':21},'fuentes_hash_verificado_antes_despues':True,'bases_denominadores_y_cambios_ajenos_conservados':True,'detalle_fuera_de_git':True,'permisos_privados':oct(private_path.stat().st_mode & 0o777),'sin_identificadores_en_decision':True,'status_tracked_conservado':git('status','--short','--untracked-files=no')==status_before,'decision_sha256':digest(OUT/'DECISION_Y_REGISTRO.json'),'pendiente':'Acta y atribución formal, fórmula 2130 y equivalencias generales no acreditadas; no se prueba validez general.'}
(OUT/'QA.json').write_text(json.dumps(qaout,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qaout,ensure_ascii=False))

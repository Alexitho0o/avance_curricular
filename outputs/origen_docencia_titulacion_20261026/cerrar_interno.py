"""Registra exclusivamente el cierre interno autorizado; fuentes y motores intactos."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,io,subprocess,re
import openpyxl
OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=REPO,text=True).strip()
def n(v):
 if isinstance(v,float) and v.is_integer():v=int(v)
 return str(v or '').strip().upper()
def doc(v):return re.sub(r'[.\s-]','',n(v))
def wb(p):return openpyxl.load_workbook(io.BytesIO(p.read_bytes()),read_only=True,data_only=True)
head=git('rev-parse','HEAD');branch=git('branch','--show-current')
tracked=git('diff','--name-only').splitlines();protected={f:sha(REPO/f) for f in tracked if (REPO/f).is_file()}
cs=json.loads(Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json').read_text())
c=next(c for c in cs if any(x['carrera']=='TCRE' for x in c['contextos_v11']))
body,dv=c['RUT'].split('-');cods={n(x['CODCLI']) for x in c['datosalumnos'] if x['CODCLI']}
s=json.loads((OUT/'SELECCION_POSTERIOR.json').read_text());r=json.loads((OUT/'RESULTADOS.json').read_text());qa=json.loads((OUT/'QA.json').read_text())
for name,h in qa['archivos'].items():assert sha(OUT/name)==h,(name,'evidencia modificada')
source=next(x for x in r if Path(x['ruta']).name=='Informe de Titulados 2025_vf.xlsx')
paths={source['ruta']:source['sha256'],s['fuente']:s['sha256'],s['respaldo_plan']['ruta']:s['respaldo_plan']['sha256']}
for p,h in paths.items():assert sha(Path(p))==h
w=wb(Path(source['ruta']));it=w['Hoja1'].values;hs=[n(x) for x in next(it)];hits=[]
for row in it:
 if n(row[hs.index('NUM_DOCUMENTO')])==body and n(row[hs.index('DV')])==dv:hits.append(row)
assert len(hits)==1
assert hits[0][hs.index('FECHA_OBT_TIT_GRA')].date().isoformat()=='2025-07-24'
assert 'CONECTIVIDAD Y REDES' in n(hits[0][hs.index('NOMBRE_TITULO')]);w.close()
w=wb(Path(s['fuente']));ds=w['DATOS ALUMNOS'];it=ds.values;hs=[n(x) for x in next(it)];records=[]
for rn,row in enumerate(it,2):
 if n(row[hs.index('CODCLI')]) in cods:
  assert doc(row[hs.index('RUT')])==body+dv
  records.append((rn,{k:row[i] for i,k in enumerate(hs)}))
assert len(records)==3
chosen=[(rn,row) for rn,row in records if n(row['ESTADOACADEMICO'])=='TITULADO']
assert len(chosen)==1
rn,row=chosen[0];assert n(row['CODCARPR'])=='TCRE' and rn==s['fila_seleccionada_datos_alumnos']
assert n(row['SITUACION'])=='31 - TITULADO APROBADO';codcli=n(row['CODCLI'])
assert w['Participacion_TIT'][f"AA{s['fila_participacion']}"].value==rn
w.close()
w=wb(Path(s['respaldo_plan']['ruta']));it=w['Hoja1'].values;hs=[n(x) for x in next(it)];plans=set();count=0
for row in it:
 if n(row[hs.index('CODCLI')])==codcli:
  assert n(row[hs.index('RUT')])==body and n(row[hs.index('DIG')])==dv
  plans.add(n(row[hs.index('PLAN_DE_ESTUDIO')]));count+=1
w.close();assert plans=={'TCRE20241'} and count==26
stamp=datetime.now(ZoneInfo('America/Santiago')).isoformat()
decision={'id':'CIERRE_INTERNO_TITULO_TCRE20241_20261026','clasificacion':'D','estado':'CERRADO_INTERNO','responsable_aprobacion':'Alexi, usuario de este chat','registro_fecha_hora':stamp,
'autorizacion':'Revisa si esta cadena permite cerrar internamente el vínculo del título con el CODCLI de TCRE y el plan TCRE20241, dejando pendiente el acta formal, ya que el actano es necesaria asi que dalo por terminado si funciona , sin cambiar las bases ni los denominadores.',
'alcance':'Solo el caso de titulación del 24-07-2025 examinado; no regla general de atribución de títulos.',
'vinculo_adoptado':{'fecha_titulo':'2025-07-24','titulo':'TÉCNICO EN CONECTIVIDAD Y REDES','carrera_umas':'TCRE','plan':'TCRE20241','codcli':'Resolver en fuente privada por hash, hoja DATOS ALUMNOS, columna CODCLI, fila 7174; identificador no publicado.'},
'criterio':'Documento y DV concordantes; único expediente TITULADO entre los tres del caso, seleccionado por fórmula posterior; su CODCLI exacto tiene un único plan observado en 26 filas de PROMEDIOS. Se acepta la cadena como correspondencia interna por autorización explícita.',
'evidencias':{'clasificacion':'B/C','fuentes_sha256':paths,'docencia':{'hoja':'Hoja1','fila':107},'seleccion':{'hoja':'DATOS ALUMNOS','fila':rn},'promedios':{'hoja':'Hoja1','filas_asignaturas':count,'planes_distintos':len(plans)}},
'pendientes_no_bloqueantes':[{'clasificacion':'E','concepto':'Acta formal o registro institucional originario que asocie el título con CODCLI y plan.'},{'clasificacion':'E','concepto':'Fórmula original del puntaje 2130 y fecha efectiva de migración; no se declaran resueltas.'}],
'efecto':'Cierra la investigación interna de este vínculo; no modifica diccionario SIES, bases, denominadores, tasas ni prueba de envío/aceptación SIES.'}
text=json.dumps(decision,ensure_ascii=False,indent=2)+'\n'
for case in cs:
 assert case['RUT'].split('-')[0] not in text
 for x in case['datosalumnos']:
  if x['CODCLI']:assert n(x['CODCLI']) not in text
assert all(sha(Path(p))==h for p,h in paths.items())
assert all(sha(REPO/p)==h for p,h in protected.items())
assert git('rev-parse','HEAD')==head
(OUT/'DECISION_CIERRE_INTERNO.json').write_text(text)
qaout={'clasificacion':'C','estado':'PASS_CIERRE_INTERNO','fecha_hora':stamp,'controles':{'evidencias_previas_integras':True,'documento_dv_concordantes':True,'unico_expediente_titulado':True,'seleccion_formula_coincidente':True,'unico_plan_por_codcli':True,'filas_promedios':count,'fuentes_intactas':True,'cambios_ajenos_preservados':True,'sin_identificadores_en_decision':True},'rama':branch,'head_antes':head,'head_despues':git('rev-parse','HEAD'),'decision_sha256':sha(OUT/'DECISION_CIERRE_INTERNO.json'),'script_sha256':sha(Path(__file__)),'limite':'Cierre interno D, atribución documental formal E no bloqueante. Sin commit/push.'}
(OUT/'QA_CIERRE_INTERNO.json').write_text(json.dumps(qaout,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qaout,ensure_ascii=False))

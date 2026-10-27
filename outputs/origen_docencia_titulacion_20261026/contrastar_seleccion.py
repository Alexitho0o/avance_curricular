"""Reproduce la selección del expediente posterior y contrasta su plan por CODCLI exacto."""
from pathlib import Path
import json,hashlib,io
from collections import Counter
import openpyxl
from openpyxl.utils import get_column_letter
OUT=Path(__file__).resolve().parent
R=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-InstitutoProfesionalSanSebasti*'))
cs=json.loads(Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json').read_text())
c=next(c for c in cs if any(x['carrera']=='TCRE' for x in c['contextos_v11']))
body,dv=c['RUT'].split('-');cods={str(x['CODCLI']).upper() for x in c['datosalumnos'] if x['CODCLI']}
def n(v):
 if isinstance(v,float) and v.is_integer():v=int(v)
 return str(v or '').strip().upper()
def load(p):
 b=p.read_bytes();return b,hashlib.sha256(b).hexdigest()
p=R/'Attachments'/'Titulados_Empleabilidad_2026-1_v4.xlsx';b,h=load(p)
w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=False);v=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
s=v['Participacion_TIT'];matches=[]
for row in s:
 if n(row[2].value)==body:matches.append(row[0].row)
assert len(matches)==1;rn=matches[0];rr=int(s[f'AA{rn}'].value)
da=v['DATOS ALUMNOS'];chosen=n(da[f'B{rr}'].value);assert chosen in cods
formula=w['DATOS ALUMNOS'][f'BY{rr}'].value
pool=[]
for row in da:
 if n(row[1].value) in cods:
  pool.append({'fila':row[0].row,'carrera':row[2].value,'estado':row[56].value,'situacion':row[57].value,'prioridad':row[76].value})
# Obtiene prioridad por coordenada verificada, no posiciones asumidas.
for a in pool:a['prioridad']=da[f"BY{a['fila']}"].value
assert max(pool,key=lambda x:x['prioridad'])['fila']==rr
result={'clasificacion':'B/C','fuente':str(p),'sha256':h,'fila_participacion':rn,'fila_seleccionada_datos_alumnos':rr,'codcli_entre_los_tres_del_caso':True,
 'formulas':{f'Participacion_TIT!Z{rn}':w['Participacion_TIT'][f'Z{rn}'].value,f'Participacion_TIT!AA{rn}':w['Participacion_TIT'][f'AA{rn}'].value,f'DATOS ALUMNOS!BY{rr}':formula},'alternativas':pool,
 'codcli_seleccionado_carrera':da[f'C{rr}'].value,'estado_seleccionado':da[f'BE{rr}'].value,'situacion_seleccionada':da[f'BF{rr}'].value}
source=next((R/'Datos DAI (RAW) - 1.1 Datos crudos'/'1.2.1 Datos Institucionales').rglob('Promedio-notas-Alexi.xlsx'))
bb,hh=load(source);pw=openpyxl.load_workbook(io.BytesIO(bb),read_only=True,data_only=True);rows=pw['Hoja1'].values;head=[n(x) for x in next(rows)];counts=Counter();loc=[];dvmatch=0
for i,row in enumerate(rows,2):
 if n(row[head.index('CODCLI')])!=chosen:continue
 plan=row[head.index('PLAN_DE_ESTUDIO')];yr=row[head.index('ANO')];per=row[head.index('PERIODO')]
 counts[(plan,yr,per)]+=1;loc.append(i)
 if n(row[head.index('RUT')])==body and n(row[head.index('DIG')])==dv:dvmatch+=1
result['respaldo_plan']={'ruta':str(source),'sha256':hh,'hoja':'Hoja1','coincidencias_codcli':sum(counts.values()),'coincidencias_documento_y_dv':dvmatch,'filas':loc,'plan_periodo':[{'plan':k[0],'ano':k[1],'periodo':k[2],'filas':vv} for k,vv in counts.items()]}
result['limite']='Selección interna del expediente por fórmula y plan observado por CODCLI; no acta de titulación, no fecha efectiva de migración, no fórmula del puntaje 2130.'
assert hashlib.sha256(p.read_bytes()).hexdigest()==h
assert hashlib.sha256(source.read_bytes()).hexdigest()==hh
payload=json.dumps(result,ensure_ascii=False,indent=2,default=str)+'\n'
for case in cs:
 assert case['RUT'].split('-')[0] not in payload
 for x in case['datosalumnos']:
  if x['CODCLI']:assert n(x['CODCLI']) not in payload
(OUT/'SELECCION_POSTERIOR.json').write_text(payload)
print(payload)

"""Contrasta actividad por CODCLI y avance por RUT/DV, sin exportar identificadores."""
import collections,csv,hashlib,json
from pathlib import Path
import openpyxl
OUT=Path(__file__).resolve().parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/busqueda_tres_llaves_sies_20261026/VALIDACION_FILAS_PRIVADA.json')
CASES=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
cases=json.loads(CASES.read_text());case=next(c for c in cases if any(y['carrera']=='TCRE' for y in c['contextos_v11']))
targets={str(r['CODCLI']).strip().upper() for r in case['datosalumnos'] if r['CODCLI']};assert len(targets)==3
body,dv=case['RUT'].split('-');body=str(int(body));dv=dv.upper()
files=json.loads(PRIVATE.read_text())
def source(name):
 candidates=[x for x in files if Path(x['ruta']).name==name];assert len(candidates)==1;return candidates[0]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def norm(x):
 if isinstance(x,float) and x.is_integer():return str(int(x))
 return str(x or '').strip().upper()
def matches(x,y):
 x=norm(x).replace('.','').replace(' ','');y=norm(y)
 return x.isdigit() and str(int(x))==body and y==dv

prom=source('Promedio-notas-Alexi.xlsx');p=Path(prom['ruta']);assert sha(p)==prom['sha256_barrido']
w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h=[norm(x) for x in next(it)];assert {'CODCLI','RUT','DIG','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO'}.issubset(h)
groups=collections.Counter();ruts=0
for row in it:
 if norm(row[h.index('CODCLI')]) not in targets:continue
 ok=matches(row[h.index('RUT')],row[h.index('DIG')]);ruts+=ok
 key=tuple(norm(row[h.index(k)]) for k in ['CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO']);groups[key]+=1
w.close();assert sha(p)==prom['sha256_barrido']
periods=[{'carrera':a,'plan':b,'anio':c,'periodo':d,'filas':n} for (a,b,c,d),n in sorted(groups.items())]
control=source('matricula_avance_curricular_2025_control.csv');p=Path(control['ruta']);assert sha(p)==control['sha256_barrido']
for encoding in ['utf-8-sig','cp1252']:
 try:
  with p.open('r',encoding=encoding,newline='') as f:
   sample=f.readline(); f.seek(0);sep=';' if sample.count(';')>sample.count(',') else ','
   reader=csv.DictReader(f,delimiter=sep);headers=reader.fieldnames; assert headers
   fields={norm(h):h for h in headers};assert {'NUM_DOCUMENTO','DV','PLAN_ESTUDIOS'}.issubset(fields)
   found=[]
   for row in reader:
    if matches(row[fields['NUM_DOCUMENTO']],row[fields['DV']]):found.append(norm(row[fields['PLAN_ESTUDIOS']]))
  break
 except UnicodeDecodeError:continue
else:raise UnicodeError('encoding')
assert sha(p)==control['sha256_barrido']
out={'clasificacion':'B fuente; C coincidencia; E asignación formal de título',
     'promedios':{'ruta':prom['ruta'],'sha256':prom['sha256_barrido'],'hoja':'Hoja1','filas_codcli':sum(groups.values()),'filas_con_rut_dv':ruts,'periodos_por_carrera_plan':periods},
     'avance':{'ruta':control['ruta'],'sha256':control['sha256_barrido'],'filas_con_rut_dv':len(found),'planes_observados':sorted(set(found)),
               'tiene_codcli':any('CODCLI' in x for x in fields),'tiene_titulo':any(x in {'TITULO','NOMBRE_TITULO','FECHA_OBT_TIT_GRA'} for x in fields)},
     'limites':'Registros de actividad y avance no acreditan de forma directa título–CODCLI–plan; las fuentes pueden solaparse. Períodos son nativos. No se vincula RUT con MRUN.'}
payload=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
for c in cases:
 assert c['RUT'].split('-')[0] not in payload
 for x in c['datosalumnos']:assert norm(x['CODCLI']) not in payload
(OUT/'RESULTADO_AGREGADO.json').write_text(payload)
print(json.dumps(out,ensure_ascii=False))

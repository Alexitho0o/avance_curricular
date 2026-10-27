"""Contrasta eventos derivados y actividad por CODCLI; no exporta identificadores."""
import collections,hashlib,json
from pathlib import Path
import openpyxl
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
priv=Path('/Users/alexi/.local/share/ipss/busqueda_tres_llaves_sies_20261026/REINTENTO_12_PRIVADO.json')
cases=json.loads(Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json').read_text())
case=next(c for c in cases if any(x['carrera']=='TCRE' for x in c['contextos_v11']))
targets={str(x['CODCLI']).strip().upper() for x in case['datosalumnos'] if x['CODCLI']};assert len(targets)==3
body,dv=case['RUT'].split('-');body=str(int(body));dv=dv.upper()
files=json.loads(priv.read_text());data=next(x for x in files if Path(x['ruta']).name=='PREGRADO_TRAYECTORIA_CARACTERIZACION_2026_P1_20260512.xlsx');p=Path(data['ruta'])
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def norm(v):
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v or '').strip().upper()
assert sha(p)==data['sha256']
w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['CAMBIOS_ACADEMICOS'];it=s.iter_rows(values_only=True);h=[norm(x) for x in next(it)];required=['CODCLI','RUT','CODCARPR','ANIO','PERIODO','ESTADOACADEMICO','SITUACION','EVENTO_ACAD_CAT'];assert set(required).issubset(h)
found=[]
for row in it:
 cli=norm(row[h.index('CODCLI')]);r=norm(row[h.index('RUT')]).replace('.','').replace(' ','')
 if cli not in targets:continue
 if '-' not in r or r.split('-')[0].lstrip('0')!=body or r.split('-')[1]!=dv:continue
 found.append({x:norm(row[h.index(x)]) for x in required if x not in ['CODCLI','RUT']})
w.close();assert sha(p)==data['sha256']
assert len(found)==2
prom=json.loads((ROOT/'outputs/contraste_codcli_rut_avance_sies_20261026/RESULTADO_AGREGADO.json').read_text())
group=prom['promedios']['periodos_por_carrera_plan']
out={'clasificacion':'B datos; C etiqueta derivada y cruce; E atribución formal',
     'fuentes':[{'ruta':str(p),'hoja':'CAMBIOS_ACADEMICOS','sha256':data['sha256']},
                {'ruta':prom['promedios']['ruta'],'hoja':prom['promedios']['hoja'],'sha256':prom['promedios']['sha256']}],
     'eventos':found,'actividad_por_carrera_plan_periodo':group,
     'limites':['Los eventos del libro son etiquetas derivadas de estados y situaciones, no un acto de titulación o bitácora de fecha efectiva.',
                'El año y período de trayectoria no se interpretan como fecha de titulación ni cambio efectivo.',
                'La asociación actividad–plan y evento–expediente está corroborada, pero el título reportado no declara CODCLI ni plan.']}
payload=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
for c in cases:
 assert c['RUT'].split('-')[0] not in payload
 for x in c['datosalumnos']:assert norm(x['CODCLI']) not in payload
(OUT/'RESULTADO_AGREGADO.json').write_text(payload)
print(json.dumps({'eventos':found,'filas_actividad':sum(x['filas'] for x in group)},ensure_ascii=False))

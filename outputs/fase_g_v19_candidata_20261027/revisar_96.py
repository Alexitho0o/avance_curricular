from pathlib import Path
from collections import defaultdict,Counter
import json,sqlite3,os,re,openpyxl,datetime,hashlib
R=Path(__file__).resolve().parents[2];P=Path.home()/'.local/share/ipss/fase_g_v19_candidata_20261027';x=json.loads((P/'OTRA_CARRERA_96_PRIVADO.json').read_text());man=json.loads((R/'outputs/fase_g_hito1_mu_siguiente_20261027/MANIFEST.json').read_text());sources=man['fuentes'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();people={z['persona'] for z in x};db=sqlite3.connect((Path.home()/'.local/share/ipss/fase_f_v18_candidata_20261027/DICCIONARIO_V18_CANDIDATA.sqlite').as_uri()+'?mode=ro',uri=True);others=defaultdict(set)
for z in x:
 for cli,raw in db.execute('select codcli,payload from observaciones where persona=? and anio=?',(z['persona'],'2024')):
  p=json.loads(raw)
  if cli!=z['codcli'] and p.get('codigo_documental_atribuible') and p.get('carrera')!=z['carrera']:others[z['persona']].add((cli,p.get('carrera')))
def val(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip().upper()
def rut(s):
 m=re.fullmatch(r'(\d+)-([0-9K])',re.sub(r'[.\s]','',val(s)));return str(int(m[1]))+'-'+m[2] if m else ''
D=defaultdict(list);A=defaultdict(list)
for key in ['da12159','da11248','p7804','p12166','p3233']:
 src=sources[key];path=src['ruta'];assert sha(path)==src['sha256'];w=openpyxl.load_workbook(path,read_only=True,data_only=True);ws=w['Hoja1'];it=ws.iter_rows(values_only=True);hd={val(v):i for i,v in enumerate(next(it)) if v is not None}
 for n,row in enumerate(it,2):
  def get(k):return row[hd[k]] if k in hd and hd[k]<len(row) else None
  pe=rut(get('RUT')) if key.startswith('da') else rut(val(get('RUT'))+'-'+val(get('DIG')));cli=val(get('CODCLI'))
  if pe not in people or not any(cli==c for c,_ in others[pe]):continue
  if key.startswith('da'):
   date=get('FECHAMATRICULA');ds=date.isoformat() if isinstance(date,(datetime.datetime,datetime.date)) else val(date);D[(pe,cli)].append({'fuente':path,'sha256':src['sha256'],'hoja':'Hoja1','fila':n,'carrera':val(get('CODCARPR')),'ano_matricula':val(get('ANOMATRICULA')),'periodo_matricula':val(get('PERIODOMATRICULA')),'ano_ingreso':val(get('ANOINGRESO')),'periodo_ingreso':val(get('PERIODOINGRESO')),'fecha_matricula':ds})
  elif val(get('ANO'))=='2024':A[(pe,cli)].append({'fuente':path,'sha256':src['sha256'],'hoja':'Hoja1','fila':n,'carrera':val(get('CODCARR')),'periodo':val(get('PERIODO')),'plan':val(get('PLAN_DE_ESTUDIO'))})
 w.close();assert sha(path)==src['sha256']
out=[]
for z in x:
 rr=[]
 for cli,car in sorted(others[z['persona']]):rr.append({'codcli':cli,'carrera':car,'datos_alumnos':D.get((z['persona'],cli),[]),'actividad_2024':A.get((z['persona'],cli),[])})
 # A date of matrícula is not necessarily the effective date of a change of program.
 out.append({'persona':z['persona'],'codcli_anterior':z['codcli'],'periodo':z['periodo'],'otros':rr,'mu_2024':z['mu_anio_siguiente'],'clasificacion':'E_FECHA_CAMBIO_NO_ACREDITADA','motivo':'Fecha de matrícula o actividad no demuestra por sí sola fecha efectiva de cambio entre expedientes.'})
p=P/'REVISION_96_PRIVADA.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2));os.chmod(p,0o600);print(json.dumps({'contextos':len(out),'con_datos_alumnos':sum(any(q['datos_alumnos'] for q in r['otros']) for r in out),'con_actividad_2024':sum(any(q['actividad_2024'] for q in r['otros']) for r in out),'con_mu_2024':sum(bool(r['mu_2024']) for r in out),'antes_confirmado':0,'despues_confirmado':0,'pendientes_fecha_cambio':len(out)}));db.close()

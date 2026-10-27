from pathlib import Path
from collections import defaultdict,Counter
import json,re,openpyxl,unicodedata,hashlib
R=Path(__file__).resolve().parents[2];P=Path('/Users/alexi/.local/share/ipss');out=Path(__file__).parent
p=P/'trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json';data=json.loads(p.read_text());assert len(data)==6358;persons={r['persona'] for r in data};assert len(persons)==3142
cat=json.loads((R/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())['catalogo'];plans={x['CODPESTUD']:x for x in json.loads((R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json').read_text())};sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest();sources={};hits=defaultdict(lambda:defaultdict(set));unknown=defaultdict(set)
def v(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def identity(b,d):
 b=v(b).replace('.','');d=v(d);return str(int(b))+'-'+d if b.isdigit() and re.fullmatch('[0-9K]',d) else ''
def diploma(car,plan):
 z=plans.get(plan);names=z.get('nombres_carrera',[]) if z else [];return car in ('DACD','ECCURYDP') or any('DIPLOMADO' in str(s).upper() for s in names),bool(z)
for name in ['PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx']:
 es=[e for e in cat if e['archivo']==name];assert len(es)==1;e=es[0];path=Path(unicodedata.normalize('NFD',e['ruta_consolidada']));assert sha(path)==e['sha256'];sources[name]={'ruta':str(path),'sha256':e['sha256'],'hoja':'Hoja1'};w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);hd={v(a):i for i,a in enumerate(next(it)) if a is not None}
 for row in it:
  def get(k):return row[hd[k]] if k in hd and hd[k]<len(row) else None
  pe=identity(get('RUT'),get('DIG'));year=v(get('ANO'));per=v(get('PERIODO'));plan=v(get('PLAN_DE_ESTUDIO'));car=v(get('CODCARR'))
  if pe not in persons or not year.isdigit():continue
  dip,known=diploma(car,plan);k=(pe,int(year),per)
  if not known:unknown[k].add(name)
  if not dip:hits[k][name].add(v(get('CODCLI')))
 w.close();assert sha(path)==e['sha256']
res=[]
for coh,yr,period in sorted({(r['anio_origen'],r['anio_observado'],r['periodo_nativo']) for r in data}):
 rr=[r for r in data if (r['anio_origen'],r['anio_observado'],r['periodo_nativo'])==(coh,yr,period)];ps={r['persona'] for r in rr};present={pe for pe in ps if hits[(pe,yr,period)]};only121={pe for pe in ps if hits[(pe,yr,period)].get('PROMEDIOSDEALUMNOS_12166.xlsx')};uncertain={pe for pe in ps if unknown[(pe,yr,period)]};res.append({'cohorte':coh,'ano_observado':yr,'periodo_nativo':period,'posiciones':len(rr),'personas_unicas':len(ps),'personas_con_actividad_observada_fuentes':len(present),'personas_con_actividad_12166':len(only121),'sin_actividad_localizada':len(ps-present),'con_plan_no_catalogado':len(uncertain)})
result={'fuente_vista_sha256':sha(p),'universo_posiciones':len(data),'universo_personas':len(persons),'fuentes':sources,'tabla':res,'limites':['Actividad observada no equivale a matrícula vigente o retención.','Cobertura y fecha de extractos no certificadas; ausencias no prueban falta de actividad.','Códigos sin plan catalogado requieren revisión para exclusión de diplomados.','Personas con varios CODCLI se cuentan una vez; evidencia puede ser de otra carrera.','La vista base congela su padrón, no redefine elegibilidad ni verifica observaciones después de v20.']};(out/'ACTIVIDAD_EXPLORATORIA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'universo_posiciones':len(data),'universo_personas':len(persons),'tabla':res},ensure_ascii=False))

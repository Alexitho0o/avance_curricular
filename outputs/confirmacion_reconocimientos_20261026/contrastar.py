"""Contrasta reconocimientos exactos entre copias UMAS sin datos personales de salida."""
import collections,hashlib,json,re
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
folder=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS')
targets={(x['carrera'],x['plan_revisado'],x['ramo']) for x in json.loads((ROOT/'outputs/busqueda_respaldo_titulos_homologaciones_20261026/RESULTADO_AGREGADO.json').read_text())['ramos']};assert len(targets)==21
cases=json.loads(Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json').read_text());people={x['RUT'] for x in cases}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1048576),b''):h.update(v)
 return h.hexdigest()
def s(v):
 if v is None:return ''
 if isinstance(v,(float,int)) and v==int(v):return str(int(v))
 return str(v).strip().upper()
events={};meta=[]
for name in ('PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx','PROMEDIOSDEALUMNOS_2071.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx'):
 p=folder/name;digest=sha(p);w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={s(v):i for i,v in enumerate(next(it)) if v is not None};fields=('RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','CODRAMO','CODSECC','ESTADO','DESCRIPCION_ESTADO','RAMOEQUIV','CONVALIDADO');assert set(fields).issubset(h)
 result=collections.defaultdict(set);invalid=0
 for row in it:
  def v(k):return s(row[h[k]]) if h[k]<len(row) else ''
  career,plan,ramo=(v(k) for k in ('CODCARR','PLAN_DE_ESTUDIO','CODRAMO'))
  if (career,plan,ramo) not in targets or v('ESTADO') not in ('I','E'):continue
  body=v('RUT').replace('.','').replace(' ','');dv=v('DIG')
  if not body.isdigit() or not re.fullmatch('[0-9K]',dv) or not v('CODCLI') or not v('ANO') or not v('PERIODO'):invalid+=1;continue
  identity=str(int(body))+'-'+dv
  key=(identity,v('CODCLI'),career,plan,v('ANO'),v('PERIODO'),ramo,v('CODSECC'),v('ESTADO'),v('DESCRIPCION_ESTADO'),v('RAMOEQUIV'),v('CONVALIDADO'))
  result[(career,plan,ramo)].add(key)
 w.close();assert sha(p)==digest;events[name]=result;meta.append({'ruta':str(p),'hoja':'Hoja1','sha256':digest,'pares_con_reconocimiento':len(result),'registros_invalidos':invalid})
baseline=events['PROMEDIOSDEALUMNOS_7804.xlsx'];others=[n for n in events if n!='PROMEDIOSDEALUMNOS_7804.xlsx'];records=[];counter=collections.Counter()
for key,values in sorted(baseline.items()):
 shared={name:len(values & events[name].get(key,set())) for name in others};any_shared=set().union(*(values & events[n].get(key,set()) for n in others));matched_4={v[0] for v in values if v[0] in people}
 row={'carrera':key[0],'plan':key[1],'ramo':key[2],'registros_en_7804':len(values),'registros_repetidos_en_al_menos_otra_extraccion':len(any_shared),'coincidencias_por_otra_extraccion':shared,'personas_de_los_cuatro_casos_en_7804':len(matched_4)};records.append(row)
 counter['pares_con_registro_7804']+=1;counter['pares_con_mismo_registro_en_otra_extraccion']+=bool(any_shared);counter['registros_en_7804']+=len(values);counter['registros_repetidos']+=len(any_shared)
out={'clasificacion':'B registros UMAS; C cruce; E autorización y vigencia','fuentes':meta,'metodo':'Llave con RUT, DV, CODCLI, carrera, plan, año, periodo, ramo, sección, estado, descripción, RAMOEQUIV y CONVALIDADO; identidades solo en memoria. Se retienen únicamente I/E; no se suman extracciones.','totales':dict(counter),'pares':records,'limites':'Cortes potencialmente derivados de la misma base no son evidencia administrativa independiente. Coincidencia no prueba autorización, vigencia del plan, equivalencia universal ni título.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['totales'],ensure_ascii=False))

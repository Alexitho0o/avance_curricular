"""Busca contextos excepcionales en respaldos históricos por identidad y expediente."""
import collections,datetime,glob,hashlib,json,os,re
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
detail=PRIVATE/'QA_EXCEPCIONES_T1_DETALLE_20261026_V2.json'
paths=[('DA_P2_2026','/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx','Hoja1'),('DA_P3_2026','/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx','Hoja1')]
for label,pattern,sheet in [('LISTADO_2025_T2','/Users/alexi/Downloads/cierre/*T2_2025 2.xlsx','Hoja1'),('LISTADO_2025_T3','/Users/alexi/Downloads/cierre/*T3_2025 2.xlsx','T3'),('LISTADO_2026_T2','/Users/alexi/Downloads/cierre/*T_2_13_07_2026.xlsx','Hoja1'),('LISTADO_2026_T3','/Users/alexi/Downloads/cierre/*T3_02_10_2026.xlsx','Base')]:
 matches=glob.glob(pattern)
 if len(matches)!=1:raise ValueError('Ruta no resuelta: '+label)
 paths.append((label,matches[0],sheet))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def txt(v):
 if v is None:return ''
 s=str(v).strip().upper();return '' if s in ('NULL','NONE','NAN') else s
def norm(v,d=None):
 s=txt(v).replace('.','').replace(' ','')
 if d is None:
  if '-' not in s:return None
  s,d=s.split('-',1)
 d=txt(d);return str(int(s))+'-'+d if re.fullmatch(r'\d+',s) and re.fullmatch(r'[0-9K]',d) else None
def field(row,h,k):
 i=h.get(k);return txt(row[i]) if i is not None and i<len(row) else ''
targets=json.loads(detail.read_text()); assert len(targets)==100
by_cli=collections.defaultdict(list)
for t in targets:by_cli[t['codcli']].append(t)
results={};aggregates={}; global_count=collections.Counter()
for label,p,sheet in paths:
 file=Path(p);w=openpyxl.load_workbook(file,read_only=True,data_only=True);s=w[sheet];it=s.iter_rows(values_only=True);h={txt(x):i for i,x in enumerate(next(it))};
 if not {'CODCLI','RUT'}.issubset(h):raise ValueError('Llaves faltantes '+label)
 matches=collections.defaultdict(list);errors=collections.Counter()
 for i,row in enumerate(it,2):
  cli=field(row,h,'CODCLI')
  if cli not in by_cli:continue
  raw=field(row,h,'RUT');pe=norm(raw)
  if pe is None:
   dv=field(row,h,'DIG') or field(row,h,'DV');pe=norm(raw,dv) if dv else None
  for t in by_cli[cli]:
   if pe!=t['persona']:
    errors['codcli_sin_misma_identidad']+=1;continue
   entry={'fuente':label,'hoja':sheet,'fila':i,'carrera':field(row,h,'CODCARPR') or field(row,h,'CODIGOCARRERA'),'jornada':field(row,h,'JORNADA'),'sede':field(row,h,'SEDE'),'ano_matricula':field(row,h,'ANOMATRICULA'),'periodo_matricula':field(row,h,'PERIODOMATRICULA'),'ano_ingreso':field(row,h,'ANOINGRESO'),'fecha_matricula':field(row,h,'FECHAMATRICULA'),'estado_actual_extracto':field(row,h,'ESTADOACADEMICO')}
   matches[t['pos']].append(entry)
 w.close()
 groups={}
 for group,fn in [('diferencias_25',lambda t:t['diferencia_familia']),('sin_T1_8',lambda t:t['sin_t1']),('CO_73',lambda t:t['co'])]:
  selected=[t for t in targets if fn(t)]; found=[t for t in selected if matches[t['pos']]]
  groups[group]={'contextos':len(selected),'mismo_rut_y_codcli':len(found),'carrera_concordante':sum(any(z['carrera']==t['carrera'] for z in matches[t['pos']]) for t in found),'jornada_concordante':sum(any(z['jornada']=={'1':'D','2':'V','4':'O'}.get(t['jornada']) for z in matches[t['pos']]) for t in found),'sede_co_observada':sum(any(z['sede']=='CO' for z in matches[t['pos']]) for t in found),'registros_fuente':sum(len(matches[t['pos']]) for t in found)}
 for t in targets:t.setdefault('respaldos',{})[label]=matches[t['pos']]
 results[label]={'ruta':str(file),'hoja':sheet,'sha256':sha(file),'grupos':groups,'alertas':dict(errors),'limite':'Coincidencia RUT/CODCLI; fecha de exportación/corte y continuidad del plan requieren acreditación. Estado de extracción no establece automáticamente estado pasado.'}
out={'clasificacion':'B fuentes; C cruces; E atribución y fechas','fecha_hora':datetime.datetime.now().astimezone().isoformat(),'contextos_union':len(targets),'fuentes':results,'nota':'Grupos superpuestos; no sumar. No se atribuye código SIES por mera coincidencia RUT/CODCLI ni por ausencia de registro.'}
dest=PRIVATE/'QA_RESPALDOS_HISTORICOS_DETALLE.json';fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(targets,f,ensure_ascii=False,default=str)
(OUT/'QA_RESPALDOS_HISTORICOS_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))

import json,re
from pathlib import Path
import openpyxl
T=Path('/tmp/ipss_embudo_2317_20261022');new=json.load(open(T/'evidencias_nuevas.json'));foc={r[0] for r in json.load(open(T/'embudo_privado.json'))};p=next(p for p in json.load(open(T/'hashes.json')) if 'CIERRE_AUDITORIA' in p);w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['TRAZABILIDAD_DATOSALUMNOS'];it=iter(s.values);h=next(it);v=lambda x:'' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip();n=0
for rn,row in enumerate(it,2):
 d=dict(zip(h,row));a=v(d.get('N_DOC')).replace('.','');b=v(d.get('DV')).upper()
 if not a.isdigit() or not re.fullmatch('[0-9K]',b):continue
 k=str(int(a))+'-'+b
 if k not in foc:continue
 for prefix in ['SIES_','FUENTE_','MATRIZ_']:
  fields=[prefix+t for t in ['COD_SED','COD_CAR','JOR','VERSION']]
  if not all(v(d.get(t)).isdigit() for t in fields):continue
  code='I162S%sC%sJ%sV%s'%tuple(v(d[t]) for t in fields)
  new.append([k,'MATRICULA','2026',code,'COMPLETO',prefix+'COMPONENTES',v(d.get('DA_PLAN_ESTUDIO')),v(d.get('CODCLI',d.get('DA_CODCLI'))),v(d.get('CODCARPR',d.get('DA_CODCARPR'))),p,s.title,rn,'MU2026;traza de corte','DERIVADO_TRAZABILIDAD; distinguir SIES/FUENTE/MATRIZ',a,b]);n+=1
(T/'evidencias_nuevas.json').write_text(json.dumps(new,ensure_ascii=False));print({'componentes_prefijados_recuperados':n})

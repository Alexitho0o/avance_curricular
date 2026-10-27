"""Mide presencia CODCLI/año/período en fuentes para contextos pendientes."""
from pathlib import Path
from collections import Counter
import json,unicodedata,openpyxl,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
p=ROOT/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
pending=[k for k,v in n['cache'].items() if not v.get('codigo_sies')];assert len(pending)==1292 and len(n['cache'])==5144
cats=json.loads((ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())['catalogo'];sources={x['archivo']:x for x in cats if x['archivo'] in ('PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx')};assert len(sources)==2
indexes={};audit={}
def scalar(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
for name,e in sources.items():
 path=Path(unicodedata.normalize('NFD',e['ruta_consolidada']));sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==e['sha256'];wb=openpyxl.load_workbook(path,read_only=True,data_only=True);it=wb['Hoja1'].iter_rows(values_only=True);h={scalar(v):i for i,v in enumerate(next(it)) if v is not None};assert all(t in h for t in ['CODCLI','ANO','PERIODO']);keys=set();count=0
 for row in it:
  count+=1;cli=scalar(row[h['CODCLI']]);ano=scalar(row[h['ANO']]);per=scalar(row[h['PERIODO']]);
  if cli and ano.isdigit() and per.isdigit():keys.add((cli,ano,per))
 wb.close();indexes[name]=keys;audit[name]={'ruta':str(path),'sha256':sha,'hoja':'Hoja1','filas':count}
a=indexes['PROMEDIOSDEALUMNOS_7804.xlsx'];b=indexes['PROMEDIOSDEALUMNOS_12166.xlsx'];categories=Counter();people=Counter();exp=set();selected=set()
for pe,cli,plan,car,jor,year,per in pending:
 k=(cli,year,per);state='ambas' if k in a and k in b else 'solo_7804' if k in a else 'solo_12166' if k in b else 'ninguna';categories[state]+=1
 if state=='solo_7804':selected.add(pe);exp.add((pe,cli,car))
assert sum(categories.values())==1292
result={'clasificacion':'C cálculo; B existencia de filas; E causa de ausencia y cobertura','unidad':'contextos del foco; llave de presencia CODCLI+año+período, sin verificar identidad ni plan','foco_contextos':5144,'pendientes':1292,'particion':dict(categories),'solo_7804_personas_distintas':len(selected),'solo_7804_expedientes_persona_codcli_carrera':len(exp),'fuentes':audit,'limites':['No prueba identidad, plan, matrícula vigente ni causa de ausencia.','No hay aquí una estimación de truncamiento institucional; el respaldo puede tener alcance o corte distinto.','Conteos por persona y expediente derivados dentro de este foco.']};(OUT/'CONTROL_7804_12166.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='fuentes'},ensure_ascii=False,indent=2))

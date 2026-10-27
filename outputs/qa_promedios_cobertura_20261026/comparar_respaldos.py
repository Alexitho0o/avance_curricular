"""Audita cobertura agregada de notas 2026; identificadores quedan en memoria."""
import collections,datetime,hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import openpyxl
BASE=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián')
CON=BASE/'IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS'
COPIES=list(BASE.glob('Archivos de Microsoft*Copilot Chat/PROMEDIOSDEALUMNOS_7952.xlsx'))
assert len(COPIES)==1
FILES={'v11_7804':CON/'PROMEDIOSDEALUMNOS_7804.xlsx','v11_12166':CON/'PROMEDIOSDEALUMNOS_12166.xlsx','v11_3233':CON/'PROMEDIOSDEALUMNOS_3233.xlsx','respaldo_anual_7804':Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/PROMEDIOSDEALUMNOS_7804.xlsx'),'otro_7952':COPIES[0]}
def clean(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def core_xml(p):
 with zipfile.ZipFile(p) as z:
  if 'docProps/core.xml' not in z.namelist():return {}
  return {x.tag.rsplit('}',1)[-1]:x.text for x in ET.fromstring(z.read('docProps/core.xml')) if x.tag.rsplit('}',1)[-1] in ('created','modified')}
meta={};codes={};tuples={};inaccesibles={}
for name,path in FILES.items():
 try:wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
 except (OSError,ValueError,Exception) as exc:
  if name=='otro_7952':inaccesibles[name]={'ruta':str(path),'estado':'no accesible para lectura','error_tipo':type(exc).__name__};continue
  raise
 s=wb['Hoja1']; it=s.iter_rows(values_only=True); raw=next(it);headers={clean(v):i for i,v in enumerate(raw) if v is not None}
 required={'ANO','PERIODO','CODCLI','CODCARR','PLAN_DE_ESTUDIO','CODRAMO','CODSECC','RUT','DIG'}
 if not required.issubset(headers):raise ValueError('Faltan cabeceras en '+name)
 counts=collections.Counter(); cs=collections.defaultdict(set);ts=collections.defaultdict(set); missing=collections.Counter();total=0
 for row in it:
  if not any(v is not None for v in row):continue
  total+=1
  def v(k):return clean(row[headers[k]]) if headers[k]<len(row) else ''
  year,period=v('ANO'),v('PERIODO');key=f'{year}-{period}';counts[key]+=1
  if key not in ('2026-2','2026-3'):continue
  cli=v('CODCLI');rut=v('RUT');dv=v('DIG');plan=v('PLAN_DE_ESTUDIO');career=v('CODCARR');course=v('CODRAMO');sec=v('CODSECC')
  if cli:cs[key].add(cli)
  else:missing[key+'_sin_codcli']+=1
  if all((rut,dv,cli,plan,career,course,sec)):ts[key].add((rut.lstrip('0') or '0',dv,cli,plan,career,course,sec))
  else:missing[key+'_llave_incompleta']+=1
 core=core_xml(path);meta[name]={'ruta':str(path),'sha256':digest(path),'tamano_bytes':path.stat().st_size,'hoja':'Hoja1','filas_datos_no_vacias':total,'filas_por_periodo_2026':{k:v for k,v in sorted(counts.items()) if k.startswith('2026-')},'codcli_distintos_2026_t2_t3':{k:len(cs[k]) for k in ('2026-2','2026-3')},'llaves_academicas_distintas_2026_t2_t3':{k:len(ts[k]) for k in ('2026-2','2026-3')},'llaves_incompletas':dict(missing),'core_creado':core.get('created'),'core_modificado':core.get('modified'),'metodo_core':'docProps/core.xml directo; null si falta','cabeceras':list(headers)};codes[name]=cs;tuples[name]=ts;wb.close();print('Procesado '+name,file=sys.stderr,flush=True)
comp={}
for period in ('2026-2','2026-3'):
 uc=set().union(*(codes[n][period] for n in ('v11_7804','v11_12166','v11_3233')));ut=set().union(*(tuples[n][period] for n in ('v11_7804','v11_12166','v11_3233')))
 comp[period]={}
 for n in ('respaldo_anual_7804','otro_7952'):
  if n not in codes:continue
  c=codes[n][period];t=tuples[n][period];comp[period][n]={'codcli_fuente':len(c),'codcli_union_v11':len(uc),'codcli_comunes':len(c&uc),'codcli_solo_fuente':len(c-uc),'codcli_solo_v11':len(uc-c),'llaves_academicas_fuente':len(t),'llaves_academicas_union_v11':len(ut),'llaves_comunes':len(t&ut),'llaves_solo_fuente':len(t-ut),'llaves_solo_v11':len(ut-t)}
out={'clasificacion':'B fuentes; C conteos y comparaciones; E completitud','fecha':datetime.datetime.now().astimezone().isoformat(),'fuentes':meta,'fuentes_no_leidas':inaccesibles,'comparaciones':comp,'llave_academica':'RUT normalizado + DIG + CODCLI + CODCARR + PLAN_DE_ESTUDIO + CODRAMO + CODSECC, por año y período; sin valores individuales','limites':'CODCLI no es persona; filas son asignaturas. El año/periodo académico no acredita fecha de corte administrativo. Igualdad o mayor cobertura no certifica extracción completa; faltan metadatos de exportación y universo esperado.'}
(Path(__file__).parent/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'fuentes':{k:{x:v[x] for x in ('filas_datos_no_vacias','filas_por_periodo_2026','codcli_distintos_2026_t2_t3')} for k,v in meta.items()},'comparaciones':comp},ensure_ascii=False))

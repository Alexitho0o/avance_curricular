"""Cruce exacto privado de reportes históricos; produce solo conteos agregados."""
import collections,hashlib,json,os,sqlite3,subprocess
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
prior=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
source=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/06_INDICADORES_ACADEMICOS_VRA')
files=[(source/'CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx','MASTER INGRESO 2024',2),(source/'PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx','DATOS CRUDOS U+ 19-11-2024',1),(source/'Cumplimiento Ingreso de Notas.xlsx','Hoja1',1)]
db=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026/DICCIONARIO_SIES_CANDIDATO_V11_86_Y_AMBIGUEDAD.sqlite')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def s(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
assert sha(db)=='1dafb1486f3ebd080ad4435a3af80b65a1a7016ba47b51f30d91b9a050985141'
cases=json.loads(prior.read_text());assert len(cases)==4
targets={}
for c in cases:
 for context in c['contextos_v11']:
  key=context['CODCLI']; assert key not in targets or targets[key]['persona']==c['RUT']
  targets[key]={'persona':c['RUT'],'caso':c['caso']}
con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
assert all(con.execute('select count(distinct persona) from observaciones where codcli=?',(key,)).fetchone()[0]==1 for key in targets)
con.close()
issues=json.loads((ROOT/'outputs/conciliacion_22_ramos_titulados_20261026/EVIDENCIA_AGREGADA.json').read_text())['discrepancias'];target_courses={x['asignatura'] for x in issues if not x['relaciones_catalogo']}
records=collections.defaultdict(list);course_hits=collections.defaultdict(lambda:collections.Counter());file_meta=[]
for path,sheet,header_row in files:
 digest=sha(path);w=openpyxl.load_workbook(path,read_only=True,data_only=True);ws=w[sheet];it=ws.iter_rows(values_only=True)
 for _ in range(header_row-1):next(it)
 h={s(v):i for i,v in enumerate(next(it)) if v is not None};assert {'CODCLI','RUT','CODIGO_PLAN_ESTUDIO','CODIGO_ASIGNATURA'}.issubset(h)
 for rn,row in enumerate(it,header_row+1):
  def get(k):return s(row[h[k]]) if k in h and h[k]<len(row) else ''
  cli=get('CODCLI');code=get('CODIGO_ASIGNATURA');plan=get('CODIGO_PLAN_ESTUDIO')
  if code in target_courses:course_hits[code][(path.name,plan)]+=1
  if cli not in targets:continue
  body=get('RUT').replace('.','').replace('-','').replace(' ','').lstrip('0');expected=targets[cli]['persona'].split('-')[0]
  if not body or body!=expected:continue
  records[targets[cli]['caso']].append({'fuente':path.name,'hoja':sheet,'fila':rn,'CODCLI':cli,'plan':plan,'ano':get('ANO'),'periodo':get('PERIODO'),'asignatura':code,'estado':get('ESTADO_ACADEMICO'),'fecha_inicio':get('FECHAINICIO'),'fecha_fin':get('FECHAFIN'),'fecha_reporte':get('FECHA REPORTE') or get('FECHA MEDICION')})
 w.close();assert sha(path)==digest;file_meta.append({'archivo':str(path),'hoja':sheet,'sha256':digest,'fila_encabezado':header_row})
groups=collections.Counter()
for c in cases:
 xs=records[c['caso']];groups['personas_con_registros']+=bool(xs);groups['personas_sin_registros']+=not bool(xs)
 for plan in {(e['carrera'],e['plan']) for t in c['titulos'] for e in t['expedientes_compatibles']}:
  if any(r['plan']==plan[1] for r in xs):groups['pares_persona_plan_observados']+=1
private=Path('/Users/alexi/.local/share/ipss/busqueda_bitacora_mallas_20261026');private.mkdir(parents=True,mode=0o700,exist_ok=True)
assert subprocess.run(['git','-C',str(private),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
dest=private/'EVIDENCIA_REPORTES_CUATRO.json';assert not dest.exists()
with os.fdopen(os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(records,f,ensure_ascii=False,indent=2)
out={'clasificacion':'B observaciones; C vínculo; E vigencia y asignación','fuentes':file_meta,'identidad':'CODCLI exacto con propietario único en v11 y cuerpo RUT idéntico; los reportes no corroboran DV del estudiante de manera independiente.','casos':dict(groups),'ramos':{code:[{'fuente':src,'plan':plan,'filas':n} for (src,plan),n in sorted(hits.items())] for code,hits in sorted(course_hits.items())},'ramos_buscados':len(target_courses),'ramos_con_filas':len(course_hits),'detalle_privado':{'ruta':str(dest),'sha256':sha(dest)},'limites':'Fecha de reporte e inicio de asignatura no prueban fecha efectiva de cambio de plan ni plan del título. Nombre de curso y actividad no equivalen a una homologación autorizada.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'casos':out['casos'],'ramos_buscados':out['ramos_buscados'],'ramos_con_filas':out['ramos_con_filas']},ensure_ascii=False))

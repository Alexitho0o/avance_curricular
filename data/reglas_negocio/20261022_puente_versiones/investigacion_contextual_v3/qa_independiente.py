import sqlite3,json,re,hashlib
from pathlib import Path
import openpyxl
O=Path(__file__).parent
rs=json.load(open(O/'PRUEBAS_CONTEXTUALES.json'));ss=json.load(open(O/'FUENTES.json'));db=sqlite3.connect(':memory:')
db.executescript('CREATE TABLE p(k,c,j,cli,plan,y,t); CREATE TABLE m(k,y,code);')
def norm(x):return str(int(x)) if isinstance(x,(int,float)) else str(x or '').strip().upper()
def key(a,b):
 a=norm(a).replace('.','').replace(' ','');b=norm(b)
 return str(int(a))+'-'+b if a.isdigit() and re.fullmatch('[0-9K]',b) else None
for s in ss:
 path=s['ruta'];assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['sha256']
 if 'DATOSDEALUMNOS' in path:continue
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w.active.values);h=next(it);batch=[]
 for values in it:
  r=dict(zip(h,values))
  if 'PROMEDIOS' in path:
   k=key(r['RUT'],r['DIG']);batch.append((k,norm(r['CODCARR']),{'D':'1','V':'2','O':'4'}.get(norm(r['JORNADA']),''),norm(r['CODCLI']),norm(r['PLAN_DE_ESTUDIO']),norm(r['ANO']),norm(r['PERIODO'])))
  elif 'MAT_IP_CIISA' in path:batch.append((key(r['MM_N_DOCUMENTO'],r['MM_DV']),norm(r['MC_CAT_PERIODO']).replace('MAT_',''),norm(r['MC_CODIGO_UNICO'])))
  elif norm(r['TIPO_DOC'])=='R':batch.append((key(r['N_DOC'],r['DV']),norm(r['ANIO_INFORMADO']),'I162S%sC%sJ%sV%s'%tuple(norm(r[t]) for t in ['COD_SED','COD_CAR','JOR','VERSION'])))
 db.executemany('INSERT INTO '+('p VALUES (?,?,?,?,?,?,?)' if 'PROMEDIOS' in path else 'm VALUES (?,?,?)'),batch);w.close()
db.executescript('CREATE INDEX mi ON m(k,y); CREATE VIEW pu AS SELECT DISTINCT * FROM p WHERE k IS NOT NULL;')
checks=[]
for r in rs:
 n,people=db.execute('SELECT COUNT(*),COUNT(DISTINCT k) FROM pu WHERE c=? AND j=?',(r['carrera'],r['jornada'])).fetchone()
 rows=db.execute('SELECT p.k,p.cli,p.plan,p.y,p.t,m.code FROM pu p LEFT JOIN m ON p.k=m.k AND p.y=m.y WHERE p.c=? AND p.j=?',(r['carrera'],r['jornada'])).fetchall();groups={}
 for k,cli,p,y,t,code in rows:
  cs=groups.setdefault((k,cli,p,y,t),set())
  if code and code.rsplit('V',1)[0] in r['familias']:cs.add(code)
 unique=sum(len(v)==1 for v in groups.values());missing=sum(not v for v in groups.values())
 assert n==r['observaciones'] and people==r['personas'] and unique==r['estadisticas'].get('un_codigo',0) and missing==r['estadisticas'].get('sin_match',0)
 checks.append({'carrera':r['carrera'],'jornada':r['jornada'],'observaciones':n,'personas':people,'un_codigo':unique,'sin_match':missing})
new=[r['carrera']+'/J'+r['jornada'] for r in rs if not r['estado_previo'].startswith('PROPUESTA') and r['completo_con_contexto_DA_y_catalogo'] and r['personas']>=3]
assert len(rs)==63 and len(new)==5
out={'estado':'PASS','metodo':'segunda lectura XLSX y SQLite DISTINCT + LEFT JOIN; contraste 63 dimensiones; controles DA/catalogo en primera implementacion, no duplicados independientemente','nuevas_propuestas_contextuales':new,'pendientes_antes':24,'pendientes_ahora':19,'denominador':63,'hashes_fuentes_consistentes':True,'checks':checks}
(O/'QA_INDEPENDIENTE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='checks'},ensure_ascii=False))

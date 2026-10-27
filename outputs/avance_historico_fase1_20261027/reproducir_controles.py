"""Auditoría de lectura: H112A/H112B/H113/H114B. Salidas solo agregadas.
No reconstruye el conteo primario de aprobaciones desde PROMEDIOS.
Ejecutar: python3 outputs/avance_historico_fase1_20261027/reproducir_controles.py
"""
from pathlib import Path
import csv, io, json, hashlib, math, subprocess
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from openpyxl import load_workbook

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
GIT_REF = '3067c97'
ONEDRIVE = next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-InstitutoProfesionalSanSebasti*'))
P = ONEDRIVE / 'Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026'
A_DIR = next(P.rglob('AVANCE_CURRICULAR_2026_DECISION_ALTERNATIVA_PERIODIZACION_CARRERAS_16769_20260709_114429'))
SOURCES = {
 'h112a': A_DIR/'DECISION_ALTERNATIVA_PERIODIZACION_CARRERAS_16769.xlsx',
 'h112a_script': A_DIR/'decision_alternativa_periodizacion_carreras_16769.py',
 'h112b_csv': P/'Carreras Avance Curricular 2026/5810_CARRERAS_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16769_21C_H112B_CONTROLADO.csv',
 'h112b_excel': P/'Carreras Avance Curricular 2026/5810_CARRERAS_AVANCE_CURRICULAR_2026_REVISION_H112B_CONTROLADO.xlsx',
 'h113_csv': P/'AVANCE_CURRICULAR_2026_SALIDAS_20260704_221542/5809_MATRICULA_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16768_FINAL_H113_REGENERADO.csv',
 'h114b_csv': P/'5809_MATRICULA_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16768_H114B_CORREGIDO_PLAN.csv',
 'h114b_excel': P/'5809_MATRICULA_AVANCE_CURRICULAR_2026_REVISION_H114B_CORREGIDO_PLAN.xlsx',
 'manual': REPO/'requerimiento_bettersoft_uplus_2026/01_fuentes_oficiales/avance_curricular_2026/Instructivo_Avance Curricular SIES - 2026.txt',
}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576), b''): h.update(b)
 return h.hexdigest()
def git(*args): return subprocess.check_output(['git',*args],cwd=REPO).decode().rstrip('\n')
def dump(name, obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sheet(book, name):
 rows=list(book[name].values); headers=list(rows[0]); return [dict(zip(headers,r)) for r in rows[1:] if any(v is not None for v in r)], headers
def norm(v):
 if v is None: return ''
 s=str(v).strip()
 try: return str(Decimal(s).normalize())
 except InvalidOperation: return s
checks=[]
def check(name, expected, observed, cls='B/C', source=''):
 checks.append(dict(control=name,esperado=expected,observado=observed,estado='PASS' if expected==observed else 'FAIL',clasificacion=cls,fuente=source))
before={k:dict(ruta=str(p),sha256=sha(p),bytes=p.stat().st_size) for k,p in SOURCES.items()}
books={k:load_workbook(SOURCES[k],read_only=True,data_only=True) for k in ['h112a','h112b_excel','h114b_excel']}
a=books['h112a']; b=books['h112b_excel']; d=books['h114b_excel']
career_excel, ch=sheet(b,'03_CARGA_SIES_16769_21C')
student_excel, sh=sheet(d,'04_CSV_CON_TITULOS')
def read_csv(key, headers):
 raw=SOURCES[key].read_bytes()
 try: txt=raw.decode('utf-8-sig'); enc='utf-8-sig compatible'
 except UnicodeDecodeError: txt=raw.decode('cp1252'); enc='cp1252 compatible'
 rows=list(csv.reader(io.StringIO(txt),delimiter=';'))
 check(key+' columnas', [len(headers)],sorted(set(map(len,rows))),source=key)
 before[key]['estructura']={'filas':len(rows),'columnas':len(headers),'encabezado':False,'delimitador':';','encoding_lector':enc}
 return [dict(zip(headers,r)) for r in rows]
careers=read_csv('h112b_csv',ch); old=read_csv('h113_csv',sh); new=read_csv('h114b_csv',sh)
check('SHA H112B', 'e355417a13f1caa7434da88ae167c663b2526225743a1ede191de7c024c2c8a0',before['h112b_csv']['sha256'],source='manifest H112B Git')
check('SHA H113', '54a7cbbb6b30784835b9d0a3df9e842285edb6249cbbd53ae54b6d4e82b8aab3',before['h113_csv']['sha256'],source='manifest H113 Git')
check('Carreras filas',43,len(careers),source='h112b_csv')
check('Matrícula filas antes',2371,len(old),source='h113_csv')
check('Matrícula filas después',2371,len(new),source='h114b_csv')
precarga,_=sheet(b,'01_PRECARGA_5810_RAW')
immutable,_=sheet(b,'04_CONTROL_INMUTABILIDAD')
pm={(norm(r['CODIGO_UNICO']),norm(r['PLAN_ESTUDIOS'])):r for r in precarga}
check('H112B precarga llaves conservadas',set(pm)=={(norm(r['CODIGO_UNICO']),norm(r['PLAN_ESTUDIOS'])) for r in careers},True,source='H112B hojas01/03')
check('H112B campos precargados inmutables',0,sum(norm(r[x['COLUMNA']])!=norm(pm[(norm(r['CODIGO_UNICO']),norm(r['PLAN_ESTUDIOS']))][x['COLUMNA']]) for r in careers for x in immutable),source='H112B hojas01/03/04')
check('H112B unidad asignatura', ['1'], sorted({r['TIPO_UNIDAD_MEDIDA'] for r in careers}),cls='B/C/D',source='H112B')
check('H112B otra unidad vacía', [''],sorted({r['OTRA_UNIDAD_MEDIDA'] for r in careers}),source='H112B')
for name,x,y,cols in [('Carreras CSV/Excel',careers,career_excel,ch),('Matrícula CSV/Excel',new,student_excel,sh)]:
 check(name+' filas',len(x),len(y),source=name)
 check(name+' diferencias de celdas normalizadas',0,sum(norm(r[c])!=norm(s[c]) for r,s in zip(x,y) for c in cols),source=name)
def ck(r):return (norm(r['CODIGO_UNICO']),norm(r['PLAN_ESTUDIOS']))
def sk(r):return tuple(norm(r[k]) for k in ['TIPO_DOCUMENTO','NUM_DOCUMENTO','DV','CODIGO_UNICO','PLAN_ESTUDIOS'])
cm={ck(r):r for r in careers}
check('Carreras llaves duplicadas',0,len(careers)-len(cm),source='h112b_csv')
for label,rows in [('H113',old),('H114B',new)]:
 check(label+' llaves individuales duplicadas',0,len(rows)-len({sk(r) for r in rows}),source=label)
 check(label+' sin carrera-plan',0,sum(ck(r) not in cm for r in rows),source=label)
check('Orden y llaves conservadas',True,[sk(r) for r in old]==[sk(r) for r in new],source='H113/H114B')
units=[f'UNIDADES_{s}_ANIO' for s in ['1ER','2DO','3ER','4TO','5TO','6TO','7MO']]
# Reproducción de la periodización ya documentada, a partir del detalle congelado H112A.
detail,_=sheet(a,'05_FUENTE_DETALLE_ASIGNATURAS'); saved_method,_=sheet(a,'06_METODO_A_GRUPOS_NIVELES'); final,_=sheet(a,'10_DISTRIBUCION_CANDIDATA_FINAL')
check('Detalle asignaturas filas',1711,len(detail),source='H112A hoja05')
check('Detalle duplicados código-unidad',0,len(detail)-len({(r['CODIGO_UNICO'],r['UNIDAD_ID']) for r in detail}),source='H112A hoja05')
dist=defaultdict(lambda:defaultdict(set)); method_diffs=0
for r,s in zip(detail,saved_method):
 allowed=int(r['ANIOS_PERMITIDOS']); size=math.ceil(int(r['NIVEL_MAX_PLAN'])/allowed) if allowed else 0
 year=min(allowed,max(1,math.ceil(int(r['NIVEL_NUM'])/size))) if size else 0
 method_diffs+=int(size!=s['TAMANO_GRUPO_NIVELES'] or year!=s['ANIO_SIES_METODO_A'] or r['CODIGO_UNICO']!=s['CODIGO_UNICO'] or r['UNIDAD_ID']!=s['UNIDAD_ID'])
 dist[r['CODIGO_UNICO']][year].add(r['UNIDAD_ID'])
check('Método A filas',len(detail),len(saved_method),source='H112A hojas05/06')
check('Método A discrepancias',0,method_diffs,source='H112A hojas05/06')
fdiffs=0
for r in final:
 counts=[len(dist[r['CODIGO_UNICO']][i]) for i in range(1,8)]
 fdiffs+=sum(norm(r[c])!=norm(v) for c,v in zip(units,counts))
 fdiffs+=int(norm(r['TOTAL_UNIDADES_MEDIDA'])!=norm(sum(counts)))
check('Distribución recreada / hoja10 diferencias',0,fdiffs,source='H112A hojas05/10')
fm={ck(r):r for r in final}
check('H112B campos distribución vs H112A',0,sum(norm(r[c])!=norm(fm[ck(r)][c]) for r in careers for c in ['TOTAL_UNIDADES_MEDIDA',*units]),source='H112A hoja10/H112B')
check('Suma años = unidades plan',0,sum(int(r['TOTAL_UNIDADES_MEDIDA'])!=sum(int(r[c]) for c in units) for r in careers),source='H112B')
check('Distribución fuera duración',0,sum(sum(int(r[c]) for i,c in enumerate(units,1) if i>math.ceil(int(r['DURACION_ESTUDIOS'])/2)) for r in careers),source='H112B')
# Atribución y reproducción celda por celda de la corrección H114B.
changed=0; changed_groups=set(); transform_diff=0; other_diff=0; agg={}
numcols=['UNIDADES_CURSADAS','UNIDADES_APROBADAS','UNID_CURSADAS_TOTAL','UNID_APROBADAS_TOTAL']
for r,s in zip(old,new):
 key=ck(r); total=int(cm[key]['TOTAL_UNIDADES_MEDIDA']); orig=int(r['UNID_APROBADAS_TOTAL']); applied=int(s['UNID_APROBADAS_TOTAL'])
 calc=min(orig,total,int(r['UNID_CURSADAS_TOTAL']))
 transform_diff+=int(calc!=applied)
 other_diff+=sum(r[c]!=s[c] for c in sh if c!='UNID_APROBADAS_TOTAL')
 if orig!=applied: changed+=1;changed_groups.add(key)
 z=agg.setdefault(key,dict(codigo_unico=key[0],plan_estudios=key[1],nombre_carrera=cm[key]['NOMBRE_CARRERA'],registros=0,registros_corregidos=0,unidades_plan_por_estudiante=total,denominador_plan_sumado=0,aprobadas_acumuladas_h113=0,aprobadas_acumuladas_h114b=0,cursadas_anuales=0,aprobadas_anuales=0,cursadas_acumuladas=0,clasificacion='B/C'))
 z['registros']+=1;z['registros_corregidos']+=int(orig!=applied);z['denominador_plan_sumado']+=total
 z['aprobadas_acumuladas_h113']+=orig;z['aprobadas_acumuladas_h114b']+=applied
 for field,col in [('cursadas_anuales','UNIDADES_CURSADAS'),('aprobadas_anuales','UNIDADES_APROBADAS'),('cursadas_acumuladas','UNID_CURSADAS_TOTAL')]:z[field]+=int(s[col])
check('H114B celdas distintas de fórmula min',0,transform_diff,source='H113+H112B contra H114B')
check('Cambios en otras columnas',0,other_diff,source='H113/H114B')
check('Registros corregidos',247,changed,source='H113/H114B y manifest H114B')
check('Carrera-plan afectados',20,len(changed_groups),source='H113/H114B y manifest H114B')
for label,rows in [('H113',old),('H114B',new)]:
 for title,left,right in [('aprobadas año > cursadas año','UNIDADES_APROBADAS','UNIDADES_CURSADAS'),('aprobadas total > cursadas total','UNID_APROBADAS_TOTAL','UNID_CURSADAS_TOTAL'),('aprobadas año > aprobadas total','UNIDADES_APROBADAS','UNID_APROBADAS_TOTAL')]:
  check(label+' '+title,0,sum(int(r[left])>int(r[right]) for r in rows),source=label)
check('H114B aprobadas total sobre plan',0,sum(int(r['UNID_APROBADAS_TOTAL'])>int(cm[ck(r)]['TOTAL_UNIDADES_MEDIDA']) for r in new),source='H114B/H112B')
totals={c:{'h113':sum(int(r[c]) for r in old),'h114b':sum(int(r[c]) for r in new)} for c in numcols}
for v in totals.values():v['diferencia']=v['h114b']-v['h113']
rows=list(agg.values())
for r in rows:
 r['reduccion_aprobadas']=r['aprobadas_acumuladas_h113']-r['aprobadas_acumuladas_h114b']
 r['avance_agregado_h114b']=r['aprobadas_acumuladas_h114b']/r['denominador_plan_sumado'] if r['denominador_plan_sumado'] else None
with (OUT/'CONCILIACION_43_CARRERA_PLAN.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
for w in books.values():w.close()
for k,p in SOURCES.items():check('Fuente inalterada '+k,before[k]['sha256'],sha(p),source=k)
# Registra referencias Git sin copiar contenido individual a las salidas.
paths=git('ls-tree','-r','--name-only',GIT_REF,'avance_curricular_2026').splitlines()
git_evidence=[]
for path in paths:
 if (('112b_' in path or '/113_' in path or '114b_' in path) and Path(path).name.startswith('manifest')) or ('112d_' in path and Path(path).name=='INFORME_CIERRE_GOBERNADO_CARGA_COMPLETA_CARRERAS_16769.md'):
  blob=subprocess.check_output(['git','show',f'{GIT_REF}:{path}'],cwd=REPO)
  git_evidence.append(dict(commit=git('rev-parse',GIT_REF),ruta=path,sha256=hashlib.sha256(blob).hexdigest()))
result=dict(clasificacion='B/C',proceso=2026,datos=2025,registros=2371,carrera_plan=len(cm),corregidos=changed,grupos_corregidos=len(changed_groups),sumas_unidades=totals,denominador_plan_sumado=sum(r['denominador_plan_sumado'] for r in rows),alcance='Reproducción desde detalle H112A y CSV H113; no desde RAW PROMEDIOS.',controles=checks)
dump('RESULTADOS.json',result)
dump('QA.json',dict(estado='PASS_CONTROLES_PARCIALES' if all(c['estado']=='PASS' for c in checks) else 'FAIL',controles=len(checks),pass_n=sum(c['estado']=='PASS' for c in checks),fallos=[c for c in checks if c['estado']!='PASS'],limites=['No reproduce desde RAW el conteo primario H113.','No acredita aceptación final PES.','No valida nueva aplicación de la corrección H114B a otros periodos.']))
dump('MANIFEST_FASE1.json',dict(fecha=datetime.now(timezone.utc).isoformat(),proceso='Avance Curricular SIES 2026',referencia_datos=2025,clasificacion='B/C/D/E',git=dict(rama=git('branch','--show-current'),head=git('rev-parse','HEAD')),fuentes=before,evidencia_git=git_evidence,script=dict(ruta=str(Path(__file__).resolve()),sha256=sha(Path(__file__))),salidas={n:sha(OUT/n) for n in ['RESULTADOS.json','QA.json','CONCILIACION_43_CARRERA_PLAN.csv']},regla_h114b=dict(clasificacion='C',expresion='min(aprobadas_total_H113,total_plan_H112B,cursadas_total_H113)',advertencia='Reproduce transformación histórica; no prueba obligatoriedad normativa de truncar al 100%.'),pendientes=['Motor primario de H113 y su reproducción RAW','Evidencia de aceptación final PES','Validar alcance de regla D de periodización antes de extensión histórica'],punto_reanudacion='Revisar cálculo primario antes de construir análisis histórico; no generar Excel todavía.'))
print(json.dumps({'controles':len(checks),'fallos':[c for c in checks if c['estado']!='PASS'],'sumas':totals,'registros_corregidos':changed},ensure_ascii=False,indent=2))

# Conservar en cada repetición el cierre documental y sus huellas.
git_before=json.loads((OUT/'GIT_ANTES.json').read_text())
git_after={'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'status':git('status','--short').splitlines()}
dump('GIT_DESPUES.json',git_after)
m=json.loads((OUT/'MANIFEST_FASE1.json').read_text())
for name in ['INFORME_FASE1.md','GIT_ANTES.json','GIT_DESPUES.json']:
    if (OUT/name).is_file(): m['salidas'][name]=sha(OUT/name)
spec=REPO/'docs/ESPECIFICACION_AVANCE_HISTORICO_FASE1_20261027.md'
m['especificacion']={'ruta':str(spec),'sha256':sha(spec)}
m['cierre_git']={'rama_antes':git_before['branch'],'rama_despues':git_after['branch'],'head_antes':git_before['head'],'head_despues':git_after['head'],'commit':False,'push':False,'estados_previos_conservados':set(git_before['status']).issubset(set(git_after['status']))}
m['estado_fase']='EJECUTADA_CON_REPRODUCCION_PRIMARIA_PENDIENTE'
dump('MANIFEST_FASE1.json',m)

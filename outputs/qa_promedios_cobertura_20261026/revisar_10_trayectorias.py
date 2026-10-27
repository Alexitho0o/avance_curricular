"""Selecciona diez expedientes reproducibles y describe períodos sin identificarlos."""
import collections,hashlib,json,os
from pathlib import Path
import openpyxl
OUT=Path(__file__).parent; P=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_12166.xlsx')
def txt(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and int(x)==x:return str(int(x))
 return str(x).strip().upper()
g=collections.defaultdict(lambda:collections.defaultdict(lambda:{'ramos':set(),'estados':set(),'filas':0}));w=openpyxl.load_workbook(P,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={txt(x):i for i,x in enumerate(next(it)) if x is not None}
for r in it:
 def v(k):return txt(r[h[k]]) if k in h and h[k]<len(r) else ''
 rut=v('RUT').replace('.','').lstrip('0');dv=v('DIG');cli=v('CODCLI');y=v('ANO');p=v('PERIODO')
 if not rut.isdigit() or not dv or not cli or not y.isdigit() or not p.isdigit():continue
 x=g[(rut,dv,cli)][(int(y),int(p))];x['filas']+=1;x['ramos'].add(v('CODRAMO'));x['estados'].add(v('ESTADO_ACADEMICO'))
w.close();chosen=[]
for state,n in [('VIGENTE',3),('ELIMINADO',3),('TITULADO',3),('SUSPENDIDO',1)]:
 eligible=[k for k,periods in g.items() if len(periods)>=3 and len({p[0] for p in periods})>=2 and {e for v in periods.values() for e in v['estados']}=={state}]
 eligible.sort(key=lambda k:hashlib.sha256('|'.join(k).encode()).hexdigest());assert len(eligible)>=n;chosen.extend(eligible[:n])
out=[];private=[]
for i,k in enumerate(chosen,1):
 periods=g[k];table=[{'anio':y,'periodo':p,'filas_asignaturas':v['filas'],'codigos_asignatura_distintos':len(v['ramos']- {''}),'estado_academico_observado':sorted(v['estados'])} for (y,p),v in sorted(periods.items())];alias='E%02d'%i;out.append({'caso':alias,'periodos':table,'ultimo_periodo':table[-1],'numero_periodos':len(table)});private.append({'caso':alias,'rut':k[0],'dv':k[1],'codcli':k[2]})
loc=Path('/Users/alexi/.local/share/ipss/v11_ultimo_estado_20261026');f=loc/'MUESTRA_10_IDENTIDADES_PRIVADA.json'
if f.exists():raise SystemExit('No sobrescribir muestra privada')
with os.fdopen(os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as z:json.dump(private,z)
res={'clasificacion':'B actividad y estados observados; C selección; E fecha y alcance','fuente':'PROMEDIOSDEALUMNOS_12166.xlsx','sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'metodo':'10 expedientes con al menos tres períodos y dos años, estratificados en 3 vigentes, 3 eliminados, 3 titulados y 1 suspendido; selección reproducible por hash de llave, no muestra representativa.','expedientes':out,'limite':'ANO/PERIODO indican actividad de asignaturas; la columna ESTADO_ACADEMICO no trae por sí sola fecha de evento ni prueba que ese estado rigiera históricamente en cada fila.'};(OUT/'MUESTRA_10_TRAYECTORIAS_AGREGADA.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))

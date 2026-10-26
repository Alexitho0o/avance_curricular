import json,hashlib,collections,datetime,subprocess,sys
from pathlib import Path
import openpyxl
C=json.load(open(sys.argv[1]));P=Path(C['privado']);O=Path(C['output']);R=O.parents[1]
load=lambda p:json.load(open(p))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def v(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def clean(x):return v(x).upper().replace('.','').replace(' ','')
rev=load(P/'REVISION_16_CASOS.json');prof=load(P/'PERFIL_FUENTES_ADICIONALES.json')
# Verify CODCLI uniqueness against all previous segments, not only selected cases.
bp=Path(load(R/'outputs/trayectorias_374_20261023_072401/MANIFEST.json')['privado'])
allseg=load(bp/'SEGMENTOS_EXPEDIENTE_PLAN.json');owners=collections.defaultdict(set)
for s in allseg:owners[s['CODCLI']].add(s['persona'])
focus={s['CODCLI']:x['persona'] for x in rev for s in x['segmentos_previos']}
assert all(owners[c]=={p} for c,p in focus.items())
spec=[]
for z in prof:
 if Path(z['path']).name=='CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx' and z['sheet']=='MASTER INGRESO 2024':spec.append((z,P/'LECTURA_CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx',2,'CALIFICACIONES_ASIGNATURA'))
 if Path(z['path']).name=='Cumplimiento Ingreso de Notas.xlsx' and z['sheet']=='Hoja1':spec.append((z,P/'LECTURA_Cumplimiento Ingreso de Notas.xlsx',1,'CALIFICACIONES_ASIGNATURA'))
 if Path(z['path']).name=='DATOSDEALUMNOS ORIGEN DE LOS DATOS2025.xlsx' and z['sheet']=='Hoja1':spec.append((z,Path(z['path']),1,'DATOSALUMNOS_HISTORICO'))
rows=[];inv=[];rejected=[]
for z,path,hr,role in spec:
 h=sha(path);assert h==z['sha256'];w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w[z['sheet']].iter_rows(min_row=hr,values_only=True)
 rawheads=[v(x).upper() for x in next(it)];counts=collections.Counter();heads=[]
 for s in rawheads:counts[s]+=1;heads.append(s if counts[s]==1 else s+'__'+str(counts[s]))
 n=found=0
 for rn,rr in enumerate(it,hr+1):
  n+=1;d=dict(zip(heads,rr));cc=v(d.get('CODCLI'))
  if cc not in focus:continue
  person=focus[cc];rut=clean(d.get('RUT'));body=person.split('-')[0]
  if rut not in [person,body,person.replace('-','')]:rejected.append({'archivo':z['path'],'hoja':z['sheet'],'fila':rn,'CODCLI':cc,'motivo':'RUT no corrobora CODCLI'});continue
  keep=['CODCLI','CODCARPR','CODCARRERA_ALUMNO','SEDE','JORNADA','REGIMEN','CODIGO_PLAN_ESTUDIO','ANO','PERIODO','PERIODO__2','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','FECHAFIRMA','CODIGO_ASIGNATURA','SECCION','FECHAINICIO','FECHAFIN','FECHA REPORTE','ESTADO','ESTADO_ACADEMICO','ESTADOACADEMICO','SITUACION']
  rec={k:v(d[k]) for k in keep if k in d};rec.update(persona=person,RUT_original=v(d.get('RUT')),archivo=z['path'],archivo_lectura=str(path),sha256=h,hoja=z['sheet'],fila=rn,rol=role,metodo='CODCLI exacto y único en inventario previo; RUT corrobora cuerpo/completo; no se usa DIG del docente')
  rows.append(rec);found+=1
 inv.append({'archivo':z['path'],'archivo_lectura':str(path),'sha256':h,'hoja':z['sheet'],'encabezados':heads,'filas_leidas':n,'filas_foco':found,'estado':'LEIDO','copia_identica':True})
 w.close()
save(P/'FILAS_RECUPERADAS_CODCLI.json',rows);save(P/'RECHAZOS_IDENTIDAD.json',rejected);save(O/'INVENTARIO_RECUPERACION.json',inv)
assert not rejected
for case in rev:
 rr=[x for x in rows if x['persona']==case['persona']];case['filas_recuperadas_codcli']=rr
 tests=[]
 for x in rr:
  if x['rol']!='CALIFICACIONES_ASIGNATURA':continue
  ctx=[s for s in case['segmentos_previos'] if s['CODCLI']==x['CODCLI'] and s['carrera']==x['CODCARRERA_ALUMNO']]
  tests.append({'fuente':x,'planes_previos':[s['plan'] for s in ctx],'coincide':any(s['plan']==x['CODIGO_PLAN_ESTUDIO'] for s in ctx)})
 case['contraste_planes_reporte_2024']=tests
save(P/'REVISION_16_CASOS_AMPLIADA.json',rev)
summary=[]
for x in rev:
 groups=collections.defaultdict(list)
 for r in x['filas_recuperadas_codcli']:
  if r['rol']=='CALIFICACIONES_ASIGNATURA':groups[r['CODCARRERA_ALUMNO'],r['CODIGO_PLAN_ESTUDIO']].append(r)
 entry={'caso':x['caso'],'calificaciones':[],'datosalumnos_filas':sum(r['rol']=='DATOSALUMNOS_HISTORICO' for r in x['filas_recuperadas_codcli'])}
 for (car,plan),rr in groups.items():
  entry['calificaciones'].append({'carrera':car,'plan':plan,'filas':len(rr),'anos_periodos':sorted(set((r['ANO'],r['PERIODO']) for r in rr)),'inicio':sorted(set(r['FECHAINICIO'] for r in rr)),'fin':sorted(set(r['FECHAFIN'] for r in rr)),'reporte':sorted(set(r.get('FECHA REPORTE','') for r in rr)),'estados':dict(collections.Counter(r['ESTADO'] for r in rr))})
 summary.append(entry)
save(O/'HALLAZGOS_RECUPERACION.json',summary)
print(json.dumps({'filas':len(rows),'rechazos':len(rejected),'personas':sum(bool(x['calificaciones']) for x in summary)},ensure_ascii=False))

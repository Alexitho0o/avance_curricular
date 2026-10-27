from pathlib import Path
import json,hashlib,collections,re,openpyxl,os
ROOT=Path(__file__).resolve().parents[2];out=Path(__file__).parent;cases=json.loads(Path('/Users/alexi/.local/share/ipss/revision_siete_20261027/RESGUARDO_FECHAS_PLAN.json').read_text());assert len(cases)==7
inv=json.loads((ROOT/'outputs/cambios_plan_12_y_4_20261023_080207/INVENTARIO_RECUPERACION.json').read_text());sources=[v for v in inv if v.get('hoja') in ['Hoja1','MASTER INGRESO 2024'] and 'CALIFICACIONES' in v['archivo_lectura'].upper() or v.get('archivo_lectura','').endswith('LECTURA_Cumplimiento Ingreso de Notas.xlsx')];assert len(sources)==2
owners=collections.defaultdict(set)
for i,c in enumerate(cases):
 owners[c['contexto']['CODCLI']].add(i)
 for x in c['filas_datos_alumno_outras'] if 'filas_datos_alumno_outras' in c else c['filas_datos_alumno_otras']:
  if x.get('CODCLI'):owners[str(x['CODCLI']).strip().upper()].add(i)
found=[[] for _ in cases];audit=[]
def clean(x):return str(x or '').strip().upper()
def norm(x):return re.sub('[^0-9K]','',clean(x))
for a in sources:
 p=Path(a['archivo_lectura']);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==a['sha256'];wb=openpyxl.load_workbook(p,read_only=True,data_only=True);sh=wb[a['hoja']];it=sh.iter_rows(values_only=True);head=None;rn=0
 for row in it:
  rn+=1;h=[clean(v) for v in row]
  if 'CODCLI' in h and 'CODIGO_PLAN_ESTUDIO' in h and 'RUT' in h:head=h;break
 assert head;num=0
 for row in it:
  rn+=1;d=dict(zip(head,row));cli=clean(d.get('CODCLI'))
  if cli not in owners:continue
  for i in owners[cli]:
   body=norm(cases[i]['contexto']['persona'].split('-')[0]);raw=norm(d.get('RUT'))
   if raw not in (body,norm(cases[i]['contexto']['persona'])):continue
   found[i].append({'archivo':p.name,'hoja':a['hoja'],'fila':rn,'CODCLI':cli,'plan':clean(d.get('CODIGO_PLAN_ESTUDIO')),'carrera':clean(d.get('CODCARRERA_ALUMNO')),'ano':clean(d.get('ANO')),'periodo':clean(d.get('PERIODO')),'inicio':str(d.get('FECHAINICIO') or ''),'fin':str(d.get('FECHAFIN') or ''),'reporte':str(d.get('FECHA REPORTE') or '')});num+=1
 wb.close();audit.append({'ruta':str(p),'sha256':sha,'hoja':a['hoja'],'referencias':num})
summary=collections.Counter();detail=[]
for i,c in enumerate(cases):
 x=c['contexto'];own=[z for z in found[i] if z['CODCLI']==x['CODCLI']];other=[z for z in found[i] if z['CODCLI']!=x['CODCLI']];same=[z for z in own if z['plan']==x['plan'] and z['ano'].replace('.0','')==x['ano'] and z['periodo'].replace('.0','')==x['periodo_UMAS']];summary['casos_con_expediente_propio']+=bool(own);summary['casos_con_expediente_alternativo']+=bool(other);summary['casos_con_plan_periodo_propio']+=bool(same);summary['casos_con_ambos']+=bool(own and other);detail.append({'contexto':x,'registros':found[i]})
priv=Path('/Users/alexi/.local/share/ipss/revision_siete_20261027/RESPALDOS_PERIODO.json');assert not priv.exists();fd=os.open(priv,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(detail,f,ensure_ascii=False,indent=2)
result={'casos':7,'resumen':dict(summary),'fuentes':audit,'advertencia':'RUT de reportes no acredita DV, se combina con CODCLI exacto previamente vinculado; fechas corresponden a asignaturas/reportes y no prueban fecha de migración ni código asignado al expediente.'};(out/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))

"""Contrasta auditoría gobernada y seis respaldos originales; no adjudica."""
from pathlib import Path
import sys,json,csv,collections,os
import openpyxl
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256,rut_normalizado
O=R/'outputs/cierre_inf35_07_jornadas_14_20261023_135630';cfg=json.loads((O/'CONFIG.json').read_text());P=Path(cfg['privado']);rs=json.loads((P/'JORNADAS_14_PENDIENTES.json').read_text());owners={r['CODCLI']:r['persona'] for r in rs};labels={r['CODCLI']:r['caso'] for r in rs};assert len(rs)==14 and len(owners)==8
A=Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/auditoria_datos_alumnos/20261021_091039_506207');m=json.loads((A/'manifest.json').read_text());H={str(A/'manifest.json'):sha256(A/'manifest.json')}
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
for name in ['CAMBIOS_PRIVADO.csv','CORTES.csv','APARICIONES_PRIVADO.csv','CALIDAD_PRIVADO.csv']:
 h=next(x['sha256'] for x in m['salidas'] if x['archivo']==name);assert sha256(A/name)==h;H[str(A/name)]=h
with (A/'CAMBIOS_PRIVADO.csv').open(encoding='utf-8-sig') as f:
 changes=[dict(r,caso=labels[r['CODCLI']]) for r in csv.DictReader(f,delimiter=';') if r['CODCLI'] in owners]
for r in changes:assert rut_normalizado(r['RUT'])==owners[r['CODCLI']]
assert len(changes)==17;jchanges=[r for r in changes if r['campo']=='JORNADA'];assert len(jchanges)==1 and jchanges[0]['caso']=='INF35-12'
want=['2026-08-25','2026-09-29','2026-09-30','2026-10-02','2026-10-21'];sources=[x for x in m['fuentes'] if x['corte_nominal'][:10] in want];assert len(sources)==5
sources.append({'ruta':'/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx','sha256':'b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869','hoja':'Hoja1','fila_encabezado':1,'corte_nominal':'2026-07-21 congelamiento; no fecha efectiva acreditada'})
back=R/'outputs/retencion_intermedia_t2_t3/20261021_133221/MANIFEST_REVISION.json';H[str(back)]=sha256(back)
rows=[];inv=[]
for x in sources:
 p=Path(x['ruta']);assert sha256(p)==x['sha256'];H[str(p)]=x['sha256'];w=openpyxl.load_workbook(p,read_only=True,data_only=True);ws=w[x['hoja']];it=iter(ws.values);header=None
 for rn,rr in enumerate(it,1):
  hh=[val(z).upper() for z in rr]
  if 'CODCLI' in hh and 'RUT' in hh:header=hh;break
  if rn>5:raise ValueError('encabezado no encontrado')
 cnt=0
 for rn,rr in enumerate(it,rn+1):
  d=dict(zip(header,rr));cc=val(d.get('CODCLI'))
  if cc not in owners:continue
  assert rut_normalizado(d['RUT'])==owners[cc]
  keep=['CODCLI','RUT','CODCARPR','JORNADA','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','FECHAFIRMA','SITUACION','ESTADOACADEMICO','SEDE']
  z={k:val(d[k]) for k in keep if k in d};z.update(caso=labels[cc],fuente=str(p),hoja=ws.title,fila=rn,sha256=x['sha256'],corte_nominal=x['corte_nominal'],tipo_corte='fecha nominal de extracción; zona horaria no confirmada');rows.append(z);cnt+=1
 w.close();inv.append(dict(x,filas_foco=cnt));print(p.name,'leído',flush=True)
assert len(rows)==48
for c in owners:
 q=[r for r in rows if r['CODCLI']==c];assert len(q)==6
change=jchanges[0];b=next(r for r in rows if r['caso']=='INF35-12' and r['corte_nominal'].startswith('2026-09-29'));a=next(r for r in rows if r['caso']=='INF35-12' and r['corte_nominal'].startswith('2026-09-30'));assert b['JORNADA']=='O' and a['JORNADA']=='D';assert b['FECHAMATRICULA']==a['FECHAMATRICULA'];assert all(b[k]==a[k] for k in ['CODCLI','RUT','CODCARPR','ANOMATRICULA','PERIODOMATRICULA']);assert b['SITUACION']!=a['SITUACION']
for f,h in H.items():assert sha256(f)==h
dump(P/'CAMBIOS_AUDITORIA_FOCO.json',changes);dump(P/'FILAS_CORTES_VERIFICADAS.json',rows);dump(O/'FUENTES_CORTES_HASHES.json',H);dump(O/'INVENTARIO_CORTES.json',inv)
# No se publica la identidad o matrícula; solo etiquetas locales de revisión.
summary=[]
for case in sorted(set(labels.values())):
 q=[r for r in rows if r['caso']==case];summary.append({'caso':case,'observaciones_pendientes':sum(r['caso']==case for r in rs),'jornadas_por_corte':{r['corte_nominal']:r['JORNADA'] for r in q},'cambios_jornada_en_auditoria':sum(r['caso']==case for r in jchanges),'clasificacion':'B diferencia entre respaldos; E fecha efectiva y código destino'})
dump(O/'RESUMEN_CORTES.json',summary);print(json.dumps(summary,ensure_ascii=False))

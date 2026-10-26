"""Prepara solamente agregados; mantiene el código T1 y consulta v7 sin nuevas decisiones."""
import sys,json,hashlib,collections,subprocess,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=Path(sys.argv[1]).resolve(); O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=Path.home()/'.local/share/ipss'
origin=P/'aplicacion_diccionario_intertrimestral_20261023_125556/ORIGENES_T1.json'
dest=P/'destinos_calendario_v7_20261023'
assert sha(origin)=='9ba34a21ce89170f6343e068ba38ac1a546a927c1bd5ffcab9f4fd6ef48288a0'
assert sha(dest/'CONTEXTOS_POR_ORIGEN_PERIODO.json')=='82a12e4dbbd9d3ea751f2601d6b4a2f4ffe6485cb7c1f53268015169dba585ca'
assert sha(dest/'RANURAS_POR_ORIGEN_PERIODO.json')=='2b6c4772818695af0d7473c9ed3998ebad6aba5c3f62fe7cce6559e4bab2f094'
orig=json.loads(origin.read_text()); byrow={x['fila_foto']:x for x in orig}
contexts=json.loads((dest/'CONTEXTOS_POR_ORIGEN_PERIODO.json').read_text())
slots=json.loads((dest/'RANURAS_POR_ORIGEN_PERIODO.json').read_text())
source=R/'outputs/aplicacion_diccionario_intertrimestral_20261023_125556/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx'
assert sha(source)=='e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe'
d=json.loads((O/'INDICADORES_AGREGADOS.json').read_text())
lookup=collections.Counter((x['anio_origen'],int(x['periodo_nativo']),x['codigo_origen_T1'],byrow[x['fila_origen_foto']]['carrera']) for x in slots if x['sin_contexto'])
multi={(x['anio'],x['codigo_origen'],x['carrera']):x['multiple'] for x in orig}
rows=[]
for x in d['por_codigo_T1']:
 for p in (2,3):
  y=x['cohorte_T1']; yy=int(x[f'periodo_T{p}'].split('-')[0]); n=x[f'T{p}_numerador']; den=x['T2_denominador' if p==2 else 'T3_denominador_vigente']
  no=lookup[(y,p,x['codigo_SIES_T1'],x['carrera_T1'])]
  rows.append([y,yy,p,x['carrera_T1'],x['codigo_SIES_T1'],x['denominador_T1_original'],n if n is not None else 'Pendiente',den,None,x[f'T{p}_alcance'],no,'Sí' if multi[(y,x['codigo_SIES_T1'],x['carrera_T1'])] else 'No',x['denominador_T1_original']-no])
assert len(rows)==218 and sum(x[5] for x in rows)==6358
states={'B/C_DOCUMENTAL_ANUAL_ATRIBUIDO':'B/C Documental anual','D_CORRESPONDENCIA_INTERNA_APROBADA':'D Interno aprobado','E_PENDIENTE':'E Pendiente'}
counter=collections.Counter()
for x in contexts:
  o=byrow[x['fila_origen_foto']]; st=states[x['estado_destino']]
  limit='Atribución documental al período pendiente' if st.startswith('D') else ('Versión/atribución pendiente; no adjudicar por totales' if st.startswith('E') else 'Código anual atribuido; no acredita día del cambio ni aceptación SIES')
  counter[(x['anio_origen'],x['anio_observado'],int(x['periodo_nativo']),o['carrera'],x['carrera_umas'],x['plan'],x['codigo_origen_T1'],x['codigo_destino'] or 'Pendiente',st,x['tipo_pendiente'] or x['relacion_codigo'],x['comparacion_plan'],x['contraste_dimensiones'],'Sí' if o['multiple'] else 'No',limit)]+=1
ctx=[list(k[:13])+[v,k[13]] for k,v in sorted(counter.items(),key=lambda z:tuple(str(a) for a in z[0]))]
assert sum(x[13] for x in ctx)==2854
tab={'origen_periodo':rows,'contextos':ctx,'resumen':d['resumen'],'origenes':3179,'familias_multiversion':sorted({x['familia'] for x in orig if x['multiple']})}
# Do not export individual keys or case aliases. Plans and SIES codes are program-level fields.
ids={str(x[k]) for x in orig for k in ('persona','documento_original') if x.get(k)}|{x['codcli'] for x in contexts}
for row in rows+ctx:
 for v in row: assert str(v) not in ids
(O/'TABLAS_SEGUIMIENTO.json').write_text(json.dumps(tab,ensure_ascii=False,indent=2)+'\n')
paths=[source,origin,dest/'CONTEXTOS_POR_ORIGEN_PERIODO.json',dest/'RANURAS_POR_ORIGEN_PERIODO.json',R/'data/diccionario_sies_seguimiento/activo.json',R/'data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json',P/'cierre_inf35_03_t3_20261023_154224/DICCIONARIO_SIES.sqlite']
for ref in d['referencias'].values():
 if 'ruta' in ref:paths.append(Path(ref['ruta']))
meta={'clasificacion':'B fuentes; C aplicación y controles; D decisiones internas previas conservadas; E pendientes explícitos','origen_excel':str(source),'fuentes':{str(p):sha(p) for p in dict.fromkeys(paths)},'diccionario':'v7_20261023_inf35_03_t3','nuevos_cierres':0,'alcance':'Código T1 documentado; 2024 observado en 2025 y 2025/2026 en el mismo año; solo períodos nativos 2 y 3. No equiparar automáticamente actividad a cierre.','git_antes':{'rama':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()},'pendientes':d['limites']}
(O/'MANIFEST_SEGUIMIENTO.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'grupos_origen_periodo':len(rows),'grupos_contexto':len(ctx),'origenes':3179,'contextos':2854,'respaldo':dict(collections.Counter({s:sum(x[13] for x in ctx if x[8]==s) for s in states.values()}))}))

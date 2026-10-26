"""Prepara vistas agregadas y privadas; no cambia reglas ni resultados fuente."""
import csv,json,hashlib,sys
from pathlib import Path
from collections import Counter
O=Path(sys.argv[1]); M=json.load(open(O/'MANIFEST.json')); P=Path(M['privado'])
Q=json.load(open(O/'RESULTADOS_QA.json')); E=json.load(open(O/'QA_RELECTURA_MULTIPROCESO.json'))
rows=json.load(open(P/'OBSERVACIONES_PRIVADAS.json'))
old=json.load(open(P/'reanudacion/antecedentes_minimos.json'))
before={tuple(r[:8]):r for s in old if s['name']=='CONTRASTE_63' for r in s['rows']}
v9={tuple(r[1:9]):r for r in json.load(open(P/'reanudacion/v9.json'))}
docstates={'CONFIRMA_CODIGO_PROPUESTO_OBSERVADO','DIFIERE_CODIGO_PROPUESTO_OBSERVADO','CODIGO_ANUAL_UNICO_SIN_PROPUESTA_PREVIA'}
transitions=Counter(); discrepancies=0
for x in rows:
    key=tuple(x[k] for k in ['persona','CODCLI','carrera','sede_dimension','jornada_sies','plan','ano','periodo'])
    b=before[key]; codes=list(filter(None,b[9].split('; ')))
    bd=codes[0] if b[10] in docstates else ''
    bi=v9[key][44] if key in v9 and v9[key][44] else bd
    x['codigo_documental_antes_v10']=bd;x['codigo_interno_antes_v10']=bi
    x['transicion_documental']='SIN_CAMBIO' if bd==x['codigo_documental_atribuible'] else 'CAMBIO'
    x['transicion_interna']='SIN_CAMBIO' if bi==x['codigo_interno_adoptado'] else 'CAMBIO'
    transitions[(x['transicion_documental'],x['transicion_interna'])]+=1
    discrepancies+=bd!=x['codigo_documental_atribuible'] or bi!=x['codigo_interno_adoptado']
assert discrepancies==0
T={'comparacion_por_clave':len(rows),'codigos_antes_despues_diferentes':discrepancies,'transiciones':{' / '.join(k):v for k,v in transitions.items()},
   'cierres_nuevos_documentales':sum(not x['codigo_documental_antes_v10'] and bool(x['codigo_documental_atribuible']) for x in rows),
   'cierres_nuevos_internos':sum(not x['codigo_interno_antes_v10'] and bool(x['codigo_interno_adoptado']) for x in rows)}
(O/'QA_TRANSICIONES.json').write_text(json.dumps(T,ensure_ascii=False,indent=2))
(P/'OBSERVACIONES_PRIVADAS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
fields=list(dict.fromkeys(k for r in rows for k in r))
with (P/'OBSERVACIONES_PRIVADAS.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fields,delimiter=';');w.writeheader()
    for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
Q['foco_actual'].update({k:v for k,v in T.items() if k.startswith('cierres_')})
Q['limites'][-1]='Relectura adicional: 49.218 localizadores completos de 33 archivos; no equivale a inventario universal ni prueba temporal de otros procesos'
(O/'RESULTADOS_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2))
d=Q['linea_base']['documental'];i=Q['equivalencias']['interno']
summary=[['Conciliación UMAS–SIES | reproducción V10'],
 ['B/C · 5.901 personas · 6.622 expedientes · 24.774 observaciones. Códigos y tasas anteriores conservados.'],
 ['La correspondencia interna no acredita envío ni aceptación SIES. Esta auditoría no calcula una nueva tasa de retención.'],
 ['Personas: categorías disjuntas','Documental','Interno vigente','Diferencia','Clasificación'],
 ['Sin observaciones pendientes',d['sin_pendientes'],i['sin_pendientes'],None,'C'],
 ['Parcialmente resueltas',d['parcialmente_resueltas'],i['parcialmente_resueltas'],None,'C'],
 ['Ninguna observación resuelta',d['ninguna_observacion_resuelta'],i['ninguna_observacion_resuelta'],None,'C'],
 ['Total de personas',None,None,None,'C · suma de tres categorías'],
 ['Con algún pendiente',None,None,None,'C · parcial + ninguna; no sumar al total'],
 ['Porcentaje con algún pendiente',None,None,None,'C · personas pendientes / personas'],
 [],['Observaciones: unidad distinta','Documental','Interno vigente','Diferencia','Clasificación'],
 ['Observaciones pendientes',3213,3094,None,'B/C'],
 ['Total de observaciones',24774,24774,None,'B'],
 ['Porcentaje de observaciones pendientes',None,None,None,'C'],
 ['Nuevos cierres frente a V10',T['cierres_nuevos_documentales'],T['cierres_nuevos_internos'],None,'C · comparación por clave'],
 [],['Lectura del resultado'],
 ['D · 119 equivalencias FCU2026 ya vigentes: IMDI 99; IRHU 14; NATP 3; ISEP 2; IFIN 1. No son nuevas reglas.'],
 ['E · 2.695 candidatos únicos dentro de 3.094 observaciones pendientes internas. Son propuestas: falta acreditar plan y vigencia temporal.'],
 ['E · No se acreditó fecha efectiva de asignación/migración del plan. Primera actividad observada y ANOINGRESO no la sustituyen.'],
 ['E · 24/63 combinaciones, 38,10%, usa otra unidad; no compararlo con porcentajes de personas. Escenario 501 personas no adoptado.'],
 ['Advertencia heredada: hoja 31 conserva 1.360 / 1.471 con tasa 92,7062%; ese cociente es 92,4541%. No corregido sin decisión.'],
 ['Fuentes: RESULTADOS_QA.json, QA_TRANSICIONES.json y registro privado por observación. Manifiesto de esta entrega: hashes y rutas.']]
if (O/'QA_CRONOLOGIA.json').exists():
 cr=json.load(open(O/'QA_CRONOLOGIA.json'))
 summary.append([f"B/C · {cr['personas_unicas_no_sumar_familias']} personas reúnen varios expedientes/planes dentro de una familia ({cr['personas_familia_con_varios_expedientes_planes']} relaciones persona–familia). E · Esto no acredita migración ni su fecha efectiva."])
f={}
for n in [5,6,7,8,9,10,13,14,15,16]:f['D'+str(n)]='=C%d-B%d'%(n,n)
for c in ['B','C']:
 f[c+'8']='=SUM(%s5:%s7)'%(c,c);f[c+'9']='=SUM(%s6:%s7)'%(c,c);f[c+'10']='=%s9/%s8'%(c,c);f[c+'15']='=%s13/%s14'%(c,c)
for n in [10,15]:f['D'+str(n)]='=(C%d-B%d)*100'%(n,n)
methods=[['Prueba retrospectiva | selección sin código objetivo'],['C · 17.826 observaciones regulares documentadas. Se evalúa después de seleccionar el candidato.'],
 ['No es validación externa ni prospectiva: familias heredadas; entrenamiento retrospectivo sin separación temporal.'],
 ['Resultado','MU ingreso actual (V10)','5 particiones por persona','Diferencia','Clasificación']]
v10=next(r['observaciones'] for r in Q['retrospectiva'] if r['metodo']=='MU_INGRESO_ACTUAL' and r['tipo']=='REGULAR'); cv=Q['validacion_por_persona']['resultados']
for k in ['ACIERTO','ERROR','EMPATE_NUEVOS','SIN_OFERTA_NUEVOS_COMPATIBLE','SIN_PERFIL','FECHA_AUSENTE_O_MULTIPLE']:methods.append([k,v10.get(k,0),cv.get(k,0),None,'C'])
methods += [['Total',None,None,None,'C'],['Aciertos / total evaluado',None,None,None,'C · incluye no seleccionados'],[],
 ['Interpretación'],['C · Todas las observaciones de una persona quedan en una misma partición. Su perfil de entrenamiento proviene de otras personas.'],
 ['E · 1.387 diferencias impiden usar la regla como equivalencia universal. No refutan la hipótesis de ingreso original al plan, cuya fecha falta.'],
 ['C · 2.695 candidatos únicos no adoptados; 399 casos sin candidato único. Sin nuevos cierres documentales o internos.'],
 ['A · Manual Oferta/Acceso 2027, pp. 65–66: estructura de código y cambios que afectan versión. Alcance 2027; no retroactividad supuesta.'],
 ['Fuentes: RESULTADOS_QA.json; scripts reproducibles del proyecto; datos privados por observación y partición.']]
mf={'B11':'=SUM(B5:B10)','C11':'=SUM(C5:C10)','B12':'=B5/B11','C12':'=C5/C11'}
for n in list(range(5,12))+[12]:mf['D'+str(n)]='=C%d-B%d'%(n,n)
mf['D12']='=(C12-B12)*100'
sources=[['Evidencia releída | alcance y límites'],['B · Localizadores completos verificados contra fila original; no equivalen a personas ni a aceptación SIES.'],
 ['Cortes efectivos de DATOSDEALUMNOS no acreditados. Años contenidos y fechas de archivo son conceptos distintos.'],
 ['Archivo / hoja','Filas o evidencias','Verificadas','SHA-256','Alcance']]
for r in E['por_archivo']:sources.append([r['archivo'],r['localizadores'],r['verificados'],r['sha256'],'B · identidad + código; revisar período/expediente por separado'])
sources.append(['TOTAL LOCALIZADORES',None,None,'','C · no personas'])
sr=len(sources);sf={'B'+str(sr):f'=SUM(B5:B{sr-1})','C'+str(sr):f'=SUM(C5:C{sr-1})'}
sources += [[],['Fuentes de reconstrucción del universo: ver INVENTARIO_FUENTES.csv (encabezados, hojas, años, hashes y límites de corte).'],
 ['B · PROMEDIOS: 70.000 filas, 57.131 en dimensiones seleccionadas; 24.774 observaciones únicas. Actividad 2019–2026.'],
 ['E · Un plan observado por expediente no demuestra ausencia de migraciones históricas. Requiere registro con plan anterior/nuevo y fecha efectiva.'],
 ['E · Base 2022–2026 derivada: el manifiesto de construcción conserva selección de RAW; no equivale a prueba de aceptación de cada fila.']]
payload=[{'name':'49_Reproduccion_V10','rows':summary,'formulas':f,'merged':[1,2,3,18,19,20,21,22,23,24]+([25] if len(summary)==25 else []),'percent':[10,15]},
 {'name':'50_Prueba_Personas','rows':methods,'formulas':mf,'merged':[1,2,3,14,15,16,17,18,19],'percent':[12]},
 {'name':'51_Evidencias_Releidas','rows':sources,'formulas':sf,'merged':[1,2,3,sr+2,sr+3,sr+4,sr+5],'percent':[]}]
(O/'payload_agregado.json').write_text(json.dumps(payload,ensure_ascii=False))
# Private Excel is a usable flat view; full nested provenance remains in adjacent JSON/CSV.
cols=['observacion_id','persona','CODCLI','carrera','sede_dimension','jornada_sies','plan','ano','periodo',
 'codigo_documental_antes_v10','codigo_documental_atribuible','codigo_interno_antes_v10','codigo_interno_adoptado',
 'codigo_propuesto','estado_documental','estado_interno','estado_propuesta','regla','requisito_pendiente',
 'transicion_documental','transicion_interna','tipo_doc_normalizado','fechas_declaradas','candidatos_calculados',
 'fuentes_promedios','evidencias_matricula','contextos_DA','trayectoria_planes_observada','prueba_fuera_persona']
def cell(v):return json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v
rr=[[cell(r.get(c,'')) for c in cols] for r in rows]
assert all(len(str(v))<32767 for row in rr for v in row)
(P/'payload_excel.json').write_text(json.dumps({'columns':cols,'rows':rr},ensure_ascii=False))
print(json.dumps({'observaciones':len(rows),'transiciones':T,'payload_agregado':str(O/'payload_agregado.json')},ensure_ascii=False))

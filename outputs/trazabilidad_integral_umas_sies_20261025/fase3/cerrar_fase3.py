"""Control independiente de las salidas y cierre agregado, sin editar fuentes."""
from pathlib import Path
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import csv, hashlib, json, subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(name,v): (OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def git(*args): return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()

r=load(OUT/'RESULTADOS_FASE3.json')
private=Path(r['privado']['ruta'])
slots=load(private/'VISTA_T1_T2_T3.json')
contexts=[c for s in slots for c in s['contextos']]
checks=[]
def check(name,value): checks.append({'control':name,'resultado':'PASA' if value else 'FALLIDO'})
check('3179 orígenes con dos posiciones cada uno',len(slots)==6358 and set(Counter(s['fila_origen_foto'] for s in slots).values())=={2})
check('2854 observaciones únicas, sin duplicación por unión',len(contexts)==len({c['observacion_id'] for c in contexts})==2854)
check('Poblaciones originales conservadas',dict(Counter(y for y,_ in {(s['anio_origen'],s['fila_origen_foto']) for s in slots}))=={2024:558,2025:1150,2026:1471})
check('2838 posiciones con contexto; 3520 sin contexto',sum(bool(s['contextos']) for s in slots)==2838 and sum(not s['contextos'] for s in slots)==3520)
check('2718 mismo código +37 otro respaldado +99 pendientes',Counter(c['relacion_codigo'] for c in contexts)=={'MISMO_CODIGO':2718,'CODIGO_DISTINTO_RESPALDADO':37,'CODIGO_PENDIENTE':99})
check('2742 documentales +13 internos aprobados +99 pendientes',Counter(c['respaldo_destino'] for c in contexts)=={'B/C_DOCUMENTAL_ANUAL_ATRIBUIDO':2742,'D_CORRESPONDENCIA_INTERNA_APROBADA':13,'E_PENDIENTE':99})
rows=load(private/'REVISION_FILAS_PROMEDIOS.json')
check('352 filas de evidencia coinciden en seis campos',len(rows)==352 and all(all(x['checks'].values()) and len(x['checks'])==6 for x in rows))
for a in r['resumen_periodo']:
    subset=[c for c in contexts if (c['anio_origen'],c['anio_observado'],c['periodo_nativo'])==(a['COHORTE_ORIGEN'],a['ANIO_OBSERVADO'],a['PERIODO_NATIVO'])]
    check(f"Control por origen {a['COHORTE_ORIGEN']} destino {a['ANIO_OBSERVADO']}-P{a['PERIODO_NATIVO']}",len(subset)==a['CONTEXTOS'] and a['CONTEXTOS']==a['MISMO_CODIGO']+a['CODIGO_DISTINTO_RESPALDADO']+a['CODIGO_PENDIENTE'])
protected=load(OUT.parent/'fase1/CADENA_Y_FUENTES.json')['preservacion']
check('13 fuentes y controles conservados por SHA-256',len(protected)==13 and all(sha(Path(p))==h for p,h in protected.items()))
check('Entradas adicionales conservadas por SHA-256',all(sha(Path(p))==h for p,h in r['fuentes_sha256'].items()))
check('Privados fuera de repositorios Git',subprocess.run(['git','-C',str(private),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0)
check('Permisos privados 700/600',private.stat().st_mode & 0o777==0o700 and all(p.stat().st_mode & 0o777==0o600 for p in private.iterdir()))
check('HEAD y cambios tracked previos conservados',git('rev-parse','HEAD')==r['git']['HEAD_antes'] and git('status','--short','--untracked-files=no')==r['git']['tracked_preexistente'])
check('Sin cambios staged',not git('diff','--cached','--name-only'))
ids={c['persona'] for c in contexts}|{c['CODCLI'] for c in contexts}|{s['documento_original'] for s in slots}
publicrows=[]
for p in OUT.glob('*.csv'):
    with p.open(encoding='utf-8-sig') as f: publicrows.extend(csv.DictReader(f,delimiter=';'))
check('Tablas agregadas sin identificadores originales',not any(str(v) in ids for x in publicrows for v in x.values() if len(str(v))>5))
assert all(c['resultado']=='PASA' for c in checks), 'Revisar QA antes del cierre'
timestamp=datetime.now(ZoneInfo('America/Santiago')).isoformat()
save('QA_FASE3.json',{'fecha':timestamp,'clasificacion':'C','estado':'PASA_TECNICO_CON_LIMITES','controles':checks,'total':len(checks),'limites':['No recalcula Excel ni tasas.','No certifica cobertura completa de matrícula/actividad; ausencia en diccionario no es deserción.','No acredita aceptación SIES ni fecha administrativa de cambio.']})

lines=['# Fase 3/6 — Seguimiento T1 en T2/T3 y excepciones','',
'**B/C — Resultado:** se reprodujo el seguimiento del padrón existente con el diccionario activo. Se conservan los 3.179 orígenes y sus 6.358 posiciones origen×período. No se agregan estudiantes ni se cambia ningún denominador.',
'', '**D — Alcance aprobado:** reutilizar códigos documentados y correspondencias internas ya autorizadas; revisar solo excepciones de carrera, sede, jornada y plan. No hubo adjudicaciones nuevas, cambios al diccionario ni modificación del Excel.',
'', '**C — Unidad:** un contexto identifica persona, CODCLI, plan y período; no equivale a una persona adicional ni a un retenido. Hay 2.854 contextos únicos en 2.838 posiciones, correspondientes a 1.527 orígenes. Las 3.520 posiciones restantes no tienen contexto en este diccionario; este resultado no prueba deserción ni ausencia en la foto de matrícula.',
'', '## Resumen de códigos por período', '', '| Cohorte de origen | Año observado | Período nativo | Padrón T1 | Mismo código | Otro respaldado | Código pendiente | Sin contexto |', '|---|---|---|---:|---:|---:|---:|---:|']
for a in r['resumen_periodo']:
    lines.append('| '+' | '.join(str(a[k]) for k in ['COHORTE_ORIGEN','ANIO_OBSERVADO','PERIODO_NATIVO','ORIGENES','MISMO_CODIGO','CODIGO_DISTINTO_RESPALDADO','CODIGO_PENDIENTE','SIN_CONTEXTO'])+' |')
lines += ['', '**B/C/D/E — Lectura:** las tres columnas de códigos cuentan contextos; “Sin contexto” cuenta posiciones de origen. Por eso no deben sumarse como estudiantes. El calendario heredado se conserva explícitamente: cohorte 2024 se observa en 2025; cohortes 2025 y 2026 en su propio año. No se convierte automáticamente un período académico nativo en fecha de cierre.',
'', '## Excepciones verificadas', '',
'- **B/C:** 2.718 contextos conservan exactamente el código completo T1. Otros 37 contienen un código distinto ya respaldado: 32 documentales anuales atribuidos y cinco correspondencias internas aprobadas (**D**).',
'- **B/C:** los 37 se distribuyen, sin solapamientos, en 23 diferencias de jornada (12 también de versión), ocho de carrera (siete también de versión) y seis solo de versión. No hay diferencias de sede en esos códigos. Una segunda carrera puede ser matrícula paralela: no se afirma abandono de la primera (**E**).',
'- **B/C:** se revisaron 149 contextos de excepción y sus 352 filas citadas de PROMEDIOS, con 2.112 comparaciones exactas de CODCLI, plan, año, período, documento y DV. Cero diferencias. El detalle preserva fuente, hoja y fila; está fuera de Git.',
'- **B/C:** en 2.828 contextos el mismo CODCLI conserva carrera UMAS y plan respecto del período nativo 1 disponible. En 26 no existe ese contexto comparable (**E**). No se infiere una fecha administrativa de cambio.',
'- **B/C:** entre T2 y T3, 1.316 trayectorias de expediente comparables conservan el plan; otras 222 no tienen ambos períodos. No se observó cambio de plan en las comparables. Esto no demuestra ausencia de cambios fuera de los períodos/cobertura revisados (**E**).',
'- **E:** quedan 99 contextos sin código de destino aplicable, vinculados a 55 orígenes; no son 99 estudiantes. En el foco heredado de carreras con varias versiones: 1.040 contextos documentales, 13 internos aprobados y 24 pendientes. Los 24 están incluidos en los 99.',
'- **B/C:** respecto de la instantánea v7, se reutilizan cinco recuperaciones documentales ya aprobadas en v8, todas con el mismo código T1. No son cierres nuevos de esta fase.',
'- **B/C/E:** 3.165 códigos de origen se recuperan en el índice MU de la API; 14 conservan respaldo literal de la fuente MU previamente verificada. Se mantienen visibles sin inventar una equivalencia de identidad ni excluirlos.',
'', '## Qué queda pendiente', '',
'**E — Atribución por contexto:** los 99 requieren evidencia de código aplicable al expediente/período. Los archivos EXCEPCIONES_AGREGADAS.csv y la vista privada conservan la regla y el requisito pendiente de cada observación. Un código T1 diferente de la jornada actual no se impone sobre una excepción histórica.',
'', '**E — Cobertura:** las 3.520 posiciones sin contexto requieren distinguir ausencia en el índice de ausencia en fuentes de matrícula/actividad. No se usan para bajar las tasas ni se reabren todos los históricos en esta fase. Los 26 contextos sin plan T1 comparable y las 14 anclas fuera del índice de la API son pendientes distintos; no se suman a los 99 como si fueran personas nuevas.',
'', '## Trazabilidad y conservación', '',
'**C:** seguir_t1.py consulta la API común a través del descriptor activo v8, contrasta las excepciones y produce una vista longitudinal. cerrar_fase3.py vuelve a contar las salidas y verifica preservación. RESULTADOS_FASE3.json registra entradas y hashes; MANIFEST_FASE3.json registra salidas y hashes.',
'', f'**C:** QA técnico: {len(checks)}/{len(checks)} controles correctos; 13 archivos protegidos sin cambios. Se corrigió durante el QA un doble incremento del contador auxiliar de pendientes; no afectó fuentes ni adjudicaciones. El recuento independiente final verifica 2.718 + 37 + 99 = 2.854.',
'', '**C/D:** no se recalcularon tasas, no se modificaron bases, denominadores, reglas ni los libros existentes. En particular, población T1-2026 de 1.471 y denominador específico T3-2026 de 1.467 se mantienen distintos según la entrega previa; esta auditoría no los reemplaza.',
'', f"**B/C:** rama `{r['git']['rama']}`, HEAD antes/después `{r['git']['HEAD_antes']}`. Sin commit ni push; PROYECTO_IPSS.json mantiene su modificación previa. Archivos agregados locales listos para revisión; esto no equivale a publicación en GitHub.",
'', '## Archivos', '',
'- RESUMEN_POR_PERIODO.csv: conteos por cohorte y período.',
'- SEGUIMIENTO_POR_CODIGO.csv: origen/destino, carrera UMAS, plan y respaldo agregados.',
'- CODIGOS_DISTINTOS_RESPALDADOS.csv: los 37 contextos agregados por combinación.',
'- EXCEPCIONES_AGREGADAS.csv: los 149 contextos de revisión, motivos, reglas y pendientes.',
'- PLANES_T2_T3.csv: comparación del plan entre períodos.',
f'- Detalle local restringido: `{private}`. VISTA_T1_T2_T3.json conserva todas las posiciones y los contextos; REVISION_FILAS_PROMEDIOS.json, los controles de evidencia; TRAYECTORIAS_PLANES.json, la comparación de planes. Permisos 700/600; fuera de repositorios Git.',
'', '**C — Reanudación:** usar esta vista y las excepciones para la siguiente fase autorizada. No volver a inferir códigos por totales ni promover pendientes por candidato único. La fase queda ejecutada con límites visibles, no como cobertura completa del 100%.', '']
(OUT/'INFORME_FASE3.md').write_text('\n'.join(lines))
save('CHECKPOINT_FASE3.json',{'fecha':timestamp,'fase':'3/6','estado':'EJECUTADA_CON_PENDIENTES_VISIBLES','clasificacion':'B/C/D/E','hitos':[
{'hito':'1/3','fuente':'descriptor v8 y ORIGENES_T1.json','accion':'Reutilizar anclas T1','resultado':'3179 orígenes conservados; 14 con respaldo MU literal fuera del índice API','archivo':'RESULTADOS_FASE3.json','pendiente':'14 anclas requieren completar índice, no excluir personas'},
{'hito':'2/3','fuente':'API común y PROMEDIOSDEALUMNOS_12166.xlsx/Hoja1','accion':'Seguir contextos y revisar excepciones','resultado':'2718 mismo código;37 otro respaldado;99 pendientes;352 filas comprobadas','archivo':'EXCEPCIONES_AGREGADAS.csv','pendiente':'99 códigos de destino;26 sin plan T1 comparable;3520 posiciones sin contexto; cifras no aditivas'},
{'hito':'3/3','fuente':'salidas y hashes de fuentes','accion':'QA y documentación','resultado':f'{len(checks)} controles correctos, originales y denominadores conservados','archivo':'QA_FASE3.json','pendiente':'No recalculado Excel; no cierre de cobertura ni aceptación SIES'}],
'siguiente':'Fase 4 según autorización y plan vigente; reutilizar vista y excepciones, no adjudicar nuevas versiones automáticamente.','no_repetir':['Conciliación anual completa de fase 2','Recálculo de tasas cerradas','Búsquedas aproximadas de identidad','Inferencia individual por totales agregados'],'commit':False,'push':False})
outputs={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST_FASE3.json'}
spec=ROOT/'docs/ESPECIFICACION_FASE3_SEGUIMIENTO_T1_20261025.md'
save('MANIFEST_FASE3.json',{'fecha':timestamp,'proceso':'Retención intertrimestral IPSS 162','fase':'3/6','alcance':'Códigos documentados T1, seguimiento y revisión de excepciones T2/T3; sin tasas nuevas','clasificaciones':{'B':'Fuentes y conteos observados','C':'Consulta exacta, agregación y QA','D':'Correspondencias internas previamente aprobadas','E':'Atribución/cobertura pendiente','A':'No se formula una nueva regla oficial'},'diccionario':r['diccionario'],'especificacion':{'ruta':str(spec),'sha256':sha(spec)},'entradas':r['fuentes_sha256'],'fuentes_protegidas':protected,'salidas':outputs,'privados_locales':r['privado'],'privacidad':'Salidas públicas agregadas, sin identificadores; detalle exclusivamente local fuera de Git. No se subió información.','qa':'QA_FASE3.json','git':r['git'],'bases_denominadores_canon_modificados':False,'recalculo_excel':False})
print(json.dumps({'QA':len(checks),'reporte':str(OUT/'INFORME_FASE3.md'),'sha256_informe':sha(OUT/'INFORME_FASE3.md'),'sha256_manifiesto':sha(OUT/'MANIFEST_FASE3.json')},ensure_ascii=False))

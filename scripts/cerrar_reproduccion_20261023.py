"""QA final y documentación persistente. No añade al índice Git ni publica."""
import csv,json,hashlib,re,sys,subprocess,zipfile,datetime,stat
from pathlib import Path
from collections import Counter,defaultdict
import openpyxl
O=Path(sys.argv[1]).resolve();R=Path(__file__).resolve().parents[1]
M=json.load(open(O/'MANIFEST.json'));P=Path(M['privado']);Q=json.load(open(O/'RESULTADOS_QA.json'));X=json.load(open(O/'QA_EXCEL.json'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
rr=json.load(open(P/'OBSERVACIONES_PRIVADAS.json'));pd=json.load(open(P/'payload_excel.json'))
px=P/'REVISION_PRIVADA_PUENTE_REPRODUCIDO_20261023.xlsx'
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
assert stat.S_IMODE(P.stat().st_mode)==0o700
w=openpyxl.load_workbook(px,read_only=True,data_only=True);it=iter(w['Observaciones'].values);heads=next(it);assert list(heads)==pd['columns']
n=0;bad=0;numeric_ids=0
for row,expected in zip(it,pd['rows'],strict=True):
 n+=1;bad+=any((a if a is not None else '')!=(b if b is not None else '') for a,b in zip(row,expected,strict=True))
 numeric_ids+=not isinstance(row[1],str) or not isinstance(row[2],str)
w.close();assert n==24774 and bad==numeric_ids==0
# Independent partitions from the serialized individual registry.
parts={}
for label,key in [('documental','codigo_documental_atribuible'),('interno','codigo_interno_adoptado')]:
 person=defaultdict(list)
 for x in rr:person[x['persona']].append(bool(x[key]))
 c=Counter('sin_pendientes' if all(v) else 'parcialmente_resueltas' if any(v) else 'ninguna_observacion_resuelta' for v in person.values())
 assert sum(c.values())==5901
 expected=Q['linea_base']['documental'] if label=='documental' else Q['equivalencias']['interno']
 assert all(c[k]==expected[k] for k in c)
 parts[label]=dict(c)
# Privacy: exact known normalized RUT/CODCLI tokens, no individual rows in the new aggregate.
ids={x['persona'] for x in rr}|{x['CODCLI'] for x in rr}
leaks=[]
book=O/'RETENCION_IPSS_PUENTE_REPRODUCIDO_20261023_V11.xlsx'
aw=openpyxl.load_workbook(book,read_only=True,data_only=False)
for s in aw:
 for row in s:
  for c in row:
   if isinstance(c.value,str) and ids.intersection(re.findall(r'[A-Za-z0-9]+(?:-[0-9K])?',c.value)):
    leaks.append({'hoja':s.title,'celda':c.coordinate})
aw.close();assert not leaks,leaks[:3]
inputs=json.load(open(O/'FUENTES_HASHES.json'))
for e in json.load(open(O/'QA_RELECTURA_MULTIPROCESO.json'))['por_archivo']:inputs[e['archivo']]=e['sha256']
changed=[p for p,h in inputs.items() if sha(p)!=h];assert not changed
old=json.load(open(O/'GIT_ANTES.json'));now={}
for path,b in old.items():
 now[path]={k:subprocess.check_output(['git','-C',path,*args],text=True).strip() for k,args in [('head',['rev-parse','HEAD']),('rama',['branch','--show-current']),('remotos',['remote','-v']),('status',['status','--short'])]}
 assert now[path]['head']==b['head'] and now[path]['rama']==b['rama'] and now[path]['remotos']==b['remotos']
dump(O/'GIT_DESPUES.json',now)
qa={'estado':'OK_CON_ADVERTENCIAS','privado_fuera_git':True,'permisos_directorio':'0700','observaciones_excel_privado':n,
 'filas_excel_privado_diferentes_registro':bad,'identificadores_excel_no_texto':numeric_ids,'particiones_independientes':parts,
 'coincidencias_identificadores_conocidos_libro_agregado':leaks,'fuentes_huella_conservada':len(inputs),'fuentes_alteradas':changed,
 'heads_ramas_remotos_conservados':True,'commit':False,'push':False,'errores_nuevas_formulas':X['errores_hojas_nuevas'],
 'limites':['Privacidad comprueba identificadores del universo y ausencia de datos individuales en nuevas hojas; no una certificación universal de información histórica',
 'Sin apertura y recálculo en Excel nativo; estilos/formato se verificaron con render y OOXML',
 'Desfase heredado en hoja 31 conservado, no corregido; tasas anteriores no recertificadas',
 'Falta acreditar ingreso original al plan y migraciones; no adoptar candidatos por totales coincidentes']}
dump(O/'QA_FINAL.json',qa)
dump(O/'FUENTES_HASHES_FINAL.json',inputs)
cr=json.load(open(O/'QA_CRONOLOGIA.json'))
report=f'''# Reproducción de la conciliación UMAS–SIES · 23-oct-2026

## Resultado y alcance

**B/C. Se reprodujo V10 sin cambiar códigos adoptados, reglas, tasas o denominadores.** Universo: 5.901 personas, 6.622 expedientes y 24.774 observaciones. Las 24.774 claves y sus estados/códigos antes y después coinciden. No hay nuevos cierres respaldados; no se aplicó el escenario de 501 personas. QA técnico: OK_CON_ADVERTENCIAS. La investigación del ingreso original al plan queda pendiente, no resuelta por ausencia de cambios.

Proceso: conciliación histórica UMAS–SIES, vinculada al subproyecto retención IPSS 162. Ejecución: 23-oct-2026. Actividad observada PROMEDIOS: 2019–2026; matrícula individual releída: 2010–2026, sin inferir cobertura integral. La presencia de ANOMATRICULA=2027 en DATOSDEALUMNOS no demuestra matrícula SIES 2027 enviada. Principal: avance_curricular/feature/ire-2026. Las fuentes y huellas exactas están en FUENTES_HASHES_FINAL.json y el inventario.

| Personas (categorías excluyentes) | Documental | Interno vigente | Respaldo |
|---|---:|---:|---|
| Sin observaciones pendientes | 4.063 | 4.150 | C |
| Parcialmente resueltas | 699 | 699 | C |
| Ninguna observación resuelta | 1.139 | 1.052 | C |
| Total | 5.901 | 5.901 | B/C |

**C. Con algún pendiente**: documental 1.838/5.901 = 31,15%; interno 1.751/5.901 = 29,67%. Esta fila es subtotal (parcial + ninguna), no otra categoría sumable. Observaciones pendientes: 3.213 y 3.094. El 38,10% de 24/63 combinaciones pertenece a otra unidad; no es evolución comparable ni retención.

## Qué se releyó y cómo se atribuyó

- **B/C.** PROMEDIOSDEALUMNOS_12166.xlsx, Hoja1: 70.000 filas de asignaturas; 57.131 pertenecen a las dimensiones estudiadas, agrupadas en 24.774 observaciones. La unidad es persona + CODCLI/carrera + sede/jornada + plan + año/período; no una fila por asignatura. Se mantienen las filas de evidencia en listas, sin expandir uniones muchos-a-muchos.
- **B.** DATOSDEALUMNOS_12159 y 11248: 15.185 y 14.637 filas. No contienen una columna explícita PLAN_DE_ESTUDIO/CODPESTUD en sus encabezados efectivos. Tienen ANOINGRESO, PERIODOINGRESO, ANOMATRICULA, PERIODOMATRICULA, FECHAMATRICULA y FECHAFIRMA. Sus cortes efectivos no se acreditan por nombre, carpeta o docProps. El plan observado procede de PROMEDIOS y catálogos, no de una columna inexistente de estos dos DA.
- **B/C.** Relectura de 12 hojas MAT 2010–2021 y BASE_RETENCION_MU 2022–2026; esta última conserva su carácter derivado, sin convertirla en evidencia primaria de aceptación. El manifiesto de construcción original identifica sus RAW y selección. Se releen 16 hojas contando los dos DA y PROMEDIOS.
- **B/C.** Relectura adicional de 49.218 localizadores completos de 33 archivos multiproceso: 49.218 coinciden en identidad y código; cero discrepancias. Son evidencias, no personas. No se declara haber reexplorado exhaustivamente todas las fuentes posibles. La comprobación no da automáticamente vigencia temporal a una evidencia de titulados/avance curricular ni prueba aceptación SIES.
- **C.** Primero identidad exacta normalizada, luego familia carrera/sede/jornada, año, expediente y contexto DA. RUT original y normalizado se conservan por separado. No se usan nombres ni coincidencias aproximadas. Las 86 alertas de atribución no se rotulan automáticamente como códigos contradictorios.
- **D/C.** Se revalidan únicamente las 119 equivalencias internas FCU2026 ya vigentes (IMDI 99, IRHU 14, NATP 3, ISEP 2, IFIN 1), con alcance de año, plan, carrera, sede y ausencia de alternativas. Permiten 87 personas completamente resueltas adicionales y una parcialmente, pero no prueban envío individual. No se crean reglas nuevas.

## Mejora de la prueba retrospectiva

**C.** Se reproduce la prueba MU ingreso actual en 17.826 observaciones regulares: 15.029 coincidencias, 1.494 diferencias, 1.044 empates, 257 sin oferta compatible y 2 sin fecha única. El código objetivo no participa directamente de la selección del candidato; se compara después. Los perfiles heredados podrían contener información relacionada con el objetivo, por lo que esta reproducción por sí sola no elimina circularidad.

**C.** Prueba adicional en cinco particiones deterministas por persona: todas las observaciones de la misma persona quedan juntas y los perfiles se aprenden únicamente de las otras particiones. Resultado: 15.171 coincidencias, 1.387 diferencias, 1.228 empates, 34 sin oferta compatible, 4 sin perfil y 2 sin fecha única. Es evaluación retrospectiva, no pronóstico: no hay separación temporal y las familias se heredan del mapa existente. Las personas de cada resultado pueden solaparse; sus conteos por resultado no se suman. Las 1.387 diferencias impiden adoptar una regla universal. Tampoco refutan una hipótesis distinta basada en ingreso original al plan, pues esa fecha sigue sin acreditarse.

## Ingreso original, planes y reingreso

**B/C.** Cada uno de los 6.622 expedientes seleccionados tiene una sola etiqueta de plan en las observaciones de PROMEDIOS revisadas. Al ampliar a persona–familia, hay {cr['personas_unicas_no_sumar_familias']} personas con varios expedientes/planes, distribuidas en {cr['personas_familia_con_varios_expedientes_planes']} relaciones persona–familia. La cronología privada conserva primer y último período observado de cada combinación. **E:** no prueba que hubiera migración administrativa ni fecha efectiva; tampoco excluye cambios anteriores no conservados en la exportación.

**B/C. Caso C3/J4:** 674 observaciones de 87 personas documentan I162S2C3J4V2 y ANIO_ING_ACT=2022. Incluyen planes IETMREOL20211 e ICRE20241 en años diferentes; el detalle agregado y las filas exactas están en QA_CRONOLOGIA.json y el registro privado. **E:** las etiquetas y el año de ingreso no autorizan a sustituir V2 por V1. Falta acto/evidencia de asignación del plan o migración con vigencia efectiva.

**A (alcance 2027).** Manual de Oferta/Acceso 2027, páginas físicas 65–66, conservado en data/reglas_negocio/20261015/fuentes/manual_oferta_acceso_2027_texto_completo.json: estructura del código y cambios relevantes para versión. No se aplica retroactivamente por supuesto. **E:** ordenar el debut en oferta o hacer coincidir totales no identifica por sí solo la versión individual ni elimina versiones anteriores.

## Pendientes exactos y decisiones no adoptadas

| Observaciones internas pendientes | Cantidad | Falta | Clasificación |
|---|---:|---|---|
| Candidato único condicionado | 2.695 | Fecha efectiva de asignación del plan al expediente, perfil individual y condiciones de continuidad/reingreso/migración | E |
| Fecha ausente o múltiple | 32 | Resolver qué campo acredita ingreso original a ese programa/plan | E |
| Sin perfil | 203 | Duración y tipo de plan aplicables, con fuente individual o equivalencia formal | E |
| Varios candidatos | 94 | Atributo discriminante o equivalencia vigente con fecha efectiva | E |
| Sin grupo | 51 | Correspondencia histórica de carrera/sede/jornada | E |
| Sin oferta compatible | 19 | Oferta histórica aplicable y alcance del perfil | E |
| Total | 3.094 | No se sustituye «pendiente» por cero ni se adopta el candidato por ser único | C |

**E/D.** No se pide una tabla inexistente como única salida: la trayectoria reconstruida deja lista la evidencia para formalizar una equivalencia institucional si se demuestra y aprueba su alcance. Hasta entonces, persona localizada, código anual, propuesta y equivalencia interna son estados diferentes. Ningún candidato nuevo fue promovido.

## Archivos y QA

- Libro agregado V11: conserva las 48 hojas de V10 byte a byte y sus 13 gráficos; agrega 49_Reproduccion_V10, 50_Prueba_Personas y 51_Evidencias_Releidas. Las nuevas hojas contienen 32 fórmulas con caché verificada y cero errores de celda. La copia de Escritorio es idéntica. Los porcentajes nuevos son pendientes/total, no tasas de retención. Diferencias entre porcentajes se expresan en puntos porcentuales.
- Privado local: REVISION_PRIVADA_PUENTE_REPRODUCIDO_20261023.xlsx, 24.774 observaciones comprobadas celda por celda contra el registro; identificadores como texto. JSON y CSV adyacentes conservan todos los campos y listas de procedencia. TRAYECTORIAS_MULTIPLES_PERSONA_FAMILIA.json agrega la investigación temporal. Directorio fuera de cualquier Git, permisos 0700; no hay copia individual en el repositorio.
- Fórmulas nuevas recalculadas con Artifact Tool y contrastadas mediante lectura independiente. No se ha abierto en Excel nativo. No se certifica cero error en todas las tasas heredadas.
- **B/C. Advertencia heredada:** hoja 31_Comparacion_Historica, MU1/T3 2026 conserva 1.360 y 1.471 junto a tasa 0,92706203135651 (compatible con 1.360/1.467). El cociente 1.360/1.471 es 0,9245411284840245. Está advertido; no se modificó ninguna cifra sin autorización.
- Las {len(inputs)} huellas de fuentes verificadas se conservan. No se sobrescribieron fuentes, V10, V7 o el motor anual. No hubo commit, push, merge, PR ni cambio de rama; los cambios previos ajenos permanecen.

## Reproducción

Ejecutar scripts/reproducir_puente_20261023.py con --reanudacion apuntando al directorio privado reanudacion de esta entrega. Ese snapshot mínimo permite reanudar sin los temporales /tmp originales. Después ejecutar verificar_evidencias_puente_20261023.py, auditar_cronologia_reproduccion_20261023.py, preparar_entrega_reproduccion_20261023.py, crear_entrega_reproduccion_20261023.mjs, ensamblar_reproduccion_20261023.py y cerrar_reproduccion_20261023.py sobre la carpeta generada. Usar dependencias y rutas locales declaradas en el checkpoint. El creador JS requiere @oai/artifact-tool y puede necesitar memoria de proceso de 8 GB para el detalle. El primer intento con 2 GB no completó el privado; el reintento verificado sí lo completó.

Los scripts mantienen huellas y condiciones de detención. El aprendizaje por partición no cambia el canon. El siguiente avance sustantivo es evaluar las 374 trayectorias múltiples contra evidencia efectiva de plan y revisar los perfiles faltantes, no repetir la búsqueda universal por nombre ni imponer 0%.
'''
(O/'INFORME_REPRODUCCION.md').write_text(report)
phase=[
 (1,'Fuentes y Git','Acceso y huellas verificados; cortes efectivos DA pendientes','INVENTARIO_FUENTES.csv; FUENTES_HASHES_FINAL.json; GIT_ANTES.json'),
 (2,'Reproducción','Universo, códigos y equivalencias vigentes reproducidos','QA_BASE_INICIAL.json; QA_TRANSICIONES.json'),
 (3,'Prueba retrospectiva','V10 reproducido y prueba por persona ejecutada; no validación externa','RESULTADOS_QA.json'),
 (4,'Ingreso original y cambios','Cronología observada reconstruida; asignación efectiva/migración NO resuelta','QA_CRONOLOGIA.json; trayectoria privada'),
 (5,'Reglas y propuestas','Solo reglas vigentes; 2.695 propuestas no adoptadas','RESULTADOS_QA.json; registro privado'),
 (6,'Registro y archivos','24.774 observaciones privadas; resumen agregado separado','QA_EXCEL.json; QA_FINAL.json'),
 (7,'Cierre y reanudación','QA con advertencias; pendientes semánticos explícitos; sin publicar','MANIFEST.json; CHECKPOINT.md; PROMPT_REANUDACION.md')]
lines=['# Bitácora de fases — 23-oct-2026','Cada fase tuvo inventario/acción, contraste y registro; el cierre técnico no cierra la falta de evidencia temporal.']
for n,name,state,evidence in phase:
 for h,act in [(1,'Entrada y alcance'),(2,'Ejecución/contraste'),(3,'Resultado y pendiente')]:lines.append(f'Fase {n}/7 · Hito {h}/3 — {name}. {act}: {state}. Evidencia: {evidence}. Fuentes: inventario y manifiesto de esta ejecución.')
(O/'BITACORA.md').write_text('\n\n'.join(lines)+'\n')
checkpoint=f'''# Checkpoint · reproducción UMAS–SIES

Ejecución terminada con pendientes semánticos. No nuevas reglas adoptadas. Resultado: documental 1.838 personas/3.213 observaciones pendientes; interno 1.751/3.094. Universo fijo 5.901/6.622/24.774.

Agregado: {book}
Privado: {px}
Reanudación privada: {P/'reanudacion'}
Registro completo: {P/'OBSERVACIONES_PRIVADAS.json'}
Evidencia adicional: {P/'TRAYECTORIAS_MULTIPLES_PERSONA_FAMILIA.json'}
Informe: {O/'INFORME_REPRODUCCION.md'}

Rama/HEAD principal: feature/ire-2026 / 80ca13a5a249a1a2bd53a699f5f73689b1f53040. Canon intacto. No commit/push. Ver GIT_DESPUES.json antes de continuar; no atribuir cambios ajenos a este estudio.
Python: /Users/alexi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
Node: /Users/alexi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
Node modules: /Users/alexi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules

Pendiente principal: acreditar fecha original/asignación efectiva del plan, migraciones y equivalencias históricas. Analizar trayectorias múltiples sin convertir proximidad temporal en prueba. Mantener separación entre propuestas, correspondencias internas y documento individual anual. No trasladar códigos posteriores hacia atrás. Desfase heredado de hoja 31 aún abierto; no tocar denominadores sin autorización.
'''
(O/'CHECKPOINT.md').write_text(checkpoint)
(O/'PROMPT_REANUDACION.md').write_text(f'''Continúa la conciliación UMAS–SIES IPSS en avance_curricular. Lee primero {O/'CHECKPOINT.md'}, {O/'INFORME_REPRODUCCION.md'} y MANIFEST.json, verifica sus hashes y acceso real. No presupongas acceso al historial del chat. No repitas lo reproducido si las fuentes conservan huella. Revisa AGENTS/agent.md y contratos aplicables. Sin commit, push, uploads, cambios de canon, fuentes ni denominadores.

Investiga las 374 personas/377 relaciones persona–familia con múltiples expedientes/planes del registro privado. Busca evidencia efectiva de asignación/migración dentro de las fuentes ya gobernadas y distingue regular, continuidad y reingreso. El listado no prueba cambios administrativos por sí solo. Conserva 2.695 candidatos condicionados y los demás pendientes; no adoptes por candidato único ni por concordancia agregada. El año de actividad no es ingreso original al plan. Los DA 12159/11248 no contienen columna explícita de plan.

Mantén por separado documental (1.838 personas pendientes) e interno vigente (1.751), universo 5.901 personas/6.622 expedientes/24.774 observaciones. Las 119 equivalencias FCU2026 son vigentes, no nuevos cierres. La nueva prueba de cinco particiones por persona tiene 1.387 diferencias; no autoriza regla universal. No se adoptó 501/5.901. No usar 24/63 como porcentaje de personas.

Clasifica A/B/C/D/E. Registra por observación fuente/hoja/fila/hash, identidad original y normalizada, expediente, plan, fechas, código observado, propuesto y adoptado, regla y evidencia pendiente. Identificadores solo en {P}, fuera de Git; agregado sin datos personales. Preserva las hojas previas y 13 gráficos. Reporta mejoras respaldadas y bloqueos exactos; no prometas 0%. Verifica QA y declara límites de recálculo. Cada avance comienza Fase X/X · Hito Y/Y. Ejecuta las tareas autorizadas y produce derivados versionados, no solamente un plan.
''')
privatefiles={p.name:sha(p) for p in P.iterdir() if p.is_file() and p.name!='MANIFEST_PRIVADO.json'}
dump(P/'MANIFEST_PRIVADO.json',{'fecha':datetime.datetime.now().astimezone().isoformat(),'fuentes':inputs,'salidas':privatefiles,'privacidad':'Fuera de Git, directorio0700; sin publicación','qa':qa})
scripts=[p for p in (R/'scripts').glob('*reproduccion_20261023*')]+[R/'scripts/reproducir_puente_20261023.py',R/'scripts/verificar_evidencias_puente_20261023.py']
M.update(fecha_cierre=datetime.datetime.now().astimezone().isoformat(),estado='OK_CON_ADVERTENCIAS',resultado='V10 reproducido; no nuevos cierres; cronología efectiva pendiente',
 fuentes_hashes=inputs,salidas_privadas_hashes={p.name:sha(p) for p in P.iterdir() if p.is_file()},
 salidas_agregadas_hashes={p.name:sha(p) for p in O.iterdir() if p.is_file() and p.name!='MANIFEST.json'},scripts_hashes={str(p):sha(p) for p in scripts},
 escritorio={X['copia_escritorio']:sha(X['copia_escritorio'])},git_despues={p:{k:v for k,v in d.items() if k!='status'} for p,d in now.items()},
 pendientes=['Fecha efectiva de plan/migración no acreditada','Cortes efectivos DA no acreditados','1.751 personas internas pendientes','Desfase previo hoja31 no corregido'],
 cambios_adoptados=0,canon_modificado=False,commit=False,push=False)
dump(O/'MANIFEST.json',M)
print(json.dumps({'estado':qa['estado'],'privado_filas':qa['observaciones_excel_privado'],'agregado_sha256':sha(book),'privado_sha256':sha(px),'fuentes_sin_cambio':len(inputs),'identificadores_agregado':len(leaks)},ensure_ascii=False))

"""Documenta la candidata y comprueba ausencia de identificadores en salidas públicas."""
from pathlib import Path
import json,hashlib,re,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
r=json.loads((OUT/'RESULTADOS.json').read_text());q=json.loads((OUT/'QA.json').read_text())
private=Path(r['detalle_privado']['ruta']);p=json.loads(private.read_text())['propuestas']
assert sha(private)==r['detalle_privado']['sha256'] and len(p)==644
assert len({v['contexto']['persona'] for v in p})==316
assert len({(v['contexto']['persona'],v['contexto']['CODCLI'],v['contexto']['carrera']) for v in p})==375
assert all(v['codigo_adoptado'] is None and v['estado']=='PROPUESTA_NO_APROBADA' for v in p)
assert q['estado']=='PASS_CANDIDATA_NO_ACTIVA'
controls=len(q['controles'])
text=f'''# Fase 2/4 · Hito 2.3 · Propuesta contextual preparada

[B/C] Fecha: 27-10-2026. Proceso: avance curricular histórico IPSS 162. Referencia anual: actividad 2025 del proceso SIES 2026; historia acumulada observada hasta 2025. Los períodos UMAS 1–5 conservan su significado de origen, sin conversión automática a trimestres.

[C/E] Estado: **candidata lista para revisar; no activada**. La fase 2 no está cerrada integralmente. Se reutilizaron las auditorías de identidad y contexto, sin reiniciar búsquedas generales ni construir un Excel.

## Qué se comprobó

[B/C] Se reprodujeron 815 contextos sin período indexado y los 644 candidatos concordantes: 316 personas, 375 expedientes, 23 códigos SIES, años 2019–2025. Cada candidato tiene actividad por identidad completa y CODCLI, plan/carrera/jornada concordantes con un contexto existente del mismo año y código MU anual único. Se contrastaron 751 enlaces con 550 filas MU distintas, sin discrepancia final. Estas cantidades incluyen la revisión de los 815, no solo los 644.

[B/C] La candidata incluye referencias originales PROMEDIOS (archivo, Hoja1, fila), evidencia MU y observaciones ancla. La sede procede de la familia gobernada y MU; PROMEDIOS no la acredita directamente. No se encontraron otras combinaciones plan/carrera/jornada en la actividad anual revisada para estos expedientes.

[E] Eso respalda una propuesta interna acotada; no demuestra fecha efectiva del plan ni ausencia de migraciones fuera de la cobertura revisada. No acredita envío/aceptación SIES ni la equivalencia con el correlativo curricular PLAN_ESTUDIOS.

## Resultado ejecutivo del escenario

[C/E] Foco fijo: **5.144 contextos, 488 personas y 1.032 expedientes**, vinculados a 489 filas observadas de una precarga de 2.371 registros. No representa todo el diccionario ni el denominador de retención de 2.379.

| Indicador | Vigente observado [B/C] | Si se aprueban los 644 [C/E] |
|---|---:|---:|
| Contextos con código atribuido | 3.126 | 3.770 |
| Contextos pendientes | 2.018 | 1.374 |
| Personas sin contextos pendientes en este foco | 41 | 162 |
| Personas parcialmente atribuidas | 402 | 281 |
| Personas sin código atribuido | 45 | 45 |
| Expedientes sin contextos pendientes | 262 | 571 |
| Expedientes parcialmente atribuidos | 474 | 165 |
| Expedientes sin código atribuido | 296 | 296 |
| Filas H113 con atribución anual pendiente | 288 | 194 |
| Filas H113 con contexto acumulado pendiente | 448 | 327 |

[C/E] La propuesta resolvería todos los contextos observados del foco de 121 personas y parte de los de otras 195. No significa 121 estudiantes con avance curricular integral validado: el plan curricular y los reconocimientos son controles distintos.

[C/E] Las filas con códigos acumulados completos pero con cambios de código pasarían de 2 a 21. El escenario conserva esas diferencias; no fuerza toda la historia al código de destino. La actividad atribuida a otra familia o versión tampoco se excluye automáticamente: debe comprobarse su reconocimiento en el plan de destino.

## Control matemático

[C] Totales del foco idénticos antes y después: 4.296 unidades cursadas y 3.792 aprobadas en 2025; 21.781 cursadas y 20.038 aprobadas acumuladas. Son aportes a filas H113, no personas ni asignaturas institucionales únicas. La proyección solo redistribuye su atribución.

| Unidades pendientes de atribución | Vigente [B/C] | Proyección [C/E] |
|---|---:|---:|
| Cursadas 2025 | 1.729 | 1.523 |
| Aprobadas 2025 | 1.556 | 1.377 |
| Cursadas acumuladas | 7.132 | 5.743 |
| Aprobadas acumuladas | 6.529 | 5.306 |

[C] Una segunda suma, candidato por candidato y fila de destino, reprodujo exactamente la partición de unidades del escenario. La diferencia entre 1.386 filas de actividad de contextos únicos candidatos y 1.389 aportes acumulados redistribuidos se debe a la reutilización de contextos en filas H113; no se interpreta como personas adicionales.

## Decisión pendiente

[E] Solicitud de aprobación concreta: permitir la correspondencia interna solo para los **644 contextos individualizados** en la candidata, bajo la conjunción de las comprobaciones anteriores. No adoptar una regla universal de propagación, ni convertir estas propuestas en evidencia documental del período. Mantener el código anual observado separado del código interno propuesto y registrar la decisión antes de activar.

[B/C] La regla vigente `NO_PROPAGAR_VERSION_ENTRE_CONTEXTOS` no se modificó. No se aplicó ninguna de las 644 propuestas. La v11 activa conserva sus 25.902 observaciones y sus adjudicaciones.

## Pendientes precisos y siguiente paso

[E] De los 815 revisados quedan 171 sin propuesta: 107 con MU anual única pero sin contexto concordante del año; 23 con MU de otra familia; 38 sin MU del año localizada en el índice; 3 sin familia gobernada para la jornada. Los otros pendientes del foco son 762 expedientes no indexados, 1 carrera distinta en el índice y 440 excepciones existentes. Sumados a los 171 dan 1.374, después de aprobar la propuesta, no antes.

[C/E] Secuencia: (1) decisión sobre esta candidata; (2) si se aprueba, incorporación aditiva y regresión completa del consumidor, sin sustituir fuentes; (3) atender los grupos restantes con sus causas ya identificadas; (4) iniciar fase 3 con atribuciones aprobadas y excepciones explícitas. Sigue pendiente el vínculo curricular PLAN_ESTUDIOS y el tratamiento de reconocimientos. No se solicita repetir búsquedas ya agotadas.

## QA y entrega

[C] **{controls} controles de construcción y comparación: PASS_CANDIDATA_NO_ACTIVA.** El control final de privacidad se registra aparte en QA_ENTREGA.json. Este PASS no valida la activación, cobertura completa, indicadores finales ni una carga SIES.

[C] La primera ejecución encontró un error técnico al cargar un fragmento del script previo (IndentationError); se corrigió y la ejecución completa posterior pasó. No fue discrepancia de datos ni alteración de fuentes. Registro: INCIDENCIA_TECNICA.json.

[B/C] Rama feature/ire-2026, HEAD 262f445828f7e939fac59c3cc76d0bb20a101746 antes y después. Los cuatro cambios previos permanecen idénticos por hash. Fuentes, H113, H114B, diccionario activo y resultados anteriores se conservaron. Sin commit, push, carga externa ni nuevo Excel.

[C] Detalle individual fuera de Git: `{private}`. SHA-256: `{sha(private)}`. Permisos privados. Las salidas de esta carpeta son código y agregados; hashes y procedencia completa en MANIFEST.json.
'''
(OUT/'INFORME_FASE2.md').write_text(text)
dump('INCIDENCIA_TECNICA.json',{'clase':'C','estado':'CORREGIDA','primera_ejecucion':'IndentationError al extraer un fragmento de código después de un comentario. No se completó la simulación.','correccion':'Omitir el resto de la línea del comentario al reutilizar el fragmento.','validacion':'Compilación del script y ejecución completa posterior PASS_CANDIDATA_NO_ACTIVA.','fuentes_modificadas':False})
# Los tokens exactos se leen exclusivamente del archivo privado; no se registran.
tokens=set()
for v in p:
 c=v['contexto'];tokens.update([c['persona'],c['persona'].split('-')[0],c['CODCLI']])
pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(map(re.escape,sorted(tokens,key=len,reverse=True)))+r')(?![A-Za-z0-9])')
public=[x for x in OUT.iterdir() if x.is_file() and x.name not in ('MANIFEST.json','QA_ENTREGA.json')]
leaks=[x.name for x in public if pattern.search(x.read_text())]
qa={'clasificacion':'C','estado':'PASS_ENTREGA_CANDIDATA' if not leaks else 'FAIL','archivos_publicos_revisados':len(public),'archivos_con_identificador_exacto':leaks,'candidatos_recontados':len(p),'personas_recontadas':len({v['contexto']['persona'] for v in p}),'expedientes_recontados':len({(v['contexto']['persona'],v['contexto']['CODCLI'],v['contexto']['carrera']) for v in p}),'todos_sin_adoptar':all(v['codigo_adoptado'] is None for v in p),'privado_fuera_git':not private.is_relative_to(ROOT),'permiso_privado_octal':oct(private.stat().st_mode&0o777),'controles_previos_pass':controls,'limite_privacidad':'Búsqueda de identificadores del foco y salidas construidas por lista explícita de agregados; no auditoría de todo el repositorio.'}
dump('QA_ENTREGA.json',qa)
assert not leaks
m=json.loads((OUT/'MANIFEST.json').read_text())
m['especificacion']={'ruta':'docs/ESPECIFICACION_CANDIDATA_644_AVANCE_20261027.md','sha256':sha(ROOT/'docs/ESPECIFICACION_CANDIDATA_644_AVANCE_20261027.md')}
m['salidas']={x.name:sha(x) for x in OUT.iterdir() if x.is_file() and x.name!='MANIFEST.json'}
dump('MANIFEST.json',m)
assert not pattern.search((OUT/'MANIFEST.json').read_text())
print(json.dumps({'qa':qa,'informe_sha256':sha(OUT/'INFORME_FASE2.md'),'manifest_sha256':sha(OUT/'MANIFEST.json')},ensure_ascii=False,indent=2))

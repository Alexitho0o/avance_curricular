"""Persist aggregate-only delivery evidence; never publish private payload contents."""
from pathlib import Path
import json,hashlib,datetime,subprocess,os
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
O=R/'outputs/retencion_intermedia_t2_t3/20261021_144031'
OLD=R/'outputs/retencion_intermedia_t2_t3/20261021_133221'
P=R/'.local_restricted/retencion_intermedia/20261021_144031'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
qa=json.loads((O/'QA_ENTREGA.json').read_text());sens=json.loads((O/'QA_SENSIBILIDAD.json').read_text())
assert qa['dictamen']=='OK_CON_PENDIENTES_E' and sens['status']=='OK'
assert qa['formula_errors']==0 and qa['missing_caches']==0
agg=Path(qa['aggregate_path']);private=Path(qa['private_path']);desktop=Path(qa['desktop_path'])
assert sha(agg)==sha(desktop)==qa['aggregate_sha256']
assert sha(private)==qa['private_sha256']
now=datetime.datetime.now().astimezone().isoformat()
for root,dirs,files in os.walk(P,followlinks=False):
 os.chmod(root,0o700)
 for name in files:
  path=Path(root)/name
  if not path.is_symlink():os.chmod(path,0o600)
new=json.loads((O/'VERIFICACION_AGREGADA.json').read_text())
pending=[
 'E: falta correspondencia institucional explícita CODCLI para dos personas: Ingeniería en Informática y Técnico en Programación y Análisis de Sistemas. Mantienen documento de origen y denominador.',
 'E: acreditar universo completo, filtros del extractor y fecha efectiva del estado para 2025-T2, 2025-T3, 2026-T2 y 2026-T3. El listado 2026-T2 no informa ESTADOACADEMICO.',
 'D/E: aprobar regla intermedia propia para término de estudios/titulación, con programa seguido y fecha acreditada. No se cambia motor ni denominadores.',
 'E: distinguir fecha de matrícula, fecha nominal de extracción y fecha efectiva de estado. La primera observación en un respaldo no acredita un cierre pasado.',
 'C/E: recálculo local con Artifact Tool, sin certificación en Microsoft Excel nativo. El antecedente de suite general sigue limitado por unidecode; no se presenta como suite integral aprobada.'
]
report=f'''Fase 4/4 · Hito 3/3 — entrega local con pendientes E

# Retención intermedia IPSS 162

Fecha/hora de cierre documental: {now}.

B/C: se verificó y reutilizó el cierre local de las 13:32, que ya tenía manifiesto, bitácora, prompt y QA. No se ejecutó finalize.py porque habría sobrescrito ese cierre. Los tres temporales indicados existen, pero la evidencia persistente es la autoridad de reanudación. La ampliación de esta entrega es el Excel privado completo, separado del agregado.

## Archivos

- B: agregado conservado: `{agg}`.
- B: copia idéntica de Escritorio: `{desktop}`.
- B: SHA-256 agregado y Escritorio: `{qa['aggregate_sha256']}`.
- B/C: detalle privado: `{private}`.
- B: SHA-256 detalle privado: `{qa['private_sha256']}`.
- C: el detalle está en `.local_restricted`, excluido por `.gitignore:76` antes de escribir. Directorios 0700 y archivos 0600. No se copió al Escritorio ni se envió a servicios externos.

## Cuatro cierres

| Cohorte D | Cierre | Denominador C/D | Presencias B/C | VIGENTE observado B/C | Filas coincidentes B/C | Tasa E |
|---|---|---:|---:|---|---:|---|
| 2024 | 2025-T2 | 558 | 1 | 1 | 1 | Pendiente |
| 2024 | 2025-T3 | 558 | 325 | 317 | 328 | Pendiente |
| 2025 | 2026-T2 | 1.150 | 2 | Sin campo | 2 | Pendiente |
| 2025 | 2026-T3 | 1.150 | 0 en listado parcial | 0 en listado parcial | 0 | Pendiente |

E: las presencias no son tasas ni prueban deserción cuando no hay match. Faltan cobertura, fecha efectiva del estado y regla intermedia. B/C: 325 personas explican 328 filas por matrículas múltiples; se conservan las filas, se cuenta una vez a cada persona.

## Veinte personas y grupo de catorce

B/C: 20 = 18 con CODCLI + 2 pendientes. Hay 19 CODCLI: 17 personas con uno y una con dos. El detalle conserva originales como texto, incluidos documentos P, DV vacíos y correspondencia explícita de IPSS_Procesamiento / 2025_carga, J=RUT, BU=N_DOC, BV=DV. Las dos personas sin CODCLI conservan sus identificadores originales. No se infiere un RUN oficial desde el puente observado (E).

B/C: se releyeron 64 fuentes adicionales por hash: 60 comparables por RUT/CODCLI y cuatro sin esa pareja; cero correspondencias nuevas. Se conservan los 58 respaldos nominales de Base Maestra. B/C: los tres respaldos principales tienen 15 matrículas de 14 personas; 13 con alguna VIGENTE en 10246 y 14 en 11998/12112. E: ninguna fotografía certifica el estado en el cierre.

C: el libro privado contiene siete hojas: Resumen_privado, Cohortes_MU (1.708 personas), Identidad_20 (20 personas), Cierres_observados (331 filas coincidentes), Matriculas_20 (1.213 observaciones de las personas objetivo, entre archivos/hojas; no 1.213 personas), MU_anual_20 (20 filas anuales encontradas) y Fuentes (75 registros archivo/hoja). Se conservaron todas las matrículas observadas, no una matrícula escogida por persona. Las fórmulas cuentan personas desde la cohorte y filas desde las observaciones. Cada cruce conserva fuente, hoja, fila y método.

B/C: el cierre anterior verificó 1.130 personas por documento + 18 por puente = 1.148 localizadas en los respaldos; se cita como control previo, no se usa como numerador de un cierre. D: ninguna de las 20 se añade de nuevo a 1.150.

## Reglas auditadas y propuesta sin ejecutar

A: la definición SIES anual sigue el correo congelado del 09-sep-2026, misma institución y cohorte de origen, duración mínima regular 4/6/8, exclusión de especiales y ciertas inconsistencias, publicación desde 10 casos y referencia 30-abril. No se extiende automáticamente a un indicador intermedio interno.

C: `procesos/caracterizacion/caracterizacion_retencion.py`, líneas 18–20 y 169–245, SHA-256 `29dae4561a9969c6c87cd14350ed79a2f2aa78a0f82a72491cb7d6a130a9ee79`: el componente opcional excluye TITULADO en base; reconoce VIGENTE/SUSPENDIDO en destino. TITULADO/EGRESADO en destino puede quedar NO_RETENIDO, sin evaluar fecha del título. Se auditó implementación; no se modificó ni activó una regla distinta.

D/E: la propuesta solicitada distingue titulación acreditada del programa seguido de falta de rematrícula cuando se debía continuar. Requiere decisión aprobada y fecha/programa del título. Se mantienen separados duración formal, nivel esperado, nivel observado, avance curricular, egreso, título intermedio, título del programa y matrícula en otra carrera. No se infiere título por duración cumplida. Conservar cohorte original y calcular otra población elegible serían decisiones distintas.

D/C: seguimiento anual separado intacto: 74/222 = 33,33% y 48/124 = 38,71%. No son las cuatro tasas intermedias. Escenario_80, colores, tablas, filtros y fórmulas del agregado quedan idénticos por conservación byte a byte.

## QA

C: {qa['controls_passed']} controles independientes aprobados; {qa['new_private_formulas_with_cache']} fórmulas nuevas con caché, cero errores de fórmula y cero cachés faltantes. ZIP íntegro, siete hojas, seis tablas con filtros, identificadores almacenados como texto, entradas contrastadas celda a celda contra la extracción privada, conteos conciliados, 75 fuentes con hashes intactos, Git sin cambios adicionales atribuibles a esta tarea. Las siete hojas se revisaron visualmente con identificadores enmascarados solo en las vistas; el archivo final conserva los identificadores reales.

C: prueba de sensibilidad sobre una persona identificada y un estado de cierre: los conteos responden, el denominador permanece y la tasa sigue pendiente; restauración comprobada, sin reexportar datos de prueba. El QA inicial detectó filtros desactivados en el exportador y se corrigió antes de esta validación. No se considera aprobada esa primera prueba fallida. También se corrigió la vista de control para que el enmascaramiento no alterara los conteos mostrados.

C/E: Artifact Tool local; no se certifica apertura/reparación ni cálculo nativo en Microsoft Excel. La suite general anterior estaba limitada por unidecode ausente; estas pruebas no la sustituyen ni declaran aprobada toda la suite.

## Pendientes exactos

'''+ '\n'.join('- '+x for x in pending)+f'''

## Git y preservación

B: avance_curricular, `feature/ire-2026`, HEAD antes/después `80ca13a5a249a1a2bd53a699f5f73689b1f53040`. CARACTERIZACIÓN, `main`, HEAD antes/después `aba337784ccde0537fc21b2977b351170ed335e8`. Se verificaron remotos y estado pendiente. Los cambios previos ajenos se preservaron, sin stage, commit, push, merge, PR ni cambio de rama.

D: fuentes originales, bases, motor anual y denominadores 558/1.150/222/124 preservados. Cierre técnico/documental de esta ampliación completado; las tasas y dos llaves siguen abiertas como E.
'''
(O/'ENTREGA_Y_PENDIENTES.md').write_text(report)
steps=[
 (1,1,'B/C verificado','Git, remotos, contratos, manifiestos y hashes; carpeta privada ignorada antes de escribir.','QA_ENTREGA.json; soporte/git_*_antes.txt','Ninguno técnico de acceso.'),
 (1,2,'B/C auditado; D/E propuesta pendiente','Fuente A SIES y código longitudinal leído. TITULADO destino no evalúa fecha.','ENTREGA_Y_PENDIENTES.md; REVISION_REGLAS.json del cierre previo','Aprobar tratamiento intermedio con fechas y programa del título.'),
 (1,3,'B/C matriz completada; tasas E','Presencias 1/325/2/0, fechas/cobertura insuficientes.','VERIFICACION_AGREGADA.json; Resumen_privado!A6:I10','Cuatro cierres sin acreditación.'),
 (2,1,'B/C conciliado','14 personas, 15 matrículas por respaldo. No se escoge una sola matrícula.','Matriculas_20; Identidad_20','Ninguno de conteo.'),
 (2,2,'B/C observado; temporalidad E','13/14 con alguna VIGENTE en 10246; 14/14 en 11998 y 12112.','Resumen_privado!A17:I20; Matriculas_20','Fecha efectiva del estado y alcance histórico.'),
 (2,3,'B/C documentado; tasa E','Estados no extrapolados al pasado ni convertidos en VIG SIES.','ENTREGA_Y_PENDIENTES.md','No se acredita retención intermedia.'),
 (3,1,'B/C verificado','64 fuentes adicionales revalidadas por hash y llave exacta; cuatro no comparables.','VERIFICACION_AGREGADA.json; Fuentes','No se usan cruces aproximados.'),
 (3,2,'E no resolución documentada','Dos personas conservan documento de origen y CODCLI pendiente.','Identidad_20; informe agregado','Correspondencias institucionales explícitas de Informática y Programación.'),
 (3,3,'C/D conciliado','20=18+2; 19 CODCLI; ninguna persona se suma al denominador.','Resumen_privado!A14:I15; QA_ENTREGA.json','Tasas pendientes.'),
 (4,1,'B/C entregado','Agregado verificado y conservado; privado nuevo completo con siete hojas y filtros.','Rutas y hashes en MANIFEST_AMPLIACION_PRIVADA.json','Datos privados excluidos de Git, solo locales.'),
 (4,2,'C QA aprobado con E','Recálculo, pruebas de sensibilidad, entradas exactas, ZIP, privacidad y vista de siete hojas.','QA_ENTREGA.json; QA_SENSIBILIDAD.json','No certificación Excel nativo ni suite integral de reglas.'),
 (4,3,'B/C cierre persistente completado','Manifiesto, bitácora, informe y prompt nuevos; copia agregada de Escritorio idéntica.','Esta carpeta; manifiesto de ampliación','Pendientes sustantivos E conservados.')
]
log=['# Bitácora de ampliación privada','',f'Anotación de cierre: {now}.','', 'B/C: las evidencias anteriores se reutilizan por hash; las nuevas verificaciones corresponden a esta ejecución. Los hitos de evidencia concluida no significan tasas aprobadas.','']
for phase,hito,status,evidence,file,pend in steps:
 log += [f'## Fase {phase}/4 · Hito {hito}/3',f'- Estado: {status}.',f'- Fuente/acción/resultado: {evidence}',f'- Archivo: {file}',f'- Pendiente: {pend}','']
(O/'BITACORA_HITOS.md').write_text('\n'.join(log)+'\n')
prompt=f'''# Reanudación: retención intermedia IPSS 162

Estado verificado el {now}. H001-RETENCION-IPSS162 anual permanece cerrado; esta ampliación intermedia conserva pendientes E.

## Qué ya existe y no se debe duplicar

- Repositorio principal: {R}, feature/ire-2026, HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040. Referencia CARACTERIZACIÓN, main, HEAD aba337784ccde0537fc21b2977b351170ed335e8. Revalidar Git, remotos y cambios pendientes antes de trabajar; no cambiar rama, stage, commit, push, merge ni PR sin nueva autorización.
- Agregado: {agg}. SHA-256 {qa['aggregate_sha256']}. Escritorio: {desktop}, idéntico. Se conserva byte a byte, incluidos fórmulas, formato y Escenario_80.
- Detalle individual privado: {private}. SHA-256 {qa['private_sha256']}. Solo local y excluido de Git por **/.local_restricted/. Verificar exclusión antes de cualquier escritura. No subir a servicios externos, GitHub, Library ni adjuntar sus identificadores a informes públicos. Permisos de carpeta 0700, archivos 0600.
- Cierre nuevo persistente: {O}. Leer MANIFEST_AMPLIACION_PRIVADA.json, ENTREGA_Y_PENDIENTES.md, BITACORA_HITOS.md, QA_ENTREGA.json y QA_SENSIBILIDAD.json. El prompt histórico se conserva en {OLD/'PROMPT_ACTUALIZADO_RETENCION.md'}; la autorización posterior amplió la entrega a dos libros separados. No volver a ejecutar el finalize.py anterior.
- QA local nuevo aprobado con pendientes E: {qa['controls_passed']} controles independientes, {qa['new_private_formulas_with_cache']} fórmulas con caché, 0 errores y 0 cachés faltantes. Pruebas de sensibilidad reales sobre archivo guardado aprobadas. Artifact Tool, no Excel nativo. No afirmar suite integral aprobada: antecedente limitado por unidecode.

## Resultados fijos y grano

- Denominadores D: 2024=558; 2025=1.150. Ejercicios anuales separados T2=222 y T3=124. No cambiarlos.
- Cierres B/C: 2024/2025-T2: 1 persona, 1 VIGENTE; 2024/2025-T3: 325 personas, 328 matrículas, 317 personas con alguna VIGENTE. 2025/2026-T2: 2 personas, sin campo de estado. 2025/2026-T3: 0 presencias en listado parcial, no 0 retenidos. Las cuatro tasas son Pendiente E.
- 20 personas P ya incluidas en 1.150: 18 identificadas, 19 CODCLI, dos pendientes. Una persona tiene dos CODCLI. Una correspondencia cambia de documento entre fuentes y se sigue por CODCLI exacto. No sumar personas otra vez. No inferir equivalencias desde cuerpo RUT, nombre, sexo ni nacimiento.
- 14 personas de seguimiento: 15 matrículas en cada respaldo 10246/11998/12112; 13 con alguna VIGENTE en 10246, 14 en los otros dos. No se extrapola al cierre ni se atribuye fecha efectiva del estado.
- 64 fuentes adicionales verificadas: 60 con RUT/CODCLI, cuatro sin pareja; no se recuperan nuevas correspondencias para dos personas. Los 58 cortes nominales Base Maestra están en el detalle, no certifican cierres. No repetir búsqueda amplia de archivos ya inventariados sin fuente nueva.
- Seguimiento anual separado C/D: 74/222=33,33%; 48/124=38,71%. No presentarlo como retención intermedia.

## Cómo revisar el privado

Resumen_privado contiene controles calculados. Cohortes_MU conserva 1.708 personas y sus documentos originales como texto. Identidad_20 tiene puente explícito J/BU/BV de 2025_carga, CODCLI y pendientes. Cierres_observados conserva 331 filas coincidentes de los cuatro listados. Matriculas_20 conserva 1.213 observaciones por fuente/hoja/fila; filtrar Grupo 14=1 para seguimiento. MU_anual_20 conserva 20 filas anuales observadas, sin trasladarlas a cierre intermedio. Fuentes trae 75 entradas archivo/hoja con ruta y SHA-256. Conservar todas las matrículas y contar una persona una vez por cohorte/cierre.

## Regla encontrada y decisión aún no implementada

A: correo SIES 09-sep-2026 congelado, regla anual. C: el componente longitudinal opcional excluye TITULADO base pero clasifica destino TITULADO/EGRESADO como NO_RETENIDO sin evaluar fecha de título. Código y hash en el informe. No modificar el motor anual ni trasladar automáticamente esa regla a la retención intermedia.

D/E: el usuario quiere distinguir titulación acreditada del programa seguido de quien debía rematricularse y no lo hizo. Faltan definición interna aprobada, programa y fecha de título. Separar duración formal, nivel teórico, NIVEL observado, avance, egreso, título intermedio, título del programa y matrícula en otra carrera. No inferir título por cumplir duración. Conservar cohorte y proponer otra población elegible son decisiones distintas.

## Trabajo restante, solo con evidencia nueva

1. Acreditar población, filtros, fecha efectiva de estado y cobertura de los cuatro cierres. Las fotografías actuales no sustituyen históricos fechados. Antes de pedir fuentes, consultar el inventario de esta entrega.
2. Obtener correspondencia institucional explícita de los dos CODCLI pendientes (Informática y Programación). Conservar sus documentos originales en el privado, nunca en Git ni en resumen público.
3. Resolver tratamiento interno de egreso/titulación y fecha de matrícula/renovación con decisión registrada. No crear tasas ni categorías sin sustento.
4. Si se autorizan cambios, crear derivados nuevos, preservar originales y formatos, recalcular, contrastar datos/fórmulas, verificar privacidad e ignorado Git, generar manifiesto/bitácora/hashes y copia del agregado en Escritorio. No copiar el privado al Escritorio ni al remoto.

Cada actualización al usuario empieza Fase X/4 · Hito Y/3. Registrar fuente, acción, resultado, archivo y pendiente. A oficial, B observado, C cálculo/implementación, D decisión, E pendiente. No dar por cerrada una tasa pendiente ni interpretar ausencia como deserción.
'''
(O/'PROMPT_ACTUALIZADO_RETENCION.md').write_text(prompt)
for p in [O/'QA_ENTREGA.json',O/'QA_SENSIBILIDAD.json',O/'VERIFICACION_AGREGADA.json']:
 assert p.exists()
evidence=[{'ruta':str(p),'sha256':sha(p),'rol':'Evidencia agregada / implementación C, sin identificadores'} for p in sorted(O.rglob('*')) if p.is_file() and p.name!='MANIFEST_AMPLIACION_PRIVADA.json']
manifest={'hito':'H001-RETENCION-IPSS162','fase_hito':'Fase 4/4 · Hito 3/3','fecha':now,'dictamen':'OK_CON_PENDIENTES_E','alcance':'Ampliación local autorizada: entrega agregada preservada y detalle privado separado; no modifica motor ni fuentes.','autor_tecnico':'Codex, por solicitud de Alexi en esta conversación','decision_D':'Ampliar a Excel privado con identificadores disponibles y todas las matrículas observadas de los objetivos. Nunca publicar individuos ni usar cruces aproximados.','agregado':{'ruta':str(agg),'sha256':sha(agg),'copia_escritorio':str(desktop),'copia_identica':True,'reutilizado_sin_cambios':True},'detalle_privado':{'ruta':str(private),'sha256':sha(private),'clasificacion':'B/C; contiene datos individuales sensibles, no Git ni servicios externos','git_ignorado_verificado_antes_y_despues':True,'regla_ignore':'.gitignore:76 **/.local_restricted/','permisos_directorio':'0700','permisos_archivo':'0600','hojas':7,'personas_cohortes':1708,'personas_objetivo':20,'observaciones_matricula_objetivos':1213,'no_incluye_nombres_nacimientos_sexo':True},'denominadores_D':[558,1150,222,124],'cierres_B_C':new['closures'],'tasas_E':['Pendiente']*4,'identidad20_B_C':new['identity20'],'seguimiento14_B_C':new['focus'],'fuentes_B_C':new['sources'],'fuentes_verificadas':75,'regla_longitudinal_verificada':{'ruta':str(R/'procesos/caracterizacion/caracterizacion_retencion.py'),'sha256':sha(R/'procesos/caracterizacion/caracterizacion_retencion.py'),'clasificacion':'C; no A','aplicacion_modificada':False},'qa_C':{'controles':qa['controls_passed'],'formulas_privadas_con_cache':qa['new_private_formulas_with_cache'],'errores':0,'caches_faltantes':0,'sensibilidad':sens,'motor':'Artifact Tool local','native_excel':False,'visual':'Siete hojas revisadas con máscaras temporales en vistas; final real exportado antes de enmascarar.','aggregate_prior_QA':{'ruta':str(OLD/'QA_INDEPENDIENTE.json'),'sha256':sha(OLD/'QA_INDEPENDIENTE.json'),'112_formulas_50_controles':'Antecedente del agregado idéntico, no sustituye QA privado nuevo.'}},'git_B':qa['git'],'sin_stage_commit_push_merge_PR':True,'originales_motor_denominadores_preservados':True,'pendientes_E':pending,'evidencias':evidence,'cierre_anterior':{'ruta':str(OLD/'MANIFEST_REVISION.json'),'sha256':sha(OLD/'MANIFEST_REVISION.json'),'conservado':True},'limite_privacidad':'El manifiesto público solo contiene rutas, hashes y agregados. El payload individual y Excel no se adjuntan, no se suben, no se copian a Library ni se proponen para Git.'}
(O/'MANIFEST_AMPLIACION_PRIVADA.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'report':str(O/'ENTREGA_Y_PENDIENTES.md'),'manifest':str(O/'MANIFEST_AMPLIACION_PRIVADA.json'),'manifest_sha256':sha(O/'MANIFEST_AMPLIACION_PRIVADA.json'),'private_sha256':sha(private),'aggregate_sha256':sha(agg),'no_commit_push':True},ensure_ascii=False,indent=2))

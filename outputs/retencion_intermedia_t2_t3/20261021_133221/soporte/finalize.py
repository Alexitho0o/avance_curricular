"""Assemble aggregate evidence, milestone log and delivery manifest."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
T=Path('/tmp/retencion_revision_20261021');R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
c=json.loads((T/'config.json').read_text());book=Path(c['output']);out=book.parent;desktop=Path('/Users/alexi/Desktop')/book.name
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.datetime.now().astimezone().isoformat()
assert book.exists() and desktop.exists() and sha(book)==sha(desktop)
files={'/tmp/retencion_counts.json':'CONTEOS_REPRODUCIDOS.json','/tmp/retencion_coverage.json':'REVISION_COBERTURA.json','/tmp/retencion_identities.json':'REVISION_LLAVES.json','/tmp/retencion_rules.json':'REVISION_REGLAS.json','/tmp/PROMPT_ACTUALIZADO_RETENCION.md':'PROMPT_ACTUALIZADO_RETENCION.md','/tmp/retencion_final_qa.json':'QA_INDEPENDIENTE.json',str(T/'qa_package.json'):'QA_PAQUETE.json'}
for src,dest in files.items():shutil.copy2(src,out/dest)
prompt_path=out/'PROMPT_ACTUALIZADO_RETENCION.md'
prompt_path.write_text(prompt_path.read_text()+'''

## Addenda de reanudación: cierre exclusivamente local

Fase 4/4 · Hito 3/3. Inspeccionar finalize.py y las salidas existentes antes de ejecutar para evitar duplicados. Completar localmente manifiesto, bitácora, informe y esta copia del prompt en 20261021_133221. Comprobar Git final y los hashes del libro y su copia de Escritorio. No subir ni transferir archivos a Library ni a otros servicios externos. Conservar tasas pendientes, ausencia de validación Excel nativo y limitación de suite completa por unidecode. No repetir el análisis validado salvo verificaciones necesarias; no modificar fuentes, motor anual, rama ni realizar commit, push, merge o PR. Entregar los siete puntos con rutas locales verificadas y pendientes sustantivos explícitos.
''')
reports={name:json.loads((out/name).read_text()) for name in ['CONTEOS_REPRODUCIDOS.json','REVISION_COBERTURA.json','REVISION_LLAVES.json','REVISION_REGLAS.json']}
source_pairs={}
def walk(value):
    if isinstance(value,dict):
        path=next((value[k] for k in ['ruta','path','source'] if isinstance(value.get(k),str) and value[k].startswith('/')),None)
        h=next((value[k] for k in ['sha256','sha256_before','hash'] if isinstance(value.get(k),str) and len(value[k])==64),None)
        if path and h:
            if path in source_pairs:assert source_pairs[path]==h,('source_hash_conflict',path)
            source_pairs[path]=h
        for x in value.values():walk(x)
    elif isinstance(value,list):
        for x in value:walk(x)
for j in reports.values():walk(j)
source_pairs[c['base']]='12bf04615558554a30275b4ee8c6197617e7195c059c4c87277a91c4697e719d'
verified=[]
for p,h in sorted(source_pairs.items()):
    actual=sha(p);assert actual==h,('source_modified',p)
    verified.append({'ruta':p,'sha256':actual,'intacto':True})
support=out/'soporte';support.mkdir(exist_ok=True)
for name in ['build.mjs','preserve.py','config.json','verify_final.mjs','finalize.py','formula_scan.ndjson','inspect.ndjson','git_before.txt']:
    shutil.copy2(T/name,support/name)
for src,name in [('/tmp/retencion_counts_reproduce.py','reproducir_conteos.py'),('/tmp/retencion_rules_probe.py','probar_reglas.py')]:
    if Path(src).exists():shutil.copy2(src,support/name)
for name in ['final_resumen.png','final_cierres.png','final_seguimiento.png','llaves.png','reglas.png','bases.png','carreras.png','fuentes.png']:
    shutil.copy2(T/name,support/name)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()
assert head=='80ca13a5a249a1a2bd53a699f5f73689b1f53040' and branch=='feature/ire-2026'
steps=[
 (1,1,'Completado','Acceso real; rama, HEAD, remotos y estado Git; agent.md, PROYECTO_IPSS.json, contrato de integración y AGENTS del módulo leídos. .agents/skills no existe.','soporte/git_before.txt; MANIFEST_REVISION.json','Ninguno de acceso. No se comprobó conectividad remota GitHub porque no se publica.'),
 (1,2,'Auditoría completada; decisiones E pendientes','11 hallazgos A–E y auditoría de duración; excepción parcial TITULADO base; titulación destino sin fecha. Una prueba existente y cinco casos sintéticos.','REVISION_REGLAS.json','Definir contrato interno de culminación entre cierres y efecto en denominador. Suite completa: falta unidecode.'),
 (1,3,'Matriz completada; acreditación de cierre pendiente E','Seis fuentes con hashes; 17 evidencias; hojas ocultas, filtros y dos estados discrepantes Base/2026_3.','REVISION_COBERTURA.json','Fecha efectiva, universo completo, estado histórico y regla de los cuatro cierres.'),
 (2,1,'Completado','14 personas y 15 matrículas por respaldo; sin duplicados de llave completa en el grupo.','REVISION_LLAVES.json: seguimiento_14','Ninguno del conteo de matrículas observadas.'),
 (2,2,'Comparación completada; acreditación temporal pendiente E','14 llaves comunes julio→octubre; 15 octubre→octubre; 58 cortes nominales revisados.','REVISION_LLAVES.json: comparaciones_llave_matricula; seguimiento_master_nominal','No hay fecha efectiva del estado al cierre; la matrícula restante cambia año/período.'),
 (2,3,'Conclusión agregada completada','13 de 14 con alguna VIGENTE en 10246; 14 en 11998/12112. No se extrapoló estado ni se asignó VIG SIES.','Revision_agregada!A29:I37','No se acredita nueva retención intermedia.'),
 (3,1,'Completado','64 fuentes adicionales únicas: 60 comparables y 4 sin esquema CODCLI/RUT; 86 copias idénticas no releídas.','REVISION_LLAVES.json: busqueda_dos_pendientes','Ninguno de acceso a las fuentes revisadas.'),
 (3,2,'No resolución documentada E','Cero CODCLI adicionales; dos casos de Informática y Programación siguen sin puente institucional explícito.','REVISION_LLAVES.json: busqueda_dos_pendientes','Faltan las dos correspondencias exactas. No se inventan ni se retiran del denominador.'),
 (3,3,'Completado','20=18+2; 19 CODCLI; intersección P/R cero; 1.130+18=1.148 presencias en respaldos, sin doble conteo.','REVISION_LLAVES.json: conciliacion_20; control_colisiones_conjunto_P_R','Continuidad al cierre permanece E.'),
 (4,1,'Completado','Excel nuevo con seis hojas; edición autorizada y hoja agregada; fórmulas y formato conservados.','Libro nuevo; soporte/build.mjs; QA_PAQUETE.json','Tasas intermedias permanecen Pendiente por evidencia.'),
 (4,2,'Completado con límites declarados','Artifact Tool recalculó; sensibilidad de prerrequisitos y selector; importación final; revisión visual; QA independiente; estilos/tablas/filtros/validaciones preservados; Escenario_80 byte idéntico.','QA_PAQUETE.json; QA_INDEPENDIENTE.json; soporte/*.png','No se abrió Microsoft Excel. Formato regional del visor no se certifica. Suite completa de reglas bloqueada por unidecode.'),
 (4,3,'Completado; pendientes sustantivos documentados','Libro, copia Escritorio y SHA-256 idénticos; manifiesto, prompt actualizado y siete puntos de entrega.','MANIFEST_REVISION.json; PROMPT_ACTUALIZADO_RETENCION.md; REVISION_COMPLETA.md','Dos llaves y cuatro cierres pendientes E; sin tasa inventada.')
]
log=['Fase 4/4 · Hito 3/3','', '# Bitácora de hitos', '',f'Fecha/hora real de esta anotación: {now}.','', 'El esquema 4×3 se incorporó durante la ejecución. Las evidencias previas se vinculan ahora a sus hitos; no se atribuyen fechas ni registros contemporáneos inexistentes. El último estado comunicado de Fase 1, Hito 2, avanzó a auditoría completada con decisiones E pendientes. El trabajo independiente continuó hasta entregar el Excel.','', 'La desconexión inicial impidió la primera ejecución. Tras recuperarse el transporte se revalidó Git y se completaron las lecturas. Una segunda desconexión interrumpió el cierre documental después de crear y verificar ambas copias del Excel. En esta reanudación se inspeccionó finalize.py y se confirmó que la carpeta final solo contenía el libro, sin manifiesto ni documentación duplicada; Git y los hashes se volvieron a comprobar. La copia 12112 del Escritorio ya no existía: se recuperó una copia idéntica en OneDrive. No hubo denegaciones de aprobación.','']
for phase,step,status,evidence,output,pending in steps:
    log.extend([f'## Fase {phase}/4 · Hito {step}/3',f'- Estado: {status}.',f'- Evidencia: {evidence}',f'- Salida: {output}',f'- Pendientes: {pending}',''])
(out/'BITACORA_HITOS.md').write_text('\n'.join(log))
bookhash=sha(book)
report=f'''Fase 4/4 · Hito 3/3

# Entrega de revisión de retención intermedia IPSS 162

Dictamen: **QA técnico aprobado con pendientes E**. Los cuatro cierres siguen sin tasa acreditada. Fecha de entrega: {now}.

## 1. Excel y copia idéntica

- Libro: `{book}`
- Escritorio: `{desktop}`
- SHA-256 de ambas copias: `{bookhash}`.

## 2. Cuatro cierres

| Cohorte | Cierre | Denominador fijo | Presencias en listado B/C | VIGENTE observado B | Vigentes acreditados al cierre | Tasa | Fuente/hoja |
|---|---|---:|---:|---|---|---|---|
| 2024 | 2025-T2 | 558 | 1 | 1 | Pendiente E | Pendiente E | Matrícula T2_2025 2.xlsx / T2_2025 |
| 2024 | 2025-T3 | 558 | 325 | 317 | Pendiente E | Pendiente E | Matrícula T3_2025 2.xlsx / T3_2025 |
| 2025 | 2026-T2 | 1.150 | 2 | Sin campo | Pendiente E | Pendiente E | Matrícula T_2_13_07_2026.xlsx / Hoja1 |
| 2025 | 2026-T3 | 1.150 | 0 | 0 en listado | Pendiente E | Pendiente E | Matrícula_T3_02_10_2026.xlsx / Base |

325 personas tienen 328 matrículas en T3-2025; se conservaron todas. Los respaldos 10246/11998 contienen 1.148 personas de la cohorte 2025, verificadas sin doble conteo. Ese dato describe fotografías de varios años/períodos; no reemplaza las presencias de los listados ni acredita retención al cierre.

## 3. Veinte personas y seguimiento de catorce

18 identificadas, 2 pendientes; 19 CODCLI (17 personas con uno y una con dos). Todas ya integraban 1.150. Una persona se recupera por CODCLI pese al cambio documental. Las 18 no figuran en los dos listados parciales 2026. No se acreditó deserción.

Entre las mismas 14 personas, 10246 tiene 13 con alguna VIGENTE; 11998 y 12112 tienen 14. Cada fuente conserva 15 matrículas sin colisiones de llave completa en ese grupo. Julio→octubre mantiene 14 llaves: 13 VIGENTE y una ELIMINADO; la otra persona pasa de una llave 2025-P1 a otra 2026-P3, sin inferir una transición de la misma matrícula.

La búsqueda revisó 64 fuentes adicionales por hash: 58 Base Maestra, 12135, 11248 y cuatro históricos sin esquema comparable. No recuperó los dos CODCLI pendientes (Informática y Programación). Los 58 respaldos muestran 13 de las 14 con alguna VIGENTE hasta el nominal 08-09 y 14 desde 09-09, incluido 02-10. Son fechas nominales, no fechas efectivas del evento o cierre.

12112 fue relocalizado en OneDrive/0_caracterizacion/2026-10-20/2027_P1_082351/01_ENTRADAS; su hash coincide con el gobernado. La antigua ruta del Escritorio ya no está disponible.

## 4. Cambios y distinción conceptual

Se actualizaron las llaves pendientes de 20 a 2 y los conteos derivados de no localizados con llave (1.146 en T2-2026 y 1.148 en T3-2026). Presencias, estados observados y denominadores no cambian. Se añadió Revision_agregada, se precisaron pendientes/fuentes y se conservaron formatos, tablas, filtros, fórmulas, validaciones y el escenario hipotético de 80 casos separado.

La retención interna documentada considera matrícula IPSS t+1 aunque cambie carrera. SIES conserva su propia cohorte, reglas y referencia anual. La auditoría halló una excepción parcial en Caracterización: TITULADO en base se excluye del seguimiento opcional; VIGENTE en base y TITULADO/EGRESADO en destino produce NO_RETENIDO sin fecha de título. Ese resultado técnico no acredita deserción. El componente no se aplica a estos denominadores.

Duración formal de oferta/plan, nivel curricular, avance real, egreso y título son conceptos distintos. No se infirió titulación por duración cumplida. La propuesta E separa culminación acreditada de continuidad/deserción; su efecto en el denominador requiere contrato, fechas y decisión explícita. No se creó una categoría “no recurrido”.

## 5. Pendientes exactos

- 2025-T2: matrícula completa de cohorte 2024 y renovaciones, fecha efectiva y estados del cierre; el listado solo contiene ingresos 2025-T2.
- 2025-T3: acreditación de exhaustividad y fecha efectiva de estados de T3_2025.
- 2026-T2: población completa de cohorte 2025, estados y fecha efectiva. Hoja1 carece de estado; congelamiento de 10246 no acredita corte.
- 2026-T3: cubrir períodos de ingreso 1 y 2, fijar hoja autorizada y fecha efectiva; resolver dos discrepancias Base/2026_3. 11998 no acredita cierre por su ejecución de octubre.
- Todos: regla intermedia propia con población, exclusiones y numerador; historial de matrícula/estado y titulación fechados. No homologar T1/T2/T3 a semestres SIES.
- Identidad: correspondencia institucional explícita para los dos CODCLI pendientes, sin cruce aproximado ni exclusión.
- Regla interna de titulación: definir antes/durante/después del corte, otra carrera, rematrícula, múltiples matrículas y egreso sin título. Decidir cohorte fija o población aún expuesta antes de cualquier tasa ajustada.

## 6. QA y Git

Recálculo con Artifact Tool, pruebas de sensibilidad (cierre sin numerador / numerador sin cierre / selector de carrera), controles independientes, revisión visual e importación del XLSX final. Cero errores de fórmula. Preservación de estilos efectivos, tablas, filtros, validaciones y hojas originales fuera de las celdas autorizadas. Escenario_80 byte idéntico. Solo agregados; sin nóminas, identificadores de alumnos, macros ni vínculos externos.

No se abrió Microsoft Excel: el comportamiento nativo y su configuración regional no se certifican. Las pruebas de reglas incluyeron una prueba existente aislada y cinco casos sintéticos; la suite completa no pudo importarse por unidecode ausente, sin cambiar el entorno.

Rama antes/después: `{branch}`. HEAD antes/después: `{head}`. Original Excel: SHA-256 `12bf04615558554a30275b4ee8c6197617e7195c059c4c87277a91c4697e719d`. Base anual: `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`. Los demás hashes y el control final de fuentes se registran en MANIFEST_REVISION.json.

## 7. Conservación

Fuentes y motor anual intactos. Denominadores 558, 1.150, 222 y 124 conservados. Seguimiento anual separado: 74/222 = 33,33% y 48/124 = 38,71%. Sin cambio de rama, commit, push, merge ni PR. Los cambios previos del checkout no fueron alterados. La entrega es local; no se declara publicada en GitHub.

La bitácora registra doce hitos y distingue revisión ejecutada de acreditación pendiente. PROMPT_ACTUALIZADO_RETENCION.md conserva el prompt original e incorpora las ampliaciones del usuario.
'''
(out/'REVISION_COMPLETA.md').write_text(report)
before=(T/'git_before.txt').read_text().splitlines()
after=subprocess.check_output(['git','status','--porcelain=v1','-uall'],cwd=R,text=True).splitlines()
prefix=out.relative_to(R).as_posix()+'/'
outside=[x for x in after if prefix not in x]
assert outside==before,('unexpected_git_status_changes',set(outside)^set(before))
manifest={
 'fase_hito':'Fase 4/4 · Hito 3/3','fecha':now,'dictamen':'QA_TECNICO_OK_CON_PENDIENTES_E','alcance':'Retención intermedia IPSS162; agregados; auditoría interna/SIES y titulación',
 'original':{'ruta':c['base'],'sha256':sha(c['base'])},'salida':{'ruta':str(book),'sha256':bookhash},'copia_escritorio':{'ruta':str(desktop),'sha256':sha(desktop),'identica':True},
 'hojas':['Resumen','Por_carrera','Fuentes_y_alcance','Bases_por_confirmar','Escenario_80','Revision_agregada'],
 'denominadores_fijos':[558,1150,222,124],'presencias_listados':[1,325,2,0],'vigentes_observados':[1,317,None,0],'vigentes_acreditados_cierre':['Pendiente']*4,'tasas_intermedias':['Pendiente']*4,
 'personas20':reports['REVISION_LLAVES.json']['conciliacion_20'],'separacion_reglas':reports['REVISION_REGLAS.json']['dictamen'],
 'metodo':{'cruces':'Llaves exactas, puente explícito N_DOC/RUT/CODCLI; sin nombres, sexo, nacimiento ni decodificación. Filas en memoria; se conservan todas las matrículas; personas únicas por universo fijado.','fechas':'Nombre, mtime, congelamiento y corrida no acreditan fecha efectiva. Estados posteriores no se extrapolan.','authoring':'Artifact Tool; transporte OOXML de celdas autorizadas y hoja nueva para preservar partes originales; openpyxl solo lectura para QA.','recalculo':'Artifact Tool, recalculate final; sensibilidad restaurada y reimportación sin reescritura.','datos_individuales_persistidos':False},
 'fuentes_revalidadas_final':verified,'fuentes_revalidadas_total':len(verified),
 'qa':{'paquete':'QA_PAQUETE.json','independiente':'QA_INDEPENDIENTE.json','visual':'Todas las vistas modificadas y hoja nueva revisadas; imágenes de soporte.','native_excel':'No ejecutado; comportamiento nativo/regional no certificado.','suite_reglas':'Prueba existente aislada OK y cinco sintéticos; suite completa bloqueada por falta de unidecode.','originales_intactos':True,'escenario80_byte_identico':True},
 'git':{'rama_antes':branch,'rama_despues':branch,'HEAD_antes':head,'HEAD_despues':head,'remotos':subprocess.check_output(['git','remote','-v'],cwd=R,text=True).splitlines(),'cambios_previos_conservados':True,'nuevos_cambios_solo_carpeta_salida':True,'status_before_sha256':sha(T/'git_before.txt'),'commit':False,'push':False,'merge':False,'PR':False,'publicado':False},
 'pendientes_E':c['pending'],
 'bloqueos':{'acceso':'Resueltas las interrupciones de transporte; reanudación local con script/salidas inspeccionados, Git y hashes comprobados. 12112 relocalizado por hash.','denegaciones':[],'documentales':['Cuatro cierres sin cobertura/fecha/estado/regla suficientes','Dos CODCLI sin correspondencia explícita','Decisión de denominador/titulación interna pendiente'],'validacion':['Aplicación Microsoft Excel no probada','Suite completa de reglas no importada por unidecode ausente']},
 'trazabilidad':'BITACORA_HITOS.md; PROMPT_ACTUALIZADO_RETENCION.md; REVISION_COMPLETA.md',
 'salidas':{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='MANIFEST_REVISION.json'}
}
(out/'MANIFEST_REVISION.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'output':str(book),'desktop':str(desktop),'manifest':str(out/'MANIFEST_REVISION.json'),'sha256':bookhash,'sources_revalidated':len(verified),'git_unchanged_except_output':True},ensure_ascii=False,indent=2))

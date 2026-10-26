"""Diagnóstico agregado de diferencias y documentación de puertas bloqueadas."""
import csv,json,hashlib,subprocess
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path.cwd();O=R/'data/reglas_negocio/20261022_puente_versiones/validacion_local_v1';B=O.parent
read=lambda n:list(csv.DictReader(open(O/n,encoding='utf-8-sig')))
def js(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def records(p):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=iter(w.active.values);h=next(it)
 for r in it:yield dict(zip(h,r))
 w.close()
def text(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def key(a,b):return text(a).replace('.','').replace(' ','').lstrip('0')+'-'+text(b).replace(' ','')
inv=json.load(open(O/'FASE0_FUENTES.json'));p=next(Path(r['ruta']) for r in inv if r['ruta'].endswith('PROMEDIOSDEALUMNOS_12166.xlsx'));m=next(Path(r['ruta']) for r in inv if 'BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA' in r['ruta'])
people=defaultdict(set)
for r in records(p):
 if r['CODCARR'] in ['IECIRE','IECIREOL']:people[r['CODCARR']].add(key(r['RUT'],r['DIG']))
bytype=defaultdict(set)
for r in records(m):
 if text(r['COD_SED'])=='2' and text(r['COD_CAR'])=='1' and text(r['JOR'])=='4' and text(r['VERSION'])=='2':bytype[text(r['TIPO_DOC'])].add(key(r['N_DOC'],r['DV']))
diag=[]
for c,ps in people.items():diag.append({'carrera':c,'match_R':len(ps&bytype['R']),'match_P':len(ps&bytype['P']),'match_sin_tipo':len(ps&(bytype['R']|bytype['P'])),'clasificacion':'C/E','interpretacion':'Incluir TIPO_DOC=P no reproduce el conteo anterior. Causa pendiente: revisar metodo previo y deduplicacion de personas; no alterar fuentes para forzar coincidencia.'})
js('DIAGNOSTICO_DIFERENCIAS_TIPO_DOC.json',diag)
# Comparar totales anteriores con los calculados; conservar las diferencias de definicion.
old=list(csv.DictReader(open(B/'TABLA_RESUMEN_TOTALES_BRECHAS_VERSIONES_20261022.csv',encoding='utf-8-sig')))
controls=read('FASE4_TOTALES_Y_BRECHAS.csv');titles=read('TITULADOS_OBSERVADOS.csv');lookup={(r['indicador'],r['grupo']):int(r['antes']) for r in controls};t={r['ano']:int(r['personas_tituladas_observadas']) for r in titles};compar=[]
for r in old:
 label=r['indicador'];y=label[-4:]
 actual=lookup.get(('anio',y)) if label.startswith('MU total') else lookup.get(('vig1',y)) if label.startswith('MU VIG') else t.get(y) if label.startswith('Titulados') else None
 if actual is not None:compar.append({'indicador':label,'anterior':float(r['valor']),'reproducido':actual,'brecha':actual-float(r['valor']),'clasificacion':'C'})
js('COMPARACION_RESUMEN_PREVIO.json',compar)
rows=read('TABLA_63_DIMENSIONES.csv');review=read('FASE2_REVISION_11.csv');nom=read('FASE3_DIAGNOSTICO_13.csv');qa=json.load(open(O/'FASE5_QA_INDEPENDIENTE.json'))
phase7='''# Preparación controlada — PENDIENTE_APROBACION_GOBERNANZA

D: Borrador autorizado por el usuario; no instalado ni publicado. Ningún cambio productivo.

| Componente | Cambio preparado | Puerta pendiente |
|---|---|---|
| Reglas de negocio | Exigir TIPO_DOC=R, RUT/DV exactos y contexto temporal explícito. Predominio >=90% y n>=3 es propuesta interna, nunca regla oficial SIES. | Tipo y duración UMAS acreditados; conciliación MU exacta; responsable y aprobación |
| SQL | Consulta de revisión SQL_BORRADOR.sql, sobre tablas agregadas; no actualiza tablas productivas. | Esquema real del consumidor y aprobación |
| Complementos | Contrato: consumir solo estado aprobado y hash fijo; devolver PENDIENTE sin código ante conflicto, falta de evidencia o contexto temporal ausente. | Identificar complementos consumidores y sus versiones; sin instalación automática |
| Skills | Texto propuesto: conservar fuentes, separar A/B/C/D/E, prohibir homologación por nombre, distinguir personas de matrículas y no sumar personas entre planes/años. | Revisión de responsables; no editar skills instaladas |
| Regresión | Dos implementaciones coinciden, hashes intactos, cero diferencia de totales MU; exigir no coincidencia R/P, no doble conteo de personas y ausencia de match distinta de cero/deserción. | Conciliación semántica de denominadores, retenidos y tasas |
| Diccionario | Usar TABLA_63_DIMENSIONES como auditoría, conservar estado previo y evidencia, sin promover. El definitivo requiere grano carrera/sede/jornada/plan/año acreditado. | Fases 1–5 con puertas satisfechas |
| Bitácora | Auditoría local 2026-10-22: 63 dimensiones, 141 pares dimensión/candidato, 0 asignaciones nuevas; 2 discrepancias de conteo cuya causa sigue pendiente. | Cierre de brechas y aprobación formal |

E: No existe diccionario definitivo. No se atribuye autoridad A a cálculos internos. VERSION y VIGENCIA se mantienen separadas.
'''
(O/'FASE7_CAMBIOS_PREPARADOS.md').write_text(phase7)
(O/'SQL_BORRADOR.sql').write_text('''-- D/E: PENDIENTE_APROBACION_GOBERNANZA. Solo revisión agregada.
-- Contrato lógico propuesto; adaptar nombres al consumidor antes de ejecutar.
-- No genera equivalencias ni cambia bases.
SELECT carrera_interna, sede, jornada, planes, codigo_predominante_observado,
       personas_coincidentes_unicas, proporcion_incidencias, estado, pendiente
FROM auditoria_puente_versiones
WHERE estado = 'PENDIENTE';
''')
phase=[('0','COMPLETA','Fuentes y derivados inventariados con SHA-256; cobertura y llaves documentadas.'),('1','EJECUTADA; PUERTA CON OBSERVACIONES','Cruce local exacto; 2 diferencias frente al derivado anterior con causa aún no acreditada.'),('2','EJECUTADA; 11 PENDIENTES','Ninguna supera simultáneamente las condiciones; faltan atributos UMAS acreditados.'),('3','EJECUTADA; 13 PENDIENTES','9 dimensiones con cobertura temporal fuera de MU; 4 sin evidencia suficiente.'),('4','PARCIAL; PROMOCIÓN DETENIDA','Cero diferencia MU y conservación de hashes. Retención conservada, pero conciliación semántica puente/denominadores/retenidos/tasas no acreditada.'),('5','QA COMPUTACIONAL PASS; GOBERNANZA BLOQUEADA','Segunda lectura y SQL coinciden en conteos, duplicados y agregados; no acredita equivalencias.'),('6','BLOQUEADA','No se genera diccionario definitivo porque faltan controles semánticos y acreditación de planes.'),('7','PREPARADA; NO APLICADA','Borradores de reglas, SQL, complementos, skills, regresión y bitácora.')]
report='# Auditoría del puente UMAS–SIES, 2026-10-22\n\n**NO CERRADO — PENDIENTE_APROBACION_GOBERNANZA.**\n\nC/E: Las 39 propuestas previas se conservan como antecedentes. No son 39 equivalencias aprobadas. Hay 11 pendientes múltiples/baja cobertura y 13 sin match en los candidatos, total 63. No se promovió ninguna dimensión.\n\n| Fase | Estado | Evidencia o pendiente |\n|---|---|---|\n'+'\n'.join('|'+ '|'.join(x)+'|' for x in phase)
report+='\n\n## Resultados de las 11 dimensiones (C/E)\n\n| Carrera | Jornada | Personas | Predominio | Resultado |\n|---|---:|---:|---:|---|\n'
for r in review:report+=f"|{r['carrera_interna']}|{r['jornada']}|{r['personas_coincidentes_unicas']}|{float(r['proporcion_incidencias'] or 0):.4%}|PENDIENTE|\n"
report+='\nLos porcentajes usan incidencias persona–código, con personas únicas y multicódigo separadas en el CSV. Cinco dimensiones tienen menos de tres personas y seis quedan bajo 90%. Tipo y duración de la malla UMAS no están acreditados por estas fuentes.\n\n## Diagnóstico de las 13 dimensiones (B/C/E)\n\n| Carrera | Jornada | Años PROMEDIOS | Causa |\n|---|---:|---|---|\n'
for r in nom:report+=f"|{r['carrera_interna']}|{r['jornada']}|{r['anios_PROMEDIOS']}|{r['causa']}|\n"
report+='\nLa cobertura se observa por carrera interna; PROMEDIOS no aporta sede. No se atribuye automáticamente a una jornada a partir de la identidad. Los códigos candidatos fijan sede, carrera, jornada y versión de cada dimensión. MU no informa plan. Los respaldos gobernados prueban actividad, no equivalencia acreditada. No hay diferencias de formato RUT/DV demostradas como causa de estas 13 dimensiones.\n\n## Controles (C)\n\n| Año | Total MU | VIG=1 | Diferencia antes/después |\n|---|---:|---:|---:|\n'
for y in ['2022','2023','2024','2025','2026']:report+=f"|{y}|{lookup[('anio',y)]}|{lookup[('vig1',y)]}|0|\n"
report+='\nTambién se controlaron código único, carrera, sede y jornada en FASE4_TOTALES_Y_BRECHAS.csv. VIG=1 y total MU son universos distintos: su diferencia no es un error de conservación.\n\nEl cruce temporal tiene 8.469 incidencias persona/carrera/plan/año/periodo sin match del mismo año; no son 8.469 personas distintas. Se eliminaron 38.802 repeticiones del grano desde filas de asignaturas, sin modificar fuentes. Ningún CODCLI+plan se vincula a más de un RUT en PROMEDIOS.\n\nLas diferencias previas están en IECIRE S2/J4 y IECIREOL S2/J4: para V2, 23→22 y 243→241. La prueba adicional incluyendo documentos P no reproduce los conteos antiguos. La causa sigue pendiente de revisar el método original y su deduplicación. No se interpreta como pérdida de matrícula.\n\nE: No se recalcularon tasas ni denominadores. Se verificó conservación de los 61 resultados JSON/CSV existentes de retención; esto no acredita una conciliación semántica con el puente. Titulados observados se informan por persona y año de observación académica, no como año oficial de titulación.\n\n## QA independiente (C/E)\n\nPython con conjuntos y una segunda lectura con SQLite coinciden exactamente en distribuciones, agregados por plan/año/periodo, duplicados y controles MU. Las fuentes conservan sus hashes. 63 dimensiones y 141 pares dimensión/candidato. QA computacional PASS; promoción BLOQUEADA. La segunda implementación comparte el lector XLSX, pero usa otro normalizador y motor de agregación.\n\n## Pendientes exactos\n\n- Acreditar tipo y duración de cada plan UMAS, sin inferirlos del nombre, nivel máximo o versión.\n- Validar temporalidad, sede/jornada del plan y correspondencia exclusiva de cada matrícula; un RUT puede aparecer en varias carreras/versiones.\n- Resolver los dos desajustes de conteo con el método original y evidencia institucional; no aceptar P como RUT.\n- Aportar MU histórica comparable para las nueve dimensiones fuera de 2022–2026 y evidencia para las otras cuatro.\n- Conciliar denominadores, retenidos y tasas por su universo vigente antes de promover.\n- Designar responsable de gobernanza y aprobar expresamente la nueva regla.\n\n## Preservación y archivos\n\nNo se modificaron originales, BASE_RETENCION_MU, denominadores ni tasas. No hubo commit, push, cambio de rama ni carga a servicios externos. Cambios preexistentes preservados. Cruces individuales solo en memoria local; salidas agregadas.\n\nInventario con rutas y SHA-256: SHA256_ENTREGABLES.json. Fuentes: FASE0_FUENTES.json. Estados Git: GIT_ANTES.json y GIT_DESPUES.json. Tabla de 63: TABLA_63_DIMENSIONES.csv. Borradores: FASE7_CAMBIOS_PREPARADOS.md y SQL_BORRADOR.sql.\n'
(O/'INFORME_FINAL.md').write_text(report)
# Añadir metadatos de cobertura por fuente sin copiar datos personales.
for r in inv:
 if r['ruta']==str(p):r.update(periodo='2019-2026 observado',cobertura='70000 filas de asignaturas; no matriculas',llaves=['CODCLI','PLAN_DE_ESTUDIO','RUT','DIG','ANO','PERIODO'])
 elif r['ruta']==str(m):r.update(periodo='2022-2026',cobertura='10200 filas MU; 10175 tipo R y 25 tipo P',llaves=['TIPO_DOC','N_DOC','DV','ANIO_INFORMADO','COD_SED','COD_CAR','JOR','VERSION'])
 elif r['ruta'].endswith('/catalogo.json'):r.update(periodo='2027',cobertura='140 filas oferta',llaves=['codigo_unico'])
 elif r['ruta'].endswith('/maestro.json'):r.update(periodo='2010-2026 oferta observada; 2007-2009 sin evidencia',cobertura='747 observaciones oferta historica; 236 planes UMAS',llaves=['codigo_unico','anio','CODPESTUD'])
 else:r.update(periodo='derivado 2026-10-22',cobertura='segun esquema y conteos del informe',llaves='dimensiones agregadas o metadatos; no identidad individual')
js('FASE0_FUENTES.json',inv)
# Control de manifest previos.
check=[]
for mf in B.glob('*.manifest.json'):
 z=json.load(open(mf));target=B/z['archivo'];check.append({'manifiesto':str(mf),'archivo':str(target),'hash_declarado':z['sha256'],'hash_actual':digest(target),'coincide':z['sha256']==digest(target)})
q0=json.load(open(B/'QA_PUENTE_VERSIONES_20261022.json'));check.append({'manifiesto':'QA previo','coincide':q0['sha256_fuente']==digest(Path(q0['archivo_fuente']))})
js('CONTROL_MANIFIESTOS_PREVIOS.json',check)
# Identificar solo cambios propios sin tocar índice Git.
repos=[R,Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN')]
git={str(p):{k:subprocess.check_output(['git','-C',str(p),*a],text=True).strip() for k,a in {'rama':['branch','--show-current'],'HEAD':['rev-parse','HEAD'],'remotos':['remote','-v'],'status':['status','--short']}.items()} for p in repos};js('GIT_DESPUES.json',git)
paths=sorted(p for p in O.iterdir() if p.is_file() and p.name!='SHA256_ENTREGABLES.json')+[R/'docs/ESPECIFICACION_PUENTE_VERSIONES_VALIDACION_20261022.md'];js('SHA256_ENTREGABLES.json',[{'ruta':str(p),'bytes':p.stat().st_size,'sha256':digest(p)} for p in paths])
print(json.dumps({'diagnostico_documentos':diag,'comparaciones_totales':compar,'hash_informe':digest(O/'INFORME_FINAL.md'),'hash_inventario':digest(O/'SHA256_ENTREGABLES.json')},ensure_ascii=False))

"""Documenta contraste de preparación MU2025 sin adjudicar tres pendientes."""
from pathlib import Path
import json,sys,collections,subprocess,datetime
from zoneinfo import ZoneInfo
from openpyxl import load_workbook
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256,rut_normalizado
O=R/'outputs/revision_tres_jornadas_20261023_150052';read=lambda p:json.loads(Path(p).read_text());cfg=read(O/'CONFIG.json');P=Path(cfg['privado']);ev=read(P/'EVIDENCIA.json');active=R/'data/diccionario_sies_seguimiento/activo.json'
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
assert read(active)==cfg['diccionario_activo'];d=DiccionarioSiesSeguimiento();assert d.descriptor['edicion']=='v6_20261023_dos_jornadas' if hasattr(d,'descriptor') else True
# Verificar unicidad del cuerpo RUT en el universo existente antes de interpretar contactos sin DV.
allpersons={x[0] for x in d.db.execute('select distinct persona from observaciones')}
for t in ev['objetivos']:
 body=t['persona'].split('-')[0];assert {x for x in allpersons if x.split('-')[0]==body}=={t['persona']}
# Las tres observaciones siguen pendientes; código personal/documental y dimensiones no se alteraron.
for t in ev['objetivos']:
 row=json.loads(d.db.execute('select payload from observaciones where id=?',(t['observacion_id'],)).fetchone()[0]);assert not row['codigo_interno_adoptado'];assert not row['codigo_documental_atribuible']
d.close()
for p,h in cfg['fuentes_sha256'].items():assert sha256(p)==h,p
# Relectura independiente de seis celdas decisivas, identificador original con DV y fórmulas.
proc=next(Path(p) for p in cfg['fuentes_sha256'] if Path(p).name=='IPSS_Procesamiento.xlsx')
download=next(Path(p) for p in cfg['fuentes_sha256'] if Path(p).name.startswith('Descarga de lo cargado'))
caseperson={t['caso']:t['persona'] for t in ev['objetivos']}
checks=[(proc,'Precarga',1023,'INF35-03',1,1),(proc,'Final a carga',1003,'INF35-03',1,1),(proc,'2025_carga',353,'INF35-04',2,4),(download,'08-05-2025_22-26-22_Matrícula_P',1018,'INF35-03',1,1),(download,'08-05-2025_22-26-22_Matrícula_P',1949,'INF35-04',2,4)]
for p,sh,rn,case,j,v in checks:
 w=load_workbook(p,read_only=True,data_only=True);s=w[sh];row=next(s.iter_rows(min_row=rn,max_row=rn,values_only=True))
 if sh=='2025_carga':body,dv,jor,ver=row[72],row[73],row[85],row[86]
 else:body,dv,jor,ver=row[2],row[3],row[15],row[16]
 assert rut_normalizado(str(int(body))+'-'+str(dv))==caseperson[case];assert (jor,ver)==(j,v);w.close()
# Limitación de Formato: inspeccionar valores cacheados de N_DOC/DV, no considerar ausencia individual.
fmt=next(Path(p) for p in cfg['fuentes_sha256'] if Path(p).name=='Formati_SIES_2025.xlsx');w=load_workbook(fmt,read_only=True,data_only=True);s=w['Formato'];cachecounts=collections.Counter()
for row in s.iter_rows(min_row=3,values_only=True):
 try:rut_normalizado(str(int(row[1]))+'-'+str(row[2]));cachecounts['identidad_con_DV_usable']+=1
 except (ValueError,TypeError,IndexError):cachecounts['sin_identidad_con_DV_usable']+=1
w.close()
results=[
 {'caso':'INF35-03','anio':2024,'periodo':2,'clasificacion':'B/C/E','codigo_adoptado':None,'hallazgo':'Actividad T2 mezcla secciones de jornada V y D/O con iguales intervalos. J1V1 personal ya consta en precarga MU2025; no hay fecha efectiva que lo atribuya a T2-2024.','pendiente':'Jornada efectiva y versión personal en T2; no seleccionar por mayoría de secciones.'},
 {'caso':'INF35-03','anio':2024,'periodo':3,'clasificacion':'B/C/E','codigo_adoptado':None,'hallazgo':'Actividad T3 respalda D; MU2025 conserva J1V1 en Precarga, Final a carga y descarga original. MU2026 documenta J1V2. Las celdas de versión examinadas son valores, no fórmulas que reconstruyan el cambio.','pendiente':'Atribución temporal de V1/V2 al plan IINF20241 en T3-2024; no retropropagar 2025 ni usar versión de compañeros.'},
 {'caso':'INF35-04','anio':2024,'periodo':2,'clasificacion':'B/C/E','codigo_adoptado':None,'hallazgo':'SGE registra propuesta T3 el 07-oct, propuesta diurna el 08-oct, inscripción sin jornada el 09-oct y cambio relatado el 13-nov. No sitúa jornada administrativa durante julio-septiembre.','pendiente':'Confirmar continuidad J1V2 de T1 durante T2 o localizar cambio previo; nota de inscripción de octubre no identifica jornada.'}
]
dump(O/'RESULTADOS.json',{'observaciones':3,'personas':2,'cierres_adicionales':0,'tabla':results})
qa={'resultado':'OK_TECNICO_CON_PENDIENTES_E','filas_preparacion_reread':len(ev['preparacion_mu2025']),'libros_preparacion':4,'contactos_academicos_pertinentes':len(ev['contactos']),'filas_decisivas_verificadas_independientemente':len(checks),'contactos_body_RUT_unico_en_universo':True,'formato_sin_match_no_prueba_ausencia':dict(cachecounts),'observaciones_sin_adjudicar':3,'dict_v6_sin_cambios_en_revision':True,'fuentes_hashes_verificados':True,'bases_denominadores_inalterados':True,'commit_push':False}
dump(O/'QA.json',qa)
report='''# Revisión de las tres observaciones de jornada restantes

Proceso: seguimiento intertrimestral IPSS 162. Referencia T2/T3-2024; contraste documental MU2025 y MU2026. No se recalcula retención ni se modifica la cohorte.

## Dos cierres aprobados ya aplicados

**D/C.** INF35-04 T3-2024 e INF35-10 T2-2025 están en `v6_20261023_dos_jornadas` como `I162S2C1J2V4`. La atribución documental continúa **E**. El cierre es individual por contexto; no convierte secciones ni fechas de clase en reglas universales. Véase `../cierre_dos_jornadas_20261023_145844/MANIFEST.json`.

## Nueva comprobación

**B.** Se releen cuatro libros de preparación MU2025 y se encuentran 18 filas relacionadas con los dos expedientes del foco. Son registros repetidos entre etapas de preparación, no 18 personas ni respaldos independientes. Se conservan hoja, fila, valor y fórmula en PREPARACION_MU2025.json; los identificadores permanecen privados.

**B. INF35-03:** `IPSS_Procesamiento.xlsx`, `Precarga`, fila 1023, columnas P/Q = 1/1; `Carga_Completa`, fila 1025, y `Carga_Completa (2)/(3)`, fila 1030, mantienen esos componentes. `Final a carga`, fila 1003, también J1V1. La descarga original de matrícula 2025, hoja `08-05-2025_22-26-22_Matrícula_P`, fila 1018, conserva J1V1. La versión ya estaba en la precarga: no la generó este diccionario. Las celdas revisadas de VERSION son valores guardados; no se encontró allí una fórmula o fecha de migración que explique V1 frente a V2. `FECH_CAR` 16-abr-2025 en precarga y 08-may-2025 en descarga son campos observados; no se interpretan como fecha efectiva de cambio de plan.

**B. INF35-04:** GESTIONSGE_1703.xlsx, Hoja1: fila 12434 (07-oct-2024) propuesta de ramos T3 pendiente de confirmación; fila 12436 (08-oct) propuesta diurna; fila 12424 (09-oct) inscripción de ramos sin jornada explícita; fila 12427 (13-nov) relato de cambio de jornada. El nuevo enlace del 09-oct confirma inscripción, pero su texto no confirma jornada ni describe T2. MU2025 `2025_carga` fila 353 ya observa V/J2V4; no acredita que esa situación correspondiera al julio-septiembre anterior.

## Resultado por observación

| Observación | Resultado | Qué falta | Clase |
|---|---|---|---|
| INF35-03 T2-2024 | Sigue pendiente; actividad en secciones mixtas | Situar jornada y versión personal en T2 | B/C/E |
| INF35-03 T3-2024 | Jornada D respaldada; versión sin resolver | Determinar si V1 de MU2025 aplica ya en T3-2024, frente a V2 documentada después | B/C/E |
| INF35-04 T2-2024 | J1V2 sigue como candidato de continuidad T1 | Evidencia de jornada efectiva de T2 o fecha/período del cambio; inscripción de octubre sin jornada no basta | B/C/E |

**E.** No se adjudica ninguna de estas tres. La fecha de incorporación al reporte y la de matrícula anual no prueban cuándo cambió el plan. Una sección reúne estudiantes; no asigna por sí misma la versión SIES personal. JORNADA administrativa vigente en una exportación no constituye una historia por período. MODALIDAD del bloque DatosAlumnos se conserva como dato de origen y no se equipara a MODALIDAD SIES.

**C.** Identidad por RUT con DV en preparación MU; contactos con cuerpo RUT exacto y carrera IINF, verificando unicidad de ese cuerpo en el universo existente, sin inventar DV. Se excluyen notas no académicas. La hoja Formato sin correspondencia de identidad cacheada no se usa para afirmar ausencia. Los libros se leen sin recalcular ni guardar.

## Control y reanudación

**C.** Cinco filas decisivas releídas independientemente; hashes de las fuentes sin cambios; diccionario v6 intacto durante esta revisión. Tres observaciones de dos personas siguen pendientes. Seis homologaciones del foco original permanecen fuera del alcance. Para avanzar: localizar el origen anterior de J1V1 conservado en Precarga o evidencia fechada que vincule explícitamente jornada/plan a T2/T3-2024; no volver a asignar por mayoría de sección.

**D/C.** Bases, Excel y denominadores conservados. Sin commit/push. Código y evidencia agregada local; detalle restringido fuera de Git. Esto no equivale a publicación remota.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('D/C: v6 vigente; cierres aprobados INF35-04 T3-2024 e INF35-10 T2-2025 J2V4. E: tres jornadas pendientes (INF35-03 T2/T3-2024, INF35-04 T2-2024), seis homologaciones fuera de foco. Nuevo B: J1V1 ya está en Precarga MU2025 de INF35-03; inscripción INF35-04 09-oct-2024 no menciona jornada. No adjudicar por sección ni retropropagar 2025. Sin bases/denominadores modificados ni commit/push.\n')
secrets={t['persona'] for t in ev['objetivos']}|{t['CODCLI'] for t in ev['objetivos']}|{t['persona'].split('-')[0] for t in ev['objetivos']}
for p in O.iterdir():
 if p.is_file():assert not any(x in p.read_text() for x in secrets),p
for p,h in cfg['fuentes_sha256'].items():assert sha256(p)==h
assert read(active)==cfg['diccionario_activo']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='80ca13a5a249a1a2bd53a699f5f73689b1f53040'
paths=[R/'scripts/revisar_tres_jornadas_preparacion_mu2025_20261023.py',Path(__file__),R/'docs/ESPECIFICACION_CIERRE_DOS_JORNADAS_REVISION_TRES_20261023.md']
dump(O/'MANIFEST.json',{'fecha_hora':datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),'fuentes_sha256':cfg['fuentes_sha256'],'antecedentes':{'secciones':'outputs/secciones_cinco_jornadas_20261023_144650/MANIFEST.json','sha256':sha256(R/'outputs/secciones_cinco_jornadas_20261023_144650/MANIFEST.json')},'diccionario_activo':cfg['diccionario_activo'],'sha256_puntero':sha256(active),'privado':str(P),'privados_sha256':{p.name:sha256(p) for p in P.iterdir()},'salidas_sha256':{p.name:sha256(p) for p in O.iterdir() if p.is_file()},'codigo_sha256':{str(p.relative_to(R)):sha256(p) for p in paths},'QA':qa,'HEAD':head,'commit_push':False})
print(json.dumps({'reporte':str(O/'INFORME.md'),'manifest_sha256':sha256(O/'MANIFEST.json'),'QA':qa},ensure_ascii=False))

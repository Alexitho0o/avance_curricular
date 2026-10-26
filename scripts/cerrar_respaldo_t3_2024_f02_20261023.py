"""Documenta alcance de la revisión T3/F02 y comprueba conservación e integridad."""
import json,csv,hashlib,datetime,subprocess,sys,collections
from pathlib import Path
from zoneinfo import ZoneInfo
C=json.load(open(sys.argv[1]));O=Path(C['output']);P=Path(C['privado']);A=Path(C['anterior']);AP=Path(C['privado_anterior']);R=O.parents[1]
load=lambda p:json.load(open(p))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def csvout(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
s=load(O/'RESULTADOS.json');f=load(P/'F02_ANTECEDENTE.json');t3=load(P/'FILAS_T3_FOCO_16.json');pr=load(P/'F02_PLAN_ANTERIOR_2024_2.json');cmp=load(P/'COMPARACION_T3_MAESTRO.json');hashes=load(O/'FUENTES_HASHES.json')
assert s['alertas_identidad']==0 and s['filas_F02_T3']==6
assert {r['CODIGO_PLAN_ESTUDIO'] for r in t3 if r['caso']=='F02'}=={'IINF20241'}
assert len({(r['sha256'],r['hoja'],r['fila']) for r in t3})==len(t3)==43
assert all(x['maestro_coincidente'] for x in cmp)
# Distinguish file aliases and repeated observations from distinct academic events.
unique_sources={(r['sha256'],r['hoja'],r['fila']) for r in pr}
academic={(r['CODCLI'],r['CODRAMO'],r['ANO'],r['PERIODO'],r['PLAN_DE_ESTUDIO'],float(r['NOTA_FINAL']),r['DESCRIPCION_ESTADO']) for r in pr}
assert len(unique_sources)==2 and len(academic)==1
s.update(plan_anterior_observaciones_distintas=2,plan_anterior_eventos_academicos_observados=1,plan_anterior_alias_mismo_archivo=1,filas_T3_reproducidas_del_maestro=len(cmp),estado_lectura='RESUELTO: tres hojas leídas',estado_fecha_efectiva='PENDIENTE',primera_fecha_reporte_plan_nuevo=min(s['fechas_reporte_plan_nuevo']))
dump(O/'RESULTADOS.json',s)
chron=[
 {'fecha_o_periodo':'2024-04-22','dato_observado':'FECHAMATRICULA del expediente IECIREOL','alcance':'Fecha de matrícula declarada; no fecha de término de plan','clase':'B/C','fuente':'DATOSDEALUMNOS: contextos anteriores y ORIGEN DE LOS DATOS2025; localizadores privados'},
 {'fecha_o_periodo':'2024-04-24','dato_observado':'FECHAMATRICULA del expediente IINF','alcance':'Fecha de matrícula declarada; no prueba de migración efectiva','clase':'B/C','fuente':'DATOSDEALUMNOS: contextos anteriores y ORIGEN DE LOS DATOS2025; localizadores privados'},
 {'fecha_o_periodo':'2024-05-27','dato_observado':'Primera FECHA REPORTE localizada con IINF20241','alcance':'Plan nuevo observado en el reporte; no día administrativo del cambio','clase':'B/C','fuente':'CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx / MASTER INGRESO 2024'},
 {'fecha_o_periodo':'2024-2, régimen BIMESTRAL','dato_observado':'Una asignatura aprobada, nota 4,3, bajo IECIREOL20211','alcance':'Conservar el registro del plan anterior; no convertir período 2 en trimestre 2','clase':'B/C','fuente':'PROMEDIOS7804 Hoja1 fila 24336 y PROMEDIOS12166 Hoja1 fila 27236'},
 {'fecha_o_periodo':'2024-11-19','dato_observado':'Seis asignaturas IINF20241, ANO=2024, PERIODO=3','alcance':'Confirma el plan del registro T3; seis observaciones ya presentes en el maestro','clase':'B/C','fuente':'PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx / DATOS CRUDOS U+ 19-11-2024'},
 {'fecha_o_periodo':'Pendiente','dato_observado':'Fecha efectiva del cambio IECIREOL20211 → IINF20241','alcance':'No hay evento administrativo ni vigencia de asignación por expediente en lo leído','clase':'E','fuente':'Vacío acotado a las fuentes revisadas'}]
# Validate the date claims against existing contexts, not invented intervals.
for car,expected in [('IECIREOL','2024-04-22'),('IINF','2024-04-24')]:
 dates={d['fecha_matricula_iso'] for seg in f['segmentos_previos'] if seg['carrera']==car for d in seg['contextos_DA']};assert dates=={expected}
assert s['primera_fecha_reporte_plan_nuevo']=='2024-05-27'
csvout(O/'CRONOLOGIA_F02_SIN_IDENTIFICADORES.csv',chron)
privrows=[]
for r in t3:
 if r['caso']=='F02':
  privrows.append({'caso':'F02','persona_RUT':r['persona'],'RUT_original':r['RUT_original'],'CODCLI':r['CODCLI'],'carrera':r['CODCARRERA_ALUMNO'],'plan':r['CODIGO_PLAN_ESTUDIO'],'ano':r['ANO'],'periodo':r['PERIODO'],'asignatura':r['ASIGNATURA'],'codigo_asignatura':r['CODIGO_ASIGNATURA'],'seccion':r['SECCION'],'fecha_inicio_asignatura':r['fechas_normalizadas']['FECHAINICIO'],'fecha_fin_asignatura':r['fechas_normalizadas']['FECHAFIN'],'fecha_medicion':r['fechas_normalizadas']['FECHA MEDICION'],'archivo':r['archivo'],'hoja':r['hoja'],'fila':r['fila'],'sha256':r['sha256'],'fecha_cambio_plan':'Pendiente'})
csvout(P/'F02_T3_DETALLE.csv',privrows)
for path,h in hashes.items():assert sha(path)==h
# Prior delivery must remain byte-for-byte intact.
previous=load(A/'MANIFEST.json');checked=0
for base,key in [(A,'salidas_agregadas_hashes'),(AP,'salidas_privadas_hashes')]:
 for name,h in previous[key].items():assert sha(base/name)==h,name;checked+=1
before=load(O/'GIT_ANTES.json')
def git(*args):return subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
after={'rama':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'status':git('status','--short'),'remotos':git('remote','-v')};assert all(before[k]==after[k] for k in ['rama','head','remotos'])
added=sorted(set(after['status'].splitlines())-set(before['status'].splitlines()));removed=sorted(set(before['status'].splitlines())-set(after['status'].splitlines()));assert not removed
allowed={'?? docs/ESPECIFICACION_REVISION_T3_2024_F02_20261023.md','?? scripts/revisar_respaldo_t3_2024_f02_20261023.py','?? scripts/cerrar_respaldo_t3_2024_f02_20261023.py'}
assert set(added)<=allowed,added
dump(O/'GIT_DESPUES.json',after)
report='''# Respaldo T3-2024 recuperado: revisión de la persona F02

**Resultado:** se resolvió el acceso al respaldo y se confirmó el plan observado de F02 en T3-2024. No se acreditó la fecha administrativa exacta de cambio de plan. Se conserva el registro del plan anterior y no se modifican las bases, versiones adoptadas ni denominadores.

Proceso: conciliación histórica UMAS–SIES del puente de retención IPSS 162. Referencia: matrícula y actividad académica de 2024. No es recálculo de retención ni aplicación de reglas MU2027. No hay una regla A nueva: B identifica datos, C identifica el cruce, D conserva la decisión de no alterar indicadores y E mantiene lo no demostrado.

## 1. Respaldo íntegro y disponible — B/C

`PRUEBA CUMPLIMIENTO INGRESO CALIFICACIONES T3_2024.xlsx`: 1.253.761 bytes. SHA-256 recalculado:

`97c0fc4fbe4dd9a24be611d0960f4ad6c1559db907a9d86d12a039bc89110fa6`

Coincide con el hash anterior. Se leyeron íntegramente sus tres hojas:

| Hoja | Lectura | Uso |
|---|---:|---|
| RESUMEN | 63 filas no vacías en un rango de 160×13 | Resumen inspeccionado; no llave individual |
| DATOS CRUDOS U+ 19-11-2024 | 4.155 registros, 27 columnas | CODCLI + cuerpo de RUT corroborado; plan y fechas |
| ERRORES | 3 registros, 25 columnas | Ninguno corresponde a las 16 personas del foco |

Los RUT de estudiantes se corroboraron con sus CODCLI; el campo DIG del docente no se utilizó. Se localizaron 43 filas de 12 personas del foco anterior, sin nuevos expedientes no reconocidos. Las 43 reproducen observaciones del maestro en los campos contrastados (expediente, plan, carrera, año/período, asignatura, sección, fechas y estados). No se cuentan como 43 evidencias independientes nuevas ni se afirma identidad total de ambos libros.

## 2. Qué confirma para F02 — B/C

- Seis asignaturas bajo **IINF20241**, ANO=2024 y PERIODO=3.
- FECHA MEDICION = **19-11-2024**.
- FECHAINICIO = **14-10-2024** y FECHAFIN = **04-01-2025** para las seis asignaturas. Son fechas de asignaturas, no de cambio de plan.
- Las seis observaciones coinciden con las ya leídas en `CUMPLIMIENTO INGRESO CALIFICACIONES.xlsx`, hoja `MASTER INGRESO 2024`. El respaldo confirma lo observado, pero no agrega una fecha anterior.
- La primera FECHA REPORTE localizada con IINF20241 sigue siendo **27-05-2024**, en el maestro. Esto confirma que el reporte lo vincula al plan nuevo en esa fecha; no demuestra que el cambio ocurriera exactamente ese día.

## 3. Por qué no se debe borrar el plan anterior — B/C

Se releyeron cinco rutas de PROMEDIOS, incluyendo dos copias idénticas de PROMEDIOS7804. El expediente anterior conserva **una asignatura** en 2024-2, régimen **BIMESTRAL**, plan **IECIREOL20211**:

`AS101IECIREOL — HABILIDADES PARA EL APRENDIZAJE DIGITAL`, APROBADO, nota 4,3, sin marca de convalidación en esas filas.

Está en PROMEDIOS7804, Hoja1 fila 24336, y PROMEDIOS12166, Hoja1 fila 27236. Son dos observaciones de una misma asignatura; las dos rutas con el mismo hash de PROMEDIOS7804 no se cuentan dos veces. No se infiere la fecha del evento a partir del corte o del nombre de estos archivos.

La presencia de esa asignatura impide sustituir automáticamente todos los registros de 2024 por IINF20241. Tampoco autoriza convertir el período bimestral 2 en el trimestre 2 del plan nuevo.

## 4. Cronología comprobable y límite

| Fecha/período | Observación | Clasificación y límite |
|---|---|---|
| 22-04-2024 | FECHAMATRICULA del expediente IECIREOL | B/C; no acredita fin del plan anterior |
| 24-04-2024 | FECHAMATRICULA del expediente IINF | B/C; no acredita por sí sola una migración |
| 27-05-2024 | Primera FECHA REPORTE localizada con IINF20241 | B/C; primera observación fechada localizada del plan nuevo |
| 2024-2 bimestral | Una asignatura aprobada bajo IECIREOL20211 | B; no consta día de asignación/cierre del plan |
| 19-11-2024 | Seis asignaturas del período 3 bajo IINF20241 | B/C; confirmación del respaldo T3 |
| Día efectivo del cambio | No consta en los campos leídos | E; no se elige 24-abril ni 27-mayo como fecha de migración |

Las dos fechas de matrícula están declaradas para expedientes distintos, no constituyen por sí solas un intervalo de cambio de plan. La semántica histórica de FECHAMATRICULA y el linaje temporal de PLAN_DE_ESTUDIO siguen limitados por el contrato gobernado; ver `docs/fase_4_planes_asignaciones_umas.md`, sección “Qué se sabe de la vigencia”.

**Conclusión:** puede confirmarse **IINF20241 como plan observado en el respaldo T3**, y desde la fecha declarada de reporte 27-mayo en el maestro. No puede confirmarse el día exacto en que dejó IECIREOL20211 ni trasladar automáticamente una versión SIES a todos los períodos. MU2024 conserva su código anual documentado **I162S2C1J4V2**; no se demostró un cambio adicional de versión SIES por este hallazgo.

## 5. Preservación, QA y reanudación

**D:** se conservan 5.901 personas, 6.622 expedientes y 24.774 observaciones. No se reducen pendientes globales por llamar “resuelta” a una corroboración parcial. Ninguna fuente, base, tasa ni código adoptado fue modificado.

**C:** QA técnico OK: lectura de las tres hojas, identidad corroborada, cero alertas de cruce, seis filas F02 contrastadas con maestro, dos observaciones de una sola asignatura antigua, hashes de entradas y de la entrega anterior conservados. **E:** la fecha efectiva sigue pendiente documental; QA técnico no la convierte en confirmación funcional.

Detalle restringido y localizadores fuente/hoja/fila: carpeta privada indicada en MANIFEST.json, especialmente F02_T3_DETALLE.csv, F02_PROMEDIOS_RELECTURA.json y F02_CRONOLOGIA_FUENTES.json. Los datos personales permanecen fuera de Git. El respaldo original no se mueve ni sobrescribe.

Reanudación precisa: si se localiza un registro de asignación/migración con CODCLI, plan anterior/nuevo y fecha efectiva, contrastarlo con esta secuencia. El error de lectura T3 está resuelto; no volver a solicitar ese archivo ni confundirlo con la evidencia administrativa que aún falta. No es necesario repetir los 16 cruces ni la búsqueda completa de versiones.

Sin commit, push, merge, PR ni cargas externas. Rama feature/ire-2026, HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes y después.
'''
(O/'INFORME_F02_T3_2024.md').write_text(report)
(O/'CHECKPOINT.md').write_text('''# Checkpoint T3-2024 / F02

Fase 1/3 · Hitos 1–3: contratos, hash y tres hojas del respaldo leídos. Bloqueo OneDrive resuelto.
Fase 2/3 · Hitos 1–3: CODCLI y cuerpo RUT corroborados; seis filas F02 reproducen maestro; una asignatura del plan antiguo preservada, sin doble conteo de copias.
Fase 3/3 · Hitos 1–3: informe, cronología, detalle privado, manifiesto y QA. Ningún cambio al canon.

Plan IINF20241 observado en reporte de 27-05-2024 y confirmado en T3 el 19-11-2024. Fecha efectiva administrativa: E, pendiente. La presencia de la asignatura anterior en 2024-2 se conserva. No tocar bases ni denominadores. Consulta INFORME_F02_T3_2024.md y MANIFEST.json antes de reanudar.
''')
qa={'estado_tecnico':'OK','estado_funcional_fecha':'PENDIENTE_E','hojas_completas':3,'hash_T3_coincide_anterior':True,'alertas_identidad':0,'filas_F02':6,'filas_F02_reproducidas_maestro':6,'filas_T3_foco_reproducidas_maestro':43,'duplicados_fuente_hoja_fila_T3':0,'observaciones_fuente_asignatura_antigua':2,'asignaturas_antiguas_distintas':1,'alias_mismo_7804_excluidos_del_conteo':1,'archivos_entrega_anterior_verificados':checked,'entradas_hash_conservadas':len(hashes),'bases_y_denominadores_sin_cambios':True,'codigo_adoptado_sin_cambios':True,'rama_head_remotos_conservados':True,'cambios_git_previos_conservados':True,'nuevos_archivos_status':added,'privado_fuera_git':subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0,'limites':['Sin evento de cambio administrativo de plan','No equiparar fechas de asignatura/matrícula/medición','No equiparar período bimestral a trimestre por su número']}
# Privacy validation against identities from the focus, no personal IDs in aggregate outputs or code.
focus=load(AP/'REVISION_16_CASOS_FINAL.json');ids={x['persona'] for x in focus}|{seg['CODCLI'] for x in focus for seg in x['segmentos_previos']}
scriptpaths=[R/'scripts/revisar_respaldo_t3_2024_f02_20261023.py',R/'scripts/cerrar_respaldo_t3_2024_f02_20261023.py']
for path in list(O.iterdir())+scriptpaths+[R/'docs/ESPECIFICACION_REVISION_T3_2024_F02_20261023.md']:
 if path.is_file():assert not any(i and i in path.read_text() for i in ids),str(path)
qa['salidas_agregadas_sin_identificadores']=True;dump(O/'QA.json',qa)
for path in P.iterdir():path.chmod(0o600)
manifest={'fecha':datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),'alcance':'Recuperación de lectura T3-2024 y revisión dirigida F02','fuentes_sha256':hashes,'entrega_anterior_manifest':{'archivo':str(A/'MANIFEST.json'),'sha256':sha(A/'MANIFEST.json')},'resultado':s,'qa':qa,'privado':str(P),'scripts':{str(p):sha(p) for p in scriptpaths},'reproduccion':['revisar_respaldo_t3_2024_f02_20261023.py CONFIG.json','cerrar_respaldo_t3_2024_f02_20261023.py CONFIG.json'],'salidas_privadas_hashes':{p.name:sha(p) for p in P.iterdir() if p.is_file()},'salidas_agregadas_hashes':{p.name:sha(p) for p in O.iterdir() if p.is_file() and p.name!='MANIFEST.json'},'bases_modificadas':False,'denominadores_modificados':False,'commit':False,'push':False,'git_antes':before,'git_despues':after}
dump(O/'MANIFEST.json',manifest)
print(json.dumps({'QA':qa,'informe':str(O/'INFORME_F02_T3_2024.md'),'sha256_informe':sha(O/'INFORME_F02_T3_2024.md')},ensure_ascii=False))

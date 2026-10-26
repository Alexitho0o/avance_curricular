"""Cierra evidencia de jornadas y QA de consumidores; no adopta otros códigos."""
from pathlib import Path
import json,sys,subprocess,collections,csv,datetime,os
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=R/'outputs/cierre_14_jornadas_15_20261023_133759';cfg=json.loads((O/'CONFIG.json').read_text());P=Path(cfg['privado']);V=Path(cfg['edicion']);oldV=R/'data/diccionario_sies_seguimiento/v1_20261023';prev=Path(cfg['revision_previa'])
def read(p):return json.loads(p.read_text())
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):os.chmod(p,0o600)
rs=read(P/'REVISION_35_ANTERIOR.json');focus=[r for r in rs if r['resultado_revision']=='E_CAMBIO_JORNADA_SIN_PERIODO'];rows=read(P/'JORNADAS_15_CONTEXTO_COMPLETO.json');new=read(P/'RESPALDOS_JORNADA_RELEIDOS.json');assert len(focus)==15
results=[];public=[]
for x in focus:
 rr=[r for r in rows if r.get('CODCLI')==x['CODCLI'] and r['persona']==x['persona']]
 snap=[r for r in new if r.get('CODCLI')==x['CODCLI'] and r['persona']==x['persona'] and Path(r['fuente']).name=='Matrícula T3_2025 2.xlsx' and r['hoja']=='T3_2025']
 suggestion=x['caso']=='INF35-07' and str(x['periodo_nativo'])=='3'
 if suggestion:
  assert x['anio']==2025 and x['codigo_origen_documentado']=='I162S2C1J2V4'
  assert len(snap)==1 and snap[0]['JORNADA']=='V'
  assert any(r.get('PLAN_DE_ESTUDIO')=='IINF20241' and r.get('ANO')=='2025' and r.get('PERIODO')=='3' for r in rr)
 results.append({'caso':x['caso'],'persona':x['persona'],'CODCLI':x['CODCLI'],'anio':x['anio'],'periodo':x['periodo_nativo'],'observacion_id':x['original_consulta']['observacion_id'],'codigo_T1':x['codigo_origen_documentado'],'propuesta_destino_no_aplicada':'I162S2C1J2V4' if suggestion else '', 'resultado':'PROPUESTA_INTERNA_RESPALDADA_FOTO_T3' if suggestion else 'E_PERIODO_CAMBIO_NO_ACREDITADO','clasificacion':'B foto, C enlace, E adopción adicional pendiente' if suggestion else 'B diferencias observadas; E periodo efectivo','evidencia_foto':snap,'marcas_49':[r for r in rr if r.get('SITUACION','').startswith('49')],'evidencias':rr})
assert sum(bool(r['propuesta_destino_no_aplicada']) for r in results)==1
notes={
'INF35-01':'MU2024/T1 J1V2 y MU2025 J1V2; fotografía T3-2025 D; MU2026 J4V2 y DA actual O. No se acredita la jornada de cada T2/T3-2024 ni el evento de cambio.',
'INF35-02':'MU2024/T1 J1V2; PROMEDIOS_2071 D, _3233 O; foto T3-2025 O y marca 49. La marca no fecha el cambio. MU2025 aún J1V2; discordancia entre fuentes conservada.',
'INF35-03':'MU2024/T1 J2V4; PROMEDIOS_2071/_3233 D; foto T3-2025 D y marca 49. MU2025 J1V1 y MU2026 J1V2; DA actual O. No asignar versión por jornada sola.',
'INF35-04':'MU2024/T1 J1V2; PROMEDIOS_2071 V, _3233 D; foto T3-2025 D y marca 49, pero MU2025 J2V4. No hay intervalo inequívoco para T2/T3-2024.',
'INF35-07':'MU2025/T1 J2V4 y foto T3-2025 V para el mismo CODCLI; PROMEDIOS conserva plan IINF20241 con actividad período 3. Propuesta J2V4 para T3. T2 sin foto comparable en archivo T2. Respaldos posteriores muestran O, sin fecha efectiva.',
'INF35-10':'MU2025/T1 J2V4; DA_4094/3194 V; DA_4490/4649 y foto T3-2025 O con marca 49. El cambio se observa entre respaldos; FECHAMATRICULA permanece 24-01-2025. No decide la jornada de T2-2025.',
'INF35-11':'MU2026/T1 J1V2 y PROMEDIOS_7804 D; PROMEDIOS_12166 y DA actual O, marca 49. Sin match en fotos T2/T3-2026 aportadas; no prueba ausencia académica ni período de cambio.',
'INF35-12':'MU2026/T1 J4V2 y PROMEDIOS_7804 O; PROMEDIOS_12166 y DA actual D, marca 49. Sin match en fotos T2/T3-2026 aportadas; falta intervalo de cambio.'}
for case in sorted({x['caso'] for x in focus}):
 z=[r for r in results if r['caso']==case];public.append({'caso_revision':case,'anio':z[0]['anio'],'periodos':','.join(str(r['periodo']) for r in z),'observaciones':len(z),'codigo_T1':z[0]['codigo_T1'],'propuestas_adicionales':sum(bool(r['propuesta_destino_no_aplicada']) for r in z),'hallazgo':notes[case],'clasificacion':'B/C hallazgos; E período/atribución pendiente salvo propuesta expresamente indicada'})
dump(P/'REVISION_JORNADAS_15.json',results)
with (O/'RESUMEN_JORNADAS_15.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(public[0]),delimiter=';');w.writeheader();w.writerows(public)
# Comparar consumidores reales sin imprimir identidades.
req=[]
for x in rs:
 t=x['original_consulta'];req.append({'metodo':'consultar','entrada':dict(persona=t['persona'],codcli=t['codcli'],plan=t['plan'],anio=t['anio'],periodo=t['periodo_nativo'],carrera=t['carrera_umas'],sede=t['evidencia']['sede_dimension'],jornada=t['evidencia']['jornada_sies'])})
outputs=[]
for i,script in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
 out=P/('QA_CONSUMIDOR_'+str(i)+'.json');assert not out.exists();run=subprocess.run([sys.executable,'-B',str(R/script),'--salida-privada',str(out)],input=json.dumps(req),capture_output=True,text=True);assert run.returncode==0,run.stderr;outputs.append(read(out))
assert outputs[0]==outputs[1]==outputs[2]
assert collections.Counter(x['estado'] for x in outputs[0])=={'REUTILIZABLE':14,'EXCEPCION':21}
assert all(x['codigo_documental'] is None for x in outputs[0] if x['estado']=='REUTILIZABLE')
# Confirmar no extrapolación a otros períodos de las ocho anclas.
assert all(outputs[0][rs.index(x)]['estado']=='EXCEPCION' for x in focus)
test=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_diccionario_sies_seguimiento'],cwd=R,capture_output=True,text=True);assert test.returncode==0;(O/'PRUEBAS_SINTETICAS.txt').write_text(test.stdout+test.stderr)
inputs=read(O/'FUENTES_HISTORICO_HASHES.json');desc=read(V/'descriptor.json');inputs.update(desc['entradas_cierre_sha256']);prior=read(prev/'MANIFEST.json');inputs[str(prev/'MANIFEST.json')]=sha256(prev/'MANIFEST.json');inputs[str(Path(prior['privado'])/'FILAS_RELEIDAS.json')]=prior['privado_hashes']['FILAS_RELEIDAS.json']
for path,h in inputs.items():assert sha256(path)==h
book=Path('/Users/alexi/Desktop/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx');assert sha256(book)=='e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe';inputs[str(book)]=sha256(book)
branch=subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip();head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();assert head==cfg['HEAD_antes'];assert branch=='feature/ire-2026'
marked={r['persona'] for r in results if r['marcas_49']};assert len(marked)==7
summary={'cierres_aplicados':14,'personas_alcance_cierre':10,'contextos_antes':35,'pendientes_foco_despues':21,'jornadas_revisadas':15,'personas_jornadas':8,'personas_con_marca_49_en_algun_respaldo':7,'propuesta_adicional_T3_2025':1,'jornadas_sin_propuesta_adicional':14,'propuestas_adicionales_aplicadas':0,'otras_6_homologaciones_intactas':True,'nuevas_fuentes_leidas':15,'filas_foco_nuevas':33,'edicion_activa':desc['edicion']}
dump(O/'RESULTADOS.json',summary)
qa=read(O/'QA_CIERRE.json');qa.update(resultado='OK_CON_ADVERTENCIAS',consumidores_comparados=3,consultas_por_consumidor=35,pruebas_sinteticas=12,marcas_49_no_usadas_como_fecha=True,propuesta_adicional_no_aplicada=True,excel_hash_inalterado=sha256(book),fuentes_historicas_reverificadas=True,HEAD_antes=head,HEAD_despues=head,rama=branch,commit_push=False,advertencias=['15 destinos T2/T3 permanecen sin adjudicación adicional; uno tiene propuesta respaldada por foto T3.','Marcas 49 y fechas de matrícula no acreditan fecha efectiva de cambio.','Los 14 cierres son internos D; el pendiente documental no cambia.'])
dump(O/'QA_FINAL.json',qa)
report='''# Cierre de 14 correspondencias y revisión de 15 jornadas

**D/C. Aplicados los 14 cierres autorizados** en la edición común `v2_20261023_14`: ocho anclas T1 con contexto histórico explícito y seis correspondencias por puente pasaporte–RUT. Se conserva v1, la decisión del usuario, fecha/hora, responsable Alexi, alerta de cambio y operaciones antes/después. Son correspondencias internas aprobadas; el campo documental y la aceptación SIES no se alteraron.

**C.** Las 35 observaciones del foco quedan en **14 reutilizables y 21 pendientes**. Dos enlaces de identidad P–RUT se añadieron al índice de consulta, conservando sus documentos originales; no se añadieron matrículas a las fuentes. Los tres consumidores locales usan el mismo puntero activo. No se afirma actualización de complementos remotos.

## Revisión adicional de T2/T3

**B/C.** Se contrastaron 15 observaciones de ocho personas contra 15 archivos adicionales: once respaldos de DatosAlumnos y las cuatro fotografías T2/T3 aportadas. Se recuperaron 33 filas del foco; cero conflictos de identidad. Los respaldos releídos se registran por hash, hoja y fila en el detalle privado. El inventario conserva también hojas sin llave individual; no se confunden tablas resumen con bases completas.

| Resultado | Observaciones | Clasificación |
|---|---:|---|
| Propuesta adicional respaldada: I162S2C1J2V4 para T3-2025 | 1 | B foto; C enlace; E adopción pendiente |
| Sin período de cambio inequívocamente acreditado | 14 | E |
| Total revisado; ninguno de estos 15 aplicado en este cierre | 15 | C |

**B/C. INF35-07:** MU2025 documenta I162S2C1J2V4; la hoja `T3_2025` del archivo Matrícula T3_2025 2.xlsx conserva jornada V para el mismo RUT y CODCLI. PROMEDIOS acredita el plan IINF20241 y actividad en período 3. Esto permite proponer reutilización interna de **J2V4 en T3-2025**, sin necesitar el día exacto de cambio. Los respaldos posteriores muestran O. No prueba envío SIES en T3 ni se extiende automáticamente a T2. La propuesta quedó sin aplicar: la autorización de cierre era para los 14 anteriores.

**B.** Siete de las ocho personas tienen `49 - CAMBIO DE JORNADA` en al menos un respaldo. Esto corrobora la existencia de una marca administrativa de cambio; no determina cuándo fue efectivo ni que sea el único cambio ocurrido. La octava tiene otras situaciones, no marca 49 en la cobertura revisada.

**B/E. INF35-10:** DA_4094 y DA_3194 registran V; DA_4490, DA_4649 y la foto T3-2025 registran O con marca 49. En todos se conserva FECHAMATRICULA=24-01-2025. Esa fecha no puede usarse como fecha de cambio: permanece igual pese a cambiar jornada/situación. Se ubicó el cambio entre respaldos, pero no permite adjudicar el T2-2025 pendiente. No se infiere la cronología por el número del archivo.

**B/E.** Los otros casos conservan desacuerdos de jornada entre MU, reportes históricos y reportes actuales. En algunos, el mismo plan IINF20241 aparece con D, V u O en distintas exportaciones. El nombre del plan no decide por sí solo versión ni jornada histórica. Los respaldos 2024 de notas confirman actividad/plan/fechas de cursos, pero no el código SIES o la fecha efectiva de migración de jornada.

**B/E.** Los archivos T2 aportados y T3-2026 no añaden coincidencias individuales para este foco; se revisaron las hojas con llaves. Esa ausencia se limita a esos listados y no acredita deserción. Las seis homologaciones TPAS fuera del foco de jornadas continúan pendientes y no fueron reclasificadas.

Ver `RESUMEN_JORNADAS_15.csv` para las ocho trayectorias, códigos T1 y respaldo por caso. Los identificadores y filas originales están únicamente en la carpeta privada declarada por el manifiesto.

## QA y conservación

**C.** 24.774 consultas comparadas entre v1/v2: exactamente 14 cierres; 24.760 respuestas restantes idénticas, salvo identificación de edición. Las dimensiones y códigos documentales originales no cambiaron. Tres consumidores locales: 35/35 respuestas iguales. Doce pruebas sintéticas correctas. Las consultas del foco siguen con 14 reutilizables y 21 pendientes. Las fuentes y el Excel V12 conservan sus hashes.

**C/E. QA OK_CON_ADVERTENCIAS:** las advertencias son la atribución documental pendiente y los destinos sin período acreditado; no hay un fallo de integridad abierto. Dos intentos de preparación se detuvieron antes de promover el puntero por controles del script (alcance del índice histórico y tipo textual de período); quedaron separados como intentos no promovidos. El intento final superó los controles completos antes de activar v2.

**D/C.** Bases, fórmulas, denominadores, tasas y Excel no modificados. Rama feature/ire-2026 y HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 conservados. Sin commit ni push.

**E. Reanudación:** valorar la propuesta acotada INF35-07/T3-2025 como correspondencia interna. Para los otros catorce destinos falta un registro de jornada aplicable al cierre/período, o un intervalo de cambio respaldado; no una nueva fórmula ni una equivalencia universal del plan. La versión de origen T1 permanece disponible para seguir la cohorte.
'''
(O/'INFORME.md').write_text(report);(O/'CHECKPOINT.md').write_text('D/C: v2_20261023_14 activa; 14 cierres aprobados. B/C: QA completo, mismos originales y denominadores. E: 21 pendientes del foco; entre 15 jornadas hay una propuesta adicional T3-2025 J2V4 no aplicada y 14 sin período acreditado. Las seis homologaciones siguen pendientes. Sin commit/push. Ver INFORME.md y MANIFEST.json.\n')
# No identificadores del foco en los resultados compartibles.
secrets={x['persona'] for x in rs}|{x['CODCLI'] for x in rs}
for directory in [O,V]:
 for f in directory.iterdir():
  if f.is_file() and f.suffix in ('.json','.csv','.md','.txt'):assert not any(v in f.read_text() for v in secrets)
files={str(f):sha256(f) for f in list(O.iterdir())+list(V.iterdir()) if f.is_file() and f.name!='MANIFEST.json'}
manifest={'fecha_hora':datetime.datetime.now().astimezone().isoformat(),'clasificacion':'D cierres autorizados; B/C evidencia y QA; E destinos pendientes','edicion_activa':desc['edicion'],'descriptor':str(V/'descriptor.json'),'sha256_descriptor':sha256(V/'descriptor.json'),'fuentes_hashes':inputs,'salidas_hashes':files,'privado':str(P),'privados_hashes':{f.name:sha256(f) for f in P.iterdir() if f.is_file()},'codigo_hashes':{str(p.relative_to(R)):sha256(p) for p in [R/'scripts/cerrar_14_diccionario_20261023.py',R/'scripts/revisar_jornadas_15_20261023.py',R/'scripts/finalizar_cierre_14_jornadas_15_20261023.py',R/'docs/ESPECIFICACION_CIERRE_14_JORNADAS_15_20261023.md',R/'docs/DICCIONARIO_SIES_SEGUIMIENTO.md']},'resultado':summary,'QA':qa,'responsable_decision':'Alexi','originales_denominadores_modificados':False,'sin_commit_push':True}
dump(O/'MANIFEST.json',manifest);print(json.dumps(summary,ensure_ascii=False));print('QA OK_CON_ADVERTENCIAS');print(O/'INFORME.md')

"""QA de cierre único y evidencia temporal; sin otros cambios de diccionario."""
from pathlib import Path
import sys,json,subprocess,collections,datetime,csv
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=R/'outputs/cierre_inf35_07_jornadas_14_20261023_135630';read=lambda p:json.loads(p.read_text());cfg=read(O/'CONFIG.json');P=Path(cfg['privado']);V=Path(cfg['edicion']);prev=Path(cfg['anterior']);pm=read(prev/'MANIFEST.json');pp=Path(pm['privado'])
def dump(p,x):
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
 if p.is_relative_to(P):p.chmod(0o600)
rs=read(pp/'REVISION_35_ANTERIOR.json');rows=read(P/'FILAS_CORTES_VERIFICADAS.json');focus=read(P/'JORNADAS_14_PENDIENTES.json');changes=read(P/'CAMBIOS_AUDITORIA_FOCO.json');summary=read(O/'RESUMEN_CORTES.json')
assert len(rows)==48 and len(focus)==14
requests=[]
for r in rs:
 t=r['original_consulta'];requests.append({'metodo':'consultar','entrada':dict(persona=t['persona'],codcli=t['codcli'],plan=t['plan'],anio=t['anio'],periodo=t['periodo_nativo'],carrera=t['carrera_umas'],sede=t['evidencia']['sede_dimension'],jornada=t['evidencia']['jornada_sies'])})
outputs=[]
for i,script in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
 out=P/('QA_CONSUMIDOR_'+str(i)+'.json');assert not out.exists();run=subprocess.run([sys.executable,'-B',str(R/script),'--salida-privada',str(out)],input=json.dumps(requests),text=True,capture_output=True);assert run.returncode==0,run.stderr;outputs.append(read(out))
assert outputs[0]==outputs[1]==outputs[2];assert collections.Counter(x['estado'] for x in outputs[0])=={'REUTILIZABLE':15,'EXCEPCION':20}
assert all(x['codigo_documental'] is None for x in outputs[0] if x['estado']=='REUTILIZABLE')
oldqueries=read(pp/'QA_CONSUMIDOR_0.json');diff=[]
for i,(b,a) in enumerate(zip(oldqueries,outputs[0])):
 b=dict(b);a=dict(a);b.pop('edicion');a.pop('edicion')
 if b!=a:diff.append(i)
assert len(diff)==1 and rs[diff[0]]['caso']=='INF35-07' and str(rs[diff[0]]['periodo_nativo'])=='3'
test=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_diccionario_sies_seguimiento'],cwd=R,text=True,capture_output=True);assert test.returncode==0;(O/'PRUEBAS_SINTETICAS.txt').write_text(test.stdout+test.stderr)
inputs=read(O/'FUENTES_CORTES_HASHES.json');desc=read(V/'descriptor.json');inputs.update(desc['entradas_cierre_sha256'])
for f,h in inputs.items():assert sha256(f)==h
book=Path('/Users/alexi/Desktop/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx');bh=sha256(book);assert bh=='e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe';inputs[str(book)]=bh
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();branch=subprocess.check_output(['git','-C',str(R),'branch','--show-current'],text=True).strip();assert head==cfg['HEAD_antes']=='80ca13a5a249a1a2bd53a699f5f73689b1f53040';assert branch=='feature/ire-2026'
# Las fechas son cortes nominales del extractor. Se acredita el cambio de dato, no fecha de acto académico.
transition=[r for r in changes if r['campo']=='JORNADA'];assert len(transition)==1 and transition[0]['caso']=='INF35-12'
proof=[r for r in rows if r['caso']=='INF35-12'];assert {r['JORNADA'] for r in proof if r['corte_nominal'].startswith(('2026-07','2026-08','2026-09-29'))}=={'O'};assert {r['JORNADA'] for r in proof if r['corte_nominal'].startswith(('2026-09-30','2026-10'))}=={'D'}
with (O/'RESUMEN_14_OBSERVACIONES.csv').open('w',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Caso de revisión','Año','Período','Código T1 conservado','Resultado temporal','Código destino','Clasificación'])
 for r in focus:
  note='O→D entre respaldos nominales 29 y 30 septiembre 2026; D corroborado 2 octubre. Falta atribuir versión destino; no fecha efectiva del acto.' if r['caso']=='INF35-12' else 'Sin intervalo aplicable acreditado para este período; auditoría disponible comienza agosto 2026.'
  w.writerow([r['caso'],r['anio'],r['periodo'],r['codigo_T1'],note,'Pendiente','B observaciones; E atribución período/versión'])
result={'cierre_nuevo_aplicado':1,'codigo':'I162S2C1J2V4','caso':'INF35-07','periodo':'T3-2025','clasificacion_cierre':'D correspondencia interna','edicion_activa':desc['edicion'],'foco_original':35,'reutilizables_foco':15,'pendientes_foco':20,'jornadas_pendientes':14,'homologaciones_pendientes':6,'personas_jornadas_revisadas':8,'intervalos_nuevos_observados':1,'caso_intervalo':'INF35-12','intervalo_nominal':['2026-09-29T12:00:39','2026-09-30T12:00:38'],'fuentes_originales_releidas':6,'filas_exactas_corroborradas':48,'cortes_auditoria_consultada':58,'cobertura_auditoria':['2026-08-25','2026-10-21'],'otros_cierres':0}
dump(O/'RESULTADOS.json',result)
qa=read(O/'QA_CIERRE.json');qa.update(resultado='OK_CON_ADVERTENCIAS',consumidores=3,consultas_por_consumidor=35,pruebas_sinteticas=12,conservacion_excel=bh,identidad_codcli_carrera_clave_matricula_conservada_en_intervalo=True,fuentes_6_hash_conforme=True,auditoria_preexistente_hash_conforme=True,HEAD_antes=head,HEAD_despues=head,rama=branch,commit_push=False,limites=['La auditoría de 58 cortes fue reutilizada como derivado gobernado; se releyeron seis originales, no se reconstruyeron los 58.','Cortes nominales y zona horaria no confirmada; el intervalo acredita cambio entre respaldos, no fecha efectiva del acto.','No se determinó versión SIES de destino a partir de jornada sola.','No se extrapoló agosto-octubre 2026 a los períodos 2024 o 2025.'])
dump(O/'QA_FINAL.json',qa)
report='''# INF35-07 cerrado y revisión temporal de 14 observaciones

**D/C.** Aplicada la autorización de Alexi: **INF35-07/T3-2025 → I162S2C1J2V4**, como correspondencia interna. Edición activa `v3_20261023_inf35_07`. Conserva v2 y las decisiones previas; el documental y aceptación SIES siguen pendientes. La jornada V observada en la foto T3 no se confunde con O del contexto posterior conservado. Solo se adjudicó esta observación.

**C.** Foco original de 35 observaciones: **15 reutilizables y 20 pendientes** (14 destinos de jornada y 6 homologaciones TPAS). No son 35 personas ni denominadores de retención.

## Hallazgo nuevo: INF35-12

**B.** Se localizaron en la auditoría gobernada de DatosAlumnos y se releyeron directamente los respaldos originales:

| Respaldo nominal | Jornada observada |
|---|---|
| DATOSDEALUMNOS_10246, congelamiento 21-jul-2026 | O |
| 25-ago-2026 | O |
| 29-sep-2026 12:00:39 | O |
| 30-sep-2026 12:00:38 | D |
| 2-oct-2026 12:00:40 | D |
| 21-oct-2026 12:00:37 | D |

**B/C.** Entre las extracciones nominales del 29 y 30 de septiembre cambia JORNADA de O a D, conservando RUT, CODCLI, carrera y clave de matrícula. Cambia también SITUACION; FECHAMATRICULA se mantiene. El respaldo de 2 de octubre corrobora D. La relación con la fuente está registrada por hoja, fila y hash en el detalle privado.

**E.** Esto acota cuándo aparece el cambio en los datos, no acredita la fecha efectiva de la solicitud/acto académico. La auditoría declara zona horaria de cortes no confirmada. No se presenta el instante del archivo como fecha oficial. El dato de 2-oct es evidencia temporal adicional para revisar T3-2026, pero no constituye una adjudicación de versión. **Jornada D por sí sola no decide V1/V2 u otra versión histórica**. I162S2C1J4V2 se conserva como código T1 de origen. No se asignó automáticamente J1V2 al destino.

**B/E.** Para T2, O está corroborado en el respaldo congelado de julio y en agosto/septiembre; no se convierte el congelamiento 21-jul en una foto exacta del 13-jul ni se presume ausencia de cambios intermedios. Las dos observaciones de INF35-12 quedan con evidencia temporal mejorada y código destino pendiente; no con una fecha inventada.

## Otras siete personas

**B/C.** La auditoría existente cubre 58 cortes nominales del 25-ago al 21-oct-2026. Para las ocho personas del foco registra 17 cambios de campos: uno de JORNADA (INF35-12), uno de SITUACION y otros de FECHAMATRICULA/NIVEL/NOTAENSENANZAMEDIA. No se localizaron otros cambios de jornada en ese intervalo. Se verificaron hashes de los derivados y se releyeron cinco originales de esa serie más DATOSDEALUMNOS_10246: 48 filas exactas, ocho por respaldo.

**B/E.** INF35-04 figura D en DATOSDEALUMNOS_10246 y O en Base Maestra desde agosto. Son respaldos de extractores distintos: la diferencia se documenta, pero no se certifica por sí sola como fecha de cambio en UMAS ni explica sus T2/T3-2024.

**E.** Los otros doce destinos siguen sin intervalo aplicable acreditado. Para los de 2024/2025, una serie que comienza en agosto 2026 es posterior al período investigado. Para INF35-11/T2-T3-2026, los seis respaldos releídos registran O; no ubican cuándo pasó desde el contexto T1 diurno. Se mantiene la evidencia previa y no se extrapola hacia atrás.

**C.** `RESUMEN_14_OBSERVACIONES.csv` conserva las catorce filas con año, período, código T1 y pendiente. Los cambios y las 48 filas de evidencia con identificadores permanecen únicamente en el almacenamiento privado declarado en MANIFEST.json. No se crean nuevas tasas ni se clasifica a nadie como desertor.

## QA y conservación

**C.** 24.774 consultas comparadas con v2: un cambio autorizado, 24.773 idénticas salvo edición. Índice MU completo idéntico; dimensiones y documental intactos. Tres consumidores locales coinciden en 35/35 consultas; doce pruebas sintéticas correctas. Excel V12 y fuentes conservan sus hashes. QA **OK_CON_ADVERTENCIAS**, por las limitaciones temporales y de atribución descritas, no por fallos de integridad.

**D/C.** Se registraron responsable Alexi, autorización, fecha/hora, alerta, descriptor anterior y operación antes/después. No se cambiaron bases, denominadores, fórmulas, tasas ni Excel. Rama feature/ire-2026; HEAD 80ca13a5a249a1a2bd53a699f5f73689b1f53040 antes/después. Sin commit ni push; no se afirma publicación remota ni sincronización de complementos.

**E. Reanudación:** contrastar la versión de destino de INF35-12 con evidencia personal/plan que corresponda a la jornada D del respaldo de 2-oct, conservando por separado el código de cohorte. Para el resto, localizar evidencia anterior a agosto 2026 que sea temporalmente comparable; no repetir la búsqueda de códigos T1 ya cerrados.
'''
(O/'INFORME.md').write_text(report);(O/'CHECKPOINT.md').write_text('D/C: v3_20261023_inf35_07 activa; 1 cierre nuevo INF35-07/T3-2025 J2V4. Foco 35: 15 reutilizables, 20 pendientes (14 jornada, 6 homologaciones). B: INF35-12 O→D entre respaldos 29–30 sep 2026, D confirmado 2 oct. E: versión destino aún pendiente; sin extrapolar. QA íntegro; no fuentes/denominadores/Excel modificados ni commit/push.\n')
secrets={r['persona'] for r in rs}|{r['CODCLI'] for r in rs}
for directory in [O,V]:
 for p in directory.iterdir():
  if p.is_file() and p.suffix in ['.json','.csv','.md','.txt']:assert not any(v in p.read_text() for v in secrets)
manifest={'fecha_hora':datetime.datetime.now().astimezone().isoformat(),'responsable_decision':'Alexi','edicion_activa':desc['edicion'],'descriptor':str(V/'descriptor.json'),'sha256_descriptor':sha256(V/'descriptor.json'),'fuentes_hashes':inputs,'salidas_hashes':{str(f):sha256(f) for f in list(O.iterdir())+list(V.iterdir()) if f.is_file() and f.name!='MANIFEST.json'},'privado':str(P),'privados_hashes':{f.name:sha256(f) for f in P.iterdir() if f.is_file()},'codigo_hashes':{str(f.relative_to(R)):sha256(f) for f in [R/'scripts/cerrar_inf35_07_t3_20261023.py',R/'scripts/revisar_cortes_jornadas_14_20261023.py',Path(__file__),R/'docs/ESPECIFICACION_CIERRE_INF35_07_Y_JORNADAS_14_20261023.md',R/'docs/DICCIONARIO_SIES_SEGUIMIENTO.md']},'resultados':result,'QA':qa,'originales_denominadores_modificados':False,'commit_push':False}
dump(O/'MANIFEST.json',manifest);print(json.dumps(result,ensure_ascii=False));print(O/'INFORME.md')

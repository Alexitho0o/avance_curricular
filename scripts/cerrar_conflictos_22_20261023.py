"""Empaqueta el diagnóstico local; no modifica fuentes ni adjudica versiones."""
from pathlib import Path
import json,hashlib,csv,shutil,datetime,subprocess,sqlite3,ast
R=Path(__file__).resolve().parents[1];O=R/'outputs/conflictos_22_errores_6_20261023_161400';S=R/'scripts/conflictos_22_20261023';S.mkdir(exist_ok=True)
load=lambda p:json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
inputs={'QA_IDENTIDAD_FILAS.json':'/tmp/errores6_identidad_filas_QA.json','ERRORES_6.json':'/tmp/errores6_agregado.json','CAMPOS_DA_22.json':'/tmp/da22_campos_agregado.json','IMPACTO_EXCEL_22.json':'/tmp/impacto_grupos_22/IMPACTO_EXCEL_22.json','TRAZA_FORMULAS.json':'/tmp/impacto_grupos_22/TRAZA_FORMULAS.json'}
for n,p in inputs.items():shutil.copy2(p,O/n)
scripts=['/tmp/auditar_seis.py','/tmp/perfilar_seis.py','/tmp/primarios_seis.py','/tmp/trayectorias_seis.py','/tmp/cerrar_seis.py','/tmp/da22_campos.py','/tmp/impacto_grupos_22.py','/tmp/impacto_grupos_22/extraer_formulas.py']
for p in scripts:
 assert Path(p).exists(),p
 ast.parse(Path(p).read_text());shutil.copy2(p,S/Path(p).name)
g=load(O/'GRUPOS_22_VARIABLES.json');s=load(O/'RESUMEN_VARIABLES.json');e=load(O/'ERRORES_6.json');i=load(O/'IMPACTO_EXCEL_22.json');d=load(O/'CAMPOS_DA_22.json');t=load(O/'TRAZA_FORMULAS.json');start=load(O/'INICIO.json');ii={x['grupo']:x for x in i['grupos']}
notes={
'G01':'Ingreso no separa todo: 2021 todavía contiene V1 y V2. 50 contextos documentan V1 en 2021 y V2 en 2022.',
'G02':'Perfiles diferentes: V1 continuidad 4 semestres y V3 regular 8. NIV_ACA separa E01 dentro de K3; no valida todo el grupo.',
'G03':'Años de ingreso 2015/2018 comparten versiones; un cambio anual V1→V4 observado.',
'G04':'Ingreso 2018 compartido; un cambio anual V1→V4 observado.',
'G05':'Ingreso 2018 compartido; no se localiza variable suficiente.',
'G06':'MU origen 2019 distingue V3; 2021–2024 V2. V3 continuidad 4 y V2 regular 8 semestres.',
'G07':'Ingreso 2019 V2; 2020 V1. Primer año observado de actividad también separa.',
'G08':'Ingreso 2020 compartido. Siete contextos cambian V1→V2 de 2021 a 2022; E02 conserva V1 hasta 2022.',
'G09':'V3 continuidad 4 semestres frente a V1 regular 8; ingreso 2019 compartido. Revisar atribución entre expedientes.',
'G10':'Ingresos 2024/2025 comparten versiones. E04 documenta V2→V1→V2 en 2024–2026.',
'G11':'Ingreso 2018 compartido; no se localiza variable suficiente.',
'G12':'Ingresos 2016/2018 comparten versiones; ambos perfiles regulares de 5 semestres.',
'G13':'Ingresos 2024/2025 compartidos; cuatro contextos documentan V4→V1 de 2024 a 2025.',
'G14':'Ingreso 2025 compartido; no se localiza variable suficiente.',
'G15':'MU origen 2016 distingue V2 y 2018 V1. DA asigna ingreso 2020 a todos; E05 solo homologaciones/convalidaciones.',
'G16':'Ingreso 2014 V1 y 2019 V2; la combinación de estados actuales también separa descriptivamente.',
'G17':'Ingreso 2018 compartido; no se localiza variable suficiente.',
'G18':'Ingreso 2022 compartido; CATEGORIA actual separa, sin prueba histórica. Tres contextos V1→V2 de 2022 a 2023.',
'G19':'Todos ingreso 2025; no se localiza variable suficiente.',
'G20':'Ingreso separa descriptivamente, pero no sigue orden creciente de versión: 2017/18 V1; 2015/19 V2.',
'G21':'Ingreso separa sin orden creciente: 2017 V1; 2014/19/20 V2. Estados actuales combinados también separan.',
'G22':'Ingreso 2015 V1; 2018/19 V2, separación descriptiva.'}
rows=[]
for x in g:
 v=x['variables_grupo'];z=ii[x['grupo']]
 rows.append({'grupo':x['grupo'],'ano':v['ano'],'carrera_umas':v['carrera'],'plan':v['plan'],'sede':v['sede_dimension'],'jornada':v['jornada_sies'],'codigos_y_contextos':' | '.join(f'{c}: {n}' for c,n in x['codigos_personas'].items()),'contextos_documentados':x['contextos_anuales'],'variables_separan_descriptivamente':' | '.join('+'.join(f) for f in x['variables_separan_completo']) or 'Ninguna en prueba temporal','hallazgo':notes[x['grupo']],'personas_T1_excel_misma_familia':z['T1_origenes_misma_familia'],'observaciones_T1_excel':z['T1_observaciones_misma_familia'],'pendientes_T1_excel':z['T1_observaciones_pendientes_misma_familia'],'personas_cohorte_anual_hoja9':z['hoja9_cohorte_anual_todos_estados']['personas'],'pendientes_en_grupo_universo_amplio':z['pendientes_actuales_grupo'],'clasificacion':'B/C observado; E causa o generalización pendiente'})
with (O/'TABLA_22_GRUPOS.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0],delimiter=';');w.writeheader();w.writerows(rows)
def table(headers,rr):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x).replace('|',' / ').replace('\n',' ') for x in row)+' |' for row in rr])
changes=sum(x['transiciones_mismo_contexto']['conteos'].get('version_distinta_ultima_ancla_anual',0) for x in g)
report='''# Revisión de 22 grupos conflictivos y seis errores

Proceso: correspondencia UMAS/SIES por expediente y año, con aplicación al seguimiento de retención IPSS162. Años observados de los grupos: 2019–2025. Revisión local del 23 de octubre de 2026. No cambia fuentes, bases, códigos adoptados, denominadores ni Excel.

## Resultado y alcance

**B/C:** Se reprodujeron los 22 grupos K2 y los seis errores K3_min3. Los grupos contienen 637 contextos anuales documentados, 586 personas distintas y 1.744 observaciones nativas. Son grupos con varios códigos ya conocidos; no equivalen a 22 carreras sin código. Los contextos pendientes del universo ampliado se presentan aparte en la tabla CSV y no se convierten en resueltos por esta revisión.

**B/C:** En siete grupos el ingreso MU separa todas las versiones observadas: G06, G07, G15, G16, G20, G21 y G22. El ingreso del corte DatosAlumnos lo hace en seis, excluyendo G15. El primer año observado de actividad separa solo G07 y G20; el período de ingreso no separa por sí solo ninguno. No se encontró una combinación temporal suficiente en los otros 15 grupos con los campos probados.

**B/E:** En G02, G06 y G09 las versiones tienen perfiles distintos de duración/tipo: regular de ocho semestres frente a continuidad de cuatro. Esa consulta usa el código SIES ya conocido: sirve para describir la diferencia, pero sería circular usarla para adivinar el código sin respaldo independiente del plan UMAS. G18 se separa por CATEGORIA del corte actual de DatosAlumnos; G16/G21 por combinación de categoría, vía, situación y estado actuales. No acreditan qué categoría regía históricamente.

**B/C:** Se observaron 70 contextos con versión distinta de la última evidencia anual anterior bajo el mismo contexto actual de persona, CODCLI, carrera, plan, sede y jornada. En 50 se pasa de C3/J4/V1 en 2021 a V2 en 2022. Esto obliga a conservar la dimensión temporal del diccionario. No demuestra por sí solo la fecha efectiva de una migración ni que el plan observado actualmente fuera el plan vigente entonces.

**E:** Una separación perfecta en esta muestra no es una regla general ni un cierre nuevo. Hay grupos con una sola persona minoritaria y fechas de ingreso que no ordenan las versiones de forma creciente. No se adoptó ninguna regla adicional.

## Los 22 grupos

Cada fila: B/C = distribución y cruce observados; E = causa o generalización no acreditada. Todos pertenecen a institución 162, sede 2. Los nombres UMAS/planes se conservan literalmente. La tabla completa con códigos únicos, conteos y relación con el Excel está en `TABLA_22_GRUPOS.csv`; las distribuciones exactas están en `GRUPOS_22_VARIABLES.json` y `CAMPOS_DA_22.json`.

'''
report+=table(['Grupo','Año · plan · jornada','Códigos documentados (contextos)','Qué distingue / qué falta','Clas.'],[[x['grupo'],f"{x['ano']} · {x['plan']} · J{x['jornada']}",x['codigos_y_contextos'],x['hallazgo'],'B/C; E'] for x in rows])
report+='''

## Seis errores experimentales

**B/C:** Se reprodujo el mismo conjunto de seis errores con cinco particiones que separan personas entre entrenamiento y prueba. Cada error corresponde a la única persona de su versión dentro del grupo K3. Al ocultarla, el grupo de entrenamiento solo conoce la otra versión. Una variable adicional que la aísle puede producir abstención; no aprende automáticamente su versión con el soporte mínimo de tres personas. Estos seis códigos ya estaban documentados: no son seis pendientes recuperados ni prueba de seis envíos incorrectos.

'''
report+=table(['Caso','Año · plan · jornada','Documentado → predicho (no aplicado)','Resultado','Clas.'],[[x['id'],f"{x['ano']} · {x['plan']} · J{x['jornada']}",f"{x['codigo']} → {x['pred']}",x['hallazgo'],'B/C; E causa'] for x in e['errores']])
report+='''

**B:** Los cuatro códigos procedentes de la base consolidada se contrastaron con los RAW: E01, CSV2024 fila354; E02, CSV2022 fila197; E03, CSV2022 fila666; E04, hoja granular2025 fila867. Coinciden. E05/E06 se leyeron en MAT_2020 fila887 y MAT_2021 fila349. No se detectó error de consolidación en esos cuatro códigos; tampoco se acredita por ello aceptación regulatoria o la causa de la asignación. Fuentes, hojas, filas, hashes y controles de identidad están en `ERRORES_6.json` y los archivos QA adicionales.

## Alcance concreto en el Excel

**B/C:** Se revisó `RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx`, 54 hojas, y su original individual. Los 105 grupos agregados reproducen las 4.473 filas del original. Cinco de los 22 grupos intersectan T1 del mismo año y la misma familia de carrera/sede/jornada:

'''
report+=table(['Grupo','Contexto','Personas T1','Observaciones','Pendientes de código actuales','Clas.'],[[z['grupo'],f"{z['variables']['plan']} · {z['variables']['ano']} · J{z['variables']['jornada']}",z['T1_origenes_misma_familia'],z['T1_observaciones_misma_familia'],z['T1_observaciones_pendientes_misma_familia'],'B/C'] for z in i['grupos'] if z['T1_origenes_misma_familia']]+[['Total sin duplicar','',123,304,0,'B/C']])
report+='''

**B/C:** Las 304 observaciones se distribuyen en 123 del período nativo1, 95 del2 y 86 del3: las181 del2/3 ya tienen código reutilizable. Estos períodos nativos no prueban por sí solos vigencia en la fecha exacta de un cierre. G06 tiene otras22 observaciones de personas T1 en otra familia; se conservaron separadas. En hoja9 anual aparece además G01/IETMREOL20211/J4/2022: 60 personas y224 observaciones, sin pendiente de código. No se suman personas entre años como si fueran una cohorte.

**B/C:** E04 sí pertenece a una trayectoria del Excel: cohorte2024, origen C1/J1/V2, seguida en MU2025, donde consta C1/J1/V1. Los otros cinco errores no aparecen en las cohortes analíticas revisadas de hoja9 ni en los grupos T1 de hoja20. Ninguno de los seis pertenece al T1 del mismo año del error ni a los grupos exactos de nuevos ingresos T2/T3. Se distinguió el rol de origen del rol de seguimiento anual siguiente.

**B/C:** En el diagnóstico anual, `02_COHORTE_ELEGIBILIDAD!W2` sigue tipo documental, documento, DV, año siguiente, año/semestre de origen y VIG≥1. No exige igualdad de versión, carrera o jornada. `Z2=IF(AND(Y2=1,W2>0),1,0)`. Por ello el destino V1/V2 de E04 no cambia por sí solo su indicador retenido. La versión de origen sí participa en el catálogo y elegibilidad inicial: no corresponde generalizar que la versión nunca importa.

**B/C:** El Excel V12 contiene cero fórmulas en hojas18/19/20: son agregados congelados. El original conserva178/487/63.036 fórmulas respectivamente. Hoja26 conserva1.847 fórmulas. Las hojas revisadas no consultan las nuevas hojas52–54 del diccionario. La integración actual es diagnóstica: cerrar una correspondencia no actualiza automáticamente las tasas. No se demostró un error de tasa causado por los seis errores de predicción, que nunca fueron aplicados.

**B/E, controles adicionales:** En los grupos nuevos T2/T3 se verificaron1.294 filas con sus fuentes;56 tienen año/período de ingreso literal diferente de su etiqueta de grupo heredada. Ninguna intersecta exactamente los22 grupos. La hoja18 original muestra1.471 personas paraT1-2026, mientras su tasaH11 divide por1.467 evaluables medianteR=1. Son diferencias de alcance ya existentes, conservadas sin corregir; no causadas por las versiones investigadas. Por eso esta revisión no recertifica todas las tasas ni todos los denominadores del libro.

## Decisión técnica y reanudación

**C, propuesta no aplicada:** Mantener el código individual documentado como referencia del año y expediente. Las variables temporales/perfil se usan para detectar excepciones y contrastar candidatos; no sustituyen esa referencia. Reutilizar T1 en seguimiento interno exige conservar persona, expediente y contexto, comprobando cambios de plan/jornada y fechas disponibles.

**E:** El trabajo siguiente más acotado es localizar las decisiones/transformaciones anuales de las transiciones agrupadas (especialmente las50 C3/J4 de2021→2022 y la oscilación E04 de2024→2026), en vez de volver a inferir el código de cada persona desde cero. Separadamente, la futura actualización del Excel debe conectar explícitamente el diccionario a su lógica y auditar las56 etiquetas y la población evaluable, sin alterar silenciosamente los denominadores. Ninguna de esas modificaciones se ejecutó aquí.

## Evidencia y controles

**B/C:** `MANIFEST.json` registra fuentes, hashes, archivos y scripts. `QA.json` verifica la reproducción, integridad de fuentes, denominadores conservados, ausencia de identificadores en los agregados y estado de Git. `TRAZA_FORMULAS.json` conserva las fórmulas observadas y las celdas exactas. `CHECKPOINT.md` deja el punto de reanudación. Los scripts se conservan bajo `scripts/conflictos_22_20261023/`, junto a los scripts principal y de cierre. Sin commit, push ni cambios al canon.
'''
(O/'INFORME.md').write_text(report)
(S/'README.md').write_text('''# Reproducción local de la auditoría

C: ejecutar desde avance_curricular con Python y openpyxl. Son lectores de fuentes privadas locales; no subirlas. El diccionario y las fuentes se abren en solo lectura. No cambia el Excel ni adopta códigos. Se conserva la ejecución del23-oct-2026; no es motor productivo.

Orden: `scripts/analizar_conflictos_22_20261023.py`; luego en esta carpeta `auditar_seis.py`, `perfilar_seis.py`, `primarios_seis.py`, `trayectorias_seis.py`, `cerrar_seis.py`, `da22_campos.py`, `impacto_grupos_22.py`, `extraer_formulas.py`; finalmente `scripts/cerrar_conflictos_22_20261023.py`.

Los intermedios agregados usan /tmp; el detalle individual usa /Users/alexi/.local/share/ipss/analisis_conflictos_22_20261023, fuera de Git. El cierre copia solo resultados sin identificadores a outputs/conflictos_22_errores_6_20261023_161400. Los localizadores privados y originales deben existir para una reproducción completa; Git no contiene esas bases. La lectura de perfiles comprueba fuentes/identidad; los localizadores de PROMEDIOS proceden del diccionario congelado y no equivalen a una relectura completa de ese archivo.

La prueba K3 divide por persona en cinco particiones. Las pruebas de nuevas variables son descriptivas: no se reentrenó ni se aprobó una regla nueva. Para otra versión del diccionario se requiere una ejecución nueva, no sobreescribir esta evidencia.
''')
# Fuentes verificadas: suma catálogo usado, base activa y archivos efectivamente contrastados.
refs={}
def add(p,expected=None,uso='Fuente leída durante la revisión'):
 p=Path(p);h=sha(p);assert expected is None or h==expected,(str(p),'hash distinto')
 refs[str(p)]={'ruta':str(p),'sha256':h,'uso':uso}
for x in e['fuentes']:add(x['ruta_actual'],x['sha256'],x.get('uso','Fuente releída para los seis errores'))
for x in [i['excel'],i['linaje_original'],t['fuente_diagnostico'],*i['fuentes_nuevos_ingresos'].values()]:add(x['ruta'],x['sha256'])
db=Path('/Users/alexi/.local/share/ipss/cierre_inf35_03_t3_20261023_154224/DICCIONARIO_SIES.sqlite');add(db,'625b9b9d449906b38be23b7c8ad6c7f4a762f43eab9f52f0bc71fe50a5cdb38e','Diccionario privado v7 consultado, no modificado')
for p in ['data/diccionario_sies_seguimiento/activo.json','data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json','data/versiones_por_cohorte/20261016/historias_oferta.json','outputs/auditoria_metodos_puente_20261023_155309/GRUPOS_MULTICODIGO.json']:
 add(R/p,uso='Regla/catálogo o antecedente de selección del universo')
assert sha(R/'data/diccionario_sies_seguimiento/activo.json')==start['activo_sha256']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip();assert head==start['HEAD'] and branch==start['rama']
status=subprocess.check_output(['git','status','--short'],cwd=R,text=True)
assert len(g)==22 and sum(x['contextos_anuales'] for x in g)==637 and len(e['errores'])==6
assert sum(x['observaciones'] for x in g)==1744 and s['personas_distintas']==586
assert s['con_algun_discriminante_descriptivo']==7 and changes==70
assert i['resumen']['personas_T1_misma_familia_sin_duplicar_entre_grupos']==123 and i['resumen']['observaciones_T1_misma_familia_sin_duplicar']==304
assert sum(x['T1_observaciones_pendientes_misma_familia'] for x in i['grupos'])==0
assert i['linaje_original']['grupos_denominadores']=={'(2024, 1)':558,'(2025, 1)':1150,'(2026, 1)':1471,'(2025, 2)':222,'(2026, 2)':527,'(2026, 3)':545}
# Escaneo contra claves reales, sin emitirlas.
conn=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True);raw=[json.loads(x[0]) for x in conn.execute('select payload from observaciones')];conn.close()
text='\n'.join(p.read_text(encoding='utf-8-sig') for p in O.iterdir() if p.is_file() and p.name not in ['INICIO.json','MANIFEST.json','QA.json','CHECKPOINT.md'])
keys={str(r[k]) for r in raw for k in ['persona','CODCLI'] if r.get(k)}
assert all(k not in text for k in keys)
checks={'22_grupos_reproducidos':True,'637_contextos_586_personas_1744_observaciones':True,'6_errores_reproducidos':e['QA']['seis_errores_reproducidos'],'primarios_4_confirmados_y_2_historicos_leidos':e['QA']['cuatro_codigos_consolidados_reproducidos_RAW'] and e['QA']['dos_historicos_leidos_directamente'],'7_particiones_temporales_no_regla_general':True,'70_cambios_anuales_observados':True,'123_personas_304_observaciones_excel_sin_pendiente_codigo':True,'denominadores_originales_conservados':True,'fuentes_hashes_sin_cambio':True,'diccionario_activo_sin_cambio':True,'sin_identificadores_individuales_en_entrega_agregada':True,'rama_HEAD_sin_cambio':True,'nuevos_cierres':0,'commit_push':False}
for p in S.glob('*.py'):ast.parse(p.read_text())
dump('QA.json',{'clasificacion':'B/C','controles':checks,'limites':['No recertifica todas las tasas ni los cierres exactos.','Particiones descriptivas no validan causalidad ni generalización.','PROMEDIOS usa evidencia congelada y hash; no relectura completa.','56 etiquetas de grupo y alcance1471/1467 requieren revisión separada.'],'git':{'rama_antes':start['rama'],'rama_despues':branch,'HEAD_antes':start['HEAD'],'HEAD_despues':head,'status_despues':status}})
(O/'CHECKPOINT.md').write_text('''# Checkpoint — revisión22grupos/seiserrores

B/C: cuatro fases terminadas para el alcance diagnóstico: reproducción; variables y fuentes; impacto en Excel; controles/entrega. Ver INFORME.md, TABLA_22_GRUPOS.csv, ERRORES_6.json e IMPACTO_EXCEL_22.json.

D: se conserva la instrucción de no alterar bases, denominadores, diccionario o Excel. Cero cierres adoptados. Sin commit/push. La atribución documental y los cierres internos previos mantienen su estado.

E: falta acreditar las reglas de las transiciones anuales y discriminar los casos restantes con fuente independiente. Prioridad: decisiones de asignación MU por grupo/año; E04 V2→V1→V2. No exigir día exacto para reconocer un código anual documentado; sí evitar convertirlo en fecha exacta de migración.

C: antes de una futura actualización del Excel, conectar el consumidor al diccionario vigente y revisar el alcance de sus fórmulas. El libro actual conserva diagnósticos v1; la consulta de esta auditoría utiliza v7. No actualizar silenciosamente. Los controles adicionales56 etiquetas/1471 versus1467 quedan visibles sin intervención.
''')
outputs=[{'ruta':str(p),'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='MANIFEST.json']
code=[{'ruta':str(p),'sha256':sha(p)} for p in sorted(S.iterdir()) if p.is_file()]+[{'ruta':str(R/p),'sha256':sha(R/p)} for p in ['scripts/analizar_conflictos_22_20261023.py','scripts/cerrar_conflictos_22_20261023.py','docs/ESPECIFICACION_CONFLICTOS_22_ERRORES_6_20261023.md']]
dump('MANIFEST.json',{'recurso':'DIAGNOSTICO_22_GRUPOS_6_ERRORES','fecha':datetime.datetime.now().astimezone().isoformat(),'proceso':'Puente UMAS-SIES por expediente/año y alcance retención intertrimestral IPSS162','clasificacion':'B datos; C pruebas; D restricción de no modificar; E causas/generalización pendientes. No crea regla A.','fuentes':list(refs.values()),'resultados':outputs,'codigo':code,'QA':'QA.json','adopciones':0,'bases_denominadores_excel_diccionario_modificados':False,'commit_push':False,'rama':branch,'HEAD':head,'privacidad':'Agregados sin RUT/CODCLI; fuentes individuales locales no incorporadas a Git.','reproduccion':'scripts/conflictos_22_20261023/README.md'})
print(json.dumps({'output':str(O),'manifest_sha256':sha(O/'MANIFEST.json'),'informe_sha256':sha(O/'INFORME.md'),'controles':checks},ensure_ascii=False))

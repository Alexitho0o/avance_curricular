"""Close the local handoff without staging or publishing files; never export identifiers."""
from pathlib import Path
import json,hashlib,datetime,subprocess,shutil,os,collections
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
C=Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN')
O=R/'outputs/retencion_intermedia_t2_t3/20261021_153436'
P=R/'.local_restricted/retencion_intermedia/20261021_153436'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now().astimezone().isoformat()
q=json.loads((O/'QA_FINAL.json').read_text());m=json.loads((O/'MODELO_AGREGADO.json').read_text());d=json.loads((P/'datos.json').read_text())
fq=json.loads((O/'QA_FILTROS_FINAL.json').read_text());assert fq['status']=='OK' and len(fq['controls'])==164
assert sum(p[18]for p in d['persons'])==2
for sn in ['QA_COMPARABILIDAD.json','QA_TRAYECTORIA.json','QA_BLOQUES_T2_T3.json']:assert json.loads((O/sn).read_text())['status']=='OK'
for name in ['agregar_lectura_trayectoria.mjs','ajustar_privado.mjs','ajustar_comparacion.mjs','limpiar_herencia.mjs','qa_filtros_final.mjs','ver_final.mjs']:
 shutil.copy2(P/name,O/'soporte'/name)
for repo,label in [(R,'avance_curricular'),(C,'CARACTERIZACION')]:
 result={k:subprocess.check_output(['git',*cmd],cwd=repo,text=True).strip()for k,cmd in {'branch':['branch','--show-current'],'HEAD':['rev-parse','HEAD'],'status':['status','--short'],'remote':['remote','get-url','origin']}.items()}
 dump(O/'soporte'/('git_despues_'+label+'.json'),result)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()=='80ca13a5a249a1a2bd53a699f5f73689b1f53040'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=C,text=True).strip()=='aba337784ccde0537fc21b2977b351170ed335e8'
assert subprocess.run(['git','check-ignore','-q',q['private']['path']],cwd=R).returncode==0
assert not subprocess.check_output(['git','ls-files','--',str(P)],cwd=R,text=True).strip()
for k in ['public','private']:assert sha(q[k]['path'])==q[k]['sha256']
assert sha(q['public']['desktop'])==q['public']['sha256']
extra=[]
for role,path in [
 ('C: selección anual aprobada',R/'outputs/retencion_intermedia_t2_t3/20261020_215248/profile.py'),
 ('B/C: correspondencias exactas previas; privado',R/'.local_restricted/retencion_intermedia/20261021_144031/payload.json'),
 ('B/C: ejercicio Escenario_80 anterior, conservado por separado',R/'outputs/retencion_intermedia_t2_t3/20261021_100654/RETENCION_INTERMEDIA_IPSS_ESCENARIO_80_20261021_100654.xlsx'),
 ('A: transcripción de regla SIES anual',R/'procesos/caracterizacion/gobernanza/sies/RETENCION/REGLA_RETENCION_1ER_ANIO_CORREO_20260909.txt')]:
 assert path.exists(),str(path)
 extra.append({'clasificacion':role,'path':str(path),'sha256':sha(path)})
bridge=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx')
assert bridge.exists()
extra.append({'clasificacion':'B/C: fuente primaria de correspondencia explícita; consumo mediante evidencia privada previa','path':str(bridge),'sheet':'2025_carga','columns':'J RUT; BU N_DOC; BV DV','sha256':sha(bridge)})
assert extra[2]['sha256']=='12bf04615558554a30275b4ee8c6197617e7195c059c4c87277a91c4697e719d'
closures=[{'cohort':2024,'closure':'2025-T2','denominator':558,'observed_presence':1,'VIGENTE_observed':1,'formal_rate':'Pendiente E'},
 {'cohort':2024,'closure':'2025-T3','denominator':558,'observed_presence':325,'VIGENTE_observed':317,'formal_rate':'Pendiente E'},
 {'cohort':2025,'closure':'2026-T2','denominator':1150,'observed_presence':2,'VIGENTE_observed':'Sin campo E','formal_rate':'Pendiente E'},
 {'cohort':2025,'closure':'2026-T3','denominator':1150,'observed_presence':0,'VIGENTE_observed':'No inferir ausencia de continuidad','formal_rate':'Pendiente E'}]
limitations=[
 'E: cobertura completa, fecha efectiva y estado aplicable de los cuatro cierres no acreditados por los listados parciales; no certificar tasas ni llamar desertor a quien no aparece.',
 'B/C/E: PERIODOMATRICULA es matrícula declarada, no último período cursado; 325 personas de cohorte 2024 en el cierre T3-2025 conservan mayoritariamente período 1.',
 'E: dos CODCLI pendientes dentro de 1150; las 20 personas ya forman parte del denominador. Las 18 identificadas reúnen 19 CODCLI.',
 'E: TITULADO/EGRESADO requieren programa y fecha acreditados para otra regla interna; no se cambia elegibilidad ni se equipara no retenido con deserción.',
 'B/C/E: Base Maestra nominal 21-oct-2026 tiene otro alcance que DatosAlumnos. Último respaldo cuenta únicamente ANOMATRICULA=2026 y VIGENTE (213/558; 491/1150). No acredita cierres históricos.',
 'C/E: detalle de matrícula no mide asignaturas aprobadas ni avance curricular; ninguna fecha de retiro se infiere por máximo período.',
 'C: Escenario_80 y los ejercicios 222/124 permanecen en su libro anterior, intactos y separados; no se aplican a 558/1150.',
 'C/E: recálculo y render local Artifact Tool y validación OOXML; Excel nativo no ejecutado.'
]
manifest={'recurso':'Seguimiento de cohortes IPSS 2024/2025 T1/T2/T3 usando maqueta T1 aprobada','hito':'H001-RETENCION-IPSS162','fecha':now,'resultado':'OK_CON_PENDIENTES_E',
 'clasificaciones':{'A':'Definición oficial, limitada al proceso/período de la fuente','B':'Dato observado','C':'Cálculo/implementación','D':'Decisión interna','E':'Hipótesis/pendiente'},
 'decision_d':'Usar la maqueta T1 conservando diseño, gráficos nativos y filtros; entregar agregado sin identificadores y detalle privado separado; no modificar fuentes, motor anual ni denominadores; sin commit/push.',
 'maqueta':{'path':m['template'],'sha256':m['template_sha256'],'sheets':18,'native_charts':13},'fuentes_directas_b':m['sources'],'fuentes_de_trazabilidad':extra,
 'metodo_c':{'cohortes_fijas':{'2024':558,'2025':1150},'grupos_agregados':349,'personas':1708,'observaciones_matricula':4021,
 'identidad':'Documento exacto TIPO_DOC+N_DOC+DV y correspondencias CODCLI explícitas; sin identificación aproximada. Una persona puede tener varios CODCLI/matrículas; conteo de personas sin duplicar.',
 'seguimiento':m['metric_definition'],'periodos':m['period_semantics'],'ultimo_respaldo':m['latest_snapshot'],
 'formulas':'SUMIFS de pesos por grupo; proporciones = suma numeradores / suma denominadores; nunca promedio de tasas.',
 'control_unico':'14_Vistas_Ejecutivas: C4 cohorte, H4 sector, S4 carrera dependiente de sector, L4 seguimiento. Hojas 12/13/15 conectadas. Bloques T2/T3 de 2025 conservan alcance explícito.',
 'comparacion_sies':'Referencias anuales heredadas como contexto en 16/17 y hoja5; solo comparables en T1 institucional, sin sector/carrera. Se eliminaron etiquetas y conclusiones heredadas erróneas en 4/10/12/13/15.'},
 'cuatro_cierres_b_c_e':closures,'controles_b_c':m['control'],'ultimas_matriculas_declaradas_b_c':m['last_period_counts'],
 'salidas':{'agregado':q['public'],'privado_no_publicable':q['private']},'QA_c':{'archivo':'QA_FINAL.json','filtros':'QA_FILTROS_FINAL.json','controles_filtro':164,'trayectorias':'QA_TRAYECTORIA.json','comparabilidad':'QA_COMPARABILIDAD.json','bloques':'QA_BLOQUES_T2_T3.json','limite':'No validación en Excel nativo; las vistas de Artifact muestran diferencias de render respecto a Excel aun en la plantilla original.'},
 'pendientes_e':limitations,'git':{'avance_curricular':{'branch':'feature/ire-2026','before_HEAD':q['git']['HEAD'],'after_HEAD':q['git']['HEAD']},'CARACTERIZACION':{'branch':'main','before_HEAD':'aba337784ccde0537fc21b2977b351170ed335e8','after_HEAD':'aba337784ccde0537fc21b2977b351170ed335e8'},'commits':False,'push':False,'stage':False},
 'politica_privacidad':'Agregado sin documentos, nombres, CODCLI individuales, MRUN ni fecha de nacimiento exacta. Detalle y derivados con identificadores únicamente en .local_restricted, verificado ignorado/no rastreado, directorios700/archivos600. No publicación ni cargas a servicios externos.',
 'reproduccion_c':['soporte/seguir_trayectorias.py: extracción inicial privada; luego ejecutar necesariamente conciliar_periodos.py que distingue cierre de período declarado.','soporte/conciliar_periodos.py: pertenencia exacta a listados, matrículas y último respaldo; 1708 personas sin duplicar.','soporte/adaptar_maqueta.py: plantilla de transporte sin datos personales y configuración agregada.','soporte/construir.mjs: autoría agregada y QA; su sección privada inicial agotó memoria; no ejecutar esa sección. Usar privado.mjs optimizado.','soporte/privado.mjs: detalle completo con rangos acotados por persona y grupo.','soporte/agregar_lectura_trayectoria.mjs; ajustar_privado.mjs; ajustar_comparacion.mjs; limpiar_herencia.mjs: ajustes finales trazables y controles.','soporte/qa_filtros_final.mjs: QA de filtros sin escribir el libro.','soporte/preservar_y_validar.py: transporte de celdas/cachés calculados a partes nativas de maqueta; conserva dibujos/tema y regenera cachés de gráficos; valida privacidad/tablas/fuentes/copia.','soporte/ver_final.mjs: lectura/render sin modificar el libro.'],
 'archivos_soporte':[{'path':str(p),'sha256':sha(p)}for p in sorted((O/'soporte').iterdir())if p.is_file()and p.name!='cerrar_entrega.py']}
dump(O/'MANIFEST_SEGUIMIENTO_MAQUETA_T1.json',manifest)
report=f'''# Seguimiento de cohortes IPSS — entrega {now[:10]}

D: se usó la maqueta T1 aprobada, con 18 hojas y 13 gráficos. Los originales, el motor anual, los denominadores 558/1150 y los ejercicios separados 222/124 se conservan. No hubo commit, push ni staging.

C: abra **14_Vistas_Ejecutivas**: C4 elige cohorte, L4 seguimiento, H4 sector y S4 carrera. Las hojas 12, 13 y 15 usan esa selección. Las tasas de un mismo grupo se obtienen dividiendo sumas, no promediando porcentajes de subgrupos. La hoja 5, desde fila 43, distribuye la última matrícula declarada localizada; no el último período efectivamente cursado.

|Cohorte D|Cierre|Estudiantes D|Presencia B/C|VIGENTE observado B/C|Tasa formal E|
|---|---|---:|---:|---|---|
|2024|2025-T2|558|1|1|Pendiente|
|2024|2025-T3|558|325|317|Pendiente|
|2025|2026-T2|1150|2|Sin campo de estado|Pendiente|
|2025|2026-T3|1150|0|No permite concluir continuidad|Pendiente|

B/C: T1 conserva 326/558 y 668/1150 del análisis anual. **Último respaldo** muestra matrícula declarada 2026 con estado VIGENTE en la extracción nominal del 21-oct-2026: 213 y 491, respectivamente. Este seguimiento común en 2026 tiene distinto tiempo transcurrido para ambas cohortes y no es retención de primer año T2/T3. Una matrícula antigua puede seguir VIGENTE en un respaldo posterior.

B/C: detalle privado de 1708 personas y 4021 observaciones de matrícula, con todas sus correspondencias exactas y referencias a fuente/hoja/fila. De las 20 personas examinadas, 18 tienen identidad resuelta mediante 19 CODCLI y 2 siguen pendientes dentro del denominador. No se realizan nuevos cruces aproximados. El libro privado permite filtrar persona y ver ingreso, matrículas, estados y fechas nominales por separado.

C: se sustituyeron los bloques heredados que decían SIES en 4/10/13/15 por comparación de presencias T2/T3; se corrigieron auxiliares de gráficos, notas y conclusiones que ya no correspondían. Las referencias SIES anuales de 16/17 permanecen como contexto y no generan brecha contra T2/T3.

C: QA OK con pendientes E: 164 controles de filtros; conciliación de 1708 personas; 24657 fórmulas privadas con caché; cero errores de fórmula en los dos libros; tablas nativas con encabezados coherentes; 13 gráficos con cachés nuevos; dibujos, medios y tema originales conservados; 69 fuentes directas verificadas por hash. No se abrió Excel nativo. Un control intermedio detectó encabezados duplicados y se corrigieron antes del QA final.

E: falta acreditar cobertura y estado efectivo de los cuatro cierres; dos CODCLI; fechas/programa de titulación para resolver otra elegibilidad interna. La matrícula declarada no demuestra avance curricular, último período cursado ni deserción. Las fuentes disponibles no entregan información suficiente para cerrar las tasas con certeza. No se aplica regla nueva ni el escenario80.

C: agregado: {q['public']['path']}

C: SHA-256 agregado y Escritorio: {q['public']['sha256']}

C: privado, excluido de Git: {q['private']['path']}

C: SHA-256 privado: {q['private']['sha256']}

B/C: avance_curricular, feature/ire-2026, HEAD antes/después 80ca13a5a249a1a2bd53a699f5f73689b1f53040. CARACTERIZACIÓN, main, HEAD antes/después aba337784ccde0537fc21b2977b351170ed335e8. Cambios ajenos preexistentes conservados. Archivos/hashes/fuentes completos en MANIFEST_SEGUIMIENTO_MAQUETA_T1.json.
'''
(O/'ENTREGA.md').write_text(report)
events=[(1,1,'B/C','Acceso/Git/contratos y especificación comprobados','soporte/git_antes.txt y git_despues_*.json','Sin commit/push; cambios ajenos conservados'),(1,2,'A/C/D/E','Regla anual conservada; no se redefine graduación','fuente de regla y docs/ESPECIFICACION_RETENCION_INTERMEDIA_T2_T3_20261021.md','Programa/fecha de título y regla interna de elegibilidad pendientes'),(1,3,'B/C/E','Cuatro cierres y fuentes nominales separados','MANIFEST_SEGUIMIENTO_MAQUETA_T1.json','Cobertura/estado efectivos de cierre pendientes'),(2,1,'B/C','Matrículas y CODCLI exactos, sin doble conteo','Libro privado Trayectorias/Matriculas/Fuentes','No identificación aproximada'),(2,2,'B/E','Respaldo nominal separado del cierre efectivo','Libro privado fechas y procedencia','No extrapolar estado actual al pasado'),(2,3,'B/C/E','Última matrícula declarada y observación reconstruidas','Hoja5 y libro privado','No es avance curricular ni último período cursado'),(3,1,'B/C','Reutilizadas correspondencias explícitas ya verificadas','fuente IPSS_Procesamiento y evidencia privada previa','No reconstrucción post-hoc'),(3,2,'B/E','18 personas/19 CODCLI; 2 no resueltas','Libro privado y control agregado de pendientes','No afirmar resolución de 20/20'),(3,3,'C/D','1708 personas conservadas','QA_FINAL.json','558/1150; no sumar las 20 otra vez'),(4,1,'C','Dos libros separados preservando maqueta','Libro agregado y privado','Sin aplicación de Escenario80'),(4,2,'C/E','Fórmulas, controles, privacidad y OOXML verificados','QA_FINAL.json y QA_FILTROS_FINAL.json','Sin validación nativa de Excel'),(4,3,'C','Cierre, copia y hashes persistentes','Manifiesto, ENTREGA.md y PROMPT_REANUDACION.md','Tasas formales no cerradas')]
log='# Bitácora de entrega\n\n'+ '\n'.join(f'- Fase {x}/4 · Hito {y}/3 — {cl}: {action}. Evidencia: {file}. Pendiente/límite: {pending}.'for x,y,cl,action,file,pending in events)+'\n\nC: el proceso inicial conjunto agotó memoria en la sección privada; se generó por separado con rangos de fórmulas acotados. QA final de ambos libros pasó. Un control de encabezados duplicados falló de forma intermedia y se corrigió con nombres únicos. Ningún fallo intermedio se presenta como aprobación.\n'
(O/'BITACORA.md').write_text(log)
prompt=f'''Continuar seguimiento IPSS 2024/2025 desde {O}. Leer ENTREGA.md, MANIFEST_SEGUIMIENTO_MAQUETA_T1.json y QA_FINAL.json. Verificar los hashes de ambos libros antes de modificar. Agregado compartible: {q['public']['path']}; copia idéntica Escritorio. Privado: {q['private']['path']}, únicamente bajo .local_restricted comprobado ignorado/no rastreado antes de escribir. No publicar identificadores ni usar servicios externos.\nConservar 558/1150, motor anual, originales y ejercicios 222/124. No aplicar Escenario80. No repetir identificación aproximada: 18/20 resueltas con19CODCLI,2pendientes. La presencia de cuatro listados es 1/325/2/0 y sus tasas formales están Pendientes E. Fuente nominal 21-oct2026 distinta de cierres. PERIODOMATRICULA es matrícula declarada, no último período cursado. La hoja14 controla C4/H4/S4/L4; la hoja5 fila43 muestra última matrícula declarada. No proponer nuevas reglas para graduación sin decisión y fecha/programa acreditados. No confundir ausencia con deserción.\nRecálculo Artifact Tool local y QA164, cero errores de fórmula; Excel nativo no certificado. No commit/push/stage/cambio de rama. Rama feature/ire-2026 HEAD80ca13a5a249a1a2bd53a699f5f73689b1f53040. Referencia main aba337784ccde0537fc21b2977b351170ed335e8. Conservar cambios ajenos. Clasificar A/B/C/D/E. Continuar solo el pendiente que el usuario encargue; no volver a diagnosticar lo ya acreditado ni declarar cerradas tasas pendientes.\n'''
(O/'PROMPT_REANUDACION.md').write_text(prompt)
for root,dirs,files in os.walk(P,followlinks=False):
 os.chmod(root,0o700)
 for n in files:
  pp=Path(root)/n
  if not pp.is_symlink():os.chmod(pp,0o600)
print(json.dumps({'status':'OK_CON_PENDIENTES_E','manifest':str(O/'MANIFEST_SEGUIMIENTO_MAQUETA_T1.json'),'manifest_sha256':sha(O/'MANIFEST_SEGUIMIENTO_MAQUETA_T1.json'),'public_sha256':sha(q['public']['path']),'private_sha256':sha(q['private']['path']),'no_commit_push':True},ensure_ascii=False,indent=2))

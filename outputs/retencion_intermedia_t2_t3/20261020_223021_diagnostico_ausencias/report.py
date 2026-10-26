from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
T=Path(__file__).parent
d=json.loads((T/'diagnosis.json').read_text())
repo=Path('/Users/alexi/Documents/GitHub/avance_curricular')
out=repo/'outputs/retencion_intermedia_t2_t3/20261020_223021_diagnostico_ausencias'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mdtable(headers,rows):
    clean=lambda x:str(x).replace('|',' / ').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(clean,r))+' |' for r in rows])
head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
branch=subprocess.check_output(['git','-C',str(repo),'branch','--show-current'],text=True).strip()
assert head=='b8140dcba0f179865671cff75f98b9e1041eeb0a'
for s in d['sources']:assert sha(s['path'])==s['sha256'],s['path']
book=repo/'outputs/retencion_intermedia_t2_t3/20261020_221157/CONTINUIDAD_IPSS_INGRESOS_2025_T2_T3_EN_MU2026_20261020_221157.xlsx'
assert sha(book)=='202072b117e61c53d4895d72f1dee7f92c2557a013ea3262d055de4bc28379a5'
assert d['coverage']['normalized_row_by_row_equal']
assert d['coverage']['canonical_hash_matches_inventory']
assert d['cohorts']['2025-T2']['denominator']==222
assert d['cohorts']['2025-T3']['denominator']==124
for c,x in d['cohorts'].items():
    assert sum(x['current_classification_persons'].values())==x['absent_mu']
    assert x['found_current_umas']==x['absent_mu']
    assert x['new_matches_more_permissive_format']==0
    assert x['same_body_different_dv_mu']==0
date=datetime.datetime.now().astimezone().isoformat()
rows=[['B/C','No localizados en MU2026',142,74],['B/C','Localizados por RUT exacto en UMAS actual',142,74],['B/C','Con ANOMATRICULA=2026 y ESTADOACADEMICO=VIGENTE',3,1],['B/C','Con ANOMATRICULA=2026, sin ningún VIGENTE en 2026',0,1],['B/C','Sin fila ANOMATRICULA=2026 en UMAS actual',139,72],['B/C','De los anteriores: con algún VIGENTE en una fila de 2025',106,48],['B/C','De los anteriores: sin ningún estado VIGENTE',33,24],['B/C','Recuperados por una normalización adicional del RUT',0,0]]
summary=mdtable(['Clase','Hallazgo, personas únicas','2025-T2','2025-T3'],rows)
sources=mdtable(['ID','Clase','Archivo / hoja','Ruta','SHA-256'],[[f'F{i+1}','B' if i!=7 else 'C',Path(s['path']).name+' / '+str(s.get('sheet') or 'no aplica'),s['path'],s['sha256']] for i,s in enumerate(d['sources'])])
state_rows=[]
for co,x in d['cohorts'].items():
    for st,num in x['no2026_current_state_combinations_persons'].items():state_rows.append(['B/C',co,st,num])
report=f'''# Diagnóstico de ausencias MU2026 — ingresos 2025-T2/T3

## Objetivo

- **D:** revisar por qué 142 personas de T2 y 74 de T3 no aparecen en matrícula unificada 2026, sin cambiar los denominadores autorizados de 222 y 124 ni modificar el libro entregado.
- **C:** proceso de seguimiento institucional de continuidad IPSS; cohorte operacional ANOINGRESO=2025 / PERIODOINGRESO=2 o 3. Observación MU2026 y contraste con extracto UMAS entregado el 20-10-2026. No se confunde con una nueva estimación de retención anual oficial SIES.
- **C:** hito de referencia H001-RETENCION-IPSS162; repositorio avance_curricular, rama `{branch}`; fecha de revisión {date}.

## Resultado principal

- **B/C:** no se detectó una falla de formato del RUT: las 346 personas de origen tienen identificadores válidos; no se recupera ninguno de los 216 ausentes al ampliar la normalización. Tampoco existe en MU2026 el mismo cuerpo numérico con otro dígito verificador para esos 216.
- **B/C:** no se detectó pérdida en la consolidación: las 4.105 filas × 32 columnas del archivo rector original se reproducen exactamente, después de aplicar la normalización documentada del constructor, en la porción 2026 de BASE_RETENCION_MU. Los 216 tampoco aparecen al buscar directamente en el original rector.
- **B:** el extracto UMAS actualizado sí contiene a los 216. Solo cinco tienen alguna fila que declara ANOMATRICULA=2026; cuatro de esos cinco figuran VIGENTE y uno solo ELIMINADO en 2026. Hay una diferencia de cobertura observable entre fuentes para esas cinco personas.
- **E:** no se puede atribuir automáticamente esa diferencia a un error de envío, una omisión o una baja. Son fotografías y alcances distintos y no está acreditada la fecha efectiva de vigencia del archivo rector.
- **B/E:** de las otras 211 personas, 154 tienen VIGENTE asociado a una fila ANOMATRICULA=2025. No se puede convertir ese estado en una matrícula 2026; tampoco prueba deserción. La causa de las tasas bajas sigue parcialmente sin explicación.

## Conteos conciliados

{summary}

**C:** las dos filas «De los anteriores» desglosan las 139/72 personas sin matrícula 2026; no deben sumarse nuevamente al total. Las categorías 3+0+139=142 y 1+1+72=74 son excluyentes. No hay personas compartidas entre las dos cohortes.

## Pruebas del identificador

- **C:** llave institucional RUT completo del archivo T2/T3 ↔ N_DOC+DV, con TIPO_DOC=R, en MU2026. Se normalizan mayúsculas, espacios, puntos y ceros iniciales. Se verifica el dígito módulo 11, sin usar nombre, sexo ni fecha de nacimiento.
- **B/C:** origen: 222 y 124 RUT únicos, todos válidos. MU2026: 4.105 registros con TIPO_DOC=R y cero llaves inválidas. UMAS nuevo: 15.136 registros, 13.011 RUT distintos válidos, cero RUT no interpretables y cero DV inválidos. Son registros históricos, no 15.136 estudiantes actuales.
- **C:** prueba adicional: eliminar separadores no alfanuméricos y contrastar cuerpos numéricos para detectar diferencias de DV. Recuperaciones: 0/142 y 0/74. Las 216 coincidencias con UMAS nuevo ya se logran con la normalización original.
- **E:** estas pruebas descartan problemas de representación observables; no certifican que nunca exista un identificador incorrecto pero formalmente válido en los sistemas.

## Integridad y cobertura de matrícula unificada

- **B:** F1 es la consolidación gobernada utilizada; su hash coincide con F6. F5 es su fuente rector original, hoja CONSOLIDADO, 4.105 filas. Su hash actual coincide con el inventario F7: `{d['coverage']['canonical_sha256']}`.
- **C:** se lee el constructor F8 sin ejecutar `main`, y se aplica su función `typed_value` a las 32 columnas del archivo rector. La comparación respeta orden de fila y columna; no compara solo dimensiones.
- **B/C:** celdas discrepantes: 0; filas omitidas: 0; coincidencias nuevas de los ausentes buscadas directamente en F5: 0 para T2 y 0 para T3.
- **C:** hash de contenido normalizado del original y de las filas 2026 de la base: `{d['coverage']['normalized_base_content_hash']}` en ambos. Este hash de contenido es distinto del hash binario de cada XLSX.
- **B:** F2 declara 5.613 filas ANOMATRICULA=2026, distribuidas en período 1=4.199, período 2=812 y período 3=602. F2 también contiene registros 2013–2027. No es una copia del universo de 4.105 filas de F1/F5.
- **E:** estos totales tienen fechas y alcances diferentes; su resta no se interpreta como matrícula omitida ni como error. El nombre REPORTE JULIO 2026 no certifica por sí solo un corte al 30 de abril ni su cobertura completa de períodos posteriores.

## Cinco personas con matrícula 2026 ausentes en MU2026

{mdtable(['Clase','Cohorte','Personas','PERIODOMATRICULA','ESTADOACADEMICO de filas 2026','FECHAMATRICULA observada'],[['B','2025-T2',3,2,'VIGENTE','20-05-2026; 01-07-2026; 08-07-2026'],['B','2025-T3',1,3,'VIGENTE','12-09-2026'],['B','2025-T3',1,1,'ELIMINADO (dos registros)','No utilizada para atribuir causa']])}

- **B:** para T2 son tres personas y tres filas. Para T3 son dos personas y tres filas: dos filas ELIMINADO de una misma persona y una fila VIGENTE de otra.
- **B/E:** la fecha 12-09-2026 es posterior a la corrida de consolidación 01-09-2026. Es compatible con una diferencia temporal, pero no acredita por sí sola la regla del corte ni la causa de las otras ausencias.
- **D:** no se incorporan estas personas al numerador anterior: mezclar estados actuales de UMAS con una fotografía MU anterior produciría otro indicador. El usuario pidió revisar, no cambiar los denominadores o las fuentes del cálculo.

## Personas sin registro de matrícula 2026 en UMAS nuevo

{mdtable(['Clase','Cohorte','Combinación de estados encontrada para la persona','Personas'],state_rows)}

- **B:** 106 personas T2 y 48 T3 tienen al menos una fila VIGENTE, todas esas filas con ANOMATRICULA=2025. Las combinaciones de estados preservan las situaciones de distintas filas/carreras de la misma persona; no se elige arbitrariamente un estado preferente.
- **E:** falta evidencia que aclare si esas 154 personas renovaron matrícula 2026, si ANOMATRICULA en esta extracción conserva un año anterior, o si el estado académico no acredita matrícula anual activa. No se puede resolver esa semántica con el nombre del archivo «actualizado».
- **B/E:** los estados ELIMINADO/SUSPENDIDO se observan como valores del extracto; sin fecha efectiva ni historia de cambios no se atribuyen a una baja ocurrida antes del corte SIES.

## Alcance mantenido y cifras no modificadas

- **D:** T2=222, T3=124, incluidos ELIMINADO. No se incorporan los 68 ingresos T2 adicionales encontrados en el archivo posterior T3.
- **C:** el libro conserva 74/222=33,3% y 48/124=38,7%, como continuidad observada en la fuente MU2026 seleccionada; se confirman los conteos, no una explicación causal de la no presencia.
- **C:** búsqueda por identidad en cualquier carrera/jornada de IPSS; no se fuerza igualdad de carrera, año de origen o semestre para este seguimiento. Se mantienen los pendientes de cohorte/carrera del libro anterior.
- **E:** no corresponde afirmar que 142 o 74 desertaron. «Ausente de MU2026» es el resultado comprobado; «deserción» no se ha demostrado.

## Fuentes y evidencia

{sources}

**C:** para F3/F4 se filtra ANOINGRESO=2025 y PERIODOINGRESO=2/3 respectivamente. En F1 se filtra ANIO_INFORMADO=2026; campos TIPO_DOC, N_DOC, DV y VIG. En F2 se usan RUT, ANOMATRICULA, PERIODOMATRICULA, ESTADOACADEMICO, SITUACION y FECHAMATRICULA. Las hojas y hashes precedentes permiten repetir cada número. No se exportan identificadores de estudiantes.

## Validaciones, estado y próximo paso

- **C:** hashes originales intactos; denominadores 222/124 y ausencias 142/74 reproducidos; identidades válidas; conteos de categorías cierran; coincidencia de 4.105 filas × 32 columnas; cero pérdida de consolidación observada.
- **C:** libro anterior intacto: `{book}`; SHA-256 `{sha(book)}`.
- **C:** rama antes/después `{branch}`, HEAD antes/después `{head}`. Se crean solo este diagnóstico, resultados agregados, script y manifiesto en una carpeta derivada nueva. Sin commit ni push.
- **E:** falta resolver la relación entre estado VIGENTE y año de matrícula para las 154 personas con fila VIGENTE 2025, y la cobertura/fecha efectiva del corte para las cinco con matrícula 2026 fuera de MU. No se declara cerrada la explicación completa de las tasas.
- **C:** próxima comprobación pertinente: historial de renovaciones/matrículas 2026 por persona, período y fecha efectiva, y especificación de los campos de DATOSDEALUMNOS. No hace falta rehacer la normalización del RUT ni reconstruir la base consolidada para resolver ese vacío.
'''
p=out/'DIAGNOSTICO_AUSENCIAS_MU2026_20261020.md';p.write_text(report)
aggregate={k:v for k,v in d.items() if k!='detail_pseudonymous'}
q=out/'RESULTADOS_AGREGADOS.json';q.write_text(json.dumps(aggregate,ensure_ascii=False,indent=2))
shutil.copy2(T/'diagnose.py',out/'diagnose.py');shutil.copy2(T/'report.py',out/'report.py')
manifest={'fecha':date,'proceso':'Seguimiento institucional continuidad IPSS 2025-T2/T3 en MU2026','decision_D':'Mantener 222/124 y libro original; analizar 142/74 ausentes con UMAS nuevo','fuentes':d['sources'],'salidas':[{'path':str(f),'sha256':sha(f)} for f in [p,q,out/'diagnose.py',out/'report.py']],'qa':'OK: formato, hashes, comparación 4105x32, controles personas; interpretación causal sigue pendiente E','git':{'branch_before':branch,'branch_after':branch,'head_before':head,'head_after':head,'commit':False,'push':False},'proteccion':'Solo resultados agregados y código en carpeta derivada. Llaves reales solo en memoria; intermedio temporal usa seudónimos, sin nombres/RUT/fecha de nacimiento.'}
(out/'MANIFEST_DIAGNOSTICO.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'report':str(p),'sha256':sha(p),'git':manifest['git']},ensure_ascii=False))

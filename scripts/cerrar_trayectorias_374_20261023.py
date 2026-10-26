"""Contrasta y documenta las trayectorias; no adopta las propuestas de fecha."""
import json,csv,hashlib,sys,datetime,subprocess,itertools,re
import openpyxl
from pathlib import Path
from collections import defaultdict,Counter
O=Path(sys.argv[1]).resolve();R=Path(__file__).resolve().parents[1];M=json.load(open(O/'MANIFEST.json'));P=Path(M['privado'])
load=lambda p:json.load(open(p));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,default=str))
def csvout(p,rs):
 if not rs:return
 fields=list(dict.fromkeys(k for r in rs for k in r))
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fields,delimiter=';');w.writeheader()
  for r in rs:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list,tuple)) else v for k,v in r.items()})
obs=load(P/'OBSERVACIONES_REVISADAS.json');rels=load(P/'RELACIONES_PERSONA_FAMILIA.json');segments=load(P/'SEGMENTOS_EXPEDIENTE_PLAN.json');pairs=load(P/'PARES_TRAYECTORIA.json');S=load(O/'RESULTADOS.json')
base=load(Path('/Users/alexi/.local/share/ipss/reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json'));b={x['observacion_id']:x for x in base}
people=defaultdict(list)
for x in obs:people[x['persona']].append(x)
parts=Counter('SIN_PENDIENTES_ANUALES' if all(x['codigo_documental_atribuible'] for x in rr) else 'PARCIAL' if any(x['codigo_documental_atribuible'] for x in rr) else 'NINGUNA_OBSERVACION_ATRIBUIDA' for rr in people.values())
assert sum(parts.values())==374
assert len(obs)==3320 and len({x['observacion_id'] for x in obs})==3320
assert all(x['codigo_documental_atribuible']==b[x['observacion_id']]['codigo_documental_atribuible'] and x['codigo_interno_adoptado']==b[x['observacion_id']]['codigo_interno_adoptado'] for x in obs)
assert len(rels)==377 and len({(x['persona'],x['familia']) for x in rels})==377
# Explicit before/after annual changes, retaining original source localizers.
changes=[]
prior_evidence=next(x['rows'] for x in load(Path('/Users/alexi/.local/share/ipss/reproduccion_puente_20261023_004044/reanudacion/antecedentes_minimos.json')) if x['name']=='EVIDENCIAS_SIES')
for rel in rels:
 ys=sorted((int(y),cs) for y,cs in rel['codigos_por_ano'].items() if cs)
 for (y,a),(yy,bb) in zip(ys,ys[1:]):
  if a==bb:continue
  matching=[x for x in obs if x['persona']==rel['persona'] and rel['familia'] in x['familias']]
  ev=[m for x in matching for m in x['evidencias_MU'] if int(m['ano']) in [y,yy] and m['familia']==rel['familia']]
  # Years may precede activity in the observation universe; preserve source references from the full prior registry.
  for x in base:
   if x['persona']==rel['persona']:
    ev.extend(dict(m,familia=m['codigo'].rsplit('V',1)[0],ano=m['anio']) for m in x['evidencias_matricula'] if m['codigo'].rsplit('V',1)[0]==rel['familia'] and int(m['anio']) in [y,yy])
  uniq={ (m.get('archivo',m.get('fuente')),m['hoja'],m['fila']):m for m in ev}
  # Recover localizers for years outside the academic-observation window.
  for target_year,target_codes in [(y,a),(yy,bb)]:
   if any(int(m.get('ano',m.get('anio',0)))==target_year for m in uniq.values()):continue
   candidates=[r for r in prior_evidence if r[0]==rel['persona'] and r[1]=='MATRICULA' and str(r[2]).replace('MAT_','')==str(target_year) and r[3] in target_codes and 'MAT_IP_CIISA_' in r[8]]
   assert candidates, 'Missing primary localizer for annual transition'
   for r in candidates:
    assert sha(r[8])==M['fuentes'][r[8]]
    wb=openpyxl.load_workbook(r[8],read_only=True,data_only=True);ws=wb[r[9]]
    header=next(ws.values);values=next(ws.iter_rows(min_row=int(r[10]),max_row=int(r[10]),values_only=True));d=dict(zip(header,values));wb.close()
    identity=str(int(d['MM_N_DOCUMENTO']))+'-'+str(d['MM_DV']).strip().upper()
    assert identity==rel['persona'] and str(d['MC_CODIGO_UNICO'])==r[3] and int(str(d['MC_CAT_PERIODO']).replace('MAT_',''))==target_year
    uniq[r[8],r[9],r[10]]={'persona':identity,'ano':target_year,'codigo':r[3],'familia':rel['familia'],'archivo':r[8],'hoja':r[9],'fila':r[10],'sha256':sha(r[8]),'verificado_fila_original':True}
  assert {y,yy} <= {int(m.get('ano',m.get('anio',0))) for m in uniq.values()}
  changes.append({'persona':rel['persona'],'familia':rel['familia'],'ultimo_ano_codigo_anterior':y,'codigo_anterior':a,'primer_ano_codigo_siguiente':yy,'codigo_siguiente':bb,
   'cruza_limite_publicado_derivado':y<=2021<yy,'anos_sin_observacion_intermedios':list(range(y+1,yy)),
   'evidencias':list(uniq.values()),'fecha_efectiva_cambio':'PENDIENTE','clasificacion':'B/C cambio de código observado entre archivos anuales; E causa y fecha efectiva'})
dump(P/'CAMBIOS_VERSION_ANUAL.json',changes);csvout(P/'CAMBIOS_VERSION_ANUAL.csv',changes)
dated=[x for x in obs if x['candidatos_por_fecha_exclusiva']];newdate=[x for x in dated if not x['codigo_documental_atribuible']]
same=[x for x in dated if x['codigo_documental_atribuible']]
date_qa={'observaciones_referencia':len(same),'personas_referencia':len({x['persona'] for x in same}),
 'matriculas_MU_referencia':len({tuple(m['MU']) for x in same for m in x['coincidencias_fecha'] if m['expedientes_con_misma_fecha']==1}),
 'concordantes':sum(x['candidatos_por_fecha_exclusiva']==[x['codigo_documental_atribuible']] for x in same),
 'nuevas_observaciones_con_pista':len(newdate),'personas_nuevas_pista':len({x['persona'] for x in newdate}),
 'limite':'Observaciones correlacionadas por persona y fuente; fecha de matrícula/renovación no prueba asignación ni vigencia histórica del plan. No regla nueva adoptada.'}
dump(P/'CUATRO_PISTAS_FECHA.json',newdate);csvout(P/'CUATRO_PISTAS_FECHA.csv',newdate)
csvout(O/'PISTAS_FECHA_AGREGADAS.csv',[{'carrera':c,'ano':y,'codigo':co,'observaciones':n,'estado':'C coincidencia documental exacta de fecha; E aplicación al período/plan'} for (c,y,co),n in Counter((x['carrera'],x['ano'],';'.join(x['candidatos_por_fecha_exclusiva'])) for x in newdate).items()])
ca=Counter((x['familia'],';'.join(x['codigo_anterior']),';'.join(x['codigo_siguiente']),x['ultimo_ano_codigo_anterior'],x['primer_ano_codigo_siguiente']) for x in changes)
csvout(O/'CAMBIOS_VERSION_ANUAL_AGREGADOS.csv',[{'familia':f,'codigo_anterior':a,'codigo_siguiente':b,'ultimo_ano_anterior':y,'primer_ano_siguiente':yy,'personas':n,'clasificacion':'B/C; E fecha efectiva'} for (f,a,b,y,yy),n in sorted(ca.items())])
assignment=Counter((x['carrera'],x['jornada_sies'],x['plan'],x['ano'],x['periodo'],x['codigo_documental_atribuible'],x['estado_revision']) for x in obs)
csvout(O/'VERSIONES_POR_PERIODO_AGREGADAS.csv',[{'carrera':c,'jornada':j,'plan_observado':p,'ano_actividad':y,'periodo_UMAS':t,'codigo_documentado_anual':co,'estado':st,'observaciones':n,'alcance':'No certifica asignación efectiva del plan al período'} for (c,j,p,y,t,co,st),n in sorted(assignment.items())])
patterns=[]
for x in pairs:
 ss=[s for s in segments if s['persona']==x['persona'] and s['familia']==x['familia'] and [s['CODCLI'],s['carrera'],s['plan']] in [x['expediente_a'],x['expediente_b']]]
 regimes=tuple(sorted({r for s in ss for r in s['regimenes']}))
 patterns.append((x['estado'],regimes))
S.update(personas_por_estado=dict(parts),comparacion_fecha=date_qa,cambios_version={'relaciones':len(changes),'personas':len({x['persona'] for x in changes}),
 'cruzan_fuentes_historicas_y_base_derivada':sum(x['cruza_limite_publicado_derivado'] for x in changes),
 'mismo_tramo_base_2022_2026':sum(x['ultimo_ano_codigo_anterior']>=2022 for x in changes)})
dump(O/'RESULTADOS.json',S)
assert len(changes)==12 and len(newdate)==4
assert all(sha(p)==h for p,h in M['fuentes'].items())
qa={'estado':'OK_CON_PENDIENTES','foco_personas':374,'relaciones':377,'observaciones':3320,'expedientes_planes':756,'pares':381,
 'duplicados_observacion':len(obs)-len({x['observacion_id'] for x in obs}),'codigos_adoptados_cambiados':sum(x['codigo_interno_adoptado']!=b[x['observacion_id']]['codigo_interno_adoptado'] for x in obs),
 'reproduccion_codigos_anuales':True,'fuentes_conservadas':True,'denominadores_globales':[5901,6622,24774],
 'distribuciones_cierran':sum(S['observaciones_por_estado'].values())==3320 and sum(S['versiones_por_relacion'].values())==377 and sum(S['patrones_pares'].values())==381,
 'privado_fuera_git':subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0,
 'limites':['Sin corte efectivo de extracción acreditado para los reportes UMAS','Códigos de MU documentados anualmente, no automáticamente por trimestre','Sin acto/fecha efectiva de migración o asignación de plan','No adopción de las cuatro pistas de fecha']}
assert qa['distribuciones_cierran'] and qa['privado_fuera_git'] and qa['codigos_adoptados_cambiados']==0
dump(O/'QA_FINAL.json',qa)
famrows=list(csv.DictReader(open(O/'RESUMEN_POR_FAMILIA.csv',encoding='utf-8-sig'),delimiter=';'))
table='\n'.join('| '+ ' | '.join([x['familia'],x['personas_en_familia'],x.get('UN_CODIGO_EN_ANIOS_OBSERVADOS') or '0',x.get('CAMBIO_CODIGO_ENTRE_ANIOS_OBSERVADOS') or '0',x.get('SIN_CODIGO_MU_LOCALIZADO') or '0'])+' |' for x in famrows)
report=f'''# Fechas y versiones de las 374 personas — revisión dirigida

**B/C.** Se revisaron las 374 personas y 377 relaciones persona–familia de la entrega anterior. El foco contiene 3.320 observaciones del universo fijo de 24.774; 3.162 pertenecen a las relaciones múltiples seleccionadas y 158 corresponden a otros contextos de las mismas personas. No se cambiaron bases, códigos adoptados, reglas ni denominadores. No hubo commit/push.

## Qué versión se puede confirmar

| Estado de las observaciones del foco | Cantidad | Alcance |
|---|---:|---|
| Código MU anual atribuible al expediente | 2.942 | B/C: código anual documentado; no prueba automáticamente cada trimestre de plan |
| Código anual único, expediente todavía ambiguo | 83 | B código; E atribución |
| Sin código anual localizado | 295 | E; no equivale a ausencia universal |
| Total | 3.320 | C |

Por persona (categorías excluyentes): **251** tienen todas sus observaciones con código anual atribuible, **116** están parcialmente cubiertas y **7** no tienen observación atribuida. Total 374. No son nuevos cierres: reproducen el estado documental anterior dentro del foco. Los indicadores globales siguen en 1.838 personas pendientes documentales y 1.751 internas. La temporalidad efectiva del plan es una pregunta adicional, no una redefinición de esos indicadores.

**B/C.** En las 377 relaciones: 360 muestran un código único a través de los años documentados, 12 un cambio entre años y cinco no tienen código MU localizado. Ninguna muestra dos códigos distintos en el mismo año dentro de la evidencia MU revisada. Una persona aparece en más de una familia en tres relaciones adicionales; no sumar familias como personas únicas.

| Familia SIES | Personas en familia | Un código observado | Cambio entre años | Sin código |
|---|---:|---:|---:|---:|
{table}

El archivo VERSIONES_POR_PERIODO_AGREGADAS.csv muestra carrera, jornada, etiqueta de plan, año/período UMAS y código **anual** documentado, sin identificadores. El registro privado conserva los localizadores de las filas fuente y el estado de cada observación. No se rellena un código anual ausente con el de otro año.

## Fechas y cambios de plan

**B/C.** Se reconstruyeron 756 combinaciones expediente–plan dentro de las relaciones y 381 pares. Hay 357 pares con años de actividad disjuntos; 20 coinciden en un año pero usan regímenes no comparables; dos comparten períodos del mismo régimen; dos tienen períodos distintos dentro del mismo año y régimen. Los dos solapamientos persisten al separar convalidaciones/homologaciones. «Sin marca de reconocimiento» describe el reporte, no acredita asistencia o matrícula vigente.

**B.** Los segmentos contienen 369 regímenes bimestrales, 368 trimestrales y 19 semestrales. No se equipara período 1 bimestral con trimestre 1, ni período UMAS con semestre SIES sin una regla documentada. **E:** secuencia observada o ausencia de solapamiento no prueba la fecha efectiva de migración.

**B/C.** Se compararon 7.930 unidades de asignatura/año/período/expediente presentes tanto en PROMEDIOS 7804 como en 12166: las 7.930 mantienen el mismo conjunto de etiquetas de plan. Se leyeron 17.599 y 8.109 filas de asignaturas del foco, respectivamente; diferencia de cobertura no se interpreta como bajas. Esta comparación no revela cambios de etiqueta entre esos reportes, pero tampoco demuestra que nunca hubiese un cambio previo o que la etiqueta corresponda históricamente a cada nota.

**B.** En 752 de los 756 segmentos se encuentran contextos concordantes en los tres DATOSDEALUMNOS; cuatro no tienen contexto exacto de expediente/carrera/sede/jornada localizado. Entre los contextos disponibles no se encontraron diferencias en ANOINGRESO, PERIODOINGRESO, FECHAMATRICULA, ANOMATRICULA ni PERIODOMATRICULA. Sus cortes efectivos de extracción no están acreditados, por lo que no se ordenan como una secuencia fechada solo por el nombre del archivo.

**B.** La matrícula MU del foco tiene 1.255 filas: 777 con fecha de matrícula interpretable y ninguna fecha no vacía pendiente de interpretación. Los años históricos y 2022–2023 carecen de ese campo en las fuentes leídas. Fecha de matrícula/renovación, fecha de firma, ingreso declarado, actividad académica y asignación efectiva de plan se mantienen separados.

## Las 12 trayectorias donde cambia el código

**B/C.** Los cambios se conservan con último año observado del código anterior, primer año observado del siguiente y años intermedios sin evidencia. Diez cruzan el tramo de fuentes históricas publicadas hasta 2021 frente a la base derivada desde 2022; dos ocurren dentro de la base 2022–2026. Esto describe procedencia, no demuestra que el cambio se deba a la fuente ni que sea un error.

El detalle agregado está en CAMBIOS_VERSION_ANUAL_AGREGADOS.csv; CAMBIOS_VERSION_ANUAL.json/CSV privado identifica cada trayectoria y conserva sus evidencias. **E:** el intervalo entre dos observaciones no es una fecha efectiva de cambio. No se renumera V1/V2/V3 ni se traslada el código posterior hacia atrás.

## Cuatro pistas adicionales de atribución por fecha

**B/C.** Cuatro observaciones de cuatro personas, antes ambiguas entre expedientes de la misma familia, tienen una fecha de matrícula MU que coincide exclusivamente con un expediente en los tres DATOSDEALUMNOS:

| Carrera interna | Año | Código MU coincidente | Observaciones |
|---|---:|---|---:|
| IECIREOL | 2024 | I162S2C1J4V2 | 2 |
| TPAREOL | 2024 | I162S2C57J4V1 | 2 |

Las fechas, filas y alternativas están en CUATRO_PISTAS_FECHA.csv privado. La coincidencia respalda qué matrícula interna puede estar asociada a la fila MU; **no acredita la vigencia del plan en todas las actividades de ese año**. Esos casos tienen también expedientes IINF o TPAS con régimen trimestral; los expedientes coincidentes son bimestrales. No se fuerza una correspondencia entre sus períodos.

**C. Control:** la coincidencia de fecha exclusiva también aparece en {date_qa['observaciones_referencia']} observaciones ya atribuibles, correspondientes a {date_qa['personas_referencia']} personas y {date_qa['matriculas_MU_referencia']} filas MU. Todas concuerdan con su código documentado. No son 185 pruebas independientes: se repiten personas y fuentes. **E/D:** usar esta pista como regla nueva de cierre requiere formalizar su alcance; aquí se registra, no se adopta ni cambia el estado vigente.

## Fuentes, recuperación y evidencia faltante

Se utilizaron PROMEDIOS 12166 y el respaldo idéntico del 7804, DATOSDEALUMNOS 12159/11248 y respaldo del 11998, matrícula histórica MAT 2010–2021, BASE_RETENCION_MU 2022–2026, mapas de familias vigentes y la documentación de planes/temporalidad. Se preservan fuente/hoja/fila y hashes.

**B.** PROMEDIOS 7804 en Descargas tiene hash distinto al manifiesto; DATOSDEALUMNOS 11998 ya no está en esa ruta. Se recuperaron ambos desde el respaldo Caracterizacion_anual_2026_20261015_130336_379868, con hashes exactamente iguales a los gobernados. RELOCALIZACION_FUENTES.json documenta las sustituciones de ubicación, sin alterar ni reemplazar los originales.

**E.** Falta evidencia con CODCLI/carrera/plan anterior/nuevo y fecha efectiva (o matrícula/plan/período con esa semántica acreditada), además del linaje de PLAN_DE_ESTUDIO del reporte. La documentación gobernada identifica RA_CARGA_RASTRO y registro de asignaturas como candidatos, pero no acredita que los extractos disponibles contengan esa historia. La búsqueda dirigida por nombres en los repositorios, Descargas y Escritorio no localizó un extracto identificado de esos eventos; no se afirma inexistencia universal. No se completa el vacío con el sufijo del plan ni con totales.

## QA y preservación

Distribuciones: 360+12+5=377; 2.942+83+295=3.320; 251+116+7=374; 357+20+2+2=381. Todas las observaciones conservan los códigos documentales e internos anteriores; cero duplicaciones por unión. Hashes de fuentes conservados, Git sin cambio de rama o HEAD. El detalle individual permanece fuera de Git en {P}; el repositorio solo contiene código, documentación y agregados.

No se modificó ningún Excel anterior ni sus gráficos, tablas, tasas o denominadores. Esta entrega es un diagnóstico dirigido con CSV/JSON reproducibles. No confundir QA técnico correcto con cierre de la asignación histórica. El estudio identifica los códigos anuales que sí se pueden respaldar y deja delimitados los 83 casos de atribución y las 295 ausencias de evidencia anual, junto con cuatro pistas nuevas revisables.
'''
(O/'INFORME_374.md').write_text(report)
dump(O/'QA_FECHA_EXCLUSIVA.json',date_qa)
(O/'CHECKPOINT.md').write_text(f'''# Checkpoint 374 · {datetime.datetime.now().astimezone().isoformat()}

Foco verificado 374 personas / 377 relaciones / 3.320 observaciones. Ver INFORME_374.md, RESULTADOS.json, QA_FINAL.json y MANIFEST.json.
Datos originales y códigos adoptados intactos. No commit/push. No modificar denominadores globales 5.901/6.622/24.774.
Privado: {P}
Resultado anual: 2.942 atribuibles; 83 código único con expediente ambiguo; 295 sin evidencia anual. Cuatro observaciones tienen fecha exclusiva MU–DA; quedan como pistas, sin nueva regla adoptada.
360 relaciones mantienen código único, 12 cambian entre años, cinco sin código. Fechas efectivas de plan pendientes. No equiparar bimestres, trimestres y semestres.
Reproducción: scripts/revisar_trayectorias_374_20261023.py y scripts/cerrar_trayectorias_374_20261023.py. Usar Python bundled con openpyxl. Las dos fuentes históricas recuperadas conservan SHA-256 de fase4; no usar la copia modificada de PROMEDIOS7804 en Descargas.
''')
oldgit=load(O/'GIT_ANTES.json');after={}
for path,before in oldgit.items():
 after[path]={k:subprocess.check_output(['git','-C',path,*args],text=True).strip() for k,args in [('rama',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short'])]}
 assert after[path]['head']==before['head'] and after[path]['rama']==before['rama']
dump(O/'GIT_DESPUES.json',after)
tokens={str(x[k]) for x in obs for k in ['persona','CODCLI'] if x[k]}
personal_pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(s) for s in sorted(tokens))+r')(?![A-Za-z0-9])')
assert not any(personal_pattern.search(p.read_text()) for p in O.iterdir() if p.is_file())
qa.update(agregados_sin_identificadores_del_foco=True,transiciones_con_localizador_ambos_anos=len(changes))
dump(O/'QA_FINAL.json',qa)
(O/'BITACORA.md').write_text('''# Bitácora de revisión dirigida

| Fase · Hito | Acción y evidencia | Resultado / pendiente |
|---|---|---|
| 1/4 · 1/3 | Git y contratos; GIT_ANTES.json | Rama/HEAD preservados |
| 1/4 · 2/3 | Fuentes y hashes; INVENTARIO_FUENTES.csv | Cortes efectivos UMAS no acreditados |
| 1/4 · 3/3 | Recuperación; RELOCALIZACION_FUENTES.json | Dos respaldos con hash exacto |
| 2/4 · 1/3 | Foco y expediente; SEGMENTOS_EXPEDIENTE_PLAN privado | 374 personas / 377 relaciones |
| 2/4 · 2/3 | Lectura MU y PROMEDIOS; FUENTES_HASHES.json | Fuentes conservadas |
| 2/4 · 3/3 | Pares y regímenes; PARES_TRAYECTORIA privado | 381 pares; no equiparar períodos de regímenes distintos |
| 3/4 · 1/3 | Códigos anuales; CAMBIOS_VERSION_ANUAL_AGREGADOS.csv | 12 cambios; fecha efectiva pendiente |
| 3/4 · 2/3 | Fechas y planes; INFORME_374.md | Sin migración fechada acreditada |
| 3/4 · 3/3 | Pistas exclusivas; QA_FECHA_EXCLUSIVA.json | Cuatro pistas no adoptadas |
| 4/4 · 1/3 | Detalle y agregado por período | Código anual separado de vigencia efectiva del plan |
| 4/4 · 2/3 | QA_FINAL.json | Cero duplicados/cambios adoptados; privacidad verificada |
| 4/4 · 3/3 | MANIFEST.json / CHECKPOINT.md | Entrega local sin commit/push; causas y fechas pendientes visibles |
''')
dump(P/'MANIFEST_PRIVADO.json',{'fuentes':M['fuentes'],'salidas':{p.name:sha(p) for p in P.iterdir() if p.is_file() and p.name!='MANIFEST_PRIVADO.json'},'fuera_git':True,'canon_intacto':True})
M.update(fecha_cierre=datetime.datetime.now().astimezone().isoformat(),QA=qa,resultado='Codigos anuales respaldados separados de temporalidad pendiente; cuatro pistas no adoptadas',
 salidas_privadas_hashes={p.name:sha(p) for p in P.iterdir() if p.is_file()},salidas_agregadas_hashes={p.name:sha(p) for p in O.iterdir() if p.is_file() and p.name!='MANIFEST.json'},
 scripts_hashes={str(p):sha(p) for p in [R/'scripts/revisar_trayectorias_374_20261023.py',Path(__file__)]})
dump(O/'MANIFEST.json',M)
print(json.dumps({'qa':qa,'validacion_fecha':date_qa,'cambios_version':S['cambios_version'],'informe':str(O/'INFORME_374.md')},ensure_ascii=False))

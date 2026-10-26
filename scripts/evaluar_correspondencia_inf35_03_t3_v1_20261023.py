"""Evalúa V1 como propuesta interna contextual; no adjudica el diccionario."""
from pathlib import Path
import json,sys,datetime,copy,subprocess
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256,DiccionarioSiesSeguimiento,aplicar_adjudicaciones
read=lambda p:json.loads(Path(p).read_text());now=datetime.datetime.now(ZoneInfo('America/Santiago'))
O=R/'outputs'/('propuesta_inf35_03_t3_v1_'+now.strftime('%Y%m%d_%H%M%S'));O.mkdir()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
prior=R/'outputs/origen_v1_inf35_03_20261023_150536';m=read(prior/'MANIFEST.json');P=Path(m['privado']);ev=read(P/'EVIDENCIA.json');hist=read(P/'AMPLIACION_PRIVADA.json')['historia_plan']
for p,h in m['fuentes_sha256'].items():assert sha256(p)==h
for n,h in m['privados_sha256'].items():assert sha256(P/n)==h
for n,h in m['salidas_sha256'].items():assert sha256(prior/n)==h
sm=read(R/'outputs/secciones_cinco_jornadas_20261023_144650/MANIFEST.json');sepath=Path(sm['privado'])/'EVIDENCIA_REVISION.json';assert sha256(sepath)==sm['privados_hashes'][sepath.name];se=read(sepath)
t=next(x for x in ev['objetivos'] if int(x['periodo'])==3);assert t['caso']=='INF35-03' and int(t['anio'])==2024
# Mismo expediente, plan y evidencia académica real, no solo homologaciones.
linked=[z for z in se['puente_actividad_plan'] if z['rendimiento']['caso']=='INF35-03' and str(z['rendimiento']['ANO'])=='2024' and str(z['rendimiento']['PERIODO'])=='3']
assert len(linked)==8
assert {z['rendimiento']['JORNADA'] for z in linked}=={'D'}
assert {tuple(z['planes']) for z in linked}=={('IINF20241',)}
for z in linked:
 assert any(x['CODCLI']==t['CODCLI'] and x['PLAN_DE_ESTUDIO']=='IINF20241' for x in z['coincidencias_promedios'])
classes={z['rendimiento']['CODIGORAMO'] for z in linked};assert classes=={'AS100PCOM','IF106IINF'}
h2025=[x for x in hist if x.get('CODCLI')==t['CODCLI'] and str(x.get('ANO'))=='2025' and str(x.get('PERIODO'))=='1' and Path(x['fuente']).name=='PROMEDIOSDEALUMNOS_3233.xlsx'];assert len(h2025)==2 and {x['PLAN_DE_ESTUDIO'] for x in h2025}=={'IINF20241'} and {x['JORNADA'] for x in h2025}=={'D'}
bridge=next(x for x in ev['preparacion_mu2025'] if Path(x['fuente']).name=='2025-2.xlsx');assert bridge['valores']['B:CODCLI']==t['CODCLI'] and bridge['valores']['J:JORNADA']=='D'
active=R/'data/diccionario_sies_seguimiento/activo.json';activehash=sha256(active);descriptor=R/read(active)['descriptor'];desc=read(descriptor);assert desc['edicion']=='v6_20261023_dos_jornadas';dbhash=sha256(desc['base_privada']['ruta'])
d=DiccionarioSiesSeguimiento();rows=[json.loads(x[0]) for x in d.db.execute('select payload from observaciones')];b=next(x for x in rows if x['observacion_id']==t['observacion_id']);assert not b['codigo_interno_adoptado'] and not b['codigo_documental_atribuible']
mu={x[0] for x in d.db.execute('select codigo from mu_anual where persona=? and anio=2025',(t['persona'],))};assert mu=={'I162S2C1J1V1'};d.close()
# Simulación, no autorización ni escritura de una versión nueva.
a=copy.deepcopy(b);a.update(codigo_interno_adoptado='I162S2C1J1V1',estado_interno='SIMULACION_PROPUESTA_INF35_03_T3',regla='PROPUESTA_CONTINUIDAD_T3_2024_T1_2025_NO_APROBADA',clasificacion='C propuesta de correspondencia interna; D pendiente aprobación; E atribución documental',requisito_pendiente='Aprobación de criterio temporal interno acotado; atribución documental T3-2024 y fecha de asignación de versión pendientes.')
sim=aplicar_adjudicaciones(rows,[{'observacion_id':b['observacion_id'],'estado_antes':b,'estado_despues':a}]);diff=[x for x,y in zip(sorted(rows,key=lambda z:z['observacion_id']),sorted(sim,key=lambda z:z['observacion_id'])) if x!=y];assert len(diff)==1
for field in ['codigo_documental_atribuible','estado_documental','persona','CODCLI','plan','ano','periodo','sede_dimension','jornada_sies']:
 assert b.get(field)==a.get(field)
def counts(rs,field):
 q=[x for x in rs if not x[field]];return {'observaciones':len(q),'personas':len({x['persona'] for x in q})}
impact={'interno_actual':counts(rows,'codigo_interno_adoptado'),'interno_simulado':counts(sim,'codigo_interno_adoptado'),'documental_actual':counts(rows,'codigo_documental_atribuible'),'documental_simulado':counts(sim,'codigo_documental_atribuible')};assert impact['interno_actual']['observaciones']-impact['interno_simulado']['observaciones']==1;assert impact['documental_actual']==impact['documental_simulado']
result={'caso':'INF35-03','anio':2024,'periodo':3,'codigo_propuesto':'I162S2C1J1V1','estado':'PROPUESTA_INTERNA_RESPALDADA_CON_SUPUESTO_TEMPORAL_NO_APLICADA','clasificacion':'B observaciones; C evaluación y simulación; D aprobación pendiente; E atribución y continuidad exacta de versión','criterio':'Mismo RUT/CODCLI, carrera y plan, actividad ordinaria T3 con jornada D corroborada y código personal único J1V1 en MU2025/T1 siguiente; reutilización retrospectiva acotada para seguimiento interno.','supuesto_explicito':'Se adopta continuidad de versión entre T3-2024 y T1-2025 para este expediente; no está demostrada por una fecha administrativa.','no_extender':['T2-2024 (actividad mixta)','otras personas o planes','T1-2024 (J2V4 documental)','2026 (J1V2 documental)','tasas, vigencia o denominadores'],'aplicado':False,'impacto_simulado':impact}
dump(O/'PROPUESTA.json',result)
report='''# INF35-03 T3-2024: propuesta de correspondencia interna V1

**C. Conclusión:** sí es defendible proponer **I162S2C1J1V1** como correspondencia interna acotada para INF35-03/T3-2024. No se afirma que fuera el código informado en 2024. Esta evaluación cambia el objeto de decisión: la investigación anterior buscaba acreditar la asignación histórica; aquí se evalúa una regla interna explícita para seguir el mismo expediente entre períodos adyacentes. No hay nueva prueba documental del período.

| Comprobación | Evidencia | Clase |
|---|---|---|
| Mismo expediente | CODCLI de 2025-2.xlsx, Hoja1 fila 497, coincide con el del seguimiento; RUT exacto vincula la matrícula anual | B/C |
| Actividad ordinaria T3-2024 en el plan | Ocho evaluaciones, dos asignaturas (AS100PCOM/IF106IINF), sección 1, enlazadas al mismo CODCLI y plan IINF20241; no son ocho personas | B/C |
| Jornada D corroborada para el contexto T3 | Rendimiento, filas 43266–43273, informa D; respaldo T3 del 19-nov y contraste de secciones ya verificados apoyan esa jornada | B/C |
| Continuidad del plan en T1-2025 | PROMEDIOS3233, Hoja1 filas 33082/53598: mismo CODCLI, IINF20241 y D | B |
| Código personal en MU2025 | J1V1 único: Precarga P/Q1023, Final a carga P/Q1003 y descarga P/Q1018 | B |
| Compatibilidad histórica | Oferta 2024 contempla J1V1. No se escoge por mayoría de compañeros ni por numeración del plan | B/C |

**C — Regla propuesta:** reutilizar el código personal del T1 siguiente para T3 anterior cuando el expediente, carrera, plan y jornada del contexto son concordantes y existe actividad académica corroborada. En esta revisión se evalúa exclusivamente INF35-03/T3-2024; no se incorpora una regla universal ni se ignoran cambios de contexto.

**E — Supuesto que debe quedar visible:** la versión permaneció entre T3-2024 y T1-2025. Las fuentes respaldan continuidad del expediente y plan, pero no prueban esa invariancia mediante fecha efectiva. La jornada de un reporte posterior no es por sí sola prueba de jornada histórica; se conserva la corroboración por actividad/secciones y sus límites. PROMEDIOS12166 registra O para historia del mismo plan y MU2026 registra J1V2: ambos permanecen como evidencia, sin trasladarlos hacia atrás ni eliminarlos.

**E — Pendientes documentales:** fecha de asignación o cambio de versión, regla que originó el literal V1 de la precarga y atribución documental del código al T3-2024. Usar V1 internamente no cierra esos pendientes, no certifica un envío o aceptación SIES y no declara errónea V2 en 2026.

**D — Decisión pendiente:** aprobar expresamente este criterio temporal acotado. El usuario solicitó evaluar su uso, no aplicar un cierre en esta intervención. La propuesta está preparada; el diccionario v6 no se modifica. La aprobación anterior de F02 era exclusiva de F02 y no se hereda automáticamente.

**C — Simulación:** una sola observación cambiaría de pendiente a correspondencia interna. T2-2024 de INF35-03 seguiría pendiente por jornada mixta; no se usa esta propuesta para resolverlo. Conteos antes/después en PROPUESTA.json; pendientes documentales idénticos. No se recalcula retención ni se interpreta actividad como vigencia automática.

**C — QA:** huellas de fuentes y evidencias verificadas; simulación en memoria de exactamente una observación, sin cambios de identidad, dimensiones, campo documental ni denominadores. Puntero y base privada v6 sin cambios. Sin cambios del Excel, fuentes o motores, sin commit/push. Detalle individual ya existente queda privado, sin duplicarlo.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('C: propuesta interna INF35-03 T3-2024 = I162S2C1J1V1, con supuesto temporal explícito; no aplicada. D: requiere aprobación acotada. E: documental y fecha siguen pendientes. No extender a T2-2024 ni 2026. Revisar PROPUESTA.json para evidencia e impacto. Diccionario v6, bases, Excel y denominadores sin cambios.\n')
assert sha256(active)==activehash and sha256(desc['base_privada']['ruta'])==dbhash
for p,h in m['fuentes_sha256'].items():assert sha256(p)==h
secrets={t['persona'],t['CODCLI'],t['persona'].split('-')[0]}
for p in O.iterdir():assert not any(s in p.read_text() for s in secrets)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='80ca13a5a249a1a2bd53a699f5f73689b1f53040'
qa={'resultado':'OK_SIMULACION_NO_APLICADA','cambios_simulados':1,'observaciones_conservadas':len(rows)-1,'documental_inalterado':True,'diccionario_activo_inalterado':True,'fuentes_bases_excel_inalterados':True,'denominadores_inalterados':True,'nuevos_identificadores_publicados':False,'commit_push':False};dump(O/'QA.json',qa)
dump(O/'MANIFEST.json',{'fecha_hora':now.isoformat(),'tipo':'Evaluación C y propuesta D pendiente; no adjudicación','antecedentes_sha256':{str(prior/'MANIFEST.json'):sha256(prior/'MANIFEST.json'),str(sepath):sha256(sepath)},'fuentes_sha256':m['fuentes_sha256'],'diccionario':{'descriptor':str(descriptor),'sha256':sha256(descriptor),'puntero_sha256':activehash,'base_sha256':dbhash},'salidas_sha256':{p.name:sha256(p) for p in O.iterdir()},'codigo_sha256':{str(Path(__file__).relative_to(R)):sha256(__file__),'docs/ESPECIFICACION_PROPUESTA_INF35_03_T3_V1_20261023.md':sha256(R/'docs/ESPECIFICACION_PROPUESTA_INF35_03_T3_V1_20261023.md')},'impacto':impact,'QA':qa,'HEAD':head})
print(json.dumps({'output':str(O),'impacto':impact,'manifest_sha256':sha256(O/'MANIFEST.json')},ensure_ascii=False))

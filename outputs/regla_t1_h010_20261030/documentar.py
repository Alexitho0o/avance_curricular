"""Documenta resultados H010 y agrega R28/R29; nunca publica ni modifica originales."""
import argparse,collections as C,json,hashlib,subprocess
from pathlib import Path
from construir import sha,dump,aggregate

def table(rows,cols):
 return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(txt(r.get(c,0)) for c in cols)+' |' for r in rows])
def txt(x):return '' if x is None else str(x)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--privado',type=Path,required=True);a=ap.parse_args();R=a.repo;P=a.privado;O=R/'outputs/regla_t1_h010_20261030';load=lambda p:json.loads(Path(p).read_text())
 cov=load(O/'COBERTURA.json');follow=load(O/'PRIMER_T1_POSTERIOR.json');stable=load(O/'ESTABILIDAD.json');err=load(O/'ERRORES_425_REENCUADRADOS.json');trans=load(O/'TRANSICION_2021_2022.json');sources=load(O/'FUENTES.json')
 result=load(P/'ASIGNACIONES_PRIVADAS.json');covrows=[]
 for k,v in cov.items():
  levels={x['nivel_asignacion']:x['n'] for x in v['por_nivel']}
  covrows.append({'Universo':k,'Total':v['total'],**levels})
 levels=sorted({x['nivel_asignacion'] for v in cov.values() for x in v['por_nivel']})
 pivot=C.defaultdict(C.Counter)
 for x in follow['por_anio_periodo']:pivot[x['anio'],x['periodo']][x['desfase']]+=x['n']
 annual=[{'Año':y,'Período':p,**dict(v),'Total':sum(v.values())} for (y,p),v in sorted(pivot.items())]
 direct=C.Counter();careers=C.Counter()
 for x in follow['respuesta_2020_2022_hacia_2023_2025']:direct[x['anio'],x['primer_T1']]+=x['n'];careers[x['carrera']]+=x['n']
 directrows=[{'Año contexto':y,**{str(dest):direct[y,dest] for dest in [2023,2024,2025]},'Total':sum(direct[y,dest] for dest in [2023,2024,2025])} for y in [2020,2021,2022]]
 st=C.defaultdict(C.Counter)
 for x in stable['por_anio']:st[x['anio']][x['estado']]+=x['n']
 stable_rows=[{'Año':y,'Siguiente':y+1,**dict(v),'Total':sum(v.values()),'% mismo código sobre únicos':round(100*v['MANTIENE']/(v['MANTIENE']+v['CAMBIA']),3) if v['MANTIENE']+v['CAMBIA'] else None} for y,v in sorted(st.items())]
 p99=load(P/'POSICIONES_99_PRIVADAS.json');dump(O/'CASOS_99_AGREGADOS.json',{'clase':'B/C/D/E; propuesta no aplicada','unidad':'posiciones V24; puede repetirse una observación','casos':aggregate(p99,['anio','periodo','carrera','plan','sede','jornada','nivel_asignacion','codigo_candidato','año_T1_fuente','desfase','motivo'])})
 (O/'PASO1_POR_CARRERA.md').write_text('# Primer T1 posterior por carrera · B/C\n\nObservaciones, no personas únicas; no localizado no equivale a nunca informado.\n\n'+table(follow['por_carrera'],['anio','periodo','carrera','primer_T1','desfase','n'])+'\n')
 requirements={'T1_SIN_LINEA_ATRIBUIDA_AL_EXPEDIENTE':'Línea MU anual atribuida al expediente y plan, con identidad y dimensiones verificables; no basta actividad.', 'CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE':'Código del plan original en oferta del mismo año y perfil compatible único; no usar el plan nuevo.', 'CAMBIO_SEDE_JORNADA_ANTES_T1':'Evidencia temporal de sede/jornada del expediente en el primer T1 y decisión sobre el contexto anterior.', 'T1_MULTIPLES_CODIGOS':'Desambiguación documental de líneas T1 del mismo expediente/plan.', 'PRIMER_T1_MULTIPLES_CODIGOS':'Desambiguación de las líneas del primer año T1; no saltar a un año posterior.', 'OFERTA_ANIO_T1_NO_LOCALIZADA':'Oferta anual correspondiente al año del T1 fuente.', 'OFERTA_ATRIBUTOS_MULTIPLES':'Versión de oferta acreditada que resuelva el conflicto de atributos.', 'PERFIL_PLAN_MULTIPLE':'Perfil único de tipo y duración para el plan/año.', 'TIPO_DURACION_PLAN_E':'Tipo y duración gobernados; el perfil v3 candidato no sustituye al v2 activo.'}
 residual=load(O/'RESIDUAL_E.json');residual['requisitos'].update(requirements);dump(O/'REQUISITOS_E.json',residual['requisitos'])
 assert all(x['motivo'] in residual['requisitos'] for x in residual['casos'])
 rules=Path.home()/'.local/share/ipss/repos/IPSS_IA_SKILLS_Y_REGLAS';rc=subprocess.check_output(['git','-C',str(rules),'rev-parse','HEAD'],text=True).strip()
 report=f'''# H010 · candidata v21 por primer T1 informado

Estado: CANDIDATA_NO_ACTIVA_CON_RESIDUALES_E. D Alexi, 30-10-2026.
No se abrió Excel; V25/V26/entregables intactos. No hay commit ni push de avance_curricular.
La meta ≤0,1 % no se alcanza. No se fuerza ninguna versión ni se abre otra iteración.

## Respuesta directa (B/C)

{table(directrows,['Año contexto','2023','2024','2025','Total'])}

Unidad: contextos nativos sin T1 atribuido del mismo expediente/plan en su año,
no estudiantes únicos ni ingresos nuevos acreditados. Carrera con mayor cantidad
observada (no umbral estadístico): {', '.join(f'{k}: {n}' for k,n in careers.most_common(8))}.
Detalle de año/período/carrera: PASO1_POR_CARRERA.md y PRIMER_T1_POSTERIOR.json.
Se distinguen persona sin MU y persona con MU sin ancla del expediente; no son
universos equivalentes. Las 2.966 de v7 incluyen períodos 1, 4 y 5: distribución
{json.dumps(follow['2966_por_periodo'],ensure_ascii=False)}. No se convierten en T2/T3.

## Paso 1 · desfase (B/C; ausencia E)

{table(annual,['Año','Período','X+1','X+2','X+3_O_MAS','SIN_T1_POSTERIOR_LOCALIZADO','Total'])}

Nunca informado sólo significa sin evidencia localizada hasta 2026. No se afirma
que una persona no existió en SIES ni que un contexto implicó matrícula. La
cobertura de los extractos históricos y el futuro están limitados.

## Cobertura separada por nivel (B/C/D/E)

{table(covrows,['Universo','Total']+levels)}

La candidata es una base privada con tablas v20 intactas y una tabla adicional
asignaciones_h010. El código candidato no reemplaza el código documental ni el
interno aprobado. El descriptor NO es un activo del consumidor actual: requiere
aprobación e integración posterior. Los cambios de plan con catálogo se muestran
en nivel propio, sin atribuirles evidencia documental del contexto original.
Las opciones MU2027 son simulaciones del consumidor activo, no T1 futuros observados.

## Estabilidad (B/C)

{table(stable_rows,['Año','Siguiente','MANTIENE','CAMBIA','MULTIPLE_E','Total','% mismo código sobre únicos'])}

Anclas: T1 de v20 + línea MU, o enlace MU–expediente–plan ANUAL congelado H002g.
No se exige actividad PROMEDIOS en período 1. Plan anual observado no acredita
fecha exacta de cambio dentro del año. No se reconstruye identidad RUT–MRUN.

Transición pública reutilizada: {trans['codigos_2021']} códigos en 2021,
{trans['codigos_2022']} en 2022; {len(trans['ultima_matricula_2021'])} con última
matrícula en 2021, controlado hasta 2026 con R25. Hasta 2025 eran 16: dos códigos
reaparecen en 2026. Fuente: TRANSICION_2021_2022.json.

{table(err['causas'],['causa','n'])}

Se reproducen los 425 errores de la prueba antigua T_plan, sin tratarlos como
fallos de H010. La transición personal apoya compatibilidad con recodificación;
no acredita una causa institucional única. Los demás carecen de esa prueba.
Detalle por código en ERRORES_425_REENCUADRADOS.json.

## Residual y límites (E)

{table(cov['v7_3049']['por_motivo'],['nivel_asignacion','motivo','n'])}

Cada combinación año/período/plan/sede/jornada tiene causa y requisito en
RESIDUAL_E.json y REQUISITOS_E.json. Los 99 se detallan sólo en agregado en CASOS_99_AGREGADOS.json.
Sin perfil tipo/duración compatible no se asigna el nivel 3. Los períodos 4/5 no
se homologan. Un ingreso 2026 sin fila MU no se simula como cohorte nueva 2027.

## Controles y gobernanza

QA.json: niveles 1–3 con evidencia anual T1; tipo/duración de nivel 3 compatibles;
3.049 y 99 conciliados; fuentes, tablas v20 y puntero intactos. Las tasas R01–R04
y R19 conservan 0,00 pp por no alteración de indicadores, no por un recálculo
ni por prueba de nuevos desgloses. Meta residual E explícita. Pruebas y
reproducción: QA_CIERRE.json. Identificadores exclusivamente privados.

Regla D registrada en IPSS_IA_SKILLS_Y_REGLAS 1.3.12, commit `{rc}`;
validador sin errores, con pendientes históricos E. No activa v21 ni cambia skills.

Mensaje preparado: `H010 propone código de contexto por primer T1 acreditado y reencuadra evidencia metodológica`.
Lista exacta: LISTA_PUBLICACION.json. No ejecutar commit/push sin autorización.
'''
 (O/'INFORME_H010.md').write_text(report)
 base=R/'outputs/auditoria_metodos_puente_20261023_155309';ident=load(base/'IDENTIFICABILIDAD.json');i=next(x for x in ident if x['llave']=='K2_mas_plan');cv=load(base/'VALIDACION_POR_PERSONA.json')['K3_mas_ingreso_DA_min3']['global'];tem=load(base/'VALIDACION_TEMPORAL.json')['T_plan'];summary=load(base/'RESUMEN.json')
 assert (i['grupos'],i['grupos_multicodigo'],cv['universo'],cv['correctos'],cv['errores'],cv['abstenciones'],tem['global']['errores'],tem['por_anio']['2022']['errores'])==(278,22,8354,7664,6,684,530,425)
 r28={'id':'R28','pregunta':'¿Se validó cómo se unen los campos UMAS con el código SIES?','resultado_clave':'EVIDENCIA_METODOLOGICA_REENCUADRADA: 278 grupos, 256 únicos/22 múltiples; K3 mínimo 3 personas: 8.354 contextos, 7.664 aciertos, 6 errores, 684 abstenciones. Prospectiva T_plan: 50,6 % cobertura, 87,5 % precisión; 425/530 errores en 2022. No mide la regla de primer T1 posterior de H010.','archivo':str((base/'RESUMEN.json').relative_to(R)),'hoja_o_seccion':'RESUMEN; IDENTIFICABILIDAD K2; VALIDACION_POR_PERSONA K3_min3; VALIDACION_TEMPORAL T_plan','script_productor':'scripts/auditar_metodos_puente_20261023.py','commit':'68ab3f91','sha256':sha(base/'RESUMEN.json'),'clase':'B/C; D reencuadre; E grupos','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Fuente independiente que discrimine los 22 grupos.','limites':'Precisión anual no aplicable a ingresos T2/T3; no se borran errores anteriores ni se declaran resueltos por conversación.','evidencias':[{'ruta':str(p.relative_to(R)),'sha256':sha(p)} for p in [base/'IDENTIFICABILIDAD.json',base/'VALIDACION_POR_PERSONA.json',base/'VALIDACION_TEMPORAL.json',R/'outputs/conflictos_22_errores_6_20261023_161400/INFORME.md']]}
 r29={'id':'R29','pregunta':'Asignación de código SIES por regla T1 (H010)','resultado_clave':f"CANDIDATA: v21 separada; universo v7 3.049, E {cov['v7_3049']['residual_E']}; V24 99 posiciones, E {cov['V24_99_posiciones']['residual_E']}. Sin activar ni alterar tasas. Meta residual ≤0,1 % no alcanzada.",'archivo':str((O/'INFORME_H010.md').relative_to(R)),'hoja_o_seccion':'Cobertura, estabilidad y residual','script_productor':str((O/'construir.py').relative_to(R)),'commit':'SIN_COMMIT; base 6505cae','sha256':sha(O/'INFORME_H010.md'),'clase':'D método; B/C evidencia; E límites','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Nueva evidencia de T1/expediente/plan, perfil tipo/duración o decisión explícita sobre residual; activación sólo por Alexi.','limites':'Ancla anual no prueba fecha de cambio; ausencia local no prueba inexistencia SIES. Nivel 5 y simulación 2027 no se mezclan con documental.'}
 mp=R/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=load(P/'ESTADO_INICIAL.json')['mapa'];m['resultados']=[x for x in m['resultados'] if x['id'] not in ['R28','R29']]+[r28,r29];mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
 md=R/'docs/MAPA_RESULTADOS_GOBERNADOS.md';s=md.read_text();s='\n'.join(line for line in s.splitlines() if not line.startswith('| R28 ·') and not line.startswith('| R29 ·'))+'\n';s=s.replace('## Mapa (27 resultados)','## Mapa (29 resultados)')
 addition='\n'.join('| '+ ' | '.join([r['id']+' · '+r['pregunta'],r['resultado_clave'],r['archivo'],r['script_productor'],r['commit'],r['sha256'],r['clase'],r['fecha_resultado'],r['no_recalcular_salvo']])+' |' for r in [r28,r29])
 s=s.replace('\n## Límites por resultado','\n'+addition+'\n\n## Límites por resultado');md.write_text(s)
 dump(O/'FUENTES_R28.json',{'validacion_cifras':'COINCIDEN','grupos':i,'cruzada':cv,'prospectiva':tem,'fuentes':r28['evidencias']})
 print(json.dumps({'directa':directrows,'top_carreras':careers.most_common(8),'R28':'cifras coinciden','R29':'CANDIDATA'},ensure_ascii=False))
if __name__=='__main__':main()

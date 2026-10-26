"""Cierra diagnóstico de procedencia de V1 sin adjudicar ni alterar indicadores."""
from pathlib import Path
import json,sys,subprocess,datetime,collections
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import sha256,DiccionarioSiesSeguimiento
O=R/'outputs/origen_v1_inf35_03_20261023_150536';read=lambda p:json.loads(Path(p).read_text());cfg=read(O/'CONFIG.json');a=read(O/'AMPLIACION.json');back=read(O/'RESPALDO_2024.json');P=Path(cfg['privado']);ev=read(P/'EVIDENCIA.json');person=ev['objetivos'][0]['persona']
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
active=R/'data/diccionario_sies_seguimiento/activo.json';assert read(active)==cfg['diccionario_activo'];desc=R/read(active)['descriptor'];descriptor=read(desc);assert sha256(desc)==read(active)['sha256'];db=Path(descriptor['base_privada']['ruta']);assert sha256(db)==descriptor['base_privada']['sha256']
inputs={**cfg['fuentes_sha256'],**a['fuentes_hashes_adicionales'],back['fuente']:back['sha256'],str(desc):sha256(desc),str(active):sha256(active),str(db):sha256(db)}
# Preservación del libro y base anual respecto de sus huellas gobernadas.
book=Path('/Users/alexi/Desktop/RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx');inputs[str(book)]='e7f797b5de9a6e9748cd250e9931947dbc8469f65d01f5a488c765e0009676fe'
base=R/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx';inputs[str(base)]='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
for p,h in inputs.items():assert sha256(p)==h,p
assert a['celda_precarga']=={'hoja':'Precarga','celda':'Q1023','valor':1,'tipo':'n','formula':False,'comentario':None,'hipervinculo':None}
assert len(ev['preparacion_mu2025'])==32
for z in ev['preparacion_mu2025']:
 for k,v in z['valores'].items():
  if k.endswith(':VERSION'):assert v==1 and k not in z['formulas']
# Registro conservado con plan individual y código anual, sin transferir el año.
d=DiccionarioSiesSeguimiento();pending=[]
for t in ev['objetivos']:
 row=json.loads(d.db.execute('select payload from observaciones where id=?',(t['observacion_id'],)).fetchone()[0]);assert not row['codigo_interno_adoptado'] and not row['codigo_documental_atribuible'];pending.append({'caso':t['caso'],'anio':t['anio'],'periodo':t['periodo'],'estado':'PENDIENTE','clasificacion':'E'})
mu=[]
for y in [2024,2025,2026]:
 cs={r[0] for r in d.db.execute('select codigo from mu_anual where persona=? and anio=?',(person,y))};mu.append({'anio':y,'codigos':sorted(cs)})
d.close()
assert next(x['codigos'] for x in mu if x['anio']==2024)==['I162S2C1J2V4']
assert next(x['codigos'] for x in mu if x['anio']==2025)==['I162S2C1J1V1']
assert next(x['codigos'] for x in mu if x['anio']==2026)==['I162S2C1J1V2']
res={'caso':'INF35-03','periodo_objetivo':'T3-2024','procedencia_observable':'IPSS_Procesamiento.xlsx / Precarga!Q1023, valor numérico literal 1, conservado en preparación y descarga MU2025','regla_generadora_localizada':False,'plan_personal':'IINF20241','codigo_documental_por_anio':mu,'codigo_T3_adoptado':None,'clasificacion':'B procedencia observada; C contraste; E correspondencia temporal no demostrada','cierres_adicionales':0,'pendiente':'Evidencia que atribuya J1V1 al expediente en T3-2024 o una equivalencia temporal aprobada; no basta un valor anual posterior o el mismo nombre de plan.'}
dump(O/'RESULTADO.json',res)
report='''# Origen de V1 — INF35-03

Proceso: seguimiento intertrimestral IPSS 162. Objetivo T3-2024, plan IINF20241; contraste con preparación MU2025. Repositorio avance_curricular, feature/ire-2026. Diagnóstico B/C/E; no nueva decisión D ni regla oficial A.

## Conclusión

**B/C.** La procedencia observable de V1 llega hasta `IPSS_Procesamiento.xlsx`, hoja `Precarga`, celda **Q1023**. Contiene el número **1**, sin fórmula, comentario ni hipervínculo de celda. No se localizó en los respaldos examinados la regla que asignó esa versión al expediente. El nombre «Precarga» no demuestra por sí solo quién generó ese dato ni una aceptación oficial.

**E.** No se puede confirmar que V1 correspondiera al plan en T3-2024. La observación sigue pendiente; no se la convirtió en V2 ni se declaró errónea la V1 enviada en 2025. Se distingue procedencia técnica localizable de causa o validez académica de la asignación.

## Cadena documental observada

| Contexto/fuente | Localizador | Dato | Clase |
|---|---|---|---|
| Respaldo Matrícula_Pregrado_2024.xlsx | Intake 1, fila 415; hoja de matrícula, fila 482 | J2V4, ingreso 2024; el respaldo conserva matrícula anual | B |
| IPSS_Procesamiento.xlsx | Precarga, P1023/Q1023 | J1/V1, valores guardados; FECH_CAR=16-abr-2025 | B |
| Mismo libro | Carga_Completa, fila 1025; Carga_Completa (2)/(3), fila 1030 | J1V1 conservado | B |
| Mismo libro | Final a carga, fila 1003 | J1V1 conservado | B |
| IPSS2025.xlsx | Hoja1, fila 1003, N/O | J1/V1 | B |
| Descarga de lo cargado_08-05-2025_22-26-22_Matrícula_Pregrado_2025.xlsx | Hoja granular, fila 1018, P/Q | J1/V1; FECH_CAR=08-may-2025 | B |
| Código anual personal MU2026, índice gobernado | mu_anual, identidad exacta, año 2026 | J1V2 | B/C |

**C/E.** La coincidencia entre estas hojas reconstruye dónde se conserva el valor; no acredita el orden temporal exacto de cada edición ni que unas fueran copiadas directamente de otras. FECH_CAR, creación/modificación del XLSX y fecha de matrícula no se usan como fecha efectiva de cambio de plan.

## Qué aportaron los otros respaldos

**B.** Se inspeccionaron 17 libros de preparación MU2025: 32 filas relacionadas con la misma persona, repetidas entre hojas y libros. Los registros UMAS cotejados muestran IINF y jornada D, pero no incorporan una equivalencia que asigne V1 al plan IINF20241. `2025-2.xlsx`, Hoja1, fila 497, conserva el CODCLI del expediente: permite confirmar identidad/expediente, pero no contiene código SIES ni versión en esa fila.

**B.** La hoja `Mapa` de IPSS_Procesamiento relaciona Informática con el componente carrera **1** (filas 12 y 17). Ese 1 es COD_CAR; no es una regla VERSION=1. La columna de VERSION examinada no apunta a ese mapa. Los vínculos externos del libro apuntan a PROMEDIOS2071; no se encontró conexión, queryTable ni VBA en ese libro que genere la versión. La ausencia de esos objetos no descarta operaciones manuales o un generador externo no conservado.

**B/C.** Se revisaron además el XLSX de matrícula incremental denominado 02-01-2025 y su CSV de 820 filas (32 columnas, sin encabezados; orden contrastado con la hoja 1 del XLSX). La persona no aparece con RUT+DV exacto en ninguno. Esta ausencia no demuestra retiro ni resuelve T3. El CSV 2024 de la misma carpeta y el respaldo 2024 enlazado desde ese libro conservan J2V4.

**B/C.** Los registros de PROMEDIOS ya extraídos con el mismo CODCLI conservan el plan IINF20241 durante T3-2024 y en períodos 2025. Las exportaciones registran jornadas distintas sobre la misma historia académica; esas jornadas no se convierten en un historial administrativo retroactivo. La continuidad del código de plan no permite por sí sola fechar qué versión SIES se utilizó antes de la matrícula anual 2025.

## Contraste de oferta

**B.** El catálogo histórico gobernado contiene en 2024 y 2025 tanto J1V1 como J1V2, ambas presenciales, regulares y de ocho semestres. V1 figura «Vigente sin estudiantes nuevos» y V2 «Vigente con estudiantes nuevos». Fuente: maestro de oferta, hoja original `in`, filas 82339/82340 para 2024 y 54243/54244 para 2025; copia exacta en AMPLIACION.json.

**E.** Esas etiquetas no deciden por sí solas la asignación de una persona que cambió de jornada. No se interpreta «sin nuevos» como eliminación de estudiantes antiguos; tampoco como autorización para trasladar V1 a cualquier plan. No hay una regla leída que establezca IINF20241 + D = V1 para este contexto.

## Resultado y siguiente evidencia

**E.** Para resolver esta observación falta la asignación efectiva a J1V1/J1V2 durante T3-2024, o una equivalencia temporal interna expresamente aprobada para ese expediente y plan. La revisión acota la búsqueda: el dato V1 ya llega como literal a Precarga!Q1023; no nace del cálculo de retención, del cruce por RUT actual ni de la tabla Mapa. No se atribuye autoría a personas desde nombres de carpetas o metadatos.

**C.** QA: fuentes/Excel/base anual/diccionario v6 conservan sus hashes; identidad exacta; detalle privado fuera de Git; no se hacen adjudicaciones. Permanecen tres observaciones por jornada pendientes en el foco anterior, incluida INF35-03 T3-2024. Bases y denominadores intactos. Sin commit/push.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('B/C: V1 se rastrea a Precarga!Q1023, literal sin fórmula/comentario. Mapa identifica C1, no V1. 17 libros de preparación, incremental XLSX/CSV y respaldo 2024 revisados. E: origen de la asignación y aplicación a T3-2024 sin demostrar; v6 sin adjudicaciones nuevas. No repetir búsqueda de RUT ni elegir versión por pares. Buscar antecedente de la precarga o equivalencia temporal aprobada. Sin bases/denominadores/Excel modificados ni commit/push.\n')
qa={'resultado':'OK_TECNICO_OBSERVACION_E','libros_preparacion':17,'filas_preparacion_foco':32,'observaciones_adjudicadas':0,'pendiente_T3_2024_conservado':True,'diccionario_v6_hash_identico':True,'base_anual_y_excel_hash_identico':True,'fuentes_hash_identico':True,'denominadores_inalterados':True,'identificadores_solo_privado':True,'sin_commit_push':True}
dump(O/'QA.json',qa)
secrets={person,person.split('-')[0],ev['objetivos'][0]['CODCLI']}
for p in O.iterdir():
 if p.is_file():assert not any(x in p.read_text() for x in secrets),p
for p,h in inputs.items():assert sha256(p)==h,p
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip();assert head=='80ca13a5a249a1a2bd53a699f5f73689b1f53040' and branch=='feature/ire-2026'
scripts=[R/'scripts/rastrear_origen_v1_inf35_03_20261023.py',R/'scripts/ampliar_origen_v1_inf35_03_20261023.py',R/'scripts/comprobar_respaldo_2024_inf35_03_20261023.py',Path(__file__),R/'docs/ESPECIFICACION_ORIGEN_V1_INF35_03_20261023.md']
dump(O/'MANIFEST.json',{'fecha_hora':datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),'objetivo':'INF35-03 T3-2024, procedencia V1 MU2025','fuentes_sha256':inputs,'salidas_sha256':{p.name:sha256(p) for p in O.iterdir() if p.is_file()},'privado':str(P),'privados_sha256':{p.name:sha256(p) for p in P.iterdir() if p.is_file()},'codigo_sha256':{str(p.relative_to(R)):sha256(p) for p in scripts},'QA':qa,'git_antes_despues':{'rama':branch,'HEAD':head},'commit_push':False})
print(json.dumps({'reporte':str(O/'INFORME.md'),'manifest_sha256':sha256(O/'MANIFEST.json'),'resultado':'T3-2024 pendiente; V1 literal de precarga verificada'},ensure_ascii=False))

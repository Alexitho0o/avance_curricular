"""Prueba retrospectiva y conclusión, sin promover un criterio nuevo."""
import json,hashlib,datetime,subprocess,sys
from pathlib import Path
from collections import Counter
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
O=Path(sys.argv[1]);m=json.loads((O/'MANIFEST.json').read_text());Q=Path(m['privado'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
obs_path=Path('/Users/alexi/.local/share/ipss/reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json')
obs=load(obs_path);mu=load(Q/'MU_RELEIDA.json');d=load(O/'RESULTADOS_DESCRIPTIVOS.json')
foc=[x for x in obs if (x['carrera'],x['plan'],x['sede_dimension'],x['jornada_sies'],x['ano'])==('IINF','IINF20241','2','4','2024')]
persons={x['persona'] for x in foc if x['codigo_documental_atribuible']};rows=[]
def select(person):
 sets=[{x['codigo'] for x in mu if x['persona']==person and x['ANIO_INFORMADO']==year and x['codigo'].startswith('I162S2C1J4V')} for year in ['2023','2025']]
 return next(iter(sets[0])) if len(sets[0])==len(sets[1])==1 and sets[0]==sets[1] else ''
for person in sorted(persons):
 pred=select(person)  # No accede al código objetivo 2024.
 truth={x['codigo_documental_atribuible'] for x in foc if x['persona']==person and x['codigo_documental_atribuible']}
 state='COINCIDE' if pred and truth=={pred} else 'DIFIERE' if pred else 'ABSTENCION'
 rows.append({'persona':person,'prediccion':pred,'objetivo':sorted(truth),'estado':state})
counts=dict(Counter(x['estado'] for x in rows));assert counts=={'ABSTENCION':102,'COINCIDE':31} or counts=={'COINCIDE':31,'ABSTENCION':102}
close_path=Path('/Users/alexi/.local/share/ipss/cierre_interno_f02_20261023_084246/ADJUDICACION_INTERNA.json');close=load(close_path)
person=close['persona'];assert select(person)=='I162S2C1J4V2'
targets=[x for x in foc if x['persona']==person];assert len(targets)==3 and all(not x['codigo_interno_adoptado'] for x in targets)
dump(Q/'PRUEBA_RETROSPECTIVA_PRIVADA.json',rows)
dump(Q/'PROPUESTA_F02_TRES_PERIODOS.json',{'regla_propuesta':'CONTINUIDAD_ANUAL_MISMA_FAMILIA_2023_2025','estado':'PROPUESTA_PARA_APROBACION_NO_ADOPTADA','alcance':'F02/IINF20241 2024/T1,T2,T3; no regla universal','observaciones':[{'observacion_id':x['observacion_id'],'persona':x['persona'],'CODCLI':x['CODCLI'],'periodo':x['periodo'],'codigo_propuesto':'I162S2C1J4V2','codigo_adoptado':x['codigo_interno_adoptado'],'fuentes_promedios':x['fuentes_promedios'],'evidencias_anuales':x['evidencias_matricula']} for x in targets]})
# Detalle completo bajo resguardo privado; publicación solo de comparación acotada.
dump(Q/'RESULTADOS_DESCRIPTIVOS_COMPLETOS.json',d)
detail=d.pop('casos_dirigidos')
d['prueba_retrospectiva']={'personas':133,'coinciden':31,'difieren':0,'abstenciones':102,'V3_seleccionadas':0,'limite':'Validación anual de subconjunto; no acredita asignación por expediente/período ni discriminación general V2/V3'}
d['F02']={'candidato_por_continuidad':'I162S2C1J4V2','periodos_propuestos':['2024/T1','2024/T2','2024/T3'],'nuevos_cierres':0,'pendientes_internos_F02':3,'cierre_autorizado_anterior_conservado':True,'estado':'PROPUESTA_PARA_APROBACION_NO_ADOPTADA'}
dump(O/'RESULTADOS_DESCRIPTIVOS.json',d)
report='''# IINF20241: contraste V2/V3 y F02

**Resultado C/E:** la evidencia converge en V2 como propuesta interna para las
tres observaciones IINF20241 de F02, pero el criterio nuevo de continuidad entre
cortes no se adopta automáticamente. La instrucción vigente exige dejar las
propuestas nuevas para aprobación. El cierre anterior autorizado se conserva.

## Comparación observada — B/C

| Elemento | V2 documentada: 132 personas | V3 documentada: una persona | F02 |
|---|---|---|---|
| Ingreso DA | 2021: 1; 2022: 8; 2023: 38; 2024: 85 | 2020 | 2023 |
| FOR_ING_ACT en MU2024 (código, sin reinterpretar) | 1: 130; 11: 2 | 11 | 1 |
| Ingreso actual/origen MU2024 | Distribución en RESULTADOS_DESCRIPTIVOS.json | 2020/2019 | 2023/2023 |
| Trayectoria dirigida | No se supone idéntica para todo el grupo | IECIRE2020/J2 hasta 2023; IINF20241/J4 en 2024 | IECIREOL20211/J4 desde 2023; IINF20241/J4 en 2024 |
| Código MU 2023 → 2024 → 2025 | Se prueba por persona, no por mayoría | C1J2V4 → C1J4V3 → sin fila localizada en la base leída | C1J4V2 → C1J4V2 → C1J4V2 |
| Homologaciones IINF20241 en 2024/T1 | No se usa como discriminador general | 3 asignaturas | 4 asignaturas |
| Plan y año de actividad IINF20241 | 2024 | 2024 | 2024 |

Todos los códigos abreviados tienen prefijo I162S2. Los conteos se calculan por
persona, evitando contar tres veces a quien tiene actividad en T1/T2/T3. Las
etiquetas documentales corresponden al diagnóstico y al código MU anual
releído; no son comprobantes de aceptación SIES por cada período UMAS.

**B:** oferta 2024: C1J4V2 es Plan Regular, ocho semestres; C1J4V3 es Plan
Regular de Continuidad, cuatro semestres. El plan previo C1J2V4 de la persona
V3 figura como Plan Regular de ocho semestres en oferta 2022 y 2023. Por tanto,
no se puede explicar su V3 afirmando que ya cursaba continuidad: lo observado
es un cambio de jornada y código/perfil declarado, cuya causa no se acredita.

**B/C:** PROMEDIOS confirma diez filas IINF20241 para F02 en 2024: seis T1
(cuatro homologadas y dos aprobadas), dos T2 aprobadas y dos T3 aprobadas.
La persona V3 tiene nueve filas: cinco T1 (tres homologadas y dos reprobadas),
dos T2 y dos T3 reprobadas. Son registros académicos del reporte, no un censo
completo de asignaturas esperadas ni prueba de matrícula al cierre. Los niveles
se solapan; tampoco distinguen por sí solos la versión. No se cambian tasas.

## Prueba independiente de selección — C

Se ocultó el código objetivo MU2024. Para cada una de las 133 personas con
versión atribuida se consultó exclusivamente MU2023 y MU2025 de la misma
persona y familia I162S2C1J4. Solo se seleccionó un código si ambos cortes
tenían el mismo código único. Después se contrastó con MU2024.

- 31 personas seleccionadas: 31 coincidencias, cero diferencias.
- 102 abstenciones por falta de los dos extremos concordantes.
- La única persona V3 no cumple el criterio y queda en abstención.
- F02, fuera del grupo documental de prueba, obtiene V2 por ambos extremos;
  además MU2024 documenta V2 para la persona/familia.

**Límite E:** la prueba valida concordancia anual en el subconjunto cubierto.
No demuestra la fecha efectiva de asignación al nuevo expediente ni valida
una regla universal: no hay caso V3 seleccionado. No usar 31/31 como precisión
general ni suponer que un ingreso 2023 obliga a V2. FOR_ING_ACT=11 tampoco
obliga a V3: hay dos personas V2 con ese valor.

## Propuesta concreta para F02 — C, pendiente de decisión D

Registrar las tres observaciones IINF20241 2024/T1, T2 y T3 como
**correspondencia interna contextual V2**, apoyada en identidad exacta,
plan/períodos observados, misma familia y V2 antes, durante y después del año.
Conservar el código documental por expediente pendiente y la fecha
administrativa del cambio como desconocida. No generalizar a todo IINF20241.

Esta propuesta relaja la exigencia previa de enlace explícito al nuevo
expediente; por eso requiere aprobación y no se aplica silenciosamente. La
instrucción del usuario que rige esta decisión dice: «Deja propuestas nuevas
para aprobación con número de afectados y riesgos».

Si se autoriza, cerraría tres observaciones de una persona: pendientes internos
3.093 → 3.090 y personas con pendiente 1.751 → 1.750, sobre los mismos
denominadores. Esto es un escenario, no el estado adoptado. Los pendientes
documentales seguirían en 3.213 observaciones / 1.838 personas.

**Estado vigente:** tres observaciones IINF20241 de F02 pendientes; una
observación IECIREOL20211 ya cerrada internamente por la autorización anterior.
No se alteraron bases, denominadores, códigos documentales ni el motor anual.

## Trazabilidad y QA

Fuentes: OBSERVACIONES_PRIVADAS.json del diagnóstico reproducido (24.774
observaciones); BASE_RETENCION_MU de la base anual 2022–2026; Hoja1 de
PROMEDIOSDEALUMNOS_12166.xlsx; oferta anual de maestro.json. Se releyeron 355
filas MU y 1.858 filas PROMEDIOS para las 134 personas del contraste.
Localizadores fuente/hoja/fila e identificadores quedan en el detalle privado;
MANIFEST.json y FUENTES_HASHES.json fijan entradas y resultados por SHA-256.

QA técnico OK_CON_ADVERTENCIAS: fuentes intactas, grupos sin doble conteo,
prueba separada por persona, cierre anterior conservado, sin promoción del
criterio nuevo. No se afirma causalidad de las diferencias. Sin commit/push.
'''
(O/'INFORME.md').write_text(report)
hashes=m['fuentes_hashes'];hashes[str(Path(__file__))]=sha(__file__)
# La especificación se amplió para documentar la prueba, no es una base fuente.
spec=R/'docs/ESPECIFICACION_CONTRASTE_F02_IINF_20261023.md';hashes[str(spec)]=sha(spec)
assert all(sha(p)==h for p,h in hashes.items())
qa=load(O/'QA.json');qa.update(estado='OK_CON_ADVERTENCIAS',prueba_personas=133,coincidencias=31,diferencias=0,abstenciones=102,propuesta_no_adoptada=True,limitacion='Sin validación de asignación individual al plan por período; único V3 en abstención')
dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',hashes)
before=load(O/'GIT_ANTES.json');after={k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]};assert before['HEAD']==after['HEAD'] and before['rama']==after['rama'];dump(O/'GIT_DESPUES.json',after)
secrets={x['persona'] for x in obs}|{x['CODCLI'] for x in obs}
for p in O.iterdir():
 if p.name=='MANIFEST.json':continue
 s=p.read_text();assert not any(k and k in s for k in secrets)
m.update(fecha_cierre=datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),fuentes_hashes=hashes,salidas_hashes={p.name:sha(p) for p in O.iterdir() if p.name!='MANIFEST.json'},privados_hashes={p.name:sha(p) for p in Q.iterdir()},clasificacion='B/C observaciones/prueba; E propuesta condicionada; D cierre anterior conservado',resultado=d['F02'],qa=qa)
dump(O/'MANIFEST.json',m)
print(json.dumps({'salida':str(O),'resultado':d['F02'],'QA':qa['estado']},ensure_ascii=False))

"""Publica el informe local del ensayo, sin adoptar sus candidatos."""
import csv,datetime,hashlib,json,subprocess,sys
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];O=Path(sys.argv[1])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=load(O/'MANIFEST.json');d=load(O/'RESULTADOS.json');Q=Path(m['privado']);t=load(Q/'RETROSPECTIVA.json');c=load(Q/'CANDIDATOS_REVISADOS.json')
assert all(sha(p)==h for p,h in m['fuentes_hashes'].items())
assert d['escenario_actividad']['observaciones_candidatas']==2 and d['escenario_incluyendo_condicionadas']['observaciones_candidatas']==3
assert len({x['observacion']['persona'] for x in c})==1
rows=[]
for x in d['tabla_candidatos']:
 rows.append({**x,'regimen':' / '.join(x['regimen']),'nombre_oferta':' / '.join(x['nombre_oferta'])})
with (O/'CANDIDATOS_AGREGADOS.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
report='''# Ensayo del criterio F02 en otros pendientes V2/V3

## Resultado ejecutivo — B/C; E adopción pendiente

Se revisaron las 3.090 observaciones internas pendientes de 1.750 personas,
después del cierre aprobado de F02. El ensayo abarca todas las carreras del
diagnóstico y años observados 2019–2026, no solo IINF20241.

**Dos observaciones son candidatas a cierre interno con actividad corroborada.
Una tercera queda condicionada porque su evidencia del período contiene solo
homologaciones. Las tres corresponden a la misma persona y al código
I162S2C6J4V2. No se seleccionan candidatos nuevos V3. Nada se aplica.**

| Carrera UMAS / plan | Período 2024 | Evidencia releída | Candidato | Evaluación |
|---|---|---|---|---|
| TTMREOL / TTMREOL20231 | Bimestre 3 | Una asignatura aprobada | I162S2C6J4V2 | Candidato interno con actividad |
| TTMREOL / TTMREOL20231 | Bimestre 5 | Una asignatura aprobada | I162S2C6J4V2 | Candidato interno con actividad |
| TCRE / TCRE20241 | Trimestre 1 | Cinco asignaturas homologadas; sin actividad distinta de reconocimiento en las filas revisadas | I162S2C6J4V2 | Condicionado; no contar como cursado probado |

Nombre en oferta del código candidato: TECNICO EN CONECTIVIDAD Y REDES.
No se fusionan el bimestre 3 y el trimestre 1 ni se transforma su numeración.
La marca de homologación no es una regla oficial de exclusión ni elimina la
observación: distingue el tipo de evidencia. Asignar versión a un reconocimiento
académico y acreditar cursado/retención del período son decisiones distintas.

## Comprobación por persona, expediente y período — B/C

La persona mantiene I162S2C6J4V2 en MU2023, MU2024 y MU2025. Se verificó
identidad exacta y familia I162S2C6J4, no nombre de carrera ni mayoría de grupo.
Cada observación se contrastó con su propio CODCLI, carrera, jornada, plan,
año y período de PROMEDIOS, además del contexto DA. La oferta 2024 contiene
el código. Los localizadores fuente/hoja/fila están en el detalle privado.

El ensayo conserva la exigencia de un código único concordante en los tres
años consecutivos. No se rellena el año intermedio usando únicamente extremos,
ni se elige una familia entre varias para hacer coincidir el resultado.

## Efecto simulado, sin aplicar — C/E

| Estado / escenario | Pendientes internos: observaciones | Personas con algún pendiente | Personas completamente cerradas nuevas |
|---|---:|---:|---:|
| Actual, después de F02 | 3.090 | 1.750 | 0 |
| Aprobar solo las dos con actividad corroborada | 3.088 | 1.750 | 0 |
| Aprobar además la observación solo de homologaciones | 3.087 | 1.749 | 1 |

El primer escenario resolvería parcialmente una persona. El segundo cerraría
esa misma persona, no otra adicional. No sumar ambas alternativas. Se mantienen
5.901 personas, 6.622 expedientes de referencia y 24.774 observaciones del
universo aprobado; tampoco se cambian denominadores de retención. Documentales:
3.213 observaciones / 1.838 personas, sin cambios en los dos escenarios.

## Prueba retrospectiva y límite — C/E

Sobre 8.354 unidades persona-año-familia de 4.762 personas con código atribuido,
se seleccionó con años anterior y posterior, ocultando el código objetivo:

- 620 selecciones V2/V3: 619 coincidencias y una diferencia.
- 468 selecciones de otras versiones, fuera del alcance V2/V3.
- 7.266 abstenciones por extremos ausentes, múltiples o no concordantes.

La diferencia corresponde a I162S2C1J1 en 2025: los extremos proponían V2 y
el año objetivo documentaba V1. Por eso se mantiene la corroboración explícita
del año intermedio; ese caso no aprobaría el criterio completo. No se corrige.

En la familia candidata I162S2C6J4 hubo 50 coincidencias, cero diferencias y
336 abstenciones. Las 50 comparaciones pertenecen a 44 personas: no son 50
personas independientes. Estos resultados no garantizan asignación documental
por expediente/período ni constituyen validación universal.

## Por qué no se seleccionan los demás — C

| Motivo principal exclusivo | Observaciones |
|---|---:|
| Años anterior/posterior no disponibles o no concordantes | 2.880 |
| Familia no única en el cruce gobernado | 167 |
| Sin contexto DA exacto | 8 |
| Código del año intermedio no corrobora | 10 |
| Versión distinta de V2/V3 | 22 |
| Candidatas con actividad | 2 |
| Condicionada solo a reconocimiento | 1 |
| Total | 3.090 |

Esta es una clasificación por la primera condición incumplida, no una suma de
causas independientes. Cobertura MU releída: 2018–2026. No hay MU2027 en las
entradas; por ello el criterio no cierra observaciones 2026 usando un año futuro.
La falta de evidencia para este método no equivale a ausencia de matrícula.

## Trazabilidad, conservación y decisión pendiente

Fuentes: base anual BASE_RETENCION_MU 2022–2026, MAT_IP_CIISA_2018–2021,
PROMEDIOSDEALUMNOS_12166.xlsx, diagnóstico reproducido y sus adjudicaciones
F02 autorizadas, familias gobernadas y oferta histórica del maestro. Se releyó
MU y se verificaron exactamente las filas de actividad candidatas.

QA OK_CON_ADVERTENCIAS: hashes de entradas conservados, universo completo
evaluado, candidatos sin duplicar personas, ninguna asignación nueva aplicada,
F02 excluido de nuevos cierres. Una diferencia retrospectiva y una observación
solo de homologaciones quedan visibles. El detalle individual permanece fuera
de Git; el informe y CSV no contienen identificadores.

La eventual adopción de las dos candidatas y el tratamiento de la tercera
requieren una decisión posterior del usuario. No se cambia el criterio de
resuelto ni los contadores vigentes por presentar este escenario.
Sin commit/push. Rama y HEAD conservados en GIT_ANTES/GIT_DESPUES.json.
'''
(O/'INFORME.md').write_text(report)
(O/'CHECKPOINT.md').write_text('# Ensayo V2/V3 no aplicado\n\nDos candidatos con actividad y uno condicionado solo a homologaciones, una persona, I162S2C6J4V2. Cero candidatos V3. Estado vigente: 3.090 observaciones / 1.750 personas internas pendientes. No aplicar escenario sin autorización; no repetir cierre F02. Leer INFORME.md y MANIFEST.json, detalle privado en CANDIDATOS_REVISADOS.json.\n')
before=load(O/'GIT_ANTES.json');after={k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]};assert before['HEAD']==after['HEAD'] and before['rama']==after['rama'];dump(O/'GIT_DESPUES.json',after)
obs=load('/Users/alexi/.local/share/ipss/reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json');secrets={x['persona'] for x in obs}|{x['CODCLI'] for x in obs}
for p in O.iterdir():
 if p.name=='MANIFEST.json':continue
 s=p.read_text();assert not any(k and k in s for k in secrets),'Identificador en salida agregada'
m['fuentes_hashes'][str(Path(__file__))]=sha(__file__);dump(O/'FUENTES_HASHES.json',m['fuentes_hashes'])
m.update(fecha_cierre=datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),salidas_hashes={p.name:sha(p) for p in O.iterdir() if p.name!='MANIFEST.json'},privados_hashes={p.name:sha(p) for p in Q.iterdir()},alcance_adopcion='Ninguno; escenario para revisión',rama=after['rama'],HEAD=after['HEAD'])
dump(O/'MANIFEST.json',m)
assert all(sha(p)==h for p,h in m['fuentes_hashes'].items())
print(json.dumps({'informe':str(O/'INFORME.md'),'sha256':sha(O/'INFORME.md'),'aplicado':False},ensure_ascii=False))

"""Documenta entrega V19 con evidencia agregada y sin identificadores personales."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,subprocess,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
a=load(OUT/'ENSAMBLADO.json');q=load(OUT/'QA_FASE4.json');c=load(OUT/'COPIA_VERIFICADA.json')
assert all(x['resultado']=='PASA' for x in q['controles'])
assert sha(Path(c['ruta']))==sha(Path(a['salida_privada']))==a['sha256']
assert git('rev-parse','HEAD')=='8e2fb85bb8703758d6878681c9e2a29016e60c63'
assert git('status','--short','--untracked-files=no')=='M PROYECTO_IPSS.json'
stamp=datetime.now(ZoneInfo('America/Santiago')).isoformat()
text=f'''# Fase 4/6 — Excel trazable V19

**D — Alcance autorizado:** recuperar el libro funcional reutilizando las fases anteriores. Sin cambios de bases, denominadores, diccionario ni nuevas adjudicaciones. Sin commit/push.

**B/C — Entrega local:** `{c['ruta']}`.
SHA-256: `{a['sha256']}`.
Copia restringida idéntica: `{a['salida_privada']}`.
Ambas están fuera de Git; contienen el detalle individual de la maqueta recuperada. El manifiesto no publica esas bases.

## Hito 1/3 — Maqueta y correcciones

**B/C:** se recuperaron las cinco hojas individuales originales —9,11,20,24,25 por su nombre visible— y las fórmulas históricas que la edición agregada había fijado. Se preservaron las fórmulas ya vigentes de V18 y las correcciones V14–V18. El resultado contiene {a['hojas']} hojas, {a['formulas']:,} fórmulas XML, {a['graficos']} gráficos y {a['tablas']} tablas.

**C:** el ensamblado conserva los dibujos/gráficos como partes originales idénticas. No importa/exporta toda la maqueta a un motor que pueda reconstruir esos objetos. Las nuevas hojas y fórmulas se crearon y recalcularon con Artifact Tool; luego se integraron sin reemplazar los estilos anteriores. Se mantuvo la reparación de estilos de V15.

**B/C/D:** valores vigentes conservados: actividad T2-2025=611/1150; actividad T3-2025=546/1150; matrícula T3-2025=1023/1150; T3-2026 grupo1=1360/1467; T2-2026=462/528 matrículas; conjunto2026=2290/2519. No son indicadores intercambiables. Ninguna cifra numérica previa de los resúmenes cambió en el archivo guardado.

## Hito 2/3 — Detalle y fórmulas conectados

**B/C:** hoja56_Vista_T1_T2_T3 integra la vista validada de fase3: 6374 filas que conservan6358 posiciones y2854 contextos. Se incluyen3520 posiciones sin contexto. Cuenta posición impide duplicar el padrón cuando hay más de un expediente; Cuenta contexto identifica la unidad del diccionario.

**C:** hoja53 columnas F/K/M ahora calculan población de origen y posiciones con/sin contexto desde56 mediante SUMIFS. Hoja54 columna N cuenta las221 combinaciones desde56 mediante COUNTIF. Hoja52 sigue consumiendo53/54. Hoja57 presenta cobertura y pendientes con fórmulas sobre56. Se probaron654 conteos de53 y221 grupos de54 contra V18, sin diferencias.

**B/C/D/E:** permanecen2718 contextos con mismo código,37 con otro código ya respaldado y99 pendientes;24 de esos99 pertenecen al foco multiversión. Se distinguen2742documentales,13internos aprobados y99pendientes. No se resuelve ningún pendiente nuevo ni se altera una tasa por falta de versión.

**C/E — Límite explícito:** la vista56 es un derivado materializado de la consulta al diccionario, con fuente/hoja/fila, regla y pendiente; se actualiza reejecutando la preparación, no consultando GitHub desde Excel. Las fuentes y ciertos numeradores/denominadores materializados de53 G/H siguen teniendo script y evidencia; no se presentan falsamente como fórmulas individuales. El avance de cobertura del diccionario no cambia el numerador de retención.

## Hito 3/3 — Guía, navegación y QA

**C:** guía27 reconstruida para57 hojas, con enlaces, rol, contenido, entradas, tipo de cálculo y privacidad. Se distinguen las auditorías históricas29–51 del estado vigente52–57. Portada, hoja18 y resumen52 incorporan navegación al detalle o al resumen actual. Se corrigieron las notas heredadas de104pendientes y v7activo: ahora99 y v8, coherentes con el descriptor.

**E — Pendientes visibles:**99 códigos (24multiversión incluidos),3520 posiciones sin contexto,66 renuncias sin nómina individual, alcance545 frente a ingreso exclusivo2026-3 y diferencias de calendario. No se suman como una misma brecha y no equivalen a desertores.

**C — QA:** {q['total']}/{q['total']} controles estructurales y de conservación correctos. Todos los XML parseables; relaciones con destinos existentes; tablas con nombres/IDs únicos; originales protegidos por hash; fórmulas previas y cifras históricas conservadas. Se verificó la dependencia en Artifact Tool cambiando temporalmente un pendiente a interno:13/99→14/98→13/99; el estado original se restauró antes de guardar. La revisión visual del suplemento se registra en el manifiesto.

**E — Próxima puerta:** falta la fase5 de conciliación integral y prueba de apertura/recálculo de todo el libro en Excel nativo, incluidos filtros conectados. El QA de este paso no certifica esa apertura ni que todas las cachés históricas se hayan recalculado. No se declara entrega definitiva ni cobertura100%.

**B/C — Git:** rama `{git('branch','--show-current')}`; HEAD antes/después `{git('rev-parse','HEAD')}`. El cambio previo de PROYECTO_IPSS.json sigue intacto; no hubo staging, commit ni push. Los archivos de esta fase están locales, no publicados.
'''
(OUT/'INFORME_FASE4.md').write_text(text)
save('CHECKPOINT_FASE4.json',{'fecha':stamp,'fase':'4/6','estado':'EDICION_LOCAL_PREPARADA_QA_NATIVO_PENDIENTE_FASE5','clasificacion':'B/C/D/E','hitos':[{'hito':'1/3','resultado':'Maqueta formularia recuperada y correcciones preservadas','archivo':'ENSAMBLADO.json'},{'hito':'2/3','resultado':'Vista longitudinal y conteos de53/54/57 conectados por fórmulas','archivo':'QA_FASE4.json'},{'hito':'3/3','resultado':'Guía57hojas, navegación, pendientes y copia de Escritorio verificados','archivo':'COPIA_VERIFICADA.json'}],'pendiente':'Fase5: recálculo integral, prueba de filtros y apertura nativa; mantener causas/atribuciones pendientes','no_repetir':['Adjudicaciones aprobadas','Extracción completa histórica','Conciliación de fuentes de fases1–3'],'bases_denominadores_modificados':False,'commit':False,'push':False})
protected=load(OUT.parent/'fase1/CADENA_Y_FUENTES.json')['preservacion']
for p,h in protected.items():assert sha(Path(p))==h
save('MANIFEST_FASE4.json',{'fecha':stamp,'proceso':'Retención intertrimestral IPSS162','version':'V19','fase':'4/6','clasificacion':'B/C/D/E; ninguna nueva regla oficial A','especificacion':{'ruta':'docs/ESPECIFICACION_FASE4_EXCEL_TRAZABLE_20261025.md','sha256':sha(ROOT/'docs/ESPECIFICACION_FASE4_EXCEL_TRAZABLE_20261025.md')},'fuentes_protegidas_sha256':protected,'vista_fase3':{'ruta':str(OUT.parent/'fase3/MANIFEST_FASE3.json'),'sha256':sha(OUT.parent/'fase3/MANIFEST_FASE3.json')},'salida_privada':a['salida_privada'],'copia_escritorio':c['ruta'],'sha256_excel':a['sha256'],'contenido_individual':'Solo local,fuera de Git; permisos600','graficos_identicos':13,'revision_visual':'resumen.png,guia.png,vista.png en carpeta privada; revisados en esta ejecución','qa':q['estado'],'recalculo_integral_nativo':'Pendiente fase5','archivos_locales':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST_FASE4.json'},'git':{'rama':git('branch','--show-current'),'HEAD_antes':git('rev-parse','HEAD'),'HEAD_despues':git('rev-parse','HEAD'),'tracked_preexistente':git('status','--short','--untracked-files=no'),'commit':False,'push':False}})
print(json.dumps({'informe':str(OUT/'INFORME_FASE4.md'),'hash_manifiesto':sha(OUT/'MANIFEST_FASE4.json')},ensure_ascii=False))

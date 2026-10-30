"""Cierre documental limitado: no certifica requisitos no ejecutados."""
import argparse,json,hashlib,subprocess,re,shutil
from pathlib import Path
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser()
    for x in ['repo','privado','libro']:ap.add_argument('--'+x,required=True)
    a=ap.parse_args();r=Path(a.repo);private=Path(a.privado);base=r/'outputs/trazabilidad_integral_umas_sies_20261025';o=base/'h008_20261030';rel=str(o.relative_to(r))
    initial=read(private/'ESTADO_INICIAL.json');cfg=read(private/'CONFIG.json');native=read(o/'QA_NATIVO_V25.json');struct=read(o/'QA_ESTRUCTURAL_PRE_EXCEL.json')
    post=read(o/'QA_GUARDADO_NATIVO.json');assert post['estado']=='PASS'
    assert sha(a.libro)==native['sha256_v25']
    # Los originales ya estaban versionados. Registrar evidencia, no duplicarlos.
    legacy=[]
    for f in ['fase4/build.mjs','fase4/cerrar.py','fase4/ensamblar.py','fase6_procedencia_v24/construir.mjs','fase6_procedencia_v24/ensamblar.py']:
        p=base/f;path=str(p.relative_to(r));commit=subprocess.check_output(['git','-C',str(r),'log','-1','--format=%H','--',path],text=True).strip()
        assert commit;legacy.append({'ruta':path,'sha256':sha(p),'commit':commit,'estado':'YA_VERSIONADO; no modificado','limite':'Constructor histórico con rutas locales; no se presenta como reproducción cruda integral parametrizada.'})
    put(o/'CONSTRUCTORES_PREVIOS.json',legacy)
    (o/'REPRODUCIR.md').write_text('''# Reproducción H008

C · Ensamblado incremental reproducido en un directorio privado aislado: V24 + fuentes fijadas en CONFIG.json. Las dos salidas previas al recálculo son idénticas byte a byte (REPRODUCCION_AISLADA.json). Excel cambia metadatos, serialización y cachés al recalcular: QA_NATIVO_V25.json comprueba fórmulas y constantes, y 6740 resultados numéricos frente a la copia QA de V24, sin diferencias.

No equivale a reproducción integral desde fuentes crudas: R19 conserva pendientes de proxies y desgloses. La Fase 6 integral queda E, no cerrada.

Variables del entorno: H008_PRIVATE (directorio privado), H008_OUTPUT (archivo nuevo), H008_PYTHON, H008_NODE y H008_NODE_MODULES (dependencias locales). CONFIG.json conserva rutas y SHA-256, nunca se publica. FUENTES_H008.json y FUENTES_FOTOS_H008.json documentan las huellas sin datos individuales.

```sh
"$H008_PYTHON" outputs/trazabilidad_integral_umas_sies_20261025/h008_20261030/reproducir_seguimiento.py \
  --config "$H008_PRIVATE/CONFIG.json" --privado "$H008_PRIVATE/ejecucion_nueva" \
  --salida "$H008_OUTPUT" --informes "$H008_PRIVATE/ejecucion_nueva/informes" \
  --node "$H008_NODE" --node-modules "$H008_NODE_MODULES"
```

La salida no debe existir: el comando se detiene antes de sobrescribir. Ejecutar qa_h008.py antes del recálculo para el control estructural y de objetos OOXML. Después, abrir y recalcular esa copia en Excel, guardar y comparar valores con la copia nativa. El control de igualdad binaria de gráficos es previo al guardado nativo, que puede reserializarlos. Nunca abrir ni guardar V24 como salida.

Los cinco constructores históricos solicitados ya estaban en Git (CONSTRUCTORES_PREVIOS.json). No se vuelven a agregar como si fueran nuevos ni se alteran sus manifiestos históricos. Los productores H008 leen rutas privadas por argumento/configuración; H007 permanece como antecedente gobernado.
''')
    (o/'COMPARACION_V24_V25.md').write_text('''# Comparación V24 → V25 · candidata

| Indicador R19 | V24 | V25 recalculada | Observado − referencia | Cambio de tasa |
|---|---:|---:|---:|---:|
| T1 2026 → T3, personas | 1360/1467 | 1360/1467 | 0/0 | 0,00 pp |
| Total T3 2026, personas | 2290/2519 | 2290/2519 | 0/0 | 0,00 pp |
| Ingreso T2 2026, matrículas | 462/528 | 462/528 | 0/0 | 0,00 pp |

B/C · Las fórmulas e insumos anteriores se conservaron. Los 6740 resultados numéricos comparables de las hojas de resultado coinciden con la copia QA gobernada de V24; detalle de hoja18 por cohorte en COMPARACION_V24_V25.json. Las celdas «Sin foto completa» y «No aplica» siguen siendo texto, no cero.

La hoja56 añade contexto v20 en AG:AO y respaldo de fotos en AP:AT. La hoja57 añade el resumen L:Q. C1 no acredita mismo expediente T1 ni vigencia. Las nuevas fotos se muestran con su año/período real; no sustituyen proxies de actividad de otro corte. En T2-2026 la foto arroja 1407 VIG1, 61 VIG0 y 3 NO APLICA, pero el proxy anterior de hoja18 se conserva como tal. No se convierte esa foto en una nueva tasa activa.

E · QA nativo de la copia adicional de 77 escenarios pendiente; 77/77 comprobados de forma independiente. No se declara Hito 2 totalmente aprobado.
''')
    # Completar comparación de celdas sólo con valores nativos agregados.
    from qa_h008 import book,equal
    _,wb=book(a.libro);comp=read(o/'COMPARACION_V24_V25.json')
    for x in comp['celdas']:
        v=wb[x['hoja']]['cells'][x['celda']]['v'];old=x['V24_referencia_recalculada'];x['V25_cache']=v
        x['delta']=v-old if isinstance(v,(float,int)) and isinstance(old,(float,int)) else None
        x['coincide']=equal(v,old);x['clase']='B/C recálculo nativo';x['causa']='Sin cambio de regla/insumos R19; C1 y fotos en respaldo separado'
    comp['limite']='Comparación nativa efectuada; pendiente de filtros nativos y reproducción cruda integral R19.';assert all(x['coincide'] for x in comp['celdas']);put(o/'COMPARACION_V24_V25.json',comp)
    qa={'estado':'PASS_CON_ALCANCE; HITO_2_Y_FASE_6_NO_CERRADOS','estructural':f"{struct['pasan']}/{struct['total']}",'regresion_independiente_filtros':'77/77','resultados_nativos_sin_diferencias':native['resultados_comparados'],'errores_formula':len(native['errores']),'apertura_sin_reparacion':True,'graficos_conservados_y_revisados':13,'tablas_conservadas':37,'formulas_y_constantes_preservadas':not native['contenido_alterado'],'v24_intacta':sha(cfg['entradas']['v24']['ruta'])==cfg['entradas']['v24']['sha256'],'sha256_v25':sha(a.libro),'pendientes_E':['Repetir 77 escenarios en la copia nativa corregida; no equivale a la regresión independiente ya aprobada.','Reproducción integral cruda de R19: proxies y desgloses pendientes; se reprodujo el ensamblado incremental.'],'commit':False,'push':False}
    qa['control_guardado_nativo']=post['estado'];qa['formulas_numericas_comparadas_libro_completo']=post['formulas_numericas_comparadas']
    put(o/'QA_H008.json',qa)
    (o/'INFORME_H008.md').write_text(f'''# H008 · Seguimiento T1–T3 V25 sobre v20

Fecha 30-10-2026. Base Git `{initial['head']}`. Estado **CANDIDATA_CON_LIMITES; Hito 2 y Fase 6 no cerrados**. Sin commit ni push. R19 permanece BORRADOR_NO_ACTIVO; R20, H001, fuentes y v20 no cambian.

## Hito 1 · Inventario cerrado

D · Alexi: las fotos representan el cierre del período 2 o 3, sin exigir un día calendario. No se atribuye fecha histórica a partir del nombre de un archivo.

B/C · Las seis combinaciones quedan inventariadas: cuatro halladas (dos ya usadas en R19 y con C4=0) y dos parciales, ambas T2-2025. De C4=1414, 681 tienen foto disponible y 733 quedan con fuente parcial. Disponibilidad no significa matrícula vigente. Evidencia: INVENTARIO_FOTOS_H008.json/.md. La fuente 10246 congelada de P2-2026 contiene 14204 filas y localiza 1471/1471 documentos del padrón T1; el listado de 528 ingresos T2 no la sustituye.

E · Falta la foto completa de cierre T2-2025. SOLICITUD_FOTOS_UMAS.md es sólo borrador, no enviado. No se pide reconstruir historia desde un estado actual.

## Hito 2 · V25 generada y recalculada; límite de QA explícito

B/C · Libro privado: `{a.libro}`. SHA-256 `{sha(a.libro)}`. V24 conserva su hash `{cfg['entradas']['v24']['sha256']}`.

B/C · Se integraron 1135 posiciones C1 y 1136 contextos v20 (una posición tiene dos). De esos contextos, 108 llevan correspondencia interna D ya aprobada y 1028 siguen E en v20. No son 1135 códigos adjudicados nuevos. Respaldo de contexto, código documental, correspondencia interna y expediente T1 quedan separados. Evidencia: INTEGRACION_C1.json.

B/C · Las fotos completas se incorporan a la vista en AP:AT, con fuente y cierre académico. FOTOS_INTEGRADAS.json informa los estados por cohorte/período. No reemplazan silenciosamente los proxies de R19. Las tasas principales conservan 1360/1467, 2290/2519 y 462/528, diferencias 0/0 y 0,00 pp; COMPARACION_V24_V25.json/.md incluye los valores por cohorte.

C · ZIP/XML íntegros; 13/13 controles estructurales; 37 tablas y 13 gráficos conservados, estilos centrados horizontal/vertical. Recálculo y guardado en Excel: 0 errores, 6740 resultados numéricos comparables sin diferencias y ninguna fórmula o constante anterior modificada. Se revisaron los 13 gráficos; se conservaron las limitaciones visuales heredadas (categorías alternadas en carrera/modalidad y etiquetas reducidas en hoja16), sin modificar series. El render nuevo del complemento es RESUMEN_COMPLEMENTO_V20.png.

C · Control adicional sobre el archivo guardado: {post['formulas_numericas_comparadas']} fórmulas con resultado numérico de todo el libro coinciden con la copia QA de V24, incluidas hojas de base y auxiliares; no se confunden con 6740 resultados de presentación. Las celdas con contenido siguen centradas y las referencias de las series y todos los autofiltros previos permanecen; la vista de seguimiento tiene su filtro ampliado a AT. La guía de hojas ya carecía de autofiltro. Excel omitió 21 celdas XML vacías, sin valor ni fórmula; no hubo pérdida de contenido. Evidencia: QA_GUARDADO_NATIVO.json.

E · Los 77 casos pasan la regresión independiente. Una copia privada adicional con escenarios nativos fue rechazada por orden de celdas; no se aceptó su reparación. El constructor quedó corregido, pero no se certifica su ejecución. Excel dejó de responder en esa prueba auxiliar y la conexión siguió agotando el tiempo de espera; no se cerró por la fuerza. **No declarar 77 interacciones nativas ni QA total aprobado.** V25 sí abrió sin reparación y quedó guardada antes de esa prueba adicional. Evidencias: QA_ESTRUCTURAL_PRE_EXCEL.json, FILTROS_77_REGRESION.json y QA_NATIVO_V25.json.

## Hito 3 · Propuesta lista, no aplicada

C/E · PROPUESTA_ADJUDICACION_99.md/.json conserva 95 candidatos únicos (63 jornada distinta y 32 sin enlace T1) y cuatro IINF20241 con alternativas. Incluye opciones por código, evidencia, límites y decisión aprobar/rechazar/pedir evidencia. Una adjudicación exclusiva de código no cambia las tasas de la hoja18: 0,00 pp; no implica nueva vigencia. No se aplicó ninguna herencia.

## Hito 4 · Sin fuente nueva

B/C · La publicación 10-07-2026 y el MRUN H2 tienen los hashes ya gobernados. R09 sigue CERRADA_DOCUMENTADA, causa E. No se reconstruyó ningún vínculo personal ni se repitió el conteo. Evidencia: CONTROL_FUENTES_MRUN.json.

## Hito 5 · Reproducción incremental, no integral cruda

C · Un comando parametrizado produjo una copia aislada idéntica byte a byte antes del recálculo: `{read(o/'REPRODUCCION_AISLADA.json')['sha256_aislada']}`. El guardado nativo cambia cachés y serialización; se comprueba contenido por separado. REPRODUCIR.md documenta el comando y CONSTRUCTORES_PREVIOS.json acredita que los constructores antiguos solicitados ya estaban versionados.

E · La Fase 6 integral sigue pendiente: reproducir R19 desde fuentes crudas y resolver su paridad de proxies/desgloses no se sustituye con V24 como entrada. Se conserva esa dependencia visible; no se declara cerrada.

## Decisiones y reanudación

1. Validar la candidata V25 sólo después de completar los 77 escenarios nativos pendientes. Las cifras R19 no se activan por este trabajo.
2. Aprobar/rechazar/pedir evidencia para los grupos de los 99; cuatro siguen con más de una opción.
3. Aprobar o ajustar el borrador de solicitud T2-2025 antes de cualquier envío.
4. La Fase 6 requiere completar reproducción cruda gobernada; no abrir nuevas inferencias para forzar el cierre.

Archivos tocados: LISTA_PUBLICACION_H008.json/.md. Los 25 cambios preexistentes quedan intactos y fuera del stage; detalles personales e intermedios, sólo privados. El libro no se incluye en la publicación propuesta.
''')
    # Guardar v2 íntegra y documentar v3 sin borrar la historia.
    prev=base/'PLAN_FASES_HITOS_v2_20261030.md'
    if not prev.exists():shutil.copyfile(base/'PLAN_FASES_HITOS.md',prev)
    plan=prev.read_text().replace('· v2','· v3',1)
    plan=plan.replace('Sin publicación nueva ni modificación del libro.','H008 genera V25 candidata; sin publicación y sin modificar V24.')
    plan=plan.replace('V24 no se migra a v20: 1.135 posiciones tienen contexto actual, pero no se integró una vista nueva','H008 integra 1135 posiciones C1 como respaldo v20 en V25; no adjudica código ni acredita expediente T1')
    plan=plan.replace('| 6: circuito reproducible y publicación | PENDIENTE |','| 6: circuito reproducible y publicación | PARCIAL; INTEGRAL PENDIENTE |')
    plan=plan.replace('| 4: Excel | EJECUTADA; fase4/MANIFEST_FASE4.json y cadena V19–V24 |','| 4: Excel | V19–V24 ejecutadas; V25 CANDIDATA_CON_LIMITES, h008_20261030/INFORME_H008.md |')
    plan=plan.replace('| 5: QA | EJECUTADA_EN_ALCANCE_DOCUMENTADO;','| 5: QA | H008 PARCIAL: recálculo y preservación PASS; 77 escenarios nativos pendientes. Antecedente EJECUTADA_EN_ALCANCE_DOCUMENTADO;')
    plan+='\n## H008 · estado v3\n\nV2 íntegra: PLAN_FASES_HITOS_v2_20261030.md, SHA-256 `'+sha(prev)+'`.\n\nH1 inventario cerrado: 681 C4 con foto disponible y 733 parciales T2-2025. D Alexi: cierre académico 2/3 sin exigir fecha exacta. H2 V25 candidata: 1135 posiciones/1136 contextos, fotos como respaldo separado, 6740 resultados nativos sin diferencias; falta certificar 77 escenarios nativos. H3 propuesta99 lista sin aplicar. H4 sin nueva fuente MRUN, R09 cerrado. H5 ensamblado incremental idéntico; no reproduce R19 crudo integral. R26 candidata, R19 borrador.\n\nComando e insumos: h008_20261030/REPRODUCIR.md, FUENTES_H008.json y FUENTES_FOTOS_H008.json. No abrir otra iteración de atribución con las mismas fuentes. Pendientes exactos y paradas en INFORME_H008.md. Sin commit ni push.\n'
    (base/'PLAN_FASES_HITOS.md').write_text(plan)
    mp=r/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=read(mp)
    r25=next(x for x in m['resultados'] if x['id']=='R25')
    r25['pendientes_H008']={'estado':'Parcialmente atendidos; ver R26 CANDIDATA','fotos':'733 C4 con fuente parcial T2-2025; solicitud borrador','adjudicacion_99':'Propuesta lista, no aplicada','fase6':'Incremental reproducida; integral cruda y 77 escenarios nativos pendientes','evidencia':rel+'/INFORME_H008.md'}
    new={'id':'R26','pregunta':'¿Qué integra V25 del seguimiento T1–T3 sobre v20 y qué falta certificar?','resultado_clave':'CANDIDATA_CON_LIMITES: 1135 posiciones/1136 contextos; 681 C4 con foto disponible y 733 parciales; tasas R19 sin cambios; QA nativo de 77 escenarios y reproducción integral pendientes.','archivo':rel+'/INFORME_H008.md','hoja_o_seccion':'Hitos 1–5; QA y límites','sha256':sha(o/'INFORME_H008.md'),'commit':'SIN_COMMIT; base '+initial['head'],'script_productor':rel+'/reproducir_seguimiento.py','clase':'B/C; D corte académico; E pendientes','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Completar QA nativo; foto completa T2-2025 o evidencia/decisión explícita para los 99; reproducción cruda gobernada R19. R09 sólo con fuente individual nueva.','limites':'No activa R19, no adjudica 99, no modifica H001/R20/v20; V25 contiene identificadores y queda local.'}
    m['resultados']=[x for x in m['resultados'] if x['id']!='R26']+[new];put(mp,m)
    md=r/'docs/MAPA_RESULTADOS_GOBERNADOS.md';text=md.read_text();lines=text.splitlines();lines=[l for l in lines if not l.startswith('| R26 ·')]
    for i,l in enumerate(lines):
        if l.startswith('| R25 ·') and 'Pendientes H008:' not in l:lines[i]=l.replace('Fase 6 del plan pendiente.','Fase 6 del plan pendiente. Pendientes H008: ver R26; 99 sin aplicar y foto T2-2025 parcial.')
    idx=next(i for i,l in enumerate(lines) if l.startswith('| R25 ·'))+1
    lines.insert(idx,f"| R26 · {new['pregunta']} | {new['resultado_clave']} | {new['archivo']} · Hitos 1–5 | {new['script_productor']} | {new['commit']} | {new['sha256']} | {new['clase']} | 2026-10-30 | {new['no_recalcular_salvo']} |")
    md.write_text('\n'.join(lines)+'\n')
    before=json.loads(subprocess.check_output(['git','-C',str(r),'show',initial['head']+':docs/MAPA_RESULTADOS_GOBERNADOS.json'],text=True))
    assert m['resultados'][:24]==before['resultados'][:24]
    assert all(sha(r/f)==h for f,h in initial['ajenos'].items())
    print('Documentación candidata actualizada; R01–R24 y cambios ajenos intactos; sin commit/push.')
if __name__=='__main__':main()

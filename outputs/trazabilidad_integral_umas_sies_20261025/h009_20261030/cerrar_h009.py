"""Documenta el cierre con límites y escanea solo las rutas autorizadas H009."""
import argparse,json,hashlib,re,ast,subprocess,shutil
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();[p.add_argument('--'+x,required=True) for x in ['repo','privado','privado-h008','desktop','reglas']];a=p.parse_args()
 r=Path(a.repo);pr=Path(a.privado);p8=Path(a.privado_h008);desk=Path(a.desktop);rules=Path(a.reglas);base=r/'outputs/trazabilidad_integral_umas_sies_20261025';o=base/'h009_20261030'
 git=lambda *v:subprocess.check_output(['git','-C',str(r),*v],text=True).strip()
 assert git('rev-parse','--abbrev-ref','HEAD')=='feature/ire-2026';assert not git('diff','--cached','--name-only')
 initial=load(p8/'ESTADO_INICIAL.json');assert all(sha(r/k)==v for k,v in initial['ajenos'].items())
 native={'estado':'E_QA_NATIVO_NO_COMPLETADO','clase':'B observación de aplicación; E cobertura no acreditada','apertura_inicial_sin_reparacion':True,'guardado_inicial_y_recalculo':True,
   'totales_iniciales_guardados':{'estudiantes':2379,'retenidos':1476,'tasa':1476/2379},
   'intento_1':{'bloque':1,'casos_previstos':'1–15','ultimo_caso_observado':4,'seleccion':'Acumulado 2022-2025 / Tecnologías / Todas','estudiantes_observados':1766,'retenidos_observados':1162,'resultado':'Tiempo de espera agotado en comando nativo y lectura posterior; el bloque no entregó resultados certificables'},
   'cierre':'Excel cerrado normalmente sin guardar selecciones de prueba; no cierre forzado',
   'reintento_unico':{'bloque':1,'caso':1,'fase':'reapertura previa al primer caso','resultado':'Dos lecturas de accesibilidad agotaron tiempo de respuesta; se detiene sin tercera iteración'},
   'casos_certificados':0,'casos_esperados':77,'capturas_representativas_revisadas':0,
   'pendiente':'Completar bloques 1–6 (15+15+15+15+15+2), prueba visual de cada año/sector/jornada y 10 combinaciones; capturar cuatro selecciones. También QA nativo de H006 v2.',
   'bloqueos_no_borrados':[x.name for x in desk.glob('~$*') if any(v in x.name for v in ('V20','V21','V25','V26'))],
   'limite':'77/77 de H008 es regresión independiente, no 77 selecciones en Excel. No se publican capturas de pantallas con datos individuales.'}
 write(o/'QA_NATIVO_H009.json',native)
 q=load(o/'QA_H009.json');assert q['estado']=='PASS_ESTRUCTURAL_CON_QA_NATIVO_E';q['qa_nativo']=native;write(o/'QA_H009.json',q)
 reproducido=pr/'reproduccion/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V26.xlsx';config=load(o/'CONFIG_GRAFICOS.json');assert sha(reproducido)==config['salida_sha256_pre_excel']
 write(o/'REPRODUCCION_H009.json',{'clase':'C','estado':'PASS','sha256_pre_excel':sha(reproducido),'igual_a_primera_generacion':True,'limite':'El guardado Excel cambia serialización y cachés; la comparación funcional posterior está en QA_H009.json.'})
 src=r/'outputs/excel_resumen_cruce_20261030/RESUMEN_CRUCE_SIES_UMAS_20261030.xlsx';v2=pr/'RESUMEN_CRUCE_SIES_UMAS_20261030_v2.xlsx';z0=ZipFile(src);z1=ZipFile(v2);dif=[];count=0
 for part in z0.namelist():
  if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',part):
   root0=E.fromstring(z0.read(part));root1=E.fromstring(z1.read(part));cells1={c.get('r'):c for c in root1.findall('.//m:sheetData/m:row/m:c',N)}
   for c in root0.findall('.//m:sheetData/m:row/m:c',N):
    count+=1;y=cells1.get(c.get('r'))
    signature=lambda c:(dict(c.attrib),[(E.QName(v).localname,dict(v.attrib),v.text) for v in c.iterdescendants()])
    if y is None or signature(c)!=signature(y):dif.append({'parte':part,'celda':c.get('r')})
 assert not dif
 copy=desk/'ENTREGA_RETENCION_20261031'/v2.name;assert not copy.exists() or sha(copy)==sha(v2)
 if not copy.exists():shutil.copy2(v2,copy)
 write(o/'QA_RESUMEN_V2.json',{'estado':'PASS_PRESERVACION_QA_NATIVO_E','clase':'C/E','celdas_originales_comparadas':count,'diferencias':dif,'original_sha256':sha(src),'copia_sha256':sha(v2),'desktop_sha256':sha(copy),'zip_integro':z1.testzip() is None,'graficos':4,'corregidos':3,'limite':'No certificado en Excel tras el segundo fallo; no sustituye el original.'})
 (o/'DECISION_ORDEN.md').write_text('''# Orden de gráficos · D Alexi, 30-10-2026

SIES frente a interna: orden por tasa SIES; interna como comparación. También se aplica a los dos gráficos comparativos de la hoja 16 que conservan series de subsistema y referencia.

Presencial / A distancia (hoja 14): tasa total de la categoría = retenidos de ambas modalidades / estudiantes de ambas modalidades, fórmula nativa desde los mismos auxiliares. Ninguna modalidad manda. La tasa total no se grafica; cada serie conserva su tasa. Una modalidad sin datos no recibe cero ni dibuja punto; una categoría sin datos en ambas no aparece.

Desempate alfabético estable; lectura ascendente de izquierda a derecha en columnas y arriba abajo en barras. Un cero real con denominador positivo se conserva. Regla general: referencia definida; sin ella, tasa total ponderada. No promediar tasas ni preguntar de nuevo por otro gráfico sin referencia.

Regla publicada en IPSS_IA_SKILLS_Y_REGLAS: reglas_negocio/formato-excel-ipss.md. La implementación no acredita por sí sola el QA visual nativo pendiente.
''')
 (o/'ORIGEN_REGRESION.md').write_text('''# Origen de la regresión · B/C/E

| Versión | Ceros al filtrar | Orden | Evidencia |
|---|---|---|---|
| AUDITADO_ENTREGA 22-10, 20fe8438… | Auxiliar CW7:CW9 consecutivo solo >0; CV recupera modalidad; no certifica gráfico | Cachés ordenadas en algunos desgloses; no prueba selección viva | REVISION_ANTECEDENTES_ENTREGAS.json: ocho gráficos con referencias rotas «label 0», «categories» |
| V14–V18 | No acreditado por matriz de correcciones | No acreditado | fase1/correcciones/MATRIZ_CORRECCIONES_V14_V18.md: cambios de tasas, notas y esquemas; no certifica simultáneamente compactación y orden |
| V19 | Referencias rotas | No certificable | fase5/REFERENCIAS_GRAFICOS_V19.json; INFORME_FASE5.md |
| V20 / V21 / V24 / V25 | Ocho rangos fijos DA:DX incluyen filas vacías | Referencias directas, sin compactación u orden dinámico en el rango final | INVENTARIO_GRAFICOS.json; fase5/patch_v21_chart_helpers.py |
| V26 candidata | Nombres INDEX de longitud dinámica; NA() solo para series ausentes | COUNTIFS con desempate, INDEX/MATCH; tasa total para modalidades y SIES para comparación | CONFIG_GRAFICOS.json; QA_H009.json. Prueba completa en Excel E |

E: no se encontró evidencia de una versión anterior con compactación, referencias válidas y orden funcionando simultáneamente. Se confirma la pérdida del mecanismo auxiliar al pasar a referencias directas, pero no una regresión desde un producto completamente correcto. No se inventa esa versión. Se revisaron versiones disponibles del Escritorio, la copia auditada privada y los manifiestos/informes fase 1, 4 y 5.
''')
 (o/'REPRODUCIR.md').write_text('''# Reproducir H009

Entradas: V25 con SHA-256 63b55351334616833a2e687fbeb36314a0cbb1538c10b6a891c99f94475adc0a; H006 original 5338543e375ed227e0297ed6ab136e1a67392e94f5969b1dd38b0d537578b03d. Libros privados por argumento; nunca incluirlos en Git.

1. `python3 construir_v26.py --origen "$V25" --salida "$V26_NUEVA" --informes "$SALIDA"`. La salida debe llamarse RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V26.xlsx para reproducir el hash; no sobrescribe.
2. `python3 corregir_resumen_v2.py --origen "$H006" --salida "$H006_V2_NUEVA" --informe "$SALIDA/RESUMEN_V2.json"`.
3. Abrir y recalcular las copias en Excel. Ejecutar los 77 casos de fase5/CASOS_FILTROS.json en bloques de 15. En H009 se agotó el único reintento: no está certificado.
4. `python3 qa_graficos_filtros.py --origen "$V25" --libro "$V26" --config CONFIG_GRAFICOS.json --salida "$QA"`. El modo estructural conserva E si no se adjunta evidencia nativa. `--nativo` exige 77 registros (seleccion, totales, graficos con aux) y cuatro capturas revisadas; un orden, cantidad o total incorrectos falla.
5. `python3 test_graficos_filtros.py`: cero observado, modalidad ausente, desempate y detección de desorden. Guardar/restaurar selección 2379/1476/62,04 %. No tratar esos tests como selección o imagen nativa.

La edición acotada OOXML conserva las estructuras nativas del libro; no reexporta bases ni crea una matriz de cálculo paralela. La copia previa al guardado reproduce el mismo hash; el guardado de Excel se controla por celdas/fórmulas/objetos, no por identidad binaria.
''')
 rh=subprocess.check_output(['git','-C',str(rules),'rev-parse','HEAD'],text=True).strip()
 report=f'''# H009 · corrección de gráficos con límite de QA nativo

Estado: CANDIDATA_CON_QA_NATIVO_E. Se cumple la parada autorizada por fallo del único reintento; no se declara cierre 77/77.

## Resultados

- D: orden SIES para comparación y tasa total ponderada para Presencial/A distancia; ver DECISION_ORDEN.md. No se añadió una serie total.
- B/C: V26 en el Escritorio, SHA-256 `{q['sha256_v26']}`. Diez gráficos corregidos: ocho en hoja 14 y dos comparativos en hoja 16; trece conservados. 37 tablas y filtros conservados. {q['valores_numericos_comparados']} valores originales iguales; cero cambios de fórmulas/constantes originales y cero errores inesperados. NA() intencional únicamente en auxiliares ausentes. Todos los estilos con contenido centrados.
- C: reproducción previa a Excel idéntica `{sha(reproducido)}`; cuatro tests PASS. Fuente: QA_H009.json, REPRODUCCION_H009.json.
- B/E: apertura inicial sin reparación y guardado nativo correctos; lectura inicial 2379/1476/62,04 %. Bloque 1 (casos 1–15) agotó respuesta; último caso visible 4, Tecnologías, 1766/1162. Cierre normal sin guardar selecciones. Único reintento falló en reapertura previa al caso 1. Cero de 77 certificados en esta ejecución; las 77 regresiones independientes H008 siguen PASS y no sustituyen el control. Faltan prueba visual completa y cuatro capturas; no se fabricaron. Bloqueos conservados: {', '.join(native['bloqueos_no_borrados'])}.
- B: R20 no tiene gráficos ni selectores de validación; tablas con autofiltro, sin auxiliares gráficos de relleno. Original 70baf95a… intacto, sin copia v2 innecesaria.
- B/C/E: H006 sí tenía tres gráficos de selectores con rangos fijos. Copia `{copy.name}` en ENTREGA_RETENCION_20261031, hash `{sha(copy)}` igual a privada. {count} celdas originales idénticas; cuatro gráficos conservados, tres corregidos. La serie histórica no conectada a selectores conserva cronología. QA nativo E; no reemplaza original.
- D/C: reglas 1.3.11, commit `{rh}`; validar PASS_CON_PENDIENTES_E (cero errores, advertencias históricas). Dos skills Codex sincronizadas con respaldo privado y hashes iguales; dos variantes Claude regeneradas, sin instalación Claude.

## H008 y límites conservados

H008 publicado por separado en `{git('rev-parse','HEAD')}`: QA estructural repetido 13/13 y privacidad PASS, 41 rutas explícitas. R19 continúa BORRADOR; no se adjudican los 99, no se reabre R09 ni se certifica reproducción cruda integral. H001, R20, v20, bases y denominadores intactos.

## Pendiente exacto / reapertura

Con Excel estable: bloque 1 desde caso 1, luego bloques 2–6; años, sectores, jornadas y diez combinaciones; cuatro capturas de gráficos agregados; mismo control sobre H006 v2. Sin nueva iteración en este turno. V26 y H006 v2 permanecen candidatas; no se publican los XLSX.

Archivos autorizados H009: los enumerados en LISTA_PUBLICACION_H009.json; sólo esta carpeta, PLAN_FASES_HITOS.md y los dos mapas. Los 25 cambios ajenos se cotejan por estado y hash en QA_PUBLICACION_H009.json.
'''
 (o/'INFORME_H009.md').write_text(report)
 plan=base/'PLAN_FASES_HITOS.md';backup=o/'PLAN_FASES_HITOS_v3_20261030.md'
 if not backup.exists():shutil.copy2(plan,backup)
 text=backup.read_text().replace('· v3','· v4',1).replace('H008 genera V25 candidata; sin publicación y sin modificar V24.','H008 publicado con límites; H009 genera V26 candidata con QA nativo E. V24 y V25 intactas.',1)
 text+='\n## H009 · estado v4\n\nDiez gráficos de V26 con auxiliares compactados, nombres dinámicos y orden D. QA estructural PASS, 244190 valores sin diferencias; QA nativo 77 casos y revisión visual E después del único reintento. H006 v2 corrige tres gráficos, también candidata con QA nativo E. R20 intacto. H008 publicado con límites; la Fase 6 integral sigue pendiente. Reproducción y requisitos exactos: h009_20261030/REPRODUCIR.md e INFORME_H009.md. No confundir publicación de evidencia con validación nativa completa.\n'
 plan.write_text(text)
 mp=r/'docs/MAPA_RESULTADOS_GOBERNADOS.json';m=load(mp);assert not any(x['id']=='R27' for x in m['resultados'])
 row={'id':'R27','pregunta':'¿Qué corrige H009 en los gráficos y qué QA falta?','resultado_clave':'CANDIDATA_CON_QA_NATIVO_E: V26, 10 gráficos corregidos; 244190 valores sin diferencias; 13 gráficos/37 tablas conservados. 77 casos nativos y revisión visual pendientes tras único reintento. H006 v2 candidata; R20 intacto.',
 'archivo':str((o/'INFORME_H009.md').relative_to(r)),'hoja_o_seccion':'Resultados y pendiente exacto','sha256':sha(o/'INFORME_H009.md'),'commit':'PUBLICACION_H009; base '+git('rev-parse','HEAD'),'script_productor':str((o/'construir_v26.py').relative_to(r)),'clase':'D orden; B/C evidencia e implementación; E QA nativo','fecha_resultado':'2026-10-30','no_recalcular_salvo':'Excel estable para completar QA delimitado o corrección demostrada de presentación; no recalcular H001/R19 ni adjudicar pendientes.','limites':'Publicación de scripts/informes no certifica 77 selectores ni cuatro capturas. Libros privados; sin cambios de cifras.'}
 m['resultados'].append(row);write(mp,m)
 md=r/'docs/MAPA_RESULTADOS_GOBERNADOS.md';text=md.read_text().replace('## Mapa (25 resultados)','## Mapa (27 resultados)')
 line='| R27 · '+row['pregunta']+' | '+row['resultado_clave']+' | '+row['archivo']+' | '+row['script_productor']+' | '+row['commit']+' | '+row['sha256']+' | '+row['clase']+' | 2026-10-30 | '+row['no_recalcular_salvo']+' |\n'
 text=text.replace('\n## Límites por resultado','\n'+line+'\n## Límites por resultado',1);md.write_text(text)
 print(json.dumps({'documentado':True,'V26':q['sha256_v26'],'H006_v2':sha(copy),'reglas_commit':rh}))
if __name__=='__main__':main()

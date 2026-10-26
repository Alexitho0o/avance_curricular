# Fase 5/6 — QA nativo de V19
## Resultado
**B/C/E — NO APROBADA PARA ENTREGA.** Excel abrió la copia sin aviso de reparación; se solicitó fullRebuild, se guardó con Excel y se comprobaron sus valores. La conciliación numérica pasa en el alcance probado; la visualización dinámica falla. No se ejecuta fase 6.

## Alcance y preservación
**D —** Retención IPSS 162, cohortes 2022–2025 y seguimiento interno T1/T2/T3 hasta 2026. Se reutilizan las fases 1–4. Sin modificar fuentes, diccionario, bases, denominadores ni V19 original. Sin commit/push.
**B —** Rama feature/ire-2026, HEAD antes/después 8e2fb85bb8703758d6878681c9e2a29016e60c63. El cambio previo de PROYECTO_IPSS.json se conserva.
**B —** Las 13 rutas del control de preservación de fase 1 mantienen sus hashes; V19 original conserva daae975e42698dfb63bb3877e63bd8b7bdc499c50da05092d21772038ef457ee.
**B —** Copia privada nativa: /Users/alexi/.local/share/ipss/trazabilidad_integral_fase5_20261025/RETENCION_IPSS_V19_PRUEBA_EXCEL_FASE5.xlsx. No se incorpora a Git: contiene detalle individual.
**B —** Única diferencia de constante tras guardar: hoja37 C19 pasó de texto «367 » a «367»; no hay cambios numéricos ni pérdida de fórmulas. Es normalización observada de Excel, no corrección de datos.

## Controles
| Clase | Control | Resultado | Evidencia |
|---|---|---|---|
| B/C | Agregaciones COUNTIFS/SUMIFS recalculadas independientemente desde detalle | 1.976 controles, 0 diferencias | CONTROLES_AGREGACION.json; conciliar.py |
| B | Valores numéricos V19 frente a copia guardada por Excel | 0 diferencias | CONCILIACION_PRE_FILTROS.json, regenerada al cierre |
| B | Fórmulas que desaparecen | 0 | Mismo archivo |
| B | Errores de fórmula en Excel | 0 celdas de error en 57 hojas | EVIDENCIA_EXCEL_NATIVO.json |
| B/E | Estado de cálculo informado por host | Automatic / Pending, no Done | No certificar ausencia de cálculo pendiente solo por los valores |
| B | Gráficos conservados | 13 objetos | Inventario nativo y ZIP |
| B/C | Cuatro selecciones verificadas | Coinciden 8 bloques + KPI hojas12/13 | Tabla siguiente |
| B/C | Autofiltro Sector de tabla T_H13_B | Tecnologías 1.766/1.162; tasa 65,7984% | SUBTOTAL109, hoja13 H136:J136 |
| B/E | Prueba exhaustiva | 4 de 77 configuraciones con resultado capturado; 73 no certificadas | Lote inicial agotó tiempo, no se cuenta como aprobado |

## Pruebas de selección
**C —** Denominador/numerador esperados provienen de hoja9 granular, calculados independientemente en conciliar.py. Cada fila coincide en los ocho bloques del panel y los KPI enlazados de hojas12 y13.
| Clase | Selección | Estudiantes | Retenidos | Tasa |
|---|---|---:|---:|---:|
| B/C | Cohorte2024 / Tecnologías / Todas | 497 | 299 | 60,16097% |
| B/C | Acumulado / Administración y Comercio / Administración Pública | 70 | 33 | 47,14286% |
| B/C | Cohortes2022+2023 / Todos / Todas | 671 | 482 | 71,83308% |
| B/C | Acumulado2022–2025 / Todos / Todas | 2.379 | 1.476 | 62,04288% |

**B —** Los selectores se restauraron a Acumulado2022–2025 / Todos / Todas y se retiró el filtro temporal de la tabla13 antes de guardar. El filtrado de la tabla13 es local; no se interpreta como selector global.

## Defecto que impide aprobar
**B —** Imagen nativa de hoja14 B4:J33 con Tecnologías2024: tablas muestran497/299=60,2%; gráfico1 sigue mostrando73,4%,70,5%,58,4%,58,1% y categorías1–4; gráfico2 muestra65,8%,51,9%,46,7% y categorías1–3. No coincide con la selección.
**B/C —** En el ZIP ORIGINAL V19, chart4.xml a chart11.xml contienen referencias de serie «label 0», «categories», «0» y, en chart6, «label 1»/«1», en lugar de rangos de celdas. No se atribuye el defecto al guardado de esta fase. Referencias completas en REFERENCIAS_GRAFICOS_V19.json.
**E —** Siguiente reparación acotada: reconectar esos ocho gráficos a los rangos dinámicos correspondientes, preservando estilos, y repetir filtros/visualización en una nueva copia. No fue aplicada en esta auditoría ni se alteraron los gráficos originales.
**E —** Quedan sin certificar los73 escenarios restantes y los54 patrones complejos de agregación del panel que no cubre el evaluador estático. Las pruebas nativas parciales no los sustituyen.

## Pendientes sustantivos conservados
**B/E —** Hoja57 concilia2.854 contextos:2.742 documentales,13 internos aprobados,99 pendientes;24 pendientes corresponden al foco de varias versiones. Son contextos, no99 personas.
**B/E —** Las3.520 posiciones sin contexto de seguimiento no se convierten en deserciones.
**E —** Se conservan las66 renuncias agregadas sin nómina individual, las diferencias de alcance persona/matrícula y los denominadores específicos de2026, incluido alcance545. No se armonizan silenciosamente.
**C —** Actividad académica, matrícula vigente, retención anual y cobertura de código son indicadores distintos. Conciliar aritmética no transforma actividad en vigencia histórica ni prueba aceptación SIES.

## Reanudación
**C —** Reanudar en Fase5/H3: reparar referencias de gráficos en copia nueva; luego completar matriz de filtros y verificar imágenes. No repetir conciliación de fuentes si sus hashes permanecen iguales. Fase6 permanece pendiente.

### V20 — corrección de ocho gráficos y QA de reapertura

La copia V20 quedó guardada en el Escritorio con SHA-256 `b9dd851da572d48635815ddb0649bf20d92b14e42cec3509898dff6a53d132f7`. Excel la abrió nuevamente sin mostrar reparación de contenido y el ZIP pasa `unzip -t`.

Los ocho gráficos de `14_Vistas_Ejecutivas` usan rangos auxiliares dinámicos en la misma hoja: `DA:DX`. Se verificaron las referencias XML de charts 4–11. No se cambiaron las tablas, las fórmulas de agregación, las bases ni los denominadores.

Las cuatro configuraciones de filtro ya certificadas nativamente en V19 se conservaron como evidencia de regresión: 2.379/1.476; 70/33; 671/482; y 497/299, respectivamente. El control independiente mantiene 1.976 agregaciones sin diferencias. Posteriormente se ejecutaron los 77 casos de `CASOS_FILTROS.json` en bloques de 15 (último de 17): 77/77 coincidencias y 0 diferencias. Los selectores quedaron restaurados al escenario base y la certificación final de V20 pasa a `PASS`.

# Origen de la regresión · B/C/E

| Versión | Ceros al filtrar | Orden | Evidencia |
|---|---|---|---|
| AUDITADO_ENTREGA 22-10, 20fe8438… | Auxiliar CW7:CW9 consecutivo solo >0; CV recupera modalidad; no certifica gráfico | Cachés ordenadas en algunos desgloses; no prueba selección viva | REVISION_ANTECEDENTES_ENTREGAS.json: ocho gráficos con referencias rotas «label 0», «categories» |
| V14–V18 | No acreditado por matriz de correcciones | No acreditado | fase1/correcciones/MATRIZ_CORRECCIONES_V14_V18.md: cambios de tasas, notas y esquemas; no certifica simultáneamente compactación y orden |
| V19 | Referencias rotas | No certificable | fase5/REFERENCIAS_GRAFICOS_V19.json; INFORME_FASE5.md |
| V20 / V21 / V24 / V25 | Ocho rangos fijos DA:DX incluyen filas vacías | Referencias directas, sin compactación u orden dinámico en el rango final | INVENTARIO_GRAFICOS.json; fase5/patch_v21_chart_helpers.py |
| V26 candidata | Nombres INDEX de longitud dinámica; NA() solo para series ausentes | COUNTIFS con desempate, INDEX/MATCH; tasa total para modalidades y SIES para comparación | CONFIG_GRAFICOS.json; QA_H009.json. Prueba completa en Excel E |

E: no se encontró evidencia de una versión anterior con compactación, referencias válidas y orden funcionando simultáneamente. Se confirma la pérdida del mecanismo auxiliar al pasar a referencias directas, pero no una regresión desde un producto completamente correcto. No se inventa esa versión. Se revisaron versiones disponibles del Escritorio, la copia auditada privada y los manifiestos/informes fase 1, 4 y 5.

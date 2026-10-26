# Documentacion del repositorio

- [Continuidad y año de ingreso a la carrera](continuidad_trayectoria_20261016.md):
  regla interna por RUT/CODCLI; ANOINGRESO puede ser heredado del técnico.

- [Versiones por cohorte sobre el cruce existente](resultados_versiones_por_cohorte_20261016.md):
  duración total, ANOINGRESO y primer año de oferta; sin rehacer agrupaciones por nombre.

- [Fase B: evaluación histórica de equivalencias](resultados_fase_b_equivalencias_historicas.md):
  513 candidatos evaluados, concordancia anual oferta/MRUN y brechas por código/plan.

- [Repositorio único y reglas de negocio](unificacion_proyectos_y_reglas_negocio_20261015.md):
  módulo Caracterización, recursos SIES comunes y reglas internas/formales por proceso.

- [Gobernanza operativa](GOBERNANZA_REPOSITORIO.md).
- [Catalogos SIES por ano](CATALOGOS_SIES_POR_ANIO.md): contrato, fuentes,
  consultas y regeneracion aislada de oferta 2026/2027.
- [Estado al 13-10-2026](ESTADO_CATALOGOS_Y_CONCILIACION_20261013.md):
  cobertura inicial de equivalencias y conciliacion de matricula.
- [Revision 6047 y DatosAlumnos](REVISION_EQUIVALENCIAS_6047_20261013.md):
  cobertura vigente, detalle de las 52 originales e integracion en Caracterizacion.
- [Modalidad independiente del codigo SIES](RESOLUCION_MODALIDAD_INDEPENDIENTE_2027.md):
  revision vigente, dos estados de resolucion y cobertura actualizada sin elegir versiones.
- [Revision de los 52 registros pendientes](REVISION_52_REGISTROS_PENDIENTES_2027.md):
  14 codigos internos, fuentes revisadas, candidatos no aplicados y respaldo faltante.
- [Nombre de carrera y Sector IPSS en MU2026](ENRIQUECIMIENTO_CARRERA_SECTOR_MU2026.md):
  enriquecimiento del libro analítico por clave completa, sin modificar las cargas.
- [Diccionario histórico SIES y UMAS 2007–2026](DICCIONARIO_HISTORICO_SIES_UMAS_2007_2026.md):
  Excel independiente de consulta, equivalencias, ejemplos y trazabilidad de versiones.
- [Fase 1: fuentes y claves históricas](fase_1_inventario_versiones_historicas.md):
  inventario verificado, uniones, cobertura y brechas del cruce SIES–UMAS.
- [Fase 2: historia observada MRUN](fase_2_historia_observada_mrun.md):
  contrato y reconstrucción de códigos, versiones, cohortes y cambios entre años.
- [Fase 3: oferta histórica SIES](fase_3_oferta_historica_sies.md):
  reconstrucción 2010–2026, códigos sin matrícula, cotejo anual y brecha 2007–2009.
- [Fase 4: planes y asociaciones UMAS](fase_4_planes_asignaciones_umas.md):
  estructura de planes, enlace interno de reportes y límites de asignación temporal.
- [Fase 5: maestro de equivalencias](fase_5_maestro_equivalencias.md):
  cobertura completa de las fuentes disponibles, candidatos separados de reglas
  efectivas y resolvedor aislado con año/período/régimen explícitos.
- [Fase 6: piloto y validación del universo](fase_6_piloto_validacion_universo.md):
  consultas sobre todos los contextos disponibles, conciliación de pesos,
  excepciones y límites para una futura integración.

- [Fase 7: integración de consumidores](fase_7_integracion_consumidores.md):
  interfaz histórica compartida, paquete portable y comprobación de paridad
  entre avance_curricular y CARACTERIZACIÓN, conservando casos pendientes.
- [Fase 8: Excel definitivo y control de cambios](fase_8_excel_diccionario_gobernado.md):
  diccionario de consulta con ocho criterios UMAS, historia SIES, candidatos,
  ejemplos y respaldo de la edición anterior.
- [Hipótesis de origen y versiones: análisis y plan](analisis_hipotesis_oferta_historica_20261015.md):
  contraste del CSV nacional completo, cambios de sector de Alexi y tres fases
  propuestas; no modifica el diccionario ni habilita equivalencias.

Los modulos nuevos son `common/catalogos_sies.py`,
`scripts/generar_catalogos_sies_por_anio.py`, `scripts/consultar_catalogo_sies.py`
y `scripts/conciliar_matricula_publicada.py`; la revision y copia portable usan
`scripts/revisar_equivalencias_6047.py` y `scripts/exportar_catalogo_caracterizacion.py`.
`scripts/revisar_modalidad_catalogo_2027.py` versiona la politica posterior.
`scripts/auditar_pendientes_catalogo_2027.py` documenta pendientes sin promover candidatos.
Pruebas focalizadas en `tests/`.
Son auxiliares: no sustituyen los comandos ni el motor oficial MU2026.

- [Diagnóstico de cohortes por carrera y muestra completa CILOG](diagnostico_cohortes_cilog_20261016.md).

- [Diagnóstico de vigencia anual y sucesión de códigos](diagnostico_vigencia_oferta_20261016.md).

- [Análisis MRUN–UMAS recuperado de Caracterización y continuación por corte](recuperacion_cruce_mrun_umas_20261016.md).

- [Prueba de 500 personas anteriores a 2023 con reportes independientes](prueba_500_enlaces_historicos_20261016.md).

- [Hipótesis de enlace conjunto MRUN–UMAS: cohortes, 500 casos y restricciones](hipotesis_enlace_conjunto_20261016.md).

- [Reconstrucción de presencia anual UMAS y contraste histórico con MRUN](reconstruccion_presencia_anual_20261016.md).

- [Capa demográfica: consistencia, contraste histórico y control de propuestas](capa_demografica_20261016.md).

- [Estado consolidado del plan y próximos hitos del diccionario](estado_plan_diccionario_20261016.md).

- [B4: matriz académica por cohorte, cobertura y evidencia](b4_matriz_academica_20261016.md).

- [B5: reglas históricas observadas y validación reservada](b5_reglas_historicas_20261016.md).

- [C1: nueva edición del diccionario, controles y reproducción](c1_edicion_diccionario_20261016.md).

- [C2: consumo común, paridad y cierre técnico](c2_consumo_comun_20261016.md).

- [Plan de cierre D1–D4: análisis, conclusiones y próximos pasos](plan_cierre_analisis_sies_umas_20261016.md).

- [D1: inventario conciliado y criterios de cierre](d1_inventario_criterios_20261016.md).

- [D2: investigación de excepciones y continuidad CILOG](d2_excepciones_20261016.md).

- [D3: reglas deterministas de uso y abstención, cobertura y consumo común](d3_reglas_validacion_20261016.md).

- [D4: conclusiones finales, diccionario con D3 y agenda de ratificación](d4_conclusiones_cierre_20261016.md).

- [Confirmación de oferta 6047 y cobertura 2027 P1 con DatosAlumnos 12023](confirmacion_oferta_2027_12023_20261016.md).

- [Resumen ejecutivo anual y preparación de códigos/planes 2027](resumen_ejecutivo_oferta_2027_20261016.md).

- [Recuperación íntegra del CSV 6047 y corrección del registro de respaldo](recuperacion_oferta_6047_20261016.md): resuelve la falta de copia completa registrada en la entrega ejecutiva; conserva las 161 filas y 51 columnas originales.

- [Control de cambios de VIG MU2027 y estudio de envíos 2026](control_cambios_vig_mu2027.md): versiones, responsable, fecha/hora, alertas y revisión interna con bloqueo de carga normativa pendiente.

## Consulta común de códigos SIES para seguimiento (2026-10-23)

[Códigos por persona, expediente y período](DICCIONARIO_SIES_SEGUIMIENTO.md): reutiliza evidencia MU y decisiones aprobadas; excepciones separadas, sin cambiar motores ni denominadores.

# V10 — prueba por cohorte y admisión

B/C · Se corrigió el eje temporal: la persistencia de estudiantes antiguos V1 no refuta una hipótesis sobre ingreso original. La prueba anterior por año observado no sirve para refutar esa hipótesis. Esta ejecución prueba los campos de ingreso disponibles; **no logró reconstruir una fecha efectiva de ingreso al plan acreditada**. Por ello no se presenta como prueba definitiva de la hipótesis corregida.

## Resultado comparable

C · V9 y V10 mantienen 3.094 observaciones internas pendientes, 1.751/5.901 personas (29,67%). Nuevas personas completamente resueltas:0; parcialmente:0. Se preservan los119 enlaces internos FCU2026 de V9 y los cierres documentales V7. El indicador documental permanece separado:1.838 personas/3.213 observaciones. Las24/63 dimensiones pendientes originales no se recalifican.

C · En el foco hay2.695 candidatos únicos condicionados; los399 restantes son32 fechas ausentes/múltiples,203 sin perfil,19 sin oferta compatible para nuevos,94 con alternativas y51 sin grupo. Candidato único no equivale a asignación probada ni a envío SIES. Cada fila privada conserva los campos, candidatos, localizadores y condición faltante.

## Validación retrospectiva sin código objetivo para seleccionar

C · Se evaluaron21.561 observaciones documentales con tres fechas alternativas. El objetivo se compara después de seleccionar candidatos por grupo/familia, duración/tipo y año de ingreso registrado, filtrando oferta «Vigente con estudiantes nuevos». Los grupos gobernados preexistentes pueden compartir fuentes con las asignaciones originales: no es validación externa independiente. Modalidad de oferta se conserva como atributo; no se validó una modalidad individual efectiva del plan con el campo escolar DA. No se afirma coincidencia individual completa de modalidad.

| Fecha registrada — regulares | Aciertos | Diferencias | Empates | Sin fecha única | Sin oferta compatible |
|---|---:|---:|---:|---:|---:|
| DA ANOINGRESO |15.069|1.497|1.040|2|218|
| MU ingreso actual |15.029|1.494|1.044|2|257|
| MU ingreso origen |14.214|1.417|978|723|494|

Cada fila suma17.826 observaciones. Personas no aditivas y otros grupos están en RESULTADO.json y Excel. Para continuidad:173 observaciones/42 personas; DA/origen excluidos por no acreditar ingreso propio al programa de continuidad. MU actual deja173 sin oferta compatible, lo que **no prueba que no exista oferta o matrícula**: puede ser la fecha equivocada para ese programa. Otros3.562 registros tienen tipo no único o perfil/grupo insuficiente.

B · No hay reingreso positivo acreditado en los campos consultados; cero/vacío no prueba inexistencia de retornos. Tampoco hay historial acreditado de cambios de plan. No se calculan aciertos por cambios/reingresos conocidos porque ese estrato no puede identificarse con estos datos.

C · Añadir vacantes positivas como sensibilidad mantiene15.029 aciertos,1.494 diferencias,1.044 empates y259 sin candidato/fecha entre17.826. No es regla nueva ni evidencia de ausencia por vacantes0.

## Ejemplo que exige revisar la fecha o transición, no descartar la hipótesis

B/C · IETMREOL/J4, año observado2023 y MU ingreso actual2022:309 observaciones predicen I162S2C3J4V1 mientras MU documenta I162S2C3J4V2. Otras238 presentan esa diferencia en2022/cohorte2022. La oferta2022 muestra ambas versiones regulares de8 semestres, no presenciales: V1 admite nuevos y tiene90/45 vacantes; V2 figura sin nuevos y0/0 vacantes. Requisito Educación Media y0 semestres reconocidos en ambas. El código observado no se reemplaza.

Localizador: data/versiones_historicas_sies_umas/fase_b_20261015/perfiles_sies_anuales.json, registros CSV134978/134979. Maestro fase5: oferta_anual2022 de esos códigos; fuente original TSV351/352, filas XLSX130914/130915. Año Inicio formal V1=2017, primera aparición disponible de oferta=2018; V2 inicioformal2019. No confundir comienzo formal, primera oferta disponible, primera matrícula y retorno.

E · La diferencia puede requerir historial de asignación/migración del plan o edición efectiva de oferta; esas causas no están demostradas. Las fechas DA/MU pueden corresponder a otro hito. No se afirma que V2 estuviera mal informado.

## Fuentes y reglas realmente utilizadas

B · FUENTES_HASHES.json registra rutas exactas y SHA256. Se reutilizaron índices privados V3/V8/V9, grupos_existentes.json del16oct, maestro.json fase5 y la equivalencia manual FCU2026. Se releyeron cuatro MU ya identificadas: MAT_IP_CIISA_2019.xlsx/MAT_2019,2020,2021 y BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx/BASE_RETENCION_MU. Campos: documento/DV, código/familia, año informado, MM_ANIO_ACTUAL/MM_ANIO_ORIGEN o ANIO_ING_ACT/ANIO_ING_ORI, REINCORPORACION. El detalle guarda ruta/hoja/fila. DA aporta CODCLI,plan,carrera,jornada,ANOINGRESO,ANOMATRICULA con corte no acreditado. Los perfiles son de grupo; no se eleva esa procedencia a perfil individual histórico.

D · Reglas consultadas: docs/fase_4_planes_asignaciones_umas.md (corte no retroactivo y contexto CODCLI/plan); docs/continuidad_trayectoria_20261016.md y common/continuidad_trayectoria.py (fecha propia de continuidad); common/versiones_por_cohorte.py (propuesta por intervalo no habilitada y sin acreditación CODPESTUD). La equivalencia manual existente FCU2026 conserva alcance2026, no se extiende atrás. No se exige prueba de envío como condición universal de enlace interno; sí falta demostrar el enlace temporal expediente-plan para esta vía concreta.

## Qué falta para aplicar la hipótesis

E · Para los2.695 candidatos: registro de asignación del CODPESTUD al CODCLI con fecha efectiva y fuente del ingreso a ese programa; si hubo retorno/migración, acto o historial que determine continuidad/cambio. Para94 empates: atributo discriminante del plan o código individual de admisión; duración/tipo no discrimina. Para32 fechas: campo de ingreso propio único;203 perfiles y51 grupos: perfil del plan y familia acreditados;19 sin oferta: edición/cobertura de admisión del año pertinente o corregir fecha propia con respaldo.

D/E · No se recomienda aprobar en bloque2.695. Una nueva regla eventual sería asignar código interno cuando fecha efectiva del plan y oferta de admisión sean concordantes, perfil individual compatible y candidato único; continuidad/retorno requieren tratamiento explícito y transiciones acreditadas. Alcance candidato2.695 registros, **no cantidad de cierres garantizados**. Antes de pedir aprobación, resolver el ejemplo C3/J4 con historial efectivo y repetir la validación. No corresponde aprobar el escenario501 ni declarar cerrado el puente.

Fuentes, canon, tasas, denominadores, rama y entregas anteriores intactos. No commit/push/uploads. El desfase T3 histórico se conserva y documenta en QA_ENTREGA.json. Los13 gráficos se preservan; nuevas hojas presentan pruebas estáticas, sin recalcular tasas.

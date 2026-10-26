# Plan de reducción de brecha UMAS–SIES

Fecha: 2026-10-22. **PENDIENTE_APROBACION_GOBERNANZA**. Diagnóstico y plan; no modifica Excel, fuentes, reglas operativas, denominadores ni tasas. A = regla oficial; B = observado; C = cálculo; D = decisión interna; E = pendiente/hipótesis. No se introduce ninguna regla A.

## Qué significa 38,10% (C)

El indicador existente es **(11 múltiples/baja cobertura + 13 sin match) / 63 dimensiones = 24/63 = 38,095238%**. Cada dimensión es carrera interna + sede + jornada entre las ambigüedades seleccionadas del catálogo 2027. No son todas las carreras, 63 planes, 63 estudiantes ni la brecha de retención IPSS–SIES.

Las 39/63 restantes son **propuestas internas por predominio**, no equivalencias acreditadas ni aprobadas. El método original exige predominio >=90% y al menos tres incidencias en el código predominante; no verifica por sí mismo plan efectivo, temporalidad, tipo/duración ni conciliación MU. Por ello 61,90% no es cobertura oficialmente resuelta. Los conteos están correctamente reproducidos para su grano original, pero la etiqueta `personas_matched` era imprecisa.

Separar tres indicadores, sin sustituir retrospectivamente el original:

1. **Brecha descriptiva por dimensión:** conservar 24/63 como línea base; cada dimensión debe mantener su historia de estado. Una dimensión con varios contextos no se declara resuelta porque se resuelva uno.
2. **Cobertura de personas:** definir universo, año y matrícula/plan. Ensayo local: 3.978 de 6.181 personas de las carreras presentes en las 63 dimensiones tienen al menos un match de candidato en el mismo año (64,36%). Esto no acredita todos sus contextos ni equivale a personas únicas de MU. No sumar celdas de personas entre años, planes o versiones. No comparar ese 64,36% con 61,90%.
3. **Acreditación y aprobación:** contar aparte relaciones documentadas, propuestas D y decisiones aprobadas. Esta ejecución no aprobó nuevas equivalencias. El estado pendiente de las 63 en la auditoría es una puerta de validación, no evidencia de que sus 63 vínculos sean erróneos ni una nueva brecha del 100% comparable con 24/63.

## Dos discrepancias ya explicadas (C)

Se localizó `/tmp/formalize_majority.py`, preservado aquí como `metodo_original_referencia.py`. **Solo referencia: no ejecutarlo**, pues escribe sobre los derivados anteriores. Su lógica de lectura y agregación se reprodujo aisladamente, con coincidencia exacta en **las 63 distribuciones**.

| Método | Grano de conteo | Tiempo y filtros |
|---|---|---|
| Original, `drop_duplicates(['rutkey','PLAN_DE_ESTUDIO','codigo_unico'])` | Persona–plan–código; suma incidencias entre códigos | No lee ANO, PERIODO, CODCLI ni TIPO_DOC; cruza todos los años por carrera y candidatos |
| Auditoría `validacion_local_v1/validar.py` | RUT/DV distintos por código en resumen histórico; grano separado carrera/plan/año/período/código en Fase 1 | Resumen histórico también cruza años; agregado temporal exige mismo año y TIPO_DOC=R |

| Dimensión S2/J4, código V2 | Original reproducido | Persona–plan con llave exacta | Personas distintas | Explicación |
|---|---:|---:|---:|---|
| IECIRE / I162S2C1J4V2 | 23 | 23 | 22 | Una incidencia persona–plan adicional sobre el total de personas |
| IECIREOL / I162S2C1J4V2 | 243 | 243 | 241 | Dos incidencias persona–plan adicionales sobre el total de personas |

No son tres personas perdidas ni un efecto del filtro temporal: ambos resúmenes históricos usan todo el intervalo. Tampoco lo explica excluir pasaportes: la llave exacta con filtro R reproduce 23/243 al conservar el plan. El normalizador original elimina cualquier carácter no numérico del cuerpo; el nuevo normaliza separadores, ceros iniciales y valida la forma. Se encontró una fila PROMEDIOS con representación normalizada diferente, pero no explica estas dos discrepancias: la prueba cambiando únicamente el grano reproduce ambas. No se modificó el Excel para actualizar su nota pendiente; hacerlo correspondería a una entrega posterior autorizada.

**Corrección técnica propuesta:** conservar `personas_unicas`, `incidencias_persona_plan` e `incidencias_persona_codigo` por separado. Fijar explícitamente el denominador del predominio antes de recalcularlo. Una persona puede participar en varias versiones: su repetición es evidencia de trayectoria o inconsistencia a investigar, no un duplicado eliminable sin contexto.

## Evidencia recuperable: no partir de cero (B/C/D)

`data/versiones_por_cohorte/20261016/grupos_existentes.json` conserva perfiles y procedencia: **31 de las 39 propuestas** tienen un perfil único de duración/tipo en el grupo existente. Esto corrige la impresión excesiva de que toda duración/tipo debe obtenerse de nuevo. Es perfil de programa gobernado, no acreditación del plan individual ni permiso para reasignar históricos.

Reutilizar las agrupaciones por códigos, no volver a emparejar por nombre. `docs/resultados_fase_b_equivalencias_historicas.md` permite acreditar un vínculo con documentación explícita y temporal sin exigir inventar todos los atributos secundarios. `docs/resultados_versiones_por_cohorte_20261016.md` documenta duración, tipo e inicio de oferta, pero el intervalo es hipótesis D/E. Para continuidad prevalece `docs/continuidad_trayectoria_20261016.md`: ANOINGRESO puede ser heredado del técnico; requiere fecha de la carrera específica. No inferir inicio del año escrito en el plan ni de NIVEL.

## Las 11 múltiples o de baja cobertura (B/C/E)

Todas son sede 2. Los porcentajes anteriores usan incidencias persona–código, no necesariamente personas distintas. Los datos por año que siguen son diagnósticos, no asignaciones.

| Carrera/J | Evidencia concreta | Vía de resolución y prueba necesaria |
|---|---|---|
| ICRE/J2 | V1:3, V4:22; 22 personas únicas; 88%. En 2025 coexisten V1:3/V4:10 para ICRE20241. Perfil no unívoco. | Revisar las tres personas multicódigo por matrícula y envío MU2025; recuperar perfil documental. Separar año solo no resuelve 2025. |
| IINF/J1 | V1:9/V2:46; 49 personas; 83,64%. Mismo plan: 2025 V1:7/V2:21; 2026 V1:2/V2:30. Perfil regular 8 semestres existente. | Reutilizar perfil; examinar coexistencia y fechas efectivas de matrícula/plan. No escoger V2 solo por mayoría ni borrar V1. |
| IINF/J2 | V1:8/V4:54; 56 personas; 87,10%. 2025 V1:8/V4:20. Grupo previo propone continuidad 4/5 semestres, mientras candidato predominante observado es regular. | Prioridad alta: resolver contradicción de perfil y alcance de código interno con evidencia institucional; aplicar lógica de continuidad solo si se confirma tipo. No promover por 90%. |
| NCONRE/J2 | Dos personas históricas; solo una coincide mismo año 2022. Perfil no unívoco. | Recuperar historia anterior a 2022 y perfil. No sumar años para fabricar n>=3. Documento explícito podría acreditar una relación por vía distinta, conservando el control estadístico. |
| NINFREOL/J4 | Una persona histórica; cero coincidencias mismo año. Perfil no unívoco. | La identidad en años posteriores no prueba el plan histórico; buscar matrícula/plan y MU del período de actividad. |
| TCRE/J1 | Una persona con V1 histórico; ningún match mismo año del plan TCRE20241. Perfil regular 5 existente. | Revisar jornada y matrícula contemporánea; no trasladar el código antiguo de esa persona al plan 2024. |
| TCRE/J2 | V1:3/V2:11; 11 personas; 78,57%. 2025 V1:2/V2:5. Perfil regular 5. | Reutilizar perfil; resolver coexistencia MU2025 mediante matrícula/plan y fuente de envío. |
| TPCRE/J1 | Una persona; match 2022 de TPCRE20191 con V2. Perfil regular 5. | Evidencia individual válida solo para ese contexto; recuperar más cobertura o documento de equivalencia, sin extrapolar a todos los planes. |
| TPCREOL/J4 | Una persona histórica; cero matches contemporáneos. Perfil regular 5. | Buscar períodos originales y asignación de plan; no acreditar con la trayectoria posterior. |
| TTMRE/J1 | V1:4/V2:5; seis personas; 55,56%. En 2022, plan 20191→V2:2 y plan 20211→V1:4; plan 20211→V2:3 en 2023. | Separar planes mejora diagnóstico; comprobar cambio efectivo y MU2022–2023. No asumir que el texto 20211 es fecha de vigencia. |
| TTMRE/J2 | V1:7/V2:21; 25 personas; 75%. Plan 20191→V2:16 en 2022; plan 20211→V1:7 en 2022 y V1:2/V2:4 en 2023. | Separar plan y año; persiste mezcla en 2023 que exige historia individual, no simple regla global de mayoría. |

## Las 13 sin match (B/C/E)

Son ausencia de coincidencia en **los candidatos de esa dimensión**, no necesariamente ausencia de la persona en MU. La cobertura PROMEDIOS por carrera no permite atribuir por sí sola todas sus personas a una jornada/sede.

| Carrera/J | Evidencia local | Acción específica |
|---|---|---|
| ICRE/J1 | Actividad 2023–2026; 255/262 personas aparecen en MU en otros códigos; cero en candidatos J1. | Revisar JORNADA de cada matrícula y familia histórica gobernada. Posible dimensión sin actividad pertinente, aún no demostrada. No trasplantar J2/J4 a J1. |
| IETMRE/J1 | Actividad 2019–2025; 67/140 aparecen en MU, cero en candidatos J1. | Separar período anterior/posterior a 2022 y jornada de matrícula; revisar equivalencias heredadas por código. |
| NAUTRE/J2 | 2019–2021, siete personas, ninguna en MU actual. | Requiere matrícula comparable anterior a 2022; el respaldo de planes registra dos planes, no identidad SIES. |
| NECIRE/J2 | 2019–2020, cuatro personas, ninguna en MU. | MU/historia individual 2019–2020; cuatro planes en respaldo no equivalen a asignaciones. |
| NETMRE/J2 | 2019, dos personas, ninguna en MU. | Fuente de matrícula 2019 y jornada acreditada; tres planes en respaldo. |
| NETMRE/J4 | Mismas dos personas de carrera y año que J2. | Separar jornadas con fuente de matrícula; no sumar como cuatro personas ni asumir actividad en ambas. |
| NICCRE/J2 | 2019–2021, nueve personas sin match MU. | Recuperar matrícula de esos años y plan efectivo. |
| NICCREOL/J4 | 2020–2021, diez personas sin match MU. | Recuperar matrícula 2020–2021; respaldo registra un plan. |
| NICIRE/J2 | 2019, una persona sin match MU. | Fuente 2019 o documento explícito; no bajar n mínimo para producir propuesta. |
| NINFRE/J2 | 2019–2021, 42 personas sin match MU. | Priorizar recuperación histórica por volumen, sin confundir volumen con acreditación. |
| NITMRE/J2 | 2019, una persona; plan observado literal NCONRE. | Verificar linaje del campo plan y correspondencia documental; no corregir el literal por semejanza. |
| TPCRE/J2 | 2019–2022; 17/66 personas aparecen en MU, cero en candidatos J2. | Separar 2022 y verificar jornada/carrera contemporánea; históricos anteriores requieren fuentes adicionales. |
| TPCRE/J4 | Mismas 66 personas de carrera y 17 con match general que J2. | Verificar existencia de matrícula J4, no reutilizar match de otra jornada ni duplicar personas entre dimensiones. |

Nueve dimensiones tienen actividad observada exclusivamente anterior a MU2022. Los perfiles SIES, la oferta histórica y los agregados MRUN prueban existencia/atributos de programas; **no sustituyen el enlace individual** RUT→matrícula→plan→código. No está demostrado que las fuentes individuales faltantes existan hoy localmente.

## Fases ejecutables y puertas de paso (D/E)

| Fase / hito | Trabajo propuesto y dependencia | Prueba / criterio de paso | Resultado esperado, sin promesa de cierre |
|---|---|---|---|
| 0 / Fijar medición | Mantener 63 dimensiones y hashes; fijar indicador de incidencias frente a personas y grano temporal. | Reproducir 39+11+13=63; separar tasas de retención y cobertura. | Línea base comparable, sin rebajar denominador. Diagnóstico ya hecho. |
| 1 / Corregir etiquetas y QA | Usar ambos métodos preservados; registrar 23/22 y 243/241 como distintos granos. No ejecutar script original en destino vigente. | Dos implementaciones reproduzcan por separado persona–plan y persona; pruebas de varias mallas por persona, DV, vacíos y R/P. | Elimina dos discrepancias de interpretación, no dos dimensiones de brecha. Causa comprobada. |
| 2 / Recuperar perfiles | Consultar grupos existentes, evidencia H5 y fuentes por hash; revisar 39 propuestas y perfiles contradictorios. | Vínculo exacto CODCARPR/sede/jornada; perfil único con procedencia o documento explícito. No nombres ni NIVEL. | Reutilizar 31 perfiles de las 39 propuestas; completar ocho sin perfil único y casos de las 11. No equivalencia automática. |
| 3 / Resolver las seis mezclas | Ensayo local por persona/matrícula/carrera/plan/año/período; incorporar sede/jornada y fecha efectiva de plan. Prioridad: coexistencias 2025 e IINF/J2. | Candidato respaldado en contexto; controlar transiciones y multiversión simultánea; reconciliar por fila MU y personas sin duplicar. | Puede producir relaciones por contexto, no una versión universal por dimensión. Cantidad resoluble aún desconocida. |
| 4 / Cubrir cinco muestras pequeñas y 13 sin match | Inventariar respaldos individuales gobernados anteriores a 2022; consultar linaje de plan, matrícula y documentación institucional. Usar oferta/MRUN solo para contraste. | Hash, período, llave y alcance compatibles. Sin fuente, queda E con requerimiento exacto. | Recuperación histórica o resolución documental. No aumentar n con duplicados ni tratar ausencia como cero/deserción. |
| 5 / Acreditar excepciones | Para dimensionar no aplicables: probar que no hubo matrícula de esa dimensión en el ámbito definido; mantener registro original. Equivalencia documental explícita es una vía distinta del predominio. | Responsable, documento y vigencia; propuesta D separada de regla A. No convertir una clasificación sin evidencia en “resuelta”. | Se puede cerrar expediente sin asignación solo si se justifica; no declarar cobertura 100% de versiones por ello. |
| 6 / QA integral | Independencia de implementación; reconciliar todos los contextos, totales MU, personas e incidencias; conservar denominadores/retención. | Diferencias numéricas cero para universos iguales; cero asignación contradictoria; evidencia y pendientes completos. | Diccionario provisional validado por contexto. Si hay una brecha real, no promover. |
| 7 / Aprobación y entrega posterior | Revisión institucional explícita, versiones separadas, prueba de consumidores y nueva comparación antes/ahora. | No hay regla productiva sin aprobación; Excel solo se actualiza por nuevo encargo y sin alterar historia. | Posible reducción demostrable. No commit/push/upload automático. |

Las ocho propuestas sin perfil único recuperado son: IECIREOL/2/4, IECSRE/2/2, IEMORE/2/2, IETMRE/2/2, IETMRE/2/4, IIND/2/4, NCONRE/2/4, NCONREOL/2/4. La búsqueda se limitó al grupo exacto existente; no prueba ausencia de otro respaldo institucional.

## Dependencias y alternativas

- **Disponible:** catálogo 2027, MU2022–2026, PROMEDIOS2019–2026, H5, grupos/perfiles, `observaciones_plan_periodo.tsv`, `catalogo_planes.json`, `evidencia_temporal.json`, oferta anual e historia agregada MRUN. Rutas y hashes principales en `FUENTES_DIAGNOSTICO.json` y manifiestos previos.
- **Disponible como agregado:** combinaciones históricas de DatosAlumnos y trayectorias gobernadas. El original `/Users/alexi/Downloads/DATOSDEALUMNOS_11998.xlsx` **no existe ahora en esa ruta**. Los agregados permiten consultas de contexto, no reconstruir personas sin respaldo individual autorizado.
- **Faltante por acreditar:** historial efectivo CODCLI/matrícula/PLAN_DE_ESTUDIO, sede/jornada por período; definición de `View_promedios_alumnos`; documentos de equivalencia temporal; matrícula individual comparable 2019–2021. Fuentes candidatas documentadas: `View_REGISTRO_DE_ASIGNATURAS` y `RA_CARGA_RASTRO`. No se afirma conexión SQL disponible.
- **Alternativa analítica:** resolver contextos y mantener varias versiones justificadas dentro de una dimensión. Evita forzar una única versión global y conserva el denominador 63; una dimensión solo sale de pendiente cuando todos sus contextos exigibles quedan resueltos o documentados.
- **Alternativa documental:** relación institucional explícita, temporal y verificable puede resolver el vínculo sin alcanzar una muestra estadística de tres personas. Debe gobernarse como otra vía de evidencia, nunca modificar retrospectivamente el umbral para “hacer pasar” un caso.
- **No aplicable:** exige evidencia de alcance, no solo falta de match. Conservar 63 en la serie histórica y presentar N/A aparte. Si se adopta otro universo, publicar otra métrica con puente de conciliación; no anunciar reducción artificial de 24/63.

## ¿Es posible llegar a cero?

**No está demostrado con las fuentes actuales.** Es razonable esperar mejora al separar grano/tiempo y reutilizar evidencia, pero el análisis temporal ya prueba que algunas mezclas persisten dentro del mismo año y plan. Las nueve dimensiones anteriores a MU2022 necesitan documentación o cobertura adicional. Las 39 propuestas también requieren revisión; 24 no es necesariamente el total final de relaciones sin acreditar.

Cero pendientes de diagnóstico, cero dimensiones sin propuesta, cero equivalencias sin acreditar y cero brecha de retención son objetivos distintos. Una decisión interna puede cerrar un expediente documental y dejar un vínculo no asignado; no equivale a cobertura individual 100%. Nunca convertir “no aplicable”, mayoría o ausencia en una equivalencia oficial.

**Siguiente paso recomendado:** ejecutar Fases 1–3 como piloto aislado sobre IINF/J2 e ICRE/J2 (mezcla 2025), y TTMRE/J1–J2 (separación por plan/año), junto con revisión de los ocho perfiles no únicos de las 39 propuestas. Antes de recalcular el 38,10%, fijar la regla de agregación desde contextos hacia las 63 dimensiones. Paralelamente inventariar respaldos 2019–2021 para las nueve dimensiones fuera de cobertura. No regenerar el Excel en esta vuelta.

## Evidencia reproducible

- `DIAGNOSTICO_GRANOS_Y_TEMPORALIDAD.json`: 63 distribuciones reproducidas, controles de grano, perfiles y conteos temporales agregados.
- `diagnosticar.py`: lectura local aislada; no persiste identificadores.
- `metodo_original_referencia.py`: copia de código original para lectura, **no ejecutar**.
- `../validacion_local_v1/validar.py`, `FASE2_REVISION_11.csv`, `FASE3_DIAGNOSTICO_13.csv` y `FASE5_QA_INDEPENDIENTE.json`: auditoría previa.
- `../../../../docs/resultados_versiones_por_cohorte_20261016.md`, `resultados_fase_b_equivalencias_historicas.md`, `continuidad_trayectoria_20261016.md`: contratos y límites existentes.

No hubo modificación del Excel, fuentes originales, reglas operativas, tasas ni denominadores. Sin commit, push ni uploads. No hay bloqueo de conexión para este diagnóstico local; los bloqueos son de evidencia y alcance descritos arriba.

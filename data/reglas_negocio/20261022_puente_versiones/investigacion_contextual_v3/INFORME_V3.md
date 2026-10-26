# Investigación contextual V3 — resultado provisional

Clasificación C: cálculos/implementación; B: datos observados; D: propuesta interna; E: pendientes. Ninguna nueva regla A oficial.

## Resultado
24/63 (38,10%) → 19/63 (30,16%) dimensiones pendientes de propuesta: 5 propuestas contextuales nuevas, reducción 7,94 puntos porcentuales. No cambia la retención ni acredita aprobación institucional. Se amplía el tipo de propuesta admisible de versión fija a correspondencia contextual completa observada, como autoriza el encargo; se mantiene universo 63 y muestra mínima 3. No se extrapola fuera del corte.

Las 39 propuestas anteriores se reproducen, pero solo IECIRE/J1, IPRE/J4 y NTCCRE/J2 pasan la prueba contextual completa adicional. Las otras 36 no se presentan como equivalencias verificadas. El total de 44 mezcla 39 propuestas estadísticas heredadas y 5 contextuales nuevas; el subconjunto contextual completo con n>=3 es 8/63. Aprobación institucional acreditada: 0.

## Fase 1 — inventario y definiciones
Oferta consolidada 2010–2026 en data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json; catálogo 2027 separado. Matrícula individual utilizada: MAT_IP_CIISA_2019–2021 y MU2022–2026; archivos 2010–2018 identificados, no necesarios para cruce del año observado PR2019–2026. No se afirma cobertura individual 2027. Fertacademy no encontrado en búsqueda acotada; no se presume equivalencia con oferta académica. IPSS_Procesos_SIES contiene modelo nacional y referencias Windows, no puente individual de plan localizado. Git status --short --untracked-files=no de ese repositorio terminó sin cambios rastreados; el inventario completo de no rastreados se interrumpió por demora. No se modificó.

## Fase 2 — hipótesis, pruebas discriminantes y límites
|Hipótesis|Prueba/fuente|Resultado y qué la limita/refuta|
|---|---|---|
|Catálogo actual excluye historia|Oferta anual H5 contra candidatos2027|NETMRE/J2 observa V2 histórica fuera catálogo; n2 impide nueva propuesta. No es ausencia de matrícula.|
|Cohorte vs observación|ANIO_ING_ACT/MM_ANIO_ACTUAL contra año PR|Cohorte elimina mezcla contextual en TTMRE/J1 y TPCREOL/J4, pero faltan 7 observaciones en cada uno; no resuelve cobertura.|
|Carrera agrupa planes|CODCLI+PLAN_DE_ESTUDIO; catálogo fase4|NITMRE tiene plan catalogado NCONRE; no asignación automática. TCRE/J2 admite dos versiones observadas y no versión fija.|
|Continuidad/duración identifica versión|grupos_existentes.json y oferta anual|Perfil único no acredita plan individual; IINF/J2 tiene perfiles continuidad 4/5 y observaciones regulares, refuta asignación universal por duración.|
|Sede/jornada histórica|DA12159 exacto y código de matrícula anual|Cinco nuevas concordantes; DA es corte actual, no certifica vigencia histórica del plan. ICRE/J1,NETMRE/J4,TCRE/J1,TPCRE/J4 no tienen PR en jornada exacta: requieren expediente histórico, no descarte del denominador.|
|Normalización/documentos múltiples|Llave exacta cuerpo/DV; tipo R en MU; unicidad CODCLI y atribución|Cinco nuevas sin identidad conflictiva ni código atribuido a expedientes múltiples; no se usan nombres, sexo ni nacimiento. No cubre pasaporte sin llave homogénea.|
|Fuente/llave incorrecta|DA12159 explícito; informes históricos y reporte4262|4262 tiene estados/identidad, no carrera/plan: no basta. 11998/12023 no disponibles en rutas documentadas; no se simulan.|
|Puente contextual legítimo|Observación persona+expediente+plan+año+periodo → matrícula exacta familia|Cinco dimensiones 100% cobertura sin contradicción; TCRE/J2 multiversión se resuelve por matrícula individual, no por mayoría ni por cohorte sola. Requiere mantener identidad local; salida agregada no motor de asignación individual.|

Fuentes exactas y hashes: FUENTES.json; detalle por caso: PRUEBAS_CONTEXTUALES.json, CONTEXTOS_OBSERVADOS.csv y DIMENSIONES_63_V3.csv. El perfil gobernado único de 31/39 es perfil agregado duración/tipo, no equivalencia aprobada.

## Fase 3 — validación
Segunda lectura independiente con SQLite contrasta número de observaciones, personas, coincidencias únicas y ausencias en las 63 dimensiones. Las pruebas DA/plan son controles adicionales de la primera implementación, no se atribuyen a la segunda. QA_INDEPENDIENTE.json registra resultado. Hashes de fuentes se comprueban antes/después. Control Excel compara valores numéricos históricos y XML de 13 gráficos; retención preservada. Discrepancia heredada FotoT3 2026: 1360/1471 no coincide con tasa almacenada; se documenta sin alterar fuente ni tasa.

## Fase 4 — entrega y preparación
Nueva versión V3, originales/V1/V2 conservados. Regla contextual queda PENDIENTE_APROBACION_GOBERNANZA; no activación SQL, skills ni reglas productivas. La especificación reproducible y controles constituyen preparación para revisión. No commit/push/uploads.

## Pendientes y siguiente paso
Revisar cortes históricos/rectificaciones con identidad, código SIES y año para los casos casi completos NCONRE/J2 (2), NICCRE/J2 (1), NINFRE/J2 (1), TPCRE/J1 (1), TPCRE/J2 (2). No eliminar observaciones sin match ni rebajar n3. Los campos y años faltantes de los 19 casos están en DIMENSIONES_63_V3.csv; se requiere trazabilidad de asignación efectiva de PLAN_DE_ESTUDIO para convertir relaciones observadas en reglas prospectivas. No se promete 0%.

## Evidencia nueva por dimensión

|Dimensión|Personas|Observaciones|Códigos observados|
|---|---:|---:|---|
|NAUTRE/J2|7|18|I162S2C22J2V2|
|NECIRE/J2|4|5|I162S2C1J2V2|
|NICCREOL/J4|9|45|I162S2C46J4V1|
|NINFREOL/J4|16|39|I162S2C1J4V3|
|TCRE/J2|10|27|I162S2C6J2V2, I162S2C6J2V1|

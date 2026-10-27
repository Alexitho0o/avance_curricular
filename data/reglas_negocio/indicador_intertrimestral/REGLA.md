# Indicador intertrimestral · borrador de extracción V24

Estado: **borrador, sin paridad completa ni activación**. No confundir la continuidad intertrimestral con la tasa anual oficial SIES.

**[A]** Retención anual SIES: misma institución y cohorte al año siguiente, elegibilidad y corte anual. No define indicador intertrimestral. Origen: `CORREO_SIES`.

**[D/C]** Grupo 1 primer año MU; grupos 2 y 3 ingresos separados. T1 2026: ingreso de origen 2026-1, VIG 1 y sin RUT duplicado. Origen: `V24:18_Foto_Intertrimestral!B80`.

**[C/E]** Grupo 1 en T2 usa proxy de actividad y estado de PROMEDIOS; no acredita foto de matrícula al cierre. Para 2024 en T3 institucional se usa también proxy. Origen: `V24:18_Foto_Intertrimestral!B3,E7:H8,E11:F11,B82`.

**[B/C]** T3 2025 consulta la foto de 2025; T3 2026 consulta DATOSDEALUMNOS, estado de extracción en T3 en curso. Origen: `V24:18_Foto_Intertrimestral!B82;24_Foto_Corte_T3_2025;25_Foto_Corte_T3_2026`.

**[C]** R representa en base T3, Q vigente; denominador T3 suma R y numerador suma Q dentro del grupo; total usa T para primera persona del año. Origen: `V24:18_Foto_Intertrimestral!G8:H10;20_Foto_BBDD!Q:R,T`.

**[D/C]** T1 2026 T3 1360/1467: cuatro no aplica de 1471; total T3 2290/2519 con cuatro exclusiones. Origen: `BASES_V16;V24:18_Foto_Intertrimestral!D93:H93,D95:H95`.

**[B/C/E]** Ingreso T2 2026: 462/528 matrículas; 527 personas en D12, renuncias agregadas sin nómina completa. No convertir a tasa de personas. Origen: `BASES_V16;V24:18_Foto_Intertrimestral!D12:F12,D94:I94;23_Foto_Renuncias_T2_2026`.

**[C]** Ingreso T2 2025 excluye del denominador T2 estados NO APLICA y PENDIENTE; T3 usa bandera R. Origen: `V24:18_Foto_Intertrimestral!E9:H9`.

**[C/E]** Sin foto completa, sin foto y no aplica conservan texto; no convertirlos a cero. Origen: `V24:18_Foto_Intertrimestral!E10:F10,E13:F13,E14:F14,E18:H18`.

**[C]** Para grupos compatibles, agregar numeradores y denominadores; no promediar porcentajes. Origen: `ESPECIFICACION`.

**[D/E]** Diplomados excluidos en el seguimiento autorizado; esta regla requiere auditar universo y filtros de V24 antes de afirmar aplicación total. Origen: `Decisión usuario; V24:20_Foto_BBDD`.

**[E]** La paridad desde fuentes crudas y por sector/carrera no está completada; constantes/proxies de hoja 26 requieren trazabilidad independiente. Origen: `V24:26_Avance_Curricular_Resumen!E1850,E1851,E1854`.


**[C/E] Actualización Hito 2b:** E1850=160, E1851=175 y E1854=1042 se reprodujeron desde PROMEDIOS 12166 por cuerpo de RUT y estado VIGENTE del extracto. La coincidencia no prueba el algoritmo original ni vigencia a fecha de cierre; el constructor original sigue E. F12 es 462/528 matrículas, mientras H11 y H14 son tasas de personas; E14/F14 conservan «Sin foto completa»/«—», sin sumar unidades distintas.


**[D/C]** Si no se encuentra la matrícula de ingreso en foto 2025/2026, mostrar «Sin matrícula de ingreso en el corte», Q=0 y R=1: queda en el denominador y no suma al numerador. La decisión evita inflar la tasa y no acredita deserción.

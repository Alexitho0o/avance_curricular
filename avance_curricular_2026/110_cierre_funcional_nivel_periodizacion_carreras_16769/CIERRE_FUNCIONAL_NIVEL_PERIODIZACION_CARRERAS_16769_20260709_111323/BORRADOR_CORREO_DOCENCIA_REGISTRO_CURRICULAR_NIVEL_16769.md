# Borrador correo - cierre pendiente NIVEL / Carreras Avance Curricular 2026

Asunto: Confirmacion requerida - ubicacion curricular por NIVEL para Carreras Avance Curricular SIES 2026

Estimadas/os,

Junto con saludar, en el marco del proceso Avance Curricular SIES 2026, carga Carreras ID SIES 16769, necesitamos confirmar la interpretacion funcional de la columna `NIVEL` de la fuente institucional de planes de estudio utilizada para preparar la distribucion anual de unidades del archivo 5810.

La fuente revisada contiene asignaturas por plan (`CODPESTUD`, `CODRAMO`, nombre de asignatura, creditos y `NIVEL`), pero las auditorias locales no encontraron una definicion explicita que indique si `NIVEL` representa semestre curricular, anio curricular, secuencia interna, nivel academico u otra codificacion. Por esta razon no podemos usar automaticamente la conversion `NIVEL 1-2 = anio 1`, `NIVEL 3-4 = anio 2`, etc.

Solicitamos confirmar documental o funcionalmente:

1. Que significa exactamente `NIVEL` en la fuente de planes de estudio.
2. Si `NIVEL` corresponde a semestre curricular del plan para las mallas de Avance Curricular 2025.
3. Si se autoriza, para el archivo Carreras Avance Curricular 2026, convertir `NIVEL` a anio SIES mediante `ANIO = techo(NIVEL / 2)`.
4. Como deben tratarse asignaturas en niveles que, bajo esa conversion, quedan fuera de `techo(DURACION_ESTUDIOS / 2)`.
5. Si existen actividades de practica, titulacion, examen final, continuidad, electivos u otra categoria que deban incluirse o excluirse de `TOTAL_UNIDADES_MEDIDA` y de `UNIDADES_1ER_ANIO` a `UNIDADES_7MO_ANIO`.
6. Confirmar o corregir el plan institucional (`CODPESTUD`) de las siguientes carreras que no tienen enlace estructurado en la conciliacion usada por el diagnostico:

- I162S2C85J4V1: CONTABILIDAD GENERAL, jornada 4, version 1, duracion 5 semestres. Plan mencionado en fundamento tecnico/conciliacion: CONG20251.
- I162S2C83J4V1: ADMINISTRACION PUBLICA, jornada 4, version 1, duracion 8 semestres. Plan mencionado en fundamento tecnico/conciliacion: ADMP20251.
- I162S2C86J4V1: AUDITORIA, jornada 4, version 1, duracion 8 semestres. Plan mencionado en fundamento tecnico/conciliacion: AUDT20251.

Idealmente necesitamos una tabla o confirmacion con estos campos:

- CODIGO_UNICO.
- CODCARR.
- CODPESTUD.
- Codigo de asignatura/ramo.
- Nombre de asignatura.
- Creditos o unidad de medida.
- Semestre curricular y/o anio curricular dentro del plan.
- Definicion del campo semestre/anio o de `NIVEL`.
- Vigencia del plan para el anio academico 2025.
- Fuente/sistema de origen y fecha de extraccion.

Mientras no contemos con esta confirmacion, el archivo Carreras Avance Curricular 2026 queda BLOQUEADO_CON_PENDIENTES y no se generara CSV de carga ni SIES_READY.

Muchas gracias.

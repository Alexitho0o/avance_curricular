# Metodologia de Identidad de Carreras

## Objetivo
Consolidar una metodologia tecnica reutilizable para relacionar carreras institucionales y codigos SIES usando solo evidencia recuperada en Fase 1.

## Alcance
Procesos cubiertos: Matricula Unificada 2026, Estudiantes Extranjeros SIES 2026, auditoria multicodcli, puentes SIES y Avance Curricular SIES 2026.

## Fuentes Usadas
La metodologia usa exclusivamente las salidas de Fase 1 en `02_CONOCIMIENTO_RECUPERADO/` y auditorias de control de Fase 1. Las fuentes originales quedan como trazabilidad, no se modifican.

## Separacion de Evidencia
Las reglas se clasifican como REGLA_OFICIAL, DATO_OBSERVADO, IMPLEMENTACION_TECNICA, DECISION_INTERNA o HIPOTESIS_O_PENDIENTE. Una implementacion tecnica no se presenta como regla oficial.

## Campos Canonicos
- CODIGO_UNICO: IDENTIFICADOR
- CODIGO_UNICO_FINAL: IDENTIFICADOR
- CODCLI: IDENTIFICADOR
- CODCARR: IDENTIFICADOR
- CODCARPR: IDENTIFICADOR
- NOMBRE_CARRERA: ATRIBUTO
- JORNADA: FILTRO
- MODALIDAD: FILTRO
- SEDE: ATRIBUTO
- VERSION: ATRIBUTO
- PLAN_ESTUDIOS: TRAZABILIDAD
- PLAN_DE_ESTUDIO: IDENTIFICADOR
- TIPO_PLAN_CARRERA: CRITERIO_DESEMPATE
- DURACION_ESTUDIOS: CRITERIO_DESEMPATE
- VIGENCIA: CONTROL_VIGENCIA
- RESOLUCION_STATUS: ESTADO
- ES_BLOQUEANTE: BLOQUEO

## Jerarquia de Decision
- Nivel 1: CODIGO_UNICO_EXACTO -> RESUELTO_CODIGO_UNICO_EXACTO
- Nivel 2: PUENTE_APROBADO -> RESUELTO_PUENTE_APROBADO
- Nivel 3: PLAN_INSTITUCIONAL -> RESUELTO_PLAN_INSTITUCIONAL
- Nivel 4: REGLA_TIPO_DURACION -> RESUELTO_REGLA_TIPO_DURACION
- Nivel 5: NOMBRE_NORMALIZADO_CANDIDATO -> CANDIDATO_NOMBRE

## Metodos de Resolucion
La resolucion prioriza codigo unico exacto, puente aprobado, plan institucional, regla tecnica/interna de tipo y duracion, y finalmente nombre solo como candidato.

## Tratamiento de Ambiguedad
Toda multiplicidad o falta de unicidad se clasifica como AMBIGUO_MULTIPLES_COINCIDENCIAS y no se resuelve arbitrariamente.

## Tratamiento de Bloqueos
Toda contradiccion, ausencia de evidencia, vigencia incompatible, jornada incompatible o marca bloqueante impide resolver identidad.

## Uso de TIPO_PLAN_CARRERA
Se usa solo con alcance documentado como IMPLEMENTACION_TECNICA o DECISION_INTERNA recuperada, nunca como regla oficial salvo respaldo oficial explicito.

## Uso de DURACION_ESTUDIOS
Se usa junto con TIPO_PLAN_CARRERA y otros campos de contexto. No debe generalizarse fuera del alcance recuperado.

## Separacion PLAN_ESTUDIOS / PLAN_DE_ESTUDIO
PLAN_ESTUDIOS SIES y PLAN_DE_ESTUDIO institucional permanecen separados. No se comparan directamente ni se asumen equivalentes.

## Catalogo de Estados
- AMBIGUO_MULTIPLES_COINCIDENCIAS
- BLOQUEADO_CONTRADICCION
- BLOQUEADO_JORNADA
- BLOQUEADO_SIN_EVIDENCIA
- BLOQUEADO_VIGENCIA
- CANDIDATO_NOMBRE
- NO_EVALUADO
- RESUELTO_CODIGO_UNICO_EXACTO
- RESUELTO_PLAN_INSTITUCIONAL
- RESUELTO_PUENTE_APROBADO
- RESUELTO_REGLA_TIPO_DURACION

## Limitaciones
Nombre normalizado no valida identidad por si solo. Fuentes de otro proceso no modifican reglas de un proceso superior o periodo distinto.

## Pendientes
Contradicciones reales detectadas: 0.

## Aplicacion Posterior a Avance Curricular
La tabla maestra posterior debe usar esta matriz para evaluar las 34 carreras directas, manteniendo separados PLAN_ESTUDIOS SIES y plan institucional.

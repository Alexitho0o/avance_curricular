# Solicitud de validación funcional — Avance Curricular SIES 2026, archivo 5809 columnas 16-19

Estimados/as,

Se solicita validar funcionalmente el cierre sin modificación de 256 casos observados en la revisión de columnas 16-19 del archivo 5809 Matrícula Avance Curricular 2026.

## 1. Bloque columna 19 — 218 casos

Se solicita validar mantener sin cambio 218 casos de `UNIDADES_APROBADAS` anual 2025.

Fundamento:
- El instructivo oficial indica que para las unidades aprobadas durante el último año académico 2025 no se deben incluir unidades aprobadas por validación de estudios o reconocimiento de aprendizajes previos.
- En la fuente PROMEDIOS, los estados observados son:
  - A = APROBADO
  - E = CONVALIDACION
  - I = HOMOLOGADO
  - R = REPROBADO
- El hito 62 muestra que 218/218 casos calzan contando solo A como aprobado y 0/218 calzan contando A+E+I.

Decisión solicitada:
Validar que para columna 19 anual 2025 se mantenga el criterio `solo A cuenta como aprobado`, excluyendo E/I del anual 2025.

## 2. Bloque sin registros académicos 2025 — 21 casos

Se solicita validar mantener sin cambio 21 casos con:
- 16 CURSO_1ER_SEM = NO
- 17 CURSO_2DO_SEM = NO
- 18 UNIDADES_CURSADAS = 0
- 19 UNIDADES_APROBADAS = 0

Evidencia:
- FILAS_2025_CODCLI_LISTA = 0.
- Estados académicos observados reales:
  - ELIMINADO: 20 casos.
  - ELIMINADO | VIGENTE: 1 caso.
- No se usa “inactivo” como estado académico.

Decisión solicitada:
Validar que la ausencia de registros académicos 2025 y los estados observados no contradicen mantener 0,0,0,0.

## 3. Bloque PERIODO_NO_1_2 — 17 casos

El hito 67 confirma que `PERIODO` raw no tiene regla oficial encontrada para mapear 1,2,3,4,5 a semestres.

Resultado:
- El escenario que calza con 5809 es mantener 5809 sin cambio: 17/17.
- El escenario 1=SEM1 y 2/3=SEM2 está bloqueado y no se aplica.

Decisión solicitada:
Validar una de estas opciones:
1. Mantener 5809 sin cambio para estos 17 casos.
2. Mantenerlos bloqueados hasta una definición institucional formal de PERIODO raw.

## Alcance

Esta validación aplica solo a Avance Curricular SIES 2026, archivo 5809, columnas 16-19.
No incluye columnas 20-21.
No implica generación de archivo de carga ni SIES_READY.

Saludos.

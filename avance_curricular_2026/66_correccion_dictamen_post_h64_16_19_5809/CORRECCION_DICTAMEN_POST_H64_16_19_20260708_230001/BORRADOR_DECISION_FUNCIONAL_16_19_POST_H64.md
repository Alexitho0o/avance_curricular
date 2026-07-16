# Borrador decision funcional 16-19 post hito 64

Proceso: Avance Curricular SIES 2026
Archivo: 5809 Matricula Avance Curricular
Ano proceso: 2026
Ano referencia datos: 2025
Declaracion de carga: NO_LISTO_PARA_CARGA

Estimadas/os,

Se solicita validacion funcional del dictamen corregido para los bloques 218, 21 y 17 de columnas 16-19 del archivo 5809, sin solicitar carga, sin modificar fuentes originales y sin aplicar correcciones automaticas.

## 1. Bloque 218 columna 19 UNIDADES_APROBADAS

El instructivo oficial de Avance Curricular SIES 2026 indica que las unidades aprobadas durante el ultimo ano academico 2025 no deben incluir unidades aprobadas por validacion de estudios o reconocimiento de aprendizajes previos.

La fuente PROMEDIOS contiene el dato observado ESTADO/DESCRIPCION_ESTADO:
- A = APROBADO
- E = CONVALIDACION
- I = HOMOLOGADO
- R = REPROBADO
- NULL/blanco = en blanco

La evidencia de los hitos 61/62 muestra que 218 de 218 casos calzan con contar solo A y 0 de 218 calzan con A+E+I. Se solicita validar cierre sin cambio de estos 218 casos, considerando que E/I son datos observados de PROMEDIOS y que su exclusion en columna 19 anual 2025 es consistente con la regla oficial de excluir validacion/reconocimiento.

## 2. Bloque 21 ausencia de registros 2025

Los 21 casos no presentan diferencia numerica entre 5809 y recalculo observado: 16=NO, 17=NO, 18=0, 19=0. La evidencia muestra FILAS_2025_CODCLI_LISTA=0 y estado academico observado principalmente ELIMINADO, con un caso ELIMINADO | VIGENTE.

No se debe denominar 'inactivo' al estado academico. Ese termino solo aparecia como indicador tecnico previo, no como valor observado de estado academico.

Se solicita validar cierre sin cambio de estos 21 casos si la ausencia de registros academicos 2025 y los estados observados no contradicen mantener 0,0,0,0.

## 3. Bloque 17 PERIODO_NO_1_2

Los 17 casos permanecen bloqueados. No se aplica el criterio 1=primer semestre y 2/3=segundo semestre, porque el hito 64 clasifico PERIODO raw como pendiente/bloqueado y sin respaldo oficial suficiente.

Se solicita confirmar que estos 17 casos deben permanecer bloqueados hasta ejecutar una gobernanza especifica de PERIODO raw para PROMEDIOS.

## 4. Alcance excluido

Las columnas 20-21 acumuladas estan fuera de alcance de este paquete, permanecen separadas y no evaluadas.

Resultado esperado de la validacion:
- Confirmar o rechazar cierre sin cambio de los 218 casos.
- Confirmar o rechazar cierre sin cambio de los 21 casos.
- Confirmar bloqueo de los 17 casos hasta gobernanza PERIODO raw.
- Confirmar que 20-21 no se evalua en este hito.

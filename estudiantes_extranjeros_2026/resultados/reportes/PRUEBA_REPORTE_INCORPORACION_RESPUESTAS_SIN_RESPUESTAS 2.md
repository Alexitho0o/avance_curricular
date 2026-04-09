# Reporte de Incorporacion de Respuestas Docencia

Fecha de ejecucion: 2026-06-18 09:12:18

- Modo: DRY_RUN
- Planilla: `estudiantes_extranjeros_2026/resultados/archivos_gestion/PRUEBA_PLANILLA_GESTION_DOCENCIA_EXTRANJEROS_2025_SIN_RESPUESTAS.xlsx`
- Base origen: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/interim/BASE_MAESTRA_EXTRANJEROS_REGULARES_2025.csv`
- SHA-256 base origen: `8a592b3ba3001bab8f4fbee1ce90276f2b4479f39043338125cb69edbb044999`
- Cambios incorporados: 0
- Errores: 0
- Pendientes condicionales: 0
- No se escribio base procesada porque la ejecucion fue dry-run.

## Estados

- SIN_RESPUESTA: 150

## Criterios aplicados

- No se reemplazaron datos por respuestas vacias.
- Nacionalidad y pais de origen se validaron contra catalogo oficial 1..197, excluyendo Chile cuando corresponde.
- Pais de origen quedo condicionado por TIPO_RESIDENCIA_ESTUDIANTE.
- La base intermedia original no se modifica.

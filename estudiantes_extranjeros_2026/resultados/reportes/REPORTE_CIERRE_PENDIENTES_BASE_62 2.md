# Reporte cierre pendientes base congelada 62

Generado: 2026-06-24T13:54:41-04:00

## Fuentes utilizadas
- Base congelada: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/frozen/BASE_EXTRANJEROS_2025_CONGELADA.tsv`
- Universo auditado: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/UNIVERSO_DEPURADO_EXTRANJEROS_REGULARES_2025.csv`
- Precarga PES: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/raw/REPORTE_PRECARGA_EXTRANJEROS_REGULARES_2026_ORIGINAL.csv`
- Matricula institucional 2025: `/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_avance_curricular_2025_control.csv`
- DatosAlumnos: `/Users/alexi/Documents/GitHub/avance_curricular/input/PROMEDIOSDEALUMNOS_7804.xlsx` hoja `DatosAlumnos`
- Fuente normativa unica: `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/docs/Instructivo_Estudiantes_Extranjeros_SIES_2026.txt`

## Hashes
- TSV congelado: `da85dd0c453a942a4490f469b75d0418e9054e458a46028f44271ac704518081`
- Universo 257: `9c78b2640f1dbec682a0850f30bd9cb0592568ccc68b864a4f80171894a72b86`
- Instructivo: `436219b2666cadc1c87c311a0961249081aae7bf76a27f2ab4455b15af9b4a13`
- Excel cierre: `49554eb5534772e386cad681a72a9c79c1ae3b0990fa182adaa49265f2628e99`

## Conteos iniciales y decisiones
- Nacionalidad ambigua inicial: 1; pendiente final: 1.
- Sin evidencia 2025 inicial: 4; confirmadas: 1; pendientes/parciales: 3.
- Coincidencias multiples iniciales: 19; resueltas: 5; pendientes: 14.
- No seleccionados iniciales: 124; desglosados: 124.

## No incluidos finales
- CONFLICTO_IDENTIDAD: 16
- EXCLUSION_MANUAL_SIN_FUNDAMENTO_DOCUMENTADO: 22
- PERSONA_INCLUIDA_OTRO_CODIGO_UNICO: 1
- PERSONA_INCLUIDA_REGISTRO_DUPLICADO: 13
- REQUIERE_CONFIRMACION_INSTITUCIONAL: 122
- SOLO_PRECARGA_SIN_CONFIRMACION: 21

## Estados finales
- EXCLUSION_CONFIRMADA: 14
- PENDIENTE_CONFIRMACION_INSTITUCIONAL: 181

## Casos pendientes institucionales
- Base 62 con revision pendiente: 18.
- No incluidos pendientes institucionales: 181.

## Limitaciones
- La base congelada no contiene CODIGO_UNICO SIES directo; por tanto no se fabrican coincidencias exactas persona-carrera SIES.
- Cuando EVIDENCIA_2025 esta vacia o es parcial, la decision queda como requerimiento institucional.
- No se infiere nacionalidad desde RUT, tipo documental, direccion, colegio, nombre ni paises asociados.

## Archivos creados
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/UNIVERSO_PENDIENTES_CIERRE_BASE_62.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_NACIONALIDAD_AMBIGUA_62.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_4_SIN_EVIDENCIA_2025.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/CANDIDATOS_19_COINCIDENCIAS_MULTIPLES.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_19_COINCIDENCIAS_MULTIPLES.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/RESOLUCION_124_NO_SELECCIONADOS.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/REGISTROS_195_NO_INCLUIDOS_RESUELTOS.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/data/processed/BASE_EXTRANJEROS_2025_CONGELADA_ENRIQUECIDA_CIERRE.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/CIERRE_TRAZABLE_PENDIENTES_BASE_62.xlsx`
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/resultados/auditorias/VALIDACION_CIERRE_PENDIENTES_BASE_62.csv`

## Respaldo
- `/Users/alexi/Documents/GitHub/avance_curricular/estudiantes_extranjeros_2026/backups/pre_cierre_pendientes_base_62_20260624_135441`

## Estado git
```
M README.md
?? backups/pre_cierre_pendientes_base_62_20260624_134419/
?? backups/pre_cierre_pendientes_base_62_20260624_134436/
?? backups/pre_cierre_pendientes_base_62_20260624_135441/
?? resultados/reportes/REPORTE_CIERRE_PENDIENTES_BASE_62.md
?? scripts/cerrar_pendientes_base_62.py
```

No se genero archivo final de carga PES.

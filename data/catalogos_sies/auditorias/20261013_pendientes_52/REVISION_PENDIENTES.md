# Revision de pendientes SIES 2027 P1

52 registros / 14 codigos internos. Nuevas equivalencias respaldadas: 0. Catalogo activo sin cambios.

Los candidatos de esta tabla NO estan aprobados ni se asignaron. Su modalidad es la del registro de oferta, no una clasificacion del estudiante.

| CODCARPR | Sede | Registros | NOMBRE_L (DatosAlumnos) | Resultado | Candidatos SIES no aplicados |
|---|---|---:|---|---|---|
| COICONSSP | CO | 1 | INGENIERIA EN CONSTRUCCION SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S3C132J3V1 |
| COTELECSP | CO | 2 | TECNICO EN ELECTRICIDAD SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S3C138J3V1 |
| COTENSSP | CO | 2 | TECNICO EN ENFERMERIA SP | VARIAS_MODALIDADES_NO_APLICADAS | I162S3C91J1V1; I162S3C91J2V1; I162S3C91J3V1 |
| COTIMAGSP | CO | 1 | TECNICO EN IMAGENOLOGIA SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S3C139J3V1 |
| COTVETSP | CO | 4 | TECNICO VETERINARIO SP | NOMBRE_AMPLIADO_NO_APLICADO | I162S3C143J3V1 |
| ICONSSP | RE | 3 | INGENIERIA EN CONSTRUCCION SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S2C132J3V1 |
| IELECSP | RE | 2 | INGENIERIA EN ELECTRICIDAD SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S2C133J3V1 |
| TCONSSP | RE | 3 | TECNICO EN CONSTRUCCION SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S2C137J3V1 |
| TELECSP | RE | 8 | TECNICO EN ELECTRICIDAD SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S2C138J3V1 |
| TENSSP | RE | 7 | TECNICO EN ENFERMERIA SP | VARIAS_MODALIDADES_NO_APLICADAS | I162S2C91J1V1; I162S2C91J2V1; I162S2C91J3V1 |
| TFARSP | RE | 7 | TECNICO EN FARMACIA SP | VARIAS_MODALIDADES_NO_APLICADAS | I162S2C115J2V1; I162S2C115J3V1 |
| TGEIN | RE | 1 | TECNICO EN GESTION INDUSTRIAL | SIN_COINCIDENCIA_NOMINAL | Sin coincidencia nominal |
| TIMAGSP | RE | 1 | TECNICO EN IMAGENOLOGIA SP | CANDIDATO_NOMINAL_UNICO_NO_APLICADO | I162S2C139J3V1 |
| TVETSP | RE | 10 | TECNICO VETERINARIO SP | NOMBRE_AMPLIADO_NO_APLICADO | I162S2C143J3V1 |

## Que falta

- 21 registros, CANDIDATO_NOMINAL_UNICO_NO_APLICADO: Equivalencia documentada del CODCARPR y sede con el candidato SIES. El nombre sin SP coincide, pero U+ indica V y la oferta jornada 3; no homologar sin respaldo.
- 16 registros, VARIAS_MODALIDADES_NO_APLICADAS: Codigo SIES o modalidad de carrera vinculada explicitamente al CODCARPR, sede y plan. Hay oferta presencial y semipresencial; ni SP ni V permiten elegir.
- 14 registros, NOMBRE_AMPLIADO_NO_APLICADO: Documento que vincule Tecnico Veterinario SP con Tecnico Veterinario en Clinica de Animales de Compania, por CODCARPR y sede, y aclare jornada U+ V frente a SIES 3.
- 1 registros, SIN_COINCIDENCIA_NOMINAL: Nombre oficial/codigo SIES 2027 del programa TGEIN y su plan. No equiparar Gestion Industrial con Control Industrial, Automatizacion o Ingenieria por semejanza.

## Evidencia

El JSON adjunto identifica hashes, hojas, filas y requerimientos UP-26/UP-27.
Los diccionarios revisados no contienen estos 14 CODCARPR. Docencia y la oferta respaldan los atributos de los candidatos, pero no su enlace a los codigos internos.

No se ejecutaron Matricula Unificada ni Caracterizacion. No se modificaron fuentes ni congelados 2026.

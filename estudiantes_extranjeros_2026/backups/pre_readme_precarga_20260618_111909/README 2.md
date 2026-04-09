# Estudiantes Extranjeros SIES 2026

Subproducto para organizar y diagnosticar la entrega **Estudiantes Extranjeros SIES 2026**, correspondiente a estudiantes con nacionalidad extranjera matriculados o con actividad academica entre el **1 de enero y el 31 de diciembre de 2025**.

## Objetivo

Integrar el proceso al repositorio existente sin crear una linea paralela de trabajo, reutilizando la gobernanza de Matricula Unificada, fuentes de estudiantes, oferta academica, puente SIES y auditorias ya disponibles.

## Entregas normativas

- Extranjeros Regulares 2026, ID de carga 16765: estudiantes extranjeros regulares en programas conducentes o certificables de pregrado, postgrado o postitulo.
- Extranjeros de Intercambio 2026, ID de carga 16764: estudiantes extranjeros en programas o actividades formativas de corta duracion, presenciales en Chile, no orientadas a titulo o grado institucional.

## Alcance de esta ejecucion

Esta fase no genera CSV definitivo para PES. Solo crea diagnostico, inventario, diccionario oficial, matriz de mapeo, brechas, reglas y nominas de gestion.

## Fuentes candidatas detectadas

- `input/PROMEDIOSDEALUMNOS_7804.xlsx`, hoja `DatosAlumnos`: CODCLI, RUT, nombres, sexo, fecha de nacimiento, nacionalidad, carrera, sede, jornada, anio/periodo de matricula e ingreso.
- `resultados/archivo_listo_para_sies.xlsx`, hoja `ARCHIVO_LISTO_SUBIDA`: campos MU normalizados, CODCLI, trazas y codigo SIES final para parte del universo.
- `gobernanza_columnas_mu/`: definiciones y reglas ya documentadas para TIPO_DOC, N_DOC, DV, nombres, sexo, FECH_NAC, NAC, PAIS_EST_SEC, ingreso y VIG.
- `gobernanza_nac.tsv` y `gobernanza_pais_est_sec.tsv`: catalogos de normalizacion existentes.
- `control/catalogos/PUENTE_SIES_COMPILADO.tsv`: puente de CODCARPR/oferta a codigo unico SIES.
- `indices_2025/cned/resultados/OFERTA_ACADEMICA_2026_DICCIONARIO_CON_ENCABEZADOS.*`: oferta/diccionario reutilizable como contraste de programas.

## Claves de cruce propuestas

1. Documento oficial normalizado: tipo documento, NUM_DOCUMENTO y DV.
2. CODCLI mediante equivalencia maestra, sin reemplazar NUM_DOCUMENTO.
3. CODCARPR + jornada + modalidad + version para CODIGO_UNICO.
4. Nombres + fecha de nacimiento solo para diagnostico y nunca para completar automaticamente.

## Campos criticos

No se deben inferir `NACIONALIDAD`, `TIPO_RESIDENCIA_ESTUDIANTE`, `PAIS_DE_ORIGEN` ni `PAIS_ESTUDIOS_SECUNDARIOS`. En esta ejecucion se detectaron 29 extranjeros confirmados por nacionalidad mapeable y 1 caso con nacionalidad no mapeada/por definir.

## Flujo propuesto

1. Validar universo 2025 regular con Docencia/Registro Academico.
2. Obtener fuente institucional de intercambio 2025 si existe.
3. Resolver campos criticos de residencia, origen y estudios secundarios.
4. Confirmar CODIGO_UNICO con puente SIES/oferta y resolver ambiguedades.
5. Ejecutar transformaciones en script separado, con auditoria y sin sobrescribir entregas previas.

## Riesgos

- Ausencia de fuente de intercambio.
- `TIPO_RESIDENCIA_ESTUDIANTE` no existe en fuentes revisadas.
- `PAIS_DE_ORIGEN` es condicional y no debe inferirse.
- `PAIS_ESTUDIOS_SECUNDARIOS` requiere evidencia de secundaria completada, no solo localidad o nacionalidad.
- Hay ambiguedades de codigo unico en puente SIES para algunos programas.
- Una nacionalidad aparece como `Por definir`.

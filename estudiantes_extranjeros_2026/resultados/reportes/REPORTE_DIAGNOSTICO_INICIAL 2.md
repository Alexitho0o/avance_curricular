# Reporte Diagnostico Inicial

Fecha de ejecucion: 2026-06-18 08:46:44

## Localizacion del instructivo

- Original: `Instructivo _Estudiantes_Extranjeros_SIES.txt`
- Copia documental estable: `estudiantes_extranjeros_2026/docs/Instructivo_Estudiantes_Extranjeros_SIES_2026.txt`
- SHA-256 original/copia: `436219b2666cadc1c87c311a0961249081aae7bf76a27f2ab4455b15af9b4a13` / `436219b2666cadc1c87c311a0961249081aae7bf76a27f2ab4455b15af9b4a13`
- Codificacion detectada: utf-8
- Lineas: 833

## Diagnostico del repositorio

Se inventariaron 2317 archivos relevantes fuera del nuevo subproducto. Distribucion por tipo:

{
  "CSV/TSV": 1304,
  "Excel": 410,
  "configuracion": 116,
  "documentacion": 411,
  "script_python": 76
}

Fuentes de alta reutilizacion detectadas:

- `archive/cleanup/cutoff_2026-04-15/moved 2/control/backups/puente_sies_backup_original_2026-04-09.tsv`: RUN/RUT|CARRERA/PROGRAMA|JORNADA
- `archive/cleanup/cutoff_2026-04-15/moved 2/control/backups/puente_sies_no_usado_2026-04-09.tsv`: RUN/RUT|CARRERA/PROGRAMA|JORNADA
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/probe_avance_parchado_v2_2026-04-04_fix_recovery/audits_reconstruccion_codigo_unico_nivmax/02_matricula_unificada_32_vs_maestra.csv`: CODCLI|RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/probe_avance_parchado_v2_2026-04-04_fix_recovery/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_auditoria_codcli_sies_2026-04-05_00-05-18/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_full_check_final_fix_2026-04-04/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_full_check_stage32_canon_fix5_2026-04-04/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_master_auditoria_2026-04-04_18-35-19/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_terminal_trace_union_2026-04-04_18-54-08/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_terminal_trace_union_fix_2026-04-04_18-58-31/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_trace_50_codcli_2026-04-04_18-43-08/audits/05_matricula_unificada_32.csv`: CODCLI|RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_trace_50_codcli_2026-04-04_18-43-08/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 2/resultados/run_trace_codcli_vs_maestro_2026-04-04_19-05-46/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 3/control/backups/puente_sies_backup_original_2026-04-09.tsv`: RUN/RUT|CARRERA/PROGRAMA|JORNADA
- `archive/cleanup/cutoff_2026-04-15/moved 3/control/backups/puente_sies_no_usado_2026-04-09.tsv`: RUN/RUT|CARRERA/PROGRAMA|JORNADA
- `archive/cleanup/cutoff_2026-04-15/moved 3/resultados/2026-04-04_fix5_estable_definitiva/matricula_unificada_2026_control.2026-04-04_fix5_estable_definitiva.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 3/resultados/audits_reconstruccion_codigo_unico/02_matricula_unificada_32_vs_maestra.csv`: CODCLI|RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 3/resultados/backup_estable_2026-04-04/matricula_unificada_2026_control.ok_2026-04-04.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 3/resultados/matricula_unificada_2026_control.csv`: RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO
- `archive/cleanup/cutoff_2026-04-15/moved 3/resultados/probe_avance_parchado_v2_2026-04-04_fix_recovery/audits_reconstruccion_codigo_unico_nivmax/02_matricula_unificada_32_vs_maestra.csv`: CODCLI|RUN/RUT|NACIONALIDAD|PAIS_ESTUDIOS_SECUNDARIOS|CARRERA/PROGRAMA|SEDE|JORNADA|MODALIDAD|INGRESO|VIGENCIA|FECHA_NACIMIENTO|SEXO

## Universo inicial

- Candidatos 2025 no Chile o por definir desde `DatosAlumnos`: 30
- Confirmados extranjeros con nacionalidad mapeable: 29
- Casos con nacionalidad no mapeada/por definir: 1
- Registros/codcli ya normalizados como OK en `archivo_listo_para_sies.xlsx`: 16
- Fuentes de intercambio detectadas: 0

## Cobertura por variable oficial regular

- TIPO_DOCUMENTO (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- NUM_DOCUMENTO (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_DIRECTO
- DV (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- PRIMER_APELLIDO (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- SEGUNDO_APELLIDO (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- NOMBRES (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- SEXO (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- FECHA_NACIMIENTO (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_CON_TRANSFORMACION
- NACIONALIDAD (EXTRANJEROS_REGULARES_2026): 96.7% - DISPONIBLE_PARCIAL
- TIPO_RESIDENCIA_ESTUDIANTE (EXTRANJEROS_REGULARES_2026): 0.0% - NO_DISPONIBLE
- PAIS_DE_ORIGEN (EXTRANJEROS_REGULARES_2026): 0.0% - NO_DISPONIBLE
- PAIS_ESTUDIOS_SECUNDARIOS (EXTRANJEROS_REGULARES_2026): 53.3% - DISPONIBLE_PARCIAL
- CODIGO_UNICO (EXTRANJEROS_REGULARES_2026): 53.3% - DISPONIBLE_MEDIANTE_CRUCE
- ANIO_INGRESO_CARRERA_ACTUAL (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_DIRECTO
- SEM_INGRESO_CARRERA_ACTUAL (EXTRANJEROS_REGULARES_2026): 100.0% - DISPONIBLE_DIRECTO
- ANIO_INGRESO_CARRERA_ORIGEN (EXTRANJEROS_REGULARES_2026): 53.3% - DISPONIBLE_MEDIANTE_CRUCE
- SEM_INGRESO_CARRERA_ORIGEN (EXTRANJEROS_REGULARES_2026): 53.3% - DISPONIBLE_MEDIANTE_CRUCE
- NOMBRE_UNIVERSIDAD_ORIGEN (EXTRANJEROS_REGULARES_2026): 0.0% - REQUIERE_CONFIRMACION_INSTITUCIONAL
- PAIS_UNIVERSIDAD_ORIGEN (EXTRANJEROS_REGULARES_2026): 0.0% - NO_DISPONIBLE
- VIGENCIA (EXTRANJEROS_REGULARES_2026): 53.3% - DISPONIBLE_MEDIANTE_CRUCE

## Brechas criticas

- NUM_DOCUMENTO: 100.0% (DISPONIBLE_DIRECTO)
- NACIONALIDAD: 96.7% (DISPONIBLE_PARCIAL)
- TIPO_RESIDENCIA_ESTUDIANTE: 0.0% (NO_DISPONIBLE)
- PAIS_DE_ORIGEN: 0.0% (NO_DISPONIBLE)
- PAIS_ESTUDIOS_SECUNDARIOS: 53.3% (DISPONIBLE_PARCIAL)

## Conflictos detectados

- MULTIPLES_CODIGOS_UNICOS_AVANCE_2025: 2
- CODCARPR_CON_PUENTE_SIES_AMBIGUO: 15

## Propuesta de cruce

1. Documento exacto normalizado.
2. CODCLI solo como llave interna mediante equivalencias trazables.
3. CODCARPR + jornada + modalidad + version para obtener CODIGO_UNICO con puente SIES/oferta.
4. Nombre y fecha de nacimiento solo para diagnostico.

## Campos que requieren gestion institucional

- TIPO_RESIDENCIA_ESTUDIANTE: ausente para todos los candidatos.
- PAIS_DE_ORIGEN: condicional a residencia 2/3; no disponible.
- PAIS_ESTUDIOS_SECUNDARIOS: requiere confirmacion de secundaria completada.
- NACIONALIDAD: un caso `Por definir`.
- CODIGO_UNICO: resolver ambiguedades de puente antes de carga.

## Siguiente fase recomendada

Levantar con Docencia/Registro Academico una planilla de resolucion de campos criticos para los candidatos 2025, confirmar si existe universo de intercambio 2025 y luego implementar transformaciones en un script separado con pruebas y auditoria.

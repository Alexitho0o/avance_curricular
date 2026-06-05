# Instrucciones Personal Academico SIES 2026

Estas instrucciones gobiernan el desarrollo futuro del modulo `personal_academico_2026/`.

## Principios

- No inventar campos, codigos, catalogos ni reglas.
- Usar como fuentes principales solo las tres fuentes oficiales conservadas en `insumos/`.
- Distinguir siempre entre regla normativa explicita y validacion tecnica preventiva.
- Documentar todo pendiente cuando el instructivo no explicite una regla.
- Mantener todo cambio dentro de `personal_academico_2026/`, salvo autorizacion expresa.

## Fuentes Permitidas

Las reglas normativas solo pueden provenir de:

1. `20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv`.
2. `20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv`.
3. `Personal Académico SIES - Instructivo 2026.txt`.

Si se necesita una regla no contenida en esas fuentes, debe quedar como pendiente de confirmacion antes de programar o exportar.

## Estructura Antes De Exportar

Todo desarrollo futuro debe validar, antes de producir un archivo candidato:

- Cantidad exacta de columnas.
- Orden exacto de columnas.
- Nombres oficiales de columnas.
- Ausencia de columnas adicionales.
- Ausencia de indices exportados.
- Control explicito de encabezado segun el uso: plantilla de estructura versus archivo de carga PES.
- Delimitador CSV conforme a la definicion oficial que se confirme para la entrega.

## Exportacion

- Generar solo CSV finales validos para PES/SIES.
- No producir archivos finales en esta fase inicial.
- No agregar columnas auxiliares a los CSV finales.
- No exportar indices.
- No sobrescribir resultados anteriores.
- Registrar toda exportacion futura en `auditorias/` y `bitacoras/`.

## Separacion De Artefactos

- `insumos/`: fuentes oficiales e insumos originales.
- `scripts/`: codigo del modulo.
- `resultados/`: salidas candidatas o finales versionadas.
- `auditorias/`: evidencia de validacion previa y posterior.
- `bitacoras/`: decisiones y pendientes.
- `catalogos/`: catalogos confirmados o derivados con fuente explicita.
- `tests/`: pruebas automatizadas.

## Validaciones Futuras

Todo script futuro debe incluir validaciones previas y producir evidencia auditable. Como minimo:

- Validacion estructural contra los CSV oficiales.
- Validacion de campos obligatorios explicitamente definidos.
- Validacion de formatos descritos en el instructivo.
- Validacion de duplicados por identificacion.
- Validacion de reglas horarias, fechas, vigencia y codigos cuando esten respaldadas por el instructivo.
- Reporte de pendientes o ambiguedades normativas antes de liberar una carga.

## No Intervencion

Queda prohibido para este modulo, salvo instruccion explicita:

- Modificar scripts de Matricula Unificada, Avance Curricular, CNED o flujos historicos.
- Usar `archive/` como fuente final.
- Sobrescribir outputs existentes en `resultados/` u otras carpetas globales.
- Cambiar dependencias globales.
- Refactorizar el repositorio fuera del alcance de Personal Academico SIES 2026.

## Reglas De Exportacion Final

- La exportacion final queda bloqueada por defecto.
- `scripts/exportar_personal_academico_2026.py` solo puede generar salida si se entrega `--permitir-exportacion-final true`.
- Antes de exportar debe validarse estructura exacta: cantidad, nombres, orden, sin columnas faltantes y sin columnas adicionales.
- Si el archivo de entrada tiene todas las columnas oficiales pero en otro orden, el exportador puede reordenar solo antes de exportar y debe dejar evidencia en auditoria.
- La salida debe escribirse siempre sin indice.
- La salida queda sin encabezado por defecto por la instruccion operativa documentada de eliminar encabezado antes de subir a PES.
- El delimitador de salida esta parametrizado. Por defecto se usa coma porque el instructivo menciona CSV delimitado por comas.
- La tension entre estructura observada con `;` e instructivo con coma queda como **PENDIENTE DE CONFIRMACION** y debe registrarse en cada auditoria de exportacion.
- No se debe habilitar exportacion final sin auditoria aprobada y decision documentada sobre delimitador y encabezado.

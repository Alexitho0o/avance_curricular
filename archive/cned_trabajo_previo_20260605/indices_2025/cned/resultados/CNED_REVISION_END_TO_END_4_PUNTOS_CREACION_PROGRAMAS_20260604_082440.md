# Revision End to End 4 Puntos - Creacion de Programas CNED/INDICES

## Dictamen ejecutivo

- Dictamen operativo: REQUIERE_REVISION_MANUAL_ANTES_DE_CREAR
- Fuente principal validada: PROMEDIOSDEALUMNOS_7804.xlsx, hoja matriz
- Fuente de existentes validada: indices_2025/cned/data/listado_referencia_cned.tsv
- Artefacto auditado: indices_2025/cned/resultados/CNED_PROGRAMAS_FALTANTES_CREAR_INDICES_DESDE_PROMEDIOS_20260604_082355.xlsx
- Hoja principal para digitacion manual: PROGRAMAS_FALTANTES_PARA_CREAR

## Conteos validados

- Total oferta en matriz: 139
- Total vigentes: 139
- Total ya existentes en INDICES: 64
- Total falta crear en INDICES: 71
- Total dudosos para revision manual: 4
- Total no crear: 0
- Codigos esperados auditados: 29 de 29 presentes en auditoria y en hoja principal

## Punto 1 - Hojas criticas del Excel

Se validaron sin faltantes las hojas criticas:

- RESUMEN_EJECUTIVO
- AUDITORIA_CODIGOS_ESPERADOS
- DUDOSOS_REVISAR_MANUAL
- PROGRAMAS_FALTANTES_PARA_CREAR

Resultado: OK

## Punto 2 - Consistencia entre Excel, CSV, JSON y Markdown

- El CSV companion coincide exactamente con la hoja PROGRAMAS_FALTANTES_PARA_CREAR en columnas, cantidad de filas y contenido.
- El JSON companion refleja los conteos auditados del proceso.
- El Markdown companion existe y corresponde al mismo set timestamped de salida.

Resultado: OK

## Punto 3 - Integridad de CODIGO_UNICO y codigos esperados

- CODIGO_UNICO vacios en hoja principal: 0
- CODIGO_UNICO duplicados en hoja principal: 0
- Formato de CODIGO_UNICO: OK para las 71 filas faltantes
- Codigos esperados presentes en AUDITORIA_CODIGOS_ESPERADOS: 29/29
- Codigos esperados presentes en PROGRAMAS_FALTANTES_PARA_CREAR: 29/29
- Codigos esperados presentes en DUDOSOS_REVISAR_MANUAL: 0

Resultado: OK

## Punto 4 - Completitud operativa de la hoja principal

- Campos del formulario INDICES presentes: 25/25
- Ajuste aplicado en esta corrida: la columna Duracion del programa en Semestres quedo exportada con el rotulo exacto esperado por la auditoria.
- Las 71 filas de la hoja principal quedaron clasificadas como FALTA_CREAR_EN_INDICES.
- No se detectaron estados YA_EXISTE dentro de la hoja principal.

Campos que siguen requiriendo digitacion o confirmacion manual en multiples filas:

- Mencion o Especialidad
- Ano de inicio de Actividades
- Campus
- Horario
- Detalle del Tipo de Programa (especiales)
- Modalidad del Programa
- Area del Conocimiento
- Sub Area
- Carrera Generica
- Titulo que otorga el programa
- Grado Academico que otorga el programa
- Dependencia
- Regimen
- Ingreso Directo
- Ingreso desde un plan Comun
- Ingreso desde Bachillerato
- Otro Tipo de Ingreso
- Ingreso otro

Resultado: OK con revision manual requerida

## Riesgos residuales no bloqueantes

- Existen 4 registros en DUDOSOS_REVISAR_MANUAL que deben revisarse antes de crear programas ambiguos.
- La hoja PROGRAMAS_EXISTENTES_NORMALIZADOS se exporta como PROGRAMAS_EXIST_NORMALIZADOS por el limite de 31 caracteres de Excel.
- El mapeo de TIPO_PLAN_CARRERA usa una regla empirica mayoritaria: 1 -> Programa Regular y 3 -> Programa Especial.
- Los casos con MODALIDAD=2 o JORNADA=3 mantienen valores REVISAR cuando no hay evidencia suficiente en la base existente.

## Conclusión

El artefacto operativo actualizado es apto para trabajo manual guiado y mantiene trazabilidad completa hacia matriz y referencia INDICES. No hay errores bloqueantes en la generacion ni en la auditoria de 4 puntos, pero la creacion debe ejecutarse con revision humana sobre los 4 dudosos y sobre los campos marcados como REVISAR.
# CNED Artefacto Operativo Limpio

## Dictamen

BASE_CNED_LIMPIA_LISTA_PARA_USO_OPERATIVO

## Archivos generados

- Excel: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_130339.xlsx
- CSV: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/data/BASE_CNED_LIMPIA_OPERATIVA.csv
- Markdown: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_ARTEFACTO_OPERATIVO_LIMPIO_20260603_130339.md
- Script: /Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/scripts/06_materializar_artefacto_operativo_cned_limpio.py

## Conteos

- BASE_CNED_LIMPIA: 59 registros
- SIN_CODIGO_SIES: 7 registros
- DUPLICADOS_CNED declarados: 288 registros
- Código SIES vacíos en BASE_CNED_LIMPIA: 0
- CLAVE_OPERATIVA únicas en BASE_CNED_LIMPIA: 59
- VALIDACION_CODIGO_UNICO = OK: 59
- VALIDACION_COD_CARRERA = REVISAR_COD_CARRERA: 59

## Validaciones principales

- BASE_CNED_LIMPIA = 59 filas
- Código SIES vacíos = 0
- CLAVE_OPERATIVA únicas = 59
- VALIDACION_CODIGO_UNICO = OK en 59 registros
- VALIDACION_COD_CARRERA = REVISAR_COD_CARRERA en 59 registros
- Pregrado/Posgrado = Pregrado en 59 registros
- Distribución Horario = Diurno 14, Otro 22, Vespertino 23
- Distribución JOR_DERIVADA = 1:14, 2:23, 4:22
- Formato Código SIES = OK en 59 registros
- Derivados del Código SIES coherentes con COD_SED/COD_CAR/JOR/VERSION
- SIN_CODIGO_SIES = 7 filas
- SIN_CODIGO_SIES conserva 7 Código SIES vacíos

## Advertencias

- REVISAR_COD_CARRERA es advertencia no bloqueante; Cód. Carrera CNED y COD_CAR_DERIVADO no son equivalentes directos.
- DUPLICADOS_CNED no incluye el detalle fila a fila porque ese detalle no fue pegado en el prompt; se registran los 288 duplicados declarados para trazabilidad.

## Reglas de uso

- No modificar Hoja1.
- No modificar archivos originales.
- No actualizar DATOS_VALIDACION_CNED_TSV.tsv.
- No actualizar DATOS_VALIDACION_CNED_TSV_ACTUALIZADO.tsv.
- Usar BASE_CNED_LIMPIA en grano CLAVE_OPERATIVA.
- Validar operativamente con Código SIES, COD_SED_DERIVADO, COD_CAR_DERIVADO, JOR_DERIVADA, VERSION_DERIVADA y CLAVE_OPERATIVA.
- Mantener SIN_CODIGO_SIES separado para revisión manual.

## Cierre

Con base exclusivamente en la información entregada en el prompt, el dictamen es BASE_CNED_LIMPIA_LISTA_PARA_USO_OPERATIVO. Sin embargo, el artefacto operativo aún debía materializarse en el proyecto, ya que el TSV manual disponible contenía solo encabezados y 0 filas.

Este proceso materializa un artefacto operativo controlado en Excel y CSV, sin modificar la hoja original, sin actualizar el TSV base y sin automatizar sustituciones. La base final queda en el grano CLAVE_OPERATIVA, con 59 registros de Pregrado, 0 códigos SIES vacíos, 0 claves duplicadas y validación fuerte sobre Código SIES y sus derivados.

La advertencia REVISAR_COD_CARRERA no bloquea el uso de la base, porque Cód. Carrera CNED y COD_CAR_DERIVADO pertenecen a naturalezas distintas. La validación operativa debe realizarse sobre Código SIES, COD_SED_DERIVADO, COD_CAR_DERIVADO, JOR_DERIVADA, VERSION_DERIVADA y CLAVE_OPERATIVA.

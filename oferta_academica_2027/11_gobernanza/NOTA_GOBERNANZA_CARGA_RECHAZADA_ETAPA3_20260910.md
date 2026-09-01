# Nota de gobernanza - Carga rechazada Etapa 3

- Proceso: SIES Oferta Academica-Acceso 2027.
- Etapa: 3 - Definicion de Arancel.
- Fecha de intento: 10-09-2026.
- Archivo enviado: `20260910 Carga 1.csv`.
- Estado PES: rechazado.
- Registros del archivo: 140.
- Estructura observada: {49: 140}.
- Estructura exigida por PES: 13 columnas.
- Universo observado: 88 registros con vigencia 1 y 52 con vigencia 2.
- Lineas con errores mostradas por PES: 100.
- Comparacion contra la salida preparada de 13 columnas: PRESENTA_DIFERENCIAS_CON_ARCHIVO_ETAPA3_PREPARADO.

## Decision

La carga queda registrada como `RECHAZADA_POR_ESTRUCTURA`. El archivo enviado contiene la estructura completa de 49 columnas y ademas incluye registros con vigencia 2. No corresponde al formato ni al universo de carga de Etapa 3. Los mensajes adicionales sobre campos y claves duplicadas no se consideran concluyentes porque fueron emitidos sobre una estructura desplazada. No se modifica el original ni se declara una carga exitosa.

La comparacion con la salida del 07-09-2026 muestra cambios en `VALOR_MATRICULA_ANUAL` (140 filas) y `ARANCEL_ANUAL` (62 filas). El derivado de reintento conserva los valores del archivo efectivamente enviado el 10-09-2026; no reutiliza automaticamente los montos anteriores.

## Reanudacion

Usar el derivado `07_resultados/etapa3_aranceles_20260910/OFERTA_ACADEMICA_ARANCELES_2027_CARGA_02_CORREGIDA_SIN_TITULOS_20260910.csv`. Contiene solo vigencia 1 y la estructura de 13 columnas. Registrar el nuevo resultado PES como una ejecucion separada.

## Fuente oficial aplicada

Instructivo Oferta Academica-Acceso 2027, Anexo 4, pagina 65: estructura de 13 columnas, prohibicion de modificar identificadores y carga exclusiva de programas con vigencia 1.

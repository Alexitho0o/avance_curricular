# Carga congelada Etapa 2 - Oferta Academica Nueva TP Adscritas (ID 17451)

**Archivo:** `28-08-2026_13-17-17_Oferta-Académica-TP-Nueva-2027.csv`
**SHA-256:** `afa38755cb5e449011ab226588505238aa41c07acdb65acf31452abc6eb3d38f`
**Tamano:** 12.548 bytes
**Fecha/hora de carga:** 28/08/2026 13:17:17
**Proceso:** Oferta Academica 2027 - Proceso 2026 - Etapa 2 (carga ID 17451)
**Institucion:** Codigo IES 162

## Que es este archivo

Es el archivo exacto que la institucion cargo en la plataforma SIES para la Etapa 2. Se guarda
congelado como respaldo de trazabilidad: es la evidencia de que fue efectivamente informado.

## Verificacion de identidad (28/08/2026)

Se verificaron tres copias independientes y las tres resultaron byte a byte identicas
(mismo SHA-256 `afa38755...`):

1. El archivo en la carpeta Downloads del usuario (nombre original del sistema).
2. La copia generada por el proyecto en
   `07_resultados/borradores_prueba_no_oficiales/OFERTA_ACADEMICA_ETAPA2_RECTOR_V2_CSV_PRUEBA_NO_OFICIAL_20260828.csv`
3. La copia entregada por el usuario para revision.

## Estructura verificada

- 37 filas de datos, las 37 con exactamente 48 campos.
- Delimitador: punto y coma (`;`). Codificacion UTF-8. Salto de linea simple (`\n`), sin CRLF.
- Sin fila de encabezado y sin linea final vacia, como exige el instructivo.
- `COD_CARRERA` vacio en las 37 filas (el instructivo indica: "El COD_CARRERA no debe ser
  cargado en esta etapa").
- `VIGENCIA_CARRERA` = 1 en las 37 filas.
- `DURACION_ESTUDIOS + DURACION_TITULACION = DURACION_TOTAL` en las 37 filas.
- `SEMESTRES_RECONOCIDOS` dentro del rango 0-14 en las 37 filas.
- Ninguna fila con `COD_NIVEL_CARRERA`=2 tiene columnas AREA_* distintas de 0.
- Toda fila con `COD_NIVEL_CARRERA`=1 tiene en 1 la columna AREA_* que corresponde a su
  `AREA_ACTUAL`.
- Sedes presentes: COD_SEDE 2 (Casa Central, 23 filas), 3 (Concepcion, 10), 4 (Patagonia, 4).

## Diferencias respecto de la fuente institucional

Comparado campo por campo contra `03_fuentes_institucionales/entregas_docencia/
20260828_etapa2_entrega_02/Oferta 2027 Etapa2_rector_v2.xlsx`, las UNICAS diferencias son las
cinco correcciones ya documentadas. No hay ninguna otra:

| Campo | Filas | Cambio | Justificacion |
|---|---|---|---|
| CARACTERISTICAS_TIPO_PLAN | 37 | `No Aplica` -> `NO APLICA` | Instructivo: usar MAYUSCULAS; valor literal "NO APLICA". Normalizacion de formato. |
| VALOR_MATRICULA_ANUAL | 37 | `0` -> `-1` | Autorizado por el usuario. Sentinel oficial "sin informacion". Montos se declaran en Etapa 3. |
| ARANCEL_ANUAL | 37 | `0` -> `-1` | Autorizado por el usuario. Instructivo: con VIGENCIA=1 debe ser >0 o -1. |
| AREA_TECNO_INFO_COMUNICA | 3 | `0` -> `1` | Filas con AREA_ACTUAL=10 y COD_NIVEL_CARRERA=1. Regla del instructivo. |
| AREA_ADMIN_DERECHO | 3 | `0` -> `1` | Filas con AREA_ACTUAL=1 y COD_NIVEL_CARRERA=1. Regla del instructivo. |
| COD_SEDE | 1 | `` -> `3` | TECNICO EN FARMACIA / SEDE CONCEPCION. Autorizado por el usuario. |

Ningun otro valor fue modificado, imputado ni inventado. El archivo institucional
`rector_v2.xlsx` NO fue modificado en ningun momento.

## Registros excluidos de esta carga

Esta carga contiene 37 de las 49 filas del archivo institucional. Las 12 restantes fueron
excluidas porque el sistema las rechaza con "La Carrera o Programa que esta ingresando como
nueva, ya existe en la Oferta Vigente Validada". SIES confirmo por correo (28/08/2026) que no
corresponden a Etapa 2, y se tramitan por Rectificacion de Etapa 1 mediante oficio. Ver
`12_pendientes/REGISTRO_BLOQUEO_ETAPA2_20260827.txt`, actualizaciones 20260828l en adelante.

## Nota sobre 6 registros aceptados que ya existian

Seis filas de esta carga coinciden con un programa ya presente en la Oferta Vigente Validada
(reporte 5912) segun sede+carrera+modalidad+jornada+tipo_plan+nivel+titulo, y aun asi el
sistema las acepto: Tecnico en Conectividad y Redes, Tecnico en Ciberseguridad, Tecnico en
Programacion y Analisis de Sistemas, Tecnico en Administracion de Empresas (dos registros) y
Tecnico en Logistica. En las seis, DURACION_ESTUDIOS y DURACION_TOTAL cambian de 5 a 4
semestres. Esto es coherente con la regla que SIES entrego: solo los cambios en duracion de
estudios y duracion total constituyen una version nueva.

## Pendiente asociado

Los montos (arancel, matricula, costo de titulacion, costo de certificado) quedan en -1 / 0 en
esta etapa y deben declararse en la Etapa 3 (Definicion de Arancel TP, carga ID 17454, ventana
07 al 11 de septiembre de 2026).

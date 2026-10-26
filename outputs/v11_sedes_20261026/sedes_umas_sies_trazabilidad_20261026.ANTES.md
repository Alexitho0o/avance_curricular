# Sedes UMAS y componente SIES: trazabilidad IPSS 162

Fecha: 2026-10-26. Alcance: conciliación y seguimiento institucional; no modifica cargas, bases, denominadores ni el puntero del diccionario.

## Interpretación

- **C**: en `I162S3C91J2V1`, `S3` es el componente de sede del código para esa institución. Por sí solo no identifica carrera, jornada ni versión; debe interpretarse junto con `I162` y el año y proceso de la fuente. No extrapolar la numeración a otras instituciones o años sin evidencia.
- **B/C**: `data/gobernanza_sede.tsv` registra RE → 2, CASA CENTRAL (SANTIAGO), y CO → 3, SEDE CONCEPCION, con validación declarada contra oferta. El catálogo es evidencia institucional existente; no constituye por sí solo una aprobación de una asignación individual de carrera o versión.
- **B**: `procesos/caracterizacion/docs/gobernanza/CATALOGO_SEDES_2027.json` registra RE Santiago, CO Concepción y PTG Patagonia para 2027 P1; la autoridad declarada es confirmación del usuario. No registra códigos SIES para PTG.
- **B/E**: `oferta_academica_2027/06_validaciones/CONCILIACION_ETAPA2_VS_REPORTE_5912_20260828_rector_v2.json` contiene registros institucionales con `cod_sede: 4` y `nombre_sede: SEDE PATAGONIA`. En algunos de ellos la coincidencia 5912 mostrada corresponde a sede 2; por tanto no acreditar con ese campo una coincidencia SIES sede 4. PTG → S4 queda propuesto y pendiente de corroboración directa por edición y fuente.
- **B/E**: `outputs/v11_fase1_cobertura_20261026/PROPUESTA_D_SEDE_CO.json` propone para 2026 las familias COTEIQ/CO/V → I162S3C114J2, COTENS/CO/V → I162S3C91J2 y COTFAR/CO/V → I162S3C115J2. La propuesta señala una excepción de COTEIQ en MU: 34/35 con C114J2V1 y 1 con C91J2V1. Es fuente local sin seguimiento en Git al momento de esta nota; no se promueve una asignación personal ni se declara aprobada la propuesta de programas.

## Direcciones aportadas por Alexi

- **D/B**: Santiago: Miguel Claro 337, Providencia, Santiago; Concepción: Avenida Lientur 1457, Concepción; Puerto Montt: Lago Panguipulli 1390, Puerto Montt. Son antecedentes proporcionados por el usuario el 2026-10-26; no se verificó una fuente documental institucional que vincule esas direcciones con los códigos SIES o la denominación Patagonia. No usar la dirección para asignar una sede sin evidencia adicional.

## Uso y pendientes

- **C**: consultar siempre `PROYECTO_IPSS.json` → recurso común `diccionario_sies_seguimiento` y el descriptor activo para resolver códigos por expediente y período. La sede es solo una dimensión de la clave; no asignar versión por año, nombre o totales agregados.
- **E**: verificar en el informe o precarga SIES con identificador de sede y edición aplicable la correspondencia S4 ↔ PTG/Puerto Montt, y las direcciones. Confirmar el alcance y aprobación de las equivalencias por programa antes de aplicarlas. No descartar la excepción documentada.
- **E**: el CSV público de matrícula 2007–2026 existente en `CARACTERIZACIÓN/gobernanza/sies` es un puntero LFS en este entorno; su presencia no acredita lectura del contenido. Las cifras 3.352 y 73 no se recalcularon para esta nota.
- **C**: esta nota es documentación local preparada para revisión. La publicación de Git y la actualización del complemento remoto requieren sus respectivos mecanismos de publicación; no se infieren de la edición local.

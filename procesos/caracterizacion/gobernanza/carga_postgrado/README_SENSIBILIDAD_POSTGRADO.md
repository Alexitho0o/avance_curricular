# Control de sensibilidad — Carga Postgrado

Fecha: 2026-05-13 17:44:20

## Estado

Se reorganizó la evidencia de `gobernanza/carga_postgrado` para separar núcleo productivo, datos sensibles, documentación, scripts auxiliares y respaldos históricos.

## Estructura

- `nucleo_productivo/`: script vigente principal.
- `datos_sensibles/`: archivos de datos con posible presencia de RUT u otros identificadores.
- `documentacion_apoyo/`: manuales, mapas, guías y documentos de referencia.
- `historico_backups/`: respaldos históricos de código.
- `scripts_auxiliares/`: scripts no centrales.
- `control_sensibilidad/`: registros de esta reorganización.

## Advertencia

El archivo `reporte_matricula_ip_san_sebastian.csv` fue clasificado como `DATOS_POSTGRADO` y contiene posible `RUT sin DV`.

No subir a repositorios remotos, compartir ni publicar este paquete sin revisar la política institucional de datos personales y sin confirmar autorización.

## Criterio

Esta reorganización no borra evidencia; solo ordena internamente el paquete de postgrado para evitar mezclar núcleo técnico, datos sensibles y respaldos históricos.

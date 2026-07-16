# H97 — SIES_READY 21 campos con FECHA_NACIMIENTO y sin VIGENCIA

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Matrícula Avance Curricular 2026, ID Carga 16768.

## Motivo

La carga H96 demostró que la plataforma sí esperaba `FECHA_NACIMIENTO`, porque al eliminarlo el `CODIGO_UNICO` fue leído como fecha.

## Corrección aplicada

- Se conserva `FECHA_NACIMIENTO`.
- Se excluye `VIGENCIA`.
- Se normaliza `FECHA_NACIMIENTO` a formato `AAAA-MM-DD`.
- Se mantiene CSV sin encabezado y delimitado por punto y coma.

## Resultado

- Filas: 2371
- Columnas: 21
- CSV sin encabezado: SI
- Separador: punto y coma
- Encoding: latin1
- Fuentes originales modificadas: NO

## Archivo a subir

`/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/97_sies_ready_21_campos_con_fecha_sin_vigencia_5809/SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA_5809_20260709_033145/5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA.csv`

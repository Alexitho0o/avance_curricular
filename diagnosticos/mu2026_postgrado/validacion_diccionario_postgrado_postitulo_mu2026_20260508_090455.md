# Validación diccionario gobernado postgrado/postítulo MU2026

Fecha ejecución: Fri May  8 09:04:55 -04 2026
Backup previo: control/diccionarios/diccionario_postgrado_postitulo_mu2026_backup_20260508_090455.tsv
Diccionario corregido: control/diccionarios/diccionario_postgrado_postitulo_mu2026.tsv

## 1. Validación cantidad de columnas
```
columnas_header=16
filas_validadas=23
errores_columnas=0
```

## 2. Resumen por ESTADO_GOBERNANZA
```
MATCH_EXACTO_NOMBRE 8
MATCH_MANUAL_GOBERNADO 2
MATCH_NORMALIZADO_NOMBRE 4
NO_MAPEAR_GENERICO 1
PENDIENTE_REVISION 7
POSIBLE_MATCH_REVISION_MANUAL 1
```

## 3. Resumen por ACCION_CARGA
```
EXCLUIR 1
EXCLUIR_HASTA_VALIDAR 8
INCLUIR 14
```

## 4. Validación de registros INCLUIR con campos críticos completos
```
INCLUIR_total=14
INCLUIR_incompletos=0
```

## 5. Pendientes gobernados
```
DCSI      DIPLOMADO EN CIBERSEGURUDAD INDUSTRIAL                        POSIBLE_MATCH_REVISION_MANUAL  EXCLUIR_HASTA_VALIDAR
ECCURYDP  EC CURSOS Y DIPLOMADOS                                        NO_MAPEAR_GENERICO             EXCLUIR
DDSC      DIPLOMADO EN DATA SCIENCE                                     PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
DDASC     DIPLOMADO EN DATA SCIENCE                                     PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
DHIAD     DIPLOMADO HERRAMIENTAS DE IA PARA EL APOYO DOCENTE            PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
DDSS      DIPLOMADO DESARROLLO SEGURO DE SOFTWARE                       PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
DAPB      DIPLOMADO EN ANALYTICS Y VISUALIZACIÓN DE DATOS CON POWER BI  PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
DGAS      DIPLOMADO EN GESTIÓN ÁGIL CON SCRUM                           PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
DLEMS     DIPLOMADO LIDERAZGO ESTRATÉGICO Y MANAGEMENT 4.0              PENDIENTE_REVISION             EXCLUIR_HASTA_VALIDAR
```

## 6. Regla de uso

- ACCION_CARGA=INCLUIR: puede alimentar trazabilidad y CSV PES-ready.
- ACCION_CARGA=EXCLUIR_HASTA_VALIDAR: solo trazabilidad; no CSV final.
- ACCION_CARGA=EXCLUIR: no mapear a un único COD_CAR.
- No modifica flujo pregrado.

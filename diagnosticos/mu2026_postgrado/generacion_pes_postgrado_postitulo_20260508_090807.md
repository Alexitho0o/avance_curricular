# Generación preliminar PES-ready postgrado/postítulo MU2026

Fecha ejecución: Fri May  8 09:08:07 -04 2026
Trazabilidad fuente: resultados/trazabilidad_matricula_unificada_2026_postgrado_postitulo.tsv
Control con encabezado: resultados/matricula_unificada_2026_postgrado_postitulo_control.csv
PES-ready sin encabezado: resultados/matricula_unificada_2026_postgrado_postitulo.csv

## 1. Archivos generados

```
resultados/matricula_unificada_2026_postgrado_postitulo_control.csv
resultados/matricula_unificada_2026_postgrado_postitulo.csv
```

## 2. Resumen generación

- Registros base 2026 con ACCION_CARGA=INCLUIR: 55
- Registros OK para PES-ready: 55
- Registros bloqueados en control: 0

## 3. Distribución por COD_CAR en PES-ready

| COD_CAR | n |
|---|---:|
| 70 | 22 |
| 53 | 18 |
| 66 | 15 |

## 4. Distribución VIG

| VIG | n |
|---|---:|
| 1 | 55 |

## 5. Bloqueados

No hay registros bloqueados.

## 6. Validación estructura PES-ready

| campos_por_fila | filas |
|---:|---:|
| 21 | 55 |

- Filas PES-ready: 55

## 7. Regla aplicada

- Archivo PES-ready: sin encabezado, delimitado por punto y coma.
- Archivo control: con encabezado y columnas de auditoría.
- Solo se cargan registros 2026 con ACCION_CARGA=INCLUIR y validación completa.
- No se modifica flujo pregrado.

# Auditoría final PES-ready · Postgrado/Postítulo · MU2026

**Fecha de ejecución:** 2026-05-08 09:14:18

---

## Resumen ejecutivo

| Indicador | Valor |
|---|---|
| Estado global | **APROBADO_CON_OBSERVACIONES** |
| Filas PES-ready | 55 |
| Campos por fila | 21 |
| Errores críticos | 0 |
| Advertencias | 1 |
| Registros bloqueados en control | 0 |
| Candidatos 2026 total | 72 |
| Candidatos 2026 incluidos | 55 |
| Candidatos 2026 excluidos | 17 |

---

## Archivos auditados

| Archivo | Ruta |
|---|---|
| Diccionario | `control/diccionarios/diccionario_postgrado_postitulo_mu2026.tsv` |
| Trazabilidad | `resultados/trazabilidad_matricula_unificada_2026_postgrado_postitulo.tsv` |
| Control CSV | `resultados/matricula_unificada_2026_postgrado_postitulo_control.csv` |
| PES-ready preliminar | `resultados/matricula_unificada_2026_postgrado_postitulo.csv` |

---

## Resultado global: APROBADO_CON_OBSERVACIONES

El archivo PES-ready es estructuralmente válido. Existen candidatos 2026 excluidos por gobernanza,
correctamente documentados fuera del CSV final. Ver sección de excluidos.

---

## FASE 1 · Estructura del PES-ready

- Total filas: **55**
- Campos por fila: {21: 55}
- Filas vacías: 0
- Filas con campo vacío: 0
- Sin encabezado: OK

**Sin errores estructurales.**

---

## FASE 2 · Validación de dominios

- Errores de dominio: 0
- Registros con TIPO_DOC=P (pasaporte): 0
- Registros con ANIO_ING_ORI=1900: 0

**Todos los dominios son válidos.**

### Advertencias fase 2
- No hay registros con TIPO_DOC=P (pasaporte). Cero casos detectados.

### Distribuciones del PES-ready

**COD_CAR**

| COD_CAR | n |
|---|---:|
| 70 | 22 |
| 53 | 18 |
| 66 | 15 |

**COD_SED**

| COD_SED | n |
|---|---:|
| 2 | 55 |

**MODALIDAD**

| MODALIDAD | n |
|---|---:|
| 3 | 37 |
| 2 | 18 |

**JOR**

| JOR | n |
|---|---:|
| 4 | 37 |
| 3 | 18 |

**VERSION**

| VERSION | n |
|---|---:|
| 1 | 55 |

**VIG**

| VIG | n |
|---|---:|
| 1 | 55 |

**SEXO**

| SEXO | n |
|---|---:|
| H | 51 |
| M | 4 |

**FOR_ING_ACT**

| FOR_ING_ACT | n |
|---|---:|
| 1 | 35 |
| 10 | 20 |

---

## FASE 3 · Contraste PES-ready vs control

- Registros PES-ready: 55
- Registros control OK: 55
- Registros bloqueados: 0

**Consistencia total entre PES-ready y control.**

---

## FASE 4 · Contraste vs trazabilidad

### Resumen candidatos 2026

| Categoría | n |
|---|---:|
| Total candidatos 2026 | 72 |
| Incluidos | 55 |
| Excluidos hasta validar | 17 |
| Excluidos genérico | 0 |
| Excluidos otros | 0 |
| Sin diccionario | 0 |

**Todos los registros cargados provienen de ACCION_CARGA=INCLUIR y son año 2026.**

### Excluidos 2026 (detalle)

| CODCLI | RUT | CODCARPR | NOMBRE_L | ACCION_CARGA | ESTADO_GOBERNANZA | OBSERVACION |
|---|---|---|---|---|---|---|
| 20261DDASC001 | 20299187-4 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC002 | 15895590-3 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC003 | 19572724-4 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC004 | 26793816-4 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC005 | 20144816-6 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC006 | 20528652-7 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC007 | 20948099-9 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC008 | 15651488-8 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC009 | 15416526-6 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC010 | 15397331-8 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DDASC011 | 20643076-1 | DDASC | DIPLOMADO EN DATA SCIENCE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DHIAD001 | 13422085-6 | DHIAD | DIPLOMADO HERRAMIENTAS DE IA PARA EL APO | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DHIAD002 | 10515044-K | DHIAD | DIPLOMADO HERRAMIENTAS DE IA PARA EL APO | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DHIAD003 | 14111591-K | DHIAD | DIPLOMADO HERRAMIENTAS DE IA PARA EL APO | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DHIAD004 | 14201993-0 | DHIAD | DIPLOMADO HERRAMIENTAS DE IA PARA EL APO | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DLEMS001 | 20954371-0 | DLEMS | DIPLOMADO LIDERAZGO ESTRATÉGICO Y MANAGE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |
| 20261DLEMS002 | 16246532-5 | DLEMS | DIPLOMADO LIDERAZGO ESTRATÉGICO Y MANAGE | EXCLUIR_HASTA_VALIDAR | PENDIENTE_REVISION | No se encontró equivalente explícito en oferta/matriz revisa |

---

## FASE 5 · Contraste vs diccionario gobernado

- Registros evaluados: 55

**Todos los registros están trazados al diccionario. Combinaciones validadas.**

---

## Regla de gobernanza aplicada

- `ACCION_CARGA=INCLUIR`: alimenta trazabilidad, control y CSV PES-ready.
- `ACCION_CARGA=EXCLUIR_HASTA_VALIDAR`: queda solo en trazabilidad.
- `ACCION_CARGA=EXCLUIR`: no se carga. Si es genérico (`NO_MAPEAR_GENERICO`), tampoco.
- `NO_MAPEAR_GENERICO`: no se carga.
- No se fuerza COD_CAR para pendientes.
- Solo registros 2026 con criterio `ANOMATRICULA=2026 OR ANOINGRESO=2026`.

---

## Evidencia de integridad del flujo pregrado

Los siguientes archivos de pregrado NO fueron modificados por este proceso:

- `matricula_unificada_2026_pregrado.csv`: existe
- `matricula_unificada_2026_pregrado_PES_READY.csv`: existe
- `matricula_unificada_2026_control.csv`: existe

---

## Advertencias totales

- No hay registros con TIPO_DOC=P (pasaporte). Cero casos detectados.

---

## Artefactos generados

- `/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_postgrado_postitulo_excluidos_2026_gobernanza.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_postgrado_postitulo_PES_READY.csv`
- `/Users/alexi/Documents/GitHub/avance_curricular/resultados/matricula_unificada_2026_postgrado_postitulo_CONTROL_FINAL.csv`

---

## Recomendación final de carga

**PROCEDER CON CARGA CON PRECAUCIÓN.** El PES-ready es válido.
Los candidatos excluidos deben validarse manualmente antes de una carga complementaria.
Utilizar: `matricula_unificada_2026_postgrado_postitulo_PES_READY.csv`

---
*Generado automáticamente · 2026-05-08 09:14:18*
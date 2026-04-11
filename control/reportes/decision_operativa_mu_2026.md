# Decision Operativa MU 2026

Documento de contraste congelado al `2026-04-01`. Para operar hoy manda el gate vigente regenerado por `qa_checks.py` en `control/gate/gate_final_mu_2026.md`.

- Fecha de emision: 2026-04-01
- Decision congelada de referencia: `CONDICIONAL`
- Estado operativo de esa referencia:
  - Listo para auditoria: `SI`
  - Listo para carga: `NO`

## Criterio de decision actual

El proyecto queda en `CONDICIONAL` porque el CSV regulatorio y sus invariantes estan conformes, el tablero conserva trazabilidad completa y la evidencia disponible permite auditoria. Sin embargo, persisten cinco columnas en `Pendiente` cuya resolucion depende de fuente nueva o de una decision funcional/normativa explicita. Por esa razon el proyecto no debe presentarse como listo para carga.

## Ruta 1 - Cierre operativo actual

Esta ruta congela el proyecto en su estado vigente:

- auditable;
- no listo para carga; y
- pendiente de resolucion externa para `Y`, `Z`, `AB`, `AC` y `AE`.

### Implicancias de Ruta 1

- Se conserva el tablero en `27 OK / 5 Pendiente` sin reapertura tecnica.
- El paquete de evidencia vigente pasa a ser el insumo oficial para auditoria, comite o decision de negocio.
- Toda nueva ejecucion del pipeline debe mantener exactamente el mismo criterio, sin intentar cerrar tecnicamente los cinco pendientes.

## Ruta 2 - Reapertura controlada de los 5 bloqueos

Esta ruta solo se habilita si aparece al menos una de estas dos condiciones:

1. una fuente nueva suficiente por fila incluida; o
2. una decision funcional/normativa explicita que cierre la semantica faltante.

### Campos que pueden reabrirse bajo Ruta 2

- `Y ASI_INS_HIS`
- `Z ASI_APR_HIS`
- `AB SIT_FON_SOL`
- `AC SUS_PRE`
- `AE REINCORPORACION`

### Regla de reapertura controlada

- La reapertura debe limitarse solo al campo que reciba fuente o decision suficiente.
- No se reabren columnas ya marcadas en `OK`.
- No se programan nuevas reglas generales sin fuente nueva o definicion funcional/normativa explicitada.
- Todo cambio debe volver a pasar por tablero, evidencia, QA y gate binario `5/5 SI`.

## Que falta para pasar de `CONDICIONAL` a `APROBADO`

El proyecto solo puede pasar a `APROBADO` si los cinco campos pendientes salen de `Pendiente` y el tablero queda en `32/32 OK`, manteniendo:

- CSV final sin header;
- 32 columnas exactas;
- separador `;`;
- `SEXO` valido;
- la referencia congelada verificaba `FOR_ING_ACT = 1`;
- exclusion de `PRIMERA_OPCION`; y
- trazabilidad auditable por fila incluida para todos los campos.

Mientras cualquiera de los cinco bloqueos siga abierto, la decision correcta sigue siendo `CONDICIONAL`.

## Recomendacion ejecutiva

- Usar Ruta 1 como estado oficial inmediato del proyecto.
- Abrir Ruta 2 solo mediante mandato expreso del area dueña, con fuente nueva o criterio funcional/normativo firmado.

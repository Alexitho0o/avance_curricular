# Resumen Ejecutivo MU 2026

- Fecha de cierre ejecutivo: 2026-04-01
- Decision vigente del proyecto: `CONDICIONAL`
- Listo para auditoria: `SI`
- Listo para carga: `NO`

## Resumen del proyecto

El pipeline regulatorio de Matricula Unificada Pregrado 2026 quedo estabilizado en su alcance actualmente defendible. El archivo final mantiene conformidad estructural, trazabilidad operativa y evidencia auditable por columna para todo el bloque que pudo cerrarse con fuente o regla explicita.

El estado aprobado del tablero queda consolidado en `27 OK / 5 Pendiente`. No se reabren fases cerradas ni se promueven columnas sin fuente nueva o decision funcional/normativa suficiente.

## Estado consolidado del tablero

- Columnas en `OK` (27): `A TIPO_DOC`, `B N_DOC`, `C DV`, `D PRIMER_APELLIDO`, `E SEGUNDO_APELLIDO`, `F NOMBRE`, `G SEXO`, `H FECH_NAC`, `I NAC`, `J PAIS_EST_SEC`, `K COD_SED`, `L COD_CAR`, `M MODALIDAD`, `N JOR`, `O VERSION`, `P FOR_ING_ACT`, `Q ANIO_ING_ACT`, `R SEM_ING_ACT`, `S ANIO_ING_ORI`, `T SEM_ING_ORI`, `U ASI_INS_ANT`, `V ASI_APR_ANT`, `W PROM_PRI_SEM`, `X PROM_SEG_SEM`, `AA NIV_ACA`, `AD FECHA_MATRICULA`, `AF VIG`
- Columnas en `Pendiente` (5): `Y ASI_INS_HIS`, `Z ASI_APR_HIS`, `AB SIT_FON_SOL`, `AC SUS_PRE`, `AE REINCORPORACION`

## Por que el proyecto es auditable pero no cargable

El proyecto es auditable porque el CSV final conserva sus invariantes, el tablero mantiene trazabilidad por columna y los bloqueos residuales quedaron explicitados con evidencia, cuantificacion y siguiente accion concreta.

El proyecto no es cargable porque persisten cinco campos cuyo cierre requiere una fuente nueva o una decision funcional/normativa explicita. En estos cinco casos la evidencia actual alcanza para demostrar el bloqueo, pero no para sostener una declaracion de cumplimiento final cargable.

## Dependencias externas o funcionales reales

1. `Y ASI_INS_HIS`: falta fuente historica multianual o acto regulatorio explicito que autorice tratar alcance monoanual como historico acumulado.
2. `Z ASI_APR_HIS`: falta fuente historica multianual o acto regulatorio explicito que autorice tratar alcance monoanual como historico acumulado.
3. `AB SIT_FON_SOL`: falta fuente institucional por fila incluida o regla funcional formal que distinga estados `0/1/2`.
4. `AC SUS_PRE`: falta fuente institucional por fila incluida o regla funcional formal que cuantifique suspensiones previas.
5. `AE REINCORPORACION`: falta decision funcional/normativa o fuente de ultima carga valida que cierre la condicion temporal exigida por el manual.

## Costo de seguir sin nuevas fuentes o decisiones

- El proyecto puede mantenerse como insumo auditable, pero no puede declararse apto para carga regulatoria final.
- Se posterga la conversion del backlog residual en cierre operativo, manteniendo dependencia de escalamiento institucional.
- Se incrementa el costo de coordinacion entre gobierno de datos, registro academico y dueños funcionales, porque cada nueva ejecucion seguira terminando en `CONDICIONAL`.
- Se conserva riesgo de observacion regulatoria si se intentara cargar el archivo sin resolver la semantica de los cinco pendientes.

## Condicion exacta para pasar de `CONDICIONAL` a `APROBADO`

El proyecto solo puede pasar de `CONDICIONAL` a `APROBADO` si las cinco columnas residuales dejan de estar en `Pendiente`, con:

1. fuente o regla definida;
2. transformacion implementada;
3. validacion QA existente;
4. ausencia de default silencioso; y
5. trazabilidad auditable por fila incluida.

Mientras cualquiera de `Y`, `Z`, `AB`, `AC` o `AE` no cumpla `5/5 SI`, el proyecto debe mantenerse como auditable y no listo para carga.

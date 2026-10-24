# H045 - Gobernanza de pendientes e incorporacion a LimeSurvey

Actualizacion exclusiva 2027 P1, autorizada el 2026-10-13: [POLITICA_INCORPORACION_CORREO_2027_P1.md](./POLITICA_INCORPORACION_CORREO_2027_P1.md) extiende la conciliacion con pendientes de correo y de fecha, sin bloqueo global por correo individual. Los CSV contienen solo casos listos; diario + acumulado + correo pendiente + fecha pendiente (con correo valido) = elegibles sin token actual. Las identidades historicas siguientes se conservan para sus procesos originales; no usar su suma diario/acumulado para forzar la exportacion de correo ausente ni de matriculas del dia actual en 2027. FCU 2026 permanece congelado.

## Proposito

Evitar que la poblacion objetivo de la encuesta quede sin incorporacion a
LimeSurvey o que se incorporen personas que no deben ser encuestadas, por
mezclar tres conceptos distintos:

- matricula vigente del periodo;
- cohorte de ingreso institucional;
- fecha de matricula dentro de la ventana diaria.

Este documento gobierna las salidas:

- `+ Nuevos inscritos acumulados no incorporados a LimeSurvey_*.csv`;
- `+ Nuevos inscritos hoy_*.csv`;
- `AUDITORIA_REZAGADOS_LIMESURVEY_*.csv`.

## Incidente que origina el contrato

En la ejecucion 2026 P3 del 27 de agosto de 2026, el acumulado contenia 26
personas vigentes sin token, pero 12 tenian `ANOINGRESO` 2024 o 2025 y no
pertenecian a la poblacion objetivo. El CSV diario contenia 11. La diferencia
tambien incluia:

- 3 personas de ingreso 2026 cuya matricula llego a la fuente despues de que
  su `FECHAMATRICULA` ya habia quedado fuera de la ventana.

El acumulado se construia antes de aplicar la regla de cohorte, mientras el
diario si aplicaba `ANOINGRESO == ANIO_ANALISIS`. Esto mezclaba poblaciones:
las cohortes anteriores quedaban indebidamente en el acumulado aunque no
debieran ser encuestadas.

## Definiciones obligatorias

### Elegible operativo

Una fila es elegible para conciliacion operativa cuando pertenece al
`ANOMATRICULA` y `PERIODOMATRICULA` analizados, permanece en el universo
maestro despues de las exclusiones parametrizadas, tiene estado `VIGENTE` y
su situacion no corresponde a titulacion aprobada.

Cuando la exclusion por firma esta activa, tambien debe cumplir
`CON_FIRMA == SI`.

### Poblacion objetivo de la encuesta

Una persona elegible operativa pertenece a la encuesta solo cuando:

```text
ANOINGRESO == ANIO_ANALISIS
```

Para una ejecucion 2026 se encuesta exclusivamente `ANOINGRESO=2026`. El ano
objetivo cambia dinamicamente con `ANIO_ANALISIS` en futuras ejecuciones.

El periodo tambien es dinamico y queda gobernado por:

```text
ANOMATRICULA == ANIO_ANALISIS
PERIODOMATRICULA == PERIODO_ANALISIS
```

Por tanto, `PERIODO_ANALISIS` puede ser 1, 2 o 3 sin cambiar la regla de ano
de ingreso.

### Pendiente acumulado fuera de ventana

Es la parte de la poblacion objetivo sin token que no pertenece a la ventana
diaria cerrada de la ejecucion. El nombre historico del archivo se conserva,
pero ya no significa "todo el universo pendiente".

Formula contractual:

```text
POBLACION_OBJETIVO = VIGENTE_ELEGIBLE_PERIODO
                     AND ANOINGRESO == ANIO_ANALISIS

PENDIENTE_TOTAL = POBLACION_OBJETIVO - TOKEN_LIMESURVEY
PENDIENTE_ACUMULADO = PENDIENTE_TOTAL - PENDIENTE_DIARIO
```

El CSV acumulado contiene unicamente pendientes fuera de la ventana diaria.
Para una carga completa se deben considerar los dos CSV, cada uno una sola
vez. El CSV diario y el acumulado son salidas separadas y no se solapan.

### Pendiente de ventana diaria

Es un pendiente total cuya `FECHAMATRICULA` pertenece a la ventana habil
cerrada de la ejecucion.

Formula contractual:

```text
PENDIENTE_DIARIO = PENDIENTE_TOTAL
                   AND VENTANA_INICIO <= FECHAMATRICULA <= VENTANA_FIN
```

`ANOINGRESO` ya fue aplicado obligatoriamente para construir el acumulado. La
ventana diaria no puede reincorporar personas de anos distintos.

### Rezagado

Es un pendiente acumulado con `FECHAMATRICULA < VENTANA_INICIO`. Solo puede
contener personas cuyo `ANOINGRESO == ANIO_ANALISIS`.

### No objetivo por ano de ingreso

Los vigentes del periodo sin token cuyo `ANOINGRESO != ANIO_ANALISIS` no se
exportan en ninguno de los dos CSV. Se registran por separado en:

```text
AUDITORIA_NO_OBJETIVO_LIMESURVEY_ANOINGRESO_*.csv
```

Una fecha vacia, invalida o posterior a la ventana debe quedar visible en la
categoria de control `otros_fuera_ventana`; nunca debe descartarse en silencio.

## Invariantes bloqueantes

1. `diario` y `acumulado` deben ser mutuamente excluyentes.
2. `rezagados` debe ser subconjunto de `acumulado`.
3. `diario`, `rezagados` y `otros_fuera_ventana` deben ser mutuamente
   excluyentes.
4. La suma de diario, rezagados y otros fuera de ventana debe ser igual a
   `pendientes_total`.
5. La suma de diario y acumulado debe ser igual a `pendientes_total`.
6. Ningun CSV LimeSurvey puede contener token vacio o duplicado.
7. `ANOINGRESO == ANIO_ANALISIS` debe aplicarse antes de construir cualquiera
   de los dos CSV.
8. Todo rezagado debe producir alerta en terminal y evidencia en auditoria.
9. La ejecucion debe informar en terminal que diario y acumulado son salidas
   separadas, sin duplicacion.
10. Los vigentes sin token de otros anos de ingreso deben reconciliar y quedar
   en la auditoria de no objetivo.

Si falla una reconciliacion, el proceso debe terminar con error; no se permite
corregir el total ocultando filas.

## Separacion de responsabilidades

| Concepto | Campo gobernante | Uso permitido |
| --- | --- | --- |
| Periodo operativo | `ANOMATRICULA`, `PERIODOMATRICULA` | Seleccionar la matricula analizada |
| Elegibilidad | `ESTADOACADEMICO`, `SITUACION`, firma y exclusiones | Construir vigentes operativos |
| Cruce LimeSurvey | RUT canonico sin DV o llave seleccionada | Determinar con token/sin token |
| Poblacion objetivo | `ANOINGRESO == ANIO_ANALISIS` | Autorizar inclusion en la encuesta |
| Ventana diaria | `FECHAMATRICULA` | Vista temporal dentro de la poblacion objetivo |

## Implementacion gobernada

La politica temporal vive en:

```text
caracterizacion_limesurvey_policy.py
```

La funcion publica es:

```text
clasificar_pendiente_limesurvey()
```

Cada `manifest_ejecucion.json` debe registrar la politica `H045-v3`, declarar
`CSV_DIARIO_Y_CSV_ACUMULADO_SEPARADOS` e indicar que `ANOINGRESO` debe ser
igual al ano analizado.

La ventana se gobierna en `caracterizacion.py` mediante `ventana_habil_scl()`.
`VENTANA_FIN` es siempre el dia calendario anterior a la fecha de ejecucion;
el dia actual nunca entra en la ventana. `VENTANA_INICIO` retrocede hasta el
ultimo dia habil anterior cuando ayer fue fin de semana o feriado. El
calendario base vive en:

```text
docs/gobernanza/FERIADOS_CHILE_2026_2040.csv
```

El archivo es versionado, se carga localmente y admite actualizaciones por
feriados legales extraordinarios, elecciones u otros cambios normativos. No
se consulta internet durante una ejecucion. Antes de usar una fecha futura
que haya cambiado, se debe actualizar ese CSV y dejar la fuente en la columna
`fuente`.

La API recibe explicitamente `ano_ingreso` y `anio_objetivo`. Eliminar esa
validacion constituye un cambio de contrato y exige actualizar este documento,
los contratos invariantes y las pruebas de regresion.

## Pruebas obligatorias

Las pruebas deben cubrir como minimo:

- ingreso 2026 con fecha dentro de ventana;
- ingreso 2024/2025 excluido aunque su fecha este dentro de ventana;
- fecha anterior clasificada como rezagada;
- fecha invalida visible en control;
- fecha posterior visible en control;
- ventana invertida bloqueante;
- uso efectivo de la funcion de politica en el bloque productivo.

Comando focalizado:

```bash
python3 -m unittest \
  tests.test_caracterizacion_limesurvey_policy \
  tests.test_h042_csv_acumulado_limesurvey
```

## Regla de operacion diaria

Para incorporar estudiantes a LimeSurvey se deben revisar ambos CSV: el diario
para la ventana cerrada de ayer y el acumulado para pendientes anteriores o
fuera de ventana. No se debe cargar dos veces un token que aparezca en ambos;
la validacion bloqueante garantiza que eso no ocurra.

Dictamen contractual:

```text
ANOINGRESO_IGUAL_A_ANIO_ANALISIS=SI
CSV_DIARIO_Y_ACUMULADO_SEPARADOS_SIN_SOLAPAMIENTO=SI
REZAGADOS_VISIBLES_Y_RECONCILIADOS=SI
```

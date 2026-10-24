# H043 — Gobernanza y validación pospublicación del Bloque 13
## Propósito
Establecer una validación automática, trazable, dinámica y reutilizable
para las salidas del Bloque 13:
> Proveniencia y Trayectorias Formativas.
## Alcance
El control se aplica al archivo:
```text
INDICADORES_TRAYECTORIAS_FORMATIVAS_{AÑO}_P{PERIODO}_{FECHA}.xlsx

El validador no modifica el Excel, no ejecuta el pipeline y no altera
los procesos diarios.

Separación de procesos

La ejecución diaria de financiamiento se mantiene en:

./procesar_financiamiento_diario.sh

Ese proceso puede terminar después del Bloque 6.bis y no debe
interpretarse como una ejecución integral.

La validación del Bloque 13 se realiza después de una ejecución
integral ya terminada, utilizando:

./validar_bloque13_pospublicacion.sh

Principios de validación

1. No se fijan cifras variables de matrícula.
2. El universo se deriva de DETALLE_MATRICULA.
3. Cada llave CODCLI debe ser no vacía y única.
4. Cada registro debe clasificarse como TECNICO o PROFESIONAL.
5. La suma de ambos niveles debe coincidir con el universo.
6. Las hojas derivadas deben pertenecer al universo principal.
7. Las hojas derivadas no deben contener llaves duplicadas.
8. INGRESO_PROFESIONAL debe reconciliar con la clasificación
    profesional.
9. QA_COBERTURA debe existir y contener registros.
10. RESUMEN_KPI debe existir y contener registros.
11. Las auditorías operativas deben almacenarse en .local/.
12. Los archivos de auditoría operativa no deben publicarse en Git.

Hojas obligatorias

RESUMEN_KPI
DETALLE_MATRICULA
PROVENIENCIA_EMTP
PROVENIENCIA_CFT
INGRESO_PROFESIONAL
SALIDA_INTERMEDIA
TECNICO_A_PROFESIONAL
DIPLOMADOS
QA_COBERTURA
DEFINICIONES

Uso con un archivo explícito

./validar_bloque13_pospublicacion.sh \
  --archivo "/ruta/INDICADORES_TRAYECTORIAS_FORMATIVAS.xlsx"

Uso con una ejecución específica

./validar_bloque13_pospublicacion.sh \
  --run-dir "/ruta/2026_P2_HHMMSS"

Uso por año y período

./validar_bloque13_pospublicacion.sh \
  --anio 2026 \
  --periodo 3

Cuando no se entrega un archivo ni una ejecución específica, el
validador busca la salida más reciente que cumpla los filtros.

Validación adicional de Git

Para exigir que el repositorio esté limpio, sincronizado y sin
divergencia:

./validar_bloque13_pospublicacion.sh \
  --anio 2026 \
  --periodo 3 \
  --require-clean-git

Salidas de auditoría

Cada validación crea una carpeta independiente dentro de:

.local/auditorias/validacion_pospublicacion_b13/

Los artefactos incluyen:

01_METRICAS_B13.xlsx
02_DISTRIBUCION_NIVELES.xlsx
03_QA_COBERTURA.xlsx
04_RESUMEN_KPI.xlsx
05_MANIFEST.json
06_CIERRE.txt

Dictámenes

Validación aprobada:

DICTAMEN=B13_VALIDADO_POSPUBLICACION

Diferencias funcionales o estructurales:

DICTAMEN=B13_REQUIERE_REVISION

Error de ejecución:

DICTAMEN=B13_VALIDACION_NO_COMPLETADA

Regla crítica sobre universos

No deben compararse directamente métricas pertenecientes a universos
diferentes.

Por ejemplo:

estudiantes nuevos de una cohorte

y:

matrícula vigente institucional integral

son universos distintos.

Las cantidades institucionales se derivan dinámicamente del archivo
generado y no deben quedar fijadas permanentemente en el código.

Referencia pospublicación usada para H043

El cierre que originó esta gobernanza se validó sobre el commit:

d1c6038eab8b915a552a74b6128c3ed53bee30ce

El cierre institucional fue:

DICTAMEN=B13_VALIDADO_END_TO_END_POSPUBLICACION

Restricciones

PIPELINE_REEJECUTADO=NO
COMANDO_DIARIO_MODIFICADO=NO
DATOS_REALES_PUBLICADOS_EN_GIT=NO
AUDITORIAS_OPERATIVAS_EN_LOCAL=SI


---

## Decisión de gobernanza sobre la hoja DIPLOMADOS

La validación pospublicación distingue entre las hojas sustantivas derivadas
del universo de matrícula y la hoja de exclusión `DIPLOMADOS`.

### Hojas sometidas a control estricto

Las siguientes hojas deben constituir subconjuntos de
`DETALLE_MATRICULA`, usando la llave CODCLI normalizada:

- `PROVENIENCIA_EMTP`
- `PROVENIENCIA_CFT`
- `INGRESO_PROFESIONAL`
- `SALIDA_INTERMEDIA`
- `TECNICO_A_PROFESIONAL`

En estas hojas son bloqueantes:

- las llaves vacías;
- las llaves fuera de `DETALLE_MATRICULA`;
- las llaves duplicadas.

### Tratamiento especial de DIPLOMADOS

`DIPLOMADOS` representa un universo de exclusión y no un subconjunto
uno a uno de `DETALLE_MATRICULA`.

Por ello:

- las llaves vacías continúan siendo bloqueantes;
- las llaves fuera de `DETALLE_MATRICULA` se informan como advertencia;
- las llaves CODCLI repetidas se informan como advertencia;
- las métricas de cardinalidad se mantienen en el manifiesto de auditoría;
- no se eliminan ni consolidan registros automáticamente.

### Evidencia H043

La validación ejecutada sobre:

`INDICADORES_TRAYECTORIAS_FORMATIVAS_2026_P2_20260721.xlsx`

obtuvo:

- `DETALLE_MATRICULA`: 627 filas y 627 CODCLI únicos;
- `DIPLOMADOS`: 707 filas;
- CODCLI únicos en `DIPLOMADOS`: 454;
- CODCLI repetidos adicionales: 253;
- duplicados exactos: 0;
- grupos repetidos con atributos diferentes: 253.

El resultado demuestra que las repeticiones no corresponden a copias
idénticas y que su eliminación automática no está autorizada.

Dictamen funcional:

`B13_VALIDADO_POSPUBLICACION`

con dos advertencias documentadas para `DIPLOMADOS`.

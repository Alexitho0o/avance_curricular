# H044 — Fuentes congeladas y selección determinística para 2026 P2

## Problema detectado

La ejecución diaria de financiamiento (`./procesar_financiamiento_diario.sh
2026 2`) delegaba en `caracterizacion.py` la selección de matrícula, tokens
y resultados LimeSurvey. Cuando ninguna variable explícita estaba definida,
el pipeline auto-detectaba en `~/Downloads` el archivo más reciente por
fecha de modificación para cada prefijo (`DATOSDEALUMNOS_*`, `tokens_*`,
`results-survey*`).

Una ejecución seleccionó automáticamente `tokens_967488.csv` y
`results-survey967488.xlsx` por ser los más recientes en Downloads. Ese par
no correspondía a la encuesta vigente y produjo cero coincidencias reales
entre matrícula y tokens. El control de coherencia existente (rechazo de
parejas con cero coincidencias) detuvo el proceso correctamente, pero dejó
en evidencia que "archivo más reciente en Downloads" no es un criterio
seguro para una ejecución productiva de 2026 P2.

## Causa raíz

`caracterizacion.py` ya soportaba selección determinística mediante rutas
explícitas por variable de entorno (`RUTA_MATRICULA`, `RUTA_INSCRITOS`,
`RUTA_RESULTADOS`, resueltas por `env_matricula_file` y
`env_limesurvey_pair` en `caracterizacion_limesurvey.py`), con prioridad
total sobre Downloads. El lanzador productivo,
`procesar_financiamiento_diario.sh`, simplemente nunca las exportaba, por
lo que el pipeline caía siempre en la auto-detección.

## Solución aplicada

Se optó por la intervención mínima (no fue necesario modificar
`caracterizacion.py` ni `caracterizacion_limesurvey.py`, cuyo mecanismo de
rutas explícitas ya era correcto):

1. **Manifiesto gobernado** (ya congelado, no modificado por esta
   intervención):
   `docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json`

2. **Nuevo resolutor aislado e importable**:
   `scripts/gobernanza/resolver_fuentes_congeladas_2026_p2.py`

   Antes de cualquier procesamiento, para 2026 P2, este módulo:
   - Lee el manifiesto y verifica `anio=2026`, `periodo=2`,
     `estado=CONGELADO` y que declare los tres roles requeridos
     (`matricula_oficial`, `inscritos_limesurvey`,
     `resultados_limesurvey`).
   - Para cada archivo: construye la ruta desde la raíz del repositorio,
     confirma que quede dentro de `.local/fuentes_congeladas/` (sin
     enlaces simbólicos que escapen del repositorio), que exista, que sea
     un archivo regular, que su nombre coincida con el declarado y que su
     SHA-256 coincida exactamente con el manifiesto.
   - Verifica consistencia interna del `survey_id` entre el manifiesto y
     los archivos de tokens/resultados.
   - Si cualquier control falla: no exporta nada, no busca sustitutos en
     Downloads, y termina con código de salida distinto de cero
     identificando el archivo y el control que falló.
   - Si todo es correcto: imprime la traza `[H044][FUENTES]` y exporta
     `RUTA_MATRICULA`, `RUTA_INSCRITOS` y `RUTA_RESULTADOS` hacia el
     pipeline existente.

3. **Modificación quirúrgica del lanzador**
   (`procesar_financiamiento_diario.sh`): se agregó un bloque que se
   activa **exclusivamente** cuando `ANIO=2026` y `PERIODO=2`. Invoca el
   resolutor, vuelca su salida al log de la corrida, y:
   - si el resolutor falla, detiene el proceso antes de invocar
     `caracterizacion.py`;
   - si tiene éxito, exporta las tres variables y continúa con el pipeline
     sin cambios adicionales (o termina con `PREFLIGHT=OK` si se solicitó
     modo preflight).

   Para cualquier otro año o período, el bloque no se ejecuta y el
   comportamiento es idéntico al anterior.

## Precedencia de selección (gobernada)

1. **Ruta explícita ya presente en el entorno** (`RUTA_MATRICULA`,
   `RUTA_INSCRITOS` o `RUTA_RESULTADOS` establecida por quien invoca el
   lanzador, por ejemplo para una prueba puntual): prevalece **rol por
   rol** y el resolutor no la sobrescribe. Si esa ruta manual resulta
   inválida, el bloqueo ocurre en `caracterizacion.py` (comportamiento ya
   existente); tampoco en ese caso se cae a Downloads.
2. **Fuente congelada gobernada 2026 P2**: se usa para cualquier rol que
   no tenga una ruta explícita ya establecida.
3. **Selección automática histórica** (Downloads / `CARACTERIZACION_INPUT_DIR`):
   se mantiene sin cambios para cualquier año/período distinto de 2026 P2.
   Para 2026 P2, mientras el manifiesto exista, nunca se llega a este
   nivel.

## Manifiesto utilizado

- Ruta: `docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json`
- Versión: `2026_P2_20260721_161905`
- Ruta restringida de archivos crudos: `.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/`
  (excluida de Git; no se publican datos personales)

## Política de hashes

Los tres archivos se validan por SHA-256 en cada ejecución contra el valor
declarado en el manifiesto. Un archivo con el nombre correcto pero
contenido alterado (aunque sea un solo byte) bloquea la ejecución. La
verificación de `survey_id` es de **consistencia interna** (manifiesto vs.
archivo), no un valor codificado de forma fija en el código: esto permite
que una futura versión congelada, con un `survey_id` distinto, siga
funcionando sin cambios de código, ya que la identidad exacta del archivo
queda garantizada por el SHA-256, no por el número de encuesta en el
nombre.

## Comportamiento para P1 / P3 y otros años

Sin cambios. El bloque de fuentes congeladas solo se activa cuando
`ANIO=2026 AND PERIODO=2`. Para cualquier otra combinación, el lanzador
sigue invocando `caracterizacion.py` exactamente como antes, incluyendo la
auto-detección en Downloads cuando no hay rutas explícitas.

## Procedimiento para congelar una nueva versión

1. Ejecutar y validar una corrida reproducible con la nueva terna de
   archivos (matrícula/tokens/resultados).
2. Calcular el SHA-256 de cada archivo y copiarlos a una **nueva** carpeta
   versionada bajo `.local/fuentes_congeladas/2026/P2/<nueva_version>/`
   (no sobrescribir la versión existente).
3. Actualizar `docs/gobernanza/FUENTES_CONGELADAS_2026_P2.json` con la
   nueva `version_fuentes`, las nuevas rutas, nombres y hashes.
4. No es necesario modificar
   `scripts/gobernanza/resolver_fuentes_congeladas_2026_p2.py` ni
   `procesar_financiamiento_diario.sh`: ambos leen el manifiesto de forma
   dinámica.

## Procedimiento de reversión

Si se necesita volver al comportamiento anterior (auto-detección desde
Downloads también para 2026 P2):
- Revertir el commit que modifica `procesar_financiamiento_diario.sh`
  (o eliminar manualmente el bloque delimitado por el comentario
  `[H044][FUENTES]`), o
- Alternativamente, exportar manualmente `RUTA_MATRICULA`,
  `RUTA_INSCRITOS` y `RUTA_RESULTADOS` antes de invocar el lanzador: al
  prevalecer sobre el manifiesto, permiten anular puntualmente la fuente
  congelada sin revertir código.

`scripts/gobernanza/resolver_fuentes_congeladas_2026_p2.py` no se invoca
para ningún otro año/período, por lo que no requiere reversión para esos
casos.

## Modo preflight

Variable: `CARACTERIZACION_PREFLIGHT_FUENTES=1`.

Cuando está activa (y `ANIO=2026 PERIODO=2`), el lanzador resuelve y valida
la terna congelada, imprime la traza `[H044][FUENTES]` y el resumen
`MODO_FUENTES=... VERSION_FUENTES=... SURVEY_ID=... HASHES=OK
DOWNLOADS=NO PREFLIGHT=OK`, y termina **antes** de invocar
`caracterizacion.py`. No se genera ninguna salida productiva ni se cargan
los archivos Excel/CSV de contenido.

## Archivos modificados

- `procesar_financiamiento_diario.sh`

## Archivos creados

- `scripts/gobernanza/resolver_fuentes_congeladas_2026_p2.py`
- `tests/test_h044_fuentes_congeladas_p2.py`
- `docs/gobernanza/H044_FUENTES_P2_DETERMINISTICAS.md` (este documento)

## Pruebas ejecutadas

- `tests/test_h044_fuentes_congeladas_p2.py`: 16 pruebas (manifiesto válido;
  matrícula/tokens/resultados faltantes; hash alterado en cada uno de los
  tres archivos; año distinto; período distinto; manifiesto no congelado;
  `survey_id` inconsistente; guard de activación exclusivo 2026 P2 —
  cubre P1 y P3; override manual por variable de entorno prevalece por
  rol; archivos recientes en Downloads son ignorados; ruta fuera de la
  zona restringida; rol faltante en el manifiesto). Todas pasan.
- Regresión sobre pruebas relacionadas ya existentes:
  `tests/test_limesurvey_selection.py`,
  `tests/test_h042_csv_acumulado_limesurvey.py`,
  `tests/test_caracterizacion_runtime.py`. Todas pasan (53/53 en conjunto
  con la suite nueva).
- Validación estática: `bash -n` sobre el lanzador modificado,
  `python3 -m py_compile` sobre los archivos Python nuevos, `git diff
  --check`. Todo correcto.
- Preflight ejecutado con el lanzador real
  (`./procesar_financiamiento_diario.sh 2026 2`) sobre un directorio base
  sandboxeado (no institucional), confirmando `PREFLIGHT=OK` sin invocar
  el pipeline completo.

## Limitaciones conocidas

- No se ejecutó una corrida institucional completa end-to-end como parte
  de esta intervención (fuera de alcance; el preflight cubre la
  resolución de fuentes sin procesar datos).
- La garantía de que P1 y P3 no se ven afectados se validó de forma
  estructural (extracción y ejecución aislada de la condición de
  activación del lanzador) más inspección directa del código; no se
  ejecutó un run completo real de P1/P3 para evitar procesar datos
  institucionales sin necesidad.
- `DATOSDEALUMNOS_10246.xlsx` es la matrícula vigente para esta versión
  congelada únicamente. Una matrícula más reciente
  (`DATOSDEALUMNOS_10280.xlsx` u otra) requiere congelar una nueva versión
  completa y validada antes de reemplazar esta línea base; no debe
  mezclarse con los tokens/resultados de esta versión sin una nueva
  validación de coincidencias.

## H045 — Fuente auxiliar académica gobernada

Desde H045, la línea base reproducible 2026 P2 incorpora una cuarta
fuente RAW:

- Rol: `promedios_academicos_auxiliar`
- Archivo: `PROMEDIOSDEALUMNOS_7804.xlsx`
- Variable: `RUTA_PROMEDIOS`
- SHA-256:
  `83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca`

El archivo se almacena en `.local/fuentes_congeladas`, permanece excluido
de Git y se valida por nombre, ruta y SHA-256 antes de ejecutar el
pipeline.

Durante cada corrida, `caracterizacion.py` conserva una copia RAW sin
modificación dentro de `01_ENTRADAS`, registrada mediante la etiqueta
`promedios_auxiliar`. Por tanto, la fuente queda trazada tanto en la
línea base congelada como en el expediente particular de cada ejecución.

Para 2026 P2 no se permite seleccionar `PROMEDIOSDEALUMNOS_*` desde
`Downloads` cuando no existe un override explícito válido.

## Addendum 2026-10-01 — Nota operativa del Desktop sin gobernanza nueva

Se revisó `/Users/alexi/Desktop/EJECUTAR FCU PERIODO 2.docx` (instructivo
personal con 3 bloques de comandos: `procesar_financiamiento_diario.sh
2026 3`, `procesar_financiamiento_diario.sh 2026 2` y
`run_caracterizacion_fijo.sh 2026 2 1` con el resolutor de fuentes
congeladas). Su contenido completo son únicamente los comandos de
ejecución ya descritos y gobernados en este documento (H044) y en
`scripts/gobernanza/resolver_fuentes_congeladas_2026_p2.py`; no aporta
datos, resultados, decisiones ni evidencia nueva.

**Decisión (D — decisión interna):** no se crea un subproyecto de
gobernanza nuevo (`FCU/2026/periodo_2`) para este archivo. Se clasifica
como instructivo operativo personal, no como evidencia. El archivo
permanece sin cambios en el Desktop; esta nota documenta la revisión y la
decisión de no gobernarlo como paquete formal.

**Pendiente de confirmación por el usuario:** esta decisión es reversible;
si el usuario prefiere conservar el instructivo como documentación
formal, puede pedir que se incorpore como anexo de este mismo H044 (no
como paquete nuevo), dado que no añade contenido distinto al ya
documentado aquí.

# Control de cambios de VIG para Matrícula Unificada 2027

## Objetivo y decisión

**D — Alexi, instrucción en esta conversación registrada el 21-10-2026:**
conservar el estudio de los envíos 2026 y exigir manifiesto, responsable, fecha,
hora y alerta para cualquier cambio futuro de reglas. No rectificar los envíos,
las bases ni los denominadores históricos. MU2026 permanece congelado.

**B/C — Antecedente:** la auditoría de envíos verificó dos nóminas que cambiaron
737 personas de VIG 1 a 0 durante la preparación. De ellas, 734 aparecen en los
envíos efectivos (729 solo VIG 0 y cinco con algún VIG 1 posterior). La razón
académica individual permanece **E**. No se documentan como 737 errores.
El informe y sus hashes se preservan en `data/reglas_negocio/mu2027/estudio/`.

## Especificación previa a la implementación

**C:** registro común `data/reglas_negocio/mu2027/`, con versiones independientes
de `reglas.json`, manifiesto de aprobación y alerta por cada alta/cambio. El
descriptor `activo.json` apunta a una versión y al hash de su manifiesto. Una
versión nunca se sobrescribe mediante el controlador. Cada nueva versión enlaza
el manifiesto anterior y describe diferencias de reglas por pareja exacta.

**D:** responsable humano de la decisión, ejecutor técnico, motivo, evidencia
de autorización y fecha/hora con zona son obligatorios. El responsable se declara
explícitamente; el nombre de usuario del sistema no acredita aprobación humana.
Las fechas de registro no se presentan como fechas originales de las decisiones
conversacionales. La evidencia también queda congelada y comprobada por hash.

**C:** el consumidor consulta una versión explícita y su hash, valida toda la
cadena y rechaza modificaciones directas, versiones sin manifiesto, cambio de
contexto y parejas desconocidas. Cada rechazo deja una alerta local fechada.
Cada promoción genera además alerta aunque esté autorizada. No se envían correos.
La alerta se produce al consultar/verificar o registrar, no mediante vigilancia
continua del sistema de archivos.

**C:** la consulta devuelve VIG propuesto interno y clase D/E. `NO APLICA` y
`PENDIENTE` no se convierten a 0, 1 ni 2. El registro de una ejecución conserva
versión y hash de reglas, versión/hash del controlador, Git HEAD, entradas,
salidas, parámetros, responsable y fecha. Los parámetros no admiten personas:
solo período y fecha de referencia. Los datos sensibles siguen fuera de Git.

## Alcance de las equivalencias

**D:** se trasladan las 32 parejas del Excel simple aprobado: 23 VIG 0, cinco
VIG 1, tres NO APLICA y una PENDIENTE. Solo se aplican a la matrícula concreta,
con estado y situación del mismo período; no al historial completo de una persona.
La decisión NO APLICA para TITULADO no prueba una exclusión universal de retención
ni autoriza excluir otra matrícula activa de esa persona.

**E:** no se identificó un manual MU2027 en las fuentes locales revisadas.
El manual de Oferta 2027 no lo reemplaza. Por ello la aplicación disponible es
una revisión interna MU2027, no un exportador de carga SIES. `--carga-sies`
debe detenerse siempre en esta implementación. La futura habilitación exige
validar el manual MU2027, resolver contradicciones y registrar nueva versión
aprobada y pruebas. No copiar al motor congelado MU2026 ni alterar otros procesos.

## Límites y operación

**C:** `common/control_reglas_mu2027.py` implementa el registro y la consulta.
`core/mu2027.py` es su entrada operativa. No se ha localizado un motor de carga
MU2027 para conectar; los futuros consumidores deben utilizar esta entrada/API.
El control no impide que una persona con escritura modifique código y manifiestos
fuera del flujo. Git, revisión y publicación son necesarios para custodia remota.
Sin commit/push, estos cambios siguen siendo una implementación local preparada.

**C:** comandos disponibles: `verificar`, `consultar`, `registrar`, `ejecucion`.
Usar `python3 core/mu2027.py --help` y la ayuda del subcomando. Una modificación
requiere un archivo nuevo de reglas, autorización fechada y hash esperado de la
versión anterior; el comando registra el responsable y genera la alerta.

**E:** las cuatro bases T2/T3 fueron declaradas parciales por Alexi. El Excel
de revisión conserva como referencia el universo anual existente, 558 en 2024
y 1.150 en 2025, sin aprobar un denominador intermedio nuevo. Ausencia de un
listado parcial no es deserción. Los 222 y 124 ingresos T2/T3 2025 buscados en
MU2026 constituyen otro ejercicio y conservan sus denominadores.

## Checkpoint de entrega, 21-10-2026

**C/D:** versión interna `20261021_v1`, 32 parejas: 23 con VIG 0, cinco
con VIG 1, tres NO APLICA y una PENDIENTE. Diez pruebas aisladas del control
pasaron; manifiestos, autorización y alerta están preservados. La integridad
del registro se comprobó también mediante la entrada operativa.

**C:** el Excel retomado es
`outputs/retencion_intermedia_t2_t3/20261021_013430/REVISION_RETENCION_INTERMEDIA_IPSS_2024_2025_20261021.xlsx`,
con copia idéntica en el Escritorio. Reutiliza los resultados ya verificados:
resumen con selector de carrera, detalle agregado y fuentes/alcance. No recalcula
elegibilidad ni transforma VIG. Diecinueve selecciones de carrera, propagación de
fórmulas y lectura independiente del XLSX verificadas; cero errores de fórmula.
No se realizó apertura nativa en Excel. Su `MANIFEST.json` conserva hashes,
entradas, controles, scripts y pendientes. No contiene filas individuales.

**B/C/E:** para la cohorte 2024 se localizan 1 y 325 estudiantes en los listados
T2/T3 2025; 1 y 317 tienen etiqueta VIGENTE. Para la cohorte 2025 se localizan
2 y 0 en T2/T3 2026; T2 no informa estado. Los cuatro cierres siguen parciales:
no hay tasa intermedia válida ni clasificación de deserción por ausencia. El
seguimiento distinto de ingresos 2025 mantiene 74/222 y 48/124 en MU2026.

**C:** rama antes/después `feature/ire-2026`; HEAD antes/después
`b8140dcba0f179865671cff75f98b9e1041eeb0a`. No se ejecutó commit ni push.
Se conservaron los cambios de trabajo previos. El recurso genérico MU2026 del
proyecto permanece separado del nuevo recurso anual `reglas_vig_mu2027`.

**E:** faltan el manual MU2027 y el futuro consumidor de carga validado. El
control disponible aplica a su entrada de revisión, no a programas externos que
lo omitan. Falta también la matrícula completa y fechada de cada cierre T2/T3.
Estos pendientes no se presentan como cerrados por el OK de pruebas técnicas.

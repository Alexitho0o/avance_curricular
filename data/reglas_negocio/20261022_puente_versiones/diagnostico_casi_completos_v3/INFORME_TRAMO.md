# Tramo acotado: cinco dimensiones casi completas

2026-10-22 · PENDIENTE_APROBACION_GOBERNANZA

## Resultado y comparabilidad
No se demuestra nueva resolución: se conserva V3, sin crear V4. El indicador heterogéneo permanece 44/63 (69,84%): 39 propuestas estadísticas heredadas + 5 propuestas contextuales. No son 44 equivalencias verificadas/aprobadas. El indicador homogéneo es 8/63 (12,70%) con cobertura contextual observacional completa y n≥3: 3 previas (IECIRE/J1, IPRE/J4, NTCCRE/J2) y 5 nuevas, conjuntos disjuntos. La misma prueba contextual se aplicó a las 63 dimensiones; las 39 heredadas no se certifican por conservar su etiqueta anterior.

## Fases
1. Inventario: búsqueda acotada Enviados/Publicados SIES por matrícula 2019/2020 encontró únicamente MAT_IP_CIISA_2019.xlsx y MAT_IP_CIISA_2020.xlsx ya utilizados. No se afirma inexistencia universal de otros respaldos.
2. Pruebas: cruce exacto local, presencia en otros años, variante de DV, contexto de asignaturas y respaldo DATOSDEALUMNOS_11248. No se exportaron personas.
3. Reconciliación: siete observaciones faltantes; las siete tienen expediente concordante en 11248. Ese extracto no aporta código SIES anual, por lo que no resuelve ninguna. No hubo match por mismo cuerpo y otro DV en el año faltante. QA independiente V3 se conserva; no se atribuye una segunda implementación nueva a este tramo.
4. Entrega: diagnóstico agregado y script reproducible; V3 y sus copias intactos. No cambios productivos, commit, push ni uploads.

## Faltantes precisos
|Dimensión|Plan|Año / periodo PROMEDIOS|Observaciones sin matrícula anual|
|---|---|---|---:|
|NCONRE/J2|NCONRE|2020 / 2|2|
|NICCRE/J2|NICCRE20191|2020 / 2|1|
|NINFRE/J2|NINFRE|2020 / 2|1|
|TPCRE/J1|TPCRE20191|2020 / 2|1|
|TPCRE/J2|TPCRE20191|2019 / 2|1|
|TPCRE/J2|TPCRE20191|2020 / 2|1|

Para estos casos falta una carga o rectificación MAT_2020 (y MAT_2019 para TPCRE/J2) con MM_N_DOCUMENTO, MM_DV, MC_CAT_PERIODO y MC_CODIGO_UNICO concordantes. Las rutas verificadas y hashes constan en FUENTES.json. El periodo 2 es el de PROMEDIOS, no una supuesta segunda carga MU.

NINFRE/J2 además presenta dos observaciones de 2019, periodos 1 y 2, sin contexto concordante en DA12159; el resultado de contraste con 11248 está en DIAGNOSTICO.json. Es un obstáculo distinto del único registro anual 2020 faltante.

TPCRE/J1 tiene dos filas de asignatura marcadas CONVALIDADO=S en la observación faltante. TPCRE/J2 tiene tres filas con S y una sin marca, distribuidas en sus dos observaciones faltantes. La convalidación puede explicar notas sin actividad contemporánea, pero no prueba ausencia de matrícula ni autoriza retirar observaciones. ESTADO_ACADEMICO es el estado del extracto; no certifica el estado histórico en 2019/2020. No se imputan ceros ni deserción.

## Auditoría de las cinco propuestas V3 frente a condiciones originales
Las cuatro dimensiones NAUTRE/J2, NECIRE/J2, NICCREOL/J4 y NINFREOL/J4 muestran una sola versión en las observaciones históricas cotejadas y al menos tres personas. Es evidencia nueva frente al catálogo/corte previo, pero no acredita por sí sola vigencia del plan individual ni igualdad del total MU por dimensión: la prueba V3 comprueba cobertura del subconjunto PROMEDIOS, no conciliación exhaustiva del universo MU con ese plan.

TCRE/J2 distribuye personas-código 8 y 2: predominancia 80%, inferior a 90%. Por tanto, NO pasa la regla original de versión única predominante. Solo puede figurar como propuesta metodológica contextual uno-a-varios, pendiente de decisión explícita. La autorización para investigar no aprueba este cambio de regla.

Para las cinco, la asignación exacta por persona/año reemplaza la predominancia fija por cobertura contextual completa; esa diferencia metodológica se declara, no se adopta productivamente. El grano persona-código de esta revisión tampoco equivale al grano original persona-plan-código. La reducción V3 24→19 mezcla evidencia histórica nueva y ampliación metodológica; no debe comunicarse como cinco aprobaciones bajo las condiciones originales. Con todos los controles originales acreditados, este tramo no certifica ninguna nueva equivalencia.

Las fuentes y tasas históricas siguen intactas. El siguiente paso útil es recuperar la carga/rectificación anual indicada o documentación de asignación efectiva plan-expediente-periodo; copiar códigos de años adyacentes o eliminar convalidaciones no cumple la prueba.

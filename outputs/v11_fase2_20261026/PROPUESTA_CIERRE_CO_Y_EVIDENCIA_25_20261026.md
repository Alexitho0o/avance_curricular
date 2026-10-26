# Evaluación de cierre interno V1 · Concepción y 25 diferencias

## 73 contextos CO

- **B/C:** en los 73 contextos, la MU 2026 granular registra por persona un único código T1, con VIG=1; PROMEDIOS registra en T1 el mismo CODCLI, plan, carrera y jornada que en el contexto destino. DATOSDEALUMNOS 10246 y 11998 muestran el mismo RUT/CODCLI con CO, carrera y jornada concordantes. Los 73 contextos corresponden a 51 personas y 51 expedientes, no a 73 personas.
- **B:** la oferta pública 2026, hoja `in`, registra una sola versión para cada familia: `I162S3C114J2V1` fila 26534; `I162S3C115J2V1` fila 26535; `I162S3C91J2V1` fila 26536. Las tres filas describen plan regular, duración total cinco semestres y vigencia con nuevos. Se verificó la etiqueta exacta de año `OFE_2026`.
- **D:** el usuario aprobó las tres familias CO, no la adjudicación individual de V1 para T2/T3. La herencia T1 estricta vigente es control de consistencia, no regla de asignación.
- **E/C · Propuesta revisable:** los 73 son candidatos fuertes para una decisión de correspondencia interna V1 limitada a estas observaciones concretas y sujetos a QA previo y posterior. Esto requeriría aprobar un nuevo criterio de atribución y registrar responsables/alcance; el código anual identificado por RUT no contiene CODCLI, y los respaldos no acreditan fecha exacta del corte o una aceptación SIES por contexto trimestral. La propuesta no declara vigente ni retenido a nadie y no cambia el denominador. No se ha aplicado.

## 25 diferencias de familia

- **B/C:** 19 presentan diferencia de jornada y seis de carrera frente a la familia T1; son 25 contextos, 16 personas. En 13 contextos de 2025 la familia destino aparece para la persona en MU 2026.
- **B/C:** para esos 13, MU 2026 tiene un único código total por persona, `ANIO_ING_ACT` no posterior a 2025; el mismo CODCLI aparece en los dos respaldos 2026; en PROMEDIOS se observó un solo plan dentro de las fuentes/años revisados y el código aparece en el índice de oferta 2025. No equivale a prueba directa del código por CODCLI en 2025 ni prueba que el plan sea único en archivos no revisados.
- **E:** auditar cada uno de esos 13 contra todas las condiciones y alcance de la decisión D de v10 —incluyendo atribución efectiva de CODCLI y fecha/alcance del cambio— antes de proponer su reutilización. No extender de forma automática las 27 adjudicaciones personales previas.
- **B/E:** en cinco contextos 2026 de tres expedientes, la jornada destino no coincide con respaldo 10246 pero sí con 11998. Se necesitan fecha efectiva del cambio y un respaldo específico del periodo afectado; una foto posterior no demuestra que el cambio ocurriera antes de T2.
- **E:** los siete contextos restantes requieren acreditar por expediente el cambio de carrera o jornada, su fecha o periodo efectivo y la relación plan/código. Los ocho sin T1 completa se solapan: seis corresponden a diferencias de carrera y dos conservan familia; no sumarlos como casos adicionales.

## Fuentes y QA

- **B/C:** MU granular `BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`, hoja `BASE_RETENCION_MU`, SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
- **B/C:** `Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx`, hoja `in`, SHA-256 `94d51a6752b40adb45c8eba65786ee8aad9f6667d15b3d07273a969ec4faed77`.
- **C:** `EVALUACION_CIERRE_CO_V1_AGREGADO_V2.json` SHA-256 `d73e0bdd88f64ecb4f56e2ff59b6b57cefcd21eaa6a43edace11282f90abe66f`; `EVALUACION_TRECE_MU2026_AGREGADO.json` SHA-256 `209c0664ecd8db71887e431753046ed23790056674fe31ba1f0fbf44148412d1`. Detalles individuales fuera de Git en `~/.local/share/ipss/v11_fase2_20261026/`.
- **C:** primera extracción de oferta se invalidó porque buscaba `2026` en vez de `OFE_2026`; usar solo V2. No se cambian bases, reglas, denominadores ni puntero activo; no se hizo push.

# H010 · candidata v21 por primer T1 informado

Estado: CANDIDATA_NO_ACTIVA_CON_RESIDUALES_E. D Alexi, 30-10-2026.
No se abrió Excel; V25/V26/entregables intactos. No hay commit ni push de avance_curricular.
La meta ≤0,1 % no se alcanza. No se fuerza ninguna versión ni se abre otra iteración.

## Respuesta directa (B/C)

| Año contexto | 2023 | 2024 | 2025 | Total |
| --- | --- | --- | --- | --- |
| 2020 | 4 | 0 | 0 | 4 |
| 2021 | 11 | 0 | 0 | 11 |
| 2022 | 46 | 3 | 0 | 49 |

Unidad: contextos nativos sin T1 atribuido del mismo expediente/plan en su año,
no estudiantes únicos ni ingresos nuevos acreditados. Carrera con mayor cantidad
observada (no umbral estadístico): IETMREOL: 15, IECIRE: 13, IECSRE: 13, IECSREOL: 9, TPAREOL: 6, TCSREOL: 3, IECIREOL: 2, TTMREOL: 2.
Detalle de año/período/carrera: PASO1_POR_CARRERA.md y PRIMER_T1_POSTERIOR.json.
Se distinguen persona sin MU y persona con MU sin ancla del expediente; no son
universos equivalentes. Las 2.966 de v7 incluyen períodos 1, 4 y 5: distribución
{"1": 402, "2": 871, "3": 1108, "4": 305, "5": 280}. No se convierten en T2/T3.

## Paso 1 · desfase (B/C; ausencia E)

| Año | Período | X+1 | X+2 | X+3_O_MAS | SIN_T1_POSTERIOR_LOCALIZADO | Total |
| --- | --- | --- | --- | --- | --- | --- |
| 2019 | 2 | 100 | 15 | 3 | 59 | 177 |
| 2019 | 3 | 39 | 5 | 0 | 46 | 90 |
| 2020 | 2 | 137 | 11 | 4 | 55 | 207 |
| 2020 | 3 | 74 | 15 | 0 | 61 | 150 |
| 2021 | 2 | 53 | 11 | 0 | 67 | 131 |
| 2021 | 3 | 42 | 0 | 0 | 21 | 63 |
| 2022 | 2 | 14 | 1 | 0 | 4 | 19 |
| 2022 | 3 | 32 | 2 | 0 | 24 | 58 |
| 2023 | 2 | 1 | 1 | 1 | 8 | 11 |
| 2023 | 3 | 24 | 1 | 1 | 102 | 128 |
| 2024 | 2 | 60 | 28 | 0 | 66 | 154 |
| 2024 | 3 | 92 | 28 | 0 | 68 | 188 |
| 2025 | 2 | 127 | 0 | 0 | 157 | 284 |
| 2025 | 3 | 173 | 0 | 0 | 102 | 275 |

Nunca informado sólo significa sin evidencia localizada hasta 2026. No se afirma
que una persona no existió en SIES ni que un contexto implicó matrícula. La
cobertura de los extractos históricos y el futuro están limitados.

## Cobertura separada por nivel (B/C/D/E)

| Universo | Total | CAMBIO_PLAN_ANTES_DE_T1_CATALOGO | DOCUMENTAL_T1 | E | HERENCIA_T1_MISMO_AÑO | MU2027 | NUNCA_INFORMADO_EN_FUENTES | PRIMER_T1_POSTERIOR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V24_99_posiciones | 99 | 2 | 0 | 38 | 0 | 8 | 4 | 47 |
| v20_completa | 27196 | 39 | 7910 | 6561 | 11811 | 26 | 248 | 601 |
| v7_3049 | 3049 | 38 | 7 | 2194 | 14 | 19 | 248 | 529 |

La candidata es una base privada con tablas v20 intactas y una tabla adicional
asignaciones_h010. El código candidato no reemplaza el código documental ni el
interno aprobado. El descriptor NO es un activo del consumidor actual: requiere
aprobación e integración posterior. Los cambios de plan con catálogo se muestran
en nivel propio, sin atribuirles evidencia documental del contexto original.
Las opciones MU2027 son simulaciones del consumidor activo, no T1 futuros observados.

## Estabilidad (B/C)

| Año | Siguiente | MANTIENE | CAMBIA | MULTIPLE_E | Total | % mismo código sobre únicos |
| --- | --- | --- | --- | --- | --- | --- |
| 2019 | 2020 | 114 | 2 | 0 | 116 | 98.276 |
| 2020 | 2021 | 157 | 0 | 0 | 157 | 100.0 |
| 2021 | 2022 | 210 | 216 | 0 | 426 | 49.296 |
| 2022 | 2023 | 513 | 9 | 0 | 522 | 98.276 |
| 2023 | 2024 | 317 | 1 | 0 | 318 | 99.686 |
| 2024 | 2025 | 639 | 64 | 0 | 703 | 90.896 |
| 2025 | 2026 | 951 | 105 | 0 | 1056 | 90.057 |

Anclas: T1 de v20 + línea MU, o enlace MU–expediente–plan ANUAL congelado H002g.
No se exige actividad PROMEDIOS en período 1. Plan anual observado no acredita
fecha exacta de cambio dentro del año. No se reconstruye identidad RUT–MRUN.

Transición pública reutilizada: 46 códigos en 2021,
26 en 2022; 14 con última
matrícula en 2021, controlado hasta 2026 con R25. Hasta 2025 eran 16: dos códigos
reaparecen en 2026. Fuente: TRANSICION_2021_2022.json.

| causa | n |
| --- | --- |
| SIN_PRUEBA_TRANSICION_T1_PERSONAL | 261 |
| TRANSICION_MISMO_EXPEDIENTE_T1_2021_2022 | 164 |

Se reproducen los 425 errores de la prueba antigua T_plan, sin tratarlos como
fallos de H010. La transición personal apoya compatibilidad con recodificación;
no acredita una causa institucional única. Los demás carecen de esa prueba.
Detalle por código en ERRORES_425_REENCUADRADOS.json.

## Residual y límites (E)

| nivel_asignacion | motivo | n |
| --- | --- | --- |
| CAMBIO_PLAN_ANTES_DE_T1_CATALOGO | CODIGO_GRUPO_ANUAL_PLAN_ORIGINAL_NO_DOCUMENTAL | 38 |
| DOCUMENTAL_T1 | EVIDENCIA_T1_MISMO_EXPEDIENTE_PLAN | 7 |
| E | CAMBIO_PLAN_SIN_CODIGO_ANUAL_UNICO_COMPATIBLE | 75 |
| E | CAMBIO_SEDE_JORNADA_ANTES_T1 | 12 |
| E | MU2027_SIN_FILA_ANTIGUO_INEQUIVOCA_NO_COHORTE_NUEVA_2027 | 767 |
| E | PERIODO_NATIVO_4_5_NO_HOMOLOGADO | 604 |
| E | PERSONA_EN_MU_SIN_T1_MISMO_EXPEDIENTE_PLAN_ACREDITADO | 121 |
| E | SIN_MU_LOCALIZADA_Y_SIN_CATALOGO_ANUAL_UNICO | 93 |
| E | T1_SIN_LINEA_ATRIBUIDA_AL_EXPEDIENTE | 424 |
| E | TIPO_DURACION_PLAN_E | 98 |
| HERENCIA_T1_MISMO_AÑO | EVIDENCIA_T1_MISMO_EXPEDIENTE_PLAN | 14 |
| MU2027 | SIMULACION_ANTIGUO_NO_T1_2027_OBSERVADO | 19 |
| NUNCA_INFORMADO_EN_FUENTES | AUSENCIA_OBSERVADA_2019_2026_NO_INEXISTENCIA_SIES | 248 |
| PRIMER_T1_POSTERIOR | EVIDENCIA_T1_MISMO_EXPEDIENTE_PLAN | 529 |

Cada combinación año/período/plan/sede/jornada tiene causa y requisito en
RESIDUAL_E.json y REQUISITOS_E.json. Los 99 se detallan sólo en agregado en CASOS_99_AGREGADOS.json.
Sin perfil tipo/duración compatible no se asigna el nivel 3. Los períodos 4/5 no
se homologan. Un ingreso 2026 sin fila MU no se simula como cohorte nueva 2027.

## Controles y gobernanza

QA.json: niveles 1–3 con evidencia anual T1; tipo/duración de nivel 3 compatibles;
3.049 y 99 conciliados; fuentes, tablas v20 y puntero intactos. Las tasas R01–R04
y R19 conservan 0,00 pp por no alteración de indicadores, no por un recálculo
ni por prueba de nuevos desgloses. Meta residual E explícita. Pruebas y
reproducción: QA_CIERRE.json. Identificadores exclusivamente privados.

Regla D registrada en IPSS_IA_SKILLS_Y_REGLAS 1.3.12, commit `a414dc81f1eec0e0952b29b6c82d5cd5b3569d1b`;
validador sin errores, con pendientes históricos E. No activa v21 ni cambia skills.

Mensaje preparado: `H010 propone código de contexto por primer T1 acreditado y reencuadra evidencia metodológica`.
Lista exacta: LISTA_PUBLICACION.json. No ejecutar commit/push sin autorización.

## H010b · cierre con D1–D3 (30-10-2026)

Lo anterior documenta la línea base H010. Esta sección es el resultado actualizado;
no reinterpreta sus asignaciones previas. **D:** decisiones de Alexi; **B/C:**
evidencia y aplicación; **E:** requisitos pendientes. v21 sigue CANDIDATA, v20 activo.

| Nivel | 3049 antes | 3049 despues | 99 antes | 99 despues |
|---|---|---|---|---|
| CAMBIO_PLAN_ANTES_DE_T1_CATALOGO | 38 | 38 | 2 | 2 |
| CAMBIO_PLAN_SEDE_CATALOGO_D3 | 0 | 19 | 0 | 7 |
| DOCUMENTAL_T1 | 7 | 7 | 0 | 0 |
| E | 2194 | 964 | 38 | 0 |
| HERENCIA_T1_MISMO_AÑO | 14 | 14 | 0 | 0 |
| INGRESO_2026_NO_INFORMADO | 0 | 840 | 0 | 21 |
| MU2027 | 19 | 19 | 8 | 8 |
| NUNCA_INFORMADO | 0 | 197 | 0 | 10 |
| NUNCA_INFORMADO_EN_FUENTES | 248 | 248 | 4 | 4 |
| PRIMER_T1_POSTERIOR | 529 | 703 | 47 | 47 |

Se agregan 1230 asignaciones a las 3.049 observaciones históricas.
Entre las 99 posiciones se agregan 38; E pasa de 38 a 0.
En todo v20 se agregan 1416 asignaciones candidatas.
Los universos no se suman: las 99 son posiciones de seguimiento, no observaciones únicas.
No cambia el numerador ni denominador de H001/R19: **0,00 pp por conservación**.

### Residual E histórico final

| motivo | n |
|---|---|
| AMBIGUEDAD_ANUAL_PERSISTENTE | 1 |
| PERIODO_NATIVO_4_5_NO_HOMOLOGADO | 604 |
| PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS | 6 |
| SIN_CODIGO_ANUAL_COMPATIBLE | 2 |
| SIN_T1_POSTERIOR_CON_ANTECEDENTE_PREVIO | 48 |
| SIN_VIGENCIA_1_COMPATIBLE | 28 |
| TIPO_DURACION_PLAN_E | 273 |
| VARIAS_VIGENCIA_1_COMPATIBLES | 2 |

Fuente: `RESIDUAL_H010B.json`, con requisito exacto y conteos por año, período,
plan, sede y jornada. Los 604 de períodos 4/5 se separan de los 360 restantes.
Los 48 con T1 previo, sin posterior, no pueden rotularse NUNCA_INFORMADO:
requieren decisión explícita sobre ese arrastre anterior. No se extiende D1 por analogía.
Los 273 sin tipo/duración necesitan perfil gobernado; 28 carecen de VIGENCIA 1
compatible; 2 tienen varias; 1 mantiene ambigüedad anual; 2 no tienen código
compatible y 6 no tienen primer T1 inequívoco con las mismas dimensiones.

### Controles y alcance de D1–D3

`resolver_h010b.py` lee la salida privada congelada de H010. Sólo revisa E en
motivos que encajan en D1–D3; todas las asignaciones anteriores se conservan.
D2 también cubre residuales 2026 que antes tenían motivo T1 sin línea: por eso
su nivel final no se limita a los 767 del motivo original. Los cruces por motivo
anterior/nuevo quedan en `TRANSICIONES_H010B.json`.

Cada alta tiene perfil v2 compatible, código en oferta del año, sede y jornada
coherentes. D2 exige VIGENCIA 1 de 2026, no de 2027. D3 usa tipo/duración antes
de VIGENCIA 1. H002 aporta la familia del plan; no se elige por nombre. Un T1
posterior también se contrasta con la oferta del año del contexto. Todo queda
separado de DOCUMENTAL_T1 y de la regla MU2027. NUNCA_INFORMADO se limita al
mismo expediente/plan y fuentes disponibles; no afirma inexistencia en SIES.

### Períodos 4/5: investigación terminada, homologación no aplicada

Fuente: `PERIODOS45_H010B.json/.md`. De 604 contextos: 598 BIMESTRAL, 3 SEMESTRAL,
3 TRIMESTRAL (campo original REGIMEN; se informa como REGIMEN_FUENTE).
Hay 377 personas distintas; 185
aparecen también en 1/2/3 del mismo año. Carreras, planes, años y coexistencia
están desglosados en el JSON, sin identificadores.

PROMEDIOS no contiene inicio/término de período. La FECHAMATRICULA de Datos
Alumnos no los reemplaza. El calendario trimestral 2026 catalogado define
T1/T2/T3 (páginas 2, 5, 7, 8 y 9), pero no define 4/5 ni años históricos.
**E:** falta calendario/definición UMAS por año y régimen; no se acredita verano.

Propuesta: conservar los períodos nativos; sólo con definición del mismo año,
someter a Alexi herencia de su T1 o primer T1 posterior, con tipo/duración y
oferta anual. Escenario condicionado a actividad del mismo año, **C/E no aplicado**:
| nivel_asignacion | n |
|---|---|
| E | 600 |
| NUNCA_INFORMADO | 2 |
| PRIMER_T1_POSTERIOR | 2 |
La simulación prueba T1 del mismo expediente/plan/año y, si falta, D1–D3.
No acredita fechas ni transforma períodos. Ninguno de los 604 se asigna en H010b.

### QA y reproducción

`QA_H010B.json` integra pruebas, reproducción de hashes, preservación de v20,
R01–R04/R19, V25/V26, mapa R01–R28 y los 25 cambios ajenos. No se abrió Excel.
El detalle sólo reside en la carpeta privada; la base candidata es un derivado
nuevo que conserva tablas v20 y añade las asignaciones en una tabla separada.
`MANIFEST.json` y `LISTA_PUBLICACION.json` sustituyen sólo el cierre de publicación;
se conservan los manifiestos/lista/descriptor H010 anteriores.

Regla D1–D3: IPSS_IA_SKILLS_Y_REGLAS **1.3.13**, commit `2f6a967`.
Publicación de H010/H010b autorizada en este prompt, condicionada a QA y privacidad.
Mensaje: `H010 asigna código de contexto por primer T1 informado; H010b aplica D1–D3 y documenta períodos 4/5`.

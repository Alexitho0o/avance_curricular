# Seguimiento por RUT, código SIES y períodos: revisión del 23-10-2026

## Encargo y resultado

D: Alexi solicita comprobar si un seguimiento por RUT en PROMEDIOS, sin buscar
código SIES, cambia el Excel V13; autoriza evitar otro archivo si el ejercicio
ya existe. También solicita verificar las equivalencias de períodos y niveles.

B/C: no se generó un Excel duplicado. V13 ya sigue a las personas sin exigir
coincidencia de código SIES de destino. El código T1 se usa para clasificar el
resultado por su carrera de origen; el diccionario del contexto se presenta en
otro bloque. Sus pendientes no descuentan estudiantes del numerador ni del
denominador. Quitar una condición SIES que no existe no cambia el cálculo.
Esto verifica separación de implementación, no demuestra por sí solo que todas
las equivalencias de carrera o todas las tasas históricas sean correctas.

## Llaves y fuentes del resultado existente

| Cohorte → observación | Resultado conservado | Cruce y condición efectivos | Clase |
|---|---|---|---|
| 2024 → 2025-2 | 160/558 | Cuerpo RUT + ANO/PERIODO en PROMEDIOS; al menos una fila con ESTADO_ACADEMICO=VIGENTE | B/C; E como acreditación del cierre |
| 2024 → 2025-3 | 175/558 | Igual criterio; período3 | B/C; E como acreditación del cierre |
| 2025 → 2025-2 | 600/1.150 | Total heredado hoja26 E1852; reproducción R+P encuentra611. Linaje individual del600 pendiente | B/C/E |
| 2025 → 2025-3 | 1.023/1.150 | Foto T3; cuerpo documental + año de ingreso de matrícula, prioridad estado/situación y Q/R de hoja20 | B/C |
| 2026 → 2026-2 | 1.042/1.471 | Cuerpo RUT + ANO/PERIODO en PROMEDIOS; al menos una fila VIGENTE | B/C; E como acreditación del cierre |
| 2026 → 2026-3 | 1.360/1.467 | Foto T3; mismo criterio de Q/R. Población original1471, cuatro NO APLICA fuera de la tasa por regla heredada | B/C |

C: el proxy no filtra por código SIES, CODCLI, plan o carrera de destino. Puede
detectar actividad de la misma persona en otro expediente. Por ello no debe
presentarse automáticamente como continuidad en la misma carrera ni como avance
del plan original. La ausencia de código no es ausencia de actividad.

C: sustituir las fotos T3 por PROMEDIOS sería otro escenario de fuente y
condición, no un experimento de retirar SIES. El estado académico del extracto
no acredita por sí solo el estado en una fecha de cierre. La existencia de
asignaturas, la nota promedio, la matrícula vigente y el avance aprobado son
medidas distintas. No se adoptó un reemplazo de fuente ni una nueva tasa.

B/C: referencias de implementación y evidencia:

- `scripts/v13_20261023_reconstruir_proxy_t1.py`, líneas21–39: llave corporal,
  conjuntos de personas, ANO/PERIODO y estado; sin filtro SIES.
- `scripts/v13_20261023_seguimiento_t1_agregado.py`, líneas41–51: agrupación
  posterior por código T1 y cálculo heredado desde Q/R.
- `scripts/preparar_seguimiento_t1_v13_20261023.py`, líneas22–36: contexto
  de diccionario separado de los numeradores.
- `scripts/construir_seguimiento_t1_v13_20261023.mjs`, líneas36–48: resumen,
  referencia18!E8 y tasas; bloque de códigos separado.
- Libro AUDITADO_ENTREGA, hoja20: I normaliza cuerpo; O=I*100000+N*10,
  donde N es año de ingreso; P busca prioridad en24/25; Q indica VIG1;
  R excluye NO APLICA/PENDIENTE/Sin foto. Hoja18 G8/G11 cuenta Q por año/grupo1;
  H8/H11 divide por R. Las fórmulas no usan código SIES.
- V13: `outputs/seguimiento_t1_hasta_2026_20261023_v13/`, con fuentes, hashes,
  controles y la discrepancia600/611 ya registrados. No se reejecutó un cruce
  masivo ni se afirma un nuevo recálculo de sus resultados en esta revisión.

## Qué establece el manual y qué implementa el proyecto

A: Instructivo Avance Curricular SIES2026, datos2025, páginas2 y4–5, solicita
presencia académica en primer/segundo semestre y unidades cursadas/aprobadas del
año y acumuladas. Avance curricular vincula unidades aprobadas con el total del
plan. Debe conservarse la misma unidad de medida en carrera y estudiante. Las
unidades de otra carrera no se atribuyen automáticamente a la carrera informada.
El tratamiento anual y acumulado de convalidaciones es distinto (página5).

A: páginas12–13 definen CURSO_1ER_SEM y CURSO_2DO_SEM. El instructivo no establece
una regla universal de conversión de tres períodos internos ni declara que
NIVEL sea un porcentaje de avance aprobado.

| Campo o uso | Regla localizada | Alcance / autoridad |
|---|---|---|
| PERIODOINGRESO → SEM_ING_ACT | 1→1; 2→2; 3→2 | C/D: configuración institucional MU2026, no fórmula oficial de todos los procesos |
| PERIODO histórico → semestre | 1→1; 2 y3→2 | C: función `_normalize_period_to_semester`, código616–622; no condiciona por régimen |
| Nivel administrativo trimestral → NIV_ACA | 1→1,2→2,3→2,4→3,5→4,6→4,7→5,8→6,9→6,10→7,11→8,12→8; superiores ceil(2n/3) | C: función625–642; aplicación4127–4155 solo si REGIMEN_FUENTE contiene TRIM |
| Nivel estudiante versus nivel asignatura | Prioridad DA_NIVEL sobre Hoja1.NIVEL | C: código2917; el segundo describe nivel del ramo en la malla, no logro de la persona |
| Presencia en otro consumidor de Avance | PERIODO==1 → CURSO_1ER_SEM; PERIODO==2 → CURSO_2DO_SEM | C/E: código2093–2094 no incorpora3 explícitamente; identificar ejecución y entradas antes de evaluar envío |

C/E: no corresponde convertir directamente «1+2→primer semestre;3→segundo»:
no es la implementación encontrada. Tampoco corresponde transportar la
normalización de SEM_ING_ACT al calendario de cada asignatura o a los cierres
T2/T3. La conversión administrativa de NIV_ACA tiene además normalizaciones y
topes de duración/cohorte en4123–4155; no se sustituye por una medida de avance.

B/C: `data/gobernanza_niveles.tsv` es un marcador textual; no acredita una tabla
de conversión. La tabla raíz `gobernanza_niveles.tsv` clasifica nivel global y
tipo de carrera, no períodos ni progreso académico.

## Comprobación GitHub y límites

B/C: consulta de solo lectura al remoto origin de avance_curricular, rama
feature/ire-2026, devuelve `843873f5ddeff6916032e8ed821776db2a632cfd`.
El objeto local de ese commit contiene exactamente los mismos bytes de
`codigo_gobernanza_v2.py` y `control/config_campos_ing.json` que los archivos
inspeccionados. La regla de niveles consta en el commit
`e6a24f86ef5dcda04cbf92db261b0d091f3e5a89` del09-abr-2026, ancestro del remoto.
Por tanto, estas implementaciones ya están versionadas y publicadas; no se
necesita inventar otra equivalencia ni duplicar el motor.

B: HEAD local permanece `80ca13a5a249a1a2bd53a699f5f73689b1f53040`.
No se sincronizó ni cambió la rama. El documento de unificación del15-oct existe
localmente pero no aparece en el commit remoto consultado; no se declara que
toda la documentación local esté publicada.

E: no se localizó en esta revisión acotada un manifiesto de envío que vincule
la aplicación de NIV_ACA_EQ_SEM_APLICADA con dos cargas efectivamente enviadas.
Código publicado no prueba envío o aceptación. La diferencia entre consumidores
de presencia queda documentada, sin modificar ni declarar erróneos los envíos.

## Fuentes y conservación

B: hashes verificados del código y configuración publicados:

- codigo_gobernanza_v2.py:
  `ddb8cba1f4af1df8c273db90b462951db3db1ce52c3218af8d472e62da9e3c4d`.
- control/config_campos_ing.json:
  `d02d2affe3069b79caf64a1df0c8e6f2ad0ac4833db9527f74b6dd0b50279f63`.
- V13 entregado:
  `c4f506adcf16e9ae2bbf072d21be5033e30ee6ee81eb5bc87171a73867cc164b`.
- PDF oficial en
  `requerimiento_bettersoft_uplus_2026/01_fuentes_oficiales/avance_curricular_2026/Instructivo_Avance Curricular SIES - 2026.pdf`:
  `bf5a986c28f3312501d00e65447417a5927c252ae89d68cc9fc48bc35056d45f`.
  Se contrastó su texto con el instructivo incorporado al proyecto ChatGPT,
  secciones2,3.g–j y campos de páginas12–13.

C/D: esta nota es una auditoría local adicional; no modifica reglas activas,
fuentes, denominadores, tasas, archivos Excel, complementos ni skills.
No contiene identificadores individuales. Sin commit ni push.

E: siguiente paso útil, si se decide comparar fuentes, es contrastar foto y
actividad del mismo período/persona/expediente, manteniendo la población fijada
y separando cambio de carrera, convalidación, estado actual y cierre histórico.
No es necesario repetir la búsqueda de código SIES para hacerlo.

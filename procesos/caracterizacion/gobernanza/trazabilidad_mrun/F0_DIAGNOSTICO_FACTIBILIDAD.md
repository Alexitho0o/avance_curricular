# F0 — Diagnóstico de factibilidad de conciliación RUT (U+) ↔ MRUN (SIES)

**Fecha:** 16-09-2026 · **Script:** `scripts/f0_diagnostico_factibilidad.py` · **Estado:** análisis, sin cruce real ejecutado ni técnica probabilística aplicada.

## Fuentes

- Maestro interno U+ (corte de referencia, 15-09-2026): `DATOSDEALUMNOS_11146.xlsx` — 14.604 filas, 12.539 RUT únicos.
- Matrícula unificada SIES granular, IP San Sebastián 2007-2026: `reporte_matricula_ip_san_sebastian_2007_2026_20260901.csv` — 24.386 filas, 11.265 MRUN únicos.
- Bridge CODCARPR+JORNADA → código único SIES: `avance_curricular/control/catalogos/PUENTE_SIES_COMPILADO.tsv` (ver nota de procedencia abajo).

Los dos primeros ya estaban en las rutas declaradas por el responsable. El tercero se **recuperó** de un commit de `avance_curricular` (`4f1108c`, 22-07-2026) que no es ancestro de ninguna rama viva del repositorio — no estaba en el árbol de trabajo antes de esta sesión. El responsable confirmó que es válido y autorizó recuperarlo; queda citado aquí para que quede trazado.

## Variables disponibles en ambos lados

| Variable | U+ | SIES granular | Comparabilidad |
| --- | --- | --- | --- |
| Fecha de nacimiento | `FECHANACIMIENTO`, día completo (DD-MM-AAAA) | `fec_nac_alu`, solo año-mes (AAAAMM) | Se trunca U+ a AAAAMM. **Pierde el día como discriminante.** |
| Sexo | `SEXO` ('F'/'M', + 9 casos 'S' sin definir) | `gen_alu` ('1'/'2') | **Mapeo 1=M/2=F sin confirmar contra manual oficial** (ver Hallazgo 1). |
| Año de ingreso | `ANOINGRESO` (por matrícula/CODCLI, se regenera al cambiar carrera) | `anio_ing_carr_ori` / `anio_ing_carr_act` | Se usó el mínimo por persona en U+ (aproxima el ingreso más antiguo registrado). |
| Carrera | `CODCARPR` + `JORNADA` (código interno) | `codigo_unico` (100% poblado) / `cod_carrera` (98,6% poblado) | Sin traducción directa; se resolvió vía bridge (ver abajo). No hay manual SIES/PES vigente con esta traducción — el bridge es un sustituto parcial, no el manual oficial. |
| Sede | `SEDE` (código corto) | `nomb_sede` (texto) | No se usó como variable de bloqueo en este diagnóstico. |

## Resultado del bloqueo determinístico

| Bloqueo | N | Sin candidato | Match único | Ambiguo (2+) |
| --- | --- | --- | --- | --- |
| fecha(año-mes) + sexo + año de ingreso | 12.539 | 1.158 (9,2%) | 3.184 (25,4%) | 8.197 (65,4%) |
| + carrera (solo el 52,9% de personas cuya carrera actual resuelve a un código SIES único vía el bridge) | 6.629 | 2.805 (42,3%) | 3.338 (50,4%) | 486 (7,3%) |

**Lectura:** el bloqueo base por sí solo es insuficiente — dos de cada tres personas quedan con múltiples candidatos, principalmente porque SIES solo trae año-mes de nacimiento (no el día). Agregar carrera reduce la ambigüedad de forma drástica (65,4% → 7,3%) para el subconjunto donde se pudo resolver, pero ese subconjunto es solo la mitad de la población (47,1% de las personas no tienen su combinación CODCARPR+JORNADA actual resuelta de forma única en el bridge, y quedan sin poder aplicar este refuerzo) y el "sin candidato" sube considerablemente (9,2% → 42,3%), porque exigir coincidencia exacta de código único SIES es una condición más estricta que solo cohorte.

## Limitaciones y hallazgos de gobernanza (no resueltos en este diagnóstico)

1. **Mapeo de sexo SIES sin confirmar.** `gen_alu` (1/2) se asumió 1=M/2=F por comparación de proporciones agregadas (U+: M=72,8%/F=27,2% vs SIES: '1'=80,5%/'2'=19,5% — misma dirección, no calzan exacto). No hay manual oficial consultado. Se declara **no consta en materiales** la confirmación de este mapeo.
2. **No existe manual SIES/PES vigente con las traducciones exactas** de jornada→número ni de carrera interna→código SIES en ningún documento disponible en este equipo (HARD STOP del prompt rector). El `PUENTE_SIES_COMPILADO.tsv` recuperado es un sustituto parcial construido a partir del extracto SIES de `DURACION_ESTUDIOS` (ver `gobernanza/sies/DURACION_ESTUDIOS.tsv`), no un manual oficial, y cubre 91 de 161 combinaciones JORNADA+CODCARPR observadas (70 quedan `AMBIGUO` en el propio bridge).
3. **9 personas en U+ con SEXO='S'** (valor no documentado, distinto de M/F) quedaron fuera del bloqueo por no tener sexo mapeable. No se infiere su significado.
4. Este diagnóstico usa el **conjunto de códigos únicos SIES observados a lo largo de todos los años** por MRUN (2007-2026) contra el **código único de la carrera actual** en U+; no filtra por año de proceso. Es una prueba de factibilidad, no una regla de matching final.

## No se ejecutó

- Ninguna técnica de conciliación probabilística (Fellegi-Sunter). Requiere declarar tasa de falsos positivos esperada y autorización explícita antes de ejecutarse sobre datos reales (HARD STOP del prompt rector) — no solicitada en esta sesión.
- Ningún cruce que asigne o persista una relación RUT↔MRUN definitiva. Esto es un diagnóstico de factibilidad, no una fusión de identidad.

## Conclusión para F2

El bloqueo determinístico simple (incluso con carrera) deja como máximo ~50% de la población con un match único confiable, y ese máximo solo aplica a la mitad de las personas. No es una base suficiente por sí sola para pedir a U+ una columna de trazabilidad basada en "podemos reconstruirla igual desde afuera" — al contrario: refuerza el caso de que la trazabilidad debe resolverse en el origen (U+), no reconstruirse post-hoc. Ver `F2_PROPUESTA_COLUMNA_TRAZABILIDAD.md`.

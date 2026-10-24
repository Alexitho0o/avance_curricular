# F2 — Propuesta de columna de trazabilidad para U+

**Estado:** propuesta para decisión del responsable del proceso. No es una implementación ni un compromiso con U+/Bettersoft.

## Problema que resuelve

`CODCLI` (identificador de matrícula en U+) no sirve para trazar a una persona en el tiempo: se regenera al cambiar carrera, jornada u otros atributos del programa (H1-H3 en `trazabilidad-codcli`). El único identificador estable de persona hoy es el **RUT**, que:

- No está en la matrícula unificada SIES granular (esa trae MRUN).
- No permite, por sí solo, reconstruir la ruta formativa completa (cambio de carrera, avance, titulación, eliminación) porque el extracto de U+ no conserva de forma confiable el historial de matrículas no vigentes (evidencia parcial en `F0`/`compara_cortes.py`: hasta un 0,3% de las personas pierden un CODCLI histórico entre extracciones separadas por 91 días, y ese código perdido no siempre corresponde a una baja formal).

## Por qué no basta con reconstruirlo desde afuera

El diagnóstico F0 muestra que ni el mejor bloqueo determinístico disponible (fecha de nacimiento + sexo + año de ingreso + carrera, esta última resuelta solo para el 52,9% de las personas vía un bridge parcial) supera ~50% de match único, y ese 50% aplica solo al subconjunto con carrera resuelta. Reconstruir la relación RUT↔MRUN por fuera de U+, con los datos actualmente disponibles, deja a la mitad de la población sin trazabilidad confiable. La causa raíz — falta de un identificador persistente de persona — solo se resuelve en el origen.

## Qué pedir a U+ (dos alternativas, no excluyentes)

### Opción A — MRUN persistente en el extracto de U+

Que Bettersoft U+ agregue una columna con el MRUN de cada estudiante (obtenido una vez desde el CEM y almacenado de forma persistente en la ficha de la persona, no recalculado por matrícula).

- Ventaja: es el identificador que SIES/CEM ya usan; elimina la necesidad de cualquier conciliación probabilística.
- Riesgo/dependencia: requiere que U+ tenga o adquiera acceso al servicio de asignación de MRUN del CEM, algo fuera del control de IPSS.

### Opción B — Identificador interno estable de persona (no de matrícula)

Que U+ agregue un identificador de **persona**, distinto de `CODCLI`, que no se regenere al cambiar carrera/jornada/sede, y que permita agrupar todas las matrículas históricas de una misma persona (vigentes y no vigentes) sin que las no vigentes desaparezcan del extracto.

- Ventaja: no depende del CEM; U+ ya identifica personas internamente de algún modo (de lo contrario no podría prevenir RUT duplicados).
- Limitación: no resuelve por sí solo el cruce con SIES/MRUN; sigue haciendo falta una conciliación RUT→MRUN (vía CEM) en algún punto del proceso.

## Evidencia que respalda la solicitud

- H1-H6 (`trazabilidad-codcli`, verificado): CODCLI compuesto, se regenera con el cambio de programa, hasta 5 CODCLI por RUT, 60 pares persona-carrera con más de un CODCLI.
- `compara_cortes.py` (esta sesión): en una ventana de 91 días, 0,3% de las personas pierden un CODCLI histórico del extracto, y el 87% de esas pérdidas ocurren sobre matrículas que en el corte antiguo figuraban como "ALUMNO REGULAR"/"VIGENTE" (no solo bajas formales) — el extracto actual no es una fuente confiable para reconstruir el historial completo por fuera de U+.
- F0 (esta sesión): el mejor bloqueo determinístico disponible hoy deja sin match único confiable a más de la mitad de la población.

## Lo que esta propuesta NO incluye

- No propone qué campo técnico exacto debe crear Bettersoft (nombre de columna, tipo de dato): eso corresponde a una conversación con el proveedor.
- No asume que el CEM otorgará acceso a MRUN bajo demanda; eso es una pregunta a resolver antes de comprometerse con la Opción A.
- No reemplaza la necesidad de mantener y versionar las tablas de equivalencia de carrera/jornada/sede (Parte 1 del manifiesto) — eso sigue siendo necesario incluso si U+ agrega la columna.

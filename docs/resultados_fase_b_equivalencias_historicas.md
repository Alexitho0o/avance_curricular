# Resultado de la fase B — Equivalencias históricas

**Corrección de alcance, 2026-10-16:** las diferencias nominales descritas aquí
no son un bloqueo para las agrupaciones ya resueltas. Se retoma el puente de
programas y duración, usando ANOINGRESO de DatosAlumnos para investigar versiones;
ver [implementación corregida](resultados_versiones_por_cohorte_20261016.md).
La acreditación de CODPESTUD individual es distinta de esa regla interna por
cohorte y no se exige para ejecutar su evaluación.

Fecha: 2026-10-15. Estado: evaluación reproducible implementada; acreditación
de equivalencias pendiente de evidencia. Se complementa H1–H8 sin regenerar
el Excel, cambiar H5 ni promover los paquetes consumidores.

## Resultado y alcance

Se evaluaron los 513 candidatos existentes y se conservaron los 141 códigos
SIES y 236 planes UMAS. No se reinició la agrupación ni se descartaron carreras
sin estudiantes o sin oferta 2026. Los 38 códigos sin candidatos y 87 planes
sin candidatos siguen presentes, con una brecha explícita.

| Control | Resultado |
|---|---:|
| Contextos de búsqueda con un solo código candidato, aún no acreditado | 127 |
| Contextos con varios códigos candidatos | 166 |
| Candidatos cuyo nombre interno coincide literalmente con el catálogo del plan | 342 |
| Candidatos con nombre distinto, sin alias acreditado | 171 |
| Candidatos con régimen UMAS/SIES 2026 igual | 23 |
| Candidatos con régimen UMAS/SIES 2026 distinto | 85 |
| Candidatos sin información comparable de régimen en 2026 | 405 |
| Candidatos sin oferta observada en 2026, conservados con su historia | 76 |
| Candidatos con actividad observada anterior a primera oferta | 10 |
| Nuevas equivalencias acreditadas | 0 |

Los conteos de candidatos no son conteos de carreras, personas o matrículas.
Los 171 nombres distintos corresponden a 56 planes; incluyen diferencias de
espaciado y nombres, sin afirmar que todas sean errores. Los 85 regímenes
distintos tampoco prueban una equivalencia incorrecta: deben contrastarse sus
unidades y la conversión formal aplicable. No se usa NIVEL como duración.

## Concordancia anual de oferta y MRUN

Se conservaron 767 claves año/Código Único: 452 en ambas fuentes, 295 solo en
oferta y 20 solo en MRUN. En las 452 compartidas, nombre, jornada, tipo de plan,
duración de estudios y duración total coinciden literalmente. Modalidad coincide
en 444 y permanece desconocida en ocho. No se trasladó un dato desde otro año.
Esto acredita concordancia de esos perfiles, no una relación con CODPESTUD.

Se registraron 97 transiciones entre años observados con cambios en al menos
uno de los ocho atributos examinados. Incluyen campos que pasan de vacío a
informado; no equivalen a 97 renovaciones curriculares. El caso I162S2C35J4V1,
5→6 semestres entre 2018 y 2019, conserva causa no acreditada.

## Ejemplos para revisar la lógica

| Contexto | Evidencia conservada | Conclusión permitida |
|---|---|---|
| ILOG / ILOG20241 / RE / O | I162S2C77J4V1 inicia en oferta en 2024; SIES regular de 8 semestres. El catálogo UMAS nombra INGENIERIA EN LOGISTICA. H5 contiene además una candidatura para ese mismo plan con nombre interno de continuidad. | Separar la candidatura cuyo nombre coincide de la que requiere alias; no trasladar el inicio de continuidad a regular. |
| CILOG / CILOG20241 / RE / O | I162S2C77J4V2 inicia en 2025; continuidad de 4 semestres. UMAS muestra seis niveles y régimen TRIMESTRAL. H5 también conserva candidatos a V1 regular. | V2 es una hipótesis de perfil coherente, pero niveles, nombre y coincidencia cronológica no documentan por sí solos la vigencia de la equivalencia. |
| NATP / NATP20251 / RE / V | Candidatos V1 continuidad (oferta desde 2025, 4 semestres) y V2 regular (desde 2026, 8 semestres, 12 trimestres). La actividad UMAS observada es de 2026. | No elegir V1 por «2025» en el plan. El perfil apoya investigar V2; conservar el vínculo como candidato hasta acreditar la relación. |
| IECIRE20211 | Hay actividad observada desde 2019 en jornada V, anterior al patrón 2021 del identificador; los candidatos incluyen varias versiones. | El año del identificador no gobierna la asignación histórica. La etiqueta del reporte no acredita el plan vigente para cada nota. |

## Evidencia pendiente y cómo incorporarla

Se revisaron H4/H5, el catálogo documental U+ V001, la documentación local de
ambos módulos y el diagnóstico de Docencia `CRUCE_DOCENCIA_MALLA_PERFIL_VS_PRECARGA_SIES_20260812_101234.json`.
Este último cruza por nombre normalizado y tipo de plan, dentro del proceso 2027;
no acredita CODPESTUD ni vigencia histórica. La búsqueda local de definiciones
SQL de View_promedios_alumnos y de referencias CODPESTUD/vigencia no localizó
un contrato adicional ejecutable. No se accedió a una base de datos UMAS.

El catálogo V001 describe ANO, PERIODO y PLAN_DE_ESTUDIO en PROMEDIOS, pero no
el linaje de la columna de plan. H4 conserva sus localizadores documentales y
las fuentes candidatas: historial de asignación, View_REGISTRO_DE_ASIGNATURAS /
RA_CARGA_RASTRO y definición SQL de View_promedios_alumnos. Las fechas de una
asignatura no se convierten en fechas de vigencia de una malla.

Para acreditar una **equivalencia entre programas**, la evidencia debe contener:

1. CODCARPR, CODPESTUD, sede y jornada UMAS, con el Código Único SIES completo.
2. Años/períodos y régimen para los que rige la relación, o fechas efectivas
   cuya conversión a períodos esté documentada.
3. Documento, tabla o resolución de origen, hash y localizador verificables.
4. Alias explícitos si el nombre interno de la consulta difiere del catálogo.

Una relación documental explícita y temporalmente acreditada puede resolver
el vínculo sin deducirlo de todos los atributos secundarios. Las brechas de
modalidad, nivel o duración describen validaciones pendientes; no obligan a
inventar esos campos cuando la equivalencia está documentada directamente.
Para reconstruir además la **asignación individual**, se requiere el historial
de plan por matrícula o una fuente que documente esa semántica por período.

Una clave UMAS completa y período no puede asignarse a dos códigos incompatibles.
La consulta inversa puede devolver varias mallas para un código SIES cuando
estén respaldadas. No se genera una sucesión artificial V1→V2 por fecha.

## Validación y reproducción

Pasaron 16 pruebas focalizadas, incluyendo integridad alterada, bloqueo de
sobrescritura, preservación de universos, claves sin colisiones y unidades/fechas
que no autorizan asignaciones. La reproducción comparó todas las salidas
byte a byte sin escribir. El CSV nacional completo se verificó por SHA-256;
el derivado institucional conserva todos sus 747 registros y 69 campos.

```sh
python3 scripts/evaluar_equivalencias_historicas.py --verificar
python3 -m unittest discover -s tests -p test_evaluacion_equivalencias.py -v
```

- [Especificación previa](fase_b_evaluacion_equivalencias_historicas.md).
- [Resumen](../data/versiones_historicas_sies_umas/fase_b_20261015/resumen.json).
- [Evaluación de candidatos](../data/versiones_historicas_sies_umas/fase_b_20261015/evaluacion_candidatos.json).
- [Conciliación oferta/MRUN](../data/versiones_historicas_sies_umas/fase_b_20261015/conciliacion_oferta_mrun.json).
- [Cobertura SIES](../data/versiones_historicas_sies_umas/fase_b_20261015/cobertura_sies.json).
- [Cobertura UMAS](../data/versiones_historicas_sies_umas/fase_b_20261015/cobertura_umas.json).
- [Brechas](../data/versiones_historicas_sies_umas/fase_b_20261015/brechas.json).
- [Manifiesto de entradas y salidas](../data/versiones_historicas_sies_umas/fase_b_20261015/manifest.json).

La fase B queda ejecutada en su evaluación técnica y cobertura, con acreditación
documental pendiente. La fase C no debe publicar estos candidatos como versiones
resueltas. El registro de brechas permite continuar sin repetir decisiones en
cada búsqueda ni ocultar las relaciones aún no acreditadas.

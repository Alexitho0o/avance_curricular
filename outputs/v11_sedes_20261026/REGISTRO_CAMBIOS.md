# Registro de cambios · sedes UMAS–SIES y complemento (26-10-2026)

## Actualización posterior autorizada

Alexi aprobó las tres familias CO y autorizó publicación 1.1.5, actualización de la skill local y commit sin push. El complemento privado se publicó como `pluginrel_6adfaf940d3c8191be8320d69110b45e` y se releerieron los tres archivos modificados; falta una prueba en conversación nueva. La skill local fue actualizada y su validador pasó. El punto 7 de la nueva referencia se corrigió antes de publicar: el corte de retención no se extrapola a otros procesos SIES. `DECISION_APROBADA_FAMILIAS_CO_20261026.md` registra alcance y excepciones. Las tablas siguientes describen el estado anterior a esta actualización.

Responsable de preparación: Claude, a pedido de Alexi. Sin commit, push ni publicación.

## Estado por canal

| Elemento | Local | Git (feature/ire-2026, e70afd3) | Remoto (GitHub / complemento) |
|---|---|---|---|
| `gobernanza_sede.tsv` (raíz, RE→2, CO→3) | sin cambios | versionado | publicado |
| `data/gobernanza_sede.tsv` (nota de traslado, 45 B) | sin cambios | versionado | publicado |
| `docs/sedes_umas_sies_trazabilidad_20261026.md` | **corregido y ampliado** (antes: `sedes_umas_sies_trazabilidad_20261026.ANTES.md`) | sin seguimiento | no |
| `outputs/v11_fase1_cobertura_20261026/` | evidencia Fase 1 | sin seguimiento | no |
| `outputs/v11_sedes_20261026/` | nuevo (este registro, QA, candidato) | sin seguimiento | no |
| Complemento «analisis-institucional-alexi» | candidato 1.1.5 preparado | — | **1.1.4 vigente**, sin cambios |
| Skill local Codex `ipss-verificacion-cifras-matricula` | parche preparado; carpeta no accesible desde esta sesión | — | — |

## Cambios

1. **C — Corrección documental.** La nota de sedes citaba `data/gobernanza_sede.tsv` como catálogo; el catálogo real es `gobernanza_sede.tsv` en la raíz. `data/` solo contiene una nota de traslado.
2. **B/E — PTG → S4.** Evidencia: carga oferta 2027 etapa 1 V06 con `4;SEDE PATAGONIA` (aceptación en PES solo declarada por el usuario). El reporte 5912 no contiene sede 4; sus coincidencias de sede 2 no la confirman. Queda E hasta tener el listado de sedes SIES o una descarga de PES.
3. **B/E — Puerto Montt.** Solo en documentos internos de docencia y en el prefijo `PM` de UMAS; sin vínculo SIES con Patagonia ni con el código 4.
4. **C — Sede CO.** Capas separadas (sede, familia, versión, atribución). Excepciones: COTEIQ 2/42, COTFAR 1/19; sin MU 2026: 9. La propuesta de programas sigue pendiente de aprobación.
5. **C — Complemento 1.1.5 (candidato).** Nueva referencia `references/sedes-umas-sies.md`; paso 9 en `diccionario-sies-seguimiento.md`; enlace en las dos skills; versión 1.1.5. Sin bases, Excel ni identificadores. `COMPLEMENTO_CAMBIOS_1.1.4_a_1.1.5.diff`, `MANIFIESTO_COMPLEMENTO_1.1.5.json`.

## Pendientes y autorizaciones

- Publicar el complemento 1.1.5: releer el release remoto (`expected_release_id` en el manifiesto) y publicar con su mecanismo; requiere autorización específica.
- Aplicar el parche a la skill local de Codex: `skill_local_codex_candidata/` (la sesión no puede acceder a `~/.codex`).
- Aprobar o rechazar la propuesta de programas de sede CO (`outputs/v11_fase1_cobertura_20261026/PROPUESTA_D_SEDE_CO.json`).
- Obtener el listado de sedes SIES (Etapa 1, «Consultar Oferta Académica Vigente…», o solicitud a SIES) para cerrar PTG → S4.
- Commit de `docs/sedes…`, `outputs/fase3_sin_contexto_20261026/`, `outputs/v11_fase1_cobertura_20261026/` y `outputs/v11_sedes_20261026/`, cuando lo autorices.

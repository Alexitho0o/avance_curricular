# GUIA_INTERVENCION_SEGURA

## Rol del documento

`GUIA_INTERVENCION_SEGURA.md` es el manual operativo de cambio del proyecto `CARACTERIZACIÓN`.

No es documento rector primario. Debe usarse después de:
- [MAPA_MAESTRO_CARACTERIZACION.md](./MAPA_MAESTRO_CARACTERIZACION.md)
- [MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md](./MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md)

Su función es responder:
- si tocas X, qué debes leer antes
- qué frontera metodológica estás cruzando
- qué mínimo debes validar antes de cerrar

## Secuencia obligatoria antes de tocar algo

1. identificar el frente afectado
2. identificar la llave dominante real
3. revisar el mapa maestro
4. revisar el mapa KPI/gobernanza si el cambio afecta métricas, niveles o naming
5. ubicar el bloque en `MANIFEST_BLOQUES.yaml` y `TVS_BLOQUES.md`
6. revisar contratos e invariantes si el cambio toca entradas, llaves o consolidación
7. recién después editar

## Matriz rápida: si tocas X, lee Y

| Si tocas… | Lee primero | Lee después |
|---|---|---|
| layout matrícula | mapa maestro | contratos + guía |
| llaves analíticas | mapa KPI/gobernanza | contratos |
| encuesta pura | mapa maestro | TVS + guía |
| salidas focalizadas de categorías / financiamiento | mapa maestro + contratos | TVS + guía |
| pregrado longitudinal | mapa maestro + mapa KPI/gobernanza | contratos + TVS |
| posgrado | mapa maestro + mapa KPI/gobernanza | TVS |
| cruce SIES complementario | mapa maestro + contratos | TVS + guía |
| KPI o naming | mapa KPI/gobernanza | guía + contratos |
| dashboards | manifest | guía |
| consolidación final | mapa maestro | contratos + manifest |
| salidas operativas | TVS | guía |

## Guía por clase de cambio

### Cambio en layout de matrícula
- leer: mapa maestro + contratos
- tocar: `B0` y `B1` solo si el layout real cambió
- validar: universos base, vigentes, eliminados, históricos, libros finales

### Cambio en llaves analíticas
- leer: mapa KPI/gobernanza + contratos
- tocar: solo después de fijar si la unidad real es `RUT`, `CODCLI`, `CODCLI_PERIODO` o `REGISTRO`
- validar: que no cambie la interpretación metodológica de KPI y hojas

### Cambio en encuesta pura
- leer: mapa maestro + TVS de `B8`, `B9`, `B10`
- validar: que no se rompa `ENCUESTA_CARACTERIZACION` ni el contrato `B8 -> B9 -> B10`
- si el cambio también afecta cruces externos o contraste con matrícula/SIES, no tratarlo como encuesta pura: reencuadrarlo como cambio en `B10.quater`

### Cambio en salidas focalizadas de categorías / financiamiento
- leer: mapa maestro + contratos + TVS de `B6` y `B6.bis`
- validar: que `B6` siga produciendo la base maestra de categorías y que `B6.bis` siga derivando `financiamiento_*.xlsx` sin recalcular la lógica base
- detenerse si: el cambio rompe la correspondencia entre `Lista_tokens_categorias_SI_*.xlsx` y `financiamiento_*.xlsx`

### Cambio en longitudinal de pregrado
- leer: mapa maestro + mapa KPI/gobernanza + contratos + TVS de `B10.bis`, `B11`, `B12`
- validar: cohorte, continuidad, niveles de análisis, consolidación final y dashboard absorbido

### Cambio en posgrado
- leer: mapa maestro + mapa KPI/gobernanza + TVS de `B10.ter`
- validar: separación metodológica, trazabilidad de `CODCLI` y frente autónomo

### Cambio en cruce SIES complementario
- leer: mapa maestro + contratos + TVS de `B10.quater`
- validar: universo base SIES, dependencia de `B10.bis` y `B10.ter`, trazabilidad de `RUT` y `CODCLI`, salida `CRUCE_SIES_*.xlsx`
- revisar además: si el cambio toca normalización de estados, integración de promedios, blindaje Excel o postprocesamiento visual, entonces también afecta la capa helper transversal `B10.x`
- detenerse si: el cambio obliga a forzar resolución sin reporte SIES filtrado o altera el universo base del cruce

### Cambio en KPI o naming visible
- leer: mapa KPI/gobernanza primero
- validar: consistencia cruzada entre hojas, dashboards y nivel analítico declarado

### Cambio en dashboards o consolidación
- leer: manifest + contratos + guía
- validar: tres libros finales, no reaparición de redundancias, integridad del workbook final

## Checklist mínimo de cierre

- el cambio respeta la llave dominante del frente
- el cambio respeta el nivel analítico real
- no se mezclaron pregrado, posgrado y encuesta
- no se rompieron contratos visibles de entrada o salida
- si toca `B6.bis`, sigue existiendo trazabilidad explícita `B6 -> B6.bis`
- si toca `B10.quater`, sigue existiendo trazabilidad explícita `B10.bis + B10.ter -> B10.quater`
- si toca contratos, exports o normalizaciones compartidas, se revisó el impacto de la capa helper transversal `B10.x`
- si toca libros analíticos, siguen existiendo solo los tres finales troncales vigentes
- si toca `CRUCE_SIES_*.xlsx`, sigue tratándose como salida analítica complementaria y no como libro final troncal
- si toca naming, el nuevo nombre es más claro y no cambia la metodología

## Fronteras que obligan a detenerse y releer

Detenerse y releer si el cambio cruza simultáneamente:
- `TOKEN` y `CODCLI`
- `RUT` y cohorte de trayectoria
- encuesta pura y base integrada de pregrado
- pregrado y posgrado
- KPI y consolidación de libros
- naming metodológico y lógica de agregación

## Qué este documento no debe hacer

No debe:
- reemplazar el mapa maestro
- redefinir la gobernanza de niveles de análisis
- duplicar contratos completos
- convertirse en un README alternativo

## Perímetro de intervención segura

- No tratar `backups/`, `diagnosticos/`, `docs/`, `cuarentena_revision_manual/` ni `archive/` como bloques funcionales del pipeline.
- Si un cambio afecta solo estas carpetas, documentar el motivo y evitar reinterpretarlo como cambio de contratos, bloques o entrypoints.
- Antes de reactivar cualquier archivo desde cuarentena o archive, verificar referencia explícita en `README`, mapa maestro, manifest y contratos.

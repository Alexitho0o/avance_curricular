# v11 · Fase 1/5 · Mapa existente y cobertura (26-10-2026)

**Hito 1/3 · B/C.** Rama `feature/ire-2026`, HEAD = remoto = `e70afd3`. Activo: v10 (`409d77a8…`), base y
componentes verificados, sin rutas `/sessions/`. 27 decisiones vigentes; la propuesta de 31 está reemplazada.
Sin seguimiento: `outputs/fase3_sin_contexto_20261026/` y 4 elementos ajenos de oferta 2027 (intactos).
Hashes de `grupos_existentes.json`, `PRUEBAS_CONTEXTUALES.json` y `maestro.json` coinciden con los esperados.

**Hito 2/3 · B/C.** `reproducir_puente_20261023.py` toma el universo desde `PRUEBAS_CONTEXTUALES.json`
(`families`, 63 combinaciones), mientras que `G` viene de `grupos_existentes.json` (132 grupos, sede RE).
Hay 52 combinaciones con actividad 2024+ fuera del filtro (41 solo con 12166; 11 más con 7804 y 3233).
Estados: 32 familia respaldada (grupo gobernado y MU coinciden), 2 respaldada con divergencia MU (CICRE-V,
CIIND-O), 4 en grupos sin MU (diplomados), 11 no localizadas (3 de sede CO con MU en S3; 7 diplomados o
educación continua; TFARSP), 3 conflicto (TCSRE-D/V, DACD). `COBERTURA_COMBINACIONES.json/.csv`.

**Hito 3/3 · C.** 311 y 488 son conjuntos distintos (308 en común). El 55 era anterior a la base v10 (56).
Corte oficial de matrícula: 30 de abril (A); 08-05-2025 es fecha de carga (B); exportación UMAS no
acreditada (E). `INCONSISTENCIAS_INVENTARIO.json`.

**D · 26-10-2026 16:30.** Alexi aprobó: (1) ampliar con las 32 combinaciones respaldadas; (2) excluir del
seguimiento diplomados y educación continua; (3) abrir propuesta D para sede CO → S3
(`PROPUESTA_D_SEDE_CO.json`: COTEIQ→C114J2, COTENS→C91J2, COTFAR→C115J2, todas V1, solo 2026),
pendiente de su aprobación. `DECISIONES_FASE1.json`.

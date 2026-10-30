# H006 · Resumen, carreras y formato de entrega

D · Alexi, 30-10-2026. Nuevas agregaciones autorizadas, sin reconstruir enlaces ni paridades. Sin commit/push en avance_curricular.

B/C: 4 familias con primera matrícula hasta 2016 y matrícula 2026; 78 VIG1. Tres sólo admiten antiguos en oferta 2027; una queda E. Rezago aproximado: 1; titulación proceso 2026: 38 registros en estas familias.
«Quedan por titular» es el proxy D solicitado (VIG1), no una comprobación individual de ausencia de título. Titulación proceso 2026 corresponde a su ventana 2025–2026; no se descuenta de VIG1. Rezago C usa años enteros frente a duración de estudios/2.

B/C: 125 códigos-año ofertados con nuevos y sin fila pública de matrícula. No acredita una no apertura operativa. Por año: 2013: 2; 2014: 7; 2015: 2; 2016: 1; 2017: 3; 2018: 3; 2019: 7; 2020: 4; 2021: 8; 2022: 10; 2023: 10; 2024: 19; 2025: 23; 2026: 26. 2027 no evaluable hasta MU 2027.

C: tendencia en 77 familias/grupos: {'CERRADA': 21, 'NUEVA': 40, 'ALZA': 10, 'BAJA': 4, 'ESTABLE': 2}. Prioridad explícita: CERRADA, NUEVA, EN_EXTINCION, ALZA/BAJA/ESTABLE. Primer año vacío en cualquier versión se muestra E, nunca cero. CERRADA sólo expresa total publicado 2026=0; no cierre administrativo. Dos códigos legados no descomponibles conservan sede/jornada/sector E; no se inventan equivalencias.

## Mayores variaciones absolutas 2022–2026

| Familia | Carrera | 2022 | 2026 | Variación |
| --- | --- | ---: | ---: | ---: |
| I162S2C46J4 | INGENIERIA EN CIBERSEGURIDAD | 106 | 334 | +228 |
| I162S2C1J4 | INGENIERIA EN INFORMATICA | 131 | 325 | +194 |
| I162S2C76J4 | INGENIERIA EN ADMINISTRACION DE EMPRESAS | 0 | 153 | +153 |
| I162S2C77J4 | INGENIERIA EN LOGISTICA | 0 | 130 | +130 |
| I162S2C91J2 | TECNICO EN ENFERMERIA | 0 | 112 | +112 |
| I162S2C3J2 | INGENIERIA EN CONECTIVIDAD Y REDES | 48 | 8 | -40 |
| I162S2C6J4 | TECNICO EN CONECTIVIDAD Y REDES | 72 | 45 | -27 |
| I162S2C57J2 | TECNICO EN PROGRAMACION Y ANALISIS DE SISTEMAS | 44 | 25 | -19 |
| I162S2C22J2 | INGENIERIA EN AUTOMATIZACION Y CONTROL INDUSTRIAL | 16 | 0 | -16 |
| I162S2C6J2 | TECNICO EN CONECTIVIDAD Y REDES | 23 | 7 | -16 |

Incluye familias NUEVAS y CERRADAS en los rankings: las barras comparan variación absoluta, no sólo las clases ALZA/BAJA.

## QA y conservación

39.546 controles de celdas del resumen, incluidos los 34.960 anteriores idénticos; 1237 controles independientes de agregados. 745 fórmulas sin errores. Retención: 1.956 controles y 41 fórmulas sin errores. Doce escenarios de filtros, más Todas; reproducción de modelos idéntica.
Se compararon todas las celdas pobladas preexistentes, sus fórmulas y sus valores recalculados: cero cambios. Sólo formato centrado/ajuste y nuevas hojas del resumen. Los 24 cambios ajenos y las fuentes se conservan. Ambos libros abren sin reparación en Excel; no se guardaron cambios desde Excel.
El QA antiguo de H003 conserva su guardia histórica de HEAD; no se alteró. El QA H006 verifica el HEAD de esta tarea y repite sus 1.956 controles y 41 fórmulas.

| Libro | SHA-256 (igual en Escritorio) |
| --- | --- |
| RESUMEN_CRUCE_SIES_UMAS_20261030.xlsx | 5338543e375ed227e0297ed6ab136e1a67392e94f5969b1dd38b0d537578b03d |
| ENTREGA_RETENCION_IPSS_20261029.xlsx | 70baf95a8daf364854f75d714d0d37af82876eb9f8302e01cb334f90e668a19e |

Fuentes y hashes: FUENTES_FIJADAS.json + FUENTES_H006.json. Controles: CONTROL_CIFRAS.json, CONTROL_INDEPENDIENTE_H006.json y QA_H006.json. PNG: renders/ (paneles y detalles) y renders_h006/ (nueve hojas). Retención: renders_artifact/ y renders/.

## Regla de centrado

IPSS_IA_SKILLS_Y_REGLAS 1.3.10, commit c62b6908303ffcabdcfb44114ad0f0b0813da8a6, publicado. Codex idéntico a canónica. Vistas ejecutivas no impone una alineación de cuerpo contradictoria; no se modificó.
Variante Claude: skills/claude/excel-formato-chile/SKILL.md; SHA-256 f9aeb966dbb6a7fc4a2ce91c7795dcfac318446172d2bd71393661bffabdc5a8. No instalada en claude.ai.

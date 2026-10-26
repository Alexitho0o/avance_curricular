# Fase5/6 · Hito3/3

B/C: V20 guardada en `/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V20.xlsx` (SHA-256 `b9dd851da572d48635815ddb0649bf20d92b14e42cec3509898dff6a53d132f7`). ZIP íntegro; las ocho gráficas de `14_Vistas_Ejecutivas` apuntan a rangos auxiliares dinámicos DA:DX. Las 1.976 conciliaciones agregadas permanecen sin diferencias.

B: Se ejecutaron los 77 casos de filtros de `CASOS_FILTROS.json` en Excel V20, en bloques de 15 (último de 17): 77/77 coincidencias, 0 diferencias. Se restauraron los selectores a `Acumulado 2022-2025 / Todos / Todas` = 2379/1476/62,04%. No se modificaron bases ni denominadores.

C: QA de gráficos: las referencias XML existen, pero la revisión visual de las capturas detectó rangos auxiliares incompletos para algunas selecciones múltiples. Las tablas y filtros pasan; los gráficos requieren una corrección adicional.

E: Estado de entrega: **QA bloqueado visualmente**. V20 no debe cerrarse como entrega final hasta corregir los auxiliares y repetir la revisión visual.

D: Sin cambios de bases/denominadores/diccionario, sin commit/push. V19 original permanece intacta. Ver INFORME_FASE5.md y MANIFEST_FASE5.json.

## Reanudación V21 (2026-10-25)

B/C: Se creó la copia `/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V21.xlsx` (SHA-256 `70c24d895dfecb2f8ad2211ad888d823338e06cbdba8be712b16ff43b37341f5`). Los auxiliares faltantes se completaron con fórmulas nativas mediante `openpyxl`, sin modificar las fuentes, bases ni denominadores. El ZIP es íntegro y el libro abre sin aviso de reparación.

B: Se verificó la presencia de las filas auxiliares para DA/DB, DG/DI, DK/DL, DN/DO, DQ/DR, DT/DU y DW/DX. La suite de filtros permanece en 77/77, sin discrepancias.

E: La revisión visual final de las ocho gráficas con filtros representativos aún debe ejecutarse para pasar de `PASS_WITH_SCOPE` a `PASS` completo.

## V22 · formato de etiquetas de gráficos (2026-10-25)

C: Se generó `/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V22.xlsx` (SHA-256 `2923ddd26f3fbd17c8588ce220367f3b363d3ecc31b169d839f7db0dd49e1518`). El único cambio respecto de V21 es el formato de las etiquetas de datos de las ocho gráficas: porcentaje con un decimal (`0,0%`). No se cambiaron valores, fórmulas, referencias, filtros, bases ni denominadores.

B/C: El ZIP es íntegro y el libro abre sin reparación. Las referencias dinámicas de los ocho gráficos se conservan y la suite de filtros permanece 77/77 sin diferencias.

D: V22 queda como copia candidata de entrega; V20 y V21 se conservan sin sobrescribir. No se hizo commit ni push.

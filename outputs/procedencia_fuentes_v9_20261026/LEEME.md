# Procedencia de las fuentes del diccionario v9 (26-10-2026)

**C — Qué hace.** `verificar_procedencia.py` vuelve a calcular el SHA-256 de las 127 fuentes
citadas por v9 y v8 (descriptores y bases privadas) y las clasifica en COINCIDE, DISTINTO,
NO_EXISTE o NO_LEGIBLE. Solo lectura. En el Mac se ejecuta sin argumentos; al leer los archivos,
OneDrive e iCloud los descargan.

**B/C — Resultado de la primera ejecución:** 99 coinciden, 25 no legibles (solo en la nube:
23 en OneDrive y 2 en el Escritorio) y 3 distintos. Ninguna fuente legible cambió.
Los 3 distintos son metadatos del propio proceso:
- `activo.json` citado por v8 y v9 con su valor previo a cada promoción (se conserva en ACTIVO_ANTERIOR.json);
- `LEEME.md` de la candidata v9, al que se agregó una línea después de citarlo.

**C — Errata.** El descriptor v9 registró rutas del repositorio con el prefijo del entorno de
ejecución. Equivalencias en `data/diccionario_sies_seguimiento/v9_20261026_cuatro_planes_v3/ERRATA_RUTAS.json`.
No afecta la consulta: los consumidores no leen esas claves.

**E — Pendiente.** Releer los 25 archivos solo en la nube y el CSV de matrícula SIES 2007–2026.

## Actualización 26-10-2026 10:05 — ejecución en el Mac

**B/C — CSV de matrícula SIES 2007–2026 verificado:** SHA-256 `4c630e05…` igual al manifiesto y al puntero LFS; Latin-1, CRLF, `;`, 58 columnas en las 280.160 filas, MAT_2007–MAT_2026, IPSS 2026 = 3.425 en 66 filas, sin duplicados de grano. Detalle en VERIFICACION_MATRICULA_SIES_2007_2026.json.

**B/C — Fuentes en el Mac:** 91 coinciden; las 3 del Escritorio ya coinciden. Los 12 «no existe» son exactamente las rutas `/sessions/…` de ERRATA_RUTAS.json. El único distinto es `activo.json` citado por v8 con su valor previo a la promoción de v8. **E:** 23 archivos de OneDrive siguen sin poder leerse en el propio Mac.

## Cierre 26-10-2026 11:25 — punto 4 resuelto

**B/C.** Con OneDrive descargado: 123 de 127 fuentes coinciden, incluidas las 35 de OneDrive. Quedan
fuera solo el libro de trabajo V12 del Escritorio (resultado, no base; vuelto a iCloud) y los
3 metadatos ya explicados (`activo.json` citado antes de cada promoción y el LEEME de la candidata v9).
Todas las bases están además copiadas y verificadas en `IPSS_CONCILIACION_UMAS_SIES_BASES`
(ver data/catalogo_fuentes/).

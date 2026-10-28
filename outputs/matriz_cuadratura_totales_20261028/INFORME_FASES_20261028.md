# Consolidación y cuadratura · 28-10-2026

## Fase 0/3 · Extracciones y copias

**B/C:** Matrícula IPSS: 20.961 registros, cod_inst 162, 2007–2025.
SHA-256 `1ae2bf5b1ac47e9ffebc0d4d9040a8fd080b42602fe3176e39b409cad4353de6`.
La copia ORIGINAL es idéntica y no se vuelve a copiar. El código observado filtra
por nombre institucional; se verificó cod_inst del resultado sin regenerarlo.

**B/C:** Titulados canónico institucional: 3.504 registros, 2007–2025,
SHA-256 `70758082b7b5ab6363b267f58d334f86349a6c355dc5636cf1654b90dedca229`.
La copia suelta de GitHub `cfcf9099…` tiene 3.073 registros y termina en 2024:
no se utiliza. No se localizó salida anual filtrada del script correspondiente
en la carpeta de extracción revisada. Los consolidadores son derivados
institucionales de publicaciones oficiales; no son archivos oficiales enviados.

**C:** Quince fuentes/documentos copiados o reutilizados por contenido. Origen
y copia verificados por hash. Véase LISTA_COPIAS.md y PLAN_CONSOLIDACION.json.
Los archivos nacionales permanecen en sus ubicaciones: 56 referencias de ruta/hash,
sin copia. Catálogos JSON/CSV y LEEME idénticos entre repositorio y OneDrive.
El consumidor selecciona bases por hash en el catálogo consolidado; las evidencias
versionadas en Git se conservan como referencias relativas con hash.

Las carpetas 09 y 12 contienen identificadores; se restringió el acceso local de
los directorios. Esto no certifica ni modifica permisos de compartición de OneDrive.
El catálogo y las salidas nuevas del repositorio sólo contienen metadatos/agregados.

## Fase 1/3 · Titulación

**A:** Instructivo Titulación Unificada 2026, páginas 3 y 6: periodo académico
1-mar-2025 a 28-feb-2026, denominado Titulados 2025. La regla histórica de otros
procesos se conserva como evidencia B; no se extrapola la normativa 2026.

**B/C:** Reporte PES 5319 por PERIODO_ACAD_TITULACION frente a publicación:
2021=214, 2022=294, 2023=342, 2024=270; coincide también por código único.
No se enlazan personas RUT con MRUN público.

**B/C/E:** Carga 2022: coinciden los 214 registros por documento/DV/código.
Carga 2023: coinciden los 283 y el PES registra 11 adicionales (6 C1J4V2,
3 C3J4V2, 1 C57J2V1 y 1 C6J2V1); fundamento de la carga adicional E.
Respaldo 2024: 341 coincidencias, 5 sólo en respaldo y 1 sólo en PES; neto +4.
Cuatro de los cinco tienen identidad y código en otro período PES; el restante
presenta cuerpo de documento coincidente y DV diferente. No se corrigen DV,
fechas ni fuentes. Detalle privado y hash referenciados desde la matriz.
Proceso 2025: 270 registros en el histórico PES; envío individual no localizado.

## Fase 2/3 · Edición aditiva de grupos

**D/B/C:** `data/versiones_por_cohorte/20261028/grupos_existentes.json` conserva
los 132 grupos anteriores y añade COTEIQ/CO/V → I162S3C114J2,
COTFAR/CO/V → I162S3C115J2 y COTENS/CO/V → I162S3C91J2.
Manifest registra hash anterior, oferta 2026 (filas 26534–26536) y gobernanza_sede.tsv.
Es un mapa de cobertura; el diccionario personal v20 no se altera.
Familias sin mapa en 2026: 73 → 0. Total cubierto por familia: 4.032 → 4.105.
Los 3 C35J4 de 2022 permanecen E. La observación de ASRE/ASREOL/TPAREOL en
expedientes de esas personas no acredita la equivalencia histórica del registro MU.

## Fase 3/3 · Brecha MU 2026

**E:** Se conserva 226 sin investigar. La extracción MRUN institucional termina
en 2025; se requiere microdato de matrícula 2026. Método futuro: conciliación de
perfiles código × sexo × rango de edad con MU, incluidos los 960 VIG 0.
No implica crear un enlace individual RUT–MRUN mediante atributos.

## QA y reanudación

Ejecutar `construir_matriz.py` y después `cerrar_qa.py`. QA.json registra controles,
DIFF_AGREGADO.json compara contra 80e2385 y LISTA_COPIAS.md informa hashes.
Estado funcional: parcial con pendientes explícitos. Fuentes, denominadores,
tasas y diccionario personal conservados. Sin commit ni push en esta fase.

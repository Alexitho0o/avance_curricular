# H002b · CHECKPOINT actualizado · 29-10-2026

## Estado vigente [D/B/C/E]

Seis relaciones código SIES–CODCARPR aprobadas D por Alexi; doce combinaciones y 43 códigos sin plan no resueltos. Ninguna asignación individual, cambio de v20, fuente, base, denominador ni tasa. La plantilla se dejó solo con encabezado; el cruce se probó solo con catálogo ficticio.

| Estado | 2026 | 2027 |
|---|---:|---:|
| APROBADA_D_2027 | 0 | 6 |
| CONTINUA | 53 | 53 |
| FUERA_ALCANCE | 11 | 21 |
| NUEVO_2027_CON_PLAN | 0 | 0 |
| NUEVO_2027_SIN_PLAN_E | 0 | 43 |
| SIN_OFERTA_2027 | 4 | 0 |
| VERSION_MULTIPLE_E | 14 | 14 |
| VERSION_MULTIPLE_RESUELTA | 24 | 24 |
| TOTAL | 106 | 161 |

## Aprobaciones y planes por cohorte

DECISIONES_APROBADAS.json es la fuente D (Alexi, 29-10-2026). La aprobación es código–CODCARPR. La tabla añade plan_por_cohorte, reutilizando las cohortes y la evidencia del maestro; no se elige malla por nombre ni año del identificador. Tres correspondencias tienen más de una malla y conservan E interno; las tres con candidato único no acreditan una asignación personal.

## Resumen de fichas (propuestas C/E; no aplicadas)

1. CADMP / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
2. CIADM / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
3. CICIB / V: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
4. CNATP / V: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
5. IECIRE / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
6. IECIREOL / O: Referencia respaldada en MU: I162S2C1J4V2; solo propuesta C/E para Alexi. Fuerza: DÉBIL.
7. IETMRE / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
8. IIND / O: Referencia respaldada en MU: I162S2C87J4V2; solo propuesta C/E para Alexi. Fuerza: DÉBIL.
9. NCONRE / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
10. NCONREOL / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
11. NINFREOL / O: Sin propuesta: no existe enlace MU–plan único de esta combinación. Fuerza: SIN EVIDENCIA.
12. TAMD / V: Referencia respaldada en MU: I162S2C78J2V1; solo propuesta C/E para Alexi. Fuerza: DÉBIL.

Los conteos usan la MU 142342 (2024=1541, 2025=2371, 2026=4105) sin filtrar VIG. El plan se vincula solo por identidad con DV, año, código y contexto exactos del v20, en solo lectura. Se distinguen B/C documentales y D internos. Sin vínculo único, cobertura E; no equivale a cero estudiantes. Los contextos de otras jornadas se muestran descartados, no se transfieren. Las fichas comparten familias: no sumar entre ellas.

FOR_ING_ACT conserva el valor informado. Se leyó el catálogo 1..11, el motor exploratorio y el runtime; no se ejecutaron ni se rederivó el campo. La traza y reglas auxiliares del motor exploratorio no están disponibles y se deja constancia. No se adopta versión según vía de ingreso.

## Reproducción y QA

python3 -B outputs/paridad_codigo_sies_20261029/construir_paridad.py --verificar

python3 -B outputs/paridad_codigo_sies_20261029/revisar_casos.py

python3 -B outputs/paridad_codigo_sies_20261029/validar_entrega.py

El QA incluye todas las pruebas H002/H002b y verifica los 24 cambios ajenos por estado y bytes. Sin carga PES. Commit y push del paquete H002 autorizados solo con QA aprobado. El hash de publicación se identifica en el historial del commit que contiene este archivo, sin hash autorreferente.

---

## Registro histórico de H002 (antes de aprobar las seis correspondencias)

Lo que sigue es antecedente del hito inicial, no el estado vigente.
# H002 · CHECKPOINT · 29-10-2026

## Contexto y resultado [C/D/E]

Oferta Académica 2027, proceso ejecutado en 2026. Catálogo 2026/2027; sin unidad persona ni período individual. Rama feature/ire-2026; HEAD 7807542b2b819521b7bd620239110686830ec406. No hubo commit ni push. No se modifica el diccionario personal v20 ni la retención.

Tabla construida: 267 filas = 106 códigos de los grupos 2026 + 161 códigos de la carga V06 2027. Tener código en los grupos no equivale a oferta anual vigente ni a un estudiante. Las propuestas se conservan E.

| Estado | 2026 | 2027 |
|---|---:|---:|
| CONTINUA | 53 | 53 |
| FUERA_ALCANCE | 11 | 21 |
| NUEVO_2027_CON_PLAN | 0 | 6 |
| NUEVO_2027_SIN_PLAN_E | 0 | 43 |
| SIN_OFERTA_2027 | 4 | 0 |
| VERSION_MULTIPLE_E | 14 | 14 |
| VERSION_MULTIPLE_RESUELTA | 24 | 24 |
| TOTAL | 106 | 161 |

## Precedencia y límites [A/B/C/D/E]

- Manual de octubre, PDF oficial: VERSION y tipo de plan, página 22; vigencia, página 28. El TXT de la edición anterior pagina esos campos en 23 y 29. Sus hashes están en FUENTES.json.
- V06: carga preparada C; el registro de confirmación de Alexi es D, no comprobante B de plataforma. No se presenta como descarga 6048. Los estados preliminares de preparación son anteriores a esa confirmación y se preservan como historia.
- 12 grupos/versiones quedan E, representados en 14 códigos por año; no son personas ni 14 carreras.
- Seis códigos sin grupo 2026 tienen candidatos de plan: aprobación D pendiente. Cinco tienen vigencia 2, por tanto no reciben nuevos; uno tiene vigencia 1. “Nuevo” aquí significa no mapeado en los grupos, no programa creado en 2027.
- 43 códigos 2027 quedan sin plan suficientemente respaldado. Algunos ya tienen CODCARPR explícito y les falta CODPESTUD; otros son nuevas jornadas/semipresencialidad u otros perfiles. No se retiran SP ni prefijos ni se traslada J4 a J3.
- Cuatro códigos heredados no aparecen en V06. No hay evidencia de cierre: no se convierten en vigencia 3 por ausencia.
- Las propuestas por código con plan usan el perfil de la equivalencia previa; no certifican duración curricular independiente, equivalencia individual ni año efectivo de malla. Los grupos con perfil interno no unívoco conservan opciones.

## Trabajo previo reutilizado

135 grupos/106 códigos y 52 grupos con más de un código; H5 con 513 candidatos y 236 identificadores de plan; historias de oferta, ensayo de cohortes y cobertura; catálogo anual 2027 ya gobernado; DURACION_ESTUDIOS.tsv real de la raíz y gobernanza_sede.tsv real. No se usan los marcadores homónimos de data/ como si fueran catálogos.

## Fuentes principales y hashes

- `data/versiones_por_cohorte/20261028/grupos_existentes.json` · SHA-256 `fe8837a760d4ed132505bf92138145e08adb3ce0a2486c9e3f26f08ca11babfc` · C/D.
- `data/versiones_por_cohorte/20261016/historias_oferta.json` · SHA-256 `2c0a09a8a85aad4b7af5fa8ba19a4c1017131927e4a848d4d82cd5bcdc2623f5` · B/C.
- `data/versiones_por_cohorte/20261016/resultados_cohortes.json` · SHA-256 `a7f55dbf2ac66f23a3899f4f45b9d8f0110a3abda4e5b8365da5e8003af82cca` · C/E.
- `data/versiones_por_cohorte/20261016/cobertura_codigos.json` · SHA-256 `c0913cbc8056c89327c641dd87a165966ca7096ef40d69658ce423c6cc48d882` · C.
- `data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json` · SHA-256 `2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5` · B/C/E.
- `DURACION_ESTUDIOS.tsv` · SHA-256 `701025451acf2f84078cf185d6ae0be0d8483d37e3b3e9483f70070397aebc6e` · B/C/D.
- `oferta_academica_2027/02_precarga_pes/reporte_dinamico_5913_2026-08-12_08:22:23.csv` · SHA-256 `4d84dbc4620cc9edccd47df3e657d4bbfcf0480b801d88fbd1a35c8dd13b04f3` · B.
- `oferta_academica_2027/10_entrega/etapa1_octubre_20261023_v06/CARGA_OFERTA_2027_ETAPA1_17467_20261023_V06.csv` · SHA-256 `d7fe88035cd1215d448272a9854bee0932c45c200f4f80bb58636b62a6ae4e0b` · C.
- `oferta_academica_2027/00_fuentes_originales/etapa1_octubre_20261020/Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf` · SHA-256 `ff864b1dce48168e6b031c454298e2d3df71d8f2377609366ead13828742d585` · A.
- `data/catalogos_sies/2027/5910_20260907_6047_20261013_modalidad_v2/catalogo.json` · SHA-256 `264f41dc115e1dd3560f9ebbd9f15bbc7a065d02a4708f55ec3e7ec8bf6a5ef4` · B/C.

## Las 24 entradas ajenas iniciales [B]

Se preservan sus bytes; ESTADO_INICIAL.json fija 25 archivos sin seguimiento y los archivos rastreados. No se incluyen ni descartan cambios ajenos.

```text
?? data/catalogo_datos/commits.sh
?? oferta_academica_2027/04_scripts/excel_manual_diplomados_20261023/aranceles_pregrado_informados_20261026.mjs
?? oferta_academica_2027/06_validaciones/aranceles_pregrado_informados_20261026/
?? oferta_academica_2027/10_entrega/aranceles_pregrado_informados_20261026/
?? oferta_academica_2027/11_gobernanza/aranceles_pregrado_informados_20261026/
?? outputs/analisis_desercion_fase2/
?? outputs/fase1_inventario_desercion_20261027/ARCHIVOS_PROPUESTOS.json
?? outputs/fase1_inventario_desercion_20261027/commits.sh
?? outputs/fase2_fase3_retencion_primer_anio_20261027/ARCHIVOS_PROPUESTOS.json
?? outputs/fase2_fase3_retencion_primer_anio_20261027/commits.sh
?? outputs/preparacion_analisis_desercion_fase0_20261027/ARCHIVOS_PROPUESTOS.json
?? outputs/preparacion_analisis_desercion_fase0_20261027/INFORME.md
?? outputs/preparacion_analisis_desercion_fase0_20261027/QA.json
?? outputs/preparacion_respaldo_diccionario_20261027/commits.sh
?? outputs/preparacion_respaldo_fase_c_20261027/commits.sh
?? outputs/preparacion_respaldo_hito2c_20261027/commits.sh
?? outputs/preparacion_respaldo_indicador_20261027/commits.sh
?? outputs/preparacion_respaldo_v15_20261027/commits.sh
?? outputs/preparacion_respaldo_v16_20261027/commits.sh
?? outputs/preparacion_respaldo_v17_20261027/commits.sh
?? outputs/preparacion_respaldo_v18_20261027/commits.sh
?? outputs/preparacion_respaldo_v19_20261027/commits.sh
?? outputs/preparacion_respaldo_v20_20261027/commits.sh
?? outputs/v11_sedes_20261026/COMPLEMENTO_CAMBIOS_1.1.4_a_1.1.5.diff
```

## Entregables y reanudación

- TABLA_PARIDAD_2026_2027.csv/.json, FUENTES.json, README y MANIFEST en data/paridad_codigo_sies/20261029/.
- DECISIONES_PENDIENTES.md/.json contiene las opciones numeradas y las listas completas. RESOLUCIONES_POR_GRUPO.json mantiene perfiles y decisiones separadas por combinación.
- QA.json: 15 controles estructurales y de reglas. VALIDACION_ENTREGA.json y PRESERVACION.json: reejecución, 11 pruebas, verificación independiente y no interferencia.
- No se generó Excel opcional: no agrega evidencia al catálogo; CSV/JSON son las fuentes de esta salida.
- Siguiente paso: Alexi revisa las 12 combinaciones E y las seis propuestas, solicitando evidencia de perfil/malla/ámbito donde falta. Este hito no activa equivalencias ni asigna personas.

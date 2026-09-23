# Cierre Gate 09: resolución de pendientes del Diccionario Maestro U+ → SIES 2026

Subproyecto `requerimiento_bettersoft_uplus_2026` · Rama `feature/ire-2026` · HEAD `4c247e7` · 22-09-2026

**Resultado: APROBADO_PARA_CONGELAR_V1.0**, con dos pendientes explícitos que no afectan requerimientos P1 (C09-05 sexo "S" y C09-09 período 3) y con la revisión visual del Word pendiente de revisión humana.

Principio aplicado: **U+ entrega hechos; la institución gobierna las reglas SIES.** Ninguna implementación histórica, supuesto o decisión interna quedó registrada como regla SIES.

## A. Estado inicial

| Elemento | Valor |
|---|---|
| Diccionario | `resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026.xlsx` (v0.9, 14 hojas, SHA-256 `94f6d9c7…`) |
| Requerimiento | `resultados/REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS.docx` (v0.9, SHA-256 `70a4c9f5…`) |
| Contradicciones | 13 (CT-01 a CT-13) |
| P1 | 25 |
| Fuentes faltantes | 8: Instructivo AC 2026; Instructivo Extranjeros 2026; archivos finales AC, Extranjeros y FCU 2026; estructura Extranjeros Intercambio 2026; evidencia de carga efectiva MU 2026 (v0.9 decía "sin comprobante PES"); manuales MU 2022-2025 |
| Estado | BORRADOR_V0.9 |

## B. Contradicciones revisadas

Las 13 se revisaron una por una con la cadena regla oficial → dato U+ → implementación → archivo enviado → resultado → conclusión (hoja `02_CADENA_EVIDENCIA` de la auditoría). La evidencia decisiva nueva fue el archivo **efectivamente cargado en PES** para MU 2026 (copias `_orig` del 08-05 y 11-05-2026, 4.165 filas) y las **respuestas de error de la plataforma** del 07-05-2026, cruzadas con el snapshot U+ usado en esa carga (08-05-2026) y con la MU enviada 2022-2025.

| ID Gate | ID v0.9 | Tema | Estado Gate 09 |
|---|---|---|---|
| C09-01 | CT-01 | VIG de titulados | NO_DETERMINABLE_DESDE_U_PLUS |
| C09-02 | CT-02 | Cambio de jornada → FOR 3 | IMPLEMENTACION_HISTORICA_INCORRECTA |
| C09-03 | CT-03 | "CONTINUIDAD" → FOR 2 | IMPLEMENTACION_HISTORICA_INCORRECTA |
| C09-04 | CT-07 | SIT_FON_SOL | RESUELTA_DATO_REAL |
| C09-05 | CT-04 | Sexo "S" | PENDIENTE_FALTA_FUENTE |
| C09-06 | CT-05 | País de estudios secundarios | NO_DETERMINABLE_DESDE_U_PLUS |
| C09-07 | CT-06 | Jornada "O" | NO_DETERMINABLE_DESDE_U_PLUS |
| C09-08 | CT-08 | Fecha de nacimiento 1900 | RESUELTA_DATO_REAL |
| C09-09 | CT-09 | Período 3 | PENDIENTE_FALTA_FUENTE |
| C09-10 | CT-10 | Año de origen 1900 con FOR 2 | RESUELTA_REGLA_OFICIAL |
| C09-11 | CT-11 | Oferta: delimitador y fecha | NO_APLICA_AL_PROCESO |
| C09-12 | CT-12 | Oferta: 48 vs 52 columnas | RESUELTA_REGLA_OFICIAL |
| C09-13 | CT-13 | Estructura MU por año | RESUELTA_DATO_REAL |

## C. Contradicciones resueltas (10)

**C09-01 VIG / titulados → TITULADO_NO_DETERMINA_VIGENCIA_SIES.** El Manual MU 2026 define VIG 2 como "estudiante egresado con matrícula vigente" (plan finalizado y actividades conducentes al título) y deja la vigencia a la reglamentación interna. El estado TITULADO vigente en U+ no dice si la matrícula estaba vigente al 30-04. En la carga real: VIG 2 = 0; ninguna fila proviene de un RUT con solo matrículas tituladas; VIG 2 nunca se informó entre 2022 y 2026. Se descartan TITULADO→2 y TITULADO→0, y con ellos todo mapeo estado U+→VIG. Bettersoft no calcula VIG: entrega matrícula del período, historial de estado con fechas y fechas de egreso y titulación.

**C09-02 Cambio de jornada → FOR 3: implementación no respaldada.** FOR 3 exige ingresar a una *nueva carrera*, con código de carrera distinto al del año anterior; según el Anexo 5 del Instructivo Oferta, un cambio de jornada cambia el componente J del código unificado, no el código de carrera. De los 95 FOR 3 cargados en 2026, 85 venían de SITUACION 49 y **83 tenían el mismo COD_CAR en la MU 2025 enviada** (37 incluso con la misma jornada), informados entonces con FOR 1.

**C09-03 "CONTINUIDAD" → FOR 2: el nombre del programa no determina la forma de ingreso.** FOR 2 exige haber cursado un plan común o bachillerato; un programa regular de continuidad admite 2, 3, 4, 5 u 11. FOR 2 nunca se usó en 2022-2025; en 2026 se cargaron 382 filas, todas de programas con "CONTINUIDAD" en el nombre. **164 estudiantes que en 2025 tenían FOR 11 en el mismo programa pasaron a FOR 2 en 2026** sin cambio de hecho, y 4 de los 7 códigos de carrera tienen filas FOR 2 y FOR 11 a la vez.

**C09-04 SIT_FON_SOL = 0 para IPSS.** Código oficial 0 = "No cumple / No aplica". La plataforma rechazó 100 líneas el 07-05-2026 con "La SITUACIÓN SOCIOECONÓMICA FONDO SOLIDARIO no corresponde para el TIPO INSTITUCIÓN"; las cargas aceptadas llevan 0 en el 100% (igual que 2022-2025). La asignación de 1 en el código es incorrecta. Limitación: el log no muestra el valor de las líneas rechazadas. Bettersoft: no calcular.

**C09-06 País de estudios secundarios: no determinable desde U+.** MU 2026 cargó 38 en el 100% (81 filas con nacionalidad extranjera) = DEFAULT_TECNICO. MU 2022-2025 y Extranjeros 2026 copiaron la nacionalidad = SUPUESTO. U+ no tiene el dato (DATO_FALTANTE) y no se halló otra fuente institucional. Se crea brecha P1 (UP-16).

**C09-07 Jornada "O": no basta para el código SIES.** En la carga real, O→4 en 2.442 pares y **O→2 en 2** (ambos con SITUACION 49: la jornada vigente en U+ no era la informada); en el PUENTE, O→J3 en 1 combinación. El código de jornada se toma del componente J del código único de la matrícula en el período.

**C09-08** El fallback 01/01/1900 no se aplicó (0 filas); PES rechazó 2 registros por fechas que implican menores de 15 años (dato de origen). **C09-10** El Cuadro N°6 prohíbe año de origen 1900 con FOR 1, 2, 3 y 6-10; PES rechazó 17 líneas por esa regla. **C09-12** La plantilla PES de Oferta tiene 48 columnas; MALLA_CURRICULAR, PERFIL_EGRESO, TEXTO_REQUISITO_INGRESO y OTROS_REQUISITOS son campos internos del contrato. **C09-13** La diferencia de estructura 2022-2023 frente a 2024-2026 es real y legítima.

**C09-11** no aplica al requerimiento U+: se gobierna en `oferta_academica_2027`.

## D. Pendientes restantes

| ID | Estado | Fuente requerida | Impacto |
|---|---|---|---|
| C09-05 Sexo "S" | PENDIENTE_FALTA_FUENTE | Catálogo oficial de SEXO de U+ (Bettersoft / Registro Académico) | 4 filas NB en MU 2026. No afecta P1: se pide el dato sin transformar |
| C09-09 Período 3 | PENDIENTE_FALTA_FUENTE | Catálogo U+ de períodos con fechas por régimen (Bettersoft) | Semestre de ingreso y avance por semestre en planes trimestrales. No afecta P1 |

Ambos quedan cubiertos por la solicitud UP-68 (catálogos U+ documentados). Otros seguimientos que no bloquean:

- Revisar las filas de Extranjeros Intercambio de la matriz contra el Anexo II del Instructivo Extranjeros 2026, ahora disponible.
- Rectificar ante SIES los registros MU 2026 afectados por C09-02 y C09-03. Es una decisión institucional fuera de este gate; el Instructivo AC 2026 indica que la corrección histórica se solicita a SIES y opera en 2027.

## E. Reglas históricas descartadas (15)

Quedan auditables en `MAPEO_ANTERIOR` / `ESTADO_ANTERIOR` y en la hoja 06 del diccionario (`DESCARTADO_COMO_REGLA`).

1. TITULADO → VIG 2
2. TITULADO → VIG 0
3. Cualquier otro estado U+ → VIG (VIGENTE→1, EGRESADO→2, ELIMINADO→0, SUSPENDIDO→0)
4. SITUACION 49/27 → FOR 3
5. SITUACION 24 → FOR 3 automático
6. Nombre con "CONTINUIDAD" → FOR 2
7. VIASDEADMISION → FOR 1/6/10/11
8. SIT_FON_SOL constante 1
9. FOR 2 ⇒ año de origen 1900
10. Fallback de fecha de nacimiento 01/01/1900
11. País de estudios secundarios = 38 por defecto o desde la comuna del colegio
12. País de estudios secundarios = nacionalidad
13. Sexo S → NB
14. Jornada O → 4 como regla universal
15. Nacionalidad "Por definir" → 38

El período 3 → semestre 2 se mantiene como decisión interna pendiente, no como regla.

## F. Campos Bettersoft modificados

40 de las 61 filas v0.9 cambiaron. Hoja 05 del diccionario v0.9.1, columnas `PRIORIDAD_ANTERIOR`, `ESTADO_ANTERIOR`, `RESOLUCION_GATE09`, `ACCION_BETTERSOFT`, `RESPALDO_NECESIDAD`, `DISPONIBILIDAD_UPLUS` y `P1_DEMOSTRADO`.

- **Pasan a entregarse sin transformar:** sexo, sede, jornada, período de ingreso, nivel, estado civil, comuna, plan, régimen y fecha de matrícula. El código SIES lo asigna la institución.
- **Suben de prioridad:**
  - País de estudios secundarios (UP-16): P2 → P1.
  - Catálogo de planes (UP-58): P2 → P1.
  - Detalle por asignatura (UP-62): P2 → P1.
  - Fechas de egreso y titulación (UP-59, UP-60): P4 → P2.
- **Maestro regulatorio:** UP-27, con la definición `ALMACENAR_CODIGO_UNICO_SIES`, P1, `MAESTRO_REGULATORIO`, granularidad `OFERTA_ACADEMICA` e historizable. Se complementa con los atributos de la oferta (UP-26: modalidad, tipo de plan, nivel, duración) y las reglas de mantención del Anexo 5 (hoja 15). La llave real es institución + sede + carrera + jornada + versión: las 70 combinaciones ambiguas de U+ difieren **solo en la versión**.

## G. Nuevos datos elementales solicitados (5)

| ID | Campo | Prioridad |
|---|---|---|
| UP-63 | Vía de admisión U+ y cupo especial utilizado | P1 |
| UP-64 | Tipo de programa de origen (plan común/bachillerato, TNS, profesional, otro) | P1 |
| UP-65 | Reconocimiento como condición de acceso (RAP) | P2 |
| UP-66 | Historial de matrícula por período (código único, jornada, sede, plan, nivel, estado) | P1 |
| UP-68 | Catálogos U+ documentados | P1 |

## H. Campos que dejan de calcularse en U+ (18 + 4 explícitos)

UP-04 tipo de documento SIES, UP-11 sexo SIES, UP-15 código de nacionalidad, UP-33 forma de ingreso SIES, UP-44 suspensiones previas, UP-45 reincorporación, UP-46 a UP-51 resúmenes académicos MU y UP-52 a UP-57 avance curricular. El Word también declara que U+ no calcula VIG, los códigos SIES de sede, carrera, jornada, modalidad y versión, el semestre SIES ni el nivel en semestres, ni SIT_FON_SOL.

Resultado: **P1 pasa de 25 a 18**, todos con necesidad respaldada por fuente oficial (`P1_NO_DEMOSTRADOS = 0`). De esos 18, 16 no existen en U+ o su existencia debe confirmarla Bettersoft; ese es el objeto del requerimiento (sección 12 del Word).

En la matriz hay 21 filas cuyo valor SIES no se puede determinar con el reporte U+ actual: VIG, FOR_ING_ACT, año y semestre de origen, COD_CAR, VERSION, MODALIDAD, JOR, PAIS_EST_SEC, SUS_PRE y REINCORPORACION en MU, y el país de estudios secundarios en Extranjeros.

## I. Fuentes incorporadas

Se copiaron 22 archivos sin mover los originales, con SHA-256 de origen igual al de destino, y 3 quedaron referenciados. Manifiesto: `01_fuentes_oficiales/MANIFIESTO_FUENTES_GATE09.tsv` (rol, proceso, año, nivel jerárquico, tipo de fuente, datos personales, rutas de origen y destino, bytes, fecha, SHA-256 de origen y destino, fecha de incorporación y estado).

- **Oficiales, en `01_fuentes_oficiales/`:**
  - Instructivos AC 2026 y Extranjeros 2026 (PDF y TXT).
  - Precarga PES de Carreras AC (5810).
  - Estructura PES de Extranjeros Regulares.
  - Reporte PES de carreras para Extranjeros (5769).
  - Plantillas PES de Oferta (Vigente Editada y Nueva).
- **Envío sin datos personales, en `02_evidencia_envios_sin_datos_personales/`:** archivo enviado de Carreras AC (ID 16769).
- **Con datos personales, en `avance_curricular/.local_restricted/requerimiento_bettersoft_uplus_2026/gate09_evidencia/`** (excluido de Git por `.git/info/exclude`; el repositorio es público según `POLITICA_DATOS_Y_GIT.md`):
  - Cargas PES MU 2026 (`_orig` del 08-05 y 11-05).
  - 3 respuestas de error PES.
  - Precargas AC 5809 y Extranjeros 5768.
  - Envíos AC Matrícula, Extranjeros (3 cargas) y FCU P1.
- **Referenciados sin copia:**
  - MU 2026 consolidado: idéntico a `FINAL_4105.csv`, que ya está en el repositorio.
  - `PROMEDIOSDEALUMNOS_7804.xlsx`: la política lo excluye de Git.
  - Manual FCU 2026 (texto).

Siete de las ocho brechas iniciales quedaron cubiertas; la estructura de Intercambio viene en el Anexo II del Instructivo Extranjeros 2026. **Aún faltan:**

- Manuales MU 2022 y 2023. Solo se necesitan para reconstrucción histórica; los de 2024 y 2025 existen en OneDrive y no se incorporaron porque no se requieren.
- Catálogo oficial de U+, que es externo y se solicita a Bettersoft en UP-68.

## J. Bloqueos

Ninguno sobre requerimientos P1. No hubo bloqueos de copia ni de checksum.

## K. Resultado del Gate

| Criterio | Resultado |
|---|---|
| 13 contradicciones revisadas | Sí |
| Todas resueltas o con pendiente explícito | Sí: 10 resueltas, 2 pendientes con fuente requerida, 1 no aplica |
| Ningún supuesto como regla oficial | Sí (QA `supuestos_como_regla_oficial = 0`) |
| Ningún código complejo calculado por Bettersoft sin respaldo | Sí (QA `bettersoft_calculados_sin_regla = []`) |
| P1 con evidencia suficiente | Sí (`P1_NO_DEMOSTRADOS = 0`) |
| Fuentes gobernadas o documentadas | Sí |
| Diccionario derivado validado | QA_XLSX = APROBADO |
| Word validado estructuralmente | QA_DOCX_ESTRUCTURAL = APROBADO (13 secciones, 17 tablas, sin secciones vacías, sin términos internos ni datos personales) |
| Word validado visualmente | PENDIENTE_REVISION_HUMANA (el entorno no tiene LibreOffice) |
| Originales intactos | Sí (SHA-256 de los 5 archivos v0.9 sin cambios) |
| Commit / push | No / No |

**GATE09 = APROBADO_PARA_CONGELAR_V1.0.** Antes de congelar hay que revisar visualmente el Word y confirmar institucionalmente las resoluciones C09-01 a C09-04.

## Entregables y regeneración

| Archivo | Contenido |
|---|---|
| `resultados/AUDITORIA_GATE09_CONTRADICCIONES_UPLUS_SIES_2026.xlsx` | Registro de 13 contradicciones, cadena de evidencia, cruces, sexo, jornada, código único, historial, país, fuentes y métricas |
| `resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v0.9.1_GATE09.xlsx` | v0.9 más 6 hojas nuevas; columnas en morado agregadas en el Gate 09 |
| `resultados/REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS_v0.9.1_GATE09.docx` | Versión para el proveedor, solo con requerimientos confirmados |
| `resultados/gate09/METRICAS_EVIDENCIA_GATE09.json`, `QA_GATE09.json` | Métricas agregadas (sin datos personales) y QA |

```bash
cd requerimiento_bettersoft_uplus_2026/scripts
python3 gate09_incorporar_fuentes.py
python3 gate09_metricas.py --prom7804 "<ruta a PROMEDIOSDEALUMNOS_7804.xlsx de la carga MU 2026>"
python3 gate09_generar.py
NODE_PATH=../../oferta_academica_2027/node_modules node generar_requerimiento_bettersoft_docx_gate09.js \
  ../resultados/gate09/req_gate09.json ../resultados/REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS_v0.9.1_GATE09.docx
python3 gate09_qa.py
```

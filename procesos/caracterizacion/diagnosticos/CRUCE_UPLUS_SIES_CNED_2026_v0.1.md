# Diagnóstico v0.1 — cruce U+ Bettersoft → SIES / INDICES CNED

Fecha: 2026-09-27. Revisión: **v0.1.1, corrección versionada del conteo de IDs**. Estado: **diagnóstico parcial; cruce histórico oficial no demostrado**. Este archivo contiene solo métricas agregadas y nombres de campos. No incorpora registros de personas. No modifica los libros fuente ni la extracción congelada.

## Objetivo

Evaluar si los datos de extracción U+ disponibles permiten asociar registros y trayectorias con los identificadores y variables de salida homologados en las matrices entregadas. El origen previo del dato dentro de U+ queda fuera de alcance.

## Fuente

| Nivel | Fuente y ubicación | Evidencia / límite |
|---|---|---|
| Salida autorizada SIES | `/Users/alexi/Downloads/SIES_Matriz_Maestra_Variables_VF 1.xlsx`, SHA-256 `46d0e5b42aba69c13c9bee18dc3a12affe0eb87f856d0866470e0bf33b914586` | Hojas `1_Inventario_Procesos`, `2_Inventario_Campos`, `3_Matriz_Maestra`, `10_Claves`, `12_Homologacion`. `3_Matriz_Maestra` contiene 31 filas de conceptos V01–V30 y V31 fuera de secuencia. `2_Inventario_Campos` contiene 573 filas de datos bajo un encabezado (574 filas físicas). |
| Salida autorizada CNED | `/Users/alexi/Downloads/CNED_Matriz_Maestra_Variables  VF.xlsx`, SHA-256 `a51f1928db95261f00ab28ef9ae9bd31659aa12f5a5f92da8b769b24346ed63f` | Hojas `1_Inventario_Secciones`, `3_Matriz_Maestra`, `10_Claves`, `13_Cruce_CNED_SIES`. `3_Matriz_Maestra` contiene 45 conceptos K01–K45, 22 familias X01–X22, una fila vacía y una de leyenda: 69 filas después del encabezado. |
| Entrada U+ real | `.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx`, SHA-256 `b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869` | `Hoja1`: 14.204 filas de datos × 67 columnas. Congelada para la corrida 2026/P2; archivo local restringido, no versionado en Git. Su manifiesto está en `docs/gobernanza/FUENTES_CONGELADAS_2026_P2.txt`. |
| Fuente auxiliar U+ | `.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/PROMEDIOSDEALUMNOS_7804.xlsx` | Disponible, pero no demuestra una equivalencia de códigos de carrera, sede y versión; requiere perfil por asignatura para un análisis AC separado. |
| Histórico SIES, **no U+** | `gobernanza/sies/HISTORICO_SIES_MANIFEST.json` y `EXTRACCION_MATRICULA_SIES _2007_2025/salida/reporte_matricula_ip_san_sebastian.csv` | 2007–2025, 20.961 registros y 83 carreras según manifiesto; nivel declarado `AGREGADO_PROGRAMA_ANIO`. Contiene `codigo_unico`, `cod_sede`, `cod_carrera`, `jornada`, `version`. No es tabla puente a `CODCARPR` ni histórico de cortes U+. |
| Gobierno interno | `README.md`, `MAPA_MAESTRO_CARACTERIZACION.md`, `MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md`, `CONTRATOS_INVARIANTES.md` | Distinguen `RUT` (persona), `CODCLI` (trayectoria), `CODCLI_PERIODO` (trayectoria por período) y registro operativo. Son definiciones técnicas internas, no reglas oficiales de carga. |

## Alcance

Ocho procesos de la hoja SIES `1_Inventario_Procesos` y diecisiete secciones S01–S17 de la hoja CNED `1_Inventario_Secciones`. La matriz CNED proviene del Manual INDICES **2025**; la vigencia de estructuras 2026 no está acreditada por ese libro. Se evalúa la **posibilidad de producir o enlazar** las variables desde esta extracción, no la validez final de un archivo de carga. `Titulados BVP`, posgrado y procesos ajenos a estas matrices quedan fuera del veredicto.

## Metodología

Se verificó el estado Git antes del análisis y se ejecutó `git fetch --all --prune`. Rama activa: `main`; HEAD inicial `7c88d51fbe3a78980119d749cb5d0204ba582323`; `main` estaba un commit adelante y uno atrás de `origin/main`; `caracterizacion.py` ya estaba modificado sin commit. Se leyeron los libros en modo solo lectura y se perfilaron las 14.204 filas de `DATOSDEALUMNOS_10246.xlsx` en memoria. No se imprimieron ni almacenaron identificadores personales. La búsqueda de archivos U+ por nombre identificó esta extracción congelada; no se encontró una serie de extractos U+ con cortes comparables ni una tabla puente validada. Esto es un **límite de evidencia**, no prueba de inexistencia fuera del repositorio.

## Reglas

**HECHO** significa observación directa en fuente. **INFERENCIA** es una relación plausible aún no demostrada. **HIPÓTESIS** es una explicación por contrastar. **RECOMENDACIÓN** es acción propuesta. **DECISIÓN** es un criterio adoptado para este diagnóstico; no altera una regla oficial.

La escala de `13_Cruce_CNED_SIES` se aplica como: **A** correspondencia exacta de campo y significado; **B** semejanza semántica inferida; **C** exige catálogo/tabla de conversión; **D** derivable con transformación y entradas suficientes; **F** parecido engañoso o no equivalente; **Sin equivalente identificado** cuando la matriz no contiene concepto aplicable. **C/D no acreditan que la conversión o derivación pueda ejecutarse hoy.** Ninguna clave candidata de las hojas `10_Claves` se promueve a llave primaria real.

## Resultados

### Perfil de la entrada U+

**HECHO.** `DATOSDEALUMNOS_10246.xlsx` tiene 14.204 filas, 67 columnas. `ANOMATRICULA` abarca 2013–2026 (14 años) y `PERIODOMATRICULA` toma 1, 2 y 3. Son **años contenidos en un archivo congelado para 2026/P2**; no demuestran snapshots históricos independientes. La fecha de extracción está en el manifiesto, no en cada fila.

| Campo | No nulos | Distintos | Diagnóstico |
|---|---:|---:|---|
| `CODCLI` | 14.204 | 14.203 | Una clave aparece dos veces; tampoco es única con `ANOMATRICULA` y `PERIODOMATRICULA` (un grupo de dos). No hay filas completamente idénticas. |
| `CODCARPR` | 14.204 | 110 | Código interno de programa. `CODIGOCARRERA` tiene los mismos 110 valores y correspondencia 1:1 **en esta extracción**. No demuestra equivalencia oficial ni estabilidad histórica. |
| `RUT` | 14.204 | 12.171 | 1.728 valores aparecen más de una vez (3.761 filas). En este archivo todos tienen guion y ninguno puntos; eso no prueba formato uniforme en otros períodos o fuentes. |
| `SEDE` | 14.204 | 2 | Códigos U+ `RE`, `CO`. Falta tabla certificada hacia SIES `S` y CNED `idSede`. |
| `JORNADA` | 14.204 | 3 | `D`, `V`, `O`. Falta homologación temporal a `J` oficial. |
| `ANOMATRICULA` / `PERIODOMATRICULA` | 14.204 / 14.204 | 14 / 3 | Indican período de fila; no sustituyen fecha de corte ni prueban estado histórico a la fecha requerida. |
| `ANOINGRESO` / `PERIODOINGRESO` | 14.204 / 14.204 | 27 / 3 | `PERIODOINGRESO=3` aparece 341 veces; significado no documentado aquí. |
| `FECHAMATRICULA` | 14.204 | 2.332 | Todo llega como texto; falta confirmar a qué matrícula/renovación corresponde. |
| `MODALIDAD` | 9.857 | 2 | Valores `CIENTIFICO-HUMANISTA` y `TÉCNICO-PROFESIONAL`: **modalidad de enseñanza media**, no modalidad del programa SIES/CNED. 4.347 vacíos. |
| `NOMBREUNIVERSIDAD` / `CARRERARANTERIOR` | 1.360 / 1.450 | — | Cobertura parcial; nombre libre no es identificador de programa. |

Los tipos observados son mixtos: años y nivel como enteros; `CODCLI`, `CODCARPR`, `RUT`, sedes, jornadas y fechas como texto. En el universo existen 12.264 filas con período de matrícula 1, 1.595 con 2 y 345 con 3. Estos son conteos de la extracción, no cifras normativas ni universo oficial de un proceso.

### Correspondencia campo por campo (67 columnas U+)

Referencia común de IDs: **V** = SIES hoja `3_Matriz_Maestra`; **K** = CNED hoja `3_Matriz_Maestra`. Las justificaciones de cruce entre reguladores están en CNED hoja `13_Cruce_CNED_SIES`. Cada fila es una **propuesta diagnóstica**, no una correspondencia aprobada. `—` significa que no se identificó ID conceptual en esas hojas.

| Campo fuente U+ | ID SIES | ID CNED | Clase | Evidencia y condición |
|---|---|---|---|---|
| Número | — | — | Sin equivalente identificado | Secuencia de exportación, no identificador oficial. |
| CODCLI | — | — | Sin equivalente identificado | Llave interna de trayectoria; útil para enlazar antes de convertir. |
| CODCARPR | V12 | K09 | C | Código interno; requiere puente a carrera oficial y vigencia. |
| NOMBRE_L | V13 | K10 | B | Nombre del programa; no sirve como llave única. |
| ANOMATRICULA | — | K25 | B | Año de matrícula frente a año de proceso; validar regla temporal. |
| PERIODOMATRICULA | — | — | Sin equivalente identificado | Campo temporal U+; valor 3 sin definición. |
| ANOINGRESO | V22 | — | D | Componente año; semestralidad exige `PERIODOINGRESO` homologado. |
| PERIODOINGRESO | V22 | — | C | Semestre de ingreso solo tras catalogar valores U+. |
| FECHAMATRICULA | V27 | — | B | Fecha disponible; semántica histórica por confirmar. |
| JORNADA | V15 | K15 | C | Código U+ a jornada SIES / horario CNED. |
| RUT | V02, V03 | K21 | D | Separar cuerpo/DV, validar tipo documental y formato; RUT no sustituye `CODCLI`. |
| NOMBRE | V06 | K22 | B | Nombre completo; K22 trata personas de otras entidades, no se usa sin rol. |
| SEXO | V07 | K23 | C | Dominio U+ debe compararse con dominio por reporte. |
| ESTADOCIVIL | — | — | Sin equivalente identificado | No figura como concepto V/K de estas matrices. |
| FECHANACIMIENTO | V08 | — | B | Mismo concepto; validar formato y proceso. |
| DIRECCIONPROCEDENCIA | — | — | Sin equivalente identificado | Domicilio personal no equivale a dirección institucional K19. |
| CIUDADPROCEDENCIA | — | — | Sin equivalente identificado | No equivale a ubicación de sede. |
| COMUNAPROCEDENCIA | V30 | — | B | Comuna de persona; verificar entidad antes de usar V30. |
| FONOPROCEDENCIA | — | — | Sin equivalente identificado | No existe concepto V/K aplicable. |
| DIRECCIONACTUAL | — | — | Sin equivalente identificado | No equivale a dirección institucional K19. |
| CIUDADACTUAL | — | — | Sin equivalente identificado | No equivale a sede. |
| COMUNAACTUAL | V30 | — | B | Comuna de persona; V30 reúne comunas de entidades distintas. |
| FONOACTUAL | — | — | Sin equivalente identificado | Sin concepto V/K aplicable. |
| MAIL | — | — | Sin equivalente identificado | Sin concepto V/K aplicable. |
| Mail_Inst | — | — | Sin equivalente identificado | Correo institucional de alumno, no de sede. |
| NACIONALIDAD | V09 | — | C | Texto U+ a dominio de nacionalidad/país requerido. |
| EMERGENCIA | — | — | Sin equivalente identificado | Contacto de emergencia fuera de matrices. |
| FONOEMERGENCIA | — | — | Sin equivalente identificado | Fuera de matrices. |
| CODIGOCOLEGIO | — | — | Sin equivalente identificado | Código de establecimiento secundario, sin ID V/K aplicable. |
| COLEGIO | — | — | Sin equivalente identificado | Nombre de establecimiento secundario, no programa superior. |
| MODALIDAD | V14 | — | F | Falso amigo: enseñanza media, no modalidad de programa. |
| DESCRIPCION | — | — | Sin equivalente identificado | Describe establecimiento escolar; validar semántica antes de reutilizar. |
| CIUDADCOLEGIO | — | — | Sin equivalente identificado | No es sede de educación superior. |
| COMUNACOLEGIO | V30 | — | B | Comuna escolar; V30 solo podría aplicar si el proceso pide esa entidad. |
| CATEGORIA | — | — | Sin equivalente identificado | Categoría U+ sin equivalencia V/K demostrada. |
| VIASDEADMISION | — | K39 | C | Vía de ingreso U+; requiere catálogo y regla por proceso. |
| MOTIVODESELECCION | — | — | Sin equivalente identificado | Sin concepto V/K aplicable. |
| MEDIOSDEINFORMACION | — | — | Sin equivalente identificado | Sin concepto V/K aplicable. |
| VIACONSULTA | — | — | Sin equivalente identificado | Sin concepto V/K aplicable. |
| NOMBREUNIVERSIDAD | — | — | Sin equivalente identificado | Nombre libre de origen, no ID de institución/programa. |
| CARRERARANTERIOR | — | — | Sin equivalente identificado | Texto libre de trayectoria previa, no código oficial. |
| RUTRESPONSABLEFINANCIERO | — | — | Sin equivalente identificado | RUT de tercero; no equivale a K21 del estudiante. |
| NOMBRERESPONSABLEFINANCIERO | — | — | Sin equivalente identificado | Nombre de tercero, no persona reportada. |
| CODIGOCARRERA | V12 | K09 | C | Coincide 1:1 con CODCARPR en esta extracción; puente oficial pendiente. |
| EMPRESA | — | — | Sin equivalente identificado | Dato laboral personal. |
| ACTIVIDAD | — | — | Sin equivalente identificado | Dato laboral personal. |
| DIRECCION_EMPRESA | — | — | Sin equivalente identificado | No equivale a K19 institucional. |
| CIUDAD_EMPRESA | — | — | Sin equivalente identificado | No equivale a sede. |
| COMUNA_EMPRESA | — | — | Sin equivalente identificado | No equivale a comuna institucional K18. |
| CANTIDADDEHIJOS | — | — | Sin equivalente identificado | Sin concepto V/K aplicable. |
| TRAMODERENTA | — | — | Sin equivalente identificado | No equivale a arancel ni ayudas K38. |
| NOMBREEMPRESA | — | — | Sin equivalente identificado | Dato laboral personal. |
| ANOEGRESOENSENANZAMEDIA | V25 | — | F | Egreso de enseñanza media, no egreso de carrera superior. |
| NOTAENSENANZAMEDIA | — | — | Sin equivalente identificado | No equiparar automáticamente a indicadores de ingreso. |
| RUT EJECUTIVO | — | — | Sin equivalente identificado | Identifica a un tercero, no estudiante. |
| NOMBRE EJECUTIVO | — | — | Sin equivalente identificado | Identifica a un tercero. |
| ESTADOACADEMICO | V24 | K16 | C | Estados con significado distinto: matrícula, programa y control de carga. No hay equivalencia automática. |
| SITUACION | V24 | — | C | Situación U+ frente a vigencia de registro; requiere regla por proceso y corte. |
| MATRICULA | — | — | Sin equivalente identificado | Código 1/2 U+ sin significado documentado; no inferir vigencia. |
| NIVEL | V20 | K11 | C | Nivel académico del estudiante U+ no es directamente nivel/tipo de programa. |
| ARANCELREAL | V31 | K38 | F | Arancel real individual no es valor de oferta ni valor oficial de matrícula. |
| CON_FIRMA | — | — | Sin equivalente identificado | Marca contractual interna. |
| FECHAFIRMA | — | — | Sin equivalente identificado | Fecha contractual, no fecha de matrícula sin regla. |
| SEDE | V11 | K02 | C | Código RE/CO exige puentes SIES y CNED, vigentes en el tiempo. |
| NOMBRES | V06 | K22 | B | Para V06 es coincidencia nominal; K22 requiere comprobar rol/entidad. |
| APELLIDO PATERNO | V04 | — | B | Primer apellido; confirmar reglas de normalización por proceso. |
| APELLIDO MATERNO | V05 | — | B | Segundo apellido; 18 nulos observados. |

**Validación pendiente de la tabla:** para V30, K22, K11 y V20 la matriz agrupa conceptos que pueden pertenecer a entidades diferentes. La relación sugerida **no autoriza carga**. En CNED `K09` es código interno de programa; no se equipara a `K07` (`Codcarr`) ni `K08` (`CodigoSIES`). Las variables no listadas en la tabla no tienen campo fuente identificado en esta extracción.

### Reconstrucción de identificadores

| Componente oficial | Evidencia U+ | Condición que falta |
|---|---|---|
| `I` institución SIES | Extracción de una institución, pero sin columna de código IES | Código institucional aprobado por fuente oficial; constante gobernada por proceso, no deducida del RUT ni del nombre. |
| `S` sede SIES | `SEDE` = RE/CO | Puente `SEDE_UPLUS → COD_SEDE_SIES`, con vigencia. |
| `C` carrera SIES | `CODCARPR` / `CODIGOCARRERA` | Puente por programa y período a `COD_CARRERA`; no se demuestra relación con el `cod_carrera` del agregado histórico SIES. |
| `J` jornada SIES | `JORNADA` = D/V/O | Catálogo/versiones; `O` no tiene interpretación oficial demostrada. |
| `V` versión SIES | **Ausente** de las 67 columnas | Maestro de Oferta Académica aceptada por SIES con versión y vigencia; el año de matrícula no reemplaza V. |

**INFERENCIA condicionada:** una clave de búsqueda `CODCARPR + SEDE + JORNADA + fecha/período de vigencia`, asociada al maestro oficial de oferta, podría devolver `CODIGO_UNICO`. Debe probar unicidad por intervalo y manejo de cambios de versión, sede, jornada y carrera. No corresponde construir el concatenado usando códigos U+ sin ese maestro. `CODCLI` enlazaría la trayectoria de la persona a la fila del programa, tras resolver la fila duplicada y la semántica de períodos. `RUT` solo apoya el cruce de persona; sus 1.728 valores repetidos muestran que no identifica una única matrícula.

Para CNED se necesitan además `SEDE_UPLUS → idSede`, `CODCARPR`/programa → `Codcarr`, y una definición verificable de qué representa `CodigoSIES` en S14. La hoja CNED `10_Claves` y el cruce `13_Cruce_CNED_SIES` los clasifican como candidatos o categoría **C**. No hay una fórmula demostrada `CODIGO_UNICO → Codcarr` ni una equivalencia `idSede = S`.

### Factibilidad por proceso y período

`Parcial` significa que hay entradas útiles para un **prototipo de cruce**, no que el reporte esté listo para envío.

| Proceso / referencia de matriz | Evidencia actual | Veredicto de cruce oficial hoy | Condición mínima |
|---|---|---|---|
| SIES Titulados y Egresados, 01-03-2025 a 28-02-2026 | `RUT`, programa interno, `ESTADOACADEMICO`; no fecha oficial de obtención de título/egreso validada | **No confiable** | Fechas y estados de titulación/egreso, puente de carrera y corte correcto. |
| SIES Matrícula Pregrado 2026, corte 30-04-2026 | Año/período y matrícula U+; no estado histórico demostrado al corte | **Parcial, no certificable** | Oferta aceptada I·S·C·J·V, estado al corte, catálogo de períodos y duplicado resuelto. |
| SIES Personal Académico 2026 | Esta tabla es de estudiantes | **No posible desde esta entrada** | Fuente de personal y reglas del instructivo. |
| SIES Matrícula Extranjeros 2025, 01-01 a 31-12-2025 | Nacionalidad y matrículas por período; sin prueba de actividad completa ni país/residencia oficiales | **Parcial, no certificable** | Universo anual, nacionalidad validada, variables de residencia/origen y puente de programa. |
| SIES Avance Curricular 2025 | Extracto auxiliar `PROMEDIOSDEALUMNOS` disponible, sin enlace a plan SIES demostrado aquí | **Parcial, no certificable** | Vincular asignaturas/unidades a `CODCLI`, plan, período y código único vigente; aplicar reglas anual/acumulado. |
| SIES Infraestructura y Recursos Educacionales 2026, corte 30-06-2026 | Entrada de estudiantes, sin inventario de inmuebles | **No posible desde esta entrada** | Fuente de infraestructura por entidad y corte. |
| SIES Oferta Académica Acceso CFT/IP 2027 | `NOMBRE_L`, códigos internos, sede, jornada; sin versión/maestro oficial completo | **Parcial, no certificable** | Maestro de programas y oferta 2027 aceptada, atributos y etapas. |
| SIES Oferta Académica 2027 Final | `ARANCELREAL` individual, no arancel oficial de programa | **No confiable** | Valores oficiales de oferta y su vigencia; no usar arancel individual. |

| Sección INDICES CNED (manual 2025) | Veredicto desde `DATOSDEALUMNOS` | Condición |
|---|---|---|
| S01 Identificación y Casa Central | No confiable | Maestro institucional. |
| S02 Junta Directiva | No posible | Fuente de autoridades. |
| S03 Ayudas Estudiantiles | No posible | Fuente de ayudas/beneficios. |
| S04 Investigación | No posible | Fuente de proyectos y resultados. |
| S05 Sede | Parcial, no certificable | Maestro de sedes e `idSede` CNED. |
| S06 Campus | No posible | Maestro de campus. |
| S07 Dependencias | No posible | Fuente de dependencias. |
| S08 Docentes | No posible | Fuente de personal académico. |
| S09 Origen Estudiantes | Parcial, no certificable | Definir universo, procedencia, clasificación y corte. |
| S10 Inmueble | No posible | Inventario de inmuebles. |
| S11 Biblioteca | No posible | Fuente bibliotecaria. |
| S12 Laboratorios y Talleres | No posible | Inventario de espacios/equipos. |
| S13 Nuevos Programas | Parcial, no certificable | Maestro de programas CNED/SIES y vigencia. |
| S14 Evolución de Programas | Parcial, no certificable | Puente `Codcarr`, `CodigoSIES`, `idSede`, año y reglas de agregado. |
| S15 Egresados y Titulados | No confiable | Fechas oficiales, universo enero–diciembre y puente CNED. |
| S16 Administración | No posible | Datos de usuarios/roles del portal, no de estudiantes. |
| S17 Malla Curricular | Parcial con `PROMEDIOSDEALUMNOS`, no certificable | Código de programa CNED, versión de malla y detalle curricular validado. |

Las secciones CNED se reportan con el período del **manual 2025**; no se les asigna un período 2026 no verificado. La hoja CNED `13_Cruce_CNED_SIES` observa expresamente diferencias de corte para S15 y S08. Ningún `Parcial` equivale a un mapeo A de registros.

## Validaciones

- 14.204 filas leídas de `Hoja1`; 67 encabezados; ninguna fila exactamente duplicada. Un `CODCLI` repetido dos veces también repite `CODCLI + ANOMATRICULA + PERIODOMATRICULA`.
- `CODCARPR` y `CODIGOCARRERA`: 110 valores cada uno y relación 1:1 en **este archivo**. No se considera tabla puente a códigos oficiales.
- Los 14 años de `ANOMATRICULA` y los tres códigos de período se observaron en filas. No se certificó integridad longitudinal ni ausencia de rectificaciones.
- Las hojas `10_Claves` de ambos libros describen identificadores **candidatos**. Se respetaron como tales.
- La hoja CNED `13_Cruce_CNED_SIES` tiene 16 C, 10 B, 4 D, 1 F y 2 «Sin equivalente identificado» (33 relaciones). Esta escala se usó sin convertir B/C/D en equivalencia aprobada.
- Las rutas y hashes identifican las entradas usadas. La extracción U+ está fuera del historial Git por su contenido personal; el informe no contiene valores de RUT, CODCLI, nombres, fechas individuales ni casos reconocibles.

## Hallazgos

1. **HECHO:** el componente V de `CODIGO_UNICO` no está en la extracción U+. Falta un maestro de oferta por vigencia; `CODCARPR` no lo determina.
2. **HECHO:** no hay tabla puente verificada U+→SIES/CNED en el material localizado. El agregado SIES histórico no contiene `CODCARPR` para probarla.
3. **HECHO:** la extracción U+ es una foto congelada de 2026/P2 con filas de 2013–2026. **INFERENCIA:** permite exploración longitudinal preliminar; no demuestra estados en todos los cortes anteriores.
4. **HECHO:** `MODALIDAD` U+ describe enseñanza media. Asociarla a V14 o modalidad de CNED sería error directo.
5. **CORRECCIÓN VERSIONADA (2026-09-27):** la nota anterior de «IDs ausentes» confundía filas físicas con identificadores conceptuales. SIES tiene 31 conceptos (V01–V30 y V31 fuera de secuencia), sin V32. CNED tiene 67 conceptos/familias (K01–K45 y X01–X22), más una fila vacía y una de leyenda; las 69 filas posteriores al encabezado no implican K46–K69. El conteo queda aclarado; no requiere validación con terceros.

## Riesgos

- Muchos a muchos entre persona, trayectoria, programa, sede, jornada, versión y período si se intenta unir solo por `RUT` o por `CODCARPR`.
- Asignación errónea de código único por reutilización/cambio histórico de código interno o por tomar el estado actual para un corte pasado.
- Falsos equivalentes (`MODALIDAD` escolar, `ARANCELREAL` individual, año de egreso de enseñanza media, estado U+ frente a vigencia de carga).
- La matriz de salida contiene relaciones conceptuales, pero no garantiza llave de carga ni regla de transformación por proceso.
- La evidencia de INDICES 2025 no acredita estructura vigente para 2026.

## Decisiones

- **DECISIÓN de diagnóstico:** no se publica ninguna correspondencia como llave oficial ni se declara un archivo «listo para carga».
- **DECISIÓN de diagnóstico:** se toma la extracción U+ tal cual, sin analizar cómo se originó el dato antes de Bettersoft.
- **DECISIÓN de diagnóstico:** se documentan los datos personales solo de forma agregada; no se agrega el libro restringido a Git.
- **RECOMENDACIÓN:** construir y validar un puente con `CODCARPR`, `SEDE`, `JORNADA`, identificadores oficiales SIES/CNED y fechas de vigencia; registrar fuente, versión y responsable de cada equivalencia.

## Estado

**Diagnóstico de factibilidad parcial.** Hay campos que permiten diseñar el cruce y detectar excepciones. No existe evidencia suficiente para afirmar que el cruce U+↔SIES↔CNED sea confiable por persona/programa/período ni para certificar retrospectivamente cortes. El repositorio tenía una modificación previa en `caracterizacion.py` y ramas divergentes; este diagnóstico no altera esos elementos. El archivo Markdown queda como versión local v0.1 para revisión; no representa aprobación funcional ni commit de Git.

## Próximo paso

1. Localizar/solicitar el maestro institucional de oferta aceptada por SIES y el catálogo CNED, con vigencias y equivalencias a `CODCARPR`, `SEDE`, `JORNADA` y versión. Confirmar la interpretación de `CodigoSIES` CNED.
2. Verificar cortes históricos U+ independientes, resolver el `CODCLI` duplicado y documentar `PERIODOMATRICULA=3`, `PERIODOINGRESO=3` y la semántica de `FECHAMATRICULA`.
3. Probar el puente sobre una muestra controlada **fuera de Git**, midiendo cobertura, unicidad y conflictos por año/período antes de ampliar a los procesos.

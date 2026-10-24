# Unificación de procesos y reglas de negocio

Decisión del usuario, 2026-10-15: un solo repositorio, con ambos procesos
separados en módulos. Este contrato precede a la incorporación de Caracterización.

## Alcance y preservación

`avance_curricular` es el repositorio contenedor. Su módulo existente conserva
ubicaciones, comandos y referencias congeladas. Caracterización se incorpora en
`procesos/caracterizacion/`, manteniendo su estructura interna y sus comandos.
No se mueve ni elimina el repositorio de origen. Se conserva una instantánea
de sus archivos versionados y no ignorados, incluidos cambios de trabajo, con
inventario de huellas, estado Git y commit de procedencia. No se copian `.git`,
entornos, cachés ni archivos locales ignorados; se identifica esta limitación.
No se mezclan historias Git ni se publica en remoto en esta intervención.

La incorporación no puede ocultar cambios concurrentes: se comprueban huellas
de origen antes y después. Las modificaciones de integración se registran
separadamente de la instantánea. El original queda disponible para reversión.
No se ejecutan pipelines reales de matrícula, caracterización ni cargas PES.

## Fuente común

Se elimina la dependencia operativa entre dos repositorios para los catálogos
anual 2026, anual 2027 e histórico H7: el módulo integrado consulta recursos
dentro del mismo repositorio contenedor, con hashes y año explícitos. Los paquetes
históricos copiados se mantienen como evidencia, no como fuentes activas editables.
El contrato H7 y las políticas anuales mantienen sus resultados; centralizar
rutas no autoriza promover candidatos a equivalencias ni cambiar elegibilidad.

Los adaptadores y el enrutamiento viven en `common/` y `scripts/`, siguiendo el
layout existente. La estructura nueva queda registrada en `PROYECTO_IPSS.json`.

## Reglas comprobadas

1. Regla interna indicada por Alexi: inicio para este diccionario = mínimo año
   de oferta del **Código Único completo**, sin filtro de matrícula, quórum o
   vigencia actual. El campo formal Año Inicio de la carga se conserva separado.
   La cobertura del archivo no se inventa: 2007–2009 siguen sin oferta disponible.
2. Regular y continuidad son programas distintos. Su primer año se calcula por
   cada código, aunque compartan nombre o componente C. Logística J4: V1=2024,
   V2=2025 en las fuentes de oferta disponibles.
3. Manual Oferta-Acceso 2027, Anexo 5, páginas 65–66: cambian ISCJV institución,
   sede registrada, jornada o nombre significativo; cambia V cuando cambia
   modalidad, duración de estudios/total, tipo de plan o nivel del programa.
4. El mismo Anexo permite cambios curriculares que no alteren los atributos
   protegidos sin cambiar código. Por ello versión SIES y malla UMAS no son una
   relación obligatoriamente uno a uno. Nombres sujetos a evaluación ministerial
   no se resuelven por semejanza automática.
5. Manual 2027 páginas 18–19/24 y manual Oferta 2026 páginas 15–17: Régimen y
   Duración del Régimen son editables en oferta vigente. Duraciones de estudios,
   titulación y total tienen unidad semestres; duración del régimen utiliza la
   unidad del régimen. No se infiere cambio de código por pasar solo de
   representación semestral a trimestral manteniendo las duraciones formales.
6. El reporte validado 5910 de 2027 y la oferta histórica 2026 comparten 103
   códigos: 34 cambian régimen 1→2 manteniendo Código Único y duraciones de
   estudios/total. Hay pares 8→12, 4→6 y 5→7 de duración del régimen. Son valores
   declarados: no se deduce una fórmula universal ni redondeo a partir de ellos.
7. I162S2C35J4V1 cambia duración de estudios 5→6 entre 2018 y 2019, manteniendo
   código. No está acreditada la causa. El manual 2027 no justifica retroactivamente
   ese cambio ni permite declararlo error en 2019 sin normativa/rectificación de
   esa edición. Se conserva como incidencia histórica pendiente de evidencia.

## Registro común de reglas

Cada regla registra ID, clase (interna, formal o transformación), proceso,
año/edición, fuente y página, entrada, salida, estado de acreditación y consumidores.
Una transformación debe conservar dato/unidad originales, dato/unidad de destino
y regla de conversión/precisión. Una definición interna no reemplaza una formal.

Retención, titulación oportuna y estados de estudiante se incorporan al inventario
de reglas y consumidores existentes. Esta intervención no inventa ni sustituye
sus fórmulas: necesitan universos, cohortes, fechas, exclusiones y fuentes de sus
respectivos procesos. La vigencia de un programa SIES no es estado académico UMAS.

## Validación exigida

- Inventario completo de archivos incorporados y diferencias justificadas.
- 51 referencias congeladas FCU2026 y referencias MU2026 intactas.
- Paridad de 1.349 consultas UMAS y 767 consultas SIES en la integración histórica.
- Pruebas de catálogo anual 2027, enriquecimiento anual 2026 y comandos de módulo.
- Rechazo de integridad alterada, rutas fuera del repositorio y año incorrecto.
- Prueba de inicio por código con regular/continuidad, sin matrícula, vacío y
  cobertura limitada; la regla no utiliza Año Inicio declarado ni el año de UMAS.
- Sin regeneración de entregas reales ni cambios al Excel del usuario.

## Resultado de la integración

Especificación registrada antes de la implementación; comprobaciones cerradas
el 2026-10-15. La integración de código y recursos SIES está preparada en el árbol
de trabajo del repositorio contenedor, sin commit ni publicación remota.

- Se incorporaron 811 archivos, 133.060.650 bytes. Los 806 archivos sin adaptación
  conservan sus bytes; cinco tienen cambios de integración declarados. El origen
  conserva su commit, archivos y cambios de trabajo. No hay `.git` anidado.
- Las consultas históricas usan una implementación común y los catálogos anuales
  2026/2027 se resuelven dentro del contenedor. Una prueba desde una copia aislada
  comprueba la portabilidad de las consultas histórica y anual 2027.
- Las 1.349 consultas UMAS y 767 SIES devuelven exactamente los mismos resultados.
  Las 51 referencias FCU2026 y las 137 referencias del contenedor registradas al
  cierre H7 conservan sus hashes. El Excel editado por Alexi permanece intacto.
- Pasaron 80 pruebas: 5 de inicio, 18 de integración histórica, 8 de catálogo
  2027, 16 de enriquecimiento anual, 30 de comandos operativos y 3 de unificación.
  No se ejecutaron pipelines reales ni se regeneraron entregas operativas.
- El CSV nacional se conserva completo mediante compresión reversible: 395.719
  registros, 69 columnas; la descompresión reproduce el SHA-256 original. Los
  manuales 2026 y 2027 conservan sus PDF y la extracción de las 129 páginas.
- Se registraron 14 reglas iniciales con autoridad, edición y estado. Retención,
  titulación oportuna, estados académicos y conversión de duraciones aún requieren
  completar la auditoría de sus contratos; inventariarlas no equivale a validarlas.
- La regla de inicio localiza oferta para 139 de los 141 códigos del maestro.
  Ocho ya aparecen en el límite inferior de la fuente (2010); no se acredita con
  ella ausencia anterior. Los dos códigos sin oferta mantienen inicio vacío.
  La cobertura 2007–2009 sigue pendiente. No se certificaron nuevas equivalencias.

La integración no incorpora fuentes ignoradas o externas de todos los procesos
de Caracterización ni recupera automáticamente objetos LFS. Por ello, la
validación de consultas y comandos no acredita todavía una ejecución integral
de cada pipeline desde una máquina nueva. La historia Git del origen permanece
en el repositorio original, que se conserva como respaldo.

Evidencias y puntos de entrada:

- [Registro del proyecto](../PROYECTO_IPSS.json).
- [Módulo Caracterización](../procesos/caracterizacion/README_INTEGRACION.md).
- [Inventario de incorporación](../data/unificacion_proyectos/20261015/importacion.json).
- [Paridad y controles de integración](../data/unificacion_proyectos/20261015/qa_integracion.json).
- [Preservación final de origen, referencias y Excel](../data/unificacion_proyectos/20261015/control_preservacion_final.json).
- [Fuentes completas y hashes](../data/reglas_negocio/20261015/fuentes.json).
- [Registro de reglas](../data/reglas_negocio/20261015/reglas.json).
- [Inicio por código](../data/reglas_negocio/20261015/inicios_por_codigo.json).
- [Cambios de régimen con el mismo código](../data/reglas_negocio/20261015/comparacion_regimen_2026_2027.json).

Comando de consulta de módulos, sin ejecutar procesos:

```sh
python3 scripts/proceso_ipss.py --listar
```

## Tres fases para completar las equivalencias

Estas fases complementan H1–H8. Preservan el maestro y la agrupación existente;
la integración del repositorio es la base común, no una acreditación de mallas.

| Fase | Hitos | Criterio de cierre |
|---|---|---|
| A. Fuentes, identidad y reglas | A1: fuentes completas y procedencia; A2: primera oferta por Código Único y programas regular/continuidad separados; A3: reglas por manual, proceso y edición, con incidencias históricas | A1–A2 ejecutados para la cobertura disponible. A3 conserva pendientes explícitos, especialmente 2007–2009 y el cambio 2019 de I162S2C35J4V1. Cada atributo usado para decidir debe tener definición y unidad. |
| B. Equivalencias históricas reproducibles | B1: gobernar correspondencias de sede, jornada, modalidad, tipo de plan y nivel; B2: resolver unidades/duraciones y vigencias del plan UMAS; B3: contrastar con oferta anual y MRUN, acreditando cada relación | Cada vínculo debe identificar Código Único, CODCARPR, CODPESTUD, contexto temporal, regla y evidencia. Se permiten varias mallas UMAS para un código SIES cuando corresponda; ninguna asignación por ordinal V o año del nombre del plan. Ambigüedades permanecen explícitas. |
| C. Diccionario y consumo común | C1: publicar una nueva edición preservando los sectores editados; C2: actualizar ambos módulos al contrato compartido; C3: comprobar ejemplos, integridad y reversión | Mismos parámetros producen la misma respuesta en ambos procesos. Ninguna doble asignación incompatible en un mismo contexto; los no resueltos conservan causa y evidencia faltante. No sobrescribir el Excel actual hasta producir y verificar la nueva edición. |

La evaluación técnica de la fase B está implementada y reproducida; ver
[resultados y brechas pendientes](resultados_fase_b_equivalencias_historicas.md).
No se acreditaron equivalencias nuevas y la fase C no ha regenerado el diccionario. La primera
oferta ordena la historia SIES; el enlace con cada malla UMAS exige las demás
condiciones y evidencia, porque el manual admite cambios curriculares sin nuevo
Código Único.

# Fase 8 — Excel definitivo y control de cambios

Autorización: «procede con la fase 8», 2026-10-15. Especificación anterior
a la autoría. Se reemplaza el diccionario independiente solicitado, conservando
un respaldo idéntico del anterior. No se modifica Matrícula Unificada ni motores.

## Contrato del libro

Destinatarios: personas que consultan y auditan el cruce académico IPSS.
Excel contiene solo dimensiones, reglas, candidatos, ejemplos y procedencia;
no registros personales. Conserva 141 códigos, 236 planes y 513 candidatos,
incluyendo programas sin actividad u oferta actual. Historia SIES mantiene
las 767 claves anuales observadas, sin inventar cobertura 2007–2009.

Consulta SIES: año y Código Único exactos, nombre anual y nombre oficial 2026
separados, componentes, jornada, modalidad y estado de oferta. Los nombres
de 2026 son los literales del maestro contrastado con la oferta indicada.

Consulta UMAS: ocho parámetros (año, período, régimen, código interno, nombre
interno, plan, sede, jornada). No permite digitar una versión para acreditar
el resultado. La edición H5 tiene cero reglas efectivas: el código acreditado
queda vacío; una coincidencia única o múltiple solo identifica candidatos.
La tabla auxiliar agrupa candidatos por contexto y nombre exactos. Período y
régimen son obligatorios para la consulta, pero no acreditan por sí mismos
la vigencia de una candidatura. Se hacen visibles la clave completa y el ámbito
2026 de los candidatos; no se extrapolan a años anteriores.

Excel usa coincidencia sensible a mayúsculas y espacios internos. Se exige
entrada literal sin espacios periféricos; no usar TRIM de Excel, que modifica
espacios internos. No se transforma jornada, sede ni modalidad escolar.
Los valores NULL/NONE/NAN se consideran faltantes. La consulta de oferta
es independiente de la acreditación curricular y de asignación individual.

Sector IPSS se incluye como referencia separada de 2026, solo para las 61
claves del catálogo sectorial ya verificado. Las otras permanecen pendientes,
sin deducir sector por semejanza de nombres ni extenderlo históricamente.
La ampliación sectorial requiere evidencia adicional y no selecciona versión.

## Estructura y fuentes

Consulta es la entrada principal. Diccionario resume un registro por código;
Historia SIES preserva las observaciones anuales; Planes UMAS conserva todo el
inventario; Programas UMAS preserva las 257 relaciones del catálogo operativo,
incluso sin plan asociado; Candidatos expone cada relación de plan H5; Claves UMAS agrupa relaciones
sin escoger destino; Ejemplos presenta casos H6 sin identidad. Guía documenta
las uniones, estados, fuentes, límites y actualización. Tablas nativas con
filtros, identificadores como texto y paneles congelados.

La preparación recibe snapshots H5/H6/H7 fijados por hash, no busca versiones
recientes de reportes personales. La autoría usa Artifact Tool del runtime
bundled y un único generador JS. Cálculos mediante fórmulas acotadas; sin macros
ni vínculos externos. Se conservan el preparador y las reglas de generación.

## Validación y entrega

Comprobar cada tabla exportada contra su proyección, cobertura y unicidad,
los 124 nombres oficiales 2026, 61 sectores respaldados, nombres históricos,
componentes separados, códigos sin actividad y candidatos pendientes.
Probar búsquedas únicas/múltiples, historia sin oferta, entradas incompletas,
nombre distinto, jornada distinta, años fuera de ámbito y colisiones de clave.
Comparar fórmulas con los resultados H7 para casos generales y fronteras.
Inspeccionar cachés y errores, renderizar todas las hojas y revisar el XLSX.
El recálculo nativo de Excel se distingue de la validación en Artifact Tool.

Conservar el anterior por SHA-256 antes de instalar el nuevo archivo. Entrega:
`DICCIONARIO_CRUCE_SIES_UMAS_2007_2026.xlsx` en la carpeta OneDrive 2026
indicada por el usuario. Registrar hash, respaldo, fuentes, controles y cambios
en `data/versiones_historicas_sies_umas/fase_8_20261015/`. H8 completa la
entrega del diccionario; no certifica las versiones pendientes de evidencia.

## Reproducción

Python prepara exclusivamente dimensiones académicas y coteja las fuentes
fijadas; Node genera el libro con el runtime bundled de Artifact Tool.
Enlazar `node_modules` en la carpeta temporal, nunca en las dependencias del
repositorio. Copiar allí el generador MJS antes de ejecutar:

```bash
python3 scripts/preparar_excel_historico_h8.py --salida /ruta/trabajo/libro.json
node /ruta/trabajo/generar_excel_historico_h8.mjs /ruta/trabajo/libro.json /ruta/trabajo/diccionario.xlsx /ruta/trabajo/vistas
python3 scripts/verificar_excel_historico_h8.py --libro /ruta/trabajo/diccionario.xlsx --datos /ruta/trabajo/libro.json --salida /ruta/trabajo/qa_xlsx.json
```

La instalación sobre el nombre solicitado se realiza solo después de verificar
la candidata, conservar el original y comprobar que su hash no cambió. Los
comandos de reproducción deben apuntar a un destino de trabajo distinto del
archivo entregado. No basta generar un XLSX para promoverlo.

Las fórmulas utilizan coincidencias EXACT por fila y controles de unicidad.
No se usa una comparación matricial EXACT dentro de SUMPRODUCT porque el
motor de autoría no la evaluó correctamente en la prueba mínima. Las posiciones
auxiliares están fuera de las tablas y se recalculan al ordenar los datos.
Los datos originales no dependen de los resultados de la consulta.

La hoja Consulta requiere texto literal en los campos UMAS y año numérico
entero. Los espacios periféricos producen una entrada incompleta explícita;
el usuario puede retirarlos sin cambiar espacios internos. H7 admite su recorte
automático; esta diferencia de interfaz no crea equivalencias ni modifica la
clave válida. Período y régimen permanecen como texto, sin convertir a semestre.


## Cierre y entrega

Estado: **COMPLETADA_CON_LIMITES_DE_EVIDENCIA**. Se instaló el diccionario
actualizado en la carpeta OneDrive 2026 solicitada, bajo su nombre original.
El archivo anterior se conserva en `respaldos/20261015_antes_fase8_diccionario/`
con su SHA-256 original. La sincronización remota de OneDrive no se verificó.

El libro tiene nueve hojas y ocho tablas con filtros: Consulta, Diccionario
SIES, Ejemplos, Historia SIES, Planes UMAS, Programas UMAS, Candidatos,
Claves UMAS y Guía. Historia conserva por separado los atributos publicados
en oferta y los informados en MRUN, sin llenar uno desde el otro.

| Control | Resultado |
|---|---:|
| Códigos SIES conservados | 141 |
| Claves anuales de historia SIES | 767 |
| Planes UMAS conservados | 236 |
| Relaciones de programa conservadas | 257 |
| Relaciones candidatas de plan | 513 |
| Contextos y nombres agrupados para consulta | 292 |
| Ejemplos generales con localizador | 13 |
| Nombres oficiales de oferta 2026 | 124 |
| Claves con Sector IPSS 2026 respaldado | 61 |
| Reglas efectivas acreditadas | 0 |

Se verificaron 43.109 celdas de datos del XLSX contra el descriptor preparado,
además de encabezados, tipos, filtros, paneles y cachés de consulta. La lógica
de agrupación coincide con 1.359 casos derivados de H7 y fronteras adicionales.
Las fórmulas se probaron en Artifact Tool en 35 casos UMAS y 34 casos SIES,
más controles de entradas inválidas y apertura: 250 aserciones aprobadas.
No se detectaron errores de fórmula ni vínculos externos o macros. Se revisaron
visualmente las nueve hojas y el bloque histórico MRUN. No se afirma recálculo
nativo en Microsoft Excel ni comportamiento probado en Windows.

Una segunda generación conservó los mismos valores, fórmulas, tipos, estilos,
tablas y paneles. Todas las partes XML resultaron idénticas salvo los IDs de
relaciones generados por la librería. Por tanto la reproducción es semántica,
no igualdad binaria del ZIP. El manifiesto identifica el hash exacto instalado.

El reemplazo del diccionario cambia deliberadamente su ruta canónica como
fuente de las fases iniciales. La edición anterior sigue disponible por hash
en el respaldo; la reubicación está registrada y no se reescribieron los
manifiestos H1–H7. Para reconstruir una fase antigua que exige aquel archivo,
se debe usar explícitamente la edición respaldada; la nueva no sustituye sus
bytes históricos. La reproducción H8 consume los snapshots académicos H5–H7.

Las 132 referencias del control de esta fase conservaron sus hashes. No se
modificaron los motores, los catálogos congelados ni Matrícula Unificada.
No se realizó commit o push. Completar H8 significa entregar el diccionario
consultable y reproducible; la acreditación de equivalencias históricas y la
ampliación sectorial siguen requiriendo evidencia.

- [Registro de entrega y respaldo](../data/versiones_historicas_sies_umas/fase_8_20261015/entrega.json).
- [Verificación del XLSX](../data/versiones_historicas_sies_umas/fase_8_20261015/qa_xlsx.json).
- [QA de cierre](../data/versiones_historicas_sies_umas/fase_8_20261015/qa_fase8.json).
- [Reproducción](../data/versiones_historicas_sies_umas/fase_8_20261015/reproduccion_verificada.json).


### Control posterior al guardado en OneDrive

El archivo cambió después de instalarse. La comparación completa confirmó
iguales datos, fórmulas, tipos, estilos, tablas y paneles, y volvió a aprobar
43.109 celdas. Aparecieron partes customXml, propiedades personalizadas y
entradas internas adicionales. No se atribuye ese cambio a una aplicación
específica ni se infiere recálculo nativo. Se conservó el archivo observado.
El registro distingue hash de autoría y hash posterior verificado. Los controles
están en `control_postguardado.json` y `qa_onedrive_postguardado.json`.

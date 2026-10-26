# Seguimiento T1 → T2/T3 hasta 2026 — V13

D: aplicación solicitada por Alexi el 23-10-2026. Se reutiliza el código T1 ya
documentado y se revisan excepciones de carrera, jornada o plan. No se alteran
bases, diccionario activo, reglas de vigencia, denominadores ni tasas existentes.
Sin commit, push o envío externo.

## Entrega y lectura

B/C: `RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V13.xlsx`, con copia idéntica en
Escritorio. SHA-256: `c4f506adcf16e9ae2bbf072d21be5033e30ee6ee81eb5bc87171a73867cc164b`.

- Hoja 52: seis resultados existentes y, por separado, controles de códigos.
- Hoja 53: 218 grupos código T1 × período; filtros por año, período, carrera,
  código y condición multiversión. La clasificación del estudiante permanece
  en su código T1 aunque exista otro código en el contexto posterior.
- Hoja 54: 223 grupos agregados de contexto, que representan 2.854 observaciones.
  Filtrar «Relación o excepción» y «Origen multiversión». «Respaldo» distingue
  código documental anual, correspondencia interna aprobada y pendiente.
- Hojas 1–51, sus 13 gráficos y sus 33 tablas: partes OOXML idénticas a V12.

## Resultados conservados

| Cohorte T1 | Año observado | Período | Numerador | Denominador | Resultado | Respaldo |
|---|---:|---:|---:|---:|---:|---|
| 2024 | 2025 | 2 | 160 | 558 | 28,67% | C/E: proxy de actividad y estado |
| 2024 | 2025 | 3 | 175 | 558 | 31,36% | C/E: proxy de actividad y estado |
| 2025 | 2025 | 2 | 600 | 1.150 | 52,17% | C/E: proxy; desglose pendiente |
| 2025 | 2025 | 3 | 1.023 | 1.150 | 88,96% | B/C: foto T3, indicadores heredados |
| 2026 | 2026 | 2 | 1.042 | 1.471 | 70,84% | C/E: proxy de actividad y estado |
| 2026 | 2026 | 3 | 1.360 | 1.467 | 92,71% | B/C: foto T3, indicadores heredados |

B/C: población T1 de origen 558/1.150/1.471. Los cuatro `NO APLICA` que ya dejaban
el denominador T3-2026 en 1.467 se conservan. Los 1.294 ingresos nuevos T2/T3
de otras filas del libro no se reclasifican ni se incorporan a estos grupos T1.

B/C/D/E: 2.737 contextos con código documental anual, 13 con correspondencia
interna aprobada y 104 pendientes. De los 2.750 respaldados, 2.713 conservan
el código T1 y 37 difieren: 23 en jornada, 8 en carrera y 6 en versión dentro
de la misma familia. No se aprobó ningún cierre nuevo. En el foco multiversión:
1.040 documentales, 13 internos y 24 pendientes; bandera heredada de V12.

C: los 6.358 registros origen × período se separan en 2.838 con contexto y
3.520 sin contexto. Hay 16 contextos adicionales por expedientes múltiples:
no se suman como estudiantes nuevos ni modifican la población de la tasa.

## Pendientes y límites

E: en T2-2025, la reproducción del proxy con documentos R y P obtiene 611
personas con estado VIGENTE. Solo R reproduce 600; no se encontró el constructor
original que justifique excluir los 11 P adicionales. No se adoptó esa exclusión
ni el 611. Se conserva 600/1.150 y el desglose por código muestra «Pendiente».

E: actividad y estado del extracto PROMEDIOS no acreditan por sí mismos vigencia
histórica en una fecha de cierre. Los períodos nativos no se homologan
automáticamente a trimestres. No se infiere deserción de ausencia de contexto.

B/C: el calendario existente sigue a 2024 en 2025-2/3; las cohortes 2025 y 2026
se observan en su mismo año. V12 consultaba todos los períodos del año de origen.
Los 203 pendientes de esa otra cobertura y los 104 de esta entrega no son una
reducción comparable ni nuevos cierres.

E: no se acredita fecha exacta de migración de plan ni aceptación individual
de SIES. El código anual documentado y la correspondencia interna conservan
sus distintos niveles de respaldo.

## Reproducción y evidencias

C: `MANIFEST_SEGUIMIENTO.json` fija rutas, hashes, descriptor v7 y scripts.
`INDICADORES_AGREGADOS.json` contiene población y conteos por código;
`CONSULTA_CALENDARIO_AGREGADA.json` contiene los controles de consultas;
`TABLAS_SEGUIMIENTO.json` es la entrada agregada del constructor Excel.
`FORMULAS.json` registra las 302 fórmulas nuevas y `QA_EXCEL.json` sus controles.
Los identificadores de las evidencias individuales permanecen fuera de Git.

C: secuencia de scripts del repositorio:

1. `v13_20261023_seguimiento_t1_agregado.py --output-dir <directorio_nuevo>`:
   reproduce los indicadores con su auxiliar hermano
   `v13_20261023_reconstruir_proxy_t1.py`. No sustituye la regla original faltante.
2. `consultar_destinos_calendario_v13_20261023.py --salida-agregada <json_nuevo>
   --salida-privada <carpeta_privada_nueva>`: consulta v7 con contexto exacto;
   `seguir_cohorte` no admite 2024→2025, por eso se separan los dos años.
3. `preparar_seguimiento_t1_v13_20261023.py <directorio_salida>`: lee las entradas
   persistentes congeladas por hash y prepara tablas y manifiesto. No contiene
   decisiones nuevas de asignación.
4. `construir_seguimiento_t1_v13_20261023.mjs <directorio_salida>`: Artifact Tool
   construye y recalcula las tres hojas, con fórmulas referidas a la hoja 18.
5. `ensamblar_seguimiento_t1_v13_20261023.py <directorio_salida>`: reemplaza solo
   52–54, agrega estilos sin modificar los antiguos, valida y copia a Escritorio.

C: los pasos 3–5 reproducen exactamente esta entrega con las evidencias locales
existentes. Para una nueva consulta, fijar primero rutas y hashes de su nueva
edición; no sustituir silenciosamente los archivos congelados. El ensamblador
rechaza sobrescribir la entrega final.

## QA y checkpoint

C: 302 fórmulas contrastadas contra cálculos independientes; 308 controles
aritméticos correctos, sin errores de cálculo en 52–54. XML y filtros de tablas
validados; 54 hojas, 35 tablas y 13 gráficos. Fuentes intactas por hash. Ramas y
HEAD sin cambio: `feature/ire-2026`, `80ca13a5a249a1a2bd53a699f5f73689b1f53040`.
Los cambios ajenos del repositorio no se incluyen ni se modifican.

E: recálculo con Artifact Tool; no se probó apertura con Excel nativo. Conservar
el límite junto a las evidencias de QA, sin afirmar compatibilidad nativa probada.

C: para continuar, trabajar sobre V13 y el descriptor v7. Resolver el linaje
individual del proxy 600 antes de repartirlo por código; revisar solamente las
104 excepciones de atribución, priorizando las 24 multiversión si corresponde.
No usar esos pendientes para alterar las tasas, restar estudiantes o reemplazar
su código de origen. No hay publicación GitHub nueva en esta entrega.

# Fase 7 — Integración de la consulta histórica entre proyectos

Autorización: «vamos con la fase 7», 2026-10-15. Esta especificación precede
a la implementación. Hito H7: las mismas entradas y ámbito producen el mismo
resultado en avance_curricular y CARACTERIZACIÓN.

## Alcance y decisión de integración

Se instala una interfaz de consulta histórica en ambos repositorios, con API
Python y comando JSON. Cada consumidor usa su copia local del mismo paquete
verificado; CARACTERIZACIÓN no depende de la ruta ni de la instalación de
avance_curricular. El exportador del origen gobierna ambas copias. No se edita
manualmente el resolvedor distribuido.

Esta integración corresponde al análisis histórico 2007–2026. Los motores
MU2026, FCU2026, el análisis anual y el catálogo operativo 2027 tienen contratos
propios. No se sustituyen esos flujos: H6 acredita la consulta técnica, pero
el registro de reglas plan/período sigue vacío. La interfaz histórica conserva
los pendientes y no rellena sus campos con resultados de esos catálogos.
El Excel definitivo corresponde a H8.

## Contrato compartido

- Consulta UMAS: año entero, período, régimen, código de carrera interno,
  nombre interno, plan, sede y jornada. Se pasan los ocho parámetros literales
  al resolvedor H5. No se completan desde año de ingreso, nombre del plan,
  MODALIDAD escolar, máximo de versión ni similitud nominal.
- Consulta SIES: año entero + Código Único. Devuelve la oferta anual y la
  observación MRUN correspondiente; no acredita una equivalencia UMAS.
- Año obligatorio y explícito en la API. No hay año activo, catálogo más
  reciente ni fallback al catálogo anual 2027. Una consulta fuera del ámbito
  conserva FUERA_AMBITO.
- Los resultados H5 se preservan íntegros: estado, motivos, candidatos,
  nombres de fuente, evidencia y asignación individual no acreditada. Los
  nombres oficiales no reciben sufijos de jornada, modalidad o continuidad.
- Los lotes conservan orden y multiplicidad, sin deduplicar ni expandir
  consultas. La API no acepta registros personales completos: recibe solo
  parámetros académicos del contrato. Sus conteos son consultas, no personas.
- El adaptador de PROMEDIOS del piloto H6 permanece congelado. Las entradas
  ya gobernadas se consumen directamente; no se introduce otro algoritmo de
  adaptación ni una conversión automática de DatosAlumnos.

## Paquete y distribución

Versión inicial `2007_2026_h5_20261015`, dentro de
`gobernanza/sies/historico/` en cada repositorio. Descriptor
`ACTIVO_2007_2026.json` con rutas relativas y SHA-256 de maestro, manifiesto H5,
resolvedor y aceptación H6. El cliente fija además el hash del descriptor.
Se verifica todo antes de ejecutar el resolvedor. Se rechazan rutas externas,
hashes distintos, esquema/ámbito incompatible y reglas efectivas nuevas en
esta edición. El paquete inicial admite únicamente el maestro H5 auditado.

Las rutas de procedencia que ya contiene H5 se conservan como metadatos.
No se abren durante la consulta ni son dependencias operativas. No se copian
reportes personales originales. Futuras reglas exigirán otra edición y un
contrato que distribuya y verifique sus evidencias; no se habilitan cambiando
el hash esperado de esta edición.

El exportador verifica primero todos los archivos de destino y rechaza una
instalación existente diferente antes de escribir. Repetir la misma edición
es idempotente. No promueve versiones diferentes ni borra copias previas.
Los auxiliares se ubican en common/, scripts/ y tests/, siguiendo el layout
de avance_curricular y evitando importar los motores congelados. En
CARACTERIZACIÓN se añade ese módulo compartido como interfaz independiente.

## Validación prevista

Comparar las 1.349 consultas UMAS y las 767 claves anuales SIES del piloto
entre los dos consumidores y H5. Exigir igualdad de objetos completos y
concordancia con estados, destinos, atributos y pesos registrados en H6.
Conservar los 141 códigos y 236 planes del maestro, incluidos los inactivos.

Probar aislamiento del repositorio de origen, portabilidad desde otra carpeta,
ausencias, alteraciones de cada componente, descriptor modificado, intento de
salida por ruta externa, repetición de instalación, rechazo sin escritura
parcial, entradas incompletas y ausencia de extrapolación. Verificar resultados
únicos y múltiples pendientes, consulta SIES sin oferta y literalidad de nombres.
Comprobar las referencias MU/FCU y las fases previas antes y después, sin
ejecutar pipelines reales ni generar entregas de matrícula/caracterización.

La aceptación técnica H7 no certifica versiones de malla. El estado de cierre
debe distinguir integración de consultas de habilitación de asignaciones.


## Uso en cualquiera de los dos proyectos

Desde la raíz del repositorio (en Windows, `python` en lugar de `python3`):

```bash
python3 scripts/consultar_sies_historico.py --anio 2026 --codigo-unico I162S2C77J4V2
python3 scripts/consultar_sies_historico.py --anio 2026 --codcarpr CILOG --nombre-interno "CONTINUIDAD INGENIERIA LOGISTICA" --plan-umas CILOG20241 --sede-umas RE --jornada-umas O --periodo 1 --regimen TRIMESTRAL
python3 scripts/consultar_sies_historico.py --lote /ruta/consultas_academicas.json
```

El JSON de lote es una lista de objetos `{"tipo":"SIES","parametros":{"anio":2026,"codigo_unico":"I162S2C77J4V2"}}`
o `tipo=UMAS` con los ocho parámetros académicos. No recibe reportes personales
completos. El comando imprime un JSON; puede redirigirse a un archivo nuevo.
Salida 0 significa oferta localizada o equivalencia acreditada: leer siempre
el estado específico. Salida 2 significa al menos una consulta pendiente,
incompleta o fuera del ámbito. Salida 1 significa carga o contrato rechazados.
La consulta de continuidad del ejemplo debe terminar en 2, con ambos candidatos.

API común, sin importar motores institucionales:

```python
from common.consulta_sies_historica import ConsultaHistorica
consulta = ConsultaHistorica()
resultado = consulta.consultar_sies(anio=2026, codigo_unico="I162S2C77J4V2")
trazabilidad = consulta.trazabilidad()
```

Distribuir la misma edición desde avance_curricular:

```bash
python3 scripts/exportar_consulta_historica.py --destino /ruta/repositorio_consumidor
python3 scripts/validar_integracion_historica.py --consumidor /ruta/CARACTERIZACION --salida /ruta/nueva/validacion_h7
python3 -m unittest discover -s tests -p 'test_integracion_historica.py' -v
```

La exportación instala siete archivos, incluyendo cliente y CLI idénticos.
Si ya existen con otros bytes, se rechaza antes de escribir. No actualiza
catálogos operativos ni promueve otra edición. Las consultas no necesitan
los reportes de Descargas ni la ruta de OneDrive del autor.


## Resultado y cierre H7

Estado: **COMPLETADA_CON_LIMITES**. La interfaz de consulta histórica quedó
instalada en ambos repositorios. Los siete archivos de cada instalación son
idénticos y la copia de Caracterización funciona de forma independiente.
No se habilitó asignación automática de versiones históricas.

| Control | Resultado |
|---|---:|
| Consultas UMAS iguales a H5 en ambos consumidores | 1.349 de 1.349 |
| Consultas SIES anuales iguales a H5 en ambos consumidores | 767 de 767 |
| Diferencias en objetos completos | 0 |
| Pruebas de integración aprobadas | 18 de 18 |
| Archivos de validación reproducidos idénticos | 3 de 3 |
| Referencias previas preservadas | 158 de 158 |
| Referencias del cierre FCU2026 verificadas | 51 de 51 |

Las 1.349 consultas UMAS representan 125.264 filas del reporte PROMEDIOS.
Permanecen 59 consultas PENDIENTE_EVIDENCIA (13.879 filas) y 1.290 consultas
SIN_EQUIVALENCIA (111.385 filas). Los 5.176 contextos de H6 concilian con
129.493 filas: las 4.229 restantes conservan sus exclusiones (4.211 por año,
17 por carrera y 1 por contexto de plan). Estos pesos no cuentan personas.
SIES conserva 747 consultas con oferta y 20 sin cobertura de oferta anual.
Los totales son resultados técnicos de los extractos congelados H5/H6.

La igualdad se comprobó sobre el objeto completo de respuesta, incluidos
candidatos, nombres literales y localizadores. Se contrastaron también estados,
destinos y pesos de H6; no se validó solo una igualdad de totales.

Las pruebas comprobaron claves incompletas, año explícito, ausencia de
extrapolación a 2025/2027, candidatos únicos y múltiples pendientes,
observaciones MRUN sin oferta, orden y repeticiones en lotes, rechazo de
columnas ajenas, aislamiento de resultados mutables, componentes alterados,
paquete ausente, enlace externo, instalación idempotente y rechazo de destino
conflictivo sin escritura parcial. La portabilidad se probó con Python en modo
`-I`, desde una carpeta temporal y una instalación independiente del origen.
Además, los CLI realmente instalados en ambos proyectos dieron los mismos
bytes y código de salida 2 para continuidad Logística. No se probó en Windows.

Las tres salidas reproducibles son resumen, tabla de paridad y manifiesto.
Los informes de QA, pruebas y controles se agregan como evidencia de cierre.
No se ejecutaron procesos diarios/anuales, no se modificaron Excel ni se
realizó commit o publicación remota. H8 permanece pendiente.

- [Resumen](../data/versiones_historicas_sies_umas/fase_7_20261015/resumen.json).
- [Paridad de consultas](../data/versiones_historicas_sies_umas/fase_7_20261015/paridad_consultas.tsv).
- [QA final](../data/versiones_historicas_sies_umas/fase_7_20261015/qa_fase7.json).
- [Ejemplo real de continuidad](../data/versiones_historicas_sies_umas/fase_7_20261015/ejemplo_cli_continuidad.json).

Fuentes de esta fase: maestro H5, SHA-256
`2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5`,
y tablas académicas H6 fijadas por su manifiesto. Edición: 2026-10-15;
intervalo objetivo 2007–2026, con los límites de cobertura anteriores.
El glosario de oferta SIES 2010–2026 (página 2) distingue modalidad,
jornada y versión; no constituye evidencia individual de asignación de malla.
La fase consume los resultados auditados y no vuelve a leer reportes personales.

# Capa demográfica del enlace histórico

Especificación previa, 2026-10-16. Extensión diagnóstica en common/, scripts/ y
tests/; conserva agrupaciones, fuentes, Excel y motores congelados.

## Reglas

Comparar sexo por diccionario específico de fuente: UMAS M=hombre/F=mujer;
MRUN 1=hombre/2=mujer; reporte H=hombre/M=mujer. Un valor no homologado no se
convierte a hombre/mujer. No se inventa codificación no binaria en MRUN.
Nacimiento se compara al año-mes: MRUN no permite discriminar por día. Edad o
rango etario no constituyen evidencia independiente de la fecha de nacimiento.
190001 es marcador sin dato. No completar fechas ni aplicar tolerancias elegidas
para favorecer un enlace. Vacíos, inválidos y no homologados quedan explícitos.

Auditar diversidad de nacimiento y sexo entre expedientes del mismo documento
UMAS, entre registros anuales MRUN y entre años MRUN. Contrastar UMAS contra
reportes históricos unidos por documento, sin usar el MRUN supuesto para elegir
el dato preferido. Registrar coincidencia, contradicción y ausencia por campo.
La contradicción no demuestra cuál fuente está equivocada.

Reproducir presencia anual y exactamente los 500 casos anteriores. Evaluar:
base con ingreso original; puerta de calidad interna UMAS/MRUN; y puerta que
además retiene contradicciones con reportes históricos. Las puertas solo
suspenden propuestas ya existentes: no eliminan competidores para generar nuevas
unicidades. Datos sin contraste documental no se presentan como corroborados.
El escenario documental comparte fuente con la referencia de evaluación: sus
resultados NO son una validación independiente ni una tasa de precisión.

Producir estados de calidad, incidencias agregadas, resultados de 500 casos y
manifest. No exportar fechas, RUT, CODCLI, MRUN ni hashes personales. Mantener
separadas inferencia de identidad y equivalencia de código académico. Validar
paridad de la reproducción, particiones y preservación de archivos congelados.

## Resultados ejecutados

Nacimiento y sexo ya participaban en el filtro de candidaturas. Esta capa añade
calidad y contraste histórico; no los presenta como variables nuevas ni como
pruebas independientes repetidas. No aumenta artificialmente las asignaciones.

La comparación usa el nacimiento a precisión AAAAMM, conforme al esquema MRUN
conservado en `data/recuperacion_cruce_mrun_umas/20261016/ER_Matricula_Educacion_Superior_2007_2026_PUBL_MRUN.pdf`,
página 2, que declara sexo 1/2 y el marcador 190001. Las fuentes UMAS y reportes
usan sus propios diccionarios, no el mismo significado de la letra M.

### Auditoría de las fuentes

- UMAS 12023: 15.072 filas; dos nacimientos no interpretables y once valores de
  sexo no homologados. Los once no se clasifican automáticamente como no binarios
  ni se convierten a una categoría binaria. Son filas, no personas diferentes.
- 12.944 documentos UMAS normalizables: no se observaron nacimientos o sexos
  válidos diferentes entre sus expedientes. Un dato coherente internamente puede
  seguir siendo distinto del reporte histórico.
- MRUN: 24.386 filas y 11.265 identificadores distintos; los valores de sexo y
  nacimiento son interpretables. No se observaron cambios de año-mes de nacimiento
  dentro de un MRUN, pero uno presenta valores de sexo distintos entre registros.
  Puede corresponder a rectificación o cambio de registro: no se declara error.
- Comparación por documento y año con reportes: 4.090 observaciones coinciden en
  ambos atributos, 50 requieren revisión y nueve no tienen persona UMAS
  comparable. Se cuentan personas/año, no personas distintas entre años.

| Año | Diferencia solo de nacimiento | Diferencia solo de sexo |
|---|---:|---:|
| 2018 | 18 | 2 |
| 2019 | 14 | 2 |
| 2020 | 12 | 1 |
| 2022 | 0 | 1 |
| Total de observaciones persona/año | 44 | 6 |

Este universo es más amplio que las 46 filas de reporte del diagnóstico anterior:
aquel exigía familia compatible y contaba filas; aquí se contrasta por documento
y año sin exigir coincidencia de carrera, para no ocultar problemas demográficos.
Los datos normalizados del reporte conservan su limitación de extracción: un
vacío normalizado no permite distinguir todos los motivos del valor original.

### Efecto en los mismos 500 casos

| Resultado | Antes | Solo calidad interna | Además contraste documental |
|---|---:|---:|---:|
| Concordante con referencia | 362 | 362 | 362 |
| Contradictorio con referencia | 1 | 1 | 0 |
| Propuesta sin referencia suficiente | 8 | 8 | 8 |
| Sin enlace aceptado por estas restricciones | 129 | 129 | 130 |
| Total | 500 | 500 | 500 |

492 casos coinciden demográficamente con el reporte y ocho presentan
contradicción. Siete de esos ocho ya estaban sin enlace; el restante es la
propuesta ENSAYO-381, TPCRE 2018, que queda suspendida. No se reemplaza su
nacimiento, no se toma el MRUN de la referencia como nueva asignación y no se
libera su candidato para crear otra unicidad artificial.

La calidad interna no detectó esa propuesta porque el dato UMAS era consistente
entre sus expedientes. El contraste histórico sí reveló la diferencia. Cero
contradicciones observadas después del control NO significa certeza ni 100 %
de precisión: la puerta documental utiliza reportes que también participan en
la referencia de evaluación. Los ocho sin referencia siguen pendientes.

### Efecto sobre las propuestas del universo ampliado

De los 2.418 enlaces forzados condicionales del ensayo anterior:

- 2.411 coinciden en demografía con el reporte por documento y año.
- Tres quedan retenidos por contradicción documental.
- Uno queda retenido por calidad interna.
- Tres no tienen contraste documental para ese contexto.

Coincidencia demográfica no acredita identidad ni asigna versión de carrera.
Los tres sin contraste conservan ese estado, no se denominan corroborados.
El algoritmo no se vuelve a ejecutar quitando personas retenidas, para evitar
que su retirada genere nuevas asignaciones sin evidencia adicional.

## Gobierno y validación

Seis pruebas cubren semántica de sexo según fuente, valores no homologados,
precisión mensual, marcador sin dato, fechas inválidas, conflictos internos y
contradicciones documentales. Se reprodujeron exactamente los resultados base
de los 500 casos; las puertas solo suspenden propuestas existentes.

Se verificaron los hashes de todas las fuentes utilizadas, 137 referencias
congeladas, Excel editado por Alexi y resultados del ensayo anterior. No se
modificaron fechas, sexo, agrupaciones, diccionario de carreras ni cargas reales.
No se exportan identificadores ni fechas. Código y agregados están en el
proyecto; las fuentes externas se referencian por hash, sin nueva copia integral.

```sh
python3 -m unittest discover -s tests -p test_capa_demografica.py
python3 scripts/diagnosticar_capa_demografica.py
```

[Resumen](../data/capa_demografica/20261016/resumen.json),
[500 casos](../data/capa_demografica/20261016/casos_500.json),
[incidencias agregadas](../data/capa_demografica/20261016/incidencias_agregadas.json),
[manifest](../data/capa_demografica/20261016/manifest.json).

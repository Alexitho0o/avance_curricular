# Hipótesis de enlace conjunto MRUN–UMAS

Especificación previa a implementación, 2026-10-16. Diagnóstico autorizado por
Alexi; no modifica el maestro, el Excel ni cargas operativas. Extensión aislada
en scripts/, common/ y tests/ conforme al layout autorizado en agent.md.

## Contrato

Construir candidaturas propias usando año observado, nacimiento AAAAMM, sexo y
familias de carreras existentes sin versión. No usar el Código Único del reporte
institucional ni su resolución documental para seleccionar enlaces. Retirar el
filtro de tipo actual: el ensayo previo demostró exclusiones históricas. Esta
retirada amplía candidatos; no acredita equivalencia regular–continuidad.

La unidad de identidad es persona/año: agrupar RUT en memoria y conservar sus
varias carreras. MRUN puede tener varias matrículas. Un enlace anual impide
asignar dos personas distintas a un mismo MRUN en ese año. Los grafos unen todas
las carreras de cada persona, sin imponer una carrera única. Fuentes UMAS de
DatosAlumnos: ANOMATRICULA define el corte experimental, no acredita que sea el
universo exacto de matrícula SIES anual.

Comparar dos variantes: base demográfica y familiar; sensibilidad que además
exige ANOINGRESO igual al ingreso original MRUN cuando ambos son años válidos.
Esta segunda es una hipótesis, no una regla acreditada; admite desconocidos,
no exige ingreso a carrera actual (continuidad puede heredar el ingreso técnico).

Calcular componentes del grafo y máximo número de pares uno a uno. Un par es
forzado condicional si quitarlo reduce el máximo: aparece en todos los
emparejamientos de máxima cardinalidad. Esto depende de que las candidaturas y
la hipótesis de maximizar enlaces sean correctas; NO equivale a identidad
certificada. Componentes equilibrados y sin colisiones tampoco la certifican.
Conservar sin asignar los nodos ambiguos o sin candidatos. No llenar cupos para
igualar totales. Totales por año/familia y cohortes originales son controles;
las familias múltiples se marcan y no se suman como universos disjuntos.

Evaluar las mismas 500 personas del ensayo anterior, seleccionadas antes de los
resultados. El enlace documental indirecto queda reservado a evaluación. Medir
acuerdos, contradicciones y referencias no resueltas separadamente. La muestra
no es una verdad oficial ni permite estimar la tasa poblacional de error.
No presentar concordancia con los campos usados como validación independiente.

## Entregables y aceptación

Script reproducible, algoritmo de asignación con pruebas de unicidad, simetría,
colisiones, componentes desiguales y confrontación exhaustiva en grafos pequeños;
conteos por cohorte y carrera; resultados anónimos de 500 casos; manifest con
hashes y comprobación de las 137 referencias congeladas y Excel del usuario.
Datos identificatorios permanecen en memoria. Fuentes externas verificadas por
hash se referencian: este diagnóstico no constituye una copia portátil de ellas.

## Incidencia de fuente antes de ejecución

DATOSDEALUMNOS_11998.xlsx ya no existe en su ruta registrada. Se autoriza como
alternativa diagnóstica explícita DATOSDEALUMNOS_12023.xlsx (SHA-256 registrado
en el cargador), manteniendo algoritmo de selección y estratos. Si se usa esta
alternativa, se informa como nuevo ensayo de 500 personas: la igualdad de
metadatos académicos no demuestra identidad de la muestra previa, cuyos
identificadores no se exportaron. No sobrescribe resultados anteriores.

## Resultado ejecutado

Se utilizó DATOSDEALUMNOS_12023.xlsx, hoja Hoja1, con hash fijo. El archivo
11998 no estaba en su ruta; la búsqueda de copias no acreditó una copia idéntica.
Se aplicó la misma selección determinista: 125 personas por año 2018, 2019,
2020 y 2022, 500 personas distintas en memoria. Coinciden los metadatos
académicos de los 500 casos anteriores; no se afirma identidad exacta de ambas
muestras porque la anterior no guardó identificadores. La comparación entre las
dos variantes de ESTE ensayo sí utiliza exactamente las mismas 500 personas.

La referencia documental indirecta resuelve 452 de los 500 casos. Se reserva
para evaluación; no alimenta el grafo. Usa reportes institucionales con documento
y código, combinados con atributos MRUN. No constituye una tabla oficial de
identidad. Nacimiento, sexo e ingreso original participan también en la
construcción de esa referencia: su coincidencia no es evidencia independiente;
el código completo, semestres y otros años aportan contraste adicional.

| Resultado en 500 personas | Año, familia, sexo y nacimiento | Añadiendo ingreso original |
|---|---:|---:|
| Enlace concordante con referencia | 310 | 360 |
| Enlace contradictorio | 2 | 1 |
| Enlace sin referencia unívoca para evaluarlo | 11 | 11 |
| Sin enlace forzado por las restricciones | 177 | 128 |
| Total | 500 | 500 |

La segunda variante mejora la concordancia en este ensayo, pero no es una regla
lista para producción. 360 es concordancia con evidencia indirecta, no 360
identidades certificadas ni una tasa poblacional de acierto. Los 128 sin enlace
incluyen tanto ambigüedades como ausencia de candidatos. Los 11 no evaluables no
se convierten en éxitos. El ingreso original no se confunde con ingreso a la
carrera actual y los marcadores especiales no se convierten en años.

### Aporte de resolver conjuntamente

En el universo experimental completo hay 2.136 personas/año UMAS. La variante
base tiene 1.209 enlaces únicos recíprocos; la asignación conjunta permite
1.229 pares forzados condicionales, 20 adicionales. Con ingreso original son
1.383 y 1.396, 13 adicionales. Esos pares aparecen en TODOS los emparejamientos
de tamaño máximo del grafo, no se escoge arbitrariamente una solución. No son
2.136 personas distintas entre años. Al agregar ingreso original baja el máximo
posible de enlaces (1.746→1.593): hay más unicidad, pero también más exclusión;
se conserva esa pérdida de cobertura.

En el control interno de personas con enlace propuesto en más de un año, la
base tiene 36 trayectorias con igual MRUN y tres con MRUN diferente. La segunda
variante tiene 38 con igual MRUN y ninguna diferente entre las resolubles. Es
consistencia interna, no prueba independiente ni evidencia de que todos los
casos tengan seguimiento longitudinal.

### Qué revelan los totales

| Año observado | Personas UMAS seleccionadas por ANOMATRICULA | Personas MRUN del año |
|---|---:|---:|
| 2018 | 495 | 1.077 |
| 2019 | 609 | 1.088 |
| 2020 | 487 | 968 |
| 2022 | 545 | 1.018 |

Estos recortes NO son universos de matrícula anual equivalentes. No se infiere
que falten estudiantes en UMAS: ANOMATRICULA del extracto actual no reconstruye
por sí solo todas las matrículas históricas. Tampoco son totales de una única
cohorte de ingreso. El siguiente trabajo debe reconstruir pertenencia anual a
partir de fuentes históricas y cortes, incluyendo continuidad, retiros y
reincorporaciones, antes de exigir igualdad de cupos.

Se construyeron además 644 paneles año/familia/ingreso original/sexo: 89 tienen
igual número de personas y 74 también igual distribución de año-mes de
nacimiento. La igualdad es un control necesario cuando se acreditan universos
comparables, pero no determina identidades si dos personas comparten atributos.
Las familias múltiples pueden repetir personas entre paneles; NO sumar estos
paneles para obtener matrícula. Se conserva año-mes de nacimiento para cruzar
en memoria, sin exportarlo. MRUN no aporta el día del nacimiento. Los valores
de sexo sin correspondencia acreditada quedan fuera del cruce demográfico.

### Contraejemplo que hay que conservar

ENSAYO-381, TPCRE, año 2018: ambas variantes producen un candidato único, pero
no coincide con el MRUN de la referencia documental. Ambos pertenecen a
I162S2C2J2V1. Por tanto, acertar el código de carrera y obtener un único candidato
no prueba que hayamos identificado correctamente a la persona. Este caso
permanece marcado como contradicción; no se promueve ninguna identidad.
La revisión puntual detectó que el año-mes de nacimiento UMAS difiere del de
la referencia MRUN, mientras sexo e ingreso original coinciden. El filtro
demográfico excluyó a la referencia y dejó otra persona como candidato único.
Esto exige controlar calidad de nacimiento, no relajar automáticamente el filtro.

## Gobierno y comprobaciones

- Algoritmo contrastado con enumeración exhaustiva de los 512 grafos posibles
  de tres personas por tres MRUN; incluye empates, colisiones, vacíos y cobertura
  desigual. Prueba adicional de resolución conjunta de tres personas.
- 137 referencias congeladas y Excel editado por Alexi conservan sus hashes.
- Resultados previos, catálogos, agrupaciones y cargas reales permanecen intactos.
- La tabla del ensayo usa casos anónimos, número de alternativas, estados y
  códigos académicos. No exporta RUT, MRUN, CODCLI ni fecha de nacimiento.
- Código, especificación y resultados en el proyecto; fuentes personales
  externas referenciadas por hash, no respaldadas íntegramente por este paquete.

Reproducción:

```sh
python3 -m unittest discover -s tests -p test_enlace_conjunto.py
python3 scripts/diagnosticar_enlace_conjunto.py
```

[Resumen](../data/hipotesis_enlace_conjunto/20261016/resumen.json),
[500 casos](../data/hipotesis_enlace_conjunto/20261016/casos_500.json),
[totales por cohorte](../data/hipotesis_enlace_conjunto/20261016/totales_cohortes.json),
[manifest](../data/hipotesis_enlace_conjunto/20261016/manifest.json).

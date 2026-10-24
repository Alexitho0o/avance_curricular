# Diagnóstico de vigencia anual para ordenar códigos SIES

Contrato previo: contrastar la hipótesis del usuario con manuales disponibles y
las 747 filas institucionales de oferta 2010–2026. Vigencia y versión se conservan
como campos distintos. La primera oferta es inicio del código para el diccionario;
Vigencia aporta su estado anual de admisión. No asignar versiones UMAS ni modificar
las agrupaciones, el Excel o las referencias congeladas. La norma 2027 no acredita
retroactivamente cumplimiento de todas las ediciones anteriores.

Se verifican transiciones 1→2 y 2→1, coexistencia de códigos con vigencia 1 dentro
de familia/tipo, y presencia MRUN con ingreso actual igual al año de observación
bajo vigencia 2. Esta última es una alerta contextual, no un error automático:
la definición de primer año de oferta excluye regular de continuidad y el ingreso
actual puede diferir del original. Ausencia de fila no se convierte en vigencia 3.

## Confirmación documental

Manual Oferta Académica 2026, página 3:
- Vigencia 1: oferta con estudiantes nuevos.
- Vigencia 2: oferta sin estudiantes nuevos, con antiguos.
- Vigencia 3: oferta no vigente, sin nuevos ni antiguos.

En la misma página se precisa que primer año se identifica operacionalmente por
el año de origen igual al año en curso; para Oferta incluye programas regulares
y especiales, excluyendo los regulares de continuidad. Manual Oferta-Acceso 2027,
página 4, reitera esta precisión.

Manual Oferta-Acceso 2027, Anexo 5, páginas 65–66: al modificar atributos que
exigen cambiar Código Único, se indica colocar el programa original en vigencia
2 y el nuevo en vigencia 1. Esto respalda usar vigencia para analizar la sucesión.
No prueba por sí solo qué plan UMAS fue asignado ni acredita retrospectivamente
que toda fila histórica haya seguido el procedimiento de esa edición.

La conclusión del diagnóstico anterior era incompleta al no contrastar este
campo. La primera oferta identifica nacimiento observado; vigencia identifica
estado anual declarado de admisión. No confundir valor 1/2 de vigencia con V1/V2
del Código Único, ni renumerar versiones a partir de este estado.

## Contraste de las filas

Se verificó el SHA-256 del CSV nacional descomprimido y se analizaron sus 747
filas IPSS (139 códigos): 486 con nuevos y 261 sin nuevos. No hay estado 3 en esta
selección; ausencia de fila no equivale a estado 3. Se detectaron 99 cambios de
vigencia, incluidos 25 retornos declarados de sin nuevos a con nuevos en 24 códigos.
Hay 13 grupos año/familia/tipo de programa con varios códigos simultáneamente
con nuevos. No son 13 carreras ni necesariamente perfiles idénticos: duración
y otros atributos deben seguir formando parte del cruce.

Ejemplo: Ingeniería en Informática diurna, familia I162S2C1J1:

| Año | V1 | V2 |
|---|---|---|
| 2018 | Con nuevos | Sin fila |
| 2019 | Sin nuevos | Con nuevos |
| 2020 | Sin nuevos | Con nuevos |
| 2021 | Con nuevos | Con nuevos |
| 2022 | Con nuevos | Sin nuevos |
| 2023–2026 | Sin nuevos | Con nuevos |

2019 respalda la hipótesis de relevo. Los años siguientes impiden convertir el
primer paso a estado 2 en cierre irreversible o en un intervalo permanente.
Estos son estados declarados observados; no se certifica la causa de cada retorno.

En 2026, MRUN contiene dos filas de I162S2C1J1V1 con ingreso actual 2026 pese a
oferta sin nuevos. Sus ingresos originales son 2024 y 2026: deben revisarse por
separado; el primer caso podría ser ingreso actual de trayectoria previa, mientras
el segundo merece contraste de edición, carga y rectificación. Ninguna causa se
asume. Vigencia ayuda a diagnosticar esta diferencia y no debe descartarse porque
haya matrícula observada bajo el código antiguo.

CILOG / I162S2C77J4V2: en oferta 2025 figura con nuevos y en 2026 sin nuevos.
MRUN 2026 tiene 11 filas con ingreso actual 2025/original 2024 y 21 con ingreso
actual 2026/original 2025. Dada la definición específica de primer año de oferta,
las 21 no demuestran por sí solas admisión prohibida: no tienen origen 2026 y el
programa es regular de continuidad. Tampoco se concluye automáticamente que la
vigencia autoriza cualquier ingreso. Requiere aplicar la definición de ese proceso.

## Resultado para gobernar posteriormente

Hipótesis confirmada como criterio formal de estado anual y evidencia de sucesión;
no confirmada como criterio único para ordenar/asignar cada malla UMAS. Conservar:

1. Código Único completo y primera oferta observada, independiente del quórum.
2. Estado de vigencia por año, sin propagar cierres indefinidamente.
3. Programa y perfil: sede, jornada, modalidad, tipo, duración y plan acreditado.
4. Episodio CODCLI/carrera e ingreso efectivo, separando origen y actual.
5. Admisibilidad según definición del proceso/año; continuidad con tratamiento
   específico. La presencia de antiguos no reabre por sí sola la admisión.
6. Si el código antiguo está en 2 y el nuevo en 1 y no hay otro candidato compatible,
   el relevo aporta evidencia decisiva para la cohorte nueva. Si ambos están en 1,
   hay retornos o contradicciones, el año/vigencia no resuelve por sí solo.

No se alteraron equivalencias, motores o Excel. El próximo uso de esta evidencia
requiere introducirla en el contrato temporal, conservando excepciones trazables.

Fuentes documentales locales:
[Manual 2026, texto completo con páginas](../data/reglas_negocio/20261015/fuentes/manual_oferta_2026_texto_completo.json),
[Manual 2027, texto completo con páginas](../data/reglas_negocio/20261015/fuentes/manual_oferta_acceso_2027_texto_completo.json).

Evidencia reproducible:
[oferta anual](../data/diagnostico_vigencia_oferta/20261016/oferta_anual.json),
[retornos declarados](../data/diagnostico_vigencia_oferta/20261016/retornos_a_con_nuevos.json),
[admisión simultánea](../data/diagnostico_vigencia_oferta/20261016/admision_simultanea.json),
[alertas contextualizadas](../data/diagnostico_vigencia_oferta/20261016/alertas_ingreso_actual.json).

Comando: `python3 scripts/diagnosticar_vigencia_oferta.py`.

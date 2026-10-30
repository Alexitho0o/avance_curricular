# H012 · Familia IECIREOL y versiones de continuadores

**CANDIDATA.** La cobertura histórica pasa de 2.872 a 2.952 contextos respaldados sobre 3.049. El residual pasa de 177 a 97 (3,18 %). La meta es ≤0,1 %. Las 99 posiciones conservan 99 respaldos. Las 80 altas proceden de la corrección C1 y de un único código admisible del año. D7 aporta cero asignaciones y D8 cero asignaciones autónomas.

## Familia · B/C

Tanto el nombre del programa en el listado UMAS como C1 en oferta SIES corresponden a Ingeniería en Informática. C3 corresponde a Ingeniería en Conectividad y Redes. El campo NOMPESTUD contiene el identificador del plan. La columna Nombre_L contiene el nombre de la carrera. El control por plan y por año sólo encontró C1 para los cuatro planes IECIREOL. CORRECCION_FAMILIA_H002_CANDIDATA.json conserva las filas H002 originales y el ajuste candidato. En el residual revisado ninguna otra denominación de plan presentó candidatos H002 de más de una carrera SIES. Personas distintas por celda, sin sumar entre años.

| Plan | Año | Código MU documental | Personas |
|---|---|---|---|
| IECIREOL | 2019 | I162S2C1J4V1 | 5 |
| IECIREOL | 2020 | I162S2C1J4V1 | 16 |
| IECIREOL | 2021 | I162S2C1J4V1 | 23 |
| IECIREOL | 2022 | I162S2C1J4V2 | 8 |
| IECIREOL | 2023 | I162S2C1J4V1 | 1 |
| IECIREOL20191 | 2019 | I162S2C1J4V2 | 24 |
| IECIREOL20191 | 2020 | I162S2C1J4V2 | 18 |
| IECIREOL20191 | 2021 | I162S2C1J4V2 | 13 |
| IECIREOL20191 | 2022 | I162S2C1J4V2 | 12 |
| IECIREOL20191 | 2023 | I162S2C1J4V2 | 2 |
| IECIREOL20191 | 2024 | I162S2C1J4V2 | 1 |
| IECIREOL20201 | 2019 | I162S2C1J4V2 | 1 |
| IECIREOL20201 | 2020 | I162S2C1J4V1 | 16 |
| IECIREOL20201 | 2021 | I162S2C1J4V1 | 10 |
| IECIREOL20201 | 2021 | I162S2C1J4V2 | 1 |
| IECIREOL20201 | 2022 | I162S2C1J4V1 | 1 |
| IECIREOL20201 | 2022 | I162S2C1J4V2 | 9 |
| IECIREOL20201 | 2023 | I162S2C1J4V2 | 8 |
| IECIREOL20201 | 2024 | I162S2C1J4V2 | 4 |
| IECIREOL20211 | 2021 | I162S2C1J4V1 | 50 |
| IECIREOL20211 | 2022 | I162S2C1J4V2 | 99 |
| IECIREOL20211 | 2023 | I162S2C1J4V2 | 151 |
| IECIREOL20211 | 2024 | I162S2C1J4V2 | 65 |
| IECIREOL20211 | 2025 | I162S2C1J4V2 | 14 |

## Validación D7 · C

Se ocultaron todos los códigos de la persona evaluada y se exigieron al menos tres personas distintas restantes con código unánime. Unidad del control amplio: persona × plan × año × código distinto. La medida de precisión usa sólo predicciones emitidas. La regla requiere ≥99,9 % antes de redondear.

| Universo | Aciertos | Errores | Abstenciones | Precisión |
|---|---|---|---|---|
| MU documental con plan/año | 4796 | 12 | 5902 | 99,75042 % |
| Sólo DOCUMENTAL_T1 | 3392 | 8 | 4510 | 99,76471 % |
| Contextos DOCUMENTAL_T1 con versiones idénticas en perfiles H011 | 956 | 1 | 233 | 99,89551 % |

El límite se incumple incluso en el control de perfiles idénticos. Se conserva la distribución de códigos del mismo plan/año, o del año posterior y después anterior cuando falta ese año, en RESIDUAL_H012.json. La validación es dentro del año. El riesgo del traslado entre años no se midió.

## Vigencia de continuadores · A/D/C

El instructivo de Oferta Académica CFT/IP 2027, página 28, y su texto en oferta_academica_2027/01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt, líneas 562–564, distinguen 1 (vigente con nuevos), 2 (sin nuevos, con antiguos) y 3 (no vigente, sin estudiantes). En los registros históricos de oferta se observaron los literales «Vigente con estudiantes nuevos» y «Vigente sin estudiantes nuevos». La decisión D8 admite ambos para el mismo expediente con T1 o matrícula anterior acreditados y sin ingreso en el año. Sólo se admiten opciones con perfil anual compatible. El año de origen, por sí solo, no acredita una matrícula anterior.

De los 28 contextos H011 sin VIGENCIA 1 compatible, 24 de IIND20251 y uno de ICIB20241 carecen de calce de perfil, y otro de ICIB20241 carece de familia/oferta anual. Los dos de TPCRE20191 acreditan matrícula previa y tienen dos versiones admisibles. D7 no se habilitó. La distribución de referencia no es unánime en ambos casos.

## Residual histórico · E

| Motivo | Contextos | Requisito |
|---|---|---|
| D7_NO_SUPERA_VALIDACION_MENOS_DE_TRES_PERSONAS | 1 | Se necesitan tres personas distintas como mínimo en el año de referencia y superar el umbral de la regla. |
| D7_NO_SUPERA_VALIDACION_NO_UNANIME | 7 | El grupo contiene distintas versiones. La distribución por plan/año figura en el detalle. Hace falta evidencia que discrimine dentro del grupo. |
| D7_NO_SUPERA_VALIDACION_UNANIME | 23 | El grupo es unánime, pero el método no pasa el umbral. Hace falta evidencia documental del expediente o una nueva decisión expresamente validada. |
| PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO | 6 | Definición UMAS de 4/5 para los tres contextos semestrales y tres trimestrales pendientes. |
| PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS | 6 | T1 acreditado del expediente y plan, unívoco y con dimensiones compatibles. |
| SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD | 41 | Perfil formal o versión anual compatible en duración total, tipo y modalidad. |
| SIN_CODIGO_ANUAL_COMPATIBLE | 2 | Código anual compatible para el plan. |
| SIN_FAMILIA_H002_U_OFERTA_ANUAL | 6 | Familia acreditada y oferta del año correspondiente. |
| T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO | 5 | Evidencia que explique el T1 frente a la oferta y al perfil anual. |

Se conservan los casos por plan, año, período y motivo. Las 23 referencias unánimes siguen sujetas al control metodológico global. La falta de tres personas en un año observado no habilita saltar al año siguiente.

## Reproducción

Ejecutar resolver.py y luego cerrar.py con el Python local del proyecto. FUENTES_H012.json identifica las entradas por SHA-256. La tabla histórica y el detalle por persona se procesaron en memoria. El único derivado individual está en el directorio privado de H012. R01–R04 y R19 tienen 0,00 pp de diferencia por conservación de fuentes. v20 sigue activo y v21 candidata.

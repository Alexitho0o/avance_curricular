# Comparación carreras a informar CNED

## 1. Objetivo

Determinar qué carreras/programas deben informarse en CNED a partir del listado de referencia y las bases existentes del proyecto.

## 2. Listado CNED incorporado

* ruta TSV: `indices_2025/cned/data/listado_referencia_cned.tsv`
* ruta JSON: `indices_2025/cned/data/listado_referencia_cned.json`
* total filas: 79
* total campos: 23
* filas con Código SIES vacío: 11
* Cod.Carr. duplicados: 0 valores (sin duplicados)
* Código SIES duplicados: 4 valores (I162S2C11J1V1, I162S2C22J1V1, I162S2C22J2V1, I162S2C46J4V1)

## 3. Fuentes revisadas

* `resultados/archivo_listo_para_sies.xlsx` [REVISION_MANUAL]
* `resultados/archivo_listo_para_sies.xlsx` [MATRICULA_UNIFICADA_32]
* `resultados/archivo_listo_para_sies.xlsx` [ARCHIVO_LISTO_SUBIDA]
* `resultados/archivo_listo_para_sies.xlsx` [EXCLUIDOS_CARGA_PREGR]
* `resultados/archivo_listo_para_sies.xlsx` [SIES_AMBIGUOS_POR_RESOL]
* `resultados/archivo_listo_para_sies.xlsx` [CATALOGO_MANUAL]
* `resultados/archivo_listo_para_sies.xlsx` [PUENTE_SIES]
* `resultados/archivo_listo_para_sies.xlsx` [AUDITORIA_CONSOLIDACION]
* `control/catalogos/PUENTE_SIES_COMPILADO.tsv`
* `resultados/matricula_unificada_2026_oficial.xlsx` [Sheet1]
* `resultados/matricula_unificada_2026_control.csv`
* `resultados/carreras_avance_curricular_2025_control.csv`
* `resultados/matricula_avance_curricular_2025_control.csv`
* `control/reportes/sies_pendientes.tsv`
* `control/codcarpr_long.tsv`
* `control/gob_codcarpr_anioingreso_long.tsv`

## 4. Criterios de comparación

* Código SIES/CODIGO_UNICO exacto.
* Cod.Carr. + Año Inicio Actividades + Horario + Sede.
* Nombre Programa normalizado + Horario/Jornada + Año Inicio Actividades + Sede.
* Nombre Programa normalizado + Tipo Programa + Modalidad Programa + Horario.
* Coincidencia difusa de Nombre Programa solo como apoyo; nunca se clasifica como trazabilidad alta.

## 5. Resultado general

| categoria | n |
| --- | --- |
| INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | 43 |
| DUPLICADO_O_AMBIGUO | 13 |
| NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | 10 |
| INFORMAR_CNED_CON_REVISION | 8 |
| NO_INFORMAR_CODIGO_FALTANTE | 5 |

## 6. Carreras recomendadas para informar

| Cod.Carr. | Codigo SIES | Nombre Programa | Horario | Tipo Programa | Modalidad Programa | categoria_final | trazabilidad | motivo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 43930 | I162S2C57J2V1 | TNS en Programación y Análisis de Sistemas | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 43935 | I162S2C57J1V1 | TNS en Programación y Análisis de Sistemas | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 38816 | I162S2C3J4V2 | Ingeniería en Conectividad y Redes | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 43932 | I162S2C57J4V1 | TNS en Programación y Análisis de Sistemas | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 43928 | I162S2C46J4V3 | Ingeniería en Ciberseguridad | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 40876 | I162S2C1J4V2 | Ingeniería en Informática (P.E.) | Otro | Programa Especial | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 43931 | I162S2C47J4V1 | TNS en Ciberseguridad | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 40716 | I162S2C46J2V3 | Ingeniería en Ciberseguridad (P.E.) | Vespertino | Programa Especial | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 48339 | I162S2C22J4V1 | Ingeniería en Automatización y Control Industrial | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51505 | I162S2C76J4V1 | Ingeniería en Administración de Empresas | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51514 | I162S2C78J1V1 | TNS en Administración de Empresas | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51506 | I162S2C78J2V1 | TNS en Administración de Empresas | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51510 | I162S2C78J4V1 | TNS en Administración de Empresas | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51512 | I162S2C79J2V1 | TNS en Logística | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51513 | I162S2C79J4V1 | TNS en Logística | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51502 | I162S2C22J4V2 | Ingeniería en Automatización y Control Industrial  (P.E.) | Otro | Programa Especial | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 6677 | I162S2C1J1V2 | Ingeniería en Informática | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 6678 | I162S2C1J2V4 | Ingeniería en Informática | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 6684 | I162S2C6J2V2 | TNS en Conectividad y Redes | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53717 | I162S2C83J4V1 | Administración Pública | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53721 | I162S2C86J4V1 | Auditoria | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53722 | I162S2C88J4V1 | Ingeniería en Ciencia de Datos | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53723 | I162S2C87J4V1 | Ingeniería Industrial (P.E.) | Otro | Programa Especial | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53720 | I162S2C84J4V1 | TNS en Administración Pública | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53719 | I162S2C89J4V1 | TNS en Ciencia de Datos | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53718 | I162S2C85J4V1 | TNS en Contabilidad General | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53725 | I162S2C91J1V1 | TNS en Enfermería | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 53726 | I162S2C91J2V1 | TNS en Enfermería | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 28356 | I162S2C10J2V1 | TNS en Prevención de Riesgos | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | BAJA | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. |
| 40717 | I162S2C47J1V1 | TNS en Ciberseguridad | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 40713 | I162S2C46J1V1 | Ingeniería en Ciberseguridad | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51503 | I162S2C76J1V1 | Ingeniería en Administración de Empresas | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51504 | I162S2C76J2V1 | Ingeniería en Administración de Empresas | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 40711 | I162S2C47J2V1 | TNS en Ciberseguridad | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 40714 | I162S2C46J2V1 | Ingeniería en Ciberseguridad | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 40712 | I162S2C48J4V1 | TNS en Control Industrial | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_REVISION | BAJA | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. |
| 42539 | I162S2C3J4V3 | Ingeniería en Conectividad y Redes (P.E.) | Otro | Programa Especial | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 32513 | I162S2C11J2V1 | TNS en Automatización y Control Industrial | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | MEDIA | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. |
| 32514 | I162S2C1J2V1 | Ingeniería en Informática | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 6679 | I162S2C3J1V2 | Ingeniería en Conectividad y Redes | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | MEDIA | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. |
| 6680 | I162S2C3J2V4 | Ingeniería en Conectividad y Redes | Vespertino | Programa Regular |  | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 32511 | I162S2C11J1V1 | TNS en Automatización y Control Industrial | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | BAJA | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. |
| 34525 | I162S2C1J2V3 | Ingeniería en Informática (P.E.) | Vespertino | Programa Especial | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 32510 | I162S2C1J1V1 | Ingeniería en Informática | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 32515 | I162S2C22J1V1 | Ingeniería en Automatización y Control Industrial | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | BAJA | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. |
| 34541 | I162S2C3J2V3 | Ingeniería en Conectividad y Redes (P.E.) | Vespertino | Programa Especial | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 36744 | I162S2C6J4V2 | TNS en Conectividad y Redes | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51507 | I162S2C77J1V1 | Ingeniería en Logística | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | MEDIA | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. |
| 51508 | I162S2C77J2V1 | Ingeniería en Logística | Vespertino | Programa Regular | Presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51509 | I162S2C77J4V1 | Ingeniería en Logística | Otro | Programa Regular | No presencial | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. |
| 51511 | I162S2C79J1V1 | TNS en Logística | Diurno | Programa Regular | Presencial | INFORMAR_CNED_CON_REVISION | MEDIA | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. |

## 7. Carreras con revisión manual

| Cod.Carr. | Codigo SIES | Nombre Programa | Horario | categoria_final | motivo | flags_validacion |
| --- | --- | --- | --- | --- | --- | --- |
| 40715 | I162S2C46J2V2 | Ingeniería en Ciberseguridad (P.E.) | Vespertino | DUPLICADO_O_AMBIGUO | Coincidencia difusa con multiples codigos/candidatos posibles. | Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 43934 |  | Ingeniería en Ciberseguridad (P.E.) | Otro | DUPLICADO_O_AMBIGUO | Coincidencia difusa con multiples codigos/candidatos posibles. | Codigo SIES vacio en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| No presencial u Horario Otro \| No es Ingreso Directo \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 38817 | I162S2C46J4V2 | Ingeniería en Informática | Otro | DUPLICADO_O_AMBIGUO | Las llaves normalizadas entregan mas de un codigo/candidato posible. | No presencial u Horario Otro |
| 38818 | I162S2C22J2V2 | Ingeniero en Automatización y Control Industrial (P.E.) | Vespertino | DUPLICADO_O_AMBIGUO | La llave de codigo encuentra mas de un codigo/candidato en bases locales. | Programa Especial \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 6681 | I162S2C2J1V1 | TNS en Programación Computacional | Diurno | DUPLICADO_O_AMBIGUO | La llave de codigo encuentra mas de un codigo/candidato en bases locales. | Año Inicio Actividades antiguo sin matricula reciente observada |
| 6682 | I162S2C2J2V1 | TNS en Programación Computacional | Vespertino | DUPLICADO_O_AMBIGUO | La llave de codigo encuentra mas de un codigo/candidato en bases locales. | Año Inicio Actividades antiguo sin matricula reciente observada |
| 6683 | I162S2C6J1V2 | TNS en Conectividad y Redes | Diurno | DUPLICADO_O_AMBIGUO | La llave de codigo encuentra mas de un codigo/candidato en bases locales. | Año Inicio Actividades antiguo sin matricula reciente observada |
| 43929 | I162S2C46J4V1 | Ingeniería en Ciberseguridad (P.E.) | Otro | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| No presencial u Horario Otro \| No es Ingreso Directo \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 43933 | I162S2C46J4V1 | Ingeniería en Ciberseguridad | Otro | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| No presencial u Horario Otro \| No es Ingreso Directo \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 28356 | I162S2C10J2V1 | TNS en Prevención de Riesgos | Vespertino | INFORMAR_CNED_CON_REVISION | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. | Año Inicio Actividades antiguo sin matricula reciente observada |
| 29354 | I162S2C22J2V1 | Ing. Ejec. en Minería y Operaciones de Planta | Vespertino | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29348 |  | Ing. Ejec. en Automatización y Control Industrial | Vespertino | DUPLICADO_O_AMBIGUO | Coincidencia difusa con multiples codigos/candidatos posibles. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 40712 | I162S2C48J4V1 | TNS en Control Industrial | Otro | INFORMAR_CNED_CON_REVISION | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. | No presencial u Horario Otro \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 32513 | I162S2C11J2V1 | TNS en Automatización y Control Industrial | Vespertino | INFORMAR_CNED_CON_REVISION | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. | Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 32512 | I162S2C22J2V1 | Ingeniería  en Automatización y Control Industrial | Vespertino | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 6679 | I162S2C3J1V2 | Ingeniería en Conectividad y Redes | Diurno | INFORMAR_CNED_CON_REVISION | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. | Año Inicio Actividades antiguo sin matricula reciente observada |
| 32511 | I162S2C11J1V1 | TNS en Automatización y Control Industrial | Diurno | INFORMAR_CNED_CON_REVISION | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. | Codigo SIES duplicado en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 32515 | I162S2C22J1V1 | Ingeniería en Automatización y Control Industrial | Diurno | INFORMAR_CNED_CON_REVISION | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 36742 | I162S2C2J4V1 | TNS en Programación Computacional | Otro | DUPLICADO_O_AMBIGUO | La llave de codigo encuentra mas de un codigo/candidato en bases locales. | No presencial u Horario Otro \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 51507 | I162S2C77J1V1 | Ingeniería en Logística | Diurno | INFORMAR_CNED_CON_REVISION | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. |  |
| 51511 | I162S2C79J1V1 | TNS en Logística | Diurno | INFORMAR_CNED_CON_REVISION | Codigo exacto aparece en oferta/catalogo/puente, pero sin matricula observada en las bases usadas. |  |

## 8. Carreras sin código o con código faltante

| Cod.Carr. | Codigo SIES | Nombre Programa | Horario | categoria_final | motivo | flags_validacion |
| --- | --- | --- | --- | --- | --- | --- |
| 43934 |  | Ingeniería en Ciberseguridad (P.E.) | Otro | DUPLICADO_O_AMBIGUO | Coincidencia difusa con multiples codigos/candidatos posibles. | Codigo SIES vacio en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| No presencial u Horario Otro \| No es Ingreso Directo \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 38816 | I162S2C3J4V2 | Ingeniería en Conectividad y Redes | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 40876 | I162S2C1J4V2 | Ingeniería en Informática (P.E.) | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | Programa Especial \| No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 40716 | I162S2C46J2V3 | Ingeniería en Ciberseguridad (P.E.) | Vespertino | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 48339 | I162S2C22J4V1 | Ingeniería en Automatización y Control Industrial | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 51505 | I162S2C76J4V1 | Ingeniería en Administración de Empresas | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 51502 | I162S2C22J4V2 | Ingeniería en Automatización y Control Industrial  (P.E.) | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | Programa Especial \| No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 45921 |  | Ingeniería en Ciberseguridad | Otro | NO_INFORMAR_CODIGO_FALTANTE | El programa aparece por llaves normalizadas, pero Codigo SIES esta vacio en el listado CNED. | Codigo SIES vacio en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| No presencial u Horario Otro |
| 53717 | I162S2C83J4V1 | Administración Pública | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 53724 |  | Naturopatía (P.E.) | Vespertino | NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | Sin Codigo SIES y sin evidencia suficiente en las bases revisadas. | Codigo SIES vacio en listado CNED \| Programa Especial \| No es Ingreso Directo |
| 43929 | I162S2C46J4V1 | Ingeniería en Ciberseguridad (P.E.) | Otro | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| No presencial u Horario Otro \| No es Ingreso Directo \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 43933 | I162S2C46J4V1 | Ingeniería en Ciberseguridad | Otro | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Programa Especial \| No presencial u Horario Otro \| No es Ingreso Directo \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 28353 |  | TNS en Minería y Operaciones de Planta | Vespertino | NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | Sin Codigo SIES y sin evidencia suficiente en las bases revisadas. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 28354 | I162S2C11J1V1 | TNS en Minería y Operaciones de Planta | Diurno | NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | No aparece evidencia suficiente en las bases revisadas. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29353 | I162S2C22J1V1 | Ing. Ejec. en Minería y Operaciones de Planta | Diurno | NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | No aparece evidencia suficiente en las bases revisadas. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29354 | I162S2C22J2V1 | Ing. Ejec. en Minería y Operaciones de Planta | Vespertino | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29351 |  | Ing. Ejec. en Automatización y Control Industrial | Diurno | NO_INFORMAR_CODIGO_FALTANTE | Solo hay similitud difusa y Codigo SIES esta vacio. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29348 |  | Ing. Ejec. en Automatización y Control Industrial | Vespertino | DUPLICADO_O_AMBIGUO | Coincidencia difusa con multiples codigos/candidatos posibles. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29352 |  | Ing. Ejec. en Prevención de Riesgos | Diurno | NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | Sin Codigo SIES y sin evidencia suficiente en las bases revisadas. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29347 |  | Ing. Ejec. en Prevención de Riesgos | Vespertino | NO_INFORMAR_SIN_MATRICULA_O_SIN_EVIDENCIA | Sin Codigo SIES y sin evidencia suficiente en las bases revisadas. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29349 |  | TNS en Automatización y Control Industrial | Diurno | NO_INFORMAR_CODIGO_FALTANTE | Solo hay similitud difusa y Codigo SIES esta vacio. | Codigo SIES vacio en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 29350 |  | TNS en Automatización y Control Industrial | Vespertino | NO_INFORMAR_CODIGO_FALTANTE | Solo hay similitud difusa y Codigo SIES esta vacio. | Codigo SIES vacio en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 28355 |  | TNS en Prevención de Riesgos | Diurno | NO_INFORMAR_CODIGO_FALTANTE | Solo hay similitud difusa y Codigo SIES esta vacio. | Codigo SIES vacio en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 42539 | I162S2C3J4V3 | Ingeniería en Conectividad y Redes (P.E.) | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | Programa Especial \| No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 32512 | I162S2C22J2V1 | Ingeniería  en Automatización y Control Industrial | Vespertino | DUPLICADO_O_AMBIGUO | Codigo SIES duplicado en el listado de referencia CNED. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 32511 | I162S2C11J1V1 | TNS en Automatización y Control Industrial | Diurno | INFORMAR_CNED_CON_REVISION | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. | Codigo SIES duplicado en listado CNED \| Mismo Nombre Programa y mismo Horario repetido en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 32515 | I162S2C22J1V1 | Ingeniería en Automatización y Control Industrial | Diurno | INFORMAR_CNED_CON_REVISION | Solo hay coincidencia difusa de nombre; no se considera match automatico definitivo. | Codigo SIES duplicado en listado CNED \| Año Inicio Actividades antiguo sin matricula reciente observada |
| 34541 | I162S2C3J2V3 | Ingeniería en Conectividad y Redes (P.E.) | Vespertino | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | Programa Especial \| Codigo asociado a nombres similares o distintos en fuentes locales |
| 51509 | I162S2C77J4V1 | Ingeniería en Logística | Otro | INFORMAR_CNED_CON_TRAZABILIDAD_ALTA | Codigo SIES/CODIGO_UNICO exacto con evidencia en matricula o archivo listo. | No presencial u Horario Otro \| Codigo asociado a nombres similares o distintos en fuentes locales |

## 9. Riesgos

* CNED se carga 1 a 1.
* Riesgo de informar programas sin código trazable.
* Riesgo de duplicar programas por jornada/modalidad.
* Riesgo de confundir “Otro” con modalidad no presencial.
* Riesgo de usar solo nombre sin código.
* Diferencias entre oferta, matrícula y bases SIES.

## 10. Recomendación operativa

1. Primero carreras con trazabilidad alta y código completo.
2. Luego carreras con revisión, previa validación manual.
3. No cargar programas con código faltante o ambiguo sin confirmar.

## 11. Punto exacto para reanudar

PUNTO EXACTO PARA REANUDAR:
Revisar la hoja CARRERAS_A_INFORMAR del archivo CNED_carreras_a_informar_comparacion.xlsx y comenzar carga manual en CNED solo con registros de trazabilidad alta.

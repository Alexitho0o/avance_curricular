# Informe de gobernanza corregido por ID_FILA_5809

## Contexto

- Proceso: Avance Curricular SIES 2026
- Subproyecto: Matrícula 5809
- Año de referencia: 2025
- Archivo base: REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx

## Corrección metodológica

El diagnóstico anterior por RUT detectó 33 RUT únicos, porque el expediente contiene distintos campos de RUT: RUT 5809, RUT evidencia y RUT formateado. Para evitar inflar el universo, el diagnóstico final se reconstruyó usando `ID_FILA_5809` como llave principal de caso.

## Resultado ejecutivo

- Universo corregido por ID_FILA_5809: **29 casos**
- Casos adecuados por CODCLI y reporte: **2**
- Casos pendientes: **27**
- Rechazos iniciales revocados: **2**
- Rechazos definitivos demostrados: **0**

## Estados finales

| ESTADO_GOBERNANZA_FINAL         |   CASOS |
|:--------------------------------|--------:|
| PENDIENTE_DEBIL_NO_CONVERTIR    |      19 |
| PENDIENTE_SIN_MODELO_DEMOSTRADO |       8 |
| ADECUADO_POR_CODCLI_Y_REPORTE   |       2 |

## Decisiones finales

| DECISION_FINAL_GOBERNANZA   |   CASOS |
|:----------------------------|--------:|
| MANTENER_PENDIENTE          |      27 |
| REVOCAR_RECHAZO_INICIAL     |       2 |

## Interpretación funcional

El archivo original de rechazados y pendientes debe tratarse como un estado preliminar. La gobernanza posterior revocó técnicamente los rechazos de los casos con adecuación demostrada por CODCLI exacto y reporte individual. Los demás casos permanecen pendientes; no corresponde convertirlos por similitud de carrera, familia CODCLI o nivel dentro de rango.

## Archivos

- Excel: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/04_gobernanza_mallas/03_auditorias/DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA_20260703_222022/02_RESULTADOS/DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA.xlsx`
- TSV: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/04_gobernanza_mallas/03_auditorias/DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA_20260703_222022/02_RESULTADOS/01_DIAGNOSTICO_FINAL_29_POR_ID_FILA.tsv`
- Carpeta: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/04_gobernanza_mallas/03_auditorias/DIAGNOSTICO_GOBERNANZA_29_CORREGIDO_POR_ID_FILA_20260703_222022`

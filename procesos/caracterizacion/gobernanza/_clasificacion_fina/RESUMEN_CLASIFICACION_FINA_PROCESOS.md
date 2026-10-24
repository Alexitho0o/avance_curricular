# Clasificación fina de procesos — Proyecto CARACTERIZACIÓN

Fecha: 2026-05-13 16:10:15

Fuente: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/_mapeo_proyecto/MAPEO_ARCHIVOS_PROYECTO_CARACTERIZACION.tsv`

## Salidas

- Excel: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.xlsx`
- TSV: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.tsv`
- JSON: `/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/_clasificacion_fina/CLASIFICACION_FINA_PROCESOS_CARACTERIZACION.json`

## Propuesta de paquetes de gobernanza

| proceso               | carpeta_sugerida                 | alcance                                                                        |   archivos_detectados |   candidatos_formales |   scripts |   excel |   csv_tsv |   json |   md_txt |   hash | recomendacion                           |
|:----------------------|:---------------------------------|:-------------------------------------------------------------------------------|----------------------:|----------------------:|----------:|--------:|----------:|-------:|---------:|-------:|:----------------------------------------|
| FCU_CARGA_PES         | gobernanza/fcu_carga_pes         | Carga oficial PES, CSV validado, auditorías E2E, hash, dictamen.               |                     9 |                     8 |         1 |       3 |         2 |      0 |        3 |      0 | CREAR_PAQUETE_GOBERNANZA                |
| FCU_ANALISIS_ENCUESTA | gobernanza/fcu_analisis_encuesta | Encuesta/LimeSurvey, SEP_TODAS, preguntas no FCU, sustentabilidad, reglas KPI. |                     2 |                     2 |         0 |       1 |         0 |      0 |        1 |      0 | CREAR_PAQUETE_GOBERNANZA                |
| ANALISIS_TRAYECTORIA  | gobernanza/analisis_trayectoria  | Trayectoria, perfil de ingreso, KPI y archivos analíticos derivados.           |                    12 |                     1 |         6 |       0 |         0 |      0 |        5 |      0 | CREAR_PAQUETE_GOBERNANZA                |
| MATRICULA_UNIFICADA   | gobernanza/matricula_unificada   | Solo evidencias de MU si corresponden a este repositorio.                      |                    31 |                     1 |        10 |       1 |         3 |      5 |       12 |      0 | CREAR_PAQUETE_GOBERNANZA                |
| CARGA_POSTGRADO       | gobernanza/carga_postgrado       | Solo si existen evidencias reales dentro del repositorio.                      |                     0 |                     0 |         0 |       0 |         0 |      0 |        0 |      0 | DOCUMENTAR_COMO_NO_LOCALIZADO_O_REVISAR |
| GOBERNANZA_META       | gobernanza/_meta                 | Mapeos, clasificación fina, auditorías de gobernanza transversal.              |                     1 |                     1 |         0 |       1 |         0 |      0 |        0 |      0 | CREAR_PAQUETE_GOBERNANZA                |

## Resumen por proceso

| proceso_fino          | tipo          |   cantidad |
|:----------------------|:--------------|-----------:|
| ANALISIS_TRAYECTORIA  | SCRIPT_CODIGO |          6 |
| ANALISIS_TRAYECTORIA  | DOCUMENTACION |          5 |
| ANALISIS_TRAYECTORIA  | CONFIG        |          1 |
| FCU_ANALISIS_ENCUESTA | DOCUMENTACION |          1 |
| FCU_ANALISIS_ENCUESTA | EXCEL         |          1 |
| FCU_CARGA_PES         | DOCUMENTACION |          3 |
| FCU_CARGA_PES         | EXCEL         |          3 |
| FCU_CARGA_PES         | TABLA_PLANA   |          2 |
| FCU_CARGA_PES         | SCRIPT_CODIGO |          1 |
| FCU_SCRIPT_AUXILIAR   | SCRIPT_CODIGO |         18 |
| GOBERNANZA_META       | EXCEL         |          1 |
| MATRICULA_UNIFICADA   | DOCUMENTACION |         12 |
| MATRICULA_UNIFICADA   | SCRIPT_CODIGO |         10 |
| MATRICULA_UNIFICADA   | JSON          |          5 |
| MATRICULA_UNIFICADA   | TABLA_PLANA   |          3 |
| MATRICULA_UNIFICADA   | EXCEL         |          1 |
| SIN_CLASIFICAR        | SCRIPT_CODIGO |       5202 |
| SIN_CLASIFICAR        | DOCUMENTACION |         98 |
| SIN_CLASIFICAR        | TABLA_PLANA   |         60 |
| SIN_CLASIFICAR        | OTRO          |         54 |
| SIN_CLASIFICAR        | JSON          |         10 |
| SIN_CLASIFICAR        | CONFIG        |          3 |
| SIN_CLASIFICAR        | WORD          |          3 |

## Lectura recomendada

1. Revisar primero `PROPUESTA_PAQUETES`.
2. Revisar `CANDIDATOS_FORMALES` para ver qué evidencias pasarán a cada paquete.
3. No mover todavía archivos productivos; el próximo paso es crear paquetes de gobernanza por proceso con copias controladas.
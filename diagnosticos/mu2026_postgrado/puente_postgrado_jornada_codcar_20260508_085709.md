# Puente postgrado jornada/COD_CAR · MU2026

Fecha ejecución: Fri May  8 08:57:09 -04 2026
Archivo fuente: /Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx

## 1. Resumen

- Programas postgrado en matriz: 22
- Candidatos postgrado en DatosAlumnos: 462

## 2. Jornadas observadas

### DatosAlumnos

| Jornada fuente | n |
|---|---:|
| O | 457 |
| V | 5 |

### matriz

| Jornada matriz | n |
|---|---:|
| 4 | 19 |
| 2 | 2 |
| 3 | 1 |

## 3. Cruce por nombre de programa sin jornada


- Filas con match por nombre: 81
- CODCLI únicos con match por nombre: 81
- Filas sin match por nombre: 381

### Programas cruzados por nombre

| Programa | n |
|---|---:|
| DIPLOMADO EN CIBERSEGURIDAD APLICADA | 31 |
| DIPLOMADO EN FULLSTACK | 19 |
| DIPLOMADO EN ARQUITECTURA CLOUD | 13 |
| DIPLOMADO EN INTELIGENCIA ARTIFICIAL | 5 |
| DIPLOMADO EN QUALITY ASSURANCE | 5 |
| DIPLOMADO EN SUPPLY CHAIN MANAGEMENT Y MINERIA DE REQUERIMIENTOS | 3 |
| DIPLOMADO EN GOBERNANZA DE DATOS | 3 |
| DIPLOMADO EN SALUD FAMILIAR CON ENFOQUE COMUNITARIO | 1 |
| DIPLOMADO EN SEGURIDAD OFENSIVA | 1 |

### Equivalencia observada DatosAlumnos.JORNADA → matriz.JORNADA

| Jornada DatosAlumnos | Jornada matriz | n |
|---|---|---:|
| O | 4 | 50 |
| O | 3 | 26 |
| V | 3 | 5 |

## 4. Registros 2026 con match por nombre

- Filas 2026 con match por nombre: 0
- CODCLI únicos 2026 con match por nombre: 0

## 5. Programas candidatos sin match por nombre

| Programa DatosAlumnos | CODCARPR | Jornada | n |
|---|---|---|---:|
| EC CURSOS Y DIPLOMADOS | ECCURYDP | O | 237 |
| DIPLOMADO EN CIBERSEGURIDAD | DCBS | O | 34 |
| DIPLOMADO EN REDES INDUSTRIALES | DREIN | O | 22 |
| DIPLOMADO EN REDES INDUSTRIALES  | DRID | O | 17 |
| DIPLOMADO EN FULL STACK | DFSCK | O | 15 |
| DIPLOMADO EN DATA SCIENCE | DDSC | O | 13 |
| DIPLOMADO EN INFRAESTRUCTURA CLOUD  | DICD | O | 11 |
| DIPLOMADO EN DATA SCIENCE | DDASC | O | 11 |
| DIPLOMADO EN CIBERSEGURUDAD INDUSTRIAL | DCSI | O | 5 |
| DIPLOMADOS EN HABILIDADES DIRECTIVAS | DHDS | O | 4 |
| DIPLOMADO HERRAMIENTAS DE IA PARA EL APOYO DOCENTE | DHIAD | O | 4 |
| DIPLOMADO DESARROLLO SEGURO DE SOFTWARE | DDSS | O | 2 |
| DIPLOMADO EN ANALYTICS Y VISUALIZACIÓN DE DATOS CON POWER BI | DAPB | O | 2 |
| DIPLOMADO EN GESTIÓN ÁGIL CON SCRUM | DGAS | O | 2 |
| DIPLOMADO LIDERAZGO ESTRATÉGICO Y MANAGEMENT 4.0  | DLEMS | O | 2 |

## 6. Recomendación técnica

Si el match por nombre cruza registros 2026, usar matriz como fuente oficial de COD_SED, COD_CAR, MODALIDAD, JOR y VERSION.
La jornada de DatosAlumnos debe conservarse solo como fuente de auditoría; para PES se debe usar la jornada codificada de matriz.
Si hay programas sin match por nombre, crear puente manual CODCARPR/CODIGOCARRERA → CODIGO_UNICO antes de generar PES-ready.

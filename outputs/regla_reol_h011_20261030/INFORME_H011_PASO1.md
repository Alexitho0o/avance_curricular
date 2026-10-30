# H011 · Paso 1 y reanudaciones

**Estado vigente.** Alexi retiró la premisa sobre RE/CO en la segunda reanudación. El criterio (c) está acreditado. El régimen S/A es del ramo. RE/CO indican sede y la oferta acredita modalidad. Las paradas descritas debajo corresponden a las dos verificaciones previas. El resultado final se encuentra en INFORME_H011.md.

**Estado: DETENIDO ANTES DEL PASO 2.** Clase B/C para las observaciones; E para el criterio (c). No se aplican D4, D5 ni D6; no se construye catálogo v3 ni se altera la candidata v21.

## Criterios

| Criterio | Resultado | Evidencia |
|---|---|---|
| a | CUMPLE_B_C | 22 planes/23 combinaciones tienen candidatos H002 no presenciales; no implica equivalencia única. |
| b | CUMPLE_OBSERVACION_B_C | Todos los registros REOL leídos indican BIMESTRAL; hay secuencias 1–5 del mismo expediente, plan y año; no se observa 6. No acredita fechas de inicio/término. |
| c | NO_ACREDITADO_E | El listado institucional usa REGIMEN S para los 22 planes; H002c no acredita qué significa S/A. No se afirma S=SEMESTRAL ni contradicción confirmada, pero no se puede descartar incompatibilidad con BIMESTRAL sin definir ámbito y significado. |

## Qué se verificó

- 22 planes REOL, 23 combinaciones carrera/plan/sede/jornada presentes en el residual. Todos tienen candidatos H002 de modalidad No presencial. Atributos por código y año en EVIDENCIA_PASO1_REOL.json → familias_y_oferta.
- Los 22 planes sí están en Listado_Planes_estudio_Sedes RE+CO.xlsx, hoja BBDD Bruta: REGIMEN S; TIPO Obl/OPC no es tipo de plan SIES.
- PROMEDIOS: 2836 combinaciones expediente–plan–año con 4/5; 2586 también tienen 1/2/3; 2108 tienen secuencia completa 1,2,3,4,5. Período 6: 0. Conjuntos sin duplicar entre extractos; no son contextos ni personas únicas.
- Reutilización H010b: los 604 históricos incluyen 598 BIMESTRAL REOL y 6 no REOL (3 SEMESTRAL y 3 TRIMESTRAL). No son 604 REOL.

## Límite que impide aceptar la conclusión universal

No se interpreta S como semestral: su significado no está acreditado, tal como documentó PERFIL_PLANES_H002C.md, párrafo inicial. Por tanto, la incompatibilidad con BIMESTRAL no está confirmada, pero el criterio de ausencia de contradicción tampoco queda acreditado. Se necesita definir el alcance de los dos campos, no elegir uno por preferencia.

Además, los candidatos de IECIREOL (sus cuatro planes), NCONREOL2019 y NINFREOL2019 incluyen tipos SIES regular y continuidad. Modalidad no presencial no demuestra por sí sola REGULAR. Esto no adjudica esos planes ni cambia H002.

Requisito: Catálogo o confirmación UMAS que defina REGIMEN=S en BBDD Bruta y su relación con REGIMEN=BIMESTRAL de PROMEDIOS. No basta el nombre REOL. Los perfiles regulares/continuidad múltiples deben conservarse separados.

## Cobertura conservada

| Universo | Antes H010b | Después de esta verificación | Residual E |
|---|---:|---:|---:|
| 3.049 contextos | 2.085 respaldados | 2.085 | 964 |
| 99 posiciones | 99 respaldadas | 99 | 0 |

Residual histórico reutilizado, sin reclasificar: 604 períodos 4/5; 273 tipo/duración E; 48 T1 previo sin posterior; 28 sin VIGENCIA 1 compatible; 6 primer T1 ambiguo/dimensiones distintas; 2 sin código anual compatible; 2 varias VIGENCIA 1; 1 ambigüedad anual. Fuente: COBERTURA_H010B.json y RESIDUAL_H010B.json.

v20 activo y v21 candidata intactos. R01–R04 y R19 sin cambios: 0,00 pp por conservación, sin recálculo. Excel no se abrió. No se actualizaron mapa ni reglas: la condición de avance no quedó acreditada. No se hace commit/push con el mensaje de asignación porque no hubo asignaciones.

## Fuentes verificadas

| Fuente | SHA-256 |
|---|---|
| /Users/alexi/Documents/GitHub/avance_curricular/data/diccionario_umas/DICCIONARIO_UMAS.json | f05ac03aa8ca0ec6cf5f754cbaacebac630b2a3346ff592d7ee0b181b82e8811 |
| /Users/alexi/Documents/GitHub/avance_curricular/data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json | 0ed5e17b1a452c85ab25b08ef0e65cdfc7258fd920d0f4dd40c60c9c4eb71063 |
| /Users/alexi/Documents/GitHub/avance_curricular/data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json | 2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5 |
| /Users/alexi/Documents/GitHub/avance_curricular/outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.md | cdea2d8d6d5c8dadca87bc91205e26bbba3d8fc8416ac422b5daa65e44c3105c |
| /Users/alexi/Documents/GitHub/avance_curricular/outputs/regla_t1_h010_20261030/PERIODOS45_H010B.json | 876caa820c5b69955dd83e89b03fcfa5150ff9f1a2caf93de20bbcb5f408aa81 |
| /Users/alexi/Documents/GitHub/avance_curricular/outputs/regla_t1_h010_20261030/RESIDUAL_H010B.json | 7420113871dc4e8f6cbdd980b8ea465b7be0f45a4ed5ad70f303715dcb18f4a3 |
| /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026/Listado_Planes_estudio_Sedes RE+CO.xlsx | fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049 |
| /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_12166.xlsx | aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015 |
| /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_2071.xlsx | 348d1807381e545425c0f204c7321172a522718dec829dd9a60bf5dd07e45ef1 |
| /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_3233.xlsx | b1f2e395b9c5fbbd20e2a99f9e652843c24d2d743d3c9a2901303c4a06b0a25e |
| /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_7804.xlsx | 83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca |
## Reanudación del Paso 1c

**B/C.** La hoja BBDD Bruta registra 11.228 filas de asignatura con S y 210 con A. ADMP20251 tiene 65 filas S, mientras PROMEDIOS registra TRIMESTRAL para ese plan. Esto corrige el motivo de la parada inicial. El campo del ramo puede coexistir con un calendario bimestral o trimestral.

**B/C.** La partición numérica 9.019 / 277 / 1.932 se reproduce sobre Codcarr separando primero REOL y luego cualquier aparición de CO. Al contrastar esos 277 ramos con el tipo v2 por carrera, plan y sede, 169 pertenecen a planes REGULAR y 108 tienen tipo E. Ninguno está clasificado CONTINUIDAD. El detalle agregado y los hashes están en EVIDENCIA_PASO1_REOL.json → reanudacion_paso1c.

**Parada del encargo.** El punto 2 queda confirmado. El punto 1 sólo se confirma como partición de texto. Falta una clave gobernada que identifique las 277 filas de continuidad, o una decisión revisada que prescinda de esa premisa. Cobertura H010b vigente, 2.085 de 3.049 y 99 de 99. No hay nuevas asignaciones ni commit.

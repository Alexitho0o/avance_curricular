# Verificación UMAS de los enlaces anuales existentes

B/C — No se modificaron asignaciones, fuentes ni denominadores. Los conteos siguientes describen el índice v8 disponible; no sustituyen la comprobación anual hoja9→MU del libro, que reprodujo2379/2379.

| Cohorte | Filas originales | Identidad/año/código en índiceMU | Contexto nativo1 único con mismo código | Sin contexto1 | Contexto1 sin código igual | Sin índiceMU |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 305 | 305 | 255 | 49 | 1 | 0 |
| 2023 | 366 | 366 | 362 | 1 | 3 | 0 |
| 2024 | 558 | 558 | 459 | 66 | 33 | 0 |
| 2025 | 1150 | 1132 | 850 | 272 | 10 | 18 |

E — Los1926 contextos concordantes son enlaces existentes de identidad, expediente, plan, año y período nativo1, con código adoptado igual al anual. La fecha efectiva histórica del plan y la aceptación SIES no se vuelven acreditadas por esta comparación. No se presenta este conteo como un cierre nuevo.

## Ejemplos reales sin identificadores personales

### Ejemplo A

B/C — Cohorte2022, período nativo1: UMAS `TPAREOL`; plan `TPAREOL20211`; sede `RE`; jornada `O` → `I162S2C57J4V1`. Componentes SIES: institución162, sede2, carrera57, jornada4, versión1.
B/C — Libro original: hoja9 fila7 → hoja11 fila8. Código y expediente ya atribuidos por `IDENTIDAD_FAMILIA_ANIO_CONTEXTO_DA_NO_MULTIPLE`. No es asignación nueva.
- B/C: `/Users/alexi/Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx`, hoja `Hoja1`, fila5201; SHA-256 `a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9`.
- B/C: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx`, hoja `Hoja1`, fila30570; SHA-256 `aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015`.
- B/C: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`, hoja `BASE_RETENCION_MU`, fila5; SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
E — `Asignación histórica efectiva del plan y aceptación SIES no acreditadas; código observado/interno separado`.

### Ejemplo B1

B/C — Cohorte2025, período nativo1: UMAS `IINF`; plan `IINF20241`; sede `RE`; jornada `D` → `I162S2C1J1V1`. Componentes SIES: institución162, sede2, carrera1, jornada1, versión1.
B/C — Libro original: hoja9 fila1262 → hoja11 fila3769. Código y expediente ya atribuidos por `IDENTIDAD_FAMILIA_ANIO_CONTEXTO_DA_NO_MULTIPLE`. No es asignación nueva.
- B/C: `/Users/alexi/Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx`, hoja `Hoja1`, fila8584; SHA-256 `a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9`.
- B/C: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx`, hoja `Hoja1`, fila40924; SHA-256 `aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015`.
- B/C: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`, hoja `BASE_RETENCION_MU`, fila3766; SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
E — `Asignación histórica efectiva del plan y aceptación SIES no acreditadas; código observado/interno separado`.

### Ejemplo B2

B/C — Cohorte2025, período nativo1: UMAS `IINF`; plan `IINF20241`; sede `RE`; jornada `D` → `I162S2C1J1V2`. Componentes SIES: institución162, sede2, carrera1, jornada1, versión2.
B/C — Libro original: hoja9 fila1239 → hoja11 fila3743. Código y expediente ya atribuidos por `IDENTIDAD_FAMILIA_ANIO_CONTEXTO_DA_NO_MULTIPLE`. No es asignación nueva.
- B/C: `/Users/alexi/Desktop/Caracterizacion_2026-10-22_2027_P1_084218/01_ENTRADAS/DATOSDEALUMNOS_12159.xlsx`, hoja `Hoja1`, fila8563; SHA-256 `a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9`.
- B/C: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx`, hoja `Hoja1`, fila39912; SHA-256 `aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015`.
- B/C: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx`, hoja `BASE_RETENCION_MU`, fila3740; SHA-256 `19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd`.
E — `Asignación histórica efectiva del plan y aceptación SIES no acreditadas; código observado/interno separado`.

C — Reproducir con verificar_umas.py en una salida nueva. RESULTADOS.json conserva campos verificables y hashes; no contiene RUT, CODCLI personales ni nombres.

E — Los ejemplos B1/B2 muestran coexistencia de versiones en la misma familia de Informática y año. El código de cada persona se conserva desde su evidencia anual; no se generaliza una versión a toda la carrera.

## QA complementario de API y dimensiones

B/C — De los1.926 contextos con código adoptado igual,1.920 coinciden además en sede y jornada;6 muestran discordancia. Estos6 no se presentan como expediente plenamente conciliado. Los1.926 comprenden1.918 atribuciones documentales anuales y8 correspondencias internas ya aprobadas.

C — La API común consultar devolvió REUTILIZABLE y el mismo código en los tres subcasos, ediciónv8_20261025_ocho_p. En cada ejemplo, DATOS ALUMNOS y PROMEDIOS contienen el mismo CODCLI literal y la misma identidad; MU conserva esa identidad completa y los componentes del código SIES. Se verificó en memoria, sin publicar identificadores. No se exigió una prueba de envío para comprobar este enlace interno.

| Ejemplo | Año/período PROMEDIOS | Régimen | Nivel de asignatura | Ramo | Estado | Convalidado |
|---|---|---|---|---|---|---|
| Ejemplo A | 2022/1 | BIMESTRAL | 1 | AS11TPAREOL · HABILIDADES PARA EL APRENDIZAJE DIGITAL | A · APROBADO | Vacío en fuente |
| Ejemplo B1 | 2025/1 | TRIMESTRAL | 1 | AT100IINF · RESOLUCIÓN DE PROBLEMAS I | A · APROBADO | Vacío en fuente |
| Ejemplo B2 | 2025/1 | TRIMESTRAL | 1 | AT100IINF · RESOLUCIÓN DE PROBLEMAS I | A · APROBADO | Vacío en fuente |

B/C/E — NIVEL se presenta tal como está en la asignatura observada; no se convierte automáticamente en trimestre de avance ni duración del programa. ANOMATRICULA del corte DA puede ser posterior al año de PROMEDIOS: se conservan ambas fechas, sin igualarlas.

B/E — La MU leída es una base anual derivada. Sus33columnas no contienen ARCHIVO_ORIGEN, FUENTE, HOJA ni FILA_ORIGEN. Las referencias5/3766/3740 localizan filas del consolidado, sin certificar fila RAW primaria, envío ni retornoSIES. Esto no invalida el enlace interno comprobado por identidad.

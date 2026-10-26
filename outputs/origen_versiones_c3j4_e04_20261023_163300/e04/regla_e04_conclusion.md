# E04 — procedencia observada de V1 en MU2025

Proceso: seguimiento intertrimestral IPSS 162; revisión del código anual de Informática, IINF20241, sede 2 y jornada 1. Años contrastados 2024–2026; preparación MU2025. Auditoría de lectura, sin adjudicación, corrección ni modificación de denominadores.

**B/C.** Se releyeron 17 libros del inventario gobernado de preparación MU2025. Se recuperaron 32 filas relacionadas con la identidad de E04; diez contienen VERSION y todas conservan el número 1 sin fórmula en esa celda. No son diez confirmaciones independientes: incluyen copias y transformaciones de una misma preparación.

**B.** El punto más anterior localizable dentro de la preparación examinada es `IPSS_Procesamiento.xlsx`, `Precarga!Q1025`: valor numérico literal 1, sin fórmula, comentario ni hipervínculo. La fila conserva `FECH_CAR=2025-04-16 11:50:07`. Este campo no se interpreta como fecha de cambio de plan ni como prueba del orden cronológico de edición de las hojas.

| Fuente | Hoja/celda o fila | Dato | Clase |
|---|---|---|---|
| CSV RAW2024, también conservado en respaldo incremental | CSV, fila 470 | J1V2, ingreso actual/origen 2024 | B |
| IPSS_Procesamiento.xlsx | Precarga!P1025/Q1025 | J1/V1, literal | B |
| IPSS_Procesamiento.xlsx | Carga_Completa, fila 1027 | J1/V1, literal | B |
| IPSS_Procesamiento.xlsx | Carga_Completa (2)/(3), fila 1032 | J1/V1, literal | B |
| IPSS_Procesamiento.xlsx | Final a carga, fila 1004 | J1/V1, literal | B |
| IPSS2025.xlsx | Hoja1!N1004/O1004 | J1/V1, literal | B |
| Descarga de lo cargado_08-05-2025_22-26-22_Matrícula_Pregrado_2025.xlsx | Hoja granular, fila 1020 | J1/V1, FECH_CAR 08-may-2025 | B |
| Matrícula_Pregrado_SIES_2025.xlsx | Hoja granular, fila 867 | J1/V1 | B |

**B/C.** La hoja `2025_carga` no contiene esta identidad; `2025_Total` sí la contiene en la fila 591, como IINF, jornada D e ingreso 2024. El expediente se recupera además en `2025-2.xlsx`, Hoja1, fila 493. Estas filas UMAS no contienen una equivalencia explícita que establezca V1 para IINF20241.

**B.** No se encontró dentro de IPSS_Procesamiento una fórmula que apunte a Mapa o VERSION, ni objetos connections, queryTables o VBA. Los vínculos externos observados apuntan a PROMEDIOSDEALUMNOS_2071.xlsx. La hoja Mapa distingue carrera/componente C: su valor 1 no constituye una regla VERSION=1. `Formati_SIES_2025.xlsx`, hoja Formato, no contiene fórmulas ni aporta una coincidencia exacta de identidad que permita atribuir allí la V1.

**B/C.** Los archivos incremental XLSX y CSV denominados 02-01-2025 no contienen la identidad exacta. El CSV sin encabezados fue leído con sus 32 posiciones contrastadas con la hoja 1 del XLSX. Esta ausencia no prueba retiro ni una cobertura completa del cierre.

## Patrón del lote, sin atribución causal

**B/C.** Precarga contiene 22 filas C1/J1/sede 2: 14 V2 y ocho V1. Las ocho V1 tienen FECH_CAR del 16-abr-2025: seis a las 10:57:08 y dos a las 11:50:07, incluidas E04. Existe también una V2 del 16-abr a las 09:25:00, por lo que ni siquiera la fecha del día define una regla universal. Las otras V2 tienen registros de enero/febrero.

**B/C.** Al comparar la misma identidad y familia C1/J1 con RAW2024: siete filas conservan V2; una pasa de V2 a V1 (E04); catorce no tienen antecedente de esa misma familia en el RAW2024 (siete V1 y siete V2). No se extrapola ausencia de familia a ausencia de matrícula institucional.

**E.** El patrón acota la búsqueda al proceso que produjo o incorporó el lote del 16-abr-2025 antes de Precarga. No demuestra que existiera una regla de versión por lote, una corrección ministerial o un error de asignación. La fórmula, consulta o decisión que generó el literal V1 no quedó localizada en los libros examinados.

**E.** La secuencia anual V2→V1→V2 no se convierte automáticamente en una migración de plan ni en un error SIES. Se conserva el código documentado de cada año. No se adopta un criterio nuevo.

## Reproducción y evidencias

- `/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/rastrear_regla_e04.py` → `/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_preparacion.json`.
- `/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/regla_e04_incremental.py` → `/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_incremental.json`.
- `/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/regla_e04_grupo_precarga.py` → `/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_grupo_precarga.json`.
- Los JSON contienen rutas originales, hojas, filas, fórmulas observadas, hashes e inventario. Los identificadores permanecen solo en la ubicación privada de revisión.
- `IPSS_Procesamiento.xlsx`: SHA-256 `e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4`.
- RAW2024: SHA-256 `5cd5c664b303301bc4e1c5f910c708c1d68e78465eebe3002364a07ea8e4a068`.

**C.** No se ejecutó ningún pipeline, commit, push, modificación del diccionario, base o denominador. La búsqueda global de scripts/SQL/Git se integra por separado con la revisión del agente principal; esta nota no afirma agotarla.

# Revisión de 0 BASES DE DATOS para titulación · 26-10-2026

**[B/C] Alcance:** carpeta indicada por Alexi en OneDrive, para el caso de Titulación Unificada 2026 cuyo título se observa en 2025. Se inventariaron nombres y se revisaron las estructuras y fuentes descritas abajo. La coincidencia individual se realizó solamente en memoria por CODCLI y RUT con DV. No se intentó un cruce RUT–MRUN.

| Fuente [B] | SHA-256 | Resultado [B/C] |
|---|---|---|
| `base de datos 1900-2026.xlsx`, `Hoja1` | `6b6cb8d515f3ac1eef9e94ebf005c3ac014c76f506294a3881b6e8ef80b55c03` | 13.308 filas de datos, 67 columnas. Se localizaron los tres CODCLI conocidos del caso con el mismo RUT y DV; las tres filas coinciden con el respaldo previamente revisado en ocho campos de carrera, estado, situación, ingreso, matrícula y jornada. Dos figuran ELIMINADO y una TITULADO. No se localizaron columnas de plan o de título/fecha de título. |
| `TITULACION/TITULADO_2025_web_27_05_2026_E.xlsx`, `in` | `2cdf4b606cfddf71e000043166d9c23a6d15992c2819954946d05819603ba46b` | Estructura agregada de 42 columnas, incluida `TOTAL TITULACIONES`, sin RUT ni CODCLI. |
| `TITULACION/Titulados_IPSS_162_Consolidado_2007_2025.csv` | `70758082b7b5ab6363b267f58d334f86349a6c355dc5636cf1654b90dedca229` | Cabecera con MRUN y fecha de título; sin RUT ni CODCLI. La identificación es sensible y no se exporta. |

**[B/C/E]** La coincidencia de la base de Datos Alumnos refuerza lo ya observado, pero no es evidencia independiente de una decisión de titulación ni indica por sí sola qué plan corresponde al título. La fecha de extracción y cobertura de esa base no están acreditadas; no se trasladan sus estados a una fecha histórica. El archivo de titulaciones agregadas y el consolidado MRUN tampoco aportan una llave documentada título–CODCLI–plan.

**[C/E] Sesión o script:** en esta carpeta se buscaron literalmente las etiquetas `TRACE_SCORE_CANDIDATO`, `TRACE_REASONS_CANDIDATO`, `Res_Tit_Unificada` y `2130` en los archivos accesibles de código, JSON, Markdown, texto y logs. No hubo coincidencias. Se inventariaron dos ZIP y dos RAR con nombres de matrícula u oferta; no se examinó su contenido. La búsqueda no incluye contenido de Excel, PDF o comprimidos y no permite afirmar que la sesión no exista en otra parte.

**[E] Pendientes:** el generador o especificación del puntaje y desempate; y un registro institucional de título que declare CODCLI y plan o una bitácora que permita vincularlos verificablemente. La carpeta aportó un respaldo adicional de expediente, pero no cerró ninguna de esas dos evidencias.

**[C] QA y conservación:** `revisar.py` comprueba SHA-256 antes y después de leer los tres archivos, compara los identificadores en memoria y genera `RESULTADO_AGREGADO.json` sin RUT, CODCLI, nombres ni nacimiento. No se alteraron fuentes, bases, diccionario, tasas ni denominadores. Sin commit ni push.

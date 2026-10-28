# Catálogo de fuentes del proyecto de conciliación UMAS–SIES

## Ampliación autorizada · 28-10-2026

La carpeta 02 también conserva `5809_Precarga Matrícula Avance Curricular 2026.csv`,
SHA-256 `f86e805ca2909f0f8e3dd439a5afb7fc15939a8078b17e13ef33b5cdec2490ed`.
Contiene nombres y documentos (datos_personales: sí); copia de lectura para
comparar MU 2025 con la precarga AC 2026, sin cambiar VIG ni reglas de retención.

| Carpeta | Contenido | Datos personales |
|---|---|---|
| 09_TITULACION_DATOS_RESTRINGIDOS | PES 5319 histórico 2007–2024 por período académico | Sí: nombres y documentos. Uso restringido |
| 11_SIES_MRUN_IPSS_162 | Extracción matrícula IPSS 2007–2025 y consolidado titulados IPSS 2007–2025 | MRUN seudonimizado; derivados institucionales de publicación SIES |
| 12_TITULACION_UNIFICADA_CARGAS | Cargas 2022/2023/2026, agregado 2024 de 470 bytes, respaldo XLSX 2024, reportes PES y documentación oficial | Las cargas y el libro combinado contienen identificadores. Uso restringido; instructivo, oficio, glosario y oferta 5320 son documentación |

También se incorporó MAT_IP_CIISA_2021.xlsx a la carpeta 02 (contiene documentos).
No se movieron ni cortaron originales. SHA-256 origen y copia verificados; cualquier
copia previa permanece conservada y puede figurar en `otras_copias_conservadas`.
Las referencias nacionales 20250729_*_PUBL_MRUN y 20250718_Titulados_*_WEB se
registran únicamente por ruta y hash; no se copian a la carpeta consolidada.
El agregado 2024 no es una nómina. El archivo enviado del proceso 2025 no se localizó;
el reporte PES 5319 conserva 270 registros de período académico 2024.

Actualizar esta ampliación con:
`python3 outputs/consolidacion_bases_onedrive_20261026/consolidar_bases.py --plan outputs/matriz_cuadratura_totales_20261028/PLAN_CONSOLIDACION.json`.
Este modo conserva entradas y bases privadas anteriores. Los catálogos JSON y CSV
se escriben idénticos aquí y en OneDrive. El consumidor de la matriz selecciona las
bases por SHA-256 en el catálogo; los resultados y catálogos versionados de Git
mantienen sus rutas relativas y hashes.

**B/C.** Todas las bases del proyecto están copiadas en una sola carpeta de OneDrive:
`~/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/`.

| Carpeta | Contenido |
|---|---|
| 01_SIES_MATRICULA_HISTORICA_2007_2026 | CSV oficial de matrícula SIES 2007–2026 |
| 02_MATRICULA_UNIFICADA_Y_CARGAS_SIES | Base MU 2022–2026 y su manifiesto, cargas y descargas SIES, intakes |
| 03_UMAS_DATOSDEALUMNOS | Extracciones DATOSDEALUMNOS |
| 04_UMAS_PROMEDIOSDEALUMNOS | Extracciones PROMEDIOSDEALUMNOS |
| 05_OFERTA_ACADEMICA_Y_DURACION | Oferta académica SIES 2010–2026 (dos ediciones) y duración de estudios |
| 06_INDICADORES_ACADEMICOS_VRA | Cumplimiento de ingreso de calificaciones |

**Regla.** Son copias: los originales no se movieron ni se modificaron. El SHA-256 identifica el
contenido, así que cada copia tiene el mismo hash que su origen; lo que cambia es la ruta.
`CATALOGO_FUENTES.json` (aquí y en la carpeta de OneDrive, idénticos) registra para cada archivo
su hash, tamaño, ruta consolidada, todos sus orígenes y qué descriptor lo cita.
`PROYECTO_IPSS.json → recursos_comunes.catalogo_fuentes` apunta a este catálogo.

**Relación con el diccionario.** Los descriptores v1–v9 conservan las rutas originales (no se
reescriben ediciones). Para reproducir desde OneDrive se busca el hash citado en el catálogo.

**Excluido por regla:** libros de trabajo (V5, V12), bases privadas derivadas de
`~/.local/share/ipss` (contienen identificadores) y catálogos derivados ya versionados en Git
(`maestro.json`, `historias_oferta.json`).

**Actualizar:** `python3 outputs/consolidacion_bases_onedrive_20261026/consolidar_bases.py`.
Es idempotente: copia solo lo nuevo y nunca sobrescribe un archivo distinto.

## 07_PRIVADAS_DICCIONARIO (agregada el 26-10-2026, a pedido de Alexi)

Copias de las bases privadas, hechas de a una con verificación en cada paso: las nueve bases
SQLite del diccionario (v1 a v9, una subcarpeta por edición) y la vista de seguimiento T1/T2/T3
de Fase 3. **Contienen RUT y CODCLI.** Están registradas en `catalogo_privadas` del catálogo.
Los originales siguen en `~/.local/share/ipss/` y el diccionario activo sigue leyendo desde ahí.
Script: `outputs/consolidacion_bases_onedrive_20261026/copiar_privada.py --paso N`.

# Catálogo de fuentes del proyecto de conciliación UMAS–SIES

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

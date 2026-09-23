# Requerimiento Bettersoft: Reporte Regulatorio Maestro U+ (SIES/PES 2026)

```text
VERSION_ACTUAL=v1.0
ESTADO=CONGELADO
FECHA_CONGELACION=2026-09-23
```

## Propósito

Diccionario maestro U+ → SIES/PES y requerimiento funcional para que Bettersoft cree en U+ un reporte regulatorio que reemplace el uso de "Datos Alumnos" en Matrícula Unificada, Avance Curricular, Estudiantes Extranjeros y FCU.

Principio: **Bettersoft entrega hechos y atributos del ERP; la institución gobierna la transformación regulatoria SIES** cuando depende de reglas funcionales, fechas de corte o trayectoria.

## Archivos oficiales v1.0

| Archivo | Uso | Destinatario |
|---|---|---|
| `resultados/REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS_v1.0.docx` | Requerimiento funcional | **Se entrega a Bettersoft** |
| `resultados/DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v1.0.xlsx` | Diccionario maestro con trazabilidad completa (matriz de 261 campos SIES, diccionario Bettersoft, catálogos, brechas, resoluciones, pendientes, matriz de solicitud y changelog) | Equipo institucional |
| `resultados/AUDITORIA_GATE09_CONTRADICCIONES_UPLUS_SIES_2026.xlsx` | Auditoría de las 13 contradicciones | Interno |
| `REPORTE_CIERRE_GATE09_UPLUS_SIES_2026.md` | Informe de cierre del Gate 09 | Interno |
| `MANIFIESTO_CONGELACION_v1.0.md` | Hashes y estado de la congelación | Interno |
| `CHANGELOG_COLUMNAS_BETTERSOFT_v0.9.1_A_v1.0.md` | Cambios de columnas entre versiones | Interno |
| `PENDIENTE_EVALUAR_RECTIFICACION_MU2026_C09_02_C09_03.md` | Pendiente institucional, fuera del requerimiento Bettersoft | Interno |

Versiones anteriores (se conservan sin modificar): `*_v0.9.1_GATE09.*` y los entregables v0.9 sin sufijo.

## Estructura

```text
requerimiento_bettersoft_uplus_2026/
├── 01_fuentes_oficiales/        instructivos AC y Extranjeros 2026, precargas y plantillas PES sin datos personales + MANIFIESTO_FUENTES_GATE09.tsv
├── 02_evidencia_envios_sin_datos_personales/
├── resultados/                  entregables por versión; gate09/ y gate10/ con métricas agregadas, QA e insumos JSON del Word
├── scripts/                     generadores y QA
└── *.md                         README, reporte Gate 09, manifiesto, changelog y pendiente institucional
```

## Regenerar

```bash
cd requerimiento_bettersoft_uplus_2026/scripts
PY=python3   # requiere pandas, openpyxl, python-docx
NODE="NODE_PATH=../../oferta_academica_2027/node_modules node"

# v0.9 (fases 1-8)
$PY generar_diccionario_maestro_uplus_sies.py --datos-alumnos /ruta/DATOSDEALUMNOS_<n>.xlsx

# Gate 09 (v0.9.1)
$PY gate09_incorporar_fuentes.py
$PY gate09_metricas.py --prom7804 "<PROMEDIOSDEALUMNOS_7804.xlsx usado en la carga MU 2026>"
$PY gate09_generar.py
eval $NODE generar_requerimiento_bettersoft_docx_gate09.js ../resultados/gate09/req_gate09.json ../resultados/REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS_v0.9.1_GATE09.docx
$PY gate09_qa.py

# Gate 10 (v1.0)
$PY gate10_generar.py
eval $NODE generar_requerimiento_bettersoft_docx_v1.js ../resultados/gate10/req_v1.json ../resultados/REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS_v1.0.docx
$PY gate10_qa.py
```

Si se regenera el Word v1.0, cambia su hash y hay que repetir la revisión visual en Microsoft Word antes de usarlo.

## Datos sensibles

- El repositorio es público (`avance_curricular_2026/01_documentacion/POLITICA_DATOS_Y_GIT.md`).
- Las evidencias con RUT, nombres o fechas de nacimiento (cargas PES, precargas y envíos) están solo en `avance_curricular/.local_restricted/requerimiento_bettersoft_uplus_2026/`. Esa carpeta está excluida de Git por `.git/info/exclude`. Esa exclusión es local: en otro clon hay que replicarla.
- `resultados/gate09/METRICAS_EVIDENCIA_GATE09.json` y los libros Excel contienen solo agregados, patrones y ejemplos ficticios.
- `*.xlsx`, `*.csv` y `*.tsv` están ignorados por `.gitignore`. Los Excel oficiales requieren `git add -f` si la institución decide versionarlos.

## Pendientes residuales

| ID | Pendiente | Estado |
|---|---|---|
| PR-01 | Significado de SEXO = S en U+ | PENDIENTE_CATALOGO_OFICIAL_UPLUS (UP-68) |
| PR-02 | Significado de PERÍODO = 3 en U+ | PENDIENTE_CATALOGO_OFICIAL_UPLUS (UP-68) |
| PR-03 | Evaluar rectificación de MU 2026 (C09-02, C09-03) | PENDIENTE_DECISION_INSTITUCIONAL (no es parte del requerimiento Bettersoft) |
| PR-04 | Revisar las filas de Extranjeros Intercambio contra el Anexo II del instructivo | PENDIENTE_REVISION |
| PR-05 | Manuales MU 2022-2023 | FUENTE_NO_DISPONIBLE (solo para reconstrucción histórica) |

# Reconstruccion limpia modulo CNED

- Fecha generacion: 2026-06-05T12:19:48
- Repositorio: /Users/alexi/Documents/GitHub/avance_curricular
- Rama creada/utilizada: `feature/cned-reconstruccion-limpia`

## 1. Estado inicial del repositorio

- Estado observado antes de la rama CNED: `clean/pes-ready-final` divergida con `origin/clean/pes-ready-final` por 1 commit local y 1 remoto.
- Accion ejecutada a solicitud del flujo: `git pull --rebase origin clean/pes-ready-final`.
- Resultado: rebase completado sin conflictos.

## 2. Archivos CNED previos detectados

- Hallazgos registrados en manifest: 188
- Manifest: `archive/cned_trabajo_previo_20260605/manifest_cned_paths_20260605.txt`
- Principal ubicacion detectada: `indices_2025/cned/`.
- Tipos detectados: datos TSV, scripts, auditorias, reportes Markdown, Excel, CSV/TSV y artefactos de conciliacion.

## 3. Archivos respaldados

- Respaldo no destructivo creado por copia.
- Carpeta: `archive/cned_trabajo_previo_20260605/`.
- No se borraron ni movieron archivos originales.
- Elementos dudosos no fueron tocados; quedan para revision manual si corresponde.

## 4. Estructura CNED creada

```text
cned/
|-- data/
|   |-- input/
|   |-- catalogos/
|   `-- processed/
|-- scripts/
|-- resultados/
|   |-- archivos_subida/
|   |-- auditorias/
|   `-- reportes/
|-- docs/
`-- tests/
```

## 5. Scripts y documentacion creados

- `cned/docs/BITACORA_CNED.md`
- `cned/docs/README_CNED.md`
- `cned/docs/REGLAS_CNED.md`
- `cned/resultados/reportes/auditoria_cned_base_20260605_121910.md`
- `cned/resultados/reportes/generacion_cned_base_20260605_121910.md`
- `cned/resultados/reportes/run_cned_20260605_121910.log`
- `cned/resultados/reportes/validacion_cned_base_20260605_121910.md`
- `cned/scripts/auditar_cned.py`
- `cned/scripts/check_no_tocar_mu2026.py`
- `cned/scripts/generar_archivo_cned.py`
- `cned/scripts/run_cned.sh`
- `cned/scripts/validar_cned.py`

## 6. Validaciones ejecutadas

- `python cned/scripts/check_no_tocar_mu2026.py`: OK, no se detectaron modificaciones en archivos protegidos MU2026.
- `bash cned/scripts/run_cned.sh`: OK, ejecucion base sin insumos CNED cargados.
- Reportes base generados en `cned/resultados/reportes/`.
- No se genero archivo de subida CNED porque falta insumo oficial, instructivo y mapeo validado.

## 7. Proteccion MU2026/PES_READY

No se modificaron scripts protegidos de Matricula Unificada / PES_READY. El chequeo dedicado valida `git diff` sobre los archivos criticos definidos para MU2026.

## 8. Estado Git final observado

```text
## feature/cned-reconstruccion-limpia
?? archive/cned_trabajo_previo_20260605/
?? cned/
```

## 9. Ultimos commits visibles

```text
fe19175 (HEAD -> feature/cned-reconstruccion-limpia, clean/pes-ready-final) fix: canonicalize clean CNED materializer script
4caf70b (origin/clean/pes-ready-final) fix: canonicalize clean CNED materializer script
4375559 feat: materialize clean CNED operational artifact
c8c2beb feat: add MU2026 PES_READY generation and exclusion audit
4829b6a (origin/main, origin/HEAD) test: add optional MU2026 cross-validation fixture
```

## 10. Proximos pasos recomendados

1. Incorporar insumo oficial CNED en `cned/data/input/`.
2. Definir estructura oficial de carga CNED.
3. Construir mapeo de columnas documentado.
4. Generar archivo de subida en `cned/resultados/archivos_subida/`.
5. Generar auditoria de diferencias en `cned/resultados/auditorias/`.
6. Validar contra oferta, programas y codigos institucionales.
7. Emitir reporte final trazable en `cned/resultados/reportes/`.

## Dictamen

DICTAMEN_FINAL: MODULO_CNED_RECONSTRUIDO_LIMPIO_SEPARADO_Y_VALIDADO_BASE

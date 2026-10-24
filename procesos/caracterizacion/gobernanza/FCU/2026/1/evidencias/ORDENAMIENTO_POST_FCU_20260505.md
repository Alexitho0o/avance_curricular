# ORDENAMIENTO POST-FCU 2026 P1 — 2026-05-05

## 1. Estado de éxito FCU/PES

| Ítem | Valor |
|------|-------|
| Fecha de carga | 2026-05-05 |
| Proceso | FCU 2026 Período 1 |
| Estado | **EXITOSO — carga confirmada en plataforma** |
| Filas subidas | 1371 |
| Campos por fila | 195 (separador `;`) |
| Línea vacía final | No |
| Pendientes condicionales | 0 |

## 2. Archivo final subido

```
/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS_PES_FINAL.csv
```

- Separador: punto y coma (`;`)
- Sin cabeceras
- Sin línea vacía final
- 1371 filas × 195 campos

## 3. Script final responsable

```
scripts/generar_fcu_pes_final.py
```

Función: convierte FCU CSV (coma) → PES/SIES (punto y coma) aplicando correcciones condicionales.

## 4. Resumen de validaciones

| Validación | Resultado |
|-----------|-----------|
| Correcciones RAP aplicadas | 65 |
| Correcciones discapacidad registro | 10 |
| Correcciones discapacidad orientación | 10 |
| Correcciones contacto | 24 |
| Pendientes RAP | 0 |
| Pendientes discapacidad registro | 0 |
| Pendientes discapacidad orientación | 0 |
| Pendientes contacto | 0 |
| Estructura 195 campos (`;`) | OK |
| Sin separador coma en salida | OK |
| Sin trailing newline | OK |
| Terminal | `OK_FCU_PES_FINAL_LISTO_PARA_SUBIR` |

Auditoría generada en:
```
/Users/alexi/Desktop/FCU_2026_AUDITORIA_PES_FINAL_20260505.csv
```

## 5. Mapa actual del proyecto (previo al ordenamiento)

```
CARACTERIZACIÓN/
├── caracterizacion.py                          ← NÚCLEO FUNCIONAL
├── analisis_sectorizado_encuesta_ac.py         ← script auxiliar
├── explorador_pygwalker.py                     ← script exploratorio
├── integracion_avance_curricular.py            ← script auxiliar
├── run_ac_integracion_test.sh                  ← script de ejecución
├── run_caracterizacion_con_sectorizado_ac.sh   ← script de ejecución
├── run_caracterizacion_fijo.sh                 ← script de ejecución
├── AUDITORIA_ORDENAMIENTO_APLICADO.md          ← documentación
├── AUDITORIA_ORDENAMIENTO_PREVIA.md            ← documentación
├── CONTRATOS_INVARIANTES.md                    ← gobernanza
├── GUIA_INTERVENCION_SEGURA.md                 ← gobernanza
├── MANIFEST_BLOQUES.yaml                       ← gobernanza
├── MAPA_MAESTRO_CARACTERIZACION.md             ← documentación
├── MAPA_MAESTRO_CARACTERIZACION_KPI_GOBERNANZA.md ← documentación
├── README.md                                   ← documentación
├── TVS_BLOQUES.md                              ← documentación
├── caracterizacion.py.bak_20260505_* (×16)    ← BACKUPS EN RAÍZ
├── scripts/
│   ├── auditar_fcu_csv.py
│   ├── convertir_fcu_pes_semicolon.py
│   ├── generar_fcu_pes_final.py               ← NÚCLEO FCU PES
│   ├── run_completo_2026_p1.py
│   └── run_fcu_2026_p1.py
├── docs/
│   ├── INTEGRACION_AVANCE_CURRICULAR_AC.md
│   └── Manual_de_Aplicacion_FCU_2026.txt
├── archive/
│   ├── caracterizacion_broken_syntax_20260425_044652.py
│   └── cleanup_2026-04-16/
├── backups/ (57 archivos)
├── outputs/
│   └── pygwalker/
├── diagnosticos/
├── cuarentena_revision_manual/
└── EXTRACCION_MATRICULA_SIES _2007_2025/
```

## 6. Propuesta de ordenamiento

### Cambios seguros a aplicar

| Acción | Origen | Destino | Motivo |
|--------|--------|---------|--------|
| Crear carpeta | — | `docs/cierre_fcu_2026_p1/` | Concentrar artefactos de cierre |
| Crear carpeta | — | `archive/backups_caracterizacion_20260505/` | Concentrar backups de raíz |
| Crear carpeta | — | `outputs/fcu_2026_p1_cierre/` | Documentar salidas del proceso |
| Mover backups `.bak_*` (×16) | raíz | `archive/backups_caracterizacion_20260505/` | Sin referencia activa en código |
| Crear manifiesto | — | `docs/cierre_fcu_2026_p1/MANIFIESTO_CIERRE_FCU_2026_P1.md` | Gobernanza documental |

## 7. Archivos que NO se deben mover

| Archivo | Motivo |
|---------|--------|
| `caracterizacion.py` | Script principal activo |
| `scripts/generar_fcu_pes_final.py` | Script PES final validado |
| `scripts/auditar_fcu_csv.py` | Script de auditoría activo |
| `scripts/convertir_fcu_pes_semicolon.py` | Referenciado potencialmente |
| `scripts/run_completo_2026_p1.py` | Script de orquestación |
| `scripts/run_fcu_2026_p1.py` | Script de ejecución FCU |
| `docs/Manual_de_Aplicacion_FCU_2026.txt` | Fuente del Anexo 5 — parseado por caracterizacion.py |
| `MANIFEST_BLOQUES.yaml` | Gobernanza operacional activa |
| `CONTRATOS_INVARIANTES.md` | Gobernanza operacional activa |
| `GUIA_INTERVENCION_SEGURA.md` | Gobernanza operacional activa |
| `backups/` (carpeta) | 57 backups históricos — no mover masivamente |

## 8. Archivos candidatos a mover

| Archivo | Destino propuesto | Condición |
|---------|------------------|-----------|
| `caracterizacion.py.bak_20260505_*` (×16 en raíz) | `archive/backups_caracterizacion_20260505/` | Sin referencias activas — SEGURO |

## 9. Archivos que requieren revisión manual

| Archivo | Motivo |
|---------|--------|
| `analisis_sectorizado_encuesta_ac.py` | Script auxiliar grande — posible uso futuro |
| `explorador_pygwalker.py` | Script exploratorio — no crítico |
| `integracion_avance_curricular.py` | Integración AC — uso futuro incierto |
| `EXTRACCION_MATRICULA_SIES _2007_2025/` | Carpeta con espacio en nombre — riesgo en rutas |
| `backups/` (57 archivos) | Demasiados para mover sin revisión individual |
| `cuarentena_revision_manual/` | Por definición requiere revisión manual |

## 10. Riesgos detectados

| Riesgo | Descripción | Mitigación |
|--------|-------------|------------|
| `docs/Manual_de_Aplicacion_FCU_2026.txt` | Parseado internamente por `caracterizacion.py` con ruta relativa | NO MOVER |
| `EXTRACCION_MATRICULA_SIES _2007_2025/` | Nombre con espacio — puede fallar en scripts shell | Pendiente de revisión manual |
| Backups en `backups/` (57) | Mezcla de fechas y propósitos | Revisar antes de mover masivamente |

## 11. Checklist de cierre

- [x] FCU 2026 P1 generada y validada
- [x] Archivo PES final subido a plataforma
- [x] Auditoría de correcciones generada
- [x] `py_compile` pasa en `caracterizacion.py`
- [x] `py_compile` pasa en `scripts/generar_fcu_pes_final.py`
- [x] `region_invalidas: 0` / `comuna_invalidas: 0`
- [x] `rut_recuperados: 8` / `rut_no_recuperables: 0`
- [x] Backups `.bak_*` de raíz movidos a `archive/backups_caracterizacion_20260505/`
- [x] Manifiesto de cierre creado en `docs/cierre_fcu_2026_p1/`
- [ ] Revisar `EXTRACCION_MATRICULA_SIES _2007_2025/` — pendiente manual
- [ ] Revisar `backups/` (57 archivos) — pendiente manual
- [ ] Revisar scripts auxiliares (`analisis_sectorizado_encuesta_ac.py`, etc.) — pendiente manual

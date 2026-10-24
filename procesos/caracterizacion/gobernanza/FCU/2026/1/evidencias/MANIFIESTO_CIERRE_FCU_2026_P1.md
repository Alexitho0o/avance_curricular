# MANIFIESTO DE CIERRE — FCU 2026 PERÍODO 1

| Campo | Valor |
|-------|-------|
| **Fecha de cierre** | 2026-05-05 |
| **Proyecto** | CARACTERIZACIÓN |
| **Proceso** | FCU 2026 Período 1 |
| **Estado** | CERRADO — EXITOSO |

---

## Archivo final subido a plataforma

```
/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS_PES_FINAL.csv
```

- Separador: `;` (punto y coma)
- Sin cabeceras
- Sin línea vacía final
- 1371 filas × 195 campos

## Script final usado

```
scripts/generar_fcu_pes_final.py
```

Responsabilidades:
- Convertir FCU CSV (coma) → PES/SIES (punto y coma)
- Aplicar correcciones condicionales RAP, discapacidad, contacto
- Validar estructura de salida
- Emitir `OK_FCU_PES_FINAL_LISTO_PARA_SUBIR`

## Auditoría final

```
/Users/alexi/Desktop/FCU_2026_AUDITORIA_PES_FINAL_20260505.csv
```

Formato: `linea_fisica;rut;nombre;regla;campo;indice;valor_anterior;valor_nuevo;observacion`

---

## Validaciones estructurales

| Check | Resultado |
|-------|-----------|
| Filas de entrada | 1371 |
| Filas de salida | 1371 |
| Campos por fila (`;`) | {195: 1371} |
| Campos por fila (`,`) | {1: 1371} |
| Trailing newline | False |

## Validaciones condicionales

| Regla | Correcciones | Pendientes |
|-------|-------------|-----------|
| RAP_P27_3_P27_4 (índice 90) | 65 | 0 |
| DISCAP_REGISTRO (índice 23) | 10 | 0 |
| DISCAP_ORIENTACION (índice 24) | 10 | 0 |
| CONTACTO (índice 134) | 24 | 0 |

## Validaciones FCU base (desde `scripts/auditar_fcu_csv.py`)

| Check | Resultado |
|-------|-----------|
| `filas_no_195_con_coma` | 0 |
| `region_invalidas` | 0 |
| `comuna_invalidas` | 0 |
| `rut_recuperados` | 8 |
| `rut_no_recuperables` | 0 |

---

## Cambios realizados en el ordenamiento (2026-05-05)

| Tipo | Origen | Destino | Cantidad |
|------|--------|---------|---------|
| Carpeta creada | — | `docs/cierre_fcu_2026_p1/` | 1 |
| Carpeta creada | — | `archive/backups_caracterizacion_20260505/` | 1 |
| Carpeta creada | — | `outputs/fcu_2026_p1_cierre/` | 1 |
| Backups movidos | raíz (`*.bak_*`) | `archive/backups_caracterizacion_20260505/` | 16 |
| Doc creado | — | `docs/ORDENAMIENTO_POST_FCU_20260505.md` | 1 |
| Doc creado | — | `docs/cierre_fcu_2026_p1/MANIFIESTO_CIERRE_FCU_2026_P1.md` | 1 |

### Backups movidos a `archive/backups_caracterizacion_20260505/`

```
caracterizacion.py.bak_20260505_214708_fcu_rut_15065249_zapallar
caracterizacion.py.bak_20260505_220029_fcu_rut_15065249_zapallar_regex
caracterizacion.py.bak_20260505_220430_fcu_rut_15065249_zapallar_final
caracterizacion.py.bak_20260505_220502_fcu_rut_15065249_zapallar_regex_final
caracterizacion.py.bak_20260505_220531_antes_fix_zapallar_seguro
caracterizacion.py.bak_20260505_cohortes_analisis_env
caracterizacion.py.bak_20260505_fcu_auditoria_safe_writer
caracterizacion.py.bak_20260505_fcu_bloqueante
caracterizacion.py.bak_20260505_fcu_preexport_no_bloqueo
caracterizacion.py.bak_20260505_fcu_recuperacion_8_casos
caracterizacion.py.bak_20260505_fcu_region_comuna_preexport
caracterizacion.py.bak_20260505_fcu_zapallar_rut15065249_fix
caracterizacion.py.bak_20260505_quirurgico
caracterizacion.py.bak_20260505_skip_b9_solo_fcu
caracterizacion.py.bak_20260505_solo_generar_fcu
caracterizacion.py.bak_20260506_rut_recovery_clean_exit
```

---

## Archivos no tocados

| Archivo/Carpeta | Motivo |
|----------------|--------|
| `caracterizacion.py` | Script principal activo — no se modifica |
| `scripts/` (todos) | Scripts activos — no se modifican |
| `docs/Manual_de_Aplicacion_FCU_2026.txt` | Parseado por `caracterizacion.py` — no se mueve |
| `MANIFEST_BLOQUES.yaml` | Gobernanza activa |
| `CONTRATOS_INVARIANTES.md` | Gobernanza activa |
| `GUIA_INTERVENCION_SEGURA.md` | Gobernanza activa |
| `backups/` (57 archivos) | Requieren revisión individual |
| `cuarentena_revision_manual/` | Requiere revisión manual explícita |
| `EXTRACCION_MATRICULA_SIES _2007_2025/` | Nombre con espacio — riesgo de rutas |
| Desktop (archivos FCU/PES) | Fuera del proyecto — solo documentados |

---

## Pendientes de revisión manual

| Ítem | Acción recomendada |
|------|--------------------|
| `backups/` (57 archivos) | Revisar y purgar los que correspondan a fases ya superadas |
| `analisis_sectorizado_encuesta_ac.py` | Evaluar si pertenece a un submódulo o se archiva |
| `explorador_pygwalker.py` | Evaluar si se mueve a `tools/` o `scripts/` |
| `integracion_avance_curricular.py` | Evaluar si sigue activo o se archiva |
| `cuarentena_revision_manual/` | Revisar contenido y resolver o archivar |
| `EXTRACCION_MATRICULA_SIES _2007_2025/` | Renombrar sin espacio cuando sea seguro |

---

## Próximos pasos recomendados

1. Confirmar recepción y validación de la carga en la plataforma SIES/PES.
2. Revisar `backups/` y purgar copias obsoletas.
3. Resolver `cuarentena_revision_manual/`.
4. Evaluar scripts auxiliares (`explorador_pygwalker.py`, etc.).
5. Renombrar `EXTRACCION_MATRICULA_SIES _2007_2025/` eliminando el espacio.
6. Para FCU 2026 Período 2: reutilizar `scripts/generar_fcu_pes_final.py` como plantilla.

---

## Comandos de validación técnica

```bash
# Compilación sintáctica
cd /Users/alexi/Documents/GitHub/CARACTERIZACIÓN
python3 -m py_compile caracterizacion.py
python3 -m py_compile scripts/generar_fcu_pes_final.py

# Generación FCU (requiere datos y env)
cd /Users/alexi/Documents/GitHub/CARACTERIZACIÓN
ANIO_ANALISIS=2026 PERIODO_ANALISIS=1 VERBOSIDAD=2 COHORTES_ANALISIS=2026 SOLO_GENERAR_FCU=1 python3 caracterizacion.py

# Revisión estructura
ls -la /Users/alexi/Documents/GitHub/CARACTERIZACIÓN/
ls archive/backups_caracterizacion_20260505/ | wc -l
ls docs/cierre_fcu_2026_p1/
```

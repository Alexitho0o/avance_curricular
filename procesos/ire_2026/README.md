# IRE 2026 — Infraestructura y Recursos Educacionales

Proceso de carga de datos para el Instituto Profesional San Sebastián (COD_IES 162).

## Especificación

- **Institución**: Instituto Profesional San Sebastián
- **COD_IES**: 162
- **ID de carga**: 16770
- **Fecha de corte**: 30 de junio de 2026
- **Plazo de carga PES**: 24 de julio de 2026
- **Estructura**: 54 columnas exactas, delimitadas por `;`

## Archivos fuente

- `data/estructura/20260706_89535_Estructura_IRE_ID_16770.csv` — Encabezados oficiales (read-only)
- `data/historico/Indicadores generales.xlsm` — Histórico 2023-2025 (read-only)
- `data/historico/ire_historico.csv` — Histórico normalizado (generado)
- `data/input/ire_2026.csv` — Entrada editable a mano, precargada con 2025

## Entregables

1. `output/IRE_2026_carga_AAAAMMDD.csv` — CSV sin encabezados, `;` delimitado, UTF-8
2. `output/IRE_2026_respaldo_AAAAMMDD.xlsx` — Excel con encabezados, tipado real
3. `output/Reporte_KPI_Infraestructura_2026.docx` — Reporte de gestión (no sube a PES)

Variantes: genera `_puntoycoma.csv` y `_coma.csv` hasta confirmar cuál acepta PES.

## Instalación

Usa el `.venv` en la raíz del monorepo (no el de otros repos del workspace).
Python 3.13 recomendado: pandas/matplotlib pueden no tener ruedas para 3.14 aún.

```bash
cd /ruta/al/repo/avance_curricular
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del monorepo (usa el `.venv` compartido):

```bash
make ire-test       # Tests unitarios
make ire-validar    # Validar estructura y reglas
make ire-generar    # Generar los tres entregables
make ire-clean      # Limpieza
```

## Configuración

**Requerido antes de generar:**

- `config/institucion.yaml` — Razón social, casa central, COD_IES
- `config/parametros_2026.yaml` — Matrícula, tenencia, datos de inmuebles, plataformas

Falla clara si algún parámetro requerido sigue en `null`.

## Notas operacionales

### Histórico `.xlsm`

- Hoja correcta para KPI: `KPI (2)` (la hoja `KPI` está rota con `#VALUE!`)
- Contiene `FEC_REF` en posición 5: no es columna de carga, se extrae como metadato
- Hojas tabular: `2024`, `2025`, `Consolidado`

### Delimitador

El instructivo de MINEDUC dice "comas" pero la estructura oficial viene con `;`.
El generador produce ambas variantes; consulta `docs/bitacora_cargas.md` para registro.

### Validación

Las 54 columnas, tipos, aplicabilidad por TIPO y catálogos están en `src/schema.py`.
Reglas Anexo III + reglas adicionales en `src/validators.py`.

### Archivo `.xlsm` histórico pendiente

`data/historico/Indicadores generales.xlsm` **no está en el repo** (no se copió desde Descargas).
`ire_historico.csv` ya contiene los datos 2023-2025 verificados contra la fuente original, así que
esto no bloquea el pipeline. Paso manual pendiente si se necesita reprocesar desde el Excel original:

```bash
cp ~/Downloads/Indicadores\ generales.xlsm procesos/ire_2026/data/historico/
```

## Checklist de carga

- [ ] `cp ~/Downloads/Indicadores generales.xlsm data/historico/` (si se requiere reprocesar histórico)
- [ ] `config/parametros_2026.yaml` completado con todos los valores 2026
- [ ] `make ire-test` pasa al 100%
- [ ] `make ire-generar` sin errores
- [ ] `output/IRE_2026_carga_*.csv` validado en PES (respuesta `.txt` en `docs/errores_pes/`)
- [ ] Registrar resultado en `docs/bitacora_cargas.md`

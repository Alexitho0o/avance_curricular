# Avance Curricular + Matrícula Unificada

Pipeline Python para dos procesos:
- `avance`: genera Avance Curricular (salidas PES/SIES + validaciones).
- `matricula`: genera `archivo_listo_para_sies.xlsx` estilo Matrícula Unificada.
- `ambos`: ejecuta ambos procesos en una sola corrida.

## Requisitos
- Python 3.9+
- `pandas`
- `numpy`
- `openpyxl`

Instalación rápida:
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## Uso rápido

### 1) Solo Avance Curricular
```bash
./.venv/bin/python codigo.py \
  --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
  --output-dir resultados \
  --proceso avance
```

### 2) Solo Matrícula Unificada
```bash
./.venv/bin/python codigo.py \
  --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
  --output-dir resultados \
  --proceso matricula
```

### 3) Ambos procesos
```bash
./.venv/bin/python codigo.py \
  --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
  --output-dir resultados \
  --proceso ambos
```

## Catálogos para matching SIES (proceso matrícula)

El proceso matrícula soporta catálogo manual y puente SIES vía TSV:
```bash
./.venv/bin/python codigo.py \
  --input "/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx" \
  --output-dir resultados \
  --proceso matricula \
  --catalogo-manual-tsv "/ruta/catalogo_manual.tsv" \
  --puente-sies-tsv "/ruta/puente_sies.tsv"
```

Si no se pasan rutas, el script intenta autodetectar:
- `catalogo_manual.tsv` en el repo o en `~/Downloads`
- `puente_sies.tsv` en el repo o en `~/Downloads`

Si no los encuentra, el pipeline igual corre, pero reporta:
- `SIN_CATALOGO_MANUAL`
- `SIN_PUENTE_SIES`

## Error común

Si ves:
`FileNotFoundError: No se encontró archivo de entrada: /ruta/a/tu_workbook.xlsx`

significa que usaste una ruta de ejemplo. Debes reemplazarla por una ruta real, por ejemplo:
`/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`.

## Licencia
MIT. Ver [LICENSE](LICENSE).

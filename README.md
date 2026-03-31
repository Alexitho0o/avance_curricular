<<<<<<< HEAD
# Avance Curricular + Matrícula Unificada
=======
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
# Avance Curricular Processor
=======
# Pipeline híbrido SIES/PES
>>>>>>> theirs

Runner canónico: `codigo.py`.

## Ejecución

```bash
python3 codigo.py --input "subir prueba.xlsx" --output-dir resultados
```

## Arquitectura

<<<<<<< ours
1. Place the Excel file to process somewhere on your computer.
2. Execute the script:
=======
# Avance Curricular

This repository provides a script to process curricular advancement data from an Excel file. The script reads the data, prepares the necessary sheets and exports formatted spreadsheets.

## Installation

Install the required Python packages using `pip` and the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

<<<<<<< ours
<<<<<<< ours
## Usage
=======
3. When prompted `🔢 Año matrícula focal`, enter the year you want to analyze.
4. Choose whether to focus on a specific period; if you answer "s", you will be asked for `🔢 Período matrícula focal (1-3)`. Answering "n" will process the whole year.
5. When prompted `Ruta de archivo .xlsx:`, provide the path to your workbook.
6. After processing finishes, two Excel files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will appear in the same directory.
>>>>>>> theirs

Run the main script:
>>>>>>> theirs
=======
- **Capa A (ingesta flexible):** detección de hojas por columnas mínimas y normalización de claves.
- **Capa B (modelo intermedio):** no colapsa a una carrera por RUT; resuelve equivalencias solo cuando son unívocas y deja ambiguos en revisión.
- **Capa C (proyección oficial):** aplica contratos exactos de salida, valida instructivo y exporta control + PES-ready.
>>>>>>> theirs

## Entregables

<<<<<<< ours
<<<<<<< ours
3. When prompted `Ruta de archivo .xlsx:`, provide the path to your workbook.
4. After processing finishes, two Excel files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will appear in the same directory.
=======
### Oficiales
1. `resultados/matricula_unificada_2026_oficial.xlsx`
2. `resultados/carreras_avance_curricular_2025_pes_ready.csv`
3. `resultados/matricula_avance_curricular_2025_pes_ready.csv`
>>>>>>> theirs
=======
3. When prompted `🔢 Año matrícula focal`, enter the year you want to analyze.
4. Choose whether to focus on a specific period; if you answer "s", you will be asked for `🔢 Período matrícula focal (1-3)`. Answering "n" will process the whole year.
5. When prompted `Ruta de archivo .xlsx:`, provide the path to your workbook.
6. After processing finishes, two Excel files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will appear in the same directory.
>>>>>>> theirs

### Control
- `resultados/matricula_unificada_2026_control.csv`
- `resultados/carreras_avance_curricular_2025_control.csv`
- `resultados/matricula_avance_curricular_2025_control.csv`

### Auditoría y trazabilidad
- `resultados/reporte_validacion.json`
- `resultados/sies_ambiguedad_diagnostico.csv`
- `resultados/sies_codcarr_sin_mapeo.csv`
- `resultados/comparacion_versiones.md`
- `resultados/diccionario_columnas.md`
- `resultados/reporte_procedencia.csv`
- `resultados/reporte_calidad_semantica.json`

## Reglas claves aplicadas

- `pes_ready` elimina `CODIGO_IES_NUM` **por nombre de columna**, nunca por índice.
- Ambigüedad `CODCARR -> CODIGO_UNICO` no se fuerza con `drop_duplicates`.
- Campos sensibles de Matrícula Unificada (`PAIS_EST_SEC`, `REINCORPORACION`) no se inventan: se reportan como `BLOCKER` si faltan.
- Orden de carga de Avance Curricular: primero Carreras, luego Matrícula.


<<<<<<< ours
## Check de calidad
=======
When executed in Colab, the script first asks for the focal year and whether you want to limit the analysis to a period. A file upload dialog then appears to select your Excel file. Once the script finishes, the resulting Excel files are automatically downloaded to your computer.
>>>>>>> theirs

<<<<<<< ours
### Campos mínimos exigidos (según instructivo SIES 2025)
- **Carreras Avance Curricular 2025**: `CODIGO_UNICO`, `PLAN_ESTUDIOS`, `TIPO_UNIDAD_MEDIDA`, `TOTAL_UNIDADES_MEDIDA`, `UNIDADES_1ER_ANIO` … `UNIDADES_7MO_ANIO`, `VIGENCIA` (y `OTRA_UNIDAD_MEDIDA` si `TIPO_UNIDAD_MEDIDA = 3`).
- **Matrícula Avance Curricular 2025**: `NUM_DOCUMENTO`, `DV`, `CODIGO_UNICO`, `PLAN_ESTUDIOS`, `CURSO_1ER_SEM`, `CURSO_2DO_SEM`, `UNIDADES_CURSADAS`, `UNIDADES_APROBADAS`, `UNID_CURSADAS_TOTAL`, `UNID_APROBADAS_TOTAL`, `VIGENCIA`.
- **Histórico** (una o varias hojas): `RUT`, `DIG`, `ANO`, `PERIODO`, `CODRAMO`, `DESCRIPCION_ESTADO`.

El script valida que estas columnas existan y que la suma de `UNIDADES_*_ANIO` coincida con `TOTAL_UNIDADES_MEDIDA` antes de procesar.

## Downloading results

The generated files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will be saved in the current working directory. In Google Colab, they are also offered as direct downloads once processing is complete.
=======
# Avance Curricular

<<<<<<< ours
Herramienta en Python para procesar planillas de avance curricular.
=======
When executed in Colab, the script first asks for the focal year and whether you want to limit the analysis to a period. A file upload dialog then appears to select your Excel file. Once the script finishes, the resulting Excel files are automatically downloaded to your computer.
>>>>>>> theirs

## Requisitos

- Python 3.x
- [pandas](https://pandas.pydata.org)
- [openpyxl](https://openpyxl.readthedocs.io)

## Licencia

Este proyecto se distribuye bajo los términos de la [licencia MIT](LICENSE).
>>>>>>> theirs
=======
The program will prompt for the location of the Excel workbook (or show an upload widget if running in Google Colab). The generated files will be saved as `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx`.
>>>>>>> theirs
=======
```bash
python3 qa_checks.py
```
>>>>>>> theirs
=======
# Avance Curricular Processor
>>>>>>> 6b9ee2bf3f51aff72dcb8254282fd67304445031

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

<<<<<<< HEAD
## Error común

Si ves:
`FileNotFoundError: No se encontró archivo de entrada: /ruta/a/tu_workbook.xlsx`

significa que usaste una ruta de ejemplo. Debes reemplazarla por una ruta real, por ejemplo:
`/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`.

## Licencia
MIT. Ver [LICENSE](LICENSE).
=======
The generated files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will be saved in the current working directory. In Google Colab, they are also offered as direct downloads once processing is complete.
>>>>>>> theirs
>>>>>>> 6b9ee2bf3f51aff72dcb8254282fd67304445031

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

This repository contains a single script `codigo.py` used to prepare the "Avance Curricular" reports required for SIES 2025. It reads an Excel workbook with information about students, careers and historical enrolment and generates two formatted Excel files:

- `A. C. Carrera 2024.xlsx`
- `A. C. Matrícula 2024.xlsx`

Both output files are written locally when running the script on your computer or saved to `/content/` when executed on Google Colab. The script also takes care of formatting columns and, in Colab, triggers a download of the results.

## Requirements

- Python 3.9 or newer
- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)
- [openpyxl](https://openpyxl.readthedocs.io/)
- `google.colab` (only when running on Colab)

Install the dependencies with:

```bash
pip install pandas numpy openpyxl
```

## Running locally

1. Place the Excel file to process somewhere on your computer.
2. Execute the script:

```bash
python codigo.py
```

3. When prompted `Ruta de archivo .xlsx:`, provide the path to your workbook.
4. After processing finishes, two Excel files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will appear in the same directory.

## Running in Google Colab

1. Upload this repository or the `codigo.py` file to a new Colab notebook.
2. Install the dependencies:

```python
!pip install pandas numpy openpyxl
```

3. Run the script inside a cell:

```python
%run codigo.py
```

When executed in Colab, a file upload dialog will appear to select your Excel file. Once the script finishes, the resulting Excel files are automatically downloaded to your computer.

## Uploading the input file

Whether you run the script locally or on Colab, you need an Excel workbook that includes the sheets required by the SIES format (Carreras, Matrícula, Históricos and Equivalencia). On Colab, use the upload widget that appears when running the script. Locally, simply provide the path when prompted.

## Downloading results

The generated files `A. C. Carrera 2024.xlsx` and `A. C. Matrícula 2024.xlsx` will be saved in the current working directory. In Google Colab, they are also offered as direct downloads once processing is complete.
>>>>>>> theirs

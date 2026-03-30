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

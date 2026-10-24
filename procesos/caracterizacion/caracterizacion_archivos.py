"""Lightweight integrity checks shared by input selection and preflight."""
from pathlib import Path
from zipfile import BadZipFile, ZipFile, is_zipfile


class InputFileValidationError(ValueError):
    pass


def validate_input_file(path):
    file = Path(path).expanduser().resolve()
    if not file.is_file():
        raise InputFileValidationError(f'Archivo de entrada no encontrado: {file}')
    if file.stat().st_size == 0:
        raise InputFileValidationError(
            f'Archivo de entrada vacio (0 bytes): {file.name}. '
            'No contiene datos ni estructura. Vuelve a exportar o descargar el archivo original.')
    if file.suffix.lower() in {'.xlsx', '.xlsm'}:
        if not is_zipfile(file):
            raise InputFileValidationError(
                f'Excel invalido: {file.name}. Su contenido no corresponde a XLSX/XLSM; '
                'cambiar la extension no lo convierte en Excel.')
        try:
            with ZipFile(file) as archive:
                if not {'[Content_Types].xml', 'xl/workbook.xml'}.issubset(archive.namelist()):
                    raise InputFileValidationError(f'Excel invalido: {file.name}; falta la estructura del libro.')
                if archive.testzip() is not None:
                    raise InputFileValidationError(f'Excel danado: {file.name}; descarga incompleta o corrupta.')
        except (BadZipFile, OSError, EOFError) as error:
            raise InputFileValidationError(f'Excel ilegible: {file.name}; {error}') from error
    return file

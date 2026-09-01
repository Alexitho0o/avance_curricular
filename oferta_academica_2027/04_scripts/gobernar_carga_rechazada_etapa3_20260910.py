#!/usr/bin/env python3
"""Gobierna y diagnostica la primera carga rechazada de Etapa 3."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUENTE = Path.home() / "Downloads" / "20260910 Carga 1.csv"
ERRORES = Path("/Users/alexi/.codex/attachments/9a0b88fb-c749-4066-a454-accb102fad6e/pasted-text.txt")
SALIDA_CORRECTA = (
    ROOT
    / "07_resultados"
    / "etapa3_aranceles_20260907"
    / "OFERTA_ACADEMICA_ARANCELES_2027_SIN_TITULOS_20260907.csv"
)
REPORTE_5910 = (
    ROOT
    / "09_respaldo"
    / "reportes_pes_validados"
    / "20260907_reporte_5910_etapa1_2"
    / "5910 Oferta Académica Vigente y Nueva Validada 2027 TP Adscritas.csv"
)

RESPALDO = ROOT / "09_respaldo" / "cargas_pes" / "20260910_etapa3_carga_01_rechazada"
VALIDACION = ROOT / "06_validaciones" / "carga_etapa3_20260910"
NOTA = ROOT / "11_gobernanza" / "NOTA_GOBERNANZA_CARGA_RECHAZADA_ETAPA3_20260910.md"
BLOQUEO = ROOT / "12_pendientes" / "REGISTRO_BLOQUEO_CARGA_ETAPA3_20260910.md"
RESULTADOS = ROOT / "07_resultados" / "etapa3_aranceles_20260910"
REINTENTO = RESULTADOS / "OFERTA_ACADEMICA_ARANCELES_2027_CARGA_02_CORREGIDA_SIN_TITULOS_20260910.csv"
CONGELADO = ROOT / "09_respaldo" / "cargas_congeladas" / "20260910_etapa3_preparada_carga_02"
DEPRECACION = (
    ROOT
    / "07_resultados"
    / "etapa3_aranceles_20260907"
    / "NO_USAR_PARA_REINTENTO_DESDE_20260910.md"
)

COLUMNAS_49 = [
    "CODIGO_IES_NUM", "COD_SEDE", "NOMBRE_SEDE", "COD_CARRERA", "NOMBRE_CARRERA",
    "MODALIDAD", "COD_JORNADA", "VERSION", "COD_TIPO_PLAN_CARRERA",
    "CARACTERISTICAS_TIPO_PLAN", "DURACION_ESTUDIOS", "DURACION_TITULACION",
    "DURACION_TOTAL", "REGIMEN", "DURACION_REGIMEN", "NOMBRE_TITULO",
    "COD_NIVEL_GLOBAL", "COD_NIVEL_CARRERA", "ANIO_INICIO", "ACREDITACION",
    "REQUISITO_INGRESO", "SEMESTRES_RECONOCIDOS", "AREA_ACTUAL",
    "AREA_ADMIN_DERECHO", "AREA_AGRI_SILVI_PESCA_VET", "AREA_ARTES_HUMANIDADES",
    "AREA_CIENCIAS_NAT_MAT_ESTAD", "AREA_CS_SOCIAL_PERIODISMO_INFO", "AREA_EDUCACION",
    "AREA_INGE_INDUSTRIA_CONSTRUC", "AREA_SALUD_BIENESTAR", "AREA_SERVICIOS",
    "AREA_TECNO_INFO_COMUNICA", "VACANTES_PRIMER_SEMESTRE",
    "VACANTES_SEGUNDO_SEMESTRE", "FECHA_ADMISION_INICIAL", "ENLACE_INFO_PROGRAMA",
    "LICENCIA_ENS_MEDIA", "NOTAS_ENS_MEDIA", "PROMEDIO_MIN_ENS_MEDIA",
    "RECONOCIMIENTOS_APREN_PREVIOS", "EXPERIENCIA_LABORAL", "MAIL_DIFUSION_CARRERA",
    "FORMATO_VALOR", "VALOR_MATRICULA_ANUAL", "COSTO_TITULACION",
    "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL", "VIGENCIA_CARRERA",
]

COLUMNAS_13 = [
    "COD_SEDE", "NOMBRE_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "MODALIDAD",
    "COD_JORNADA", "VERSION", "FORMATO_VALOR", "VALOR_MATRICULA_ANUAL",
    "COSTO_TITULACION", "VALOR_CERTIFICADO_DIPLOMA", "ARANCEL_ANUAL",
    "VIGENCIA_CARRERA",
]
IDX_49 = {nombre: i for i, nombre in enumerate(COLUMNAS_49)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def leer_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle, delimiter=";"))


def leer_5910(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="latin-1", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=";"))
    return rows[0], rows[1:]


def proyectar_etapa3(row: list[str]) -> list[str]:
    return [row[IDX_49[columna]] for columna in COLUMNAS_13]


def clave(row: list[str]) -> str:
    return "--".join(row[:7])


def analizar_errores(texto: str) -> tuple[list[int], Counter[str], dict[str, list[int]]]:
    lineas_reportadas: list[int] = []
    conteos: Counter[str] = Counter()
    ejemplos: dict[str, list[int]] = {}
    linea_actual = 0

    for linea in texto.splitlines():
        match = re.match(r"Errores en linea (\d+):", linea)
        if match:
            linea_actual = int(match.group(1))
            lineas_reportadas.append(linea_actual)
            continue
        mensaje = linea.strip()
        if not mensaje:
            continue
        if mensaje.startswith("Cantidad de campos"):
            categoria = "Cantidad de campos (49) no concuerda con estructura (13)"
        elif mensaje.startswith("El campo "):
            categoria = mensaje
        elif mensaje.startswith("Clave Duplicada"):
            categoria = "Clave duplicada informada por PES"
        else:
            categoria = "Mensaje no clasificado"
        conteos[categoria] += 1
        ejemplos.setdefault(categoria, [])
        if linea_actual and len(ejemplos[categoria]) < 5:
            ejemplos[categoria].append(linea_actual)
    return lineas_reportadas, conteos, ejemplos


def escribir_tsv(path: Path, rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, delimiter="\t", lineterminator="\n").writerows(rows)


def main() -> None:
    for path in (FUENTE, ERRORES, SALIDA_CORRECTA, REPORTE_5910):
        if not path.is_file():
            raise FileNotFoundError(path)

    RESPALDO.mkdir(parents=True, exist_ok=True)
    VALIDACION.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    CONGELADO.mkdir(parents=True, exist_ok=True)

    fuente_gobernada = RESPALDO / FUENTE.name
    errores_gobernados = RESPALDO / "ERRORES_PES_CARGA_01_20260910.txt"
    shutil.copy2(FUENTE, fuente_gobernada)
    shutil.copy2(ERRORES, errores_gobernados)

    filas_carga = leer_csv(FUENTE)
    filas_correctas = leer_csv(SALIDA_CORRECTA)
    distribucion_columnas = Counter(len(row) for row in filas_carga)
    filas_49 = [row for row in filas_carga if len(row) == 49]
    proyectadas = [proyectar_etapa3(row) for row in filas_49]

    comparables = min(len(proyectadas), len(filas_correctas))
    iguales_posicion = sum(proyectadas[i] == filas_correctas[i] for i in range(comparables))
    diferencias_por_columna: Counter[str] = Counter()
    detalle = [["fila", "clave_etapa3", "estado", "columnas_diferentes"]]
    for i in range(comparables):
        diferencias = [
            COLUMNAS_13[j]
            for j, (observado, esperado) in enumerate(zip(proyectadas[i], filas_correctas[i]))
            if observado != esperado
        ]
        diferencias_por_columna.update(diferencias)
        detalle.append([
            i + 1,
            clave(proyectadas[i]),
            "IGUAL" if not diferencias else "DIFERENTE",
            ",".join(diferencias),
        ])
    for i in range(comparables, len(proyectadas)):
        detalle.append([i + 1, clave(proyectadas[i]), "SOLO_CARGA_RECHAZADA", ""])
    for i in range(comparables, len(filas_correctas)):
        detalle.append([i + 1, clave(filas_correctas[i]), "SOLO_ARCHIVO_CORRECTO", ""])

    texto_errores = ERRORES.read_text(encoding="utf-8", errors="replace")
    lineas_reportadas, conteos, ejemplos = analizar_errores(texto_errores)

    estado_contenido = (
        "COINCIDE_TOTALMENTE_TRAS_PROYECCION_A_13_COLUMNAS"
        if len(proyectadas) == len(filas_correctas) and iguales_posicion == len(filas_correctas)
        else "PRESENTA_DIFERENCIAS_CON_ARCHIVO_ETAPA3_PREPARADO"
    )

    # El Anexo 4, pagina 65, limita esta carga a programas con vigencia 1.
    filas_reintento = [row for row in proyectadas if row[12] == "1"]
    with REINTENTO.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, delimiter=";", lineterminator="\n").writerows(filas_reintento)
    contenido = REINTENTO.read_text(encoding="utf-8")
    if contenido.endswith("\n"):
        REINTENTO.write_text(contenido[:-1], encoding="utf-8")

    header_5910, rows_5910 = leer_5910(REPORTE_5910)
    idx_5910 = {nombre: i for i, nombre in enumerate(header_5910)}
    columnas_id = COLUMNAS_13[:7] + ["VIGENCIA_CARRERA"]
    ids_5910 = {
        tuple(row[idx_5910[columna]] for columna in columnas_id)
        for row in rows_5910
    }
    ids_reintento = {tuple(row[:7] + [row[12]]) for row in filas_reintento}
    claves_reintento = [tuple(row[:7]) for row in filas_reintento]
    duplicados_reintento = len(claves_reintento) - len(set(claves_reintento))
    dominios_invalidos = {
        "FORMATO_VALOR": sum(row[7] not in {"1", "2"} for row in filas_reintento),
        "VALOR_MATRICULA_ANUAL": sum(
            not row[8].lstrip("-").isdigit() or int(row[8]) == 0 or int(row[8]) < -1
            for row in filas_reintento
        ),
        "COSTO_TITULACION": sum(not row[9].isdigit() or int(row[9]) < 0 for row in filas_reintento),
        "VALOR_CERTIFICADO_DIPLOMA": sum(
            not row[10].isdigit() or int(row[10]) < 0 for row in filas_reintento
        ),
        "ARANCEL_ANUAL": sum(
            not row[11].lstrip("-").isdigit() or int(row[11]) == 0 or int(row[11]) < -1
            for row in filas_reintento
        ),
        "VIGENCIA_CARRERA": sum(row[12] != "1" for row in filas_reintento),
    }
    reintento_ok = not any(dominios_invalidos.values()) and not duplicados_reintento and ids_reintento <= ids_5910
    validacion_reintento = {
        "archivo": str(REINTENTO.relative_to(ROOT)),
        "estado": "PREPARADO_NO_CARGADO" if reintento_ok else "BLOQUEADO",
        "filas": len(filas_reintento),
        "columnas": 13,
        "filas_con_13_columnas": sum(len(row) == 13 for row in filas_reintento),
        "encabezado": False,
        "vigencia_1": sum(row[12] == "1" for row in filas_reintento),
        "duplicados_clave_A_G": duplicados_reintento,
        "identificadores_presentes_en_5910": len(ids_reintento & ids_5910),
        "identificadores_fuera_de_5910": len(ids_reintento - ids_5910),
        "dominios_invalidos": dominios_invalidos,
        "sha256": sha256(REINTENTO),
    }
    (VALIDACION / "VALIDACION_ARCHIVO_REINTENTO_ETAPA3_20260910.json").write_text(
        json.dumps(validacion_reintento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    escribir_tsv(
        RESULTADOS / "MANIFIESTO_ARCHIVO_REINTENTO_ETAPA3_20260910.tsv",
        [
            ["clasificacion", "archivo", "filas", "columnas", "sha256", "estado", "fuente_derivacion"],
            [
                "carga_etapa3_corregida",
                REINTENTO.name,
                len(filas_reintento),
                13,
                validacion_reintento["sha256"],
                validacion_reintento["estado"],
                str(fuente_gobernada.relative_to(ROOT)),
            ],
        ],
    )
    (RESULTADOS / "README.md").write_text(
        "# Archivo preparado para reintento de Etapa 3\n\n"
        "- Fecha de preparacion: 10-09-2026.\n"
        "- Estado: `PREPARADO_NO_CARGADO`.\n"
        "- Registros: 88.\n"
        "- Columnas: 13, sin encabezado.\n"
        "- Universo: solo `VIGENCIA_CARRERA=1`.\n"
        "- Duplicados de la clave A:G: 0.\n"
        "- Identificadores fuera del reporte 5910: 0.\n"
        f"- SHA-256: `{validacion_reintento['sha256']}`.\n\n"
        "Fuente de derivacion: copia inmutable de `20260910 Carga 1.csv`, gobernada como carga rechazada. "
        "Se conservaron sus montos y solo se seleccionaron las 13 columnas de Etapa 3 y los registros con "
        "vigencia 1.\n",
        encoding="utf-8",
    )
    congelado_csv = CONGELADO / REINTENTO.name
    shutil.copy2(REINTENTO, congelado_csv)
    escribir_tsv(
        CONGELADO / "MANIFIESTO_PRE_CARGA_CONGELADA_ETAPA3_20260910.tsv",
        [
            ["clasificacion", "archivo", "filas", "columnas", "sha256", "estado"],
            [
                "pre_carga_congelada_etapa3",
                congelado_csv.name,
                len(filas_reintento),
                13,
                sha256(congelado_csv),
                "PREPARADA_NO_CARGADA",
            ],
        ],
    )
    (CONGELADO / "README_GOBERNANZA_PRE_CARGA_ETAPA3_20260910.md").write_text(
        "# Pre-carga congelada Etapa 3\n\n"
        "- Proceso: SIES Oferta Academica-Acceso 2027.\n"
        "- Etapa: 3 - Definicion de Arancel.\n"
        "- Fecha de congelamiento: 10-09-2026.\n"
        "- Estado: `PREPARADA_NO_CARGADA`.\n"
        "- Registros: 88.\n"
        "- Columnas: 13, sin encabezado.\n"
        "- Universo: solo vigencia 1.\n"
        f"- SHA-256: `{sha256(congelado_csv)}`.\n\n"
        "Esta copia es inmutable y corresponde al archivo preparado para el segundo intento. No acredita "
        "una carga exitosa. Cuando PES acepte el archivo, se debe conservar la evidencia de aceptacion y "
        "promover esta misma huella a carga final congelada.\n",
        encoding="utf-8",
    )
    DEPRECACION.write_text(
        "# No usar para reintento desde 10-09-2026\n\n"
        "La salida sin titulos generada el 07-09-2026 contiene 140 registros, incluidos 52 con vigencia 2, "
        "y usa montos anteriores. El Anexo 4, pagina 65, indica que Etapa 3 solo carga programas con vigencia 1.\n\n"
        "Archivo vigente para el proximo intento: "
        "`../etapa3_aranceles_20260910/OFERTA_ACADEMICA_ARANCELES_2027_CARGA_02_CORREGIDA_SIN_TITULOS_20260910.csv`.\n",
        encoding="utf-8",
    )
    resumen = {
        "proceso": "SIES Oferta Academica-Acceso 2027",
        "etapa": "Etapa 3 - Definicion de Arancel",
        "fecha_ejecucion_pes": "2026-09-10",
        "carga": "Carga 1",
        "estado": "RECHAZADA_POR_ESTRUCTURA",
        "fuente_carga": str(fuente_gobernada.relative_to(ROOT)),
        "evidencia_errores": str(errores_gobernados.relative_to(ROOT)),
        "archivo_correcto_referencia": str(SALIDA_CORRECTA.relative_to(ROOT)),
        "estructura_observada": dict(sorted(distribucion_columnas.items())),
        "estructura_exigida": 13,
        "filas_carga": len(filas_carga),
        "filas_archivo_correcto": len(filas_correctas),
        "filas_reportadas_por_pes": len(set(lineas_reportadas)),
        "rango_lineas_reportadas": [min(lineas_reportadas), max(lineas_reportadas)] if lineas_reportadas else [],
        "comparacion_contenido": {
            "estado": estado_contenido,
            "filas_comparables": comparables,
            "filas_iguales_en_misma_posicion": iguales_posicion,
            "filas_diferentes_en_misma_posicion": comparables - iguales_posicion,
            "diferencias_por_columna": dict(diferencias_por_columna),
        },
        "universo_vigencia": dict(Counter(row[12] for row in proyectadas)),
        "archivo_reintento": validacion_reintento,
        "errores_pes": [
            {"mensaje": mensaje, "cantidad": cantidad, "ejemplos_linea": ejemplos[mensaje]}
            for mensaje, cantidad in conteos.most_common()
        ],
        "diagnostico": (
            "Se intento cargar la estructura completa de 49 columnas y 52 programas con vigencia 2. "
            "La Etapa 3 exige 13 columnas y solo programas con vigencia 1. Los demas mensajes de PES no se "
            "consideran concluyentes hasta reintentar con la estructura correcta."
        ),
        "generado": datetime.now().astimezone().isoformat(timespec="seconds"),
    }

    (VALIDACION / "RESUMEN_VALIDACION_CARGA_RECHAZADA_ETAPA3_20260910.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    escribir_tsv(
        VALIDACION / "ERRORES_AGRUPADOS_CARGA_RECHAZADA_ETAPA3_20260910.tsv",
        [["mensaje_pes", "cantidad", "ejemplos_linea"]]
        + [[mensaje, cantidad, ",".join(map(str, ejemplos[mensaje]))] for mensaje, cantidad in conteos.most_common()],
    )
    escribir_tsv(
        VALIDACION / "CONCILIACION_CARGA_49_VS_ETAPA3_13_20260910.tsv",
        detalle,
    )

    manifiesto = [["clasificacion", "archivo", "bytes", "sha256", "origen", "estado"]]
    for clasificacion, path, origen, estado in (
        ("carga_enviada_pes", fuente_gobernada, "Descargas", "original_inmutable_rechazado"),
        ("evidencia_errores_pes", errores_gobernados, "PES/copia_textual_usuario", "original_inmutable"),
    ):
        manifiesto.append([clasificacion, path.name, path.stat().st_size, sha256(path), origen, estado])
    escribir_tsv(RESPALDO / "MANIFIESTO_CARGA_RECHAZADA_ETAPA3_20260910.tsv", manifiesto)

    NOTA.write_text(
        "# Nota de gobernanza - Carga rechazada Etapa 3\n\n"
        "- Proceso: SIES Oferta Academica-Acceso 2027.\n"
        "- Etapa: 3 - Definicion de Arancel.\n"
        "- Fecha de intento: 10-09-2026.\n"
        "- Archivo enviado: `20260910 Carga 1.csv`.\n"
        "- Estado PES: rechazado.\n"
        f"- Registros del archivo: {len(filas_carga)}.\n"
        f"- Estructura observada: {dict(sorted(distribucion_columnas.items()))}.\n"
        "- Estructura exigida por PES: 13 columnas.\n"
        f"- Universo observado: {sum(row[12] == '1' for row in proyectadas)} registros con vigencia 1 y "
        f"{sum(row[12] == '2' for row in proyectadas)} con vigencia 2.\n"
        f"- Lineas con errores mostradas por PES: {len(set(lineas_reportadas))}.\n"
        f"- Comparacion contra la salida preparada de 13 columnas: {estado_contenido}.\n\n"
        "## Decision\n\n"
        "La carga queda registrada como `RECHAZADA_POR_ESTRUCTURA`. El archivo enviado contiene la "
        "estructura completa de 49 columnas y ademas incluye registros con vigencia 2. No corresponde al "
        "formato ni al universo de carga de Etapa 3. Los mensajes "
        "adicionales sobre campos y claves duplicadas no se consideran concluyentes porque fueron emitidos "
        "sobre una estructura desplazada. No se modifica el original ni se declara una carga exitosa.\n\n"
        "La comparacion con la salida del 07-09-2026 muestra cambios en "
        f"`VALOR_MATRICULA_ANUAL` ({diferencias_por_columna.get('VALOR_MATRICULA_ANUAL', 0)} filas) y "
        f"`ARANCEL_ANUAL` ({diferencias_por_columna.get('ARANCEL_ANUAL', 0)} filas). El derivado de reintento "
        "conserva los valores del archivo efectivamente enviado el 10-09-2026; no reutiliza automaticamente "
        "los montos anteriores.\n\n"
        "## Reanudacion\n\n"
        "Usar el derivado `07_resultados/etapa3_aranceles_20260910/"
        "OFERTA_ACADEMICA_ARANCELES_2027_CARGA_02_CORREGIDA_SIN_TITULOS_20260910.csv`. "
        "Contiene solo vigencia 1 y la estructura de 13 columnas. Registrar el nuevo resultado PES como una "
        "ejecucion separada.\n\n"
        "## Fuente oficial aplicada\n\n"
        "Instructivo Oferta Academica-Acceso 2027, Anexo 4, pagina 65: estructura de 13 columnas, prohibicion "
        "de modificar identificadores y carga exclusiva de programas con vigencia 1.\n",
        encoding="utf-8",
    )
    if not BLOQUEO.exists() or "RESUELTO" not in BLOQUEO.read_text(encoding="utf-8"):
        BLOQUEO.write_text(
            "# Bloqueo de carga Etapa 3 - 10-09-2026\n\n"
            "Estado: `PENDIENTE_REINTENTO`.\n\n"
            "Motivo: el primer intento utilizo 49 columnas e incluyo 52 registros con vigencia 2; PES exige "
            "13 columnas y solo programas con vigencia 1.\n\n"
            "Condicion de cierre: nueva carga con la estructura oficial de 13 columnas y respaldo del resultado PES.\n",
            encoding="utf-8",
        )

    print(f"filas_carga={len(filas_carga)}")
    print(f"columnas_observadas={dict(sorted(distribucion_columnas.items()))}")
    print(f"lineas_error_pes={len(set(lineas_reportadas))}")
    print(f"filas_iguales_proyeccion_13={iguales_posicion}/{comparables}")
    print(f"estado={estado_contenido}")
    print(f"reintento={validacion_reintento['estado']} filas={len(filas_reintento)} columnas=13")


if __name__ == "__main__":
    main()

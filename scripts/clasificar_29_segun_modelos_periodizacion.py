#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import json
import re
import unicodedata

import pandas as pd


RAIZ = Path(
    "/Users/alexi/Documents/GitHub/avance_curricular"
).resolve()

FUENTE = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "CRUCE_29_PROMEDIOALUMNOS_AVANCE_20260703_122716"
    / "02_RESULTADOS"
    / "CRUCE_29_PROMEDIOALUMNOS_AVANCE.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"CLASIFICACION_29_MODELOS_PERIODIZACION_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"

RESULTADOS.mkdir(parents=True, exist_ok=False)
AUDITORIAS.mkdir(parents=True, exist_ok=True)


def norm(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(r"\s+", "", texto)


def separar(valor):
    return sorted({
        norm(elemento)
        for elemento in re.split(
            r"\s*\|\s*",
            str(valor or ""),
        )
        if norm(elemento)
    })


if not FUENTE.exists():
    raise RuntimeError(
        f"No existe el Excel de origen: {FUENTE}"
    )


libro = pd.ExcelFile(
    FUENTE,
    engine="openpyxl",
)

requeridas = {
    "CRUCE_29",
    "MODELOS_PERIODIZACION",
}

faltantes = requeridas - set(libro.sheet_names)

if faltantes:
    raise RuntimeError(
        "Faltan hojas requeridas: "
        + " | ".join(sorted(faltantes))
    )


casos = pd.read_excel(
    FUENTE,
    sheet_name="CRUCE_29",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

modelos = pd.read_excel(
    FUENTE,
    sheet_name="MODELOS_PERIODIZACION",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

if len(casos) != 29:
    raise RuntimeError(
        f"Se esperaban 29 casos y se encontraron {len(casos)}."
    )

if len(modelos) != 2:
    raise RuntimeError(
        f"Se esperaban 2 modelos y se encontraron {len(modelos)}."
    )


for columna in [
    "CODCLI_MODELO",
    "CARRERA_MODELO",
    "PLAN_MODELO",
    "TIPO_PERIODIZACION_MODELO",
    "REGLA_OBSERVADA",
]:
    if columna not in modelos.columns:
        modelos[columna] = ""


modelos["CODCLI_MODELO_NORM"] = (
    modelos["CODCLI_MODELO"].map(norm)
)

modelos["CARRERA_MODELO_NORM"] = (
    modelos["CARRERA_MODELO"].map(norm)
)

modelos["PLAN_MODELO_NORM"] = (
    modelos["PLAN_MODELO"].map(norm)
)


filas = []

for _, caso in casos.iterrows():
    codcli = separar(
        caso.get(
            "CODCLI_PROMEDIOS_LISTA",
            "",
        )
    )

    carreras = set(
        separar(
            caso.get(
                "CARRERAS_PROMEDIOS_LISTA",
                "",
            )
        )
    )

    planes = set(
        separar(
            caso.get(
                "PLANES_PROMEDIOS_LISTA",
                "",
            )
        )
    )

    carrera_5809 = norm(
        caso.get(
            "CODCARR_PLAN_VIGENTE",
            "",
        )
    )

    carrera_evidencia = norm(
        caso.get(
            "CODCARPR_EVIDENCIA",
            "",
        )
    )

    if carrera_5809:
        carreras.add(carrera_5809)

    if carrera_evidencia:
        carreras.add(carrera_evidencia)

    coincidencias = []

    for _, modelo in modelos.iterrows():
        codcli_modelo = modelo[
            "CODCLI_MODELO_NORM"
        ]

        carrera_modelo = modelo[
            "CARRERA_MODELO_NORM"
        ]

        plan_modelo = modelo[
            "PLAN_MODELO_NORM"
        ]

        coincide_codcli = (
            codcli_modelo
            and codcli_modelo in codcli
        )

        coincide_plan = (
            plan_modelo
            and plan_modelo in planes
        )

        coincide_carrera = (
            carrera_modelo
            and carrera_modelo in carreras
        )

        if coincide_codcli:
            nivel_respaldo = "CODCLI_EXACTO"

        elif coincide_plan and coincide_carrera:
            nivel_respaldo = "PLAN_Y_CARRERA"

        elif coincide_plan:
            nivel_respaldo = "SOLO_PLAN"

        elif coincide_carrera:
            nivel_respaldo = "SOLO_CARRERA"

        else:
            nivel_respaldo = "SIN_COINCIDENCIA"

        coincidencias.append({
            "CODCLI_MODELO":
            modelo["CODCLI_MODELO"],

            "CARRERA_MODELO":
            modelo["CARRERA_MODELO"],

            "PLAN_MODELO":
            modelo["PLAN_MODELO"],

            "TIPO_PERIODIZACION":
            modelo["TIPO_PERIODIZACION_MODELO"],

            "REGLA_OBSERVADA":
            modelo["REGLA_OBSERVADA"],

            "NIVEL_RESPALDO":
            nivel_respaldo,
        })

    exactos = [
        item
        for item in coincidencias
        if item["NIVEL_RESPALDO"] == "CODCLI_EXACTO"
    ]

    plan_carrera = [
        item
        for item in coincidencias
        if item["NIVEL_RESPALDO"] == "PLAN_Y_CARRERA"
    ]

    solo_plan = [
        item
        for item in coincidencias
        if item["NIVEL_RESPALDO"] == "SOLO_PLAN"
    ]

    solo_carrera = [
        item
        for item in coincidencias
        if item["NIVEL_RESPALDO"] == "SOLO_CARRERA"
    ]

    if len(exactos) == 1:
        elegido = exactos[0]

        estado = (
            "MODELO_CONFIRMADO_POR_CODCLI"
        )

        puede_convertir = (
            "SI_PARA_ESTE_ESTUDIANTE"
        )

        fundamento = (
            "El CODCLI del estudiante coincide exactamente "
            "con el CODCLI del reporte de Avance de Malla."
        )

    elif len(plan_carrera) == 1:
        elegido = plan_carrera[0]

        estado = (
            "CANDIDATO_POR_PLAN_Y_CARRERA"
        )

        puede_convertir = (
            "NO_REQUIERE_CONFIRMAR_QUE_EL_PLAN_COMPARTE_LA_ESTRUCTURA"
        )

        fundamento = (
            "El plan y la carrera coinciden con un modelo, "
            "pero el CODCLI no aparece directamente en el reporte."
        )

    elif len(solo_plan) == 1:
        elegido = solo_plan[0]

        estado = (
            "CANDIDATO_SOLO_POR_PLAN"
        )

        puede_convertir = "NO"

        fundamento = (
            "Solo existe coincidencia de plan. "
            "Falta confirmar la carrera y la estructura aplicable."
        )

    elif len(solo_carrera) == 1:
        elegido = solo_carrera[0]

        estado = (
            "REFERENCIA_SOLO_POR_CARRERA"
        )

        puede_convertir = "NO"

        fundamento = (
            "Solo coincide la carrera. La carrera no demuestra "
            "que el estudiante pertenezca al mismo plan ni "
            "a la misma periodización."
        )

    elif (
        len(plan_carrera)
        + len(solo_plan)
        + len(solo_carrera)
    ) > 1:
        elegido = {
            "CODCLI_MODELO": "",
            "CARRERA_MODELO": "",
            "PLAN_MODELO": "",
            "TIPO_PERIODIZACION": "",
            "REGLA_OBSERVADA": "",
        }

        estado = "AMBIGUO_ENTRE_MODELOS"
        puede_convertir = "NO"

        fundamento = (
            "La evidencia permite relacionar el estudiante "
            "con más de un modelo. No corresponde seleccionar "
            "una periodización automáticamente."
        )

    else:
        elegido = {
            "CODCLI_MODELO": "",
            "CARRERA_MODELO": "",
            "PLAN_MODELO": "",
            "TIPO_PERIODIZACION": "",
            "REGLA_OBSERVADA": "",
        }

        estado = "SIN_MODELO_DEMOSTRADO"
        puede_convertir = "NO"

        fundamento = (
            "No existe coincidencia demostrada por CODCLI, "
            "plan o carrera con los dos reportes disponibles."
        )

    fila = caso.to_dict()

    fila.update({
        "ESTADO_ASOCIACION_MODELO":
        estado,

        "PUEDE_CONVERTIR_NIVEL":
        puede_convertir,

        "CODCLI_MODELO_ASOCIADO":
        elegido["CODCLI_MODELO"],

        "CARRERA_MODELO_ASOCIADA":
        elegido["CARRERA_MODELO"],

        "PLAN_MODELO_ASOCIADO":
        elegido["PLAN_MODELO"],

        "TIPO_PERIODIZACION_ASOCIADA":
        elegido["TIPO_PERIODIZACION"],

        "REGLA_CONVERSION_ASOCIADA":
        elegido["REGLA_OBSERVADA"],

        "FUNDAMENTO_ASOCIACION":
        fundamento,
    })

    filas.append(fila)


resultado = pd.DataFrame(filas)

confirmados = resultado[
    resultado[
        "ESTADO_ASOCIACION_MODELO"
    ].eq("MODELO_CONFIRMADO_POR_CODCLI")
].copy()

candidatos = resultado[
    resultado[
        "ESTADO_ASOCIACION_MODELO"
    ].isin([
        "CANDIDATO_POR_PLAN_Y_CARRERA",
        "CANDIDATO_SOLO_POR_PLAN",
        "REFERENCIA_SOLO_POR_CARRERA",
    ])
].copy()

pendientes = resultado[
    resultado[
        "PUEDE_CONVERTIR_NIVEL"
    ].ne("SI_PARA_ESTE_ESTUDIANTE")
].copy()


resumen = (
    resultado[
        "ESTADO_ASOCIACION_MODELO"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_29",
        "RESULTADO": (
            "OK"
            if len(resultado) == 29
            else "ERROR"
        ),
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "CONFIRMADOS_CODCLI",
        "RESULTADO": (
            "OK"
            if len(confirmados) == 2
            else "REVISAR"
        ),
        "DETALLE": len(confirmados),
    },
    {
        "VALIDACION": "CONVERSION_AUTOMATICA_OTROS_27",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
    {
        "VALIDACION": "NIVELES_MODIFICADOS",
        "RESULTADO": "OK",
        "DETALLE": 0,
    },
    {
        "VALIDACION": "FUENTES_MODIFICADAS",
        "RESULTADO": "OK",
        "DETALLE": "NO",
    },
])


resultado.to_csv(
    RESULTADOS
    / "01_CLASIFICACION_29_MODELOS.tsv",
    sep="\t",
    index=False,
)

confirmados.to_csv(
    RESULTADOS
    / "02_CONFIRMADOS_POR_CODCLI.tsv",
    sep="\t",
    index=False,
)

candidatos.to_csv(
    RESULTADOS
    / "03_CANDIDATOS_NO_CONFIRMADOS.tsv",
    sep="\t",
    index=False,
)

pendientes.to_csv(
    RESULTADOS
    / "04_PENDIENTES_SIN_CONVERSION.tsv",
    sep="\t",
    index=False,
)

validaciones.to_csv(
    AUDITORIAS
    / "01_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


excel = (
    RESULTADOS
    / "CLASIFICACION_29_MODELOS_PERIODIZACION.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    confirmados.to_excel(
        writer,
        sheet_name="CONFIRMADOS_CODCLI",
        index=False,
    )

    candidatos.to_excel(
        writer,
        sheet_name="CANDIDATOS",
        index=False,
    )

    pendientes.to_excel(
        writer,
        sheet_name="PENDIENTES",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="CLASIFICACION_29",
        index=False,
    )

    modelos.to_excel(
        writer,
        sheet_name="MODELOS_ORIGEN",
        index=False,
    )

    validaciones.to_excel(
        writer,
        sheet_name="VALIDACIONES",
        index=False,
    )

    for hoja in writer.book.worksheets:
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for columna in hoja.columns:
            letra = columna[0].column_letter

            ancho = max(
                len(str(celda.value or ""))
                for celda in columna[:2000]
            )

            hoja.column_dimensions[letra].width = min(
                max(ancho + 2, 12),
                55,
            )


manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia": 2025,
    "universo": 29,
    "jerarquia_asociacion": [
        "CODCLI exacto",
        "plan y carrera",
        "plan",
        "carrera",
    ],
    "confirmados_por_codcli": len(confirmados),
    "niveles_modificados": 0,
    "fuentes_modificadas": False,
    "archivo_carga_generado": False,
}

(SALIDA / "manifest_ejecucion.json").write_text(
    json.dumps(
        manifiesto,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 104)
print("CLASIFICACIÓN DE LOS 29 SEGÚN MODELOS DE PERIODIZACIÓN")
print("=" * 104)

for _, fila in resumen.iterrows():
    print(f"{fila['ESTADO']}: {fila['CASOS']}")

print()
print(f"Confirmados por CODCLI: {len(confirmados)}")
print(f"Pendientes sin conversión automática: {len(pendientes)}")
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Niveles modificados: 0")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 104)

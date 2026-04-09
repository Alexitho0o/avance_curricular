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

FUENTE_CLASIFICACION = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "CLASIFICACION_29_MODELOS_PERIODIZACION_20260703_123007"
    / "02_RESULTADOS"
    / "CLASIFICACION_29_MODELOS_PERIODIZACION.xlsx"
)

PROMEDIOS = (
    RAIZ
    / "avance_curricular_2026"
    / "00_fuentes_congeladas"
    / "CARGA_CONGELADA_20260626_005826"
    / "originales"
    / "PROMEDIOSDEALUMNOS_7804.xlsx"
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"DIAGNOSTICO_27_CODCLI_PLAN_{timestamp}"
)

RESULTADOS = SALIDA / "02_RESULTADOS"
AUDITORIAS = SALIDA / "03_AUDITORIAS"

RESULTADOS.mkdir(parents=True, exist_ok=False)
AUDITORIAS.mkdir(parents=True, exist_ok=True)


def limpiar(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def norm(valor):
    texto = limpiar(valor).upper()

    if re.fullmatch(r"-?\d+\.0", texto):
        texto = texto[:-2]

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(r"\s+", "", texto)


def norm_rut(valor):
    return re.sub(
        r"[^0-9K]",
        "",
        norm(valor),
    )


def separar_lista(valor):
    return sorted({
        norm(elemento)
        for elemento in re.split(
            r"\s*\|\s*",
            limpiar(valor),
        )
        if norm(elemento)
    })


def obtener_columna(df, nombres, obligatoria=False):
    mapa = {
        norm(columna): columna
        for columna in df.columns
    }

    for nombre in nombres:
        clave = norm(nombre)

        if clave in mapa:
            return mapa[clave]

    if obligatoria:
        raise RuntimeError(
            "No se encontró ninguna columna entre: "
            + " | ".join(nombres)
        )

    return None


def extraer_familia_codcli(codcli):
    codigo = norm(codcli)

    if not codigo:
        return ""

    # Ejemplos observados:
    # 20181IECIREOL015 → IECIREOL
    # 20241TCIB027     → TCIB
    coincidencia = re.match(
        r"^\d{5}([A-Z]+)(?:\d+)?$",
        codigo,
    )

    if coincidencia:
        return coincidencia.group(1)

    coincidencia = re.match(
        r"^\d{4,6}([A-Z][A-Z0-9]+)$",
        codigo,
    )

    if coincidencia:
        resto = coincidencia.group(1)

        return re.sub(
            r"\d+$",
            "",
            resto,
        )

    return ""


def extraer_anio_periodo_ingreso(codcli):
    codigo = norm(codcli)

    coincidencia = re.match(
        r"^(\d{4})(\d)",
        codigo,
    )

    if not coincidencia:
        return "", ""

    return (
        coincidencia.group(1),
        coincidencia.group(2),
    )


for ruta in (
    FUENTE_CLASIFICACION,
    PROMEDIOS,
):
    if not ruta.exists():
        raise RuntimeError(
            f"No existe la fuente requerida: {ruta}"
        )


clasificacion = pd.read_excel(
    FUENTE_CLASIFICACION,
    sheet_name="CLASIFICACION_29",
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

pendientes = clasificacion[
    ~clasificacion[
        "ESTADO_ASOCIACION_MODELO"
    ].eq("MODELO_CONFIRMADO_POR_CODCLI")
].copy()

if len(pendientes) != 27:
    raise RuntimeError(
        f"Se esperaban 27 pendientes y se encontraron "
        f"{len(pendientes)}."
    )


datos = pd.read_excel(
    PROMEDIOS,
    sheet_name="DatosAlumnos",
    dtype=object,
    engine="openpyxl",
)

datos = datos.dropna(
    axis=0,
    how="all",
).dropna(
    axis=1,
    how="all",
)

col_rut = obtener_columna(
    datos,
    ["RUT"],
    obligatoria=True,
)

col_codcli = obtener_columna(
    datos,
    ["CODCLI"],
    obligatoria=True,
)

col_carrera = obtener_columna(
    datos,
    ["CODCARPR"],
    obligatoria=True,
)

col_nivel = obtener_columna(
    datos,
    ["NIVEL"],
    obligatoria=True,
)

col_plan = obtener_columna(
    datos,
    [
        "CODPESTUD",
        "PLAN_ESTUDIOS",
        "PLAN",
    ],
    obligatoria=False,
)


base = pd.DataFrame({
    "RUT_DATOS": datos[col_rut].map(norm_rut),
    "CODCLI_DATOS": datos[col_codcli].map(norm),
    "CODCARPR_DATOS": datos[col_carrera].map(norm),
    "NIVEL_DATOS": datos[col_nivel],
    "PLAN_DATOS": (
        datos[col_plan].map(norm)
        if col_plan
        else ""
    ),
    "FILA_DATOSALUMNOS":
    range(2, len(datos) + 2),
})

base = base[
    base["RUT_DATOS"].ne("")
    & base["CODCLI_DATOS"].ne("")
].copy()

base["FAMILIA_CODCLI"] = (
    base["CODCLI_DATOS"]
    .map(extraer_familia_codcli)
)

base[
    [
        "ANIO_INGRESO_CODCLI",
        "PERIODO_INGRESO_CODCLI",
    ]
] = base["CODCLI_DATOS"].apply(
    lambda valor: pd.Series(
        extraer_anio_periodo_ingreso(valor)
    )
)


detalle = pendientes[
    [
        "ID_FILA_5809",
        "RUT_5809_CONTROL",
        "RUT_EVIDENCIA_CRUCE",
        "CODCARR_PLAN_VIGENTE",
        "CODCARPR_EVIDENCIA",
        "NIVEL_EVIDENCIA",
        "ESTADO_ASOCIACION_MODELO",
    ]
].merge(
    base,
    left_on="RUT_EVIDENCIA_CRUCE",
    right_on="RUT_DATOS",
    how="left",
)

detalle["COINCIDE_CARRERA_5809"] = [
    (
        "SI"
        if norm(carrera_datos)
        and norm(carrera_datos) == norm(carrera_5809)
        else "NO"
    )
    for carrera_datos, carrera_5809 in zip(
        detalle["CODCARPR_DATOS"],
        detalle["CODCARR_PLAN_VIGENTE"],
    )
]

detalle["COINCIDE_CARRERA_EVIDENCIA"] = [
    (
        "SI"
        if norm(carrera_datos)
        and norm(carrera_datos) == norm(carrera_evidencia)
        else "NO"
    )
    for carrera_datos, carrera_evidencia in zip(
        detalle["CODCARPR_DATOS"],
        detalle["CODCARPR_EVIDENCIA"],
    )
]


MODELOS = {
    "IECIREOL": {
        "familias_codcli": {
            "IECIREOL",
        },
        "carreras": {
            "IECIREOL",
            "IINF",
        },
        "plan": "IECIREOL",
        "tipo": "ANTIGUA_EXTENDIDA_20_PERIODOS_4_ANIOS",
        "regla": (
            "1-5→Año 1; 6-10→Año 2; "
            "11-15→Año 3; 16-20→Año 4"
        ),
    },
    "TCIB20241": {
        "familias_codcli": {
            "TCIB",
        },
        "carreras": {
            "TCIB",
            "ICIB",
        },
        "plan": "TCIB20241",
        "tipo": "INTENSIVA_7_PERIODOS_3_ANIOS",
        "regla": (
            "1-3→Año 1; 4-6→Año 2; 7→Año 3"
        ),
    },
}


def clasificar_fila(fila):
    familia = norm(
        fila.get(
            "FAMILIA_CODCLI",
            "",
        )
    )

    carrera = norm(
        fila.get(
            "CODCARPR_DATOS",
            "",
        )
    )

    plan = norm(
        fila.get(
            "PLAN_DATOS",
            "",
        )
    )

    candidatos = []

    for nombre, modelo in MODELOS.items():
        coincide_familia = (
            familia in modelo["familias_codcli"]
        )

        coincide_carrera = (
            carrera in modelo["carreras"]
        )

        coincide_plan = (
            plan
            and plan == modelo["plan"]
        )

        if coincide_plan and coincide_familia:
            respaldo = "PLAN_Y_FAMILIA_CODCLI"

        elif coincide_familia and coincide_carrera:
            respaldo = "FAMILIA_CODCLI_Y_CARRERA"

        elif coincide_familia:
            respaldo = "SOLO_FAMILIA_CODCLI"

        elif coincide_plan:
            respaldo = "SOLO_PLAN"

        elif coincide_carrera:
            respaldo = "SOLO_CARRERA"

        else:
            continue

        candidatos.append({
            "modelo": nombre,
            "respaldo": respaldo,
            "tipo": modelo["tipo"],
            "regla": modelo["regla"],
        })

    if len(candidatos) == 0:
        return pd.Series({
            "MODELO_CANDIDATO": "",
            "NIVEL_RESPALDO_MODELO":
            "SIN_MODELO_DEMOSTRADO",
            "TIPO_PERIODIZACION_CANDIDATA": "",
            "REGLA_CANDIDATA": "",
            "PUEDE_CONVERTIR": "NO",
        })

    if len(candidatos) > 1:
        return pd.Series({
            "MODELO_CANDIDATO":
            " | ".join(
                sorted({
                    candidato["modelo"]
                    for candidato in candidatos
                })
            ),
            "NIVEL_RESPALDO_MODELO":
            "AMBIGUO_ENTRE_MODELOS",
            "TIPO_PERIODIZACION_CANDIDATA": "",
            "REGLA_CANDIDATA": "",
            "PUEDE_CONVERTIR": "NO",
        })

    candidato = candidatos[0]

    if candidato["respaldo"] in {
        "PLAN_Y_FAMILIA_CODCLI",
    }:
        puede = (
            "PENDIENTE_CONFIRMAR_QUE_EL_PLAN_HISTORICO_"
            "USA_LA_MISMA_PERIODIZACION"
        )

    else:
        puede = "NO"

    return pd.Series({
        "MODELO_CANDIDATO":
        candidato["modelo"],

        "NIVEL_RESPALDO_MODELO":
        candidato["respaldo"],

        "TIPO_PERIODIZACION_CANDIDATA":
        candidato["tipo"],

        "REGLA_CANDIDATA":
        candidato["regla"],

        "PUEDE_CONVERTIR":
        puede,
    })


clasificacion_detalle = detalle.apply(
    clasificar_fila,
    axis=1,
)

detalle = pd.concat(
    [
        detalle,
        clasificacion_detalle,
    ],
    axis=1,
)


def resumir_estudiante(grupo):
    codcli = sorted({
        norm(valor)
        for valor in grupo["CODCLI_DATOS"]
        if norm(valor)
    })

    familias = sorted({
        norm(valor)
        for valor in grupo["FAMILIA_CODCLI"]
        if norm(valor)
    })

    carreras = sorted({
        norm(valor)
        for valor in grupo["CODCARPR_DATOS"]
        if norm(valor)
    })

    niveles = sorted({
        str(valor).strip()
        for valor in grupo["NIVEL_DATOS"]
        if not pd.isna(valor)
        and str(valor).strip()
    })

    modelos = sorted({
        norm(valor)
        for valor in grupo["MODELO_CANDIDATO"]
        if norm(valor)
    })

    respaldos = sorted({
        norm(valor)
        for valor in grupo["NIVEL_RESPALDO_MODELO"]
        if norm(valor)
    })

    if len(modelos) == 1 and respaldos == [
        "PLANYFAMILIACODCLI"
    ]:
        estado = (
            "CANDIDATO_FUERTE_REQUIERE_VALIDACION_DE_PLAN"
        )

    elif len(modelos) == 1:
        estado = (
            "CANDIDATO_DEBIL_NO_CONVERTIR"
        )

    elif len(modelos) > 1:
        estado = (
            "AMBIGUO_ENTRE_MODELOS"
        )

    else:
        estado = (
            "SIN_MODELO_DEMOSTRADO"
        )

    return pd.Series({
        "N_CODCLI_HISTORICOS": len(codcli),
        "CODCLI_HISTORICOS": " | ".join(codcli),
        "FAMILIAS_CODCLI": " | ".join(familias),
        "CARRERAS_DATOSALUMNOS": " | ".join(carreras),
        "NIVELES_DATOSALUMNOS": " | ".join(niveles),
        "MODELOS_CANDIDATOS": " | ".join(modelos),
        "RESPALDOS_OBSERVADOS": " | ".join(respaldos),
        "ESTADO_DIAGNOSTICO_27": estado,
    })


resumen_27 = (
    detalle.groupby(
        "ID_FILA_5809",
        dropna=False,
    )
    .apply(
        resumir_estudiante,
        include_groups=False,
    )
    .reset_index()
)

resultado = pendientes.merge(
    resumen_27,
    on="ID_FILA_5809",
    how="left",
    validate="one_to_one",
)

if len(resultado) != 27:
    raise RuntimeError(
        "El resultado no conserva los 27 pendientes."
    )


resumen_estados = (
    resultado[
        "ESTADO_DIAGNOSTICO_27"
    ]
    .value_counts(dropna=False)
    .rename_axis("ESTADO")
    .reset_index(name="CASOS")
)


candidatos_fuertes = resultado[
    resultado[
        "ESTADO_DIAGNOSTICO_27"
    ].eq(
        "CANDIDATO_FUERTE_REQUIERE_VALIDACION_DE_PLAN"
    )
].copy()

candidatos_debiles = resultado[
    resultado[
        "ESTADO_DIAGNOSTICO_27"
    ].eq(
        "CANDIDATO_DEBIL_NO_CONVERTIR"
    )
].copy()

sin_modelo = resultado[
    resultado[
        "ESTADO_DIAGNOSTICO_27"
    ].isin([
        "SIN_MODELO_DEMOSTRADO",
        "AMBIGUO_ENTRE_MODELOS",
    ])
].copy()


resultado.to_csv(
    RESULTADOS
    / "01_DIAGNOSTICO_27_PENDIENTES.tsv",
    sep="\t",
    index=False,
)

detalle.to_csv(
    RESULTADOS
    / "02_DETALLE_HISTORICO_CODCLI_27.tsv",
    sep="\t",
    index=False,
)

candidatos_fuertes.to_csv(
    RESULTADOS
    / "03_CANDIDATOS_FUERTES.tsv",
    sep="\t",
    index=False,
)

candidatos_debiles.to_csv(
    RESULTADOS
    / "04_CANDIDATOS_DEBILES.tsv",
    sep="\t",
    index=False,
)

sin_modelo.to_csv(
    RESULTADOS
    / "05_SIN_MODELO_O_AMBIGUOS.tsv",
    sep="\t",
    index=False,
)


validaciones = pd.DataFrame([
    {
        "VALIDACION": "UNIVERSO_27",
        "RESULTADO": (
            "OK"
            if len(resultado) == 27
            else "ERROR"
        ),
        "DETALLE": len(resultado),
    },
    {
        "VALIDACION": "CONVERSION_AUTOMATICA",
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

validaciones.to_csv(
    AUDITORIAS / "01_VALIDACIONES.tsv",
    sep="\t",
    index=False,
)


excel = (
    RESULTADOS
    / "DIAGNOSTICO_27_PENDIENTES_CODCLI_PLAN.xlsx"
)

with pd.ExcelWriter(
    excel,
    engine="openpyxl",
) as writer:
    resumen_estados.to_excel(
        writer,
        sheet_name="RESUMEN",
        index=False,
    )

    resultado.to_excel(
        writer,
        sheet_name="DIAGNOSTICO_27",
        index=False,
    )

    candidatos_fuertes.to_excel(
        writer,
        sheet_name="CANDIDATOS_FUERTES",
        index=False,
    )

    candidatos_debiles.to_excel(
        writer,
        sheet_name="CANDIDATOS_DEBILES",
        index=False,
    )

    sin_modelo.to_excel(
        writer,
        sheet_name="SIN_MODELO_AMBIGUOS",
        index=False,
    )

    detalle.to_excel(
        writer,
        sheet_name="DETALLE_HISTORICO",
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
                60,
            )


manifiesto = {
    "fecha_ejecucion": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "5809 Matrícula",
    "anio_referencia": 2025,
    "universo": 27,
    "llave_principal": "CODCLI histórico",
    "segunda_variable": "carrera",
    "comparacion_adicional": "plan/familia CODCLI",
    "conversion_automatica": False,
    "niveles_modificados": 0,
    "fuentes_modificadas": False,
    "archivo_carga_generado": False,
    "salida": str(SALIDA),
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
print("=" * 108)
print("DIAGNÓSTICO DE LOS 27 PENDIENTES POR CODCLI, PLAN Y CARRERA")
print("=" * 108)

for _, fila in resumen_estados.iterrows():
    print(
        f"{fila['ESTADO']}: "
        f"{fila['CASOS']}"
    )

print()
print(
    "Candidatos fuertes para validar plan: "
    f"{len(candidatos_fuertes)}"
)
print(
    "Candidatos débiles sin conversión: "
    f"{len(candidatos_debiles)}"
)
print(
    "Sin modelo o ambiguos: "
    f"{len(sin_modelo)}"
)
print()
print(f"Excel: {excel}")
print(f"Carpeta: {SALIDA}")
print("Conversión automática: NO")
print("Niveles modificados: 0")
print("Fuentes modificadas: NO")
print("Archivo final de carga generado: NO")
print("=" * 108)

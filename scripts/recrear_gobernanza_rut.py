#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import os
import re
import json
import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular").resolve()

ARCHIVO_29 = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / "EXTRACCION_RUT_CODCLI_29_20260703_104251"
    / "02_RESULTADOS"
    / "REVISION_RUT_CODCLI_RECHAZADOS_Y_PENDIENTES.xlsx"
)

ARTEFACTOS = [
    ARCHIVO_29,
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/CLASIFICACION_29_MODELOS_PERIODIZACION_20260703_123007/02_RESULTADOS/CLASIFICACION_29_MODELOS_PERIODIZACION.xlsx",
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/ADECUACION_2_CASOS_PERIODIZACION_20260703_123204/02_RESULTADOS/ADECUACION_2_CASOS_PERIODIZACION.xlsx",
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/DIAGNOSTICO_27_CODCLI_PLAN_20260703_123419/02_RESULTADOS/DIAGNOSTICO_27_PENDIENTES_CODCLI_PLAN.xlsx",
    RAIZ / "avance_curricular_2026/04_gobernanza_mallas/03_auditorias/DESCOMPOSICION_19_CANDIDATOS_DEBILES_20260703_123657/02_RESULTADOS/DESCOMPOSICION_19_CANDIDATOS_DEBILES.xlsx",
]


def norm_rut(valor):
    return re.sub(r"[^0-9Kk]", "", str(valor or "")).upper()


def leer_hojas(path):
    if not path.exists():
        return []

    try:
        xl = pd.ExcelFile(path, engine="openpyxl")
    except Exception:
        return []

    hojas = []

    for hoja in xl.sheet_names:
        try:
            df = pd.read_excel(
                path,
                sheet_name=hoja,
                dtype=str,
                keep_default_na=False,
                engine="openpyxl",
            )
            df["__ARCHIVO__"] = path.name
            df["__RUTA__"] = str(path)
            df["__HOJA__"] = hoja
            hojas.append(df)
        except Exception:
            pass

    return hojas


rut_input = os.environ.get("RUT_OBJETIVO", "").strip()
rut_norm = norm_rut(rut_input)

if not rut_norm:
    raise SystemExit(
        'Debe definir RUT_OBJETIVO. Ejemplo: RUT_OBJETIVO="16555449-3" python3 scripts/recrear_gobernanza_rut.py'
    )

if not ARCHIVO_29.exists():
    raise SystemExit(f"No existe archivo base de los 29: {ARCHIVO_29}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026"
    / "04_gobernanza_mallas"
    / "03_auditorias"
    / f"EXPEDIENTE_GOBERNANZA_RUT_{rut_norm}_{timestamp}"
)

SALIDA.mkdir(parents=True, exist_ok=False)

resultados = []
fuentes_revisadas = []

for artefacto in ARTEFACTOS:
    fuentes_revisadas.append({
        "RUTA": str(artefacto),
        "EXISTE": artefacto.exists(),
    })

    for df in leer_hojas(artefacto):
        columnas_busqueda = [
            c for c in df.columns
            if "RUT" in c.upper() or "DOCUMENTO" in c.upper()
        ]

        if not columnas_busqueda:
            continue

        mask_total = pd.Series(False, index=df.index)
        columnas_match = []

        for col in columnas_busqueda:
            mask = df[col].map(norm_rut).eq(rut_norm)

            if mask.any():
                mask_total = mask_total | mask
                columnas_match.append(col)

        if mask_total.any():
            hallazgo = df.loc[mask_total].copy()
            hallazgo["__COLUMNAS_MATCH__"] = " | ".join(columnas_match)
            resultados.append(hallazgo)

if resultados:
    consolidado = pd.concat(
        resultados,
        ignore_index=True,
        sort=False,
    )
else:
    consolidado = pd.DataFrame()

estado = (
    "ENCONTRADO_EN_GOBERNANZA_29"
    if len(consolidado) > 0
    else "NO_ENCONTRADO_EN_GOBERNANZA_29"
)

columnas_preferidas = [
    c for c in [
        "__ARCHIVO__",
        "__HOJA__",
        "__COLUMNAS_MATCH__",
        "N_ORDEN_REVISION",
        "ID_FILA_5809",
        "RUT_5809_CONTROL",
        "RUT_EVIDENCIA_CRUCE",
        "RUT_5809_NORMALIZADO",
        "RUT_EVIDENCIA_NORMALIZADO",
        "RUT_5809_FORMATEADO",
        "CODCLI_PROMEDIOS_LISTA",
        "CODCLI_MODELO_ASOCIADO",
        "CODCARR_PLAN_VIGENTE",
        "CODCARPR_EVIDENCIA",
        "NIVEL_EVIDENCIA",
        "DECISION_RECOMENDADA",
        "ESTADO_CIERRE_RECOMENDADO",
        "CATEGORIA_REVISION",
        "ESTADO_ASOCIACION_MODELO",
        "ESTADO_ADECUACION",
        "ANIO_CURRICULAR_ADECUADO",
        "ESTADO_DIAGNOSTICO_27",
        "ESTADO_FINAL_19",
        "RESPALDO_REAL",
        "DECISION_ACTUAL",
        "FUNDAMENTO",
        "FUNDAMENTO_ADECUACION",
    ]
    if len(consolidado) > 0 and c in consolidado.columns
]

excel = SALIDA / f"EXPEDIENTE_GOBERNANZA_RUT_{rut_norm}.xlsx"
md = SALIDA / f"INFORME_GOBERNANZA_RUT_{rut_norm}.md"
manifest = SALIDA / "manifest_expediente.json"

with pd.ExcelWriter(excel, engine="openpyxl") as writer:
    pd.DataFrame([
        {
            "RUT_CONSULTADO": rut_input,
            "RUT_NORMALIZADO": rut_norm,
            "ESTADO": estado,
            "REGISTROS_ENCONTRADOS": len(consolidado),
            "FUENTE_BASE_29": str(ARCHIVO_29),
            "FUENTES_ORIGINALES_MODIFICADAS": "NO",
        }
    ]).to_excel(writer, sheet_name="RESUMEN", index=False)

    if len(consolidado) > 0:
        if columnas_preferidas:
            consolidado[columnas_preferidas].to_excel(
                writer,
                sheet_name="RESUMEN_GOBERNANZA",
                index=False,
            )

        consolidado.to_excel(
            writer,
            sheet_name="DETALLE_COMPLETO",
            index=False,
        )
    else:
        pd.DataFrame([
            {
                "OBSERVACION": (
                    "El RUT no fue encontrado en el archivo base de los "
                    "29 casos ni en los artefactos posteriores revisados."
                )
            }
        ]).to_excel(writer, sheet_name="SIN_HALLAZGO", index=False)

    pd.DataFrame(fuentes_revisadas).to_excel(
        writer,
        sheet_name="FUENTES_REVISADAS",
        index=False,
    )

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            letra = col[0].column_letter
            ancho = max(len(str(cell.value or "")) for cell in col[:2000])
            ws.column_dimensions[letra].width = min(max(ancho + 2, 12), 60)

lineas = []
lineas.append(f"# Expediente de gobernanza por RUT {rut_norm}")
lineas.append("")
lineas.append("## Contexto")
lineas.append("")
lineas.append("- Proceso: Avance Curricular SIES 2026")
lineas.append("- Subproyecto: Matrícula 5809")
lineas.append("- Año de referencia: 2025")
lineas.append("")
lineas.append("## Resultado")
lineas.append("")
lineas.append(f"- RUT consultado: `{rut_input}`")
lineas.append(f"- RUT normalizado: `{rut_norm}`")
lineas.append(f"- Estado: **{estado}**")
lineas.append(f"- Registros encontrados: **{len(consolidado)}**")
lineas.append("")
lineas.append("## Interpretación")
lineas.append("")

if len(consolidado) > 0:
    lineas.append(
        "El RUT aparece en el expediente gobernado de los 29 casos "
        "o en sus artefactos posteriores. Debe revisarse el Excel "
        "generado para confirmar si el caso quedó adecuado, pendiente "
        "o sin modelo demostrado."
    )
else:
    lineas.append(
        "El RUT no aparece en los artefactos gobernados de los 29 casos. "
        "Si proviene de otro archivo de excluidos, ese archivo debe "
        "compararse explícitamente."
    )

lineas.append("")
lineas.append("## Archivos generados")
lineas.append("")
lineas.append(f"- Excel: `{excel}`")
lineas.append(f"- Manifest: `{manifest}`")
lineas.append(f"- Carpeta: `{SALIDA}`")

md.write_text("\n".join(lineas) + "\n", encoding="utf-8")

manifest.write_text(
    json.dumps(
        {
            "fecha": datetime.now().isoformat(),
            "proceso": "Avance Curricular SIES 2026",
            "subproyecto": "Matrícula 5809",
            "rut_consultado": rut_input,
            "rut_normalizado": rut_norm,
            "estado": estado,
            "registros_encontrados": len(consolidado),
            "fuente_base_29": str(ARCHIVO_29),
            "artefactos_revisados": [str(p) for p in ARTEFACTOS],
            "excel": str(excel),
            "informe": str(md),
            "fuentes_originales_modificadas": False,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

print()
print("=" * 120)
print("RECREACIÓN DE GOBERNANZA POR RUT")
print("=" * 120)
print(f"RUT consultado: {rut_input}")
print(f"RUT normalizado: {rut_norm}")
print(f"Estado: {estado}")
print(f"Registros encontrados: {len(consolidado)}")
print()

if len(consolidado) > 0 and columnas_preferidas:
    print("Resumen de gobernanza:")
    print(consolidado[columnas_preferidas].to_string(index=False))
elif len(consolidado) == 0:
    print("El RUT no aparece en los artefactos gobernados de los 29 casos.")

print()
print("=" * 120)
print("EXPEDIENTE GENERADO")
print("=" * 120)
print(f"Excel: {excel}")
print(f"Informe: {md}")
print(f"Carpeta: {SALIDA}")
print("Fuentes originales modificadas: NO")
print("=" * 120)

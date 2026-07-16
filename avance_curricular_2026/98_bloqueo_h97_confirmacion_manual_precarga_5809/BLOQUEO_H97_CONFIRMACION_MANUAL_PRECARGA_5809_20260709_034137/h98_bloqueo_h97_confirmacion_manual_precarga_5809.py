from pathlib import Path
from datetime import datetime
import pandas as pd
import shutil
import hashlib
import json

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/98_bloqueo_h97_confirmacion_manual_precarga_5809"
    / f"BLOQUEO_H97_CONFIRMACION_MANUAL_PRECARGA_5809_{ts}"
)
SALIDA.mkdir(parents=True, exist_ok=True)

ORIGINAL_5809 = RAIZ / "avance_curricular_2026/00_fuentes_congeladas/CARGA_CONGELADA_20260626_005826/originales/5809_Precarga Matrícula Avance Curricular 2026.csv"

CSV_DESKTOP_H97 = DESKTOP / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_SUBIR_ID_16768.csv"

cols_oficiales_22 = [
    "CODIGO_IES_NUM",
    "TIPO_DOCUMENTO",
    "NUM_DOCUMENTO",
    "DV",
    "PRIMER_APELLIDO",
    "SEGUNDO_APELLIDO",
    "NOMBRES",
    "SEXO",
    "FECHA_NACIMIENTO",
    "CODIGO_UNICO",
    "PLAN_ESTUDIOS",
    "ANIO_INGRESO_CARRERA_ACTUAL",
    "SEM_INGRESO_CARRERA_ACTUAL",
    "ANIO_INGRESO_CARRERA_ORIGEN",
    "SEM_INGRESO_CARRERA_ORIGEN",
    "CURSO_1ER_SEM",
    "CURSO_2DO_SEM",
    "UNIDADES_CURSADAS",
    "UNIDADES_APROBADAS",
    "UNID_CURSADAS_TOTAL",
    "UNID_APROBADAS_TOTAL",
    "VIGENCIA",
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def ultimo(base, prefijo):
    dirs = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")
    return dirs[0]

def imprimir(titulo, df):
    print()
    print("=" * 160)
    print(titulo)
    print("=" * 160)
    if df.empty:
        print("(sin datos)")
    else:
        print(df.to_string(index=False))

print("[1/8] Localizando archivos H95/H96/H97 y precarga original...", flush=True)

if not ORIGINAL_5809.exists():
    raise SystemExit(f"BLOQUEO: no existe precarga original: {ORIGINAL_5809}")

H95 = ultimo(
    RAIZ / "avance_curricular_2026/95_validacion_final_sies_ready_5809",
    "VALIDACION_FINAL_SIES_READY_5809_",
)
csv_h95 = H95 / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY.csv"

H97_BASE = RAIZ / "avance_curricular_2026/97_sies_ready_21_campos_con_fecha_sin_vigencia_5809"
h97_dirs = sorted(
    [p for p in H97_BASE.glob("SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA_5809_*") if p.is_dir()],
    key=lambda p: p.stat().st_mtime,
    reverse=True,
) if H97_BASE.exists() else []

csv_h97 = ""
if h97_dirs:
    posible = h97_dirs[0] / "5809_MATRICULA_AVANCE_CURRICULAR_2026_SIES_READY_21_CAMPOS_CON_FECHA_SIN_VIGENCIA.csv"
    if posible.exists():
        csv_h97 = str(posible)

if not csv_h95.exists():
    raise SystemExit(f"BLOQUEO: no existe CSV H95: {csv_h95}")

print(f"Precarga original: {ORIGINAL_5809}")
print(f"H95 oficial 22 campos: {csv_h95}")
print(f"H97 descartado: {csv_h97 or 'NO_LOCALIZADO'}")

print("[2/8] Eliminando del Escritorio el CSV H97 para evitar carga errónea...", flush=True)

desktop_accion = "NO_EXISTIA"
desktop_respaldo = ""

if CSV_DESKTOP_H97.exists():
    respaldo = SALIDA / CSV_DESKTOP_H97.name
    shutil.copy2(CSV_DESKTOP_H97, respaldo)
    CSV_DESKTOP_H97.unlink()
    desktop_accion = "ELIMINADO_DEL_ESCRITORIO_Y_RESPALDADO_EN_H98"
    desktop_respaldo = str(respaldo)

print(f"Acción sobre CSV de escritorio H97: {desktop_accion}")

print("[3/8] Leyendo precarga original y H95...", flush=True)

df_orig = pd.read_csv(
    ORIGINAL_5809,
    sep=";",
    dtype=str,
    keep_default_na=False,
    encoding="latin1",
)

df_h95 = pd.read_csv(
    csv_h95,
    sep=";",
    header=None,
    names=cols_oficiales_22,
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig",
)

print(f"Precarga original shape: {df_orig.shape}")
print(f"H95 shape: {df_h95.shape}")

print("[4/8] Validando estructura oficial 22 campos...", flush=True)

validaciones = []

def add(nombre, resultado, observado, esperado, severidad="CRITICA"):
    validaciones.append({
        "VALIDACION": nombre,
        "RESULTADO": resultado,
        "OBSERVADO": observado,
        "ESPERADO": esperado,
        "SEVERIDAD": severidad,
    })

add("Precarga original existe", "OK" if ORIGINAL_5809.exists() else "ERROR", str(ORIGINAL_5809.exists()), "True")
add("H95 existe", "OK" if csv_h95.exists() else "ERROR", str(csv_h95.exists()), "True")
add("Filas precarga original", "OK" if len(df_orig) == 2371 else "ERROR", len(df_orig), 2371)
add("Columnas precarga original", "OK" if len(df_orig.columns) == 22 else "ERROR", len(df_orig.columns), 22)
add("Filas H95", "OK" if len(df_h95) == 2371 else "ERROR", len(df_h95), 2371)
add("Columnas H95", "OK" if len(df_h95.columns) == 22 else "ERROR", len(df_h95.columns), 22)
add("VIGENCIA existe en precarga original", "OK" if "VIGENCIA" in df_orig.columns else "ERROR", "VIGENCIA" in df_orig.columns, "True")
add("VIGENCIA existe en H95", "OK" if "VIGENCIA" in df_h95.columns else "ERROR", "VIGENCIA" in df_h95.columns, "True")
add("FECHA_NACIMIENTO existe en precarga original", "OK" if "FECHA_NACIMIENTO" in df_orig.columns else "ERROR", "FECHA_NACIMIENTO" in df_orig.columns, "True")
add("FECHA_NACIMIENTO existe en H95", "OK" if "FECHA_NACIMIENTO" in df_h95.columns else "ERROR", "FECHA_NACIMIENTO" in df_h95.columns, "True")

orden_orig_ok = list(df_orig.columns) == cols_oficiales_22
orden_h95_ok = list(df_h95.columns) == cols_oficiales_22

add("Orden columnas precarga original = estructura oficial 22", "OK" if orden_orig_ok else "ERROR", orden_orig_ok, "True")
add("Orden columnas H95 = estructura oficial 22", "OK" if orden_h95_ok else "ERROR", orden_h95_ok, "True")

# Recuento real de separadores por fila: 21 separadores = 22 campos.
def contar_campos_csv(path, encoding):
    conteos = {}
    max_muestras = []
    with open(path, "r", encoding=encoding, errors="replace", newline="") as f:
        for i, line in enumerate(f, start=1):
            line = line.rstrip("\n\r")
            n = line.count(";") + 1
            conteos[n] = conteos.get(n, 0) + 1
            if len(max_muestras) < 5:
                max_muestras.append({"LINEA": i, "CAMPOS": n, "TEXTO_INICIO": line[:160]})
    return conteos, pd.DataFrame(max_muestras)

conteos_orig, muestra_orig = contar_campos_csv(ORIGINAL_5809, "latin1")
conteos_h95, muestra_h95 = contar_campos_csv(csv_h95, "utf-8-sig")

# La precarga original tiene encabezado, por eso 2372 líneas con 22 campos.
add("Campos por línea precarga original", "OK" if list(conteos_orig.keys()) == [22] else "ERROR", str(conteos_orig), "{22: todas}")
add("Campos por línea H95", "OK" if list(conteos_h95.keys()) == [22] else "ERROR", str(conteos_h95), "{22: todas}")

# Inmutabilidad de campos precargados.
precarga_no_modificable = cols_oficiales_22[:15] + ["VIGENCIA"]
diferencias = []

for c in precarga_no_modificable:
    mask = df_orig[c].astype(str) != df_h95[c].astype(str)
    if mask.any():
        tmp = pd.DataFrame({
            "FILA": df_orig.index[mask] + 1,
            "COLUMNA": c,
            "VALOR_PRECARGA_ORIGINAL": df_orig.loc[mask, c].astype(str),
            "VALOR_H95": df_h95.loc[mask, c].astype(str),
        })
        diferencias.append(tmp)

df_diff = pd.concat(diferencias, ignore_index=True) if diferencias else pd.DataFrame(
    columns=["FILA", "COLUMNA", "VALOR_PRECARGA_ORIGINAL", "VALOR_H95"]
)

add(
    "Inmutabilidad campos precargados 1-15 y VIGENCIA",
    "OK" if len(df_diff) == 0 else "ERROR",
    len(df_diff),
    0,
)

validaciones_df = pd.DataFrame(validaciones)
errores = validaciones_df[validaciones_df["RESULTADO"].eq("ERROR")]

print("[5/8] Construyendo dictamen funcional...", flush=True)

estructura = pd.DataFrame({
    "N_ORDEN": range(1, 23),
    "COLUMNA_OFICIAL_22": cols_oficiales_22,
    "EN_PRECARGA_ORIGINAL": [c in df_orig.columns for c in cols_oficiales_22],
    "EN_H95": [c in df_h95.columns for c in cols_oficiales_22],
    "TRATAMIENTO": [
        "PRECARGA_NO_MODIFICABLE" if i <= 15 else
        "CAMPO_COMPLETADO_CALCULADO" if 16 <= i <= 21 else
        "PRECARGA_NO_MODIFICABLE"
        for i in range(1, 23)
    ],
})

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "5809 Matrícula Avance Curricular",
    "ID_CARGA": 16768,
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "FUENTE_SUPERIOR": "Instructivo_Avance Curricular SIES - 2026.txt",
    "FUENTE_TECNICA_CONTROL": str(ORIGINAL_5809),
    "H95": str(csv_h95),
    "H97": csv_h97 or "NO_LOCALIZADO",
    "DICTAMEN_H95": "MANTIENE_ESTRUCTURA_OFICIAL_22_CAMPOS_CON_VIGENCIA",
    "DICTAMEN_H97": "DESCARTADO_NO_SUBIR_EXCLUYE_VIGENCIA_OBLIGATORIA",
    "ACCION_ESCRITORIO_H97": desktop_accion,
    "ARCHIVO_ESCRITORIO_ACTUAL_PARA_SUBIR": "NINGUNO_HASTA_RESOLVER_INCONSISTENCIA_PLATAFORMA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CONCLUSION": "PREVALECE_MANUAL_PRECARGA_22_CAMPOS;_NO_CORRESPONDE_ELIMINAR_VIGENCIA",
}])

resumen = pd.DataFrame([
    {"INDICADOR": "Precarga original filas", "VALOR": len(df_orig)},
    {"INDICADOR": "Precarga original columnas", "VALOR": len(df_orig.columns)},
    {"INDICADOR": "H95 filas", "VALOR": len(df_h95)},
    {"INDICADOR": "H95 columnas", "VALOR": len(df_h95.columns)},
    {"INDICADOR": "VIGENCIA en precarga original", "VALOR": "SI" if "VIGENCIA" in df_orig.columns else "NO"},
    {"INDICADOR": "VIGENCIA en H95", "VALOR": "SI" if "VIGENCIA" in df_h95.columns else "NO"},
    {"INDICADOR": "Diferencias campos precargados 1-15 + VIGENCIA", "VALOR": len(df_diff)},
    {"INDICADOR": "Errores validación H98", "VALOR": len(errores)},
    {"INDICADOR": "CSV H97 eliminado del Escritorio", "VALOR": desktop_accion},
])

print("[6/8] Escribiendo auditoría H98...", flush=True)

excel_out = SALIDA / "AUDITORIA_H98_BLOQUEO_H97_CONFIRMACION_MANUAL_PRECARGA_5809.xlsx"
informe_out = SALIDA / "INFORME_H98_BLOQUEO_H97_CONFIRMACION_MANUAL_PRECARGA_5809.md"
manifest_out = SALIDA / "manifest_h98_bloqueo_h97_confirmacion_manual_precarga_5809.json"
script_out = SALIDA / "h98_bloqueo_h97_confirmacion_manual_precarga_5809.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN", index=False)
    resumen.to_excel(writer, sheet_name="01_RESUMEN", index=False)
    validaciones_df.to_excel(writer, sheet_name="02_VALIDACIONES", index=False)
    estructura.to_excel(writer, sheet_name="03_ESTRUCTURA_OFICIAL_22", index=False)
    df_diff.to_excel(writer, sheet_name="04_DIF_PRECARGA_H95", index=False)
    pd.DataFrame([{"CAMPOS": k, "LINEAS": v} for k, v in conteos_orig.items()]).to_excel(writer, sheet_name="05_CONTEO_CAMPOS_ORIG", index=False)
    pd.DataFrame([{"CAMPOS": k, "LINEAS": v} for k, v in conteos_h95.items()]).to_excel(writer, sheet_name="06_CONTEO_CAMPOS_H95", index=False)
    muestra_orig.to_excel(writer, sheet_name="07_MUESTRA_ORIG", index=False)
    muestra_h95.to_excel(writer, sheet_name="08_MUESTRA_H95", index=False)
    pd.DataFrame([
        {"ARCHIVO": "PRECARGA_ORIGINAL_5809", "RUTA": str(ORIGINAL_5809), "SHA256": sha256(ORIGINAL_5809)},
        {"ARCHIVO": "H95_22_CAMPOS_CON_VIGENCIA", "RUTA": str(csv_h95), "SHA256": sha256(csv_h95)},
        {"ARCHIVO": "H97_DESCARTADO", "RUTA": csv_h97, "SHA256": sha256(Path(csv_h97)) if csv_h97 else ""},
        {"ARCHIVO": "H97_DESKTOP_RESPALDADO_ANTES_DE_ELIMINAR", "RUTA": desktop_respaldo, "SHA256": sha256(Path(desktop_respaldo)) if desktop_respaldo else ""},
    ]).to_excel(writer, sheet_name="09_FUENTES_HASH", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 120)

informe_out.write_text(
f"""# H98 — Bloqueo H97 y confirmación de estructura oficial 5809

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

5809 Matrícula Avance Curricular, ID Carga 16768.

## Dictamen

Se descarta H97 como archivo de carga porque excluye `VIGENCIA`.

## Fundamento

La fuente superior del proceso es el instructivo oficial. La precarga original 5809 contiene 22 columnas, incluyendo `FECHA_NACIMIENTO` y `VIGENCIA`.

## Resultado técnico

- Precarga original filas: {len(df_orig)}
- Precarga original columnas: {len(df_orig.columns)}
- H95 filas: {len(df_h95)}
- H95 columnas: {len(df_h95.columns)}
- Diferencias en campos precargados 1-15 + VIGENCIA entre precarga y H95: {len(df_diff)}
- H97 en Escritorio: {desktop_accion}

## Conclusión

No corresponde eliminar `VIGENCIA` para adaptar la carga. Debe prevalecer la estructura oficial/precarga de 22 campos. La inconsistencia debe tratarse como problema de estructura activa de plataforma, plantilla o selección de carga, no como modificación del archivo oficial.

## Archivo recomendado para defensa técnica

`{csv_h95}`

## Archivo no recomendado

H97 queda descartado por exclusión de `VIGENCIA`.
""",
encoding="utf-8"
)

manifest_out.write_text(json.dumps({
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "H98 bloqueo H97 confirmación manual precarga 5809",
    "id_carga": 16768,
    "precarga_original": str(ORIGINAL_5809),
    "csv_h95": str(csv_h95),
    "csv_h97": csv_h97,
    "desktop_h97_accion": desktop_accion,
    "desktop_h97_respaldo": desktop_respaldo,
    "auditoria": str(excel_out),
    "informe": str(informe_out),
    "validaciones_error": len(errores),
    "conclusion": "PREVALECE_MANUAL_PRECARGA_22_CAMPOS_CON_VIGENCIA",
    "fuentes_originales_modificadas": False,
}, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h98_bloqueo_h97_confirmacion_manual_precarga_5809.py"), script_out)

print("[7/8] Dejando aviso NO_SUBIR en Escritorio...", flush=True)

aviso = DESKTOP / "NO_SUBIR_HASTA_RESOLVER_ESTRUCTURA_5809_ID_16768.txt"
aviso.write_text(
f"""NO SUBIR H97.

Proceso: Avance Curricular SIES 2026
Subproyecto: 5809 Matrícula Avance Curricular
ID Carga: 16768

Dictamen H98:
- H97 fue descartado porque excluye VIGENCIA.
- El instructivo/precarga gobierna 22 campos con FECHA_NACIMIENTO y VIGENCIA.
- No queda CSV de carga en el Escritorio hasta resolver la inconsistencia de plataforma.

Auditoría:
{excel_out}

Informe:
{informe_out}

Archivo H95 defendible por estructura oficial:
{csv_h95}
""",
encoding="utf-8"
)

print("[8/8] Resultado final H98", flush=True)

print()
print("=" * 160)
print("H98 — BLOQUEO H97 Y CONFIRMACIÓN MANUAL/PRECARGA COMPLETADO")
print("=" * 160)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 Matrícula Avance Curricular")
print("ID Carga: 16768")
print("Resultado: PREVALECE ESTRUCTURA OFICIAL 22 CAMPOS CON VIGENCIA")
print("H97: DESCARTADO / NO SUBIR")
print("CSV de carga en Escritorio: NINGUNO")
print(f"Aviso Escritorio: {aviso}")
print(f"Auditoría H98: {excel_out}")
print(f"Informe H98: {informe_out}")
print(f"Manifest H98: {manifest_out}")
print("=" * 160)

imprimir("DICTAMEN", dictamen)
imprimir("RESUMEN", resumen)
imprimir("VALIDACIONES", validaciones_df)

if len(errores) > 0:
    raise SystemExit("BLOQUEO: H98 detectó errores internos. Revisar auditoría.")

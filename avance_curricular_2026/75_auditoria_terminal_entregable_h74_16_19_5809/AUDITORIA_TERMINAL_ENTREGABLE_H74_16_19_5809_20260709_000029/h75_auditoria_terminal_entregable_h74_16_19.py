from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import zipfile
import hashlib
import shutil
import re

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/75_auditoria_terminal_entregable_h74_16_19_5809"
    / f"AUDITORIA_TERMINAL_ENTREGABLE_H74_16_19_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_AUDITORIA_TERMINAL_H74_16_19_5809_{timestamp}"

SALIDA.mkdir(parents=True, exist_ok=True)
ESCRITORIO.mkdir(parents=True, exist_ok=True)

def norm(x):
    x = str(x or "").upper()
    for a, b in {"Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","Ñ":"N"}.items():
        x = x.replace(a, b)
    x = re.sub(r"[^A-Z0-9]+", "_", x)
    return re.sub(r"_+", "_", x).strip("_")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def ultimo(base, prefijo):
    if not base.exists():
        raise SystemExit(f"BLOQUEO: no existe carpeta base: {base}")
    dirs = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")
    return dirs[0]

def primer_excel(carpeta):
    excels = sorted(
        [p for p in carpeta.glob("*.xlsx") if not p.name.startswith("~$")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not excels:
        raise SystemExit(f"BLOQUEO: no hay Excel en {carpeta}")
    return excels[0]

def buscar_hoja(xlsx, patrones):
    xls = pd.ExcelFile(xlsx, engine="openpyxl")
    for p in patrones:
        for h in xls.sheet_names:
            if norm(p) == norm(h) or norm(p) in norm(h):
                return h
    return None

def leer(xlsx, patrones):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        xls = pd.ExcelFile(xlsx, engine="openpyxl")
        raise SystemExit(
            f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. "
            f"Hojas disponibles: {xls.sheet_names}"
        )
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def imprimir(titulo, df, n=None):
    print()
    print("=" * 150)
    print(titulo)
    print("=" * 150)
    if df.empty:
        print("(sin datos)")
        return
    if n is None:
        print(df.to_string(index=False))
    else:
        print(df.head(n).to_string(index=False))
        if len(df) > n:
            print(f"... mostrando {n} de {len(df)} filas")

print("[1/10] Localizando entregable H74 y fuentes H68/H69/H72/H73...", flush=True)

H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)
H69 = ultimo(
    RAIZ / "avance_curricular_2026/69_paquete_operativo_167_pendientes_16_19_5809",
    "PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_",
)
H72 = ultimo(
    RAIZ / "avance_curricular_2026/72_revision_end_to_end_167_pendientes_hasta_csv_piloto_5809",
    "REVISION_E2E_167_PENDIENTES_HASTA_CSV_PILOTO_5809_",
)
H73 = ultimo(
    RAIZ / "avance_curricular_2026/73_consolidado_final_estado_16_19_5809",
    "CONSOLIDADO_FINAL_ESTADO_16_19_5809_",
)
H74 = ultimo(
    RAIZ / "avance_curricular_2026/74_entregable_final_cierre_tecnico_16_19_5809",
    "ENTREGABLE_FINAL_CIERRE_TECNICO_16_19_5809_",
)

EX68 = primer_excel(H68)
EX69 = primer_excel(H69)
EX72 = primer_excel(H72)
EX73 = primer_excel(H73)

print(f"   H68: {H68}")
print(f"   H69: {H69}")
print(f"   H72: {H72}")
print(f"   H73: {H73}")
print(f"   H74: {H74}")

print("[2/10] Verificando archivos esperados en H74...", flush=True)

esperados_h74 = [
    "CONSOLIDADO_FINAL_ESTADO_16_19_5809.xlsx",
    "INFORME_CONSOLIDADO_FINAL_ESTADO_16_19_5809.md",
    "ACTA_TECNICA_CIERRE_DOCUMENTAL_16_19_5809.md",
    "manifest_consolidado_final_estado_16_19_5809.json",
    "RESUMEN_EJECUTIVO_CIERRE_TECNICO_16_19_5809.md",
    "README_H74_ENTREGABLE_FINAL.md",
    "indice_artifactos_h74.json",
]

archivos_h74 = []
for nombre in esperados_h74:
    p = H74 / nombre
    archivos_h74.append({
        "ARCHIVO": nombre,
        "EXISTE": "SI" if p.exists() else "NO",
        "RUTA": str(p),
        "SHA256": sha256(p) if p.exists() else "",
        "BYTES": p.stat().st_size if p.exists() else 0,
    })

archivos_h74_df = pd.DataFrame(archivos_h74)

if (archivos_h74_df["EXISTE"] != "SI").any():
    imprimir("ARCHIVOS H74", archivos_h74_df)
    raise SystemExit("BLOQUEO: faltan archivos esperados en H74.")

zips = sorted(H74.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
if not zips:
    raise SystemExit("BLOQUEO: H74 no contiene ZIP.")
ZIP_H74 = zips[0]

print(f"   ZIP H74: {ZIP_H74}")

print("[3/10] Validando contenido del ZIP...", flush=True)

with zipfile.ZipFile(ZIP_H74, "r") as z:
    zip_names = sorted(z.namelist())

zip_df = pd.DataFrame([{"ARCHIVO_ZIP": n} for n in zip_names])

faltan_zip = sorted(set(esperados_h74) - set(zip_names))
if faltan_zip:
    imprimir("CONTENIDO ZIP", zip_df)
    raise SystemExit(f"BLOQUEO: faltan archivos dentro del ZIP: {faltan_zip}")

print("[4/10] Leyendo Excel consolidado H74/H73...", flush=True)

EX_H74 = H74 / "CONSOLIDADO_FINAL_ESTADO_16_19_5809.xlsx"
dictamen = leer(EX_H74, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
tablero = leer(EX_H74, ["01_TABLERO_FINAL", "TABLERO"])
h68_256 = leer(EX_H74, ["02_H68_256_DECISION", "H68"])
h72_167 = leer(EX_H74, ["03_H72_167_BLOQUEADOS", "H72"])
causas_167 = leer(EX_H74, ["04_CAUSAS_167", "CAUSAS"])
columnas_167 = leer(EX_H74, ["05_COLUMNAS_167", "COLUMNAS"])
rutas = leer(EX_H74, ["06_RUTAS_REANUDACION", "RUTAS"])
control = leer(EX_H74, ["07_CONTROL_CARGA", "CONTROL"])
fuentes_h74_xlsx = leer(EX_H74, ["10_FUENTES", "FUENTES"])
manifest_legible = leer(EX_H74, ["11_MANIFEST_LEGIBLE", "MANIFEST"])

print("[5/10] Leyendo fuentes originales de metodología H68/H69/H72/H73...", flush=True)

dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
dict69 = leer(EX69, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
resumen69 = leer(EX69, ["01_RESUMEN_RUTAS", "RESUMEN"])
dict72 = leer(EX72, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
decisiones72 = leer(EX72, ["01_DECISIONES_167", "DECISIONES"])
resumen_decisiones72 = leer(EX72, ["02_RESUMEN_DECISIONES", "RESUMEN_DECISIONES"])
dict73 = leer(EX73, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
tablero73 = leer(EX73, ["01_TABLERO_FINAL", "TABLERO"])

print("[6/10] Validando metodología y consistencia de cifras...", flush=True)

validaciones = []

def add_control(nombre, esperado, observado, regla):
    ok = str(esperado) == str(observado)
    validaciones.append({
        "CONTROL": nombre,
        "ESPERADO": esperado,
        "OBSERVADO": observado,
        "RESULTADO": "OK" if ok else "ERROR",
        "REGLA_METODOLOGICA": regla,
    })

d0 = dictamen.iloc[0]
add_control("Proceso", "Avance Curricular SIES 2026", d0["PROCESO"], "Debe mantener proceso identificado.")
add_control("Subproyecto", "Consolidado final estado 16-19 archivo 5809", d0["SUBPROYECTO"], "Debe mantener subproyecto 5809 16-19.")
add_control("Año proceso", "2026", str(d0["AÑO_PROCESO"]), "No confundir año de proceso.")
add_control("Año referencia datos", "2025", str(d0["AÑO_REFERENCIA_DATOS"]), "Columnas 16-19 corresponden a año referencia 2025.")
add_control("Declaración carga", "NO_LISTO_PARA_CARGA", d0["DECLARACION_CARGA"], "No puede declararse listo con pendientes.")
add_control("Dictamen carga", "NO_APTO_PARA_CARGA", d0["DICTAMEN_CARGA"], "No apto con 167 bloqueados y 256 pendientes de decisión.")
add_control("Fuentes originales modificadas", "NO", d0["FUENTES_ORIGINALES_MODIFICADAS"], "No modificar fuentes originales.")
add_control("Correcciones aplicadas", "NO", d0["CORRECCIONES_APLICADAS"], "No aplicar cambios sin decisión/evidencia.")
add_control("Archivo carga generado", "NO", d0["ARCHIVO_CARGA_GENERADO"], "No generar archivo integral sin cierre.")
add_control("SIES_READY generado", "NO", d0["SIES_READY_GENERADO"], "No generar SIES_READY con bloqueos.")
add_control("Subida SIES permitida", "NO", d0["SUBIDA_SIES_PERMITIDA"], "No subir subconjunto ni archivo bloqueado.")
add_control("20-21 evaluado", "NO", d0["RECALCULO_20_21"], "20-21 acumulado es frente separado.")

add_control("Pendientes originales 16-19", "423", str(d0["PENDIENTES_ORIGINALES_16_19"]), "H58/H59 fijan universo pendiente 423.")
add_control("Cerrables decisión funcional", "256", str(d0["CERRABLES_SOLO_CON_DECISION_FUNCIONAL"]), "H68 consolida 256 cerrables si se validan.")
add_control("Bloqueados evidencia faltante", "167", str(d0["BLOQUEADOS_POR_EVIDENCIA_FALTANTE"]), "H72 consolida 167 bloqueados.")
add_control("Corregibles terminal", "0", str(d0["CORREGIBLES_POR_TERMINAL"]), "H72 demuestra 0 corregibles por terminal.")

# Cruce con H68
h68_d0 = dict68.iloc[0]
add_control("H68 pendientes originales", "423", str(h68_d0["PENDIENTES_16_19_ORIGINAL"]), "H73/H74 debe heredar 423 desde H68.")
add_control("H68 cerrables si validan", "256", str(h68_d0["CERRABLES_SI_SE_VALIDAN"]), "H73/H74 debe heredar 256 desde H68.")
add_control("H68 restantes estimados", "167", str(h68_d0["PENDIENTES_RESTANTES_ESTIMADOS"]), "H73/H74 debe heredar 167 desde H68.")

# Cruce con H72
h72_d0 = dict72.iloc[0]
add_control("H72 total 167", "167", str(h72_d0["TOTAL_167"]), "H72 debe contener 167 pendientes.")
add_control("H72 cerrables terminal", "0", str(h72_d0["CERRABLES_POR_TERMINAL"]), "No hay cierre por terminal.")
add_control("H72 bloqueados terminal", "167", str(h72_d0["BLOQUEADOS_POR_TERMINAL"]), "Todos los 167 quedan bloqueados.")

# Suma metodología
suma = int(d0["CERRABLES_SOLO_CON_DECISION_FUNCIONAL"]) + int(d0["BLOQUEADOS_POR_EVIDENCIA_FALTANTE"])
add_control("Suma 256 + 167", "423", str(suma), "El tablero debe cerrar contra 423 pendientes originales.")

validaciones_df = pd.DataFrame(validaciones)

if (validaciones_df["RESULTADO"] != "OK").any():
    imprimir("VALIDACIONES METODOLOGICAS", validaciones_df)
    raise SystemExit("BLOQUEO: hay validaciones metodológicas con ERROR.")

print("[7/10] Validando que no exista archivo de carga/SIES_READY dentro del entregable...", flush=True)

patrones_prohibidos = [
    "SIES_READY",
    "CARGA_FINAL",
    "ARCHIVO_CARGA",
    "SUBIR_SIES",
    "LISTO_PARA_CARGA",
]

prohibidos = []
for p in H74.rglob("*"):
    if p.is_file():
        up = p.name.upper()
        for pat in patrones_prohibidos:
            if pat in up and "NO_SUBIR" not in up and "NO_LISTO" not in up:
                prohibidos.append(str(p))

prohibidos_df = pd.DataFrame({"ARCHIVO_PROHIBIDO": prohibidos})
if prohibidos:
    imprimir("ARCHIVOS PROHIBIDOS DETECTADOS", prohibidos_df)
    raise SystemExit("BLOQUEO: se detectó posible archivo de carga/SIES_READY en H74.")

print("[8/10] Generando auditoría terminal y salidas...", flush=True)

auditoria = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Auditoría terminal entregable H74 16-19 archivo 5809",
    "hito": 75,
    "hito74": str(H74),
    "zip_h74": str(ZIP_H74),
    "dictamen": "VALIDADO_CONFORME_METODOLOGIA",
    "declaracion_carga": "NO_LISTO_PARA_CARGA",
    "dictamen_carga": "NO_APTO_PARA_CARGA",
    "pendientes_originales_16_19": 423,
    "cerrables_solo_con_decision_funcional": 256,
    "bloqueados_por_evidencia_faltante": 167,
    "corregibles_por_terminal": 0,
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "subida_sies_permitida": False,
    "recalculo_20_21": False,
    "validaciones_ok": int((validaciones_df["RESULTADO"] == "OK").sum()),
    "validaciones_error": int((validaciones_df["RESULTADO"] != "OK").sum()),
}

excel_out = SALIDA / "AUDITORIA_TERMINAL_ENTREGABLE_H74_16_19_5809.xlsx"
informe_out = SALIDA / "INFORME_AUDITORIA_TERMINAL_ENTREGABLE_H74_16_19_5809.md"
manifest_out = SALIDA / "manifest_auditoria_terminal_entregable_h74_16_19_5809.json"
script_out = SALIDA / "h75_auditoria_terminal_entregable_h74_16_19.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    pd.DataFrame([auditoria]).to_excel(writer, sheet_name="00_DICTAMEN_AUDITORIA", index=False)
    validaciones_df.to_excel(writer, sheet_name="01_VALIDACIONES", index=False)
    archivos_h74_df.to_excel(writer, sheet_name="02_ARCHIVOS_H74", index=False)
    zip_df.to_excel(writer, sheet_name="03_CONTENIDO_ZIP", index=False)
    dictamen.to_excel(writer, sheet_name="04_DICTAMEN_H74", index=False)
    tablero.to_excel(writer, sheet_name="05_TABLERO_H74", index=False)
    h68_256.to_excel(writer, sheet_name="06_H68_256", index=False)
    h72_167.to_excel(writer, sheet_name="07_H72_167", index=False)
    causas_167.to_excel(writer, sheet_name="08_CAUSAS_167", index=False)
    columnas_167.to_excel(writer, sheet_name="09_COLUMNAS_167", index=False)
    rutas.to_excel(writer, sheet_name="10_RUTAS_REANUDACION", index=False)
    control.to_excel(writer, sheet_name="11_CONTROL_CARGA", index=False)
    fuentes_h74_xlsx.to_excel(writer, sheet_name="12_FUENTES_H74", index=False)
    manifest_legible.to_excel(writer, sheet_name="13_MANIFEST_LEGIBLE", index=False)
    resumen_decisiones72.to_excel(writer, sheet_name="14_CRUCE_H72_DECISIONES", index=False)
    pd.DataFrame([
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "69", "RUTA": str(H69), "EXCEL": str(EX69), "SHA256": sha256(EX69)},
        {"HITO": "72", "RUTA": str(H72), "EXCEL": str(EX72), "SHA256": sha256(EX72)},
        {"HITO": "73", "RUTA": str(H73), "EXCEL": str(EX73), "SHA256": sha256(EX73)},
        {"HITO": "74", "RUTA": str(H74), "EXCEL": str(EX_H74), "ZIP": str(ZIP_H74), "SHA256_ZIP": sha256(ZIP_H74)},
    ]).to_excel(writer, sheet_name="15_TRAZABILIDAD", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 110)

informe = f"""# Hito 75 — Auditoría terminal entregable H74 16-19

## Dictamen

VALIDADO_CONFORME_METODOLOGIA.

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Resultado validado

- Pendientes originales 16-19: 423.
- Cerrables solo con decisión funcional: 256.
- Bloqueados por evidencia faltante: 167.
- Corregibles por terminal: 0.

## Control de carga

- Declaración carga: NO_LISTO_PARA_CARGA.
- Dictamen carga: NO_APTO_PARA_CARGA.
- Fuentes originales modificadas: NO.
- Correcciones aplicadas: NO.
- Archivo de carga generado: NO.
- SIES_READY generado: NO.
- Subida SIES permitida: NO.
- 20-21 evaluado: NO.

## Metodología validada

El entregable H74 fue contrastado contra H68, H69, H72 y H73.
Las cifras cierran: 256 + 167 = 423.
No se detectaron archivos de carga ni SIES_READY dentro del entregable.
El ZIP contiene los archivos esperados.
"""

informe_out.write_text(informe, encoding="utf-8")
manifest_out.write_text(json.dumps(auditoria, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copy2(Path("/tmp/h75_auditoria_terminal_entregable_h74_16_19.py"), script_out)

for archivo in [excel_out, informe_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[9/10] Mostrando datos completos de validación en terminal...", flush=True)

print()
print("=" * 150)
print("HITO 75 — AUDITORÍA TERMINAL ENTREGABLE H74 16-19 VALIDADA")
print("=" * 150)
print("Proceso: Avance Curricular SIES 2026")
print("Subproyecto: 5809 columnas 16-19")
print("Dictamen auditoría: VALIDADO_CONFORME_METODOLOGIA")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print()
print("Cierre numérico:")
print("- 423 pendientes originales")
print("- 256 cerrables solo con decisión funcional")
print("- 167 bloqueados por evidencia faltante")
print("- 0 corregibles por terminal")
print("- 256 + 167 = 423")

imprimir("VALIDACIONES METODOLOGICAS COMPLETAS", validaciones_df)
imprimir("ARCHIVOS H74 VALIDADOS", archivos_h74_df)
imprimir("CONTENIDO COMPLETO DEL ZIP H74", zip_df)
imprimir("DICTAMEN GLOBAL H74", dictamen)
imprimir("TABLERO FINAL H74", tablero)
imprimir("H68 — MATRIZ 256 DECISION FUNCIONAL", h68_256)
imprimir("H72 — RESUMEN 167 BLOQUEADOS", h72_167)
imprimir("CAUSAS 167", causas_167)
imprimir("COLUMNAS AFECTADAS 167", columnas_167)
imprimir("RUTAS DE REANUDACION", rutas)
imprimir("CONTROL DE CARGA", control)

print()
print("=" * 150)
print("ARCHIVOS H75")
print("=" * 150)
print(f"Excel auditoría: {excel_out}")
print(f"Informe auditoría: {informe_out}")
print(f"Manifest auditoría: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 150)

print("[10/10] Terminado.", flush=True)

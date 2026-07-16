from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import shutil
import re
import hashlib

RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path.home() / "Desktop"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

SALIDA = (
    RAIZ
    / "avance_curricular_2026/73_consolidado_final_estado_16_19_5809"
    / f"CONSOLIDADO_FINAL_ESTADO_16_19_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_CONSOLIDADO_FINAL_ESTADO_16_19_5809_{timestamp}"

for carpeta in [SALIDA, ESCRITORIO]:
    carpeta.mkdir(parents=True, exist_ok=True)

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

    carpetas = sorted(
        [p for p in base.glob(prefijo + "*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not carpetas:
        raise SystemExit(f"BLOQUEO: no se encontró {prefijo} en {base}")

    return carpetas[0]

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
            f"Hojas: {xls.sheet_names}"
        )
    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(xlsx, sheet_name=h, dtype=str, keep_default_na=False, engine="openpyxl")

def imprimir(titulo, df, n=50):
    print()
    print("=" * 130)
    print(titulo)
    print("=" * 130)
    if df.empty:
        print("(sin datos)")
        return
    print(df.head(n).to_string(index=False))
    if len(df) > n:
        print(f"... mostrando {n} de {len(df)} filas")

print("[1/9] Localizando hitos 68, 69, 72...", flush=True)

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

EX68 = primer_excel(H68)
EX69 = primer_excel(H69)
EX72 = primer_excel(H72)

print(f"   H68: {EX68}", flush=True)
print(f"   H69: {EX69}", flush=True)
print(f"   H72: {EX72}", flush=True)

print("[2/9] Leyendo insumos...", flush=True)

dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ"])
dict69 = leer(EX69, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
resumen69 = leer(EX69, ["01_RESUMEN_RUTAS", "RESUMEN"])
dict72 = leer(EX72, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
decisiones72 = leer(EX72, ["01_DECISIONES_167", "DECISIONES"])
resumen_decisiones72 = leer(EX72, ["02_RESUMEN_DECISIONES", "RESUMEN_DECISIONES"])
resumen_causas72 = leer(EX72, ["03_RESUMEN_CAUSAS", "RESUMEN_CAUSAS"])
resumen_columnas72 = leer(EX72, ["04_RESUMEN_COLUMNAS", "RESUMEN_COLUMNAS"])
checklist72 = leer(EX72, ["08_CHECKLIST_SIES", "CHECKLIST"])
pasos72 = leer(EX72, ["09_20_PASOS", "20_PASOS"])

print("[3/9] Validando números esperados...", flush=True)

pendientes_originales = int(float(str(dict68.loc[0, "PENDIENTES_16_19_ORIGINAL"]).replace(",", ".")))
cerrables_h68 = int(float(str(dict68.loc[0, "CERRABLES_SI_SE_VALIDAN"]).replace(",", ".")))
pendientes_restantes_h68 = int(float(str(dict68.loc[0, "PENDIENTES_RESTANTES_ESTIMADOS"]).replace(",", ".")))

total_167_h72 = int(float(str(dict72.loc[0, "TOTAL_167"]).replace(",", ".")))
cerrables_terminal_h72 = int(float(str(dict72.loc[0, "CERRABLES_POR_TERMINAL"]).replace(",", ".")))
bloqueados_terminal_h72 = int(float(str(dict72.loc[0, "BLOQUEADOS_POR_TERMINAL"]).replace(",", ".")))

controles = {
    "pendientes_originales": pendientes_originales,
    "cerrables_h68": cerrables_h68,
    "pendientes_restantes_h68": pendientes_restantes_h68,
    "total_167_h72": total_167_h72,
    "cerrables_terminal_h72": cerrables_terminal_h72,
    "bloqueados_terminal_h72": bloqueados_terminal_h72,
}

esperado = {
    "pendientes_originales": 423,
    "cerrables_h68": 256,
    "pendientes_restantes_h68": 167,
    "total_167_h72": 167,
    "cerrables_terminal_h72": 0,
    "bloqueados_terminal_h72": 167,
}

for k, v in esperado.items():
    if controles[k] != v:
        raise SystemExit(f"BLOQUEO: control {k} esperado {v}, detectado {controles[k]}")

print("[4/9] Construyendo tablero final...", flush=True)

tablero = pd.DataFrame([
    {
        "BLOQUE": "TOTAL_PENDIENTES_ORIGINALES_16_19",
        "CASOS": 423,
        "ESTADO": "PUNTO_DE_PARTIDA",
        "TRATAMIENTO": "Universo de diferencias/pending 16-19 desde H58/H59.",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
    },
    {
        "BLOQUE": "CERRABLES_SOLO_CON_DECISION_FUNCIONAL_H68",
        "CASOS": 256,
        "ESTADO": "PENDIENTE_VALIDACION_FUNCIONAL",
        "TRATAMIENTO": "218 columna 19 SOLO A + 21 sin registros académicos 2025 + 17 PERIODO_NO_1_2 manteniendo 5809 sin cambio.",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
    },
    {
        "BLOQUE": "BLOQUEADOS_POR_EVIDENCIA_FALTANTE_H72",
        "CASOS": 167,
        "ESTADO": "BLOQUEADO",
        "TRATAMIENTO": "102 mapeo institucional + 57 fuente académica complementaria + 8 revisión funcional puntual.",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
    },
    {
        "BLOQUE": "CORREGIBLES_POR_TERMINAL",
        "CASOS": 0,
        "ESTADO": "SIN_CASOS",
        "TRATAMIENTO": "No hay casos con evidencia suficiente para corrección por terminal.",
        "PUEDE_CORREGIRSE_POR_TERMINAL": "NO",
        "PUEDE_IR_A_CARGA": "NO",
    },
])

rutas_reanudacion = pd.DataFrame([
    {
        "ORDEN": 1,
        "RUTA": "VALIDACION_FUNCIONAL_H68_256",
        "CASOS": 256,
        "REQUISITO": "Decisión funcional explícita para cerrar sin cambio los bloques 218, 21 y 17.",
        "ACCION_SIGUIENTE": "Registrar decisión y crear hito de cierre funcional de 256.",
        "ESTADO": "PENDIENTE",
    },
    {
        "ORDEN": 2,
        "RUTA": "MAPEO_INSTITUCIONAL",
        "CASOS": 102,
        "REQUISITO": "Resolver CODCLI_LISTA, identidad académica, documentos no calzantes y conflictos de mapeo.",
        "ACCION_SIGUIENTE": "Incorporar matriz de mapeo validada.",
        "ESTADO": "BLOQUEADO",
    },
    {
        "ORDEN": 3,
        "RUTA": "FUENTE_ACADEMICA_COMPLEMENTARIA",
        "CASOS": 57,
        "REQUISITO": "Incorporar evidencia académica 2025 para casos sin respaldo suficiente en PROMEDIOS.",
        "ACCION_SIGUIENTE": "Cargar fuente complementaria como evidencia, no como regla.",
        "ESTADO": "BLOQUEADO",
    },
    {
        "ORDEN": 4,
        "RUTA": "REVISION_FUNCIONAL_PUNTUAL",
        "CASOS": 8,
        "REQUISITO": "Resolver 6 datos 5809 no calzantes y 2 estados NULL/blanco.",
        "ACCION_SIGUIENTE": "Registrar decisión caso a caso.",
        "ESTADO": "BLOQUEADO",
    },
    {
        "ORDEN": 5,
        "RUTA": "20_21_ACUMULADO",
        "CASOS": "NO_EVALUADO",
        "REQUISITO": "Abrir proceso separado de acumulados 20-21.",
        "ACCION_SIGUIENTE": "No mezclar con cierre 16-19.",
        "ESTADO": "FUERA_DE_ALCANCE",
    },
])

estado_carga = pd.DataFrame([
    {"CONTROL": "Pendientes 16-19 completamente resueltos", "RESULTADO": "NO", "DICTAMEN": "256 requieren decisión funcional; 167 requieren evidencia/validación."},
    {"CONTROL": "Correcciones aplicadas", "RESULTADO": "NO", "DICTAMEN": "No se ha autorizado ni materializado corrección."},
    {"CONTROL": "Archivo integral de carga generado", "RESULTADO": "NO", "DICTAMEN": "No existe candidato integral."},
    {"CONTROL": "SIES_READY generado", "RESULTADO": "NO", "DICTAMEN": "No permitido."},
    {"CONTROL": "Subida SIES permitida", "RESULTADO": "NO", "DICTAMEN": "No permitido."},
    {"CONTROL": "20-21 evaluado", "RESULTADO": "NO", "DICTAMEN": "Separado / fuera de alcance."},
    {"CONTROL": "Estado final 16-19", "RESULTADO": "NO_APTO_PARA_CARGA", "DICTAMEN": "Cierre técnico documental, no carga."},
])

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Consolidado final estado 16-19 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "CIERRE_TECNICO_DOCUMENTAL_16_19",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "DICTAMEN_CARGA": "NO_APTO_PARA_CARGA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "SUBIDA_SIES_PERMITIDA": "NO",
    "RECALCULO_20_21": "NO",
    "PENDIENTES_ORIGINALES_16_19": 423,
    "CERRABLES_SOLO_CON_DECISION_FUNCIONAL": 256,
    "BLOQUEADOS_POR_EVIDENCIA_FALTANTE": 167,
    "CORREGIBLES_POR_TERMINAL": 0,
    "DICTAMEN_GLOBAL": "Cierre técnico documental: no hay condiciones para corrección, archivo final, SIES_READY ni carga. Reanudar por validación funcional H68 y rutas H72.",
}])

print("[5/9] Preparando informe y acta de cierre...", flush=True)

acta_cierre = f"""# Acta técnica de cierre documental 16-19 — Avance Curricular 5809

## Estado

Proceso: Avance Curricular SIES 2026
Archivo: 5809 Matrícula Avance Curricular
Columnas: 16-19
Año referencia datos: 2025

## Dictamen

NO_APTO_PARA_CARGA / NO_LISTO_PARA_CARGA.

## Resultado consolidado

- Pendientes originales 16-19: 423.
- Cerrables solo con decisión funcional: 256.
- Bloqueados por evidencia faltante: 167.
- Corregibles por terminal: 0.

## Desglose

### 256 cerrables solo con decisión funcional

Estos casos no deben corregirse por terminal. Requieren validación explícita para cerrar sin cambio:

- 218 columna 19 SOLO A.
- 21 sin registros académicos 2025.
- 17 PERIODO_NO_1_2 manteniendo 5809 sin cambio.

### 167 bloqueados por evidencia faltante

- 102 MAPEO_INSTITUCIONAL.
- 57 FUENTE_ACADEMICA_COMPLEMENTARIA.
- 8 REVISION_FUNCIONAL_PUNTUAL.

## Control de carga

No se generó archivo de carga.
No se generó SIES_READY.
No se permite subida a SIES.
20-21 no fue evaluado y debe mantenerse separado.

## Reanudación

1. Registrar decisión funcional H68 para 256 casos.
2. Resolver mapeo institucional para 102 casos.
3. Incorporar fuente académica complementaria para 57 casos.
4. Resolver revisión funcional puntual para 8 casos.
5. Solo después evaluar candidato técnico 16-19.
"""

informe = f"""# Hito 73 — Consolidado final estado 16-19

## Estado

- Proceso: Avance Curricular SIES 2026.
- Subproyecto: archivo 5809, columnas 16-19.
- Estado: cierre técnico documental.
- Declaración carga: NO_LISTO_PARA_CARGA.
- Dictamen carga: NO_APTO_PARA_CARGA.

## Resultado

| Bloque | Casos | Estado |
|---|---:|---|
| Pendientes originales 16-19 | 423 | Punto de partida |
| Cerrables solo con decisión funcional | 256 | Pendiente validación funcional |
| Bloqueados por evidencia faltante | 167 | Bloqueado |
| Corregibles por terminal | 0 | Sin casos |

## Conclusión

No hay condiciones para generar archivo final, SIES_READY ni carga.
El cierre de 16-19 debe reanudarse por rutas documentadas.
"""

print("[6/9] Escribiendo productos...", flush=True)

excel_out = SALIDA / "CONSOLIDADO_FINAL_ESTADO_16_19_5809.xlsx"
informe_out = SALIDA / "INFORME_CONSOLIDADO_FINAL_ESTADO_16_19_5809.md"
acta_out = SALIDA / "ACTA_TECNICA_CIERRE_DOCUMENTAL_16_19_5809.md"
manifest_out = SALIDA / "manifest_consolidado_final_estado_16_19_5809.json"
script_out = SALIDA / "h73_consolidado_final_estado_16_19_5809.py"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    tablero.to_excel(writer, sheet_name="01_TABLERO_FINAL", index=False)
    matriz68.to_excel(writer, sheet_name="02_H68_256_DECISION", index=False)
    resumen_decisiones72.to_excel(writer, sheet_name="03_H72_167_BLOQUEADOS", index=False)
    resumen_causas72.to_excel(writer, sheet_name="04_CAUSAS_167", index=False)
    resumen_columnas72.to_excel(writer, sheet_name="05_COLUMNAS_167", index=False)
    rutas_reanudacion.to_excel(writer, sheet_name="06_RUTAS_REANUDACION", index=False)
    estado_carga.to_excel(writer, sheet_name="07_CONTROL_CARGA", index=False)
    checklist72.to_excel(writer, sheet_name="08_CHECKLIST_H72", index=False)
    pasos72.to_excel(writer, sheet_name="09_20_PASOS_H72", index=False)
    pd.DataFrame([
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "69", "RUTA": str(H69), "EXCEL": str(EX69), "SHA256": sha256(EX69)},
        {"HITO": "72", "RUTA": str(H72), "EXCEL": str(EX72), "SHA256": sha256(EX72)},
        {"HITO": "73", "RUTA": str(SALIDA), "EXCEL": str(excel_out), "SHA256": ""},
    ]).to_excel(writer, sheet_name="10_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "dictamen_carga": "NO_APTO_PARA_CARGA",
        "fuentes_modificadas": "NO",
        "correcciones": "NO",
        "archivo_carga": "NO",
        "sies_ready": "NO",
        "subida_sies": "NO",
        "recalculo_20_21": "NO",
        "pendientes_originales": 423,
        "cerrables_decision_funcional": 256,
        "bloqueados_evidencia": 167,
        "corregibles_terminal": 0,
    }]).to_excel(writer, sheet_name="11_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 100)

informe_out.write_text(informe, encoding="utf-8")
acta_out.write_text(acta_cierre, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Consolidado final estado 16-19 archivo 5809",
    "hito": 73,
    "hito68": str(H68),
    "hito69": str(H69),
    "hito72": str(H72),
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
    "declaracion_carga": "NO_LISTO_PARA_CARGA",
    "dictamen_carga": "NO_APTO_PARA_CARGA",
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "acta": str(acta_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

shutil.copy2(Path("/tmp/h73_consolidado_final_estado_16_19_5809.py"), script_out)

for archivo in [excel_out, informe_out, acta_out, manifest_out, script_out]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[7/9] Verificando productos y controles...", flush=True)

assert excel_out.exists()
assert informe_out.exists()
assert acta_out.exists()
assert manifest_out.exists()
assert script_out.exists()
assert pendientes_originales == 423
assert cerrables_h68 == 256
assert total_167_h72 == 167
assert cerrables_terminal_h72 == 0
assert bloqueados_terminal_h72 == 167

print("[8/9] Preparando salida terminal...", flush=True)

print()
print("=" * 130)
print("HITO 73 — CONSOLIDADO FINAL ESTADO 16-19 GENERADO")
print("=" * 130)
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("Subida SIES permitida: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")
print("Dictamen carga: NO_APTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("TABLERO FINAL", tablero)
imprimir("RUTAS DE REANUDACIÓN", rutas_reanudacion)
imprimir("CONTROL DE CARGA", estado_carga)

print()
print("=" * 130)
print("ARCHIVOS")
print("=" * 130)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Acta técnica: {acta_out}")
print(f"Manifest: {manifest_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 130)

print("[9/9] Terminado.", flush=True)

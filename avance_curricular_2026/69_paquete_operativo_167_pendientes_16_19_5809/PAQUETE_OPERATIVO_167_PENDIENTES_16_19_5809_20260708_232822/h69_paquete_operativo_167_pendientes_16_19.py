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
    / "avance_curricular_2026/69_paquete_operativo_167_pendientes_16_19_5809"
    / f"PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_{timestamp}"
)

ESCRITORIO = DESKTOP / f"AVANCE_CURRICULAR_2026_PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809_{timestamp}"

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
            if norm(p) == norm(h):
                return h
    for p in patrones:
        for h in xls.sheet_names:
            if norm(p) in norm(h):
                return h
    return None

def leer(xlsx, patrones, obligatorio=True):
    h = buscar_hoja(xlsx, patrones)
    if h is None:
        if obligatorio:
            xls = pd.ExcelFile(xlsx, engine="openpyxl")
            raise SystemExit(
                f"BLOQUEO: no se encontró hoja {patrones} en {xlsx}. "
                f"Hojas: {xls.sheet_names}"
            )
        return pd.DataFrame()

    print(f"   Leyendo {xlsx.name} :: {h}", flush=True)
    return pd.read_excel(
        xlsx,
        sheet_name=h,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

def col(df, patrones):
    if df.empty:
        return None
    mapa = {norm(c): c for c in df.columns}
    for p in patrones:
        if norm(p) in mapa:
            return mapa[norm(p)]
    for c in df.columns:
        nc = norm(c)
        for p in patrones:
            if norm(p) in nc:
                return c
    return None

def imprimir(titulo, df, n=30):
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

print("[1/9] Localizando hitos 58, 59 y 68...", flush=True)

H58 = ultimo(
    RAIZ / "avance_curricular_2026/58_consolidado_resolucion_16_19_gobernado_5809",
    "CONSOLIDADO_RESOLUCION_16_19_GOBERNADO_",
)

H59 = ultimo(
    RAIZ / "avance_curricular_2026/59_paquete_validacion_humana_16_19_5809",
    "PAQUETE_VALIDACION_HUMANA_16_19_",
)

H68 = ultimo(
    RAIZ / "avance_curricular_2026/68_paquete_decision_funcional_16_19_5809",
    "PAQUETE_DECISION_FUNCIONAL_16_19_5809_",
)

EX58 = primer_excel(H58)
EX59 = primer_excel(H59)
EX68 = primer_excel(H68)

for p in [EX58, EX59, EX68]:
    if not p.exists():
        raise SystemExit(f"BLOQUEO: no existe fuente requerida: {p}")

print(f"   H58: {EX58}", flush=True)
print(f"   H59: {EX59}", flush=True)
print(f"   H68: {EX68}", flush=True)

print("[2/9] Leyendo base consolidada y paquete H68...", flush=True)

base423 = leer(EX58, ["03_CONSOLIDADO_423", "CONSOLIDADO_423", "DETALLE_423", "CONSOLIDADO"])
dict68 = leer(EX68, ["00_DICTAMEN_GLOBAL", "DICTAMEN"])
matriz68 = leer(EX68, ["01_MATRIZ_DECISION", "MATRIZ_DECISION"])

# Preferir hojas específicas del H59 si existen; si no, usar H58 consolidado.
mapeo59 = leer(EX59, ["04_MAPEO_INSTITUCIONAL_102", "MAPEO_INSTITUCIONAL"], obligatorio=False)
fuente59 = leer(EX59, ["05_FUENTE_COMPLEMENTARIA_57", "FUENTE_ACADEMICA", "FUENTE_COMPLEMENTARIA"], obligatorio=False)
revision59 = leer(EX59, ["06_REVISION_FUNCIONAL_8", "REVISION_FUNCIONAL"], obligatorio=False)

print("[3/9] Detectando columnas de clasificación...", flush=True)

c_ruta = col(base423, ["RUTA_RESOLUCION", "RUTA", "RUTA_OPERATIVA", "TIPO_RUTA"])
c_causa = col(base423, ["CAUSA_AUDITADA", "CAUSA_PRINCIPAL", "CAUSA"])
c_fila = col(base423, ["FILA_5809", "FILA"])
c_doc = col(base423, ["NUM_DOCUMENTO", "DOCUMENTO"])
c_codigo = col(base423, ["CODIGO_UNICO"])
c_plan = col(base423, ["PLAN_ESTUDIOS"])
c_codcli = col(base423, ["CODCLI_LISTA", "CODCLI_LISTA_NORM"])
c_colaf = col(base423, ["COLUMNA_AFECTADA_16_19", "COLUMNA_AFECTADA", "COLUMNAS_AFECTADAS"])
c_val5809 = col(base423, ["VALOR_ACTUAL_5809", "VALOR_5809"])
c_valrec = col(base423, ["VALOR_RECALCULADO_OBSERVADO", "VALOR_RECALCULADO"])
c_accion = col(base423, ["ACCION_SUGERIDA", "ACCION"])
c_pregunta = col(base423, ["PREGUNTA_CONCRETA_AREA_RESPONSABLE", "PREGUNTA_CONCRETA", "PREGUNTA"])

if not c_ruta:
    raise SystemExit(
        "BLOQUEO: no se detectó columna de ruta en H58. "
        "Se requiere RUTA_RESOLUCION/RUTA/RUTA_OPERATIVA para separar los 167."
    )

base423 = base423.copy()
base423["RUTA_KEY"] = base423[c_ruta].astype(str).str.strip().str.upper()

# Excluir rutas de decisión funcional ya empaquetadas en H68.
rutas_167 = {
    "MAPEO_INSTITUCIONAL": "MAPEO_INSTITUCIONAL",
    "FUENTE_ACADEMICA_COMPLEMENTARIA": "FUENTE_ACADEMICA_COMPLEMENTARIA",
    "REVISION_FUNCIONAL": "REVISION_FUNCIONAL_PUNTUAL",
    "REVISION_FUNCIONAL_PUNTUAL": "REVISION_FUNCIONAL_PUNTUAL",
}

base423["RUTA_H69"] = base423["RUTA_KEY"].map(rutas_167).fillna("FUERA_H69")

pendientes167 = base423[base423["RUTA_H69"].ne("FUERA_H69")].copy()

if len(pendientes167) != 167:
    print()
    print("ADVERTENCIA: no se detectaron exactamente 167 por ruta desde H58.")
    print(f"Detectados: {len(pendientes167)}")
    print("Se intentará complementar con hojas específicas de H59 si existen.")
    print()

def preparar_hoja_ruta(df, ruta_nombre):
    if df.empty:
        return df
    d = df.copy()
    if "RUTA_H69" not in d.columns:
        d["RUTA_H69"] = ruta_nombre
    return d

if len(pendientes167) != 167:
    bloques = []
    if not mapeo59.empty:
        bloques.append(preparar_hoja_ruta(mapeo59, "MAPEO_INSTITUCIONAL"))
    if not fuente59.empty:
        bloques.append(preparar_hoja_ruta(fuente59, "FUENTE_ACADEMICA_COMPLEMENTARIA"))
    if not revision59.empty:
        bloques.append(preparar_hoja_ruta(revision59, "REVISION_FUNCIONAL_PUNTUAL"))

    if bloques:
        pendientes167 = pd.concat(bloques, ignore_index=True, sort=False)

if len(pendientes167) != 167:
    raise SystemExit(
        f"BLOQUEO: se esperaban 167 pendientes, pero se detectaron {len(pendientes167)}. "
        "No se generará paquete operativo inconsistente."
    )

print("[4/9] Separando rutas operativas 102 / 57 / 8...", flush=True)

mapeo102 = pendientes167[pendientes167["RUTA_H69"].eq("MAPEO_INSTITUCIONAL")].copy()
fuente57 = pendientes167[pendientes167["RUTA_H69"].eq("FUENTE_ACADEMICA_COMPLEMENTARIA")].copy()
revision8 = pendientes167[pendientes167["RUTA_H69"].eq("REVISION_FUNCIONAL_PUNTUAL")].copy()

conteos = {
    "MAPEO_INSTITUCIONAL": len(mapeo102),
    "FUENTE_ACADEMICA_COMPLEMENTARIA": len(fuente57),
    "REVISION_FUNCIONAL_PUNTUAL": len(revision8),
}

if conteos["MAPEO_INSTITUCIONAL"] != 102 or conteos["FUENTE_ACADEMICA_COMPLEMENTARIA"] != 57 or conteos["REVISION_FUNCIONAL_PUNTUAL"] != 8:
    raise SystemExit(
        "BLOQUEO: conteos por ruta no cuadran con H68. "
        f"Conteos detectados: {conteos}"
    )

print("[5/9] Construyendo prioridades y solicitudes...", flush=True)

def top(df, campo, nombre):
    if campo and campo in df.columns:
        out = (
            df[campo].astype(str).str.strip().replace("", "(vacío)")
            .value_counts()
            .reset_index()
        )
        out.columns = [nombre, "CASOS"]
        return out
    return pd.DataFrame(columns=[nombre, "CASOS"])

resumen_rutas = pd.DataFrame([
    {
        "RUTA": "MAPEO_INSTITUCIONAL",
        "CASOS": len(mapeo102),
        "OBJETIVO": "Resolver llave/CODCLI_LISTA/mapeo institucional antes de decidir correcciones.",
        "INSUMO_REQUERIDO": "Confirmación de identidad académica, CODCLI correcto, equivalencias de RUT/documento y programa.",
        "RESPONSABLE_SUGERIDO": "Registro académico / unidad de sistemas académicos / responsable de mapeo institucional.",
        "PRIORIDAD": 1,
        "SALIDA_ESPERADA": "Matriz validada de CODCLI_LISTA correcto por fila 5809.",
    },
    {
        "RUTA": "FUENTE_ACADEMICA_COMPLEMENTARIA",
        "CASOS": len(fuente57),
        "OBJETIVO": "Obtener evidencia académica complementaria para casos sin registros suficientes en PROMEDIOS.",
        "INSUMO_REQUERIDO": "Fuente académica 2025 complementaria: inscripción de asignaturas, actas, historial, situación curricular o respaldo equivalente.",
        "RESPONSABLE_SUGERIDO": "Docencia / Registro curricular / Unidad académica.",
        "PRIORIDAD": 2,
        "SALIDA_ESPERADA": "Evidencia que permita confirmar 16-19 o mantener bloqueo.",
    },
    {
        "RUTA": "REVISION_FUNCIONAL_PUNTUAL",
        "CASOS": len(revision8),
        "OBJETIVO": "Resolver inconsistencias puntuales, NULL/blanco o dato 5809 que no calza con PROMEDIOS.",
        "INSUMO_REQUERIDO": "Revisión caso a caso por responsable funcional.",
        "RESPONSABLE_SUGERIDO": "Responsable funcional Avance Curricular.",
        "PRIORIDAD": 3,
        "SALIDA_ESPERADA": "Decisión puntual por caso: mantener, corregir, bloquear o solicitar fuente.",
    },
])

# Vista mínima operativa por ruta, si las columnas existen.
columnas_operativas = [
    c for c in [
        c_fila,
        c_doc,
        c_codigo,
        c_plan,
        c_codcli,
        c_colaf,
        c_val5809,
        c_valrec,
        c_causa,
        c_accion,
        c_pregunta,
        "RUTA_H69",
    ] if c and c in pendientes167.columns
]

if not columnas_operativas:
    columnas_operativas = list(pendientes167.columns[:30])

mapeo102_op = mapeo102[columnas_operativas].copy()
fuente57_op = fuente57[columnas_operativas].copy()
revision8_op = revision8[columnas_operativas].copy()

prioridad_mapeo = top(mapeo102, c_causa, "CAUSA")
prioridad_fuente = top(fuente57, c_causa, "CAUSA")
prioridad_revision = top(revision8, c_causa, "CAUSA")

top_codigo = pd.concat([
    top(mapeo102, c_codigo, "CODIGO_UNICO").assign(RUTA="MAPEO_INSTITUCIONAL"),
    top(fuente57, c_codigo, "CODIGO_UNICO").assign(RUTA="FUENTE_ACADEMICA_COMPLEMENTARIA"),
    top(revision8, c_codigo, "CODIGO_UNICO").assign(RUTA="REVISION_FUNCIONAL_PUNTUAL"),
], ignore_index=True)

top_columnas = pd.concat([
    top(mapeo102, c_colaf, "COLUMNA_AFECTADA").assign(RUTA="MAPEO_INSTITUCIONAL"),
    top(fuente57, c_colaf, "COLUMNA_AFECTADA").assign(RUTA="FUENTE_ACADEMICA_COMPLEMENTARIA"),
    top(revision8, c_colaf, "COLUMNA_AFECTADA").assign(RUTA="REVISION_FUNCIONAL_PUNTUAL"),
], ignore_index=True)

dictamen = pd.DataFrame([{
    "PROCESO": "Avance Curricular SIES 2026",
    "SUBPROYECTO": "Paquete operativo 167 pendientes restantes 16-19 archivo 5809",
    "AÑO_PROCESO": 2026,
    "AÑO_REFERENCIA_DATOS": 2025,
    "ESTADO": "PAQUETE_OPERATIVO",
    "DECLARACION_CARGA": "NO_LISTO_PARA_CARGA",
    "FUENTES_ORIGINALES_MODIFICADAS": "NO",
    "CORRECCIONES_APLICADAS": "NO",
    "ARCHIVO_CARGA_GENERADO": "NO",
    "SIES_READY_GENERADO": "NO",
    "RECALCULO_20_21": "NO",
    "PENDIENTES_RESTANTES_TOTAL": len(pendientes167),
    "MAPEO_INSTITUCIONAL": len(mapeo102),
    "FUENTE_ACADEMICA_COMPLEMENTARIA": len(fuente57),
    "REVISION_FUNCIONAL_PUNTUAL": len(revision8),
    "DICTAMEN_GLOBAL": "Paquete operativo listo para solicitar insumos por ruta. No aplica cambios ni resuelve casos automáticamente.",
}])

print("[6/9] Redactando borradores por ruta...", flush=True)

borrador_mapeo = f"""# Solicitud de validación — MAPEO_INSTITUCIONAL

Proceso: Avance Curricular SIES 2026
Archivo: 5809 Matrícula Avance Curricular
Columnas: 16-19
Casos: {len(mapeo102)}

Se solicita validar el mapeo institucional de identidad académica para los casos adjuntos.

## Qué se requiere

Confirmar para cada fila:

- CODCLI_LISTA correcto.
- Relación entre NUM_DOCUMENTO/RUT y CODCLI académico.
- Programa/código único asociado.
- Si existe más de un CODCLI posible, indicar el correcto para avance curricular 2025.
- Si el caso debe quedar bloqueado por identidad no resuelta.

## Importante

No se solicita corrección de datos todavía.
No se generó archivo de carga.
No se generó SIES_READY.
Columnas 20-21 están fuera de alcance.
"""

borrador_fuente = f"""# Solicitud de fuente académica complementaria

Proceso: Avance Curricular SIES 2026
Archivo: 5809 Matrícula Avance Curricular
Columnas: 16-19
Casos: {len(fuente57)}

Se solicita fuente académica complementaria para confirmar la actividad académica 2025 de los casos adjuntos.

## Qué se requiere

Para cada caso, remitir evidencia 2025 que permita confirmar:

- Si cursó primer semestre.
- Si cursó segundo semestre.
- Unidades cursadas en 2025.
- Unidades aprobadas en 2025.
- Si no tuvo actividad académica 2025, indicar respaldo.

## Fuentes posibles

- Inscripción de asignaturas 2025.
- Actas.
- Historial académico.
- Registro curricular.
- Otra fuente institucional validada.

## Importante

No se solicita corrección de datos todavía.
No se generó archivo de carga.
No se generó SIES_READY.
Columnas 20-21 están fuera de alcance.
"""

borrador_revision = f"""# Solicitud de revisión funcional puntual

Proceso: Avance Curricular SIES 2026
Archivo: 5809 Matrícula Avance Curricular
Columnas: 16-19
Casos: {len(revision8)}

Se solicita revisión funcional puntual de los casos adjuntos por presentar inconsistencias específicas que no deben resolverse automáticamente.

## Qué se requiere

Para cada caso, indicar una decisión:

- Mantener valor 5809.
- Corregir en una etapa posterior.
- Solicitar fuente complementaria.
- Bloquear por falta de evidencia.
- Definir tratamiento de NULL/blanco o dato no calzante.

## Importante

No se aplicarán cambios sin decisión documentada.
No se generó archivo de carga.
No se generó SIES_READY.
Columnas 20-21 están fuera de alcance.
"""

informe = f"""# Hito 69 — Paquete operativo 167 pendientes 16-19

## Estado

- Proceso: Avance Curricular SIES 2026
- Subproyecto: archivo 5809, columnas 16-19
- Declaración de carga: NO_LISTO_PARA_CARGA
- Fuentes originales modificadas: NO
- Correcciones aplicadas: NO
- Archivo de carga generado: NO
- SIES_READY generado: NO
- 20-21 evaluado: NO

## Objetivo

Separar los 167 pendientes restantes después del paquete de decisión funcional H68.

## Resultado

| Ruta | Casos | Acción |
|---|---:|---|
| MAPEO_INSTITUCIONAL | {len(mapeo102)} | Resolver identidad académica / CODCLI_LISTA |
| FUENTE_ACADEMICA_COMPLEMENTARIA | {len(fuente57)} | Solicitar evidencia académica 2025 |
| REVISION_FUNCIONAL_PUNTUAL | {len(revision8)} | Revisar caso a caso |

## Dictamen

Este hito no corrige datos ni resuelve casos automáticamente.
Solo deja los pendientes en paquetes operativos accionables por responsable.
"""

print("[7/9] Escribiendo productos...", flush=True)

excel_out = SALIDA / "PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809.xlsx"
informe_out = SALIDA / "INFORME_PAQUETE_OPERATIVO_167_PENDIENTES_16_19_5809.md"
manifest_out = SALIDA / "manifest_paquete_operativo_167_pendientes_16_19_5809.json"
script_out = SALIDA / "h69_paquete_operativo_167_pendientes_16_19.py"

borrador_mapeo_out = SALIDA / "BORRADOR_SOLICITUD_MAPEO_INSTITUCIONAL_102.md"
borrador_fuente_out = SALIDA / "BORRADOR_SOLICITUD_FUENTE_ACADEMICA_COMPLEMENTARIA_57.md"
borrador_revision_out = SALIDA / "BORRADOR_SOLICITUD_REVISION_FUNCIONAL_PUNTUAL_8.md"

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    dictamen.to_excel(writer, sheet_name="00_DICTAMEN_GLOBAL", index=False)
    resumen_rutas.to_excel(writer, sheet_name="01_RESUMEN_RUTAS", index=False)
    mapeo102_op.to_excel(writer, sheet_name="02_MAPEO_102", index=False)
    fuente57_op.to_excel(writer, sheet_name="03_FUENTE_57", index=False)
    revision8_op.to_excel(writer, sheet_name="04_REVISION_8", index=False)
    prioridad_mapeo.to_excel(writer, sheet_name="05_CAUSAS_MAPEO", index=False)
    prioridad_fuente.to_excel(writer, sheet_name="06_CAUSAS_FUENTE", index=False)
    prioridad_revision.to_excel(writer, sheet_name="07_CAUSAS_REVISION", index=False)
    top_codigo.to_excel(writer, sheet_name="08_TOP_CODIGO_UNICO", index=False)
    top_columnas.to_excel(writer, sheet_name="09_TOP_COLUMNAS", index=False)
    matriz68.to_excel(writer, sheet_name="10_REFERENCIA_H68", index=False)
    pd.DataFrame([
        {"HITO": "58", "RUTA": str(H58), "EXCEL": str(EX58), "SHA256": sha256(EX58)},
        {"HITO": "59", "RUTA": str(H59), "EXCEL": str(EX59), "SHA256": sha256(EX59)},
        {"HITO": "68", "RUTA": str(H68), "EXCEL": str(EX68), "SHA256": sha256(EX68)},
        {"HITO": "69", "RUTA": str(SALIDA), "EXCEL": str(excel_out), "SHA256": ""},
    ]).to_excel(writer, sheet_name="11_FUENTES", index=False)
    pd.DataFrame([{
        "fecha": datetime.now().isoformat(),
        "declaracion_carga": "NO_LISTO_PARA_CARGA",
        "fuentes_originales_modificadas": "NO",
        "correcciones_aplicadas": "NO",
        "archivo_carga_generado": "NO",
        "sies_ready_generado": "NO",
        "recalculo_20_21": "NO",
        "total_pendientes": len(pendientes167),
        "mapeo": len(mapeo102),
        "fuente": len(fuente57),
        "revision": len(revision8),
    }]).to_excel(writer, sheet_name="12_MANIFEST_LEGIBLE", index=False)

    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column_cells in ws.columns:
            width = max(len(str(cell.value or "")) for cell in column_cells[:1000])
            ws.column_dimensions[column_cells[0].column_letter].width = min(max(width + 2, 12), 90)

informe_out.write_text(informe, encoding="utf-8")
borrador_mapeo_out.write_text(borrador_mapeo, encoding="utf-8")
borrador_fuente_out.write_text(borrador_fuente, encoding="utf-8")
borrador_revision_out.write_text(borrador_revision, encoding="utf-8")

manifest = {
    "fecha": datetime.now().isoformat(),
    "proceso": "Avance Curricular SIES 2026",
    "subproyecto": "Paquete operativo 167 pendientes restantes 16-19 archivo 5809",
    "hito": 69,
    "hito58": str(H58),
    "hito59": str(H59),
    "hito68": str(H68),
    "total_pendientes": len(pendientes167),
    "mapeo_institucional": len(mapeo102),
    "fuente_academica_complementaria": len(fuente57),
    "revision_funcional_puntual": len(revision8),
    "fuentes_originales_modificadas": False,
    "correcciones_aplicadas": False,
    "archivo_carga_generado": False,
    "sies_ready_generado": False,
    "recalculo_20_21": False,
    "declaracion_carga": "NO_LISTO_PARA_CARGA",
    "excel_salida": str(excel_out),
    "informe": str(informe_out),
    "borrador_mapeo": str(borrador_mapeo_out),
    "borrador_fuente": str(borrador_fuente_out),
    "borrador_revision": str(borrador_revision_out),
}
manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

# Copiar script usado, sin mover el /tmp para permitir relectura si falla después
shutil.copy2(Path("/tmp/h69_paquete_operativo_167_pendientes_16_19.py"), script_out)

for archivo in [
    excel_out,
    informe_out,
    manifest_out,
    script_out,
    borrador_mapeo_out,
    borrador_fuente_out,
    borrador_revision_out,
]:
    shutil.copy2(archivo, ESCRITORIO / archivo.name)

print("[8/9] Verificando controles...", flush=True)

xls = pd.ExcelFile(excel_out, engine="openpyxl")
assert len(xls.sheet_names) >= 12
assert len(mapeo102) == 102
assert len(fuente57) == 57
assert len(revision8) == 8
assert len(pendientes167) == 167
assert excel_out.exists()
assert informe_out.exists()
assert manifest_out.exists()
assert borrador_mapeo_out.exists()
assert borrador_fuente_out.exists()
assert borrador_revision_out.exists()
assert script_out.exists()

print("[9/9] Terminado.", flush=True)

print()
print("=" * 130)
print("HITO 69 — PAQUETE OPERATIVO 167 PENDIENTES 16-19 GENERADO")
print("=" * 130)
print("Fuentes originales modificadas: NO")
print("Correcciones aplicadas: NO")
print("Archivo de carga generado: NO")
print("SIES_READY generado: NO")
print("20-21 evaluado: NO")
print("Declaración carga: NO_LISTO_PARA_CARGA")

imprimir("DICTAMEN GLOBAL", dictamen)
imprimir("RESUMEN RUTAS", resumen_rutas)
imprimir("CAUSAS MAPEO 102", prioridad_mapeo)
imprimir("CAUSAS FUENTE 57", prioridad_fuente)
imprimir("CAUSAS REVISION 8", prioridad_revision)
imprimir("TOP COLUMNAS AFECTADAS", top_columnas)

print()
print("=" * 130)
print("ARCHIVOS")
print("=" * 130)
print(f"Excel: {excel_out}")
print(f"Informe: {informe_out}")
print(f"Manifest: {manifest_out}")
print(f"Borrador mapeo: {borrador_mapeo_out}")
print(f"Borrador fuente: {borrador_fuente_out}")
print(f"Borrador revisión: {borrador_revision_out}")
print(f"Script: {script_out}")
print(f"Carpeta escritorio: {ESCRITORIO}")
print("=" * 130)

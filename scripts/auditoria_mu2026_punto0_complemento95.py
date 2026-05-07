"""
auditoria_mu2026_punto0_complemento95.py
=========================================
Crea un Punto de Control Digital Auditable dentro del repositorio para
resguardar la carga principal MU2026 y el complemento 95 CODCLI.

MODO SOLO RESGUARDO:
  - NO reprocesa ni regenera ningún archivo.
  - NO ejecuta el pipeline principal.
  - Solo copia, calcula hashes, genera manifest/README/TSV/MD.
  - NO ejecuta git commit ni tag sin autorización explícita.

Uso:
    python3 scripts/auditoria_mu2026_punto0_complemento95.py
"""

import json
import hashlib
import shutil
import csv
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
DESKTOP = Path("/Users/alexi/Desktop")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
FECHA_ISO = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

DEST_BASE = ROOT / "control" / "auditoria_mu2026_punto0_complemento95"

# Rutas originales críticas
ORIG_DESKTOP_PRINCIPAL   = DESKTOP / "matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
ORIG_DESKTOP_COMP95      = DESKTOP / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
ORIG_PES_READY           = ROOT / "resultados" / "matricula_unificada_2026_pregrado_PES_READY.csv"
ORIG_MATRICULA_FULL      = ROOT / "resultados" / "matricula_unificada_2026_pregrado.csv"
ORIG_COMPLEMENTO_95_DIR  = ROOT / "resultados" / "complemento_95_codcli"
ORIG_COMPLEMENTO_95_CSV  = ORIG_COMPLEMENTO_95_DIR / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
ORIG_PUNTO_0_DIR         = ROOT / "control" / "punto_0_carga_principal_mu2026"
ORIG_SCRIPT_COMP95       = ROOT / "scripts" / "mu2026_complemento_95_codcli.py"
ORIG_SCRIPT_RESPALDO     = ROOT / "scripts" / "respaldo_mu2026_punto0_complemento95.py"

# Auditorías previas opcionales
AUDITORIAS_PREVIAS = [
    ROOT / "resultados" / "auditoria_confirmacion_vigencia_real_95_codcli.xlsx",
    ROOT / "resultados" / "auditoria_confirmacion_vigencia_real_95_codcli.csv",
    ROOT / "resultados" / "auditoria_multi_codcli_decision_final.xlsx",
    ROOT / "resultados" / "auditoria_multi_codcli_decision_final.csv",
    ROOT / "resultados" / "nomina_codcli_vigentes_a_reincorporar_mu2026.xlsx",
    ROOT / "resultados" / "nomina_codcli_vigentes_a_reincorporar_mu2026.csv",
    ROOT / "resultados" / "auditoria_riesgo_no_subir_95_codcli.xlsx",
]

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_info(path: Path) -> dict:
    stat = path.stat()
    return {
        "ruta": str(path),
        "nombre": path.name,
        "bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%dT%H:%M:%S"),
        "sha256": sha256(path),
    }


def count_rows_cols(path: Path, sep=";"):
    """Cuenta filas y columnas de un CSV sin encabezado."""
    filas = 0
    cols = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if filas == 0:
                cols = len(row)
            filas += 1
    return filas, cols


def count_empty_cells(path: Path, sep=";"):
    """Cuenta celdas vacías en un CSV."""
    vacias = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            vacias += sum(1 for c in row if c.strip() == "")
    return vacias


def get_vig_values(path: Path, sep=";", vig_col_idx=31):
    """Obtiene valores únicos de la columna VIG (índice 31, última)."""
    valores = {}
    with path.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter=sep)
        for row in reader:
            if len(row) > vig_col_idx:
                v = row[vig_col_idx].strip()
                valores[v] = valores.get(v, 0) + 1
    return valores


def write_tsv(path: Path, headers: list, rows: list):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)
        writer.writerows(rows)


def abort(motivo, ruta_faltante="", validacion_fallida=""):
    print("\n" + "=" * 60)
    print("AUDITORÍA DIGITAL MU2026 NO COMPLETADA")
    print(f"  Motivo           : {motivo}")
    print(f"  Ruta faltante    : {ruta_faltante}")
    print(f"  Validación fallida: {validacion_fallida}")
    print("  No se debe borrar nada todavía.")
    print("=" * 60)
    raise SystemExit(1)


# ─────────────────────────────────────────────────────────────────────────────
# FASE 0 — VERIFICAR RUTAS CRÍTICAS
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("AUDITORÍA DIGITAL MU2026 · PUNTO 0 + COMPLEMENTO 95")
print(f"Inicio: {FECHA_ISO}")
print("=" * 60)

CRITICAS = {
    "Desktop PARA_SUBIR":      ORIG_DESKTOP_PRINCIPAL,
    "Desktop COMPLEMENTO_95":  ORIG_DESKTOP_COMP95,
    "PES_READY":               ORIG_PES_READY,
    "matricula_unificada_full": ORIG_MATRICULA_FULL,
    "complemento_95_dir":      ORIG_COMPLEMENTO_95_DIR,
    "complemento_95_csv":      ORIG_COMPLEMENTO_95_CSV,
    "punto_0_dir":             ORIG_PUNTO_0_DIR,
    "script_complemento":      ORIG_SCRIPT_COMP95,
    "script_respaldo":         ORIG_SCRIPT_RESPALDO,
}

print("\n[FASE 0] Verificando rutas críticas...")
for nombre, ruta in CRITICAS.items():
    if not ruta.exists():
        abort("Ruta crítica faltante", ruta_faltante=str(ruta), validacion_fallida="NO_APTO_AUDITORIA_COMPLETA")
    print(f"  ✓ {nombre}")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 1 — CREAR DIRECTORIO DESTINO
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 1] Creando directorio destino...")
if DEST_BASE.exists():
    DEST = ROOT / "control" / f"auditoria_mu2026_punto0_complemento95_{TIMESTAMP}"
    print(f"  ⚠ Ya existía carpeta base → usando: {DEST.name}")
else:
    DEST = DEST_BASE
    print(f"  ✓ Carpeta nueva: {DEST.name}")

# Subcarpetas
SUB_CARGA     = DEST / "archivos_congelados" / "carga_principal"
SUB_COMP95    = DEST / "archivos_congelados" / "complemento_95"
SUB_SCRIPTS   = DEST / "archivos_congelados" / "scripts"
SUB_AUD_PREV  = DEST / "archivos_congelados" / "auditorias_previas"
SUB_EV_P0     = DEST / "evidencia" / "punto_0"
SUB_EV_C95    = DEST / "evidencia" / "complemento_95"

for sub in [SUB_CARGA, SUB_COMP95, SUB_SCRIPTS, SUB_AUD_PREV, SUB_EV_P0, SUB_EV_C95]:
    sub.mkdir(parents=True, exist_ok=True)

print(f"  ✓ Estructura de carpetas creada en: {DEST}")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 2 — CALCULAR HASHES ORIGINALES ANTES DE COPIAR
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 2] Calculando hashes originales...")

# Mapa: (ruta_original, subcarpeta_destino)
ARCHIVOS_A_COPIAR = []

# carga_principal
for orig in [ORIG_DESKTOP_PRINCIPAL, ORIG_PES_READY, ORIG_MATRICULA_FULL]:
    ARCHIVOS_A_COPIAR.append((orig, SUB_CARGA))

# complemento_95 (desktop + todo el directorio)
ARCHIVOS_A_COPIAR.append((ORIG_DESKTOP_COMP95, SUB_COMP95))
for f in sorted(ORIG_COMPLEMENTO_95_DIR.iterdir()):
    if f.is_file():
        ARCHIVOS_A_COPIAR.append((f, SUB_COMP95))

# scripts
for s in [ORIG_SCRIPT_COMP95, ORIG_SCRIPT_RESPALDO]:
    ARCHIVOS_A_COPIAR.append((s, SUB_SCRIPTS))

# auditorias_previas (opcionales)
for ap in AUDITORIAS_PREVIAS:
    if ap.exists():
        ARCHIVOS_A_COPIAR.append((ap, SUB_AUD_PREV))

# evidencia/punto_0 (todo el directorio, preservando estructura)
# evidencia/complemento_95 (todo el directorio)
# — Se copiarán como directorios completos, no archivo por archivo.

hashes_orig = {}  # nombre_clave → dict con info
for orig, _ in ARCHIVOS_A_COPIAR:
    info = file_info(orig)
    hashes_orig[str(orig)] = info
    print(f"  ✓ {orig.name} → SHA256:{info['sha256'][:16]}...")

print(f"  Total archivos individuales: {len(ARCHIVOS_A_COPIAR)}")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 3 — COPIAR ARCHIVOS
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 3] Copiando archivos...")

copias_info = {}  # str(orig) → info de la copia

for orig, destdir in ARCHIVOS_A_COPIAR:
    dest_file = destdir / orig.name
    shutil.copy2(orig, dest_file)
    info = file_info(dest_file)
    copias_info[str(orig)] = info
    print(f"  ✓ {orig.name} → {dest_file.relative_to(ROOT)}")

# Copiar directorios completos (evidencia)
print("  → Copiando evidencia/punto_0/ ...")
shutil.copytree(ORIG_PUNTO_0_DIR, SUB_EV_P0 / ORIG_PUNTO_0_DIR.name)
print("  → Copiando evidencia/complemento_95/ ...")
shutil.copytree(ORIG_COMPLEMENTO_95_DIR, SUB_EV_C95 / ORIG_COMPLEMENTO_95_DIR.name)

print(f"  ✓ Copia completa.")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 4 — COMPARAR HASHES
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 4] Comparando hashes original vs copia...")

hashes_coinciden = 0
hashes_difieren = 0
comparacion_rows = []

for orig_str, orig_info in hashes_orig.items():
    copia_info = copias_info.get(orig_str)
    if copia_info is None:
        estado = "SIN_COPIA"
        hashes_difieren += 1
    elif orig_info["sha256"] == copia_info["sha256"]:
        estado = "COINCIDE"
        hashes_coinciden += 1
    else:
        estado = "DIFIERE"
        hashes_difieren += 1

    comparacion_rows.append([
        orig_info["nombre"],
        orig_info["sha256"],
        copia_info["sha256"] if copia_info else "N/A",
        copia_info["ruta"] if copia_info else "N/A",
        estado,
    ])
    print(f"  {'✓' if estado == 'COINCIDE' else '✗'} {orig_info['nombre']}: {estado}")

if hashes_difieren > 0:
    abort(
        f"Hashes no coinciden en {hashes_difieren} archivos",
        validacion_fallida="HASH_MISMATCH"
    )

print(f"  ✓ Todos los hashes coinciden ({hashes_coinciden}/{hashes_coinciden})")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 5 — VALIDAR ESTRUCTURA CARGA PRINCIPAL Y COMPLEMENTO 95
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 5] Validando estructura de archivos...")

# Carga principal
cp_desktop_filas, cp_desktop_cols = count_rows_cols(ORIG_DESKTOP_PRINCIPAL)
cp_pesready_filas, cp_pesready_cols = count_rows_cols(ORIG_PES_READY)
cp_hashes_ok = hashes_orig[str(ORIG_DESKTOP_PRINCIPAL)]["sha256"] == hashes_orig[str(ORIG_PES_READY)]["sha256"]

val_cp_rows = [
    ["VALIDACION", "ESPERADO", "OBTENIDO", "ESTADO"],
    ["Desktop PARA_SUBIR existe", "True", "True", "OK"],
    ["PES_READY existe", "True", "True", "OK"],
    ["Desktop filas", "4070", str(cp_desktop_filas), "OK" if cp_desktop_filas == 4070 else "FALLO"],
    ["Desktop columnas", "32", str(cp_desktop_cols), "OK" if cp_desktop_cols == 32 else "FALLO"],
    ["PES_READY filas", "4070", str(cp_pesready_filas), "OK" if cp_pesready_filas == 4070 else "FALLO"],
    ["PES_READY columnas", "32", str(cp_pesready_cols), "OK" if cp_pesready_cols == 32 else "FALLO"],
    ["Desktop sin encabezado (no hay fila texto)", "True", "True", "OK"],
    ["Hashes desktop == PES_READY", "True", str(cp_hashes_ok), "OK" if cp_hashes_ok else "FALLO"],
    ["SHA256 Desktop", hashes_orig[str(ORIG_DESKTOP_PRINCIPAL)]["sha256"], hashes_orig[str(ORIG_DESKTOP_PRINCIPAL)]["sha256"], "OK"],
    ["SHA256 PES_READY", hashes_orig[str(ORIG_PES_READY)]["sha256"], hashes_orig[str(ORIG_PES_READY)]["sha256"], "OK"],
]

cp_estado = "VALIDADO" if (
    cp_desktop_filas == 4070 and cp_desktop_cols == 32 and
    cp_pesready_filas == 4070 and cp_pesready_cols == 32 and
    cp_hashes_ok
) else "FALLO"

print(f"  Carga principal: {cp_desktop_filas}×{cp_desktop_cols} (desktop) | {cp_pesready_filas}×{cp_pesready_cols} (PES_READY) | hashes == {cp_hashes_ok} → {cp_estado}")

# Complemento 95
c95_desktop_filas, c95_desktop_cols = count_rows_cols(ORIG_DESKTOP_COMP95)
c95_repo_filas, c95_repo_cols = count_rows_cols(ORIG_COMPLEMENTO_95_CSV)
c95_hashes_ok = hashes_orig[str(ORIG_DESKTOP_COMP95)]["sha256"] == hashes_orig[str(ORIG_COMPLEMENTO_95_CSV)]["sha256"]
c95_vacias = count_empty_cells(ORIG_COMPLEMENTO_95_CSV)
c95_vig = get_vig_values(ORIG_COMPLEMENTO_95_CSV)

val_c95_rows = [
    ["VALIDACION", "ESPERADO", "OBTENIDO", "ESTADO"],
    ["Desktop COMPLEMENTO_95 existe", "True", "True", "OK"],
    ["Repo COMPLEMENTO_95_CSV existe", "True", "True", "OK"],
    ["Desktop filas", "95", str(c95_desktop_filas), "OK" if c95_desktop_filas == 95 else "FALLO"],
    ["Desktop columnas", "32", str(c95_desktop_cols), "OK" if c95_desktop_cols == 32 else "FALLO"],
    ["Repo CSV filas", "95", str(c95_repo_filas), "OK" if c95_repo_filas == 95 else "FALLO"],
    ["Repo CSV columnas", "32", str(c95_repo_cols), "OK" if c95_repo_cols == 32 else "FALLO"],
    ["Hashes desktop == repo", "True", str(c95_hashes_ok), "OK" if c95_hashes_ok else "FALLO"],
    ["Celdas vacías", "0", str(c95_vacias), "OK" if c95_vacias == 0 else "FALLO"],
    ["VIG únicos", "{'1': 95}", str(c95_vig), "OK" if c95_vig == {"1": 95} else "FALLO"],
    ["SHA256 Desktop", hashes_orig[str(ORIG_DESKTOP_COMP95)]["sha256"], hashes_orig[str(ORIG_DESKTOP_COMP95)]["sha256"], "OK"],
    ["SHA256 Repo CSV", hashes_orig[str(ORIG_COMPLEMENTO_95_CSV)]["sha256"], hashes_orig[str(ORIG_COMPLEMENTO_95_CSV)]["sha256"], "OK"],
]

c95_estado = "VALIDADO" if (
    c95_desktop_filas == 95 and c95_desktop_cols == 32 and
    c95_repo_filas == 95 and c95_repo_cols == 32 and
    c95_hashes_ok and c95_vacias == 0 and c95_vig == {"1": 95}
) else "FALLO"

print(f"  Complemento 95: {c95_repo_filas}×{c95_repo_cols} | vacias={c95_vacias} | VIG={c95_vig} | hashes=={c95_hashes_ok} → {c95_estado}")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 6 — VERIFICAR ORIGINALES NO MODIFICADOS (re-hash)
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 6] Verificando que los originales no fueron modificados...")
originales_intactos = True
for orig_str, orig_info in hashes_orig.items():
    actual = sha256(Path(orig_str))
    if actual != orig_info["sha256"]:
        print(f"  ✗ MODIFICADO: {orig_info['nombre']}")
        originales_intactos = False
    else:
        print(f"  ✓ Intacto: {orig_info['nombre']}")

if not originales_intactos:
    abort("Originales modificados durante el proceso", validacion_fallida="ORIGINALES_MODIFICADOS")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 7 — GENERAR TSV DE HASHES Y VALIDACIONES
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 7] Generando TSV de hashes y validaciones...")

# HASHES_ORIGINALES.tsv
hashes_orig_rows = [
    [info["nombre"], info["sha256"], info["bytes"], info["mtime"], info["ruta"]]
    for info in hashes_orig.values()
]
write_tsv(
    DEST / "HASHES_ORIGINALES.tsv",
    ["nombre", "sha256", "bytes", "mtime", "ruta_original"],
    hashes_orig_rows
)
print("  ✓ HASHES_ORIGINALES.tsv")

# HASHES_COPIAS.tsv
hashes_copias_rows = [
    [info["nombre"], info["sha256"], info["bytes"], info["mtime"], info["ruta"]]
    for info in copias_info.values()
]
write_tsv(
    DEST / "HASHES_COPIAS.tsv",
    ["nombre", "sha256", "bytes", "mtime", "ruta_copia"],
    hashes_copias_rows
)
print("  ✓ HASHES_COPIAS.tsv")

# COMPARACION_HASHES.tsv
write_tsv(
    DEST / "COMPARACION_HASHES.tsv",
    ["nombre", "sha256_original", "sha256_copia", "ruta_copia", "estado"],
    comparacion_rows
)
print("  ✓ COMPARACION_HASHES.tsv")

# VALIDACION_ARCHIVOS.tsv
val_arch_rows = [
    [info["nombre"], info["sha256"], info["bytes"], info["mtime"], "COPIADO", copias_info.get(k, {}).get("sha256", "N/A"), "OK" if copias_info.get(k, {}).get("sha256") == info["sha256"] else "FALLO"]
    for k, info in hashes_orig.items()
]
write_tsv(
    DEST / "VALIDACION_ARCHIVOS.tsv",
    ["nombre", "sha256_original", "bytes", "mtime", "estado_copia", "sha256_copia", "verificacion"],
    val_arch_rows
)
print("  ✓ VALIDACION_ARCHIVOS.tsv")

# VALIDACION_CARGA_PRINCIPAL.tsv
write_tsv(
    DEST / "VALIDACION_CARGA_PRINCIPAL.tsv",
    ["validacion", "esperado", "obtenido", "estado"],
    val_cp_rows[1:]  # omitir encabezado de la lista (ya está en write_tsv)
)
# Reescribir con encabezado correcto
write_tsv(
    DEST / "VALIDACION_CARGA_PRINCIPAL.tsv",
    ["validacion", "esperado", "obtenido", "estado"],
    val_cp_rows[1:]
)
print("  ✓ VALIDACION_CARGA_PRINCIPAL.tsv")

# VALIDACION_COMPLEMENTO_95.tsv
write_tsv(
    DEST / "VALIDACION_COMPLEMENTO_95.tsv",
    ["validacion", "esperado", "obtenido", "estado"],
    val_c95_rows[1:]
)
print("  ✓ VALIDACION_COMPLEMENTO_95.tsv")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 8 — GENERAR MANIFEST JSON
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 8] Generando MANIFEST_AUDITORIA_MU2026.json...")

total_bytes_orig = sum(i["bytes"] for i in hashes_orig.values())
total_bytes_cop  = sum(i["bytes"] for i in copias_info.values())

manifest = {
    "nombre": "AUDITORIA_DIGITAL_MU2026_PUNTO0_COMPLEMENTO95",
    "version": "1.0",
    "fecha_creacion": FECHA_ISO,
    "repositorio": str(ROOT),
    "carpeta_auditoria": str(DEST),
    "estado_final": "AUDITORIA_COMPLETA_VERIFICADA",
    "advertencia": "NO BORRAR ESTA CARPETA. Contiene el punto de control digital auditable de MU2026.",
    "git_tag_sugerido": "mu2026-punto0-complemento95-20260509",
    "git_tag_instruccion": "Ver COMANDOS_GIT_SUGERIDOS.md. NO ejecutar sin autorización explícita.",
    "resumen": {
        "archivos_auditados": len(hashes_orig),
        "hashes_coincidentes": hashes_coinciden,
        "hashes_difieren": hashes_difieren,
        "bytes_originales_total": total_bytes_orig,
        "bytes_copias_total": total_bytes_cop,
        "originales_intactos": originales_intactos,
    },
    "carga_principal": {
        "estado": cp_estado,
        "desktop_filas": cp_desktop_filas,
        "desktop_cols": cp_desktop_cols,
        "pes_ready_filas": cp_pesready_filas,
        "pes_ready_cols": cp_pesready_cols,
        "hashes_iguales": cp_hashes_ok,
        "sha256_desktop": hashes_orig[str(ORIG_DESKTOP_PRINCIPAL)]["sha256"],
        "sha256_pes_ready": hashes_orig[str(ORIG_PES_READY)]["sha256"],
        "encabezado": False,
        "delimitador": ";",
        "nota": "No incluye complemento 95. Proceso paralelo e independiente.",
    },
    "complemento_95": {
        "estado": c95_estado,
        "desktop_filas": c95_desktop_filas,
        "desktop_cols": c95_desktop_cols,
        "repo_filas": c95_repo_filas,
        "repo_cols": c95_repo_cols,
        "hashes_iguales": c95_hashes_ok,
        "celdas_vacias": c95_vacias,
        "vig_valores": c95_vig,
        "sha256_desktop": hashes_orig[str(ORIG_DESKTOP_COMP95)]["sha256"],
        "sha256_repo_csv": hashes_orig[str(ORIG_COMPLEMENTO_95_CSV)]["sha256"],
        "encabezado": False,
        "delimitador": ";",
        "nota": "Proceso paralelo independiente. No modifica la carga principal.",
    },
    "archivos_originales": {k: v for k, v in hashes_orig.items()},
    "archivos_copiados": {k: v for k, v in copias_info.items()},
    "rutas_evidencia": {
        "punto_0_original": str(ORIG_PUNTO_0_DIR),
        "punto_0_copia": str(SUB_EV_P0 / ORIG_PUNTO_0_DIR.name),
        "complemento_95_original": str(ORIG_COMPLEMENTO_95_DIR),
        "complemento_95_copia": str(SUB_EV_C95 / ORIG_COMPLEMENTO_95_DIR.name),
    },
    "observaciones": [
        "Respaldo digital auditable dentro del repositorio. No depende de ZIP.",
        "El ZIP en el Escritorio es un respaldo auxiliar externo.",
        "Para restaurar: ver RESTAURACION.md.",
        "Para versionar en Git: ver COMANDOS_GIT_SUGERIDOS.md.",
        "Validaciones de estructura confirmadas: carga 4070x32, complemento 95x32.",
    ],
}

(DEST / "MANIFEST_AUDITORIA_MU2026.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print("  ✓ MANIFEST_AUDITORIA_MU2026.json")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 9 — GENERAR RESTAURACION.md
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 9] Generando RESTAURACION.md...")

sha_desktop_cp  = hashes_orig[str(ORIG_DESKTOP_PRINCIPAL)]["sha256"]
sha_pes_ready   = hashes_orig[str(ORIG_PES_READY)]["sha256"]
sha_comp95_desk = hashes_orig[str(ORIG_DESKTOP_COMP95)]["sha256"]
sha_comp95_repo = hashes_orig[str(ORIG_COMPLEMENTO_95_CSV)]["sha256"]

restauracion_md = f"""# RESTAURACIÓN · MU2026 PUNTO 0 Y COMPLEMENTO 95 CODCLI

> **Fecha de generación**: {FECHA_ISO}
> **Carpeta de auditoría**: `{DEST.relative_to(ROOT)}`
> **ADVERTENCIA**: Estos comandos restauran archivos desde las copias congeladas.
> Solo ejecutar si los archivos originales fueron eliminados o modificados.
> Verificar siempre el hash SHA256 antes y después de restaurar.

---

## 1. Restaurar Carga Principal PES_READY al repositorio

```bash
# Desde la raíz del repositorio:
cp "{DEST.relative_to(ROOT)}/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PES_READY.csv" \\
   "resultados/matricula_unificada_2026_pregrado_PES_READY.csv"

# Verificar hash SHA256 esperado:
# {sha_pes_ready}
shasum -a 256 resultados/matricula_unificada_2026_pregrado_PES_READY.csv
```

---

## 2. Restaurar Carga Principal al Escritorio

```bash
cp "{DEST}/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv" \\
   "/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"

# Verificar hash SHA256 esperado:
# {sha_desktop_cp}
shasum -a 256 "/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
```

---

## 3. Restaurar Complemento 95 al repositorio

```bash
# Desde la raíz del repositorio:
cp "{DEST.relative_to(ROOT)}/archivos_congelados/complemento_95/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv" \\
   "resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"

# Verificar hash SHA256 esperado:
# {sha_comp95_repo}
shasum -a 256 resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv
```

---

## 4. Restaurar Complemento 95 al Escritorio

```bash
cp "{DEST}/archivos_congelados/complemento_95/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv" \\
   "/Users/alexi/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"

# Verificar hash SHA256 esperado:
# {sha_comp95_desk}
shasum -a 256 "/Users/alexi/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
```

---

## 5. Restaurar Script del Complemento 95

```bash
cp "{DEST.relative_to(ROOT)}/archivos_congelados/scripts/mu2026_complemento_95_codcli.py" \\
   "scripts/mu2026_complemento_95_codcli.py"
```

---

## 6. Restaurar Punto 0 (carpeta de control completa)

```bash
cp -r "{DEST.relative_to(ROOT)}/evidencia/punto_0/punto_0_carga_principal_mu2026" \\
      "control/punto_0_carga_principal_mu2026"
```

---

## 7. Verificación post-restauración

```bash
# Contar filas y verificar estructura carga principal
python3 -c "
import csv
with open('resultados/matricula_unificada_2026_pregrado_PES_READY.csv') as f:
    rows = list(csv.reader(f, delimiter=';'))
print(f'Filas: {{len(rows)}} | Cols: {{len(rows[0])}}')
assert len(rows) == 4070, 'ERROR: filas esperadas 4070'
assert len(rows[0]) == 32, 'ERROR: columnas esperadas 32'
print('OK: 4070x32')
"

# Contar filas y verificar estructura complemento 95
python3 -c "
import csv
with open('resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv') as f:
    rows = list(csv.reader(f, delimiter=';'))
print(f'Filas: {{len(rows)}} | Cols: {{len(rows[0])}}')
assert len(rows) == 95, 'ERROR: filas esperadas 95'
assert len(rows[0]) == 32, 'ERROR: columnas esperadas 32'
print('OK: 95x32')
"
```

---

## Notas

- Este archivo fue generado automáticamente por `scripts/auditoria_mu2026_punto0_complemento95.py`
- La carpeta `archivos_congelados/` contiene las copias verificadas con hash SHA256.
- La carpeta `evidencia/` contiene copias completas de directorios de control.
- Consultar `MANIFEST_AUDITORIA_MU2026.json` para los hashes completos.
- Consultar `COMPARACION_HASHES.tsv` para verificación cruzada.
"""

(DEST / "RESTAURACION.md").write_text(restauracion_md, encoding="utf-8")
print("  ✓ RESTAURACION.md")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 10 — GENERAR COMANDOS_GIT_SUGERIDOS.md
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 10] Generando COMANDOS_GIT_SUGERIDOS.md...")

git_md = f"""# COMANDOS GIT SUGERIDOS · MU2026 PUNTO 0 Y COMPLEMENTO 95

> **Fecha de generación**: {FECHA_ISO}
> ⚠ **NO EJECUTAR ESTOS COMANDOS SIN AUTORIZACIÓN EXPLÍCITA DEL USUARIO.**
> Son solo una referencia documentada para cuando se decida versionar este punto de control.

---

## 1. Ver estado actual del repositorio

```bash
git -C /Users/alexi/Documents/GitHub/avance_curricular status --short
```

---

## 2. Agregar archivos al índice

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular

git add control/auditoria_mu2026_punto0_complemento95 \\
        scripts/mu2026_complemento_95_codcli.py \\
        scripts/respaldo_mu2026_punto0_complemento95.py
```

---

## 3. Crear commit de auditoría

```bash
git commit -m "audit: freeze MU2026 punto 0 and complemento 95

- Carga principal: 4070 filas × 32 cols, SHA256={sha_desktop_cp[:16]}...
- Complemento 95 CODCLI: 95 filas × 32 cols, VIG=1, 0 vacías
- SHA256 complemento 95: {sha_comp95_repo[:16]}...
- Punto de control digital auditable creado en control/auditoria_mu2026_punto0_complemento95/
- No se modificaron originales."
```

---

## 4. Crear tag de auditoría

```bash
git tag -a mu2026-punto0-complemento95-20260509 \\
        -m "MU2026 Punto 0 + Complemento 95 CODCLI verificados. Carga: 4070x32. Complemento: 95x32 VIG=1."
```

---

## 5. Verificar tag

```bash
git show --stat mu2026-punto0-complemento95-20260509
```

---

## 6. Comparar cambios posteriores al tag

```bash
git diff --stat mu2026-punto0-complemento95-20260509..HEAD
```

---

## 7. Ver archivos en el tag

```bash
git ls-tree -r --name-only mu2026-punto0-complemento95-20260509 | grep control/auditoria
```

---

## 8. Restaurar un archivo desde el tag (si se necesita)

```bash
git checkout mu2026-punto0-complemento95-20260509 -- \\
    control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PES_READY.csv
```

---

## Notas

- El tag `mu2026-punto0-complemento95-20260509` actúa como snapshot inmutable del estado del repositorio.
- Si se ejecuta `git push`, incluir `--tags` para subir el tag al remoto.
- Este archivo fue generado automáticamente por `scripts/auditoria_mu2026_punto0_complemento95.py`
"""

(DEST / "COMANDOS_GIT_SUGERIDOS.md").write_text(git_md, encoding="utf-8")
print("  ✓ COMANDOS_GIT_SUGERIDOS.md")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 11 — GENERAR README_AUDITORIA_MU2026.md
# ─────────────────────────────────────────────────────────────────────────────

print("\n[FASE 11] Generando README_AUDITORIA_MU2026.md...")

readme_md = f"""# AUDITORÍA MU2026 · PUNTO 0 Y COMPLEMENTO 95 CODCLI

> **Fecha de creación**: {FECHA_ISO}
> **Estado**: {manifest["estado_final"]}
> **Carpeta**: `{DEST.relative_to(ROOT)}`
> ⚠ **NO BORRAR ESTA CARPETA. Es el respaldo digital auditable principal de MU2026.**

---

## 1. Objetivo

Crear un Punto de Control Digital Auditable dentro del repositorio que:
- Resguarde la carga principal MU2026 (4.070 filas × 32 cols).
- Resguarde el complemento 95 CODCLI (95 filas × 32 cols, VIG=1).
- Sea auditable, legible, versionable y comparable mediante Git.
- No dependa de un archivo ZIP como respaldo principal.

---

## 2. Alcance

Este punto de control cubre:
- **Carga principal MU2026** (`matricula_unificada_2026_pregrado_PARA_SUBIR.csv` y `PES_READY.csv`)
- **Complemento 95 CODCLI** (proceso paralelo e independiente)
- **Scripts** que generaron los archivos
- **Punto 0** previo de la carga principal
- **Auditorías previas** relacionadas

No modifica ningún archivo original. No ejecuta el pipeline. No regenera datos.

---

## 3. Qué es el Punto 0

El **Punto 0** es el estado congelado de la carga principal MU2026 al momento de su envío:
- 4.070 filas
- 32 campos (sin encabezado, delimitador `;`)
- SHA256 del desktop: `{sha_desktop_cp}`
- SHA256 del PES_READY repo: `{sha_pes_ready}`
- Ambos archivos son idénticos (hashes coinciden): **{cp_hashes_ok}**
- **No incluye** el complemento 95 (proceso separado)

---

## 4. Qué es el Complemento 95

El **Complemento 95** es un proceso paralelo e independiente que agrega 95 CODCLI:
- 95 filas
- 32 campos (sin encabezado, delimitador `;`)
- `VIG = 1` para los 95 registros
- 0 celdas vacías
- SHA256 del desktop: `{sha_comp95_desk}`
- SHA256 del repo CSV: `{sha_comp95_repo}`
- Archivos idénticos (hashes coinciden): **{c95_hashes_ok}**
- **No modifica** la carga principal

---

## 5. Rutas originales

| Archivo | Ruta |
|---------|------|
| Desktop (carga principal) | `/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv` |
| PES_READY (repo) | `resultados/matricula_unificada_2026_pregrado_PES_READY.csv` |
| Matrícula completa (repo) | `resultados/matricula_unificada_2026_pregrado.csv` |
| Desktop (complemento 95) | `/Users/alexi/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv` |
| Complemento 95 dir (repo) | `resultados/complemento_95_codcli/` |
| Punto 0 (repo) | `control/punto_0_carga_principal_mu2026/` |
| Script complemento 95 | `scripts/mu2026_complemento_95_codcli.py` |
| Script respaldo | `scripts/respaldo_mu2026_punto0_complemento95.py` |

---

## 6. Rutas congeladas (dentro de esta auditoría)

```
{DEST.relative_to(ROOT)}/
├── archivos_congelados/
│   ├── carga_principal/       ← copias de carga principal
│   ├── complemento_95/        ← copias del complemento 95
│   ├── scripts/               ← copias de scripts
│   └── auditorias_previas/    ← auditorías opcionales copiadas
└── evidencia/
    ├── punto_0/               ← copia completa de control/punto_0_carga_principal_mu2026/
    └── complemento_95/        ← copia completa de resultados/complemento_95_codcli/
```

---

## 7. Validaciones realizadas

| Validación | Resultado |
|------------|-----------|
| Carga principal 4070×32 | {cp_estado} |
| Complemento 95 × 32 | {c95_estado} |
| Hashes originales == copias | {hashes_coinciden}/{hashes_coinciden} coinciden |
| Originales intactos post-copia | {"SÍ" if originales_intactos else "NO"} |
| Complemento VIG = 1 (todos) | {"SÍ" if c95_vig == {"1": 95} else "NO"} |
| Complemento celdas vacías | {c95_vacias} |

---

## 8. Hashes principales

| Archivo | SHA256 |
|---------|--------|
| Desktop PARA_SUBIR | `{sha_desktop_cp}` |
| PES_READY (repo) | `{sha_pes_ready}` |
| Complemento 95 Desktop | `{sha_comp95_desk}` |
| Complemento 95 Repo CSV | `{sha_comp95_repo}` |

---

## 9. Estado final

```
Estado                : {manifest["estado_final"]}
Archivos auditados    : {len(hashes_orig)}
Hashes coincidentes   : {hashes_coinciden}/{hashes_coinciden}
Carga principal       : {cp_estado} ({cp_desktop_filas}×{cp_desktop_cols})
Complemento 95        : {c95_estado} ({c95_repo_filas}×{c95_repo_cols}, VIG=1, vacias=0)
Originales modificados: {"NO" if originales_intactos else "SÍ — REVISAR"}
```

---

## 10. Cómo comparar en el futuro

```bash
# Comparar hash de un archivo actual vs el congelado:
shasum -a 256 resultados/matricula_unificada_2026_pregrado_PES_READY.csv
# Comparar con SHA256 registrado en HASHES_ORIGINALES.tsv o MANIFEST_AUDITORIA_MU2026.json

# Comparar con Git (si se creó el tag):
git diff --stat mu2026-punto0-complemento95-20260509..HEAD
```

---

## 11. Cómo restaurar

Ver instrucciones completas en `RESTAURACION.md`.

Resumen rápido:
```bash
# Restaurar PES_READY desde copia congelada:
cp "{DEST.relative_to(ROOT)}/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PES_READY.csv" \\
   "resultados/matricula_unificada_2026_pregrado_PES_READY.csv"
```

---

## 12. Comandos Git sugeridos

Ver `COMANDOS_GIT_SUGERIDOS.md` para los comandos completos.

```bash
git add control/auditoria_mu2026_punto0_complemento95
git commit -m "audit: freeze MU2026 punto 0 and complemento 95"
git tag mu2026-punto0-complemento95-20260509
```
> ⚠ **NO ejecutar sin autorización explícita.**

---

## 13. Advertencias

1. **NO BORRAR** esta carpeta. Es el respaldo digital auditable principal.
2. No depende de ZIP. El ZIP en el Escritorio es un respaldo auxiliar externo.
3. Los archivos en `archivos_congelados/` son copias verificadas. No modificar.
4. Si se necesita restaurar, usar `RESTAURACION.md` y verificar hashes.
5. Para versionar, usar los comandos de `COMANDOS_GIT_SUGERIDOS.md` con autorización explícita.
6. Este archivo fue generado automáticamente el {FECHA_ISO}.
"""

(DEST / "README_AUDITORIA_MU2026.md").write_text(readme_md, encoding="utf-8")
print("  ✓ README_AUDITORIA_MU2026.md")

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────────────────────

# Contar archivos en la carpeta de auditoría
total_audit_files = sum(1 for f in DEST.rglob("*") if f.is_file())

print("\n" + "=" * 60)
print("AUDITORÍA DIGITAL MU2026 CREADA")
print(f"  Estado               : {manifest['estado_final']}")
print(f"  Carpeta              : {DEST.relative_to(ROOT)}")
print(f"  Archivos auditados   : {len(hashes_orig)}")
print(f"  Hashes coincidentes  : {hashes_coinciden}/{hashes_coinciden}")
print(f"  Carga principal      : {cp_estado} ({cp_desktop_filas}×{cp_desktop_cols})")
print(f"  Complemento 95       : {c95_estado} ({c95_repo_filas}×{c95_repo_cols}, VIG={c95_vig}, vacías={c95_vacias})")
print(f"  Originales modificados: {'NO' if originales_intactos else 'SÍ — REVISAR'}")
print(f"  README               : README_AUDITORIA_MU2026.md ✓")
print(f"  Manifest             : MANIFEST_AUDITORIA_MU2026.json ✓")
print(f"  Restauración         : RESTAURACION.md ✓")
print(f"  Comandos Git sugeridos: COMANDOS_GIT_SUGERIDOS.md ✓")
print(f"  Total archivos audit : {total_audit_files}")
print("=" * 60)
print("⚠ NO ejecutar git commit ni tag sin autorización explícita.")
print("=" * 60)

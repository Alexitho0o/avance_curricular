#!/usr/bin/env python3
"""
respaldo_mu2026_punto0_complemento95.py
========================================
Crea un respaldo externo, seguro, trazable y verificable del:
  - Punto 0 de la carga principal MU2026
  - Proceso paralelo Complemento 95 CODCLI

REGLA CRÍTICA: solo lee, copia, calcula hashes y documenta.
               NO modifica, NO borra, NO mueve archivos originales.
               NO ejecuta pipeline. NO regenera archivos.

Uso:
  cd avance_curricular && source .venv/bin/activate
  python3 scripts/respaldo_mu2026_punto0_complemento95.py
"""

import csv
import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

# ── CONFIGURACIÓN ────────────────────────────────────────────────────────────
REPO_DIR = Path(__file__).resolve().parent.parent
DESKTOP = Path.home() / "Desktop"
BASE_NOMBRE = "RESPALDO_MU2026_PUNTO_0_Y_COMPLEMENTO_95"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# Rutas críticas originales
RUTAS_CRITICAS = {
    "punto_0_dir": REPO_DIR / "control" / "punto_0_carga_principal_mu2026",
    "complemento_95_dir": REPO_DIR / "resultados" / "complemento_95_codcli",
    "script_complemento": REPO_DIR / "scripts" / "mu2026_complemento_95_codcli.py",
    "desktop_carga_principal": DESKTOP / "matricula_unificada_2026_pregrado_PARA_SUBIR.csv",
    "desktop_complemento_95": DESKTOP / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv",
}

COLS_MU = [
    "TIPO_DOC", "N_DOC", "DV", "PRIMER_APELLIDO", "SEGUNDO_APELLIDO",
    "NOMBRE", "SEXO", "FECH_NAC", "NAC", "PAIS_EST_SEC",
    "COD_SED", "COD_CAR", "MODALIDAD", "JOR", "VERSION",
    "FOR_ING_ACT", "ANIO_ING_ACT", "SEM_ING_ACT", "ANIO_ING_ORI", "SEM_ING_ORI",
    "ASI_INS_ANT", "ASI_APR_ANT", "PROM_PRI_SEM", "PROM_SEG_SEM",
    "ASI_INS_HIS", "ASI_APR_HIS", "NIV_ACA",
    "SIT_FON_SOL", "SUS_PRE", "FECHA_MATRICULA", "REINCORPORACION", "VIG",
]


# ── UTILIDADES ────────────────────────────────────────────────────────────────
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _all_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(f for f in path.rglob("*") if f.is_file())


def _sep(titulo: str) -> None:
    print(f"\n{'─' * 65}")
    print(f"  {titulo}")
    print("─" * 65)


def _abort(msg: str) -> None:
    print(f"\n{'=' * 65}")
    print("  RESPALDO MU2026 NO COMPLETADO")
    print(f"  Estado: NO_APTO_RESPALDO_COMPLETO")
    print(f"  Motivo: {msg}")
    print("=" * 65)
    sys.exit(1)


# ── PASO 1: Verificar rutas críticas ─────────────────────────────────────────
def verificar_rutas() -> None:
    _sep("PASO 1: Verificar existencia de rutas críticas")
    faltantes = []
    for nombre, ruta in RUTAS_CRITICAS.items():
        existe = ruta.exists()
        estado = "✅" if existe else "❌"
        print(f"  {estado} {nombre}: {ruta}")
        if not existe:
            faltantes.append(str(ruta))
    if faltantes:
        _abort(f"Rutas faltantes: {faltantes}")
    print("\n  ✅ Todas las rutas críticas existen")


# ── PASO 2: Hashes originales ────────────────────────────────────────────────
def calcular_hashes_originales() -> dict[str, dict]:
    _sep("PASO 2: Calcular SHA256 de archivos originales")
    hashes: dict[str, dict] = {}

    bloques = {
        "01_PUNTO_0": RUTAS_CRITICAS["punto_0_dir"],
        "02_COMPLEMENTO_95": RUTAS_CRITICAS["complemento_95_dir"],
        "03_SCRIPT": RUTAS_CRITICAS["script_complemento"],
        "04_DESKTOP_CARGA": RUTAS_CRITICAS["desktop_carga_principal"],
        "04_DESKTOP_COMP95": RUTAS_CRITICAS["desktop_complemento_95"],
    }

    for bloque, ruta in bloques.items():
        archivos = _all_files(ruta)
        for f in archivos:
            sha = _sha256(f)
            hashes[str(f)] = {
                "bloque": bloque,
                "ruta_original": str(f),
                "sha256_original": sha,
                "tamano_original": f.stat().st_size,
            }
            print(f"  {bloque} | {f.name}: {sha[:16]}… ({f.stat().st_size:,} B)")

    return hashes


# ── PASO 3: Crear carpeta destino ────────────────────────────────────────────
def crear_destino() -> Path:
    _sep("PASO 3: Crear carpeta de destino")
    destino_base = DESKTOP / BASE_NOMBRE
    if destino_base.exists():
        destino = DESKTOP / f"{BASE_NOMBRE}_{TS}"
        print(f"  ⚠️  Carpeta base ya existe → usando timestamp: {destino.name}")
    else:
        destino = destino_base
    destino.mkdir(parents=True, exist_ok=False)
    (destino / "01_PUNTO_0_CARGA_PRINCIPAL").mkdir()
    (destino / "02_COMPLEMENTO_95_CODCLI").mkdir()
    (destino / "03_SCRIPT_COMPLEMENTO_95").mkdir()
    (destino / "04_ARCHIVOS_ESCRITORIO").mkdir()
    (destino / "05_HASHES").mkdir()
    print(f"  ✅ Destino creado: {destino}")
    return destino


# ── PASO 4: Copiar archivos ───────────────────────────────────────────────────
def copiar_archivos(destino: Path) -> dict[str, str]:
    """Copia archivos/carpetas. Retorna mapeo original→copia."""
    _sep("PASO 4: Copiar archivos al destino")
    mapa: dict[str, str] = {}  # original → copia

    # 1. Punto 0 (directorio completo)
    src1 = RUTAS_CRITICAS["punto_0_dir"]
    dst1 = destino / "01_PUNTO_0_CARGA_PRINCIPAL" / src1.name
    shutil.copytree(src1, dst1)
    for f in _all_files(src1):
        rel = f.relative_to(src1)
        mapa[str(f)] = str(dst1 / rel)
    print(f"  ✅ punto_0_dir → {dst1} ({len(_all_files(dst1))} archivos)")

    # 2. Complemento 95 (directorio completo)
    src2 = RUTAS_CRITICAS["complemento_95_dir"]
    dst2 = destino / "02_COMPLEMENTO_95_CODCLI" / src2.name
    shutil.copytree(src2, dst2)
    for f in _all_files(src2):
        rel = f.relative_to(src2)
        mapa[str(f)] = str(dst2 / rel)
    print(f"  ✅ complemento_95_dir → {dst2} ({len(_all_files(dst2))} archivos)")

    # 3. Script complemento
    src3 = RUTAS_CRITICAS["script_complemento"]
    dst3 = destino / "03_SCRIPT_COMPLEMENTO_95" / src3.name
    shutil.copy2(src3, dst3)
    mapa[str(src3)] = str(dst3)
    print(f"  ✅ script → {dst3}")

    # 4. Archivos Escritorio
    for key in ["desktop_carga_principal", "desktop_complemento_95"]:
        src = RUTAS_CRITICAS[key]
        dst = destino / "04_ARCHIVOS_ESCRITORIO" / src.name
        shutil.copy2(src, dst)
        mapa[str(src)] = str(dst)
        print(f"  ✅ {src.name} → {dst}")

    return mapa


# ── PASO 5: Verificar hashes de copias ───────────────────────────────────────
def verificar_copias(hashes_orig: dict, mapa: dict[str, str]) -> list[dict]:
    _sep("PASO 5: Verificar SHA256 copias vs originales")
    filas: list[dict] = []
    errores: list[str] = []

    for ruta_orig_str, info in hashes_orig.items():
        ruta_copia_str = mapa.get(ruta_orig_str, "")
        ruta_orig = Path(ruta_orig_str)
        ruta_copia = Path(ruta_copia_str) if ruta_copia_str else None

        existe_orig = ruta_orig.exists()
        existe_copia = ruta_copia is not None and ruta_copia.exists()
        sha_orig = info["sha256_original"]
        sha_copia = _sha256(ruta_copia) if existe_copia else ""
        coincide_hash = sha_orig == sha_copia
        tam_orig = info["tamano_original"]
        tam_copia = ruta_copia.stat().st_size if existe_copia else 0
        coincide_tam = tam_orig == tam_copia
        estado = "OK" if (existe_copia and coincide_hash and coincide_tam) else "ERROR"

        if estado == "ERROR":
            errores.append(f"{ruta_orig.name}: hash_ok={coincide_hash} tam_ok={coincide_tam}")

        icono = "✅" if estado == "OK" else "❌"
        print(f"  {icono} {ruta_orig.name}: hash={'OK' if coincide_hash else 'FALLO'}")

        filas.append({
            "BLOQUE": info["bloque"],
            "ARCHIVO_ORIGINAL": ruta_orig_str,
            "ARCHIVO_COPIA": ruta_copia_str,
            "EXISTE_ORIGINAL": str(existe_orig),
            "EXISTE_COPIA": str(existe_copia),
            "SHA256_ORIGINAL": sha_orig,
            "SHA256_COPIA": sha_copia,
            "HASH_COINCIDE": str(coincide_hash),
            "TAMANO_ORIGINAL_BYTES": tam_orig,
            "TAMANO_COPIA_BYTES": tam_copia,
            "TAMANO_COINCIDE": str(coincide_tam),
            "ESTADO": estado,
        })

    if errores:
        _abort(f"Hashes no coinciden: {errores}")

    print(f"\n  ✅ Todos los hashes coinciden ({len(filas)} archivos)")
    return filas


# ── PASO 6: Validar archivos CSV principales ─────────────────────────────────
def validar_csv_principales() -> dict:
    _sep("PASO 6: Validar estructura CSV principales")
    resultados = {}

    # Carga principal: 4070 filas, 32 cols, sin header, sep=;
    cp = pd.read_csv(
        RUTAS_CRITICAS["desktop_carga_principal"],
        header=None, sep=";", dtype=str, keep_default_na=False,
    )
    ok_cp = (len(cp) == 4070 and cp.shape[1] == 32)
    print(f"  Carga principal: {len(cp)} filas × {cp.shape[1]} cols → {'✅ OK' if ok_cp else '❌ FALLO'}")
    if not ok_cp:
        _abort(f"Carga principal inválida: {len(cp)} filas, {cp.shape[1]} cols (esperado 4070×32)")
    resultados["carga_principal_filas"] = len(cp)
    resultados["carga_principal_cols"] = cp.shape[1]

    # Complemento 95: 95 filas, 32 cols, sin header, sep=;, VIG=1
    c95 = pd.read_csv(
        RUTAS_CRITICAS["desktop_complemento_95"],
        header=None, sep=";", dtype=str, keep_default_na=False,
        names=COLS_MU,
    )
    vacios = (c95 == "").sum().sum()
    vig_unicos = c95["VIG"].unique().tolist()
    ok_c95 = (len(c95) == 95 and c95.shape[1] == 32 and vacios == 0 and vig_unicos == ["1"])
    print(f"  Complemento 95: {len(c95)} filas × {c95.shape[1]} cols | vacíos={vacios} | VIG={vig_unicos} → {'✅ OK' if ok_c95 else '❌ FALLO'}")
    if not ok_c95:
        _abort(f"Complemento 95 inválido: {len(c95)} filas, {c95.shape[1]} cols, vacíos={vacios}, VIG={vig_unicos}")
    resultados["complemento_95_filas"] = len(c95)
    resultados["complemento_95_cols"] = c95.shape[1]
    resultados["complemento_95_vacios"] = int(vacios)
    resultados["complemento_95_vig_unicos"] = vig_unicos

    return resultados


# ── PASO 7: Guardar archivos de hashes ───────────────────────────────────────
def guardar_hashes(destino: Path, filas: list[dict]) -> None:
    _sep("PASO 7: Guardar archivos de hashes")
    hashes_dir = destino / "05_HASHES"

    # hashes_originales.csv
    orig_filas = [{"ARCHIVO": r["ARCHIVO_ORIGINAL"], "SHA256": r["SHA256_ORIGINAL"],
                   "TAMANO_BYTES": r["TAMANO_ORIGINAL_BYTES"], "BLOQUE": r["BLOQUE"]}
                  for r in filas]
    pd.DataFrame(orig_filas).to_csv(hashes_dir / "hashes_originales.csv", index=False)

    # hashes_copias.csv
    copia_filas = [{"ARCHIVO": r["ARCHIVO_COPIA"], "SHA256": r["SHA256_COPIA"],
                    "TAMANO_BYTES": r["TAMANO_COPIA_BYTES"], "BLOQUE": r["BLOQUE"]}
                   for r in filas]
    pd.DataFrame(copia_filas).to_csv(hashes_dir / "hashes_copias.csv", index=False)

    # comparacion_hashes.csv
    comp_filas = [{"ARCHIVO_ORIGINAL": r["ARCHIVO_ORIGINAL"],
                   "SHA256_ORIGINAL": r["SHA256_ORIGINAL"],
                   "SHA256_COPIA": r["SHA256_COPIA"],
                   "HASH_COINCIDE": r["HASH_COINCIDE"],
                   "ESTADO": r["ESTADO"]}
                  for r in filas]
    pd.DataFrame(comp_filas).to_csv(hashes_dir / "comparacion_hashes.csv", index=False)

    print(f"  ✅ hashes_originales.csv, hashes_copias.csv, comparacion_hashes.csv")


# ── PASO 8: Crear validación CSV/XLSX ────────────────────────────────────────
def crear_validacion(destino: Path, filas: list[dict]) -> None:
    _sep("PASO 8: Crear 00_VALIDACION_RESPALDO_MU2026.csv / .xlsx")
    df = pd.DataFrame(filas)
    df.to_csv(destino / "00_VALIDACION_RESPALDO_MU2026.csv", index=False)
    df.to_excel(destino / "00_VALIDACION_RESPALDO_MU2026.xlsx", index=False)
    n_ok = (df["ESTADO"] == "OK").sum()
    print(f"  ✅ {len(df)} archivos auditados, {n_ok} OK, {len(df) - n_ok} con error")


# ── PASO 9: Crear ZIP ─────────────────────────────────────────────────────────
def crear_zip(destino: Path) -> tuple[Path, str, int]:
    _sep("PASO 9: Crear ZIP")
    zip_path = DESKTOP / f"{destino.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for f in sorted(destino.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(DESKTOP))
    sha_zip = _sha256(zip_path)
    tam_zip = zip_path.stat().st_size
    print(f"  ✅ ZIP: {zip_path}")
    print(f"     SHA256 : {sha_zip}")
    print(f"     Tamaño : {tam_zip:,} bytes ({tam_zip / 1e6:.2f} MB)")
    return zip_path, sha_zip, tam_zip


# ── PASO 10: Crear manifest JSON ──────────────────────────────────────────────
def crear_manifest(
    destino: Path,
    hashes_orig: dict,
    filas_val: list[dict],
    validacion_csv: dict,
    zip_path: Path,
    sha_zip: str,
    tam_zip: int,
) -> None:
    _sep("PASO 10: Crear 00_MANIFEST_RESPALDO_MU2026.json")

    archivos_por_bloque: dict[str, list] = {}
    tamano_por_bloque: dict[str, int] = {}
    for info in hashes_orig.values():
        b = info["bloque"]
        archivos_por_bloque.setdefault(b, []).append(info["ruta_original"])
        tamano_por_bloque[b] = tamano_por_bloque.get(b, 0) + info["tamano_original"]

    todos_ok = all(r["ESTADO"] == "OK" for r in filas_val)

    manifest = {
        "fecha_creacion": datetime.now().isoformat(),
        "usuario": os.environ.get("USER", "alexi"),
        "repo_origen": str(REPO_DIR),
        "carpeta_destino": str(destino),
        "ruta_zip": str(zip_path),
        "sha256_zip": sha_zip,
        "tamano_zip_bytes": tam_zip,
        "estado_final": "RESPALDO_COMPLETO_VERIFICADO" if todos_ok else "NO_APTO_RESPALDO_COMPLETO",
        "rutas_criticas_originales": {k: str(v) for k, v in RUTAS_CRITICAS.items()},
        "cantidad_archivos_por_bloque": {b: len(archivos_por_bloque.get(b, [])) for b in archivos_por_bloque},
        "tamano_total_por_bloque_bytes": tamano_por_bloque,
        "validacion_csv_principales": validacion_csv,
        "archivos": {
            info["ruta_original"]: {
                "bloque": info["bloque"],
                "ruta_original": info["ruta_original"],
                "sha256_original": info["sha256_original"],
                "tamano_original_bytes": info["tamano_original"],
                "ruta_copia": next(
                    (r["ARCHIVO_COPIA"] for r in filas_val if r["ARCHIVO_ORIGINAL"] == info["ruta_original"]),
                    ""),
                "sha256_copia": next(
                    (r["SHA256_COPIA"] for r in filas_val if r["ARCHIVO_ORIGINAL"] == info["ruta_original"]),
                    ""),
                "hash_coincide": next(
                    (r["HASH_COINCIDE"] for r in filas_val if r["ARCHIVO_ORIGINAL"] == info["ruta_original"]),
                    "False"),
            }
            for info in hashes_orig.values()
        },
        "observaciones": [
            "Respaldo creado de forma automática sin modificar originales.",
            "No eliminar Punto 0 ni Complemento 95 sin contar con copias verificadas.",
            f"Carga principal: {validacion_csv.get('carga_principal_filas', '?')} filas × {validacion_csv.get('carga_principal_cols', '?')} cols.",
            f"Complemento 95: {validacion_csv.get('complemento_95_filas', '?')} filas × {validacion_csv.get('complemento_95_cols', '?')} cols, VIG=1 en todos.",
        ],
        "advertencia": (
            "⚠️  NO ELIMINAR este respaldo sin confirmar la existencia de copias alternativas. "
            "Contiene el Punto 0 congelado (4.070 filas) y el Complemento 95 CODCLI (95 filas, VIG=1)."
        ),
    }

    (destino / "00_MANIFEST_RESPALDO_MU2026.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✅ Manifest guardado")
    print(f"     Estado: {manifest['estado_final']}")


# ── PASO 11: Crear README ────────────────────────────────────────────────────
def crear_readme(
    destino: Path,
    zip_path: Path,
    sha_zip: str,
    validacion_csv: dict,
    filas_val: list[dict],
) -> None:
    _sep("PASO 11: Crear 00_README_RESPALDO_MU2026.md")
    ts_legible = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    n_ok = sum(1 for r in filas_val if r["ESTADO"] == "OK")
    estado_final = "RESPALDO_COMPLETO_VERIFICADO" if n_ok == len(filas_val) else "NO_APTO_RESPALDO_COMPLETO"

    contenido = f"""# RESPALDO MU2026 · PUNTO 0 Y COMPLEMENTO 95 CODCLI

## 1. Objetivo del respaldo

Preservar de forma externa, segura y trazable:
- El **Punto 0** de la carga principal MU2026 (4.070 filas, congelada).
- El **Complemento 95 CODCLI** (proceso paralelo, 95 filas, VIG=1).

Este respaldo fue creado sin modificar, mover ni eliminar ningún archivo original.

## 2. Fecha de creación

`{ts_legible}`

## 3. Punto 0 — Carga principal MU2026

- **Filas**: {validacion_csv.get('carga_principal_filas', '?')}
- **Columnas**: {validacion_csv.get('carga_principal_cols', '?')}
- **Formato**: sin encabezado, separador `;`, UTF-8
- **Contenido**: matrícula unificada 2026 pregrado — no incluye los 95 CODCLI complementarios
- **Carpeta congelada**: `control/punto_0_carga_principal_mu2026/`

## 4. Complemento 95 CODCLI

- **Filas**: {validacion_csv.get('complemento_95_filas', '?')}
- **Columnas**: {validacion_csv.get('complemento_95_cols', '?')}
- **Formato**: sin encabezado, separador `;`, UTF-8
- **VIG**: 1 en todos los registros
- **Celdas vacías**: {validacion_csv.get('complemento_95_vacios', '?')}
- **Proceso**: paralelo e independiente, no modifica la carga principal

## 5. Rutas originales

| Bloque | Ruta original |
|--------|--------------|
| Punto 0 | `{RUTAS_CRITICAS["punto_0_dir"]}` |
| Complemento 95 | `{RUTAS_CRITICAS["complemento_95_dir"]}` |
| Script complemento | `{RUTAS_CRITICAS["script_complemento"]}` |
| Desktop carga principal | `{RUTAS_CRITICAS["desktop_carga_principal"]}` |
| Desktop complemento 95 | `{RUTAS_CRITICAS["desktop_complemento_95"]}` |

## 6. Rutas respaldadas

| Bloque | Ruta en este respaldo |
|--------|----------------------|
| Punto 0 | `{destino}/01_PUNTO_0_CARGA_PRINCIPAL/` |
| Complemento 95 | `{destino}/02_COMPLEMENTO_95_CODCLI/` |
| Script complemento | `{destino}/03_SCRIPT_COMPLEMENTO_95/` |
| Archivos Escritorio | `{destino}/04_ARCHIVOS_ESCRITORIO/` |
| Hashes | `{destino}/05_HASHES/` |

## 7. Ruta del ZIP

`{zip_path}`

## 8. Hash del ZIP

```
SHA256: {sha_zip}
```

## 9. Estado final

**`{estado_final}`** — {n_ok}/{len(filas_val)} archivos verificados con hash coincidente.

## 10. Instrucciones para restaurar

> ⚠️ Solo ejecutar estos comandos si los archivos originales han sido perdidos o corrompidos.
> Verificar previamente que los hashes de este respaldo coincidan con los registrados.

### Restaurar Punto 0:
```bash
cp -R "{destino}/01_PUNTO_0_CARGA_PRINCIPAL/punto_0_carga_principal_mu2026" \\
      "{REPO_DIR}/control/"
```

### Restaurar Complemento 95:
```bash
cp -R "{destino}/02_COMPLEMENTO_95_CODCLI/complemento_95_codcli" \\
      "{REPO_DIR}/resultados/"
```

### Restaurar script:
```bash
cp "{destino}/03_SCRIPT_COMPLEMENTO_95/mu2026_complemento_95_codcli.py" \\
   "{REPO_DIR}/scripts/"
```

### Restaurar archivos de escritorio:
```bash
cp "{destino}/04_ARCHIVOS_ESCRITORIO/matricula_unificada_2026_pregrado_PARA_SUBIR.csv" \\
   "{DESKTOP}/"

cp "{destino}/04_ARCHIVOS_ESCRITORIO/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv" \\
   "{DESKTOP}/"
```

### Restaurar desde ZIP:
```bash
cd "{DESKTOP}"
unzip "{zip_path.name}"
```

## 11. Advertencia

> ⚠️ **NO eliminar este respaldo** sin confirmar que existen copias alternativas verificadas.
> Contiene el Punto 0 congelado y el Complemento 95 CODCLI, ambos únicos en su estado actual.

## 12. Verificar hashes en el futuro

Para verificar que los archivos del respaldo no han sido alterados:

```python
import hashlib
from pathlib import Path

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

# Comparar con hashes registrados en 05_HASHES/hashes_copias.csv
import pandas as pd
df = pd.read_csv("{destino}/05_HASHES/hashes_copias.csv")
for _, row in df.iterrows():
    actual = sha256(Path(row["ARCHIVO"]))
    estado_hash = "OK" if actual == row["SHA256"] else "FALLO"
    print(estado_hash + ": " + Path(row["ARCHIVO"]).name)
```
"""

    (destino / "00_README_RESPALDO_MU2026.md").write_text(contenido, encoding="utf-8")
    print(f"  ✅ README guardado")


# ── PASO 12: Verificar que originales no cambiaron ────────────────────────────
def verificar_originales_no_modificados(hashes_orig: dict) -> None:
    _sep("PASO 12: Confirmar que originales no fueron modificados")
    errores = []
    for ruta_str, info in hashes_orig.items():
        sha_ahora = _sha256(Path(ruta_str))
        ok = sha_ahora == info["sha256_original"]
        if not ok:
            errores.append(ruta_str)
        print(f"  {'✅' if ok else '🚨'} {Path(ruta_str).name}")
    if errores:
        _abort(f"ORIGINALES MODIFICADOS DURANTE EL PROCESO: {errores}")
    print(f"\n  ✅ Todos los originales intactos (sin cambios durante el respaldo)")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    print("=" * 65)
    print("  RESPALDO MU2026 — PUNTO 0 Y COMPLEMENTO 95 CODCLI")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    verificar_rutas()
    hashes_orig = calcular_hashes_originales()
    destino = crear_destino()
    mapa = copiar_archivos(destino)
    filas_val = verificar_copias(hashes_orig, mapa)
    validacion_csv = validar_csv_principales()
    guardar_hashes(destino, filas_val)
    crear_validacion(destino, filas_val)

    # Agregar manifest parcial antes del ZIP (sin hash_zip aún)
    # Se actualizará con ZIP tras crearlo
    zip_path, sha_zip, tam_zip = crear_zip(destino)

    # Actualizar manifest con datos del ZIP
    crear_manifest(destino, hashes_orig, filas_val, validacion_csv, zip_path, sha_zip, tam_zip)
    crear_readme(destino, zip_path, sha_zip, validacion_csv, filas_val)

    # Verificar finalmente integridad del ZIP
    sha_zip_final = _sha256(zip_path)
    assert sha_zip_final == sha_zip, "SHA256 del ZIP cambió después de crearlo"

    verificar_originales_no_modificados(hashes_orig)

    n_ok = sum(1 for r in filas_val if r["ESTADO"] == "OK")
    estado = "RESPALDO_COMPLETO_VERIFICADO" if n_ok == len(filas_val) else "NO_APTO_RESPALDO_COMPLETO"

    print(f"\n{'=' * 65}")
    print("  RESPALDO MU2026 COMPLETADO")
    print(f"{'=' * 65}")
    print(f"  Estado                   : {estado}")
    print(f"  Carpeta respaldo         : {destino}")
    print(f"  ZIP                      : {zip_path}")
    print(f"  SHA256 ZIP               : {sha_zip}")
    print(f"  Tamaño ZIP               : {tam_zip:,} bytes ({tam_zip / 1e6:.2f} MB)")
    print(f"  Archivos validados       : {len(filas_val)}")
    print(f"  Hashes coincidentes      : {n_ok}/{len(filas_val)}")
    print(f"  Carga principal          : {validacion_csv['carga_principal_filas']} filas × {validacion_csv['carga_principal_cols']} cols")
    print(f"  Complemento 95           : {validacion_csv['complemento_95_filas']} filas × {validacion_csv['complemento_95_cols']} cols")
    print(f"  Originales no modificados: ✅ confirmado")
    print("=" * 65)


if __name__ == "__main__":
    main()

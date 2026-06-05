from pathlib import Path
from datetime import datetime
import subprocess
import sys
import csv
import hashlib
import json

ROOT = Path("/Users/alexi/Documents/GitHub/avance_curricular")
MOD = ROOT / "personal_academico_2026"

errores = []
advertencias = []
oks = []

def ok(msg):
    oks.append(msg)
    print(f"✅ {msg}")

def warn(msg):
    advertencias.append(msg)
    print(f"⚠️  {msg}")

def err(msg):
    errores.append(msg)
    print(f"❌ {msg}")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_delimited(path, delimiter):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f, delimiter=delimiter))

def check_exists(path, label, required=True):
    if path.exists():
        ok(f"Existe {label}: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return True
    if required:
        err(f"No existe {label}: {path}")
    else:
        warn(f"No existe {label}: {path}")
    return False

def run_cmd(args, label, required=False):
    print(f"\n▶ {label}")
    print("  " + " ".join(map(str, args)))
    r = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if r.stdout.strip():
        print(r.stdout[-5000:])
    if r.stderr.strip():
        print(r.stderr[-3000:])
    if r.returncode == 0:
        ok(label)
    else:
        if required:
            err(f"Falló: {label}")
        else:
            warn(f"Falló o no disponible: {label}")
    return r

print("=" * 100)
print("VERIFICACIÓN END TO END — PERSONAL ACADÉMICO SIES 2026")
print("=" * 100)
print("Fecha/hora:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("Repo:", ROOT)
print("Módulo:", MOD)
print("Python:", sys.executable)
print("=" * 100)

print("\n[1] Git")
run_cmd(["git", "branch", "--show-current"], "Rama actual", required=False)
run_cmd(["git", "status", "--short"], "Estado git corto", required=False)

print("\n[2] Estructura esperada del módulo")
check_exists(MOD, "módulo", True)

for rel in [
    "README.md",
    "INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md",
    "docs",
    "insumos",
    "insumos/preliminares",
    "catalogos",
    "scripts",
    "tests",
    "tests/fixtures",
    "resultados",
    "auditorias",
    "auditorias/base_preliminar",
    "bitacoras",
    "bitacoras/base_preliminar",
    "data",
    "data/base_general",
    "data/base_general/backups",
]:
    check_exists(MOD / rel, rel, required=False)

print("\n[3] Archivos normativos oficiales")
oficial_en = MOD / "insumos" / "20260421_57181_20260420_Estructura_Personal_Académico_en_Institución_2026.csv"
oficial_fuera = MOD / "insumos" / "20260421_84406_20260420_Estructura_Personal_Académico_Fuera_Institución_2026.csv"
instructivo = MOD / "insumos" / "Personal Académico SIES - Instructivo 2026.txt"

if check_exists(oficial_en, "estructura oficial en institución", False):
    try:
        rows = read_delimited(oficial_en, ";")
        header = rows[0] if rows else []
        print("Filas:", len(rows), "| Columnas con ;:", len(header))
        print("Primera columna:", header[0] if header else "")
        print("Última columna:", header[-1] if header else "")
        print("SHA256:", sha256(oficial_en))
        if len(header) == 34 and header[0] == "TIPO_DOCUMENTO" and header[-1] == "VIGENCIA":
            ok("Estructura EN INSTITUCIÓN coincide con 34 columnas oficiales.")
        else:
            err("Estructura EN INSTITUCIÓN no coincide con 34 columnas oficiales.")
        rows_comma = read_delimited(oficial_en, ",")
        if rows_comma and len(rows_comma[0]) == 1:
            ok("Confirmada tensión: estructura observada usa ;, aunque instructivo menciona coma.")
        else:
            warn("La lectura con coma no dio una sola columna; revisar delimitador.")
    except Exception as e:
        err(f"No se pudo leer estructura EN INSTITUCIÓN: {e}")

if check_exists(oficial_fuera, "estructura oficial fuera institución", False):
    try:
        rows = read_delimited(oficial_fuera, ";")
        header = rows[0] if rows else []
        print("Filas:", len(rows), "| Columnas con ;:", len(header))
        print("Primera columna:", header[0] if header else "")
        print("Última columna:", header[-1] if header else "")
        print("SHA256:", sha256(oficial_fuera))
        if len(header) == 27 and header[0] == "TIPO_DOCUMENTO" and header[-1] == "VIGENCIA":
            ok("Estructura FUERA INSTITUCIÓN coincide con 27 columnas oficiales.")
        else:
            err("Estructura FUERA INSTITUCIÓN no coincide con 27 columnas oficiales.")
    except Exception as e:
        err(f"No se pudo leer estructura FUERA INSTITUCIÓN: {e}")

if check_exists(instructivo, "instructivo oficial", False):
    txt = instructivo.read_text(encoding="utf-8", errors="replace")
    print("Caracteres instructivo:", len(txt))
    for term in ["PES", "CSV", "mayo de 2026", "12 de junio", "duplic"]:
        if term.lower() in txt.lower():
            ok(f"Instructivo contiene referencia: {term}")
        else:
            warn(f"No se encontró referencia en instructivo: {term}")

print("\n[4] Scripts esperados")
scripts = [
    "config_personal_academico_2026.py",
    "validaciones_personal_academico_2026.py",
    "validar_archivo_personal_academico_2026.py",
    "exportar_personal_academico_2026.py",
    "incorporar_base_preliminar_personal_academico_2026.py",
]
for s in scripts:
    check_exists(MOD / "scripts" / s, f"scripts/{s}", required=(s != "incorporar_base_preliminar_personal_academico_2026.py"))

print("\n[5] Compilación Python")
for p in sorted((MOD / "scripts").glob("*.py")) if (MOD / "scripts").exists() else []:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], cwd=ROOT, text=True, capture_output=True)
    if r.returncode == 0:
        ok(f"py_compile OK: {p.relative_to(ROOT)}")
    else:
        err(f"py_compile falla: {p.relative_to(ROOT)}\n{r.stderr}")

print("\n[6] RAW preliminar TSV")
raw = MOD / "insumos" / "preliminares" / "base_preliminar_personal_academico_en_institucion_RAW.tsv"
if check_exists(raw, "RAW TSV base preliminar", False):
    try:
        lines = [line for line in raw.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
        print("Filas no vacías RAW:", len(lines))
        print("SHA256 RAW:", sha256(raw))
        if lines:
            header = lines[0].split("\t")
            print("Columnas encabezado RAW:", len(header))
            print("Primer encabezado:", header[0] if header else "")
            print("Último encabezado:", header[-1] if header else "")
            if len(header) == 34:
                ok("RAW tiene 34 columnas en encabezado.")
            else:
                err(f"RAW tiene {len(header)} columnas; se esperaban 34.")
            repeated = 0
            bad = []
            for i, line in enumerate(lines[1:], start=2):
                cols = line.split("\t")
                if cols == header:
                    repeated += 1
                elif len(cols) != 34:
                    bad.append((i, len(cols), line[:120]))
            print("Encabezados repetidos internos:", repeated)
            print("Filas con ancho distinto de 34:", len(bad))
            if repeated >= 1:
                ok("Se detectó encabezado repetido interno para auditar.")
            else:
                warn("No se detectó encabezado repetido interno.")
            if bad:
                err("Hay filas RAW con ancho distinto de 34.")
                for rownum, width, preview in bad[:20]:
                    print(f"Fila {rownum}: {width} columnas | {preview}")
            else:
                ok("RAW no tiene filas de datos con ancho distinto de 34.")
    except Exception as e:
        err(f"No se pudo revisar RAW: {e}")

print("\n[7] Ejecutar incorporador si existe")
inc = MOD / "scripts" / "incorporar_base_preliminar_personal_academico_2026.py"
if inc.exists() and raw.exists():
    run_cmd([sys.executable, str(inc)], "Ejecutar incorporador base preliminar", required=False)
else:
    warn("No se ejecuta incorporador porque falta script o RAW.")

print("\n[8] Base normalizada y base general")
normalizada = MOD / "data" / "base_general" / "base_preliminar_en_institucion_normalizada.tsv"
base_general = MOD / "data" / "base_general" / "base_general_personal_academico_en_institucion.tsv"

for path, label in [(normalizada, "base preliminar normalizada"), (base_general, "base general acumulable")]:
    if check_exists(path, label, False):
        try:
            rows = read_delimited(path, "\t")
            header = rows[0] if rows else []
            print(label, "| filas:", len(rows), "| columnas:", len(header))
            print("Primera columna:", header[0] if header else "")
            print("Última columna:", header[-1] if header else "")
            if len(header) == 34 and header[0] == "TIPO_DOCUMENTO" and header[-1] == "VIGENCIA":
                ok(f"{label} tiene estructura oficial de 34 columnas.")
            else:
                err(f"{label} no tiene estructura oficial de 34 columnas.")
            docs = {}
            for idx, row in enumerate(rows[1:], start=2):
                if len(row) >= 3:
                    key = (row[0], row[1], row[2])
                    docs.setdefault(key, []).append(idx)
            dup = {k:v for k, v in docs.items() if len(v) > 1}
            print("Documentos repetidos por TIPO+NUM+DV:", len(dup))
            if dup:
                warn(f"{label} contiene documentos repetidos; revisar duplicidad normativa.")
                for k, v in list(dup.items())[:10]:
                    print("  ", k, "filas", v[:10])
        except Exception as e:
            err(f"No se pudo revisar {label}: {e}")

print("\n[9] Catálogo de mapeo")
mapeo = MOD / "catalogos" / "mapeo_encabezados_base_preliminar_en_institucion.tsv"
if check_exists(mapeo, "catálogo mapeo encabezados", False):
    rows = read_delimited(mapeo, "\t")
    header = rows[0] if rows else []
    print("Filas mapeo:", len(rows), "| columnas:", len(header))
    esperado = ["encabezado_preliminar", "encabezado_normalizado", "encabezado_oficial", "estado_mapeo", "observacion"]
    if header == esperado:
        ok("Mapeo tiene encabezado esperado.")
    else:
        warn(f"Mapeo tiene encabezado distinto: {header}")

print("\n[10] Auditorías, reportes y bitácoras")
audit_dir = MOD / "auditorias" / "base_preliminar"
if audit_dir.exists():
    audits = sorted(audit_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    print("Auditorías base preliminar:", len(audits))
    for p in audits[:10]:
        print("  ", p.relative_to(ROOT), "| bytes:", p.stat().st_size)
    if audits:
        ok("Existen auditorías de base preliminar.")
    else:
        warn("No hay auditorías de base preliminar.")
else:
    warn("No existe auditorias/base_preliminar.")

for rel in [
    "docs/DIAGNOSTICO_REPOSITORIO_PERSONAL_ACADEMICO_2026.md",
    "docs/DIAGNOSTICO_INSUMOS_OFICIALES_PERSONAL_ACADEMICO_2026.md",
    "docs/DICCIONARIO_PERSONAL_ACADEMICO_2026.md",
    "docs/REPORTE_FASE_2_VALIDADOR_BASE.md",
    "docs/REPORTE_FASE_3_BASE_PRELIMINAR.md",
    "bitacoras/BITACORA_FASE_2_VALIDADOR_BASE.md",
    "bitacoras/base_preliminar/BITACORA_FASE_3_BASE_PRELIMINAR.md",
]:
    check_exists(MOD / rel, rel, required=False)

print("\n[11] Validar fixtures y base general")
val = MOD / "scripts" / "validar_archivo_personal_academico_2026.py"
if val.exists():
    fx_en = MOD / "tests" / "fixtures" / "en_institucion_valido_minimo.csv"
    fx_fuera = MOD / "tests" / "fixtures" / "fuera_institucion_valido_minimo.csv"

    if fx_en.exists():
        run_cmd([sys.executable, str(val), "--tipo", "en_institucion", "--input", str(fx_en)], "Validar fixture en institución", required=False)
    else:
        warn("No existe fixture en_institucion_valido_minimo.csv")

    if fx_fuera.exists():
        run_cmd([sys.executable, str(val), "--tipo", "fuera_institucion", "--input", str(fx_fuera)], "Validar fixture fuera institución", required=False)
    else:
        warn("No existe fixture fuera_institucion_valido_minimo.csv")

    if base_general.exists():
        r = run_cmd([sys.executable, str(val), "--tipo", "en_institucion", "--input", str(base_general), "--delimitador-entrada", "tab"], "Validar base general TSV con delimitador tab", required=False)
        if r.returncode != 0:
            warn("Si el error indica que 'tab' no es aceptado, falta ajustar el validador para interpretar tab como \\t.")
else:
    err("No existe validador principal.")

print("\n[12] Probar bloqueo del exportador")
exp = MOD / "scripts" / "exportar_personal_academico_2026.py"
if exp.exists():
    input_export = base_general if base_general.exists() else (MOD / "tests" / "fixtures" / "en_institucion_valido_minimo.csv")
    out_test = MOD / "resultados" / "TEST_NO_DEBE_CREARSE_PES_READY.csv"
    if out_test.exists():
        out_test.unlink()
    if input_export.exists():
        run_cmd([sys.executable, str(exp), "--tipo", "en_institucion", "--input", str(input_export), "--output", str(out_test)], "Probar exportador bloqueado sin permiso final", required=False)
        if out_test.exists():
            err("El exportador creó PES_READY sin --permitir-exportacion-final. Revisar bloqueo.")
        else:
            ok("Exportador permanece bloqueado: no creó PES_READY sin permiso explícito.")
    else:
        warn("No hay input para probar exportador.")
else:
    warn("No existe exportador.")

print("\n[13] Pytest")
r = subprocess.run([sys.executable, "-m", "pytest", str(MOD / "tests")], cwd=ROOT, text=True, capture_output=True)
if r.returncode == 0:
    ok("pytest OK.")
    print(r.stdout[-3000:])
else:
    if "No module named pytest" in (r.stderr + r.stdout):
        warn("pytest no está instalado. No se instalan dependencias por seguridad.")
    else:
        warn("pytest falló o hay tests pendientes.")
        print(r.stdout[-3000:])
        print(r.stderr[-3000:])

print("\n[14] .gitignore y archivos ignorados")
gitignore = ROOT / ".gitignore"
if gitignore.exists():
    txt = gitignore.read_text(encoding="utf-8", errors="replace")
    if "*.csv" in txt:
        warn(".gitignore contiene *.csv: CSV oficiales, fixtures y auditorías pueden estar ignorados por git.")
    else:
        ok(".gitignore no contiene *.csv global.")
else:
    warn("No existe .gitignore.")

run_cmd(["git", "status", "--ignored", "--short", "personal_academico_2026"], "Archivos ignorados dentro del módulo", required=False)

print("\n[15] Búsqueda PES_READY")
pes_ready = [p for p in MOD.rglob("*") if p.is_file() and "PES_READY" in p.name.upper()]
if pes_ready:
    warn("Hay archivos con PES_READY en el módulo. Revisar que no sean salidas finales no autorizadas.")
    for p in pes_ready:
        print("  ", p.relative_to(ROOT), "| bytes:", p.stat().st_size)
else:
    ok("No se detectan archivos PES_READY reales.")

print("\n" + "=" * 100)
print("RESUMEN FINAL")
print("=" * 100)
print("OK:", len(oks))
print("ADVERTENCIAS:", len(advertencias))
print("ERRORES:", len(errores))

if advertencias:
    print("\nADVERTENCIAS:")
    for i, m in enumerate(advertencias, 1):
        print(f"{i}. {m}")

if errores:
    print("\nERRORES:")
    for i, m in enumerate(errores, 1):
        print(f"{i}. {m}")
    print("\nESTADO FINAL: REVISAR / NO GENERAR CARGA PES")
    raise SystemExit(1)

print("\nESTADO FINAL: VERIFICACIÓN COMPLETADA SIN ERRORES CRÍTICOS")
print("Nota: cualquier advertencia debe revisarse antes de habilitar una exportación PES_READY.")

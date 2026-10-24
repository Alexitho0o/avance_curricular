"""
generar_fcu_pes_final.py
────────────────────────────────────────────────────────────────────────────
Convierte FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS.csv (separador ,)
al formato exigido por PES/SIES (separador ;, sin encabezado, sin línea vacía
final) y aplica correcciones condicionales detectadas en la carga rechazada.

No modifica caracterizacion.py ni ningún archivo fuente.

Ejecución:
    python3 scripts/generar_fcu_pes_final.py
"""

import csv
import pathlib
import sys
from collections import Counter

# ── Rutas exactas ────────────────────────────────────────────────────────────
ENTRADA = pathlib.Path(
    "/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS.csv"
)
SALIDA = pathlib.Path(
    "/Users/alexi/Desktop/FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS_PES_FINAL.csv"
)
AUDITORIA = pathlib.Path(
    "/Users/alexi/Desktop/FCU_2026_AUDITORIA_PES_FINAL_20260505.csv"
)

FILAS_ESPERADAS = 1371
COLS_ESPERADAS = 195

# ── Índices base cero (confirmados) ──────────────────────────────────────────
IDX_NOMBRE   = 1
IDX_APELL1   = 2
IDX_APELL2   = 3
IDX_RUT      = 5
IDX_DISCAP_FIS  = 18
IDX_DISCAP_AUD  = 19
IDX_DISCAP_VIS  = 20
IDX_DISCAP_INT  = 21
IDX_DISCAP_PSQ  = 22
IDX_DISCAP_REGIS  = 23
IDX_DISCAP_ORIENT = 24
IDX_RAP         = 89
IDX_RAZ_NO_RAP  = 90
IDX_CONTACTO    = 134


# ════════════════════════════════════════════════════════════════════════════
# 1. LECTURA Y VALIDACIÓN DE ENTRADA
# ════════════════════════════════════════════════════════════════════════════
def leer_y_validar_entrada(ruta: pathlib.Path) -> list[list[str]]:
    if not ruta.exists():
        raise SystemExit(f"[ERROR] Archivo de entrada no encontrado: {ruta}")

    raw = ruta.read_bytes().decode("utf-8-sig", errors="replace")
    # Normalizar saltos de línea
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    # Eliminar únicamente la línea vacía final si existe
    lines = raw.split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()

    # Filas vacías internas
    vacias_internas = [i + 1 for i, ln in enumerate(lines) if ln.strip() == ""]
    if vacias_internas:
        raise SystemExit(
            f"[ERROR] Filas vacías internas en entrada: {vacias_internas[:10]}"
        )

    rows = list(csv.reader(lines, delimiter=","))

    if len(rows) != FILAS_ESPERADAS:
        raise SystemExit(
            f"[ERROR] Entrada tiene {len(rows)} filas físicas; se esperaban {FILAS_ESPERADAS}."
        )

    conteo = Counter(len(r) for r in rows)
    if conteo != Counter({COLS_ESPERADAS: FILAS_ESPERADAS}):
        raise SystemExit(
            f"[ERROR] Campos por fila en entrada (coma): {dict(conteo)}; "
            f"se esperaba {{{COLS_ESPERADAS}: {FILAS_ESPERADAS}}}."
        )

    # Verificar ausencia de encabezado: col 5 de la primera fila debe ser un RUT
    primer_rut = rows[0][IDX_RUT].strip()
    if not any(c.isdigit() for c in primer_rut):
        raise SystemExit(
            f"[ERROR] La primera fila parece encabezado (fila[5]={primer_rut!r})."
        )

    return rows


# ════════════════════════════════════════════════════════════════════════════
# 2. CORRECCIONES CONDICIONALES
# ════════════════════════════════════════════════════════════════════════════
def aplicar_correcciones(
    rows: list[list[str]],
) -> tuple[list[list[str]], list[dict]]:
    audit: list[dict] = []
    corr_rap = 0
    corr_discap_reg = 0
    corr_discap_ori = 0
    corr_contacto = 0

    for linea_fisica, fila in enumerate(rows, start=1):
        rut = fila[IDX_RUT].strip()
        nombre = " ".join(
            [
                fila[IDX_NOMBRE].strip(),
                fila[IDX_APELL1].strip(),
                fila[IDX_APELL2].strip(),
            ]
        ).strip()

        # ── Regla 1: RAP P27.3 / P27.4 ──────────────────────────────────────
        # Si RAP == "2" (No) y RAZ_NO_RAP vacío → imputar "3"
        if fila[IDX_RAP].strip() == "2" and fila[IDX_RAZ_NO_RAP].strip() == "":
            fila[IDX_RAZ_NO_RAP] = "3"
            corr_rap += 1
            audit.append(
                {
                    "linea_fisica": linea_fisica,
                    "rut": rut,
                    "nombre": nombre,
                    "regla": "RAP_P27_3_P27_4",
                    "campo": "RAZ_NO_RAP",
                    "indice": IDX_RAZ_NO_RAP,
                    "valor_anterior": "",
                    "valor_nuevo": "3",
                    "observacion": "RAP=2 (No) sin RAZ_NO_RAP; se imputa valor 3 (No corresponde)",
                }
            )

        # ── Regla 2a: Discapacidad → Registro Nacional ────────────────────
        # Si alguna discapacidad específica == "1" y DISCAP_REGIS vacío → "4"
        discap_activa = any(
            fila[idx].strip() == "1"
            for idx in (
                IDX_DISCAP_FIS,
                IDX_DISCAP_AUD,
                IDX_DISCAP_VIS,
                IDX_DISCAP_INT,
                IDX_DISCAP_PSQ,
            )
        )
        if discap_activa and fila[IDX_DISCAP_REGIS].strip() == "":
            fila[IDX_DISCAP_REGIS] = "4"
            corr_discap_reg += 1
            tipos = [
                n
                for n, idx in [
                    ("DISCAP_FIS", IDX_DISCAP_FIS),
                    ("DISCAP_AUD", IDX_DISCAP_AUD),
                    ("DISCAP_VIS", IDX_DISCAP_VIS),
                    ("DISCAP_INT", IDX_DISCAP_INT),
                    ("DISCAP_PSQ", IDX_DISCAP_PSQ),
                ]
                if fila[idx].strip() == "1"
            ]
            audit.append(
                {
                    "linea_fisica": linea_fisica,
                    "rut": rut,
                    "nombre": nombre,
                    "regla": "DISCAP_REGISTRO",
                    "campo": "DISCAP_REGIS",
                    "indice": IDX_DISCAP_REGIS,
                    "valor_anterior": "",
                    "valor_nuevo": "4",
                    "observacion": (
                        f"Discapacidad declarada ({', '.join(tipos)}) sin DISCAP_REGIS; "
                        "se imputa 4 (No registrado)"
                    ),
                }
            )

        # ── Regla 2b: DISCAP_REGIS en {3,4} → DISCAP_ORIENT ──────────────
        # Si DISCAP_REGIS es "3" o "4" y DISCAP_ORIENT vacío → "2"
        if fila[IDX_DISCAP_REGIS].strip() in {"3", "4"} and fila[IDX_DISCAP_ORIENT].strip() == "":
            fila[IDX_DISCAP_ORIENT] = "2"
            corr_discap_ori += 1
            audit.append(
                {
                    "linea_fisica": linea_fisica,
                    "rut": rut,
                    "nombre": nombre,
                    "regla": "DISCAP_ORIENTACION",
                    "campo": "DISCAP_ORIENT",
                    "indice": IDX_DISCAP_ORIENT,
                    "valor_anterior": "",
                    "valor_nuevo": "2",
                    "observacion": (
                        f"DISCAP_REGIS={fila[IDX_DISCAP_REGIS].strip()!r} sin DISCAP_ORIENT; "
                        "se imputa 2 (No requiere orientación)"
                    ),
                }
            )

        # ── Regla 3: CONTACTO ────────────────────────────────────────────────
        if fila[IDX_CONTACTO].strip() == "":
            fila[IDX_CONTACTO] = "3"
            corr_contacto += 1
            audit.append(
                {
                    "linea_fisica": linea_fisica,
                    "rut": rut,
                    "nombre": nombre,
                    "regla": "CONTACTO",
                    "campo": "CONTACTO",
                    "indice": IDX_CONTACTO,
                    "valor_anterior": "",
                    "valor_nuevo": "3",
                    "observacion": "CONTACTO vacío; se imputa 3 (No desea ser contactado)",
                }
            )

    return rows, audit, corr_rap, corr_discap_reg, corr_discap_ori, corr_contacto


# ════════════════════════════════════════════════════════════════════════════
# 3. ESCRITURA DE AUDITORÍA
# ════════════════════════════════════════════════════════════════════════════
def escribir_auditoria(audit: list[dict], ruta: pathlib.Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "linea_fisica", "rut", "nombre", "regla", "campo",
        "indice", "valor_anterior", "valor_nuevo", "observacion",
    ]
    with ruta.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=campos, delimiter=";")
        writer.writeheader()
        writer.writerows(audit)


# ════════════════════════════════════════════════════════════════════════════
# 4. ESCRITURA DEL ARCHIVO FINAL (sin línea vacía final)
# ════════════════════════════════════════════════════════════════════════════
def escribir_salida(rows: list[list[str]], ruta: pathlib.Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    texto = "\n".join(";".join(fila) for fila in rows)
    ruta.write_text(texto, encoding="utf-8", newline="")


# ════════════════════════════════════════════════════════════════════════════
# 5. VALIDACIÓN FÍSICA DEL ARCHIVO FINAL
# ════════════════════════════════════════════════════════════════════════════
def validar_salida(ruta: pathlib.Path, rows_corregidas: list[list[str]]) -> dict:
    raw_bytes = ruta.read_bytes()
    termina_salto = raw_bytes.endswith(b"\n") or raw_bytes.endswith(b"\r\n")

    texto = ruta.read_text(encoding="utf-8", errors="replace")
    lines_sc = texto.split("\n")
    # Eliminar línea vacía final si por alguna razón quedó
    while lines_sc and lines_sc[-1].strip() == "":
        lines_sc.pop()

    rows_sc = list(csv.reader(lines_sc, delimiter=";"))
    conteo_sc = Counter(len(r) for r in rows_sc)

    rows_coma = list(csv.reader(lines_sc, delimiter=","))
    conteo_coma = Counter(len(r) for r in rows_coma)

    return {
        "filas_sc": len(rows_sc),
        "conteo_sc": dict(conteo_sc),
        "filas_coma": len(rows_coma),
        "conteo_coma": dict(conteo_coma),
        "termina_salto": termina_salto,
    }


# ════════════════════════════════════════════════════════════════════════════
# 6. VALIDACIÓN DE REGLAS CONDICIONALES POST-CORRECCIÓN
# ════════════════════════════════════════════════════════════════════════════
def validar_reglas(rows: list[list[str]]) -> dict:
    pend_rap = sum(
        1 for f in rows
        if f[IDX_RAP].strip() == "2" and f[IDX_RAZ_NO_RAP].strip() == ""
    )
    pend_disc_reg = sum(
        1 for f in rows
        if any(f[i].strip() == "1" for i in (
            IDX_DISCAP_FIS, IDX_DISCAP_AUD, IDX_DISCAP_VIS,
            IDX_DISCAP_INT, IDX_DISCAP_PSQ,
        ))
        and f[IDX_DISCAP_REGIS].strip() == ""
    )
    pend_disc_ori = sum(
        1 for f in rows
        if f[IDX_DISCAP_REGIS].strip() in {"3", "4"}
        and f[IDX_DISCAP_ORIENT].strip() == ""
    )
    pend_contacto = sum(
        1 for f in rows if f[IDX_CONTACTO].strip() == ""
    )
    return {
        "pendientes_rap": pend_rap,
        "pendientes_discap_registro": pend_disc_reg,
        "pendientes_discap_orientacion": pend_disc_ori,
        "pendientes_contacto": pend_contacto,
    }


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════
def main() -> None:
    # 1. Leer y validar entrada
    rows = leer_y_validar_entrada(ENTRADA)
    filas_entrada = len(rows)

    # 2. Correcciones condicionales
    rows, audit, corr_rap, corr_discap_reg, corr_discap_ori, corr_contacto = (
        aplicar_correcciones(rows)
    )

    # 3. Auditoría
    escribir_auditoria(audit, AUDITORIA)

    # 4. Escritura final
    escribir_salida(rows, SALIDA)

    # 5. Validación física
    val = validar_salida(SALIDA, rows)

    # 6. Validación reglas condicionales post-corrección
    pend = validar_reglas(rows)

    # ── Resumen ──────────────────────────────────────────────────────────────
    filas_salida = val["filas_sc"]
    campos_sc = val["conteo_sc"]
    campos_coma = val["conteo_coma"]

    print(f"archivo_entrada:                  {ENTRADA}")
    print(f"archivo_salida:                   {SALIDA}")
    print(f"auditoria_salida:                 {AUDITORIA}")
    print(f"filas_entrada:                    {filas_entrada}")
    print(f"filas_salida:                     {filas_salida}")
    print(f"campos_por_fila_entrada_coma:     {{{COLS_ESPERADAS}: {filas_entrada}}}")
    print(f"campos_por_fila_salida_semicolon: {campos_sc}")
    print(f"campos_por_fila_salida_coma:      {campos_coma}")
    print(f"termina_con_salto_linea:          {val['termina_salto']}")
    print(f"correcciones_rap:                 {corr_rap}")
    print(f"correcciones_discap_registro:     {corr_discap_reg}")
    print(f"correcciones_discap_orientacion:  {corr_discap_ori}")
    print(f"correcciones_contacto:            {corr_contacto}")
    print(f"pendientes_rap:                   {pend['pendientes_rap']}")
    print(f"pendientes_discap_registro:       {pend['pendientes_discap_registro']}")
    print(f"pendientes_discap_orientacion:    {pend['pendientes_discap_orientacion']}")
    print(f"pendientes_contacto:              {pend['pendientes_contacto']}")

    # ── Verificaciones finales ───────────────────────────────────────────────
    errores: list[str] = []

    if filas_salida != FILAS_ESPERADAS:
        errores.append(
            f"filas_salida={filas_salida} != {FILAS_ESPERADAS}"
        )
    if campos_sc != {COLS_ESPERADAS: FILAS_ESPERADAS}:
        errores.append(
            f"campos_salida_semicolon incorrecto: {campos_sc}"
        )
    if campos_coma != {1: FILAS_ESPERADAS}:
        errores.append(
            f"campos_salida_coma no es 1 por fila: {campos_coma}"
        )
    if val["termina_salto"]:
        errores.append("El archivo final termina con salto de línea.")
    for k, v in pend.items():
        if v != 0:
            errores.append(f"{k}={v} (se esperaba 0)")

    if errores:
        print()
        for e in errores:
            print(f"[ERROR] {e}")
        raise SystemExit("[FALLA] No se cumplen todos los criterios. Ver errores arriba.")

    print()
    print("OK_FCU_PES_FINAL_LISTO_PARA_SUBIR")


if __name__ == "__main__":
    main()

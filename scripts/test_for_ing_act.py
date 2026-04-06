#!/usr/bin/env python3
"""
Tests automatizados para motor FOR_ING_ACT — MU 2026
Valida golden cases, integridad de flags, dominio y políticas.
"""
import json, sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
TRACE = BASE / "control" / "for_ing_act_trace_long.tsv"
GOLDEN = BASE / "control" / "for_ing_act_golden_cases.json"

passed = 0
failed = 0
errors = []


def ok(test_id: str, msg: str):
    global passed
    passed += 1
    print(f"  ✅ {test_id}: {msg}")


def fail(test_id: str, msg: str):
    global failed
    failed += 1
    errors.append(f"{test_id}: {msg}")
    print(f"  ❌ {test_id}: {msg}")


def main():
    global passed, failed

    print("=" * 80)
    print("Tests FOR_ING_ACT — MU 2026")
    print("=" * 80)

    # Load
    df = pd.read_csv(TRACE, sep="\t")
    with open(GOLDEN) as f:
        golden = json.load(f)

    n_codcli = df["CODCLI"].nunique()
    print(f"  Trace: {len(df)} filas, {n_codcli} CODCLI únicos\n")

    # ═══════════════════════════════════════════════════════════════════════
    # A. TESTS DE DOMINIO Y POLÍTICA
    # ═══════════════════════════════════════════════════════════════════════
    print("--- A. Dominio y Política ---")

    # A1: Solo códigos soportados
    soportados = {1, 2, 3, 4, 11}
    emitidos = set(df["FOR_ING_ACT"].unique())
    if emitidos.issubset(soportados):
        ok("A1", f"Todos los códigos emitidos ∈ {soportados}: {emitidos}")
    else:
        fail("A1", f"Códigos fuera de dominio: {emitidos - soportados}")

    # A2: Ningún código bloqueado
    bloqueados = {5, 6, 7, 8, 9, 10}
    emitidos_bloq = emitidos & bloqueados
    if not emitidos_bloq:
        ok("A2", "Ningún código bloqueado (5-10) emitido")
    else:
        fail("A2", f"Códigos bloqueados emitidos: {emitidos_bloq}")

    # A3: FOR=4 es 0 (externo bloqueado)
    n4 = (df["FOR_ING_ACT"] == 4).sum()
    if n4 == 0:
        ok("A3", "FOR=4 (externo) = 0 registros (política BLOQUEADO_SIN_FUENTE)")
    else:
        fail("A3", f"FOR=4 tiene {n4} registros pero debería ser 0")

    # A4: ≥500 CODCLI evaluados
    if n_codcli >= 500:
        ok("A4", f"{n_codcli} CODCLI evaluados (≥500)")
    else:
        fail("A4", f"Solo {n_codcli} CODCLI evaluados (<500)")

    # ═══════════════════════════════════════════════════════════════════════
    # B. INTEGRIDAD DE FLAGS
    # ═══════════════════════════════════════════════════════════════════════
    print("\n--- B. Integridad de Flags ---")

    # B1: FOR=11 → TIENE_TNS_PREV_DA=1 AND PROFESIONAL=1
    r11 = df[df["FOR_ING_ACT"] == 11]
    bad11 = r11[(r11["TIENE_TNS_PREV_DA"] != 1) | (r11["PROGRAMA_ACTUAL_ES_PROFESIONAL_DA"] != 1)]
    if len(bad11) == 0:
        ok("B1", f"FOR=11 ({len(r11)}): todos TIENE_TNS_PREV=1 AND PROFESIONAL=1")
    else:
        fail("B1", f"{len(bad11)} FOR=11 sin flags correctos")

    # B2: FOR=2 → ES_CONTINUIDAD_DA=1
    r2 = df[df["FOR_ING_ACT"] == 2]
    bad2 = r2[r2["ES_CONTINUIDAD_DA"] != 1]
    if len(bad2) == 0:
        ok("B2", f"FOR=2 ({len(r2)}): todos ES_CONTINUIDAD_DA=1")
    else:
        fail("B2", f"{len(bad2)} FOR=2 sin ES_CONTINUIDAD_DA=1")

    # B3: FOR=3 → ES_CAMBIO_INTERNO_DA=1
    r3 = df[df["FOR_ING_ACT"] == 3]
    bad3 = r3[r3["ES_CAMBIO_INTERNO_DA"] != 1]
    if len(bad3) == 0:
        ok("B3", f"FOR=3 ({len(r3)}): todos ES_CAMBIO_INTERNO_DA=1")
    else:
        fail("B3", f"{len(bad3)} FOR=3 sin ES_CAMBIO_INTERNO_DA=1")

    # B4: FOR=1 → ningún flag especial TRUE que debería haber disparado otra regla
    r1 = df[df["FOR_ING_ACT"] == 1]
    r1_bad = r1[(r1["ES_CONTINUIDAD_DA"] == 1) |
                ((r1["TIENE_TNS_PREV_DA"] == 1) & (r1["PROGRAMA_ACTUAL_ES_PROFESIONAL_DA"] == 1)) |
                (r1["ES_CAMBIO_INTERNO_DA"] == 1)]
    if len(r1_bad) == 0:
        ok("B4", f"FOR=1 ({len(r1)}): ninguno con flags que debieron capturar regla superior")
    else:
        fail("B4", f"{len(r1_bad)} FOR=1 con flags inconsistentes")

    # B5: ES_CAMBIO_EXTERNO_DA es siempre 0
    if (df["ES_CAMBIO_EXTERNO_DA"] == 0).all():
        ok("B5", "ES_CAMBIO_EXTERNO_DA=0 para todos (política de bloqueo)")
    else:
        fail("B5", "Hay registros con ES_CAMBIO_EXTERNO_DA=1")

    # ═══════════════════════════════════════════════════════════════════════
    # C. PRIORIDAD DEL ÁRBOL
    # ═══════════════════════════════════════════════════════════════════════
    print("\n--- C. Prioridad del Árbol ---")

    # C1: CONTINUIDAD + CAMBIO_INTERNO sin TNS prev → code 2 (no 3)
    ci_cont = df[(df["ES_CONTINUIDAD_DA"] == 1) & (df["ES_CAMBIO_INTERNO_DA"] == 1) &
                 (df["TIENE_TNS_PREV_DA"] == 0)]
    if len(ci_cont) > 0:
        bad_prio = ci_cont[ci_cont["FOR_ING_ACT"] != 2]
        if len(bad_prio) == 0:
            ok("C1", f"CONTINUIDAD+CAMBIO_INTERNO sin TNS → FOR=2 ({len(ci_cont)} casos)")
        else:
            fail("C1", f"{len(bad_prio)} casos con CONTINUIDAD+CAMBIO_INTERNO sin TNS que NO son FOR=2")
    else:
        ok("C1", "No hay casos CONTINUIDAD+CAMBIO_INTERNO sin TNS (N/A)")

    # C2: CONTINUIDAD + CAMBIO_INTERNO + TNS prev → code 11 (no 2 ni 3)
    ci_cont_tns = df[(df["ES_CONTINUIDAD_DA"] == 1) & (df["ES_CAMBIO_INTERNO_DA"] == 1) &
                     (df["TIENE_TNS_PREV_DA"] == 1)]
    if len(ci_cont_tns) > 0:
        bad_prio = ci_cont_tns[ci_cont_tns["FOR_ING_ACT"] != 11]
        if len(bad_prio) == 0:
            ok("C2", f"CONTINUIDAD+CAMBIO_INTERNO+TNS → FOR=11 ({len(ci_cont_tns)} caso(s))")
        else:
            fail("C2", f"{len(bad_prio)} casos con triple flag que NO son FOR=11")
    else:
        ok("C2", "No hay casos con triple flag (N/A)")

    # C3: Validación manual V2 — programa CONTINUIDAD nunca es code 1
    cont_1 = df[(df["ES_CONTINUIDAD_DA"] == 1) & (df["FOR_ING_ACT"] == 1)]
    if len(cont_1) == 0:
        ok("C3", "Ningún programa CONTINUIDAD con FOR=1 (cumple manual V2)")
    else:
        fail("C3", f"{len(cont_1)} CONTINUIDAD con FOR=1 (viola manual)")

    # ═══════════════════════════════════════════════════════════════════════
    # D. GOLDEN CASES INDIVIDUALES
    # ═══════════════════════════════════════════════════════════════════════
    print("\n--- D. Golden Cases ---")

    for gc in golden:
        gc_id = gc["id"]
        # Skip pattern-based / aggregate cases (GC04, GC05, GC10, GC11, GC12)
        if "codcli" not in gc:
            continue

        codcli = gc["codcli"]
        match = df[df["CODCLI"] == codcli]
        if len(match) == 0:
            fail(gc_id, f"CODCLI {codcli} no encontrado en trace")
            continue
        row = match.iloc[0]
        expected_for = gc["expected_for_ing_act"]
        actual_for = int(row["FOR_ING_ACT"])
        expected_rule = gc["expected_rule"]
        actual_rule = row["FOR_ING_ACT_RULE_DA"]

        if actual_for != expected_for:
            fail(gc_id, f"{codcli}: FOR={actual_for} (esperado {expected_for})")
            continue
        if actual_rule != expected_rule:
            fail(gc_id, f"{codcli}: RULE={actual_rule} (esperado {expected_rule})")
            continue
        # Check expected flags
        if "expected_flags" in gc:
            flag_ok = True
            for flag, expected_val in gc["expected_flags"].items():
                if flag in row.index:
                    actual_val = int(row[flag])
                    if actual_val != expected_val:
                        fail(gc_id, f"{codcli}: {flag}={actual_val} (esperado {expected_val})")
                        flag_ok = False
                        break
            if flag_ok:
                ok(gc_id, f"{codcli}: FOR={actual_for}, RULE={actual_rule} ✓")
        else:
            ok(gc_id, f"{codcli}: FOR={actual_for}, RULE={actual_rule} ✓")

    # ═══════════════════════════════════════════════════════════════════════
    # RESUMEN
    # ═══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print(f"RESULTADO: {passed} PASSED / {failed} FAILED")
    if errors:
        print("\nFALLOS:")
        for e in errors:
            print(f"  ❌ {e}")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

import re
from collections import Counter


def normalize_run(num, dv=""):
    raw = "" if num is None else str(num).strip().upper()
    raw_dv = "" if dv is None else str(dv).strip().upper()
    if "-" in raw and not raw_dv:
        raw, raw_dv = raw.rsplit("-", 1)
    body = raw.replace(".", "").replace(" ", "")
    check = raw_dv.replace(".", "").replace(" ", "").upper()
    return body, check


def normalize_passport(value):
    return "" if value is None else str(value).strip().upper()


def rut_expected_dv(body):
    if not re.fullmatch(r"\d+", body or ""):
        return ""
    total = 0
    mult = 2
    for char in reversed(body):
        total += int(char) * mult
        mult = 2 if mult == 7 else mult + 1
    result = 11 - (total % 11)
    if result == 11:
        return "0"
    if result == 10:
        return "K"
    return str(result)


def classify_cardinality(left_keys, right_keys):
    left = Counter(k for k in left_keys if k)
    right = Counter(k for k in right_keys if k)
    common = set(left) & set(right)
    out = {"1:1": 0, "1:N": 0, "N:1": 0, "N:N": 0}
    for key in common:
        l_count = left[key]
        r_count = right[key]
        if l_count == 1 and r_count == 1:
            out["1:1"] += 1
        elif l_count == 1:
            out["1:N"] += 1
        elif r_count == 1:
            out["N:1"] += 1
        else:
            out["N:N"] += 1
    return out


def left_join_size(left_keys, right_keys):
    right = Counter(k for k in right_keys if k)
    size = 0
    for key in left_keys:
        matches = right.get(key, 0)
        size += matches if key and matches else 1
    return size


def test_run_normalization_preserves_text_and_dv():
    body, dv = normalize_run("12.345.678", "k")
    assert body == "12345678"
    assert dv == "K"


def test_passport_is_not_treated_as_run():
    passport = normalize_passport(" ab-001 ")
    body, dv = normalize_run(passport, "")
    assert passport == "AB-001"
    assert rut_expected_dv(body) == ""
    assert dv == "001"


def test_codcli_repeated_by_subject_is_expected_granularity():
    keys = ["C1", "C1", "C1"]
    subjects = ["A1", "A2", "A3"]
    assert len(set(keys)) == 1
    assert len(set(zip(keys, subjects))) == 3


def test_person_with_two_careers_is_not_deduplicated():
    rows = [("DOC1", "CODE1"), ("DOC1", "CODE2")]
    assert len(set(doc for doc, _ in rows)) == 1
    assert len(set(rows)) == 2


def test_person_with_two_plans_requires_review():
    rows = [("DOC1", "CODE1", "PLAN1"), ("DOC1", "CODE1", "PLAN2")]
    assert len(set((doc, code) for doc, code, _ in rows)) == 1
    assert len(set(rows)) == 2


def test_codigo_sies_ambiguous_by_codcarpr():
    bridge = [("CAR1", "DAY", "SIES1"), ("CAR1", "DAY", "SIES2")]
    codes = {code for car, jornada, code in bridge if (car, jornada) == ("CAR1", "DAY")}
    assert len(codes) == 2


def test_codcarpr_with_two_sies_codes_is_not_unique():
    bridge = [("CAR1", "SIES1"), ("CAR1", "SIES2")]
    assert classify_cardinality(["CAR1"], [car for car, _ in bridge])["1:N"] == 1


def test_left_join_preserves_left_rows_without_match():
    assert left_join_size(["A", "B"], ["A"]) == 2


def test_many_to_many_expansion_detected():
    assert classify_cardinality(["A", "A"], ["A", "A"])["N:N"] == 1
    assert left_join_size(["A", "A"], ["A", "A"]) == 4


def test_incomplete_document_is_detectable():
    body, dv = normalize_run("", "")
    assert body == ""
    assert dv == ""


def test_empty_plan_is_not_valid_assignment():
    plan = ""
    assert not plan


def test_missing_codigo_has_no_match():
    assert classify_cardinality(["CODE_X"], ["CODE_A", "CODE_B"]) == {
        "1:1": 0,
        "1:N": 0,
        "N:1": 0,
        "N:N": 0,
    }


def test_person_career_unique_combination():
    rows = [("DOC1", "CODE1"), ("DOC2", "CODE1")]
    assert len(rows) == len(set(rows))


def test_person_career_duplicate_combination_detected():
    rows = [("DOC1", "CODE1"), ("DOC1", "CODE1")]
    assert len(rows) != len(set(rows))


def test_initial_zeroes_are_preserved():
    body, dv = normalize_run("00123456", "7")
    assert body == "00123456"
    assert dv == "7"

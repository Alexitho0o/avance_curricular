"""Contraste agregado del listado con H002c y el catálogo v2. Reutiliza el Paso 1."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import openpyxl

out = Path(__file__).resolve().parent
repo = out.parents[1]
listado = repo / "data/cierre_d2/20261016/fuentes/Listado_Planes_estudio_Sedes RE+CO.xlsx"
perfil = repo / "outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json"
tipos = repo / "data/paridad_codigo_sies/regla_operativa_mu_v2/TIPO_PLAN_POR_PLAN_UMAS.json"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(listado) == "fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049"
wb = openpyxl.load_workbook(listado, read_only=True, data_only=True)
rows = iter(wb["BBDD Bruta"].values)
header = next(rows)
regimen = Counter()
grupos = Counter()
co = Counter()
admp = Counter()
catalogo = {
    (r["codcarpr"], r["plan_umas"], r["sede_umas"]): r["tipo_plan"]
    for r in json.loads(tipos.read_text())["filas"]
}
for values in rows:
    r = dict(zip(header, values))
    if not r["CODRAMO"]:
        assert not r["REGIMEN"]
        continue
    regimen[r["REGIMEN"]] += 1
    if r["REGIMEN"] != "S":
        continue
    carrera, plan, sede = r["Codcarr"], r["CODPESTUD"], r["Sede"]
    grupo = "REOL" if "REOL" in carrera else "literal_CO" if "CO" in carrera else "resto"
    grupos[grupo] += 1
    if grupo == "literal_CO":
        co[carrera, sede, catalogo[carrera, plan, sede]] += 1
    if plan == "ADMP20251" and carrera == "ADMP":
        admp["S"] += 1
wb.close()
referencia = next(r for r in json.loads(perfil.read_text())["perfiles"]
                  if r["codcarpr"] == "ADMP" and r["CODPESTUD"] == "ADMP20251")
assert admp["S"] > 0 and "TRIMESTRAL" in {x["regimen"] for x in referencia["conversion_si_regimen_PROMEDIOS"]}
assert regimen == {"S": 11228, "A": 210}
assert grupos == {"REOL": 1932, "literal_CO": 277, "resto": 9019}
con_tipo = Counter()
for (_, _, tipo), n in co.items():
    con_tipo[tipo] += n
assert con_tipo == {"REGULAR": 169, "E": 108}
p = out / "EVIDENCIA_PASO1_REOL.json"
evidencia = json.loads(p.read_text())
evidencia["reanudacion_paso1c"] = {
    "fuentes": {str(x.relative_to(repo)): sha(x) for x in [listado, perfil, tipos]},
    "hoja": "BBDD Bruta", "unidad": "fila de asignatura con CODRAMO",
    "regimen": dict(regimen), "grupos_lexicos_en_filas_S": dict(grupos),
    "ADMP20251": {"filas_S": admp["S"], "regimen_PROMEDIOS": "TRIMESTRAL"},
    "CO_por_carrera_sede_tipo_v2": [{"carrera": c, "sede": s, "tipo_v2": t, "filas_S": n}
                                      for (c, s, t), n in sorted(co.items())],
    "tipo_v2_en_grupo_CO": dict(con_tipo),
    "conclusion": "El grano y ADMP confirman la distinción entre régimen del ramo y calendario del plan. La etiqueta continuidad del grupo de 277 contradice el catálogo v2.",
    "estado": "PARADA_POR_CONTEO_277_CONTINUIDAD_NO_CONFIRMADO",
}
p.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
informe = out / "INFORME_H011_PASO1.md"
section = "\n## Reanudación del Paso 1c"
base = informe.read_text().split(section)[0]
informe.write_text(base.rstrip() + section + '''

**B/C.** La hoja BBDD Bruta registra 11.228 filas de asignatura con S y 210 con A. ADMP20251 tiene '''+str(admp["S"])+''' filas S, mientras PROMEDIOS registra TRIMESTRAL para ese plan. Esto corrige el motivo de la parada inicial. El campo del ramo puede coexistir con un calendario bimestral o trimestral.

**B/C.** La partición numérica 9.019 / 277 / 1.932 se reproduce sobre Codcarr separando primero REOL y luego cualquier aparición de CO. Al contrastar esos 277 ramos con el tipo v2 por carrera, plan y sede, 169 pertenecen a planes REGULAR y 108 tienen tipo E. Ninguno está clasificado CONTINUIDAD. El detalle agregado y los hashes están en EVIDENCIA_PASO1_REOL.json → reanudacion_paso1c.

**Parada del encargo.** El punto 2 queda confirmado. El punto 1 sólo se confirma como partición de texto. Falta una clave gobernada que identifique las 277 filas de continuidad, o una decisión revisada que prescinda de esa premisa. Cobertura H010b vigente, 2.085 de 3.049 y 99 de 99. No hay nuevas asignaciones ni commit.
''')
print(dict(regimen), dict(grupos), dict(con_tipo), dict(admp))

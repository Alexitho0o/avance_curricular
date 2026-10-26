"""Copia UNA base privada por ejecución a la carpeta consolidada de OneDrive (decisión de Alexi, 26-10-2026).

Las bases contienen RUT y CODCLI: se copian (nunca se mueven) a 07_PRIVADAS_DICCIONARIO y quedan
registradas en la sección `catalogo_privadas` del catálogo. Verifica el hash del origen contra el
descriptor de su edición, el de la copia contra el origen, y que el origen no cambie.
Uso en Mac:  python3 copiar_privada.py --paso N      (N = 1..11; el 11 es la base v10)
"""
import argparse, datetime as dt, hashlib, json, shutil, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIV = "/Users/alexi/.local/share/ipss"
ONEDRIVE = "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián"
CARPETA = "IPSS_CONCILIACION_UMAS_SIES_BASES"
SUB = "07_PRIVADAS_DICCIONARIO"
DIC = "data/diccionario_sies_seguimiento/"
PASOS = {  # paso: (edición o conjunto, descriptor que fija el hash o None, ruta relativa en PRIV, hash esperado si no hay descriptor)
    11: ("v10_20261026_mu2026_27", DIC + "v10_20261026_mu2026_27/descriptor.json", None, None),
    1: ("v9_20261026_cuatro_planes_v3", DIC + "v9_20261026_cuatro_planes_v3/descriptor.json", None, None),
    2: ("v8_20261025_ocho_p", DIC + "v8_20261025_ocho_p/descriptor.json", None, None),
    3: ("v7_20261023_inf35_03_t3", DIC + "v7_20261023_inf35_03_t3/descriptor.json", None, None),
    4: ("v6_20261023_dos_jornadas", DIC + "v6_20261023_dos_jornadas/descriptor.json", None, None),
    5: ("v5_20261023_siete_jornadas", DIC + "v5_20261023_siete_jornadas/descriptor.json", None, None),
    6: ("v4_20261023_inf35_12", DIC + "v4_20261023_inf35_12/descriptor.json", None, None),
    7: ("v3_20261023_inf35_07", DIC + "v3_20261023_inf35_07/descriptor.json", None, None),
    8: ("v2_20261023_14", DIC + "v2_20261023_14/descriptor.json", None, None),
    9: ("v1_20261023", DIC + "v1_20261023/descriptor.json", None, None),
    10: ("vista_seguimiento_fase3_20261025", None, "trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json",
         "72edecb9507f46985533d1c63b83735beb4db58d743c89c226ca6be1a2c8ef31"),
}
nfc = lambda x: unicodedata.normalize("NFC", x)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def resolver(base, resto):
    cur = Path(base)
    for parte in [x for x in resto.split("/") if x]:
        hijos = {nfc(c.name): c for c in cur.iterdir()}
        if nfc(parte) not in hijos:
            return None
        cur = hijos[nfc(parte)]
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paso", type=int, required=True, choices=sorted(PASOS))
    ap.add_argument("--priv-local", default=PRIV)
    ap.add_argument("--onedrive-local", default=ONEDRIVE)
    a = ap.parse_args()
    nombre, desc_rel, rel, esperado = PASOS[a.paso]
    if desc_rel:
        d = json.loads((ROOT / desc_rel).read_text())
        rel = d["base_privada"]["ruta"][len(PRIV) + 1:]
        esperado = d["base_privada"]["sha256"]
    origen = Path(a.priv_local) / rel
    h0 = sha(origen)
    if h0 != esperado:
        sys.exit(f"ALTO: el origen no coincide con el hash fijado ({h0[:12]} vs {esperado[:12]}).")
    raiz = resolver(Path(a.onedrive_local).parent, Path(a.onedrive_local).name)
    destino_dir = raiz / CARPETA / SUB / nombre
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / origen.name
    accion = "YA_EXISTIA_IDENTICO"
    if destino.exists():
        if sha(destino) != h0:
            sys.exit("ALTO: ya existe una copia distinta; no se sobrescribe.")
    else:
        tmp = destino_dir / (origen.name + ".copiando")
        shutil.copyfile(origen, tmp)
        if sha(tmp) != h0:
            sys.exit("ALTO: copia corrupta.")
        tmp.rename(destino)
        accion = "COPIADO"
    if sha(origen) != h0:
        sys.exit("ALTO: el origen cambió durante la copia.")
    entrada = {"paso": f"{a.paso}/{10 if a.paso <= 10 else len(PASOS)}", "conjunto": nombre, "archivo": origen.name,
               "ruta_origen": f"{PRIV}/{rel}", "ruta_consolidada": f"{ONEDRIVE}/{CARPETA}/{SUB}/{nombre}/{origen.name}",
               "sha256": h0, "bytes": origen.stat().st_size, "hash_fijado_por": desc_rel or "manifiesto Fase 3",
               "accion": accion, "contiene_identificadores": True,
               "fecha_hora": dt.datetime.now().astimezone().isoformat()}
    for cat_p in (raiz / CARPETA / "CATALOGO_FUENTES.json", ROOT / "data/catalogo_fuentes/CATALOGO_FUENTES.json"):
        cat = json.loads(cat_p.read_text(encoding="utf-8"))
        lista = [e for e in cat.get("catalogo_privadas", []) if e["paso"] != entrada["paso"]]
        cat["catalogo_privadas"] = sorted(lista + [entrada], key=lambda e: int(e["paso"].split("/")[0]))
        cat_p.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(entrada, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

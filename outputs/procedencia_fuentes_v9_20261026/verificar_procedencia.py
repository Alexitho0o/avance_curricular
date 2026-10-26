"""Recuenta los hashes de todas las fuentes citadas por el diccionario activo (v9) y su edición anterior.

Estados: COINCIDE, DISTINTO, NO_EXISTE, NO_LEGIBLE (por ejemplo, archivo solo en la nube).
Solo lectura. Salidas agregadas por ruta; sin contenido de las fuentes ni identificadores.
Uso en Mac: python3 verificar_procedencia.py   (en otro entorno: --mapa '/Users/alexi/X=/ruta/local/X' ...)
"""
import argparse, collections, datetime as dt, hashlib, json, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def localizar(ruta, mapa):
    """Resuelve la ruta componente a componente comparando nombres en NFC (macOS guarda NFD)."""
    nfc = lambda x: unicodedata.normalize("NFC", x)
    ruta = nfc(ruta)
    for mac, loc in mapa:
        if ruta.startswith(nfc(mac)):
            base, resto = Path(loc), ruta[len(nfc(mac)):].lstrip("/")
            break
    else:
        base, resto = Path("/"), ruta.lstrip("/")
    if not base.exists():
        cand = [c for c in base.parent.iterdir() if nfc(c.name) == nfc(base.name)] if base.parent.exists() else []
        if not cand:
            return None
        base = cand[0]
    actual = base
    for parte in [x for x in resto.split("/") if x]:
        try:
            hijos = {nfc(c.name): c for c in actual.iterdir()}
        except OSError:
            return None
        if nfc(parte) not in hijos:
            return None
        actual = hijos[nfc(parte)]
    return actual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapa", action="append", default=[], help="prefijo_mac=prefijo_local")
    a = ap.parse_args()
    mapa = sorted((tuple(x.split("=", 1)) for x in a.mapa), key=lambda t: -len(t[0]))
    activo = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    d9 = json.loads((ROOT / activo["descriptor"]).read_text())
    d8 = json.loads((ROOT / d9["edicion_anterior"]["descriptor"]).read_text())
    citas = {}
    for origen, desc in (("v9.entradas_sha256", d9), ("v9.entradas_cierre_sha256", d9), ("v8.entradas_cierre_sha256", d8)):
        clave = origen.split(".", 1)[1]
        for ruta, h in desc.get(clave, {}).items():
            citas.setdefault(ruta, {"esperado": h, "citado_en": []})["citado_en"].append(origen)
            if citas[ruta]["esperado"] != h:
                citas[ruta]["conflicto_entre_descriptores"] = True
    for ruta, h in (("base_privada_v9", d9["base_privada"]), ("base_privada_v8", d8["base_privada"])):
        citas.setdefault(h["ruta"], {"esperado": h["sha256"], "citado_en": []})["citado_en"].append(ruta)
    filas = []
    for ruta, info in sorted(citas.items()):
        p = localizar(ruta, mapa)
        if p is None:
            estado, actual = "NO_EXISTE", None
        else:
            try:
                actual = sha(p)
                estado = "COINCIDE" if actual == info["esperado"] else "DISTINTO"
            except OSError:
                estado, actual = "NO_LEGIBLE", None
        nombre = Path(ruta).name.upper()
        tipo = ("DATOSDEALUMNOS" if "DATOSDEALUMNOS" in nombre else "PROMEDIOSDEALUMNOS" if "PROMEDIOSDEALUMNOS" in nombre
                else "BASE_PRIVADA" if nombre.endswith(".SQLITE") else "MATRICULA_SIES" if "MATR" in nombre else "OTRA")
        ubic = ("OneDrive" if "/CloudStorage/" in ruta else "Descargas" if "/Downloads/" in ruta else "Escritorio" if "/Desktop/" in ruta
                else "Privada" if "/.local/share/ipss/" in ruta else "Repositorio")
        filas.append({"ruta": ruta, "tipo": tipo, "ubicacion": ubic, "estado": estado, "sha256_esperado": info["esperado"],
                      "sha256_actual": actual, "citado_en": info["citado_en"], **({"conflicto": True} if info.get("conflicto_entre_descriptores") else {})})
    resumen = collections.Counter(f["estado"] for f in filas)
    por_tipo = collections.Counter((f["tipo"], f["estado"]) for f in filas)
    por_ubic = collections.Counter((f["ubicacion"], f["estado"]) for f in filas)
    out = {"clasificacion": "B fuentes; C verificación de integridad", "fecha_hora": dt.datetime.now().astimezone().isoformat(),
           "edicion_activa": d9["edicion"], "descriptor_sha256": activo["sha256"], "script_sha256": sha(Path(__file__)),
           "fuentes": len(filas), "resumen": dict(resumen),
           "por_tipo": {f"{t}|{e}": n for (t, e), n in sorted(por_tipo.items())},
           "por_ubicacion": {f"{u}|{e}": n for (u, e), n in sorted(por_ubic.items())},
           "detalle": filas}
    (Path(__file__).parent / "PROCEDENCIA_V9.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: out[k] for k in ("fuentes", "resumen", "por_tipo", "por_ubicacion")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

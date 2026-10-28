"""Copia (nunca mueve) las bases del proyecto de conciliación UMAS–SIES a una sola carpeta de OneDrive.

- Origen: fuentes de datos citadas por los descriptores del diccionario (activo y anterior) más las
  bases oficiales del repositorio (matrícula SIES 2007–2026, base MU, oferta, duración).
- Excluye resultados de trabajo (libros V5/V12) y bases privadas derivadas (SQLite, JSON con identificadores).
- Una copia por contenido (SHA-256); el catálogo registra todos los orígenes de cada copia.
- Verifica el hash de cada copia contra el origen y contra el hash citado. Idempotente: si la copia
  ya existe con el mismo hash, no se vuelve a copiar; nunca sobrescribe un archivo distinto.
Uso en Mac:  python3 consolidar_bases.py
"""
import argparse, csv, datetime as dt, hashlib, json, shutil, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ONEDRIVE = "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián"
DESTINO_MAC = ONEDRIVE + "/IPSS_CONCILIACION_UMAS_SIES_BASES"
GH = "/Users/alexi/Documents/GitHub"
EXTRA = [  # bases oficiales del repositorio o del Escritorio no citadas como entradas del diccionario
    "/Users/alexi/Desktop/Matricula_2007_2026_WEB_10_07_2026.csv",
    GH + "/avance_curricular/oferta_academica_2027/01_fuentes_oficiales/historico_comparativo_sies_162/20260817_161807_sies_historico_2010_2026/Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx",
    GH + "/avance_curricular/data/reglas_negocio/20261015/fuentes/Oferta_Academica_2010_al_2026_SIES_12_01_2026_WEB_E.csv.gz",
    GH + "/avance_curricular/data/DURACION_ESTUDIOS.tsv",
    GH + "/avance_curricular/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/MANIFEST_BASE_RETENCION_MU_2022_2026.json",
]
EXCLUIR = ("IPSS_CONCILIACION_CARRERAS_UMAS_SIES", "RETENCION_IPSS_DICCIONARIO_APLICADO", "oferta_v5_hoja3")
EXT = (".xlsx", ".xls", ".csv", ".gz", ".tsv")
nfc = lambda x: unicodedata.normalize("NFC", x)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def localizar(ruta, mapa):
    ruta = nfc(ruta)
    for mac, loc in mapa:
        if ruta.startswith(nfc(mac)):
            cur = Path(loc)
            for parte in [x for x in ruta[len(nfc(mac)):].split("/") if x]:
                try:
                    hijos = {nfc(c.name): c for c in cur.iterdir()}
                except OSError:
                    return None
                if nfc(parte) not in hijos:
                    return None
                cur = hijos[nfc(parte)]
            return cur
    p = Path(ruta)
    return p if p.exists() else None


def categoria(ruta):
    n = Path(ruta).name.upper()
    if n.startswith("MATRICULA_2007_2026"):
        return "01_SIES_MATRICULA_HISTORICA_2007_2026"
    if "DATOSDEALUMNOS" in n:
        return "03_UMAS_DATOSDEALUMNOS"
    if "PROMEDIOSDEALUMNOS" in n:
        return "04_UMAS_PROMEDIOSDEALUMNOS"
    if "OFERTA_ACADEMICA" in n or "DURACION_ESTUDIOS" in n:
        return "05_OFERTA_ACADEMICA_Y_DURACION"
    if "Indicadores Intermedios" in ruta:
        return "06_INDICADORES_ACADEMICOS_VRA"
    return "02_MATRICULA_UNIFICADA_Y_CARGAS_SIES"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapa", action="append", default=[], help="prefijo_mac=prefijo_local (solo fuera del Mac)")
    ap.add_argument("--plan", type=Path, help="Ampliación explícita por ruta/hash/categoría; conserva todo el catálogo anterior")
    a = ap.parse_args()
    if a.plan:
        ampliar_catalogo(a.plan)
        return
    mapa = sorted((tuple(x.split("=", 1)) for x in a.mapa), key=lambda t: -len(t[0]))
    destino = localizar(ONEDRIVE, mapa)
    if destino is None:
        sys.exit("ALTO: carpeta OneDrive no disponible.")
    destino = destino / "IPSS_CONCILIACION_UMAS_SIES_BASES"
    activo = json.loads((ROOT / "data/diccionario_sies_seguimiento/activo.json").read_text())
    d9 = json.loads((ROOT / activo["descriptor"]).read_text())
    d8 = json.loads((ROOT / d9["edicion_anterior"]["descriptor"]).read_text())
    citadas = {}
    for etiqueta, dic in (("v9.entradas_sha256", d9.get("entradas_sha256", {})), ("v8.entradas_cierre_sha256", d8.get("entradas_cierre_sha256", {})),
                          ("v9.entradas_cierre_sha256", d9.get("entradas_cierre_sha256", {}))):
        for r, h in dic.items():
            if r.startswith("/sessions/") or not r.lower().endswith(EXT) or any(x in r for x in EXCLUIR) or "/.local/share/ipss/" in r:
                continue
            citadas.setdefault(nfc(r), {"hash_citado": h, "citado_en": []})["citado_en"].append(etiqueta)
    for r in EXTRA:
        citadas.setdefault(nfc(r), {"hash_citado": None, "citado_en": []})["citado_en"].append("base_oficial_del_proyecto")

    por_hash, pendientes = {}, []
    for r, info in sorted(citadas.items()):
        p = localizar(r, mapa)
        if p is None:
            pendientes.append({"origen": r, "motivo": "NO_EXISTE"}); continue
        try:
            h = sha(p)
        except OSError:
            pendientes.append({"origen": r, "motivo": "SOLO_EN_LA_NUBE_NO_LEGIBLE", "bytes": p.stat().st_size}); continue
        if info["hash_citado"] and h != info["hash_citado"]:
            pendientes.append({"origen": r, "motivo": "HASH_DISTINTO_AL_CITADO", "sha256_actual": h}); continue
        e = por_hash.setdefault(h, {"sha256": h, "bytes": p.stat().st_size, "categoria": categoria(r), "origenes": []})
        e["origenes"].append({"ruta": r, "citado_en": info["citado_en"], "_local": str(p)})

    usados = {}
    catalogo = []
    for h, e in sorted(por_hash.items(), key=lambda kv: (kv[1]["categoria"], Path(kv[1]["origenes"][0]["ruta"]).name)):
        original = Path(e["origenes"][0]["ruta"]).name
        carpeta = destino / e["categoria"]; carpeta.mkdir(parents=True, exist_ok=True)
        sufijo = f"{Path(original).stem}__{h[:8]}{''.join(Path(original).suffixes)}"
        plano = carpeta / original
        ocupado = usados.get((e["categoria"], nfc(original).lower()))
        if plano.exists() and sha(plano) == h:
            nombre = original                     # ya hay una copia idéntica con el nombre original
        elif (ocupado and ocupado != h) or plano.exists() or (carpeta / sufijo).exists():
            nombre = sufijo                       # mismo nombre, otro contenido: se distingue por hash
        else:
            nombre = original
        usados[(e["categoria"], nfc(nombre).lower())] = h
        dst = carpeta / nombre
        accion = "YA_EXISTIA_IDENTICO"
        if dst.exists():
            if sha(dst) != h:
                sys.exit(f"ALTO: {dst} ya existe con otro contenido; no se sobrescribe.")
        else:
            tmp = carpeta / (nombre + ".copiando")
            shutil.copyfile(e["origenes"][0]["_local"], tmp)
            if sha(tmp) != h:
                sys.exit(f"ALTO: copia corrupta de {nombre}.")
            tmp.rename(dst)
            accion = "COPIADO"
        if sha(e["origenes"][0]["_local"]) != h:
            sys.exit(f"ALTO: el origen de {nombre} cambió durante la copia.")
        catalogo.append({"categoria": e["categoria"], "archivo": nombre,
                         "ruta_consolidada": f"{DESTINO_MAC}/{e['categoria']}/{nombre}",
                         "sha256": h, "bytes": e["bytes"], "accion": accion,
                         "hash_copia_igual_origen": True,
                         "origenes": [{k: v for k, v in o.items() if not k.startswith("_")} for o in e["origenes"]]})

    ahora = dt.datetime.now().astimezone().isoformat()
    cat = {"clasificacion": "B fuentes copiadas; C verificación de integridad",
           "fecha_hora": ahora, "carpeta_consolidada": DESTINO_MAC,
           "regla": "Copia sin mover ni modificar el original. El SHA-256 identifica el contenido: la copia tiene el mismo hash que el origen; lo que cambia es la ruta.",
           "diccionario_activo": {"descriptor": activo["descriptor"], "sha256": activo["sha256"]},
           "archivos": len(catalogo), "bytes_total": sum(c["bytes"] for c in catalogo),
           "pendientes": pendientes, "catalogo": catalogo,
           "excluidos_por_regla": ["libros de trabajo V5/V12 (resultados, no bases)",
                                   "bases privadas derivadas en ~/.local/share/ipss (SQLite y JSON con identificadores)"],
           "script_sha256": sha(Path(__file__))}
    previo = destino / "CATALOGO_FUENTES.json"
    if previo.exists():  # conserva la sección de bases privadas copiadas paso a paso
        cat["catalogo_privadas"] = json.loads(previo.read_text(encoding="utf-8")).get("catalogo_privadas", [])
    texto = json.dumps(cat, ensure_ascii=False, indent=1)
    (destino / "CATALOGO_FUENTES.json").write_text(texto, encoding="utf-8")
    repo_cat = ROOT / "data/catalogo_fuentes/CATALOGO_FUENTES.json"
    repo_cat.parent.mkdir(parents=True, exist_ok=True)
    repo_cat.write_text(texto, encoding="utf-8")
    with open(destino / "CATALOGO_FUENTES.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["CATEGORIA", "ARCHIVO", "SHA256", "BYTES", "ORIGEN_PRINCIPAL", "N_ORIGENES", "CITADO_EN"])
        for c in catalogo:
            w.writerow([c["categoria"], c["archivo"], c["sha256"], c["bytes"], c["origenes"][0]["ruta"], len(c["origenes"]),
                        " | ".join(sorted({x for o in c["origenes"] for x in o["citado_en"]}))])
        for p in pendientes:
            w.writerow(["PENDIENTE", Path(p["origen"]).name, "", p.get("bytes", ""), p["origen"], "", p["motivo"]])
    print(json.dumps({"archivos": len(catalogo), "copiados": sum(c["accion"] == "COPIADO" for c in catalogo),
                      "ya_existian": sum(c["accion"] != "COPIADO" for c in catalogo),
                      "bytes_total": cat["bytes_total"], "pendientes": [(Path(p["origen"]).name, p["motivo"]) for p in pendientes],
                      "por_categoria": {k: sum(1 for c in catalogo if c["categoria"] == k) for k in sorted({c["categoria"] for c in catalogo})}},
                     ensure_ascii=False, indent=1))


def ampliar_catalogo(plan_path):
    """Amplía copias autorizadas sin reconstruir ni truncar el catálogo vigente."""
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    repo = ROOT / 'data/catalogo_fuentes'
    cat = json.loads((repo / 'CATALOGO_FUENTES.json').read_text(encoding='utf-8'))
    destino = localizar(cat['carpeta_consolidada'], [(ONEDRIVE, ONEDRIVE)])
    if destino is None: raise FileNotFoundError('Destino consolidado no disponible')
    registros = {x['sha256']: x for x in cat['catalogo']}
    operaciones = []
    for item in plan['copias']:
        src = Path(item['origen']); expected = item['sha256']
        if sha(src) != expected: raise ValueError('Origen con hash distinto: '+src.name)
        dst = destino / item['categoria'] / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if sha(dst) != expected: raise ValueError('Destino distinto; no se sobrescribe: '+dst.name)
            accion = 'YA_EXISTIA_IDENTICO'
        else:
            with dst.open('xb') as fout, src.open('rb') as fin: shutil.copyfileobj(fin, fout)
            accion = 'COPIADO'
        if sha(dst) != expected or sha(src) != expected: raise ValueError('Integridad de copia no confirmada')
        old = registros.get(expected)
        origenes = list(old.get('origenes', [])) if old else []
        if not any(nfc(o['ruta'])==nfc(str(src)) for o in origenes): origenes.append({'ruta':str(src),'citado_en':['matriz_cuadratura_totales_20261028']})
        record = {'categoria':item['categoria'],'archivo':dst.name,'ruta_consolidada':str(dst),'sha256':expected,'bytes':dst.stat().st_size,'accion':accion,'hash_copia_igual_origen':True,'origenes':origenes,'datos_personales':item['datos_personales'],'descripcion':item['descripcion']}
        if old and nfc(old['ruta_consolidada'])!=nfc(str(dst)):
            record['otras_copias_conservadas'] = old.get('otras_copias_conservadas',[])+[old['ruta_consolidada']]
        elif old and old.get('otras_copias_conservadas'):
            record['otras_copias_conservadas'] = old['otras_copias_conservadas']
        registros[expected] = record
        operaciones.append({'origen':str(src),'destino':str(dst),'sha256':expected,'accion':accion,'datos_personales':item['datos_personales']})
    cat['catalogo'] = sorted(registros.values(),key=lambda x:(x['categoria'],x['archivo']))
    cat['archivos'] = len(cat['catalogo']); cat['bytes_total'] = sum(x['bytes'] for x in cat['catalogo'])
    cat['referencias_nacionales_sin_copia'] = plan['referencias_nacionales_sin_copia']
    cat['ampliacion_matriz_20261028'] = {'plan_sha256':sha(plan_path),'script_sha256':sha(Path(__file__)),'operaciones':operaciones}
    texto = json.dumps(cat,ensure_ascii=False,indent=1)+'\n'
    for p in (repo/'CATALOGO_FUENTES.json',destino/'CATALOGO_FUENTES.json'): p.write_text(texto,encoding='utf-8')
    import io
    stream=io.StringIO(newline=''); writer=csv.writer(stream,delimiter=';')
    writer.writerow(['CATEGORIA','ARCHIVO','SHA256','BYTES','ORIGEN_PRINCIPAL','RUTA_CONSOLIDADA','DATOS_PERSONALES'])
    for x in cat['catalogo']: writer.writerow([x['categoria'],x['archivo'],x['sha256'],x['bytes'],x['origenes'][0]['ruta'],x['ruta_consolidada'],x.get('datos_personales','desconocido')])
    contenido=stream.getvalue().encode('utf-8-sig')
    for p in (repo/'CATALOGO_FUENTES.csv',destino/'CATALOGO_FUENTES.csv'): p.write_bytes(contenido)
    assert sha(repo/'CATALOGO_FUENTES.json')==sha(destino/'CATALOGO_FUENTES.json')
    assert sha(repo/'CATALOGO_FUENTES.csv')==sha(destino/'CATALOGO_FUENTES.csv')
    print(json.dumps({'copias':len(operaciones),'archivos_catalogados':cat['archivos'],'catalogos_identicos':True},ensure_ascii=False))

if __name__ == "__main__":
    main()

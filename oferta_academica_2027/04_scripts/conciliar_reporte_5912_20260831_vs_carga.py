#!/usr/bin/env python3
import csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "09_respaldo/reportes_pes_validados/20260831_reporte_5912_etapa1/reporte_dinamico_5912_2026-08-31_12:34:51.csv"
LOAD = ROOT / "07_resultados/cargas_congeladas/20260817_155153_etapa1_areas_vigencia_fecha/CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv"
PRECARGA = ROOT / "02_precarga_pes/reporte_dinamico_5913_2026-08-12_08:22:23.csv"
OUT = ROOT / "06_validaciones/conciliacion_5912_20260831_vs_carga"
NO_LOAD = {"CODIGO_IES_NUM", "CANTIDAD_MATRICULA_DFE", "CANTIDAD_BENEFICIO_DFE"}
KEY = ["COD_SEDE", "COD_CARRERA", "MODALIDAD", "COD_JORNADA", "VERSION"]

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.reader(f, delimiter=";"))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pre = rows(PRECARGA); expected = [x for x in pre[0] if x not in NO_LOAD]
    rep = rows(REPORT); rh = rep[0]; rdata = [[r[rh.index(x)] for x in expected] for r in rep[1:]]
    load = rows(LOAD)
    pos = [expected.index(x) for x in KEY]
    make_key = lambda r: tuple(r[i] for i in pos)
    rmap = {make_key(r): (i, r) for i, r in enumerate(rdata, 1)}
    lmap = {make_key(r): (i, r) for i, r in enumerate(load, 1)}
    diffs = []
    for key in sorted(set(rmap) & set(lmap)):
        ri, rr = rmap[key]; li, lr = lmap[key]
        for i, field in enumerate(expected):
            if rr[i] != lr[i]: diffs.append(["|".join(key), li, ri, field, lr[i], rr[i]])
    only_load = sorted(set(lmap) - set(rmap)); only_report = sorted(set(rmap) - set(lmap))
    def sums(data, field):
        i = expected.index(field); return sum(float((r[i] or "0").replace(",", ".")) for r in data)
    vig = expected.index("VIGENCIA_CARRERA")
    detail = OUT / "DETALLE_CONCILIACION_5912_20260831_VS_CARGA.tsv"
    with detail.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(["llave_sies","fila_carga","fila_5912","campo","valor_carga","valor_5912"]); w.writerows(diffs)
    summary = {
        "proceso":"SIES Oferta Academica-Acceso 2027", "etapa":"Etapa 1 - Oferta Academica Vigente Editada TP Adscritas",
        "reporte_5912":{"ruta":str(REPORT),"sha256":sha(REPORT),"filas":len(rdata),"columnas":len(rh),"columna_extra":[x for x in rh if x not in expected]},
        "carga_comparada":{"ruta":str(LOAD),"sha256":sha(LOAD),"filas":len(load),"columnas":len(expected)},
        "metodo":"Conciliacion por llave COD_SEDE+COD_CARRERA+MODALIDAD+COD_JORNADA+VERSION; comparacion campo a campo de las 48 columnas cargables.",
        "resultado":{"llaves_solo_carga":len(only_load),"llaves_solo_5912":len(only_report),"diferencias_celda":len(diffs),"filas_con_diferencias":len({x[0] for x in diffs}),"diferencias_por_campo":dict(Counter(x[3] for x in diffs)),"identico":not diffs and not only_load and not only_report},
        "vacantes":{"carga":{"primer_semestre":sums(load,"VACANTES_PRIMER_SEMESTRE"),"segundo_semestre":sums(load,"VACANTES_SEGUNDO_SEMESTRE"),"total":sums(load,"VACANTES_PRIMER_SEMESTRE")+sums(load,"VACANTES_SEGUNDO_SEMESTRE")},"reporte_5912":{"primer_semestre":sums(rdata,"VACANTES_PRIMER_SEMESTRE"),"segundo_semestre":sums(rdata,"VACANTES_SEGUNDO_SEMESTRE"),"total":sums(rdata,"VACANTES_PRIMER_SEMESTRE")+sums(rdata,"VACANTES_SEGUNDO_SEMESTRE")}},
        "vigencia":{"carga":dict(Counter(r[vig] for r in load)),"reporte_5912":dict(Counter(r[vig] for r in rdata))},
    }
    sp = OUT / "RESUMEN_CONCILIACION_5912_20260831_VS_CARGA.json"; sp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest = REPORT.parent / "MANIFIESTO_5912_20260831.tsv"; manifest.write_text("clasificacion\tarchivo\tbytes\tsha256\nreporte_validado_pes_5912\t{}\t{}\t{}\n".format(REPORT.name,REPORT.stat().st_size,sha(REPORT)),encoding="utf-8")
    readme = REPORT.parent / "README_GOBERNANZA_5912_20260831.md"; readme.write_text("# Reporte 5912 validado - 31 de agosto de 2026\n\nReporte SIES gobernado sin modificar. Conciliado contra la carga congelada de Etapa 1 por llave SIES y por las 48 columnas cargables. Ver resultados en `"+str(sp)+"`.\n",encoding="utf-8")
    print(json.dumps({"reporte":str(REPORT),"sha256":sha(REPORT),"filas":len(rdata),"columnas":len(rh),"llaves_coincidentes":len(set(rmap)&set(lmap)),"diferencias_celda":len(diffs),"diferencias_por_campo":dict(Counter(x[3] for x in diffs)),"vacantes_carga":summary["vacantes"]["carga"],"vacantes_5912":summary["vacantes"]["reporte_5912"],"vigencia_carga":summary["vigencia"]["carga"],"vigencia_5912":summary["vigencia"]["reporte_5912"],"resumen":str(sp),"detalle":str(detail)},ensure_ascii=False,indent=2))
if __name__ == "__main__": main()

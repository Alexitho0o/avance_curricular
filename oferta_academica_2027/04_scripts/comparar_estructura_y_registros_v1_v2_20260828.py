# -*- coding: utf-8 -*-
# Comparacion estructural y registro por registro: v1 (entrega_01) vs v2 (entrega_02, rector_v2)
import json, os, re, unicodedata
import openpyxl

BASE = os.path.expanduser("~/mnt/avance_curricular/oferta_academica_2027")
V1 = os.path.join(BASE, "03_fuentes_institucionales/entregas_docencia/20260827_etapa2_entrega_01/Oferta 2027 Etapa2_prueba_1.xlsx")
V2 = os.path.join(BASE, "03_fuentes_institucionales/entregas_docencia/20260828_etapa2_entrega_02/Oferta 2027 Etapa2_rector_v2.xlsx")
OUT = os.path.join(BASE, "06_validaciones")
STAMP = "20260828"

# Estructura oficial de referencia (48 columnas, Anexo2 pag.35-41) ya confirmada en Fase 3 v1
OFICIAL_48 = ["COD_SEDE","NOMBRE_SEDE","COD_CARRERA","NOMBRE_CARRERA","MODALIDAD","COD_JORNADA","VERSION",
 "COD_TIPO_PLAN_CARRERA","CARACTERISTICAS_TIPO_PLAN","DURACION_ESTUDIOS","DURACION_TITULACION","DURACION_TOTAL",
 "REGIMEN","DURACION_REGIMEN","NOMBRE_TITULO","COD_NIVEL_GLOBAL","COD_NIVEL_CARRERA","ANIO_INICIO","ACREDITACION",
 "REQUISITO_INGRESO","SEMESTRES_RECONOCIDOS","AREA_ACTUAL","AREA_ADMIN_DERECHO","AREA_AGRI_SILVI_PESCA_VET",
 "AREA_ARTES_HUMANIDADES","AREA_CIENCIAS_NAT_MAT_ESTAD","AREA_CS_SOCIAL_PERIODISMO_INFO","AREA_EDUCACION",
 "AREA_INGE_INDUSTRIA_CONSTRUC","AREA_SALUD_BIENESTAR","AREA_SERVICIOS","AREA_TECNO_INFO_COMUNICA",
 "VACANTES_PRIMER_SEMESTRE","VACANTES_SEGUNDO_SEMESTRE","FECHA_ADMISION_INICIAL","ENLACE_INFO_PROGRAMA",
 "LICENCIA_ENS_MEDIA","NOTAS_ENS_MEDIA","PROMEDIO_MIN_ENS_MEDIA","RECONOCIMIENTOS_APREN_PREVIOS",
 "EXPERIENCIA_LABORAL","MAIL_DIFUSION_CARRERA","FORMATO_VALOR","VALOR_MATRICULA_ANUAL","COSTO_TITULACION",
 "VALOR_CERTIFICADO_DIPLOMA","ARANCEL_ANUAL","VIGENCIA_CARRERA"]

def norm(s):
    if s is None: return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s)

def load(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[wb.sheetnames[0]]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column+1)]
    rows = []
    empty_trailing = []
    for r in range(2, ws.max_row+1):
        vals = [ws.cell(row=r, column=c).value for c in range(1, ws.max_column+1)]
        if all(v is None for v in vals):
            empty_trailing.append(r)
            continue
        row = dict(zip(headers, vals))
        row["_fila_excel"] = r
        rows.append(row)
    return {"sheet": wb.sheetnames[0], "headers": headers, "max_row": ws.max_row, "max_col": ws.max_column,
            "rows": rows, "filas_vacias": empty_trailing}

v1 = load(V1)
v2 = load(V2)

# --- comparacion estructural ---
h1, h2 = v1["headers"], v2["headers"]
agregados = [h for h in h2 if h not in h1]
eliminados = [h for h in h1 if h not in h2]
comunes_orden_v1 = [h for h in h1 if h in h2]
comunes_orden_v2 = [h for h in h2 if h in h1]
orden_cambiado = comunes_orden_v1 != comunes_orden_v2

primeras48_v1 = h1[:48]
primeras48_v2 = h2[:48]
coincide_48_v1 = primeras48_v1 == OFICIAL_48
coincide_48_v2 = primeras48_v2 == OFICIAL_48

# duplicados internos v2 por llave diagnostica
def key_diag(row):
    return (norm(row.get("NOMBRE_SEDE")), norm(row.get("NOMBRE_CARRERA")), str(row.get("MODALIDAD")), str(row.get("COD_JORNADA")), str(row.get("COD_TIPO_PLAN_CARRERA")), str(row.get("COD_NIVEL_CARRERA")), norm(row.get("NOMBRE_TITULO")))

dup_map_v2 = {}
for row in v2["rows"]:
    dup_map_v2.setdefault(key_diag(row), []).append(row["_fila_excel"])
duplicados_internos_v2 = {str(k): v for k, v in dup_map_v2.items() if len(v) > 1}

estructura = {
    "v1": {"hoja": v1["sheet"], "filas_totales": v1["max_row"], "registros_reales": len(v1["rows"]), "columnas_totales": v1["max_col"], "filas_vacias_finales": v1["filas_vacias"]},
    "v2": {"hoja": v2["sheet"], "filas_totales": v2["max_row"], "registros_reales": len(v2["rows"]), "columnas_totales": v2["max_col"], "filas_vacias_finales": v2["filas_vacias"]},
    "encabezados_agregados_en_v2": agregados,
    "encabezados_eliminados_en_v2": eliminados,
    "cambio_de_orden_en_columnas_comunes": orden_cambiado,
    "primeras_48_columnas_v1_coinciden_con_anexo2_pag35_41": coincide_48_v1,
    "primeras_48_columnas_v2_coinciden_con_anexo2_pag35_41": coincide_48_v2,
    "columna_sector_ipss_en_v1": "SECTOR IPSS" in h1,
    "columna_sector_ipss_en_v2": "SECTOR IPSS" in h2,
    "duplicados_internos_v2_por_llave_diagnostica": duplicados_internos_v2,
    "nota_estructura_oficial": "La coincidencia con la tabla del Anexo 2 (pag.35-41) del instructivo NO equivale a confirmar la estructura oficial PES: sigue sin existir un archivo de estructura descargado directamente de PES. Estado: FUENTE_INSTITUCIONAL_PENDIENTE_DE_CONFIRMACION_ESTRUCTURAL para ambas versiones.",
}

# --- comparacion registro por registro ---
def norm_val(v):
    # normaliza formato sin alterar el valor semantico (espacios, mayus/minus para texto, tipo numerico)
    if v is None:
        return None
    if isinstance(v, str):
        return norm(v)
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v

CAMPOS_LLAVE = ["COD_SEDE","NOMBRE_SEDE","NOMBRE_CARRERA","MODALIDAD","COD_JORNADA","COD_TIPO_PLAN_CARRERA","COD_NIVEL_CARRERA","NOMBRE_TITULO"]
CAMPOS_COMPARABLES = [h for h in OFICIAL_48 if h not in ("COD_CARRERA",)]

idx_v1 = {}
for row in v1["rows"]:
    k = tuple(norm_val(row.get(c)) for c in CAMPOS_LLAVE)
    idx_v1.setdefault(k, []).append(row)
idx_v2 = {}
for row in v2["rows"]:
    k = tuple(norm_val(row.get(c)) for c in CAMPOS_LLAVE)
    idx_v2.setdefault(k, []).append(row)

detalle_registros = []
resumen_reg = {}

matched_v1_keys = set()
for k, rows2 in idx_v2.items():
    rows1 = idx_v1.get(k)
    for row2 in rows2:
        fila2 = row2["_fila_excel"]
        if rows1:
            matched_v1_keys.add(k)
            row1 = rows1[0]
            cambios_valor = []
            cambios_formato = []
            for c in CAMPOS_COMPARABLES:
                a, b = row1.get(c), row2.get(c)
                na, nb = norm_val(a), norm_val(b)
                if na != nb:
                    cambios_valor.append(f"{c}: '{a}' -> '{b}'")
                elif a != b:
                    cambios_formato.append(f"{c}: '{a}' -> '{b}' (solo formato)")
            if cambios_valor:
                clasif = "REGISTRO_MODIFICADO"
            else:
                clasif = "SIN_CAMBIOS"
            detalle_registros.append({
                "fila_v1": row1["_fila_excel"], "fila_v2": fila2, "carrera": row2.get("NOMBRE_CARRERA"),
                "sede": row2.get("NOMBRE_SEDE"), "clasificacion": clasif,
                "cambios_de_valor": "; ".join(cambios_valor), "cambios_de_formato": "; ".join(cambios_formato),
            })
        else:
            detalle_registros.append({
                "fila_v1": None, "fila_v2": fila2, "carrera": row2.get("NOMBRE_CARRERA"),
                "sede": row2.get("NOMBRE_SEDE"), "clasificacion": "REGISTRO_NUEVO",
                "cambios_de_valor": "", "cambios_de_formato": "",
            })

for k, rows1 in idx_v1.items():
    if k not in matched_v1_keys:
        for row1 in rows1:
            detalle_registros.append({
                "fila_v1": row1["_fila_excel"], "fila_v2": None, "carrera": row1.get("NOMBRE_CARRERA"),
                "sede": row1.get("NOMBRE_SEDE"), "clasificacion": "REGISTRO_ELIMINADO",
                "cambios_de_valor": "", "cambios_de_formato": "",
            })

# --- segunda pasada: match blando (COD_SEDE+NOMBRE_CARRERA+NOMBRE_TITULO) para pares que
# cambiaron un campo de la llave (modalidad/jornada/tipo_plan/nivel/sede), evitando falsos
# pares nuevo+eliminado cuando en realidad es el mismo programa con un atributo modificado ---
nuevos = [d for d in detalle_registros if d["clasificacion"] == "REGISTRO_NUEVO"]
eliminados = [d for d in detalle_registros if d["clasificacion"] == "REGISTRO_ELIMINADO"]

def soft_key(row):
    return (norm_val(row.get("COD_SEDE")), norm_val(row.get("NOMBRE_CARRERA")), norm_val(row.get("NOMBRE_TITULO")))

rows2_by_fila = {r["_fila_excel"]: r for r in v2["rows"]}
rows1_by_fila = {r["_fila_excel"]: r for r in v1["rows"]}

reclasificados_filas_v2 = set()
reclasificados_filas_v1 = set()
for dn in nuevos:
    row2 = rows2_by_fila[dn["fila_v2"]]
    sk2 = soft_key(row2)
    for de in eliminados:
        if de["fila_v1"] in reclasificados_filas_v1:
            continue
        row1 = rows1_by_fila[de["fila_v1"]]
        if soft_key(row1) == sk2:
            cambios_valor = []
            cambios_formato = []
            for c in CAMPOS_COMPARABLES:
                a, b = row1.get(c), row2.get(c)
                na, nb = norm_val(a), norm_val(b)
                if na != nb:
                    cambios_valor.append(f"{c}: '{a}' -> '{b}'")
                elif a != b:
                    cambios_formato.append(f"{c}: '{a}' -> '{b}' (solo formato)")
            dn["fila_v1"] = de["fila_v1"]
            dn["clasificacion"] = "REGISTRO_MODIFICADO"
            dn["cambios_de_valor"] = "; ".join(cambios_valor) + " [reclasificado: coincide por sede+carrera+titulo, cambio en llave diagnostica (modalidad/jornada/tipo_plan/nivel)]"
            dn["cambios_de_formato"] = "; ".join(cambios_formato)
            reclasificados_filas_v2.add(dn["fila_v2"])
            reclasificados_filas_v1.add(de["fila_v1"])
            break

detalle_registros = [d for d in detalle_registros if not (d["clasificacion"] == "REGISTRO_ELIMINADO" and d["fila_v1"] in reclasificados_filas_v1)]

resumen_reg = {}
for d in detalle_registros:
    resumen_reg[d["clasificacion"]] = resumen_reg.get(d["clasificacion"], 0) + 1


for d in detalle_registros:
    resumen_reg[d["clasificacion"]] = resumen_reg.get(d["clasificacion"], 0) + 1

out = {"estructura": estructura, "resumen_registros": resumen_reg, "detalle_registros": detalle_registros}
json_path = os.path.join(OUT, f"COMPARACION_ESTRUCTURAL_Y_REGISTROS_V1_VS_V2_{STAMP}.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)

tsv_path = os.path.join(OUT, f"COMPARACION_REGISTROS_V1_VS_V2_{STAMP}.tsv")
cols = ["fila_v1","fila_v2","sede","carrera","clasificacion","cambios_de_valor","cambios_de_formato"]
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for d in detalle_registros:
        f.write("\t".join(str(d.get(c,"")).replace("\t"," ").replace("\n"," ") for c in cols) + "\n")

print("ESTRUCTURA:")
for k, v in estructura.items():
    print(" ", k, "=", v)
print("RESUMEN REGISTROS:", resumen_reg)
print("JSON:", json_path)
print("TSV:", tsv_path)

"""Conciliación agregada 2026 con el cierre del 30-jul; no asigna versiones.

Reutiliza el puente publicado y la lectura agregada de Fase2. No abre fuentes
individuales ni modifica fuentes, libros, reglas o denominadores de retención.
"""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

ROOT = Path('/Users/alexi/Documents/GitHub/avance_curricular')
OUT = Path(__file__).resolve().parent
PUENTE = ROOT/'procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv'
PMAN = PUENTE.with_suffix('.manifest.json')
JUL = ROOT/'outputs/lectura_independiente_libro_mu2026/20260730_232242'
CRUCE = JUL/'CRUCE_66_CODIGOS.csv'
FORMS = JUL/'INVENTARIO_FORMULAS.csv'
AUD = ROOT/'outputs/auditoria_integral_publicacion_vs_pregrado_posgrado_2026/20260730_223007'
AM = AUD/'MANIFEST_AUDITORIA_INTEGRAL_MU2026_PUBLICACION_PREGRADO_POSGRADO_20260730_223007.json'
CLOSE = ROOT/'outputs/cierre_gobernado_auditoria_integral_mu2026/20260730_233407/CIERRE_GOBERNADO_AUDITORIA_MU2026_20260730_233407/02_CONTROL_Y_TRAZABILIDAD'
NEW = ROOT/'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/DETALLE_CONCILIACION.csv'
RESULT = NEW.with_name('RESULTADOS.json')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read_csv(p, delimiter=','):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=delimiter))
def integer(v): return int(float(v)) if str(v).strip() else 0
def save(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def export(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)

assert NEW.exists() and RESULT.exists(), 'Esperar salida agregada de conciliación; no duplicar lectura individual.'
paths=[PUENTE,PMAN,CRUCE,FORMS,AM,CLOSE/'ACTA_CIERRE_GOBERNADO_MU2026.txt',
       CLOSE/'MANIFEST_CIERRE_GOBERNADO_MU2026.json',NEW,RESULT,
       ROOT/'procesos/caracterizacion/gobernanza/sies/MATRICULA_2007_2026.manifest.json']
hashes={str(p):sha(p) for p in paths}
pm=json.loads(PMAN.read_text());am=json.loads(AM.read_text());newresult=json.loads(RESULT.read_text())
assert sha(PUENTE)==pm['salidas']['csv_sha256']
bridge=[r for r in read_csv(PUENTE) if r['ANIO']=='2026']
old={r['CODIGO']:r for r in read_csv(CRUCE,';')}
new={r['CODIGO_COMPLETO']:r for r in read_csv(NEW,';') if r['ANIO']=='2026'}
assert len(bridge)==len(old)==len(new)==66
assert {r['CODIGO_CARRERA_CSV'] for r in bridge}==set(old)==set(new)
forms=read_csv(FORMS,';')
formula=next(r for r in forms if r['HOJA']=='07_PREGRADO_COMPLETO' and r['CELDA']=='AM7')
assert formula['FORMULA']=='=IF(OR([@VIG]="1",[@VIG]="2"),"SI","NO")'
details=[]
for r in bridge:
    code=r['CODIGO_CARRERA_CSV'];o=old[code];n=new[code]
    pub=integer(r['TOTAL_MATRICULA_CSV']);total=integer(r['BASE_TOTAL_FILAS']);v1=integer(r['BASE_VIG1'])
    assert (pub,total,v1)==(integer(n['CSV_TOTAL_ESTRUCTURAL_UNION']),integer(n['MU_TOTAL_ESTRUCTURAL_UNION']),integer(n['MU_VIG1_ESTRUCTURAL_UNION']))
    assert pub==integer(o['PUBLICACION'])
    post=r['NIVEL_GLOBAL']=='Postítulo'
    if not post: assert v1==integer(o['INSTITUCIONAL'])
    details.append({'ANIO':2026,'CODIGO_COMPLETO':code,'COD_CAR':integer(r['COD_CAR']),
        'CARRERA':r['NOMBRE_CARRERA'],'NIVEL_CSV':r['NIVEL_GLOBAL'],
        'CSV_PUBLICACION':pub,'CIERRE_JULIO_PUBLICACION':integer(o['PUBLICACION']),
        'MU_TOTAL_FILAS':total,'MU_VIG0':integer(n['MU_VIG0_FILAS']),
        'MU_VIG1':v1,'MU_VIG2':integer(n['MU_VIG2_FILAS']),
        'MU_VIG_OTROS':integer(n['MU_VIG_OTROS_FILAS']),
        'INSTITUCIONAL_CIERRE_JULIO':integer(o['INSTITUCIONAL']),
        'DIF_PUBLICACION_MU_VIG1':pub-v1,'DIF_CIERRE_JULIO':integer(o['DIFERENCIA']),
        'ESTADO_CIERRE_JULIO':o['ESTADO'],
        'ESTADO_ACTUAL':'FUERA_ALCANCE_BASE_PREGRADO' if post else 'BRECHA_MISMO_CODIGO_CIERRE_JULIO' if pub!=v1 else 'COINCIDE_AGREGADO',
        'CAUSA':'Diferencia de alcance comprobada: Postítulo está en fuente separada del cierre, no en BASE pregrado.' if post else 'Pendiente: coincidencia de brecha con julio no acredita causa ni identidad.' if pub!=v1 else 'Igualdad de conteos; no prueba equivalencia de todas las personas.',
        'CLASIFICACION':'B/C; E causa pendiente' if pub!=v1 and not post else 'B/C',
        'LOCALIZADOR_PUENTE':'ANIO=2026 + CODIGO_CARRERA_CSV='+code,
        'LOCALIZADOR_JULIO':'CODIGO='+code,
        'LOCALIZADOR_ACTUAL':'ANIO=2026 + CODIGO_COMPLETO='+code})
pre=[r for r in details if r['NIVEL_CSV']=='Pregrado'];post=[r for r in details if r['NIVEL_CSV']=='Postítulo']
assert len(pre)==63 and len(post)==3
assert sum(r['MU_TOTAL_FILAS'] for r in pre)==4105
assert sum(r['MU_VIG0'] for r in pre)==960
assert sum(r['MU_VIG1'] for r in pre)==3145
assert sum(r['MU_VIG2'] for r in pre)==sum(r['MU_VIG_OTROS'] for r in pre)==0
assert sum(r['CSV_PUBLICACION'] for r in pre)==3371
assert sum(r['CSV_PUBLICACION'] for r in post)==sum(r['INSTITUCIONAL_CIERRE_JULIO'] for r in post)==54
assert sum(r['DIF_CIERRE_JULIO'] for r in details)==226
assert sum(r['DIF_PUBLICACION_MU_VIG1'] for r in details)==280
assert sum(max(r['DIF_CIERRE_JULIO'],0) for r in details)==228
assert sum(min(r['DIF_CIERRE_JULIO'],0) for r in details)==-2
assert sum(r['DIF_CIERRE_JULIO']!=0 for r in details)==48

groups=defaultdict(list)
for r in pre:groups[r['COD_CAR']].append(r)
careers=[]
for c,rows in sorted(groups.items()):
    p=sum(r['CSV_PUBLICACION'] for r in rows);v=sum(r['MU_VIG1'] for r in rows)
    pos=sum(max(r['DIF_CIERRE_JULIO'],0) for r in rows);neg=sum(min(r['DIF_CIERRE_JULIO'],0) for r in rows)
    careers.append({'ANIO':2026,'COD_CAR':c,'CARRERA':rows[0]['CARRERA'],
        'CODIGOS_COMPLETOS':len(rows),'PUBLICACION':p,'MU_VIG1':v,'DIFERENCIA_NETA':p-v,
        'DIFERENCIAS_POSITIVAS':pos,'DIFERENCIAS_NEGATIVAS':neg,
        'CODIGOS_CON_DIFERENCIA':sum(r['DIF_CIERRE_JULIO']!=0 for r in rows),
        'COMPENSACION_NETO_CERO':p==v and pos>0 and neg<0,
        'CLASIFICACION':'B/C; E causa de diferencias no acreditada',
        'INTERPRETACION':'Suma por carrera; no demuestra reclasificación de jornada o versión individual.'})
assert len(careers)==32 and sum(r['DIFERENCIA_NETA']!=0 for r in careers)==27
assert {r['COD_CAR'] for r in careers if r['COMPENSACION_NETO_CERO']}=={6,79}

sources=[]
for s in am['fuentes']:
    if s['ID_FUENTE'] in ['PUB2026','PRE_CSV','PRE_XLSX','POS_CSV','POS_TIT']:
        sources.append({'id':s['ID_FUENTE'],'ruta_o_referencia':s['RUTA'],'origen':s['ORIGEN'],
            'sha256_reportado_manifest_julio':s['SHA256'],'blob_si_corresponde':s['BLOB'],
            'hoja':s['HOJA'],'filas':s['FILAS_DATOS'],'columnas':s['COLUMNAS'],
            'verificacion_actual':'Se reutiliza manifiesto y cruce agregados; no se relee ni materializa fuente individual histórica.'})
claims=[
 {'clase':'B/C','hallazgo':'MU pregrado 2026 contiene4105 filas:3145 VIG1+960 VIG0; VIG2 y otros son0.','evidencia':str(NEW),'localizador':'ANIO=2026; suma MU_TOTAL_FILAS/MU_VIG0_FILAS/MU_VIG1_FILAS/MU_VIG2_FILAS'},
 {'clase':'C','hallazgo':'El comparador de julio acepta VIG1 o2; como no hay VIG2, coincide con filtrar VIG1. No implica equivalencia universal de ambos criterios.','evidencia':str(FORMS),'localizador':'07_PREGRADO_COMPLETO!AM7; 11_RESUMEN_POR_CODIGO!L5'},
 {'clase':'B/C','hallazgo':'Los66 códigos reproducen publicación de julio;63 pregrado reproducen institucional exactamente. No es solo igualdad del neto226.','evidencia':str(CRUCE),'localizador':'Todas las66 filas comparadas por CODIGO con puente y conciliación actual'},
 {'clase':'B/C','hallazgo':'Tres Postítulos suman54; el cierre usa fuente propia de21 columnas. Los ceros en BASE pregrado son ausencia de alcance, no54 estudiantes faltantes.','evidencia':str(AM),'localizador':'fuentes POS_CSV/POS_TIT; CRUCE códigos C53J3V1,C66J4V1,C70J4V1'},
 {'clase':'B/C','hallazgo':'48 códigos pregrado difieren:46 positivos suman228 y2 negativos suman−2; neto226.','evidencia':str(CRUCE),'localizador':'DIFERENCIA; niveles PREGRADO'},
 {'clase':'B/C/E','hallazgo':'27 de32 carreras tienen diferencia neta; cinco neto0, pero C6 yC79 contienen diferencias compensadas. Igualar carrera no acredita cambios personales de jornada/versión.','evidencia':str(PUENTE),'localizador':'ANIO2026; COD_CAR6 y79; agregado por COD_CAR'},
 {'clase':'E','hallazgo':'La causa individual de las48 diferencias no queda demostrada por la conciliación. No se puede distribuir personas para forzar los totales.','evidencia':str(AM),'localizador':'pendientes PUBLICACION_AGREGADA_SIN_RUT'},
 {'clase':'E','hallazgo':'El manifiesto puente septiembre describe causas cerradas por agregación. Se conservan sus conteos comprobados, pero esa conclusión causal excede la evidencia agregada. No se modifica el manifiesto histórico.','evidencia':str(PMAN),'localizador':'cierre_carrera_2026_09_30.patrones_encontrados; qa.detalle'},
]
export('DETALLE_66_CODIGOS_2026.csv',details)
export('CONTROL_32_CARRERAS_2026.csv',careers)
payload={'fecha':datetime.now().astimezone().isoformat(),'fase':'2/6','alcance':'Solo conciliación agregada2026; sin adjudicaciones individuales',
 'clasificacion':'B observación; C agregación/QA; D alcance previo conservado; E causas no acreditadas. Sin nueva regla A.',
 'ecuaciones':{'base_pregrado':'4105 =3145 VIG1+960 VIG0+0 VIG2+0 otros',
    'publicacion':'3425 =3371 Pregrado+54 Postítulo',
    'institucional_comparable_julio':'3199 =3145 Pregrado VIG1o2+54 Posgrado/Postítulo',
    'brecha_comparable':'226 =3371−3145 =3425−3199 =228−2',
    'puente_total_sin_postitulo_institucional':'280 =3425−3145 =226+54 fuera del alcance de BASE pregrado',
    'comparar_publicacion_con_todas_filas_mu':'−734 =3371−4105 =226−960; no es la brecha entre vigentes comparables'},
 'totales':{'mu_pregrado_total':4105,'mu_vig0':960,'mu_vig1':3145,'mu_vig2':0,'mu_otros':0,
    'publicacion_pregrado':3371,'publicacion_postitulo':54,'publicacion_total':3425,
    'institucional_postitulo_julio':54,'institucional_comparable_julio':3199,'brecha_comparable':226,
    'codigos_union':66,'codigos_pregrado':63,'codigos_postitulo':3,'codigos_con_brecha':48,
    'positivos':46,'suma_positiva':228,'negativos':2,'suma_negativa':-2,'carreras_pregrado':32,'carreras_brecha_neta':27},
 'hallazgos':claims,'fuentes_julio':sources,'fuentes_sha256_recalculados':hashes,
 'limites':['No se releyeron fuentes individuales históricas de julio; se reutilizan sus manifiestos, fórmula inventariada y cruce agregado.',
   'La conciliación actual de MU/CSV fue producida en fase2/conciliacion; aquí se verifican sus agregados y hashes.',
   'Coincidencia de conteos por código no prueba igualdad de identidades o aceptación individual SIES.',
   'Los archivos XLSX PRE_XLSX julio y fuente rector2026 tienen hashes distintos. La igualdad observada es agregada por código, no identidad binaria ni de filas.',
   'No se modifica el cierre previo ni se consideran resueltas causas por igualdad neta.',
   'No se modifica ningún dato, código, libro, denominador o tasa de retención.']}
save('RESULTADOS_BRECHA_2026.json',payload)
lines=['# Fase 2/6 · Brecha 2026 y alcance de las fuentes','','B/C — La diferencia de226 se reproduce por código completo, no solo en el total. Su causa individual permanece pendiente.',
 '', '| Universo / criterio | Total | Respaldo |', '|---|---:|---|',
 '| MU pregrado: todas las filas |4.105|B: lectura agregada actual|',
 '| MU pregrado: VIG=0 |960|B: lectura agregada actual|',
 '| MU pregrado: VIG=1 |3.145|B: lectura agregada actual|',
 '| MU pregrado: VIG=2 / otros |0 /0|B: lectura agregada actual|',
 '| Publicación: Pregrado |3.371|B:63 códigos|',
 '| Publicación: Postítulo |54|B: tres códigos; fuera de BASE pregrado|',
 '| Publicación total |3.425|C:3.371+54|',
 '| Institucional comparable del cierre de julio |3.199|C:3.145 pregrado+54 posgrado/postítulo de otra fuente|',
 '| Brecha comparable |226|C:3.371−3.145; también3.425−3.199|',
 '', 'C — La fórmula inventariada de julio, `07_PREGRADO_COMPLETO!AM7`, usa `OR(VIG="1",VIG="2")`. La coincidencia con VIG=1 se debe a que VIG=2 es cero en esta base; no cambia la regla histórica.',
 '', 'B/C — El puente de198 filas contiene66 códigos en2026. Todos sus totales de publicación coinciden con el cierre de julio. Los63 códigos pregrado coinciden también en el institucional. Los tres Postítulos son C53J3V1=17, C66J4V1=15 y C70J4V1=22; en julio tienen fuente separada con21 columnas.',
 '', 'C — Al comparar toda la publicación con BASE pregrado surge280=226+54 de distinto alcance. No son54 faltantes nuevos. Al comparar Pregrado publicado con todas las filas MU surge−734=226−960: incluye filas VIG=0 y responde a otra comparación.',
 '', '## Diferencias que siguen sin causa individual demostrada', '',
 'B/C — Hay48 códigos pregrado con diferencias:46 positivos suman228; dos negativos suman−2. Los códigos solo publicación son I162S2C77J1V1 (1) e I162S2C87J4V1 (5). Los66 códigos completos están en DETALLE_66_CODIGOS_2026.csv.',
 '', 'B/C/E — Al agrupar por COD_CAR hay27 carreras con brecha neta y cinco con neto cero. Dos de esas cinco ocultan compensaciones:',
 '', '| Carrera SIES | Código | Diferencia publicación−MU VIG1 | Respaldo |', '|---|---|---:|---|',
 '|6|I162S2C6J2V2|+1|B/C|','|6|I162S2C6J4V2|−1|B/C|',
 '|79|I162S2C79J2V1|−1|B/C|','|79|I162S2C79J4V1|+1|B/C|',
 '', 'E — Estos patrones no prueban que una persona cambió de jornada o versión. El manifiesto del30-sep declara causas cerradas por agregación; aquí se conserva la reproducción de los números y se separa esa afirmación causal no acreditada. No se modifica el antecedente.',
 '', 'E — Los hashes de la fuente XLSX de julio y del esquema rector posterior son distintos. Se confirma igualdad de agregados pregrado por código, no igualdad binaria o individual. Publicación agregada no contiene la identidad necesaria para asignar una diferencia a una persona.',
 '', '## Fuentes y localizadores', '']
for claim in claims:
    lines.append(f"- {claim['clase']} — {claim['hallazgo']} Fuente: `{claim['evidencia']}`; `{claim['localizador']}`.")
lines+=['','## QA y límites','','C — Se verificaron66 códigos,63 cruces institucionales pregrado, tres Postítulos,32 sumas por carrera y la partición VIG. Se conserva íntegramente cada fuente por hash. No se recalculan tasas de retención ni se alteran denominadores. No se exportan identificadores individuales.','']
(OUT/'INFORME_BRECHA_2026.md').write_text('\n'.join(lines))
assert hashes=={str(p):sha(p) for p in paths}
qa={'clasificacion':'C','estado':'PASS_CON_CAUSAS_PENDIENTES','codigos_publicacion_cotejados':66,
 'codigos_institucional_pregrado_cotejados':63,'codigos_postitulo_separados':3,
 'VIG1_vs_VIG1_o_2_igual_solo_por_VIG2_cero':True,'control_carreras':32,
 'fuentes_conservadas':True,'datos_individuales_exportados':False,'asignaciones_o_cambios_bases':0,
 'tasas_y_denominadores_retencion_modificados':False,'commit_push':False,
 'archivos':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='QA_Y_MANIFEST.json'}}
save('QA_Y_MANIFEST.json',qa)
print(json.dumps(qa,ensure_ascii=False,indent=2))

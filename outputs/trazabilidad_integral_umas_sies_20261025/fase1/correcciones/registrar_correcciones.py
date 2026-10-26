"""Registra cambios agregados V14–V18 existentes; no modifica libros ni bases.

Alcance autorizado: outputs/trazabilidad_integral_umas_sies_20261025/fase1/correcciones.
Los resultados históricos se leen de sus evidencias; no se recalcula retención.
"""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from datetime import datetime
import hashlib
import json
import re

ROOT = Path('/Users/alexi/Documents/GitHub/avance_curricular')
OUT = Path(__file__).resolve().parent
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(rel):
    return json.loads((ROOT / rel).read_text())

def evidence(rel):
    p = ROOT / rel
    return {'ruta': str(p), 'sha256_recalculado': sha(p)}

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def sheet(path, num):
    """Lee únicamente la hoja agregada solicitada; jamás exporta hojas individuales."""
    with ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(t.text or '' for t in s.iter(NS+'t'))
                       for s in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        tree = ET.fromstring(z.read(f'xl/worksheets/sheet{num}.xml'))
        cells = {}
        for c in tree.iter(NS+'c'):
            v = c.find(NS+'v')
            value = None if v is None else v.text
            if c.get('t') == 's' and value is not None:
                value = strings[int(value)]
            elif c.get('t') == 'inlineStr':
                value = ''.join(t.text or '' for t in c.iter(NS+'t'))
            f = c.find(NS+'f')
            cells[c.get('r')] = {'valor_cache_o_literal': value,
                                'formula': None if f is None else f.text,
                                'estilo': c.get('s')}
        return cells

VERSIONS = {
    'V14': 'outputs/correccion_proxy_t2_2025_20261023_v14',
    'V15': 'outputs/correccion_proxy_t3_2025_20261023_v15',
    'V16': 'outputs/aclaracion_tasas_2026_20261023_v16',
    'V17': 'outputs/pendientes_entrega_20261024_v17',
    'V18': 'outputs/auditoria_diccionario_sies_20261025/fase3_20261025',
}
manifest_names = {'V14':'MANIFEST_CORRECCION.json', 'V15':'MANIFEST_CORRECCION.json',
                  'V16':'MANIFEST_TASAS_2026_V16.json', 'V17':'QA_Y_MANIFEST.json',
                  'V18':'QA_EXCEL.json'}
manifest = {v: load(d+'/'+manifest_names[v]) for v,d in VERSIONS.items()}
sources = {v:evidence(d+'/'+manifest_names[v]) for v,d in VERSIONS.items()}
detail = []
for version in ['V14','V15','V16']:
    ed_rel = VERSIONS[version]+'/EDICION.json'
    ed = load(ed_rel)
    for row in ed['edits']:
        current = row.get('formula', row.get('value'))
        kind = 'fórmula' if 'formula' in row else ('nota/etiqueta' if isinstance(current,str) else 'valor agregado')
        if current == row.get('before') and row.get('expected') != row.get('before'):
            kind = 'caché de fórmula conservada'
        detail.append({'version':version, 'hoja':row['sheet'], 'celda':row['cell'],
                       'contenido_anterior':row.get('before'), 'contenido_actualizado':current,
                       'resultado_esperado':row.get('expected'), 'tipo':kind,
                       'clasificacion':'B/C; D para criterio interno; no A',
                       'estado':'Corrección documentada; conservar salvo supersesión posterior explícita',
                       'evidencia':evidence(ed_rel)})

v17 = Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx')
v18 = Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx')
assert sha(v17) == manifest['V17']['sha256_salida']
assert sha(v18) == manifest['V18']['sha256']
v17cells = sheet(v17,55)
v17_nonempty = [c for c,val in v17cells.items() if val['valor_cache_o_literal'] is not None or val['formula']]
v18_deltas = {}
for number in [52,54]:
    before, after = sheet(v17,number),sheet(v18,number)
    v18_deltas[str(number)] = {
        'celdas_contenido_o_cache_cambiado':[c for c in sorted(set(before)|set(after))
               if {k:v for k,v in before.get(c,{}).items() if k!='estilo'} !=
                  {k:v for k,v in after.get(c,{}).items() if k!='estilo'}],
        'celdas_estilo_cambiado':[c for c in sorted(set(before)|set(after))
                                if before.get(c,{}).get('estilo')!=after.get(c,{}).get('estilo')],
    }
    assert {c:x['formula'] for c,x in before.items() if x['formula']} == {c:x['formula'] for c,x in after.items() if x['formula']}

matrix = [
 {'version':'V14','hoja_celdas':'26_Avance_Curricular_Resumen!D1852,E1852,F1852,H1852; 18_Foto_Intertrimestral!E8,F8; 52_Codigos_SIES_Revision!E8,G8,I8',
  'regla_anterior':'600 VIGENTE y 680 presencias literales, algoritmo original no localizado.',
  'regla_a_conservar':'Cruce exacto de documentos R y P; puente explícito 2025_carga J/BU/BV. 694 presencias; 611 actividad período2 y estado VIGENTE. E1852 suma grupos de hoja53; hoja18 enlaza E1852.',
  'numerador':611,'denominador':1150,'tasa':611/1150,'tipo':'fórmula + agregado + nota','estado':'Aprobado/conservado; la exigencia histórica exacta fue sustituida por D de V15. Algoritmo original600 sigue E.','clasificacion':'B/C/D/E','evidencia':sources['V14']},
 {'version':'V14','hoja_celdas':'53_Codigos_T1_Confirmados!G54:G124,I54:I124,J54:J124 SOLO filas pares; 28_QA_Matematica!C11:F12,H11',
  'regla_anterior':'Grupos con numeradores previos.',
  'regla_a_conservar':'36 grupos actualizados (G numerador; I tasa; J explicación). No cambiar denominadores H. 28!C11:F11 y C12:F12 cotejan611 y611/1150.',
  'numerador':611,'denominador':1150,'tipo':'agregados + fórmulas + controles','estado':'Conservar. G tiene conteos literales reproducibles por script, no fórmulas individuales. Restaurar fórmulas no convierte estos agregados en prueba personal.','clasificacion':'B/C','evidencia':sources['V14']},
 {'version':'V15','hoja_celdas':'26_Avance_Curricular_Resumen!D1853,E1853,F1853,H1853,A1857:H1861; 18_Foto_Intertrimestral!B82; 28_QA_Matematica!A18,A19; 52_Codigos_SIES_Revision!A1,A14,A32',
  'regla_anterior':'535 VIGENTE,582 presencias; foto matrícula T3 ya1023.',
  'regla_a_conservar':'596 presencias=582R+14P;546 VIGENTE=535R+11P. Fórmulas SUM del bloque1859:1860. Criterio interno aprobado: actividad del período y VIGENTE del extracto sin exigir fecha exacta del estado. La foto de matrícula1023/1150 sigue siendo otro indicador.',
  'numerador':546,'denominador':1150,'tasa':546/1150,'tipo':'fórmula + nota','estado':'Aprobado/conservado; mecanismo original535 E, sin impedir nuevo cálculo reproducible.','clasificacion':'B/C/D/E','evidencia':sources['V15']},
 {'version':'V15','hoja_celdas':'xl/styles.xml (sin cambio de valor en celdas)',
  'regla_anterior':'Tres extensiones de estilos con referencias huérfanas producían reparación.',
  'regla_a_conservar':'Retiro exclusivo de tres extensiones;315 estilos y22dxf conservados. No reintroducir OOXML previo al reparar fórmulas.',
  'numerador':None,'denominador':None,'tipo':'esquema/compatibilidad','estado':'QA histórico: apertura Excel nativa sin reparación. Este registro no ejecutó apertura nueva.','clasificacion':'B/C','evidencia':evidence(VERSIONS['V15']+'/evidencia/QA_ESTILOS.json')},
 {'version':'V16','hoja_celdas':'18_Foto_Intertrimestral!H11,H93; D93:G93; B96',
  'regla_anterior':'Misma tasa almacenada sin la base visible para entenderla.',
  'regla_a_conservar':'1360/(1471−4)=1360/1467; cuatro exclusiones internas titulados documentadas. H11 referencia H93; denominador F93 deriva de hoja53.',
  'numerador':1360,'denominador':1467,'tasa':1360/1467,'tipo':'fórmula + nota','estado':'Conservar decisión interna ya documentada; no elevarla a regla oficial SIES.','clasificacion':'B/C/D','evidencia':sources['V16']},
 {'version':'V16','hoja_celdas':'18_Foto_Intertrimestral!F12,H94; D94,F94,G94; B97',
  'regla_anterior':'462/528; presentación podía confundirse con527 personas.',
  'regla_a_conservar':'462/528 matrículas; F94=SUM(23_Foto_Renuncias_T2_2026!C6:C24). 527 personas no reemplaza528 matrículas.66 renuncias agregadas sin nómina de origen.',
  'numerador':462,'denominador':528,'tasa':462/528,'tipo':'fórmula + nota','estado':'Resultado de matrículas conservado; tasa por personas E.','clasificacion':'B/C/E','evidencia':sources['V16']},
 {'version':'V16','hoja_celdas':'18_Foto_Intertrimestral!H14,H95; D95:G95; B96',
  'regla_anterior':'Mismo valor de tasa almacenado.',
  'regla_a_conservar':'2290/(2523−4)=2290/2519; cuatro exclusiones internas documentadas. H14 referencia H95.',
  'numerador':2290,'denominador':2519,'tasa':2290/2519,'tipo':'fórmula + nota','estado':'Conservar; no sustituir población por suma de subgrupos con duplicados.','clasificacion':'B/C/D','evidencia':sources['V16']},
 {'version':'V17','hoja_celdas':'55_Pendientes_entrega!A1:D18 (celdas pobladas exactas en JSON)',
  'regla_anterior':'Aclaraciones dispersas.',
  'regla_a_conservar':'Hoja informativa:66 renuncias sin respaldo individual; diferencia actividad/matrícula; fotos faltantes; tasa anual tresperíodos pendiente; cuatro exclusiones; promedio ponderado; límites QA.',
  'numerador':None,'denominador':None,'tipo':'nota/esquema','estado':'Conservar; B11=104 pendientes describe V17 y debe armonizarse con99 deV18 en una futura edición, no borrarse silenciosamente.','clasificacion':'B/C/D/E','evidencia':sources['V17']},
 {'version':'V18','hoja_celdas':'52_Codigos_SIES_Revision!F19,H19,F20,H20,F24,H24 (solo cachés); A1,A27,A28,A32,A33 (notas); 54_Contextos_y_Pendientes!A1,A6:O228',
  'regla_anterior':'2737 documentales+13 internos+104 pendientes=2854 contextos.',
  'regla_a_conservar':'2742 documentales+13 internos+99 pendientes=2854. Cinco recuperaciones enExcel; foco multiversión1040documentales+13internos+24pendientes=1077. No cambia tasa. Hoja54:221filas en6:226;227:228vacías; tabla conserva228. Fórmulas52 preservadas.',
  'numerador':2755,'denominador':2854,'tipo':'caché + agregado + nota','estado':'Edición v8 posteriormente promovida en fase4; A32 aún menciona activo v7 y debe actualizarse en edición futura. No cambiar V18 aquí.','clasificacion':'B/C/D/E','evidencia':sources['V18']},
]

annual_dir='outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/'
annual=load(annual_dir+'INVENTARIO_FUENTES_SHA256.json')
annual_manifest=load(annual_dir+'MANIFEST_BASE_RETENCION_MU_2022_2026.json')
for a in annual:
    count=next(x for x in annual_manifest['conteos'] if x['anio']==a['anio'])
    a['filas_consolidadas_reportadas']=count['filas_consolidadas']
    a['fecha_corte_efectiva_acreditada_en_inventario']='No consta; no deducida de nombre/carpeta'
    a['estatus_procedencia']='Fuente institucional granular seleccionada; no prueba individual de recepción/aceptación SIES'
    a['sha256_estado']='Hash reportado por inventario previo; fuente individual no releída en esta fase'
    a['columnas_faltantes_en_consolidado']=count['columnas_faltantes_vs_2026']
    a['columnas_extra_no_consolidadas']=count['columnas_extra_no_consolidadas']
    a['clasificacion_evidencia']='B inventario; E corte efectivo no acreditado aquí'
save('FUENTES_ANUALES_REUTILIZADAS.json', {
    'alcance':'Inventario existente, sin nuevos cruces ni recálculo anual',
    'evidencias':[evidence(annual_dir+'INVENTARIO_FUENTES_SHA256.json'),evidence(annual_dir+'MANIFEST_BASE_RETENCION_MU_2022_2026.json')],
    'fuentes':annual,
    'componentes_codigo_presentes':['COD_SED','COD_CAR','JOR','VERSION'],
    'institucion':'Contexto IPSS162 del proceso; no completar otra institución por supuesto',
    'consolidado':annual_manifest['salidas'],
    'advertencia':'Matrícula total, cohorte elegible de retención y titulaciones son universos distintos; no imponer igualdad entre sus totales.'})

save('MATRIZ_CORRECCIONES_V14_V18.json', {
    'fecha_generacion':datetime.now().astimezone().isoformat(),
    'alcance':'Fase1 H1/H3: correcciones que debe conservar una restauración posterior de fórmulas. No se modifica ningún libro.',
    'clasificacion':'B lectura de evidencia; C registro técnico; D decisiones previas identificadas; E límites. No nuevas reglas A.',
    'matriz':matrix,
    'celdas_V14_V16':detail,
    'V17_celdas_nuevas_con_contenido':v17_nonempty,
    'V18_deltas_releidos_de_libros':v18_deltas,
    'libros_verificados_por_hash':[
        {'ruta':str(v17),'sha256':sha(v17),'coincide_manifiesto':True},
        {'ruta':str(v18),'sha256':sha(v18),'coincide_manifiesto':True}],
    'estado_actual_diccionario':{'puntero':evidence('data/diccionario_sies_seguimiento/activo.json'),
        'contenido':load('data/diccionario_sies_seguimiento/activo.json'),
        'activacion_y_publicacion':evidence('outputs/auditoria_diccionario_sies_20261025/fase4_20261025/INFORME_FASE4.md')},
    'limites':['Se reutilizan QA históricos, no se ejecutan nuevamente cruces individuales ni cálculos anuales.',
               'Se preservan fórmula y valor observado como tipos distintos; la existencia de un literal no implica error si tiene fuente/script trazables.',
               'Libro original22oct no es referencia numérica actual: V14/V15 corrigen600→611 y535→546.',
               'V18 no fue reabierto/recalculado en Excel nativo en esta fase.',
               '99 pendientes Excel no equivalen a24 pendientes multiversión ni a3041 observaciones históricas.',
               'No se incorpora ningún identificador estudiantil. Las diferencias hoja54 se listan por coordenada, sin copiar contenido de contexto.']})

lines=['# Correcciones V14–V18 que deben conservarse', '',
 'B/C — Registro de evidencias existentes. No restaura ni cambia fórmulas, bases, tasas o denominadores. El original del22-oct no es la referencia numérica vigente.', '',
 '| Versión | Hoja y celdas | Corrección / resultado vigente | Tipo y estado |',
 '|---|---|---|---|']
for row in matrix:
    lines.append('| '+row['version']+' | '+row['hoja_celdas'].replace('|','/')+' | '+row['regla_a_conservar'].replace('|','/')+' | '+row['clasificacion']+' · '+row['tipo']+'. '+row['estado'].replace('|','/')+' |')
lines += ['', '## Límites y pendientes de actualización', '',
 '- B/C: se cotejaron los hashes reales de V17 y V18 en Escritorio con sus manifiestos. Coinciden.',
 '- C/D: el auxiliar de actividad de2025 usa611/1150 enT2 y546/1150 enT3. La matrículaT3 mantiene1023/1150. Son indicadores distintos; no sustituir uno por otro.',
 '- E: la nómina que origina66 renuncias sigue pendiente.462/528 es tasa de matrículas, no462/527 personas.',
 '- B/E: V18 conserva55!B11 con104 pendientes deV17, aunque52!H24 contiene99;52!A32 aún dice activo v7, aunque el puntero común esv8. Deben corregirse las notas en la próxima edición, conservando el antecedente y sin alterar las tasas.',
 '- C: restaurar fórmulas debe preservar el arreglo OOXML V15 y no reintroducir extensiones huérfanas. Hay conteos agregados legítimamente literales; su reproducción está en scripts y evidencias, no necesariamente en fórmula de celda.',
 '- E: no se vuelve a certificar la apertura nativa, todo el libro ni las fuentes individuales. Los QA V14–V18 se registran como antecedentes existentes.',
 '- C: el JSON contiene las206 entradas de EDICION V14–V16 y las coordenadas efectivamente cambiadas enV18. Los listados exactos distinguen modificaciones de contenido/caché y estilo.',
 '', '## Evidencias y hashes recalculados', '']
for v,e in sources.items():
    lines.append(f"- B · {v}: `{e['ruta']}` — `{e['sha256_recalculado']}`.")
lines += ['', '## Fuentes anuales ya inventariadas', '',
 '| Año | Fuente / hoja | Filas reportadas | Alcance del corte |', '|---|---|---:|---|']
for a in annual:
    sheets=[s['name'] for dg in a['diagnostico'] for s in dg.get('sheets',[]) if s['name']!='Hoja1']
    lines.append(f"| {a['anio']} | {a['archivo']} / {', '.join(sheets) or 'CSV'} | {a['filas_consolidadas_reportadas']} | B/E: inventario previo; fecha efectiva no acreditada aquí. |")
lines += ['', 'B/C — El esquema conserva COD_SED, COD_CAR, JOR y VERSION. La conciliación por código completo se puede apoyar en estos componentes; no requiere suponer que COD_CAR solo es el código completo.',
 'E — La carpeta Enviados y el nombre de un archivo no acreditan por sí solos aceptación SIES. Los cortes y cadenas envío/retorno deben quedar conectados por proceso/año. Matrícula total, retención elegible y titulaciones no comparten automáticamente universo.', '']
(OUT/'MATRIZ_CORRECCIONES_V14_V18.md').write_text('\n'.join(lines))
assert len(detail) == 206 and len(matrix) == 9 and len(annual) == 5
for row in detail:
    assert re.fullmatch('[A-Z]+[0-9]+', row['celda'])
    for field in ['contenido_anterior', 'contenido_actualizado', 'resultado_esperado']:
        assert not re.search(r'\b\d{7,8}-[0-9Kk]\b', str(row[field]))
qa={
 'clasificacion':'C','estado':'REGISTRO_REPRODUCIDO_SIN_MODIFICAR_ORIGINALES',
 'entradas_edicion_por_version':{v:sum(x['version']==v for x in detail) for v in ['V14','V15','V16']},
 'celdas_V17_pobladas':len(v17_nonempty),
 'V18_celdas_contenido_cambiado':{k:len(v['celdas_contenido_o_cache_cambiado']) for k,v in v18_deltas.items()},
 'formula_texto_hojas_52_54_V17_V18_identico':True,
 'bloques_correccion_registrados':9,
 'fuentes_anuales_reutilizadas':5,
 'contenido_trasladado_sin_patron_RUT_con_DV':True,
 'limite_privacidad':'No se exportan hojas individuales ni valores de filas de contexto; control de patrón no es certificación universal de privacidad.',
 'originales_hash_conservados':sha(v17)==manifest['V17']['sha256_salida'] and sha(v18)==manifest['V18']['sha256'],
 'no_recalculo_anual':True,'no_cambios_fuentes_ni_libros':True,'commit_push':False,
 'entregables':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='QA_Y_MANIFEST.json'}
}
save('QA_Y_MANIFEST.json',qa)
print(json.dumps(qa,ensure_ascii=False,indent=2))

#!/usr/bin/env python3
"""Consolida límites D2 y verifica preservación sin activar resultados."""
import json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/cierre_d2/20261016'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(BASE/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def main():
    criteria=load(ROOT/'data/cierre_d1/20261016/criterios.json');inventory=load(ROOT/'data/cierre_d1/20261016/inventario.json')
    search=load(BASE/'busqueda_fuentes.json');review=load(BASE/'revision_fuentes_candidatas.json');dossiers=load(BASE/'expedientes_16.json')
    brechas=[]
    for c in criteria:
        refs=[{'universo':r['universo'],'id':r['id']} for r in inventory if c['id'] in r['causas_pendientes']]
        finding='No se incorporó evidencia de atribución/fechas suficiente para cerrar esta categoría; se conserva estado D1.'
        if c['id']=='CONFLICTO':finding='16 contextos releídos: 14 con coexistencia nuevos/antiguos y dos solo antiguos; cinco con ingresos declarados en años solo antiguos. No hay regla UMAS unívoca acreditada.'
        elif c['id'] in ('SIN_OFERTA','OFERTA_EN_LIMITE_2010'):finding='Sin candidato de oferta 2007–2009 en búsqueda acotada por nombres; no demuestra inexistencia fuera de ese alcance.'
        elif c['id'] in ('SIN_PLAN_OBSERVADO','VIGENCIA_MALLA_NO_ACREDITADA','VARIOS_PLANES_OBSERVADOS','SIN_ACTIVIDAD_OBSERVADA','SIN_RELACION_PLAN'):finding='Catálogo ya conocido H4 releído completo: 11.438 filas, sin campos de vigencia/fecha. Su copia íntegra queda gobernada; no resuelve vigencia por episodio.'
        elif c['id']=='PRIMERA_OBSERVACION_NO_ES_INGRESO':finding='CILOG conserva tres registros 2024 sin actividad, hoy retiro/retracto; el mínimo de presencia puede incorporar esos antecedentes. El extracto 11248 no cambia ANOINGRESO en las 49 coincidencias.'
        elif c['id']=='SIN_CONTRASTE_RESERVADO':finding='Las 211 reglas K0 conservan falta de reserva. Reporte 4262/2025 no contiene carrera/código/plan; el nuevo extracto 11248 no aporta etiqueta SIES. No se reutiliza la reserva como evidencia nueva.'
        elif c['id']=='FUERA_COBERTURA_PERSONAL':finding='Los ocho contextos CILOG 2024–2026 permanecen fuera del enlace B5. MRUN agrega evidencia de cohortes, no identidades UMAS. Las demás brechas fuera de cobertura permanecen identificadas.'
        brechas.append({'causa':c['id'],'elementos':refs,'conteos_por_universo':dict(Counter(r['universo'] for r in refs)),
            'hallazgo_d2':finding,'estado':'INVESTIGACION_ACOTADA_CERRADA_CON_BRECHA','fuente_faltante':c['fuente_necesaria'],'siguiente_accion':c['accion'],'criterio_salida':c['criterio_salida']})
    save('brechas_por_categoria.json',brechas)
    counts=Counter()
    for r in dossiers:
        for s in r['detalle_agregado']:
            if s['admision_anio_ingreso_actual']=='SOLO_ANTIGUOS':counts[s['estado_actual_umas'],s['situacion_actual_umas']]+=s['personas']
    q={'fase':'D2','estado':'H4_H5_H6_EJECUTADOS_CON_BRECHAS','expedientes_revisados':len(dossiers),
       'coexistencia_nuevos_antiguos':sum(r['conclusion'].startswith('COEXISTENCIA') for r in dossiers),
       'contextos_con_reporte_parcial':[r['contexto'] for r in dossiers if r['personas_sin_reporte_atribuible']],
       'incidencias_admision_por_estado_actual':[{'estado':a,'situacion':b,'observaciones_persona_estrato':n} for (a,b),n in sorted(counts.items())],
       'fuentes_busqueda':{'directorios':len(search['alcance']),'archivos_listados':sum(x['archivos_listados'] for x in search['alcance']),'candidatos_por_nombre':len(search['candidatos']),'candidatos_oferta_2007_2009':sum('OFERTA_2007_2009_CANDIDATA' in r['categorias'] for r in search['candidatos'])},
       'categorias_brecha_conservadas':len(brechas),'reglas_promovidas':0,'siguiente_fase':'D3','limite':'Cierre de investigación acotada, no resolución de todas las equivalencias; conteos por estrato no son personas únicas entre contextos.'}
    save('cierre.json',q)
    # Integridad de las fuentes releídas y de las entregas anteriores.
    m=load(BASE/'manifest_investigacion.json')
    for name,digest in m['fuentes_sha256'].items():assert sha(Path(name) if Path(name).is_absolute() else ROOT/name)==digest,name
    for name,digest in m['salidas_sha256'].items():assert sha(BASE/name)==digest,name
    for name in ('reporte_4262_2025','extracto_11248'):
        s=review[name];assert sha(Path(s['path']))==s['sha256']
    cat=review['catalogo_planes'];assert sha(ROOT/cat['copia_completa'])==cat['fuente']['sha256']
    protected=load(ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json')['referencias_sha256']
    for name,digest in protected.items():assert sha(ROOT/name)==digest,name
    for edition in ('data/diccionario_c1/20261016/entrega.json','data/consumo_comun_c2/20261016/qa.json'):
        for name,digest in load(ROOT/edition)['archivos_sha256'].items():assert sha(ROOT/name)==digest,name
    d1=load(ROOT/'data/cierre_d1/20261016/manifest.json')
    for name,digest in d1['salidas_sha256'].items():assert sha(ROOT/'data/cierre_d1/20261016'/name)==digest,name
    files=[p for p in BASE.rglob('*') if p.is_file() and p.name not in ('manifest_cierre.json','qa.json')]
    scripts=['scripts/investigar_excepciones_d2.py','scripts/buscar_fuentes_d2.py','scripts/completar_fuentes_d2.py','scripts/cerrar_investigacion_d2.py','tests/test_excepciones_d2.py']
    extra=['data/cierre_d1/20261016/inventario.json','data/cierre_d1/20261016/criterios.json','data/recuperacion_cruce_mrun_umas/20261016/esquema_mrun_texto_completo.json','docs/d2_excepciones_20261016.md']
    save('manifest_cierre.json',{'archivos_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files+[ROOT/n for n in scripts+extra]},'referencias_protegidas':len(protected),'c1_c2_d1_preservados':True,'fuentes_personales_no_copiadas':'Referenciadas y verificadas por hash; la reproducción analítica requiere las fuentes externas autorizadas.'})
    print(json.dumps(q,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

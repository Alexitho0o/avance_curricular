#!/usr/bin/env python3
"""Construye edición D3 completa desde resultados congelados, sin nuevos enlaces."""
import hashlib,json,sys
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from common.reglas_dictamen_d3 import evaluar_contexto
OUT=ROOT/'data/validacion_d3/20261016'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((ROOT/n).read_text())
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def main():
    # Rechazar fuentes cerradas alteradas, no actualizar sus hashes.
    for folder in ('data/cierre_d1/20261016','data/cierre_d2/20261016'):
        if 'd1' in folder:
            for n,h in load(folder+'/manifest.json')['salidas_sha256'].items():assert sha(ROOT/folder/n)==h,n
        else:
            for n,h in load(folder+'/manifest_cierre.json')['archivos_sha256'].items():assert sha(ROOT/n)==h,n
    inputs=['data/matriz_academica_b4/20261016/matriz_contextos.json','data/reglas_historicas_b5/20261016/reglas_observadas.json',
       'data/cierre_d2/20261016/expedientes_16.json','data/matriz_academica_b4/20261016/oferta_anual_referencia.json',
       'data/versiones_por_cohorte/20261016/grupos_existentes.json','data/cierre_d1/20261016/inventario.json',
       'data/diccionario_c1/20261016/celdas_originales.json','data/cierre_d2/20261016/logistica_mrun_cohortes.json',
       'data/cierre_d2/20261016/cilog.json','common/reglas_dictamen_d3.py']
    for prefix in ('data/matriz_academica_b4/20261016/','data/reglas_historicas_b5/20261016/'):
        for n,h in load(prefix+'manifest.json')['salidas_sha256'].items():assert sha(ROOT/(prefix+n))==h,n
    contexts,rules,dossiers,offers,groups,inventory,cells,cohorts,cilog=[load(n) for n in inputs[:-1]]
    byctx=defaultdict(list)
    for r in rules:
        if r['modelo']=='K0':
            for cid in r['contextos_b4']:byctx[cid].append(r)
    dossiers={r['contexto']:r for r in dossiers}
    offers={(r['anio'],r['codigo_unico']):r for r in offers}
    groups={(g['codcarpr'],g['sede'],g['jornada']):g for g in groups}
    results=[evaluar_contexto(c,byctx[c['contexto']],dossiers.get(c['contexto']),offers,groups.get((c['codcarpr'],c['sede_umas'],c['jornada_umas']))) for c in contexts]
    assert len(results)==len({r['clave'] for r in results})==1986
    sourcecells=cells['Diccionario SIES'];attributes={}
    for i in range(6,147):
        code=sourcecells[f'A{i}'];attributes[code]={key:sourcecells.get(f'{col}{i}') for key,col in [('nombre_oficial_2026','B'),('ultimo_nombre_historico','C'),('jornada_2026','J'),('modalidad_2026','K'),('tipo_plan_2026','L'),('sector_ipss_2026','S'),('estado_sector','T'),('evidencia_sector','U')]}
    codes=[];plans=[]
    result_by_id={r['contexto']:r for r in results}
    for r in inventory:
        if r['universo'] not in ('CODIGO_SIES','PLAN_UMAS'):continue
        links=r['vinculos']['contextos_observados']
        updated=dict(r,estado_d1=r['estado_cierre'],estado_cierre='DICTAMEN_D3_CON_BRECHAS',
            estados_contextos_observados=dict(Counter(result_by_id[c]['estado'] for c in links)),
            codigo_asignado=None,habilitada_para_resolver=False)
        if r['universo']=='CODIGO_SIES':codes.append(dict(updated,atributos_c1_referencia_2026=attributes[r['id']]))
        else:plans.append(updated)
    assert len(codes)==141 and len(plans)==236
    policy=[
      ('D3-01','CLAVE_EXACTA_ANUAL','No extrapolar entre años; parámetros literales de B5.', 'docs/b5_reglas_historicas_20261016.md'),
      ('D3-02','EPISODIO_NO_INFERIDO','Primera observación/ANOINGRESO no acreditan ingreso efectivo a continuidad.','docs/d2_excepciones_20261016.md'),
      ('D3-03','ADMISION_POR_ANIO','Solo antiguos en observación no prueba error; conservar discrepancia documentada de ingreso.','data/cierre_d2/20261016/expedientes_16.json'),
      ('D3-04','CONFLICTO_NO_RESUELTO_POR_FRECUENCIA','No elegir destino ante conflicto o atribución ambigua.','data/cierre_d1/20261016/criterios.json'),
      ('D3-05','AUSENCIA_EXPLICITA','Sin evidencia o sin regla no hay selección por cercanía.','docs/d1_inventario_criterios_20261016.md'),
      ('D3-06','MALLA_REQUIERE_VIGENCIA','Plan observado no acredita vigencia curricular; no asignar malla en esta edición.','data/cierre_d2/20261016/revision_fuentes_candidatas.json'),
      ('D3-07','CORROBORACION_OBSERVACIONAL','Preservar nivel de evidencia K0 sin certificar ni revalidar la reserva.','docs/b5_reglas_historicas_20261016.md'),
      ('D3-08','PERFIL_SEPARADO','Comparación de tipo/duración de referencia; conservar candidatos y no presumir vigencia histórica.','data/versiones_por_cohorte/20261016/grupos_existentes.json'),
      ('D3-09','VARIANTE_NO_EVITA_ABSTENCION','K1–K3 no superan impedimentos del contexto; dato posterior impide uso histórico.','docs/b5_reglas_historicas_20261016.md')]
    save('reglas.json',[dict(id=i,nombre=n,condicion=t,fuente=s,autoridad='INTERNA_ANALITICA',habilita_carga=False) for i,n,t,s in policy])
    package={'edicion':'D3_20261016','contextos':results,'codigos_sies':codes,'planes_umas':plans,
        'incidencias_cilog':{'contextos':cilog['contextos_b4'],'perfil_continuidad':cilog['perfil_cilog'],'perfil_regular':cilog['perfil_ilog_online'],
            'cohortes_mrun_continuidad':[r for r in cohorts if r['codigo']=='I162S2C77J4V2'],
            'limite':'Datos MRUN agregados; no atribuir a personas UMAS ni usar como nuevo contraste independiente.'}}
    save('dictamenes.json',package)
    summary={'fase':'D3','universos':{'contextos':len(results),'codigos':len(codes),'planes':len(plans)},
        'dictamen_contextos':dict(Counter(r['estado'] for r in results)),
        'alcances':dict(Counter(r['alcance'] for r in results)),
        'causas_no_aditivas':dict(Counter(c for r in results for c in r['causas_abstencion_asignacion'])),
        'k0_conservado':dict(Counter(r['estado'] for r in rules if r['modelo']=='K0')),
        'reglas_b5_conservadas':len(rules),'contextos_abstencion_asignacion':len(results),'asignaciones_activadas':0,
        'validacion_independiente_nueva':False,'contraste':'Regresión B5 y verificación de hallazgos D2, sin nuevas etiquetas independientes.',
        'metricas_reserva_b5_referencia_no_reestimadas':load('data/reglas_historicas_b5/20261016/resumen.json')['hipotesis']['K0']['evaluacion_reserva'],
        'cobertura_por_estado':{s:{'contextos':sum(r['estado']==s for r in results),'codigos_observados_distintos':len({code for r in results if r['estado']==s for code in r['codigos_observados']}),'planes_observados_distintos':len({p for c,r in zip(contexts,results) if r['estado']==s for p in c['planes_observados']})} for s in sorted({r['estado'] for r in results})}}
    save('resumen.json',summary)
    sourcehashes={n:sha(ROOT/n) for n in inputs+['scripts/construir_dictamen_d3.py','data/reglas_historicas_b5/20261016/resumen.json']}
    for _,_,_,n in policy:sourcehashes[n]=sha(ROOT/n)
    save('manifest.json',{'fuentes_sha256':sourcehashes,'salidas_sha256':{n:sha(OUT/n) for n in ['reglas.json','dictamenes.json','resumen.json']}})
    save('descriptor.json',{'edicion':'D3_20261016','archivos_sha256':{str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['reglas.json','dictamenes.json','manifest.json']},'motor_sha256':sha(ROOT/'common/reglas_dictamen_d3.py')})
    print(json.dumps(summary,ensure_ascii=False,indent=2));print('SHA_DESCRIPTOR',sha(OUT/'descriptor.json'))
if __name__=='__main__':main()

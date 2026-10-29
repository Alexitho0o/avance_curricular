#!/usr/bin/env python3
"""QA aditivo H002d; conserva validadores e informes históricos."""
from pathlib import Path
from collections import Counter
import csv
import json
import re
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import cuadrar_totales_h002d as b


def command(*args):
    return subprocess.run(args,cwd=ROOT,capture_output=True,text=True)


def main():
    base=b.load('outputs/paridad_codigo_sies_20261029/ESTADO_INICIAL_H002D.json')
    controls={}
    controls['HEAD_rama']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==base['HEAD'] and subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()==base['rama']
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines()
    controls['24_ajenos_status']=len(base['status'])==24 and all(x in status for x in base['status'])
    controls['24_ajenos_bytes']=all(b.sha(ROOT/x['ruta'])==x['sha256'] for x in base['ajenos'])
    controls['H002_b_c_bytes_intactos']=all(b.sha(ROOT/p)==h for p,h in base['protegidos'].items())
    staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
    controls['solo_nuevos_H002d']=not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).strip() and all(p not in base['protegidos'] and p.startswith('outputs/paridad_codigo_sies_20261029/') for p in staged)
    old=b.load('data/paridad_codigo_sies/20261029/MANIFEST.json')
    controls['H002_fuentes_y_salidas_hash']=all(b.sha(ROOT/x['ruta'])==x['sha256'] for x in old['entradas']) and all(b.sha(ROOT/p)==h for p,h in old['salidas'].items())
    controls['H002_auxiliares_hash']=all(b.sha(ROOT/p)==h for p,h in old['auxiliares_H002b'].items())
    controls['H002_milestone_hash']=b.load('manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/REGISTRO.json')['manifest_sha256']==b.sha(ROOT/'data/paridad_codigo_sies/20261029/MANIFEST.json')
    tab=b.load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas']
    controls['H002_106_161_sin_cambio']=Counter(x['anio'] for x in tab)==Counter({2026:106,2027:161}) and len({(x['anio'],x['codigo_unico']) for x in tab})==267
    run=command(sys.executable,'-B',str(OUT/'construir_paridad.py'),'--verificar')
    controls['H002_reproduccion']=run.returncode==0
    run=command(sys.executable,'-B',str(OUT/'revisar_casos.py'))
    controls['H002b_reproduccion_fichas']=run.returncode==0
    # Reusar resultado H002c sólo después de verificar entradas, salidas y scripts.
    mc=b.load('outputs/paridad_codigo_sies_20261029/MANIFEST_H002C.json')
    controls['H002c_hashes_para_reusar_QA']=all(b.sha(x['ruta'])==x['sha256'] for x in mc['fuentes']) and all(b.sha(OUT/n)==h for n,h in mc['salidas'].items()) and all(b.sha(ROOT/n)==h for n,h in mc['componentes'].items())
    controls['H002c_QA_previo_PASS']=b.load('outputs/paridad_codigo_sies_20261029/QA_H002C.json')['estado']=='PASS_CON_PENDIENTES_E'
    tests=[]
    for p in sorted(OUT.glob('test_*.py')):
        run=command(sys.executable,'-B',str(p));tests.append({'archivo':p.name,'exit':run.returncode,'pruebas':sum(int(n) for n in re.findall(r'Ran (\d+) tests?',run.stderr))})
    controls['42_pruebas_H002_hasta_d']=sum(x['pruebas'] for x in tests)==42 and all(x['exit']==0 for x in tests)
    v=b.load('outputs/paridad_codigo_sies_20261029/REVISION_CASO_A_CASO_12_v3.json')
    p=b.load('outputs/paridad_codigo_sies_20261029/PROPUESTA_PLANES_43_v2.json')
    audit=b.load('outputs/paridad_codigo_sies_20261029/CONTROL_TOTALES_H002D.json')
    controls['12_unicos_sin_aplicar']=len(v['casos'])==12 and {x['numero_original'] for x in v['casos']}==set(range(1,13)) and all(not x['aplicada'] and x['decision_Alexi']=='____' for x in v['casos'])
    controls['12_suma_clases']=Counter(x['clasificacion'] for x in v['casos'])==Counter(v['conteos'])
    controls['12_regla_dos_vias_y_ninguna_contradice']=all(b.combine(*[x['evidencias'][k] for k in ['a_perfil','b_documental_v20','c_cuadratura_exacta']])==x['clasificacion'] for x in v['casos'])
    controls['c_sin_aproximaciones_ni_ceros']=all(m['interno_expedientes']>0 and m['interno_expedientes']==m['SIES_matriculas'] and m['delta_interno_menos_publico']==0 and m['igualdad_exacta_con_control_MU'] for x in v['casos'] for m in x['cuadraturas_exactas_c'])
    controls['c_no_vota_subtotales_ni_perfiles_incompatibles']=all(m['plan']=='CONJUNTO_PLANES_DEL_GRUPO' and m['perfil_grupo_compatible'] for x in v['casos'] for m in x['cuadraturas_exactas_c'])
    controls['unidades_y_cortes_separados']=all(not r['comparable_corte_SIES'] for x in v['casos'] for r in x['conteos_internos_por_anio_plan'])
    controls['Permanencia_no_repetida_historicamente']=all(r['expedientes'] is None for x in v['casos'] for r in x['conteos_internos_por_anio_plan'] if r['fuente']=='Permanencia.xlsx' and r['anio']!=2026)
    controls['primera_anual_publica_no_sustituida_por_total']=any(t['SIES_primer_anio'] is None and t['SIES_total']>0 for x in v['casos'] for t in x['totales_por_anio_codigo'])
    controls['37_y_6_recomprobados']=p['conteos']=={'CODIGO_NUEVO_2027_SIN_HISTORIA':37,'HISTORICO_SIN_MATRICULA_VIGENTE':6} and len(p['casos'])==43
    controls['37_sin_historia_publica_ni_MU']=all(not x['historia_publica'] and not x['historia_MU_2022_2026'] for x in p['casos'] if x['listado_para_UMAS'])
    hist=[x for x in p['casos'] if not x['listado_para_UMAS']]
    controls['6_solo_C35_ultima_2019_2022']=len(hist)==6 and all(b.dimension(x['codigo_unico'])[1]=='35' and 2019<=x['ultima_matricula_publica']['anio']<=2022 for x in hist)
    mu=[x for x in hist if x['historia_MU_2022_2026']]
    controls['MU_solo_C35J4V2_2022']=len(mu)==1 and mu[0]['codigo_unico']=='I162S2C35J4V2' and {z['anio'] for z in mu[0]['historia_MU_2022_2026']}=={2022}
    observations=p['observaciones_oferta']
    controls['observacion_oferta_7_con_manual_p28']=len(observations)==7 and {x['codigo_unico'] for x in observations}=={x['codigo_unico'] for x in hist}|{'I162S2C11J4V1'} and all(x['pagina']==28 and x['vigencia_declarada']=='2' and x['no_modificar_oferta'] for x in observations)
    controls['publicacion_280160_filas_3425_IPSS_2026']=audit['filas_publicacion']==280160 and audit['MAT_2026_IPSS']==3425
    controls['puente_198_y_cifras_publicas_paridad']=audit['filas_puente']==198 and not audit['publicacion_vs_puente_diferencias']
    controls['MRUN_2026_paridad']=audit['MRUN_2026_diferencias']==0
    code=command(sys.executable,'-B',str(OUT/'cuadrar_totales_h002d.py'),'--verificar')
    controls['reproduccion_H002d_hash']=code.returncode==0
    manifest=b.load('outputs/paridad_codigo_sies_20261029/MANIFEST_H002D.json')
    controls['fuentes_salidas_componentes_H002d_hash']=all(b.sha(x['ruta'])==x['sha256'] for x in manifest['fuentes']) and all(b.sha(OUT/n)==h for n,h in manifest['salidas'].items()) and all(b.sha(ROOT/n)==h for n,h in manifest['componentes'].items())
    patterns={'rut_dv':r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)',
        'email':r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','codcli':r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)'}
    findings=[]
    for f in OUT.iterdir():
        if not f.is_file() or str(f.relative_to(ROOT)) in base['protegidos']:continue
        s=re.sub(r'\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40})\b','HASH',f.read_text())
        for name,pat in patterns.items():
            if re.search(pat,s):findings.append({'archivo':f.name,'patron':name})
    controls['privacidad_sin_hallazgos']=not findings
    result={'hito':'H002d','clase':'C','estado':'PASS_CON_PENDIENTES_E' if all(controls.values()) else 'FAIL',
        'controles':controls,'pruebas':tests,'hallazgos_privacidad':findings,
        'reproduccion_error':code.stderr[-1800:] if code.returncode else '',
        'nota':'QA técnico no aprueba propuestas ni prueba identidad por totales. Se reusan validaciones previas sólo con entradas/salidas intactas.'}
    (OUT/'QA_H002D.json').write_text(b.dump(result));print(b.dump(result))
    return 0 if all(controls.values()) else 1


if __name__=='__main__':raise SystemExit(main())

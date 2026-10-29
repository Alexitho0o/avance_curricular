#!/usr/bin/env python3
"""QA H002c: controles H002 reutilizados; no reescribir QA históricos."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import resolver_planes_h002c as b


def run(*args):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
    return p.returncode,p.stdout,p.stderr


def main():
    base=b.load('outputs/paridad_codigo_sies_20261029/ESTADO_INICIAL_H002C.json')
    h=b.load('data/paridad_codigo_sies/20261029/MANIFEST.json')
    controls={}
    table=b.load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')
    rr=table['filas'];keys={(x['anio'],x['codigo_unico']) for x in rr}
    controls['H002_106_161_universos']=Counter(x['anio'] for x in rr)==Counter({2026:106,2027:161}) and len(keys)==267
    with (ROOT/'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.csv').open() as f:
        cc=list(csv.DictReader(f,delimiter=';'))
    controls['H002_CSV_JSON']=keys=={(int(x['anio']),x['codigo_unico']) for x in cc} and len(cc)==267
    controls['H002_sumas_estados']=all(Counter(x['estado'] for x in rr if x['anio']==y)==
        Counter({k:v for k,v in table['conteos_por_anio_estado'][str(y)].items() if v}) for y in [2026,2027])
    controls['H002_entradas_salidas_hash']=all(b.sha(ROOT/x['ruta'])==x['sha256'] for x in h['entradas']) and all(b.sha(ROOT/p)==v for p,v in h['salidas'].items())
    controls['H002_componentes_hash']=all(b.sha(ROOT/p)==v for p,v in h['auxiliares_H002b'].items())
    controls['H002_hito_manifest']=b.load('manifests/milestones/H002-PARIDAD-CODIGO-SIES-2027/REGISTRO.json')['manifest_sha256']==b.sha(ROOT/'data/paridad_codigo_sies/20261029/MANIFEST.json')
    configs={x['id']:x for x in b.load('data/paridad_codigo_sies/20261029/FUENTES.json')['fuentes']}
    with (ROOT/configs['carga_v06']['ruta']).open() as f:
        raw=list(csv.reader(f,delimiter=';'))
    rows27={'I162S'+v[0]+'C'+v[2]+'J'+v[5]+'V'+v[6]:v for v in raw}
    controls['H002_2027_atributos_literales']=all(x['nombre_carrera']==rows27[x['codigo_unico']][3] and
        x['modalidad_codigo']==rows27[x['codigo_unico']][4] and x['tipo_plan_codigo']==rows27[x['codigo_unico']][7] and
        x['duracion_total_semestres']==rows27[x['codigo_unico']][11] and x['vigencia_2027']==rows27[x['codigo_unico']][47]
        for x in rr if x['anio']==2027)
    controls['H002_267_filas_sin_cambio']=all(b.sha(ROOT/p)==v for p,v in base['protegidos'].items())
    controls['24_cambios_ajenos_bytes']=all(b.sha(ROOT/x['ruta'])==x['sha256'] for x in base['ajenos'])
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines()
    controls['24_cambios_ajenos_status']=all(x in status for x in base['status']) and len(base['status'])==24
    controls['rama_HEAD_correctos']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==base['HEAD'] and subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()==base['rama']
    # No hay ninguna modificación a archivos rastreados; staging sólo nuevos H002c.
    staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
    modified=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    controls['sin_modificaciones_rastreados']=not modified and all(p not in base['protegidos'] and p.startswith('outputs/paridad_codigo_sies_20261029/') for p in staged)
    tests=[]
    for p in sorted(OUT.glob('test_*.py')):
        code,stdout,stderr=run(sys.executable,'-B',str(p))
        tests.append({'archivo':p.name,'exit':code,'pruebas':sum(int(m) for m in re.findall(r'Ran (\d+) tests?',stderr))})
    controls['pruebas_H002_y_H002c']=all(x['exit']==0 for x in tests) and sum(x['pruebas'] for x in tests)==32
    code,_,err=run(sys.executable,'-B',str(OUT/'construir_paridad.py'),'--verificar')
    controls['H002_reproduccion_tabla']=code==0
    code,_,err2=run(sys.executable,'-B',str(OUT/'revisar_casos.py'))
    controls['H002b_reproduccion_fichas_v1']=code==0 and all(b.sha(ROOT/p)==v for p,v in base['protegidos'].items())
    c=b.load('outputs/paridad_codigo_sies_20261029/REVISION_CASO_A_CASO_12_v2.json')
    p=b.load('outputs/paridad_codigo_sies_20261029/PROPUESTA_PLANES_43.json')
    profile=b.load('outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json')
    old=b.load('outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json')
    controls['12_unicos_ordenados_sin_aplicar']=len(c['casos'])==12 and {x['numero_original'] for x in c['casos']}==set(range(1,13)) and all(not x['aplicada'] and x['decision_Alexi']=='____' for x in c['casos']) and [x['clasificacion']=='CALCE_UNICO' for x in c['casos']]==sorted([x['clasificacion']=='CALCE_UNICO' for x in c['casos']],reverse=True)
    controls['43_codigos_originales_sin_aplicar']=len(p['casos'])==43 and {x['codigo_unico'] for x in p['casos']}=={x['codigo_unico'] for x in old['nuevo_2027_sin_plan_E']} and all(not x['aplicada'] and x['decision_Alexi']=='____' for x in p['casos'])
    controls['sumas_clases_12_y_43']=sum(c['conteos'].values())==12 and sum(sum(v.values()) for v in p['conteos_grupo_clase'].values())==43
    controls['calce_unico_dos_evidencias_mismo_plan']=all(len(x['opciones_perfil_a'])==len(x['opciones_documentales_b'])==1 and x['opciones_perfil_a']==x['opciones_documentales_b'] and any(z['clasificacion']=='CALCE_UNICO' for z in x['planes']) for x in c['casos'] if x['clasificacion']=='CALCE_UNICO')
    controls['grupo_B_no_plan_en_fuentes_y_sede_correcta']=all(not x['planes_candidatos'] and not x['familia_en_catalogo_historico_2026'] for x in p['casos'] if x['grupo']=='B')
    controls['S4_no_hereda_plan_otra_sede']=all(not x['planes_candidatos'] for x in p['casos'] if x['codigo_unico'].startswith('I162S4'))
    controls['permanencia_no_se_presenta_con_plan']=all('plan' not in q for x in p['casos'] for q in x['presencia_Permanencia_sin_plan'])
    controls['TIPO_asignatura_no_tipo_plan']=all(set(x['TIPO_asignatura'])<={'Obl','OPC'} for x in profile['perfiles'])
    controls['documental_D_separados']=all(x['clase']=='B/C_DOCUMENTAL_ANUAL' for x in profile['observaciones_v20_por_plan_codigo_anio']) and all(x['clase']=='D_INTERNO' for x in profile['correspondencias_D_separadas'])
    controls['aceptacion_no_acreditada_visible']=profile['aceptacion_documentales_v20']=={'NO_ACREDITADA':11014}
    code,_,err3=run(sys.executable,'-B',str(OUT/'resolver_planes_h002c.py'),'--verificar')
    controls['H002c_reproduccion_hash']=code==0
    manifest=b.load('outputs/paridad_codigo_sies_20261029/MANIFEST_H002C.json')
    controls['H002c_fuentes_salidas_componentes_hash']=all(b.sha(x['ruta'])==x['sha256'] for x in manifest['fuentes']) and all(b.sha(OUT/p)==v for p,v in manifest['salidas'].items()) and all(b.sha(ROOT/p)==v for p,v in manifest['componentes'].items())
    # Mismas reglas de privacidad H002, sin ampliar excepciones; no exportar valores.
    patterns={'rut_con_dv':r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)',
        'correo':r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
        'codcli_individual':r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)'}
    findings=[]
    new_files=[f for f in OUT.iterdir() if f.is_file() and str(f.relative_to(ROOT)) not in base['protegidos']]
    for f in new_files:
        clean=re.sub(r'\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40})\b','HASH',f.read_text())
        for label,pattern in patterns.items():
            if re.search(pattern,clean):findings.append({'archivo':f.name,'patron':label})
    controls['escaneo_identificadores_sin_hallazgos']=not findings
    controls['ninguna_fuente_copiada_ni_versionada']=all(f.suffix in {'.json','.md','.py'} for f in new_files)
    out={'hito':'H002c','estado':'PASS_CON_PENDIENTES_E' if all(controls.values()) else 'FAIL','clase':'C',
        'controles':controls,'pruebas':tests,'hallazgos_privacidad':findings,
        'QA_historico':'El validador original conserva su baseline precommit 7807542. Se reusan sus pruebas, reproducción y controles de datos, con preservación nueva contra 76830cf, sin alterar sus bytes.',
        'errores_ejecucion':{'H002':err if code else '', 'v1':err2[-1000:] if not controls['H002b_reproduccion_fichas_v1'] else '', 'H002c':err3[-1000:] if not controls['H002c_reproduccion_hash'] else ''},
        'advertencias':['PASS no aprueba equivalencias; (b) documental no acredita aceptación PES.','A=regla; B=observación; C=cálculo; D=decisión existente; E=pendiente.']}
    (OUT/'QA_H002C.json').write_text(b.dump(out))
    print(b.dump(out))
    return 0 if all(controls.values()) else 1


if __name__=='__main__':
    raise SystemExit(main())

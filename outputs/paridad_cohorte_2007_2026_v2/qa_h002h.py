#!/usr/bin/env python3
"""QA de H002h; checks independientes y reproducción sin alterar lo previo."""
import argparse
import csv
import re
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
from construir_h002h import ROOT, OUT, DATA, sha, js, read


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reproducir',action='store_true');args=ap.parse_args()
    baseline=read(OUT/'ESTADO_INICIAL.json');manifest=read(DATA/'MANIFEST.json');r=read(OUT/'RESULTADOS.json')
    matrix=read(DATA/'MATRIZ_PARIDAD_COHORTE.json');hist=read(DATA/'CUADRATURA_COHORTES.json')
    splits=read(OUT/'REPARTOS_FORMA_INGRESO.json')['grupos'];diag=read(OUT/'DIAGNOSTICO_20.json')['codigos']
    rules=read(DATA/'REGLAS_CANDIDATAS.json')['reglas'];lots=read(OUT/'LOTES_REVISION_v3.json')['lotes']
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True)
    scope=('outputs/paridad_cohorte_2007_2026_v2/','data/paridad_codigo_sies/cohorte_2007_2026_v2/')
    checks={}
    checks['rama_head']=git('branch','--show-current').strip()=='feature/ire-2026'
    delta=git('diff','--name-only',baseline['head'],'HEAD').splitlines()
    ancestor=subprocess.run(['git','merge-base','--is-ancestor',baseline['head'],'HEAD'],cwd=ROOT).returncode==0
    checks['historial_desde_head_inicial_solo_H002h']=ancestor and all(p.startswith(scope) for p in delta)
    checks['24_ajenos_intactos']=sorted(x for x in git('status','--porcelain').splitlines() if not x[3:].startswith(scope))==sorted(baseline['ajenos'])
    checks['protegidos_intactos']=all(sha(ROOT/k)==v for k,v in baseline['protegidos'].items())
    checks['fuentes_hash']=all(sha(e['ruta'])==e['sha256'] for e in manifest['fuentes'])
    checks['salidas_hash']=all(sha(ROOT/k)==v for k,v in manifest['salidas'].items())
    checks['scripts_hash']=all(sha(ROOT/k)==v for k,v in manifest['scripts'].items())
    # SQL independiente: CASE jerárquico sobre original, primer año con ventana.
    src=next(e['ruta'] for e in manifest['fuentes'] if e['id']=='sies_individual')
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE t(y INT,c TEXT,f TEXT,p TEXT,ay INT,ase TEXT,oy INT,ose TEXT)')
    values=[]
    with open(src,encoding='utf-8-sig') as f:
        for x in csv.DictReader(f):
            integer=lambda v:int(v) if v.isdigit() else 0
            values.append((int(x['cat_periodo']),x['codigo_unico'],re.sub(r'V\d+$','',x['codigo_unico']),x['mrun'],integer(x['anio_ing_carr_act']),x['sem_ing_carr_act'],integer(x['anio_ing_carr_ori']),x['sem_ing_carr_ori']))
    db.executemany('INSERT INTO t VALUES(?,?,?,?,?,?,?,?)',values);del values
    query='''WITH q AS (SELECT *,MIN(y) OVER(PARTITION BY p,f) AS first_y FROM t), d AS
    (SELECT *,CASE WHEN ay>1900 AND ay<=y AND ase IN ('1','2') THEN 'a'
    WHEN oy>1900 AND oy<=y AND ose IN ('1','2') THEN 'b'
    WHEN p!='' AND first_y>=2008 THEN 'c' WHEN p!='' AND first_y=2007 THEN 'censurada'
    ELSE 'sin_identificador' END AS via FROM q) SELECT y,via,COUNT(*) FROM d GROUP BY y,via'''
    sql_counts={(y,v):n for y,v,n in db.execute(query)}
    checks['derivacion_SQL_independiente']=all(sql_counts.get((x['anio'],v),0)==x[v] for x in r['cohortes_vias'] for v in ['a','b','c','censurada','sin_identificador'])
    checks['20961_conservadas']=sum(x['matriculas'] for x in matrix['SIES'])==sum(x['total'] for x in r['cohortes_vias'])==20961
    mc=Counter()
    for x in matrix['SIES']:mc[x['anio'],x['codigo_sies']]+=x['matriculas']
    cc=read(OUT/'CONTROL_SIES_PUBLICACION.json')['filas']
    checks['publicacion_0_diferencias']=all(x['diferencia']==0 and mc[x['anio'],x['codigo_sies']]==x['publicacion'] for x in cc)
    checks['c_no_inventa_semestre']=all(x['cohorte_semestre']=='NO_OBSERVADO' for x in matrix['SIES'] if x['via_cohorte']=='c')
    checks['censura_no_asigna_ingreso']=all(x['cohorte_anio'] is None for x in matrix['SIES'] if x['via_cohorte']=='censurada')
    old_matrix=read(ROOT/'data/paridad_codigo_sies/cohorte_2007_2026/MATRIZ_PARIDAD_COHORTE.json')['filas']
    prior=Counter();now=Counter()
    for x in old_matrix:
        if x['origen']=='MU_DATOS_ALUMNOS' and x['codcarpr']!='SIN_ENLACE':prior[x['anio'],x['codigo_sies']]+=x['matriculas']
    for x in matrix['MU']:now[x['anio'],x['codigo_sies']]+=x['matriculas']
    checks['enlaces_MU_conservados']=+prior==+now
    checks['20_codigos_exactos']={x['codigo_sies'] for x in diag}=={x['codigo_sies'] for x in read(ROOT/'outputs/paridad_cohorte_2007_2026/VALIDACION_95_H002_v2.json')['codigos'] if x['estado']=='CONTRADICE'} and len(diag)==20
    checks['sin_regla_activa']=all(not x['activa'] for x in rules)
    checks['candidatas_sin_conflicto_interno']=all(len(x['codigos_matriculas_anuales'])==1 for x in rules if x['estado']=='CANDIDATA_LOCAL_SIN_EXCEPCIONES_OBSERVADAS')
    checks['ADMP_pendiente']=r['ADMP_CADMP'].startswith('PENDIENTE')
    checks['candidatas_SIES_sin_plan_UMAS']=all(not x['planes_observados'] and x['grupo_explicado_completo'] for x in rules if x['origen']=='SIES')
    checks['comparacion_mismo_universo']=sum(r['historia_mismo_universo'].values())==173 and sum(r['historia_casos_nuevos'].values())+173==len(hist['cohortes'])
    checks['explicaciones_sin_excepcion']=all(x['version_por_forma']['explicado'] and not x['version_por_forma']['conflictos'] and x['version_por_forma']['sin_dato']==0 for x in splits if x['estado']=='EXPLICADO_POR_FORMA_INGRESO')
    checks['fijadas_con_perfil']=all(x['estado']=='CUADRA_EXACTO' and not x['cohorte_censurada_filas'] and all(v=='PERFIL_FORMAL_COMPATIBLE' for v in x['perfiles'].values()) for x in hist['cohortes'] if x['fijacion']=='FIJADA_C')
    counts=Counter(x['estado'] for x in hist['cohortes'])
    checks['estados_historia_suman']=dict(counts)==r['historia_ahora'] and sum(counts.values())==len(hist['cohortes'])
    checks['lotes_unicos']=len(lots)==len({(x['familia'],x['problema']) for x in lots})
    groups=defaultdict(set)
    for x in lots:groups[x['lote']].add(re.sub(r'J\d+$','',x['familia']))
    checks['max5_carreras']=all(len(v)<=5 for v in groups.values())
    checks['lotes_contiguos']= [x['lote'] for x in lots]==sorted(x['lote'] for x in lots)
    violations=[]
    for folder in [OUT,DATA]:
        for p in folder.iterdir():
            if not p.is_file() or p.name=='QA.json':continue
            text=p.read_text();text=re.sub(r'\b[0-9a-fA-F]{40,64}\b','HASH',text)
            patterns=[r'\b\d{7,8}-[0-9Kk]\b',r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b',r'(?i)"(?:mrun|RUT|CODCLI|N_DOC|fec_nac_alu)"\s*:\s*"?\d+',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}']
            if any(re.search(pat,text) for pat in patterns):violations.append(str(p.relative_to(ROOT)))
    checks['privacidad']=not violations
    checks['markdown_limpio']=all(all(l==l.rstrip() for l in p.read_text().splitlines()) for d in [OUT,DATA] for p in d.glob('*.md'))
    tests=[]
    for directory in [OUT,ROOT/'outputs/paridad_cohorte_2007_2026',ROOT/'outputs/paridad_codigo_sies_20261029']:
        run=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(directory),'-p','test_*.py'],cwd=ROOT,capture_output=True,text=True)
        tests.append({'ruta':str(directory.relative_to(ROOT)),'returncode':run.returncode,'resultado':run.stderr})
    checks['pruebas']=all(x['returncode']==0 for x in tests)
    reproduction=None
    if args.reproducir:
        run=subprocess.run([sys.executable,'-B',str(OUT/'construir_h002h.py'),'--verificar'],cwd=ROOT,capture_output=True,text=True)
        reproduction={'returncode':run.returncode,'resultado':'0 diferencias de bytes' if not run.returncode else run.stderr}
        checks['reproduccion']=not run.returncode
    result={'estado':'PASS_CON_PENDIENTES_E' if all(checks.values()) else 'FAIL','controles':checks,'pruebas':tests,'reproduccion':reproduction,'privacidad_violaciones':violations,'pendientes':r['causalidad_limites']}
    (OUT/'QA.json').write_text(js(result))
    print(js({'estado':result['estado'],'controles':len(checks),'fallos':[k for k,v in checks.items() if not v],'pruebas':tests,'reproduccion':reproduction}))
    return 0 if all(checks.values()) else 1

if __name__=='__main__':raise SystemExit(main())

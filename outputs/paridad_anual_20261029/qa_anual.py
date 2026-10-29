#!/usr/bin/env python3
"""QA independiente de H002f; conciliación SQL privada y salidas agregadas."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
DATA=ROOT/'data/paridad_codigo_sies/anual_20261029'
sys.path.insert(0,str(OUT))
from construir_anual import sha,js,read,PRIVATE


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode()


def main():
    p=argparse.ArgumentParser();p.add_argument('--reproducir',action='store_true');args=p.parse_args()
    initial=read(OUT/'ESTADO_INICIAL.json');manifest=read(DATA/'MANIFEST.json')
    matrix=read(DATA/'MATRIZ_PARIDAD_ANUAL.json')['filas'];result=read(OUT/'RESULTADOS.json')
    balances=read(OUT/'CONTROL_POR_CODIGO_ANIO.json')['filas'];validation=read(OUT/'VALIDACION_95_H002.json')['filas']
    checks={}
    checks['rama']=git('branch','--show-current').strip()=='feature/ire-2026'
    checks['base_preservada_en_historia']=subprocess.run(['git','merge-base','--is-ancestor',initial['HEAD'],'HEAD'],cwd=ROOT).returncode==0
    checks['fuentes_integras']=all(sha(x['ruta'])==x['sha256'] for x in manifest['fuentes'])
    checks['salidas_hash']=all(sha(ROOT/k)==v for k,v in manifest['salidas'].items())
    checks['script_hash']=sha(ROOT/manifest['generador']['ruta'])==manifest['generador']['sha256']
    checks['auxiliares_hash']=all(sha(ROOT/k)==v for k,v in manifest['auxiliares'].items())
    checks['protegidos_H002_v20_grupos_ajenos']=all(sha(ROOT/k)==v for k,v in initial['protegidos'].items())
    scope=('data/paridad_codigo_sies/anual_20261029/','outputs/paridad_anual_20261029/')
    status=git('status','--porcelain').splitlines()
    checks['24_ajenos_intactos']=sorted(s for s in status if not s[3:].startswith(scope))==sorted(initial['status_ajeno'])
    changed=git('diff','--name-only').splitlines()+git('diff','--cached','--name-only').splitlines()
    checks['cambios_solo_nuevos_H002f']=all(x.startswith(scope) for x in changed)
    mr=[r for r in matrix if r['anio']>=2022];hist=[r for r in matrix if r['anio']<2022]
    checks['todas_filas_MU_por_anio']={y:sum(x['matriculas_mu_incluidas']+x['matriculas_mu_excluidas_vig'] for x in mr if x['anio']==y) for y in range(2022,2027)}=={2022:1038,2023:1145,2024:1541,2025:2371,2026:4105}
    # Ruta independiente SQL: reconstruir totales y clasificación desde la traza privada.
    detail=read(PRIVATE/'ENLACES_MU_PLAN.json');db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE enlaces(anio INT,codigo TEXT,incluida INT,car TEXT,plan TEXT,sede TEXT,jornada TEXT,motivo TEXT)')
    for r in detail:
        v=r['seleccion'];car,plan,site,j=(v[1],v[2],v[3],v[4]) if v else ('SIN_ENLACE','SIN_ENLACE','','')
        db.execute('INSERT INTO enlaces VALUES(?,?,?,?,?,?,?,?)',(r['anio'],r['codigo_sies'],int(r['incluida']),car,plan,site,j,r['motivo']))
    sql={(y,c,car,pl,s,j,why):(n,ex) for y,c,car,pl,s,j,why,n,ex in db.execute('SELECT anio,codigo,car,plan,sede,jornada,motivo,SUM(incluida),SUM(1-incluida) FROM enlaces GROUP BY anio,codigo,car,plan,sede,jornada,motivo')}
    actual={(r['anio'],r['codigo_sies'],r['codcarpr'],r['plan_umas'],r['sede_umas'],r['jornada_umas'],r['sin_enlace_motivo'] or 'ENLAZADO_UNICO'):(r['matriculas_mu_incluidas'],r['matriculas_mu_excluidas_vig']) for r in mr}
    checks['SQL_independiente_matriz_0_diferencias']=sql==actual
    sqlcode={(y,c):(n,total) for y,c,n,total in db.execute('SELECT anio,codigo,SUM(incluida),COUNT(*) FROM enlaces GROUP BY anio,codigo')}
    checks['suma_por_codigo_conserva_seleccion_y_fuera']=all(sqlcode.get((b['anio'],b['codigo_sies']),(0,0))==(b['mu_seleccionada'],b['filas_mu']) for b in balances)
    checks['enlazados_mas_sin_enlace_igual_mu']=all(b['matriculas_enlazadas']+b['matriculas_sin_enlace']==b['mu_seleccionada'] for b in balances)
    sqlgroups={(y,ca,pl,s,j):n for y,ca,pl,s,j,n in db.execute("SELECT anio,car,plan,sede,jornada,COUNT(DISTINCT codigo) FROM enlaces WHERE incluida=1 AND car!='SIN_ENLACE' GROUP BY anio,car,plan,sede,jornada")}
    checks['repartidos_contados_por_codigo_distinto']=all((r['estado']=='REPARTIDO')==(sqlgroups[(r['anio'],r['codcarpr'],r['plan_umas'],r['sede_umas'],r['jornada_umas'])]>1) for r in mr if r['matriculas_mu_incluidas'] and r['codcarpr']!='SIN_ENLACE')
    checks['sin_duplicar_matriculas_por_join']=len({r['fila_mu'] for r in detail})==len(detail)==10200
    checks['no_elige_enlace_ambiguo']=all(not r['seleccion'] or len(r['candidatos'])==1 for r in detail)
    checks['toda_seleccion_tiene_fuentes_da_y_actividad']=all(not r['seleccion'] or (r['referencias_DA'] and r['referencias_PROMEDIOS']) for r in detail)
    checks['control_total_publicado_no_ajustado']=all(b['diferencia_sies_menos_mu']==b['sies_total']-b['mu_seleccionada'] for b in balances)
    checks['anclas_declaradas_sin_falsos_cierres']={x['anio']:x['codigos_con_diferencia'] for x in result['anual']}=={2022:0,2023:2,2024:0,2025:0,2026:48}
    checks['2026_no_ancla']=all(not b['ancla_codigo'] for b in balances if b['anio']==2026)
    checks['puente_reutilizado']=result['puente_reproducido'] is True
    checks['95_codigos_unicos']=len(validation)==len({v['codigo_sies'] for v in validation})==95
    checks['confirma_solo_con_enlace_completo']=all(v['coincidentes']>0 and v['contradictorias']==0 and v['sin_enlace']==0 and v['anio_ancla_mas_reciente'] in [2022,2023,2024,2025] for v in validation if v['estado']=='CONFIRMA')
    checks['historico_no_atribuye_version']=all(r['clase']=='C/E' and not r['asignacion_version_autorizada'] and not r['codigo_es_destino_observado'] for r in hist)
    checks['historico_tolerancia_10']=all((r['estado']=='CUADRA_TOTAL')==(r['expedientes_actividad_anual']==r['sies_codigo_total']) and (r['estado']!='APROXIMA' or 0<abs(r['diferencia_porcentaje'])<=10) for r in hist)
    for name,key in [('MATRIZ_PARIDAD_ANUAL','filas'),('RESUMEN_POR_CARRERA','carreras')]:
        with (DATA/(name+'.csv')).open() as f:rr=list(csv.DictReader(f,delimiter=';'))
        checks['CSV_JSON_'+name]=len(rr)==len(read(DATA/(name+'.json'))[key])
    checks['lotes_cinco_carreras']=result['lotes_revision']['lotes']==(result['lotes_revision']['carreras']+4)//5
    tests=[]
    for folder,pattern in [(OUT,'test_*.py'),(ROOT/'outputs/paridad_codigo_sies_20261029','test_*.py')]:
        run=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(folder),'-p',pattern],cwd=ROOT,capture_output=True,text=True)
        tests.append({'directorio':str(folder.relative_to(ROOT)),'returncode':run.returncode,'resumen':run.stderr[-2500:]})
    checks['pruebas']=all(t['returncode']==0 for t in tests)
    scans=[];violations=[]
    for folder in [DATA,OUT]:
        for path in sorted(folder.iterdir()):
            if not path.is_file() or path.name=='QA.json':continue
            text=path.read_text()
            scrub=re.sub(r'\b[0-9a-f]{40,64}\b','HASH',text,flags=re.I)
            # Detecta valores, no nombres de campos ni códigos de catálogo.
            patterns=[r'\b\d{7,8}-[0-9Kk]\b',r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b',r'(?i)"(?:N_DOC|NUM_DOCUMENTO|CODCLI|RUT)"\s*:\s*"?\d{6,}',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}']
            for pat in patterns:
                if re.search(pat,scrub):violations.append({'archivo':str(path.relative_to(ROOT)),'regla':pat})
            scans.append(str(path.relative_to(ROOT)))
    checks['privacidad_0_identificadores']=not violations
    checks['markdown_sin_espacios_finales']=all(all(line==line.rstrip() for line in p.read_text().splitlines()) and not p.read_bytes().endswith(b'\n\n') for folder in [DATA,OUT] for p in folder.glob('*.md'))
    repro=None
    if args.reproducir:
        run=subprocess.run([sys.executable,'-B',str(OUT/'construir_anual.py'),'--verificar'],cwd=ROOT,capture_output=True,text=True)
        repro={'returncode':run.returncode,'resultado':'PASS' if run.returncode==0 else run.stderr[-2000:]}
        checks['reproduccion_completa_desde_fuentes']=run.returncode==0
    elif (OUT/'QA.json').exists():
        prev=read(OUT/'QA.json');repro=prev.get('reproduccion')
        checks['reproduccion_completa_desde_fuentes']=bool(repro and repro['returncode']==0 and prev.get('manifest_sha256')==sha(DATA/'MANIFEST.json'))
    else:checks['reproduccion_completa_desde_fuentes']=False
    checks['arbol_privado_no_publicado']=all(not x.startswith('.local') for x in git('ls-files',str(PRIVATE)).splitlines()) if PRIVATE.is_relative_to(ROOT) else True
    qa={'estado':'PASS_CON_PENDIENTES_E' if all(checks.values()) else 'FAIL','controles':checks,'pruebas':tests,
        'reproduccion':repro,'manifest_sha256':sha(DATA/'MANIFEST.json'),'archivos_escaneados':scans,'violaciones':violations,
        'clase':'C','alcance':'Integridad y reproducibilidad; PASS no equivale a paridad histórica cerrada.',
        'pendientes':{'sin_enlace_por_anio':{str(x['anio']):x['sin_enlace_matriculas'] for x in result['anual']},'validacion_95':result['validacion_95']}}
    (OUT/'QA.json').write_text(js(qa))
    print(js({'estado':qa['estado'],'controles':len(checks),'fallos':[k for k,v in checks.items() if not v],'pruebas':tests}))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

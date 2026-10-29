#!/usr/bin/env python3
"""QA H002g: sumas independientes y conservación; no certifica hipótesis."""
import argparse,json,re,subprocess,sys,hashlib,sqlite3
from pathlib import Path
from collections import Counter,defaultdict
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;DATA=ROOT/'data/paridad_codigo_sies/cohorte_2007_2026'
from construir_cohortes import sha,js,read,PRIVATE

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--reproducir',action='store_true');args=ap.parse_args()
    initial=read(OUT/'ESTADO_INICIAL.json');m=read(DATA/'MANIFEST.json');matrix=read(DATA/'MATRIZ_PARIDAD_COHORTE.json')['filas'];results=read(OUT/'RESULTADOS.json');rules=read(DATA/'REGLAS_VERSION_POR_COHORTE.json')['reglas'];controls=read(OUT/'CONTROL_SIES_PUBLICACION.json')['filas'];mucontrols=read(OUT/'CONTROL_MU_PUBLICACION.json')['filas'];lots=read(OUT/'LOTES_REVISION_v2.json')['lotes'];valid=read(OUT/'VALIDACION_95_H002_v2.json')['codigos'];detail=read(PRIVATE/'ENLACES_MU_DA.json');checks={}
    git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT,text=True)
    scope=('data/paridad_codigo_sies/cohorte_2007_2026/','outputs/paridad_cohorte_2007_2026/')
    checks['rama_correcta']=git('branch','--show-current').strip()=='feature/ire-2026'
    checks['head_esperado']=git('rev-parse','HEAD').strip()==initial['head']
    checks['24_ajenos_status_intacto']=sorted(x for x in git('status','--porcelain').splitlines() if not x[3:].startswith(scope))==sorted(initial['ajenos'])
    checks['H002_H002f_v20_fuentes_ajenos_intactos']=all(sha(ROOT/k)==v for k,v in initial['protegidos'].items())
    checks['inputs_hash']=all(sha(e['ruta'])==e['sha256'] for e in m['fuentes'])
    checks['output_hash']=all(sha(ROOT/k)==v for k,v in m['salidas'].items())
    checks['generador_hash']=sha(ROOT/m['generador']['ruta'])==m['generador']['sha256']
    checks['sies_20961']=sum(r['matriculas'] for r in matrix if r['origen']=='SIES_INDIVIDUAL')==20961
    sc=Counter()
    for r in matrix:
        if r['origen']=='SIES_INDIVIDUAL':sc[r['anio'],r['codigo_sies']]+=r['matriculas']
    checks['micro_publico_0_diferencias']=all(r['diferencia']==0 and sc[r['anio'],r['codigo_sies']]==r['publicacion'] for r in controls)
    checks['no_cohorte_SIES_2026_inventada']=all(r['anio']<=2025 for r in matrix if r['origen']=='SIES_INDIVIDUAL')
    # Ruta SQL independiente de los conteos del generador, desde el detalle privado MU.
    db=sqlite3.connect(':memory:');db.execute('CREATE TABLE detalle(linea INT,anio INT,codigo TEXT,incluida INT,enlace INT)')
    db.executemany('INSERT INTO detalle VALUES(?,?,?,?,?)',[(r['fila_fuente_mu'],r['anio'],r['codigo_sies'],int(r['incluida']),int(bool(r['seleccion']))) for r in detail])
    counts={(y,c):(n,total) for y,c,n,total in db.execute('SELECT anio,codigo,SUM(incluida),COUNT(*) FROM detalle GROUP BY anio,codigo')}
    checks['MU_10200_una_vez']=db.execute('SELECT COUNT(*),COUNT(DISTINCT linea) FROM detalle').fetchone()==(10200,10200)
    checks['SQL_totales_codigo']=all(counts.get((r['anio'],r['codigo_sies']),(0,0))==(r['mu_seleccionada'],r['mu_seleccionada']+r['mu_excluida']) for r in mucontrols)
    mm=Counter()
    for r in matrix:
        if r['origen']=='MU_DATOS_ALUMNOS':mm[r['anio'],r['codigo_sies']]+=r['matriculas'];mm[r['anio'],r['codigo_sies'],'todas']+=r['matriculas']+r['excluidas_vig']
    checks['matriz_conserva_MU']=all(mm[y,c]==n and mm[y,c,'todas']==t for (y,c),(n,t) in counts.items())
    ca={y:(n,linked,nt,lt) for y,n,linked,nt,lt in db.execute('SELECT anio,SUM(incluida),SUM(incluida*enlace),COUNT(*),SUM(enlace) FROM detalle GROUP BY anio')}
    checks['SQL_cobertura']=all(ca[r['anio']]==(r['seleccionadas'],r['enlace_seleccionadas'],r['filas_mu'],r['enlace_todas']) for r in results['anual'])
    checks['enlace_sin_actividad_conservado']=sum(bool(r['seleccion']) and r['plan']=='PLAN_NO_OBSERVADO' for r in detail)>0
    checks['sin_eleccion_fuera_candidatos']=all(not r['seleccion'] or r['seleccion'] in r['candidatos'] for r in detail)
    checks['anclas_no_modificadas']={y:sum(r['diferencia']!=0 for r in mucontrols if r['anio']==y) for y in range(2022,2027)}=={2022:0,2023:2,2024:0,2025:0,2026:48}
    checks['brecha_226_intacta']=sum(r['diferencia'] for r in mucontrols if r['anio']==2026)==226
    checks['95_unicos']=len(valid)==len({r['codigo_sies'] for r in valid})==95
    checks['sin_falso_confirma']=all(not r['cohortes_con_reparto'] and r['matriculas_anuales_con_plan_y_cohorte']>0 and r['sin_enlace_o_plan_o_cohorte']==0 for r in valid if r['estado']=='CONFIRMA')
    checks['reparto_declarado']=all((len(r['codigos_y_matriculas_anuales'])>1)==(r['estado']=='COHORTE_REPARTIDA_E') for r in rules)
    checks['no_regla_fija_si_cambios']=not results['regla_fija_confirmada'] if results['estabilidad_sies_transiciones']['CAMBIA'] else True
    checks['lotes_sin_fragmentos']=len(lots)==len({(r['familia'],r['problema']) for r in lots}) and all(r['problema']!='SIN_ENLACE' for r in lots)
    lotcars=defaultdict(set)
    for r in lots:lotcars[r['lote']].add(re.sub(r'J\d+$','',r['familia']))
    checks['maximo_cinco_carreras_lote']=all(len(v)<=5 for v in lotcars.values())
    violations=[]
    for folder in [DATA,OUT]:
        for p in folder.iterdir():
            if not p.is_file() or p.name=='QA.json':continue
            s=p.read_text();s=re.sub(r'\b[0-9a-fA-F]{40,64}\b','HASH',s)
            patterns=[r'\b\d{7,8}-[0-9Kk]\b',r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b',r'(?i)"(?:mrun|RUT|CODCLI|N_DOC|fec_nac_alu)"\s*:\s*"?\d+',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}']
            if any(re.search(x,s) for x in patterns):violations.append(str(p.relative_to(ROOT)))
    checks['privacidad_sin_identificadores']=not violations
    checks['markdown_limpio']=all(not p.read_bytes().endswith(b'\n\n') and all(x==x.rstrip() for x in p.read_text().splitlines()) for folder in [DATA,OUT] for p in folder.glob('*.md'))
    tests=[]
    for folder in [OUT,ROOT/'outputs/paridad_codigo_sies_20261029']:
        proc=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(folder),'-p','test_*.py'],cwd=ROOT,capture_output=True,text=True);tests.append({'ruta':str(folder.relative_to(ROOT)),'returncode':proc.returncode,'resultado':proc.stderr})
    checks['pruebas']=all(x['returncode']==0 for x in tests)
    rep=None
    if args.reproducir:
        proc=subprocess.run([sys.executable,'-B',str(OUT/'construir_cohortes.py'),'--verificar'],cwd=ROOT,capture_output=True,text=True);rep={'returncode':proc.returncode,'resultado':proc.stderr if proc.returncode else 'Reproducción íntegra, cero diferencias de bytes'};checks['reproducible']=proc.returncode==0
    result={'estado':'PASS_CON_PENDIENTES_E' if all(checks.values()) else 'FAIL','controles':checks,'pruebas':tests,'reproduccion':rep,'privacidad_violaciones':violations,'pendientes':'Cohorte actual ausente; período UMAS no homologado históricamente; cambios de código; cobertura/planes incompletos; ADMP/CADMP no aprobado; sin adjudicación.'}
    (OUT/'QA.json').write_text(js(result));print(js({'estado':result['estado'],'controles':len(checks),'fallos':[k for k,v in checks.items() if not v],'tests':tests,'reproduccion':rep}));return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(main())

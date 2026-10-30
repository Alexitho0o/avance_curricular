#!/usr/bin/env python3
"""QA H002l: preservación, pruebas, repetibilidad y privacidad de agregados."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT));import construir

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    built,manual,info,totals=construir.construir()
    assert all((ROOT/p).read_bytes()==b for p,b in built.items())
    meta=json.loads((OUT/'ESTADO_INICIAL.json').read_text());p=Path(meta['snapshot_privado']);assert sha(p)==meta['sha256'];initial=json.loads(p.read_text())
    allowed=set(built)|{'common/codigo_sies_mu2027.py','docs/ESPECIFICACION_H002L.md'}
    allowed|={str(f.relative_to(ROOT)) for f in OUT.iterdir() if f.is_file()}
    allowed|={str((OUT/f).relative_to(ROOT)) for f in ['QA_FINAL.json','ARCHIVOS_PROPUESTOS.json','MANIFEST_H002L.json']}
    protected=set(initial['versionados'])-allowed
    assert all((ROOT/p).is_file() and sha(ROOT/p)==initial['versionados'][p] for p in protected),'Protegido alterado'
    assert all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in initial['ajenos'].items()),'Ajeno alterado'
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    assert len(initial['status'].splitlines())==24 and all(s in status.splitlines() for s in initial['status'].splitlines())
    tests=[]
    for d,pattern in [(str(OUT.relative_to(ROOT)),'test_*.py'),('outputs/paridad_codigo_sies_20261029','test_h002b.py'),('tests','test_normalizacion_dv_cero_fase_c.py')]:
        p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',d,'-p',pattern,'-q'],cwd=ROOT,capture_output=True,text=True)
        if p.returncode:raise ValueError('Pruebas fallidas: '+d+'\n'+p.stderr)
        tests.append({'ruta':d,'patron':pattern,'pruebas':int(re.search(r'Ran (\d+) tests?',p.stderr)[1]),'estado':'PASS'})
    (OUT/'ARCHIVOS_PROPUESTOS.json').write_bytes(construir.js({'archivos':sorted(allowed),'restriccion':'Sólo H002l; tabla H002, v1, fuentes y ajenos intactos.'}))
    # Identificadores privados utilizados sólo en memoria para escanear coincidencias.
    rule=json.loads((ROOT/'data/reglas_negocio/mu2027/REGLA_CODIGO_SIES_MU2027.json').read_text())
    private=json.loads(Path(rule['fuentes']['prueba_privada_H002j']['ruta']).read_text());ids=set()
    for r in private:
        ident=r.get('identidad')
        if ident and len(str(ident[1]))>=7:ids.add(str(ident[1]))
        e=r.get('expediente')
        if e is not None and len(str(e))>=7:ids.add(str(e))
    idrx=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(v) for v in sorted(ids,key=len,reverse=True))+r')(?![A-Za-z0-9])')
    rx=re.compile(r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b')
    failures=[];scanned=[]
    for path in sorted(allowed):
        p=ROOT/path
        if not p.exists():continue
        text=re.sub(r'\b[0-9a-fA-F]{20,}\b','HASH',p.read_text());n=len(rx.findall(text))+len(idrx.findall(text))
        if n:failures.append({'archivo':path,'coincidencias':n})
        scanned.append(path)
    if failures:raise ValueError('Privacidad: '+str(failures))
    # Método independiente por código de oferta: no consulta tipo/plan.
    from common.codigo_sies_mu2027 import cargar_contexto
    _,offer,rows,_=cargar_contexto();by={r['codigo_unico']:r['vigencia_2027'] for r in offer}
    independent={'sin_codigo':sum(not r.get('real') for r in rows.values()),'sin_oferta':sum(bool(r.get('real')) and r['real'] not in by for r in rows.values()),
                 'vigencia_3':sum(by.get(r.get('real'))=='3' for r in rows.values())}
    assert sum(independent.values())==totals['antiguos']['revision_H002l']
    final={'estado':'PASS','clase':'C','tests':tests,'total_tests':sum(t['pruebas'] for t in tests),'reproduccion_salidas':len(built),'diferencias':0,
        'controles':{'tabla_H002_inalterada':True,'v1_inalterada':True,'regla_ACTIVA':rule['estado']=='ACTIVA','antiguos_sin_tipo_como_filtro':True,
                    'antiguos_conciliados':totals['antiguos']['conservan_codigo']+totals['antiguos']['revision_H002l']==4105,
                    'opciones_nuevos_conciliadas':sum(totals['nuevos'][k] for k in ['asignacion','revision_real','informativos'])==223},
        'independiente_por_codigo':independent,'preservacion':{'versionados':len(protected),'entradas_ajenas':24,'archivos_ajenos_por_hash':len(initial['ajenos'])},
        'privacidad':{'coincidencias':0,'archivos':len(scanned),'metodo':'Patrones, identificadores privados sólo en memoria y revisión de estructura agregada; detalle fuera de Git.'},
        'totales':totals,'limite':'No son alumnos observados 2027 ni carga; 37 códigos permanecen E. Pruebas H002k se reproducen con su versión congelada.'}
    assert all(final['controles'].values())
    (OUT/'QA_FINAL.json').write_bytes(construir.js(final))
    (OUT/'MANIFEST_H002L.json').write_bytes(construir.js({'hito':'H002l','base_commit':construir.BASE,'fuentes':json.loads((OUT/'FUENTES.json').read_text()),
        'archivos':{f:sha(ROOT/f) for f in sorted(allowed) if (ROOT/f).exists() and f!=str((OUT/'MANIFEST_H002L.json').relative_to(ROOT))},'datos_personales':False}))
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    print(json.dumps({'estado':'PASS','pruebas':final['total_tests'],'archivos':len(allowed),'preservacion':final['preservacion'],'escaneo_coincidencias':0},ensure_ascii=False))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""QA H002k: reproducción, pruebas, privacidad y preservación; sólo agregados."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT));import construir

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    built,detail,qa=construir.construir()
    for rel,raw in built.items():
        if (ROOT/rel).read_bytes()!=raw:raise ValueError('Reproducción distinta: '+rel)
    snapshot=json.loads((OUT/'ESTADO_INICIAL.json').read_text())
    private=Path(snapshot['respaldo_privado'])
    assert digest(private)==snapshot['sha256_respaldo_privado']
    before=json.loads(private.read_text())
    explicit=set(built)|{'common/codigo_sies_mu2027.py','docs/ESPECIFICACION_H002K.md','data/paridad_codigo_sies/20261029/DECISIONES_APROBADAS_v3.json'}
    explicit|={str(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()}
    explicit|={str((OUT/p).relative_to(ROOT)) for p in ['QA_FINAL.json','ARCHIVOS_PROPUESTOS.json','MANIFEST_H002K.json']}
    excluded=set(before['versionados'])-explicit
    altered=[p for p in sorted(excluded) if not (ROOT/p).is_file() or digest(ROOT/p)!=before['versionados'][p]]
    assert not altered, 'Archivo protegido alterado: '+str(altered)
    status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    original=before['status_ajeno'].splitlines()
    assert len(original)==24 and all(line in status.splitlines() for line in original)
    # Lista explícita; nunca abarca oferta ni otros outputs previos.
    manifest={'archivos':sorted(explicit),'excluidos':'Los 24 ajenos, bases y detalle privado; ningún commits.sh'}
    (OUT/'ARCHIVOS_PROPUESTOS.json').write_bytes(construir.js(manifest))
    tests=[]
    for directory,pattern in [(str(OUT.relative_to(ROOT)),'test_*.py'),('outputs/paridad_codigo_sies_20261029','test_h002b.py'),('outputs/regla_operativa_mu_v2_20261029','test_regla_v2.py'),('tests','test_normalizacion_dv_cero_fase_c.py')]:
        proc=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',directory,'-p',pattern,'-q'],cwd=ROOT,capture_output=True,text=True)
        if proc.returncode:raise ValueError('Pruebas fallan: '+directory+'\n'+proc.stderr)
        match=re.search(r'Ran (\d+) tests?',proc.stderr);tests.append({'ruta':directory,'patron':pattern,'pruebas':int(match[1]),'estado':'PASS'})
    sources=construir.read(str(OUT.relative_to(ROOT))+'/FUENTES.json')
    rows=construir.read(sources['prueba_privada_H002j']['ruta'])
    ids=set()
    for row in rows:
        ident=row['identidad']
        if ident and len(str(ident[1]))>=7:ids.add(str(ident[1]))
        if row.get('expediente') is not None and len(str(row['expediente']))>=7:ids.add(str(row['expediente']))
    # No devuelve coincidencias ni valores; sólo archivo/cantidad ante fallo.
    id_re=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(v) for v in sorted(ids,key=len,reverse=True))+r')(?![A-Za-z0-9])')
    pattern=re.compile(r'(?<!\w)(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?!\w)|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b')
    scanned=[];fail=[]
    for rel in sorted(explicit):
        p=ROOT/rel
        if not p.is_file():continue
        text=p.read_text();text=re.sub(r'\b[0-9a-fA-F]{20,}\b','HASH',text)
        n=len(pattern.findall(text))+len(id_re.findall(text))
        if n:fail.append({'archivo':rel,'coincidencias':n})
        scanned.append(rel)
    if fail:raise ValueError('Privacidad bloqueante, revisar en privado: '+str(fail))
    # Hashes de las skills: ninguna instalación se modifica.
    skills=json.loads((OUT/'REVISION_SKILLS.json').read_text())
    assert all(digest(Path(x['ruta']))==x['sha256'] for x in skills['archivos'])
    final={'estado':'PASS','clase':'C','reproduccion':{'salidas':len(built),'diferencias':0},'pruebas':tests,'total_pruebas':sum(t['pruebas'] for t in tests),
        'preservacion':{'versionados_fuera_alcance_intactos':len(excluded),'cambios_ajenos_intactos':24,'skills_instaladas_intactas':len(skills['archivos'])},
        'privacidad':{'archivos_escaneados':len(scanned),'coincidencias':0,'metodo':'Patrones de documento/correo y coincidencia con identificadores privados sólo en memoria; revisión de campos agregados.',
                      'detalle_nominativo':'~/.local/share/ipss/h002k_20261029/LISTA_REVISION_MANUAL_MU2027.json'},
        'tabla':{'filas_modificadas':qa['filas_modificadas'],'restantes_intactas':265,'conteos':qa['conteos']},
        'manual':qa['revision'],'nuevos_catalogo':qa['nuevos_catalogo'],'familias_ambiguas':len(qa['familias_ambiguas']),
        'limites':['37 códigos y revisión manual no equivalen a paridad completa de alumnos 2027.',
                   'Los tests de promoción H002e se reproducen en su commit histórico; no se cambia su expectativa para hacerlos pasar sobre H002k.']}
    (OUT/'QA_FINAL.json').write_bytes(construir.js(final))
    hashes={p:digest(ROOT/p) for p in sorted(explicit) if (ROOT/p).is_file() and p!=str((OUT/'MANIFEST_H002K.json').relative_to(ROOT))}
    (OUT/'MANIFEST_H002K.json').write_bytes(construir.js({'hito':'H002k','base_commit':construir.BASE,'archivos_sha256':hashes,'datos_personales':False}))
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    print(json.dumps({'estado':'PASS','pruebas':final['total_pruebas'],'archivos':len(explicit),'preservacion':final['preservacion'],'privacidad_coincidencias':0},ensure_ascii=False))
if __name__=='__main__':main()

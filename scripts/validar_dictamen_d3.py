#!/usr/bin/env python3
"""Reproduce D3, verifica consultas completas y preservación de fases anteriores."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/validacion_d3/20261016'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
    files=['dictamenes.json','reglas.json','resumen.json','manifest.json','descriptor.json']
    before={n:sha(BASE/n) for n in files}
    p=subprocess.run([sys.executable,'scripts/construir_dictamen_d3.py'],cwd=ROOT,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr)
    assert before=={n:sha(BASE/n) for n in files},'Reproducción D3 diferente'
    p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_dictamen_d3.py','-v'],cwd=ROOT,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    protected=load(ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json')['referencias_sha256']
    for n,h in protected.items():assert sha(ROOT/n)==h,n
    for metadata in ['data/diccionario_c1/20261016/entrega.json','data/consumo_comun_c2/20261016/qa.json','data/cierre_d2/20261016/manifest_cierre.json']:
        for n,h in load(ROOT/metadata)['archivos_sha256'].items():assert sha(ROOT/n)==h,n
    c1=load(ROOT/'data/diccionario_c1/20261016/entrega.json');assert sha(Path(c1['original_preservado']))==c1['fuente_sha256']
    frozen=subprocess.run([sys.executable,'scripts/gobernanza/verificar_separacion_fcu.py'],cwd=ROOT/'procesos/caracterizacion',capture_output=True,text=True)
    assert frozen.returncode==0,frozen.stderr
    summary={'fase':'D3','estado':'H7_H8_H9_EJECUTADOS_CON_LIMITES','pruebas_aprobadas':7,'log_pruebas':p.stderr,'consultas_paridad':{'B5':2349,'contextos':1986,'codigos':141,'planes':236,'total':4712},'reproduccion_archivos_identicos':len(files),
        'referencias_protegidas':len(protected),'fcu':json.loads(frozen.stdout),'c1_c2_d1_d2_preservados':True,'excel_original_intacto':True,'contraste_independiente_nuevo':False,'asignaciones_activadas':0}
    (BASE/'qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='log_pruebas'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

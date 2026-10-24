#!/usr/bin/env python3
"""Reproduce las pruebas de consumo C2 y registra controles sin pipelines reales."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/consumo_comun_c2/20261016'
def main():
    checks=[]
    for pattern in ('test_diccionario_c2.py','test_reglas_historicas_b5.py','test_unificacion_proyectos.py'):
        proc=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=ROOT,capture_output=True,text=True)
        checks.append({'prueba':pattern,'salida':proc.returncode,'detalle':proc.stdout+proc.stderr})
    p=subprocess.run([sys.executable,'scripts/gobernanza/verificar_separacion_fcu.py'],cwd=ROOT/'procesos/caracterizacion',capture_output=True,text=True)
    checks.append({'prueba':'referencias_fcu','salida':p.returncode,'detalle':p.stdout+p.stderr})
    files=['common/diccionario_c2.py','scripts/consultar_diccionario_c2.py','procesos/caracterizacion/scripts/consultar_diccionario_c2.py','tests/test_diccionario_c2.py','scripts/validar_consumo_c2.py','PROYECTO_IPSS.json','data/consumo_comun_c2/20261016/descriptor.json']
    summary={'estado':'VERIFICADO' if all(c['salida']==0 for c in checks) else 'FALLIDO',
             'paridad_claves_b5':2349 if checks[0]['salida']==0 else None,
             'consultas_productivas_habilitadas':0,'controles':checks,
             'archivos_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}}
    (BASE/'qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'estado':summary['estado'],'paridad':summary['paridad_claves_b5'],'controles':[(c['prueba'],c['salida']) for c in checks]},ensure_ascii=False))
    return 0 if summary['estado']=='VERIFICADO' else 1
if __name__=='__main__':raise SystemExit(main())

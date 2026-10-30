"""Ensaya en un puntero aislado y verifica de nuevo con el puntero real. Revierte ante fallo."""
import collections as C
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from construir_v21 import ROOT,OUT,P,D,OLD,load,dump,sha
from control_tasas import rates
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
from common.seguimiento_promedios import CapaPromedios
from common.codigo_sies_mu2027 import cargar_contexto,resolver
def probe(root):
    service=DiccionarioSiesSeguimiento(root=root)
    try:
        lv=rates(service);layer=CapaPromedios(service);assert not layer.problema
        return {'edicion':service.edicion,'tasas':lv}
    finally:service.close()

def consumers():
    svc=DiccionarioSiesSeguimiento(root=ROOT);sample=[];count=C.Counter()
    for person,cli,plan,y,per,car,s,j,payload in svc.db.execute('select persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload from observaciones order by id'):
        r=json.loads(payload);lvl=r['nivel_asignacion']
        if count[lvl]>=6:continue
        q=dict(persona=person,codcli=cli,plan=plan,anio=y,periodo=per,carrera=car,sede=s,jornada=j)
        z=svc.consultar(**q)
        if z.get('observacion_id')!=r['observacion_id']:continue
        sample.append({'metodo':'consultar','entrada':q});count[lvl]+=1
    svc.close();answers=[]
    with tempfile.TemporaryDirectory(dir=P) as td:
        for i,f in enumerate(['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']):
            dest=Path(td)/f'{i}.json'
            cmd=subprocess.run([sys.executable,str(ROOT/f),'--salida-privada',str(dest)],input=json.dumps(sample),text=True,capture_output=True,cwd=ROOT)
            if cmd.returncode:raise RuntimeError('Fallo del consumidor '+f)
            data=load(dest);assert all(z['edicion']==D.name and z['seguimiento_promedios']['estado']=='DISPONIBLE' for z in data)
            assert all(z['codigo_sies']==(z['evidencia']['codigo_documental_atribuible'] or z['evidencia']['codigo_interno_adoptado'] or None) for z in data)
            answers.append(sha(dest))
    assert len(set(answers))==1 and count['VERSION_POR_MU_DEL_PLAN'] and count['E'] and count['DOCUMENTAL_T1']
    planes,oferta,antiguos,pendientes=cargar_contexto()
    mu=C.Counter(resolver({'anio':2027,'via_solicitada':'ANTIGUO','fila_mu2026':i},planes,oferta,antiguos,pendientes)['via'] for i in antiguos)
    assert sum(mu.values())==4105
    tests={}
    for folder,pattern in [('outputs/paridad_codigo_sies_20261029','test_paridad.py'),('outputs/depuracion_codigo_mu2027_20261029','test_h002l.py')]:
        run=subprocess.run([sys.executable,'-m','unittest','discover','-s',folder,'-p',pattern],cwd=ROOT,text=True,capture_output=True)
        if run.returncode:raise RuntimeError(run.stderr)
        tests[pattern]=next(x for x in run.stderr.splitlines() if ' tests in ' in x)
    return {'tres_consumidores_identicos':True,'consultas_por_consumidor':len(sample),'por_nivel':dict(count),'mu2027':dict(mu),'pruebas':tests}
def main():
    real=ROOT/'data/diccionario_sies_seguimiento/activo.json'
    prev=real.read_bytes();assert json.loads(prev)['descriptor']==OLD
    baseline=probe(ROOT)
    obj={'descriptor':str((D/'descriptor.json').relative_to(ROOT)),'sha256':sha(D/'descriptor.json')}
    with tempfile.TemporaryDirectory(dir=P) as tmp:
        root=Path(tmp)
        (root/'PROYECTO_IPSS.json').symlink_to(ROOT/'PROYECTO_IPSS.json')
        for f in [*load(D/'descriptor.json')['componentes_sha256'],obj['descriptor'],load(D/'descriptor.json')['capa_promedios']['metadata']]:
            dest=root/f;dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(ROOT/f)
        dump(root/real.relative_to(ROOT),obj);trial=probe(root)
    def core(r):return {k:(v['numerador'],v['denominador']) for k,v in r['tasas'].items()}
    assert core(baseline)==core(trial)
    tmp=real.with_suffix('.h013.tmp')
    try:
        dump(tmp,obj);os.replace(tmp,real)
        live=probe(ROOT);assert live==trial
        smoke=consumers()
        dump(OUT/'QA_ACTIVACION.json',{'estado':'PASS','v20':baseline,'ensayo_v21':trial,'puntero_real_v21':live,'consumidores':smoke,'metodo':'Cálculo H001 sobre MU y catálogo aprobados, y R19 sobre banderas de la foto V24 aprobada. Reagrupación por contextos de cada puntero. R19 ingreso T2 se calcula por área con matriculados menos renuncias. Los códigos no determinan el denominador.'})
    except BaseException:
        tmp.write_bytes(prev);os.replace(tmp,real);raise
    print('PASS',live['edicion'],smoke)
if __name__=='__main__':main()

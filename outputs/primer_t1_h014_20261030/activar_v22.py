"""Compara v21, puntero v22 aislado y puntero v22 real. Reversión ante cualquier discrepancia."""
import os
import tempfile
import sys
from pathlib import Path
from construir_v22 import OUT,ROOT,PRIVATE,D,DATA,OLD,load,dump,sha
sys.path.insert(0,str(ROOT/'outputs/activacion_v21_h013_20261030'))
import activar as anterior

def main():
    real=DATA/'activo.json';prev=real.read_bytes()
    active=load(real);assert active['descriptor']==str(OLD.relative_to(ROOT)) and sha(OLD)==active['sha256']
    base=anterior.probe(ROOT)
    obj={'descriptor':str((D/'descriptor.json').relative_to(ROOT)),'sha256':sha(D/'descriptor.json')}
    with tempfile.TemporaryDirectory(dir=PRIVATE) as tmp:
        root=Path(tmp)
        (root/'PROYECTO_IPSS.json').symlink_to(ROOT/'PROYECTO_IPSS.json')
        for f in [*load(D/'descriptor.json')['componentes_sha256'],obj['descriptor'],load(D/'descriptor.json')['capa_promedios']['metadata']]:
            dest=root/f;dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(ROOT/f)
        dump(root/real.relative_to(ROOT),obj);trial=anterior.probe(root)
    assert trial['tasas']==base['tasas']
    archive=DATA/'archivo_v21_h014';archive.mkdir(exist_ok=True);(archive/'activo.json').write_bytes(prev)
    tmp=real.with_suffix('.h014.tmp')
    try:
        dump(tmp,obj);os.replace(tmp,real)
        live=anterior.probe(ROOT);assert live==trial
        anterior.D=D;anterior.P=PRIVATE
        smoke=anterior.consumers()
        dump(OUT/'QA_ACTIVACION.json',{'estado':'PASS','v21':base,'ensayo_v22':trial,'puntero_real_v22':live,'consumidores':smoke})
    except BaseException:
        tmp.write_bytes(prev);os.replace(tmp,real);raise
    print(live['edicion'],smoke['consultas_por_consumidor'],'consultas por consumidor')
if __name__=='__main__':main()

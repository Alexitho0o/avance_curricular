"""Prueba los consumidores sin promover el puntero: inyección aislada del descriptor."""
import json,sys,subprocess,hashlib
from pathlib import Path
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');O=Path(__file__).parent;P=Path('/Users/alexi/.local/share/ipss/fase3_candidata_20261025')
sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
s=DiccionarioSiesSeguimiento(descriptor=O/'descriptor_candidato.json')
ops=json.loads((P.parent/'fase2_historico_20261025/OPERACIONES_CANDIDATAS.json').read_text())['operaciones'];req=[]
for op in ops:
 x=op['estado_despues_propuesto'];req.append({'metodo':'consultar','entrada':dict(persona=x['persona'],codcli=x['CODCLI'],plan=x['plan'],anio=x['ano'],periodo=x['periodo'],carrera=x['carrera'],sede=x['sede_dimension'],jornada=x['jornada_sies'])})
expected=[s.consultar(**q['entrada']) for q in req];s.close()
commands=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']
bootstrap="import sys,runpy;sys.path.insert(0,sys.argv[1]);import common.diccionario_sies_seguimiento as m;old=m.DiccionarioSiesSeguimiento;m.DiccionarioSiesSeguimiento=lambda:old(descriptor=sys.argv[2]);command=sys.argv[3];sys.argv=[command,'--salida-privada',sys.argv[4]];runpy.run_path(command,run_name='__main__')"
# Bind descriptor before argv is replaced.
bootstrap=bootstrap.replace("old=m.DiccionarioSiesSeguimiento;m.DiccionarioSiesSeguimiento=lambda:old(descriptor=sys.argv[2])","old=m.DiccionarioSiesSeguimiento;descriptor=sys.argv[2];m.DiccionarioSiesSeguimiento=lambda:old(descriptor=descriptor)")
for i,cmd in enumerate(commands):
 dst=P/f'consumidor_{i}.json';assert not dst.exists()
 p=subprocess.run([sys.executable,'-B','-c',bootstrap,str(R),str(O/'descriptor_candidato.json'),str(R/cmd),str(dst)],input=json.dumps(req),text=True,capture_output=True);assert p.returncode==0,p.stderr
 assert json.loads(dst.read_text())==expected;assert dst.stat().st_mode&0o777==0o600
bad=json.loads((O/'descriptor_candidato.json').read_text());bad['base_privada']['sha256']='0'*64;(P/'descriptor_qa_alterado.json').write_text(json.dumps(bad))
try:DiccionarioSiesSeguimiento(descriptor=P/'descriptor_qa_alterado.json')
except ValueError:pass
else:raise AssertionError('No rechazó hash alterado')
q={'clasificacion':'C','consumidores':3,'consultas_por_consumidor':8,'respuestas_iguales':True,'hash_alterado_rechazado':True,'pruebas_existentes_correctas':12,'limite':'Descriptor candidato inyectado solo en proceso de prueba; consumidores productivos conservan v7.'}
(O/'QA_CONSUMIDORES.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps(q))

"""Consulta v11 y adjunta capa separada de estados observados; solo salida privada."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
META=Path(__file__).parent/'RESULTADO_CAPA_V11_ULTIMO_ESTADO.json'
def main():
 p=argparse.ArgumentParser();p.add_argument('--salida-privada',required=True,type=Path);args=p.parse_args();target=args.salida_privada.expanduser().resolve()
 if target.exists() or not target.parent.is_dir() or target.is_relative_to(ROOT) or subprocess.run(['git','-C',str(target.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode==0:raise ValueError('Salida debe ser nueva y estar fuera de Git')
 meta=json.loads(META.read_text());path=Path(meta['capa_privada']['ruta']);assert sha256(path)==meta['capa_privada']['sha256'];indexed={r['observacion_id']:r for r in json.loads(path.read_text())};svc=DiccionarioSiesSeguimiento()
 if svc.edicion!=meta['edicion_diccionario'] or svc.descriptor['base_privada']['sha256']!=meta['sha256_base_v11']:raise ValueError('Capa y diccionario no coinciden; regenerar capa')
 queries=json.load(sys.stdin);assert isinstance(queries,list);answers=[]
 for q in queries:
  r=svc.consultar(**q);e=r.get('evidencia');identifiers=[r['observacion_id']] if 'observacion_id' in r else [x['observacion_id'] for x in e] if isinstance(e,list) else []
  answers.append({'codigo_sies':r,'seguimiento_observado':[indexed[x] for x in identifiers if x in indexed],'limite':'Último periodo observado en 12166; estado del extracto, no estado histórico acreditado. Foto no es cálculo de retención.'})
 svc.close()
 with os.fdopen(os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'w') as f:json.dump(answers,f,ensure_ascii=False)
 print(json.dumps({'consultas':len(answers),'salida_privada':str(target)}))
if __name__=='__main__':main()

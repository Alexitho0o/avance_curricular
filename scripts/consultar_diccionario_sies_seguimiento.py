#!/usr/bin/env python3
"""Consulta común de códigos SIES y capa PROMEDIOS; salida individual privada."""
import argparse,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,ROOT
from common.seguimiento_promedios import CapaPromedios
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--salida-privada',type=Path,required=True);args=parser.parse_args();output=args.salida_privada.expanduser().resolve()
 if not output.parent.is_dir() or output.is_relative_to(ROOT) or output.exists() or subprocess.run(['git','-C',str(output.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode==0:raise ValueError('Se requiere archivo nuevo en carpeta privada existente fuera del repositorio')
 requests=json.load(sys.stdin)
 if not isinstance(requests,list):raise ValueError('Entrada debe ser lista de consultas')
 service=DiccionarioSiesSeguimiento();capa=CapaPromedios(service);result=[]
 try:
  for item in requests:
   method=item['metodo']
   if method not in ('consultar','codigos_mu','seguir_cohorte'):raise ValueError('Método fuera del contrato')
   val=getattr(service,method)(**item['entrada'])
   if method=='consultar':val['seguimiento_promedios']=capa.consultar(val)
   elif method=='seguir_cohorte':
    for destination in val:destination['consulta']['seguimiento_promedios']=capa.consultar(destination['consulta'])
   else:val['seguimiento_promedios']={'estado':'SIN_CONTEXTO_DE_EXPEDIENTE','observaciones':[]}
   result.append(val)
 finally:service.close()
 with os.fdopen(os.open(output,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'w') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({'consultas':len(result),'salida_privada':str(output)},ensure_ascii=False))
if __name__=='__main__':main()

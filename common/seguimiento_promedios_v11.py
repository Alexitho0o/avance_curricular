"""Enriquece la respuesta v11 sin modificar códigos, fuentes ni denominadores."""
import json
from pathlib import Path
from common.diccionario_sies_seguimiento import sha256

class CapaPromedios:
 def __init__(self,service):
  self.data={};self.problema=None;self.meta=None
  try:
   cfg=service.descriptor['capa_promedios'];path=Path(cfg['metadata']);
   if not path.is_absolute():path=service.root/path
   if sha256(path)!=cfg['sha256']:raise ValueError('MANIFIESTO_ALTERADO')
   self.meta=json.loads(path.read_text())
   if self.meta['sha256_base_v11']!=service.descriptor['base_privada']['sha256']:raise ValueError('BASE_DISTINTA')
   private=Path(self.meta['capa_privada']['ruta'])
   if sha256(private)!=self.meta['capa_privada']['sha256']:raise ValueError('CAPA_ALTERADA')
   rows=json.loads(private.read_text());self.data={x['observacion_id']:x for x in rows}
   if len(self.data)!=len(rows):raise ValueError('OBSERVACIONES_DUPLICADAS')
  except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
   self.data={};self.problema=type(exc).__name__
 def consultar(self,result):
  if self.problema:return {'estado':'PENDIENTE_CAPA_NO_DISPONIBLE_O_NO_VERIFICADA','motivo':self.problema,'observaciones':[]}
  if 'observacion_id' in result:ids=[result['observacion_id']]
  else:
   evidence=result.get('evidencia');ids=[x['observacion_id'] for x in evidence if 'observacion_id' in x] if isinstance(evidence,list) else []
  if not ids:return {'estado':'SIN_CONTEXTO_CONSULTABLE','observaciones':[]}
  rows=[self.data[x] for x in ids if x in self.data]
  if len(rows)!=len(ids):return {'estado':'PENDIENTE_OBSERVACION_SIN_CAPA','observaciones':rows}
  return {'estado':'DISPONIBLE','observaciones':rows,'alcance':'Último período observado en el extracto 12166; no acredita fecha histórica ni cierre. Fotos y discrepancias son evidencia separada.'}

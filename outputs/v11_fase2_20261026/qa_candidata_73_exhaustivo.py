"""Audita la candidata y sus consultas sin modificarla ni exponer identidades."""
import collections, hashlib, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, sha256
OUT=Path(__file__).parent; PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
previous=OUT/'DESCRIPTOR_CANDIDATA.json'; current=OUT/'DESCRIPTOR_CANDIDATA_73_CO.json'
first=DiccionarioSiesSeguimiento(descriptor=previous); second=DiccionarioSiesSeguimiento(descriptor=current)
rows=first.db.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones ORDER BY id').fetchall()
changes=collections.Counter(); errors=collections.Counter(); changed_ids=[]
for r in rows:
 q=dict(zip(('persona','codcli','plan','anio','periodo','carrera','sede','jornada'),r[1:]))
 try:
  a=first.consultar(**q); b=second.consultar(**q);a.pop('edicion',None);b.pop('edicion',None)
  if a!=b:
   changes[(a.get('nivel_respaldo'),b.get('nivel_respaldo'))]+=1;changed_ids.append(r[0])
 except Exception as exc: errors[type(exc).__name__]+=1
ops=json.loads((PRIVATE/'ADJUDICACIONES_73_CO_V1.json').read_text()); ids={x['observacion_id'] for x in ops}
assert len(rows)==25900 and not errors and len(changed_ids)==73 and set(changed_ids)==ids
assert changes=={('E_PENDIENTE','D_CORRESPONDENCIA_INTERNA_APROBADA'):73}
incoming=json.loads((PRIVATE/'CONTEXTOS_CANDIDATOS.json').read_text());key=lambda x:(x['persona'],x['CODCLI'],x['plan'],x['anio'],x['periodo'])
dups=collections.Counter(map(key,incoming));amb=[x for x in incoming if dups[key(x)]>1];assert len(amb)==2
q=dict(zip(('persona','codcli','plan','anio','periodo'),key(amb[0])));z=second.consultar(**q)
assert z['nivel_respaldo']=='E_PENDIENTE' and z['codigo_sies'] is None
summary={'clasificacion':'C controles; E alcance del QA','observaciones_consultadas':len(rows),'consultas_que_cambiaron':len(changed_ids),'cambios_por_respaldo':{'E_a_D':len(changed_ids)},'consultas_no_cambiadas':len(rows)-len(changed_ids),'errores':dict(errors),'llave_ambigua_sin_adjudicacion':True,'ambigua_motivo_servicio':z['motivo'],'alternativas_excluidas':len(amb),'base_v11_anterior_sha256':first.descriptor['base_privada']['sha256'],'base_candidata_sha256':second.descriptor['base_privada']['sha256'],'descriptor_sha256':sha256(current),'nota':'Revisión funcional no acredita ausencia de información ni activa candidata; observaciones excluidas por llave ambigua requieren evidencia.'}
first.close();second.close();(OUT/'QA_CANDIDATA_73_EXHAUSTIVO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))

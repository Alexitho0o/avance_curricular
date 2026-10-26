"""QA de regresión completo por observación y pruebas negativas de ambigüedad."""
import collections,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
OUT=Path(__file__).parent;P=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
old=DiccionarioSiesSeguimiento(descriptor=OUT/'DESCRIPTOR_CANDIDATA_73_CO.json');new=DiccionarioSiesSeguimiento(descriptor=OUT/'DESCRIPTOR_CANDIDATA_86_Y_AMBIGUEDAD.json')
rows=old.db.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones ORDER BY id').fetchall();details=json.loads((P/'ADJUDICACIONES_13_2025_Y_ALTERNATIVAS.json').read_text());expected={x['observacion_id'] for x in details['adjudicaciones']};assert len(expected)==13
stats={};changed_full=set();changed_partial=set();errors=collections.Counter()
for r in rows:
 q=dict(zip(('persona','codcli','plan','anio','periodo','carrera','sede','jornada'),r[1:]))
 for mode in ('completa','sin_dimensiones'):
  args=q if mode=='completa' else {k:q[k] for k in ('persona','codcli','plan','anio','periodo')}
  try:
   a=old.consultar(**args);b=new.consultar(**args);a.pop('edicion',None);b.pop('edicion',None)
   if a!=b:
    (changed_full if mode=='completa' else changed_partial).add(r[0])
    if r[0] in expected:assert a['nivel_respaldo']=='E_PENDIENTE' and b['nivel_respaldo']=='D_CORRESPONDENCIA_INTERNA_APROBADA'
  except Exception as ex:errors[type(ex).__name__]+=1
assert not errors and changed_full==expected and changed_partial==expected
amb=details['alternativas'];assert len(amb)==2
z=amb[0];bare={'persona':z['persona'],'codcli':z['CODCLI'],'plan':z['plan'],'anio':z['ano'],'periodo':z['periodo']};r=new.consultar(**bare);assert r['motivo']=='CONTEXTO_MULTIPLE' and r['codigo_sies'] is None and len(r['evidencia'])==2
for x in amb:
 r=new.consultar(**bare,carrera=x['carrera'],sede=x['sede_dimension'],jornada=x['jornada_sies']);assert r['nivel_respaldo']=='E_PENDIENTE' and r['codigo_sies'] is None
res={'clasificacion':'C QA; E restricciones de fuente','consultas_completas':len(rows),'consultas_sin_dimensiones':len(rows),'cambios_autorizados_cada_modo':len(changed_full),'otros_cambios':0,'errores':dict(errors),'sin_jornada':'CONTEXTO_MULTIPLE con dos alternativas y sin código','con_jornada':'Dos alternativas visibles como E sin código','base_privada_sha256':new.descriptor['base_privada']['sha256'],'descriptor_sha256':sha256(OUT/'DESCRIPTOR_CANDIDATA_86_Y_AMBIGUEDAD.json'),'nota':'Prueba sobre candidata no activa; no certifica exhaustividad de fuentes.'}
old.close();new.close();(OUT/'QA_V11_86_REGRESION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))

"""Revisión agregada de respaldo docente y relaciones de ramos entre planes."""
import collections,hashlib,json,re
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
private=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json');cases=json.loads(private.read_text())
estructura=ROOT/'data/versiones_historicas_sies_umas/fase_4_20261015/estructura_asignaturas.json'
prev=ROOT/'outputs/conciliacion_22_ramos_titulados_20261026/EVIDENCIA_AGREGADA.json'
root=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados')
book=next(root.glob('Titulaci*/2026/enviado por docencia/Informe de Titulados 2025_vf.xlsx'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def s(v):
 if v is None:return ''
 if isinstance(v,(int,float)) and v==int(v):return str(int(v))
 return str(v).strip().upper()
def rut(n,d):
 n=s(n).replace('.','').replace(' ','');d=s(d)
 return str(int(n))+'-'+d if n.isdigit() and re.fullmatch('[0-9K]',d) else None
ids={x['RUT']:x['caso'] for x in cases};assert len(ids)==4
digest=sha(book);assert digest=='676e6451eed59dae08d4cbcf99188932e0a2b586f9c3eb46f4b597721743f236'
w=openpyxl.load_workbook(book,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h=[s(x) for x in next(it)];matched=collections.Counter();blank=collections.Counter()
for row in it:
 r=dict(zip(h,row));person=rut(r.get('NUM_DOCUMENTO'),r.get('DV'))
 if person not in ids or s(r.get('TIPO_DOCUMENTO'))!='R':continue
 matched[ids[person]]+=1
 if not s(r.get('COD_SIES_OBT_TIT')):blank[ids[person]]+=1
w.close();assert sha(book)==digest
p=json.loads(prev.read_text());structure=json.loads(estructura.read_text());edges=[]
for x in structure:
 for e in x.get('equivalencias_detalle',[]):edges.append({'plan_origen':x['CODPESTUD'],'ramo_origen':x['CODRAMO'],'plan_destino':e.get('plan_destino'),'ramo_destino':e.get('ramo_destino'),'filas_fuente':e.get('filas_fuente',[])})
issues=[]
for item in p['discrepancias']:
 if item['relaciones_catalogo']:continue
 code=item['asignatura'];found=[e for e in edges if code in (e['ramo_origen'],e['ramo_destino'])]
 issues.append({'carrera':item['carrera'],'plan_revisado':item['plan'],'ramo':code,'relaciones_codigo_en_cualquier_plan':found,'conclusion':'B/C referencia en otros planes; E equivalencia para plan revisado' if found else 'E sin referencia del código en relaciones revisadas'})
assert len(issues)==21
result={'clasificacion':'B fuentes; C cruce; E atribución','fuentes':{'informe_docencia':{'ruta':str(book),'hoja':'Hoja1','sha256':digest,'columnas_codcli_plan_presentes':False},'estructura':{'ruta':str(estructura),'sha256':sha(estructura),'procedencia':'Listado_Planes_estudio_Sedes RE+CO.xlsx / BBDD Bruta'}},'titulados':{'personas_buscadas':4,'personas_en_informe_docencia':len(matched),'personas_con_codigo_sies_vacio':len(blank),'limite':'Informe de Docencia carece de CODCLI y PLAN_DE_ESTUDIO; no asigna plan y no prueba aceptación.'},'ramos':issues,'conteos':{'ramos_revisados':len(issues),'ramos_con_referencia_en_cualquier_plan':sum(bool(x['relaciones_codigo_en_cualquier_plan']) for x in issues)},'limitaciones':'Las relaciones son literales del catálogo y pueden involucrar otros planes. No se infiere transitividad ni homologación individual. No se han cambiado fuentes o denominadores.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'titulados':result['titulados'],'conteos':result['conteos']},ensure_ascii=False))

"""Extrae solo metadatos y referencias agregadas de las fuentes, sin datos individuales."""
import datetime,hashlib,json,xml.etree.ElementTree as ET,zipfile
from pathlib import Path
OUT=Path(__file__).parent;ROOT=OUT.parents[1]
sources=json.loads((OUT/'DIFERENCIAS_ASIGNATURA_AGREGADO.json').read_text())['fuentes']
manifest=Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/04_AUDITORIA/manifest_ejecucion.json')
inventory=ROOT/'procesos/retencion_intermedia_t2_t3/INVENTARIO_COPIAS_EXTERNAS_20261022.json';catalog=ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def local(tag):return tag.rsplit('}',1)[-1]
def metadata(path):
 with zipfile.ZipFile(path) as z:
  core={}
  if 'docProps/core.xml' in z.namelist():
   r=ET.fromstring(z.read('docProps/core.xml'))
   core={local(x.tag):x.text for x in r if local(x.tag) in ('created','modified')}
  wb=ET.fromstring(z.read('xl/workbook.xml'));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
  sheets=wb.find('m:sheets',ns); sheet=next(x for x in sheets if x.attrib.get('name')=='Hoja1');rid=sheet.attrib['{'+ns['r']+'}id']
  rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'));target=next(x.attrib['Target'] for x in rel if x.attrib['Id']==rid);target=target.lstrip('/');target=target if target.startswith('xl/') else 'xl/'+target
  filter_refs=[];filter_fields=0;hidden=0;total=0
  with z.open(target) as f:
   for _,e in ET.iterparse(f,events=('end',)):
    k=local(e.tag)
    if k=='autoFilter':filter_refs.append(e.attrib.get('ref',''));filter_fields+=len([x for x in e if local(x.tag)=='filterColumn'])
    elif k=='row':total+=1;hidden+=e.attrib.get('hidden') in ('1','true')
    e.clear()
 return {'core_xml':core,'hoja':'Hoja1','autofiltro_rangos':filter_refs,'filtros_de_columna':filter_fields,'filas_ocultas':hidden,'elementos_fila':total}
m=json.loads(manifest.read_text());e=next(x for x in m['entradas'] if x['tipo']=='promedios_auxiliar');i=json.loads(inventory.read_text());v=next(x for x in i['archivos'] if x['archivo']=='PROMEDIOSDEALUMNOS_12166.xlsx')
assert e['sha256_original']==sources['respaldo_ampliado']['sha256'] and v['sha256']==sources['v11_12166']['sha256']
same_input=[]
for period in ('P1','P2','P3'):
 f=manifest.parents[2]/period/'04_AUDITORIA/manifest_ejecucion.json'; d=json.loads(f.read_text()); entry=next(x for x in d['entradas'] if x['tipo']=='promedios_auxiliar');same_input.append({'periodo_proceso':period,'manifest':str(f),'sha256_manifest':sha(f),'fecha_inicio':d['fecha_inicio'],'sha256_promedios':entry['sha256_original']})
assert all(x['sha256_promedios']==e['sha256_original'] for x in same_input)
out={'clasificacion':'B fuentes y metadatos; C lectura; E origen UMAS','fecha_revision':datetime.datetime.now().astimezone().isoformat(),'respaldo_ampliado':{'manifest_path':str(manifest),'manifest_sha256':sha(manifest),'fecha_inicio_procesamiento':m['fecha_inicio'],'fecha_fin_procesamiento':m['fecha_termino'],'periodo_procesamiento':m['periodo'],'entrada':e,'metadata_archivo':metadata(Path(sources['respaldo_ampliado']['ruta'])),'procesos_con_misma_entrada':same_input},'v11_12166':{'inventario_path':str(inventory),'inventario_sha256':sha(inventory),'fecha_inventario':i['fecha_inventario'],'archivo_inventariado':v,'catalogo_path':str(catalog),'catalogo_sha256':sha(catalog),'metadata_archivo':metadata(Path(sources['v11_12166']['ruta']))},'limite':'Fechas de procesamiento e inventario no son exportación UMAS ni corte; filtros visibles de Excel no prueban filtros de consulta origen.'}
(OUT/'PROCEDENCIA_EXPORTACION_AGREGADA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))

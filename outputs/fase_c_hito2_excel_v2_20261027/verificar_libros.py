"""Comparación V1/V2 por huellas de celdas y objetos, sin exportar datos personales."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,hashlib,json,io
root=Path('/Users/alexi/Desktop');v1=root/'AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V1.xlsx';v2=root/'AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V2.xlsx';out=Path(__file__).parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h1=h(v1);assert h1=='642a9e707d1f5dd01e1bae250e8fdb4a4d23077d4c18c1144f96949158aa28cc'
ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def inspect(path):
 result={};errors={};formulas={}
 with zipfile.ZipFile(path) as z:
  if 'xl/sharedStrings.xml' in z.namelist():
   ss=ET.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(t.text or '' for t in si.iter(ns+'t')) for si in ss]
  else:strings=[]
  for idx in range(1,16):
   dig=hashlib.sha256();nf=0;ne=0;name=f'xl/worksheets/sheet{idx}.xml'
   with z.open(name) as f:
    for _,elem in ET.iterparse(f,events=('end',)):
     if elem.tag!=ns+'c':continue
     coord=elem.get('r');typ=elem.get('t','n');fml=elem.find(ns+'f');v=elem.find(ns+'v');inline=elem.find(ns+'is');
     if fml is not None:kind='formula';val=fml.text or '';nf+=1
     elif typ=='s' and v is not None:kind='text';val=strings[int(v.text)]
     elif typ=='inlineStr' and inline is not None:kind='text';val=''.join(t.text or '' for t in inline.iter(ns+'t'))
     elif v is not None:kind='error' if typ=='e' else 'number' if typ=='n' else typ;val=v.text or '';ne+=typ=='e'
     else:elem.clear();continue
     if idx==5 and coord in {'A6','B6','C6','D6','E6','F6'}:elem.clear();continue
     dig.update(json.dumps([coord,kind,val],ensure_ascii=False,separators=(',',':')).encode());dig.update(b'\n');elem.clear()
   result[name]=dig.hexdigest();errors[name]=ne;formulas[name]=nf
  objects={kind:len([s for s in z.namelist() if s.startswith('xl/'+prefix) and s.endswith('.xml')]) for kind,prefix in [('graficos','charts/chart'),('tablas','tables/table')]}
  bad=z.testzip();assert bad is None
 return result,errors,formulas,objects
before,err1,f1,obj1=inspect(v1);after,err2,f2,obj2=inspect(v2);changed=[x for x in before if before[x]!=after[x]];result={'sha256_v1':h1,'sha256_v2':h(v2),'hojas_celdas_sin_cambio_fuera_de_A6_F6':not changed,'hojas_con_diferencias_fuera_alcance':changed,'errores_v1':sum(err1.values()),'errores_v2':sum(err2.values()),'formulas_por_hoja_iguales':f1==f2,'objetos_v1':obj1,'objetos_v2':obj2,'notas':['Huellas excluyen caché de fórmulas; valores y fórmulas comparados por hoja.','No se exportan valores de celdas.']};(out/'QA_COMPARACION_LIBROS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));assert not changed and f1==f2 and obj1==obj2 and sum(err2.values())==0

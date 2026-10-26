from pathlib import Path
import json,zipfile,re,xml.etree.ElementTree as E,hashlib
from xml.sax.saxutils import escape
import openpyxl
O=Path('/tmp/ipss_validacion_2165_20261023');p=O/'REVISION_PRIVADA_VALIDACION_IPSS_20261023_V6.xlsx';data=json.load(open(O/'payload.json'));N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def col(i):
 s=''
 while i:i,r=divmod(i-1,26);s=chr(65+r)+s
 return s
with zipfile.ZipFile(p) as z:
 replacements={}
 for i,item in enumerate(data,1):
  if len(item['rows'])<=500:continue
  name=f'xl/worksheets/sheet{i}.xml';raw=z.read(name).decode();root=E.fromstring(raw);sd=root.find(N+'sheetData');style={}
  for row in sd:
   if row.get('r')=='2':
    for c in row:style[re.sub('[0-9]','',c.get('r'))]=c.get('s','0')
  first=re.search(r'<(?:\w+:)?row\b[^>]*r="1"[^>]*>.*?</(?:\w+:)?row>',raw,re.S).group()
  out=[first]
  for rn,vals in enumerate(item['rows'],2):
   cells=[]
   for ci,v in enumerate(vals,1):
    if v is None:continue
    c=col(ci);attr=f'r="{c}{rn}" s="{style.get(c,"0")}"'
    if isinstance(v,bool):cell=f'<c {attr} t="b"><v>{int(v)}</v></c>'
    elif isinstance(v,(int,float)):cell=f'<c {attr}><v>{v}</v></c>'
    else:cell=f'<c {attr} t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>'
    cells.append(cell)
   out.append(f'<row r="{rn}">'+''.join(cells)+'</row>')
  raw=raw.replace('<x:','<').replace('</x:','</').replace('xmlns:x=','xmlns=');first=out[0].replace('<x:','<').replace('</x:','</');out[0]=first
  raw=re.sub(r'<sheetData>.*?</sheetData>','<sheetData>'+''.join(out)+'</sheetData>',raw,flags=re.S);raw=re.sub(r'<dimension\b[^>]*/>',f'<dimension ref="A1:{col(len(item["headers"]))}{len(item["rows"])+1}"/>',raw)
  replacements[name]=raw.encode()
 tmp=O/'expanded.tmp'
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zz:
  for n in z.namelist():zz.writestr(n,replacements.get(n,z.read(n)))
tmp.replace(p)
w=openpyxl.load_workbook(p,read_only=True,data_only=False)
for item in data:
 s=w[item['name']];it=iter(s);h=next(it);assert [c.value for c in h]==item['headers'];count=0
 for row,expect in zip(it,item['rows']):
  assert len(row)==len(expect)
  for ci,(cell,v) in enumerate(zip(row,expect)):
   a=cell.value
   if a is None and v=='':continue
   if ci in item.get('datecols',[]) and isinstance(v,(float,int)):
    from openpyxl.utils.datetime import to_excel
    assert abs(to_excel(a)-v)<1e-8
   else:assert a==v,'Diferencia privada, contenido omitido'
   if ci in item.get('textcols',[]) and a is not None:assert cell.data_type=='s' and cell.number_format=='@'
   assert cell.data_type!='e'
  count+=1
 assert count==len(item['rows']) and next(it,None) is None
q={'estado':'PASS','todas_celdas_contra_proyeccion':True,'identificadores_texto':True,'fuera_Git':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};(O/'QA_LIBRO_PRIVADO.json').write_text(json.dumps(q));print(json.dumps(q))

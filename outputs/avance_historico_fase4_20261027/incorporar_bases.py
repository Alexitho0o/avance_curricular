"""Incorpora exclusivamente valores RAW a las hojas reservadas por Artifact Tool.

Escritura secuencial para limitar memoria. No modifica fuentes ni fórmulas.
"""
import json, re, zipfile, hashlib
from pathlib import Path
from xml.sax.saxutils import escape
from xml.etree import ElementTree as ET

O = Path(__file__).parent
P = Path.home()/'.local/share/ipss/avance_historico_fase4_20261027'
OUT = O/'AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V1.xlsx'
NS = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
data = json.loads((P/'inputs.json').read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
catalog=P/'catalog.jsonl'
with catalog.open('w') as f:
    for row in data['catalog']:f.write(json.dumps(row,ensure_ascii=False)+'\n')
data['raw']['catalog']={'ruta':str(catalog),'filas':len(data['catalog']),'columnas':list(range(11)),'sha256':sha(catalog)}
checks=[]
with zipfile.ZipFile(P/'base_visual.xlsx') as zi:
    rels={x.attrib['Id']: x.attrib['Target'] for x in ET.fromstring(zi.read('xl/_rels/workbook.xml.rels'))}
    sheets={x.attrib['name']: rels[x.attrib['{'+NS['r']+'}id']] for x in ET.fromstring(zi.read('xl/workbook.xml')).find('s:sheets',NS)}
    targets={}
    for name,label in [('13_RAW_7804','prom7804'),('14_RAW_12166','prom12166'),('12_Listado_mallas','catalog')]:
        target=sheets[name]
        target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        targets[target]=(name,label)
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zo:
        for info in zi.infolist():
            b=zi.read(info.filename)
            if info.filename not in targets:
                if info.filename.startswith('xl/tables/') and b'name="ListadoMallas"' in b:
                    b=b.replace(b'A5:K9',f'A5:K{len(data["catalog"])+5}'.encode())
                zo.writestr(info,b)
                continue
            name,label=targets[info.filename]; meta=data['raw'][label]
            assert sha(meta['ruta'])==meta['sha256']
            xml=b.decode(); end=meta['filas']+5; width=len(meta['columnas']); last=chr(64+width)
            xml=xml.replace('<x:sheetViews>',f'<x:dimension ref="A1:{last}{end}"/><x:sheetViews>',1)
            left,right=xml.split('</x:sheetData>',1)
            left=re.sub(r'<x:row\b[^>]*\br="(\d+)"[^>]*(?:/>|>.*?</x:row>)',lambda m:m.group(0) if int(m.group(1))<=5 else '',left,flags=re.S)
            assert '<x:autoFilter' not in right
            with zo.open(info.filename,'w',force_zip64=True) as dest:
                dest.write(left.encode())
                n=0
                with Path(meta['ruta']).open() as f:
                    for n,line in enumerate(f,1):
                        row=json.loads(line); assert len(row)==width
                        r=n+5; cells=[]
                        for c,value in enumerate(row):
                            coord=f'{chr(65+c)}{r}'
                            if c==0:
                                cells.append(f'<x:c s="1" r="{coord}" t="n"><x:v>{value}</x:v></x:c>')
                            else:
                                text=str(value) if value is not None else ''
                                assert not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',text)
                                cells.append(f'<x:c s="1" r="{coord}" t="inlineStr"><x:is><x:t xml:space="preserve">{escape(text)}</x:t></x:is></x:c>')
                        dest.write((f'<x:row r="{r}">'+''.join(cells)+'</x:row>').encode())
                assert n==meta['filas']
                af='' if label=='catalog' else f'<x:autoFilter ref="A5:{last}{end}"/>'
                dest.write(('</x:sheetData>'+af+right).encode())
            checks.append({'hoja':name,'filas':n,'columnas':width,'fuente_extraida_sha256':meta['sha256']})
(O/'INCORPORACION_RAW.json').write_text(json.dumps({'clasificacion':'C','control':checks,'salida':str(OUT),'sha256':sha(OUT)},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'hojas_RAW':checks,'salida':str(OUT),'bytes':OUT.stat().st_size},ensure_ascii=False))

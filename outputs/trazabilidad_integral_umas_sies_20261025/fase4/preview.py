"""Extrae solo vistas de revisión; no altera el libro final ni simula recálculo."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import json,os
OUT=Path(__file__).resolve().parent
P=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025')
final=Path(json.loads((OUT/'ENSAMBLADO.json').read_text())['salida_privada'])
z=ZipFile(final);NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PR='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types';q=lambda x:'{'+NS+'}'+x
w=E.fromstring(z.read('xl/workbook.xml'));ss=w.find(q('sheets'))
for s in list(ss):
    if int(s.get('sheetId')) not in [28,56,57]:ss.remove(s)
dn=w.find(q('definedNames'))
if dn is not None:w.remove(dn)
rels=E.fromstring(z.read('xl/_rels/workbook.xml.rels'));ids={s.get('{'+R+'}id') for s in ss}
for r in list(rels):
    if r.get('Id') not in ids and not r.get('Type').endswith(('/styles','/theme')):rels.remove(r)
parts={'xl/workbook.xml':E.tostring(w),'xl/_rels/workbook.xml.rels':E.tostring(rels),'xl/styles.xml':z.read('xl/styles.xml'),'_rels/.rels':b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'}
for name in z.namelist():
    if name.startswith('xl/theme/'):parts[name]=z.read(name)
for i,maxr in [(28,10),(56,10),(57,29)]:
    r=E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'));data=r.find(q('sheetData'))
    for row in list(data):
        if int(row.get('r'))>maxr:data.remove(row)
        else:
            for c in row:
                f=c.find(q('f'))
                if f is not None:c.remove(f)
    for tag in ['tableParts','conditionalFormatting','hyperlinks']:
        for el in list(r.findall(q(tag))):r.remove(el)
    dim=r.find(q('dimension'));dim.set('ref',f'A1:{"AB" if i==56 else "G" if i==28 else "I"}{maxr}')
    parts[f'xl/worksheets/sheet{i}.xml']=E.tostring(r)
ct=E.fromstring(z.read('[Content_Types].xml'))
for el in list(ct):
    if el.get('PartName') and el.get('PartName').lstrip('/') not in parts:ct.remove(el)
parts['[Content_Types].xml']=E.tostring(ct)
with ZipFile(P/'preview.xlsx','w',ZIP_DEFLATED) as o:
    for name,b in parts.items():o.writestr(name,b)
os.chmod(P/'preview.xlsx',0o600)

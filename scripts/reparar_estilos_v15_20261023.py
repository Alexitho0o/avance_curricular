"""Remove only orphan xfComplement extension from a copied stylesheet; no XLSX changes."""
from pathlib import Path
import zipfile,re,xml.etree.ElementTree as E,json,hashlib
P=Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/correccion_proxy_t2_2025_20261023_v14/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V14.xlsx')
OUT=Path('/tmp/estilos_v15_sin_huerfanos.xml');z=zipfile.ZipFile(P);orig=z.read('xl/styles.xml');text=orig.decode();ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
a=E.fromstring(orig);xf=a.find('m:cellXfs',ns);indexes=[i for i,x in enumerate(xf) if any(n.tag.endswith('}xfComplement')for n in x.iter())]
used=set()
for p in z.namelist():
 if re.fullmatch('xl/worksheets/sheet[0-9]+.xml',p):
  for n in E.fromstring(z.read(p)).iter():
   if n.tag.rsplit('}',1)[-1] in ('c','row') and n.get('s'):used.add(int(n.get('s')))
   elif n.tag.rsplit('}',1)[-1]=='col' and n.get('style'):used.add(int(n.get('style')))
assert not any('featurepropertybag' in p.lower()for p in z.namelist())
pat=r'<extLst><ext uri="\{C7286773-470A-42A8-94C5-96B5CB345126\}"><ns1:xfComplement i="0"\s*/></ext></extLst>'
new,count=re.subn(pat,'',text);assert count==len(indexes)==3
OUT.write_bytes(new.encode());b=E.fromstring(OUT.read_bytes());assert len(b.find('m:cellXfs',ns))==315
# Removing these metadata extensions does not change any existing font, fill, format, border or alignment.
for i,x in enumerate(xf):
 if i in indexes:x.remove(x.find('m:extLst',ns))
assert E.tostring(a)==E.tostring(b)
report={'source':str(P),'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'output':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'style_indices':indexes,'referenced_styles':sorted(set(indexes)&used),'removed_extension_count':count,'feature_property_bag_parts_present':False,'cell_xfs_count':315,'dxf_count':len(b.find('m:dxfs',ns)),'scope':'Only three orphan xfComplement extLst elements removed. All other XML bytes retained.','causality':'Candidate corroborated by native repair removal; requires clean native-open test.'}
Path('/tmp/estilos_v15_sin_huerfanos.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))

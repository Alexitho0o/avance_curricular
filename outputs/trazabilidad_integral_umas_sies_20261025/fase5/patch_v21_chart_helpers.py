import re, zipfile, shutil
from pathlib import Path
from xml.sax.saxutils import escape

src=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V20.xlsx')
dst=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V21.xlsx')
shutil.copy2(src,dst)
with zipfile.ZipFile(dst) as z: files={n:z.read(n) for n in z.namelist()}
name='xl/worksheets/sheet15.xml'; s=files[name].decode()
def add(row, cells):
    global s
    m=re.search(rf'(<row[^>]* r="{row}"[^>]*>)(.*?)(</row>)',s,re.S)
    if not m: raise RuntimeError(row)
    body=m.group(2)
    for ref,form,text in cells:
        body=re.sub(rf'<c[^>]* r="{re.escape(ref)}"[^>]*>.*?</c>','',body,flags=re.S)
        typ=' t="str"' if text else ''
        body+=f'<c r="{ref}"{typ}><f>{escape(form)}</f><v></v></c>'
    s=s[:m.start()]+m.group(1)+body+m.group(3)+s[m.end():]

for r,srcrow in [(4,42),(5,43)]:
    add(r,[(f'DA{r}',f'BP{srcrow}',False),(f'DB{r}',f'IFERROR(BS{srcrow}/BR{srcrow},"")',False),(f'DG{r}',str(2022+r-2),True)])
for r,srcrow in zip(range(4,18),range(9,23)): add(r,[(f'DK{r}',f'R{srcrow}',True),(f'DL{r}',f'V{srcrow}',False)])
for r,srcrow in zip(range(4,28),range(9,33)): add(r,[(f'DN{r}',f'AC{srcrow}',True),(f'DO{r}',f'AB{srcrow}',False)])
for r,srcrow in zip(range(4,6),range(9,11)): add(r,[(f'DQ{r}',f'AD{srcrow}',True),(f'DR{r}',f'AG{srcrow}',False),(f'DT{r}',f'AI{srcrow}',True),(f'DU{r}',f'AL{srcrow}',False)])
for r,srcrow in zip(range(4,7),range(9,12)): add(r,[(f'DW{r}',f'AN{srcrow}',True),(f'DX{r}',f'AQ{srcrow}',False)])
files[name]=s.encode()
tmp=dst.with_suffix('.tmp.xlsx')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    for n,d in files.items(): z.writestr(n,d)
tmp.replace(dst)
print(dst)

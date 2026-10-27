"""Derivado local con cambios puntuales de la instantánea; preserva paquetes XLSX."""
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile,hashlib,re,os
src=Path('/Users/alexi/Desktop/AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V2.xlsx');dst=Path('/Users/alexi/Desktop/AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V3.xlsx')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src)=='1300c4ead3da4f0d9a68880498814f5a73a0f6a881734891ee163ff15908eaec';assert not dst.exists()
with zipfile.ZipFile(src) as zin:
 sheet=zin.read('xl/worksheets/sheet5.xml').decode('utf8')
 for cell,old,new in [('B6','<c r="B6" s="10"><v>1292</v></c>','<c r="B6" s="10"><v>990</v></c>'),('D6','<c r="D6" s="10" t="s"><v>31956</v></c>','<c r="D6" s="10" t="inlineStr"><is><t>'+escape('1.028 atribuciones internas incorporadas en v12–v15')+'</t></is></c>'),('E6','<c r="E6" s="10" t="s"><v>31957</v></c>','<c r="E6" s="10" t="inlineStr"><is><t>'+escape('Atribución documental pendiente; diccionario v17 activo')+'</t></is></c>')]:
  assert sheet.count(old)==1,cell;sheet=sheet.replace(old,new,1)
 with zipfile.ZipFile(dst,'x') as zout:
  zout.comment=zin.comment
  for info in zin.infolist():zout.writestr(info,sheet.encode('utf8') if info.filename=='xl/worksheets/sheet5.xml' else zin.read(info.filename))
os.chmod(dst,0o600);assert sha(src)=='1300c4ead3da4f0d9a68880498814f5a73a0f6a881734891ee163ff15908eaec';print('V3_SHA256',sha(dst))

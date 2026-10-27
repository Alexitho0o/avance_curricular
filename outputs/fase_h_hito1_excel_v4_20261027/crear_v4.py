from pathlib import Path
from xml.sax.saxutils import escape
import zipfile,hashlib,re,json,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent;src=Path('/Users/alexi/Desktop/AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V3.xlsx');dst=Path('/Users/alexi/Desktop/AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V4.xlsx');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(src)=='c62d01a0b59aec75cc62d55c4cb96f593d5d80d57809e625b39efbd4b2715bb5' and not dst.exists();rows=json.loads((O/'MOTIVOS_AGREGADOS.json').read_text());values={'B6':545,'D6':'1.473 correspondencias internas v12–v20','E6':'Atribución documental pendiente; diccionario v20 activo','A15':'Foco de 5.144 contextos: 545 pendientes, incluye 8 de diplomados.','A16':'Sin esos 8 contextos: 537 pendientes; no es exclusión general de todos los diplomados.','A18':'Motivo de pendiente','B18':'Contextos','C18':'Expedientes','D18':'Personas','E18':'Clase','A24':'No sumar personas ni expedientes entre filas; pueden repetirse.','A26':'Correspondencias internas desde v12','B27':'Contextos','C27':'Tipo de respaldo','A28':'v12','B28':644,'C28':'D; desglose D1/D2 no acreditado aquí','A29':'v13','B29':47,'C29':'D; desglose D1/D2 no acreditado aquí','A30':'v14','B30':35,'C30':'D; desglose D1/D2 no acreditado aquí','A31':'v15','B31':302,'C31':'D1','A32':'v18','B32':244,'C32':'D1','A33':'v19','B33':105,'C33':'83 D1 + 22 D2a','A34':'v20','B34':96,'C34':'D2','A35':'Total','B35':('formula','SUM(B28:B34)',1473),'A37':'D1 conocidos: 629; D2 conocidos: 118; anteriores sin desglose: 726.','A38':'Todos son cierres internos; atribución documental del período sigue pendiente.','A40':'Vistas históricas: instantánea V3, no recalculada automáticamente con el diccionario v20.'}
for i,x in enumerate(rows,19):
 for col,k in [('A','motivo'),('B','contextos'),('C','expedientes'),('D','personas')]:values[col+str(i)]=x[k]
 values['E'+str(i)]='C/E'
with zipfile.ZipFile(src) as a:
 sheet=a.read('xl/worksheets/sheet5.xml').decode()
 for cell,value in values.items():
  pattern=r'<c r="'+cell+r'"[^>]*?(?:/>|>.*?</c>)';match=re.search(pattern,sheet);assert match,cell;old=match.group();style='10' if cell[0] in 'ABCDE' else '1'
  if isinstance(value,tuple):new=f'<c r="{cell}" s="{style}"><f>{escape(value[1])}</f><v>{value[2]}</v></c>'
  elif isinstance(value,int):new=f'<c r="{cell}" s="{style}"><v>{value}</v></c>'
  else:new=f'<c r="{cell}" s="{style}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
  sheet=sheet[:match.start()]+new+sheet[match.end():]
 with zipfile.ZipFile(dst,'x') as z:
  z.comment=a.comment
  for info in a.infolist():z.writestr(info,sheet.encode() if info.filename=='xl/worksheets/sheet5.xml' else a.read(info.filename))
os.chmod(dst,0o600);assert sha(src)=='c62d01a0b59aec75cc62d55c4cb96f593d5d80d57809e625b39efbd4b2715bb5';print('V4 sha256',sha(dst))

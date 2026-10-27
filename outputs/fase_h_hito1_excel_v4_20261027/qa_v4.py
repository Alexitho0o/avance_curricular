from pathlib import Path
import zipfile,hashlib,json,re,openpyxl
O=Path(__file__).parent;a=Path('/Users/alexi/Desktop/AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V3.xlsx');b=Path('/Users/alexi/Desktop/AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V4.xlsx');sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();w1=openpyxl.load_workbook(a,read_only=True,data_only=False);w2=openpyxl.load_workbook(b,read_only=True,data_only=False);assert w1.sheetnames==w2.sheetnames;changes=[]
for s1,s2 in zip(w1,w2):
 for rows in zip(s1.iter_rows(),s2.iter_rows()):
  for x,y in zip(*rows):
   if x.value!=y.value:changes.append((s1.title,x.coordinate))
assert all(x[0]=='05_Pendientes' for x in changes);w1.close();w2.close()
with zipfile.ZipFile(a) as z1,zipfile.ZipFile(b) as z2:
 assert not z1.testzip() and not z2.testzip();changed=[x for x in z1.namelist() if z1.read(x)!=z2.read(x)];assert changed==['xl/worksheets/sheet5.xml'];objs={}
 for prefix in ('charts/chart','tables/table'):
  files=[n for n in z1.namelist() if n.startswith('xl/'+prefix) and n.endswith('.xml')];assert all(z1.read(n)==z2.read(n) for n in files);objs[prefix]=len(files)
 errors=0
 for n in z2.namelist():
  if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'):errors+=len(re.findall(rb'<(?:\w+:)?c\b[^>]*\bt="e"',z2.read(n)))
 assert errors==0 and objs=={'charts/chart':3,'tables/table':12}
w=openpyxl.load_workbook(b,read_only=True,data_only=True);s=w['05_Pendientes'];assert s['B6'].value==545 and s['B35'].value==1473;mot=json.loads((O/'MOTIVOS_AGREGADOS.json').read_text());assert sum(x['contextos'] for x in mot)==545;assert sum(x['contextos'] for x in mot if not x['motivo'].startswith('Diplomados'))==537
q=w['07_QA_matematico'];controls=[(q.cell(i,2).value,q.cell(i,3).value,q.cell(i,4).value,q.cell(i,5).value) for i in range(6,18)];assert all(x[0]==x[1] and x[2]==0 and x[3]=='Coincide' for x in controls);w.close();result={'V3_sha256':sha(a),'V4_sha256':sha(b),'celdas_cambiadas':changes,'partes_modificadas':changed,'graficos':3,'tablas':12,'errores_cacheados':errors,'controles_matematicos_cacheados':12,'foco':545,'foco_sin_ocho_diplomados':537,'limites':['No se recalculó en Excel; ausencia de errores solo respecto a valores almacenados.','Vistas previas son instantánea, no están conectadas al diccionario v20.','Visualización y filtros no se probaron en Excel para V4; tablas y objetos permanecen idénticos.','726 correspondencias de v12–v14 sin desglose D1/D2 verificado.']};(O/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='celdas_cambiadas'},ensure_ascii=False))

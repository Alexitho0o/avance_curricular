"""QA agregado: compara paquetes y controles sin extraer identificadores."""
from pathlib import Path
from datetime import datetime
import zipfile,hashlib,re,json,xml.etree.ElementTree as ET,openpyxl
root=Path('/Users/alexi/Desktop');a=root/'AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V2.xlsx';b=root/'AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V3.xlsx';out=Path(__file__).parent
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();assert sha(a)=='1300c4ead3da4f0d9a68880498814f5a73a0f6a881734891ee163ff15908eaec'
with zipfile.ZipFile(a) as z1,zipfile.ZipFile(b) as z2:
 assert not z1.testzip() and not z2.testzip(); assert set(z1.namelist())==set(z2.namelist());changed=[x for x in z1.namelist() if z1.read(x)!=z2.read(x)];assert changed==['xl/worksheets/sheet5.xml'];s1=z1.read(changed[0]).decode();s2=z2.read(changed[0]).decode();cells=['B6','D6','E6']
 for cell in cells:
  pat=r'<c\b[^>]*\br="'+cell+r'"[^>]*>.*?</c>';s1,n1=re.subn(pat,'<CONTROL_'+cell+'/>',s1);s2,n2=re.subn(pat,'<CONTROL_'+cell+'/>',s2);assert n1==n2==1
 assert s1==s2
 forms=errors=0;objects={}
 for n in z2.namelist():
  if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'):
   s=z2.read(n);errors+=len(re.findall(rb'<(?:\w+:)?c\b[^>]*\bt="e"',s));forms+=len(re.findall(rb'<(?:\w+:)?f(?:\s|>)',s))
 for prefix in ['charts/chart','tables/table']:
  files=[n for n in z1.namelist() if n.startswith('xl/'+prefix) and n.endswith('.xml')];objects[prefix]=len(files);assert all(z1.read(n)==z2.read(n) for n in files)
 assert objects=={'charts/chart':3,'tables/table':12} and errors==0
w=openpyxl.load_workbook(b,read_only=True,data_only=True);s=w['05_Pendientes'];assert s['B6'].value==990 and 'v15' in s['D6'].value and 'v17' in s['E6'].value
qa=w['07_QA_matematico'];r=[(qa.cell(i,2).value,qa.cell(i,3).value,qa.cell(i,4).value,qa.cell(i,5).value) for i in range(6,18)];assert all(x[0]==x[1] and x[2]==0 and x[3]=='Coincide' for x in r);w.close()
f=json.loads(Path('outputs/fase_d_v16_candidata_20261027/QA_FOCO.json').read_text());assert f['v16']['contextos_pendientes']==990 and f['v16']['expedientes_totalmente_pendientes']==215 and f['v16']['personas_totalmente_pendientes']==45
active=json.loads(Path('data/diccionario_sies_seguimiento/activo.json').read_text());assert active['sha256']=='ef3ec2ec32ba2772b5dae53c732471bef4b68a51f31014fd2b647e6474a8d161'
result={'fecha':datetime.now().astimezone().isoformat(),'V2_sha256':sha(a),'V3_sha256':sha(b),'cambios':[{'hoja':'05_Pendientes','celda':'B6','antes':1292,'despues':990},{'hoja':'05_Pendientes','celda':'D6','antes':'726 atribuciones internas incorporadas en v12–v14','despues':'1.028 atribuciones internas incorporadas en v12–v15'},{'hoja':'05_Pendientes','celda':'E6','antes':'Atribución documental pendiente; diccionario v14 activo','despues':'Atribución documental pendiente; diccionario v17 activo'}],'otras_celdas_objetos_estilos_formulas_conservados':True,'partes_modificadas':changed,'graficos':3,'tablas':12,'formulas_en_xml':forms,'errores_cacheados_excel':errors,'controles_matematicos_cacheados_coinciden':12,'foco_5144':f['v16'],'edicion':'v17','exclusion_diplomados':'vistas V2 conservadas byte a byte; no se alteran filtros ni fuentes','capa_promedios':'No integrada en vistas de V2; se conserva, sin fingir conexión dinámica a v17','limites':['Ceros de error corresponden a valores almacenados; no prueban ausencia de error en todos los escenarios de filtros.','Los 12 controles se inspeccionaron en Excel y en caché; no se certifica recálculo exhaustivo de todas las fórmulas.','La diferencia de unidades utiliza QA v16 y v17 conserva base y códigos; no recrea la fuente del foco.'],'sin_commit_push':True}
(out/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))

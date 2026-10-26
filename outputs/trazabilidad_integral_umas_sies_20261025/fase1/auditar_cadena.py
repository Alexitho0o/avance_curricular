"""Fase1/H1: verifica fuentes seleccionadas y estructura, sin modificar fuentes."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,xml.etree.ElementTree as ET,datetime,time
R=Path(__file__).resolve().parents[3];O=Path(__file__).parent
BASE=R/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def git(*a):return subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
now=datetime.datetime.now().astimezone().isoformat();head=git('rev-parse','HEAD');branch=git('branch','--show-current')
assert head=='8e2fb85bb8703758d6878681c9e2a29016e60c63' and branch=='feature/ire-2026'
active=read(R/'data/diccionario_sies_seguimiento/activo.json');desc=read(R/active['descriptor']);assert sha(R/active['descriptor'])==active['sha256']
paths=[('maqueta_formularia','/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx','20fe8438cba065f15240f1e67c066e5feb8bac8841f182864e40ca7bc9512aa8','Resultado de cálculo interno con detalle; maqueta, no referencia de últimas correcciones'),('V17','/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx','8b461d53f75ac26e2e38aa46d0aae921736d21ac2a64034cfd26c08495756a52','Resultado agregado con correcciones y pendientes vigentes al cierreV17'),('V18','/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx','2bd21ca31d391b59f4bd2c56d4876becd12aae05cb9673a7e069b5542ed66b01','Candidata agregada V18; diccionario promovido después, notas históricas no actualizadas'),('MU_derivada',str(BASE/'BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'),'19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd','Base derivada granular anual2022–2026, no padrón de elegibles'),('diccionario_activo',desc['base_privada']['ruta'],desc['base_privada']['sha256'],'Indice privado de códigos por contexto; no motor de retención')]
inventory=read(BASE/'INVENTARIO_FUENTES_SHA256.json');manifest=read(BASE/'MANIFEST_BASE_RETENCION_MU_2022_2026.json')
for s in inventory:paths.append(('MU_original_'+str(s['anio']),s['archivo'],s['sha256'],s['clasificacion']+'; rol de envío/retorno no acreditado por nombre de ruta'))
checks=[]
for kind,path,expected,role in paths:
 p=Path(path);result={'id':kind,'clasificacion':'B','ruta':path,'rol':role,'sha256_esperado':expected,'disponible':p.is_file()}
 for attempt in range(3):
  try:result['sha256_observado']=sha(p);result['bytes']=p.stat().st_size;result['hash_coincide']=result['sha256_observado']==expected;break
  except OSError as e:
   if attempt<2:time.sleep(2)
   else:result.update(clasificacion='E',error_tipo=type(e).__name__,errno=e.errno,hash_coincide=None)
 if result.get('sha256_observado'):assert result['hash_coincide'],kind
 checks.append(result)
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};books=[]
for kind,path,h,role in paths[:4]:
 sheets=[]
 with zipfile.ZipFile(path) as z:
  wb=ET.fromstring(z.read('xl/workbook.xml'));rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'));targets={n.get('Id'):n.get('Target') for n in rels}
  for s in wb.find('m:sheets',N):
   t=targets[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];part=t.lstrip('/') if t.startswith('/') else 'xl/'+t;root=ET.fromstring(z.read(part));dim=root.find('m:dimension',N)
   sheets.append({'hoja':s.get('name'),'parte':part,'dimension':dim.get('ref') if dim is not None else None,'formulas':len(root.findall('.//m:f',N)),'errores_cache':len(root.findall('.//m:c[@t="e"]',N))})
  books.append({'id':kind,'clasificacion':'B/C','ruta':path,'hojas':sheets,'graficos':sum(n.startswith('xl/charts/chart') and n.endswith('.xml') for n in z.namelist()),'tablas':sum(n.startswith('xl/tables/table') and n.endswith('.xml') for n in z.namelist())})
protected={str(R/'PROYECTO_IPSS.json'):sha(R/'PROYECTO_IPSS.json'),str(R/'data/diccionario_sies_seguimiento/activo.json'):sha(R/'data/diccionario_sies_seguimiento/activo.json'),str(R/active['descriptor']):sha(R/active['descriptor'])}
for x in checks:
 if x.get('hash_coincide'):protected[x['ruta']]=x['sha256_observado']
state={'clasificacion':'B/C','fecha':now,'hito':'Fase1/6 H1/3','estado':'FUENTES_SELECCIONADAS_VERIFICADAS' if all(c.get('hash_coincide') for c in checks) else 'VERIFICACION_CON_FUENTES_PENDIENTES','rama':branch,'HEAD':head,'edicion':desc['edicion'],'fuentes':checks,'estructuras':books,'conteos_mu_declarados_en_manifiesto':manifest['conteos'],'limites':['Conteos anuales provienen del manifiesto leído; esta rutina no reproduce las reglas de elegibilidad.','Sin recálculo/apertura en Excel nativo.','No se presume aceptación SIES de las fuentes por estar en Enviados.'],'preservacion':protected}
(O/'CADENA_Y_FUENTES.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'fuentes':len(checks),'hashes_coincidentes':sum(bool(x.get('hash_coincide')) for x in checks),'libros_inspeccionados':len(books),'HEAD':head,'edicion':desc['edicion']}))

from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as ET,collections,re,time,signal
P=Path(__file__).resolve().parent
inv=json.loads((P/'INVENTARIO_ONEDRIVE.json').read_text())
files=[x for x in inv['archivos'] if '/2025/Matricula/' in x['ruta'] and x['extension']=='.xlsx']
priority=['2 y 3er Intake.xlsx','Matricula 2 y 3er 2024.xlsx','IPSS_Procesamiento.xlsx','DATOSDEALUMNOS_1758_CRUDO_10_04_2025_FINAL_SIES.xlsx','Formati_SIES_2025.xlsx','Descarga de lo cargado_08-05-2025_22-26-22_Matrícula_Pregrado_2025.xlsx']
files.sort(key=lambda f:priority.index(Path(f['ruta']).name) if Path(f['ruta']).name in priority else 100)
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
results=[]
for f in files:
 p=Path(f['ruta']);r={'ruta':str(p),'bytes_metadato':f['bytes']}
 def timeout(signum,frame):raise TimeoutError('Lectura limitada a 20 segundos')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(20)
 try:
  blob=p.read_bytes();r['sha256']=hashlib.sha256(blob).hexdigest()
  with zipfile.ZipFile(__import__('io').BytesIO(blob)) as z:
   wb=ET.fromstring(z.read('xl/workbook.xml'));rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'));rel={x.attrib['Id']:x.attrib['Target'] for x in rels}
   strings=[]
   if 'xl/sharedStrings.xml' in z.namelist():
    sst=ET.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(x.itertext()) for x in sst]
   r['objetos_codigo']=[n for n in z.namelist() if any(x in n.lower() for x in ['querytable','connections','customxml','vbaproject','externallink'])]
   sheets=[]
   for sh in wb.find('s:sheets',ns):
    target=rel[sh.attrib['{'+ns['r']+'}id']];name=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    xml=ET.fromstring(z.read(name));dim=xml.find('s:dimension',ns);rows=xml.findall('s:sheetData/s:row',ns)
    first=[]
    for row in rows[:4]:
     vals=[]
     for c in row:
      v=c.find('s:v',ns);t=c.attrib.get('t');val=strings[int(v.text)] if t=='s' and v is not None and v.text else ''.join(c.find('s:is',ns).itertext()) if t=='inlineStr' and c.find('s:is',ns) is not None else v.text if v is not None else ''
      vals.append((c.attrib['r'],val or ''))
     if sum(any(token in v.upper() for token in ['CODCLI','CODCAR','ING_ORI','ANOINGRESO','N_DOC','TIPO_DOC','NIVEL','RUT','JORNADA']) for _,v in vals)>=2:first=vals;break
    fcs=collections.Counter();samples=[]
    for c in xml.findall('.//s:c',ns):
     ff=c.find('s:f',ns)
     if ff is not None:
      col=re.sub(r'\d','',c.attrib['r']);fcs[col]+=1;formula=ff.text or ''
      if len(samples)<40 and (col in ['G','H','Q','R','S','T'] or any(t in formula.upper() for t in ['2025','2024','ING_ORI','ANOINGRESO','CODCLI'])):
       if not re.search(r'\b\d{7,9}[-]?[0-9Kk]?\b',formula):samples.append({'celda':c.attrib['r'],'formula':formula})
    sheets.append({'hoja':sh.attrib['name'],'xml':name,'dimension':dim.attrib.get('ref') if dim is not None else None,'encabezados_detectados':first,'formulas_por_columna':dict(fcs),'formulas_muestra':samples})
   r['hojas']=sheets
 except Exception as e:r['error']=str(e)
 finally:signal.alarm(0)
 results.append(r);(P/'RESPALDOS_XLSX_INSPECCION.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 print(p.name,'ERROR' if 'error'in r else [(s['hoja'],s['dimension'],sum(s['formulas_por_columna'].values()))for s in r['hojas']],flush=True)

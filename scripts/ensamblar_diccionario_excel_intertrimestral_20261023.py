"""Agrega revisión con OOXML; todas las hojas/tablas/gráficos preexistentes quedan idénticos."""
import sys,re,json,zipfile,hashlib,shutil,subprocess,posixpath,xml.etree.ElementTree as E
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
O=Path(sys.argv[1]).resolve();R=Path(__file__).resolve().parents[1]
meta=json.loads((O/'MANIFEST_APLICACION.json').read_text());source=Path(meta['origen_excel']);dst=O/'RETENCION_IPSS_DICCIONARIO_APLICADO_20261023_V12.xlsx'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==meta['fuentes'][str(source)]
z=zipfile.ZipFile(source);new=zipfile.ZipFile(O/'suplemento.xlsx');NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';q=lambda x:'{'+NS+'}'+x;E.register_namespace('',NS)
strings=[''.join(n.itertext()) for n in E.fromstring(new.read('xl/sharedStrings.xml'))]
base=z.read('xl/styles.xml').decode();b=E.fromstring(base);a=E.fromstring(new.read('xl/styles.xml'));offset={};num_map={}
for tag in ['numFmts','fonts','fills','borders','cellXfs']:
 old=b.find(q(tag));extra=a.find(q(tag));offset[tag]=len(old) if old is not None else 0
 if extra is None:continue
 if tag=='numFmts':
  nextid=max([163]+[int(n.get('numFmtId')) for n in old] if old is not None else [163])+1
  for n in extra:num_map[int(n.get('numFmtId'))]=nextid;n.set('numFmtId',str(nextid));nextid+=1
 if tag=='cellXfs':
  for n in extra:
   for attr,t in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:n.set(attr,str(int(n.get(attr,'0'))+offset[t]))
   n.set('numFmtId',str(num_map.get(int(n.get('numFmtId','0')),int(n.get('numFmtId','0')))));n.set('xfId','0')
 children=''.join(E.tostring(n,encoding='unicode').replace(' xmlns="'+NS+'"','') for n in extra)
 found=re.search(rf'<{tag}\b[^>]*>.*?</{tag}>',base,re.S)
 if found:
  chunk=re.sub(r'count="\d+"',f'count="{offset[tag]+len(extra)}"',found.group(),count=1).replace(f'</{tag}>',children+f'</{tag}>');base=base[:found.start()]+chunk+base[found.end():]
 else:base=base.replace('<fonts',f'<{tag} count="{len(extra)}">{children}</{tag}><fonts',1)
def clean(txt):
 txt=txt.lstrip('\ufeff').replace('<x:','<').replace('</x:','</').replace('xmlns:x=','xmlns=')
 def cell(m):
  st=m.group()
  if re.search(r'\bt="s"',st):
   idx=int(re.search(r'<v>(\d+)</v>',st).group(1));st=re.sub(r'\bt="s"','t="inlineStr"',st);st=re.sub(r'<v>.*?</v>',lambda m:'<is><t xml:space="preserve">'+escape(strings[idx])+'</t></is>',st,flags=re.S)
  if re.search(r'\bs="\d+"',st):st=re.sub(r'\bs="(\d+)"',lambda m:f's="{int(m.group(1))+offset["cellXfs"]}"',st,count=1)
  else:st=st.replace('<c ','<c s="'+str(offset['cellXfs'])+'" ',1)
  return st
 return re.sub(r'<c\b[^>]*(?<!/)>.*?</c>',cell,txt,flags=re.S)
work=z.read('xl/workbook.xml').decode();rels=z.read('xl/_rels/workbook.xml.rels').decode();ct=z.read('[Content_Types].xml').decode()
oldnames=[s.get('name') for s in E.fromstring(work).find(q('sheets'))];assert len(oldnames)==51
names=[s.get('name') for s in E.fromstring(new.read('xl/workbook.xml')).find(q('sheets'))]
repl={};tablemax=max(int(re.search(r'table(\d+)\.xml',n).group(1)) for n in z.namelist() if re.fullmatch(r'xl/tables/table\d+\.xml',n))
for i,name in enumerate(names,1):
 assert name not in oldnames
 j=len(oldnames)+i;part=f'xl/worksheets/sheet{j}.xml';assert part not in z.namelist();repl[part]=clean(new.read(f'xl/worksheets/sheet{i}.xml').decode())
 work=work.replace('</sheets>',f'<sheet name="{escape(name)}" sheetId="{j}" r:id="rIdDictionary{j}"/></sheets>')
 rels=rels.replace('</Relationships>',f'<Relationship Id="rIdDictionary{j}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{j}.xml"/></Relationships>')
 ct=ct.replace('</Types>',f'<Override PartName="/{part}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
 rp=f'xl/worksheets/_rels/sheet{i}.xml.rels'
 if rp in new.namelist():
  rr=E.fromstring(new.read(rp))
  for rel in rr:
   assert rel.get('Type').endswith('/table')
   target=rel.get('Target').lstrip('/');tablemax+=1;dest=f'xl/tables/table{tablemax}.xml';tt=E.fromstring(new.read(target));tt.set('id',str(tablemax));repl[dest]=E.tostring(tt,encoding='unicode');rel.set('Target','/'+dest)
   ct=ct.replace('</Types>',f'<Override PartName="/{dest}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml"/></Types>')
  repl[f'xl/worksheets/_rels/sheet{j}.xml.rels']=E.tostring(rr,encoding='unicode')
repl.update({'xl/styles.xml':base,'xl/workbook.xml':work,'xl/_rels/workbook.xml.rels':rels,'[Content_Types].xml':ct})
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as out:
 for name in z.namelist():out.writestr(name,repl.pop(name).encode() if name in repl else z.read(name))
 for name,data in repl.items():out.writestr(name,data.encode())
zz=zipfile.ZipFile(dst);assert zz.testzip() is None;assert len(zz.namelist())==len(set(zz.namelist()))
changed=[n for n in z.namelist() if z.read(n)!=zz.read(n)];assert set(changed)=={'xl/styles.xml','xl/workbook.xml','xl/_rels/workbook.xml.rels','[Content_Types].xml'}
for n in zz.namelist():
 if n.endswith(('.xml','.rels')):E.fromstring(zz.read(n))
charts=[n for n in z.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml',n)];tables=[n for n in z.namelist() if re.fullmatch(r'xl/tables/table\d+\.xml',n)]
assert len(charts)==13
# Validate ids, filter range and header identity for ALL tables using native relationships.
w=openpyxl.load_workbook(dst,read_only=True,data_only=True);wf=openpyxl.load_workbook(dst,read_only=True,data_only=False);old=openpyxl.load_workbook(source,read_only=True,data_only=True)
assert w.sheetnames==oldnames+names
forms=json.loads((O/'FORMULAS_NUEVAS.json').read_text());assert len(forms)==86
for x in forms:
 assert wf[x['sheet']][x['cell']].value==x['formula'];assert w[x['sheet']][x['cell']].value is not None
# Independent arithmetic against Python counters, not formula cache alone.
t=json.loads((O/'tablas.json').read_text());s=w[names[0]];checks=0
for rr,year in [(6,2024),(7,2025),(8,2026)]:
 os=[x for x in t['origenes'] if x[0]==year];cs=[x for x in t['contextos'] if x[0]==year]
 want=[sum(x[k] for x in os) for k in (5,6,7)]+[sum(x[12] for x in cs if x[9]==st) for st in ['B/C Documental','D Interno aprobado','E Pendiente']]
 for col,value in zip('CDEFGH',want):assert s[f'{col}{rr}'].value==value;checks+=1
families=sorted({x[2] for x in t['origenes'] if x[4]=='Sí'})
for rr,f in enumerate(families,17):
 os=[x for x in t['origenes'] if x[2]==f];cs=[x for x in t['contextos'] if x[5]==f]
 want=[sum(x[5] for x in os)]+[sum(x[12] for x in cs if x[9]==st) for st in ['B/C Documental','D Interno aprobado','E Pendiente']]+[sum(x[7] for x in os),sum(x[12] for x in cs)]
 for col,value in zip('CDEFGH',want):assert s[f'{col}{rr}'].value==value;checks+=1
for col in 'CDEFGH':assert s[f'{col}9'].value==sum(s[f'{col}{rr}'].value for rr in (6,7,8));checks+=1
end=17+len(families)
for col in 'CDEFGH':assert s[f'{col}{end}'].value==sum(s[f'{col}{rr}'].value for rr in range(17,end));checks+=1
assert s['C11'].value==0;assert s['G11'].value==5320;checks+=2
errors=[]
for name in names:
 for row in w[name]:
  for c in row:
   if c.data_type=='e':errors.append([name,c.coordinate,c.value])
assert not errors
# Aggregate outputs must not contain the available personal identifiers as cell values.
private=Path(meta['privado']);ori=json.loads((private/'ORIGENES_T1.json').read_text());contexts=json.loads((private/'CONSULTAS_EXACTAS.json').read_text());ids={str(x[k]) for x in ori for k in ('persona','documento_original') if x.get(k)}|{x['codcli'] for x in contexts}
for name in names:
 for row in w[name]:
  for c in row:assert str(c.value) not in ids
# New tables are native, uniquely identified and match worksheet headers exactly.
ids_table=set();names_table=set();trchecks=0
for part in zz.namelist():
 if not re.fullmatch(r'xl/tables/table\d+\.xml',part):continue
 tab=E.fromstring(zz.read(part));assert tab.get('id') not in ids_table;ids_table.add(tab.get('id'));assert tab.get('name') not in names_table;names_table.add(tab.get('name'))
 if part in tables:continue
 cols=tab.find(q('tableColumns'));assert int(cols.get('count'))==len(cols);assert tab.find(q('autoFilter')).get('ref')==tab.get('ref')
 found=False
 for si,name in enumerate(names,52):
  rp=f'xl/worksheets/_rels/sheet{si}.xml.rels'
  if rp not in zz.namelist():continue
  if any(r.get('Target').lstrip('/')==part for r in E.fromstring(zz.read(rp))):
   start=tab.get('ref').split(':')[0];rownum=int(re.search(r'\d+',start).group());assert [w[name].cell(rownum,j+1).value for j in range(len(cols))]==[x.get('name') for x in cols];found=True
 assert found;trchecks+=1
assert trchecks==2
for p,h in meta['fuentes'].items():assert sha(p)==h
assert sha(source)==meta['fuentes'][str(source)]
desktop=Path.home()/'Desktop'/dst.name
if desktop.exists():raise RuntimeError('No sobrescribir copia ya existente')
shutil.copy2(dst,desktop);assert sha(dst)==sha(desktop)
qa={'estado':'OK_CON_PENDIENTES_E','hojas_originales_bytes_identicos':51,'graficos_originales_bytes_identicos':len(charts),'tablas_originales_bytes_identicos':len(tables),'hojas_nuevas':names,'tablas_nuevas_estructura_validada':trchecks,'formulas_nuevas_verificadas':len(forms),'controles_aritmeticos_independientes':checks,'errores_en_hojas_nuevas':errors,'denominadores_T1_conservados':{'2024':558,'2025':1150,'2026':1471},'fuentes_hash_sin_cambio':True,'datos_personales_agregados_al_excel':False,'partes_originales_modificadas':changed,'limites':['Recálculo de suplemento con Artifact Tool; no se ha probado apertura en Excel nativo.','Conservación exacta de las hojas anteriores no certifica semánticamente sus tasas históricas.','Pendientes de versión/contexto permanecen; no hay nuevos cierres de equivalencia.'],'sha256':sha(dst),'archivo':str(dst),'copia_escritorio':str(desktop),'copia_sha256':sha(desktop)}
(O/'QA_EXCEL.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
meta.update({'salida':str(dst),'salida_sha256':sha(dst),'copia_escritorio':str(desktop),'copia_sha256':sha(desktop),'QA':qa,'scripts':{str(R/p):sha(R/p) for p in ['scripts/aplicar_diccionario_excel_intertrimestral_20261023.py','scripts/construir_hojas_diccionario_intertrimestral_20261023.mjs','scripts/ensamblar_diccionario_excel_intertrimestral_20261023.py']},'git':{'rama':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'commit':False,'push':False}})
(O/'MANIFEST_APLICACION.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False))

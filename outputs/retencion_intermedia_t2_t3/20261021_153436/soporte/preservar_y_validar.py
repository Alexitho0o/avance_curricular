"""Transport Artifact-authored cells/caches into the native template package; preserve charts and visual features."""
from pathlib import Path
import json,zipfile,hashlib,copy,re,datetime,shutil,subprocess
from lxml import etree as E
import openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');O=R/'outputs/retencion_intermedia_t2_t3/20261021_153436';P=R/'.local_restricted/retencion_intermedia/20261021_153436'
c=json.loads((O/'soporte/config.json').read_text());model=json.loads((O/'MODELO_AGREGADO.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';RNS='http://schemas.openxmlformats.org/officeDocument/2006/relationships';CNS='http://schemas.openxmlformats.org/drawingml/2006/chart';q=lambda s:'{'+NS+'}'+s;qc=lambda s:'{'+CNS+'}'+s
xml=E.fromstring;ser=lambda t:E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
def readzip(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def paths(parts):
 wb=xml(parts['xl/workbook.xml']);re=xml(parts['xl/_rels/workbook.xml.rels']);ri={s.get('Id'):s.get('Target')for s in re}
 return {s.get('name'):(lambda t:t.lstrip('/') if t.startswith('/') else 'xl/'+t)(ri[s.get('{'+RNS+'}id')])for s in wb.find(q('sheets'))}
parts=readzip(c['scaffold']);candidate=readzip(P/'public_candidate.xlsx');orig=readzip(c['template']);mp=paths(parts);cp=paths(candidate)
styles=xml(parts['xl/styles.xml']);cs=xml(candidate['xl/styles.xml']);dst=styles.find(q('numFmts'));src=cs.find(q('numFmts'));nm={}
if dst is None:dst=E.Element(q('numFmts'),count='0');styles.insert(0,dst)
used={int(x.get('numFmtId')) for x in dst}
for el in src if src is not None else []:
 n=int(el.get('numFmtId'));new=max({163}|used)+1;used.add(new);nm[n]=new;cc=copy.deepcopy(el);cc.set('numFmtId',str(new));dst.append(cc)
dst.set('count',str(len(dst)));offsets={}
for kind in ['fonts','fills','borders','cellStyleXfs','cellXfs','dxfs']:
 dst=styles.find(q(kind));src=cs.find(q(kind))
 if dst is None:dst=E.SubElement(styles,q(kind),count='0')
 offsets[kind]=len(dst)
 for el in src if src is not None else []:
  cc=copy.deepcopy(el)
  if kind in ['cellStyleXfs','cellXfs']:
   for attr,section in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
    if attr in cc.attrib:cc.set(attr,str(int(cc.get(attr))+offsets[section]))
   if 'numFmtId' in cc.attrib:cc.set('numFmtId',str(nm.get(int(cc.get('numFmtId')),int(cc.get('numFmtId')))))
   if kind=='cellXfs' and 'xfId' in cc.attrib:cc.set('xfId',str(int(cc.get('xfId'))+offsets['cellStyleXfs']))
  for fmt in cc.iter(q('numFmt')):fmt.set('numFmtId',str(nm.get(int(fmt.get('numFmtId')),int(fmt.get('numFmtId')))))
  dst.append(cc)
 dst.set('count',str(len(dst)))
parts['xl/styles.xml']=ser(styles)
ss=xml(candidate['xl/sharedStrings.xml']) if 'xl/sharedStrings.xml' in candidate else []
def inline(cell):
 if cell.get('t')=='s':
  idx=int(cell.find(q('v')).text);cell.remove(cell.find(q('v')));cell.set('t','inlineStr');ii=E.SubElement(cell,q('is'))
  for child in ss[idx]:ii.append(copy.deepcopy(child))
 if cell.find(q('f')) is not None and cell.get('t')=='inlineStr':
  ii=cell.find(q('is'));value=''.join(ii.itertext()) if ii is not None else ''
  if ii is not None:cell.remove(ii)
  cell.set('t','str');E.SubElement(cell,q('v')).text=value
 if 's' in cell.attrib:cell.set('s',str(int(cell.get('s'))+offsets['cellXfs']))
 return cell
for name,path in mp.items():
 tree=xml(parts[path]);ct=xml(candidate[cp[name]]);sd=copy.deepcopy(ct.find(q('sheetData')))
 for row in sd:
  if 's' in row.attrib:row.set('s',str(int(row.get('s'))+offsets['cellXfs']))
  for cell in row:inline(cell)
 old=tree.find(q('sheetData'));tree.replace(old,sd)
 if name=='11_Entradas_Agregadas':
  for tag in ['cols','sheetViews']:
   xx=ct.find(q(tag))
   if xx is not None:
    xx=copy.deepcopy(xx)
    if tag=='cols':
     for col in xx:
      if 'style'in col.attrib:col.set('style',str(int(col.get('style'))+offsets['cellXfs']))
    ox=tree.find(q(tag))
    if ox is not None:tree.replace(ox,xx)
  af=tree.find(q('autoFilter'))
  if af is None:af=E.Element(q('autoFilter'));tree.insert(tree.index(sd)+1,af)
  af.set('ref',f"A4:AK{c['last11']}")
 if name=='5_Evolucion':
  newmerges=ct.find(q('mergeCells'));oldmerges=tree.find(q('mergeCells'))
  if newmerges is not None:
   if oldmerges is not None:tree.replace(oldmerges,copy.deepcopy(newmerges))
   else:tree.insert(tree.index(sd)+1,copy.deepcopy(newmerges))
 parts[path]=ser(tree)
# Native tables must have header names identical to the actual cells; mismatches caused previous Excel repairs.
cw=openpyxl.load_workbook(P/'public_candidate.xlsx',data_only=True)
for name,path in mp.items():
 relpath=str(Path(path).parent/'_rels'/(Path(path).name+'.rels'))
 if relpath not in parts:continue
 rel=xml(parts[relpath]);ri={x.get('Id'):x.get('Target')for x in rel};tree=xml(parts[path]);tables=tree.find(q('tableParts'))
 if tables is None:continue
 for tp in tables:
  target=ri[tp.get('{'+RNS+'}id')];tablepath=target.lstrip('/') if target.startswith('/') else str((Path(path).parent/target))
  tablepath=str(Path(tablepath));tablepath=re.sub(r'worksheets/\.\./','',tablepath)
  tx=xml(parts[tablepath]);cols=tx.find(q('tableColumns'));mincol,minrow,maxcol,maxrow=openpyxl.utils.range_boundaries(tx.get('ref'));seen=set()
  for j,el in enumerate(cols,mincol):
   value=cw[name].cell(minrow,j).value;value=str(value) if value not in (None,'') else f'Columna{j-mincol+1}'
   if value in seen:value+=f' {j-mincol+1}'
   seen.add(value);el.set('name',value)
  af=tx.find(q('autoFilter'))
  if af is not None:af.set('ref',tx.get('ref'))
  parts[tablepath]=ser(tx)
# Refresh chart caches while leaving native formulas, colors, geometry and all drawing parts intact.
wb=xml(parts['xl/workbook.xml']);dn=wb.find(q('definedNames'));names={el.get('name'):el.text for el in dn} if dn is not None else {}
def cells(ref):
 ref=ref.lstrip('=')
 if re.match(r'\[0\]!',ref):ref=names[ref.split('!',1)[1]]
 if ref.startswith('OFFSET('):
  mm=re.search(r"OFFSET\('([^']+)'!\$(\w+)\$(\d+),0,0,MAX\(1,COUNTIF\('([^']+)'!(\$\w+\$\d+:\$\w+\$\d+),\">0\"\)\),1\)",ref)
  if not mm:raise ValueError('Unsupported native chart range '+ref)
  sn,col,row,cn,cr=mm.groups();n=max(1,sum(isinstance(cc.value,(int,float)) and cc.value>0 for rr in cw[cn][cr]for cc in rr));return [cw[sn].cell(int(row)+i,openpyxl.utils.column_index_from_string(col)).value for i in range(n)]
 mm=re.match(r"'?([^'!]+)'?!([\$A-Z0-9:]+)$",ref)
 if not mm:return []
 sn,ran=mm.groups()
 if ':'not in ran:return [cw[sn][ran].value]
 return [cc.value for rr in cw[sn][ran]for cc in rr]
chartcounts=0
for path in [n for n in parts if re.fullmatch(r'xl/charts/chart\d+\.xml',n)]:
 tree=xml(parts[path]);chartcounts+=1
 if path=='xl/charts/chart1.xml':
  for ff in tree.iter(qc('f')):
   if ff.text:ff.text=ff.text.replace('$B$24:$B$27','$B$24:$B$25').replace('$C$24:$C$27','$C$24:$C$25').replace('$D$24:$D$27','$D$24:$D$25').replace('$E$24:$E$27','$E$24:$E$25')
 if path=='xl/charts/chart2.xml':
  for tt in tree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
   if tt.text:tt.text='Cohorte 2025 — presencia en listados parciales T2/T3'
  for series,label in zip(tree.iter(qc('ser')),['Presencia 2026-T2','Presencia 2026-T3']):
   tx=series.find(qc('tx'))
   if tx is not None:
    for vv in tx.iter(qc('v')):vv.text=label
 for el in tree.iter():
  if el.tag in [qc('numRef'),qc('strRef')]:
   ff=el.find(qc('f'))
   if ff is None:continue
   vals=cells(ff.text);kind='numCache' if el.tag==qc('numRef') else 'strCache';old=el.find(qc(kind))
   if old is not None:el.remove(old)
   cache=E.SubElement(el,qc(kind))
   if kind=='numCache':E.SubElement(cache,qc('formatCode')).text='0.0%'
   E.SubElement(cache,qc('ptCount'),val=str(len(vals)))
   for i,v in enumerate(vals):
    if v in (None,'') or (kind=='numCache' and not isinstance(v,(int,float))):continue
    E.SubElement(E.SubElement(cache,qc('pt'),idx=str(i)),qc('v')).text=str(v)
 for el in tree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
  if path=='xl/charts/chart3.xml' and el.text and ('Tasa de retención' in el.text or 'Tasa de continuidad' in el.text):el.text='Seguimiento por cohorte — SIES anual solo en T1'
  elif el.text and 'retención' in el.text.lower() and 'Nacional' not in el.text:el.text=el.text.replace('Retención','Continuidad').replace('retención','continuidad')
 parts[path]=ser(tree)
# Rename metadata/navigation references outside worksheet content too.
for path,b in list(parts.items()):
 if path.endswith(('.xml','.rels')) and path!='xl/styles.xml':
  for a,new in c['renames'].items():b=b.replace(a.encode(),new.encode())
  parts[path]=b
calc=wb.find(q('calcPr'))
if calc is not None:calc.set('calcMode','auto');calc.set('fullCalcOnLoad','1')
parts['xl/workbook.xml']=ser(wb)
final=Path(c['out'])
with zipfile.ZipFile(final,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in parts.items():z.writestr(name,b)
assert zipfile.ZipFile(final).testzip() is None
fw=openpyxl.load_workbook(final,data_only=False);fv=openpyxl.load_workbook(final,data_only=True)
errors=[{'sheet':s.title,'cell':cc.coordinate,'error':cc.value}for s in fv for row in s for cc in row if cc.data_type=='e']
assert not errors,errors[:15]
assert len(fw.sheetnames)==18 and sum(len(s._charts) for s in fw)==13
assert sha(c['template'])==model['template_sha256']
assert all(sha(s['path'])==s['sha256'] for s in model['sources'])
assert fv['14_Vistas_Ejecutivas']['C7'].value==1708 and fv['14_Vistas_Ejecutivas']['D7'].value==704
assert parts['xl/theme/theme1.xml']==orig['xl/theme/theme1.xml']
preserved=[n for n in orig if n.startswith('xl/drawings/')or n.startswith('xl/media/')]
assert all(parts[n]==orig[n] for n in preserved)
# Strict scan: no individual identifiers or orphaned shared strings from the original workbook.
private=json.loads((P/'datos.json').read_text());ids={str(v) for row in private['persons']for v in [row[3],row[5]]if v and v!='Pendiente' and len(str(v))>=6}
pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(x)for x in sorted(ids,key=len,reverse=True))+r')(?![A-Za-z0-9])')
assert not any(pattern.search(b.decode('utf8','ignore')) for n,b in parts.items() if n.endswith('.xml')),'Individual identifier in public workbook'
native=[]
for s in fw:
 for t in s.tables.values():
  a,b,c0,d0=openpyxl.utils.range_boundaries(t.ref)
  assert [x.name for x in t.tableColumns]==[str(s.cell(b,j).value)for j in range(a,c0+1)]
 native.append({'sheet':s.title,'charts':len(s._charts),'tables':len(s.tables)})
desktop=Path('/Users/alexi/Desktop')/final.name;shutil.copy2(final,desktop);assert sha(desktop)==sha(final)
pp=P/'TRAYECTORIAS_PRIVADAS_IPSS_20261021_153436.xlsx';assert pp.exists();pf=openpyxl.load_workbook(pp,data_only=False);pv=openpyxl.load_workbook(pp,data_only=True)
assert pv['Trayectorias'].max_row-5==1708 and pv['Matriculas'].max_row-5==len(private['observations'])
pe=[(s.title,cc.coordinate,cc.value)for s in pv for row in s for cc in row if cc.data_type=='e'];assert not pe,pe[:5]
nf=sum(cc.data_type=='f' for s in pf for row in s for cc in row);missing=sum(pv[s.title][cc.coordinate].value is None for s in pf for row in s for cc in row if cc.data_type=='f');assert missing==0
ordered=sorted(private['persons'],key=lambda r:(r[29],r[0]))
for i,row in enumerate(ordered,6):
 for col in [3,4,5,6]:
  value=pv['Trayectorias'].cell(i,col).value
  assert value in (None,'') if row[col-1]=='' else str(value)==str(row[col-1])
 for col,ix in [(12,11),(13,12),(16,15),(18,17)]:assert pv['Trayectorias'].cell(i,col).value==row[ix]
for root,dirs,files in __import__('os').walk(P,followlinks=False):
 __import__('os').chmod(root,0o700)
 for n in files:
  pth=Path(root)/n
  if not pth.is_symlink():__import__('os').chmod(pth,0o600)
git={'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'status':subprocess.check_output(['git','status','--short'],cwd=R,text=True)}
assert git['branch']=='feature/ire-2026' and git['HEAD']=='80ca13a5a249a1a2bd53a699f5f73689b1f53040'
qa={'date':datetime.datetime.now().astimezone().isoformat(),'status':'OK_CON_PENDIENTES_E','template_sha256':sha(c['template']),'public':{'path':str(final),'sha256':sha(final),'desktop':str(desktop),'identifiers':0,'sheets':18,'charts':13,'formula_errors':errors,'original_drawings_media_byte_identical':True,'theme_byte_identical':True,'table_headers_exact':True},'private':{'path':str(pp),'sha256':sha(pp),'persons':1708,'observations':len(private['observations']),'formulas':nf,'missing_caches':missing,'formula_errors':pe,'ignored':subprocess.run(['git','check-ignore','-q',str(pp)],cwd=R).returncode==0},'native_structure':native,'source_hashes_intact':True,'connected_filter_QA':'QA_FILTROS.json','native_excel':'No ejecutado; validación OOXML, recálculo Artifact Tool y controles independientes.','git':git,'no_commit_push':True}
(O/'QA_FINAL.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':qa['status'],'public':qa['public'],'private':qa['private']},ensure_ascii=False,indent=2))

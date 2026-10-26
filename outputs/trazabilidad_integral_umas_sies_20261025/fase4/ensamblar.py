"""Recupera las partes originales preservando gráficos; integra suplemento Artifact.

No usa un roundtrip de la maqueta para evitar perder dibujos/estilos/validaciones.
La edición completa contiene datos individuales: salida exclusivamente local.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from collections import Counter
from lxml import etree as E
import json,hashlib,os,re,posixpath,subprocess

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
P=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025')
ORIGINAL=Path('/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx')
BASE=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V18_CANDIDATA.xlsx')
DEST=P/'RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V19_TRAZABLE.xlsx'
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PR='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
q=lambda x:'{'+NS+'}'+x
n={'s':NS}
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def xml(b):return E.fromstring(b)
def dump(e):return E.tostring(e,encoding='utf-8',xml_declaration=True,standalone=True)
def load(p):return json.loads(p.read_text())
protected=load(OUT.parent/'fase1/CADENA_Y_FUENTES.json')['preservacion']
assert all(sha(Path(p))==h for p,h in protected.items())
assert not DEST.exists()
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
za=ZipFile(ORIGINAL);zb=ZipFile(BASE);zd=ZipFile(P/'suplemento.xlsx')
parts={i.filename:zb.read(i.filename) for i in zb.infolist()}
def ss(z):return [''.join(x.itertext()) for x in xml(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
sa=ss(za);sd=ss(zd)
def inline(root,strings):
    for c in root.findall('.//s:c',n):
        if c.get('t')=='s':
            v=c.find(q('v'));value=strings[int(v.text)];c.remove(v);c.set('t','inlineStr');t=E.SubElement(E.SubElement(c,q('is')),q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=value
    return root
def cells(root):return {c.get('r'):c for c in root.findall('.//s:sheetData/s:row/s:c',n)}
def value(c):
    if c is None:return None
    v=c.find(q('v'));t=c.find(q('is'))
    return ''.join(t.itertext()) if t is not None else v.text if v is not None else None
def getcell(root,ref):
    cs=cells(root)
    if ref in cs:return cs[ref]
    data=root.find(q('sheetData'));rn=int(re.search(r'\d+',ref).group());row=next((r for r in data if int(r.get('r'))==rn),None)
    if row is None:
        row=E.Element(q('row'),r=str(rn));data.append(row);data[:]=sorted(data,key=lambda r:int(r.get('r')))
    c=E.SubElement(row,q('c'),r=ref)
    def cn(x):
        a=re.match('[A-Z]+',x.get('r')).group();v=0
        for ch in a:v=v*26+ord(ch)-64
        return v
    row[:]=sorted(row,key=cn)
    return c
def content(c,text=None,formula=None,cache=None):
    for x in list(c):c.remove(x)
    c.attrib.pop('t',None)
    if formula is not None:
        E.SubElement(c,q('f')).text=formula.lstrip('=')
        if cache is not None:
            if isinstance(cache,str):c.set('t','str')
            E.SubElement(c,q('v')).text=str(cache)
    elif isinstance(text,(int,float)):
        E.SubElement(c,q('v')).text=str(text)
    else:
        c.set('t','inlineStr');E.SubElement(E.SubElement(c,q('is')),q('t')).text=str(text or '')
def copy_content(dst,src):
    for x in list(dst):dst.remove(x)
    dst.attrib.pop('t',None)
    if src.get('t'):dst.set('t',src.get('t'))
    for x in src:dst.append(deepcopy(x))

# Style indices in original are an exact prefix of the preserved V18 style set.
style=xml(parts['xl/styles.xml']);origstyle=xml(za.read('xl/styles.xml'))
for tag in ['numFmts','fonts','fills','borders','cellXfs','dxfs']:
    assert all(E.tostring(x)==E.tostring(y) for x,y in zip(origstyle.find(q(tag)),style.find(q(tag))))
restore_sources={10,12,21,25,26};restored=Counter();skipped=[];roots={}
correction=load(OUT.parent/'fase1/correcciones/MATRIZ_CORRECCIONES_V14_V18.json')
names=[s.get('name') for s in xml(parts['xl/workbook.xml']).find(q('sheets'))]
approved={(x['hoja'],x['celda']) for x in correction['celdas_V14_V16']}
for i in range(1,30):
    original=inline(xml(za.read(f'xl/worksheets/sheet{i}.xml')),sa)
    current=xml(parts[f'xl/worksheets/sheet{i}.xml'])
    if i in restore_sources:
        current=original;restored[names[i-1]]=len(current.findall('.//s:f',n))
        rel=f'xl/worksheets/_rels/sheet{i}.xml.rels'
        if rel in za.namelist():parts[rel]=za.read(rel)
    elif i!=28:
        target=cells(current)
        for ref,c in cells(original).items():
            dest=target.get(ref)
            if c.find(q('f')) is not None and dest is not None and dest.find(q('f')) is None:
                if (names[i-1],ref) in approved:skipped.append([names[i-1],ref]);continue
                assert value(c)==value(dest),f'Diferencia no aprobada: hoja {i}, {ref}'
                copy_content(dest,c);restored[names[i-1]]+=1
            # Recover formula description changed during aggregate-only delivery.
            if dest is not None and 'Foto de valores históricos preservados' in (value(dest) or ''):copy_content(dest,c)
        dv=original.find(q('dataValidations'))
        if dv is not None and current.find(q('dataValidations')) is None:
            after=['hyperlinks','printOptions','pageMargins','pageSetup','headerFooter','drawing','legacyDrawing','tableParts','extLst']
            idx=next((j for j,x in enumerate(current) if E.QName(x).localname in after),len(current));current.insert(idx,deepcopy(dv))
    roots[i]=current

# Append donor styles without reindexing any existing style or graphic.
donorstyle=xml(zd.read('xl/styles.xml'));offset={};num_map={}
for tag in ['numFmts','fonts','fills','borders','cellXfs','dxfs']:
    a=style.find(q(tag));b=donorstyle.find(q(tag));offset[tag]=len(a) if a is not None else 0
    if b is None:continue
    if a is None:a=E.Element(q(tag));style.insert(0,a)
    for item in b:
        item=deepcopy(item)
        if tag=='numFmts':
            ni=max([163]+[int(t.get('numFmtId')) for t in a])+1;num_map[int(item.get('numFmtId'))]=ni;item.set('numFmtId',str(ni))
        if tag=='cellXfs':
            for attr,k in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:item.set(attr,str(int(item.get(attr,'0'))+offset[k]))
            ni=int(item.get('numFmtId','0'));item.set('numFmtId',str(num_map.get(ni,ni)));item.set('xfId','0')
        a.append(item)
    a.set('count',str(len(a)))
parts['xl/styles.xml']=dump(style)
ct=xml(parts['[Content_Types].xml']);wb=xml(parts['xl/workbook.xml']);rels=xml(parts['xl/_rels/workbook.xml.rels'])
max_table=max(int(re.search(r'table(\d+)',p).group(1)) for p in parts if re.fullmatch(r'xl/tables/table\d+.xml',p))
def transplant(donor_index,target_index):
    global max_table
    root=inline(xml(zd.read(f'xl/worksheets/sheet{donor_index}.xml')),sd)
    for c in root.findall('.//s:c',n):c.set('s',str(int(c.get('s','0'))+offset['cellXfs']))
    for cf in root.findall('.//s:cfRule',n):
        if cf.get('dxfId'):cf.set('dxfId',str(int(cf.get('dxfId'))+offset['dxfs']))
    rr=f'xl/worksheets/_rels/sheet{donor_index}.xml.rels'
    if rr in zd.namelist():
        rrxml=xml(zd.read(rr))
        for rel in rrxml:
            target=rel.get('Target')
            if 'table' in rel.get('Type'):
                src=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/worksheets/'+target)
                tab=xml(zd.read(src));max_table+=1;tab.set('id',str(max_table));new=f'xl/tables/table{max_table}.xml';parts[new]=dump(tab);rel.set('Target',f'../tables/table{max_table}.xml')
                E.SubElement(ct,'{'+CT+'}Override',PartName='/'+new,ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml')
            else:assert rel.get('TargetMode')=='External','Unexpected donor relationship'
        parts[f'xl/worksheets/_rels/sheet{target_index}.xml.rels']=dump(rrxml)
    return root
roots[28]=transplant(1,28);roots[56]=transplant(2,56);roots[57]=transplant(3,57)
for i,name in [(56,'56_Vista_T1_T2_T3'),(57,'57_Trazabilidad_Actual')]:
    E.SubElement(wb.find(q('sheets')),q('sheet'),name=name,sheetId=str(i),attrib={'{'+R+'}id':f'rIdFase4_{i}'})
    E.SubElement(rels,'{'+PR+'}Relationship',Id=f'rIdFase4_{i}',Type=R+'/worksheet',Target=f'worksheets/sheet{i}.xml')
    E.SubElement(ct,'{'+CT+'}Override',PartName=f'/xl/worksheets/sheet{i}.xml',ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
for i in [52,53,54,55]:roots[i]=xml(parts[f'xl/worksheets/sheet{i}.xml'])
for i,di,cols,end in [(53,4,['F','K','M'],223),(54,5,['N'],226)]:
    dc=cells(xml(zd.read(f'xl/worksheets/sheet{di}.xml')))
    for row in range(6,end+1):
        for col in cols:copy_content(getcell(roots[i],f'{col}{row}'),dc[f'{col}{row}'])

notes={
 (52,'A1'):'52 · Seguimiento de T1 en T2 y T3 hasta 2026. C · Diccionario v8 activo; vista local trazable en hoja56. Tasas y denominadores conservados.',
 (52,'A32'):'C · Diccionario activo v8 verificado por hash. Cinco recuperaciones previamente aprobadas afectan estos contextos. No hay nuevas adjudicaciones en fases3–4.',
 (52,'A33'):'C · Fuente de conteos: vista56 → agregados54/53 → resumen52. Navegación y pendientes en57; evidencia de ejecución en MANIFEST_FASE4.json. No acredita aceptación SIES.',
 (55,'B11'):'E · 99 códigos de contexto pendientes; 24 del foco multiversión. No equivalen a personas ni afectan los denominadores.',
 (55,'D11'):'Ver hojas52 y57. Conteo actual conectado a detalle56.',
 (53,'J4'):'C · F/K/M consultan vista56; numeradores G y denominadores H conservan su materialización reproducible y alcance de V18.',
}
for (i,ref),text in notes.items():content(getcell(roots[i],ref),text=text)
content(getcell(roots[55],'B11'),formula='"E · "&\'52_Codigos_SIES_Revision\'!H24&" códigos pendientes; incluye24 multiversión. No son personas ni cambia denominadores."',cache='E · 99 códigos pendientes; incluye24 multiversión. No son personas ni cambia denominadores.')
for i,ref,target,label in [(1,'A42','57_Trazabilidad_Actual','V19 · Trazabilidad y pendientes actuales'),(19,'B99','57_Trazabilidad_Actual','Ver trazabilidad actual y pendientes'),(52,'A35','56_Vista_T1_T2_T3','Abrir detalle local T1–T2–T3 y evidencias')]:
    content(getcell(roots[i],ref),formula=f'HYPERLINK("#\'{target}\'!A1","{label}")',cache=label)

# Artifact's HYPERLINK is unsupported: use native worksheet hyperlinks.
# This also supports a donor already generated before that limitation was found.
link_cells={i:cells(roots[i]) for i in [28,56,57]}
def native_link(root,ref,location,label):
    cm=next(link_cells[i] for i in link_cells if roots[i] is root)
    content(cm[ref],text=label)
    h=root.find(q('hyperlinks'))
    if h is None:
        h=E.Element(q('hyperlinks'))
        after=['printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst']
        idx=next((j for j,x in enumerate(root) if E.QName(x).localname in after),len(root));root.insert(idx,h)
    E.SubElement(h,q('hyperlink'),ref=ref,location=location,display=label)
payload=load(P/'payload.json')
for j,row in enumerate(payload['rows'],6):native_link(roots[56],f'AA{j}',f"'20_Foto_BBDD'!A{row[0]}",'Ver origen')
for j,row in enumerate(payload['guide'],5):native_link(roots[28],f'E{j}',f"'{row[0]}'!A1",'Abrir hoja')
for ref,loc,label in [('B23',"'56_Vista_T1_T2_T3'!A5",'Abrir detalle'),('B24',"'18_Foto_Intertrimestral'!B5",'Ver resultados'),('B25',"'27_Guia_Hojas'!A4",'Ver guía')]:native_link(roots[57],ref,loc,label)

def update_dimension(root):
    cs=list(cells(root));maxr=max(int(re.search(r'\d+',a).group()) for a in cs)
    def num(a):
        v=0
        for ch in re.match('[A-Z]+',a).group():v=v*26+ord(ch)-64
        return v
    maxc=max(cs,key=num);col=re.match('[A-Z]+',maxc).group();dim=root.find(q('dimension'))
    if dim is None:dim=E.Element(q('dimension'));root.insert(1 if root.find(q('sheetPr')) is not None else 0,dim)
    dim.set('ref',f'A1:{col}{maxr}')
for i,root in roots.items():update_dimension(root);parts[f'xl/worksheets/sheet{i}.xml']=dump(root)
calc=wb.find(q('calcPr'))
if calc is None:calc=E.SubElement(wb,q('calcPr'))
calc.set('calcMode','auto');calc.set('fullCalcOnLoad','1');calc.set('forceFullCalc','1')
for rel in list(rels):
    if 'calcChain' in rel.get('Type',''):rels.remove(rel)
for elem in list(ct):
    if elem.get('PartName')=='/xl/calcChain.xml':ct.remove(elem)
parts.pop('xl/calcChain.xml',None)
parts['xl/workbook.xml']=dump(wb);parts['xl/_rels/workbook.xml.rels']=dump(rels);parts['[Content_Types].xml']=dump(ct)

# Structural invariants before writing any final book.
assert len(wb.find(q('sheets')))==57
for name,b in parts.items():
    if name.endswith('.xml') or name.endswith('.rels'):xml(b)
charts=[p for p in parts if re.fullmatch(r'xl/charts/chart\d+.xml',p)]
assert len(charts)==13 and all(parts[p]==zb.read(p) for p in charts)
assert all(sha(Path(p))==h for p,h in protected.items())
with ZipFile(DEST,'x',ZIP_DEFLATED,compresslevel=6) as z:
    for name,b in parts.items():z.writestr(name,b)
os.chmod(DEST,0o600)
stats={'original':str(ORIGINAL),'base':str(BASE),'salida_privada':str(DEST),'sha256':sha(DEST),'hojas':57,'graficos':13,'tablas':len([p for p in parts if re.fullmatch(r'xl/tables/table\d+.xml',p)]),'formulas':sum(len(xml(b).findall('.//s:f',n)) for p,b in parts.items() if re.fullmatch(r'xl/worksheets/sheet\d+.xml',p)),'formulas_recuperadas_por_hoja':dict(restored),'correcciones_no_revertidas':skipped,'fuentes_preservadas':True,'bases_denominadores_modificados':False,'recalculo_completo':'Pendiente fase5; suplemento recalculado Artifact Tool','publicacion_git':False}
(OUT/'ENSAMBLADO.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:stats[k] for k in ['hojas','graficos','tablas','formulas','sha256']},ensure_ascii=False))

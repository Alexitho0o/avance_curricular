"""Inyecta únicamente columnas de procedencia creadas con Artifact Tool."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json, hashlib, collections, posixpath, subprocess, copy

ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular')
OUT=Path(__file__).parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/procedencia_v24_20261025')
SRC=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V23.xlsx')
DST=SRC.with_name(SRC.name.replace('_V23','_V24'))
SOURCE=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json')
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'; n={'m':NS}
def tag(x): return '{'+NS+'}'+x
def hash(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def strings(z):
 if 'xl/sharedStrings.xml' not in z.namelist(): return []
 return [''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall(tag('si'))]
def val(c,ss):
 if c is None:return None
 if c.get('t')=='inlineStr': return ''.join(c.find(tag('is')).itertext())
 v=c.findtext(tag('v'))
 return ss[int(v)] if c.get('t')=='s' else v

assert not DST.exists()
assert hash(SRC)=='d8cec9c835552608cb0752a0aba2d050ca7fa506ec9559edd96800a03497d97c'
assert subprocess.run(['git','-C',str(PRIVATE),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
z=ZipFile(SRC); f=ZipFile(PRIVATE/'fragment.xlsx'); ss=strings(z); fs=strings(f)
part='xl/worksheets/sheet56.xml'; root=E.fromstring(z.read(part)); frag=E.fromstring(f.read('xl/worksheets/sheet1.xml'))
rows={int(r.get('r')):r for r in root.find(tag('sheetData'))}; cells={c.get('r'):c for r in rows.values() for c in r}
slots=json.loads(SOURCE.read_text()); flat=[(s,c) for s in slots for c in (s['contextos'] or [None])]
assert len(flat)==6374
for rn,(s,c) in enumerate(flat,6):
 assert val(cells.get(f'M{rn}'),ss)==s['codigo_origen_T1']
 assert val(cells.get(f'N{rn}'),ss)==(c['codigo_destino'] or 'Pendiente' if c else 'Pendiente')
 assert val(cells.get(f'H{rn}'),ss)==(c['CODCLI'] if c else 'Pendiente')
counts=collections.Counter(); newcells=0
for row in frag.find(tag('sheetData')):
 rn=int(row.get('r'))
 for c in row:
  ref=c.get('r'); col=''.join(x for x in ref if x.isalpha())
  if col not in ['AC','AD','AE','AF']:continue
  assert ref not in cells
  if c.get('t')=='s':
   text=val(c,fs); c.remove(c.find(tag('v'))); c.set('t','inlineStr'); E.SubElement(E.SubElement(c,tag('is')),tag('t')).text=text
  c.set('s','185' if rn==5 else '184')
  rows[rn].append(c);newcells+=1
  if col=='AC' and rn>=6:
   assert c.find(tag('f')) is not None
   value=val(c,fs);assert value and not value.startswith('#');counts[value]+=1
assert dict(counts)==json.loads((PRIVATE/'counts.json').read_text())
root.find(tag('dimension')).set('ref','A1:AF6379')
cols=root.find(tag('cols'))
for i,w in [(29,50),(30,23),(31,78),(32,18)]:E.SubElement(cols,tag('col'),min=str(i),max=str(i),width=str(w),customWidth='1')
replacements={part:E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)}
rels=E.fromstring(z.read('xl/worksheets/_rels/sheet56.xml.rels'))
tp=root.find(tag('tableParts'))
rid=tp[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
target=next(r.get('Target') for r in rels if r.get('Id')==rid)
tablepath=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/worksheets/'+target)
t=E.fromstring(z.read(tablepath)); assert t.get('ref')=='A5:AB6379'
t.set('ref','A5:AF6379')
if t.find(tag('autoFilter')) is not None:t.find(tag('autoFilter')).set('ref','A5:AF6379')
tc=t.find(tag('tableColumns'));tc.set('count','32')
for i,h in enumerate(['Procedencia del código destino','Continuidad T1 corroborada (1/0)','Evidencia o condición pendiente','Clase de respaldo'],29):E.SubElement(tc,tag('tableColumn'),id=str(i),name=h)
replacements[tablepath]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
with ZipFile(DST,'x',ZIP_DEFLATED) as dest:
 for item in z.infolist():dest.writestr(copy.copy(item),replacements.get(item.filename,z.read(item.filename)))
d=ZipFile(DST);assert d.testzip() is None
changed=[name for name in z.namelist() if z.read(name)!=d.read(name)]
assert set(changed)==set(replacements)
for name in d.namelist():
 if name.endswith('.xml'):E.fromstring(d.read(name))
# Original cell XML and formulas are semantically identical; only new columns added.
after=E.fromstring(d.read(part)); ac={c.get('r'):c for r in after.find(tag('sheetData')) for c in r}
for ref,c in cells.items(): assert E.tostring(c)==E.tostring(ac[ref])
report={'clasificacion':'B/C; decisiones previas D; pendientes E','estado':'QA_ESTRUCTURAL_Y_CLASIFICACION_OK','origen':str(SRC),'sha256_origen':hash(SRC),'salida':str(DST),'sha256_salida':hash(DST),'fuente_privada_sha256':hash(SOURCE),'filas':len(flat),'categorias':dict(counts),'componentes_modificados':changed,'celdas_agregadas':newcells,'contextos_pendientes':99,'sin_contexto':3520,'nuevas_adjudicaciones':0,'formulas_nuevas':6374,'bases_denominadores_y_graficos_preservados':True,'recalculo':'Clasificaciones nuevas recalculadas con Artifact Tool; libro completo no recalculado en Excel nativo','commit':False,'push':False,'HEAD':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()}
(OUT/'QA_MANIFEST_V24.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))

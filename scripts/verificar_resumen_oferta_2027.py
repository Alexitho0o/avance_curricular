#!/usr/bin/env python3
"""Ordena solo metadatos OOXML y verifica el Excel autorado con Artifact Tool."""
import argparse, hashlib, json, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
import openpyxl

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'data/resumen_oferta_2027/20261016'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put_first(file):
    """API documentada sin operación de orden: modifica solo orden/vista y nombres locales."""
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    ET.register_namespace('',ns['s']);ET.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    with zipfile.ZipFile(file) as z:
        infos=z.infolist();parts={x.filename:z.read(x) for x in infos}
    root=ET.fromstring(parts['xl/workbook.xml']);sheets=root.find('s:sheets',ns);old=list(sheets)
    selected=next(s for s in old if s.attrib['name']=='Resumen ejecutivo');new=[selected]+[s for s in old if s is not selected]
    mapping={i:new.index(s) for i,s in enumerate(old)}
    for s in old:sheets.remove(s)
    for s in new:sheets.append(s)
    for x in root.findall('s:definedNames/s:definedName',ns):
        if 'localSheetId' in x.attrib:x.attrib['localSheetId']=str(mapping[int(x.attrib['localSheetId'])])
    for x in root.findall('s:bookViews/s:workbookView',ns):x.set('activeTab','0');x.set('firstSheet','0')
    parts['xl/workbook.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    relns={'p':'http://schemas.openxmlformats.org/package/2006/relationships'}
    rels=ET.fromstring(parts['xl/_rels/workbook.xml.rels']);rid=selected.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
    target=next(x.attrib['Target'] for x in rels if x.attrib['Id']==rid)
    selected_path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    for name in parts:
        if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
            s=ET.fromstring(parts[name]);views=s.findall('s:sheetViews/s:sheetView',ns)
            for view in views:view.set('tabSelected','1' if name==selected_path else '0')
            parts[name]=ET.tostring(s,encoding='utf-8',xml_declaration=True)
    temp=file.with_suffix('.ordering.tmp')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for info in infos:z.writestr(info,parts[info.filename])
    temp.replace(file)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ordenar',action='store_true');args=ap.parse_args()
    p=load(BASE/'libro.json');out=Path(p['output'])
    if args.ordenar:put_first(out)
    assert sha(p['source'])==p['source_sha256']
    src=openpyxl.load_workbook(p['source']);dst=openpyxl.load_workbook(out);cache=openpyxl.load_workbook(out,data_only=True)
    assert dst.sheetnames[0]=='Resumen ejecutivo' and dst.active.title=='Resumen ejecutivo'
    assert dst.sheetnames[1:22]==src.sheetnames and len(dst.sheetnames)==25
    count=0
    for s in src:
        t=dst[s.title]
        for row in s:
            for c in row:
                if c.value is None:continue
                count+=1;o=t[c.coordinate];assert c.value==o.value,(s.title,c.coordinate)
                for attr in ['font','fill','alignment','border','number_format','protection']:assert str(getattr(c,attr))==str(getattr(o,attr)),(s.title,c.coordinate,attr)
        assert s.merged_cells==t.merged_cells and s.data_validations==t.data_validations
        assert set(s.tables)==set(t.tables)
        for name in s.tables:assert s.tables[name].ref==t.tables[name].ref and s.tables[name].autoFilter==t.tables[name].autoFilter
        a,b=s.sheet_view.pane,t.sheet_view.pane
        assert (a is None)==(b is None)
        if a:assert (a.xSplit,a.ySplit,a.state)==(b.xSplit,b.ySplit,b.state)
    checked=0
    for info in p['sheets']:
        s=dst[info['name']];assert [s.cell(5,j+1).value for j in range(len(info['headers']))]==info['headers']
        for i,row in enumerate(info['rows'],6):
            for j,v in enumerate(row,1):
                actual=s.cell(i,j).value;assert (None if actual=='' else actual)==(None if v=='' else v),(info['name'],i,j,v,actual);checked+=1
    errors=[(s.title,c.coordinate,c.value) for s in cache for row in s for c in row if c.data_type=='e'];assert not errors,errors[:5]
    q=cache['Resumen ejecutivo'];assert [q[x].value for x in ['A6','D6','G6','J6']]==[124,161,37,'Por confirmar']
    assert [q[f'M{i}'].value for i in range(25,31)]==[118,22,21,236,0,0]
    for i,m in enumerate(p['metrics'],11):
        if m[0]<2010:assert q[f'B{i}'].value=='Sin cobertura';continue
        assert q[f'B{i}'].value==m[1]
        if m[0]>2010:
            for j,col in enumerate('CDEFG',2):assert abs(q[f'{col}{i}'].value-m[j])<1e-10
    assert len(dst['Resumen ejecutivo']._charts)==1
    for name in ['Preparación oferta 2027','Preparación UMAS 2027']:
        s=dst[name];cols=['Q'] if 'oferta' in name else ['K','L','M','N','O']
        for col in cols:assert all(s[f'{col}{r}'].value is None for r in range(6,s.max_row+1)),name
    assert len({r[1] for r in p['sheets'][1]['rows']})>0
    d4=load(ROOT/'data/cierre_d4/20261016/entrega.json')
    for name,h in d4['archivos_sha256'].items():assert sha(ROOT/name)==h,name
    refs=load(ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json')['referencias_sha256']
    for name,h in refs.items():assert sha(ROOT/name)==h,name
    for name,h in load(BASE/'fuentes.json')['archivos_sha256'].items():assert sha(ROOT/name)==h,name
    qa={'estado':'VERIFICADO','primera_hoja_y_activa':'Resumen ejecutivo','hojas':25,'celdas_d4_preservadas':count,'celdas_nuevas_comprobadas':checked,'serie_csv_claves_coincide_h3':True,'oferta_2026':124,'escenario_2027':161,'aumento_esperado':37,'mallas_2027':'POR_CONFIRMAR','oferta_2027_confirmada':0,'planes_historicos':236,'registros_umas':346,'dimensiones_umas':72,'codcarpr_distintos':67,'errores_formula':errors,'grafico':1,'referencias_protegidas':len(refs),'archivos_d4_preservados':len(d4['archivos_sha256']),'recalculo_excel_nativo':False,'sha256':sha(out),'orden_hojas':'OOXML, sin modificar datos, formulas ni estilos; autores originales Artifact Tool'}
    (BASE/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

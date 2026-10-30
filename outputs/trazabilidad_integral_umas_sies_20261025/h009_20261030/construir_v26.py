"""Parche acotado de gráficos: auxiliares nativos, nombres dinámicos y cachés.

Preserva todas las celdas originales. No calcula cohortes ni enlaces. Las tasas
de orden se obtienen únicamente de numeradores/denominadores auxiliares existentes.
"""
import argparse,copy,json,hashlib,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZipInfo
from lxml import etree as E
from openpyxl.utils.cell import get_column_letter as col,column_index_from_string as colnum
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
M=N['m'];C=N['c']
def t(x):return '{'+M+'}'+x
def ct(x):return '{'+C+'}'+x
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xml(e):return E.tostring(e,xml_declaration=True,encoding='UTF-8',standalone=True)
def cells(root,ss):
    out={}
    for c in root.findall('m:sheetData/m:row/m:c',N):
        v=c.findtext('m:v',namespaces=N)
        if c.get('t')=='s':v=ss[int(v)]
        elif c.get('t')=='inlineStr':v=''.join(c.find('m:is',N).itertext())
        elif v is not None and c.get('t') not in ('str','e'):
            try:v=float(v)
            except ValueError:pass
        out[c.get('r')]=v
    return out
def main():
    p=argparse.ArgumentParser()
    for key in ('origen','salida','informes'):p.add_argument('--'+key,required=True)
    a=p.parse_args();source=Path(a.origen);dest=Path(a.salida);out=Path(a.informes)
    assert sha(source)=='63b55351334616833a2e687fbeb36314a0cbb1538c10b6a891c99f94475adc0a'
    assert not dest.exists(),'La copia de salida ya existe; no sobrescribir'
    z=ZipFile(source);ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
    roots={14:E.fromstring(z.read('xl/worksheets/sheet15.xml')),16:E.fromstring(z.read('xl/worksheets/sheet17.xml'))}
    values={s:cells(r,ss) for s,r in roots.items()};replacement={};wb=E.fromstring(z.read('xl/workbook.xml'));names=wb.find('m:definedNames',N)
    configs=[(4,14,'DA',['DB'],2,5,'BR',40),(5,14,'DD',['DE'],2,4,'H',7),(6,14,'DG',['DH','DI'],2,5,None,40),
        (7,14,'DK',['DL'],2,18,'T',7),(8,14,'DN',['DO'],2,28,'Z',7),(9,14,'DQ',['DR'],2,4,'AE',7),
        (10,14,'DT',['DU'],2,4,'AJ',7),(11,14,'DW',['DX'],2,6,'AO',7),
        (12,16,'B',['E','F','H','J'],8,11,None,8),(13,16,'L',['O','P'],38,41,None,38)]
    specs=[]
    for index,(chart,s,label,series,start,end,denom,dr) in enumerate(configs):
        root=roots[s];v=values[s];sheet='14_Vistas_Ejecutivas' if s==14 else '16_Comparacion_Nacional_SIES'
        # Each block: category, sort rate, rank, compact category, series values.
        c0=1000+index*10;lc,vc,rc,oc=[col(c0+i) for i in range(4)];sc=[col(c0+4+i) for i in range(len(series))]
        sd=root.find('m:sheetData',N);rows={int(r.get('r')):r for r in sd};existing={c.get('r') for r in sd for c in r}
        def add(address,formula,value=None,style='0'):
            assert address not in existing,address
            rn=int(re.search(r'\d+',address)[0])
            if rn not in rows:rows[rn]=E.SubElement(sd,t('row'),r=str(rn))
            cell=E.SubElement(rows[rn],t('c'),r=address,s=style)
            E.SubElement(cell,t('f')).text=formula
            if value is not None:
                if value=='#N/A':cell.set('t','e')
                elif isinstance(value,str):cell.set('t','str')
                E.SubElement(cell,t('v')).text=str(value)
        observations=[];n=end-start+1
        for j,r in enumerate(range(start,end+1),2):
            d=dr+j-2;category=v.get(f'{label}{r}');sr=[v.get(f'{c}{r}') for c in series]
            if chart==6:
                ds=[v.get(f'{c}{d}',0) for c in ('BT','BV')];nums=[v.get(f'{c}{d}',0) for c in ('BU','BW')]
                total=sum(ds);key=sum(nums)/total if total else None
                keyf=f'IF(SUM(BT{d},BV{d})>0,SUM(BU{d},BW{d})/SUM(BT{d},BV{d}),"")'
                sr=[num/den if den else None for num,den in zip(nums,ds)]
            elif chart in (12,13):
                key=sr[1] if isinstance(sr[1],(int,float)) else None
                keyf=f'IF(ISNUMBER({series[1]}{r}),{series[1]}{r},"")'
            else:
                total=v.get(f'{denom}{d}',0);key=sr[0] if isinstance(total,(int,float)) and total>0 and isinstance(sr[0],(int,float)) else None
                keyf=f'IF(AND({denom}{d}>0,ISNUMBER({series[0]}{r})),{series[0]}{r},"")'
            valid=category not in (None,'',0) and key is not None
            observations.append({'source_row':r,'helper_row':j,'categoria':category,'orden':key if valid else None,'series':sr})
            add(f'{lc}{j}',f'{label}{r}',category)
            add(f'{vc}{j}',f'IF(AND({label}{r}<>"",{label}{r}<>0),{keyf},"")',key if valid else '')
        ordered=sorted([x for x in observations if x['orden'] is not None],key=lambda x:(x['orden'],str(x['categoria']).casefold(),x['source_row']))
        ranks={x['helper_row']:i for i,x in enumerate(ordered,1)}
        vr=f'${vc}$2:${vc}${n+1}';lr=f'${lc}$2:${lc}${n+1}';rr=f'${rc}$2:${rc}${n+1}'
        for x in observations:
            j=x['helper_row'];rf=f'IF(ISNUMBER({vc}{j}),COUNTIFS({vr},"<"&{vc}{j},{vr},">=0")+COUNTIFS({vr},{vc}{j},{lr},"<"&{lc}{j})+COUNTIFS(${vc}$2:{vc}{j},{vc}{j},${lc}$2:{lc}{j},{lc}{j}),"")'
            add(f'{rc}{j}',rf,ranks.get(j,''))
        add(f'{rc}1',f'COUNT({rr})',len(ordered))
        for k in range(1,n+1):
            j=k+1;x=ordered[k-1] if k<=len(ordered) else None
            match=f'MATCH({k},{rr},0)'
            add(f'{oc}{j}',f'IFERROR(INDEX({lr},{match}),"")',x['categoria'] if x else '')
            for si,output_col in enumerate(sc):
                input_col=series[si];sr_range=f'${input_col}${start}:${input_col}${end}'
                val=x['series'][si] if x else None
                if chart==6:
                    dc,nc=[('BT','BU'),('BV','BW')][si]
                    den=f'INDEX(${dc}$40:${dc}$43,{match})';num=f'INDEX(${nc}$40:${nc}$43,{match})'
                    formula=f'IFERROR(IF({den}>0,{num}/{den},NA()),NA())'
                else:formula=f'IFERROR(IF(ISNUMBER(INDEX({sr_range},{match})),INDEX({sr_range},{match}),NA()),NA())'
                pct_style=root.find('.//m:c[@r="'+('DB2' if s==14 else 'E8')+'"]',N).get('s','0')
                add(f'{output_col}{j}',formula,val if isinstance(val,(int,float)) else '#N/A',style=pct_style)
        for suffix,c in [('CAT',oc)]+[(f'S{i+1}',c) for i,c in enumerate(sc)]:
            name=f'H009_G{chart}_{suffix}';assert not any(x.get('name')==name for x in names)
            E.SubElement(names,t('definedName'),name=name).text=f"INDEX('{sheet}'!${c}$2:${c}${n+1},1):INDEX('{sheet}'!${c}$2:${c}${n+1},MAX(1,'{sheet}'!${rc}$1))"
        part=f'xl/charts/chart{chart}.xml';ch=E.fromstring(z.read(part));sers=ch.findall('.//c:ser',N);assert len(sers)==len(series)
        for si,ser in enumerate(sers):
            cat=ser.find('c:cat',N);val=ser.find('c:val',N)
            for node,suffix,is_text in [(cat,'CAT',True),(val,f'S{si+1}',False)]:
                node.clear();ref=E.SubElement(node,ct('strRef' if is_text else 'numRef'))
                E.SubElement(ref,ct('f')).text=f"'{dest.name}'!H009_G{chart}_{suffix}"
                cache=E.SubElement(ref,ct('strCache' if is_text else 'numCache'))
                if not is_text:E.SubElement(cache,ct('formatCode')).text='0.0%'
                E.SubElement(cache,ct('ptCount'),val=str(len(ordered)))
                for i,x in enumerate(ordered):
                    value=x['categoria'] if is_text else x['series'][si]
                    if value is None or value=='':continue
                    point=E.SubElement(cache,ct('pt'),idx=str(i));E.SubElement(point,ct('v')).text=str(value)
        horizontal=bool(ch.xpath('//c:barDir[@val="bar"]',namespaces=N))
        for axis in ch.findall('.//c:catAx',N):
            orient=axis.find('c:scaling/c:orientation',N)
            if orient is not None:orient.set('val','maxMin' if horizontal else 'minMax')
        for nf in ch.findall('.//c:dLbls/c:numFmt',N):nf.set('formatCode','0.0%');nf.set('sourceLinked','0')
        replacement[part]=xml(ch)
        specs.append({'grafico':chart,'hoja':sheet,'columnas_auxiliares':f'{lc}:{sc[-1]}','contador':f'{rc}1','orden':'SIES' if chart in (12,13) else 'TOTAL_PONDERADA' if chart==6 else 'TASA_SERIE','categorias_iniciales':len(ordered),'observaciones_iniciales':ordered,'clase':'D criterio; C implementación'})
    for s,root in roots.items():
        sd=root.find('m:sheetData',N);sd[:]=sorted(sd,key=lambda x:int(x.get('r')))
        for row in sd:row[:]=sorted(row,key=lambda x:colnum(re.match('[A-Z]+',x.get('r'))[0]))
        dim=root.find('m:dimension',N);endrow=max(int(x.get('r')) for x in sd);last=max(colnum(re.match('[A-Z]+',c.get('r'))[0]) for row in sd for c in row)
        dim.set('ref',f'A1:{col(last)}{endrow}')
        replacement[f'xl/worksheets/sheet{s+1}.xml']=xml(root)
    calc=wb.find('m:calcPr',N);calc.set('fullCalcOnLoad','1');calc.set('forceFullCalc','1');replacement['xl/workbook.xml']=xml(wb)
    with ZipFile(dest,'x',ZIP_DEFLATED) as target:
        for item in z.infolist():
            info=ZipInfo(item.filename,(2026,10,30,0,0,0));info.compress_type=ZIP_DEFLATED
            target.writestr(info,replacement.get(item.filename,z.read(item.filename)))
    out.mkdir(parents=True,exist_ok=True)
    (out/'CONFIG_GRAFICOS.json').write_text(json.dumps({'origen_sha256':sha(source),'salida_sha256_pre_excel':sha(dest),'graficos':specs,'limites':'NA() intencional solo en auxiliares de series ausentes; no cero de relleno. Selección vacía usa ancla vacía sin puntos.'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'graficos_corregidos':len(specs),'sha256':sha(dest)}))
if __name__=='__main__':main()

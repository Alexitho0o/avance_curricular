"""Stream immutable source cells into an Artifact-authored workbook.

Only source literals are deferred. Calculations and cached results are preserved;
other ZIP members, including Artifact-authored charts and styles, stay identical.
"""
import json
from copy import copy
import math
from pathlib import Path
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
RNS='http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def column_name(index):
    result=''
    while index:
        index,rem=divmod(index-1,26)
        result=chr(65+rem)+result
    return result


def column_number(name):
    result=0
    for char in name:
        result=result*26+ord(char)-64
    return result


def validate_source_dependencies(payload):
    """Fail closed if a future calculation starts reading a deferred literal."""
    sources={t['name']:t for t in payload['main'] if t.get('stream_source_literals')}
    if sources and any(re.search(r'\b(?:INDIRECT|OFFSET)\s*\(',formula,re.I)
                       for table in payload['main'] for formula in table['formulas'].values()):
        raise ValueError('Referencia dinamica no verificable con una fuente diferida.')
    for name,source in sources.items():
        allowed={re.match(r'[A-Z]+',a)[0] for a in source['formulas']}
        pattern=re.compile(re.escape("'"+name+"'!"),re.I)
        for table in payload['main']:
            for address,formula in table['formulas'].items():
                for match in pattern.finditer(formula):
                    reference=re.match(r'\$?([A-Z]+)(?:\$?\d+)?(?::\$?([A-Z]+)(?:\$?\d+)?)?(?![A-Z0-9_])',
                                       formula[match.end():],re.I)
                    if reference is None:
                        raise ValueError(f'Referencia no verificable a una fuente diferida: {table["name"]}!{address}')
                    first,last=reference[1].upper(),(reference[2] or reference[1]).upper()
                    lower,upper=sorted((column_number(first),column_number(last)))
                    if any(column_name(c) not in allowed for c in range(lower,upper+1)):
                        raise ValueError(f'Formula depende de una fuente diferida: {table["name"]}!{address}')
    return sources


def source_cell(address,value,style):
    cell=ET.Element(f'{{{NS}}}c',{'r':address,'s':style})
    if isinstance(value,bool):
        cell.set('t','b')
        ET.SubElement(cell,f'{{{NS}}}v').text='1' if value else '0'
    elif isinstance(value,(int,float)):
        if not math.isfinite(value):
            raise ValueError(f'Numero no finito en {address}')
        ET.SubElement(cell,f'{{{NS}}}v').text=str(value)
    else:
        value=str(value)
        if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',value):
            raise ValueError(f'Caracter XML no valido en {address}; no eliminar silenciosamente.')
        cell.set('t','inlineStr')
        inline=ET.SubElement(cell,f'{{{NS}}}is')
        ET.SubElement(inline,f'{{{NS}}}t',{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=value
    return cell


def write_source_sheet(output,original,table):
    root=ET.fromstring(original)
    data=root.find(f'{{{NS}}}sheetData')
    existing={int(row.attrib['r']):row for row in data}
    sample=existing[7].find(f'{{{NS}}}c')
    style=sample.attrib.get('s','0')
    for column in root.findall(f'{{{NS}}}cols/{{{NS}}}col'):
        column.set('style',style)
    end=len(table['rows'])+6
    dimension=root.find(f'{{{NS}}}dimension')
    if dimension is None:
        dimension=ET.Element(f'{{{NS}}}dimension')
        root.insert(1 if root.find(f'{{{NS}}}sheetPr') is not None else 0,dimension)
    dimension.set('ref',f'A1:{column_name(len(table["headers"]))}{max(7,end)}')
    if root.find(f'{{{NS}}}autoFilter') is None and table['rows']:
        root.insert(list(root).index(data)+1,ET.Element(f'{{{NS}}}autoFilter',{
            'ref':f'A6:{column_name(len(table["headers"]))}{end}'}))
    data.clear()
    marker='ANUAL_STREAMED_SHEET_DATA'
    data.text=marker
    prefix,suffix=ET.tostring(root,encoding='utf-8',xml_declaration=True).split(marker.encode())
    output.write(prefix)
    for number in range(1,max(7,end)+1):
        row=existing.pop(number,None)
        if number<=6:
            if row is not None:
                output.write(ET.tostring(row,encoding='utf-8'))
            continue
        if row is None:
            row=ET.Element(f'{{{NS}}}row',{'r':str(number),'ht':'30','customHeight':'1'})
        cells={c.attrib['r']:c for c in row}
        for c in list(row):
            row.remove(c)
        values=table['rows'][number-7] if number<=end else []
        for index,value in enumerate(values,1):
            address=f'{column_name(index)}{number}'
            if address in table['formulas']:
                cell=cells.get(address)
                if cell is None or cell.find(f'{{{NS}}}f') is None:
                    raise ValueError(f'Formula fuente perdida: {table["name"]}!{address}')
                row.append(cell)
            elif value is not None and value!='':
                row.append(source_cell(address,value,style))
        output.write(ET.tostring(row,encoding='utf-8'))
    output.write(suffix)


def complete_source_sheets(path,payload):
    sources=validate_source_dependencies(payload)
    if not sources:
        return
    ET.register_namespace('',NS)
    ET.register_namespace('r',RNS)
    path=Path(path)
    temporary=path.with_suffix('.sources.tmp')
    evidence=[]
    try:
        with zipfile.ZipFile(path) as source, zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as target:
            rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(source.read('xl/_rels/workbook.xml.rels'))}
            edits={}
            for sheet in ET.fromstring(source.read('xl/workbook.xml')).find(f'{{{NS}}}sheets'):
                if sheet.attrib['name'] in sources:
                    member=rels[sheet.attrib[f'{{{RNS}}}id']]
                    member=member.lstrip('/') if member.startswith('/') else 'xl/'+member
                    edits[member]=sources[sheet.attrib['name']]
            if len(edits)!=len(sources):
                raise ValueError('Faltan hojas de respuestas en el libro exportado.')
            for info in source.infolist():
                with target.open(copy(info),'w',force_zip64=True) as out:
                    if info.filename in edits:
                        table=edits[info.filename]
                        write_source_sheet(out,source.read(info.filename),table)
                        evidence.append({'hoja':table['name'],'filas':len(table['rows']),
                                         'columnas':len(table['headers']),'formulas_conservadas':len(table['formulas'])})
                    else:
                        with source.open(info) as incoming:
                            shutil.copyfileobj(incoming,out,1024*1024)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    audit=path.parent.parent/'04_AUDITORIA'
    (audit/'escritura_fuentes_incremental.json').write_text(json.dumps({
        'modo':'LITERALES_POR_FILA','hojas':evidence,
        'calculos_y_graficos':'Artifact Tool; no modificados por el transporte XML',
        'validacion_celda_a_celda':'obligatoria antes de publicar'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

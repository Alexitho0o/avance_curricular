#!/usr/bin/env python3
"""Comprueba contenido y rasgos OOXML del Excel H8, sin editarlo."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def col(index):
    value='';index+=1
    while index:index,rem=divmod(index-1,26);value=chr(65+rem)+value
    return value


def read_book(path):
    z=zipfile.ZipFile(path);assert z.testzip() is None
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(el.itertext()) for el in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    rels={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    result={}
    for item in ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets',NS):
        target=rels[item.attrib['{'+REL+'}id']];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        tree=ET.fromstring(z.read(target));cells={};formulas={};types={}
        for cell in tree.findall('.//s:sheetData/s:row/s:c',NS):
            addr=cell.attrib['r'];t=cell.get('t');node=cell.find('s:v',NS);raw=None if node is None else node.text
            if t=='s':value=strings[int(raw)]
            elif t=='inlineStr':value=''.join(cell.find('s:is',NS).itertext())
            elif t in ('str','e'):value=raw or ''
            elif t=='b':value=raw=='1'
            elif raw is None:value=None
            else:value=float(raw);value=int(value) if value.is_integer() else value
            cells[addr]=value;types[addr]=t
            formula=cell.find('s:f',NS)
            if formula is not None:formulas[addr]=formula.text or ''
        result[item.attrib['name']]={'cells':cells,'formulas':formulas,'types':types,'tree':tree}
    return z,result


def verify(workbook,payload_path):
    payload=json.loads(payload_path.read_text());z,book=read_book(workbook)
    assert len(book)==len(payload['sheets'])+1
    comparisons=0;tablecounts={}
    for s in payload['sheets']:
        data=book[s['name']]
        for i,h in enumerate(s['headers']):assert data['cells'][col(i)+'5']==h
        for rownum,row in enumerate(s['rows'],start=6):
            for i,expected in enumerate(row):
                actual=data['cells'].get(col(i)+str(rownum))
                assert (actual if actual is not None else '')==(expected if expected is not None else ''),(s['name'],rownum,i,actual,expected)
                if isinstance(expected,str) and expected:
                    assert data['types'][col(i)+str(rownum)] in ('s','inlineStr','str'),(s['name'],rownum,i,'identificador convertido')
                comparisons+=1
        assert data['tree'].find('s:sheetViews/s:sheetView/s:pane',NS) is not None,s['name']
        tablecounts[s['name']]=len(s['rows'])
    errors=[(name,addr,value) for name,data in book.items() for addr,value in data['cells'].items() if data['types'][addr]=='e']
    assert not errors,errors
    assert not any(n.startswith('xl/externalLinks/') or n.endswith('vbaProject.bin') for n in z.namelist())
    tables=[n for n in z.namelist() if n.startswith('xl/tables/table') and n.endswith('.xml')]
    assert len(tables)==len(payload['sheets'])
    for name in tables:assert ET.fromstring(z.read(name)).find('s:autoFilter',NS) is not None,name
    q=book['Consulta']['cells']
    assert q['B11']=='INGENIERIA EN LOGISTICA'
    assert q['B31']=='PENDIENTE_EVIDENCIA' and q.get('B33','') in ('',None)
    assert q['B34']=='I162S2C77J4V1\nI162S2C77J4V2'
    assert q['B37']=='No' and q['B38']==0
    dic=next(s for s in payload['sheets'] if s['name']=='Diccionario SIES')
    assert len({r[0] for r in dic['rows']})==141
    assert sum(bool(r[1]) for r in dic['rows'])==124
    assert sum(bool(r[18]) for r in dic['rows'])==61
    codes={r[0] for r in dic['rows']}
    assert {'I162M2008N1','I162M2008N3','I162S2C46J2V2','I162S2C46J4V2'}<=codes
    # Compare the grouped context algorithm to every H7-derived UMAS test.
    keyrows=next(s for s in payload['sheets'] if s['name']=='Claves UMAS')['rows']
    groups={tuple(r[:5]):r for r in keyrows};assert len(groups)==len(keyrows)
    contexts={tuple(r[:4]) for r in keyrows}
    for case in payload['tests_umas']:
        p=case['params'];fields=[p[k] for k in ('codcarpr','plan_umas','sede_umas','jornada_umas','nombre_interno')]
        missing=any(not isinstance(p[k],str) or not p[k] or p[k].upper() in ('NULL','NONE','NAN') for k in ('codcarpr','plan_umas','sede_umas','jornada_umas','nombre_interno','periodo','regimen'))
        state='SIN_EQUIVALENCIA';reason='';candidates=[]
        if missing:state='ENTRADA_INCOMPLETA'
        elif not 2007<=p['anio']<=2026:state='FUERA_AMBITO'
        elif p['anio']<2010:state='SIN_OFERTA_ANUAL';reason='SIN_COBERTURA_ANUAL'
        elif p['anio']==2026:
            row=groups.get(tuple(fields))
            if row:state=row[8];reason=row[9];candidates=row[6].split('\n')
            elif tuple(fields[:4]) in contexts:reason='NOMBRE_INTERNO_NO_COINCIDE'
        assert (state,reason,candidates)==(case['estado'],case['motivo'],case['candidatos']),p
    semantic={'sheets':{name:{'cells':data['cells'],'formulas':data['formulas'],'types':data['types'],
                    'panes':[node.attrib for node in data['tree'].findall('s:sheetViews/s:sheetView/s:pane',NS)]}
              for name,data in book.items()},
              'styles_sha256':hashlib.sha256(z.read('xl/styles.xml')).hexdigest(),
              'tables':{name:hashlib.sha256(z.read(name)).hexdigest() for name in tables}}
    return {'estado':'APROBADO','xlsx_sha256':hashlib.sha256(workbook.read_bytes()).hexdigest(),
            'contenido_semantico_sha256':hashlib.sha256(json.dumps(semantic,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
            'hojas':len(book),'tablas_con_filtro':len(tables),'filas_por_tabla':tablecounts,
            'celdas_datos_comparadas':comparisons,'errores_formula':errors,
            'casos_algoritmo_contra_h7':len(payload['tests_umas']),
            'nombres_literales_2026':124,'sectores_2026_respaldados':61,
            'macros_y_vinculos_externos':False,'recalculo_nativo_excel_verificado':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--libro',type=Path,required=True);parser.add_argument('--datos',type=Path,required=True)
    parser.add_argument('--salida',type=Path,required=True);args=parser.parse_args()
    report=verify(args.libro,args.datos)
    args.salida.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

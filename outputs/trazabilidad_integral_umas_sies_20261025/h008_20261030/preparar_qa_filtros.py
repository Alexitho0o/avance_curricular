"""Materializa 77 escenarios del motor COUNTIFS/SUMIFS en una copia privada.

No sustituye los selectores del libro de entrega ni modifica su contenido.
Usa las fórmulas auxiliares reales de hoja 14, sustituyendo sólo sus parámetros.
"""
import argparse,json,re,copy
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from qa_h008 import book,N
NS=N['m']
def tag(x):return '{'+NS+'}'+x
def main():
    p=argparse.ArgumentParser()
    for x in ['libro','casos','salida']:p.add_argument('--'+x,required=True)
    a=p.parse_args();z,b=book(a.libro);dest=Path(a.salida);assert not dest.exists()
    cases=json.loads(Path(a.casos).read_text());assert len(cases)==77
    root=copy.deepcopy(b['57_Trazabilidad_Actual']['root']);sd=root.find('m:sheetData',N)
    assert max(int(r.get('r')) for r in sd)<40
    source=b['14_Vistas_Ejecutivas']['cells']
    def add(row,col,value,formula=False):
        c=E.SubElement(row,tag('c'),r=f'{col}{row.get("r")}')
        if formula:E.SubElement(c,tag('f')).text=value
        elif isinstance(value,(int,float)):E.SubElement(c,tag('v')).text=str(value)
        else:c.set('t','inlineStr');E.SubElement(E.SubElement(c,tag('is')),tag('t')).text=value
    for i,c in enumerate(cases,40):
        row=E.SubElement(sd,tag('row'),r=str(i));years=[2022,2023,2024,2025] if c['cohorte']=='Acumulado 2022-2025' else [y for y in [2022,2023,2024,2025] if str(y) in c['cohorte']]
        for col,k in [('A','cohorte'),('B','sector'),('C','carrera'),('F','n'),('G','retenidos')]:add(row,col,c[k])
        for col,stem in [('D','BR'),('E','BS')]:
            terms=[]
            for y,r in zip([2022,2023,2024,2025],range(40,44)):
                f=source[f'{stem}{r}']['f']
                for old,new in [(f'$BQ{r}',str(int(y in years))),(f'$BP{r}',str(y)),('$BO$12',f'IF(B{i}="Todos","*",B{i})'),('$BO$13',f'IF(C{i}="Todas","*",C{i})')]:f=f.replace(old,new)
                assert not re.search(r'\$(?:BQ|BP|BO)',f)
                terms.append(f)
            add(row,col,'SUM('+','.join(terms)+')',True)
        add(row,'H',f'AND(D{i}=F{i},E{i}=G{i})',True)
        row[:]=sorted(row,key=lambda cell:cell.get('r').rstrip('0123456789'))
    root.find('m:dimension',N).set('ref','A1:Q116')
    with ZipFile(dest,'x',ZIP_DEFLATED) as out:
        for item in z.infolist():out.writestr(item,E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if item.filename==b['57_Trazabilidad_Actual']['part'] else z.read(item.filename))
    print('77 escenarios preparados en copia privada; requiere recálculo nativo.')
if __name__=='__main__':main()

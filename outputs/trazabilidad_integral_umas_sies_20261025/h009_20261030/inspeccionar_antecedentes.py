"""Lectura de gráficos y auxiliares agregados, sin escribir los libros originales."""
import argparse,json,re,hashlib
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def inspect(p):
 z=ZipFile(p);charts=[]
 for k in z.namelist():
  if re.fullmatch(r'xl/(?:drawings/)?charts/chart\d+\.xml',k):
   x=E.fromstring(z.read(k));charts.append({'parte':k,'refs':x.xpath('//c:f/text()',namespaces=N),'solo_visibles':x.xpath('//c:plotVisOnly/@val',namespaces=N),'vacios':x.xpath('//c:dispBlanksAs/@val',namespaces=N),'categorias_cache':[x.text for x in x.findall('.//c:cat//c:pt/c:v',N)]})
 selectors=[];samples=[]
 for k in z.namelist():
  if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',k):
   x=E.fromstring(z.read(k));d=x.findall('.//m:dataValidation',N)
   if d:selectors.append({'parte':k,'validaciones':[{'rango':e.get('sqref'),'tipo':e.get('type'),'formula':e.findtext('m:formula1',namespaces=N)} for e in d]})
   if k=='xl/worksheets/sheet15.xml':
    for c in x.findall('.//m:c',N):
     if re.fullmatch(r'(?:CV|CW|DA|DB)(?:2|3|7|8|9)',c.get('r','')):
      samples.append({'celda':c.get('r'),'formula':c.findtext('m:f',namespaces=N)})
 return {'ruta':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'graficos':charts,'selectores':selectors,'muestra_auxiliar':samples}
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--auditado',required=True);p.add_argument('--salida',required=True);a=p.parse_args();r=Path(a.repo)
 files=[Path(a.auditado),r/'outputs/entrega_retencion_20261029/ENTREGA_RETENCION_IPSS_20261029.xlsx',r/'outputs/excel_resumen_cruce_20261030/RESUMEN_CRUCE_SIES_UMAS_20261030.xlsx']
 data=[inspect(f) for f in files];Path(a.salida).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'archivo':Path(d['ruta']).name,'graficos':len(d['graficos']),'validaciones':len(d['selectores'])} for d in data]))
if __name__=='__main__':main()

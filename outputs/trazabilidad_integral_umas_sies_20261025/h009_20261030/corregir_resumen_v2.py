"""Copia H006: compacta y ordena sus tres gráficos conectados a selectores.

No modifica el detalle ni los paneles. La serie histórica fija queda cronológica.
La copia requiere QA nativo; cachés iniciales no equivalen a ese control.
"""
import argparse,json,re,hashlib
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from lxml import etree as E
from construir_v26 import N,M,C,t,ct,xml,sha,cells,col,colnum
def main():
 p=argparse.ArgumentParser();[p.add_argument('--'+x,required=True) for x in ['origen','salida','informe']];a=p.parse_args();src=Path(a.origen);dest=Path(a.salida)
 assert sha(src)=='5338543e375ed227e0297ed6ab136e1a67392e94f5969b1dd38b0d537578b03d';assert not dest.exists()
 z=ZipFile(src);ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
 wb=E.fromstring(z.read('xl/workbook.xml'));names=wb.find('m:definedNames',N)
 if names is None:
  names=E.Element(t('definedNames'));sheets=wb.find('m:sheets',N);wb.insert(list(wb).index(sheets)+1,names)
 roots={};replace={};report=[]
 for idx,(ch,sn,sheet,lc,vc,first,last) in enumerate([(2,8,'7_Ofertadas_No_Abiertas','O','P',8,24),(3,9,'8_Tendencia_Matricula','AI','AJ',8,17),(4,9,'8_Tendencia_Matricula','AL','AM',8,17)]):
  part=f'xl/worksheets/sheet{sn}.xml';root=roots.setdefault(part,E.fromstring(z.read(part)));val=cells(root,ss);sd=root.find('m:sheetData',N);rows={int(r.get('r')):r for r in sd};existing={c.get('r') for r in sd for c in r};base=200+idx*7;ls,vs,rs,lo,vo=[col(base+i) for i in range(5)];n=last-first+1
  style=root.find(f'.//m:c[@r="{vc}{first}"]',N).get('s','0')
  obs=[{'cat':val.get(f'{lc}{r}'),'valor':val.get(f'{vc}{r}'),'r':r} for r in range(first,last+1)];valid=[x for x in obs if x['cat'] not in ('',None,0) and isinstance(x['valor'],(int,float)) and x['valor']!=0];ordered=sorted(valid,key=lambda x:(x['valor'],str(x['cat']).casefold(),x['r']));ranks={x['r']:i for i,x in enumerate(ordered,1)}
  def add(addr,f,value,st='0'):
   assert addr not in existing;rn=int(re.search(r'\d+',addr)[0])
   if rn not in rows:rows[rn]=E.SubElement(sd,t('row'),r=str(rn))
   c=E.SubElement(rows[rn],t('c'),r=addr,s=st);E.SubElement(c,t('f')).text=f
   if isinstance(value,str):c.set('t','e' if value=='#N/A' else 'str')
   E.SubElement(c,t('v')).text=str(value)
  vr=f'${vs}$2:${vs}${n+1}';lr=f'${ls}$2:${ls}${n+1}';rr=f'${rs}$2:${rs}${n+1}'
  for j,x in enumerate(obs,2):
   r=x['r'];add(f'{ls}{j}',f'{lc}{r}',x['cat'] if x['cat'] is not None else '')
   add(f'{vs}{j}',f'IF(AND({lc}{r}<>"",ISNUMBER({vc}{r}),{vc}{r}<>0),{vc}{r},"")',x['valor'] if r in ranks else '')
   add(f'{rs}{j}',f'IF(ISNUMBER({vs}{j}),COUNTIFS({vr},"<"&{vs}{j},{vr},"<>")+COUNTIFS({vr},{vs}{j},{lr},"<"&{ls}{j})+COUNTIFS(${vs}$2:{vs}{j},{vs}{j},${ls}$2:{ls}{j},{ls}{j}),"")',ranks.get(r,''))
  add(f'{rs}1',f'COUNT({rr})',len(ordered))
  for k in range(1,n+1):
   x=ordered[k-1] if k<=len(ordered) else None;add(f'{lo}{k+1}',f'IFERROR(INDEX({lr},MATCH({k},{rr},0)),"")',x['cat'] if x else '')
   add(f'{vo}{k+1}',f'IFERROR(INDEX({vr},MATCH({k},{rr},0)),NA())',x['valor'] if x else '#N/A',style)
  for suffix,c in [('CAT',lo),('VAL',vo)]:E.SubElement(names,t('definedName'),name=f'H009_RES{ch}_{suffix}').text=f"INDEX('{sheet}'!${c}$2:${c}${n+1},1):INDEX('{sheet}'!${c}$2:${c}${n+1},MAX(1,'{sheet}'!${rs}$1))"
  cp=f'xl/drawings/charts/chart{ch}.xml';chart=E.fromstring(z.read(cp));ser=chart.find('.//c:ser',N)
  for what,suffix,kind in [('cat','CAT','str'),('val','VAL','num')]:
   node=ser.find('c:'+what,N);node.clear();ref=E.SubElement(node,ct(kind+'Ref'));E.SubElement(ref,ct('f')).text=f"'{dest.name}'!H009_RES{ch}_{suffix}";cache=E.SubElement(ref,ct(kind+'Cache'))
   if kind=='num':E.SubElement(cache,ct('formatCode')).text='0'
   E.SubElement(cache,ct('ptCount'),val=str(len(ordered)))
   for i,x in enumerate(ordered):pt=E.SubElement(cache,ct('pt'),idx=str(i));E.SubElement(pt,ct('v')).text=str(x['cat'] if what=='cat' else x['valor'])
  horizontal=bool(chart.xpath('//c:barDir[@val="bar"]',namespaces=N))
  for ax in chart.findall('.//c:catAx',N):
   orient=ax.find('c:scaling/c:orientation',N)
   if orient is not None:orient.set('val','maxMin' if horizontal else 'minMax')
  replace[cp]=xml(chart);report.append({'grafico':ch,'hoja':sheet,'categorias':len(ordered),'orden':ordered,'contador':rs+'1','sin_cambiar_tablas':True})
 for part,root in roots.items():
  sd=root.find('m:sheetData',N);sd[:]=sorted(sd,key=lambda x:int(x.get('r')))
  for row in sd:row[:]=sorted(row,key=lambda x:colnum(re.match('[A-Z]+',x.get('r'))[0]))
  dim=root.find('m:dimension',N)
  if dim is not None:dim.set('ref',f'A1:{col(220)}{max(int(r.get("r")) for r in sd)}')
  replace[part]=xml(root)
 calc=wb.find('m:calcPr',N)
 if calc is not None:calc.set('fullCalcOnLoad','1');calc.set('forceFullCalc','1')
 replace['xl/workbook.xml']=xml(wb)
 with ZipFile(dest,'x',ZIP_DEFLATED) as target:
  for k in z.namelist():info=ZipInfo(k,(2026,10,30,0,0,0));info.compress_type=ZIP_DEFLATED;target.writestr(info,replace.get(k,z.read(k)))
 Path(a.informe).write_text(json.dumps({'clase':'C corrección; E QA nativo','original_sha256':sha(src),'copia_sha256':sha(dest),'graficos':report,'limite':'Se conserva el panel completo de datos y sus ceros observados; se retira relleno del gráfico. Verificación nativa pendiente por fallo de Excel en H009.'},ensure_ascii=False,indent=2)+'\n');print(sha(dest))
if __name__=='__main__':main()

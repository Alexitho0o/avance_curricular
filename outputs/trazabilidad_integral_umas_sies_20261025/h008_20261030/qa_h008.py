"""QA estructural, preservación y regresión independiente; no sustituye QA nativo."""
import argparse, collections, json, posixpath, re, subprocess, math
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from openpyxl.formula.translate import Translator
from preparar import load,sha,write
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def book(path):
    z=ZipFile(path);assert z.testzip() is None
    for name in z.namelist():
        if name.endswith('.xml'):E.fromstring(z.read(name))
    ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
    rel={e.get('Id'):e.get('Target') for e in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};out={}
    for sheet in E.fromstring(z.read('xl/workbook.xml')).find('m:sheets',N):
        target=rel[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];part=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target);root=E.fromstring(z.read(part));cells={};masters={};followers=[]
        rows=[int(r.get('r')) for r in root.findall('m:sheetData/m:row',N)];assert rows==sorted(set(rows)),'Orden/duplicado de filas inválido'
        for c in root.findall('m:sheetData/m:row/m:c',N):
            ref=c.get('r');typ=c.get('t');v=c.findtext('m:v',namespaces=N);i=c.find('m:is',N);f=c.find('m:f',N)
            if i is not None:v=''.join(i.itertext())
            elif typ=='s':v=ss[int(v)]
            elif v is not None and typ not in ['str','e','d']:
                try:v=float(v);v=int(v) if v.is_integer() else v
                except ValueError:pass
            formula=f.text if f is not None else None
            if f is not None and f.get('t')=='shared':
                if f.text:masters[f.get('si')]=(ref,f.text)
                else:followers.append((ref,f.get('si')))
            cells[ref]={'v':v,'f':formula,'t':typ,'style':int(c.get('s','0'))}
        for ref,si in followers:
            start,f=masters[si];cells[ref]['f']=Translator('='+f,origin=start).translate_formula(ref)[1:]
        out[sheet.get('name')]={'part':part,'cells':cells,'root':root}
    return z,out
def equal(a,b):
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-10)
    return a==b
def check(args):
    cfg=load(args.config);o=Path(args.salida);z,b=book(cfg['entradas']['v24']['ruta']);v,d=book(args.libro);_,ref=book(cfg['entradas']['v24_recalculada']['ruta']);checks=[]
    def ck(name,ok,detail=None):checks.append({'control':name,'pasa':bool(ok),'detalle':detail})
    ck('V24 hash intacto',sha(cfg['entradas']['v24']['ruta'])==cfg['entradas']['v24']['sha256'])
    ck('57 hojas preservadas',list(b)==list(d) and len(d)==57)
    lost=[];changed=[]
    for sheet,s in b.items():
        for addr,x in s['cells'].items():
            new=d[sheet]['cells'].get(addr)
            if new is None:lost.append([sheet,addr]);continue
            if x['f']!=new['f'] or (x['f'] is None and not equal(x['v'],new['v'])):changed.append([sheet,addr])
    ck('Contenido y fórmulas anteriores preservados',not lost and not changed,{'perdidas':lost,'cambios':changed})
    charts=[n for n in z.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml',n)]
    ck('13 gráficos sin cambios OOXML',len(charts)==13 and all(z.read(n)==v.read(n) for n in charts))
    tables=lambda zz:len([n for n in zz.namelist() if re.fullmatch(r'xl/tables/table\d+\.xml',n)])
    ck('Tablas preservadas',tables(z)==tables(v),tables(v))
    styles=E.fromstring(v.read('xl/styles.xml')).find('m:cellXfs',N)
    aligned=all(x.find('m:alignment',N) is not None and x.find('m:alignment',N).get('horizontal')=='center' and x.find('m:alignment',N).get('vertical')=='center' for x in styles)
    ck('Todos los estilos centrados H/V',aligned)
    errors=[{'hoja':s,'celda':a} for s,sh in d.items() for a,x in sh['cells'].items() if x['t']=='e']
    ck('Sin errores almacenados',not errors,errors)
    s=d['56_Vista_T1_T2_T3']['cells'];ck('C1 posiciones 1135',sum(s.get(f'AG{r}',{}).get('v',0) or 0 for r in range(6,6380))==1135)
    ck('C1 contextos 1136',sum(s.get(f'AH{r}',{}).get('v',0) or 0 for r in range(6,6380))==1136)
    # Repetición de los 77 escenarios desde el detalle preservado. No afirmar
    # ejecución de selectores en Excel si no se dispone de su evidencia nativa.
    base=d['9_Base_Analitica_Detalle']['cells'];rows=[]
    mapping=d['8_Mapeo_Sector_IPSS']['cells']
    sectors={mapping.get(f'B{r}',{}).get('v'):mapping.get(f'C{r}',{}).get('v') for r in range(6,23)}
    for rn in range(7,2386):
        row={k:base.get(f'{col}{rn}',{}).get('v') for k,col in [('cohorte','B'),('carrera','C'),('sector','E'),('retenido','F')]}
        # Evaluación independiente de la búsqueda exacta de sector conservada;
        # la caché V24 vacía no se interpreta como sector ausente.
        expected=f'IFERROR(VLOOKUP(C{rn},\'8_Mapeo_Sector_IPSS\'!$B$6:$C$22,2,FALSE()),"SIN MAPEO")'
        assert base[f'E{rn}']['f']==expected
        row['sector']=sectors.get(row['carrera'],'SIN MAPEO')
        rows.append(row)
    filters=[]
    for i,c in enumerate(load(cfg['entradas']['casos_filtros']['ruta']),1):
        yy=[2022,2023,2024,2025] if c['cohorte']=='Acumulado 2022-2025' else [y for y in [2022,2023,2024,2025] if str(y) in c['cohorte']]
        rr=[x for x in rows if x['cohorte'] in yy and (c['sector']=='Todos' or x['sector']==c['sector']) and (c['carrera']=='Todas' or x['carrera']==c['carrera'])];n=len(rr);ret=sum(x['retenido'] for x in rr)
        filters.append({'caso':i,'n':n,'retenidos':ret,'esperado_n':c['n'],'esperado_retenidos':c['retenidos'],'coincide':(n,ret)==(c['n'],c['retenidos'])})
    ck('77 escenarios independientes',len(filters)==77 and all(x['coincide'] for x in filters))
    write(o/'FILTROS_77_REGRESION.json',{'clase':'C regresión independiente','casos':filters,'limite':'No equivale a 77 interacciones nativas; esta certificación se informa aparte.'})
    # Comparación verificable de fórmulas e insumos; cachés originales vacíos no
    # se convierten en cero. La referencia numérica es la copia QA gobernada.
    comparisons=[]
    for rn in range(7,15):
        for col in 'DEFGH':
            addr=f'{col}{rn}';x=ref['18_Foto_Intertrimestral']['cells'].get(addr,{});y=d['18_Foto_Intertrimestral']['cells'].get(addr,{})
            comparisons.append({'hoja':'18_Foto_Intertrimestral','celda':addr,'V24_referencia_recalculada':x.get('v'),'V25_cache':y.get('v'),'formula_preservada':b['18_Foto_Intertrimestral']['cells'].get(addr,{}).get('f')==y.get('f'),'delta':y.get('v')-x.get('v') if isinstance(y.get('v'),(int,float)) and isinstance(x.get('v'),(int,float)) else None,'causa':'Sin cambio de regla/insumos R19; C1 y fotos solo respaldos separados','clase':'C; certificación nativa pendiente si caché vacío'})
    write(o/'COMPARACION_V24_V25.json',{'celdas':comparisons,'tasas_referencia':[{'indicador':'T1 2026 → T3','numerador':1360,'denominador':1467},{'indicador':'Total T3 2026','numerador':2290,'denominador':2519},{'indicador':'Ingreso T2 2026','numerador':462,'denominador':528}],'cambio_calculo_esperado_pp':0,'limite':'Esperado por preservación; no se presenta como recálculo nativo si no consta.'})
    old=load(Path(args.privado)/'ESTADO_INICIAL.json');r=Path(args.repo)
    ck('Cambios ajenos intactos',all((r/f).is_file() and sha(r/f)==h for f,h in old['ajenos'].items()))
    ck('Stage vacío',not subprocess.check_output(['git','-C',str(r),'diff','--cached','--name-only']).strip())
    ck('v20 y R19 intactos',all(sha(e['ruta'])==e['sha256'] for k,e in cfg['entradas'].items()))
    report={'clase':'B/C; requisitos no certificados E','controles':checks,'pasan':sum(x['pasa'] for x in checks),'total':len(checks),'estado':'PASS_ESTRUCTURAL_NO_CERTIFICACION_NATIVA' if all(x['pasa'] for x in checks) else 'FAIL','nativo':{'recalculo_completo':'PENDIENTE','77_filtros_en_Excel':'PENDIENTE','apertura_sin_reparacion':'PENDIENTE','revision_visual_13_graficos':'PENDIENTE'},'sha256_v25':sha(args.libro)}
    write(o/'QA_H008.json',report);print(json.dumps({'estado':report['estado'],'pasan':report['pasan'],'total':report['total']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();[p.add_argument('--'+x,required=True) for x in ['config','libro','salida','privado','repo']];check(p.parse_args())

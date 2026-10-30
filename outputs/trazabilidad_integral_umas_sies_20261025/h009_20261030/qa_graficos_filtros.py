"""QA reproducible de auxiliares y preservación; exige evidencia nativa separada.

Nunca trata una caché o simulación como prueba visual. --nativo permite incorporar
las 77 selecciones capturadas por Excel; sin ellas el QA completo permanece E.
"""
import argparse,hashlib,json,re,sys,math
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from openpyxl.utils.cell import column_index_from_string as ci,get_column_letter as cl
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'h008_20261030'))
from qa_h008 import book,equal,N
C={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def validar_aux(rows):
    n=int(rows[0][2]);raw=rows[1:];selected=[x for x in raw if isinstance(x[1],(float,int)) and not isinstance(x[1],bool)]
    expected=sorted(selected,key=lambda x:(x[1],str(x[0]).casefold()))
    ranks=[x[2] for x in selected]
    # Excel usa su colación regional; comparar orden numérico y rango estable,
    # además de la igualdad de etiquetas cuando no existe empate.
    actual=[x[3] for x in raw[:n]]
    expected_names=[x[0] for x in expected]
    return {'cantidad':n,'cantidad_correcta':n==len(selected),'rangos_consecutivos':sorted(ranks)==list(range(1,n+1)),
      'orden':actual==expected_names,'sin_etiquetas_vacias':all(x not in ('',None,0) for x in actual),
      'series_ausentes':sum(x in ('#N/A',None,'') for row in raw[:n] for x in row[4:]),
      'ceros_observados':sum(x==0 for row in raw[:n] for x in row[4:])}
def main():
    p=argparse.ArgumentParser();[p.add_argument('--'+x,required=True) for x in ['origen','libro','config','salida']];p.add_argument('--nativo');a=p.parse_args()
    cfg=json.loads(Path(a.config).read_text());oz,old=book(a.origen);z,new=book(a.libro)
    changed=[];diff=[];compared=0;errors=[];aligned=[];omitted=0
    styles=E.fromstring(z.read('xl/styles.xml')).find('m:cellXfs',N)
    for sn,sh in old.items():
      for addr,x in sh['cells'].items():
        y=new[sn]['cells'].get(addr)
        if y is None and x['f'] is None and x['v'] is None:omitted+=1;continue
        if y is None or x['f']!=y['f'] or (x['f'] is None and not equal(x['v'],y['v'])):changed.append({'hoja':sn,'celda':addr})
        if isinstance(x['v'],(int,float)):
          compared+=1
          if not equal(x['v'],(y or {}).get('v')):diff.append({'hoja':sn,'celda':addr})
    intentional=0
    for sn,sh in new.items():
      for addr,x in sh['cells'].items():
        is_aux=sn in ('14_Vistas_Ejecutivas','16_Comparacion_Nacional_SIES') and ci(re.match('[A-Z]+',addr)[0])>=1000
        if x['t']=='e':
          if is_aux and x['v']=='#N/A' and 'NA()' in (x['f'] or ''):intentional+=1
          else:errors.append({'hoja':sn,'celda':addr})
        if x['v'] is None and x['f'] is None:continue
        al=styles[x['style']].find('m:alignment',N)
        if al is None or al.get('horizontal')!='center' or al.get('vertical')!='center':aligned.append({'hoja':sn,'celda':addr})
    charts=lambda zz:sorted(k for k in zz.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml',k))
    tables=lambda zz:sorted(k for k in zz.namelist() if re.fullmatch(r'xl/tables/table\d+\.xml',k))
    ns=E.fromstring(z.read('xl/workbook.xml')).find('m:definedNames',N);names={x.get('name'):x.text for x in ns}
    controls={'V25_hash_intacto':sha(a.origen)==cfg['origen_sha256'],'hojas_preservadas':list(old)==list(new),
       'contenido_original_preservado':not changed,'numeros_originales_iguales':not diff,'sin_errores_inesperados':not errors,
       'centrado_HV':not aligned,'13_graficos':len(charts(z))==13,'37_tablas':len(tables(z))==37}
    aux=[]
    for spec in cfg['graficos']:
      sc=new[spec['hoja']]['cells'];start,end=spec['columnas_auxiliares'].split(':');c0=ci(start);cend=ci(end);rows=[]
      n=len(spec['observaciones_iniciales'])
      # Máximo del bloque se obtiene de sus fórmulas, no de la selección actual.
      present=[int(re.search(r'\d+',k)[0]) for k in sc if re.match('[A-Z]+',k)[0]==start];last=max(present)
      for rn in range(1,last+1):rows.append([sc.get(f'{cl(c)}{rn}',{}).get('v') for c in range(c0,cend+1)])
      check=validar_aux(rows);check['grafico']=spec['grafico'];aux.append(check)
      part=f"xl/charts/chart{spec['grafico']}.xml";ch=E.fromstring(z.read(part));refs=ch.xpath('//c:ser/c:cat//c:f/text()|//c:ser/c:val//c:f/text()',namespaces=C)
      controls[f"G{spec['grafico']}_nombres_dinamicos"]=all('!H009_' in f for f in refs) and all('INDEX(' in v for k,v in names.items() if k.startswith(f"H009_G{spec['grafico']}_"))
      controls[f"G{spec['grafico']}_orden_y_compactacion"]=all(check[k] for k in ('cantidad_correcta','rangos_consecutivos','orden','sin_etiquetas_vacias'))
    uid='{http://schemas.microsoft.com/office/spreadsheetml/2014/revision}uid'
    def filt(zz):
      result={}
      for k in tables(zz):
        root=E.fromstring(zz.read(k));af=root.find('m:autoFilter',N)
        result[root.get('name')]=None if af is None else [(E.QName(x).localname,{k:v for k,v in x.attrib.items() if k!=uid},x.text) for x in af.iter()]
      return result
    controls['filtros_preservados']=filt(oz)==filt(z)
    native=json.loads(Path(a.nativo).read_text()) if a.nativo else {'estado':'E_NO_COMPLETADO','casos_certificados':0}
    if a.nativo:
      cases=native.get('casos',[])
      checks=[]
      for case in cases:
        match=case['totales'][:2]==[case['seleccion']['n'],case['seleccion']['retenidos']]
        results=[validar_aux(g['aux']) for g in case['graficos']]
        checks.append(match and len(results)==8 and all(all(r[k] for k in ('cantidad_correcta','rangos_consecutivos','orden','sin_etiquetas_vacias')) for r in results))
      controls['77_selectores_nativos']=len(cases)==77 and all(checks)
      controls['capturas_revisadas']=native.get('capturas_revisadas',0)>=4
    result={'estado':'PASS_ESTRUCTURAL_CON_QA_NATIVO_E' if all(controls.values()) else 'FAIL','clase':'C QA estructural; B cachés Excel; E cobertura nativa',
      'controles':controls,'valores_numericos_comparados':compared,'diferencias_numericas':diff,'celdas_originales_alteradas':changed,
      'errores_inesperados':errors,'NA_intencionales_auxiliares':intentional,'no_centradas':aligned,'vacias_omitidas':omitted,
      'auxiliares':aux,'qa_nativo':native,'sha256_v26':sha(a.libro),'sha256_v25':sha(a.origen)}
    write(a.salida,result);print(json.dumps({k:result[k] for k in ('estado','valores_numericos_comparados','sha256_v26')}));assert all(controls.values())
if __name__=='__main__':main()

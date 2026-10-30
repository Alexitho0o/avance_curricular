"""Verificación de solo lectura después del guardado nativo; no automatiza Excel."""
import argparse,json,re
from pathlib import Path
from lxml import etree as E
from qa_h008 import book,equal,N
from preparar import sha,load,write

def main():
    p=argparse.ArgumentParser()
    for x in ['config','libro','salida']:p.add_argument('--'+x,required=True)
    a=p.parse_args();cfg=load(a.config)
    old,base=book(cfg['entradas']['v24']['ruta'])
    z,current=book(a.libro)
    _,reference=book(cfg['entradas']['v24_recalculada']['ruta'])
    changes=[];differences=[];errors=[];not_centered=[];empty_omitted=[];n=0
    styles=E.fromstring(z.read('xl/styles.xml')).find('m:cellXfs',N)
    for sheet,s in base.items():
        for addr,x in s['cells'].items():
            y=current[sheet]['cells'].get(addr)
            if y is None and x['f'] is None and x['v'] is None:
                empty_omitted.append({'hoja':sheet,'celda':addr,'causa':'Celda OOXML sin valor ni fórmula omitida al guardar en Excel'})
                continue
            if y is None or x['f']!=y['f'] or (x['f'] is None and not equal(x['v'],y['v'])):
                changes.append({'hoja':sheet,'celda':addr})
    by_sheet={}
    for sheet,s in reference.items():
        count=0
        for addr,x in s['cells'].items():
            if x['f'] is not None and isinstance(x['v'],(int,float)):
                n+=1;count+=1
                if not equal(x['v'],current[sheet]['cells'].get(addr,{}).get('v')):
                    differences.append({'hoja':sheet,'celda':addr})
        by_sheet[sheet]=count
    for sheet,s in current.items():
        for addr,x in s['cells'].items():
            if x['t']=='e':errors.append({'hoja':sheet,'celda':addr})
            if x['v'] is None and x['f'] is None:continue
            alignment=styles[x['style']].find('m:alignment',N)
            if alignment is None or alignment.get('horizontal')!='center' or alignment.get('vertical')!='center':
                not_centered.append({'hoja':sheet,'celda':addr})
    charts=lambda zz:sorted(k for k in zz.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml',k))
    tables=lambda zz:sorted(k for k in zz.namelist() if re.fullmatch(r'xl/tables/table\d+\.xml',k))
    # Comparación de referencias de series; no exige serialización XML idéntica.
    chart_ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
    refs=lambda zz,k:E.fromstring(zz.read(k)).xpath('//c:f/text()',namespaces=chart_ns)
    series_equal=charts(old)==charts(z) and all(refs(old,k)==refs(z,k) for k in charts(old))
    def filters(zz):
        return {E.fromstring(zz.read(k)).get('name'):E.fromstring(zz.read(k)).find('m:autoFilter',N) for k in tables(zz)}
    old_filters=filters(old);new_filters=filters(z)
    # La guía de hojas nunca tuvo autofiltro. Se preservan los existentes y se
    # comprueba por separado el filtro ampliado de la vista de seguimiento.
    # Excel puede reescribir namespaces: comparar atributos y descendientes.
    revision_uid='{http://schemas.microsoft.com/office/spreadsheetml/2014/revision}uid'
    functional_attrs=lambda el:{k:v for k,v in el.attrib.items() if k!=revision_uid}
    signature=lambda el:(functional_attrs(el),[(E.QName(c).localname,functional_attrs(c),c.text) for c in el.iterdescendants()])
    filters_preserved=all(new_filters.get(k) is not None and signature(v)==signature(new_filters[k]) for k,v in old_filters.items() if v is not None)
    controls={'fuentes_intactas':all(sha(x['ruta'])==x['sha256'] for x in cfg['entradas'].values()),
        'hojas_preservadas':list(base)==list(current),'formulas_constantes_preservadas':not changes,
        'caches_numericas_iguales':not differences,'sin_errores_formula':not errors,
        'celdas_con_contenido_centradas':not not_centered,'13_graficos_series_preservadas':len(charts(z))==13 and series_equal,
        '37_tablas_preservadas':len(tables(z))==len(tables(old))==37,
        'autofiltros_previos_preservados':filters_preserved,
        'filtro_complemento_ampliado':new_filters['VistaT1T2T3V19'] is not None and new_filters['VistaT1T2T3V19'].get('ref')=='A5:AT6379'}
    report={'clase':'C: lectura del XLSX guardado por Excel; no sustituye prueba de selectores',
        'estado':'PASS' if all(controls.values()) else 'FAIL','controles':controls,
        'formulas_numericas_comparadas':n,'por_hoja':by_sheet,'diferencias':differences,
        'contenido_alterado':changes,'celdas_vacias_omitidas_por_Excel':empty_omitted,'errores':errors,'no_centradas':not_centered,
        'tablas_sin_autofiltro_heredadas':[k for k,v in new_filters.items() if v is None and old_filters.get(k) is None],
        'serializacion_filtros':'Excel añadió uid del namespace revision; se comparan exactamente todos los demás atributos, rangos y descendientes.',
        'sha256_v25':sha(a.libro),'limite':'No certifica los 77 escenarios en la aplicación ni reproducción cruda integral.'}
    write(a.salida,report)
    print(json.dumps({'estado':report['estado'],'controles':controls,'comparadas':n,'diferencias':len(differences)}))
    assert all(controls.values())
if __name__=='__main__':main()

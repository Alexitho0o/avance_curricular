"""Completa cobertura temporal observable. Una fecha de edición nunca acredita un corte."""
import collections as C
import re
import sqlite3
from pathlib import Path
import openpyxl
from inventario import OUT,CLOUD,ROOT,load,dump,table
def periods(data):
    return ', '.join(map(str,sorted(data))) if data else 'E'
def profiles():
    result=load(OUT/'INVENTARIO.json');schema=load(OUT/'COBERTURA_FUENTES_LEIDAS.json');byfile=C.defaultdict(list)
    for s in schema:byfile[s['archivo']].append(s)
    for row in result['archivos']:
        f=CLOUD/row['ruta'];category=row['categoria'][:2];years=set();term=set();evidence=None
        if f.name in byfile:
            for s in byfile[f.name]:
                years.update(s['anios_observados']);term.update(s['periodos_2025'])
            evidence='Años observados en las hojas leídas (actividad, última matrícula o MU según tipo)'
        elif f.suffix.lower()=='.sqlite':
            with sqlite3.connect(f.as_uri()+'?mode=ro&immutable=1',uri=True) as db:
                for y,t in db.execute('select distinct anio,periodo from observaciones'):
                    years.add(str(y))
                    if str(y)=='2025':term.add(str(t))
            evidence='observaciones.anio y periodo; instantánea de diccionario'
        elif category=='07' and f.suffix=='.json':
            d=load(f)
            if isinstance(d,list):
                for z in d:
                    if not isinstance(z,dict):continue
                    y=str(z.get('anio_observado',z.get('ano',z.get('anio',''))))
                    if y.isdigit() and 1990<=int(y)<=2026:
                        years.add(y)
                        if y=='2025':term.add(str(z.get('periodo_nativo',z.get('periodo','E'))))
            evidence='Campos temporales explícitos de la capa o vista archivada'
        if f.suffix.lower()=='.xlsx':
            w=openpyxl.load_workbook(f,read_only=True,data_only=True)
            row['fecha_modificacion_libro_no_corte']=w.properties.modified.date().isoformat() if w.properties.modified else None
            if category in ('06','08','09','12') or (category=='02' and not years):
                # Sólo columnas que declaran año; distinguir años de referencia de edición.
                for ws in w.worksheets:
                    it=iter(ws.values);idx=None
                    for i,v in enumerate(it):
                        hdr=[str(a or '').strip().upper() for a in v]
                        ix=[i for i,t in enumerate(hdr) if t in {'AÑO','AÑO COHORTE','ANO','COHORTE','ANIO','ANIO_INFORMADO','AÑO ORIGEN','AÑO OBSERVADO','MC_CAT_PERIODO','CAT_PERIODO','ANOINGRESO'}]
                        if ix:idx=ix;break
                        if i>=7:break
                    if idx:
                        for v in it:
                            for i in idx:
                                if i>=len(v):continue
                                val=str(v[i]);match=re.fullmatch(r'(?:MAT_|OFE_)?((?:19|20)\d{2})(?:\.0)?',val)
                                if match and 1990<=int(match[1])<=2026:years.add(match[1])
                evidence='Años observados en columnas explícitas del libro; incluye años de ingreso si así se rotulan'
            w.close()
        if years:row['cobertura']=periods(years)+(' · períodos observados de 2025: '+periods(term) if term else '')+' · '+str(evidence)
        row['corte_estado']='E: cierre temporal no acreditado' if category in ('02','03','04') else 'No aplica a foto DA'
        if category=='04':row['corte_estado']='Actividad del año/período de la fila; estado académico del extracto'
        if f.name=='2025-2.xlsx':row['corte_estado']='Hoja1 contiene 52 matrículas de 2025-3; Detalle1 es selección de ingreso. No acredita cierre T2 completo'
        if row['categoria'] in ('RAÍZ',) and f.name.startswith('CATALOGO'):row['tipo']='Catálogo'
    dump(OUT/'INVENTARIO.json',result)
    return result
if __name__=='__main__':
    r=profiles();print('Perfiles temporales',len(r['archivos']))

"""Lectura de columnas necesarias. La salida intermedia sólo se escribe en el directorio privado."""
import collections as C
import csv
import os
import unicodedata
import openpyxl
from inventario import ROOT,CLOUD,OUT,P,load,dump,sha,H8
def txt(x):
    if x is None:return ''
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip()
def norm(x):return unicodedata.normalize('NFKD',txt(x).upper()).encode('ascii','ignore').decode().strip()
def key(x):
    s=txt(x).upper().replace('.','').replace(' ','').split('-')[0]
    return str(int(s)) if s.isdigit() else s
def full(doc,dv=None):
    val=txt(doc).strip().replace('.','').replace(' ','').upper()
    if '-' in val:
        body,check=val.rsplit('-',1)
    else:body,check=val,txt(dv).upper()
    return key(body)+'-'+check if body and check and check in '0123456789K' and len(check)==1 and key(body).isdigit() else ''
def main():
    os.umask(0o077);P.mkdir(exist_ok=True)
    inv=load(OUT/'INVENTARIO.json')['archivos']
    cfg=load(H8/'FUENTES_H008.json')['entradas']
    def prior(k):
        ref=cfg[k];assert sha(ref['ruta'])==ref['sha256'];return load(ref['ruta'])
    slots=prior('slots')
    c4={(r['fila_vista_origen'],str(r['periodo'])) for r in prior('posiciones_h007') if r['causa']=='FOTO_NO_COMPLETA_Y_SIN_CONTEXTO'}
    pad=[{'pos':s['fila_origen_foto'],'cohorte':int(s['anio_origen']),'persona':s['persona'],'body':key(s['documento_original']),'C4':(s['fila_origen_foto'],'2') in c4} for s in slots if int(s['anio_observado'])==2025 and str(s['periodo_nativo'])=='2' and int(s['anio_origen']) in (2024,2025)]
    assert C.Counter(s['cohorte'] for s in pad)=={2024:558,2025:1150} and sum(s['C4'] for s in pad)==733
    import sqlite3
    active=load(ROOT/'data/diccionario_sies_seguimiento/activo.json');v22=load(ROOT/active['descriptor']);assert sha(ROOT/active['descriptor'])==active['sha256']
    assert sha(v22['base_privada']['ruta'])==v22['base_privada']['sha256']
    db=sqlite3.connect(__import__('pathlib').Path(v22['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    d7=load(ROOT/'data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json');assert sha(d7['base_privada']['ruta'])==d7['base_privada']['sha256']
    db7=sqlite3.connect(__import__('pathlib').Path(d7['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True)
    hist={z['observacion_id'] for p, in db7.execute('select payload from observaciones') if not (z:=__import__('json').loads(p)).get('codigo_interno_adoptado')};db7.close()
    import json
    targets=[json.loads(p) for i,p in db.execute('select o.id,o.payload from observaciones o join asignaciones_v22 a on a.observacion_id=o.id where a.nivel_asignacion="E"') if i in hist];db.close();assert len(targets)==59
    bodies={s['body'] for s in pad};persons={r['persona'] for r in targets};targetplans={r['plan'] for r in targets}
    proms=[];da=[];mu=[];docplan=[];schema=[]
    def read_rows(rows,src,sheet,cut,kind):
        it=iter(rows);header=None;start=0
        for line in it:
            start+=1
            alias={'MM_N_DOCUMENTO':'N_DOC','MM_DV':'DV','MC_CAT_PERIODO':'ANIO_INFORMADO','MC_CODIGO_UNICO':'CODIGO_UNICO'}
            h=[alias.get(norm(v),norm(v)) for v in line]
            if any(k in h for k in ['N_DOC','RUT','NUMERO_DOCUMENTO','NUM_DOCUMENTO']) and any(k in h for k in ['CODCLI','ANOINGRESO','COD_CAR','CODIGO_UNICO','PLAN_DE_ESTUDIO','VIGENCIA']):
                header={k:h.index(k) for k in set(h) if k};break
            if start>=12:return
        if header is None:return
        isprom='PLAN_DE_ESTUDIO' in header and 'PERIODO' in header
        isda='RUT' in header and 'ANOINGRESO' in header
        ismu='N_DOC' in header and ('COD_CAR' in header or 'CODIGO_UNICO' in header) or 'CODIGO_UNICO' in header and ('NUMERO_DOCUMENTO' in header or 'NUM_DOCUMENTO' in header)
        if not (isprom or isda or ismu):return
        n=0;years=C.Counter();periods=C.Counter();latest=''
        for lineno,r in enumerate(it,start+1):
            def v(k):
                ix=header.get(k);return txt(r[ix]) if ix is not None and ix<len(r) else ''
            doc=v('RUT') or v('N_DOC') or v('NUMERO_DOCUMENTO') or v('NUM_DOCUMENTO')
            if not doc:continue
            n+=1;body=key(doc);ident=full(doc,v('DIG') or v('DV'))
            if isprom:
                y,term=v('ANO'),v('PERIODO');years[y]+=1;periods[y,term]+=1
                if y=='2025' and term=='2' and body in bodies:
                    proms.append([src,body,v('CODCLI'),v('CODCARR'),v('PLAN_DE_ESTUDIO'),norm(v('ESTADO_ACADEMICO')),v('ESTADO'),v('CONVALIDADO')])
                if ident in persons or v('PLAN_DE_ESTUDIO') in targetplans:
                    docplan.append([ident,v('CODCLI'),v('PLAN_DE_ESTUDIO'),v('CODCARR'),v('JORNADA'),y,term,src])
            elif isda:
                y,term=v('ANOMATRICULA'),v('PERIODOMATRICULA');years[y]+=1;periods[y,term]+=1
                date=v('FECHAMATRICULA')
                if date[:4].isdigit() and len(date)>=10:latest=max(latest,date[:10])
                if body in bodies or ident in persons or v('CODCARPR') in {r['carrera'] for r in targets}:
                    da.append([src,sheet,body,ident,v('CODCLI'),v('CODCARPR'),v('SEDE'),v('JORNADA'),v('ANOINGRESO'),v('PERIODOINGRESO'),y,term,norm(v('ESTADOACADEMICO')),norm(v('SITUACION'))])
            else:
                y=v('ANIO_INFORMADO') or cut
                if y.startswith('MAT_') and y[4:].isdigit():y=y[4:]
                years[y]+=1
                code=v('CODIGO_UNICO')
                if not code and all(v(k) for k in ['COD_SED','COD_CAR','JOR','VERSION']):
                    code='I162S'+v('COD_SED')+'C'+v('COD_CAR')+'J'+v('JOR')+'V'+v('VERSION')
                if ident and code and y and v('TIPO_DOC') in ('','R') and v('TIPO_DOCUMENTO') in ('','R'):mu.append([src,sheet,y,ident,code,kind])
        schema.append({'archivo':src,'hoja':sheet,'clase_contenido':'PROMEDIOS' if isprom else 'DA' if isda else 'MU','filas_con_documento':n,'anios_observados':sorted(k for k in years if k.isdigit() and 1990<=int(k)<=2026),'periodos_2025':{t:n for (y,t),n in periods.items() if y=='2025' and t in ('1','2','3','4','5')},'maxima_fecha_matricula_observada':latest or None,'columna_fecha_corte_o_extraccion':sorted(k for k in header if 'EXTRACCION' in k or 'FECHA_CORTE' in k)})
    trialfiles=[(CLOUD/r['ruta'],r['sha256']) for r in inv if r['categoria'][:2] in ('02','03','04') and r['ruta'].lower().endswith(('.xlsx','.csv'))]
    from pathlib import Path
    partial=next(Path.home().glob('Downloads/cierre/*T2_2025 2.xlsx'))
    trialfiles.append((partial,'ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3'))
    for p,h in trialfiles:
        assert sha(p)==h,p.name
        name=p.name
        year='2021' if name=='MAT_IP_CIISA_2021.xlsx' else '2024' if '2024' in name else '2025' if ('2025' in name or name in ('IPSS_Procesamiento.xlsx','2353.xlsx') or name.startswith('5809_')) else ''
        if p.suffix.lower()=='.xlsx':
            wb=openpyxl.load_workbook(p,read_only=True,data_only=True)
            for ws in wb.worksheets:
                kind='DOCUMENTAL' if (name.startswith('Descarga de lo cargado_08-05-2025') and ws.title.startswith('08-05-2025_22-26-22')) or (name=='Matrícula_Pregrado_2024.xlsx' and ws.title.startswith('08-05-2024_18-31-54')) or name in ('MAT_IP_CIISA_2021.xlsx','BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx') else 'CARGA_O_PREPARACION'
                read_rows(ws.values,name,ws.title,year,kind)
            wb.close()
        else:
            import io
            raw=p.read_bytes()
            try:content=raw.decode('utf-8-sig')
            except UnicodeDecodeError:content=raw.decode('latin1')
            rows=list(csv.reader(io.StringIO(content),delimiter=';'))
            if name.startswith('02-01-2025') and rows and 'TIPO_DOC' not in rows[0]:
                companion=p.with_name(p.stem.removesuffix('_F')+'.xlsx')
                assert sha(companion)==dict(trialfiles)[companion]
                book=openpyxl.load_workbook(companion,read_only=True,data_only=True)
                it=iter(book['1'].values);headers=next(it)[:32];assert headers[-1]=='VIG'
                cols=[headers.index(k) for k in ('N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION')]
                row_key=lambda r:tuple(txt(r[i]) for i in cols)
                verified={row_key(r) for r in it};book.close()
                assert all(len(r)==len(headers) and row_key(r) in verified for r in rows)
                rows.insert(0,headers)
            read_rows(rows,name,'CSV',year,'DOCUMENTAL' if name.startswith(('08-05-2024','5809_')) else 'CARGA_O_PREPARACION')
    dump(P/'indices.json',{'padrón':pad,'objetivos':targets,'prom':proms,'da':da,'mu':mu,'planes':docplan,'parcial':partial.name})
    dump(OUT/'COBERTURA_FUENTES_LEIDAS.json',schema)
    print('Lectura completa',len(schema),'hojas',len(proms),'registros PROMEDIOS T2/padrón antes de deduplicar')
if __name__=='__main__':main()

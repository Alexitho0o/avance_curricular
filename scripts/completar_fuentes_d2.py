#!/usr/bin/env python3
"""Inspecciona fuentes candidatas D2; preserva completo el catálogo académico leído."""
import csv,hashlib,io,json,shutil,sys
from collections import Counter
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.reconstruir_planes_umas import read_sheet
from scripts.fuentes_ensayo_enlace_conjunto import token,doc,sha
OUT=ROOT/'data/cierre_d2/20261016'
def main():
    f=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_4_20261015/fuentes.json').read_text())['sources']['planes']
    p=Path(f['path']);assert sha(p)==f['sha256']
    wb=openpyxl.load_workbook(p,read_only=True,data_only=True);s=wb[f['sheet']];rows=s.iter_rows(values_only=True);headers=list(next(rows));allrows=list(rows)
    catalog=[dict(zip(headers,r)) for r in allrows];cilog=[r for r in catalog if str(r['Codcarr']).strip()=='CILOG']
    dest=OUT/'fuentes'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest);assert sha(dest)==f['sha256']
    plans=sorted({str(r['CODPESTUD']).strip() for r in cilog})
    summary={'catalogo_planes':{'fuente':f,'copia_completa':str(dest.relative_to(ROOT)),'hoja':s.title,'filas_datos':len(allrows),'columnas':headers,'filas_cilog':len(cilog),'planes_cilog':plans,
      'fechas_vigencia_explicitamente_localizadas':[h for h in headers if any(t in h.lower() for t in ('fecha','vigencia','inicio','termino'))],'limite':'Listado de asignaturas y planes; no documento de apertura ni prueba de vigencia histórica por estudiante.'}}
    lookup=json.loads((OUT/'busqueda_fuentes.json').read_text());sies=next(Path(x['directorio']) for x in lookup['alcance'] if x['directorio'].endswith('SIES'))
    p=next(sies.glob('Publicados/*/2025 - 1207/4262*'));raw=p.read_bytes()
    try:text=raw.decode('utf-8-sig');encoding='utf-8-sig'
    except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1'
    rows=list(csv.DictReader(io.StringIO(text),delimiter=';'))
    summary['reporte_4262_2025']={'path':str(p),'sha256':sha(p),'columnas':list(rows[0]) if rows else [],'filas':len(rows),'lectura':'COMPLETA_EN_MEMORIA_SIN_EXPORTAR_PERSONAS','conclusion':'NO_CONTIENE_CODIGO_CARRERA_NI_PLAN; no permite atribuir matrícula a CILOG ni resolver versión.'}
    # Corte alternativo localizado: no se supone que el nombre 2025 acredite fecha de extracción.
    p=Path('/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx')
    fields=('RUT','CODCLI','CODCARPR','ANOINGRESO','ANOMATRICULA','SEDE','JORNADA')
    old,meta=read_sheet(p,'Hoja1',fields);new,_=read_sheet('/Users/alexi/Downloads/DATOSDEALUMNOS_12023.xlsx','Hoja1',fields)
    newidx={(doc(r['RUT']),token(r['CODCLI']),token(r['CODCARPR'])):r for r in new if doc(r['RUT'])}
    changes=Counter();n=0;matched=0
    for r in old:
        if token(r['CODCARPR'])!='CILOG':continue
        n+=1;k=(doc(r['RUT']),token(r['CODCLI']),token(r['CODCARPR']));q=newidx.get(k) if k[0] else None
        if q:
            matched+=1;changes[(token(r['ANOINGRESO']),token(q['ANOINGRESO']),token(r['ANOMATRICULA']),token(q['ANOMATRICULA']))]+=1
    summary['extracto_11248']={'path':str(p),'sha256':sha(p),'filas_leidas':len(old),'cilog_filas':n,'cilog_filas_coincidentes_identidad_expediente_carrera':matched,
      'transiciones_agregadas':[dict(zip(['ingreso_11248','ingreso_12023','matricula_11248','matricula_12023'],k),filas=v) for k,v in sorted(changes.items())],
      'corte_temporal':'NO_ACREDITADO_POR_NOMBRE_DE_ARCHIVO','limite':'Comparación de extractos, no historial certificado; no aporta por sí solo código SIES.'}
    wb.close();(OUT/'revision_fuentes_candidatas.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

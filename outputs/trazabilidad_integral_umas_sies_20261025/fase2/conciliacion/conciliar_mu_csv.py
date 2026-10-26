"""Conciliación agregada IPSS162 2022–2026; fuentes y asignaciones inmutables.

No distribuye matrícula para asignar identidad/versión. Los ceros estructurales
de la unión se identifican con banderas de presencia; las celdas fuente ausentes
permanecen vacías. Solo exporta agregados.
"""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import argparse,csv,datetime,hashlib,json,re,subprocess,unicodedata
import openpyxl

ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular')
MU=ROOT/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
OLD=ROOT/'procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv'
OM=OLD.with_name('TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json')
PAT=re.compile(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def val(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def integer(v):
    s=val(v);assert s, 'Campo numérico vacío'
    d=Decimal(s);assert d.is_finite() and d==int(d),'Valor no entero';return int(d)
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def source_csv():
    cloud=Path('/Users/alexi/Library/CloudStorage')
    r=next(p for p in cloud.iterdir() if p.name.startswith('OneDrive-InstitutoProfesionalSanSebasti'))
    p=next(p for p in (r/'0 BASES DE DATOS').iterdir() if unicodedata.normalize('NFC',p.name)=='MATRÍCULA')
    return p/'Matricula_2007_2026_WEB_10_07_2026.csv'
def export(p,rows):
    assert rows
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
def main():
    a=argparse.ArgumentParser();a.add_argument('--salida',type=Path,default=Path(__file__).parent)
    a.add_argument('--actualizar-auditoria',action='store_true',help='Regenera solo las salidas agregadas de esta auditoría; nunca las fuentes.')
    args=a.parse_args();out=args.salida
    out.mkdir(parents=True,exist_ok=True);assert args.actualizar_auditoria or not (out/'RESULTADOS.json').exists(),'Usar salida nueva'
    published=source_csv();sourcehash={str(MU):sha(MU),str(published):sha(published),str(OLD):sha(OLD),str(OM):sha(OM)}
    assert sourcehash[str(MU)]=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
    assert sourcehash[str(published)]=='4c630e05e07312ebd567ed77b0c26c5d0230380deea4fc89a6123b11b7aba154'
    oldmanifest=json.loads(OM.read_text());assert sourcehash[str(OLD)]==oldmanifest['salidas']['csv_sha256']
    git_before={'rama':git('branch','--show-current'),'HEAD':git('rev-parse','HEAD')}
    # Canon and rule pointer snapshots are verified; unrelated work is untouched.
    protected=[ROOT/'PROYECTO_IPSS.json',ROOT/'data/diccionario_sies_seguimiento/ACTIVO.json']
    protected={str(p):sha(p) for p in protected if p.exists()}
    pub={};csv_years=Counter();csv_rows=0;duplicates=[];headlen=0;selected_rows=0
    with published.open(encoding='latin-1',newline='') as f:
        reader=csv.DictReader(f,delimiter=';');headlen=len(reader.fieldnames)
        for rn,r in enumerate(reader,2):
            csv_rows+=1;csv_years[r['AÑO']]+=1
            if r['CÓDIGO DE INSTITUCIÓN']!='162' or r['AÑO'] not in {f'MAT_{y}' for y in range(2022,2027)}:continue
            assert None not in r and all(v is not None for v in r.values()),'Estructura CSV'
            selected_rows+=1;year=int(r['AÑO'][4:]);code=r['CÓDIGO CARRERA'];m=PAT.fullmatch(code);assert m and int(m.group(1))==162
            total=integer(r['TOTAL MATRÍCULA']);first=integer(r['TOTAL MATRÍCULA PRIMER AÑO']) if val(r['TOTAL MATRÍCULA PRIMER AÑO']) else None
            assert total>=0 and (first is None or 0<=first<=total)
            key=(year,code)
            if key in pub:duplicates.append({'anio':year,'codigo':code,'fila_csv':rn})
            pub[key]={'total':total,'primer_anio':first,'nombre':r['NOMBRE CARRERA'],'nivel':r['NIVEL GLOBAL'],'fila_csv':rn,'components':tuple(map(int,m.groups()))}
    assert not duplicates,'Llave pública año+código duplicada: no agregar silenciosamente'
    assert headlen==58
    mu=defaultdict(lambda:{'rows':0,'vig':Counter(),'people':set(),'p1':set(),'p12':set(),'incomplete':0,'firstrow':None,'lastrow':None})
    mu_years=Counter();doc_types=Counter();vig_values=Counter();annual_people=defaultdict(set);mu_rows=0
    wb=openpyxl.load_workbook(MU,read_only=True,data_only=True);ws=wb['BASE_RETENCION_MU'];it=iter(ws.values);heads=list(next(it))
    for rn,row in enumerate(it,2):
        if not any(v is not None for v in row):continue
        r=dict(zip(heads,row));year=integer(r['ANIO_INFORMADO']);assert year in range(2022,2027)
        vals=[integer(r[k]) for k in ('COD_SED','COD_CAR','JOR','VERSION')];assert all(v>0 for v in vals)
        code=f'I162S{vals[0]}C{vals[1]}J{vals[2]}V{vals[3]}';assert PAT.fullmatch(code)
        vig=val(r['VIG']);tipo=val(r['TIPO_DOC']).upper();doc=val(r['N_DOC']);dv=val(r['DV']).upper();identity=(tipo,doc,dv)
        # R requires its DV; P may legitimately retain blank DV. No reconstruction.
        complete=bool(tipo and doc and (dv or tipo!='R'))
        z=mu[(year,code)];z['rows']+=1;z['vig'][vig]+=1;z['incomplete']+=not complete
        z['firstrow']=rn if z['firstrow'] is None else z['firstrow'];z['lastrow']=rn
        if complete:
            z['people'].add(identity);annual_people[year].add(identity)
            if vig=='1':z['p1'].add(identity)
            if vig in ('1','2'):z['p12'].add(identity)
        mu_rows+=1;mu_years[year]+=1;doc_types[tipo]+=1;vig_values[vig]+=1
    wb.close();assert mu_rows==10200
    keys=sorted(set(pub)|set(mu));detail=[]
    for year,code in keys:
        p=pub.get((year,code));m=mu.get((year,code));comp=tuple(map(int,PAT.fullmatch(code).groups()))
        mu_n=m['rows'] if m else 0;v0=m['vig']['0'] if m else 0;v1=m['vig']['1'] if m else 0;v2=m['vig']['2'] if m else 0
        other=mu_n-v0-v1-v2;csv_n=p['total'] if p else 0;level=p['nivel'] if p else 'NIVEL_NO_ACREDITADO'
        assert mu_n==v0+v1+v2+other
        row={'ANIO':year,'CODIGO_COMPLETO':code,'COD_INST':comp[0],'COD_SED':comp[1],'COD_CAR':comp[2],'JOR':comp[3],'VERSION':comp[4],
          'CSV_PRESENTE':bool(p),'MU_PRESENTE':bool(m),'PRESENCIA':'AMBAS' if p and m else 'SOLO_CSV' if p else 'SOLO_MU',
          'NOMBRE_CARRERA_CSV':p['nombre'] if p else None,'NIVEL_GLOBAL_CSV':p['nivel'] if p else None,'ALCANCE':level,
          'CSV_TOTAL_MATRICULA':p['total'] if p else None,'CSV_PRIMER_ANIO':p['primer_anio'] if p else None,
          'MU_TOTAL_FILAS':mu_n if m else None,'MU_VIG0_FILAS':v0 if m else None,'MU_VIG1_FILAS':v1 if m else None,'MU_VIG2_FILAS':v2 if m else None,'MU_VIG_OTROS_FILAS':other if m else None,
          'MU_PERSONAS_TIPO_DOC_DV':len(m['people']) if m else None,'MU_PERSONAS_VIG1':len(m['p1']) if m else None,'MU_PERSONAS_VIG1_O_2':len(m['p12']) if m else None,
          'MU_IDENTIDAD_INCOMPLETA_FILAS':m['incomplete'] if m else None,'MU_EXCESO_FILAS_SOBRE_PERSONAS':mu_n-len(m['people']) if m else None,
          'DIF_CSV_MU_TOTAL_AMBAS':csv_n-mu_n if p and m else None,'DIF_CSV_VIG1_AMBAS':csv_n-v1 if p and m else None,'DIF_CSV_VIG1_O_2_AMBAS':csv_n-v1-v2 if p and m else None,
          'CSV_TOTAL_ESTRUCTURAL_UNION':csv_n,'MU_TOTAL_ESTRUCTURAL_UNION':mu_n,'MU_VIG1_ESTRUCTURAL_UNION':v1,'MU_VIG1_O_2_ESTRUCTURAL_UNION':v1+v2,
          'DIF_CSV_MU_TOTAL_UNION':csv_n-mu_n,'DIF_CSV_VIG1_UNION':csv_n-v1,'DIF_CSV_VIG1_O_2_UNION':csv_n-v1-v2,
          'CSV_FILA_ORIGEN':p['fila_csv'] if p else None,'MU_PRIMERA_FILA':m['firstrow'] if m else None,'MU_ULTIMA_FILA':m['lastrow'] if m else None,
          'CLASIFICACION':'B/C; E causa no acreditada',
          'OBSERVACION':'Postítulo visible, fuera del alcance pregrado declarado de BASE; no agregar a comparación pregrado.' if level=='Postítulo' else 'Solo MU: nivel y nombre no acreditados por el CSV de ese año.' if not p else 'Conteos observados; una igualdad agregada no acredita asignación individual ni causa de las diferencias.'}
        detail.append(row)
    assert len(detail)==198
    def summary(rows,year,level):
        s={'ANIO':year,'ALCANCE':level,'CODIGOS_UNION':len(rows),'AMBAS':sum(r['PRESENCIA']=='AMBAS' for r in rows),'SOLO_CSV':sum(r['PRESENCIA']=='SOLO_CSV' for r in rows),'SOLO_MU':sum(r['PRESENCIA']=='SOLO_MU' for r in rows),
           'CSV_TOTAL':sum(r['CSV_TOTAL_ESTRUCTURAL_UNION'] for r in rows),'CSV_PRIMER_ANIO_SUMA_OBSERVADA':sum(r['CSV_PRIMER_ANIO'] for r in rows if r['CSV_PRIMER_ANIO'] is not None),'CSV_PRIMER_ANIO_CELDAS_VACIAS_PRESENTES':sum(r['CSV_PRESENTE'] and r['CSV_PRIMER_ANIO'] is None for r in rows),
           'MU_TOTAL_FILAS':sum(r['MU_TOTAL_ESTRUCTURAL_UNION'] for r in rows),'MU_VIG0':sum(r['MU_VIG0_FILAS'] or 0 for r in rows),'MU_VIG1':sum(r['MU_VIG1_FILAS'] or 0 for r in rows),'MU_VIG2':sum(r['MU_VIG2_FILAS'] or 0 for r in rows),'MU_VIG_OTROS':sum(r['MU_VIG_OTROS_FILAS'] or 0 for r in rows),
           'MU_PERSONAS_DISTINTAS_EN_ALCANCE':len(set().union(*(mu[(year,r['CODIGO_COMPLETO'])]['people'] for r in rows if r['MU_PRESENTE']))),
           'MU_SUMA_PERSONAS_POR_CODIGO':sum(r['MU_PERSONAS_TIPO_DOC_DV'] or 0 for r in rows)}
        for label,col in [('TOTAL','DIF_CSV_MU_TOTAL_UNION'),('VIG1','DIF_CSV_VIG1_UNION'),('VIG1_O_2','DIF_CSV_VIG1_O_2_UNION')]:
            diffs=[r[col] for r in rows];both=[r for r in rows if r['PRESENCIA']=='AMBAS']
            s.update({f'COINCIDEN_{label}_AMBAS':sum(r[col]==0 for r in both),f'DIFIEREN_{label}_AMBAS':sum(r[col]!=0 for r in both),f'CODIGOS_DIFERENCIA_{label}_UNION':sum(x!=0 for x in diffs),f'CODIGOS_DIFERENCIA_CERO_{label}_UNION':sum(x==0 for x in diffs),f'DIF_{label}_NETA_UNION':sum(diffs),f'DIF_{label}_POSITIVAS_UNION':sum(x for x in diffs if x>0),f'DIF_{label}_NEGATIVAS_UNION':sum(x for x in diffs if x<0),f'DIF_{label}_ABSOLUTA_UNION':sum(abs(x) for x in diffs)})
        s['CLASIFICACION']='B/C; E causa pendiente';return s
    summaries=[]
    for year in range(2022,2027):
        rows=[r for r in detail if r['ANIO']==year];summaries.append(summary(rows,year,'TOTAL_UNION'))
        for level in sorted({r['ALCANCE'] for r in rows}):summaries.append(summary([r for r in rows if r['ALCANCE']==level],year,level))
    with OLD.open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
    oldmap={(integer(r['ANIO']),r['CODIGO_CARRERA_CSV']):r for r in old};assert len(oldmap)==len(old)==198
    mismatches=[]
    pairs={'TOTAL_MATRICULA_CSV':'CSV_TOTAL_ESTRUCTURAL_UNION','BASE_TOTAL_FILAS':'MU_TOTAL_ESTRUCTURAL_UNION','BASE_VIG1':'MU_VIG1_ESTRUCTURAL_UNION','DIFERENCIA_VS_TOTAL':'DIF_CSV_MU_TOTAL_UNION','DIFERENCIA_VS_VIG1':'DIF_CSV_VIG1_UNION'}
    for r in detail:
        o=oldmap[(r['ANIO'],r['CODIGO_COMPLETO'])]
        for oldcol,newcol in pairs.items():
            if integer(o[oldcol])!=r[newcol]:mismatches.append({'anio':r['ANIO'],'codigo':r['CODIGO_COMPLETO'],'campo':oldcol,'anterior':o[oldcol],'actual':r[newcol]})
    assert not mismatches,'Diferencias numéricas con puente existente'
    all_diffs=[r for r in detail if r['PRESENCIA']!='AMBAS' or any(r[c]!=0 for c in ('DIF_CSV_MU_TOTAL_UNION','DIF_CSV_VIG1_UNION','DIF_CSV_VIG1_O_2_UNION'))]
    totals=[x for x in summaries if x['ALCANCE']=='TOTAL_UNION']
    assert sum(x['MU_TOTAL_FILAS'] for x in totals)==mu_rows
    assert sum(x['CSV_TOTAL'] for x in totals)==sum(r['total'] for r in pub.values())
    assert all(x['MU_TOTAL_FILAS']==x['MU_VIG0']+x['MU_VIG1']+x['MU_VIG2']+x['MU_VIG_OTROS'] for x in summaries)
    assert {p:sha(p) for p in sourcehash}==sourcehash
    assert {p:sha(p) for p in protected}==protected
    assert git('rev-parse','HEAD')==git_before['HEAD'] and git('branch','--show-current')==git_before['rama']
    export(out/'DETALLE_CONCILIACION.csv',detail);export(out/'SOLO_DIFERENCIAS.csv',all_diffs);export(out/'RESUMEN_ANUAL.csv',summaries)
    result={'fase':'2/6','hitos':'2-3','fecha':datetime.datetime.now().astimezone().isoformat(),'clasificacion':'B/C; D alcance conservado; E causas no acreditadas','fuentes_sha256':sourcehash,'git':git_before,
      'metodo':{'llave':'ANIO_INFORMADO/AÑO + I162S{COD_SED}C{COD_CAR}J{JOR}V{VERSION}','regla':'Se lee VERSION individual existente, nunca se distribuyen totales para asignarla.','csv':'latin-1, delimitador ;. CP1252 estricto no decodifica todo el archivo.','identidad':'(TIPO_DOC,N_DOC,DV) observados como texto; R exige DV, P conserva DV vacío si corresponde. No inferencia ni normalización aproximada.','unidad':'Matrículas/filas por código; personas únicas se reportan separadas.','ausencias':'Fuente ausente=null; ceros solo en columnas explícitas ESTRUCTURAL_UNION con banderas de presencia. Primer año vacío conserva null; resumen suma valores observados y cuenta vacíos, sin tratarlos como cero confirmado.','alcance':'Pregrado, Postítulo y nivel no acreditado de soloMU separados. Primer año CSV no se compara con total matrícula MU.'},
      'qa':{'estado':'PASS_CON_LIMITES_DE_INTERPRETACION','csv_filas_datos':csv_rows,'csv_registros_incluyendo_encabezado':csv_rows+1,'csv_columnas':headlen,'csv_filas_seleccionadas':selected_rows,'csv_llaves_duplicadas':len(duplicates),'mu_filas':mu_rows,'mu_por_anio':dict(mu_years),'mu_tipos_documento':dict(doc_types),'mu_vig_valores':dict(vig_values),'mu_identidad_incompleta_filas':sum(r['MU_IDENTIDAD_INCOMPLETA_FILAS'] or 0 for r in detail),'mu_repeticion_persona_dentro_codigo':sum(r['MU_EXCESO_FILAS_SOBRE_PERSONAS'] or 0 for r in detail),'union_filas':len(detail),'columnas_numericas_legacy_comparadas':len(pairs),'celdas_comparadas_legacy':len(detail)*len(pairs),'diferencias_legacy':len(mismatches),'identificadores_exportados':False,'asignaciones_nuevas':0,'fuentes_hash_conservados':True,'canon_y_denominadores_modificados':False},
      'resumen_anual':summaries,'puente_anterior':{'hash':sourcehash[str(OLD)],'filas':198,'celdas_numericas_iguales':990,'interpretaciones_causales_no_adoptadas':['Igualdad al agrupar carrera no prueba reclasificación de jornada/versión individual.','Igualdad de una brecha con226 no prueba misma composición ni causa.','Coincidencia usando VIG0 en2025 no acredita razón de inclusión ni cambia reglas.']},
      'pendientes':['La conciliación cuantifica diferencias, no adjudica causas ni identidad/versiones.','SoloMU carece de nivel acreditado por el CSV del mismo año.','Las tasas de retención y denominadores permanecen fuera del alcance.','No se selecciona un filtro VIG para hacer coincidir la publicación.']}
    (out/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# Fase 2/6 · Hitos 2-3 — Conciliación agregada anual','','B/C — Unión por año+código SIES completo, 198 filas. Se leen componentes individuales ya existentes en MU; no se asignan versiones con totales. Se reproducen 990/990 celdas numéricas del puente anterior. Sus explicaciones causales no se adoptan.','','| Año | Códigos | CSV total | CSV primer año | MU filas | VIG0 | VIG1 | VIG2 | CSV−MU | CSV−VIG1 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for s in totals:lines.append('| '+' | '.join(str(s[k]) for k in ('ANIO','CODIGOS_UNION','CSV_TOTAL','CSV_PRIMER_ANIO_SUMA_OBSERVADA','MU_TOTAL_FILAS','MU_VIG0','MU_VIG1','MU_VIG2','DIF_TOTAL_NETA_UNION','DIF_VIG1_NETA_UNION'))+' |')
    lines+=['','B/C — La tabla anterior conserva todos los niveles. Primer año es suma de valores observados; sus celdas vacías permanecen vacías y se contabilizan en el resumen, sin tratarlas como ceros confirmados. El archivo tiene 280.160 filas de datos y 280.161 registros incluyendo encabezado; 58 columnas. Lectura completa Latin-1; CP1252 estricto no admite todos sus bytes.','','## Pregrado según el CSV del mismo año','','| Año | Códigos | CSV | MU filas | MU VIG1 | Códigos con diferencia VIG1 | Neto | Positivas | Negativas | Absoluta |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for s in summaries:
        if s['ALCANCE']=='Pregrado':lines.append('| '+' | '.join(str(s[k]) for k in ('ANIO','CODIGOS_UNION','CSV_TOTAL','MU_TOTAL_FILAS','MU_VIG1','CODIGOS_DIFERENCIA_VIG1_UNION','DIF_VIG1_NETA_UNION','DIF_VIG1_POSITIVAS_UNION','DIF_VIG1_NEGATIVAS_UNION','DIF_VIG1_ABSOLUTA_UNION'))+' |')
    lines+=['','B/C/E — En 2023 el neto pregrado es 0, pero dos códigos difieren (+1 y −1): no son todos concordantes. En 2026 son 48 códigos pregrado con diferencia: 46 presentes en ambas fuentes y 2 solo en CSV; neto 226 y diferencia absoluta 230. Los 54 de Postítulo están separados, fuera del alcance de BASE. Los 6 códigos solo MU (2 matrículas en 2022 y 6 en 2024) conservan nivel no acreditado por el CSV; no se clasifican por semejanza.','','C — DETALLE_CONCILIACION.csv conserva campos fuente vacíos cuando un código no existe en una fuente. Las diferencias de unión usan ceros estructurales explícitos, no valores atribuidos a una celda ausente. RESUMEN_ANUAL.csv separa Pregrado, Postítulo y NIVEL_NO_ACREDITADO; presenta diferencias netas, positivas, negativas y absolutas, coincidencias y exclusivos.','','B/C — Identidad se cuenta como TIPO_DOC+N_DOC+DV disponible; las personas únicas por código y por año se presentan separadas de las matrículas. No se exporta ninguna identidad.','','E — Coincidir al sumar carreras no acredita redistribuciones de versión/jornada ni justifica corregir personas. La causa de cada diferencia sigue pendiente salvo evidencia específica, que este ejercicio no produce. Primer año CSV es una variable separada del total matrícula. Ninguna tasa de retención fue recalculada.','','## Fuentes']
    for p,h in sourcehash.items():lines+=[f'- B: `{p}` — SHA-256 `{h}`.']
    lines+=['','C — Reproducción: ejecutar conciliar_mu_csv.py con --salida apuntando a una carpeta nueva. Fuentes, edición activa, rama y HEAD verificados sin cambios. Sin commit/push.']
    (out/'INFORME.md').write_text('\n'.join(lines)+'\n')
    (out/'MANIFEST.json').write_text(json.dumps({'clasificacion':'C','entradas_sha256':sourcehash,'salidas_sha256':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='MANIFEST.json'},'fuentes_preservadas':True,'datos_individuales_exportados':False,'git':git_before},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'estado':result['qa']['estado'],'union':len(detail),'diferencias_legacy':len(mismatches),'resumen_total':totals,'salida':str(out)},ensure_ascii=False))
if __name__=='__main__':main()

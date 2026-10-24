#!/usr/bin/env python3
"""Prepara serie anual, escenario 2027 y columnas pendientes sin asignar códigos."""
import csv, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/resumen_oferta_2027/20261016'
def load(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    BASE.mkdir(parents=True,exist_ok=True)
    history_path=ROOT/'data/reglas_negocio/20261015/fuentes/Oferta_Academica_2010_al_2026_SIES_12_01_2026_WEB_E.csv.gz'
    with gzip.open(history_path,'rt',encoding='latin-1',newline='') as f:
        allrows=csv.DictReader(f,delimiter=';')
        hist=[(i,r) for i,r in enumerate(allrows,2) if r['Código IES']=='162']
    snapshot=BASE/'fuentes/oferta_2027_dimensiones.json'
    retained=json.loads(snapshot.read_text());future=retained['filas']
    report_sha=retained['fuente_original_sha256']
    assert report_sha=='4edfefaabf449b35163fa090ecac39649ecaf6aab10bbe3a4ef7e83a244f8e62'
    h3=load('data/versiones_historicas_sies_umas/fase_3_20261015/historia_codigos.json')
    expected={(x['codigo_unico'],a) for x in h3 for a in x['anios_oferta_observada']}
    actual={(r['Código Único'],int(r['Año'].replace('OFE_',''))) for _,r in hist}
    assert actual==expected and len(actual)==len(hist)==747
    annual=defaultdict(set);first={};detail=[]
    for rownum,r in hist:
        y=int(r['Año'].replace('OFE_',''));code=r['Código Único'];annual[y].add(code);first[code]=min(first.get(code,y),y)
        detail.append([y,code,code,'HISTORICO_PUBLICADO',r['Nombre Carrera'],r['Nivel Global'],r['Tipo Carrera'],r['Modalidad'],r['Jornada'],r['Código Sede'],r['Versión'],r['Duración Total'],r['Vigencia'],None,None,None,None,None,f'CSV nacional, fila {rownum}'])
    old=annual[2026];seen=set().union(*annual.values());prepares=[];futurekeys=set()
    modality={'1':'Presencial','2':'Semipresencial','3':'No presencial'}
    jornada={'1':'Diurna','2':'Vespertina','3':'Semipresencial','4':'A distancia','5':'Otra'}
    types={'1':'Plan Regular','3':'Plan Regular de Continuidad'}
    for i,r in enumerate(future,2):
        code=f"I{r['CODIGO_IES_NUM']}S{r['COD_SEDE']}C{r['COD_CARRERA']}J{r['COD_JORNADA']}V{r['VERSION']}"
        assert code not in futurekeys;futurekeys.add(code)
        level={'1':'Pregrado','3':'Postítulo'}[r['COD_NIVEL_GLOBAL']]
        movement='CONTINUA_DESDE_2026' if code in old else 'REAPARECE' if code in seen else 'NUEVA_CLAVE_ESPERADA_2027'
        detail.append([2027,code,None,'ESPERADO_NO_CONFIRMADO',r['NOMBRE_CARRERA'],level,types.get(r['COD_TIPO_PLAN_CARRERA'],r['COD_TIPO_PLAN_CARRERA']),modality[r['MODALIDAD']],jornada[r['COD_JORNADA']],r['COD_SEDE'],r['VERSION'],r['DURACION_TOTAL'],r['VIGENCIA_CARRERA'],None,None,None,None,None,f'6047, fila {i}; clave compuesta provisional'])
        prepares.append([f'O27-{i-1:03}',r['NOMBRE_CARRERA'],level,r['NOMBRE_SEDE'],r['COD_SEDE'],jornada[r['COD_JORNADA']],r['COD_JORNADA'],modality[r['MODALIDAD']],r['MODALIDAD'],types.get(r['COD_TIPO_PLAN_CARRERA'],r['COD_TIPO_PLAN_CARRERA']),r['DURACION_TOTAL'],r['REGIMEN'],r['DURACION_REGIMEN'],r['COD_CARRERA'],r['VERSION'],code,None,'PENDIENTE_CONFIRMACION_SIES_2027',movement,None,None,None,None,'PENDIENTE_VINCULO_Y_VIGENCIA',f'6047, fila {i}'])
    annual[2027]=futurekeys
    previous=None;ever=set();metrics=[]
    for y in range(2007,2028):
        if y<2010:metrics.append([y,None,None,None,None,None,None,'SIN_COBERTURA_OFERTA']);continue
        s=annual[y];new=len(s-ever) if y>2010 else None
        entered=len(s-previous) if previous is not None else None
        left=len(previous-s) if previous is not None else None
        delta=len(s)-len(previous) if previous is not None else None
        metrics.append([y,len(s),new,entered,left,delta,delta/len(previous) if previous else None,'ESPERADO_NO_CONFIRMADO' if y==2027 else 'BASE_OBSERVADA' if y==2010 else 'HISTORICO_PUBLICADO'])
        for r in detail:
            if r[0]==y:
                r[13]=int(y>2010 and r[1] not in ever)
                r[14]=int(previous is not None and r[1] not in previous)
                r[15]=min(first.get(r[1],2027),y)
                r[16]=int(r[1] not in annual.get(y+1,set())) if y<2027 else None
                r[17]=int(y==2010)
        ever|=s;previous=s
    coverage=load('data/catalogos_sies/auditorias/20261016_12023_p1/cobertura.json')
    umas=[]
    for i,r in enumerate(coverage['dimensiones'],1):
        umas.append([f'U27-{i:03}',r['CODCARPR'],r['NOMBRE_L'],r['SEDE'],r['JORNADA'],2027,1,r['registros'],r['ESTADO_CODIGO_SIES'],r['CANDIDATOS_SIES'],None,None,None,None,None,'PENDIENTE_PLAN_Y_CODIGO_CONFIRMADO',None])
    source=ROOT/'outputs/diccionario_d4_20261016/DICCIONARIO_CRUCE_SIES_UMAS_2007_2026_D4.xlsx'
    package={'source':str(source),'source_sha256':sha(source),'output':str(ROOT/'outputs/diccionario_ejecutivo_2027_20261016/DICCIONARIO_SIES_UMAS_RESUMEN_2027.xlsx'),
      'metrics':metrics,'historical_plans':236,'umas_programs':len({r['CODCARPR'] for r in coverage['dimensiones']}),'umas_dimensions':len(umas),'umas_records':coverage['registros'],
      'sheets':[
       {'name':'Serie oferta','headers':['Año','Clave oferta / provisional 2027','Código SIES publicado histórico','Estado fuente','Nombre literal oferta','Nivel','Tipo de plan','Modalidad','Jornada','Sede','Versión SIES / propuesta','Duración total · semestres','Vigencia literal fuente','Primera aparición tras base 2010','Entrada respecto año anterior','Primer año observado / esperado','Ausente al año siguiente','Pertenece base 2010','Localizador'], 'rows':sorted(detail,key=lambda x:(x[0],x[1])), 'widths':[12,28,29,31,52,20,37,24,24,12,22,23,43,24,24,24,24,21,58], 'note':'Historia 2010–2026: CSV nacional completo, institución 162. 2027: escenario 6047; códigos definitivos pendientes.'},
       {'name':'Preparación oferta 2027','headers':['ID oferta','Nombre literal oferta','Nivel','Nombre sede','Sede propuesta','Jornada','Jornada propuesta','Modalidad','Modalidad propuesta','Tipo de plan','Duración total · semestres','Régimen fuente','Duración régimen','Carrera SIES propuesta','Versión SIES propuesta','Clave compuesta provisional','Código Único confirmado 2027','Estado código','Movimiento esperado','CODCARPR vinculado','CODPESTUD confirmado','Versión malla UMAS','Inicio vigencia malla','Estado plan','Fuente'], 'rows':prepares,'widths':[16,52,20,40,18,24,20,24,22,37,24,20,22,23,23,29,31,48,40,25,26,24,25,42,48],'note':'161 combinaciones esperadas, incluidos 21 diplomados. Columnas amarillas listas para respaldo futuro; no asignar por semejanza.'},
       {'name':'Preparación UMAS 2027','headers':['ID dimensión','CODCARPR','Nombre interno UMAS','Sede UMAS','Jornada UMAS','Año matrícula','Período matrícula','Registros del extracto','Estado catálogo previo','Candidatos catálogo previo','Código SIES confirmado 2027','CODPESTUD confirmado 2027','Versión malla UMAS','Inicio vigencia malla','Fin vigencia malla','Estado preparación','Respaldo de confirmación'], 'rows':umas, 'widths':[18,20,54,16,18,20,20,24,31,36,31,32,25,25,25,47,60],'note':'12023, Hoja1: ANOMATRICULA=2027 / PERIODOMATRICULA=1. No contiene CODPESTUD; dimensiones no equivalen a mallas.'}]
    }
    BASE.joinpath('libro.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
    BASE.joinpath('fuentes.json').write_text(json.dumps({'csv_2027_sha256':report_sha,'csv_2027_snapshot':str(snapshot.relative_to(ROOT)),'csv_2027_snapshot_integral':False,'csv_2027_antecedente':'data/catalogos_sies/2027/5910_20260907_6047_20261013/EVIDENCIA_DIMENSIONES.json','archivos_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [history_path,snapshot,source,ROOT/'data/versiones_historicas_sies_umas/fase_3_20261015/historia_codigos.json',ROOT/'data/catalogos_sies/auditorias/20261016_12023_p1/cobertura.json']},'confirmaciones_2027':0,'historia_csv_coincide_claves_h3':True},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'serie':metrics,'preparacion_oferta':len(prepares),'dimensiones_umas':len(umas),'programas_umas':package['umas_programs'],'registros_umas':package['umas_records']}))
if __name__=='__main__':main()

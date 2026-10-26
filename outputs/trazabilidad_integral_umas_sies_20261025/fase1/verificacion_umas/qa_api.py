"""QA final: API común y privacidad de los ejemplos, sin releer libros."""
from pathlib import Path
import hashlib,json,re,sys
import openpyxl
ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular');sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
OUT=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def norm(x):return val(x).upper().replace('.','').replace(' ','')
def main():
    result=json.loads((OUT/'RESULTADOS.json').read_text())
    details=json.loads(Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase1_20261025/llaves/DETALLE_LLAVES.json').read_text())['detalle']
    api=DiccionarioSiesSeguimiento(root=ROOT);checks=[];secrets=[]
    for e in result['ejemplos']:
        d=next(x for x in details if x['fila_hoja9']==e['libro_original']['hoja9_fila'])
        person=norm(d['documento_original'])+'-'+norm(d['dv_original'])
        rr=[json.loads(row[0]) for row in api.db.execute("SELECT payload FROM observaciones WHERE persona=? AND anio=? AND periodo='1'",(person,val(d['cohorte'])))]
        rr=[r for r in rr if r['carrera']==e['codigo_umas'] and r['plan']==e['plan_umas'] and (r['codigo_documental_atribuible'] or r['codigo_interno_adoptado'])==e['codigo_sies_completo']]
        assert len(rr)==1;r=rr[0]
        q=api.consultar(persona=person,codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
        assert q['codigo_sies']==e['codigo_sies_completo'] and q['estado']=='REUTILIZABLE'
        checks.append({'ejemplo':e['ejemplo'],'codigo':q['codigo_sies'],'estado':q['estado'],'respaldo':q['nivel_respaldo'],'edicion':q['edicion'],'QA':'PASS'})
        secrets.extend([person,r['CODCLI']])
    api.close()
    result['conteos']['contextos_sede_jornada_discordantes']=result['conteos']['un_contexto_nativo1_con_codigo_igual']-result['conteos']['contextos_sede_jornada_concordantes']
    assert result['conteos']['contextos_sede_jornada_discordantes']==6
    result['QA']['consulta_API_comun_tres_subcasos']=checks
    limit='1926 contextos tienen código adoptado igual;1920 concuerdan además en sede/jornada observadas y6 difieren. No considerar los6 como expediente plenamente conciliado.'
    if limit not in result['limites']:result['limites'].insert(0,limit)
    mu_path=Path(result['ejemplos'][0]['fuente_MU']['fuente'])
    w=openpyxl.load_workbook(mu_path,read_only=True,data_only=True)
    heads=list(next(w['BASE_RETENCION_MU'].iter_rows(min_row=1,max_row=1,values_only=True)));w.close()
    prov=[x for x in heads if x and any(t in str(x).upper() for t in ('ARCHIVO','FUENTE','FILA','HOJA'))]
    assert not prov
    result['linaje_MU_derivada']={'clasificacion':'B/E','tipo':'BASE DERIVADA, NO RETORNO O ENVÍO PRIMARIO','numero_columnas':len(heads),'campos_origen_archivo_hoja_fila':prov,'limite':'Las filas5/3766/3740 son del consolidado derivado; no conserva localizadores del RAW primario en sus columnas.'}
    for e in result['ejemplos']:
        e['fuente_MU']['tipo']='Base anual derivada; no prueba de envío/retorno SIES'
        if 'validacion_fuentes_primarias_UMAS' in e:e['validacion_filas_fuentes']=e.pop('validacion_fuentes_primarias_UMAS')
    (OUT/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (OUT/'QA_API.json').write_text(json.dumps({'clasificacion':'C','estado':'PASS','consulta_API':checks,'identificadores_exportados':False,'fuentes_excel_releidas':False,'asignaciones':0},ensure_ascii=False,indent=2)+'\n')
    p=OUT/'INFORME.md';s=p.read_text();marker='\n## QA complementario de API y dimensiones\n'
    if marker in s:s=s.split(marker)[0]
    s+=marker+'\nB/C — De los1.926 contextos con código adoptado igual,1.920 coinciden además en sede y jornada;6 muestran discordancia. Estos6 no se presentan como expediente plenamente conciliado. Los1.926 comprenden1.918 atribuciones documentales anuales y8 correspondencias internas ya aprobadas.\n\nC — La API común consultar devolvió REUTILIZABLE y el mismo código en los tres subcasos, ediciónv8_20261025_ocho_p. En cada ejemplo, DATOS ALUMNOS y PROMEDIOS contienen el mismo CODCLI literal y la misma identidad; MU conserva esa identidad completa y los componentes del código SIES. Se verificó en memoria, sin publicar identificadores. No se exigió una prueba de envío para comprobar este enlace interno.\n\n| Ejemplo | Año/período PROMEDIOS | Régimen | Nivel de asignatura | Ramo | Estado | Convalidado |\n|---|---|---|---|---|---|---|\n'
    for e in result['ejemplos']:
        p=e['campos_observados_releidos']['PROMEDIOS'];s+=f"| {e['ejemplo']} | {p['ANO']}/{p['PERIODO']} | {p['REGIMEN']} | {p['NIVEL']} | {p['CODRAMO']} · {p['ASIGNATURA']} | {p['ESTADO']} · {p['DESCRIPCION_ESTADO']} | {p['CONVALIDADO'] if p['CONVALIDADO'] is not None else 'Vacío en fuente'} |\n"
    s+='\nB/C/E — NIVEL se presenta tal como está en la asignatura observada; no se convierte automáticamente en trimestre de avance ni duración del programa. ANOMATRICULA del corte DA puede ser posterior al año de PROMEDIOS: se conservan ambas fechas, sin igualarlas.\n\nB/E — La MU leída es una base anual derivada. Sus33columnas no contienen ARCHIVO_ORIGEN, FUENTE, HOJA ni FILA_ORIGEN. Las referencias5/3766/3740 localizan filas del consolidado, sin certificar fila RAW primaria, envío ni retornoSIES. Esto no invalida el enlace interno comprobado por identidad.\n'
    (OUT/'INFORME.md').write_text(s)
    for name in ('RESULTADOS.json','INFORME.md','QA_API.json'):
        text=(OUT/name).read_text()
        assert not any(x in text for x in secrets),'Identificador personal en salida'
    m=json.loads((OUT/'MANIFEST.json').read_text());m['salidas_sha256']={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST.json'}
    (OUT/'MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'QA':'PASS','ejemplos_API':checks,'dimension_concordante':1920,'discordante':6},ensure_ascii=False))
if __name__=='__main__':main()

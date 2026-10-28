"""QA y lista exacta de informes: no prepara staging, commit ni publicación."""
import collections,hashlib,json,re,sqlite3,subprocess
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def txt(x):
    if x is None:return ''
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip().upper()
def doc(n,dv):
    n=txt(n).replace('.','').replace(' ','');v=txt(dv)
    return n+'-'+v if v else n
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
assert head=='a7330f4a3b306b899f929bce7292100a745386fd' and branch=='feature/ire-2026'
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
baseline=json.loads(subprocess.check_output(['git','show',head+':outputs/matriz_cuadratura_totales_20261028/MATRIZ_CUADRATURA_TOTALES_2022_2026.json'],cwd=ROOT,text=True))
matrix=read(OUT/'MATRIZ_CUADRATURA_TOTALES_2022_2026.json')
assert baseline['matriz']==matrix['matriz'],'Cambió el núcleo de la matriz'
assert baseline['fuentes']==matrix['fuentes'],'Cambió una fuente de la matriz'
audit=read(OUT/'DICTAMEN_LIBROS_Y_CARGAS_MU2026.json')
pes=read(OUT/'BUSQUEDA_DESCARGA_PES_MU2026.json');ac=read(OUT/'BUSQUEDA_PRECARGA_AC2027.json')
assert not pes['metodo_mu2026_ejecutado'] and not ac['metodo_mu2026_ejecutado']
assert not any(s['errores'] for s in pes['ambitos']+ac['ambitos'])
assert not any(s['coincidencias'] for s in ac['ambitos']+ac['catalogos'])
assert ac['rotulo_vigente']==matrix['brecha_mu2026']['precarga_ac2027_disponibilidad']['resultado']
assert audit['prueba_cargas_acumulativas']['estado']=='E_NO_EJECUTADA'
for b in audit['libros']:assert sha(b['ruta'])==b['sha256']
assert audit['libros'][0]['06_DETALLE_TOTAL']['identica_multiconjunto_rut_codigo_vig']
assert audit['libros'][0]['Hoja1']['coincide_con_H001_V24_por_cohorte_documento_retencion']
assert audit['libros'][1]['continuidades_ya_en_vigentes_expedientes']==400
for report,ref in matrix['informes_busqueda_y_dictamen'].items():assert sha(OUT/(report+'.json'))==ref['sha256']
for cat in pes['catalogos']+ac['catalogos']:assert sha(cat['ruta'])==cat['sha256']
sql=sqlite3.connect(':memory:');sql.execute('CREATE TABLE mu(doc,code,vig)');sql.execute('CREATE TABLE april(doc,family)')
base=audit['fuente_base_mu'];assert sha(base['ruta'])==base['sha256']
tokens=set();book=openpyxl.load_workbook(base['ruta'],read_only=True,data_only=True)
it=book['BASE_RETENCION_MU'].iter_rows(values_only=True);h=next(it)
for row in it:
    r=dict(zip(h,row));n=txt(r['N_DOC']);d=doc(n,r['DV']);tokens.update((n,d))
    if txt(r['ANIO_INFORMADO'])!='2026':continue
    c='I162S{}C{}J{}V{}'.format(*(txt(r[k]) for k in ('COD_SED','COD_CAR','JOR','VERSION')))
    sql.execute('INSERT INTO mu VALUES(?,?,?)',(d,c,txt(r['VIG'])))
book.close()
private=read(audit['detalle_privado']['ruta']);assert sha(audit['detalle_privado']['ruta'])==audit['detalle_privado']['sha256']
for r in private['abril']:
    tokens.update((r['documento'],r['documento'].split('-')[0],r['codcli']))
    for fam in r['familias']:sql.execute('INSERT INTO april VALUES(?,?)',(r['documento'],fam))
sql_counts=dict(sql.execute("SELECT code,COUNT(*) FROM mu WHERE vig='0' AND EXISTS(SELECT 1 FROM april WHERE april.doc=mu.doc AND april.family=substr(mu.code,1,instr(mu.code,'V')-1)) GROUP BY code"))
for r in audit['comparacion_abril_48_codigos']:
    assert sql_counts.get(r['codigo_sies'],0)==r['nuestras_vig0_vigentes_abril_misma_familia']
    assert r['brecha_publicado_menos_vig1']==r['publicacion_sies']-r['vig1_nuestra']
    assert r['residuo_escenario_agregar_esos_vig0']==r['brecha_publicado_menos_vig1']-r['nuestras_vig0_vigentes_abril_misma_familia']
check=audit['comprobacion_abril']
assert sum(sql_counts.values())==check['vig0_nuestra_con_vigente_abril_familia_todos_codigos']
assert sum(r['nuestras_vig0_vigentes_abril_misma_familia'] for r in audit['comparacion_abril_48_codigos'])==check['vig0_nuestra_con_vigente_abril_familia_en_48']
assert check['suma_brecha']==226 and check['residuo_neto_escenario']==226-check['vig0_nuestra_con_vigente_abril_familia_en_48']
sql.execute('CREATE TABLE gaps(code,diff)');sql.execute('CREATE TABLE candidates(code,n)')
sql.executemany('INSERT INTO candidates VALUES(?,?)',list(sql_counts.items()))
sql.executemany('INSERT INTO gaps VALUES(?,?)',[(r['codigo_sies'],r['brecha_publicado_menos_vig1']) for r in audit['comparacion_abril_48_codigos']])
sql_cover=sql.execute('''SELECT
SUM(CASE WHEN diff>0 THEN diff ELSE 0 END),
SUM(CASE WHEN diff>0 THEN MIN(diff,COALESCE(n,0)) ELSE 0 END),
SUM(CASE WHEN diff>0 THEN MAX(diff-COALESCE(n,0),0) ELSE 0 END),
SUM(CASE WHEN diff>0 AND COALESCE(n,0)>=diff THEN 1 ELSE 0 END),
SUM(CASE WHEN diff>0 AND COALESCE(n,0)<diff THEN 1 ELSE 0 END),
SUM(CASE WHEN diff<0 THEN 1 ELSE 0 END),
SUM(CASE WHEN diff<0 THEN diff ELSE 0 END),
SUM(CASE WHEN COALESCE(n,0)>=diff THEN 1 ELSE 0 END),
SUM(CASE WHEN diff>0 AND COALESCE(n,0)=diff THEN 1 ELSE 0 END)
FROM gaps LEFT JOIN candidates USING(code)''').fetchone()
c=check['compatibilidad_por_codigo']
assert sql_cover==(228,193,35,30,16,2,-2,32,4)
assert (c['brecha_positiva'],c['cubrible_total'],c['sin_cubrir_total'],c['codigos_positivos_cubiertos_totalmente'],c['codigos_positivos_insuficientes'],c['codigos_negativos'],c['brecha_negativa'],c['codigos_candidatas_mayor_igual_brecha_incluye_negativos'],c['codigos_positivos_exactos'])==sql_cover
assert c['cubrible_en_positivos_cubiertos_totalmente']==139 and c['cubrible_en_insuficientes']==54
assert sum(r['sin_cubrir'] for r in c['no_cubiertas_por_codigo'])==35
assert len(c['no_cubiertas_por_codigo'])==16
assert c['compatibilidad_porcentaje']==100*193/228
assert matrix['brecha_mu2026']['compatibilidad_abf_abril']==c
uncovered={r['codigo_sies']:r for r in c['no_cubiertas_por_codigo']}
assert uncovered['I162S2C87J4V1']['solo_publicado_sin_mu'] and uncovered['I162S2C87J4V1']['sin_cubrir']==5
assert uncovered['I162S2C77J1V1']['solo_publicado_sin_mu'] and uncovered['I162S2C77J1V1']['sin_cubrir']==1
plan=read(OUT/'PREPARACION_CARGAS_ACUMULATIVAS_MU2026.json')
assert plan['estado']=='PREPARADO_NO_EJECUTADO' and not plan['ejecucion_con_archivos_reales']
assert plan['estado_reconstruido'] is None and plan['vig1_resultante'] is None
assert sha(plan['manual']['ruta'])==plan['manual']['sha256']==audit['prueba_cargas_acumulativas']['manual']['sha256']
assert plan['llaves_candidatas'][0]['campos']==['TIPO_DOC','N_DOC','DV','CODIGO_UNICO']
assert plan['llaves_candidatas'][1]['campos']==['TIPO_DOC','N_DOC','DV','COD_CAR']
assert plan['antecedente_llaves_equivalentes']['llave_2_original']==['TIPO_DOC','N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION']
assert plan['hipotesis_sensibilidad']['resultado'] is None
assert audit['prueba_cargas_acumulativas']['preparacion_sensibilidad']['llave_2']==plan['llaves_candidatas'][1]['campos']
# Equivalencia histórica código/componentes y diferencia estructural de la
# nueva llave gruesa. No se simula la historia ni se procesan cargas reales.
components=[]
for row in audit['comparacion_abril_48_codigos']:
    code=row['codigo_sies'];parts=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)',code).groups()
    assert 'I162S{}C{}J{}V{}'.format(*parts)==code
    components.append(parts)
assert len(set(components))==48
coarse=collections.Counter(parts[1] for parts in components)
assert len(coarse)<48 and any(n>1 for n in coarse.values())
sql.close()
files=['MATRIZ_CUADRATURA_TOTALES_2022_2026.json','MATRIZ_CUADRATURA_TOTALES_2022_2026.md','QA.json','construir_matriz.py','BUSQUEDA_DESCARGA_PES_MU2026.json','BUSQUEDA_DESCARGA_PES_MU2026.md','buscar_descarga_pes_mu2026.py','BUSQUEDA_PRECARGA_AC2027.json','BUSQUEDA_PRECARGA_AC2027.md','buscar_precarga_ac2027.py','DICTAMEN_LIBROS_Y_CARGAS_MU2026.json','DICTAMEN_LIBROS_Y_CARGAS_MU2026.md','auditar_libros_y_cargas_mu2026.py','cerrar_qa_busquedas.py','QA_BUSQUEDAS_Y_DICTAMEN.json','MANIFEST_BUSQUEDAS_Y_DICTAMEN.json','preparar_cargas_acumulativas.py','PREPARACION_CARGAS_ACUMULATIVAS_MU2026.json','PREPARACION_CARGAS_ACUMULATIVAS_MU2026.md']
qa={'estado':'PASS_CON_PENDIENTES_E','fecha':'2026-10-28','rama':branch,'head_antes_y_despues':head,'matriz_numerica_igual_al_head':True,'fuentes_matriz_iguales_al_head':True,'libros_y_base_intactos_sha256':True,'detalle_4105_identico_por_multiconjunto':True,'hoja1_2379_igual_a_H001_V24':True,'continuidades_400_sin_doble_conteo':True,'cruce_abril_independiente_sql':{'diferencias':0,'vig0_en_todos_codigos':sum(sql_counts.values()),'vig0_en_48':check['vig0_nuestra_con_vigente_abril_familia_en_48']},'cuadratura_por_codigo_48':True,'brecha_226_conservada':True,'ac2027_rotulo_D_sin_convertir_a_A':True,'errores_en_busquedas':0,'reconstruccion_acumulativa':'E; no ejecutada sin llave e historial acreditados','staging_vacio':True,'commit_push_ejecutados':False,'detalle_individual_solo_privado':True,'privacidad':{'archivos':len(files),'coincidencias_identificadores_observados':0,'coincidencias_patron_rut_dv':0,'alcance':'Documentos MU, documentos y CODCLI de abril por límites de token; no se publican los valores. Metadatos de autor solicitados se conservan.'}}
qa['compatibilidad_por_codigo_sql']={'diferencias':0,'brecha_positiva':228,'cubrible':193,'pendiente_positivo':35,'porcentaje':100*193/228,'positivos_cubiertos':30,'exactos':4,'insuficientes':16,'negativos':2,'diferencia_negativa':-2,'neto':226,'nota':'32 con candidatas >= brecha incluyen 2 negativos; 193 se compone de 139+54, no sólo de los suficientes.'}
qa['etapa']='QA previo al commit y push autorizados; los estados de ejecución reflejan este instante.'
qa['preparacion_llaves']={'protocolo_generado':True,'reconstruccion_real_ejecutada':False,'equivalencia_de_formulaciones_originales_verificada_codigos':48,'llave_1':'documento + código único','llave_2':'documento + COD_CAR, sin sede, jornada ni versión','sensibilidad_gruesa_estructuralmente_distinta':True,'codigos_en_control_estructural':48,'cod_car_distintos_en_control':len(coarse),'cod_car_con_varios_codigos':sum(n>1 for n in coarse.values()),'hipotesis_sin_resultado':True,'llave_normativa_confirmada':False,'faltan':'Historial PES y archivo cargado de cada carga Finalizado'}
(OUT/'QA_BUSQUEDAS_Y_DICTAMEN.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
general=read(OUT/'QA.json');general['busquedas_y_dictamen']={'estado':qa['estado'],'qa':'QA_BUSQUEDAS_Y_DICTAMEN.json','sha256':sha(OUT/'QA_BUSQUEDAS_Y_DICTAMEN.json'),'matriz_numerica_igual_al_head':True,'privacidad_sin_coincidencias':True}
(OUT/'QA.json').write_text(json.dumps(general,ensure_ascii=False,indent=2)+'\n')
manifest={'estado':'QA_PREVIO_AL_RESPALDO_AUTORIZADO','head_esperado':head,'rama':branch,'autorizacion':'D: Alexi autoriza commit y push exclusivamente de estos 19 archivos, con la segunda llave gruesa y sin ejecutar la reconstrucción.','archivos_exactos':[{'ruta':str((OUT/name).relative_to(ROOT)),'sha256':sha(OUT/name)} for name in files if not name.startswith('MANIFEST_')],'manifest_excluido_de_su_propio_hash':True,'excluidos':['Datos individuales y bases XLSX/CSV','commits.sh','oferta_academica_2027/','Cualquier otro cambio pendiente'],'fuentes':[{'ruta':b['ruta'],'sha256':b['sha256']} for b in audit['libros']],'pendientes':['Fuente individual SIES MU2026 no localizada','Calendario oficial AC2027 no verificado: rótulo D de Alexi','Llave completa de actualización PES e historial exitoso de cargas sin acreditar','Brecha226 sin causa demostrada']}
(OUT/'MANIFEST_BUSQUEDAS_Y_DICTAMEN.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(t) for t in sorted(tokens,key=len,reverse=True) if len(t)>=6)+r')(?![A-Za-z0-9])')
observed=sum(len(pattern.findall((OUT/name).read_text())) for name in files)
rutpattern=re.compile(r'(?<![A-Za-z0-9])\d{7,9}-[\dKk](?![A-Za-z0-9])')
structural=sum(len(rutpattern.findall((OUT/name).read_text())) for name in files)
assert observed==structural==0,'Detener: posible identificador en archivo publicable'
assert subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True).returncode==0
print(json.dumps({'qa':qa['estado'],'archivos_exactos':len(files),'identificadores_detectados':observed,'sql_diferencias':0,'matriz_numerica_igual':True,'commit_push':False},ensure_ascii=False))

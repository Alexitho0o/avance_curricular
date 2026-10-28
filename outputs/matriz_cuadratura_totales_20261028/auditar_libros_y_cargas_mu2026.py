"""Auditoría sólo lectura: libros internos y condiciones de prueba acumulativa."""
import collections,csv,datetime,glob,hashlib,json,re
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/matriz_cuadratura_totales_20261028');PRIVATE.mkdir(parents=True,exist_ok=True)
def text(x):
    if x is None:return ''
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip().upper()
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(s):
    it=s.iter_rows(values_only=True);h=next(it)
    return h,[r for r in it if any(x is not None for x in r)]
def doc(n,dv=None):
    s=text(n).replace('.','').replace(' ','')
    if dv is not None:s+='-'+text(dv)
    return s
def code(r):return 'I162S{}C{}J{}V{}'.format(*(text(r[k]) for k in ('COD_SED','COD_CAR','JOR','VERSION')))
def source_meta(p,w):
    pr=w.properties
    return {'ruta':str(p),'sha256':sha(p),'autor_declarado':pr.creator,'ultimo_modificador_declarado':pr.lastModifiedBy,'fecha_creacion_ooxml':str(pr.created),'fecha_modificacion_ooxml':str(pr.modified),'nota_fechas':'Metadatos editables del libro; no acreditan fecha de recepción PES ni instante de extracción UMAS.','hojas':[{'hoja':s.title,'filas_declaradas':s.max_row,'columnas_declaradas':s.max_column} for s in w]}
def relation(a,b):
    if a==b:return 'idéntico'
    if a<b:return 'subconjunto'
    if b<a:return 'superconjunto'
    return 'independiente' if not a&b else 'independiente con intersección parcial'
cat=json.loads((ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())
base=Path(next(x['ruta_consolidada'] for x in cat['catalogo'] if x['sha256']=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'))
assert sha(base)=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
b=openpyxl.load_workbook(base,read_only=True,data_only=True);h,rs=load(b['BASE_RETENCION_MU']);mu=[dict(zip(h,r)) for r in rs if text(r[0])=='2026'];b.close()
mu_key={(doc(r['N_DOC'],r['DV']) if text(r['DV']) else doc(r['N_DOC']),code(r)):text(r['VIG']) for r in mu}
assert len(mu)==4105
by_doc=collections.defaultdict(set)
for d,c in mu_key:by_doc[d].add(c)
src=Path(glob.glob('/Users/alexi/Library/CloudStorage/OneDrive-*/Datos DAI*/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026')[0])
paths=[src/'MATRÍCULA UNIFICADA 2026.xlsx',src/'SEGUNDA CARGA/ARCHIVOS VARIOS/Matricula Unificada_ ABF.xlsx',src/'PRIMERA CARGA/RESPALDO MATRÍCULA UNIFICADA 2026.xlsx']
expected=['7787626606187375b6915a0c0651885fff54567841e87e7685351a8b593d65f1','02b48ea4f4de0cd210bfeb743149f063947e121aed70442a1f6a541cb2be1e44','7a9240c994cbf375a0ff5e871f5a8eca70e94c8605fffa40b5b8c53d3366ada5']
assert [sha(p) for p in paths]==expected,'Fuente distinta de la auditada'
assert len(mu_key)==len(mu),'Llave documental/código no única en MU'
books=[];priv=[]
w=openpyxl.load_workbook(paths[0],read_only=True,data_only=True);meta=source_meta(paths[0],w)
h,rows=load(w['06_DETALLE_TOTAL']);vals=[dict(zip(h,r)) for r in rows]
detail=collections.Counter((doc(r['RUT']),code(r),text(r['VIG'])) for r in vals)
basecounter=collections.Counter((d,c,v) for (d,c),v in mu_key.items())
meta['06_DETALLE_TOTAL']={'registros':len(rows),'grano':'matrícula por documento y código SIES','relacion_mu2026':relation(set(detail),set(basecounter)),'identica_multiconjunto_rut_codigo_vig':detail==basecounter,'solo_libro':sum((detail-basecounter).values()),'solo_mu':sum((basecounter-detail).values())}
h,rows=load(w['Hoja1']);hc=collections.Counter((text(r[0]),doc(r[6],r[7]),text(r[4])) for r in rows);yearcounts=collections.Counter(text(r[0]) for r in rows)
v24=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261025_V24.xlsx')
try:
    assert sha(v24)=='bfeba67628107f460cad69c5db119a6245782142bd5b65ab435b0cd116bca2db'
    ref=openpyxl.load_workbook(v24,read_only=True,data_only=True);s=ref['9_Base_Analitica_Detalle']
    refc=collections.Counter((text(r[1]),doc(r[7],r[8]),text(r[5])) for r in s.iter_rows(min_row=7,values_only=True) if r[1] in (2022,2023,2024,2025));ref.close()
    same=hc==refc
except (OSError,AssertionError):same=None
meta['Hoja1']={'registros':len(rows),'grano':'persona-cohorte con indicador anual retenido','por_cohorte':dict(yearcounts),'coincide_con_H001_V24_por_cohorte_documento_retencion':same,'origen':'C comparación con V24; no equivale a bitácora de creación','relacion_mu2026':'independiente: cohortes 2022–2025, no padrón de matrícula 2026'}
meta['dictamen']={'a_fuente_sies':'NO SIRVE: libro interno, no descarga PES acreditada','b_brecha_226':'NO SIRVE: derivado que reproduce nuestra base' if detail==basecounter else 'SIRVE PARCIAL: discrepancia interna, no lado SIES','c_otro_uso':'SIRVE: auditoría de nuestra MU y reproducción histórica H001; no es evidencia independiente de SIES'}
books.append(meta);w.close()
group_path=ROOT/'data/versiones_por_cohorte/20261028/grupos_existentes.json';groups=json.loads(group_path.read_text());gmap=collections.defaultdict(list)
assert sha(group_path)=='fe8837a760d4ed132505bf92138145e08adb3ce0a2486c9e3f26f08ca11babfc'
for g in groups:gmap[(g['codcarpr'],g['sede'],g['jornada'])].append(g)
abril_code=collections.defaultdict(set);abril_families=collections.defaultdict(set);abril_families_estrictas=collections.defaultdict(set);ambiguos=collections.Counter();april_priv=[]
def prep_sheet(w,name):
    h,rows=load(w[name]);actual=collections.Counter();keys=[];profiles={k:collections.Counter() for k in ('ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','VIG')}
    for row in rows:
        r=dict(zip(h,row))
        if not r.get('TIPO_DOC') or r.get('N_DOC') is None:continue
        d=doc(r['N_DOC'],r['DV']) if text(r['DV']) else doc(r['N_DOC']);c=code(r);vig=text(r['VIG']);actual[(d,c,vig)]+=1;keys.append((d,c))
        for field in profiles:profiles[field][text(r.get(field))]+=1
    kset=set(keys);sames=sum(n for k,n in actual.items() if k in basecounter)
    return {'registros':len(rows),'matriculas_con_llave':len(keys),'llaves_distintas':len(kset),'grano':'matrícula preparada de 32 campos MU','relacion_mu2026_documento_codigo':relation(kset,set(mu_key)),'interseccion_mu2026':len(kset & set(mu_key)),'coincidencias_tambien_vig':sames,'sin_correspondencia_mu2026':len(kset-set(mu_key)),'campos_ingreso_y_vig':{k:dict(v) for k,v in profiles.items()}},actual
w=openpyxl.load_workbook(paths[1],read_only=True,data_only=True);meta=source_meta(paths[1],w)
meta['MATRICULA_UNIFICADA_32'],_=prep_sheet(w,'MATRICULA_UNIFICADA_32')
exp_sets={}
for sn in ('Vigentes','Continuidades'):
    h,rows=load(w[sn]);positions={name:i for i,name in enumerate(h)};exps=set();docset=set();states=collections.Counter()
    for row in rows:
        # Las dos columnas RUT contienen sólo el cuerpo; DV es independiente.
        # Usar el cuerpo de la segunda RUT y su DV explícito, incluido 0.
        d=doc(row[10],row[11]);c=text(row[positions['CODCARPR']]);sede=text(row[positions['SEDE']]);j=text(row[positions['JORNADA']]);cl=text(row[positions['CODCLI']]);state=text(row[positions['ESTADOACADEMICO']]);exps.add((d,cl));docset.add(d);states[state]+=1
        if sn!='Vigentes' or state!='VIGENTE':continue
        gg=gmap.get((c,sede,j),[]);families={f for g in gg for f in g['familias']};codes={cc for g in gg for cc in g['codigos_base']}
        for f in families:abril_families[f].add(d)
        if len(families)==1:abril_families_estrictas[next(iter(families))].add(d)
        in_mu={cc for cc in by_doc.get(d,set()) if cc.rsplit('V',1)[0] in families}
        if len(in_mu)==1:selected=next(iter(in_mu));method='código de referencia MU2026, misma familia'
        elif not in_mu and len(codes)==1:selected=next(iter(codes));method='candidato único de grupo'
        else:
            selected=None;method='sin grupo' if not gg else 'version_no_univoca'
            ambiguos[method]+=1
        if selected:abril_code[selected].add(d)
        april_priv.append({'documento':d,'codcli':cl,'codcarpr':c,'familias':sorted(families),'codigo_referencia':selected,'metodo':method})
    exp_sets[sn]=exps
    meta[sn]={'registros':len(rows),'personas_documento':len(docset),'expedientes_documento_codcli':len(exps),'estados':dict(states),'grano':'expediente UMAS; la persona puede repetirse por CODCLI','documentos_en_mu2026':len(docset & set(by_doc)),'relacion_documentos_mu2026':relation(docset,set(by_doc))}
meta['continuidades_ya_en_vigentes_expedientes']=len(exp_sets['Vigentes']&exp_sets['Continuidades'])
meta['Vigentes']['normalizacion_documento']='RUT cuerpo en columnas A/K + DV en L; se conserva DV numérico 0. No se cruza el cuerpo solo.'
meta['asignacion_codigos_abril']={'metodo':'Grupos 20261028; se conserva código MU de referencia sólo con familia única concordante, o candidato único; no se elige versión por totales','ambiguedades_filas':dict(ambiguos),'fuente_mapa_sha256':sha(group_path),'limite':'Versión de referencia anual no acredita versión asignada al 09-04. Conteos por código son C/E y excluyen filas no atribuibles.'}
meta['dictamen']={'a_fuente_sies':'NO SIRVE: preparación interna anterior al corte','b_brecha_226':'SIRVE PARCIAL: prueba de compatibilidad por código; no acredita aceptación SIES','c_otro_uso':'SIRVE: trazabilidad UMAS pre-corte, continuidad y preparación MU'}
books.append(meta);w.close()
with (ROOT/'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/DETALLE_CONCILIACION.csv').open(encoding='utf-8-sig',newline='') as f:agg=[r for r in csv.DictReader(f,delimiter=';') if r['ANIO']=='2026' and r['ALCANCE']=='Pregrado' and int(r['DIF_CSV_VIG1_UNION'])!=0]
assert len(agg)==48
table=[];match_private=[]
for a in agg:
    c=a['CODIGO_COMPLETO'];fam=c.rsplit('V',1)[0];zeros={d for (d,cc),v in mu_key.items() if cc==c and v=='0'}
    overlap=zeros & abril_families[fam];pub=int(a['CSV_TOTAL_ESTRUCTURAL_UNION']);vig1=int(a['MU_VIG1_ESTRUCTURAL_UNION'])
    table.append({'codigo_sies':c,'vigentes_abril_codigo_referencia_personas':len(abril_code[c]),'vig1_nuestra':vig1,'publicacion_sies':pub,'brecha_publicado_menos_vig1':pub-vig1,'nuestras_vig0_vigentes_abril_misma_familia':len(overlap),'coincidencias_con_familia_unica':len(zeros & abril_families_estrictas[fam]),'residuo_escenario_agregar_esos_vig0':pub-vig1-len(overlap),'clase':'B abril; C cruce por familia candidata; E explicación SIES/versión abril'})
    positive=max(pub-vig1,0);cover=min(positive,len(overlap))
    table[-1].update(brecha_positiva=positive,cubrible_por_candidatas=cover,sin_cubrir=positive-cover,grupo_compatibilidad='BRECHA_NEGATIVA' if pub<vig1 else 'POSITIVA_CUBIERTA' if len(overlap)>=positive else 'POSITIVA_INSUFICIENTE')
    match_private.extend({'documento':d,'codigo_mu2026':c,'vig_mu':0,'estado_abril':'VIGENTE','alcance':'coincidencia de familia; no prueba de versión abril'} for d in sorted(overlap))
total_overlap=sum(r['nuestras_vig0_vigentes_abril_misma_familia'] for r in table)
all_zero_match={(d,c) for (d,c),v in mu_key.items() if v=='0' and d in abril_families[c.rsplit('V',1)[0]]}
april_check={'codigos':48,'unidad':'matrículas documento/código, no suma de personas únicas entre códigos','suma_brecha':sum(r['brecha_publicado_menos_vig1'] for r in table),'vig0_mu2026_total':sum(v=='0' for v in mu_key.values()),'vig0_nuestra_con_vigente_abril_familia_todos_codigos':len(all_zero_match),'vig0_nuestra_con_vigente_abril_familia_en_48':total_overlap,'residuo_neto_escenario':sum(r['residuo_escenario_agregar_esos_vig0'] for r in table),'codigos_con_residuo_cero':sum(r['residuo_escenario_agregar_esos_vig0']==0 for r in table),'cuadra_todos_los_codigos':all(r['residuo_escenario_agregar_esos_vig0']==0 for r in table),'estado':'E: una fotografía interna no acredita aceptación SIES ni causa de la brecha'}
april_check['coincidencias_familia_unica_en_48']=sum(r['coincidencias_con_familia_unica'] for r in table)
april_check['nota_familia']='El mapa contiene IECIREOL con dos familias candidatas. Se separa el control de familia única; no se asigna familia por totales.'
positive=[r for r in table if r['brecha_publicado_menos_vig1']>0]
negative=[r for r in table if r['brecha_publicado_menos_vig1']<0]
covered=[r for r in positive if r['sin_cubrir']==0]
short=[r for r in positive if r['sin_cubrir']>0]
positive_gap=sum(r['brecha_positiva'] for r in table);coverable=sum(r['cubrible_por_candidatas'] for r in table)
compatibility={'clase':'C/E compatibilidad, no aceptación SIES','hipotesis':'SIES pudo contar una parte de nuestras VIG 0 que estaban vigentes en abril, no necesariamente todas.','formula':'cubrible por código = min(max(publicado − VIG1 nuestra, 0), candidatas); porcentaje = suma cubrible / suma brechas positivas','codigos_positivos':len(positive),'brecha_positiva':positive_gap,'codigos_positivos_cubiertos_totalmente':len(covered),'codigos_candidatas_mayor_igual_brecha_incluye_negativos':len(covered)+len(negative),'codigos_positivos_exactos':sum(r['brecha_positiva']==r['nuestras_vig0_vigentes_abril_misma_familia'] for r in positive),'cubrible_en_positivos_cubiertos_totalmente':sum(r['cubrible_por_candidatas'] for r in covered),'codigos_positivos_insuficientes':len(short),'cubrible_en_insuficientes':sum(r['cubrible_por_candidatas'] for r in short),'cubrible_total':coverable,'sin_cubrir_total':sum(r['sin_cubrir'] for r in table),'compatibilidad_porcentaje':100*coverable/positive_gap,'codigos_negativos':len(negative),'brecha_negativa':sum(r['brecha_publicado_menos_vig1'] for r in negative),'brecha_neta':sum(r['brecha_publicado_menos_vig1'] for r in table),'nota_conteos':'Los 32 códigos de candidatas >= brecha incluyen los dos negativos: 30 positivos cubiertos + 16 insuficientes + 2 negativos = 48. Los 193 cubribles suman 139 de los 30 positivos cubiertos y 54 de los 16 insuficientes.','clasificacion':'Compatible con aproximadamente el 85% de la brecha positiva (C/E); no acredita aceptación SIES.','no_cubiertas_por_codigo':[{'codigo_sies':r['codigo_sies'],'brecha_positiva':r['brecha_positiva'],'candidatas':r['nuestras_vig0_vigentes_abril_misma_familia'],'cubrible':r['cubrible_por_candidatas'],'sin_cubrir':r['sin_cubrir'],'solo_publicado_sin_mu':r['vig1_nuestra']==0 and not any(cc==r['codigo_sies'] for _,cc in mu_key),'estado':'E'} for r in short],'negativas_por_codigo':[{'codigo_sies':r['codigo_sies'],'diferencia':r['brecha_publicado_menos_vig1'],'estado':'E: diferencia negativa separada, sin compensar pendientes positivos'} for r in negative]}
assert len(covered)+len(short)+len(negative)==48
assert coverable+compatibility['sin_cubrir_total']==positive_gap
april_check['compatibilidad_por_codigo']=compatibility
w=openpyxl.load_workbook(paths[2],read_only=True,data_only=True);meta=source_meta(paths[2],w);meta['SUBIR'],actual=prep_sheet(w,'SUBIR')
first_focus={c:sum(n for (d,cc,v),n in actual.items() if cc==c) for c in (r['codigo_sies'] for r in table)}
meta['SUBIR']['registros_en_48_codigos']=sum(first_focus.values());meta['SUBIR']['por_codigo_en_48']=first_focus
meta['dictamen']={'a_fuente_sies':'NO SIRVE: libro de preparación anterior al corte, sin prueba de recepción PES','b_brecha_226':'SIRVE PARCIAL: propuesta pre-corte del primer año; no valida la cifra SIES','c_otro_uso':'SIRVE: preparación MU/FCU y control de cohorte inicial. SUBIR contiene estructura MU de 32 campos; no se reduce a FCU.'}
books.append(meta);w.close()
manual=ROOT/'manual_matrícula_unificada.txt'
loads=[]
for p in sorted(src.rglob('*')):
    if p.is_file() and (p.suffix.lower() in ('.zip','.csv') or 'rectific' in p.name.lower()):
        n=p.name.lower()
        if any(k in n for k in ('_orig','para_subir','libro1','rectific','matricula_unificada_ok')):loads.append({'ruta':str(p),'bytes':p.stat().st_size,'recepcion_finalizada':'E no acreditada por nombre o existencia del archivo'})
accum={'estado':'E_NO_EJECUTADA','manual':{'ruta':str(manual),'sha256':sha(manual),'acumulativas':'A página 15, líneas 468–470: cargas acumulativas, actualización al cargar correctamente','finalizada':'A página 16, líneas 483–498: historial y resultado Finalizado permiten acreditar éxito','vig0':'A páginas 17–18, líneas 519–529: para retirar matrícula se recarga VIG 0; no se borra el registro','identificacion':'Página 38, líneas 1266–1267 menciona misma identificación, sin explicitar aquí la composición completa de la llave.'},'bloqueos':['No se acreditó en manual la composición exacta de la llave de actualización; no se sustituye por una llave inferida de nuestros scripts.','No hay historial PES completo de cargas Finalizado que acredite orden, éxito de primeras/segunda/tercera cargas y recepción de rectificación 23-06.','No se localizó evidencia verificable de reinicio/eliminación de cargas 2026 en los respaldos revisados. Ausencia de evidencia no prueba que no ocurriera.'],'archivos_candidatos':loads,'vig1_resultante':None,'llaves_antiguas_no_sobrescritas':None,'nota':'No se reconstruye un estado PES fingiendo que los envíos locales equivalen a cargas aceptadas.'}
accum['respaldos_internos_revisados']=[{'ruta':str(ROOT/r),'sha256':sha(ROOT/r)} for r in ('CIERRE_PES_READY_MU2026.md','control/gate/gate_final_mu_2026.md','control/reportes/decision_operativa_mu_2026.md','control/reportes/ejecucion_oficial_mu_2026.md')]
accum['evidencia_parcial']='B: CIERRE_PES_READY_MU2026.md del 07-05 declara 3.402 filas y comparación con un archivo que completó carga; el gate registra 3.433 filas brutas. Son controles internos, no historial completo de recepciones PES ni evidencia de las cargas posteriores.'
accum['vig1_nuestra_institucional']=3145;accum['publicacion_sies_pregrado']=3371
accum['preparacion_sensibilidad']={'estado':'PREPARADO_NO_EJECUTADO','clase':'C/E, llaves candidatas no confirmadas como llave normativa PES','llave_1':['TIPO_DOC','N_DOC','DV','CODIGO_UNICO'],'llave_2':['TIPO_DOC','N_DOC','DV','COD_CAR'],'documento':'Tipo, número y DV originales; DV 0 se conserva. No se usa cuerpo de RUT solo.','antecedente':'Las formulaciones originales documento+código único y documento+S+C+J+V son equivalentes con I162 fijo y componentes coherentes. Se reemplaza la segunda.','relacion_entre_llaves':'L1 conserva código único completo; L2 gruesa omite sede, jornada y versión y puede sobrescribir contextos distintos de una misma carrera.','hipotesis':'C/E: si L1 reproduce mejor la publicación que L2 y el linaje confirma registros antiguos no sobrescritos, éstos son una explicación candidata; no es prueba de aceptación SIES.','fuente_requerida':'Export o captura del Historial de Carga MU2026, más ver el archivo cargado de cada carga Finalizado; Alexi descargará estos respaldos.','prohibicion':'No reconstruir con archivos locales de envío, orig.zip, PARA_SUBIR o reconstrucciones internas.','protocolo':'PREPARACION_CARGAS_ACUMULATIVAS_MU2026.json'}
result={'clase':'B metadatos/filas; C comparación; D rótulo AC2027 de Alexi; E atribución SIES y prueba acumulativa','libros':books,'comparacion_abril_48_codigos':table,'comprobacion_abril':april_check,'prueba_cargas_acumulativas':accum}
private_path=PRIVATE/'DICTAMEN_LIBROS_MU2026_DETALLE.json';private_path.write_text(json.dumps({'abril':april_priv,'vig0_abril_48':match_private},ensure_ascii=False,indent=2)+'\n');private_path.chmod(0o600)
result['detalle_privado']={'ruta':str(private_path),'sha256':sha(private_path)}
assert [sha(p) for p in paths]==expected
result['fuentes_intactas_por_hash']=True
result['fuente_base_mu']={'ruta':str(base),'sha256':sha(base),'registros_mu2026':4105}
(OUT/'DICTAMEN_LIBROS_Y_CARGAS_MU2026.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# Dictamen de libros internos y prueba acumulativa MU2026','','| Libro | (a) Fuente SIES | (b) Brecha 226 | (c) Otro uso |','|---|---|---|---|']
for b in books:lines.append('| '+Path(b['ruta']).name+' | '+' | '.join(b['dictamen'].values())+' |')
lines+=['','## Metadatos y composición de los libros [B]','', 'Las fechas son propiedades OOXML editables, sin zona horaria acreditada; no prueban corte ni recepción PES. Dimensiones incluyen encabezados y posibles celdas de formato.']
for b in books:
    lines+=['', '### '+Path(b['ruta']).name,'',f"Autor: {b['autor_declarado']}. Último modificador: {b['ultimo_modificador_declarado']}. Creación: {b['fecha_creacion_ooxml']}. Modificación: {b['fecha_modificacion_ooxml']}.",f"SHA-256: `{b['sha256']}`.",'','| Hoja | Filas declaradas | Columnas declaradas |','|---|---:|---:|']
    lines += [f"| {s['hoja']} | {s['filas_declaradas']} | {s['columnas_declaradas']} |" for s in b['hojas']]
lines+=['','## Universo, grano y relación con MU [B/C]','', '06_DETALLE_TOTAL: 4.105 matrículas por documento/código; idéntico por documento, código y VIG, con cero filas exclusivas. Hoja1: 2.379 personas-cohorte H001 (305/366/558/1.150 para 2022/2023/2024/2025), idénticas a V24 por documento/cohorte/indicador. Esto acredita contenido, no la autoría del proceso que creó Hoja1.','']
for sn in ('Vigentes','Continuidades','MATRICULA_UNIFICADA_32'):
    lines.append(f"ABF · {sn}: "+json.dumps(books[1][sn],ensure_ascii=False))
lines+=['',f"Continuidades: {books[1]['continuidades_ya_en_vigentes_expedientes']} de 400 expedientes ya están en Vigentes; no se suman nuevamente.", 'RESPALDO · SUBIR: '+json.dumps({k:v for k,v in books[2]['SUBIR'].items() if k!='por_codigo_en_48'},ensure_ascii=False),'','Los conjuntos ABF y SUBIR son independientes con intersección parcial respecto de MU anual; no son subconjuntos por documento/código. Las identidades se comparan con DV explícito, incluido 0.','', '## Compatibilidad por código de la fotografía UMAS de abril [C/E]','', '**Compatible con el 84,65% (aproximadamente 85%) de la brecha positiva; no acredita aceptación SIES.** La hipótesis contempla una parte de las VIG 0 vigentes en abril, sin sumar automáticamente las 459.','', '| Grupo disjunto | Códigos | Brecha positiva | Cubrible | Sin cubrir |','|---|---:|---:|---:|---:|',f"| Positiva cubierta totalmente (4 exactos) | {len(covered)} | {sum(r['brecha_positiva'] for r in covered)} | {sum(r['cubrible_por_candidatas'] for r in covered)} | 0 |",f"| Positiva insuficiente | {len(short)} | {sum(r['brecha_positiva'] for r in short)} | {sum(r['cubrible_por_candidatas'] for r in short)} | {compatibility['sin_cubrir_total']} |",f"| Total positivo | {len(positive)} | {positive_gap} | {coverable} | {compatibility['sin_cubrir_total']} |",'','Cubrible = suma de min(brecha positiva, candidatas), calculada por código: 139 + 54 = 193; 193/228 = 84,6491%. Brecha neta: 228 − 2 = 226. Los 32 códigos que cumplen candidatas >= brecha incluyen dos negativos; no equivalen a 32 positivos ni a 193 cubribles por sí solos.','', 'Las versiones de referencia usan código MU cuando es único en la misma familia o un candidato único. Las 49 filas no atribuibles quedan visibles. Todas las 459 coincidencias candidatas tienen familia única en este foco; no se acredita con ello la versión en abril ni aceptación SIES.','', '| Código | Vigentes abril atribuibles | VIG1 nuestra | Publicado | Brecha | Candidatas VIG0 abril | Cubrible | Sin cubrir |','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in table:lines.append('| '+r['codigo_sies']+' | '+' | '.join(str(r[k]) for k in ('vigentes_abril_codigo_referencia_personas','vig1_nuestra','publicacion_sies','brecha_publicado_menos_vig1','nuestras_vig0_vigentes_abril_misma_familia','cubrible_por_candidatas','sin_cubrir'))+' |')
lines+=['','### Las 35 matrículas no cubiertas: pendientes E por código','','| Código | Brecha positiva | Candidatas | Cubrible | Sin cubrir | Sólo publicado, sin MU |','|---|---:|---:|---:|---:|---|']
for r in compatibility['no_cubiertas_por_codigo']:lines.append(f"| {r['codigo_sies']} | {r['brecha_positiva']} | {r['candidatas']} | {r['cubrible']} | {r['sin_cubrir']} | {'Sí' if r['solo_publicado_sin_mu'] else 'No'} |")
lines+=['','### Brechas negativas: separadas de los pendientes positivos [E]','','| Código | Diferencia publicado menos nuestra VIG1 |','|---|---:|']
for r in compatibility['negativas_por_codigo']:lines.append(f"| {r['codigo_sies']} | {r['diferencia']} |")
lines+=['','## Cargas acumulativas: preparadas, no ejecutadas [C/E]', '', 'A: Manual MU2026 p.15, líneas 468–478: cargas acumulativas; el registro se actualiza al cargarse correctamente, resultado Finalizado. P.16, líneas 483–498: Historial de Carga ordenado por fecha y acción ver el archivo cargado.', '', 'Las formulaciones originales documento+código único y documento+S+C+J+V eran equivalentes con I162 fijo y componentes coherentes [C]. Se reemplaza la segunda por una sensibilidad gruesa: L1 documento+código único; L2 documento+COD_CAR, sin sede, jornada ni versión. Documento conserva tipo, número y DV, incluido 0. Son candidatas C/E, no llave normativa PES confirmada.', '', 'Hipótesis C/E: si L1 reproduce mejor la publicación que L2 y el linaje identifica registros antiguos no sobrescritos, éstos son una explicación candidata. Se evaluará por código, discrepancia absoluta total y códigos coincidentes; el neto no basta. No acredita aceptación SIES.', '', 'Fuente requerida: Alexi descargará export o captura del Historial de Carga MU2026 y el archivo cargado de cada carga Finalizado. Se excluirán errores y se acreditarán orden, hashes y posibles reinicios. No se usarán archivos locales de envío. Protocolo: PREPARACION_CARGAS_ACUMULATIVAS_MU2026.json. No hay cifra reconstruida de VIG1 ni de llaves antiguas.']
(OUT/'DICTAMEN_LIBROS_Y_CARGAS_MU2026.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'detalle_total':books[0]['06_DETALLE_TOTAL'],'hoja1':books[0]['Hoja1'],'abril':april_check,'subir':books[2]['SUBIR'],'prueba_acumulativa':accum['estado']},ensure_ascii=False))

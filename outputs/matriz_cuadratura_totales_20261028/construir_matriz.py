#!/usr/bin/env python3
"""Cuadratura agregada: no escribe registros individuales y valida sus entradas."""
import collections, csv, glob, hashlib, json, re, sys
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from common.analisis_desercion.h001 import reproducir_h001, normalizar, llave, origen, positivo, codigo
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, rut_normalizado
def hashfile(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()
def verified(path, expected):
    p = Path(path)
    if hashfile(p) != expected: raise ValueError('Hash distinto: ' + str(p))
    return p
def one(pattern):
    hits=glob.glob(pattern)
    if len(hits)!=1: raise ValueError('Ruta no única: '+pattern)
    return Path(hits[0])
def norm(x):
    if x is None: return ''
    s=str(x).strip().upper()
    if s.endswith('.0') and s[:-2].isdigit(): s=s[:-2]
    return re.sub(r'[^0-9A-Z]', '', s)
def identity(tipo, doc, dv):
    t,d,v=norm(tipo),norm(doc),norm(dv)
    if not t or not d or (t == 'R' and not v): return None
    return (t,d,v)
def jsonread(p): return json.loads(Path(p).read_text(encoding='utf-8'))
CAT_PATH=ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json'
CAT=jsonread(CAT_PATH)
def fuente(expected):
    matches=[x for x in CAT['catalogo'] if x['sha256']==expected]
    if len(matches)!=1: raise ValueError('Hash sin entrada única en catálogo '+expected)
    return verified(matches[0]['ruta_consolidada'],expected)

base=fuente('19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd')
agg=verified(ROOT/'outputs/retencion_primer_anio_h001_activo_20261028/RETENCION_PRIMER_ANIO_AGREGADO.json','ad40ada98ec2f30fbd788afc5dc4c1afd620d8ab624ab41d114049f882e258c5')
publico=fuente('70758082b7b5ab6363b267f58d334f86349a6c355dc5636cf1654b90dedca229')
da=fuente('a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9')
glosario=fuente('b9be9c46aa1c27452d55fc9efaef87c65624c40d4bc1234d21e87897f89af05f')
grupos_path=verified(ROOT/'data/versiones_por_cohorte/20261028/grupos_existentes.json','fe8837a760d4ed132505bf92138145e08adb3ce0a2486c9e3f26f08ca11babfc')
maestro_path=verified(ROOT/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json','2ef459251e91ecebe5370402e3d2ea25341aeecbfb3ca54eca210cc347c392a5')
familias=collections.defaultdict(set)
for grupo in jsonread(grupos_path):
    for familia in grupo['familias']: familias[familia].add(normalizar(grupo['codcarpr']))
for grupo in jsonread(maestro_path)['equivalencias_programa_2026']:
    code=normalizar(grupo['codigo_unico']); familia=re.sub(r'V\d+$','',code)
    if re.fullmatch(r'I162S\d+C\d+J\d+',familia): familias[familia].add(normalizar(grupo['codcarpr']))
mu=collections.defaultdict(list)
ws=openpyxl.load_workbook(base,read_only=True,data_only=True)['BASE_RETENCION_MU']
it=ws.iter_rows(values_only=True); hdr=next(it)
for row in it:
    r=dict(zip(hdr,row)); a=r['ANIO_INFORMADO']
    if a and 2022<=int(a)<=2026: mu[int(a)].append(r)
diagnostico=verified(ROOT/'outputs/retencion_primer_anio_ipss_162/20260930_000000/RETENCION_PRIMER_ANIO_IPSS_162_DIAGNOSTICO_BRECHAS_20260930.xlsx','5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3')
w=openpyxl.load_workbook(diagnostico,read_only=True,data_only=True)
it=w['01_CATALOGO_CARRERA'].iter_rows(values_only=True); ch=next(it); catalogo=[dict(zip(ch,r)) for r in it]
all_rows=[r for year in sorted(mu) for r in mu[year]]
ac2026=fuente('f86e805ca2909f0f8e3dd439a5afb7fc15939a8078b17e13ef33b5cdec2490ed')
with ac2026.open(encoding='latin1',newline='') as f:
    ac_reader=csv.DictReader(f,delimiter=';')
    required={'TIPO_DOCUMENTO','NUM_DOCUMENTO','DV','CODIGO_UNICO','VIGENCIA'}
    if not required.issubset(ac_reader.fieldnames):raise ValueError('Precarga AC sin campos obligatorios')
    ac_rows=list(ac_reader)
ac_index=collections.defaultdict(set)
for r in ac_rows:
    k=(identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV']),normalizar(r['CODIGO_UNICO']))
    ac_index[k].add(normalizar(r['VIGENCIA']))
ac_counts=collections.Counter();ac_details=[]
for fila,r in enumerate(mu[2025],2):
    ident=identity(r['TIPO_DOC'],r['N_DOC'],r['DV']); code=codigo(r);vig=normalizar(r['VIG'])
    key=(ident,code); states=ac_index.get(key,set())
    ac_counts['mu_vig_'+vig]+=1
    if ident is not None and states=={'1'}:ac_counts['mu_vig_'+vig+'_en_ac_vigencia_1']+=1
    else:ac_counts['sin_coincidencia_univoca_vigencia_1']+=1
    ac_details.append({'identidad':ident,'codigo':code,'vig_mu':vig,'vigencias_ac_observadas':sorted(states)})
assert ac_counts['mu_vig_1']==2298 and ac_counts['mu_vig_0']==73
assert ac_counts['mu_vig_1_en_ac_vigencia_1']==2298 and ac_counts['mu_vig_0_en_ac_vigencia_1']==73
assert ac_counts['sin_coincidencia_univoca_vigencia_1']==0
ac_private=Path('/Users/alexi/.local/share/ipss/matriz_cuadratura_totales_20261028/CRUCE_MU2025_PRECARGA_AC2026.json')
ac_private.parent.mkdir(parents=True,exist_ok=True)
ac_private.write_text(json.dumps(ac_details,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');ac_private.chmod(0o600)
eligibles=reproducir_h001(all_rows,catalogo)
por_programa=collections.defaultdict(list); por_persona=collections.defaultdict(list)
for p in catalogo: por_programa[(normalizar(p['ANO']),normalizar(p['CODIGO_UNICO']))].append(p)
for r in all_rows: por_persona[(normalizar(r['ANIO_INFORMADO']),llave(r))].append(r)
minimos={'Técnico de Nivel Superior':4,'Profesional Sin Licenciatura':6,'Profesional Con Licenciatura':8,'Licenciatura no conducente a título':8}
exclusiones=collections.defaultdict(collections.Counter)
for r in all_rows:
    y=int(r['ANIO_INFORMADO']); o=origen(r)
    if y not in range(2022,2026) or o[0]!=str(y) or o[1] not in ('1','2'): continue
    if normalizar(r['VIG'])=='0': motivo='VIG 0'
    else:
        programas=por_programa[('OFE_'+str(y),codigo(r))]
        if len(programas)!=1: motivo='catálogo sin coincidencia única'
        else:
            p=programas[0]; minimo=minimos.get(normalizar(p['NIVEL_CARRERA']))
            if (normalizar(p['NIVEL_GLOBAL'])!='Pregrado' or normalizar(p['TIPO_CARRERA'])!='Plan Regular' or normalizar(p['PLAN_ESPECIAL'])!='NO APLICA' or minimo is None or float(p['DURACION_ESTUDIOS'])<minimo): motivo='programa o duración no elegible'
            else:
                actual=[a for a in por_persona[(str(y),llave(r))] if positivo(a) and origen(a)==o]
                siguiente=[a for a in por_persona[(str(y+1),llave(r))] if positivo(a)]
                if len(actual)>1: motivo='matrículas positivas duplicadas en cohorte'
                elif len(siguiente)>sum(origen(a)==o for a in siguiente): motivo='origen distinto en año siguiente'
                else: motivo='elegible'
    exclusiones[y][motivo]+=1
for y in range(2022,2026):
    if exclusiones[y]['elegible']!=len(eligibles.get(y,[])): raise ValueError('Discrepancia clasificación H001 '+str(y))
previo={r['cohorte']:r for r in jsonread(agg)['grupos']['institucional']}
res=jsonread(ROOT/'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/RESULTADOS.json')
pre={r['ANIO']:r for r in res['resumen_anual'] if r['ALCANCE']=='Pregrado'}
base_agg=jsonread(ROOT/'data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json')
public=collections.defaultdict(collections.Counter)
total_publico=0
with open(publico,encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f):
        total_publico+=1
        try: year=int(r['cat_periodo'])
        except (ValueError,TypeError): continue
        if 2021<=year<=2025: public[year][(r['codigo_unico'],r['nomb_carrera'])]+=1
manifest=jsonread(ROOT/'outputs/reproduccion_puente_20261023_004044/FUENTES_HASHES_FINAL.json')
fuentes_hist=jsonread(ROOT/'outputs/reproduccion_puente_20261023_004044/FUENTES_HASHES.json')
hist=[(p,h) for p,h in fuentes_hist.items() if p.endswith('/MAT_IP_CIISA_2021.xlsx')]
if len(hist)!=1: raise ValueError('MU 2021 sin fuente única')
mu21=fuente(hist[0][1]); s=openpyxl.load_workbook(mu21,read_only=True,data_only=True)['MAT_2021']
it=s.iter_rows(values_only=True); hh=next(it); mu[2021]=[]
for row in it:
    r=dict(zip(hh,row)); doc=r.get('MM_N_DOCUMENTO'); dv=r.get('MM_DV')
    if doc is not None and dv is not None: mu[2021].append({'TIPO_DOC':'R','N_DOC':doc,'DV':dv})
titulos={}
cargas_individuales={}
for year, token in ((2022,'TIT_2022_162_def'),(2023,'TIT_IP_CIISA_2023')):
    paths=[(p,h) for p,h in manifest.items() if token in p and p.endswith('.csv')]
    if len(paths)!=1: raise ValueError('Fuente de titulación no única '+str(year))
    path=fuente(paths[0][1]); encoding='latin1' if year==2022 else 'utf-8-sig'
    with path.open(encoding=encoding,newline='') as f: records=list(csv.DictReader(f,delimiter=';'))
    cargas_individuales[year]=records
    personas={identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV']) for r in records}; personas.discard(None)
    title_codes=collections.Counter(r['COD_SIES_OBT_TIT'].strip() for r in records)
    matches={}
    for y in (year-1,year):
        if y not in mu: matches[str(y)]=None; continue
        ids={identity(r['TIPO_DOC'],r['N_DOC'],r['DV']) for r in mu[y]}; ids.discard(None)
        matches[str(y)]=len(personas & ids)
    titulos[year]={'archivo':str(path),'sha256':hashfile(path),'registros':len(records),'personas_con_llave_comparable':len(personas),'personas_con_mu_por_anio':matches,'por_codigo_obtenido':dict(title_codes),'estado':'E','nota':'Archivo de carga observado; alineación proceso t y cat_periodo t−1 es observación, no regla oficial acreditada. El cruce MU comprueba identidad, no expediente.'}
embudo=jsonread(ROOT/'outputs/auditoria_embudo_2317_20261022/HASHES_FUENTES.json')
f26=[(p,h) for p,h in embudo.items() if p.endswith('/Titulación Unificada 2026.csv')]
if len(f26)!=1: raise ValueError('Carga titulación 2026 no localizada')
p26=fuente(f26[0][1]); h22=next(csv.reader(open(titulos[2022]['archivo'],encoding='latin1',newline=''),delimiter=';'))
with p26.open(encoding='utf-8-sig',newline='') as f: rows26=list(csv.reader(f,delimiter=';'))
if any(len(r)!=len(h22) for r in rows26): raise ValueError('Estructura 2026 inesperada')
records=[dict(zip(h22,r)) for r in rows26]
personas={identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV']) for r in records}; personas.discard(None)
matches={}
for y in (2025,2026):
    ids={identity(r['TIPO_DOC'],r['N_DOC'],r['DV']) for r in mu[y]}; ids.discard(None); matches[str(y)]=len(personas & ids)
titulos[2026]={'archivo':str(p26),'sha256':hashfile(p26),'registros':len(records),'personas_con_llave_comparable':len(personas),'personas_con_mu_por_anio':matches,'por_codigo_obtenido':dict(collections.Counter(r['COD_SIES_OBT_TIT'].strip() for r in records)),'estado':'E','nota':'Estructura homologada con encabezado de 2022; carácter final de la carga y comparabilidad por código pendientes.'}
p24s=[(p,h) for p,h in fuentes_hist.items() if p.endswith('/TIT_IP_CIISA_2024.xlsx')]
if len(p24s)!=1: raise ValueError('Respaldo 2024 no localizado')
p24=fuente(p24s[0][1]); w24=openpyxl.load_workbook(p24,read_only=True,data_only=True)
s24=w24['21-03-2023_18-23-51_Titulados_2']; it=s24.iter_rows(values_only=True); h24=next(it)
rs24=[dict(zip(h24,r)) for r in it if r[1] and r[2]]
cargas_individuales[2024]=rs24
personas={identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV']) for r in rs24}; personas.discard(None)
matches={}
for y in (2023,2024):
    ids={identity(r['TIPO_DOC'],r['N_DOC'],r['DV']) for r in mu[y]}; ids.discard(None); matches[str(y)]=len(personas & ids)
titulos[2024]={'archivo':str(p24),'sha256':hashfile(p24),'hoja':s24.title,'registros':len(rs24),'personas_con_llave_comparable':len(personas),'personas_con_mu_por_anio':matches,'por_codigo_obtenido':dict(collections.Counter(normalizar(r['COD_SIES_OBT_TIT']) for r in rs24)),'estado':'E','nota':'Respaldo inventariado en Publicados: nombre y hoja no acreditan carga final del proceso 2024.'}
pes5319=fuente('08df93d633765d5b5b6ec9fafd89cb88898d9475e9e1696626fe352c669b4a56')
manual_entry=next(x for x in CAT['catalogo'] if x['archivo'].startswith('Instructivo_Titulacio'))
manual=fuente(manual_entry['sha256'])
accepted=collections.defaultdict(list)
with pes5319.open(encoding='latin1',newline='') as f:
    for fila,r in enumerate(csv.DictReader(f,delimiter=';'),2):
        y=normalizar(r['PERIODO_ACAD_TITULACION'])
        if y.isdigit(): accepted[int(y)].append((fila,r))
def codigo_derivado(c):
    c=normalizar(c)
    return 'I'+c if re.fullmatch(r'162S\d+C\d+J\d+V\d+',c) else c
contraste_pes=[]; privados=[]
for proceso in (2022,2023,2024,2025):
    periodo=proceso-1
    accepted_counter=collections.Counter((identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV']),codigo_derivado(r['COD_UNICO_OBT_TIT'])) for _,r in accepted[periodo])
    by_code=collections.Counter()
    for (ident,code),n in accepted_counter.items(): by_code[code]+=n
    published=collections.Counter()
    for (code,_),n in public[periodo].items(): published[code]+=n
    por_codigo=[{'codigo_sies':c,'pes5319':by_code[c],'publicado':published[c],'diferencia':by_code[c]-published[c]} for c in sorted(set(by_code)|set(published))]
    resumen={'proceso':proceso,'periodo_acad_titulacion':periodo,'pes5319_registros':sum(accepted_counter.values()),'publicado_registros':sum(published.values()),'pes_publicado_por_codigo':por_codigo,'estado_pes_publicacion':'CUADRA' if by_code==published else 'E','clase':'B reporte histórico PES; C comparación por código; no enlaza MRUN y RUT'}
    if proceso in cargas_individuales:
        cargados=collections.Counter((identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV']),codigo_derivado(r['COD_SIES_OBT_TIT'])) for r in cargas_individuales[proceso])
        solo_carga=cargados-accepted_counter; solo_pes=accepted_counter-cargados
        def aggregate(counter):
            codes=collections.Counter()
            for (_ident,code),n in counter.items(): codes[code]+=n
            return dict(sorted(codes.items()))
        causas=collections.Counter(); detalle_causas=collections.Counter()
        for (ident,code),n in solo_carga.items():
            same=[];body=[]
            for yy,rows in accepted.items():
                for _,r in rows:
                    other=identity(r['TIPO_DOCUMENTO'],r['NUM_DOCUMENTO'],r['DV'])
                    if ident==other: same.append((yy,codigo_derivado(r['COD_UNICO_OBT_TIT'])))
                    elif ident and other and ident[:2]==other[:2]: body.append((yy,codigo_derivado(r['COD_UNICO_OBT_TIT'])))
            periods=sorted({yy for yy,cc in same if cc==code and yy!=periodo})
            if periods:
                label='misma_identidad_y_codigo_en_otro_periodo_PES'
                detalle_causas[(label,code,','.join(map(str,periods)))]+=n
            elif same:label='misma_identidad_PES_con_otro_codigo'
            elif body:label='cuerpo_documento_PES_con_DV_distinto'
            else:label='documento_no_localizado_en_PES'
            causas[label]+=n
        resumen.update({'carga_registros':sum(cargados.values()),'coinciden_rut_dv_codigo_registros':sum((cargados & accepted_counter).values()),'solo_carga_por_codigo':aggregate(solo_carga),'solo_pes_por_codigo':aggregate(solo_pes),'duplicados_exactos_en_carga':sum(n-1 for n in cargados.values() if n>1),'neto_carga_menos_pes':sum(cargados.values())-sum(accepted_counter.values()),'causas_observadas_solo_carga':dict(causas),'otros_periodos_por_codigo':[{'motivo':m,'codigo':cc,'periodos_pes':pp,'registros':nn} for (m,cc,pp),nn in sorted(detalle_causas.items())],'explicacion':'B/C comparación exacta y diferencias de período/DV observadas; E fundamento de incorporación, omisión o asignación temporal no acreditado. No se corrige fuente ni DV.'})
        privados.append({'proceso':proceso,'fuente_carga':titulos[proceso]['archivo'],'fuente_pes':str(pes5319),'solo_carga':[{'identidad':ident,'codigo':code,'registros':n} for (ident,code),n in solo_carga.items()],'solo_pes':[{'identidad':ident,'codigo':code,'registros':n} for (ident,code),n in solo_pes.items()]})
    else: resumen['carga_enviada']='E: archivo enviado del proceso 2025 no localizado; 5319 aporta registro histórico B, no copia del envío.'
    contraste_pes.append(resumen)
private_dir=Path('/Users/alexi/.local/share/ipss/matriz_cuadratura_totales_20261028'); private_dir.mkdir(parents=True,exist_ok=True)
(private_dir/'CONTRASTE_TITULACION_5319.json').write_text(json.dumps(privados,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
da_por_persona=collections.defaultdict(set); da_documentos=set()
ws=openpyxl.load_workbook(da,read_only=True,data_only=True)['Hoja1']; it=ws.iter_rows(values_only=True); headers=next(it)
for row in it:
    r=dict(zip(headers,row))
    try: persona=rut_normalizado(r.get('RUT'))
    except ValueError: continue
    da_documentos.add(persona)
    if r.get('CODCLI') and r.get('CODCARPR'): da_por_persona[persona].add((normalizar(r['CODCLI']),normalizar(r['CODCARPR'])))
dic=DiccionarioSiesSeguimiento(); enlaces=collections.defaultdict(set); observaciones_persona_anio=set()
if not dic.edicion.startswith('v20_'): raise ValueError('La edición activa no es v20')
cols=('persona','codcli','plan','anio','periodo','carrera','sede','jornada')
for row in dic.db.execute('SELECT persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones'):
    persona,codcli,plan,anio,periodo,carrera,sede,jornada=row
    if str(anio) not in ('2022','2023','2024','2025','2026'): continue
    observaciones_persona_anio.add((persona,str(anio)))
    if (normalizar(codcli),normalizar(carrera)) not in da_por_persona.get(persona,set()): continue
    try: q=dic.consultar(**dict(zip(cols,row)))
    except ValueError: continue
    m=re.fullmatch(r'I162S\d+C(\d+)J\d+V\d+',q.get('codigo_sies') or '')
    if m: enlaces[(persona,str(anio))].add(str(int(m.group(1))))
dic.close()
mat=[]
for year in range(2022,2027):
    x=pre[year]; total_ids={identity(r['TIPO_DOC'],r['N_DOC'],r['DV']) for r in mu[year]}; total_ids.discard(None)
    candidates=eligibles.get(year,[]); found=[identity(r['TIPO_DOC'],r['N_DOC'],r['DV']) for r,_ in candidates if identity(r['TIPO_DOC'],r['N_DOC'],r['DV']) in total_ids]
    counts=previo.get(year)
    if counts and len(candidates)!=counts['casos']: raise ValueError('Denominador H001 no concilia '+str(year))
    levels=[r for r in res['resumen_anual'] if r['ANIO']==year and r['ALCANCE']=='NIVEL_NO_ACREDITADO']
    other=sum(r['MU_TOTAL_FILAS'] for r in levels)
    if x['MU_TOTAL_FILAS']+other != len(mu[year]): raise ValueError('Alcance MU no concilia '+str(year))
    post=[r for r in res['resumen_anual'] if r['ANIO']==year and r['ALCANCE']=='Postítulo']
    post_total=sum(r['CSV_TOTAL'] for r in post)
    t=titulos.get(year); pub=sum(public[year-1].values())
    if t:
        t['cat_periodo_publicado']=year-1; t['registros_publicados']=pub; t['diferencia_carga_menos_publicacion']=t['registros']-pub
        pc=collections.Counter()
        for (code,_name),n in public[year-1].items(): pc[code]+=n
        t['comparacion_codigo']=[{'codigo_sies':c,'carga':t['por_codigo_obtenido'].get(c,0),'publicacion':pc.get(c,0),'estado':'E'} for c in sorted(set(t['por_codigo_obtenido'])|set(pc))]
        if year==2024:
            normalizados=collections.Counter()
            for c,n in t['por_codigo_obtenido'].items():
                nuevo='I'+c if re.fullmatch(r'162S\d+C\d+J\d+V\d+',c) else c
                normalizados[nuevo]+=n
            t['comparacion_codigo_normalizada']=[{'codigo_sies':c,'carga':normalizados.get(c,0),'publicacion':pc.get(c,0),'diferencia':normalizados.get(c,0)-pc.get(c,0),'estado':'E'} for c in sorted(set(normalizados)|set(pc))]
            t['control_prefijo']={'codigos_modificados_en_derivado':sum(n for c,n in t['por_codigo_obtenido'].items() if re.fullmatch(r'162S\d+C\d+J\d+V\d+',c)),'neto_antes':t['diferencia_carga_menos_publicacion'],'neto_despues':sum(normalizados.values())-sum(pc.values()),'diferencia_formato':'B/C: dos diferencias inversas se anulan al normalizar prefijo; no demuestra igualdad individual.'}
    mat.append({'anio':year,'mu_sies':{'mu_filas':len(mu[year]),'mu_pregrado_filas':x['MU_TOTAL_FILAS'],'mu_nivel_no_acreditado_filas':other,'vig1_pregrado':x['MU_VIG1'],'vig0_pregrado':x['MU_VIG0'],'publicado_pregrado':x['CSV_TOTAL'],'publicado_postitulo':post_total,'publicado_institucional':x['CSV_TOTAL']+post_total,'diferencia_publicado_menos_vig1':x['DIF_VIG1_NETA_UNION'],'estado':'CUADRA' if x['DIF_VIG1_NETA_UNION']==0 else 'E','fuente':'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/RESULTADOS.json','nota':'2025 y 2026: diferencia neta observada; causa individual pendiente.'},'retencion_mu':{'matriculas_mu':len(mu[year]),'personas_mu_llave_comparable':len(total_ids),'candidatos_primer_anio_filas':sum(exclusiones[year].values()) if counts else None,'motivos_exclusiones_filas':dict(exclusiones[year]) if counts else None,'elegibles_h001_filas':len(candidates) if counts else None,'h001_en_mu_con_llave_comparable_filas':len(found) if counts else None,'estado':'CUADRA' if counts and len(found)==len(candidates) else 'E','nota':'Candidatos son registros con año y semestre de origen compatibles; partición por primer motivo según implementación H001. Unidad filas.'},'titulacion_publicada':{'cat_periodo':year-1,'registros':pub,'carga':t['registros'] if t else None,'estado':'E','nota':'Alineación t↔t−1 observada, no se acredita como norma. Código agregado no enlaza personas con MRUN.'},'titulacion_mu':t or {'estado':'E','nota':'Carga individual del proceso no acreditada en esta ejecución.'},'datos_alumnos_mu':{'matriculas_mu':len(mu[year]),'estado':'E','nota':'Falta enlace RUT+DV, CODCLI y carrera. No se usa coincidencia por cuerpo de documento.'}})
for entry in mat:
    year=entry['anio']; coverage=collections.Counter()
    for r in mu[year]:
        ident=identity(r['TIPO_DOC'],r['N_DOC'],r['DV']); persona=None
        if ident and ident[0]=='R':
            try: persona=rut_normalizado(ident[1]+'-'+ident[2])
            except ValueError: pass
        if persona not in da_documentos:
            coverage['no_localizado']+=1
            if not persona: coverage['no_localizado_sin_rut_dv_comparable']+=1
        elif normalizar(r['COD_CAR']) in enlaces.get((persona,str(year)),set()): coverage['rut_dv_y_carrera']+=1
        else: coverage['solo_rut_dv']+=1
    if sum(coverage[k] for k in ('rut_dv_y_carrera','solo_rut_dv','no_localizado'))!=len(mu[year]): raise ValueError('Cobertura DA no concilia')
    entry['datos_alumnos_mu']={'matriculas_mu':len(mu[year]),'rut_dv_y_carrera':coverage['rut_dv_y_carrera'],'solo_rut_dv':coverage['solo_rut_dv'],'no_localizado':coverage['no_localizado'],'no_localizado_sin_rut_dv_comparable':coverage['no_localizado_sin_rut_dv_comparable'],'estado':'E','nota':'RUT+DV exacto; carrera por CODCLI y carrera UMAS de DA, contexto del mismo año y código documental o D aprobado en diccionario v20. Solo documento incluye no acreditado y carrera distinta. No localizado incluye documentos sin RUT+DV comparable; no demuestra inexistencia del expediente. No evalúa vigencia.'}
    family_coverage=collections.Counter(); sin_observacion_2026=0; sin_mapeo_por_familia=collections.Counter()
    for r in mu[year]:
        ident=identity(r['TIPO_DOC'],r['N_DOC'],r['DV']); persona=None
        if ident and ident[0]=='R':
            try: persona=rut_normalizado(ident[1]+'-'+ident[2])
            except ValueError: pass
        if persona not in da_documentos:
            family_coverage['no_localizado']+=1
            if not persona: family_coverage['sin_rut_dv_comparable']+=1
        else:
            family='I162S{}C{}J{}'.format(*(normalizar(r[k]) for k in ('COD_SED','COD_CAR','JOR')))
            candidates=familias.get(family,set()); codes={c for _,c in da_por_persona[persona]}
            if not candidates:
                family_coverage['familia_sin_mapeo']+=1
                sin_mapeo_por_familia[family]+=1
            elif not codes: family_coverage['sin_codcarpr_en_da']+=1
            elif codes & candidates: family_coverage['rut_dv_y_carrera']+=1
            else: family_coverage['codcarpr_fuera_familia']+=1
        if year==2026 and persona in da_documentos and normalizar(r['COD_CAR']) not in enlaces.get((persona,str(year)),set()) and (persona,str(year)) not in observaciones_persona_anio: sin_observacion_2026+=1
    # No se debe mezclar ausencia de CODCARPR en DA con familia sin mapeo.
    if family_coverage['sin_codcarpr_en_da']: raise ValueError('Hay documento sin CODCARPR; requiere categoría adicional')
    if sum(family_coverage[k] for k in ('rut_dv_y_carrera','codcarpr_fuera_familia','familia_sin_mapeo','no_localizado'))!=len(mu[year]): raise ValueError('Categorías familia no concilian')
    if sum(sin_mapeo_por_familia.values())!=family_coverage['familia_sin_mapeo']: raise ValueError('Desglose familia sin mapeo no concilia')
    entry['cobertura_familia']={'matriculas_mu':len(mu[year]),**dict(family_coverage),'sin_observacion_diccionario_2026_entre_no_respaldados':sin_observacion_2026 if year==2026 else None,'estado':'B/C/E','nota':'Candidatos según grupos y relaciones operativas del maestro 2026; no acreditan plan, vigencia temporal ni atribución individual. Fuera del conjunto no prueba por sí sola cambio de carrera.'}
    entry['cobertura_familia']['familias_sin_mapeo']=[{'anio':year,'familia_sies':f,'matriculas':n,'clase':'B/C; E equivalencia pendiente'} for f,n in sorted(sin_mapeo_por_familia.items())]
    if year==2025:
        entry['mu_sies']['estado']='CUADRA'
        entry['mu_sies']['nota']='SIES registró como matriculadas las 73 VIG 0 (precarga AC 2026). B: todas con mismo documento/DV, código y VIGENCIA 1 en precarga. La causa normativa sigue E.'
        entry['mu_sies']['contraste_precarga_ac2026']={'clase':'B datos observados; C cruce; E fundamento normativo','fuente':str(ac2026),'sha256':hashfile(ac2026),'mu_vig1':2298,'mu_vig0':73,'vig1_en_ac_mismo_codigo_vigencia1':ac_counts['mu_vig_1_en_ac_vigencia_1'],'vig0_en_ac_mismo_codigo_vigencia1':ac_counts['mu_vig_0_en_ac_vigencia_1'],'sin_coincidencia_univoca':ac_counts['sin_coincidencia_univoca_vigencia_1'],'filas_precarga':len(ac_rows),'llaves_precarga':len(ac_index),'detalle_privado':str(ac_private),'detalle_sha256':hashfile(ac_private)}
    if year==2026:
        entry['retencion_mu']['estado']='NO APLICA AÚN'
        entry['retencion_mu']['nota']='Requiere MU 2027 para observar t+1; H001 no calcula esta cohorte en esta ejecución.'
catalogo_fuentes={'mu':str(base),'mu_2021':str(mu21),'catalogo_h001':str(diagnostico),'h001_agregado':str(agg),'publicacion_titulados':str(publico),'glosario_titulados':str(glosario),'datos_alumnos':str(da),'grupos_carrera':str(grupos_path),'maestro_carreras':str(maestro_path),'catalogo_fuentes':'data/catalogo_fuentes/CATALOGO_FUENTES.json','diccionario_activo':'data/diccionario_sies_seguimiento/activo.json','inventario_titulacion':'outputs/inventario_busquedas_titulacion_20261026/INFORME.md','conciliacion_mu_sies':'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/RESULTADOS.json','regla_h001':'manifests/milestones/H001-RETENCION-IPSS162/README.md','implementacion_h001':'common/analisis_desercion/h001.py','puente':'procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json'}
result={'estado':'PARCIAL_CON_PENDIENTES','clases':'A oficial; B observado; C cálculo; D decisión; E pendiente','fuentes':{k:{'ruta':v,'sha256':hashfile(v if Path(v).is_absolute() else ROOT/v)} for k,v in catalogo_fuentes.items()},'matriz':mat,'titulados_publicados_por_codigo':[{'anio_publicacion':a,'codigo_sies':code,'carrera':name,'registros':n} for a in sorted(public) for (code,name),n in sorted(public[a].items())], 'pendientes':['Alineación t↔t−1 de titulación observada B; regla escrita no localizada en esta ejecución.','Inventario de búsquedas de titulación 20261026 revisado: describe scripts, no acredita carga de proceso 2025; carácter final del respaldo 2024 pendiente.','Titulación y publicación: diferencias por código no explicadas; MRUN no permite enlace por persona.','DATOSDEALUMNOS_12159 figura en catálogo y descriptor v20 con hash e idéntica copia; no hay fecha de extracción ni evidencia de que sea el extracto más reciente.','Copia antigua del consolidado cfcf9099… no utilizada; fuente única OneDrive 70758082…']}
result['fuentes']['pes5319']={'ruta':str(pes5319),'sha256':hashfile(pes5319)}
result['fuentes']['precarga_ac2026']={'ruta':str(ac2026),'sha256':hashfile(ac2026),'encoding':'latin1','delimitador':';','clase':'B precarga SIES; no altera definición VIG MU'}
result['fuentes']['instructivo_titulacion_2026']={'ruta':str(manual),'sha256':hashfile(manual),'paginas':[3,6],'clase':'A','ventana':'1-mar-2025 a 28-feb-2026; captura 2026, Titulados 2025'}
result['contraste_pes5319']=contraste_pes
result['detalle_privado']={'ruta':str(private_dir/'CONTRASTE_TITULACION_5319.json'),'sha256':hashfile(private_dir/'CONTRASTE_TITULACION_5319.json'),'publicable':False}
result['pendientes']=[x for x in result['pendientes'] if not x.startswith('Alineación')]
result['pendientes'].append('A: ventana 2026 escrita en instructivo págs. 3 y 6. Ventanas de procesos históricos corroboradas por el reporte y rótulos B; no se extrapola norma 2026 a otros manuales.')
result['brecha_mu2026']={'estado':'E','valor_conservado':226,'investigacion_realizada':False,'fuente_mrun_ipss_disponible_hasta':2025,'requisito':'Fuente SIES individual MU 2026: descarga lo cargado PES o precarga AC 2027; metadato de año y hash obligatorios','hipotesis':'E: algunos VIG 0 de nuestra MU 2026 podrían figurar matriculados en SIES, como se observa en 2025; no se extrapolan 73 ni 960 a retenidos ni se corrigen tasas.','respaldo_hipotesis':'B cruce MU 2025 con precarga AC 2026: 73/73 VIG 0 aparecen con VIGENCIA 1','metodo_preparado':'metodo_mu2026.py; sólo 48 códigos con diferencia; VIG 1 nuestra / VIG 0 nuestra / no está en nuestra base; no ejecutado con fuente real.'}
result['brecha_mu2026']['metodo_sha256']=hashfile(OUT/'metodo_mu2026.py')
rotulo_ac2027='No existe aún (D, Alexi): el proceso AC 2027 ocurre después de MU 2027 (abril–mayo 2027); su precarga contendrá la matrícula 2026 registrada por SIES'
result['brecha_mu2026']['precarga_ac2027_disponibilidad']={'clase':'D rótulo aprobado por Alexi; B/C búsqueda local','fecha_busqueda':'2026-10-28','resultado':rotulo_ac2027,'observacion_busqueda':'No localizada en catálogos, OneDrive Enviados/Avance Curricular, Descargas ni Escritorio; no existe carpeta 2027 en el ámbito OneDrive revisado.','fecha_oficial':None,'metodo_ejecutado':False}
for nombre in ('BUSQUEDA_DESCARGA_PES_MU2026','BUSQUEDA_PRECARGA_AC2027','DICTAMEN_LIBROS_Y_CARGAS_MU2026','PREPARACION_CARGAS_ACUMULATIVAS_MU2026'):
    p=OUT/(nombre+'.json')
    if p.exists():result.setdefault('informes_busqueda_y_dictamen',{})[nombre]={'ruta':str(p),'sha256':hashfile(p),'clase':'B/C evidencia; D rótulo; E atribución y reconstrucción pendientes'}
dictamen_path=OUT/'DICTAMEN_LIBROS_Y_CARGAS_MU2026.json'
if dictamen_path.exists():
    dictamen=json.loads(dictamen_path.read_text())
    result['brecha_mu2026']['compatibilidad_abf_abril']=dictamen['comprobacion_abril']['compatibilidad_por_codigo']
c35=collections.Counter()
for r in mu[2022]:
    if (normalizar(r['COD_SED']),normalizar(r['COD_CAR']),normalizar(r['JOR']))==('2','35','4'):
        ident=identity(r['TIPO_DOC'],r['N_DOC'],r['DV'])
        if ident and ident[0]=='R':
            pe=rut_normalizado(ident[1]+'-'+ident[2]); c35.update({c for _,c in da_por_persona.get(pe,set())})
result['revision_c35j4']={'anio':2022,'familia':'I162S2C35J4','codcarpr_observados_en_personas_da':dict(c35),'estado':'E','nota':'Oferta histórica identifica Técnico en Análisis de Sistemas, pero observar otros expedientes actuales no acredita equivalencia histórica. No se agrega familia a partir de nombre ni RUT.'}
assert all(sum(x['registros'] for x in result['titulados_publicados_por_codigo'] if x['anio_publicacion']==y)==sum(public[y].values()) for y in public)
assert total_publico==3504
(OUT/'MATRIZ_CUADRATURA_TOTALES_2022_2026.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Matriz de cuadratura 2022–2026','', 'B/C: datos observados y cálculos; E: pendiente. H001 cuenta filas; validar unicidad antes de llamar personas.','', '| Año | MU filas | Pregrado + nivel no acreditado | VIG1 / VIG0 pregrado | SIES pregrado + postítulo | Brecha pregrado | H001 candidatos / elegibles (filas) | Titulación carga / SIES t−1 (registros) | Respaldo de código único v20 / solo RUT / no localizado |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
for x in mat:
    m=x['mu_sies'];h=x['retencion_mu'];t=x['titulacion_publicada'];d=x['datos_alumnos_mu']
    lines.append(f"| {x['anio']} | {m['mu_filas']} | {m['mu_pregrado_filas']} + {m['mu_nivel_no_acreditado_filas']} | {m['vig1_pregrado']} / {m['vig0_pregrado']} | {m['publicado_pregrado']} + {m['publicado_postitulo']} | {m['diferencia_publicado_menos_vig1']} | {h['candidatos_primer_anio_filas'] if h['candidatos_primer_anio_filas'] is not None else 'No aplica aún'} / {h['elegibles_h001_filas'] if h['elegibles_h001_filas'] is not None else 'E'} | {t['carga'] if t['carga'] is not None else 'E'} / {t['registros']} | {d['rut_dv_y_carrera']} / {d['solo_rut_dv']} / {d['no_localizado']} |")
lines += ['', 'La última columna conserva la medición anterior denominada respaldo de código único en v20: exige código en v20 pero compara solo su componente C con MU, por lo que no acredita que el código completo coincida. No es la cobertura de carrera ni indica vigencia.','', '**MU 2025: SIES registró como matriculadas las 73 VIG 0 (precarga AC 2026).** [B/C] Las 2.298 VIG 1 y las 73 VIG 0 coinciden por documento+DV y código con VIGENCIA 1 en AC 2026 (2.371/2.371). Para documentos P se conserva el tipo documental y el DV original, incluso vacío; no se inventa RUT. La causa normativa continúa E: VIGENCIA de AC y VIG de MU pertenecen a procesos distintos. H001 2026: NO APLICA AÚN; requiere MU 2027.', '', '## Cobertura por familia SIES y CODCARPR de Datos Alumnos', '', '| Año | RUT+DV y carrera candidata | RUT+DV, CODCARPR fuera de candidatos | RUT+DV sin familia mapeada | No localizado | Sin RUT+DV comparable (incluido en no localizado) |', '|---|---:|---:|---:|---:|---:|']
for x in mat:
    f=x['cobertura_familia']; lines.append(f"| {x['anio']} | {f.get('rut_dv_y_carrera',0)} | {f.get('codcarpr_fuera_familia',0)} | {f.get('familia_sin_mapeo',0)} | {f.get('no_localizado',0)} | {f.get('sin_rut_dv_comparable',0)} |")
lines += ['', 'Las equivalencias son candidatos de grupos existentes y relaciones operativas 2026 del maestro. No acreditan plan ni vigencia histórica; una carrera fuera del conjunto puede deberse a cobertura incompleta del catálogo. No localizado incluye documentos no comparables.']
lines += ['', '### Matrículas en familias sin mapeo — desglose agregado', '', '| Año MU | Familia SIES | Matrículas | Clase |', '|---|---|---:|---|']
for x in mat:
    for r in x['cobertura_familia']['familias_sin_mapeo']:
        lines.append(f"| {r['anio']} | {r['familia_sies']} | {r['matriculas']} | B/C; equivalencia E |")
lines += ['', 'Nueva edición de grupos 20261028: agrega sólo tres familias CO. Familia sin mapeo en 2026: 73 → 0. Las 3 matrículas C35J4 de 2022 siguen pendientes; no se modifica el diccionario personal.']
f=next(x['cobertura_familia'] for x in mat if x['anio']==2026)
lines += [f"En 2026, entre las matrículas sin respaldo v20, {f['sin_observacion_diccionario_2026_entre_no_respaldados']} pertenecen a personas sin ninguna observación del diccionario en 2026; no se afirma que la causa sea exclusivamente PROMEDIOS."]
lines += ['', '## Diferencias de titulación por código (carga menos publicación)', '', '| Proceso | Código SIES | Carga | Publicación | Diferencia | Estado |', '|---|---|---:|---:|---:|---|']
for y in (2023,2024):
    for z in titulos[y]['comparacion_codigo']:
        if z['carga']!=z['publicacion']: lines.append(f"| {y} | {z['codigo_sies'] or '(vacío)'} | {z['carga']} | {z['publicacion']} | {z['carga']-z['publicacion']} | E |")
lines += ['', 'En 2024 se observó `162S2C47J1V1` sin I y una diferencia inversa para `I162S2C47J1V1`: al normalizar el prefijo únicamente en el derivado se anulan estas dos diferencias por código [B/C]. No demuestra igualdad individual. La diferencia neta del proceso no cambia. El resto permanece E.', '', '| Proceso 2024: código derivado | Carga normalizada | Publicación | Diferencia | Estado |', '|---|---:|---:|---:|---|']
for z in titulos[2024]['comparacion_codigo_normalizada']:
    if z['diferencia']: lines.append(f"| {z['codigo_sies']} | {z['carga']} | {z['publicacion']} | {z['diferencia']} | E |")
lines += ['', 'Los motivos H001 se encuentran en el JSON: cada fila cuenta una vez por primer motivo aplicable. Instructivo Titulación Unificada 2026, págs. 3 y 6 [A]: ventana 1-mar-2025 a 28-feb-2026, denominada Titulados 2025. No se extrapola el manual 2026 para afirmar normativas históricas. El reporte PES 5319 permite comprobar el período académico por registro [B]. El respaldo 2024 mantiene alcance pendiente. No existe enlace individual RUT–MRUN.', '', '## Reporte PES 5319 frente a publicación', '', '| Proceso | PERIODO_ACAD_TITULACION | PES 5319 | Publicación | Coincidencia por código |', '|---|---:|---:|---:|---|']
for x in contraste_pes:lines.append(f"| {x['proceso']} | {x['periodo_acad_titulacion']} | {x['pes5319_registros']} | {x['publicado_registros']} | {x['estado_pes_publicacion']} |")
lines += ['', '## Cargas frente a PES 5319: RUT+DV y código derivado', '', '| Proceso | Carga | PES | Coinciden | Sólo carga | Sólo PES | Duplicados exactos en carga | Neto |', '|---|---:|---:|---:|---:|---:|---:|---:|']
for x in contraste_pes:
    if 'carga_registros' in x: lines.append(f"| {x['proceso']} | {x['carga_registros']} | {x['pes5319_registros']} | {x['coinciden_rut_dv_codigo_registros']} | {sum(x['solo_carga_por_codigo'].values())} | {sum(x['solo_pes_por_codigo'].values())} | {x['duplicados_exactos_en_carga']} | {x['neto_carga_menos_pes']} |")
lines += ['', 'El JSON desglosa los registros no coincidentes por código; sus identificadores se guardan exclusivamente en la salida privada. En 2024, cuatro registros del respaldo tienen la misma identidad y código en otro período PES; otro registro presenta cuerpo de documento coincidente pero DV distinto. No se decide cuál DV corregir ni se altera una fecha. Esto localiza el neto +4; el fundamento institucional del desfase sigue E. En 2023, los 283 registros enviados están en el histórico, que agrega 11; el origen del envío adicional no se acredita. Proceso 2025: 5319 contiene 270 registros históricos [B]; no se localizó el archivo enviado.', '', 'Brecha MU 2026 = 226 [E]. Método preparado y no ejecutado sobre datos reales: `metodo_mu2026.contrastar_fuente` requiere descarga individual de lo cargado en PES MU 2026 o precarga AC 2027 con año de matrícula 2026, hash y adaptador de columnas acreditados. Clasifica sólo los 48 códigos pregrado con diferencia como VIG 1 nuestra, VIG 0 nuestra o matrícula documento/código ausente en nuestra base. El caso 2025 respalda investigar esta hipótesis, sin extrapolarlo a 2026. El análisis de perfiles MRUN queda como alternativa cuando exista microdato 2026.', '', 'Pendientes:']+[f'- {p}' for p in result['pendientes']]
lines += ['', '## Titulación frente a matrícula: comparación preliminar por persona', '', '| Proceso | Registros de carga observada | Personas con documento comparable | Presentes en MU t−1 | Presentes en MU t |', '|---|---:|---:|---:|---:|']
for y,t in titulos.items():
    a=t['personas_con_mu_por_anio']; lines.append(f"| {y} | {t['registros']} | {t['personas_con_llave_comparable']} | {a[str(y-1)] if a[str(y-1)] is not None else 'E'} | {a[str(y)]} |")
lines += ['', 'B/C: presencias por documento, sin atribución de expediente. MU 2021 procede del respaldo histórico inventariado, separado de la base 142342.']
(OUT/'MATRIZ_CUADRATURA_TOTALES_2022_2026.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
with (OUT/'MATRIZ_CUADRATURA_TOTALES_2022_2026.md').open('a',encoding='utf-8') as f:
    f.write('\n'+rotulo_ac2027+'. No se presenta como calendario oficial A. B/C: no localizada en los ámbitos revisados. Método 2026 no ejecutado.\n')
    f.write('\n## Búsquedas y dictamen de libros MU2026\n\n')
    for nombre in result.get('informes_busqueda_y_dictamen',{}):f.write(f'- [{nombre}]({nombre}.md): evidencia y hashes en el JSON homónimo.\n')
    audit_path=OUT/'DICTAMEN_LIBROS_Y_CARGAS_MU2026.json'
    if audit_path.exists():
        audit=json.loads(audit_path.read_text());a=audit['comprobacion_abril']
        c=a['compatibilidad_por_codigo']
        f.write(f"\nB/C: 06_DETALLE_TOTAL reproduce las 4.105 matrículas y Hoja1 las 2.379 filas históricas H001. ABF: SIRVE PARCIAL; {c['cubrible_total']}/{c['brecha_positiva']} = {c['compatibilidad_porcentaje']:.2f}% de la brecha positiva compatible con parte de las VIG0 vigentes en abril (aproximadamente 85%, C/E); no acredita aceptación SIES. No se suman automáticamente las 459 candidatas.\n")
        f.write(f"\nGrupos disjuntos: {c['codigos_positivos_cubiertos_totalmente']} positivos cubiertos (4 exactos), {c['codigos_positivos_insuficientes']} insuficientes y {c['codigos_negativos']} negativos ({c['brecha_negativa']}). La brecha positiva {c['brecha_positiva']} más la negativa {c['brecha_negativa']} conserva la neta 226. Los 32 códigos con candidatas >= brecha incluyen los dos negativos.\n")
        f.write('\n### Pendientes E: 35 matrículas no cubiertas por candidatas de abril\n\n| Código | Brecha positiva | Candidatas | Cubrible | Sin cubrir |\n|---|---:|---:|---:|---:|\n')
        for r in c['no_cubiertas_por_codigo']:f.write(f"| {r['codigo_sies']} | {r['brecha_positiva']} | {r['candidatas']} | {r['cubrible']} | {r['sin_cubrir']} |\n")
        f.write('\nLas dos brechas negativas se detallan en el dictamen y no compensan las 35 pendientes positivas. E: reconstrucción no ejecutada. Las dos formulaciones originales eran equivalentes con I162 fijo; se preparan ahora L1 documento+código único y L2 gruesa documento+COD_CAR, sin sede, jornada ni versión (C/E). Si L1 reproduce mejor la publicación y el linaje confirma registros antiguos no sobrescritos, éstos serán una explicación candidata. Alexi descargará el Historial y el archivo cargado de cada carga Finalizado. No se usarán envíos locales. Fuentes, bases, denominadores y tasas intactos.\n')
def detectar(x, path=''):
    hits=[]
    if isinstance(x,dict):
        for k,v in x.items(): hits+=detectar(v,path+'/'+k)
    elif isinstance(x,list):
        for v in x: hits+=detectar(v,path+'[]')
    elif isinstance(x,str) and not any(k in path for k in ('sha256','archivo','ruta','fuente','nota','pendientes')):
        if re.fullmatch(r'\d{7,9}-?[0-9Kk]',x): hits.append(path)
    return hits
hits=detectar(result)
if hits: raise ValueError('Posible identificador en salida agregada')
qa={'estado':'PARCIAL_CON_PENDIENTES','hash_entradas_principales_verificado':True,'consolidado_one_drive_registros':total_publico,'diccionario_v20_componentes_y_base_verificados':True,'cobertura_da_tres_niveles_disjuntos_suma_mu':True,'cobertura_por_familia_cuatro_niveles_disjuntos_suma_mu':True,'prefijo_2024_derivado_no_altera_neto':titulos[2024]['control_prefijo']['neto_antes']==titulos[2024]['control_prefijo']['neto_despues'],'h001_elegibles_conciliados':True,'h001_particion_por_primer_motivo':True,'mu_pregrado_mas_no_acreditado_concilia':True,'suma_codigos_titulados_concilia':True,'escaneo_identificadores_sospechosos':len(hits),'limitacion_escaneo':'Patrón de identificador numérico en valores agregados; no equivale a certificación absoluta. Rutas, hashes y notas excluidas para evitar falsos positivos.','pendientes':result['pendientes']}
(OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Segunda comprobación: contraste de los cuatro archivos con identificadores
# observados en las entradas, sólo en memoria; no se publican coincidencias.
private_tokens=set(da_documentos)
for expedientes in da_por_persona.values():
    private_tokens.update(c for c,_ in expedientes if len(c)>=6)
for registros in mu.values():
    for r in registros:
        token=normalizar(r.get('N_DOC'))
        if len(token)>=6: private_tokens.add(token)
pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+ '|'.join(re.escape(t) for t in sorted(private_tokens,key=len,reverse=True)) +r')(?![A-Za-z0-9])')
files=('MATRIZ_CUADRATURA_TOTALES_2022_2026.md','MATRIZ_CUADRATURA_TOTALES_2022_2026.json','QA.json','construir_matriz.py')
privacy_hits=sum(sum(1 for _ in pattern.finditer((OUT/name).read_text(encoding='utf-8'))) for name in files)
if privacy_hits: raise ValueError('Se detectaron posibles identificadores de fuente en archivos de entrega; no publicar')
qa['desglose_familias_sin_mapeo_concilia']=True
qa['mu2025_precarga_ac2026']={'vig1_mismo_codigo_vigencia1':2298,'vig0_mismo_codigo_vigencia1':73,'sin_coincidencia':0,'qa':'PASS','causa_normativa':'E'}
qa['metodo_mu2026']={'estado':'PREPARADO_NO_EJECUTADO_CON_FUENTE_REAL','pruebas_sinteticas':'Ejecutar test_metodo_mu2026.py; no sustituye validación real','sha256':hashfile(OUT/'metodo_mu2026.py')}
qa['escaneo_cuatro_archivos_con_identificadores_de_fuentes']={'archivos':list(files),'coincidencias':privacy_hits,'metodo':'Identificadores observados en MU/DA por límites de token; sólo se publica el número de coincidencias.'}
(OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Matriz parcial generada; controles de suma aprobados; escaneo estructurado sin coincidencias.')

#!/usr/bin/env python3
"""H002j: catálogo de tipo por plan y prueba de sensibilidad; sin adjudicación."""
import sys,csv,json,re,hashlib,subprocess,sqlite3,argparse
from pathlib import Path
from collections import Counter,defaultdict
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;DATA=ROOT/'data/paridad_codigo_sies/regla_operativa_mu_v2'
sys.path.insert(0,str(ROOT/'outputs/regla_operativa_mu_20261029'))
import construir as old
sha,read,js,txt,family,pct,csvbytes,table=old.sha,old.read,old.js,old.txt,old.family,old.pct,old.csvbytes,old.table
PRIVATE=Path.home()/'.local/share/ipss/h002j_20261029'
FIVE=['I162S2C3J4','I162S2C76J4','I162S2C46J4','I162S2C1J4','I162S2C77J4']
LABEL={'1':'REGULAR','3':'CONTINUIDAD'}
MISSING={'SIN_ENLACE','PLAN_NO_OBSERVADO','PLAN_MULTIPLE_E',''}

def num(x):
    try:return float(x)
    except (TypeError,ValueError):return None

def determine(p, catalog):
    """Sin acceso a mayorías SIES ni a resultados individuales."""
    ds={num(x['semestres_calculados']) for x in p['conversion_si_regimen_PROMEDIOS'] if num(x['semestres_calculados']) is not None}
    duration=next(iter(ds)) if len(ds)==1 else None
    formal={(num(x['semestres']),txt(x['tipo_plan_codigo'])) for x in p['perfil_formal_H112B']}
    groups={(num(d),txt(t)) for g in p['perfiles_grupo_gobernado'] for d,t in g['perfiles']}
    ftypes={t for d,t in formal};gtypes={t for d,t in groups}
    candidates={t for d,t in formal if d==duration} if duration is not None else set()
    ramos_match=any(x['diferencia_listado_menos_5810']==0 for x in p['contraste_ramos_5810']) or any(x['diferencia']==0 for x in p['contraste_ramos_Permanencia'])
    if len(ftypes)==1 and ftypes<={'1','3'}:
        if duration is not None and not candidates:return 'E','PERFIL_FORMAL_DURACION_CONTRADICTORIA',duration
        return next(iter(ftypes)),'PERFIL_H112B_UNICO',duration
    if len(candidates)==1 and candidates<={'1','3'}:
        return next(iter(candidates)),'PERFIL_H112B_DESAMBIGUADO_POR_DURACION',duration
    compatible={t for d,t in groups if duration is None or d==duration}
    if len(compatible)==1 and compatible<={'1','3'}:
        return next(iter(compatible)),'PERFIL_GRUPO_GOBERNADO_COMPATIBLE',duration
    ct={txt(r['TIPO_PLAN_CARRERA']) for r in catalog if num(r['DURACION_ESTUDIOS'])==duration} if duration is not None else set()
    if ramos_match and len(ct)==1 and ct<={'1','3'}:
        return next(iter(ct)),'DURACION_Y_RAMOS_CON_CATALOGO_CANDIDATO',duration
    return 'E','EVIDENCIA_NO_UNIVOCA_O_INSUFICIENTE',duration

def residual(r, split, same_previous, change, offers, typ):
    flags=[]
    if change:flags.append('CAMBIO_DE_PLAN_REAL')
    if split or (r['grupo']=='ANTIGUO' and same_previous and r['predicho'] is not None and r['predicho']!=r['real']):flags.append('INCONSISTENCIA_DE_CARGA')
    if r['grupo']=='NUEVO' and r['real'] not in {c for c,t,v in offers if v=='1'}:flags.append('OFERTA_HISTORICA_NO_REFLEJA_CARGA')
    if typ=='E':flags.append('TIPO_PLAN_E')
    if not flags:flags.append('OTRA')
    return flags[0],flags

def main(check=False):
    sources=read(OUT/'FUENTES.json')
    for e in sources:
        if sha(e['ruta'])!=e['sha256']:raise ValueError('Fuente alterada: '+e['id'])
    src={e['id']:Path(e['ruta']) for e in sources};built={}
    def put(p,x):built[p]=js(x) if not isinstance(x,str) else x
    inputrows=read(src['privado_H002i']);links=read(src['enlaces_H002g']);lb={r['fila_fuente_mu']:r for r in links}
    profiles=read(src['outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json'])
    master=read(src['data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json'])
    offer=defaultdict(list);code_type={}
    for r in master['oferta_anual']:
        y=r['anio'];c=r['codigo_unico'];t=old.TYPE.get(r['tipo_plan_sies'],'E');v={'Vigente con estudiantes nuevos':'1','Vigente sin estudiantes nuevos':'2','No vigente':'3'}.get(r['vigencia'],'E')
        if y in range(2023,2027):offer[y,family(c)].append((c,t,v))
        code_type[y,c]=t
    dur=list(csv.DictReader(src['DURACION_ESTUDIOS.tsv'].open(),delimiter='\t'));durby=defaultdict(list)
    for r in dur:
        cs={r['CODCARPR_CANONICO']}|set(r['CODCARPR_ALIAS_LIST'].split('|'))
        for c in cs-{'','NAN'}:durby[c].append(r)
    formal={};cat=[];seen=set()
    for p in profiles['perfiles']:
        key=p['codcarpr'],p['CODPESTUD'],p['sede_umas'];assert key not in seen;seen.add(key)
        typ,method,duration=determine(p,durby[key[0]])
        record={'codcarpr':key[0],'plan_umas':key[1],'sede_umas':key[2],'tipo_plan':LABEL.get(typ,'E'),'tipo_codigo':typ,'clase':'C' if typ!='E' else 'E',
            'metodo':method,'duracion_diagnostica_semestres':duration,'ramos_listado':p['ramos_distintos'],
            'evidencia':{'fuente':'outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json','localizador':{'codcarpr':key[0],'CODPESTUD':key[1],'sede_umas':key[2]},
                'perfil_H112B':p['perfil_formal_H112B'],'perfil_grupos':p['perfiles_grupo_gobernado'],
                '5810':p['contraste_ramos_5810'],'Permanencia_sin_plan':p['contraste_ramos_Permanencia'],
                'duracion_regimen':p['conversion_si_regimen_PROMEDIOS'],'catalogo_duracion':sorted({(r['CODIGO_UNICO'],r['DURACION_ESTUDIOS'],r['TIPO_PLAN_CARRERA']) for r in durby[key[0]]})},
            'prefijo_C':'NO_USADO: hipótesis universal rechazada; perfiles evaluados individualmente',
            'ADMP_CADMP':'CODIGO_PENDIENTE_ALEXI' if key[0] in ('ADMP','CADMP') else 'NO_APLICA'}
        formal[key]=typ;cat.append(record)
    def context(r):
        link=lb[r['fila_mu']];sel=link['seleccion']
        return (r['codcarpr'],r['plan'],sel[2] if sel else '')
    for r in inputrows:
        k=context(r)
        if k not in seen and r['plan'] not in MISSING:
            seen.add(k);formal[k]='E';cat.append({'codcarpr':k[0],'plan_umas':k[1],'sede_umas':k[2],'tipo_plan':'E','tipo_codigo':'E','clase':'E','metodo':'SIN_PERFIL_CATALOGADO','duracion_diagnostica_semestres':None,'ramos_listado':None,'evidencia':{'fuente':'enlace anual H002g; no inventar perfil'},'prefijo_C':'NO_USADO','ADMP_CADMP':'CODIGO_PENDIENTE_ALEXI' if k[0] in ('ADMP','CADMP') else 'NO_APLICA'})
    # Mayoría sólo apoyo: no entra en determine ni en formal.
    support=defaultdict(Counter)
    for link in links:
        y=link['anio'];sel=link['seleccion']
        if y not in (2022,2024,2025) or not link['incluida'] or not sel:continue
        k=sel[1],link['plan'],sel[2];t=code_type.get((y,link['codigo_sies']),'E');support[k][t]+=1
    for p in cat:
        k=p['codcarpr'],p['plan_umas'],p['sede_umas'];sc=support[k];mx=max(sc.values(),default=0);tops=sorted(t for t,n in sc.items() if n==mx)
        p['apoyo_anclas_tipo_matriculas']=dict(sorted(sc.items()));p['mayoria_tipo_apoyo']=tops
        p['apoyo_vs_tipo']='NO_USADO_PARA_DECIDIR; '+('CONTRADICE' if len(tops)==1 and tops[0]!='E' and p['tipo_codigo'] not in ('E',tops[0]) else 'SIN_CONTRADICCION_MAYORITARIA' if tops else 'SIN_DATO')
    cat.sort(key=lambda p:(p['codcarpr'],p['plan_umas'],p['sede_umas']))
    result=[]
    for original in inputrows:
        r=dict(original);k=context(r);typ=formal.get(k,'E');types={typ} if typ!='E' else set()
        pred,why=old.predict(r['grupo'],set(r['previos']),offer[r['anio'],r['familia']],types)
        r.update(tipo_j=typ,predicho=pred,motivo=why,acierto=pred==r['real'],acierto_i=original['acierto'],predicho_i=original['predicho'])
        result.append(r)
    # Patrón mismo plan/cohorte/tipo/año, sin mezclar familias ni semestres.
    splitcodes=defaultdict(set);previous=defaultdict(list)
    for link in links:
        if link['identidad']:previous[tuple(link['identidad']),link['anio'],family(link['codigo_sies'])].append(link)
    def splitkey(r):return r['anio'],r['familia'],r['codcarpr'],r['plan'],tuple(lb[r['fila_mu']]['cohorte_sies']),r['tipo_j']
    for r in result:
        co=lb[r['fila_mu']]['cohorte_sies']
        if r['tipo_j']!='E' and r['plan'] not in MISSING and co[0] is not None:splitcodes[splitkey(r)].add(r['real'])
    residuals=[]
    for r in result:
        if r['grupo']=='OTRO' or r['acierto']:continue
        link=lb[r['fila_mu']];pe=tuple(r['identidad']) if r['identidad'] else None
        prior=previous.get((pe,r['anio']-1,r['familia']),[])
        oldplans={p['plan'] for p in prior};oldexp={p['seleccion'][0] if p['seleccion'] else None for p in prior}
        known=bool(prior) and not (oldplans&MISSING) and None not in oldexp and r['plan'] not in MISSING and r['expediente'] is not None
        same=known and oldplans=={r['plan']} and oldexp=={r['expediente']}
        change=r['cambio_plan_observado'] or r['cambio_expediente_observado']
        split=len(splitcodes[splitkey(r)])>1
        principal,flags=residual(r,split,same,change,offer[r['anio'],r['familia']],r['tipo_j'])
        r.update(causa_j=principal,indicadores_j=flags,reparto_mismo_plan_cohorte=split,antiguo_mismo_plan_expediente_comprobado=same)
        residuals.append(r)
    # Comparación mismos denominadores; OTRO sólo conteo.
    groups=old.metrics(result,['anio','grupo']);oldgroups=old.metrics(inputrows,['anio','grupo'])
    def compare(a,b,fields):
        by={tuple(r[k] for k in fields):r for r in b};rows=[]
        for r in a:
            prev=by[tuple(r[k] for k in fields)];assert r['filas_mu']==prev['filas_mu']
            rows.append({**{k:r[k] for k in fields},'filas_mu':r['filas_mu'],'aciertos_H002i':prev['aciertos'],'aciertos_H002j':r['aciertos'],
                         'acierto_H002i_pct':prev['acierto_pct'],'acierto_H002j_pct':r['acierto_pct'],'delta_pp':round(r['acierto_pct']-prev['acierto_pct'],6) if r['acierto_pct'] is not None else None,
                         'predicciones_H002i':prev['predicciones'],'predicciones_H002j':r['predicciones']})
        return rows
    comparison=compare(groups,oldgroups,['anio','grupo'])
    for r in comparison:
        if r['grupo']=='OTRO':r['acierto_H002i_pct']=None;r['acierto_H002j_pct']=None;r['delta_pp']=None
    evalj=[r for r in result if r['grupo']!='OTRO'];evali=[r for r in inputrows if r['grupo']!='OTRO']
    totals=compare(old.metrics(evalj,['anio']),old.metrics(evali,['anio']),['anio'])
    five=compare(old.metrics([r for r in evalj if r['familia'] in FIVE],['anio','familia','grupo']),old.metrics([r for r in evali if r['familia'] in FIVE],['anio','familia','grupo']),['anio','familia','grupo'])
    ft=compare(old.metrics([r for r in evalj if r['familia'] in FIVE],['anio','familia']),old.metrics([r for r in evali if r['familia'] in FIVE],['anio','familia']),['anio','familia'])
    causes=Counter(r['causa_j'] for r in residuals)
    rc=Counter((r['anio'],r['familia'],r['grupo'],r['causa_j'],r['real'],r['predicho'] or 'SIN_PREDICCION',r['tipo_j']) for r in residuals)
    rr=[dict(zip(['anio','familia','grupo','causa','codigo_informado','codigo_segun_regla','tipo_codigo'],k),filas=n,clase='C/E; patrón diagnóstico, no error probado') for k,n in sorted(rc.items())]
    incons=[r for r in rr if r['causa']=='INCONSISTENCIA_DE_CARGA']
    # Todos los indicadores de inconsistencia, aunque otra causa tenga prioridad.
    overlaps=Counter(flag for r in residuals for flag in r['indicadores_j'])
    ic=Counter((r['anio'],r['familia'],r['real'],r['predicho'] or 'SIN_PREDICCION') for r in residuals if 'INCONSISTENCIA_DE_CARGA' in r['indicadores_j'])
    fullinc=[dict(zip(['anio','familia','codigo_informado','codigo_segun_regla'],k),filas=n) for k,n in sorted(ic.items())]
    annualinc=defaultdict(lambda:{'filas':0,'codigos_segun_regla':set()})
    for r in incons:
        a=annualinc[r['anio'],r['familia']];a['filas']+=r['filas'];a['codigos_segun_regla'].add(r['codigo_segun_regla'])
    annualincrows=[{'anio':y,'familia':f,'filas':a['filas'],'codigos_segun_regla':sorted(a['codigos_segun_regla'])} for (y,f),a in sorted(annualinc.items())]
    offercheck=[]
    for r in rr:
        if r['grupo']=='NUEVO' and r['codigo_informado'] not in {c for c,t,v in offer[r['anio'],r['familia']] if v=='1'}:
            vs=[v for c,t,v in offer[r['anio'],r['familia']] if c==r['codigo_informado']]
            offercheck.append(dict(r,vigencia_extraccion=vs,fuente='oferta_anual; histórico del 05-06-2026; rutas y hashes en MANIFEST',carga_anual='E: no localizada en alcance documentado',busqueda='outputs/regla_operativa_mu_v2_20261029/BUSQUEDA_CARGAS_OFERTA.json'))
    # Simulación reutiliza V06/H002 inmutables de H002i, enriquecida por plan.
    simi=read(src['data/paridad_codigo_sies/regla_operativa_mu/SIMULACION_NUEVOS_2027.json'])['filas']
    htable=read(src['data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json'])['filas'];hby={r['codigo_unico']:r for r in htable if r['anio']==2027}
    sf=[]
    for s in simi:
        allcodes=set(s['codigos_candidatos_nuevos'])|set(s['codigos_sin_nuevos'])|set(s['H002_E'])|set(s['H002_para_nuevos'])
        # Las familias con ambas clases de plan se informan aunque una no admita nuevos.
        types={hby[c]['tipo_plan_codigo'] for c in allcodes if c in hby}
        if not {'1','3'}<=types:continue
        cars={ca for c in allcodes if c in hby for ca in hby[c]['codcarpr']}
        for typ in ('1','3'):
            opt=next((x['codigos'] for x in s['opciones_por_tipo'] if x['tipo_plan']==typ),[])
            plans=[p['codcarpr']+' / '+p['plan_umas']+' / '+p['sede_umas'] for p in cat if p['codcarpr'] in cars and p['tipo_codigo']==typ]
            declared=sorted(c for c in allcodes if c in hby and hby[c]['tipo_plan_codigo']==typ and hby[c]['version_para_nuevos_2027']=='sí')
            unknown=sorted(c for c in allcodes if c in hby and hby[c]['tipo_plan_codigo']==typ and hby[c]['version_para_nuevos_2027']=='E')
            state='NO_COMPARABLE_E' if unknown or len(opt)>1 else 'COINCIDE' if sorted(opt)==declared else 'DIFIERE'
            sf.append({'familia':s['familia'],'tipo_plan':LABEL[typ],'codigos_nuevos_2027':opt,'versiones':[re.search(r'V(\d+)$',c)[1] for c in opt],
                'planes_catalogados_tipo':plans,'H002_para_nuevos':declared,'H002_E':unknown,'comparacion':state,
                'ADMP_CADMP':'PENDIENTE_ALEXI' if s['familia']=='I162S2C83J4' else 'NO_APLICA','clase':'C/E; V06 preparada, sin adjudicación'})
    # Universo potencial antiguo: toda MU2026 de cinco familias, no sólo ANTIGUO de retrospectiva.
    current=Counter()
    for r in result:
        if r['anio']!=2026 or r['familia'] not in FIVE:continue
        actualtype=code_type.get((2026,r['real']),'E');t=r['tipo_j']
        state='NO_COMPARABLE_E' if 'E' in (t,actualtype) else 'INCOMPATIBLE_CON_TIPO' if t!=actualtype else 'COMPATIBLE_CON_TIPO'
        current[r['familia'],state,r['real'],LABEL.get(t,'E')]+=1
    old2027=[dict(zip(['familia','estado','codigo_actual','tipo_plan_umas'],k),matriculas=n,clase='C/E; no decidir corregir ni conservar') for k,n in sorted(current.items())]
    # SQL independiente de sumas y denominadores.
    db=sqlite3.connect(':memory:');db.execute('create table r(anio int, grupo text, familia text, hit int, oldhit int)')
    db.executemany('insert into r values(?,?,?,?,?)',[(r['anio'],r['grupo'],r['familia'],int(r['acierto']),int(r['acierto_i'])) for r in result])
    sq=db.execute('select anio,grupo,count(*),sum(hit),sum(oldhit) from r group by anio,grupo order by anio,grupo').fetchall()
    assert sq==[(r['anio'],r['grupo'],r['filas_mu'],r['aciertos_H002j'],r['aciertos_H002i']) for r in comparison];db.close()
    assert all(r['predicho']==r['predicho_i'] for r in result if r['grupo']!='NUEVO')
    assert sum(not r['acierto'] for r in inputrows if r['grupo']!='OTRO')==830
    assert sum(not r['acierto'] for r in inputrows if r['grupo']!='OTRO' and r['familia'] in FIVE)==556
    assert len(result)==9162 and sum(causes.values())==sum(not r['acierto'] for r in evalj)
    baseline=read(src['data/paridad_codigo_sies/regla_operativa_mu/METRICAS_REGLA_2023_2026.json'])
    assert [(r['anio'],r['grupo'],r['filas_mu'],r['aciertos_H002i']) for r in comparison]==[(r['anio'],r['grupo'],r['filas_mu'],r['aciertos']) for r in baseline['por_grupo']]
    missing361=Counter((r['codcarpr'],r['plan'],tuple(r['types'])) for r in inputrows if r['causa']=='TIPO_PLAN_NO_DETERMINABLE')
    assert sum(missing361.values())==361
    summary={'clase':'C/E','estado':'CANDIDATA_NO_ACTIVA','planes_por_tipo':dict(Counter(p['tipo_plan'] for p in cat)),'planes_catalogados':len(cat),'por_grupo':comparison,'totales':totals,'cinco_familias':five,'cinco_familias_total':ft,'residuales_causa_principal':dict(causes),'indicadores_no_excluyentes':dict(overlaps),'simulacion_2027':dict(Counter(s['comparacion'] for s in sf)),
        'rectificacion_diagnostico':'H002i usó perfil formal H112B vacío o múltiple, no FOR_ING_ACT. Prefijo C universal rechazado en H002c; no aplicado aquí.',
        '361_origen':[{'codcarpr':k[0],'plan':k[1],'tipos_H112B':list(k[2]),'filas':n} for k,n in sorted(missing361.items())]}
    put(DATA/'TIPO_PLAN_POR_PLAN_UMAS.json',{'filas':cat,'conteos':summary['planes_por_tipo']});put(DATA/'TIPO_PLAN_POR_PLAN_UMAS.csv',csvbytes(cat))
    put(DATA/'METRICAS_H002i_H002j.json',summary);put(DATA/'METRICAS_H002i_H002j.csv',csvbytes(comparison))
    put(DATA/'CINCO_FAMILIAS.csv',csvbytes(five));put(DATA/'CINCO_FAMILIAS_TOTAL.csv',csvbytes(ft))
    put(DATA/'SIMULACION_NUEVOS_2027.json',sf);put(DATA/'SIMULACION_NUEVOS_2027.csv',csvbytes(sf))
    put(OUT/'CONTRASTE_OFERTA_RESIDUALES.json',offercheck);put(OUT/'INCONSISTENCIAS_FAMILIA_ANIO.csv',csvbytes(annualincrows));put(OUT/'RESIDUALES.json',rr);put(OUT/'INCONSISTENCIA_DE_CARGA.csv',csvbytes(incons));put(OUT/'INDICADORES_INCONSISTENCIA_NO_EXCLUYENTES.csv',csvbytes(fullinc))
    put(OUT/'ANTIGUOS_2027_CINCO_FAMILIAS.json',old2027);put(OUT/'ANTIGUOS_2027_CINCO_FAMILIAS.csv',csvbytes(old2027))
    notes='''
D/C · Regla CANDIDATA, no activa. Unidades: filas de matrícula; ninguna tasa oficial se modifica. Denominador de acierto incluye no predecibles y conserva todos los valores VIG. OTRO no entra al total evaluable. No se modifica la regla de antiguos; el tipo UMAS sólo desempata varias versiones vigentes para nuevos.

C/E · El tipo se deriva de evidencia de plan específica. No se usa FOR, nombre ni prefijo como sustituto del tipo. Duración desde niveles/regímenes sigue siendo conversión diagnóstica C, no certificación curricular. Permanencia carece de plan; sus ramos se usan como contraste agregado. La mayoría SIES en anclas sólo informa apoyo/contradicción, nunca selecciona el tipo. No llenar un plan anual desconocido por el plan único actual de la carrera.

C/E · INCONSISTENCIA_DE_CARGA es el patrón diagnóstico solicitado, no prueba de error ni autorización de rectificación. Cambio observado de expediente/plan no acredita su causa administrativa. Si falta cualquiera de los dos datos de un año, no se afirma que el antiguo conservó ambos. La causa principal usa precedencia cambio observado → inconsistencia → oferta → tipo E → otra; los indicadores superpuestos se conservan aparte. Para oferta histórica, no se localizó carga institucional 2023–2026 en las carpetas revisadas: ver BUSQUEDA_CARGAS_OFERTA.json. No se atribuye al SIES una regla distinta ni se certifica que el histórico fuese el catálogo usado al cargar.

C/E · La simulación 2027 usa V06 preparada y compara con H002 sin alterarlo. NO_COMPARABLE_E conserva sus pendientes. ADMP/CADMP sigue pendiente de Alexi aunque se describa el tipo; no se aprueba ningún código. Antiguos potenciales 2027 son filas MU2026, no matrícula 2027 observada; incompatibilidad de tipo no implica que deban cambiar de versión, que pudo fijarse por cohorte.

Reproducir: ejecutar construir_v2.py; --check exige identidad de bytes sin reescribir. Fuentes por ruta/hash en MANIFEST. Sólo conteos y catálogo en Git; detalle individual privado.
'''
    put(DATA/'README.md','# H002j · Tipo por plan y comparación de regla\n'+notes)
    report='# H002j · Prueba con tipo de plan UMAS\n\n'+summary['rectificacion_diagnostico']+'\n\n'+table([{'tipo':k,'planes':v} for k,v in sorted(summary['planes_por_tipo'].items())],['tipo','planes'])
    report+='\n## H002i frente a H002j por grupo\n\n'+table(comparison,['anio','grupo','filas_mu','aciertos_H002i','aciertos_H002j','acierto_H002i_pct','acierto_H002j_pct'])
    report+='\n## Total evaluable\n\n'+table(totals,['anio','filas_mu','acierto_H002i_pct','acierto_H002j_pct','delta_pp'])
    report+='\n## Cinco familias, total por año\n\n'+table(ft,['anio','familia','filas_mu','acierto_H002i_pct','acierto_H002j_pct'])
    report+='\n## Cinco familias por grupo\n\n'+table(five,['anio','familia','grupo','filas_mu','acierto_H002i_pct','acierto_H002j_pct'])
    report+='\n## Residuales principales disjuntos\n\n'+table([{'causa':k,'filas':v} for k,v in sorted(causes.items())],['causa','filas'])
    report+='\n## INCONSISTENCIA_DE_CARGA: código observado y previsto\n\n'+table(incons,['anio','familia','codigo_informado','codigo_segun_regla','filas'])
    report+='\n## Nuevos 2027 por tipo\n\n'+table(sf,['familia','tipo_plan','versiones','comparacion'])
    oldsum=Counter((r['familia'],r['estado']) for r in [])
    for r in old2027:oldsum[r['familia'],r['estado']]+=r['matriculas']
    report+='\n## Antiguos potenciales 2027, universo MU2026\n\n'+table([{'familia':f,'estado':s,'matriculas':n} for (f,s),n in sorted(oldsum.items())],['familia','estado','matriculas'])+notes
    put(OUT/'INFORME.md',report)
    initial=read(OUT/'ESTADO_INICIAL.json');assert all(sha(ROOT/p)==h for p,h in initial['protegidos'].items())
    scopes=['data/paridad_codigo_sies/regla_operativa_mu_v2/','outputs/regla_operativa_mu_v2_20261029/']
    unrelated=[s for s in subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines() if not any(p in s for p in scopes)]
    assert unrelated==initial['ajenos']
    # Privacidad: tokenización de identificadores leídos, únicamente en memoria.
    forbidden=set()
    for r in inputrows:
        if r['identidad']:
            _,d,v=r['identidad'];forbidden.update([d,d+'-'+v])
        if r['expediente']:forbidden.add(str(r['expediente']))
    def scan(s):
        s=re.sub(r'\b[0-9a-f]{32,64}\b','HASH',s,flags=re.I)
        tokens=set(re.findall(r'\w+',s))|set(re.findall(r'(?<!\w)\w+[-.]\w+(?!\w)',s))
        assert not ({v for v in forbidden if len(v)>=6}&tokens),'Privacidad: revisar sólo en privado'
        assert not re.search(r'\b\d{7,8}-[0-9Kk]\b',s),'Patrón documental no permitido'
    for s in built.values():scan(s)
    for p in OUT.iterdir():
        if p.is_file() and p.suffix in ('.py','.md','.json'):scan(p.read_text())
    qa={'estado':'PASS','fuentes_verificadas':len(sources),'filas_prueba':len(result),'denominadores_H002i_iguales':True,'antiguos_prediccion_sin_cambio':True,'SQL_diferencias':0,'protegidos_intactos':len(initial['protegidos']),'ajenos_intactos':len(unrelated),'planes':len(cat),'regla':'CANDIDATA_NO_ACTIVA','ADMP_CADMP':'PENDIENTE_ALEXI','privacidad':'PASS'}
    put(OUT/'QA.json',qa)
    put(DATA/'MANIFEST.json',{'hito':'H002j','fecha':'2026-10-29','fuentes':sources,'script_sha256':sha(__file__),'complementos':{str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['ESPECIFICACION.md','FUENTES.json','BUSQUEDA_CARGAS_OFERTA.json','test_regla_v2.py']},'salidas':{str(p.relative_to(ROOT)):hashlib.sha256(s.encode()).hexdigest() for p,s in built.items()}})
    if check:
        assert all(p.exists() and p.read_bytes()==s.encode() for p,s in built.items()),'Reproducción distinta'
        print('REPRODUCCION_IDENTICA',len(built))
    else:
        for p,s in built.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
        PRIVATE.mkdir(parents=True,exist_ok=True);(PRIVATE/'PRUEBA.json').write_text(js(result))
    print(js({'planes':summary['planes_por_tipo'],'total':totals,'causas':dict(causes),'2027':summary['simulacion_2027'],'QA':qa}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');main(ap.parse_args().check)

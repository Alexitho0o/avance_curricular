#!/usr/bin/env python3
"""H002i: prueba retrospectiva candidata; no adjudica ni genera cargas."""
import sys, csv, json, re, hashlib, argparse, copy, sqlite3, subprocess
from pathlib import Path
from collections import Counter, defaultdict
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
DATA=ROOT/'data/paridad_codigo_sies/regla_operativa_mu'
CLOSE=ROOT/'data/paridad_codigo_sies/cierre_historico_2007_2021'
sys.path.insert(0,str(ROOT/'outputs/paridad_cohorte_2007_2026'))
from construir_cohortes import sha, js, read, txt, number, ident, family, codigo, sheet_rows, csvbytes
PRIVATE=Path.home()/'.local/share/ipss/h002i_20261029'
TYPE={'Plan Regular':'1','Plan Regular de Continuidad':'3','Plan Especial':'2'}

def classify(previous, entry_year, year):
    return 'ANTIGUO' if previous else 'NUEVO' if entry_year==year else 'OTRO'

def predict(group, previous, offers, types):
    """Predicción ciega al código observado de Y. Ningún desempate por frecuencia."""
    if group=='OTRO': return None,'FUERA_REGLA'
    if group=='ANTIGUO':
        return (next(iter(previous)),'CODIGO_PREVIO_UNICO') if len(previous)==1 else (None,'CODIGO_PREVIO_MULTIPLE')
    if not offers:return None,'OFERTA_FALTANTE'
    active={c:t for c,t,v in offers if v=='1'}
    if not active:return None,'SIN_VERSION_VIGENCIA_1'
    if len(active)==1:return next(iter(active)),'OFERTA_UNICA_VIGENCIA_1'
    if len(types)!=1:return None,'TIPO_PLAN_NO_DETERMINABLE'
    candidates={c for c,t in active.items() if t in types}
    if len(candidates)==1:return next(iter(candidates)),'TIPO_PLAN_DESAMBIGUA'
    return None,'AMBIGUO_OFERTA' if candidates else 'TIPO_PLAN_SIN_OFERTA_COMPATIBLE'

def cause(group, predicted, actual, why, offers):
    if group=='OTRO':return 'NO_APLICA'
    if predicted==actual:return 'ACIERTO'
    if group=='ANTIGUO':return 'CAMBIO_DE_CODIGO_DEL_ALUMNO' if predicted else 'OTRA'
    if not offers:return 'OFERTA_FALTANTE'
    if actual not in {c for c,t,v in offers if v=='1'}:return 'VERSION_NUEVA_NO_DECLARADA'
    if why in ('TIPO_PLAN_NO_DETERMINABLE','TIPO_PLAN_SIN_OFERTA_COMPATIBLE'):return 'TIPO_PLAN_NO_DETERMINABLE'
    return 'OTRA'

def pct(a,b):return round(100*a/b,6) if b else None

def metrics(rows, fields):
    groups=defaultdict(list)
    for r in rows:groups[tuple(r[k] for k in fields)].append(r)
    out=[]
    for k,rs in sorted(groups.items()):
        pred=sum(r['predicho'] is not None for r in rs);hit=sum(r['acierto'] for r in rs)
        out.append(dict(zip(fields,k),filas_mu=len(rs),predicciones=pred,aciertos=hit,
            no_aciertos=len(rs)-hit,sin_prediccion=len(rs)-pred,acierto_pct=pct(hit,len(rs)),
            cobertura_prediccion_pct=pct(pred,len(rs)),acierto_entre_predicciones_pct=pct(hit,pred)))
    return out

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(js(obj) if not isinstance(obj,str) else obj)

def table(rows,fields):
    return '| '+' | '.join(fields)+' |\n| '+' | '.join(['---']*len(fields))+' |\n'+''.join('| '+' | '.join(str(r.get(k,'')) for k in fields)+' |\n' for r in rows)

def main(check=False):
    sources=read(OUT/'FUENTES.json');src={s['id']:Path(s['ruta']) for s in sources}
    for s in sources:
        if sha(s['ruta'])!=s['sha256']:raise ValueError('Fuente alterada: '+s['id'])
    built={}
    def put(p,x):built[p]=js(x) if not isinstance(x,str) else x
    master=read(src['data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json'])
    # Oferta histórica de su extracción gobernada, no de los códigos MU a predecir.
    offer=defaultdict(list);originalrows={}
    for r in csv.DictReader(src['oferta_anual'].open(),delimiter='\t'):
        y=number(r['ANO'].removeprefix('OFE_'))
        if y in range(2023,2027):originalrows[y,r['CODIGO_UNICO']]=r
    for r in master['oferta_anual']:
        y=r['anio']
        if y not in range(2023,2027):continue
        c=r['codigo_unico'];original=originalrows[y,c]
        assert original['VIGENCIA']==r['vigencia'] and original['TIPO_CARRERA']==r['tipo_plan_sies']
        vig={'Vigente con estudiantes nuevos':'1','Vigente sin estudiantes nuevos':'2','No vigente':'3'}.get(r['vigencia'])
        assert vig is not None,'Vigencia histórica no reconocida'
        typ=TYPE.get(r['tipo_plan_sies']);assert typ is not None,'Tipo histórico no reconocido'
        offer[y,family(c)].append((c,typ,vig))
    assert sum(map(len,offer.values()))==len(originalrows)
    formal=defaultdict(set)
    for p in read(src['outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json'])['perfiles']:
        for v in p['perfil_formal_H112B']:formal[p['codcarpr'],p['CODPESTUD']].add(txt(v['tipo_plan_codigo']))
    links=read(src['enlaces_H002g']);linkbyline={r['fila_fuente_mu']:r for r in links}
    assert len(linkbyline)==len(links)
    mup=next(p for name,p in src.items() if name.startswith('BASE_RETENCION_'))
    fields=['ANIO_INFORMADO','TIPO_DOC','N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION','VIG','ANIO_ING_ACT','SEM_ING_ACT','FOR_ING_ACT']
    mu=[];prev=defaultdict(set);priorplans=defaultdict(set);priorexp=defaultdict(set)
    for line,r in sheet_rows(mup,'BASE_RETENCION_MU',fields):
        y=number(r['ANIO_INFORMADO']);pe=ident(r['TIPO_DOC'],r['N_DOC'],r['DV']);c=codigo(r);f=family(c);link=linkbyline[line]
        assert link['anio']==y and link['codigo_sies']==c and link['identidad']==(list(pe) if pe else None)
        sel=link['seleccion'];ca=sel[1] if sel else 'SIN_ENLACE';pl=link['plan']
        types=formal[ca,pl];ctx=(pe,y,f)
        if pe:
            prev[ctx].add(c)
            if sel:priorexp[ctx].add(sel[0])
            if pl not in ('SIN_ENLACE','PLAN_NO_OBSERVADO','PLAN_MULTIPLE_E'):priorplans[ctx].add(pl)
        mu.append({'anio':y,'identidad':pe,'familia':f,'real':c,'ingreso':number(r['ANIO_ING_ACT']),
                   'for_ing_act':r['FOR_ING_ACT'],'vig':r['VIG'],'plan':pl,'codcarpr':ca,'types':types,
                   'expediente':sel[0] if sel else None,'fila_mu':line})
    assert len(mu)==len(links)==10200
    result=[];overlap=Counter();changes=Counter();sens=Counter()
    for r in mu:
        y=r['anio'];pe=r['identidad'];f=r['familia']
        if y<2023:continue
        previous=prev.get((pe,y-1,f),set()) if pe else set();group=classify(previous,r['ingreso'],y)
        offers=offer[y,f];pred,why=predict(group,previous,offers,r['types'])
        actual=r['real'];hit=pred==actual
        pt={t for c,t,v in offers if c==pred};forok=not (pt=={'3'} and r['for_ing_act'] not in ('2','3','4','11'))
        # Control 2026 separado: no se impone a años anteriores sin norma anual.
        sens[y,'CONTROL_FOR_2026_INCOMPATIBLE' if not forok else 'SIN_INCOMPATIBILIDAD_FOR_2026']+=1
        if group=='ANTIGUO' and r['ingreso']==y:overlap[y]+=1
        ps=priorplans.get((pe,y-1,f),set());es=priorexp.get((pe,y-1,f),set())
        changeplan=bool(ps and r['plan'] not in ('SIN_ENLACE','PLAN_NO_OBSERVADO','PLAN_MULTIPLE_E') and r['plan'] not in ps)
        changeexp=bool(es and r['expediente'] and r['expediente'] not in es)
        if changeplan:changes[y,'PLAN_OBSERVADO_DISTINTO']+=1
        if changeexp:changes[y,'EXPEDIENTE_OBSERVADO_DISTINTO']+=1
        result.append(dict(r,grupo=group,predicho=pred,motivo=why,causa=cause(group,pred,actual,why,offers),
                           acierto=hit,previos=sorted(previous),control_for_2026_compatible=forok,
                           cambio_plan_observado=changeplan,cambio_expediente_observado=changeexp))
    evaluable=[r for r in result if r['grupo']!='OTRO'];ms=metrics(result,['anio','grupo']);mf=metrics(evaluable,['anio','familia','grupo'])
    # OTRO no tiene predicción ni tasa; se informa universo separado.
    for r in ms:
        if r['grupo']=='OTRO':r['acierto_pct']=None;r['no_aciertos']=None
    total=metrics(evaluable,['anio'])
    yearly=[]
    for y in range(2023,2027):
        a={r['grupo']:r for r in ms if r['anio']==y};t=next(r for r in total if r['anio']==y)
        yearly.append({'anio':y,'filas_mu':sum(r['filas_mu'] for r in a.values()),
                       'antiguos':a.get('ANTIGUO',{}).get('filas_mu',0),'antiguos_acierto_pct':a.get('ANTIGUO',{}).get('acierto_pct'),
                       'nuevos':a.get('NUEVO',{}).get('filas_mu',0),'nuevos_acierto_pct':a.get('NUEVO',{}).get('acierto_pct'),
                       'otros':a.get('OTRO',{}).get('filas_mu',0),'total_evaluable':t['filas_mu'],'total_acierto_pct':t['acierto_pct'],
                       'antiguo_y_cohorte_del_anio':overlap[y]})
    errors=Counter((r['anio'],r['familia'],r['grupo'],r['causa'],r['motivo']) for r in evaluable if not r['acierto'])
    errorrows=[dict(zip(['anio','familia','grupo','causa','motivo'],k),filas_mu=n) for k,n in sorted(errors.items())]
    top=Counter(r['familia'] for r in evaluable if not r['acierto']).most_common(5)
    causes=Counter(r['causa'] for r in evaluable if not r['acierto'])
    # SQLite independiente: sumas, denominadores y partición sin funciones de agrupación Python.
    db=sqlite3.connect(':memory:');db.execute('create table prueba(anio int, grupo text, familia text, hit int, pred int)')
    db.executemany('insert into prueba values(?,?,?,?,?)',[(r['anio'],r['grupo'],r['familia'],int(r['acierto']),int(r['predicho'] is not None)) for r in result])
    sql=db.execute('select anio,grupo,count(*),sum(hit),sum(pred) from prueba group by anio,grupo order by anio,grupo').fetchall()
    assert sql==[(r['anio'],r['grupo'],r['filas_mu'],r['aciertos'],r['predicciones']) for r in ms]
    sqlfam=db.execute("select anio,familia,grupo,count(*),sum(hit),sum(pred) from prueba where grupo!='OTRO' group by anio,familia,grupo order by anio,familia,grupo").fetchall()
    assert sqlfam==[(r['anio'],r['familia'],r['grupo'],r['filas_mu'],r['aciertos'],r['predicciones']) for r in mf]
    db.execute('create table mu(anio int, persona text, familia text, ingreso int, fila int)')
    db.executemany('insert into mu values(?,?,?,?,?)',[(r['anio'],json.dumps(r['identidad']) if r['identidad'] else None,r['familia'],r['ingreso'],r['fila_mu']) for r in mu])
    db.execute('create index mu_persona on mu(anio,persona,familia)')
    independent=db.execute("select a.fila, case when exists(select 1 from mu b where b.anio=a.anio-1 and b.persona=a.persona and b.familia=a.familia) then 'ANTIGUO' when a.ingreso=a.anio then 'NUEVO' else 'OTRO' end from mu a where a.anio>=2023 order by a.fila").fetchall()
    assert independent==sorted((r['fila_mu'],r['grupo']) for r in result)
    db.close()
    # Cierre documental; conserva la tabla de H002h, no recalcula fuentes anteriores.
    history=read(src['outputs/paridad_cohorte_2007_2026_v2/RESULTADOS.json'])['totales_ingreso_por_anio']
    put(CLOSE/'TOTALES_Y_ALCANCE.json',{'estado':'CIERRE_E_CON_CAUSA_POR_DECISION_D','decision':'Alexi, 29-10-2026','tabla':history})
    closemd='# Cierre histórico 2007–2021\n\nD · Alexi, 29-10-2026. CIERRE E CON CAUSA; no es una conciliación lograda ni un pendiente abierto. Datos Alumnos es una foto de expedientes, no el registro anual al corte SIES. No se vuelve a cuadrar la historia anterior a 2022 con esa foto.\n\nB/C · Tabla reutilizada de H002h; unidades diferentes conservadas explícitamente. El 264 de 2007 corresponde a cohortes derivadas, no a la columna pública de primer año (211). No se equiparan esas definiciones.\n\n'
    closemd+=table(history,['anio','interno_total_expedientes_anoingreso','interno_familias_mapeadas','sies_cohorte_derivada_ingresa_en_anio','sies_primer_anio_publicado'])
    closemd+='\nEl registro SIES por estudiante/código responde matrícula observada por año, código, versión y trayectorias dentro de SIES; su control congelado contra publicación arroja cero diferencias. No identifica el plan UMAS ni permite enlazar notas, expedientes o títulos internos. No se reconstruye RUT–MRUN. La falta de historia comparable cierra la paridad interna, no impugna la historia oficial. Retiros previos al corte, segundo semestre y cambios de plan describen límites y posibles diferencias de universo; no son causas personales acreditadas.\n\nFuentes y hashes: MANIFEST.json; control y fuentes primarias de H002g, tabla de H002h. Los originales permanecen intactos.\n'
    put(CLOSE/'README.md',closemd)
    lots=read(src['outputs/paridad_cohorte_2007_2026_v2/LOTES_REVISION_v3.json'])['lotes']
    splits=read(src['outputs/paridad_cohorte_2007_2026_v2/REPARTOS_FORMA_INGRESO.json'])['grupos']
    years={tuple(g['grupo']):{t['anio'] for t in g['tabla']} for g in splits if g['origen']=='SIES'}
    annotated=[]
    for lot in lots:
        x=copy.deepcopy(lot);flags=[]
        for ev in lot['evidencia']:
            ys=years.get(tuple(ev.get('grupo',[])),set())
            flags.append(lot['problema'] in ('NO_CUADRA','AMBIGUA') or (lot['problema']=='REPARTO_SIES' and bool(ys) and max(ys)<=2021))
        x['cierre_h002i']={'estado':'CERRADAS_POR_DECISION_D' if flags and all(flags) else 'CIERRE_PARCIAL' if any(flags) else 'ABIERTA',
                          'evidencias_cerradas':[i+1 for i,v in enumerate(flags) if v],
                          'decision':'Alexi, 29-10-2026' if any(flags) else None,
                          'motivo':'Sólo historia 2007–2021; no hay registro UMAS histórico comparable' if any(flags) else 'Conserva el alcance de H002h; ADMP/CADMP no aprobado'}
        annotated.append(x)
    lc=Counter(x['cierre_h002i']['estado'] for x in annotated)
    put(OUT/'LOTES_REVISION_v3_CIERRE_H002i.json',{'origen_sha256':sha(src['outputs/paridad_cohorte_2007_2026_v2/LOTES_REVISION_v3.json']),'lotes':annotated,'resumen':dict(lc)})
    lm='# Lotes v3 · copia derivada con cierre H002i\n\nSe conserva cada entrada original; H002h no se modifica. Las decisiones históricas cerradas no solicitan nueva aprobación.\n'
    for x in annotated:
        lm+=f"\n## Lote {x['lote']} · {x['familia']} · {x['problema']}\n\nEstado: **{x['cierre_h002i']['estado']}**. Evidencias cerradas: {x['cierre_h002i']['evidencias_cerradas']}.\n\nPropuesta original: {x['propuesta']}\n\nEvidencia original conservada:\n\n```json\n{js(x['evidencia'])}```\n"
        if x['cierre_h002i']['estado']!='CERRADAS_POR_DECISION_D':lm+='\nDecisión Alexi: ____\n'
    put(OUT/'LOTES_REVISION_v3_CIERRE_H002i.md',lm)
    # Simulación de catálogo, separada de personas y de la oferta aceptada.
    with src['precarga5913'].open(encoding='utf-8-sig') as f:headers=next(csv.reader(f,delimiter=';'))
    headers=[h for h in headers if h not in ('CODIGO_IES_NUM','CANTIDAD_MATRICULA_DFE','CANTIDAD_BENEFICIO_DFE')]
    raw=list(csv.reader(src['carga_v06'].open(encoding='utf-8-sig'),delimiter=';'));assert all(len(r)==len(headers) for r in raw)
    v06=[dict(zip(headers,r)) for r in raw];h002=[r for r in read(src['data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json'])['filas'] if r['anio']==2027]
    hby={r['codigo_unico']:r for r in h002};families=defaultdict(list)
    for r in v06:
        c='I162S'+r['COD_SEDE']+'C'+r['COD_CARRERA']+'J'+r['COD_JORNADA']+'V'+r['VERSION']
        assert c in hby
        families[family(c)].append((c,r))
    simulation=[]
    for f,rs in sorted(families.items()):
        active=[(c,r) for c,r in rs if r['VIGENCIA_CARRERA']=='1' and hby[c]['estado']!='FUERA_ALCANCE']
        typs=defaultdict(list)
        for c,r in active:typs[r['COD_TIPO_PLAN_CARRERA']].append(c)
        cond=[{'tipo_plan':t,'codigos':sorted(cs),'resultado':'UNICO_CONDICIONADO_AL_PLAN' if len(cs)==1 else 'AMBIGUO_OFERTA'} for t,cs in sorted(typs.items())]
        predicted=sorted(c for t,cs in typs.items() if len(cs)==1 for c in cs)
        declared=sorted(c for c,r in rs if hby[c]['version_para_nuevos_2027']=='sí')
        unknown=sorted(c for c,r in rs if hby[c]['version_para_nuevos_2027']=='E')
        state='NO_COMPARABLE_E' if unknown or any(len(cs)>1 for cs in typs.values()) else 'COINCIDE' if predicted==declared else 'DIFIERE'
        simulation.append({'familia':f,'clase':'C/E','estado_comparacion':state,'opciones_por_tipo':cond,'codigos_candidatos_nuevos':predicted,
                           'H002_para_nuevos':declared,'H002_E':unknown,'codigos_sin_nuevos':[c for c,r in rs if r['VIGENCIA_CARRERA']!='1'],
                           'fuera_alcance':[c for c,r in rs if hby[c]['estado']=='FUERA_ALCANCE'],
                           'ADMP_CADMP':'PENDIENTE_ALEXI' if f=='I162S2C83J4' else 'NO_APLICA'})
    simcount=Counter(r['estado_comparacion'] for r in simulation)
    summary={'estado':'CANDIDATA_NO_ACTIVA','clase':'C/E','unidad':'filas de matrícula MU; no personas únicas',
        'anual':yearly,'por_grupo':ms,'por_familia':mf,'desaciertos':errorrows,'causas':dict(causes),'cinco_familias':top,
        'lotes':dict(lc),'simulacion_2027':dict(simcount),'antiguos_2027_universo_mu2026':4105,
        'cambios_observados':[{'anio':y,'tipo':k,'filas':n} for (y,k),n in sorted(changes.items())],
        'control_FOR_2026_sensibilidad':[{'anio':y,'control':k,'filas':n} for (y,k),n in sorted(sens.items())]}
    put(DATA/'METRICAS_REGLA_2023_2026.json',summary);put(DATA/'METRICAS_REGLA_2023_2026.csv',csvbytes(ms))
    put(DATA/'SIMULACION_NUEVOS_2027.json',{'fuente':'V06 carga preparada C; no aceptación acreditada','filas':simulation,'resumen':dict(simcount)})
    put(DATA/'SIMULACION_NUEVOS_2027.csv',csvbytes(simulation))
    put(OUT/'DESACIERTOS_POR_FAMILIA.csv',csvbytes(errorrows));put(OUT/'METRICAS_POR_FAMILIA.csv',csvbytes(mf))
    # Diagnóstico agregado por código real/predicho/plan/FOR para auditar la prueba.
    agg=Counter((r['anio'],r['grupo'],r['familia'],r['codcarpr'],r['plan'],r['for_ing_act'],r['vig'],r['real'],r['predicho'] or '',r['motivo'],r['causa']) for r in result)
    ar=[dict(zip(['anio','grupo','familia','codcarpr','plan','for_ing_act','vig','codigo_real','codigo_predicho','motivo','causa'],k),filas=n) for k,n in sorted(agg.items())]
    put(OUT/'DIAGNOSTICO_AGREGADO.json',ar)
    notes='''
D · Alexi, 29-10-2026 autoriza probar; no activar. ANTIGUO prevalece sobre NUEVO si hay solapamiento. Identidad exacta y misma familia (S+C+J), sin filtro VIG. Código previo múltiple no se resuelve por mayoría. NUEVO: ANIO_ING_ACT del año, sin presencia anterior en esa familia. OTRO queda fuera de la tasa evaluable. Cambios de plan/expediente observados se informan sin alterar esta precedencia; no equivalen a bitácora de migración.

C · % acierto = aciertos / todas las filas ANTIGUO o NUEVO, incluidas las no predecibles. Total = suma de aciertos / suma de ambos grupos; nunca promedio de porcentajes. OTRO no es error ni acierto. Son matrículas, no personas únicas. CSV de métricas por grupo; JSON incluye familias y denominadores completos.

B/C · Oferta anual extraída del histórico 2010–2026 del 05-06-2026, contrastada con maestro y TSV gobernados. No acredita qué versión del catálogo estaba disponible el día de la carga. Perfiles H112B son evidencia interna candidata, no aceptación PES. FOR observado no se transforma en tipo de plan: FOR 11 no distingue por sí solo regular de continuidad. El control de compatibilidad FOR de 2026 se presenta separado, como sensibilidad C/E y no filtro histórico. Una oferta única permite predecir aun sin plan formal; no acredita compatibilidad individual del plan.

C/E · Para 2027 V06 es carga preparada; cada familia puede tener opciones distintas por tipo, no una versión universal. H002 con E es NO_COMPARABLE_E. ADMP/CADMP permanece pendiente incluso si su catálogo tiene opciones únicas por tipo. Antiguos 2027: universo potencial MU 2026 de 4.105 matrículas, no retención ni carga ni asignación personal. Aprobación expresa y métricas por año son requisitos previos a activar.

Fuentes por ruta/hash en MANIFEST.json. Reproducción: ejecutar construir.py; --check compara los bytes sin reescribir salidas. Detalle individual sólo en ~/.local/share/ipss/h002i_20261029/. No cambia H002–H002h, diccionario v20, fuentes ni tasas.
'''
    put(DATA/'README.md','# Regla operativa MU · candidata H002i\n'+notes)
    report='# H002i · Cierre histórico y prueba retrospectiva\n\nEstado: CANDIDATA_NO_ACTIVA (D/C/E).\n\n'+table(yearly,['anio','filas_mu','antiguos','antiguos_acierto_pct','nuevos','nuevos_acierto_pct','otros','total_evaluable','total_acierto_pct'])
    report+='\n## Desaciertos (incluye sin predicción)\n\n'+table([{'causa':k,'filas':v} for k,v in sorted(causes.items())],['causa','filas'])
    report+='\n## Cinco familias con más desaciertos\n\n'+table([{'familia':k,'filas':v} for k,v in top],['familia','filas'])
    report+='\n## Simulación 2027\n\n'+table([{'comparacion':k,'familias':v} for k,v in sorted(simcount.items())],['comparacion','familias'])
    report+='\n## Solapamientos y cambios observados\n\n'+table(summary['cambios_observados'],['anio','tipo','filas'])
    report+='\nLa prioridad literal del Paso 2 conserva estos casos en ANTIGUO si hay presencia anterior en la misma familia. No deben interpretarse automáticamente como antiguos sin cambio para una carga futura; la regla candidata requiere resolver ese alcance. Un cambio observado en el enlace anual no acredita una migración administrativa.\n'
    report+='\n## Control FOR de 2026 (separado)\n\n'+table(summary['control_FOR_2026_sensibilidad'],['anio','control','filas'])
    report+='\nLos dos casos incompatibles del control FOR de 2026 no se corrigen ni se usan para alterar el dato informado. No se convierte este control en norma retrospectiva.\n'
    report+='\n## Cierre histórico\n\n'+str(dict(lc))+'; todas las entradas originales conservadas. Ver data/paridad_codigo_sies/cierre_historico_2007_2021/README.md y LOTES_REVISION_v3_CIERRE_H002i.md.\n'+notes
    put(OUT/'INFORME.md',report)
    # QA independiente de resultados esperados de acierto.
    initial=read(OUT/'ESTADO_INICIAL.json');protected=initial['protegidos']
    assert all(sha(ROOT/p)==h for p,h in protected.items()),'Archivo protegido modificado'
    unrelated=[s for s in subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines() if not any(q in s for q in ('data/paridad_codigo_sies/cierre_historico_2007_2021/','data/paridad_codigo_sies/regla_operativa_mu/','outputs/regla_operativa_mu_20261029/'))]
    assert unrelated==initial['ajenos'],'Estado ajeno distinto'
    assert [r['filas_mu'] for r in yearly]==[1145,1541,2371,4105]
    assert all(r['antiguos']+r['nuevos']+r['otros']==r['filas_mu'] for r in yearly)
    assert sum(r['filas'] for r in ar)==9162
    assert all(not r['acierto'] and r['predicho'] is None for r in result if r['grupo']=='OTRO')
    assert len(simulation)==len(families) and sum(len(rs) for rs in families.values())==161
    assert len(annotated)==len(lots) and all({k:v for k,v in x.items() if k!='cierre_h002i'}==old for x,old in zip(annotated,lots))
    # Privacidad: no proyectar identificadores, cotejar tokens reales sólo en memoria.
    forbidden=set()
    for r in mu:
        if r['identidad']:
            _,doc,dv=r['identidad'];forbidden.update([doc,doc+'-'+dv,doc+'.'+dv])
        if r['expediente']:forbidden.add(str(r['expediente']))
    def scan(text):
        text=re.sub(r'\b[0-9a-f]{32,64}\b','HASH',text,flags=re.I)
        tokens=set(re.findall(r'\w+',text)) | set(re.findall(r'(?<!\w)\w+[-.]\w+(?!\w)',text))
        hits={v for v in forbidden if len(v)>=6} & tokens
        if hits:raise ValueError('Identificador detectado; revisar sólo en privado')
        assert not re.search(r'\b\d{7,8}-[\dKk]\b',text),'Formato de documento en salida'
    for content in built.values():scan(content)
    for p in OUT.glob('*.py'):scan(p.read_text())
    qa={'estado':'PASS','fuentes_verificadas':len(sources),'filas_mu_base':len(mu),'filas_prueba':len(result),
        'particion_anual':yearly,'sql_diferencias':0,'sql_clasificacion_filas_diferencias':0,'protegidos_intactos':len(protected),'ajenos_intactos':len(unrelated),
        'lotes_originales_conservados':len(lots),'conteos_lotes':dict(lc),'codigo_personal_publicado':False,
        'escaneo_identificadores':'PASS','simulacion_codigos':161,'simulacion_familias':len(families),
        'H002_no_modificada':True,'ADMP_CADMP':'PENDIENTE_ALEXI','regla':'CANDIDATA_NO_ACTIVA'}
    put(OUT/'QA.json',qa)
    for folder in (CLOSE,DATA):
        outs={str(p.relative_to(ROOT)):hashlib.sha256(s.encode()).hexdigest() for p,s in built.items() if p.parent==folder}
        put(folder/'MANIFEST.json',{'hito':'H002i','fecha':'2026-10-29','clase':'D/C/E','fuentes':sources,
            'script':{'ruta':str(Path(__file__).relative_to(ROOT)),'sha256':sha(__file__)},'salidas':outs})
    if check:
        bad=[str(p.relative_to(ROOT)) for p,s in built.items() if not p.exists() or p.read_bytes()!=s.encode()]
        assert not bad,'Reproducción distinta: '+str(bad)
        print('REPRODUCCION_IDENTICA',len(built))
    else:
        for p,s in built.items():write(p,s)
        PRIVATE.mkdir(parents=True,exist_ok=True)
        serial=[{k:sorted(v) if isinstance(v,set) else v for k,v in r.items()} for r in result]
        write(PRIVATE/'PRUEBA_RETROSPECTIVA.json',serial)
    print(js({'anual':yearly,'causas':dict(causes),'simulacion':dict(simcount),'lotes':dict(lc),'QA':'PASS'}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();main(args.check)

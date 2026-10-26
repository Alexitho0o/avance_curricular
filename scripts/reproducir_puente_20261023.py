"""Relectura independiente y auditoría de V10. No modifica reglas ni fuentes.

Resultados individuales fuera de Git; evidencia anual no acredita asignación
histórica de plan ni aceptación SIES. Ejecución desde la raíz del repositorio.
"""
import ast, csv, datetime, hashlib, json, os, re, subprocess, zipfile, argparse
from collections import Counter, defaultdict
from pathlib import Path
import openpyxl

R = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--reanudacion',type=Path);ARGS=parser.parse_args()
STAMP = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
O = R / 'outputs' / ('reproduccion_puente_' + STAMP)
P = Path.home() / '.local/share/ipss' / ('reproduccion_puente_' + STAMP)
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode != 0
os.umask(0o077); P.mkdir(parents=True); O.mkdir()
HASHES = {}; INVENTORY = []; QA = {}; LOG = []
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def source(p):
    p=Path(p); HASHES[str(p)]=sha(p); return p
def load(p): return json.loads(source(p).read_text())
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def val(x): return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def norm(a,b=None):
    a=val(a).upper().replace(' ','').replace('.','')
    s=a if b is None else a+'-'+val(b).upper()
    if not re.fullmatch(r'\d+-[0-9K]',s): return None
    a,b=s.split('-'); return str(int(a))+'-'+b
def rows(p,sheet=None):
    p=source(p); w=openpyxl.load_workbook(p,read_only=True,data_only=True)
    s=w[sheet] if sheet else w.active; it=iter(s.values); heads=next(it); n=0
    years=Counter()
    for rn,v in enumerate(it,2):
        d=dict(zip(heads,v)); n+=1
        for k in ['ANO','ANIO_INFORMADO','MC_CAT_PERIODO','ANOMATRICULA']:
            if k in d: years[val(d[k])]+=1; break
        yield rn,d,s.title
    INVENTORY.append({'archivo':str(p),'sha256':HASHES[str(p)],'hoja':s.title,
        'filas':n,'encabezados':heads,'anios_observados':dict(years),
        'created_docprops_no_corte':str(w.properties.created),'modified_docprops_no_corte':str(w.properties.modified),
        'corte_efectivo':'NO_ACREDITADO_POR_DOC_PROPS'})
    w.close()
def csvout(p,rr):
    if not rr:return
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        fields=list(dict.fromkeys(k for r in rr for k in r))
        wr=csv.DictWriter(f,fieldnames=fields,delimiter=';');wr.writeheader()
        for r in rr:
            wr.writerow({k:json.dumps(v,ensure_ascii=False,default=str) if isinstance(v,(list,dict,set,tuple)) else v for k,v in r.items()})
def progress(f,h,t):
    line=f'Fase {f}/7 · Hito {h}/3 — {t}';LOG.append(line);print(line,flush=True)
def partition(rr,field):
    by=defaultdict(list)
    for x in rr:by[x['persona']].append(bool(x[field]))
    return {'sin_pendientes':sum(all(v) for v in by.values()),
        'parcialmente_resueltas':sum(any(v) and not all(v) for v in by.values()),
        'ninguna_observacion_resuelta':sum(not any(v) for v in by.values()),
        'personas_con_algun_pendiente':sum(not all(v) for v in by.values()),
        'observaciones_pendientes':sum(not x[field] for x in rr)}

GIT={}
for repo in [R,R.parent/'CARACTERIZACIÓN',R.parent/'IPSS_Procesos_SIES']:
    GIT[str(repo)]={k:subprocess.check_output(['git','-C',str(repo),*args],text=True).strip() for k,args in
        [('head',['rev-parse','HEAD']),('rama',['branch','--show-current']),('remotos',['remote','-v']),('status',['status','--short'])]}
dump(O/'GIT_ANTES.json',GIT)
progress(1,1,'Inventario y comprobación de huellas previas')
old=load(ARGS.reanudacion/'antecedentes_minimos.json' if ARGS.reanudacion else '/tmp/ipss_revision_63_20261022/payload.json')
get=lambda n:next(s['rows'] for s in old if s['name']==n)
expected={tuple(r[:8]):r for r in get('CONTRASTE_63')}
assert len(expected)==len(get('CONTRASTE_63'))
hashchecks=[]
declared=dict(get('HASHES'))
for version in ['20261023_v8','20261023_v9','20261023_v10']:
    declared.update(load(R/f'outputs/retencion_puente_provisional_{version}/FUENTES_HASHES.json'))
for path,h in declared.items():
    if ARGS.reanudacion and path.startswith('/tmp/'):
        hashchecks.append({'archivo':path,'sha256_declarado':h,'sha256_actual':'','estado':'INTERMEDIO_HISTORICO_SUSTITUIDO_POR_SNAPSHOT_MINIMO'});continue
    try: actual=sha(path);HASHES[path]=actual;state='OK' if actual==h else 'HASH_DISTINTO'
    except OSError as e:actual='';state=type(e).__name__
    hashchecks.append({'archivo':path,'sha256_declarado':h,'sha256_actual':actual,'estado':state})
csvout(O/'HUELLAS_PREVIAS.csv',hashchecks)
assert all(x['estado'] in ['OK','INTERMEDIO_HISTORICO_SUSTITUIDO_POR_SNAPSHOT_MINIMO'] for x in hashchecks), 'Fase dependiente bloqueada: fuentes cambiadas/inaccesibles'
G={(g['codcarpr'],g['sede'],g['jornada']):g for g in load(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json')}
M=load(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
plans={x['CODPESTUD']:x for x in load(R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json')}
dims=load(R/'data/reglas_negocio/20261022_puente_versiones/investigacion_contextual_v3/PRUEBAS_CONTEXTUALES.json')
families={(x['carrera'],x['jornada']):set(x['familias']) for x in dims}
sites={(x['carrera'],x['jornada']):x['sede'] for x in dims}
jmap={'D':'1','V':'2','O':'4'};revj={v:k for k,v in jmap.items()}
DA=[Path('/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx'),Path('/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx')]
PR=Path('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx')
da=defaultdict(list); da0=defaultdict(list); contexts=[]
for n,path in enumerate(DA):
    for rn,d,sh in rows(path,'Hoja1'):
        k=norm(d.get('RUT'));cli=val(d.get('CODCLI'));c=val(d.get('CODCARPR'))
        z={q:val(d.get(q)) for q in ['RUT','CODCLI','CODCARPR','SEDE','JORNADA','ANOINGRESO','PERIODOINGRESO','ANOMATRICULA','PERIODOMATRICULA','FECHAMATRICULA']}
        z.update(persona=k,fuente=str(path),hoja=sh,fila=rn)
        da[cli,c].append(z)
        if n==0:da0[cli,c].append(z)
progress(1,3,'Lectura de PROMEDIOS y reconstrucción de unidades únicas')
pr=defaultdict(list);allpr=defaultdict(set);cliowners=defaultdict(set);rawcount=0;invalid=0
for rn,d,sh in rows(PR,'Hoja1'):
    rawcount+=1;k=norm(d.get('RUT'),d.get('DIG'));j=jmap.get(val(d.get('JORNADA')),'');c=val(d.get('CODCARR'));cli=val(d.get('CODCLI'))
    if not k:invalid+=1;continue
    plan,y,t=(val(d.get(q)) for q in ['PLAN_DE_ESTUDIO','ANO','PERIODO'])
    allpr[c,j].add((k,cli,plan,y,t));cliowners[cli].add(k)
    if (c,j) not in families:continue
    key=(k,cli,c,sites[c,j],j,plan,y,t)
    pr[key].append({'fuente':str(PR),'hoja':sh,'fila':rn,'RUT_original':val(d.get('RUT')),'DV_original':val(d.get('DIG')),
        'CODCLI_original':val(d.get('CODCLI')),'ANO':y,'PERIODO':t,'PLAN_DE_ESTUDIO':plan,
        'estado_ramo':val(d.get('DESCRIPCION_ESTADO')),'convalidado':val(d.get('CONVALIDADO'))})
QA['universo_raw']={'personas':len({k[0] for k in pr}),'expedientes':len({(k[2],k[1]) for k in pr}),
    'observaciones':len(pr),'filas_asignatura_seleccionadas':sum(map(len,pr.values())), 'filas_promedios':rawcount,'identidades_invalidas_fuera_y_dentro':invalid,
    'unidades_faltan':len(set(expected)-set(pr)),'unidades_nuevas':len(set(pr)-set(expected))}
dump(O/'QA_BASE_INICIAL.json',QA)
assert set(pr)==set(expected),'No reproduce el universo: detener fases dependientes'
attr=defaultdict(set)
for (c,j),units in allpr.items():
    fam=G.get((c,'RE',revj.get(j)),{}).get('familias',[])
    for k,cli,plan,y,t in units:
        for f in fam:attr[k,y,f].add((c,cli))
mu=defaultdict(list); muall=defaultdict(list)
mus=sorted({(e[8],e[9]) for e in get('EVIDENCIAS_SIES') if e[1]=='MATRICULA'})
progress(2,1,f'Relectura de {len(mus)} fuentes/hojas de matrícula')
for path,sh in mus:
    # Only explicit primary MAT and the fixed derived base carry annual evidence.
    if 'MAT_IP_CIISA_' not in path and 'BASE_RETENCION_MATRICULA' not in path:continue
    for rn,d,sheet in rows(path,sh):
        historic='MC_CODIGO_UNICO' in d
        typ=val(d.get('TIPO_DOC') if not historic else d.get('MM_TIPO_DOC')).upper()
        if not historic and typ not in ['','R','1','RUT']:continue
        k=norm(d.get('MM_N_DOCUMENTO') if historic else d.get('N_DOC'),d.get('MM_DV') if historic else d.get('DV'))
        y=val(d.get('MC_CAT_PERIODO') if historic else d.get('ANIO_INFORMADO')).replace('MAT_','')
        code=val(d.get('MC_CODIGO_UNICO')) if historic else 'I162S%sC%sJ%sV%s'%tuple(val(d.get(q)) for q in ['COD_SED','COD_CAR','JOR','VERSION'])
        if not k or not re.fullmatch(r'I\d+S\d+C\d+J\d+V\d+',code):continue
        z={'codigo':code,'anio':y,'fuente':path,'hoja':sheet,'fila':rn,'tipo_doc_original':typ,
            'documento_original':val(d.get('MM_N_DOCUMENTO') if historic else d.get('N_DOC')),
            'dv_original':val(d.get('MM_DV') if historic else d.get('DV')),
            'ingreso_actual':val(d.get('MM_ANIO_ACTUAL') if historic else d.get('ANIO_ING_ACT')),
            'ingreso_origen':val(d.get('MM_ANIO_ORIGEN') if historic else d.get('ANIO_ING_ORI')),
            'reincorporacion':val(d.get('REINCORPORACION'))}
        mu[k,y].append(z);muall[k].append(z)
results=[];mismatch=[];counts=Counter();docstates={'CONFIRMA_CODIGO_PROPUESTO_OBSERVADO','DIFIERE_CODIGO_PROPUESTO_OBSERVADO','CODIGO_ANUAL_UNICO_SIN_PROPUESTA_PREVIA'}
for key in sorted(pr):
    k,cli,c,site,j,plan,y,t=key;r=expected[key];fam=families[c,j];ev=[e for e in mu[k,y] if e['codigo'].rsplit('V',1)[0] in fam];codes={e['codigo'] for e in ev}
    ds=[d for d in da0[cli,c] if d['persona']==k and d['SEDE']=='RE' and jmap.get(d['JORNADA'])==j]
    amb=len(cliowners[cli])>1 or len({d['persona'] for d in da0[cli,c]})>1 or any(len(attr[k,y,co.rsplit('V',1)[0]])>1 for co in codes)
    state='SIN_EVIDENCIA_ANUAL_APLICABLE' if not codes else 'CONTRADICCION_O_ATRIBUCION_MULTIPLE' if len(codes)>1 or amb else 'CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO' if not ds else 'CONFIRMA_CODIGO_PROPUESTO_OBSERVADO' if r[8] and r[8] in codes else 'DIFIERE_CODIGO_PROPUESTO_OBSERVADO' if r[8] else 'CODIGO_ANUAL_UNICO_SIN_PROPUESTA_PREVIA'
    if state!=r[10] or codes!=set(filter(None,r[9].split('; '))):mismatch.append(key)
    counts[state]+=1
    code=next(iter(codes)) if state in docstates else ''
    results.append({'observacion_id':len(results)+1,'persona':k,'CODCLI':cli,'carrera':c,'sede_dimension':site,'jornada_sies':j,'plan':plan,'ano':y,'periodo':t,
        'codigo_propuesto_inicial':r[8],'codigos_anuales_documentados':sorted(codes),'codigo_documental_atribuible':code,
        'codigo_interno_adoptado':code,'estado_documental':state,'estado_interno':state,'regla':'IDENTIDAD_FAMILIA_ANIO_CONTEXTO_DA_NO_MULTIPLE' if code else '',
        'evidencias_matricula':ev,'fuentes_promedios':pr[key], 'contextos_DA':ds,'tipo_doc_normalizado':'RUT','clasificacion':'B/C; E fecha efectiva del plan',
        'aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO'})
QA['linea_base']={'estados':dict(counts),'discrepancias_observaciones':len(mismatch),'documental':partition(results,'codigo_documental_atribuible')}
dump(O/'QA_BASE_INICIAL.json',QA)
assert not mismatch,'Diferencias frente al código anual: no avanzar'
progress(2,3,'Línea base documental reconstruida; verificar equivalencias internas')
v8=load(ARGS.reanudacion/'v8.json' if ARGS.reanudacion else '/tmp/ipss_cruce_historico_20261023/resultados.json');v9=load(ARGS.reanudacion/'v9.json' if ARGS.reanudacion else '/tmp/ipss_validacion_2165_20261023/resultados.json')
resume=P/'reanudacion';resume.mkdir()
dump(resume/'antecedentes_minimos.json',[s for s in old if s['name'] in ['HASHES','CONTRASTE_63','EVIDENCIAS_SIES']]);dump(resume/'v8.json',v8);dump(resume/'v9.json',v9)
if ARGS.reanudacion:
    fixed=json.loads((ARGS.reanudacion/'HASHES.json').read_text());assert all(sha(ARGS.reanudacion/n)==h for n,h in fixed.items())
dump(resume/'HASHES.json',{p.name:sha(p) for p in resume.iterdir() if p.is_file()})
v8by={tuple(x[1:9]):x for x in v8};v9by={tuple(x[1:9]):x for x in v9}
manualsrc=source(R/'procesos/caracterizacion/caracterizacion.py');tree=ast.parse(manualsrc.read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_fcu2026_manual_equivalencias_cod_car')
assign=next(n for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows' for t in n.targets))
manual={(x[1],x[4],x[3]):x[5] for x in ast.literal_eval(assign.value)}
snapshot=load(R/'data/diccionario_sies_umas/20261015/evidencia/caracterizacion_reglas_y_fuentes.json')['equivalencias_manual_fcu2026']['filas']
assert manual=={(x['CODCARPR'],x['SEDE'],x['JORNADA']):x['CODIGO_UNICO_SIES'] for x in snapshot}
offidx=defaultdict(list)
for x in M['oferta_anual']:offidx[x['anio'],x['codigo_unico'].rsplit('V',1)[0]].append(x)
tp={'Plan Regular':'1','Plan Especial':'2','Plan Regular de Continuidad':'3'}
offcode=defaultdict(list)
for x in M['oferta_anual']:offcode[x['anio'],x['codigo_unico']].append(x)
adopted=Counter();manualdiscrep=0
for x in results:
    key=(x['persona'],x['CODCLI'],x['carrera'],x['sede_dimension'],x['jornada_sies'],x['plan'],x['ano'],x['periodo']);old9=v9by.get(key)
    x['estado_antes_v10']=old9[43] if old9 else x['estado_interno']
    if not old9:continue
    code=manual.get((x['carrera'],'RE',revj[x['jornada_sies']]),'');pm=plans.get(x['plan'],{});g=G.get((x['carrera'],'RE',revj[x['jornada_sies']]),{})
    planok=bool(pm and x['carrera'] in pm['carreras_internas'] and pm['sedes']==['RE'])
    profok=any([o['duracion_total'],tp.get(o['tipo_plan_sies'])] in g.get('perfiles_duracion_tipo',[]) for o in offcode[int(x['ano']),code])
    other=any(e['codigo'].rsplit('V',1)[0]==code.rsplit('V',1)[0] and e['codigo']!=code for e in muall[x['persona']]) if code else False
    peers={cli for (c,j),units in allpr.items() if c==x['carrera'] for k,cli,p,y,t in units if k==x['persona'] and y==x['ano']}
    valid=bool(x['ano']=='2026' and code and old9[19]==code and planok and profok and not other and len(peers)==1)
    manualdiscrep+=valid!=bool(old9[44])
    if valid:
        x['codigo_interno_adoptado']=code;x['estado_interno']='CORRESPONDENCIA_INTERNA_REGLA_VIGENTE';x['regla']='FCU2026_SCOPE_2026_PLAN_CARRERA_SEDE_SIN_ALTERNATIVA';adopted[x['carrera']]+=1
        x['fuente_equivalencia']={'archivo':str(manualsrc),'funcion':fn.name,'linea':fn.lineno,'clasificacion':'D'}
QA['equivalencias']={'adoptadas':dict(adopted),'discrepancias':manualdiscrep,'interno':partition(results,'codigo_interno_adoptado')}
assert manualdiscrep==0
dump(O/'QA_BASE_INICIAL.json',QA)
progress(3,1,'Prueba retrospectiva con objetivos separados y partición por persona')
def yearset(v):
    vv={int(z) for z in v if str(z).isdigit() and 2007<=int(z)<=2026};return next(iter(vv)) if len(vv)==1 else None
def predict(g,y,profiles=None):
    if not g:return [],'SIN_GRUPO'
    if y is None:return [],'FECHA_AUSENTE_O_MULTIPLE'
    prof={tuple(p) for p in g['perfiles_duracion_tipo']} if profiles is None else profiles
    if not prof:return [],'SIN_PERFIL'
    candidates={o['codigo_unico'] for fam in g['familias'] for o in offidx[y,fam]
        if (o['duracion_total'],tp.get(o['tipo_plan_sies'])) in prof and o['vigencia']=='Vigente con estudiantes nuevos'}
    return sorted(candidates),'UNICO' if len(candidates)==1 else 'EMPATE_NUEVOS' if candidates else 'SIN_OFERTA_NUEVOS_COMPATIBLE'
tests=defaultdict(Counter);testpeople=defaultdict(lambda:defaultdict(set));training=defaultdict(Counter)
trajectory=defaultdict(set)
for (c,j),units in allpr.items():
    for k,cli,plan,y,t in units:trajectory[k,cli,c].add((y,t,plan))
for x in results:
    k,cli,c,j,y=x['persona'],x['CODCLI'],x['carrera'],x['jornada_sies'],x['ano'];g=G.get((c,'RE',revj[j]));fam=g['familias'] if g else []
    es=[e for e in mu[k,y] if e['codigo'].rsplit('V',1)[0] in fam]
    ds=[d for d in da[cli,c] if d['persona']==k and jmap.get(d['JORNADA'])==j]
    dates={'DA_ANOINGRESO':yearset([d['ANOINGRESO'] for d in ds]),'MU_INGRESO_ACTUAL':yearset([e['ingreso_actual'] for e in es]),'MU_INGRESO_ORIGEN':yearset([e['ingreso_origen'] for e in es])}
    types={p[1] for p in g['perfiles_duracion_tipo']} if g else set();typ='REGULAR' if types=={'1'} else 'CONTINUIDAD' if types=={'3'} else 'TIPO_NO_UNICO'
    x.update(fechas_declaradas=dates,tipo_perfil_grupo=typ,origen_perfil='GRUPO_GOBERNADO_NO_PERFIL_INDIVIDUAL',trayectoria_planes_observada=sorted(trajectory[k,cli,c]),
        fecha_efectiva_plan='',reingreso_acreditado=False,fold_persona=int(hashlib.sha256(k.encode()).hexdigest()[:12],16)%5)
    x['planes_distintos_expediente']=len({p for y,t,p in trajectory[k,cli,c]})
    x['cambio_plan_efectivo_acreditado']=False
    if x['codigo_documental_atribuible']:
        for meth,yy in dates.items():
            if typ=='CONTINUIDAD' and meth!='MU_INGRESO_ACTUAL':codes=[];state='EXCLUIDO_FECHA_NO_PROPIA_CONTINUIDAD'
            else:
                codes,state=predict(g,yy)
                if len(codes)==1:state='ACIERTO' if codes[0]==x['codigo_documental_atribuible'] else 'ERROR'
            tests[meth,typ][state]+=1;testpeople[meth,typ][state].add(k)
        # Training counts by person, never per subject row; target-code profile only from other folds.
        for o in offcode[int(y),x['codigo_documental_atribuible']]:
            training[c,j,x['fold_persona']][k,o['duracion_total'],tp.get(o['tipo_plan_sies'])]=1
    if not x['codigo_interno_adoptado']:
        esall=[e for e in muall[k] if e['codigo'].rsplit('V',1)[0] in fam]
        yy=yearset([e['ingreso_actual'] for e in esall]) if typ=='CONTINUIDAD' else dates['DA_ANOINGRESO']
        codes,state=predict(g,yy);x['candidatos_calculados']=codes;x['codigo_propuesto']=codes[0] if len(codes)==1 else '';x['estado_propuesta']=state
        x['requisito_pendiente']='Fecha efectiva de asignación del plan al CODCLI y regla de migración/reingreso; perfil de grupo no acredita plan histórico'
        if state=='EMPATE_NUEVOS':x['requisito_pendiente']='Atributo discriminante o equivalencia explícita para las versiones coexistentes, con fecha efectiva'
        elif state!='UNICO':x['requisito_pendiente']='Completar '+state+' con fuente del programa/plan y período, sin inferirla del nombre'
    else:x.update(candidatos_calculados=[],codigo_propuesto='',estado_propuesta='NO_NECESARIA',requisito_pendiente='Asignación histórica efectiva del plan y aceptación SIES no acreditadas; código observado/interno separado')
cv=Counter();cvpersons=defaultdict(set);cvfold=defaultdict(Counter)
for x in results:
    if not x['codigo_documental_atribuible'] or x['tipo_perfil_grupo']!='REGULAR':continue
    c,j=x['carrera'],x['jornada_sies'];fold=x['fold_persona'];prof={(dur,typ) for f in range(5) if f!=fold for k,dur,typ in training[c,j,f]}
    codes,state=predict(G.get((c,'RE',revj[j])),x['fechas_declaradas']['MU_INGRESO_ACTUAL'],prof)
    if len(codes)==1:state='ACIERTO' if codes[0]==x['codigo_documental_atribuible'] else 'ERROR'
    cv[state]+=1;cvpersons[state].add(x['persona']);cvfold[fold][state]+=1
    x['prueba_fuera_persona']={'candidatos':codes,'resultado':state,'fold':fold}
QA['retrospectiva']=[{'metodo':m,'tipo':t,'observaciones':dict(v),'personas_no_aditivas':{s:len(k) for s,k in testpeople[m,t].items()}} for (m,t),v in tests.items()]
QA['validacion_por_persona']={'metodo':'5 particiones deterministas por persona; perfil aprendido solo otras particiones; familias heredadas mantienen dependencia residual',
    'resultados':dict(cv),'personas_no_aditivas':{s:len(k) for s,k in cvpersons.items()},'particiones':dict(cvfold)}
assert tests['MU_INGRESO_ACTUAL','REGULAR']==Counter({'ACIERTO':15029,'ERROR':1494,'EMPATE_NUEVOS':1044,'SIN_OFERTA_NUEVOS_COMPATIBLE':257,'FECHA_AUSENTE_O_MULTIPLE':2})
progress(4,2,'Cronologías observadas; no equivalen a fecha efectiva ni reingreso')
expkeys={(x['persona'],x['CODCLI'],x['carrera']) for x in results}
QA['cronologia']={'expedientes_con_mas_de_un_plan_observado':sum(len({p for y,t,p in v})>1 for key,v in trajectory.items() if key in expkeys),
    'observaciones_con_mas_de_un_plan_expediente':sum(x['planes_distintos_expediente']>1 for x in results),
    'fechas_efectivas_plan_acreditadas':sum(bool(x['fecha_efectiva_plan']) for x in results),
    'limite':'Cronología de actividad y etiquetas de plan; no acto de migración ni fecha original confirmada'}
focus=[x for x in results if not x['codigo_interno_adoptado']]
QA['foco_actual']={'estados_candidato':dict(Counter(x['estado_propuesta'] for x in focus)), 'candidatos_unicos':sum(bool(x['codigo_propuesto']) for x in focus),
    'cierres_nuevos_documentales':0,'cierres_nuevos_internos':0,'motivo':'No hay nueva fecha efectiva ni equivalencia aprobada; candidatos no promovidos'}
progress(5,3,'Reglas existentes revalidadas; propuestas nuevas sin adoptar')
# Keep observation cardinality constant, sources nested instead of many-to-many expansions.
csvout(P/'OBSERVACIONES_PRIVADAS.csv',results);dump(P/'OBSERVACIONES_PRIVADAS.json',results)
csvout(O/'INVENTARIO_FUENTES.csv',INVENTORY)
agg=defaultdict(Counter)
for x in results:
    a=agg[x['carrera'],x['jornada_sies'],x['ano']];a['observaciones']+=1;a['documentales']+=bool(x['codigo_documental_atribuible']);a['internas']+=bool(x['codigo_interno_adoptado']);a['propuestas_no_adoptadas']+=bool(x['codigo_propuesto'])
csvout(O/'RESUMEN_CARRERA_ANIO.csv',[{'carrera':k[0],'jornada':k[1],'ano':k[2],**dict(v),'pendientes_documentales':v['observaciones']-v['documentales'],'pendientes_internos':v['observaciones']-v['internas'],'clasificacion':'C'} for k,v in sorted(agg.items())])
progress(6,3,'Registro completo privado escrito; ninguna identidad en el resumen')
QA['preservacion_fuentes']=all(sha(p)==h for p,h in HASHES.items())
QA['registros_privados']=len(results);QA['sin_expansion']=len(results)==len(pr)
QA['particiones_disjuntas']=all(sum(v[k] for k in ['sin_pendientes','parcialmente_resueltas','ninguna_observacion_resuelta'])==5901 for v in [QA['linea_base']['documental'],QA['equivalencias']['interno']])
QA['estado']='OK_CON_ADVERTENCIAS';QA['limites']=['Cortes DA no acreditados','Plan histórico no acreditado','Oferta y grupos heredados no son validación externa','Aceptación individual SIES no acreditada','Otros procesos verificados por huella del índice, no relectura independiente completa en esta ejecución']
dump(O/'RESULTADOS_QA.json',QA);dump(O/'FUENTES_HASHES.json',HASHES)
dump(P/'MANIFEST_PRIVADO.json',{'fuentes':HASHES,'salidas':{p.name:sha(p) for p in P.iterdir() if p.is_file()},'privacidad':'Fuera de cualquier repositorio Git; directorio 700; solo identidad y campos académicos necesarios'})
dump(O/'MANIFEST.json',{'fecha':STAMP,'proceso':'Conciliación UMAS–SIES histórica','clasificacion':'B/C/D/E','privado':str(P),'salidas_privadas_hashes':{p.name:sha(p) for p in P.iterdir() if p.is_file()},'git_antes':{p:{k:v for k,v in d.items() if k!='status'} for p,d in GIT.items()},'canon_modificado':False,'commit':False,'push':False,'script':str(Path(__file__)),'script_sha256':sha(__file__)})
progress(7,3,'Particiones conciliadas; análisis ejecutado, con pendientes semánticos visibles')
(O/'BITACORA.md').write_text('\n\n'.join(LOG)+'\n')
print(json.dumps({'output':str(O),'privado':str(P),'qa':QA},ensure_ascii=False),flush=True)

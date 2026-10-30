"""H005: presentación de catálogos y agregados gobernados; no enlaza personas.

Las sumas son exclusivamente agrupaciones de filas agregadas ya publicadas.
No importa motores H002 ni lee bases individuales. FUENTES_FIJADAS no se renueva.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, json, hashlib, re, subprocess, sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
RUNTIME=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
BOOK='RESUMEN_CRUCE_SIES_UMAS_20261030.xlsx'
YEARS=list(range(2007,2027))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def col(n):
    s=''
    while n:n,m=divmod(n-1,26);s=chr(65+m)+s
    return s
def joined(v):return ' / '.join(sorted(set(str(x) for x in v if x not in [None,'','NULL']))) or 'E'
def validplan(p):return bool(p) and p not in {'SIN_ENLACE','PLAN_NO_OBSERVADO','NO_ENLAZADO_A_MRUN','E'}
def fuentes():
    a=json.loads((OUT/'FUENTES_FIJADAS.json').read_text())
    for x in a:
        if sha(x['ruta'])!=x['sha256']:raise ValueError('Fuente alterada: '+x['id'])
    return {x['id']:x for x in a}
def model():
    F=fuentes()
    def js(k):return json.loads(Path(F[k]['ruta']).read_text())
    def cs(k,sep=';'):return list(csv.DictReader(open(F[k]['ruta'],encoding='utf-8-sig'),delimiter=sep))
    master=js('MAESTRO');table=js('H002');h27={r['codigo_unico']:r for r in table['filas'] if r['anio']==2027}
    h26={r['codigo_unico']:r for r in table['filas'] if r['anio']==2026}
    matrix=cs('MATRIZ');mu=[r for r in matrix if r['origen']=='MU_DATOS_ALUMNOS']
    types=cs('TIPOS_V2');v3=cs('TIPOS_V3',',');results=js('RESULTADOS')
    public={};latest={};history=defaultdict(dict);public_rows={}
    with open(F['PUBLICA']['ruta'],encoding='latin1') as f:
        for i,r in enumerate(csv.DictReader(f,delimiter=';'),2):
            if r['CÓDIGO DE INSTITUCIÓN']!='162':continue
            y=int(r['AÑO'].removeprefix('MAT_'));c=r['CÓDIGO CARRERA'];n=int(r['TOTAL MATRÍCULA'])
            assert (c,y) not in public
            public[c,y]=n;history[c][y]=n;public_rows[c,y]=r
            if c not in latest or y>latest[c][0]:latest[c]=(y,r,i)
    assert len(public)==472
    # Control preexistente de SIES individual frente a publicación, sin leer microdatos.
    for r in js('CONTROL_SIES')['filas']:
        assert r['diferencia']==0 and public[r['codigo_sies'],r['anio']]==r['publicacion']==r['registro_individual']
    codes=sorted(set(history)|set(h27)|set(h26)|{r['codigo_sies'] for r in mu})
    pairs={};nmu=Counter();nlink=Counter();nplan=Counter();plans_seen=defaultdict(set)
    def pair(c,p):
        return pairs.setdefault((c,p),{'codcarpr':set(),'sites':set(),'shifts':set(),'years':Counter(),'methods':set(),'sources':set(),'intakes':set(),'notes':set()})
    for r in mu:
        c=r['codigo_sies'];y=int(r['anio']);n=int(r['matriculas']);nmu[c,y]+=n
        if r['estado']=='SIN_ENLACE':continue
        nlink[c,y]+=n;p=r['plan_umas']
        if validplan(p):nplan[c,y]+=n
        q=pair(c,p);q['codcarpr'].add(r['codcarpr']);q['sites'].add(r['sede_umas']);q['shifts'].add(r['jornada_umas'])
        q['years'][y]+=n;q['methods'].add('CRUCE_PERSONA_MU_2022_2026');q['sources'].add('MATRIZ')
        if r['ingreso_umas_anio'].isdigit():q['intakes'].add(int(r['ingreso_umas_anio']))
        q['notes'].add(r['plan_respaldo'])
        if validplan(p):plans_seen[p].add(c)
    # Reutiliza selecciones explícitas de H002. No convierte la lista general
    # de candidatos ni las equivalencias del maestro en vínculos acreditados.
    for c,r in h27.items():
        if r['estado'] not in {'CONTINUA','VERSION_MULTIPLE_RESUELTA','APROBADA_D_2027'}:continue
        groups=r['resoluciones_grupo']
        if not groups and r['estado']=='APROBADA_D_2027':groups=[dict(x,codigo_sies_aprobado=c,planes_catalogados_candidatos=x['plan_umas']) for x in r['candidatos_internos']]
        for g in groups:
            sel=g.get('resolucion_nuevos_2027',{}).get('seleccion')
            approved=g.get('codigo_sies_aprobado')
            if approved!=c and sel!=c:continue
            ps=g.get('planes_explicitos_aprobados') or g.get('planes_catalogados_candidatos',[])
            if not ps:ps=['PLAN_NO_OBSERVADO']
            for p in ps:
                q=pair(c,p);q['codcarpr'].add(g['codcarpr']);q['sites'].add(g.get('sede_umas',''));q['shifts'].add(g.get('jornada_umas',''))
                q['methods'].add('APROBACION_D_2027' if approved==c else 'REGLA_MU_2027');q['sources'].add('H002')
                q['notes'].add('Catálogo 2027; no atribución retroactiva ni acreditación de cohorte/malla')
                if validplan(p):plans_seen[p].add(c)
    for c in codes:
        if not any(k[0]==c for k in pairs):pair(c,'')
    type_by=defaultdict(list);cand_by=defaultdict(list)
    for r in types:type_by[r['plan_umas']].append(r)
    for r in v3:cand_by[r['plan_umas']].append(r)
    def typ(p):
        a=type_by[p];v={r['tipo_plan'] for r in a}
        return (next(iter(v)) if len(v)==1 else 'E',joined(r['clase'] for r in a))
    def attrs(c):
        h=h27.get(c,h26.get(c,{}));r=latest.get(c,(None,{},None))[1];m=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)',c)
        return [c,h.get('nombre_carrera') or r.get('NOMBRE CARRERA','E'),m[1] if m else 'E',m[3] if m else 'E',m[4] if m else 'E',h.get('modalidad') or r.get('MODALIDAD') or 'E',h.get('nivel_global') or r.get('NIVEL GLOBAL','E'),h.get('tipo_plan') or r.get('TIPO DE PLAN DE LA CARRERA','E')]
    def activeyears(c):return sorted(y for y,n in history[c].items() if n>0)
    def reason(c,hasplan):
        h=h27.get(c,{});state=h.get('estado');ys=activeyears(c)
        if state=='FUERA_ALCANCE':return 'FUERA_ALCANCE'
        if hasplan:return 'UNIDO'
        if state=='NUEVO_2027_SIN_PLAN_E':return 'NUEVO_2027_SIN_ALUMNOS'
        if state=='HISTORICO_SIN_MATRICULA_RECIENTE':return 'HISTORICO_SIN_MATRICULA_RECIENTE'
        if ys and max(ys)<2022:return 'SOLO_ANTES_2022'
        if sum(nlink[c,y] for y in range(2022,2027)):return 'PLAN_NO_OBSERVADO'
        return 'SIN_ENLACE'
    closure={'UNIDO':'Reutilizar el vínculo según su período y método; no extenderlo a otras cohortes.',
      'FUERA_ALCANCE':'Excluido del seguimiento por decisión D; catálogo descriptivo conservado.',
      'NUEVO_2027_SIN_ALUMNOS':'MU 2027: primera matrícula y cuadratura por código y total.',
      'HISTORICO_SIN_MATRICULA_RECIENTE':'Sin necesidad de paridad 2027; conservar historia.',
      'SOLO_ANTES_2022':'Cierre E: Datos Alumnos no conserva el histórico; solo reabrir con registro UMAS anual.',
      'PLAN_NO_OBSERVADO':'Expediente enlazado, plan anual no observado; nueva evidencia de plan.',
      'SIN_ENLACE':'E: nueva evidencia gobernada; no repetir enlaces con las mismas fuentes.'}
    blocks=[];controls=[];sheets=[]
    def sheet(name,title,widths,freeze,notes):
        s=dict(name=name,title=title,widths=widths,freeze=freeze,notes=notes,blocks=[],renders=[]);sheets.append(s);return s
    def block(s,id,title,row,column,headers,rows,source,formats=None,formulas=None):
        b=dict(id=id,title=title,row=row,column=column,headers=headers,rows=rows,source=source,formats=formats or {},formulas=formulas or {})
        s['blocks'].append(b)
        for i,r in enumerate(rows):
            assert len(r)==len(headers),(id,len(r),len(headers))
            for j,x in enumerate(r):
                a=f'{col(column+j+1)}{row+1+i}';controls.append(dict(hoja=s['name'],celda=a,esperado=x,fuente=source,registro=i+1,campo=headers[j],formula=b['formulas'].get(a)))
        return b
    fmtcount='[>=1000000]#"."000"."000;[>=1000]#"."000;0'
    base=[]
    for (c,p),q in sorted(pairs.items()):
        ys=activeyears(c);t,cl=typ(p);has=validplan(p);mot=reason(c,has)
        method=joined(q['methods']) if q['methods'] else ('SOLO_SIES_PRE_2022' if ys and max(ys)<2022 else 'SIN_UNION')
        base.append(attrs(c)+[min(ys) if ys else 'n.a.',max(ys) if ys else 'n.a.']+[public.get((c,y),0) for y in YEARS]+[
          h27.get(c,{}).get('vigencia_2027','n.a.'),joined(q['codcarpr']),p or 'E: sin plan',t,cl]+[q['years'][y] for y in range(2022,2027)]+[
          method,'UNIDO' if has and mot=='UNIDO' else 'PENDIENTE',mot,'D/C' if 'APROBACION_D_2027' in q['methods'] else ('B/C' if has else 'E'),joined(q['sources']|{'PUBLICA'}),joined(q['notes'])])
    s1=sheet('1_Base_Completa','IPSS · Base de códigos SIES y planes UMAS',[25,54,9,10,10,20,18,26,12,12]+[12]*20+[12,24,26,20,12]+[14]*5+[48,16,40,12,25,65],7,[
      (3,'Filas de catálogo: código × plan. La matrícula SIES 2007–2026 se repite entre planes: NO sumar esas columnas aquí.'),
      (4,'Los enlaces MU son matrículas-año seleccionadas de H002g. Un enlace a expediente no prueba un plan anual. Fuentes y hashes en hoja 4.'),
      (5,'Corte 30-10-2026. A oficial; B observado; C implementación/inferencia; D decisión interna; E pendiente. Sin nuevos cruces.')])
    bh=['Código SIES','Carrera SIES','Sede SIES','Jornada SIES','Versión','Modalidad','Nivel','Tipo plan SIES','Primer año','Último año']+[str(y) for y in YEARS]+['Vigencia 2027','CODCARPR','Plan UMAS','Tipo UMAS v2','Clase tipo']+['Enlazadas '+str(y) for y in range(2022,2027)]+['Método de unión','Estado','Motivo','Clase unión','Fuente (ID)','Límite / alcance']
    block(s1,'Base','Una fila por código y plan observado o candidato explícito de H002',7,0,bh,base,'PUBLICA; MATRIZ; H002; TIPOS_V2',{**{i:fmtcount for i in list(range(10,30))+list(range(35,40))},8:'0',9:'0'})
    s1['renders']=['A1:H18','AE6:AN18','AO6:AT18']
    # Un código por fila: dimensión aditiva para todas las cifras SIES.
    detail=[]
    for c in codes:
        ys=activeyears(c);a=attrs(c)
        detail.append(a[:2]+[a[6],min(ys) if ys else 'n.a.',max(ys) if ys else 'n.a.',len(ys)]+[public.get((c,y),0) for y in YEARS]+[h27.get(c,{}).get('estado','SIN_OFERTA_2027'),1 if ys else 0,'PUBLICA; H002',1 if ys and max(ys)<2022 else 0])
    s2=sheet('2_Programas_SIES','IPSS · Programas SIES históricos y oferta 2027',[25,54,18,14,14,14]+[12]*20+[40,16,25,4,14,18,4]+[14]*9,14,[(3,'Un código por fila. Cero = sin matrícula publicada en ese año; no equivale a cierre de oferta.'),(4,'Atributos: catálogo 2027 si existe; si no, última matrícula publicada. Históricos y oferta son universos distintos.')])
    s2['freeze']=5
    s2['notes'].append((12,'Detalle A14; oferta 2027 en S5; serie anual y gráfico en AE5. Use el cuadro de nombres de Excel para ir a esas celdas.'))
    s2['widths'][29]=20
    b2=block(s2,'Programas','Detalle único por código',14,0,['Código SIES','Carrera SIES','Nivel','Primer año','Último año','Años activos']+[str(y) for y in YEARS]+['Estado H002 2027','Con historia (1/0)','Fuente (ID)','Solo antes de 2022 (1/0)'],detail,'PUBLICA; H002',{**{i:fmtcount for i in range(6,26)},3:'0',4:'0'})
    end=14+len(detail);level=Counter(r[2] for r in detail if r[27]);summ=[['Con matrícula 2007–2026',sum(r[27] for r in detail)],['Con matrícula 2026',sum(r[25]>0 for r in detail)],['Catálogo H002 2026',len(h26)],['Oferta H002 2027',len(h27)],['Universo unión de catálogos',len(detail)]]
    fs={f'B{6+i}':f'=SUM(AB15:AB{end})' if i==0 else f'=COUNTIFS(Z15:Z{end},">0")' if i==1 else f'=COUNTA(A15:A{end})' for i in [0,1,4]}
    summ.append(['Solo matrícula anterior a 2022',sum(r[29] for r in detail)]);fs['B11']=f'=SUM(AD15:AD{end})'
    block(s2,'ResumenSIES','Universos separados',5,0,['Universo','Códigos'],summ,'PUBLICA; H002',formulas=fs)
    block(s2,'Niveles','Históricos por nivel',5,3,['Nivel','Códigos'],[[k,v] for k,v in sorted(level.items())],'PUBLICA',formulas={f'E{6+i}':f'=COUNTIFS(C15:C{end},D{6+i},AB15:AB{end},1)' for i,k in enumerate(sorted(level))})
    annual=[[str(y),sum(public.get((c,y),0)>0 for c in codes)] for y in YEARS]
    block(s2,'Activos','Códigos con matrícula por año',5,30,['Año','Códigos activos'],annual,'PUBLICA',formulas={f'AF{6+i}':f'=COUNTIFS({col(7+i)}15:{col(7+i)}{end},">0")' for i in range(20)})
    statecounts=Counter(r['estado'] for r in h27.values())
    block(s2,'Oferta','Oferta 2027',5,7,['Estado','Códigos'],[[k,v] for k,v in sorted(statecounts.items())],'H002',formulas={f'I{6+i}':f'=COUNTIFS(AA15:AA{end},H{6+i})' for i,k in enumerate(sorted(statecounts))})
    # La oferta usa un bloque ancho propio; no hereda las columnas de años.
    ob=s2['blocks'][-1];ob['column']=18
    ob['formulas']={f'T{6+i}':f'=COUNTIFS(AA15:AA{end},S{6+i})' for i,k in enumerate(sorted(statecounts))}
    for c in controls:
        if c['hoja']==s2['name'] and c['fuente']=='H002' and c['campo'] in ['Estado','Códigos']:
            # Solo el bloque Oferta; los otros tienen fuente compuesta.
            r=c['registro']+5;c['celda']=('S' if c['campo']=='Estado' else 'T')+str(r);c['formula']=ob['formulas'].get(c['celda'])
    s2['widths'][18]=42;s2['widths'][19]=16
    s2['chart']={'range':'AE5:AF25','from':'AH5','to':'AR25'};s2['renders']=['A1:E11','A13:F26','S4:T12','AE4:AR26']
    # UMAS: 236 planes únicos del maestro; otros identificadores en MU no se
    # incorporan silenciosamente al catálogo. Se muestran solamente en Base.
    umas=[];cdim=defaultdict(set)
    for p in sorted(master['planes_umas'],key=lambda x:x['CODPESTUD']):
        name=p['CODPESTUD'];cars={x['Codcarr'] for x in p['contextos_catalogo']}|{x for x in p['carreras_promedios'] if x not in {'NULL',''}}
        for c in cars:cdim[c].add(name)
        intake={i for (c,pl),q in pairs.items() if pl==name for i in q['intakes'] if i>1900};t,cl=typ(name)
        umas.append([name,joined(cars),joined(x['Sede'] for x in p['contextos_catalogo']),joined(p['jornadas_promedios']),t,cl,
          min(intake) if intake else 'E',max(intake) if intake else 'E',joined(plans_seen[name]),p['estado_equivalencia'],
          'UNIDO' if plans_seen[name] else 'SIN_UNION',joined(x['clasificacion'] for x in cand_by[name])+' (CANDIDATO)',
          'MAESTRO; TIPOS_V2; TIPOS_V3; MATRIZ; H002','Ingreso observado solo en enlaces agregados H002g; no historia completa'])
    s3=sheet('3_Codigos_UMAS','IPSS · Catálogo de planes y códigos UMAS',[27,30,16,17,24,14,14,14,55,36,18,37,35,65,4,24,15,18,45],13,[(3,'236 planes del maestro; CODCARPR distintos en sus contextos y actividad. La v3 se muestra como CANDIDATO y no reemplaza la v2.'),(4,'Un plan por fila. Los candidatos del maestro no cuentan como unión. Ingreso inicial/final: solo lo observado en la matriz reutilizada.')])
    n3=13+len(umas);block(s3,'Planes','Detalle de planes del maestro',13,0,['Plan UMAS','CODCARPR','Sede UMAS','Jornada UMAS','Tipo v2','Clase v2','Ingreso inicial','Ingreso final','Códigos SIES enlazados','Estado en maestro','Unión','Tipo v3 candidato','Fuente (ID)','Límite'],umas,'MAESTRO; TIPOS_V2; TIPOS_V3; MATRIZ; H002',{6:'0',7:'0'})
    ts=Counter(r[4] for r in umas);ul=sum(r[10]=='UNIDO' for r in umas)
    block(s3,'ResumenUMAS','Planes del maestro',5,0,['Tipo v2','Planes','Con unión'],[[k,v,sum(r[4]==k and r[10]=='UNIDO' for r in umas)] for k,v in sorted(ts.items())],'MAESTRO; TIPOS_V2',formulas={**{f'B{6+i}':f'=COUNTIFS(E14:E{n3},A{6+i})' for i,k in enumerate(sorted(ts))},**{f'C{6+i}':f'=COUNTIFS(E14:E{n3},A{6+i},K14:K{n3},"UNIDO")' for i,k in enumerate(sorted(ts))}})
    dim=[[c,len(ps),'UNIDO' if any(plans_seen[p] for p in ps) else 'SIN_UNION',joined(ps)] for c,ps in sorted(cdim.items())]
    block(s3,'CODCARPR','Dimensión CODCARPR (no sumar entre planes)',13,15,['CODCARPR','Planes','Unión','Planes asociados'],dim,'MAESTRO; MATRIZ; H002')
    block(s3,'UniversosUMAS','Universos',5,5,['Universo','Cantidad'],[['Planes',len(umas)],['CODCARPR distintos',len(dim)],['Planes con unión',ul],['Planes sin unión',len(umas)-ul],['CODCARPR con unión',sum(r[2]=='UNIDO' for r in dim)],['CODCARPR sin unión',sum(r[2]=='SIN_UNION' for r in dim)]],'MAESTRO; MATRIZ; H002',formulas={'G6':f'=COUNTA(A14:A{n3})','G7':f'=COUNTA(P14:P{13+len(dim)})','G8':f'=COUNTIFS(K14:K{n3},"UNIDO")','G9':f'=COUNTIFS(K14:K{n3},"SIN_UNION")','G10':f'=COUNTIFS(R14:R{13+len(dim)},"UNIDO")','G11':f'=COUNTIFS(R14:R{13+len(dim)},"SIN_UNION")'})
    s3['freeze']=5
    s3['notes'].append((12,'Detalle de planes A13; listado único de CODCARPR en P13. Los dos catálogos tienen unidades distintas.'))
    s3['renders']=['A1:G12','A12:H24','P12:S24']
    cross=[]
    for c in codes:
        cp=[(p,q) for (code,p),q in pairs.items() if code==c];ps=sorted(p for p,q in cp if validplan(p));rs=reason(c,bool(ps));methods={m for p,q in cp for m in q['methods']}
        cross.append([c,'UNIDO' if rs=='UNIDO' else 'PENDIENTE',joined(methods) if methods else ('SOLO_SIES_PRE_2022' if rs=='SOLO_ANTES_2022' else 'SIN_UNION'),joined(ps),rs,closure[rs],
          sum(nmu[c,y] for y in range(2022,2027)),sum(nlink[c,y] for y in range(2022,2027)),sum(nplan[c,y] for y in range(2022,2027)),
          h27.get(c,{}).get('estado','SIN_OFERTA_2027'),'B/C/D; E límites','MATRIZ; H002; CIERRE; TECHO'])
    s4=sheet('4_Cruce_SIES_UMAS','IPSS · Cobertura del cruce y pendientes',[25,20,48,55,40,65,16,18,18,40,18,28,4,45,16,4,42,15],14,[(3,'Cobertura a expediente ≠ disponibilidad del plan anual. Uniones históricas B/C y catálogo 2027 C/D se distinguen; no certifican identidad curricular.'),(4,'Antes de 2022: solo SIES; cuadratura con foto actual UMAS cerrada E. No se suman SIES_INDIVIDUAL, MU_DATOS_ALUMNOS y CUADRATURA_TOTALES_C.')])
    nc=14+len(cross);block(s4,'Cruces','Detalle único por código SIES',14,0,['Código SIES','Estado','Método','Planes enlazados','Motivo','Forma de cierre','MU seleccionada','Enlace expediente','Con plan anual','Estado H002 2027','Clase','Fuente (ID)'],cross,'MATRIZ; H002; CIERRE; TECHO',{6:fmtcount,7:fmtcount,8:fmtcount})
    yr=[]
    for a in results['anual']:
        y=a['anio'];tot=sum(nmu[c,y] for c in codes);linked=sum(nlink[c,y] for c in codes);known=sum(nplan[c,y] for c in codes)
        assert tot==a['seleccionadas'] and linked==a['enlace_seleccionadas']
        yr.append([y,len({c for c in codes if nmu[c,y]>0}),len({c for c in codes if nlink[c,y]>0}),tot,linked,linked/tot,known])
    alltot=sum(r[3] for r in yr);alllink=sum(r[4] for r in yr);allplan=sum(r[6] for r in yr)
    yr.append(['2022–2026',len({c for c in codes if sum(nmu[c,y] for y in range(2022,2027))}),len({c for c in codes if sum(nlink[c,y] for y in range(2022,2027))}),alltot,alllink,alllink/alltot,allplan])
    formulas={f'F{6+i}':f'=E{6+i}/D{6+i}' for i in range(6)}
    formulas.update({'B11':f'=COUNTIFS(G15:G{nc},">0")','C11':f'=COUNTIFS(H15:H{nc},">0")','D11':f'=SUM(G15:G{nc})','E11':f'=SUM(H15:H{nc})','G11':f'=SUM(I15:I{nc})'})
    block(s4,'Cobertura','MU seleccionada de H002g · matrículas-año, no personas únicas',5,0,['Año','Códigos MU','Con enlace','Matrículas MU','Enlazadas','% enlace','Con plan'],yr,'RESULTADOS/anual; MATRIZ',formats={3:fmtcount,4:fmtcount,5:'0.0%',6:fmtcount},formulas=formulas)
    reasons=Counter(r[4] for r in cross)
    block(s4,'Pendientes','Unión de catálogos: motivos excluyentes',5,13,['Motivo','Códigos'],[[k,v] for k,v in sorted(reasons.items())],'MATRIZ; H002; CIERRE',formulas={f'O{6+i}':f'=COUNTIFS(E15:E{nc},N{6+i})' for i,k in enumerate(sorted(reasons))})
    block(s4,'H0022027','Estados de oferta 2027',5,16,['Estado','Códigos'],[[k,v] for k,v in sorted(statecounts.items())],'H002',formulas={f'R{6+i}':f'=COUNTIFS(J15:J{nc},Q{6+i})' for i,k in enumerate(sorted(statecounts))})
    fr=nc+4;source_rows=[[f['id'],f['ruta'],f['sha256'],f['clase'],f['commit']] for f in F.values()]
    block(s4,'Fuentes','Fuentes fijadas por hash · corte documental 30-10-2026',fr,0,['ID','Ruta','SHA-256','Clase','Commit / linaje'],source_rows,'FUENTES_FIJADAS.json')
    # El resumen de cobertura tiene columnas propias; el detalle se mantiene
    # a la derecha para no ensanchar sus números ni estrechar las explicaciones.
    s4['widths']=[18,16,16,18,18,16,18,4,43,16,4,43,26,20,48,55,40,65,16,18,18,40,18,28,4,4,22,100,72,25,48]
    for b in s4['blocks']:
        old=b['column']
        if b['id']=='Cruces':b['column']=12
        elif b['id']=='Pendientes':b['column']=8
        elif b['id']=='H0022027':b['column']=11
        elif b['id']=='Fuentes':b['column']=26;b['row']=16
        for x in controls:
            if x['hoja']==s4['name'] and x['fuente']==b['source']:
                # Campo/registro bastan, pero solo dentro del rango original.
                a=x['celda'];match=re.fullmatch(r'([A-Z]+)(\d+)',a);number=int(match[2]);ci=0
                for ch in match[1]:ci=ci*26+ord(ch)-64
                if b['row']<=number<=b['row']+len(b['rows']) and old+1<=ci<=old+len(b['headers']):
                    x['celda']=f'{col(ci+b["column"]-old)}{number}'
        if b['id']=='Fuentes':
            for x in controls:
                if x['hoja']==s4['name'] and x['fuente']=='FUENTES_FIJADAS.json':
                    j=b['headers'].index(x['campo']);x['celda']=f'{col(27+j)}{16+x["registro"]}'
    cb=next(b for b in s4['blocks'] if b['id']=='Cobertura')
    cb['formulas'].update({'B11':f'=COUNTIFS(S15:S{nc},">0")','C11':f'=COUNTIFS(T15:T{nc},">0")','D11':f'=SUM(S15:S{nc})','E11':f'=SUM(T15:T{nc})','G11':f'=SUM(U15:U{nc})'})
    for b in s4['blocks']:
        if b['id']=='Pendientes':b['formulas']={f'J{6+i}':f'=COUNTIFS(Q15:Q{nc},I{6+i})' for i,k in enumerate(sorted(reasons))}
        if b['id']=='H0022027':b['formulas']={f'M{6+i}':f'=COUNTIFS(V15:V{nc},L{6+i})' for i,k in enumerate(sorted(statecounts))}
    # Controles finales de ubicación se reconstruyen desde los mismos datos.
    controls=[x for x in controls if x['hoja']!=s4['name']]
    for b in s4['blocks']:
        for i,r in enumerate(b['rows']):
            for j,x in enumerate(r):
                a=f'{col(b["column"]+j+1)}{b["row"]+i+1}';controls.append(dict(hoja=s4['name'],celda=a,esperado=x,fuente=b['source'],registro=i+1,campo=b['headers'][j],formula=b['formulas'].get(a)))
    s4['freeze']=5
    s4['notes'].append((12,'Detalle por código desde M14; fuentes con rutas y hashes en AA16. La cobertura se mide sobre matrículas-año seleccionadas.'))
    s4['renders']=['A1:G12','I4:M12','M13:R24','AA15:AE19']
    stats=dict(codigos_historicos=sum(bool(activeyears(c)) for c in codes),activos_2026=sum(public.get((c,2026),0)>0 for c in codes),
      historicos_por_nivel=dict(level),universo_union=len(codes),planes=len(umas),codcarpr=len(dim),codcarpr_unidos=sum(r[2]=='UNIDO' for r in dim),planes_unidos=ul,
      matriz_codigos=yr[-1][1],matriz_codigos_enlazados=yr[-1][2],matriculas_seleccionadas=alltot,enlazadas=alllink,con_plan=allplan,
      porcentaje_enlace=100*alllink/alltot,porcentaje_plan=100*allplan/alltot,estados_2027=dict(statecounts),motivos=dict(reasons),
      solo_pre_2022=sum(bool(activeyears(c)) and max(activeyears(c))<2022 for c in codes),filas_base=len(base),anual=yr,
      codigos_matriz_incluyendo_solo_excluidas=len({r['codigo_sies'] for r in mu}),codigos_enlazados_incluyendo_solo_excluidas=len({r['codigo_sies'] for r in mu if r['estado']!='SIN_ENLACE'}),
      tipos_maestro=dict(ts),planes_fuera_maestro=sorted({p for c,p in pairs if validplan(p)}-{r['CODPESTUD'] for r in master['planes_umas']}))
    stats['h005b']=ampliar_h005b(sheets,F,master,h27,public_rows,block,sheet,mu,types)
    from ampliar_h006 import ampliar
    stats['h006']=ampliar(sheets,F,master,h27,public_rows,block,sheet,stats)
    # Recalcular sólo direcciones de presentación después de añadir columnas y
    # renumerar hojas. Cada celda previa se conserva por bloque/registro/campo.
    controls=[]
    for s in sheets:
        for b in s['blocks']:
            for i,r in enumerate(b['rows']):
                for j,x in enumerate(r):
                    a=f'{col(b["column"]+j+1)}{b["row"]+i+1}'
                    controls.append(dict(hoja=s['name'],bloque=b['id'],celda=a,esperado=x,fuente=b['source'],registro=i+1,campo=b['headers'][j],formula=b['formulas'].get(a)))
    dump(OUT/'CIFRAS_CLAVE.json',stats)
    dump(OUT/'CONTROL_CIFRAS.json',controls)
    dump(OUT/'MODELO_AGREGADO.json',dict(book=BOOK,font='Arial',palette=js('PALETA'),sheets=sheets))
    dump(OUT/'QA_FUENTES.json',dict(estado='PASS',fuentes=len(F),control_sies_reutilizado=406,filas_publicas_IPSS=472,
       sin_lectura_microdatos=False,lectura_MU_H006='Solo componentes del código, VIG e ingreso; agregados sin enlace',sin_nuevos_enlaces=True,denominador_reutilizado=alltot,fuentes_conservadas=True))
    print(json.dumps(stats,ensure_ascii=False,indent=2))
    return stats
def ampliar_h005b(sheets,F,master,h27,public_rows,block,sheet,mu,types):
    """Extiende H005 sólo con atributos de catálogo y diagnósticos agregados.

    No obtiene identidades, no decide versiones de personas y no modifica los
    enlaces de H002g. Las comparaciones de atributos son descriptivas C.
    """
    s1,s2,s4,s5=sheets
    s4['name']='4_Codigos_UMAS';s5['name']='5_Cruce_SIES_UMAS'
    s1['notes']=[(r,t.replace('hoja 4','hoja 5')) for r,t in s1['notes']]
    offers=master['oferta_anual'];offer={};olast={}
    for r in offers:
        k=r['codigo_unico'],int(r['anio']);assert k not in offer
        offer[k]=r
        if k[0] not in olast or r['anio']>olast[k[0]]['anio']:olast[k[0]]=r
    assert {r['vigencia'] for r in offers}=={'Vigente con estudiantes nuevos','Vigente sin estudiantes nuevos'}
    viglabels={'Vigente con estudiantes nuevos':1,'Vigente sin estudiantes nuevos':2}
    def vig(c,y):return viglabels[offer[c,y]['vigencia']] if (c,y) in offer else 'n.a.'
    def num(v):
        try:
            x=float(str(v).replace(',','.'));return int(x) if x.is_integer() else x
        except (ValueError,TypeError):return 'E'
    fields=['DURACIÓN ESTUDIO CARRERA','DURACIÓN TOTAL DE CARRERA','TIPO DE PLAN DE LA CARRERA','MODALIDAD','NIVEL GLOBAL','CARRERA CLASIFICACIÓN NIVEL 1']
    labels=['Duración de estudios','Duración total','Tipo de plan','Modalidad','Nivel global','Nivel específico']
    hist=defaultdict(dict);families=defaultdict(set)
    for (c,y),r in public_rows.items():
        hist[c][y]=r
        if re.fullmatch(r'I162S\d+C\d+J\d+V\d+',c):families[c.rsplit('V',1)[0]].add(c)
    latest={c:rs[max(rs)] for c,rs in hist.items()}
    def different(rows):return any(len({r[f].strip() for r in rows if r[f].strip()})>1 for f in fields)
    type_diff='VERSIONES_POR_DURACION_O_TIPO';type_same='VERSIONES_ATRIBUTOS_IDENTICOS'
    ftypes={};lasttypes={}
    for fa,cs in families.items():
        if len(cs)<2:continue
        ftypes[fa]=type_diff if different([r for c in cs for r in hist[c].values()]) else type_same
        lasttypes[fa]=type_diff if different([latest[c] for c in cs]) else type_same
    def ftype(c):
        f=c.rsplit('V',1)[0]
        return ftypes.get(f,'UNA_VERSION_OBSERVADA' if c in hist else 'E: sin historia pública')
    changes={}
    for c,rs in hist.items():
        d={}
        for f in fields:
            values=defaultdict(list)
            for y,r in sorted(rs.items()):
                if r[f].strip():values[r[f].strip()].append(y)
            if len(values)>1:d[f]=dict(values)
        if d:changes[c]=d
    # H005: se agregan columnas al final sin cambiar las anteriores.
    base=next(b for b in s1['blocks'] if b['id']=='Base')
    base['headers']+=['Duración estudios (sem.)','Duración total (sem.)','Tipo de familia histórica','Año atributos duración','Fuente duración']
    for r in base['rows']:
        c=r[0]
        if c in latest:
            a=latest[c];ext=[num(a[fields[0]]),num(a[fields[1]]),ftype(c),max(hist[c]),'PUBLICA; última matrícula']
        elif c in olast:
            a=olast[c];ext=[num(a['duracion_estudios']),num(a['duracion_total']),ftype(c),a['anio'],'MAESTRO/oferta_anual; sin matrícula']
        else:ext=['E',num(h27.get(c,{}).get('duracion_total_semestres')),ftype(c),2027,'H002; estudios no acreditados']
        r.extend(ext)
    s1['widths'] += [19,19,46,18,45]
    s1['renders'].append('AU6:AY18')
    # Oferta completa, separada del universo original para mantener sus controles.
    p=next(b for b in s2['blocks'] if b['id']=='Programas')
    original_codes={r[0] for r in p['rows']}
    p['headers'] += [f'Vigencia {y}' for y in range(2010,2027)]
    for r in p['rows']:r.extend(vig(r[0],y) for y in range(2010,2027))
    s2['widths'] += [14]*(70-len(s2['widths']))
    for i in range(30,47):s2['widths'][i]=14
    ofrows=[]
    for c,a in sorted(olast.items()):
        ys=sorted(y for code,y in offer if code==c)
        ofrows.append([c,a['nombre_carrera'],a['nivel_global'],min(ys),max(ys),1 if c in original_codes else 0]+[vig(c,y) for y in range(2010,2027)]+['MAESTRO/oferta_anual'])
    start=200;end=start+len(ofrows)
    block(s2,'OfertaHistorica','Catálogo completo de oferta 2010–2026',start,0,['Código SIES oferta','Carrera oferta','Nivel oferta','Primer año oferta','Último año oferta','En detalle H005 (1/0)']+[f'Vigencia oferta {y}' for y in range(2010,2027)]+['Fuente oferta'],ofrows,'MAESTRO/oferta_anual',{3:'0',4:'0'})
    levels=Counter(r[2] for r in ofrows)
    summ=[['EN_OFERTA 2010–2026',len(ofrows)]]+[[k,v] for k,v in sorted(levels.items())]+[['EN_OFERTA 2026',sum((c,2026) in offer for c in olast)],['Sólo oferta; fuera del detalle H005',sum(r[5]==0 for r in ofrows)]]
    formulas={'I6':f'=COUNTA(A{start+1}:A{end})','I9':f'=COUNTIFS(W{start+1}:W{end},1)+COUNTIFS(W{start+1}:W{end},2)','I10':f'=COUNTIFS(F{start+1}:F{end},0)'}
    for i,k in enumerate(sorted(levels)):formulas[f'I{7+i}']=f'=COUNTIFS(C{start+1}:C{end},H{7+i})'
    block(s2,'ResumenOfertaHistorica','Oferta no equivale a matrícula',5,7,['Oferta histórica','Códigos'],summ,'MAESTRO/oferta_anual',formulas=formulas)
    s2['widths'][7]=43;s2['widths'][8]=18
    annual=next(b for b in s2['blocks'] if b['id']=='Activos')
    annual['column']=49;annual['headers'].append('EN_OFERTA')
    annual['formulas']={f'AY{6+i}':f'=COUNTIFS({col(7+i)}15:{col(7+i)}{14+len(p["rows"])},">0")' for i in range(20)}
    for i,r in enumerate(annual['rows']):
        y=int(r[0]);r.append(sum((c,y) in offer for c in olast) if y>=2010 else 'E: sin fuente')
        if y>=2010:
            cc=col(7+y-2010);annual['formulas'][f'AZ{6+i}']=f'=COUNTIFS({cc}{start+1}:{cc}{end},1)+COUNTIFS({cc}{start+1}:{cc}{end},2)'
    s2['widths'][49:52]=[15,20,20]
    s2['chart']={'range':'AX5:AZ25','from':'BB5','to':'BR25','title':'Códigos EN_OFERTA y CON_MATRÍCULA','legend':True}
    s2['notes']=[(r,t) for r,t in s2['notes'] if r not in (3,4,12)] + [
      (3,'EN_OFERTA: código presente con vigencia 1 o 2 en oferta_anual del maestro; CON_MATRÍCULA: matrícula pública mayor que cero.'),
      (4,'La oferta incluye versiones sin alumnos, vigentes sólo por antiguos y diplomados sin matrícula.\n2007–2009: oferta no disponible; no se representa como cero.'),
      (12,'Detalle H005 A14; vigencias por año AE14; oferta completa A200; serie y gráfico AX5. n.a. = no observado en esa oferta, no cierre.')]
    s2['noteHeights']={'3':56,'4':56,'12':48}
    s2['renders']=['A1:I12','A13:F24','AE13:AK24','AX4:BR26','A199:H210']
    # Hoja nueva: todos los códigos con versiones múltiples observados en PUBLICA.
    s3=sheet('3_Versiones_SIES','IPSS · Versiones y atributos SIES',[24,25,44,12,15,15,32,21,20,32,13,13,14,47,13,70,28,4,25,42,90,13,13,38],5,[
      (3,'Clasificación histórica 2007–2026: compara valores conocidos de duración, tipo, modalidad y nivel; los vacíos no prueban cambios.'),
      (4,'A · Oferta 2027, líneas 240–248 y 2333–2337: cambiar duración, tipo, nivel o modalidad exige nueva versión. No acredita por sí solo un error de una carga histórica.'),
      (10,'Detalle A12: duración y atributos de la última matrícula de cada código; historia de cambios en P. Cambios por código desde S12.')])
    s3['noteHeights']={'3':54,'4':64,'10':45}
    counts=Counter(ftypes.values());lastcounts=Counter(lasttypes.values())
    block(s3,'ResumenVersiones','Una fila por clasificación de familia',5,0,['Clasificación histórica','Familias','Versión final por código: familias'],[[k,counts[k],lastcounts[k]] for k in [type_diff,type_same]],'PUBLICA; comparación de atributos')
    vrows=[]
    for fa,cs in sorted(families.items()):
        if len(cs)<2:continue
        for c in sorted(cs):
            a=latest[c];chg=changes.get(c,{})
            seq='; '.join(f'{labels[fields.index(f)]}: '+ ' / '.join(f'{v} ({",".join(map(str,ys))})' for v,ys in vals.items()) for f,vals in chg.items()) or 'Sin cambios observados en campos conocidos'
            vrows.append([fa,c,a['NOMBRE CARRERA'],c.rsplit('V',1)[1],num(a[fields[0]]),num(a[fields[1]]),a[fields[2]],a[fields[3]] or 'E',a[fields[4]],a[fields[5]],min(hist[c]),max(hist[c]),h27.get(c,{}).get('vigencia_2027','n.a.'),ftypes[fa],max(hist[c]),seq,'PUBLICA; H002'])
    block(s3,'Versiones','Una fila por versión con matrícula',12,0,['Familia SIES','Código SIES','Carrera','Versión','Estudios (sem.)','Total (sem.)','Tipo de plan','Modalidad','Nivel global','Nivel específico','Primer año','Último año','Vigencia 2027','Clase familia histórica','Año atributos','Cambios observados en el código','Fuente'],vrows,'PUBLICA; H002',{10:'0',11:'0',14:'0'})
    crows=[]
    for c,d in sorted(changes.items()):
        seq='; '.join(f'{labels[fields.index(f)]}: '+ ' / '.join(f'{v} ({",".join(map(str,ys))})' for v,ys in vals.items()) for f,vals in d.items())
        crows.append([c,', '.join(labels[fields.index(f)] for f in d),seq,min(hist[c]),max(hist[c]),'B cambio; E causa histórica'])
    block(s3,'CambiosAtributos','Un código por fila; no interpreta vacíos como cambio',12,18,['Código con cambio','Atributos','Valores y años publicados','Primer año','Último año','Clase / límite'],crows,'PUBLICA',{3:'0',4:'0'})
    s3['renders']=['A1:G10','A11:G23','H11:O23','S11:X21']
    sheets.remove(s3);sheets.insert(2,s3)
    # H005c: tipo del plan v2 frente al tipo del código realmente informado,
    # con año explícito. No se usa el código esperado H002j para decidir error.
    type_index=defaultdict(set)
    for r in types:type_index[r['plan_umas']].add(r['tipo_plan'])
    def umas_type(p):
        if not validplan(p):return 'SIN_PLAN'
        values=type_index[p]
        return next(iter(values)) if len(values)==1 else 'E'
    def sies_type(c,y):
        return {'Plan Regular':'REGULAR','Plan Regular de Continuidad':'CONTINUIDAD'}.get(offer.get((c,y),{}).get('tipo_plan_sies'),'E')
    def coherence(tu,ts):
        if tu in {'E','SIN_PLAN'} or ts=='E':return 'NO_EVALUABLE'
        return 'CORRECTO_SEGUN_MANUAL' if tu==ts else 'ERROR_DE_CARGA_SEGUN_MANUAL'
    cross=Counter();errors_by=Counter();linked=Counter();coherent=Counter();focus=Counter()
    for r in mu:
        if r['estado']=='SIN_ENLACE':continue
        y=int(r['anio']);n=int(r['matriculas']);p=r['plan_umas'];c=r['codigo_sies']
        tu=umas_type(p);ts=sies_type(c,y);st=coherence(tu,ts)
        cross[y,tu,ts,st]+=n;linked[y]+=n;coherent[y,st]+=n
        if st=='ERROR_DE_CARGA_SEGUN_MANUAL':errors_by[y,r['codcarpr'],p,c,tu,ts]+=n
        if validplan(p) and r['codcarpr'] in {'CICRE','CICIB','CIINF'}:focus[y,r['codcarpr'],st]+=n
    assert all(ts!='E' or n==0 for (y,tu,ts,st),n in cross.items()), 'Tipo SIES anual no observado: no forzar clasificación'
    # Mantener la etiqueta anterior como dato de trazabilidad congelado H005b.
    baseline=OUT/'CLASIFICACION_253_H005B.json'
    olddiag=json.loads(baseline.read_text());old_by={x['id']:x for x in olddiag['grupos']}
    diag=json.loads(Path(F['DIAG253']['ruta']).read_text());assert sum(r['matriculas'] for r in diag['casos_agregados'])==diag['total']==253
    ds=[];agg=Counter();by_class=Counter();causes=Counter()
    for i,r in enumerate(diag['casos_agregados'],1):
        tu=umas_type(r['plan']);ts=sies_type(r['codigo_informado'],r['anio']);st=coherence(tu,ts)
        if st=='NO_EVALUABLE':
            cl='NO_EVALUABLE';back='E';why='Tipo de plan UMAS E en catálogo v2; no se infiere del código ni se activa el catálogo v3.'
        elif st=='ERROR_DE_CARGA_SEGUN_MANUAL':
            cl=st;back='A criterio de versiones; C contraste de tipos';why='El tipo del plan UMAS v2 se cruza con el tipo de la versión informada en oferta_anual del mismo año.'
        elif tu=='CONTINUIDAD':
            cl='CORRECTO_TRASLADO_A_CONTINUIDAD';back='B/C';why='Plan de continuidad informado en versión de continuidad. El código esperado H002j no determina la coherencia.'
        else:
            cl='VERSION_POR_PLAN_O_ANIO';back='C';why='Plan regular informado en versión regular. Etiqueta descriptiva del reparto; no afirma causa individual del cambio.'
        n=r['matriculas'];by_class[cl]+=n;agg[cl,r['familia'],r['anio']]+=n;causes[why]+=n
        old=old_by[i];assert (old['plan'],old['anio'],old['codigo_informado'],old['matriculas'])==(r['plan'],r['anio'],r['codigo_informado'],n)
        ds.append(dict(id=i,anio=r['anio'],familia=r['familia'],plan=r['plan'],grupo=r['grupo'],codigo_informado=r['codigo_informado'],codigo_comparado_H002j=r['codigo_H002j'],tipo_plan_diagnostico=old['tipo_plan_diagnostico'],tipo_umas_v2=tu,tipo_sies_anual=ts,matriculas=n,clasificacion=cl,clase=back,motivo=why,clasificacion_anterior=old['clasificacion'],fuente='DIAG253; TIPOS_V2; MAESTRO/oferta_anual; MANUAL_OFERTA2027'))
    s5['widths'] += [16]*(60-len(s5['widths']))
    s5['widths'][40:45]=[48,18,28,60,45]
    classes=['ERROR_DE_CARGA_SEGUN_MANUAL','VERSION_POR_PLAN_O_ANIO','CORRECTO_TRASLADO_A_CONTINUIDAD','NO_EVALUABLE']
    summary=[[k,by_class[k],('A criterio; C contraste' if k==classes[0] else 'E' if k=='NO_EVALUABLE' else 'B/C')] for k in classes]
    block(s5,'Resumen253','253 originales; clasificación H005c por tipos observados',5,40,['Clasificación de los 253','Matrículas-año','Clase'],summary,'DIAG253; TIPOS_V2; MAESTRO',formulas={f'AP{6+i}':f'=SUMIFS(AR13:AR{12+len(agg)},AO13:AO{12+len(agg)},AO{6+i})' for i in range(4)})
    ar=[[cl,fa,y,n,'Clasificación H005c; tipo UMAS v2 y SIES anual'] for (cl,fa,y),n in sorted(agg.items())]
    block(s5,'Clasificacion253','253 originales por familia y año',12,40,['Clasificación','Familia','Año','Matrículas-año','Alcance'],ar,'DIAG253; TIPOS_V2; MAESTRO',{2:'0'})
    s5['widths'][46:60]=[13,25,27,22,25,25,32,18,46,70,80,46,20,20]
    dr=[[d['anio'],d['familia'],d['plan'],d['grupo'],d['codigo_informado'],d['codigo_comparado_H002j'],d['tipo_plan_diagnostico'],d['matriculas'],d['clasificacion'],d['clase'],d['motivo'],d['clasificacion_anterior'],d['tipo_umas_v2'],d['tipo_sies_anual']] for d in ds]
    block(s5,'Evidencia253','Los mismos 34 grupos; etiqueta anterior y tipos usados visibles',12,46,['Año','Familia','Plan UMAS','Grupo','Código informado','Código comparado H002j','Tipo plan diagnóstico','Matrículas-año','Clasificación','Clase','Fundamento / límite','Etiqueta anterior H005b','Tipo UMAS v2','Tipo SIES anual'],dr,'DIAG253; TIPOS_V2; MAESTRO',{0:'0'})
    # Universo enlazado completo, separado del subconjunto diagnóstico de 253.
    yr=[];cf={}
    for y in range(2022,2027):
        i=y-2022;row=56+i
        yr.append([y,coherent[y,'CORRECTO_SEGUN_MANUAL'],coherent[y,'ERROR_DE_CARGA_SEGUN_MANUAL'],coherent[y,'NO_EVALUABLE'],linked[y]])
        for j,st in enumerate(['CORRECTO_SEGUN_MANUAL','ERROR_DE_CARGA_SEGUN_MANUAL','NO_EVALUABLE']):
            cf[f'{col(42+j)}{row}']=f'=SUMIFS(AR68:AR107,AO68:AO107,AO{row},AS68:AS107,"{st}")'
        cf[f'AS{row}']=f'=SUM(AP{row}:AR{row})'
    block(s5,'CoherenciaAnual','Matrículas MU enlazadas, no personas únicas',55,40,['Año','CORRECTO_SEGUN_MANUAL','ERROR_DE_CARGA_SEGUN_MANUAL','NO_EVALUABLE','Total enlazadas'],yr,'MATRIZ/MU_DATOS_ALUMNOS; TIPOS_V2; MAESTRO',{0:'0',1:'[>=1000]#"."000;0',2:'[>=1000]#"."000;0',3:'[>=1000]#"."000;0',4:'[>=1000]#"."000;0'},cf)
    cr=[]
    for y in range(2022,2027):
        for tu in ['REGULAR','CONTINUIDAD','E','SIN_PLAN']:
            for ts in ['REGULAR','CONTINUIDAD']:
                st=coherence(tu,ts);cr.append([y,tu,ts,cross[y,tu,ts,st],st,'A criterio; B/C dato y contraste; E sin tipo'])
    block(s5,'CoherenciaTipos','Matriz tipo UMAS por tipo SIES anual',67,40,['Año','Tipo plan UMAS v2','Tipo versión SIES','Matrículas-año','Estado','Clase'],cr,'MATRIZ/MU_DATOS_ALUMNOS; TIPOS_V2; MAESTRO',{0:'0'})
    er=[[y,cp,p,c,tu,ts,n,'A criterio; C contraste; no modifica carga'] for (y,cp,p,c,tu,ts),n in sorted(errors_by.items())]
    block(s5,'CrucesTipos','Cruces de tipos por año, plan y código informado',55,46,['Año','CODCARPR','Plan UMAS','Código informado','Tipo UMAS v2','Tipo SIES anual','Matrículas-año','Clase'],er,'MATRIZ/MU_DATOS_ALUMNOS; TIPOS_V2; MAESTRO',{0:'0'})
    note='En 2024–2025, los alumnos de los planes de continuidad CICRE, CICIB y CIINF se informaron en el código regular; en 2026 los planes observados quedaron 100 % en su versión de continuidad.\nLos traslados V2→V3 de 2025–2026 son correcciones de coherencia de tipo, no inconsistencias.\nLa tabla incluye continuidad correcta en 2025; CICIB usa V3 regular→V1 continuidad. Un CICRE 2026 sin plan observado queda NO_EVALUABLE. No certifica trayectorias individuales ni aplica cambios.'
    assert all(st=='CORRECTO_SEGUN_MANUAL' or n==0 for (y,cp,st),n in focus.items() if y==2026)
    s5['customNotes']=[dict(range='AO49:AS51',text=note)]
    s5['renders']+=['AO4:AQ10','AO49:AS61','AO66:AT78','AU54:BB65','BC12:BH20']
    coherent_out=dict(anual=[dict(anio=r[0],correcto=r[1],error=r[2],no_evaluable=r[3],enlazadas=r[4]) for r in yr],cruce_tipos=[dict(anio=y,tipo_umas=tu,tipo_sies=ts,matriculas=n,estado=st) for y,tu,ts,n,st,cl in cr],errores=[dict(anio=y,codcarpr=cp,plan=p,codigo=c,tipo_umas=tu,tipo_sies=ts,matriculas=n) for y,cp,p,c,tu,ts,n,cl in er],nota=note,fuentes=['MATRIZ','TIPOS_V2','MAESTRO'])
    dump(OUT/'COHERENCIA_TIPO_H005C.json',coherent_out)
    dump(OUT/'CLASIFICACION_253_H005C.json',dict(total=253,grupos=ds,resumen=dict(by_class),trazabilidad=sha(baseline),limite='Coherencia de tipos, sin reconstrucción de enlaces ni trayectorias individuales'))
    # Controles explícitos: los nuevos bloques no solapan tablas existentes.
    for s in sheets:
        rect=[]
        for b in s['blocks']:
            a=(b['row'],b['row']+len(b['rows']),b['column'],b['column']+len(b['headers'])-1)
            for old,id in rect:assert a[1]<old[0] or a[0]>old[1] or a[3]<old[2] or a[2]>old[3],(s['name'],b['id'],id)
            rect.append((a,b['id']))
    additions=dict(en_oferta=len(olast),oferta_por_nivel=dict(levels),oferta_2026=sum((c,2026) in offer for c in olast),oferta_sin_fila_H005=sorted(set(olast)-original_codes),
        familias_historicas=dict(counts),familias_ultima_foto=dict(lastcounts),familias_identicas=sorted(f for f,t in ftypes.items() if t==type_same),
        codigos_con_cambios=len(changes),codigos_cambios=sorted(changes),versiones_multiple=len(vrows),clasificacion_253=dict(by_class),causas_253=dict(causes),
        clases_por_familia_anio=[dict(clasificacion=c,familia=f,anio=y,matriculas=n) for (c,f,y),n in sorted(agg.items())])
    additions['coherencia_anual']=coherent_out['anual']
    additions['correccion']='H005c: tipo UMAS v2 contra tipo SIES oferta_anual; H005b conservado como antecedente'
    dump(OUT/'ATRIBUTOS_VERSIONES_H005B.json',dict(familias=ftypes,foto_final=lasttypes,cambios=changes,criterio='Todos los valores conocidos 2007–2026; vacíos excluidos; lectura descriptiva sin nueva paridad'))
    return additions

if __name__=='__main__':
    model()
    if '--solo-modelo' not in sys.argv:
        subprocess.run([str(RUNTIME/'node/bin/node'),str(OUT/'construir.mjs')],check=True)

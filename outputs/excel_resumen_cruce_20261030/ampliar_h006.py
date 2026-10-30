"""H006: agregaciones de catálogos y MU, sin enlaces ni paridades nuevas.

La lectura MU selecciona solo año, componentes del código, VIG e ingreso.
No exporta personas ni identifica quién está pendiente de titularse.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json, hashlib, re
import openpyxl

OUT=Path(__file__).resolve().parent
COUNT='[>=1000000]#"."000"."000;[>=1000]#"."000;0'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def col(n):
    s=''
    while n:n,m=divmod(n-1,26);s=chr(65+m)+s
    return s
def integer(v):
    if v is None or v=='':return None
    try:return int(float(str(v).replace(',','.')))
    except (ValueError,TypeError):return None

def ampliar(sheets,F,master,h27,public,block,sheet,stats):
    sources=json.loads((OUT/'FUENTES_H006.json').read_text())
    for s in sources:assert sha(s['ruta'])==s['sha256'],s['id']
    src={s['id']:s for s in sources}
    sector=json.loads(Path(src['SECTOR']['ruta']).read_text())['mapeo_por_cod_car']
    offer={(r['codigo_unico'],r['anio']):r for r in master['oferta_anual']}
    family=lambda c:c.rsplit('V',1)[0]
    codes=defaultdict(set);hist=defaultdict(dict)
    for (c,y),r in public.items():codes[family(c)].add(c);hist[c][y]=r
    latest={c:ys[max(ys)] for c,ys in hist.items()}
    def dims(c):
        m=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)(?:V\d+)?',c)
        if m is None:return ['E: sin sede','E: sin jornada','E: sin sector']
        sd,ca,jo=m.groups()
        return [{'2':'Santiago','3':'Concepción','4':'Patagonia'}.get(sd,'E: sede '+sd),{'1':'Diurna','2':'Vespertina','3':'Semipresencial','4':'A distancia'}.get(jo,'E: jornada '+jo),sector.get(ca,['','E: sin sector'])[1]]
    def name(fa):
        cs=codes[fa];c=max(cs,key=lambda c:(max(hist[c]),c));return latest[c]['NOMBRE CARRERA']
    def total(fa,y,field='TOTAL MATRÍCULA'):
        observed=[public[c,y] for c in codes[fa] if (c,y) in public]
        if field=='TOTAL MATRÍCULA PRIMER AÑO' and any(integer(r.get(field)) is None for r in observed):return 'E: sin dato'
        return sum(integer(r.get(field)) or 0 for r in observed)
    def vig(c,y):
        if y==2027:return str(h27.get(c,{}).get('vigencia_2027','E'))
        return {'Vigente con estudiantes nuevos':'1','Vigente sin estudiantes nuevos':'2'}.get(offer.get((c,y),{}).get('vigencia'),'E')
    def vig_family(fa,y):
        cs=set(codes[fa])|{c for c in h27 if family(c)==fa}
        # Versiones históricas sin fila de oferta se explicitan; no se infiere cierre.
        return ' / '.join(c.split('V')[-1]+': '+vig(c,y) for c in sorted(cs))
    def extinct(fa):
        vs={vig(c,2027) for c in set(codes[fa])|{c for c in h27 if family(c)==fa}}
        return 'Sí' if '2' in vs and '1' not in vs and 'E' not in vs else 'E' if 'E' in vs and '1' not in vs else 'No'
    # MU 2026: no enlace a UMAS; solo componentes ya informados y cohorte actual.
    mu=Counter();cohort=Counter();lag=Counter();lag_e=Counter();vig_all=Counter()
    w=openpyxl.load_workbook(src['MU_142342']['ruta'],read_only=True,data_only=True)
    sh=w['BASE_RETENCION_MU'];it=sh.iter_rows(values_only=True);headers=next(it);idx={k:i for i,k in enumerate(headers)}
    for row in it:
        if integer(row[idx['ANIO_INFORMADO']])!=2026:continue
        v=integer(row[idx['VIG']]);vig_all[str(v)]+=1
        if v!=1:continue
        components=[integer(row[idx[k]]) for k in ['COD_SED','COD_CAR','JOR','VERSION']];assert all(x is not None for x in components)
        c='I162S%dC%dJ%dV%d'%tuple(components);mu[c]+=1
        y=integer(row[idx['ANIO_ING_ACT']]);valid=y is not None and 1900<=y<=2026
        group='≤ 2016' if valid and y<=2016 else '2017–2021' if valid and y<=2021 else '≥ 2022' if valid else 'E: ingreso'
        cohort[c,group]+=1
        dur=integer(public.get((c,2026),{}).get('DURACIÓN ESTUDIO CARRERA'))
        if dur is None:dur=integer(offer.get((c,2026),{}).get('duracion_estudios'))
        if not valid or dur is None or dur<=0:lag_e[c]+=1
        elif 2026-y>dur/2:lag[c]+=1
    w.close();assert sum(mu.values())==3145 and sum(vig_all.values())==4105
    tit=json.loads(Path(src['TITULACION_AGREGADA']['ruta']).read_text())
    t26=next(r for r in tit['matriz'] if r['anio']==2026)['titulacion_mu']
    titles={r['codigo_sies']:r['carga'] for r in t26['comparacion_codigo']};assert sum(titles.values())==431
    # Tablas nuevas: solo familias con matrícula observada; no replica planes.
    old=[]
    for fa in sorted(codes):
        ys=sorted({y for c in codes[fa] for y,r in hist[c].items() if integer(r['TOTAL MATRÍCULA'])>0})
        if min(ys)>2016 or total(fa,2026)==0:continue
        cs=codes[fa];nn=sum(mu[c] for c in cs)
        old.append([fa,name(fa),*dims(fa),' / '.join(sorted(cs)),min(ys),len(ys),vig_family(fa,2026),vig_family(fa,2027),nn]+[sum(cohort[c,k] for c in cs) for k in ['≤ 2016','2017–2021','≥ 2022','E: ingreso']]+[sum(lag[c] for c in cs),sum(lag_e[c] for c in cs),sum(titles.get(c,0) for c in cs),extinct(fa),total(fa,2026),'B/C; proxy D','PUBLICA; MU_142342; TITULACION_AGREGADA; H002'])
    unopened=[]
    for (c,y),r in sorted(offer.items(),key=lambda x:(x[0][1],x[0][0])):
        if r['vigencia']!='Vigente con estudiantes nuevos':continue
        p=public.get((c,y));n=integer(p['TOTAL MATRÍCULA PRIMER AÑO']) if p else None
        if p is not None and n!=0:continue
        unopened.append([str(y),c,r['nombre_carrera'],*dims(c),integer(r['duracion_estudios']) or 'E',r['tipo_plan_sies'],0 if p else 'Sin fila SIES',1 if p else 0,r['nivel_global'],'B/C: primer año 0 o sin fila; no prueba apertura operativa','MAESTRO/oferta_anual; PUBLICA'])
    trend=[]
    for fa in sorted(codes):
        ys=sorted({y for c in codes[fa] for y,r in hist[c].items() if integer(r['TOTAL MATRÍCULA'])>0});a,b,d=total(fa,2022),total(fa,2026),total(fa,2024)
        p26=total(fa,2026,'TOTAL MATRÍCULA PRIMER AÑO')
        state='CERRADA' if b==0 else 'NUEVA' if a==0 else 'EN_EXTINCION' if p26==0 else 'ALZA' if (b-a)/a>=.1 else 'BAJA' if (b-a)/a<=-.1 else 'ESTABLE'
        trend.append([fa,name(fa),*dims(fa),' / '.join(sorted(codes[fa])),min(ys),max(ys)]+[n for y in range(2019,2027) for n in [total(fa,y),total(fa,y,'TOTAL MATRÍCULA PRIMER AÑO')]]+[b-a,(b-a)/a if a else 'E: base 0',b-d,(b-d)/d if d else 'E: base 0',state,'B/C; PUBLICA',b-a,'',''])
    # Paneles con criterios acotados; toda dimensión está poblada como texto.
    def panel(s,rows,dimcols):
        s['selectors']=[dict(label='SEDE',cell='B4',labelCell='A4',values=['Todas']+sorted({r[dimcols[0]] for r in rows})),dict(label='JORNADA',cell='D4',labelCell='C4',values=['Todas']+sorted({r[dimcols[1]] for r in rows})),dict(label='SECTOR IPSS',cell='F4',labelCell='E4',values=['Todas']+sorted({r[dimcols[2]] for r in rows}))]
        return ','.join(f'${col(j+1)}$19:${col(j+1)}${18+len(rows)},IF(${sel}$4="Todas","*",${sel}$4)' for j,sel in zip(dimcols,['B','D','F']))
    s=sheet('6_Carreras_Antiguas','IPSS · Familias con matrícula desde 2016 o antes',[25,46,20,23,28,28,14,14,45,45,19,16,16,16,16,18,18,18,22,18,24,50],18,[(3,'Familia = sede + carrera + jornada; se suman versiones. Filtros para el panel; autofiltro independiente para el detalle.'),(15,'«Quedan por titular» = VIG1 MU 2026 (proxy D); no certifica ausencia de título. Rezago: 2026 − ingreso actual > duración de estudios/2; aproximación anual C.'),(16,'Titulación: proceso 2026, referencia 2025, 431 cargas agregadas; no se resta de VIG1. Vigencia por versión: 1 con nuevos, 2 solo antiguos, 3 sin estudiantes, E sin fila.')])
    s['noteHeights']={15:46,16:46};crit=panel(s,old,[2,3,4]);end=18+len(old)
    headers=['Familia SIES','Carrera','Sede','Jornada','Sector IPSS','Códigos incluidos','Primer año','Años con matrícula','Vigencia 2026 por versión','Vigencia 2027 por versión','VIG1 / quedan por titular (proxy)','Ingreso ≤ 2016','Ingreso 2017–2021','Ingreso ≥ 2022','Ingreso E','Rezago aproximado','Rezago no evaluable','Titulación proceso 2026','Solo antiguos 2027','Matrícula SIES 2026','Clase','Fuente']
    block(s,'AntiguasDetalle','Familias antiguas',18,0,headers,old,'PUBLICA; MAESTRO; MU_142342; TITULACION_AGREGADA; H002',{**{i:COUNT for i in range(10,20) if i!=18},6:'0'})
    oldsum=[['Familias antiguas',len(old),'familias'],['VIG1 / quedan por titular (proxy)',sum(r[10] for r in old),'matrículas'],['Solo antiguos en oferta 2027',sum(r[18]=='Sí' for r in old),'familias'],['Rezago aproximado',sum(r[15] for r in old),'matrículas'],['Ingreso ≤ 2016',sum(r[11] for r in old),'matrículas'],['Titulados proceso 2026',sum(r[17] for r in old),'registros de titulación']]
    fs={'B8':f'=COUNTIFS({crit})','B9':f'=SUMIFS(K19:K{end},{crit})','B10':f'=COUNTIFS({crit},S19:S{end},"Sí")','B11':f'=SUMIFS(P19:P{end},{crit})','B12':f'=SUMIFS(L19:L{end},{crit})','B13':f'=SUMIFS(R19:R{end},{crit})'}
    block(s,'AntiguasResumen','Vista filtrada',7,0,['Indicador','Total filtrado','Unidad'],oldsum,'Detalle AntiguasDetalle',{1:COUNT},fs)
    s['renders']=['A1:F16','A18:H25','K18:U25'];s['titleEnd']='F'
    s['conditional']=[dict(range=f'A19:V{end}',formula='$S19="Sí"',fill='#FFF2CC')]
    s=sheet('7_Ofertadas_No_Abiertas','IPSS · Oferta con nuevos sin primer año observado',[16,25,46,20,23,28,17,30,20,14,20,48,48]+[18]*4,18,[(3,'Códigos-año con VIGENCIA 1 y primer año SIES = 0 o sin fila. No acredita que una carrera no se abrió operacionalmente.'),(15,'2027: NO EVALUABLE hasta la MU 2027. No se asigna cero. La oferta V06 es carga preparada C; no aceptación técnica PES.')]);s['titleEnd']='F';crit=panel(s,unopened,[3,4,5]);end=18+len(unopened)
    block(s,'NoAbiertasDetalle','Detalle oferta sin primer año',18,0,['Año','Código SIES','Carrera','Sede','Jornada','Sector IPSS','Duración estudios semestres','Tipo plan','Primer año SIES','Fila pública (1/0)','Nivel','Límite / clase','Fuente'],unopened,'MAESTRO; PUBLICA',{6:'0',9:'0'})
    ny=Counter(r[0] for r in unopened);rows=[[str(y),ny[str(y)]] for y in range(2010,2027)]
    block(s,'NoAbiertasAnual','Conteo por año filtrado',7,7,['Año','Códigos-año'],rows,'NoAbiertasDetalle',{1:COUNT},{f'I{8+i}':f'=COUNTIFS({crit},A19:A{end},H{8+i})' for i in range(17)})
    block(s,'NoAbiertasResumen','Vista filtrada',7,0,['Indicador','Total filtrado','Unidad'],[['Ofertas sin primer año observado',len(unopened),'códigos-año'],['Con fila y primer año cero',sum(r[9] for r in unopened),'códigos-año'],['Sin fila SIES',sum(not r[9] for r in unopened),'códigos-año']],'NoAbiertasDetalle',{1:COUNT},{'B8':f'=COUNTIFS({crit})','B9':f'=COUNTIFS({crit},J19:J{end},1)','B10':f'=COUNTIFS({crit},J19:J{end},0)'})
    # Bloque anual va a la derecha del detalle para evitar superposición de filas 18–24.
    b=s['blocks'][-2];b['column']=14;b['formulas']={f'P{8+i}':f'=COUNTIFS({crit},A19:A{end},O{8+i})' for i in range(17)}
    s['widths']+=[18]*10;s['charts']=[{'range':'O7:P24','from':'R6','to':'AA23','title':'Oferta sin primer año observado · filtros','legend':False}]
    s['renders']=['A1:F16','A18:M24','O6:AA25']
    s=sheet('8_Tendencia_Matricula','IPSS · Tendencia por familia, suma de versiones',[25,46,20,23,28,28,14,14]+[14]*16+[18,18,18,18,23,30,18,15,15]+[25,48,18,25,48,18]+[18]*16,18,[(3,'Matrículas, no personas únicas. Familia = sede + carrera + jornada. Top 10 por variación absoluta 2022→2026; filtros compartidos.'),(15,'Prioridad C: CERRADA (total 2026=0), NUEVA (base 2022=0), EN_EXTINCION (primer año 2026=0), luego ALZA/BAJA ±10 % o ESTABLE. No certifica cierre de oferta.'),(16,'Sin fila: ausencia de matrícula publicada; primer año vacío en una versión: E, nunca cero. Porcentaje con base cero: E. CERRADA no acredita cierre de oferta.')]);s['titleEnd']='F';s['noteHeights']={15:54,16:42};crit=panel(s,trend,[2,3,4]);end=18+len(trend)
    fs={}
    for i,r in enumerate(trend,19):
        r[30]=r[24]
        fs.update({f'Y{i}':f'=W{i}-O{i}',f'Z{i}':f'=IF(O{i}=0,"E: base 0",Y{i}/O{i})',f'AA{i}':f'=W{i}-S{i}',f'AB{i}':f'=IF(S{i}=0,"E: base 0",AA{i}/S{i})',f'AE{i}':f'=IF(AND(OR($B$4="Todas",C{i}=$B$4),OR($D$4="Todas",D{i}=$D$4),OR($F$4="Todas",E{i}=$F$4)),Y{i},"")',f'AF{i}':f'=IF(AND(ISNUMBER(AE{i}),AE{i}>0),COUNTIF($AE$19:$AE${end},">"&AE{i})+COUNTIF($AE$19:AE{i},AE{i}),"")',f'AG{i}':f'=IF(AND(ISNUMBER(AE{i}),AE{i}<0),COUNTIF($AE$19:$AE${end},"<"&AE{i})+COUNTIF($AE$19:AE{i},AE{i}),"")'})
    pos=sorted([r for r in trend if r[24]>0],key=lambda r:(-r[24],r[0]));neg=sorted([r for r in trend if r[24]<0],key=lambda r:(r[24],r[0]))
    for r in trend:r[31]=pos.index(r)+1 if r in pos else '';r[32]=neg.index(r)+1 if r in neg else ''
    headers=['Familia SIES','Carrera','Sede','Jornada','Sector IPSS','Códigos incluidos','Primer año','Último año']+[k for y in range(2019,2027) for k in [f'Total {y}',f'Primer año {y}']]+['Variación absoluta 2022→2026','Variación % 2022→2026','Variación absoluta 2024→2026','Variación % 2024→2026','Clasificación','Clase / fuente','Auxiliar variación filtrada','Auxiliar orden alza','Auxiliar orden baja']
    block(s,'TendenciaDetalle','Matrícula por familia',18,0,headers,trend,'PUBLICA; SECTOR',{**{i:COUNT for i in range(8,24)},6:'0',7:'0',24:'0;-0;0',25:'0.0%',26:'0;-0;0',27:'0.0%'},fs)
    st=Counter(r[28] for r in trend);ss=[[k,st[k],'familias'] for k in ['ALZA','BAJA','ESTABLE','NUEVA','EN_EXTINCION','CERRADA']]+[['TOTAL',len(trend),'familias']]
    block(s,'TendenciaResumen','Vista filtrada',7,0,['Estado','Total filtrado','Unidad'],ss,'TendenciaDetalle',{}, {f'B{8+i}':f'=COUNTIFS({crit},AC19:AC{end},A{8+i})' if i<6 else f'=COUNTIFS({crit})' for i in range(7)})
    for start,rank,ordered,label in [(33,'AF',pos,'alzas'),(36,'AG',neg,'bajas')]:
        rr=[];ff={}
        for i in range(10):
            a=ordered[i] if i<len(ordered) else None;rr.append([a[0] if a else '',a[1] if a else '',a[24] if a else ''])
            for j,target in enumerate(['A','B','Y']):ff[f'{col(start+j+1)}{8+i}']=f'=IFERROR(INDEX(${target}$19:${target}${end},MATCH({i+1},${rank}$19:${rank}${end},0)),"")'
        block(s,'Top'+label,'Top 10 '+label,7,start,['Familia','Carrera','Cambio absoluto'],rr,'TendenciaDetalle',{2:'0;-0;0'},ff)
    s['charts']=[{'range':'AI7:AJ17','from':'AN6','to':'AW24','title':'Top 10 alzas · variación 2022→2026','legend':False},{'range':'AL7:AM17','from':'AY6','to':'BH24','title':'Top 10 bajas · variación 2022→2026','legend':False}]
    s['widths']+=[18]*6;s['renders']=['A1:F16','A18:H26','Y18:AC26','AH6:AJ17','AK6:AM17','AN5:AW25','AY5:BH25']
    # Resumen reutilizado: cifras proceden literalmente del mapa previo.
    mapa=json.loads(Path(src['MAPA_H006']['ruta']).read_text());byid={r['id']:r for r in mapa['resultados']}
    rows=[]
    for id in ['R01','R02','R03','R04','R07','R09','R11','R18','R19']:
        r=byid[id];rows.append([id,r['pregunta'],r['resultado_clave'],'H003 · '+r.get('hoja_o_seccion','') if id in ['R01','R02','R03','R04','R07','R09','R19'] else r['archivo'],r['clase'],r['no_recalcular_salvo'],'Todas','Todas','Todas','MAPA_H006/'+id])
    rows += [['R21-SIES','¿Qué catálogos se reúnen?','139 en oferta; 106 con matrícula','2_Programas_SIES','B/C','Nueva fuente gobernada','Todas','Todas','Todas','CIFRAS_CLAVE/H005b'],['R21-UMAS','¿Cuántos planes y códigos internos?','236 planes; 127 CODCARPR','4_Codigos_UMAS','B/C','Nuevo catálogo UMAS','Todas','Todas','Todas','CIFRAS_CLAVE'],['R21-ENLACE','¿Qué cobertura tiene el enlace?','8.814/9.146 matrículas-año; 96,4 %','5_Cruce_SIES_UMAS','B/C','No recalcular con mismas fuentes','Todas','Todas','Todas','CIFRAS_CLAVE'],['R21-TIPOS','¿Qué cruces de tipo se observan?','2024: 133; 2025: 171; 2026: 0 evaluables','5_Cruce_SIES_UMAS','A criterio; B/C contraste; E sin tipo','Nuevo respaldo de tipo o carga','Todas','Todas','Todas','COHERENCIA_TIPO_H005C']]
    missing=[[i,byid[i]['pregunta'],byid[i]['resultado_clave'],byid[i]['archivo'],byid[i]['clase'],byid[i]['no_recalcular_salvo'],'Todas','Todas','Todas','MAPA_H006/'+i] for i in ['R09','R12','R13','R15','R19']]
    missing += [['H006-2027','Oferta y primer ingreso 2027','No evaluable aún','7_Ofertadas_No_Abiertas','E','MU 2027 y oferta aceptada en PES','Todas','Todas','Todas','H002/V06 carga preparada C']]
    s=sheet('0_Resumen','IPSS · Qué logramos y qué falta',[20,45,70,56,26,65,19,22,28,30],7,[(3,'Resumen de resultados gobernados: cifras reutilizadas, límites visibles y ninguna nueva paridad. Tablas de detalle y filtros en hojas 6–8.'),(4,'Corte: 30-10-2026. A oficial; B observado; C implementación/inferencia; D decisión interna; E pendiente. H001 es indicador interno, no tasa oficial.')]);s['titleEnd']='F';s['noteHeights']={3:36,4:40}
    hdr=['Resultado','Pregunta / motivo','Cifra clave o estado','Hoja / archivo de detalle','Clase','Condición de cierre o reapertura','Sede','Jornada','Sector IPSS','Fuente']
    block(s,'Logramos','Qué logramos y por qué',7,0,hdr,rows,'MAPA_H006; CIFRAS_CLAVE; COHERENCIA_TIPO_H005C')
    block(s,'Falta','Qué falta y por qué',23,0,hdr,missing,'MAPA_H006; H002')
    s['customNotes']=[dict(range='A6:F6',text='QUÉ LOGRAMOS Y POR QUÉ'),dict(range='A22:F22',text='QUÉ FALTA Y POR QUÉ')];s['renders']=['A1:F12','A13:F21','A22:F30']
    sheets.remove(s);sheets.insert(0,s)
    result=dict(antiguas=len(old),vig1_antiguas=sum(r[10] for r in old),extincion_2027=sum(r[18]=='Sí' for r in old),extincion_2027_E=sum(r[18]=='E' for r in old),rezago=sum(r[15] for r in old),rezago_E=sum(r[16] for r in old),no_abiertas=len(unopened),no_abiertas_por_anio=dict(sorted(ny.items())),tendencia=dict(st),familias_tendencia=len(trend),top5_alzas=[dict(familia=r[0],carrera=r[1],delta=r[24],base2022=r[14],matricula2026=r[22]) for r in pos[:5]],top5_bajas=[dict(familia=r[0],carrera=r[1],delta=r[24],base2022=r[14],matricula2026=r[22]) for r in neg[:5]],vig_mu2026=dict(vig_all),fuentes=sources,criterio_rezago='2026 menos ANIO_ING_ACT > duración de estudios en semestres / 2; sin meses, aproximación C',criterio_tendencia='Prioridad CERRADA > NUEVA > EN_EXTINCION > ALZA/BAJA/ESTABLE; +/-10%; referencia 2022',alcance='Agregados nuevos autorizados; no reconstruye enlaces ni modifica reglas de cálculo activas')
    dump(OUT/'RESULTADOS_H006.json',result)
    dump(OUT/'DATOS_H006.json',dict(antiguas=old,no_abiertas=unopened,tendencia=trend,mu_vig1_por_codigo=dict(sorted(mu.items())),cohortes_por_codigo=[dict(codigo=c,cohorte=k,matriculas=n) for (c,k),n in sorted(cohort.items())]))
    return result

#!/usr/bin/env python3
"""Cuadratura agregada H002d. No exporta identidades ni modifica fuentes."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from resolver_planes_h002c import txt, sha, load, dump, rows, dimension, write_same


def count(v):
    s=txt(v)
    if not s:
        return None
    n=float(s)
    if n < 0 or not n.is_integer():
        raise ValueError('Conteo no entero/no positivo')
    return int(n)


def combine(a,b,c):
    ev=[set(x) for x in (a,b,c) if x]
    if not ev:
        return 'SIN_CALCE'
    if any(not x & y for i,x in enumerate(ev) for y in ev[i+1:]):
        return 'CONFLICTO'
    decisive=[next(iter(x)) for x in ev if len(x)==1]
    if len(set(decisive))>1:
        return 'CONFLICTO'
    if len(decisive)>=2 and len(set(decisive))==1 and all(decisive[0] in x for x in ev):
        return 'CALCE_UNICO'
    return 'CALCE_DEBIL'


def compatible_profile(profiles, target):
    """Guardia de alcance: un subtotal numérico no vence un perfil incompatible."""
    return not profiles or tuple(target) in {tuple(x) for x in profiles}


def inputs():
    path=OUT/'FUENTES_H002D.json'
    cat=load('data/catalogo_fuentes/CATALOGO_FUENTES.json')
    if path.exists():
        ss=json.loads(path.read_text())
    else:
        ss=[]
        rels=[
            'data/catalogo_fuentes/CATALOGO_FUENTES.json',
            'data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json',
            'outputs/paridad_codigo_sies_20261029/REVISION_CASO_A_CASO_12_v2.json',
            'outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json',
            'outputs/paridad_codigo_sies_20261029/FUENTES_H002C.json',
            'outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json',
            'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json',
            'data/versiones_historicas_sies_umas/fase_2_20261015/historia_codigo_anio.tsv',
            'outputs/matriz_cuadratura_totales_20261028/FUENTE_MRUN2026_Y_LIMPIEZA.json',
            'procesos/caracterizacion/gobernanza/sies/MATRICULA_2007_2026.manifest.json',
            'procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json',
            'procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv',
            'data/diccionario_umas/CONTROLES_UMAS.json',
            'oferta_academica_2027/00_fuentes_originales/etapa1_octubre_20261020/Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf']
        for rel in rels:
            ss.append({'id':rel,'ruta':str(ROOT/rel),'sha256':sha(ROOT/rel),'clase':'A' if rel.endswith('.pdf') else 'B/C'})
        wanted={'Matricula_2007_2026_WEB_10_07_2026.csv','PROMEDIOSDEALUMNOS_7804.xlsx',
            'PROMEDIOSDEALUMNOS_12166.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx','PROMEDIOSDEALUMNOS_2071.xlsx',
            'DATOSDEALUMNOS_12159.xlsx','Permanencia.xlsx'}
        for e in cat['catalogo']:
            if e['archivo'] in wanted:
                ss.append({'id':e['archivo'],'ruta':e['ruta_consolidada'],'sha256':e['sha256'],'clase':'B',
                    'datos_personales':e['archivo']!='Matricula_2007_2026_WEB_10_07_2026.csv'})
        # El registro original indicado por Alexi se verifica como referencia sin tocarlo.
        ext=Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/gobernanza/sies')
        for name in ['MATRICULA_2007_2026.manifest.json','TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json']:
            ss.append({'id':'CARACTERIZACION/'+name,'ruta':str(ext/name),'sha256':sha(ext/name),'clase':'B/C'})
    for e in ss:
        if sha(e['ruta'])!=e['sha256']:
            raise ValueError('Fuente alterada: '+e['id'])
    return ss


def build():
    sources=inputs();src={x['id']:Path(x['ruta']) for x in sources}
    def local(p):return json.loads(src[p].read_text())
    ref=local('procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.manifest.json')
    bridgepath=src['procesos/caracterizacion/gobernanza/sies/TABLA_PUENTE_CSV_BASE_RETENCION_MU.csv']
    if sha(bridgepath)!=ref['salidas']['csv_sha256']:
        raise ValueError('Puente distinto del manifiesto gobernado')
    siesmanifest=local('procesos/caracterizacion/gobernanza/sies/MATRICULA_2007_2026.manifest.json')
    if sha(src['Matricula_2007_2026_WEB_10_07_2026.csv'])!=siesmanifest['sha256']:
        raise ValueError('Publicación distinta del manifiesto')
    public={};all_rows=0;ipss_rows=0;nonstandard=[]
    with src['Matricula_2007_2026_WEB_10_07_2026.csv'].open(encoding='latin1',newline='') as f:
        rd=csv.DictReader(f,delimiter=';')
        if len(rd.fieldnames)!=58:
            raise ValueError('Publicación no tiene las 58 columnas esperadas')
        for line,row in enumerate(rd,2):
            all_rows+=1
            if row['CÓDIGO DE INSTITUCIÓN']!='162':continue
            ipss_rows+=1
            year=int(row['AÑO'].removeprefix('MAT_'));code=row['CÓDIGO CARRERA']
            if not re.fullmatch(r'I162S\d+C\d+J\d+V\d+',code):
                nonstandard.append({'anio':year,'codigo_literal':code,'fila_fuente':line,
                    'clase':'B/E','tratamiento':'Literal histórico fuera del foco H002; no normalizar ni inventar componentes.'})
            if (year,code) in public:
                raise ValueError('Llave anual pública duplicada: no sumar silenciosamente')
            public[(year,code)]={'total':count(row['TOTAL MATRÍCULA']),
                'primer_anio':count(row['TOTAL MATRÍCULA PRIMER AÑO']), 'fila_fuente':line,
                'nombre':row['NOMBRE CARRERA'],'sede':row['NOMBRE SEDE'],'jornada':row['JORNADA'],'modalidad':row['MODALIDAD']}
    if all_rows!=280160:
        raise ValueError('Cobertura pública distinta: no completar ausencias con supuestos')
    with bridgepath.open(encoding='utf-8-sig') as f:
        bridge={}
        for row in csv.DictReader(f):
            year=int(row['ANIO']);code=row['CODIGO_CARRERA_CSV'];s,c,j,v=dimension(code)
            if (s,c,j,v)!=(row['COD_SED'],row['COD_CAR'],row['JOR'],row['VERSION']):
                raise ValueError('Llave del puente no coincide con código literal')
            bridge[(year,code)]={'total':count(row['BASE_TOTAL_FILAS']),'VIG1':count(row['BASE_VIG1']),
                'publicado_puente':count(row['TOTAL_MATRICULA_CSV'])}
    if len(bridge)!=198:
        raise ValueError('Puente fuera de cobertura gobernada')
    # Reusar agregados MRUN gobernados; sin lectura de registros individuales MRUN.
    master=local('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
    mr={}
    for row in master['mrun_anual']:
        k=(int(row['cat_periodo']),row['codigo_unico'])
        if k in mr:raise ValueError('MRUN anual agregado duplicado')
        mr[k]=count(row['filas_matricula'])
    m26=local('outputs/matriz_cuadratura_totales_20261028/FUENTE_MRUN2026_Y_LIMPIEZA.json')
    if any(mr.get((2026,x['codigo_sies']))!=x['mrun'] for x in m26['paridad_por_codigo']):
        raise ValueError('Agregados MRUN gobernados discrepan')
    previous=local('outputs/paridad_codigo_sies_20261029/REVISION_CASO_A_CASO_12_v2.json')
    pending=local('outputs/paridad_codigo_sies_20261029/DECISIONES_PENDIENTES.json')
    previous_group={x['numero']:x for x in pending['version_multiple_E_por_grupo']}
    sies_rows={x['codigo_unico']:x for x in load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas'] if x['anio']==2027}
    profile=local('outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.json')
    plan_sites=defaultdict(set)
    for x in profile['perfiles']:plan_sites[(x['codcarpr'],x['CODPESTUD'])].add(x['sede_umas'])
    careers={x['codcarpr'] for x in previous['casos']}
    # Conjuntos privados sólo en memoria; no se guardan ni se imprimen valores.
    pp=defaultdict(set);annual=defaultdict(set);cli_plans=defaultdict(set)
    for name in ['PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx',
                 'PROMEDIOSDEALUMNOS_3233.xlsx','PROMEDIOSDEALUMNOS_2071.xlsx']:
        n=0
        for _,row in rows(src[name],'Hoja1'):
            car,plan,year,jour,period,cli=(txt(row.get(k)) for k in ['CODCARR','PLAN_DE_ESTUDIO','ANO','JORNADA','PERIODO','CODCLI'])
            if car not in careers or year not in {'2024','2025','2026'} or not cli or not plan or plan.upper() in {'NULL','NAN','NONE'}:continue
            pp[(name,car,plan,jour,int(year),period)].add(cli)
            annual[(name,car,plan,jour,int(year))].add(cli)
            cli_plans[(cli,car,int(year))].add(plan);n+=1
        print('Actividad leída',name,n,'filas de carreras del foco; sin exportar identificadores',flush=True)
    da=[];owners=defaultdict(set)
    for _,row in rows(src['DATOSDEALUMNOS_12159.xlsx'],'Hoja1'):
        cli=txt(row.get('CODCLI'));car=txt(row.get('CODCARPR'))
        if not cli or car not in careers:continue
        owners[cli].add(txt(row.get('RUT')))
        da.append((cli,car,txt(row.get('SEDE')),txt(row.get('JORNADA')),txt(row.get('ANOMATRICULA'))))
    per=[]
    for _,row in rows(src['Permanencia.xlsx'],'Worksheet'):
        cli=txt(row.get('CODCLI'));car=txt(row.get('CARRERA_ALUM'))
        if cli and car in careers:
            per.append((cli,car,txt(row.get('COD_SEDE')),txt(row.get('JORNADA')),txt(row.get('ANO'))))
    def internal_rows(case,year):
        car=case['codcarpr'];site=case['sede'];jour=case['jornada'];plans={p['plan'] for p in case['planes']}
        output=[];group_ids=defaultdict(set);group_plans=defaultdict(set)
        for k,ids in sorted(annual.items()):
            name,c,p,j,y=k
            if (c,j,y)!=(car,jour,year) or p not in plans:continue
            sites=plan_sites.get((car,p),set())
            if sites!={site}:continue
            output.append({'fuente':name,'anio':year,'plan':p,'jornada':jour,'sede_catalogo':site,
                'ventana':'ANUAL_ACTIVIDAD','expedientes':len(ids),'unidad':'CODCLI distintos con actividad',
                'estado_sede':'C sede de catálogo; no acredita sede histórica individual','comparable_corte_SIES':False})
            group_ids[(name,'ANUAL_GRUPO')].update(ids);group_plans[(name,'ANUAL_GRUPO')].add(p)
            for (nn,cc,pl,jj,yy,pd),idp in sorted(pp.items()):
                if (nn,cc,pl,jj,yy)==k:
                    output.append({'fuente':name,'anio':year,'plan':p,'jornada':jour,'sede_catalogo':site,
                        'ventana':'PERIODO_UMAS_'+pd,'expedientes':len(idp),'unidad':'CODCLI distintos con actividad',
                        'estado_sede':'C sede de catálogo; no acredita sede histórica individual','comparable_corte_SIES':False})
                    if pd=='1':
                        group_ids[(name,'PERIODO_UMAS_1_GRUPO')].update(idp);group_plans[(name,'PERIODO_UMAS_1_GRUPO')].add(p)
        for (name,window),ids in sorted(group_ids.items()):
            output.append({'fuente':name,'anio':year,'plan':'CONJUNTO_PLANES_DEL_GRUPO','ventana':window,
                'planes_incluidos':sorted(group_plans[(name,window)]),'expedientes':len(ids),
                'unidad':'CODCLI distintos en la unión de planes del grupo; no suma de subtotales',
                'comparable_corte_SIES':False})
        # No convertir una foto actual en una matrícula histórica anual.
        for name,data in [('DATOSDEALUMNOS_12159.xlsx',da),('Permanencia.xlsx',per)]:
            if year!=2026:
                output.append({'fuente':name,'anio':year,'plan':None,'ventana':'FOTO_ACTUAL_NO_HISTORICA',
                    'expedientes':None,'estado':'E: no acredita fotografía del año','comparable_corte_SIES':False})
                continue
            all_ids=set();linked=defaultdict(set);amb=set();missing=set();ownerbad=set()
            for cli,c,s,j,yreported in data:
                if (c,s,j)!=(car,site,jour):continue
                all_ids.add(cli)
                if len(owners.get(cli,set()))>1:
                    ownerbad.add(cli);continue
                candidates=cli_plans.get((cli,car,year),set())
                if not candidates:missing.add(cli)
                elif len(candidates)>1:amb.add(cli)
                else:
                    pl=next(iter(candidates))
                    if pl in plans:linked[pl].add(cli)
            # Total sin plan permite recomprobar indicios de Claude; no vota c.
            output.append({'fuente':name,'anio':year,'plan':None,'ventana':'FOTO_CARRERA_SIN_PLAN',
                'expedientes':len(all_ids),'sin_plan_actividad_2026':len(missing),'plan_multiple':len(amb),
                'CODCLI_con_propietario_multiple':len(ownerbad),'unidad':'CODCLI distintos en foto actual',
                'comparable_corte_SIES':False,'estado':'B: fotografía actual, sin columna de plan'})
            for pl,ids in sorted(linked.items()):
                output.append({'fuente':name,'anio':year,'plan':pl,'ventana':'FOTO_CON_PLAN_UNICO_OBSERVADO_PROMEDIOS',
                    'expedientes':len(ids),'unidad':'CODCLI distintos, plan por enlace interno sólo analítico',
                    'comparable_corte_SIES':False,'estado':'C/E: no acredita matrícula al 30-abr ni vigencia histórica'})
            union=set().union(*linked.values()) if linked else set()
            output.append({'fuente':name,'anio':year,'plan':'CONJUNTO_PLANES_DEL_GRUPO',
                'ventana':'FOTO_GRUPO_CON_PLAN_OBSERVADO','expedientes':len(union),
                'completo_en_extracto':len(union)==len(all_ids) and not amb and not missing and not ownerbad,
                'unidad':'CODCLI distintos; no sumar planes repetidos','comparable_corte_SIES':False})
        return output
    def totals(code,year):
        x=public.get((year,code));mu=bridge.get((year,code));m=mr.get((year,code))
        return {'anio':year,'codigo_unico':code,'SIES_total':x['total'] if x else 0,
            'SIES_primer_anio':x['primer_anio'] if x else None,
            'SIES_estado':'B_PUBLICADO' if x else 'SIN_FILA_EN_PUBLICACION_VERIFICADA',
            'fila_SIES':x['fila_fuente'] if x else None,'MU_total':mu['total'] if mu else 0,
            'MU_VIG1':mu['VIG1'] if mu else 0,'MRUN_total':m,
            'MRUN_estado':'B/C agregado gobernado' if m is not None else 'E: sin fila agregada; no inferir cero',
            'unidad_publica_MU_MRUN':'registros de matrícula; no personas únicas'}
    results=[]
    for case in previous['casos']:
        nums=case['numero_original'];opts=[x['codigo_unico'] for x in case['opciones_SIES']]
        opts=sorted(set(opts+case['opciones_historicas_sin_oferta_2027']))
        table=[];internals=[];matches=[];deltas=[]
        for year in [2024,2025,2026]:
            ii=internal_rows(case,year);internals.extend(ii)
            for code in opts:
                t=totals(code,year);table.append(t)
                for ix in ii:
                    if ix.get('plan') is None or ix['expedientes'] is None:continue
                    context_profile=previous_group[nums]['perfiles']
                    sies_profile=[sies_rows[code]['duracion_total_semestres'],sies_rows[code]['tipo_plan_codigo']] if code in sies_rows else []
                    compat=compatible_profile(context_profile,sies_profile)
                    eligible=(ix['ventana'] in {'ANUAL_GRUPO','PERIODO_UMAS_1_GRUPO'} or
                        (ix['ventana']=='FOTO_GRUPO_CON_PLAN_OBSERVADO' and ix['completo_en_extracto'])) and compat
                    equal=bool(ix['expedientes']>0 and ix['expedientes']==t['SIES_total'] and
                        t['SIES_total'] in {t['MU_total'],t['MU_VIG1']})
                    d={'anio':year,'codigo_unico':code,'plan':ix['plan'],'fuente':ix['fuente'],'ventana':ix['ventana'],
                       'interno_expedientes':ix['expedientes'],'SIES_matriculas':t['SIES_total'],
                       'delta_interno_menos_publico':ix['expedientes']-t['SIES_total'],
                       'ventana_admitida_c':eligible,'igualdad_exacta_con_control_MU':equal and eligible,
                       'perfil_grupo_compatible':compat,
                       'motivo_exclusion_c':'Perfil de grupo incompatible; coincidencia numérica no cambia la correspondencia.' if not compat else
                           'Subtotal de plan o foto con cobertura parcial: no representa al grupo completo.' if not eligible else None,
                       'limite':'C/E igualdad de totales entre ventanas distintas, no identidad ni aceptación individual'}
                    deltas.append(d)
                    if equal and eligible:matches.append(d)
        c=sorted({m['codigo_unico'] for m in matches});a=case['opciones_perfil_a'];b=case['opciones_documentales_b']
        st=combine(a,b,c)
        results.append({'numero_original':nums,'codcarpr':case['codcarpr'],'sede':case['sede'],'jornada':case['jornada'],
            'grupo':case['grupo'],'clasificacion':st,'evidencias':{'a_perfil':a,'b_documental_v20':b,'c_cuadratura_exacta':c},
            'estado_c':'UNIVOCA_INDICIARIA' if len(c)==1 else 'AMBIGUA' if c else 'SIN_IGUALDAD_EXACTA',
            'cuadraturas_exactas_c':matches,'comparacion_interno_publicacion':deltas,
            'totales_por_anio_codigo':table,'conteos_internos_por_anio_plan':internals,
            'estado_H002c_anterior':case['clasificacion'],'admision_2027_H002c':case['admision_2027'],
            'nota':'Propuesta C/E. Cada a/b/c es una sola vía; fuentes/cortes distintos no se suman. No se usan distancias aproximadas ni vía de ingreso para escoger versión.',
            'decision_Alexi':'____','aplicada':False})
    results.sort(key=lambda x:({'CALCE_UNICO':0,'CALCE_DEBIL':1,'CONFLICTO':2,'SIN_CALCE':3}[x['clasificacion']],x['numero_original']))
    table2027={x['codigo_unico']:x for x in load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas'] if x['anio']==2027}
    out43=[];observations=[]
    for row in pending['nuevo_2027_sin_plan_E']:
        code=row['codigo_unico'];history=[{'anio':y,'matriculas':p['total'],'fila_SIES':p['fila_fuente']} for (y,c),p in sorted(public.items()) if c==code and p['total'] is not None and p['total']>0]
        muhist=[{'anio':y,'MU_total':p['total'],'MU_VIG1':p['VIG1']} for (y,c),p in sorted(bridge.items()) if c==code and p['total'] is not None and p['total']>0]
        category='HISTORICO_SIN_MATRICULA_VIGENTE' if history else 'CODIGO_NUEVO_2027_SIN_HISTORIA'
        last=history[-1] if history else None
        if history and last['anio']>=2024:
            raise ValueError('Hallazgo histórico distinto del esperado; no forzar categoría')
        if not history and muhist:
            raise ValueError('Código sin matrícula pública con MU interna: necesita categoría E propia')
        item={'codigo_unico':code,'nombre_carrera':row['nombre_carrera'],'cod_sede':row['cod_sede'],
            'sede_umas':{'2':'RE','3':'CO','4':'PTG'}.get(row['cod_sede']),'cod_jornada':row['cod_jornada'],
            'modalidad':row['modalidad'],'modalidad_codigo':row['modalidad_codigo'],'vigencia_2027_declarada':row['vigencia_2027'],
            'categoria':category,'clase':'B/C','historia_publica':history,'ultima_matricula_publica':last,'historia_MU_2022_2026':muhist,
            'listado_para_UMAS':not history,'decision_Alexi':'____','aplicada':False,
            'nota':'Sin historia significa ausencia de matrícula en las fuentes/coberturas verificadas; no acredita primera creación en oferta.' if not history else
                'D: se deja fuera de la paridad para retención 2027 en esta propuesta; no se elimina de oferta ni del historial.'}
        out43.append(item)
        if row['vigencia_2027']=='2' and not any(h['anio']>=2024 for h in history):
            observations.append({'codigo_unico':code,'nombre_carrera':row['nombre_carrera'],'vigencia_declarada':'2',
                'significado_oficial':'Vigente sin estudiantes nuevos; solamente quedan estudiantes antiguos',
                'ultima_matricula_publica':last,'estado':'OBSERVACION_OFERTA','clase':'E para Alexi; A significado; B declaración de carga',
                'fuente_oficial':'oferta_academica_2027/00_fuentes_originales/etapa1_octubre_20261020/Instructivo_Oferta_Academica_2027_CFT_E_IP_DFE.pdf',
                'pagina':28,'no_modificar_oferta':True,'decision_Alexi':'____'})
    out43.sort(key=lambda x:(not x['listado_para_UMAS'],x['codigo_unico']))
    notes=[
        'A: manual Oferta 2027 página 28: vigencia 2 no es cerrada. Ausencia de matrícula reciente se observa sin cambiar oferta.',
        'B: publicación completa MAT_2007–MAT_2026; conteos de matrícula y primer año por código. Blancos de primer año no se vuelven cero.',
        'C: c exige igualdad exacta positiva del conjunto de planes del grupo y concordancia pública con MU total o VIG1. No sumas de subtotales; fotos parciales y perfiles incompatibles no votan. Una aproximación es sólo indicio no decisivo.',
        'C/E: cuadros de actividad anual, período 1 y fotos actuales tienen ventanas diferentes del corte SIES. La igualdad no acredita la misma población.',
        'C/E: DA/Permanencia no traen plan. Su vínculo con plan único observado en PROMEDIOS es analítico, no una asignación histórica formal.',
        'E: v20 no acredita aceptación PES. Se reutiliza b sin convertir D internas en documental.',
        'D: no aplicar propuestas; no modificar tabla de paridad, diccionario, fuentes, indicadores ni oferta.']
    review={'hito':'H002d','clase':'B/C/E','reglas':notes,'conteos':dict(Counter(x['clasificacion'] for x in results)),
        'unidad_interna':'expedientes CODCLI distintos; no sumar fotos ni extracciones solapadas',
        'unidad_SIES_MU_MRUN':'matrículas por año/código; no personas únicas','casos':results,'sin_aplicar':True}
    proposal={'hito':'H002d','clase':'B/C/D/E','reglas':notes,'conteos':dict(Counter(x['categoria'] for x in out43)),
        'casos':out43,'observaciones_oferta':sorted(observations,key=lambda x:x['codigo_unico']),
        'observaciones_transversales_no_sumar':True,'sin_aplicar':True}
    audit={'filas_publicacion':all_rows,'filas_IPSS_publicacion':ipss_rows,'filas_puente':len(bridge),
        'codigos_historicos_no_ISCJV_fuera_foco':nonstandard,
        'MAT_2026_IPSS':sum(p['total'] for (y,c),p in public.items() if y==2026),
        'puente_clave':ref['llave'],'publicacion_vs_puente_diferencias':[
            {'anio':y,'codigo':c} for (y,c),p in bridge.items() if (public.get((y,c),{}).get('total') if (y,c) in public else 0)!=p['publicado_puente']],
        'MRUN_2026_diferencias':sum(mr.get((2026,x['codigo_sies']))!=x['mrun'] for x in m26['paridad_por_codigo']),
        'MRUN_agregado_2024_2025_2026':True,'sin_identificadores_en_salidas':True}
    for e in sources:
        if sha(e['ruta'])!=e['sha256']:raise ValueError('Fuente modificada durante lectura')
    return sources,review,proposal,audit


def render12(v):
    ll=['# H002d · revisión de doce combinaciones, versión 3','','Propuestas C/E sin aplicar. Se conservan v1 y v2. Cada a/b/c cuenta como una vía, no como un voto por archivo.','']
    for x in v['casos']:
        ll += [f"## Caso {x['numero_original']}. {x['codcarpr']} / {x['sede']} / {x['jornada']} — {x['clasificacion']}",'',
            'a: '+(', '.join(x['evidencias']['a_perfil']) or 'sin perfil completo')+'; b: '+(', '.join(x['evidencias']['b_documental_v20']) or 'sin documental de estas opciones')+'; c: '+(', '.join(x['evidencias']['c_cuadratura_exacta']) or 'sin igualdad exacta')+'.','',
            '| Año | Código | SIES total | SIES primer año | MU total | MU VIG1 | MRUN agregado |','|---:|---|---:|---:|---:|---:|---:|']
        for r in x['totales_por_anio_codigo']:
            ll.append('| '+' | '.join('NR/E' if r[k] is None else str(r[k]) for k in ['anio','codigo_unico','SIES_total','SIES_primer_anio','MU_total','MU_VIG1','MRUN_total'])+' |')
        ll += ['', 'Sin fila pública: se informa sin matrícula observada en la cobertura; primer año NR no equivale a cero. MRUN E significa sin fila agregada.','',
            '| Año | Fuente interna | Plan | Ventana | Expedientes distintos |','|---:|---|---|---|---:|']
        for r in x['conteos_internos_por_anio_plan']:
            ll.append('| '+str(r['anio'])+' | '+r['fuente']+' | '+str(r.get('plan') or 'sin plan')+' | '+r['ventana']+' | '+str(r['expedientes'] if r['expedientes'] is not None else 'E/no histórica')+' |')
        ll += ['', '**Igualdades que respaldan c:**','']
        if not x['cuadraturas_exactas_c']:ll.append('Ninguna. Los deltas completos, incluidos los aproximados, permanecen en el JSON.')
        for r in x['cuadraturas_exactas_c']:
            ll.append('- '+str(r['anio'])+' · '+r['fuente']+' · '+r['plan']+' · '+r['ventana']+': '+str(r['interno_expedientes'])+' = '+r['codigo_unico']+' ('+str(r['SIES_matriculas'])+'); MU concordante.')
        ll += ['',x['nota'],'',x['admision_2027_H002c'],'','Decisión Alexi: ____','']
    ll += ['## Reglas y fuentes','',*['- '+s for s in v['reglas']], '', 'Rutas y SHA-256 completos: FUENTES_H002D.json. Conteos y diferencias completos: JSON complementario.']
    return '\n'.join(ll)+'\n'


def render43(v):
    ll=['# H002d · reclasificación de los 43 códigos, versión 2','','Propuesta sin aplicar. Las categorías principales suman 43. Observaciones de oferta son banderas transversales: no sumarlas.','',
        '## Lista única para solicitar a UMAS: sin historia de matrícula','',
        '| Código | Nombre SIES | Sede | Jornada SIES | Modalidad |','|---|---|---|---|---|']
    for x in v['casos']:
        if x['listado_para_UMAS']:
            ll.append('| '+' | '.join(str(x[k]) for k in ['codigo_unico','nombre_carrera','cod_sede','cod_jornada','modalidad'])+' |')
    ll += ['', '## Histórico sin matrícula vigente reciente','','| Código | Última matrícula pública | Total en ese año | Matrícula MU 2022–2026 |','|---|---:|---:|---|']
    for x in v['casos']:
        if not x['listado_para_UMAS']:
            h=x['ultima_matricula_publica'];m=', '.join(str(z['anio'])+': '+str(z['MU_total']) for z in x['historia_MU_2022_2026']) or 'sin filas positivas'
            ll.append('| '+x['codigo_unico']+' | '+str(h['anio'])+' | '+str(h['matriculas'])+' | '+m+' |')
    ll += ['', '## Observaciones de oferta para Alexi (E)','',
        'A: Manual Oferta 2027, página 28: vigencia 2 = vigente sin nuevos; solamente quedan estudiantes antiguos. No significa carrera cerrada.','',
        '| Código | Vigencia declarada | Última matrícula pública |','|---|---|---|']
    for x in v['observaciones_oferta']:
        h=x['ultima_matricula_publica'];ll.append('| '+x['codigo_unico']+' | 2 | '+(str(h['anio'])+' ('+str(h['matriculas'])+')' if h else 'sin matrícula observada 2007–2026')+' |')
    ll += ['', 'No se modifica la carga. La declaración de antiguos sin matrícula pública reciente requiere explicación institucional; no se concluye error o cierre por ausencia.','',
        '## Decisiones por código','']
    for x in v['casos']:
        ll += ['### '+x['codigo_unico']+' · '+x['categoria'],'',x['nota'],'','Decisión Alexi: ____','']
    ll += ['## Fuentes y límites','',*['- '+s for s in v['reglas']], '', 'Rutas y hashes: FUENTES_H002D.json; origen de la vigencia: carga 2027 preservada en H002.']
    return '\n'.join(ll)+'\n'


def main():
    ss,v,p,a=build();verify='--verificar' in sys.argv
    texts={'FUENTES_H002D.json':dump(ss),'REVISION_CASO_A_CASO_12_v3.json':dump(v),
        'REVISION_CASO_A_CASO_12_v3.md':render12(v),'PROPUESTA_PLANES_43_v2.json':dump(p),
        'PROPUESTA_PLANES_43_v2.md':render43(p),'CONTROL_TOTALES_H002D.json':dump(a)}
    for n,t in texts.items():
        if (OUT/n).exists() and (OUT/n).read_text()!=t:raise ValueError('Salida existente distinta: '+n)
    for n,t in texts.items():write_same(OUT/n,t,verify)
    mf={'hito':'H002d','clase':'C','HEAD_base':'cd78f5ac439e442733a69d0d4d30d61619b49b47','fuentes':ss,
        'salidas':{n:hashlib.sha256(t.encode()).hexdigest() for n,t in texts.items()},
        'componentes':{str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['cuadrar_totales_h002d.py','qa_h002d.py','test_h002d.py','ESPECIFICACION_H002D.md']},
        'sin_aplicar':True,'conteos_12':v['conteos'],'conteos_43':p['conteos']}
    write_same(OUT/'MANIFEST_H002D.json',dump(mf),verify)
    print(dump({'12':v['conteos'],'43':p['conteos'],'observaciones_oferta':len(p['observaciones_oferta']),'audit':a}))


if __name__=='__main__':main()

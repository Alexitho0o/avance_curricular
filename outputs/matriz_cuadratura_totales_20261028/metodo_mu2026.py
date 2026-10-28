"""Método preparado; ningún procesamiento 2026 se ejecuta al importar el módulo."""
import collections,csv,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PRIVATE=Path('/Users/alexi/.local/share/ipss')
def _text(x):
    if x is None:return ''
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip().upper()
def _key(r):
    t=_text(r['TIPO_DOCUMENTO']);n=_text(r['NUM_DOCUMENTO']);dv=_text(r['DV']);c=_text(r['CODIGO_UNICO'])
    if not t or not n or (t=='R' and not re.fullmatch(r'[0-9K]',dv)) or not re.fullmatch(r'I162S\d+C\d+J\d+V\d+',c):raise ValueError('Identidad o código incompleto: no se clasifica como ausente')
    return t,n,dv,c
def codigos_con_diferencia():
    p=ROOT/'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/DETALLE_CONCILIACION.csv'
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    if h!='f60b2e327f016ca1abeb8f26f65d11b4b9ebdbaff785a9a4912c40bb21235eaa':raise ValueError('Agregado de diferencias alterado')
    with p.open(encoding='utf-8-sig',newline='') as f:codes={r['CODIGO_COMPLETO'] for r in csv.DictReader(f,delimiter=';') if r['ANIO']=='2026' and r['ALCANCE']=='Pregrado' and int(r['DIF_CSV_VIG1_UNION'])!=0}
    if len(codes)!=48:raise ValueError('El foco debe contener los 48 códigos gobernados')
    return codes
def clasificar(filas_sies,filas_mu,codigos):
    """Filas SIES adaptadas a TIPO_DOCUMENTO/NUM_DOCUMENTO/DV/CODIGO_UNICO.

    Unidad: matrícula documento+DV+código único, deduplicada. El resto de nuestra
    MU se conserva para distinguir ausentes de cambios de código. No calcula tasas.
    """
    ours={}
    for r in filas_mu:
        if _text(r['ANIO_INFORMADO'])!='2026':continue
        c='I162S{}C{}J{}V{}'.format(*(_text(r[k]) for k in ('COD_SED','COD_CAR','JOR','VERSION')))
        k=_key({'TIPO_DOCUMENTO':r['TIPO_DOC'],'NUM_DOCUMENTO':r['N_DOC'],'DV':r['DV'],'CODIGO_UNICO':c})
        vig=_text(r['VIG'])
        if vig not in ('0','1'):raise ValueError('VIG nuestra fuera del universo 0/1; revisar antes de clasificar')
        if k in ours and ours[k]!=vig:raise ValueError('Matrícula nuestra con VIG contradictorio')
        ours[k]=vig
    seen=set();out=collections.defaultdict(collections.Counter);details=[];source_rows=0;outside=0
    for row in filas_sies:
        source_rows+=1
        if _text(row['CODIGO_UNICO']) not in codigos:outside+=1;continue
        k=_key(row)
        if k in seen:continue
        seen.add(k)
        if k not in ours:label='no_esta_en_nuestra_base'
        elif ours[k]=='0':label='vig0_nuestra'
        else:label='vig1_nuestra'
        out[k[3]][label]+=1
        details.append({'llave':k,'clasificacion':label})
    result={'unidad':'matrículas únicas por documento+DV+código','clase':'B fuente SIES; C cruce; E explicación normativa','filas_sies_leidas':source_rows,'filas_fuera_foco':outside,'matriculas_foco':len(seen),'filas_duplicadas_foco':source_rows-outside-len(seen),'por_codigo':[{'codigo_sies':c,'vig1_nuestra':out[c]['vig1_nuestra'],'vig0_nuestra':out[c]['vig0_nuestra'],'no_esta_en_nuestra_base':out[c]['no_esta_en_nuestra_base']} for c in sorted(codigos)]}
    assert sum(sum(r[k] for k in ('vig1_nuestra','vig0_nuestra','no_esta_en_nuestra_base')) for r in result['por_codigo'])==len(seen)
    return result,details
def contrastar_fuente(fuente_sies,sha256_esperado,filas_mu,*,anio_matricula,campos,encoding,detalle_privado):
    """Requiere fuente futura explícita, hash y año acreditado; no busca sustitutos.

    campos mapea nombres estándar a columnas del archivo. No filtra por vigencia
    SIES: el alcance de la descarga/precarga debe documentarse antes de ejecutarlo.
    """
    if anio_matricula!=2026:raise ValueError('Se requiere evidencia de matrícula del año 2026')
    p=Path(fuente_sies)
    if not p.is_file():raise FileNotFoundError('Falta descarga individual PES MU 2026 o precarga AC 2027')
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    if h!=sha256_esperado:raise ValueError('Hash de la fuente SIES distinto')
    filas_mu=list(filas_mu)
    stock=collections.Counter(_text(r['VIG']) for r in filas_mu if _text(r['ANIO_INFORMADO'])=='2026')
    if stock!={'0':960,'1':3145}:raise ValueError('El universo MU 2026 no reproduce la base congelada 142342 (960/3145)')
    dest=Path(detalle_privado).resolve()
    if not dest.is_relative_to(PRIVATE.resolve()):raise ValueError('Identificadores sólo en ~/.local/share/ipss')
    with p.open(encoding=encoding,newline='') as f:
        reader=csv.DictReader(f,delimiter=';')
        if set(campos)!= {'TIPO_DOCUMENTO','NUM_DOCUMENTO','DV','CODIGO_UNICO'} or not set(campos.values()).issubset(reader.fieldnames):raise ValueError('Adaptador de columnas incompleto')
        rows=[{key:r[col] for key,col in campos.items()} for r in reader]
    result,details=clasificar(rows,filas_mu,codigos_con_diferencia())
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(details,ensure_ascii=False,indent=2)+'\n');dest.chmod(0o600)
    result['fuente']={'ruta':str(p),'sha256':h,'anio_matricula':anio_matricula,'encoding':encoding,'columnas':campos}
    result['control_universo_mu2026']={'vig0':stock['0'],'vig1':stock['1'],'base_esperada_sha256':'19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd','nota':'El llamador debe entregar las filas obtenidas de esa fuente verificada; el conteo es control adicional, no reemplaza el hash.'}
    return result

def diagnosticar_mrun(filas_mrun,filas_mu,grupos,codigos,*,_al_evaluar=None):
    """Adaptador diagnóstico A/B/C del 16-10; nunca retorna pares ni identidades.

    Objetivo: cada registro MRUN del foco. Candidatos: matrículas MU, sin usar
    versión como bloqueo. La MU usa SEXO H/M; UMAS M/F es otra codificación.
    Tipo sólo cuando todos los perfiles gobernados de la familia son unánimes.
    No reemplaza el contraste documental de contrastar_fuente.
    """
    import sys
    sys.path.insert(0,str(ROOT))
    from scripts.diagnosticar_candidatos_mrun_umas import birth
    types={'1':'Plan Regular','2':'Plan Especial','3':'Plan Regular de Continuidad'}
    profiles=collections.defaultdict(set);incomplete=set()
    for g in grupos:
        for fam in g['familias']:
            ts={_text(p[1]) for p in g.get('perfiles_duracion_tipo',[])}
            profiles[fam].update(ts)
            if not ts:incomplete.add(fam)
    unanimous={f:types[next(iter(ts))] for f,ts in profiles.items() if len(ts)==1 and f not in incomplete and next(iter(ts)) in types}
    prepared=[];index=collections.defaultdict(list);seen=set()
    for r in filas_mu:
        if _text(r['ANIO_INFORMADO'])!='2026':continue
        c='I162S{}C{}J{}V{}'.format(*(_text(r[k]) for k in ('COD_SED','COD_CAR','JOR','VERSION')))
        ident=_key({'TIPO_DOCUMENTO':r['TIPO_DOC'],'NUM_DOCUMENTO':r['N_DOC'],'DV':r['DV'],'CODIGO_UNICO':c})
        if ident in seen:raise ValueError('MU duplicada: no reducir el universo silenciosamente')
        seen.add(ident)
        vig=_text(r['VIG'])
        if vig not in ('0','1'):raise ValueError('VIG fuera del alcance gobernado')
        ym=birth(r['FECH_NAC']);sx=_text(r['SEXO']);fam=c.rsplit('V',1)[0]
        item={'vig':vig,'familia':fam,'codigo':c};pos=len(prepared);prepared.append(item)
        if ym and sx in ('H','M'):index['2026',ym,sx].append(pos)
    labels=('vig1_candidata_unica','vig0_candidata_unica','varios_candidatos','sin_candidato')
    stages={s:collections.defaultdict(collections.Counter) for s in ('A_anio_nacimiento_sexo','B_mas_familia_ISCJ','C_mas_tipo_solo_unanime')}
    no_comparable=collections.Counter();type_applied=collections.Counter();ambiguities=collections.defaultdict(collections.Counter)
    shared=collections.defaultdict(int);singletons=[];total=outside=0;version_differences=collections.Counter()
    for r in filas_mrun:
        if _text(r['cat_periodo'])!='2026' or _text(r['cod_inst'])!='162':raise ValueError('Se requiere subconjunto MRUN IPSS2026 acreditado')
        c=_text(r['codigo_unico'])
        if c not in codigos:outside+=1;continue
        total+=1;ym=birth(r['fec_nac_alu']);sx={'1':'H','2':'M'}.get(_text(r['gen_alu']));fam=c.rsplit('V',1)[0]
        valid=bool(ym and sx);a=index.get(('2026',ym,sx),[]) if valid else []
        b=[i for i in a if prepared[i]['familia']==fam]
        expected=unanimous.get(fam)
        cc=b if expected is None or _text(r['tipo_plan_carr'])==_text(expected) else []
        if _al_evaluar is not None:_al_evaluar(c,prepared,a,b,cc)
        type_applied['aplicado' if expected is not None else 'omitido_sin_unanimidad_completa']+=1
        if not valid:no_comparable[c]+=1
        for name,ids in zip(stages,(a,b,cc)):
            label='sin_candidato' if not ids else ('varios_candidatos' if len(ids)>1 else 'vig'+prepared[ids[0]]['vig']+'_candidata_unica')
            stages[name][c][label]+=1
        for i in cc:shared[i]+=1
        if len(cc)==1:
            singletons.append((c,cc[0]))
            if prepared[cc[0]]['codigo']!=c:version_differences[c]+=1
        elif cc:
            vs={prepared[i]['vig'] for i in cc}
            ambiguities[c]['varios_solo_vig1' if vs=={'1'} else 'varios_solo_vig0' if vs=={'0'} else 'varios_mixtos_vig1_vig0']+=1
    aggregated={}
    for s,bycode in stages.items():
        aggregated[s]=[{'codigo_sies':c,**{k:bycode[c][k] for k in labels},'registros_mrun':sum(bycode[c].values())} for c in sorted(codigos)]
        assert sum(x['registros_mrun'] for x in aggregated[s])==total
    final=aggregated['C_mas_tipo_solo_unanime']
    reused=collections.Counter(c for c,i in singletons if shared[i]>1)
    for r in final:
        c=r['codigo_sies'];r.update({k:ambiguities[c][k] for k in ('varios_solo_vig1','varios_solo_vig0','varios_mixtos_vig1_vig0')})
        r['sin_datos_comparables_incluido_en_sin_candidato']=no_comparable[c]
        r['unicos_con_fila_mu_compartida_por_varios_registros_mrun']=reused[c]
        r['unicos_con_version_distinta']=version_differences[c]
        assert r['varios_candidatos']==sum(r[k] for k in ('varios_solo_vig1','varios_solo_vig0','varios_mixtos_vig1_vig0'))
    return {'clase':'C/E diagnóstico determinístico de compatibilidad, no identidad ni recepción individual acreditada','unidad':'registros MRUN; candidatos son filas de matrícula MU, no personas deducidas por coincidencia','matriculas_mu':len(prepared),'registros_mrun_foco':total,'registros_mrun_fuera_foco':outside,'etapas':aggregated,'por_codigo':final,'tipo_programa':dict(type_applied),'normalizacion_sexo':'MRUN 1=Hombre -> MU H; MRUN 2=Mujer -> MU M. UMAS M/F no se confunde con MU H/M.','perfiles_tipo':'Unión de perfiles existentes compatibles con familia; si falta perfil o hay varios tipos, no se filtra por tipo. No se elige tipo a partir de los MRUN objetivo.','fuente_fecha':'birth de scripts/diagnosticar_candidatos_mrun_umas.py; AAAAMM sin día; 190001 sin dato','version_usada_como_bloqueo':False,'identidades_certificadas':0,'vinculos_rut_mrun_persistidos':False,'limite':'Un candidato no acredita identidad. Distintos registros MRUN pueden compartir candidato MU; se informa el conteo, sin forzar asignación uno a uno ni sumar candidatos como personas confirmadas.'}


def diagnosticar_inverso_mrun(filas_mrun,filas_mu,grupos,codigos):
    """Reutiliza exactamente A/B/C; observador transitorio, sin guardar vínculos.

    La prueba inversa usa todo MRUN2026 IPSS y publica además la sensibilidad
    limitada a los 48 códigos. Las tablas origen/destino cuentan soportes de
    perfil, no personas ni asignaciones exclusivas.
    """
    filas_mrun=list(filas_mrun);filas_mu=list(filas_mu)
    all_codes={_text(r['codigo_unico']) for r in filas_mrun}
    reached={scope:{s:set() for s in 'ABC'} for scope in ('todo_IPSS','solo_48_codigos')}
    rejected=collections.defaultdict(collections.Counter);pairs=collections.Counter();prepared_last=[]
    def observe(c,prepared,a,b,cc):
        nonlocal prepared_last
        prepared_last=prepared
        for stage,ids in zip('ABC',(a,b,cc)):
            reached['todo_IPSS'][stage].update(ids)
            if c in codigos:reached['solo_48_codigos'][stage].update(ids)
        if c not in codigos or cc:return
        row=rejected[c];row['sin_candidato_C']+=1
        if not a:row['sin_candidato_A']+=1;return
        row['con_candidato_A']+=1
        same=any(prepared[i]['familia']==c.rsplit('V',1)[0] for i in a)
        other=any(prepared[i]['familia']!=c.rsplit('V',1)[0] for i in a)
        row['A_solo_otra_familia' if other and not same else 'A_misma_y_otra_familia' if other else 'A_solo_misma_familia']+=1
        vig={prepared[i]['vig'] for i in a}
        row['A_solo_vig1' if vig=={'1'} else 'A_solo_vig0' if vig=={'0'} else 'A_mixto_vig0_vig1']+=1
        # Una vez por registro MRUN y código/VIG de destino; no por cada fila candidata.
        for dest,v in {(prepared[i]['codigo'],prepared[i]['vig']) for i in a}:
            pairs[c,dest,v]+=1
    diagnosticar_mrun(filas_mrun,filas_mu,grupos,all_codes,_al_evaluar=observe)
    ours=[i for i,r in enumerate(prepared_last) if r['vig']=='1' and r['codigo'] in codigos]
    inverse=[]
    for c in sorted(codigos):
        ids={i for i in ours if prepared_last[i]['codigo']==c};row={'codigo_sies':c,'vig1_nuestra':len(ids)}
        for scope,stages in reached.items():
            row[scope]={s:{'con_candidato':len(ids & used),'sin_candidato':len(ids-used)} for s,used in stages.items()}
        inverse.append(row)
    reject_keys=('sin_candidato_C','sin_candidato_A','con_candidato_A','A_solo_otra_familia','A_misma_y_otra_familia','A_solo_misma_familia','A_solo_vig1','A_solo_vig0','A_mixto_vig0_vig1')
    residual=[{'codigo_origen_mrun':c,**{k:rejected[c][k] for k in reject_keys}} for c in sorted(codigos)]
    summary={k:sum(r[k] for r in residual) for k in reject_keys}
    summary['vig1_foco']=len(ours)
    summary['inversa']={scope:{s:{k:sum(r[scope][s][k] for r in inverse) for k in ('con_candidato','sin_candidato')} for s in 'ABC'} for scope in reached}
    assert summary['sin_candidato_C']==summary['sin_candidato_A']+summary['con_candidato_A']
    assert summary['con_candidato_A']==sum(summary[k] for k in ('A_solo_otra_familia','A_misma_y_otra_familia','A_solo_misma_familia'))
    return {'clase':'C/E','resumen':summary,'inversa_por_codigo':inverse,'residual_240_por_codigo':residual,'soportes_origen_destino':[{'codigo_origen_mrun':a,'codigo_destino_mu':b,'vig_destino':v,'registros_mrun_con_soporte':n} for (a,b,v),n in sorted(pairs.items())], 'unidad':'Inversa: matrículas MU VIG1; residual: registros MRUN. Soportes origen/destino no sumables entre destinos.', 'alcance':'Comparación inversa principal contra todo MRUN2026 IPSS, con sensibilidad sólo 48 códigos; candidatos del residual contra las 4105 filas MU.', 'dictamen':'Compatibilidad demográfica no demuestra reclasificación ni ausencia de matrícula. Los perfiles sin candidato pueden reflejar cobertura, datos no comparables o discrepancias de atributos. No se fuerza identidad ni versión.', 'vinculos_rut_mrun_persistidos':False}

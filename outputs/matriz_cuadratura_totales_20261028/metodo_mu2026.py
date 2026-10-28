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

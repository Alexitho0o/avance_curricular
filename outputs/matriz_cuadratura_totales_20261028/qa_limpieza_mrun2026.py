"""QA independiente SQL: metadatos, fuentes, bloques y ausencia de identificadores."""
import collections,csv,datetime,hashlib,json,re,sqlite3,subprocess,sys
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def txt(x):
    if x is None:return ''
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip().upper()
def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    baseline_head='782efc8b4e37e60898cbea832667c887199bf536';assert subprocess.run(['git','merge-base','--is-ancestor',baseline_head,head],cwd=ROOT,capture_output=True).returncode==0
    previous=json.loads(subprocess.check_output(['git','show',baseline_head+':outputs/matriz_cuadratura_totales_20261028/MATRIZ_CUADRATURA_TOTALES_2022_2026.json'],cwd=ROOT,text=True))
    matrix=read(OUT/'MATRIZ_CUADRATURA_TOTALES_2022_2026.json');assert previous['matriz']==matrix['matriz']
    cat=read(ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json');dest=Path(cat['carpeta_consolidada'])
    assert cat['archivos']==len(cat['catalogo']) and cat['bytes_total']==sum(r['bytes'] for r in cat['catalogo'])
    for name in ('CATALOGO_FUENTES.json','CATALOGO_FUENTES.csv','LEEME.md'):
        assert sha(ROOT/'data/catalogo_fuentes'/name)==sha(dest/name)
        assert '_DUPLICADO_PARA_BORRAR' not in (ROOT/'data/catalogo_fuentes'/name).read_text(encoding='utf-8-sig')
    assert not (dest/'_DUPLICADO_PARA_BORRAR').exists()
    cleanup=read(OUT/'LIMPIEZA_Y_CANDIDATAS_MRUN2026.json');assert cleanup['archivos_borrados']==0;assert len(cleanup['borrados_confirmados'])==1;assert not Path(cleanup['borrados_confirmados'][0]['ruta']).exists()
    for row in cleanup['carpetas_protegidas']:
        assert Path(row['ruta']).exists()
        assert row['bytes']==sum(p.stat().st_size for p in Path(row['ruta']).rglob('*') if p.is_file())
        if row['referencias_protectoras']:assert row not in cleanup['candidatas_no_protegidas']
    assert {r['id'] for r in cat['cierres_operativos_20261028']}=={'PROMEDIOS_2026','COPIA_MATRICULA_2007_2025_DISTINTA','27_ORIGEN_DESCONOCIDO'}
    assert read(ROOT/'data/catalogo_datos/QA.json')['desconocidos_revision_manual']==[]
    frozen=['data/diccionario_sies_seguimiento/activo.json','data/recuperacion_cruce_mrun_umas/20261016/manifest.json','docs/recuperacion_cruce_mrun_umas_20261016.md','scripts/diagnosticar_candidatos_mrun_umas.py','data/versiones_por_cohorte/20261016/grupos_existentes.json','data/versiones_por_cohorte/20261028/grupos_existentes.json']
    frozen+= [str(p.relative_to(ROOT)) for p in (ROOT/'data/diccionario_sies_seguimiento').glob('*/descriptor.json')]
    for name in frozen:assert hashlib.sha256(subprocess.check_output(['git','show',baseline_head+':'+name],cwd=ROOT)).hexdigest()==sha(ROOT/name)
    source=read(OUT/'FUENTE_MRUN2026_Y_LIMPIEZA.json');diag=read(OUT/'DIAGNOSTICO_BRECHA_MRUN2026.json')
    assert sha(source['fuente_h2']['fuente_h2'])==source['fuente_h2']['sha256_h2']=='510b7d03405398ed29196f750048dea1b07656ba722c1bf12cb3ab427098f0fd'
    assert source['mrun2026']=={'total':3425,'pregrado':3371,'postitulo':54}
    assert all(r['diferencia']==0 for r in source['paridad_por_codigo'])
    assert len({r['sha256'] for r in source['nacionales']})==1
    for r in source['nacionales']:assert Path(r['ruta']).stat().st_size==r['bytes']==1015950538
    for r in diag['fuentes']:assert sha(r['ruta'])==r['sha256']
    mr=Path(source['fuente_consolidada']['ruta_consolidada']);assert sha(mr)==source['fuente_consolidada']['sha256']
    base=Path(next(r['ruta_consolidada'] for r in cat['catalogo'] if r['sha256'].startswith('19cf33ae')))
    con=sqlite3.connect(':memory:');con.execute('CREATE TABLE mu(i INTEGER,y,ym,sx,fam,vig)');con.execute('CREATE TABLE mr(i INTEGER,y,ym,sx,fam,typ,expected,c)')
    gp=read(ROOT/'data/versiones_por_cohorte/20261028/grupos_existentes.json');types=collections.defaultdict(set);missing=set()
    for g in gp:
        for f in g['familias']:
            ts={txt(p[1]) for p in g.get('perfiles_duracion_tipo',[])};types[f].update(ts)
            if not ts:missing.add(f)
    names={'1':'PLAN REGULAR','2':'PLAN ESPECIAL','3':'PLAN REGULAR DE CONTINUIDAD'}
    expected={f:names[next(iter(ts))] for f,ts in types.items() if len(ts)==1 and f not in missing and next(iter(ts)) in names}
    def date_mu(x):
        try:
            d=datetime.datetime.strptime(txt(x),'%d/%m/%Y')
            return d.strftime('%Y%m') if d.year>1900 else None
        except ValueError:return None
    def date_mr(x):
        s=txt(x)
        if re.fullmatch(r'\d{6}',s) and 1900<int(s[:4])<=2026 and 1<=int(s[4:])<=12:return s
        return None
    secrets=set();w=openpyxl.load_workbook(base,read_only=True,data_only=True);it=w['BASE_RETENCION_MU'].iter_rows(values_only=True);h=next(it);n=0
    for row in it:
        r=dict(zip(h,row));doc=txt(r['N_DOC']);dv=txt(r['DV']);secrets.update((doc,doc+'-'+dv))
        if txt(r['ANIO_INFORMADO'])!='2026':continue
        fam='I162S{}C{}J{}'.format(*(txt(r[k]) for k in ('COD_SED','COD_CAR','JOR')));sx=txt(r['SEXO']);ym=date_mu(r['FECH_NAC']) if sx in ('H','M') else None
        con.execute('INSERT INTO mu VALUES(?,?,?,?,?,?)',(n,'2026',ym,sx,fam,txt(r['VIG'])));n+=1
    w.close();assert n==4105
    focus={r['codigo_sies'] for r in diag['por_codigo']}
    with mr.open(newline='') as f:rows=list(csv.DictReader(f))
    for i,r in enumerate(rows):
        secrets.add(txt(r['mrun']))
        c=txt(r['codigo_unico'])
        if c not in focus:continue
        fam=c.rsplit('V',1)[0];sx={'1':'H','2':'M'}.get(txt(r['gen_alu']))
        con.execute('INSERT INTO mr VALUES(?,?,?,?,?,?,?,?)',(i,'2026',date_mr(r['fec_nac_alu']),sx,fam,txt(r['tipo_plan_carr']),expected.get(fam),c))
    con.execute('CREATE INDEX mu_profile ON mu(y,ym,sx,fam)')
    for stage,condition in [('A_anio_nacimiento_sexo',''),('B_mas_familia_ISCJ',' AND mu.fam=mr.fam'),('C_mas_tipo_solo_unanime',' AND mu.fam=mr.fam AND (mr.expected IS NULL OR mr.expected=mr.typ)')]:
        result=con.execute('SELECT mr.c,COUNT(mu.i),MIN(mu.vig) FROM mr LEFT JOIN mu ON mu.y=mr.y AND mu.ym=mr.ym AND mu.sx=mr.sx'+condition+' GROUP BY mr.i').fetchall()
        counts=collections.defaultdict(collections.Counter)
        for c,n,vig in result:counts[c]['sin_candidato' if n==0 else 'varios_candidatos' if n>1 else 'vig'+vig+'_candidata_unica']+=1
        for r in diag['etapas'][stage]:
            for key in ('vig1_candidata_unica','vig0_candidata_unica','varios_candidatos','sin_candidato'):assert counts[r['codigo_sies']][key]==r[key],(stage,key)
    con.close()
    assert sum(diag['resumen'][k] for k in ('vig1_candidata_unica','vig0_candidata_unica','varios_candidatos','sin_candidato'))==2973
    assert diag['resumen']['brecha_neta']==226 and diag['resumen']['brecha_positiva']==228
    assert diag['resumen']['capacidad_descriptiva_positiva']+diag['resumen']['pendiente_positivo_sin_candidata_vig0']==228
    tests=subprocess.run([sys.executable,str(OUT/'test_metodo_mu2026.py')],capture_output=True,text=True)
    assert tests.returncode==0,tests.stderr
    assert diag['identidades_certificadas']==0 and not diag['vinculos_rut_mrun_persistidos']
    public=[ROOT/'data/catalogo_fuentes'/n for n in ('CATALOGO_FUENTES.json','CATALOGO_FUENTES.csv','LEEME.md')]+[ROOT/'data/catalogo_datos'/n for n in ('CATALOGO_DATOS_IPSS.json','CATALOGO_DATOS_IPSS.md','QA.json')]
    public += [p for p in OUT.iterdir() if p.suffix in ('.json','.md','.py')]
    # Complementar con CODCLI de la auditoría previa; nunca se imprimen tokens.
    private=read('/Users/alexi/.local/share/ipss/matriz_cuadratura_totales_20261028/DICTAMEN_LIBROS_MU2026_DETALLE.json')
    for r in private['abril']:secrets.update((r['documento'],r['documento'].split('-')[0],r['codcli']))
    sys.path.insert(0,str(ROOT));from common.diccionario_umas import patron_tokens_privados
    pattern=patron_tokens_privados({s for s in secrets if len(s)>=6})
    hits=sum(len(pattern.findall(p.read_text(encoding='utf-8-sig'))) for p in public)
    assert hits==0,'Posible identificador en salida; no publicar'
    q={'estado':'PASS_CON_PENDIENTES_E','head':head,'clases':'A oficial; B observado; C cálculo; D decisión; E pendiente','catalogos_repo_onedrive_identicos':True,'duplicado_ausente_y_canonico_verificado':True,'candidatas_borradas_por_ejecutora':0,'borrados_externos_confirmados':len(cleanup['borrados_confirmados']),'carpetas_protegidas':sum(bool(r['referencias_protectoras']) for r in cleanup['carpetas_protegidas']),'candidatas_para_confirmar':len(cleanup['candidatas_no_protegidas']),'cierres_D':3,'fuentes_h2_y_mu_por_hash':True,'nacionales_identicos_solo_referencia':True,'paridad_publicacion_por_codigo_diferencias':0,'MRUN2026':source['mrun2026'],'SQL_independiente_A_B_C':{'codigos':48,'registros':2973,'diferencias':0},'pruebas_sinteticas':{'cantidad':15,'resultado':'PASS'},'nucleo_matriz_igual_al_commit':True,'descriptores_y_activo_intactos':True,'bases_denominadores_tasas_intactos':True,'identidades_certificadas':0,'vinculos_rut_mrun_persistidos':False,'escaneo_identificadores':{'archivos':len(public),'coincidencias':hits,'alcance':'Documentos MU, CODCLI previos y MRUN leídos, por límites de token. Los datos individuales nunca se exportan en salidas.'},'limites':['Candidaturas por perfiles no son identidad ni prueba de aceptación de VIG0','Ambigüedades, reutilización de candidatos y sin candidato permanecen E','La incertidumbre de metadatos de los27 archivos se conserva aunque su revisión se cierre D'],'commit_push_ejecutados':False}
    write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
    write(OUT/'QA_LIMPIEZA_MRUN2026.json',q)
    mainqa=read(OUT/'QA.json');mainqa['diagnostico_mrun2026']=q
    mainqa['metodo_mu2026']={'estado_documental':'PREPARADO_NO_EJECUTADO_SIN_FUENTE_IDENTIFICADA','estado_adaptador_mrun':'DIAGNOSTICO_EJECUTADO_SIN_VINCULOS_PERSONALES','pruebas_sinteticas':{'cantidad':15,'resultado':'PASS'},'sha256':sha(OUT/'metodo_mu2026.py')}
    write(OUT/'QA.json',mainqa)
    manifest={'estado':'PREPARADO_SIN_COMMIT_PUSH','head':head,'ejecucion':'Limpieza de metadatos y diagnóstico MRUN autorizado; no reconstrucción PES','fuente_y_copia':source['fuente_consolidada'],'script_fuente':{'ruta':str(OUT/'preparar_fuente_mrun2026.py'),'sha256':sha(OUT/'preparar_fuente_mrun2026.py')},'script_diagnostico':{'ruta':str(OUT/'diagnosticar_brecha_mrun2026.py'),'sha256':sha(OUT/'diagnosticar_brecha_mrun2026.py')},'qa':{'ruta':str(OUT/'QA_LIMPIEZA_MRUN2026.json'),'sha256':sha(OUT/'QA_LIMPIEZA_MRUN2026.json')},'salidas_primarias':[{'ruta':str(OUT/n),'sha256':sha(OUT/n)} for n in ('FUENTE_MRUN2026_Y_LIMPIEZA.json','LIMPIEZA_Y_CANDIDATAS_MRUN2026.json','DIAGNOSTICO_BRECHA_MRUN2026.json','DIAGNOSTICO_BRECHA_MRUN2026.md','MATRIZ_CUADRATURA_TOTALES_2022_2026.json','MATRIZ_CUADRATURA_TOTALES_2022_2026.md')],'pendiente':'Respaldo autorizado por Alexi 2026-10-28; borrado externo de candidata31 documentado, sin otros borrados'}
    manifest['catalogos']=[{'ruta':str(ROOT/'data/catalogo_fuentes'/n),'ruta_onedrive':str(dest/n),'sha256':sha(ROOT/'data/catalogo_fuentes'/n)} for n in ('CATALOGO_FUENTES.json','CATALOGO_FUENTES.csv','LEEME.md')]
    write(OUT/'MANIFEST_LIMPIEZA_MRUN2026.json',manifest)
    # Escanear también los documentos recién generados, sin revelar coincidencias.
    for p in (OUT/'QA_LIMPIEZA_MRUN2026.json',OUT/'MANIFEST_LIMPIEZA_MRUN2026.json',OUT/'QA.json'):assert not pattern.search(p.read_text())
    assert subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True).returncode==0
    print(json.dumps({'qa':q['estado'],'sql_diferencias':0,'pruebas':15,'identificadores_detectados':0,'candidatas_para_confirmar':len(cleanup['candidatas_no_protegidas']),'sin_commit_push':True}))
if __name__=='__main__':main()

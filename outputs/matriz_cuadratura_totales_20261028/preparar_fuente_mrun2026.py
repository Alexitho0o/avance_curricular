"""Limpieza de metadatos y copia MRUN IPSS2026; nunca borra candidatas ni originales."""
import collections,csv,hashlib,importlib.util,json,os,subprocess,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/matriz_cuadratura_totales_20261028')
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=1 if Path(p).name=='CATALOGO_FUENTES.json' else 2)+'\n')
def norm(s):return unicodedata.normalize('NFC',str(s))
def main():
    assert subprocess.run(['git','merge-base','--is-ancestor','782efc8b4e37e60898cbea832667c887199bf536','HEAD'],cwd=ROOT,capture_output=True).returncode==0
    prior_cleanup=read(OUT/'LIMPIEZA_Y_CANDIDATAS_MRUN2026.json') if (OUT/'LIMPIEZA_Y_CANDIDATAS_MRUN2026.json').exists() else {}
    cp=ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json';cat=read(cp);dest=Path(cat['carpeta_consolidada'])
    duplicate=dest/'_DUPLICADO_PARA_BORRAR';assert not duplicate.exists(),'El duplicado aún existe; no se autoriza borrarlo aquí'
    canonical=next(r for r in cat['catalogo'] if r['sha256']=='57da408869681bdaa7eb18ee13ea482bad377ea9c58dc10afdb5ff34aeebbd09')
    assert sha(canonical['ruta_consolidada'])==canonical['sha256']
    refs=0
    # Quitar sólo referencias a la copia eliminada, nunca su fuente canónica.
    for r in cat['catalogo']:
        for key in ('otras_copias_conservadas','origenes'):
            if key in r:
                old=r[key];r[key]=[v for v in old if '_DUPLICADO_PARA_BORRAR' not in str(v)];refs+=len(old)-len(r[key])
    assert '_DUPLICADO_PARA_BORRAR' not in json.dumps(cat)
    decisions=[{'id':'PROMEDIOS_2026','estado':'CERRADO_D','responsable':'Alexi','fecha':'2026-10-28','decision':'12166 es la única extracción; se acepta su límite. Permanencia cubre la actividad 2026 según Alexi. No solicitar extracción sin tope.','alcance':'D; no certifica cobertura completa de 12166 ni recalcula indicadores.'},{'id':'COPIA_MATRICULA_2007_2025_DISTINTA','estado':'CERRADO_D','responsable':'Alexi','fecha':'2026-10-28','decision':'No continuar investigando la copia distinta; conservar no usar y no equivalente al canónico.'},{'id':'27_ORIGEN_DESCONOCIDO','estado':'CERRADO_D','responsable':'Alexi','fecha':'2026-10-28','decision':'Se retira la revisión manual de pendientes. Mantener la incertidumbre de metadatos y tratamiento restringido; no declarar ausencia de datos personales.'}]
    cat['cierres_operativos_20261028']=decisions
    cat['limpieza_duplicado_20261028']={'clase':'D Alexi; B/C verificación','eliminado_por':'cerebro, según Alexi','referencias_retiradas_en_esta_ejecucion':refs,'copia_canonica_sha256':canonical['sha256'],'copia_canonica_disponible':True,'nota':'La ruta de copia redundante ya no figura en el catálogo; no se borraron archivos en esta ejecución.'}
    for p in (cp,dest/'CATALOGO_FUENTES.json'):write(p,cat)
    # Inventario conservador: toda referencia en descriptores, catálogos o
    # scripts versionados protege el directorio, incluso de ediciones fallidas.
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    scripts=[ROOT/r for r in tracked if r and Path(r).suffix in ('.py','.sh','.js','.mjs','.ts')]
    descriptors=sorted((ROOT/'data/diccionario_sies_seguimiento').glob('*/descriptor.json'))
    documents=[ROOT/'data/diccionario_sies_seguimiento/activo.json',cp,ROOT/'data/catalogo_datos/CATALOGO_DATOS_IPSS.json',*descriptors,*scripts]
    texts=[(str(p.relative_to(ROOT)),norm(p.read_text(errors='replace'))) for p in documents if p.is_file()]
    folders=[p for p in PRIVATE.parent.iterdir() if p.is_dir() and any(k in p.name.lower() for k in ('candidat','fallid'))]
    folders += [p for p in (dest/'07_PRIVADAS_DICCIONARIO').iterdir() if p.is_dir()]
    inventory=[]
    for folder in folders:
        references=[label for label,content in texts if norm(str(folder)) in content or folder.name in content]
        size=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
        motive='Nombre de candidata o respaldo privado; no equivale a fallida prescindible.'
        if folder.name=='v10_candidata_31_20261026':
            evidence=ROOT/'outputs/v11_fase1_cobertura_20261026/LEEME.md'
            assert 'la propuesta de 31 está reemplazada' in evidence.read_text()
            motive='Propuesta de 31 reemplazada por las 27 vigentes de v10; evidencia: outputs/v11_fase1_cobertura_20261026/LEEME.md. Sin referencia protectora localizada; requiere confirmación del cerebro antes de borrar.'
        inventory.append({'ruta':str(folder),'bytes':size,'motivo':motive,'estado':'PROTEGIDA_REFERENCIADA' if references else 'REQUIERE_CONFIRMAR_FALLIDA_Y_CEREBRO','referencias_protectoras':references})
    eligible=[r for r in inventory if not r['referencias_protectoras']]
    cleanup={'clase':'B/C inventario; D exclusiones; E elegibilidad para borrar','carpeta_duplicada_eliminada_por_tercero':str(duplicate),'hash_canonico':canonical['sha256'],'referencias_ya_ausentes':refs==0,'candidatas_no_protegidas':eligible,'carpetas_protegidas':inventory,'criterio':'Ruta o nombre de carpeta citado en activo, descriptores, catálogo o script versionado excluye el borrado; protección deliberadamente conservadora. No se ha borrado ninguna candidata.','archivos_borrados':0,'cierres_pendientes':decisions}
    cleanup['borrados_confirmados']=prior_cleanup.get('borrados_confirmados',[])
    write(OUT/'LIMPIEZA_Y_CANDIDATAS_MRUN2026.json',cleanup)
    lines=['# Limpieza y candidatas · 28-10-2026','','D, Alexi: la copia redundante fue eliminada por el cerebro. B/C: carpeta ausente, copia canónica disponible y hash verificado. No había referencias a retirar en los catálogos revisados; se registra el cierre.','','## Candidatas sin referencia protectora — no borrar sin confirmar','','| Ruta | Bytes lógicos | Motivo |','|---|---:|---|']
    for r in eligible:lines.append(f"| {r['ruta']} | {r['bytes']} | {r['motivo']} |")
    if not eligible:lines.append('| Ninguna | 0 | Todas tienen referencia protectora |')
    lines+=['',f'{len(inventory)} carpetas inventariadas; referencias protectoras y tamaños completos en el JSON. No se identifica como fallida borrable una carpeta por llevar candidata en el nombre. Cero borrados.','','## Pendientes retirados por decisión D','']+[f"- {d['id']}: {d['decision']}" for d in decisions]
    for event in cleanup['borrados_confirmados']:
        lines+=['','## Borrado externo confirmado [D/B/C]','',event['ruta']+': '+event['motivo']+' Responsable: '+event['responsable_borrado']+'. Esta ejecución no borra archivos.']
    (OUT/'LIMPIEZA_Y_CANDIDATAS_MRUN2026.md').write_text('\n'.join(lines)+'\n')
    dp=ROOT/'data/catalogo_datos/CATALOGO_DATOS_IPSS.json';datos=read(dp);datos['cierres_operativos_20261028']=decisions
    for x in datos.get('copias_fuera_0_bases_de_datos',[]):
        if 'contenido distinto' in x.get('relacion',''):x['seguimiento_estado']='CERRADO_D_20261028; no usar, no equivalente'
    write(dp,datos)
    qp=ROOT/'data/catalogo_datos/QA.json';q=read(qp)
    q['desconocidos_revision_manual_cerrada_D']=q.get('desconocidos_revision_manual_cerrada_D',q.get('desconocidos_revision_manual',[]))
    q['desconocidos_revision_manual']=[];q['cierre_revision_desconocidos']='D Alexi 28-10-2026; incertidumbre conservada, fuera de pendientes; tratamiento restringido'
    write(qp,q)
    dm=ROOT/'data/catalogo_datos/CATALOGO_DATOS_IPSS.md';s=dm.read_text().split('\n## Cierres operativos D · 28-10-2026')[0]
    dm.write_text(s+'\n## Cierres operativos D · 28-10-2026\n\nSe retiran de tareas pendientes la extracción PROMEDIOS sin tope, la investigación de la copia distinta de matrícula 2007–2025 y la revisión de los 27 archivos de origen desconocido. Se conservan los metadatos observados, no usar para la copia distinta y tratamiento restringido para los desconocidos. No se certifica cobertura completa ni ausencia de datos personales.\n')
    # Fuente H2 ya existente: sólo derivar su subconjunto 2026, sin reconstruir H2.
    mh=read(ROOT/'data/recuperacion_cruce_mrun_umas/20261016/manifest.json')
    h2=Path(next(p for p in mh['fuentes_sha256'] if 'reporte_matricula' in p));assert sha(h2)==mh['fuentes_sha256'][str(h2)]
    with h2.open(newline='') as f:
        rd=csv.DictReader(f);header=rd.fieldnames;historical=list(rd)
    assert len(historical)==24386
    rows=[r for r in historical if r['cat_periodo']=='2026' and r['cod_inst']=='162']
    assert len(rows)==3425
    counts=collections.Counter(r['nivel_global'] for r in rows);assert counts=={'Pregrado':3371,'Postítulo':54}
    extraction=PRIVATE/'MRUN_MATRICULA_IPSS_162_2026_H2.csv'
    import io
    buf=io.StringIO(newline='');wr=csv.DictWriter(buf,fieldnames=header);wr.writeheader();wr.writerows(rows);data=buf.getvalue().encode('utf-8')
    if extraction.exists():assert extraction.read_bytes()==data,'Derivado previo distinto; no sobrescribir'
    else:
        with extraction.open('xb') as f:f.write(data)
        extraction.chmod(0o600)
    publication=ROOT/'outputs/trazabilidad_integral_umas_sies_20261025/fase2/conciliacion/DETALLE_CONCILIACION.csv'
    with publication.open(encoding='utf-8-sig',newline='') as f:agg=[r for r in csv.DictReader(f,delimiter=';') if r['ANIO']=='2026']
    reported={r['CODIGO_COMPLETO']:int(r['CSV_TOTAL_ESTRUCTURAL_UNION']) for r in agg}
    observed=collections.Counter(r['codigo_unico'] for r in rows)
    parity=[{'codigo_sies':c,'mrun':observed[c],'publicado':reported.get(c,0),'diferencia':observed[c]-reported.get(c,0)} for c in sorted(set(observed)|set(reported))]
    assert all(r['diferencia']==0 for r in parity),'MRUN no concilia por código con publicación'
    nationals=read(PRIVATE/'NACIONALES_MRUN2026_METADATOS.json');assert len(nationals)==2 and len({r['sha256'] for r in nationals})==1
    references=list(cat['referencias_nacionales_sin_copia'])
    for item in nationals:
        if not any(norm(x['ruta'])==norm(item['ruta']) for x in references):references.append({**item,'accion':'SOLO_REFERENCIA_SIN_COPIA','clase':'B/C hash nacional verificado'})
    plan={'copias':[{'origen':str(extraction),'categoria':'11_SIES_MRUN_IPSS_162','sha256':sha(extraction),'datos_personales':'sí; MRUN seudonimizado, sin RUT/CODCLI','descripcion':'Subconjunto IPSS2026 de H2, 3.425 matrículas. No contiene vínculos con identificadores UMAS.'}],'referencias_nacionales_sin_copia':references}
    write(OUT/'PLAN_CONSOLIDACION_MRUN2026.json',plan)
    consol=ROOT/'outputs/consolidacion_bases_onedrive_20261026/consolidar_bases.py'
    subprocess.run(['python3',str(consol),'--plan',str(OUT/'PLAN_CONSOLIDACION_MRUN2026.json')],check=True,cwd=ROOT)
    cat=read(cp);entry=next(r for r in cat['catalogo'] if r['sha256']==sha(extraction))
    entry['procedencia_primaria']={'fuente_h2':str(h2),'sha256_h2':sha(h2),'fuente_nacional_2026':nationals[0],'regla_filtro':'cat_periodo=2026 y cod_inst=162','manifest_h2':'data/recuperacion_cruce_mrun_umas/20261016/manifest.json'}
    for p in (cp,dest/'CATALOGO_FUENTES.json'):write(p,cat)
    lp=ROOT/'data/catalogo_fuentes/LEEME.md';s=lp.read_text().split('\n## Limpieza y MRUN 2026 · 28-10-2026')[0]
    s=s.replace('Extracción matrícula IPSS 2007–2025 y consolidado titulados IPSS 2007–2025','Extracción matrícula IPSS 2007–2025, subconjunto MRUN matrícula IPSS 2026 y consolidado titulados IPSS 2007–2025')
    s+='\n## Limpieza y MRUN 2026 · 28-10-2026\n\nD, Alexi: copia redundante eliminada por el cerebro; catálogo sin su ruta y canónico DATOSDEALUMNOS_1758 conservado (SHA-256 57da4088…). Ninguna candidata borrada. Se cierran los tres pendientes operativos descritos en LIMPIEZA_Y_CANDIDATAS_MRUN2026.json.\n\nLa carpeta 11 incorpora MRUN_MATRICULA_IPSS_162_2026_H2.csv: 3.425 matrículas (3.371 pregrado + 54 postítulo), extraídas del H2 de 24.386 filas con hash 510b7d03…. Contiene MRUN seudonimizado; uso restringido, sin vínculo RUT–MRUN. Los dos nacionales de 1.015.950.538 bytes son idénticos por SHA-256 y sólo se referencian; no se copian.\n'
    for p in (lp,dest/'LEEME.md'):p.write_text(s)
    result={'clase':'B fuente observada; C extracción/paridad; D cierre de pendientes','fuente_h2':entry['procedencia_primaria'],'filas_h2':24386,'fuente_consolidada':entry,'mrun2026':{'total':3425,'pregrado':3371,'postitulo':54},'paridad_por_codigo':parity,'diferencias_por_codigo':0,'nacionales':nationals,'copias_nacionales_identicas':True,'archivos_nacionales_copiados':0,'catalogos_json_csv_leeme_identicos':all(sha(ROOT/'data/catalogo_fuentes'/n)==sha(dest/n) for n in ('CATALOGO_FUENTES.json','CATALOGO_FUENTES.csv','LEEME.md')),'originales_modificados':False,'vinculos_rut_mrun_persistidos':False}
    assert result['catalogos_json_csv_leeme_identicos']
    write(OUT/'FUENTE_MRUN2026_Y_LIMPIEZA.json',result)
    print(json.dumps({'h2':24386,'mrun2026':counts,'paridad_codigos':0,'candidatas_no_protegidas':len(eligible),'catalogos_identicos':True},ensure_ascii=False))
if __name__=='__main__':main()

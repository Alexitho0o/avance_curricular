"""QA agregado de consolidación, mapa y matriz; no escribe identificadores."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
current=read(OUT/'MATRIZ_CUADRATURA_TOTALES_2022_2026.json')
prior=json.loads(subprocess.check_output(['git','show','80e2385:outputs/matriz_cuadratura_totales_20261028/MATRIZ_CUADRATURA_TOTALES_2022_2026.json'],cwd=ROOT,text=True))
changes=[]
for old,new in zip(prior['matriz'],current['matriz']):
    assert old['anio']==new['anio']
    assert old['mu_sies']==new['mu_sies']
    assert old['retencion_mu']==new['retencion_mu']
    assert old['datos_alumnos_mu']==new['datos_alumnos_mu']
    changes.append({'anio':new['anio'],'familia_sin_mapeo_antes':old['cobertura_familia'].get('familia_sin_mapeo',0),'familia_sin_mapeo_despues':new['cobertura_familia'].get('familia_sin_mapeo',0),'rut_dv_carrera_antes':old['cobertura_familia'].get('rut_dv_y_carrera',0),'rut_dv_carrera_despues':new['cobertura_familia'].get('rut_dv_y_carrera',0)})
oldgroups=read(ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json');newgroups=read(ROOT/'data/versiones_por_cohorte/20261028/grupos_existentes.json')
assert oldgroups==newgroups[:len(oldgroups)] and len(newgroups)==len(oldgroups)+3
assert {x['familias'][0] for x in newgroups[len(oldgroups):]}=={'I162S3C114J2','I162S3C115J2','I162S3C91J2'}
cat=read(ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json'); dest=Path(cat['carpeta_consolidada']);plan=read(OUT/'PLAN_CONSOLIDACION.json')
copias=[]
for r in plan['copias']:
    d=dest/r['categoria']/Path(r['origen']).name
    assert sha(d)==sha(r['origen'])==r['sha256']
    copias.append({'archivo':d.name,'categoria':r['categoria'],'origen':r['origen'],'destino':str(d),'sha256':r['sha256'],'datos_personales':r['datos_personales']})
for name in ('CATALOGO_FUENTES.json','CATALOGO_FUENTES.csv','LEEME.md'):assert sha(ROOT/'data/catalogo_fuentes'/name)==sha(dest/name)
assert len(cat['catalogo'])==cat['archivos'];assert sum(x['bytes'] for x in cat['catalogo'])==cat['bytes_total']
assert all(r['sha256'] for r in cat['referencias_nacionales_sin_copia'])
pespath=Path(current['fuentes']['pes5319']['ruta']);periodos={};ids=set()
with pespath.open(encoding='latin1',newline='') as f:
    for r in csv.DictReader(f,delimiter=';'):
        p=r['PERIODO_ACAD_TITULACION'];periodos[p]=periodos.get(p,0)+1
        ids.update((r['NUM_DOCUMENTO'],r['NUM_DOCUMENTO']+'-'+r['DV']))
for r in current['contraste_pes5319']:
    assert periodos[str(r['periodo_acad_titulacion'])]==r['pes5319_registros']==r['publicado_registros']
    assert all(x['diferencia']==0 for x in r['pes_publicado_por_codigo'])
for group in ('data/diccionario_sies_seguimiento/activo.json','data/versiones_por_cohorte/20261016/grupos_existentes.json','common/analisis_desercion/h001.py'):
    baseline=subprocess.check_output(['git','show','80e2385:'+group],cwd=ROOT)
    assert hashlib.sha256(baseline).hexdigest()==sha(ROOT/group)
diff={'referencia':'80e2385','clasificacion':'B/C cambios de cobertura; D ampliación de tres familias; E excepciones','cambios':changes,'fuentes_denominadores_tasas_y_diccionario_conservados':True,'pes5319_frente_publicacion':[{'proceso':r['proceso'],'registros':r['pes5319_registros'],'estado':r['estado_pes_publicacion']} for r in current['contraste_pes5319']]}
(OUT/'DIFF_AGREGADO.json').write_text(json.dumps(diff,ensure_ascii=False,indent=2)+'\n')
lines=['# Copias consolidadas verificadas · 28-10-2026','','| Carpeta | Archivo | SHA-256 | Datos personales |','|---|---|---|---|']
for r in copias:lines.append(f"| {r['categoria']} | {r['archivo']} | {r['sha256']} | {r['datos_personales']} |")
lines+=['','Orígenes y destinos completos: PLAN_CONSOLIDACION.json y CATALOGO_FUENTES.json. Nacionales: sólo referencia, sin copia.']
(OUT/'LISTA_COPIAS.md').write_text('\n'.join(lines)+'\n')
qa=read(OUT/'QA.json');qa.update({'copias_verificadas_contra_origen':len(copias),'catalogos_json_csv_y_leeme_identicos':True,'mapa_anterior_132_grupos_intacto':True,'mapa_nuevo_solo_3_adiciones':True,'cuadratura_pes5319_publicacion_por_codigo':True,'controles_mu_h001_diccionario_v20_sin_cambios':True,'brecha_226_no_investigada':True,'nacionales_solo_referencia':len(cat['referencias_nacionales_sin_copia'])})
# Complementa el escaneo del constructor con los documentos del reporte PES.
pattern=re.compile(r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(x) for x in sorted(ids,key=len,reverse=True) if len(x)>=6)+r')(?![A-Za-z0-9])')
files=list(OUT.glob('*.json'))+list(OUT.glob('*.md'))+list(OUT.glob('*.py'))
hits=sum(len(pattern.findall(p.read_text())) for p in files)
assert hits==0,'Posible documento PES en salida publicable'
qa['escaneo_documentos_pes5319_en_salidas']={'archivos':len(files),'coincidencias':hits}
(OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'qa':'PASS_CON_PENDIENTES_FUNCIONALES','copias':len(copias),'diff':changes,'escaneo_pes':hits},ensure_ascii=False))

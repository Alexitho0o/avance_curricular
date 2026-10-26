import json,re,hashlib,unicodedata
from pathlib import Path
import openpyxl
T=Path('/tmp/ipss_embudo_2317_20261022');prior=json.load(open('/tmp/ipss_revision_63_20261022/payload.json'));u=next(s['rows'] for s in prior if s['name']=='CONTRASTE_63');states={'CONTRADICCION_O_ATRIBUCION_MULTIPLE','SIN_EVIDENCIA_ANUAL_APLICABLE','CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO','DIFIERE_CODIGO_PROPUESTO_OBSERVADO'};focus={r[0] for r in u if r[10] in states};inv=json.load(open('data/cierre_d2/20261016/busqueda_fuentes.json'));ps=[r['path'] for r in inv['candidatos'] if '/2025/SIES/AVANCE CURRICULAR/' in r['path'] and '/borrar/' not in r['path']];new=json.load(open(T/'evidencias_nuevas.json'));cov=json.load(open(T/'cobertura.json'));hs=json.load(open(T/'hashes.json'))
def v(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def n(x):return unicodedata.normalize('NFKD',v(x)).encode('ascii','ignore').decode().upper()
for p in ps:
 try:
  hs[p]=hashlib.sha256(Path(p).read_bytes()).hexdigest();w=openpyxl.load_workbook(p,read_only=True,data_only=True)
  for s in w:
   h=None;total=matches=0
   for rn,row in enumerate(s.values,1):
    if h is None:
     hh=[n(x) for x in row]
     if any(z in hh for z in ['NUM_DOCUMENTO','N_DOC','RUN']):h=hh
     if rn>=15 and h is None:break
     continue
    total+=1;d=dict(zip(h,row));a=v(d.get('NUM_DOCUMENTO',d.get('N_DOC',d.get('RUN')))).replace('.','');b=v(d.get('DV')).upper()
    if not a.isdigit() or not re.fullmatch('[0-9K]',b):continue
    k=str(int(a))+'-'+b
    if k not in focus:continue
    matches+=1;code=v(d.get('CODIGO_UNICO',d.get('MATRICULA_CODIGO_UNICO'))).upper()
    new.append([k,'AVANCE','2025',code,'COMPLETO' if re.fullmatch(r'I\d+S\d+C\d+J\d+V\d+',code) else 'INCOMPLETO','CODIGO_UNICO',v(d.get('PLAN_ESTUDIOS')),'','',p,s.title,rn,'Carpeta2025/nombre2024: año académico no acreditado','ARCHIVO_SUBIR_U_ORIGINAL; no comprobante aceptación',a,b])
   cov.append([p,s.title,total,matches,matches,'LEIDO' if h else 'SIN_LLAVE_RECONOCIDA','Año2024/2025 no resuelto por nombre'])
  w.close()
 except Exception as e:cov.append([p,'',0,0,0,'INACCESIBLE',type(e).__name__])
(T/'evidencias_nuevas.json').write_text(json.dumps(new,ensure_ascii=False));(T/'cobertura.json').write_text(json.dumps(cov,ensure_ascii=False));(T/'hashes.json').write_text(json.dumps(hs,ensure_ascii=False));print({'archivos_dirigidos_adicionales':len(ps),'evidencias_totales_nuevas':len(new)})

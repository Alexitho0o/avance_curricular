import json,csv,re
from pathlib import Path
T=Path('/tmp/ipss_embudo_2317_20261022');old=json.load(open('/tmp/ipss_revision_63_20261022/payload.json'));u=next(s['rows'] for s in old if s['name']=='CONTRASTE_63');focus={r[0] for r in u if r[10] in ['CONTRADICCION_O_ATRIBUCION_MULTIPLE','SIN_EVIDENCIA_ANUAL_APLICABLE','CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO','DIFIERE_CODIGO_PROPUESTO_OBSERVADO']};paths=json.load(open(T/'hashes.json'));p=next(p for p in paths if Path(p).name=='Titulación Unificada 2026.csv');schemas=json.load(open('/tmp/ipss_revision_privada_20261022/schemas_v2.json'));h=next(r['headers'] for r in schemas if Path(r['path']).name.startswith('TIT_2022_162_def'));rows=list(csv.reader(open(p,encoding='utf-8-sig'),delimiter=';'));assert all(len(r)==len(h)==23 for r in rows)
# Mismo orden de 23 campos que CSV titulación con encabezado; XLSX2026 agrega CARRERA/JORNADA y columna vacía.
new=json.load(open(T/'evidencias_nuevas.json'));n=0
for rn,r in enumerate(rows,1):
 d=dict(zip(h,r));body=d['NUM_DOCUMENTO'].replace('.','').strip();dv=d['DV'].strip().upper()
 if not body.isdigit() or not re.fullmatch('[0-9K]',dv):continue
 k=str(int(body))+'-'+dv
 if k not in focus:continue
 for field in ['COD_SIES_OBT_TIT','COD_SIES_TERMINAL']:
  code=d[field].strip().upper()
  if not code:continue
  new.append([k,'TITULADOS','2026',code,'COMPLETO' if re.fullmatch(r'I\d+S\d+C\d+J\d+V\d+',code) else 'INCOMPLETO',field,'','','',p,'CSV',rn,'PROCESO_2026; no año de matrícula','CSV_SIN_ENCABEZADO_ESQUEMA23_TIT2022; cotejo XLSX2026 parcial 397/431',d['NUM_DOCUMENTO'],d['DV']]);n+=1
(T/'evidencias_nuevas.json').write_text(json.dumps(new,ensure_ascii=False));cov=json.load(open(T/'cobertura.json'));cov.append([p,'CSV_ESQUEMA23_TIT2022',len(rows),len({r[0] for r in new if r[9]==p}),n,'INCORPORADO_ESQUEMA_EXPLICITO;397/431 cotejo mismo código XLSX','Sin asumir aceptación ni identidad de variantes']);(T/'cobertura.json').write_text(json.dumps(cov,ensure_ascii=False));print({'evidencias_csv_titulados_foco':n})

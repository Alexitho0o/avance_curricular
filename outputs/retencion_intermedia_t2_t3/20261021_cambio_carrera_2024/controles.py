exec(compile((__import__('pathlib').Path(__file__).parent/'revisar.py').read_text(),'revisar.py','exec'))
ix24=defaultdict(list)
for r in mu:
 if r['ANIO_INFORMADO']==2024:ix24[key(r['N_DOC'],r['DV'])].append(r)
rows=[]
for term,ks in subsets.items():
 cnt=Counter();detail=Counter()
 for k in ks:
  ss=[r for r in ui[k] if text(r['ANOINGRESO'])=='2024' and text(r['PERIODOINGRESO'])==str(term)]
  dr=[r for r in ix25[k] if text(r['ANIO_ING_ORI'])=='2025']
  mapped=set().union(*(cc.get(text(r['CODCARPR']),set()) for r in ss));dest={text(r['COD_CAR']) for r in dr}
  same=(mapped==dest)
  year=' / '.join(sorted({str(r['FECHA_MATRICULA'].year) if hasattr(r['FECHA_MATRICULA'],'year') else text(r['FECHA_MATRICULA'])[:4] for r in dr}))
  detail[('MISMA_CARRERA' if same else 'CARRERA_DISTINTA',year)]+=1
  old=ix24[k]
  if not old:cnt['no_aparece_MU2024']+=1
  else:
   prev_codes={text(r['COD_CAR']) for r in old};cnt['aparece_MU2024']+=1
   cnt['codigos_MU2024_MU2025_iguales' if prev_codes==dest else 'codigos_MU2024_MU2025_distintos']+=1
   cnt['origen2024_en_MU2024' if any(text(r['ANIO_ING_ORI'])=='2024' for r in old) else 'otro_origen_MU2024']+=1
 rows.append({'periodo':term,'controles_MU2024':dict(cnt),'fecha_matricula_RAW2025_por_carrera':[{'carrera':a,'anio_fecha_matricula':b,'personas':n}for(a,b),n in detail.items()]})
(P/'CONTROLES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('CONTROLES',json.dumps(rows,ensure_ascii=False))

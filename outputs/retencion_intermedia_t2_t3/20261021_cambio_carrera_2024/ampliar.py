exec(compile((__import__('pathlib').Path(__file__).parent/'revisar.py').read_text(),'revisar.py','exec'))
allresults=[]
namebycar=defaultdict(set)
for r in cat:namebycar[r['CODIGO_CARRERA']].add(r['NOMBRE_CARRERA'])
for term,ks in subsets.items():
 stats=defaultdict(Counter);transitions=[]
 for k in sorted(ks):
  ss=[r for r in ui[k] if text(r['ANOINGRESO'])=='2024' and text(r['PERIODOINGRESO'])==str(term)]
  dr=[r for r in ix25[k] if text(r['ANIO_ING_ORI'])=='2025']
  mapped=set().union(*(cc.get(text(r['CODCARPR']),set()) for r in ss));dest={text(r['COD_CAR']) for r in dr}
  result='MISMA_CARRERA' if mapped==dest else 'CARRERA_DISTINTA'
  stats['clasificacion'][result]+=1
  for f in ['NIVEL_1','NIVEL_2','CONTINUIDAD','COD_NIV_GLO','FECH_CAR','FECHA_MATRICULA','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','FOR_ING_ACT','VIGENCIA']:
   stats[f][' / '.join(sorted({text(r.get(f)) for r in dr}))]+=1
  stats['filas_persona_MU'][str(len(ix25[k]))]+=1
  if result=='CARRERA_DISTINTA':
   target_rows=[r for r in ui[k] if cc.get(text(r['CODCARPR']),set())&dest]
   new2025=[r for r in target_rows if text(r['ANOINGRESO'])=='2025']
   transitions.append({'periodo_2024':term,'carrera_UMAS_2024':' / '.join(sorted({text(r['NOMBRE_L']) for r in ss})),'codigo_origen':' / '.join(sorted(mapped)),'carrera_MU2025':' / '.join(sorted(set().union(*(namebycar[c] for c in dest)))),'codigo_destino':' / '.join(sorted(dest)),'hay_carrera_destino_en_UMAS':bool(target_rows),'hay_carrera_destino_ingreso2025_en_UMAS':bool(new2025),'estados_situaciones_origen':sorted({text(r['ESTADOACADEMICO'])+' / '+text(r['SITUACION']) for r in ss}),'ingresos_carrera_destino_UMAS':sorted({text(r['ANOINGRESO'])+':'+text(r['PERIODOINGRESO']) for r in target_rows}),'FOR_ING_ACT_MU2025':sorted({text(r['FOR_ING_ACT']) for r in dr})})
  oldrows=[r for r in older if key(r['RUT'])==k and text(r['ANOINGRESO'])=='2024' and text(r['PERIODOINGRESO'])==str(term)]
  stats['respaldo10246_origen2024']['con_mismo_CODCARPR' if {text(r['CODCARPR']) for r in ss}=={text(r['CODCARPR']) for r in oldrows} else 'difiere_o_no_hay']+=1
 allresults.append({'periodo':term,'estadisticas':{a:dict(b) for a,b in stats.items()},'transiciones_carrera':transitions})
(P/'AMPLIACION.json').write_text(json.dumps(allresults,ensure_ascii=False,indent=2)+'\n')
print('AMPLIACION',json.dumps(allresults,ensure_ascii=False))

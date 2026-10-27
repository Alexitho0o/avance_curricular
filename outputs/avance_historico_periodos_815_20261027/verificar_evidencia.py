"""Se ejecuta dentro de revisar_periodos.py; relee filas MU, no exporta personas."""
import openpyxl
expected_hash=json.loads((ROOT/'outputs/reproduccion_puente_20261023_004044/FUENTES_HASHES_FINAL.json').read_text())
expected_hash.update(service.descriptor['entradas_sha256'])
source_audit={}; readrows={}
def scalar(x):
 return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def identity(a,b):
 a=scalar(a).replace('.','').replace(' ','');b=scalar(b).upper().strip()
 return str(int(a))+'-'+b if a.isdigit() and re.fullmatch('[0-9K]',b) else None
for source,wanted in source_refs.items():
 p=Path(source);actual=sha(p);exp=expected_hash.get(source)
 ck('Hash evidencia MU '+p.name,exp,actual)
 if exp!=actual:raise ValueError('Fuente MU sin hash concordante')
 wb=openpyxl.load_workbook(p,read_only=True,data_only=True);nread=0
 for sh in {x[0] for x in wanted}:
  ids={int(row) for sheet,row in wanted if sheet==sh};it=iter(wb[sh].values);heads=next(it)
  for rn,vals in enumerate(it,2):
   if rn not in ids:continue
   d=dict(zip(heads,vals));nread+=1
   if sh=='BASE_RETENCION_MU':
    pe=identity(d['N_DOC'],d['DV']);year=scalar(d['ANIO_INFORMADO']);code='I162S%sC%sJ%sV%s'%tuple(scalar(d[k]) for k in ['COD_SED','COD_CAR','JOR','VERSION'])
   else:
    pe=identity(d['MM_N_DOCUMENTO'],d['MM_DV']);year=scalar(d['MC_CAT_PERIODO']).removeprefix('MAT_');code=scalar(d['MC_CODIGO_UNICO'])
   readrows[(source,sh,rn)]=(pe,year,code)
 wb.close();ck('Referencias leidas '+p.name,len(wanted),nread)
 source_audit[source]={'sha256':actual,'referencias_verificadas':nread}
# Fotografía de actividad completa: no ignorar otros planes/jornadas del mismo expediente/año.
raw_contexts=defaultdict(set)
for ctx,grp in h.groupby(['_BODY','_DV','CODCLI','_ANO_NUM'],dropna=False):
 a,b,cli,year=ctx
 if not a.isdigit() or not re.fullmatch('[0-9K]',b) or str(year)=='nan':continue
 raw_contexts[(str(int(a))+'-'+b,clean(cli),str(int(year)))].update((clean(x),clean(y),clean(z)) for x,y,z in zip(grp['PLAN_DE_ESTUDIO'],grp['CODCARR'],grp['JORNADA']))
full_stats=Counter();periods=Counter();anchor_periods=Counter();strong_codes=Counter();strong_years=Counter();strong_people=set();strong_exp=set();reflinks=0;mismatch=0;strong_keys=set();annual_units=Counter();refchecked=set()
for c in candidates:
 pe,cli,pl,ca,jo,an,period=c['key'];periods[period]+=1
 verified=True
 for e in c['mu']:
  ref=(e['fuente'],e['hoja'],int(e['fila']));refchecked.add(ref);reflinks+=1
  ok=readrows.get(ref)==(pe,an,e['codigo']);mismatch+=not ok;verified&=ok
 if c['state']!='CANDIDATO_MISMO_ANIO_PLAN_CARRERA_JORNADA_Y_MU':continue
 anchor_periods[','.join(sorted({str(x['periodo']) for x in c['exact']}))]+=1
 rawalts=raw_contexts[(pe,cli,an)]-{(pl,ca,jo)}
 if not verified:final='DIFERENCIA_INDICE_FUENTE'
 elif rawalts:final='COINCIDENCIA_CON_OTRO_PLAN_CARRERA_O_JORNADA_EN_PROMEDIOS_ANUAL'
 else:final='CANDIDATO_CONCORDANTE_SIN_ALTERNATIVA_RAW_ANUAL'
 full_stats[final]+=1
 if final=='CANDIDATO_CONCORDANTE_SIN_ALTERNATIVA_RAW_ANUAL':
  strong_keys.add(c['key']);strong_codes[c['codes'][0]]+=1;strong_years[an]+=1;strong_people.add(pe);strong_exp.add((pe,cli,ca))
  annual_units['filas_actividad_contextos_unicos']+=c['activity']['activity_rows'];annual_units['filas_A_R_2025_contextos_unicos']+=c['activity']['annual2025']
ck('Enlaces indice contra filas MU',0,mismatch);ck('Particion 644 candidatos',644,sum(full_stats.values()))
# Perfil descriptivo, sin aplicar regla nueva ni modificar el diccionario.
result2={'clase':'B/C/E','foco':815,'candidatos_iniciales':644,'verificacion_candidatos':dict(full_stats),'periodos_UMAS_observados_sin_conversion':dict(periods),'periodos_ancla_del_mismo_anio':dict(anchor_periods),'enlaces_fuente_revisados':reflinks,'filas_fuente_distintas':len(refchecked),'discrepancias_indice_fuente':mismatch,'candidatos_concordantes':len(strong_keys),'personas_candidatos':len(strong_people),'expedientes_candidatos':len(strong_exp),'por_codigo_candidato':dict(strong_codes),'por_anio_candidato':dict(strong_years),'actividad_candidata':dict(annual_units),'fuentes_mu':source_audit,'asignaciones_aplicadas':0,'pendiente_decision':'La extensión a períodos no indexados del mismo año se conserva como propuesta C/E. No acredita fecha efectiva del plan, número PLAN_ESTUDIOS SIES ni envío/aceptación.','fuentes_inalteradas':True}
for source,meta in source_audit.items():ck('Preservacion evidencia MU '+Path(source).name,meta['sha256'],sha(Path(source)))
dump('VERIFICACION_FUENTES_Y_CONTEXTO.json',result2)
with (OUT/'CANDIDATOS_POR_CODIGO.csv').open('w',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['CODIGO_SIES','CONTEXTOS_CANDIDATOS','CLASIFICACION','ESTADO']);w.writerows((k,v,'C/E','NO_APLICADO') for k,v in sorted(strong_codes.items()))
print(json.dumps(result2,ensure_ascii=False,indent=2),flush=True)

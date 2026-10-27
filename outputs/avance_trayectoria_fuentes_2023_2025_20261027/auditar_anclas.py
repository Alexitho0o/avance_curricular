from pathlib import Path
import collections,re,json,hashlib,openpyxl,csv
root=Path('/Users/alexi/Documents/GitHub/avance_curricular');p=root/'outputs/avance_trayectoria_plan_fase2_20261027/reconstruir_107.py';n={};exec(compile(p.read_text().split('out=collections.Counter(); examples=[]')[0],str(p),'exec'),n)
cs=[c for c in n['candidates'] if any(x['plan']==c['key'][2] and x['carrera']==c['key'][3] and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==c['mu_codes'][0] for x in n['n']['byexp'][(c['key'][0],c['key'][1])])];assert len(cs)==89
inv=json.loads((root/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/INVENTARIO_FUENTES_SHA256.json').read_text());selected={str(x['anio']):x for x in inv if x['anio'] in [2023,2024,2025]}
def val(x):
 if x is None:return ''
 if isinstance(x,float) and x.is_integer():return str(int(x))
 return str(x).strip().upper()
def norm(x):return re.sub(r'[^0-9K]','',val(x))
raw={};meta=[];confianza=collections.Counter(); cases=collections.Counter()
for year,e in selected.items():
 p=Path(e['archivo']);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==e['sha256'];idx=collections.defaultdict(list)
 if year=='2025':
  w=openpyxl.load_workbook(p,read_only=True,data_only=True);sh=w['08-05-2025_22-26-22_Matrícula_P'];it=sh.iter_rows(values_only=True);h=next(it);data=(dict(zip(h,row)) for row in it)
 else:
  f=p.open(encoding='utf-8-sig' if year=='2023' else 'latin-1',newline='');data=csv.DictReader(f,delimiter=';')
 for d in data:
  doc=norm(d.get('N_DOC'))+norm(d.get('DV'));code='I162S'+val(d.get('COD_SED'))+'C'+val(d.get('COD_CAR'))+'J'+val(d.get('JOR'))+'V'+val(d.get('VERSION'));idx[doc].append(code)
 if year=='2025':w.close()
 else:f.close()
 raw[year]=idx;meta.append({'anio':year,'ruta':str(p),'sha256':digest})
p=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive*/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx'));sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4'
w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['2025_carga'].iter_rows(values_only=True);next(it);prep=collections.defaultdict(list)
for row in it:
 row=tuple(row)+(None,)*115;doc=norm(row[72])+norm(row[73]);code='I162S'+val(row[82])+'C'+val(row[83])+'J'+val(row[85])+'V'+val(row[86]);prep[doc].append((val(row[1]),val(row[8]),code))
w.close();counters={y:collections.Counter() for y in raw};breakdown=collections.Counter()
for c in cs:
 pe,cli,plan,car,jo,year,per=c['key'];code=c['mu_codes'][0];doc=norm(pe);codes=raw[year].get(doc,[]);ctr=counters[year];ctr['contextos']+=1;ctr['codigo_exacto_en_fuente']+=code in codes;ctr['sin_codigo_exacto_en_fuente']+=code not in codes;ctr['multiples_codigos_en_fuente']+=len(set(codes))>1
 obs=n['n']['byexp'][(pe,cli)]
 anchors=[x for x in obs if x['plan']==plan and x['carrera']==car and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==code]
 documentary=any(x.get('codigo_documental_atribuible')==code for x in anchors)
 same_context=[x for x in obs if str(x['ano'])==year and x['plan']==plan and x['carrera']==car]
 alternatives=[x for x in obs if str(x['ano'])==year and (x['plan']!=plan or x['carrera']!=car)]
 confianza['ancla_documental_mismo_codigo_plan_otro_periodo']+=documentary
 confianza['ancla_solo_interna']+=not documentary
 confianza['indice_contexto_ano_mismo_plan']+=bool(same_context)
 confianza['indice_otro_plan_o_carrera_anio']+=bool(alternatives)
 if year=='2025':
  rows=prep.get(doc,[]);match=[r for r in rows if r==(car,jo,code)]
  if match and documentary and not alternatives:cases['candidatos_2025_ancla_documental_fuente_preparacion_sin_alternativas_indice']+=1
  if match:breakdown['coincidencia_completa']+=1
  elif not rows:breakdown['identidad_ausente_en_preparacion']+=1
  elif not any(x[0]==car for x in rows):breakdown['carrera_umas_distinta']+=1
  elif not any(x[0]==car and x[1]==jo for x in rows):breakdown['jornada_umas_distinta']+=1
  else:breakdown['codigo_sies_distinto_o_incompleto']+=1
assert sum(x['contextos'] for x in counters.values())==89
out={'alcance':'89 contextos; fuentes anuales institucionales, no prueba de aceptación PES','fuentes':meta,'fuente_preparacion':{'ruta':str(p),'hoja':'2025_carga','sha256':sha},'contraste_anual':{k:dict(v) for k,v in counters.items()},'preparacion_2025':dict(breakdown),'anclas_y_contexto':dict(confianza),'intersecciones':dict(cases),'limitacion':'Fuentes MU no incluyen CODCLI ni PLAN_DE_ESTUDIO. El cruce por persona y código no acredita por sí mismo plan ni asignación a expediente; no se modificaron datos o denominadores.'}
print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)

from pathlib import Path
import json,collections,re,openpyxl,hashlib,os
ROOT=Path(__file__).resolve().parents[2];p=ROOT/'outputs/avance_trayectoria_plan_fase2_20261027/reconstruir_107.py';n={};exec(compile(p.read_text().split('out=collections.Counter(); examples=[]')[0],str(p),'exec'),n)
cs=[c for c in n['candidates'] if any(x['plan']==c['key'][2] and x['carrera']==c['key'][3] and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==c['mu_codes'][0] for x in n['n']['byexp'][(c['key'][0],c['key'][1])])];assert len(cs)==89;cs=[c for c in cs if c['key'][5]=='2025'];assert len(cs)==69
source=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive*/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx'));sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4'
def val(x):
 if x is None:return ''
 if isinstance(x,float) and x.is_integer():return str(int(x))
 return str(x).strip().upper()
def old(x):return re.sub(r'[^0-9K]','',str(x or '').upper())
def new(x):return re.sub(r'[^0-9K]','',val(x))
w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=w['2025_carga'].iter_rows(values_only=True);next(it);a=collections.defaultdict(list);b=collections.defaultdict(list)
for rn,row in enumerate(it,2):
 row=tuple(row)+(None,)*115;code='I162S'+val(row[82])+'C'+val(row[83])+'J'+val(row[85])+'V'+val(row[86]);item={'fila':rn,'carrera':val(row[1]),'jornada':val(row[8]),'codigo':code,'documento_original':val(row[72]),'dv_original':val(row[73]),'dv_tipo':type(row[73]).__name__};a[old(row[72])+old(row[73])].append(item);b[new(row[72])+new(row[73])].append(item)
w.close();private=[];counts=collections.Counter();changes=collections.Counter()
for c in cs:
 pe,cli,plan,car,jo,year,per=c['key'];code=c['mu_codes'][0];aa=a[old(pe)];bb=b[new(pe)];matches=lambda x:[v for v in x if (v['carrera'],v['jornada'],v['codigo'])==(car,jo,code)]
 first='COINCIDE' if matches(aa) else 'DIFERENCIA';second='COINCIDE' if matches(bb) else 'NO_ENCONTRADO' if not bb else 'CARRERA_DISTINTA' if not any(x['carrera']==car for x in bb) else 'JORNADA_DISTINTA' if not any(x['carrera']==car and x['jornada']==jo for x in bb) else 'CODIGO_DISTINTO'
 counts[first]+=1;counts['NUEVO_'+second]+=1
 if first=='DIFERENCIA' and second=='COINCIDE':changes['DV_CERO_NUMERICO']+=any(x['dv_original']=='0' and x['dv_tipo'] in ('int','float') for x in matches(bb))
 private.append({'persona':pe,'CODCLI':cli,'plan':plan,'carrera':car,'jornada':jo,'anio':year,'periodo':per,'codigo':code,'resultado_44':first,'resultado_47':second,'referencias_metodo_44':aa,'referencias_metodo_47':bb})
assert counts['COINCIDE']==44 and counts['DIFERENCIA']==25 and counts['NUEVO_COINCIDE']==47 and counts['NUEVO_NO_ENCONTRADO']==20 and counts['NUEVO_CARRERA_DISTINTA']==2 and changes['DV_CERO_NUMERICO']==3
private_dir=Path('/Users/alexi/.local/share/ipss/fase_c_hito3_20261027');private_dir.mkdir(mode=0o700,parents=True,exist_ok=True);private_dir.chmod(0o700);pp=private_dir/'COMPARACION_CASO_A_CASO.json';assert not pp.exists();fd=os.open(pp,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(private,f,ensure_ascii=False,indent=2)
result={'clasificacion':'B/C','universo_contextos_2025':69,'misma_fuente':str(source),'misma_hoja':'2025_carga','sha256_fuente':sha,'resultados':dict(counts),'diferencias_reproducidas':dict(changes),'causa':'El método 44 normaliza con str(x or ""); para DV numérico 0 devuelve vacío. El método 47 conserva el cero.','filtro_carrera_jornada_codigo_igual':True,'agregado_44_no_desglosa_25':True,'detalle_privado':{'ruta':str(pp),'sha256':hashlib.sha256(pp.read_bytes()).hexdigest()},'salvedad':'La coincidencia es por documento/carrera/jornada/código; no acredita CODCLI ni plan en esa hoja.'}
(Path(__file__).parent/'COMPARACION_MU2025.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('detalle_privado','misma_fuente')},ensure_ascii=False,indent=2));n['n']['service'].close()

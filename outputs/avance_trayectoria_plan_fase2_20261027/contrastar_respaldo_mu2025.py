from pathlib import Path
import collections,re,json,hashlib,openpyxl
p=Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/avance_trayectoria_plan_fase2_20261027/reconstruir_107.py');n={};exec(compile(p.read_text().split('out=collections.Counter(); examples=[]')[0],str(p),'exec'),n)
cs=[c for c in n['candidates'] if any(x['plan']==c['key'][2] and x['carrera']==c['key'][3] and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==c['mu_codes'][0] for x in n['n']['byexp'][(c['key'][0],c['key'][1])])];assert len(cs)==89
p=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive*/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx'))
hashv=hashlib.sha256(p.read_bytes()).hexdigest();assert hashv=='e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4'
w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['2025_carga'];it=s.iter_rows(values_only=True);heads=next(it)
def norm(x):return re.sub(r'[^0-9K]','',str(x or '').upper())
def val(x):
 if x is None:return ''
 if isinstance(x,float) and x.is_integer():return str(int(x))
 return str(x).strip().upper()
index=collections.defaultdict(list)
for row in it:
 row=tuple(row)+(None,)*115;doc=norm(row[72])+norm(row[73]);code='I162S'+val(row[82])+'C'+val(row[83])+'J'+val(row[85])+'V'+val(row[86]);index[doc].append((val(row[1]),val(row[8]),code))
w.close();counts=collections.Counter(); byyear=collections.Counter()
for c in cs:
 pe,cli,plan,car,jo,year,per=c['key'];byyear[year]+=1
 if year!='2025':continue
 rows=index[norm(pe)]; matches=[x for x in rows if x==(car,jo,c['mu_codes'][0])]
 counts['total_2025']+=1;counts['coincide_RUT_carrera_jornada_codigo']+=bool(matches);counts['sin_coincidencia_completa']+=not bool(matches);counts['otras_filas_mismo_RUT']+=any(x!=(car,jo,c['mu_codes'][0]) for x in rows)
print(json.dumps({'archivo':str(p),'sha256':hashv,'hoja':'2025_carga','filas_por_anio':dict(byyear),'conteos_2025':dict(counts),'limite':'La hoja no tiene CODCLI ni PLAN_DE_ESTUDIO; el enlace a expediente requiere evidencia adicional. No se ejecutaron cierres.'},ensure_ascii=False,indent=2),flush=True)

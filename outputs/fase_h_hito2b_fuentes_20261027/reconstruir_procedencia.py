from pathlib import Path
from collections import Counter
import hashlib,json,os,re,sqlite3,glob,unicodedata,openpyxl
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_h_hito2b_20261027';os.umask(0o077);P.mkdir(mode=0o700,parents=True,exist_ok=True);assert not (P/'PARIDAD_PRIVADA.sqlite').exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def find(pattern):
 a=glob.glob('/Users/alexi/Downloads/cierre/*.xlsx');r=[Path(x) for x in a if pattern in unicodedata.normalize('NFC',Path(x).name)];assert len(r)==1,(pattern,len(r));return r[0]
sources={'maqueta':Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/0 BASES DE DATOS/RETENCION/RETENCION_IPSS_FINAL_REVISADO_20261005.xlsx'),'t2_2025':find('T2_2025 2.xlsx'),'t2_2026':find('T_2_13_07_2026.xlsx'),'t3_2026':find('T3_02_10_2026.xlsx'),'v24':P.parent/'fase_h_regla_intertrimestral_20261027/V24_QA_COPIA.xlsx'};hashes={k:sha(v) for k,v in sources.items()};assert hashes['maqueta']=='5b64030011ad64f742a95ad72a91cc326ad918afaea46ea989496d2e8c44f899';assert hashes['v24']=='1e28d5955d874e7d86ec0ca87ab6a2cc478515c0dbd604f4fc86f60fa491c481'
def norm(v):
 if v is None:return ''
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v).strip()
def identity(v):return norm(v).upper().replace('.','').replace(' ','')
opened={k:openpyxl.load_workbook(p,read_only=True,data_only=True) for k,p in sources.items()};mat={}
for k,sh,header in [('maqueta','9_Base_Analitica_Detalle',6),('maqueta','11_BASE_RETENCION_MU_RAW',4),('t2_2025','Hoja1',1),('t2_2026','Hoja1',1),('t3_2026','Base',1)]:
 ws=opened[k][sh];it=ws.iter_rows(values_only=True);rr=list(it);hd={norm(v).upper():i for i,v in enumerate(rr[header-1]) if v is not None};mat[(k,sh)]=(rr,hd)
v=opened['v24']['20_Foto_BBDD'];rows=list(v.iter_rows(min_row=6,max_row=4478,values_only=True));db=sqlite3.connect(P/'PARIDAD_PRIVADA.sqlite');db.execute('create table comprobacion(fila_v24 integer, fuente text, hoja text, fila_fuente integer, esperado_documento text, observado_documento text, estado text)');c=Counter();groups=Counter()
for i,r in enumerate(rows,6):
 year,group,ref,doc=r[1],r[2],norm(r[3]),r[4];m=re.search(r'fila (\d+)',ref)
 if not m:c['SIN_FILA_ORIGEN']+=1;continue
 rn=int(m[1]);key='maqueta' if str(ref).startswith('RETENCION') else 't2_2025' if year==2025 and group==2 else 't2_2026' if year==2026 and group==2 else 't3_2026' if year==2026 and group==3 else None;sheet='9_Base_Analitica_Detalle' if key=='maqueta' and year in (2024,2025) else '11_BASE_RETENCION_MU_RAW' if key=='maqueta' else 'Base' if key=='t3_2026' else 'Hoja1'
 if not key or (key,sheet) not in mat:c['SIN_FUENTE']+=1;continue
 arr,hd=mat[(key,sheet)];sr=arr[rn-1]
 if sheet=='9_Base_Analitica_Detalle':expect=norm(sr[7])+('-'+norm(sr[8]) if norm(sr[8]) else '')
 elif sheet=='11_BASE_RETENCION_MU_RAW':expect=norm(sr[2])+('-'+norm(sr[3]) if norm(sr[3]) else '')
 else:expect=norm(sr[hd['RUT']])
 result='COINCIDE' if identity(expect)==identity(doc) else 'DOCUMENTO_DIFERENTE';c[result]+=1;groups[(year,group,result)]+=1;db.execute('insert into comprobacion values(?,?,?,?,?,?,?)',(i,str(sources[key]),sheet,rn,expect,norm(doc),result))
db.commit();db.close()
for w in opened.values():w.close()
assert all(sha(v)==hashes[k] for k,v in sources.items());res={'registros_v24':len(rows),'resultado_por_documento_y_fila':dict(c),'grupos':[{'ano':k[0],'grupo':k[1],'estado':k[2],'filas':v} for k,v in sorted(groups.items())],'fuentes':{k:{'ruta':str(v),'sha256':hashes[k]} for k,v in sources.items()},'detalle_privado':{'ruta':str(P/'PARIDAD_PRIVADA.sqlite'),'sha256':sha(P/'PARIDAD_PRIVADA.sqlite')},'limitaciones':['La fila original se toma de la referencia de V24: verifica linaje, no selecciona independientemente la población ni reproduce deduplicación.','Solo se contrastó documento; no se reconstruyeron vigencia, carrera, sector, estado, ni otros campos de hoja 20.','El documento se compara como lo presenta V24; no implica validación de identidad ni DV.']};(O/'PROCEDENCIA_DOCUMENTOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'registros':len(rows),'resultado':dict(c),'grupos':res['grupos']},ensure_ascii=False))

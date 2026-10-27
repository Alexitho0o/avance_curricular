"""Inspección de traza y registros de carga sin exportar datos individuales."""
import collections,hashlib,json,re,zipfile
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
prior=json.loads((ROOT/'outputs/conciliacion_22_ramos_titulados_20261026/EVIDENCIA_AGREGADA.json').read_text());book=Path(prior['fuentes']['respaldo_xlsx']['ruta'])
cases=json.loads(Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json').read_text())
base=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados')
folder=next(base.glob('Titulaci*/2026/errores en las subidas'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
expected=prior['fuentes']['respaldo_xlsx']['sha256'];assert sha(book)==expected
w=openpyxl.load_workbook(book,read_only=True,data_only=False);sheet=w['Res_Tit_Unificada'];it=sheet.iter_rows(values_only=False);h=[str(c.value or '') for c in next(it)];columns=[i for i,v in enumerate(h) if v.startswith('TRACE_')];wanted={r['fila'] for c in cases for r in c['trazas_calculadas']};types=collections.Counter();keytypes=collections.Counter();n=0
for rownum,row in enumerate(it,2):
 if rownum not in wanted:continue
 n+=1
 for i in columns:
  cell=row[i];typ='formula' if cell.data_type=='f' else 'vacia' if cell.value is None else 'valor';types[typ]+=1
  if h[i] in ('TRACE_SCORE_CANDIDATO','TRACE_REASONS_CANDIDATO'):keytypes[h[i]+'_'+typ]+=1
w.close();assert n==4 and sha(book)==expected
with zipfile.ZipFile(book) as z:
 names=z.namelist(); features={'vba':any(x.endswith('vbaProject.bin') for x in names),'conexiones':any(x=='xl/connections.xml' for x in names),'enlaces_externos':sum(x.startswith('xl/externalLinks/externalLink') and x.endswith('.xml') for x in names)}
people={x['RUT'] for x in cases};codcli={o['CODCLI'] for c in cases for o in c['contextos_v11']};plans={'IINF20241','IECIREOL20211','TCRE20241','TTMRE20211'};ramos={x['ramo'] for x in json.loads((ROOT/'outputs/busqueda_respaldo_titulos_homologaciones_20261026/RESULTADO_AGREGADO.json').read_text())['ramos']}
read=[];unread=[];totals=collections.Counter();matched=set()
for p in sorted(folder.glob('*.txt')):
 try:
  raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
  try:text=raw.decode('utf-8-sig')
  except UnicodeDecodeError:text=raw.decode('cp1252')
  normalized=text.upper().replace('.','').replace(' ','');found=set()
  for person in people:
   body,dv=person.split('-')
   if re.search(r'(?<!\d)'+re.escape(body)+r'-?'+re.escape(dv)+r'(?![0-9K])',normalized):found.add(person)
  matched|=found;upper=text.upper();flags={'codcli':any(x in upper for x in codcli),'plan':any(x in upper for x in plans),'ramo':any(x in upper for x in ramos)}
  for k,v in flags.items():totals[k]+=v
  read.append({'archivo':p.name,'sha256':digest,'personas_rut_dv_exacto':len(found),'menciones_codcli':flags['codcli'],'menciones_plan':flags['plan'],'menciones_ramo':flags['ramo']})
 except Exception as e:unread.append({'archivo':p.name,'error':type(e).__name__})
out={'clasificacion':'B libros/reportes; C inspección; E origen y atribución','libro':{'ruta':str(book),'sha256':expected,'filas_caso':n,'columnas_traza':len(columns),'tipos_celdas':dict(types),'tipos_puntaje_y_razones':dict(keytypes),'caracteristicas':features},'reportes_carga':{'carpeta':str(folder),'leidos':len(read),'no_leidos':unread,'personas_rut_dv_exacto':len(matched),'archivos_con_mencion':dict(totals),'archivos':read},'limites':'Valores y coincidencias no prueban fórmula original, criterio de admisión, plan formal o aceptación; búsqueda literal y errores cubren solo archivos disponibles. No se exporta contenido personal.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'celdas':dict(types),'puntaje_razones':dict(keytypes),'caracteristicas':features,'reportes_leidos':len(read),'reportes_no_leidos':len(unread),'personas_en_reportes':len(matched),'archivos_con_mencion':dict(totals)},ensure_ascii=False))

"""H011 Paso 1: sólo evidencia agregada; no asigna códigos ni modifica catálogos."""
import json,hashlib,collections as C,sys,sqlite3,os
from pathlib import Path
import openpyxl
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/h011_20261030';os.umask(0o077);P.mkdir(exist_ok=True)
sources={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 p=Path(p);p=p if p.is_absolute() else R/p;sources[str(p)]=sha(p);return json.loads(p.read_text())
def text(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
res=load('outputs/regla_t1_h010_20261030/RESIDUAL_H010B.json');period=load('outputs/regla_t1_h010_20261030/PERIODOS45_H010B.json');par=load('data/paridad_codigo_sies/20261029/TABLA_PARIDAD_2026_2027.json')['filas'];maestro=load('data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json');dd=load('data/diccionario_umas/DICCIONARIO_UMAS.json')
plans=sorted({z['plan'] for z in res['casos'] if 'REOL' in z['plan']});keys=sorted({(z['carrera'],z['plan'],z['sede'],z['jornada']) for z in res['casos'] if z['plan'] in plans});attrs=[]
for c,p,s,j in keys:
 matches=[z for z in par if c in z['codcarpr'] and p in z['plan_umas'] and str(z['cod_sede'])==s and str(z['cod_jornada'])==j];codes={z['codigo_unico'] for z in matches};annual=[{k:z[k] for k in ['anio','codigo_unico','modalidad','jornada','tipo_plan_sies','duracion_estudios','duracion_total','vigencia']} for z in maestro['oferta_anual'] if z['codigo_unico'] in codes]
 attrs.append({'carrera':c,'plan':p,'sede':s,'jornada':j,'codigos_H002':sorted(codes),'modalidades_H002':sorted({z['modalidad'] for z in matches}),'oferta_por_anio':annual})
listado=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Avance Curricular/2026/Listado_Planes_estudio_Sedes RE+CO.xlsx');assert sha(listado)=='fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049';sources[str(listado)]=sha(listado);wb=openpyxl.load_workbook(listado,read_only=True,data_only=True);it=wb['BBDD Bruta'].iter_rows(values_only=True);head=next(it);ix={v:i for i,v in enumerate(head)};lr=C.defaultdict(list)
for v in it:
 plan=text(v[ix['CODPESTUD']])
 if plan in plans:lr[plan].append({'regimen':text(v[ix['REGIMEN']]),'tipo':text(v[ix['TIPO']]),'ramo':text(v[ix['CODRAMO']]),'nivel':text(v[ix['NIVEL']])})
wb.close()
# Conjuntos de expediente+plan+año; no suma duplicados entre extracciones ni guarda identidades.
sequences=C.defaultdict(set);regimes=C.defaultdict(set);rawreg=C.Counter();sources_rows=[]
for f in dd['fuentes']:
 if not f['archivo'].startswith('PROMEDIOSDEALUMNOS_'):continue
 p=Path(f['ruta']);assert sha(p)==f['sha256'];sources[str(p)]=f['sha256'];wb=openpyxl.load_workbook(p,read_only=True,data_only=True);count=0
 for meta in f['hojas']:
  if meta.get('fila_cabecera')!=1:continue
  ws=wb[meta['hoja']];it=ws.iter_rows(values_only=True);h=[text(v) for v in next(it)];ix={v:i for i,v in enumerate(h)}
  if not all(k in ix for k in ['CODCLI','PLAN_DE_ESTUDIO','ANO','PERIODO','REGIMEN']):continue
  for v in it:
   pl=text(v[ix['PLAN_DE_ESTUDIO']])
   if pl not in plans:continue
   y=text(v[ix['ANO']]);per=text(v[ix['PERIODO']]);reg=text(v[ix['REGIMEN']]);cli=text(v[ix['CODCLI']]);sequences[cli,pl,y].add(per);regimes[pl,y].add(reg);rawreg[pl,y,reg]+=1;count+=1
 wb.close();sources_rows.append({'fuente':f['archivo'],'filas_REOL':count,'unidad':'filas de asignaturas; no sumar entre extractos'})
seqcounts=C.Counter((pl,y,','.join(sorted(ps)),bool(ps & {'4','5'}),bool(ps & {'1','2','3'})) for (cli,pl,y),ps in sequences.items());regrows=[{'plan':pl,'anio':y,'regimenes':sorted(rr)} for (pl,y),rr in sorted(regimes.items())];seqrows=[{'plan':k[0],'anio':k[1],'periodos':k[2],'tiene_45':k[3],'tiene_123':k[4],'expedientes_plan_anio':n} for k,n in sorted(seqcounts.items())]
listrows=[{'plan':p,'incluido':bool(lr[p]),'regimenes':sorted({r['regimen'] for r in lr[p]}),'tipos_literal':sorted({r['tipo'] for r in lr[p]}),'ramos_distintos':len({r['ramo'] for r in lr[p]})} for p in plans]
result={'clase':'B/C; criterio no demostrado queda E','planes':len(plans),'combinaciones':len(keys),'familias_y_oferta':attrs,'listado_UMAS':listrows,'regimen_por_plan_anio':regrows,'secuencias_mismo_expediente_plan_anio':seqrows,'fuentes_promedios':sources_rows,'periodo6':sum(n for (pl,y,ps,a,b),n in seqcounts.items() if '6' in ps.split(',')),'con45':sum(n for (pl,y,ps,a,b),n in seqcounts.items() if a),'con45_y123':sum(n for (pl,y,ps,a,b),n in seqcounts.items() if a and b),'regimenes_no_bimestrales':[x for x in regrows if set(x['regimenes'])!={'BIMESTRAL'}],'fuentes':[{'ruta':p,'sha256':h} for p,h in sorted(sources.items())]};dump(O/'EVIDENCIA_PASO1_REOL.json',result)
print(json.dumps({k:result[k] for k in ['planes','combinaciones','periodo6','con45','con45_y123','regimenes_no_bimestrales']},ensure_ascii=False))

# El antecedente gobernado impide interpretar la abreviatura S sin catálogo UMAS.
reference=R/'outputs/paridad_codigo_sies_20261029/PERFIL_PLANES_H002C.md';sources[str(reference)]=sha(reference)
assert 'No se acreditó el significado de S/A' in reference.read_text()
result['criterios']={'a':{'estado':'CUMPLE_B_C','evidencia':'22 planes/23 combinaciones tienen candidatos H002 no presenciales; no implica equivalencia única.'},'b':{'estado':'CUMPLE_OBSERVACION_B_C','evidencia':'Todos los registros REOL leídos indican BIMESTRAL; hay secuencias 1–5 del mismo expediente, plan y año; no se observa 6. No acredita fechas de inicio/término.'},'c':{'estado':'NO_ACREDITADO_E','evidencia':'El listado institucional usa REGIMEN S para los 22 planes; H002c no acredita qué significa S/A. No se afirma S=SEMESTRAL ni contradicción confirmada, pero no se puede descartar incompatibilidad con BIMESTRAL sin definir ámbito y significado.'}}
result['decision_paso1']='DETENER_ANTES_PASO2'
result['requisito']='Catálogo o confirmación UMAS que defina REGIMEN=S en BBDD Bruta y su relación con REGIMEN=BIMESTRAL de PROMEDIOS. No basta el nombre REOL. Los perfiles regulares/continuidad múltiples deben conservarse separados.'
result['fuentes']=[{'ruta':p,'sha256':h} for p,h in sorted(sources.items())];dump(O/'EVIDENCIA_PASO1_REOL.json',result)
full=sum(z['expedientes_plan_anio'] for z in seqrows if z['periodos']=='1,2,3,4,5')
lines=['# H011 · Paso 1: verificación REOL y parada','', '**Estado: DETENIDO ANTES DEL PASO 2.** Clase B/C para las observaciones; E para el criterio (c). No se aplican D4, D5 ni D6; no se construye catálogo v3 ni se altera la candidata v21.','', '## Criterios','', '| Criterio | Resultado | Evidencia |','|---|---|---|']
for k,v in result['criterios'].items():lines.append('| '+k+' | '+v['estado']+' | '+v['evidencia']+' |')
lines+=['', '## Qué se verificó','',f"- 22 planes REOL, 23 combinaciones carrera/plan/sede/jornada presentes en el residual. Todos tienen candidatos H002 de modalidad No presencial. Atributos por código y año en EVIDENCIA_PASO1_REOL.json → familias_y_oferta.",'- Los 22 planes sí están en Listado_Planes_estudio_Sedes RE+CO.xlsx, hoja BBDD Bruta: REGIMEN S; TIPO Obl/OPC no es tipo de plan SIES.',f"- PROMEDIOS: {result['con45']} combinaciones expediente–plan–año con 4/5; {result['con45_y123']} también tienen 1/2/3; {full} tienen secuencia completa 1,2,3,4,5. Período 6: {result['periodo6']}. Conjuntos sin duplicar entre extractos; no son contextos ni personas únicas.",'- Reutilización H010b: los 604 históricos incluyen 598 BIMESTRAL REOL y 6 no REOL (3 SEMESTRAL y 3 TRIMESTRAL). No son 604 REOL.','', '## Límite que impide aceptar la conclusión universal','', 'No se interpreta S como semestral: su significado no está acreditado, tal como documentó PERFIL_PLANES_H002C.md, párrafo inicial. Por tanto, la incompatibilidad con BIMESTRAL no está confirmada, pero el criterio de ausencia de contradicción tampoco queda acreditado. Se necesita definir el alcance de los dos campos, no elegir uno por preferencia.','', 'Además, los candidatos de IECIREOL (sus cuatro planes), NCONREOL2019 y NINFREOL2019 incluyen tipos SIES regular y continuidad. Modalidad no presencial no demuestra por sí sola REGULAR. Esto no adjudica esos planes ni cambia H002.','', 'Requisito: '+result['requisito'],'', '## Cobertura conservada','', '| Universo | Antes H010b | Después de esta verificación | Residual E |','|---|---:|---:|---:|','| 3.049 contextos | 2.085 respaldados | 2.085 | 964 |','| 99 posiciones | 99 respaldadas | 99 | 0 |','', 'Residual histórico reutilizado, sin reclasificar: 604 períodos 4/5; 273 tipo/duración E; 48 T1 previo sin posterior; 28 sin VIGENCIA 1 compatible; 6 primer T1 ambiguo/dimensiones distintas; 2 sin código anual compatible; 2 varias VIGENCIA 1; 1 ambigüedad anual. Fuente: COBERTURA_H010B.json y RESIDUAL_H010B.json.','', 'v20 activo y v21 candidata intactos. R01–R04 y R19 sin cambios: 0,00 pp por conservación, sin recálculo. Excel no se abrió. No se actualizaron mapa ni reglas: la condición de avance no quedó acreditada. No se hace commit/push con el mensaje de asignación porque no hubo asignaciones.','', '## Fuentes verificadas','', '| Fuente | SHA-256 |','|---|---|']
for p,h in sorted(sources.items()):lines.append('| '+p+' | '+h+' |')
(O/'INFORME_H011_PASO1.md').write_text('\n'.join(lines)+'\n')

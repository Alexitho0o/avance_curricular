from pathlib import Path
import sys,os,hashlib,json,sqlite3,copy,re,subprocess
import pandas as pd
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
from common.seguimiento_promedios_v11 import CapaPromedios
OUT=Path(__file__).parent;P=Path('/Users/alexi/.local/share/ipss/candidata_47_20261027/CANDIDATA_47.json');props=json.loads(P.read_text())['propuestas'];assert len(props)==47
active=ROOT/'data/diccionario_sies_seguimiento/activo.json';active_bytes=active.read_bytes();prev=json.loads(active_bytes);old=DiccionarioSiesSeguimiento();assert old.edicion=='v12_20261027_644_internos';old_db=old.descriptor['base_privada']['sha256']
manifest=json.loads((ROOT/'outputs/avance_historico_origen_h113_20261027/MANIFEST_ORIGEN_H113.json').read_text());source=Path(manifest['fuentes']['promedios']['ruta']);assert sha256(source)==manifest['fuentes']['promedios']['sha256']
cols=['RUT','DIG','CODCLI','CODCARR','JORNADA','PLAN_DE_ESTUDIO','ANO','PERIODO','ESTADO'];df=pd.read_excel(source,sheet_name='Hoja1',dtype=str,keep_default_na=False,usecols=cols)
def norm(x):return str(x).strip().upper()
def body(x):return re.sub(r'[.\s]','',norm(x))
def num(x):
 try:return str(int(float(x)))
 except:return ''
index={}
for i,row in df.iterrows():
 k=(body(row['RUT'])+'-'+body(row['DIG']),norm(row['CODCLI']),num(row['ANO']));index.setdefault(k,[]).append((i+2,norm(row['PLAN_DE_ESTUDIO']),norm(row['CODCARR']),norm(row['JORNADA']),num(row['PERIODO']),norm(row['ESTADO'])))
checks=[];qualified=[];rejected=[]
for p in props:
 x=p['contexto'];pe=x['persona'];cli=x['CODCLI'];plan=x['plan'];car=x['carrera'];jor=x['jornada_UMAS'];year=x['ano'];period=x['periodo_UMAS'];code=p['codigo'];mu=old.codigos_mu(persona=pe,anio=year)
 vals=index.get((pe,cli,year),[]);eligible=[v for v in vals if v[1:5]==(plan,car,jor,period) and v[5] in ('A','R','E','I')];other={(v[1],v[2],v[3]) for v in vals if v[5] in ('A','R','E','I')}-{(plan,car,jor)}
 anchors=[a for a in p['anclas'] if a['persona']==pe and a['CODCLI']==cli and a['plan']==plan and a['carrera']==car and a.get('codigo_documental_atribuible')==code]
 oldrows=old.db.execute('SELECT codcli,payload FROM observaciones WHERE persona=? AND anio=?',(pe,year)).fetchall();othercli=any(c!=cli and (json.loads(v).get('codigo_documental_atribuible') or json.loads(v).get('codigo_interno_adoptado'))==code for c,v in oldrows)
 verdict=old.consultar(persona=pe,codcli=cli,plan=plan,anio=year,periodo=period,carrera=car)
 if mu['codigos']!=[code] or not eligible or other or not anchors or othercli or verdict['motivo']!='CONTEXTO_NO_LOCALIZADO':rejected.append((p,'EVIDENCIA_O_CONTEXTO_NO_UNICO'));continue
 qualified.append((p,eligible,anchors))
assert len(qualified)+len(rejected)==47
print('Candidatos comprobados:',len(qualified),'pendientes:',len(rejected),flush=True)
# Ninguna fuente normativa se sustituye: ancla anual y actividad solo atribuyen internamente.
PRIVATE=Path('/Users/alexi/.local/share/ipss/activacion_47_20261027');PRIVATE.mkdir(parents=True,mode=0o700,exist_ok=True);PRIVATE.chmod(0o700)
ed='v13_20261027_contextos_47';dest=ROOT/'data/diccionario_sies_seguimiento'/ed
assert not dest.exists();assert not (PRIVATE/'DICCIONARIO_V13.sqlite').exists();dest.mkdir()
base=PRIVATE/'DICCIONARIO_V13.sqlite';db=sqlite3.connect(base);old.db.backup(db);os.chmod(base,0o600)
oldrows=old.db.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload FROM observaciones ORDER BY id').fetchall();maxid=max(x[0] for x in oldrows);new=[]
for p,eligible,anchors in qualified:
 x=p['contexto'];code=p['codigo'];match=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)',code);assert match
 assert all(str(a['sede_dimension'])==match[1] and str(a['jornada_sies'])==match[3] for a in anchors)
 maxid+=1
 row={'observacion_id':maxid,'persona':x['persona'],'CODCLI':x['CODCLI'],'plan':x['plan'],'ano':x['ano'],'periodo':x['periodo_UMAS'],'carrera':x['carrera'],'sede_dimension':match[1],'jornada_sies':match[3],'codigo_documental_atribuible':'','codigo_interno_adoptado':code,'codigo_propuesto':'','estado_documental':'PENDIENTE_ATRIBUCION_PERIODO','estado_interno':'CORRESPONDENCIA_INTERNA_APROBADA','clasificacion':'D_CORRESPONDENCIA_INTERNA_APROBADA','regla':'MU_ANUAL_UNICA_MISMO_CODCLI_PLAN_CARRERA_JORNADA_ANCLA_DOCUMENTAL_OTRO_ANIO','requisito_pendiente':'Atribución documental al plan en período y fecha efectiva de cambios no acreditadas; no prueba aceptación SIES.','aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO','fuentes_promedios':[{'fuente':str(source),'hoja':'Hoja1','fila':v[0]} for v in eligible],'evidencias_matricula':p['evidencias_MU'],'anclas_existentes':[{'observacion_id':a['observacion_id'],'ano':a['ano'],'periodo':a['periodo']} for a in anchors],'decision':'CRITERIO_APROBADO_USUARIO_20261027','actividad':p['actividad']}
 db.execute('INSERT INTO observaciones VALUES (?,?,?,?,?,?,?,?,?,?)',(maxid,x['persona'],x['CODCLI'],x['plan'],x['ano'],x['periodo_UMAS'],x['carrera'],match[1],match[3],json.dumps(row,ensure_ascii=False)));new.append(row)
db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close()
d=copy.deepcopy(old.descriptor);d['edicion']=ed;d['fecha_hora']=datetime.now().astimezone().isoformat();d['estado']='CANDIDATA_QA';d['base_privada']={'ruta':str(base),'sha256':sha256(base)};d['edicion_anterior']=prev;d['resumen_anterior']=d['resumen'];d['resumen']=dict(d['resumen']);d['resumen']['universo_observaciones']=len(oldrows)+len(new);d['resumen']['solo_correspondencia_interna_aprobada']+=len(new);d['resumen']['nuevos_contextos_internos_v13']=len(new)
mp=dest/'CAPA_PROMEDIOS_COMPATIBLE.json';meta_path=ROOT/old.descriptor['capa_promedios']['metadata'];assert sha256(meta_path)==old.descriptor['capa_promedios']['sha256'];meta=json.loads(meta_path.read_text());meta['edicion_diccionario']=ed;meta['sha256_base_v11']=sha256(base);meta['alcance_v13']='Observaciones previas preservadas; nuevas observaciones con capa de fotos y estado pendiente de indexacion.';mp.write_text(json.dumps(meta,ensure_ascii=False,indent=2));d['capa_promedios']['metadata']=str(mp.relative_to(ROOT));d['capa_promedios']['sha256']=sha256(mp)
dp=dest/'descriptor.json';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2));candidate=DiccionarioSiesSeguimiento(descriptor=dp)
fields=('persona','codcli','plan','anio','periodo','carrera','sede','jornada')
for row in oldrows:
 q=dict(zip(fields,row[1:9]));a=old.consultar(**q);b=candidate.consultar(**q);a.pop('edicion');b.pop('edicion');assert a==b
for row in new:
 q=dict(persona=row['persona'],codcli=row['CODCLI'],plan=row['plan'],anio=row['ano'],periodo=row['periodo'],carrera=row['carrera'],sede=row['sede_dimension'],jornada=row['jornada_sies']);v=candidate.consultar(**q);assert v['codigo_sies']==row['codigo_interno_adoptado'] and v['codigo_documental'] is None and v['nivel_respaldo']=='D_CORRESPONDENCIA_INTERNA_APROBADA'
assert candidate.db.execute('SELECT * FROM observaciones WHERE id<=? ORDER BY id',(oldrows[-1][0],)).fetchall()==oldrows
assert candidate.db.execute('SELECT * FROM mu_anual ORDER BY rowid').fetchall()==old.db.execute('SELECT * FROM mu_anual ORDER BY rowid').fetchall();assert CapaPromedios(candidate).problema is None
old.close();candidate.close();assert sha256(source)==manifest['fuentes']['promedios']['sha256'];assert sha256(Path(json.loads((ROOT/prev['descriptor']).read_text())['base_privada']['ruta']))==old_db
assert active.read_bytes()==active_bytes
d['estado']='ACTIVA_APROBADA_QA_PASS';dp.write_text(json.dumps(d,ensure_ascii=False,indent=2));(dest/'ACTIVO_ANTERIOR.json').write_bytes(active_bytes)
qa={'estado':'PASS','propuestas':47,'aceptados':len(new),'rechazados':len(rejected),'consultas_anteriores_iguales':len(oldrows),'observaciones_y_MU_anteriores_preservadas':True,'capa_nueva':'PENDIENTE_INDEXACION','atribucion_documental':'PENDIENTE','fuentes_y_denominadores_modificados':False,'commit':False,'push':False}
(dest/'DECISION.json').write_text(json.dumps({'clase':'D','responsable':'Alexi','fecha_hora':datetime.now().astimezone().isoformat(),'autorizacion':'Coincidencia de MU anual única con mismo CODCLI, carrera, sede, jornada y plan; caso TCIB20241 aprobado expresamente','candidata_sha256':sha256(P),'observaciones_aceptadas':len(new),'atribucion_documental':'PENDIENTE'},ensure_ascii=False,indent=2));(dest/'QA.json').write_text(json.dumps(qa,indent=2));(dest/'ALERTA_CAMBIO.json').write_text(json.dumps({'antes':prev,'despues':{'descriptor':str(dp.relative_to(ROOT)),'sha256':sha256(dp)},'cantidad':len(new)},indent=2))
active.write_text(json.dumps({'descriptor':str(dp.relative_to(ROOT)),'sha256':sha256(dp)},indent=2)+'\n');(OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa),flush=True)

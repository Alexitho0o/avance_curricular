"""Candidata aditiva con 13 decisiones aprobadas y dos alternativas pendientes."""
import collections,copy,datetime,json,os,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import aplicar_adjudicaciones,sha256
P=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026'); olddesc=OUT/'DESCRIPTOR_CANDIDATA_73_CO.json'
desc=json.loads(olddesc.read_text()); old=Path(desc['base_privada']['ruta']); assert sha256(old)==desc['base_privada']['sha256']
new=P/'DICCIONARIO_SIES_CANDIDATO_V11_86_Y_AMBIGUEDAD.sqlite'; priv=P/'ADJUDICACIONES_13_2025_Y_ALTERNATIVAS.json'; output=OUT/'DESCRIPTOR_CANDIDATA_86_Y_AMBIGUEDAD.json'
for p in (new,priv,output):
 if p.exists(): raise SystemExit('Preservar salida existente: '+str(p))
assert not P.resolve().is_relative_to(ROOT.resolve())
targets=json.loads((P/'EVALUACION_CIERRE_CO_V1_DETALLE_V2.json').read_text());targets=[t for t in targets if t['diferencia_familia'] and t['anio']=='2025' and any(m['anio']=='2026' and m.get('codigo','').rsplit('V',1)[0] in t['familias_destino'] for m in t['mu_fuente_primaria'])];assert len(targets)==13 and len({t['persona'] for t in targets})==8
incoming=json.loads((P/'CONTEXTOS_CANDIDATOS.json').read_text()); k=lambda x:(x['persona'],x['CODCLI'],x['plan'],x['anio'],x['periodo']);count=collections.Counter(map(k,incoming));amb=[x for x in incoming if count[k(x)]>1];assert len(amb)==2 and len({k(x) for x in amb})==1 and {x['jornada_sies'] for x in amb}=={'1','2'}
src=sqlite3.connect(old.as_uri()+'?mode=ro',uri=True);dst=sqlite3.connect(new);src.backup(dst);os.chmod(new,0o600)
before=src.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload FROM observaciones ORDER BY id').fetchall();mu_before=src.execute('SELECT * FROM mu_anual ORDER BY rowid').fetchall();ops=[];codes=collections.Counter()
for t in targets:
 mu=[m for m in t['mu_fuente_primaria'] if m['anio']=='2026'];cs={m['codigo'] for m in mu};assert len(cs)==1;code=next(iter(cs)); assert code.rsplit('V',1)[0] in t['familias_destino']
 args=(t['persona'],t['codcli'],t['plan'],t['anio'],t['periodo'],t['carrera'],t['sede_actual'],t['jornada']);rows=dst.execute('SELECT id,payload FROM observaciones WHERE persona=? AND codcli=? AND plan=? AND anio=? AND periodo=? AND carrera=? AND sede=? AND jornada=?',args).fetchall();assert len(rows)==1
 oid,payload=rows[0];r=json.loads(payload);assert not r['codigo_interno_adoptado'] and not r['codigo_documental_atribuible']
 n=copy.deepcopy(r);n.update({'codigo_interno_adoptado':code,'estado_interno':'CORRESPONDENCIA_INTERNA_13_2025_APROBADA','regla':'MU2026_CAMBIO_JORNADA_13_2025_APROBADO','clasificacion':'D correspondencia interna aprobada; B MU2026 y oferta 2025; E atribucion documental 2025','requisito_pendiente':'No acredita asignacion documental al CODCLI en 2025, fecha efectiva del cambio, aceptacion SIES ni vigencia de cierre.'})
 op={'observacion_id':r['observacion_id'],'estado_antes':r,'estado_despues':n};assert aplicar_adjudicaciones([r],[op])==[n];dst.execute('UPDATE observaciones SET payload=? WHERE id=?',(json.dumps(n,ensure_ascii=False),oid));ops.append(op);codes[code]+=1
inserted=[];nextid=dst.execute('SELECT max(id) FROM observaciones').fetchone()[0]+1
for x in amb:
 identity=k(x); owners={r[0] for r in dst.execute('SELECT DISTINCT persona FROM observaciones WHERE codcli=?',(x['CODCLI'],))};assert not owners or owners=={x['persona']}
 assert not dst.execute('SELECT 1 FROM observaciones WHERE persona=? AND codcli=? AND plan=? AND anio=? AND periodo=? AND carrera=? AND sede=? AND jornada=?',(*identity,x['carrera'],x['sede_umas_actual'],x['jornada_sies'])).fetchone()
 payload={'observacion_id':nextid,'persona':x['persona'],'CODCLI':x['CODCLI'],'plan':x['plan'],'ano':x['anio'],'periodo':x['periodo'],'carrera':x['carrera'],'sede_dimension':x['sede_umas_actual'],'jornada_sies':x['jornada_sies'],'codigo_documental_atribuible':'','codigo_interno_adoptado':'','codigo_propuesto':'','estado_interno':'ALTERNATIVA_JORNADA_AMBIGUA_SIN_ADJUDICAR','clasificacion':'E_PENDIENTE','regla':'CONSERVAR_ALTERNATIVAS_SIN_SELECCION','requisito_pendiente':'Acreditar jornada y fecha efectiva del cambio; no asumir retencion ni vigencia.','aceptacion_SIES':'NO_ACREDITADA','plan_efectivo_periodo':'NO_ACREDITADO','familias_candidatas':x['familias_candidatas'],'fuentes_promedios':x['fuentes_filas']}
 dst.execute('INSERT INTO observaciones (id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload) VALUES (?,?,?,?,?,?,?,?,?,?)',(nextid,*identity,x['carrera'],x['sede_umas_actual'],x['jornada_sies'],json.dumps(payload,ensure_ascii=False)));inserted.append(payload);nextid+=1
dst.commit();assert dst.execute('PRAGMA integrity_check').fetchone()[0]=='ok';after=dst.execute('SELECT id,persona,codcli,plan,anio,periodo,carrera,sede,jornada,payload FROM observaciones ORDER BY id').fetchall();assert dst.execute('SELECT * FROM mu_anual ORDER BY rowid').fetchall()==mu_before
assert len(before)==25900 and len(after)==25902 and all(a[:9]==b[:9] for a,b in zip(before,after));changed={a[0] for a,b in zip(before,after) if a[9]!=b[9]};assert changed=={o['observacion_id'] for o in ops} and len(changed)==13
dst.close();src.close();assert sha256(old)==desc['base_privada']['sha256']
fd=os.open(priv,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump({'adjudicaciones':ops,'alternativas':inserted},f,ensure_ascii=False)
newdesc=copy.deepcopy(desc);newdesc.update({'edicion':'v11_candidata_86_y_ambiguedad_20261026','fecha_hora':datetime.datetime.now().astimezone().isoformat(),'base_privada':{'ruta':str(new),'sha256':sha256(new)},'edicion_anterior':{'descriptor':str(olddesc),'sha256':sha256(olddesc)},'estado':'CANDIDATA_NO_ACTIVA','nota_v11':'73 CO + 13 correspondencias D aprobadas; dos alternativas de jornada en E; no es QA de fuente completa.'})
newdesc['resumen'].update({'universo_observaciones':25902,'contextos_nuevos_E':1042,'adjudicaciones_internas_2025':13,'alternativas_jornada_ambiguas':2});output.write_text(json.dumps(newdesc,ensure_ascii=False,indent=2)+'\n')
q={'clasificacion':'C cambios de candidata; D adjudicaciones; E alternativas','estado':'QA_EN_CURSO','observaciones_antes':25900,'observaciones_despues':25902,'cambios_2025':13,'codigos_2025':dict(codes),'alternativas_ambiguas':2,'mu_y_dimensiones_previas_sin_cambios':True,'base_anterior_sha256':sha256(old),'base_candidata_sha256':sha256(new),'descriptor_sha256':sha256(output),'detalle_privado_sha256':sha256(priv)};(OUT/'QA_CANDIDATA_86_Y_AMBIGUEDAD.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False))
